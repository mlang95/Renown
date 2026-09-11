#!/usr/bin/env python
# pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data.
# Model B: tiles are placed into settlement wards, so each carries its live play
# info (gate, upkeep, innate, mastery); the full tech tree lives in the reference.
# Usage:  python pursuit_tiles.py [out.pdf]      (default: cards/pursuit_tiles.pdf)
import sys, os
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

# ── type palette + sort order ──
TYPE_ORDER = ["Raw Materials", "Husbandry", "Energy", "Craft", "Power", "Civic", "Secrecy", "Monument"]
TYPE_COLOR = {
    "Raw Materials": "#6b5330", "Husbandry": "#4f7a3a", "Energy": "#c8791f",
    "Craft": "#2E5A8C", "Power": "#9E2B25", "Civic": "#3f7d7a",
    "Secrecy": "#3a3a42", "Monument": "#B48A1E",
}
INK = HexColor("#26262e"); MUTE = HexColor("#6f6f77"); TAG = HexColor("#8a8072")
LINE = HexColor("#e6e2d8"); BODY = HexColor("#2b2b32")

UPK_BY_TYPE = getattr(rd, "PURSUIT_UPKEEP_BY_TYPE", {"Monument": 300, "Power": 200, "Energy": 0})
UPK_DEFAULT = getattr(rd, "PURSUIT_UPKEEP_DEFAULT", 100)
def upkeep(t): return UPK_BY_TYPE.get(t, UPK_DEFAULT)

# ── geometry: 5 x 5 tiles per Letter page ──
PAGE_W, PAGE_H = letter
MX, MY = 30, 28
COLS, ROWS = 5, 5
GAP = 7
TW = (PAGE_W - 2*MX - (COLS-1)*GAP) / COLS
TH = (PAGE_H - 2*MY - (ROWS-1)*GAP) / ROWS
HEAD_H = 20

DOMAIN_COLOR = {"Industry": "#2E5A8C", "Prowess": "#9E2B25",
                "Cunning": "#1c1c20", "Piety": "#C6A024"}
def _domain_of(d):
    eng = d.get("engine") or {}
    dd = eng.get("domain") or {}
    if dd:
        return max(dd, key=dd.get)
    u = d.get("unlock") or ""
    for x in ("Industry", "Prowess", "Cunning", "Piety"):
        if x in u:
            return x
    return None

def _c(h): return HexColor(h)

def _clean(s):
    s = (s or "").replace("**", "").replace("*", "")
    return s.strip()

