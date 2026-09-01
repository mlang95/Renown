#!/usr/bin/env python3
"""combat_sheet.py — Renown combat quick-reference (print & laminate)."""
import sys, os
sys.path.insert(0, ".")
import renown_data as rd

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

SERIF, SERIF_B, SERIF_I = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
for face, fn in [("EBG", "EBGaramond-Regular.ttf"), ("EBG-B", "EBGaramond-Bold.ttf"),
                 ("EBG-I", "EBGaramond-Italic.ttf")]:
    for base in ("/root/.fonts", "fonts", "."):
        p = os.path.join(base, fn)
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont(face, p))
                if face == "EBG": SERIF = "EBG"
                elif face == "EBG-B": SERIF_B = "EBG-B"
                elif face == "EBG-I": SERIF_I = "EBG-I"
            except Exception:
                pass
            break

PARCH=(0.96,0.93,0.86); INK=(0.16,0.12,0.08); ACCENT=(0.45,0.18,0.12)
RULE=(0.55,0.45,0.32); BAND=(0.88,0.83,0.72); BANDALT=(0.92,0.88,0.79); CALLOUT=(0.86,0.80,0.66)
PAGE_W, PAGE_H = letter
MARGIN = 0.5 * inch

def _set(c, rgb): c.setFillColorRGB(*rgb)
def _stroke(c, rgb): c.setStrokeColorRGB(*rgb)
def bg(c): _set(c, PARCH); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)

def gtext(key):
    """Single source of truth: pull a keyword's rule text from renown_data.GLOSSARY
    (whitespace-collapsed). Falls back to '' so a renamed/removed key never crashes."""
    return " ".join(str(rd.GLOSSARY.get(key, "")).split())

def header(c, title, sub=None):
    _set(c, ACCENT); c.setFont(SERIF_B, 22)
    c.drawString(MARGIN, PAGE_H-MARGIN-14, title)
    if sub:
        _set(c, INK); c.setFont(SERIF_I, 10); c.drawString(MARGIN, PAGE_H-MARGIN-28, sub)
    _stroke(c, RULE); c.setLineWidth(1.2)
    y = PAGE_H-MARGIN-36; c.line(MARGIN, y, PAGE_W-MARGIN, y)
    return y-14

def chart(c, x, y, w, title, headers, rows, colw=None, fs=8, rowh=13, title_fs=11, align=None):
    # align: per-column 'l' (left, default) | 'c' (centred) | 'r' (right) |
    # 'num' (right-aligned to the column's centre line, so signed ints like
    # 0 and -1 line up on their last digit while the column reads as centred).
    _set(c, ACCENT); c.setFont(SERIF_B, title_fs); c.drawString(x, y, title); y -= 6
    _stroke(c, RULE); c.setLineWidth(0.6); c.line(x, y, x+w, y); y -= rowh
    n = len(headers)
    if colw is None: colw = [w/n]*n
    if align is None: align = ["l"]*n
    NUM_ANCHOR = 0.62                      # fraction of column width for 'num' right edge
    def place(ln, cx, cw, a, font, size):
        if a == "c":   c.drawCentredString(cx+cw/2, _Y, ln)
        elif a == "r": c.drawRightString(cx+cw-3, _Y, ln)
        elif a == "num": c.drawRightString(cx+cw*NUM_ANCHOR, _Y, ln)
        else:          c.drawString(cx+2, _Y, ln)
    _set(c, INK); c.setFont(SERIF_B, fs); cx = x; _Y = y+3
    for h, cw, a in zip(headers, colw, align): place(str(h), cx, cw, a, SERIF_B, fs); cx += cw
    y += 1; _stroke(c, RULE); c.setLineWidth(0.4); c.line(x, y-2, x+w, y-2); y -= rowh
    for i, row in enumerate(rows):
        wrapped = []; maxlines = 1
        for cell, cw in zip(row, colw):
            txt = str(cell); words = txt.split(); lines = []; curl = ""
            for wd in words:
                t = (curl+" "+wd).strip()
                if c.stringWidth(t, SERIF, fs) <= cw-4: curl = t
                else:
                    if curl: lines.append(curl)
                    curl = wd
            if curl: lines.append(curl)
            if not lines: lines = [""]
            wrapped.append(lines); maxlines = max(maxlines, len(lines))
        rh = rowh + (maxlines-1)*(fs+1)
        if i % 2 == 0:
            _set(c, BANDALT); c.rect(x, y-rh+rowh-2, w, rh, fill=1, stroke=0)
        _set(c, INK); c.setFont(SERIF, fs); cx = x
        for lines, cw, a in zip(wrapped, colw, align):
            _Y = y+3
            for ln in lines: place(ln, cx, cw, a, SERIF, fs); _Y -= (fs+1)
            cx += cw
        y -= rh
    return y-4

