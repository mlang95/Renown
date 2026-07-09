#!/usr/bin/env python
# domain_board.py - landscape Domain Standing Board.
#   * 4 Domain tracks 1-10 (tier marks: Rising 3, Established 6, Sovereign 10)
#   * Renown track 0-30 with Era demarcations (Founding/Ascension/Eminence/Zenith)
#   * Domain standing definitions + Era standing table
# Data-driven from renown_data. Usage: python domain_board.py [out.pdf]
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

DOMAINS = ["Industry", "Prowess", "Cunning", "Piety"]
DOMC = {"Industry": "#2E5A8C", "Prowess": "#9E2B25", "Cunning": "#3a3a42", "Piety": "#C6A024"}
ERA_COL = ["#7d7566", "#6f7a52", "#5f7360", "#5a4f72"]
INK = HexColor("#2b2620"); MUTE = HexColor("#6f6f77"); TAG = HexColor("#8a8072")
PARCH = HexColor("#f4efe4"); FRAME = HexColor("#c9bfa8"); LINE = HexColor("#e6e2d8")

PW, PH = landscape(letter)
MX, MY = 28, 26
def _c(h): return HexColor(h)

# tier thresholds on the 1-10 domain track
TIERS = [(3, "Rising"), (6, "Established"), (10, "Sovereign")]

TIER_COL = {"Primitive": "#6f7a52", "Developed": "#5f7360", "Sophisticated": "#4f6a72"}
SLOTBG = HexColor("#efe9db")

def infra_tracker(c, x, y, w):
    """Shared infrastructure tracker with inline effect text (markers sit on the row)."""
    c.setFont(SERIF_B, 11); c.setFillColor(INK)
    c.drawString(x, y, "Infrastructure")
    c.setFont(SERIF_I, 8); c.setFillColor(MUTE)
    c.drawString(x + c.stringWidth("Infrastructure", SERIF_B, 11) + 8, y, "empire-wide \u00b7 build once")
    y -= 11
    tiers = ["Primitive", "Developed", "Sophisticated"]
    colw = (w - 2*18) / 3
    xs = [x, x + colw + 18, x + 2*(colw + 18)]
    efs = 5.8
    for ci, tier in enumerate(tiers):
        cx = xs[ci]
        c.setFillColor(_c(TIER_COL[tier])); c.roundRect(cx, y - 13, colw, 13, 2, stroke=0, fill=1)
        c.setFont(SERIF_B, 7.5); c.setFillColor(Color(1,1,1)); c.drawString(cx + 6, y - 10, tier.upper())
        ry = y - 15
        for n, d in [(n, d) for n, d in rd.INFRASTRUCTURE.items() if d.get("tier") == tier]:
            up = d.get("upkeep", 0)
            eff = " ".join(str(d.get("empire_bonus", "")).replace("**", "").split())
            elines = wrap(c, eff, SERIF, efs, colw - 12)
            rh = max(12, 9.5 + len(elines) * (efs + 1.0))
            c.setFillColor(SLOTBG); c.setStrokeColor(FRAME); c.setLineWidth(0.5)
            c.roundRect(cx, ry - rh, colw, rh, 2, stroke=1, fill=1)
            c.setFillColor(_c(TIER_COL[tier])); c.rect(cx, ry - rh, 3, rh, stroke=0, fill=1)
            c.setFont(SERIF_B, 6.8); c.setFillColor(INK); c.drawString(cx + 8, ry - 7.5, n)
            c.setFont(SERIF, 5.4); c.setFillColor(TAG)
            c.drawRightString(cx + colw - 5, ry - 7.5, f"u{up}" if up else "free")
            ty = ry - 14
            c.setFont(SERIF, efs); c.setFillColor(HexColor("#3a3a42"))
            for ln in elines:
                c.drawString(cx + 8, ty, ln); ty -= efs + 1.0
            ry -= rh + 2.2
    return ry

