"""Configuration - single source of truth for all settings."""
import logging
import os
from dataclasses import dataclass, field
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

@dataclass(frozen=True)
class APIConfig:
    api_key: str = field(default_factory=lambda: os.getenv("AGENT_ROUTER_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.getenv("AGENT_ROUTER_BASE_URL", "https://openrouter.ai/api/v1"))
    model: str = field(default_factory=lambda: os.getenv("AGENT_ROUTER_MODEL", "glm-5.1"))
    max_tokens: int = 1024
    temperature: float = 0.1

@dataclass(frozen=True)
class Paths:
    drugs_csv: Path = field(default_factory=lambda: BASE_DIR / "input" / "all_non_cosmotics_drug_all.csv")
    tawreed_csv: Path = field(default_factory=lambda: BASE_DIR / "input" / "tawreed_products.csv")
    output_csv: Path = field(default_factory=lambda: BASE_DIR / "output" / "matched_drugs_verified.csv")
    env_file: Path = field(default_factory=lambda: BASE_DIR / ".env")

def load_env(path: Path | None = None):
    path = path or Paths().env_file
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
