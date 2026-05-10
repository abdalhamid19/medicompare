"""Main entry point for the drug matching pipeline."""
import argparse
import asyncio
import logging
import os

from drug_matcher.ai_health import AIKey, dedupe, run_health_checks, write_reports
from drug_matcher.ai_rotation import configured_attempts
from drug_matcher.ai_rotation_health import (
    attempts_from_health,
    run_rotation_health,
    write_rotation_reports,
)
from drug_matcher.config import MatchingConfig, APIConfig, setup_logging, load_env, resolve_api_config, PROVIDERS
from drug_matcher.pipeline import MatchPipeline

logger = logging.getLogger("medicompare")


def parse_args():
    parser = argparse.ArgumentParser(description="MediCompare - Drug Matching Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of drugs to process")
    parser.add_argument("--start", type=int, default=None, help="Start index (0-based, inclusive)")
    parser.add_argument("--end", type=int, default=None, help="End index (0-based, exclusive)")
    parser.add_argument("--resume", action="store_true", help="Resume from last completed position")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--threshold", type=int, default=80, help="Fuzzy matching threshold (default: 80)")
    parser.add_argument("--ai-threshold", type=float, default=90.0, help="AI verification threshold (default: 90)")
    parser.add_argument("--output", default=None, help="Output CSV path")
    parser.add_argument("--trace", action="store_true", help="Enable detailed algorithm trace (CSV+TXT in output/trace/)")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI verification and search (algorithm only)")
    parser.add_argument("--model", default=None, help="AI model to use (e.g. openai/gpt-4o-mini, big-pickle)")
    parser.add_argument("--provider", default=None, choices=list(PROVIDERS.keys()), help="API provider (openrouter, opencode, agentrouter, custom)")
    parser.add_argument("--api-key", default=None, help="API key (overrides .env)")
    parser.add_argument("--review-model", default=None, help="Second AI model for cross-review (e.g. big-pickle)")
    parser.add_argument("--review-threshold", type=float, default=None, help="Review AI decisions with confidence below this (default: 1.0)")
    parser.add_argument("--no-ai-preflight", action="store_true", help="Skip AI health preflight")
    parser.add_argument("--ai-timeout", type=float, default=10.0, help="AI preflight timeout in seconds")
    parser.add_argument("--ai-search-limit", type=int, default=None, help="Maximum unmatched rows to send through AI search")
    return parser.parse_args()


def _key_items(keys: tuple[str, ...]) -> list[AIKey]:
    return [AIKey(f"key_{i + 1}", key) for i, key in enumerate(keys) if key]


def _healthy_rows(rows):
    return [row for row in rows if row.get("ok") and row.get("mode") == "json"]


def _apply_preflight(api_cfg, rows):
    healthy = _healthy_rows(rows)
    if not healthy:
        return APIConfig(
            api_key="",
            api_keys=(),
            base_url=api_cfg.base_url,
            model=api_cfg.model,
            fallback_models=api_cfg.fallback_models,
            review_model="",
            healthy_combos=(),
            max_tokens=api_cfg.max_tokens,
            temperature=api_cfg.temperature,
        )
    primary = str(healthy[0]["model"])
    healthy_models = dedupe([str(row["model"]) for row in healthy])
    review_model = api_cfg.review_model if api_cfg.review_model in healthy_models else ""
    key_suffixes = {str(row["key_masked"])[-6:] for row in healthy}
    keys = tuple(key for key in api_cfg.api_keys if key[-6:] in key_suffixes)
    combos = tuple((str(row["key_masked"])[-6:], str(row["model"])) for row in healthy)
    return APIConfig(
        api_key=keys[0] if keys else "",
        api_keys=keys,
        base_url=api_cfg.base_url,
        model=primary,
        fallback_models=tuple(m for m in healthy_models if m != primary),
        review_model=review_model,
        healthy_combos=combos,
        max_tokens=api_cfg.max_tokens,
        temperature=api_cfg.temperature,
    )


def _rotation_api_config(attempts, max_tokens=512, temperature=0.1):
    first = attempts[0] if attempts else None
    return APIConfig(
        api_key=first.api_key if first else "",
        api_keys=(first.api_key,) if first else (),
        base_url=first.base_url if first else "",
        model=first.model if first else "",
        fallback_models=(),
        review_model="",
        healthy_combos=(),
        attempt_plan=tuple(attempts),
        max_tokens=max_tokens,
        temperature=temperature,
    )