def _wrap_runs(c, runs, size, maxw):
    """runs = [(text,bold),...] -> list of lines, each a list of (word,bold)."""
    words = []
    for text, bold in runs:
        for wd in str(text).split():
            words.append((wd, bold))
    lines, cur, curw = [], [], 0
    for wd, bold in words:
        fnt = SERIF_B if bold else SERIF
        ww = c.stringWidth(wd + " ", fnt, size)
        if curw + ww > maxw and cur:
            lines.append(cur); cur, curw = [], 0
        cur.append((wd, bold)); curw += ww
    if cur: lines.append(cur)
    return lines

def _cell_lines(c, emp, cmb, size, maxw):
    """Empire effect (bold before ':') then combat effect (bold) on a new line."""
    lines = []
    if emp:
        if ":" in emp:
            pre, post = emp.split(":", 1)
            runs = [(pre + ":", True), (post.strip(), False)]
        else:
            runs = [(emp, False)]
        lines += _wrap_runs(c, runs, size, maxw)
    if cmb:
        lines += _wrap_runs(c, [(cmb, True)], size, maxw)
    return lines

def draw_def_table(c, x, ytop, w, colw, data, fs=6.4):
    c.setFont(SERIF_B, 11); c.setFillColor(INK); c.drawString(x, ytop, "Domain Standing Effects")
    headers = ["Domain", "Rising (3)", "Established (6)", "Sovereign (10)"]
    y = ytop - 14
    c.setFillColor(_c("#5f5647")); c.rect(x, y - 14, w, 14, stroke=0, fill=1)
    cx = x; c.setFont(SERIF_B, 7); c.setFillColor(Color(1,1,1))
    for j, h in enumerate(headers):
        c.drawString(cx + 3, y - 10, h); cx += colw[j]
    y -= 14
    lh = fs + 1.6
    for dom, tiers in data:
        cells = [None] + [_cell_lines(c, emp, cmb, fs, colw[j+1] - 6) for j, (emp, cmb) in enumerate(tiers)]
        rh = max(len(cl) for cl in cells[1:]) * lh + 5
        cx = x; c.setStrokeColor(LINE); c.setLineWidth(0.4)
        # domain label cell
        c.rect(cx, y - rh, colw[0], rh, stroke=1, fill=0)
        c.setFont(SERIF_B, fs + 0.5); c.setFillColor(_c(DOMC.get(dom, "#2b2620")))
        c.drawString(cx + 3, y - fs - 2, dom); cx += colw[0]
        for j in range(3):
            c.rect(cx, y - rh, colw[j+1], rh, stroke=1, fill=0)
            ty = y - fs - 2
            for line in cells[j+1]:
                lx = cx + 3
                for wd, bold in line:
                    c.setFont(SERIF_B if bold else SERIF, fs)
                    c.setFillColor(_c("#3a3a42") if bold else INK)
                    c.drawString(lx, ty, wd)
                    lx += c.stringWidth(wd + " ", SERIF_B if bold else SERIF, fs)
                ty -= lh
            cx += colw[j+1]
        y -= rh
    return y

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

def domain_track(c, x, y, w, dom):
    col = _c(DOMC[dom]); n = 10
    lab_w = 66
    cellw = (w - lab_w) / n
    H = 26                                   # markers sit on the cell; no pip guides
    c.setFont(SERIF_B, 11); c.setFillColor(col); c.drawString(x, y - 15, dom)
    tset = {t: nm for t, nm in TIERS}
    for i in range(1, n + 1):
        cx = x + lab_w + (i - 1) * cellw
        shade = 0.14 + 0.5 * (i / n)
        c.setFillColor(Color(col.red, col.green, col.blue, shade))
        c.setStrokeColor(FRAME); c.setLineWidth(0.5)
        c.rect(cx, y - H, cellw, H, stroke=1, fill=1)
        c.setFont(SERIF_B, 8); c.setFillColor(Color(1,1,1) if i > 5 else INK)
        c.drawCentredString(cx + cellw/2, y - H/2 - 3, str(i))
        if i in tset:                        # tier threshold marker
            c.setStrokeColor(col); c.setLineWidth(2)
            c.rect(cx, y - H, cellw, H, stroke=1, fill=0)
            c.setFont(SERIF_B, 6); c.setFillColor(col)
            c.drawCentredString(cx + cellw/2, y - H - 8, tset[i])

