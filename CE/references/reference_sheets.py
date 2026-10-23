"""
Renown — Reference sheet generators.

Contains:
1. Infrastructure single-page reference (one US Letter page, all 13 buildings)
2. Wonder cards (4 cards, 1 page)
3. Action reference cards (one card per Domain, two when its text won't fit; read from renown_data.ACTIONS)

Install:    pip install reportlab
Use from a notebook:
    from reference_sheets import (
        make_infrastructure_pdf,
        make_actions_pdf,
    )
    make_infrastructure_pdf(r"C:\\path\\infrastructure.pdf")
    make_actions_pdf(r"C:\\path\\actions.pdf")

Print at 100% / "actual size".
"""

import re
import display_pdf; display_pdf.install()   # NAME_DISPLAY on every drawn/measured string (before reportlab imports)
from display_pdf import D as _D
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, grey, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------- Layout constants ----------
PAGE_W, PAGE_H = letter
CARD_W = 2.5 * inch
CARD_H = 3.5 * inch
COLS, ROWS = 3, 3
PAD = 0.10 * inch
MARGIN_X = (PAGE_W - CARD_W * COLS) / 2
MARGIN_Y = (PAGE_H - CARD_H * ROWS) / 2

# ---------- Colors ----------
DOMAIN_COLORS = {
    "prowess":  HexColor("#B23A3A"),
    "cunning":  HexColor("#5B3A8C"),
    "piety":    HexColor("#C9A227"),
    "industry": HexColor("#3A7A4A"),
    "diplomacy": HexColor("#2A4D7F"),
}
TIER_COLORS = {
    "Primitive":     HexColor("#7A6A4A"),
    "Developed":     HexColor("#3A7A4A"),
    "Sophisticated": HexColor("#2A4D7F"),
    "Prodigious":    HexColor("#5B3A8C"),
    "Wondrous":      HexColor("#8C6A1A"),
}
HEADER_BG = HexColor("#F5F2EC")
ACCENT = HexColor("#4A2E1F")
DOT_COLOR = HexColor("#BBBBBB")

# ============================================================
# DATA — Infrastructure and Wonders (loaded from infrastructure.csv)
# ============================================================
import os
import csv

_INFRA_CSV_DEFAULT = os.path.join(os.path.dirname(__file__) or '.', 'infrastructure.csv')


def _load_infra_and_wonders(csv_path=None):
    """Load infrastructure.csv. Returns (infrastructure_list, wonders_list)
    in the tuple shapes the renderers expect.
    Infrastructure: (name, upkeep, frequency, bonus, tier, build_time, requirement)
    Wonders:        (name, effect)"""
    path = csv_path or _INFRA_CSV_DEFAULT
    infra, wonders = [], []
    if not os.path.exists(path):
        return infra, wonders
    with open(path, newline='', encoding='cp1252') as f:
        for r in csv.DictReader(f):
            if r['Category'] == 'Infrastructure':
                infra.append((
                    r['Name'],
                    r.get('Upkeep', ''),
                    r.get('Upkeep Frequency', ''),
                    r.get('Empire Bonus', ''),
                    r.get('Tier', ''),
                    r.get('Build Time', ''),
                    r.get('Requirement', ''),
                ))
            elif r['Category'] == 'Wonder':
                wonders.append((r['Name'], r.get('Empire Bonus', '')))
    # Add the generic Wonder row for the Infrastructure card-deck (placeholder)
    
    return infra, wonders


def _load_from_renown_data():
    """Build the renderer tuples from renown_data — the single source of truth.
    (infrastructure.csv is retired; _load_infra_and_wonders remains for legacy CSV use.)"""
    import renown_data as rd
    infra = [(name, str(e["upkeep"]), e["upkeep_frequency"], e["empire_bonus"],
              e["tier"], str(e["build_time"]), e["requirement"])
             for name, e in rd.INFRASTRUCTURE.items()]
    return infra


INFRASTRUCTURE = _load_from_renown_data()   # Wonders are its Wondrous tier

