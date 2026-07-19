# PoE2 Build Lab operations

Live site: https://brickerp.github.io/poe2-build-lab/
Repository: https://github.com/BrickerP/poe2-build-lab
Search Console property: URL-prefix `https://brickerp.github.io/poe2-build-lab/`

## Deployment contract

- Hosting target: GitHub Pages Actions deployment of the allowlisted `dist/` artifact from `main`.
- Required repository setting: Pages build source must be GitHub Actions (`build_type=workflow`), never legacy `main` branch root publishing.
- Search Console: ownership verified with `googlead1eaf93276e5fa5.html`.
- Sitemap: submitted in Search Console as `sitemap.xml` on 2026-06-16.
- Advertising: disabled in site code. `ads.txt` retains the publisher declaration but pages load no ad network until a Google-certified consent management platform is configured.

The workflow validates generated source, rejects generator drift, packages twice to prove deterministic output, validates the packaged artifact, and deploys only on `main`. Pull requests may upload generic `dist` evidence but never deploy Pages.

Local release verification:

```sh
test "$(python3 -c 'import platform; print(platform.python_version())')" = "$(tr -d '[:space:]' < .python-version)"
test "$(node --version)" = "v$(tr -d '[:space:]' < .node-version)"
python3 sitegen.py
python3 -m py_compile sitegen.py scripts/*.py
python3 scripts/test_patch_status.py
python3 scripts/check_patch_status.py --check
python3 scripts/validate_site.py
python3 scripts/package_site.py --check-deterministic
python3 scripts/validate_site.py --root dist --dist
python3 scripts/test_validate_site.py
python3 scripts/test_runtime_site.py
```

The `dist/` allowlist contains only public HTML/runtime assets, crawl helpers, Search Console verification, `.build` downloads, the exact schema-valid published build JSON required by the three browser tools, and `.nojekyll`. It excludes source SVG, Python, non-runtime JSON, Markdown operations notes, scripts, repository metadata, and CI configuration.

Every page data record owns its real `last_modified` date. The generator uses that value for both JSON-LD `dateModified` and sitemap `lastmod`; do not replace it with the sitemap generation date. The custom 404 uses project-root paths so its CSS, favicon, navigation, and recovery link also work when GitHub Pages serves the same body for a deeply nested missing URL.

## Daily monitoring: natural traffic

Open Google Search Console for the property and check:

1. **效果 / Performance**
   - Total impressions: early signal that Google has discovered pages.
   - Total clicks: real organic traffic.
   - Queries: exact long-tail keywords users searched.
   - Pages: which guide pages are getting impressions.
2. **网页 / Pages**
   - Indexed pages vs not indexed pages.
   - Any crawl or duplicate/canonical issues.
3. **站点地图 / Sitemaps**
   - Confirm `sitemap.xml` eventually changes from temporary fetch failure to successful processing.

Early expectation: Search Console may show little or no data for several days after launch.

## Weekly content loop

Each week:

1. Pull Search Console queries with impressions but low CTR.
2. Rewrite titles/meta descriptions for those pages.
3. Add 2-5 new long-tail pages based on PoE2 player questions.
4. Update patch labels when official PoE2 patch notes change mechanics.
5. Add first-hand screenshots/testing notes once a PoE2 account is available.

Priority content backlog:

- Best Monk beginner build
- Best Mercenary beginner build
- Best Sorceress beginner build
- How to respec in PoE2
- PoE2 Spirit explained
- PoE2 campaign progression checklist
- PoE2 early gear upgrade guide
- PoE2 beginner defensive layers

## Advertising safety gate

Ad loading is intentionally disabled. Before any future advertising launch:

1. Configure a Google-certified consent management platform for all required regions.
2. Update the privacy policy to describe the exact vendors, storage, consent controls, and revocation path.
3. Review Google site and ad-serving status.
4. Keep `ads.txt` accurate; its publisher declaration does not itself load code or set cookies.
5. Add only real ad units after consent behavior is tested.

CI rejects ad-network domains in generated HTML. Do not bypass that gate to test production advertising.

## What increases revenue

- More indexed pages with search demand.
- Better CTR from Search Console query/title tuning.
- More original value: screenshots, tables, checklists, tools.
- Patch freshness: update pages quickly after official changes.
- Avoid thin/AI-only pages; they increase Search/AdSense policy risk.

## Research cadence

Before adding build pages, review `docs/research/README.md`. Each new repeated player pain point should get its own Markdown card under `docs/research/` before it becomes a page or tool.
