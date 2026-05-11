from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from drug_matcher.ai_rotation import (
    AIModelAttempt,
    DEFAULT_MODELS,
    PROVIDER_ORDER,
    configured_attempts,
    rank_attempts,
)
from drug_matcher.ai_rotation_health import rank_health_rows
from drug_matcher.ai_rotation_health import attempts_from_health
from drug_matcher.config import PROVIDERS
from run_matcher import _rotation_api_config


class AIRotationTests(unittest.TestCase):
    def test_groq_provider_is_configured(self):
        self.assertEqual(PROVIDERS["groq"]["base_url"], "https://api.groq.com/openai/v1")
        self.assertIn("GROQ_API_KEY_1", PROVIDERS["groq"]["env_keys"])

    def test_new_rotation_providers_are_configured(self):
        expected = {
            "github": ("GITHUB_API_KEY_1", "openai/gpt-4.1-mini"),
            "cloudflare": ("CLOUDFLARE_API_TOKEN_1", "@cf/openai/gpt-oss-120b"),
            "cerebras": ("CEREBRAS_API_KEY_1", "gpt-oss-120b"),
            "google": ("GOOGLE_API_KEY_1", "gemini-2.5-flash"),
            "mistral": ("MISTRAL_API_KEY_1", "mistral-small-latest"),
        }

        for provider, (key_name, model) in expected.items():
            with self.subTest(provider=provider):
                self.assertIn(provider, PROVIDERS)
                self.assertIn(provider, PROVIDER_ORDER)
                self.assertIn(key_name, PROVIDERS[provider]["env_keys"])
                self.assertIn(model, DEFAULT_MODELS[provider])

    def test_configured_attempts_reads_multiple_keys_for_new_provider(self):
        env = {
            "GITHUB_API_KEY_1": "github_pat_first123456",
            "GITHUB_API_KEY_2": "github_pat_second654321",
        }
        with patch.dict(os.environ, env, clear=False):
            attempts = configured_attempts("github")

        suffixes = {attempt.key_suffix for attempt in attempts}
        self.assertEqual(suffixes, {"123456", "654321"})
        self.assertIn("openai/gpt-4.1-mini", {attempt.model for attempt in attempts})

    def test_cloudflare_uses_base_url_env_for_rotation(self):
        env = {
            "CLOUDFLARE_BASE_URL": "https://api.cloudflare.com/client/v4/accounts/test/ai/v1",
            "CLOUDFLARE_API_TOKEN_1": "cfut_first123456",
        }
        with patch.dict(os.environ, env, clear=False):
            attempts = configured_attempts("cloudflare")

        self.assertGreater(len(attempts), 0)
        self.assertEqual(attempts[0].base_url, env["CLOUDFLARE_BASE_URL"])
        self.assertEqual(attempts[0].model, "@cf/openai/gpt-oss-120b")

    def test_cloudflare_pairs_each_token_with_matching_account_id(self):
        env = {
            "CLOUDFLARE_API_TOKEN_1": "cfut_first123456",
            "CLOUDFLARE_API_TOKEN_2": "cfut_second654321",
            "CLOUDFLARE_ACCOUNT_ID_1": "account-one",
            "CLOUDFLARE_ACCOUNT_ID_2": "account-two",
        }
        with patch.dict(os.environ, env, clear=False):
            attempts = configured_attempts("cloudflare")

        first = next(a for a in attempts if a.key_suffix == "123456")
        second = next(a for a in attempts if a.key_suffix == "654321")
        self.assertIn("/accounts/account-one/ai/v1", first.base_url)
        self.assertIn("/accounts/account-two/ai/v1", second.base_url)

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

    def test_health_ranking_keeps_failures_as_late_fallbacks(self):
        rows = [
            {
                "ok": False, "quality_rank": 1, "elapsed_s": 0.1,
                "provider": "google", "http_status": 429,
                "error_type": "http_429",
            },
            {
                "ok": False, "quality_rank": 1, "elapsed_s": 0.1,
                "provider": "google", "http_status": 403,
                "error_type": "http_403",
            },
            {
                "ok": False, "quality_rank": 1, "elapsed_s": 0.1,
                "provider": "cerebras", "http_status": 404,
                "error_type": "http_404",
                "error_message": "model_not_found",
            },
            {
                "ok": False, "quality_rank": 1, "elapsed_s": 0.1,
                "provider": "github", "error_type": "TimeoutError",
            },
            {
                "ok": True, "quality_rank": 5, "elapsed_s": 9.0,
                "provider": "mistral",
            },
        ]

        ranked = rank_health_rows(rows)

        self.assertEqual(ranked[0]["health_status"], "working")
        self.assertEqual(ranked[1]["health_status"], "degraded")
        self.assertEqual(ranked[2]["health_status"], "quota-limited")
        self.assertEqual(ranked[3]["health_status"], "permission-failed")
        self.assertEqual(ranked[4]["health_status"], "model-not-accessible")
        self.assertEqual(ranked[-1]["rotation_recommendation"], "last-choice-model-access")

    def test_attempts_from_health_falls_back_when_no_healthy_attempts(self):
        attempts = (
            AIModelAttempt(
                "google", "url", "GOOGLE_API_KEY_1",
                "key111111", "gemini-2.5-pro", 1,
            ),
            AIModelAttempt(
                "cerebras", "url", "CEREBRAS_API_KEY_1",
                "key222222", "gpt-oss-120b", 1,
            ),
        )
        rows = rank_health_rows([
            {
                "ok": False, "mode": "json", "provider": "google",
                "key_suffix": "111111", "model": "gemini-2.5-pro",
                "quality_rank": 1, "http_status": 429,
                "error_type": "http_429",
            },
            {
                "ok": False, "mode": "json", "provider": "cerebras",
                "key_suffix": "222222", "model": "gpt-oss-120b",
                "quality_rank": 1, "http_status": 404,
                "error_type": "http_404",
            },
        ])

        selected = attempts_from_health(attempts, rows)

        self.assertEqual(selected, attempts)

    def test_rotation_api_config_builds_separate_review_plan(self):
        primary = AIModelAttempt(
            "groq", "https://api.groq.com/openai/v1", "GROQ_API_KEY_1",
            "gsk-primary111111", "openai/gpt-oss-120b", 1,
        )
        reviewer = AIModelAttempt(
            "openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
            "sk-or-review222222", "openai/gpt-4o-mini", 2,
        )

        cfg = _rotation_api_config((primary, reviewer), review_model="rotation")

        self.assertEqual(cfg.model, "openai/gpt-oss-120b")
        self.assertEqual(cfg.review_model, "rotation")
        self.assertEqual(cfg.attempt_plan, (primary, reviewer))
        self.assertEqual(cfg.review_attempt_plan, (reviewer,))


if __name__ == "__main__":
    unittest.main()
