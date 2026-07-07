#!/usr/bin/env python
# settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3
# wards) used for every settlement; a Metropolis Extension appends a 4th ward to
# the single capital; a Hamlet mat (3 wards, no upgrade). Data-driven.
# Ward slots match the pursuit tile (~40x52mm); tune SLOT_*.
# Usage:  python settlement_mats.py [out.pdf]
import sys, os, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import renown_data as rd

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

MM = 72.0 / 25.4
SLOT_W, SLOT_H = 40*MM, 52*MM
SLOT_GAP = 6
PAD = 12
HEAD_H = 24
LADDER_H = 46

INK = HexColor("#2b2620"); MUTE = HexColor("#8a8072"); TAG = HexColor("#a59a82")
PARCH = HexColor("#f4efe4"); FRAME = HexColor("#c9bfa8"); SLOTBG = HexColor("#efe9db")
SLOTLINE = HexColor("#b7ab8e")
TIER_COL = {0: "#7d7566", 1: "#6f7a52", 2: "#5f7360", 3: "#4f6a72", 4: "#5a4f72"}
PAGE_W, PAGE_H = letter
MX, MY = 26, 26
MAT_GAP = 16

def _c(h): return HexColor(h)

def panel_size(tiers):
    n = len(tiers)
    w = n*SLOT_W + (n-1)*SLOT_GAP + 2*PAD
    h = HEAD_H + 6 + LADDER_H + 14 + SLOT_H + 26 + 2*PAD
    return w, h

def draw_panel(c, x, ytop, tiers, title, subtitle, head_col, legend, connector=False):
    n = len(tiers)
    w, h = panel_size(tiers)

    c.setFillColor(PARCH); c.setStrokeColor(FRAME); c.setLineWidth(1.2)
    c.roundRect(x, ytop - h, w, h, 8, stroke=1, fill=1)

    # left connector notches (for the extension that appends onto a mat)
    if connector:
        c.setFillColor(PARCH); c.setStrokeColor(FRAME); c.setLineWidth(1.2)
        for cy in (ytop - h*0.34, ytop - h*0.66):
            c.circle(x, cy, 6, stroke=1, fill=1)

    hy = ytop - HEAD_H
    c.saveState(); hp = c.beginPath(); hp.roundRect(x, hy, w, HEAD_H, 8); c.clipPath(hp, stroke=0, fill=0)
    c.setFillColor(_c(head_col)); c.rect(x, hy, w, HEAD_H, stroke=0, fill=1); c.restoreState()
    c.setFont(SERIF_B, 12.5); c.setFillColor(Color(1, 1, 1)); c.drawString(x + PAD, hy + 7.5, title)
    if subtitle:
        c.setFont(SERIF_I, 8.2); c.setFillColor(Color(1, 1, 1, 0.85))
        c.drawRightString(x + w - PAD, hy + 8, subtitle)

    # tier ladder
    ly = hy - 6
    cellw = (w - 2*PAD) / n
    for i, t in enumerate(tiers):
        d = rd.SETTLEMENTS[t]; cx = x + PAD + i*cellw
        c.setFillColor(_c(TIER_COL.get(d.get("tier"), "#6b6257")))
        c.roundRect(cx + 2, ly - LADDER_H, cellw - 4, LADDER_H, 4, stroke=0, fill=1)
        c.setFont(SERIF_B, 9); c.setFillColor(Color(1, 1, 1)); c.drawString(cx + 8, ly - 12, t)
        c.setFillColor(Color(1, 1, 1, 0.9)); c.setFont(SERIF, 6.6)
        c.drawString(cx + 8, ly - 22, f"Tax {d.get('tax_income')}  Mus {d.get('muster_limit')}")
        c.drawString(cx + 8, ly - 31, f"Reach {d.get('reach')}  Build {d.get('build_time')}t")
        c.setStrokeColor(Color(1, 1, 1, 0.7)); c.setLineWidth(0.8)
        c.circle(cx + cellw - 12, ly - LADDER_H + 11, 5, stroke=1, fill=0)
        if i < n - 1:
            c.setFillColor(Color(1, 1, 1)); c.setFont(SERIF_B, 11)
            c.drawCentredString(cx + cellw, ly - LADDER_H/2 - 4, "\u203a")

    # ward slots, one per tier, tagged by unlock tier
    gy = ly - LADDER_H - 14
    for i, t in enumerate(tiers):
        sx = x + PAD + i*(SLOT_W + SLOT_GAP)
        c.setFillColor(SLOTBG); c.setStrokeColor(SLOTLINE); c.setLineWidth(0.8); c.setDash(3, 2)
        c.roundRect(sx, gy - SLOT_H, SLOT_W, SLOT_H, 4, stroke=1, fill=1); c.setDash()
        tag = t.upper()
        c.setFont(SERIF_B, 6.6); tw = c.stringWidth(tag, SERIF_B, 6.6)
        c.setFillColor(_c(TIER_COL.get(rd.SETTLEMENTS[t].get("tier"), "#6b6257")))
        c.roundRect(sx + 6, gy - 16, tw + 12, 12, 3, stroke=0, fill=1)
        c.setFillColor(Color(1, 1, 1)); c.drawString(sx + 12, gy - 13, tag)
        c.setFont(SERIF_I, 8); c.setFillColor(MUTE)
        c.drawCentredString(sx + SLOT_W/2, gy - SLOT_H/2 - 3, "ward")
    if legend:
        c.setFont(SERIF_I, 7.5); c.setFillColor(MUTE)
        c.drawString(x + PAD, ytop - h + 7, legend)
    return w, h

