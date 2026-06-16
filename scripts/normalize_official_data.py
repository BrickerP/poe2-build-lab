#!/usr/bin/env python3
"""Normalize the raw GGG passive tree export into a compact official index.

Input:  data/passive-tree/data.json   (raw GGG export, fetched separately)
Output: data/official/passive-tree.json

The raw GGG export schema is large and may shift between patches, so this
normalizer is defensive: it extracts the fields the build schema and the
``.build`` exporter need and records anything it could not interpret under
``known_gaps`` rather than guessing.

What the official passive-tree export authoritatively provides (and this
normalizer extracts):

- passive node ids in both id spaces: the numeric ``skill`` id (dict key) and
  the semantic ``id`` string (e.g. ``"AscendancyWarrior1Notable4"``). The
  official ``.build`` file format references passives by the semantic id.
- per-class base attributes (Str/Dex/Int).
- ascendancy code <-> name mapping (e.g. ``Sorceress1`` -> ``Stormweaver``),
  read from the ascendancy start nodes, which carry the in-game name. The
  ``.build`` file format references ascendancy by code (e.g. ``"Warrior1"``).

What it does NOT provide: skill gem, support gem, or base-item ids. GGG only
publishes the passive (and atlas) trees as official data exports
(https://www.pathofexile.com/developer/docs/data). Those id spaces are tracked
as known gaps in data/official/manifest.json and stay TBD in build cards.

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


def extract_node_ids(raw: dict) -> tuple[list[str], list[str]]:
    """Return (numeric node ids, semantic node ids) from the export.

    Tolerant of schema variation: the numeric id is the ``skill`` field or the
    dict key; the semantic id is the ``id`` field (used by ``.build`` passives).
    """
    numeric: set[str] = set()
    semantic: set[str] = set()
    nodes = raw.get("nodes")
    if isinstance(nodes, dict):
        for key, node in nodes.items():
            if key.isdigit():
                numeric.add(key)
            if isinstance(node, dict):
                skill = node.get("skill")
                if skill is not None:
                    numeric.add(str(skill))
                sid = node.get("id")
                if isinstance(sid, str) and sid:
                    semantic.add(sid)
    elif isinstance(nodes, list):
        for node in nodes:
            if isinstance(node, dict):
                skill = node.get("skill") or node.get("id")
                if skill is not None:
                    numeric.add(str(skill))
                sid = node.get("id")
                if isinstance(sid, str) and sid:
                    semantic.add(sid)
    return sorted(numeric), sorted(semantic)


def extract_classes(raw: dict) -> list[dict]:
    """Per-class base attributes from the raw ``classes`` list."""
    classes = raw.get("classes")
    result = []
    if isinstance(classes, list):
        for entry in classes:
            if isinstance(entry, dict) and entry.get("name"):
                result.append(
                    {
                        "name": entry["name"],
                        "base_str": entry.get("base_str"),
                        "base_dex": entry.get("base_dex"),
                        "base_int": entry.get("base_int"),
                    }
                )
    return result


def extract_ascendancies(raw: dict) -> list[dict]:
    """Ascendancy code <-> name mapping from ascendancy start nodes.

    The start node carries the authoritative in-game ascendancy ``name`` and an
    ``ascendancyId`` code (e.g. ``Sorceress1``). Only mapped entries with a
    non-empty name are returned; unreleased/blank slots are skipped rather than
    invented.
    """
    nodes = raw.get("nodes")
    out = []
    iterable = nodes.values() if isinstance(nodes, dict) else (nodes or [])
    for node in iterable:
        if not isinstance(node, dict):
            continue
        if not node.get("isAscendancyStart"):
            continue
        code = node.get("ascendancyId")
        name = node.get("name")
        if code and name:
            klass = "".join(ch for ch in code if not ch.isdigit())
            out.append({"class": klass, "code": code, "name": name})
    out.sort(key=lambda a: a["code"])
    return out


def update_manifest(node_count: int, ascendancy_count: int) -> None:
    if not MANIFEST_PATH.exists():
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for ds in manifest.get("datasets", []):
        if ds.get("type") == "passive-tree":
            ds["coverage"] = "complete" if node_count else "partial"
            ds["coverage_notes"] = (
                f"Normalized {node_count} passive node ids (numeric + semantic) and "
                f"{ascendancy_count} ascendancy code/name mappings plus per-class base "
                "attributes from the official GGG export."
            )
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

    node_ids, semantic_node_ids = extract_node_ids(raw)
    classes = extract_classes(raw)
    ascendancies = extract_ascendancies(raw)

    known_gaps = []
    if not node_ids:
        known_gaps.append("No passive node ids extracted; export schema may differ from expectations.")
    if not classes:
        known_gaps.append("No class base-attribute metadata extracted.")
    if not ascendancies:
        known_gaps.append("No ascendancy code/name mapping extracted.")

    normalized = {
        "generated_at": date.today().isoformat(),
        "source": "data/passive-tree/data.json",
        "patch_version": raw.get("tree", "unknown"),
        "node_count": len(node_ids),
        "semantic_node_count": len(semantic_node_ids),
        "classes": classes,
        "ascendancies": ascendancies,
        "node_ids": node_ids,
        "semantic_node_ids": semantic_node_ids,
        "known_gaps": known_gaps,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    update_manifest(len(node_ids), len(ascendancies))

    print(
        f"Normalized {len(node_ids)} numeric / {len(semantic_node_ids)} semantic passive node id(s), "
        f"{len(classes)} class(es), {len(ascendancies)} ascendancy mapping(s) -> "
        f"{OUT_PATH.relative_to(ROOT)}"
    )
    if known_gaps:
        print("Known gaps recorded:")
        for gap in known_gaps:
            print(f"  - {gap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