async def _preflight_rotation(api_cfg, timeout, trace=None):
    attempts = tuple(api_cfg.attempt_plan)
    if not attempts:
        return api_cfg
    if trace and trace.enabled:
        trace.log_ai_preflight_start([a.model for a in attempts], len(attempts))
    rows = await run_rotation_health(
        attempts, ["json"], timeout_s=timeout,
        max_tokens=min(api_cfg.max_tokens, 256),
        concurrency=min(len(attempts), 4),
    )
    write_rotation_reports(rows)
    selected = attempts_from_health(attempts, rows)
    if trace and trace.enabled:
        trace.log_ai_preflight_result(rows, len(selected))
    logger.info(
        "AI rotation preflight: %s/%s healthy attempts",
        len(selected), len(rows),
    )
    return _rotation_api_config(
        selected, max_tokens=api_cfg.max_tokens,
        temperature=api_cfg.temperature,
    )


async def _preflight_api(api_cfg, timeout, trace=None):
    if api_cfg.attempt_plan:
        return await _preflight_rotation(api_cfg, timeout, trace)
    keys = _key_items(api_cfg.api_keys)
    models = dedupe(
        [api_cfg.model] + list(api_cfg.fallback_models)
        + ([api_cfg.review_model] if api_cfg.review_model else [])
    )
    if not keys or not models:
        return api_cfg
    if trace and trace.enabled:
        trace.log_ai_preflight_start(models, len(keys))
    rows = await run_health_checks(
        keys, models, ["json"], timeout_s=timeout,
        max_tokens=min(api_cfg.max_tokens, 256),
        concurrency=min(len(keys) * len(models), 4),
        base_url=api_cfg.base_url,
    )
    write_reports(rows)
    healthy_count = len(_healthy_rows(rows))
    if trace and trace.enabled:
        trace.log_ai_preflight_result(rows, healthy_count)
    logger.info(
        "AI preflight: %s/%s healthy model/key combos",
        healthy_count, len(rows),
    )
    return _apply_preflight(api_cfg, rows)


def main():
    args = parse_args()
    setup_logging(args.log_level)
    load_env()

    match_cfg = MatchingConfig(
        fuzzy_threshold=args.threshold,
        brand_prefix_min=4,
        ai_verify_threshold=args.ai_threshold,
        ai_batch_size=20,
        ai_max_concurrent=5,
        top_k_candidates=10,
        ai_review_threshold=args.review_threshold if args.review_threshold is not None else 0.95,
        ai_search_limit=args.ai_search_limit,
    )

    if args.provider == "rotation":
        api_cfg = _rotation_api_config(configured_attempts("auto"))
    else:
        resolved = resolve_api_config(
            provider=args.provider or "",
            model=args.model or "",
            api_key=args.api_key or "",
        )
        api_cfg = APIConfig(
            api_key=resolved["api_key"],
            api_keys=resolved.get("api_keys", ()),
            base_url=resolved["base_url"],
            model=resolved["model"],
            fallback_models=resolved.get("fallback_models", ()),
            review_model=args.review_model or os.getenv("REVIEW_MODEL", ""),
            max_tokens=512,
            temperature=0.1,
        )

    trace = None
    if args.trace:
        from drug_matcher.trace_log import MatchTraceLog
        trace = MatchTraceLog(enabled=True)

    if not args.no_ai and not args.no_ai_preflight and api_cfg.api_key:
        api_cfg = asyncio.run(_preflight_api(api_cfg, args.ai_timeout, trace))

    # Resolve start/end from --resume or explicit args
    start = args.start
    end = args.end
    if args.resume:
        progress = MatchPipeline.load_progress()
        if progress:
            start = progress["last_end"]
            logger.info(f"Resuming from row {start} (from previous run)")
        else:
            logger.info("No progress file found — starting from beginning")

    pipeline = MatchPipeline(cfg=match_cfg, api_cfg=api_cfg, limit=args.limit, start=start, end=end)
    if trace:
        pipeline._trace = trace
    result = asyncio.run(pipeline.run_full(output_path=args.output, skip_ai=args.no_ai))

    return result


if __name__ == "__main__":
    main()
