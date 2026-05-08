"""Run the AI verification phase."""
import argparse
import asyncio
from drug_matcher.config import MatchingConfig, APIConfig, setup_logging, load_env
from drug_matcher.pipeline import MatchPipeline


def parse_args():
    parser = argparse.ArgumentParser(description="MediCompare - AI Verification Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of drugs to process")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--threshold", type=int, default=80, help="Fuzzy matching threshold (default: 80)")
    parser.add_argument("--ai-threshold", type=float, default=90.0, help="AI verification threshold (default: 90)")
    parser.add_argument("--output", default=None, help="Output CSV path")
    parser.add_argument("--trace", action="store_true", help="Enable detailed algorithm trace (CSV+TXT in output/trace/)")
    return parser.parse_args()


async def main():
    args = parse_args()
    setup_logging(args.log_level)
    load_env()

    cfg = MatchingConfig(
        fuzzy_threshold=args.threshold,
        brand_prefix_min=4,
        ai_verify_threshold=args.ai_threshold,
        ai_batch_size=20,
        ai_max_concurrent=5,
        top_k_candidates=10,
    )
    api_cfg = APIConfig(
        max_tokens=512,
        temperature=0.1,
    )

    pipeline = MatchPipeline(cfg=cfg, api_cfg=api_cfg, limit=args.limit)
    if args.trace:
        from drug_matcher.trace_log import MatchTraceLog
        pipeline._trace = MatchTraceLog(enabled=True)
    pipeline.load_data()
    pipeline.run_matching()
    await pipeline.run_ai_verification()
    await pipeline.run_ai_search_unmatched()
    pipeline.run_post_cleanup()
    pipeline.save(args.output)
    pipeline.print_stats()

if __name__ == "__main__":
    asyncio.run(main())
