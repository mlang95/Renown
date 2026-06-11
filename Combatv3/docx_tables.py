#!/usr/bin/env python3
"""docx_tables.py — generate Word table fragments (OOXML) from renown_data.

Each function returns the <w:tbl>...</w:tbl> XML for one data-shaped table, built
live from the single source of truth. build_docs.py injects these into authored
prose docs wherever a {{TABLE:name}} marker appears, so the prose stays hand-
written while every embedded data table regenerates from canon.

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

SZ = "17"   # EB Garamond 8.5pt — unified dense table style (matches Compendium)

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
    cm = ('<w:tblCellMar><w:top w:w="14" w:type="dxa"/><w:left w:w="40" w:type="dxa"/>'
          '<w:bottom w:w="14" w:type="dxa"/><w:right w:w="40" w:type="dxa"/></w:tblCellMar>')
    tblpr = (f'<w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:jc w:val="center"/>{bd}'
             f'<w:tblLayout w:type="fixed"/>{cm}</w:tblPr>')
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
    rows = [[n, str(v["tier"]), str(v["tax_income"]), str(v["muster_limit"]),
             str(v["wards"]), str(v["build_time"]), str(v["reach"])]
            for n, v in rd.SETTLEMENTS.items()]
    return _table(["Settlement", "Tier", "Tax (Winter)", "Muster", "Wards", "Build", "Reach"], rows)

def eras():
    rows = [[n, str(v["renown"]), str(v["armies"]), str(v["cities"]),
             f"+{v['influence_per_turn']}", str(v["innate_diplomacy_influence"]), v["unlocks"] or "—"]
            for n, v in rd.ERAS.items()]
    return _table(["Era", "Renown", "Armies", "Cities", "Infl/Turn", "Diplo Infl", "Unlocks"], rows)

def public_order():
    rows = [[str(k), name, eff] for k, (name, eff) in sorted(rd.PUBLIC_ORDER.items())]
    return _table(["PO", "State", "Effect"], rows)

def domain_board():
    b = rd.DOMAIN_BOARD
    rows = [[d, b[d].get("Rising", ""), b[d].get("Established", ""), b[d].get("Sovereign", "")]
            for d in ["Industry", "Prowess", "Cunning", "Piety"]]
    return _table(["Domain", "Rising (3)", "Established (6)", "Sovereign (10)"], rows)

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
    "public_order": public_order, "domain_board": domain_board,
    "weapons": weapons, "armor": armor, "seasons": seasons,
}

def get(name):
    if name not in REGISTRY:
        raise KeyError(f"no table '{name}'. available: {sorted(REGISTRY)}")
    return REGISTRY[name]()

if __name__ == "__main__":
    print("Available {{TABLE:name}} markers:", ", ".join(sorted(REGISTRY)))

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
