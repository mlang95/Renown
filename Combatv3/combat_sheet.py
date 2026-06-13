#!/usr/bin/env python3
"""combat_sheet.py — Renown combat quick-reference (print & laminate).

A two-page (front/back) Letter-portrait sheet in the style of a wargame codex
back cover: a vertical Skirmish-step "spine" down the left with roll callouts,
and supporting data charts (retinues, defense sequence, tactic matrix, weapon /
armor / shield profiles, keywords) on the right and on the back.

All combat data is pulled live from renown_data — re-run to track rule changes.
Usage:  python combat_sheet.py [out.pdf]
"""
import sys, os
sys.path.insert(0, ".")
import renown_data as rd

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── fonts (EB Garamond, with Helvetica fallback) ──
SERIF, SERIF_B, SERIF_I = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
for face, fn in [("EBG", "EBGaramond-Regular.ttf"), ("EBG-B", "EBGaramond-Bold.ttf"),
                 ("EBG-I", "EBGaramond-Italic.ttf")]:
    for base in ("/root/.fonts", "fonts", "."):
        p = os.path.join(base, fn)
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont(face, p))
                if face == "EBG": SERIF = "EBG"
                elif face == "EBG-B": SERIF_B = "EBG-B"
                elif face == "EBG-I": SERIF_I = "EBG-I"
            except Exception:
                pass
            break

# ── palette (parchment to match rulebook/wiki) ──
PARCH   = (0.96, 0.93, 0.86)
INK     = (0.16, 0.12, 0.08)
ACCENT  = (0.45, 0.18, 0.12)   # oxblood
RULE    = (0.55, 0.45, 0.32)
BAND    = (0.88, 0.83, 0.72)
BANDALT = (0.92, 0.88, 0.79)
CALLOUT = (0.86, 0.80, 0.66)

PAGE_W, PAGE_H = letter
MARGIN = 0.5 * inch

def _set(c, rgb): c.setFillColorRGB(*rgb)
def _stroke(c, rgb): c.setStrokeColorRGB(*rgb)

def bg(c):
    _set(c, PARCH); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

def header(c, title, sub=None):
    _set(c, ACCENT)
    c.setFont(SERIF_B, 22)
    c.drawString(MARGIN, PAGE_H - MARGIN - 14, title)
    if sub:
        _set(c, INK); c.setFont(SERIF_I, 10)
        c.drawString(MARGIN, PAGE_H - MARGIN - 28, sub)
    _stroke(c, RULE); c.setLineWidth(1.2)
    y = PAGE_H - MARGIN - 36
    c.line(MARGIN, y, PAGE_W - MARGIN, y)
    return y - 14

# ── generic chart table ──
def chart(c, x, y, w, title, headers, rows, colw=None, fs=8, rowh=13, title_fs=11):
    """Draw a titled table; returns the y after the table."""
    _set(c, ACCENT); c.setFont(SERIF_B, title_fs)
    c.drawString(x, y, title)
    y -= 6
    _stroke(c, RULE); c.setLineWidth(0.6); c.line(x, y, x + w, y)
    y -= rowh
    n = len(headers)
    if colw is None:
        colw = [w / n] * n
    # header row
    _set(c, INK); c.setFont(SERIF_B, fs)
    cx = x
    for h, cw in zip(headers, colw):
        c.drawString(cx + 2, y + 3, str(h)); cx += cw
    y += 1
    _stroke(c, RULE); c.setLineWidth(0.4); c.line(x, y - 2, x + w, y - 2)
    y -= rowh
    # body (wraps tall cells to extra lines)
    for i, row in enumerate(rows):
        # measure how many lines this row needs (max across cells)
        wrapped = []
        maxlines = 1
        for cell, cw in zip(row, colw):
            txt = str(cell); words = txt.split(); lines = []; curl = ""
            for wd in words:
                t = (curl + " " + wd).strip()
                if c.stringWidth(t, SERIF, fs) <= cw - 4: curl = t
                else:
                    if curl: lines.append(curl)
                    curl = wd
            if curl: lines.append(curl)
            if not lines: lines = [""]
            wrapped.append(lines); maxlines = max(maxlines, len(lines))
        rh = rowh + (maxlines - 1) * (fs + 1)
        # band spans the full row height, anchored at the row's top (y) down to (y - rh)
        if i % 2 == 0:
            _set(c, BANDALT); c.rect(x, y - rh + rowh - 2, w, rh, fill=1, stroke=0)
        _set(c, INK); c.setFont(SERIF, fs)
        cx = x
        for lines, cw in zip(wrapped, colw):
            yy = y + 3
            for ln in lines:
                c.drawString(cx + 2, yy, ln); yy -= (fs + 1)
            cx += cw
        y -= rh
    return y - 4

