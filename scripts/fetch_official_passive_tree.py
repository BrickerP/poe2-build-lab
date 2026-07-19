#!/usr/bin/env python3
"""Fetch the official GGG PoE2 passive skill tree export.

Source of truth: the immutable GGG repository commit recorded in
data/official/manifest.json and independently anchored in validate_builds.py.

This script is intentionally dependency-free (urllib from the stdlib) so it can
run in CI or on a fresh checkout without a package manager.

Behaviour:
- Downloads data.json from the commit-addressed raw URL.
- Verifies the upstream identity, SHA-256, Git blob SHA-1, JSON schema, and
  recorded structure before replacing any local file.
- Writes it to data/passive-tree/data.json.
- Updates only fetched_at in data/official/manifest.json.

If the network is unavailable (sandboxed environments, CI without egress), the
script exits non-zero with clear instructions and leaves the placeholder +
manifest untouched, so it never fabricates data.

Usage:
    python3 scripts/fetch_official_passive_tree.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "data" / "official" / "manifest.json"
OUT_PATH = ROOT / "data" / "passive-tree" / "data.json"

try:
    from scripts.validate_builds import (
        validate_passive_tree_raw_payload,
        validate_passive_tree_source_contract,
    )
except ModuleNotFoundError:
    from validate_builds import (  # type: ignore[no-redef]
        validate_passive_tree_raw_payload,
        validate_passive_tree_source_contract,
    )


def load_passive_tree_contract() -> tuple[dict, dict]:
    if not MANIFEST_PATH.is_file():
        raise ValueError("data/official/manifest.json does not exist")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    datasets = manifest.get("datasets")
    passive = (
        [
            dataset
            for dataset in datasets
            if isinstance(dataset, dict) and dataset.get("type") == "passive-tree"
        ]
        if isinstance(datasets, list)
        else []
    )
    if len(passive) != 1:
        raise ValueError(
            "manifest must contain exactly one passive-tree dataset, "
            f"found {len(passive)}"
        )
    errors = validate_passive_tree_source_contract(passive[0])
    if errors:
        raise ValueError("; ".join(errors))
    return manifest, passive[0]


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


def update_manifest(manifest: dict) -> None:
    for dataset in manifest["datasets"]:
        if isinstance(dataset, dict) and dataset.get("type") == "passive-tree":
            dataset["fetched_at"] = date.today().isoformat()
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout", type=int, default=30, help="HTTP timeout in seconds (default 30)."
    )
    args = parser.parse_args()

    try:
        manifest, dataset = load_passive_tree_contract()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: invalid passive-tree provenance contract: {exc}", file=sys.stderr)
        return 1

    url = dataset["source_url"]
    print(f"Fetching official passive tree from:\n  {url}")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "poe2-build-lab-fetch/1.0"})
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            raw = resp.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"\nERROR: could not download passive tree data: {exc}", file=sys.stderr)
        print(
            "\nThis is expected in a sandboxed/offline environment. To complete Phase 0.5:\n"
            "  1. Run this script from a machine with network access:\n"
            "       python3 scripts/fetch_official_passive_tree.py\n"
            f"  2. It will write the raw export to {OUT_PATH.relative_to(ROOT)}\n"
            "  3. Then run: python3 scripts/normalize_official_data.py\n"
            "  4. Commit data/passive-tree/data.json and the updated manifest.\n",
            file=sys.stderr,
        )
        return 1

    actual_sha256 = hashlib.sha256(raw).hexdigest()
    if actual_sha256 != dataset["raw_sha256"]:
        print(
            "\nERROR: downloaded payload does not match the reviewed immutable "
            f"SHA-256: expected {dataset['raw_sha256']}, got {actual_sha256}",
            file=sys.stderr,
        )
        return 1

    actual_blob_sha1 = git_blob_sha1(raw)
    if actual_blob_sha1 != dataset["source_blob_git_sha1"]:
        print(
            "\nERROR: downloaded payload does not match the reviewed upstream Git "
            f"blob: expected {dataset['source_blob_git_sha1']}, got {actual_blob_sha1}",
            file=sys.stderr,
        )
        return 1

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"\nERROR: downloaded payload is not valid JSON: {exc}", file=sys.stderr)
        return 1

    payload_errors = validate_passive_tree_raw_payload(payload, dataset)
    if payload_errors:
        print("\nERROR: downloaded payload violates the manifest structure contract:", file=sys.stderr)
        for error in payload_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=OUT_PATH.parent, prefix=f".{OUT_PATH.name}.", delete=False
        ) as temporary:
            temporary.write(raw)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        temporary_path.replace(OUT_PATH)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    update_manifest(manifest)

    print(f"\nWrote {len(raw)} bytes to {OUT_PATH.relative_to(ROOT)}")
    print("Verified immutable upstream commit, Git blob, SHA-256, and raw structure.")
    print("Updated data/official/manifest.json (fetched_at only).")
    print("Next: python3 scripts/normalize_official_data.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
