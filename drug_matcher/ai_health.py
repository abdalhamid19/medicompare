"""Reusable AI provider health checks."""
from __future__ import annotations

import asyncio
import csv
import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

from .config import PROVIDERS
from .verifier import _extract_json

OPENCODE_BASE_URL = PROVIDERS["opencode"]["base_url"]
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


@dataclass(frozen=True, slots=True)
class AIKey:
    name: str
    value: str


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


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


def content_from_response(data: Any) -> tuple[str, str]:
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
    except Exception as exc:  # noqa: BLE001 - diagnostics should report type.
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


def empty_result(key: AIKey, model: str, mode: str, base_url: str) -> dict[str, Any]:
    return {
        "key_name": key.name,
        "key_masked": mask_key(key.value),
        "model": model,
        "mode": mode,
        "base_url": base_url,
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


async def test_one(
    session: aiohttp.ClientSession,
    key: AIKey,
    model: str,
    mode: str,
    timeout_s: float,
    max_tokens: int,
    base_url: str = OPENCODE_BASE_URL,
) -> dict[str, Any]:
    started = time.perf_counter()
    result = empty_result(key, model, mode, base_url)
    headers = {
        "Authorization": f"Bearer {key.value}",
        "Content-Type": "application/json",
    }
    payload = build_payload(model, mode, max_tokens)
    try:
        async with session.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=timeout_s),
        ) as resp:
            return await _handle_response(resp, result)
    except Exception as exc:  # noqa: BLE001 - report exact runtime failure.
        result["error_type"] = type(exc).__name__
        result["error_message"] = str(exc)[:300]
        return result
    finally:
        result["elapsed_s"] = round(time.perf_counter() - started, 3)


async def _handle_response(resp, result: dict[str, Any]) -> dict[str, Any]:
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
    content, content_error = content_from_response(data)
    result["content_excerpt"] = content[:500].replace("\n", "\\n")
    if content_error:
        result["error_type"] = "response_shape"
        result["error_message"] = content_error
        return result
    return _validate_content(content, result)


def _validate_content(content: str, result: dict[str, Any]) -> dict[str, Any]:
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


async def run_health_checks(
    keys: list[AIKey],
    models: list[str],
    modes: list[str],
    timeout_s: float = 20.0,
    max_tokens: int = 256,
    concurrency: int = 4,
    base_url: str = OPENCODE_BASE_URL,
) -> list[dict[str, Any]]:
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        sem = asyncio.Semaphore(concurrency)

        async def guarded(key: AIKey, model: str, mode: str):
            async with sem:
                return await test_one(
                    session, key, model, mode,
                    timeout_s, max_tokens, base_url,
                )

        tasks = [
            guarded(key, model, mode)
            for key in keys
            for model in models
            for mode in modes
        ]
        return await asyncio.gather(*tasks)


def healthy_combos(rows: list[dict[str, Any]]) -> tuple[tuple[str, str], ...]:
    combos = []
    seen = set()
    for row in rows:
        if not row.get("ok") or row.get("mode") != "json":
            continue
        combo = (str(row["key_masked"])[-6:], str(row["model"]))
        if combo not in seen:
            seen.add(combo)
            combos.append(combo)
    return tuple(combos)


def write_reports(rows: list[dict[str, Any]]) -> tuple[Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = OUT_DIR / f"opencode_model_test_{stamp}.csv"
    json_path = OUT_DIR / f"opencode_model_test_{stamp}.json"
    if not rows:
        rows = [empty_result(AIKey("", ""), "", "", OPENCODE_BASE_URL)]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return csv_path, json_path