# ============================================================
# DATA — Actions per Domain (from renown_data: ACTIONS, ENVOY_OUTCOMES)
# ============================================================
# Each entry: (action_name, description). Description = cost and requirement (when there is one), the effect, and the
# action's own Endorsed bonus when it differs from its Domain's. Domains in resolution order.
ACTION_DOMAINS = ["Diplomacy", "Prowess", "Cunning", "Piety", "Industry"]
_GLYPHS = {"→": "to", "−": "-", "≥": ">=", "≤": "<=", "×": "x"}   # outside Helvetica's WinAnsi set


def _plain(s):
    s = str(s or "").strip()
    for a, b in _GLYPHS.items():
        s = s.replace(a, b)
    return s


def _load_actions():
    import renown_data as rd
    out = {d: [] for d in ACTION_DOMAINS}
    outcomes = getattr(rd, "ENVOY_OUTCOMES", {})
    for name, a in rd.ACTIONS.items():
        d = a.get("domain")
        if d not in out:
            continue
        parts = []
        cost = _plain(a.get("cost"))
        if cost and cost.lower() not in ("none", "0 gold", "0", "-", "—"):
            parts.append(f"Cost **{cost}.**")
        req = _plain(a.get("requires"))
        if req:
            parts.append(f"**Requires {req}.**")
        parts.append(_plain(a.get("effect")))
        end = _plain(a.get("endorsed")).rstrip(".")
        dom_end = _plain((outcomes.get(d) or {}).get("endorsed")).rstrip(".")
        if end and end.lower() != dom_end.lower():
            parts.append(f"**Endorsed:** {end}.")
        out[d].append((name, " ".join(x for x in parts if x)))
    resolve = {d: (_plain((outcomes.get(d) or {}).get("condemned")), _plain((outcomes.get(d) or {}).get("endorsed")))
               for d in ACTION_DOMAINS}
    return out, resolve


ACTIONS, DOMAIN_RESOLVE = _load_actions()

