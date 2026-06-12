"""
Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator.

Creates one PDF per card type (or one combined PDF with all of them).
Card size: 2.5" x 3.5" (fits standard MTG sleeves).

Install:    pip install reportlab
Use from a notebook:
    from equipment_sheet import (
        make_weapons_pdf, make_ranged_pdf, make_shields_pdf,
        make_armor_pdf, make_retinues_pdf,
        make_infrastructure_pdf, make_alliances_pdf,
        make_all_pdf,
    )
    make_all_pdf(r"C:\\path\\everything.pdf")

To rebalance: edit the WEAPONS / RANGED / SHIELDS / ARMOR / RETINUES /
INFRASTRUCTURE / ALLIANCES tables near the top of this file.
To add or rewrite a keyword definition, edit GLOSSARY.

Print at 100% / "actual size" — never "fit to page".
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

# ---------- Colors ----------
TYPE_COLORS = {
    "Weapon":         HexColor("#B23A3A"),   # red
    "Ranged Weapon":  HexColor("#3A7A4A"),   # green
    "Shield":         HexColor("#2A4D7F"),   # blue
    "Armor":          HexColor("#5C5C5C"),   # graphite
    "Retinue Type":   HexColor("#5B3A8C"),   # purple
    "Infrastructure": HexColor("#7A6A4A"),   # tan/civic
    "Alliance":       HexColor("#1E5BAA"),   # diplomatic blue
}

# Per-alliance accent (overrides Alliance default if the alliance name maps here)
ALLIANCE_ACCENTS = {
    "Peace Treaty (default)": HexColor("#6E6E6E"),  # grey — neutral default
    "Non-Aggression Pact":    HexColor("#7A6A4A"),  # tan — cautious peace
    "Trade Agreement":        HexColor("#3A7A4A"),  # green — economy
    "Defensive Alliance":     HexColor("#2A4D7F"),  # blue — protection
    "Military Alliance":      HexColor("#B23A3A"),  # red — warfare
    "Vassal / Suzerain":      HexColor("#5B3A8C"),  # purple — dominion
}

# Body-block accent for the secondary section (Mastery / Restrictions)
SECONDARY_ACCENT = HexColor("#8C6A1A")

DOT_COLOR = HexColor("#BBBBBB")

# ---------- Glossary ----------
# Keyword definitions come from renown_data — the single source of truth.
# Editing renown_data.GLOSSARY renames/redefines keywords here automatically.
from renown_data import GLOSSARY

# Legacy spellings/names that may still appear in equipment.csv Effects text,
# mapped to the canonical GLOSSARY keys.
ALIASES = {
    "Shatter Armour": "Deadly",
    "Shatter Armor":  "Deadly",
    "Regenerate":     "Recover",
    "Rend":           "Serrated",
    "-1TBH":          "-1 to Strike",
    "Unshakable":     "Unbreakable",
    "Steadfast":      "Immune Panic",
}

import os
import csv

# ---------- Equipment data loaded from equipment.csv ----------
# All equipment lives in equipment.csv as a single file with a Category column.
# This module loads it on import and presents per-category lists in the same
# tuple shapes the renderers expect.

_EQ_CSV_DEFAULT = os.path.join(os.path.dirname(__file__) or '.', 'equipment.csv')


def _read_csv_rows(path):
    """Read a CSV with encoding fallback (UTF-8 first, then cp1252 for
    Excel re-saves) and strip Excel text-escape apostrophes from values."""
    last_err = None
    for enc in ('utf-8-sig', 'cp1252'):
        try:
            with open(path, newline='', encoding=enc) as f:
                rows = list(csv.DictReader(f))
            break
        except UnicodeDecodeError as e:
            last_err = e
    else:
        raise last_err
    for r in rows:
        for k, v in r.items():
            if isinstance(v, str):
                r[k] = v.strip().lstrip("'").strip()
    return rows


def _load_equipment(csv_path=None):
    """Load equipment.csv. Returns (weapons, ranged, shields, armor, retinues)
    as lists of tuples in the same shapes the renderers expect."""
    path = csv_path or _EQ_CSV_DEFAULT
    if not os.path.exists(path):
        return [], [], [], [], []

    weapons, ranged, shields, armor, retinues = [], [], [], [], []
    for r in _read_csv_rows(path):
        cat = r['Category']
        name = r['Name']
        tier = r.get('Tier', '') or ''
        effects = r.get('Effects', '') or ''
        unlock = (r.get('Pursuit Unlock') or r.get('Specialization Unlock')
                  or '') or 'None'
        note = (r.get('Note') or '').lstrip('*').strip()
        if cat == 'Weapon':
            weapons.append((name, r.get('AP', ''), r.get('Initiative', ''),
                            effects, tier, unlock, note))
        elif cat == 'Ranged':
            ranged.append((name, r.get('AP', ''), r.get('Initiative', ''),
                           effects, tier, unlock, note))
        elif cat == 'Shield':
            shields.append((name, r.get('Save', ''), r.get('Initiative', ''),
                            effects, tier, unlock, note))
        elif cat == 'Armor':
            armor.append((name, r.get('Save', ''), effects, tier,
                          unlock, note))
        elif cat == 'Retinue':
            retinues.append((name, r.get('Cost', ''),
                 r.get('To Hit') or r.get('Strike', ''),
                 r.get('Endurance', ''),
                 r.get('Shaking') or r.get('Morale', ''),
                 unlock, note))
    return weapons, ranged, shields, armor, retinues


def _load_from_renown_data():
    """Build the renderer tuples from renown_data — the single source of truth.
    (equipment.csv is retired; _load_equipment remains for legacy CSV use.)"""
    import renown_data as rd

    def _i(v):  # signed init display
        return f"+{v}" if v > 0 else str(v)
    def _fx(tags):
        return ", ".join(tags) if tags else "None"

    tier_unlock = {t: (rd.TIER_UNLOCK.get(t) or "None") for t in (rd.TIERS + [None])}
    weapons = [(n, str(w["ap"]), _i(w["init"]), _fx(w["tags"]), w["tier"],
                tier_unlock.get(w["tier"], "None"), w.get("note", "")) for n, w in rd.WEAPONS.items()]
    ranged = [(n, str(w["ap"]), _i(w["init"]), _fx(w["tags"]), w["tier"],
               tier_unlock.get(w["tier"], "None"), w.get("note", "")) for n, w in rd.RANGED.items()]
    shields = [(n, f"+{sh['save_bonus']}", _i(sh["init"]), _fx(sh["tags"]), sh["tier"] or "",
                tier_unlock.get(sh["tier"], "None"), "")
               for n, sh in rd.SHIELDS.items() if n]
    armor = [(n, f"{a['save']}+", _fx(a["tags"]), a["tier"],
              tier_unlock.get(a["tier"], "None"), "") for n, a in rd.ARMORS.items()]
    retinue_unlock = {"Levy": "None", "Man-at-Arms": "Coliseum",
                      "Sergeant": "War College", "Knight Templar": "Preceptory"}
    retinues = [(n, str(r["cost"]), f"{r['to_hit']}+", str(r["endurance"]), f"{r['shaking']}+",
                 retinue_unlock.get(n, "None"),
                 "Unbreakable" if r.get("unbreakable") else "")
                for n, r in rd.RETINUES.items()]
    return weapons, ranged, shields, armor, retinues


WEAPONS, RANGED, SHIELDS, ARMOR, RETINUES = _load_from_renown_data()

# ---------- Infrastructure loaded from infrastructure.csv ----------
# The renderer needs tuple shape (name, tier, cost, slots, income, effect, prereq).
# infrastructure.csv stores (Name, Category, Upkeep, Upkeep Frequency, Empire Bonus, Tier, Build Time, Requirement).
# We adapt: tier->Tier, cost->Upkeep, slots="0" (infra doesn't consume slots),
# income="—" (Empire Bonus is the effect text), effect->Empire Bonus, prereq->Requirement.

_INFRA_CSV_DEFAULT = os.path.join(os.path.dirname(__file__) or '.', 'infrastructure.csv')


def _load_infrastructure(csv_path=None):
    """Load infrastructure rows from infrastructure.csv. Excludes Wonders."""
    path = csv_path or _INFRA_CSV_DEFAULT
    if not os.path.exists(path):
        return []
    out = []
    for r in _read_csv_rows(path):
        if r['Category'] != 'Infrastructure':
            continue
        name = r['Name']
        tier = r.get('Tier', '')
        cost = r.get('Upkeep', '')
        effect = r.get('Empire Bonus', '')
        prereq = r.get('Requirement', '') or None
        if prereq == 'None':
            prereq = None
        out.append((name, tier, cost, "0", "—", effect, prereq))
    return out


INFRASTRUCTURE = _load_infrastructure()

# ALLIANCES: (name, vote_cost, duration, benefits, restrictions, breaking) — per Rules §Treaties & Alliances
ALLIANCES = [
    ("Peace Treaty (default)",
     "Sign Treaty action", "Truce Timer 5 from start of game or signing",
     "Not at War.\nNot trading.",
     "Cannot Declare War while Truce Timer is active.",
     "End Treaty action, or expires when Truce Timer reaches 0."),

    ("Non-Aggression Pact",
     "Sign Treaty action", "Until ended",
     "Neither party may Declare War on the other.",
     "Cannot Declare War on the other party.",
     "End Treaty action. Both Players gain Truce Timer 5."),

    ("Trade Agreement",
     "Sign Treaty action", "Until ended",
     "Peace Treaty plus Trade.\n100 x Host's Trading Spec count, max 1000 per partner.\nRequires both Players to border and have active Dirt Roads.",
     "Neither party may Declare War while active.",
     "End Treaty at any time. Player who ends it gets one more Trade Income next time they are Host."),

    ("Defensive Alliance",
     "Sign Treaty action (Viscount)", "Until ended",
     "If any member is declared war upon, all members declare war on the attacker.\nMembers count as Allied Players.",
     "Peace Treaty requires unanimous agreement.\nWar Declaration is immediate.",
     "End Treaty (Alliance acting requires all Allies to agree)."),

    ("Military Alliance",
     "Sign Treaty action (Baron)", "Until ended",
     "If any member goes to war, all must declare war (their next action).\nMembers count as Allied Players.",
     "Peace Treaty requires unanimous agreement.\nAlliance may cast out a member via End Treaty if all others agree.",
     "End Treaty (Alliance acting requires all Allies to agree)."),

    ("Vassal / Suzerain",
     "Conquest", "Permanent",
     "Suzerain collects: half of Vassal's Trade Income from other Players\nand the first 3 Influence the Vassal generates each turn.\nVassal counts in Military and Defensive Alliance with Suzerain.\nMutual Exchange (Empire Phase) allowed: up to 2000 gold, settlements, or forces.",
     "Vassal cannot perform Nobility actions and cannot be the target of Nobility actions.\nVassal's treaties exactly mirror Suzerain.",
     "If the Suzerain becomes vassalized, both the original Vassal and the Suzerain become Vassals to the new Suzerain."),
]


# ---------- Title-case helper ("to" and "be" stay lowercase) ----------
_LOWER_WORDS = {"to", "be", "of", "the"}


def _smart_title(s):
    if not s:
        return s
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


def _draw_dotted_row(c, x, y, label, value, size, max_w,
                     left_font="Helvetica-Bold", right_font="Helvetica-Bold",
                     value_color=None):
    c.setFillColor(black)
    c.setFont(left_font, size)
    c.drawString(x, y, label)

    label_w = stringWidth(label, left_font, size)
    value_w = stringWidth(value, right_font, size)
    gap = 3
    dot_area = max_w - label_w - value_w - 2 * gap
    dot_w = stringWidth(".", "Helvetica", size)
    if dot_area > dot_w * 2 and dot_w > 0:
        n_dots = int(dot_area / dot_w)
        c.setFillColor(DOT_COLOR)
        c.setFont("Helvetica", size)
        c.drawString(x + label_w + gap, y, "." * n_dots)

    c.setFillColor(value_color or black)
    c.setFont(right_font, size)
    c.drawRightString(x + max_w, y, value)
    c.setFillColor(black)


# ---------- Keyword extraction ----------
def extract_keywords(*text_blocks):
    """Find canonical glossary keywords mentioned in any of the text blocks."""
    combined = " ".join(b for b in text_blocks if b)
    if not combined:
        return []

    found = []
    seen = set()
    # Search canonical first, then aliases. Sort by length DESC so longer matches first.
    all_terms = list(GLOSSARY.keys()) + list(ALIASES.keys())
    for term in sorted(all_terms, key=lambda t: -len(t)):
        canonical = ALIASES.get(term, term)
        if canonical in seen:
            continue
        if re.search(r"\b" + re.escape(term) + r"\b", combined, re.IGNORECASE):
            found.append(canonical)
            seen.add(canonical)
    return found


# ---------- Card spec builders ----------
def weapon_to_spec(row):
    name, ap, init, effect, tier, unlock, note = row
    return {
        "name": name, "type": "Weapon", "tier": tier,
        "unlock": None if unlock == "None" else unlock,
        "stats": [("AP", ap), ("Initiative", init)],
        "effect": None if effect == "None" else effect,
        "note": note or None,
    }


def ranged_to_spec(row):
    name, ap, init, effect, tier, unlock, note = row
    return {
        "name": name, "type": "Ranged Weapon", "tier": tier,
        "unlock": None if unlock == "None" else unlock,
        "stats": [("AP", ap), ("Initiative", init)],
        "effect": None if effect == "None" else effect,
        "note": note or None,
    }


def shield_to_spec(row):
    name, save, init, effect, tier, unlock, note = row
    return {
        "name": name, "type": "Shield", "tier": tier,
        "unlock": None if unlock == "None" else unlock,
        "stats": [("Save", save), ("Initiative", init)],
        "effect": None if effect == "None" else effect,
        "note": note or None,
    }


def armor_to_spec(row):
    name, save, effect, tier, unlock, note = row
    return {
        "name": name, "type": "Armor", "tier": tier,
        "unlock": None if unlock == "None" else unlock,
        "stats": [("Save", save)],
        "effect": None if effect in ("", "None") else effect,
        "note": note or None,
    }


def retinue_to_spec(row):
    name, cost, to_hit, end, shaking, unlock, note = row
    return {
        "name": name, "type": "Retinue Type", "tier": None,
        "unlock": None if unlock == "None" else unlock,
        "stats": [
            ("Cost", cost),
            ("Strike", to_hit),
            ("Endurance", end),
            ("Morale", shaking),
        ],
        "effect": None,
        "note": note or None,
    }


def infrastructure_to_spec(row):
    name, tier, cost, slots, income, effect, prereq = row
    stats = [("Cost", cost), ("Slots", slots)]
    if income and income != "—":
        stats.append(("Income", income))
    return {
        "name": name, "type": "Infrastructure",
        "tier": tier or None,
        "unlock": prereq,
        "stats": stats,
        "effect": effect or None,
    }


def alliance_to_spec(row):
    name, vote_cost, duration, benefits, restrictions, breaking = row
    stats = []
    if vote_cost and vote_cost != "—":
        stats.append(("Vote Cost", vote_cost))
    if duration and duration != "—":
        stats.append(("Duration", duration))
    return {
        "name": name, "type": "Alliance",
        "tier": None, "unlock": None,
        "stats": stats,
        "benefits": benefits or None,
        "restrictions": restrictions or None,
        "breaking": breaking or None,
    }


# ---------- Card drawing ----------
def draw_equipment_card(c, x, y, spec):
    inner_w = CARD_W - 2 * PAD
    cx = x + CARD_W / 2
    accent = TYPE_COLORS.get(spec["type"], HexColor("#5C2A1E"))

    # Border
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.rect(x, y, CARD_W, CARD_H)

    cur_y = y + CARD_H - PAD

    # ---- Header ----
    # Name (centered, bold)
    name_text, name_size = _fit(spec["name"], inner_w, "Helvetica-Bold", 13.0, 9.5)
    cur_y -= name_size
    c.setFont("Helvetica-Bold", name_size)
    c.drawCentredString(cx, cur_y, name_text)
    cur_y -= 4

    # Type (italic, centered, colored)
    cur_y -= 8.5
    c.setFillColor(accent)
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawCentredString(cx, cur_y, spec["type"])
    c.setFillColor(black)
    cur_y -= 2

    # Tier / Unlock line
    parts = [p for p in [spec.get("tier"), spec.get("unlock")] if p]
    if parts:
        tu_line = " / ".join(parts)
        # Auto-shrink for long combined lines (Knight's Templar)
        tu_text, tu_size = _fit(tu_line, inner_w, "Helvetica", 8.0, 6.5)
        cur_y -= tu_size + 2
        c.setFont("Helvetica", tu_size)
        c.drawCentredString(cx, cur_y, tu_text)
        cur_y -= 2

    # Accent bar
    cur_y -= 5
    c.setFillColor(accent)
    c.rect(x + PAD + 12, cur_y, inner_w - 24, 1.5, stroke=0, fill=1)
    c.setFillColor(black)
    cur_y -= 6

    # ---- Stats (dotted leader rows) ----
    stats = spec.get("stats", [])
    stat_size = 9.5 if len(stats) <= 2 else 9.0
    for label, value in stats:
        cur_y -= stat_size
        _draw_dotted_row(c, x + PAD, cur_y, label, str(value), stat_size, inner_w,
                         value_color=accent)
        cur_y -= 3

    # ---- Effect ----
    effect = spec.get("effect")
    if effect:
        cur_y -= 3
        c.setStrokeColor(grey)
        c.setLineWidth(0.4)
        c.line(x + PAD, cur_y, x + CARD_W - PAD, cur_y)
        c.setStrokeColor(black)
        cur_y -= 4

        # "EFFECT" label
        cur_y -= 7.5
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(accent)
        c.drawString(x + PAD, cur_y, "EFFECT")
        c.setFillColor(black)
        cur_y -= 3

        # Effect text — preserve user's original casing
        # Auto-fit effect text size 9 → 7.5
        for fsize in [9.0, 8.5, 8.0, 7.5]:
            elines = _wrap(effect, "Helvetica", fsize, inner_w)
            if len(elines) <= 4:
                break
        c.setFont("Helvetica", fsize)
        for line in elines:
            cur_y -= fsize
            c.drawString(x + PAD, cur_y, line)
            cur_y -= 1.5

    # ---- Note (italic, accent-marked) ----
    note = spec.get("note")
    if note:
        cur_y -= 4
        for nsize in [8.0, 7.5, 7.0]:
            nlines = _wrap(note, "Helvetica-Oblique", nsize, inner_w)
            if len(nlines) <= 3:
                break
        c.setFillColor(SECONDARY_ACCENT)
        for line in nlines:
            cur_y -= nsize
            c.setFont("Helvetica-Oblique", nsize)
            c.drawString(x + PAD, cur_y, line)
            cur_y -= 1.5
        c.setFillColor(black)

    # ---- Keyword definitions (bottom, italic, fit if space) ----
    body_floor = y + PAD
    available_h = cur_y - body_floor

    # Collect keywords from effect + note + stat values (for things like Unshakable)
    text_for_keywords = [effect or "", note or ""] + [str(v) for _, v in stats]
    keywords = extract_keywords(*text_for_keywords)

    if keywords and available_h > 14:
        # Divider
        cur_y -= 4
        c.setStrokeColor(grey)
        c.setLineWidth(0.3)
        c.line(x + PAD, cur_y, x + CARD_W - PAD, cur_y)
        c.setStrokeColor(black)
        cur_y -= 3

        kw_size = 6.5
        kw_lh = kw_size + 1.0

        for kw in keywords:
            definition = GLOSSARY.get(kw)
            if not definition:
                continue
            full_text = f"{kw}: {definition}"
            lines = _wrap(full_text, "Helvetica-Oblique", kw_size, inner_w)
            block_h = len(lines) * kw_lh + 1.5
            if cur_y - block_h < body_floor:
                break

            # First line: bold-italic prefix "Keyword:" then italic rest
            first = lines[0]
            prefix = f"{kw}:"
            cur_y -= kw_size
            if first.startswith(prefix):
                c.setFont("Helvetica-BoldOblique", kw_size)
                c.drawString(x + PAD, cur_y, prefix)
                pw = stringWidth(prefix + " ", "Helvetica-BoldOblique", kw_size)
                rest = first[len(prefix):].lstrip()
                c.setFont("Helvetica-Oblique", kw_size)
                c.drawString(x + PAD + pw, cur_y, rest)
            else:
                c.setFont("Helvetica-Oblique", kw_size)
                c.drawString(x + PAD, cur_y, first)
            for line in lines[1:]:
                cur_y -= kw_lh
                c.setFont("Helvetica-Oblique", kw_size)
                c.drawString(x + PAD, cur_y, line)
            cur_y -= 2.5


# ---------- Crop marks ----------
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
    _stamp_version(c)


def _stamp_version(c):
    """Small grey version stamp from renown_data.VERSION, bottom-right of each page."""
    try:
        from renown_data import VERSION
    except Exception:
        return
    c.setFillColor(grey)
    c.setFont("Helvetica", 6)
    c.drawRightString(PAGE_W - MARGIN_X, MARGIN_Y * 0.45, f"Renown v{VERSION}")
    c.setFillColor(black)


# ---------- PDF builder ----------
def _render_pdf(specs, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    per_page = COLS * ROWS

    for i, spec in enumerate(specs):
        slot = i % per_page
        if slot == 0 and i > 0:
            draw_crop_marks(c)
            c.showPage()

        col = slot % COLS
        r = slot // COLS
        cx = MARGIN_X + col * CARD_W
        cy = PAGE_H - MARGIN_Y - (r + 1) * CARD_H
        draw_equipment_card(c, cx, cy, spec)

    draw_crop_marks(c)
    c.save()
    n_pages = (len(specs) + per_page - 1) // per_page
    print(f"Wrote {pdf_path}  ({len(specs)} cards, {n_pages} page(s))")


def make_weapons_pdf(pdf_path):
    _render_pdf([weapon_to_spec(r) for r in WEAPONS], pdf_path)


def make_ranged_pdf(pdf_path):
    _render_pdf([ranged_to_spec(r) for r in RANGED], pdf_path)


def make_shields_pdf(pdf_path):
    _render_pdf([shield_to_spec(r) for r in SHIELDS], pdf_path)


def make_armor_pdf(pdf_path):
    _render_pdf([armor_to_spec(r) for r in ARMOR], pdf_path)


def make_retinues_pdf(pdf_path):
    _render_pdf([retinue_to_spec(r) for r in RETINUES], pdf_path)


def make_all_pdf(pdf_path):
    """Render everything in one PDF, grouped by type."""
    specs = (
        [weapon_to_spec(r) for r in WEAPONS]
        + [ranged_to_spec(r) for r in RANGED]
        + [shield_to_spec(r) for r in SHIELDS]
        + [armor_to_spec(r) for r in ARMOR]
        + [retinue_to_spec(r) for r in RETINUES]
    )
    _render_pdf(specs, pdf_path)