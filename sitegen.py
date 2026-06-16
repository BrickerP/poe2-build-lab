import json
from pathlib import Path
from html import escape
from datetime import date

ADSENSE_CLIENT = "ca-pub-1111218417177666"

SITE = {
    "name": "PoE2 Build Lab",
    "tagline": "Clear Path of Exile 2 starter guides, build checklists, and patch-aware beginner notes.",
    "url": "https://brickerp.github.io/poe2-build-lab/",
    "updated": "2026-06-16",
    "patch": "0.5.2 Early Access"
}

NAV = [
    ("Home", "index.html"),
    ("Build Cards", "builds/index.html"),
    ("Attribute Checker", "tools/attribute-checker.html"),
    ("Beginner Guide", "guides/beginner-guide.html"),
    ("Currency", "guides/currency-guide.html"),
    ("Checklist", "tools/beginner-build-checklist.html"),
    ("About", "about.html"),
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
        "content": """
<section class=\"grid cards\">
  <article class=\"card highlight\"><p class=\"eyebrow\">Start here</p><h2>Build cards</h2><p>Compare starter builds by patch trust, budget, complexity, gear priorities, and what can go wrong — before spending your first passive points.</p><a class=\"button\" href=\"builds/index.html\">Browse build cards</a></article>
  <article class=\"card\"><p class=\"eyebrow\">New player guide</p><h2>What to do first</h2><p>A quick path through skills, support gems, defenses, and early upgrades.</p><a href=\"guides/beginner-guide.html\">Open guide</a></article>
  <article class=\"card\"><p class=\"eyebrow\">Systems</p><h2>Currency basics</h2><p>Understand common crafting and upgrade currencies before you waste valuable items.</p><a href=\"guides/currency-guide.html\">Learn currency</a></article>
</section>
<section class=\"content-block\">
  <h2>Current editorial stance</h2>
  <p>PoE2 Build Lab is starting as a focused beginner resource for Path of Exile 2 Early Access. Guides are written to be version-labeled and easy to update after patches. We avoid claiming a build is the absolute best unless it has been checked against current patch notes and in-game evidence.</p>
  <div class=\"notice\"><strong>Patch context:</strong> The site currently tracks <b>0.5.2 Early Access</b>. Treat all build advice as a starting point and verify before investing expensive currency.</div>
</section>
<section class=\"grid cards\">
  <article class=\"card\"><h3>Classes explained</h3><p>Choose a class based on playstyle, range, defense, and early learning curve.</p><a href=\"guides/classes-explained.html\">Compare classes</a></article>
  <article class=\"card\"><h3>Skill gems explained</h3><p>Skill gems, support gems, and why links matter more than raw tooltip damage.</p><a href=\"guides/skill-gems-explained.html\">Read systems guide</a></article>
  <article class=\"card\"><h3>Beginner checklist</h3><p>A practical act-by-act checklist for defenses, flasks, gems, and upgrades.</p><a href=\"tools/beginner-build-checklist.html\">Use checklist</a></article>
</section>
"""
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
        "title": "Path of Exile 2 Beginner Build Checklist",
        "description": "A practical PoE2 beginner build checklist for damage, defenses, gems, gear, resources, and patch-safe guide following.",
        "heading": "PoE2 beginner build checklist",
        "content": """
<p class=\"lede\">Use this checklist before deciding your build is broken. Most early problems are caused by one missing layer, not by the entire character being doomed.</p>
<section class=\"checklist\">
<label><input type=\"checkbox\"> I have one main damage skill, not five half-supported skills.</label>
<label><input type=\"checkbox\"> My supports improve real gameplay, not just tooltip damage.</label>
<label><input type=\"checkbox\"> My weapon or gem level has been updated recently.</label>
<label><input type=\"checkbox\"> My gear has life or relevant survivability.</label>
<label><input type=\"checkbox\"> My elemental resistances are not obviously neglected.</label>
<label><input type=\"checkbox\"> I know whether deaths come from one-shots, crowd pressure, resource issues, or low damage.</label>
<label><input type=\"checkbox\"> The guide I follow has a recent patch date.</label>
<label><input type=\"checkbox\"> I have not spent rare currency on a temporary item without a reason.</label>
</section>
<h2>How to use it</h2>
<p>If two or more boxes are unchecked, fix those before rerolling. If all boxes are checked and the build still fails, the issue may be a bad archetype for the current patch, a missing key mechanic, or content that expects stronger gear.</p>
"""
    },
    {
        "path": "tools/attribute-checker.html",
        "title": "PoE2 Attribute, Spirit & Gear-Swap Checker",
        "description": "Free Path of Exile 2 calculator: check Strength/Dexterity/Intelligence deficits, Spirit reservation, and whether swapping a gear slot breaks a skill or Spirit reservation. Prefills from build cards. No backend.",
        "heading": "Attribute, Spirit & gear-swap checker",
        "subtitle": "Planning aid · verify in game",
        "scripts": ["assets/js/attribute-calculator.js"],
        "content": """
<p class=\"lede\">Answer two questions competitors leave separate: <em>what attributes am I missing?</em> and <em>what breaks if I swap this gear?</em> Open this tool from a build card to prefill its Spirit and gear-swap data, or enter values manually.</p>
<div id=\"build-banner\" class=\"notice\" style=\"display:none\"></div>
<div class=\"notice notice-warn\"><strong>Planning aid — verify in game.</strong> Exact gem and base attribute requirements need a verified data source; until then, enter the requirement you want to meet. Numbers here are guidance, not a guarantee.</div>

<section class=\"build-section\" id=\"attr-calc\">
  <h2>1. Attribute deficits</h2>
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

<section class=\"build-section\" id=\"spirit-calc\">
  <h2>2. Spirit reservation</h2>
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

<section class=\"build-section\" id=\"swap-calc\">
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

<section class=\"build-section\">
  <h2>How this helps</h2>
  <p>Beginners often swap an amulet or weapon for more damage and suddenly a skill greys out or a minion vanishes. That is usually a lost attribute requirement or a lost Spirit source. This checker connects your planned requirements, your Spirit budget, and the build's gear-swap warnings so you can see the breakage before it happens — then confirm it in game.</p>
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
<h2>Why PoE2 Build Lab does not ship .build files yet</h2>
<div class=\"notice notice-warn\"><strong>Honest status:</strong> Our exporter targets the official <code>.build</code> schema and maps each build's ascendancy (verified against the official passive-tree export), gear-slot priorities, and skills. But the official data exports do <strong>not</strong> include skill-gem or support-gem ids — those only exist in extracted game files. Rather than ship a <code>.build</code> with placeholder gem ids that would fail to import, we keep export disabled until verified gem ids are available. Build cards say plainly when an import file is not yet available.</div>
<p>For background on the decision chain, see the <a href=\"../builds/index.html\">build cards</a>.</p>
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
    items=[]
    for label, href in NAV:
        url = prefix + href
        cls = ' class="active"' if href == current else ''
        items.append(f'<a{cls} href="{url}">{escape(label)}</a>')
    return ''.join(items)

def render_page(page):
    path = page['path']
    prefix = depth_prefix(path)
    canonical = SITE['url'] + ('' if path == 'index.html' else path)
    heading = page.get('heading', SITE['name'])
    hero = page.get('hero', False)
    nav = nav_html(prefix, path)
    if hero:
        main_intro = f'''
<section class="hero">
  <p class="eyebrow">Patch-aware beginner guides · Updated {SITE['updated']}</p>
  <h1>{SITE['name']}</h1>
  <p>{SITE['tagline']}</p>
  <div class="hero-actions"><a class="button" href="builds/index.html">Browse build cards</a><a class="button secondary" href="tools/beginner-build-checklist.html">Open checklist</a></div>
</section>
'''
    else:
        subtitle = page.get('subtitle', f'Updated {SITE["updated"]} · {SITE["patch"]}')
        main_intro = f'<section class="page-title"><p class="eyebrow">{subtitle}</p><h1>{escape(heading)}</h1></section>'
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
<body>
  <header class="site-header"><a class="brand" href="{prefix}index.html">PoE2 Build Lab</a><nav>{nav}</nav></header>
  <main>{main_intro}<article class="article">{page['content']}</article></main>
  <footer><p>Independent Path of Exile 2 beginner guide site. Not affiliated with Grinding Gear Games.</p><p><a href="{prefix}privacy-policy.html">Privacy Policy</a> · <a href="{prefix}contact.html">Contact</a> · <a href="{prefix}sitemap.xml">Sitemap</a></p></footer>
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


def render_patch_trust_block(build):
    src = build.get("source", {})
    trust = build.get("trust", {})
    links = "".join(
        f'<a href="{escape(l["url"])}" rel="nofollow noopener">{escape(l["label"])}</a>'
        for l in build.get("source_links", []) if l.get("url")
    )
    links_html = f'<p class="src-links">Sources: {links}</p>' if links else ""
    asc = build.get("ascendancy", "")
    asc_display = asc if asc and asc != "TBD" else "Pending verified data"
    rows = [
        ("Patch version", build.get("patch_version", "?")),
        ("Class / ascendancy", f'{build.get("class","?")} / {asc_display}'),
        ("Last reviewed", build.get("last_reviewed", "?")),
        ("Review state", REVIEW_STATE_LABELS.get(build.get("review_state", "draft"), ("Unknown", ""))[0]),
        ("Trust score", f'{trust.get("score", "?")} / 5'),
        ("Source", f'{escape(src.get("type", "?"))} — {escape(src.get("notes", ""))}'),
        ("Verification proof", ", ".join(trust.get("proof", [])) or "none"),
    ]
    table = "".join(f"<tr><th>{escape(k)}</th><td>{v if k=='Source' else escape(str(v))}</td></tr>" for k, v in rows)
    return f"""
<section class="build-section">
  <h2>Patch &amp; trust</h2>
  <table class="kv">{table}</table>
  {links_html}
</section>"""


def render_known_broken_block(build):
    broken = build.get("known_broken_by_patch", [])
    if broken:
        body = f'<div class="notice notice-bad"><strong>Known broken by patch:</strong><ul>{li_list(broken)}</ul></div>'
    else:
        body = '<p class="muted">No patches are currently recorded as breaking this build. This field is always tracked so a patch cannot silently invalidate the page.</p>'
    return f'<section class="build-section"><h2>Known broken by patch</h2>{body}</section>'


def render_viability_block(build):
    trust = build.get("trust", {})
    fit = build.get("content_fit", {})
    rows = [
        ("Controller-friendly", VIABILITY_LABELS.get(trust.get("controller_friendly", "unknown"))),
        ("Hardcore viable", VIABILITY_LABELS.get(trust.get("hardcore_viable", "unknown"))),
        ("SSF viable", VIABILITY_LABELS.get(trust.get("ssf_viable", "unknown"))),
        ("Trade viable", VIABILITY_LABELS.get(trust.get("trade_viable", "unknown"))),
        ("Campaign", fit.get("campaign", "unknown").replace("_", " ")),
        ("Early maps", fit.get("early_maps", "unknown").replace("_", " ")),
        ("Pinnacle", fit.get("pinnacle", "unknown").replace("_", " ")),
    ]
    table = "".join(f"<tr><th>{escape(k)}</th><td>{escape(str(v))}</td></tr>" for k, v in rows)
    return f'<section class="build-section"><h2>Viability &amp; content fit</h2><table class="kv">{table}</table></section>'


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
    return f'<section class="build-section"><h2>Skills &amp; supports</h2>{"".join(items)}</section>'


def render_passive_block(build):
    milestones = build.get("passive_milestones", [])
    if not milestones:
        body = '<p class="muted">Passive milestones placeholder — exact node ids pending verified passive-tree mapping.</p>'
    else:
        rows = "".join(
            f"<tr><th>{escape(m['stage'])}</th><td>{escape(m['goal'])}</td></tr>"
            for m in milestones
        )
        body = (
            f'<table class="kv">{rows}</table>'
            '<p class="muted">Exact passive node ids are not yet mapped for this draft; goals are directional.</p>'
        )
    return f'<section class="build-section"><h2>Passive milestones</h2>{body}</section>'


def render_attributes_block(build):
    attrs = build.get("attributes", {})
    notes = li_list(attrs.get("notes", []))
    checker = f'../tools/attribute-checker.html?build={build["id"]}'
    return (
        '<section class="build-section"><h2>Attributes</h2>'
        f'<p>Deficit policy: <b>{escape(attrs.get("deficit_policy", "warn"))}</b>. '
        'Exact Str/Dex/Int numbers depend on verified gem and base data; enter the requirement you want to meet in the checker.</p>'
        f'<ul>{notes}</ul>'
        f'<p><a class="button" href="{checker}">Open in attribute &amp; gear-swap checker</a></p></section>'
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
        '<section class="build-section"><h2>Spirit budget</h2>'
        f'<p>Required: <b>{spirit.get("required", 0)}</b> · Planned: <b>{spirit.get("planned", 0)}</b></p>'
        f'<p class="muted">Reservation sources:</p><ul>{src_html}</ul>'
        f'<ul>{li_list(spirit.get("notes", []))}</ul></section>'
    )


def render_gear_block(build):
    rows = []
    for slot, data in build.get("gear_slots", {}).items():
        prio = ", ".join(data.get("priority", []))
        note = data.get("budget_note", "")
        rows.append(
            f"<tr><th>{escape(slot.replace('_', ' '))}</th>"
            f"<td>{escape(data.get('base', ''))}</td>"
            f"<td>{escape(prio)}</td>"
            f"<td class='muted'>{escape(note)}</td></tr>"
        )
    table = (
        "<table class='gear'><thead><tr><th>Slot</th><th>Base</th>"
        "<th>Stat priority (highest first)</th><th>Budget note</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
    return f'<section class="build-section"><h2>Gear slot priorities</h2>{table}</section>'


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
    return f'<section class="build-section"><h2>Gear-swap warnings</h2>{items}</section>'


def render_defense_block(build):
    d = build.get("defenses", {})
    parts = [f'<h3>Campaign targets</h3><ul>{li_list(d.get("campaign_targets", []))}</ul>']
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
    return f'<section class="build-section"><h2>Defensive checklist</h2>{"".join(parts)}</section>'


def render_risks_block(build):
    trust = build.get("trust", {})
    return (
        '<section class="build-section"><h2>Known risks &amp; failure modes</h2>'
        f'<h3>Failure modes</h3><ul>{li_list(trust.get("failure_modes", []))}</ul>'
        f'<h3>Risk flags</h3><ul>{li_list(trust.get("risks", []))}</ul></section>'
    )


def render_trade_block(build):
    handoff = build.get("trade_handoff", {})
    if not handoff.get("enabled") or not handoff.get("filters"):
        return ""
    rows = []
    for f in handoff["filters"]:
        price = ""
        if f.get("approx_price"):
            price = f" <span class='muted'>(~{escape(f['approx_price'])}, checked {escape(f.get('checked_at',''))})</span>"
        rows.append(
            f"<tr><th>{escape(f['slot'].replace('_',' '))}</th>"
            f"<td>{escape(f.get('budget_tier',''))}</td>"
            f"<td>{escape(', '.join(f.get('required_stats', [])))}</td>"
            f"<td class='muted'>{escape(', '.join(f.get('optional_stats', [])))}</td>"
            f"<td class='muted'>{escape(', '.join(f.get('ignore_at_low_budget', [])))}{price}</td></tr>"
        )
    table = (
        "<table class='gear'><thead><tr><th>Slot</th><th>Budget</th><th>Required stats</th>"
        "<th>Nice to have</th><th>Ignore at low budget</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
    return (
        '<section class="build-section"><h2>How to search trade</h2>'
        '<p class="muted">Search these stats on the official trade site. We do not quote live prices; '
        'use this as a filter recipe, not a price promise.</p>'
        f'{table}</section>'
    )


def render_import_block(build):
    kind, text = import_status(build)
    if kind == "available":
        bf = build["build_file"]
        return (
            '<section class="build-section"><h2>In-game import (.build)</h2>'
            f'<p><a class="button" href="../{escape(bf["path"])}">Download .build file</a></p>'
            '<p class="muted">New to import files? See '
            '<a href="../guides/import-build-files.html">how to import PoE2 .build files</a>.</p>'
            '</section>'
        )
    return (
        '<section class="build-section"><h2>In-game import (.build)</h2>'
        '<div class="notice"><strong>Import file not yet available.</strong> '
        'This is a published guide, not yet an in-game import file. A <code>.build</code> export will be '
        'added once verified skill-gem ids exist (GGG publishes no official gem export, and we never '
        'ship placeholder ids). The ascendancy and gear-slot hints are already resolved; only the gem ids are pending.</div>'
        '<p class="muted">Want to understand the format and folder paths? See '
        '<a href="../guides/import-build-files.html">how to import PoE2 .build files</a>.</p>'
        '</section>'
    )


def build_page_content(build):
    draft_notice = ""
    if build.get("status") == "draft":
        draft_notice = (
            '<div class="notice notice-warn"><strong>Draft card.</strong> '
            'This archetype is research-backed but not yet in-game verified, so it is not indexed for search. '
            'Exact gem, base, and passive ids are still being confirmed against verified data before this card is published.</div>'
        )
    summary = f'<p class="lede">{escape(build.get("summary", ""))}</p>' if build.get("summary") else ""
    who = ""
    if build.get("who_should_play"):
        who = f'<section class="build-section"><h2>Who should play this</h2><ul>{li_list(build["who_should_play"])}</ul></section>'
    return "".join([
        render_build_tags(build),
        draft_notice,
        summary,
        who,
        render_patch_trust_block(build),
        render_known_broken_block(build),
        render_viability_block(build),
        render_skills_block(build),
        render_passive_block(build),
        render_attributes_block(build),
        render_spirit_block(build),
        render_gear_block(build),
        render_gear_swap_block(build),
        render_defense_block(build),
        render_risks_block(build),
        render_trade_block(build),
        render_import_block(build),
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


def render_build_card(build):
    imp_kind, imp_text = import_status(build)
    href = f"{build['id']}.html"
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
  <p class="muted import-line">{escape(imp_text)} · Patch {escape(build.get('patch_version','?'))}</p>
  <a class="button" href="{href}">Open build card</a>
</article>"""


def build_index_content(builds):
    cards = "".join(render_build_card(b) for b in builds)
    return f"""
<p class="lede">Each build card connects the decisions a starter actually has to make: is it patch-reviewed, how expensive is it, how complex is it, which gear slots matter first, and what can go wrong. Compare archetypes here before reading a long guide.</p>
<div class="notice"><strong>Updated:</strong> {SITE['updated']} · <strong>Patch:</strong> {SITE['patch']}. Draft cards are research-backed starting points, not in-game-verified meta promises.</div>
<section class="grid cards build-grid">{cards}</section>
<section class="content-block">
  <h2>Looking for the archetype overview?</h2>
  <p>The original <a href="best-beginner-builds.html">beginner build archetypes</a> page is still available as a higher-level comparison.</p>
</section>
"""


builds_data = load_builds()
build_index_page = {
    "path": "builds/index.html",
    "title": "PoE2 Build Cards: Patch-Reviewed Starter Builds",
    "description": "Path of Exile 2 build cards comparing starter builds by patch trust, budget, complexity, gear slot priorities, attributes, defenses, and .build import status.",
    "heading": "PoE2 build cards",
    "in_sitemap": True,
    "content": build_index_content(builds_data),
}
build_pages = [build_index_page] + [build_detail_page(b) for b in builds_data]

all_pages = pages + build_pages

for p in all_pages:
    out = Path(p['path'])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_page(p), encoding='utf-8')

