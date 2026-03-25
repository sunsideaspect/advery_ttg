from __future__ import annotations

import json
from pathlib import Path


DEFAULT_MANAGER_MAPPING: dict[str, str] = {
    "offer_activechannel": "ivan.ivanov@example.com",
    "offer_other": "anna.petrova@example.com",
}

PROFILES_PATH = Path("data/profiles.json")


def load_manager_mapping(path: Path | None) -> dict[str, str]:
    if path is None:
        return DEFAULT_MANAGER_MAPPING
    if not path.exists():
        raise FileNotFoundError(f"Manager mapping file not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Manager mapping JSON must be an object: {offer_id: email}")
    return {str(k): str(v) for k, v in raw.items()}
