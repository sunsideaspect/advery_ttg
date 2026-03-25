"""Historical profile builder for offer traffic baselines."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Tuple

from .models import HistoricalPoint, Profile


def _median_abs_deviation(values: List[float]) -> float:
    if not values:
        return 0.0
    m = median(values)
    deviations = [abs(v - m) for v in values]
    return float(median(deviations))


def _group_key(point: HistoricalPoint) -> Tuple[str, str, int, int]:
    return (point.offer_id, point.geo, point.day_of_week, point.slot_10m)


def build_profiles(points: Iterable[HistoricalPoint]) -> Dict[str, Profile]:
    grouped: Dict[Tuple[str, str, int, int], List[HistoricalPoint]] = {}
    for point in points:
        grouped.setdefault(_group_key(point), []).append(point)

    profiles: Dict[str, Profile] = {}
    for key, values in grouped.items():
        offer_id, geo, day_of_week, slot_10m = key
        clicks = [v.clicks_10m for v in values]
        hits = [v.hits_10m for v in values]

        mean_clicks_10m = sum(clicks) / len(clicks)
        mean_hits_10m = sum(hits) / len(hits)
        mad_clicks_10m = _median_abs_deviation(clicks)
        robust_lower_clicks_10m = max(0.0, median(clicks) - 3.0 * mad_clicks_10m)
        hit_to_click_ratio = (
            0.0 if mean_hits_10m == 0 else min(1.0, mean_clicks_10m / mean_hits_10m)
        )

        profile = Profile(
            offer_id=offer_id,
            geo=geo,
            day_of_week=day_of_week,
            slot_10m=slot_10m,
            mean_clicks_10m=mean_clicks_10m,
            mad_clicks_10m=mad_clicks_10m,
            robust_lower_clicks_10m=robust_lower_clicks_10m,
            mean_hits_10m=mean_hits_10m,
            hit_to_click_ratio=hit_to_click_ratio,
            sample_size=len(values),
        )
        profiles[profile.key] = profile
    return profiles


def save_profiles(profiles: Dict[str, Profile], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = [asdict(profile) for profile in profiles.values()]
    path.write_text(json.dumps(content, indent=2), encoding="utf-8")


def load_profiles(path: Path) -> Dict[str, Profile]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    profiles: Dict[str, Profile] = {}
    for item in raw:
        profile = Profile(**item)
        profiles[profile.key] = profile
    return profiles
