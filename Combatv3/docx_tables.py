#!/usr/bin/env python3
"""docx_tables.py — generate Word table fragments (OOXML) from renown_data.

Each function returns the <w:tbl>...</w:tbl> XML for one data-shaped table, built
live from the single source of truth. build_docs.py injects these into authored
prose docs wherever a {{TABLE:name}} marker appears, so the prose stays hand-
written (now in RULES_reorganized.md) while every embedded data table regenerates
from canon.

Registry at the bottom maps marker name -> builder. Add a row there to expose a
new table to the docs.
"""
import sys
sys.path.insert(0, ".")
import renown_data as rd

FONT = "EB Garamond"
HEAD_FILL = "D5E8F0"

def _esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

SZ = "17"   # EB Garamond 8.5pt — table cells

import re as _re
USABLE_TWIPS = 10466   # A4 portrait, 0.5" margins -> 11906 - 720 - 720
CHAR_W   = 105         # ~twips per char, EB Garamond 8.5pt (generous, bold headers)
CELL_PAD = 180         # left+right cell margin (90+90)
SLACK    = 85

_BOLD = _re.compile(r"\*\*(.+?)\*\*")

def _cell(text, bold=False, w_dxa=1000):
    text = str(text)
    def run(t, b):
        return (f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
                f'{"<w:b/><w:bCs/>" if b else ""}<w:sz w:val="{SZ}"/><w:szCs w:val="{SZ}"/></w:rPr>'
                f'<w:t xml:space="preserve">{_esc(t)}</w:t></w:r>')
    runs, pos = "", 0
    for m in _BOLD.finditer(text):              # honor **bold** segments in the data
        if m.start() > pos:
            runs += run(text[pos:m.start()], bold)
        runs += run(m.group(1), True)
        pos = m.end()
    if pos < len(text):
        runs += run(text[pos:], bold)
    if not runs:
        runs = run("", bold)
    return (f'<w:tc><w:tcPr><w:tcW w:w="{w_dxa}" w:type="dxa"/></w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:before="0" w:after="0"/>'
            f'<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:sz w:val="{SZ}"/></w:rPr></w:pPr>'
            f'{runs}</w:p></w:tc>')

def _col_widths(headers, rows, cap_chars=34):
    """Absolute column widths (twips) summing to the usable page width.
    Each column is at least wide enough for its longest single word (so no word
    wraps mid-token), then leftover space is shared out to columns that hold the
    longest text (so multi-line cells stay short). Numeric/short columns collapse."""
    cols = list(zip(*([list(headers)] + [list(r) for r in rows]))) if rows else [(h,) for h in headers]
    mins, want = [], []
    for col in cols:
        cells = [str(c).replace("**", "") for c in col]
        lword = max((max((len(w) for w in _re.split(r"\s+", c) if w), default=1)) for c in cells)
        lcell = max(len(c) for c in cells)
        mins.append(lword * CHAR_W + CELL_PAD + SLACK)
        want.append(max(1, min(lcell, cap_chars) - lword))   # appetite for wrap room
    smin = sum(mins)
    if smin >= USABLE_TWIPS:                                  # too many columns: scale to fit
        scale = USABLE_TWIPS / smin
        w = [max(300, int(m * scale)) for m in mins]
    else:
        extra, sw = USABLE_TWIPS - smin, float(sum(want))
        w = [mins[i] + int(round(extra * want[i] / sw)) for i in range(len(mins))]
    w[-1] += USABLE_TWIPS - sum(w)                            # absorb rounding
    return w

