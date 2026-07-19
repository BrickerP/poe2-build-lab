#!/usr/bin/env python3
"""Regression tests for the post-deploy live artifact gate."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from verify_live_deploy import (
    Response,
    SITE_URL,
    audit_once,
    content_type_for,
    public_url,
    published_files,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD_ARTIFACT_SHA = "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c"
VALID_CSS = """@font-face {
  font-family: "Source Sans 3";
  font-style: normal;
  font-weight: 400 700;
  font-display: swap;
  src: url("assets/fonts/source-sans-3-latin-variable.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: "Libre Baskerville";
  font-style: normal;
  font-weight: 400 700;
  font-display: swap;
  src: url("assets/fonts/libre-baskerville-latin-variable.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
body {}
"""


class LiveDeployTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.dist = self.root / "dist"
        self.dist.mkdir()
        marker = (
            '<a href="https://example.com/patch" rel="nofollow noopener">Patch Test</a>'
        )
        (self.dist / "index.html").write_text(
            '<link rel="canonical" href="' + SITE_URL + '">' + marker,
            encoding="utf-8",
        )
        (self.dist / "styles.css").write_text(VALID_CSS, encoding="utf-8")
        font_dir = self.dist / "assets/fonts"
        font_dir.mkdir(parents=True)
        (font_dir / "source-sans-3-latin-variable.woff2").write_bytes(b"font")
        (self.dist / ".nojekyll").write_bytes(b"")
        self.ledger = self.root / "patch-notes.json"
        self.ledger.write_text(
            json.dumps(
                {
                    "current_patch": "Patch Test",
                    "patches": [
                        {
                            "patch_version": "Patch Test",
                            "source_url": "https://example.com/patch",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def responses(self) -> dict[str, Response]:
        return {
            public_url("index.html"): Response(
                200,
                "text/html",
                (self.dist / "index.html").read_bytes(),
                SITE_URL,
            ),
            public_url("styles.css"): Response(
                200,
                "text/css",
                (self.dist / "styles.css").read_bytes(),
                SITE_URL + "styles.css",
            ),
            public_url("assets/fonts/source-sans-3-latin-variable.woff2"): Response(
                200,
                "font/woff2",
                b"font",
                SITE_URL + "assets/fonts/source-sans-3-latin-variable.woff2",
            ),
        }

    def audit(self, responses: dict[str, Response]) -> list[str]:
        def fetcher(url: str, _timeout: float) -> Response:
            return responses[url]

        return audit_once(
            self.dist,
            self.ledger,
            base_url=SITE_URL,
            timeout=1,
            fetcher=fetcher,
        )

    def test_exact_artifact_passes_and_nojekyll_is_not_requested(self) -> None:
        self.assertEqual(
            ["source-sans-3-latin-variable.woff2", "index.html", "styles.css"],
            [p.name for p in published_files(self.dist)],
        )
        self.assertEqual([], self.audit(self.responses()))

    def test_byte_drift_is_rejected(self) -> None:
        responses = self.responses()
        responses[SITE_URL + "styles.css"] = Response(
            200,
            "text/css",
            b"body{color:red}\n",
            SITE_URL + "styles.css",
        )
        self.assertIn("live bytes differ from immutable dist", "\n".join(self.audit(responses)))

    def test_mime_redirect_canonical_patch_and_tracking_are_rejected(self) -> None:
        responses = self.responses()
        bad_index = (
            '<link rel="canonical" href="https://wrong.example/">'
            '<script src="https://www.googletagmanager.com/tag.js"></script>'
        ).encode()
        responses[SITE_URL] = Response(200, "text/plain", bad_index, SITE_URL + "index.html")
        errors = "\n".join(self.audit(responses))
        self.assertIn("Content-Type", errors)
        self.assertIn("redirected", errors)
        self.assertIn("live bytes differ", errors)
        self.assertIn("canonical", errors)
        self.assertIn("current patch marker", errors)
        self.assertIn("advertising or tracking reference", errors)

    def test_known_content_types_are_explicit(self) -> None:
        self.assertEqual({"application/octet-stream", "text/plain"}, content_type_for(Path("x.build")))
        self.assertEqual({"application/javascript", "text/javascript"}, content_type_for(Path("x.js")))
        self.assertEqual({"font/woff2"}, content_type_for(Path("x.woff2")))

    def test_woff2_mime_is_enforced(self) -> None:
        responses = self.responses()
        font_url = SITE_URL + "assets/fonts/source-sans-3-latin-variable.woff2"
        responses[font_url] = Response(200, "application/octet-stream", b"font", font_url)
        errors = "\n".join(self.audit(responses))
        self.assertIn("Content-Type 'application/octet-stream'", errors)
        self.assertIn("font/woff2", errors)

    def test_live_font_css_contract_is_enforced(self) -> None:
        responses = self.responses()
        bad_css = VALID_CSS.replace(
            'url("assets/fonts/source-sans-3-latin-variable.woff2")',
            'url("https://fonts.gstatic.com/remote.woff2")',
        ).encode()
        responses[SITE_URL + "styles.css"] = Response(
            200,
            "text/css",
            bad_css,
            SITE_URL + "styles.css",
        )
        errors = "\n".join(self.audit(responses))
        self.assertIn("live bytes differ", errors)
        self.assertIn('contract for "Source Sans 3" differs: mismatched src', errors)

    def test_live_font_css_contract_uses_effective_comment_free_css(self) -> None:
        responses = self.responses()
        bad_css = VALID_CSS.replace(
            '  font-family: "Source Sans 3";',
            '  /* font-family: "Source Sans 3"; */',
        ).encode()
        responses[SITE_URL + "styles.css"] = Response(
            200,
            "text/css",
            bad_css,
            SITE_URL + "styles.css",
        )
        errors = "\n".join(self.audit(responses))
        self.assertIn("live bytes differ", errors)
        self.assertIn("missing effective font-family", errors)

    def test_workflow_downloads_existing_artifact_and_verifies_after_deploy(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        download = f"actions/download-artifact@{DOWNLOAD_ARTIFACT_SHA}"
        self.assertIn(download, workflow)
        self.assertIn("name: poe2-site-evidence-${{ github.run_attempt }}", workflow)
        self.assertIn("python3 scripts/verify_live_deploy.py", workflow)
        self.assertLess(workflow.index("name: Deploy exact dist artifact"), workflow.index(download))
        self.assertLess(workflow.index(download), workflow.index("python3 scripts/verify_live_deploy.py"))


if __name__ == "__main__":
    unittest.main()
