#!/usr/bin/env python3
"""wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline
(RULES_reorganized_*.md) into HTML, so build_wiki.py can consume that same file.

Tables are rebuilt from renown_data, mirroring the column shapes in docx_tables.py,
so the wiki and the printed rulebook stay in sync from the one source of truth.

Integration (build_wiki.py), three edits:
    import wiki_markers as wm
    # first line of md_to_html(md,current=None):
    md = wm.preprocess_inline(md)
    # inside the while loop, just after the heading branch:
    _bh = wm.block_html(ln)
    if _bh is not None:
        close_all(); out.append(_bh); i += 1; continue

Cells are only escaped + **bold**/*em* here (no autolinking): build_wiki's own final
autolink pass runs over the injected HTML and links terms exactly once.
"""
import re, html
import renown_data as rd

VERSION = str(getattr(rd, "VERSION", ""))

# ── inline: {{VAL:dotted.path}} and {{VERSION}} ──
VAL_RE = re.compile(r"\{\{VAL:([^}]+)\}\}")
VERSION_RE = re.compile(r"\{\{VERSION\}\}")

def _resolve_val(path):
    cur = rd
    for i, seg in enumerate(path.split(".")):
        seg = seg.strip()
        if i == 0:
            cur = getattr(rd, seg, None)
        elif hasattr(cur, "get"):
            cur = cur.get(seg)
        else:
            try:
                cur = cur[seg]
            except Exception:
                cur = None
        if cur is None:
            return "?"
    return str(cur)

def preprocess_inline(md):
    md = VERSION_RE.sub(VERSION, md)
    return VAL_RE.sub(lambda m: _resolve_val(m.group(1)), md)

# ── tiny inline formatter (escape + bold/italic/code); NO autolink ──
def _inline(s):
    s = html.escape(str(s))
    s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s

