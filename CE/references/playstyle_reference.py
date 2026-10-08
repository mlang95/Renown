#!/usr/bin/env python
# playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture).
# Reads CULTURES, NODES (Monuments), ACTIONS, WONDERS, FACTIONS, DOMAIN_BOARD from renown_data.
# Standing path is derived from each culture's Monument unlocks.
# Usage:  python playstyle_reference.py [out.pdf] [--per-page N]   (default: cards/playstyle_reference.pdf, 5)
import sys, os, re, math
import display_pdf; display_pdf.install()   # NAME_DISPLAY on every drawn/measured string (before reportlab imports)
from display_pdf import D as _D
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

CULT    = rd.CULTURES
ACTIONS = rd.ACTIONS
WONDERS = getattr(rd, "WONDERS", {})
FACT    = getattr(rd, "FACTIONS", {})
DBOARD  = getattr(rd, "DOMAIN_BOARD", {})
FSUM    = getattr(rd, "FACTION_SUMMARIES", {})
MONS    = {k: v for k, v in rd.NODES.items() if v.get("monument") or v.get("type") == "Monument"}

DOMS  = ["Industry", "Prowess", "Cunning", "Piety"]
LVL   = ["Untested", "Rising", "Established", "Sovereign"]
PTS   = {"Untested": 0, "Rising": 3, "Established": 6, "Sovereign": 10}
TYPE_LABEL = {"pure": "Pure", "pair": "Pair", "triple": "Triple", "centre": "Centre"}
TYPE_ORDER = ["pure", "pair", "triple", "centre"]   # centre last: most complex

AXES = [("military_solutions", "Military"), ("economy_generators", "Economy"),
        ("faith_management", "Faith"), ("doubt_warfare", "Disruption"),
        ("political_control", "Influence"), ("board_presence", "Board"),
        ("degenerate_punishment", "Punish")]
AXIS_LABELS = [lab for _, lab in AXES]

IND, PRO, CUN, PIE, DIP = "#2E5A8C", "#9E2B25", "#1c1c20", "#C6A024", "#5f6f52"
DOMC = {"Industry": IND, "Prowess": PRO, "Cunning": CUN, "Piety": PIE, "Diplomacy": DIP}
INK   = HexColor("#26262e"); MUTE = HexColor("#7a7a82"); TAG = HexColor("#a59a82")
WONINK= HexColor("#7a5a1a"); GRIDC = HexColor("#d9d4c8"); RING = HexColor("#e3ded3")
META  = HexColor("#33333b"); SEP = HexColor("#efece4")


def _c(h): return HexColor(h)
def disp(x): return x[4:] if x.startswith("The ") else x


# ---------------------------------------------------------------- validation
def validate():
    warn = []
    seen = {}
    for cn, c in CULT.items():
        for d in c.get("domains", []):
            if d not in DOMS: warn.append(f"{cn}: unknown domain {d!r}")
        for m in c.get("monuments", []):
            if m not in MONS: warn.append(f"{cn}: {m!r} is not a Monument in NODES")
        for w in c.get("wonders", []):
            if w not in WONDERS: warn.append(f"{cn}: {w!r} not in WONDERS")
        for a in c.get("actions", []):
            if a.split(":")[0].strip() not in ACTIONS: warn.append(f"{cn}: action {a!r} not in ACTIONS")
        for f in c.get("factions", []):
            if f not in FACT: warn.append(f"{cn}: faction {f!r} not in FACTIONS")
            seen.setdefault(f, []).append(cn)
        for k, _ in AXES:
            if k not in c.get("radar", {}): warn.append(f"{cn}: radar missing {k}")
    for f in FACT:
        if f not in FSUM: warn.append(f"faction {f!r} has no FACTION_SUMMARIES entry")
    for f in FACT:
        if f not in seen: warn.append(f"faction {f!r} not mapped to a culture")
    for w in warn: print("  WARN", w)
    return warn