# ── tactical terrain (battle-tile modifiers) ──
# Source of truth = renown_data.TACTICAL_TERRAIN if present; else this fallback.
# Seize precedence (highest first): Ministry of Military Strategy > Hill >
# Forest (defender) > general rule (attacker).
_TERRAIN_FALLBACK = [
    ("Hill", "Occupant Seizes the Initiative every Skirmish (only an enemy Ministry of Military Strategy overrides)."),
    ("Open Field", "Ranged Weapons +1 to Strike."),
    ("Forest", "Only Scout / Ambush / Flank / Defensive Formation. Defender Seizes the Initiative."),
    ("Mire (Wetlands)", "Unwieldy + Immune Steady; -1 to Save."),
    ("Tundra", "Strained."),
    ("Mountains", "Impassable."),
    ("Water", "End Move after crossing 1 Water Territory."),
    ("Any tile", "Any player may Fall Back after the first Skirmish."),
]

def _terrain_rows():
    tt = getattr(rd, "TACTICAL_TERRAIN", None)
    if isinstance(tt, dict) and tt:
        rows = [[k, v.get("effect", "") if isinstance(v, dict) else str(v)]
                for k, v in tt.items()]
        for g in getattr(rd, "TACTICAL_GLOBAL", []) or []:
            rows.append(["Any tile", g])
        return rows
    return [[k, v] for k, v in _TERRAIN_FALLBACK]

def terrain_chart(c, x, y, w, fs=6.0, rowh=8.6):
    rows = _terrain_rows()
    y = chart(c, x, y, w, "Terrain Modifiers (Battle Tile)",
              ["Terrain", "Effect"], rows,
              colw=[w*0.26, w*0.74], fs=fs, rowh=rowh)
    return y - 4

