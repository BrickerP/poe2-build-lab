#!/usr/bin/env python3
"""Verify the deployed Pages site is the exact packaged ``dist`` artifact."""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

from font_contract import validate_font_face_contract

SITE_URL = "https://brickerp.github.io/poe2-build-lab/"
IGNORED_CONTROL_FILES = {".nojekyll"}
AD_TRACKING_DOMAINS = (
    "adservice.google.com",
    "doubleclick.net",
    "google-analytics.com",
    "googleadservices.com",
    "googlesyndication.com",
    "googletagmanager.com",
    "googletagservices.com",
)
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".txt", ".xml"}
CONTENT_TYPES = {
    ".build": {"application/octet-stream", "text/plain"},
    ".css": {"text/css"},
    ".html": {"text/html"},
    ".js": {"application/javascript", "text/javascript"},
    ".json": {"application/json"},
    ".png": {"image/png"},
    ".txt": {"text/plain"},
    ".woff2": {"font/woff2"},
    ".xml": {"application/xml", "text/xml"},
}


@dataclass(frozen=True)
class Response:
    status: int
    content_type: str
    body: bytes
    final_url: str


class CanonicalParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.canonicals: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "link":
            return
        values = {key.lower(): value or "" for key, value in attrs}
        if "canonical" in values.get("rel", "").lower().split():
            self.canonicals.append(values.get("href", ""))


def published_files(dist_root: Path) -> list[Path]:
    files = [path for path in dist_root.rglob("*") if path.is_file()]
    return sorted(
        (path for path in files if path.relative_to(dist_root).as_posix() not in IGNORED_CONTROL_FILES),
        key=lambda path: path.relative_to(dist_root).as_posix(),
    )


def content_type_for(path: Path) -> set[str]:
    allowed = CONTENT_TYPES.get(path.suffix.lower())
    if allowed:
        return allowed
    guessed, _ = mimetypes.guess_type(path.name)
    return {guessed} if guessed else {"application/octet-stream"}


def public_url(relative: str, base_url: str = SITE_URL) -> str:
    if relative == "index.html":
        return base_url
    return urljoin(base_url, quote(relative, safe="/"))


def expected_canonical(relative: str) -> str:
    return SITE_URL if relative == "index.html" else SITE_URL + relative


def load_current_patch(ledger_path: Path) -> tuple[str, str]:
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    version = ledger.get("current_patch")
    matches = [
        patch
        for patch in ledger.get("patches", [])
        if isinstance(patch, dict) and patch.get("patch_version") == version
    ]
    if not isinstance(version, str) or not version or len(matches) != 1:
        raise ValueError("patch ledger must identify exactly one current patch entry")
    source_url = matches[0].get("source_url")
    if not isinstance(source_url, str) or not source_url.startswith("https://"):
        raise ValueError("current patch source URL must be absolute HTTPS")
    return version, source_url


