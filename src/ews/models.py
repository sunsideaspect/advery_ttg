from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AlertType(str, Enum):
    BLACK_HOLE = "black_hole"
    TRAFFIC_LOOP = "traffic_loop"
    FALSE_CAP = "false_cap"
    BEHAVIORAL_DROP = "behavioral_drop"
    OWNER_MISSING = "owner_missing"


class Severity(str, Enum):
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class HistoricalPoint:
    offer_id: str
    geo: str
    day_of_week: int
    slot_10m: int
    hits_10m: int
    clicks_10m: int


@dataclass(frozen=True)
class Profile:
    offer_id: str
    geo: str
    day_of_week: int
    slot_10m: int
    mean_clicks_10m: float
    mad_clicks_10m: float
    robust_lower_clicks_10m: float
    mean_hits_10m: float
    hit_to_click_ratio: float
    sample_size: int

    @property
    def key(self) -> str:
        return make_profile_key(self.offer_id, self.geo, self.day_of_week, self.slot_10m)


@dataclass(frozen=True)
class Snapshot:
    offer_id: str
    offer_name: str
    geo: str
    day_of_week: int
    slot_10m: int
    hits_10m: int
    clicks_10m: int
    cap_counter: int
    cap_limit: int
    declines_cap_reason_10m: int = 0

    @property
    def ratio(self) -> float:
        return self.clicks_10m / self.hits_10m if self.hits_10m > 0 else 0.0

    @property
    def cap_status(self) -> str:
        if self.cap_limit <= 0:
            return "UNKNOWN"
        used_pct = (self.cap_counter / self.cap_limit) * 100
        state = "FULL" if self.cap_counter >= self.cap_limit else "OPEN"
        return f"{state} ({used_pct:.1f}% used)"


@dataclass(frozen=True)
class Alert:
    alert_type: AlertType
    severity: Severity
    offer_id: str
    offer_name: str
    geo: str
    manager_email: str
    reason: str
    expected_clicks_10m: float
    actual_clicks_10m: int
    hits_10m: int
    cap_status: str

    @property
    def dedup_key(self) -> str:
        return f"{self.alert_type.value}:{self.offer_id}:{self.geo}"


def make_profile_key(offer_id: str, geo: str, day_of_week: int, slot_10m: int) -> str:
    return f"{offer_id}|{geo}|{day_of_week}|{slot_10m}"
