"""
Renown — Tactic card sheet generator (v3).

v3 changes (from yesterday's tactic rebalance):
  - Scout buffs:  +1 TBH vs Flank, vs FF (vs Charge already in v2)
  - Ambush buffs: +1 TS vs Scout, vs Flank; +1 TH vs DF
  - Charge nerf:  -1 TS vs Scout, vs Ambush, vs DF
  - Mirror cells (Scout/Ambush/Flank vs self): "No Combat" instead of "Battle Ends"
  Opponent-side reciprocals applied consistently for matchup symmetry.

One card per tactic. Each card lists the matchup vs each opposing tactic,
formatted as a dotted leader: "Scout..............No Combat".

The outcome is auto-classified into a tier and colored:
    Extremely Good  → blue
    Good            → green
    About Even      → amber
    Bad             → orange
    Very Bad        → red
    Combat Skipped  → grey
    Battle Ends     → purple

Card size: 2.5" x 3.5".

Install:    pip install reportlab
Use from a notebook:
    from tactic_sheet import make_pdf
    make_pdf(r"C:\\path\\tactics.pdf")

Edit TACTIC_TABLE below to rebalance.
"""

import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, grey, HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------- Layout ----------
CARD_W = 2.5 * inch
CARD_H = 3.5 * inch
COLS, ROWS = 3, 3
PAGE_W, PAGE_H = letter
PAD = 0.10 * inch
MARGIN_X = (PAGE_W - CARD_W * COLS) / 2
MARGIN_Y = (PAGE_H - CARD_H * ROWS) / 2

ACCENT = HexColor("#5C2A1E")  # rust accent under title

# Tier colors — print-friendly palette
TIER_COLORS = {
    "extremely_good": HexColor("#1E5BAA"),  # blue
    "good":           HexColor("#2E7D32"),  # green
    "even":           HexColor("#B8860B"),  # amber
    "bad":            HexColor("#D95F2E"),  # orange
    "very_bad":       HexColor("#B23A3A"),  # red
    "skipped":        HexColor("#6E6E6E"),  # grey
    "battle_ends":    HexColor("#6A2C8C"),  # purple
}
DOT_COLOR = HexColor("#BBBBBB")

# ---------- Data ----------
TACTIC_ORDER = [
    "Scout",
    "Ambush",
    "Flank",
    "Charge",
    "Fighting Formation",
    "Defensive Formation",
    "Fall Back",
]

# Rows = your tactic. Columns follow TACTIC_ORDER.
TACTIC_TABLE = {
    "Scout":               ["+1I",                                      "+1I",                                            "-1I, +1 to Save",              "+1I",                                            "-1 to Save",                   "+1I",                                "Battle Ends"],
    "Ambush":              ["-1I, +1 to Save",                          "-1I, +1 to Save",                                "+1I, -1 to Hit",               "+1I, +1 to Hit",                                 "+1I, +1 to Save",              "-1 to Hit",                          "Battle Ends"],
    "Flank":               ["+1I",                                      "-1I, +1 to Hit",                                 "No Combat",                    "-1I",                                            "+1I, +1 to Hit",               "+1I",                                "-1I"],
    "Charge":              ["-1I, +1 to Hit",                           "-1I, -1 to Save",                                "+1I",                          "+1 to Hit",                                      "+1I, -1 to Hit",               "-1I, -1 to Save",                    "+1I, +1 to Hit"],
    "Fighting Formation":  ["+1 to Hit",                                "-1I",                                            "-1I",                          "-1I, +1 to Hit",                                 "-1I, +1 to Hit",               "+1 to Hit",                          "+1 to Hit"],
    "Defensive Formation": ["-1I, +1 to Save",                          "+1 to Save",                                     "-1I, +1 to Save",              "+1I, +1 to Hit, +1 to Save",                     "+1 to Save",                   "+1 to Save",                         "Battle Ends"],
    "Fall Back":           ["Battle Ends",                              "Battle Ends",                                    "+1I, +1 to Hit",               "-1I",                                            "No Bonus",                     "Battle Ends",                        "Battle Ends"],
}

