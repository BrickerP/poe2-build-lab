# Finding 03: The in-game Build Planner is the killer feature to support

## Research result

PoE2 now has an official Build Planner file format. This is the highest-leverage site capability: publish guides that export valid `.build` files so users can load them into the game.

## Evidence

Official developer docs describe the Build Planner as a PoE2-only file format. It integrates with mission-critical systems: skills, crafting, passives, and ascendancy. The game expects JSON `*.build` files in the `Preferences/BuildPlanner` directory.

The official schema supports:

- build name, author, description, ascendancy
- passives by ID, with level intervals and hover text
- skills by BaseItemTypes ID
- support skills by ID
- inventory slot hints with stat-priority hover text
- markup for colored/bold/size text

Important constraint: the docs say editing/creating builds inside PoE2 is currently not supported. That increases demand for external websites/tools that can create valid files.

## Reddit / community signal

r/pathofexile2builds shows current demand for:

- popular guides with the new in-game Build Planner
- Mobalytics Build Planner export
- where/how to use the new import build
- tools that convert PoE2 builds into `.build` files

## Product implication

Build pages should not end at prose. They should have:

- Download `.build`
- Copy install path instructions for Windows/SteamOS
- Validate JSON before publishing
- Include `inventory_slots` hints for gear upgrades
- Include passive/skill IDs from official/exported data

## Minimal data model

```json
{
  "name": "Starter build name",
  "patch": "0.5.2",
  "ascendancy": "...",
  "passives": [],
  "skills": [],
  "inventory_slots": []
}
```

## Sources

- Official Build Planner docs: https://www.pathofexile.com/developer/docs/game
- Reddit: popular guides with new in-game Build Planner: https://www.reddit.com/r/pathofexile2builds/comments/1tsen1b/popular_guides_with_the_new_in_game_build_planner/
- Reddit: Mobalytics Build Planner Export: https://www.reddit.com/r/pathofexile2builds/comments/1tq7m5q/mobalytics_build_planner_export/
- Reddit: where/how to use new import build: https://www.reddit.com/r/pathofexile2builds/comments/1tujna2/wherehow_t_use_the_new_import_build/
- Official X Build Guide system signal: https://x.com/pathofexile/status/2055755167287349304