# ── the skirmish-step spine ──
def step_spine(c, x, y, w):
    """Vertical numbered flow of the Skirmish steps with roll callouts."""
    rts = {n: r["to_hit"] for n, r in rd.RETINUES.items()}
    rt_str = ", ".join(f"{n.split()[0] if n!='Knight Templar' else 'KT'} {v}+"
                        for n, v in rts.items())
    STEPS = [
        ("Form the Line", "Up to 10 front line (1 Strike die each) + up to 5 reserve. Refill between Skirmishes."),
        ("Choose Tactics", "Both pick a Tactic in secret, reveal together. (See Tactic Matrix.)"),
        ("Declare Equipment", "Attacker declares first; Defender responds."),
        ("Initiative", "Range \u22122 to +2 (Ministry: +3). Higher Strikes first. At \u22122\u2212 you Blunder (Strike only on natural 6)."),
        ("Roll to Strike", f"D6 per front-line retinue \u2265 to-Strike: {rt_str}. Natural 6 \u2192 Cleave / Deadly / Destroy Shield."),
        ("Strike & Defend", "Per Strike, defender resolves in order: Parry \u2192 Save \u2192 Recover. Unsaved = casualty (leaves field at once)."),
        ("Panic Check", "If a side took 5+ casualties this Skirmish, before it Strikes back: roll Morale (\u22645 dice). Immune Panic auto-passes. 7+ \u2192 Rout."),
        ("Strike Back", "The other side Strikes the same way, if able."),
        ("Lose Endurance", "Each side that fought: \u22121 Endurance. At 0 Endurance \u2192 Fatigued."),
        ("Break Check", "Each Fatigued field, before its token: roll Morale (\u22645 dice). Unbreakable auto-passes. Never triggers Panic. 7+ \u2192 Rout."),
        ("Fatigue Token", "Each Fatigued side gains a token: \u22121 to Strike, Parry, Recover, Morale (rolls cap 6+; Morale uncapped). Tokens stack."),
        ("End the Skirmish", "Battle ends if a side is wiped, Routs (Morale 7+), or Falls Back. Else refill and repeat."),
    ]
    num_w = 20
    title_fs, body_fs = 10.5, 8
    _set(c, ACCENT); c.setFont(SERIF_B, 12)
    c.drawString(x, y, "THE SKIRMISH"); y -= 4
    _stroke(c, RULE); c.setLineWidth(1.0); c.line(x, y, x + w, y); y -= 14
    spine_x = x + num_w / 2
    for i, (title, body) in enumerate(STEPS, 1):
        # wrap body
        words = body.split(); lines = []; cur = ""
        avail = w - num_w - 6
        for wd in words:
            t = (cur + " " + wd).strip()
            if c.stringWidth(t, SERIF, body_fs) <= avail: cur = t
            else: lines.append(cur); cur = wd
        if cur: lines.append(cur)
        block_h = 12 + len(lines) * (body_fs + 1.5) + 6
        # number disc
        _set(c, ACCENT); c.circle(spine_x, y + 3, 8, fill=1, stroke=0)
        _set(c, PARCH); c.setFont(SERIF_B, 9)
        c.drawCentredString(spine_x, y + 0.5, str(i))
        # title + body
        tx = x + num_w + 4
        _set(c, INK); c.setFont(SERIF_B, title_fs)
        c.drawString(tx, y + 1, title)
        yy = y - (body_fs + 2)
        _set(c, INK); c.setFont(SERIF, body_fs)
        for ln in lines:
            c.drawString(tx, yy, ln); yy -= (body_fs + 1.5)
        y = yy - 6
    return y

