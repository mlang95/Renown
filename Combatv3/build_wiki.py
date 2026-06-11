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
import renown_data as rd

SRC = sys.argv[1] if len(sys.argv) > 1 else "RULES.md"
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "wiki"
os.makedirs(OUTDIR, exist_ok=True)

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

# ── linkable terms: pursuits link to their TYPE page (anchored), glossary to glossary ──
TERMS = {}
for name, d in rd.NODES.items():
    TERMS[name] = (f"type-{slug(d.get('type','other'))}.html", slug(name))
for term in rd.GLOSSARY:
    TERMS.setdefault(term, ("glossary.html", slug(term)))
FACTIONS = getattr(rd, "FACTIONS", {})
for f in FACTIONS:
    TERMS.setdefault(f, (f"faction-{slug(f)}.html", None))

TERM_LIST = sorted(TERMS, key=lambda t:-len(t))
TERM_RE = re.compile(r"\b(" + "|".join(re.escape(t) for t in TERM_LIST) + r")\b")
def autolink(text, current=None):
    def repl(m):
        term=m.group(1); url,anchor=TERMS[term]
        if url==current: return term
        href=url+(f"#{anchor}" if anchor else "")
        return f'<a class="term" href="{href}">{term}</a>'
    return TERM_RE.sub(repl, text)

# ── markdown inline + block ──
def md_inline(s):
    s=html.escape(s)
    s=re.sub(r"\*\*\*(.+?)\*\*\*",r"<strong><em>\1</em></strong>",s)
    s=re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",s)
    s=re.sub(r"\*(.+?)\*",r"<em>\1</em>",s)
    s=re.sub(r"`(.+?)`",r"<code>\1</code>",s)
    return s
def md_to_html(md,current=None):
    out,i,lines=[],0,md.split("\n"); inl=False
    while i<len(lines):
        ln=lines[i].rstrip()
        if not ln.strip():
            if inl: out.append("</ul>"); inl=False
            i+=1; continue
        m=re.match(r"^(#{1,6})\s+(.*)$",ln)
        if m:
            if inl: out.append("</ul>"); inl=False
            lvl=len(m.group(1)); out.append(f"<h{lvl} id='{slug(m.group(2))}'>{md_inline(m.group(2))}</h{lvl}>")
            i+=1; continue
        if re.match(r"^[-*]\s+",ln) or re.match(r"^\d+\.\s+",ln):
            if not inl: out.append("<ul>"); inl=True
            out.append("<li>"+md_inline(re.sub(r"^([-*]|\d+\.)\s+","",ln))+"</li>"); i+=1; continue
        if inl: out.append("</ul>"); inl=False
        out.append("<p>"+md_inline(ln)+"</p>"); i+=1
    if inl: out.append("</ul>")
    return autolink("\n".join(out),current)

# ── split RULES.md ──
raw=open(SRC,encoding="utf-8").read()
parts=re.split(r"(?m)^#{1,2}\s+",raw)
intro=parts[0]; sections=[]
for c in parts[1:]:
    nl=c.find("\n"); title=(c[:nl] if nl>=0 else c).strip()
    sections.append((title,"## "+title+"\n"+(c[nl+1:] if nl>=0 else "")))

# register rule-section titles + aliases as linkable terms (now that sections exist)
_section_slugs = {slug(t) for t,_ in sections}
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
# rebuild the matcher now that TERMS grew
TERM_LIST = sorted(TERMS, key=lambda t:-len(t))
TERM_RE = re.compile(r"\b(" + "|".join(re.escape(t) for t in TERM_LIST) + r")\b")

