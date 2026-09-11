"""
Renown — Specialization card sheet generator.

Reads a CSV and lays out cards 3x3 on US Letter as a print-ready PDF.
Card size: 2.5" x 3.5" (fits standard MTG sleeves).

Install:    pip install reportlab
Use from a notebook:
    from card_sheet import make_pdf
    make_pdf(r"C:\\path\\cards.csv", r"C:\\path\\cards.pdf")

CSV columns (case-insensitive, all optional except Specialization):
    Specialization        - card name (required)
    Type                  - e.g. "Specialization", "Power Specialization"
    Unlock Requirement    - domain standing(s), e.g. "Cunning Established"
    Mastery Requirement   - other specs needed to mastery, e.g. "Academy + Inn"
    Innate Effects        - primary rules text. Use \\n for line breaks.
                            Wrap keywords in **bold**.
    Mastery Effect        - secondary, more powerful text. Same formatting rules.
    Builds Into           - comma-separated specs that this enables. Bottom-right.
    Category              - optional accent color: prowess / cunning / piety /
                            industry / nobility / civic. If blank, derived from Type.

Print at 100% / "actual size" — never "fit to page".
"""

import csv
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, grey, HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------- Symbol font ----------
# Keyword symbols need glyphs Helvetica lacks (it renders missing glyphs as a
# black box). Register EB Garamond for the symbol cells; fall back to Helvetica
# if the fonts folder isn't present. SYM_FONT is used wherever a symbol is drawn.
import os as _os
from reportlab.pdfbase import pdfmetrics as _pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as _TTFont
SYM_FONT = "Helvetica-Bold"
try:
    _fdir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fonts")
    _fpath = _os.path.join(_fdir, "EBGaramond-Bold.ttf")
    if _os.path.exists(_fpath):
        _pdfmetrics.registerFont(_TTFont("EBGaramondSym", _fpath))
        SYM_FONT = "EBGaramondSym"
except Exception:
    SYM_FONT = "Helvetica-Bold"

# ---------- Layout ----------
CARD_W = 2.5 * inch
CARD_H = 3.5 * inch
COLS, ROWS = 3, 3
PAGE_W, PAGE_H = letter
PAD = 0.12 * inch
MARGIN_X = (PAGE_W - CARD_W * COLS) / 2
MARGIN_Y = (PAGE_H - CARD_H * ROWS) / 2

# ---------- Colors ----------
CATEGORY_COLORS = {
    "prowess":   HexColor("#B23A3A"),
    "cunning":   HexColor("#5B3A8C"),
    "piety":     HexColor("#C9A227"),
    "industry":  HexColor("#3A7A4A"),
    "nobility":  HexColor("#2A4D7F"),
    "civic":     HexColor("#7A6A4A"),
}
MASTERY_ACCENT = HexColor("#8C6A1A")  # bronze/gold for the MASTERY label


# ---------- CSV helpers ----------
def _norm_row(row):
    """Lowercase + strip keys so 'Mastery Requirement' and 'mastery requirement' both work."""
    return {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}


def _get(row, *keys):
    for k in keys:
        v = row.get(k.lower())
        if v:
            v = v.strip()
            # Treat dashes / placeholders as empty
            if v in {"-", "\u2014", "\u2013", "n/a", "N/A", "none", "None"}:
                continue
            return v
    return ""