# ── FRONT PAGE ──
def front(c):
    bg(c)
    top = header(c, "Combat Quick Reference",
                 f"Renown v{rd.VERSION} \u2014 the Skirmish sequence & rolls")
    # left spine ~58% width, right column tables
    gap = 0.3 * inch
    left_w = (PAGE_W - 2 * MARGIN - gap) * 0.56
    right_x = MARGIN + left_w + gap
    right_w = PAGE_W - MARGIN - right_x

    step_spine(c, MARGIN, top, left_w)

    # right column charts
    y = top
    # Retinues
    rt_rows = [[n, f"{r['to_hit']}+", r['endurance'], f"{r['shaking']}+",
                r['cost'], ("Unbrk" if r.get('unbreakable') else "")]
               for n, r in rd.RETINUES.items()]
    y = chart(c, right_x, y, right_w, "Retinues",
              ["Type", "Strk", "End", "Mor", "Cost", ""],
              rt_rows, colw=[right_w*0.34, right_w*0.12, right_w*0.11,
                             right_w*0.12, right_w*0.18, right_w*0.13])
    y -= 6
    # Defense sequence
    def_rows = [
        ["1 Parry", "D6 \u2265 5+ cancels; nat 6 = Riposte. \u22121 vs ranged / Unstoppable / per Fatigue."],
        ["2 Save", "D6 + weapon AP + shield bonus \u2265 armor value."],
        ["3 Recover", "After failed Save: D6 \u2265 Recover value. Worsened by Fatigue & Serrated."],
    ]
    y = chart(c, right_x, y, right_w, "Defense Sequence (per Strike)",
              ["Step", "Roll"], def_rows,
              colw=[right_w*0.24, right_w*0.76], fs=7.5)
    y -= 6
    # Natural-6 triggers
    nat_rows = [
        ["Deadly", "On Strike: AP \u22125; can only be Parried or Recovered on a natural 6."],
        ["Cleave", "On Strike: roll one extra Strike die at your modified value (can chain)."],
        ["Destroy Shield", "On Strike: target loses Shield for the rest of the Battle."],
        ["Poison", "A natural 6 to Save against this retinue's Strikes fails."],
        ["Riposte", "A natural 6 on a Parry (melee): striker immediately takes a Strike back."],
    ]
    y = chart(c, right_x, y, right_w, "On a Natural 6",
              ["Keyword", "Effect"], nat_rows,
              colw=[right_w*0.26, right_w*0.74], fs=7.5)
    y -= 6
    # Standing combat effects
    se_rows = [[f"{dom} {st}", eff] for (dom, st), eff in rd.STANDING_EFFECTS.items()]
    y = chart(c, right_x, y, right_w, "Standing Combat Effects",
              ["Standing", "Effect"], se_rows,
              colw=[right_w*0.42, right_w*0.58], fs=7.5)
    y -= 8

    # The 6+ ceiling: what's clamped to 6+, what can be pushed to 7+, what's uncapped.
    cap_rows = [
        ["Blunder (Init \u22122 or lower)",
         "Your to-Strike is set to 6+ (hit only on a natural 6), before other negative modifiers."],
        ["Capped at 6+",
         "Fatigue \u22121 to to-Strike, Parry, and Recover; Planishing keeps the Save at 6+ vs any AP. A natural 6 always has a chance."],
        ["Pushes past 6+ \u2192 7+ (auto-miss)",
         "Shield \u22121 to Strike (Scutum/Tower/Heater) and enemy tactic to-Strike penalties apply AFTER the cap \u2014 they can raise the target to 7+."],
        ["Uncapped \u2192 Rout",
         "Fatigue's \u22121 to Morale is NOT capped. At modified Morale 7+ the army Routs."],
    ]
    y = chart(c, right_x, y, right_w, "The 6+ Ceiling",
              ["Rule", "Effect"], cap_rows,
              colw=[right_w*0.34, right_w*0.66], fs=7.5)

    _footer(c, "Front")
    c.showPage()