def _table(headers, rows, widths=None):
    dxa = list(widths) if widths else _col_widths(headers, rows)
    bd = '<w:tblBorders>' + ''.join(
        f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        for e in ("top", "left", "bottom", "right", "insideH", "insideV")) + '</w:tblBorders>'
    cm = ('<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="90" w:type="dxa"/>'
          '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="90" w:type="dxa"/></w:tblCellMar>')
    look = '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
    tblpr = (f'<w:tblPr><w:tblW w:w="{USABLE_TWIPS}" w:type="dxa"/><w:jc w:val="center"/>{bd}'
             f'<w:tblLayout w:type="fixed"/>{cm}{look}</w:tblPr>')
    grid = '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{d}"/>' for d in dxa) + '</w:tblGrid>'
    head = '<w:tr><w:trPr><w:tblHeader/></w:trPr>' + ''.join(_cell(h, True, d) for h, d in zip(headers, dxa)) + '</w:tr>'
    body = ''.join('<w:tr>' + ''.join(_cell(c, False, d) for c, d in zip(r, dxa)) + '</w:tr>' for r in rows)
    return f'<w:tbl>{tblpr}{grid}{head}{body}</w:tbl>'

# ── table builders ──
def retinues():
    rows = [[n, f"{x['to_hit']}+", str(x['endurance']), f"{x['shaking']}+",
             "Unbreakable" if x.get("unbreakable") else "—"] for n, x in rd.RETINUES.items()]
    return _table(["Retinue", "To Strike", "Endurance", "Morale", "Keyword"], rows)

def settlements():
    # 9-col form matching the authored Rules table; sourced from SETTLEMENTS.
    rows = [[str(v["tier"]), n, v["sea_variant"] or "None", str(v["tax_income"]),
             str(v["muster_limit"]), str(v["build_time"]), str(v["wards"]),
             str(v["reach"]), v["notes"] or "—"]
            for n, v in rd.SETTLEMENTS.items()]
    return _table(["Tier", "Settlement", "Sea", "Tax", "Muster", "Build", "Wards", "Reach", "Notes"], rows)

def eras():
    rows = [[n, str(v["renown"]), str(v["armies"]), str(v["cities"]),
             f"+{v['influence_per_turn']}", str(v["innate_diplomacy_influence"]), v["unlocks"] or "—"]
            for n, v in rd.ERAS.items()]
    return _table(["Era", "Renown", "Armies", "Cities", "Infl/Turn", "Diplo Infl", "Unlocks"], rows)

def public_order():
    rows = [[str(k), name, eff] for k, (name, eff) in sorted(rd.PUBLIC_ORDER.items())]
    return _table(["PO", "State", "Effect"], rows)

def po_modifiers():
    rows = []
    for sign in ("faith", "doubt"):
        for src, cond in rd.PO_MODIFIERS.get(sign, {}).items():
            rows.append([f"{sign.title()} 1", src, cond])
    return _table(["Type", "Source", "Condition"], rows)

def domain_board():
    # Full authored shape: Untested..Sovereign per domain, then the two influence rows.
    # Combat standing effects (rd.STANDING_EFFECTS) are folded into the same cell —
    # they unlock from the domain board, so they aren't partitioned out.
    b = rd.DOMAIN_BOARD
    se = getattr(rd, "STANDING_EFFECTS", {})
    def cell(d, tier):
        base = (b[d].get(tier, "") or "").strip()
        cmb = se.get((d, tier))
        if cmb:
            base = (base + " " if base else "") + str(cmb).strip()
        return base
    rows = [[d, "—", cell(d, "Rising"), cell(d, "Established"), cell(d, "Sovereign")]
            for d in ["Industry", "Prowess", "Cunning", "Piety"]]
    order = ["Untested", "Rising", "Established", "Sovereign"]
    mi = b.get("max_influence_per_vote", {})
    inn = b.get("innate_influence_own_envoys", {})
    rows.append(["Max Influence Per Vote"] + [str(mi.get(t, "")) for t in order])
    rows.append(["Innate Influence on Own Envoys"] + [str(inn.get(t, "")) for t in order])
    return _table(["Domain", "Untested", "Rising (3)", "Established (6)", "Sovereign (10)"], rows)

