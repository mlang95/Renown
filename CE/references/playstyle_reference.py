#!/usr/bin/env python
# playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture).
# Reads CULTURES, NODES (Monuments), MONUMENT_SUMMARY, WONDERS, FACTIONS, DOMAIN_BOARD from renown_data_d10.
# Standing path is derived from each culture's Monument unlocks. Path names come from spec_tree_sheet.TREES.
# Faction mechanics are listed rarest-first (fewest cultures sharing them) until the banner is full.
# Usage:  python playstyle_reference.py [out.pdf] [--per-page N]   (default: cards/playstyle_reference.pdf, 4)
import sys, os, re, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import display_pdf; display_pdf.install()   # NAME_DISPLAY on every drawn/measured string (before reportlab imports)
from display_pdf import D as _D
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import renown_data_d10 as rd

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
FSUM    = {k: v.get("summary", "") for k, v in FACT.items() if isinstance(v, dict)}
MONS    = {k: v for k, v in rd.NODES.items() if v.get("monument") or v.get("type") == "Monument"}
MSUM    = getattr(rd, "MONUMENT_SUMMARY", {})
try:
    from spec_tree_sheet import TREES
except Exception:
    TREES = {}

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


MECH_ALIASES = {"fiends in low places": "friends in low places"}


def _mech_key(s):
    key = " ".join(str(s or "").split()).casefold()
    return MECH_ALIASES.get(key, key)


def culture_faction_rows(c):
    """Resolve a culture's mechanic_name labels to faction records for their summaries."""
    by_mechanic = {_mech_key(mech_name(f)): f for f in FACT}
    labels = c.get("mechanic_name", [])
    if isinstance(labels, str):
        labels = [labels]
    rows, represented = [], set()
    for label in labels:
        f = by_mechanic.get(_mech_key(label))
        if f in represented:
            continue
        if f:
            rows.append((str(label), f))
            represented.add(f)
        else:
            rows.append((str(label), None))
    label_keys = {_mech_key(x) for x in labels}
    for f in c.get("factions", []):
        if f in FACT and f not in represented and _mech_key(mech_name(f)) not in label_keys:
            rows.append((mech_name(f), f))
    return rows


def mech_counts():
    """{faction (or label key): number of cultures listing it}"""
    n = {}
    for c in CULT.values():
        for label, f in culture_faction_rows(c):
            k = f or _mech_key(label)
            n[k] = n.get(k, 0) + 1
    return n


def rarest_first(c):
    """culture_faction_rows ordered by how few cultures share each mechanic (ties keep data order)."""
    rows, n = culture_faction_rows(c), mech_counts()
    return sorted(rows, key=lambda r: (n.get(r[1] or _mech_key(r[0]), 0), rows.index(r)))


def path_name(m):
    return TREES.get(m) or f"Path of {disp(m)}"


# ---------------------------------------------------------------- validation
def validate():
    warn = []
    seen = {}
    for cn, c in CULT.items():
        for d in c.get("domains", []):
            if d not in DOMS: warn.append(f"{cn}: unknown domain {d!r}")
        for m in c.get("monuments", []):
            if m not in MONS: warn.append(f"{cn}: {m!r} is not a Monument in NODES")
            elif not MSUM.get(m): warn.append(f"{cn}: Monument {m!r} has no MONUMENT_SUMMARY")
        for w in c.get("wonders", []):
            if w not in WONDERS: warn.append(f"{cn}: {w!r} not in WONDERS")
        for a in c.get("actions", []):
            if a.split(":")[0].strip() not in ACTIONS: warn.append(f"{cn}: action {a!r} not in ACTIONS")
        labels = c.get("mechanic_name", [])
        labels = [labels] if isinstance(labels, str) else labels
        keys = [_mech_key(x) for x in labels]
        for k in sorted({k for k in keys if keys.count(k) > 1}):
            warn.append(f"{cn}: mechanic_name {k!r} listed {keys.count(k)} times")
        for x in labels:
            if str(x) != str(x).strip(): warn.append(f"{cn}: mechanic_name {x!r} has stray whitespace")
        for label, f in culture_faction_rows(c):
            if f is None:
                warn.append(f"{cn}: mechanic_name {label!r} has no FACTIONS match")
                continue
            seen.setdefault(f, []).append(cn)
        for k, _ in AXES:
            if k not in c.get("radar", {}): warn.append(f"{cn}: radar missing {k}")
    for f in FACT:
        if not FSUM.get(f): warn.append(f"faction {f!r} has no FACTIONS summary")
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
    return str((FACT.get(f) or {}).get("mechanic_name", "")) or disp(f)


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


