#!/usr/bin/env python3
"""Normalize community-extracted PoE2 gem/base-item data into compact id maps.

Inputs (fetched by scripts/fetch_community_data.py, pinned in
data/sources/community-links.json):

- data/community/raw/pob-poe2-gems.lua    Path of Building Community (PoE2) gem table
- data/community/raw/repoe-base-items.json RePoE fork (PoE2) base items

Outputs (committed; consumed by the validator, exporter, and pages):

- data/community/skill-gems.json    active skill gems    {id (gameId), name, req, tags}
- data/community/support-gems.json  support gems         {id (gameId), name, req, tags}
- data/community/base-items.json    equippable base items {id, name, item_class, drop_level, req}

Why ``gameId`` and not the Lua table key: the Path of Building table is keyed by
an internal display id, but each entry's ``gameId`` is the actual in-game item
metadata path the ``.build`` File Watcher expects. PoE2 gem paths are irregular
(``Metadata/Items/Gems/SkillGemSpark`` vs ``Metadata/Items/Gem/SkillGemFireball``),
so the exact ``gameId`` is taken per gem rather than any blanket convention.

This parser is intentionally dependency-free (regex over the well-formed,
machine-generated Lua) so it runs on a bare python3 in CI.

Usage:
    python3 scripts/normalize_community_data.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "community" / "raw"
GEMS_LUA = RAW_DIR / "pob-poe2-gems.lua"
BASE_ITEMS_RAW = RAW_DIR / "repoe-base-items.json"
OUT_DIR = ROOT / "data" / "community"
SKILL_OUT = OUT_DIR / "skill-gems.json"
SUPPORT_OUT = OUT_DIR / "support-gems.json"
BASE_OUT = OUT_DIR / "base-items.json"
MANIFEST_PATH = OUT_DIR / "manifest.json"
SOURCES_PATH = ROOT / "data" / "sources" / "community-links.json"

# Equippable item classes (gear, jewellery, weapons, flasks, jewels). Everything
# else (gems, currency, maps, quest items, league mechanics) is excluded — we
# only need base ids that a build can reference.
EQUIP_CLASSES = {
    "Amulet", "Belt", "Body Armour", "Boots", "Bow", "Buckler", "Claw",
    "Crossbow", "Dagger", "Flail", "Focus", "Gloves", "Helmet", "Jewel",
    "LifeFlask", "ManaFlask", "One Hand Axe", "One Hand Mace", "One Hand Sword",
    "Quiver", "Ring", "Sceptre", "Shield", "Spear", "Staff", "Talisman",
    "Two Hand Axe", "Two Hand Mace", "Two Hand Sword", "UtilityFlask", "Wand",
    "Warstaff",
}

# Lua block: one tab indent, ["<key>"] = { ... \n\t},
GEM_BLOCK = re.compile(r'\t\["[^"]+"\]\s*=\s*\{(?P<body>.*?)\n\t\},', re.S)


def _lua_str(body: str, field: str):
    m = re.search(r'\b' + field + r'\s*=\s*"([^"]*)"', body)
    return m.group(1) if m else None


def _lua_int(body: str, field: str) -> int:
    m = re.search(r'\b' + field + r'\s*=\s*(-?\d+)', body)
    return int(m.group(1)) if m else 0


def _lua_tags(body: str) -> list[str]:
    m = re.search(r'tags\s*=\s*\{(.*?)\}', body, re.S)
    if not m:
        return []
    return sorted(re.findall(r'(\w+)\s*=\s*true', m.group(1)))


def parse_gems(text: str):
    """Return (skill_gems, support_gems) deduped by gameId, in file order."""
    skills, supports = {}, {}
    for block in GEM_BLOCK.finditer(text):
        body = block.group("body")
        game_id = _lua_str(body, "gameId")
        name = _lua_str(body, "name")
        if not game_id or not name:
            continue
        is_support = "SupportGem" in game_id
        bucket = supports if is_support else skills
        if game_id in bucket:
            continue  # keep first (base) variant for a given metadata id
        bucket[game_id] = {
            "id": game_id,
            "name": name,
            "req": {
                "str": _lua_int(body, "reqStr"),
                "dex": _lua_int(body, "reqDex"),
                "int": _lua_int(body, "reqInt"),
            },
            "tags": _lua_tags(body),
        }
    return list(skills.values()), list(supports.values())


def parse_base_items(raw: dict):
    out = []
    for meta_id, item in raw.items():
        if item.get("item_class") not in EQUIP_CLASSES:
            continue
        req = item.get("requirements") or {}
        out.append({
            "id": meta_id,
            "name": item.get("name"),
            "item_class": item.get("item_class"),
            "drop_level": item.get("drop_level"),
            "release_state": item.get("release_state"),
            "req": {
                "str": req.get("strength", 0) or 0,
                "dex": req.get("dexterity", 0) or 0,
                "int": req.get("intelligence", 0) or 0,
                "level": req.get("level", 0) or 0,
            },
        })
    out.sort(key=lambda b: (b["item_class"] or "", b["name"] or ""))
    return out


def source_meta(source_id: str) -> dict:
    if not SOURCES_PATH.exists():
        return {}
    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    for src in sources.get("sources", []):
        if src.get("id") == source_id:
            return src
    return {}


def write_dataset(path: Path, kind: str, source_id: str, items: list) -> None:
    src = source_meta(source_id)
    payload = {
        "generated_at": date.today().isoformat(),
        "provenance": "community",
        "kind": kind,
        "source": src.get("label", source_id),
        "source_url": src.get("url"),
        "pinned_commit": src.get("pinned_commit"),
        "note": (
            "Community-extracted PoE2 data, not an official GGG export. "
            "Game data (c) Grinding Gear Games."
        ),
        "count": len(items),
        "items": items,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_manifest(skill_n: int, support_n: int, base_n: int) -> None:
    if not MANIFEST_PATH.exists():
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    counts = {"skill-gems": skill_n, "support-gems": support_n, "base-items": base_n}
    for ds in manifest.get("datasets", []):
        n = counts.get(ds.get("type"))
        if n is None:
            continue
        ds["coverage"] = "present" if n else "missing"
        ds["count"] = n
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> int:
    if not GEMS_LUA.exists():
        print(
            f"ERROR: {GEMS_LUA.relative_to(ROOT)} not found.\n"
            "Run scripts/fetch_community_data.py first (needs network access).",
            file=sys.stderr,
        )
        return 1

    skills, supports = parse_gems(GEMS_LUA.read_text(encoding="utf-8"))
    if not skills or not supports:
        print("ERROR: parsed 0 skill or support gems; Gems.lua format may have changed.", file=sys.stderr)
        return 1
    write_dataset(SKILL_OUT, "skill-gems", "pob-poe2-gems", skills)
    write_dataset(SUPPORT_OUT, "support-gems", "pob-poe2-gems", supports)
    print(f"Skill gems:   {len(skills):4d} -> {SKILL_OUT.relative_to(ROOT)}")
    print(f"Support gems: {len(supports):4d} -> {SUPPORT_OUT.relative_to(ROOT)}")

    base_n = 0
    if BASE_ITEMS_RAW.exists():
        bases = parse_base_items(json.loads(BASE_ITEMS_RAW.read_text(encoding="utf-8")))
        write_dataset(BASE_OUT, "base-items", "repoe-poe2-base-items", bases)
        base_n = len(bases)
        print(f"Base items:   {base_n:4d} -> {BASE_OUT.relative_to(ROOT)}")
    else:
        print(
            f"WARN: {BASE_ITEMS_RAW.relative_to(ROOT)} not found; skipping base items "
            "(run fetch_community_data.py --only base-items to populate)."
        )

    update_manifest(len(skills), len(supports), base_n)
    print("Updated data/community/manifest.json coverage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
