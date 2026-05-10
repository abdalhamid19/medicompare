"""Diagnose OpenCode API keys and models with detailed safe output.

This script is intentionally not part of the normal unit test suite. It reads
keys/models from .env, masks secrets, calls the OpenCode chat completions API,
and writes CSV/JSON reports under output/api_model_tests/.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

from drug_matcher.config import PROVIDERS, load_env
from drug_matcher.verifier import _extract_json

BASE_URL = PROVIDERS["opencode"]["base_url"]
OUT_DIR = Path("output/api_model_tests")

TEST_MESSAGES = [
    {
        "role": "system",
        "content": (
            "Return JSON only. You verify whether two drug product names are "
            "the same sellable product."
        ),
    },
    {
        "role": "user",
        "content": (
            'Are these the same product? A="PANADOL 20 TAB", '
            'B="PANADOL 20 TABLETS". Return exactly: '
            '{"is_correct": true, "reason": "brief", "confidence": 0.0-1.0}'
        ),
    },
]


def _env(name: str) -> str:
    import os

    return os.getenv(name, "").strip()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def configured_keys() -> list[tuple[str, str]]:
    keys = [
        ("OPENCODE_API_KEY_1", _env("OPENCODE_API_KEY_1")),
        ("OPENCODE_API_KEY_2", _env("OPENCODE_API_KEY_2")),
        ("OPENCODE_API_KEY", _env("OPENCODE_API_KEY")),
    ]
    seen = set()
    out = []
    for name, key in keys:
        if key and key not in seen:
            seen.add(key)
            out.append((name, key))
    return out


def configured_models() -> list[str]:
    return _dedupe(
        [_env("AGENT_ROUTER_MODEL")]
        + _split_csv(_env("FALLBACK_MODELS"))
        + [_env("REVIEW_MODEL")]
    )


def mask_key(key: str) -> str:
    return f"...{key[-6:]}" if key else ""


def build_payload(model: str, mode: str, max_tokens: int) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": TEST_MESSAGES,
        "max_tokens": max_tokens,
        "temperature": 0.1,
    }
    if mode == "json":
        payload["response_format"] = {"type": "json_object"}
    return payload


def _content_from_response(data: Any) -> tuple[str, str]:
    try:
        choice = data["choices"][0]
        message = choice.get("message", {})
        content = message.get("content", "")
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        return str(content or ""), ""
    except Exception as exc:  # noqa: BLE001 - this is a diagnostics script.
        return "", f"{type(exc).__name__}: {exc}"


def validate_model_json(content: str) -> tuple[bool, str, dict[str, Any] | None]:
    parsed = _extract_json(content)
    if parsed is None:
        return False, "invalid_json", None
    required = {"is_correct", "reason", "confidence"}
    missing = sorted(required - set(parsed))
    if missing:
        return False, f"missing_fields:{','.join(missing)}", parsed
    return True, "ok", parsed


async def test_one(
    session: aiohttp.ClientSession,
    key_name: str,
    key: str,
    model: str,
    mode: str,
    timeout_s: float,
    max_tokens: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    result: dict[str, Any] = {
        "key_name": key_name,
        "key_masked": mask_key(key),
        "model": model,
        "mode": mode,
        "base_url": BASE_URL,
        "http_status": "",
        "elapsed_s": "",
        "ok": False,
        "json_ok": False,
        "schema_ok": False,
        "is_correct": "",
        "confidence": "",
        "error_type": "",
        "error_message": "",
        "content_excerpt": "",
        "raw_excerpt": "",
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = build_payload(model, mode, max_tokens)
    try:
        async with session.post(
            f"{BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=timeout_s),
        ) as resp:
            result["http_status"] = resp.status
            text = await resp.text()
            result["raw_excerpt"] = text[:500].replace("\n", "\\n")
            if resp.status != 200:
                result["error_type"] = f"http_{resp.status}"
                result["error_message"] = text[:300].replace("\n", " ")
                return result
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                result["error_type"] = "response_not_json"
                result["error_message"] = str(exc)
                return result
            content, content_error = _content_from_response(data)
            result["content_excerpt"] = content[:500].replace("\n", "\\n")
            if content_error:
                result["error_type"] = "response_shape"
                result["error_message"] = content_error
                return result
            schema_ok, reason, parsed = validate_model_json(content)
            result["json_ok"] = parsed is not None
            result["schema_ok"] = schema_ok
            if parsed:
                result["is_correct"] = parsed.get("is_correct", "")
                result["confidence"] = parsed.get("confidence", "")
            if not schema_ok:
                result["error_type"] = reason
                result["error_message"] = content[:300].replace("\n", " ")
                return result
            result["ok"] = True
            return result
    except Exception as exc:  # noqa: BLE001 - report exact runtime failure.
        result["error_type"] = type(exc).__name__
        result["error_message"] = str(exc)[:300]
        return result
    finally:
        result["elapsed_s"] = round(time.perf_counter() - started, 3)


def print_row(row: dict[str, Any]) -> None:
    status = "OK" if row["ok"] else "FAIL"
    print(
        f"{status:4} key={row['key_name']}({row['key_masked']}) "
        f"model={row['model']} mode={row['mode']} "
        f"http={row['http_status']} elapsed={row['elapsed_s']}s "
        f"json={row['json_ok']} schema={row['schema_ok']} "
        f"error={row['error_type']}",
        flush=True,
    )
    if row["error_message"]:
        print(f"     {row['error_message'][:220]}", flush=True)


def write_reports(rows: list[dict[str, Any]]) -> tuple[Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = OUT_DIR / f"opencode_model_test_{stamp}.csv"
    json_path = OUT_DIR / f"opencode_model_test_{stamp}.json"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return csv_path, json_path


async def run(args) -> int:
    load_env()
    keys = configured_keys()
    models = _dedupe(args.models or configured_models())
    modes = ["json", "plain"] if args.mode == "both" else [args.mode]

    if not keys:
        print("No OpenCode keys found in .env or environment.")
        return 2
    if not models:
        print("No models found. Set AGENT_ROUTER_MODEL/FALLBACK_MODELS/REVIEW_MODEL.")
        return 2

    print(f"Testing {len(keys)} key(s), {len(models)} model(s), modes={modes}")
    print(f"Base URL: {BASE_URL}")
    rows = []
    connector = aiohttp.TCPConnector(limit=args.concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        sem = asyncio.Semaphore(args.concurrency)

        async def guarded(key_name, key, model, mode):
            async with sem:
                row = await test_one(
                    session, key_name, key, model, mode,
                    args.timeout, args.max_tokens,
                )
                print_row(row)
                return row

        tasks = [
            guarded(key_name, key, model, mode)
            for key_name, key in keys
            for model in models
            for mode in modes
        ]
        rows = await asyncio.gather(*tasks)

    csv_path, json_path = write_reports(rows)
    ok_count = sum(1 for row in rows if row["ok"])
    print(f"\nSummary: {ok_count}/{len(rows)} passed")
    print(f"CSV:  {csv_path}")
    print(f"JSON: {json_path}")
    return 0 if ok_count else 1


def parse_args():
    parser = argparse.ArgumentParser(
        description="Test OpenCode keys/models and save detailed diagnostics.",
    )
    parser.add_argument(
        "--models", nargs="+", default=None,
        help="Models to test. Default: AGENT_ROUTER_MODEL + FALLBACK_MODELS + REVIEW_MODEL.",
    )
    parser.add_argument(
        "--mode", choices=["json", "plain", "both"], default="json",
        help="Test response_format JSON mode, plain mode, or both.",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--concurrency", type=int, default=4)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run(parse_args())))