# Each tactic's signature trade-off, using the matrix motif vocabulary:
#   Quick / Slow (init)  ·  Precise / Clumsy (hit)  ·  Fortified / Exposed (save)
#   Retreat (Battle Ends)  ·  No Contact (mirror skip)
RISK_REWARD = {
    "Scout":               ("Exposed",   "Quick"),
    "Ambush":              ("Clumsy",    "Quick & Precise"),
    "Flank":               ("Slow",      "Quick"),
    "Charge":              ("Exposed",   "Precise"),
    "Fighting Formation":  ("Slow",      "Precise"),
    "Defensive Formation": ("Slow",      "Fortified"),
    "Fall Back":           ("Slow",      "Retreat"),
}


# ---------- Title-case helper ("to" and "be" stay lowercase) ----------
_LOWER_WORDS = {"to", "be"}


def _smart_title(s):
    out = []
    for word in re.split(r"(\s+)", s):
        if not word.strip():
            out.append(word)
            continue
        if any(ch.isdigit() for ch in word):
            out.append(word)
            continue
        lw = word.lower()
        if lw in _LOWER_WORDS:
            out.append(lw)
        else:
            out.append(lw[:1].upper() + lw[1:])
    return "".join(out)


# ---------- Outcome classifier ----------
def classify(outcome):
    """Return tier key for an outcome string, scored from the card's perspective."""
    o = outcome.lower().strip()
    if "no combat" in o:
        return "skipped"
    if "battle ends" in o:
        return "battle_ends"
    if "no bonus" in o or o.startswith("both "):
        return "even"

    # Sum signed magnitudes, with polarity flipped for "to be hit" / enemy save
    score = 0
    for part in outcome.split(","):
        m = re.match(r"\s*([+\-])\s*(\d+)(.*)", part)
        if not m:
            continue
        sign = +1 if m.group(1) == "+" else -1
        mag = int(m.group(2))
        rest = m.group(3).lower().strip()
        if "to be hit" in rest:
            polarity = -1
        elif "their save" in rest or "enemy save" in rest:
            polarity = -1
        else:
            polarity = +1
        score += sign * polarity * mag

    if score >= 3:
        return "extremely_good"
    if score >= 1:
        return "good"
    if score == 0:
        return "even"
    if score == -1:
        return "bad"
    return "very_bad"


# ---------- Text helpers ----------
def _fit(text, max_w, font, start, floor):
    size = start
    while size > floor and stringWidth(text, font, size) > max_w:
        size -= 0.5
    if stringWidth(text, font, size) <= max_w:
        return text, size
    s = text
    while s and stringWidth(s + "\u2026", font, size) > max_w:
        s = s[:-1]
    return (s.rstrip() + "\u2026"), size


def _layout_row(opp, outcome, font_left, font_right, size, max_w, gap=2, min_dots_w=4):
    """
    Decide how to lay out a row. Returns list of line-segments:
      [{'left': 'Scout', 'right': 'No Combat'}]                # single dotted line
      [{'left': 'Defensive Formation', 'right': '+1I, +1 to Save,'},
       {'left': '',                    'right': '-1 to be Hit'}]   # wrapped
    """
    left_w = stringWidth(opp, font_left, size)
    full_right_w = stringWidth(outcome, font_right, size)

    if left_w + 2 * gap + min_dots_w + full_right_w <= max_w:
        return [{"left": opp, "right": outcome}]

    # Wrap outcome across multiple lines, first line shares with tactic name
    words = outcome.split()
    if not words:
        return [{"left": opp, "right": ""}]

    available_first = max_w - left_w - 2 * gap - min_dots_w
    first, rest = [], list(words)
    while rest:
        cand = " ".join(first + [rest[0]])
        if stringWidth(cand, font_right, size) <= available_first:
            first.append(rest.pop(0))
        else:
            break

    segments = []
    if first:
        segments.append({"left": opp, "right": " ".join(first)})
    else:
        segments.append({"left": opp, "right": ""})

    # Right-aligned wrap of remaining words
    cur = []
    for w in rest:
        cand = " ".join(cur + [w])
        if stringWidth(cand, font_right, size) <= max_w:
            cur.append(w)
        else:
            if cur:
                segments.append({"left": "", "right": " ".join(cur)})
                cur = [w]
            else:
                segments.append({"left": "", "right": w})
                cur = []
    if cur:
        segments.append({"left": "", "right": " ".join(cur)})

    return segments


