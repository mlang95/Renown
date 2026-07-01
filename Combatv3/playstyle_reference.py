#!/usr/bin/env python
# playstyle_reference.py - one-page (landscape Letter) playstyle reference card.
# Reads PLAYSTYLES, FACTIONS, WONDERS from renown_data (single source of truth).
# Usage:  python playstyle_reference.py [out.pdf]      (default: cards/playstyle_reference.pdf)
import sys, os, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import renown_data as rd

# ---- fonts (EB Garamond, same loader as combat_sheet.py; Helvetica fallback) ----
SERIF, SERIF_B, SERIF_I = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
for face, fn in [("EBG", "EBGaramond-Regular.ttf"), ("EBG-B", "EBGaramond-Bold.ttf"),
                 ("EBG-I", "EBGaramond-Italic.ttf")]:
    for base in ("/root/.fonts", "fonts", "."):
        p = os.path.join(base, fn)
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont(face, p))
                if   face == "EBG":   SERIF = "EBG"
                elif face == "EBG-B": SERIF_B = "EBG-B"
                elif face == "EBG-I": SERIF_I = "EBG-I"
            except Exception:
                pass
            break

PS   = rd.PLAYSTYLES
FACT = getattr(rd, "FACTIONS", {})
try:    WONDERS = set(rd.WONDERS)
except Exception: WONDERS = set()

AXES = [("military_solutions", "Military"), ("economy_generators", "Economy"),
        ("faith_management", "Faith"), ("doubt_warfare", "Disruption"),
        ("political_control", "Influence")] #("board_presence", "Board"),
        #("degenerate_punishment", "Punish")]
AXIS_LABELS = [lab for _, lab in AXES]

IND, PRO, CUN, PIE = "#2E5A8C", "#9E2B25", "#1c1c20", "#C6A024"
NEU = "#6a6a72"
DOMC = {"Industry": IND, "Prowess": PRO, "Cunning": CUN, "Piety": PIE}
SPECIAL = {"Polymath": "#CC6A1A", "Influence": "#6A3D8F", "Generalist": NEU, "The Duke": "#2b2b32"}
INK   = HexColor("#26262e"); MUTE = HexColor("#7a7a82"); TAG = HexColor("#a59a82")
WONINK= HexColor("#7a5a1a"); GRIDC = HexColor("#d9d4c8"); RING = HexColor("#e3ded3")
META  = HexColor("#33333b")

ORDER = ['Generalist', 'Mono-Industry', 'Industry x Piety', 'Industry x Cunning',
         'Industry x Prowess', 'Mono-Prowess', 'Prowess x Piety', 'Prowess x Cunning',
         'Cunning x Piety', 'Influence', 'Polymath', 'The Duke']
ORDER = [b for b in ORDER if b in PS] + [b for b in PS if b not in ORDER]  # tolerate set changes

def doms_of(name):
    if " x " in name: return name.split(" x ")
    if name.startswith("Mono-"): return [name.split("-", 1)[1]]
    return [name]
def disp(x): return x[4:] if x.startswith("The ") else x
def mech_name(key):
    ent = FACT.get(key); m = str(ent.get("mechanic", "")) if isinstance(ent, dict) else ""
    return m.split(":")[0].strip() if ":" in m else disp(key)

def _c(hexs): return HexColor(hexs)
def mix(h1, h2, t=0.5):
    a = tuple(int(h1[i:i+2], 16) for i in (1, 3, 5)); b = tuple(int(h2[i:i+2], 16) for i in (1, 3, 5))
    return Color(*[(a[i] + (b[i]-a[i])*t)/255.0 for i in range(3)])

def head_colors(doms):
    cols = [DOMC[d] for d in doms if d in DOMC]
    if len(cols) == 2:  return ("grad", [_c(cols[0]), mix(cols[0], cols[1]), _c(cols[1])], [0.14, 0.5, 0.86])
    if len(cols) == 1:  return ("solid", _c(cols[0]), None)
    return ("solid", _c(SPECIAL.get(doms[0], NEU)), None)
