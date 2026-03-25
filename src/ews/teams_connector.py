"""Power Automate payload formatter."""

from __future__ import annotations

from .models import Alert


def build_power_automate_payload(alert: Alert) -> dict:
    return {
        "alert_type": alert.alert_type.value,
        "severity": alert.severity.value,
        "offer_id": alert.offer_id,
        "offer_name": alert.offer_name,
        "geo": alert.geo,
        "manager_email": alert.manager_email,
        "reason": alert.reason,
        "stats": {
            "expected_clicks_10m": round(alert.expected_clicks_10m, 2),
            "actual_clicks_10m": alert.actual_clicks_10m,
            "hits_10m": alert.hits_10m,
            "cap_status": alert.cap_status,
        },
        "dedup_key": alert.dedup_key,
    }
