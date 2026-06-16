# Finding 05: Attributes and stat starvation are a recurring beginner/build pain

## Research result

PoE2 attributes are not just flavor stats. They gate gear and gem usage, and gear swaps can break skills. This is a strong opportunity for an attribute calculator and gear-swap validator.

## Evidence

PoE2 Wiki summarizes core attribute mechanics:

- Strength is required for armour/melee-aligned equipment and skills and grants life.
- Dexterity is required for evasion/ranged-aligned equipment and skills and grants accuracy.
- Intelligence is required for energy shield/spell-aligned equipment and skills and grants mana.
- Attributes can come from items or the passive tree.

Reddit pain points include:

- attribute requirements for skills feeling excessive
- players expecting to spend gear affixes on attributes/reduced requirements
- stat starvation making decent crafted items unusable
- gear/skill swaps causing hidden breakage, especially around weapon sets and skill requirements
- new players asking whether they can lock themselves out of builds

## User pain

Players need to know before they buy, craft, or respec:

- required Str/Dex/Int for planned gems and gear
- current Str/Dex/Int from tree + gear
- missing attributes after each gear swap
- whether weapon-set-specific skills will break
- whether a build is stat-stacker, attribute-light, or attribute-starved

## Product implication

Add an Attribute Budget Calculator:

```text
Inputs:
- class/ascendancy
- passive attribute nodes
- planned gems + gem levels
- item base requirements
- gear affixes with +attributes

Outputs:
- minimum required Str/Dex/Int
- current planned Str/Dex/Int
- deficit by level band
- gear slots that should carry attributes
- warning: swapping this item breaks these skills
```

## Sources

- PoE2 Wiki Attribute mechanics: https://www.poe2wiki.net/wiki/Attribute
- Reddit: attribute requirements for skills are ridiculous: https://www.reddit.com/r/PathOfExile2/comments/1jxrazy/attribute_requirements_for_skills_are_ridiculous/
- Reddit: perpetually stat starved: https://www.reddit.com/r/pathofexile2builds/comments/1h9j80r/perpetually_stat_starved/
- Reddit: gear/skill swaps causing issues: https://www.reddit.com/r/PathOfExile2/comments/1krxfwx/taking_skillsgear_off_and_putting_them_back_on_is/
- Reddit: lock yourself out of builds: https://www.reddit.com/r/PathOfExile2/comments/1hgoz76/is_it_possible_to_completely_lock_yourself_out_of/
