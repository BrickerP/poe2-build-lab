#!/usr/bin/env python3
"""Negative regression tests for the generated-site trust boundary."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_site.py"
DIST = ROOT / "dist"


class SiteValidatorNegativeTests(unittest.TestCase):
    def setUp(self):
        if not DIST.is_dir():
            self.fail("dist/ is required; run scripts/package_site.py before this test")
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "site"
        shutil.copytree(DIST, self.root)

    def tearDown(self):
        self.temporary.cleanup()

    def mutate(self, relative, old, new):
        path = self.root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def assert_rejected(self, expected):
        result = subprocess.run(
            ["python3", str(VALIDATOR), "--root", str(self.root), "--dist"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        output = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, output)
        self.assertIn(expected, output)

    def test_javascript_anchor_is_rejected(self):
        self.mutate("index.html", 'href="builds/index.html"', 'href="javascript:alert(1)"')
        self.assert_rejected("URL scheme 'javascript' is not allowed")

    def test_data_anchor_is_rejected(self):
        self.mutate("index.html", 'href="builds/index.html"', 'href="data:text/html,unsafe"')
        self.assert_rejected("URL scheme 'data' is not allowed")

    def test_missing_same_origin_absolute_resource_is_rejected(self):
        self.mutate(
            "index.html",
            'href="styles.css"',
            'href="https://brickerp.github.io/poe2-build-lab/assets/missing.css"',
        )
        self.assert_rejected("broken internal link href")

    def test_non_json_ld_inline_script_is_rejected(self):
        self.mutate("index.html", "</body>", "<script>window.bad = true</script></body>")
        self.assert_rejected("non-JSON-LD inline script is not allowed")

    def test_external_script_is_rejected(self):
        self.mutate("index.html", "</body>", '<script src="https://example.com/app.js"></script></body>')
        self.assert_rejected("external URL is not allowed for this resource")

    def test_ad_network_subdomain_is_rejected(self):
        self.mutate("index.html", "</body>", '<script src="https://cdn.doubleclick.net/ad.js"></script></body>')
        self.assert_rejected("advertising or tracking network reference is disabled: doubleclick.net")

    def test_extra_sitemap_url_is_rejected(self):
        self.mutate(
            "sitemap.xml",
            "</urlset>",
            "  <url><loc>https://brickerp.github.io/poe2-build-lab/ghost.html</loc><lastmod>2026-07-19</lastmod></url>\n</urlset>",
        )
        self.assert_rejected("unexpected or non-indexable URL")

    def test_nested_404_relative_resource_is_rejected(self):
        self.mutate("404.html", 'href="/poe2-build-lab/styles.css"', 'href="styles.css"')
        self.assert_rejected("nested 404 fixture: broken internal link href 'styles.css'")

    def test_missing_runtime_build_json_is_rejected(self):
        (self.root / "data/builds/starter-elemental-caster.json").unlink()
        self.assert_rejected("dist: missing allowlisted file data/builds/starter-elemental-caster.json")

    def test_extra_runtime_json_is_rejected(self):
        extra = self.root / "data/builds/secret.json"
        extra.write_text('{"secret":"must not ship"}', encoding="utf-8")
        self.assert_rejected("dist: unexpected file data/builds/secret.json")

    def test_malicious_runtime_json_is_rejected(self):
        path = self.root / "data/builds/starter-elemental-caster.json"
        build = json.loads(path.read_text(encoding="utf-8"))
        build["injected_html"] = '<script src="https://cdn.doubleclick.net/ad.js"></script>'
        path.write_text(json.dumps(build), encoding="utf-8")
        self.assert_rejected("dist: runtime JSON schema violation")


if __name__ == "__main__":
    unittest.main()