# ---------- Text helpers ----------
def _split_bold(text):
    parts = []
    for chunk in re.split(r"(\*\*[^*]+\*\*)", text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            parts.append((chunk[2:-2], True))
        else:
            parts.append((chunk, False))
    return parts


def _wrap_rich(text, font_regular, font_bold, size, max_width):
    lines = []
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
        space_w = stringWidth(" ", font_regular, size)
        for word, is_bold in tokens:
            f = font_bold if is_bold else font_regular
            ww = stringWidth(word, f, size)
            no_space = word and word[0] in ",.;:!?)"
            extra = (ww if no_space else space_w + ww) if cur else ww
            if cur_w + extra <= max_width:
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


def _draw_rich_line(c, x, y, segments, font_regular, font_bold, size):
    cur_x = x
    space_w = stringWidth(" ", font_regular, size)
    for i, (word, is_bold) in enumerate(segments):
        f = font_bold if is_bold else font_regular
        c.setFont(f, size)
        if i > 0 and not (word and word[0] in ",.;:!?)"):
            cur_x += space_w
        c.drawString(cur_x, y, word)
        cur_x += stringWidth(word, f, size)


def _fit_centered(text, max_w, font, start, floor):
    size = start
    while size > floor and stringWidth(text, font, size) > max_w:
        size -= 0.5
    if stringWidth(text, font, size) <= max_w:
        return text, size
    s = text
    while s and stringWidth(s + "\u2026", font, size) > max_w:
        s = s[:-1]
    return (s.rstrip() + "\u2026"), size


def _derive_category(type_line, unlock_line, explicit):
    if explicit:
        return explicit.lower()
    haystack = (type_line + " " + unlock_line).lower()
    for key in CATEGORY_COLORS:
        if key in haystack:
            return key
    return ""



# ---------- Equipment-on-pursuit mapping (eliminates the standalone equipment deck) ----------
# Each tier-/gate-defining pursuit card carries the equipment it unlocks. Weapon
# keywords wrap to a second line beneath each weapon. Crude starting gear + Levy
# live on a separate "starting" reference card.
def _equipment_owner_map():
    import renown_data as _rd
    OVERRIDE = {"Cavalry Spear": "Stable", "Lance": "Stable"}
    TIER_CARD = {"Cast": "Furnace", "Wrought": "Blacksmith", "Forged": "Forge",
                 "Crafted": "Advanced Blast Furnace"}
    ARMOR_CARD = {"Leather": "Tannery", "Chainmail": "Armory",
                  "Full Plate": "Gilded Foundry", "Gothic Plate": "Advanced Blast Furnace"}
    owners = {}
    def add(owner, kind, name, d, source=None):
        owners.setdefault(owner, []).append((kind, name, d, source))
    for n, w in _rd.WEAPONS.items():
        if w.get("tier") == "Crude": continue
        owner = OVERRIDE.get(n) or TIER_CARD.get(w.get("tier"))
        if owner: add(owner, "weapon", n, w)
    for n, w in _rd.RANGED.items():
        add("Fletchery", "ranged", n, w)
    for n, sh in _rd.SHIELDS.items():
        if n: add("Joinery", "shield", n, sh)
    for n, a in _rd.ARMORS.items():
        owner = ARMOR_CARD.get(n)
        if owner: add(owner, "armor", n, a)
    # ABF also surfaces the Crafted-tier shield (Heater) and ranged (Pilum) for now
    # ABF surfaces the Crafted-tier shield/ranged, but they "live" on Joinery/Fletchery —
    # mark them with a source so their keywords are defined there, not re-keyed on ABF.
    if "Heater Shield" in _rd.SHIELDS:
        add("Advanced Blast Furnace", "shield", "Heater Shield", _rd.SHIELDS["Heater Shield"], "Joinery")
    if "Pilum" in _rd.RANGED:
        add("Advanced Blast Furnace", "ranged", "Pilum", _rd.RANGED["Pilum"], "Fletchery")
    # retinue profiles fold onto their unlocking pursuit (Levy -> starting card)
    RET_CARD = {"Man-at-Arms": "Coliseum", "Sergeant": "War College",
                "Knight Templar": "Preceptory of the Knight\'s Templar"}
    for n, r in _rd.RETINUES.items():
        owner = RET_CARD.get(n)
        if owner: add(owner, "retinue", n, r)
    return owners

EQUIPMENT_BY_PURSUIT = _equipment_owner_map()

TIER_MARK = {"Crude": "1\u00b7Cr", "Cast": "2\u00b7Ca", "Wrought": "3\u00b7W",
             "Forged": "4\u00b7F", "Crafted": "5\u00b7Cf"}


# Fixed GLOBAL keyword symbols — a player learns the symbol once and it means the
# same thing on every card. Concise definitions sized for card footnotes.
KEYWORD_SYMBOL = {
    "Deadly": "\u2020", "Cleave": "\u2021", "Steady": "*", "Unwieldy": "\u00b6",
    "2H": "\u00a7", "Unstoppable": "\u00bb", "Destroy Shield": "\u25c6",
    "Deflect": "\u00ac", "Nimble": "\u25b2", "One Shot": "\u00b0",
    "-1 to Strike": "\u2212", "Immune Destroy Shield": "\u00d8", "Unbreakable": "#",
}
KEYWORD_DEF = {
    "Deadly": "nat-6 Strike: AP -5; only Parry/Recover on 6",
    "Cleave": "nat-6 Strike: roll another Strike",
    "Steady": "Init can't be lowered by Tactics",
    "Unwieldy": "Init can't be raised by Tactics",
    "2H": "no Shield",
    "Unstoppable": "ignore shield -1 to Strike; target -1 Parry, max 6+",
    "Destroy Shield": "nat-6 Strike: target loses Shield",
    "Deflect": "vs ranged: -1 Parry, no Riposte, max 6+",
    "Nimble": "+1 Init, Skirmish 1",
    "One Shot": "Skirmish 1 only",
    "-1 to Strike": "attackers take -1 to Strike",
    "Immune Destroy Shield": "shield can't be destroyed",
    "Unbreakable": "Immune Break checks",
}



def _eq_label(owner):
    import renown_data as _rd
    # human label for the unlock block based on what's on the card
    kinds = {k for k, _, _, _ in EQUIPMENT_BY_PURSUIT.get(owner, [])}
    if kinds == {"ranged"}: return "UNLOCKS — Ranged Weapons"
    if kinds == {"shield"}: return "UNLOCKS — Shields"
    if kinds == {"armor"}:  return "UNLOCKS — Armor"
    if "retinue" in kinds: return "UNLOCKS — Retinue"
    if "armor" in kinds and "weapon" in kinds: return "UNLOCKS — Weapons & Armor"
    return "UNLOCKS — Weapons"

# ---------- Card drawing ----------

def _draw_equipment_block(c, x, cur_y, inner_w, eq_items, label):
    """Render the equipment table (alternating rows, tier col, global symbols, def key).
    Returns the new cur_y. Shared by pursuit cards and the Starting Forces card."""
    if not eq_items:
        return cur_y
    # collect distinct keywords (borrowed items define theirs on their source card)
    kw_order = []
    for kind, iname, d, source in eq_items:
        if source:
            continue
        for t in (d.get("tags") or []):
            if t not in kw_order: kw_order.append(t)
        if kind == "retinue" and d.get("unbreakable") and "Unbreakable" not in kw_order:
            kw_order.append("Unbreakable")
    kw_sym = {kw: KEYWORD_SYMBOL.get(kw, "?") for kw in kw_order}

    cur_y -= 6
    c.setStrokeColor(grey); c.setLineWidth(0.4)
    c.line(x + PAD, cur_y, x + CARD_W - PAD, cur_y)
    c.setStrokeColor(black); cur_y -= 9
    c.setFont("Helvetica-Bold", 7.0)
    c.drawString(x + PAD, cur_y, label); cur_y -= 9
    is_retinue = any(k == "retinue" for k, _, _, _ in eq_items)
    c.setFont("Helvetica-Bold", 5.8)
    c.drawString(x + PAD + 2, cur_y, "Item")
    if is_retinue:
        c.drawString(x + PAD + 78, cur_y, "Strike")
        c.drawString(x + PAD + 112, cur_y, "End")
        c.drawString(x + PAD + 138, cur_y, "Mor")
    else:
        c.drawString(x + PAD + 70, cur_y, "Tier")
        c.drawString(x + PAD + 92, cur_y, "AP")
        c.drawString(x + PAD + 108, cur_y, "Init")
        c.drawString(x + PAD + 128, cur_y, "Kw")
    cur_y -= 8
    row_h = 8.5
    for ri, (kind, iname, d, source) in enumerate(eq_items):
        if ri % 2 == 0:
            c.setFillColor(HexColor("#F0F0F0"))
            c.rect(x + PAD, cur_y - 1.5, inner_w, row_h, stroke=0, fill=1)
            c.setFillColor(black)
        c.setFont("Helvetica", 6.3)
        c.drawString(x + PAD + 2, cur_y, iname[:20])
        morale = ""
        if kind in ("weapon", "ranged"):
            ap, init = str(d.get("ap","")), f"{d.get('init',0):+d}"
            syms = "".join(kw_sym.get(t, "") for t in (d.get("tags") or []))
        elif kind == "shield":
            ap, init = f"+{d.get('save_bonus','')}", f"{d.get('init',0):+d}"
            syms = "".join(kw_sym.get(t, "") for t in (d.get("tags") or []))
        elif kind == "armor":
            ap, init = f"{d.get('save','')}+", ""
            syms = "".join(kw_sym.get(t, "") for t in (d.get("tags") or []))
        elif kind == "retinue":
            ap, init = f"{d.get('to_hit','')}+", str(d.get('endurance',''))
            morale = f"{d.get('shaking','')}+"
            syms = kw_sym.get("Unbreakable", "") if d.get("unbreakable") else ""
        if source:
            syms = f"*{source}"
        if kind == "retinue":
            c.drawString(x + PAD + 78, cur_y, ap)
            c.drawString(x + PAD + 112, cur_y, init)
            c.drawString(x + PAD + 138, cur_y, morale)
            c.setFont(SYM_FONT, 6.8); c.drawString(x + PAD + 162, cur_y, syms)
        else:
            c.setFont("Helvetica", 5.8)
            c.drawString(x + PAD + 70, cur_y, TIER_MARK.get(d.get("tier"), ""))
            c.setFont("Helvetica", 6.3)
            c.drawString(x + PAD + 92, cur_y, ap)
            c.drawString(x + PAD + 108, cur_y, init)
            c.setFont(SYM_FONT, 6.8); c.drawString(x + PAD + 128, cur_y, syms)
        cur_y -= row_h
    if kw_sym:
        cur_y -= 2
        for kw, sym in kw_sym.items():
            definition = KEYWORD_DEF.get(kw, "")
            c.setFont(SYM_FONT, 5.5); c.drawString(x + PAD, cur_y, sym)
            c.setFont("Helvetica", 5.5)
            c.drawString(x + PAD + 7, cur_y, f"{kw}: {definition}" if definition else kw)
            cur_y -= 6.5
    cur_y -= 1
    return cur_y


def draw_spec_card(c, x, y, row):
    inner_w = CARD_W - 2 * PAD
    cx = x + CARD_W / 2

    # Border
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.rect(x, y, CARD_W, CARD_H)

    # ---- Pull fields ----
    name        = _get(row, "Pursuits", "name")
    type_line   = _get(row, "type")
    unlock      = _get(row, "unlock requirement", "unlock requirements", "unlocks", "unlock")
    mast_req    = _get(row, "mastery requirement", "mastery requirements", "mastery req")
    innate      = _get(row, "innate effects", "innate effect", "innate")
    mastery     = _get(row, "mastery effect", "mastery effects", "mastery")
    builds_into = _get(row, "builds into", "builds_into")
    category    = _derive_category(type_line, unlock, _get(row, "category"))
    accent      = CATEGORY_COLORS.get(category)

    # ============ HEADER (centered) ============
    cur_y = y + CARD_H - PAD

    # Name — auto-shrink, centered, bold
    name_text, name_size = _fit_centered(name, inner_w, "Helvetica-Bold", 12.0, 9.0)
    cur_y -= name_size
    c.setFont("Helvetica-Bold", name_size)
    c.drawCentredString(cx, cur_y, name_text)
    cur_y -= 3

    # Accent rule under name (if category known)
    if accent:
        cur_y -= 1
        c.setFillColor(accent)
        c.rect(x + PAD + 18, cur_y, inner_w - 36, 1.5, stroke=0, fill=1)
        c.setFillColor(black)
        cur_y -= 4

    # Type
    if type_line:
        type_text, type_size = _fit_centered(type_line, inner_w, "Helvetica-Oblique", 8.5, 7.0)
        cur_y -= type_size
        c.setFont("Helvetica-Oblique", type_size)
        c.drawCentredString(cx, cur_y, type_text)
        cur_y -= 3

    # Unlock requirement (wraps; never truncates)
    if unlock:
        u_size = 7.5
        if stringWidth(f"Unlocks: {unlock}", "Helvetica", u_size) <= inner_w:
            cur_y -= u_size
            c.setFont("Helvetica", u_size)
            c.drawCentredString(cx, cur_y, f"Unlocks: {unlock}")
            cur_y -= 2
        else:
            # Wrap into multiple centered lines
            for u_try in [7.5, 7.0, 6.5]:
                lines = _wrap_rich(f"Unlocks: {unlock}", "Helvetica", "Helvetica-Bold", u_try, inner_w)
                if len(lines) <= 3:
                    break
            for segs in lines:
                cur_y -= u_try
                if segs:
                    line_text = " ".join(w for w,_ in segs)
                    c.setFont("Helvetica", u_try)
                    c.drawCentredString(cx, cur_y, line_text)
            cur_y -= 2

    # Mastery requirement (wraps; never truncates)
    if mast_req:
        m_size = 7.5
        if stringWidth(f"Mastery: {mast_req}", "Helvetica", m_size) <= inner_w:
            cur_y -= m_size
            c.setFont("Helvetica", m_size)
            c.drawCentredString(cx, cur_y, f"Mastery: {mast_req}")
            cur_y -= 2
        else:
            for m_try in [7.5, 7.0, 6.5]:
                lines = _wrap_rich(f"Mastery: {mast_req}", "Helvetica", "Helvetica-Bold", m_try, inner_w)
                if len(lines) <= 3:
                    break
            for segs in lines:
                cur_y -= m_try
                if segs:
                    line_text = " ".join(w for w,_ in segs)
                    c.setFont("Helvetica", m_try)
                    c.drawCentredString(cx, cur_y, line_text)
            cur_y -= 2

    # Divider between header and body
    cur_y -= 3
    c.setStrokeColor(grey)
    c.setLineWidth(0.4)
    c.line(x + PAD, cur_y, x + CARD_W - PAD, cur_y)
    c.setStrokeColor(black)
    cur_y -= 4

    body_top = cur_y

    # ============ FOOTER reservation ============
    # "Builds into:" can wrap to 2 lines if long
    builds_lines = []
    if builds_into:
        builds_text = "Builds into: " + builds_into
        # Wrap as plain text, right-aligned, footer font
        for size in [6.5, 6.0]:
            tmp = _wrap_rich(builds_text, "Helvetica-Oblique", "Helvetica-BoldOblique", size, inner_w)
            if len(tmp) <= 2:
                builds_lines = tmp
                builds_size = size
                break
        else:
            builds_lines = tmp[:2]
            builds_size = 6.0

    footer_h = (len(builds_lines) * (builds_size + 1.5) + 2) if builds_lines else 2
    body_floor = y + PAD + footer_h

    # ============ BODY (Innate + Mastery) ============
    chosen = None
    for body_size in [9.0, 8.5, 8.0, 7.5, 7.0]:
        line_h = body_size + 1.5
        label_size = max(7.5, body_size - 0.5)
        label_h = label_size + 3

        innate_lines = _wrap_rich(innate, "Helvetica", "Helvetica-Bold", body_size, inner_w) if innate else []
        mastery_lines = _wrap_rich(mastery, "Helvetica", "Helvetica-Bold", body_size, inner_w) if mastery else []

        innate_h  = (label_h + len(innate_lines)  * line_h) if innate_lines  else 0
        mastery_h = (label_h + len(mastery_lines) * line_h + 4) if mastery_lines else 0  # +4 for separator above
        gap = 4 if (innate_lines and mastery_lines) else 0

        total_h = innate_h + mastery_h + gap

        if total_h <= (body_top - body_floor):
            chosen = (body_size, line_h, label_size, label_h, innate_lines, mastery_lines)
            break

    if chosen is None:
        body_size = 7.0
        line_h = body_size + 1.5
        label_size = 7.0
        label_h = label_size + 3
        innate_lines = _wrap_rich(innate, "Helvetica", "Helvetica-Bold", body_size, inner_w) if innate else []
        mastery_lines = _wrap_rich(mastery, "Helvetica", "Helvetica-Bold", body_size, inner_w) if mastery else []
        chosen = (body_size, line_h, label_size, label_h, innate_lines, mastery_lines)

    body_size, line_h, label_size, label_h, innate_lines, mastery_lines = chosen

    cur_y = body_top

    # --- Innate block (always renders; em dash if empty) ---
    cur_y -= label_size
    c.setFont("Helvetica-Bold", label_size)
    c.drawString(x + PAD, cur_y, "INNATE")
    cur_y -= 3
    if innate_lines:
        for segs in innate_lines:
            cur_y -= body_size
            if segs:
                _draw_rich_line(c, x + PAD, cur_y, segs, "Helvetica", "Helvetica-Bold", body_size)
            cur_y -= (line_h - body_size)
    else:
        cur_y -= body_size
        c.setFont("Helvetica", body_size)
        c.drawString(x + PAD, cur_y, "\u2014")
        cur_y -= (line_h - body_size)

    # --- Mastery block ---
    if mastery_lines:
        cur_y -= 4
        # subtle accent line above MASTERY
        c.setStrokeColor(MASTERY_ACCENT)
        c.setLineWidth(0.6)
        c.line(x + PAD, cur_y, x + PAD + 30, cur_y)
        c.setStrokeColor(black)
        cur_y -= 4

        cur_y -= label_size
        c.setFillColor(MASTERY_ACCENT)
        c.setFont("Helvetica-Bold", label_size)
        c.drawString(x + PAD, cur_y, "MASTERY")
        c.setFillColor(black)
        cur_y -= 3
        for segs in mastery_lines:
            cur_y -= body_size
            if segs:
                _draw_rich_line(c, x + PAD, cur_y, segs, "Helvetica", "Helvetica-Bold", body_size)
            cur_y -= (line_h - body_size)

    # ============ EQUIPMENT BLOCK (shared handler) ============
    eq_items = EQUIPMENT_BY_PURSUIT.get(name, [])
    if eq_items:
        cur_y = _draw_equipment_block(c, x, cur_y, inner_w, eq_items, _eq_label(name))

    # ============ FOOTER: Builds Into (bottom-right) ============
    if builds_lines:
        c.setFont("Helvetica-Oblique", builds_size)
        fy = y + PAD + (len(builds_lines) - 1) * (builds_size + 1.5) + 1
        for segs in builds_lines:
            # render right-aligned
            line_str = " ".join(w for w, _ in segs)
            c.drawRightString(x + CARD_W - PAD, fy, line_str)
            fy -= (builds_size + 1.5)



def draw_starting_card(c, x, y):
    """The baseline every player opens with: Levy retinue + Crude starting gear."""
    import renown_data as _rd
    c.setStrokeColor(black); c.setLineWidth(0.5); c.rect(x, y, CARD_W, CARD_H)
    inner_w = CARD_W - 2 * PAD
    cx = x + CARD_W/2; cur_y = y + CARD_H - PAD
    cur_y -= 13; c.setFont("Helvetica-Bold", 13); c.drawCentredString(cx, cur_y, "Starting Forces"); cur_y -= 5
    c.setFillColor(MASTERY_ACCENT); c.rect(x+PAD+18, cur_y, CARD_W-2*PAD-36, 1.5, stroke=0, fill=1); c.setFillColor(black); cur_y -= 8
    c.setFont("Helvetica-Oblique", 7.5); c.drawCentredString(cx, cur_y, "Every player begins with these"); cur_y -= 6

    # Levy retinue — rendered via the shared equipment handler
    lv = dict(_rd.RETINUES["Levy"])
    cur_y = _draw_equipment_block(c, x, cur_y, inner_w,
                                  [("retinue", "Levy", lv, None)], "RETINUE — Levy")
    # Crude starting weapons + Cloth armor — shared handler (tier col shows 1\u00b7Cr)
    crude = [("weapon", wn, _rd.WEAPONS[wn], None) for wn in ["Farm Tools", "Cudgel", "Pitchfork"]]
    crude.append(("armor", "Cloth", _rd.ARMORS["Cloth"], None))
    cur_y = _draw_equipment_block(c, x, cur_y, inner_w, crude, "STARTING GEAR — Crude")
    c.setFont("Helvetica-Oblique", 6.0)
    c.drawCentredString(cx, y+PAD+3, "Re-equip freely before each Battle with anything unlocked")

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


def _eff_innate(n):
    """Prepend 'Efficient X' (from the node's efficient field) to its innate text."""
    eff = n.get("efficient"); innate = n.get("innate", "") or ""
    if not eff:
        return innate
    txt = "**Efficient " + (eff if isinstance(eff, str) else ", ".join(eff)) + "**"
    return txt + ("; " + innate.lstrip("; ").strip() if innate else "")

def _rows_from_renown_data(mode="renown", players=1):
    """Build renderer rows from renown_data.NODES — the single source of truth.
    mode='renown' = all 105 pursuits; mode='escalation' = the combat subset.
    players>1 duplicates each card by its spec-tree fan-out copy count."""
    from renown_data import get_data
    copies = None
    if players and players > 1:
        import card_copies
        copies = card_copies.copy_map(mode, players)
    rows = []
    for name, n in get_data(mode).items():
        if mode == "escalation":
            # Combat cards: text comes from the escalation.ranks dict, NOT the
            # full-game innate/mastery. rank 1 -> INNATE, rank 2 -> MASTERY.
            # Non-combat type/builds-into are dropped to leave room for the
            # equipment table.
            esc = n.get("escalation", {}) or {}
            ranks = esc.get("ranks", {}) or {}
            innate_txt  = ranks.get(1, "") or ""
            mastery_txt = ranks.get(2, "") or ""
            row = _norm_row({
                "Pursuits": name,
                "Type": "",
                "Unlock Requirement": esc.get("standing", n.get("unlock", "")),
                "Mastery Requirement": n.get("mastery_req", ""),
                "Innate Effects": innate_txt,
                "Mastery Effect": mastery_txt,
                "Builds Into": "",
            })
        else:
            row = _norm_row({
                "Pursuits": name,
                "Type": n.get("type", ""),
                "Unlock Requirement": n.get("unlock", ""),
                "Mastery Requirement": n.get("mastery_req", ""),
                "Innate Effects": _eff_innate(n),
                "Mastery Effect": n.get("mastery", ""),
                "Builds Into": ", ".join(n.get("builds_into", [])),
            })
        rows.extend([row] * (copies[name] if copies else 1))
    return rows


def make_pdf(pdf_path, csv_path=None, mode="renown", players=1):
    """Default: render pursuit cards from renown_data.NODES (mode='renown'|'escalation').
    Legacy: make_pdf('specs.csv', 'out.pdf') still works (CSV mode)."""
    if csv_path is not None and str(pdf_path).lower().endswith(".csv"):
        pdf_path, csv_path = csv_path, pdf_path
    if csv_path:
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = [_norm_row(r) for r in csv.DictReader(f)]
    else:
        rows = _rows_from_renown_data(mode, players)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    per_page = COLS * ROWS

    # Starting card first (Levy + Crude gear) — only in renown/escalation full decks
    draw_starting_card(c, MARGIN_X, PAGE_H - MARGIN_Y - CARD_H)
    start_offset = 1

    for i0, row in enumerate(rows):
        i = i0 + start_offset
        slot = i % per_page
        if slot == 0 and i > 0:
            draw_crop_marks(c)
            c.showPage()

        col = slot % COLS
        r = slot // COLS
        cx = MARGIN_X + col * CARD_W
        cy = PAGE_H - MARGIN_Y - (r + 1) * CARD_H
        draw_spec_card(c, cx, cy, row)

    draw_crop_marks(c)
    c.save()
    print(f"Wrote {pdf_path}  ({len(rows)} cards, "
          f"{(len(rows) + per_page - 1) // per_page} page(s))")