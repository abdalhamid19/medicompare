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


def make_reported_errors_index(threshold: int = 70) -> DrugIndex:
    tawreed = pd.DataFrame(
        [
            {
                "product_name_ar": "اكانزا بخاخ",
                "product_name_en": "AKANZA LIQUID SPRAY 15 ML",
                "store_product_id": "1688183",
            },
            {
                "product_name_ar": "ايه اي جي",
                "product_name_en": "AIG ESOMEPRAZOLE 40 MG 28 CAPSULES 2 STRIPS",
                "store_product_id": "2435517",
            },
            {
                "product_name_ar": "اكرين",
                "product_name_en": "INFINITY AKREN FACIAL CLEANSER 250 ML",
                "store_product_id": "901898",
            },
            {
                "product_name_ar": "البوستكس دي",
                "product_name_en": "ALBUSTIX D 16 / 12.5 MG 30 TAB.",
                "store_product_id": "2510356",
            },
            {
                "product_name_ar": "اليكسولايت موز",
                "product_name_en": "ALEXOLYTE (ORS) SYRUP 360 ML BANANA",
                "store_product_id": "1032871",
            },
            {
                "product_name_ar": "اليكسولايت برتقال",
                "product_name_en": "ALEXOLYTE (ORS) SYRUP 360 ML ORANGE",
                "store_product_id": "2468401",
            },
            {
                "product_name_ar": "اليكسولايت اناناس",
                "product_name_en": "ALEXOLYTE (ORS) SYRUP 360 ML PINEAPPLE",
                "store_product_id": "1533835",
            },
            {
                "product_name_ar": "اليكسولايت فراوله",
                "product_name_en": "ALEXOLYTE (ORS) SYRUP 360 ML STRAWBERRY",
                "store_product_id": "2468398",
            },
            {
                "product_name_ar": "الجيزال",
                "product_name_en": "ALGESAL SURACTIVE 40 GM CREAM",
                "store_product_id": "987471",
            },
        ]
    )
    cfg = MatchingConfig(fuzzy_threshold=threshold, top_k_candidates=10)
    return DrugIndex(tawreed, cfg)


class DrugIndexTests(unittest.TestCase):
    def test_best_match_handles_compact_dosage_and_quantity(self) -> None:
        index = make_index()

        record, score, method = index.best_match("+*** AUGMENTIN625MG 10TABS")

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record["store_product_id"], "T-1")
        self.assertGreaterEqual(score, 70)
        self.assertIn(method, {"brand_index", "token_set_ratio", "token_sort_ratio", "partial_token_sort_ratio"})

    def test_best_match_rejects_import_status_mismatch(self) -> None:
        index = make_index(threshold=65)

        record, score, method = index.best_match("+***IMP AUGMENTIN625MG 10TABS")

        self.assertIsNone(record)
        self.assertEqual(score, 0.0)
        self.assertEqual(method, "no_match")

    def test_best_match_rejects_quantity_mismatch_even_when_brand_matches(self) -> None:
        index = make_index(threshold=65)

        record, score, method = index.best_match("VIGOTON PLUS 20 TABS")

        self.assertIsNone(record)
        self.assertEqual(score, 0.0)
        self.assertEqual(method, "no_match")

    def test_best_match_marks_numeric_noise_invalid(self) -> None:
        index = make_index(threshold=65)

        record, score, method = index.best_match("45645841635")

        self.assertIsNone(record)
        self.assertEqual(score, 0.0)
        self.assertEqual(method, "invalid_name")

    def test_best_match_rejects_missing_b12_variant(self) -> None:
        tawreed = pd.DataFrame(
            [
                {
                    "product_name_ar": "فيروجلوبين",
                    "product_name_en": "FEROGLOBIN 30 CAPS",
                    "store_product_id": "T-1",
                },
            ]
        )
        index = DrugIndex(tawreed, MatchingConfig(fuzzy_threshold=65))

        record, score, method = index.best_match("FEROGLOBIN B12 30 CAP")

        self.assertIsNone(record)
        self.assertEqual(score, 0.0)
        self.assertEqual(method, "no_match")

    def test_fuzzy_match_returns_ranked_candidates_above_threshold(self) -> None:
        index = make_index(threshold=65)

        matches = index.fuzzy_match("INDERAL 10MG 50TAB", top_k=3)

        self.assertTrue(matches)
        self.assertEqual(matches[0][0]["store_product_id"], "T-2")
        self.assertGreaterEqual(matches[0][1], 65)

    def test_reported_false_negatives_are_matched(self) -> None:
        index = make_reported_errors_index(threshold=65)
        cases = [
            ("AKANZA SPRAY 15 ML", "1688183"),
            ("aig esomeprprazole 40ml 28capsules", "2435517"),
            ("AKREN CLEANSER FACIAL WASH 250 ML", "901898"),
            ("ALEXOLYTE 360ML BANANA FLAVOR", "1032871"),
            ("ALEXOLYTE 360ML ORANGE FLAVOR SYRUP", "2468401"),
            ("ALEXOLYTE 360ML PINEAPPLE FLAVOR", "1533835"),
            ("ALEXOLYTE 360ML STRAWBERRY FLAVOR", "2468398"),
            ("ALGESAL CREAM 40 GM", "987471"),
        ]
        for query, expected_id in cases:
            with self.subTest(query=query):
                record, score, method = index.best_match(query)
                self.assertIsNotNone(record)
                assert record is not None
                self.assertEqual(record["store_product_id"], expected_id)
                self.assertGreaterEqual(score, 65)
                self.assertNotEqual(method, "no_match")

    def test_reported_modifier_mismatch_stays_rejected(self) -> None:
        index = make_reported_errors_index(threshold=65)

        record, score, method = index.best_match("ALBUSTIX 16\\12.5 MG 30 TAB")

        self.assertIsNone(record)
        self.assertEqual(score, 0.0)
        self.assertEqual(method, "no_match")


if __name__ == "__main__":
    unittest.main()
