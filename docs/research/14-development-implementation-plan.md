# Finding 14: Development implementation plan — PoE2 Build Decision Assistant

Research date: 2026-06-16
Repo: `/Users/yupeng/Downloads/money`
Live target: https://brickerp.github.io/poe2-build-lab/

## Executive decision

The product should stay a lightweight static site for the first implementation cycle, but it must stop being only article pages. The next version should introduce a machine-readable build data layer and render pages/tools from that data.

Target product:

> A PoE2 build decision assistant that connects build choice, patch validity, attributes, gear slots, defenses, trade handoff, and official `.build` import files.

Do not build a generic PoE2 blog or a PoE Ninja clone. The defensible wedge is the decision chain:

`class/ascendancy -> passives -> skills/supports/spirit -> attributes -> gear slots/base types -> affixes/mod tiers -> defenses -> budget/trade -> patch validity -> in-game .build handoff`

## Canonical development contract

Treat this document as the implementation source of truth for the next product cycle. Earlier research cards remain evidence and background, but day-to-day development should use this document for:

- product scope
- feature priority
- data model
- repository structure
- validation requirements
- patch/content operations
- release readiness
- non-goals

If a future research card changes a product decision, update this document in the same commit or before implementation begins. Do not let implementation depend on scattered implicit knowledge from cards `01`-`13`.

Product framing:

- Build the strongest PoE2 build decision assistant first.
- Do not try to beat Maxroll on total guide volume in the MVP.
- Do not try to beat PoE2DB on raw database completeness.
- Do not try to beat PoE Ninja on live economy/meta snapshots.
- Win by connecting decisions that other tools leave separate: trust, attributes, gear, trade filters, defenses, and `.build` handoff.

## Competitive-analysis quality check

`13-competitive-analysis.md` is usable and directionally strong.

What it gets right:

- It does not overclaim. It acknowledges Maxroll, Mobalytics, PoE2DB, official trade, and Reddit each solve part of the problem.
- It identifies the real gap as workflow discontinuity, not lack of content.
- It correctly avoids fixed price promises and raw database mirroring.
- It aligns with the prior 12 research cards: build trust, `.build` files, attribute starvation, gear slot specificity, defenses, trade volatility, and data provenance.
- It turns competitor strengths into implementation patterns rather than treating competitors as irrelevant.

Small caution:

- Mobalytics already has planner/export mindshare, so `.build` export alone is not enough. The implementation must pair export with trust metadata, slot-level gear priorities, attribute warnings, and trade handoff.
- PoE2 economic/meta data may change quickly. Any page that implies current meta strength must carry `patch_version`, `last_reviewed`, and a stale-content warning.

No blocking questions remain. The plan below is implementable with the current repo.

## Priority model

Prioritize by:

1. User decision value: does it answer a painful "what should I do next?" question?
2. Differentiation: does it connect systems competitors leave separate?
3. Static-site feasibility: can it work on GitHub Pages without a backend?
4. Data risk: can claims be sourced and maintained without scraping or stale price promises?

Priority labels:

- `P0`: foundation required before the product can become a build assistant.
- `P1`: MVP user-facing value, should ship first.
- `P2`: high-value differentiators after the data layer exists.
- `P3`: expansion and SEO/content depth.
- `Later`: useful but should not distract from the decision-assistant wedge.

## Current repo constraints

Current architecture:

- Static GitHub Pages site.
- Single Python generator: `sitegen.py`.
- Generated HTML pages at repo root, `guides/`, `builds/`, and `tools/`.
- No package manager, no backend, no build pipeline beyond running Python.
- Search Console and AdSense already configured.

Implication:

- Keep the first implementation plain Python + JSON + vanilla JS.
- Add structure incrementally instead of migrating immediately to a frontend framework.
- Use generated static HTML for SEO pages.
- Use small client-side JS only for calculators and interactive filters.

## Target repo structure

Recommended structure after Phase 1-3:

