#!/usr/bin/env python3
"""Shared, exact contract for the self-hosted stylesheet font faces."""

from __future__ import annotations

import re

LATIN_UNICODE_RANGE = (
    "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, "
    "U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, "
    "U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
)

FONT_FACE_CONTRACT = {
    '"Source Sans 3"': {
        "font-family": '"Source Sans 3"',
        "font-style": "normal",
        "font-weight": "400 700",
        "font-display": "swap",
        "src": 'url("assets/fonts/source-sans-3-latin-variable.woff2") format("woff2")',
        "unicode-range": LATIN_UNICODE_RANGE,
    },
    '"Libre Baskerville"': {
        "font-family": '"Libre Baskerville"',
        "font-style": "normal",
        "font-weight": "400 700",
        "font-display": "swap",
        "src": 'url("assets/fonts/libre-baskerville-latin-variable.woff2") format("woff2")',
        "unicode-range": LATIN_UNICODE_RANGE,
    },
}

FONT_FACE_TOKEN_RE = re.compile(r"@font-face\b", re.IGNORECASE)
FONT_FACE_BLOCK_RE = re.compile(r"@font-face\s*\{([^{}]*)\}", re.IGNORECASE | re.DOTALL)
DECLARATION_RE = re.compile(r"([-\w]+)\s*:\s*([^;{}]+)\s*;", re.DOTALL)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def strip_css_comments(css: str) -> tuple[str, str | None]:
    """Remove comments outside strings and reject structurally invalid CSS text."""
    output: list[str] = []
    index = 0
    quote: str | None = None
    while index < len(css):
        character = css[index]
        if quote is not None:
            output.append(character)
            if character == "\\":
                index += 1
                if index >= len(css):
                    return "".join(output), "unterminated CSS string escape"
                output.append(css[index])
            elif character == quote:
                quote = None
            elif character in "\r\n\f":
                return "".join(output), "unterminated CSS string"
            index += 1
            continue

        if character in {'"', "'"}:
            quote = character
            output.append(character)
            index += 1
            continue
        if css.startswith("/*", index):
            end = css.find("*/", index + 2)
            if end < 0:
                return "".join(output), "unterminated CSS comment"
            index = end + 2
            continue
        if css.startswith("*/", index):
            return "".join(output), "unmatched CSS comment terminator"
        output.append(character)
        index += 1

    if quote is not None:
        return "".join(output), "unterminated CSS string"
    return "".join(output), None


def validate_font_face_contract(css: str, *, label: str = "styles.css") -> list[str]:
    """Validate effective (comment-free) CSS against the exact two-face contract."""
    errors: list[str] = []
    effective, scan_error = strip_css_comments(css)
    if scan_error:
        return [f"{label}: {scan_error}"]

    tokens = FONT_FACE_TOKEN_RE.findall(effective)
    blocks = FONT_FACE_BLOCK_RE.findall(effective)
    if len(tokens) != len(blocks):
        errors.append(f"{label}: malformed @font-face block")
    if len(blocks) != len(FONT_FACE_CONTRACT):
        errors.append(
            f"{label}: expected exactly {len(FONT_FACE_CONTRACT)} effective @font-face blocks; "
            f"found {len(blocks)}"
        )

    actual_by_family: dict[str, dict[str, str]] = {}
    for index, block in enumerate(blocks, start=1):
        declarations: dict[str, str] = {}
        for match in DECLARATION_RE.finditer(block):
            name = match.group(1).lower()
            if name in declarations:
                errors.append(f"{label}: @font-face #{index} repeats descriptor {name!r}")
            declarations[name] = _normalize(match.group(2))
        remainder = DECLARATION_RE.sub("", block).strip()
        if remainder:
            errors.append(f"{label}: @font-face #{index} has malformed declaration content")
        family = declarations.get("font-family")
        if family is None:
            errors.append(f"{label}: @font-face #{index} is missing effective font-family")
            continue
        if family in actual_by_family:
            errors.append(f"{label}: duplicate @font-face contract for {family}")
        actual_by_family[family] = declarations

    for family, expected in FONT_FACE_CONTRACT.items():
        actual = actual_by_family.get(family)
        if actual is None:
            errors.append(f"{label}: missing effective @font-face contract for {family}")
            continue
        if actual != expected:
            missing = sorted(expected.keys() - actual.keys())
            extra = sorted(actual.keys() - expected.keys())
            mismatched = sorted(
                key for key in expected.keys() & actual.keys() if expected[key] != actual[key]
            )
            details = []
            if missing:
                details.append("missing " + ", ".join(missing))
            if extra:
                details.append("unexpected " + ", ".join(extra))
            if mismatched:
                details.append("mismatched " + ", ".join(mismatched))
            errors.append(
                f"{label}: @font-face contract for {family} differs: " + "; ".join(details)
            )

    for family in sorted(actual_by_family.keys() - FONT_FACE_CONTRACT.keys()):
        errors.append(f"{label}: unexpected @font-face family {family}")
    return errors
