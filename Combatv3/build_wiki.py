#!/usr/bin/env python3
"""build_wiki.py — multi-page linked HTML wiki from RULES.md + renown_data.

Structure:
  - index.html                : rules intro
  - rules-<section>.html       : one page per ## section of RULES.md
  - pursuits.html              : landing/index of all pursuit categories
  - type-<type>.html           : one page per pursuit TYPE (stat table)   [canonical home]
  - domain-<domain>.html       : filtered index — pursuits gated to a domain
  - standing-<tier>.html       : filtered index — pursuits gated to a standing
  - paths.html                 : build-path chains (text trees from builds_into)
  - glossary.html, factions.html
  - search across everything

Usage: python build_wiki.py [RULES.md] [out_dir]
"""
import sys, os, re, html, json
sys.path.insert(0, ".")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import renown_data as rd
import wiki_markers as wm
_VERSION = str(getattr(rd, "VERSION", ""))

# ── world lore source: the hand-maintained world.txt book ─────────────────────
# The Lore section renders whatever is currently in world.txt (parsed by
# worldtxt.py), so editing world.txt updates the wiki. Set WORLD_TXT to point
# anywhere; otherwise these locations are searched (relative to the cwd, this
# script, and the RULES file), including a worldbuilding/ subfolder.
try:
    import worldtxt as _wt
except Exception as _e:
    _wt = None
    print(f"  [lore] worldtxt.py not importable ({_e}) -> Lore section skipped")
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_RULES_DIR = os.path.dirname(os.path.abspath(sys.argv[1])) if len(sys.argv) > 1 else os.getcwd()
def _find_world_txt():
    env = os.environ.get("WORLD_TXT")
    if env:
        return env, [env]
    names = ["world.txt", os.path.join("worldbuilding", "world.txt")]
    bases = [os.getcwd(), _SCRIPT_DIR, _RULES_DIR,
             os.path.dirname(_SCRIPT_DIR), os.path.dirname(_RULES_DIR)]
    tried = []
    for base in bases:
        for nm in names:
            p = os.path.normpath(os.path.join(base, nm))
            if p not in tried:
                tried.append(p)
            if os.path.exists(p):
                return p, tried
    return None, tried

WORLD_TXT, _WT_TRIED = _find_world_txt() if _wt else (None, [])
WORLD_SECTIONS = []   # [(title, body_lines), ...] in file order
WORLD_CULTURES = []   # demonyms extracted from THE FIFTEEN
WORLD_PLACES = []     # [{name, owner, desc, kind}, ...] gazetteer entries
if _wt and WORLD_TXT and os.path.exists(WORLD_TXT):
    try:
        _wtext = open(WORLD_TXT, encoding="utf-8").read()
        WORLD_SECTIONS = _wt.parse_sections(_wtext)
        WORLD_CULTURES = _wt.extract_cultures(WORLD_SECTIONS)
        WORLD_PLACES = _wt.extract_places(WORLD_SECTIONS)
        print(f"  [lore] world.txt -> {WORLD_TXT}  "
              f"({len(WORLD_SECTIONS)} sections, {len(WORLD_CULTURES)} cultures)")
    except Exception as _e:
        print(f"  [lore] world.txt present but failed to parse: {_e}")
elif _wt:
    print("  [lore] world.txt NOT FOUND -> Lore section skipped. "
          "Set WORLD_TXT=<path> or place world.txt in one of:")
    for _p in _WT_TRIED:
        print(f"           {_p}")

# Map each world.txt section title (matched loosely) to a wiki page + nav label,
# in the book's reading order. Titles not listed here still render, appended in
# file order onto the hub-following pages.
_LORE_SECTION_MAP = [
    ("PREMISE",  "lore.html",          "Overview"),
    ("MAP",      "lore-map.html",      "The Map"),
    ("FIFTEEN",  "lore-cultures.html", "The Fifteen"),
    ("WORLD",    "lore-map.html",      "The Map"),   # merged into the Map page
    ("TIMELINE", "lore-ages.html",     "The Timeline"),
    ("DARKNESS", "lore-darkness.html", "Age of Darkness"),
]
def _lore_page_for(title):
    up = title.upper()
    for key, url, label in _LORE_SECTION_MAP:
        if key in up:
            return url, label
    return None, None

# Which Lore pages we'll emit, in reading order — decided up front from the
# sections present, so nav() (built before the pages emit) and the emission
# below stay in sync.
LORE_NAV = []
_seen_urls = set()
for _title, _ in WORLD_SECTIONS:
    _url, _label = _lore_page_for(_title)
    if _url and _url not in _seen_urls:
        LORE_NAV.append((_url, _label)); _seen_urls.add(_url)

SRC = sys.argv[1] if len(sys.argv) > 1 else "RULES.md"
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "wiki"
os.makedirs(OUTDIR, exist_ok=True)

# ── world map image (map7.png) ────────────────────────────────────────────────
# Discovered like world.txt (cwd, this script, the RULES file, their parents, and
# worldbuilding/ or Assets/ under each), copied into the output so it deploys with
# the wiki, and embedded on the Map lore page. Override with WORLD_MAP=<path>.
import shutil as _shutil
def _find_asset(fname, subdirs=("", "worldbuilding", "Assets", "assets", "img")):
    env = os.environ.get("WORLD_MAP")
    if env and os.path.exists(env):
        return env
    bases = [os.getcwd(), _SCRIPT_DIR, _RULES_DIR,
             os.path.dirname(_SCRIPT_DIR), os.path.dirname(_RULES_DIR)]
    for base in bases:
        for sub in subdirs:
            p = os.path.normpath(os.path.join(base, sub, fname))
            if os.path.exists(p):
                return p
    return None

MAP_IMG_SRC = _find_asset("map7.png")
MAP_IMG = None  # basename referenced from lore-map.html once copied
if MAP_IMG_SRC:
    try:
        MAP_IMG = os.path.basename(MAP_IMG_SRC)
        _shutil.copyfile(MAP_IMG_SRC, os.path.join(OUTDIR, MAP_IMG))
        print(f"  [lore] map image -> {MAP_IMG_SRC}")
    except Exception as _e:
        print(f"  [lore] map image found but copy failed: {_e}")
        MAP_IMG = None


TYPE_ORDER = ["Raw Materials","Husbandry","Energy","Craft","Power","Civic","Secrecy","Monument"]
DOMAINS = ["Industry","Prowess","Cunning","Piety"]
TIERS = ["Rising","Established","Sovereign"]

