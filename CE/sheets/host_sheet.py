#!/usr/bin/env python
# host_sheet.py - Host Card, front & back (landscape Letter), generated from
# renown_data so the drift-prone values (camp size, army threshold, growth,
# Cunning trigger, trade multiplier, spawn rule) can never go stale. Mirrors the
# font/geometry conventions of playstyle_reference.py.
# Usage:  python host_sheet.py [out.pdf]     (default: cards/host_sheet.pdf)
import sys, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import renown_data as rd

# ---- fonts (EB Garamond; Helvetica fallback) ----
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

# ---- palette (matches playstyle_reference) ----
INK   = HexColor("#26262e"); MUTE = HexColor("#7a7a82"); TAG = HexColor("#a59a82")
CUN   = HexColor("#1c1c20"); GOLD = HexColor("#C6A024"); RED = HexColor("#9E2B25")
HEADBG = HexColor("#2b2b32"); BOXBG = HexColor("#faf8f3"); GRIDC = HexColor("#d9d4c8")
LINE  = HexColor("#efece4"); META = HexColor("#33333b")

# ---- data pulled live from renown_data (the whole point) ----
CAMP_START = rd.BANDIT_CAMP_START
ARMY_THRESH = rd.BANDIT_ARMY_THRESHOLD
GROWTH = rd.BANDIT_GROWTH_PER_ERA
BEH = rd.BANDIT_BEHAVIOR
TR = rd.TRADE_RULES
SPAWN = rd.BANDITS.get("Spawn a Bandit Camp", "")
DOMVAL = rd.BANDITS.get("Bandit Domain Value", "")
# Cunning-trigger threshold parsed from the behavior text so it tracks the data.
import re as _re
_m = _re.search(r"(\d+)\+?\s*retinues", BEH.get("Cunning Roll", ""))
CUNNING_MIN = _m.group(1) if _m else "?"
# Armament-by-era: use renown_data if present, else a local fallback (add
# BANDIT_ARMAMENT_BY_ERA to renown_data to make this single-source too).
ARMAMENT = getattr(rd, "BANDIT_ARMAMENT_BY_ERA", {
    "Founding":  "Cudgels + Cloth",
    "Ascension": "Arming Swords + Kite Shields + Leather",
    "Eminence":  "Halberds + Chainmail",
    "Zenith":    "Battle Axes + Full Plate",
})

PAGE_W, PAGE_H = landscape(letter)     # 792 x 612
MX, MT, MB = 34, 26, 24