def renown_track(c, x, y, w):
    n = 30
    cellw = w / n
    eras = list(rd.ERAS.items())            # Founding0 Ascension8 Eminence18 Zenith30
    thresh = [(nm, e["renown"]) for nm, e in eras]
    def era_at(v):
        cur = eras[0][0]
        for nm, e in eras:
            if v >= e["renown"]: cur = nm
        return cur
    order = [nm for nm, _ in eras]
    c.setFont(SERIF_B, 12); c.setFillColor(INK); c.drawString(x, y + 6, "Renown")
    for v in range(1, n + 1):
        cx = x + (v - 1) * cellw
        ei = order.index(era_at(v))
        c.setFillColor(_c(ERA_COL[ei])); c.setStrokeColor(FRAME); c.setLineWidth(0.4)
        c.rect(cx, y - 20, cellw, 20, stroke=1, fill=1)
        c.setFont(SERIF_B, 7); c.setFillColor(Color(1,1,1))
        c.drawCentredString(cx + cellw/2, y - 13, str(v))
    # era demarcation lines + labels at thresholds
    for i, (nm, rv) in enumerate(thresh):
        mx = x + max(0, rv) * cellw
        c.setStrokeColor(_c("#3a3a42")); c.setLineWidth(1.4)
        c.line(mx, y - 24, mx, y + 2)
        c.setFont(SERIF_B, 8); c.setFillColor(_c(ERA_COL[i]))
        c.drawString(mx + 2, y - 33, f"{nm} ({rv})")

def draw_table(c, x, ytop, w, headers, rows, colw, title, head_col, fs=7, hfs=8):
    c.setFont(SERIF_B, 11); c.setFillColor(INK); c.drawString(x, ytop, title)
    y = ytop - 14
    # header
    c.setFillColor(_c(head_col)); c.rect(x, y - 14, w, 14, stroke=0, fill=1)
    cx = x
    c.setFont(SERIF_B, hfs); c.setFillColor(Color(1,1,1))
    for j, h in enumerate(headers):
        c.drawString(cx + 3, y - 10, h); cx += colw[j]
    y -= 14
    for r in rows:
        # measure row height by tallest wrapped cell
        cellsw = [wrap(c, r[j], SERIF, fs, colw[j] - 6) for j in range(len(r))]
        rh = max(len(cw) for cw in cellsw) * (fs + 1.5) + 4
        cx = x
        c.setStrokeColor(LINE); c.setLineWidth(0.4)
        for j in range(len(r)):
            c.rect(cx, y - rh, colw[j], rh, stroke=1, fill=0)
            c.setFont(SERIF_B if j == 0 else SERIF, fs)
            c.setFillColor(_c(DOMC.get(r[0], "#2b2620")) if j == 0 else INK)
            ty = y - fs - 1
            for ln in cellsw[j]:
                c.drawString(cx + 3, ty, ln); ty -= fs + 1.5
            cx += colw[j]
        y -= rh
    return y

def _seasons_strip(c, x, y, w):
    """Seasons as a full-width 4-cell strip (name + effect)."""
    c.setFont(SERIF_B, 11); c.setFillColor(INK); c.drawString(x, y, "Seasons")
    y -= 12
    seasons = list(rd.SEASONS.items())
    cw = w / 4
    SEA_COL = {"Winter": "#4a6a8c", "Spring": "#4f7a3a", "Summer": "#b5651a", "Fall": "#8a5a2a"}
    h = 38
    for i, (nm, s) in enumerate(seasons):
        cx = x + i * cw
        col = _c(SEA_COL.get(nm, "#4f6a52"))
        c.setFillColor(SLOTBG); c.setStrokeColor(FRAME); c.setLineWidth(0.5)
        c.roundRect(cx + 2, y - h, cw - 4, h, 2, stroke=1, fill=1)
        c.setFillColor(col); c.roundRect(cx + 2, y - 13, cw - 4, 13, 2, stroke=0, fill=1)
        c.setFont(SERIF_B, 7.5); c.setFillColor(Color(1, 1, 1))
        c.drawString(cx + 8, y - 10, f"{nm} \u2014 {s.get('name','')}")
        c.setFont(SERIF, 6.0); c.setFillColor(HexColor("#3a3a42"))
        ty = y - 22
        for ln in wrap(c, s.get("effect", ""), SERIF, 5.8, cw - 14):
            c.drawString(cx + 8, ty, ln); ty -= 6.6
    return y - h

