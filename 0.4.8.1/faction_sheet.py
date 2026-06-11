"""
Renown — Faction card sheet generator.

Reads factions.csv and lays out faction cards 3x3 on US Letter as a
print-ready PDF.
Card size: 2.5" x 3.5" (fits standard MTG sleeves).

Install:    pip install reportlab
Use from a notebook:
    from faction_sheet import make_pdf
    make_pdf(r"C:\\path\\factions.csv", r"C:\\path\\factions.pdf")

CSV columns expected:
    Inspiration, AI Name, Feel, Difficulty, Strength, Mechanic, Pair, Complement

Faction cards are content-dense — mechanics can be 100+ words. The body text
auto-fits from 8.5pt down to 6pt before truncating with an ellipsis.

Print at 100% / "actual size" — never "fit to page".
"""

import csv
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

# ---------- Colors ----------
ACCENT = HexColor("#4A2E1F")        # deep brown — faction title accent
INSPIRATION_GREY = HexColor("#777777")
PAIR_COLOR = HexColor("#2E7D32")    # green — synergy
COMP_COLOR = HexColor("#1E5BAA")    # blue — balance
DOT_COLOR = HexColor("#BBBBBB")

# Difficulty tier colors
DIFFICULTY_COLORS = {
    "low":    HexColor("#2E7D32"),  # green
    "medium": HexColor("#B8860B"),  # amber
    "high":   HexColor("#B23A3A"),  # red
}
# Strength tier colors (slightly muted vs difficulty)
STRENGTH_COLORS = {
    "low":    HexColor("#6E6E6E"),  # grey
    "medium": HexColor("#B8860B"),  # amber
    "high":   HexColor("#5B3A8C"),  # purple
}


# ---------- CSV helpers ----------
def _norm_row(row):
    return {(k or "").strip(): (v or "").strip() for k, v in row.items()}


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


def _wrap(text, font, size, max_w):
    if not text:
        return []
    lines = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            continue
        words = para.split()
        if not words:
            continue
        cur = words[0]
        for w in words[1:]:
            if stringWidth(cur + " " + w, font, size) <= max_w:
                cur += " " + w
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def _wrap_with_bold_prefix(prefix, body, font_reg, font_bold, size, max_w):
    """Wrap text where the first word(s) of `prefix` are bold and `body` is regular.
    Returns list of segment-lists, each segment being (text, is_bold).
    """
    if not prefix and not body:
        return []
    lines = []
    space_w = stringWidth(" ", font_reg, size)

    cur = []
    cur_w = 0.0

    def can_fit(extra_w):
        return cur_w + extra_w <= max_w

    # Add prefix word-by-word as bold
    for word in prefix.split():
        ww = stringWidth(word, font_bold, size)
        extra = (space_w + ww) if cur else ww
        if can_fit(extra):
            cur.append((word, True))
            cur_w += extra
        else:
            lines.append(cur)
            cur = [(word, True)]
            cur_w = ww

    # Body words (regular)
    for word in body.split():
        ww = stringWidth(word, font_reg, size)
        extra = (space_w + ww) if cur else ww
        if can_fit(extra):
            cur.append((word, False))
            cur_w += extra
        else:
            lines.append(cur)
            cur = [(word, False)]
            cur_w = ww

    if cur:
        lines.append(cur)

    return lines


def _draw_segment_line(c, x, y, segments, font_reg, font_bold, size):
    cur_x = x
    space_w = stringWidth(" ", font_reg, size)
    for i, (word, is_bold) in enumerate(segments):
        f = font_bold if is_bold else font_reg
        c.setFont(f, size)
        if i > 0:
            cur_x += space_w
        c.drawString(cur_x, y, word)
        cur_x += stringWidth(word, f, size)


def _split_mechanic(text):
    """Split 'Name: rest of text' into (name, body). If no colon, body is the whole text."""
    m = re.match(r"^([^:]{2,60}):\s*(.*)$", text, re.DOTALL)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None, text.strip()


def _draw_chip(c, x, y, w, h, label, value, color):
    """Draw a small colored chip showing 'LABEL: value'."""
    c.setFillColor(color)
    c.roundRect(x, y, w, h, 2, stroke=0, fill=1)
    c.setFillColor(HexColor("#FFFFFF"))
    # Center text
    label_size = 6.5
    val_size = 7.5
    c.setFont("Helvetica-Bold", label_size)
    c.drawCentredString(x + w / 2, y + h - label_size - 1.5, label)
    c.setFont("Helvetica-Bold", val_size)
    c.drawCentredString(x + w / 2, y + 2, value.upper())
    c.setFillColor(black)


