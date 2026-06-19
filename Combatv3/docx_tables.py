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

def _cell(text, bold=False, pct=2000):
    shade = ""
    rpr = f'<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>{"<w:b/><w:bCs/>" if bold else ""}<w:sz w:val="{SZ}"/><w:szCs w:val="{SZ}"/></w:rPr>'
    return (f'<w:tc><w:tcPr><w:tcW w:w="{pct}" w:type="pct"/>{shade}</w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:before="0" w:after="0"/>'
            f'<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:sz w:val="{SZ}"/></w:rPr></w:pPr>'
            f'<w:r>{rpr}<w:t xml:space="preserve">{_esc(text)}</w:t></w:r></w:p></w:tc>')

def _table(headers, rows, total_w=None):
    n = len(headers)
    pct = 5000 // n
    bd = '<w:tblBorders>' + ''.join(
        f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        for e in ("top", "left", "bottom", "right", "insideH", "insideV")) + '</w:tblBorders>'
    cm = ('<w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
          '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar>')
    look = '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
    tblpr = (f'<w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:jc w:val="center"/>{bd}'
             f'<w:tblLayout w:type="fixed"/>{cm}{look}</w:tblPr>')
    grid = '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{9360//n}"/>' for _ in range(n)) + '</w:tblGrid>'
    head = '<w:tr><w:trPr><w:tblHeader/></w:trPr>' + ''.join(_cell(h, True, pct) for h in headers) + '</w:tr>'
    body = ''.join('<w:tr>' + ''.join(_cell(c, False, pct) for c in r) + '</w:tr>' for r in rows)
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
    return _table(["Tier", "Settlement", "Sea Variant", "Tax Income",
                   "Muster Limit/Turn", "Build Time", "Settlement Wards", "Reach", "Notes"], rows)

def eras():
    rows = [[n, str(v["renown"]), str(v["armies"]), str(v["cities"]),
             f"+{v['influence_per_turn']}", str(v["innate_diplomacy_influence"]), v["unlocks"] or "—"]
            for n, v in rd.ERAS.items()]
    return _table(["Era", "Renown", "Armies", "Cities", "Infl/Turn", "Diplo Infl", "Unlocks"], rows)

def public_order():
    rows = [[str(k), name, eff] for k, (name, eff) in sorted(rd.PUBLIC_ORDER.items(), reverse=True)]
    return _table(["PO", "State", "Effect"], rows)

def po_modifiers():
    rows = []
    for sign in ("faith", "doubt"):
        for src, cond in rd.PO_MODIFIERS.get(sign, {}).items():
            rows.append([sign.title(), src, cond])
    return _table(["Type", "Source", "Condition"], rows)

def domain_board():
    # Full authored shape: Untested..Sovereign per domain, then the two influence rows.
    b = rd.DOMAIN_BOARD
    rows = [[d, "—", b[d].get("Rising", ""), b[d].get("Established", ""), b[d].get("Sovereign", "")]
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

REGISTRY = {
    "retinues": retinues, "settlements": settlements, "eras": eras,
    "public_order": public_order, "po_modifiers": po_modifiers,
    "domain_board": domain_board, "envoy_outcomes": envoy_outcomes,
    "net_influence": net_influence, "influence_gain": influence_gain,
    "treaties": treaties, "bandit_growth": bandit_growth, "edicts": edicts,
    "weapons": weapons, "armor": armor, "seasons": seasons,
}

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
