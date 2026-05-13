"""Run the AI verification phase."""
import argparse
import asyncio
import logging

from drug_matcher.config import MatchingConfig, APIConfig, setup_logging, load_env, resolve_api_config, PROVIDERS
from drug_matcher.pipeline import MatchPipeline

logger = logging.getLogger("medicompare")


def parse_args():
    parser = argparse.ArgumentParser(description="MediCompare - AI Verification Pipeline")
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
    parser.add_argument("--model", default=None, help="AI model to use (e.g. openai/gpt-4o-mini, big-pickle)")
    parser.add_argument("--provider", default=None, choices=list(PROVIDERS.keys()), help="API provider (groq, opencode, openrouter, custom)")
    parser.add_argument("--api-key", default=None, help="API key (overrides .env)")
    parser.add_argument("--review-model", default=None, help="Second AI model for cross-review (e.g. big-pickle)")
    parser.add_argument("--review-threshold", type=float, default=None, help="Review AI decisions with confidence below this (default: 1.0)")
    parser.add_argument("--ai-search-policy", choices=["safe", "review-candidates", "expanded", "aggressive"], default="review-candidates", help="AI search expansion policy")
    parser.add_argument("--ai-search-min-candidate-score", type=float, default=None, help="Minimum candidate score before AI search")
    parser.add_argument("--ai-search-accept-confidence", type=float, default=None, help="Minimum AI confidence to accept search match")
    parser.add_argument("--ai-search-candidate-limit", type=int, default=None, help="Candidate limit per search strategy before AI search")
    parser.add_argument("--ai-search-review-candidate-min-score", type=float, default=None, help="Minimum review-candidate score before AI search")
    parser.add_argument("--ai-search-review-accept-confidence", type=float, default=None, help="Minimum AI confidence to accept component-mismatch search matches")
    parser.add_argument("--ai-search-review-candidate-limit", type=int, default=None, help="Maximum component-mismatch review candidates per item")
    return parser.parse_args()


def _search_policy_values(args):
    defaults = {
        "safe": (80.0, 0.75, 5),
        "review-candidates": (80.0, 0.75, 8),
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


async def main():
    args = parse_args()
    setup_logging(args.log_level)
    load_env()
    search_min_score, search_confidence, search_candidate_limit = (
        _search_policy_values(args)
    )

    cfg = MatchingConfig(
        fuzzy_threshold=args.threshold,
        brand_prefix_min=4,
        ai_verify_threshold=args.ai_threshold,
        ai_verify_policy=args.ai_verify_policy,
        ai_verify_limit=args.ai_verify_limit,
        ai_batch_size=20,
        ai_max_concurrent=5,
        top_k_candidates=10,
        ai_review_threshold=args.review_threshold if args.review_threshold is not None else 0.95,
        ai_search_policy=args.ai_search_policy,
        ai_search_min_candidate_score=search_min_score,
        ai_search_accept_confidence=search_confidence,
        ai_search_candidate_limit=search_candidate_limit,
        ai_search_review_candidate_min_score=(
            args.ai_search_review_candidate_min_score
            if args.ai_search_review_candidate_min_score is not None else 68.0
        ),
        ai_search_review_accept_confidence=(
            args.ai_search_review_accept_confidence
            if args.ai_search_review_accept_confidence is not None else 0.85
        ),
        ai_search_review_candidate_limit=(
            args.ai_search_review_candidate_limit
            if args.ai_search_review_candidate_limit is not None else 8
        ),
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

    pipeline = MatchPipeline(cfg=cfg, api_cfg=api_cfg, limit=args.limit, start=start, end=end)
    if args.trace:
        from drug_matcher.trace_log import MatchTraceLog
        pipeline._trace = MatchTraceLog(enabled=True)
    pipeline.load_data()
    pipeline.run_matching()
    await pipeline.run_ai_verification()
    await pipeline.run_ai_search_unmatched()
    await pipeline.run_ai_review()
    pipeline.run_post_cleanup()
    pipeline.save(args.output)
    pipeline.print_stats()

if __name__ == "__main__":
    asyncio.run(main())
