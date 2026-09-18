# renown_data — single source of truth (CSV/0.4.8 branch, card-verified)
# Edit THIS file; equipment.csv, cards, and docs are generated from it.
VERSION = "0.4.9.9-d10"

# ── DICE ─────────────────────────────────────────────────────────────────────
# Single source for die size, shared with the combat engines. Every threshold
# string below is an f-string built from these, so changing the die rewrites the
# rules text with it. Values come from dice_config (CE/combatv4) when it is
# importable, so the data file and the engines can never disagree; the fallbacks
# only apply when this file is imported standalone for doc/card generation.
try:
    from dice_config import (FACES, FOCUSED_THR, ROUT_THR, CAP_THR,
                             AUTO_PASS_FLOOR, FATIGUE_STRIKE, FATIGUE_MORALE,
                             PARRY_BASE, RECOVER_BASE, DEADLY_AP, DEADLY_MODE,
                             UNSTOPPABLE_MOD, IMPROVED_PARRY_MOD, SOURCE as DICE_SOURCE)
except ImportError:  # standalone (build_wiki, gen_compendium, card sheets, ...)
    FACES            = 10
    FOCUSED_THR      = FACES
    ROUT_THR         = FACES + 1
    CAP_THR          = FACES
    AUTO_PASS_FLOOR  = 2
    FATIGUE_STRIKE   = 2
    FATIGUE_MORALE   = 2
    PARRY_BASE       = 8
    RECOVER_BASE     = 8
    DEADLY_AP        = 5
    DEADLY_MODE      = "additional"
    UNSTOPPABLE_MOD  = 2
    IMPROVED_PARRY_MOD = 1
    DICE_SOURCE      = "renown_data fallback"

BLUNDER_THR = CAP_THR   # Blunder sets to-Strike to the worst printable target
DICE_PROVENANCE = (f"d{FACES} | Focused {FOCUSED_THR}+ | Parry {PARRY_BASE}+ | "
                   f"Recover {RECOVER_BASE}+ | src {DICE_SOURCE}")
# ── Keyword constants ─────────────────────────────────────────────────────
# Rename a keyword here and it renames everywhere (GLOSSARY keys, tags, cards).

STEADY          = "Steady"
UNWIELDY        = "Unwieldy"
TWO_H           = "2H"
SHATTER_ARMOR   = "Deadly"
UNSTOPPABLE     = "Unstoppable"
CLEAVE          = "Cleave"
POISON          = "Poison"
NIMBLE          = "Nimble"
DRILLED         = "Drilled"
DESTROY_SHIELD  = "Destroy Shield"
BLUNDER         = "Blunder"
ONE_SHOT        = "One-Shot"
DEFLECT         = "Deflect"
IMMUNE_PANIC    = "Immune Panic"
UNBREAKABLE     = "Unbreakable"
PARRY           = "Parry"
RIPOSTE         = "Riposte"
NO_PARRY        = "Awkward"
RECOVER         = "Recover"
SERRATED        = "Serrated"
ENDURING        = "Enduring"   # Recover still gets a CAP_THR+ save while Fatigued (exception to off-when-fatigued)
STRAIN          = "Strain"
MINUS_1_TBH     = "Shielded"
PLANISHING      = "Planishing"
FATIGUE_TOKEN   = "Fatigue Token"
CRUSADER        = "Zealous"

IMMUNE = "Immune"
def immune(keyword):
    """Immunity to a keyword, referencing the canonical name so renames
    propagate. immune(DESTROY_SHIELD) -> 'Immune Destroy Shield'."""
    return f"{IMMUNE} {keyword}"
	
NEGATE = "Negate"
def negate(keyword):
    """Offensive cancel of an enemy keyword, referencing the canonical name so renames
    propagate. negate(MINUS_1_TBH) -> 'Negate Shielded'."""
    return f"{NEGATE} {keyword}"

# convenience aliases for the immunities currently in use
IMMUNE_DESTROY_SHIELD = immune(DESTROY_SHIELD)
IMMUNE_UNWIELDY       = immune(UNWIELDY)
IMMUNE_STRAIN         = immune(STRAIN)
# Negate family (offensive — cancel an enemy keyword) + atomic penalty/bundle terms
NEGATE_UNSTOPPABLE = "Immune Unstoppable"

NEGATE_TEMPERED    = f"Negate {PLANISHING}"
NEGATE_RIPOSTE     = "Negate Riposte"
NEGATE_SHIELDED    = negate(MINUS_1_TBH)   # "Negate Shielded": attacker ignores defender's Shielded (-1 to Strike)
MINUS_1_PARRY      = "-1 to Parry"
HALFSWORD          = "Halfsword"   # RESERVED — engine path intact, no weapon carries it (shelved)
DUAL_WIELD         = "Dual Wield"
FLORENTINE         = "Florentine"  # Parry survives Fatigue: degrades to CAP_THR+ but is never disabled. Grants Parry. Only active while Dual Wielding.
PIVOTAL = "Focused"


GLOSSARY = {
    STEADY:         "Initiative cannot be reduced by Tactics.",
    UNWIELDY:       "Initiative cannot be improved by Tactics.",
    TWO_H:          "Cannot use a Shield.",
    SHATTER_ARMOR:  f"On a {PIVOTAL} Strike: that strike's AP is increased by {DEADLY_AP}, and the defender may Parry or {RECOVER} only with a {PIVOTAL} roll.",
    UNSTOPPABLE:    f"-{UNSTOPPABLE_MOD} to the defender's Parry roll, to a maximum of {CAP_THR}+).",
    CLEAVE:         f"On a {PIVOTAL} Strike: roll one extra Strike die at your modified to-Strike.",
    POISON:         f"When the Defender receives a Strike and rolls a {PIVOTAL} Save, it fails; the resulting wound may only be {RECOVER}ed with a {PIVOTAL} {RECOVER}.",
    NIMBLE:         "Gain +1 Initiative in the first Skirmish of each Battle.",
    DRILLED:        "Does not lose Endurance in the first Skirmish of each Battle.",
    DESTROY_SHIELD: f"On a {PIVOTAL} Strike: the target loses its Shield attributes for the rest of the Battle.",
    BLUNDER:        f"At Initiative -2, your to-Strike is set to {BLUNDER_THR}+, before other negative modifiers.",
    ONE_SHOT:       "May only be Equipped in the first Skirmish of a Battle. Requires a Tiltyard.",
    #DEFLECT:        "-1 to Parry and Negate Riposte against this weapon's Strikes. (All Ranged weapons have Deflect.)",
    #IMMUNE_PANIC:   "Automatically passes Panic checks.",
    #UNBREAKABLE:    "Immune Break: does not take Break checks while Fatigued.",
    PARRY:          f"While not Fatigued, roll a D{FACES} to attempt to Parry a Strike before an Armor Save. On a {PARRY_BASE}+ (Improved by Improved Parry), the Strike is Parried and has no further effect.",
    RIPOSTE:        "While not Fatigued, if you Focused a Parry against a Melee Weapon's Strike, you Riposte: your opponent immediately takes a Strike from your melee weapon. You can Riposte a Riposte.",
    NO_PARRY:       "While equipped with this weapon during a skirmish, you cannot Parry, and so cannot Riposte.",
    RECOVER:        f"While not Fatigued, if a to-Save roll fails, roll a D{FACES} & compare it to your Recover value: a result greater than or equal to your Recover value recovers the retinue.",
    SERRATED:       "A cumulative -2 penalty to the defender's Recover roll.",
    PLANISHING:     f"A {PIVOTAL} Save succeeds, regardless of AP.",
    FATIGUE_TOKEN:  f"Each token is -{FATIGUE_STRIKE} to your Strike to a maximum of {CAP_THR}+; and Morale -{FATIGUE_MORALE} (uncapped). If your modified Morale is ever {ROUT_THR}+, your army Routs. These effects are cumulative.",
    MINUS_1_TBH:    f"A cumulative -1 penalty to the Strike roll (to a maximum of {CAP_THR}+). Sources: a shield's -1 to Strike.",
	#NEGATE_UNSTOPPABLE: "Cancels the attacker's Parry from Unstoppable: this shield's -1 to Strike still applies, and the attacker's -1 to Parry does not.",
    NEGATE_TEMPERED: f"Ignores {PLANISHING}: this weapon's AP can reduce the target's Save beyond {CAP_THR}+ (to auto-fail).",
    NEGATE_RIPOSTE: f"The target's Parry can never Riposte this weapon's Strikes (a natural {FOCUSED_THR} Parry still cancels the Strike, but no counter-Strike follows).",
    #MINUS_1_PARRY: "A stacking -1 penalty to the defender's Parry roll (to a maximum of 6+). Sources: Unstoppable, Deflect, and each Fatigue token.",
    DUAL_WIELD: "A failed Strike is rerolled once; the rerolled Strike can be Focused. Dual Wield confers Two-Handed. You cannot reroll successful Strikes.",
    FLORENTINE: "Only active while Dual Wielding. Even while Fatigued, a Focused Parry succeeds. This alone does not enable Riposte while Fatigued.",
    "Immune [keyword]": "Cancels that keyword as it applies to you (e.g. Immune Unwieldy, Strain, Destroy Shield).",

    # ── Combat keywords ported from the Escalation Campaign glossary ──
    "AP":            "Armor Penetration — a weapon's (negative) modifier to the defender's Save roll; the more negative, the harder to save.",
    "Blocked":       "-1 Initiative in the first Skirmish (negated by Immune Blocked).",
    "Strained":      "-1 Initiative every Skirmish (negated by Immune Strain). Does not gain Endurance in the Empire Phase.",
    #"Improved Parry": "Your Parry succeeds on 4+ instead of 5+.",
    #"Heal X":        "At the end of each Skirmish, for every X casualties you took from Strikes, return 1 retinue to your Army.",
    "Seize the Initiative": "Won by the roll-off at the start of the Battle — the winner of their last Battle adds +1 to the roll. You become the Attacker and gain +1 Initiative in the first Skirmish. Some Tactics and the Ministry monument also grant it.",

    # ── Battle-structure terms (doc glossary, wording updated to current rules) ──
    "Attacker / Defender": "Set by the roll-off. Each Skirmish the Attacker declares equipment first; the Defender then responds.",
    "Battle":        "One fight between two players, resolved as a series of Skirmishes until a side is wiped out, Routs, or Falls Back.",
    "Skirmish":      "One round of a Battle, run through the numbered Battle steps; a Battle repeats Skirmishes until it ends.",
    "Casualty":      "A retinue removed from the field — from an unsaved Strike or a failed Panic or Break check.",
    "Field":         "Your retinues in play — front line (up to 10) plus reserve (up to 5). Casualties leave the field at once, lowering its count.",
    "Endurance":     "A side's stamina. Each side that fights loses 1 per Skirmish; at 0 it becomes Fatigued.",
    "Fatigued":      f"A side at 0 Endurance. Each Skirmish its field takes a Break check, then it gains a Fatigue token. Fatigued Armies cannot {PARRY}, {RIPOSTE}, or {RECOVER}",
    "Break check":   "Taken by each Fatigued side's field every Skirmish, just before it gains its Fatigue token. Roll Morale (up to 5 dice, modified by Fatigue tokens); failures are casualties, but a Break check never triggers a Panic check. Unbreakable auto-passes.",
    "Panic check":   "Taken at most once per Skirmish by a side that suffered more than 5 casualties in that Skirmish, after it Strikes back. Roll Morale (up to 5 dice); Immune Panic auto-passes.",
    "Morale":        f"How steady a retinue is when tested (lower is steadier; see the retinue table). Break and Panic checks roll it: a D{FACES} per retinue in the field, up to 5 dice, each must meet its modified value; failures are casualties. If the modified value is ever {ROUT_THR}+, the army Routs.",
    "Rout":          f"The army breaks and leaves the Battle (you lose it). Whenever an army's modified Morale value reaches {ROUT_THR}+ or more, it Routs automatically.",
    "Fall Back":     "A controlled retreat that ends the Battle with at least one retinue left — a partial success.",
    "Strike":        f"A landed hit. Roll a D{FACES}, apply modifiers to the roll, and Strike on a result >= the to-Strike number. The target may then Parry, Save, and Recover.",
    "to-Strike number": f"The D{FACES} result a retinue needs to Strike (see the retinue table; lower is better). Bonuses add to the roll; penalties and Fatigue tokens subtract.",
    "Save":          f"The defender's roll to avoid a casualty: roll a D{FACES}, add the weapon's AP (a negative) and the shield's Save bonus (a positive); the hit is saved on a result >= the armor value.",
    "Natural roll":  "The number on the die before any modifiers. Modifiers never change what counts as 'natural'.",
    "Initiative":    "Decides who Strikes first each Skirmish (higher first). Runs -2 to +2 (Ministry can raise the maximum to +3). At -2 or lower you Blunder.",
    "Tactic":        "A choice both players make secretly and reveal together each Skirmish; it can shift Initiative, Strike, and Save rolls.",
    "Dual-equip":    "Carry two weapons at once (e.g. melee + ranged). Granted by the Tiltyard, which also gives Unwieldy until its mastery removes it.",
    "Edict":         "A scoring achievement: reach a Sovereign Standing, or complete a Monument.",
    "Monument":      "A Domain's capstone Pursuit. Completing one scores its Edict and grants a powerful effect.",

    # ── Empire keywords (referenced by Pursuits/Factions; DRAFTED — review wording) ──
    "Faith X":       "Gain X Faith: each Faith raises your Public Order track by 1 when resolved.",
    "Doubt X":       "Gain X Doubt: each Doubt lowers your Public Order track by 1 when resolved.",
    "Extort X":      "Take X from the stated source: the gold goes to you instead of its owner.",
    "Recoup":        "Regain the stated cost in gold after paying it.",
    "Speed":         "An Army's movement allowance in Territories per Move action. Base Speed value of an army is Speed 2",

    # ── Council, Influence & Envoys (from Rules; the political loop) ──
    "Influence":     "The political currency of voting. Spend it to Support or Oppose Envoys. You gain it each turn from your Era, innate modifiers (trade partners, alliances, war), Pursuits, and Infrastructure.",
    "Influence X":   "An automatic +X (or -X) to an Envoy's net Influence from a Pursuit, Infrastructure, or Faction.",
    "Envoy":         "The currency of actions: send an Envoy to perform an action during the Envoy Phase. Council Envoys act on the voted Domain; Personal Envoys are sent by Era progression.",
    "Vote":          "On each Envoy, every player in clockwise order from the starting player must Support, Oppose, or Abstain.",
    "Support X":     "Spend X Influence to increase an Envoy's net Influence.",
    "Oppose X":      "Spend X Influence to decrease an Envoy's net Influence.",
    "Abstain":       "Decline to spend Influence on a vote.",
    "Net Influence": "The sum of an Envoy's starting Influence (1+ by Standing) and all Support, Oppose, and Influence X. The total sets the outcome: -3 or less Condemned, 0 or less Failed (gain Doubt +1), 1+ passes.",
    "Endorsed":      "An Envoy that passes with 3+ net Influence, triggering its endorsed effect (and a Domain's Rising/Established/Sovereign endorsement).",
    "Condemned":     "An Envoy whose net Influence is -3 or less: it fails and you resolve that Domain's Condemn effect.",
    "Council Phase": "Before Personal Envoys, all players vote on a Domain (clockwise; Host breaks ties). Each then sends a free Council Envoy of that Domain. Council Envoys auto-Abstain and their net Influence cannot drop below 1.",
    "Council Envoy": "A free Envoy resolved in the Council Phase on the voted Domain; auto-Abstained, net Influence floored at 1.",
    "Personal Envoy": "An Envoy you send in the Envoy Phase to perform an action; count and reach scale with Era.",
	"Envoy Outcome": "How a Sent Envoy resolves, by Net Influence: Condemned (<= -3), "
                    "Failed (-3 < Net <= 0, gain Doubt 1), Passed (>= 1), Endorsed (>= 3). The per-domain "
                    "effect at each band is given by the Envoy Outcome Table; an action's own endorsed bonus overrides "
                    "the domain default.",

    # ── Empire actions ──
    "Charter":       "Found or upgrade a Settlement (Industry action).",
    "Muster":        "Raise retinues into an Army, up to a Settlement's muster limit (Industry/Prowess).",
    "Pursue":        "Build a Pursuit, spending its purchase cost and a Settlement ward (Industry).",
    "Build":         "Construct Infrastructure (Industry action).",
    "Repair":        "Restore damaged Infrastructure or Settlements (Industry).",
    "Move":          "Advance an Army up to its Speed in Territories (Prowess).",
    "Demand Tribute": "Coerce gold or concessions from another player (Prowess).",

    # ── Diplomacy & alliances ──
    "Diplomacy":     "Free Envoy actions for forming and ending Treaties and Trade Agreements; resolved before Domain Envoys.",
    "Treaty":        "A standing agreement between players (e.g. Trade Agreement, Non-Aggression, Alliance) signed via Diplomacy.",
    "Alliance":      "A Treaty binding players to mutual support; Military and Defensive Alliances unlock by Era.",
    "Vassal":        "A player subordinated via Vassalization: their chartered settlements return to them, they mirror the Suzerain's Treaties, count as allied to the Suzerain, and cannot perform or be targeted by Diplomacy actions.",
    "Suzerain":      "The player who has Vassalized another; the vassal mirrors their Treaties.",

    # ── Empire state ──
    "Renown":        "The shared progress track. Gain 1 per Rest Phase; thresholds raise your Era (Ascension 8, Eminence 18, Zenith 30).",
    "Domain":        "One of the four identities — Industry, Prowess, Cunning, Piety — raised by spending Domain points. Values 3/6/10 = Rising/Established/Sovereign Standing.",
    "Domain Point":  "Gain 1 per Rest Phase; spend to raise a Domain value by 1.",
    "Standing":      "Your tier in a Domain: Untested, Rising (3), Established (6), Sovereign (10). Sets max Influence per vote (1/2/3/4) and unlocks Domain effects.",
    "Public Order":  "A track from -5 to 10, adjusted each turn by Faith minus Doubt; its band applies cumulative effects (see the Public Order table).",
    "Reach":         "How far a Settlement projects control, in Territories (by tier). Calculated like Range X",
    "Edict":         "A scoring achievement / win path: reach a Sovereign Standing, complete a Monument, or fulfill a victory condition (Wonder, wealth, Vassalize, Living Saints, Last Standing).",

    # ── World ──
    "Bandit":        "Neutral hostile force; Bandit Camps spawn in Outlaw Country and on low Public Order.",
    "Outlaw Country": "Uncontrollable territories in your starting region where Bandit Camps spawn, starting at 3 and expanding if there is no room to place new Bandit Camps.",
    "Siege":         "Sieging a Settlement with an Army to capture it; does not increment in Winter.",
}

# ── Pivotal: one word for "a natural FOCUSED_THR" across all combat effects ─────────────
# Pure synonym — Pivotal carries no mechanics of its own; each keyword does the work.
# Swap the term anywhere by editing this one string. Must be defined before use;
# this .update() form can be pasted anywhere after GLOSSARY and the constants exist.


