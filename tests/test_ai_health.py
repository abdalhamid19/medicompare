from __future__ import annotations

import asyncio
import json
import unittest

from drug_matcher.ai_health import (
    AIKey,
    extract_quota_headers,
    healthy_combos,
    reset_in_text,
    test_one,
    validate_model_json,
)


class _FakeResponse:
    def __init__(self, status: int, payload: str, headers=None):
        self.status = status
        self._payload = payload
        self.headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def text(self):
        return self._payload


class _FakeSession:
    def __init__(self, status: int, payload: str, headers=None):
        self._status = status
        self._payload = payload
        self._headers = headers or {}

    def post(self, *args, **kwargs):
        return _FakeResponse(self._status, self._payload, self._headers)


class _TimeoutSession:
    def post(self, *args, **kwargs):
        raise TimeoutError("slow model")


class AIHealthTests(unittest.TestCase):
    def test_valid_json_response_is_ok(self):
        content = json.dumps({
            "is_correct": True,
            "reason": "same product",
            "confidence": 0.95,
        })
        payload = json.dumps({"choices": [{"message": {"content": content}}]})
        result = asyncio.run(
            test_one(
                _FakeSession(200, payload),
                AIKey("KEY_1", "sk-test123456"),
                "model-ok",
                "json",
                1,
                64,
            )
        )

        self.assertTrue(result["ok"])
        self.assertTrue(result["schema_ok"])
        self.assertNotIn("sk-test", result["key_masked"])

    def test_unsupported_model_is_not_ok(self):
        payload = '{"type":"error","error":{"message":"Model not supported"}}'
        result = asyncio.run(
            test_one(
                _FakeSession(401, payload),
                AIKey("KEY_1", "sk-test123456"),
                "bad-model",
                "json",
                1,
                64,
            )
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "http_401")

    def test_rate_limit_is_not_ok(self):
        payload = '{"type":"error","error":{"type":"FreeUsageLimitError"}}'
        result = asyncio.run(
            test_one(
                _FakeSession(429, payload, {"retry-after": "3600"}),
                AIKey("KEY_1", "sk-test123456"),
                "rate-limited",
                "json",
                1,
                64,
            )
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "http_429")
        self.assertEqual(result["quota_remaining_day"], "0")
        self.assertEqual(result["quota_reset_day_in"], "1h")
        self.assertEqual(result["quota_reset_in"], "1h")

    def test_invalid_json_content_is_not_ok(self):
        payload = json.dumps({"choices": [{"message": {"content": "not json"}}]})
        result = asyncio.run(
            test_one(
                _FakeSession(200, payload),
                AIKey("KEY_1", "sk-test123456"),
                "bad-json",
                "json",
                1,
                64,
            )
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "invalid_json")

    def test_timeout_is_not_ok(self):
        result = asyncio.run(
            test_one(
                _TimeoutSession(),
                AIKey("KEY_1", "sk-test123456"),
                "slow-model",
                "json",
                1,
                64,
            )
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "TimeoutError")

    def test_healthy_combos_keeps_only_json_ok_rows(self):
        rows = [
            {"ok": True, "mode": "json", "key_masked": "...123456", "model": "a"},
            {"ok": True, "mode": "plain", "key_masked": "...123456", "model": "b"},
            {"ok": False, "mode": "json", "key_masked": "...654321", "model": "c"},
        ]

        self.assertEqual(healthy_combos(rows), (("123456", "a"),))

    def test_validate_model_json_requires_schema(self):
        ok, reason, parsed = validate_model_json('{"is_correct": true}')

        self.assertFalse(ok)
        self.assertIn("missing_fields", reason)
        self.assertIsNotNone(parsed)

    def test_quota_headers_are_captured(self):
        content = json.dumps({
            "is_correct": True,
            "reason": "same product",
            "confidence": 0.95,
        })
        payload = json.dumps({"choices": [{"message": {"content": content}}]})
        headers = {
            "x-ratelimit-limit-requests": "60",
            "x-ratelimit-remaining-requests": "42",
            "x-ratelimit-reset-requests": "30",
            "x-ratelimit-limit-requests-day": "1000",
            "x-ratelimit-remaining-requests-day": "900",
            "x-ratelimit-reset-requests-day": "86400",
            "retry-after": "5",
        }

        result = asyncio.run(
            test_one(
                _FakeSession(200, payload, headers),
                AIKey("KEY_1", "sk-test123456"),
                "model-ok",
                "json",
                1,
                64,
            )
        )

        self.assertEqual(result["rate_limit_requests"], "60")
        self.assertEqual(result["rate_remaining_requests"], "42")
        self.assertEqual(result["rate_reset_requests_in"], "30s")
        self.assertEqual(result["quota_limit_day"], "1000")
        self.assertEqual(result["quota_remaining_day"], "900")
        self.assertEqual(result["quota_reset_day_in"], "1d")
        self.assertEqual(result["retry_after_in"], "5s")

    def test_extract_quota_headers_accepts_minute_aliases(self):
        info = extract_quota_headers({
            "x-rpm-limit": "10",
            "x-rpm-remaining": "7",
            "x-rpm-reset": "60",
        })

        self.assertEqual(info["quota_limit_minute"], "10")
        self.assertEqual(info["quota_remaining_minute"], "7")
        self.assertEqual(info["quota_reset_minute_in"], "1m")

    def test_reset_in_text_handles_epoch_seconds(self):
        self.assertEqual(reset_in_text("1700000060", now=1700000000), "1m")


if __name__ == "__main__":
    unittest.main()
