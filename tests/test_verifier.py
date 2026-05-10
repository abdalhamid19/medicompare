from __future__ import annotations

import asyncio
import unittest
from unittest.mock import patch

from drug_matcher.config import APIConfig
from drug_matcher.prompts import (
    FRESH_REVIEW_PROMPT,
    REVIEW_PROMPT,
    SEARCH_PROMPT,
    VERIFY_PROMPT,
    render_prompt,
)
from drug_matcher.verifier import (
    AIVerifier,
    SYSTEM_PROMPT,
    _fallback_from_unparseable_response,
)


class AIVerifierTests(unittest.TestCase):
    def test_verify_one_without_api_key_is_safe_offline(self) -> None:
        verifier = AIVerifier(APIConfig(api_key=""))

        result = asyncio.run(verifier.verify_one("PANADOL 20 TAB", "PANADOL 20 TABLETS"))

        self.assertEqual(result, {"is_correct": True, "reason": "no_api_key", "confidence": 0.5})

    def test_verify_batch_preserves_row_indexes_without_api_key(self) -> None:
        verifier = AIVerifier(APIConfig(api_key=""))

        results = asyncio.run(verifier.verify_batch([("A", "B", 10), ("C", "D", 20)]))

        self.assertEqual([item["row_idx"] for item in results], [10, 20])
        self.assertTrue(all(item["reason"] == "no_api_key" for item in results))

    def test_find_better_match_without_api_key_returns_none(self) -> None:
        verifier = AIVerifier(APIConfig(api_key=""))

        result = asyncio.run(verifier.find_better_match("PANADOL", [({"product_name_en": "PANADOL"}, 100.0, 0)]))

        self.assertIsNone(result)

    def test_prompt_contains_negative_matching_rules(self) -> None:
        prompt = SYSTEM_PROMPT.upper()
        self.assertIn("PLUS", prompt)
        self.assertIn("DOSAGE", prompt)
        self.assertIn("QUANTITY", prompt)
        self.assertIn("B12", prompt)
        self.assertIn("FLAVOR", prompt)
        self.assertIn("IMPORTED", prompt)
        self.assertIn("ROUTE", prompt)
        self.assertIn("VIAL", prompt)
        self.assertIn("SPRAY", prompt)
        self.assertIn("PRICE", prompt)

    def test_task_prompts_are_loaded_and_renderable(self) -> None:
        rendered = render_prompt(
            VERIFY_PROMPT,
            drug_a="A",
            drug_b="B",
            drug_b_ar_line="",
        )

        self.assertIn("DRUG A", rendered)
        self.assertIn("is_correct", VERIFY_PROMPT)
        self.assertIn("best_index", SEARCH_PROMPT)
        self.assertIn("agree", REVIEW_PROMPT)
        self.assertIn("is_correct", FRESH_REVIEW_PROMPT)

    def test_verify_prompt_includes_component_context(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key"))
        captured = {}

        async def fake_call(self, payload):
            captured["payload"] = payload
            return {"is_correct": True, "reason": "ok", "confidence": 0.9}

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            asyncio.run(
                verifier.verify_one(
                    "PANADOL 20 TAB",
                    "PANADOL 20 TABLETS",
                    algo_score=88,
                    algo_method="brand_index",
                    inventory_price="34",
                    candidate_price="34",
                )
            )

        user_prompt = captured["payload"]["messages"][1]["content"]
        self.assertIn("DRUG A parsed context", user_prompt)
        self.assertIn("normalized='PANADOL 20 TAB'", user_prompt)
        self.assertIn("score=88", user_prompt)
        self.assertIn("method=brand_index", user_prompt)
        self.assertIn("Price context", user_prompt)
        self.assertIn("inventory=34", user_prompt)
        self.assertIn("candidate=34", user_prompt)
        self.assertIn("delta=0.0%", user_prompt)

    def test_search_prompt_includes_candidate_context(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key"))
        captured = {}

        async def fake_call(self, payload):
            captured["payload"] = payload
            return {
                "_raw": {"best_index": 1},
                "reason": "ok",
                "confidence": 0.9,
            }

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            result = asyncio.run(
                verifier.find_better_match(
                    "PANADOL 20 TAB",
                    [
                        ({
                            "product_name_en": "PANADOL 20 TABLETS",
                            "price": 34,
                        }, 90.0, 0),
                    ],
                    inventory_price="34",
                )
            )

        user_prompt = captured["payload"]["messages"][1]["content"]
        self.assertIsNotNone(result)
        self.assertIn("Inventory parsed context", user_prompt)
        self.assertIn("Inventory price: 34", user_prompt)
        self.assertIn("candidate_price=34", user_prompt)
        self.assertIn("price_delta=0.0%", user_prompt)
        self.assertIn("parsed:", user_prompt)
        self.assertIn("PANADOL 20 TABLETS", user_prompt)

    def test_review_prompts_include_price_context(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key", review_model="review"))
        captured = {}

        async def fake_call(self, payload):
            captured["payload"] = payload
            return {"agree": True, "reason": "ok", "confidence": 0.9}

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            asyncio.run(
                verifier.review_one(
                    "PANADOL 20 TAB",
                    "PANADOL 20 TABLETS",
                    "ai_confirmed",
                    0.8,
                    "first ok",
                    inventory_price="34",
                    candidate_price="35",
                )
            )

        user_prompt = captured["payload"]["messages"][1]["content"]
        self.assertIn("Price context", user_prompt)
        self.assertIn("inventory=34", user_prompt)
        self.assertIn("candidate=35", user_prompt)

    def test_invalid_json_fallback_is_low_confidence_and_traceable(self) -> None:
        result = _fallback_from_unparseable_response(
            "This is a correct match but not JSON",
            "test-model",
        )

        self.assertTrue(result["is_correct"])
        self.assertLess(result["confidence"], 0.7)
        self.assertTrue(result["parse_failed"])
        self.assertIn("invalid_json", result["reason"])
        self.assertEqual(result["model_used"], "test-model")

    def test_review_invalid_json_does_not_override_first_ai(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key", review_model="review"))

        async def fake_call(self, payload):
            return {
                "is_correct": False,
                "agree": False,
                "reason": "invalid_json:bad response",
                "confidence": 0.55,
                "parse_failed": True,
            }

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            result = asyncio.run(
                verifier.review_one(
                    "PANADOL 20 TAB",
                    "PANADOL 20 TABLETS",
                    "ai_rejected",
                    0.6,
                    "first rejected",
                )
            )

        self.assertTrue(result["is_correct"])
        self.assertLessEqual(result["confidence"], 0.5)
        self.assertTrue(result["parse_failed"])

    def test_fresh_review_invalid_json_rejects_conservatively(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key", review_model="review"))

        async def fake_call(self, payload):
            return {
                "is_correct": True,
                "reason": "invalid_json:bad response",
                "confidence": 0.55,
                "parse_failed": True,
            }

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            result = asyncio.run(
                verifier.review_one(
                    "PANADOL 20 TAB",
                    "PANADOL 20 TABLETS",
                    "ai_confirmed",
                    0.0,
                    "api failed",
                    api_failed=True,
                )
            )

        self.assertFalse(result["is_correct"])
        self.assertLessEqual(result["confidence"], 0.5)
        self.assertTrue(result["parse_failed"])

    def test_attempt_plan_uses_only_healthy_combos_when_present(self) -> None:
        cfg = APIConfig(
            api_key="sk-primary-111111",
            api_keys=("sk-primary-111111", "sk-secondary-222222"),
            model="bad-model",
            fallback_models=("good-model", "other-model"),
            healthy_combos=(("222222", "good-model"),),
        )
        verifier = AIVerifier(cfg)

        plan = verifier._build_attempt_plan("bad-model")

        self.assertEqual(plan, [("sk-secondary-222222", "good-model")])

    def test_attempt_plan_skips_failed_healthy_combo(self) -> None:
        cfg = APIConfig(
            api_key="sk-primary-111111",
            api_keys=("sk-primary-111111",),
            model="good-model",
            healthy_combos=(("111111", "good-model"),),
        )
        verifier = AIVerifier(cfg)
        verifier._failed_combos.add(("111111", "good-model"))

        plan = verifier._build_attempt_plan("good-model")

        self.assertEqual(plan, [])

    def test_auth_failure_disables_combo_immediately(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="sk-primary-111111"))

        disabled = verifier._record_combo_failure(
            "sk-primary-111111", "model-a", "http_401", permanent=True,
        )

        self.assertTrue(disabled)
        self.assertIn(("111111", "model-a"), verifier._failed_combos)

    def test_transient_failures_disable_combo_after_small_limit(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="sk-primary-111111"))

        first = verifier._record_combo_failure(
            "sk-primary-111111", "model-a", "TimeoutError",
        )
        second = verifier._record_combo_failure(
            "sk-primary-111111", "model-a", "TimeoutError",
        )

        self.assertFalse(first)
        self.assertTrue(second)
        self.assertIn(("111111", "model-a"), verifier._failed_combos)


if __name__ == "__main__":
    unittest.main()
