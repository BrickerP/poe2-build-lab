#!/usr/bin/env python3
"""Fetch COMMUNITY-extracted PoE2 gem/base-item datasets.

Context (docs/research/14-development-implementation-plan.md): GGG publishes NO
official skill-gem, support-gem, or base-item export — only the passive/atlas
trees. To unblock a real, working ``.build`` export, this project accepts
*community*-extracted ids, kept strictly separate from official data and clearly
attributed. Sources are pinned by commit in
``data/sources/community-links.json``:

- Skill/support gems: Path of Building Community (PoE2) ``src/Data/Gems.lua``.
  We read each gem's ``gameId`` field, which is the EXACT in-game ``.build``
  metadata id (cross-validated against GGG's official ``.build`` example).
- Base items: RePoE fork (PoE2) ``data/base_items.json``.

Behaviour mirrors ``fetch_official_passive_tree.py``: dependency-free urllib,
honest failure if the network is unavailable, no fabrication. The gems ``.lua``
is vendored under ``data/community/raw/`` (small; lets the custom parser be
audited/re-run offline). The 7.5 MB base-items raw is written to the same dir
but is intentionally git-ignored — only the compact normalized output is
committed (see ``data/community/README.md``).

Usage:
    python3 scripts/fetch_community_data.py
    python3 scripts/fetch_community_data.py --only gems
    python3 scripts/fetch_community_data.py --only base-items
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT / "data" / "sources" / "community-links.json"
MANIFEST_PATH = ROOT / "data" / "community" / "manifest.json"
RAW_DIR = ROOT / "data" / "community" / "raw"

# (source id, output filename under data/community/raw/)
TARGETS = {
    "gems": ("pob-poe2-gems", "pob-poe2-gems.lua"),
    "base-items": ("repoe-poe2-base-items", "repoe-base-items.json"),
}


def load_sources() -> dict:
    return json.loads(SOURCES_PATH.read_text(encoding="utf-8"))


def source_by_id(sources: dict, source_id: str) -> dict | None:
    for src in sources.get("sources", []):
        if src.get("id") == source_id:
            return src
    return None


def download(url: str, timeout: int) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "poe2-build-lab-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def update_manifest(kind: str, byte_len: int) -> None:
    """Record fetched_at on the matching community dataset(s)."""
    if not MANIFEST_PATH.exists():
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    types = (
        ["skill-gems", "support-gems"] if kind == "gems" else ["base-items"]
    )
    for ds in manifest.get("datasets", []):
        if ds.get("type") in types:
            ds["fetched_at"] = date.today().isoformat()
            ds["raw_bytes"] = byte_len
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def fetch_one(kind: str, sources: dict, timeout: int) -> int:
    source_id, filename = TARGETS[kind]
    src = source_by_id(sources, source_id)
    if not src or not src.get("raw_data_url"):
        print(f"ERROR: no raw_data_url for source '{source_id}'", file=sys.stderr)
        return 1
    url = src["raw_data_url"]
    print(f"Fetching {kind} ({source_id}, commit {src.get('pinned_commit', '?')[:12]}):\n  {url}")
    try:
        raw = download(url, timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"\nERROR: could not download {kind} data: {exc}", file=sys.stderr)
        print(
            "This is expected in a sandboxed/offline environment. Re-run from a "
            "machine with network access, then run scripts/normalize_community_data.py.",
            file=sys.stderr,
        )
        return 1

    if filename.endswith(".json"):
        try:
            json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"\nERROR: downloaded {kind} payload is not valid JSON: {exc}", file=sys.stderr)
            return 1

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = RAW_DIR / filename
    out.write_bytes(raw)
    update_manifest(kind, len(raw))
    print(f"  Wrote {len(raw)} bytes to {out.relative_to(ROOT)}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=sorted(TARGETS), help="Fetch a single dataset.")
    parser.add_argument("--timeout", type=int, default=120, help="HTTP timeout seconds (default 120).")
    args = parser.parse_args()

    sources = load_sources()
    kinds = [args.only] if args.only else list(TARGETS)
    rc = 0
    for kind in kinds:
        rc |= fetch_one(kind, sources, args.timeout)
    if rc == 0:
        print("Next: python3 scripts/normalize_community_data.py")
    return rc


if __name__ == "__main__":
    sys.exit(main())
