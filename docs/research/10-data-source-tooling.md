# Finding 10: The tool stack should combine official exports with community databases carefully

## Research result

A serious PoE2 guide site needs data. The safest architecture is official sources first, then clearly labeled community data for gaps.

## Evidence

Official sources:

- Path of Exile developer docs define the Build Planner file schema.
- Grinding Gear Games maintains `poe2-skilltree-export`, exported data for PoE2's passive skill tree.
- The official data export currently includes thousands of passive tree nodes and class metadata.
- X official account announced JSON availability for the Return of the Ancients skill tree.

Community / supplemental sources:

- PoE2DB provides extracted/collected data for item modifiers, skill gems, support gems, base types, waystones, tablets, and more.
- r/pathofexile2builds community bookmarks recommend PoE2DB, Craft of Exile POE2, wiki, Path of Building Community, and Filterblade.

## Local verification

A direct fetch of `grindinggear/poe2-skilltree-export` `data.json` on 2026-06-16 showed:

- `nodes`: 5,151
- `groups`: 1,621
- `classes`: 12

This confirms a static site can ingest official passive tree data without a backend.

## Product implication

Data-layer plan:

1. `data/passive-tree.json` from GGG export
2. `data/builds/*.json` authored by us
3. optional `data/modifiers/*.json` derived manually or from clearly labeled community sources
4. schema validation script for `.build` output
5. provenance metadata on every generated page

## Source risk

Do not silently scrape and republish all community data as if it were official. For AdSense/SEO safety, use transformed guidance, attribution, and original analysis instead of bulk database cloning.

## Sources

- Official developer docs: https://www.pathofexile.com/developer/docs/game
- GGG passive tree export repo: https://github.com/grindinggear/poe2-skilltree-export
- Official X JSON availability: https://x.com/pathofexile/status/2059140111355482420
- PoE2DB Modifiers: https://poe2db.tw/us/Modifiers
- r/pathofexile2builds resources: https://www.reddit.com/r/pathofexile2builds/
