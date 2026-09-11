"""Generate renown_data_d10.py from renown_data_CE.py.

- Inserts a DICE constants block; every die-dependent literal becomes an f-string.
- Plugs the agreed d10 numbers for retinues, armor, shields, Recover, Parry.
- Leaves ALL weapon/ranged AP untouched (Gage is dialing those in manually).
Every replacement is asserted, so a miss fails loudly instead of silently skipping.
"""
import re, sys

SRC = "renown_data_CE.py"
DST = "renown_data_d10.py"
s = open(SRC, encoding="utf-8").read()
hits = []


def rep(old, new, n=1, label=""):
    global s
    c = s.count(old)
    assert c == n, f"[{label}] expected {n} occurrence(s), found {c}: {old[:70]!r}"
    s = s.replace(old, new)
    hits.append(label or old[:40])


# ── 1. DICE constants block ──────────────────────────────────────────────────
DICE = '''VERSION = "0.4.9.8-d10"

# ── DICE ─────────────────────────────────────────────────────────────────────
# Single source for die size. Every threshold string below is an f-string built
# from these, so changing FACES rewrites the rules text with it.
FACES            = 10   # die size for every combat roll
FOCUSED_THR      = 10   # Focused fires on this natural result or higher (FACES = nat-max only, FACES-1 = top two)
ROUT_THR         = FACES + 1   # a modified Morale target this high or worse Routs
CAP_THR          = FACES       # the old "6+" ceiling: worst printable target
AUTO_PASS_FLOOR  = 2           # a target modified below this auto-passes (set None to delete the rule)
BLUNDER_THR      = FACES       # Blunder sets to-Strike to this
PARRY_BASE       = 8           # base Parry target
FATIGUE_STRIKE   = 2           # per-token penalty to Strike (magnitude)
FATIGUE_MORALE   = 2           # per-token penalty to Morale (magnitude)
'''
rep('VERSION = "0.4.9.8"', DICE.rstrip(), 1, "DICE block")

# ── 2. Keyword-constant comments ─────────────────────────────────────────────
rep('# Recover still gets a 6+ save while Fatigued',
    '# Recover still gets a CAP_THR+ save while Fatigued', 1, "ENDURING comment")
rep('# Parry survives Fatigue: degrades to 6+ but is never disabled.',
    '# Parry survives Fatigue: degrades to CAP_THR+ but is never disabled.', 1, "FLORENTINE comment")

# ── 3. GLOSSARY combat entries → f-strings ───────────────────────────────────
rep('BLUNDER:        "At Initiative -2 or lower, your to-Strike is set to 6+, before other negative modifiers.",',
    'BLUNDER:        f"At Initiative -2 or lower, your to-Strike is set to {BLUNDER_THR}+, before other negative modifiers.",',
    1, "BLUNDER")

rep('PARRY:          "While not Fatigued, roll a d6 to attempt to Parry a Strike before the Save. On a 5+, the Strike is Parried.",',
    'PARRY:          f"While not Fatigued, roll a D{FACES} to attempt to Parry a Strike before the Save. On a {PARRY_BASE}+, the Strike is Parried.",',
    1, "PARRY")

rep('RECOVER:        "While not Fatigued, if a to-Save roll fails, roll a d6: a result of X+ Recovers the retinue.",',
    'RECOVER:        f"While not Fatigued, if a to-Save roll fails, roll a D{FACES}: a result of X+ Recovers the retinue.",',
    1, "RECOVER")

rep('FATIGUE_TOKEN:  "Each token is -1 to your Strike to a maximum of 6+; and Morale -1 (uncapped). If your modified Morale is ever 7+, your army Routs. These effects are cumulative.",',
    'FATIGUE_TOKEN:  f"Each token is -{FATIGUE_STRIKE} to your Strike to a maximum of {CAP_THR}+; and Morale -{FATIGUE_MORALE} (uncapped). If your modified Morale is ever {ROUT_THR}+, your army Routs. These effects are cumulative.",',
    1, "FATIGUE_TOKEN (early)")

rep('MINUS_1_TBH:    "A cumulative -1 penalty to the Strike roll (to a maximum of 6+). Sources: a shield\'s -1 to Strike.",',
    'MINUS_1_TBH:    f"A cumulative -1 penalty to the Strike roll (to a maximum of {CAP_THR}+). Sources: a shield\'s -1 to Strike.",',
    1, "MINUS_1_TBH")

rep("NEGATE_TEMPERED: \"Ignores Tempered: this weapon's AP can reduce the target's Save past 6+ (to auto-fail), defeating the Tempered floor.\",",
    "NEGATE_TEMPERED: f\"Ignores Tempered: this weapon's AP can reduce the target's Save past {CAP_THR}+ (to auto-fail), defeating the Tempered floor.\",",
    1, "NEGATE_TEMPERED")

