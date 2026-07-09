#!/usr/bin/env python
# infra_board.py - landscape Infrastructure Board.
#   * shared tracker: every infrastructure has 4 pip guides so all players mark
#     what they own (empire-wide, build once)
#   * grouped by tier; effects table on the same page
# Data-driven from renown_data.INFRASTRUCTURE. Usage: python infra_board.py [out.pdf]
import sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
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
            except Exception: pass
            break

TIERS = ["Primitive", "Developed", "Sophisticated"]
TIER_COL = {"Primitive": "#6f7a52", "Developed": "#5f7360", "Sophisticated": "#4f6a72"}
INK = HexColor("#2b2620"); MUTE = HexColor("#6f6f77"); TAG = HexColor("#8a8072")
PARCH = HexColor("#f4efe4"); FRAME = HexColor("#c9bfa8"); LINE = HexColor("#e6e2d8")
SLOTBG = HexColor("#efe9db")

PW, PH = landscape(letter)
MX, MY = 28, 26
def _c(h): return HexColor(h)
def _clean(s): return " ".join(str(s or "").replace("**", "").split())

def wrap(c, text, font, size, maxw):
    out, cur = [], ""
    for w in str(text).split():
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= maxw: cur = t
        else:
            if cur: out.append(cur)
            cur = w
    if cur: out.append(cur)
    return out

def infra_row(c, x, y, w, name, tier, upkeep):
    col = _c(TIER_COL[tier]); rowh = 26
    c.setFillColor(SLOTBG); c.setStrokeColor(FRAME); c.setLineWidth(0.6)
    c.roundRect(x, y - rowh, w, rowh, 3, stroke=1, fill=1)
    c.setFillColor(col); c.rect(x, y - rowh, 4, rowh, stroke=0, fill=1)   # tier tab
    c.setFont(SERIF_B, 9); c.setFillColor(INK); c.drawString(x + 10, y - 12, name)
    c.setFont(SERIF, 6.5); c.setFillColor(TAG)
    c.drawString(x + 10, y - 21, f"upkeep {upkeep}" if upkeep else "free")
    # 4 player pip guides on the right
    c.setStrokeColor(col); c.setLineWidth(0.8)
    for k in range(4):
        px = x + w - 16 - k*15
        c.circle(px, y - rowh/2, 4.2, stroke=1, fill=0)

def draw_effects(c, x, ytop, w):
    """Two-column effects legend for all 12 infrastructure."""
    infra = [(n, d) for t in TIERS for n, d in rd.INFRASTRUCTURE.items() if d.get("tier") == t]
    c.setFont(SERIF_B, 11); c.setFillColor(INK); c.drawString(x, ytop, "Effects")
    colw = (w - 24) / 2
    xs = [x, x + colw + 24]
    half = (len(infra) + 1) // 2
    for col, group in enumerate((infra[:half], infra[half:])):
        yy = ytop - 14; xx = xs[col]
        for n, d in group:
            eff = _clean(d.get("empire_bonus"))
            req = d.get("requirement")
            reqs = "" if not req or req == "None" else f"  (needs {req})"
            c.setFont(SERIF_B, 7.5); c.setFillColor(_c(TIER_COL[d.get("tier")]))
            nw = c.stringWidth(n, SERIF_B, 7.5); c.drawString(xx, yy, n)
            body = eff + reqs
            c.setFont(SERIF, 7); c.setFillColor(HexColor("#3a3a42"))
            first = True; drawn = []; line = ""; avail = colw - nw - 6
            for wd in body.split():
                t = (line + " " + wd).strip()
                if c.stringWidth(t, SERIF, 7) <= (avail if first else colw): line = t
                else:
                    drawn.append((line, first)); first = False; line = wd; avail = colw
            drawn.append((line, first))
            for txt, fst in drawn:
                c.drawString((xx + nw + 5) if fst else xx, yy, txt); yy -= 8.6
            yy -= 2

def build(out):
    c = canvas.Canvas(out, pagesize=(PW, PH))
    x = MX; w = PW - 2*MX; y = PH - MY

    c.setFillColor(INK); c.setFont(SERIF_B, 16); c.drawString(x, y - 12, "Infrastructure Board")
    c.setFont(SERIF_I, 9); c.setFillColor(MUTE)
    c.drawRightString(x + w, y - 11, "empire-wide \u00b7 build once \u00b7 one pip per player who owns it")
    y -= 34

    # tracker: 3 tier columns, 4 infra each, 4 pips per infra
    colw = (w - 2*20) / 3
    xs = [x, x + colw + 20, x + 2*(colw + 20)]
    for ci, tier in enumerate(TIERS):
        cx = xs[ci]
        c.setFillColor(_c(TIER_COL[tier]))
        c.roundRect(cx, y - 18, colw, 18, 3, stroke=0, fill=1)
        c.setFont(SERIF_B, 10); c.setFillColor(Color(1,1,1)); c.drawString(cx + 8, y - 13, tier.upper())
        items = [(n, d) for n, d in rd.INFRASTRUCTURE.items() if d.get("tier") == tier]
        ry = y - 24
        for n, d in items:
            infra_row(c, cx, ry, colw, n, tier, d.get("upkeep", 0))
            ry -= 30
    y -= 18 + 4*30 + 16

    draw_effects(c, x, y, w)

    c.showPage(); c.save()
    print(f"infra board -> {out}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("cards", "infra_board.pdf")
    d = os.path.dirname(out)
    if d and not os.path.exists(d): os.makedirs(d, exist_ok=True)
    build(out)
