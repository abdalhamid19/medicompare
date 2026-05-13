from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from drug_matcher.ai_rotation import (
    AIModelAttempt,
    DEFAULT_MODELS,
    PROVIDER_ORDER,
    _model_tier,
    configured_attempts,
    rank_attempts,
)
from drug_matcher.ai_rotation_health import rank_health_rows
from drug_matcher.ai_rotation_health import attempts_from_health
from drug_matcher.ai_rotation_health import attempts_from_partial_health
from drug_matcher.ai_rotation_health import cached_working_attempts
from drug_matcher.ai_rotation_health import load_latest_rotation_health
from drug_matcher.ai_rotation_health import select_preflight_attempts
from drug_matcher import ai_rotation_health
from drug_matcher.config import PROVIDERS
from run_matcher import _rotation_api_config
from run_matcher import _smart_preflight_enough
from run_matcher import _smart_preflight_attempts


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
                normalized = {m.removeprefix("models/") for m in DEFAULT_MODELS[provider]}
                self.assertIn(model.removeprefix("models/"), normalized)

    def test_model_tiers_split_default_models_into_thirds(self):
        tiers = [
            _model_tier(rank, len(DEFAULT_MODELS["groq"]))
            for rank, _ in enumerate(DEFAULT_MODELS["groq"], start=1)
        ]

        self.assertEqual(tiers[:3], [1, 1, 1])
        self.assertEqual(tiers[3:6], [2, 2, 2])
        self.assertEqual(tiers[6:], [3, 3, 3])

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

    def test_balanced_ranking_keeps_high_tier_before_lower_tier(self):
        attempts = [
            AIModelAttempt(
                "groq", "url", "k", "key111111", "tier-two", 4,
                quota_remaining=1000, rotation_tier=2,
            ),
            AIModelAttempt(
                "groq", "url", "k", "key222222", "tier-one", 3,
                quota_remaining=1, rotation_tier=1,
            ),
        ]

        ranked = rank_attempts(attempts)

        self.assertEqual(ranked[0].model, "tier-one")

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

    def test_health_ranking_prefers_higher_rotation_tier(self):
        rows = [
            {
                "ok": True, "quality_rank": 4, "rotation_tier": 1,
                "elapsed_s": 5.0, "provider": "groq",
            },
            {
                "ok": True, "quality_rank": 1, "rotation_tier": 2,
                "elapsed_s": 0.1, "provider": "opencode",
            },
        ]

        ranked = rank_health_rows(rows)

        self.assertEqual(ranked[0]["provider"], "groq")

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

    def test_select_preflight_attempts_limits_budget_and_balances_providers(self):
        attempts = tuple(
            AIModelAttempt(
                provider, "url", f"{provider.upper()}_API_KEY_1",
                f"key-{provider}-{rank:06d}", f"{provider}-model-{rank}",
                rank, rotation_tier=1 if rank <= 2 else 2,
            )
            for provider in ("groq", "github", "mistral")
            for rank in range(1, 5)
        )

        selected = select_preflight_attempts(attempts, budget=5, tier_limit=1)

        self.assertEqual(len(selected), 5)
        self.assertTrue(all(attempt.rotation_tier == 1 for attempt in selected))
        self.assertEqual(
            [attempt.provider for attempt in selected[:3]],
            ["github", "groq", "mistral"],
        )

    def test_attempts_from_partial_health_keeps_untested_fallbacks(self):
        healthy = AIModelAttempt(
            "groq", "url", "GROQ_API_KEY_1",
            "key111111", "strong", 1, rotation_tier=1,
        )
        untested = AIModelAttempt(
            "mistral", "url", "MISTRAL_API_KEY_1",
            "key222222", "backup", 1, rotation_tier=1,
        )
        failed = AIModelAttempt(
            "github", "url", "GITHUB_API_KEY_1",
            "key333333", "blocked", 1, rotation_tier=1,
        )
        rows = rank_health_rows([
            {
                "ok": True, "mode": "json", "provider": "groq",
                "key_suffix": "111111", "model": "strong",
            },
            {
                "ok": False, "mode": "json", "provider": "github",
                "key_suffix": "333333", "model": "blocked",
                "http_status": 403, "error_type": "http_403",
            },
        ])

        selected = attempts_from_partial_health((healthy, untested, failed), rows)

        self.assertEqual(selected[:2], (healthy, untested))
        self.assertEqual(selected[-1], failed)

    def test_cached_working_attempts_maps_recent_rows_to_attempts(self):
        attempt = AIModelAttempt(
            "groq", "url", "GROQ_API_KEY_1",
            "key111111", "strong", 1, rotation_tier=1,
        )
        rows = [{
            "ok": True, "mode": "json", "provider": "groq",
            "key_suffix": "111111", "model": "strong",
        }]

        selected = cached_working_attempts((attempt,), rows, limit=5)

        self.assertEqual(selected, (attempt,))

    def test_load_latest_rotation_health_ignores_corrupt_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            bad = out_dir / "ai_rotation_test_20260101_000000.json"
            bad.write_text("{bad", encoding="utf-8")
            good = out_dir / "ai_rotation_test_20260101_000001.json"
            good.write_text('[{"ok": true}]', encoding="utf-8")
            with patch.object(ai_rotation_health, "OUT_DIR", out_dir):
                rows = load_latest_rotation_health(3600)

        self.assertEqual(rows, [{"ok": True}])

    def test_rotation_api_config_builds_separate_review_plan(self):
        primary = AIModelAttempt(
            "groq", "https://api.groq.com/openai/v1", "GROQ_API_KEY_1",
            "gsk-primary111111", "openai/gpt-oss-120b", 1,
        )
        weak_reviewer = AIModelAttempt(
            "openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
            "sk-or-review222222", "openai/gpt-4o-mini", 2,
        )
        strong_reviewer = AIModelAttempt(
            "opencode", "https://opencode.ai/zen/v1", "OPENCODE_API_KEY",
            "sk-review333333", "big-pickle", 1,
        )

        cfg = _rotation_api_config(
            (primary, weak_reviewer, strong_reviewer),
            review_model="rotation",
        )

        self.assertEqual(cfg.model, "openai/gpt-oss-120b")
        self.assertEqual(cfg.review_model, "rotation")
        self.assertEqual(cfg.attempt_plan, (primary, weak_reviewer, strong_reviewer))
        self.assertEqual(cfg.review_attempt_plan, (strong_reviewer,))

    def test_smart_preflight_enough_requires_count_and_provider_diversity(self):
        rows = [
            {"ok": True, "mode": "json", "provider": "groq"},
            {"ok": True, "mode": "json", "provider": "mistral"},
            {"ok": True, "mode": "json", "provider": "github"},
        ]

        self.assertTrue(_smart_preflight_enough(rows, 3, 3))
        self.assertFalse(_smart_preflight_enough(rows[:2], 3, 2))
        self.assertFalse(_smart_preflight_enough(rows, 3, 4))

    def test_smart_preflight_attempts_refreshes_cached_plus_uncached(self):
        cached = AIModelAttempt(
            "groq", "url", "GROQ_API_KEY_1",
            "key111111", "cached", 1, rotation_tier=1,
        )
        uncached = AIModelAttempt(
            "mistral", "url", "MISTRAL_API_KEY_1",
            "key222222", "uncached", 1, rotation_tier=1,
        )
        rows = [{
            "ok": True, "mode": "json", "provider": "groq",
            "key_suffix": "111111", "model": "cached",
        }]
        with patch("run_matcher.load_latest_rotation_health", return_value=rows):
            selected, cache_rows = _smart_preflight_attempts(
                (cached, uncached), budget=2, tier_limit=1,
                cache_ttl=3600, refresh=1,
            )

        self.assertEqual(selected, (cached, uncached))
        self.assertEqual(cache_rows, rows)


if __name__ == "__main__":
    unittest.main()
