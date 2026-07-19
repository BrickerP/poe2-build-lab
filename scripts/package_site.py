#!/usr/bin/env python3
"""Build a deterministic, allowlisted GitHub Pages artifact in ``dist/``."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

from runtime_builds import published_runtime_builds

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_ROOT = REPO_ROOT / "dist"

ROOT_FILES = (
    "404.html",
    "about.html",
    "ads.txt",
    "contact.html",
    "googlead1eaf93276e5fa5.html",
    "index.html",
    "privacy-policy.html",
    "robots.txt",
    "sitemap.xml",
    "styles.css",
    "assets/favicon.png",
    "assets/social-card.png",
)

TREE_RULES = (
    ("assets/builds", "*.build"),
    ("assets/js", "*.js"),
    ("builds", "**/*.html"),
    ("guides", "**/*.html"),
    ("tools", "**/*.html"),
)


def source_files(source_root: Path = REPO_ROOT) -> list[Path]:
    """Return the complete allowlisted source set, failing on missing essentials."""
    files = [source_root / relative for relative in ROOT_FILES]
    for directory, pattern in TREE_RULES:
        matched = sorted((source_root / directory).glob(pattern))
        if not matched:
            raise FileNotFoundError(f"Allowlisted tree is empty: {directory}/{pattern}")
        files.extend(matched)
    files.extend(published_runtime_builds(source_root))
    missing = [path for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing allowlisted site file(s): "
            + ", ".join(path.relative_to(source_root).as_posix() for path in missing)
        )
    return sorted(set(files), key=lambda path: path.relative_to(source_root).as_posix())


def expected_dist_paths(source_root: Path = REPO_ROOT) -> set[str]:
    paths = {path.relative_to(source_root).as_posix() for path in source_files(source_root)}
    paths.add(".nojekyll")
    return paths


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((item for item in root.rglob("*") if item.is_file())):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def package_site(source_root: Path = REPO_ROOT, dist_root: Path = DIST_ROOT) -> str:
    source_root = source_root.resolve()
    dist_root = dist_root.resolve()
    if dist_root == source_root or dist_root.parent != source_root or dist_root.name != "dist":
        raise ValueError(f"Refusing unsafe dist path: {dist_root}")
    if dist_root.exists():
        shutil.rmtree(dist_root)
    dist_root.mkdir(parents=True)

    for source in source_files(source_root):
        relative = source.relative_to(source_root)
        destination = dist_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
    (dist_root / ".nojekyll").write_bytes(b"")
    return tree_digest(dist_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-deterministic",
        action="store_true",
        help="Package twice and fail unless both artifact content hashes match.",
    )
    args = parser.parse_args()

    first = package_site()
    if args.check_deterministic:
        second = package_site()
        if first != second:
            raise RuntimeError(f"Packaging is not deterministic: {first} != {second}")
        print(f"Deterministic packaging verified: {second}")
    else:
        print(f"Packaged clean Pages artifact: {first}")
    print(f"Files: {len(expected_dist_paths())} -> {DIST_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
