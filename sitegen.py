import json
from pathlib import Path
from html import escape
from datetime import date

ADSENSE_CLIENT = "ca-pub-1111218417177666"

SITE = {
    "name": "PoE2 Build Lab",
    "tagline": "PoE2 Build Decision Assistant — patch-reviewed build cards, attribute checks, gear upgrades, defenses, trade handoff, and .build import.",
    "url": "https://brickerp.github.io/poe2-build-lab/",
    "updated": "2026-06-17",
    "patch": "0.5.2 Early Access"
}

NAV = [
    ("Builds", "builds/index.html", "Compare patch-reviewed starters"),
    ("Can I Wear It?", "tools/attribute-checker.html", "Stats, Spirit & gear swaps"),
    ("Next Upgrade", "tools/gear-upgrade-checker.html", "Slot affix priorities by stage"),
    ("Why Am I Dying?", "tools/beginner-build-checklist.html", "Death pattern → fix path"),
    ("Guides", "guides/index.html", "Reference when you're stuck"),
    ("Endgame", "guides/endgame-hub.html", "Atlas, waystones & bosses"),
]

DECISION_GRID = [
    ("◇", "Pick a build", "Compare starters by budget & trust", "builds/index.html"),
    ("◆", "Can I wear this?", "Check attributes & Spirit", "tools/attribute-checker.html"),
    ("▣", "Next gear piece", "Slot affix targets by stage", "tools/gear-upgrade-checker.html"),
    ("✕", "Why am I dying?", "Death pattern → first fix", "tools/beginner-build-checklist.html"),
    ("↓", "Import .build", "Download & load in-game", "guides/import-build-files.html"),
    ("◎", "Endgame path", "Atlas & progression blockers", "guides/endgame-hub.html"),
]

# Review-state presentation. Keys must match build review_state enum values.
REVIEW_STATE_LABELS = {
    "current": ("Patch-reviewed", "ok"),
    "needs_review": ("Needs review", "warn"),
    "needs_testing": ("Needs in-game testing", "warn"),
    "stale": ("Stale", "warn"),
    "broken": ("Known broken", "bad"),
    "draft": ("Draft", "warn"),
}

VIABILITY_LABELS = {"yes": "Yes", "no": "No", "unknown": "Unknown"}

