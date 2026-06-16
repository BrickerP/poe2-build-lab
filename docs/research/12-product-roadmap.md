# Finding 12: Product roadmap should move from content site to build/gear utility site

## Research result

The original site can attract early indexation, but it will not become meaningfully useful or defensible until it supports build, gear, attributes, and import/export. The product should become a lightweight PoE2 build lab, not a generic blog.

## Phase 1: Research-backed content cleanup

- Correct any stale patch wording.
- Add visible patch/source metadata to every guide.
- Add research-backed pages for:
  - how to use `.build` files
  - attribute requirements explained
  - gear stat priorities by slot
  - how to judge whether a build is bait
  - beginner defense checklist

## Phase 2: Build cards

Add `data/builds/*.json` and render one build card per build:

- patch version
- source link
- trust score
- class/ascendancy
- skills/supports
- passive milestones
- gear slot priorities
- attributes required
- budget tier
- known risks

## Phase 3: `.build` file exporter

Use official Build Planner schema to generate JSON `.build` files from build cards.

Acceptance criteria:

- exported file validates as JSON
- includes passives, skills/supports, and inventory slot hints
- includes safe install instructions for Windows/SteamOS
- page explains that in-game editing is not currently supported

## Phase 4: Attribute and gear calculator

Static client-side calculator:

- input current attributes
- input planned gems/gear
- calculate deficits
- show which gear slots can fix missing stats
- warn when gear swap breaks skills

## Phase 5: Trade handoff and revenue pages

- generate official trade-search guidance/filters
- avoid volatile price guarantees
- add affiliate only if policy-safe
- add AdSense only after account approval and enough original content

## SEO angle

High-value long-tail pages:

- "how to use PoE2 build files"
- "PoE2 attribute requirements explained"
- "why can't I equip this gem PoE2"
- "PoE2 beginner gear stat priorities"
- "PoE2 build bait checklist"
- "PoE2 0.5 starter build import file"

## Sources

- Official Build Planner docs: https://www.pathofexile.com/developer/docs/game
- Official Return of the Ancients live update thread: https://www.pathofexile.com/forum/view-thread/3933988
- Reddit build index/trust warning: https://www.reddit.com/r/pathofexile2builds/comments/1tny1to/05_return_of_the_ancients_league_starter_build/
- Reddit build planner demand: https://www.reddit.com/r/pathofexile2builds/comments/1tsen1b/popular_guides_with_the_new_in_game_build_planner/
- PoE2DB data surface: https://poe2db.tw/us/Modifiers
- GGG skill tree export: https://github.com/grindinggear/poe2-skilltree-export
