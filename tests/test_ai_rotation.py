from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from drug_matcher.ai_rotation import AIModelAttempt, configured_attempts, rank_attempts
from drug_matcher.ai_rotation_health import rank_health_rows
from drug_matcher.config import PROVIDERS


class AIRotationTests(unittest.TestCase):
    def test_groq_provider_is_configured(self):
        self.assertEqual(PROVIDERS["groq"]["base_url"], "https://api.groq.com/openai/v1")
        self.assertIn("GROQ_API_KEY_1", PROVIDERS["groq"]["env_keys"])

    def test_configured_attempts_masks_keys(self):
        env = {
            "GROQ_API_KEY_1": "gsk-secret123456",
            "OPENCODE_API_KEY_1": "",
        }
        with patch.dict(os.environ, env, clear=False):
            attempts = configured_attempts("groq")

        self.assertGreater(len(attempts), 0)
        self.assertEqual(attempts[0].key_masked, "...123456")
        self.assertNotIn("secret", repr(attempts[0]))

    def test_balanced_ranking_prefers_eligible_quality_then_quota(self):
        attempts = [
            AIModelAttempt(
                "groq", "url", "k", "key111111", "weak", 3,
                latency=1.0, quota_remaining=100, eligible=True,
            ),
            AIModelAttempt(
                "groq", "url", "k", "key222222", "strong", 1,
                latency=5.0, quota_remaining=1, eligible=True,
            ),
            AIModelAttempt(
                "groq", "url", "k", "key333333", "disabled", 1,
                quota_remaining=999, eligible=False,
            ),
        ]

        ranked = rank_attempts(attempts)

        self.assertEqual(ranked[0].model, "strong")
        self.assertEqual(ranked[-1].model, "disabled")

    def test_health_rows_are_ranked_with_score(self):
        rows = [
            {
                "ok": True, "quality_rank": 2, "elapsed_s": 1.0,
                "rate_remaining_requests": "100",
                "provider": "groq",
            },
            {
                "ok": True, "quality_rank": 1, "elapsed_s": 5.0,
                "rate_remaining_requests": "1",
                "provider": "opencode",
            },
            {
                "ok": False, "quality_rank": 1, "elapsed_s": 0.1,
                "provider": "groq",
            },
        ]

        ranked = rank_health_rows(rows)

        self.assertEqual(ranked[0]["provider"], "opencode")
        self.assertEqual(ranked[0]["rotation_rank"], 1)
        self.assertGreater(ranked[0]["rotation_score"], 0)
        self.assertEqual(ranked[-1]["ok"], False)


if __name__ == "__main__":
    unittest.main()
