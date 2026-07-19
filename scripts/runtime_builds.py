#!/usr/bin/env python3
"""Select and validate the build JSON files required by browser tools."""

from __future__ import annotations

import json
from pathlib import Path

from validate_builds import validate_against_schema


class RuntimeBuildError(ValueError):
    """A build cannot safely cross the public runtime-data boundary."""


def published_runtime_builds(source_root: Path) -> list[Path]:
    """Return the exact schema-valid published build files, in stable order."""
    builds_dir = source_root / "data" / "builds"
    schema_path = builds_dir / "schema.json"
    if not schema_path.is_file():
        raise RuntimeBuildError(f"runtime build schema missing: {schema_path}")

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeBuildError(f"invalid runtime build schema: {exc}") from exc

    published: list[Path] = []
    for path in sorted(builds_dir.glob("*.json")):
        if path.name == "schema.json":
            continue
        try:
            build = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeBuildError(f"{path.name}: invalid JSON: {exc}") from exc
        errors: list[str] = []
        validate_against_schema(build, schema, schema, "", errors)
        if errors:
            raise RuntimeBuildError(
                f"{path.name}: runtime build does not match schema: " + "; ".join(errors)
            )
        if build.get("id") != path.stem:
            raise RuntimeBuildError(
                f"{path.name}: runtime build id {build.get('id')!r} does not match filename"
            )
        if build.get("status") == "published":
            published.append(path)
    if not published:
        raise RuntimeBuildError("no schema-valid published runtime builds found")
    return published


def runtime_dist_paths(source_root: Path) -> set[str]:
    return {
        path.relative_to(source_root).as_posix()
        for path in published_runtime_builds(source_root)
    }