# ---------- Card drawing ----------
def draw_tactic_card(c, x, y, tactic, outcomes):
    inner_w = CARD_W - 2 * PAD
    cx = x + CARD_W / 2

    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.rect(x, y, CARD_W, CARD_H)

    cur_y = y + CARD_H - PAD

    # Title
    title_text, title_size = _fit(tactic, inner_w, "Helvetica-Bold", 14.0, 10.0)
    cur_y -= title_size
    c.setFont("Helvetica-Bold", title_size)
    c.drawCentredString(cx, cur_y, title_text)
    cur_y -= 3

    # Accent bar
    cur_y -= 1
    c.setFillColor(ACCENT)
    c.rect(x + PAD + 18, cur_y, inner_w - 36, 1.5, stroke=0, fill=1)
    c.setFillColor(black)
    cur_y -= 4

    # Subtitle
    cur_y -= 8
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(cx, cur_y, "If your opponent plays...")
    cur_y -= 6

    # Divider
    c.setStrokeColor(grey)
    c.setLineWidth(0.4)
    c.line(x + PAD, cur_y, x + CARD_W - PAD, cur_y)
    c.setStrokeColor(black)
    cur_y -= 4

    body_top = cur_y
    # Reserve space for Risk/Reward footer (2 lines + divider + padding)
    FOOTER_H = 22
    body_floor = y + PAD + 2 + FOOTER_H

    # Auto-fit body size:
    # Pass 1 — pick the LARGEST size where every row fits on a single line AND vertical fits.
    # Pass 2 — fall back to largest size that just fits vertically (allowing wraps).
    LINE_GAP = 1.5
    ROW_GAP = 3.0
    SIZES = [9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0]

    def _try(size):
        rows_data = []
        all_single = True
        total_h = 0
        for opp, outcome in zip(TACTIC_ORDER, outcomes):
            outcome_disp = _smart_title(outcome)
            tier = classify(outcome)
            segs = _layout_row(opp, outcome_disp, "Helvetica-Bold", "Helvetica-Bold",
                               size, inner_w)
            rows_data.append((segs, tier))
            n = len(segs)
            if n > 1:
                all_single = False
            total_h += n * size + (n - 1) * LINE_GAP + ROW_GAP
        total_h -= ROW_GAP
        return rows_data, all_single, total_h

    chosen = None
    avail = body_top - body_floor
    for size in SIZES:
        rows_data, all_single, total_h = _try(size)
        if all_single and total_h <= avail:
            chosen = (size, rows_data)
            break
    if chosen is None:
        for size in SIZES:
            rows_data, _, total_h = _try(size)
            if total_h <= avail:
                chosen = (size, rows_data)
                break
    if chosen is None:
        size = 6.0
        rows_data, _, _ = _try(size)
        chosen = (size, rows_data)

    size, rows_data = chosen
    dot_w = stringWidth(".", "Helvetica", size)

    # Render rows
    cur_y = body_top
    for segs, tier in rows_data:
        color = TIER_COLORS[tier]
        for i, seg in enumerate(segs):
            cur_y -= size
            left = seg["left"]
            right = seg["right"]

            if left:
                # Tactic name (bold, black)
                c.setFillColor(black)
                c.setFont("Helvetica-Bold", size)
                c.drawString(x + PAD, cur_y, left)
                left_w = stringWidth(left, "Helvetica-Bold", size)
                right_w = stringWidth(right, "Helvetica-Bold", size)
                gap = 3

                # Dots fill
                dot_area_w = inner_w - left_w - right_w - 2 * gap
                if dot_area_w > 0 and dot_w > 0:
                    n_dots = int(dot_area_w / dot_w)
                    if n_dots > 0:
                        c.setFillColor(DOT_COLOR)
                        c.setFont("Helvetica", size)
                        c.drawString(x + PAD + left_w + gap, cur_y, "." * n_dots)

            # Right side (colored, bold), right-aligned
            if right:
                c.setFillColor(color)
                c.setFont("Helvetica-Bold", size)
                c.drawRightString(x + CARD_W - PAD, cur_y, right)

            if i < len(segs) - 1:
                cur_y -= LINE_GAP
        cur_y -= ROW_GAP
        c.setFillColor(black)

    # ── Risk / Reward footer ───────────────────────────────────────────
    risk, reward = RISK_REWARD.get(tactic, ("", ""))
    if risk or reward:
        footer_y = y + PAD + 2 + FOOTER_H
        # Divider above footer
        c.setStrokeColor(grey)
        c.setLineWidth(0.4)
        c.line(x + PAD, footer_y, x + CARD_W - PAD, footer_y)
        c.setStrokeColor(black)
        footer_size = 7.0
        label_color = HexColor("#5C2A1E")
        # Reward line (above Risk so the bottom-most line is Risk; flip order if preferred)
        line_y = footer_y - footer_size - 1
        c.setFont("Helvetica-Bold", footer_size)
        c.setFillColor(label_color)
        c.drawString(x + PAD, line_y, "Reward:")
        reward_label_w = stringWidth("Reward:", "Helvetica-Bold", footer_size)
        c.setFont("Helvetica", footer_size)
        c.setFillColor(black)
        c.drawString(x + PAD + reward_label_w + 3, line_y, reward)
        # Risk line
        line_y -= footer_size + 2
        c.setFont("Helvetica-Bold", footer_size)
        c.setFillColor(label_color)
        c.drawString(x + PAD, line_y, "Risk:")
        risk_label_w = stringWidth("Risk:", "Helvetica-Bold", footer_size)
        c.setFont("Helvetica", footer_size)
        c.setFillColor(black)
        c.drawString(x + PAD + risk_label_w + 3, line_y, risk)


