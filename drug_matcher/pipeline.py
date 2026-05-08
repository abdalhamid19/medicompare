"""Pipeline orchestrator - coordinates matching, verification, and output."""
import asyncio
import logging
import re
import sys
from typing import Any

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

from .config import MatchingConfig, APIConfig, Paths, load_env

logger = logging.getLogger("medicompare")
from .normalizer import normalize, parse_drug, components_match
from .indexer import DrugIndex
from .verifier import AIVerifier


class MatchPipeline:
    """Full matching pipeline with optional AI verification."""

    __slots__ = ("_cfg", "_api_cfg", "_drugs_df", "_index", "_verifier", "_results", "_limit")

    def __init__(
        self,
        cfg: MatchingConfig | None = None,
        api_cfg: APIConfig | None = None,
        limit: int | None = None,
    ):
        load_env()
        self._cfg = cfg or MatchingConfig()
        self._api_cfg = api_cfg or APIConfig()
        self._limit = limit
        self._drugs_df: pd.DataFrame | None = None
        self._index: DrugIndex | None = None
        self._verifier: AIVerifier | None = None
        self._results: pd.DataFrame | None = None

    def load_data(self, drugs_path: str | None = None, tawreed_path: str | None = None):
        """Load and prepare data sources."""
        paths = Paths()
        drugs_path = drugs_path or paths.drugs_csv
        tawreed_path = tawreed_path or paths.tawreed_csv

        drugs = pd.read_csv(drugs_path, encoding="utf-8-sig")
        drugs.columns = ["code", "drug_name"]

        tawreed = pd.read_csv(tawreed_path, encoding="utf-8-sig")

        if self._limit:
            drugs = drugs.head(self._limit)
            logger.info(f"Limit applied: processing {len(drugs)} drugs")
        self._drugs_df = drugs
        self._index = DrugIndex(tawreed, self._cfg)
        logger.info(f"Loaded {len(drugs)} drugs, {self._index.size} tawreed products")

    def run_matching(self) -> pd.DataFrame:
        """Phase 1: Algorithmic matching using brand index + fuzzy search."""
        if self._drugs_df is None or self._index is None:
            raise RuntimeError("Call load_data() first")

        results = []
        stats = {"brand_index": 0, "fuzzy": 0, "no_match": 0}

        for row in self._drugs_df.itertuples(index=False):
            code = str(row.code)
            drug_name = str(row.drug_name)
            best_rec, score, method = self._index.best_match(drug_name)

            if best_rec is not None:
                results.append({
                    "code": code,
                    "drug_name": drug_name,
                    "matched_product_name_en": best_rec["product_name_en"],
                    "matched_product_name_ar": best_rec["product_name_ar"],
                    "matched_store_product_id": best_rec["store_product_id"],
                    "match_score": round(score, 1),
                    "verified": "algo_match",
                    "match_method": method,
                })
                if "brand" in method:
                    stats["brand_index"] += 1
                else:
                    stats["fuzzy"] += 1
            else:
                results.append({
                    "code": code,
                    "drug_name": drug_name,
                    "matched_product_name_en": "",
                    "matched_product_name_ar": "",
                    "matched_store_product_id": "",
                    "match_score": "",
                    "verified": "",
                    "match_method": method,
                })
                stats["no_match"] += 1

        self._results = pd.DataFrame(results)
        logger.info(f"Phase 1 done: {stats}")
        matched = self._results[self._results["matched_product_name_en"] != ""]
        logger.info(f"  Matched: {len(matched)}, Not matched: {len(self._results) - len(matched)}")
        return self._results

    async def run_ai_verification(self) -> pd.DataFrame:
        """Phase 2: AI verification of matches below threshold."""
        if self._results is None:
            raise RuntimeError("Call run_matching() first")

        if not self._api_cfg.api_key:
            logger.warning("No API key - skipping AI verification")
            return self._results

        # Select matches to verify (below threshold)
        matched = self._results[self._results["matched_product_name_en"] != ""].copy()
        scores = pd.to_numeric(matched["match_score"], errors="coerce")
        to_verify = matched[scores < self._cfg.ai_verify_threshold]

        if len(to_verify) == 0:
            logger.info("No matches below AI verification threshold")
            return self._results

        logger.info(f"Phase 2: Verifying {len(to_verify)} matches with AI (threshold={self._cfg.ai_verify_threshold})")

        # Build verification batches
        verify_items = []
        for idx, row in to_verify.iterrows():
            verify_items.append((row["drug_name"], row["matched_product_name_en"], idx))

        async with AIVerifier(self._api_cfg, max_concurrent=self._cfg.ai_max_concurrent) as verifier:
            # Process in batches
            all_results = []
            batch_size = self._cfg.ai_batch_size
            for i in range(0, len(verify_items), batch_size):
                batch = verify_items[i:i + batch_size]
                batch_results = await verifier.verify_batch(batch)
                all_results.extend(batch_results)
                done = min(i + batch_size, len(verify_items))
                logger.info(f"  Verified {done}/{len(verify_items)}")

            # Apply results
            rejected = 0
            corrected = 0
            for vr in all_results:
                idx = vr.get("row_idx")
                if idx is None:
                    continue

                if not vr["is_correct"]:
                    # Try to find better match with AI
                    drug_name = self._results.at[idx, "drug_name"]
                    parsed = parse_drug(drug_name)
                    norm = parsed.normalized

                    # Get top candidates
                    candidates = self._index.fuzzy_match(norm, top_k=5)
                    # Filter by component match
                    valid_candidates = []
                    for rec, score, cidx in candidates:
                        is_ok, _ = components_match(parsed, self._index._parsed_cache[cidx], self._cfg.brand_prefix_min)
                        if is_ok:
                            valid_candidates.append((rec, score, cidx))

                    if valid_candidates:
                        ai_result = await verifier.find_better_match(drug_name, valid_candidates)
                        if ai_result and ai_result.get("record"):
                            rec = ai_result["record"]
                            self._results.at[idx, "matched_product_name_en"] = rec["product_name_en"]
                            self._results.at[idx, "matched_product_name_ar"] = rec["product_name_ar"]
                            self._results.at[idx, "matched_store_product_id"] = rec["store_product_id"]
                            self._results.at[idx, "match_score"] = round(ai_result["score"], 1)
                            self._results.at[idx, "verified"] = "ai_corrected"
                            self._results.at[idx, "match_method"] = "ai_verified"
                            corrected += 1
                            continue

                    # No better match found - remove
                    self._results.at[idx, "matched_product_name_en"] = ""
                    self._results.at[idx, "matched_product_name_ar"] = ""
                    self._results.at[idx, "matched_store_product_id"] = ""
                    self._results.at[idx, "match_score"] = ""
                    self._results.at[idx, "verified"] = "ai_rejected"
                    self._results.at[idx, "match_method"] = "ai_verified"
                    rejected += 1
                else:
                    self._results.at[idx, "verified"] = "ai_confirmed"
                    self._results.at[idx, "match_method"] = "ai_verified"

            logger.info(f"  AI Results: confirmed={len(all_results)-rejected-corrected}, corrected={corrected}, rejected={rejected}")

        return self._results

    async def run_ai_search_unmatched(self) -> pd.DataFrame:
        """Phase 3: AI searches for matches among previously unmatched items."""
        if self._results is None:
            raise RuntimeError("Call run_matching() first")

        if not self._api_cfg.api_key:
            logger.warning("No API key - skipping AI search")
            return self._results

        unmatched = self._results[
            (self._results["matched_product_name_en"].isna()) |
            (self._results["matched_product_name_en"] == "")
        ].copy()

        if len(unmatched) == 0:
            logger.info("No unmatched items to search")
            return self._results

        logger.info(f"Phase 3: AI searching for matches among {len(unmatched)} unmatched items")

        async with AIVerifier(self._api_cfg, max_concurrent=self._cfg.ai_max_concurrent) as verifier:
            found = 0
            batch_size = self._cfg.ai_batch_size

            items = list(unmatched.iterrows())
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                for _, row in batch:
                    drug_name = row["drug_name"]
                    parsed = parse_drug(drug_name)
                    norm = parsed.normalized

                    if not norm or len(norm) < 3:
                        continue

                    # Get fuzzy candidates with lower threshold
                    candidates = []
                    for scorer in [fuzz.token_set_ratio, fuzz.token_sort_ratio]:
                        results = process.extract(norm, self._index._norms, scorer=scorer, limit=5)
                        for match_name, score, idx in results:
                            if score >= 70:
                                is_ok, _ = components_match(parsed, self._index._parsed_cache[idx], self._cfg.brand_prefix_min)
                                if is_ok:
                                    candidates.append((self._index._records[idx], score, idx))

                    # Also try brand index
                    brand_hits = self._index.lookup_by_brand(parsed)
                    for rec, idx in brand_hits:
                        score = fuzz.token_sort_ratio(norm, self._index._norms[idx])
                        if score >= 65:
                            candidates.append((rec, score, idx))

                    # Deduplicate
                    seen_ids = set()
                    unique_candidates = []
                    for rec, score, idx in candidates:
                        sid = rec["store_product_id"]
                        if sid not in seen_ids:
                            seen_ids.add(sid)
                            unique_candidates.append((rec, score, idx))

                    if not unique_candidates:
                        continue

                    # Ask AI to pick best or reject all
                    ai_result = await verifier.find_better_match(drug_name, unique_candidates)
                    if ai_result and ai_result.get("record") and ai_result.get("confidence", 0) >= 0.7:
                        rec = ai_result["record"]
                        idx = row.name
                        self._results.at[idx, "matched_product_name_en"] = rec["product_name_en"]
                        self._results.at[idx, "matched_product_name_ar"] = rec["product_name_ar"]
                        self._results.at[idx, "matched_store_product_id"] = rec["store_product_id"]
                        self._results.at[idx, "match_score"] = round(ai_result.get("score", 0), 1)
                        self._results.at[idx, "verified"] = "ai_found"
                        self._results.at[idx, "match_method"] = "ai_search"
                        found += 1

                done = min(i + batch_size, len(items))
                logger.info(f"  Searched {done}/{len(items)}, found {found}")

            logger.info(f"  AI Search found {found} new matches")

        return self._results

    def run_post_cleanup(self) -> pd.DataFrame:
        """Remove algorithmically detectable wrong matches (dosage, qty, volume, weight, brand mismatches)."""
        if self._results is None:
            raise RuntimeError("Call run_matching() first")

        m = self._results[self._results["matched_product_name_en"].notna() & (self._results["matched_product_name_en"] != "")].copy()
        if len(m) == 0:
            return self._results

        removed = 0
        for idx, r in m.iterrows():
            d_comp = parse_drug(r["drug_name"])
            m_comp = parse_drug(r["matched_product_name_en"])
            is_ok, reason = components_match(d_comp, m_comp, self._cfg.brand_prefix_min)

            # Also check brand prefix (first 4 chars)
            d_brand = re.sub(r"[^A-Z0-9]", "", d_comp.brand)
            m_brand = re.sub(r"[^A-Z0-9]", "", m_comp.brand)
            brand_mismatch = False
            if d_brand and m_brand and len(d_brand) >= 4 and len(m_brand) >= 4:
                if d_brand[:4] != m_brand[:4]:
                    if d_brand not in m_brand and m_brand not in d_brand:
                        brand_mismatch = True

            if not is_ok or brand_mismatch:
                self._results.at[idx, "matched_product_name_en"] = np.nan
                self._results.at[idx, "matched_product_name_ar"] = np.nan
                self._results.at[idx, "matched_store_product_id"] = np.nan
                self._results.at[idx, "match_score"] = np.nan
                self._results.at[idx, "verified"] = np.nan
                self._results.at[idx, "match_method"] = np.nan
                removed += 1

        logger.info(f"Post-cleanup: removed {removed} wrong matches")
        return self._results

    def save(self, output_path: str | None = None) -> str:
        """Save results to CSV."""
        if self._results is None:
            raise RuntimeError("No results to save")
        path = output_path or str(Paths().output_csv)
        self._results.to_csv(path, index=False, encoding="utf-8-sig")
        logger.info(f"Saved to {path}")
        return path

    def print_stats(self):
        """Print final statistics."""
        if self._results is None:
            return

        total = len(self._results)
        has_match = self._results["matched_product_name_en"].notna() & (self._results["matched_product_name_en"] != "")
        matched = self._results[has_match]
        not_matched = self._results[~has_match]

        logger.info(f"{'='*50}")
        logger.info(f"FINAL RESULTS")
        logger.info(f"{'='*50}")
        logger.info(f"Total drugs: {total}")
        logger.info(f"Matched: {len(matched)} ({len(matched)/total*100:.1f}%)")
        logger.info(f"Not matched: {len(not_matched)} ({len(not_matched)/total*100:.1f}%)")

        if len(matched) > 0:
            scores = pd.to_numeric(matched["match_score"], errors="coerce")
            logger.info(f"Score distribution:")
            logger.info(f"  100:   {(scores == 100).sum()}")
            logger.info(f"  95-99: {((scores >= 95) & (scores < 100)).sum()}")
            logger.info(f"  90-94: {((scores >= 90) & (scores < 95)).sum()}")
            logger.info(f"  80-89: {((scores >= 80) & (scores < 90)).sum()}")
            logger.info(f"  70-79: {((scores >= 70) & (scores < 80)).sum()}")
            logger.info(f"  <70:   {(scores < 70).sum()}")

        logger.info(f"Verification breakdown:")
        logger.info(self._results["verified"].value_counts(dropna=False).to_string())

        logger.info(f"Method breakdown:")
        logger.info(self._results["match_method"].value_counts(dropna=False).to_string())

    async def run_full(self, drugs_path: str | None = None, tawreed_path: str | None = None, output_path: str | None = None) -> pd.DataFrame:
        """Run the complete pipeline."""
        self.load_data(drugs_path, tawreed_path)
        self.run_matching()
        await self.run_ai_verification()
        await self.run_ai_search_unmatched()
        self.run_post_cleanup()
        self.save(output_path)
        self.print_stats()
        return self._results