rep("NEGATE_RIPOSTE: \"The target's Parry can never Riposte this weapon's Strikes (a natural 6 Parry still cancels the Strike, but no counter-Strike follows).\",",
    "NEGATE_RIPOSTE: f\"The target's Parry can never Riposte this weapon's Strikes (a natural {FOCUSED_THR} Parry still cancels the Strike, but no counter-Strike follows).\",",
    1, "NEGATE_RIPOSTE")

rep('"Morale":        "How steady a retinue is when tested (lower is steadier; see the retinue table). Break and Panic checks roll it: a D6 per retinue in the field, up to 5 dice, each must meet its modified value; failures are casualties. If the modified value is ever 7+, the army Routs.",',
    '"Morale":        f"How steady a retinue is when tested (lower is steadier; see the retinue table). Break and Panic checks roll it: a D{FACES} per retinue in the field, up to 5 dice, each must meet its modified value; failures are casualties. If the modified value is ever {ROUT_THR}+, the army Routs.",',
    1, "Morale")

rep('"Strike":        "A landed hit. Roll a D6, apply modifiers to the roll, and Strike on a result >= the to-Strike number. The target may then Parry, Save, and Recover.",',
    '"Strike":        f"A landed hit. Roll a D{FACES}, apply modifiers to the roll, and Strike on a result >= the to-Strike number. The target may then Parry, Save, and Recover.",',
    1, "Strike")

rep('"to-Strike number": "The D6 result a retinue needs to Strike (see the retinue table; lower is better). Bonuses add to the roll; penalties and Fatigue tokens subtract.",',
    '"to-Strike number": f"The D{FACES} result a retinue needs to Strike (see the retinue table; lower is better). Bonuses add to the roll; penalties and Fatigue tokens subtract.",',
    1, "to-Strike number")

rep('"Save":          "The defender\'s roll to avoid a casualty: roll a D6, add the weapon\'s AP (a negative) and the shield\'s Save bonus (a positive); the hit is saved on a result >= the armor value.",',
    '"Save":          f"The defender\'s roll to avoid a casualty: roll a D{FACES}, add the weapon\'s AP (a negative) and the shield\'s Save bonus (a positive); the hit is saved on a result >= the armor value.",',
    1, "Save")

# ── 4. Pivotal / Focused ─────────────────────────────────────────────────────
rep('# ── Pivotal: one word for "a natural 6" across all combat effects',
    '# ── Pivotal: one word for "a natural FOCUSED_THR" across all combat effects', 1, "Pivotal comment")
rep('PIVOTAL:        "A natural 6, before modifiers.",',
    'PIVOTAL:        f"A natural {FOCUSED_THR}, before modifiers." if FOCUSED_THR == FACES else f"A natural {FOCUSED_THR} or higher, before modifiers.",',
    1, "PIVOTAL def")

rep('FATIGUE_TOKEN:  "Each token is -1 to your Strike (to a maximum of 6+) and Morale -1 (uncapped); if your modified Morale is ever 7+, your army Routs. Tokens stack. While Fatigued, retinues cannot Parry or Recover.",',
    'FATIGUE_TOKEN:  f"Each token is -{FATIGUE_STRIKE} to your Strike (to a maximum of {CAP_THR}+) and Morale -{FATIGUE_MORALE} (uncapped); if your modified Morale is ever {ROUT_THR}+, your army Routs. Tokens stack. While Fatigued, retinues cannot Parry or Recover.",',
    1, "FATIGUE_TOKEN (override)")

# ── 5. MORALE_GLOSSARY working notes ─────────────────────────────────────────
rep("Fatigue token; failures are casualties. Target 7+ is unmakeable = Rout.",
    "Fatigue token; failures are casualties. Target ROUT_THR+ is unmakeable = Rout.", 1, "morale note 1")
rep("\"break casualties. BUT still Routs if the morale target climbs to 7+ from \"",
    "\"break casualties. BUT still Routs if the morale target climbs to ROUT_THR+ from \"", 1, "morale note 2")
rep("\"Caps the morale target at 6 permanently.", "\"Caps the morale target at CAP_THR permanently.", 1, "morale note 3")
rep("\"check each Skirmish (keeps bleeding casualties at a 6+ roll), but the target \"",
    "\"check each Skirmish (keeps bleeding casualties at a CAP_THR+ roll), but the target \"", 1, "morale note 4")
rep("can never reach 7, so it NEVER Routs.", "can never reach ROUT_THR, so it NEVER Routs.", 1, "morale note 5")

