"""AI verification and search steps extracted from pipeline."""
import logging

import pandas as pd
from rapidfuzz import fuzz, process

from .config import MatchingConfig, APIConfig
from .normalizer import parse_drug, components_match
from .indexer import DrugIndex
from .verifier import AIVerifier

logger = logging.getLogger("medicompare")


async def run_ai_verification(
    results: pd.DataFrame,
    index: DrugIndex,
    cfg: MatchingConfig,
    api_cfg: APIConfig,
) -> pd.DataFrame:
    """AI verification of matches below threshold."""
    if not api_cfg.api_key:
        logger.warning("No API key - skipping AI verification")
        return results
    to_verify = _select_for_verification(results, cfg)
    if len(to_verify) == 0:
        logger.info("No matches below AI verification threshold")
        return results
    logger.info(
        f"Phase 2: Verifying {len(to_verify)} matches "
        f"with AI (threshold={cfg.ai_verify_threshold})",
    )
    items = _build_verify_items(to_verify)
    async with AIVerifier(
        api_cfg, max_concurrent=cfg.ai_max_concurrent,
    ) as verifier:
        all_results = await _batch_verify(verifier, items, cfg)
        rejected, corrected = await _apply_verification(
            verifier, results, index, all_results, cfg,
        )
        logger.info(
            f"  AI Results: "
            f"confirmed={len(all_results)-rejected-corrected}, "
            f"corrected={corrected}, rejected={rejected}",
        )
    return results


async def run_ai_search(
    results: pd.DataFrame,
    index: DrugIndex,
    cfg: MatchingConfig,
    api_cfg: APIConfig,
) -> pd.DataFrame:
    """AI searches for matches among unmatched items."""
    if not api_cfg.api_key:
        logger.warning("No API key - skipping AI search")
        return results
    unmatched = _get_unmatched(results)
    if len(unmatched) == 0:
        logger.info("No unmatched items to search")
        return results
    logger.info(
        f"Phase 3: AI searching for matches "
        f"among {len(unmatched)} unmatched items",
    )
    async with AIVerifier(
        api_cfg, max_concurrent=cfg.ai_max_concurrent,
    ) as verifier:
        found = await _search_batch(
            verifier, results, index, unmatched, cfg,
        )
        logger.info(f"  AI Search found {found} new matches")
    return results


# --- helpers ---

def _select_for_verification(results, cfg):
    matched = results[results["matched_product_name_en"] != ""].copy()
    scores = pd.to_numeric(matched["match_score"], errors="coerce")
    return matched[scores < cfg.ai_verify_threshold]


def _build_verify_items(to_verify):
    return [
        (row["drug_name"], row["matched_product_name_en"], idx)
        for idx, row in to_verify.iterrows()
    ]


async def _batch_verify(verifier, items, cfg):
    all_results = []
    batch_size = cfg.ai_batch_size
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        results = await verifier.verify_batch(batch)
        all_results.extend(results)
        done = min(i + batch_size, len(items))
        logger.info(f"  Verified {done}/{len(items)}")
    return all_results


async def _apply_verification(verifier, results, index, all_results, cfg):
    rejected = 0
    corrected = 0
    for vr in all_results:
        idx = vr.get("row_idx")
        if idx is None:
            continue
        if not vr["is_correct"]:
            c, r = await _handle_rejected(
                verifier, results, index, idx, cfg,
            )
            corrected += c
            rejected += r
        else:
            results.at[idx, "verified"] = "ai_confirmed"
            results.at[idx, "match_method"] = "ai_verified"
    return rejected, corrected


