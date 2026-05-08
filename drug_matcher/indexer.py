"""Inverted index for fast brand-based lookup + fuzzy matching."""
import re
from collections import defaultdict

import pandas as pd
from rapidfuzz import fuzz, process

from .normalizer import normalize, parse_drug, DrugComponents, components_match
from .config import MatchingConfig


class DrugIndex:
    """Pre-built index over tawreed products for O(1) brand
    lookup + cached fuzzy search. Uses list-based storage."""

    __slots__ = (
        "_names_en", "_names_ar", "_ids",
        "_norms", "_parsed", "_brand_index", "_cfg",
    )

    def __init__(self, tawreed_df: pd.DataFrame, cfg: MatchingConfig | None = None):
        self._cfg = cfg or MatchingConfig()
        df = tawreed_df.rename(columns={
            tawreed_df.columns[0]: "product_name_ar",
            tawreed_df.columns[1]: "product_name_en",
            tawreed_df.columns[2]: "store_product_id",
        })
        self._names_en = df["product_name_en"].tolist()
        self._names_ar = df["product_name_ar"].tolist()
        self._ids = df["store_product_id"].astype(str).tolist()
        self._norms = [normalize(n) for n in self._names_en]
        self._parsed = [parse_drug(n) for n in self._names_en]
        self._brand_index: dict[str, list[int]] = defaultdict(list)
        self._build_brand_index()

    def _build_brand_index(self):
        for i, parsed in enumerate(self._parsed):
            brand = re.sub(r"[^A-Z0-9]", "", parsed.brand)
            for plen in range(3, min(len(brand) + 1, 8)):
                self._brand_index[brand[:plen]].append(i)

    # --- public read interface ---

    def get_record(self, idx: int) -> dict:
        """Return record dict for a given index."""
        return {
            "product_name_en": self._names_en[idx],
            "product_name_ar": self._names_ar[idx],
            "store_product_id": self._ids[idx],
        }

    def get_parsed(self, idx: int) -> DrugComponents:
        """Return parsed components for a given index."""
        return self._parsed[idx]

    def score_candidate(self, query_norm: str, idx: int, scorer=None) -> float:
        """Score a candidate by index using the given scorer."""
        scorer = scorer or fuzz.token_sort_ratio
        return scorer(query_norm, self._norms[idx])

    def get_candidates(
        self, parsed: DrugComponents, limit: int = 10,
    ) -> list[tuple[int, float]]:
        """Return (idx, score) pairs for brand + fuzzy candidates."""
        brand_hits = self._brand_lookup(parsed)
        fuzzy_hits = self._fuzzy_lookup(parsed.normalized, limit)
        return self._dedupe(brand_hits + fuzzy_hits)

    # --- internal lookups ---

    def _brand_lookup(self, parsed: DrugComponents) -> list[tuple[int, float]]:
        brand = re.sub(r"[^A-Z0-9]", "", parsed.brand)
        if len(brand) < 3:
            return []
        hits = []
        seen = set()
        for plen in range(min(len(brand), 7), 2, -1):
            for idx in self._brand_index.get(brand[:plen], []):
                if idx not in seen:
                    seen.add(idx)
                    is_ok, _ = components_match(
                        parsed, self._parsed[idx],
                        self._cfg.brand_prefix_min,
                    )
                    if is_ok:
                        score = fuzz.token_sort_ratio(
                            parsed.normalized, self._norms[idx],
                        )
                        hits.append((idx, score))
        return hits

    def _fuzzy_lookup(self, query: str, limit: int) -> list[tuple[int, float]]:
        results = process.extract(
            query, self._norms,
            scorer=fuzz.token_set_ratio, limit=limit,
        )
        return [
            (idx, score) for _, score, idx in results
            if score >= self._cfg.fuzzy_threshold
        ]

    def _dedupe(self, hits: list[tuple[int, float]]) -> list[tuple[int, float]]:
        seen = set()
        out = []
        for idx, score in hits:
            if idx not in seen:
                seen.add(idx)
                out.append((idx, score))
        return out

    # --- top-level match ---

    def lookup_by_brand(self, drug_components: DrugComponents):
        """Brand lookup returning (record_dict, index) pairs."""
        return [(self.get_record(i), i) for i, _ in self._brand_lookup(drug_components)]

    def fuzzy_match(self, query: str, top_k: int | None = None):
        """Fuzzy match returning (record_dict, score, index)."""
        top_k = top_k or self._cfg.top_k_candidates
        out = []
        for idx, score in self._fuzzy_lookup(query, top_k):
            out.append((self.get_record(idx), score, idx))
        return out

    def best_match(self, drug_name: str) -> tuple[dict | None, float, str]:
        """Find best verified match. Returns (record, score, method)."""
        parsed = parse_drug(drug_name)
        norm = parsed.normalized
        if not norm or len(norm) < 3:
            return None, 0.0, "too_short"
        rec, score = self._try_brand_match(parsed, norm)
        if rec is not None:
            return rec, score, "brand_index"
        rec, score, method = self._try_fuzzy_match(parsed, norm)
        if rec is not None:
            return rec, score, method
        return None, 0.0, "no_match"

    def best_match_detailed(
        self, drug_name: str,
    ) -> tuple[dict | None, float, str, dict]:
        """Like best_match but also returns trace dict for logging."""
        parsed = parse_drug(drug_name)
        norm = parsed.normalized
        trace = {
            "norm": norm, "brand": parsed.brand,
            "brand_hits": [], "fuzzy_steps": [],
            "component_checks": [],
        }
        if not norm or len(norm) < 3:
            return None, 0.0, "too_short", trace
        hits = self._brand_lookup(parsed)
        trace["brand_hits"] = hits
        if hits:
            best_idx, best_score = max(hits, key=lambda x: x[1])
            if best_score >= self._cfg.fuzzy_threshold:
                ok, reason = components_match(
                    parsed, self._parsed[best_idx],
                    self._cfg.brand_prefix_min,
                )
                trace["component_checks"].append(
                    (best_idx, ok, reason),
                )
                if ok:
                    return (
                        self.get_record(best_idx),
                        best_score, "brand_index", trace,
                    )
        for scorer in [fuzz.token_set_ratio, fuzz.token_sort_ratio, fuzz.partial_token_sort_ratio]:
            result = process.extractOne(
                norm, self._norms, scorer=scorer,
                score_cutoff=self._cfg.fuzzy_threshold,
            )
            trace["fuzzy_steps"].append(
                (scorer.__name__, result),
            )
            if result:
                _, score, idx = result
                ok, reason = components_match(
                    parsed, self._parsed[idx],
                    self._cfg.brand_prefix_min,
                )
                trace["component_checks"].append(
                    (idx, ok, reason),
                )
                if ok:
                    return (
                        self.get_record(idx), score,
                        scorer.__name__, trace,
                    )
        return None, 0.0, "no_match", trace

    def _try_brand_match(self, parsed, norm):
        hits = self._brand_lookup(parsed)
        if not hits:
            return None, 0.0
        best_idx, best_score = max(hits, key=lambda x: x[1])
        if best_score >= self._cfg.fuzzy_threshold:
            return self.get_record(best_idx), best_score
        return None, 0.0

    def _try_fuzzy_match(self, parsed, norm):
        best = None
        for scorer in [fuzz.token_set_ratio, fuzz.token_sort_ratio, fuzz.partial_token_sort_ratio]:
            result = process.extractOne(
                norm, self._norms, scorer=scorer,
                score_cutoff=self._cfg.fuzzy_threshold,
            )
            if result:
                _, score, idx = result
                is_ok, _ = components_match(
                    parsed, self._parsed[idx],
                    self._cfg.brand_prefix_min,
                )
                if is_ok and (best is None or score > best[1]):
                    best = (self.get_record(idx), score, scorer.__name__)
        return best or (None, 0.0, "")

    @property
    def size(self) -> int:
        return len(self._names_en)

    @property
    def norms(self) -> list[str]:
        """Public read-only access to normalized names list."""
        return self._norms
