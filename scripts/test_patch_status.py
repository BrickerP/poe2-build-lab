#!/usr/bin/env python3
"""Regression tests for patch-ledger current-state enforcement."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from check_patch_status import collect_violations


class PatchStatusTests(unittest.TestCase):
    def fixture(self, build_state="needs_review"):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        builds = root / "builds"
        builds.mkdir()
        (builds / "demo.json").write_text(
            json.dumps(
                {
                    "id": "demo",
                    "status": "published",
                    "patch_version": "0.5.3 Early Access",
                    "last_reviewed": "2026-07-01",
                    "review_state": build_state,
                }
            ),
            encoding="utf-8",
        )
        ledger = {
            "current_patch": "0.5.4c Early Access",
            "updated_at": "2026-07-17",
            "patches": [
                {
                    "patch_version": "0.5.3 Early Access",
                    "date": "2026-07-01",
                    "source_url": "https://example.com/0.5.3",
                    "summary": "Historical reviewed patch.",
                    "affects_builds": ["demo"],
                    "review_state_after": "current",
                },
                {
                    "patch_version": "0.5.4c Early Access",
                    "date": "2026-07-17",
                    "source_url": "https://example.com/0.5.4c",
                    "summary": "Latest patch requires review.",
                    "affects_builds": ["demo"],
                    "review_state_after": "needs_review",
                },
            ],
        }
        ledger_path = root / "patch-notes.json"
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        return temporary, ledger_path, builds, ledger

    def test_latest_relevant_patch_controls_current_state(self):
        temporary, ledger_path, builds, _ = self.fixture()
        with temporary:
            errors, _, _, _ = collect_violations(ledger_path, builds)
        self.assertEqual([], errors)

    def test_wrong_state_for_latest_relevant_patch_fails(self):
        temporary, ledger_path, builds, _ = self.fixture(build_state="current")
        with temporary:
            errors, _, _, _ = collect_violations(ledger_path, builds)
        self.assertTrue(any("latest relevant patch" in error for error in errors), errors)

    def test_historical_build_references_are_still_validated(self):
        temporary, ledger_path, builds, ledger = self.fixture()
        with temporary:
            ledger["patches"][0]["affects_builds"] = ["missing-build"]
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
            errors, _, _, _ = collect_violations(ledger_path, builds)
        self.assertTrue(any("no such build" in error for error in errors), errors)

    def test_official_links_cannot_duplicate_current_patch_marker(self):
        temporary, ledger_path, builds, _ = self.fixture()
        with temporary:
            official_links = ledger_path.parent / "official-links.json"
            official_links.write_text(
                json.dumps({"patch_version": "0.5.4c Early Access", "sources": []}),
                encoding="utf-8",
            )
            errors, _, _, _ = collect_violations(ledger_path, builds, official_links)
        self.assertTrue(any("duplicates patch ledger" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
