#!/usr/bin/env python3
"""Build ESCALATION_CAMPAIGN.pdf. Portrait main doc + a merged LANDSCAPE two-player Domain Board page."""
import sys
sys.path.insert(0, ".")
import renown_combat as rc
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle, NextPageTemplate, PageBreak,
                                Image as RLImage, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
_FDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
for _n, _f in [("EBGaramond", "EBGaramond-Regular.ttf"), ("EBGaramond-Bold", "EBGaramond-Bold.ttf"),
               ("EBGaramond-Italic", "EBGaramond-Italic.ttf"), ("EBGaramond-BoldItalic", "EBGaramond-BoldItalic.ttf")]:
    pdfmetrics.registerFont(TTFont(_n, os.path.join(_FDIR, _f)))
pdfmetrics.registerFontFamily("EBGaramond", normal="EBGaramond", bold="EBGaramond-Bold",
                              italic="EBGaramond-Italic", boldItalic="EBGaramond-BoldItalic")
from pypdf import PdfReader, PdfWriter
import subprocess

PAGE = letter
M = 0.45 * inch
W = PAGE[0] - 2 * M
ink = colors.HexColor("#1a1a1a"); accent = colors.HexColor("#7a1f1f")
rule = colors.HexColor("#888888"); zebra = colors.HexColor("#f2efe9")
slot = colors.HexColor("#efe9df"); white = colors.white
D_IND, D_PROW, D_PIETY, D_CUN, D_EDICT = (colors.HexColor("#1f4e8c"), colors.HexColor("#9e1b1b"),
    colors.HexColor("#e8c200"), colors.HexColor("#1a1a1a"), colors.HexColor("#5d2e8e"))
T_IND, T_PROW, T_PIETY, T_CUN, T_MON = (colors.HexColor("#e6ecf4"), colors.HexColor("#f4e2e2"),
    colors.HexColor("#f7eccb"), colors.HexColor("#e8e8e8"), colors.HexColor("#ece3f3"))

S = dict(
    h1=ParagraphStyle("h1", fontName="EBGaramond-Bold", fontSize=17, leading=19, textColor=accent, spaceAfter=2),
    sub=ParagraphStyle("sub", fontName="EBGaramond-Italic", fontSize=8.5, leading=10, textColor=colors.HexColor("#555"), spaceAfter=6),
    h2=ParagraphStyle("h2", fontName="EBGaramond-Bold", fontSize=10.5, leading=12, textColor=accent, spaceBefore=6, spaceAfter=2),
    b=ParagraphStyle("b", fontName="EBGaramond", fontSize=8.8, leading=10.6, textColor=ink),
    step=ParagraphStyle("step", fontName="EBGaramond", fontSize=8.4, leading=10.1, textColor=ink, spaceAfter=1.8, leftIndent=10, firstLineIndent=-10),
    bsm=ParagraphStyle("bsm", fontName="EBGaramond", fontSize=7.5, leading=9.0, textColor=ink),
    cell=ParagraphStyle("cell", fontName="EBGaramond", fontSize=7.3, leading=8.6, textColor=ink),
    tc=ParagraphStyle("tc", fontName="EBGaramond", fontSize=7.0, leading=8.2, textColor=ink),
    tcb=ParagraphStyle("tcb", fontName="EBGaramond-Bold", fontSize=7.0, leading=8.2, textColor=ink),
    mon=ParagraphStyle("mon", fontName="EBGaramond-Bold", fontSize=7.0, leading=8.2, textColor=D_EDICT),
    grpw=ParagraphStyle("grpw", fontName="EBGaramond-Bold", fontSize=7.8, leading=9.2, textColor=white),
    grpk=ParagraphStyle("grpk", fontName="EBGaramond-Bold", fontSize=7.8, leading=9.2, textColor=ink),
    board=ParagraphStyle("board", fontName="EBGaramond-Bold", fontSize=10, leading=11.5, textColor=ink, alignment=1),
    boardhdr=ParagraphStyle("boardhdr", fontName="EBGaramond-Bold", fontSize=9.5, leading=11, textColor=white, alignment=1),
    boardblk=ParagraphStyle("boardblk", fontName="EBGaramond-Bold", fontSize=9.5, leading=11, textColor=ink, alignment=1),
    blabel=ParagraphStyle("blabel", fontName="EBGaramond-Bold", fontSize=7, leading=8, textColor=white, alignment=1),
    blabelk=ParagraphStyle("blabelk", fontName="EBGaramond-Bold", fontSize=7, leading=8, textColor=ink, alignment=1),
)
def P(t, st="b"): return Paragraph(t, S[st])
MIN = "\u2212"  # proper minus sign for numeric consistency
def numf(x): return str(x).replace("-", MIN)
def initf(v): return (f"+{v}" if v > 0 else (numf(v) if v < 0 else "0"))
def tagf(tlist): return (", ".join(tlist) or "—").replace("-1TBH", MIN + "1 to Strike")

