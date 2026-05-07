"""Run the AI verification phase."""
import asyncio
from drug_matcher.config import MatchingConfig, APIConfig
from drug_matcher.pipeline import MatchPipeline

async def main():
    cfg = MatchingConfig(
        fuzzy_threshold=80,
        brand_prefix_min=4,
        ai_verify_threshold=90.0,
        ai_batch_size=20,
        ai_max_concurrent=5,
        top_k_candidates=10,
    )
    api_cfg = APIConfig(
        max_tokens=512,
        temperature=0.1,
    )

    pipeline = MatchPipeline(cfg=cfg, api_cfg=api_cfg)
    pipeline.load_data()
    pipeline.run_matching()
    await pipeline.run_ai_verification()
    await pipeline.run_ai_search_unmatched()
    pipeline.run_post_cleanup()
    pipeline.save()
    pipeline.print_stats()

if __name__ == "__main__":
    asyncio.run(main())