def draw_crop_marks(c):
    c.setStrokeColor(grey)
    c.setLineWidth(0.25)
    tick = 0.15 * inch
    gap = 0.04 * inch
    for i in range(COLS + 1):
        gx = MARGIN_X + i * CARD_W
        c.line(gx, MARGIN_Y - gap, gx, MARGIN_Y - gap - tick)
        c.line(gx, PAGE_H - MARGIN_Y + gap, gx, PAGE_H - MARGIN_Y + gap + tick)
    for i in range(ROWS + 1):
        gy = MARGIN_Y + i * CARD_H
        c.line(MARGIN_X - gap, gy, MARGIN_X - gap - tick, gy)
        c.line(PAGE_W - MARGIN_X + gap, gy, PAGE_W - MARGIN_X + gap + tick, gy)
    c.setStrokeColor(black)


def make_pdf(pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    per_page = COLS * ROWS

    for i, tactic in enumerate(TACTIC_ORDER):
        slot = i % per_page
        if slot == 0 and i > 0:
            draw_crop_marks(c)
            c.showPage()

        col = slot % COLS
        r = slot // COLS
        cx = MARGIN_X + col * CARD_W
        cy = PAGE_H - MARGIN_Y - (r + 1) * CARD_H
        draw_tactic_card(c, cx, cy, tactic, TACTIC_TABLE[tactic])

    draw_crop_marks(c)
    c.save()
    print(f"Wrote {pdf_path}  ({len(TACTIC_ORDER)} cards, "
          f"{(len(TACTIC_ORDER) + per_page - 1) // per_page} page(s))")