def tbl(rows, widths, header=True, font=7.2, pad=1.7, right_cols=()):
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    st = [("FONTNAME", (0, 0), (-1, -1), "EBGaramond"), ("FONTSIZE", (0, 0), (-1, -1), font),
          ("LEADING", (0, 0), (-1, -1), font + 1.2), ("TEXTCOLOR", (0, 0), (-1, -1), ink),
          ("TOPPADDING", (0, 0), (-1, -1), pad), ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
          ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
          ("LINEBELOW", (0, 0), (-1, 0), 0.7, rule),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, zebra]), ("VALIGN", (0, 0), (-1, -1), "TOP")]
    for c in right_cols:
        st.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    if header: st.append(("FONTNAME", (0, 0), (-1, 0), "EBGaramond-Bold"))
    t.setStyle(TableStyle(st)); return t

BHDR = ["Pursuit", "Build Action Req", "Mastery Req", "Innate Effect", "Mastery Effect"]
BW = [W*0.18, W*0.22, W*0.22, W*0.17, W*0.21]
def btable(tint, rows):
    data = [[P(h, "tcb") for h in BHDR]]
    style = [("FONTNAME", (0, 0), (-1, 0), "EBGaramond-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 7.0),
             ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
             ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
             ("LINEBELOW", (0, 0), (-1, 0), 0.7, rule), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, tint])]
    r = 1
    for (nm, breq, mreq_, inn, mas, isM) in rows:
        data.append([Paragraph(nm, S["mon"] if isM else S["tcb"]),
                     P(breq, "tc"), P(mreq_, "tc"), P(inn, "tc"), P(mas, "tc")])
        if isM:
            style.append(("BACKGROUND", (0, r), (-1, r), T_MON))
        r += 1
    t = Table(data, colWidths=BW, repeatRows=1)
    t.setStyle(TableStyle(style)); return t

def make_board(sovereign=True):
    CELL = 40 * mm
    def bc(t): return Paragraph(t, S["board"])
    full = [
        [P("Domain", "boardhdr"), P("Rising", "boardhdr"), P("Established", "boardhdr"), P("Sovereign", "boardhdr")],
        [P("Industry", "boardhdr"), bc("Build<br/>Action"), bc("Build<br/>Action"), bc("Build<br/>Action")],
        [P("Prowess", "boardhdr"), bc("Immune<br/>Blocked"), bc("Parry"), bc("Edict only")],
        [P("Piety", "boardblk"), bc("Gain<br/>Established<br/>Piety"), bc("Improve<br/>Morale +1"), bc("Edict only")],
        [P("Cunning", "boardhdr"), bc("Foes gain<br/>Blocked"), bc("Gain<br/>Sovereign<br/>Cunning"), bc("Foes gain<br/>Strained")],
    ]
    n = 4 if sovereign else 3
    board = [row[:n] for row in full]
    last = n - 1
    t = Table(board, colWidths=[24 * mm] + [CELL] * (n - 1), rowHeights=[8 * mm, CELL, CELL, CELL, CELL])
    style = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (0, 1), D_IND), ("BACKGROUND", (0, 2), (0, 2), D_PROW),
        ("BACKGROUND", (0, 3), (0, 3), D_PIETY), ("BACKGROUND", (0, 4), (0, 4), D_CUN),
        ("BACKGROUND", (1, 1), (-1, -1), slot), ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#bbbbbb")),
        ("BOX", (1, 1), (-1, -1), 1.0, rule), ("INNERGRID", (1, 1), (-1, -1), 1.0, rule)]
    if sovereign:
        style += [("BACKGROUND", (0, 0), (last - 1, 0), accent), ("BACKGROUND", (last, 0), (last, 0), D_EDICT)]
    else:
        style.append(("BACKGROUND", (0, 0), (last, 0), accent))
    t.setStyle(TableStyle(style))
    return t

def make_two_player_board():
    """One shared grid: a single Domain label column, then Player 1's three standings and
    Player 2's three standings. Sovereign columns kept (purple)."""
    CELL = 40 * mm; LBL = 24 * mm; H1 = 7 * mm; H2 = 9 * mm
    def bc(t): return Paragraph(t, S["board"])
    A = {"Industry": ["Build<br/>Action", "Build<br/>Action", "Build<br/>Action"],
         "Prowess": ["Immune<br/>Blocked", "Parry", "Edict only"],
         "Piety": ["Gain<br/>Established<br/>Piety", "Improve<br/>Morale +1", "Edict only"],
         "Cunning": ["Foes gain<br/>Blocked", "Gain<br/>Sovereign<br/>Cunning", "Foes gain<br/>Strained"]}
    doms = [("Industry", "boardhdr", D_IND), ("Prowess", "boardhdr", D_PROW),
            ("Piety", "boardblk", D_PIETY), ("Cunning", "boardhdr", D_CUN)]
    rows = [[P("Domain", "boardhdr"), P("PLAYER 1", "boardhdr"), "", "", P("PLAYER 2", "boardhdr"), "", ""],
            ["", P("Rising", "boardhdr"), P("Established", "boardhdr"), P("Sovereign", "boardhdr"),
                 P("Rising", "boardhdr"), P("Established", "boardhdr"), P("Sovereign", "boardhdr")]]
    for d, st, _ in doms:
        rows.append([P(d, st)] + [bc(x) for x in A[d]] + [bc(x) for x in A[d]])
    t = Table(rows, colWidths=[LBL] + [CELL] * 6, rowHeights=[H1, H2, CELL, CELL, CELL, CELL])
    style = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("SPAN", (0, 0), (0, 1)), ("SPAN", (1, 0), (3, 0)), ("SPAN", (4, 0), (6, 0)),
        ("BACKGROUND", (0, 0), (0, 1), accent), ("BACKGROUND", (1, 0), (6, 0), accent),
        ("BACKGROUND", (1, 1), (2, 1), accent), ("BACKGROUND", (3, 1), (3, 1), D_EDICT),
        ("BACKGROUND", (4, 1), (5, 1), accent), ("BACKGROUND", (6, 1), (6, 1), D_EDICT),
        ("BACKGROUND", (1, 2), (-1, -1), slot),
        ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#bbbbbb")),
        ("BOX", (1, 2), (-1, -1), 1.0, rule), ("INNERGRID", (1, 2), (-1, -1), 1.0, rule),
        ("LINEAFTER", (3, 0), (3, -1), 1.6, ink)]
    for i, (d, st, col) in enumerate(doms):
        style.append(("BACKGROUND", (0, 2 + i), (0, 2 + i), col))
    t.setStyle(TableStyle(style))
    return t

