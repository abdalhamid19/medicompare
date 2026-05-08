"""Main entry point for the drug matching pipeline."""
import argparse
import asyncio

from drug_matcher.config import MatchingConfig, APIConfig, setup_logging, load_env, resolve_api_config, PROVIDERS
from drug_matcher.pipeline import MatchPipeline


def parse_args():
    parser = argparse.ArgumentParser(description="MediCompare - Drug Matching Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of drugs to process")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--threshold", type=int, default=80, help="Fuzzy matching threshold (default: 80)")
    parser.add_argument("--ai-threshold", type=float, default=90.0, help="AI verification threshold (default: 90)")
    parser.add_argument("--output", default=None, help="Output CSV path")
    parser.add_argument("--trace", action="store_true", help="Enable detailed algorithm trace (CSV+TXT in output/trace/)")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI verification and search (algorithm only)")
    parser.add_argument("--model", default=None, help="AI model to use (e.g. openai/gpt-4o-mini, big-pickle)")
    parser.add_argument("--provider", default=None, choices=list(PROVIDERS.keys()), help="API provider (openrouter, opencode, agentrouter, custom)")
    parser.add_argument("--api-key", default=None, help="API key (overrides .env)")
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
    )

    resolved = resolve_api_config(
        provider=args.provider or "",
        model=args.model or "",
        api_key=args.api_key or "",
    )
    api_cfg = APIConfig(
        api_key=resolved["api_key"],
        base_url=resolved["base_url"],
        model=resolved["model"],
        max_tokens=512,
        temperature=0.1,
    )

    pipeline = MatchPipeline(cfg=match_cfg, api_cfg=api_cfg, limit=args.limit)
    if args.trace:
        from drug_matcher.trace_log import MatchTraceLog
        pipeline._trace = MatchTraceLog(enabled=True)
    result = asyncio.run(pipeline.run_full(output_path=args.output, skip_ai=args.no_ai))

    return result


if __name__ == "__main__":
    main()