# ============================================================
# Text helpers
# ============================================================
def _split_bold(text):
    text = _D(text)   # display layer: alias whole text before split/measure
    parts = []
    for chunk in re.split(r"(\*\*[^*]+\*\*)", text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            parts.append((chunk[2:-2], True))
        else:
            parts.append((chunk, False))
    return parts


def _wrap_rich(text, font_reg, font_bold, size, max_w):
    text = _D(text)   # display layer: alias whole text before split/measure
    if not text:
        return []
    lines = []
    space_w = stringWidth(" ", font_reg, size)
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append([])
            continue
        tokens = []
        for seg, is_bold in _split_bold(paragraph):
            for word in seg.split():
                tokens.append((word, is_bold))
        cur = []
        cur_w = 0.0
        for word, is_bold in tokens:
            f = font_bold if is_bold else font_reg
            ww = stringWidth(word, f, size)
            extra = (space_w + ww) if cur else ww
            if cur_w + extra <= max_w:
                cur.append((word, is_bold))
                cur_w += extra
            else:
                if cur:
                    lines.append(cur)
                cur = [(word, is_bold)]
                cur_w = ww
        if cur:
            lines.append(cur)
    return lines


def _draw_rich_line(c, x, y, segs, font_reg, font_bold, size, color=None):
    cur_x = x
    space_w = stringWidth(" ", font_reg, size)
    if color:
        c.setFillColor(color)
    for i, (word, is_bold) in enumerate(segs):
        f = font_bold if is_bold else font_reg
        c.setFont(f, size)
        if i > 0:
            cur_x += space_w
        c.drawString(cur_x, y, word)
        cur_x += stringWidth(word, f, size)
    if color:
        c.setFillColor(black)


def _fit(text, max_w, font, start, floor):
    text = _D(text)   # display layer: alias whole text before split/measure
    size = start
    while size > floor and stringWidth(text, font, size) > max_w:
        size -= 0.5
    if stringWidth(text, font, size) <= max_w:
        return text, size
    s = text
    while s and stringWidth(s + "\u2026", font, size) > max_w:
        s = s[:-1]
    return (s.rstrip() + "\u2026"), size


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


# ============================================================
# 1. Infrastructure single-page reference
# ============================================================
def make_infrastructure_pdf(pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=letter)

    # Page header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(ACCENT)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 0.5 * inch, "INFRASTRUCTURE")
    c.setFillColor(black)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 0.5 * inch - 12,
                        "Apply to all Settlements in your Province. Build prior tier first.")

    # Table area
    table_x = 0.4 * inch
    table_y_top = PAGE_H - 1.0 * inch
    table_w = PAGE_W - 0.8 * inch

    # Column widths
    col_widths = {
        "name":   1.15 * inch,
        "tier":   0.75 * inch,
        "upkeep": 0.70 * inch,
        "build":  0.40 * inch,
        "req":    1.80 * inch,
    }
    bonus_w = table_w - sum(col_widths.values())

    # Header row
    headers = [
        ("name",   "Building"),
        ("tier",   "Tier"),
        ("upkeep", "Upkeep"),
        ("build",  "Build"),
        ("req",    "Requires"),
    ]
    header_y = table_y_top - 0.20 * inch
    c.setFillColor(HEADER_BG)
    c.rect(table_x, header_y - 4, table_w, 0.20 * inch, stroke=0, fill=1)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 8.5)
    cur_x = table_x + 4
    for key, label in headers:
        c.drawString(cur_x, header_y, label)
        cur_x += col_widths[key]
    c.drawString(cur_x, header_y, "Bonus")

    # Rows
    row_y = header_y - 0.05 * inch
    for i, (name, upkeep, freq, bonus, tier, build_time, req) in enumerate(INFRASTRUCTURE):
        # Wrap bonus to estimate row height
        bonus_lines = _wrap_rich(bonus, "Helvetica", "Helvetica-Bold", 7.5, bonus_w - 8)
        line_h = 9
        row_h = max(0.30 * inch, len(bonus_lines) * line_h + 8)

        # Alternating row background
        if i % 2 == 0:
            c.setFillColor(HexColor("#FAFAF7"))
            c.rect(table_x, row_y - row_h, table_w, row_h, stroke=0, fill=1)
            c.setFillColor(black)

        # Tier color stripe (left edge of row)
        tier_color = TIER_COLORS.get(tier, HexColor("#888888"))
        c.setFillColor(tier_color)
        c.rect(table_x, row_y - row_h, 2, row_h, stroke=0, fill=1)
        c.setFillColor(black)

        # Cells
        cell_y = row_y - 12
        cur_x = table_x + 4

        # Name (bold)
        c.setFont("Helvetica-Bold", 8.5)
        nm, _ = _fit(name, col_widths["name"] - 6, "Helvetica-Bold", 8.5, 7.0)
        c.drawString(cur_x, cell_y, nm)
        cur_x += col_widths["name"]

        # Tier (colored, auto-sized to fit column)
        c.setFillColor(tier_color)
        tier_text, tier_size = _fit(tier.upper(), col_widths["tier"] - 4,
                                    "Helvetica-Bold", 7.5, 6.0)
        c.setFont("Helvetica-Bold", tier_size)
        c.drawString(cur_x, cell_y, tier_text)
        c.setFillColor(black)
        cur_x += col_widths["tier"]

        # Upkeep
        c.setFont("Helvetica", 8)
        upkeep_text, upkeep_size = _fit(upkeep, col_widths["upkeep"] - 6, "Helvetica", 8.0, 6.5)
        c.setFont("Helvetica", upkeep_size)
        c.drawString(cur_x, cell_y, upkeep_text)
        cur_x += col_widths["upkeep"]

        # Build time
        c.setFont("Helvetica", 8)
        c.drawString(cur_x, cell_y, build_time)
        cur_x += col_widths["build"]

        # Requirement (allow 2 lines)
        req_lines = _wrap_rich(req, "Helvetica", "Helvetica-Bold", 7.5, col_widths["req"] - 4)
        req_lh = 9
        # Recompute row_h to account for requirement wrap as well
        new_row_h = max(0.30 * inch,
                        max(len(bonus_lines), len(req_lines)) * line_h + 8)
        if new_row_h != row_h:
            # Need to redraw the background since we're past it; just expand row_h
            # by drawing additional bg below
            extra = new_row_h - row_h
            if i % 2 == 0:
                c.setFillColor(HexColor("#FAFAF7"))
                c.rect(table_x, row_y - new_row_h, table_w, extra, stroke=0, fill=1)
                c.setFillColor(black)
            # Extend tier stripe
            c.setFillColor(tier_color)
            c.rect(table_x, row_y - new_row_h, 2, extra, stroke=0, fill=1)
            c.setFillColor(black)
            row_h = new_row_h
        c.setFont("Helvetica", 7.5)
        ry = row_y - 9
        for ln in req_lines:
            txt = " ".join(w for w, _ in ln) if ln else ""
            c.drawString(cur_x, ry, txt)
            ry -= req_lh
        cur_x += col_widths["req"]

        # Bonus (multi-line, rich text)
        bonus_y = row_y - 9
        for segs in bonus_lines:
            if segs:
                _draw_rich_line(c, cur_x, bonus_y, segs, "Helvetica", "Helvetica-Bold", 7.5)
            bonus_y -= line_h

        # Row separator
        c.setStrokeColor(HexColor("#DDDDDD"))
        c.setLineWidth(0.3)
        c.line(table_x, row_y - row_h, table_x + table_w, row_y - row_h)
        c.setStrokeColor(black)

        row_y -= row_h

    # Footer note
    foot_y = row_y - 0.20 * inch
    c.setFont("Helvetica-Oblique", 7.5)
    c.setFillColor(HexColor("#555555"))
    c.drawString(table_x,
                 foot_y,
                 "Wonders (Wondrous tier) are built in your Capital, have Immune Razed, and are one per game.")
    c.setFillColor(black)

    c.save()
    print(f"Wrote {pdf_path}  (1 page)")


