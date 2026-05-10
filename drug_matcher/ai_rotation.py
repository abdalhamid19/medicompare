"""Provider/model rotation planning for AI calls."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from .ai_health import dedupe, mask_key, split_csv
from .config import PROVIDERS

PROVIDER_ORDER = ("groq", "opencode", "openrouter", "agentrouter")

DEFAULT_MODELS = {
    "groq": (
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "qwen/qwen3-32b",
        "llama-3.1-8b-instant",
    ),
    "opencode": (
        "nemotron-3-super-free",
        "minimax-m2.5-free",
        "big-pickle",
        "trinity-large-preview-free",
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
    base_url = info.get("base_url", "")
    if not base_url:
        return []
    keys = _provider_keys(provider, info)
    models = _provider_models(provider, info)
    attempts = []
    for key_name, key_value in keys:
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
