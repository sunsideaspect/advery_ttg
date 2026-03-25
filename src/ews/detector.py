"""Anomaly detection rules for EWS MVP."""

from __future__ import annotations

from typing import Dict, Iterable, List

from .models import Alert, AlertType, Profile, Severity, Snapshot, make_profile_key


class Detector:
    def __init__(
        self,
        manager_mapping: Dict[str, str],
        min_hits_for_black_hole: int = 50,
        loop_hits_multiplier: float = 2.0,
        loop_ratio_multiplier: float = 0.1,
        false_cap_declines_threshold: int = 100,
    ) -> None:
        self.manager_mapping = manager_mapping
        self.min_hits_for_black_hole = min_hits_for_black_hole
        self.loop_hits_multiplier = loop_hits_multiplier
        self.loop_ratio_multiplier = loop_ratio_multiplier
        self.false_cap_declines_threshold = false_cap_declines_threshold

    def detect(self, snapshots: Iterable[Snapshot], profiles: Dict[str, Profile]) -> List[Alert]:
        alerts: List[Alert] = []
        for s in snapshots:
            alert = self._detect_one(s, profiles)
            if alert is not None:
                alerts.append(alert)
        return alerts

    def _detect_one(self, s: Snapshot, profiles: Dict[str, Profile]) -> Alert | None:
        # Context filters
        if s.cap_limit > 0 and s.cap_counter >= s.cap_limit:
            return None
        if s.hits_10m == 0:
            return None

        manager_email = self.manager_mapping.get(s.offer_id, "unassigned@local")
        key = make_profile_key(s.offer_id, s.geo, s.day_of_week, s.slot_10m)
        profile = profiles.get(key)
        has_offer_profile = any(
            p.offer_id == s.offer_id and p.geo == s.geo for p in profiles.values()
        )

        # New offer guardrail
        if not has_offer_profile:
            if s.hits_10m >= self.min_hits_for_black_hole and s.clicks_10m == 0:
                return self._mk_alert(
                    s=s,
                    manager_email=manager_email,
                    alert_type=AlertType.BLACK_HOLE,
                    severity=Severity.CRITICAL,
                    reason="New-offer guardrail: hits present, clicks zero, cap open.",
                    expected_clicks_10m=0.0,
                )
            return None

        if profile is None:
            return None

        # Rule #1: Black hole
        if s.hits_10m >= self.min_hits_for_black_hole and s.clicks_10m == 0:
            return self._mk_alert(
                s=s,
                manager_email=manager_email,
                alert_type=AlertType.BLACK_HOLE,
                severity=Severity.CRITICAL,
                reason="Traffic input exists but clicks are zero while cap is open.",
                expected_clicks_10m=profile.mean_clicks_10m,
            )

        # Rule #2: Traffic loop
        if (
            s.hits_10m > profile.mean_hits_10m * self.loop_hits_multiplier
            and s.ratio < profile.hit_to_click_ratio * self.loop_ratio_multiplier
        ):
            return self._mk_alert(
                s=s,
                manager_email=manager_email,
                alert_type=AlertType.TRAFFIC_LOOP,
                severity=Severity.HIGH,
                reason="Hits spiked while hit-to-click ratio collapsed.",
                expected_clicks_10m=profile.mean_clicks_10m,
            )

        # Rule #3: False cap sync issue
        if (
            s.declines_cap_reason_10m > self.false_cap_declines_threshold
            and s.cap_counter < s.cap_limit
        ):
            return self._mk_alert(
                s=s,
                manager_email=manager_email,
                alert_type=AlertType.FALSE_CAP,
                severity=Severity.HIGH,
                reason="Cap declines high but cap counter shows offer is still open.",
                expected_clicks_10m=profile.mean_clicks_10m,
            )

        # Rule #4: Behavioral drop (robust threshold)
        if s.clicks_10m < profile.robust_lower_clicks_10m:
            return self._mk_alert(
                s=s,
                manager_email=manager_email,
                alert_type=AlertType.BEHAVIORAL_DROP,
                severity=Severity.WARNING,
                reason=(
                    f"Clicks below robust baseline: actual={s.clicks_10m}, "
                    f"threshold={profile.robust_lower_clicks_10m:.2f}."
                ),
                expected_clicks_10m=profile.mean_clicks_10m,
            )

        return None

    def _mk_alert(
        self,
        s: Snapshot,
        manager_email: str,
        alert_type: AlertType,
        severity: Severity,
        reason: str,
        expected_clicks_10m: float,
    ) -> Alert:
        return Alert(
            alert_type=alert_type,
            severity=severity,
            offer_id=s.offer_id,
            offer_name=s.offer_name,
            geo=s.geo,
            manager_email=manager_email,
            reason=reason,
            expected_clicks_10m=expected_clicks_10m,
            actual_clicks_10m=s.clicks_10m,
            hits_10m=s.hits_10m,
            cap_status=s.cap_status,
        )
