"""Main entry point for the drug matching pipeline."""
import argparse
import asyncio
import logging
import os

from drug_matcher.ai_health import AIKey, dedupe, run_health_checks, write_reports
from drug_matcher.ai_rotation import configured_attempts
from drug_matcher.ai_rotation_health import (
    attempts_from_partial_health,
    attempts_from_health,
    cached_working_attempts,
    load_latest_rotation_health,
    run_rotation_health,
    select_preflight_attempts,
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
    parser.add_argument("--ai-verify-policy", choices=["score", "fuzzy", "all-non-exact", "all"], default="score", help="AI verification selection policy")
    parser.add_argument("--ai-verify-limit", type=int, default=None, help="Maximum matched rows to send through AI verification")
    parser.add_argument("--output", default=None, help="Output CSV path")
    parser.add_argument("--trace", action="store_true", help="Enable detailed algorithm trace (CSV+TXT in output/trace/)")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI verification and search (algorithm only)")
    parser.add_argument("--model", default=None, help="AI model to use (e.g. openai/gpt-4o-mini, big-pickle)")
    parser.add_argument("--provider", default=None, choices=list(PROVIDERS.keys()), help="API provider (rotation, groq, opencode, openrouter, custom)")
    parser.add_argument("--api-key", default=None, help="API key (overrides .env)")
    parser.add_argument("--review-model", default=None, help="Second AI model for cross-review (e.g. big-pickle)")
    parser.add_argument("--review-threshold", type=float, default=None, help="Review AI decisions with confidence below this (default: 1.0)")
    parser.add_argument("--no-ai-preflight", action="store_true", help="Skip AI health preflight")
    parser.add_argument("--ai-timeout", type=float, default=10.0, help="AI preflight timeout in seconds")
    parser.add_argument("--ai-search-limit", type=int, default=None, help="Maximum unmatched rows to send through AI search")
    parser.add_argument("--ai-search-policy", choices=["safe", "expanded", "aggressive"], default="safe", help="AI search expansion policy")
    parser.add_argument("--ai-search-min-candidate-score", type=float, default=None, help="Minimum candidate score before AI search")
    parser.add_argument("--ai-search-accept-confidence", type=float, default=None, help="Minimum AI confidence to accept search match")
    parser.add_argument("--ai-search-candidate-limit", type=int, default=None, help="Candidate limit per search strategy before AI search")
    parser.add_argument("--concurrency", type=int, default=None, help="Maximum concurrent AI requests and preflight checks")
    parser.add_argument("--rotation-preflight-policy", choices=["smart", "full", "off"], default="smart", help="Rotation preflight policy")
    parser.add_argument("--rotation-preflight-budget", type=int, default=60, help="Maximum rotation attempts to test in smart preflight")
    parser.add_argument("--rotation-preflight-min-healthy", type=int, default=24, help="Minimum healthy attempts targeted by smart preflight")
    parser.add_argument("--rotation-preflight-min-providers", type=int, default=3, help="Minimum healthy providers targeted by smart preflight")
    parser.add_argument("--rotation-preflight-tier-limit", type=int, default=1, help="Highest model tier to test in smart preflight")
    parser.add_argument("--rotation-preflight-cache-ttl", type=float, default=21600.0, help="Seconds to reuse latest rotation preflight report")
    parser.add_argument("--rotation-preflight-refresh", type=int, default=10, help="Cached working attempts to refresh during smart preflight")
    return parser.parse_args()


def _search_policy_values(args):
    defaults = {
        "safe": (80.0, 0.75, 5),
        "expanded": (75.0, 0.75, 10),
        "aggressive": (70.0, 0.75, 15),
    }
    min_score, confidence, limit = defaults[args.ai_search_policy]
    return (
        args.ai_search_min_candidate_score
        if args.ai_search_min_candidate_score is not None else min_score,
        args.ai_search_accept_confidence
        if args.ai_search_accept_confidence is not None else confidence,
        args.ai_search_candidate_limit
        if args.ai_search_candidate_limit is not None else limit,
    )


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


def _review_rotation_attempts(attempts):
    if len(attempts) <= 1:
        return tuple(attempts)
    primary = attempts[0].safe_tuple()
    alternates = [attempt for attempt in attempts if attempt.safe_tuple() != primary]
    return tuple(alternates or attempts)


def _rotation_api_config(
    attempts, max_tokens=512, temperature=0.1, review_model="",
):
    first = attempts[0] if attempts else None
    review_attempt_plan = (
        _review_rotation_attempts(tuple(attempts))
        if review_model == "rotation" else ()
    )
    return APIConfig(
        api_key=first.api_key if first else "",
        api_keys=(first.api_key,) if first else (),
        base_url=first.base_url if first else "",
        model=first.model if first else "",
        fallback_models=(),
        review_model=review_model,
        healthy_combos=(),
        attempt_plan=tuple(attempts),
        review_attempt_plan=review_attempt_plan,
        max_tokens=max_tokens,
        temperature=temperature,
    )


def _smart_preflight_enough(rows, min_healthy, min_providers):
    healthy = _healthy_rows(rows)
    providers = {str(row.get("provider", "")) for row in healthy}
    return len(healthy) >= min_healthy and len(providers) >= min_providers


def _smart_preflight_attempts(
    attempts, budget, tier_limit, cache_ttl, refresh,
):
    cache_rows = load_latest_rotation_health(cache_ttl)
    cached = cached_working_attempts(attempts, cache_rows, refresh)
    remaining = max(0, budget - len(cached))
    cached_keys = {attempt.safe_tuple() for attempt in cached}
    uncached = tuple(
        attempt for attempt in attempts if attempt.safe_tuple() not in cached_keys
    )
    sampled = select_preflight_attempts(uncached, remaining, tier_limit)
    selected = []
    seen = set()
    for attempt in (*cached, *sampled):
        key = attempt.safe_tuple()
        if key in seen:
            continue
        seen.add(key)
        selected.append(attempt)
    return tuple(selected), cache_rows


async def _preflight_rotation(
    api_cfg, timeout, trace=None, concurrency=4,
    policy="smart", budget=60, min_healthy=24, min_providers=3,
    tier_limit=1, cache_ttl=21600.0, refresh=10,
):
    attempts = tuple(api_cfg.attempt_plan)
    if not attempts:
        return api_cfg
    if policy == "off":
        return api_cfg
    preflight_attempts = attempts
    cache_rows = []
    if policy == "smart":
        preflight_attempts, cache_rows = _smart_preflight_attempts(
            attempts, budget, tier_limit, cache_ttl, refresh,
        )
    if trace and trace.enabled:
        trace.log_rotation_preflight_start(
            len(preflight_attempts),
            (
                f"policy={policy} budget={budget} cache_rows={len(cache_rows)} "
                f"refresh={refresh} tier_limit={tier_limit}"
            ),
        )
    rows = await run_rotation_health(
        preflight_attempts, ["json"], timeout_s=timeout,
        max_tokens=min(api_cfg.max_tokens, 256),
        concurrency=max(1, min(len(preflight_attempts), concurrency)),
    )
    merged_rows = rows + cache_rows
    write_rotation_reports(rows)
    selected = (
        attempts_from_partial_health(attempts, merged_rows)
        if policy == "smart" else attempts_from_health(attempts, rows)
    )
    if trace and trace.enabled:
        for row in rows:
            trace.log_rotation_ranked_attempt(row)
        trace.log_ai_preflight_result(rows, len(selected))
    logger.info(
        "AI rotation preflight (%s): tested %s/%s, selected %s attempts "
        "(%s healthy)",
        policy, len(rows), len(attempts), len(selected), len(_healthy_rows(rows)),
    )
    if policy == "smart" and not _smart_preflight_enough(
        rows, min_healthy, min_providers,
    ):
        logger.warning(
            "AI rotation smart preflight below target: healthy=%s "
            "providers=%s target=%s/%s",
            len(_healthy_rows(rows)),
            len({str(row.get("provider", "")) for row in _healthy_rows(rows)}),
            min_healthy,
            min_providers,
        )
    return _rotation_api_config(
        selected, max_tokens=api_cfg.max_tokens,
        temperature=api_cfg.temperature,
        review_model=api_cfg.review_model,
    )


async def _preflight_api(
    api_cfg, timeout, trace=None, concurrency=4,
    rotation_policy="smart", rotation_budget=60,
    rotation_min_healthy=24, rotation_min_providers=3,
    rotation_tier_limit=1, rotation_cache_ttl=21600.0,
    rotation_refresh=10,
):
    if api_cfg.attempt_plan:
        return await _preflight_rotation(
            api_cfg, timeout, trace, concurrency,
            policy=rotation_policy,
            budget=rotation_budget,
            min_healthy=rotation_min_healthy,
            min_providers=rotation_min_providers,
            tier_limit=rotation_tier_limit,
            cache_ttl=rotation_cache_ttl,
            refresh=rotation_refresh,
        )
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
        concurrency=max(1, min(len(keys) * len(models), concurrency)),
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
    ai_concurrency = max(1, args.concurrency or 5)
    search_min_score, search_confidence, search_candidate_limit = (
        _search_policy_values(args)
    )

    match_cfg = MatchingConfig(
        fuzzy_threshold=args.threshold,
        brand_prefix_min=4,
        ai_verify_threshold=args.ai_threshold,
        ai_verify_policy=args.ai_verify_policy,
        ai_verify_limit=args.ai_verify_limit,
        ai_batch_size=20,
        ai_max_concurrent=ai_concurrency,
        top_k_candidates=10,
        ai_review_threshold=args.review_threshold if args.review_threshold is not None else 0.95,
        ai_search_limit=args.ai_search_limit,
        ai_search_policy=args.ai_search_policy,
        ai_search_min_candidate_score=search_min_score,
        ai_search_accept_confidence=search_confidence,
        ai_search_candidate_limit=search_candidate_limit,
    )

    if args.provider == "rotation":
        api_cfg = _rotation_api_config(
            configured_attempts("auto"),
            review_model=args.review_model or "",
        )
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
        api_cfg = asyncio.run(
            _preflight_api(
                api_cfg, args.ai_timeout, trace, ai_concurrency,
                rotation_policy=args.rotation_preflight_policy,
                rotation_budget=args.rotation_preflight_budget,
                rotation_min_healthy=args.rotation_preflight_min_healthy,
                rotation_min_providers=args.rotation_preflight_min_providers,
                rotation_tier_limit=args.rotation_preflight_tier_limit,
                rotation_cache_ttl=args.rotation_preflight_cache_ttl,
                rotation_refresh=args.rotation_preflight_refresh,
            )
        )

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
