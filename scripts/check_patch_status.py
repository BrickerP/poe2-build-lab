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
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
BUILDS_DIR = ROOT / "data" / "builds"
PATCH_NOTES_PATH = ROOT / "data" / "sources" / "patch-notes.json"
OFFICIAL_LINKS_PATH = ROOT / "data" / "sources" / "official-links.json"
DEFAULT_REVIEW_WINDOW_DAYS = 45
REVIEW_STATES = {"current", "needs_review", "needs_testing", "stale", "broken", "draft"}


def load_json(path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def load_builds(builds_dir=BUILDS_DIR):
    builds = []
    for path in sorted(builds_dir.glob("*.json")):
        if path.name == "schema.json":
            continue
        builds.append(load_json(path))
    return builds


def collect_violations(
    patch_notes_path=PATCH_NOTES_PATH,
    builds_dir=BUILDS_DIR,
    official_links_path=OFFICIAL_LINKS_PATH,
):
    errors = []
    warnings = []

    if not patch_notes_path.exists():
        errors.append(f"patch ledger missing at {patch_notes_path}")
        return errors, warnings, None, []

    ledger = load_json(patch_notes_path)
    current_patch = ledger.get("current_patch", "")
    ledger_updated = parse_date(ledger.get("updated_at"))
    builds = load_builds(builds_dir)
    by_id = {b["id"]: b for b in builds if b.get("id")}
    if official_links_path.exists():
        official_links = load_json(official_links_path)
        for duplicated_key in ("patch_version", "current_patch", "updated_at"):
            if duplicated_key in official_links:
                errors.append(
                    f"official-links.json duplicates patch ledger field {duplicated_key!r}"
                )
    if not current_patch:
        errors.append("patch ledger current_patch must be a non-empty string")
    if not ledger_updated:
        errors.append("patch ledger updated_at must be an ISO date")

    patches = ledger.get("patches", [])
    if not isinstance(patches, list):
        errors.append("patch ledger patches must be a list")
        patches = []

    latest_relevant = {}
    seen_versions = set()
    valid_patch_dates = []
    for sequence, patch in enumerate(patches):
        if not isinstance(patch, dict):
            errors.append(f"patch entry {sequence} must be an object")
            continue
        patch_ver = patch.get("patch_version", "")
        affects = patch.get("affects_builds", [])
        patch_date = parse_date(patch.get("date"))
        source_url = patch.get("source_url", "")
        expected_state = patch.get("review_state_after")
        if not patch_ver:
            errors.append(f"patch entry {sequence} has no patch_version")
        elif patch_ver in seen_versions:
            errors.append(f"patch ledger has duplicate patch_version {patch_ver!r}")
        else:
            seen_versions.add(patch_ver)
        if not patch_date:
            errors.append(f"patch {patch_ver!r} has an invalid date")
        else:
            valid_patch_dates.append(patch_date)
        if not isinstance(patch.get("summary"), str) or not patch["summary"].strip():
            errors.append(f"patch {patch_ver!r} summary must be a non-empty string")
        source_parts = urlsplit(source_url) if isinstance(source_url, str) else None
        if not source_parts or source_parts.scheme != "https" or not source_parts.netloc:
            errors.append(f"patch {patch_ver!r} source_url must be an absolute HTTPS URL")
        if not isinstance(affects, list) or any(not isinstance(item, str) for item in affects):
            errors.append(f"patch {patch_ver!r} affects_builds must be a list of build ids")
            continue
        if expected_state not in REVIEW_STATES:
            errors.append(f"patch {patch_ver!r} has invalid review_state_after {expected_state!r}")
            continue
        for build_id in affects:
            build = by_id.get(build_id)
            if not build:
                errors.append(
                    f"patch {patch_ver!r} lists affects_builds {build_id!r} but no such build exists"
                )
            if patch_date:
                candidate = (patch_date, sequence, expected_state, patch_ver)
                if build_id not in latest_relevant or candidate[:2] > latest_relevant[build_id][:2]:
                    latest_relevant[build_id] = candidate

    if current_patch and current_patch not in seen_versions:
        errors.append(f"current_patch {current_patch!r} has no matching ledger entry")
    current_entries = [
        patch for patch in patches
        if isinstance(patch, dict) and patch.get("patch_version") == current_patch
    ]
    if current_patch and len(current_entries) != 1:
        errors.append("patch ledger must contain exactly one current patch entry")
    if ledger_updated and valid_patch_dates and ledger_updated < max(valid_patch_dates):
        errors.append("patch ledger updated_at predates its newest patch entry")

    for build_id, (_, _, expected_state, patch_ver) in latest_relevant.items():
        build = by_id.get(build_id)
        if build and build.get("status") == "published":
            actual_state = build.get("review_state")
            if actual_state != expected_state:
                errors.append(
                    f"{build_id}: latest relevant patch {patch_ver!r} "
                    f"with review_state {actual_state!r} (expected {expected_state!r})"
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
