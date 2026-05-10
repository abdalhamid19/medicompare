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

PROVIDERS = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "env_key": "OPENROUTER_API_KEY",
        "env_keys": ["OPENROUTER_API_KEY"],
        "default_model": "openai/gpt-4o-mini",
    },
    "opencode": {
        "base_url": "https://opencode.ai/zen/v1",
        "env_key": "OPENCODE_API_KEY",
        "env_keys": ["OPENCODE_API_KEY_1", "OPENCODE_API_KEY_2", "OPENCODE_API_KEY"],
        "default_model": "big-pickle",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "env_key": "GROQ_API_KEY",
        "env_keys": ["GROQ_API_KEY_1", "GROQ_API_KEY"],
        "default_model": "openai/gpt-oss-120b",
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
        url = p["base_url"]
        mdl = model or os.getenv("AI_MODEL", "") or p["default_model"]
        return {"api_key": key, "api_keys": unique_keys, "base_url": url, "model": mdl, "fallback_models": fallback_models}
    # No provider: use env vars or .env
    key = api_key or os.getenv("OPENROUTER_API_KEY", "")
    url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    mdl = model or os.getenv("AI_MODEL", "openai/gpt-4o-mini")
    all_keys = tuple(
        k for k in (
            api_key,
            os.getenv("OPENCODE_API_KEY_1", ""),
            os.getenv("OPENCODE_API_KEY_2", ""),
            os.getenv("OPENCODE_API_KEY", ""),
            os.getenv("GROQ_API_KEY_1", ""),
            os.getenv("GROQ_API_KEY", ""),
            os.getenv("OPENROUTER_API_KEY", ""),
            os.getenv("CUSTOM_API_KEY", ""),
        ) if k
    )
    seen = set()
    unique_keys = tuple(k for k in all_keys if k not in seen and not seen.add(k))
    return {"api_key": key, "api_keys": unique_keys, "base_url": url, "model": mdl, "fallback_models": fallback_models}


@dataclass(frozen=True)
class APIConfig:
    api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    api_keys: tuple = field(default_factory=lambda: tuple(
        k for k in (
            os.getenv("OPENCODE_API_KEY_1", ""),
            os.getenv("OPENCODE_API_KEY_2", ""),
            os.getenv("OPENCODE_API_KEY", ""),
            os.getenv("GROQ_API_KEY_1", ""),
            os.getenv("GROQ_API_KEY", ""),
            os.getenv("OPENROUTER_API_KEY", ""),
            os.getenv("CUSTOM_API_KEY", ""),
        ) if k
    ))
    base_url: str = field(default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))
    model: str = field(default_factory=lambda: os.getenv("AI_MODEL", "openai/gpt-4o-mini"))
    fallback_models: tuple = field(default_factory=lambda: tuple(
        m.strip() for m in os.getenv("FALLBACK_MODELS", "").split(",") if m.strip()
    ))
    review_model: str = field(default_factory=lambda: os.getenv("REVIEW_MODEL", ""))
    healthy_combos: tuple = ()
    attempt_plan: tuple = ()
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