# ─────────────────────────────────────────────────────────────────────────────
# MORALE_GLOSSARY — personal working notes on the morale-immunity keyword family.
# NOT yet merged into GLOSSARY / cards / wiki: these are candidate Knight Templar
# abilities under test (only ONE will see final implementation). All are data-key
# driven: set e.g. {"unbreakable": True} on a retinue (one key only). None of them
# touch Immune Panic, which separately auto-passes the Panic check (>5 casualties).
#
# Background the four interact with:
#   Morale target = base `shaking` + Fatigue tokens - shake bonuses (e.g. Abbey +1).
#   Break check: each Fatigued side rolls every Skirmish (up to 5 dice) before its
#                Fatigue token; failures are casualties. Target ROUT_THR+ is unmakeable = Rout.
#   Panic check: a side that took >5 casualties this Skirmish rolls once after it
#                Strikes back. (Handled by Immune Panic, not by these four.)
# ─────────────────────────────────────────────────────────────────────────────
MORALE_GLOSSARY = {
    "Unbreakable": "Skips the Break check entirely while Fatigued: never rolls, never takes "
                   "break casualties. BUT still Routs if the morale target climbs to ROUT_THR+ from "
                   "accumulated Fatigue. Stands fully immune, then collapses all at once — and "
                   "because it stays full-size up to the Rout, it loses MORE soldiers when it "
                   "finally breaks than a unit that bled down gradually.",
    "Unshakable":  "Caps the morale target at CAP_THR permanently. Still TAKES every Break and Panic "
                   "check each Skirmish (keeps bleeding casualties at a CAP_THR+ roll), but the target "
                   "can never reach ROUT_THR, so it NEVER Routs. Bends and bleeds forever, never shatters. "
                   "Makes the `shaking` stat (and the Abbey bonus) irrelevant — it's capped regardless.",
    "Rally":       "Auto-passes the FIRST Break check it is ever required to take in a battle "
                   "(no roll, no casualties, no Rout); every Break check after is normal. One free "
                   "crisis, then mortal. The only one of the four that keeps `shaking` a live dial — "
                   "so it's the one that synergizes with lowering KT base shaking and stacking Abbey +1.",
    "Zealot":      "Locks the morale target at base `shaking`, ignoring ALL modifiers: Fatigue "
                   "tokens don't raise it, shake bonuses (Abbey) don't lower it. Takes checks every "
                   "Skirmish at that fixed number, never escalates, never Routs. A fixed wall whose "
                   "strength is entirely its base stat. Unlike Unshakable (caps at 6), Zealot pins at "
                   "base — which can be better or worse than 6 — and deliberately ignores Abbey synergy.",
}



# ── Army / Skirmish structural constants ──────────────────────────────────────
# Caps that the rules prose previously hard-coded. Pull these via {{VAL:...}} so
# the rulebook can never drift from canon.
ARMY_MAX_RETINUES   = 25   # maximum retinues a single Army may hold
FRONT_LINE_MAX      = 10   # retinues placed in the front line per Skirmish (one Strike die each)
RESERVE_MAX         = 5    # retinues held in reserve to replace front-line losses
MORALE_DICE_MAX     = 5    # max dice rolled on a Break or Panic check
PANIC_CASUALTY_THRESHOLD = 5  # take a Panic check if casualties this Skirmish exceed this
ENDURANCE_REGAIN    = 2    # +Endurance restored to non-Strained armies in the Empire Phase



RETINUES = {
    "Levy":           {"cost": 1000, "to_hit": 8, "endurance": 2, "shaking": 7, "unbreakable": False, "speed": 3, "max_size": ARMY_MAX_RETINUES},
    "Man-at-Arms":    {"cost": 2000, "to_hit": 5, "endurance": 3, "shaking": 6, "unbreakable": False, "speed": 3, "max_size": ARMY_MAX_RETINUES},
    "Sergeant":       {"cost": 2000, "to_hit": 3, "endurance": 2, "shaking": 5, "unbreakable": False, "speed": 3, "max_size": ARMY_MAX_RETINUES},
    "Knight Templar": {"cost": 2000, "to_hit": 4, "endurance": 2, "shaking": 4, "unbreakable": False, "speed": 3, "max_size": ARMY_MAX_RETINUES},
}

WEAPONS = {
    "Farm Tools":     {"ap":  0, "init":  0, "tier": "Crude",   "tags": [NO_PARRY]},
    "Cudgel":         {"ap": -1, "init": -1, "tier": "Crude",   "tags": [TWO_H, UNWIELDY, NO_PARRY]},
    "Pitchfork":      {"ap":  0, "init":  1, "tier": "Crude",   "tags": [TWO_H, UNWIELDY, NO_PARRY]},
    "Daggers":        {"ap":  0, "init":  1, "tier": "Cast",    "tags": [TWO_H, SHATTER_ARMOR]},
    "Short Sword":    {"ap":  0, "init":  0, "tier": "Cast",    "tags": [STEADY]},
    "Spears":         {"ap": -1, "init":  1, "tier": "Cast",    "tags": [UNWIELDY]},
    "Arming Sword":   {"ap": -1, "init":  0, "tier": "Wrought", "tags": [STEADY]},
    "Pike":           {"ap": -2, "init":  1, "tier": "Wrought", "tags": [TWO_H, STEADY, UNWIELDY, SHATTER_ARMOR, NO_PARRY]},
    "Flail":          {"ap": -1, "init":  0, "tier": "Wrought", "tags": [UNWIELDY, UNSTOPPABLE, CLEAVE, NO_PARRY], 'note': 'Cannot Dual Wield'},
    "Halberd":        {"ap": -3, "init":  0, "tier": "Wrought", "tags": [TWO_H, UNWIELDY]},
    "Battle Axe":     {"ap": -4, "init": -1, "tier": "Wrought", "tags": [TWO_H, UNWIELDY, UNSTOPPABLE, CLEAVE, NEGATE_SHIELDED]},
    "Cavalry Spear":  {"ap": -2, "init":  1, "tier": "Wrought", "tags": [STEADY, UNWIELDY, NEGATE_RIPOSTE, NO_PARRY], 'note': "Needs Stable; no Tower Shield or Dual Wield or Ranged Weapon; cannot Parry"},
    "Morningstar":    {"ap": -4, "init": -1, "tier": "Forged",  "tags": [CLEAVE, DESTROY_SHIELD], 'note': 'Cannot Dual Wield'},
    "Bastard Sword":  {"ap": -3, "init":  0, "tier": "Forged",  "tags": [STEADY], 'note': 'At the beginning of each equipment step, you may choose the 1H or 2H profile.'},
    "2HBastard":      {"ap": -3, "init":  0, "tier": "Forged",  "tags": [TWO_H, UNWIELDY, UNSTOPPABLE, CLEAVE]},
    "War Hammer":     {"ap":-10, "init": -1, "tier": "Forged",  "tags": [TWO_H, UNWIELDY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_RIPOSTE, DESTROY_SHIELD]},
    "Lance":          {"ap": -4, "init":  1, "tier": "Forged",  "tags": [STEADY, UNWIELDY, UNSTOPPABLE, NO_PARRY, NEGATE_RIPOSTE], 'note': "Needs Stable; no Tower Shield, Dual Wield, Ranged weapon, or Parry."},
    "Estoc":          {"ap": -3, "init":  1, "tier": "Crafted", "tags": [STEADY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_RIPOSTE, NEGATE_TEMPERED]},
    "Poleaxe":        {"ap": -6, "init":  0, "tier": "Crafted", "tags": [TWO_H, STEADY, CLEAVE, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_TEMPERED]},
}

RANGED = {
    "Hunting Bow": {"ap": -1, "init":  2, "tier": "Crude",   "tags": [TWO_H, UNSTOPPABLE, NEGATE_RIPOSTE]},
    "Longbow":     {"ap": -2, "init":  2, "tier": "Cast",    "tags": [TWO_H, UNSTOPPABLE, SHATTER_ARMOR, NEGATE_RIPOSTE]},
    "Javelin":     {"ap": -2, "init":  1, "tier": "Wrought", "tags": [STEADY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_RIPOSTE, DESTROY_SHIELD, ONE_SHOT], 'note': 'Cannot Dual Wield'},
    "Crossbow":    {"ap": -4, "init":  0, "tier": "Forged",  "tags": [UNWIELDY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_RIPOSTE], 'note': "Tower Shield only (no other shield), cannot Dual Wield"},
    "Arquebus":    {"ap": -7, "init":  2, "tier": "Crafted", "tags": [TWO_H, UNWIELDY, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_RIPOSTE, NEGATE_TEMPERED, NO_PARRY], 'note': "May only use the Fighting Formation or Fall Back Tactics.", 'requires': ["ABF", "Artillery Park"], 'tactics_allowed': ["Fighting Formation", "Fall Back"]},
    "Pilum":       {"ap": -5, "init":  1, "tier": "Crafted", "tags": [STEADY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_RIPOSTE, DESTROY_SHIELD, ONE_SHOT]},
}

SHIELDS = {
    None:            {"save_bonus": 0, "init":  0, "tier": None,     "tags": []},
    "Buckler Shield":{"save_bonus": 1, "init":  0, "tier": "Crude",  "tags": []},
    "Targe Shield":  {"save_bonus": 1, "init":  0, "tier": "Cast",   "tags": [UNWIELDY, MINUS_1_TBH]},
    "Kite Shield":   {"save_bonus": 1, "init":  0, "tier": "Wrought","tags": [STEADY, MINUS_1_TBH]},
    "Tower Shield":  {"save_bonus": 2, "init":  0, "tier": "Forged", "tags": [UNWIELDY, MINUS_1_TBH]},
    "Heater Shield": {"save_bonus": 2, "init":  0, "tier": "Crafted","tags": [MINUS_1_TBH, IMMUNE_DESTROY_SHIELD]},
}

ARMORS = {
    "Cloth":       {"save": 10, "tier": None,      "tags": []},
    "Gambeson":    {"save":  9, "tier": "Crude",   "tags": []},
    "Leather":     {"save":  8, "tier": "Cast",    "tags": []},
    "Chainmail":   {"save":  7, "tier": "Wrought", "tags": []},
    "Full Plate":  {"save":  6, "tier": "Forged",  "tags": []},
    "Gothic Plate":{"save":  5, "tier": "Crafted", "tags": []},
}

# ── Tier ladder ────────────────────────────────────────────────────────────
# Worst → best; each tier unlocked by the named Industry node.
TIERS = ["Crude", "Cast", "Wrought", "Forged", "Crafted"]
TIER_UNLOCK = {
    "Crude":   None,
    "Cast":    "Furnace",
    "Wrought": "Blacksmith",
    "Forged":  "Forge",
    "Crafted": "Advanced Blast Furnace",
}


# ── Domain Standing combat effects (Escalation) ───────────────────────────
# Standings: Rising = 3, Established = 6, Sovereign = 10 domain points.
STANDING_EFFECTS = {
    ("Prowess", "Established"): "Gain Parry.", #Remove "Parry"
    ("Piety",   "Established"): "Shake +1",
    ("Cunning", "Established"): "Opponent gains Blunder in the first Skirmish.", #Remove "Foes gain Blunder in first Skirmish"
    ("Cunning", "Sovereign"):   "Opponent gains Strain.", #Remove "Foes gain Strain"
}
	
# ── Tactics ────────────────────────────────────────────────────────────────
def _m(I=0, TH=0, TS=0, end=False, no_combat=False, endurance_loss=True, strain=False):
    return {"I": I, "TH": TH, "TS": TS,
            "end": end, "no_combat": no_combat, "endurance_loss": endurance_loss,
            "strain": strain}

# Tactic matrix transcribed verbatim from tactic_cards.pdf. Format is the card-holder's
# perspective: (A_tactic, B_tactic) -> (A's gains/penalties, B's gains/penalties).
# All values express the named side's own modifier (not opponent-relative).
# ============================================================================
# TACTIC MATRIX — SINGLE SOURCE OF TRUTH. Edit tactic interactions HERE.
# Format: (A_tactic, B_tactic) -> (A's modifier cell, B's modifier cell).
# Each cell is _m(I=, TH=, TS=, end=, no_combat=). All values are the named
# side's OWN modifier (lower TH/TS target = better). normalized_matrix.py just
# returns this dict — there is no second copy to drift from.
# ============================================================================
TACTIC_MATRIX = {
    # -- Scout --
    ("Scout", "Scout"):                            (_m(I=1), _m(I=1)),
    ("Scout", "Ambush"):                           (_m(I=1), _m(I=-1, TS=1)),
    ("Scout", "Flank"):                            (_m(I=-1, TS=1), _m(I=1)),
    ("Scout", "Charge"):                           (_m(I=1), _m(I=-1)),
    ("Scout", "Fighting Formation"):               (_m(TS=-1), _m(I=-1, TH=1)),
    ("Scout", "Defensive Formation"):              (_m(I=1), _m(I=-1, TS=1)),
    ("Scout", "Fall Back"):                        (_m(end=True), _m(end=True, strain=True)),
    # -- Ambush --
    ("Ambush", "Scout"):                           (_m(I=-1, TS=1), _m(I=1)),
    ("Ambush", "Ambush"):                          (_m(I=-1, TS=1), _m(I=-1, TS=1)),
    ("Ambush", "Flank"):                           (_m(I=1, TH=-1), _m(I=-1, TH=1)),
    ("Ambush", "Charge"):                          (_m(I=1, TH=1), _m(I=-1, TS=-1)),
    ("Ambush", "Fighting Formation"):              (_m(I=1, TS=1), _m(I=-1, TS=-1)),
    ("Ambush", "Defensive Formation"):             (_m(I=1), _m(TS=1, I=-1)),
    ("Ambush", "Fall Back"):                       (_m(end=True), _m(end=True, strain=True)),
    # -- Flank --
    ("Flank", "Scout"):                            (_m(I=1), _m(I=-1, TS=1)),
    ("Flank", "Ambush"):                           (_m(I=-1, TH=1), _m(I=1, TH=-1)),
    ("Flank", "Flank"):                            (_m(no_combat=True), _m(no_combat=True)),
    ("Flank", "Charge"):                           (_m(I=-1), _m(I=1)),
    ("Flank", "Fighting Formation"):               (_m(I=1, TH=1), _m(I=-1)),
    ("Flank", "Defensive Formation"):              (_m(I=1), _m(I=-1, TS=1)),
    ("Flank", "Fall Back"):                        (_m(I=-1), _m(I=1, TH=1)),
    # -- Charge --
    ("Charge", "Scout"):                           (_m(I=-1), _m(I=1)),
    ("Charge", "Ambush"):                          (_m(I=-1, TS=-1), _m(I=1, TH=1)),
    ("Charge", "Flank"):                           (_m(I=1), _m(I=-1)),
    ("Charge", "Charge"):                          (_m(TH=1), _m(TH=1)),
    ("Charge", "Fighting Formation"):              (_m(I=1, TH=-1), _m(I=-1, TH=1)),
    ("Charge", "Defensive Formation"):             (_m(TS=-1), _m(TH=1, TS=1)),
    ("Charge", "Fall Back"):                       (_m(I=1, TH=1), _m(I=-1)),
    # -- Fighting Formation --
    ("Fighting Formation", "Scout"):               (_m(I=-1, TH=1), _m(TS=-1)),
    ("Fighting Formation", "Ambush"):              (_m(I=-1, TS=-1), _m(I=1, TS=1)),
    ("Fighting Formation", "Flank"):               (_m(I=-1), _m(I=1, TH=1)),
    ("Fighting Formation", "Charge"):              (_m(I=-1, TH=1), _m(I=1, TH=-1)),
    ("Fighting Formation", "Fighting Formation"):  (_m(I=-1, TH=1), _m(I=-1, TH=1)),
    ("Fighting Formation", "Defensive Formation"): (_m(TH=1), _m(TS=1)),
    ("Fighting Formation", "Fall Back"):           (_m(TH=1), _m()),
    # -- Defensive Formation --
    ("Defensive Formation", "Scout"):              (_m(I=-1, TS=1), _m(I=1)),
    ("Defensive Formation", "Ambush"):             (_m(TS=1, I=-1), _m(I=1)),
    ("Defensive Formation", "Flank"):              (_m(I=-1, TS=1), _m(I=1)),
    ("Defensive Formation", "Charge"):             (_m(TH=1, TS=1), _m(TS=-1)),
    ("Defensive Formation", "Fighting Formation"): (_m(TS=1), _m(TH=1)),
    ("Defensive Formation", "Defensive Formation"): (_m(TS=1), _m(TS=1)),
    ("Defensive Formation", "Fall Back"):          (_m(end=True), _m(end=True, strain=True)),
    # -- Fall Back --
    ("Fall Back", "Scout"):                        (_m(end=True, strain=True), _m(end=True)),
    ("Fall Back", "Ambush"):                       (_m(end=True, strain=True), _m(end=True)),
    ("Fall Back", "Flank"):                        (_m(I=1, TH=1), _m(I=-1)),
    ("Fall Back", "Charge"):                       (_m(I=-1), _m(I=1, TH=1)),
    ("Fall Back", "Fighting Formation"):           (_m(), _m(TH=1)),
    ("Fall Back", "Defensive Formation"):          (_m(end=True, strain=True), _m(end=True)),
    ("Fall Back", "Fall Back"):                    (_m(end=True), _m(end=True)),
}
 
TACTICS = ["Scout", "Ambush", "Flank", "Charge", "Fighting Formation", "Defensive Formation", "Fall Back"]
 



# PLAYSTYLE: faction playstyle taxonomy (12 buckets)
# 7 axes (0; fill 1->5) | pairs | complements | factions | wonders | both.
# Seats: Royal Pavilion=prowess-adjacent only; Senate Hall=Generalist/Influence/Polymath only;
# Advanced Blast Furnace=assumed default (stripped). Complements pruned to archetype domains
# (wonders exempt). Saddlery removed from Influence.