def wrap(c, text, font, size, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= maxw:
            cur = t
        else:
            if cur: out.append(cur)
            cur = w
    if cur: out.append(cur)
    return out

def body_layout(c, inn, mas, mas_req, gate, gate_col, x, y_top, y_floor, w, cap=10.5, floor=5.5):
    """Pick the largest single body font at which INNATE+MASTERY both fit in the
    vertical budget (y_top..y_floor), then draw them. Requirements print inline
    after the section label: gate after INNATE, mas_req after MASTERY."""
    avail = y_top - y_floor
    size = cap
    while size > floor:
        lh = size + 1.8
        lines = blocks = 0
        for txt in (inn, mas):
            if txt:
                lines += len(wrap(c, txt, SERIF, size, w)); blocks += 1
        rs = max(5.0, size*0.72)
        req_lines = 0
        if inn and gate:     req_lines += len(wrap(c, "INNATE: " + gate, SERIF_I, rs, w))
        if mas and mas_req:  req_lines += len(wrap(c, "MASTERY: " + mas_req, SERIF_I, rs, w))
        needed = lines * lh + blocks * (size * 0.85 + 3) + req_lines * (rs + 1.4)
        if needed <= avail:
            break
        size -= 0.3
    y = y_top
    for label, txt, req in (("INNATE", inn, gate), ("MASTERY", mas, mas_req)):
        if not txt:
            continue
        lab_sz = max(5.4, size * 0.66)
        if req:
            # "LABEL:" then the requirement inline in italics, wrapping
            rs = max(5.0, size * 0.72)
            head = label + ": "
            req_col = gate_col if (label == "INNATE" and gate_col) else MUTE
            c.setFont(SERIF_B, lab_sz); c.setFillColor(TAG)
            c.drawString(x, y, head)
            hx = x + c.stringWidth(head, SERIF_B, lab_sz)
            c.setFont(SERIF_I, rs); c.setFillColor(req_col)
            words = req.split()
            line = ""; first = True
            for wd in words:
                trial = (line + " " + wd).strip()
                avail = (x + w - hx) if first else w
                if c.stringWidth(trial, SERIF_I, rs) <= avail:
                    line = trial
                else:
                    c.drawString(hx if first else x, y, line)
                    y -= rs + 1.4; first = False; line = wd; hx = x
            if line:
                c.drawString(hx if first else x, y, line); y -= rs + 1.4
            y -= 1.5
        else:
            c.setFont(SERIF_B, lab_sz); c.setFillColor(TAG)
            c.drawString(x, y, label)
            y -= size * 0.85 + 1.5
        c.setFont(SERIF, size); c.setFillColor(BODY)
        for ln in wrap(c, txt, SERIF, size, w):
            c.drawString(x, y, ln); y -= size + 1.8
        y -= 3
    return y

def fit_block(c, label, text, x, y, w, max_lines, base=8.2, min_sz=6.2):
    """Draw a TAG label + wrapped text, shrinking font until it fits max_lines.
    Returns the y after drawing."""
    size = base
    while size >= min_sz:
        lines = wrap(c, text, SERIF, size, w)
        if len(lines) <= max_lines:
            break
        size -= 0.4
    lines = wrap(c, text, SERIF, size, w)[:max_lines]
    c.setFont(SERIF_B, 5.8); c.setFillColor(TAG); c.drawString(x, y, label)
    y -= 8
    c.setFont(SERIF, size); c.setFillColor(BODY)
    for ln in lines:
        c.drawString(x, y, ln); y -= size + 1.6
    return y

def tile(c, name, d, x, ytop):
    s = max(0.58, min(1.0, TW / 178.0))   # scale factor vs the original 3-col width
    head_h = 20 * s
    nm_sz, meta_sz, body_base, body_min, foot_sz = 10.5*s, 7.2*s, 8.2*s, 5.4*s, 6.2*s
    pad = 7 * s
    t = d.get("type", "")
    mon = d.get("monument")
    col = _c(TYPE_COLOR.get(t, "#555"))
    gate = (d.get("unlock") or "").strip()
    gate = "" if gate in ("", "-", "\u2014") else gate

    # clip to rounded rect
    c.saveState()
    cp = c.beginPath(); cp.roundRect(x, ytop - TH, TW, TH, 5); c.clipPath(cp, stroke=0, fill=0)
    # header bar
    hy = ytop - head_h
    c.setFillColor(col); c.rect(x, hy, TW, head_h, stroke=0, fill=1)
    c.restoreState()

    # name (shadow + white), monument diamond
    c.setFont(SERIF_B, nm_sz)
    nm = name
    up_val = upkeep(t)
    reserve = 20
    if up_val: reserve += 16
    if mon: reserve += 14
    name_limit = TW - reserve * s
    while c.stringWidth(nm, SERIF_B, nm_sz) > name_limit and len(nm) > 6:
        nm = nm[:-2]
    if nm != name:
        nm = nm.rstrip() + "\u2026"
    c.setFillColor(Color(0, 0, 0, 0.28)); c.drawString(x + pad + 0.5, hy + head_h*0.31 - 0.4, nm)
    c.setFillColor(Color(1, 1, 1)); c.drawString(x + pad, hy + head_h*0.31, nm)
    up = upkeep(t)
    corner_x = x + TW - pad
    if up:
        c.setFillColor(Color(1, 1, 1)); c.setFont(SERIF_B, nm_sz)
        c.drawRightString(corner_x, hy + head_h*0.31, str(up))
        corner_x -= c.stringWidth(str(up), SERIF_B, nm_sz) + 6*s
    if mon:
        c.setFillColor(Color(1, 1, 1)); c.setFont(SERIF_B, nm_sz)
        c.drawRightString(corner_x, hy + head_h*0.31, "\u25c6")

    # meta line: efficient (left)  — gate moves into INNATE below
    my = hy - 9*s
    eff_raw = d.get("efficient")
    if isinstance(eff_raw, (list, tuple)):
        eff = ", ".join(eff_raw)
    else:
        eff = (eff_raw or "").strip()
    if eff:
        c.setFont(SERIF_I, meta_sz*1.15); c.setFillColor(_c("#3f7d7a"))
        c.drawString(x + pad, my, f"efficient: {eff}")
    line_y = my - 5*s
    c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(x + 6*s, line_y, x + TW - 6*s, line_y)

    # builds_into footer line
    bi = d.get("builds_into") or []
    bi_txt = ""
    if bi:
        bi_txt = "\u2192 " + ", ".join(bi)
        c.setFont(SERIF_I, foot_sz)
        while c.stringWidth(bi_txt, SERIF_I, foot_sz) > TW - 2*pad - c.stringWidth(t, SERIF_I, foot_sz) - 8 and "," in bi_txt:
            bi_txt = bi_txt.rsplit(",", 1)[0]
        if bi_txt != "\u2192 " + ", ".join(bi):
            bi_txt += "\u2026"

    # body: innate + mastery, sized to fill the available height
    y = line_y - 12*s
    floor_y = ytop - TH + 15*s          # leave room for the footer row
    inn = _clean(d.get("innate"))
    mas = _clean(d.get("mastery"))
    mreq = d.get("mastery_req")
    mreq = "" if not mreq or str(mreq).strip() in ("", "-", "\u2014") else _clean(mreq)
    gate_txt = "" if not gate or str(gate).strip() in ("", "-", "\u2014") else _clean(gate)
    _dom = _domain_of(d)
    gate_col = _c(DOMAIN_COLOR[_dom]) if _dom else None
    body_layout(c, inn, mas, mreq, gate_txt, gate_col, x + pad, y, floor_y, TW - 2*pad, cap=10.5, floor=5.5)

    # footer: type (left) + builds_into (right) + border
    c.setFont(SERIF_I, foot_sz); c.setFillColor(TAG)
    c.drawString(x + pad, ytop - TH + 5*s, t)
    if bi_txt:
        c.setFillColor(_c("#8a8072"))
        c.drawRightString(x + TW - pad, ytop - TH + 5*s, bi_txt)
    c.setStrokeColor(LINE); c.setLineWidth(0.9)
    c.roundRect(x, ytop - TH, TW, TH, 5, stroke=1, fill=0)

def build(out):
    c = canvas.Canvas(out, pagesize=letter)
    order = sorted(rd.NODES.items(),
                   key=lambda kv: (TYPE_ORDER.index(kv[1].get("type")) if kv[1].get("type") in TYPE_ORDER else 99, kv[0]))
    per = COLS * ROWS
    for i, (name, d) in enumerate(order):
        slot = i % per
        if slot == 0 and i:
            c.showPage()
        r, cc = divmod(slot, COLS)
        x = MX + cc * (TW + GAP)
        ytop = PAGE_H - MY - r * (TH + GAP)
        tile(c, name, d, x, ytop)
    c.showPage(); c.save()
    print(f"pursuit tiles -> {out}  ({len(order)} tiles, {-(-len(order)//per)} pages)")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("cards", "pursuit_tiles.pdf")
    d = os.path.dirname(out)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    build(out)
