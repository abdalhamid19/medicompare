"""Configuration - single source of truth for all settings."""
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("medicompare")


def setup_logging(level: str = "INFO"):
    """Configure logging for the medicompare package."""
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%H:%M:%S"
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format=fmt, datefmt=datefmt)

BASE_DIR = Path(__file__).resolve().parent.parent


def numbered_env_keys(prefix: str, count: int = 6, include_legacy: bool = True) -> list[str]:
    keys = [f"{prefix}_{idx}" for idx in range(1, count + 1)]
    if include_legacy:
        keys.append(prefix)
    return keys


def configured_env_key_names() -> list[str]:
    keys: list[str] = []
    for info in PROVIDERS.values():
        keys.extend(info.get("env_keys", ()))
    return keys


def configured_env_key_values() -> tuple[str, ...]:
    return tuple(os.getenv(name, "") for name in configured_env_key_names())


def provider_base_url(info: dict) -> str:
    account_id = os.getenv(info.get("account_id_env", ""), "").strip()
    if account_id:
        return cloudflare_base_url(account_id)
    url = os.getenv(info.get("base_url_env", ""), "").strip() or info["base_url"]
    return "" if "<" in url or ">" in url else url


def cloudflare_base_url(account_id: str) -> str:
    account_id = account_id.strip()
    if not account_id:
        return ""
    return f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1"


@dataclass(frozen=True)
class MatchingConfig:
    fuzzy_threshold: int = 80
    brand_prefix_min: int = 4
    brand_prefix_ratio: float = 0.75
    ai_verify_threshold: float = 90.0  # verify matches below this score
    ai_batch_size: int = 20
    ai_max_concurrent: int = 5
    top_k_candidates: int = 10
    ai_review_threshold: float = 0.8  # review AI decisions with confidence below this
    ai_search_limit: int | None = None
    ai_verify_policy: str = "score"
    ai_verify_limit: int | None = None
    ai_search_policy: str = "safe"
    ai_search_min_candidate_score: float = 80.0
    ai_search_accept_confidence: float = 0.75
    ai_search_candidate_limit: int = 5

PROVIDERS = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "env_key": "OPENROUTER_API_KEY",
        "env_keys": numbered_env_keys("OPENROUTER_API_KEY"),
        "default_model": "openai/gpt-4o-mini",
    },
    "opencode": {
        "base_url": "https://opencode.ai/zen/v1",
        "env_key": "OPENCODE_API_KEY",
        "env_keys": numbered_env_keys("OPENCODE_API_KEY"),
        "default_model": "big-pickle",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "env_key": "GROQ_API_KEY",
        "env_keys": numbered_env_keys("GROQ_API_KEY"),
        "default_model": "openai/gpt-oss-120b",
    },
    "github": {
        "base_url": "https://models.github.ai/inference",
        "env_key": "GITHUB_API_KEY",
        "env_keys": numbered_env_keys("GITHUB_API_KEY"),
        "default_model": "openai/gpt-4.1-mini",
    },
    "cloudflare": {
        "base_url": "",
        "base_url_env": "CLOUDFLARE_BASE_URL",
        "account_id_env": "CLOUDFLARE_ACCOUNT_ID",
        "account_id_envs": numbered_env_keys("CLOUDFLARE_ACCOUNT_ID", include_legacy=False),
        "env_key": "CLOUDFLARE_API_TOKEN",
        "env_keys": numbered_env_keys("CLOUDFLARE_API_TOKEN"),
        "default_model": "@cf/openai/gpt-oss-120b",
    },
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "env_key": "CEREBRAS_API_KEY",
        "env_keys": numbered_env_keys("CEREBRAS_API_KEY"),
        "default_model": "gpt-oss-120b",
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "env_key": "GOOGLE_API_KEY",
        "env_keys": numbered_env_keys("GOOGLE_API_KEY", count=4),
        "default_model": "gemini-2.5-flash",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "env_key": "MISTRAL_API_KEY",
        "env_keys": numbered_env_keys("MISTRAL_API_KEY"),
        "default_model": "mistral-small-latest",
    },
    "rotation": {
        "base_url": "",
        "env_key": "",
        "env_keys": [],
        "default_model": "",
    },
    "custom": {
        "base_url": "",
        "env_key": "CUSTOM_API_KEY",
        "env_keys": ["CUSTOM_API_KEY"],
        "default_model": "",
    },
}

def resolve_api_config(provider: str = "", model: str = "", api_key: str = "") -> dict:
    """Resolve API config from provider name, falling back to env vars.
    Returns dict with api_key, api_keys, base_url, model, fallback_models."""
    fallback_models = tuple(
        m.strip() for m in os.getenv("FALLBACK_MODELS", "").split(",") if m.strip()
    )
    # If provider specified, use its defaults
    if provider and provider in PROVIDERS:
        p = PROVIDERS[provider]
        key = api_key or os.getenv(p["env_key"], "")
        # Collect all keys for this provider
        all_keys = tuple(
            k for k in (
                api_key,
                *(os.getenv(ek, "") for ek in p.get("env_keys", [p["env_key"]])),
            ) if k
        )
        # Deduplicate while preserving order
        seen = set()
        unique_keys = tuple(k for k in all_keys if k not in seen and not seen.add(k))
        url = provider_base_url(p)
        mdl = model or os.getenv("AI_MODEL", "") or p["default_model"]
        return {"api_key": key, "api_keys": unique_keys, "base_url": url, "model": mdl, "fallback_models": fallback_models}
    # No provider: use env vars or .env
    key = api_key or os.getenv("OPENROUTER_API_KEY", "")
    url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    mdl = model or os.getenv("AI_MODEL", "openai/gpt-4o-mini")
    all_keys = tuple(k for k in (api_key, *configured_env_key_values()) if k)
    seen = set()
    unique_keys = tuple(k for k in all_keys if k not in seen and not seen.add(k))
    return {"api_key": key, "api_keys": unique_keys, "base_url": url, "model": mdl, "fallback_models": fallback_models}


@dataclass(frozen=True)
class APIConfig:
    api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    api_keys: tuple = field(default_factory=lambda: tuple(
        k for k in configured_env_key_values() if k
    ))
    base_url: str = field(default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))
    model: str = field(default_factory=lambda: os.getenv("AI_MODEL", "openai/gpt-4o-mini"))
    fallback_models: tuple = field(default_factory=lambda: tuple(
        m.strip() for m in os.getenv("FALLBACK_MODELS", "").split(",") if m.strip()
    ))
    review_model: str = field(default_factory=lambda: os.getenv("REVIEW_MODEL", ""))
    healthy_combos: tuple = ()
    attempt_plan: tuple = ()
    review_attempt_plan: tuple = ()
    max_tokens: int = 1024
    temperature: float = 0.1

@dataclass(frozen=True)
class Paths:
    drugs_csv: Path = field(default_factory=lambda: BASE_DIR / "input" / "all_non_cosmotics_drug_all.csv")
    tawreed_csv: Path = field(default_factory=lambda: BASE_DIR / "input" / "tawreed_products.csv")
    output_csv: Path = field(default_factory=lambda: BASE_DIR / "output" / f"matched_drugs_verified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    env_file: Path = field(default_factory=lambda: BASE_DIR / ".env")

def load_env(path: Path | None = None):
    path = path or Paths().env_file
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")
