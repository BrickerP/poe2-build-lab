#!/usr/bin/env python3
"""Negative regression tests for the generated-site trust boundary."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_site.py"
DIST = ROOT / "dist"


class FormNameParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.controls = []
        self.elements = {}
        self.ids = set()
        self.labels_for = set()
        self.label_depth = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
            self.elements[values["id"]] = values
        if tag == "label":
            self.label_depth += 1
            if values.get("for"):
                self.labels_for.add(values["for"])
        elif tag in {"button", "input", "select", "textarea"}:
            self.controls.append((tag, values, self.label_depth > 0))

    def handle_endtag(self, tag):
        if tag == "label":
            self.label_depth -= 1


class SiteAccessibilityTests(unittest.TestCase):
    def test_attribute_checker_controls_have_accessible_names(self):
        parser = FormNameParser()
        parser.feed((ROOT / "tools/attribute-checker.html").read_text(encoding="utf-8"))

        unnamed = []
        for tag, attrs, wrapped_by_label in parser.controls:
            labelled_by = attrs.get("aria-labelledby", "").split()
            has_name = (
                bool(attrs.get("aria-label"))
                or bool(labelled_by) and all(reference in parser.ids for reference in labelled_by)
                or attrs.get("id") in parser.labels_for
                or wrapped_by_label
            )
            if not has_name:
                unnamed.append(attrs.get("id") or tag)

        numeric_inputs = [
            attrs
            for tag, attrs, _ in parser.controls
            if tag == "input" and attrs.get("type") == "number"
        ]
        self.assertEqual(15, len(numeric_inputs))
        self.assertEqual(16, len(parser.controls))
        self.assertEqual([], unnamed)

    def test_attribute_checker_results_and_failure_banner_are_polite_statuses(self):
        parser = FormNameParser()
        parser.feed((ROOT / "tools/attribute-checker.html").read_text(encoding="utf-8"))

        for element_id in ("build-banner", "attr-summary", "spirit-result", "swap-result"):
            with self.subTest(element_id=element_id):
                attrs = parser.elements[element_id]
                self.assertEqual("status", attrs.get("role"))
                self.assertEqual("polite", attrs.get("aria-live"))

        for element_id in ("swap-str", "swap-dex", "swap-int", "swap-spirit"):
            with self.subTest(element_id=element_id):
                self.assertIn(
                    "swap-loss-group",
                    parser.elements[element_id].get("aria-labelledby", "").split(),
                )


class SiteGeneratorTests(unittest.TestCase):
    def test_readme_python_pin_comes_from_python_version_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copy2(ROOT / "sitegen.py", root / "sitegen.py")
            shutil.copytree(ROOT / "data", root / "data")
            (root / ".python-version").write_text("9.8.7-test\n", encoding="utf-8")

            result = subprocess.run(
                ["python3", "sitegen.py"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn(
                "Python runtime pinned to `9.8.7-test` through `.python-version`",
                readme,
            )


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

    def test_duplicate_attributes_are_rejected_case_insensitively(self):
        cases = (
            (
                '<script src="https://example.com/app.js" '
                'src="assets/js/attribute-calculator.js"></script>',
                "script has duplicate src attribute",
            ),
            (
                '<img src="https://example.com/image.png" src="assets/favicon.png">',
                "img has duplicate src attribute",
            ),
            (
                '<svg><rect filter="url(https://example.com/filter.svg#f)" '
                'filter="url(#local-filter)"></rect></svg>',
                "rect has duplicate filter attribute",
            ),
            (
                '<img Src="https://example.com/image.png" sRC="assets/favicon.png">',
                "img has duplicate src attribute",
            ),
        )
        for markup, expected in cases:
            with self.subTest(markup=markup):
                shutil.rmtree(self.root)
                shutil.copytree(DIST, self.root)
                self.mutate("index.html", "</body>", f"{markup}</body>")
                self.assert_rejected(expected)

    def test_svg_script_external_href_resources_are_rejected(self):
        cases = (
            (
                '<svg><script href="https://example.com/app.js"></script></svg>',
                "unsafe script href",
            ),
            (
                '<svg xmlns:xlink="http://www.w3.org/1999/xlink">'
                '<script xlink:href="https://example.com/app.js"></script></svg>',
                "unsafe script xlink:href",
            ),
        )
        for markup, expected in cases:
            with self.subTest(markup=markup):
                shutil.rmtree(self.root)
                shutil.copytree(DIST, self.root)
                self.mutate("index.html", "</body>", f"{markup}</body>")
                self.assert_rejected(expected)

    def test_svg_script_local_href_resources_follow_local_policy(self):
        self.mutate(
            "index.html",
            "</body>",
            '<svg xmlns:xlink="http://www.w3.org/1999/xlink">'
            '<script href="assets/js/attribute-calculator.js"></script>'
            '<script xlink:href="#local-script"></script></svg></body>',
        )
        result = subprocess.run(
            ["python3", str(VALIDATOR), "--root", str(self.root), "--dist"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_missing_or_duplicate_current_nav_is_rejected(self):
        cases = (
            (
                ' aria-current="page"',
                "",
                "nav must mark exactly the rendered-page link aria-current; expected 1, found 0",
            ),
            (
                '<a class="nav-link" href="builds/index.html">',
                '<a class="nav-link" href="builds/index.html" aria-current="page">',
                "nav must mark exactly the rendered-page link aria-current; expected 1, found 2",
            ),
        )
        for old, new, expected in cases:
            with self.subTest(expected=expected):
                shutil.rmtree(self.root)
                shutil.copytree(DIST, self.root)
                self.mutate("index.html", old, new)
                self.assert_rejected(expected)

    def test_wrong_current_nav_destination_is_rejected(self):
        self.mutate(
            "index.html",
            '<a class="nav-link home-link active" href="index.html" aria-current="page">',
            '<a class="nav-link home-link" href="index.html">',
        )
        self.mutate(
            "index.html",
            '<a class="nav-link" href="builds/index.html">',
            '<a class="nav-link active" href="builds/index.html" aria-current="page">',
        )
        self.assert_rejected("does not identify the rendered page")

    def test_section_active_detail_page_has_no_aria_current(self):
        path = self.root / "builds/starter-elemental-caster.html"
        text = path.read_text(encoding="utf-8")
        self.assertIn('class="nav-link active"', text)
        self.assertNotIn('aria-current="page"', text)

        result = subprocess.run(
            ["python3", str(VALIDATOR), "--root", str(self.root), "--dist"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_external_passive_resources_are_rejected(self):
        cases = (
            ('<link rel="stylesheet" href="https://example.com/style.css">', "unsafe link href"),
            ('<iframe src="https://example.com/frame"></iframe>', "unsafe iframe src"),
            ('<iframe srcdoc="unsafe inline document"></iframe>', "iframe srcdoc is not allowed"),
            ('<embed src="https://example.com/file.pdf">', "unsafe embed src"),
            ('<object data="https://example.com/file.pdf"></object>', "unsafe object data"),
            ('<img src="https://example.com/image.png">', "unsafe img src"),
            ('<source src="https://example.com/video.mp4">', "unsafe source src"),
            ('<audio src="https://example.com/audio.mp3"></audio>', "unsafe audio src"),
            ('<video src="https://example.com/video.mp4"></video>', "unsafe video src"),
            ('<video poster="https://example.com/poster.png"></video>', "unsafe video poster"),
            ('<track src="https://example.com/captions.vtt">', "unsafe track src"),
            (
                '<img srcset="assets/social-card.png 1x, https://example.com/image.png 2x">',
                "unsafe img srcset",
            ),
            (
                '<source srcset="assets/social-card.png 1x, https://example.com/image.png 2x">',
                "unsafe source srcset",
            ),
            (
                '<link rel="preload" as="image" href="assets/favicon.png" '
                'imagesrcset="assets/favicon.png 1x, https://example.com/image.png 2x">',
                "unsafe link imagesrcset",
            ),
            (
                '<svg><filter><feImage href="https://example.com/image.png"></feImage>'
                '</filter></svg>',
                "unsafe feimage href",
            ),
            (
                '<svg xmlns:xlink="http://www.w3.org/1999/xlink"><filter>'
                '<feImage xlink:href="https://example.com/image.png"></feImage>'
                '</filter></svg>',
                "unsafe feimage xlink:href",
            ),
        )
        for markup, expected in cases:
            with self.subTest(markup=markup):
                shutil.rmtree(self.root)
                shutil.copytree(DIST, self.root)
                self.mutate("index.html", "</body>", f"{markup}</body>")
                self.assert_rejected(expected)

    def test_local_passive_resources_are_allowed(self):
        self.mutate(
            "index.html",
            "</head>",
            '<link rel="preload" as="image" href="assets/favicon.png" '
            'imagesrcset="assets/favicon.png 1x, assets/social-card.png 2x">'
            '<style>@media (min-width: 1px) { .hidden { display: none; } }</style></head>',
        )
        self.mutate(
            "index.html",
            "</body>",
            '<img src="assets/social-card.png" '
            'srcset="assets/favicon.png 1x, assets/social-card.png 2x">'
            '<iframe src="about.html"></iframe>'
            '<svg xmlns:xlink="http://www.w3.org/1999/xlink"><filter id="local-filter">'
            '<feImage href="assets/favicon.png"></feImage>'
            '<feImage xlink:href="assets/social-card.png"></feImage>'
            '</filter><use href="#local-filter"></use></svg>'
            '<div style="display:none"></div></body>',
        )
        result = subprocess.run(
            ["python3", str(VALIDATOR), "--root", str(self.root), "--dist"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_event_handler_attributes_are_rejected(self):
        cases = (
            (
                '<img src="assets/favicon.png" '
                'onload="fetch(\'https://example.com/\')">',
                "img onload is not allowed",
            ),
            (
                '<svg onLoad="fetch(\'https://example.com/\')"></svg>',
                "svg onload is not allowed",
            ),
            (
                '<button ONCLICK="fetch(\'https://example.com/\')">Run</button>',
                "button onclick is not allowed",
            ),
        )
        for markup, expected in cases:
            with self.subTest(markup=markup):
                shutil.rmtree(self.root)
                shutil.copytree(DIST, self.root)
                self.mutate("index.html", "</body>", f"{markup}</body>")
                self.assert_rejected(expected)

    def test_svg_presentation_external_urls_are_rejected(self):
        attributes = (
            "filter",
            "fill",
            "stroke",
            "clip-path",
            "color-profile",
            "cursor",
            "marker",
            "marker-start",
            "marker-mid",
            "marker-end",
            "mask",
            "mask-border-source",
            "mask-image",
            "offset-path",
            "shape-inside",
            "shape-outside",
        )
        for attribute in attributes:
            with self.subTest(attribute=attribute):
                shutil.rmtree(self.root)
                shutil.copytree(DIST, self.root)
                markup = (
                    f'<svg><rect {attribute}="url(https://example.net/resource.svg#id)">'
                    "</rect></svg>"
                )
                self.mutate("index.html", "</body>", f"{markup}</body>")
                self.assert_rejected(f"unsafe rect {attribute} url")

    def test_svg_presentation_url_obfuscation_is_rejected(self):
        cases = (
            (
                '<svg><rect fill="url(  \'https://example.net/paint.svg#p\'  )">'
                "</rect></svg>",
                "unsafe rect fill url",
            ),
            (
                r'<svg><rect stroke="u\72l(\68 ttps://example.net/paint.svg#p)">'
                r"</rect></svg>",
                "unsafe rect stroke url",
            ),
            (
                '<svg><rect clip-path="url/**/( //example.net/clip.svg#c )">'
                "</rect></svg>",
                "unsafe rect clip-path url",
            ),
            (
                "<svg><rect filter='url(\"data:image/svg+xml,unsafe\")'>"
                "</rect></svg>",
                "unsafe rect filter url",
            ),
            (
                '<svg><rect mask="url(\'https://example.net/mask.svg#id)">'
                "</rect></svg>",
                "unsafe rect mask: malformed CSS unterminated quoted url()",
            ),
        )
        for markup, expected in cases:
            with self.subTest(markup=markup):
                shutil.rmtree(self.root)
                shutil.copytree(DIST, self.root)
                self.mutate("index.html", "</body>", f"{markup}</body>")
                self.assert_rejected(expected)

    def test_svg_presentation_local_values_are_allowed(self):
        markup = (
            '<svg><defs><filter id="local-filter"></filter>'
            '<clipPath id="local-clip"></clipPath><marker id="local-marker"></marker>'
            '<mask id="local-mask"></mask><linearGradient id="local-paint">'
            "</linearGradient></defs>"
            '<rect filter="url(#local-filter)" fill="url(#local-paint) #fff" '
            'stroke="none" '
            'clip-path="url( \'#local-clip\' )" cursor="auto" '
            r'marker-start="u\72l(\23 local-marker)" '
            'marker-mid="none" marker-end="url(#local-marker)" '
            'mask="url(#local-mask)"></rect></svg>'
        )
        self.mutate("index.html", "</body>", f"{markup}</body>")
        result = subprocess.run(
            ["python3", str(VALIDATOR), "--root", str(self.root), "--dist"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_resolution_and_inline_request_bypasses_are_rejected(self):
        cases = (
            (
                "</head>",
                '<base href="https://example.com/"><img src="assets/favicon.png">',
                "base href is not allowed",
            ),
            (
                "</body>",
                '<a href="about.html" ping="https://example.com/audit">About</a>',
                "a ping is not allowed",
            ),
            (
                "</body>",
                '<div style="background-image:url(https://example.com/image.png)"></div>',
                "div style contains resource-loading CSS",
            ),
            (
                "</body>",
                '<div style="background-image:u\\72l(https://example.com/image.png)"></div>',
                "div style contains resource-loading CSS",
            ),
            (
                "</head>",
                '<style>@import "https://example.com/style.css";</style>',
                "style element contains resource-loading CSS",
            ),
            (
                "</head>",
                '<style>.hero { background: url(https://example.com/image.png); }</style>',
                "style element contains resource-loading CSS",
            ),
        )
        for marker, markup, expected in cases:
            with self.subTest(markup=markup):
                shutil.rmtree(self.root)
                shutil.copytree(DIST, self.root)
                self.mutate("index.html", marker, f"{markup}{marker}")
                self.assert_rejected(expected)

    def test_automatic_navigation_and_submission_boundaries_are_rejected(self):
        cases = (
            (
                "</head>",
                '<meta http-equiv="refresh" content="0; url=https://example.com/">',
                "meta http-equiv='refresh' is not allowed",
            ),
            (
                "<body",
                '<body background="https://example.com/bg.png"',
                "body background is not allowed",
            ),
            (
                "</body>",
                '<table background="https://example.com/bg.png"></table>',
                "table background is not allowed",
            ),
            (
                "</body>",
                '<table><tr><td background="https://example.com/bg.png"></td></tr></table>',
                "td background is not allowed",
            ),
            (
                "</body>",
                '<table><tr><th background="https://example.com/bg.png"></th></tr></table>',
                "th background is not allowed",
            ),
            (
                "</body>",
                '<form action="https://example.com/submit"></form>',
                "form action is not allowed",
            ),
            (
                "</body>",
                '<button formaction="https://example.com/submit">Send</button>',
                "button formaction is not allowed",
            ),
            (
                "</body>",
                '<input formaction="https://example.com/submit">',
                "input formaction is not allowed",
            ),
            ("</body>", '<area href="javascript:alert(1)">', "unsafe area href"),
            (
                "<html",
                '<html manifest="https://example.com/cache.appcache"',
                "html manifest is not allowed",
            ),
            (
                "</body>",
                '<applet codebase="https://example.com/"></applet>',
                "applet codebase is not allowed",
            ),
            (
                "</body>",
                '<object codebase="https://example.com/"></object>',
                "object codebase is not allowed",
            ),
        )
        for marker, markup, expected in cases:
            with self.subTest(markup=markup):
                shutil.rmtree(self.root)
                shutil.copytree(DIST, self.root)
                self.mutate("index.html", marker, markup)
                self.assert_rejected(expected)

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