def layout(c, runs, size, maxw, indent=0):
    """Word-wrap styled runs [(text, font, color)] -> lines of [(dx, word, font, color)].
    Lines after the first start at `indent`."""
    lines, cur, cx = [], [], 0
    for txt, font, col in runs:
        for i, w in enumerate(_D(txt).split(" ")):
            if not w: continue
            lead = " " if (cur and (i > 0 or txt.startswith(" "))) else ""
            ww = c.stringWidth(lead + w, font, size)
            if cur and cx + ww > maxw:
                lines.append(cur); cur = []; cx = indent; lead = ""
                ww = c.stringWidth(w, font, size)
            cur.append((cx + c.stringWidth(lead, font, size), w, font, col)); cx += ww
    if cur: lines.append(cur)
    return lines


def draw_lines(c, x, y, lines, size, lead):
    for ln in lines:
        for dx, w, font, col in ln:
            c.setFont(font, size); c.setFillColor(col); c.drawString(x + dx, y, w)
        y -= lead
    return y


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
COLW = 262        # Monuments & Wonders column; Faction Mechanics takes the rest
LEAD = 9.0
SZ   = 8.3
SSZ  = 7.2        # summary text
SLEAD = 8.2


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
    c.drawString(tx, ty - 12, cu.get("archetype") or TYPE_LABEL.get(cu.get("type"), ""))
    c.setFont(SERIF, 8.6)
    yy = ty - 23
    for ln in wrap(c, " \u00d7 ".join(doms), SERIF, 8.6, HW - 18):
        c.setFillColor(Color(0, 0, 0, 0.35)); c.drawString(tx + 0.4, yy - 0.4, ln)
        c.setFillColor(Color(1, 1, 1)); c.drawString(tx, yy, ln); yy -= 10
    # standing path (minimum Standings to unlock every Monument)
    req, open_any, _ = standing_path(cu)
    yy -= 4
    c.setFont(SERIF_B, 6.4); c.setFillColor(Color(1, 1, 1, 0.75)); c.drawString(tx, yy, "STANDING")
    yy -= 9.5
    st = [f"{req[d]} {d}" for d in DOMS if req[d] != "Untested"] + [f"+{n} {lvl} (any)" for n, lvl, _ in open_any]
    c.setFont(SERIF, 8.0)
    for ln in st:
        c.setFillColor(Color(0, 0, 0, 0.35)); c.drawString(tx + 0.4, yy - 0.4, ln)
        c.setFillColor(Color(1, 1, 1)); c.drawString(tx, yy, ln); yy -= 9.2

    # radar
    vals = [cu.get("radar", {}).get(k, 0) for k, _ in AXES]
    radar(c, x + HW + RW/2, ybot + bh/2 - 2, min(25, bh/2 - 18), vals, _c(DOMC[doms[0]]))

    # detail columns
    x1 = x + HW + RW + 2
    x2 = x1 + COLW + PAD
    w2 = x + W - PAD - x2
    for sx in (x1 - 3, x2 - PAD/2):
        c.setStrokeColor(SEP); c.setLineWidth(0.6); c.line(sx, ybot + 6, sx, ytop - 6)
    top = ytop - 12
    floor = ybot + 6

    # col 1: monuments (path + summary) + wonders
    tag(c, x1, top, "Monuments")
    yy = top - 10.5
    for m in cu.get("monuments", []):
        u = unlock_short(MONS.get(m, {}).get("unlock", "")).strip()
        c.setFont(SERIF_B, SZ); c.setFillColor(META); c.drawString(x1, yy, _D(m))
        mw = c.stringWidth(_D(m), SERIF_B, SZ)
        c.setFont(SERIF_I, 7.0); c.setFillColor(MUTE)
        if mw + 4 + c.stringWidth(u, SERIF_I, 7.0) <= COLW:
            c.drawString(x1 + mw + 4, yy, u)
        yy -= SLEAD
        runs = [(path_name(m) + ":", SERIF_I, WONINK), (" " + MSUM.get(m, ""), SERIF, INK)]
        yy = draw_lines(c, x1 + 6, yy, layout(c, runs, SSZ, COLW - 6, 0), SSZ, SLEAD) - 2.2
    yy -= 1
    flow(c, x1, yy, COLW, [("◆ " + disp(w), SERIF, WONINK) for w in cu.get("wonders", [])],
         SZ, LEAD, sep=("   ", SERIF, WONINK))

    # col 2: faction mechanics, rarest first, while they fit
    tag(c, x2, top, "Faction Mechanics")
    yy = top - 10.5
    for label, f in rarest_first(cu):
        runs = [(label.strip(), SERIF_B, META)]
        if f and FSUM.get(f): runs.append((" — " + FSUM[f], SERIF, INK))
        lines = layout(c, runs, SSZ + 0.2, w2, 6)
        if yy - (len(lines) - 1)*SLEAD < floor: continue
        yy = draw_lines(c, x2, yy, lines, SSZ + 0.2, SLEAD) - 2.6

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


def build(out, per_page=4):
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
    per = 4
    if "--per-page" in args:
        i = args.index("--per-page"); per = int(args[i+1]); del args[i:i+2]
    out = args[0] if args else os.path.join("cards", "playstyle_reference.pdf")
    d = os.path.dirname(out)
    if d and not os.path.exists(d): os.makedirs(d, exist_ok=True)
    build(out, per)
