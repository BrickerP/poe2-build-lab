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

import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
BUILDS_DIR = ROOT / "data" / "builds"
SCHEMA_PATH = BUILDS_DIR / "schema.json"
OFFICIAL_DIR = ROOT / "data" / "official"
MANIFEST_PATH = OFFICIAL_DIR / "manifest.json"
COMMUNITY_DIR = ROOT / "data" / "community"
COMMUNITY_MANIFEST_PATH = COMMUNITY_DIR / "manifest.json"
COMMUNITY_SKILL_GEMS_PATH = COMMUNITY_DIR / "skill-gems.json"
COMMUNITY_SUPPORT_GEMS_PATH = COMMUNITY_DIR / "support-gems.json"

TBD = "TBD"
DEFAULT_REVIEW_WINDOW_DAYS = 45
OFFICIAL_TRADE_HOST = "www.pathofexile.com"
OFFICIAL_TRADE_LANDING_PATH = "/trade2"
OFFICIAL_POE2_TRADE_PATH = "/trade2/search/poe2/"

# Reviewed immutable upstream snapshot. Updating the passive tree requires
# independently verifying a new GGG commit and changing this trust anchor in
# code review; editing the data file and manifest together is not sufficient.
PASSIVE_TREE_TRUSTED_SNAPSHOT = {
    "source_repo": "grindinggear/poe2-skilltree-export",
    "source_commit": "1e9eb2d8c1946398c3aaaacfbaead5c75c0d1fa6",
    "source_path": "data.json",
    "source_url": (
        "https://raw.githubusercontent.com/grindinggear/poe2-skilltree-export/"
        "1e9eb2d8c1946398c3aaaacfbaead5c75c0d1fa6/data.json"
    ),
    "source_commit_url": (
        "https://github.com/grindinggear/poe2-skilltree-export/commit/"
        "1e9eb2d8c1946398c3aaaacfbaead5c75c0d1fa6"
    ),
    "source_commit_subject": "0.5.2",
    "source_blob_git_sha1": "65986cb127f51e73ff691d01b1c7289f8d7e5def",
    "raw_sha256": "f83c94ce7b09f2bfc5b3b1d63523c2ab3d2582d0e964f6aeec34b8b0390abcfe",
    "normalized_sha256": "b1bc8b023bd922adf156fe29eb20c96c313e0239f1942abe0f70d2ea77285c42",
    "raw_tree_name": "Default",
}

PASSIVE_TREE_SOURCE_FIELDS = tuple(PASSIVE_TREE_TRUSTED_SNAPSHOT)
PASSIVE_TREE_COUNT_FIELDS = {
    "raw_node_record_count": ("nodes", dict),
    "group_count": ("groups", dict),
    "edge_count": ("edges", list),
    "skill_override_count": ("skillOverrides", dict),
    "jewel_slot_count": ("jewelSlots", list),
}


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_blob_sha1(path):
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


def _resolve_manifest_path(root, dataset_type, field, value, errors):
    label = f"official manifest {dataset_type}.{field}"
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty repository-relative path")
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        errors.append(f"{label} must be repository-relative, got {value!r}")
        return None
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    if not resolved.is_relative_to(resolved_root):
        errors.append(f"{label} escapes repository root: {value!r}")
        return None
    if not resolved.is_file():
        errors.append(f"{label} does not exist as a file: {value!r}")
        return None
    return resolved


def _load_provenance_json(path, label, errors):
    try:
        return load_json(path)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        errors.append(f"{label} is not valid JSON: {exc}")
    except OSError as exc:
        errors.append(f"{label} could not be read: {exc}")
    return None


def _normalization_extractors():
    try:
        from scripts.normalize_official_data import (
            extract_ascendancies,
            extract_classes,
            extract_node_ids,
        )
    except ModuleNotFoundError:
        from normalize_official_data import (  # type: ignore[no-redef]
            extract_ascendancies,
            extract_classes,
            extract_node_ids,
        )
    return extract_node_ids, extract_classes, extract_ascendancies


def validate_passive_tree_source_contract(
    dataset, trusted_snapshot=PASSIVE_TREE_TRUSTED_SNAPSHOT
):
    """Validate immutable upstream identity separately from local file state."""
    errors = []
    if not isinstance(dataset, dict):
        return ["official manifest passive-tree dataset must be an object"]
    for field in PASSIVE_TREE_SOURCE_FIELDS:
        expected = trusted_snapshot.get(field)
        if field not in dataset:
            errors.append(f"official manifest passive-tree missing required {field}")
        elif dataset[field] != expected:
            errors.append(
                f"official manifest passive-tree {field} is not the reviewed immutable "
                f"upstream value: expected {expected!r}, got {dataset[field]!r}"
            )
    return errors


