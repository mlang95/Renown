#!/usr/bin/env python3
"""docx_tables.py — generate Word table fragments (OOXML) from renown_data.

Each function returns the <w:tbl>...</w:tbl> XML for one data-shaped table, built
live from the single source of truth. build_docs.py injects these into authored
prose docs wherever a {{TABLE:name}} marker appears, so the prose stays hand-
written (now in RULES_reorganized.md) while every embedded data table regenerates
from canon.

Registry at the bottom maps marker name -> builder. Add a row there to expose a
new table to the docs.
"""
import sys
sys.path.insert(0, ".")
import renown_data as rd

FONT = "EB Garamond"
HEAD_FILL = "D5E8F0"

def _esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

SZ = "17"   # EB Garamond 8.5pt — table cells

import re as _re
USABLE_TWIPS = 10466   # A4 portrait, 0.5" margins -> 11906 - 720 - 720
CHAR_W   = 105         # ~twips per char, EB Garamond 8.5pt (generous, bold headers)
CELL_PAD = 180         # left+right cell margin (90+90)
SLACK    = 120

_BOLD = _re.compile(r"\*\*(.+?)\*\*")

XE_RE = _re.compile("\x00XE:([^\x00]+)\x00")

def xe_mark(term):
    """Sentinel a builder appends to cell/prose text; rendered as an invisible XE index field."""
    return f"\x00XE:{term}\x00"

def xe_field_xml(term):
    """OOXML runs for one { XE "term" } index entry (Word + LibreOffice build {{INDEX}} from these)."""
    t = getattr(rd, "display_text", lambda x: x)(str(term)).replace('"', "'").replace(":", "\\:")
    return ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> XE "{_esc(t)}" </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>')

def _cell(text, bold=False, w_dxa=1000):
    text = getattr(rd, "display_text", lambda x: x)(str(text))   # display layer (keywords, names in cells)
    xes = "".join(xe_field_xml(m) for m in XE_RE.findall(text))
    text = XE_RE.sub("", text)
    def run(t, b):
        return (f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
                f'{"<w:b/><w:bCs/>" if b else ""}<w:sz w:val="{SZ}"/><w:szCs w:val="{SZ}"/></w:rPr>'
                f'<w:t xml:space="preserve">{_esc(t)}</w:t></w:r>')
    runs, pos = "", 0
    for m in _BOLD.finditer(text):              # honor **bold** segments in the data
        if m.start() > pos:
            runs += run(text[pos:m.start()], bold)
        runs += run(m.group(1), True)
        pos = m.end()
    if pos < len(text):
        runs += run(text[pos:], bold)
    if not runs:
        runs = run("", bold)
    runs += xes
    return (f'<w:tc><w:tcPr><w:tcW w:w="{w_dxa}" w:type="dxa"/></w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:before="0" w:after="0"/>'
            f'<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:sz w:val="{SZ}"/></w:rPr></w:pPr>'
            f'{runs}</w:p></w:tc>')

# Text measurement: the real EB Garamond metrics when references/fonts is present (PIL), else CHAR_W per character.
_FONTS = {}
def _font(bold):
    if bold not in _FONTS:
        try:
            import os
            from PIL import ImageFont
            fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts",
                              "EBGaramond-Bold.ttf" if bold else "EBGaramond-Regular.ttf")
            _FONTS[bold] = ImageFont.truetype(fn, 400)
        except Exception:
            _FONTS[bold] = None
    return _FONTS[bold]

_TW = {}
def _tw(text, bold=False):
    """Width of text in twips at the table size (SZ half-points)."""
    k = (text, bold)
    if k not in _TW:
        f = _font(bold)
        pt = int(SZ) / 2
        _TW[k] = (f.getlength(text) / 400 * pt * 20) if f else len(text) * CHAR_W
    return _TW[k]

def _wrap_lines(text, avail, bold=False):
    """Lines a cell needs in `avail` twips of text width (greedy word wrap; an over-long word takes extra lines)."""
    sp = _tw(" ", bold)
    lines, cur = 1, 0.0
    for w in _re.split(r"\s+", text.strip()):
        if not w:
            continue
        L = _tw(w, bold)
        if cur == 0:
            cur = L
        elif cur + sp + L <= avail:
            cur += sp + L
        else:
            lines += 1; cur = L
        while cur > avail and avail > 0:
            lines += 1; cur -= avail
    return lines

