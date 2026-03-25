from __future__ import annotations

from pathlib import Path


DEFAULT_MANAGER_MAPPING: dict[str, str] = {
    "offer_activechannel": "ivan.ivanov@example.com",
    "offer_other": "anna.petrova@example.com",
}

PROFILES_PATH = Path("data/profiles.json")