def validate_passive_tree_raw_payload(raw, dataset):
    """Validate the pinned export's schema and recorded raw structure."""
    errors = []
    if not isinstance(raw, dict):
        return ["passive-tree local_raw must contain a JSON object"]

    if raw.get("tree") != dataset.get("raw_tree_name"):
        errors.append(
            "official manifest passive-tree raw_tree_name mismatch: "
            f"recorded {dataset.get('raw_tree_name')!r}, raw export {raw.get('tree')!r}"
        )

    for field, (raw_field, expected_type) in PASSIVE_TREE_COUNT_FIELDS.items():
        value = raw.get(raw_field)
        if not isinstance(value, expected_type):
            errors.append(
                f"passive-tree local_raw {raw_field} must be a {expected_type.__name__}"
            )
            continue
        recorded = dataset.get(field)
        actual = len(value)
        if not isinstance(recorded, int) or isinstance(recorded, bool) or recorded < 0:
            errors.append(
                f"official manifest passive-tree {field} must be a non-negative integer"
            )
        elif recorded != actual:
            errors.append(
                f"official manifest passive-tree {field} mismatch: "
                f"recorded {recorded!r}, derived {actual}"
            )
    return errors


def validate_passive_tree_source_catalog(dataset, root=ROOT):
    """Keep the public source catalog bound to the reviewed manifest snapshot."""
    errors = []
    path = root / "data" / "sources" / "official-links.json"
    if not path.is_file():
        return ["data/sources/official-links.json does not exist"]
    catalog = _load_provenance_json(path, "official source catalog", errors)
    if not isinstance(catalog, dict):
        if catalog is not None:
            errors.append("official source catalog must contain a JSON object")
        return errors
    sources = catalog.get("sources")
    matches = (
        [
            source
            for source in sources
            if isinstance(source, dict)
            and source.get("id") == "ggg-passive-tree-export"
        ]
        if isinstance(sources, list)
        else []
    )
    if len(matches) != 1:
        errors.append(
            "official source catalog must contain exactly one "
            f"ggg-passive-tree-export entry, found {len(matches)}"
        )
        return errors
    source = matches[0]
    expected = {
        "url": f"https://github.com/{dataset.get('source_repo')}",
        "source_commit": dataset.get("source_commit"),
        "source_path": dataset.get("source_path"),
        "raw_data_url": dataset.get("source_url"),
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(
                f"official source catalog ggg-passive-tree-export.{field} mismatch: "
                f"expected {value!r}, got {source.get(field)!r}"
            )
    return errors


def validate_official_manifest_provenance(
    manifest, root=ROOT, trusted_snapshot=PASSIVE_TREE_TRUSTED_SNAPSHOT
):
    """Prove every local manifest resource and the passive-tree derivation.

    SHA-256 checks bind the manifest to committed bytes. The deterministic
    comparison reconstructs every normalized field derived from the raw GGG
    export; ``generated_at`` is retained from the committed artifact because it
    records snapshot production time rather than raw source content.
    """
    errors = []
    if not isinstance(manifest, dict):
        return ["data/official/manifest.json must contain a JSON object"]
    datasets = manifest.get("datasets")
    if not isinstance(datasets, list):
        return ["data/official/manifest.json datasets must be an array"]

    local_paths = {}
    for index, dataset in enumerate(datasets):
        if not isinstance(dataset, dict):
            errors.append(f"official manifest datasets[{index}] must be an object")
            continue
        dataset_type = dataset.get("type") or f"datasets[{index}]"
        for field, value in dataset.items():
            if field.startswith("local_"):
                local_paths[(index, field)] = _resolve_manifest_path(
                    root, dataset_type, field, value, errors
                )

    passive_entries = [
        (index, dataset)
        for index, dataset in enumerate(datasets)
        if isinstance(dataset, dict) and dataset.get("type") == "passive-tree"
    ]
    if len(passive_entries) != 1:
        errors.append(
            "official manifest must contain exactly one passive-tree dataset, "
            f"found {len(passive_entries)}"
        )
        return errors

    index, dataset = passive_entries[0]
    if dataset.get("coverage") != "complete":
        errors.append(
            "official manifest passive-tree coverage must be 'complete' for "
            "published build validation"
        )

    errors.extend(validate_passive_tree_source_contract(dataset, trusted_snapshot))
    errors.extend(validate_passive_tree_source_catalog(dataset, root))

    required_metadata = (
        "local_raw",
        "local_normalized",
        "raw_sha256",
        "normalized_sha256",
        "raw_node_record_count",
        "node_count",
        "semantic_node_count",
        "class_count",
        "ascendancy_count",
        *PASSIVE_TREE_COUNT_FIELDS,
    )
    for field in required_metadata:
        if field not in dataset:
            errors.append(f"official manifest passive-tree missing required {field}")

    raw_path = local_paths.get((index, "local_raw"))
    normalized_path = local_paths.get((index, "local_normalized"))
    if not raw_path or not normalized_path:
        return errors

    for field, path in (("raw_sha256", raw_path), ("normalized_sha256", normalized_path)):
        recorded = dataset.get(field)
        if not isinstance(recorded, str) or not re.fullmatch(r"[0-9a-f]{64}", recorded):
            errors.append(f"official manifest passive-tree {field} must be 64 lowercase hex digits")
        else:
            actual = _sha256(path)
            if actual != recorded:
                errors.append(
                    f"official manifest passive-tree {field} mismatch: "
                    f"recorded {recorded}, actual {actual}"
                )

    recorded_blob = dataset.get("source_blob_git_sha1")
    if isinstance(recorded_blob, str) and re.fullmatch(r"[0-9a-f]{40}", recorded_blob):
        actual_blob = _git_blob_sha1(raw_path)
        if actual_blob != recorded_blob:
            errors.append(
                "official manifest passive-tree source_blob_git_sha1 mismatch: "
                f"recorded {recorded_blob}, actual {actual_blob}"
            )

    raw = _load_provenance_json(raw_path, "passive-tree local_raw", errors)
    normalized = _load_provenance_json(
        normalized_path, "passive-tree local_normalized", errors
    )
    if not isinstance(raw, dict) or not isinstance(normalized, dict):
        if raw is not None and not isinstance(raw, dict):
            errors.append("passive-tree local_raw must contain a JSON object")
        if normalized is not None and not isinstance(normalized, dict):
            errors.append("passive-tree local_normalized must contain a JSON object")
        return errors

    errors.extend(validate_passive_tree_raw_payload(raw, dataset))
    raw_nodes = raw.get("nodes")
    if not isinstance(raw_nodes, dict):
        return errors

    extract_node_ids, extract_classes, extract_ascendancies = _normalization_extractors()
    node_ids, semantic_node_ids = extract_node_ids(raw)
    classes = extract_classes(raw)
    ascendancies = extract_ascendancies(raw)
    raw_node_record_count = len(raw_nodes)

    derived_counts = {
        "raw_node_record_count": raw_node_record_count,
        "node_count": len(node_ids),
        "semantic_node_count": len(semantic_node_ids),
        "class_count": len(classes),
        "ascendancy_count": len(ascendancies),
    }
    for field, actual in derived_counts.items():
        recorded = dataset.get(field)
        if not isinstance(recorded, int) or isinstance(recorded, bool) or recorded < 0:
            errors.append(
                f"official manifest passive-tree {field} must be a non-negative integer"
            )
        elif recorded != actual:
            errors.append(
                f"official manifest passive-tree {field} mismatch: "
                f"recorded {recorded!r}, derived {actual}"
            )

    known_gaps = []
    if not node_ids:
        known_gaps.append("No passive node ids extracted; export schema may differ from expectations.")
    if not classes:
        known_gaps.append("No class base-attribute metadata extracted.")
    if not ascendancies:
        known_gaps.append("No ascendancy code/name mapping extracted.")
    expected = {
        "generated_at": normalized.get("generated_at"),
        "source": dataset.get("local_raw"),
        "patch_version": raw.get("tree", "unknown"),
        "node_count": len(node_ids),
        "semantic_node_count": len(semantic_node_ids),
        "classes": classes,
        "ascendancies": ascendancies,
        "node_ids": node_ids,
        "semantic_node_ids": semantic_node_ids,
        "known_gaps": known_gaps,
    }
    if normalized != expected:
        errors.append(
            "passive-tree local_normalized does not deterministically match local_raw"
        )
    return errors


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
    """Yield (label, value, category) for every field that must hold an exact id.

    Categories drive the published-build gate (see business_rules):

    - ``gem``       skill/support gem ids. Rendered by archetype name, never as an
                    exact id, and consumed only by the .build exporter, which is
                    independently gated by build_file.enabled. Per doc 14 release
                    sequence item 5 ("Publish Build Cards without .build export if
                    IDs are not ready"), these may stay TBD on a published card.
    - ``ascendancy`` rendered on the page and required by .build export; must be
                    resolved and verified against official data to publish.
    - ``node``      passive node ids. Optional; when present they assert exact
                    tree placement and must be real official ids.
    - ``base``      gear base-item ids. Optional; when present they assert an
                    exact base and require a non-missing base-items dataset.
    """
    yield ("ascendancy", build.get("ascendancy"), "ascendancy")
    for i, skill in enumerate(build.get("skills", [])):
        yield (f"skills[{i}].gem_id", skill.get("gem_id"), "gem")
        for j, sup in enumerate(skill.get("supports", [])):
            yield (f"skills[{i}].supports[{j}].gem_id", sup.get("gem_id"), "gem")
    for slot_name, slot in build.get("gear_slots", {}).items():
        if "base_item_id" in slot:
            yield (f"gear_slots.{slot_name}.base_item_id", slot.get("base_item_id"), "base")
    for i, milestone in enumerate(build.get("passive_milestones", [])):
        for j, node in enumerate(milestone.get("node_ids", [])):
            yield (f"passive_milestones[{i}].node_ids[{j}]", node, "node")


def dataset_coverage(manifest, dataset_type):
    if not manifest:
        return None
    for ds in manifest.get("datasets", []):
        if ds.get("type") == dataset_type:
            return ds.get("coverage")
    return None


def manifest_passive_tree_complete(manifest):
    return dataset_coverage(manifest, "passive-tree") == "complete"


def official_ascendancies(passive_tree):
    """Return the set of valid ascendancy names + codes from official data."""
    valid = set()
    if not passive_tree:
        return valid
    for asc in passive_tree.get("ascendancies", []):
        if asc.get("name"):
            valid.add(asc["name"])
        if asc.get("code"):
            valid.add(asc["code"])
    return valid


def official_node_ids(passive_tree):
    if not passive_tree:
        return set()
    return set(passive_tree.get("node_ids", [])) | set(passive_tree.get("semantic_node_ids", []))


def load_community_gem_ids():
    """Set of real gem metadata ids from the community datasets (empty if absent)."""
    ids = set()
    for path in (COMMUNITY_SKILL_GEMS_PATH, COMMUNITY_SUPPORT_GEMS_PATH):
        if path.exists():
            for item in load_json(path).get("items", []):
                if item.get("id"):
                    ids.add(item["id"])
    return ids


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def is_official_trade_url(value):
    if not isinstance(value, str) or value != value.strip():
        return False
    try:
        parts = urlsplit(value)
    except ValueError:
        return False
    if (
        parts.scheme != "https"
        or parts.netloc != OFFICIAL_TRADE_HOST
        or parts.query
        or parts.fragment
    ):
        return False
    path = unquote(parts.path)
    if "\\" in path or any(segment in {".", ".."} for segment in path.split("/")):
        return False
    return path == OFFICIAL_TRADE_LANDING_PATH or path.startswith(
        OFFICIAL_POE2_TRADE_PATH
    )


def business_rules(build, manifest, passive_tree, community_manifest, community_gem_ids, errors):
    status = build.get("status")
    published = status == "published"

    exact_ids = list(collect_exact_ids(build))
    valid_asc = official_ascendancies(passive_tree)
    valid_nodes = official_node_ids(passive_tree)

    # No fabricated gem ids: any non-TBD skill/support gem id must exist in the
    # community gem datasets. Applies to every build (draft or published) so a
    # typo'd id can never reach an export-enabled card.
    if community_gem_ids:
        for label, value, cat in exact_ids:
            if cat == "gem" and value and value != TBD and value not in community_gem_ids:
                errors.append(
                    f"{label}={value!r} is not a known community gem id "
                    "(data/community/skill-gems.json / support-gems.json)"
                )

    # Published-build TBD policy (doc 14 build-data rules + release sequence item 5):
    #   - ascendancy is rendered and required by export -> must resolve AND match
    #     official data; a missing ascendancy dataset cannot back a published claim.
    #   - node ids / base ids are optional, but when present they assert exact
    #     mechanics and must be real (and base ids need a non-missing dataset).
    #   - skill/support gem ids may remain TBD: the card renders skills by name
    #     and the only consumer (.build export) is gated by build_file.enabled.
    if published:
        for label, value, cat in exact_ids:
            if cat == "ascendancy":
                if value == TBD or not value:
                    errors.append(
                        f"published build has unresolved {label} (TBD); resolve it from "
                        "official data before publishing"
                    )
                elif valid_asc and value not in valid_asc:
                    errors.append(
                        f"published build {label}={value!r} is not a known official "
                        "ascendancy name/code in data/official/passive-tree.json"
                    )
                elif not valid_asc:
                    errors.append(
                        f"published build asserts {label}={value!r} but official "
                        "ascendancy data is unavailable to verify it"
                    )
            elif cat == "node":
                if value == TBD:
                    errors.append(f"published build has TBD passive node id at {label}")
                elif valid_nodes and value not in valid_nodes:
                    errors.append(
                        f"published build {label}={value!r} is not a known official passive node id"
                    )
            elif cat == "base":
                if value == TBD:
                    errors.append(f"published build has TBD base-item id at {label}")
                elif dataset_coverage(community_manifest, "base-items") != "present":
                    errors.append(
                        f"published build asserts exact {label}={value!r} but the "
                        "community base-items dataset is not marked coverage='present'"
                    )

    # .build export must never ship placeholder ids, regardless of status.
    build_file = build.get("build_file", {})
    if build_file.get("enabled"):
        tbd_hits = [label for label, value, _ in exact_ids if value == TBD]
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
        for ds_type in ("skill-gems", "support-gems"):
            if dataset_coverage(community_manifest, ds_type) != "present":
                errors.append(
                    f"build_file.enabled=true but community {ds_type} dataset is not "
                    "marked coverage='present' in data/community/manifest.json"
                )
        asc = build.get("ascendancy")
        if valid_asc and asc not in valid_asc:
            errors.append(
                f"build_file.enabled=true but ascendancy {asc!r} is not a known official ascendancy"
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
        if "trade_url" in flt and not is_official_trade_url(flt.get("trade_url")):
            errors.append(
                f"trade_handoff.filters[{i}].trade_url must use "
                "https://www.pathofexile.com/trade2 or an official "
                "/trade2/search/poe2/ path"
            )
        if flt.get("approx_price") and not flt.get("checked_at"):
            errors.append(
                f"trade_handoff.filters[{i}] has approx_price without checked_at"
            )

    # Published builds: expanded gear guidance (Phase 4) on core slots.
    if published:
        core_slots = (
            "weapon", "body_armour", "helmet", "gloves", "boots",
            "belt", "amulet", "ring_1", "ring_2",
        )
        for slot in core_slots:
            data = build.get("gear_slots", {}).get(slot)
            if not data:
                errors.append(f"published build missing gear_slots.{slot}")
                continue
            for field in (
                "required_affixes", "good_affixes", "luxury_affixes",
                "campaign_target", "early_maps_target",
            ):
                if not data.get(field):
                    errors.append(
                        f"published build gear_slots.{slot} missing {field}"
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
    provenance_errors = []
    manifest = None
    if not MANIFEST_PATH.exists():
        provenance_errors.append("data/official/manifest.json does not exist")
    else:
        try:
            manifest = load_json(MANIFEST_PATH)
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            provenance_errors.append(f"data/official/manifest.json is not valid JSON: {exc}")
    if manifest is not None:
        provenance_errors.extend(validate_official_manifest_provenance(manifest, ROOT))

    trusted_manifest = manifest if not provenance_errors else None
    passive_tree = None
    if trusted_manifest:
        passive_dataset = next(
            ds
            for ds in trusted_manifest["datasets"]
            if ds.get("type") == "passive-tree"
        )
        passive_tree = load_json(ROOT / passive_dataset["local_normalized"])
    community_manifest = load_json(COMMUNITY_MANIFEST_PATH) if COMMUNITY_MANIFEST_PATH.exists() else None
    community_gem_ids = load_community_gem_ids()

    build_paths = sorted(p for p in BUILDS_DIR.glob("*.json") if p.name != "schema.json")
    if not build_paths:
        if provenance_errors:
            for error in provenance_errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("No build files found in data/builds/ (only schema.json). Provenance validated.")
        return 0

    total_errors = len(provenance_errors)
    seen_ids = {}
    if provenance_errors:
        print(f"FAIL  official passive-tree provenance ({len(provenance_errors)} error(s)):")
        for error in provenance_errors:
            print(f"      - {error}")
        print()
    else:
        print("PASS  official passive-tree provenance (paths, hashes, counts, normalization)\n")
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
            business_rules(
                build,
                trusted_manifest,
                passive_tree,
                community_manifest,
                community_gem_ids,
                errors,
            )

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
        print(f"VALIDATION FAILED: {total_errors} error(s) across provenance/build checks.")
        return 1
    print(f"VALIDATION PASSED: {len(build_paths)} build(s) OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