pages = [
    {
        "path": "index.html",
        "title": "PoE2 Build Lab: Path of Exile 2 Beginner Builds and Guides",
        "description": "Patch-aware Path of Exile 2 beginner builds, leveling notes, currency basics, and checklists for new and returning players.",
        "hero": True,
        "content": "__HOMEPAGE__",
    },
    {
        "path": "builds/best-beginner-builds.html",
        "title": "Best Path of Exile 2 Beginner Build Archetypes for Patch 0.5.2",
        "description": "Beginner-friendly Path of Exile 2 build archetypes for patch 0.5.2, with pros, risks, and safe gearing priorities.",
        "heading": "Best PoE2 beginner build archetypes",
        "content": """
<p class=\"lede\">If you are new to Path of Exile 2, your first build should be simple to pilot, cheap to repair, and forgiving when your gear is bad. This page ranks <em>archetypes</em>, not unverified exact meta builds.</p>
<div class=\"notice\"><strong>Updated:</strong> 2026-06-16 · <strong>Patch:</strong> 0.5.2 Early Access · This page is meant as a safe starter direction, not a promise of endgame dominance.</div>
<table>
<thead><tr><th>Starter direction</th><th>Why it is beginner-friendly</th><th>Main risk</th><th>First gearing priority</th></tr></thead>
<tbody>
<tr><td>Ranged elemental caster</td><td>Clear targeting, easier boss spacing, strong learning value for skill/support gems.</td><td>Can feel fragile if you ignore life, resistances, and movement.</td><td>Life, resistances, cast speed, relevant elemental damage.</td></tr>
<tr><td>Minion / companion-oriented Witch</td><td>Extra bodies reduce pressure while you learn enemy attacks.</td><td>Minion scaling can be confusing and patch-sensitive.</td><td>Gem levels, minion damage/survivability, defensive stats on gear.</td></tr>
<tr><td>Ranged projectile Ranger / Mercenary</td><td>Good for learning positioning, kiting, and screen control.</td><td>Requires movement discipline and weapon upgrades.</td><td>Weapon damage, attack speed, life, resistances.</td></tr>
<tr><td>Simple melee bruiser</td><td>Teaches stun windows, dodge timing, and defensive gearing.</td><td>More punishing for brand-new players because you stand closer to danger.</td><td>Weapon DPS, armour/evasion as appropriate, life, recovery.</td></tr>
</tbody>
</table>
<h2>Fast recommendation</h2>
<p>For a first character, start with a ranged elemental caster or minion-oriented Witch-style build. They let you learn boss patterns without also fighting melee range, weapon breakpoints, and perfect dodge timing at the same time.</p>
<h2>What makes a good starter build?</h2>
<ul>
<li><strong>Low currency dependence:</strong> it should function on campaign rares, not require a rare unique item.</li>
<li><strong>Simple buttons:</strong> one main damage skill, one movement/defense plan, one boss setup.</li>
<li><strong>Clear scaling:</strong> you understand whether to upgrade gem levels, weapon DPS, elemental damage, minion stats, or defenses.</li>
<li><strong>Patch resilience:</strong> if one support gem gets nerfed, the build should still be playable.</li>
</ul>
<h2>Beginner mistakes to avoid</h2>
<ul>
<li>Following an endgame showcase without checking whether it works during leveling.</li>
<li>Spending all currency on damage while entering acts with weak resistances and low life.</li>
<li>Changing several systems at once; change one skill/support setup, then test.</li>
<li>Trusting an old guide without checking the patch date.</li>
</ul>
<h2>Next step</h2>
<p>Pick one archetype, finish Act 1 with it, and keep notes on deaths: one-shot, damage too low, mana issues, or unclear mechanics. Those notes tell you what to fix before copying a more advanced build.</p>
<p>For a structured, decision-by-decision view of each starter, see the <a href=\"index.html\">build cards</a>: patch trust, budget, gear slot priorities, defenses, and import status in one place.</p>
"""
    },
    {
        "path": "guides/beginner-guide.html",
        "title": "Path of Exile 2 Beginner Guide: What to Do First",
        "description": "A practical Path of Exile 2 beginner guide covering skills, support gems, defenses, gear upgrades, and early progression habits.",
        "heading": "PoE2 beginner guide: what to do first",
        "content": """
<p class=\"lede\">Path of Exile 2 is easier when you treat the campaign as a learning lab. Your goal is not to copy a perfect build immediately; your goal is to keep damage, defenses, and movement improving together.</p>
<div class=\"notice\"><strong>Quick answer:</strong> Choose one main skill, support it properly, keep defenses current, upgrade weapons or gem levels often, and read boss attacks instead of face-tanking.</div>
<h2>1. Pick one main damage plan</h2>
<p>New players often equip every interesting skill and end up with no coherent scaling. Start with one main damage skill, one support setup, and one utility or movement option.</p>
<h2>2. Support gems matter</h2>
<p>A support gem can change how a skill behaves, how it scales, or how safe it feels. When comparing supports, test on the same enemy type and ask: does this improve clear speed, boss damage, uptime, or survival?</p>
<h2>3. Upgrade defenses before you feel stuck</h2>
<ul>
<li>Keep life or equivalent survivability on gear.</li>
<li>Watch elemental resistances as you enter harder zones.</li>
<li>Use flasks/recovery deliberately; do not wait until every fight is desperate.</li>
<li>Practice dodge timing against bosses before blaming your build.</li>
</ul>
<h2>4. Replace weak gear frequently</h2>
<p>During leveling, a plain rare item with the right stats can beat a flashy item with irrelevant modifiers. If your damage suddenly falls off, check your weapon, gem level, and support setup first.</p>
<h2>5. Learn from deaths</h2>
<table><thead><tr><th>Death pattern</th><th>Likely issue</th><th>Fix</th></tr></thead><tbody>
<tr><td>Boss one-shots you</td><td>Too little defense or missing dodge window</td><td>Add life/resists, learn telegraphs, improve spacing</td></tr>
<tr><td>Packs overwhelm you</td><td>Weak clear or poor crowd control</td><td>Improve AoE support, positioning, or utility skill</td></tr>
<tr><td>Fights take too long</td><td>Damage scaling behind curve</td><td>Upgrade weapon/gem/supports, simplify rotation</td></tr>
<tr><td>Always out of resource</td><td>Cost/recovery mismatch</td><td>Change supports, add recovery, avoid over-linking early</td></tr>
</tbody></table>
<h2>Beginner rule</h2>
<p>If a guide cannot explain how the build works before expensive items, do not use it as your first character.</p>
"""
    },
    {
        "path": "guides/classes-explained.html",
        "title": "Path of Exile 2 Classes Explained for Beginners",
        "description": "A beginner-friendly explanation of Path of Exile 2 class choice, playstyle, range, defenses, and learning curve.",
        "heading": "PoE2 classes explained for beginners",
        "content": """
<p class=\"lede\">Your class is your starting point on the passive tree and your early identity. It does not permanently lock every decision, but it strongly shapes your first hours.</p>
<table><thead><tr><th>Playstyle question</th><th>Beginner-friendly answer</th></tr></thead><tbody>
<tr><td>Do you want safer spacing?</td><td>Start ranged: caster, bow/projectile, or minion direction.</td></tr>
<tr><td>Do you enjoy timing and close-range pressure?</td><td>Melee can be satisfying, but it is less forgiving while learning bosses.</td></tr>
<tr><td>Do you want fewer active decisions?</td><td>Minions/companions can reduce pressure, but scaling details still matter.</td></tr>
<tr><td>Do you want fast clear?</td><td>Projectile or AoE spell directions often feel smoother for early mapping-style content.</td></tr>
</tbody></table>
<h2>How to choose your first class</h2>
<ol>
<li>Pick the combat range you enjoy.</li>
<li>Check whether the build needs a specific item to function.</li>
<li>Prefer clear scaling words: spell damage, elemental damage, minion damage, projectile damage, attack weapon DPS.</li>
<li>Avoid a build that needs three mechanics you do not understand yet.</li>
</ol>
<h2>What not to overthink</h2>
<p>Do not restart every time a tier list changes. In Early Access, patches move numbers around often. A stable learning build that reaches later content teaches more than rerolling into every trend.</p>
"""
    },
    {
        "path": "guides/skill-gems-explained.html",
        "title": "Path of Exile 2 Skill Gems and Support Gems Explained",
        "description": "Understand Path of Exile 2 skill gems, support gems, main skills, utility skills, and how to test gem setups safely.",
        "heading": "Skill gems and support gems explained",
        "content": """
<p class=\"lede\">Most beginner builds fail because the player swaps skills randomly instead of understanding the role of each gem.</p>
<h2>The simple model</h2>
<ul>
<li><strong>Main skill:</strong> the button that kills most enemies.</li>
<li><strong>Boss skill or setup:</strong> extra damage or uptime against tougher enemies.</li>
<li><strong>Support gems:</strong> modifiers that change damage, behavior, cost, or reliability.</li>
<li><strong>Utility:</strong> movement, defense, exposure, curse-like effects, crowd control, or recovery.</li>
</ul>
<h2>How to test a support gem</h2>
<ol>
<li>Change only one support at a time.</li>
<li>Test against a similar pack or boss phase.</li>
<li>Watch clear speed, resource cost, safety, and boss uptime.</li>
<li>Keep notes if the result is patch-sensitive.</li>
</ol>
<h2>Common beginner trap</h2>
<p>The highest tooltip number is not always the best support. A support that makes a skill easier to land, cheaper to sustain, or safer to use can be better during campaign progression.</p>
"""
    },
    {
        "path": "guides/currency-guide.html",
        "title": "Path of Exile 2 Currency Guide for Beginners",
        "description": "A beginner-friendly Path of Exile 2 currency guide explaining how to think about crafting, upgrades, trading value, and waste prevention.",
        "heading": "PoE2 currency guide for beginners",
        "content": """
<p class=\"lede\">Currency in Path of Exile 2 is not just money. Many currency items are crafting actions. The beginner goal is to avoid wasting valuable items on gear you will replace quickly.</p>
<div class=\"notice\"><strong>Rule:</strong> During campaign, use common upgrade tools to fix weak slots. Save rare/high-value currency until you understand what item base and modifiers you are chasing.</div>
<h2>How to think about currency</h2>
<table><thead><tr><th>Use case</th><th>Beginner approach</th></tr></thead><tbody>
<tr><td>Fixing a bad weapon</td><td>Worth spending common resources if your damage is blocking progress.</td></tr>
<tr><td>Improving resistances</td><td>Often worth it; defenses keep your build playable.</td></tr>
<tr><td>Rolling random endgame items</td><td>Avoid until you know bases, affixes, and current market value.</td></tr>
<tr><td>Trading</td><td>Check multiple listings and avoid panic-buying after one hard boss.</td></tr>
</tbody></table>
<h2>Beginner spending priorities</h2>
<ol>
<li>Keep your main weapon or gem scaling current.</li>
<li>Patch holes in life/resistances.</li>
<li>Improve movement/recovery if deaths come from being trapped or too slow.</li>
<li>Only then chase luxury damage stats.</li>
</ol>
<h2>When to save currency</h2>
<p>If you cannot explain why an item base is good, why a modifier matters, and how long you will keep the item, save your expensive currency.</p>
"""
    },
    {
        "path": "tools/beginner-build-checklist.html",
        "title": "PoE2 Defense Diagnostic — Why Am I Dying?",
        "description": "Path of Exile 2 defense diagnostic: map death patterns to causes, first fixes, and responsible gear slots. Build-aware mode prefills from build cards.",
        "heading": "Defense diagnostic",
        "subtitle": "Death pattern → fix path",
        "tool_purpose": "Match how you died to a likely cause, first fix, and gear slot. Open from a build card for per-build targets.",
        "scripts": ["assets/js/defense-diagnostic.js"],
        "in_sitemap": True,
        "content": """
<p class="tool-quicklinks"><a class="button secondary button-sm" href="../builds/starter-elemental-caster.html">Elemental Caster</a> <a class="button secondary button-sm" href="../builds/starter-minion-witch.html">Minion Witch</a> <span class="muted">— prefill from a build</span></p>
<div id="build-banner" class="notice notice-compact" style="display:none"></div>
<div class="notice notice-warn notice-compact"><strong>Verify in game.</strong> Enter the requirement you see on your gem tooltip — numbers here are planning guidance.</div>
<p><label>Filter patterns: <input id="diag-search" type="search" placeholder="e.g. one-shot, mana, greyed out"></label></p>
<table class="gear responsive-stack"><thead><tr><th>Death pattern</th><th>Likely cause</th><th>First fix</th><th>Gear slot</th></tr></thead><tbody id="diag-results"></tbody></table>
<section class="build-section" id="build-defense-targets"></section>
<h2>Related tools</h2>
<p class="muted"><a href="gear-upgrade-checker.html">Gear upgrade planner</a> · <a href="attribute-checker.html">Attribute checker</a></p>
"""
    },
    {
        "path": "tools/gear-upgrade-checker.html",
        "title": "PoE2 Gear Upgrade Planner by Build & Stage",
        "description": "Interactive gear upgrade planner for Path of Exile 2: required, good, and luxury affixes per slot for campaign, early maps, and red maps. Prefills from build cards.",
        "heading": "Gear upgrade planner",
        "subtitle": "Slot affix tiers by stage",
        "tool_purpose": "What affixes matter on this slot at campaign vs maps? Open from a build card to prefill slot priorities.",
        "scripts": ["assets/js/gear-upgrade-checker.js"],
        "in_sitemap": True,
        "content": """
<p class="tool-quicklinks"><a class="button secondary button-sm" href="../builds/starter-elemental-caster.html?via=gear">Elemental Caster</a> <a class="button secondary button-sm" href="../builds/starter-minion-witch.html?via=gear">Minion Witch</a></p>
<div id="build-banner" class="notice notice-compact" style="display:none"></div>
<div class="notice notice-warn notice-compact"><strong>No price promises.</strong> Trade links open the official site; type filter recipes manually if deep links do not prefill.</div>
<div class="tool-controls">
<label>Stage: <select id="upgrade-stage"><option value="campaign">Campaign</option><option value="early_maps">Early maps</option><option value="red_maps">Red maps / pinnacle</option></select></label>
<label>Slot: <select id="upgrade-slot"></select></label>
</div>
<p id="upgrade-suggest" class="muted"></p>
<div id="upgrade-output" class="build-section"></div>
"""
    },
    {
        "path": "tools/attribute-checker.html",
        "title": "PoE2 Attribute, Spirit & Gear-Swap Checker",
        "description": "Free Path of Exile 2 calculator: check Strength/Dexterity/Intelligence deficits, Spirit reservation, and whether swapping a gear slot breaks a skill or Spirit reservation. Prefills from build cards. No backend.",
        "heading": "Attribute & gear-swap checker",
        "subtitle": "Planning aid · verify in game",
        "tool_purpose": "What attributes am I missing? What breaks if I swap this amulet? Prefills from build cards.",
        "in_sitemap": True,
        "scripts": ["assets/js/attribute-calculator.js"],
        "content": """
<p class="tool-quicklinks"><a class="button secondary button-sm" href="?build=starter-elemental-caster">Elemental Caster</a> <a class="button secondary button-sm" href="?build=starter-minion-witch">Minion Witch</a></p>
<div id="build-banner" class="notice notice-compact" style="display:none"></div>
<div class="notice notice-warn notice-compact"><strong>Verify in game.</strong> Enter requirements from your gem tooltips.</div>

<section class="build-section" id="attr-calc">
  <h2>1. What attributes am I missing?</h2>
  <p class=\"muted\">Enter the highest requirement you need to meet (from a gem or a gear base), your current attributes from the tree/quests, and what your gear adds.</p>
  <table class=\"calc-input\">
    <thead><tr><th>Attribute</th><th>Requirement</th><th>Current (tree/quests)</th><th>From gear</th></tr></thead>
    <tbody>
      <tr><th>Strength</th><td><input id=\"req-str\" type=\"number\" min=\"0\" value=\"0\"></td><td><input id=\"cur-str\" type=\"number\" min=\"0\" value=\"0\"></td><td><input id=\"gear-str\" type=\"number\" min=\"0\" value=\"0\"></td></tr>
      <tr><th>Dexterity</th><td><input id=\"req-dex\" type=\"number\" min=\"0\" value=\"0\"></td><td><input id=\"cur-dex\" type=\"number\" min=\"0\" value=\"0\"></td><td><input id=\"gear-dex\" type=\"number\" min=\"0\" value=\"0\"></td></tr>
      <tr><th>Intelligence</th><td><input id=\"req-int\" type=\"number\" min=\"0\" value=\"0\"></td><td><input id=\"cur-int\" type=\"number\" min=\"0\" value=\"0\"></td><td><input id=\"gear-int\" type=\"number\" min=\"0\" value=\"0\"></td></tr>
    </tbody>
  </table>
  <p id=\"attr-summary\" class=\"calc-summary\"></p>
  <table class=\"kv\"><thead><tr><th>Attribute</th><th>Required</th><th>Effective</th><th>Result</th></tr></thead><tbody id=\"attr-results\"></tbody></table>
</section>

<section class="build-section" id="spirit-calc">
  <h2>2. Do I have enough Spirit?</h2>
  <p class=\"muted\">Reservation builds (auras, minions, companions, persistent buffs) are gated by Spirit. Enter your Spirit capacity and total reservation.</p>
  <table class=\"calc-input\">
    <tbody>
      <tr><th>Spirit capacity</th><td><input id=\"spirit-capacity\" type=\"number\" min=\"0\" value=\"0\"></td></tr>
      <tr><th>Spirit reserved</th><td><input id=\"spirit-reserved\" type=\"number\" min=\"0\" value=\"0\"></td></tr>
    </tbody>
  </table>
  <p id=\"spirit-result\" class=\"calc-summary\"></p>
  <div id=\"spirit-sources\"></div>
</section>

<section class="build-section" id="swap-calc">
  <h2>3. Will this gear swap break something?</h2>
  <p class=\"muted\">Pick the slot you want to change. We show the build's authored swap warnings, then simulate the attributes/Spirit you would lose.</p>
  <p><label>Slot to swap: <select id=\"swap-slot\"></select></label></p>
  <table class=\"calc-input\">
    <thead><tr><th colspan=\"4\">Attributes / Spirit this slot currently gives you</th></tr>
    <tr><th>Strength</th><th>Dexterity</th><th>Intelligence</th><th>Spirit</th></tr></thead>
    <tbody><tr>
      <td><input id=\"swap-str\" type=\"number\" min=\"0\" value=\"0\"></td>
      <td><input id=\"swap-dex\" type=\"number\" min=\"0\" value=\"0\"></td>
      <td><input id=\"swap-int\" type=\"number\" min=\"0\" value=\"0\"></td>
      <td><input id=\"swap-spirit\" type=\"number\" min=\"0\" value=\"0\"></td>
    </tr></tbody>
  </table>
  <div id=\"swap-result\"></div>
</section>
"""
    },
    {
        "path": "guides/import-build-files.html",
        "title": "How to Import PoE2 .build Files (In-Game Build Planner)",
        "description": "Where to put Path of Exile 2 .build files on Windows and SteamOS, how to load them in the in-game Build Planner, and why in-game editing is not supported.",
        "heading": "How to import PoE2 .build files",
        "content": """
<p class=\"lede\">Path of Exile 2 has an official in-game <strong>Build Planner</strong>. It reads <code>.build</code> files and highlights the matching passives, skill gems, and gear slots inside the game — no alt-tabbing. It is plug-and-play: importing works, but creating or editing builds inside the game is not currently supported.</p>
<div class=\"notice\"><strong>Source:</strong> Official <a href=\"https://www.pathofexile.com/developer/docs/game\" rel=\"nofollow noopener\">Path of Exile developer docs — Build Planner</a>. The <code>.build</code> format is Version 1 (Experimental); paths below are the official defaults.</div>
<h2>1. Get a .build file</h2>
<p>Download a <code>.build</code> file from a guide that offers one. The file is plain JSON describing the ascendancy, passives, skill/support gems, and per-slot gear priorities.</p>
<h2>2. Put it in the Build Planner folder</h2>
<p>The game only reads <code>.build</code> files from a specific folder. Create it if it does not exist, then drop the file in.</p>
<table><thead><tr><th>Platform</th><th>Build Planner folder</th></tr></thead><tbody>
<tr><td>Windows</td><td><code>C:\\Users\\&lt;YourName&gt;\\Documents\\My Games\\Path of Exile 2\\BuildPlanner</code></td></tr>
<tr><td>SteamOS</td><td><code>/home/deck/.local/share/Steam/steamapps/compatdata/2315204395/pfx/drive_c/users/steamuser/Documents/My Games/Path of Exile 2/BuildPlanner</code></td></tr>
</tbody></table>
<h2>3. Load it in-game</h2>
<ol>
<li>Launch Path of Exile 2 and load your character.</li>
<li>Open the Passive Skill Tree (default <kbd>P</kbd>).</li>
<li>Click the Build Planner icon in the top-left of the tree screen.</li>
<li>Select your imported build from the list. Hints light up across your tree, skill bar, and gear slots.</li>
</ol>
<h2>In-game editing is not supported</h2>
<p>You can import and follow a build, but you cannot author or edit one inside Path of Exile 2. Make changes in the source file (or an external planner) and reload.</p>
<h2>How we source the ids inside our .build files</h2>
<div class=\"notice\"><strong>Data provenance:</strong> Our exporter targets the official <code>.build</code> schema. Ascendancy and passive node ids come from the <strong>official</strong> GGG passive-tree export. Skill and support gem ids come from <strong>community-extracted</strong> game data (the <a href=\"https://github.com/PathOfBuildingCommunity/PathOfBuilding-PoE2\" rel=\"nofollow noopener\">Path of Building Community PoE2</a> project), because GGG does not publish an official gem export. We use each gem's exact in-game metadata id, cross-validated against GGG's own <code>.build</code> example, and we never ship a placeholder or guessed id — a build with unresolved gems simply has no download. Game data is © Grinding Gear Games.</div>
<p>For background on the decision chain, see the <a href=\"../builds/index.html\">build cards</a>.</p>
"""
    },
    {
        "path": "guides/index.html",
        "title": "PoE2 Build Lab Guides Hub",
        "description": "Guides for Path of Exile 2 build decisions: attributes, gear priorities, build bait, defenses, .build files, and post-campaign progression.",
        "heading": "Guides",
        "in_sitemap": True,
        "content": "__GUIDES_INDEX__",
    },
    {
        "path": "guides/attribute-requirements.html",
        "title": "PoE2 Attribute Requirements Explained",
        "description": "Path of Exile 2 Strength, Dexterity, and Intelligence requirements: where they come from, how gear swaps break gems, and how to fix deficits.",
        "heading": "PoE2 attribute requirements explained",
        "in_sitemap": True,
        "content": """
<p class=\"lede\">Attributes gate gems and some gear bases. They come from your class start, passive tree, quests, and equipment — and a single swap can silently disable a skill.</p>
<h2>Where requirements come from</h2>
<ul>
<li><strong>Skill and support gems</strong> — each gem lists Str/Dex/Int requirements that scale with level.</li>
<li><strong>Weapon and armour bases</strong> — some bases need attributes to equip.</li>
<li><strong>Passive tree</strong> — primary source of \"free\" attributes during leveling.</li>
</ul>
<h2>Common failure mode</h2>
<p>You upgrade the amulet for damage and your main skill greys out because the old amulet supplied +Intelligence. This is attribute starvation — not a broken build.</p>
<h2>What to do</h2>
<p>Use the <a href=\"../tools/attribute-checker.html\">attribute &amp; gear-swap checker</a> with a <a href=\"../builds/index.html\">build card</a> prefill, or read gem requirements on the tooltip and patch the deficit on amulet, rings, or helmet.</p>
<div class=\"notice\"><strong>Data:</strong> Gem requirements on build cards use community-extracted ids (Path of Building Community PoE2). Verify in game before expensive crafts.</div>
"""
    },
    {
        "path": "guides/why-cant-equip-gem.html",
        "title": "Why Can't I Equip This Gem in PoE2?",
        "description": "Troubleshoot Path of Exile 2 gem equip failures: attribute deficits, weapon restrictions, duplicate skills, and Spirit reservation.",
        "heading": "Why can't I equip this gem?",
        "in_sitemap": True,
        "content": """
<p class=\"lede\">When a gem won't equip, the game is usually telling you one of four things.</p>
<table><thead><tr><th>Symptom</th><th>Cause</th><th>Fix</th></tr></thead><tbody>
<tr><td>Greyed out in inventory</td><td>Attribute requirement too high</td><td>Add Str/Dex/Int on gear or take tree nodes; use attribute checker</td></tr>
<tr><td>Cannot link to weapon</td><td>Wrong weapon type or skill tag mismatch</td><td>Match gem tags (spell vs attack, minion vs direct)</td></tr>
<tr><td>Skill works then stops after gear swap</td><td>Lost attributes from removed piece</td><td>Model swap in gear-swap checker before committing</td></tr>
<tr><td>Cannot add another minion/aura</td><td>Spirit reservation exceeded</td><td>Track Spirit on weapon/amulet/body; drop a reservation source</td></tr>
</tbody></table>
<p>See <a href=\"attribute-requirements.html\">attribute requirements</a> and the <a href=\"../tools/attribute-checker.html\">checker tool</a>.</p>
"""
    },
    {
        "path": "guides/beginner-gear-priorities.html",
        "title": "PoE2 Beginner Gear Stat Priorities by Slot",
        "description": "Beginner Path of Exile 2 gearing: required vs luxury affixes per slot for campaign and early maps, without fixed price promises.",
        "heading": "Beginner gear stat priorities",
        "in_sitemap": True,
        "content": """
<p class=\"lede\">During leveling, a plain rare with the <em>right</em> stats beats a flashy item with wrong modifiers. Priorities depend on slot and stage — not a single tier list.</p>
<h2>Universal rules</h2>
<ul>
<li><strong>Weapon</strong> — keeps damage scaling current (spell damage, minion damage, or weapon DPS).</li>
<li><strong>Boots</strong> — movement speed is a defense stat; do not skip it.</li>
<li><strong>Rings/amulet/belt</strong> — patch life and resistances before luxury damage.</li>
<li><strong>Chest/helmet/gloves</strong> — life or ES plus resistances; attributes if gems are gated.</li>
</ul>
<p>Per-build slot tables live on <a href=\"../builds/index.html\">build cards</a> and the <a href=\"../tools/gear-upgrade-checker.html\">gear upgrade planner</a>.</p>
"""
    },
    {
        "path": "guides/build-bait-checklist.html",
        "title": "PoE2 Build Bait Checklist — Trust Before You Invest",
        "description": "Checklist to spot Path of Exile 2 build bait: patch date, budget, complexity, source, and failure modes before copying a showcase build.",
        "heading": "Build bait checklist",
        "in_sitemap": True,
        "content": """
<p class=\"lede\">A build is \"bait\" when it looks strong in a video but fails without expensive items, ignores defenses, or is stale after a patch.</p>
<section class=\"checklist\">
<label><input type=\"checkbox\"> Patch version and <code>last_reviewed</code> date are visible and recent.</label>
<label><input type=\"checkbox\"> Budget/complexity/gear dependency match your situation.</label>
<label><input type=\"checkbox\"> Source is identified (creator, self-tested, or research-backed).</label>
<label><input type=\"checkbox\"> Failure modes and risks are stated — not only highlight moments.</label>
<label><input type=\"checkbox\"> Controller/HC/SSF/trade viability is labeled, not assumed.</label>
<label><input type=\"checkbox\"> Defensive targets exist — not \"just don't get hit\".</label>
<label><input type=\"checkbox\"> Attribute and Spirit requirements are explainable.</label>
</section>
<p>Our <a href=\"../builds/index.html\">build cards</a> expose this rubric on every published starter.</p>
"""
    },
    {
        "path": "guides/beginner-defensive-layers.html",
        "title": "PoE2 Beginner Defensive Layers Explained",
        "description": "Path of Exile 2 defensive layers for beginners: life/ES, resistances, recovery, movement, and map mods to avoid.",
        "heading": "Beginner defensive layers",
        "in_sitemap": True,
        "content": """
<p class=\"lede\">Survival is layered. Fixing one layer without checking the others is why \"I capped resists but still die\" happens.</p>
<h2>Layers to track</h2>
<ul>
<li><strong>Life or energy shield</strong> — raw hit pool.</li>
<li><strong>Elemental resistances</strong> — cap fire/cold/lightning for maps when possible.</li>
<li><strong>Recovery</strong> — flasks, regeneration, leech, or sustain skills.</li>
<li><strong>Movement</strong> — boots movement speed plus a reposition skill.</li>
<li><strong>Mechanics</strong> — dodge telegraphs, don't face-tank.</li>
</ul>
<p>Map mods that punish recovery or add player damage are listed per build on build cards. Use the <a href=\"../tools/beginner-build-checklist.html\">defense diagnostic</a> when you know <em>how</em> you die.</p>
"""
    },
    {
        "path": "guides/after-campaign.html",
        "title": "What to Do After the PoE2 Campaign",
        "description": "Path of Exile 2 post-campaign checklist: first maps, resistance caps, waystone sustain habits, and when to push harder content.",
        "heading": "What to do after campaign",
        "in_sitemap": True,
        "content": """
<p class=\"lede\">Finishing the campaign is not endgame — it is the point where defenses and economy matter more than raw leveling speed.</p>
<h2>First-hour checklist</h2>
<ul>
<li>Cap elemental resistances if possible before pushing harder maps.</li>
<li>Keep weapon/gem scaling current — campaign gear falls off quickly.</li>
<li>Pick map mods you can sustain; avoid player damage/recovery penalties until stable.</li>
<li>Stock waystones and learn sustain loops (see <a href=\"endgame-hub.html\">Endgame hub</a>).</li>
</ul>
<p>Match expectations to your <a href=\"../builds/index.html\">build card</a> content-fit tags (campaign vs early maps vs pinnacle).</p>
"""
    },
    {
        "path": "guides/endgame-hub.html",
        "title": "PoE2 Endgame Hub — Atlas, Waystones, Bosses",
        "description": "Static Path of Exile 2 endgame hub: Atlas first steps, waystone sustain overview, boss unlock paths, and known progression blockers for 0.5.2.",
        "heading": "Endgame hub",
        "in_sitemap": True,
        "content": """
<p class=\"lede\">Endgame in PoE2 Early Access is still moving with patches. This hub summarizes progression blockers and where to look official — not a full Maxroll-style atlas guide.</p>
<div class=\"notice\"><strong>Patch:</strong> 0.5.2 Early Access · Last hub review 2026-06-17. Verify mechanics after hotfixes.</div>
<h2>Atlas first steps</h2>
<ul>
<li>Unlock the Atlas through campaign progression and follow in-game prompts for your league.</li>
<li>Start on white/yellow maps until resistances and recovery are stable.</li>
<li>Read map modifiers before activating — player damage and less recovery are common pain points.</li>
</ul>
<h2>Waystone sustain</h2>
<p>Sustain is a loop: run maps that reward waystones, use vendors and content that refill supply, and avoid burning high-tier stones before your build is ready. Exact rates change with patches — track your own runs rather than trusting stale numbers.</p>
<h2>Boss unlock overview</h2>
<p>Pinnacle and boss content unlock through Atlas progression and specific encounters. Treat boss guides as patch-dated; check <a href=\"https://www.pathofexile.com/forum/view-forum/2212\" rel=\"nofollow noopener\">official patch notes</a> when a gate changes.</p>
<h2>Known progression blockers</h2>
<ul>
<li><strong>Defense not maps-ready</strong> — fix via build card defense targets and <a href=\"../tools/beginner-build-checklist.html\">diagnostic</a>.</li>
<li><strong>Attribute/Spirit breakage after upgrade</strong> — use <a href=\"../tools/attribute-checker.html\">attribute checker</a> before expensive trades.</li>
<li><strong>Economy volatility</strong> — use trade filter recipes on build cards, not fixed prices.</li>
</ul>
<p>Per-build endgame viability is labeled on each <a href=\"../builds/index.html\">build card</a> (campaign / early maps / pinnacle).</p>
"""
    },
    {
        "path": "about.html",
        "title": "About PoE2 Build Lab",
        "description": "About PoE2 Build Lab, an independent Path of Exile 2 beginner guide site.",
        "heading": "About PoE2 Build Lab",
        "content": """
<p>PoE2 Build Lab is an independent beginner-focused Path of Exile 2 guide site. The goal is to publish practical, patch-labeled guides that help new and returning players make better early decisions.</p>
<p>This site is not affiliated with Grinding Gear Games. Path of Exile 2 names and related marks belong to their respective owners.</p>
<h2>Editorial policy</h2>
<ul>
<li>Pages should show an updated date and patch context when advice may change.</li>
<li>We avoid copying forum, wiki, or Reddit text.</li>
<li>Build claims should be updated when official patch notes change the underlying mechanic.</li>
<li>Future hands-on screenshots and testing notes will be added as the site grows.</li>
</ul>
"""
    },
    {
        "path": "contact.html",
        "title": "Contact PoE2 Build Lab",
        "description": "Contact information for PoE2 Build Lab corrections, guide updates, and feedback.",
        "heading": "Contact",
        "content": """
<p>For corrections, outdated patch notes, or guide suggestions, open an issue on the site repository or contact the maintainer through the linked GitHub profile.</p>
<p><a href=\"https://github.com/BrickerP/poe2-build-lab\">GitHub repository</a></p>
"""
    },
    {
        "path": "privacy-policy.html",
        "title": "Privacy Policy for PoE2 Build Lab",
        "description": "Privacy policy for PoE2 Build Lab, including analytics and advertising readiness notes.",
        "heading": "Privacy Policy",
        "content": """
<p><strong>Effective date:</strong> 2026-06-16</p>
<p>PoE2 Build Lab is a static informational website. At launch, the site does not collect account registrations, comments, payments, or direct personal information.</p>
<h2>Analytics</h2>
<p>The site may use Google Search Console to understand how pages appear in Google Search. Search Console reports aggregated search performance and does not create user accounts on this site.</p>
<h2>Advertising</h2>
<p>The site includes Google AdSense code using publisher ID <code>pub-1111218417177666</code>. Google and its advertising partners may use cookies or similar technologies to serve and measure ads when Google enables ad serving for this site.</p>
<h2>External links</h2>
<p>The site links to external resources such as official game pages, patch notes, and GitHub. External sites have their own privacy policies.</p>
<h2>Contact</h2>
<p>For privacy questions or corrections, contact the maintainer through the GitHub repository.</p>
"""
    },
]