# ============================================================
# 2. Wonder cards (4 cards, 1 page)
# ============================================================
def make_infrastructure_cards_pdf(pdf_path):
    """Render each infrastructure as a standalone card, like Wonders."""
    c = canvas.Canvas(pdf_path, pagesize=letter)

    for i, (name, upkeep, freq, bonus, tier, build_time, requirement) in enumerate(INFRASTRUCTURE):
        accent = TIER_COLORS.get(tier, HexColor("#7A6A4A"))

        slot = i % (COLS * ROWS)
        if i > 0 and slot == 0:
            draw_crop_marks(c)
            c.showPage()
        col = slot % COLS
        r = slot // COLS
        x = MARGIN_X + col * CARD_W
        y = PAGE_H - MARGIN_Y - (r + 1) * CARD_H

        inner_w = CARD_W - 2 * PAD
        cx = x + CARD_W / 2

        # Border (thicker for Wonder tier, normal for others)
        c.setStrokeColor(accent)
        c.setLineWidth(2.0 if tier == "Wondrous" else 1.2)
        c.rect(x, y, CARD_W, CARD_H)

        cur_y = y + CARD_H - PAD

        # Tier label at top
        cur_y -= 9
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(accent)
        c.drawCentredString(cx, cur_y, f"◆ {tier.upper()} INFRASTRUCTURE ◆")
        c.setFillColor(black)
        cur_y -= 6

        # Name
        name_text, name_size = _fit(name, inner_w, "Helvetica-Bold", 14.0, 10.0)
        cur_y -= name_size
        c.setFont("Helvetica-Bold", name_size)
        c.drawCentredString(cx, cur_y, name_text)
        cur_y -= 6

        # Accent rule
        c.setFillColor(accent)
        c.rect(x + PAD + 18, cur_y, inner_w - 36, 1.5, stroke=0, fill=1)
        c.setFillColor(black)
        cur_y -= 8

        # Stats line: Build Time · Upkeep · Frequency
        c.setFont("Helvetica-Oblique", 7.5)
        c.setFillColor(HexColor("#666666"))
        stats = f"Build Time {build_time} · Upkeep {upkeep}"
        if freq and freq != "—":
            stats += f" {freq}"
        c.drawCentredString(cx, cur_y, stats)
        cur_y -= 9

        # Requirement
        if requirement and requirement != "None":
            req_text, req_size = _fit(f"Requires: {requirement}", inner_w, "Helvetica-Oblique", 7.5, 6.0)
            c.setFont("Helvetica-Oblique", req_size)
            c.drawCentredString(cx, cur_y, req_text)
            cur_y -= 9
        else:
            c.drawCentredString(cx, cur_y, "No prerequisite")
            cur_y -= 9
        c.setFillColor(black)
        cur_y -= 6

        # Effect — auto-fit
        chosen = None
        for size in [11.0, 10.0, 9.5, 9.0, 8.5, 8.0]:
            line_h = size + 2
            lines = _wrap_rich(bonus, "Helvetica", "Helvetica-Bold", size, inner_w)
            if len(lines) * line_h <= (cur_y - y - PAD - 6):
                chosen = (size, line_h, lines)
                break
        if chosen is None:
            size = 8.0
            line_h = size + 2
            lines = _wrap_rich(bonus, "Helvetica", "Helvetica-Bold", size, inner_w)
            chosen = (size, line_h, lines)

        size, line_h, lines = chosen
        for segs in lines:
            cur_y -= size
            if segs:
                _draw_rich_line(c, x + PAD, cur_y, segs, "Helvetica", "Helvetica-Bold", size)
            cur_y -= (line_h - size)

    draw_crop_marks(c)
    c.save()
    pages = (len(INFRASTRUCTURE) + COLS * ROWS - 1) // (COLS * ROWS)
    print(f"Wrote {pdf_path}  ({len(INFRASTRUCTURE)} cards, {pages} page(s))")


