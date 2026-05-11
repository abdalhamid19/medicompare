#!/usr/bin/env python3
"""Fetch all models + rate limits from each provider API and export CSV/JSON.

Usage:
    python tools/fetch_models.py
    python tools/fetch_models.py --no-probe   # skip rate-limit probing
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import aiohttp
except ImportError:
    print("pip install aiohttp")
    sys.exit(1)

# ── Paths ──────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output" / "models"

# ── Load .env ──────────────────────────────────────────────
_env = ROOT / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

# ── Provider config ────────────────────────────────────────
PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/models",
        "chat_url": "https://api.groq.com/openai/v1/chat/completions",
        "keys": [os.getenv("GROQ_API_KEY_1", ""), os.getenv("GROQ_API_KEY", "")],
        "all_free": True,  # Groq has no paid tier — all models free within rate limits
    },
    "opencode": {
        "url": "https://opencode.ai/zen/v1/models",
        "chat_url": "https://opencode.ai/zen/v1/chat/completions",
        "keys": [
            os.getenv("OPENCODE_API_KEY_1", ""),
            os.getenv("OPENCODE_API_KEY_2", ""),
            os.getenv("OPENCODE_API_KEY", ""),
        ],
        "all_free": False,
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/models",
        "chat_url": "",  # no probe needed — pricing in /models
        "keys": [],  # public endpoint
        "all_free": False,
    },
    "cerebras": {
        "url": "https://api.cerebras.ai/v1/models",
        "chat_url": "https://api.cerebras.ai/v1/chat/completions",
        "keys": [os.getenv("CEREBRAS_API_KEY_1", ""), os.getenv("CEREBRAS_API_KEY", "")],
        "all_free": True,  # Cerebras has no paid tier
    },
    "github": {
        "url": "https://models.github.ai/v1/models",
        "chat_url": "https://models.github.ai/v1/chat/completions",
        "keys": [os.getenv("GITHUB_API_KEY_1", ""), os.getenv("GITHUB_API_KEY", "")],
        "all_free": True,  # GitHub Models free within rate limits
    },
    "google": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models",
        "chat_url": "",  # Google uses different chat endpoint format
        "keys": [os.getenv("GOOGLE_API_KEY_1", ""), os.getenv("GOOGLE_API_KEY", "")],
        "all_free": True,  # Google Gemini free within rate limits
        "response_key": "models",  # different API response key
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/models",
        "chat_url": "https://api.mistral.ai/v1/chat/completions",
        "keys": [os.getenv("MISTRAL_API_KEY_1", ""), os.getenv("MISTRAL_API_KEY", "")],
        "all_free": False,
    },
    "cloudflare": {
        "url": "",  # built dynamically from account_id
        "chat_url": "",  # built dynamically
        "keys": [os.getenv("CLOUDFLARE_API_TOKEN_1", ""), os.getenv("CLOUDFLARE_API_TOKEN", "")],
        "all_free": True,  # Cloudflare Workers AI free within limits
        "account_id": os.getenv("CLOUDFLARE_ACCOUNT_ID_1", "") or os.getenv("CLOUDFLARE_ACCOUNT_ID", ""),
        "response_key": "result",  # different API response key
    },
}

# ── Helpers ────────────────────────────────────────────────
def _is_free(model_id: str, pricing: dict, provider_all_free: bool) -> bool:
    if provider_all_free:
        return True
    if ":free" in model_id or model_id.endswith("-free"):
        return True
    p = pricing.get("prompt", "N/A")
    c = pricing.get("completion", "N/A")
    return str(p) == "0" and str(c) == "0"


def _safe(val, default=""):
    if val is None:
        return default
    return val


def _key(providers_cfg: dict, name: str) -> str:
    return next((k for k in providers_cfg[name]["keys"] if k), "")


# ── Fetch /models ──────────────────────────────────────────
async def fetch_models(
    session: aiohttp.ClientSession, name: str, url: str, keys: list[str],
    response_key: str = "data", provider_cfg: dict | None = None,
) -> list[dict]:
    headers = {"Content-Type": "application/json"}
    key = next((k for k in keys if k), "")

    # Google: key goes in URL query param
    if name == "google" and key:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}key={key}"
    # Cloudflare: build URL from account_id
    elif name == "cloudflare":
        account_id = (provider_cfg or {}).get("account_id", "")
        if not account_id:
            print(f"  ❌ {name}: no CLOUDFLARE_ACCOUNT_ID")
            return []
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/models/search"
        if key:
            headers["Authorization"] = f"Bearer {key}"
    elif key:
        headers["Authorization"] = f"Bearer {key}"

    try:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                print(f"  ❌ {name}: status={resp.status} {text[:200]}")
                return []
            data = await resp.json()
            return data.get(response_key, [])
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        return []


# ── Probe rate limits via a tiny chat request ──────────────
async def probe_rate_limits(
    session: aiohttp.ClientSession,
    provider: str,
    chat_url: str,
    key: str,
    model_id: str,
) -> dict:
    """Send a 1-token chat request and extract rate-limit headers."""
    if not chat_url or not key:
        return {}
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
    }
    info: dict = {"probe_status": "", "rate_limit_requests": "", "rate_limit_tokens": "",
                  "rate_remaining_requests": "", "rate_remaining_tokens": "",
                  "rate_reset_requests": "", "retry_after": "", "probe_error": ""}
    try:
        async with session.post(chat_url, headers=headers, json=payload) as resp:
            info["probe_status"] = resp.status
            for h in resp.headers:
                hl = h.lower()
                if "ratelimit-limit-requests" in hl:
                    info["rate_limit_requests"] = resp.headers[h]
                elif "ratelimit-limit-tokens" in hl:
                    info["rate_limit_tokens"] = resp.headers[h]
                elif "ratelimit-remaining-requests" in hl:
                    info["rate_remaining_requests"] = resp.headers[h]
                elif "ratelimit-remaining-tokens" in hl:
                    info["rate_remaining_tokens"] = resp.headers[h]
                elif "ratelimit-reset-requests" in hl:
                    info["rate_reset_requests"] = resp.headers[h]
                elif "retry-after" in hl:
                    info["retry_after"] = resp.headers[h]
            if resp.status == 429:
                body = await resp.text()
                info["probe_error"] = body[:200]
    except Exception as e:
        info["probe_status"] = "error"
        info["probe_error"] = str(e)[:200]
    return info


# ── Normalize model data ───────────────────────────────────
def normalize_model(provider: str, m: dict, provider_all_free: bool) -> dict:
    mid = m.get("id", "")
    pricing = m.get("pricing", {})
    arch = m.get("architecture", {})
    top = m.get("top_provider", {})
    per_req = m.get("per_request_limits")

    prompt_price = pricing.get("prompt", "N/A")
    comp_price = pricing.get("completion", "N/A")
    is_free = _is_free(mid, pricing, provider_all_free)

    row = {
        "provider": provider,
        "model_id": mid,
        "name": m.get("name", ""),
        "owned_by": m.get("owned_by", ""),
        "is_free": is_free,
        "prompt_price_per_1m": prompt_price,
        "completion_price_per_1m": comp_price,
        "image_price_per_1m": pricing.get("image", ""),
        "audio_price_per_1m": pricing.get("audio", ""),
        "web_search_price": pricing.get("web_search", ""),
        "input_cache_read_price": pricing.get("input_cache_read", ""),
        "input_cache_write_price": pricing.get("input_cache_write", ""),
        "internal_reasoning_price": pricing.get("internal_reasoning", ""),
        "context_length": _safe(m.get("context_length") or m.get("context_window"), ""),
        "modality": arch.get("modality", ""),
        "input_modalities": "|".join(arch.get("input_modalities") or []),
        "output_modalities": "|".join(arch.get("output_modalities") or []),
        "tokenizer": arch.get("tokenizer", ""),
        "instruct_type": arch.get("instruct_type", ""),
        "max_completion_tokens": _safe(
            m.get("max_completion_tokens") or (top.get("max_completion_tokens") if top else None), ""
        ),
        "is_moderated": _safe(top.get("is_moderated") if top else None, ""),
        "per_request_limits": _safe(per_req, ""),
        "supported_parameters": "|".join(m.get("supported_parameters") or []),
        "knowledge_cutoff": _safe(m.get("knowledge_cutoff"), ""),
        "expiration_date": _safe(m.get("expiration_date"), ""),
        "active": _safe(m.get("active"), ""),
        "description": (m.get("description") or "")[:500],
        # rate limit fields (filled by probe)
        "probe_status": "",
        "rate_limit_requests": "",
        "rate_limit_tokens": "",
        "rate_remaining_requests": "",
        "rate_remaining_tokens": "",
        "rate_reset_requests": "",
        "retry_after": "",
        "probe_error": "",
    }
    return row


def normalize_google(m: dict) -> dict:
    """Normalize Google Gemini API model format."""
    mid = m.get("name", "")  # e.g. "models/gemini-2.5-flash"
    display = m.get("displayName", "")
    is_free = True  # Google Gemini free tier
    return {
        "provider": "google",
        "model_id": mid,
        "name": display,
        "owned_by": "Google",
        "is_free": is_free,
        "prompt_price_per_1m": "0",
        "completion_price_per_1m": "0",
        "image_price_per_1m": "",
        "audio_price_per_1m": "",
        "web_search_price": "",
        "input_cache_read_price": "",
        "input_cache_write_price": "",
        "internal_reasoning_price": "",
        "context_length": _safe(m.get("inputTokenLimit"), ""),
        "modality": "text+image+audio+video->text",
        "input_modalities": "|".join(m.get("supportedGenerationMethods", [])),
        "output_modalities": "text",
        "tokenizer": "",
        "instruct_type": "",
        "max_completion_tokens": _safe(m.get("outputTokenLimit"), ""),
        "is_moderated": "",
        "per_request_limits": "",
        "supported_parameters": "|".join(m.get("supportedGenerationMethods", [])),
        "knowledge_cutoff": "",
        "expiration_date": "",
        "active": "true" if "generateContent" in m.get("supportedGenerationMethods", []) else "false",
        "description": (m.get("description") or "")[:500],
        "probe_status": "",
        "rate_limit_requests": "",
        "rate_limit_tokens": "",
        "rate_remaining_requests": "",
        "rate_remaining_tokens": "",
        "rate_reset_requests": "",
        "retry_after": "",
        "probe_error": "",
    }


def normalize_cloudflare(m: dict) -> dict:
    """Normalize Cloudflare Workers AI model format."""
    mid = m.get("name", "")  # e.g. "@cf/openai/gpt-oss-120b"
    task = m.get("task", {})
    task_name = task.get("name", "") if task else ""
    is_free = True  # Cloudflare Workers AI free within limits
    return {
        "provider": "cloudflare",
        "model_id": mid,
        "name": mid.replace("@cf/", ""),
        "owned_by": "",
        "is_free": is_free,
        "prompt_price_per_1m": "0",
        "completion_price_per_1m": "0",
        "image_price_per_1m": "",
        "audio_price_per_1m": "",
        "web_search_price": "",
        "input_cache_read_price": "",
        "input_cache_write_price": "",
        "internal_reasoning_price": "",
        "context_length": "",
        "modality": task_name,
        "input_modalities": "",
        "output_modalities": "",
        "tokenizer": "",
        "instruct_type": "",
        "max_completion_tokens": "",
        "is_moderated": "",
        "per_request_limits": "",
        "supported_parameters": "",
        "knowledge_cutoff": "",
        "expiration_date": "",
        "active": "true",
        "description": (m.get("description") or "")[:500],
        "probe_status": "",
        "rate_limit_requests": "",
        "rate_limit_tokens": "",
        "rate_remaining_requests": "",
        "rate_remaining_tokens": "",
        "rate_reset_requests": "",
        "retry_after": "",
        "probe_error": "",
    }


def normalize_github(m: dict) -> dict:
    """Normalize GitHub Models API format."""
    mid = m.get("id", "")
    rate_tier = m.get("rate_limit_tier", "")
    is_free = True  # GitHub Models free within rate limits
    return {
        "provider": "github",
        "model_id": mid,
        "name": m.get("name", ""),
        "owned_by": m.get("publisher", ""),
        "is_free": is_free,
        "prompt_price_per_1m": "0",
        "completion_price_per_1m": "0",
        "image_price_per_1m": "",
        "audio_price_per_1m": "",
        "web_search_price": "",
        "input_cache_read_price": "",
        "input_cache_write_price": "",
        "internal_reasoning_price": "",
        "context_length": "",
        "modality": "",
        "input_modalities": "|".join(m.get("supported_input_modalities", [])),
        "output_modalities": "|".join(m.get("supported_output_modalities", [])),
        "tokenizer": "",
        "instruct_type": "",
        "max_completion_tokens": "",
        "is_moderated": "",
        "per_request_limits": rate_tier,
        "supported_parameters": "",
        "knowledge_cutoff": "",
        "expiration_date": "",
        "active": "true",
        "description": (m.get("summary") or "")[:500],
        "probe_status": "",
        "rate_limit_requests": "",
        "rate_limit_tokens": "",
        "rate_remaining_requests": "",
        "rate_remaining_tokens": "",
        "rate_reset_requests": "",
        "retry_after": "",
        "probe_error": "",
    }


def normalize_mistral(m: dict) -> dict:
    """Normalize Mistral API model format."""
    mid = m.get("id", "")
    caps = m.get("capabilities", {})
    is_free = "free" in mid.lower() or mid.startswith("mistral-small") or mid.startswith("ministral") or mid.startswith("codestral")
    return {
        "provider": "mistral",
        "model_id": mid,
        "name": m.get("name", mid),
        "owned_by": m.get("owned_by", "mistralai"),
        "is_free": is_free,
        "prompt_price_per_1m": "",
        "completion_price_per_1m": "",
        "image_price_per_1m": "",
        "audio_price_per_1m": "",
        "web_search_price": "",
        "input_cache_read_price": "",
        "input_cache_write_price": "",
        "internal_reasoning_price": "",
        "context_length": _safe(m.get("max_context_length"), ""),
        "modality": "",
        "input_modalities": "",
        "output_modalities": "",
        "tokenizer": "",
        "instruct_type": "",
        "max_completion_tokens": _safe(m.get("max_output_tokens"), ""),
        "is_moderated": "",
        "per_request_limits": "",
        "supported_parameters": "|".join(k for k, v in caps.items() if v is True) if caps else "",
        "knowledge_cutoff": "",
        "expiration_date": "",
        "active": "true",
        "description": (m.get("description") or "")[:500],
        "probe_status": "",
        "rate_limit_requests": "",
        "rate_limit_tokens": "",
        "rate_remaining_requests": "",
        "rate_remaining_tokens": "",
        "rate_reset_requests": "",
        "retry_after": "",
        "probe_error": "",
    }


# Map provider name to its normalize function
NORMALIZE_FN = {
    "google": normalize_google,
    "cloudflare": normalize_cloudflare,
    "github": normalize_github,
    "mistral": normalize_mistral,
}


# ── Main ───────────────────────────────────────────────────
async def main(args):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    all_rows: list[dict] = []

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        for name, info in PROVIDERS.items():
            print(f"\n{'='*60}")
            print(f"  {name.upper()} — {info.get('url') or '(dynamic)'}")
            print(f"{'='*60}")
            response_key = info.get("response_key", "data")
            models = await fetch_models(session, name, info.get("url", ""), info["keys"],
                                        response_key=response_key, provider_cfg=info)
            if not models:
                continue

            key = _key(PROVIDERS, name)
            chat_url = info.get("chat_url", "")

            free_models = []
            paid_models = []
            for m in models:
                # Cloudflare: skip non-text-generation models
                if name == "cloudflare":
                    task_name = (m.get("task") or {}).get("name", "")
                    if task_name not in ("Text Generation", "Text Generation 2"):
                        continue
                # Google: skip models that don't support generateContent
                if name == "google":
                    methods = m.get("supportedGenerationMethods", [])
                    if "generateContent" not in methods:
                        continue

                # Use provider-specific normalize if available, else generic
                norm_fn = NORMALIZE_FN.get(name)
                if norm_fn:
                    row = norm_fn(m)
                else:
                    row = normalize_model(name, m, info["all_free"])

                # Probe rate limits for chat models (skip whisper, guard, etc.)
                if args.probe and chat_url and key:
                    mid = row["model_id"]
                    is_non_chat = any(kw in mid.lower() for kw in ["whisper", "guard", "safeguard", "orpheus"])
                    is_chat = not is_non_chat and (
                        row["modality"].startswith("text")
                        or "text" in row["input_modalities"]
                        or row["context_length"] not in ("", "448", "512")  # Groq has no modality field
                    )
                    if is_chat:
                        print(f"    Probing {mid}...", end="", flush=True)
                        rl = await probe_rate_limits(session, name, chat_url, key, mid)
                        row.update(rl)
                        print(f" status={rl.get('probe_status','')} lim_req={rl.get('rate_limit_requests','')} lim_tok={rl.get('rate_limit_tokens','')}")
                        # Small delay to avoid hitting rate limits during probing
                        await asyncio.sleep(0.3)

                all_rows.append(row)
                if row["is_free"]:
                    free_models.append(row["model_id"])
                else:
                    paid_models.append(row["model_id"])

            print(f"  Total: {len(models)}  |  Free: {len(free_models)}  |  Paid: {len(paid_models)}")
            if free_models:
                for f in sorted(free_models):
                    print(f"    ✅ {f}")
            if paid_models:
                for p in sorted(paid_models):
                    print(f"    💰 {p}")

    # ── Export ──────────────────────────────────────────────
    if not all_rows:
        print("\nNo models fetched. Exiting.")
        return

    # JSON
    json_path = OUTPUT_DIR / f"models_{ts}.json"
    json_path.write_text(json.dumps(all_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n📄 JSON → {json_path}")

    # CSV
    csv_path = OUTPUT_DIR / f"models_{ts}.csv"
    fieldnames = list(all_rows[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"📊 CSV  → {csv_path}")

    # ── Summary ─────────────────────────────────────────────
    free_count = sum(1 for r in all_rows if r["is_free"])
    paid_count = len(all_rows) - free_count
    print(f"\n{'='*60}")
    print(f"  SUMMARY: {len(all_rows)} models | {free_count} free | {paid_count} paid")
    for prov in PROVIDERS:
        prov_rows = [r for r in all_rows if r["provider"] == prov]
        prov_free = sum(1 for r in prov_rows if r["is_free"])
        print(f"    {prov}: {len(prov_rows)} models ({prov_free} free)")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch models + rate limits from providers")
    parser.add_argument("--no-probe", dest="probe", action="store_false",
                        help="Skip rate-limit probing (faster but less info)")
    args = parser.parse_args()
    asyncio.run(main(args))