Path('styles.css').write_text(r'''
:root{--bg:#0d1117;--panel:#161b22;--panel2:#1f2937;--text:#e6edf3;--muted:#9da7b3;--accent:#f59e0b;--accent2:#60a5fa;--line:#30363d;--good:#34d399}*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at top left,#1d2a3a 0,#0d1117 36rem);color:var(--text);line-height:1.65}.site-header{position:sticky;top:0;z-index:10;display:flex;justify-content:space-between;align-items:center;padding:1rem clamp(1rem,4vw,4rem);background:rgba(13,17,23,.88);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}.brand{font-weight:800;color:var(--text);text-decoration:none;letter-spacing:.02em}nav{display:flex;gap:.85rem;flex-wrap:wrap}nav a,footer a,.article a{color:#93c5fd;text-decoration:none}nav a{font-size:.93rem;color:var(--muted)}nav a.active,nav a:hover{color:var(--text)}main{max-width:1120px;margin:auto;padding:2.5rem clamp(1rem,4vw,3rem)}.hero{padding:4rem 0 3rem;max-width:860px}.hero h1,.page-title h1{font-size:clamp(2.4rem,7vw,5.4rem);line-height:1;margin:.25rem 0 1rem;letter-spacing:-.06em}.hero p{font-size:1.22rem;color:var(--muted);max-width:760px}.eyebrow{color:var(--accent);text-transform:uppercase;font-size:.78rem;font-weight:800;letter-spacing:.12em}.hero-actions{display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem}.button{display:inline-block;background:linear-gradient(135deg,#f59e0b,#f97316);color:#111827!important;padding:.78rem 1rem;border-radius:999px;font-weight:800;text-decoration:none}.button.secondary{background:#243244;color:var(--text)!important;border:1px solid var(--line)}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}.card,.content-block,.article{background:rgba(22,27,34,.78);border:1px solid var(--line);border-radius:20px;padding:1.25rem;box-shadow:0 20px 60px rgba(0,0,0,.18)}.card.highlight{background:linear-gradient(160deg,rgba(245,158,11,.18),rgba(22,27,34,.9));border-color:rgba(245,158,11,.45)}.card h2,.card h3{line-height:1.15;margin:.3rem 0}.content-block{margin:1rem 0}.page-title{padding:2rem 0 1rem}.article{max-width:880px;margin:auto}.article .lede{font-size:1.2rem;color:#c9d1d9}.notice{border-left:4px solid var(--accent);background:rgba(245,158,11,.08);padding:1rem;border-radius:12px;margin:1rem 0}table{width:100%;border-collapse:collapse;margin:1.25rem 0;background:rgba(15,23,42,.4);border-radius:14px;overflow:hidden}th,td{border-bottom:1px solid var(--line);padding:.8rem;text-align:left;vertical-align:top}th{color:#facc15;background:rgba(255,255,255,.04)}tr:last-child td{border-bottom:0}h2{margin-top:2rem;line-height:1.2}ul,ol{padding-left:1.35rem}.checklist{display:grid;gap:.75rem}.checklist label{display:flex;gap:.65rem;align-items:flex-start;background:rgba(255,255,255,.04);padding:.85rem;border-radius:12px;border:1px solid var(--line)}input[type=checkbox]{margin-top:.35rem}footer{max-width:1120px;margin:2rem auto;padding:2rem clamp(1rem,4vw,3rem);color:var(--muted);border-top:1px solid var(--line)}.tag-row{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0}.tag{display:inline-block;font-size:.8rem;background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:999px;padding:.25rem .7rem;color:var(--muted)}.tag b{color:var(--text);font-weight:700}.tag-ok{border-color:rgba(52,211,153,.5)}.tag-warn{border-color:rgba(245,158,11,.5)}.badge{display:inline-block;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;padding:.2rem .55rem;border-radius:6px}.badge-ok{background:rgba(52,211,153,.18);color:#6ee7b7}.badge-warn{background:rgba(245,158,11,.18);color:#fcd34d}.badge-bad{background:rgba(248,113,113,.18);color:#fca5a5}.muted{color:var(--muted)}.build-section{margin-top:2rem;padding-top:1.25rem;border-top:1px solid var(--line)}.build-section h2{margin-top:0}.build-section h3{margin:1rem 0 .3rem;font-size:1rem;color:#facc15}table.kv th{width:34%;color:var(--muted);background:transparent}table.kv td{color:var(--text)}table.gear th{color:#facc15}.skill{background:rgba(255,255,255,.03);border:1px solid var(--line);border-radius:12px;padding:.8rem 1rem;margin:.6rem 0}.skill h3{margin:.1rem 0;color:var(--text)}.skill .role{font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;color:var(--accent);border:1px solid var(--line);border-radius:6px;padding:.1rem .4rem;margin-left:.4rem}.supports{margin:.4rem 0 0}.notice-warn{border-left-color:var(--accent)}.notice-bad{border-left-color:#f87171;background:rgba(248,113,113,.08)}.src-links a{margin-right:.8rem}.build-card .card-head{display:flex;align-items:center;gap:.6rem;margin-bottom:.3rem}.build-card .cls{color:var(--muted);font-size:.85rem}.build-card h2{margin:.2rem 0}.build-card h2 a{color:var(--text)}.build-card .import-line{font-size:.82rem;margin:.4rem 0 .8rem}.build-grid .button{margin-top:.4rem}.calc-input input{width:100%;max-width:8rem;background:rgba(15,23,42,.6);border:1px solid var(--line);border-radius:8px;color:var(--text);padding:.45rem .55rem;font:inherit}.calc-input th{color:var(--muted)}.calc-summary{font-weight:700;padding:.6rem .8rem;border-radius:10px;margin:1rem 0}.res-ok{color:#6ee7b7}.res-bad{color:#fca5a5}td.res-ok{color:#6ee7b7}td.res-bad{color:#fca5a5}.calc-summary.res-ok{background:rgba(52,211,153,.12)}.calc-summary.res-bad{background:rgba(248,113,113,.12)}#swap-slot{background:rgba(15,23,42,.6);border:1px solid var(--line);border-radius:8px;color:var(--text);padding:.45rem .6rem;font:inherit}
@media(max-width:820px){.site-header{align-items:flex-start;gap:1rem;flex-direction:column}.grid{grid-template-columns:1fr}.hero{padding-top:2rem}th,td{display:block;width:100%}th{display:none}td{border-bottom:0;padding:.55rem .8rem}tr{display:block;border-bottom:1px solid var(--line);padding:.45rem 0}table.kv th{display:none}}
'''.strip()+"\n", encoding='utf-8')

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
Path('404.html').write_text(render_page({"path":"404.html","title":"Page not found - PoE2 Build Lab","description":"Page not found.","heading":"Page not found","content":"<p>The page you requested does not exist yet. Start from the <a href=\"index.html\">homepage</a>.</p>"}), encoding='utf-8')
Path('README.md').write_text(f"""# PoE2 Build Lab\n\nStatic beginner-guide site for Path of Exile 2.\n\nLive URL target: {SITE['url']}\n\n## Launch checklist\n\n- [x] Static pages\n- [x] SEO titles/descriptions\n- [x] `robots.txt` and `sitemap.xml`\n- [x] About / Contact / Privacy Policy\n- [x] Google Search Console URL-prefix property and verification\n- [x] AdSense publisher ID configured in site code\n\n## AdSense status\n\nAdSense publisher ID `pub-1111218417177666` is configured in the site code and `ads.txt`; actual ad serving still depends on Google site review and Auto ads status.\n""", encoding='utf-8')
