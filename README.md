# PoE2 Build Lab

Static beginner-guide site for Path of Exile 2.

Live URL target: https://brickerp.github.io/poe2-build-lab/

## Maintenance model

- Python is pinned exactly by `.python-version`; CI and local release checks must report that same patch version.
- Edit build data in `data/builds/*.json`.
- Edit generated page content and each page's real `last_modified` date in `data/pages/*.json`.
- Edit visual system in `styles.css`.
- Run `python3 sitegen.py` after content or data changes.
- Verify the active runtime with `test "$(python3 -c 'import platform; print(platform.python_version())')" = "$(tr -d '[:space:]' < .python-version)"`.

## Launch checklist

- [x] Python runtime pinned to `3.14.6` through `.python-version` and CI `python-version-file`
- [x] Static pages
- [x] SEO titles/descriptions and valid JSON-LD
- [x] `robots.txt` and `sitemap.xml`
- [x] About / Contact / Privacy Policy
- [x] Google Search Console URL-prefix property and verification
- [x] Advertising disabled until a Google-certified consent management platform is configured

## Current patch

The site tracks **0.5.4c Early Access** as the latest official patch, posted 2026-07-17 according to the date displayed on the canonical forum thread: https://www.pathofexile.com/forum/view-thread/3985152. Build cards keep their actual last-reviewed patch and visibly show `needs_review` when they have not been retested. Site metadata was last regenerated 2026-07-19.

## Advertising status

Ad loading is intentionally disabled on every page. The publisher declaration remains in `ads.txt`, but no AdSense, DoubleClick, or other advertising script is loaded until a Google-certified consent management platform is configured and the privacy policy is updated.