def step_spine(c, x, y, w):
    rts = {n: r["to_hit"] for n, r in rd.RETINUES.items()}
    rt_str = ", ".join(f"{n.split()[0] if n!='Knight Templar' else 'KT'} {v}+" for n, v in rts.items())
    STEPS = [
        ("Form the Line","Up to 10 front line (1 Strike die each) + up to 5 reserve. Fill at beginning of each skirmish. Rest remain at camp. Default max Army size is 25."),
        ("Choose Tactics","Both pick a Tactic in secret, reveal together. Fall Back can't be chosen in Skirmish 1. (See Tactic Matrix.)"),
        ("Declare Equipment","Attacker declares first; Defender responds (Only relevant with Tiltyard or Bastard Sword dual profile)."),
        ("Initiative","Range \u22122 to +2. Higher Strikes first. At \u22122\u2212 you Blunder (Only Focused Strikes)."),
        ("Roll to Strike",f"D6 per front-line retinue \u2265 to-Strike: {rt_str}. Focused Strike \u2192 Cleave / Deadly / Destroy Shield."),
        ("Strike & Defend","Per Strike, defender resolves in order: Parry \u2192 Save \u2192 Recover. Unsaved = casualty (leaves field at once, replenished by reserves after all Strikes)."),
        ("Strike Back","The other side Strikes the same way, if able."),
		("Panic Check","If a side took 5+ casualties this Skirmish: roll Morale (\u22645 dice)."),
        ("Lose Endurance","Each side that fought: \u22121 Endurance. At 0 Endurance \u2192 Fatigued."),
        ("Break Check","Each Fatigued field, before its token: roll Morale (\u22645 dice). Never triggers Panic. 7+ \u2192 Rout."),
        ("Fatigue Token","Each Fatigued side gains a token: \u22121 to Strike & Morale (rolls cap 6+; Morale uncapped). Tokens stack. You cannot Parry or Recover while Fatigued unless otherwise specified."),
        ("End the Skirmish","Battle ends if a side is wiped, Routs (Morale 7+), or Falls Back. Else, Form the Line."),
    ]
    num_w = 20; title_fs, body_fs = 10.5, 8
    _set(c, ACCENT); c.setFont(SERIF_B, 12); c.drawString(x, y, "THE SKIRMISH"); y -= 4
    _stroke(c, RULE); c.setLineWidth(1.0); c.line(x, y, x+w, y); y -= 14
    spine_x = x + num_w/2
    for i, (title, body) in enumerate(STEPS, 1):
        words = body.split(); lines = []; cur = ""; avail = w-num_w-6
        for wd in words:
            t = (cur+" "+wd).strip()
            if c.stringWidth(t, SERIF, body_fs) <= avail: cur = t
            else: lines.append(cur); cur = wd
        if cur: lines.append(cur)
        _set(c, ACCENT); c.circle(spine_x, y+3, 8, fill=1, stroke=0)
        _set(c, PARCH); c.setFont(SERIF_B, 9); c.drawCentredString(spine_x, y+0.5, str(i))
        tx = x+num_w+4
        _set(c, INK); c.setFont(SERIF_B, title_fs); c.drawString(tx, y+1, title)
        yy = y-(body_fs+2); _set(c, INK); c.setFont(SERIF, body_fs)
        for ln in lines: c.drawString(tx, yy, ln); yy -= (body_fs+1.5)
        y = yy-6
    return y

def front(c):
    bg(c)
    top = header(c, "Combat Quick Reference", f"Renown v{rd.VERSION} \u2014 the Skirmish sequence & rolls")
    gap = 0.3*inch
    left_w = (PAGE_W-2*MARGIN-gap)*0.56
    right_x = MARGIN+left_w+gap; right_w = PAGE_W-MARGIN-right_x
    left_end = step_spine(c, MARGIN, top, left_w)
    y = top
    rt_rows = [[n, f"{r['to_hit']}+", r['endurance'], f"{r['shaking']}+", r['cost'],
                ("Unbrk" if r.get('unbreakable') else "")] for n, r in rd.RETINUES.items()]
    y = chart(c, right_x, y, right_w, "Retinues", ["Type","Strk","End","Mor","Cost",""], rt_rows,
              colw=[right_w*0.34,right_w*0.12,right_w*0.11,right_w*0.12,right_w*0.18,right_w*0.13],
              align=["l","num","num","num","num","l"]); y -= 6
    def_rows = [["1 " + rd.PARRY, gtext(rd.PARRY)],
                ["2 Save", "D6 + weapon AP + shield bonus \u2265 armor value."],
                ["3 " + rd.RECOVER, gtext(rd.RECOVER)]]
    y = chart(c, right_x, y, right_w, "Defense Sequence (per Strike)", ["Step","Roll"], def_rows,
              colw=[right_w*0.24,right_w*0.76], fs=7.5); y -= 6
    nat_keys = [rd.SHATTER_ARMOR, rd.CLEAVE, rd.DESTROY_SHIELD, rd.POISON, rd.RIPOSTE, rd.PLANISHING]
    nat_rows = [[k, gtext(k)] for k in nat_keys if k in rd.GLOSSARY]
    y = chart(c, right_x, y, right_w, "On a Natural 6", ["Keyword","Effect"], nat_rows,
              colw=[right_w*0.26,right_w*0.74], fs=7.5); y -= 6
    se_rows = [[f"{dom} {st}", eff] for ( st,dom), eff in rd.STANDING_EFFECTS.items()]
    y = chart(c, right_x, y, right_w, "Standing Combat Effects", ["Standing","Effect"], se_rows,
              colw=[right_w*0.42,right_w*0.58], fs=7.5); y -= 8
    cap_rows = [["Blunder (Init \u22122 or lower)","Your to-Strike is set to 6+, only a Focused Strike can succeed, before other negative modifiers."],
                ["Capped at 6+","Fatigue \u22121 to to-Strike; Tempered keeps the Save at 6+ vs any AP. A Focused Save succeeds. (No Parry or Recover while Fatigued.)"],
                ["Pushes past 6+ \u2192 7+ (auto-miss)","Shield \u22121 to Strike (Kite/Tower/Heater) and enemy tactic to-Strike penalties apply AFTER the cap \u2014 they can raise the target to 7+."],
                ["Uncapped \u2192 Rout","Fatigue's \u22121 to Morale is NOT capped. At modified Morale 7+ the army Routs."]]
    y = chart(c, right_x, y, right_w, "The 6+ Ceiling", ["Rule","Effect"], cap_rows,
              colw=[right_w*0.34,right_w*0.66], fs=7.5)
    # compact Tactic Matrix in the lower-left whitespace, below the Skirmish steps
    tactic_grid(c, MARGIN, left_end - 14, left_w, rowh=17, cell_fs=5.2, label_fs=6,
                hdr_fs=5.8, title_fs=10, line_h=6.6, label_w=42)
    _footer(c, "Front"); c.showPage()

