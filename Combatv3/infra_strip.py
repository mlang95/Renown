#!/usr/bin/env python
# infra_strip.py - infrastructure ownership grid. Names as column headers once
# (grouped by tier), one row of 12 check boxes per player. Fits many players/page.
# Effects live on the reference; this is the empire-wide build record.
# Usage:  python infra_strip.py [out.pdf] [players]     (default: cards/infra_strip.pdf, 6)
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
            except Exception:
                pass
            break

TIERS = ["Primitive", "Developed", "Sophisticated"]
TIER_COL = {"Primitive": "#6f7a52", "Developed": "#5f7360", "Sophisticated": "#4f6a72"}
PARCH = HexColor("#f4efe4"); FRAME = HexColor("#c9bfa8"); INK = HexColor("#2b2620")
MUTE = HexColor("#6f6f77"); BOX = HexColor("#9c917a"); BANDALT = HexColor("# efe9db".replace(" ", ""))
ROWALT = HexColor("#efe9db")

PAGE_W, PAGE_H = landscape(letter)
MX, MY = 26, 26

def _c(h): return HexColor(h)

def build(out, players=6):
    c = canvas.Canvas(out, pagesize=(PAGE_W, PAGE_H))
    c.setFillColor(INK); c.setFont(SERIF_B, 16); c.drawString(MX, PAGE_H - MY - 12, "Infrastructure")
    c.setFont(SERIF_I, 9); c.setFillColor(MUTE)
    c.drawString(MX + c.stringWidth("Infrastructure", SERIF_B, 16) + 8, PAGE_H - MY - 11,
                 "empire-wide \u00b7 build once \u00b7 check when owned  (effects: see reference)")

    infra = [(n, d) for t in TIERS for n, d in rd.INFRASTRUCTURE.items() if d.get("tier") == t]
    n = len(infra)                                   # 12
    label_w = 74
    grid_x = MX + label_w
    grid_w = PAGE_W - MX - grid_x
    cw = grid_w / n
    top = PAGE_H - MY - 28
    hdr_h = 46
    row_h = min(30, (top - hdr_h - MY) / players)

    # tier bands + names as column headers
    xi = grid_x
    # group tint behind each tier's 4 columns
    idx = 0
    for t in TIERS:
        cols = [1 for nm, d in infra if d.get("tier") == t]
        span = len(cols) * cw
        c.setFillColor(_c(TIER_COL[t])); c.setFillAlpha(0.16)
        c.rect(grid_x + idx*cw, top - hdr_h, span, hdr_h + row_h*players, stroke=0, fill=1)
        c.setFillAlpha(1)
        # tier label
        c.setFont(SERIF_B, 7.5); c.setFillColor(_c(TIER_COL[t]))
        c.drawCentredString(grid_x + idx*cw + span/2, top + 2, t.upper())
        idx += len(cols)

    # column names (wrapped to 2 lines), vertical divider ticks
    for i, (nm, d) in enumerate(infra):
        cx = grid_x + i*cw
        words = nm.split()
        if len(words) == 1: lines = [nm]
        else: lines = [words[0], " ".join(words[1:])]
        c.setFont(SERIF_B, 6.6); c.setFillColor(INK)
        ly = top - 10
        for ln in lines:
            c.drawCentredString(cx + cw/2, ly, ln); ly -= 7.6
        up = d.get("upkeep", 0)
        c.setFont(SERIF, 5.6); c.setFillColor(MUTE)
        c.drawCentredString(cx + cw/2, ly, f"u{up}" if up else "free")

    # player rows
    gy = top - hdr_h
    for r in range(players):
        ry = gy - r*row_h
        if r % 2 == 0:
            c.setFillColor(ROWALT); c.rect(MX, ry - row_h, PAGE_W - 2*MX, row_h, stroke=0, fill=1)
        c.setFont(SERIF_B, 9); c.setFillColor(INK)
        c.drawString(MX + 4, ry - row_h/2 - 3, f"Player {r+1}")
        for i in range(n):
            cx = grid_x + i*cw
            bs = 11
            c.setStrokeColor(BOX); c.setLineWidth(1.0)
            c.rect(cx + cw/2 - bs/2, ry - row_h/2 - bs/2, bs, bs, stroke=1, fill=0)
    # frame + column dividers
    c.setStrokeColor(FRAME); c.setLineWidth(0.8)
    c.rect(MX, gy - players*row_h, PAGE_W - 2*MX, hdr_h + players*row_h, stroke=1, fill=0)
    c.setStrokeColor(HexColor("#ddd6c6")); c.setLineWidth(0.4)
    for i in range(n + 1):
        cx = grid_x + i*cw
        c.line(cx, gy - players*row_h, cx, gy)
    c.line(grid_x, gy, grid_x, gy)

    # rules legend below the grid (full width, two columns)
    ly = gy - players*row_h - 16
    c.setFont(SERIF_B, 9); c.setFillColor(INK); c.drawString(MX, ly, "Effects")
    ly -= 12
    colw = (PAGE_W - 2*MX - 24) / 2
    xs = [MX, MX + colw + 24]
    half = (len(infra) + 1) // 2
    for col, group in enumerate((infra[:half], infra[half:])):
        yy = ly; xx = xs[col]
        for nm, d in group:
            eff = " ".join(str(d.get("empire_bonus", "")).replace("**", "").split())
            req = d.get("requirement")
            reqs = "" if not req or req == "None" else f"  (needs {req})"
            c.setFont(SERIF_B, 7); c.setFillColor(_c(TIER_COL[d.get("tier")]))
            nw = c.stringWidth(nm, SERIF_B, 7)
            c.drawString(xx, yy, nm)
            c.setFont(SERIF, 7); c.setFillColor(HexColor("#3a3a42"))
            body = eff + reqs
            avail = colw - nw - 6
            first = True; tx = xx + nw + 5; line = ""
            words = body.split(); drawn = []
            for wd in words:
                t = (line + " " + wd).strip()
                if c.stringWidth(t, SERIF, 7) <= (avail if first else colw): line = t
                else:
                    drawn.append((line, first)); first = False; line = wd; avail = colw
            drawn.append((line, first))
            for txt, fst in drawn:
                c.drawString(tx if fst else xx, yy, txt); yy -= 8.6
            yy -= 2

    c.showPage(); c.save()
    print(f"infra grid -> {out}  ({players} players x 12 infrastructure)")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("cards", "infra_strip.pdf")
    players = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    dd = os.path.dirname(out)
    if dd and not os.path.exists(dd): os.makedirs(dd, exist_ok=True)
    build(out, players)