LEGEND = ("<font color='#1f4e8c'><b>■</b></font> Industry &nbsp; <font color='#9e1b1b'><b>■</b></font> Prowess &nbsp; "
          "<font color='#b89400'><b>■</b></font> Piety &nbsp; <font color='#1a1a1a'><b>■</b></font> Cunning &nbsp; "
          "<font color='#5d2e8e'><b>■</b></font> Edict (Sovereign standing or Monument)")

# ════════════════════ LANDSCAPE TWO-PLAYER BOARD PAGE (separate doc, merged later) ════════════════════
LM = 0.2 * inch
LPAGE = landscape(letter)
LW = LPAGE[0] - 2 * LM
bdoc = BaseDocTemplate("board.pdf", pagesize=LPAGE, leftMargin=LM, rightMargin=LM, topMargin=LM, bottomMargin=LM)
bdoc.addPageTemplates([PageTemplate(id="land", frames=[Frame(LM, LM, LW, LPAGE[1] - 2 * LM, id="lf")])])
bstory = [P("DOMAIN BOARDS — ONE GRID, BOTH PLAYERS", "h1"),
          P("Each player tracks their own three columns (one shared Domain column). Cover every ability cell with a "
            "40&nbsp;mm base at setup; remove a base when you unlock that standing. A Sovereign cell also scores an "
            "Edict (+1 VP).", "sub")]
brd = make_two_player_board(); brd.hAlign = "CENTER"
bstory += [Spacer(1, 4), brd, Spacer(1, 6), P(LEGEND, "bsm")]
bdoc.build(bstory)

# ════════════════════ MAIN PORTRAIT DOC ════════════════════
doc = BaseDocTemplate("main.pdf", pagesize=PAGE, leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
                      title="Renown — Escalation Campaign", author="Renown")
doc.addPageTemplates([PageTemplate(id="one", frames=[Frame(M, M, W, PAGE[1] - 2 * M, id="full")])])
story = []

story.append(P("RENOWN — ESCALATION CAMPAIGN", "h1"))
story.append(P("A fast, battle-driven mode for 2+ players. Ten+ turns.", "sub"))
story.append(P("DICE PRINCIPLE", "h2"))
story.append(P("A successful roll is written as <b>X+</b>: roll that number or higher on a <b>d6</b>. Apply modifiers to the "
               "<b>roll</b>: <b>+1</b> per bonus, <b>−1</b> per penalty: each negative modifier requires your roll to be one "
               "higher to succeed, each positive modifier one lower. "
               "<b>If a 7 or more is ever needed to succeed a roll, it automatically fails; if a 1 or less is ever needed, it "
               "automatically passes. Note:</b> if a roll automatically passes or fails but a natural result could still "
               "trigger an effect, you still roll the die to see whether that effect triggers.", "b"))
story.append(P("A <b>natural</b> roll is the die before modifiers. A <b>natural 6</b> triggers <b>Cleave, Deadly, Destroy "
               "Shield and Riposte</b> (and a natural-6 Save fails against Poison).", "b"))
story.append(P("<b>The rolls:</b> <b>Roll-off</b> — higher <b>Seizes the Initiative</b>; <b>to Strike</b> — roll ≥ to-Strike number; "
               "<b>Parry</b> — roll ≥ 5 (Improved 4+), natural 6 = Riposte; <b>to Save</b> — roll − AP + shield bonus ≥ armor value; "
               "<b>Recover</b> — roll ≥ X; <b>Panic</b> — roll ≥ Morale value; <b>Break</b> — roll ≥ Morale value.", "b"))
story.append(P("SETUP", "h2"))
story.append(P("Each player starts with an <b>army composition</b> of <b>25 Levy retinues, Farm Tools, Cloth armor, no shield</b>. "
               "All four Domains (<b>Industry, Prowess, Piety, Cunning</b>) start <b>Untested</b> (no effect). "
               "No Pursuits, 0 Victory Points (VP). Every Battle is fought at an army size of <b>25</b>; "
               "what carries over between Battles is your <b>Standings, Pursuits, unlocks, and VP</b>."))