# ---------- Card drawing ----------
def draw_faction_card(c, x, y, row):
    inner_w = CARD_W - 2 * PAD
    cx = x + CARD_W / 2

    # Border
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.rect(x, y, CARD_W, CARD_H)

    cur_y = y + CARD_H - PAD

    # ---- Title (AI Name) ----
    name = row.get("AI Name", "") or "(Unnamed)"
    name_text, name_size = _fit(name, inner_w, "Helvetica-Bold", 13.5, 9.5)
    cur_y -= name_size
    c.setFont("Helvetica-Bold", name_size)
    c.drawCentredString(cx, cur_y, name_text)
    cur_y -= 2

    # ---- Feel (italic, colored) ----
    feel = row.get("Feel", "")
    if feel:
        cur_y -= 8
        feel_text, feel_size = _fit(feel, inner_w, "Helvetica-Oblique", 8.5, 7.0)
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Oblique", feel_size)
        c.drawCentredString(cx, cur_y, feel_text)
        c.setFillColor(black)
        cur_y -= 2

    # ---- Inspiration line (small grey) ----
    inspiration = row.get("Inspiration", "")
    if inspiration:
        cur_y -= 7
        c.setFillColor(INSPIRATION_GREY)
        c.setFont("Helvetica-Oblique", 6.5)
        c.drawCentredString(cx, cur_y, f"Inspired by: {inspiration}")
        c.setFillColor(black)
        cur_y -= 1

    # ---- Accent bar ----
    cur_y -= 5
    c.setFillColor(ACCENT)
    c.rect(x + PAD + 14, cur_y, inner_w - 28, 1.2, stroke=0, fill=1)
    c.setFillColor(black)
    cur_y -= 4

    # ---- Difficulty / Strength chips ----
    diff = (row.get("Difficulty", "") or "—").strip()
    strg = (row.get("Strength", "") or "—").strip()
    diff_color = DIFFICULTY_COLORS.get(diff.lower(), HexColor("#888888"))
    strg_color = STRENGTH_COLORS.get(strg.lower(), HexColor("#888888"))

    chip_h = 16
    chip_w = (inner_w - 6) / 2
    chip_y = cur_y - chip_h
    _draw_chip(c, x + PAD, chip_y, chip_w, chip_h, "DIFFICULTY", diff, diff_color)
    _draw_chip(c, x + PAD + chip_w + 6, chip_y, chip_w, chip_h, "STRENGTH", strg, strg_color)
    cur_y = chip_y - 5

    # ---- Reserve footer space for Pair/Complement ----
    pair = row.get("Pair", "")
    comp = row.get("Complement", "")

    # Pre-wrap footer to know its height
    footer_lines = []
    footer_size = 6.5
    footer_lh = footer_size + 1.2
    if pair:
        plines = _wrap_with_bold_prefix("Pair:", pair, "Helvetica-Oblique",
                                        "Helvetica-BoldOblique", footer_size, inner_w)
        footer_lines.append(("pair", plines))
    if comp:
        clines = _wrap_with_bold_prefix("Complement:", comp, "Helvetica-Oblique",
                                        "Helvetica-BoldOblique", footer_size, inner_w)
        footer_lines.append(("comp", clines))

    footer_h = sum(len(lines) * footer_lh for _, lines in footer_lines)
    if footer_lines:
        footer_h += 4 + 3 * (len(footer_lines) - 1)  # divider + spacing between sections
        footer_h += 4  # padding above footer

    body_top = cur_y
    body_floor = y + PAD + footer_h + 2

    # ---- Mechanic body ----
    mechanic = row.get("Mechanic", "")
    mech_name, mech_body = _split_mechanic(mechanic)

    chosen = None
    for body_size in [8.5, 8.0, 7.5, 7.0, 6.5, 6.0]:
        line_h = body_size + 1.4
        if mech_name:
            seg_lines = _wrap_with_bold_prefix(
                mech_name + ":", mech_body,
                "Helvetica", "Helvetica-Bold", body_size, inner_w
            )
        else:
            # Wrap whole thing as plain text → convert to segment format
            plain_lines = _wrap(mech_body, "Helvetica", body_size, inner_w)
            seg_lines = [[(w, False) for w in line.split()] for line in plain_lines]

        total_h = len(seg_lines) * line_h
        if total_h <= (body_top - body_floor):
            chosen = (body_size, line_h, seg_lines)
            break

    if chosen is None:
        # Take smallest size and truncate with ellipsis on last visible line
        body_size = 6.0
        line_h = body_size + 1.2
        if mech_name:
            seg_lines = _wrap_with_bold_prefix(
                mech_name + ":", mech_body,
                "Helvetica", "Helvetica-Bold", body_size, inner_w
            )
        else:
            plain_lines = _wrap(mech_body, "Helvetica", body_size, inner_w)
            seg_lines = [[(w, False) for w in line.split()] for line in plain_lines]
        avail = body_top - body_floor
        max_lines = max(1, int(avail / line_h))
        if len(seg_lines) > max_lines:
            seg_lines = seg_lines[:max_lines]
            # Add ellipsis to last line
            if seg_lines and seg_lines[-1]:
                last = seg_lines[-1]
                last_word, last_bold = last[-1]
                seg_lines[-1][-1] = (last_word + "\u2026", last_bold)
            elif seg_lines:
                seg_lines[-1] = [("\u2026", False)]
        chosen = (body_size, line_h, seg_lines)

    body_size, line_h, seg_lines = chosen

    cur_y = body_top
    for segs in seg_lines:
        cur_y -= body_size
        if segs:
            _draw_segment_line(c, x + PAD, cur_y, segs,
                               "Helvetica", "Helvetica-Bold", body_size)
        cur_y -= (line_h - body_size)

    # ---- Footer: Pair / Complement ----
    if footer_lines:
        # Divider above footer
        cur_y = y + PAD + footer_h - 2
        c.setStrokeColor(grey)
        c.setLineWidth(0.3)
        c.line(x + PAD, cur_y, x + CARD_W - PAD, cur_y)
        c.setStrokeColor(black)
        cur_y -= 3

        for i, (kind, lines) in enumerate(footer_lines):
            color = PAIR_COLOR if kind == "pair" else COMP_COLOR
            for j, segs in enumerate(lines):
                cur_y -= footer_size
                # First line: prefix in colored bold-italic; others: regular italic
                cur_x = x + PAD
                space_w = stringWidth(" ", "Helvetica-Oblique", footer_size)
                for k, (word, is_bold) in enumerate(segs):
                    if is_bold:
                        c.setFillColor(color)
                        c.setFont("Helvetica-BoldOblique", footer_size)
                    else:
                        c.setFillColor(black)
                        c.setFont("Helvetica-Oblique", footer_size)
                    if k > 0:
                        cur_x += space_w
                    c.drawString(cur_x, cur_y, word)
                    f = "Helvetica-BoldOblique" if is_bold else "Helvetica-Oblique"
                    cur_x += stringWidth(word, f, footer_size)
                cur_y -= (footer_lh - footer_size)
            if i < len(footer_lines) - 1:
                cur_y -= 1
        c.setFillColor(black)


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