```text
data/
  builds/
    schema.json
    starter-elemental-caster.json
    starter-minion-witch.json
  official/
    manifest.json
    passive-tree.json
    base-items.json
    skill-gems.json
    support-gems.json
  sources/
    official-links.json
    patch-notes.json
scripts/
  validate_builds.py
  export_build_files.py
  fetch_official_passive_tree.py
  normalize_official_data.py
  check_patch_status.py
assets/
  js/
    attribute-calculator.js
    gear-swap-validator.js
    build-filters.js
  builds/
    starter-elemental-caster.build
    starter-minion-witch.build
builds/
  index.html
  starter-elemental-caster.html
  starter-minion-witch.html
tools/
  attribute-checker.html
  gear-upgrade-checker.html
docs/
  research/
```

Do not add a backend in the MVP. Static files are enough for the first decision assistant.

Official data files may start partial. A partial official data file is acceptable only if:

- its `manifest.json` records source URL, fetch date, patch, and coverage notes
- the validator knows which fields are authoritative
- published pages do not present missing data as exact

## Build data model

Add `data/builds/schema.json` and one JSON file per build.

Minimal build object:

```json
{
  "id": "starter-elemental-caster",
  "name": "Starter Elemental Caster",
  "patch_version": "0.5.2 Early Access",
  "last_reviewed": "2026-06-16",
  "status": "draft",
  "review_state": "needs_testing",
  "known_broken_by_patch": [],
  "source": {
    "type": "self-authored",
    "url": "",
    "notes": "Research-backed starter archetype; not a copied creator build."
  },
  "trust": {
    "score": 3,
    "proof": ["research-card", "manual-review"],
    "source_type": "self-authored",
    "verified_at": "2026-06-16",
    "budget_floor": "low",
    "controller_friendly": "unknown",
    "hardcore_viable": "unknown",
    "ssf_viable": "unknown",
    "trade_viable": "yes",
    "failure_modes": ["low defenses if resistances are ignored"],
    "risks": ["not-in-game-tested", "patch-sensitive"]
  },
  "class": "Witch",
  "ascendancy": "TBD",
  "budget": "low",
  "complexity": "low",
  "gear_dependency": "low",
  "content_fit": {
    "campaign": "recommended",
    "early_maps": "viable",
    "pinnacle": "unknown"
  },
  "skills": [
    {
      "name": "Main damage skill",
      "role": "main",
      "gem_id": "TBD",
      "supports": []
    }
  ],
  "attributes": {
    "required": { "str": 0, "dex": 0, "int": 0 },
    "planned": { "str": 0, "dex": 0, "int": 0 },
    "deficit_policy": "warn",
    "notes": ["Exact requirements need gem/base data before publishing as final."]
  },
  "spirit_budget": {
    "required": 0,
    "planned": 0,
    "sources": [],
    "notes": ["Track aura/reservation assumptions and unexplained Spirit requirements."]
  },
  "gear_slots": {
    "weapon": {
      "base": "Relevant spell weapon",
      "base_item_id": "TBD",
      "attribute_requirements": { "str": 0, "dex": 0, "int": 0 },
      "priority": ["+gem levels or spell damage", "cast speed", "mana or attributes"],
      "budget_note": "Use a cheap rare during campaign; do not chase perfect affixes early."
    },
    "boots": {
      "base": "Any defensive base that meets attribute requirements",
      "priority": ["movement speed", "life or energy shield", "resistances"],
      "budget_note": "Movement speed is a practical defensive stat."
    }
  },
  "gear_swap_warnings": [
    {
      "slot": "amulet",
      "removed_stats": ["+intelligence"],
      "breaks": ["Main damage skill requirement"],
      "message": "Replacing this slot without intelligence can disable planned skills."
    }
  ],
  "defenses": {
    "campaign_targets": ["cap practical elemental resistances when possible", "keep life/ES current"],
    "map_mods_to_avoid": ["TBD"]
  },
  "trade_handoff": {
    "enabled": false,
    "filters": []
  },
  "build_file": {
    "enabled": false,
    "path": ""
  }
}
```

Rules:

