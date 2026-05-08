"""Main entry point for the drug matching pipeline."""
import argparse
import asyncio

from drug_matcher.config import MatchingConfig, APIConfig, setup_logging
from drug_matcher.pipeline import MatchPipeline


def parse_args():
    parser = argparse.ArgumentParser(description="MediCompare - Drug Matching Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of drugs to process")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--threshold", type=int, default=80, help="Fuzzy matching threshold (default: 80)")
    parser.add_argument("--ai-threshold", type=float, default=90.0, help="AI verification threshold (default: 90)")
    parser.add_argument("--output", default=None, help="Output CSV path")
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(args.log_level)

    match_cfg = MatchingConfig(
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

    pipeline = MatchPipeline(cfg=match_cfg, api_cfg=api_cfg, limit=args.limit)
    result = asyncio.run(pipeline.run_full(output_path=args.output))

    return result


if __name__ == "__main__":
    main()
