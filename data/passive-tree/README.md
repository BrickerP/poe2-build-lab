# Passive tree data (official GGG export)

This directory holds the raw official Path of Exile 2 passive skill tree export.

- **File:** `data.json` (vendored / committed — pinned snapshot)
- **Source:** [`grindinggear/poe2-skilltree-export`](https://github.com/grindinggear/poe2-skilltree-export) → `data.json`
- **Official confirmation:** [GGG developer data exports](https://www.pathofexile.com/developer/docs/data)
- **Pinned patch:** see `data/official/manifest.json`

The raw export is vendored so validation, generation, and the `.build` exporter
work on a fresh checkout (and in CI) without network egress.

## What this export provides

`scripts/normalize_official_data.py` derives `data/official/passive-tree.json`:

- passive node ids — numeric (`skill`) and semantic (`id`, used by `.build` passives)
- per-class base attributes (Str/Dex/Int)
- ascendancy code ↔ name mapping (e.g. `Sorceress1` → `Stormweaver`)

## What it does NOT provide

Skill gems, support gems, and base items. GGG only publishes the passive (and
atlas) trees as official exports. Those id spaces are tracked as known gaps in
`data/official/manifest.json`, stay `TBD` in build cards, and block `.build`
export — they are never fabricated.

## How to refresh it

```bash
# 1. Download the raw GGG export (needs internet)
python3 scripts/fetch_official_passive_tree.py

# 2. Normalize it into data/official/passive-tree.json
python3 scripts/normalize_official_data.py

# 3. Re-validate and regenerate
python3 scripts/validate_builds.py
python3 sitegen.py
```