story.append(P("TURN SEQUENCE", "h2"))
story.append(P("<b>1 — BATTLE.</b> Pair off and fight one Battle (rotate pairings each turn).", "b"))
story.append(tbl([["Result", "VP"],
                  ["Decisive Win: Reduce the enemy army to zero or cause a Rout.", "+3"],
                  ["Minor Victory: The enemy army Fell Back.", "+2"],
                  ["Lose, but end it via a successful Fall Back with 1+ retinue remaining.", "+1"],
                  ["Lose any other way (wiped out, Routed, failed Fall Back).", "0"]], [W * 0.84, W * 0.16]))
story.append(Spacer(1, 3))
story.append(P("<b>2 — ADVANCEMENT</b> (all players simultaneously):", "b"))
story.append(P("• <b>Unlock one Domain Standing</b>: advance any one Domain one step — Untested → Rising → Established → Sovereign, if the prior standing is already unlocked.<br/>"
               "• <b>Perform one Build Action</b>: construct one Pursuit whose build requirements you satisfy.<br/>"
               "• <b>You may change your army to any other composition you have unlocked.</b> You must announce it before the "
               "end of the turn. If it's an issue, both players play their army's composition face down and reveal simultaneously.", "b"))
story.append(P("BATTLE WALKTHROUGH", "h2"))
story.append(P("<b>Begin the Battle — roll off for the Initiative.</b> Each player rolls one d6 — <b>+1 if you won your last "
               "Battle</b> — re-rolling ties. The higher roller <b>Seizes the Initiative</b>: they are the <b>Attacker</b> for "
               "this Battle and gain <b>+1 Initiative in the first Skirmish</b>; their opponent is the <b>Defender</b>.", "b"))
story.append(P("Fought as a series of <b>Skirmishes</b> — repeat these steps each Skirmish until the Battle ends; rule detail is in the Glossary.", "bsm"))
steps = [
 ("1. Form the Field.", "Each player places the maximum retinues available into the field, up to <b>10</b> retinues in the front line — one attack each — and up to 5 in reserve to replace losses before striking back."),
 ("2. Choose Tactics.", "Both players secretly pick one <b>Tactic</b>, then reveal simultaneously."),
 ("3. Declare equipment.", "The <b>Attacker</b> names their equipment first; the <b>Defender</b> then names theirs."),
 ("4. Initiative.", "Initiative runs from <b>−2 to +2</b>. The higher Initiative Strikes first this Skirmish. At <b>−2 or lower you Blunder</b> — your <b>Strike</b> value cannot be improved beyond 6+."),
 ("5. Roll to Strike.", "Roll a d6 for each front-line retinue. To calculate the to-Strike result needed: the Retinue's to-Strike, plus positive modifiers, minus 1 per Fatigue token, to a maximum of 6+, and then any other remaining negative modifiers."),
 ("6. Strike and defend.", "Resolve the first player's <b>Strikes</b> — <b>Parry</b> (immediately resolve <b>Ripostes</b>), then <b>Save</b>, then <b>Recover</b>; the rest are casualties. Casualties leave the field immediately, lowering its <b>Field</b> count."),
 ("7. Panic check.", "If any army takes <b>5 or more casualties</b> this Skirmish from combat at any time, it takes a <b>Panic check</b> immediately: roll a d6 per retinue in the field, <b>up to 5 dice</b>. If the result is ever <b>modified to require 7 or more, that army Routs instead</b>. You Panic at most once per Skirmish."),
 ("8. Strike back.", "The other player Strikes the same way, if able."),
 ("9. Lose Endurance.", "Each army that participated loses 1 Endurance. A player's army at 0 Endurance is <b>Fatigued</b>."),
 ("10. Break check.", "Each <b>Fatigued</b> player's field takes a <b>break check</b> — before it gains a token: roll a d6 per retinue in the field, <b>up to 5 dice</b>, roll against <b>its modified Morale value</b> — modified negatively by 1 per Fatigue token and by other positive modifiers. Failures are casualties; a break check never triggers a Panic check. A Morale value ever <b>modified to 7 or more Routs the whole army</b>."),
 ("11. Fatigue token.", "Then each Fatigued side gains a <b>Fatigue token</b> — each is <b>−1 to its Strike, Morale, Parry and Recover rolls</b>, all capped at 6+ except Morale (uncapped), and they stack."),
 ("12. End the Skirmish.", "The Battle ends if a player's army size is reduced to 0, Routs, or successfully <b>Falls Back</b>. Otherwise start the next Skirmish at step 1. You cannot Fall Back during the first and second Skirmish of any Battle."),
]
for head, body in steps:
    story.append(P(f"<b>{head}</b> {body}", "step"))
story.append(PageBreak())

# ── ARMORY ──
# All five tables share ONE column grid so headers and numbers align vertically down the page:
#   name 0.16 | stat 0.06 | stat 0.06 | stat 0.06 | wide 0.32 | mid 0.24 | tier 0.10
#   (boundaries at 0.16 / 0.22 / 0.28 / 0.34 / 0.66 / 0.90 of W)
# Tables missing a stat carry a blank spacer column in that slot.
GRID7 = [W*0.16, W*0.06, W*0.06, W*0.06, W*0.32, W*0.24, W*0.10]
story.append(P("ARMORY REFERENCE", "h1"))
story.append(P("RETINUES <font size=7 color='#555'>(the physical capability of your Troops)</font>", "h2"))
notes = {"Levy": "—", "Man-at-Arms": "—", "Sergeant": "—", "Knight Templar": "Unbreakable"}
unlock = {"Levy": "—", "Man-at-Arms": "Coliseum", "Sergeant": "War College", "Knight Templar": "Preceptory"}
rows = [["Retinue", "Strike", "Endur", "Morale", "Notes", "Unlock", ""]]
for k, v in rc.RETINUES.items():
    rows.append([k, f"{v['to_hit']}+", v["endurance"], v["shaking"], notes[k], unlock[k], ""])