def depth_prefix(path):
    parts = Path(path).parts
    return "../" * (len(parts)-1)

def nav_html(prefix, current):
    items = []
    home_url = prefix + "index.html"
    home_cls = ' active' if current == "index.html" else ""
    items.append(
        f'<a class="nav-link{home_cls}" href="{home_url}">'
        f'<span class="nav-label">Home</span>'
        f'<span class="nav-desc">Start here</span></a>'
    )
    for label, href, desc in NAV:
        url = prefix + href
        cls = " active" if href == current else ""
        items.append(
            f'<a class="nav-link{cls}" href="{url}">'
            f'<span class="nav-label">{escape(label)}</span>'
            f'<span class="nav-desc">{escape(desc)}</span></a>'
        )
    return "".join(items)


def decision_grid_html(prefix=""):
    cards = []
    for icon, label, desc, href in DECISION_GRID:
        cards.append(
            f'<a class="decision-card" href="{prefix}{href}">'
            f'<span class="decision-icon">{icon}</span>'
            f'<span class="decision-label">{escape(label)}</span>'
            f'<span class="decision-desc">{escape(desc)}</span></a>'
        )
    return f'<div class="decision-grid">{"".join(cards)}</div>'


def guides_index_content():
    return f"""
<p class="lede">Deep-dive reference — each links back to build cards and tools.</p>
{decision_grid_html("../")}
<section class="section-block" style="margin-top:2rem">
  <h2>All guides</h2>
  <div class="decision-grid">
    <a class="decision-card" href="import-build-files.html"><span class="decision-icon">↓</span><span class="decision-label">Import .build</span><span class="decision-desc">Windows/SteamOS paths</span></a>
    <a class="decision-card" href="attribute-requirements.html"><span class="decision-icon">◆</span><span class="decision-label">Attributes</span><span class="decision-desc">Str/Dex/Int & gear swaps</span></a>
    <a class="decision-card" href="why-cant-equip-gem.html"><span class="decision-icon">?</span><span class="decision-label">Can't equip gem</span><span class="decision-desc">Requirements & fixes</span></a>
    <a class="decision-card" href="beginner-gear-priorities.html"><span class="decision-icon">▣</span><span class="decision-label">Gear priorities</span><span class="decision-desc">Stat targets by slot</span></a>
    <a class="decision-card" href="build-bait-checklist.html"><span class="decision-icon">⚠</span><span class="decision-label">Build bait</span><span class="decision-desc">Trust before you invest</span></a>
    <a class="decision-card" href="beginner-defensive-layers.html"><span class="decision-icon">🛡</span><span class="decision-label">Defenses</span><span class="decision-desc">Life, resists, recovery</span></a>
    <a class="decision-card" href="after-campaign.html"><span class="decision-icon">→</span><span class="decision-label">After campaign</span><span class="decision-desc">First maps checklist</span></a>
    <a class="decision-card" href="endgame-hub.html"><span class="decision-icon">◎</span><span class="decision-label">Endgame hub</span><span class="decision-desc">Atlas & blockers</span></a>
  </div>
</section>
"""


