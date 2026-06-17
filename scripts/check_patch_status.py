#!/usr/bin/env python3
"""Patch and review-state gate for PoE2 Build Lab (doc 14 Content and Patch Ops).

Enforces that published build cards cannot silently appear current when:
- a material patch lists them in affects_builds but review_state is still current
- last_reviewed is outside the configured review window while review_state is current
- patch_version disagrees with the patch ledger without an explicit review flag

Usage:
    python3 scripts/check_patch_status.py          # human-readable report
    python3 scripts/check_patch_status.py --check  # CI gate (non-zero on violations)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDS_DIR = ROOT / "data" / "builds"
PATCH_NOTES_PATH = ROOT / "data" / "sources" / "patch-notes.json"
DEFAULT_REVIEW_WINDOW_DAYS = 45


def load_json(path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def load_builds():
    builds = []
    for path in sorted(BUILDS_DIR.glob("*.json")):
        if path.name == "schema.json":
            continue
        builds.append(load_json(path))
    return builds


def collect_violations():
    errors = []
    warnings = []

    if not PATCH_NOTES_PATH.exists():
        errors.append(f"patch ledger missing at {PATCH_NOTES_PATH}")
        return errors, warnings, None, []

    ledger = load_json(PATCH_NOTES_PATH)
    current_patch = ledger.get("current_patch", "")
    ledger_updated = parse_date(ledger.get("updated_at"))
    builds = load_builds()
    by_id = {b["id"]: b for b in builds if b.get("id")}

    for patch in ledger.get("patches", []):
        patch_ver = patch.get("patch_version", "")
        affects = patch.get("affects_builds", [])
        expected_state = patch.get("review_state_after", "needs_review")
        if not affects:
            continue
        for build_id in affects:
            build = by_id.get(build_id)
            if not build:
                errors.append(
                    f"patch {patch_ver!r} lists affects_builds {build_id!r} but no such build exists"
                )
                continue
            if build.get("status") != "published":
                continue
            if build.get("review_state") == "current" and expected_state != "current":
                errors.append(
                    f"{build_id}: listed in affects_builds for patch {patch_ver!r} "
                    f"but review_state is still 'current' (expected {expected_state!r})"
                )

    for build in builds:
        bid = build.get("id", "?")
        if build.get("status") != "published":
            continue

        state = build.get("review_state", "draft")
        reviewed = parse_date(build.get("last_reviewed"))
        patch_ver = build.get("patch_version", "")

        if patch_ver and current_patch and patch_ver != current_patch and state == "current":
            errors.append(
                f"{bid}: patch_version {patch_ver!r} != ledger current_patch "
                f"{current_patch!r} but review_state is still 'current'"
            )
        elif patch_ver and current_patch and patch_ver != current_patch:
            warnings.append(
                f"{bid}: patch_version {patch_ver!r} != ledger {current_patch!r} "
                f"(review_state={state!r})"
            )

        if state == "current" and reviewed:
            window = build.get("review_window_days", DEFAULT_REVIEW_WINDOW_DAYS)
            age = (date.today() - reviewed).days
            if age > window:
                errors.append(
                    f"{bid}: last_reviewed {build.get('last_reviewed')} is {age}d old "
                    f"(> {window}d window) but review_state is still 'current'"
                )

        if ledger_updated and reviewed and state == "current" and reviewed < ledger_updated:
            warnings.append(
                f"{bid}: last_reviewed {build.get('last_reviewed')} is before patch "
                f"ledger updated_at {ledger.get('updated_at')}"
            )

        if state in ("needs_review", "stale", "broken"):
            warnings.append(f"{bid}: published with review_state={state!r}")

    return errors, warnings, ledger, builds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="CI mode: exit non-zero when patch/review rules are violated.",
    )
    args = parser.parse_args()

    errors, warnings, ledger, builds = collect_violations()

    if ledger:
        print(
            f"Patch ledger: current_patch={ledger.get('current_patch')!r}, "
            f"updated_at={ledger.get('updated_at')}"
        )
    print(f"Scanning {len(builds)} build card(s)\n")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"FAIL  {e}")

    print()
    if errors:
        print(f"PATCH CHECK FAILED: {len(errors)} violation(s).")
        return 1 if args.check else 0
    print("PATCH CHECK OK: no enforceable patch/review SLA violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
