#!/usr/bin/env python3
"""Regression tests for build-data provenance validation."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "validate_builds", ROOT / "scripts" / "validate_builds.py"
)
VALIDATE_BUILDS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATE_BUILDS)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


class TradeUrlValidationTests(unittest.TestCase):
    VALID_URLS = (
        "https://www.pathofexile.com/trade2",
        "https://www.pathofexile.com/trade2/search/poe2/Standard/example",
    )
    HOSTILE_URLS = {
        "javascript": "javascript:alert(1)",
        "data": "data:text/html,unsafe",
        "scheme-relative": "//www.pathofexile.com/trade2",
        "off-domain": "https://example.com/trade2",
        "wrong-path": "https://www.pathofexile.com/forum",
    }

    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (ROOT / "data" / "builds" / "schema.json").read_text(encoding="utf-8")
        )
        cls.filter_schema = cls.schema["properties"]["trade_handoff"]["properties"][
            "filters"
        ]["items"]

    def validate_filter(self, trade_url=...):
        trade_filter = {
            "slot": "weapon",
            "budget_tier": "low",
            "required_stats": ["damage"],
        }
        if trade_url is not ...:
            trade_filter["trade_url"] = trade_url

        schema_errors = []
        VALIDATE_BUILDS.validate_against_schema(
            trade_filter,
            self.filter_schema,
            self.schema,
            "trade_handoff.filters[0]",
            schema_errors,
        )
        business_errors = []
        VALIDATE_BUILDS.business_rules(
            {"trade_handoff": {"enabled": True, "filters": [trade_filter]}},
            None,
            None,
            None,
            set(),
            business_errors,
        )
        return schema_errors, business_errors

    def test_official_trade_urls_pass_schema_and_business_rules(self):
        for url in self.VALID_URLS:
            with self.subTest(url=url):
                self.assertEqual(([], []), self.validate_filter(url))

    def test_missing_trade_url_remains_optional(self):
        self.assertEqual(([], []), self.validate_filter())

    def test_hostile_trade_urls_fail_schema_and_business_rules(self):
        for label, url in self.HOSTILE_URLS.items():
            with self.subTest(label=label):
                schema_errors, business_errors = self.validate_filter(url)
                self.assertTrue(schema_errors, label)
                self.assertTrue(
                    any("trade_url must use" in error for error in business_errors),
                    business_errors,
                )

    def test_site_generator_never_renders_hostile_trade_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            shutil.copy2(ROOT / "sitegen.py", root / "sitegen.py")
            shutil.copytree(ROOT / "data", root / "data")
            shutil.copy2(ROOT / ".python-version", root / ".python-version")

            build_path = root / "data" / "builds" / "starter-elemental-caster.json"
            build = json.loads(build_path.read_text(encoding="utf-8"))
            original = build["trade_handoff"]["filters"][0]
            filters = []
            for index, url in enumerate(self.HOSTILE_URLS.values()):
                trade_filter = copy.deepcopy(original)
                trade_filter["slot"] = f"hostile_{index}"
                trade_filter["trade_url"] = url
                filters.append(trade_filter)
            missing = copy.deepcopy(original)
            missing["slot"] = "missing_url"
            missing.pop("trade_url", None)
            filters.append(missing)
            build["trade_handoff"]["filters"] = filters
            build_path.write_text(json.dumps(build) + "\n", encoding="utf-8")

            result = subprocess.run(
                ["python3", "sitegen.py"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            html = (root / "builds" / "starter-elemental-caster.html").read_text(
                encoding="utf-8"
            )
            for url in self.HOSTILE_URLS.values():
                self.assertNotIn(f'href="{url}"', html)
            self.assertEqual(
                len(self.HOSTILE_URLS) + 1,
                html.count("Official trade link unavailable"),
            )


class PassiveTreeProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        raw_path = self.root / "data" / "passive-tree" / "data.json"
        normalized_path = self.root / "data" / "official" / "passive-tree.json"
        raw_path.parent.mkdir(parents=True)
        normalized_path.parent.mkdir(parents=True)

        self.raw = {
            "tree": "test-patch",
            "classes": [
                {
                    "name": "Druid",
                    "base_str": 11,
                    "base_dex": 10,
                    "base_int": 10,
                }
            ],
            "nodes": {
                "root": {"id": "root"},
                "10": {"skill": 10, "id": "DruidStart"},
                "11": {
                    "skill": 11,
                    "id": "Druid1Start",
                    "isAscendancyStart": True,
                    "ascendancyId": "Druid1",
                    "name": "Oracle",
                },
            },
            "groups": {"1": {"x": 0, "y": 0}},
            "edges": [{"id": 1}],
            "skillOverrides": {},
            "jewelSlots": [],
        }
        self.normalized = {
            "generated_at": "2026-01-01",
            "source": "data/passive-tree/data.json",
            "patch_version": "test-patch",
            "node_count": 2,
            "semantic_node_count": 3,
            "classes": [
                {"name": "Druid", "base_str": 11, "base_dex": 10, "base_int": 10}
            ],
            "ascendancies": [
                {"class": "Druid", "code": "Druid1", "name": "Oracle"}
            ],
            "node_ids": ["10", "11"],
            "semantic_node_ids": ["Druid1Start", "DruidStart", "root"],
            "known_gaps": [],
        }
        raw_path.write_text(json.dumps(self.raw) + "\n", encoding="utf-8")
        normalized_path.write_text(json.dumps(self.normalized) + "\n", encoding="utf-8")
        self.raw_path = raw_path
        self.normalized_path = normalized_path
        source_commit = "1" * 40
        self.trusted_snapshot = {
            "source_repo": "official/example",
            "source_commit": source_commit,
            "source_path": "data.json",
            "source_url": (
                f"https://raw.githubusercontent.com/official/example/{source_commit}/data.json"
            ),
            "source_commit_url": (
                f"https://github.com/official/example/commit/{source_commit}"
            ),
            "source_commit_subject": "test-release",
            "source_blob_git_sha1": git_blob_sha1(raw_path),
            "raw_sha256": sha256(raw_path),
            "normalized_sha256": sha256(normalized_path),
            "raw_tree_name": "test-patch",
        }
        self.manifest = {
            "datasets": [
                {
                    "type": "passive-tree",
                    "coverage": "complete",
                    **self.trusted_snapshot,
                    "local_raw": "data/passive-tree/data.json",
                    "local_normalized": "data/official/passive-tree.json",
                    "raw_node_record_count": 3,
                    "node_count": 2,
                    "semantic_node_count": 3,
                    "class_count": 1,
                    "ascendancy_count": 1,
                    "group_count": 1,
                    "edge_count": 1,
                    "skill_override_count": 0,
                    "jewel_slot_count": 0,
                }
            ]
        }
        sources_path = self.root / "data" / "sources" / "official-links.json"
        sources_path.parent.mkdir(parents=True)
        sources_path.write_text(
            json.dumps(
                {
                    "sources": [
                        {
                            "id": "ggg-passive-tree-export",
                            "url": "https://github.com/official/example",
                            "source_commit": source_commit,
                            "source_path": "data.json",
                            "raw_data_url": self.trusted_snapshot["source_url"],
                        }
                    ]
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.sources_path = sources_path

    def tearDown(self):
        self.temporary.cleanup()

    def validate(self, manifest=None):
        return VALIDATE_BUILDS.validate_official_manifest_provenance(
            self.manifest if manifest is None else manifest,
            self.root,
            self.trusted_snapshot,
        )

    def test_valid_raw_and_normalized_resources_pass(self):
        self.assertEqual([], self.validate())

    def test_missing_raw_is_rejected(self):
        self.raw_path.unlink()
        self.assert_error("local_raw does not exist")

    def test_corrupt_raw_is_rejected(self):
        self.raw_path.write_text("{not-json", encoding="utf-8")
        self.manifest["datasets"][0]["raw_sha256"] = sha256(self.raw_path)
        self.assert_error("local_raw is not valid JSON")

    def test_corrupt_normalized_is_rejected(self):
        self.normalized_path.write_text("{not-json", encoding="utf-8")
        self.manifest["datasets"][0]["normalized_sha256"] = sha256(
            self.normalized_path
        )
        self.assert_error("local_normalized is not valid JSON")

    def test_recorded_hash_mismatch_is_rejected(self):
        self.manifest["datasets"][0]["raw_sha256"] = "0" * 64
        self.assert_error("raw_sha256 mismatch")

    def test_recorded_count_mismatch_is_rejected(self):
        self.manifest["datasets"][0]["node_count"] = 999
        self.assert_error("node_count mismatch")

    def test_moving_branch_source_url_is_rejected(self):
        self.manifest["datasets"][0]["source_url"] = (
            "https://raw.githubusercontent.com/official/example/master/data.json"
        )
        self.assert_error("source_url is not the reviewed immutable upstream value")

    def test_moving_branch_source_catalog_url_is_rejected(self):
        catalog = json.loads(self.sources_path.read_text(encoding="utf-8"))
        catalog["sources"][0]["raw_data_url"] = (
            "https://raw.githubusercontent.com/official/example/master/data.json"
        )
        self.sources_path.write_text(json.dumps(catalog) + "\n", encoding="utf-8")
        self.assert_error("official source catalog ggg-passive-tree-export.raw_data_url mismatch")

    def test_mismatched_upstream_repo_commit_and_path_are_rejected(self):
        dataset = self.manifest["datasets"][0]
        dataset["source_repo"] = "attacker/fork"
        dataset["source_commit"] = "2" * 40
        dataset["source_path"] = "fabricated.json"
        errors = self.validate()
        for field in ("source_repo", "source_commit", "source_path"):
            self.assertTrue(any(field in error for error in errors), errors)

    def test_incomplete_upstream_provenance_is_rejected(self):
        del self.manifest["datasets"][0]["source_blob_git_sha1"]
        self.assert_error("missing required source_blob_git_sha1")

    def test_incomplete_coverage_is_rejected(self):
        self.manifest["datasets"][0]["coverage"] = "partial"
        self.assert_error("coverage must be 'complete'")

    def test_self_consistent_fabricated_raw_and_manifest_are_rejected(self):
        self.raw["nodes"]["12"] = {"skill": 12, "id": "Fabricated"}
        self.raw_path.write_text(json.dumps(self.raw) + "\n", encoding="utf-8")
        dataset = self.manifest["datasets"][0]
        dataset["raw_sha256"] = sha256(self.raw_path)
        dataset["source_blob_git_sha1"] = git_blob_sha1(self.raw_path)
        dataset["raw_node_record_count"] = 4
        dataset["node_count"] = 3
        dataset["semantic_node_count"] = 4
        errors = self.validate()
        self.assertTrue(
            any("raw_sha256 is not the reviewed immutable upstream value" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("source_blob_git_sha1 is not the reviewed immutable upstream value" in error for error in errors),
            errors,
        )

    def test_raw_structure_count_mismatch_is_rejected(self):
        self.manifest["datasets"][0]["edge_count"] = 99
        self.assert_error("edge_count mismatch")

    def test_raw_tree_name_mismatch_is_rejected(self):
        self.raw["tree"] = "Other"
        self.raw_path.write_text(json.dumps(self.raw) + "\n", encoding="utf-8")
        self.manifest["datasets"][0]["raw_sha256"] = sha256(self.raw_path)
        self.manifest["datasets"][0]["source_blob_git_sha1"] = git_blob_sha1(
            self.raw_path
        )
        self.assert_error("raw_tree_name mismatch")

    def test_path_traversal_is_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["datasets"][0]["local_raw"] = "../outside.json"
        errors = self.validate(manifest)
        self.assertTrue(any("local_raw escapes repository root" in error for error in errors), errors)

    def test_every_manifest_local_path_must_exist(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["datasets"].append(
            {"type": "future-dataset", "local_fixture": "data/missing.json"}
        )
        errors = self.validate(manifest)
        self.assertTrue(
            any("future-dataset.local_fixture does not exist" in error for error in errors),
            errors,
        )

    def test_raw_to_normalized_drift_is_rejected_even_with_updated_hash(self):
        drifted = copy.deepcopy(self.normalized)
        drifted["ascendancies"][0]["name"] = "Fabricated"
        self.normalized_path.write_text(json.dumps(drifted) + "\n", encoding="utf-8")
        self.manifest["datasets"][0]["normalized_sha256"] = sha256(
            self.normalized_path
        )
        self.assert_error("does not deterministically match local_raw")

    def assert_error(self, expected):
        errors = self.validate()
        self.assertTrue(any(expected in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
