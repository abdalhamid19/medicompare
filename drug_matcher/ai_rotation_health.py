"""Health checks and ranking for rotated AI attempts."""
from __future__ import annotations

import asyncio
import csv
import json
from datetime import datetime
from pathlib import Path

import aiohttp

from .ai_health import AIKey, OUT_DIR, test_one
from .ai_rotation import AIModelAttempt


async def run_rotation_health(
    attempts: tuple[AIModelAttempt, ...],
    modes: list[str],
    timeout_s: float,
    max_tokens: int,
    concurrency: int,
) -> list[dict]:
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        sem = asyncio.Semaphore(concurrency)

        async def guarded(attempt: AIModelAttempt, mode: str):
            async with sem:
                row = await test_one(
                    session,
                    AIKey(attempt.key_name, attempt.api_key),
                    attempt.model,
                    mode,
                    timeout_s,
                    max_tokens,
                    attempt.base_url,
                )
                return _with_attempt(row, attempt)

        tasks = [
            guarded(attempt, mode)
            for attempt in attempts
            for mode in modes
        ]
        return rank_health_rows(await asyncio.gather(*tasks))


def rank_health_rows(rows: list[dict]) -> list[dict]:
    ranked = sorted(rows, key=_health_sort_key)
    for idx, row in enumerate(ranked, start=1):
        row["rotation_rank"] = idx
        row["rotation_score"] = _rotation_score(row)
    return ranked


def write_rotation_reports(rows: list[dict]) -> tuple[Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = OUT_DIR / f"ai_rotation_test_{stamp}.csv"
    json_path = OUT_DIR / f"ai_rotation_test_{stamp}.json"
    if not rows:
        rows = [{"provider": "", "model": "", "ok": False}]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return csv_path, json_path


def attempts_from_health(
    attempts: tuple[AIModelAttempt, ...],
    rows: list[dict],
) -> tuple[AIModelAttempt, ...]:
    by_key = {attempt.safe_tuple(): attempt for attempt in attempts}
    selected = []
    for row in rows:
        if not row.get("ok") or row.get("mode") != "json":
            continue
        key = (
            str(row.get("provider", "")),
            str(row.get("key_suffix", "")),
            str(row.get("model", "")),
        )
        attempt = by_key.get(key)
        if attempt:
            selected.append(attempt)
    return tuple(selected)


def _with_attempt(row: dict, attempt: AIModelAttempt) -> dict:
    row["provider"] = attempt.provider
    row["quality_rank"] = attempt.quality_rank
    row["key_suffix"] = attempt.key_suffix
    return row


def _health_sort_key(row: dict):
    return (
        not row.get("ok"),
        int(row.get("quality_rank") or 999),
        -_quota_remaining(row),
        float(row.get("elapsed_s") or 9999),
        str(row.get("provider", "")),
    )


def _rotation_score(row: dict) -> float:
    if not row.get("ok"):
        return 0.0
    quality = max(0.0, 100.0 - int(row.get("quality_rank") or 100) * 10)
    quota = min(_quota_remaining(row), 1000.0) / 20.0
    latency = max(0.0, 20.0 - float(row.get("elapsed_s") or 20))
    return round(quality + quota + latency, 2)


def _quota_remaining(row: dict) -> float:
    for key in (
        "rate_remaining_requests",
        "quota_remaining_day",
        "quota_remaining_minute",
        "rate_remaining_tokens",
    ):
        value = _to_number(row.get(key))
        if value is not None:
            return value
    return 0.0


def _to_number(value) -> float | None:
    if value in (None, ""):
        return None
    text = str(value).replace(",", "").strip()
    multipliers = {"K": 1_000, "M": 1_000_000}
    suffix = text[-1:].upper()
    if suffix in multipliers:
        text = text[:-1]
        multiplier = multipliers[suffix]
    else:
        multiplier = 1
    try:
        return float(text) * multiplier
    except ValueError:
        return None
