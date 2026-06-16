#!/usr/bin/env python3
"""Normalize the raw GGG passive tree export into a compact id index.

Input:  data/passive-tree/data.json   (raw GGG export, fetched separately)
Output: data/official/passive-tree.json (normalized: node ids + class roots)

The raw GGG export schema is large and may shift between patches, so this
normalizer is defensive: it extracts the fields the build schema needs (passive
node ids and, when present, class/ascendancy start node metadata) and records
anything it could not interpret under "known_gaps" rather than guessing.

Run scripts/fetch_official_passive_tree.py first. If the raw file is absent,
this script explains the gap and exits non-zero without fabricating data.

Usage:
    python3 scripts/normalize_official_data.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "passive-tree" / "data.json"
OUT_PATH = ROOT / "data" / "official" / "passive-tree.json"
MANIFEST_PATH = ROOT / "data" / "official" / "manifest.json"


def extract_node_ids(raw: dict) -> list[str]:
    """Return passive node ids from the export, tolerant of schema variation."""
    nodes = raw.get("nodes")
    if isinstance(nodes, dict):
        return sorted(nodes.keys())
    if isinstance(nodes, list):
        ids = []
        for node in nodes:
            if isinstance(node, dict):
                node_id = node.get("skill") or node.get("id")
                if node_id is not None:
                    ids.append(str(node_id))
        return sorted(set(ids))
    return []


def extract_classes(raw: dict) -> list[dict]:
    classes = raw.get("classes") or raw.get("characterData")
    result = []
    if isinstance(classes, list):
        for entry in classes:
            if isinstance(entry, dict):
                result.append(
                    {
                        "name": entry.get("name") or entry.get("base_str") or "unknown",
                        "ascendancies": [
                            a.get("name")
                            for a in entry.get("ascendancies", [])
                            if isinstance(a, dict) and a.get("name")
                        ],
                    }
                )
    return result


def update_manifest(node_count: int) -> None:
    if not MANIFEST_PATH.exists():
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for ds in manifest.get("datasets", []):
        if ds.get("type") == "passive-tree":
            ds["coverage"] = "complete" if node_count else "partial"
            ds["known_gaps"] = (
                [] if node_count else ["Normalizer found 0 node ids; export schema may have changed."]
            )
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    if not RAW_PATH.exists():
        print(
            f"ERROR: raw export not found at {RAW_PATH.relative_to(ROOT)}.\n"
            "Run scripts/fetch_official_passive_tree.py first (needs network access).",
            file=sys.stderr,
        )
        return 1

    try:
        raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: raw export is not valid JSON: {exc}", file=sys.stderr)
        return 1

    node_ids = extract_node_ids(raw)
    classes = extract_classes(raw)

    known_gaps = []
    if not node_ids:
        known_gaps.append("No passive node ids extracted; export schema may differ from expectations.")
    if not classes:
        known_gaps.append("No class/ascendancy metadata extracted.")

    normalized = {
        "generated_at": date.today().isoformat(),
        "source": "data/passive-tree/data.json",
        "node_count": len(node_ids),
        "node_ids": node_ids,
        "classes": classes,
        "known_gaps": known_gaps,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    update_manifest(len(node_ids))

    print(f"Normalized {len(node_ids)} passive node id(s) -> {OUT_PATH.relative_to(ROOT)}")
    if known_gaps:
        print("Known gaps recorded:")
        for gap in known_gaps:
            print(f"  - {gap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