# ---------------------------------------------------------------- standing path
def parse_unlock(s):
    """-> (specific {domain: level}, generic [(count, level)])"""
    spec, gen = {}, []
    for lvl, d in re.findall(r"(Rising|Established|Sovereign)\s+(Industry|Prowess|Cunning|Piety)", s or ""):
        if LVL.index(lvl) > LVL.index(spec.get(d, "Untested")): spec[d] = lvl
    for n, lvl in re.findall(r"(\d+)\s+(Rising|Established|Sovereign)\b(?!\s+(?:Industry|Prowess|Cunning|Piety))", s or ""):
        gen.append((int(n), lvl))
    return spec, gen


def standing_path(c):
    """-> (req {domain: level}, open_any [(count, level, cost)], total points)"""
    req = {d: "Untested" for d in DOMS}
    gens = []
    for m in c.get("monuments", []):
        spec, gen = parse_unlock(MONS.get(m, {}).get("unlock", ""))
        for d, lvl in spec.items():
            if LVL.index(lvl) > LVL.index(req[d]): req[d] = lvl
        gens += gen
    open_any = []
    for n, lvl in sorted(gens, key=lambda g: -g[0]):
        have = [d for d in DOMS if LVL.index(req[d]) >= LVL.index(lvl)]
        deficit = n - len(have)
        if deficit <= 0: continue
        cand = [d for d in DOMS if d not in have]
        if deficit >= len(cand):
            for d in cand: req[d] = lvl
        else:
            costs = sorted(PTS[lvl] - PTS[req[d]] for d in cand)
            open_any.append((deficit, lvl, sum(costs[:deficit])))
    total = sum(PTS[v] for v in req.values()) + sum(x[2] for x in open_any)
    return req, open_any, total


def unlock_short(s):
    s = (s or "").replace("Sovereign", "Sov").replace("Established", "Est")
    return s


def mech_name(f):
    m = str((FACT.get(f) or {}).get("mechanic", ""))
    return m.split(":")[0].strip() if ":" in m else disp(f)


def standing_title(d, lvl):
    t = (DBOARD.get(d, {}) or {}).get(lvl, "")
    return t.split(":")[0].strip() if ":" in t else ""


# ---------------------------------------------------------------- drawing helpers
def flow(c, x, y, maxw, tokens, size, lead, sep=None):
    """Place styled tokens left->right, wrapping at token boundaries. tokens: [(text, font, color)].
    sep: (text, font, color) drawn between tokens when they share a line. Returns y after last line."""
    cx = x
    first = True
    for txt, font, col in tokens:
        txt = _D(txt)
        tw = c.stringWidth(txt, font, size)
        sw = c.stringWidth(sep[0], sep[1], size) if (sep and not first) else 0
        if not first and cx + sw + tw > x + maxw:
            y -= lead; cx = x; sw = 0
        elif sep and not first:
            c.setFont(sep[1], size); c.setFillColor(sep[2]); c.drawString(cx, y, sep[0]); cx += sw
        c.setFont(font, size); c.setFillColor(col); c.drawString(cx, y, txt); cx += tw
        first = False
    return y - lead


def wrap(c, text, font, size, maxw):
    words, lines, cur = _D(text).split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def chip(c, x, y, dom, s=5.2):
    c.setFillColor(_c(DOMC.get(dom, "#888888"))); c.rect(x, y + 0.6, s, s, stroke=0, fill=1)


def tag(c, x, y, label):
    c.setFont(SERIF_B, 6.4); c.setFillColor(TAG); c.drawString(x, y, label.upper())


