"""Main entry point for the drug matching pipeline."""
import argparse
import asyncio
import logging

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
    return parser.parse_args()


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
    )

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
        review_model=args.review_model or "",
        max_tokens=512,
        temperature=0.1,
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
    if args.trace:
        from drug_matcher.trace_log import MatchTraceLog
        pipeline._trace = MatchTraceLog(enabled=True)
    result = asyncio.run(pipeline.run_full(output_path=args.output, skip_ai=args.no_ai))

    return result


if __name__ == "__main__":
    main()
