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

PAGES_DIR = Path("data/pages")


def load_static_pages():
    """Load generated-page source data from JSON so content edits do not touch Python."""
    pages = []
    if not PAGES_DIR.exists():
        raise FileNotFoundError(f"Missing page data directory: {PAGES_DIR}")
    for path in sorted(PAGES_DIR.glob("*.json")):
        page = json.loads(path.read_text(encoding="utf-8"))
        page.setdefault("order", 999)
        for key in ("path", "title", "description", "content"):
            if key not in page:
                raise ValueError(f"{path} missing required field: {key}")
        pages.append(page)
    seen = set()
    for page in pages:
        if page["path"] in seen:
            raise ValueError(f"Duplicate generated page path: {page['path']}")
        seen.add(page["path"])
    return sorted(pages, key=lambda page: (page.get("order", 999), page["path"]))


pages = load_static_pages()

def depth_prefix(path):
    parts = Path(path).parts
    return "../" * (len(parts)-1)

def nav_html(prefix, current):
    items = []
    home_url = prefix + "index.html"
    home_cls = ' active' if current == "index.html" else ""
    items.append(
        f'<a class="nav-link home-link{home_cls}" href="{home_url}">'
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
<section class="section-block section-spaced">
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
  <p class="muted section-kicker">Every link answers a real in-game question.</p>
  {decision_grid_html()}
</section>
<section class="content-block">
  <p class="muted flush"><strong>Patch {escape(SITE["patch"])}</strong> · Updated {SITE["updated"]}. Build cards show review state and <code>known_broken_by_patch</code> — verify in game before expensive investments.</p>
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
  <div class="hero-grid">
    <div class="hero-copy">
      <div class="hero-top">
        <span class="patch-pill">{escape(SITE["patch"])}</span>
        <span class="patch-pill muted-pill">Updated {SITE["updated"]}</span>
      </div>
      <h1>Pick your starter. Know what breaks.</h1>
      <p class="hero-sub">Choose a build, import it, then check stats, gear, and death patterns before you waste currency.</p>
      <div class="hero-actions">
        <a class="button" href="builds/index.html">Compare builds</a>
        <a class="button secondary" href="tools/attribute-checker.html">Check my stats</a>
      </div>
    </div>
    <div class="start-panel" aria-label="Recommended first steps">
      <p class="eyebrow">Start here</p>
      <ol class="start-steps">
        <li><span>1</span><strong>Choose a starter</strong><em>Low budget, honest risks, current patch.</em></li>
        <li><span>2</span><strong>Import the .build</strong><em>Load skills and slot hints in-game.</em></li>
        <li><span>3</span><strong>Check before trading</strong><em>Attributes, Spirit, gear swaps, defenses.</em></li>
      </ol>
    </div>
  </div>
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
        download_btn = f'<a class="button secondary button-sm" href="{asset_prefix}{escape(build["build_file"]["path"])}">Import to game</a>'
    primary_label = "Start this build" if compact else "Open build plan"
    actions = (
        f'<div class="build-card-actions">'
        f'<a class="button" href="{href}">{primary_label}</a>'
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
  <p class="muted flush">Updated {SITE['updated']} · {SITE['patch']}. Draft cards are research-backed, not in-game-verified meta promises.</p>
  <p class="content-followup"><a href="best-beginner-builds.html">Archetype overview</a> — higher-level comparison if you have not picked a class yet.</p>
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
Path('README.md').write_text(f"""# PoE2 Build Lab\n\nStatic beginner-guide site for Path of Exile 2.\n\nLive URL target: {SITE['url']}\n\n## Maintenance model\n\n- Edit build data in `data/builds/*.json`.\n- Edit generated page content in `data/pages/*.json`.\n- Edit visual system in `styles.css`.\n- Run `python3 sitegen.py` after content or data changes.\n\n## Launch checklist\n\n- [x] Static pages\n- [x] SEO titles/descriptions\n- [x] `robots.txt` and `sitemap.xml`\n- [x] About / Contact / Privacy Policy\n- [x] Google Search Console URL-prefix property and verification\n- [x] AdSense publisher ID configured in site code\n\n## AdSense status\n\nAdSense publisher ID `pub-1111218417177666` is configured in the site code and `ads.txt`; actual ad serving still depends on Google site review and Auto ads status.\n""", encoding='utf-8')