- `TBD` is allowed in drafts but not in published build pages that claim exact mechanics.
- Every published build must have `patch_version`, `last_reviewed`, `review_state`, `source`, `trust`, `budget`, `complexity`, `gear_dependency`, `content_fit`, and `risks`.
- Every published build must expose `known_broken_by_patch`, even when the value is an empty list.
- Every published build must expose controller, hardcore, SSF, and trade viability as `yes`, `no`, or `unknown`.
- Every build that uses reservation, auras, persistent buffs, or Spirit-gated mechanics must include `spirit_budget`.
- Any exact passive/skill IDs must come from official data or exported game-compatible data.
- `.build` export must not be enabled until required passive, skill, support, and inventory slot IDs are no longer placeholders.
- Community data can guide authored recommendations, but pages must not bulk-republish raw database tables.

## Development workflow

Use this workflow for every feature/page/tool:

1. Research card
   - Confirm the user pain and source category in `docs/research/`.
   - Decide whether the work is a page, data model, generator feature, or calculator.

2. Data first
   - Add or update structured JSON.
   - Add validation rules before relying on the data in generated pages.
   - If exact IDs or requirements are involved, add or update official data ingest before rendering.

3. Render second
   - Extend `sitegen.py` or split it into generator modules if the file becomes hard to maintain.
   - Generate static HTML from the same data object used by tools/exporters.

4. Tooling/export third
   - Add `.build` export, calculators, or trade handoff only after the build data has the required fields.

5. Verify
   - Run generator.
   - Run schema/data validation.
   - Inspect generated pages locally.
   - Check sitemap includes new public pages.

6. Publish
   - Commit with a Lore-format commit message.
   - Deploy through GitHub Pages.
   - After deployment, inspect live URL and submit/monitor Search Console if major pages changed.

## Phase plan

### Phase 0 — Foundation cleanup and safety rails

Priority: `P0`

Goal:

Make the static site safe to grow from article MVP into data-backed build assistant.

Tasks:

- Add `data/builds/` and `data/builds/schema.json`.
- Add `scripts/validate_builds.py`.
- Add `data/official/manifest.json` even before all official datasets are available.
- Add a generator helper layer inside `sitegen.py` or separate `scripts/sitegen/` if needed.
- Add common page metadata support:
  - `patch_version`
  - `last_reviewed`
  - `review_state`
  - `known_broken_by_patch`
  - `source_links`
  - `stale_warning`
- Add a visible research-backed disclaimer for build pages.
- Keep existing pages and SEO URLs stable.

Acceptance criteria:

- `python3 sitegen.py` still regenerates the site.
- `python3 scripts/validate_builds.py` passes.
- Existing pages keep their current URLs.
- New schema rejects missing patch/trust fields for published builds.
- New schema rejects missing full trust rubric fields for published builds.

Stop condition:

- The site can load build JSON and fail fast on invalid published build data.

### Phase 0.5 — Official data ingest

Priority: `P0`

Goal:

Prevent `.build` export, attribute calculation, and gear-swap warnings from getting stuck at `TBD`.

This phase is part of the foundation, not a later enhancement. Build Cards can render draft guidance before all IDs are known, but exact import/export and requirement calculators depend on authoritative data.

Tasks:

- Add `scripts/fetch_official_passive_tree.py`.
- Add `scripts/normalize_official_data.py`.
- Fetch or vendor official/passive-tree data from GGG export.
- Create `data/official/manifest.json` with:
  - source URL
  - fetched_at
  - patch_version
  - dataset type
  - coverage status
  - known gaps
- Normalize and store:
  - passive tree node IDs
  - class/ascendancy metadata when available
  - skill gem IDs when available from official or game-compatible source
  - support gem IDs when available from official or game-compatible source
  - base item requirement data when available
- Mark unsupported datasets explicitly rather than guessing.
- Add validator checks that prevent published `.build` export from using placeholder IDs.

Acceptance criteria:

- `data/official/manifest.json` records official-data provenance.
- Passive tree data can be loaded by validation/generation code.
- Build JSON can reference official IDs and fail when IDs are unknown in published export mode.
- Missing gem/base datasets are represented as known gaps, not silent assumptions.

