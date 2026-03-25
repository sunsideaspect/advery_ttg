from __future__ import annotations

import argparse

from .config import DEFAULT_MANAGER_MAPPING, PROFILES_PATH
from .detector import Detector
from .mock_data import historical_points, scenario_snapshot
from .profiler import build_profiles, save_profiles
from .teams_connector import build_power_automate_payload


def run_once(scenario: str) -> None:
    points = historical_points()
    profiles = build_profiles(points)
    save_profiles(profiles, PROFILES_PATH)

    detector = Detector(manager_mapping=DEFAULT_MANAGER_MAPPING)
    snapshots = scenario_snapshot(scenario)
    alerts = detector.detect(snapshots, profiles)

    if not alerts:
        print("No anomalies detected.")
        return

    for alert in alerts:
        print(
            f"[{alert.severity.value}] {alert.alert_type.value} "
            f"{alert.offer_id}/{alert.geo} "
            f"exp={alert.expected_clicks_10m:.1f} "
            f"act={alert.actual_clicks_10m} hits={alert.hits_10m} "
            f"cap={alert.cap_status}"
        )
        print("Reason:", alert.reason)
        print("Power Automate payload:", build_power_automate_payload(alert))
        print("-" * 80)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run EWS MVP scenarios.")
    parser.add_argument(
        "--scenario",
        choices=["healthy", "black_hole", "loop", "false_cap", "drop", "new_offer_black_hole"],
        default="healthy",
        help="Scenario to simulate.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_once(args.scenario)


if __name__ == "__main__":
    main()