# ── tactic matrix (compact grid) ──
def tactic_grid(c, x, y, w):
    T = rd.TACTICS
    n = len(T)
    abbr = {"Scout":"Sc","Ambush":"Am","Flank":"Fl","Charge":"Ch",
            "Fighting Formation":"FF","Defensive Formation":"DF","Fall Back":"FB"}
    # full row labels: two-word tactics stack onto two lines so the label
    # column stays narrow (one word wide) and the grid stays square.
    rowlabel = {t: t.split(" ") if " " in t else [t] for t in T}
    _set(c, ACCENT); c.setFont(SERIF_B, 12)
    c.drawString(x, y, "TACTIC MATRIX")
    y -= 4
    _stroke(c, RULE); c.setLineWidth(1.0); c.line(x, y, x + w, y)
    y -= 6
    _set(c, INK); c.setFont(SERIF_I, 7)
    c.drawString(x, y, "Your tactic (row) vs opponent (col). I=Init, H=to-Strike, S=Save (lower target better).")
    y -= 12
    label_w = 50          # fits the longest single word (Defensive / Formation)
    cell = (w - label_w) / n
    rowh = 26
    def fmt(m):
        parts = []
        if m.get("end"): return "END"
        if m.get("no_combat"): return "no cbt"
        if m.get("I"): parts.append(f"I{m['I']:+d}")
        if m.get("TH"): parts.append(f"H{m['TH']:+d}")
        if m.get("TS"): parts.append(f"S{m['TS']:+d}")
        return " ".join(parts) if parts else "\u2014"
    # column headers — full names, stacked two lines (to keep columns narrow)
    _set(c, INK); c.setFont(SERIF_B, 6.8)
    cx = x + label_w
    hdr_h = 16
    for t in T:
        words = t.split(" ") if " " in t else [t]
        ty = y - (hdr_h - len(words)*7)/2 - 5
        for wd in words:
            c.drawCentredString(cx + cell/2, ty, wd); ty -= 7
        cx += cell
    y -= hdr_h
    _stroke(c, RULE); c.setLineWidth(0.5); c.line(x, y, x + w, y)
    y -= rowh
    for ri, rt in enumerate(T):
        if ri % 2 == 0:
            _set(c, BANDALT); c.rect(x, y, w, rowh, fill=1, stroke=0)
        # full row name, stacked if two words, vertically centered in the row
        _set(c, ACCENT); c.setFont(SERIF_B, 7)
        words = rowlabel[rt]
        line_h = 8
        total_h = len(words) * line_h
        ty = y + rowh/2 + total_h/2 - line_h + 1
        for wd in words:
            c.drawString(x + 1, ty, wd); ty -= line_h
        cx = x + label_w
        for ct in T:
            a, _b = rd.TACTIC_MATRIX[(rt, ct)]
            _set(c, INK); c.setFont(SERIF, 7)
            c.drawCentredString(cx + cell/2, y + rowh/2 - 2, fmt(a))
            _stroke(c, RULE); c.setLineWidth(0.2)
            c.line(cx, y, cx, y + rowh)
            cx += cell
        y -= rowh
    _stroke(c, RULE); c.setLineWidth(0.5); c.line(x, y + rowh, x + w, y + rowh)
    return y - 6