def _col_widths(headers, rows, step=60):
    """Absolute column widths (twips) summing to the usable page width.
    Each column starts wide enough for its longest single word (no word breaks mid-token). The rest of the page
    width goes, a step at a time, to whichever column most reduces the table's total height (sum over rows of the
    row's tallest cell). Columns of short names / lists ("Established Industry", "Alchemy, Forgotten Catacombs")
    therefore wrap to two lines when that lets a long Effect column shrink by more."""
    table = [list(headers)] + [list(r) for r in rows]
    ncol = len(headers)
    cells = [[_re.sub(XE_RE, "", str(r[c]) if c < len(r) else "").replace("**", "") for c in range(ncol)] for r in table]
    bold = lambda k: k == 0
    lword = [max(max((_tw(w, bold(k)) for w in _re.split(r"\s+", row[c]) if w), default=0) for k, row in enumerate(cells))
             for c in range(ncol)]
    w = [int(lw + CELL_PAD + SLACK) for lw in lword]
    if sum(w) >= USABLE_TWIPS:                                # too many columns: scale to fit
        scale = USABLE_TWIPS / sum(w)
        w = [max(300, int(x * scale)) for x in w]
        w[-1] += USABLE_TWIPS - sum(w)
        return w
    avail = lambda x: x - CELL_PAD - SLACK / 2
    lines = [[_wrap_lines(row[c], avail(w[c]), bold(k)) for c in range(ncol)] for k, row in enumerate(cells)]
    spare = USABLE_TWIPS - sum(w)
    def lines_at(c, width):
        return [_wrap_lines(row[c], avail(width), bold(k)) for k, row in enumerate(cells)]
    while spare >= step:
        base = sum(max(r) for r in lines)
        best = None
        for c in range(ncol):
            cur_c = sum(r[c] for r in lines)
            for k in range(1, int(spare // step) + 1):          # smallest widening that saves a line somewhere
                col = lines_at(c, w[c] + k * step)
                trial = sum(max(max(r[:c] + r[c + 1:], default=0), col[q]) for q, r in enumerate(lines))
                if base - trial > 0 or cur_c - sum(col) > 0:
                    key = ((base - trial) / k, (cur_c - sum(col)) / k)
                    if best is None or key > best[0]:
                        best = (key, c, k, col)
                    break
        if best is None:
            break                                              # every cell already as short as it can get
        _, c, k, col = best
        w[c] += k * step; spare -= k * step
        for q, r in enumerate(lines):
            r[c] = col[q]
    if spare > 0:                                              # leftover: share by each column's one-line width
        nat = [max(_tw(row[c], bold(k)) for k, row in enumerate(cells)) + 1 for c in range(ncol)]
        tot = sum(nat)
        w = [w[c] + int(spare * nat[c] / tot) for c in range(ncol)]
    w[-1] += USABLE_TWIPS - sum(w)                            # absorb rounding
    return w

def _table(headers, rows, widths=None):
    dxa = list(widths) if widths else _col_widths(headers, rows)
    bd = '<w:tblBorders>' + ''.join(
        f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        for e in ("top", "left", "bottom", "right", "insideH", "insideV")) + '</w:tblBorders>'
    cm = ('<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="90" w:type="dxa"/>'
          '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="90" w:type="dxa"/></w:tblCellMar>')
    look = '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
    tblpr = (f'<w:tblPr><w:tblW w:w="{USABLE_TWIPS}" w:type="dxa"/><w:jc w:val="center"/>{bd}'
             f'<w:tblLayout w:type="fixed"/>{cm}{look}</w:tblPr>')
    grid = '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{d}"/>' for d in dxa) + '</w:tblGrid>'
    head = '<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' + ''.join(_cell(h, True, d) for h, d in zip(headers, dxa)) + '</w:tr>'
    body = ''.join('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + ''.join(_cell(c, False, d) for c, d in zip(r, dxa)) + '</w:tr>' for r in rows)
    return f'<w:tbl>{tblpr}{grid}{head}{body}</w:tbl>'

# ── table builders ──
def retinues():
    aura = any("aura" in x for x in rd.RETINUES.values())               # Aura column only when the data has it
    rows = [[n, str(x.get("cost", "")), f"{x['to_hit']}+", str(x['endurance']), f"{x['shaking']}+",
             str(x.get("speed", "—"))] + ([str(x.get("aura", "—"))] if aura else []) + [str(x.get("max_size", "—")),
             "Unbreakable" if x.get("unbreakable") else "—"] for n, x in rd.RETINUES.items()]
    return _table(["Retinue", "Cost", "To Strike", "Endurance", "Morale", "Speed"] + (["Aura"] if aura else []) + ["Max Size", "Keyword"], rows)

def settlements():
    # 9-col form matching the authored Rules table; sourced from SETTLEMENTS.
    sea = any(v.get("sea_variant") for v in rd.SETTLEMENTS.values())      # no column when no Settlement has a sea variant (SIMPLE)
    aura = any("aura" in v for v in rd.SETTLEMENTS.values())
    rows = [[str(v["tier"]), n] + ([v["sea_variant"] or "None"] if sea else []) + [str(v["tax_income"]),
             str(v["muster_limit"]), str(v["build_time"]), str(v["wards"]),
             str(v["reach"])] + ([str(v.get("aura", "—"))] if aura else []) + [v["notes"] or "—"]
            for n, v in rd.SETTLEMENTS.items()]
    return _table(["Tier", "Settlement"] + (["Sea"] if sea else []) + ["Tax", "Muster", "Build", "Wards", "Reach"] + (["Aura"] if aura else []) + ["Notes"], rows)

def eras():
    rows = [[n, str(v["renown"]), str(v["armies"]), str(v["cities"]), str(v.get("max_settlements", "—")),
             f"+{v['influence_per_turn']}", str(v["innate_diplomacy_influence"]), v.get("envoys", "") or "—",
             v["unlocks"] or "—"]
            for n, v in rd.ERAS.items()]
    return _table(["Era", "Renown", "Armies", "Cities", "Max Settlements", "Infl/Turn", "Diplo Authority", "Envoys", "Unlocks"], rows)

def public_order():
    # X = the band's value in each Era (PO_BANDS / ERAS po_scale_*); bands without a number show "—"
    if hasattr(rd, "PO_BANDS"):
        eras = list(rd.ERAS)
        rows = [[str(k), name, t.replace("{n}", "X").replace("{s}", "(s)")] +
                [str(rd.po_value(k, e)) if rd.po_value(k, e) is not None else "—" for e in eras]
                for k, (name, t, _b) in sorted(rd.PO_BANDS.items())]
        return _table(["PO", "State", "Effect"] + [f"X: {e}" for e in eras], rows)
    rows = [[str(k), name, eff] for k, (name, eff) in sorted(rd.PUBLIC_ORDER.items())]
    return _table(["PO", "State", "Effect"], rows)

def po_modifiers():
    rows = []
    for sign in ("faith", "doubt"):
        for src, cond in rd.PO_MODIFIERS.get(sign, {}).items():
            rows.append([f"{sign.title()} +1", src, cond])
    return _table(["Type", "Source", "Condition"], rows)
    

DOMAIN_ORDER = ["Prowess", "Cunning", "Piety", "Industry"]   # Envoy resolution order (Diplomacy first where it appears)

def _standing_headers():
    """Domain-board header row; tier numbers from STANDING_THRESHOLDS, rank from STANDING_RANK."""
    st = getattr(rd, "STANDING_THRESHOLDS", {"Untested": 1, "Rising": 3, "Established": 6, "Sovereign": 10})
    rk = getattr(rd, "STANDING_RANK", {})
    r = lambda t: f" · Rank {rk[t]}" if t in rk else ""
    return ["Domain", "Untested" + r("Untested")] + [f"{t} ({st[t]}){r(t)}" for t in ("Rising", "Established", "Sovereign")]

def domain_board():
    # Full authored shape: Untested..Sovereign per domain, then the two influence rows.
    # Combat standing effects (rd.STANDING_EFFECTS) are folded into the same cell —
    # they unlock from the domain board, so they aren't partitioned out.
    b = rd.DOMAIN_BOARD
    se = getattr(rd, "STANDING_EFFECTS", {})
    def cell(d, tier):
        base = (b[d].get(tier, "") or "").strip()
        cmb = se.get((d, tier))
        if cmb:
            base = (base + " " if base else "") + str(cmb).strip()
        return base
    rows = [[d, cell(d, "Rising"), cell(d, "Established"), cell(d, "Sovereign")]
            for d in DOMAIN_ORDER if d in b]                        # Untested has no Standing effect: no column
    # Influence-by-Standing rows live in the rules' own "Standing & Influence" table (not repeated here)
    return _table([h for h in _standing_headers() if not h.startswith("Untested")], rows)

def envoy_outcomes():
    DOM = ["Diplomacy"] + DOMAIN_ORDER
    rows = [[d,
             rd.ENVOY_OUTCOMES[d].get("condemned", ""),
             rd.ENVOY_OUTCOMES[d].get("failed", ""),
             rd.ENVOY_OUTCOMES[d].get("passed", ""),
             rd.ENVOY_OUTCOMES[d].get("endorsed", "")]
            for d in DOM if d in rd.ENVOY_OUTCOMES]
    return _table(["Domain", "Condemned", "Failed", "Passed", "Endorsed"], rows)

def net_influence():
    # Numbers come from canon; the result/effect wording is fixed rules text.
    t = rd.ENVOY_OUTCOME_THRESHOLDS
    rows = [
        [f"{t.get('Condemned')} or less", "Condemned", "Resolve that Domain's Condemn effect"],
        [f"{t.get('Failed')} or less",    "Failed",    "Gain Doubt 1"],
        [f"{t.get('Passed')}+",           "Passed",    "Perform the action's Pass effect"],
        [f"{t.get('Endorsed')}+",         "Endorsed",  "Also perform the Endorsed effect"],
    ]
    return _table(["Net Influence", "Result", "Effect"], rows)

def influence_gain():
    rows = [[k, d.get("change", ""), d.get("notes", "")] for k, d in rd.INFLUENCE_GAIN.items()]
    return _table(["Source", "Influence Change", "Notes"], rows)

def treaties():
    rows = [[n, d.get("signed_via", ""), d.get("era", ""), d.get("effect", "")]
            for n, d in rd.TREATIES.items()]
    return _table(["Treaty", "Signed Via", "Era", "Effect"], rows)

def bandit_growth():
    rows = [[k, str(v)] for k, v in rd.BANDIT_GROWTH_PER_ERA.items()]
    return _table(["Era", "Retinues Gained per Turn"], rows)

def _die_span(lo, hi):
    return f"{lo}" if lo == hi else f"{lo}\u2013{hi}"

def _die_rows(table):
    return [[_die_span(lo, hi), action] for lo, hi, action in rd.die_table_ranges(table)]

def bandit_cunning():
    return _table([f"d{rd.BANDIT_FACES}", "Cunning Action"], _die_rows(rd.BANDIT_CUNNING_TABLE))

def bandit_tactics():
    return _table([f"d{rd.BANDIT_FACES}", "Tactic"], _die_rows(rd.BANDIT_TACTIC_TABLE))

def bandit_armaments():
    return _table(["Era", "Armament"],
                  [[k, v] for k, v in rd.BANDIT_EQUIPMENT_PER_ERA.items()])

def bandits_by_era():
    """Bandit growth + armaments in one table (one row per Era)."""
    eras = list(dict.fromkeys(list(rd.BANDIT_GROWTH_PER_ERA) + list(rd.BANDIT_EQUIPMENT_PER_ERA)))
    return _table(["Era", "Retinues Gained per Turn", "Armament"],
                  [[e, str(rd.BANDIT_GROWTH_PER_ERA.get(e, "\u2014")), rd.BANDIT_EQUIPMENT_PER_ERA.get(e, "\u2014")] for e in eras])

def edicts():
    rows = [[n, d.get("type", ""), d.get("requirement", "")] for n, d in rd.EDICTS.items()]
    return _table(["Edict", "Type", "Requirement"], rows)

def weapons():
    rows = [[rd.display(n), (getattr(rd,"ITEM_TIER_DISPLAY",{}).get(n) or rd.display_tier(x["tier"])), str(x["ap"]), f"{x['init']:+d}", ", ".join(x["tags"]) or "—"]
           for n, x in rd.WEAPONS.items()]
    return _table(["Weapon", "Tier", "AP", "Init", "Keywords"], rows)

def armor():
    rows = [[rd.display(n), (getattr(rd,"ITEM_TIER_DISPLAY",{}).get(n) or rd.display_tier(x["tier"])), f"{x['save']}+", ", ".join(x["tags"]) or "—"]
           for n, x in rd.ARMORS.items()]
    return _table(["Armor", "Tier", "Save", "Keywords"], rows)

def seasons():
    ks = list(rd.SEASONS); y = getattr(rd, "AGE_YEAR_SEASON", ks[0])
    ks = ks[ks.index(y):] + ks[:ks.index(y)] if y in ks else ks      # cycle order, starting with the Season that turns the Year
    rows = [[s, rd.SEASONS[s]["name"], rd.SEASONS[s]["effect"]] for s in ks]
    return _table(["Season", "Name", "Effect"], rows)

def ages():
    rows = [[n, a["rising"] or "Each player's choice", f"{a['years'][0]}\u2013{a['years'][1]}"]
            for n, a in getattr(rd, "AGES", {}).items()]
    return _table(["Age", "Starting Rising", "Starting Year"], rows)

def ranged():
    rows = [[rd.display(n), (getattr(rd,"ITEM_TIER_DISPLAY",{}).get(n) or rd.display_tier(x["tier"])), str(x["ap"]), f"{x['init']:+d}", ", ".join(x["tags"]) or "—"]
           for n, x in rd.RANGED.items()]
    return _table(["Ranged Weapon", "Tier", "AP", "Init", "Keywords"], rows)

def shields():
    rows = [[rd.display(n) if n else "None", (getattr(rd,"ITEM_TIER_DISPLAY",{}).get(n) or rd.display_tier(x["tier"])) or "—", f"+{x['save_bonus']}", f"{x['init']:+d}",
             ", ".join(x["tags"]) or "—"] for n, x in rd.SHIELDS.items()]
    return _table(["Shield", "Tier", "Save Bonus", "Init", "Keywords"], rows)

def infrastructure():
    rows = [[n, v.get("tier", ""), str(v.get("upkeep", "")), str(v.get("build_time", "")),
             v.get("requirement", ""), v.get("empire_bonus", "")]
            for n, v in rd.INFRASTRUCTURE.items()]
    return _table(["Infrastructure", "Tier", "Upkeep", "Build Time", "Requirement", "Empire Bonus"], rows)

_TAC_BASE = {"Hill": "Grassland", "Open Field": "Grassland", "Mire": "Wetlands", "Forest": "Forest",
             "Tundra": "Tundra", "Mountains": "Mountains", "Water": "Water"}

def terrain():
    battle = {}
    for feat, fd in (getattr(rd, "TACTICAL_TERRAIN", {}) or {}).items():
        base = _TAC_BASE.get(feat, feat); note = fd.get("effect", "")
        battle.setdefault(base, []).append(f"{feat}: {note}" if feat != base else note)
    rows = [[t, v.get("Effect", "") or "—", ", ".join(v.get("Raw Materials", [])) or "—",
             "  ".join(battle.get(t, [])) or "—"] for t, v in rd.TERRAIN.items()]
    return _table(["Terrain", "Map Effect", "Raw Materials", "Battle Effect"], rows)

def tactical_terrain():
    rows = [[t, v.get("identify", ""), v.get("effect", "")] for t, v in rd.TACTICAL_TERRAIN.items()]
    return _table(["Tactical Terrain", "Identify", "Effect"], rows)

def factions():
    fb = getattr(rd, "faction_body", lambda k: rd.FACTIONS[k].get("mechanic", ""))   # name = mechanic title; body without it
    rows = [[n, v.get("feel", ""), v.get("difficulty", ""), v.get("strength", ""), fb(n)]
            for n, v in rd.FACTIONS.items()]
    return _table(["Faction", "Feel", "Difficulty", "Strength", "Mechanic"], rows)

def timers():
    rows = [[n + xe_mark(n), ("—" if v.get("default") is None else str(v.get("default"))),
             v.get("where", ""), v.get("tracks", "")] for n, v in rd.TIMERS.items()]
    return _table(["Timer", "Default", "Where", "Tracks"], rows)

def build_timers():
    rows = []
    for k, v in rd.BUILD_TIMERS.items():
        if isinstance(v, dict):
            for sub, sv in v.items():
                rows.append([f"{k} ({sub})", str(sv)])
        else:
            rows.append([k, str(v)])
    return _table(["Build", "Turns"], rows)

def _siege_text_sources(sign):
    """[(name, kind, value, condition)] for every 'Siege Timer +X' (sign '+') or '-X' (sign '-') in Holding,
    Infrastructure / Wonder and Heritage text. Condition = the clause's leading 'While ...' text, if any."""
    pat = _re.compile(r"Siege Timers?\s*" + (r"\+" if sign == "+" else "[\u2212-]") + r"\s*(\d+)")
    srcs = [("Holding", n, f"{v.get('innate', '')}; {'' if getattr(rd, 'SIMPLE', False) else v.get('mastery', '')}") for n, v in rd.NODES.items()]
    srcs += [("Infrastructure", n, str(v.get("empire_bonus", ""))) for n, v in rd.INFRASTRUCTURE.items()]
    srcs += [("Faction", n, str(v.get("mechanic", ""))) for n, v in rd.FACTIONS.items()]
    out = []
    for kind, name, txt in srcs:
        for m in pat.finditer(txt.replace("**", "")):
            head = txt[:m.start()].replace("**", "")
            cond = _re.search(r"(While [^.;]*?),[^.;]*$", head)
            out.append((name, kind, int(m.group(1)), cond.group(1) if cond else ""))
    return out

def siege_calculus(mode="Lay Siege"):
    spec = rd.SIEGE_CALCULUS[mode]; vals = rd.SIEGE_SOURCE_VALUES
    def fmt(src):
        v = vals.get(src, {})
        if v.get("from") == "SETTLEMENTS":
            ts={t: s[v["field"]] for t, s in rd.SETTLEMENTS.items()}
            return f"+{min(ts.values())} to +{max(ts.values())}", ", ".join(f"{t} {n}" for t, n in ts.items())
        if v.get("from") == "text":   # its own "Siege Timer +X" text, counted only in its own Settlement
            hit=[f"+{val}" for name, kind, val, cond in _siege_text_sources("+") if name == src]
            return (" / ".join(hit) or "\u2014"), "only in its own Settlement" if hit else "value undefined"
        if v.get("from")=="board_state": return f"+{v['value']}", v.get("rule","")
        if "value" in v: return f"+{v['value']}", ""
        return "\u2014","value undefined"
    kinds = {n: "Infrastructure" for n in rd.INFRASTRUCTURE}
    kinds.update({n: "Holding" for n in rd.NODES})
    def note(src, n):
        return "; ".join(x for x in (kinds.get(src, ""), n) if x)
    listed = list(spec["settlement_sources"])
    rows = [[src, t, note(src, n)] for src in listed for t, n in [fmt(src)]]
    if mode == "Lay Siege":
        for name, kind, val, cond in _siege_text_sources("+"):
            if name in listed:
                continue
            rows.append([name, f"+{val}", "; ".join(x for x in (kind, cond) if x)])
    if spec.get("attacker_sources"):
        red = sorted(f"{name} \u2212{val}" for name, kind, val, cond in _siege_text_sources("-"))
        rows.append(["Attacker effects","\u2212 varies",", ".join(red) or "from effect text"])
    return _table(["Source","Timer","Note"], rows)

def _heading_xml(text, level):
    """A heading paragraph matching md_to_docx's heading style (outline level -> TOC)."""
    size = {1: 40, 2: 36, 3: 32, 4: 28}.get(level, 24)
    before = {1: 240, 2: 240, 3: 160}.get(level, 120)
    return (f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="{before}" w:after="80"/>'
            f'<w:outlineLvl w:val="{level - 1}"/></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:b/><w:bCs/>'
            f'<w:sz w:val="{size}"/></w:rPr><w:t xml:space="preserve">{_esc(getattr(rd, "display_text", lambda x: x)(text))}</w:t></w:r></w:p>')

_REQ_TOK = _re.compile(r"^(Rising|Established|Sovereign)\s+(Prowess|Cunning|Piety|Industry)$", _re.I)
_REQ_ANY = _re.compile(r"^(\d+)\s+(Rising|Established|Sovereign)$", _re.I)
_ST_RANK = {"Rising": 1, "Established": 2, "Sovereign": 3}

def _req_groups(unlock):
    """Standing-requirement groups for one unlock string: [] (none), ['Rising Industry'], or one per '+' part."""
    u = (unlock or "").strip()
    if u in ("", "-", "\u2014"):
        return []
    return [t.strip() for t in _re.split(r"\s*[+,]\s*", u) if t.strip()]

def _req_label(tok):
    m = _REQ_ANY.match(tok)
    if m:
        n = int(m.group(1)); return f"{n} Domain{'s' if n != 1 else ''} at {m.group(2).title()}"
    return tok

def _req_key(tok):
    m = _REQ_TOK.match(tok)
    if m:
        return (0, DOMAIN_ORDER.index(m.group(2).title()), _ST_RANK[m.group(1).title()])
    m = _REQ_ANY.match(tok)
    if m:
        return (1, int(m.group(1)), _ST_RANK[m.group(2).title()])
    return (2, 0, 0)

def holdings():
    """Every NODES entry, grouped by Standing requirement (a Holding with two requirements appears under both);
    Domain sub-headings in Envoy resolution order. Monuments sit in their Standing group, marked (Monument)."""
    simple = getattr(rd, "SIMPLE", False)
    chain = getattr(rd, "CHAIN_TERM", "Efficient")
    term = getattr(rd, "PURSUIT_TERM", ("Pursuit", "Pursuits"))[0]
    def row(n, v, extra=None):
        eff = v.get("efficient")
        eff_txt = (rd.display(eff) if isinstance(eff, str) else rd.display_list(eff)) if eff else "\u2014"
        mon = v.get("type") == "Monument" or v.get("monument")
        name = rd.display(n) + (" (Monument)" if mon else "") + (f" (also {extra})" if extra else "")
        if simple:
            return [name, rd.display_text(v.get("infrastructure_req", "")) or "\u2014", eff_txt,
                    rd.display_text(v.get("innate", "") or "") or "\u2014"]
        return [name, rd.display_text(v.get("mastery_req", "")) or "\u2014", eff_txt,
                rd.display_text(v.get("innate", "") or "") or "\u2014", rd.display_text(v.get("mastery", "")) or "\u2014"]
    hdr = ([term, "Infrastructure Req", chain, "Effect"] if simple
           else [term, "Mastery Unlock", "Efficient", "Innate Effect", "Mastery Effect"])
    groups = {}
    for n, v in rd.NODES.items():
        reqs = _req_groups(v.get("unlock"))
        for t in (reqs or ["None"]):
            others = [x for x in reqs if x != t]
            groups.setdefault(t, []).append(row(n, v, " + ".join(others) if others else None))
    out, last_dom = [], None
    sortk = lambda r: _re.sub(r"\*\*", "", r[0]).lower()
    widths = _col_widths(hdr, [r for g in groups.values() for r in g])    # one column grid for every Holding table
    for t in sorted(groups, key=lambda t: (-1, 0, 0) if t == "None" else _req_key(t)):
        m = _REQ_TOK.match(t)
        dom = m.group(2).title() if m else ("No Requirement" if t == "None" else "Any Domain")
        if dom != last_dom:
            out.append(_heading_xml(dom, 2)); last_dom = dom
        if t != "None":
            out.append(_heading_xml(_req_label(t), 3))
        out.append(_table(hdr, sorted(groups[t], key=sortk), widths=widths))
    return "".join(out)

def tactic_matrix():
    T = rd.TACTICS
    def cell(a, b):
        v = rd.TACTIC_MATRIX.get((a, b))
        if not v: return ""
        me = v[0]; bits = []
        if me.get("I"):  bits.append(f"Initiative {me['I']:+d}")
        if me.get("TH"): bits.append(f"Strike {me['TH']:+d}")
        if me.get("TS"): bits.append(f"Save {me['TS']:+d}")
        if me.get("no_combat"): bits.append("no combat")
        return " ".join(bits) or "—"
    return _table(["Your Tactic ↓  vs →"] + list(T), [[a] + [cell(a, b) for b in T] for a in T])

def trade_rules():
    t = rd.TRADE_RULES
    return _table(["Rule", "Value"], [["Income per Craft", str(t["income_per_craft"])],
                                      ["Requirements", t["requirements"]],
                                      ["No-trade Season", t["no_trade_season"]]])


REGISTRY = {
    "retinues": retinues, "settlements": settlements, "eras": eras,
    "public_order": public_order, "po_modifiers": po_modifiers,
    "domain_board": domain_board, "envoy_outcomes": envoy_outcomes,
    "net_influence": net_influence, "influence_gain": influence_gain,
    "treaties": treaties, "bandit_growth": bandit_growth, "edicts": edicts,
    "weapons": weapons, "armor": armor, "seasons": seasons, "ages": ages,
    "ranged": ranged, "shields": shields, "infrastructure": infrastructure,
    "terrain": terrain, "tactical_terrain": tactical_terrain,
    "factions": factions, "timers": timers, "build_timers": build_timers, "siege_calculus": siege_calculus,
    "bandit_cunning": bandit_cunning, "bandit_tactics": bandit_tactics,
    "bandit_armaments": bandit_armaments, "bandits_by_era": bandits_by_era,
    "holdings": holdings, "tactic_matrix": tactic_matrix, "trade_rules": trade_rules,
}

# ── {{ACTIONS:Domain}} — render every ACTIONS entry of a domain as prose ──
# Mirrors the authored "## <Domain> Actions" layout so the action text stops
# living in two places. Returns a run of <w:p> paragraphs (not a table).
def _p(runs_xml, before=0, after=40, ind=0, keep_next=False):
    pind = f'<w:ind w:left="{ind}" w:hanging="{ind}"/>' if ind else ''
    keep = ("<w:keepNext/>" if keep_next else "") + "<w:keepLines/>"
    return (f'<w:p><w:pPr>{keep}<w:spacing w:before="{before}" w:after="{after}"/>{pind}'
            f'<w:rPr>{_FONT_RPR}</w:rPr></w:pPr>{runs_xml}</w:p>')

def _run(text, bold=False, ital=False):
    style = ("<w:b/><w:bCs/>" if bold else "") + ("<w:i/><w:iCs/>" if ital else "")
    return (f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/>{style}'
            f'<w:sz w:val="20"/></w:rPr><w:t xml:space="preserve">{_esc(text)}</w:t></w:r>')

def _bullet(runs_xml, after=20, keep_next=False):
    keep = ("<w:keepNext/>" if keep_next else "") + "<w:keepLines/>"
    return ('<w:p><w:pPr><w:pStyle w:val="ListBullet"/>'
            f'{keep}<w:spacing w:before="0" w:after="{after}"/>'
            '<w:ind w:left="360" w:hanging="180"/>'
            f'<w:rPr>{_FONT_RPR}</w:rPr></w:pPr>{runs_xml}</w:p>')

def _action_block(name, a):
    # Emit the block's paragraphs with keep_next set on every paragraph except the
    # final one, so an action never splits across a column or page break.
    end = a.get("endorsed", "")
    notes = a.get("notes", [])
    cost = a.get("cost", "None")
    req = a.get("requires", "")
    meta = _run("Cost: ", bold=True) + _run(cost)
    if req:
        meta += _run("      Requires: ", bold=True) + _run(req)
    out = []
    out.append(_p(_run(name, bold=True), before=120, after=20, keep_next=True))
    out.append(_p(meta, after=20, keep_next=True))
    last_is_effect = not end and not notes
    out.append(_p(_run("Effect: ", bold=True) + _run(a.get("effect", "")),
                  after=20, keep_next=not last_is_effect))
    if end:
        out.append(_p(_run("Endorsed: ", bold=True) + _run(end),
                      after=20, keep_next=bool(notes)))
    for j, note in enumerate(notes):
        out.append(_bullet(_run(note), keep_next=(j < len(notes) - 1)))
    return "".join(out)

def actions(domain):
    items = [(n, a) for n, a in rd.ACTIONS.items() if a.get("domain") == domain]
    out = []
    for i, (n, a) in enumerate(items, 1):
        # prepend the ordinal into the bolded title
        block = _action_block(f"{i}. {n}", a)
        out.append(block)
    return "".join(out)

# ── {{VAL:dotted.path}} — resolve one scalar out of renown_data ──
# Path syntax: NAME or NAME.key or NAME.key.subkey. dict keys and (rarely) list
# indices both work. Returns str(value); raises on a bad path so build fails loud.
def value(path):
    parts = path.split(".")
    cur = getattr(rd, parts[0])
    for p in parts[1:]:
        if isinstance(cur, dict):
            cur = cur[p]
        elif isinstance(cur, (list, tuple)):
            cur = cur[int(p)]
        else:
            raise KeyError(f"VAL path '{path}': cannot index {type(cur).__name__} with '{p}'")
    return str(cur)

# ── {{LIST:NAME}} — render a renown_data list of strings as bullets ──
def list_block(name):
    seq = getattr(rd, name)
    if not isinstance(seq, (list, tuple)):
        raise KeyError(f"LIST '{name}' is not a list/tuple")
    return "".join(
        f'<w:p><w:pPr><w:pStyle w:val="ListBullet"/><w:rPr>{_FONT_RPR}</w:rPr></w:pPr>'
        f'{_run(str(item))}</w:p>' for item in seq)

def get(name):
    if name not in REGISTRY:
        raise KeyError(f"no table '{name}'. available: {sorted(REGISTRY)}")
    return REGISTRY[name]()

# ── glossary access (for {{DEF:term}} and {{GLOSSARY}} markers) ──
def _gloss_lookup():
    """Return {lower_term: (display_term, definition)} from renown_data.GLOSSARY,
    resolving constant-keyed entries to their string form."""
    out = {}
    disp = getattr(rd, "display_text", lambda x: x)
    for k, v in rd.GLOSSARY.items():
        term = str(k)
        out[term.lower()] = (term, v)
        out.setdefault(disp(term).lower(), (term, v))     # "Holding" finds the "Pursuit" entry
    return out

def lookup(term):
    """(canonical key, definition) for a term or its display name; (None, '') if unknown."""
    return _gloss_lookup().get(term.lower(), (None, ""))

def glossary_categories():
    """[(title, [canonical term, ...])] from renown_data.GLOSSARY_CATEGORIES (terms that exist only)."""
    g = {str(k) for k in rd.GLOSSARY}
    return [(title, [str(t) for t in terms if str(t) in g])
            for title, terms in getattr(rd, "GLOSSARY_CATEGORIES", [])]

def glossary_category(title):
    """{{GLOSSARY:Category}} — one category as a Term | Definition table; each term is an index entry."""
    cats = dict(glossary_categories())
    if title not in cats:
        raise KeyError(f"no glossary category '{title}'. available: {list(cats)}")
    g = {str(k): v for k, v in rd.GLOSSARY.items()}
    rows = [[t + xe_mark(t), see_definition(t, g[t])] for t in cats[title]]
    return _heading_xml(f"Glossary · {title}", 4) + _table(["Term", "Definition"], rows)

_SENT_END = _re.compile(r"(?<!\be\.g)(?<!\bi\.e)(?<!\betc)(?<!\bvs)\.(?=\s+[A-Z(])")

def _first_sentence(text):
    m = _SENT_END.search(str(text))
    return str(text)[:m.end()] if m else str(text)

def see_definition(term, full):
    """GLOSSARY_SEE terms: first sentence (or the given short text) + "See <rule> (<section>)"; else the full text.
    Rule numbers come from rule_numbers.ANCHORS (filled when the rules md is numbered)."""
    v = getattr(rd, "GLOSSARY_SEE", {}).get(term)
    if not v:
        return full
    short, aid = v if isinstance(v, tuple) else (_first_sentence(full), v)
    import rule_numbers as rn
    r = rn.ref(aid)
    if not r:
        print(f"  docx_tables: GLOSSARY_SEE '{term}' -> '{aid}' unresolved; printing the full definition", file=sys.stderr)
        return full
    short = short.strip()
    return f"{short}{'' if short.endswith(('.', ')')) else '.'} See {r[0]} ({r[1]})."

def definition(term):
    """The definition string for a term (case-insensitive); '' if unknown."""
    g = _gloss_lookup()
    hit = g.get(term.lower())
    return hit[1] if hit else ""

def glossary_block():
    """The full glossary as an alphabetized definition list (term bold, def after)."""
    g = rd.GLOSSARY
    items = sorted(((str(k), v) for k, v in g.items()), key=lambda x: x[0].lower())
    paras = []
    for term, d in items:
        paras.append(
            f'<w:p><w:pPr><w:spacing w:after="40"/><w:rPr>{_FONT_RPR}</w:rPr></w:pPr>'
            f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:b/><w:bCs/><w:sz w:val="17"/></w:rPr>'
            f'<w:t xml:space="preserve">{_esc(term)} — </w:t></w:r>'
            f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:sz w:val="17"/></w:rPr>'
            f'<w:t xml:space="preserve">{_esc(d)}</w:t></w:r></w:p>')
    return "".join(paras)

_FONT_RPR = f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:sz w:val="17"/>'

if __name__ == "__main__":
    print("Available {{TABLE:name}} markers:", ", ".join(sorted(REGISTRY)))