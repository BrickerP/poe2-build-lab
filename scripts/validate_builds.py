#!/usr/bin/env python3
"""Validate PoE2 Build Lab build cards.

This is the test layer for the build data contract defined in
docs/research/14-development-implementation-plan.md.

It does two things:

1. Structural validation against data/builds/schema.json using a small
   JSON-Schema subset interpreter (no third-party dependencies, so it runs on a
   bare ``python3`` in CI).
2. Business-rule validation that JSON Schema cannot express: draft/published
   TBD policy, .build export safety, Spirit gating, gear-swap slot integrity,
   trade-price provenance, and patch review-window staleness.

Exit code is non-zero if any build fails, so it doubles as a CI/PR gate.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDS_DIR = ROOT / "data" / "builds"
SCHEMA_PATH = BUILDS_DIR / "schema.json"
MANIFEST_PATH = ROOT / "data" / "official" / "manifest.json"

TBD = "TBD"
DEFAULT_REVIEW_WINDOW_DAYS = 45

# Fields whose values are exact game mechanics. They may stay "TBD" in drafts
# but must be resolved before a build is published.
EXACT_ID_FIELDS_DESC = (
    "ascendancy, skill gem ids, support gem ids, gear base item ids, passive node ids"
)


# --------------------------------------------------------------------------- #
# Minimal JSON Schema (draft-07 subset) validator
# --------------------------------------------------------------------------- #
class SchemaError(Exception):
    pass


def _resolve_ref(root_schema, ref):
    if not ref.startswith("#/"):
        raise SchemaError(f"Unsupported $ref: {ref}")
    node = root_schema
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def validate_against_schema(instance, schema, root_schema, path, errors):
    if "$ref" in schema:
        schema = _resolve_ref(root_schema, schema["$ref"])

    expected_type = schema.get("type")
    if expected_type and not _check_type(instance, expected_type):
        errors.append(f"{path or '<root>'}: expected type {expected_type}, got {_typename(instance)}")
        return  # further checks are meaningless against the wrong type

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path or '<root>'}: value {instance!r} not in allowed {schema['enum']}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength {schema['minLength']}")
        pattern = schema.get("pattern")
        if pattern and not re.search(pattern, instance):
            errors.append(f"{path}: {instance!r} does not match pattern {pattern}")

    if isinstance(instance, bool):
        # bool is a subclass of int; guard before numeric checks
        pass
    elif isinstance(instance, (int, float)):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} above maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                validate_against_schema(item, item_schema, root_schema, f"{path}[{i}]", errors)

    if isinstance(instance, dict):
        if "minProperties" in schema and len(instance) < schema["minProperties"]:
            errors.append(f"{path or '<root>'}: fewer than minProperties {schema['minProperties']}")
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path or '<root>'}: missing required field '{req}'")
        props = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = f"{path}.{key}" if path else key
            if key in props:
                validate_against_schema(value, props[key], root_schema, child_path, errors)
            elif additional is False:
                errors.append(f"{path or '<root>'}: unexpected field '{key}'")
            elif isinstance(additional, dict):
                validate_against_schema(value, additional, root_schema, child_path, errors)


def _check_type(instance, expected):
    types = expected if isinstance(expected, list) else [expected]
    for t in types:
        if t == "object" and isinstance(instance, dict):
            return True
        if t == "array" and isinstance(instance, list):
            return True
        if t == "string" and isinstance(instance, str):
            return True
        if t == "integer" and isinstance(instance, int) and not isinstance(instance, bool):
            return True
        if t == "number" and isinstance(instance, (int, float)) and not isinstance(instance, bool):
            return True
        if t == "boolean" and isinstance(instance, bool):
            return True
        if t == "null" and instance is None:
            return True
    return False


def _typename(instance):
    if isinstance(instance, bool):
        return "boolean"
    if isinstance(instance, str):
        return "string"
    if isinstance(instance, int):
        return "integer"
    if isinstance(instance, float):
        return "number"
    if isinstance(instance, list):
        return "array"
    if isinstance(instance, dict):
        return "object"
    if instance is None:
        return "null"
    return type(instance).__name__


# --------------------------------------------------------------------------- #
# Business rules from doc 14
# --------------------------------------------------------------------------- #
def collect_exact_ids(build):
    """Yield (label, value) for every field that must hold an exact game id."""
    yield ("ascendancy", build.get("ascendancy"))
    for i, skill in enumerate(build.get("skills", [])):
        yield (f"skills[{i}].gem_id", skill.get("gem_id"))
        for j, sup in enumerate(skill.get("supports", [])):
            yield (f"skills[{i}].supports[{j}].gem_id", sup.get("gem_id"))
    for slot_name, slot in build.get("gear_slots", {}).items():
        if "base_item_id" in slot:
            yield (f"gear_slots.{slot_name}.base_item_id", slot.get("base_item_id"))
    for i, milestone in enumerate(build.get("passive_milestones", [])):
        for j, node in enumerate(milestone.get("node_ids", [])):
            yield (f"passive_milestones[{i}].node_ids[{j}]", node)


def manifest_passive_tree_complete(manifest):
    if not manifest:
        return False
    for ds in manifest.get("datasets", []):
        if ds.get("type") == "passive-tree":
            return ds.get("coverage") == "complete"
    return False


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def business_rules(build, manifest, errors):
    status = build.get("status")
    published = status == "published"

    exact_ids = list(collect_exact_ids(build))

    # TBD policy: allowed in drafts, blocked on published exact-mechanics fields.
    if published:
        tbd_hits = [label for label, value in exact_ids if value == TBD]
        if tbd_hits:
            errors.append(
                "published build still has TBD in exact-mechanics fields "
                f"({EXACT_ID_FIELDS_DESC}): {', '.join(tbd_hits)}"
            )

    # .build export must never ship placeholder ids, regardless of status.
    build_file = build.get("build_file", {})
    if build_file.get("enabled"):
        tbd_hits = [label for label, value in exact_ids if value == TBD]
        if tbd_hits:
            errors.append(
                "build_file.enabled=true but exact ids are still TBD: "
                + ", ".join(tbd_hits)
            )
        if not manifest_passive_tree_complete(manifest):
            errors.append(
                "build_file.enabled=true but official passive-tree dataset is not "
                "marked coverage='complete' in data/official/manifest.json"
            )
        if not build_file.get("path"):
            errors.append("build_file.enabled=true but build_file.path is empty")

    # Spirit gating: reservation builds must carry a spirit budget.
    uses_spirit = bool(build.get("uses_spirit"))
    spirit = build.get("spirit_budget")
    if spirit and spirit.get("required", 0) > 0:
        uses_spirit = True
    if uses_spirit and not spirit:
        errors.append("uses Spirit (uses_spirit/spirit required) but spirit_budget is missing")

    # gear_swap_warnings must reference real slots.
    slot_names = set(build.get("gear_slots", {}).keys())
    for i, warn in enumerate(build.get("gear_swap_warnings", [])):
        slot = warn.get("slot")
        if slot not in slot_names:
            errors.append(
                f"gear_swap_warnings[{i}] references slot '{slot}' that is not in gear_slots"
            )

    # Trade handoff: any explicit price needs a check date.
    for i, flt in enumerate(build.get("trade_handoff", {}).get("filters", [])):
        if flt.get("approx_price") and not flt.get("checked_at"):
            errors.append(
                f"trade_handoff.filters[{i}] has approx_price without checked_at"
            )

    # Patch staleness: a published build cannot claim 'current' past its window.
    if published and build.get("review_state") == "current":
        reviewed = parse_date(build.get("last_reviewed"))
        if reviewed:
            window = build.get("review_window_days", DEFAULT_REVIEW_WINDOW_DAYS)
            age = (date.today() - reviewed).days
            if age > window:
                errors.append(
                    f"published build is {age} days past last_reviewed (> {window}d window) "
                    "but review_state is still 'current'; set needs_review or stale"
                )


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def load_json(path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def main():
    if not SCHEMA_PATH.exists():
        print(f"ERROR: schema not found at {SCHEMA_PATH}", file=sys.stderr)
        return 2

    schema = load_json(SCHEMA_PATH)
    manifest = load_json(MANIFEST_PATH) if MANIFEST_PATH.exists() else None

    build_paths = sorted(p for p in BUILDS_DIR.glob("*.json") if p.name != "schema.json")
    if not build_paths:
        print("No build files found in data/builds/ (only schema.json). Nothing to validate.")
        return 0

    total_errors = 0
    seen_ids = {}
    print(f"Validating {len(build_paths)} build file(s) against schema.json\n")

    for path in build_paths:
        errors = []
        try:
            build = load_json(path)
        except json.JSONDecodeError as exc:
            print(f"FAIL  {path.name}: invalid JSON: {exc}")
            total_errors += 1
            continue

        validate_against_schema(build, schema, schema, "", errors)

        # Duplicate id + id/filename consistency.
        build_id = build.get("id")
        if build_id:
            if build_id in seen_ids:
                errors.append(f"duplicate build id '{build_id}' (also in {seen_ids[build_id]})")
            else:
                seen_ids[build_id] = path.name
            if path.stem != build_id:
                errors.append(f"id '{build_id}' does not match filename '{path.stem}'")

        # Only run business rules when the structure is sane enough.
        if isinstance(build, dict):
            business_rules(build, manifest, errors)

        if errors:
            total_errors += len(errors)
            print(f"FAIL  {path.name} ({len(errors)} error(s)):")
            for err in errors:
                print(f"      - {err}")
        else:
            state = f"{build.get('status')}/{build.get('review_state')}"
            print(f"PASS  {path.name}  [{state}]")

    print()
    if total_errors:
        print(f"VALIDATION FAILED: {total_errors} error(s) across builds.")
        return 1
    print(f"VALIDATION PASSED: {len(build_paths)} build(s) OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