def draw_hamlet(c, x, ytop):
    d = rd.SETTLEMENTS["Hamlet"]; wards = d.get("wards", 3)
    cols = min(3, wards); rows = math.ceil(wards/cols); P = 12
    w = cols*SLOT_W + (cols-1)*SLOT_GAP + 2*P
    h = HEAD_H + 18 + rows*SLOT_H + (rows-1)*SLOT_GAP + 2*P
    c.setFillColor(PARCH); c.setStrokeColor(FRAME); c.setLineWidth(1.2)
    c.roundRect(x, ytop - h, w, h, 8, stroke=1, fill=1)
    hy = ytop - HEAD_H
    c.saveState(); hp = c.beginPath(); hp.roundRect(x, hy, w, HEAD_H, 8); c.clipPath(hp, stroke=0, fill=0)
    c.setFillColor(_c(TIER_COL[0])); c.rect(x, hy, w, HEAD_H, stroke=0, fill=1); c.restoreState()
    c.setFont(SERIF_B, 12.5); c.setFillColor(Color(1, 1, 1)); c.drawString(x + P, hy + 7.5, "Hamlet")
    c.setFont(SERIF_I, 8.2); c.setFillColor(Color(1, 1, 1, 0.85))
    c.drawRightString(x + w - P, hy + 8, f"Tier 0  \u00b7  {wards} wards  \u00b7  does not upgrade")
    gy = hy - P - 4
    for i in range(wards):
        r, cc = divmod(i, cols)
        sx = x + P + cc*(SLOT_W + SLOT_GAP); sty = gy - r*(SLOT_H + SLOT_GAP)
        c.setFillColor(SLOTBG); c.setStrokeColor(SLOTLINE); c.setLineWidth(0.8); c.setDash(3, 2)
        c.roundRect(sx, sty - SLOT_H, SLOT_W, SLOT_H, 4, stroke=1, fill=1); c.setDash()
        c.setFont(SERIF_I, 8); c.setFillColor(MUTE)
        c.drawCentredString(sx + SLOT_W/2, sty - SLOT_H/2 - 3, "ward")
    return w, h

def build(out):
    c = canvas.Canvas(out, pagesize=letter)
    x = MX; y = PAGE_H - MY
    # Settlement mat (Village -> City) + Metropolis Extension appended to its right
    w, h = draw_panel(c, x, y, ["Village", "Town", "City"], "Settlement",
                      "Village \u2192 City", "#5f5647",
                      "Each ward unlocks at its tagged tier.")
    draw_panel(c, x + w - 6, y, ["Metropolis"], "+ Metropolis", "",
               "#5a4f72", "Appends to your capital.", connector=True)
    y -= h + MAT_GAP
    draw_hamlet(c, x, y)
    c.showPage(); c.save()
    print(f"settlement mats -> {out}  (Settlement + Metropolis extension + Hamlet, slot {SLOT_W/MM:.0f}x{SLOT_H/MM:.0f}mm)")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("cards", "settlement_mats.pdf")
    dd = os.path.dirname(out)
    if dd and not os.path.exists(dd):
        os.makedirs(dd, exist_ok=True)
    build(out)