def radar(c, cx, cy, R, vals, color):
    n = len(vals)
    ang = [math.radians(90 - i*360/n) for i in range(n)]
    def pt(i, r): return (cx + r*math.cos(ang[i]), cy + r*math.sin(ang[i]))
    c.setStrokeColor(RING); c.setLineWidth(0.6)
    for lvl in range(1, 6):
        r = R*lvl/5; p = c.beginPath(); p.moveTo(*pt(0, r))
        for i in range(1, n): p.lineTo(*pt(i, r))
        p.close(); c.drawPath(p, stroke=1, fill=0)
    for i in range(n): c.line(cx, cy, *pt(i, R))
    p = c.beginPath(); p.moveTo(*pt(0, R*vals[0]/5))
    for i in range(1, n): p.lineTo(*pt(i, R*vals[i]/5))
    p.close()
    c.setFillColor(color); c.setFillAlpha(0.34); c.setStrokeColor(color); c.setStrokeAlpha(1); c.setLineWidth(1.4)
    c.drawPath(p, stroke=1, fill=1); c.setFillAlpha(1)
    for i in range(n):
        x, y = pt(i, R*vals[i]/5); c.circle(x, y, 1.4, stroke=0, fill=1)
    c.setFont(SERIF, 6.0); c.setFillColor(MUTE)
    for i in range(n):
        lx, ly = pt(i, R + 6); ca = math.cos(ang[i]); sa = math.sin(ang[i])
        dy = 3.0 if sa < -0.34 else (-1.5 if sa > 0.34 else -2.0)
        if abs(ca) < 0.34: c.drawCentredString(lx, ly - dy, AXIS_LABELS[i])
        elif ca > 0:       c.drawString(lx, ly - dy, AXIS_LABELS[i])
        else:              c.drawRightString(lx, ly - dy, AXIS_LABELS[i])


# ---------------------------------------------------------------- geometry
PAGE_W, PAGE_H = landscape(letter)           # 792 x 612
MX = 29; MT = 22; MB = 20
TITLE_Y = PAGE_H - MT - 16
RULE_Y  = PAGE_H - MT - 26
FOOT_Y  = MB + 4
TOP = RULE_Y - 8
BOT = FOOT_Y + 12
GAP = 7
W   = PAGE_W - 2*MX
HW  = 118          # header block width
RW  = 104          # radar block width
PAD = 9
COLW = [160, 160]  # detail columns 1 and 2; column 3 takes the rest
LEAD = 9.2
SZ   = 8.3