story.append(tbl(rows, GRID7, right_cols=(1, 2, 3)))
story.append(P("WEAPON TIERS", "h2"))
story.append(P("Five tiers, worst to best: <b>Crude · Cast · Wrought · Forged · Crafted</b>. Each tier is unlocked by an Industry Pursuit (see that Pursuit's effect under Pursuits). A weapon's tier is shown in its Tier column.", "b"))
story.append(P("MELEE WEAPONS <font size=7 color='#555'>(Unwieldy = cannot gain Initiative from Tactics; vice versa for Steady)</font>", "h2"))
WNOTE = {"Lance": "Needs Stable; no Tower Shield or Crossbow dual", "Cavalry Spear": "Needs Stable; no Tower Shield or Crossbow dual"}
rows = [["Weapon", "AP", "Init", "", "Tags", "Note", "Tier"]]
for k, v in rc.WEAPONS.items():
    rows.append([k, numf(v["ap"]), initf(v["init"]), "",
                 Paragraph(tagf(v["tags"]), S["tc"]),
                 Paragraph(WNOTE.get(k, "—"), S["tc"]), v["tier"]])
story.append(tbl(rows, GRID7, right_cols=(1, 2)))
story.append(P("RANGED <font size=7 color='#555'>(all have Deflect; Fletchery to equip, Tiltyard to dual-equip. Deflect: −1 to Parry saves from Deflect weapons; cannot be Riposted)</font>", "h2"))
RNOTE = {"Crossbow": "Tower Shield only (no other shield permitted)"}
rows = [["Weapon", "AP", "Init", "", "Tags", "Note", "Tier"]]
for k, v in rc.RANGED.items():
    rows.append([k, numf(v["ap"]), initf(v["init"]), "",
                 Paragraph(tagf([t for t in v["tags"] if t != "Deflect"]), S["tc"]),
                 Paragraph(RNOTE.get(k, "—"), S["tc"]), v["tier"]])
story.append(tbl(rows, GRID7, right_cols=(1, 2)))
story.append(P("SHIELDS <font size=7 color='#555'>(require Joinery + the matching metal-tier building)</font>", "h2"))
rows = [["Shield", "Save", "Init", "", "Tags", "Tier"]]
for k, v in rc.SHIELDS.items():
    if k is None: continue
    rows.append([k.replace(" Shield", ""), f"+{v['save_bonus']}", initf(v["init"]), "", tagf(v["tags"]), v["tier"]])
story.append(tbl(rows, [W*0.16, W*0.06, W*0.06, W*0.06, W*0.56, W*0.10], right_cols=(1, 2)))
story.append(P("ARMOR <font size=7 color='#555'>(Save target; heavier Armor grants Unwieldy — nothing happens if Unwieldy stacks)</font>", "h2"))
au = {"Cloth": "—", "Leather": "Tannery", "Chainmail": "Armory", "Full Plate": "Gilded Foundry", "Gothic Plate": "Advanced Blast Furnace"}
rows = [["Armor", "Save", "", "Tags", "Unlocked by", "Tier"]]
for k, v in rc.ARMORS.items():
    rows.append([k, f"{v['save']}+", "", ", ".join(v["tags"]) or "—", au[k], v["tier"]])
story.append(tbl(rows, [W*0.16, W*0.06, W*0.12, W*0.32, W*0.24, W*0.10], right_cols=(1,)))
story.append(PageBreak())

# ── BUILDINGS (5-column, colour-coded by domain) ──
story.append(P("PURSUITS", "h1"))
story.append(P("Organised by Domain (colour-coded); rows alternate in the Domain tint and <b>monuments are the purple rows</b>. "
               "<b>Build Action Req = the Domain Standing only</b> (the sole build requirement); every Pursuit listed under "
               "<b>Mastery Req</b> is needed to master, not to build.", "sub"))
story.append(P(LEGEND, "bsm")); story.append(Spacer(1, 3))

