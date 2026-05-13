from __future__ import annotations

import asyncio
import unittest
from unittest.mock import patch

from drug_matcher.config import APIConfig
from drug_matcher.ai_rotation import AIModelAttempt
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
    _api_error_code,
    _extract_json,
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

    def test_extract_json_rejects_null_content(self) -> None:
        self.assertIsNone(_extract_json(None))

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
        self.assertIn("hard_conflicts", VERIFY_PROMPT)
        self.assertIn("mismatched_fields", SEARCH_PROMPT)

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

    def test_find_better_match_accepts_numeric_string_best_index(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key"))

        async def fake_call(self, payload):
            return {
                "_raw": {"best_index": "1"},
                "reason": "ok",
                "confidence": 0.9,
            }

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            result = asyncio.run(
                verifier.find_better_match(
                    "PANADOL 20 TAB",
                    [({"product_name_en": "PANADOL 20 TABLETS"}, 90.0, 0)],
                )
            )

        self.assertIsNotNone(result)
        self.assertEqual(result["record"]["product_name_en"], "PANADOL 20 TABLETS")
        self.assertEqual(result["best_index"], 1)

    def test_find_better_match_rejects_invalid_best_index_string(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key"))

        async def fake_call(self, payload):
            return {
                "_raw": {"best_index": "1-1"},
                "reason": "bad index",
                "confidence": 0.95,
                "model_used": "model-a",
            }

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            result = asyncio.run(
                verifier.find_better_match(
                    "PANADOL 20 TAB",
                    [({"product_name_en": "PANADOL 20 TABLETS"}, 90.0, 0)],
                )
            )

        self.assertIsNotNone(result)
        self.assertIsNone(result["record"])
        self.assertEqual(result["best_index"], 0)
        self.assertEqual(result["error_code"], "invalid_best_index")
        self.assertTrue(result["parse_failed"])
        self.assertIn("invalid_best_index:1-1", result["reason"])

    def test_find_better_match_rejects_missing_best_index(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key"))

        async def fake_call(self, payload):
            return {
                "_raw": {"best_index": None},
                "reason": "missing",
                "confidence": 0.9,
            }

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            result = asyncio.run(
                verifier.find_better_match(
                    "PANADOL 20 TAB",
                    [({"product_name_en": "PANADOL 20 TABLETS"}, 90.0, 0)],
                )
            )

        self.assertIsNotNone(result)
        self.assertIsNone(result["record"])
        self.assertEqual(result["error_code"], "invalid_best_index")

    def test_find_better_match_rejects_out_of_range_best_index(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key"))

        async def fake_call(self, payload):
            return {
                "_raw": {"best_index": 99},
                "reason": "out of range",
                "confidence": 0.9,
            }

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            result = asyncio.run(
                verifier.find_better_match(
                    "PANADOL 20 TAB",
                    [({"product_name_en": "PANADOL 20 TABLETS"}, 90.0, 0)],
                )
            )

        self.assertIsNotNone(result)
        self.assertIsNone(result["record"])
        self.assertEqual(result["best_index"], 0)
        self.assertEqual(result["error_code"], "invalid_best_index")

    def test_find_better_match_keeps_best_index_zero_as_no_match(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key"))

        async def fake_call(self, payload):
            return {
                "_raw": {"best_index": 0},
                "reason": "none",
                "confidence": 0.8,
            }

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            result = asyncio.run(
                verifier.find_better_match(
                    "PANADOL 20 TAB",
                    [({"product_name_en": "PANADOL 20 TABLETS"}, 90.0, 0)],
                )
            )

        self.assertIsNotNone(result)
        self.assertIsNone(result["record"])
        self.assertEqual(result["best_index"], 0)
        self.assertFalse(result["parse_failed"])

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

    def test_invalid_json_fallback_rejects_low_confidence_and_is_traceable(self) -> None:
        result = _fallback_from_unparseable_response(
            "This is a correct match but not JSON",
            "test-model",
        )

        self.assertFalse(result["is_correct"])
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

    def test_review_agreement_confirms_ai_found(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="test-key", review_model="review"))

        async def fake_call(self, payload):
            return {"agree": True, "reason": "same product", "confidence": 0.98}

        with patch.object(AIVerifier, "_call_api", new=fake_call):
            result = asyncio.run(
                verifier.review_one(
                    "AMRIZOLE N SUPP",
                    "AMRIZOLE N 5 VAG. SUPP.",
                    "ai_found",
                    0.98,
                    "different_modifier",
                )
            )

        self.assertTrue(result["is_correct"])
        self.assertEqual(result["confidence"], 0.98)

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

    def test_rate_limit_can_disable_combo_immediately_for_retry_after(self) -> None:
        verifier = AIVerifier(APIConfig(api_key="sk-primary-111111"))

        disabled = verifier._record_combo_failure(
            "sk-primary-111111", "model-a", "rate_limited",
            permanent=True, provider="groq",
        )

        self.assertTrue(disabled)
        self.assertIn(("groq", "111111", "model-a"), verifier._failed_combos)

    def test_failed_generation_error_is_classified(self) -> None:
        text = (
            '{"error":{"message":"Failed to validate JSON",'
            '"code":"json_validate_failed","failed_generation":"..."}}'
        )

        self.assertEqual(_api_error_code(400, text), "json_generation_failed")

    def test_request_plan_uses_rotated_attempts(self) -> None:
        attempt = AIModelAttempt(
            provider="groq",
            base_url="https://api.groq.com/openai/v1",
            key_name="GROQ_API_KEY_1",
            api_key="gsk-test123456",
            model="openai/gpt-oss-120b",
            quality_rank=1,
        )
        verifier = AIVerifier(APIConfig(api_key="gsk-test123456", attempt_plan=(attempt,)))

        plan = verifier._build_request_plan("ignored")

        self.assertEqual(plan[0]["provider"], "groq")
        self.assertEqual(plan[0]["base_url"], "https://api.groq.com/openai/v1")
        self.assertEqual(plan[0]["model"], "openai/gpt-oss-120b")

    def test_request_plan_skips_failed_rotated_attempt(self) -> None:
        attempt = AIModelAttempt(
            provider="groq",
            base_url="https://api.groq.com/openai/v1",
            key_name="GROQ_API_KEY_1",
            api_key="gsk-test123456",
            model="openai/gpt-oss-120b",
            quality_rank=1,
        )
        verifier = AIVerifier(APIConfig(api_key="gsk-test123456", attempt_plan=(attempt,)))
        verifier._failed_combos.add(("groq", "123456", "openai/gpt-oss-120b"))

        self.assertEqual(verifier._build_request_plan("ignored"), [])

    def test_review_rotation_skips_weaker_review_attempts(self) -> None:
        primary = AIModelAttempt(
            provider="groq",
            base_url="https://api.groq.com/openai/v1",
            key_name="GROQ_API_KEY_1",
            api_key="gsk-primary111111",
            model="openai/gpt-oss-120b",
            quality_rank=1,
        )
        reviewer = AIModelAttempt(
            provider="openrouter",
            base_url="https://openrouter.ai/api/v1",
            key_name="OPENROUTER_API_KEY",
            api_key="sk-or-review222222",
            model="openai/gpt-4o-mini",
            quality_rank=2,
        )
        cfg = APIConfig(
            api_key=primary.api_key,
            model=primary.model,
            review_model="rotation",
            attempt_plan=(primary, reviewer),
            review_attempt_plan=(reviewer,),
        )
        verifier = AIVerifier(cfg)

        plan = verifier._build_request_plan("rotation")

        self.assertEqual(plan, [])

    def test_review_rotation_uses_strong_review_attempt_plan(self) -> None:
        primary = AIModelAttempt(
            provider="groq",
            base_url="https://api.groq.com/openai/v1",
            key_name="GROQ_API_KEY_1",
            api_key="gsk-primary111111",
            model="openai/gpt-oss-120b",
            quality_rank=1,
        )
        reviewer = AIModelAttempt(
            provider="opencode",
            base_url="https://opencode.ai/zen/v1",
            key_name="OPENCODE_API_KEY",
            api_key="sk-review222222",
            model="big-pickle",
            quality_rank=1,
        )
        cfg = APIConfig(
            api_key=primary.api_key,
            model=primary.model,
            review_model="rotation",
            attempt_plan=(primary, reviewer),
            review_attempt_plan=(reviewer,),
        )
        verifier = AIVerifier(cfg)

        plan = verifier._build_request_plan("rotation")

        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["provider"], "opencode")
        self.assertEqual(plan[0]["model"], "big-pickle")

    def test_rotation_specific_review_model_filters_attempts(self) -> None:
        primary = AIModelAttempt(
            provider="groq",
            base_url="https://api.groq.com/openai/v1",
            key_name="GROQ_API_KEY_1",
            api_key="gsk-primary111111",
            model="openai/gpt-oss-120b",
            quality_rank=1,
        )
        reviewer = AIModelAttempt(
            provider="opencode",
            base_url="https://opencode.ai/zen/v1",
            key_name="OPENCODE_API_KEY_1",
            api_key="sk-review222222",
            model="big-pickle",
            quality_rank=2,
        )
        cfg = APIConfig(
            api_key=primary.api_key,
            model=primary.model,
            review_model="big-pickle",
            attempt_plan=(primary, reviewer),
        )
        verifier = AIVerifier(cfg)

        plan = verifier._build_request_plan("big-pickle")

        self.assertEqual(plan, [])

    def test_rotation_specific_strong_review_model_filters_attempts(self) -> None:
        primary = AIModelAttempt(
            provider="groq",
            base_url="https://api.groq.com/openai/v1",
            key_name="GROQ_API_KEY_1",
            api_key="gsk-primary111111",
            model="openai/gpt-oss-120b",
            quality_rank=1,
        )
        reviewer = AIModelAttempt(
            provider="opencode",
            base_url="https://opencode.ai/zen/v1",
            key_name="OPENCODE_API_KEY_1",
            api_key="sk-review222222",
            model="big-pickle",
            quality_rank=1,
        )
        cfg = APIConfig(
            api_key=primary.api_key,
            model=primary.model,
            review_model="big-pickle",
            attempt_plan=(primary, reviewer),
        )
        verifier = AIVerifier(cfg)

        plan = verifier._build_request_plan("big-pickle")

        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["provider"], "opencode")
        self.assertEqual(plan[0]["model"], "big-pickle")

    def test_rotation_request_plan_round_robins_within_same_tier(self) -> None:
        attempts = tuple(
            AIModelAttempt(
                "groq", "url", "GROQ_API_KEY_1",
                f"gsk-key{idx:06d}", f"model-{idx}", idx,
                rotation_tier=1,
            )
            for idx in range(1, 4)
        )
        verifier = AIVerifier(
            APIConfig(api_key=attempts[0].api_key, attempt_plan=attempts),
        )

        first = verifier._build_request_plan("ignored")[0]["model"]
        second = verifier._build_request_plan("ignored")[0]["model"]
        third = verifier._build_request_plan("ignored")[0]["model"]
        fourth = verifier._build_request_plan("ignored")[0]["model"]

        self.assertEqual([first, second, third, fourth], [
            "model-1", "model-2", "model-3", "model-1",
        ])

    def test_rotation_request_plan_keeps_lower_tiers_as_late_fallbacks(self) -> None:
        high = AIModelAttempt(
            "groq", "url", "GROQ_API_KEY_1",
            "gsk-high111111", "high", 1, rotation_tier=1,
        )
        low = AIModelAttempt(
            "groq", "url", "GROQ_API_KEY_1",
            "gsk-low222222", "low", 4, rotation_tier=2,
        )
        verifier = AIVerifier(
            APIConfig(api_key=high.api_key, attempt_plan=(high, low)),
        )

        plan = verifier._build_request_plan("ignored")

        self.assertEqual([item["model"] for item in plan], ["high", "low"])
        self.assertEqual([item["rotation_tier"] for item in plan], [1, 2])

    def test_rotation_request_plan_moves_to_lower_tier_when_high_tier_failed(self):
        high = AIModelAttempt(
            "groq", "url", "GROQ_API_KEY_1",
            "gsk-high111111", "high", 1, rotation_tier=1,
        )
        low = AIModelAttempt(
            "groq", "url", "GROQ_API_KEY_1",
            "gsk-low222222", "low", 4, rotation_tier=2,
        )
        verifier = AIVerifier(
            APIConfig(api_key=high.api_key, attempt_plan=(high, low)),
        )
        verifier._failed_combos.add(("groq", "111111", "high"))

        plan = verifier._build_request_plan("ignored")

        self.assertEqual(plan[0]["model"], "low")

    def test_rotation_success_on_fallback_advances_after_actual_combo(self):
        first = AIModelAttempt(
            "groq", "url", "GROQ_API_KEY_1",
            "gsk-first111111", "first", 1, rotation_tier=1,
        )
        second = AIModelAttempt(
            "groq", "url", "GROQ_API_KEY_2",
            "gsk-second222222", "second", 1, rotation_tier=1,
        )
        verifier = AIVerifier(
            APIConfig(api_key=first.api_key, attempt_plan=(first, second)),
        )

        plan = verifier._build_request_plan("ignored")
        verifier._record_rotation_used(plan[1])
        next_plan = verifier._build_request_plan("ignored")

        self.assertEqual(next_plan[0]["model"], "first")


if __name__ == "__main__":
    unittest.main()
