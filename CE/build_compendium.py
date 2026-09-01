#!/usr/bin/env python3
"""build_compendium.py — render the Compendium .docx from compendium_data.json,
a pure-Python replacement for build_compendium.js (no Node required).

Matches the authored doc's look: landscape, 0.5" margins, EB Garamond, tight
bordered tables, **bold** markup parsed into runs.

Usage:  python build_compendium.py compendium_data.json Compendium.docx
"""
import json, re, sys, os
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import renown_data as rd
except Exception as e:
    sys.stderr.write(f"WARN: renown_data not importable ({e}); Speed/Max Settlements/Terrain/Bandit tables will be limited\n")
    rd = None
from docx import Document
from docx.shared import Pt, RGBColor, Twips
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "EB Garamond"
BODY = 8.5          # pt
HEAD_FILL = "EFEFEF"

def _set_cell_border(cell, color="auto", sz=4):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(sz))
        e.set(qn("w:space"), "0"); e.set(qn("w:color"), color)
        borders.append(e)
    tcPr.append(borders)

def _shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

def _rich(paragraph, text, bold=False, italic=False, size=BODY):
    """Parse **bold** markup into runs on an existing paragraph."""
    text = str(text)
    parts = [p for p in re.split(r"(\*\*[^*]+\*\*)", text) if p != ""]
    if not parts:
        parts = [text]
    for p in parts:
        m = re.match(r"^\*\*([^*]+)\*\*$", p)
        r = paragraph.add_run(m.group(1) if m else p)
        r.font.name = FONT; r.font.size = Pt(size)
        r.bold = True if m else bold
        r.italic = italic

def _cell_para(cell):
    para = cell.paragraphs[0]
    pf = para.paragraph_format
    pf.space_before = Pt(0); pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    return para


def _content_weights(headers, rows, floor=6, cap=60):
    w=[]
    for i in range(len(headers)):
        ht=re.sub(r"\*\*","",str(headers[i]))
        hword=max([len(x) for x in ht.split()] or [floor])
        m=max(len(ht),hword)
        for r in rows:
            if i<len(r) and r[i] is not None:
                m=max(m,len(re.sub(r"\*\*","",str(r[i]))))
        w.append(min(cap,max(floor,hword,m)))
    return w

def _alpha(rows, col=0):
    return sorted(rows, key=lambda r: re.sub(r"\*\*","",str(r[col] or "")).lower())