PLAYSTYLES = {
    'Industry x Prowess': {
        'military_solutions'    : 5,
        'economy_generators'    : 4,
        'faith_management'      : 2,
        'doubt_warfare'         : 2,
        'political_control'     : 3,
        'board_presence'        : 4,
        'degenerate_punishment' : 2,
        'pairs':       {'Advanced Blast Furnace', 'Royal Pavilion', 'The Grand Exchange', 'Colossus'},
        'complements': set(),
        'factions':    ['The Iron Shore', 'The Winter Wolves', 'The Pale Throne'],
        'wonders':     ['Colossus', 'The Grand Exchange'],
    },
    'Industry x Cunning': {
        'military_solutions'    : 2,
        'economy_generators'    : 5,
        'faith_management'      : 2,
        'doubt_warfare'         : 4,
        'political_control'     : 4,
        'board_presence'        : 1,
        'degenerate_punishment' : 3,
        'pairs':       {'Aristocratic Court', "Thieves' Guild" , 'The Grand Exchange', 'High Chancery'},
        'complements': {"Manor House", "Outrider Intercept Post"},
        'factions':    ['The Crimson Tide', 'The Grand Compact', 'The Illuminated Order'],
        'wonders':     ['High Chancery', 'The Grand Exchange'],
    },
    'Industry x Piety': {
        'military_solutions'    : 3,
        'economy_generators'    : 4,
        'faith_management'      : 4,
        'doubt_warfare'         : 3,
        'political_control'     : 2,
        'board_presence'        : 1,
        'degenerate_punishment' : 3,
        'pairs':       { 'Inquisitorial Palace', 'The Grand Exchange', 'The Great Basilica'},
        'complements': set(),
        'factions':    ['The Iron Faith', 'The Luminous Court', 'The Sacred Throne'],
        'wonders':     ['The Grand Exchange', 'The Great Basilica'],

    },
    'Prowess x Cunning': {
        'military_solutions'    : 4,
        'economy_generators'    : 2,
        'faith_management'      : 1,
        'doubt_warfare'         : 4,
        'political_control'     : 3,
        'board_presence'        : 4,
        'degenerate_punishment' : 5,
        'pairs':       {'Royal Pavilion', 'Outrider Intercept Post'},
        'complements': {"Thieves' Guild", "Cipher Chamber"},
        'factions':    ["The Squatters' Crown", 'The Bandit King'],
        'wonders':     ['Colossus', 'High Chancery'],

    },
    'Prowess x Piety': {
        'military_solutions'    : 5,
        'economy_generators'    : 2,
        'faith_management'      : 4,
        'doubt_warfare'         : 3,
        'political_control'     : 2,
        'board_presence'        : 3,
        'degenerate_punishment' : 2,
        'pairs':       {'Royal Pavilion', "Preceptory of the Knight's Templar", "Imperial Palace" },
        'complements': {'Inquisitorial Palace'},
        'factions':    ['The Undying Flame', 'The Bloodied Cross', 'The Blazing Standard'],
        'wonders':     ['Colossus', 'The Great Basilica'],

    },
    'Cunning x Piety': {
        'military_solutions'    : 2,
        'economy_generators'    : 2,
        'faith_management'      : 4,
        'doubt_warfare'         : 5,
        'political_control'     : 4,
        'board_presence'        : 1,
        'degenerate_punishment' : 5,
        'pairs':       {"Thieves' Guild", 'Inquisitorial Palace'},
        'complements': {"War College"},
        'factions':    ['The Velvet Hand', 'The Ashen Vale', 'The Smoldering Crown'],
        'wonders':     ['High Chancery', 'The Great Basilica'],

    },
    'Mono-Industry': {
        'military_solutions'    : 3,
        'economy_generators'    : 5,
        'faith_management'      : 3,
        'doubt_warfare'         : 1,
        'political_control'     : 3,
        'board_presence'        : 3,
        'degenerate_punishment' : 2,
        'pairs':       {'Aristocratic Court', 'Studium Generale', 'Winery', 'The Grand Exchange'},
        'complements': {'Advanced Blast Furnace', 'Colossus','The Great Basilica', 'High Chancery', "Meadery"},
        'factions':    ['The Verdant Kingdom', 'The Merchant Republics', 'The Gilded Path', 'The Gilded Crescent'],
        'wonders':     ['Colossus', 'High Chancery', 'The Grand Exchange', 'The Great Basilica'],
    },
    'Mono-Prowess': {
        'military_solutions'    : 5,
        'economy_generators'    : 1,
        'faith_management'      : 3,
        'doubt_warfare'         : 2,
        'political_control'     : 2,
        'board_presence'        : 5,
        'degenerate_punishment' : 4,
        'pairs':       {"Ministry of Military Strategy", 'Royal Pavilion'},
        'complements': {"Imperial Palace"},
        'factions':    ['The Battering Ram', 'The Boundless Steppe', 'The Yew Heart', 'The Elder Grove'],
        'wonders':     ['Colossus', 'The Great Basilica'],
    },
    'Generalist': {
        'military_solutions'    : 3,
        'economy_generators'    : 3,
        'faith_management'      : 4,
        'doubt_warfare'         : 2,
        'political_control'     : 4,
        'board_presence'        : 3,
        'degenerate_punishment' : 2,
        'pairs':       {'Senate Hall', 'Inquisitorial Palace', 'Forge', 'Imperial Palace'},
        'complements': set(),
        'factions':    ['The Iron Throne', 'The Final Word', 'The Tunnellers', 'The Ancient Wilds'],
        'wonders':     ['High Chancery', 'The Grand Exchange', 'The Great Basilica'],
        'both':        {'Senate Hall'},
    },
    'Influence': {
        'military_solutions'    : 2,
        'economy_generators'    : 3,
        'faith_management'      : 4,
        'doubt_warfare'         : 3,
        'political_control'     : 5,
        'board_presence'        : 2,
        'degenerate_punishment' : 3,
        'pairs':       {'Studium Generale', 'Senate Hall', 'Aristocratic Court'},
        'complements': {"War College", "Ministry of Military Strategy"},
        'factions':    ['The Crowned Star', 'The Entwined Crown', 'The Eternal Court', 'The Inner Circle', 'The Hermit Crown'],
        'wonders':     ['High Chancery', 'The Great Basilica'],

    },
    'Polymath': {
        'military_solutions'    : 4,
        'economy_generators'    : 4,
        'faith_management'      : 4,
        'doubt_warfare'         : 4,
        'political_control'     : 4,
        'board_presence'        : 4,
        'degenerate_punishment' : 2,
        'pairs':       {'Studium Generale', "Manor House"},
        'complements': {'Senate Hall', 'Advanced Blast Furnace'},
        'factions':    ['The Hall of Masks', 'The Wandering Crown', 'The Forked Tongue', 'The Broken Banner', 'The Sublime Gate'],
        'wonders':     ['Colossus', 'High Chancery', 'The Grand Exchange', 'The Great Basilica'],

    },
    'The Duke': {
        'military_solutions'    : 2,
        'economy_generators'    : 5,
        'faith_management'      : 5,
        'doubt_warfare'         : 1,
        'political_control'     : 5,
        'board_presence'        : 1,
        'degenerate_punishment' : 1,
        'pairs':       {'Studium Generale', 'The Grand Exchange'},
        'complements': set(),
        'factions':    ['The Dukedom'],
        'wonders':     ['High Chancery', 'The Great Basilica','The Grand Exchange'],

    },
}


