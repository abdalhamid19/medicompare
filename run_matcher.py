"""Main entry point for the drug matching pipeline."""
import asyncio

from drug_matcher.config import MatchingConfig, APIConfig
from drug_matcher.pipeline import MatchPipeline


def main():
    # Configuration
    match_cfg = MatchingConfig(
        fuzzy_threshold=80,
        brand_prefix_min=4,
        ai_verify_threshold=90.0,  # AI verifies matches below 90%
        ai_batch_size=20,
        ai_max_concurrent=5,
        top_k_candidates=10,
    )

    api_cfg = APIConfig(
        max_tokens=512,
        temperature=0.1,
    )

    pipeline = MatchPipeline(cfg=match_cfg, api_cfg=api_cfg)

    # Run full pipeline
    result = asyncio.run(pipeline.run_full())

    return result


if __name__ == "__main__":
    main()
