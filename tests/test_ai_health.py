from __future__ import annotations

import asyncio
import json
import unittest

from drug_matcher.ai_health import (
    AIKey,
    healthy_combos,
    test_one,
    validate_model_json,
)


class _FakeResponse:
    def __init__(self, status: int, payload: str):
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def text(self):
        return self._payload


class _FakeSession:
    def __init__(self, status: int, payload: str):
        self._status = status
        self._payload = payload

    def post(self, *args, **kwargs):
        return _FakeResponse(self._status, self._payload)


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
                _FakeSession(429, payload),
                AIKey("KEY_1", "sk-test123456"),
                "rate-limited",
                "json",
                1,
                64,
            )
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "http_429")

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


if __name__ == "__main__":
    unittest.main()