Stop condition:

- There is a documented path from official data source -> normalized JSON -> build schema -> `.build` exporter or calculator.

### Phase 1 — Build Cards MVP

Priority: `P1`

Goal:

Ship the first differentiated user-facing object: structured build cards with trust, budget, risk, and patch metadata.

Tasks:

- Create `builds/index.html` generated from `data/builds/*.json`.
- Create at least two starter build JSON files:
  - starter ranged elemental caster
  - starter minion/companion Witch
- Add per-build pages:
  - summary
  - who should play it
  - patch/trust block
  - known broken-by-patch block
  - budget/complexity/gear dependency
  - controller/HC/SSF/trade viability
  - skills/supports section
  - passive milestones placeholder
  - gear slot priorities
  - Spirit budget when relevant
  - defensive checklist
  - known risks and failure modes
- Replace the old "Best beginner build archetypes" page link emphasis with build-card navigation while keeping the old URL alive.

Acceptance criteria:

- A new user can compare starter builds without reading a long guide.
- Every build card answers:
  - Is this beginner-friendly?
  - Is it patch-reviewed?
  - Is it expensive?
  - What can go wrong?
  - What content is it suitable for?
  - Is it controller/HC/SSF/trade friendly?
  - What gear slots matter first?

Stop condition:

- Two build cards are published and included in sitemap/nav.

### Phase 2 — `.build` export

Priority: `P1`

Goal:

Turn build pages into game handoff pages, not just reading material.

Tasks:

- Read official Build Planner docs before implementation.
- Use Phase 0.5 official data before enabling export for any published build.
- Add `scripts/export_build_files.py`.
- Map build JSON fields to official `.build` JSON:
  - build name
  - author
  - description
  - ascendancy
  - passives by ID where available
  - skills/supports by ID where available
  - `inventory_slots` hints from gear slot priorities
- Write exported files under `assets/builds/*.build`.
- Add download button on build pages.
- Add install instructions page:
  - Windows path
  - SteamOS path if verified
  - note that in-game editing is not currently supported
- Add export validation:
  - valid JSON
  - required top-level fields
  - no `TBD` IDs in published export files
  - no stale `patch_version` mismatch between build JSON and official data manifest unless explicitly allowed

Acceptance criteria:

- Published build pages with `build_file.enabled=true` have a downloadable `.build` file.
- Export script refuses to publish placeholder IDs.
- Page clearly distinguishes "guide is published" from "official import file is available."

Stop condition:

- At least one build has a valid downloadable `.build` file generated from source JSON.

### Phase 3 — Attribute, Spirit, and gear-swap calculator

Priority: `P2`

Goal:

Solve the clearest competitor gap: "Can I equip/use this after planned gear and gem changes?"

Tasks:

- Add `tools/attribute-checker.html`.
- Add `assets/js/attribute-calculator.js`.
- Add `assets/js/gear-swap-validator.js` if the logic is large enough to keep separate.
- MVP inputs:
  - current Strength/Dexterity/Intelligence
  - current Spirit
  - planned skill/gem requirements
  - planned gear/base requirements
  - attribute bonuses from gear
  - Spirit sources and reservations where relevant
- MVP outputs:
  - required attributes
  - current planned attributes
  - deficit by attribute
  - Spirit deficit or unexplained Spirit assumptions
  - which gear slots can reasonably fix the deficit
  - gear-swap warnings for slots that provide required attributes or Spirit
  - which skills/supports/items break after a planned swap
- Add per-build prefill from build JSON.
- Add MVP rule-table support:
  - if a removed slot supplies an attribute that keeps a requirement non-negative, warn
  - if a removed slot supplies required Spirit, warn
  - if a planned gem/base requirement exceeds planned attributes, warn
- Add warnings:
  - "This result is a planning aid; verify in game."
  - "Exact gem/base requirements need verified data source."

Acceptance criteria:

- User can enter current attributes and see deficits.
- User can see Spirit deficits when the build uses Spirit-gated setup.
- User can model at least one gear swap and see whether it breaks planned skills/items.
- Build page can link into calculator with the build's planned requirements.
- Calculator does not require a backend.

