from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import DEFAULT_MANAGER_MAPPING, PROFILES_PATH, load_manager_mapping
from .data_io import iter_missing_manager_emails, load_historical_points, load_snapshots
from .detector import Detector
from .mock_data import historical_points, scenario_snapshot
from .profiler import build_profiles, save_profiles
from .teams_connector import build_power_automate_payload


def _render_alert(alert: object) -> None:
    # object type used only to keep function local and simple for CLI output.
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


def run_demo(scenario: str) -> None:
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
        _render_alert(alert)


def run_with_files(history_file: Path, snapshot_file: Path, manager_mapping_file: Path | None) -> None:
    points = load_historical_points(history_file)
    profiles = build_profiles(points)
    save_profiles(profiles, PROFILES_PATH)

    manager_mapping = load_manager_mapping(manager_mapping_file) if manager_mapping_file else {}
    if not manager_mapping:
        manager_mapping = DEFAULT_MANAGER_MAPPING

    snapshots = load_snapshots(snapshot_file)
    missing_manager_offers = iter_missing_manager_emails(snapshots, manager_mapping)
    if missing_manager_offers:
        print("Warning: missing manager mapping for offers:", ", ".join(missing_manager_offers))

    detector = Detector(manager_mapping=manager_mapping)
    alerts = detector.detect(snapshots, profiles)

    print(
        json.dumps(
            {
                "history_rows": len(points),
                "snapshot_rows": len(snapshots),
                "alerts_count": len(alerts),
            }
        )
    )

    if not alerts:
        print("No anomalies detected.")
        return

    for alert in alerts:
        _render_alert(alert)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run EWS MVP scenarios or file-based checks.")
    parser.add_argument(
        "--mode",
        choices=["demo", "files"],
        default="demo",
        help="Run with built-in demo data or with external files.",
    )
    parser.add_argument(
        "--scenario",
        choices=["healthy", "black_hole", "loop", "false_cap", "drop", "new_offer_black_hole"],
        default="healthy",
        help="Scenario to simulate when --mode demo.",
    )
    parser.add_argument(
        "--history-file",
        type=Path,
        help="Path to historical CSV/JSON (required for --mode files).",
    )
    parser.add_argument(
        "--snapshot-file",
        type=Path,
        help="Path to current snapshot CSV/JSON (required for --mode files).",
    )
    parser.add_argument(
        "--manager-mapping-file",
        type=Path,
        help="Optional path to manager mapping JSON {offer_id: email}.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.mode == "demo":
        run_demo(args.scenario)
        return

    if not args.history_file or not args.snapshot_file:
        parser.error("--history-file and --snapshot-file are required when --mode files.")

    run_with_files(args.history_file, args.snapshot_file, args.manager_mapping_file)


if __name__ == "__main__":
    main()