def envoy_outcomes():
    DOM = ["Prowess", "Cunning", "Piety", "Industry", "Diplomacy"]
    rows = [[d,
             rd.ENVOY_OUTCOMES[d].get("condemned", ""),
             rd.ENVOY_OUTCOMES[d].get("failed", ""),
             rd.ENVOY_OUTCOMES[d].get("passed", ""),
             rd.ENVOY_OUTCOMES[d].get("endorsed", "")]
            for d in DOM if d in rd.ENVOY_OUTCOMES]
    return _table(["Domain", "Condemned", "Failed", "Passed", "Endorsed"], rows)

def net_influence():
    # Numbers come from canon; the result/effect wording is fixed rules text.
    t = rd.ENVOY_OUTCOME_THRESHOLDS
    rows = [
        [f"{t.get('Condemned')} or less", "Condemned", "Resolve that Domain's Condemn effect"],
        [f"{t.get('Failed')} or less",    "Failed",    "Gain Doubt 1"],
        [f"{t.get('Passed')}+",           "Passed",    "Perform the action's Pass effect"],
        [f"{t.get('Endorsed')}+",         "Endorsed",  "Also perform the Endorsed effect"],
    ]
    return _table(["Net Influence", "Result", "Effect"], rows)

def influence_gain():
    rows = [[k, d.get("change", ""), d.get("notes", "")] for k, d in rd.INFLUENCE_GAIN.items()]
    return _table(["Source", "Influence Change", "Notes"], rows)

def treaties():
    rows = [[n, d.get("signed_via", ""), d.get("era", ""), d.get("effect", "")]
            for n, d in rd.TREATIES.items()]
    return _table(["Treaty", "Signed Via", "Era", "Effect"], rows)

def bandit_growth():
    rows = [[k, str(v)] for k, v in rd.BANDIT_GROWTH_PER_ERA.items()]
    return _table(["Era", "Retinues Gained per Turn"], rows)

def edicts():
    rows = [[n, d.get("type", ""), d.get("requirement", "")] for n, d in rd.EDICTS.items()]
    return _table(["Edict", "Type", "Requirement"], rows)

def weapons():
    rows = [[n, x["tier"], str(x["ap"]), f"{x['init']:+d}", ", ".join(x["tags"]) or "—"]
            for n, x in rd.WEAPONS.items()]
    return _table(["Weapon", "Tier", "AP", "Init", "Keywords"], rows)

def armor():
    rows = [[n, x["tier"], f"{x['save']}+", ", ".join(x["tags"]) or "—"]
            for n, x in rd.ARMORS.items()]
    return _table(["Armor", "Tier", "Save", "Keywords"], rows)

def seasons():
    rows = [[s, v["name"], v["effect"]] for s, v in rd.SEASONS.items()]
    return _table(["Season", "Name", "Effect"], rows)

def ranged():
    rows = [[n, x["tier"], str(x["ap"]), f"{x['init']:+d}", ", ".join(x["tags"]) or "—"]
            for n, x in rd.RANGED.items()]
    return _table(["Ranged Weapon", "Tier", "AP", "Init", "Keywords"], rows)

def shields():
    rows = [[n or "None", x["tier"] or "—", f"+{x['save_bonus']}", f"{x['init']:+d}",
             ", ".join(x["tags"]) or "—"] for n, x in rd.SHIELDS.items()]
    return _table(["Shield", "Tier", "Save Bonus", "Init", "Keywords"], rows)

def infrastructure():
    rows = [[n, v.get("tier", ""), str(v.get("upkeep", "")), str(v.get("build_time", "")),
             v.get("requirement", ""), v.get("empire_bonus", "")]
            for n, v in rd.INFRASTRUCTURE.items()]
    return _table(["Infrastructure", "Tier", "Upkeep", "Build Time", "Requirement", "Empire Bonus"], rows)

def wonders():
    rows = [[n, str(v.get("upkeep", "")), str(v.get("build_time", "")),
             v.get("requirement", ""), v.get("empire_bonus", "")]
            for n, v in rd.WONDERS.items()]
    return _table(["Wonder", "Upkeep", "Build Time", "Requirement", "Empire Bonus"], rows)