Stop condition:

- Attribute checker can answer "what am I missing?" and "what breaks if I swap this?" for at least the starter builds.

### Phase 4 — Gear slot priorities and upgrade planner

Priority: `P2`

Goal:

Replace generic "get better gear" advice with slot-specific upgrade decisions.

Tasks:

- Expand `gear_slots` in build JSON.
- Add fields:
  - base type
  - required affixes
  - good affixes
  - luxury affixes
  - budget compromise
  - campaign target
  - early maps target
  - red maps/pinnacle target where known
- Render gear slot tables on build pages.
- Add `tools/gear-upgrade-checker.html` if the static table becomes insufficient.
- Add `inventory_slots` export hint integration for `.build` files.

Acceptance criteria:

- For each starter build, a user can identify the top 3 stats per slot.
- Gear advice distinguishes required stats from luxury stats.
- Gear advice avoids exact prices unless manually dated and clearly marked.

Stop condition:

- Each published build has slot-level gear priorities for weapon, body armour, boots, rings, amulet, gloves, helmet, and belt.

### Phase 5 — Trade handoff

Priority: `P2`

Goal:

Help users search for upgrades without pretending to be a live price oracle.

Tasks:

- Add `trade_handoff.filters` to build JSON.
- For each filter recipe, store:
  - slot
  - budget tier
  - required stats
  - optional stats
  - stats to ignore at low budget
  - official trade URL if a stable prefilled link is available
- Render "How to search trade" blocks on build pages.
- Avoid current-price claims.
- Add last manual price-check date only if a human actually checked it.

Acceptance criteria:

- Build pages can tell a user what to type/filter for on official trade.
- No page claims "this costs X" without a date and source.
- Trade content remains useful even when prices move.

Stop condition:

- At least weapon, boots, rings, and amulet have trade filter recipes for one starter build.

### Phase 6 — Defense diagnostic

Priority: `P2`

Goal:

Answer "why am I dying?" with a build-aware checklist.

Tasks:

- Add defense target fields to build JSON:
  - campaign targets
  - early maps targets
  - recovery source
  - movement baseline
  - resistances
  - chaos resistance note
  - map mods to avoid
- Upgrade `tools/beginner-build-checklist.html` into a richer diagnostic.
- Add per-build defense blocks:
  - likely death pattern
  - likely cause
  - first fix
  - gear slot responsible

Acceptance criteria:

- User can map death pattern to a fix path.
- Defense guidance is stage-specific, not generic.

Stop condition:

- Starter builds include at least campaign and early-map defensive targets.

## Parallel workstream — Content and Patch Ops

Priority: `P0 ongoing`

Goal:

Keep the static site trustworthy after patches. A build assistant loses value quickly if its pages look precise but are stale.

This workstream runs alongside every development phase. It is not a P3 content task.

Daily tasks during active PoE2 patch windows:

- Check official forum patch notes and live-update threads first.
- Check official X only as an update signal, then resolve mechanics through official forum/docs or verified data.
- Scan Reddit for repeated pain points:
  - build bait/trust questions
  - attribute starvation
  - gear-swap breakage
  - Spirit confusion
  - trade/search confusion
  - post-campaign progression blockers
- If a patch may affect a published build, mark that build `review_state: needs_review` before making new claims.

Patch SLA:

- Same day as a material patch/hotfix: mark affected builds or pages as `needs_review`.
- Within 24 hours: review top-traffic pages and all published Build Cards.
- Within 72 hours: update or explicitly stale-label any page with mechanics affected by the patch.
- If exact verification is unavailable, keep the warning visible and set affected fields to `unknown` rather than guessing.

Weekly tasks:

- Check Search Console for impressions, clicks, queries, and low-CTR pages.
- Promote repeated Reddit/Search Console pain into research notes and then pages/tools.
- Review stale builds by `last_reviewed` age.
- Add or update 2-5 pages only when they answer real long-tail demand.
- Remove or de-index thin pages rather than expanding volume for its own sake.

