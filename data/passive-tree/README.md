# Passive tree data (official GGG export)

This directory holds the raw official Path of Exile 2 passive skill tree export.

- **Expected file:** `data.json`
- **Source:** [`grindinggear/poe2-skilltree-export`](https://github.com/grindinggear/poe2-skilltree-export) → `data.json`
- **Pinned patch:** `0.5.2 Early Access` (see `data/official/manifest.json`)

The raw export is **not vendored yet** because the fetch requires network egress
that is not available in the current build environment.

## How to populate it

```bash
# 1. Download the raw GGG export (needs internet)
python3 scripts/fetch_official_passive_tree.py

# 2. Normalize it into data/official/passive-tree.json (node ids + classes)
python3 scripts/normalize_official_data.py

# 3. Re-validate and regenerate
python3 scripts/validate_builds.py
python3 sitegen.py
```

Until `data.json` exists and the manifest reports `coverage: "complete"`,
`.build` export stays disabled and build cards keep `TBD` passive node ids
(allowed only in `draft` builds — see `scripts/validate_builds.py`).