def banner(c, name, x, ytop, bh):
    cu = CULT[name]; doms = cu["domains"]
    ybot = ytop - bh
    # frame clip
    c.saveState()
    fp = c.beginPath(); fp.roundRect(x, ybot, W, bh, 4); c.clipPath(fp, stroke=0, fill=0)
    # header block (domain gradient, left->right)
    cols = [_c(DOMC[d]) for d in doms]
    c.saveState()
    hp = c.beginPath(); hp.rect(x, ybot, HW, bh); c.clipPath(hp, stroke=0, fill=0)
    if len(cols) == 1:
        c.setFillColor(cols[0]); c.rect(x, ybot, HW, bh, stroke=0, fill=1)
    else:
        pos = [i/(len(cols)-1) for i in range(len(cols))]
        c.linearGradient(x, ybot, x + HW, ybot, cols, pos, extend=True)
    c.restoreState()
    c.restoreState()

    # header text
    tx = x + 9; ty = ytop - 20
    c.setFont(SERIF_B, 14.5)
    c.setFillColor(Color(0, 0, 0, 0.35)); c.drawString(tx + 0.6, ty - 0.6, name)
    c.setFillColor(Color(1, 1, 1));       c.drawString(tx, ty, name)
    c.setFont(SERIF_I, 8.6); c.setFillColor(Color(1, 1, 1, 0.92))
    c.drawString(tx, ty - 12, TYPE_LABEL.get(cu.get("type"), "") )
    c.setFont(SERIF, 8.6)
    yy = ty - 23
    for ln in wrap(c, " \u00d7 ".join(doms), SERIF, 8.6, HW - 18):
        c.setFillColor(Color(0, 0, 0, 0.35)); c.drawString(tx + 0.4, yy - 0.4, ln)
        c.setFillColor(Color(1, 1, 1)); c.drawString(tx, yy, ln); yy -= 10
    req, open_any, _ = standing_path(cu)

    # radar
    vals = [cu.get("radar", {}).get(k, 0) for k, _ in AXES]
    radar(c, x + HW + RW/2, ybot + bh/2 - 2, min(25, bh/2 - 18), vals, _c(DOMC[doms[0]]))

    # detail columns
    x1 = x + HW + RW + 2
    x2 = x1 + COLW[0] + PAD
    x3 = x2 + COLW[1] + PAD
    w3 = x + W - PAD - x3
    for sx in (x1 - 3, x2 - PAD/2, x3 - PAD/2):
        c.setStrokeColor(SEP); c.setLineWidth(0.6); c.line(sx, ybot + 6, sx, ytop - 6)
    top = ytop - 12

    # col 1: monuments + actions
    tag(c, x1, top, "Monuments")
    yy = top - 10.5
    for m in cu.get("monuments", []):
        u = unlock_short(MONS.get(m, {}).get("unlock", ""))
        c.setFont(SERIF_B, SZ); c.setFillColor(META); c.drawString(x1, yy, _D(m))
        mw = c.stringWidth(_D(m), SERIF_B, SZ)
        c.setFont(SERIF_I, 7.0); c.setFillColor(MUTE)
        if mw + 4 + c.stringWidth(u, SERIF_I, 7.0) <= COLW[0]:
            c.drawString(x1 + mw + 4, yy, u)
        else:
            yy -= 7.6; c.drawString(x1 + 6, yy, u)
        yy -= LEAD
    yy -= 3
    tag(c, x1, yy, "Actions"); yy -= 10.5
    for a in cu.get("actions", []):
        base, _, mode = a.partition(":")
        base = base.strip(); mode = mode.strip()
        ad = ACTIONS.get(base, {})
        chip(c, x1, yy, ad.get("domain", ""))
        c.setFont(SERIF_B, SZ); c.setFillColor(META)
        c.drawString(x1 + 8, yy, _D(base))
        cx = x1 + 8 + c.stringWidth(_D(base), SERIF_B, SZ)
        if mode:
            extra = " \u2014 " + mode
            c.setFont(SERIF, SZ); c.drawString(cx, yy, extra); cx += c.stringWidth(extra, SERIF, SZ)
        rq = ad.get("requires", "")
        if rq:
            c.setFont(SERIF_I, 7.0); c.setFillColor(MUTE); c.drawString(cx + 4, yy, unlock_short(rq))
        yy -= LEAD

    # col 2: standing path + wonders
    tag(c, x2, top, "Standing")
    yy = top - 10.5
    for d in DOMS:
        lvl = req[d]
        if lvl == "Untested": continue
        chip(c, x2, yy, d)
        c.setFont(SERIF_B, SZ); c.setFillColor(META)
        st = f"{lvl} {d}"; c.drawString(x2 + 8, yy, st)
        t = standing_title(d, lvl)
        if t:
            c.setFont(SERIF_I, 7.0); c.setFillColor(MUTE)
            c.drawString(x2 + 12 + c.stringWidth(st, SERIF_B, SZ), yy, t)
        yy -= LEAD
    for n, lvl, cost in open_any:
        c.setFont(SERIF_B, SZ); c.setFillColor(META)
        c.drawString(x2 + 8, yy, f"+{n} {lvl} (any)")
        yy -= LEAD
    yy -= 3
    tag(c, x2, yy, "Wonders"); yy -= 10.5
    flow(c, x2, yy, COLW[1], [("\u25c6 " + disp(w), SERIF, WONINK) for w in cu.get("wonders", [])],
         SZ, LEAD, sep=("   ", SERIF, WONINK))

    # col 3: factions (mechanic name + summary), shrink to fit
    tag(c, x3, top, "Factions")
    floor = ybot + 5
    fl = cu.get("factions", [])
    for size in (8.0, 7.7, 7.4, 7.1, 6.8, 6.5):
        lead = size + 1.0
        rows = []
        for f in fl:
            fc = (FACT.get(f) or {}).get("final_cut", True)
            nm = mech_name(f)
            lines = wrap(c, FSUM.get(f, ""), SERIF, size - 0.6, w3 - 6)
            rows.append((nm, fc, lines))
        need = sum(lead + len(r[2])*(lead - 0.6) + 1.5 for r in rows)
        if top - 10.5 - need >= floor - lead: break
    yy = top - 10.5
    for nm, fc, lines in rows:
        c.setFont(SERIF_B, size); c.setFillColor(META)
        c.drawString(x3, yy, _D(nm)); yy -= lead
        c.setFont(SERIF, size - 0.6); c.setFillColor(MUTE)
        for ln in lines:
            c.drawString(x3 + 6, yy, ln); yy -= lead - 0.6
        yy -= 1.5

    # border
    c.setStrokeColor(GRIDC); c.setLineWidth(0.8)
    c.roundRect(x, ybot, W, bh, 4, stroke=1, fill=0)


