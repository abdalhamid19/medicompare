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
        [_env("AGENT_ROUTER_MODEL")]
        + split_csv(_env("FALLBACK_MODELS"))
        + [_env("REVIEW_MODEL")]
    )


def print_row(row: dict) -> None:
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


async def run(args) -> int:
    load_env()
    keys = configured_keys()
    models = dedupe(args.models or configured_models())
    modes = ["json", "plain"] if args.mode == "both" else [args.mode]

    if not keys:
        print("No OpenCode keys found in .env or environment.")
        return 2
    if not models:
        print("No models found. Set AGENT_ROUTER_MODEL/FALLBACK_MODELS/REVIEW_MODEL.")
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