Operational fields:

- `review_state`: `current`, `needs_review`, `stale`, `broken`, `draft`
- `last_reviewed`: date of last meaningful mechanics review
- `known_broken_by_patch`: list of patch IDs or notes that invalidate the build
- `review_notes`: short human-readable reason for current state

Acceptance criteria:

- A patch can never silently leave published build pages appearing current when they are known to be unreviewed.
- Every published build has a visible review state.
- Weekly content additions are tied to a documented user query or pain point.

Stop condition:

- Patch freshness is enforceable through data fields and validation, not only editorial discipline.

### Phase 7 — Content and endgame expansion

Priority: `P3`

Goal:

Grow SEO and retention after the core assistant exists.

Tasks:

- Add guide pages from research:
  - how to use PoE2 `.build` files
  - PoE2 attribute requirements explained
  - why can't I equip this gem?
  - beginner gear stat priorities
  - build bait checklist
  - beginner defensive layers
  - what to do after campaign
- Add Endgame Hub later:
  - Atlas first steps
  - waystone sustain
  - boss unlock tracker
  - mechanic reward tables
  - known progression blockers
- Use `docs/research/11-social-source-strategy.md` cadence:
  - Reddit for recurring pain
  - official forum/docs for mechanics
  - X only as update signal

Acceptance criteria:

- Each new page maps to a real query/pain.
- Each mechanics claim has official, wiki, PoE2DB, or clearly labeled community backing.
- Thin content is avoided.

Stop condition:

- Core assistant pages exist before broad endgame content expansion.

## Feature priority backlog

| Priority | Feature | Why now | Main files |
| --- | --- | --- | --- |
| P0 | Build JSON schema + validator | Required for every later feature | `data/builds/schema.json`, `scripts/validate_builds.py` |
| P0 | Patch/source metadata renderer | Prevents stale build trust failure | `sitegen.py`, build JSON |
| P0 | Official data ingest | Unblocks `.build` export, IDs, attributes, and gear-swap validation | `data/official/`, `scripts/fetch_official_passive_tree.py`, `scripts/normalize_official_data.py` |
| P0 ongoing | Content and patch ops | Prevents patch churn from destroying trust | `scripts/check_patch_status.py`, build JSON, `docs/OPERATIONS.md` |
| P1 | Build Cards index and detail pages | First real product shift from article site to assistant | `data/builds/*.json`, `builds/*.html` |
| P1 | `.build` export pipeline | High demand and strong handoff value | `scripts/export_build_files.py`, `assets/builds/*.build` |
| P2 | Attribute/Spirit/gear-swap calculator | Strong competitor gap and beginner pain | `tools/attribute-checker.html`, `assets/js/attribute-calculator.js`, `assets/js/gear-swap-validator.js` |
| P2 | Slot-level gear priorities | Makes build advice actionable | build JSON, generated build pages |
| P2 | Trade handoff recipes | Bridges build needs to official trade without price risk | build JSON, generated build pages |
| P2 | Defense diagnostic | Solves repeated "why am I dying?" pain | build JSON, checklist tool |
| P3 | Endgame hub | Useful SEO and retention, but secondary to build assistant | `guides/`, `tools/` |
| Later | Live price tracking | High maintenance and not needed for MVP | likely backend, not GitHub Pages |
| Later | Full PoB-style simulator | Too broad; existing tools already own this | separate product decision |

## Implementation details

### Generator evolution

Start by extending `sitegen.py`, but split if it becomes hard to review.

Suggested internal functions:

```text
load_builds()
validate_page_metadata()
render_build_index(builds)
render_build_page(build)
render_patch_badge(build)
render_trust_block(build)
render_review_state(build)
render_gear_slots(build)
render_spirit_budget(build)
render_defense_block(build)
render_trade_handoff(build)
write_static_pages()
write_sitemap(pages)
```

If the file exceeds comfortable review size, move helpers to:

```text
scripts/sitegen/models.py
scripts/sitegen/render.py
scripts/sitegen/pages.py
```

Keep `python3 sitegen.py` as the main command so current operations remain simple.