def terrain():
    rows = [[t, v.get("Effect", ""), ", ".join(v.get("Raw Materials", [])) or "—"]
            for t, v in rd.TERRAIN.items()]
    return _table(["Terrain", "Effect", "Raw Materials"], rows)

def tactical_terrain():
    rows = [[t, v.get("identify", ""), v.get("effect", "")] for t, v in rd.TACTICAL_TERRAIN.items()]
    return _table(["Tactical Terrain", "Identify", "Effect"], rows)

def factions():
    rows = [[n, v.get("feel", ""), v.get("difficulty", ""), v.get("strength", ""), v.get("mechanic", "")]
            for n, v in rd.FACTIONS.items()]
    return _table(["Faction", "Feel", "Difficulty", "Strength", "Mechanic"], rows)

def timers():
    rows = [[n, ("—" if v.get("default") is None else str(v.get("default"))),
             v.get("where", ""), v.get("tracks", "")] for n, v in rd.TIMERS.items()]
    return _table(["Timer", "Default", "Where", "Tracks"], rows)

def build_timers():
    rows = []
    for k, v in rd.BUILD_TIMERS.items():
        if isinstance(v, dict):
            for sub, sv in v.items():
                rows.append([f"{k} ({sub})", str(sv)])
        else:
            rows.append([k, str(v)])
    return _table(["Build", "Turns"], rows)

REGISTRY = {
    "retinues": retinues, "settlements": settlements, "eras": eras,
    "public_order": public_order, "po_modifiers": po_modifiers,
    "domain_board": domain_board, "envoy_outcomes": envoy_outcomes,
    "net_influence": net_influence, "influence_gain": influence_gain,
    "treaties": treaties, "bandit_growth": bandit_growth, "edicts": edicts,
    "weapons": weapons, "armor": armor, "seasons": seasons,
    "ranged": ranged, "shields": shields, "infrastructure": infrastructure,
    "wonders": wonders, "terrain": terrain, "tactical_terrain": tactical_terrain,
    "factions": factions, "timers": timers, "build_timers": build_timers,
}

# ── {{ACTIONS:Domain}} — render every ACTIONS entry of a domain as prose ──
# Mirrors the authored "## <Domain> Actions" layout so the action text stops
# living in two places. Returns a run of <w:p> paragraphs (not a table).
def _p(runs_xml, before=0, after=40, ind=0, keep_next=False):
    pind = f'<w:ind w:left="{ind}" w:hanging="{ind}"/>' if ind else ''
    keep = ("<w:keepNext/>" if keep_next else "") + "<w:keepLines/>"
    return (f'<w:p><w:pPr>{keep}<w:spacing w:before="{before}" w:after="{after}"/>{pind}'
            f'<w:rPr>{_FONT_RPR}</w:rPr></w:pPr>{runs_xml}</w:p>')

def _run(text, bold=False, ital=False):
    style = ("<w:b/><w:bCs/>" if bold else "") + ("<w:i/><w:iCs/>" if ital else "")
    return (f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/>{style}'
            f'<w:sz w:val="20"/></w:rPr><w:t xml:space="preserve">{_esc(text)}</w:t></w:r>')

def _bullet(runs_xml, after=20, keep_next=False):
    keep = ("<w:keepNext/>" if keep_next else "") + "<w:keepLines/>"
    return ('<w:p><w:pPr><w:pStyle w:val="ListBullet"/>'
            f'{keep}<w:spacing w:before="0" w:after="{after}"/>'
            '<w:ind w:left="360" w:hanging="180"/>'
            f'<w:rPr>{_FONT_RPR}</w:rPr></w:pPr>{runs_xml}</w:p>')