story.append(P("<font color='#1f4e8c'>INDUSTRY</font>", "h2"))
story.append(btable(T_IND, [
 ("Furnace", "—", "—", "Cast weapons", "—", False),
 ("Blacksmith", "Rising Industry", "Furnace", "—", "Wrought weapons", False),
 ("Forge", "Established Industry", "Blacksmith, Furnace", "—", "Forged weapons", False),
 ("Tannery", "—", "Animal Husbandry", "—", "Leather armor", False),
 ("Armory", "Rising Industry", "Tannery, Blacksmith", "—", "Chainmail", False),
 ("Gilded Foundry", "Established Industry", "Armory, Blacksmith", "Full Plate", "Planishing", False),
 ("Master Workshop", "Established Industry", "Forge, Blacksmith", "—", "Serrated", False),
 ("Joinery", "Rising Industry", "Carpentry", "—", "Shields", False),
 ("Stable", "—", "Animal Husbandry, Blacksmith or Carpentry", "—", "Cavalry weapons (Lance, Cavalry Spear)", False),
 ("Advanced Blast Furnace", "Sovereign Industry", "Gilded Foundry, Master Workshop, Blacksmith, Stable, Forge", "—", "Crafted tier", True),
]))
story.append(P("<font color='#9e1b1b'>PROWESS</font>", "h2"))
story.append(btable(T_PROW, [
 ("Conditioning Field", "—", "—", "+1 Endurance", "—", False),
 ("Coliseum", "Rising Prowess", "Conditioning Field", "—", "Man-at-Arms unlock", False),
 ("Fletchery", "—", "Carpentry", "—", "Ranged weapons", False),
 ("Grand Tournament", "Established Prowess", "Conditioning Field, Coliseum", "Improved Parry", "Riposte", False),
 ("Tiltyard", "Established Prowess", "Fletchery, Coliseum", "Dual-equip; weapons gain Unwieldy while dual-equipped", "Immune Unwieldy", False),
 ("War College", "Established Prowess", "Levy Hall, Academy", "—", "Sergeant unlock", False),
 ("Royal Pavilion", "Sovereign Prowess", "Grand Tournament, Tiltyard", "Immune Strain", "Drilled, Nimble", True),
 ("Ministry of Military Strategy", "Sovereign Prowess", "University, War College", "Seize the Initiative in Skirmish 1; Immune -1 to-Strike Tactics", "Gain +1I, max Initiative +3. Riposte, Deadly, Cleave, and Destroy Shield on natural 5.", True),
]))
story.append(P("<font color='#b89400'>PIETY</font>", "h2"))
story.append(btable(T_PIETY, [
 ("Apothecary", "—", "Herb Garden or Alchemy", "—", "Heal 4", False),
 ("Infirmary", "—", "Apothecary, Herb Garden or Alchemy", "—", "Recover 6; +1 if already gained", False),
 ("Hospitaller", "Established Piety", "Apothecary, Infirmary", "Recover +1", "Recover +1", False),
 ("Preceptory of the Knight's Templar", "Sovereign Piety + Established Prowess", "Monastery, Pilgrimage Site, Hospitaller, Abbey", "Immune Panic", "Knight Templar unlock", True),
]))
story.append(P("<font color='#1a1a1a'>CUNNING</font>", "h2"))
story.append(btable(T_CUN, [
 ("Toxicarium", "Rising Cunning", "Academy", "—", "Poison", False),
 ("Outrider Intercept Post", "Sovereign Cunning", "Caravanery, Cipher Chamber", "Once each battle (Skirmish 1), see the enemy's Tactic before you choose yours", "Every Skirmish, you may force your opponent to reveal their Tactic before you select yours", True),
]))
story.append(PageBreak())

