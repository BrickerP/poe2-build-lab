# Finding 06: Gear advice must be slot/base/affix-specific, not generic "get better gear"

## Research result

PoE2 players struggle to identify whether an item is good because item value depends on slot, base type, attribute requirements, build damage scaling, defenses, sockets/quality/runes, and trade price. Generic gear advice is not enough.

## Evidence

PoE2DB exposes the depth of the item/modifier surface. Its modifier page separates modifiers by item classes and bases, including one-handed weapons, two-handed weapons, rings, amulets, belts, gloves, boots, body armours, helmets, shields, foci, quivers, jewels, flasks, charms, relics, tablets, and waystones.

Official Build Planner schema supports `inventory_slots` and hover text for gear stat priorities. The official example explicitly uses inventory slot hints such as weapon, body armour, boots, helmet, gloves, belt, rings, and amulet with ranked stat priorities.

Community signals include questions about:

- Act 1 gearing
- which armour type to use for Mercenary
- whether to prioritize physical or lightning damage on a weapon
- attribute-stacking gear and expensive attribute/resistance combinations
- spirit totals that seem unexplained from visible gear

## User pain

Players need slot-level answers:

- Which base type fits my build?
- What are the top 3 affixes for this slot?
- What is an acceptable campaign item vs endgame item?
- Which stat can I compromise on when budget is low?
- Does this build need a unique, a rare weapon, or generic life/resist gear?

## Product implication

Create gear modules per build:

```yaml
gear_slots:
  Weapon1:
    base: Any high physical DPS two-handed mace
    priority:
      - highest physical DPS
      - attack speed if relevant
      - +level / flat damage if build-specific
    budget_note: campaign rare is enough until maps
  BodyArmour1:
    base: armour/evasion/es class-specific
    priority:
      - life
      - resistances
      - primary defense
      - attributes if stat-starved
```

## Sources

- PoE2DB Modifiers: https://poe2db.tw/us/Modifiers
- Official Build Planner docs and inventory slot example: https://www.pathofexile.com/developer/docs/game
- Reddit: Act 1 gearing: https://www.reddit.com/r/PathOfExile2/comments/1mvcm06/act_1_gearing/
- Reddit: Mercenary armour question: https://www.reddit.com/r/pathofexile2builds/comments/1hh1po4/newbie_best_type_of_armor_for_mercenary_is/
- Reddit: Galvanic shards weapon stat priority appears in subreddit feed: https://www.reddit.com/r/pathofexile2builds/
- Reddit: ELI5 spirit from gear: https://www.reddit.com/r/PathOfExile2/comments/1il2oxx/eli5_how_are_builds_getting_so_much_spirit/
