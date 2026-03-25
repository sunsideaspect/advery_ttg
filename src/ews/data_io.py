"""Load history/snapshot data from CSV or JSON files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from .models import HistoricalPoint, Snapshot


def _load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]

    if path.suffix.lower() == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("JSON input must be an array of objects.")
        if not all(isinstance(item, dict) for item in raw):
            raise ValueError("Each JSON array item must be an object.")
        return raw

    raise ValueError(f"Unsupported file type: {path.suffix}. Use CSV or JSON.")


def _to_int(value: object, field_name: str) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Invalid integer in field '{field_name}': {value!r}") from exc


def load_historical_points(path: Path) -> list[HistoricalPoint]:
    """Load historical points from CSV/JSON.

    Required fields:
    - offer_id, geo, day_of_week, slot_10m, hits_10m, clicks_10m
    """
    rows = _load_rows(path)
    points: list[HistoricalPoint] = []
    for row in rows:
        points.append(
            HistoricalPoint(
                offer_id=str(row["offer_id"]),
                geo=str(row["geo"]),
                day_of_week=_to_int(row["day_of_week"], "day_of_week"),
                slot_10m=_to_int(row["slot_10m"], "slot_10m"),
                hits_10m=_to_int(row["hits_10m"], "hits_10m"),
                clicks_10m=_to_int(row["clicks_10m"], "clicks_10m"),
            )
        )
    return points


def load_snapshots(path: Path) -> list[Snapshot]:
    """Load current snapshots from CSV/JSON.

    Required fields:
    - offer_id, offer_name, geo, day_of_week, slot_10m, hits_10m, clicks_10m,
      cap_counter, cap_limit
    Optional:
    - declines_cap_reason_10m (default 0)
    """
    rows = _load_rows(path)
    snapshots: list[Snapshot] = []
    for row in rows:
        snapshots.append(
            Snapshot(
                offer_id=str(row["offer_id"]),
                offer_name=str(row["offer_name"]),
                geo=str(row["geo"]),
                day_of_week=_to_int(row["day_of_week"], "day_of_week"),
                slot_10m=_to_int(row["slot_10m"], "slot_10m"),
                hits_10m=_to_int(row["hits_10m"], "hits_10m"),
                clicks_10m=_to_int(row["clicks_10m"], "clicks_10m"),
                cap_counter=_to_int(row["cap_counter"], "cap_counter"),
                cap_limit=_to_int(row["cap_limit"], "cap_limit"),
                declines_cap_reason_10m=_to_int(
                    row.get("declines_cap_reason_10m", 0),
                    "declines_cap_reason_10m",
                ),
            )
        )
    return snapshots


def iter_missing_manager_emails(
    snapshots: Iterable[Snapshot], manager_mapping: dict[str, str]
) -> list[str]:
    """Return offer IDs that have no manager mapping."""
    missing: set[str] = set()
    for snapshot in snapshots:
        if snapshot.offer_id not in manager_mapping:
            missing.add(snapshot.offer_id)
    return sorted(missing)