def make_buildings_pdf(pdf_path):
    """Combined PDF: every infrastructure card followed by every wonder card,
    paginated continuously. Both share the same tier-color border scheme and
    layout grid."""
    c = canvas.Canvas(pdf_path, pagesize=letter)

    wonder_accent = HexColor("#8C6A1A")  # bronze
    page_slots = COLS * ROWS

    # Combine into a single iteration list, each entry tagged as 'infra' or 'wonder'
    items = [('infra', tup) for tup in INFRASTRUCTURE]

    for i, (kind, payload) in enumerate(items):
        slot = i % page_slots
        if i > 0 and slot == 0:
            draw_crop_marks(c)
            c.showPage()
        col = slot % COLS
        r = slot // COLS
        x = MARGIN_X + col * CARD_W
        y = PAGE_H - MARGIN_Y - (r + 1) * CARD_H

        inner_w = CARD_W - 2 * PAD
        cx = x + CARD_W / 2

        if kind == 'infra':
            name, upkeep, freq, bonus, tier, build_time, requirement = payload
            accent = TIER_COLORS.get(tier, HexColor("#7A6A4A"))

            # Border
            c.setStrokeColor(accent)
            c.setLineWidth(2.0 if tier == "Wondrous" else 1.2)
            c.rect(x, y, CARD_W, CARD_H)

            cur_y = y + CARD_H - PAD

            # Tier label
            cur_y -= 9
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColor(accent)
            c.drawCentredString(cx, cur_y, f"◆ {tier.upper()} INFRASTRUCTURE ◆")
            c.setFillColor(black)
            cur_y -= 6

            # Name
            name_text, name_size = _fit(name, inner_w, "Helvetica-Bold", 14.0, 10.0)
            cur_y -= name_size
            c.setFont("Helvetica-Bold", name_size)
            c.drawCentredString(cx, cur_y, name_text)
            cur_y -= 6

            # Accent rule
            c.setFillColor(accent)
            c.rect(x + PAD + 18, cur_y, inner_w - 36, 1.5, stroke=0, fill=1)
            c.setFillColor(black)
            cur_y -= 8

            # Stats
            c.setFont("Helvetica-Oblique", 7.5)
            c.setFillColor(HexColor("#666666"))
            stats = f"Build Time {build_time} · Upkeep {upkeep}"
            if freq and freq != "—":
                stats += f" {freq}"
            c.drawCentredString(cx, cur_y, stats)
            cur_y -= 9

            # Requirement
            if requirement and requirement != "None":
                req_text, req_size = _fit(f"Requires: {requirement}", inner_w, "Helvetica-Oblique", 7.5, 6.0)
                c.setFont("Helvetica-Oblique", req_size)
                c.drawCentredString(cx, cur_y, req_text)
                cur_y -= 9
            else:
                c.drawCentredString(cx, cur_y, "No prerequisite")
                cur_y -= 9
            c.setFillColor(black)
            cur_y -= 6

            # Effect
            chosen = None
            for size in [11.0, 10.0, 9.5, 9.0, 8.5, 8.0]:
                line_h = size + 2
                lines = _wrap_rich(bonus, "Helvetica", "Helvetica-Bold", size, inner_w)
                if len(lines) * line_h <= (cur_y - y - PAD - 6):
                    chosen = (size, line_h, lines)
                    break
            if chosen is None:
                size = 8.0
                line_h = size + 2
                lines = _wrap_rich(bonus, "Helvetica", "Helvetica-Bold", size, inner_w)
                chosen = (size, line_h, lines)
            size, line_h, lines = chosen
            for segs in lines:
                cur_y -= size
                if segs:
                    _draw_rich_line(c, x + PAD, cur_y, segs, "Helvetica", "Helvetica-Bold", size)
                cur_y -= (line_h - size)

        else:  # wonder
            name, effect = payload
            accent = wonder_accent

            # Border (thicker for Wonder)
            c.setStrokeColor(accent)
            c.setLineWidth(2.0)
            c.rect(x, y, CARD_W, CARD_H)

            cur_y = y + CARD_H - PAD

            # WONDER label
            cur_y -= 9
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColor(accent)
            c.drawCentredString(cx, cur_y, "✦ WORLD WONDER ✦")
            c.setFillColor(black)
            cur_y -= 6

            # Name
            name_text, name_size = _fit(name, inner_w, "Helvetica-Bold", 14.0, 10.0)
            cur_y -= name_size
            c.setFont("Helvetica-Bold", name_size)
            c.drawCentredString(cx, cur_y, name_text)
            cur_y -= 6

            # Accent rule
            c.setFillColor(accent)
            c.rect(x + PAD + 18, cur_y, inner_w - 36, 1.5, stroke=0, fill=1)
            c.setFillColor(black)
            cur_y -= 8

            # Stats lines
            c.setFont("Helvetica-Oblique", 7.5)
            c.setFillColor(HexColor("#666666"))
            c.drawCentredString(cx, cur_y, "Build Time 10 · Upkeep 200 · Built in Capital")
            c.drawCentredString(cx, cur_y - 9, "Cannot be Razed · Unique (1 per game)")
            c.setFillColor(black)
            cur_y -= 24

            # Effect
            chosen = None
            for size in [11.0, 10.0, 9.5, 9.0, 8.5]:
                line_h = size + 2
                lines = _wrap_rich(effect, "Helvetica", "Helvetica-Bold", size, inner_w)
                if len(lines) * line_h <= (cur_y - y - PAD - 12):
                    chosen = (size, line_h, lines)
                    break
            if chosen is None:
                size = 8.5
                line_h = size + 2
                lines = _wrap_rich(effect, "Helvetica", "Helvetica-Bold", size, inner_w)
                chosen = (size, line_h, lines)
            size, line_h, lines = chosen
            for segs in lines:
                cur_y -= size
                if segs:
                    _draw_rich_line(c, x + PAD, cur_y, segs, "Helvetica", "Helvetica-Bold", size)
                cur_y -= (line_h - size)

    draw_crop_marks(c)
    c.save()
    total_cards = len(items)
    pages = (total_cards + page_slots - 1) // page_slots
    print(f"Wrote {pdf_path}  ({total_cards} cards, {pages} page(s))")