def _action_block(name, a):
    # Emit the block's paragraphs with keep_next set on every paragraph except the
    # final one, so an action never splits across a column or page break.
    end = a.get("endorsed", "")
    notes = a.get("notes", [])
    cost = a.get("cost", "None")
    req = a.get("requires", "")
    meta = _run("Cost: ", bold=True) + _run(cost)
    if req:
        meta += _run("      Requires: ", bold=True) + _run(req)
    out = []
    out.append(_p(_run(name, bold=True), before=120, after=20, keep_next=True))
    out.append(_p(meta, after=20, keep_next=True))
    last_is_effect = not end and not notes
    out.append(_p(_run("Effect: ", bold=True) + _run(a.get("effect", "")),
                  after=20, keep_next=not last_is_effect))
    if end:
        out.append(_p(_run("Endorsed: ", bold=True) + _run(end),
                      after=20, keep_next=bool(notes)))
    for j, note in enumerate(notes):
        out.append(_bullet(_run(note), keep_next=(j < len(notes) - 1)))
    return "".join(out)

def actions(domain):
    items = [(n, a) for n, a in rd.ACTIONS.items() if a.get("domain") == domain]
    out = []
    for i, (n, a) in enumerate(items, 1):
        # prepend the ordinal into the bolded title
        block = _action_block(f"{i}. {n}", a)
        out.append(block)
    return "".join(out)

# ── {{VAL:dotted.path}} — resolve one scalar out of renown_data ──
# Path syntax: NAME or NAME.key or NAME.key.subkey. dict keys and (rarely) list
# indices both work. Returns str(value); raises on a bad path so build fails loud.
def value(path):
    parts = path.split(".")
    cur = getattr(rd, parts[0])
    for p in parts[1:]:
        if isinstance(cur, dict):
            cur = cur[p]
        elif isinstance(cur, (list, tuple)):
            cur = cur[int(p)]
        else:
            raise KeyError(f"VAL path '{path}': cannot index {type(cur).__name__} with '{p}'")
    return str(cur)

# ── {{LIST:NAME}} — render a renown_data list of strings as bullets ──
def list_block(name):
    seq = getattr(rd, name)
    if not isinstance(seq, (list, tuple)):
        raise KeyError(f"LIST '{name}' is not a list/tuple")
    return "".join(
        f'<w:p><w:pPr><w:pStyle w:val="ListBullet"/><w:rPr>{_FONT_RPR}</w:rPr></w:pPr>'
        f'{_run(str(item))}</w:p>' for item in seq)

def get(name):
    if name not in REGISTRY:
        raise KeyError(f"no table '{name}'. available: {sorted(REGISTRY)}")
    return REGISTRY[name]()

# ── glossary access (for {{DEF:term}} and {{GLOSSARY}} markers) ──
def _gloss_lookup():
    """Return {lower_term: (display_term, definition)} from renown_data.GLOSSARY,
    resolving constant-keyed entries to their string form."""
    out = {}
    for k, v in rd.GLOSSARY.items():
        term = str(k)
        out[term.lower()] = (term, v)
    return out

def definition(term):
    """The definition string for a term (case-insensitive); '' if unknown."""
    g = _gloss_lookup()
    hit = g.get(term.lower())
    return hit[1] if hit else ""

def glossary_block():
    """The full glossary as an alphabetized definition list (term bold, def after)."""
    g = rd.GLOSSARY
    items = sorted(((str(k), v) for k, v in g.items()), key=lambda x: x[0].lower())
    paras = []
    for term, d in items:
        paras.append(
            f'<w:p><w:pPr><w:spacing w:after="40"/><w:rPr>{_FONT_RPR}</w:rPr></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:b/><w:bCs/><w:sz w:val="17"/></w:rPr>'
            f'<w:t xml:space="preserve">{_esc(term)} — </w:t></w:r>'
            f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:sz w:val="17"/></w:rPr>'
            f'<w:t xml:space="preserve">{_esc(d)}</w:t></w:r></w:p>')
    return "".join(paras)

_FONT_RPR = f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:sz w:val="17"/>'

if __name__ == "__main__":
    print("Available {{TABLE:name}} markers:", ", ".join(sorted(REGISTRY)))