def wrap(c, text, font, size, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def header(c, title, subtitle):
    ty = PAGE_H - MT - 14
    c.setFillColor(INK); c.setFont(SERIF_B, 20); c.drawString(MX, ty, "RENOWN")
    w = c.stringWidth("RENOWN", SERIF_B, 20)
    c.setFont(SERIF_I, 12); c.setFillColor(MUTE)
    c.drawString(MX + w + 8, ty + 1, "\u00b7 " + title)
    c.setFont(SERIF_I, 9); c.setFillColor(MUTE)
    c.drawRightString(PAGE_W - MX, ty + 3, subtitle)
    ry = PAGE_H - MT - 24
    c.setStrokeColor(INK); c.setLineWidth(1.6); c.line(MX, ry, PAGE_W - MX, ry)
    return ry - 10

class Col:
    """A flowing column that draws boxed sections top-down."""
    def __init__(self, c, x, w, top, bottom):
        self.c, self.x, self.w, self.y, self.bottom = c, x, w, top, bottom

    def box(self, title, draw, est_h):
        c = self.c
        if self.y - est_h < self.bottom:   # (single-page layout: sections are tuned to fit)
            pass
        top = self.y
        # header bar
        c.setFillColor(HEADBG); c.roundRect(self.x, top - 15, self.w, 15, 3, stroke=0, fill=1)
        c.setFillColor(Color(1, 1, 1)); c.setFont(SERIF_B, 9.5)
        c.drawString(self.x + 7, top - 11, title)
        # body
        by = top - 15 - 8
        end_y = draw(c, self.x + 8, by, self.w - 16)
        # border around whole section
        c.setStrokeColor(GRIDC); c.setLineWidth(0.8)
        c.roundRect(self.x, end_y - 4, self.w, (top - (end_y - 4)), 3, stroke=1, fill=0)
        self.y = end_y - 4 - 10
        return self.y

def bullets(c, x, y, w, items, font=None, size=8.4, lead=10.4, gap=2, numbered=False):
    font = font or SERIF
    for i, it in enumerate(items, 1):
        mark = f"{i}." if numbered else "\u2022"
        c.setFont(SERIF_B if numbered else SERIF, size); c.setFillColor(META)
        c.drawString(x, y, mark)
        lines = wrap(c, it, font, size, w - 14)
        c.setFont(font, size); c.setFillColor(META)
        for ln in lines:
            c.drawString(x + 14, y, ln); y -= lead
        y -= gap
    return y

def keyval(c, x, y, w, rows, size=8.4, lead=10.4):
    for tag, val in rows:
        c.setFont(SERIF_B, 6.6); c.setFillColor(TAG); c.drawString(x, y, tag.upper())
        c.setFont(SERIF, size); c.setFillColor(META)
        yy = y
        for ln in wrap(c, val, SERIF, size, w - 62):
            c.drawString(x + 62, yy, ln); yy -= lead
        y = min(y - lead, yy) - 2
    return y

def table(c, x, y, w, headers, rows, size=8.2, rh=12.6, weights=None):
    n = len(headers)
    if weights:
        tot = float(sum(weights)); xs = []; acc = 0
        for wt in weights: xs.append(x + w*acc/tot); acc += wt
        widths = [w*wt/tot for wt in weights]
    else:
        xs = [x + i*(w/n) for i in range(n)]; widths = [w/n]*n
    c.setFillColor(LINE); c.rect(x, y - rh + 3, w, rh, stroke=0, fill=1)
    c.setFont(SERIF_B, size); c.setFillColor(INK)
    for i, h in enumerate(headers):
        c.drawString(xs[i] + 3, y - rh + 7, h)
    y -= rh
    for row in rows:
        # measure wrapped height of this row across columns
        celllines = [wrap(c, str(row[i]), SERIF, size, widths[i]-6) for i in range(n)]
        rows_h = max(len(cl) for cl in celllines) * (size + 1.6) + 4
        c.setFont(SERIF, size); c.setFillColor(META)
        for i, cl in enumerate(celllines):
            yy = y - size - 1
            for ln in cl:
                c.drawString(xs[i] + 3, yy, ln); yy -= (size + 1.6)
        c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(x, y - rows_h + 2, x + w, y - rows_h + 2)
        y -= rows_h
    return y

# ---------------- SIDE A: duties + trade ----------------
def turn_flow(c, x, y_top, w):
    """Full-width horizontal turn-sequence flowchart. Returns bottom y."""
    phases = [
        ("EMPIRE", "start of turn", "Activate Standing effects \u00b7 apply Season \u00b7 tick timers \u00b7 gain Income, Influence & Envoys"),
        ("COUNCIL", "", "Vote a Domain (clockwise; Host breaks ties) \u00b7 each resolves one free action of it"),
        ("ENVOY", "", "Declare envoys \u2192 Diplomacy first, then Domains (Prowess \u2192 Cunning \u2192 Piety \u2192 Industry)"),
        ("BATTLE", "", "Resolve any Skirmishes, Sieges, and Battles declared this turn"),
        ("REST", "end of turn", "Cleanup \u00b7 Season +1 \u00b7 score +1 Renown \u00b7 spend 1 Domain Point \u00b7 pass Host clockwise"),
    ]
    n = len(phases)
    arrow = 13
    bw = (w - arrow*(n-1)) / n
    bh = 62
    ty = y_top
    c.setFont(SERIF_B, 6.6); c.setFillColor(TAG)
    c.drawString(x, ty + 6, "TURN SEQUENCE")
    for i, (name, note, desc) in enumerate(phases):
        bx = x + i*(bw + arrow)
        by = ty - bh
        c.setFillColor(BOXBG); c.setStrokeColor(INK); c.setLineWidth(1.0)
        c.roundRect(bx, by, bw, bh, 4, stroke=1, fill=1)
        c.setFillColor(INK); c.setLineWidth(3.2)
        c.setStrokeColor(HexColor("#8a6d1a") if name in ("EMPIRE","REST") else INK)
        c.line(bx, by+bh-1.4, bx+bw, by+bh-1.4)   # top accent bar
        c.setFont(SERIF_B, 8.4); c.setFillColor(INK)
        c.drawString(bx+6, by+bh-13, name)
        if note:
            c.setFont(SERIF_I, 6.0); c.setFillColor(MUTE)
            c.drawRightString(bx+bw-5, by+bh-12, note)
        c.setFont(SERIF, 6.6); c.setFillColor(META)
        yy = by+bh-24
        for ln in wrap(c, desc, SERIF, 6.6, bw-10):
            c.drawString(bx+5, yy, ln); yy -= 8.0
        if i < n-1:   # arrow to next
            ax = bx + bw; ay = by + bh/2
            c.setStrokeColor(HexColor("#8a6d1a")); c.setLineWidth(1.6)
            c.line(ax+1, ay, ax+arrow-3, ay)
            c.setFillColor(HexColor("#8a6d1a"))
            c.saveState(); c.translate(ax+arrow-3, ay)
            p = c.beginPath(); p.moveTo(0,0); p.lineTo(-3.4,2.2); p.lineTo(-3.4,-2.2); p.close()
            c.drawPath(p, fill=1, stroke=0); c.restoreState()
    return ty - bh

def side_a(c):
    top = header(c, "Host Card", "Side A \u00b7 held by the current Host \u00b7 passes clockwise each Rest Phase")
    gap = 14
    colw = (PAGE_W - 2*MX - gap) / 2
    L = Col(c, MX, colw, top, MB)
    R = Col(c, MX + colw + gap, colw, top, MB)

    def duties(c, x, y, w):
        c.setFont(SERIF_I, 8.2); c.setFillColor(MUTE)
        for ln in wrap(c, "You run the parts of the game that aren't any single player's turn, in order:", SERIF_I, 8.2, w):
            c.drawString(x, y, ln); y -= 10
        y -= 2
        return bullets(c, x, y, w, [
            "Trade Income \u2014 calculate and distribute (see below).",
            "Bandit Mechanics \u2014 grow, convert, act, spawn (Side B).",
            "Break ties \u2014 Council vote, Bandit Army targets, anything not explicitly resolved.",
            "Resolve timers \u2014 confirm every player advances their Build / Repair / Truce / Siege / Muster / Sack / Capture timers in the Empire Phase.",
        ], numbered=True)
    L.box("Your Job Each Turn", duties, 120)

    def passing(c, x, y, w):
        txt = ("After your Rest Phase, pass the Host token (and this card) clockwise. "
               "Skip all Host duties in Spring \u2014 no Host, Bandits, Trade Income, Council, or "
               "Diplomacy actions; Spring grants +1 Envoy instead.")
        c.setFont(SERIF, 8.4); c.setFillColor(META)
        for ln in wrap(c, txt, SERIF, 8.4, w):
            c.drawString(x, y, ln); y -= 10.4
        return y - 2
    L.box("Passing the Host", passing, 60)

    def trade(c, x, y, w):
        y = keyval(c, x, y, w, [
            ("Who", "Both players border each other, both have active Dirt Roads "
                    "(or a faction/spec exception), and a signed Trade Agreement."),
            ("Income", f"For each Trade Agreement, BOTH players gain {TR['income_per_craft']} \u00d7 the Host's Craft X."),
        ])
        y -= 2
        c.setFont(SERIF_B, 6.6); c.setFillColor(TAG); c.drawString(x, y, "WHEN IT FLOWS")
        y -= 10
        y = bullets(c, x, y, w, [
            "Just signed: the player who did NOT perform Sign Treaty gets income the next time they are Host; both flow normally thereafter.",
            "Just ended: the player who ended the treaty gets income the next time they are Host, then it stops.",
            f"No trade income in {TR['no_trade_season']}. Tax is collected in {TR['tax_season']}.",
        ], size=8.2, lead=10.0)
        return y
    R.box("Trade Income", trade, 150)

    def ties(c, x, y, w):
        return table(c, x, y, w, ["Situation", "Resolution"], [
            ["Council vote tied", "Host casts deciding vote"],
            ["Bandit Army equal targets", "Host chooses"],
            ["Players tied for \u2018highest X\u2019", "Host chooses"],
            ["Spawn placement ambiguous", "Apply rules; if still tied, Host chooses"],
        ])
    R.box("Quick Tie-Breakers", ties, 90)

    # full-width turn sequence flowchart across the bottom
    turn_flow(c, MX, MB + 78, PAGE_W - 2*MX)

# ---------------- SIDE B: bandit mechanics ----------------
def side_b(c):
    top = header(c, "Host Card", "Side B \u00b7 Bandit Mechanics \u00b7 resolved by the Host after Trade Income")
    gap = 14
    colw = (PAGE_W - 2*MX - gap) / 2
    L = Col(c, MX, colw, top, MB)
    R = Col(c, MX + colw + gap, colw, top, MB)

    def order(c, x, y, w):
        return bullets(c, x, y, w, [
            "Grow existing Bandit Camps (table at right).",
            f"Convert any Camp at {ARMY_THRESH}+ retinues into a Bandit Army.",
            f"Act \u2014 each Camp/Army of {CUNNING_MIN}+ retinues performs a Cunning Action (d3); each Bandit Army performs a Move.",
            SPAWN,
        ], numbered=True, size=8.4)
    L.box("Phase Order", order, 90)

    def cunning(c, x, y, w):
        c.setFont(SERIF, 8.4); c.setFillColor(META)
        for ln in wrap(c, DOMVAL, SERIF, 8.4, w):
            c.drawString(x, y, ln); y -= 10.4
        y -= 3
        c.setFont(SERIF_B, 6.6); c.setFillColor(TAG)
        c.drawString(x, y, f"CUNNING ACTION \u2014 CAMPS/ARMIES OF {CUNNING_MIN}+ (ROLL D3)"); y -= 10
        y = bullets(c, x, y, w, ["1 \u2014 Intercept Caravan", "2 \u2014 Raze", "3 \u2014 Destabilize"],
                    size=8.4, lead=10.0, gap=0)
        y -= 3
        c.setFont(SERIF_I, 7.8); c.setFillColor(MUTE)
        for ln in wrap(c, "All players Abstain Bandit actions; innate modifiers can still apply and may cause a Fail.", SERIF_I, 7.8, w):
            c.drawString(x, y, ln); y -= 9.6
        return y
    L.box("Cunning & Domain Value", cunning, 120)

    def army(c, x, y, w):
        c.setFont(SERIF, 8.4); c.setFillColor(META)
        for ln in wrap(c, BEH.get("Army Behavior", ""), SERIF, 8.4, w):
            c.drawString(x, y, ln); y -= 10.4
        y -= 3
        c.setFont(SERIF_B, 6.6); c.setFillColor(TAG); c.drawString(x, y, "ATTACKING A CAMP"); y -= 10
        c.setFont(SERIF, 8.4); c.setFillColor(META)
        for ln in wrap(c, BEH.get("Attacking", ""), SERIF, 8.4, w):
            c.drawString(x, y, ln); y -= 10.4
        return y
    L.box("Bandit Army & Attacking", army, 120)

    def growth(c, x, y, w):
        rows = [[era, f"+{g}"] for era, g in GROWTH.items()]
        y = table(c, x, y, w, ["Realm Era", "Retinues / turn"], rows)
        y -= 4
        c.setFont(SERIF_I, 7.8); c.setFillColor(MUTE)
        for ln in wrap(c, f"New Camps start at {CAMP_START} retinues. Camps and Armies grow each turn but never exceed {ARMY_THRESH}; a Camp becomes a Bandit Army at {ARMY_THRESH}. After casualties they regrow toward {ARMY_THRESH}.", SERIF_I, 7.8, w):
            c.drawString(x, y, ln); y -= 9.6
        return y
    R.box("Growth Table", growth, 100)

    def armament(c, x, y, w):
        rows = [[era, eq] for era, eq in ARMAMENT.items()]
        return table(c, x, y, w, ["Realm Era", "Equipment"], rows, size=7.8)
    R.box("Armament by Realm Era", armament, 90)

    def domval(c, x, y, w):
        rows = [
            ["Camp start size", f"{CAMP_START} retinues"],
            ["Becomes an Army", f"{ARMY_THRESH}+ retinues"],
            ["Cunning trigger", f"{CUNNING_MIN}+ retinues"],
            ["Domain Value", "+2 Cunning & +2 Prowess per 5 retinues"],
        ]
        return table(c, x, y, w, ["Key value", "Current"], rows, size=8.0)
    R.box("Key Bandit Values", domval, 90)

def one_page(c):
    top = header(c, "Host Card", "Turn sequence \u00b7 Host duties \u00b7 Bandit mechanics")
    flow_bot = turn_flow(c, MX, top - 4, PAGE_W - 2*MX)

    gap = 12
    colw = (PAGE_W - 2*MX - 2*gap) / 3
    ctop = flow_bot - 14
    C1 = Col(c, MX, colw, ctop, MB)
    C2 = Col(c, MX + colw + gap, colw, ctop, MB)
    C3 = Col(c, MX + 2*(colw + gap), colw, ctop, MB)

    def duties(c, x, y, w):
        return bullets(c, x, y, w, [
            "Trade Income \u2014 calculate & distribute (below).",
            "Bandit Mechanics \u2014 grow, convert, act, spawn.",
            "Break ties \u2014 Council vote, Bandit targets, anything unresolved.",
        ], numbered=True, size=8.0, lead=9.8)
    C1.box("Your Job Each Turn", duties, 0)

    def passing(c, x, y, w):
        txt = ("Pass the Host token clockwise after your Rest Phase. No Host in Spring \u2014 "
               "no Bandits, Trade Income, or Council; Spring grants +1 Envoy instead.")
        c.setFont(SERIF, 8.0); c.setFillColor(META)
        for ln in wrap(c, txt, SERIF, 8.0, w):
            c.drawString(x, y, ln); y -= 9.8
        return y - 2
    C1.box("Passing the Host", passing, 0)

    def ties(c, x, y, w):
        return table(c, x, y, w, ["Situation", "Resolution"], [
            ["Council vote tied", "Host votes"],
            ["Bandit equal targets", "Host chooses"],
            ["Tied for \u2018highest X\u2019", "Host chooses"],
            ["Spawn ambiguous", "Rules, else Host"],
        ], size=7.6, weights=[1.15, 1])
    C1.box("Quick Tie-Breakers", ties, 0)

    def trade(c, x, y, w):
        y = keyval(c, x, y, w, [
            ("Who", "Both border each other, both have active Dirt Roads (or an exception), and a signed Trade Agreement."),
            ("Income", f"Per Trade Agreement, BOTH gain {TR['income_per_craft']} \u00d7 the Host's Craft X."),
        ], size=7.8, lead=9.6)
        y -= 2
        c.setFont(SERIF_B, 6.4); c.setFillColor(TAG); c.drawString(x, y, "WHEN IT FLOWS"); y -= 9
        y = bullets(c, x, y, w, [
            "Just signed: the player who did NOT sign gets income next time they Host; both flow after.",
            "Just ended: the ender gets income next Host turn, then it stops.",
            f"No income in {TR['no_trade_season']}. Tax collected in {TR['tax_season']}.",
        ], size=7.6, lead=9.2)
        return y
    C2.box("Trade Income", trade, 0)

    def order(c, x, y, w):
        return bullets(c, x, y, w, [
            "Grow existing Bandit Camps (table \u2192).",
            f"Convert any Camp at {ARMY_THRESH}+ retinues into a Bandit Army.",
            f"Act \u2014 each Camp/Army of {CUNNING_MIN}+ performs a Cunning Action (d3); each Army performs a Move.",
            SPAWN,
        ], numbered=True, size=7.8, lead=9.6)
    C2.box("Bandit Phase Order", order, 0)

    def domval(c, x, y, w):
        return table(c, x, y, w, ["Key value", "Current"], [
            ["Camp start", f"{CAMP_START} retinues"],
            ["Becomes Army", f"{ARMY_THRESH}+ retinues"],
            ["Cunning trigger", f"{CUNNING_MIN}+ retinues"],
            ["Domain Value", "+2 Cunning & +2 Prowess / 5 retinues"],
        ], size=7.6, weights=[1, 1.3])
    C2.box("Key Bandit Values", domval, 0)

    def cunning(c, x, y, w):
        c.setFont(SERIF_B, 6.4); c.setFillColor(TAG)
        c.drawString(x, y, f"CUNNING ACTION \u2014 {CUNNING_MIN}+ RETINUES (D3)"); y -= 9
        y = bullets(c, x, y, w, ["1 \u2014 Intercept Caravan", "2 \u2014 Raze", "3 \u2014 Destabilize"],
                    size=7.8, lead=9.2, gap=0)
        y -= 2
        c.setFont(SERIF_I, 7.2); c.setFillColor(MUTE)
        for ln in wrap(c, "All players Abstain Bandit actions; innate modifiers can still apply and may Fail.", SERIF_I, 7.2, w):
            c.drawString(x, y, ln); y -= 8.8
        return y
    C3.box("Cunning Actions", cunning, 0)

    def army(c, x, y, w):
        c.setFont(SERIF, 7.8); c.setFillColor(META)
        for ln in wrap(c, BEH.get("Army Behavior", ""), SERIF, 7.8, w):
            c.drawString(x, y, ln); y -= 9.4
        y -= 2
        c.setFont(SERIF_B, 6.4); c.setFillColor(TAG); c.drawString(x, y, "ATTACKING A CAMP"); y -= 9
        c.setFont(SERIF, 7.8); c.setFillColor(META)
        for ln in wrap(c, BEH.get("Attacking", ""), SERIF, 7.8, w):
            c.drawString(x, y, ln); y -= 9.4
        return y
    C3.box("Bandit Army & Attacking", army, 0)

    def growth(c, x, y, w):
        rows = [[era, f"+{GROWTH[era]}", ARMAMENT.get(era, "")] for era in GROWTH]
        y = table(c, x, y, w, ["Era", "Growth", "Armament"], rows, size=7.4, weights=[1.1, 0.8, 3.1])
        y -= 3
        c.setFont(SERIF_I, 7.0); c.setFillColor(MUTE)
        for ln in wrap(c, f"New Camps start at {CAMP_START}; grow each turn but never exceed {ARMY_THRESH} (a Camp becomes an Army at {ARMY_THRESH}). Growth is retinues/turn.", SERIF_I, 7.0, w):
            c.drawString(x, y, ln); y -= 8.6
        return y
    C3.box("Growth & Armament by Era", growth, 0)


def build(out):
    c = canvas.Canvas(out, pagesize=(PAGE_W, PAGE_H))
    one_page(c); c.showPage()
    c.save()
    print("host sheet ->", out)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("cards", "host_sheet.pdf")
    d = os.path.dirname(out)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    build(out)