# ── nav ──
def nav(current=""):
    it=['<div class="navhead">Rules</div>']
    it.append(f"<a href='turn-sequence.html'{' class=active' if current=='turn-sequence.html' else ''}>★ Turn Sequence</a>")
    for t,_ in sections:
        u=f"rules-{slug(t)}.html"; it.append(f"<a href='{u}'{' class=active' if u==current else ''}>{html.escape(t)}</a>")
    it.append('<div class="navhead">Pursuits</div>')
    it.append(f"<a href='pursuits.html'{' class=active' if current=='pursuits.html' else ''}>Overview</a>")
    for t in TYPE_ORDER:
        u=f"type-{slug(t)}.html"; it.append(f"<a href='{u}'{' class=active' if u==current else ''}>{t}</a>")
    it.append('<div class="navhead">Views</div>')
    for d in DOMAINS:
        u=f"domain-{slug(d)}.html"; it.append(f"<a href='{u}'{' class=active' if u==current else ''}>{d}</a>")
    it.append(f"<a href='paths.html'{' class=active' if current=='paths.html' else ''}>Build Paths</a>")
    it.append('<div class="navhead">Reference</div>')
    for label,uu in [("Equipment","equipment-ref.html"),("Combat Keywords","keywords-ref.html"),
                     ("Infrastructure","infrastructure-ref.html"),("Wonders","wonders-ref.html"),
                     ("Settlements","settlements-ref.html"),("Eras","eras-ref.html"),
                     ("Public Order","public-order-ref.html"),("Domain Board","domain-board-ref.html"),
                     ("Seasons","seasons-ref.html"),("Reference Tables","reference-tables.html")]:
        it.append(f"<a href='{uu}'{' class=active' if current==uu else ''}>{label}</a>")
    it.append(f"<a href='glossary.html'{' class=active' if current=='glossary.html' else ''}>Glossary</a>")
    if FACTIONS: it.append(f"<a href='factions.html'{' class=active' if current=='factions.html' else ''}>Factions</a>")
    return "\n".join(it)

