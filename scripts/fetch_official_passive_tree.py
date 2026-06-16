#!/usr/bin/env python3
"""Fetch the official GGG PoE2 passive skill tree export.

Source of truth: https://github.com/grindinggear/poe2-skilltree-export (data.json)

This script is intentionally dependency-free (urllib from the stdlib) so it can
run in CI or on a fresh checkout without a package manager.

Behaviour:
- Downloads data.json from the pinned raw URL.
- Verifies the payload parses as JSON.
- Writes it to data/passive-tree/data.json.
- Updates data/official/manifest.json: fetched_at + coverage='complete' for the
  passive-tree dataset.

If the network is unavailable (sandboxed environments, CI without egress), the
script exits non-zero with clear instructions and leaves the placeholder +
manifest untouched, so it never fabricates data.

Usage:
    python3 scripts/fetch_official_passive_tree.py
    python3 scripts/fetch_official_passive_tree.py --url <override>
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
MANIFEST_PATH = ROOT / "data" / "official" / "manifest.json"
SOURCES_PATH = ROOT / "data" / "sources" / "official-links.json"
OUT_PATH = ROOT / "data" / "passive-tree" / "data.json"

FALLBACK_URL = (
    "https://raw.githubusercontent.com/grindinggear/poe2-skilltree-export/master/data.json"
)


def resolve_url(cli_url: str | None) -> str:
    if cli_url:
        return cli_url
    if SOURCES_PATH.exists():
        sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
        for src in sources.get("sources", []):
            if src.get("id") == "ggg-passive-tree-export" and src.get("raw_data_url"):
                return src["raw_data_url"]
    return FALLBACK_URL


def update_manifest(byte_len: int) -> None:
    if not MANIFEST_PATH.exists():
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for ds in manifest.get("datasets", []):
        if ds.get("type") == "passive-tree":
            ds["fetched_at"] = date.today().isoformat()
            ds["coverage"] = "complete"
            ds["known_gaps"] = [
                f"Raw GGG export fetched ({byte_len} bytes). "
                "Run scripts/normalize_official_data.py to derive node ids before enabling export."
            ]
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Override the raw data.json URL.")
    parser.add_argument(
        "--timeout", type=int, default=30, help="HTTP timeout in seconds (default 30)."
    )
    args = parser.parse_args()

    url = resolve_url(args.url)
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

    try:
        json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"\nERROR: downloaded payload is not valid JSON: {exc}", file=sys.stderr)
        return 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(raw)
    update_manifest(len(raw))

    print(f"\nWrote {len(raw)} bytes to {OUT_PATH.relative_to(ROOT)}")
    print("Updated data/official/manifest.json (passive-tree coverage=complete).")
    print("Next: python3 scripts/normalize_official_data.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
