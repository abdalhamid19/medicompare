"""Pipeline orchestrator - coordinates matching, verification, and output."""
import logging
import re

import numpy as np
import pandas as pd

from .config import MatchingConfig, APIConfig, Paths, load_env
from .normalizer import parse_drug, components_match
from .indexer import DrugIndex
from .ai_steps import run_ai_verification, run_ai_search
from .trace_log import MatchTraceLog

logger = logging.getLogger("medicompare")

_RESULT_COLS = [
    "code", "drug_name", "matched_product_name_en",
    "matched_product_name_ar", "matched_store_product_id",
    "match_score", "verified", "match_method",
]


class MatchPipeline:
    """Full matching pipeline with optional AI verification."""

    __slots__ = (
        "_cfg", "_api_cfg", "_drugs_df", "_index",
        "_results", "_limit", "_trace",
    )

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
        self._results: pd.DataFrame | None = None
        self._trace: MatchTraceLog | None = None

    # --- data loading ---

    def load_data(
        self, drugs_path: str | None = None,
        tawreed_path: str | None = None,
    ):
        """Load and prepare data sources."""
        paths = Paths()
        drugs_path = drugs_path or paths.drugs_csv
        tawreed_path = tawreed_path or paths.tawreed_csv
        drugs = pd.read_csv(
            drugs_path, encoding="utf-8-sig",
            dtype=str, usecols=[0, 1],
        )
        drugs.columns = ["code", "drug_name"]
        tawreed = pd.read_csv(
            tawreed_path, encoding="utf-8-sig",
            dtype=str, usecols=[0, 1, 2],
        )
        if self._limit:
            drugs = drugs.head(self._limit)
            logger.info(f"Limit applied: processing {len(drugs)} drugs")
        self._drugs_df = drugs
        self._index = DrugIndex(tawreed, self._cfg)
        logger.info(
            f"Loaded {len(drugs)} drugs, "
            f"{self._index.size} tawreed products",
        )

    # --- Phase 1: algorithmic matching ---

    def run_matching(self) -> pd.DataFrame:
        """Algorithmic matching using brand index + fuzzy search."""
        self._require_data()
        results = []
        stats = {"brand_index": 0, "fuzzy": 0, "no_match": 0}
        for row in self._drugs_df.itertuples(index=False):
            rec, score, method = self._match_one(row, stats)
            results.append(self._make_row(row, rec, score, method, stats))
        self._results = pd.DataFrame(results)
        logger.info(f"Phase 1 done: {stats}")
        self._log_match_counts()
        return self._results

    def _match_one(self, row, stats):
        """Match one drug, with trace if enabled."""
        drug_name = str(row.drug_name)
        if not self._trace or not self._trace.enabled:
            return self._index.best_match(drug_name)
        code = str(row.code)
        rec, score, method, trace = self._index.best_match_detailed(drug_name)
        self._trace.log_normalization(
            code, drug_name, trace["norm"], trace["brand"],
        )
        self._trace.log_brand_lookup(
            code, drug_name, trace["norm"],
            trace["brand"], trace["brand_hits"],
        )
        for scorer_name, result in trace["fuzzy_steps"]:
            self._trace.log_fuzzy_step(
                code, drug_name, trace["norm"],
                trace["brand"], scorer_name, result,
            )
        for cidx, ok, reason in trace["component_checks"]:
            self._trace.log_component_check(
                code, drug_name, trace["norm"],
                trace["brand"], cidx, ok, reason,
            )
        match_name = rec["product_name_en"] if rec else None
        self._trace.log_final(
            code, drug_name, trace["norm"],
            trace["brand"], match_name, score, method,
        )
        return rec, score, method

    def _make_row(self, row, rec, score, method, stats):
        code = str(row.code)
        drug_name = str(row.drug_name)
        if rec is not None:
            key = "brand_index" if "brand" in method else "fuzzy"
            stats[key] += 1
            return {
                "code": code, "drug_name": drug_name,
                "matched_product_name_en": rec["product_name_en"],
                "matched_product_name_ar": rec["product_name_ar"],
                "matched_store_product_id": rec["store_product_id"],
                "match_score": round(score, 1),
                "verified": "algo_match",
                "match_method": method,
            }
        stats["no_match"] += 1
        return {
            "code": code, "drug_name": drug_name,
            "matched_product_name_en": "",
            "matched_product_name_ar": "",
            "matched_store_product_id": "",
            "match_score": "", "verified": "",
            "match_method": method,
        }

    def _log_match_counts(self):
        matched = self._results[
            self._results["matched_product_name_en"] != ""
        ]
        total = len(self._results)
        logger.info(
            f"  Matched: {len(matched)}, "
            f"Not matched: {total - len(matched)}",
        )

    # --- Phase 2 & 3: AI steps (delegated) ---

    async def run_ai_verification(self) -> pd.DataFrame:
        """AI verification of matches below threshold."""
        self._require_results()
        self._results = await run_ai_verification(
            self._results, self._index, self._cfg, self._api_cfg,
        )
        return self._results

    async def run_ai_search_unmatched(self) -> pd.DataFrame:
        """AI searches for matches among unmatched items."""
        self._require_results()
        self._results = await run_ai_search(
            self._results, self._index, self._cfg, self._api_cfg,
        )
        return self._results

    # --- Phase 4: post cleanup ---

    def run_post_cleanup(self) -> pd.DataFrame:
        """Remove algorithmically detectable wrong matches."""
        self._require_results()
        matched = self._results[
            self._results["matched_product_name_en"].notna() &
            (self._results["matched_product_name_en"] != "")
        ].copy()
        if len(matched) == 0:
            return self._results
        removed = 0
        for idx, r in matched.iterrows():
            if self._is_cleanup_mismatch(r):
                self._nan_out_row(idx)
                removed += 1
        logger.info(f"Post-cleanup: removed {removed} wrong matches")
        return self._results

    def _is_cleanup_mismatch(self, r):
        d_comp = parse_drug(r["drug_name"])
        m_comp = parse_drug(r["matched_product_name_en"])
        is_ok, _ = components_match(
            d_comp, m_comp, self._cfg.brand_prefix_min,
        )
        d_brand = re.sub(r"[^A-Z0-9]", "", d_comp.brand)
        m_brand = re.sub(r"[^A-Z0-9]", "", m_comp.brand)
        brand_mismatch = (
            d_brand and m_brand
            and len(d_brand) >= 4 and len(m_brand) >= 4
            and d_brand[:4] != m_brand[:4]
            and d_brand not in m_brand
            and m_brand not in d_brand
        )
        return not is_ok or brand_mismatch

    def _nan_out_row(self, idx):
        for col in _RESULT_COLS[2:]:
            self._results.at[idx, col] = np.nan

    # --- save & stats ---

    def save(self, output_path: str | None = None) -> str:
        """Save results to CSV."""
        if self._results is None:
            raise RuntimeError("No results to save")
        path = output_path or str(Paths().output_csv)
        self._results.to_csv(path, index=False, encoding="utf-8-sig")
        logger.info(f"Saved to {path}")
        if self._trace and self._trace.enabled:
            self._trace.save()
        return path

    def print_stats(self):
        """Print final statistics."""
        if self._results is None:
            return
        total = len(self._results)
        has_match = (
            self._results["matched_product_name_en"].notna()
            & (self._results["matched_product_name_en"] != "")
        )
        matched = self._results[has_match]
        not_matched = self._results[~has_match]
        logger.info("=" * 50)
        logger.info("FINAL RESULTS")
        logger.info("=" * 50)
        logger.info(f"Total drugs: {total}")
        logger.info(
            f"Matched: {len(matched)} "
            f"({len(matched)/total*100:.1f}%)",
        )
        logger.info(
            f"Not matched: {len(not_matched)} "
            f"({len(not_matched)/total*100:.1f}%)",
        )
        if len(matched) > 0:
            self._log_score_dist(matched)
        logger.info("Verification breakdown:")
        logger.info(
            self._results["verified"]
            .value_counts(dropna=False).to_string(),
        )
        logger.info("Method breakdown:")
        logger.info(
            self._results["match_method"]
            .value_counts(dropna=False).to_string(),
        )

    def _log_score_dist(self, matched):
        scores = pd.to_numeric(matched["match_score"], errors="coerce")
        logger.info("Score distribution:")
        for label, lo, hi in [
            ("100", 100, 101), ("95-99", 95, 100),
            ("90-94", 90, 95), ("80-89", 80, 90),
            ("70-79", 70, 80),
        ]:
            count = ((scores >= lo) & (scores < hi)).sum()
            logger.info(f"  {label}: {count}")
        logger.info(f"  <70: {(scores < 70).sum()}")

    # --- full pipeline ---

    async def run_full(
        self, drugs_path: str | None = None,
        tawreed_path: str | None = None,
        output_path: str | None = None,
    ) -> pd.DataFrame:
        """Run the complete pipeline."""
        self.load_data(drugs_path, tawreed_path)
        self.run_matching()
        await self.run_ai_verification()
        await self.run_ai_search_unmatched()
        self.run_post_cleanup()
        self.save(output_path)
        self.print_stats()
        return self._results

    # --- guards ---

    def _require_data(self):
        if self._drugs_df is None or self._index is None:
            raise RuntimeError("Call load_data() first")

    def _require_results(self):
        if self._results is None:
            raise RuntimeError("Call run_matching() first")