def build_tableau(out):
    """A full player tableau on ONE landscape page: 3 Settlement mats + Hamlet."""
    from reportlab.lib.pagesizes import landscape
    global SLOT_W, SLOT_H
    SLOT_W, SLOT_H = 37*MM, 46*MM        # sized to fit a 2x2 on landscape Letter
    PW, PH = landscape(letter)
    c = canvas.Canvas(out, pagesize=(PW, PH))
    pw, ph = panel_size(["Village", "Town", "City"])
    gap = 16
    col_x = [MX, MX + pw + gap]
    row_y = [PH - MX, PH - MX - ph - gap]
    # three settlement mats + hamlet in the fourth cell
    draw_panel(c, col_x[0], row_y[0], ["Village", "Town", "City"], "Settlement", "Village \u2192 City", "#5f5647", "Each ward unlocks at its tagged tier.")
    draw_panel(c, col_x[1], row_y[0], ["Village", "Town", "City"], "Settlement", "Village \u2192 City", "#5f5647", None)
    draw_panel(c, col_x[0], row_y[1], ["Village", "Town", "City"], "Settlement", "Village \u2192 City", "#5f5647", None)
    draw_hamlet(c, col_x[1], row_y[1])
    c.showPage(); c.save()
    print(f"tableau -> {out}  (3 Settlement + Hamlet, landscape, slot {SLOT_W/MM:.0f}x{SLOT_H/MM:.0f}mm)")

def _ladder_strip(c, x, y, w, tiers, h=52):
    """The tier reference, drawn once: one cell per tier with stats."""
    n = len(tiers); cw = w / n
    for i, t in enumerate(tiers):
        d = rd.SETTLEMENTS[t]; cx = x + i*cw
        c.setFillColor(_c(TIER_COL.get(d.get("tier"), "#6b6257")))
        c.roundRect(cx + 2, y - h, cw - 4, h, 4, stroke=0, fill=1)
        c.setFont(SERIF_B, 9.5); c.setFillColor(Color(1, 1, 1)); c.drawString(cx + 9, y - 14, t)
        c.setFillColor(Color(1, 1, 1, 0.9)); c.setFont(SERIF, 7)
        c.drawString(cx + 9, y - 26, f"Tax {d.get('tax_income')}   Muster {d.get('muster_limit')}")
        c.drawString(cx + 9, y - 37, f"Reach {d.get('reach')}   Build {d.get('build_time')}t")
        if i < n - 1 and tiers[i] != "Hamlet" and tiers[i+1] != "Hamlet":
            c.setFillColor(_c("#8a8072")); c.setFont(SERIF_B, 12)
            c.drawCentredString(cx + cw, y - h/2 - 4, "\u203a")

def _ward_row(c, x, ytop, label, tiers, sub=None, gutter=78):
    """A settlement's row: left gutter label + one tagged ward slot per tier."""
    # gutter
    c.setFont(SERIF_B, 10); c.setFillColor(INK); c.drawString(x, ytop - SLOT_H/2 + 4, label)
    if sub:
        c.setFont(SERIF_I, 7); c.setFillColor(MUTE); c.drawString(x, ytop - SLOT_H/2 - 8, sub)
    for i, t in enumerate(tiers):
        sx = x + gutter + i*(SLOT_W + SLOT_GAP)
        c.setFillColor(SLOTBG); c.setStrokeColor(SLOTLINE); c.setLineWidth(0.8); c.setDash(3, 2)
        c.roundRect(sx, ytop - SLOT_H, SLOT_W, SLOT_H, 4, stroke=1, fill=1); c.setDash()
        if t:
            tag = t.upper(); c.setFont(SERIF_B, 6.4); tw = c.stringWidth(tag, SERIF_B, 6.4)
            c.setFillColor(_c(TIER_COL.get(rd.SETTLEMENTS[t].get("tier"), "#6b6257")))
            c.roundRect(sx + 5, ytop - 15, tw + 10, 11, 2.5, stroke=0, fill=1)
            c.setFillColor(Color(1, 1, 1)); c.drawString(sx + 10, ytop - 12.5, tag)
        c.setFont(SERIF_I, 7.5); c.setFillColor(MUTE)
        c.drawCentredString(sx + SLOT_W/2, ytop - SLOT_H/2 - 3, "ward")

def _wrap_po(c, text, maxw, font="Helvetica", size=5.0):
    out, cur = [], ""
    for wd in str(text).split():
        t = (cur + " " + wd).strip()
        if c.stringWidth(t, SERIF, size) <= maxw: cur = t
        else:
            if cur: out.append(cur)
            cur = wd
    if cur: out.append(cur)
    return out[:3]