def fetch_url(url: str, timeout: float) -> Response:
    request = Request(
        url,
        headers={
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
            "User-Agent": "poe2-build-lab-live-verifier/1.0",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return Response(
            status=response.status,
            content_type=response.headers.get_content_type().lower(),
            body=response.read(),
            final_url=response.geturl(),
        )


def validate_live_invariants(
    live: dict[str, Response],
    *,
    patch_version: str,
    patch_source_url: str,
) -> list[str]:
    errors: list[str] = []
    for relative, response in sorted(live.items()):
        if Path(relative).suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = response.body.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{relative}: live text response is not UTF-8")
            continue
        lowered = text.lower()
        for domain in AD_TRACKING_DOMAINS:
            if domain in lowered:
                errors.append(f"{relative}: advertising or tracking reference is enabled: {domain}")
        if relative.endswith(".html") and relative != "googlead1eaf93276e5fa5.html":
            parser = CanonicalParser()
            parser.feed(text)
            expected = expected_canonical(relative)
            if parser.canonicals != [expected]:
                errors.append(
                    f"{relative}: canonical {parser.canonicals!r}; expected exactly [{expected!r}]"
                )

    index = live.get("index.html")
    if index is None:
        errors.append("index.html: missing from live audit")
    else:
        marker = f'href="{patch_source_url}" rel="nofollow noopener">{patch_version}</a>'
        if marker.encode("utf-8") not in index.body:
            errors.append("index.html: current patch marker does not match patch ledger")
    stylesheet = live.get("styles.css")
    if stylesheet is None:
        errors.append("styles.css: missing from live audit")
    else:
        try:
            css = stylesheet.body.decode("utf-8")
        except UnicodeDecodeError:
            errors.append("styles.css: live stylesheet is not UTF-8")
        else:
            if "@import" in css.lower() or "fonts.googleapis.com" in css.lower():
                errors.append("styles.css: live stylesheet must not import remote fonts")
            errors.extend(validate_font_face_contract(css, label="styles.css: live"))
    return errors


def audit_once(
    dist_root: Path,
    ledger_path: Path,
    *,
    base_url: str,
    timeout: float,
    fetcher=fetch_url,
) -> list[str]:
    errors: list[str] = []
    live: dict[str, Response] = {}
    patch_version, patch_source_url = load_current_patch(ledger_path)

    def fetch_path(path: Path) -> tuple[Path, Response | None, str | None]:
        relative = path.relative_to(dist_root).as_posix()
        url = public_url(relative, base_url)
        try:
            return path, fetcher(url, timeout), None
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            return path, None, f"{relative}: request failed: {exc}"

    files = published_files(dist_root)
    results: list[tuple[Path, Response | None, str | None]] = []
    with ThreadPoolExecutor(max_workers=min(8, len(files))) as executor:
        futures = [executor.submit(fetch_path, path) for path in files]
        results.extend(future.result() for future in as_completed(futures))

    for path, response, fetch_error in sorted(
        results,
        key=lambda result: result[0].relative_to(dist_root).as_posix(),
    ):
        relative = path.relative_to(dist_root).as_posix()
        if fetch_error:
            errors.append(fetch_error)
            continue
        if response is None:  # pragma: no cover - defensive type narrowing
            continue
        url = public_url(relative, base_url)
        live[relative] = response
        if response.status != 200:
            errors.append(f"{relative}: HTTP {response.status}; expected 200")
        if response.final_url != url:
            errors.append(f"{relative}: redirected to {response.final_url!r}; expected {url!r}")
        allowed_types = content_type_for(path)
        if response.content_type not in allowed_types:
            errors.append(
                f"{relative}: Content-Type {response.content_type!r}; expected one of {sorted(allowed_types)!r}"
            )
        expected_body = path.read_bytes()
        if response.body != expected_body:
            errors.append(
                f"{relative}: live bytes differ from immutable dist "
                f"({len(response.body)} != {len(expected_body)} bytes)"
            )
    errors.extend(
        validate_live_invariants(
            live,
            patch_version=patch_version,
            patch_source_url=patch_source_url,
        )
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument(
        "--patch-ledger",
        type=Path,
        default=Path("data/sources/patch-notes.json"),
    )
    parser.add_argument("--base-url", default=SITE_URL)
    parser.add_argument("--attempts", type=int, default=8)
    parser.add_argument("--delay-seconds", type=float, default=8.0)
    parser.add_argument("--timeout-seconds", type=float, default=8.0)
    args = parser.parse_args()

    dist_root = args.dist.resolve()
    if not dist_root.is_dir():
        parser.error(f"dist directory does not exist: {dist_root}")
    if args.base_url != SITE_URL:
        parser.error(f"base URL must be exactly {SITE_URL!r}")
    if args.attempts < 1 or args.delay_seconds < 0 or args.timeout_seconds <= 0:
        parser.error("attempts and timeout must be positive; delay must be non-negative")
    files = published_files(dist_root)
    if not files:
        parser.error("dist contains no publishable files")

    for attempt in range(1, args.attempts + 1):
        try:
            errors = audit_once(
                dist_root,
                args.patch_ledger,
                base_url=args.base_url,
                timeout=args.timeout_seconds,
            )
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"LIVE DEPLOY VERIFICATION FAILED: invalid local evidence: {exc}", file=sys.stderr)
            return 1
        if not errors:
            print(
                f"LIVE DEPLOY VERIFIED on attempt {attempt}: {len(files)} served file(s) "
                "match the immutable dist byte-for-byte; status, content types, base URL, "
                "canonical metadata, current patch, and ad/tracking policy are valid."
            )
            return 0
        print(f"Attempt {attempt}/{args.attempts} not converged ({len(errors)} issue(s)):")
        for error in errors[:20]:
            print(f"  - {error}")
        if len(errors) > 20:
            print(f"  - ... {len(errors) - 20} more")
        if attempt < args.attempts:
            time.sleep(args.delay_seconds)

    print("LIVE DEPLOY VERIFICATION FAILED after bounded CDN retries.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
