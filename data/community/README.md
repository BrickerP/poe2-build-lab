# Community-extracted data (NOT official)

This directory holds **community**-sourced Path of Exile 2 game data, kept
separate from `data/official/` so provenance is never ambiguous.

GGG publishes **no** official skill-gem, support-gem, or base-item export — only
the passive/atlas trees (see `data/official/`). To unblock a real, working
`.build` export, this project accepts community-extracted ids, with clear
attribution and **no bulk-republishing** as site content. Only the id mappings
needed to resolve builds and power export are ingested.

## Sources (pinned by commit in `data/sources/community-links.json`)

| Dataset | Source | Field used | Why |
| --- | --- | --- | --- |
| `skill-gems.json`, `support-gems.json` | [Path of Building Community (PoE2)](https://github.com/PathOfBuildingCommunity/PathOfBuilding-PoE2) `src/Data/Gems.lua` | each gem's `gameId` | Exact in-game `.build` metadata id. Cross-validated against GGG's official `.build` example. |
| `base-items.json` | [RePoE fork (PoE2)](https://github.com/repoe-fork/poe2) `data/base_items.json` | metadata key | Equippable base ids + attribute requirements for on-page exact base reqs. |

Underlying game data is © Grinding Gear Games. Tooling licenses: Path of
Building is MIT; RePoE tooling is MIT (© 2016 brather1ng).

## Why `gameId` (gems) and not the table key

PoE2 gem metadata paths are **irregular** — e.g. `Metadata/Items/Gems/SkillGemSpark`
(plural `Gems`) but `Metadata/Items/Gem/SkillGemFireball` (singular `Gem`). The
Path of Building table is keyed by an internal display id, while each entry's
`gameId` is the actual path the in-game File Watcher expects. We take the exact
`gameId` per gem rather than applying any blanket convention, so no id is
fabricated or transformed.

## What is vendored vs fetched

- `raw/pob-poe2-gems.lua` is **vendored** (committed) so the custom Lua→JSON
  parser can be audited and re-run offline.
- The 7.5 MB RePoE `base_items.json` raw is **git-ignored** (fetched
  transiently); only the compact normalized `base-items.json` is committed.

## Refresh

```bash
python3 scripts/fetch_community_data.py        # download pinned snapshots
python3 scripts/normalize_community_data.py     # -> skill-gems/support-gems/base-items.json
python3 scripts/validate_builds.py              # re-validate
python3 sitegen.py                              # regenerate
```