def build_board(out):
    """Landscape Settlement Board: tier ladder once at top, then a 2x2 grid of
    settlement rows (3 Settlements + Hamlet). Slots = the pursuit tile (master)."""
    from reportlab.lib.pagesizes import landscape
    global SLOT_W, SLOT_H
    SLOT_W, SLOT_H = 37*MM, 50*MM            # matches the pursuit tile as it prints
    PW, PH = landscape(letter)               # 792 x 612
    c = canvas.Canvas(out, pagesize=(PW, PH))
    x = MX; y = PH - MY; w = PW - 2*MX

    c.setFillColor(INK); c.setFont(SERIF_B, 15); c.drawString(x, y - 13, "Settlement Board")
    c.setFont(SERIF_I, 8.5); c.setFillColor(MUTE)
    c.drawRightString(x + w, y - 12, "wards unlock left to right \u00b7 ward count = tier")
    y -= 22
    _ladder_strip(c, x, y, w, ["Hamlet", "Village", "Town", "City", "Metropolis"], h=48)
    y -= 48 + 20

    def panel(px, ptop, tiers):
        sy = ptop
        for i, t in enumerate(tiers):
            sx = px + i*(SLOT_W + SLOT_GAP)
            c.setFillColor(SLOTBG); c.setStrokeColor(SLOTLINE); c.setLineWidth(0.8); c.setDash(3, 2)
            c.roundRect(sx, sy - SLOT_H, SLOT_W, SLOT_H, 4, stroke=1, fill=1); c.setDash()
            if t:
                tag = t.upper(); c.setFont(SERIF_B, 6.4); tw = c.stringWidth(tag, SERIF_B, 6.4)
                c.setFillColor(_c(TIER_COL.get(rd.SETTLEMENTS[t].get("tier"), "#6b6257")))
                c.roundRect(sx + 5, sy - 15, tw + 10, 11, 2.5, stroke=0, fill=1)
                c.setFillColor(Color(1, 1, 1)); c.drawString(sx + 10, sy - 12.5, tag)
            c.setFont(SERIF_I, 7.5); c.setFillColor(MUTE)
            c.drawCentredString(sx + SLOT_W/2, sy - SLOT_H/2 - 3, "ward")

    panel_w = 3*SLOT_W + 2*SLOT_GAP
    col_x = [x, x + w - panel_w]             # flush to left and right edges
    row_top = [y, y - SLOT_H - 18]           # packed under the ladder; bottom trims off
    cells = [["Village", "Town", "City"],
             ["Village", "Town", "City"],
             ["Village", "Town", "City"],
             [None, None, None]]
    for i, tiers in enumerate(cells):
        r, cc = divmod(i, 2)
        panel(col_x[cc], row_top[r], tiers)

    # ---- bottom strip: Public Order spectrum across full width ----
    by = MY + 78
    c.setStrokeColor(FRAME); c.setLineWidth(0.8); c.line(x, by + 16, x + w, by + 16)
    c.setFont(SERIF_B, 11); c.setFillColor(INK); c.drawString(x, by, "Public Order")

    lo, hi = min(rd.PUBLIC_ORDER), max(rd.PUBLIC_ORDER)
    n = hi - lo
    y0 = by - 46
    cellw = w / (n + 1)
    for i, val in enumerate(range(lo, hi + 1)):
        cx0 = x + i*cellw
        if val < 0:    fill = "#9E2B25"
        elif val == 0: fill = "#efe9db"
        elif val >= 6: fill = "#B48A1E"
        else:          fill = "#5f7360"
        c.setFillColor(_c(fill)); c.setStrokeColor(SLOTLINE); c.setLineWidth(0.5)
        c.rect(cx0, y0, cellw, 24, stroke=1, fill=1)
        c.setFont(SERIF_B, 9); c.setFillColor(Color(1,1,1) if val != 0 else INK)
        c.drawCentredString(cx0 + cellw/2, y0 + 8, str(val))
        band = rd.PUBLIC_ORDER.get(val)
        nm = band[0] if isinstance(band, (tuple, list)) else None
        eff = band[1] if isinstance(band, (tuple, list)) and len(band) > 1 else None
        if nm:
            c.setFont(SERIF_B, 5.6); c.setFillColor(INK)
            c.drawCentredString(cx0 + cellw/2, y0 - 9, nm)
        if eff:
            c.setFont(SERIF, 5.0); c.setFillColor(MUTE)
            for j, ln in enumerate(_wrap_po(c, eff, cellw - 4)):
                c.drawCentredString(cx0 + cellw/2, y0 - 17 - j*6, ln)

    c.showPage(); c.save()
    print(f"settlement board -> {out}  (landscape, ladder + 2x2 + PO spectrum, slot {SLOT_W/MM:.0f}x{SLOT_H/MM:.0f}mm)")