# ============================================================
# 3. Action reference cards (5 cards, one per Domain)
# ============================================================
def _draw_action_card(c, x, y, domain, actions, condemn, endorsed, part=""):
    inner_w = CARD_W - 2 * PAD
    cx = x + CARD_W / 2
    accent = DOMAIN_COLORS[domain.lower()]

    # Border
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.rect(x, y, CARD_W, CARD_H)

    cur_y = y + CARD_H - PAD

    # Domain title
    cur_y -= 14
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(accent)
    c.drawCentredString(cx, cur_y, domain.upper() + ("  " + part if part else ""))
    c.setFillColor(black)
    cur_y -= 4

    # "ACTIONS" subtitle
    cur_y -= 8
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(cx, cur_y, "Domain Actions")
    cur_y -= 4

    # Accent bar
    c.setFillColor(accent)
    c.rect(x + PAD + 14, cur_y, inner_w - 28, 1.5, stroke=0, fill=1)
    c.setFillColor(black)
    cur_y -= 6

    # Reserve footer for Condemn / Endorsed
    footer_size = 6.5
    footer_lh = footer_size + 1.5
    cond_lines = _wrap_rich(condemn, "Helvetica", "Helvetica-Bold", footer_size, inner_w - 50)
    end_lines = _wrap_rich(endorsed, "Helvetica", "Helvetica-Bold", footer_size, inner_w - 50)
    footer_h = (len(cond_lines) + len(end_lines)) * footer_lh + 14

    body_top = cur_y
    body_floor = y + PAD + footer_h

    # Auto-fit body
    chosen = None
    for body_size in [8.5, 8.0, 7.5, 7.0, 6.5, 6.0]:
        line_h = body_size + 1.4
        action_data = []
        total_h = 0
        label_size = body_size
        for name, desc in actions:
            desc_lines = _wrap_rich(desc, "Helvetica", "Helvetica-Bold", body_size, inner_w)
            action_data.append((name, desc_lines))
            total_h += label_size + 2 + len(desc_lines) * line_h + 4
        total_h -= 4
        if total_h <= (body_top - body_floor):
            chosen = (body_size, line_h, label_size, action_data)
            break
    if chosen is None:
        body_size = 6.0
        line_h = body_size + 1.2
        action_data = []
        for name, desc in actions:
            desc_lines = _wrap_rich(desc, "Helvetica", "Helvetica-Bold", body_size, inner_w)
            action_data.append((name, desc_lines))
        chosen = (body_size, line_h, body_size, action_data)

    body_size, line_h, label_size, action_data = chosen

    cur_y = body_top
    for i, (name, desc_lines) in enumerate(action_data):
        if i > 0:
            cur_y -= 3
        cur_y -= label_size
        c.setFillColor(accent)
        c.setFont("Helvetica-Bold", label_size)
        c.drawString(x + PAD, cur_y, name.upper())
        c.setFillColor(black)
        cur_y -= 2
        for segs in desc_lines:
            cur_y -= body_size
            if segs:
                _draw_rich_line(c, x + PAD, cur_y, segs,
                                "Helvetica", "Helvetica-Bold", body_size)
            cur_y -= (line_h - body_size)

    # Footer: Condemn / Endorsed
    foot_y = y + PAD + footer_h - 2
    c.setStrokeColor(grey)
    c.setLineWidth(0.3)
    c.line(x + PAD, foot_y, x + CARD_W - PAD, foot_y)
    c.setStrokeColor(black)
    foot_y -= 3

    # Condemned
    foot_y -= footer_size
    c.setFillColor(HexColor("#B23A3A"))
    c.setFont("Helvetica-Bold", footer_size)
    c.drawString(x + PAD, foot_y, "CONDEMN:")
    c.setFillColor(black)
    label_w = stringWidth("CONDEMN: ", "Helvetica-Bold", footer_size)
    cur_x = x + PAD + label_w
    if cond_lines:
        first = cond_lines[0]
        _draw_rich_line(c, cur_x, foot_y, first,
                        "Helvetica", "Helvetica-Bold", footer_size)
        for segs in cond_lines[1:]:
            foot_y -= footer_lh
            _draw_rich_line(c, x + PAD, foot_y, segs,
                            "Helvetica", "Helvetica-Bold", footer_size)
    foot_y -= footer_lh

    # Endorsed
    foot_y -= 0
    c.setFillColor(HexColor("#2E7D32"))
    c.setFont("Helvetica-Bold", footer_size)
    c.drawString(x + PAD, foot_y, "ENDORSE:")
    c.setFillColor(black)
    label_w = stringWidth("ENDORSE: ", "Helvetica-Bold", footer_size)
    cur_x = x + PAD + label_w
    if end_lines:
        first = end_lines[0]
        _draw_rich_line(c, cur_x, foot_y, first,
                        "Helvetica", "Helvetica-Bold", footer_size)
        for segs in end_lines[1:]:
            foot_y -= footer_lh
            _draw_rich_line(c, x + PAD, foot_y, segs,
                            "Helvetica", "Helvetica-Bold", footer_size)