def order():
    names = list(CULT)
    return sorted(names, key=lambda n: (TYPE_ORDER.index(CULT[n].get("type")) if CULT[n].get("type") in TYPE_ORDER else 9,
                                        names.index(n)))


def page_chrome(c, pg, npg):
    c.setFillColor(INK); c.setFont(SERIF_B, 20); c.drawString(MX, TITLE_Y, "RENOWN")
    w = c.stringWidth("RENOWN", SERIF_B, 20)
    c.setFont(SERIF_I, 12); c.setFillColor(HexColor("#6a6a72"))
    c.drawString(MX + w + 8, TITLE_Y + 1, "\u00b7 culture playstyles")
    lx = PAGE_W - MX
    for nm in reversed(DOMS + ["Diplomacy"]):
        c.setFont(SERIF, 9.5); tw = c.stringWidth(nm, SERIF, 9.5)
        c.setFillColor(INK); c.drawRightString(lx, TITLE_Y + 1, nm); lx -= tw + 6
        c.setFillColor(_c(DOMC[nm])); c.rect(lx - 9, TITLE_Y - 1, 9, 9, stroke=0, fill=1); lx -= 9 + 13
    c.setStrokeColor(INK); c.setLineWidth(1.6); c.line(MX, RULE_Y, PAGE_W - MX, RULE_Y)
    c.setFont(SERIF_I, 8.5); c.setFillColor(MUTE)
    c.drawCentredString(PAGE_W/2, FOOT_Y,
        "Radar = relative emphasis (1\u20135)  \u00b7  Standing = minimum Domain Standings to unlock every listed Monument"
        "  \u00b7  \u25c6 Wonder")
    c.drawRightString(PAGE_W - MX, FOOT_Y, f"{pg}/{npg}")


def build(out, per_page=5):
    validate()
    names = order()
    pages = [names[i:i+per_page] for i in range(0, len(names), per_page)]
    bh = (TOP - BOT - (per_page - 1)*GAP) / per_page
    c = canvas.Canvas(out, pagesize=(PAGE_W, PAGE_H))
    for pi, pg in enumerate(pages, 1):
        page_chrome(c, pi, len(pages))
        for i, n in enumerate(pg):
            banner(c, n, MX, TOP - i*(bh + GAP), bh)
        c.showPage()
    c.save()
    print("playstyle reference ->", out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    per = 5
    if "--per-page" in args:
        i = args.index("--per-page"); per = int(args[i+1]); del args[i:i+2]
    out = args[0] if args else os.path.join("cards", "playstyle_reference.pdf")
    d = os.path.dirname(out)
    if d and not os.path.exists(d): os.makedirs(d, exist_ok=True)
    build(out, per)