def bar_color(doms):
    if doms[0] in DOMC: return _c(DOMC[doms[0]])
    return _c(SPECIAL.get(doms[0], NEU))

def wrap(c, text, font, size, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ---- geometry (points; landscape Letter) ----
PAGE_W, PAGE_H = landscape(letter)           # 792 x 612
MX = 29; MT = 22; MB = 20
TITLE_Y = PAGE_H - MT - 16
RULE_Y  = PAGE_H - MT - 26
FOOT_Y  = MB + 4
GRID_TOP = RULE_Y - 8
GRID_BOT = FOOT_Y + 12
GAP = 7
COLS, ROWS = 4, 3
COL_W = (PAGE_W - 2*MX - (COLS-1)*GAP) / COLS
ROW_H = (GRID_TOP - GRID_BOT - (ROWS-1)*GAP) / ROWS
HEAD_H = 17

def radar(c, cx, cy, R, vals, color):
    n = len(vals)
    ang = [math.radians(90 - i*360/n) for i in range(n)]      # Military at top, clockwise
    def pt(i, r): return (cx + r*math.cos(ang[i]), cy + r*math.sin(ang[i]))
    # rings
    c.setStrokeColor(RING); c.setLineWidth(0.6)
    for lvl in range(1, 6):
        r = R*lvl/5; p = c.beginPath()
        x0, y0 = pt(0, r); p.moveTo(x0, y0)
        for i in range(1, n): p.lineTo(*pt(i, r))
        p.close(); c.drawPath(p, stroke=1, fill=0)
    for i in range(n):
        c.line(cx, cy, *pt(i, R))
    # data polygon
    p = c.beginPath(); x0, y0 = pt(0, R*vals[0]/5); p.moveTo(x0, y0)
    for i in range(1, n): p.lineTo(*pt(i, R*vals[i]/5))
    p.close()
    c.setFillColor(color); c.setFillAlpha(0.34); c.setStrokeColor(color); c.setStrokeAlpha(1); c.setLineWidth(1.5)
    c.drawPath(p, stroke=1, fill=1); c.setFillAlpha(1)
    c.setFillColor(color)
    for i in range(n):
        x, y = pt(i, R*vals[i]/5); c.circle(x, y, 1.5, stroke=0, fill=1)
    # labels
    c.setFont(SERIF, 6.2); c.setFillColor(MUTE)
    for i in range(n):
        lx, ly = pt(i, R + 8); ca = math.cos(ang[i]); sa = math.sin(ang[i])
        dy = 3.0 if sa < -0.34 else (-1.5 if sa > 0.34 else -2.0)
        if abs(ca) < 0.34:   c.drawCentredString(lx, ly - dy, AXIS_LABELS[i])
        elif ca > 0:         c.drawString(lx, ly - dy, AXIS_LABELS[i])
        else:                c.drawRightString(lx, ly - dy, AXIS_LABELS[i])

def card(c, name, x, ytop):
    d = PS[name]; doms = doms_of(name)
    vals = [d.get(k, 0) for k, _ in AXES]
    wonset = {disp(w) for w in d.get("wonders", [])}
    builds = sorted({disp(p) for p in d.get("pairs", set())} - wonset)
    wonders = sorted(disp(w) for w in d.get("wonders", []))
    facts  = " \u00b7 ".join(mech_name(f) for f in d.get("factions", []))

    # card clip + header
    c.saveState()
    cp = c.beginPath(); cp.roundRect(x, ytop - ROW_H, COL_W, ROW_H, 4); c.clipPath(cp, stroke=0, fill=0)
    kind, col, pos = head_colors(doms)
    hy = ytop - HEAD_H
    hp = c.beginPath(); hp.rect(x, hy, COL_W, HEAD_H); c.clipPath(hp, stroke=0, fill=0)
    if kind == "grad":
        c.linearGradient(x, hy, x + COL_W, hy, col, pos, extend=True)
    else:
        c.setFillColor(col); c.rect(x, hy, COL_W, HEAD_H, stroke=0, fill=1)
    c.restoreState()
    # header text (dark shadow + white)
    ty = hy + 5
    c.setFont(SERIF_B, 11)
    c.setFillColor(Color(0, 0, 0, 0.30)); c.drawString(x + 7.6, ty - 0.6, name)
    c.setFillColor(Color(1, 1, 1)); c.drawString(x + 7.0, ty, name)

    # radar
    radar(c, x + COL_W/2, hy - 44, 28, vals, bar_color(doms))

    # meta rows
    inner = x + 9; tag_w = 34; val_x = inner + tag_w; maxw = x + COL_W - 9 - val_x
    yy = hy - 92
    sep_y = yy + 9
    c.setStrokeColor(HexColor("#efece4")); c.setLineWidth(0.6); c.line(x + 6, sep_y, x + COL_W - 6, sep_y)
    def row(tag, val, color=META):
        nonlocal yy
        c.setFont(SERIF_B, 6.4); c.setFillColor(TAG); c.drawString(inner, yy, tag.upper())
        c.setFont(SERIF, 8.6); c.setFillColor(color)
        for ln in wrap(c, val, SERIF, 8.6, maxw):
            c.drawString(val_x, yy, ln); yy -= 9.6
        yy -= 1.5
    row("Factions", facts or "\u2014")
    row("Build", " \u00b7 ".join(builds) if builds else "\u2014")
    # wonders with diamond marks
    c.setFont(SERIF_B, 6.4); c.setFillColor(TAG); c.drawString(inner, yy, "WONDER")
    c.setFont(SERIF, 8.6); c.setFillColor(WONINK)
    wtext = "  ".join("\u25c6 " + w for w in wonders)
    for ln in wrap(c, wtext, SERIF, 8.6, maxw):
        c.drawString(val_x, yy, ln); yy -= 9.6

    # border
    c.setStrokeColor(GRIDC); c.setLineWidth(0.8)
    c.roundRect(x, ytop - ROW_H, COL_W, ROW_H, 4, stroke=1, fill=0)

def build(out):
    c = canvas.Canvas(out, pagesize=(PAGE_W, PAGE_H))
    # title
    c.setFillColor(INK); c.setFont(SERIF_B, 20); c.drawString(MX, TITLE_Y, "RENOWN")
    w = c.stringWidth("RENOWN", SERIF_B, 20)
    c.setFont(SERIF_I, 12); c.setFillColor(HexColor("#6a6a72"))
    c.drawString(MX + w + 8, TITLE_Y + 1, "\u00b7 playstyle reference")
    # domain legend (right)
    lx = PAGE_W - MX
    for nm, hexc in reversed(list(DOMC.items())):
        c.setFont(SERIF, 9.5)
        tw = c.stringWidth(nm, SERIF, 9.5)
        c.setFillColor(INK); c.drawRightString(lx, TITLE_Y + 1, nm); lx -= tw + 6
        c.setFillColor(_c(hexc)); c.rect(lx - 9, TITLE_Y - 1, 9, 9, stroke=0, fill=1); lx -= 9 + 13
    c.setStrokeColor(INK); c.setLineWidth(1.6); c.line(MX, RULE_Y, PAGE_W - MX, RULE_Y)
    # grid
    for idx, name in enumerate(ORDER):
        r, col = divmod(idx, COLS)
        x = MX + col*(COL_W + GAP)
        ytop = GRID_TOP - r*(ROW_H + GAP)
        card(c, name, x, ytop)
    # footer
    c.setFont(SERIF_I, 8.5); c.setFillColor(MUTE)
    c.drawCentredString(PAGE_W/2, FOOT_Y,
        "Radar = relative emphasis (1\u20135) across the seven strategic axes  \u00b7  "
        "\u25c6 marks a Wonder  \u00b7  paired archetypes blend their two domain colors")
    c.showPage(); c.save()
    print("playstyle reference ->", out)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("cards", "playstyle_reference.pdf")
    d = os.path.dirname(out)
    if d and not os.path.exists(d): os.makedirs(d, exist_ok=True)
    build(out)