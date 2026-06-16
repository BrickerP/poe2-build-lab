#!/usr/bin/env python3
"""Export build cards to the official PoE2 ``.build`` file format.

Target schema: the official in-game Build Planner format documented at
https://www.pathofexile.com/developer/docs/game (Version 1, Experimental). A
``.build`` file is a single JSON object:

    name             (required) display name
    author           (optional) string
    ascendancy       (optional) code, e.g. "Sorceress1"
    passives         array of semantic passive node ids (or {id, additional_text})
    skills           array of {id (gem metadata path), additional_text, support_skills}
    inventory_slots  array of {inventory_id (e.g. "Weapon1"), additional_text}

Safety contract (doc 14 Phase 2 + verification checklist):

- Only builds with ``build_file.enabled == true`` are exported.
- The exporter REFUSES to emit if any required id is still ``TBD``/placeholder
  (skill/support gem metadata ids, ascendancy, or any present passive node id),
  so a placeholder ``.build`` can never ship.
- Ascendancy names are translated to official codes via
  ``data/official/passive-tree.json``; an unknown ascendancy is a hard refusal.
- ``inventory_slots`` are derived from gear-slot priorities. The official format
  uses a slot id plus free-text stat-priority hints (no base-item id), so this
  needs no base-item dataset.

Gem id source: GGG publishes no official skill-gem export, so gem ids are
resolved from COMMUNITY-extracted data (Path of Building Community PoE2
``gameId`` field, normalized into ``data/community/skill-gems.json`` and
``support-gems.json``). Per doc 14 this community data is accepted to power
export. Every skill/support gem id in an enabled build must be a member of that
dataset, so a typo'd or fabricated id is refused. A build whose gems are still
``TBD`` keeps ``build_file.enabled: false`` and is skipped.

Usage:
    python3 scripts/export_build_files.py            # export all enabled builds
    python3 scripts/export_build_files.py --check     # CI gate: validate only
    python3 scripts/export_build_files.py --selftest  # run built-in tests
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDS_DIR = ROOT / "data" / "builds"
OFFICIAL_DIR = ROOT / "data" / "official"
PASSIVE_TREE_PATH = OFFICIAL_DIR / "passive-tree.json"
COMMUNITY_DIR = ROOT / "data" / "community"
SKILL_GEMS_PATH = COMMUNITY_DIR / "skill-gems.json"
SUPPORT_GEMS_PATH = COMMUNITY_DIR / "support-gems.json"
OUT_DIR = ROOT / "assets" / "builds"

TBD = "TBD"
AUTHOR = "PoE2 Build Lab"

# Map our gear-slot keys to official .build inventory_id values.
INVENTORY_ID_MAP = {
    "weapon": "Weapon1",
    "weapon_1": "Weapon1",
    "weapon_2": "Weapon2",
    "offhand": "Weapon2",
    "body_armour": "BodyArmour1",
    "helmet": "Helm1",
    "gloves": "Gloves1",
    "boots": "Boots1",
    "belt": "Belt1",
    "amulet": "Amulet1",
    "ring_1": "Ring1",
    "ring_2": "Ring2",
}


class ExportRefused(Exception):
    """Raised when a build cannot be exported without placeholder/invalid ids."""


def load_json(path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def ascendancy_code_map(passive_tree):
    """name -> code and code -> code, from official ascendancy data."""
    mapping = {}
    for asc in (passive_tree or {}).get("ascendancies", []):
        name, code = asc.get("name"), asc.get("code")
        if name and code:
            mapping[name] = code
            mapping[code] = code
    return mapping


def official_node_ids(passive_tree):
    pt = passive_tree or {}
    return set(pt.get("node_ids", [])) | set(pt.get("semantic_node_ids", []))


def community_gem_ids():
    """Set of every real gem metadata id from the community datasets.

    Returns an empty set if the datasets are absent (e.g. a partial checkout);
    callers treat an empty set as "no verification available" and skip the
    membership check rather than refusing every id.
    """
    ids = set()
    for path in (SKILL_GEMS_PATH, SUPPORT_GEMS_PATH):
        if path.exists():
            for item in load_json(path).get("items", []):
                if item.get("id"):
                    ids.add(item["id"])
    return ids


def _slot_additional_text(slot_name, slot):
    base = slot.get("base", "Any base")
    priorities = slot.get("priority", [])
    lines = ["Stat Priority", "-------------------"]
    lines += [f"{i + 1}. {p}" for i, p in enumerate(priorities)]
    # Real newlines: json.dumps serializes them as the \n escape GGG's official
    # .build example uses, so the in-game markup renders line breaks (not a
    # literal "\n"). See docs/research/03-build-planner-build-files.md.
    body = "\n".join(lines)
    text = f"<silver>{{{base}}}\n\n<grey>{{{body}}}"
    if slot.get("budget_note"):
        text += f"\n\n<grey>{{Budget: {slot['budget_note']}}}"
    return text


def build_to_dotbuild(build, passive_tree, valid_gem_ids=None):
    """Map a build card dict to an official .build dict, or raise ExportRefused.

    ``valid_gem_ids`` is the set of real gem metadata ids from the community
    datasets. When non-empty, every skill/support gem id must be a member, so a
    typo'd or fabricated id can never ship. An empty/``None`` set skips the
    membership check (datasets unavailable).
    """
    asc_map = ascendancy_code_map(passive_tree)
    valid_nodes = official_node_ids(passive_tree)
    valid_gem_ids = valid_gem_ids or set()

    # Ascendancy: required to be resolved + known.
    asc_name = build.get("ascendancy")
    if not asc_name or asc_name == TBD:
        raise ExportRefused("ascendancy is unresolved (TBD)")
    asc_code = asc_map.get(asc_name)
    if not asc_code:
        raise ExportRefused(f"ascendancy {asc_name!r} is not a known official ascendancy")

    # Skills: every gem id (and support id) must be a real metadata path.
    skills = []
    for i, skill in enumerate(build.get("skills", [])):
        gem = skill.get("gem_id")
        if not gem or gem == TBD:
            raise ExportRefused(f"skills[{i}].gem_id is TBD")
        if valid_gem_ids and gem not in valid_gem_ids:
            raise ExportRefused(f"skills[{i}].gem_id {gem!r} is not a known community gem id")
        entry = {"id": gem}
        if skill.get("note"):
            entry["additional_text"] = skill["note"]
        supports = []
        for j, sup in enumerate(skill.get("supports", [])):
            sup_gem = sup.get("gem_id")
            if not sup_gem or sup_gem == TBD:
                raise ExportRefused(f"skills[{i}].supports[{j}].gem_id is TBD")
            if valid_gem_ids and sup_gem not in valid_gem_ids:
                raise ExportRefused(
                    f"skills[{i}].supports[{j}].gem_id {sup_gem!r} is not a known community gem id"
                )
            if sup.get("note"):
                supports.append({"id": sup_gem, "additional_text": sup["note"]})
            else:
                supports.append(sup_gem)
        if supports:
            entry["support_skills"] = supports
        skills.append(entry)

    # Passives: optional, but any provided node id must be real and non-TBD.
    passives = []
    for milestone in build.get("passive_milestones", []):
        for node in milestone.get("node_ids", []):
            if node == TBD:
                raise ExportRefused("a passive_milestones node id is TBD")
            if valid_nodes and node not in valid_nodes:
                raise ExportRefused(f"passive node id {node!r} is not in the official tree")
            passives.append(node)

    # Inventory slots: derived from gear-slot priorities (no base-item id needed).
    inventory_slots = []
    for slot_name, slot in build.get("gear_slots", {}).items():
        inv_id = INVENTORY_ID_MAP.get(slot_name)
        if not inv_id:
            continue
        inventory_slots.append(
            {"inventory_id": inv_id, "additional_text": _slot_additional_text(slot_name, slot)}
        )

    dotbuild = {
        "name": build.get("name", build.get("id", "PoE2 Build")),
        "author": AUTHOR,
        "ascendancy": asc_code,
        "passives": passives,
        "skills": skills,
        "inventory_slots": inventory_slots,
    }
    return dotbuild


def export_build(build, passive_tree, write, valid_gem_ids=None):
    """Return (status, message). status in {'written','refused','skipped'}."""
    bid = build.get("id", "?")
    bf = build.get("build_file", {})
    if not bf.get("enabled"):
        return ("skipped", f"{bid}: build_file.enabled is false (export disabled)")
    try:
        dotbuild = build_to_dotbuild(build, passive_tree, valid_gem_ids)
    except ExportRefused as exc:
        return ("refused", f"{bid}: REFUSED — {exc}")

    # Sanity: must serialize to valid JSON and the file watcher needs name + skills.
    payload = json.dumps(dotbuild, indent=2, ensure_ascii=False) + "\n"
    json.loads(payload)
    if not dotbuild["name"] or not dotbuild["skills"]:
        return ("refused", f"{bid}: REFUSED — a .build needs a name and at least one skill")

    rel = bf.get("path") or f"assets/builds/{bid}.build"
    if write:
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    return ("written", f"{bid}: {'wrote' if write else 'valid'} {rel}")


def run(check):
    builds = sorted(
        (p for p in BUILDS_DIR.glob("*.json") if p.name != "schema.json"),
        key=lambda p: p.name,
    )
    passive_tree = load_json(PASSIVE_TREE_PATH) if PASSIVE_TREE_PATH.exists() else None
    valid_gem_ids = community_gem_ids()

    enabled, written, refused = 0, 0, 0
    mode = "check" if check else "export"
    gem_note = f"{len(valid_gem_ids)} community gem ids loaded" if valid_gem_ids else "no community gem dataset (id check skipped)"
    print(f"Build exporter ({mode} mode): scanning {len(builds)} build file(s); {gem_note}\n")
    for path in builds:
        build = load_json(path)
        if build.get("build_file", {}).get("enabled"):
            enabled += 1
        status, msg = export_build(build, passive_tree, write=not check, valid_gem_ids=valid_gem_ids)
        if status == "written":
            written += 1
            print(f"OK    {msg}")
        elif status == "refused":
            refused += 1
            print(f"FAIL  {msg}")
        else:
            print(f"--    {msg}")

    print()
    if refused:
        print(f"EXPORT FAILED: {refused} enabled build(s) could not produce a valid .build.")
        return 1
    if enabled == 0:
        print(
            "No builds have build_file.enabled=true. Nothing to export.\n"
            "This is the expected 'cleanly disabled' state until verified skill-gem "
            "ids exist (GGG publishes no official gem export); the site UI says the "
            "import file is not yet available."
        )
        return 0
    print(f"EXPORT OK: {written} build(s) {'validated' if check else 'written'} to assets/builds/.")
    return 0


# --------------------------------------------------------------------------- #
# Built-in tests (happy path + refusal), runnable without third-party deps.
# --------------------------------------------------------------------------- #
def selftest():
    fake_tree = {
        "ascendancies": [{"class": "Sorceress", "code": "Sorceress1", "name": "Stormweaver"}],
        "node_ids": ["12345"],
        "semantic_node_ids": ["fire10"],
    }
    base = {
        "id": "t",
        "name": "Test Build",
        "ascendancy": "Stormweaver",
        "skills": [
            {
                "name": "Main",
                "gem_id": "Metadata/Items/Gems/SkillGemFireball",
                "note": "Aim it.",
                "supports": [
                    {"name": "Added", "gem_id": "Metadata/Items/Gems/SupportGemAdded", "note": "n"},
                    {"name": "Cast", "gem_id": "Metadata/Items/Gems/SupportGemCastSpeed"},
                ],
            }
        ],
        "passive_milestones": [{"stage": "x", "goal": "y", "node_ids": ["fire10"]}],
        "gear_slots": {
            "weapon": {"base": "Wand", "priority": ["spell damage", "cast speed"], "budget_note": "cheap"},
            "ring_1": {"base": "Any ring", "priority": ["resistances"]},
        },
    }
    failures = []

    # Happy path: fully resolved -> valid .build with mapped fields.
    out = build_to_dotbuild(base, fake_tree)
    json.loads(json.dumps(out))  # serializable
    checks = [
        (out["name"] == "Test Build", "name mapped"),
        (out["ascendancy"] == "Sorceress1", "ascendancy name->code"),
        (out["passives"] == ["fire10"], "passives carried + validated"),
        (out["skills"][0]["id"] == "Metadata/Items/Gems/SkillGemFireball", "skill gem id"),
        (out["skills"][0]["support_skills"][0]["id"].endswith("SupportGemAdded"), "support obj form"),
        (out["skills"][0]["support_skills"][1].endswith("SupportGemCastSpeed"), "support str form"),
        (out["inventory_slots"][0]["inventory_id"] == "Weapon1", "weapon->Weapon1"),
        (out["inventory_slots"][1]["inventory_id"] == "Ring1", "ring_1->Ring1"),
        ("Stat Priority" in out["inventory_slots"][0]["additional_text"], "slot priority text"),
    ]
    for ok, label in checks:
        if not ok:
            failures.append(f"happy-path: {label}")

    # Refusal cases.
    def expect_refuse(mutate, label):
        b = json.loads(json.dumps(base))
        mutate(b)
        try:
            build_to_dotbuild(b, fake_tree)
            failures.append(f"should refuse: {label}")
        except ExportRefused:
            pass

    expect_refuse(lambda b: b["skills"][0].update(gem_id=TBD), "TBD skill gem id")
    expect_refuse(lambda b: b["skills"][0]["supports"][0].update(gem_id=TBD), "TBD support gem id")
    expect_refuse(lambda b: b.update(ascendancy=TBD), "TBD ascendancy")
    expect_refuse(lambda b: b.update(ascendancy="Not An Ascendancy"), "unknown ascendancy")
    expect_refuse(
        lambda b: b["passive_milestones"][0].update(node_ids=["99999"]), "node id not in tree"
    )

    # Community gem-id membership: a non-TBD id absent from the dataset is refused.
    known = {
        "Metadata/Items/Gems/SkillGemFireball",
        "Metadata/Items/Gems/SupportGemAdded",
        "Metadata/Items/Gems/SupportGemCastSpeed",
    }
    try:
        build_to_dotbuild(base, fake_tree, valid_gem_ids=known)  # all known -> ok
    except ExportRefused as exc:
        failures.append(f"membership: rejected a known id set ({exc})")
    bad = json.loads(json.dumps(base))
    bad["skills"][0]["gem_id"] = "Metadata/Items/Gems/SkillGemDefinitelyFake"
    try:
        build_to_dotbuild(bad, fake_tree, valid_gem_ids=known)
        failures.append("should refuse: gem id not in community dataset")
    except ExportRefused:
        pass

    if failures:
        print("SELFTEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SELFTEST PASSED: mapping + refusal behavior verified.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate only; do not write files (CI gate).")
    parser.add_argument("--selftest", action="store_true", help="Run built-in mapping/refusal tests.")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    return run(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
