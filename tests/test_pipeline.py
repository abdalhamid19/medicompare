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
                    {"كود": "D-1", "إسم الصنف": "+***IMP AUGMENTIN625MG 10TABS"},
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

    def test_post_cleanup_removes_component_mismatches(self) -> None:
        pipeline = MatchPipeline(cfg=MatchingConfig(), api_cfg=None)
        pipeline._results = pd.DataFrame(
            [
                {
                    "code": "D-1",
                    "drug_name": "GYNOCONAZOLE 0.8% CREAM",
                    "matched_product_name_en": "GYNOCONAZOL 0.4% CREAM",
                    "matched_product_name_ar": "جينكونازول",
                    "matched_store_product_id": "T-4",
                    "match_score": 88.0,
                    "verified": "ai_confirmed",
                    "match_method": "ai_verified",
                }
            ]
        )

        cleaned = pipeline.run_post_cleanup()

        self.assertEqual(cleaned.at[0, "matched_product_name_en"], "")
        self.assertEqual(cleaned.at[0, "matched_store_product_id"], "")
        self.assertEqual(cleaned.at[0, "verified"], "cleanup_rejected")
        self.assertEqual(cleaned.at[0, "match_method"], "post_cleanup")


if __name__ == "__main__":
    unittest.main()