# ── BACK PAGE ──
def back(c):
    bg(c)
    top = header(c, "Combat Charts", f"Renown v{rd.VERSION} \u2014 tactics, equipment & keywords")
    full_w = PAGE_W - 2 * MARGIN

    y = tactic_grid(c, MARGIN, top, full_w)
    y -= 8

    # two columns below the matrix
    gap = 0.3 * inch
    col_w = (full_w - gap) / 2
    lx, rx = MARGIN, MARGIN + col_w + gap
    y_start = y

    # LEFT: weapons + ranged
    def kw_short(tags):
        m = {"Deadly":"Dly","Unstoppable":"Unst","Cleave":"Clv","Destroy Shield":"DShd",
             "Unwieldy":"Unw","Steady":"Stdy","2H":"2H","Nimble":"Nmb","Deflect":"Dfl",
             "One Shot":"1Sht","Poison":"Psn"}
        return ", ".join(m.get(t, t) for t in tags) or "\u2014"
    wrows = [[n, w["tier"][:3], w["ap"], f"{w['init']:+d}", kw_short(w["tags"])]
             for n, w in rd.WEAPONS.items()]
    yl = chart(c, lx, y_start, col_w, "Melee Weapons",
               ["Weapon", "Tier", "AP", "Init", "Keywords"], wrows,
               colw=[col_w*0.26, col_w*0.13, col_w*0.10, col_w*0.11, col_w*0.40],
               fs=6.6, rowh=10.5)
    rrows = [[n, w["tier"][:3], w["ap"], f"{w['init']:+d}", kw_short(w["tags"])]
             for n, w in rd.RANGED.items()]
    yl = chart(c, lx, yl - 4, col_w, "Ranged Weapons",
               ["Weapon", "Tier", "AP", "Init", "Keywords"], rrows,
               colw=[col_w*0.26, col_w*0.13, col_w*0.10, col_w*0.11, col_w*0.40],
               fs=6.6, rowh=10.5)

    # RIGHT COLUMN: Armor, Shields, then Keywords
    yr = y_start
    arows = [[n, a["tier"][:3], f"{a['save']}+"] for n, a in rd.ARMORS.items()]
    yr = chart(c, rx, yr, col_w, "Armor",
               ["Armor", "Tier", "Save"], arows,
               colw=[col_w*0.5, col_w*0.25, col_w*0.25], fs=6.8, rowh=10.5)
    srows = [[n, s["tier"][:3] if s["tier"] else "\u2014", f"+{s['save_bonus']}",
              f"{s['init']:+d}", kw_short(s["tags"])]
             for n, s in rd.SHIELDS.items() if n]
    yr = chart(c, rx, yr - 4, col_w, "Shields",
               ["Shield", "Tier", "Save", "Init", "Keywords"], srows,
               colw=[col_w*0.28, col_w*0.13, col_w*0.13, col_w*0.12, col_w*0.34],
               fs=6.6, rowh=10.5)

    # Keyword glossary (compact) — continues down the right column
    KW = [rd.SHATTER_ARMOR, rd.CLEAVE, rd.DESTROY_SHIELD, rd.POISON, rd.UNSTOPPABLE,
          rd.PARRY, rd.RIPOSTE, rd.RECOVER, rd.SERRATED, rd.PLANISHING, rd.DEFLECT,
          rd.NIMBLE, rd.DRILLED, rd.STEADY, rd.UNWIELDY, rd.BLUNDER, rd.ONE_SHOT,
          rd.IMMUNE_PANIC, rd.UNBREAKABLE, rd.FATIGUE_TOKEN, rd.MINUS_1_TBH, rd.TWO_H]
    _set(c, ACCENT); c.setFont(SERIF_B, 11)
    c.drawString(rx, yr - 4, "Keywords")
    yk = yr - 10
    _stroke(c, RULE); c.setLineWidth(0.6); c.line(rx, yk, rx + col_w, yk); yk -= 12
    for k in KW:
        if k not in rd.GLOSSARY: continue
        defn = " ".join(str(rd.GLOSSARY[k]).split())
        _set(c, INK); c.setFont(SERIF_B, 7.0)
        c.drawString(rx, yk, k)
        kw_w = c.stringWidth(k + "  ", SERIF_B, 7.0)
        c.setFont(SERIF, 6.6)
        words = defn.split(); line = ""; first = True; yy = yk
        tx0 = rx + kw_w
        for wd in words:
            t = (line + " " + wd).strip()
            w_avail = (col_w - kw_w) if first else col_w
            if c.stringWidth(t, SERIF, 6.6) <= w_avail:
                line = t
            else:
                c.drawString(tx0 if first else rx, yy, line)
                yy -= 7.5; first = False; tx0 = rx; line = wd
        c.drawString(tx0 if first else rx, yy, line)
        yk = yy - 8.5

    _footer(c, "Back")
    c.showPage()

def _footer(c, label):
    _set(c, RULE); c.setFont(SERIF_I, 7)
    c.drawString(MARGIN, MARGIN - 6, f"Renown \u2014 Combat Quick Reference ({label})")
    c.drawRightString(PAGE_W - MARGIN, MARGIN - 6, f"v{rd.VERSION}")

def build(out_path):
    c = canvas.Canvas(out_path, pagesize=letter)
    c.setTitle("Renown — Combat Quick Reference")
    front(c)
    back(c)
    c.save()
    print(f"wrote combat sheet -> {out_path}")

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "combat_sheet.pdf")