def homepage_content(published_builds):
    featured = "".join(
        render_build_card(b, compact=True, card_prefix="builds/", asset_prefix="")
        for b in published_builds[:2]
    )
    return f"""
<section class="section-block">
  <div class="section-head">
    <h2>Starter builds</h2>
    <a class="link-more" href="builds/index.html">All builds →</a>
  </div>
  <div class="grid featured-builds">{featured}</div>
</section>
<section class="section-block">
  <h2>What do you need?</h2>
  <p class="muted" style="margin:-0.25rem 0 1rem">Every link answers a real in-game question.</p>
  {decision_grid_html()}
</section>
<section class="content-block">
  <p class="muted" style="margin:0"><strong>Patch {escape(SITE["patch"])}</strong> · Updated {SITE["updated"]}. Build cards show review state and <code>known_broken_by_patch</code> — verify in game before expensive investments.</p>
</section>
"""

def render_page(page, build=None):
    path = page['path']
    prefix = depth_prefix(path)
    canonical = SITE['url'] + ('' if path == 'index.html' else path)
    heading = page.get('heading', SITE['name'])
    hero = page.get('hero', False)
    is_tool = path.startswith('tools/')
    is_build = path.startswith('builds/') and path != 'builds/index.html' and build
    nav = nav_html(prefix, path)
    body_class = ' class="tool-page"' if is_tool else ''
    main_class = ' class="tool-page"' if is_tool else ''
    if hero:
        main_intro = f'''
<section class="hero hero-compact">
  <div class="hero-top">
    <span class="patch-pill">{escape(SITE["patch"])}</span>
    <span class="patch-pill muted-pill">Updated {SITE["updated"]}</span>
  </div>
  <h1>Pick your starter. Know what breaks.</h1>
  <p class="hero-sub">Patch-reviewed build cards and tools for the decisions that actually matter in Path of Exile 2.</p>
</section>
'''
    elif is_tool:
        purpose = page.get("tool_purpose", page.get("description", ""))
        main_intro = (
            f'<section class="page-title tool-title">'
            f'<p class="eyebrow">{escape(page.get("subtitle", "Planning aid · verify in game"))}</p>'
            f'<h1>{escape(heading)}</h1>'
            f'<p class="tool-purpose">{escape(purpose)}</p></section>'
        )
    else:
        subtitle = page.get('subtitle', f'Updated {SITE["updated"]} · {SITE["patch"]}')
        main_intro = f'<section class="page-title"><p class="eyebrow">{escape(subtitle)}</p><h1>{escape(heading)}</h1></section>'
    sticky_html = render_build_sticky(build, prefix) if is_build else ""
    content = page['content']
    robots_meta = '\n  <meta name="robots" content="noindex, follow">' if page.get('noindex') else ''
    scripts_html = ''.join(f'<script src="{prefix}{escape(s)}" defer></script>' for s in page.get('scripts', []))
    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(page['title'])}</title>
  <meta name="description" content="{escape(page['description'])}">{robots_meta}
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{escape(page['title'])}">
  <meta property="og:description" content="{escape(page['description'])}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <link rel="stylesheet" href="{prefix}styles.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":{page['title']!r},"description":{page['description']!r},"url":{canonical!r},"dateModified":"{SITE['updated']}"}}</script>