def slug(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
def dom_of(u):
    for d in DOMAINS:
        if d in (u or ""): return d
    return None
def tier_of(u):
    for t in ["Untested"]+TIERS:
        if t in (u or ""): return t
    return None

# ── linkable terms: pursuits link to their TYPE page (anchored) ──
# Priority is first-write-wins (setdefault). Order matters: pursuits, factions,
# domain-board, section aliases, reference and lore pages are all registered
# BEFORE the glossary, so a term with a dedicated home links there and the
# glossary stub only catches terms with no richer page.
TERMS = {}
for name, d in rd.NODES.items():
    TERMS[name] = (f"type-{slug(d.get('type','other'))}.html", slug(name))
FACTIONS = getattr(rd, "FACTIONS", {})
for f in FACTIONS:
    TERMS.setdefault(f, ("factions.html", slug(f)))

# Domain-standing effect names (e.g. "Grand Vizier", "Titan of Industry") -> domain board.
# Each DOMAIN_BOARD cell reads "Name: description"; register the Name part.
for _dom, _tiers in getattr(rd, "DOMAIN_BOARD", {}).items():
    if not isinstance(_tiers, dict):
        continue
    for _tier, _txt in _tiers.items():
        if _tier not in ("Rising", "Established", "Sovereign"):
            continue
        if isinstance(_txt, str) and ":" in _txt:
            _name = _txt.split(":", 1)[0].strip()
            if _name and len(_name) > 2:
                TERMS.setdefault(_name, ("domain-board-ref.html", None))

# Single-word game terms whose lowercase form is common English (e.g. "keep",
# "strike", "save"). For these we require an EXACT-CASE match before linking, so
# ordinary prose isn't peppered with false-positive links. Multiword and proper
# terms are always matched case-insensitively.
AMBIGUOUS_TERMS = {
    "Strike","Save","Reach","Recover","Parry","Speed","Steady","Drilled","Nimble",
    "Serrated","Strained","Focused","Damaged","Build","Move","Host","Support",
    "Oppose","Hold","Rush","Charge","Keep","Cost","Library","Garrison","Standing",
    "Deflect","Recoup","Sack","Sally","Convert","Capture","Cipher","Panic","Rout",
}

TERM_RE = None
_LOWER_MAP = {}
def _rebuild_terms():
    """Rebuild the matcher + lowercase lookup from the current TERMS dict. Call
    once after all term registration; cheap to call again if TERMS grows."""
    global TERM_RE, _LOWER_MAP
    term_list = sorted(TERMS, key=lambda t: -len(t))
    TERM_RE = re.compile(r"\b(" + "|".join(re.escape(t) for t in term_list) + r")\b", re.IGNORECASE)
    _LOWER_MAP = {t.lower(): t for t in TERMS}
_rebuild_terms()

_TAG_SPLIT = re.compile(r"(<[^>]+>)")
def _link_text(text, current, current_anchor, seen):
    def repl(m):
        matched = m.group(1)
        key = _LOWER_MAP.get(matched.lower())
        if key is None:
            return matched
        # ambiguous common words: only link the exact-case (proper-noun) form
        if key in AMBIGUOUS_TERMS and matched != key:
            return matched
        # first occurrence only (per autolink call → per page for prose, per cell
        # for tables): don't re-link the same term again in this blob
        if key in seen:
            return matched
        url, anchor = TERMS[key]
        # suppress a true self-reference (same page + same/absent anchor);
        # note the first *valid* link before we mark it seen
        if url == current and (anchor is None or anchor == current_anchor):
            return matched
        seen.add(key)
        href = url + (f"#{anchor}" if anchor else "")
        return f'<a class="term" href="{href}">{matched}</a>'
    return TERM_RE.sub(repl, text)

def autolink(text, current=None, current_anchor=None, seen=None):
    """Tag-aware autolinker. Links glossary/pursuit/reference/lore terms, but never
    inside an existing <a>, inside <code>, inside a heading, or inside tag
    attributes — and only the first occurrence of each term per call."""
    if seen is None:
        seen = set()
    out, skip, head = [], 0, 0
    for tok in _TAG_SPLIT.split(text):
        if tok.startswith("<") and tok.endswith(">"):
            low = tok.lower(); m = re.match(r"</?([a-z0-9]+)", low)
            name = m.group(1) if m else ""
            close = low.startswith("</"); selfclose = low.endswith("/>")
            if name in ("a", "code"):
                if close: skip = max(0, skip - 1)
                elif not selfclose: skip += 1
            elif name in ("h1","h2","h3","h4","h5","h6"):
                if close: head = max(0, head - 1)
                elif not selfclose: head += 1
            out.append(tok)
        else:
            out.append(tok if (skip or head or not tok) else _link_text(tok, current, current_anchor, seen))
    return "".join(out)

# ── markdown inline + block ──
def md_inline(s):
    s=html.escape(s)
    s=re.sub(r"\*\*\*(.+?)\*\*\*",r"<strong><em>\1</em></strong>",s)
    s=re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",s)
    s=re.sub(r"\*(.+?)\*",r"<em>\1</em>",s)
    s=re.sub(r"`(.+?)`",r"<code>\1</code>",s)
    return s
def md_to_html(md,current=None):
    md = wm.preprocess_inline(md)
    out,i,lines=[],0,md.split("\n")
    # list-nesting stack: each entry is the source indent width that opened a <ul>.
    # Empty = not currently in a list. Indentation (leading spaces, tab=4) sets depth:
    # a deeper indent than the current level opens a nested <ul>; a shallower one closes
    # back down to the matching level.
    stack=[]
    def close_all():
        while stack:
            out.append("</ul>"); stack.pop()
    while i<len(lines):
        raw=lines[i]
        ln=raw.rstrip()
        if not ln.strip():
            close_all(); i+=1; continue
        m=re.match(r"^(#{1,6})\s+(.*)$",ln)
        if m:
            close_all()
            lvl=len(m.group(1)); out.append(f"<h{lvl} id='{slug(m.group(2))}'>{md_inline(m.group(2))}</h{lvl}>")
            i+=1; continue
        _bh = wm.block_html(ln)
        if _bh is not None:
            close_all(); out.append(_bh); i += 1; continue
        # GFM pipe table: a header row containing '|', then a separator row of
        # dashes (|---|---|), then zero or more body rows. Rendered with the same
        # table styling as the data-driven reference pages.
        if "|" in ln and i+1 < len(lines) and re.match(r"^\s*\|?[\s:\-|]+\|[\s:\-|]*$", lines[i+1].rstrip()) and "-" in lines[i+1]:
            close_all()
            def _cells(row):
                row = row.strip()
                if row.startswith("|"): row = row[1:]
                if row.endswith("|"): row = row[:-1]
                return [c.strip() for c in row.split("|")]
            header = _cells(ln)
            i += 2  # skip header + separator
            body_rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                body_rows.append(_cells(lines[i])); i += 1
            th = "".join(f"<th>{md_inline(c)}</th>" for c in header)
            trs = []
            for r in body_rows:
                tds = "".join(f"<td>{md_inline(c)}</td>" for c in r)
                trs.append(f"<tr>{tds}</tr>")
            out.append(f"<table class='pursuits'><thead><tr>{th}</tr></thead><tbody>{''.join(trs)}</tbody></table>")
            continue
        lm=re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$",ln)
        if lm:
            indent=len(lm.group(1).replace("\t","    "))
            if not stack:
                out.append("<ul>"); stack.append(indent)
            elif indent>stack[-1]:
                # deeper → open a nested list (nest inside the open <li>: reopen it)
                out.append("<ul>"); stack.append(indent)
            else:
                # same or shallower → close lists until we're at/under this indent
                while len(stack)>1 and indent<stack[-1]:
                    out.append("</ul>"); stack.pop()
            out.append("<li>"+md_inline(lm.group(3))+"</li>")
            i+=1; continue
        close_all()
        out.append("<p>"+md_inline(ln)+"</p>"); i+=1
    close_all()
    return autolink("\n".join(out),current)

# ── split RULES.md ──
raw=open(SRC,encoding="utf-8").read()
parts=re.split(r"(?m)^#{1,2}\s+",raw)
intro=parts[0]; sections=[]
for c in parts[1:]:
    nl=c.find("\n"); title=(c[:nl] if nl>=0 else c).strip()
    body_raw=(c[nl+1:] if nl>=0 else "")
    sections.append((title,"## "+title+"\n"+body_raw))
# Parent-divider sections (e.g. "# The Turn", "# Armies") carry no prose of their
# own — their content lives in child sub-sections that became their own pages.
# These render as blank pages, so we skip emitting them and drop them from nav.
# A section is "empty" when nothing but whitespace follows its title line.
def _section_is_empty(body_md):
    # body_md = "## Title\n<rest>"; strip the title line, check the remainder
    nl = body_md.find("\n")
    rest = body_md[nl+1:] if nl >= 0 else ""
    return not rest.strip()
EMPTY_SECTIONS = {t for t, b in sections if _section_is_empty(b)}
# Sections we actually build pages for / show in nav.
sections_live = [(t, b) for t, b in sections if t not in EMPTY_SECTIONS]

# register rule-section titles + aliases as linkable terms (now that sections exist)
_section_slugs = {slug(t) for t,_ in sections_live}
_SECTION_ALIASES = {
    "Domain Standings": "Domain Standings", "Domain Standing": "Domain Standings",
    "Bandit Mechanics": "Bandit Mechanics", "Bandits": "Bandit Mechanics", "Bandit Camp": "Bandit Mechanics",
    "Territory": "Territory", "Territories": "Territory",
    "Public Order": "Public Order",
    "Treasury Management": "Treasury Management", "Insolvency": "Treasury Management", "Bankruptcy": "Treasury Management",
    "Seasons": "Seasons", "Siege Warfare": "Siege Warfare", "Siege": "Siege Warfare",
    "Battle Phase": "Battle Phase", "Council Phase": "Council Phase", "Envoy Phase": "Envoy Phase",
    "Trade & Income Rules": "Trade & Income Rules", "Settlements": "Settlements", "Settlement": "Settlements",
    "Infrastructure": "Infrastructure", "Treaties & Alliances": "Treaties & Alliances",
    "Alliance": "Treaties & Alliances", "Treaty": "Treaties & Alliances",
    "Edicts": "Edicts", "Edict": "Edicts", "Vassalization": "Edicts", "Vassalize": "Edicts",
}
for alias, section in _SECTION_ALIASES.items():
    if slug(section) in _section_slugs:
        TERMS.setdefault(alias, (f"rules-{slug(section)}.html", None))

# Envoy Outcomes page — register early so rule pages can link to it.
TERMS.setdefault("Envoy Outcome",       ("envoy-outcomes-ref.html", None))
TERMS.setdefault("Envoy Outcomes",      ("envoy-outcomes-ref.html", None))
TERMS.setdefault("Domain Resolve Table", ("envoy-outcomes-ref.html", None))

# ── register EVERY reference/lore term up front ───────────────────────────────
# Historically these were registered as a side effect of generating each ref page,
# which runs AFTER the rule/type pages — so the matcher was frozen before ~50 of
# them existed and they never linked anywhere. Registering them here, before any
# page is emitted, lets every page cross-link the full vocabulary.
def _register_reference_terms():
    reg = [
        ("INFRASTRUCTURE", "infrastructure-ref.html"),
        ("WONDERS",        "wonders-ref.html"),
        ("ACTIONS",        "actions-ref.html"),
        ("TREATIES",       "treaties-ref.html"),
        ("EDICTS",         "edicts-ref.html"),
        ("TERRAIN",        "terrain-ref.html"),
        ("SETTLEMENTS",    "settlements-ref.html"),
        ("RETINUES",       "equipment-ref.html"),
        ("WEAPONS",        "equipment-ref.html"),
        ("RANGED",         "equipment-ref.html"),
        ("SHIELDS",        "equipment-ref.html"),
        ("ARMORS",         "equipment-ref.html"),
    ]
    for attr, page_url in reg:
        for n in getattr(rd, attr, {}) or {}:
            if n and isinstance(n, str):
                TERMS.setdefault(n, (page_url, None))
    for kind in ("faith", "doubt"):
        for n in getattr(rd, "PO_MODIFIERS", {}).get(kind, {}):
            TERMS.setdefault(n, ("systems-ref.html", None))
    for n in getattr(rd, "TIMERS", {}) or {}:
        TERMS.setdefault(n, ("systems-ref.html", None))

def _register_lore_terms():
    # culture demonyms link to their entry on the Fifteen page
    for name in WORLD_CULTURES:
        TERMS.setdefault(name, ("lore-cultures.html", slug(name)))
    # named places link to their gazetteer row on the Map page; seas have no
    # gazetteer row (they're in The Sea table) so they link to the page itself
    for p in WORLD_PLACES:
        if not p.get("name"):
            continue
        if p["kind"] in ("territory", "unclaimed"):
            TERMS.setdefault(p["name"], ("lore-map.html", "geo-" + slug(p["name"])))
        else:
            TERMS.setdefault(p["name"], ("lore-map.html", None))

_register_reference_terms()
_register_lore_terms()
# Glossary LAST: it's the fallback home for any term without a richer page, so
# stubs (e.g. "Siege") never shadow a dedicated rules/reference page.
for term in rd.GLOSSARY:
    TERMS.setdefault(term, ("glossary.html", slug(term)))
# rebuild the matcher now that TERMS is complete
_rebuild_terms()

# ── nav ──
def nav(current=""):
    groups = []  # (group_id, label, [link_html, ...])
    def A(u, label):
        return f"<a href='{u}'{' class=active' if u==current else ''}>{label}</a>"

    rules = [A("turn-sequence.html", "★ Turn Sequence")]
    for t, _ in sections_live:
        rules.append(A(f"rules-{slug(t)}.html", html.escape(t)))
    groups.append(("rules", "Rules", rules))

    pursuits = [A("pursuits.html", "Overview")]
    for t in TYPE_ORDER:
        pursuits.append(A(f"type-{slug(t)}.html", t))
    groups.append(("pursuits", "Pursuits", pursuits))

    views = [A(f"domain-{slug(d)}.html", d) for d in DOMAINS]
    views.append(A("paths.html", "Build Paths"))
    groups.append(("views", "Views", views))

    ref = []
    for label, uu in [("Actions","actions-ref.html"),("Envoy Outcomes","envoy-outcomes-ref.html"),
                      ("Treaties & Alliances","treaties-ref.html"),("Edicts","edicts-ref.html"),
                      ("Economy","economy-ref.html"),("Terrain & Movement","terrain-ref.html"),
                      ("Bandits","bandits-ref.html"),("Timers, Influence & PO","systems-ref.html"),
                      ("Equipment","equipment-ref.html"),("Combat Keywords","keywords-ref.html"),
                      ("Infrastructure","infrastructure-ref.html"),("Wonders","wonders-ref.html"),
                      ("Settlements","settlements-ref.html"),("Eras","eras-ref.html"),
                      ("Public Order","public-order-ref.html"),("Domain Board","domain-board-ref.html"),
                      ("Seasons","seasons-ref.html"),("Tactic Matrix","tactic-matrix-ref.html"),
                      ("Reference Tables","reference-tables.html")]:
        ref.append(A(uu, label))
    ref.append(A("glossary.html", "Glossary"))
    if FACTIONS:
        ref.append(A("factions.html", "Factions"))
    groups.append(("reference", "Reference", ref))

    esc = [A(uu, label) for label, uu in
           [("Overview","escalation.html"),("Battle Rules","escalation-rules.html"),
            ("Combat Pursuits","escalation-pursuits.html"),("Tactic Matrix","tactic-matrix-ref.html"),
            ("Equipment","equipment-ref.html"),("Combat Keywords","keywords-ref.html")]]
    groups.append(("escalation", "Escalation", esc))

    if LORE_NAV:
        groups.append(("lore", "Lore", [A(uu, label) for uu, label in LORE_NAV]))

    out = []
    for gid, label, links in groups:
        out.append(f"<div class='navgroup' data-group='{gid}'>"
                   f"<button type='button' class='navhead'>{label}<span class='chev'>›</span></button>"
                   f"<div class='navlinks'>{''.join(links)}</div></div>")
    return "\n".join(out)

def page(title,body,current=""):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>(function(){{try{{var t=localStorage.getItem('theme')||'dark';document.documentElement.setAttribute('data-theme',t);if(localStorage.getItem('gamemode')==='1')document.documentElement.classList.add('game-pending');}}catch(e){{document.documentElement.setAttribute('data-theme','dark');}}}})();</script>
<title>{html.escape(title)} — Renown</title><link rel="stylesheet" href="wiki.css"></head><body>
<input id="q" placeholder="Search…" autocomplete="off"><div id="results"></div>
<button id="navtoggle" aria-label="Menu" onclick="document.body.classList.toggle('nav-open')">☰</button>
<div class="topbtns">
<button id="gamemode" type="button" aria-label="Game mode" title="Game mode: rules + reference only">♟</button>
<button id="theme" type="button" aria-label="Toggle dark mode" title="Toggle dark mode">◐</button>
</div>
<div class="wrap"><nav>{nav(current)}</nav><main>{body}</main></div>
<script src="search.js"></script><script src="ui.js"></script>
<div class="versionstamp">Renown v{_VERSION}</div></body></html>"""

search_index=[]

# ── rule section pages ──
for t,body_md in sections_live:
    u=f"rules-{slug(t)}.html"; bh=md_to_html(body_md,u)
    open(os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page(t,bh,u))
    search_index.append({"title":t,"url":u,"text":re.sub(r"<[^>]+>","",bh)[:1200]})
open(os.path.join(OUTDIR,"index.html"),"w",encoding="utf-8").write(
    page("Renown Rules",md_to_html(intro or "# Renown","index.html"),"index.html"))

# ── TYPE pages (canonical pursuit home: full stat table) ──
by_type={}
for n,d in rd.NODES.items(): by_type.setdefault(d.get("type","?"),[]).append(n)
COLS=[("unlock","Gate"),("mastery_req","Build Req"),("innate","Innate"),
      ("mastery","Mastery"),("efficient","Efficient"),("builds_into","Builds Into")]
def stat_table(names,current):
    head="".join(f"<th>{lbl}</th>" for _,lbl in COLS)
    rows=[]
    for n in sorted(names):
        d=rd.NODES[n]; cells=[]
        for k,_ in COLS:
            v=d.get(k,""); v=", ".join(v) if isinstance(v,list) else (v or "")
            cells.append(f"<td>{autolink(md_inline(str(v)),current) if v else '<span class=dim>—</span>'}</td>")
        mon=" ◆" if d.get("monument") else ""
        rows.append(f"<tr id='{slug(n)}'><td class='nm'>{html.escape(n)}{mon}</td>"+"".join(cells)+"</tr>")
    return f"<table class='pursuits'><thead><tr><th>Pursuit</th>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
for t in TYPE_ORDER:
    if t not in by_type: continue
    u=f"type-{slug(t)}.html"
    body=f"<h1>{t} <span class='count'>{len(by_type[t])}</span></h1>"+stat_table(by_type[t],u)
    open(os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page(t,body,u))
    for n in by_type[t]:
        d=rd.NODES[n]
        search_index.append({"title":n,"url":f"{u}#{slug(n)}","text":f"{n} {t} {d.get('innate','')} {d.get('mastery','')}"})

# ── pursuits overview ──
ov=["<h1>Pursuits</h1><p>Pursuits are grouped by <strong>type</strong>. Use the views for domain/standing/path slices.</p><div class='cards'>"]
for t in TYPE_ORDER:
    if t in by_type:
        ov.append(f"<a class='card' href='type-{slug(t)}.html'><span class='ct'>{t}</span><span class='cn'>{len(by_type[t])} pursuits</span></a>")
ov.append("</div>")
open(os.path.join(OUTDIR,"pursuits.html"),"w",encoding="utf-8").write(page("Pursuits","".join(ov),"pursuits.html"))

# ── DOMAIN index pages (filtered link-lists into type pages) ──
def index_page(title,filt,u):
    groups={}
    for n,d in rd.NODES.items():
        if filt(d): groups.setdefault(d.get("type","?"),[]).append(n)
    b=[f"<h1>{title} <span class='count'>{sum(len(v) for v in groups.values())}</span></h1>"]
    for t in TYPE_ORDER:
        if t not in groups: continue
        b.append(f"<h2>{t}</h2><ul class='cols'>")
        for n in sorted(groups[t]):
            b.append(f"<li><a class='term' href='type-{slug(t)}.html#{slug(n)}'>{html.escape(n)}</a> <span class='gate'>{html.escape(rd.NODES[n].get('unlock','') or '')}</span></li>")
        b.append("</ul>")
    open(os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page(title,"".join(b),u))
for d in DOMAINS:
    index_page(f"{d} Pursuits", lambda nd,D=d: dom_of(nd.get("unlock",""))==D, f"domain-{slug(d)}.html")
for t in TIERS:
    index_page(f"{t} Tier", lambda nd,T=t: tier_of(nd.get("unlock",""))==T, f"standing-{slug(t)}.html")

# ── BUILD PATHS page (text chains from builds_into) ──
def chains():
    targets=set()
    for d in rd.NODES.values(): targets|=set(d.get("builds_into") or [])
    roots=sorted([n for n in rd.NODES if n not in targets])
    def node_html(n,seen):
        d=rd.NODES.get(n,{})
        link=f"<a class='term' href='type-{slug(d.get('type','other'))}.html#{slug(n)}'>{html.escape(n)}</a>"
        mon=" ◆" if d.get("monument") else ""
        kids=[c for c in (d.get("builds_into") or []) if c not in seen]
        inner=""
        if kids:
            inner="<ul>"+"".join(node_html(c,seen|{c}) for c in kids)+"</ul>"
        return f"<li>{link}{mon}{inner}</li>"
    b=["<h1>Build Paths</h1><p>Chains follow <em>builds-into</em> from each root pursuit. ◆ = Monument.</p>"]
    for r in roots:
        b.append(f"<div class='chain'><ul>{node_html(r,{r})}</ul></div>")
    return "".join(b)
open(os.path.join(OUTDIR,"paths.html"),"w",encoding="utf-8").write(page("Build Paths",chains(),"paths.html"))

# ── TURN SEQUENCE (hand-built, linked phase flow) ──
# map each phase to its detail page if one exists
import os as _os
_pages = set(f for f in _os.listdir(OUTDIR) if f.endswith(".html"))
def _link(label, *candidates):
    for c in candidates:
        if c in _pages:
            return f"<a class='term' href='{c}'>{label}</a>"
    return label

PHASES = [
    ("1 · Empire Phase", "Start of turn. Resolve start-of-turn effects, collect income, check Public Order.",
     ["rules-seasons.html","seasons-ref.html"], ["Income", "Public Order"]),
    ("2 · Council Phase", "Players resolve Council business; Council Envoys are sent and voted before Domain Envoys.",
     ["rules-council-phase.html"], ["Council Envoy", "Influence", "Abstain"]),
    ("3 · Envoy Phase", "Diplomacy Envoys first, then Domain Envoys. Send → Vote → Net Influence → Resolve.",
     ["rules-envoy-phase.html"], ["Envoy", "Influence", "Endorsed", "Condemned", "Diplomacy"]),
    ("4 · Battle Phase", "Skirmishes, Sieges, and Battles resolve. Roll off for Initiative; fight in Skirmishes.",
     ["rules-battle-phase.html","rules-siege-warfare.html"], ["Skirmish", "Initiative", "Battle", "Siege"]),
    ("5 · Rest Phase", "Cleanup → Season +1 → score Renown → spend 1 Domain Point → pass the Host.",
     ["rules-seasons.html","seasons-ref.html"], ["Season", "Renown", "Domain Point", "Edict"]),
]

ts = ["<h1>Turn Sequence</h1>",
      "<p>Each turn flows through five phases, then passes the Host and repeats. "
      "Click a phase for full detail, or any <a class='term' href='glossary.html'>term</a> for its definition.</p>",
      "<div class='turnflow'>"]
for i, (name, desc, pages, terms) in enumerate(PHASES):
    head = _link(name, *pages)
    ts.append(f"<div class='phase'><div class='ph-head'>{head}</div>"
              f"<div class='ph-desc'>{autolink(md_inline(desc),'turn-sequence.html')}</div>")
    if terms:
        chips = " ".join(autolink(t, "turn-sequence.html") for t in terms)
        ts.append(f"<div class='ph-terms'>{chips}</div>")
    ts.append("</div>")
    if i < len(PHASES)-1:
        ts.append("<div class='arrow'>↓</div>")
ts.append("<div class='arrow loop'>↺ back to Empire Phase</div></div>")
open(_os.path.join(OUTDIR,"turn-sequence.html"),"w",encoding="utf-8").write(
    page("Turn Sequence", "".join(ts), "turn-sequence.html"))
search_index.append({"title":"Turn Sequence","url":"turn-sequence.html",
                     "text":"turn sequence empire council envoy battle rest phase order of play"})

# ════════════ REFERENCE PAGES from renown_data structures ════════════
def _kv_table(rows):
    """rows = list of (label, value_html)."""
    return "<table class='kv'>"+"".join(f"<tr><th>{html.escape(str(l))}</th><td>{v}</td></tr>" for l,v in rows)+"</table>"

def _grid(headers, rows, current):
    h="".join(f"<th>{html.escape(str(x))}</th>" for x in headers)
    body=[]
    for r in rows:
        cells="".join(f"<td>{autolink(md_inline(str(c)), current)}</td>" for c in r)
        body.append(f"<tr>{cells}</tr>")
    return f"<table class='pursuits'><thead><tr>{h}</tr></thead><tbody>{''.join(body)}</tbody></table>"

# Infrastructure
if hasattr(rd, "INFRASTRUCTURE"):
    u="infrastructure-ref.html"
    TIER_ORD={"Primitive":0,"Developed":1,"Sophisticated":2}
    items=sorted(rd.INFRASTRUCTURE.items(), key=lambda kv:(TIER_ORD.get(kv[1].get("tier"),9), kv[0]))
    rows=[[n, d.get("tier",""), d.get("upkeep",""), d.get("build_time",""), d.get("requirement",""), d.get("empire_bonus","")] for n,d in items]
    body=f"<h1>Infrastructure <span class='count'>{len(items)}</span></h1>"
    body+="<p>Per-settlement builds on a three-tier ladder. All four Wonders require <strong>all Infrastructure unlocked</strong>.</p>"
    body+=_grid(["Build","Tier","Upkeep","Build Time","Requirement","Effect"], rows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Infrastructure",body,u))
    for n,d in rd.INFRASTRUCTURE.items():
        TERMS.setdefault(n,(u,None)); search_index.append({"title":n,"url":u,"text":f"{n} infrastructure {d.get('empire_bonus','')}"})

# Wonders
if hasattr(rd, "WONDERS"):
    u="wonders-ref.html"
    rows=[[n, d.get("build_time",""), d.get("upkeep",""), d.get("empire_bonus","")] for n,d in rd.WONDERS.items()]
    body=f"<h1>Wonders <span class='count'>{len(rd.WONDERS)}</span></h1>"
    body+="<p>The apex builds — one per Domain, each gated behind <strong>all Infrastructure unlocked</strong> (the Industry spine).</p>"
    body+=_grid(["Wonder","Build Time","Upkeep","Effect"], rows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Wonders",body,u))
    for n,d in rd.WONDERS.items():
        TERMS.setdefault(n,(u,None)); search_index.append({"title":n,"url":u,"text":f"{n} wonder {d.get('empire_bonus','')}"})

# Actions (grouped by domain) — data-driven from rd.ACTIONS
if hasattr(rd, "ACTIONS"):
    u="actions-ref.html"
    DOM_ORDER=["Prowess","Cunning","Piety","Industry","Diplomacy"]
    body=f"<h1>Actions <span class='count'>{len(rd.ACTIONS)}</span></h1>"
    body+="<p>Every Envoy action, grouped by Domain. Each is Sent during the Envoy Phase, voted on, and resolved on a pass.</p>"
    for dom in DOM_ORDER:
        acts=[(n,a) for n,a in rd.ACTIONS.items() if a.get("domain")==dom]
        if not acts: continue
        body+=f"<h2>{dom}</h2>"
        rows=[]
        for n,a in acts:
            req=a.get("requires","") or "\u2014"
            notes=a.get("notes",[])
            eff=a.get("effect","")
            if notes:
                eff = eff + " \u2014 " + "; ".join(notes)
            rows.append([n, a.get("cost","") or "\u2014", req, eff, a.get("endorsed","") or "\u2014"])
        body+=_grid(["Action","Cost","Requires","Effect (if passes)","Endorsed"], rows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Actions",body,u))
    for n,a in rd.ACTIONS.items():
        TERMS.setdefault(n,(u,None)); search_index.append({"title":n,"url":u,"text":f"{n} {a.get('domain','')} action {a.get('effect','')}"})
        
# Envoy Outcomes — data-driven from rd.ENVOY_OUTCOMES + rd.ENVOY_OUTCOME_THRESHOLDS
if hasattr(rd, "ENVOY_OUTCOMES"):
    u="envoy-outcomes-ref.html"
    DOM_ORDER=["Prowess","Cunning","Piety","Industry","Diplomacy"]
    th=getattr(rd,"ENVOY_OUTCOME_THRESHOLDS",{})
    body="<h1>Envoy Outcomes</h1>"
    body+=("<p>How a Sent Envoy resolves by <strong>Net Influence</strong>: "
           f"Condemned (\u2264{th.get('Condemned','?')}), Failed (\u2264{th.get('Failed','?')}, gain Doubt 1), "
           f"Passed (\u2265{th.get('Passed','?')}), Endorsed (\u2265{th.get('Endorsed','?')}). "
           "An individual action's own Endorsed bonus (see Actions) overrides the domain default below.</p>")
    rows=[[dom,
           rd.ENVOY_OUTCOMES[dom].get("condemned",""),
           rd.ENVOY_OUTCOMES[dom].get("failed",""),
           rd.ENVOY_OUTCOMES[dom].get("passed",""),
           rd.ENVOY_OUTCOMES[dom].get("endorsed","")]
          for dom in DOM_ORDER if dom in rd.ENVOY_OUTCOMES]
    body+=_grid(["Domain","Condemned","Failed","Passed","Endorsed"], rows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Envoy Outcomes",body,u))
    for _t in ("Envoy Outcome", "Envoy Outcomes", "Domain Resolve Table"):
        TERMS.setdefault(_t, (u, None))
    search_index.append({"title":"Envoy Outcomes","url":u,
        "text":"envoy outcomes condemned failed passed endorsed net influence resolve domain"})
        
# Treaties & Alliances — data-driven from rd.TREATIES + rd.ALLIANCE_RULES
if hasattr(rd, "TREATIES"):
    u="treaties-ref.html"
    rows=[[n, d.get("signed_via",""), d.get("era",""), d.get("effect","")] for n,d in rd.TREATIES.items()]
    body=f"<h1>Treaties &amp; Alliances <span class='count'>{len(rd.TREATIES)}</span></h1>"
    body+="<p>Standing agreements signed via Diplomacy. Alliances scale with Era.</p>"
    body+=_grid(["Treaty","Signed Via","Era","Effect"], rows, u)
    if hasattr(rd,"ALLIANCE_RULES") and rd.ALLIANCE_RULES:
        body+="<h2>Alliance Rules</h2><ul>"+"".join(f"<li>{html.escape(x)}</li>" for x in rd.ALLIANCE_RULES)+"</ul>"
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Treaties & Alliances",body,u))
    for n,d in rd.TREATIES.items():
        TERMS.setdefault(n,(u,None)); search_index.append({"title":n,"url":u,"text":f"{n} treaty {d.get('effect','')}"})

# Edicts (win paths) — data-driven from rd.EDICTS
if hasattr(rd, "EDICTS"):
    u="edicts-ref.html"
    rows=[[n, d.get("type",""), d.get("requirement","")] for n,d in rd.EDICTS.items()]
    body=f"<h1>Edicts <span class='count'>{len(rd.EDICTS)}</span></h1>"
    body+="<p>Scoring achievements / win paths. Completing one raises the shared Renown tracker by 1; any Edict may be completed multiple times. Whoever has completed the most when the Last Alliance Standing condition is met wins.</p>"
    body+=_grid(["Edict","Type","Requirement"], rows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Edicts",body,u))
    for n,d in rd.EDICTS.items():
        TERMS.setdefault(n,(u,None)); search_index.append({"title":n,"url":u,"text":f"{n} edict win {d.get('requirement','')}"})

# Economy Reference — costs + the three upkeep tracks (rd.COSTS, rd.UPKEEP_TRACKS)
if hasattr(rd, "COSTS") or hasattr(rd, "UPKEEP_TRACKS"):
    u="economy-ref.html"
    body="<h1>Economy Reference</h1>"
    if hasattr(rd, "UPKEEP_TRACKS"):
        body+="<h2>Upkeep — three separate tracks</h2>"
        body+="<p>Each upkeep pool is reduced by different effects; a reducer that names one track does not touch the others.</p>"
        body+=_grid(["Track","How it works"], [[k, v] for k,v in rd.UPKEEP_TRACKS.items()], u)
        if hasattr(rd, "PURSUIT_UPKEEP_BY_TYPE"):
            pu=rd.PURSUIT_UPKEEP_BY_TYPE
            extra=", ".join(f"{k} {v}" for k,v in pu.items())
            dflt=getattr(rd,"PURSUIT_UPKEEP_DEFAULT","")
            body+=f"<p class='mut'>Pursuit upkeep by type: {extra}, all others {dflt}.</p>"
    if hasattr(rd, "COSTS"):
        body+="<h2>Action &amp; empire costs</h2>"
        body+=_grid(["Item","Cost"], [[k, v] for k,v in rd.COSTS.items()], u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Economy Reference",body,u))
    search_index.append({"title":"Economy Reference","url":u,
        "text":"upkeep costs pursuit army infrastructure tax trade "+ " ".join(rd.COSTS.values() if hasattr(rd,'COSTS') else [])})

# Terrain & Movement — TERRAIN + MOVEMENT_MODIFIERS
if hasattr(rd, "TERRAIN"):
    u="terrain-ref.html"
    trows=[[t, d.get("Effect","") or "\u2014", ", ".join(d.get("Raw Materials",[])) or "\u2014"]
           for t,d in rd.TERRAIN.items()]
    body="<h1>Terrain &amp; Movement</h1>"
    body+="<p>The six territory types, their movement effects, and the Raw Material pursuits each can host.</p>"
    body+=_grid(["Terrain","Effect","Raw Materials"], trows, u)
    if hasattr(rd, "MOVEMENT_MODIFIERS"):
        body+="<h2>Movement Modifiers</h2>"
        body+="<p>Sources that change how terrain affects movement (infrastructure, faction, and pursuit effects).</p>"
        mrows=[]
        for k,d in rd.MOVEMENT_MODIFIERS.items():
            eff=d.get("Effect","")
            eff=" ".join(eff) if isinstance(eff,list) else eff
            mrows.append([k, eff])
        body+=_grid(["Source","Effect"], mrows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Terrain & Movement",body,u))
    for t in rd.TERRAIN:
        TERMS.setdefault(t,(u,None)); search_index.append({"title":t,"url":u,"text":f"{t} terrain {rd.TERRAIN[t].get('Effect','')}"})
    search_index.append({"title":"Terrain & Movement","url":u,"text":"terrain movement grassland wetland tundra mountain water forest roads bridge"})

# Bandits — BANDITS + BANDIT_BEHAVIOR + BANDIT_GROWTH_PER_ERA
if hasattr(rd, "BANDITS"):
    u="bandits-ref.html"
    body="<h1>Bandits</h1>"
    body+=_grid(["Term","Rule"], [[k,v] for k,v in rd.BANDITS.items()], u)
    if hasattr(rd, "BANDIT_BEHAVIOR"):
        body+="<h2>Behavior</h2>"
        body+=_grid(["Aspect","Rule"], [[k,v] for k,v in rd.BANDIT_BEHAVIOR.items()], u)
    if hasattr(rd, "BANDIT_GROWTH_PER_ERA"):
        body+="<h2>Growth per Era</h2>"
        body+=_grid(["Era","Retinues / turn"], [[k,str(v)] for k,v in rd.BANDIT_GROWTH_PER_ERA.items()], u)
    if hasattr(rd, "BANDIT_EQUIPMENT_PER_ERA"):
        body+="<h2>Armaments per Era</h2>"
        body+=_grid(["Era","Armaments"], [[k,v] for k,v in rd.BANDIT_EQUIPMENT_PER_ERA.items()], u)
    if hasattr(rd,"BANDIT_CAMP_START"):
        body+=f"<p class='mut'>Camp starts at {rd.BANDIT_CAMP_START} retinues; becomes a Bandit Army at {getattr(rd,'BANDIT_ARMY_THRESHOLD','?')}.</p>"
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Bandits",body,u))
    search_index.append({"title":"Bandits","url":u,"text":"bandits outlaw country camp army growth cunning raze destabilize"})

# Timers / Influence / Public Order modifiers — TIMERS + INFLUENCE_GAIN + PO_MODIFIERS
if hasattr(rd, "TIMERS") or hasattr(rd, "INFLUENCE_GAIN") or hasattr(rd, "PO_MODIFIERS"):
    u="systems-ref.html"
    body="<h1>Timers, Influence &amp; Public Order Modifiers</h1>"
    if hasattr(rd, "TIMERS"):
        body+="<h2>Timers</h2>"
        body+=_grid(["Timer","Where","Tracks"], [[k, d.get("where",""), d.get("tracks","")] for k,d in rd.TIMERS.items()], u)
    if hasattr(rd, "INFLUENCE_GAIN"):
        body+="<h2>Influence Gain (per turn)</h2>"
        body+=_grid(["Source","Change","Notes"], [[k, d.get("change",""), d.get("notes","")] for k,d in rd.INFLUENCE_GAIN.items()], u)
    if hasattr(rd, "PO_MODIFIERS"):
        body+="<h2>Innate Faith / Doubt Sources</h2>"
        porows=[]
        for kind in ("faith","doubt"):
            for name,cond in rd.PO_MODIFIERS.get(kind,{}).items():
                porows.append([kind.capitalize(), name, cond])
        body+=_grid(["Type","Source","Condition"], porows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Timers, Influence & PO",body,u))
    # make PO-modifier names + timer names linkable
    if hasattr(rd,"PO_MODIFIERS"):
        for kind in ("faith","doubt"):
            for name in rd.PO_MODIFIERS.get(kind,{}):
                TERMS.setdefault(name,(u,None))
    if hasattr(rd,"TIMERS"):
        for name in rd.TIMERS:
            TERMS.setdefault(name,(u,None))
    search_index.append({"title":"Timers, Influence & PO","url":u,"text":"timers influence public order modifiers faith doubt border tension"})

# Settlements
if hasattr(rd, "SETTLEMENTS"):
    u="settlements-ref.html"
    items=sorted(rd.SETTLEMENTS.items(), key=lambda kv: kv[1].get("tier",0))
    rows=[[n, d.get("tax_income",""), d.get("muster_limit",""), d.get("wards",""), d.get("reach",""), d.get("build_time",""), d.get("sea_variant") or "—", d.get("notes","")] for n,d in items]
    body=f"<h1>Settlements <span class='count'>{len(items)}</span></h1>"
    body+=_grid(["Settlement","Tax","Muster","Wards","Reach","Build","Sea Variant","Notes"], rows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Settlements",body,u))
    search_index.append({"title":"Settlements","url":u,"text":"settlements hamlet village town city metropolis tax muster wards reach"})

# Eras
if hasattr(rd, "ERAS"):
    u="eras-ref.html"
    items=sorted(rd.ERAS.items(), key=lambda kv: kv[1].get("renown",0))
    rows=[[n, d.get("renown",""), d.get("armies",""), d.get("cities",""), d.get("max_settlements",""), d.get("influence_per_turn",""), d.get("innate_diplomacy_influence",""), d.get("envoys",""), d.get("unlocks","")] for n,d in items]
    body=f"<h1>Eras <span class='count'>{len(items)}</span></h1>"
    body+="<p>Shared-Renown thresholds raise everyone's Era, lifting army/city caps and influence.</p>"
    body+=_grid(["Era","Renown","Armies","Cities","Max Settlements","Influence/Turn","Diplo Infl","Envoys","Unlocks"], rows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Eras",body,u))
    search_index.append({"title":"Eras","url":u,"text":"eras founding ascension eminence zenith renown army cap"})

# Public Order
if hasattr(rd, "PUBLIC_ORDER"):
    u="public-order-ref.html"
    rows=[[k, v[0], v[1]] for k,v in sorted(rd.PUBLIC_ORDER.items(), reverse=True)]
    _lo,_hi=min(rd.PUBLIC_ORDER),max(rd.PUBLIC_ORDER)
    body=f"<h1>Public Order Track</h1><p>From {_lo} to {_hi}; Faith raises it, Doubt lowers it.</p>"
    body+=_grid(["Value","State","Effect"], rows, u)
    if hasattr(rd,"PO_MODIFIERS"):
        body+="<h2>Faith sources</h2>"+_grid(["Source","Condition"], [[k,v] for k,v in rd.PO_MODIFIERS.get("faith",{}).items()], u)
        body+="<h2>Doubt sources</h2>"+_grid(["Source","Condition"], [[k,v] for k,v in rd.PO_MODIFIERS.get("doubt",{}).items()], u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Public Order",body,u))
    search_index.append({"title":"Public Order Track","url":u,"text":"public order faith doubt uprising living saints"})

# Domain Board
if hasattr(rd, "DOMAIN_BOARD"):
    u="domain-board-ref.html"
    db=rd.DOMAIN_BOARD
    DOM_ORDER=["Industry","Prowess","Piety","Cunning"]
    TIER_ORDER=["Rising","Established","Sovereign"]
    rows=[]
    for dom in DOM_ORDER:
        if dom in db:
            rows.append([dom]+[db[dom].get(tier,"") for tier in TIER_ORDER])
    body="<h1>Domain Board</h1><p>Empire-side standing effects unlocked by raising a Domain. Rows are Domains; columns are Standings.</p>"
    body+=_grid(["Domain"]+TIER_ORDER, rows, u)
    mi=db.get("max_influence_per_vote",{}); inn=db.get("innate_influence_own_envoys",{})
    body+="<h2>Influence by Standing</h2>"
    body+=_grid(["Standing","Max Influence / Vote","Innate Influence (own Envoys)"],
                [[t, mi.get(t,""), inn.get(t,"")] for t in ["Untested","Rising","Established","Sovereign"]], u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Domain Board",body,u))
    search_index.append({"title":"Domain Board","url":u,"text":"domain board standing indomitable grand vizier influence"})

# Seasons
if hasattr(rd, "SEASONS"):
    u="seasons-ref.html"
    rows=[[k, v.get("name",""), v.get("effect","")] for k,v in rd.SEASONS.items()]
    body="<h1>Seasons</h1><p>A four-turn cycle; the Rest Phase advances the Season.</p>"+_grid(["Season","Name","Effect"], rows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Seasons",body,u))
    search_index.append({"title":"Seasons","url":u,"text":"seasons winter spring summer fall"})

# Equipment (Retinues / Weapons / Ranged / Shields / Armor)
u="equipment-ref.html"
eq=["<h1>Equipment</h1>"]
if hasattr(rd,"RETINUES"):
    eq.append("<h2>Retinues</h2>")
    eq.append(_grid(["Retinue","Cost","To-Hit","Endurance","Morale","Speed","Max Size"],
        [[n,d.get("cost"),f"{d.get('to_hit')}+",d.get("endurance"),f"{d.get('shaking')}+",d.get("speed","—"),d.get("max_size","—")] for n,d in rd.RETINUES.items()], u))
def _wrow(n,d): return [n, d.get("ap"), (f"+{d['init']}" if d.get('init',0)>0 else d.get('init')), d.get("tier"), ", ".join(d.get("tags",[]))]
if hasattr(rd,"WEAPONS"):
    eq.append("<h2>Melee Weapons</h2>")
    eq.append(_grid(["Weapon","AP","Init","Tier","Keywords"], [_wrow(n,d) for n,d in rd.WEAPONS.items()], u))
if hasattr(rd,"RANGED"):
    eq.append("<h2>Ranged Weapons</h2>")
    eq.append(_grid(["Weapon","AP","Init","Tier","Keywords"], [_wrow(n,d) for n,d in rd.RANGED.items()], u))
if hasattr(rd,"SHIELDS"):
    eq.append("<h2>Shields</h2>")
    eq.append(_grid(["Shield","Save Bonus","Init","Tier","Keywords"],
        [[(n or "None"), f"+{d.get('save_bonus')}", d.get("init"), d.get("tier") or "—", ", ".join(d.get("tags",[]))] for n,d in rd.SHIELDS.items()], u))
if hasattr(rd,"ARMORS"):
    eq.append("<h2>Armor</h2>")
    eq.append(_grid(["Armor","Save","Tier","Keywords"], [[n,f"{d.get('save')}+",d.get("tier"),", ".join(d.get("tags",[]))] for n,d in rd.ARMORS.items()], u))
open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Equipment","".join(eq),u))
search_index.append({"title":"Equipment","url":u,"text":"equipment retinues weapons ranged shields armor stats"})

# Reference Tables — the catch-all for tables with no dedicated page of their own.
# Bandits, Timers, Influence Gain and Bandit-growth all live on bandits-ref /
# systems-ref, so they're linked here rather than duplicated.
u="reference-tables.html"
rt=["<h1>Reference Tables</h1>",
    "<p class='mut'>Odds and ends that don't have a page of their own. "
    "See also <a class='term' href='bandits-ref.html'>Bandits</a>, "
    "<a class='term' href='systems-ref.html'>Timers, Influence &amp; PO</a>, and "
    "<a class='term' href='economy-ref.html'>Economy</a>.</p>"]
if hasattr(rd,"TRADE_RULES"):
    tr=rd.TRADE_RULES
    rt.append("<h2>Trade Rules</h2>")
    rt.append(_kv_table([("Income per Craft", tr.get("income_per_craft","")),("Requirements", tr.get("requirements","")),("No trade in", tr.get("no_trade_season","")),("Tax collected in", tr.get("tax_season",""))]))
if hasattr(rd,"BUILD_TIMERS"):
    rt.append("<h2>Build Timers</h2><p>Turns until a build completes.</p>")
    bt_rows=[]
    for k,v in rd.BUILD_TIMERS.items():
        if isinstance(v,dict):
            for tier,n in v.items(): bt_rows.append([f"{k} ({tier})", n])
        else:
            bt_rows.append([k, v])
    rt.append(_grid(["Build","Turns"], bt_rows, u))
if hasattr(rd,"TIER_UNLOCK"):
    rt.append("<h2>Equipment Tier Ladder</h2><p>Each tier is unlocked by the named Industry node.</p>")
    rt.append(_grid(["Tier","Unlocked by"], [[t,(rd.TIER_UNLOCK.get(t) or "Starting")] for t in getattr(rd,"TIERS",list(rd.TIER_UNLOCK))], u))
if hasattr(rd,"STANDING_EFFECTS"):
    rt.append("<h2>Combat Standing Effects</h2><p>Battlefield effects granted by Domain Standing (Escalation).</p>")
    se_rows=[[dom, tier, eff] for (dom,tier),eff in rd.STANDING_EFFECTS.items()]
    rt.append(_grid(["Domain","Standing","Effect"], se_rows, u))
open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Reference Tables","".join(rt),u))
search_index.append({"title":"Reference Tables","url":u,"text":"trade rules build timers tier unlock standing effects"})

# ── Tactic Matrix (7x7 interaction grid) ──
if hasattr(rd,"TACTIC_MATRIX") and hasattr(rd,"TACTICS"):
    u="tactic-matrix-ref.html"
    def _fmt_cell(c):
        parts=[]
        if c.get("I"):  parts.append(f"I{c['I']:+d}")
        if c.get("TH"): parts.append(f"Strike{c['TH']:+d}")
        if c.get("TS"): parts.append(f"Save{c['TS']:+d}")
        if c.get("end"): parts.append("Battle ends")
        if c.get("no_combat"): parts.append("No combat")
        return ", ".join(parts) if parts else "—"
    tt=rd.TACTICS
    # header row: your tactic (rows) vs their tactic (cols); cell = YOUR modifier
    head="<th>You ↓ / Them →</th>"+"".join(f"<th>{html.escape(t)}</th>" for t in tt)
    body=[]
    for a in tt:
        cells=[f"<th>{html.escape(a)}</th>"]
        for b in tt:
            pair=rd.TACTIC_MATRIX.get((a,b))
            cells.append(f"<td>{_fmt_cell(pair[0]) if pair else '—'}</td>")
        body.append("<tr>"+"".join(cells)+"</tr>")
    grid=f"<table class='pursuits tacticmatrix'><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"
    tm=["<h1>Tactic Matrix</h1>",
        "<p>Both players reveal a Tactic each Skirmish. Each cell shows <strong>your</strong> modifier when you play the row tactic and your opponent plays the column tactic. "
        "I = Initiative, Strike = to-Strike roll, Save = Save roll (lower target is better).</p>",
        grid,
        "<p style='margin-top:16px;font-size:13px'>The seven Tactics: "+", ".join(f"<a class='term' href='glossary.html'>{html.escape(t)}</a>" for t in tt)+".</p>"]
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Tactic Matrix","".join(tm),u))
    search_index.append({"title":"Tactic Matrix","url":u,"text":"tactic matrix scout ambush flank charge fighting defensive formation fall back initiative"})

# ════════════ ESCALATION SECTION ════════════
# Landing page (hub) + Battle Rules (prose, mirrors the PDF) + Combat Pursuits (data-driven from escalation.ranks).
u="escalation.html"
esc_body=["<h1>Escalation Campaign</h1>",
 "<p>A fast, battle-driven mode for 2+ players over ten or more turns. Every player runs the same starting army; "
 "what carries between Battles is your Standings, Pursuits, unlocks, and Victory Points.</p>",
 "<h2>In this section</h2>",
 "<table class='pursuits'><tbody>",
 "<tr><td><a href='escalation-rules.html'>Battle Rules</a></td><td>Setup, turn sequence, victory points, and the step-by-step Skirmish walkthrough.</td></tr>",
 "<tr><td><a href='escalation-pursuits.html'>Combat Pursuits</a></td><td>The pursuits available in Escalation, by Domain, with their unlock and rank effects.</td></tr>",
 "<tr><td><a href='tactic-matrix-ref.html'>Tactic Matrix</a></td><td>The 7\u00d77 grid of Tactic interactions revealed each Skirmish.</td></tr>",
 "<tr><td><a href='equipment-ref.html'>Equipment / Armory</a></td><td>Retinues, weapons, ranged, shields, and armor stats.</td></tr>",
 "<tr><td><a href='keywords-ref.html'>Combat Keywords</a></td><td>Deadly, Cleave, Poison, Parry, and the rest \u2014 what every keyword does.</td></tr>",
 "<tr><td><a href='domain-board-ref.html'>Domain Board</a></td><td>Standing effects and the influence track.</td></tr>",
 "</tbody></table>"]
open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Escalation Campaign","".join(esc_body),u))
search_index.append({"title":"Escalation Campaign","url":u,"text":"escalation campaign combat battle mode overview"})

# Battle Rules (prose, mirrors build_escalation_campaign_pdf.py — keep in sync if the PDF rules change)
u="escalation-rules.html"
er=["<h1>Escalation \u2014 Battle Rules</h1>"]
er.append("<h2>Dice Principle</h2>")
er.append("<p>A successful roll is written <strong>X+</strong>: roll that number or higher on a d6. Each <strong>\u22121</strong> penalty "
          "requires your roll to be one higher; each <strong>+1</strong> bonus, one lower. If a 7+ is ever needed it automatically fails; "
          "if a 1 or less is needed it automatically passes (but if a natural result could still trigger an effect, you still roll). "
          "A <strong>natural</strong> roll is the die before modifiers; a <strong>natural 6</strong> triggers Cleave, Deadly, Destroy Shield "
          "and Riposte (and a natural-6 Save fails against Poison).</p>")
er.append("<h2>Setup</h2>")
er.append("<p>Each player starts with <strong>25 Levy retinues, Farm Tools, Cloth armor, no shield</strong>. All four Domains start "
          "Untested. No Pursuits, 0 VP. Every Battle is fought at an army size of 25; Standings, Pursuits, unlocks and VP carry over.</p>")
er.append("<h2>Turn Sequence</h2>")
er.append("<p><strong>1 \u2014 Battle.</strong> Pair off and fight one Battle (rotate pairings each turn).</p>")
er.append(_grid(["Result","VP"],[
    ["Decisive Win: reduce the enemy army to zero or cause a Rout.","+3"],
    ["Minor Victory: the enemy army Fell Back.","+2"],
    ["Lose, but end it via a successful Fall Back with 1+ retinue remaining.","+1"],
    ["Lose any other way (wiped out, Routed, failed Fall Back).","0"]], u))
er.append("<p><strong>2 \u2014 Advancement</strong> (all players simultaneously): unlock one Domain Standing (advance one Domain one step, "
          "if the prior standing is unlocked); perform one Build Action (construct one Pursuit you qualify for); and you may change your "
          "army to any composition you have unlocked.</p>")
er.append("<h2>Battle Walkthrough</h2>")
er.append("<p>Roll off for Initiative (<strong>+1 if you won your last Battle</strong>, re-roll ties). The higher roller Seizes the "
          "Initiative: they are the Attacker and gain +1 Initiative in the first Skirmish. A Battle is a series of Skirmishes \u2014 repeat "
          "these steps until it ends:</p>")
_steps=[
 ("Form the Field","Place up to 10 retinues in the front line (one attack each) plus up to 5 in reserve."),
 ("Choose Tactics","Both players secretly pick one Tactic, then reveal together."),
 ("Declare equipment","The Attacker names equipment first; the Defender responds."),
 ("Initiative","Runs \u22122 to +2. Higher Strikes first. At \u22122 or lower you Blunder (Strike can't be improved beyond 6+)."),
 ("Roll to Strike","Roll a d6 per front-line retinue against the to-Strike number (plus bonuses, minus 1 per Fatigue token, to a max of 6+, then other penalties)."),
 ("Strike and defend","Resolve Strikes \u2014 Parry (resolve Ripostes), then Save, then Recover. Casualties leave the field at once."),
 ("Panic check","A side taking 5+ casualties this Skirmish takes a Panic check (d6 per retinue, up to 5 dice); a value modified to 7+ Routs the army. At most once per Skirmish."),
 ("Strike back","The other player Strikes the same way, if able."),
 ("Lose Endurance","Each army that fought loses 1 Endurance; at 0 it is Fatigued."),
 ("Break check","Each Fatigued field rolls Morale (up to 5 dice) before gaining its token; failures are casualties; never triggers Panic. 7+ Routs."),
 ("Fatigue token","Each Fatigued side gains a token: \u22121 to Strike, Morale, Parry, Recover (capped 6+ except Morale); they stack."),
 ("End the Skirmish","The Battle ends if a side hits 0, Routs, or Falls Back. You cannot Fall Back in the first two Skirmishes."),
]
er.append("<ol>")
for h,b in _steps:
    er.append(f"<li><strong>{html.escape(h)}.</strong> {autolink(md_inline(b),u)}</li>")
er.append("</ol>")
open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Escalation Battle Rules","".join(er),u))
search_index.append({"title":"Escalation Battle Rules","url":u,"text":"escalation battle rules setup turn sequence skirmish walkthrough victory points dice"})

# Combat Pursuits (data-driven from escalation.ranks, grouped by Domain)
u="escalation-pursuits.html"
esc_nodes=rd.get_data("escalation")
from collections import defaultdict as _dd
_groups=_dd(list)
for nm,n in esc_nodes.items():
    e=n.get("escalation",{}) or {}
    st=e.get("standing","")
    dom=next((d for d in ["Industry","Prowess","Piety","Cunning"] if d in st),"Other")
    _groups[dom].append((nm,e.get("standing",""),e.get("ranks",{}) or {},n.get("mastery_req",""),n.get("monument")))
cp=["<h1>Escalation \u2014 Combat Pursuits</h1>",
    "<p>The pursuits available in the Escalation Campaign, grouped by Domain. <strong>Unlock</strong> is the Domain Standing required to build; "
    "<strong>Mastery Req</strong> lists the pursuits needed to master it. Rank&nbsp;1 is the innate effect; Rank&nbsp;2 (where present) is the mastery effect.</p>"]
DOM_COLOR={"Industry":"#1f4e8c","Prowess":"#9e1b1b","Piety":"#b89400","Cunning":"#1a1a1a"}
for dom in ["Industry","Prowess","Piety","Cunning"]:
    if dom not in _groups: continue
    cp.append(f"<h2 style='color:{DOM_COLOR[dom]}'>{dom}</h2>")
    rows=[]
    for nm,st,ranks,mreq,mon in sorted(_groups[dom], key=lambda r:r[1]):
        r1=ranks.get(1,"") or ""
        r2=ranks.get(2,"") or ""
        label=f"{nm} \u2605" if mon else nm
        rows.append([label, st, (mreq or "\u2014"), r1, (r2 or "\u2014")])
    cp.append(_grid(["Pursuit","Unlock","Mastery Req","Rank 1 (Innate)","Rank 2 (Mastery)"], rows, u))
open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Escalation Combat Pursuits","".join(cp),u))
search_index.append({"title":"Escalation Combat Pursuits","url":u,"text":"escalation combat pursuits industry prowess piety cunning ranks mastery monument"})


# Combat Keywords (the keyword subset of glossary)
u="keywords-ref.html"
KW=[rd.STEADY,rd.UNWIELDY,rd.TWO_H,rd.SHATTER_ARMOR,rd.UNSTOPPABLE,rd.CLEAVE,rd.POISON,rd.NIMBLE,rd.DRILLED,rd.DESTROY_SHIELD,rd.BLUNDER,rd.ONE_SHOT,rd.DEFLECT,rd.IMMUNE_PANIC,rd.UNBREAKABLE,rd.PARRY,rd.RIPOSTE,rd.RECOVER,rd.SERRATED,rd.PLANISHING,rd.FATIGUE_TOKEN,rd.MINUS_1_TBH,rd.NEGATE_UNSTOPPABLE,rd.NEGATE_TEMPERED,rd.MINUS_1_PARRY,rd.NEGATE_RIPOSTE]
kw=["<h1>Combat Keywords</h1><dl class='gloss'>"]
for k in KW:
    if k in rd.GLOSSARY:
        kw.append(f"<dt id='{slug(k)}'>{html.escape(k)}</dt><dd>{autolink(md_inline(str(rd.GLOSSARY[k])),u,slug(k))}</dd>")
kw.append("</dl>")
open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Combat Keywords","".join(kw),u))
search_index.append({"title":"Combat Keywords","url":u,"text":"keywords deadly cleave poison parry riposte"})

# ── glossary ──
# A term's "context page": where it's used/defined more fully than the glossary
# stub. Built from the richer registries so a glossary entry can link out to it.
CONTEXT_PAGE = {}
for _n in getattr(rd, "NODES", {}):           # pursuits -> their type page
    CONTEXT_PAGE[_n] = TERMS[_n]
for _n in getattr(rd, "ACTIONS", {}):          # actions -> actions-ref
    CONTEXT_PAGE[_n] = ("actions-ref.html", None)
for _n in getattr(rd, "TREATIES", {}):
    CONTEXT_PAGE[_n] = ("treaties-ref.html", None)
for _n in getattr(rd, "EDICTS", {}):
    CONTEXT_PAGE.setdefault(_n, ("edicts-ref.html", None))
for _n in getattr(rd, "FACTIONS", {}):
    CONTEXT_PAGE[_n] = ("factions.html", slug(_n))
# hand-mapped concept -> reference page for common glossary nouns
_CONCEPT_PAGE = {
    "Reach":"settlements-ref.html","Reach X":"settlements-ref.html",
    "Public Order":"public-order-ref.html","Standing":"domain-board-ref.html",
    "Domain":"domain-board-ref.html","Renown":"eras-ref.html","Era":"eras-ref.html",
    "Treaty":"treaties-ref.html","Alliance":"treaties-ref.html","Edict":"edicts-ref.html",
    "Bandit":"bandits-ref.html","Outlaw Country":"bandits-ref.html",
    "Influence":"systems-ref.html",
    "Speed":"economy-ref.html","Extort X":"economy-ref.html","Recoup":"economy-ref.html",
    "Territory":"terrain-ref.html","Province":"terrain-ref.html","Region":"terrain-ref.html",
}
for _t,_pg in _CONCEPT_PAGE.items():
    CONTEXT_PAGE.setdefault(_t, (_pg, None))

gl=["<h1>Glossary</h1><dl class='gloss'>"]
for term in sorted(rd.GLOSSARY):
    sl=slug(term)
    body=autolink(md_inline(str(rd.GLOSSARY[term])),'glossary.html',sl)
    # "Used in" backlink to a richer context page, when one exists and differs.
    used=""
    cp=CONTEXT_PAGE.get(term)
    if cp and cp[0]!="glossary.html":
        href=cp[0]+(f"#{cp[1]}" if cp[1] else "")
        used=f" <a class='usedin' href='{href}'>→ in context</a>"
    gl.append(f"<dt id='{sl}'>{html.escape(term)}</dt><dd>{body}{used}</dd>")
gl.append("</dl>")
open(os.path.join(OUTDIR,"glossary.html"),"w",encoding="utf-8").write(page("Glossary","".join(gl),"glossary.html"))
for term in rd.GLOSSARY:
    search_index.append({"title":term,"url":f"glossary.html#{slug(term)}","text":f"{term} {rd.GLOSSARY[term]}"})

# ── factions ──
if FACTIONS:
    fi=["<h1>Factions</h1><dl class='gloss'>"]
    for f in sorted(FACTIONS):
        fd=FACTIONS[f]; desc=fd if isinstance(fd,str) else (fd.get("mechanic") or fd.get("feel") or "")
        fi.append(f"<dt id='{slug(f)}'>{html.escape(f)}</dt><dd>{md_inline(str(desc))}</dd>")
    fi.append("</dl>")
    open(os.path.join(OUTDIR,"factions.html"),"w",encoding="utf-8").write(page("Factions","".join(fi),"factions.html"))

# ════════════ LORE SECTION (rendered from world.txt via worldtxt.py) ════════════
# Every section in world.txt becomes a linked wiki page, in the book's reading
# order. Culture demonyms are cross-linked; "slop —>" draft markers are stripped
# by the parser. Omitted entirely if world.txt isn't present.
LORE_PAGES = []  # (url, title) in reading order, for nav + prev/next
if WORLD_SECTIONS:
    def _wl_esc(s):
        # inline formatter for parsed lore text: escape, light **bold**/*em*,
        # then autolink (fresh seen per field, so tables link per-cell)
        return md_inline(str(s))
    def _emit_lore(url, title, body_html, search_text):
        # link the whole page body once (first-occurrence per page), suppressing
        # self-references to this page
        linked = autolink(body_html, url)
        open(_os.path.join(OUTDIR, url), "w", encoding="utf-8").write(page(title, linked, url))
        search_index.append({"title": title, "url": url, "text": search_text})

    # group sections by their destination page (a page may take >1 section, though
    # here it's 1:1) and render, preserving file order
    _page_titles = {  # url -> <h1> heading for that page
        "lore.html":          "The World of Vaelohk",
        "lore-map.html":      "The Map",
        "lore-cultures.html": "The Fifteen",
        "lore-ages.html":     "The Timeline",
        "lore-darkness.html": "The Age of Darkness",
    }
    _page_search = {
        "lore.html":          "lore world vaelohk premise draggath fracture peoples",
        "lore-map.html":      "map vaelohk sea corners centre regions places geography duke unclaimed",
        "lore-cultures.html": "cultures fifteen " + " ".join(WORLD_CULTURES),
        "lore-ages.html":     "timeline ages fracture plenty tetramorph doubt renown chronicle",
        "lore-darkness.html": "age of darkness old gods foundings draggath trusti clypso cailen",
    }
    _page_body = {}   # url -> list of html fragments
    _page_order = []  # urls in first-seen order
    for _title, _body in WORLD_SECTIONS:
        _url, _ = _lore_page_for(_title)
        if not _url:
            continue
        if _url not in _page_body:
            _page_body[_url] = []
            _page_order.append(_url)
            h1 = _page_titles.get(_url, _title.title())
            _page_body[_url].append(f"<h1>{html.escape(h1)}</h1>")
            # the Fifteen gets a count badge
            if _url == "lore-cultures.html" and WORLD_CULTURES:
                _page_body[_url][-1] = (f"<h1>The Fifteen "
                                        f"<span class='count'>{len(WORLD_CULTURES)}</span></h1>")
            # the Map page gets the world map image under its heading
            if _url == "lore-map.html" and MAP_IMG:
                _page_body[_url].append(
                    f"<figure class='lore-map'><img src='{MAP_IMG}' "
                    f"alt='Map of Vaelohk' loading='lazy'>"
                    f"<figcaption>The world of Vaelohk.</figcaption></figure>")
        _page_body[_url].append(_wt.render_section(_title, _body, esc=_wl_esc, slug=slug))

    # ── Gazetteer: index every named place that has text, linked to who holds it ──
    if WORLD_PLACES and "lore-map.html" in _page_body:
        u = "lore-map.html"
        terr = sorted((p for p in WORLD_PLACES if p["kind"] == "territory"), key=lambda p: p["name"])
        uncl = sorted((p for p in WORLD_PLACES if p["kind"] == "unclaimed"), key=lambda p: p["name"])
        rows = []
        for p in terr + uncl:
            pid = "geo-" + slug(p["name"])
            if p["owner"]:
                held = f"<a class='term' href='lore-cultures.html#{slug(p['owner'])}'>{html.escape(p['owner'])}</a>"
            else:
                held = "<span class='mut'>Unclaimed</span>"
            desc = md_inline(p["desc"]) if p["desc"] else ""
            rows.append(f"<tr id='{pid}'><td><strong>{html.escape(p['name'])}</strong></td>"
                        f"<td>{held}</td><td>{desc}</td></tr>")
        g = ["<h2 class='wl-group'>Gazetteer</h2>",
             "<p class='mut'>Named places with recorded lore, and who holds them. "
             "Seas are listed under The Sea above.</p>",
             "<table class='pursuits wl-gazetteer'><thead><tr><th>Place</th><th>Held by</th>"
             "<th>Description</th></tr></thead><tbody>", *rows, "</tbody></table>"]
        _page_body[u].append("".join(g))

    for _url in _page_order:
        _emit_lore(_url, _page_titles.get(_url, _url), "".join(_page_body[_url]),
                   _page_search.get(_url, "lore"))
        LORE_PAGES.append((_url, _page_titles.get(_url, _url)))


# ── CSS ──
open(os.path.join(OUTDIR,"wiki.css"),"w",encoding="utf-8").write("""
:root{--bg:#f7f6f3;--panel:#fff;--ink:#1d1d1d;--mut:#888;--line:#e2e0db;--accent:#5b2e8e;--link:#1F4E8C;--hover:#ece9e3;--chip:#eee4f7;--th:var(--th);--rowline:#efeee9;--rowhover:#fcfbff;--linkline:#aac;--shadow:rgba(0,0,0,.12)}
 :root[data-theme=dark]{--bg:#15141a;--panel:#201e28;--ink:#e8e6e1;--mut:#9c99a6;--line:#34313f;--accent:#c4a2f0;--link:#82b4ec;--hover:#2b2836;--chip:#342a48;--th:#272430;--rowline:#2c2936;--rowhover:#262330;--linkline:#566;--shadow:rgba(0,0,0,.5)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15.5px/1.6 Georgia,serif}
#q{position:fixed;top:0;left:0;right:0;z-index:30;width:100%;padding:11px 16px;border:0;border-bottom:1px solid var(--line);font:15px sans-serif;background:var(--panel)}
#results{position:fixed;top:43px;left:0;right:0;background:var(--panel);z-index:29;box-shadow:0 6px 18px var(--shadow);max-height:62vh;overflow:auto;display:none}
#results a{display:block;padding:9px 16px;border-bottom:1px solid var(--rowline);text-decoration:none;color:var(--ink);font:14px sans-serif}
#results a:hover,#results a.sel{background:var(--hover)}#results .t{font-weight:700;color:var(--accent)}#results .s{color:var(--mut);font-size:12.5px}
.wrap{display:flex;max-width:1180px;margin:54px auto 0}
nav{flex:0 0 215px;position:sticky;top:54px;height:calc(100vh - 54px);overflow:auto;padding:16px 12px;border-right:1px solid var(--line);font:13px sans-serif}
nav a{display:block;padding:3px 8px;color:var(--ink);text-decoration:none;border-radius:5px}nav a:hover{background:var(--hover)}nav a.active{background:var(--accent);color:var(--panel)}
.navhead{display:flex;align-items:center;justify-content:space-between;width:100%;font-weight:700;text-transform:uppercase;font-size:10.5px;letter-spacing:1px;color:var(--mut);margin:13px 0 4px;padding:2px 8px;background:none;border:0;cursor:pointer;font-family:sans-serif}
.navgroup:first-child .navhead{margin-top:0}
.navhead:hover{color:var(--ink)}
.navhead .chev{transition:transform .15s;font-size:14px;opacity:.7}
.navgroup:not(.collapsed) .chev{transform:rotate(90deg)}
.navgroup.collapsed .navlinks{display:none}
body.game-mode .navgroup:not([data-group=rules]):not([data-group=reference]){display:none}
html.game-pending .navgroup:not([data-group=rules]):not([data-group=reference]){display:none}
.topbtns{position:fixed;top:0;right:0;z-index:31;height:43px;display:flex;align-items:center;gap:3px;padding-right:8px}
.topbtns button{height:32px;min-width:34px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:7px;font-size:15px;cursor:pointer;line-height:1}
.topbtns button:hover{border-color:var(--accent)}
.topbtns button.on{background:var(--accent);color:var(--panel);border-color:var(--accent)}
#q{padding-right:92px}
main{flex:1;padding:8px 30px 80px;min-width:0}
h1{font-size:26px;margin:.2em 0 .6em;border-bottom:2px solid var(--accent);padding-bottom:.2em}
h1 .count,.count{font:13px sans-serif;background:var(--chip);color:var(--accent);padding:2px 9px;border-radius:11px;vertical-align:middle}
h2{font-size:19px;margin:1.2em 0 .4em}h3{font-size:16px;margin:1em 0 .3em;color:var(--ink)}p{margin:.5em 0}
a.term{color:var(--link);text-decoration:none;border-bottom:1px dotted var(--linkline)}a.term:hover{background:var(--hover)}
table.pursuits{border-collapse:collapse;width:100%;font:13px sans-serif;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}
table.pursuits th{background:var(--th);text-align:left;padding:7px 9px;font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:var(--mut)}
table.pursuits td{padding:7px 9px;border-top:1px solid var(--rowline);vertical-align:top}table.pursuits tr:hover td{background:var(--rowhover)}
td.nm{font-weight:700;white-space:nowrap;font-family:Georgia,serif}.dim{color:var(--mut)}
table.tacticmatrix{font-size:11.5px;display:block;overflow-x:auto}
table.tacticmatrix th{white-space:nowrap}
table.tacticmatrix tbody th{background:var(--th);font-family:Georgia,serif;text-transform:none;letter-spacing:0;font-size:12px;color:var(--ink);position:sticky;left:0}
table.tacticmatrix td{white-space:nowrap;font-size:11px}
.gate{color:var(--mut);font-size:12px}
ul.cols{columns:2;font:14px sans-serif;list-style:none;padding:0}ul.cols li{margin:3px 0;break-inside:avoid}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;margin-top:1em}
.card{display:flex;flex-direction:column;padding:16px;background:var(--panel);border:1px solid var(--line);border-radius:9px;text-decoration:none;color:var(--ink)}
.card:hover{border-color:var(--accent);box-shadow:0 3px 10px rgba(91,46,142,.1)}.card .ct{font-weight:700;font-size:16px}.card .cn{color:var(--mut);font-size:13px;font-family:sans-serif}
.chain{margin:.4em 0 1em}.chain ul{list-style:none;padding-left:18px;border-left:1px solid var(--line)}.chain>ul{border-left:0;padding-left:0}.chain li{margin:2px 0;font:14px sans-serif}
dl.gloss dt{font-weight:700;color:var(--accent);margin-top:.9em;font-size:16px}dl.gloss dd{margin:.15em 0 0}
a.usedin{color:var(--link);text-decoration:none;font-size:12px;font-style:italic;opacity:.75;white-space:nowrap}a.usedin:hover{opacity:1}
code{background:var(--rowline);padding:1px 5px;border-radius:4px;font-size:.9em}
.turnflow{max-width:620px}
.phase{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:8px;padding:12px 16px;margin:0}
.ph-head{font-weight:700;font-size:17px;font-family:Georgia,serif}
.ph-head a{color:var(--accent)!important;border:0!important}
.ph-desc{font-size:14px;margin:4px 0 0;font-family:sans-serif}
.ph-terms{margin-top:7px;font-size:12.5px;font-family:sans-serif}
.ph-terms a{margin-right:4px}
.arrow{text-align:center;color:var(--accent);font-size:20px;margin:6px 0;font-weight:700}
.arrow.loop{font-size:13px;color:var(--mut);font-family:sans-serif;margin-top:10px}
.pagefoot{margin-top:48px;border-top:1px solid var(--line);padding-top:16px;font-family:sans-serif}
.related{font-size:13px;margin-bottom:16px}
.related .rl{color:var(--mut);text-transform:uppercase;letter-spacing:.5px;font-size:11px;font-weight:700;margin-right:6px}
.related a{display:inline-block;margin:3px 6px 3px 0;padding:3px 10px;background:var(--chip);border-radius:12px;border:0!important}
.prevnext{display:flex;justify-content:space-between;gap:12px;font-size:14px}
.pn{padding:8px 14px;border:1px solid var(--line);border-radius:7px;text-decoration:none;color:var(--ink);max-width:46%;border-bottom:1px solid var(--line)!important}
.pn:hover{border-color:var(--accent);background:var(--hover)}
.pn.next{margin-left:auto;text-align:right}
.versionstamp{position:fixed;bottom:8px;right:12px;font-family:sans-serif;font-size:11px;color:var(--mut);opacity:.6;pointer-events:none}
/* lore (world.txt) */
h2.wl-group{margin-top:1.6em;text-transform:uppercase;letter-spacing:1px;font-size:15px;color:var(--accent);border-top:1px solid var(--line);padding-top:.8em}
h3.wl-culture{margin-top:1.4em;font-size:22px;color:var(--ink)}
.wl-type{font:12px sans-serif;color:var(--mut);text-transform:uppercase;letter-spacing:.6px;margin:-.2em 0 .6em}
h3.wl-sub{font-size:15px;color:var(--ink);text-transform:uppercase;letter-spacing:.5px;margin:1.2em 0 .3em}
h4.wl-label{font:11px sans-serif;text-transform:uppercase;letter-spacing:1px;color:var(--mut);margin:1em 0 .2em}
dl.wl-defs{margin:.3em 0 1em}dl.wl-defs dt{font-weight:700;font-family:Georgia,serif;color:var(--ink);margin-top:.5em}
dl.wl-defs dd{margin:.1em 0 0;color:var(--ink)}
table.wl-attrs{max-width:640px;margin:.4em 0 1em}
table.wl-table{max-width:560px}
table.kv{border-collapse:collapse;width:100%;font:13.5px sans-serif;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}
table.kv th{background:var(--th);text-align:left;padding:6px 10px;color:var(--mut);font-weight:700;white-space:nowrap;vertical-align:top;width:1%}
table.kv td{padding:6px 10px;border-top:1px solid var(--rowline);vertical-align:top}
figure.lore-map{margin:0 0 1.4em;text-align:center}
figure.lore-map img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:10px;box-shadow:0 2px 10px var(--shadow)}
figure.lore-map figcaption{font:12px sans-serif;color:var(--mut);margin-top:.5em;font-style:italic}
#navtoggle{display:none}
@media(max-width:760px){
  .wrap{flex-direction:column;margin-top:44px}
  #navtoggle{display:flex;align-items:center;justify-content:center;position:fixed;top:0;left:0;z-index:31;height:44px;width:50px;border:0;border-right:1px solid var(--line);background:var(--panel);font-size:20px;line-height:1;cursor:pointer;color:var(--ink)}
  #q{padding-left:58px}
  nav{position:static;height:auto;flex:none;border-right:0;border-bottom:1px solid var(--line);display:none}
  body.nav-open nav{display:block}
}
""")

# ── search.js ──
js="""const IDX=__IDX__;const q=document.getElementById('q'),box=document.getElementById('results');let sel=-1,cur=[];
q.addEventListener('input',()=>{const v=q.value.toLowerCase().trim();sel=-1;if(v.length<2){box.style.display='none';return;}
cur=IDX.map(d=>{const t=d.title.toLowerCase(),x=d.text.toLowerCase();let s=0;if(t===v)s=100;else if(t.startsWith(v))s=60;else if(t.includes(v))s=40;else if(x.includes(v))s=15;return{d,s};}).filter(o=>o.s>0).sort((a,b)=>b.s-a.s).slice(0,14);
if(!cur.length){box.innerHTML='<a><span class=s>No matches</span></a>';box.style.display='block';return;}
box.innerHTML=cur.map((o,i)=>`<a href="${o.d.url}" data-i="${i}"><span class="t">${o.d.title}</span> <span class="s">${o.d.text.slice(0,80).replace(/</g,'&lt;')}…</span></a>`).join('');box.style.display='block';});
q.addEventListener('keydown',e=>{const a=box.querySelectorAll('a');if(e.key==='ArrowDown')sel=Math.min(sel+1,a.length-1);else if(e.key==='ArrowUp')sel=Math.max(sel-1,0);else if(e.key==='Enter'&&cur.length){location.href=cur[Math.max(sel,0)].d.url;return;}else return;a.forEach((el,i)=>el.classList.toggle('sel',i===sel));e.preventDefault();});
document.addEventListener('click',e=>{if(e.target!==q)box.style.display='none';});"""
open(os.path.join(OUTDIR,"search.js"),"w",encoding="utf-8").write(js.replace("__IDX__",json.dumps(search_index)))

open(os.path.join(OUTDIR,"ui.js"),"w",encoding="utf-8").write(r"""
(function(){
  var root=document.documentElement, body=document.body;
  // ── theme toggle (head script already applied the stored/system theme) ──
  var tb=document.getElementById('theme');
  function setTheme(t){root.setAttribute('data-theme',t);try{localStorage.setItem('theme',t)}catch(e){}}
  if(tb)tb.addEventListener('click',function(){setTheme(root.getAttribute('data-theme')==='dark'?'light':'dark')});
  // ── game mode: rules + reference only ──
  var gm=document.getElementById('gamemode');
  function setGame(on){body.classList.toggle('game-mode',on);if(gm)gm.classList.toggle('on',on);root.classList.remove('game-pending');try{localStorage.setItem('gamemode',on?'1':'0')}catch(e){}}
  var gs=false;try{gs=localStorage.getItem('gamemode')==='1'}catch(e){}
  setGame(gs);
  if(gm)gm.addEventListener('click',function(){setGame(!body.classList.contains('game-mode'))});
  // ── collapsible nav groups (persisted); escalation collapsed by default ──
  var KEY='navcollapsed', collapsed;
  try{collapsed=JSON.parse(localStorage.getItem(KEY)||'null')}catch(e){collapsed=null}
  var first=(collapsed===null); if(first)collapsed=['escalation'];
  var groups=[].slice.call(document.querySelectorAll('.navgroup'));
  groups.forEach(function(g){ if(collapsed.indexOf(g.dataset.group)>=0)g.classList.add('collapsed'); });
  var act=document.querySelector('nav a.active');           // always reveal current group
  if(act){var ag=act.closest('.navgroup'); if(ag)ag.classList.remove('collapsed');}
  function persist(){var c=groups.filter(function(g){return g.classList.contains('collapsed')}).map(function(g){return g.dataset.group});try{localStorage.setItem(KEY,JSON.stringify(c))}catch(e){}}
  if(first)persist();
  groups.forEach(function(g){var h=g.querySelector('.navhead'); if(h)h.addEventListener('click',function(){g.classList.toggle('collapsed');persist();});});
})();
""")

# ════════════ POST-PROCESS: prev/next + related footers ════════════
import glob, collections

# reading order for prev/next = the rule section order (from RULES.md) + key pages
order = ["index.html", "turn-sequence.html"]
order += [f"rules-{slug(t)}.html" for t,_ in sections_live]
order += ["pursuits.html"] + [f"type-{slug(t)}.html" for t in TYPE_ORDER if t in by_type]
order += [f"domain-{slug(d)}.html" for d in DOMAINS]
order += [f"standing-{slug(t)}.html" for t in TIERS]
order += ["paths.html", "glossary.html"]
if FACTIONS: order.append("factions.html")
order += [uu for uu, _ in LORE_NAV]
order = [p for p in order if _os.path.exists(_os.path.join(OUTDIR, p))]

titles = {}  # url -> display title (pull from <title> or <h1>)
pagetext = {}  # url -> plaintext
pagelinks = {}  # url -> set of internal hrefs

for u in order:
    html_src = open(_os.path.join(OUTDIR, u), encoding="utf-8").read()
    mt = re.search(r"<h1[^>]*>(.*?)</h1>", html_src, re.S)
    if mt:
        # drop the count badge span, then strip tags
        h1 = re.sub(r"<span class='count'>.*?</span>", "", mt.group(1), flags=re.S)
        titles[u] = html.unescape(re.sub(r"<[^>]+>", "", h1)).strip()
    else:
        tt = re.search(r"<title>(.*?) \u2014 Renown</title>", html_src)
        titles[u] = html.unescape(tt.group(1)).strip() if tt else u
    body = re.search(r"<main>(.*?)</main>", html_src, re.S)
    bd = body.group(1) if body else ""
    pagetext[u] = re.sub(r"<[^>]+>", " ", bd)
    pagelinks[u] = set(re.findall(r"href='([a-z0-9\-]+\.html)", bd)) | set(re.findall(r'href="([a-z0-9\-]+\.html)', bd))

# term frequency across pages (for rarity weighting)
term_pages = collections.defaultdict(set)
present = {}
for u in order:
    txt = pagetext[u]
    found = set(t for t in TERMS if re.search(r"\b"+re.escape(t)+r"\b", txt))
    present[u] = found
    for t in found:
        term_pages[t].add(u)

def related_for(u):
    # score other pages by shared distinctive terms (rarer term = higher weight) + direct links
    scores = collections.Counter()
    for t in present[u]:
        npg = len(term_pages[t])
        if npg < 2 or npg > 18:  # skip ubiquitous or unique terms
            continue
        w = 1.0 / npg
        for other in term_pages[t]:
            if other != u:
                scores[other] += w
    # boost pages this page directly links to
    for lnk in pagelinks[u]:
        if lnk in titles and lnk != u:
            scores[lnk] += 0.5
    ranked = [p for p,_ in scores.most_common(6)]
    return ranked

for i, u in enumerate(order):
    prev_u = order[i-1] if i > 0 else None
    next_u = order[i+1] if i < len(order)-1 else None
    rel = related_for(u)
    foot = ['<div class="pagefoot">']
    if rel:
        chips = " ".join(f"<a class='term' href='{r}'>{html.escape(titles[r])}</a>" for r in rel)
        foot.append(f"<div class='related'><span class='rl'>Related:</span> {chips}</div>")
    nav_links = []
    if prev_u: nav_links.append(f"<a class='pn prev' href='{prev_u}'>\u2190 {html.escape(titles[prev_u])}</a>")
    if next_u: nav_links.append(f"<a class='pn next' href='{next_u}'>{html.escape(titles[next_u])} \u2192</a>")
    if nav_links:
        foot.append(f"<div class='prevnext'>{''.join(nav_links)}</div>")
    foot.append("</div>")
    footer_html = "".join(foot)
    _p = _os.path.join(OUTDIR, u)
    html_src = open(_p, encoding="utf-8").read()
    html_src = html_src.replace("</main>", footer_html + "</main>", 1)
    # Atomic write with retry: OneDrive can lock a file mid-rewrite and leave it
    # truncated to 0 bytes. Write to a temp file, then replace, retrying on lock.
    import time as _time
    for _attempt in range(5):
        try:
            _tmp = _p + ".tmp"
            with open(_tmp, "w", encoding="utf-8") as _fh:
                _fh.write(html_src)
                _fh.flush()
                _os.fsync(_fh.fileno())
            _os.replace(_tmp, _p)   # atomic on Windows
            break
        except (PermissionError, OSError):
            _time.sleep(0.3)
    else:
        # last resort: direct write
        with open(_p, "w", encoding="utf-8") as _fh:
            _fh.write(html_src)


# emit an empty .nojekyll so GitHub Pages serves files as-is (no Jekyll front-matter leak)
open(_os.path.join(OUTDIR, ".nojekyll"), "w").close()
print(f"wiki -> {OUTDIR}/index.html")
print(f"  {len(sections_live)} rule pages ({len(EMPTY_SECTIONS)} blank parents skipped) | {len([t for t in TYPE_ORDER if t in by_type])} type pages | "
      f"{len(DOMAINS)} domain + {len(TIERS)} standing views | paths | {len(rd.GLOSSARY)} glossary | {len(search_index)} search")