def tactic_grid(c, x, y, w, rowh=26, cell_fs=7, label_fs=7, hdr_fs=6.8, title_fs=12,
                line_h=8, label_w=50, title="TACTIC MATRIX", intro=True):
    T = rd.TACTICS; n = len(T)
    rowlabel = {t: t.split(" ") if " " in t else [t] for t in T}
    _set(c, ACCENT); c.setFont(SERIF_B, title_fs); c.drawString(x, y, title); y -= 4
    _stroke(c, RULE); c.setLineWidth(1.0); c.line(x, y, x+w, y); y -= 6
    if intro:
        _set(c, INK); c.setFont(SERIF_I, max(6, cell_fs))
        c.drawString(x, y, "Your tactic (row) vs opponent (col). I = Initiative, Str = to Strike, Sv = to Save (lower target is better)."); y -= 11
    cell = (w-label_w)/n
    def fmt(m):
        parts = []
        if m.get("end"): return "END"
        if m.get("no_combat"): return "no cbt"
        if m.get("I"): parts.append(f"I{m['I']:+d}")
        if m.get("TH"): parts.append(f"Str{m['TH']:+d}")
        if m.get("TS"): parts.append(f"Sv{m['TS']:+d}")
        return " ".join(parts) if parts else "\u2014"
    _set(c, INK); c.setFont(SERIF_B, hdr_fs); cx = x+label_w; hdr_h = line_h*2 + 2
    for t in T:
        words = t.split(" ") if " " in t else [t]; ty = y-(hdr_h-len(words)*line_h)/2-line_h+1
        for wd in words: c.drawCentredString(cx+cell/2, ty, wd); ty -= line_h
        cx += cell
    y -= hdr_h; _stroke(c, RULE); c.setLineWidth(0.5); c.line(x, y, x+w, y); y -= rowh
    for ri, rt in enumerate(T):
        if ri % 2 == 0: _set(c, BANDALT); c.rect(x, y, w, rowh, fill=1, stroke=0)
        _set(c, ACCENT); c.setFont(SERIF_B, label_fs); words = rowlabel[rt]
        ty = y+rowh/2+len(words)*line_h/2-line_h+1
        for wd in words: c.drawString(x+1, ty, wd); ty -= line_h
        cx = x+label_w
        for ct in T:
            a, _b = rd.TACTIC_MATRIX[(rt, ct)]
            _set(c, INK); c.setFont(SERIF, cell_fs); c.drawCentredString(cx+cell/2, y+rowh/2-cell_fs/2+1, fmt(a))
            _stroke(c, RULE); c.setLineWidth(0.2); c.line(cx, y, cx, y+rowh); cx += cell
        y -= rowh
    _stroke(c, RULE); c.setLineWidth(0.5); c.line(x, y+rowh, x+w, y+rowh)
    return y-6