def build(out):
    c = canvas.Canvas(out, pagesize=(PW, PH))
    x = MX; w = PW - 2*MX; y = PH - MY

    c.setFillColor(INK); c.setFont(SERIF_B, 16); c.drawString(x, y - 12, "Domain Standing Board")
    c.setFont(SERIF_I, 9); c.setFillColor(MUTE)
    c.drawRightString(x + w, y - 11, "advance a cube per Domain \u00b7 Renown drives the Era")
    y -= 34

    # Renown track (full width)
    renown_track(c, x, y - 6, w)
    y -= 58

    # 4 domain tracks
    # 4 domain tracks (taller cells, 2x2 pip guides)
    half = (w - 24) / 2
    for i, dom in enumerate(DOMAINS):
        col = i % 2; rowi = i // 2
        tx = x + col * (half + 24); ty = y - rowi * 40
        domain_track(c, tx, ty, half, dom)
    y -= 2 * 40 + 6

    # definitions table (left) + era table (right)
    b = rd.DOMAIN_BOARD
    se = getattr(rd, "STANDING_EFFECTS", {})
    def_data = []
    for d in DOMAINS:
        tiers = []
        for tier in ("Rising", "Established", "Sovereign"):
            emp = (b[d].get(tier, "") or "").strip()
            cmb = se.get((d, tier))
            tiers.append((emp, str(cmb).strip() if cmb else ""))
        def_data.append((d, tiers))
    def_w = w * 0.60
    def_colw = [56, (def_w - 56)/3, (def_w - 56)/3, (def_w - 56)/3]
    ybot = draw_def_table(c, x, y, def_w, def_colw, def_data, fs=6.0)

    era_rows = [[nm, str(e["renown"]), str(e["armies"]), str(e["cities"]),
                 str(e["influence_per_turn"]), str(e.get("unlocks", "") or "\u2014")]
                for nm, e in rd.ERAS.items()]
    ex = x + def_w + 20; ew = w - def_w - 20
    era_colw = [64, 44, 42, 40, 40, ew - 230]
    era_bot = draw_table(c, ex, y, ew, ["Era", "Renown", "Armies", "Cities", "Infl", "Unlocks"],
                         era_rows, era_colw, "Era Standing", "#5a4f72", fs=7, hfs=7)

    # Envoys & Diplomacy as a table, under Era Standing
    det_rows = [[nm, str(e.get("envoys", "") or "").strip(),
                 f"+{e.get('innate_diplomacy_influence', 0)}"] for nm, e in rd.ERAS.items()]
    det_colw = [64, ew - 64 - 52, 52]
    # Envoys & Diplomacy table (no Seasons in the right column)
    draw_table(c, ex, era_bot - 14, ew, ["Era", "Envoys", "Diplo Infl"],
               det_rows, det_colw, "Envoys & Diplomacy", "#5a4f72", fs=6.6, hfs=7)

    # infrastructure tracker, then Seasons strip beneath it (full width)
    infra_bot = infra_tracker(c, x, MY + 160, w)
    _seasons_strip(c, x, infra_bot - 12, w)

    c.showPage(); c.save()
    print(f"domain board -> {out}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("cards", "domain_board.pdf")
    d = os.path.dirname(out)
    if d and not os.path.exists(d): os.makedirs(d, exist_ok=True)
    build(out)