# ── GLOSSARY ──
story.append(P("GLOSSARY", "h2"))
G = [
 ("Battle", "One fight between two players (Turn step 1), resolved as a series of Skirmishes until a side is wiped out, Routs, or Falls Back."),
 ("Skirmish", "One round of a Battle, run through the numbered Battle steps; a Battle repeats Skirmishes until it ends."),
 ("Field", "Your retinues in play — front line (up to 10) plus reserve (up to 5). Casualties leave the field at once, lowering its count."),
 ("Natural roll", "The number on the die before any modifiers. A natural 6 triggers Cleave, Deadly, Destroy Shield and Riposte — modifiers never change what counts as 'natural'."),
 ("Strike", "A landed hit. Roll a d6, apply modifiers to the roll, and Strike on a result ≥ the to-Strike number. The target may then Parry, Save, and Recover."),
 ("to-Strike", "The d6 result a retinue needs to roll to successfully Strike. Bonuses add to the roll; penalties and Fatigue tokens subtract."),
 ("Initiative", "Decides who Strikes first each Skirmish (higher first). Runs −2 to +2 (Ministry can raise the maximum to +3). At −2 or lower you Blunder — your Strike value cannot be improved beyond 6+."),
 ("Seize the Initiative", "Won by the roll-off at the start of the Battle — the winner of their last Battle adds +1 to the roll. You become the Attacker and gain +1 Initiative in the first Skirmish. Some Tactics and the Ministry monument also grant it."),
 ("Attacker / Defender", "Set by the roll-off. Each Skirmish the Attacker declares equipment first; the Defender then responds."),
 ("Tactic", "A choice both players make secretly and reveal together each Skirmish; it can shift Initiative and Strike rolls."),
 ("Parry", "Roll a d6 to cancel a Strike on a 5+ (a natural 6 is a Riposte). −1 versus Unstoppable, versus ranged, and per Fatigue token (to a maximum of 6+). A Deadly Strike can only be Parried on a natural 6."),
 ("Improved Parry", "Your Parry succeeds on 4+ instead of 5+."),
 ("Riposte", "A Parry of a natural 6 cancels the Strike and Strikes back once; it does not bypass a Deadly Strike's natural-6 restriction."),
 ("Save", "The defender's roll to avoid a casualty: roll a d6, add the weapon's AP (a negative) and the shield's Save bonus (a positive); the hit is saved on a result ≥ the armor value (Cloth 6+ … Gothic Plate 2+)."),
 ("AP", "Armor Penetration — a weapon's (negative) modifier to the defender's Save roll. Reduce the result of the roll by 1 per AP."),
 ("Casualty", "A retinue removed from the field — from an unsaved Strike or a failed Panic or Break check."),
 ("Recover X", "After a failed Parry and Save, roll a d6: a result of X+ saves the retinue (worsened by Fatigue and Serrated, to a maximum of 6+). Against a Deadly Strike, only a natural 6 Recovers."),
 ("Heal X", "At the end of each Skirmish, for every X casualties you took from Strikes, return 1 retinue to your Army."),
 ("Endurance", "A side's stamina. Each side that fights loses 1 per Skirmish; at 0 it becomes Fatigued."),
 ("Fatigued", "A side at 0 Endurance. Each Skirmish its field takes a break check, then it gains a Fatigue token (see Fatigue token)."),
 ("Fatigue token", "Each token is −1 to that army's Strike, Morale, Parry and Recover rolls for the rest of the Battle — all capped at 6+ except Morale, which is uncapped, so enough tokens will Rout the army. They stack."),
 ("Morale", "A test used to determine whether retinues Flee as casualties. Break and Panic checks both roll it: a d6 per retinue in the field, up to 5 dice, each ≥ its modified Morale value; failures are casualties. Any such check ever modified to 7 or more Routs the whole army."),
 ("Break check", "Taken by each Fatigued side's field every Skirmish, just before it gains its Fatigue token. Roll Morale (up to 5 dice); failures are casualties, but a break check never triggers a Panic check. Unbreakable retinues auto-pass it."),
 ("Panic check", "Taken at once by a side that suffered 5 or more casualties in a Skirmish, before it Strikes back. Roll a d6 per retinue in the field, up to 5 dice; Immune Panic auto-passes it."),
 ("Rout", "The army breaks and leaves the Battle (you lose it). A Panic or break check ever modified to 7 or more Routs the whole army automatically."),
 ("Fall Back", "A controlled retreat that ends the Battle with at least one retinue left from the Fall Back tactic — a partial success worth +1 VP."),
 ("Edict", "A scoring achievement worth +1 VP: reach a Sovereign Standing, or complete (master) a Monument."),
 ("Monument", "A Domain's capstone Pursuit (the purple rows). Completing one scores its Edict (+1 VP) and grants a powerful effect. Only one of each Monument can be built each game."),
 ("Nimble", "+1 Initiative in the first Skirmish."),
 ("Drilled", "No Endurance loss in the first Skirmish."),
 ("Unwieldy", "Your Initiative cannot be improved by Tactics."),
 ("Steady", "Your Initiative cannot be reduced by Tactics."),
 ("Blocked", "−1 Initiative in the first Skirmish (negated by Immune Blocked)."),
 ("Strained", "−1 Initiative every Skirmish (negated by Immune Strain)."),
 ("Immune [keyword]", "Cancels that keyword as it applies to you — e.g. Immune Unwieldy, Strain, Blocked, Panic or Destroy Shield."),
 ("2H", "Two-handed: no shield. A Bastard Sword may choose its profile during the declare equipment phase."),
 ("Dual-equip", "Carry two weapons at once (e.g. melee + ranged). Granted by the Tiltyard, which also gives Unwieldy until its mastery removes it."),
 ("Deadly", "On a natural 6 to Strike, AP is increased by -5; the Strike can only be Parried or Recovered on a natural 6."),
 ("Cleave", "Each natural 6 to Strike adds one extra Strike."),
 ("Destroy Shield", "A natural 6 against a shield-bearer destroys their shield for the rest of the Battle."),
 ("Unbreakable", "Automatically passes all Break checks."),
    ("Unstoppable", "Ignore the target shield's −1 to Strike, and the target's Parry is −1 against you."),
 ("Serrated", "Your Strikes worsen the enemy's Recover roll by 1 — enough to deny Recover entirely. (Master Workshop mastery.)"),
 ("Poison", "The defender's Save fails on a natural 6 (Toxicarium mastery)."),
 ("One Shot", "A ranged weapon can be equipped in the first Skirmish only. If you have no other weapon, you must use Farm Tools after the first Skirmish. Requires a Tiltyard."),
 ("Deflect", "Every ranged weapon has it: a ranged Strike is −1 to Parry and never Ripostes."),
 ("Shield (−1 to Strike)", "Attackers Striking a shield-bearer take −1 to the Strike roll."),
 ("Planishing", "Your to Save cannot be reduced beyond 6+"),
]
def glossary_table(entries, width):
    gs = ParagraphStyle("gl", fontName="EBGaramond", fontSize=8.2, leading=9.4, textColor=ink, spaceAfter=3.4)
    ents = sorted(entries, key=lambda e: e[0].lower())
    half = (len(ents) + 1) // 2
    col = lambda items: [Paragraph(f'<b><font color="#5d2e8e">{t}</font></b> — {d}', gs) for t, d in items]
    cw = (width - 12) / 2
    t = Table([[col(ents[:half]), col(ents[half:])]], colWidths=[cw, cw])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (0, -1), 0), ("LEFTPADDING", (1, 0), (1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    return t
story.append(glossary_table(G, W))

doc.build(story)

# ════════════════════ TALENT TREE — regenerate from renown_data and render via Graphviz ════════════════════
# nodes_escalation.csv <- renown_data (current), then render_trees_2x2.py -> talent_tree_2x2.pdf (landscape page)
_HAVE_TREE = True
try:
    subprocess.run([sys.executable, "gen_escalation_nodes.py", "nodes_escalation.csv"], check=True)
    subprocess.run([sys.executable, "render_trees_2x2.py", "nodes_escalation.csv", "talent_tree_2x2"], check=True)
except Exception as _e:
    _HAVE_TREE = False
    print("NOTE: talent tree render failed -> tree page skipped (%s)" % _e)

# ════════════════════ TACTIC MATRIX — one landscape sheet ════════════════════
tdoc = BaseDocTemplate("tactics.pdf", pagesize=LPAGE, leftMargin=LM, rightMargin=LM, topMargin=LM, bottomMargin=LM)
tdoc.addPageTemplates([PageTemplate(id="land", frames=[Frame(LM, LM, LW, LPAGE[1] - 2 * LM, id="tf")])])

def _mods_str(m):
    if m["end"]: return "Battle ends"
    if m["no_combat"]: return "No combat"
    sgn = lambda x: ("+" if x > 0 else "−") + str(abs(x))
    parts = []
    if m["I"]:  parts.append(sgn(m["I"]) + " I")
    if m["TH"]: parts.append(sgn(m["TH"]) + " H")
    if m["TS"]: parts.append(sgn(m["TS"]) + " S")
    return "  ".join(parts) if parts else "—"

_ABBR = {"Scout": "Scout", "Ambush": "Ambush", "Flank": "Flank", "Charge": "Charge",
         "Fighting Formation": "Fight.<br/>Form.", "Defensive Formation": "Def.<br/>Form.",
         "Fall Back": "Fall<br/>Back"}
_tac = rc.TACTICS
_hst = ParagraphStyle("th", fontName="EBGaramond-Bold", fontSize=7.6, leading=8.4, alignment=1, textColor=white)
_cst = ParagraphStyle("tcell", fontName="EBGaramond", fontSize=7.6, leading=8.8, alignment=1, textColor=ink)
_rst = ParagraphStyle("trow", fontName="EBGaramond-Bold", fontSize=8, leading=9, textColor=ink)
_corner = Paragraph("You ↓ &nbsp; Foe →", ParagraphStyle("cn", fontName="EBGaramond-BoldItalic", fontSize=7.2, leading=8, alignment=1, textColor=white))
_data = [[_corner] + [Paragraph(_ABBR[t], _hst) for t in _tac]]
for rt in _tac:
    _row = [Paragraph(rt, _rst)]
    for ct in _tac:
        _row.append(Paragraph(_mods_str(rc.TACTIC_MATRIX[(rt, ct)][0]), _cst))
    _data.append(_row)
_lw = LW * 0.135
_cw = (LW - _lw) / 7
_tt = Table(_data, colWidths=[_lw] + [_cw] * 7, repeatRows=1)
_tsty = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (1, 0), (-1, -1), "CENTER"),
         ("GRID", (0, 0), (-1, -1), 0.5, rule),
         ("ROWBACKGROUNDS", (1, 1), (-1, -1), [white, zebra]),
         ("BACKGROUND", (0, 0), (-1, 0), D_CUN),
         ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#e8e8e8")),
         ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
         ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
for _i in range(len(_tac)):
    _tsty.append(("BACKGROUND", (_i + 1, _i + 1), (_i + 1, _i + 1), colors.HexColor("#efe9dd")))
_tt.setStyle(TableStyle(_tsty))
tstory = [P("TACTIC MATRIX", "h1"),
          P("Both players pick a Tactic in secret each Skirmish (Battle step 2), then reveal together. "
            "Find <b>your</b> Tactic down the left and your <b>opponent's</b> across the top — the cell shows the modifiers "
            "<b>you</b> gain that Skirmish. Your opponent reads their own row for theirs.", "sub"),
          P("<b>I</b> = Initiative &nbsp;&nbsp; <b>H</b> = to-Strike (easier to hit) &nbsp;&nbsp; <b>S</b> = Save (harder to be killed). "
            "&nbsp; + helps you, − hurts you. &nbsp; <b>Battle ends</b> = the fight breaks off this Skirmish; "
            "<b>No combat</b> = both Flank — no engagement, but Endurance is still spent.", "bsm"),
          Spacer(1, 6), _tt]
tdoc.build(tstory)

# ════════════════════ MERGE: portrait body, then build-paths, then board, then tactics LAST ════════════════════
main = PdfReader("main.pdf"); board = PdfReader("board.pdf"); tactics = PdfReader("tactics.pdf")
tree = PdfReader("talent_tree_2x2.pdf") if _HAVE_TREE else None
out = PdfWriter()
for pg in main.pages:                 # rules, armory, buildings, enablers + glossary
    out.add_page(pg)
if _HAVE_TREE and tree:
    out.add_page(tree.pages[0])        # talent tree (landscape, one sheet)
out.add_page(board.pages[0])           # domain boards (landscape)
out.add_page(tactics.pages[0])         # tactic matrix (landscape) — LAST PAGE
with open("ESCALATION_CAMPAIGN.pdf", "wb") as f:
    out.write(f)
print("pages:", len(PdfReader("ESCALATION_CAMPAIGN.pdf").pages),
      "| tree page:", (1 if _HAVE_TREE and tree else 0), "| board pages:", len(board.pages))