# ── NODES — THE master node graph. EDIT HERE (CSVs are retired/exported). ──
# Per node: rules text (type/unlock/mastery_req/innate/mastery/builds_into),
# 'escalation' = Escalation talent-tree view (presence = membership),
# 'engine' = machine-readable sim semantics (cost/prereqs/domain/tags/upkeep;
#            'alias' = the short name the sim uses internally).
# Rules text and engine tags must be kept in agreement when editing.
NODES = {
    "Quarry": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "Masonry",
        "innate": "+300, **Natural**; Craft +1",
        "mastery": "",
        "builds_into": ["Masonry"],
        "monument": False},
    "Salt Works": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "Smokehouse",
        "innate": "+300, **Natural**; Craft +1",
        "mastery": "",
        "builds_into": ["Smokehouse", "Harbor", "Reliquary", "Levy Hall"],
        "monument": False},
    "Apiary": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "Chandlery",
        "innate": "+300, **Natural**; Craft +1",
        "mastery": "",
        "builds_into": ["Chandlery", "Alchemy", "Vineyard", "Orchard", "Meadery"],
        "monument": False},
    "Peat Bog": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "Alchemy",
        "innate": "+300, **Natural**; Craft +1",
        "mastery": "",
        "builds_into": ["Alchemy", "Herb Garden", "Vineyard", "Orchard"],
        "monument": False},
    "Forestry": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "Carpentry",
        "innate": "+300, **Natural**; Craft +1",
        "mastery": "",
        "builds_into": ["Carpentry", "Fletchery", "Kiln", "Charcoal Burner"],
        "monument": False},
    "Fishmongery": {
        "type": "Raw Materials",
        "unlock": "Water Settlement",
        "mastery_req": "Harbor",
        "innate": "+300, **Natural**; Craft +1",
        "mastery": "",
        "builds_into": ["Harbor"],
        "monument": False},
    "Mine": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "Blacksmith",
        "innate": "+300, **Natural**; Craft +1",
        "mastery": "",
        "builds_into": ["Furnace", "Blacksmith", "Jewelry Foundry"],
        "monument": False},
    "Arable Land": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "Granary",
        "innate": "+300, **Natural**; Craft +1",
        "mastery": "",
        "builds_into": ["Granary", "Herb Garden", "Animal Husbandry", "Bakery", "Vineyard", "Orchard"],
        "monument": False},
    "Common Land": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "Workyard",
        "innate": "+500, **Natural**, **Doubt +1**",
        "mastery": "",
        "builds_into": ["Workyard", "Burgages"],
        "monument": False},
    "Herb Garden": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land or Peat Bog",
        "innate": "+200, **Natural**",
        "mastery": "Craft +1",
        "builds_into": ["Apothecary", "Spice Merchant"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Animal Husbandry": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land",
        "innate": "+100, **Natural**, Unlock **Crude** armor and shield.",
        "mastery": "+300",
        "builds_into": ["Saddlery", "Tannery", "Stable", "Weavery", "Butchery"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Gambeson armor"}, "row": 1, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": ["tier:Gambeson"], "mastery_tags": [], "mastery_req": []}},
    "Saddlery": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land + Animal Husbandry + Stable",
        "innate": "+500, **Natural**",
        "mastery": "**Upkeep -500**; Speed +1",
        "efficient": "Stable",
        "builds_into": [],
        "monument": False},
    "Vineyard": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land + Apiary or Peat Bog",
        "innate": "**Natural**",
        "mastery": "+600 in **Fall**",
        "builds_into": ["Winery"],
        "monument": False},
    "Orchard": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land + Apiary or Peat Bog",
        "innate": "**Natural**",
        "mastery": "+400 in **Fall**",
        "builds_into": ["Meadery", "Cidery"],
        "monument": False},
    "Carpentry": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Forestry",
        "innate": "**Build Timer −1**",
        "mastery": "+100; Craft+1",
        "efficient": "Forestry",
        "builds_into": ["Joinery", "Fletchery", "Artisan Workshop", "Trade Guild", "Shipyard", "Stable"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Alchemy": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Apiary or Peat Bog",
        "innate": "+100",
        "mastery": "+200; Craft+1",
        "efficient": "Peat Bog",
        "builds_into": ["Academy", "Infirmary", "Toxicarium"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Masonry": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Quarry",
        "innate": "**Build Timer −1**",
        "mastery": "+100; Craft+1",
        "efficient": "Quarry",
        "builds_into": ["Courtyard", "Episcopal Court", "Trade Guild", "Citadel"],
        "monument": False},
    "Butchery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Animal Husbandry + Tannery + Salt Works",
        "innate": "+300",
        "mastery": "**Upkeep -200**; Craft+1",
        "efficient": "Smokehouse",
        "builds_into": ["Smokehouse"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": ["Animal Husbandry", "Tannery"], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Animal Husbandry", "Tannery", "Salt Works"], "upkeep_effects": [{"flat": 500}]}},
    "Bakery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Arable Land + Mill",
        "innate": "+300; Faith +1",
        "mastery": "+100; Craft +2",
		"efficient": "Arable Land",
        "builds_into": [],
        "monument": False},
    "Weavery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Merchant Quarter + Animal Husbandry",
        "innate": "+300",
        "mastery": "+300; Craft +2",
        "builds_into": ["Artisan Workshop"],
        "monument": False},
    "Fletchery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Carpentry",
        "innate": "Unlocks **Ranged Weapons**",
        "mastery": "**Upkeep -200**",
        "efficient": "Carpentry",
        "builds_into": ["Tiltyard"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Ranged weapons"}, "row": 1, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Carpentry"], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Forestry", "Carpentry"], "upkeep_effects": [{"if_ranged": 200}]}},
    "Chandlery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Apiary",
        "innate": "+200",
        "mastery": "**Influence −1** to Cunning actions targeting you; Craft +1",
        "efficient": "Apiary",
        "builds_into": ["Reliquary", "Pilgrimage Site"],
        "monument": False},
    "Tannery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Animal Husbandry",
        "innate": "Unlocks **Cast** armor & shield.",
        "mastery": "**Upkeep -200**; Craft +1",
        "efficient": "Animal Husbandry",
        "builds_into": ["Butchery", "Armory"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Leather armor"}, "row": 2, "gate": None, "requires_all": ["Animal Husbandry"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": ["tier:Leather"], "mastery_tags": [], "mastery_req": ["Animal Husbandry"], "upkeep_effects": [{"flat": 200}]}},
    "Joinery": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "Carpentry",
        "innate": "+200, unlocks **Shields**",
        "mastery": "**Upkeep -200**",
        "efficient": "Carpentry",
        "builds_into": ["Winery", "Meadery", "Cidery"],
        "monument": False,
        "escalation": {"standing": "Rising Industry", "ranks": {1: "Shields"}, "row": 2, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Carpentry"], "domain": {"Industry": 3}, "innate_tags": ["tier:Shields"], "mastery_tags": [], "mastery_req": ["Carpentry"], "upkeep_effects": [{"if_shield": 200}]}},
    "Furnace": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Mine",
        "innate": "Unlocks **Cast Weapons**",
        "mastery": "+200",
        "efficient": "Mine",
        "builds_into": ["Blacksmith", "Jewelry Foundry"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Cast weapons"}, "row": 1, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": ["tier:Cast"], "mastery_tags": [], "mastery_req": ["Mine"]}},
    "Blacksmith": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "Furnace",
        "innate": "+200; Craft +1",
        "mastery": "Unlocks **Wrought** Tier",
        "efficient": "Furnace",
        "builds_into": ["Forge", "Armory", "Stable", "Siege Works", "Supply Depot"],
        "monument": False,
        "escalation": {"standing": "Rising Industry", "ranks": {1: "Wrought weapons"}, "row": 2, "gate": None, "requires_all": ["Furnace"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Furnace"], "domain": {"Industry": 3}, "innate_tags": [], "mastery_tags": ["tier:Wrought"], "mastery_req": ["Furnace"], "efficient": "Furnace"}},
    "Jewelry Foundry": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Mine + Merchant Quarter + Furnace",
        "innate": "+200; Craft +2",
        "mastery": "+500; **Influence +1** to Cunning Envoys targeting this player",
        "efficient": "Gilded Foundry",
        "builds_into": [],
        "monument": False},
    "Armory": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "Tannery + Blacksmith",
        "innate": "**Unlock Wrought** armor & shield",
        "mastery": "**Upkeep -300**; Craft +1",
        "efficient": "Tannery",
        "builds_into": ["Gilded Foundry"],
        "monument": False,
        "escalation": {"standing": "Rising Industry", "ranks": {1: "Chainmail"}, "row": 3, "gate": None, "requires_all": ["Tannery"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Tannery", "Blacksmith"], "domain": {"Industry": 3}, "innate_tags": ["tier:Chainmail"], "mastery_tags": [], "mastery_req": ["Tannery", "Blacksmith"], "efficient": "Tannery", "upkeep_effects": [{"flat": 200}]}},
    "Master Workshop": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Blacksmith",
        "innate": "**Upkeep -200**; Craft +1",
        "mastery": "Add **Serrated** to Weapons",
        "builds_into": ["Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: "Serrated"}, "row": 5, "gate": None, "requires_all": ["Stable"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Blacksmith"], "domain": {"Industry": 6}, "innate_tags": [], "mastery_tags": ["Serrated"], "mastery_req": ["Blacksmith"], "upkeep_effects": [{"flat": 200}]}},
    "Gilded Foundry": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Armory + Blacksmith",
        "innate": f"{PLANISHING}: Your to-Save can't be reduced beyond {CAP_THR}+.",
        "mastery": "Unlock **Forged** armor and shield. Craft +1.",
        "efficient": "Armory",
        "builds_into": ["Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: f"Full Plate + {PLANISHING}"}, "row": 5, "gate": None, "requires_all": ["Stable"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Armory"], "domain": {"Industry": 6}, "innate_tags": [PLANISHING], "mastery_tags": ["tier:FullPlate"], "mastery_req": ["Armory","Blacksmith"]}},
    "Smokehouse": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Salt Works + Kiln + Butchery",
        "innate": "+300; Craft +1",
        "mastery": "**Upkeep -200**",
        "efficient": "Salt Works",
        "builds_into": ["Supply Depot"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": ["Butchery"], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Salt Works", "Kiln", "Butchery"], "efficient": "Butchery", "upkeep_effects": [{"flat": 200}]}},
    "Workyard": {
        "type": "Craft",
        "unlock": "—",
        "mastery_req": "Common Land",
        "innate": "**Doubt +1**, +400",
        "mastery": "+400",
        "efficient": "Common Land",
        "builds_into": ["Census Hall", "Storehouse"],
        "monument": False},
    "Storehouse": {
        "type": "Craft",
        "unlock": "Sovereign Industry",
        "mastery_req": "Workyard + Shipyard",
        "innate": "**Doubt +2**, +600",
        "mastery": "**Build Timer −2**",
        "builds_into": ["Office of Works"],
        "monument": False},
    "Meadery": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Apiary + Inn",
        "innate": "**Faith +1**, +300",
        "mastery": "+200,**Speed +1** in **Winter**",
        "efficient": "Apiary",
        "builds_into": [],
        "monument": False},
    "Winery": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Vineyard + Joinery",
        "innate": "+400",
        "mastery": "Craft +3",
        "efficient": "Vineyard",
        "builds_into": [],
        "monument": False},
    "Cidery": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Orchard + Joinery + Inn",
        "innate": "**Faith +1**, +200",
        "mastery": "+300; Craft +1",
        "efficient": "Orchard",
        "builds_into": [],
        "monument": False},
    "Market Square": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "2 Raw Materials",
        "innate": "Craft +2",
        "mastery": "+400",
        "efficient": "Courtyard",
        "builds_into": ["Inn", "Merchant Quarter", "Spice Merchant", "Census Hall", "Thieves' Guild"],
        "monument": False},
    "Inn": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Caravanery + Market Square",
        "innate": "**Faith +1** for trading partners with Craft 3+",
        "mastery": "**Faith +1**",
        "builds_into": ["Secret Cellar", "Meadery", "Cidery"],
        "monument": False},
    "Spice Merchant": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Caravanery + Merchant Quarter + Herb Garden",
        "innate": "+300; Influence +1 to Cunning Envoys targeting you",
        "mastery": "+500; Craft +2",
        "builds_into": [],
        "monument": False},
    "Harbor": {
        "type": "Craft",
        "unlock": "Water Settlement",
        "mastery_req": "Fishmongery + Salt Works",
        "innate": "+300; Craft +2",
        "mastery": "**Extort 200** per **player** without **Harbor**",
        "efficient": "Fishmongery",
        "builds_into": ["Shipyard"],
        "monument": False},
    "Merchant Quarter": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "Craft 3 + Market Square",
        "innate": "+500",
        "mastery": "Trade Partners gain Craft +2",
        "efficient": "Market Square",
        "builds_into": ["Money Lending", "Court Artists", "Spice Merchant", "Jewelry Foundry", "Weavery"],
        "monument": False},
    "Money Lending": {
        "type": "Power",
        "unlock": "Established Industry",
        "mastery_req": "Merchant Quarter",
        "innate": "**Extort 500**",
        "mastery": "May loan money to Trade Partners at 100 per 1000/turn interest(minimum 100); on Default: Perform **Demand Tribute**",
        "builds_into": ["Court Artists", "Aristocratic Court"],
        "monument": False},
    "Census Hall": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Workyard + Market Square",
        "innate": "**Doubt +1**; +200",
        "mastery": "+500",
        "builds_into": [],
        "monument": False},
    "Caravanery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Market Square or Merchant Quarter + Stable",
        "innate": "**Influence -1** to **Intercept Caravan actions** targeting your **settlements**",
        "mastery": "**Craft +2**; **Speed -2** to non-allied players in your Province.",
        "builds_into": ["Inn", "Spice Merchant", "Courier Network", "Toll House"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {"Cunning": 6}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Market Square"]}},
    "Stable": {
        "type": "Civic",
        "unlock": "1 Rising",
        "mastery_req": "Animal Husbandry + Blacksmith or Carpentry",
        "innate": "**Speed +1**",
        "mastery": "**Speed +1**; Unlocks Cavalry Weapons",
        "efficient": "Animal Husbandry",
        "builds_into": ["Saddlery", "Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Cavalry weapons"}, "row": 4, "gate": 3, "requires_all": [], "requires_any": ["Forge", "Armory"], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Animal Husbandry", "Blacksmith"], "efficient": "Animal Husbandry"}},
    "Shipyard": {
        "type": "Craft",
        "unlock": "Established Industry, Water Settlement",
        "mastery_req": "Carpentry + Harbor",
        "innate": "Craft +1",
        "mastery": "Craft +2; Water Territory treated as Grassland for movement",
        "efficient": "Harbor",
        "builds_into": ["Storehouse"],
        "monument": False},
    "Coliseum": {
        "type": "Civic",
        "unlock": "Rising Prowess",
        "mastery_req": "Conditioning Field",
        "innate": "**Faith +1** while at War",
        "mastery": "Unlocks **Man-at-Arms** for **Muster**",
        "efficient": "Conditioning Field",
        "builds_into": ["War College", "Tiltyard", "Grand Tournament", "Stable"],
        "monument": False,
        "escalation": {"standing": "Rising Prowess", "ranks": {1: "Man-at-Arms unlock"}, "row": 2, "gate": None, "requires_all": ["Conditioning Field"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Conditioning Field"], "domain": {"Prowess": 3}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Conditioning Field"]}},
    "Interrogation Chambers": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Episcopal Court",
        "innate": "",
        "mastery": "Cunning actions targetting this player that cause Doubt are reduced by 1, to a minimum of 0.",
        "efficient": "Episcopal Court",
        "builds_into": ["Execution Dock"],
        "monument": False},
    "Abbey": {
        "type": "Civic",
        "unlock": "Established Piety",
        "mastery_req": "Episcopal Court + Academy",
        "innate": "Once/turn: **Influence +1** another player's Piety Envoy",
        "mastery": "Shake +1.",
        "efficient": "Episcopal Court",
        "builds_into": ["Reliquary", "Monastery"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {"Piety": 6}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Episcopal Court", "Academy"]}},
    "Reliquary": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Salt Works + Chandlery + Cathedral",
        "innate": "",
        "mastery": "First **Doubt** per turn reduced by 1 (min 0)",
        "efficient": "Abbey",
        "builds_into": ["Pilgrimage Site", "Papal Palace"],
        "monument": False},
    "Monastery": {
        "type": "Power",
        "unlock": "Established Piety",
        "mastery_req": "Abbey",
        "innate": "**Influence −1** to Piety actions targeting you",
        "mastery": "Other players can't Oppose your Piety Envoys",
        "efficient": "Abbey",
        "builds_into": ["Inquisitorial Palace", "Preceptory of the Knight's Templar"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {"Piety": 6}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Bell Tower": {
        "type": "Civic",
        "unlock": "Established Piety",
        "mastery_req": "Episcopal Court",
        "innate": "**+1 Influence**/turn",
        "mastery": "**Influence +1** to Piety actions",
        "efficient": "Courtyard",
        "builds_into": ["Embassy"],
        "monument": False},
    "Execution Dock": {
        "type": "Civic",
        "unlock": "Established Piety",
        "mastery_req": "Interrogation Chambers",
        "innate": "**Influence -1** to **Foster Rebellion actions** targeting your **settlements**",
        "mastery": "**Players** who **target** you or your **settlements** with **actions** that cause **doubt** gain **Doubt +1**",
        "builds_into": ["Inquisitorial Palace", "Imperial Palace"],
        "monument": False},
    "Hospitaller": {
        "type": "Power",
        "unlock": "Established Piety",
        "mastery_req": "Apothecary + Infirmary",
        "innate": "**Recover** improved by +1",
        "mastery": f"Enduring: while Fatigued, your Recover rolls can't be reduced beyond {CAP_THR}+.",
        "efficient": "Infirmary",
        "builds_into": ["Preceptory of the Knight's Templar"],
        "monument": False,
        "escalation": {"standing": "Established Piety", "ranks": {1: f"Recover 6; {ENDURING}"}, "row": 4, "gate": None, "requires_all": ["Infirmary"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Apothecary", "Infirmary"], "domain": {"Piety": 6}, "innate_tags": ["Recover 6"], "mastery_tags": [ENDURING], "mastery_req": ["Apothecary", "Infirmary"]}},
    "Jester's Court": {
        "type": "Civic",
        "unlock": "1 Rising",
        "mastery_req": "Courtyard",
        "innate": "First **Oppose** on your Envoy: reduce by 1",
        "mastery": "Second **Oppose** on your Envoy: reduce by 1",
        "efficient": "Courtyard",
        "builds_into": ["Embassy"],
        "monument": False},
    "Embassy": {
        "type": "Civic",
        "unlock": "1 Established",
        "mastery_req": "Bell Tower + Jester's Court",
        "innate": "**Influence +1** to Diplomacy Envoys",
        "mastery": "Players that perform a Diplomacy action targetting you may perform another Displomacy action targetting you.",
        "efficient": "Jester's Court",
        "builds_into": ["Senate Hall"],
        "monument": False},
    "Granary": {
        "type": "Civic",
        "unlock": "Rising Industry",
        "mastery_req": "Arable Land",
        "innate": "Upkeep -200",
        "mastery": "Armies and Garrisons gain **Endurance** while Besieged",
        "efficient": "Arable Land",
        "builds_into": ["Supply Depot", "Citadel"],
        "monument": False},
    "Academy": {
        "type": "Civic",
        "unlock": "1 Rising",
        "mastery_req": "Library + Alchemy",
        "innate": "**Influence +1** to Council Envoys",
        "mastery": "**Influence +1** to non-Council Envoys",
        "builds_into": ["University", "Abbey", "War College", "Forgery Workshop", "Toxicarium", "College of Engineering"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Courtyard": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Masonry",
        "innate": "Craft +1",
        "mastery": "**Faith +1**",
        "builds_into": ["Conditioning Field", "Jester's Court", "Market Square"],
        "monument": False},
    "Episcopal Court": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Masonry",
        "innate": "**Faith +1**",
        "mastery": "Reduce the first instance of Doubt at start of turn by 1, min 0.",
        "builds_into": ["Interrogation Chambers", "Abbey", "Bell Tower"],
        "monument": False,
		"efficient": "Courtyard"},
    "Conditioning Field": {
        "type": "Civic",
        "unlock": "Rising Prowess",
        "mastery_req": "Courtyard",
        "innate": "**Faith +1** while not at War",
        "mastery": "Armies gain **Nimble**",
        "efficient": "Courtyard",
        "builds_into": ["Coliseum", "Grand Tournament"],
        "monument": False,
        "escalation": {"standing": "Untested Prowess", "ranks": {1: "Nimble"}, "row": 1, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Courtyard"], "domain": {"Prowess": 3}, "innate_tags": [], "mastery_tags": ["Nimble"], "mastery_req": []}},
    "Grand Tournament": {
        "type": "Civic",
        "unlock": "Established Prowess",
        "mastery_req": "Coliseum + Conditioning Field",
        "innate": "**Faith +1**; Improve Parry by +1.",
        "mastery": "3x/turn: exchange 500 gold for **1 Influence**; Armies gain **Riposte**",
        "efficient": "Coliseum",
        "builds_into": ["Royal Pavilion"],
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Riposte"}, "row": 4, "gate": None, "requires_all": ["Coliseum"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {"Prowess": 6}, "innate_tags": ["Parry +1"], "mastery_tags": ["Riposte"], "mastery_req": ["Conditioning Field", "Coliseum"], "efficient": "Coliseum"}},
    "Apothecary": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Herb Garden + Alchemy",
        "innate": "+300",
        "mastery": f"Gain Recover {RECOVER_BASE}, or improve Recover by +1.",
        "efficient": "Alchemy",
        "builds_into": ["Infirmary", "Hospitaller"],
        "monument": False,
        "escalation": {"standing": "Untested Piety", "ranks": {1: "Recover 8"}, "row": 1, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": ["Recover 8"], "mastery_req": ["Herb Garden"]}},
    "Infirmary": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Alchemy + Herb Garden",
        "innate": "+200",
        "mastery": "Improve Recover by +1",
        "efficient": "Apothecary",
        "builds_into": ["Hospitaller"],
        "monument": False,
        "escalation": {"standing": "Untested Piety", "ranks": {1: "Recover 7"}, "row": 2, "gate": None, "requires_all": ["Apothecary"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Apothecary"], "domain": {}, "innate_tags": [], "mastery_tags": ["Recover 7"], "mastery_req": ["Alchemy", "Herb Garden"], "efficient": "Apothecary", "upkeep_effects": [{"flat": 100}]}},
    "Supply Depot": {
        "type": "Civic",
        "unlock": "Rising Industry",
        "mastery_req": "Granary or Smokehouse",
        "innate": "**Craft +2**",
        "mastery": "May **Muster** an Army in a Settlement under Siege and increment Muster Timers.",
        "efficient": "Granary",
        "builds_into": [],
        "monument": False},
    "Artisan Workshop": {
        "type": "Civic",
        "unlock": "Established Industry",
        "mastery_req": "Carpentry + Arable Land + Weavery",
        "innate": "+400",
        "mastery": "+200, **Faith +1**",
        "builds_into": ["Court Artists"],
        "monument": False},
    "University": {
        "type": "Power",
        "unlock": "1 Established",
        "mastery_req": "Academy",
        "innate": "May spend one additional **Influence** per Support or Oppose",
        "mastery": "+1 **Influence** per Domain you are Rising",
        "efficient": "Academy",
        "builds_into": ["Studium Generale", "Ministry of Military Strategy", "College of Engineering"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Trade Guild": {
        "type": "Civic",
        "unlock": "Rising Industry",
        "mastery_req": "Masonry or Carpentry",
        "innate": "No Upkeep on **Primitive Infrastructure**",
        "mastery": "No Upkeep on **Developed Infrastructure**",
        "builds_into": ["College of Engineering"],
        "monument": False},
    "Court Artists": {
        "type": "Civic",
        "unlock": "Established Industry",
        "mastery_req": "Merchant Quarter + Artisan Workshop",
        "innate": "**Extort 500**; **Faith +1**",
        "mastery": "**Extort 500**; Target of Extort gains **Faith +1**",
        "builds_into": ["Aristocratic Court"],
        "monument": False},
    "Courier Network": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Caravanery + Inn",
        "innate": "Once/turn: **Influence −1** on Target Envoy",
        "mastery": "Once/turn: successfully Performed Personal Envoy can be Performed next turn; send 1 fewer Envoys next turn",
        "builds_into": ["Toll House", "Beacon Towers", "Outlaw Rookery"],
        "monument": False},
    "Toll House": {
        "type": "Civic",
        "unlock": "—",
        "mastery_req": "Caravanery + Courier Network",
        "innate": "Once/turn when an Army ends a Move action within Province: Perform a Diplomacy action targeting that army's player",
        "mastery": "**Extort 500** when non-Allied Army ends a Move action within Province",
        "builds_into": ["Beacon Towers"],
        "monument": False},
    "College of Engineering": {
        "type": "Power",
        "unlock": "Established Industry",
        "mastery_req": "Academy + Trade Guild",
        "innate": "No Upkeep on **Sophisticated Infrastructure**",
        "mastery": "**Build Timer −2**",
        "efficient": "Trade Guild",
        "builds_into": ["Office of Works"],
        "monument": False},
    "Secret Cellar": {
        "type": "Energy",
        "unlock": "Rising Cunning",
        "mastery_req": "Smuggler's Nook",
        "innate": "—",
        "mastery": "Passed Cunning actions **Recoup 500 Gold**",
        "efficient": "Inn",
        "builds_into": ["Smuggler's Nook", "Forgery Workshop", "Forgotten Catacombs", "Thieves' Guild"],
        "monument": False},
    "Smuggler's Nook": {
        "type": "Secrecy",
        "unlock": "Established Cunning",
        "mastery_req": "Secret Cellar + Inn",
        "innate": "gain Immune Uprising (Bandit Camp Spawn at -5PO)",
        "mastery": "Bandit Camps in your Outlaw Country don't target you and target other players instead randomly.",
        "efficient": "Secret Cellar",
        "builds_into": ["Thieves' Guild", "Outlaw Rookery"],
        "monument": False},
    "Black Market": {
        "type": "Secrecy",
        "unlock": "Established Cunning",
        "mastery_req": "Market Square + Smuggler's Nook",
        "innate": "When another player **Extorts** gold from any source: **Extort 200** per 1000 (minimum 100) from that player at the end of that resolution.",
        "mastery": "When another player **Recoups** gold from any source: **Extort 200** per 1000 (minimum 100) from that player at the end of that resolution.",
        "efficient": "Market Square",
        "builds_into": ["Thieves' Guild"],
        "monument": False},
    "Forgery Workshop": {
        "type": "Power",
        "unlock": "Established Cunning",
        "mastery_req": "Academy + Secret Cellar",
        "innate": "**Extort 200** anytime a player Opposes an Envoy of yours",
        "mastery": "Once/turn: attempt another Cunning Envoy targeting a different player if your Cunning Envoy Failed",
        "efficient": "Academy",
        "builds_into": ["Aristocratic Court"],
        "monument": False},
    "Toxicarium": {
        "type": "Secrecy",
        "unlock": "Rising Cunning",
        "mastery_req": "Academy + Alchemy",
        "innate": "Weapons gain **Poison**",
        "mastery": "All Endorsed Cunning actions give an additional **Doubt +1** to Target",
        "efficient": "Alchemy",
        "builds_into": ["Outlaw Rookery"],
        "monument": False,
        "escalation": {"standing": "Rising Cunning", "ranks": {1: "Poison"}, "row": 2, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Academy", "Alchemy"], "domain": {"Cunning": 3}, "innate_tags": ["Poison"], "mastery_tags": [], "mastery_req": ["Academy", "Alchemy"], "upkeep_effects": [{"flat": 100}]}},
    "Pilgrimage Site": {
        "type": "Energy",
        "unlock": "Rising Piety",
        "mastery_req": "Reliquary + Chandlery",
        "innate": "**Extort 200** every player without a Pilgrimage Site",
        "mastery": "**Doubt +1** to all other players without a Pilgrimage Site",
        "efficient": "Reliquary",
        "builds_into": ["Papal Palace"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {"Piety": 3}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Beacon Towers": {
        "type": "Energy",
        "unlock": "Rising Prowess",
        "mastery_req": "Courier Network + Toll House",
        "innate": "—",
        "mastery": "Whenever a non-allied Army ends a Move action within Province, you may immediately perform a Move action",
        "efficient": "Toll House",
        "builds_into": [],
        "monument": False},
    "Forgotten Catacombs": {
        "type": "Secrecy",
        "unlock": "Rising Cunning",
        "mastery_req": "Secret Cellar",
        "innate": "Whenever you are the target of **Extort**, reduce the Extort amount by 100 (min 100).",
        "mastery": "Cunning actions against you can't be **Endorsed**",
        "efficient": "Secret Cellar",
        "builds_into": [],
        "monument": False},
    "Charcoal Burner": {
        "type": "Energy",
        "unlock": "Established Industry",
        "mastery_req": "Forestry + Kiln",
        "innate": "+400",
        "mastery": "",
        "efficient": ["Forestry", "Kiln"],
        "builds_into": [],
        "monument": False},
    "Mill": {
        "type": "Energy",
        "unlock": "Rising Industry",
        "mastery_req": "Bakery/Weavery/Forge/Carpentry",
        "innate": "+300",
        "mastery": "",
        "efficient": ["Bakery", "Weavery", "Forge", "Carpentry"],
        "builds_into": ["Bakery"],
        "monument": False},
    "Kiln": {
        "type": "Energy",
        "unlock": "Rising Industry",
        "mastery_req": "Forestry",
        "innate": "+300",
        "mastery": "",
        "efficient": "Forestry",
        "builds_into": ["Smokehouse", "Charcoal Burner"],
        "monument": False},
    "Burgages": {
        "type": "Energy",
        "unlock": "-",
        "mastery_req": "Common Land",
        "innate": "+200",
        "mastery": "**Faith +1**",
        "efficient": "Common Land",
        "builds_into": [],
        "monument": False},
    "Levy Hall": {
        "type": "Power",
        "unlock": "Rising Prowess",
        "mastery_req": "Keep + Salt Works",
        "innate": "**Upkeep -1000 while an army is range 0 of controlled settlement**",
        "mastery": "**Upkeep -1000 while an army is range 0 of controlled settlement**",
        "builds_into": ["War College", "Ministry of Military Strategy"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {"Prowess": 3}, "innate_tags": [], "mastery_tags": [], "mastery_req": [], "upkeep_effects": [{"flat": 200}]}},
    "Siege Works": {
        "type": "Power",
        "unlock": "Rising Prowess",
        "mastery_req": "Blacksmith",
        "innate": "**Siege Timer −1**",
        "mastery": "**Siege Timer −1**; Sieges Increment in **Winter**",
        "builds_into": ["Siege Camp"],
        "monument": False},
    "Siege Camp": {
        "type": "Power",
        "unlock": "Established Prowess",
        "mastery_req": "Siege Works",
        "innate": "**Siege Timer −1**",
        "mastery": "Armies gain **Immune Strained** during Lay Siege",
        "efficient": "Siege Works",
        "builds_into": ["Artillery Park"],
        "monument": False},
    "Citadel": {
        "type": "Power",
        "unlock": "Established Industry",
        "mastery_req": "Masonry + Granary",
        "innate": "**Siege Timer +1**",
        "mastery": "**Siege Timer +1**, Controlled Settlements gain **Reach +1**",
        "efficient": "Granary",
        "builds_into": ["Imperial Palace"],
        "monument": False},
    "War College": {
        "type": "Power",
        "unlock": "Established Prowess",
        "mastery_req": "Levy Hall + Academy",
        "innate": "Gain **+2 Influence** while At War",
        "mastery": "Unlocks **Sergeants** for Muster",
        "efficient": "Academy",
        "builds_into": ["Ministry of Military Strategy"],
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Sergeant unlock"}, "row": 4, "gate": None, "requires_all": ["Coliseum"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [ "Levy Hall", "Academy"], "domain": {"Prowess": 6}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Levy Hall", "Academy"], "efficient": "Academy"}},
    "Forge": {
        "type": "Power",
        "unlock": "Established Industry",
        "mastery_req": "Blacksmith",
        "innate": "Craft +2",
        "mastery": "Unlocks **Forged** Tier",
        "efficient": "Blacksmith",
        "builds_into": ["Master Workshop", "Gilded Foundry", "Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: "Forged weapons"}, "row": 3, "gate": None, "requires_all": ["Blacksmith"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Blacksmith"], "domain": {"Industry": 6}, "innate_tags": [], "mastery_tags": ["tier:Forged"], "mastery_req": ["Blacksmith"], "efficient": "Blacksmith"}},
    "Tiltyard": {
        "type": "Power",
        "unlock": "Established Prowess",
        "mastery_req": "Fletchery + Coliseum",
        "innate": "Armies may be Equipped with a second weapon (a Ranged and a Melee Weapon); the army gains **Unwieldy**",
        "mastery": "Your armies have **Immune Unwieldy**. Instead, they may equip two of the same 1H Melee Weapon to gain **Dual Wield**, **Two-Handed**, and **Florentine** (while Fatigued, may Parry on a natural {FOCUSED_THR}).",
        "builds_into": ["Royal Pavilion"],
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Dual-equip; Immune Unwieldy; Dual Wield (two of a kind)"}, "row": 4, "gate": None, "requires_all": ["Coliseum"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Fletchery", "Coliseum"], "domain": {"Prowess": 6}, "innate_tags": [], "mastery_tags": ["Immune Unwieldy", "Florentine"], "mastery_req": ["Fletchery", "Coliseum"]}},
    "Office of Works": {
        "type": "Monument",
        "unlock": "Sovereign Industry",
        "mastery_req": "College of Engineering + Storehouse",
        "innate": "Settlements & allied armies inside them are not affected by 'Settlements being Besieged' restrictions.",
        "mastery": "Siege Timer +2; Build Timer -2",
        "builds_into": [],
        "monument": True},
    "Royal Pavilion": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "Grand Tournament + Tiltyard",
        "innate": "Armies gain **Immune Strained**. Improve Parry by +1",
        "mastery": "Gain +1 to Strike. Deadly, & Cleave also trigger Focused Strikes on a natural 8+.",
		"efficient": "Tiltyard",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Prowess", "ranks": {1: "Immune Strain; Drilled"}, "row": 6, "gate": None, "requires_all": ["Tiltyard", "Grand Tournament"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Tiltyard"], "domain": {"Prowess": 10}, "innate_tags": ["Immune Strain", "Parry +1"], "mastery_tags": ["Crit 8","Strike +1"], "mastery_req": ["Grand Tournament", "Tiltyard"]}},
    "Imperial Palace": {
        "type": "Monument",
        "unlock": "Established Prowess",
        "mastery_req": "Citadel + Execution Dock",
        "innate": "Each Empire Phase, all non-allied players with a lower Prowess value gain Doubt +2.",
        "mastery": "If your Envoy would fail, it passes instead.",
        "efficient": "Citadel",
        "builds_into": [],
        "monument": True},
    "Artillery Park": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "Siege Camp + Master Workshop",
        "innate": "Siege Timers ignore Wooden & Stone Walls. Unlocks Arquebus",
        "mastery": "Settlements you Siege can't Sally Forth. Siege Timer −1.",
        "efficient": "Siege Camp",
        "builds_into": [],
        "monument": True,
        "engine": {"cost": 1, "prereqs": ["Siege Camp", "Master Workshop"],
                   "domain": {"Prowess": 10},
                   "innate_tags": ["Artillery Park"], "mastery_tags": [],
                   "mastery_req": ["Siege Camp", "Master Workshop"],
                   "efficient": "Siege Camp"}},
    "Ministry of Military Strategy": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "University + War College",
        "innate": "Always gains **Seize the Initiative**, and your opponent doesn't; Gain +1I & max initiative is 3",
        "mastery": "Gain Drilled.",
        "efficient": "War College",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Prowess", "ranks": {1: "Always Seize the Initiative; Gain +1I; your maximum initiative increases to 3.", 2: "Deadly, & Cleave also trigger on a natural 8+."}, "row": 6, "gate": None, "requires_all": ["War College"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {"Prowess": 10}, "innate_tags": ["Seize: first", "Init +1", "MaxInit3"], "mastery_tags": ["Drilled"], "mastery_req": ["University", "War College"]}},
    "Thieves' Guild": {
        "type": "Monument",
        "unlock": "Sovereign Cunning",
        "mastery_req": "Market Square + Smuggler's Nook + Secret Cellar + Black Market",
        "innate": "Whenever another player performs a Cunning action, you may recoup 1000 gold",
        "mastery": "**Extort 25%** of Trade Income from players who don't trade with you",
        "builds_into": [],
        "monument": True},
    "Senate Hall": {
        "type": "Monument",
        "unlock": "1 Sovereign",
        "mastery_req": "Embassy + Library + Town Hall",
        "innate": "**Faith +1**, gain **+1 Influence** per other player per Turn",
        "mastery": "Once/turn: Before players Support or Oppose, you may auto-**Condemn** an At War Envoy OR auto-**Endorse** an Ally's Envoy",
        "builds_into": [],
        "monument": True},
    "Papal Palace": {
        "type": "Monument",
        "unlock": "Sovereign Piety",
        "mastery_req": "Monastery + Pilgrimage Site + Reliquary",
        "innate": "Your Piety actions that cause doubt cause an additional doubt. You no longer pay cost for Piety actions.",
        "mastery": "At the start of each turn, Tithe every other player with lower Piety, resolved in the Extort step.\nOnce per turn, you may perform Spread Gospel.",
        "builds_into": [],
        "monument": True},
    "Inquisitorial Palace": {
        "type": "Monument",
        "unlock": "Sovereign Piety",
        "mastery_req": "Execution Dock + Monastery",
        "innate": "**Doubt +1**; Unlocks **Grand Vizier** which uses your **Public Order** instead of your **Cunning** value.",
        "mastery": "You may use your **Piety Value** as **Cunning Value** for **Grand Vizier**.",
        "efficient": "Monastery",
        "builds_into": [],
        "monument": True},
    "Preceptory of the Knight's Templar": {
        "type": "Monument",
        "unlock": "Sovereign Piety + Established Prowess",
        "mastery_req": "Monastery + Hospitaller + Abbey",
        "innate": f"Armies gain **{CRUSADER}**: Automatically pass the first Panic Check of every Battle.",
        "mastery": "Unlocks **Knight's Templar** for Muster",
        "efficient": "Monastery",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Piety", "ranks": {1: f"{CRUSADER}", 2: "Knight Templar unlock"}, "row": 6, "gate": None, "requires_all": ["Hospitaller"], "requires_any": [], "extra_req": "Established Prowess"},
        "engine": {"alias": "Preceptory", "cost": 1, "prereqs": [], "domain": {"Piety": 10, "Prowess": 6}, "innate_tags": ["Resolute"], "mastery_tags": [], "mastery_req": ["Monastery", "Pilgrimage Site", "Hospitaller", "Abbey"]}},
    "Manor House": {
        "type": "Monument",
        "unlock": "Established Industry",
        "mastery_req": "Hamlet + Market Square",
        "innate": "Gain +100 gold for each active natural specialization.",
        "mastery": "Gain +100 gold for each active energy specialization.",
        "builds_into": [],
        "monument": True},
    "Aristocratic Court": {
        "type": "Monument",
        "unlock": "Sovereign Cunning",
        "mastery_req": "Money Lending + Forgery Workshop + Court Artists",
        "innate": "Each Empire Phase, Extort 500 from each non-allied player with a lower Cunning value.",
        "mastery": "Your Vote counts as 2 votes toward Domain selection during the Council Phase.",
        "efficient": "Court Artists",
        "builds_into": [],
        "monument": True},
    "Studium Generale": {
        "type": "Monument",
        "unlock": "4 Established",
        "mastery_req": "University + Academy",
        "innate": "+1 **Influence** per **Established** Standing",
        "mastery": "May gain one **Sovereign Domain** effect without spending the Domain Points",
        "builds_into": [],
        "monument": True},
    "Outlaw Rookery": {
        "type": "Monument",
        "unlock": "Sovereign Cunning",
        "mastery_req": "Smuggler's Nook + Toxicarium + Courier Network",
        "innate": "Both Bandit Camps & you gain Influence +1 when performing Cunning actions.",
        "mastery": "Endorsed Foster Rebellion places Bandit Camps with 25 retinues instead of 10.",
        "efficient": "Smuggler's Nook",
        "builds_into": [],
        "monument": True},
    "Advanced Blast Furnace": {
        "type": "Monument",
        "unlock": "Sovereign Industry",
        "mastery_req": "Gilded Foundry + Master Workshop + Blacksmith + Stable",
        "innate": "**Upkeep -500**",
        "mastery": "**Crafted** Tier Unlocked; Craft +2",
        "efficient": "Forge",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Industry", "ranks": {1: "Crafted tier"}, "row": 6, "gate": None, "requires_all": ["Stable", "Master Workshop", "Gilded Foundry"], "requires_any": [], "extra_req": ""},
        "engine": {"alias": "ABF", "cost": 1, "prereqs": ["Gilded Foundry", "Master Workshop", "Blacksmith", "Stable"], "domain": {"Industry": 10}, "innate_tags": ["ABF"], "mastery_tags": ["tier:Crafted"], "mastery_req": ["Gilded Foundry", "Master Workshop", "Blacksmith", "Stable"], "efficient": "Forge", "upkeep_effects": [{"flat": 500}]}},
    "Cipher Chamber": {
        "type": "Power",
        "unlock": "Established Cunning",
        "mastery_req": "University + Courier Network",
        "innate": "Once/turn when a player Sends an Envoy: that player must declare the specific Action they would Perform if the Envoy Passes (including sub-Actions). If it Passes, they must Perform that declared Action.",
        "mastery": "Once/turn: select any active **Timer** you did not select last turn; increase it by 2.",
        "efficient": "University",
        "builds_into": ["Outrider Intercept Post"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": ["University", "Courier Network"], "domain": {"Cunning": 10}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["University", "Courier Network"]}},
    "Outrider Intercept Post": {
        "type": "Monument",
        "unlock": "Sovereign Cunning",
        "mastery_req": "Caravanery + Cipher Chamber",
        "innate": "In the first Skirmish of every Battle, your opponent plays their Tactic Card face up before you select your own.",
        "mastery": "Every Skirmish, you may force your opponent to reveal their Tactic Card they selected before you select your own.",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Cunning", "ranks": {1: "First Skirmish: see enemy Tactic before choosing", 2: "Every Skirmish: see enemy Tactic before choosing"}, "row": 6, "gate": None, "requires_all": ["Toxicarium"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Caravanery", "Cipher Chamber"], "domain": {"Cunning": 10}, "innate_tags": ["Outrider: once"], "mastery_tags": ["Outrider: every"], "mastery_req": ["Caravanery", "Cipher Chamber"]}}
    
}

def get_data(mode="renown"):
    """Return the node set for a game mode. 'escalation' = the combat subset
    (nodes carrying an 'escalation' key); 'renown' = everything."""
    if mode == "escalation":
        return {k: v for k, v in NODES.items() if "escalation" in v}
    return dict(NODES)

# ── FACTIONS ────────────────────────────────────────────────────────────────
# Master source for the 38+ asymmetric factions. Edit HERE; faction cards and
# docs are generated from this dict (factions.csv is retired).
FACTIONS = {
    'The Battering Ram': {
        'final_cut': True,
        'inspiration': 'Siege-focused',
        'feel': 'Offensive, Arrogant',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': 'Siege Specialist: You begin the game with a Siege Works (no Ward, no upkeep, always-active Mastery). When a player builds a Citadel, you must Siege it as an Edict.',
        'pair': 'Siege Camp, Royal Pavilion',
        'complement': 'Senate Hall',
    },
    'The Boundless Steppe': {
        'final_cut': False,
        'inspiration': 'Mongol Horde',
        'feel': 'Fast',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': "Horsemasters: You begin the game with a Stable (no Ward, no upkeep, always-active Mastery that can't be deactivated).",
        'pair': 'Saddlery, Royal Pavilion',
        'complement': 'Forge',
    },
    'The Bandit King': {
        'final_cut': True,
        'inspiration': 'Brigands',
        'feel': 'Scrappy',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic': "Friends in Low Places: You begin the game with a Smuggler's Nook (no Ward, no upkeep, always-active Mastery that can't be deactivated). Each turn, you may control one Bandit Camp outside your Territory. When a Bandit Camp is generated, you may place it in your Outlaw Country instead.",
        'pair': "Thieves' Guild, Saddlery",
        'complement': 'Royal Pavilion',
    },
    'The Crowned Star': {
        'final_cut': True,
        'inspiration': 'Reigning Sovereign',
        'feel': 'Sovereign Voice',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': "The Monarch: Each turn, you choose every Council Envoy's Domain. Every Envoy you send has Influence −1.",
        'pair': 'Senate Hall, Aristocratic Court',
        'complement': 'Royal Pavilion',
    },
    'The Crimson Tide': {
        'final_cut': False,
        'inspiration': 'Pirate',
        'feel': 'Pirate Life',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': "Sea Lanes: Other players can't perform Intercept Caravan on you. You begin the game with a Shipyard (no Ward, no upkeep, always-active Mastery) — even without a Water Settlement.",
        'pair': "Shipyard, Thieves' Guild",
        'complement': 'Royal Pavilion',
    },
    'The Entwined Crown': {
        'final_cut': True,
        'inspiration': 'Habsburg Dynasty',
        'feel': 'Diplomatic, Inescapable',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': "Royal Marriage: Once per game, you may join an Alliance without unanimous consent, or form one with a player who isn't in an Alliance. While in that Alliance, each member gains Faith +1 and Influence +1 per turn.",
        'pair': 'Aristocratic Court, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Eternal Court': {
        'final_cut': True,
        'inspiration': 'Byzantine Empire',
        'feel': 'Patient & Reserved',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': "Patient Court: Your unspent Influence isn't discarded in the Rest Phase. While the Era is Zenith, you may spend up to 5 Influence per Envoy, regardless of your Domain Standing.",
        'pair': 'Senate Hall, Aristocratic Court',
        'complement': 'Royal Pavilion',
    },
    'The Final Word': {
        'final_cut': False,
        'inspiration': 'Warlord Council',
        'feel': 'Cold Steel',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': 'The Decider: Ignore the innate Doubt and Influence modifiers for being At War.',
        'pair': 'Royal Pavilion, Imperial Palace',
        'complement': 'Senate Hall',
    },
    'The Gilded Crescent': {
        'final_cut': False,
        'inspiration': 'Moorish Caliphate',
        'feel': 'Egalitarian',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': "Prosperity For All: You begin the game with an Inn (no Ward, no upkeep, always-active Mastery that can't be deactivated).",
        'pair': 'Meadery & Winery, Studium Generale',
        'complement': 'Royal Pavilion',
    },
    'The Gilded Path': {
        'final_cut': False,
        'inspiration': 'Great Income',
        'feel': 'Rich Trader',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic': "Silk Road: You begin the game with an Artisan Workshop (no Ward, no upkeep, always-active Mastery). You can't refuse a Trade Agreement.",
        'pair': 'Meadery & Winery, Forge',
        'complement': 'Royal Pavilion',
    },
    'The Hermit Crown': {
        'final_cut': False,
        'inspiration': 'Independent',
        'feel': 'Independent',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic': "Independent, but Ambitious: You Abstain on every vote on other players' Envoys, and other players must spend 2 Influence to affect your Envoys by 1. Your Personal Envoys have Influence +1. You can't vote on Council Envoys.",
        'pair': 'Studium Generale, Saddlery',
        'complement': 'Royal Pavilion',
    },
    'The Illuminated Order': {
        'final_cut': False,
        'inspiration': 'Scholarly',
        'feel': 'Knowledge is Power',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': 'Knowledge is Power: Each turn, gain Influence +1 for every 3 Pursuits you have.',
        'pair': 'Studium Generale, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Iron Faith': {
        'final_cut': True,
        'inspiration': 'Crusader States',
        'feel': 'Piously Resolute',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': 'Fortress of Faith: While your Public Order is 3 or higher, Lay Siege actions targeting Settlements you Control have Siege Timer +2.',
        'pair': "Siege Camp, Preceptory of the Knight's Templar",
        'complement': 'Senate Hall',
    },
    'The Iron Shore': {
        'final_cut': True,
        'inspiration': 'Norse',
        'feel': 'Scavenger',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': 'Scavengers: You collect the Spoils of War whether you win or lose a Battle, and may also recoup the cost of your Retinues lost as Casualties in that Battle. When you perform the Repair action, Extort 2000 from the taret that performed the Raze action.',
        'pair': 'Royal Pavilion, Shipyard',
        'complement': 'Forge',
    },
    'The Iron Throne': {
        'final_cut': True,
        'inspiration': 'Defensive',
        'feel': 'Defensive, Impenetrable',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': "Unimpeachable: You begin the game with a Citadel (no Ward, no upkeep, always-active Mastery). You (and your Alliance) can't perform Declare War or Crusade.",
        'pair': 'Inquisitorial Palace, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Merchant Republics': {
        'final_cut': True,
        'inspiration': 'Italian City States',
        'feel': 'Trade Dependent',
        'difficulty': 'Low',
        'strength': 'High',
        'mechanic': "Heart of Trade: You begin the game with Stone Roads (no upkeep, can't be Razed). No player may trade unless they first hold a Trade Agreement with you, or are At War with you. When another player becomes eligible, you must attempt once to Sign a Trade Agreement with them. You can't perform the End Treaty action.",
        'pair': 'Shipyard, Meadery & Winery',
        'complement': 'Royal Pavilion',
    },
    'The Sacred Throne': {
        'final_cut': True,
        'inspiration': 'Papal State',
        'feel': 'Pure and Defensive',
        'difficulty': 'Low',
        'strength': 'High',
        'mechanic': 'Sacrosanct: When a player Declares War on you, that player and their allies gain Doubt +1.',
        'pair': "Inquisitorial Palace, Preceptory of the Knight's Templar",
        'complement': 'Royal Pavilion',
    },
    'The Tunnellers': {
        'final_cut': True,
        'inspiration': 'Dwarves',
        'feel': 'Mountain Passers',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic': 'Tunnellers: You treat mountain Territory as grassland for movement, and begin the game with a Mine Raw-Material Pursuit (no Ward, no upkeep, always-active Mastery).',
        'pair': 'Forge, Advanced Blast Furnace',
        'complement': 'Royal Pavilion',
    },
    'The Undying Flame': {
        'final_cut': True,
        'inspiration': 'Martyrs',
        'feel': 'Unconvinced',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic': f"Martyrdom: Your Armies' Morale can't be modified beyond {CAP_THR}+, but still suffer −{FATIGUE_MORALE} per Fatigue Token. Gain Faith +1 for every player you're At War with, and Faith +1 in every Battle where you lose 20 or more Retinues (win or lose). Your Armies have Immune War Weariness.",
        'pair': "Preceptory of the Knight's Templar, Inquisitorial Palace",
        'complement': 'Royal Pavilion',
    },
    'The Verdant Kingdom': {
        'final_cut': True,
        'inspiration': 'Industry',
        'feel': 'Pure Economy',
        'difficulty': 'Low',
        'strength': 'High',
        'mechanic': "Peaceful & Inventive: You can't Declare War, enter Military Alliances, perform Cunning actions, or build Pursuits that require Prowess or Cunning Standing. Gain 100 gold per total Craft level across all active sources.",
        'pair': 'Forge, Advanced Blast Furnace, Meadery & Winery',
        'complement': 'Senate Hall',
    },
    'The Winter Wolves': {
        'final_cut': False,
        'inspiration': 'Vikings',
        'feel': 'Aggressive, Parasitic',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': "Danegeld: While At War, your Armies pay no upkeep in Territory your at-war player controls. You don't gain Speed −1 in Winter.",
        'pair': 'Royal Pavilion, Shipyard',
        'complement': 'Forge',
    },
    'The Ancient Wilds': {
        'final_cut': True,
        'inspiration': 'Celtic Kingdoms',
        'feel': 'Oathkeepers',
        'difficulty': 'Medium',
        'strength': 'High',
        'mechanic': 'Highlander Way: Enemy Armies have Speed −1 in your Province. You ignore all terrain Speed modifiers and may trade without Dirt Roads. You must accept the first Non-Aggression Pact each player or Alliance offers you. If that player later joins an Alliance, this is considered satisfied for that Alliance.',
        'pair': 'Royal Pavilion, Saddlery',
        'complement': 'Senate Hall',
    },
    'The Bloodied Cross': {
        'final_cut': True,
        'inspiration': 'Crusading Sect',
        'feel': 'Holy War Without End',
        'difficulty': 'Medium',
        'strength': 'High',
        'mechanic': "Prophets of War: You may Crusade at Rising Piety instead of Sovereign Piety, with no cap on active Crusades. Each player gains Doubt +1 per Crusade you're on. You can't perform Convert actions.",
        'pair': "Preceptory of the Knight's Templar, Inquisitorial Palace",
        'complement': 'Senate Hall',
    },
    'The Blazing Standard': {
        'final_cut': False,
        'inspiration': 'Teutonic Knight',
        'feel': 'Crusader Feel',
        'difficulty': 'Medium',
        'strength': 'High',
        'mechanic': "Burning Cross: You begin the game with a Preceptory of the Knight's Templar (no Ward, no upkeep, always-active Mastery). When you Declared War via Crusade, that player takes a Panic Check at the start of every Battle, after lines are formed. During the Prowess Envoy phase, if you don't have an Army of 25 Knight's Templars, you must attempt to send an Envoy; if it passes, you must muster an Army until it holds 25 Knight's Templar Retinues.",
        'pair': "Preceptory of the Knight's Templar, Royal Pavilion",
        'complement': 'Senate Hall',
    },
    'The Inner Circle': {
        'final_cut': True,
        'inspiration': 'Natural Leader',
        'feel': 'Strength Through Diplomacy',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic': "Palatine: Each player allied with you has Influence +1 on their Envoys. Each turn, you may spend 1 of an ally's Influence, targeting your own Envoys if you wish.",
        'pair': 'Senate Hall, Aristocratic Court',
        'complement': 'Royal Pavilion',
    },
    'The Luminous Court': {
        'final_cut': True,
        'inspiration': 'Renaissance',
        'feel': 'Civic Soft Power',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic': "Arts & Humanities / Hearts & Minds: You can't pursue Craft Pursuits. Your Civic Pursuits have Craft +1 and cost no Upkeep. You must accept a Peace Treaty if one is offered.",
        'pair': 'Studium Generale, Aristocratic Court, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Grand Compact': {
        'final_cut': False,
        'inspiration': 'Hanseatic League',
        'feel': 'Peace Through Trade',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic': 'Mercantile Pact: When a player Declares War on you, each player who holds a Trade Agreement with you must either Declare War back or End that Trade Agreement.',
        'pair': 'Shipyard, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Pale Throne': {
        'final_cut': True,
        'inspiration': 'Undead',
        'feel': 'Undead',
        'difficulty': 'Medium',
        'strength': 'Low',
        'mechanic': "Inexorable: Your Armies always have Unwieldy and can't gain Immune Unwieldy; they also have Recover +1, Speed −1, and Immune Panic. Your Public Order can't exceed 1.",
        'pair': "Preceptory of the Knight's Templar, Forge",
        'complement': 'Advanced Blast Furnace',
    },
    'The Sublime Gate': {
        'final_cut': False,
        'inspiration': 'Ottoman Empire',
        'feel': 'Mercantile Military',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic': "Integrated Arms: When you perform a Muster action, you may muster Retinues and equipment from your Trade Partners' Pursuits (and their Mastery Effects, if active), paying their cost.",
        'pair': 'Forge, Advanced Blast Furnace',
        'complement': 'Royal Pavilion',
    },
    'The Velvet Hand': {
        'final_cut': False,
        'inspiration': 'Patrons',
        'feel': 'Generous Sponsor',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic': 'Friends in High Places: At the start of the turn, a player who supported an Envoy you sent that passed gains Faith +1; if that Envoy was endorsed, they Extort 500 gold per Era.',
        'pair': 'Aristocratic Court, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Ashen Vale': {
        'final_cut': True,
        'inspiration': 'Plague',
        'feel': 'Sickly',
        'difficulty': 'High',
        'strength': 'Low',
        'mechanic': "Pestilence: Each bordering player gains Doubt +1. Your Settlements have Reach +1, and all your Retinues have Poison. You can't pursue an Apothecary, Infirmary, or Hospitaller.",
        'pair': "Thieves' Guild, Inquisitorial Palace",
        'complement': 'Royal Pavilion',
    },
    'The Broken Banner': {
        'final_cut': False,
        'inspiration': 'Mercenary',
        'feel': 'Always for Sale',
        'difficulty': 'High',
        'strength': 'Low',
        'mechanic': "The Highest Bidder: You can't Declare War and can't be the target of a Declare War action. Each turn, you must sign the Military or Defensive Alliance offered by the highest-bidding player, and must be paid each turn. To overturn your current Alliance, a player must pay more than the prior agreement. You can't sign or end Alliances via a Diplomacy action.",
        'pair': 'Royal Pavilion, Forge',
        'complement': 'Senate Hall',
    },
    'The Forked Tongue': {
        'final_cut': True,
        'inspiration': 'Deceptive',
        'feel': 'Two-Faced',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic': 'Masters of Duplicity: You may hold any number of Treaties at once with any number of players, even contradictory ones. Your Treaties are never automatically canceled or voided by game events. When something would normally force a Treaty to cancel, you choose which obligation to honor and keep all your other Treaties intact. Other players may still End Treaty with you.',
        'pair': "Thieves' Guild, Senate Hall",
        'complement': 'Royal Pavilion',
    },
    'The Hall of Masks': {
        'final_cut': False,
        'inspiration': 'Doppelganger',
        'feel': 'Shifting Identity',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic': "Mimic: At the start of each turn, choose another player's Faction; you have that Faction this turn. You can't choose that same Faction next turn.",
        'pair': 'Studium Generale, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Smoldering Crown': {
        'final_cut': True,
        'inspiration': 'Terrorists',
        'feel': 'Aggressive, Destructive',
        'difficulty': 'High',
        'strength': 'Medium',
        'mechanic': "Reckless: Your Cunning Envoys have Influence +2 when targeting a player with Public Order above 0. You begin the game with a Secret Cellar (no Ward, no upkeep, always-active Mastery). You can't be in an Alliance and can't perform Diplomacy actions. A Prowess Envoy you send can't fail — if it would be condemned, it passes instead.",
        'pair': "Thieves' Guild, Inquisitorial Palace",
        'complement': 'Royal Pavilion',
    },
    "The Squatters' Crown": {
        'final_cut': False,
        'inspiration': 'Insurgents',
        'feel': 'Mobile Occupier',
        'difficulty': 'High',
        'strength': 'Medium',
        'mechanic': "Occupy: You start with an additional Army; all your Armies begin inside your Settlements. While you're outside a Settlement, you don't control it — to collect taxes or use its Pursuits, end your turn inside it. To Occupy a Settlement, begin a Battle adjacent to it as if Sieging, but instead Battle the Garrison and any Armies at War with you or sharing its owner; if you win (or there's no force to fight), move inside. In the Upkeep Phase, pay upkeep only on equipment. You count as having all Infrastructure of your Occupied Settlements, and always count as 3 Trading Pursuits. When you leave a Settlement, you can't re-enter it until you Occupy another Settlement and sign a Trade Agreement.",
        'pair': 'Royal Pavilion, Saddlery',
        'complement': 'Forge',
    },
    'The Wandering Crown': {
        'final_cut': True,
        'inspiration': 'Nomadic',
        'feel': 'Nomads',
        'difficulty': 'High',
        'strength': 'Medium',
        'mechanic': "Wandering Nomads: Your Armies function as Settlements — a Band, Tribe, or Horde, upgraded accordingly — count as Settlements with Reach 3, and each has a Muster Field. You may have one additional Army per Era, starting with two. Your Armies don't require troops to exist and can't be besieged. You can't build Infrastructure, but may build Pursuits; Raw Material Pursuits within Reach are always active and take no Settlement Ward. You may trade so long as your border touches another player's. You may begin a new Army adjacent to any existing Army with a Charter Settlement or Muster Army action. When an Army is destroyed, so is its Settlement. Nomads pay no upkeep.",
        'pair': 'Saddlery, Royal Pavilion',
        'complement': 'Forge',
    },
    'The Dukedom': {
        'final_cut': True,
        'inspiration': 'The Game',
        'feel': 'King of the Castle',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic': "The Great Arbiter: The Duke begins the game trading with every player under a Non-Aggression Pact. The Duke can't join Alliances, perform Cunning actions, or Declare War. When a player Declares War on the Duke, that player's Trade Agreements, Non-Aggression Pacts, and Defensive Alliances are immediately and permanently voided (their Military Alliance stays intact), and every other player simultaneously Declares War on that player and their Military Alliance; none of these can be reinstated while At War with the Duke. The Duke sees all private actions, resolves player actions, and manages Bandit Mechanics. If the Duke is eliminated, the game ends. The Duke may optionally choose a Faction.",
        'pair': 'Senate Hall, Aristocratic Court',
        'complement': 'Royal Pavilion, Imperial Palace',
    },
    'The Elder Grove': {
        'final_cut': True,
        'inspiration': 'Elves',
        'feel': 'Cautious Quickfighters',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': "Wise & Suspicious: Gain Doubt +1. While your Public Order is 1 or higher, your Armies have +1 Initiative, Steady, and Speed +1. You can't be in an Alliance.",
        'pair': 'Forge',
        'complement': 'Inquisitorial Palace',
    },
    'The Yew Heart': {
        'final_cut': True,
        'inspiration': 'English Longbows',
        'feel': 'Skilled Volleys',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic': "Archery is a Way of Life: You begin the game with a Fletchery (no Ward, no upkeep, always-active Mastery that can't be deactivated). Your Armies must always equip a ranged weapon, and Ranged Weapons have +1 to Strike. Your Armies can't equip full plate or articulated gothic plate, can't use shields, and can't build a Preceptory of Knight's Templar.",
        'pair': 'Royal Pavilion',
        'complement': 'Senate Hall',
    },
}


# ── INFRASTRUCTURE & WONDERS ───────────────────────────────────────────────
# Empire-level builds (per-settlement infrastructure + unique Wonders).
# Master source — edit HERE; reference sheets are generated from these dicts.
# Tiered upkeep/build values (e.g. '50/100/200') are strings.
INFRASTRUCTURE = {'Dirt Roads': {'upkeep': 0,
                'upkeep_frequency': '—',
                'empire_bonus': 'Can Trade; If you start a Move action within Province, gain Speed +1',
                'tier': 'Primitive',
                'build_time': 2,
                'requirement': 'None'},
 'Hitching Post': {'upkeep': 0,
                   'upkeep_frequency': '—',
                   'empire_bonus': 'Craft +1',
                   'tier': 'Primitive',
                   'build_time': 2,
                   'requirement': 'None'},
 'Muster Field': {'upkeep': 200,
                  'upkeep_frequency': 'per Turn',
                  'empire_bonus': 'Can Muster',
                  'tier': 'Primitive',
                  'build_time': 2,
                  'requirement': 'None'},
 'Wooden Walls': {'upkeep': 200,
                  'upkeep_frequency': 'per Turn',
                  'empire_bonus': '**Influence -2** to **Raze actions** from players targeting your **settlements**. **Influence -1** to Bandit **Cunning actions** targetting your **settlements**.',
                  'tier': 'Primitive',
                  'build_time': 2,
                  'requirement': 'None'},
 'Stone Roads': {'upkeep': 200,
                 'upkeep_frequency': 'per Turn',
                 'empire_bonus': 'If you start a Move action within Province, gain additional Speed +1',
                 'tier': 'Developed',
                 'build_time': 3,
                 'requirement': 'Dirt Roads'},
 'Town Hall': {'upkeep': 200,
               'upkeep_frequency': 'per Turn',
               'empire_bonus': '+1 Influence per turn',
               'tier': 'Developed',
               'build_time': 3,
               'requirement': 'One Tier Primitive'},
 'Bridges': {'upkeep': 0,
             'upkeep_frequency': '—',
             'empire_bonus': 'Armies cross Water Territory at full movement within Province; Stone Roads may be built over '
                             'Water',
             'tier': 'Developed',
             'build_time': 3,
             'requirement': 'One Tier Primitive + Stone Roads'},
 'Garrison': {'upkeep': '300',
              'upkeep_frequency': 'per Turn',
              'empire_bonus': 'Local Armies form (10/15/25/50 by Settlement size). All Garrisons share '
                              "Equipment. Can't be targeted; may Sally Forth.",
              'tier': 'Developed',
              'build_time': 3,
              'requirement': 'Muster Field'},
 'Stone Walls': {'upkeep': 300,
                 'upkeep_frequency': 'per Turn',
                 'empire_bonus': '**Influence -2** to **Destabilize actions** from players targeting your **settlements**. **Influence -1** to Bandit **Cunning actions** targetting your **settlements**.',
                 'tier': 'Sophisticated',
                 'build_time': 4,
                 'requirement': 'One Tier Developed + Wooden Walls'},
 'Keep': {'upkeep': 300,
          'upkeep_frequency': 'per Turn',
          'empire_bonus': 'May Muster from Garrison in addition to normal Muster Limits. If so set Garrison '
                          'to 0 and Muster Timer 1. Garrison returns to full when resolved.',
          'tier': 'Sophisticated',
          'build_time': 4,
          'requirement': 'Garrison'},
 'Cathedral': {'upkeep': 300,
               'upkeep_frequency': 'per Turn',
               'empire_bonus': 'Faith +2',
               'tier': 'Sophisticated',
               'build_time': 4,
               'requirement': 'Requires Capital City'},
 'Library': {'upkeep': 300,
             'upkeep_frequency': 'per Turn',
             'empire_bonus': 'Influence +1 to Council Envoys',
             'tier': 'Sophisticated',
             'build_time': 4,
             'requirement': 'Town Hall'}}

WONDERS = {'Colossus': {'upkeep': 500,
              'upkeep_frequency': 'per Wonder',
              'empire_bonus': 'You may **support** your own **prowess envoys** before other **players '
                              'vote**. **Armies** move **Speed +2**, **Siege Timer -2**, & gain **Immune '
                              'Blunder**.',
              'tier': 'Wonder',
              'build_time': 10,
              'requirement': 'All Infrastructure unlocked'},
 'The Grand Exchange': {'upkeep': 500,
                        'upkeep_frequency': 'per Wonder',
                        'empire_bonus': 'Whenever you generate **Trade Income** you generate **twice as '
                                        'much** for yourself.',
                        'tier': 'Wonder',
                        'build_time': 10,
                        'requirement': 'All Infrastructure unlocked'},
 'The Great Basilica': {'upkeep': 500,
                        'upkeep_frequency': 'per Wonder',
                        'empire_bonus': 'If your **Public Order** would ever be less than 5 set it to 5 '
                                        'instead. Your **Settlements** gain **Reach +1**.',
                        'tier': 'Wonder',
                        'build_time': 10,
                        'requirement': 'All Infrastructure unlocked'},
 'High Chancery': {'upkeep': 500,
                   'upkeep_frequency': 'per Wonder',
                   'empire_bonus': 'Once per turn: automatically **Condemn** or **Endorse** one Envoy Sent '
                                   'by any other player regardless of **Net Influence** after Influence has '
                                   'been spent, even if it’s a Council Envoy.',
                   'tier': 'Wonder',
                   'build_time': 10,
                   'requirement': 'All Infrastructure unlocked'}}
# ── EMPIRE RULES (ingested from Rules.docx — new data, nothing replaced) ─────
# Settlement tiers: tax is the WINTER collection (once per 4 turns); wards =
# pursuit slots (1 per tier; Hamlet exception); muster = retinues/turn.
SETTLEMENTS = {
    "Hamlet":     {"tier": 0, "sea_variant": None,        "tax_income": 0,     "muster_limit": 0,  "build_time": 1, "wards": 3, "reach": 1, "notes": "Husbandry pursuits only; exactly range 2 from capital; may always pursue Arable Land"},
    "Village":    {"tier": 1, "sea_variant": None,        "tax_income": 1000,  "muster_limit": 5, "build_time": 1, "wards": 1, "reach": 1, "notes": ""},
    "Town":       {"tier": 2, "sea_variant": "Sea Town",  "tax_income": 3000,  "muster_limit": 10, "build_time": 2, "wards": 2, "reach": 2, "notes": ""},
    "City":       {"tier": 3, "sea_variant": "Port",      "tax_income": 5000,  "muster_limit": 25, "build_time": 3, "wards": 3, "reach": 3, "notes": ""},
    "Metropolis": {"tier": 4, "sea_variant": "—",         "tax_income": 8000, "muster_limit": 25, "build_time": 5, "wards": 4, "reach": 4, "notes": "Capital only, requires Sovereign Industry (Titan of Industry)"},
}

# Era progression: shared-Renown thresholds; caps on armies/cities; influence.
ERAS = {
    "Founding":  {"renown": 1,  "armies": 1, "cities": 0, "max_settlements": 3, "influence_per_turn": 1, "innate_diplomacy_influence": 1, "envoys": "1 Council + 1 Personal Envoy per turn", "unlocks": ""},
    "Ascension": {"renown": 8,  "armies": 2, "cities": 1, "max_settlements": 4, "influence_per_turn": 2, "innate_diplomacy_influence": 2, "envoys": "Council Envoys perform 2 actions of that domain", "unlocks": "May resolve Charter Cities"},
    "Eminence":  {"renown": 18, "armies": 3, "cities": 2, "max_settlements": 5, "influence_per_turn": 3, "innate_diplomacy_influence": 3, "envoys": "Personal Envoys perform 2 actions of that domain", "unlocks": "May form Military Alliances"},
    "Zenith":    {"renown": 30, "armies": 4, "cities": 3, "max_settlements": 6, "influence_per_turn": 4, "innate_diplomacy_influence": 4, "envoys": "Send 2 Personal Envoys per turn", "unlocks": "May form Defensive Alliances"},
}

# Public Order track (−5..7): state name + effect.
PUBLIC_ORDER = {
    -5: ("Uprising",      "Bandit Camp spawns in your Outlaw Country"),
    -4: ("Recession",     "-1000 Tax Income per Settlement"),
    -3: ("Aimless",       "Speed -2"),
    -2: ("Indecisive",    "-1 Influence"),
    -1: ("Wavering",      "No effect"),
     0: ("Neutral",       "No effect"),
     1: ("Focused",       "No effect"),
     2: ("Confident",     "+1 Influence"),
     3: ("Motivated",     "Speed +1"),
     4: ("Economic Boom", "Tax income +500 per settlement"),
     5: ("Eureka",        "Activate 1 inactive Mastery until end of turn."),
     #6: ("Devout",        "+1 Influence"),
	 #7: ("Pious",         "Immune Deficit"),
	 #8: ("Holy",          "Immune to Spread Gospel"),
	 #9: ("Sanctified",    "Immune to Send Missionaries"),
    10: ("Living Saints", "Begin Pious Timer Edict"),
}

# Innate Faith/Doubt sources (per turn, applied at the Public Order step).
PO_MODIFIERS = {
    "faith": {
        "Lasting Legacy":  "Most recent Battle was Won",
        "Restored Order":  "Destroyed a Bandit Camp last turn",
    },
    "doubt": {
        "Local Unrest":    "Per active Bandit Camp in your Territory",
        "Deficit":         "Net Income is negative",
        "Insolvency":      "Per consecutive Upkeep Phase with negative Treasury",
        "Border Tension":  "Per other player Army in your Territory (not Alliance or NAP)",
        "Invasion":        "Additional per other player Army in your Territory at War",
        "State of Alarm":  "If at War",
        "Mounting Panic":  "Per Settlement being Besieged",
		"War Weariness":    "Per consecutive Battle loss"
    },
}

# Domain board: empire-side standing effects (combat-side lives in STANDING_EFFECTS).
DOMAIN_BOARD = {
    "Industry": {
        "Rising":      "Trade Secrets: Perform endorsed Pursuit.",
        "Established": "Grand Architect: May have an additional City. Perform endorsed Charter.",
        "Sovereign":   "Titan of Industry: Your capital may be chartered to a Metropolis. Perform endorsed Charter.",
    },
    "Prowess": {
        "Rising":      "Indomitable: Once per turn, if you have not sent a Personal Envoy, you may instead perform a Prowess action; send 1 fewer Envoy this turn (min 0). In addition, may use Declare War action.",
        "Established": "Edict of War: May have an additional Army. Perform a Muster Action.",
        "Sovereign":   "High Quartermaster: Upkeep -2000. May change equipment on your armies during any upkeep phase where that army is within Province. No longer lose Influence while at War.",
    },
    "Cunning": {
        "Rising":      "Clandestine Councilor: Once per Envoy Phase, during a vote on an Envoy, target a player - that player Abstains that Envoy.",
        "Established": "Grand Vizier: Players may not target you with Cunning Envoys if your Cunning value is higher.",
        "Sovereign":   "Master Conspirator: Once per turn, if your non-Cunning Envoy passes or is Endorsed, you may instead perform a Cunning action.",
    },
    "Piety": {
        "Rising":      "Divine Mandate: Faith +1 each Empire Phase.",
        "Established": "One True Gospel: Each Empire Phase, all other non-allied players with a lower Piety value gain Doubt +2.",
        "Sovereign":   "Pillar of Faith: If your Public Order would be set below 3, set it to 3. In addition, may use the Crusade action.",
    },
    # Influence scaling by standing (Untested/Rising/Established/Sovereign):
    "max_influence_per_vote":  {"Untested": 1, "Rising": 2, "Established": 3, "Sovereign": 4},
    "innate_influence_own_envoys": {"Untested": 1, "Rising": 2, "Established": 3, "Sovereign": 4},
}

# Seasons (turn cycle of 4; Rest Phase advances Season +1).
SEASONS = {
    "Winter": {"name": "Freezing",    "effect": "All Armies gain Speed -1; Sieges do not increment. Tax income collected."},
    "Spring": {"name": "Planting",    "effect": "No Host, Bandit Mechanics, Trade Income, Council Phase, or Diplomacy Actions. Gain +1 Envoy. Bandit Camps Spawn."},
    "Summer": {"name": "Campaigning", "effect": "All Armies gain Speed +2"},
    "Fall":   {"name": "Harvest",     "effect": "Husbandry Mastery Effects are doubled."},
}

# Trade & income constants (Rules: Trade & Income Rules).
TRADE_RULES = {
    "income_per_craft": 100,                # Trade Income = 100 x host's Craft X, per active agreement
    "requirements": "Players must have active Dirt Road infrastructure, and a signed Trade Agreement",
    "no_trade_season": "Spring",            # no trade income in Spring
    "tax_season": "Winter",                 # tax collected only in Winter
}


# ── Efficient graph (canonical) ──────────────────────────────────────────────
# Source of truth = each node's `efficient` FIELD (str for one target, list for
# Energy multi-targets). Direction is builder -> raw (the node holding the field
# stacks INTO the named target's ward). Card/Compendium render it as "Efficient X".
def efficient_graph():
    """Return {node: [targets]} from the `efficient` field on each NODES entry."""
    out = {}
    for n, v in NODES.items():
        e = v.get("efficient")
        if not e:
            continue
        out[n] = [e] if isinstance(e, str) else list(e)
    return out

EFFICIENT_MULTI = efficient_graph()                       # {node: [targets]}
EFFICIENT = {n: t[0] for n, t in EFFICIENT_MULTI.items()} # first target (1-partner view)

# ============================================================================
# COMPENDIUM-SOURCED ADDITIONS (non-combat) — bandits, timers, influence, terms
# Values transcribed verbatim from Compendium-Updated.docx. Combat keywords
# (Regenerate/Steadfast/Unshakable/Shaking Test/Tripped/Maximum Endurance) are
# intentionally excluded as deprecated relative to the combat model above.
# ============================================================================
BANDIT_CAMP_START = 5
BANDIT_ARMY_THRESHOLD = 25
BANDIT_GROWTH_PER_ERA = {"Founding": 1, "Ascension": 2, "Eminence": 3, "Zenith": 4}
BANDIT_EQUIPMENT_PER_ERA = {"Founding": "Cudgel + Cloth", "Ascension": "Arming Swords, Target Shields, & Leather Armor" , "Eminence": "Halberds + Chainmail", "Zenith": "Battle Axes + Full Plate"}
BANDITS = {
    "Bandit Domain Value": "For every 5 Retinues in the Bandit Camp or Army, the Bandit Camp has +2 Cunning and +2 Prowess.",
    "Bandit Camp": f"A collection of Bandits in Outlaw Country, starting with {BANDIT_CAMP_START} Retinues.",
    "Bandit Growth": f"Bandit Camps gain ({'/'.join(str(v) for v in BANDIT_GROWTH_PER_ERA.values())}) Retinues a turn, based on the Era of the Realm.",
    "Bandit Army": f"A Bandit Camp becomes a Bandit Army at {BANDIT_ARMY_THRESHOLD} Retinues. Performs Move actions toward the closest Settlement or Army, laying Siege or Skirmishing if possible, in addition to Bandit Cunning Mechanics. Bandit Armies cannot exceed {BANDIT_ARMY_THRESHOLD}",
    "Spawn a Bandit Camp": "Each Spring, every player gains a Bandit Camp. When a Bandit Camp is spawned in Spring, it immediately performs a Raze action at a base influence of 1 targetting the closest settlement.",
}

TIMERS = {
    "Build Timer":   {"where": "Infrastructure / Settlement Wards / Pursuits", "default": None, "tracks": "Turns until an infrastructure/build completes and becomes Active."},
    "Repair Timer":  {"where": "Damaged Pursuits / Infrastructure", "default": 2, "tracks": "Turns until a Damaged piece is repaired and its effects return."},
    "Truce Timer":   {"where": "Treaties / diplomacy outcomes", "default": 5, "tracks": "Turns remaining until a Truce expires (and related diplomacy restrictions end)."},
    "Siege Timer":   {"where": "Lay Siege", "default": None, "tracks": "Turns remaining until a Siege resolves."},
    "Muster Timer":  {"where": "Muster effects (e.g., Garrison timing)", "default": 1, "tracks": "Turns remaining until Recruited Retinues become Active (or until a temporary Muster state ends)."},
    "Sack Timer":    {"where": "After Sacking a Settlement", "default": 2, "tracks": "Cooldown before the same force may Lay Siege again (per Sack rules)."},
    "Capture Timer": {"where": "Capturing a Settlement after Siege", "default": 1, "tracks": "Turns until a Captured Settlement becomes Controlled by the Player with the Capture Timer and applies the listed capture effects."},
    "Convert Timer": {"where": "Convert (Piety action)", "default": None, "tracks": "Turns until a Convert attempt resolves (or fails early if conditions change)."},
}

# ── Chartering / map placement constants (prose-only before; tunable balance) ──
CHARTER_MIN_RANGE   = 4   # min range a new settlement must be from any other settlement
OUTLAW_BUFFER_RANGE = 2   # new settlements must be at least this far from Outlaw Country
HAMLET_RANGE        = 2   # exact range a Hamlet sits from the capital
OUTLAW_COUNTRY_START = 3  # Outlaw Country territories demarcated at game start

# ── Vassalage ─────────────────────────────────────────────────────────────────
VASSAL_EXCHANGE_CAP = 5000  # max gold a Suzerain/vassal may exchange per Empire Phase
VASSAL_INFLUENCE_TAKE = 3   # first N Influence the vassal generates each turn goes to Suzerain


# Build durations in turns. Infrastructure keyed by its tier name.
BUILD_TIMERS = {
    "Pursuit": 1,
    "Power Pursuit": 2,
    "Monument Pursuit": 3,
    "Village": 1,
    "Hamlet": 1,
    "Town": 2,
    "City": 3,
    "Metropolis": 5,
    "Wonder": 10,
    "Repair": 2,
    "Infrastructure": {"Primitive": 2, "Developed": 3, "Sophisticated": 4},
}

TERRAIN = {
	"Grassland": {"Effect": "—", "Raw Materials": ["Arable Land", "Apiary"]},
	"Wetlands": {"Effect": "Speed -1", "Raw Materials": ["Peat Bog", "Forestry"]},
	"Tundra": {"Effect": "gain Strained", "Raw Materials": ["Quarry", "Salt Works"]},
	"Mountains": {"Effect": "Impassable", "Raw Materials": ["Mine"]},
	"Water": {"Effect": "Must end move after moving over 1 Water Territory (must end on land)", "Raw Materials": ["Fishmongery"]},
	"Forest": {"Effect": "Speed -1", "Raw Materials": ["Forestry","Apiary"]},
	"Hill":  {"Effect": "Gains Seize the Initiative. Where Settlements can be chartered."},
}

MOVEMENT_MODIFIERS = {
	"Dirt Roads" : {"Effect": "Immune Speed -1 from Terrain"},
	"Stone Roads" : {"Effect": "Immune Speed -1 from Terrain. Gain Speed +2"},
	"Bridge" : {"Effect": "Immune Water Effect."},
	"Tunneler": {"Effect": "Immune Mountain Effect"},
	"Ancient Wilds": {"Effect": ["Immune Speed -1 from Terrain", "Other armies gain Speed -1 in Province."]},
	"Shipyard": {"Effect": "Immune Water Effect"}
}

# ── TACTICAL TERRAIN (battle-tile modifiers for the skirmish board) ──
# Seize the Initiative precedence (highest first): Ministry of Military
# Strategy > Hill > Forest (defender) > general rule (attacker).
TACTICAL_TERRAIN = {
    "Hill":       {"identify": "Grassland fully ringed by grassland",
                   "effect": "An army on a Hill Seizes the Initiative every Skirmish."},
    "Open Field": {"identify": "Any other grassland",
                   "effect": "Ranged Weapons gain +1 to Strike."},
    "Forest":     {"identify": "Forest",
                   "effect": "You may only play Scout, Ambush, Flank, or Defensive Formation. The defending player Seizes the Initiative."},
    "Mire":       {"identify": "Wetlands",
                   "effect": "Gain Unwieldy and Immune Steady; -1 to Save."},
    "Tundra":     {"identify": "Tundra",
                   "effect": "Gain Strained."},
    "Mountains":  {"identify": "Mountains",
                   "effect": "Impassable."},
    "Water":      {"identify": "Water",
                   "effect": "Must end Move after moving 1 Water Territory. Cannot Skirmish or Siege move."},
}
TACTICAL_GLOBAL = ["Any player may Fall Back after the first Skirmish."]

INFLUENCE_GAIN = {
    "Era": {"change": "+1/+2/+3/+4", "notes": "Based on the Current Era"},
    "Trading Partners": {"change": "+1", "notes": "Per Trading Partner."},
    "Alliances": {"change": "+1", "notes": "Per Alliance Member."},
    "Infrastructure tier completed": {"change": "+1", "notes": "Per Infrastructure tier fully completed."},
    "Cunning Standing": {"change": "+1", "notes": "per unlocked Cunning Standing."},
    "Fully Mustered Army": {"change": "+1", "notes": "Per active Army of 25 Retinues."},
    "Condemned Envoy last turn": {"change": "-1", "notes": "Per Condemned Envoy last turn."},
    "At War": {"change": "-3", "notes": "While at War."},
    "Monuments & Wonders": {"change": "+1", "notes": "Per active Monument or Wonder."},
    "Other sources": {"change": "+X", "notes": "From other effects like Pursuits."},
}

# --- Glossary additions (map/spatial, action, and outcome terms) ---
GLOSSARY.update({
    "Border": "Your Settlement's Reach is Range 1 or within Reach of another Player's Reach.",
    "Province": "The collection of Contested Territory and Controlled Territory by your Settlement's Reach.",
    "Region": "A collection of Territories of the same Type.",
    "Realm": "The total collection of Regions.",
    "Territory": "1 Hex.",
    "Contested": "Territory that is within Reach of more than one player's settlement(s). Considered Controlled by all Players that have a Settlement within Reach.",
    "Controlled": "Territory that is within Reach of a single Player's Settlement(s).",
    "Uncontrolled": "Territory that is not within Reach of any Player Settlement.",
    "Adjacent": "Range 1.",
    "Next to": "Range 2.",
    "Within": "Range 0.",
    "Range X": "The amount of Territories you must move in order to get from your current position to the specific Territory.",
    "Reach X": "The Range X characteristic which determines what Territories you Control and are in your Province.",
	"Host": "The turn's starting player, who holds the Host Card. The role passes clockwise each Rest Phase (there is no Host in Spring). The Host collects and distributes Trade Income, resolves Bandit Mechanics, and breaks ties (Council vote, bandit targeting, and any tie not otherwise resolved).",
    "Send an Envoy": "Declare a Domain, spend 1 Envoy.",
    "Perform": "When you Perform an action, immediately do the description of the action. Pay the action's normal Cost.",
    "Resolve": "Attempt to Perform an action.",
    "Cost / Pay": "Cost to perform an action, usually in Gold or Doubt.",
    "Fail": "An unsuccessful to Hit or to Save.",
    "Failed": "Net Influence 0 or less.",
    "Passed": "Net Influence 1 or more.",
})
# ============================================================================
# NEW STRUCTURES — paste into renown_data.py and modify as needed.
# Built from RULES.md (v0.4.8.3.1). Schemas chosen to be generator-friendly:
# the wiki / FAQ / compendium can iterate these the same way they do NODES.
# ============================================================================




# ── ENVOY OUTCOMES ───────────────────────────────────────────────────────
# Resolution bands for a Sent Envoy, by Net Influence (starting Influence by
# Standing + all Support/Oppose/Influence X):
#   Condemned : Net <= -3   (resolve the domain's Condemn effect)
#   Failed    : Net <= 0     (gain Doubt 1)
#   Passed    : Net >= 1
#   Endorsed  : Net >= <THRESHOLD?>   (Passed + the domain's endorsed bonus)
ENVOY_OUTCOME_THRESHOLDS = {
    "Condemned": -3,   # Net Influence <= -3
    "Failed":     0,   # Net Influence <= 0  (and > -3)
    "Passed":     1,   # Net Influence >= 1
    "Endorsed":   3,  
}
# Per-domain effect at each outcome band. Prowess Condemn is a combat penalty
# (Strain; if already Strained, no Move this turn or next) rather than Doubt+Cost,
# since Prowess actions carry no gold/doubt cost.
ENVOY_OUTCOMES = {
    "Prowess":   {"condemned": "Doubt 1 + Armies gain Strain; if already Strained, that army cannot perform a Move action this turn or next.",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Perform a Move action"},
    "Cunning":   {"condemned": "Doubt 1 + pay the action's cost",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Extort 2000"},
    "Piety":     {"condemned": "Doubt 1 + pay the action's cost",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Faith 1"},
    "Industry":  {"condemned": "Doubt 1 + pay the action's cost",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Recoup 2000"},
    "Diplomacy": {"condemned": "Doubt 1 + pay the action's cost",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Perform a Diplomacy action"},
}


# ── ACTIONS ─────────────────────────────────────────────────────────────────
# Every Envoy action, by domain. Fields:
#   domain   : Prowess | Cunning | Piety | Industry | Diplomacy
#   cost     : gold/doubt/None cost to perform (string, as written)
#   requires : standing or other gate to send ("" = none)
#   effect   : the "if passes" description (concise)
#   endorsed : the endorsed bonus
#   notes    : list of rules notes (sub-clauses)
ACTIONS = {
    'Move': {
        'domain': 'Prowess',
        'cost': 'None',
        'requires': '',
        'effect': 'Move an Army up to its Speed in Territories. Then choose one: March — move up to 2× Speed, lose 1 Endurance, take no other action; Battle — end adjacent to a non-allied Army not in a Settlement, then begin a Battle; Lay Siege — end adjacent to an at-war Settlement, then begin a Siege; Muster — end within range 2 of your Settlements, not within range 1 of a non-ally, at an active Muster Field, then recruit up to your combined muster limit (you may swap Retinues between adjacent allied Armies and change equipment).',
        'endorsed': 'Perform another Move action (same or a different Army).',
        'notes': ['An Army may be the target of only one Move action per turn.', "While an Army's Battle, Siege, or Muster Timer is running, it can't be the target of actions.", "When an Army performs the Battle mode, it has Seize the Initiative in that Battle's first Skirmish."],
    },
    'Declare War': {
        'domain': 'Prowess',
        'cost': 'None',
        'requires': 'Rising Prowess',
        'effect': 'Choose a non-allied player you have no NAP or active truce with. You and that player are now At War, and any Trade Agreements between you end. If the target is in a Defensive Alliance, every member is now At War with you.',
        'endorsed': 'Perform a Move action.',
        'notes': ['If you are in a Military Alliance, then at the start of your next turn every member Declares War on the target and sends 1 fewer Envoy that turn.'],
    },
    'Demand Tribute': {
        'domain': 'Prowess',
        'cost': 'None',
        'requires': '',
        'effect': 'Choose a non-allied player you have no NAP with, then negotiate terms. If the target agrees, sign a NAP or Alliance (the target picks among the offered terms). If the target refuses, or later fails to meet the terms, immediately Declare War on them.',
        'endorsed': 'Perform a Move action.',
        'notes': ['Terms may include gold, Settlements, Territory, Treaties, or promises. A promise is unenforceable, but breaking one counts as failing the terms.'],
    },
    'Intercept Caravan': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': 'Choose a player. The next turn that player is Host, Extort their Trade Income.',
        'endorsed': 'Extort 2000.',
        'notes': ["This affects only a single turn's trade income; normal income resumes afterward."],
    },
    'Foster Rebellion': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': 'Choose a player. At the next Bandit Mechanics step, place a Bandit Camp of 10 Retinues in their Outlaw Country.',
        'endorsed': 'Extort 2000.',
        'notes': ["If that player's Outlaw Country has no room, expand it by one Territory and spawn there instead."],
    },
    'Raze': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': "Choose another player's Settlement, then choose one active Pursuit, active Infrastructure, or active Build Timer in it: that target becomes Damaged, and its effects are inactive until Repaired. A Damaged Build Timer doesn't increment until Repaired.",
        'endorsed': 'Extort 2000.',
        'notes': ["A Wonder has Immune Razed and can't be targeted."],
    },
    'Destabilize': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': 'Choose a player. In the next Extort step during Winter, Extort their Tax Income.',
        'endorsed': 'Extort 2000.',
        'notes': ["This affects only the next single turn's tax income, when it's collected."],
    },
    'Spread Gospel': {
        'domain': 'Piety',
        'cost': 'Doubt 1',
        'requires': '',
        'effect': 'Each non-allied player gains Doubt 1. Each allied player gains Faith 1.',
        'endorsed': 'Gain Faith 1.',
    },
    'Send Missionaries': {
        'domain': 'Piety',
        'cost': 'Doubt 1',
        'requires': '',
        'effect': 'Choose a target player or Alliance. If the target is outside your Alliance, each player in it gains Doubt 2. If the target is inside your Alliance, each other allied player gains Faith 2.',
        'endorsed': 'Gain Faith 1.',
    },
    'Tithe': {
        'domain': 'Piety',
        'cost': 'Doubt 1',
        'requires': '',
        'effect': 'Choose a player. Extort 10% of their Treasury (round down to the nearest 100, minimum 0).',
        'endorsed': 'Gain Faith 1.',
    },
    'Convert': {
        'domain': 'Piety',
        'cost': 'Doubt 1',
        'requires': '',
        'effect': "Choose another player's closest non-capital Settlement; its Public Order must be −5 or lower. Lay Siege using only Settlement-type Siege modifiers (Settlement Size and Citadel) and set a Convert Timer. When it reaches 0, the Settlement joins your empire (see Capture).",
        'endorsed': 'Gain Faith 1.',
        'notes': ["If the target's Public Order rises to 1 or higher before the timer reaches 0, the Convert fails and the timer is removed."],
    },
    'Crusade': {
        'domain': 'Piety',
        'cost': 'Doubt 1',
        'requires': 'Sovereign Piety',
        'effect': 'Declare War on a non-ally you have no NAP or truce with, then immediately perform a Move action with one of your Armies.',
        'endorsed': 'Gain Faith 1.',
        'notes': ['While a Crusade is active, neither player may Declare War on, Sign or End a Treaty with, Negotiate with, or Demand Tribute from the other.', 'You may have only one active Crusade at a time. It ends only when one of the two players is Vassalized or otherwise removed from the game.'],
    },
    'Build': {
        'domain': 'Industry',
        'cost': '2000 gold',
        'requires': '',
        'effect': 'Choose an unlocked, available Infrastructure and set a Build Timer equal to its build time. When it completes, the Infrastructure becomes active in every Settlement in your province.',
        'endorsed': 'Recoup 2000.',
        'notes': ['You must have at least one Infrastructure from the prior tier before building the next tier.', 'A Wonder is built in your capital and requires all other Infrastructure to be active when the Build action is performed.'],
    },
    'Repair': {
        'domain': 'Industry',
        'cost': '0 gold',
        'requires': '',
        'effect': 'Choose a Damaged Pursuit or Infrastructure in a Settlement you control and set Build Timer 2. When it reaches 0, choose one: Restore — reactivate it with all effects; Demolish — remove the Pursuit tile from your Empire Tableau.',
        'endorsed': 'Recoup 2000.',
    },
    'Pursue': {
        'domain': 'Industry',
        'cost': '2000 gold',
        'requires': '',
        'effect': 'Choose an inactive Settlement Ward you control, then choose a Pursuit whose prerequisites you meet and set a Build Timer equal to its build time (usually 1). When it completes, place the Pursuit in an available Ward slot; its innate effect activates immediately, and its mastery effect activates if all mastery requirements are met.',
        'endorsed': 'Recoup 2000.',
        'notes': ['You may have only 2 Monument Pursuits across your empire.', 'Power and unique Pursuits have Build Timer +1; Monuments +2; all others Build Timer 1.'],
    },
    'Charter': {
        'domain': 'Industry',
        'cost': '2000 gold',
        'requires': '',
        'effect': 'Choose one: Charter a new Village — on uncontrolled or in-province non-water, non-mountain Territory, range 4+ from any Settlement and range 2+ from Outlaw Country; or Expand a non-City Settlement one tier into an adjacent Territory (Village to Sea/Town, Sea/Town to Port/City, Port/City to Metropolis), adding a Ward.',
        'endorsed': 'Recoup 2000.',
        'notes': ["To upgrade to City or Metropolis you must meet that tier's requirements; otherwise set Build Timer 1."],
    },
    'Sign Treaty': {
        'domain': 'Diplomacy',
        'cost': 'None',
        'requires': '',
        'effect': 'Ask players to agree, then choose one and both sign it: Peace Treaty — end the war, set Truce Timer 5; Trade Agreement — begin trading next turn; Non-Aggression Pact — no Declare War (ending it via End Treaty gives both Truce Timer 5); Alliance — join, form, or invite to a Defensive or Military Alliance.',
        'endorsed': 'Perform a Diplomacy action.',
        'notes': ['When acting on behalf of an Alliance, End Treaty requires all allies to agree.', "A player can't be in more than one Alliance."],
    },
    'Negotiate': {
        'domain': 'Diplomacy',
        'cost': 'None',
        'requires': '',
        'effect': 'Propose terms to a target; they agree or refuse. Terms may include gold, Settlement ownership, Territory, signing or ending a Treaty, or promises (non-binding).',
        'endorsed': 'Perform a Diplomacy action.',
        'notes': ['If a promise goes unfulfilled, the affected player may Declare War on the promiser.', 'Also used to resolve Demand Tribute and Siege surrenders.'],
    },
    'End Treaty': {
        'domain': 'Diplomacy',
        'cost': 'None',
        'requires': '',
        'effect': "Choose a target with whom you have an active Treaty and no active Truce Timer; remove that Treaty. The target doesn't need to agree.",
        'endorsed': 'Perform a Diplomacy action.',
    },
}

# ── TREATIES ────────────────────────────────────────────────────────────────
# The standing agreements players can hold. signed_via is the action; ended_via
# notes how it ends; era is when it unlocks (alliances scale with Era).
TREATIES = {
    "Peace Treaty":      {"signed_via": "Sign Treaty", "effect": "Ends war between the two players; sets Truce Timer 5.", "era": "Any"},
    "Trade Agreement":   {"signed_via": "Sign Treaty", "effect": "Begin trading (Trade Income flows from next turn). Requires bordering + active Dirt Road.", "era": "Any"},
    "Non-Aggression Pact": {"signed_via": "Sign Treaty", "effect": "Neither player may Declare War on the other. Ending it via End Treaty gives both a Truce Timer 5.", "era": "Any"},
    "Military Alliance":  {"signed_via": "Sign Treaty", "effect": "Mutual offensive pact: if a member Declares War, all members Declare War on the target next turn (and send 1 fewer envoy).", "era": "Eminence"},
    "Defensive Alliance": {"signed_via": "Sign Treaty", "effect": "Mutual defense: attacking one member puts all members at war with the attacker.", "era": "Zenith"},
}
# General alliance rules (prose, surfaced for the wiki):
ALLIANCE_RULES = [
    "New alliance members are added by unanimous agreement.",
    "A player cannot be in more than one alliance at a time.",
    "An alliance may remove a member via End Treaty if all others agree.",
]

# ── EDICTS / WIN CONDITIONS ──────────────────────────────────────────────────
# Completing an Edict raises the Renown tracker by 1. Any Edict may be completed
# multiple times. Whoever has completed the most when the Last Alliance Standing
# condition is met wins.
EDICTS = {
    "Sovereign Standing": {"type": "Standing",  "requirement": "Reach a Sovereign Standing (Domain value 10) in any Domain."},
    "Monument":           {"type": "Build",     "requirement": "Have an active Mastery Effect of a Monument pursuit."},
    "Wonder":             {"type": "Build",     "requirement": "Complete a World Wonder."},
    "Wealth":             {"type": "Economy",   "requirement": "Generate 5,000 gold per turn for five consecutive turns, net Upkeep costs."},
    "Vassalize":          {"type": "Conquest",  "requirement": "Vassalize a rival player (control their capital with no other settlements/armies under them)."},
    "Living Saints":      {"type": "Piety",     "requirement": "Sustain Public Order 10 (Living Saints) for five consecutive turns (Pious Timer)."},
    "Last Alliance Standing": {"type": "Endgame", "requirement": "Be the last alliance standing — the game-ending stop condition."},
}
# Note: consecutive-turn Edicts require the timer to increment each turn; if it
# fails to increment for any reason, remove the timer until restarted.

# ── BANDIT BEHAVIOR ──────────────────────────────────────────────────────────
# Extends BANDITS with the Cunning-mechanic + army-behavior tables from Rules.
BANDIT_BEHAVIOR = {
    "Renown":        "Bandits share the Realm's Renown level.",
    "Domain Value":  "+2 Cunning and +2 Prowess per 5 retinues in the camp (e.g. 25 retinues = 10 Cunning = Sovereign).",
    "At War":        "All players are At War with all bandits. Players Abstain all bandit actions, but innate modifiers can still cause them to Fail.",
    "Cunning Roll":  "If 10+ retinues in camp, roll a d3 each turn: 1 = Intercept Caravan, 2 = Raze, 3 = Destabilize.",
    "Treasury":      "Bandit camps keep Extorted gold in their treasury and pay no costs or upkeep. Destroying a camp/army Extorts its treasury.",
    "Army Behavior": "After bandit mechanics, a Bandit Army performs a Move: Skirmish (player army in range) > Lay Siege (player settlement in range) > March (toward closest army/settlement). Host breaks range ties.",
    "Attacking":     "Move to end adjacent to a camp; another player rolls bandit tactics (D{FACES}; a Focused result = Fall Back) and resolves to-strike/save as a Battle. Bandits never Fall Back but may Flee. Extort the camp's gold if destroyed.",
}

# ── UPKEEP — THREE SEPARATE TRACKS ────────────────────────────────────────────
# Renown has three distinct upkeep pools, each reduced by different effects.
# Keep them straight: a reducer that names one track does NOT touch the others.
#
# 1) PURSUIT upkeep  — fixed by pursuit type (below). Zeroed for Civic pursuits
#    by the Luminous Court faction. Not touched by "Upkeep -X" or Trade Guild.
# 2) ARMY upkeep     — retinue count x (retinue cost - "Upkeep -X" modifiers).
#    The "Upkeep -200 / -300 / -500" effects (Levy Hall, Tannery, Armory,
#    Saddlery, Butchery, Fletchery, Smokehouse, ABF) and High Quartermaster
#    (-2000) reduce the per-retinue cost here.
# 3) INFRASTRUCTURE upkeep — the per-settlement upkeep in INFRASTRUCTURE.
#    Trade Guild removes upkeep on Primitive (innate) and Developed (mastery)
#    infrastructure; College of Engineering removes it on Sophisticated.
UPKEEP_TRACKS = {
    "Pursuit":        "Fixed by pursuit type: Monument 300, Power 200, Energy 0, all others 0. Luminous Court zeroes Civic-pursuit upkeep.",
    "Army":           "Σ(retinue costs x army) - Upkeep -X. Reduced by Levy Hall (-200/-300), Tannery/Armory/Saddlery/Butchery/Fletchery/Smokehouse (-200), ABF (-500), High Quartermaster (-2000).",
    "Infrastructure": "Per-Empire upkeep in INFRASTRUCTURE. Trade Guild removes Primitive (innate) + Developed (mastery); College of Engineering removes Sophisticated.",
}

# 1) PURSUIT upkeep — fixed by type.
PURSUIT_UPKEEP_BY_TYPE = {
    "Monument": 300,
    "Power":    200,
    "Energy":   0,
}
PURSUIT_UPKEEP_DEFAULT = 0

def pursuit_upkeep(node):
    """Per-turn upkeep for a node, fixed by its type. node = a NODES entry (dict) or a type string."""
    t = node.get("type") if isinstance(node, dict) else node
    return PURSUIT_UPKEEP_BY_TYPE.get(t, PURSUIT_UPKEEP_DEFAULT)

# 2) ARMY upkeep — formula note (per-retinue costs in RETINUES[*]["cost"]).
ARMY_UPKEEP_NOTE = "Net Army Upkeep = retinue count x (retinue cost - Upkeep -X modifiers)."

# ── ACTION / EMPIRE GOLD COSTS ───────────────────────────────────────────────
# The flat costs the rules attach to actions and siege outcomes.
COSTS = {
    "Pursue action":   "2000 gold (the envoy action; pursuit then costs per-turn upkeep by type)",
    "Pursuit upkeep":  "Per turn by type (fixed): Monument 300, Power 200, Energy 0, all others 0",
    "Army upkeep":     "retinue count x (retinue cost - Upkeep -X modifiers)",
    "Infrastructure upkeep": "Per-settlement (see INFRASTRUCTURE); Trade Guild removes Primitive/Developed, College of Engineering removes Sophisticated",
    "Cunning action":  "2000 gold (Intercept Caravan / Foster Rebellion / Raze / Destabilize)",
    "Industry action": "2000 gold (Build / Repair / Pursue / Charter)",
    "Piety action":    "Doubt 1 (Spread Gospel / Send Missionaries / Tithe / Convert / Crusade)",
    "Prowess action":  "None (Move / Declare War / Demand Tribute)",
    "Diplomacy action":"None (Sign Treaty / Negotiate / End Treaty)",
    "Sack":            "Extort 1000 per settlement tier; reduce settlement by 1 tier; Sack Timer 2",
    "Tax per tier":    "500 gold per settlement tier per turn (collected in Winter)",
    "Trade Income":    "100 x host's Craft X per active Trade Agreement",
}

# phase order (currently only in RULES_reorganized)
PHASES = ("Empire", "Council", "Envoy", "Battle", "Rest")
STARTING_TURN_PHASE_OPENER = PHASES[1]
# ACTIONS["Move"] says "March (move up to 2x Speed)"
MARCH_MULTIPLIER = 2
STANDING_ARMY_SIEGE_MODIFIER = 1
# economy.py has this as a local constant (EMPIRE_START)
EMPIRE_START_TIERS = ("Town", "Village", "Village")
STARTING_TREASURY = 10000

BOARD_SIZES = {
    "Tight":    {3: (12,10), 4: (16,12), 5: (18,14), 6: (20,16)},
    "Standard": {3: (18,14), 4: (20,16), 5: (22,18), 6: (24,20)},
    "Campaign": {3: (30,24), 4: (30,24), 5: (30,24), 6: (30,24)},
}

SIEGE_CALCULUS = {
    "Lay Siege": {
        "settlement_sources": ["Settlement Size", "Wooden Walls", "Stone Walls",
                               "Citadel", "Garrison", "Standing Army"],
        "attacker_sources": True,      # Siege Works, Siege Camp, army effects
        "floor": 1,
    },
    "Convert": {
        "settlement_sources": ["Settlement Size", "Citadel"],
        "attacker_sources": False,     # settlement-type modifiers only
        "floor": 1,
    },
}

# Sources whose value isn't in effect text
SIEGE_SOURCE_VALUES = {
    "Settlement Size": {"from": "SETTLEMENTS", "field": "tier"},
    "Standing Army":   {"from": "board_state", "value": STANDING_ARMY_SIEGE_MODIFIER,
                        "rule": "army at range 0 of the settlement"},
    "Garrison":        {"value": 1},
    "Wooden Walls":    {"value": 1},
    "Stone Walls":     {"value": 2},
    "Citadel":         {"innate_value": 1, "mastery_value": 1},
}

# ── Missing glossary definitions (CE) ────────────────────────────────────────
GLOSSARY.update({
    PIVOTAL:        f"A natural {FOCUSED_THR}, before modifiers." if FOCUSED_THR == FACES else f"A natural {FOCUSED_THR} or higher, before modifiers.",
    FATIGUE_TOKEN:  f"Each token is -{FATIGUE_STRIKE} to your Strike (to a maximum of {CAP_THR}+) and Morale -{FATIGUE_MORALE} (uncapped); if your modified Morale is ever {ROUT_THR}+, your army Routs. Tokens stack. While Fatigued, retinues cannot Parry or Recover.",
    "Sally Forth":  "While a settlement you control is besieged and you have an army inside it, you may Sally Forth: Battle in the Battle Phase without performing an action.",
    "War Weariness":"gain Doubt 1 for each consecutive Battle you lose in the Empire Phase.",
    "Ward":         "A slot in a Settlement that holds one Pursuit; a Settlement has one Ward per tier (a Hamlet has 3 Husbandry Wards).",
    "Efficient X":  "While this Pursuit occupies the same Settlement Ward as X (the Raw Material or Pursuit named on its tile), it uses no ward of its own \u2014 the two share one ward. Placed anywhere else, it fills a ward normally. (Core Principle 14.) Note: Two Pursuits that are Efficient with the same Pursuit cannot share a Ward with each other.",
})

# ══════════════════════════════════════════════════════════════════════════════
# DISPLAY LAYER — engine ids stay stable; only printed labels change.
# Add an alias here, never rename an id in NODES/WEAPONS/TIERS/loadouts.
# ══════════════════════════════════════════════════════════════════════════════
import re as _re_disp

# Entity ids -> printed label (weapons, ranged, shields, armor, nodes).
NAME_DISPLAY = {
    "Spears": "Spear",
    "Pilum": "Angon",
    "Farm Tools": "Farm Tool",
    "Artillery Park": "Ordinance Yard",
    "Coliseum": "Castle Yard",
    "Javelin": "Throwing Axe",
    "Crafted" : "Tempered",
    "Gambeson": "Padded",
}

# Equipment tier ids -> printed label. Separate map because tiers are a closed
# set the engine keys on (loadouts.TIER_INDUSTRY_REQ, WEAPONS_BY_TIER, ...).
TIER_DISPLAY = {
    "Crafted": "Tempered",
}

# One combined table for free-text rewriting. Keep ids unique across both maps.
ALIASES = {**NAME_DISPLAY, **TIER_DISPLAY}

# Longest-first alternation so "Artillery Park" wins over a hypothetical "Park",
# and \b so "Coliseum" never fires inside "Coliseums" or "GrandColiseum".
_ALIAS_RE = _re_disp.compile(
    r"\b(" + "|".join(_re_disp.escape(k) for k in
                      sorted(ALIASES, key=len, reverse=True)) + r")\b"
) if ALIASES else None


def display(name):
    """Player-facing label for an engine id. Returns the id when unaliased."""
    return ALIASES.get(name, name)


def display_tier(tier):
    """Player-facing label for a tier id. Handles None/'' (shields)."""
    return TIER_DISPLAY.get(tier, tier) if tier else tier


def display_text(s):
    """Rewrite every alias inside a free-text string — mastery_req, effect and
    note text, escalation ranks. Single pass over a combined pattern, so a
    rename can never cascade into another rename's output."""
    if not s or _ALIAS_RE is None:
        return s
    return _ALIAS_RE.sub(lambda m: ALIASES[m.group(1)], str(s))


def display_list(seq, sep=", "):
    """Join an id list (builds_into, prereqs, requires_all) as labels."""
    return sep.join(display(x) for x in (seq or []))


def undisplay(label):
    """Label -> engine id. For wiki anchors and cross-links that must resolve
    back to a real key. Raises on an ambiguous alias rather than guessing."""
    hits = [k for k, v in ALIASES.items() if v == label]
    if len(hits) > 1:
        raise KeyError(f"alias {label!r} maps back to {hits}")
    return hits[0] if hits else label


def verify_aliases():
    """Return (ok, problems). Run from verify_d10.py."""
    problems = []
    for k, v in ALIASES.items():
        if k == v:
            problems.append(f"{k!r} aliases to itself")
        if v in ALIASES:
            problems.append(f"{k!r} -> {v!r}, but {v!r} is itself an alias key (chain)")
    for label in set(ALIASES.values()):
        owners = [k for k, v in ALIASES.items() if v == label]
        if len(owners) > 1:
            problems.append(f"label {label!r} claimed by {owners}")
    # An alias key that is not a real id is a typo that silently does nothing.
    known = set(NODES) | set(WEAPONS) | set(RANGED) | set(SHIELDS) | set(ARMORS) | set(TIERS)
    for k in ALIASES:
        if k not in known:
            problems.append(f"alias key {k!r} matches no node/weapon/tier id")
    return (not problems, problems)
 

# ══════════════════════════════════════════════════════════════════════════════
# BANDIT DIE TABLES — dice-agnostic. Keys are a face value or a (lo, hi) range.
# Edit the tables; every renderer (MD, host sheet, cards) recomputes from them.
# ══════════════════════════════════════════════════════════════════════════════
BANDIT_FACES = FACES          # die bandits roll; tracks dice_config.FACES
BANDIT_CUNNING_MIN = 10       # retinues in camp required to roll the Cunning table

# ── Generic table plumbing (works for any value/range: action table) ─────────
def die_table_ranges(table, faces=None):
    """Normalize {int|(lo,hi): action} to a sorted [(lo, hi, action), ...]."""
    out = []
    for key, action in table.items():
        lo, hi = (key, key) if isinstance(key, int) else (key[0], key[1])
        out.append((lo, hi, action))
    return sorted(out)

def die_table_rows(table, faces=None):
    """Human-readable rows: '1-3 – Intercept Caravan', '10 – Foster Rebellion'."""
    rows = []
    for lo, hi, action in die_table_ranges(table, faces):
        span = f"{lo}" if lo == hi else f"{lo}-{hi}"
        rows.append(f"{span} \u2013 {action}")
    return rows

def die_table_text(table, faces=None):
    """Inline form: '1-3 = Intercept Caravan, 4-6 = Raze, ...'."""
    parts = []
    for lo, hi, action in die_table_ranges(table, faces):
        span = f"{lo}" if lo == hi else f"{lo}-{hi}"
        parts.append(f"{span} = {action}")
    return ", ".join(parts)

def die_table_lookup(table, roll, faces=None):
    """Resolve a rolled value to its action; None if the face is uncovered."""
    for lo, hi, action in die_table_ranges(table, faces):
        if lo <= roll <= hi:
            return action
    return None

def die_table_verify(table, faces=None, label="table"):
    """Return (ok, problems). Checks every face 1..faces is covered exactly once."""
    faces = BANDIT_FACES if faces is None else faces
    ranges = die_table_ranges(table, faces)
    problems, seen = [], {}
    for lo, hi, action in ranges:
        if lo > hi:
            problems.append(f"{label}: inverted range {lo}-{hi} ({action})")
        if lo < 1 or hi > faces:
            problems.append(f"{label}: {lo}-{hi} ({action}) outside 1-{faces}")
        for v in range(max(lo, 1), min(hi, faces) + 1):
            if v in seen:
                problems.append(f"{label}: face {v} claimed by both {seen[v]} and {action}")
            seen[v] = action
    missing = [v for v in range(1, faces + 1) if v not in seen]
    if missing:
        problems.append(f"{label}: faces uncovered: {missing}")
    return (not problems, problems)

def die_table_weights(table, faces=None):
    """{action: face count} — for eyeballing frequency when modulating."""
    faces = BANDIT_FACES if faces is None else faces
    w = {}
    for lo, hi, action in die_table_ranges(table, faces):
        w[action] = w.get(action, 0) + (min(hi, faces) - max(lo, 1) + 1)
    return w

# ── CUNNING TABLE — what a camp of BANDIT_CUNNING_MIN+ retinues does each turn ─
# Tune these ranges freely; die_table_verify() enforces full coverage of 1..FACES.
BANDIT_CUNNING_TABLE = {
    (1, 2):  "Intercept Caravan",
    (3, 7):  "Raze",
    (8, 9):  "Destabilize",
    10:      "Foster Rebellion",
}

def bandit_cunning_ranges(faces=None): return die_table_ranges(BANDIT_CUNNING_TABLE, faces)
def bandit_cunning_rows(faces=None):   return die_table_rows(BANDIT_CUNNING_TABLE, faces)
def bandit_cunning_lookup(roll, faces=None): return die_table_lookup(BANDIT_CUNNING_TABLE, roll, faces)

def bandit_cunning_text(faces=None):
    faces = BANDIT_FACES if faces is None else faces
    return (f"If {BANDIT_CUNNING_MIN}+ retinues in camp, roll a d{faces} each turn: "
            f"{die_table_text(BANDIT_CUNNING_TABLE, faces)}.")

# ── TACTIC TABLE — explicit ranges, same plumbing (replaces the even auto-split)
BANDIT_TACTIC_TABLE = {
    (1, 2):  "Ambush",
    (3, 4):  "Flank",
    (5, 6):  "Charge",
    (7, 8):  "Fighting Formation",
    (9, 10): "Defensive Formation",
}
BANDIT_TACTICS = [a for _, _, a in die_table_ranges(BANDIT_TACTIC_TABLE)]

def bandit_tactic_ranges(faces=None): return die_table_ranges(BANDIT_TACTIC_TABLE, faces)
def bandit_tactic_rows(faces=None):   return die_table_rows(BANDIT_TACTIC_TABLE, faces)
def bandit_tactic_lookup(roll, faces=None): return die_table_lookup(BANDIT_TACTIC_TABLE, roll, faces)

# ── Coverage check (call from verify_d10.py / build step) ────────────────────
def verify_bandit_tables(faces=None):
    ok_c, p_c = die_table_verify(BANDIT_CUNNING_TABLE, faces, "BANDIT_CUNNING_TABLE")
    ok_t, p_t = die_table_verify(BANDIT_TACTIC_TABLE,  faces, "BANDIT_TACTIC_TABLE")
    return (ok_c and ok_t, p_c + p_t)

# ── Wire the generated text back into BANDIT_BEHAVIOR ────────────────────────
# Place after BANDIT_BEHAVIOR is defined, or move the dict below this block.
BANDIT_BEHAVIOR["Cunning Roll"] = bandit_cunning_text()
BANDIT_BEHAVIOR["Attacking"] = (
    f"Move to end adjacent to a camp; another player rolls bandit tactics on a "
    f"D{BANDIT_FACES} (see the bandit tactic table) and resolves to-strike/save as a "
    f"Battle. Bandits never Fall Back but may Flee. Extort the camp's gold if destroyed."
)

if __name__ == "__main__":
    ok, problems = verify_bandit_tables()
    print(f"d{BANDIT_FACES} | bandit tables {'OK' if ok else 'FAIL'}")
    for p in problems:
        print("  " + p)
    print("Cunning:", die_table_weights(BANDIT_CUNNING_TABLE))
    print("Tactics:", die_table_weights(BANDIT_TACTIC_TABLE))
    print(bandit_cunning_text())