</head>
<body{body_class}>
  <header class="site-header"><a class="brand" href="{prefix}index.html">PoE2 <span>Build Lab</span></a><nav>{nav}</nav></header>
  <main{main_class}>{main_intro}{sticky_html}<article class="article">{content}</article></main>
  <footer><p>Independent Path of Exile 2 beginner guide site. Not affiliated with Grinding Gear Games.</p><p><a href="{prefix}privacy-policy.html">Privacy</a> · <a href="{prefix}contact.html">Contact</a> · <a href="{prefix}about.html">About</a> · <a href="{prefix}sitemap.xml">Sitemap</a></p></footer>
  {scripts_html}
</body>
</html>'''
    return html

# --------------------------------------------------------------------------- #
# Build Cards (Phase 1) — rendered from data/builds/*.json
# --------------------------------------------------------------------------- #
BUILDS_DIR = Path("data/builds")


def load_builds():
    """Load and sort build JSON files. schema.json is metadata, not a build."""
    builds = []
    if not BUILDS_DIR.exists():
        return builds
    for path in sorted(BUILDS_DIR.glob("*.json")):
        if path.name == "schema.json":
            continue
        builds.append(json.loads(path.read_text(encoding="utf-8")))
    return builds


def tag(label, value, kind="info"):
    return f'<span class="tag tag-{kind}">{escape(label)}: <b>{escape(str(value))}</b></span>'


def review_badge(build):
    label, kind = REVIEW_STATE_LABELS.get(build.get("review_state", "draft"), ("Unknown", "warn"))
    return f'<span class="badge badge-{kind}">{escape(label)}</span>'


def import_status(build):
    bf = build.get("build_file", {})
    if bf.get("enabled") and bf.get("path"):
        return ("available", "Import file ready")
    return ("unavailable", "Import file not yet available")


def li_list(items):
    return "".join(f"<li>{escape(str(i))}</li>" for i in items) if items else "<li>None recorded yet.</li>"


def render_stale_warning(build):
    state = build.get("review_state", "draft")
    if state == "current":
        return ""
    label, _ = REVIEW_STATE_LABELS.get(state, ("Unknown", "warn"))
    return (
        f'<div class="notice notice-warn notice-compact">'
        f'<strong>{escape(label)}</strong> · patch {escape(build.get("patch_version", "?"))}'
        f' · reviewed {escape(build.get("last_reviewed", "?"))}'
        f'</div>'
    )


def render_build_sticky(build, prefix):
    """Sticky summary bar for build detail pages."""
    imp_kind, _ = import_status(build)
    review_label, review_kind = REVIEW_STATE_LABELS.get(
        build.get("review_state", "draft"), ("Unknown", "warn")
    )
    actions = []
    if imp_kind == "available":
        bf = build["build_file"]
        actions.append(
            f'<a class="button button-sm" href="{prefix}{escape(bf["path"])}">Download .build</a>'
        )
    actions.append(
        f'<a class="button secondary button-sm" href="{prefix}tools/attribute-checker.html?build={build["id"]}">Check stats</a>'
    )
    actions.append(
        f'<a class="button secondary button-sm" href="{prefix}tools/gear-upgrade-checker.html?build={build["id"]}">Gear upgrades</a>'
    )
    return f'''
