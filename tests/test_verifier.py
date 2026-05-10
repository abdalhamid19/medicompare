from __future__ import annotations

import asyncio
import unittest

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


if __name__ == "__main__":
    unittest.main()