def page(title,body,current=""):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>{html.escape(title)} — Renown</title><link rel="stylesheet" href="wiki.css"></head><body>
<input id="q" placeholder="Search…" autocomplete="off"><div id="results"></div>
<div class="wrap"><nav>{nav(current)}</nav><main>{body}</main></div>
<script src="search.js"></script></body></html>"""

search_index=[]

# ── rule section pages ──
for t,body_md in sections:
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
     ["rules-seasons.html"], ["Income", "Public Order"]),
    ("2 · Council Phase", "Players resolve Council business; Council Envoys are sent and voted before Domain Envoys.",
     ["rules-council-phase.html"], ["Council Envoy", "Influence", "Abstain"]),
    ("3 · Envoy Phase", "Diplomacy Envoys first, then Domain Envoys. Send → Vote → Net Influence → Resolve.",
     ["rules-envoy-phase.html"], ["Envoy", "Influence", "Endorsed", "Condemned", "Diplomacy"]),
    ("4 · Battle Phase", "Skirmishes, Sieges, and Battles resolve. Roll off for Initiative; fight in Skirmishes.",
     ["rules-battle-phase.html","rules-siege-warfare.html"], ["Skirmish", "Initiative", "Battle", "Siege"]),
    ("5 · Rest Phase", "Cleanup → Season +1 → score Renown → spend 1 Domain Point → pass the Host.",
     ["rules-seasons.html"], ["Season", "Renown", "Domain Point", "Edict"]),
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
    rows=[[n, d.get("renown",""), d.get("armies",""), d.get("cities",""), d.get("influence_per_turn",""), d.get("envoys",""), d.get("unlocks","")] for n,d in items]
    body=f"<h1>Eras <span class='count'>{len(items)}</span></h1>"
    body+="<p>Shared-Renown thresholds raise everyone's Era, lifting army/city caps and influence.</p>"
    body+=_grid(["Era","Renown","Armies","Cities","Influence/Turn","Envoys","Unlocks"], rows, u)
    open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Eras",body,u))
    search_index.append({"title":"Eras","url":u,"text":"eras founding ascension eminence zenith renown army cap"})

# Public Order
if hasattr(rd, "PUBLIC_ORDER"):
    u="public-order-ref.html"
    rows=[[k, v[0], v[1]] for k,v in sorted(rd.PUBLIC_ORDER.items(), reverse=True)]
    body="<h1>Public Order Track</h1><p>From -5 to 7, adjusted each turn by Faith minus Doubt.</p>"
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
    rows=[]
    for dom in ["Industry","Prowess","Cunning","Piety"]:
        if dom in db:
            for tier in ["Rising","Established","Sovereign"]:
                rows.append([dom, tier, db[dom].get(tier,"")])
    body="<h1>Domain Board</h1><p>Empire-side standing effects unlocked by raising a Domain.</p>"
    body+=_grid(["Domain","Standing","Effect"], rows, u)
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
    eq.append(_grid(["Retinue","Cost","To-Hit","Endurance","Morale","Unbreakable"],
        [[n,d.get("cost"),f"{d.get('to_hit')}+",d.get("endurance"),f"{d.get('shaking')}+","Yes" if d.get("unbreakable") else "—"] for n,d in rd.RETINUES.items()], u))
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

# Bandits / Timers / Influence Gain reference
u="reference-tables.html"
rt=["<h1>Reference Tables</h1>"]
if hasattr(rd,"BANDITS"):
    rt.append("<h2>Bandits</h2>")
    rt.append(_grid(["Term","Rule"], [[k,v] for k,v in rd.BANDITS.items()], u))
if hasattr(rd,"TIMERS"):
    rt.append("<h2>Timers</h2>")
    rt.append(_grid(["Timer","Where","Tracks"], [[k, v.get("where",""), v.get("tracks","")] for k,v in rd.TIMERS.items()], u))
if hasattr(rd,"INFLUENCE_GAIN"):
    rt.append("<h2>Influence Gain</h2>")
    rt.append(_grid(["Source","Change","Notes"], [[k, v.get("change",""), v.get("notes","")] for k,v in rd.INFLUENCE_GAIN.items()], u))
if hasattr(rd,"TRADE_RULES"):
    tr=rd.TRADE_RULES
    rt.append("<h2>Trade Rules</h2>")
    rt.append(_kv_table([("Income per Craft", tr.get("income_per_craft","")),("Requirements", tr.get("requirements","")),("No trade in", tr.get("no_trade_season","")),("Tax collected in", tr.get("tax_season",""))]))
open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Reference Tables","".join(rt),u))
search_index.append({"title":"Reference Tables","url":u,"text":"bandits timers influence gain trade rules"})

# Combat Keywords (the keyword subset of glossary)
u="keywords-ref.html"
KW=[rd.STEADY,rd.UNWIELDY,rd.TWO_H,rd.SHATTER_ARMOR,rd.UNSTOPPABLE,rd.CLEAVE,rd.POISON,rd.NIMBLE,rd.DRILLED,rd.DESTROY_SHIELD,rd.BLUNDER,rd.ONE_SHOT,rd.DEFLECT,rd.IMMUNE_PANIC,rd.UNBREAKABLE,rd.PARRY,rd.RIPOSTE,rd.RECOVER,rd.SERRATED,rd.PLANISHING,rd.FATIGUE_TOKEN,rd.MINUS_1_TBH]
kw=["<h1>Combat Keywords</h1><dl class='gloss'>"]
for k in KW:
    if k in rd.GLOSSARY:
        kw.append(f"<dt id='{slug(k)}'>{html.escape(k)}</dt><dd>{autolink(md_inline(str(rd.GLOSSARY[k])),u)}</dd>")
kw.append("</dl>")
open(_os.path.join(OUTDIR,u),"w",encoding="utf-8").write(page("Combat Keywords","".join(kw),u))
search_index.append({"title":"Combat Keywords","url":u,"text":"keywords deadly cleave poison parry riposte"})

# ── glossary ──
gl=["<h1>Glossary</h1><dl class='gloss'>"]
for term in sorted(rd.GLOSSARY):
    gl.append(f"<dt id='{slug(term)}'>{html.escape(term)}</dt><dd>{autolink(md_inline(str(rd.GLOSSARY[term])),'glossary.html')}</dd>")
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

# ── CSS ──
open(os.path.join(OUTDIR,"wiki.css"),"w",encoding="utf-8").write("""
:root{--bg:#f7f6f3;--ink:#1d1d1d;--mut:#888;--line:#e2e0db;--accent:#5b2e8e;--link:#1F4E8C}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15.5px/1.6 Georgia,serif}
#q{position:fixed;top:0;left:0;right:0;z-index:30;width:100%;padding:11px 16px;border:0;border-bottom:1px solid var(--line);font:15px sans-serif;background:#fff}
#results{position:fixed;top:43px;left:0;right:0;background:#fff;z-index:29;box-shadow:0 6px 18px rgba(0,0,0,.1);max-height:62vh;overflow:auto;display:none}
#results a{display:block;padding:9px 16px;border-bottom:1px solid #f0efea;text-decoration:none;color:var(--ink);font:14px sans-serif}
#results a:hover,#results a.sel{background:#f3eefa}#results .t{font-weight:700;color:var(--accent)}#results .s{color:var(--mut);font-size:12.5px}
.wrap{display:flex;max-width:1180px;margin:54px auto 0}
nav{flex:0 0 215px;position:sticky;top:54px;height:calc(100vh - 54px);overflow:auto;padding:16px 12px;border-right:1px solid var(--line);font:13px sans-serif}
nav a{display:block;padding:3px 8px;color:var(--ink);text-decoration:none;border-radius:5px}nav a:hover{background:#ece9e3}nav a.active{background:var(--accent);color:#fff}
.navhead{font-weight:700;text-transform:uppercase;font-size:10.5px;letter-spacing:1px;color:var(--mut);margin:13px 0 4px;padding-left:8px}.navhead:first-child{margin-top:0}
main{flex:1;padding:8px 30px 80px;min-width:0}
h1{font-size:26px;margin:.2em 0 .6em;border-bottom:2px solid var(--accent);padding-bottom:.2em}
h1 .count,.count{font:13px sans-serif;background:#eee4f7;color:var(--accent);padding:2px 9px;border-radius:11px;vertical-align:middle}
h2{font-size:19px;margin:1.2em 0 .4em}h3{font-size:16px;margin:1em 0 .3em;color:#444}p{margin:.5em 0}
a.term{color:var(--link);text-decoration:none;border-bottom:1px dotted #aac}a.term:hover{background:#eef3fb}
table.pursuits{border-collapse:collapse;width:100%;font:13px sans-serif;background:#fff;border:1px solid var(--line);border-radius:8px;overflow:hidden}
table.pursuits th{background:#f1efe9;text-align:left;padding:7px 9px;font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:var(--mut)}
table.pursuits td{padding:7px 9px;border-top:1px solid #efeee9;vertical-align:top}table.pursuits tr:hover td{background:#fcfbff}
td.nm{font-weight:700;white-space:nowrap;font-family:Georgia,serif}.dim{color:#ccc}
.gate{color:var(--mut);font-size:12px}
ul.cols{columns:2;font:14px sans-serif;list-style:none;padding:0}ul.cols li{margin:3px 0;break-inside:avoid}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;margin-top:1em}
.card{display:flex;flex-direction:column;padding:16px;background:#fff;border:1px solid var(--line);border-radius:9px;text-decoration:none;color:var(--ink)}
.card:hover{border-color:var(--accent);box-shadow:0 3px 10px rgba(91,46,142,.1)}.card .ct{font-weight:700;font-size:16px}.card .cn{color:var(--mut);font-size:13px;font-family:sans-serif}
.chain{margin:.4em 0 1em}.chain ul{list-style:none;padding-left:18px;border-left:1px solid var(--line)}.chain>ul{border-left:0;padding-left:0}.chain li{margin:2px 0;font:14px sans-serif}
dl.gloss dt{font-weight:700;color:var(--accent);margin-top:.9em;font-size:16px}dl.gloss dd{margin:.15em 0 0}
code{background:#efeee9;padding:1px 5px;border-radius:4px;font-size:.9em}
.turnflow{max-width:620px}
.phase{background:#fff;border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:8px;padding:12px 16px;margin:0}
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
.related a{display:inline-block;margin:3px 6px 3px 0;padding:3px 10px;background:#eee4f7;border-radius:12px;border:0!important}
.prevnext{display:flex;justify-content:space-between;gap:12px;font-size:14px}
.pn{padding:8px 14px;border:1px solid var(--line);border-radius:7px;text-decoration:none;color:var(--ink);max-width:46%;border-bottom:1px solid var(--line)!important}
.pn:hover{border-color:var(--accent);background:#faf7fe}
.pn.next{margin-left:auto;text-align:right}
@media(max-width:760px){.wrap{flex-direction:column}nav{position:static;height:auto;flex:none;border-right:0;border-bottom:1px solid var(--line)}}
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

# ════════════ POST-PROCESS: prev/next + related footers ════════════
import glob, collections

# reading order for prev/next = the rule section order (from RULES.md) + key pages
order = ["index.html", "turn-sequence.html"]
order += [f"rules-{slug(t)}.html" for t,_ in sections]
order += ["pursuits.html"] + [f"type-{slug(t)}.html" for t in TYPE_ORDER if t in by_type]
order += [f"domain-{slug(d)}.html" for d in DOMAINS]
order += [f"standing-{slug(t)}.html" for t in TIERS]
order += ["paths.html", "glossary.html"]
if FACTIONS: order.append("factions.html")
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
print(f"  {len(sections)} rule pages | {len([t for t in TYPE_ORDER if t in by_type])} type pages | "
      f"{len(DOMAINS)} domain + {len(TIERS)} standing views | paths | {len(rd.GLOSSARY)} glossary | {len(search_index)} search")