MIN_ACTION_SIZE = 6.5   # a Domain whose actions need smaller type than this is split across cards


def _card_room(condemn, endorsed):
    """Height left for the actions on one card (same layout as _draw_action_card)."""
    inner_w = CARD_W - 2 * PAD
    footer_h = (len(_wrap_rich(condemn, "Helvetica", "Helvetica-Bold", 6.5, inner_w - 50)) +
                len(_wrap_rich(endorsed, "Helvetica", "Helvetica-Bold", 6.5, inner_w - 50))) * (6.5 + 1.5) + 14
    return (CARD_H - PAD - 36) - (PAD + footer_h)


def _card_need(actions, size=MIN_ACTION_SIZE):
    inner_w = CARD_W - 2 * PAD
    return sum(size + 2 + len(_wrap_rich(desc, "Helvetica", "Helvetica-Bold", size, inner_w)) * (size + 1.4) + 4
               for _, desc in actions) - 4


def _partitions(items):
    """Every way to group items (each group keeps the items' order); small n only (5 actions -> 52 groupings)."""
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in _partitions(rest):
        yield [[first]] + p
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]


def _split_domain(actions, room):
    """Fewest cards that each fit at MIN_ACTION_SIZE; among those, the most even split. Cards follow the first
    action they hold, and each card lists its actions in data order."""
    best = None
    for groups in _partitions(list(actions)):
        groups = sorted(groups, key=lambda g: actions.index(g[0]))
        needs = [_card_need(g) for g in groups]
        if any(nd > room and len(g) > 1 for g, nd in zip(groups, needs)):
            continue                                 # a card may overrun only when one action alone is too long
        key = (len(groups), max(needs))
        if best is None or key < best[0]:
            best = (key, groups)
    return best[1] if best else [[a] for a in actions]