def _rows_from_renown_data():
    """Build renderer rows from renown_data.FACTIONS — the single source of truth."""
    from renown_data import FACTIONS
    rows = []
    for name, f in FACTIONS.items():
        rows.append({
            "AI Name": name,
            "Inspiration": f.get("inspiration", ""),
            "Feel": f.get("feel", ""),
            "Difficulty": f.get("difficulty", ""),
            "Strength": f.get("strength", ""),
            "Mechanic": f.get("mechanic", ""),
            "Pair": f.get("pair", ""),
            "Complement": f.get("complement", ""),
        })
    return rows


def make_pdf(pdf_path, csv_path=None):
    """Default: render every faction in renown_data.FACTIONS.
    Legacy: make_pdf('factions.csv', 'out.pdf') still works (CSV mode)."""
    # Legacy positional order (csv, pdf): first arg ends in .csv and second given.
    if csv_path is not None and str(pdf_path).lower().endswith(".csv"):
        pdf_path, csv_path = csv_path, pdf_path
    if csv_path:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            rows = [_norm_row(r) for r in csv.DictReader(f)]
    else:
        rows = _rows_from_renown_data()

    c = canvas.Canvas(pdf_path, pagesize=letter)
    per_page = COLS * ROWS

    for i, row in enumerate(rows):
        slot = i % per_page
        if slot == 0 and i > 0:
            draw_crop_marks(c)
            c.showPage()

        col = slot % COLS
        r = slot // COLS
        cx = MARGIN_X + col * CARD_W
        cy = PAGE_H - MARGIN_Y - (r + 1) * CARD_H
        draw_faction_card(c, cx, cy, row)

    draw_crop_marks(c)
    c.save()
    n_pages = (len(rows) + per_page - 1) // per_page
    print(f"Wrote {pdf_path}  ({len(rows)} cards, {n_pages} page(s))")
