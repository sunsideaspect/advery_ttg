from __future__ import annotations

from typing import Dict, List

from .models import HistoricalPoint, Snapshot


def historical_points() -> List[HistoricalPoint]:
    rows: List[HistoricalPoint] = []
    # Tuesday, slot 84 (14:00-14:10) stable profile
    for clicks in [26, 25, 27, 24, 26, 25, 27, 26]:
        rows.append(
            HistoricalPoint(
                offer_id="offer_activechannel",
                geo="US",
                day_of_week=1,
                slot_10m=84,
                hits_10m=clicks + 6,
                clicks_10m=clicks,
            )
        )

    for clicks in [14, 16, 15, 13, 17, 16, 15, 14]:
        rows.append(
            HistoricalPoint(
                offer_id="offer_other",
                geo="US",
                day_of_week=1,
                slot_10m=84,
                hits_10m=clicks + 5,
                clicks_10m=clicks,
            )
        )
    return rows


def manager_mapping() -> Dict[str, str]:
    return {
        "offer_activechannel": "ivan.ivanov@example.com",
        "offer_other": "anna.petrova@example.com",
    }


def scenario_snapshot(name: str) -> List[Snapshot]:
    base = Snapshot(
        offer_id="offer_activechannel",
        offer_name="ActiveChannel_CPC_Mob",
        geo="US",
        day_of_week=1,
        slot_10m=84,
        hits_10m=32,
        clicks_10m=26,
        cap_counter=100,
        cap_limit=1000,
        declines_cap_reason_10m=0,
    )

    if name == "healthy":
        return [base]
    if name == "black_hole":
        return [Snapshot(**{**base.__dict__, "hits_10m": 60, "clicks_10m": 0})]
    if name == "loop":
        return [Snapshot(**{**base.__dict__, "hits_10m": 80, "clicks_10m": 2})]
    if name == "false_cap":
        return [
            Snapshot(
                **{
                    **base.__dict__,
                    "clicks_10m": 8,
                    "declines_cap_reason_10m": 180,
                    "cap_counter": 220,
                    "cap_limit": 1000,
                }
            )
        ]
    if name == "drop":
        return [Snapshot(**{**base.__dict__, "hits_10m": 28, "clicks_10m": 4})]
    if name == "new_offer_black_hole":
        return [
            Snapshot(
                offer_id="offer_new",
                offer_name="NewOffer_CPC",
                geo="US",
                day_of_week=1,
                slot_10m=84,
                hits_10m=70,
                clicks_10m=0,
                cap_counter=0,
                cap_limit=500,
                declines_cap_reason_10m=0,
            )
        ]

    raise ValueError(f"Unknown scenario: {name}")