### Validation rules

`scripts/validate_builds.py` should fail on:

- invalid JSON
- duplicate build IDs
- published build missing `patch_version`
- published build missing `last_reviewed`
- published build missing `review_state`
- published build missing `known_broken_by_patch`
- published build missing `source`
- published build missing full trust/risk metadata
- published build missing controller/HC/SSF/trade viability fields
- published build using an invalid `review_state`
- `.build` export enabled while IDs are `TBD`
- `.build` export enabled while official data manifest does not cover required IDs
- published exact requirement using a dataset marked as missing or unverified
- gear slot missing priority list
- Spirit-gated build missing `spirit_budget`
- gear-swap warning references a slot that does not exist
- trade handoff containing exact price without `checked_at`
- published page older than configured review window while `review_state` is still `current`

### CI and PR gates

Add GitHub Actions once Phase 0 introduces scripts.

Required PR checks:

```bash
python3 scripts/validate_builds.py
python3 sitegen.py
python3 scripts/export_build_files.py --check
python3 scripts/check_patch_status.py --check
```

CI should fail when:

- generated files are stale after `sitegen.py`
- build schema validation fails
- export-enabled builds cannot produce valid `.build` JSON
- published pages include unresolved `TBD` in exact-mechanics sections
- sitemap omits a public generated page
- review-state SLA is violated

If GitHub Actions is not set up yet, run the same commands locally before every commit.

### SEO and sitemap rules

- Generated public pages must be in `sitemap.xml`.
- Draft builds should not be linked from public index or sitemap.
- Page title should include build name + PoE2 + patch context when useful.
- Meta description should describe the decision job, not just the class name.

Example:

```text
Starter Elemental Caster PoE2 Build Card for 0.5.2
Patch-reviewed PoE2 starter caster build card with budget, gear priorities, attributes, defenses, and .build import status.
```

### UI rules

- Build cards should be scannable before deep reading.
- Use compact tags for:
  - patch
  - budget
  - complexity
  - gear dependency
  - import file status
  - stale warning
- Put the highest-value actions near the top:
  - Download `.build` if available
  - Open attribute checker
  - See gear priorities
  - View trade handoff
- Avoid a marketing landing page for tools; make the tool itself the page.

### Data provenance

Use source hierarchy:

1. Official Path of Exile developer docs and patch notes.
2. GGG official data exports.
3. In-game/manual testing when available.
4. PoE2DB/Wiki as labeled supplemental data.
5. Reddit/YouTube/community as pain discovery and creator-source metadata, not sole mechanical proof.

Every generated page should expose enough provenance to answer:

- where did this build come from?
- when was it last checked?
- what patch is it for?
- what is still unknown?

### Success metrics

MVP success is not "more pages than competitors." Track whether users can complete the decision jobs.

Product metrics:

- number of published Build Cards with full trust metadata
- number of published builds with valid `.build` export
- number of builds with attribute/Spirit prefill
- number of builds with gear-swap warnings
- number of builds with trade handoff recipes
- number of stale or `needs_review` builds visible to users

SEO and discovery metrics:

- Search Console impressions for build-file, attribute, gear, and beginner queries
- click-through rate for Build Card pages
- indexed page count for non-thin pages
- query growth around "PoE2 build file", "attribute requirements", "gear stat priority", and "build bait"

Quality metrics:

- zero published exact-mechanics pages with unresolved `TBD`
- zero export-enabled builds with invalid `.build` JSON
- zero silent stale builds after a material patch
- every new public page has source/provenance metadata

## Verification checklist

Run before claiming a phase complete:

```bash
python3 scripts/validate_builds.py
python3 sitegen.py
python3 scripts/export_build_files.py --check
python3 scripts/check_patch_status.py --check
```

Then check:

- no command failed
- generated HTML exists for expected routes
- `sitemap.xml` includes public pages
- draft pages are not indexed
- stale or `needs_review` builds are visibly labeled, not silently presented as current
- no `TBD` appears on pages that claim exact build import support
- no `TBD` appears in exact attribute, Spirit, passive, skill, support, or base-item sections on published pages
- `.build` files are valid JSON
- export-enabled builds match the official data manifest coverage
- links to local CSS and nested pages resolve
- mobile layout does not break tables/cards
- calculators work without a backend
- trade handoff has text fallback even if official trade deep links change

