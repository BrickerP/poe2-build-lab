#!/usr/bin/env python3
"""Validate generated site integrity without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

from package_site import REPO_ROOT, expected_dist_paths
from runtime_builds import runtime_dist_paths
from validate_builds import validate_against_schema

SITE_URL = "https://brickerp.github.io/poe2-build-lab/"
SITE_PATH = "/poe2-build-lab/"
SITE_HOST = urlsplit(SITE_URL).netloc
SOCIAL_IMAGE = SITE_URL + "assets/social-card.png"
EXCLUDED_HTML = {"googlead1eaf93276e5fa5.html"}
AD_DOMAINS = (
    "adservice.google.com",
    "doubleclick.net",
    "google-analytics.com",
    "googleadservices.com",
    "googlesyndication.com",
    "googletagmanager.com",
    "googletagservices.com",
)
RESOURCE_ATTRIBUTES = {
    "animate": ("href", "xlink:href"),
    "animatecolor": ("href", "xlink:href"),
    "animatemotion": ("href", "xlink:href"),
    "animatetransform": ("href", "xlink:href"),
    "audio": ("src",),
    "cursor": ("href", "xlink:href"),
    "embed": ("src",),
    "feimage": ("href", "xlink:href"),
    "filter": ("href", "xlink:href"),
    "frame": ("src",),
    "iframe": ("src",),
    "image": ("href", "xlink:href"),
    "img": ("src", "srcset"),
    "input": ("src",),
    "lineargradient": ("href", "xlink:href"),
    "link": ("imagesrcset",),
    "mpath": ("href", "xlink:href"),
    "object": ("data",),
    "pattern": ("href", "xlink:href"),
    "portal": ("src",),
    "radialgradient": ("href", "xlink:href"),
    "set": ("href", "xlink:href"),
    "source": ("src", "srcset"),
    "textpath": ("href", "xlink:href"),
    "track": ("src",),
    "tref": ("href", "xlink:href"),
    "use": ("href", "xlink:href"),
    "video": ("src", "poster"),
}
FORBIDDEN_ATTRIBUTES = {
    ("a", "ping"),
    ("area", "ping"),
    ("applet", "archive"),
    ("applet", "code"),
    ("applet", "codebase"),
    ("applet", "object"),
    ("base", "href"),
    ("bgsound", "src"),
    ("button", "formaction"),
    ("command", "icon"),
    ("form", "action"),
    ("html", "manifest"),
    ("iframe", "srcdoc"),
    ("input", "formaction"),
    ("menuitem", "icon"),
    ("object", "archive"),
    ("object", "classid"),
    ("object", "codebase"),
}
FORBIDDEN_GLOBAL_ATTRIBUTES = {"background"}
FORBIDDEN_META_HTTP_EQUIV = {"refresh"}
CSS_RESOURCE_MARKERS = (
    "url",
    "image(",
    "image-set",
    "@import",
    "http:",
    "https:",
    "//",
    "\\",
)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
CSS_ESCAPE_RE = re.compile(
    r"\\(?:([0-9a-fA-F]{1,6})(?:\r\n|[ \t\r\n\f])?|(\r\n|[\n\r\f])|(.))",
    re.DOTALL,
)
CSS_URL_FUNCTION_RE = re.compile(r"(?<![\w-])url\s*\(", re.IGNORECASE)
SVG_URL_PRESENTATION_ATTRIBUTES = {
    "clip-path",
    "color-profile",
    "cursor",
    "fill",
    "filter",
    "marker",
    "marker-end",
    "marker-mid",
    "marker-start",
    "mask",
    "mask-border-source",
    "mask-image",
    "offset-path",
    "shape-inside",
    "shape-outside",
    "stroke",
}


def normalize_css_escapes(value: str) -> str:
    """Decode CSS escapes before applying URL policy checks."""

    def replace(match: re.Match[str]) -> str:
        hexadecimal, newline, escaped = match.groups()
        if hexadecimal is not None:
            codepoint = int(hexadecimal, 16)
            if codepoint == 0 or codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
                return "\N{REPLACEMENT CHARACTER}"
            return chr(codepoint)
        if newline is not None:
            return ""
        return escaped

    return CSS_ESCAPE_RE.sub(replace, value)


def css_url_references(value: str) -> tuple[list[str], str | None]:
    """Extract normalized CSS url() values, failing closed on malformed syntax."""
    normalized = CSS_COMMENT_RE.sub("", normalize_css_escapes(value))
    references: list[str] = []
    offset = 0
    while match := CSS_URL_FUNCTION_RE.search(normalized, offset):
        cursor = match.end()
        while cursor < len(normalized) and normalized[cursor].isspace():
            cursor += 1
        if cursor >= len(normalized):
            return references, "unterminated url()"

        quote = normalized[cursor] if normalized[cursor] in {'"', "'"} else None
        if quote:
            cursor += 1
            end = normalized.find(quote, cursor)
            if end < 0:
                return references, "unterminated quoted url()"
            reference = normalized[cursor:end]
            cursor = end + 1
            while cursor < len(normalized) and normalized[cursor].isspace():
                cursor += 1
            if cursor >= len(normalized) or normalized[cursor] != ")":
                return references, "unexpected content after quoted url()"
        else:
            end = normalized.find(")", cursor)
            if end < 0:
                return references, "unterminated url()"
            reference = normalized[cursor:end].strip()
            cursor = end

        if not reference:
            return references, "empty url()"
        references.append(reference)
        offset = cursor + 1
    return references, None


def contains_resource_loading_css(value: str) -> bool:
    normalized = CSS_COMMENT_RE.sub("", normalize_css_escapes(value)).lower()
    return any(marker in normalized for marker in CSS_RESOURCE_MARKERS)


def is_local_fragment(reference: str) -> bool:
    parts = urlsplit(reference.strip())
    return not parts.scheme and not parts.netloc and not parts.path and bool(parts.fragment)


def current_patch_metadata() -> tuple[str, str, str]:
    ledger_path = REPO_ROOT / "data" / "sources" / "patch-notes.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    version = ledger.get("current_patch")
    matches = [
        patch for patch in ledger.get("patches", [])
        if isinstance(patch, dict) and patch.get("patch_version") == version
    ]
    if not isinstance(version, str) or not version or len(matches) != 1:
        raise ValueError("patch ledger must identify exactly one current patch entry")
    patch = matches[0]
    patch_date = patch.get("date")
    source_url = patch.get("source_url")
    date.fromisoformat(str(patch_date))
    if not isinstance(source_url, str) or not source_url.startswith("https://"):
        raise ValueError("current patch source_url must be absolute HTTPS")
    return version, patch_date, source_url


def validate_patch_marker(root: Path) -> list[str]:
    try:
        version, patch_date, source_url = current_patch_metadata()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"patch ledger: {exc}"]
    index_path = root / "index.html"
    if not index_path.is_file():
        return ["index.html: missing current patch marker"]
    text = index_path.read_text(encoding="utf-8")
    expected_link = f'href="{source_url}" rel="nofollow noopener">{version}</a>'
    errors = []
    if expected_link not in text:
        errors.append(
            "index.html: current patch marker does not exactly match patch-notes.json"
        )
    readme_path = root / "README.md"
    if readme_path.is_file():
        readme = readme_path.read_text(encoding="utf-8")
        expected_readme = (
            f"The site tracks **{version}** as the latest official patch, posted "
            f"{patch_date} according to the date displayed on the canonical forum thread: "
            f"{source_url}."
        )
        if expected_readme not in readme:
            errors.append(
                "README.md: current patch version/date/source do not exactly match patch-notes.json"
            )
    return errors


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.meta: list[dict[str, str]] = []
        self.links: list[tuple[str, dict[str, str]]] = []
        self.nav_links: list[dict[str, str]] = []
        self._nav_depth = 0
        self.resources: list[tuple[str, str, str]] = []
        self.svg_presentation_values: list[tuple[str, str, str]] = []
        self.duplicate_attributes: list[tuple[str, str]] = []
        self.forbidden_attributes: list[tuple[str, str]] = []
        self.forbidden_meta_directives: list[str] = []
        self.styles: list[dict[str, object]] = []
        self.scripts: list[dict[str, object]] = []
        self._style_index: int | None = None
        self._script_index: int | None = None
        self._svg_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized_attrs = [(key.lower(), value or "") for key, value in attrs]
        seen_attributes: set[str] = set()
        for attribute, _ in normalized_attrs:
            if attribute in seen_attributes:
                self.duplicate_attributes.append((tag, attribute))
            seen_attributes.add(attribute)
        values = dict(normalized_attrs)
        is_svg_script = tag == "script" and self._svg_depth > 0
        if tag == "svg":
            self._svg_depth += 1
        if tag == "nav":
            self._nav_depth += 1
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            self.meta.append(values)
            directive = values.get("http-equiv", "").strip().lower()
            if directive in FORBIDDEN_META_HTTP_EQUIV:
                self.forbidden_meta_directives.append(directive)
        elif tag in {"a", "area", "link"}:
            self.links.append((tag, values))
        elif tag == "style":
            self.styles.append({"label": "style element", "parts": []})
            self._style_index = len(self.styles) - 1
        elif tag == "script":
            self.scripts.append({"attrs": values, "parts": [], "is_svg": is_svg_script})
            self._script_index = len(self.scripts) - 1
        if tag == "a" and self._nav_depth:
            self.nav_links.append(values)
        if "style" in values:
            self.styles.append({"label": f"{tag} style", "parts": [values["style"]]})
        for blocked_tag, attribute in FORBIDDEN_ATTRIBUTES:
            if tag == blocked_tag and attribute in values:
                self.forbidden_attributes.append((tag, attribute))
        for attribute in FORBIDDEN_GLOBAL_ATTRIBUTES:
            if attribute in values:
                self.forbidden_attributes.append((tag, attribute))
        for attribute in values:
            if attribute.startswith("on"):
                self.forbidden_attributes.append((tag, attribute))
        for attribute in RESOURCE_ATTRIBUTES.get(tag, ()):
            value = values.get(attribute)
            if value:
                self.resources.append((tag, attribute, value))
        if is_svg_script:
            for attribute in ("href", "xlink:href"):
                value = values.get(attribute)
                if value:
                    self.resources.append((tag, attribute, value))
        for attribute in SVG_URL_PRESENTATION_ATTRIBUTES:
            value = values.get(attribute)
            if value:
                self.svg_presentation_values.append((tag, attribute, value))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "style":
            self._style_index = None
        elif tag == "script":
            self._script_index = None
        if tag == "nav":
            self._nav_depth -= 1
        if tag == "svg":
            self._svg_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._style_index is not None:
            parts = self.styles[self._style_index]["parts"]
            assert isinstance(parts, list)
            parts.append(data)
        if self._script_index is not None:
            parts = self.scripts[self._script_index]["parts"]
            assert isinstance(parts, list)
            parts.append(data)


def parse_page(path: Path) -> tuple[str, PageParser]:
    text = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(text)
    return text, parser


def meta_value(parser: PageParser, key: str, value: str) -> str | None:
    for item in parser.meta:
        if item.get(key, "").lower() == value.lower():
            return item.get("content")
    return None


def link_value(parser: PageParser, relation: str) -> str | None:
    for tag, item in parser.links:
        if tag == "link" and relation in item.get("rel", "").lower().split():
            return item.get("href")
    return None


def expected_canonical(relative: str) -> str:
    return SITE_URL if relative == "index.html" else SITE_URL + relative


def resolve_reference(
    root: Path,
    page: Path,
    reference: str,
    *,
    request_url: str | None = None,
    allowed_external: bool,
    allowed_special: set[str] | None = None,
) -> tuple[Path | None, str | None]:
    """Resolve a URL to a local artifact or return a policy error."""
    allowed_special = allowed_special or set()
    value = reference.strip()
    if not value:
        return None, None
    if value.startswith("//"):
        return None, "scheme-relative URLs are not allowed"

    parts = urlsplit(value)
    scheme = parts.scheme.lower()
    if scheme in allowed_special:
        return None, None
    if scheme and scheme != "https":
        return None, f"URL scheme {scheme!r} is not allowed"

    if request_url and not scheme and not parts.netloc and not value.startswith("/"):
        return resolve_reference(
            root,
            page,
            urljoin(request_url, value),
            allowed_external=allowed_external,
            allowed_special=allowed_special,
        )

    if scheme == "https" or parts.netloc:
        if parts.netloc != SITE_HOST:
            if allowed_external and scheme == "https":
                return None, None
            return None, "external URL is not allowed for this resource"
        path = unquote(parts.path)
        if not path.startswith(SITE_PATH):
            return None, "same-origin URL is outside the project site path"
        relative = path[len(SITE_PATH):]
        target = root / (relative or "index.html")
    else:
        path = unquote(parts.path)
        if not path:
            return None, None
        if path.startswith("/"):
            if not path.startswith(SITE_PATH):
                return None, "root-relative URL is outside the project site path"
            target = root / (path[len(SITE_PATH):] or "index.html")
        else:
            target = page.parent / path

    target = target.resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return None, "local URL escapes the site root"
    return target, None


def validate_current_nav(root: Path, path: Path, parser: PageParser) -> list[str]:
    current_links = [link for link in parser.nav_links if "aria-current" in link]
    errors: list[str] = []
    exact_links: list[dict[str, str]] = []
    for link in parser.nav_links:
        href = link.get("href", "")
        target, policy_error = resolve_reference(
            root,
            path,
            href,
            allowed_external=False,
        )
        href_parts = urlsplit(href)
        if (
            not policy_error
            and target == path.resolve()
            and not href_parts.query
            and not href_parts.fragment
        ):
            exact_links.append(link)

    expected_count = 1 if exact_links else 0
    if len(exact_links) > 1:
        errors.append(
            f"nav has {len(exact_links)} links to the rendered page; expected at most 1"
        )
    if len(current_links) != expected_count:
        errors.append(
            "nav must mark exactly the rendered-page link aria-current; "
            f"expected {expected_count}, found {len(current_links)}"
        )
    for current_link in current_links:
        if current_link.get("aria-current") != "page":
            errors.append("current nav link must use aria-current=\"page\"")
        href = current_link.get("href", "")
        target, policy_error = resolve_reference(
            root,
            path,
            href,
            allowed_external=False,
        )
        href_parts = urlsplit(href)
        if (
            policy_error
            or target != path.resolve()
            or href_parts.query
            or href_parts.fragment
        ):
            errors.append(
                f"current nav link {href!r} does not identify the rendered page"
            )
    return errors


def validate_references(
    root: Path,
    path: Path,
    parser: PageParser,
    *,
    request_url: str | None = None,
) -> list[str]:
    errors: list[str] = []
    for tag, attribute in parser.duplicate_attributes:
        errors.append(f"{tag} has duplicate {attribute} attribute")
    for directive in parser.forbidden_meta_directives:
        errors.append(f"meta http-equiv={directive!r} is not allowed")
    for tag, attribute in parser.forbidden_attributes:
        errors.append(f"{tag} {attribute} is not allowed")
    for style in parser.styles:
        label = style["label"]
        parts = style["parts"]
        assert isinstance(label, str) and isinstance(parts, list)
        css = "".join(parts)
        if contains_resource_loading_css(css):
            errors.append(f"{label} contains resource-loading CSS")
    for tag, attribute, value in parser.svg_presentation_values:
        references, syntax_error = css_url_references(value)
        if syntax_error:
            errors.append(f"unsafe {tag} {attribute}: malformed CSS {syntax_error}")
            continue
        for reference in references:
            if not is_local_fragment(reference):
                errors.append(
                    f"unsafe {tag} {attribute} url {reference!r}: "
                    "only local fragment references are allowed"
                )
    for tag, item in parser.links:
        href = item.get("href")
        if not href:
            continue
        target, policy_error = resolve_reference(
            root,
            path,
            href,
            request_url=request_url,
            allowed_external=tag in {"a", "area"},
            allowed_special={"mailto", "tel"} if tag in {"a", "area"} else set(),
        )
        if policy_error:
            errors.append(f"unsafe {tag} href {href!r}: {policy_error}")
        elif target is not None and not target.is_file():
            errors.append(f"broken internal {tag} href {href!r}")

    for tag, attribute, value in parser.resources:
        references = (
            [candidate.strip().split()[0] for candidate in value.split(",") if candidate.strip()]
            if attribute.endswith("srcset")
            else [value]
        )
        for reference in references:
            target, policy_error = resolve_reference(
                root,
                path,
                reference,
                request_url=request_url,
                allowed_external=False,
            )
            if policy_error:
                errors.append(f"unsafe {tag} {attribute} {reference!r}: {policy_error}")
            elif target is not None and not target.is_file():
                errors.append(f"broken local {tag} {attribute} {reference!r}")

    for script in parser.scripts:
        attrs = script["attrs"]
        parts = script["parts"]
        assert isinstance(attrs, dict) and isinstance(parts, list)
        src = attrs.get("src", "")
        script_type = attrs.get("type", "").lower()
        content = "".join(parts).strip()
        if script.get("is_svg"):
            href = attrs.get("href", "") or attrs.get("xlink:href", "")
            if href:
                if content:
                    errors.append(
                        f"external SVG script element {href!r} must not contain inline code"
                    )
            else:
                errors.append("inline SVG script is not allowed")
            continue
        if src:
            if content:
                errors.append(f"external script element {src!r} must not contain inline code")
            target, policy_error = resolve_reference(
                root,
                path,
                src,
                request_url=request_url,
                allowed_external=False,
            )
            if policy_error:
                errors.append(f"unsafe script src {src!r}: {policy_error}")
            elif target is None or not target.is_file():
                errors.append(f"broken local script {src!r}")
        elif script_type != "application/ld+json":
            errors.append("non-JSON-LD inline script is not allowed")
    return errors


def json_ld_values(parser: PageParser) -> tuple[list[dict[str, object]], list[str]]:
    values: list[dict[str, object]] = []
    errors: list[str] = []
    for script in parser.scripts:
        attrs = script["attrs"]
        parts = script["parts"]
        assert isinstance(attrs, dict) and isinstance(parts, list)
        if attrs.get("type", "").lower() != "application/ld+json":
            continue
        try:
            value = json.loads("".join(parts).strip())
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON-LD: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append("JSON-LD root must be an object")
            continue
        values.append(value)
    return values, errors


def validate_page(root: Path, path: Path) -> list[str]:
    relative = path.relative_to(root).as_posix()
    text, parser = parse_page(path)
    errors: list[str] = []

    if not parser.title.strip():
        errors.append("missing title")
    required_meta = {
        ("name", "description"): None,
        ("property", "og:title"): None,
        ("property", "og:description"): None,
        ("property", "og:url"): expected_canonical(relative),
        ("property", "og:image"): SOCIAL_IMAGE,
        ("property", "og:image:type"): "image/png",
        ("property", "og:image:width"): "1200",
        ("property", "og:image:height"): "630",
        ("name", "twitter:card"): "summary_large_image",
        ("name", "twitter:title"): None,
        ("name", "twitter:description"): None,
        ("name", "twitter:image"): SOCIAL_IMAGE,
    }
    for (key, name), expected in required_meta.items():
        actual = meta_value(parser, key, name)
        if not actual:
            errors.append(f"missing {name} metadata")
        elif expected is not None and actual != expected:
            errors.append(f"{name}={actual!r}; expected {expected!r}")

    expected = expected_canonical(relative)
    canonical = link_value(parser, "canonical")
    if canonical != expected:
        errors.append(f"canonical={canonical!r}; expected {expected!r}")
    favicon = link_value(parser, "icon")
    if not favicon:
        errors.append("missing favicon link")

    json_ld, json_errors = json_ld_values(parser)
    errors.extend(json_errors)
    if len(json_ld) != 1:
        errors.append(f"expected exactly one JSON-LD block, found {len(json_ld)}")
    for value in json_ld:
        if value.get("url") != expected:
            errors.append(f"JSON-LD url={value.get('url')!r}; expected {expected!r}")
        if value.get("name") != parser.title.strip():
            errors.append("JSON-LD name does not match title")
        try:
            date.fromisoformat(str(value.get("dateModified", "")))
        except ValueError:
            errors.append("JSON-LD dateModified must be an ISO date")

    lowered = text.lower()
    for domain in AD_DOMAINS:
        if domain in lowered:
            errors.append(f"advertising or tracking network reference is disabled: {domain}")

    errors.extend(validate_current_nav(root, path, parser))
    errors.extend(validate_references(root, path, parser))
    if relative == "404.html":
        nested_url = SITE_URL + "missing/deep/example"
        errors.extend(
            f"nested 404 fixture: {error}"
            for error in validate_references(root, path, parser, request_url=nested_url)
        )
    return [f"{relative}: {error}" for error in errors]


def is_noindex(parser: PageParser) -> bool:
    robots = meta_value(parser, "name", "robots") or ""
    return "noindex" in {token.strip().lower() for token in robots.split(",")}


def validate_sitemap(root: Path, pages: list[Path]) -> list[str]:
    sitemap_path = root / "sitemap.xml"
    try:
        document_root = ElementTree.parse(sitemap_path).getroot()
    except (OSError, ElementTree.ParseError) as exc:
        return [f"sitemap.xml: {exc}"]

    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    actual: dict[str, str] = {}
    errors: list[str] = []
    for node in document_root.findall("sm:url", namespace):
        loc = node.findtext("sm:loc", namespaces=namespace)
        lastmod = node.findtext("sm:lastmod", namespaces=namespace)
        if not loc:
            errors.append("sitemap.xml: entry missing loc")
            continue
        if loc in actual:
            errors.append(f"sitemap.xml: duplicate {loc}")
        actual[loc] = lastmod or ""

    expected: dict[str, str] = {}
    for page in pages:
        relative = page.relative_to(root).as_posix()
        _, parser = parse_page(page)
        if relative == "404.html" or is_noindex(parser):
            continue
        json_ld, _ = json_ld_values(parser)
        if len(json_ld) == 1:
            expected[expected_canonical(relative)] = str(json_ld[0].get("dateModified", ""))

    for url in sorted(expected.keys() - actual.keys()):
        errors.append(f"sitemap.xml: missing {url}")
    for url in sorted(actual.keys() - expected.keys()):
        errors.append(f"sitemap.xml: unexpected or non-indexable URL {url}")
    for url in sorted(expected.keys() & actual.keys()):
        if actual[url] != expected[url]:
            errors.append(
                f"sitemap.xml: lastmod for {url} is {actual[url]!r}; expected {expected[url]!r}"
            )
    if len(set(expected.values())) < 2:
        errors.append("sitemap.xml: page modification dates are blanket values, not content-derived")
    return errors


def site_pages(root: Path) -> list[Path]:
    pages = list(root.glob("*.html"))
    for directory in ("builds", "guides", "tools"):
        pages.extend((root / directory).rglob("*.html"))
    return sorted(
        path for path in pages
        if path.relative_to(root).as_posix() not in EXCLUDED_HTML
    )


def validate_dist_inventory(root: Path) -> list[str]:
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    }
    expected = expected_dist_paths(REPO_ROOT)
    errors = [f"dist: missing allowlisted file {path}" for path in sorted(expected - actual)]
    errors.extend(f"dist: unexpected file {path}" for path in sorted(actual - expected))
    allowed_json = runtime_dist_paths(REPO_ROOT)
    forbidden_extensions = {".py", ".md", ".svg"}
    errors.extend(
        f"dist: forbidden source extension published: {path}"
        for path in sorted(actual)
        if Path(path).suffix.lower() in forbidden_extensions
    )
    errors.extend(
        f"dist: unexpected JSON published: {path}"
        for path in sorted(actual)
        if Path(path).suffix.lower() == ".json" and path not in allowed_json
    )
    schema = json.loads((REPO_ROOT / "data" / "builds" / "schema.json").read_text(encoding="utf-8"))
    for relative in sorted(allowed_json & actual):
        path = root / relative
        try:
            build = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"dist: invalid runtime JSON {relative}: {exc}")
            continue
        schema_errors: list[str] = []
        validate_against_schema(build, schema, schema, "", schema_errors)
        if schema_errors:
            errors.append(
                f"dist: runtime JSON schema violation {relative}: " + "; ".join(schema_errors)
            )
        if build.get("status") != "published":
            errors.append(f"dist: runtime JSON is not published: {relative}")
        if build.get("id") != path.stem:
            errors.append(f"dist: runtime JSON id does not match filename: {relative}")
    return errors


def validate_javascript_policy(root: Path) -> list[str]:
    """Scan the JavaScript that will actually ship, not only HTML wrappers."""
    errors: list[str] = []
    for path in sorted((root / "assets" / "js").glob("*.js")):
        lowered = path.read_text(encoding="utf-8").lower()
        relative = path.relative_to(root).as_posix()
        for domain in AD_DOMAINS:
            if domain in lowered:
                errors.append(
                    f"{relative}: advertising or tracking network reference is disabled: {domain}"
                )
    return errors


def validate_png(path: Path, dimensions: tuple[int, int]) -> list[str]:
    label = path.as_posix()
    if not path.is_file():
        return [f"{label}: image missing"]
    image_bytes = path.read_bytes()
    if image_bytes[:8] != b"\x89PNG\r\n\x1a\n":
        return [f"{label}: invalid PNG signature"]
    if len(image_bytes) < 24 or image_bytes[12:16] != b"IHDR":
        return [f"{label}: missing PNG IHDR"]
    actual = struct.unpack(">II", image_bytes[16:24])
    if actual != dimensions:
        return [f"{label}: dimensions {actual[0]}x{actual[1]}; expected {dimensions[0]}x{dimensions[1]}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--dist", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"site root does not exist: {root}")

    pages = site_pages(root)
    errors: list[str] = []
    for page in pages:
        errors.extend(validate_page(root, page))
    errors.extend(validate_sitemap(root, pages))
    errors.extend(validate_patch_marker(root))
    if args.dist:
        errors.extend(validate_dist_inventory(root))
    errors.extend(validate_javascript_policy(root))
    errors.extend(validate_png(root / "assets" / "social-card.png", (1200, 630)))
    errors.extend(validate_png(root / "assets" / "favicon.png", (32, 32)))

    if errors:
        for error in errors:
            print(f"FAIL  {error}")
        print(f"\nSITE VALIDATION FAILED: {len(errors)} violation(s).")
        return 1
    scope = "packaged dist" if args.dist else "source site"
    print(
        f"SITE VALIDATION PASSED ({scope}): {len(pages)} generated page(s), metadata, "
        "JSON-LD, safe references/scripts, exact sitemap, images, and ad-disable policy are valid."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
