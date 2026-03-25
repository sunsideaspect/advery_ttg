"""Load history/snapshot data from CSV or JSON files.

This loader is tolerant to schema differences:
- supports multiple aliases for common fields (offer_id, geo, timestamp, etc.)
- can derive `day_of_week` and `slot_10m` from timestamp if those fields are absent
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import HistoricalPoint, Snapshot


FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "offer_id": ("offerId", "offerID", "offer", "offerid", "offer_name_id"),
    "offer_name": ("offerName", "name", "offer_title", "offerTitle"),
    "geo": ("country", "country_code", "geo_code", "geoCode"),
    "day_of_week": ("dow", "weekday", "dayofweek"),
    "slot_10m": ("slot", "time_slot_10m", "timeslot_10m"),
    "hits_10m": ("hits", "requests", "hit_count", "requests_10m"),
    "clicks_10m": ("clicks", "click_count", "accepted_clicks", "clicks_count"),
    "cap_counter": ("cap_used", "capUsed", "cap_count", "counter"),
    "cap_limit": ("cap", "cap_limit_daily", "capLimit", "limit"),
    "declines_cap_reason_10m": (
        "declines_cap_reason",
        "cap_declines",
        "declined_by_cap",
        "declines",
    ),
    "timestamp": ("ts", "event_time", "created_at", "datetime", "time", "date_time"),
}


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


def _find_value(row: dict, canonical_name: str, *, required: bool = True) -> object:
    candidates = (canonical_name, *FIELD_ALIASES.get(canonical_name, ()))
    for candidate in candidates:
        if candidate in row and row[candidate] not in (None, ""):
            return row[candidate]
    if required:
        raise KeyError(
            f"Missing required field '{canonical_name}'. "
            f"Tried aliases: {', '.join(candidates)}"
        )
    return None


def _parse_timestamp(value: object) -> datetime:
    if isinstance(value, (int, float)):
        # Assume UNIX timestamp in seconds.
        return datetime.fromtimestamp(float(value))

    text = str(value).strip()
    if not text:
        raise ValueError("Empty timestamp value.")

    if text.isdigit():
        return datetime.fromtimestamp(int(text))

    normalized = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        pass

    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
    )
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unsupported timestamp format: {value!r}")


def _resolve_day_slot(row: dict) -> tuple[int, int]:
    day_value = _find_value(row, "day_of_week", required=False)
    slot_value = _find_value(row, "slot_10m", required=False)
    if day_value is not None and slot_value is not None:
        return _to_int(day_value, "day_of_week"), _to_int(slot_value, "slot_10m")

    ts_value = _find_value(row, "timestamp", required=True)
    dt = _parse_timestamp(ts_value)
    return dt.weekday(), dt.hour * 6 + dt.minute // 10


def load_historical_points(path: Path) -> list[HistoricalPoint]:
    """Load historical points from CSV/JSON.

    Canonical fields:
    - offer_id, geo, day_of_week, slot_10m, hits_10m, clicks_10m

    Notes:
    - day_of_week + slot_10m can be omitted if timestamp-like field exists.
    - many common aliases are supported.
    """
    rows = _load_rows(path)
    points: list[HistoricalPoint] = []
    for row in rows:
        day_of_week, slot_10m = _resolve_day_slot(row)
        points.append(
            HistoricalPoint(
                offer_id=str(_find_value(row, "offer_id")),
                geo=str(_find_value(row, "geo")),
                day_of_week=day_of_week,
                slot_10m=slot_10m,
                hits_10m=_to_int(_find_value(row, "hits_10m"), "hits_10m"),
                clicks_10m=_to_int(_find_value(row, "clicks_10m"), "clicks_10m"),
            )
        )
    return points


def load_snapshots(path: Path) -> list[Snapshot]:
    """Load current snapshots from CSV/JSON.

    Canonical fields:
    - offer_id, offer_name, geo, day_of_week, slot_10m, hits_10m, clicks_10m,
      cap_counter, cap_limit
    Optional:
    - declines_cap_reason_10m (default 0)

    Notes:
    - day_of_week + slot_10m can be omitted if timestamp-like field exists.
    - many common aliases are supported.
    """
    rows = _load_rows(path)
    snapshots: list[Snapshot] = []
    for row in rows:
        day_of_week, slot_10m = _resolve_day_slot(row)
        snapshots.append(
            Snapshot(
                offer_id=str(_find_value(row, "offer_id")),
                offer_name=str(_find_value(row, "offer_name")),
                geo=str(_find_value(row, "geo")),
                day_of_week=day_of_week,
                slot_10m=slot_10m,
                hits_10m=_to_int(_find_value(row, "hits_10m"), "hits_10m"),
                clicks_10m=_to_int(_find_value(row, "clicks_10m"), "clicks_10m"),
                cap_counter=_to_int(_find_value(row, "cap_counter"), "cap_counter"),
                cap_limit=_to_int(_find_value(row, "cap_limit"), "cap_limit"),
                declines_cap_reason_10m=_to_int(
                    _find_value(row, "declines_cap_reason_10m", required=False) or 0,
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
