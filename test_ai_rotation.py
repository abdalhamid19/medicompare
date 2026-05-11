"""Diagnose and rank all configured AI providers for rotation."""
from __future__ import annotations

import argparse
import asyncio
from collections import Counter

from drug_matcher.ai_rotation import configured_attempts
from drug_matcher.ai_rotation_health import (
    run_rotation_health,
    write_rotation_reports,
)
from drug_matcher.config import load_env


def print_row(row: dict) -> None:
    status = "OK" if row.get("ok") else "FAIL"
    print(
        f"{status:4} rank={row.get('rotation_rank')} "
        f"provider={row.get('provider')} "
        f"key={row.get('key_name')}({row.get('key_masked')}) "
        f"model={row.get('model')} mode={row.get('mode')} "
        f"http={row.get('http_status')} elapsed={row.get('elapsed_s')}s "
        f"json={row.get('json_ok')} schema={row.get('schema_ok')} "
        f"rpd={_quota(row, 'rate_remaining_requests', 'rate_limit_requests')} "
        f"tpm={_quota(row, 'rate_remaining_tokens', 'rate_limit_tokens')} "
        f"reset={row.get('quota_reset_in') or row.get('retry_after_in') or 'n/a'} "
        f"status={row.get('health_status')} "
        f"tier={row.get('fallback_tier')} "
        f"recommend={row.get('rotation_recommendation')} "
        f"score={row.get('rotation_score')} "
        f"error={row.get('error_type')}",
        flush=True,
    )
    if row.get("error_message"):
        print(f"     {str(row['error_message'])[:220]}", flush=True)


def _quota(row: dict, remaining_key: str, limit_key: str) -> str:
    remaining = row.get(remaining_key) or "n/a"
    limit = row.get(limit_key) or "n/a"
    return f"{remaining}/{limit}"


def print_summary(rows: list[dict]) -> None:
    by_status = Counter(row.get("health_status", "unknown") for row in rows)
    by_provider_status = Counter(
        (row.get("provider", ""), row.get("health_status", "unknown"))
        for row in rows
    )
    print("\nStatus summary:", flush=True)
    for status, count in by_status.most_common():
        print(f"  {status}: {count}", flush=True)
    print("\nProvider/status summary:", flush=True)
    for (provider, status), count in sorted(by_provider_status.items()):
        print(f"  {provider}: {status}={count}", flush=True)


async def run(args) -> int:
    load_env()
    attempts = configured_attempts(args.providers)
    modes = ["json", "plain"] if args.mode == "both" else [args.mode]
    if args.models:
        wanted = set(args.models)
        attempts = tuple(a for a in attempts if a.model in wanted)
    if not attempts:
        print("No rotation attempts found. Configure provider API keys in .env.")
        return 2

    print(
        f"Testing {len(attempts)} attempt(s), "
        f"providers={args.providers}, modes={modes}",
    )
    rows = await run_rotation_health(
        attempts, modes, args.timeout,
        args.max_tokens, args.concurrency,
    )
    for row in rows:
        print_row(row)
    print_summary(rows)
    csv_path, json_path = write_rotation_reports(rows)
    ok_count = sum(1 for row in rows if row.get("ok"))
    print(f"\nSummary: {ok_count}/{len(rows)} passed")
    print(f"CSV:  {csv_path}")
    print(f"JSON: {json_path}")
    return 0 if ok_count else 1


def parse_args():
    parser = argparse.ArgumentParser(
        description="Test and rank all configured AI provider/model attempts.",
    )
    parser.add_argument(
        "--providers", default="auto",
        help="Comma-separated providers or auto. Example: groq,opencode",
    )
    parser.add_argument("--models", nargs="+", default=None)
    parser.add_argument(
        "--mode", choices=["json", "plain", "both"], default="json",
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--concurrency", type=int, default=4)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run(parse_args())))