def _htable(headers, rows):
    th = "".join(f"<th>{_inline(h)}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table class='pursuits'><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"

def _ul(items):
    return "<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ul>"

# ── {{TABLE:name}} renderers — mirror docx_tables.py shapes ──
def _t_public_order():
    rows = [[str(k), n, e] for k, (n, e) in sorted(rd.PUBLIC_ORDER.items())]
    return _htable(["PO", "State", "Effect"], rows)

def _t_po_modifiers():
    rows = []
    for sign in ("faith", "doubt"):
        for src, cond in rd.PO_MODIFIERS.get(sign, {}).items():
            rows.append([f"{sign.title()} 1", src, cond])
    return _htable(["Type", "Source", "Condition"], rows)

def _t_domain_board():
    b = rd.DOMAIN_BOARD
    order = ["Untested", "Rising", "Established", "Sovereign"]
    rows = [[d, "\u2014", b[d].get("Rising", ""), b[d].get("Established", ""), b[d].get("Sovereign", "")]
            for d in ["Industry", "Prowess", "Cunning", "Piety"]]
    mi = b.get("max_influence_per_vote", {}); inn = b.get("innate_influence_own_envoys", {})
    rows.append(["Max Influence Per Vote"] + [str(mi.get(t, "")) for t in order])
    rows.append(["Innate Influence on Own Envoys"] + [str(inn.get(t, "")) for t in order])
    return _htable(["Domain", "Untested", "Rising (3)", "Established (6)", "Sovereign (10)"], rows)

def _t_net_influence():
    t = rd.ENVOY_OUTCOME_THRESHOLDS
    rows = [
        [f"{t.get('Condemned')} or less", "Condemned", "Resolve that Domain's Condemn effect"],
        [f"{t.get('Failed')} or less",    "Failed",    "Gain Doubt 1"],
        [f"{t.get('Passed')}+",           "Passed",    "Perform the action's Pass effect"],
        [f"{t.get('Endorsed')}+",         "Endorsed",  "Also perform the Endorsed effect"],
    ]
    return _htable(["Net Influence", "Result", "Effect"], rows)

def _t_influence_gain():
    return _htable(["Source", "Influence Change", "Notes"],
                   [[k, d.get("change", ""), d.get("notes", "")] for k, d in rd.INFLUENCE_GAIN.items()])

def _t_bandit_growth():
    return _htable(["Era", "Retinues Gained per Turn"],
                   [[k, str(v)] for k, v in rd.BANDIT_GROWTH_PER_ERA.items()])

def _t_treaties():
    return _htable(["Treaty", "Signed Via", "Era", "Effect"],
                   [[n, d.get("signed_via", ""), d.get("era", ""), d.get("effect", "")] for n, d in rd.TREATIES.items()])

def _t_edicts():
    return _htable(["Edict", "Type", "Requirement"],
                   [[n, d.get("type", ""), d.get("requirement", "")] for n, d in rd.EDICTS.items()])

def _t_seasons():
    return _htable(["Season", "Name", "Effect"],
                   [[k, v.get("name", ""), v.get("effect", "")] for k, v in rd.SEASONS.items()])

def _t_eras():
    items = sorted(rd.ERAS.items(), key=lambda kv: kv[1].get("renown", 0))
    return _htable(["Era", "Renown", "Armies", "Cities", "Influence/Turn", "Envoys", "Unlocks"],
                   [[n, d.get("renown", ""), d.get("armies", ""), d.get("cities", ""),
                     d.get("influence_per_turn", ""), d.get("envoys", ""), d.get("unlocks", "")] for n, d in items])

def _t_settlements():
    items = sorted(rd.SETTLEMENTS.items(), key=lambda kv: kv[1].get("tier", 0))
    return _htable(["Settlement", "Tax", "Muster", "Wards", "Reach", "Build", "Sea Variant", "Notes"],
                   [[n, d.get("tax_income", ""), d.get("muster_limit", ""), d.get("wards", ""),
                     d.get("reach", ""), d.get("build_time", ""), d.get("sea_variant") or "\u2014",
                     d.get("notes", "")] for n, d in items])

def _t_terrain():
    return _htable(["Terrain", "Effect", "Raw Materials"],
                   [[t, d.get("Effect", "") or "\u2014", ", ".join(d.get("Raw Materials", [])) or "\u2014"]
                    for t, d in rd.TERRAIN.items()])

def _t_infrastructure():
    TIER_ORD = {"Primitive": 0, "Developed": 1, "Sophisticated": 2}
    items = sorted(rd.INFRASTRUCTURE.items(), key=lambda kv: (TIER_ORD.get(kv[1].get("tier"), 9), kv[0]))
    return _htable(["Build", "Tier", "Upkeep", "Build Time", "Requirement", "Effect"],
                   [[n, d.get("tier", ""), d.get("upkeep", ""), d.get("build_time", ""),
                     d.get("requirement", ""), d.get("empire_bonus", "")] for n, d in items])

def _t_wonders():
    return _htable(["Wonder", "Build Time", "Upkeep", "Effect"],
                   [[n, d.get("build_time", ""), d.get("upkeep", ""), d.get("empire_bonus", "")]
                    for n, d in rd.WONDERS.items()])

TABLE_RENDER = {
    "public_order": _t_public_order, "po_modifiers": _t_po_modifiers, "domain_board": _t_domain_board,
    "net_influence": _t_net_influence, "influence_gain": _t_influence_gain, "bandit_growth": _t_bandit_growth,
    "treaties": _t_treaties, "edicts": _t_edicts, "seasons": _t_seasons, "eras": _t_eras,
    "settlements": _t_settlements, "terrain": _t_terrain, "infrastructure": _t_infrastructure,
    "wonders": _t_wonders,
}

def _render_actions(domain):
    rows = []
    for n, a in rd.ACTIONS.items():
        if a.get("domain") != domain:
            continue
        notes = a.get("notes", [])
        eff = a.get("effect", "")
        if notes:
            eff = eff + " \u2014 " + "; ".join(notes)
        rows.append([n, a.get("cost", "") or "\u2014", a.get("requires", "") or "\u2014",
                     eff, a.get("endorsed", "") or "\u2014"])
    return _htable(["Action", "Cost", "Requires", "Effect (if passes)", "Endorsed"], rows)

_LIST_SRC = {"ALLIANCE_RULES": lambda: getattr(rd, "ALLIANCE_RULES", [])}

BLOCK_MK = re.compile(r"^\s*\{\{(TABLE|ACTIONS|LIST|COLS):([^}]+)\}\}\s*$")

def block_html(line):
    """Return HTML for a block-marker line, "" for COLS (print-only), or None if
    the line isn't a block marker."""
    m = BLOCK_MK.match(line)
    if not m:
        return None
    kind, arg = m.group(1), m.group(2).strip()
    if kind == "COLS":
        return ""                       # column breaks are a print concern; drop
    if kind == "TABLE":
        r = TABLE_RENDER.get(arg)
        return r() if r else f"<p><em>[unknown table: {html.escape(arg)}]</em></p>"
    if kind == "ACTIONS":
        return _render_actions(arg)
    if kind == "LIST":
        src = _LIST_SRC.get(arg)
        return _ul(src()) if src else f"<p><em>[unknown list: {html.escape(arg)}]</em></p>"
    return None


if __name__ == "__main__":
    # self-test: resolve every marker in the given rules file
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "RULES_reorganized_5.md"
    text = open(src, encoding="utf-8").read()
    text = preprocess_inline(text)
    leftover_val = VAL_RE.findall(text) + VERSION_RE.findall(text)
    print("unresolved inline markers:", leftover_val or "none")
    blocks = re.findall(r"^\s*\{\{(?:TABLE|ACTIONS|LIST|COLS):[^}]+\}\}\s*$", text, re.M)
    ok = 0
    for ln in blocks:
        h = block_html(ln)
        tag = "COLS(drop)" if h == "" else ("OK" if h and "unknown" not in h else "FAIL")
        if "unknown" in (h or ""):
            print("  ", ln.strip(), "->", tag, h)
        ok += 1
    print(f"block markers rendered: {ok}")