async def _handle_rejected(verifier, results, index, idx, cfg):
    drug_name = results.at[idx, "drug_name"]
    parsed = parse_drug(drug_name)
    norm = parsed.normalized
    candidates = index.fuzzy_match(norm, top_k=5)
    valid = [
        (rec, score, cidx) for rec, score, cidx in candidates
        if components_match(
            parsed, index.get_parsed(cidx),
            cfg.brand_prefix_min,
        )[0]
    ]
    if valid:
        ai_result = await verifier.find_better_match(drug_name, valid)
        if ai_result and ai_result.get("record"):
            _apply_correction(results, idx, ai_result)
            return 1, 0
    _clear_match(results, idx)
    results.at[idx, "verified"] = "ai_rejected"
    results.at[idx, "match_method"] = "ai_verified"
    return 0, 1


def _apply_correction(results, idx, ai_result):
    rec = ai_result["record"]
    results.at[idx, "matched_product_name_en"] = rec["product_name_en"]
    results.at[idx, "matched_product_name_ar"] = rec["product_name_ar"]
    results.at[idx, "matched_store_product_id"] = rec["store_product_id"]
    results.at[idx, "match_score"] = round(ai_result["score"], 1)
    results.at[idx, "verified"] = "ai_corrected"
    results.at[idx, "match_method"] = "ai_verified"


def _clear_match(results, idx):
    results.at[idx, "matched_product_name_en"] = ""
    results.at[idx, "matched_product_name_ar"] = ""
    results.at[idx, "matched_store_product_id"] = ""
    results.at[idx, "match_score"] = ""


def _get_unmatched(results):
    return results[
        (results["matched_product_name_en"].isna()) |
        (results["matched_product_name_en"] == "")
    ].copy()


async def _search_batch(verifier, results, index, unmatched, cfg):
    found = 0
    batch_size = cfg.ai_batch_size
    items = list(unmatched.iterrows())
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        for _, row in batch:
            found += await _try_search_one(
                verifier, results, index, row, cfg,
            )
        done = min(i + batch_size, len(items))
        logger.info(f"  Searched {done}/{len(items)}, found {found}")
    return found


async def _try_search_one(verifier, results, index, row, cfg):
    drug_name = row["drug_name"]
    parsed = parse_drug(drug_name)
    norm = parsed.normalized
    if not norm or len(norm) < 3:
        return 0
    candidates = _search_candidates(parsed, norm, index, cfg)
    if not candidates:
        return 0
    ai_result = await verifier.find_better_match(drug_name, candidates)
    if ai_result and ai_result.get("record") and ai_result.get("confidence", 0) >= 0.7:
        _apply_search_result(results, row.name, ai_result)
        return 1
    return 0


def _search_candidates(parsed, norm, index, cfg):
    """Gather fuzzy + brand candidates for unmatched search."""
    candidates = []
    for scorer in [fuzz.token_set_ratio, fuzz.token_sort_ratio]:
        results = process.extract(
            norm, index.norms,
            scorer=scorer, limit=5,
        )
        for _, score, idx in results:
            if score >= 70 and components_match(
                parsed, index.get_parsed(idx),
                cfg.brand_prefix_min,
            )[0]:
                candidates.append(
                    (index.get_record(idx), score, idx),
                )
    brand_hits = index.lookup_by_brand(parsed)
    for rec, idx in brand_hits:
        score = index.score_candidate(norm, idx)
        if score >= 65:
            candidates.append((rec, score, idx))
    return _dedupe_candidates(candidates)


def _dedupe_candidates(candidates):
    seen = set()
    out = []
    for rec, score, idx in candidates:
        sid = rec["store_product_id"]
        if sid not in seen:
            seen.add(sid)
            out.append((rec, score, idx))
    return out


def _apply_search_result(results, idx, ai_result):
    rec = ai_result["record"]
    results.at[idx, "matched_product_name_en"] = rec["product_name_en"]
    results.at[idx, "matched_product_name_ar"] = rec["product_name_ar"]
    results.at[idx, "matched_store_product_id"] = rec["store_product_id"]
    results.at[idx, "match_score"] = round(ai_result.get("score", 0), 1)
    results.at[idx, "verified"] = "ai_found"
    results.at[idx, "match_method"] = "ai_search"
