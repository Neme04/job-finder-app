"""Loads the source registry and company seed list config."""

import json
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent
SOURCES_CONFIG_PATH = ENGINE_DIR / "sources.config.json"
SEEDS_PATH = ENGINE_DIR / "seeds" / "companies.json"


def load_sources_config(path: Path = SOURCES_CONFIG_PATH) -> dict:
    with open(path) as f:
        return json.load(f)


def load_company_seeds(path: Path = SEEDS_PATH) -> dict:
    with open(path) as f:
        return json.load(f)


def enabled_ats_sources(config: dict) -> list[dict]:
    return [s for s in config.get("ats_sources", []) if s.get("enabled")]


def enabled_feed_sources(config: dict) -> list[dict]:
    return [s for s in config.get("feed_sources", []) if s.get("enabled")]