# ── 6. Node / faction cap clauses ────────────────────────────────────────────
rep('"mastery": f"{PLANISHING}: Your to-Save can\'t be reduced beyond 6+. Craft +1",',
    '"mastery": f"{PLANISHING}: Your to-Save can\'t be reduced beyond {CAP_THR}+. Craft +1",', 1, "Gilded Foundry")
rep('"mastery": "Enduring: while Fatigued, your Recover rolls can\'t be reduced beyond 6+.",',
    '"mastery": f"Enduring: while Fatigued, your Recover rolls can\'t be reduced beyond {CAP_THR}+.",', 1, "Hospitaller")
rep('**Florentine** (while Fatigued, may Parry on a natural 6).',
    '**Florentine** (while Fatigued, may Parry on a natural {FOCUSED_THR}).', 1, "Tiltyard")
rep("'mechanic': \"Martyrdom: Your Armies' Morale can't be modified beyond 6+, but still suffer \u22121 per Fatigue Token.",
    "'mechanic': f\"Martyrdom: Your Armies' Morale can't be modified beyond {CAP_THR}+, but still suffer \u2212{FATIGUE_MORALE} per Fatigue Token.",
    1, "Undying Flame")

# ── 7. Bandit tactics — fixes the unreachable "d6, 7 = Fall Back" bug ────────
rep('another player rolls bandit tactics (d6, 7 = Fall Back)',
    'another player rolls bandit tactics (D{FACES}; a Focused result = Fall Back)', 1, "bandit tactics bug")

# ── 8. RETINUES ──────────────────────────────────────────────────────────────
for name, th, sh in [("Levy", 6, 8), ("Man-at-Arms", 5, 7), ("Sergeant", 3, 6), ("Knight Templar", 4, 5)]:
    m = re.search(rf'("{re.escape(name)}":\s*\{{[^}}]*?)"to_hit": (\d+)(.*?)"shaking": (\d+)', s, re.S)
    assert m, f"retinue {name} not found"
    s = s[:m.start()] + f'{m.group(1)}"to_hit": {th}{m.group(3)}"shaking": {sh}' + s[m.end():]
    hits.append(f"retinue {name}")

# ── 9. SHIELDS ───────────────────────────────────────────────────────────────
rep('"Targe Shield":  {"save_bonus": 0,', '"Targe Shield":  {"save_bonus": 1,', 1, "Targe +1")
rep('"Kite Shield":   {"save_bonus": 1,', '"Kite Shield":   {"save_bonus": 2,', 1, "Kite +2")
rep('"Tower Shield":  {"save_bonus": 2,', '"Tower Shield":  {"save_bonus": 2,', 1, "Tower +2 (unchanged)")
rep('"Heater Shield": {"save_bonus": 2,', '"Heater Shield": {"save_bonus": 3,', 1, "Heater +3")

# ── 10. ARMORS (+ Gambeson at Crude) ─────────────────────────────────────────
rep('''ARMORS = {
    "Cloth":       {"save": 7, "tier": "Crude",   "tags": []},
    "Leather":     {"save": 5, "tier": "Cast",    "tags": []},
    "Chainmail":   {"save": 4, "tier": "Wrought", "tags": []},
    "Full Plate":  {"save": 3, "tier": "Forged",  "tags": []},
    "Gothic Plate":{"save": 2, "tier": "Crafted", "tags": ["Immune Unwieldy"]},
}''',
    '''ARMORS = {
    "Cloth":       {"save": 10, "tier": "Crude",   "tags": []},
    "Gambeson":    {"save":  8, "tier": "Crude",   "tags": []},
    "Leather":     {"save":  7, "tier": "Cast",    "tags": []},
    "Chainmail":   {"save":  6, "tier": "Wrought", "tags": []},
    "Full Plate":  {"save":  4, "tier": "Forged",  "tags": []},
    "Gothic Plate":{"save":  3, "tier": "Crafted", "tags": ["Immune Unwieldy"]},
}''', 1, "ARMORS + Gambeson")

# ── 11. Recover ladder 6/5/4 → 10/9/8 ────────────────────────────────────────
for old, new, n in [('"Recover 6"', '"Recover 10"', 2), ('"Recover 5"', '"Recover 9"', 2),
                    ('"Recover 4"', '"Recover 8"', 1), ('Recover 4+', 'Recover 8+', 1),
                    ('"Gain Recover 6, or improve Recover by +1."', '"Gain Recover 10, or improve Recover by +1."', 1)]:
    c = s.count(old)
    assert c == n, f"[Recover] {old} expected {n}, found {c}"
    s = s.replace(old, new)
    hits.append(f"Recover {old}->{new}")

open(DST, "w", encoding="utf-8").write(s)
print(f"wrote {DST}  ({len(hits)} edits)")
for h in hits:
    print("  -", h)