def _action_cards():
    """[(domain, part label, actions)]: each Domain on as few cards as keep its type at MIN_ACTION_SIZE or larger."""
    cards = []
    for domain in ACTION_DOMAINS:
        condemn, endorsed = DOMAIN_RESOLVE[domain]
        groups = _split_domain(ACTIONS[domain], _card_room(condemn, endorsed))
        for i, g in enumerate(groups):
            cards.append((domain, f"{i + 1}/{len(groups)}" if len(groups) > 1 else "", g))
    return cards


def make_actions_pdf(pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    cards = _action_cards()
    per_page = COLS * ROWS
    for i, (domain, part, acts) in enumerate(cards):
        if i and i % per_page == 0:
            draw_crop_marks(c)
            c.showPage()
        k = i % per_page
        x = MARGIN_X + (k % COLS) * CARD_W
        y = PAGE_H - MARGIN_Y - (k // COLS + 1) * CARD_H
        condemn, endorsed = DOMAIN_RESOLVE[domain]
        _draw_action_card(c, x, y, domain, acts, condemn, endorsed, part)

    draw_crop_marks(c)
    c.save()
    pages = (len(cards) + per_page - 1) // per_page
    print(f"Wrote {pdf_path}  ({len(cards)} cards, {pages} page{'s' if pages > 1 else ''})")


if __name__ == "__main__":
    import sys
    make_actions_pdf(sys.argv[1] if len(sys.argv) > 1 else "action_cards.pdf")