<div class="build-sticky">
  <div class="build-sticky-inner">
    <div class="build-sticky-meta">
      <span class="build-sticky-name">{escape(build["name"])}</span>
      <span class="tag">{escape(class_line(build))}</span>
      <span class="badge badge-{review_kind}">{escape(review_label)}</span>
      <span class="tag">Budget: <b>{escape(build.get("budget", "?"))}</b></span>
    </div>
    <div class="build-sticky-actions">{"".join(actions)}</div>
  </div>
</div>'''


def render_provenance_block(build):
    return (
        '<section class="build-section"><h2>Data provenance</h2>'
        '<p class="muted">Ascendancy and passive node ids come from the official GGG passive-tree export. '
        'Skill and support gem ids come from community-extracted data (Path of Building Community PoE2); '
        'GGG does not publish an official gem export. Gear affix tables are authored guidance. '
        'Trade handoff is filter-recipe text — not live price data.</p></section>'
    )


def render_build_tags(build):
    imp_kind, imp_text = import_status(build)
    tags = [
        tag("Patch", build.get("patch_version", "?")),
        tag("Budget", build.get("budget", "?")),
        tag("Complexity", build.get("complexity", "?")),
        tag("Gear dependency", build.get("gear_dependency", "?")),
        f'<span class="tag tag-{"ok" if imp_kind=="available" else "warn"}">{escape(imp_text)}</span>',
    ]
    return '<div class="tag-row">' + "".join(tags) + "</div>"


def render_trust_section(build):
    """Combined patch/trust/viability — lower priority, compact."""
    src = build.get("source", {})
    trust = build.get("trust", {})
    fit = build.get("content_fit", {})
    links = "".join(
        f'<a href="{escape(l["url"])}" rel="nofollow noopener">{escape(l["label"])}</a>'
        for l in build.get("source_links", []) if l.get("url")
    )
    links_html = f'<p class="src-links muted">Sources: {links}</p>' if links else ""
    asc = build.get("ascendancy", "")
    asc_display = asc if asc and asc != "TBD" else "Pending verified data"
    broken = build.get("known_broken_by_patch", [])
    broken_html = ""
    if broken:
        broken_html = f'<div class="notice notice-bad notice-compact"><strong>Known broken:</strong> {"; ".join(escape(b) for b in broken)}</div>'
    rows = [
        ("Patch", build.get("patch_version", "?")),
        ("Class", f'{build.get("class","?")} / {asc_display}'),
        ("Last reviewed", build.get("last_reviewed", "?")),
        ("Review state", REVIEW_STATE_LABELS.get(build.get("review_state", "draft"), ("Unknown", ""))[0]),
        ("Trust score", f'{trust.get("score", "?")} / 5'),
        ("Source", f'{escape(src.get("type", "?"))} — {escape(src.get("notes", ""))}'),
        ("Controller", VIABILITY_LABELS.get(trust.get("controller_friendly", "unknown"))),
        ("Hardcore", VIABILITY_LABELS.get(trust.get("hardcore_viable", "unknown"))),
        ("SSF", VIABILITY_LABELS.get(trust.get("ssf_viable", "unknown"))),
        ("Trade", VIABILITY_LABELS.get(trust.get("trade_viable", "unknown"))),
        ("Campaign fit", fit.get("campaign", "unknown").replace("_", " ")),
        ("Early maps", fit.get("early_maps", "unknown").replace("_", " ")),
        ("Pinnacle", fit.get("pinnacle", "unknown").replace("_", " ")),
    ]
    table = "".join(
        f"<tr><th>{escape(k)}</th><td>{v if k == 'Source' else escape(str(v))}</td></tr>"
        for k, v in rows
    )
    return (
        f'<section class="build-section trust-section"><h2>Patch &amp; trust details</h2>'
        f'{broken_html}'
        f'<table class="kv">{table}</table>{links_html}</section>'
    )


def render_skills_block(build):
    items = []
    for skill in build.get("skills", []):
        supports = skill.get("supports", [])
        sup_html = ""
        if supports:
            sup_items = "".join(
                f"<li><b>{escape(s['name'])}</b>{(' — ' + escape(s['note'])) if s.get('note') else ''}</li>"
                for s in supports
            )
            sup_html = f"<ul class='supports'>{sup_items}</ul>"
        note = f"<p class='muted'>{escape(skill['note'])}</p>" if skill.get("note") else ""
        items.append(
            f"<div class='skill'><h3>{escape(skill['name'])} "
            f"<span class='role'>{escape(skill['role'])}</span></h3>{note}{sup_html}</div>"
        )
    return f'<section class="build-section"><h2>What skills do I use?</h2>{"".join(items)}</section>'


def render_passive_block(build):
    milestones = build.get("passive_milestones", [])
    if not milestones:
        body = '<p class="muted">Passive milestones placeholder — exact node ids pending verified passive-tree mapping.</p>'
    else:
        rows = []
        has_nodes = False
        for m in milestones:
            nodes = m.get("node_ids", [])
            if nodes:
                has_nodes = True
            node_note = f'<br><span class="muted">Nodes: {escape(", ".join(nodes))}</span>' if nodes else ""
            rows.append(
                f"<tr><th>{escape(m['stage'])}</th><td>{escape(m['goal'])}{node_note}</td></tr>"
            )
        body = f'<table class="kv">{"".join(rows)}</table>'
        if has_nodes and build.get("build_file", {}).get("enabled"):
            body += '<p class="muted">Node ids above are included in the downloadable .build file (official tree export).</p>'
        elif not has_nodes:
            body += '<p class="muted">Goals are directional until node ids are mapped.</p>'
    return f'<section class="build-section"><h2>Where do I path on the tree?</h2>{body}</section>'


def render_attributes_block(build):
    attrs = build.get("attributes", {})
    req = attrs.get("required", {})
    planned = attrs.get("planned", {})
    notes = li_list(attrs.get("notes", []))
    checker = f'../tools/attribute-checker.html?build={build["id"]}'
    return (
        '<section class="build-section"><h2>Can I equip my gems?</h2>'
        f'<p>Deficit policy: <b>{escape(attrs.get("deficit_policy", "warn"))}</b>. '
        f'Required (gems): Str {req.get("str", 0)} / Dex {req.get("dex", 0)} / Int {req.get("int", 0)} · '
        f'Planned loadout: Str {planned.get("str", 0)} / Dex {planned.get("dex", 0)} / Int {planned.get("int", 0)}.</p>'
        f'<ul>{notes}</ul>'
        f'<p><a class="button secondary" href="{checker}">Open attribute checker</a></p></section>'
    )


def render_spirit_block(build):
    spirit = build.get("spirit_budget")
    if not spirit:
        return ""
    sources = spirit.get("sources", [])
    src_html = (
        "".join(f"<li>{escape(s['name'])}: {escape(str(s['amount']))}</li>" for s in sources)
        if sources else "<li>Sources not yet itemized.</li>"
    )
    return (
        '<section class="build-section"><h2>Do I have enough Spirit?</h2>'
        f'<p>Required: <b>{spirit.get("required", 0)}</b> · Planned: <b>{spirit.get("planned", 0)}</b></p>'
        f'<p class="muted">Reservation sources:</p><ul>{src_html}</ul>'
        f'<ul>{li_list(spirit.get("notes", []))}</ul></section>'
    )


def render_gear_block(build):
    bid = build["id"]
    upgrade = f'../tools/gear-upgrade-checker.html?build={bid}'
    sections = []
    for slot, data in build.get("gear_slots", {}).items():
        slot_label = escape(slot.replace("_", " "))
        affix_rows = []
        for label, key in (
            ("Required", "required_affixes"),
            ("Good", "good_affixes"),
            ("Luxury", "luxury_affixes"),
        ):
            vals = data.get(key, [])
            if vals:
                affix_rows.append(
                    f"<tr><th>{label}</th><td>{escape('; '.join(vals))}</td></tr>"
                )
        stage_rows = []
        for label, key in (
            ("Campaign", "campaign_target"),
            ("Early maps", "early_maps_target"),
            ("Red maps", "red_maps_target"),
        ):
            if data.get(key):
                stage_rows.append(
                    f"<tr><th>{label}</th><td>{escape(data[key])}</td></tr>"
                )
        affix_table = ""
        if affix_rows:
            affix_table = (
                "<table class='gear'><thead><tr><th>Tier</th><th>Affixes</th></tr></thead>"
                f"<tbody>{''.join(affix_rows)}</tbody></table>"
            )
        stage_table = ""
        if stage_rows:
            stage_table = (
                "<table class='kv'><tbody>" + "".join(stage_rows) + "</tbody></table>"
            )
        compromise = (
            f"<p class='muted'><strong>Budget compromise:</strong> {escape(data.get('budget_compromise', ''))}</p>"
            if data.get("budget_compromise") else ""
        )
        sections.append(
            f"<div class='skill'><h3>{slot_label}</h3>"
            f"<p><strong>Base:</strong> {escape(data.get('base', ''))}</p>"
            f"{affix_table}{stage_table}{compromise}</div>"
        )
    return (
        '<section class="build-section"><h2>What gear goes in each slot?</h2>'
        f'<p><a class="button secondary" href="{upgrade}">Open gear upgrade planner</a></p>'
        f'{"".join(sections)}</section>'
    )


def render_gear_swap_block(build):
    warnings = build.get("gear_swap_warnings", [])
    if not warnings:
        return ""
    items = "".join(
        f"<div class='notice notice-warn'><strong>{escape(w['slot'].replace('_',' '))}:</strong> "
        f"{escape(w['message'])}"
        f"{(' <span class=muted>Breaks: ' + escape(', '.join(w['breaks'])) + '</span>') if w.get('breaks') else ''}"
        "</div>"
        for w in warnings
    )
    return f'<section class="build-section"><h2>What breaks if I swap gear?</h2>{items}</section>'


def render_defense_block(build):
    d = build.get("defenses", {})
    diag = f'../tools/beginner-build-checklist.html?build={build["id"]}'
    parts = [
        f'<p><a class="button secondary" href="{diag}">Open defense diagnostic for this build</a></p>',
        f'<h3>Campaign targets</h3><ul>{li_list(d.get("campaign_targets", []))}</ul>',
    ]
    if d.get("early_maps_targets"):
        parts.append(f'<h3>Early maps targets</h3><ul>{li_list(d.get("early_maps_targets"))}</ul>')
    extra = []
    for label, key in (("Recovery", "recovery"), ("Movement", "movement_baseline"), ("Chaos resistance", "chaos_resistance_note")):
        if d.get(key):
            extra.append(f"<li><b>{label}:</b> {escape(d[key])}</li>")
    if extra:
        parts.append(f'<ul>{"".join(extra)}</ul>')
    if d.get("map_mods_to_avoid"):
        parts.append(f'<h3>Map mods to avoid</h3><ul>{li_list(d.get("map_mods_to_avoid"))}</ul>')
    if d.get("death_diagnostic"):
        rows = "".join(
            f"<tr><td>{escape(x['pattern'])}</td><td>{escape(x['cause'])}</td>"
            f"<td>{escape(x['first_fix'])}</td><td>{escape(x['gear_slot'].replace('_', ' '))}</td></tr>"
            for x in d["death_diagnostic"]
        )
        parts.append(
            '<h3>Death pattern → fix</h3>'
            '<table class="gear"><thead><tr><th>Pattern</th><th>Cause</th><th>First fix</th><th>Slot</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>'
        )
    return f'<section class="build-section"><h2>How do I not die?</h2>{"".join(parts)}</section>'


def render_risks_block(build):
    trust = build.get("trust", {})
    return (
        '<section class="build-section"><h2>What can go wrong?</h2>'
        f'<h3>Failure modes</h3><ul>{li_list(trust.get("failure_modes", []))}</ul>'
        f'<h3>Risk flags</h3><ul>{li_list(trust.get("risks", []))}</ul></section>'
    )


def render_trade_block(build):
    handoff = build.get("trade_handoff", {})
    if not handoff.get("enabled") or not handoff.get("filters"):
        return ""
    blocks = []
    for f in handoff["filters"]:
        recipe = f.get("filter_recipe") or (
            "Required: " + ", ".join(f.get("required_stats", []))
        )
        price = ""
        if f.get("approx_price"):
            price = f" <span class='muted'>(~{escape(f['approx_price'])}, checked {escape(f.get('checked_at',''))})</span>"
        link = ""
        if f.get("trade_url"):
            link = (
                f'<p><a href="{escape(f["trade_url"])}" rel="nofollow noopener">Open official trade</a> '
                '<span class="muted">— if the link does not prefill filters, use the recipe text below.</span></p>'
            )
        blocks.append(
            f"<div class='skill'><h3>{escape(f['slot'].replace('_',' '))} "
            f"<span class='role'>{escape(f.get('budget_tier',''))} budget</span></h3>"
            f"{link}<p>{escape(recipe)}</p>"
            f"<p class='muted'>Required: {escape(', '.join(f.get('required_stats', [])))} · "
            f"Optional: {escape(', '.join(f.get('optional_stats', [])))} · "
            f"Ignore: {escape(', '.join(f.get('ignore_at_low_budget', [])))}{price}</p></div>"
        )
    return (
        '<section class="build-section"><h2>How do I find gear on trade?</h2>'
        '<p class="muted">Filter recipes only — we do not quote live prices. '
        'Official trade may require manual filter entry.</p>'
        f'{"".join(blocks)}</section>'
    )


def render_import_block(build):
    kind, text = import_status(build)
    if kind == "available":
        return (
            '<section class="build-section"><h2>Load this in-game</h2>'
            '<p class="muted">Use the <strong>Download .build</strong> button above. '
            'New to import files? See '
            '<a href="../guides/import-build-files.html">how to import PoE2 .build files</a>.</p>'
            '</section>'
        )
    return (
        '<section class="build-section"><h2>Load this in-game</h2>'
        '<div class="notice notice-compact"><strong>.build file pending.</strong> '
        'Gem ids still being verified — gear and passive hints are ready on the card.</div>'
        '<p class="muted"><a href="../guides/import-build-files.html">How to import .build files</a></p>'
        '</section>'
    )


def build_page_content(build):
    draft_notice = ""
    if build.get("status") == "draft":
        draft_notice = (
            '<div class="notice notice-warn notice-compact"><strong>Draft card</strong> — '
            'not indexed; gem and passive ids still being verified.</div>'
        )
    summary = f'<p class="lede">{escape(build.get("summary", ""))}</p>' if build.get("summary") else ""
    who = ""
    if build.get("who_should_play"):
        who = f'<section class="build-section"><h2>Is this build for me?</h2><ul>{li_list(build["who_should_play"])}</ul></section>'
    return "".join([
        render_stale_warning(build),
        draft_notice,
        summary,
        who,
        render_skills_block(build),
        render_passive_block(build),
        render_attributes_block(build),
        render_spirit_block(build),
        render_gear_block(build),
        render_gear_swap_block(build),
        render_defense_block(build),
        render_trade_block(build),
        render_risks_block(build),
        render_import_block(build),
        render_trust_section(build),
        render_provenance_block(build),
    ])


def build_detail_page(build):
    name = build["name"]
    patch = build.get("patch_version", SITE["patch"])
    return {
        "path": f"builds/{build['id']}.html",
        "title": f"{name} PoE2 Build Card for {patch}",
        "description": (
            f"{name}: PoE2 build card with patch trust, budget, complexity, gear slot priorities, "
            f"attributes, Spirit, defenses, and .build import status."
        ),
        "heading": name,
        "subtitle": f"{patch} · {REVIEW_STATE_LABELS.get(build.get('review_state','draft'),('Draft','warn'))[0]} · Last reviewed {build.get('last_reviewed','?')}",
        "noindex": build.get("status") != "published",
        "in_sitemap": build.get("status") == "published",
        "content": build_page_content(build),
    }


def class_line(build):
    """'Sorceress · Stormweaver' once an ascendancy is resolved, else just the class."""
    cls = build.get("class", "")
    asc = build.get("ascendancy", "")
    if asc and asc != "TBD":
        return f"{cls} · {asc}"
    return cls


def render_build_card(build, compact=False, card_prefix="", asset_prefix="../"):
    imp_kind, imp_text = import_status(build)
    trust = build.get("trust", {})
    href = f"{card_prefix}{build['id']}.html"
    rubric = ""
    if not compact:
        rubric = (
            f'<p class="muted import-line">'
            f'Controller {VIABILITY_LABELS.get(trust.get("controller_friendly","unknown"))} · '
            f'HC {VIABILITY_LABELS.get(trust.get("hardcore_viable","unknown"))} · '
            f'SSF {VIABILITY_LABELS.get(trust.get("ssf_viable","unknown"))} · '
            f'Trade {VIABILITY_LABELS.get(trust.get("trade_viable","unknown"))}'
            f'</p>'
        )
    download_btn = ""
    if imp_kind == "available":
        download_btn = f'<a class="button secondary button-sm" href="{asset_prefix}{escape(build["build_file"]["path"])}">.build</a>'
    actions = (
        f'<div class="build-card-actions">'
        f'<a class="button" href="{href}">View build</a>'
        f'{download_btn}'
        f'</div>'
    )
    return f"""
<article class="card build-card">
  <div class="card-head">{review_badge(build)} <span class="cls">{escape(class_line(build))}</span></div>
  <h2><a href="{href}">{escape(build['name'])}</a></h2>
  <p>{escape(build.get('summary',''))}</p>
  <div class="tag-row">
    {tag("Budget", build.get("budget","?"))}
    {tag("Complexity", build.get("complexity","?"))}
    {tag("Gear", build.get("gear_dependency","?"))}
  </div>
  {rubric}
  <p class="muted import-line">{escape(imp_text)} · {escape(build.get('patch_version','?'))}</p>
  {actions}
</article>"""


def build_index_content(builds):
    cards = "".join(render_build_card(b) for b in builds)
    return f"""
<p class="lede">Each card connects the decisions a starter actually faces: patch trust, budget, gear slots, attributes, defenses, and .build import — not a prose tier list.</p>
<section class="grid featured-builds">{cards}</section>
<section class="content-block">
  <p class="muted" style="margin:0">Updated {SITE['updated']} · {SITE['patch']}. Draft cards are research-backed, not in-game-verified meta promises.</p>
  <p style="margin:0.75rem 0 0"><a href="best-beginner-builds.html">Archetype overview</a> — higher-level comparison if you have not picked a class yet.</p>
</section>
"""


builds_data = load_builds()
published_builds = [b for b in builds_data if b.get("status") == "published"]
build_index_page = {
    "path": "builds/index.html",
    "title": "PoE2 Build Cards: Patch-Reviewed Starter Builds",
    "description": "Path of Exile 2 build cards comparing starter builds by patch trust, budget, complexity, gear slot priorities, attributes, defenses, and .build import status.",
    "heading": "Starter builds",
    "in_sitemap": True,
    "content": build_index_content(published_builds),
}
build_pages = [build_index_page] + [build_detail_page(b) for b in builds_data]

all_pages = pages + build_pages

build_by_path = {f"builds/{b['id']}.html": b for b in builds_data}

for p in all_pages:
    page = dict(p)
    if page.get("content") == "__HOMEPAGE__":
        page["content"] = homepage_content(published_builds)
    elif page.get("content") == "__GUIDES_INDEX__":
        page["content"] = guides_index_content()
    build = build_by_path.get(page["path"])
    out = Path(page["path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_page(page, build=build), encoding="utf-8")

# styles.css is maintained as a standalone file (not regenerated here).

# Search and crawling helpers.
# Public pages go in the sitemap; draft/noindex build pages are excluded so
# unverified content is never presented to search engines as authoritative.
urls = []
for p in all_pages:
    if p.get('noindex') or p.get('in_sitemap') is False:
        continue
    loc = SITE['url'] + ('' if p['path']=='index.html' else p['path'])
    urls.append(f"  <url><loc>{loc}</loc><lastmod>{SITE['updated']}</lastmod></url>")
Path('sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n', encoding='utf-8')
Path('robots.txt').write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}sitemap.xml\n", encoding='utf-8')
Path('ads.txt').write_text("google.com, pub-1111218417177666, DIRECT, f08c47fec0942fa0\n", encoding='utf-8')
Path("404.html").write_text(
    render_page({
        "path": "404.html",
        "title": "Page not found - PoE2 Build Lab",
        "description": "Page not found.",
        "heading": "Page not found",
        "content": '<p class="lede">This page does not exist.</p><p><a class="button" href="index.html">Back to home</a></p>',
    }),
    encoding="utf-8",
)
Path('README.md').write_text(f"""# PoE2 Build Lab\n\nStatic beginner-guide site for Path of Exile 2.\n\nLive URL target: {SITE['url']}\n\n## Launch checklist\n\n- [x] Static pages\n- [x] SEO titles/descriptions\n- [x] `robots.txt` and `sitemap.xml`\n- [x] About / Contact / Privacy Policy\n- [x] Google Search Console URL-prefix property and verification\n- [x] AdSense publisher ID configured in site code\n\n## AdSense status\n\nAdSense publisher ID `pub-1111218417177666` is configured in the site code and `ads.txt`; actual ad serving still depends on Google site review and Auto ads status.\n""", encoding='utf-8')
