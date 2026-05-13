from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from drug_matcher.config import MatchingConfig
from drug_matcher.pipeline import MatchPipeline


class PipelineTests(unittest.TestCase):
    def test_pipeline_loads_matches_and_saves_without_ai(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            drugs_path = tmp_path / "drugs.csv"
            tawreed_path = tmp_path / "tawreed.csv"
            output_path = tmp_path / "matched.csv"

            pd.DataFrame(
                [
                    {"كود": "D-1", "إسم الصنف": "+*** AUGMENTIN625MG 10TABS"},
                    {"كود": "D-2", "إسم الصنف": "UNKNOWN PRODUCT 20 TAB"},
                ]
            ).to_csv(drugs_path, index=False, encoding="utf-8-sig")

            pd.DataFrame(
                [
                    {"product_name_ar": "اوجمنتين", "product_name_en": "AUGMENTIN 625 MG 10 F.C. TAB.", "store_product_id": "T-1"},
                    {"product_name_ar": "انديرال", "product_name_en": "INDERAL 10 MG 50 TABS", "store_product_id": "T-2"},
                ]
            ).to_csv(tawreed_path, index=False, encoding="utf-8-sig")

            pipeline = MatchPipeline(cfg=MatchingConfig(fuzzy_threshold=70), api_cfg=None)
            pipeline.load_data(str(drugs_path), str(tawreed_path))
            results = pipeline.run_matching()

            first = results.loc[results["code"] == "D-1"].iloc[0]
            second = results.loc[results["code"] == "D-2"].iloc[0]

            self.assertEqual(first["matched_store_product_id"], "T-1")
            self.assertEqual(first["verified"], "algo_match")
            self.assertEqual(second["matched_product_name_en"], "")
            self.assertEqual(second["match_method"], "no_match")

            saved = pipeline.save(str(output_path))
            self.assertEqual(saved, str(output_path))
            self.assertTrue(output_path.exists())
            saved_df = pd.read_csv(saved, dtype=str)
            self.assertNotIn("_drug_price", saved_df.columns)
            self.assertNotIn("_matched_price", saved_df.columns)

            review_path = tmp_path / "review.csv"
            review_saved = pipeline.save_manual_review(str(review_path))
            review = pd.read_csv(review_saved, dtype=str)
            self.assertEqual(review_saved, str(review_path))
            self.assertIn("manual_decision", review.columns)
            self.assertIn("manual_reason", review.columns)
            self.assertIn("correct_store_product_id", review.columns)
            self.assertNotIn("_drug_price", review.columns)
            self.assertNotIn("_matched_price", review.columns)
            self.assertTrue((review["code"] == "D-2").any())

    def test_pipeline_has_no_post_cleanup_phase(self) -> None:
        pipeline = MatchPipeline(cfg=MatchingConfig(), api_cfg=None)

        self.assertFalse(hasattr(pipeline, "run_post_cleanup"))

    def test_pipeline_passes_price_signal_to_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            drugs_path = tmp_path / "drugs.csv"
            tawreed_path = tmp_path / "tawreed.csv"

            pd.DataFrame(
                [
                    {
                        "كود": "D-1",
                        "إسم الصنف": "PRICECID 10MG 30TAB",
                        "سعر البيع": "40",
                    },
                ]
            ).to_csv(drugs_path, index=False, encoding="utf-8-sig")

            pd.DataFrame(
                [
                    {
                        "product_name_ar": "مرشح ارخص",
                        "product_name_en": "PRICECID 10 MG 30 TAB SMALL PACK",
                        "store_product_id": "wrong-price",
                        "product_id": "P-1",
                        "sale_price": "30",
                    },
                    {
                        "product_name_ar": "مرشح السعر",
                        "product_name_en": "PRICECID 10 MG 30 TAB LARGE PACK",
                        "store_product_id": "right-price",
                        "product_id": "P-2",
                        "sale_price": "40",
                    },
                ]
            ).to_csv(tawreed_path, index=False, encoding="utf-8-sig")

            pipeline = MatchPipeline(cfg=MatchingConfig(fuzzy_threshold=65), api_cfg=None)
            pipeline.load_data(str(drugs_path), str(tawreed_path))
            results = pipeline.run_matching()

            row = results.iloc[0]
            self.assertEqual(row["matched_store_product_id"], "right-price")

    def test_start_and_limit_select_following_batch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            drugs_path = tmp_path / "drugs.csv"
            tawreed_path = tmp_path / "tawreed.csv"

            pd.DataFrame(
                [
                    {"كود": "D-1", "إسم الصنف": "FIRST 10 MG 10 TAB"},
                    {"كود": "D-2", "إسم الصنف": "SECOND 10 MG 10 TAB"},
                    {"كود": "D-3", "إسم الصنف": "THIRD 10 MG 10 TAB"},
                    {"كود": "D-4", "إسم الصنف": "FOURTH 10 MG 10 TAB"},
                ]
            ).to_csv(drugs_path, index=False, encoding="utf-8-sig")
            pd.DataFrame(
                [
                    {
                        "product_name_ar": "ثاني",
                        "product_name_en": "SECOND 10 MG 10 TAB",
                        "store_product_id": "T-2",
                    },
                ]
            ).to_csv(tawreed_path, index=False, encoding="utf-8-sig")

            pipeline = MatchPipeline(
                cfg=MatchingConfig(), api_cfg=None, start=1, limit=2,
            )
            pipeline.load_data(str(drugs_path), str(tawreed_path))
            results = pipeline.run_matching()

            self.assertEqual(results["code"].tolist(), ["D-2", "D-3"])


if __name__ == "__main__":
    unittest.main()
