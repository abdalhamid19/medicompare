from __future__ import annotations

import unittest

import pandas as pd

from drug_matcher.config import MatchingConfig
from drug_matcher.indexer import DrugIndex


def make_index(threshold: int = 70) -> DrugIndex:
    tawreed = pd.DataFrame(
        [
            {"product_name_ar": "اوجمنتين", "product_name_en": "AUGMENTIN 625 MG 10 F.C. TAB.", "store_product_id": "T-1"},
            {"product_name_ar": "انديرال", "product_name_en": "INDERAL 10 MG 50 TABS", "store_product_id": "T-2"},
            {"product_name_ar": "فيجوتون", "product_name_en": "VIGOTON 30 TABS", "store_product_id": "T-3"},
            {"product_name_ar": "جينكونازول", "product_name_en": "GYNOCONAZOL 0.4% CREAM", "store_product_id": "T-4"},
        ]
    )
    return DrugIndex(tawreed, MatchingConfig(fuzzy_threshold=threshold, top_k_candidates=5))


class DrugIndexTests(unittest.TestCase):
    def test_best_match_handles_compact_dosage_and_quantity(self) -> None:
        index = make_index()

        record, score, method = index.best_match("+***IMP AUGMENTIN625MG 10TABS")

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record["store_product_id"], "T-1")
        self.assertGreaterEqual(score, 70)
        self.assertIn(method, {"brand_index", "token_set_ratio", "token_sort_ratio", "partial_token_sort_ratio"})

    def test_best_match_rejects_quantity_mismatch_even_when_brand_matches(self) -> None:
        index = make_index(threshold=65)

        record, score, method = index.best_match("VIGOTON PLUS 20 TABS")

        self.assertIsNone(record)
        self.assertEqual(score, 0.0)
        self.assertEqual(method, "no_match")

    def test_fuzzy_match_returns_ranked_candidates_above_threshold(self) -> None:
        index = make_index(threshold=65)

        matches = index.fuzzy_match("INDERAL 10MG 50TAB", top_k=3)

        self.assertTrue(matches)
        self.assertEqual(matches[0][0]["store_product_id"], "T-2")
        self.assertGreaterEqual(matches[0][1], 65)


if __name__ == "__main__":
    unittest.main()
