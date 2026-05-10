"""Diagnose OpenCode API keys and models with detailed safe output."""
from __future__ import annotations

import argparse
import asyncio

from drug_matcher.ai_health import (
    AIKey,
    OPENCODE_BASE_URL,
    dedupe,
    run_health_checks,
    split_csv,
    write_reports,
)
from drug_matcher.config import load_env


def _env(name: str) -> str:
    import os

    return os.getenv(name, "").strip()


def configured_keys() -> list[AIKey]:
    keys = [
        AIKey("OPENCODE_API_KEY_1", _env("OPENCODE_API_KEY_1")),
        AIKey("OPENCODE_API_KEY_2", _env("OPENCODE_API_KEY_2")),
        AIKey("OPENCODE_API_KEY", _env("OPENCODE_API_KEY")),
    ]
    seen = set()
    out = []
    for key in keys:
        if key.value and key.value not in seen:
            seen.add(key.value)
            out.append(key)
    return out


def configured_models() -> list[str]:
    return dedupe(
        [_env("AI_MODEL")]
        + split_csv(_env("FALLBACK_MODELS"))
        + [_env("REVIEW_MODEL")]
    )


def print_row(row: dict) -> None:
    status = "OK" if row["ok"] else "FAIL"
    minute = _quota_text(
        row.get("quota_remaining_minute"),
        row.get("quota_limit_minute"),
        row.get("quota_reset_minute_in"),
    )
    day = _quota_text(
        row.get("quota_remaining_day"),
        row.get("quota_limit_day"),
        row.get("quota_reset_day_in"),
    )
    requests = _quota_text(
        row.get("rate_remaining_requests"),
        row.get("rate_limit_requests"),
        row.get("rate_reset_requests_in"),
    )
    quota_reset = row.get("quota_reset_in") or "n/a"
    print(
        f"{status:4} key={row['key_name']}({row['key_masked']}) "
        f"model={row['model']} mode={row['mode']} "
        f"http={row['http_status']} elapsed={row['elapsed_s']}s "
        f"json={row['json_ok']} schema={row['schema_ok']} "
        f"rpm={minute} day={day} req={requests} "
        f"quota_reset={quota_reset} "
        f"error={row['error_type']}",
        flush=True,
    )
    if row["error_message"]:
        print(f"     {row['error_message'][:220]}", flush=True)
    if row.get("retry_after_in"):
        print(f"     retry_after={row['retry_after_in']}", flush=True)
    if row.get("rate_headers") and row.get("rate_headers") != "{}":
        print(f"     rate_headers={row['rate_headers'][:300]}", flush=True)


def _quota_text(remaining, limit, reset_in) -> str:
    remaining = str(remaining or "n/a")
    limit = str(limit or "n/a")
    reset = f", reset={reset_in}" if reset_in else ""
    return f"{remaining}/{limit}{reset}"


async def run(args) -> int:
    load_env()
    keys = configured_keys()
    models = dedupe(args.models or configured_models())
    modes = ["json", "plain"] if args.mode == "both" else [args.mode]

    if not keys:
        print("No OpenCode keys found in .env or environment.")
        return 2
    if not models:
        print("No models found. Set AI_MODEL/FALLBACK_MODELS/REVIEW_MODEL.")
        return 2

    print(f"Testing {len(keys)} key(s), {len(models)} model(s), modes={modes}")
    print(f"Base URL: {OPENCODE_BASE_URL}")
    rows = await run_health_checks(
        keys, models, modes, args.timeout,
        args.max_tokens, args.concurrency, OPENCODE_BASE_URL,
    )
    for row in rows:
        print_row(row)

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
        help="Models to test. Default: AI_MODEL + FALLBACK_MODELS + REVIEW_MODEL.",
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
