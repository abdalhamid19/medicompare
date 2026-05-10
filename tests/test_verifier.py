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
from drug_matcher.verifier import AIVerifier, SYSTEM_PROMPT


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
                )
            )

        user_prompt = captured["payload"]["messages"][1]["content"]
        self.assertIn("DRUG A parsed context", user_prompt)
        self.assertIn("normalized='PANADOL 20 TAB'", user_prompt)
        self.assertIn("score=88", user_prompt)
        self.assertIn("method=brand_index", user_prompt)

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
                    [({"product_name_en": "PANADOL 20 TABLETS"}, 90.0, 0)],
                )
            )

        user_prompt = captured["payload"]["messages"][1]["content"]
        self.assertIsNotNone(result)
        self.assertIn("Inventory parsed context", user_prompt)
        self.assertIn("parsed:", user_prompt)
        self.assertIn("PANADOL 20 TABLETS", user_prompt)


if __name__ == "__main__":
    unittest.main()
