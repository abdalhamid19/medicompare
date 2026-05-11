"""Provider/model rotation planning for AI calls."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from .ai_health import dedupe, mask_key, split_csv
from .config import PROVIDERS, cloudflare_base_url, provider_base_url

PROVIDER_ORDER = (
    "groq",
    "opencode",
    "openrouter",
    "github",
    "cerebras",
    "google",
    "mistral",
    "cloudflare",
)

DEFAULT_MODELS = {
    "groq": (
        "openai/gpt-oss-120b",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "qwen/qwen3-32b",
        "llama-3.3-70b-versatile",
        "groq/compound",
        "openai/gpt-oss-20b",
        "groq/compound-mini",
        "llama-3.1-8b-instant",
        "allam-2-7b",
    ),
    "opencode": (
        "big-pickle",
        "nemotron-3-super-free",
        "minimax-m2.5-free",
        "ring-2.6-1t-free",
        "trinity-large-preview-free",
        "hy3-preview-free",
    ),
    "openrouter": (
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "inclusionai/ring-2.6-1t:free",
        "openai/gpt-oss-120b:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "qwen/qwen3-next-80b-a3b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "minimax/minimax-m2.5:free",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "google/gemma-4-31b-it:free",
        "openai/gpt-oss-20b:free",
        "z-ai/glm-4.5-air:free",
        "qwen/qwen3-coder:free",
        "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "google/gemma-4-26b-a4b-it:free",
        "poolside/laguna-m.1:free",
        "baidu/cobuddy:free",
        "nvidia/nemotron-nano-12b-v2-vl:free",
        "nvidia/nemotron-nano-9b-v2:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "poolside/laguna-xs.2:free",
        "baidu/qianfan-ocr-fast:free",
        "liquid/lfm-2.5-1.2b-thinking:free",
        "liquid/lfm-2.5-1.2b-instruct:free",
        "openrouter/owl-alpha",
        "openrouter/free",
    ),
    "github": (
        "openai/gpt-4.1-mini",
        "openai/gpt-4o-mini",
        "openai/gpt-4.1",
        "openai/gpt-4.1-nano",
        "meta/Llama-3.3-70B-Instruct",
    ),
    "cloudflare": (
        "@cf/openai/gpt-oss-120b",
        "@cf/openai/gpt-oss-20b",
        "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        "@cf/qwen/qwen3-32b",
    ),
    "cerebras": (
        "llama3.1-8b",
        "gpt-oss-120b",
        "gpt-oss-20b",
        "llama-4-scout-17b-16e-instruct",
    ),
    "google": (
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ),
    "mistral": (
        "mistral-small-latest",
        "mistral-medium-latest",
        "mistral-large-latest",
        "ministral-8b-latest",
        "open-mistral-nemo",
    ),
}


@dataclass(frozen=True, slots=True)
class AIModelAttempt:
    provider: str
    base_url: str
    key_name: str
    api_key: str = field(repr=False)
    model: str
    quality_rank: int
    latency: float = 9999.0
    quota_remaining: float = 0.0
    eligible: bool = True
    disabled_until: str = ""

    @property
    def key_suffix(self) -> str:
        return self.api_key[-6:] if self.api_key else ""

    @property
    def key_masked(self) -> str:
        return mask_key(self.api_key)

    def safe_tuple(self) -> tuple[str, str, str]:
        return self.provider, self.key_suffix, self.model


def configured_attempts(providers: str = "auto") -> tuple[AIModelAttempt, ...]:
    selected = _selected_providers(providers)
    attempts: list[AIModelAttempt] = []
    for provider in selected:
        attempts.extend(_provider_attempts(provider))
    return tuple(rank_attempts(attempts))


def rank_attempts(attempts) -> list[AIModelAttempt]:
    return sorted(attempts, key=_balanced_sort_key)


def _balanced_sort_key(attempt: AIModelAttempt):
    quota_sort = -attempt.quota_remaining if attempt.quota_remaining else 0
    return (
        not attempt.eligible,
        bool(attempt.disabled_until),
        attempt.quality_rank,
        quota_sort,
        attempt.latency,
        PROVIDER_ORDER.index(attempt.provider)
        if attempt.provider in PROVIDER_ORDER else len(PROVIDER_ORDER),
    )


def _selected_providers(value: str) -> tuple[str, ...]:
    if not value or value == "auto":
        return PROVIDER_ORDER
    requested = tuple(p.strip() for p in value.split(",") if p.strip())
    return tuple(p for p in requested if p in PROVIDERS and p != "rotation")


def _provider_attempts(provider: str) -> list[AIModelAttempt]:
    info = PROVIDERS.get(provider, {})
    keys = _provider_keys(provider, info)
    models = _provider_models(provider, info)
    attempts = []
    for key_name, key_value in keys:
        base_url = _provider_base_url(provider, info, key_name)
        if not base_url:
            continue
        for rank, model in enumerate(models, start=1):
            attempts.append(
                AIModelAttempt(
                    provider=provider,
                    base_url=base_url,
                    key_name=key_name,
                    api_key=key_value,
                    model=model,
                    quality_rank=rank,
                )
            )
    return attempts


def _cloudflare_account_ids(info: dict) -> dict[str, str]:
    account_id_envs = info.get("account_id_envs", ())
    return {
        key_env: os.getenv(account_env, "").strip()
        for key_env, account_env in zip(info.get("env_keys", ()), account_id_envs)
        if os.getenv(account_env, "").strip()
    }


def _provider_base_url(provider: str, info: dict, key_name: str) -> str:
    if provider == "cloudflare":
        account_id = _cloudflare_account_ids(info).get(key_name, "")
        if account_id:
            return cloudflare_base_url(account_id)
    return provider_base_url(info)


def _provider_keys(provider: str, info: dict) -> list[tuple[str, str]]:
    keys = []
    for env_name in info.get("env_keys", ()):
        value = os.getenv(env_name, "").strip()
        if value:
            keys.append((env_name, value))
    seen = set()
    out = []
    for item in keys:
        if item[1] not in seen:
            seen.add(item[1])
            out.append(item)
    return out


def _provider_models(provider: str, info: dict) -> list[str]:
    env_name = f"{provider.upper()}_MODELS"
    env_models = split_csv(os.getenv(env_name, ""))
    defaults = list(DEFAULT_MODELS.get(provider, ()))
    if not defaults and info.get("default_model"):
        defaults = [info["default_model"]]
    return dedupe(env_models + defaults)
