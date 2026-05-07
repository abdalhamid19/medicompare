"""Inverted index for fast brand-based lookup + fuzzy matching cache."""
import re
from collections import defaultdict
from typing import Any

import pandas as pd
from rapidfuzz import fuzz, process

from .normalizer import normalize, parse_drug, DrugComponents, components_match
from .config import MatchingConfig


class DrugIndex:
    """Pre-built index over tawreed products for O(1) brand lookup + cached fuzzy search."""

    __slots__ = ("_df", "_norms", "_records", "_brand_index", "_cfg", "_parsed_cache")

    def __init__(self, tawreed_df: pd.DataFrame, cfg: MatchingConfig | None = None):
        self._cfg = cfg or MatchingConfig()
        self._df = tawreed_df.rename(columns={
            tawreed_df.columns[0]: "product_name_ar",
            tawreed_df.columns[1]: "product_name_en",
            tawreed_df.columns[2]: "store_product_id",
        })

        # Pre-compute normalized names (vectorized)
        self._df["norm_en"] = self._df["product_name_en"].apply(normalize)
        self._norms = self._df["norm_en"].tolist()
        self._records = self._df.to_dict("records")

        # Build inverted index: brand_prefix -> [record_indices]
        self._brand_index: dict[str, list[int]] = defaultdict(list)
        self._parsed_cache: dict[int, DrugComponents] = {}

        for i, row in enumerate(self._records):
            parsed = parse_drug(row["product_name_en"])
            self._parsed_cache[i] = parsed
            brand = re.sub(r"[^A-Z0-9]", "", parsed.brand)
            for prefix_len in range(3, min(len(brand) + 1, 8)):
                self._brand_index[brand[:prefix_len]].append(i)

    def lookup_by_brand(self, drug_components: DrugComponents) -> list[tuple[dict, int]]:
        """Fast brand-based lookup returning (record, index) pairs."""
        brand = re.sub(r"[^A-Z0-9]", "", drug_components.brand)
        if len(brand) < 3:
            return []

        candidates = []
        seen = set()
        for prefix_len in range(min(len(brand), 7), 2, -1):
            prefix = brand[:prefix_len]
            for idx in self._brand_index.get(prefix, []):
                if idx not in seen:
                    seen.add(idx)
                    is_ok, _ = components_match(drug_components, self._parsed_cache[idx], self._cfg.brand_prefix_min)
                    if is_ok:
                        candidates.append((self._records[idx], idx))
        return candidates

    def fuzzy_match(self, query: str, top_k: int | None = None) -> list[tuple[dict, float, int]]:
        """Fuzzy match returning (record, score, index) sorted by score desc."""
        top_k = top_k or self._cfg.top_k_candidates
        results = process.extract(query, self._norms, scorer=fuzz.token_set_ratio, limit=top_k)
        out = []
        for match_name, score, idx in results:
            if score >= self._cfg.fuzzy_threshold:
                out.append((self._records[idx], score, idx))
        return out

    def best_match(self, drug_name: str) -> tuple[dict | None, float, str]:
        """Find best verified match for a drug name. Returns (record, score, method)."""
        parsed = parse_drug(drug_name)
        norm = parsed.normalized

        if not norm or len(norm) < 3:
            return None, 0.0, "too_short"

        # Strategy 1: Brand index lookup (fastest, O(1))
        brand_hits = self.lookup_by_brand(parsed)
        if brand_hits:
            best_rec, best_idx = max(brand_hits, key=lambda x: fuzz.token_sort_ratio(norm, self._norms[x[1]]))
            score = fuzz.token_sort_ratio(norm, self._norms[best_idx])
            # Reject brand_index matches with very low fuzzy score (different products)
            if score >= self._cfg.fuzzy_threshold:
                return best_rec, score, "brand_index"

        # Strategy 2: Fuzzy matching with multiple scorers
        best = None
        for scorer in [fuzz.token_set_ratio, fuzz.token_sort_ratio, fuzz.partial_token_sort_ratio]:
            result = process.extractOne(norm, self._norms, scorer=scorer, score_cutoff=self._cfg.fuzzy_threshold)
            if result:
                match_name, score, idx = result
                is_ok, _ = components_match(parsed, self._parsed_cache[idx], self._cfg.brand_prefix_min)
                if is_ok:
                    if best is None or score > best[1]:
                        best = (self._records[idx], score, scorer.__name__)

        if best:
            return best[0], best[1], best[2]

        return None, 0.0, "no_match"

    @property
    def size(self) -> int:
        return len(self._records)