def _kw_lines(c, w, k, defn, name_fs, body_fs):
    kw_w = c.stringWidth(k+"  ", SERIF_B, name_fs); words = defn.split(); line=""; first=True; lines=1
    for wd in words:
        t = (line+" "+wd).strip(); avail = (w-kw_w) if first else w
        if c.stringWidth(t, SERIF, body_fs) <= avail: line = t
        else: lines += 1; first = False; line = wd
    return lines

def _draw_keyword(c, x, y, w, k, defn, name_fs, body_fs, line_h):
    _set(c, ACCENT); c.setFont(SERIF_B, name_fs); c.drawString(x, y, k)
    kw_w = c.stringWidth(k+"  ", SERIF_B, name_fs); _set(c, INK); c.setFont(SERIF, body_fs)
    words = defn.split(); line=""; first=True; yy=y; tx0=x+kw_w
    for wd in words:
        t = (line+" "+wd).strip(); avail = (w-kw_w) if first else w
        if c.stringWidth(t, SERIF, body_fs) <= avail: line = t
        else: c.drawString(tx0 if first else x, yy, line); yy -= line_h; first=False; tx0=x; line=wd
    c.drawString(tx0 if first else x, yy, line)
    return yy

def keywords_block(c, x, y, full_w, gap, KW, floor):
    """Keywords in two balanced full-width columns; auto-fits font/spacing to fill the
    available space (up to a cap) while clearing the footer. Text pulled from GLOSSARY."""
    _set(c, ACCENT); c.setFont(SERIF_B, 11); c.drawString(x, y, "Keywords")
    yk = y-10; _stroke(c, RULE); c.setLineWidth(0.6); c.line(x, yk, x+full_w, yk); yk -= 12
    cw = (full_w-gap)/2; xs = [x, x+cw+gap]; avail = yk - floor
    items = sorted([(k, " ".join(str(rd.GLOSSARY[k]).split())) for k in KW if k in rd.GLOSSARY],
                   key=lambda kv: kv[0].lower())
    def layout(scale):
        nfs, bfs, lh, gp = 7.0*scale, 6.6*scale, 7.5*scale, 8.5*scale
        hs = [_kw_lines(c, cw, k, d, nfs, bfs)*lh + gp for k, d in items]
        half = sum(hs)/2; acc = 0; split = len(hs)
        for i, h in enumerate(hs):                       # balanced break point
            if acc >= half and i > 0: split = i; break
            acc += h
        return (nfs, bfs, lh, gp), split, max(sum(hs[:split]), sum(hs[split:]))
    # largest scale (<= cap) where the taller balanced column still fits
    scale = 1.9
    while scale > 0.6:
        params, split, tallest = layout(scale)
        if tallest <= avail: break
        scale -= 0.04
    (nfs, bfs, lh, gp), split, _ = layout(scale)
    yy = yk
    for i, (k, d) in enumerate(items):
        if i == split: yy = yk
        cx = xs[0] if i < split else xs[1]
        yy = _draw_keyword(c, cx, yy, cw, k, d, nfs, bfs, lh) - gp
    return yy