For visual smoke testing:

```bash
python3 -m http.server 8000
```

Open:

- `http://localhost:8000/`
- `http://localhost:8000/builds/`
- one generated build page
- `http://localhost:8000/tools/attribute-checker.html`
- any page that contains a stale/review warning

## Release sequence

Recommended first release:

1. Phase 0 foundation.
2. Phase 0.5 official data ingest, at least passive tree manifest and known gaps.
3. Content and Patch Ops fields plus validation.
4. Phase 1 Build Cards with two starter builds.
5. Publish Build Cards without `.build` export if IDs are not ready, but show import status honestly.
6. Add `.build` export for one build once official IDs are verified.
7. Add Attribute/Spirit/Gear-swap Calculator.
8. Add slot-level gear priorities and trade handoff recipes for the first exported build.

Reason:

- Build Cards create visible value immediately.
- `.build` export is powerful but should not ship with placeholder IDs.
- Official data ingest prevents calculator/export work from becoming permanent `TBD`.
- Patch-state validation protects trust while the site is still small.
- Attribute Calculator can start with manual inputs, but exact prefilled requirements must come from verified data.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Stale patch/meta advice | Require `last_reviewed`, `review_state`, `known_broken_by_patch`, patch warning, and source links |
| Copyright/data scraping risk | Do not bulk clone PoE2DB/wiki data; write transformed guidance with attribution |
| False precision in prices | Use trade filter recipes, not price promises |
| `.build` files invalid | Add exporter validation and do not export placeholders |
| Official data gaps block exact features | Track gaps in `data/official/manifest.json`; ship honest draft guidance without pretending exactness |
| Trust rubric becomes too shallow | Require controller/HC/SSF/trade viability, proof, failure modes, and risks in schema |
| Gear-swap breakage remains unsolved | Implement rule-table warnings before attempting advanced simulation |
| Patch operations become manual memory | Add `scripts/check_patch_status.py --check` and visible review states |
| Overbuilding before traffic | Keep MVP static and data-backed; avoid backend/live prices |
| Competing with Maxroll directly | Focus on decision chain and tool handoff, not prose guide depth |
| Too many build pages to maintain | Start with curated starter builds and clear draft/published status |

## Definition of done

The first complete implementation is done when:

- The repo has a validated `data/builds/*.json` layer.
- The repo has `data/official/manifest.json` and at least passive-tree provenance documented.
- The site renders a build index and at least two build detail pages from JSON.
- Each build page shows patch, review state, source, trust, budget, complexity, gear dependency, content fit, controller/HC/SSF/trade viability, gear slots, defenses, failure modes, and known risks.
- Published builds expose `known_broken_by_patch` and `last_reviewed`.
- At least one build has a valid generated `.build` download, or the UI clearly says import file is not yet available.
- The attribute checker exists and can calculate simple Str/Dex/Int deficits.
- Spirit budget is represented when relevant.
- Gear-swap warnings exist for at least one starter build where a slot carries required attributes or Spirit.
- At least one build has trade handoff recipes with text fallback.
- Patch status validation can mark or fail stale builds.
- Generated pages are in sitemap and can be served locally.
- CI or local PR gate commands pass:
  - `python3 scripts/validate_builds.py`
  - `python3 sitegen.py`
  - `python3 scripts/export_build_files.py --check`
  - `python3 scripts/check_patch_status.py --check`
- Research-to-page and content/patch ops workflow remain documented here.

## Non-goals for MVP

- Live price tracking.
- Full DPS simulation.
- Full passive-tree visual editor.
- Bulk mirrored item/mod database.
- User accounts.
- Backend service.
- Ranking every community build.
- Becoming a broad Maxroll-style guide library before the decision-assistant core works.

These can be reconsidered after the data-backed static assistant proves user value.
