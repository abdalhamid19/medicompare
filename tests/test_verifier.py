from __future__ import annotations

import asyncio
import unittest

from drug_matcher.config import APIConfig
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


if __name__ == "__main__":
    unittest.main()