def back(c):
    bg(c)
    top = header(c, "Combat Charts", f"Renown v{rd.VERSION} \u2014 equipment, terrain & keywords    (\u00ac = Negate, ! = Immune)")
    full_w = PAGE_W-2*MARGIN
    gap = 0.3*inch; col_w = (full_w-gap)/2; lx, rx = MARGIN, MARGIN+col_w+gap; y_start = top
    def kw_short(tags):
        m = {"Deadly":"Dly","Unstoppable":"Unst","Cleave":"Clv","Destroy Shield":"DShd",
             "Unwieldy":"Unw","Steady":"Stdy","2H":"2H","Nimble":"Nmb","Deflect":"Dfl",
             "One Shot":"1Sht","Poison":"Psn","Negate Shielded":"¬Shd","Negate Riposte":"¬Rip",
             "Negate Tempered":"¬Tmp","Negate Unstoppable":"¬Uns","Dual Wield":"Dual","Florentine":"Flor"}
        m = {"Deadly":"Deadly","Unstoppable":"Unstopp","Cleave":"Cleave","Destroy Shield":"DShield",
             "Unwieldy":"Unwldy","Steady":"Stdy","2H":"2H","Nimble":"Nmb",
             "One Shot":"1Shot","Poison":"Poison","Negate Shielded":"¬Shielded","Negate Riposte":"¬Riposte",
             "Negate Tempered":"¬Tempered","Dual Wield":"Dual", "Immune Destroy Shield" : "!DShield"}
        return ", ".join(m.get(t, t) for t in tags) or "\u2014"
    wrows = [[n, w["tier"], w["ap"], f"{w['init']:+d}", kw_short(w["tags"])] for n, w in rd.WEAPONS.items()]
    yl = chart(c, lx, y_start, col_w, "Melee Weapons", ["Weapon","Tier","AP","Init","Keywords"], wrows,
               colw=[col_w*0.24, col_w*0.13, col_w*0.08, col_w*0.09, col_w*0.46], fs=7.2, rowh=11,
               align=["l","l","num","num","l"])
    rrows = [[n, w["tier"], w["ap"], f"{w['init']:+d}", kw_short(w["tags"])] for n, w in rd.RANGED.items()]
    yl = chart(c, lx, yl-6, col_w, "Ranged Weapons", ["Weapon","Tier","AP","Init","Keywords"], rrows,
               colw=[col_w*0.24, col_w*0.13, col_w*0.08, col_w*0.09, col_w*0.46], fs=7.2, rowh=11,
               align=["l","l","num","num","l"])
    yr = y_start
    arows = [[n, a["tier"], f"{a['save']}+"] for n, a in rd.ARMORS.items()]
    yr = chart(c, rx, yr, col_w, "Armor", ["Armor","Tier","Save"], arows,
               colw=[col_w*0.45,col_w*0.32,col_w*0.23], fs=8, rowh=12.5, align=["l","l","num"])
    srows = [[n, s["tier"] if s["tier"] else "\u2014", f"+{s['save_bonus']}", f"{s['init']:+d}", kw_short(s["tags"])]
             for n, s in rd.SHIELDS.items() if n]
    yr = chart(c, rx, yr-6, col_w, "Shields", ["Shield","Tier","Save","Init","Keywords"], srows,
               colw=[col_w*0.26,col_w*0.18,col_w*0.12,col_w*0.11,col_w*0.33], fs=7.5, rowh=12.5,
               align=["l","l","num","num","l"])
    yr = terrain_chart(c, rx, yr-6, col_w, fs=7.2, rowh=11)
    KW = [rd.SHATTER_ARMOR, rd.CLEAVE, rd.DESTROY_SHIELD, rd.POISON, rd.UNSTOPPABLE,
          rd.PARRY, rd.RIPOSTE, rd.FLORENTINE, rd.RECOVER, rd.SERRATED, rd.PLANISHING, rd.DEFLECT,
          rd.NIMBLE, rd.DRILLED, rd.STEADY, rd.UNWIELDY, rd.BLUNDER, rd.ONE_SHOT,
          rd.IMMUNE_PANIC, rd.UNBREAKABLE, rd.FATIGUE_TOKEN, rd.MINUS_1_TBH, rd.TWO_H,
          rd.NEGATE_UNSTOPPABLE, rd.NEGATE_TEMPERED, rd.MINUS_1_PARRY, rd.NEGATE_RIPOSTE]
    # Keywords span the full page width in two columns, below both table columns,
    # so the (often long) list uses the lower-left whitespace instead of overflowing.
    keywords_block(c, MARGIN, min(yl, yr) - 8, full_w, gap, KW, floor=MARGIN + 6)
    _footer(c, "Back"); c.showPage()

def _footer(c, label):
    _set(c, RULE); c.setFont(SERIF_I, 7)
    c.drawString(MARGIN, MARGIN-6, f"Renown \u2014 Combat Quick Reference ({label})")
    c.drawRightString(PAGE_W-MARGIN, MARGIN-6, f"v{rd.VERSION}")

def build(out_path):
    c = canvas.Canvas(out_path, pagesize=letter)
    c.setTitle("Renown — Combat Quick Reference")
    front(c); back(c); c.save()
    print(f"wrote combat sheet -> {out_path}")

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "combat_sheet.pdf")