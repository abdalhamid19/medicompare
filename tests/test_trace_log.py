from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from drug_matcher.config import MatchingConfig
from drug_matcher.normalizer import parse_drug
from drug_matcher.pipeline import MatchPipeline
from drug_matcher.trace_log import MatchTraceLog


class TraceLogTests(unittest.TestCase):
    def test_trace_csv_includes_diagnostic_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trace = MatchTraceLog(log_dir=tmpdir)
            comp = parse_drug("AMIKACIN 500MG VIAL")

            trace.log_normalization(
                "D-1", "AMIKACIN 500MG VIAL",
                comp.normalized, comp.brand,
                comp.dosage_nums, comp.form,
                row_index=3,
                components=trace.components_text(comp),
            )
            csv_path, _, summary_path = trace.save()

            with open(csv_path, encoding="utf-8-sig", newline="") as f:
                row = next(csv.DictReader(f))

            self.assertEqual(row["row_index"], "3")
            self.assertEqual(row["phase"], "normalize")
            self.assertIn("form=VIAL", row["inventory_components"])
            self.assertIn("run_id", row)
            self.assertTrue(Path(summary_path).exists())

    def test_rejected_candidate_records_reject_rule(self) -> None:
        trace = MatchTraceLog(enabled=True)
        comp = parse_drug("AMIKACIN 500MG VIAL")
        cand = parse_drug("AMIKACIN SPRAY 100 ML")

        trace._append(
            "D-1", "AMIKACIN 500MG VIAL",
            comp.normalized, comp.brand,
            step="component_check",
            phase="component_check",
            decision="rejected",
            reject_rule="form_mismatch",
            candidate_components=trace.components_text(cand),
        )

        row = trace._rows[0]
        self.assertEqual(row["reject_rule"], "form_mismatch")
        self.assertEqual(row["decision"], "rejected")

    def test_api_and_parse_failure_events_are_traceable(self) -> None:
        trace = MatchTraceLog(enabled=True)
        comp = parse_drug("PANADOL 20 TAB")

        trace.log_api_attempts(
            "D-1", "PANADOL 20 TAB", comp.normalized, comp.brand,
            [{
                "attempt": 1,
                "model": "minimax",
                "status": 401,
                "fallback_used": False,
                "decision": "failed",
                "error_stage": "api",
                "error_code": "http_401",
                "key_suffix": "abc123",
                "reason": "unauthorized",
            }],
        )
        trace.log_ai_parse_failure(
            "D-1", "PANADOL 20 TAB", comp.normalized, comp.brand,
            "not json", model_used="fallback",
        )

        api_row, parse_row = trace._rows
        self.assertEqual(api_row["step"], "api_attempt")
        self.assertEqual(api_row["api_status"], 401)
        self.assertIn("key=...abc123", api_row["selection_reason"])
        self.assertEqual(parse_row["parse_failed"], "true")
        self.assertEqual(parse_row["error_code"], "invalid_json")

    def test_summary_contains_one_row_per_drug(self) -> None:
        trace = MatchTraceLog(enabled=True)
        comp = parse_drug("UNKNOWN PRODUCT")
        trace.log_ai_preflight_start(["model-a"], 2)
        trace.log_final(
            "D-1", "UNKNOWN PRODUCT", comp.normalized, comp.brand,
            None, 0.0, "no_match", "search",
            "no_match -> eligible for AI search",
        )

        rows = trace._summary_rows()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["code"], "D-1")
        self.assertEqual(rows[0]["final_status"], "no_match")
        self.assertEqual(rows[0]["failure_stage"], "matching")

    def test_preflight_events_are_traceable(self) -> None:
        trace = MatchTraceLog(enabled=True)

        trace.log_ai_preflight_start(["bad", "good"], 2)
        trace.log_ai_preflight_result(
            [
                {"ok": False, "error_type": "http_401"},
                {"ok": True, "error_type": ""},
            ],
            healthy_count=1,
        )

        self.assertEqual(trace._rows[0]["step"], "ai_preflight_start")
        self.assertEqual(trace._rows[0]["phase"], "ai_preflight")
        self.assertIn("2 key", trace._rows[0]["selection_reason"])
        self.assertEqual(trace._rows[1]["decision"], "healthy")
        self.assertIn("healthy_combos=1", trace._rows[1]["selection_reason"])

    def test_rotation_events_are_traceable(self) -> None:
        trace = MatchTraceLog(enabled=True)
        trace.log_rotation_preflight_start(3)
        trace.log_rotation_ranked_attempt({
            "ok": True,
            "provider": "groq",
            "model": "openai/gpt-oss-120b",
            "key_suffix": "abc123",
            "rotation_rank": 1,
            "rotation_score": 150.0,
            "http_status": 200,
        })

        self.assertEqual(trace._rows[0]["step"], "rotation_preflight_start")
        self.assertEqual(trace._rows[1]["provider_used"], "groq")
        self.assertEqual(trace._rows[1]["model_used"], "openai/gpt-oss-120b")

    def test_rotation_api_attempt_adds_usage_event(self) -> None:
        trace = MatchTraceLog(enabled=True)
        comp = parse_drug("PANADOL 20 TAB")

        trace.log_api_attempts(
            "D-1", "PANADOL 20 TAB", comp.normalized, comp.brand,
            [{
                "attempt": 1,
                "provider": "groq",
                "model": "openai/gpt-oss-120b",
                "status": 200,
                "fallback_used": False,
                "decision": "success",
                "key_suffix": "abc123",
                "reason": "parsed_json",
            }],
        )

        self.assertEqual(trace._rows[0]["step"], "api_attempt")
        self.assertEqual(trace._rows[1]["step"], "rotation_attempt_used")
        self.assertEqual(trace._rows[1]["provider_used"], "groq")

    def test_ai_search_rejection_reason_uses_actual_threshold_direction(self) -> None:
        trace = MatchTraceLog(enabled=True)
        comp = parse_drug("ADMLASE SYRUP 120 ML")

        trace.log_ai_search_result(
            "D-1", "ADMLASE SYRUP 120 ML", comp.normalized, comp.brand,
            False, None, 0.6,
            model_used="model-a",
            accept_threshold=0.75,
            error_code="best_index_0",
        )

        self.assertIn("confidence=0.6 < 0.75 -> rejected", trace._rows[0]["selection_reason"])

    def test_summary_treats_reviewed_ai_found_as_matched(self) -> None:
        trace = MatchTraceLog(enabled=True)
        comp = parse_drug("AMRIZOLE N SUPP")
        trace.log_final(
            "D-1", "AMRIZOLE N SUPP", comp.normalized, comp.brand,
            None, 0.0, "no_match", "search",
            "no_match -> eligible for AI search",
        )
        trace.log_ai_search_result(
            "D-1", "AMRIZOLE N SUPP", comp.normalized, comp.brand,
            True, "AMRIZOLE N 5 VAG. SUPP.", 0.98,
            accept_threshold=0.75,
        )
        trace.log_ai_review_result(
            "D-1", "AMRIZOLE N SUPP", comp.normalized, comp.brand,
            True, 0.98, "same product", "ai_found_reviewed",
        )

        row = trace._summary_rows()[0]

        self.assertEqual(row["final_status"], "matched")
        self.assertEqual(row["final_match"], "AMRIZOLE N 5 VAG. SUPP.")

    def test_post_cleanup_rejection_is_logged(self) -> None:
        pipeline = MatchPipeline(cfg=MatchingConfig(), api_cfg=None)
        pipeline._trace = MatchTraceLog(enabled=True)
        pipeline._results = pd.DataFrame([{
            "code": "D-1",
            "drug_name": "GYNOCONAZOLE 0.8% CREAM",
            "matched_product_name_en": "GYNOCONAZOL 0.4% CREAM",
            "matched_product_name_ar": "جينكونازول",
            "matched_store_product_id": "T-4",
            "match_score": 88.0,
            "verified": "ai_confirmed",
            "match_method": "ai_verified",
            "ai_confidence": "",
            "ai_review_confidence": "",
        }])

        pipeline.run_post_cleanup()

        cleanup_rows = [
            r for r in pipeline._trace._rows
            if r["step"] == "post_cleanup"
        ]
        self.assertEqual(len(cleanup_rows), 1)
        self.assertEqual(cleanup_rows[0]["decision"], "cleanup_rejected")
        self.assertEqual(cleanup_rows[0]["error_stage"], "post_cleanup")


if __name__ == "__main__":
    unittest.main()