from reportlab.pdfbase.pdfmetrics import stringWidth as _sw
from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TTF
_MEAS_RF, _MEAS_BF = "Helvetica", "Helvetica-Bold"
for _dir in (os.path.dirname(os.path.abspath(__file__)),
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"), "fonts", "."):
    try:
        _pm.registerFont(_TTF("EBG", os.path.join(_dir, "EBGaramond-Regular.ttf")))
        _pm.registerFont(_TTF("EBGB", os.path.join(_dir, "EBGaramond-Bold.ttf")))
        _MEAS_RF, _MEAS_BF = "EBG", "EBGB"
        break
    except Exception:
        continue

def _col_layout(headers, rows, total_in=10.0, cap=48, tight=None):
    """Width columns to minimize wrapping, measured in the ACTUAL font. Each column
    prefers its NATURAL width (longest full string on one line). If all fit, keep
    compact. If not, only the widest columns shrink (water-filling from each
    column's single-word floor); short columns keep natural and never wrap."""
    tight = tight or set()
    FS = 8.5; PAD = 0.19   # Word default cell margins (0.08in x2 = 0.16) + safety
    RF, BF = _MEAS_RF, _MEAS_BF
    def w_full(s, bold): return _sw(re.sub(r"\*\*","",s), BF if bold else RF, FS)/72.0 + PAD
    def w_word(s, bold):
        ws = re.sub(r"\*\*","",s).split()
        return (max((_sw(w, BF if bold else RF, FS) for w in ws), default=0))/72.0 + PAD
    n = len(headers)
    nat_in = [0.0]*n; word_in = [0.0]*n
    for i in range(n):
        h = str(headers[i])
        cells = [str(r[i]) for r in rows if i < len(r) and r[i] is not None]
        nat_in[i]  = max([w_full(h, True)] + [w_full(c, False) for c in cells])
        word_in[i] = max([w_word(h, True)] + [w_word(c, False) for c in cells])
    width = [None]*n
    for i in tight: width[i] = nat_in[i]
    fixed = sum(width[i] for i in tight)
    free = [i for i in range(n) if i not in tight]
    rem = total_in - fixed
    if not free:
        s = sum(width); return [w*total_in/s for w in width] if s else width
    if rem <= 0:
        for i in free: width[i] = word_in[i]
        s = sum(width); return [w*total_in/s for w in width]
    if sum(nat_in[i] for i in free) <= rem:
        for i in free: width[i] = nat_in[i]   # compact; don't balloon
        return width
    base = sum(word_in[i] for i in free)
    if base >= rem:
        for i in free: width[i] = word_in[i]
        s = fixed + sum(word_in[i] for i in free); k = total_in/s
        return [w*k if i in tight else word_in[i]*k for i, w in enumerate(width)]
    water = rem - base
    lo, hi = 0.0, max(nat_in[i]-word_in[i] for i in free)
    for _ in range(60):
        mid = (lo+hi)/2
        if sum(min(nat_in[i]-word_in[i], mid) for i in free) < water: lo = mid
        else: hi = mid
    for i in free: width[i] = word_in[i] + min(nat_in[i]-word_in[i], lo)
    return width

def _set_col_widths(t, widths_in):
    tbl = t._tbl; tblPr = tbl.tblPr
    # fixed layout (find-or-create, don't stack duplicates)
    lay = tblPr.find(qn("w:tblLayout"))
    if lay is None:
        lay = OxmlElement("w:tblLayout"); tblPr.append(lay)
    lay.set(qn("w:type"), "fixed")
    # total table width
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW"); tblPr.append(tblW)
    tblW.set(qn("w:w"), str(int(sum(widths_in)*1440))); tblW.set(qn("w:type"), "dxa")
    # rewrite the grid columns (Word uses these under fixed layout)
    grid = tbl.find(qn("w:tblGrid"))
    if grid is not None:
        for gc in list(grid.findall(qn("w:gridCol"))):
            grid.remove(gc)
        for wi in widths_in:
            gc = OxmlElement("w:gridCol"); gc.set(qn("w:w"), str(int(wi*1440))); grid.append(gc)
    # and set each cell width to match
    for i, col in enumerate(t.columns):
        wtw = Twips(int(widths_in[i]*1440))
        for cell in col.cells:
            cell.width = wtw

def add_table(doc, headers, rows, total_in=10.0, gap=True, tight=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    t.autofit = False
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        p = _cell_para(hdr[i])
        _rich(p, h, bold=True)
        _shade(hdr[i], HEAD_FILL); _set_cell_border(hdr[i])
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            if i >= len(cells): break
            p = _cell_para(cells[i])
            _rich(p, "" if val is None else val)
            _set_cell_border(cells[i])
    _set_col_widths(t, _col_layout(headers, rows, total_in, tight=tight))
    if gap:
        g=doc.add_paragraph(); g.paragraph_format.space_after=Pt(2)
    return t

def _heading(doc, text, size, before, after, level=1):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(before); pf.space_after = Pt(after); pf.keep_with_next = True
    r = p.add_run(text); r.bold = True; r.font.name = FONT; r.font.size = Pt(size)
    ol = OxmlElement("w:outlineLvl"); ol.set(qn("w:val"), str(level - 1))
    p._p.get_or_add_pPr().append(ol)
    return p

def h1(doc, t): return _heading(doc, t, 16, 9, 3, level=1)
def h2(doc, t): return _heading(doc, t, 13, 6, 2, level=2)


def add_tables_row(doc, specs, widths_in=None):
    n=len(specs)
    outer=doc.add_table(rows=1, cols=n); outer.alignment=WD_TABLE_ALIGNMENT.LEFT
    tblPr=outer._tbl.tblPr; lay=OxmlElement("w:tblLayout"); lay.set(qn("w:type"),"fixed"); tblPr.append(lay)
    widths_in=widths_in or [10.0/n]*n
    for i,(headers,rows) in enumerate(specs):
        cell=outer.rows[0].cells[i]; cell.width=Twips(int(widths_in[i]*1440))
        cell._tc.remove(cell.paragraphs[0]._p)
        it=cell.add_table(rows=1, cols=len(headers)); it.alignment=WD_TABLE_ALIGNMENT.LEFT; it.autofit=False
        hdr=it.rows[0].cells
        for j,h in enumerate(headers):
            p=_cell_para(hdr[j]); _rich(p,h,bold=True); _shade(hdr[j],HEAD_FILL); _set_cell_border(hdr[j])
        for row in rows:
            cc=it.add_row().cells
            for j,val in enumerate(row):
                if j>=len(cc): break
                _rich(_cell_para(cc[j]),"" if val is None else val); _set_cell_border(cc[j])
        _set_col_widths(it,_col_layout(headers,rows,widths_in[i]-0.1))
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
    return outer

def build(data, out_path):
    doc = Document()
    # default font
    style = doc.styles["Normal"]
    style.font.name = FONT; style.font.size = Pt(BODY)
    # landscape, 0.5" margins
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width = Twips(16838); sec.page_height = Twips(11906)
    for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(sec, m, Twips(720))

    # Title
    p = doc.add_paragraph(); r = p.add_run("Renown — Compendium")
    r.bold = True; r.font.name = FONT; r.font.size = Pt(22)
    ver = data.get("version", "")
    sub = "Generated from renown_data.py"
    if ver:
        sub = f"v{ver} · " + sub
    p2 = doc.add_paragraph(); _rich(p2, sub, italic=True)

    eq = data["equipment"]

    # ── section emitters (row-prep preserved; order set in assembly below) ──
    def sec_eras():
        if rd is not None and getattr(rd, "ERAS", None):
            _rows = [[nm, str(e.get("renown","")), str(e.get("armies","")), str(e.get("cities","")),
                      str(e.get("max_settlements","")), f"+{e.get('influence_per_turn',0)}",
                      str(e.get("innate_diplomacy_influence","")), e.get("envoys","") or "",
                      e.get("unlocks","") or "\u2014"] for nm, e in rd.ERAS.items()]
            h2(doc, "Eras"); add_table(doc, ["Era","Renown","Armies","Cities","Max Settlements","Infl/Turn","Diplo Infl","Envoys","Unlocks"], _rows)
        else:
            h2(doc, "Eras"); add_table(doc, ["Era","Renown","Armies","Cities","Infl/Turn","Diplo Infl","Envoys","Unlocks"], data["eras"])

    def sec_seasons():
        h2(doc, "Seasons"); add_table(doc, ["Season","Name","Effect"], data["seasons"])

    def sec_domain_standings():
        _emp = data["domain_board"]; _cmb = {r[0]: r for r in data["standing_effects"]}
        _merged = []
        for er in _emp:
            dom = er[0]; cr = _cmb.get(dom, [dom,"","",""]); row = [dom]
            for i in (1,2,3):
                e = (er[i] if i < len(er) and er[i] else "").strip()
                c = (cr[i] if i < len(cr) and cr[i] else "").strip()
                row.append((e+" "+c).strip() if c else e)
            _merged.append(row)
        add_table(doc, ["Domain","Rising (3)","Established (6)","Sovereign (10)"], _merged)

    def sec_settlements():
        h2(doc, "Settlements"); add_table(doc, ["Settlement","Tier","Sea Variant","Tax","Muster","Build","Wards","Reach","Notes"], data["settlements"])

    def sec_infra():
        h2(doc, "Infrastructure"); add_table(doc, ["Infrastructure","Upkeep","Freq","Empire Bonus","Tier","Build","Requirement"], data["infrastructure"])

    def sec_wonders():
        h2(doc, "Wonders"); add_table(doc, ["Wonder","Empire Bonus","Build","Requirement"], data["wonders"])

    def sec_terrain():
        if rd is not None and getattr(rd, "TERRAIN", None):
            h2(doc, "Terrain")
            tac = getattr(rd, "TACTICAL_TERRAIN", {}) or {}
            BASE = {"Hill": "Grassland", "Open Field": "Grassland", "Mire": "Wetlands",
                    "Forest": "Forest", "Tundra": "Tundra", "Mountains": "Mountains", "Water": "Water"}
            battle = {}
            for feat, fd in tac.items():
                base = BASE.get(feat, feat); note = fd.get("effect", ""); label = feat if feat != base else ""
                battle.setdefault(base, []).append((f"{label}: {note}" if label else note))
            trows = []
            for n, d in rd.TERRAIN.items():
                mats = ", ".join(d.get("Raw Materials", []) or []) or "\u2014"
                mapfx = d.get("Effect", "\u2014") or "\u2014"
                btl = "  ".join(battle.get(n, [])) or "\u2014"
                trows.append([n, mats, mapfx, btl])
            add_table(doc, ["Terrain", "Raw Materials", "Map Effect", "Battle Effect"], trows)

    def sec_pursuits():
        for s in data["pursuit_sections"]:
            h2(doc, s["title"]); add_table(doc, ["Pursuit", "Mastery Unlock", "Innate Effect", "Mastery Effect"], _alpha(s["rows"]))

    def sec_public_order():
        h2(doc, "Public Order"); add_table(doc, ["PO","State","Effect"], data["public_order"])

    def sec_faith():
        h2(doc, "Faith & Doubt Sources"); add_table(doc, ["Type","Source","Condition"], data["po_modifiers"])

    def sec_trade():
        h2(doc, "Trade & Income"); add_table(doc, ["Rule","Value"], data["trade_rules"], tight={0})

    def sec_retinues():
        h2(doc, "Retinues")
        if rd is not None and getattr(rd, "RETINUES", None):
            _rows = [[n, str(x.get("cost","")), f"{x['to_hit']}+", str(x.get("endurance","")),
                      f"{x['shaking']}+", str(x.get("speed","\u2014")), str(x.get("max_size","\u2014"))]
                     for n, x in rd.RETINUES.items()]
            add_table(doc, ["Retinue","Cost","To Hit","Endurance","Morale","Speed","Max Size"], _rows)
        else:
            add_table(doc, ["Retinue","Cost","To Hit","Endurance","Morale","Speed"], eq["Retinues"])

    def sec_weapons():
        h2(doc, "Melee Weapons");  add_table(doc, ["Weapon","Tier","AP","Init","Keywords"], eq["Weapons"])
        h2(doc, "Ranged Weapons"); add_table(doc, ["Ranged","Tier","AP","Init","Keywords"], eq["Ranged"])
        h2(doc, "Shields");        add_table(doc, ["Shield","Tier","Save","Init","Keywords"], eq["Shields"])
        h2(doc, "Armor");          add_table(doc, ["Armor","Tier","Save","Keywords"], eq["Armor"])

    def sec_tactic_matrix():
        h2(doc, "Tactic Matrix")
        def _relabel(v):
            s = str(v); return s.replace("TS", "Save").replace("TH", "Strike")
        _tm_head = [_relabel(h) for h in data["tactic_matrix_header"]]
        _tm_rows = [[_relabel(c) for c in r] for r in data["tactic_matrix_rows"]]
        add_table(doc, _tm_head, _tm_rows)
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(2)
        _leg = p.add_run("I = Initiative \u00b7 Strike = to Strike \u00b7 Save = to Save"); _leg.italic = True; _leg.font.size = Pt(7)

    def sec_bandits():
        if rd is not None and getattr(rd, "BANDIT_GROWTH_PER_ERA", None):
            g = rd.BANDIT_GROWTH_PER_ERA; growth = dict(g.items() if isinstance(g, dict) else g)
            equip = getattr(rd, "BANDIT_EQUIPMENT_PER_ERA", {}) or {}
            order = list(rd.ERAS.keys()) if getattr(rd, "ERAS", None) else list(growth.keys())
            brows = [[era, f"+{growth.get(era,'\u2014')}/turn", equip.get(era, "\u2014")] for era in order]
            add_table(doc, ["Era", "Bandit Growth", "Armaments"], brows)

    def sec_factions():
        add_table(doc, ["Faction","Mechanic"], data["factions"], tight={0})

    def sec_glossary():
        for cat in data["glossary_categorized"]:
            h2(doc, cat["title"]); add_table(doc, ["Term","Definition"], _alpha(cat["rows"]), tight={0})

    # ── assembly: grouped by likeness, in rulebook introduction order ──
    h1(doc, "Progression");         sec_eras(); sec_seasons()
    h1(doc, "Domains & Standings"); sec_domain_standings()
    h1(doc, "Empire");              sec_settlements(); sec_infra(); sec_wonders(); sec_terrain()
    h1(doc, "Pursuits");            sec_pursuits()
    h1(doc, "Economy");             sec_public_order(); sec_faith(); sec_trade()
    h1(doc, "Armies & Combat");     sec_retinues(); sec_weapons(); sec_tactic_matrix()
    h1(doc, "Bandits");             sec_bandits()
    h1(doc, "Factions");            sec_factions()
    h1(doc, "Glossary");            sec_glossary()
    doc.save(out_path)
    print("wrote " + out_path)

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "compendium_data.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "Compendium.docx"
    build(json.load(open(src, encoding="utf-8")), out)