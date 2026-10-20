# renown_data — single source of truth (CSV/0.4.8 branch, card-verified)
# Edit THIS file; equipment.csv, cards, and docs are generated from it.
import os as _os
SIMPLE = _os.environ.get("RENOWN_SIMPLE", "1") == "1"   # build_all_CE.bat: set SIMPLE=1|0
vS = "-SIMPLE" if SIMPLE else ""
VERSION = f"0.4.9.9.13-d10{vS}"
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
# ── Balance constants (rules text + data strings read these) ─────────────────
SACK_EXTORT_PER_TIER = 2000
WEALTH_EDICT_GOLD    = 50000
MUSTER_RANGE         = 2
MARCH_MULTIPLIER     = 2
PO_MIN               = -5
PO_MAX               = 10
INITIATIVE_MIN       = -2
INITIATIVE_MAX       = 2
STANDING_THRESHOLDS = {
    "Untested":    1,
    "Rising":      3,
    "Established": 6,
    "Sovereign":  10,
}
_ST = STANDING_THRESHOLDS

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
SERRATED_MOD    = 2          # Serrated: cumulative penalty to the defender's Recover roll
ENDURING        = "Enduring"   # successfully Recovered Strikes don't count toward the Panic check threshold
STRAIN          = "Strain"
MINUS_1_TBH     = "Shielded"
PLANISHING      = "Planishing"
FATIGUE_TOKEN   = "Fatigue Token"
CRUSADER        = "Righteous Fervour"

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

NEGATE_TEMPERED    = f"Negate {PLANISHING}"   # RETIRED (Oct 19 2026): on no item; constant kept for engine imports
NEGATE_RIPOSTE     = "Negate Riposte"           # RETIRED (Oct 19 2026): folded into Unstoppable; constant kept for engine imports
NEGATE_SHIELDED    = negate(MINUS_1_TBH)   # "Negate Shielded": attacker ignores defender's Shielded (-1 to Strike)
MINUS_1_PARRY      = "-1 to Parry"
HALFSWORD          = "Halfsword"   # RESERVED — engine path intact, no weapon carries it (shelved)
DUAL_WIELD         = "Dual Wield"
FLORENTINE         = "Florentine"  # Parry survives Fatigue: degrades to CAP_THR+ but is never disabled. Grants Parry. Only active while Dual Wielding.
PIVOTAL = "Focused"


GLOSSARY = {
    STEADY:         "Initiative cannot be reduced by Tactics.",
    UNWIELDY:       "Initiative cannot be improved by Tactics.",
    TWO_H:          "Cannot use a Shield: while a 2H weapon is Equipped, your Shield gives nothing that Skirmish (no Save bonus, Initiative or keywords).",
    SHATTER_ARMOR:  f"On a {PIVOTAL} Strike: that strike's AP is increased by {DEADLY_AP}, and the defender may Parry or {RECOVER} only with a {PIVOTAL} roll.",
    UNSTOPPABLE:    f"-{UNSTOPPABLE_MOD} to the defender's Parry roll (to a maximum of {CAP_THR}+); a Parry against it can't Riposte.",
    CLEAVE:         f"On a {PIVOTAL} Strike: roll one extra Strike die at your modified to-Strike.",
    POISON:         f"When the Defender receives a Strike and rolls a {PIVOTAL} Save, it fails; the resulting wound may only be {RECOVER}ed with a {PIVOTAL} {RECOVER}.",
    NIMBLE:         "Gain Initiative +1 in the first Skirmish of each Battle.",
    DRILLED:        "Does not lose Endurance in the first Skirmish of each Battle.",
    DESTROY_SHIELD: f"On a {PIVOTAL} Strike: the target loses its Shield attributes for the rest of the Battle.",
    BLUNDER:        f"At Initiative {INITIATIVE_MIN}, your to-Strike is set to {BLUNDER_THR}+, before other negative modifiers.",
    ONE_SHOT:       "Must be Equipped in the first Skirmish of a Battle, and can't be Equipped after it. Requires a Tiltyard.",
    #DEFLECT:        "-1 to Parry and Negate Riposte against this weapon's Strikes. (All Ranged weapons have Deflect.)",
    #IMMUNE_PANIC:   "Automatically passes Panic checks.",
    #UNBREAKABLE:    "Immune Break: does not take Break checks while Fatigued.",
    PARRY:          f"If your Army has gained {PARRY}, roll a D{FACES} to attempt to Parry a Strike before an Armor Save. On a {PARRY_BASE}+ (Improved by Improved Parry), the Strike is Parried and has no further effect.",
    RIPOSTE:        f"If your Army has gained {RIPOSTE} and rolls a Focused Parry against a Melee Weapon's Strike, you Riposte: your opponent immediately takes a Strike from your melee weapon. You can Riposte a Riposte.",
    NO_PARRY:       "While equipped with this weapon during a skirmish, you cannot Parry, and so cannot Riposte.",
    RECOVER:        f"If your Army has gained {RECOVER} and a to-Save roll fails, roll a D{FACES} & compare it to your Recover value: a result greater than or equal to your Recover value recovers the retinue. Recovered Strikes still count toward the Panic check threshold.",
    ENDURING:       "Successfully Recovered Strikes don't count toward the Panic check threshold.",
    SERRATED:       f"A cumulative -{SERRATED_MOD} penalty to the defender's Recover roll.",
    PLANISHING:     f"A {PIVOTAL} Save succeeds, regardless of AP.",
    FATIGUE_TOKEN:  f"Each token reduces Morale -{FATIGUE_MORALE} by. If your modified Morale is ever {ROUT_THR}+, your army Routs. These effects are cumulative.",
    MINUS_1_TBH:    f"A cumulative -1 penalty to the Strike roll (to a maximum of {CAP_THR}+). Sources: a shield's -1 to Strike.",
	#NEGATE_UNSTOPPABLE: "Cancels the attacker's Parry from Unstoppable: this shield's -1 to Strike still applies, and the attacker's -1 to Parry does not.",
    #MINUS_1_PARRY: "A stacking -1 penalty to the defender's Parry roll (to a maximum of 6+). Sources: Unstoppable, Deflect, and each Fatigue token.",
    DUAL_WIELD: "A failed Strike is rerolled once; the rerolled Strike can be Focused. Dual Wield confers Two-Handed. You cannot reroll successful Strikes.",
    #FLORENTINE: "Only active while Dual Wielding.",
    "Immune [keyword]": "Can't gain that keyword's effect as it applies to your Army (e.g. Immune Strain, Destroy Shield, Steady, etc.).",
    "Negate [keyword]": "Your opponent can't gain that keyword's effect as it applies to their Army (e.g. Negate Shielded).",

    # ── Combat keywords ported from the Escalation Campaign glossary ──
    "AP":            "Armor Penetration — a weapon's (negative) modifier to the defender's Save roll; the more negative, the harder to save.",
    "Blocked":       "Initiative -1 in the first Skirmish (negated by Immune Blocked). Armies with Blocked cannot perform Move actions.",
    "Strained":      "Initiative -1 every Skirmish (negated by Immune Strain). Does not gain Endurance in the Empire Phase.",
    #"Improved Parry": "Your Parry succeeds on 4+ instead of 5+.",
    #"Heal X":        "At the end of each Skirmish, for every X casualties you took from Strikes, return 1 retinue to your Army.",
    "Seize the Initiative": "Typically, the player who performed the Battle Action gains Seize the Initiative, but Terrain and the Ministry of Military Strategy can affect that. When a player gains Seize the Initiative, the player gains Initiative +1 in the first skirmish.",

    # ── Battle-structure terms (doc glossary, wording updated to current rules) ──
    "Attacker / Defender": "The Attacker performed the Move action that caused the Battle or Lay Siege; the other side is the Defender.",
    "Battle":        "A collection of Skirmishes between two players, continuing until a side's Retinue count is reduced to 0, Routs, or successfully Falls Back, ending the Battle.",
    "Skirmish":      "One round of a Battle, run through the numbered Battle steps; a Battle repeats Skirmishes until it ends.",
    "Casualty":      "A retinue removed from the field — from an unsaved Strike or a failed Panic or Break check.",
    "Field":         "Your retinues in play — front line (up to 10) plus reserve (up to 5). Casualties leave the field at once, lowering its count.",
    "Endurance":     "A side's stamina. Each side that fights loses 1 per Skirmish; at 0 it becomes Fatigued.",
    "Fatigued":      f"A side at 0 Endurance. Each Skirmish its field takes a Break check, then it gains a Fatigue token.",
    "Break check":   "Taken by each Fatigued side's field every Skirmish, just before it gains its Fatigue token. Roll Morale (5 dice, modified by Fatigue tokens); failures are casualties, but a Break check never triggers a Panic check. Unbreakable auto-passes.",
    "Panic check":   "Taken at most once per Skirmish by a side that suffered more than 5 casualties in that Skirmish (Recovered Strikes count, unless Enduring), after both sides have Struck. Roll Morale (5 dice); Immune Panic auto-passes.",
    "Morale":        f"How steady a retinue is when tested (lower is steadier; see the retinue table). Break and Panic checks roll it: a D{FACES} per retinue in the field, up to 5 dice, each must meet its modified value; failures are casualties. If the modified value is ever {ROUT_THR}+, the army Routs.",
    "Rout":          f"The army breaks and leaves the Battle. Apply casualties equal to the remaining retinues. Whenever an army's modified Morale value reaches {ROUT_THR}+ or more, it Routs automatically.",
    "Fall Back":     "A controlled retreat that ends the Battle with at least one retinue left — a partial success.",
    "Strike":        f"A landed hit. Roll a D{FACES}, apply modifiers to the roll, and Strike on a result >= the to-Strike number. The target may then Parry, Save, and Recover.",
    "to-Strike number": f"The D{FACES} result a retinue needs to Strike (see the retinue table; lower is better). Bonuses add to the roll; penalties and Fatigue tokens subtract.",
    "Save":          f"The defender's roll to avoid a casualty: roll a D{FACES}, add the weapon's AP (a negative) and the shield's Save bonus (a positive); the hit is saved on a result >= the armor value.",
    "Natural roll":  "The number on the die before any modifiers. Modifiers never change what counts as 'natural'.",
    "Initiative":    f"Decides who Strikes first each Skirmish (higher first). Runs {INITIATIVE_MIN} to +{INITIATIVE_MAX} (Ministry can raise the maximum to +3). At {INITIATIVE_MIN} or lower you Blunder.",
    "Tactic":        "A choice both players make secretly and reveal together each Skirmish; it can shift Initiative, Strike, and Save rolls.",
    "Dual-equip":    "Carry two weapons at once (e.g. melee + ranged). Granted by the Tiltyard, which also gives Unwieldy until its mastery removes it.",
    "Monument":      "A Domain's capstone Pursuit. Completing one scores its Edict and grants a powerful effect.",

    # ── Empire keywords (referenced by Pursuits/Factions; DRAFTED — review wording) ──
    "Faith X":       "Gain X Faith: each Faith raises your Public Order track by 1 when resolved.",
    "Doubt X":       "Gain X Doubt: each Doubt lowers your Public Order track by 1 when resolved.",
    "Extort X":      "Take X from the stated source: the gold goes to you instead of its owner.",
    "Recoup X":      "Undo up to X of the cost you paid (refund gold, or remove Doubt gained).",
    "Speed X":       "An Army's movement allowance in Territories per Move action. Base Speed value of an army is Speed 3",

    # ── Council, Influence & Envoys (from Rules; the political loop) ──
    "Influence":     "The political currency of voting. Spend it to Support or Oppose Envoys. You gain it each Empire Phase from your Era, innate modifiers (trade partners, alliances, war), Pursuits, and Infrastructure.",
    "Authority X":   "An automatic +X (or -X) to an Envoy's net Influence from a Pursuit, Infrastructure, or Faction.",
    "Envoy":         "The currency of actions: send an Envoy to perform an action during the Envoy Phase. Council Envoys act on the voted Domain; Personal Envoys are sent by Era progression.",
    "Vote":          "On each Envoy, every player except the sender, in clockwise order from the starting player, must Support, Oppose, or Abstain. No talking during a vote.",
    "Support X":     "Spend X Influence to increase an Envoy's net Influence.",
    "Oppose X":      "Spend X Influence to decrease an Envoy's net Influence.",
    "Abstain":       "Decline to spend Influence on a vote.",
    "Net Influence": "The sum of an Envoy's starting Influence (1+ by Standing) and all Support, Oppose, and Authority X. The total sets the outcome: -3 or less Condemned, 0 or less Failed (gain Doubt +1), 1+ passes.",
    "Endorsed":      "An Envoy that passes with 3+ net Influence, triggering its endorsed effect (and a Domain's Rising/Established/Sovereign endorsement).",
    "Condemned":     "An Envoy whose net Influence is -3 or less: it fails and you resolve that Domain's Condemn effect.",
    "Council Phase": "Before Personal Envoys, a brief Forum, then all players vote on a Domain with no talking (clockwise; Host breaks ties). Each then sends a free Council Envoy of that Domain. Council Envoys auto-Abstain and their net Influence cannot drop below 1.",
    "Council Envoy": "A free Envoy resolved in the Council Phase on the voted Domain; auto-Abstained, net Influence floored at 1.",
    "Personal Envoy": "An Envoy you send in the Envoy Phase to attempt to perform an action; the amount of Envoys you can spend and the volume of actions you can perform with one scales with Era.",
	"Envoy Outcome": "How a Sent Envoy resolves, by Net Influence: Condemned (<= -3), "
                    "Failed (-3 < Net <= 0, gain Doubt 1), Passed (>= 1), Endorsed (>= 3). The per-domain "
                    "effect at each band is given by the Envoy Outcome Table; an action's own endorsed bonus overrides "
                    "the domain default.",

    # ── Empire actions ──
    "Charter":       "Found or upgrade a Settlement (Industry action).",
    "Muster":        "Raise a new Army or Reinforce an existing one near a Muster Field; Retinues arrive each Empire Phase over a Muster Timer (Prowess action).",
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
    "Domain":        f"One of the four identities — Industry, Prowess, Cunning, Piety — raised by spending Domain points. Values {_ST['Rising']}/{_ST['Established']}/{_ST['Sovereign']} = Rising/Established/Sovereign Standing.",
    "Domain Point":  "Gain {DOMAIN_POINTS_PER_TURN} each Rest Phase; spend to raise a Domain value by 1.",
    "Standing":      f"Your tier in a Domain: Untested, Rising ({_ST['Rising']}), Established ({_ST['Established']}), Sovereign ({_ST['Sovereign']}). Sets max Influence per vote (1/2/3/4) and unlocks Domain effects.",
    "Public Order":  f"A track from {PO_MIN} to {PO_MAX}, adjusted each turn by Faith minus Doubt; its band applies cumulative effects (see the Public Order table).",
    "Reach":         "How far a Settlement projects control, in Territories (by tier). Calculated like Range X",
    "Edict":         "A scoring achievement. Grants the Realm +1 Renown every time one is achieved.",

    # ── World ──
    "Bandit":        "Neutral hostile force; Bandit Camps spawn in Outlaw Country and on low Public Order.",
    "Outlaw Country": "Uncontrollable Territory zones where Bandit Camps spawn ({OUTLAW_COUNTRY_START} Territories each at Setup). A zone is your Outlaw Country while any of its Territories is within your Province. Foster Rebellion expands it when there is no room; otherwise, when there is no room, its Bandit Camps grow instead.",
    "Wild Outlaw Country": "Outlaw Country the Host places outside every Province at Setup. After Setup it works like any other Outlaw Country zone.",
    "Siege":         "Sieging a Settlement with an Army to capture it; Siege Timers don't count down in Winter.",
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
    "Levy":           {"cost": 1000, "to_hit": 6, "endurance": 3, "shaking": 7, "unbreakable": False, "speed": 5, "max_size": ARMY_MAX_RETINUES},
    "Man-at-Arms":    {"cost": 2000, "to_hit": 5, "endurance": 4, "shaking": 6, "unbreakable": False, "speed": 5, "max_size": ARMY_MAX_RETINUES},
    "Sergeant":       {"cost": 3000, "to_hit": 3, "endurance": 3, "shaking": 5, "unbreakable": False, "speed": 5, "max_size": ARMY_MAX_RETINUES},
    "Knight Templar": {"cost": 3000, "to_hit": 4, "endurance": 3, "shaking": 4, "unbreakable": False, "speed": 5, "max_size": ARMY_MAX_RETINUES},
}

WEAPONS = {
    "Farm Tools":     {"ap":  0, "init":  0, "tier": "Crude",   "tags": [NO_PARRY]},
    "Cudgel":         {"ap": -1, "init": -1, "tier": "Crude",   "tags": [TWO_H, UNWIELDY, NO_PARRY]},
    "Pitchfork":      {"ap":  0, "init":  1, "tier": "Crude",   "tags": [TWO_H, UNWIELDY, NO_PARRY]},
    "Daggers":        {"ap":  0, "init":  0, "tier": "Cast",    "tags": [TWO_H, SHATTER_ARMOR, NO_PARRY]},
    "Short Sword":    {"ap":  0, "init":  0, "tier": "Cast",    "tags": [STEADY]},
    "Spears":         {"ap": -1, "init":  1, "tier": "Cast",    "tags": [UNWIELDY]},
    "Arming Sword":   {"ap": -1, "init":  0, "tier": "Wrought", "tags": [STEADY]},
    "Pike":           {"ap": -2, "init":  1, "tier": "Wrought", "tags": [TWO_H, STEADY, UNWIELDY, SHATTER_ARMOR, NO_PARRY]},
    "Flail":          {"ap": -1, "init":  0, "tier": "Wrought", "tags": [UNWIELDY, UNSTOPPABLE, CLEAVE, NO_PARRY], 'note': 'Cannot Dual Wield'},
    "Halberd":        {"ap": -2, "init":  0, "tier": "Wrought", "tags": [TWO_H, STEADY]},
    "Battle Axe":     {"ap": -3, "init": -1, "tier": "Wrought", "tags": [TWO_H, UNSTOPPABLE, CLEAVE, NEGATE_SHIELDED]},
    "Cavalry Spear":  {"ap": -2, "init":  1, "tier": "Wrought", "tags": [STEADY, UNSTOPPABLE, UNWIELDY, NO_PARRY], 'note': "Needs Stable Mastery; no Tower Shield or Dual Wield or Ranged Weapon"},
    "Morningstar":    {"ap": -4, "init": -1, "tier": "Forged",  "tags": [CLEAVE, DESTROY_SHIELD], 'note': 'Cannot Dual Wield'},
    "Bastard Sword":  {"ap": -2, "init":  0, "tier": "Forged",  "tags": [STEADY], 'note': 'At the beginning of each equipment step, you may choose the 1H or 2H profile.'},
    "2HBastard":      {"ap": -2, "init":  0, "tier": "Forged",  "tags": [TWO_H, UNSTOPPABLE, CLEAVE]},
    "War Hammer":     {"ap":-10, "init": -1, "tier": "Forged",  "tags": [TWO_H, STEADY, UNSTOPPABLE, NEGATE_SHIELDED, DESTROY_SHIELD]},
    "Lance":          {"ap": -4, "init":  1, "tier": "Forged",  "tags": [STEADY, UNWIELDY, UNSTOPPABLE, NO_PARRY, DESTROY_SHIELD], 'note': "Needs Saddlery; no Tower Shield, Dual Wield, Ranged weapon."},
    "Estoc":          {"ap": -3, "init":  0, "tier": "Crafted", "tags": [STEADY, SHATTER_ARMOR, UNSTOPPABLE]},
    "Poleaxe":        {"ap": -5, "init":  0, "tier": "Crafted", "tags": [TWO_H, STEADY, CLEAVE, UNSTOPPABLE, NEGATE_SHIELDED]},
}

RANGED = {
    "Hunting Bow": {"ap":  0, "init":  2, "tier": "Crude",   "tags": [TWO_H, UNSTOPPABLE, NO_PARRY]},
    "Longbow":     {"ap": -1, "init":  2, "tier": "Cast",    "tags": [TWO_H, UNSTOPPABLE, SHATTER_ARMOR, NO_PARRY]},
    "Javelin":     {"ap": -2, "init":  1, "tier": "Wrought", "tags": [STEADY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, DESTROY_SHIELD, ONE_SHOT, NO_PARRY], 'note': 'Cannot Dual Wield'},
    "Crossbow":    {"ap": -4, "init":  1, "tier": "Forged",  "tags": [TWO_H, UNWIELDY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NO_PARRY], 'note': "Cannot Dual Wield"},#'note': "Tower Shield only (no other shield), cannot Dual Wield"
    "Pilum":       {"ap": -5, "init":  1, "tier": "Crafted", "tags": [STEADY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, DESTROY_SHIELD, ONE_SHOT, NO_PARRY]},
    "Arquebus":    {"ap": -6, "init":  2, "tier": "Crude",   "tags": [TWO_H, UNWIELDY, UNSTOPPABLE, NEGATE_SHIELDED, NO_PARRY], 'note': "May only use the Fighting Formation or Fall Back Tactics.", 'requires': ["Artillery Park"], 'tactics_allowed': ["Fighting Formation", "Fall Back"]},
   
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
    "Gambeson":    {"save":  8, "tier": "Crude",   "tags": []},
    "Leather":     {"save":  7, "tier": "Cast",    "tags": []},
    "Chainmail":   {"save":  6, "tier": "Wrought", "tags": []},
    "Full Plate":  {"save":  5, "tier": "Forged",  "tags": []},
    "Gothic Plate":{"save":  4, "tier": "Crafted", "tags": []},
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
    ("Piety",   "Rising"): "Morale +1",
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
# One line per tactic shown in the board's Tactics matchups panel (objective / risk, in your words). Empty = not shown.
TACTIC_NOTES = {}
 



# CULTURES: the 15 worldlore cultures as playstyles (replaces PLAYSTYLES).
# Names/domains match renown_worldlore.CULTURES. Read by references/playstyle_reference.py.
# type      : pure | pair | triple | centre
# domains   : culture's domains, lead first (drives banner colours)
# monuments : Monument nodes (NODES type == 'Monument') - standing path is derived from their unlocks
# wonders   : keys of WONDERS
# actions   : "Action" or "Action: mode" - Action must be a key of ACTIONS
# factions  : keys of FACTIONS; every faction maps to at least one culture (duplicates allowed)
# radar     : relative emphasis 1-5 on the seven reference axes
# Culture view filter (settlement board): a player may pick a culture to focus the Holding tree / catalog on its
# Domains, Monuments and Wonders. No game effect. CULTURE_SELF_MADE is the name of "no culture" (everything shown).
CULTURE_SELF_MADE = "Self-made"

CULTURES = {
    # ---- pure ----
    'Trusteki': {
        'type': 'pure', 'domains': ['Industry'],
        'monuments': ['Office of Works', 'Manor House', 'Advanced Blast Furnace'],
        'wonders':   ['Colossus', 'The Grand Exchange', 'The Eternal Sepulchre', 'High Chancery'],
        'actions':   ['Pursue', 'Repair', 'Build'],
        'factions':  ['The Verdant Kingdom', 'The Elder Grove', 'The Illuminated Order', 'The Hermit Crown'],
        'radar': {'military_solutions': 3, 'economy_generators': 5, 'faith_management': 3, 'doubt_warfare': 1,
                  'political_control': 3, 'board_presence': 3, 'degenerate_punishment': 2},
    },
    'Kraghs': {
        'type': 'pure', 'domains': ['Prowess'],
        'monuments': ['Royal Pavilion', 'Artillery Park', 'Ministry of Military Strategy'],
        'wonders':   ['Colossus'],
        'actions':   ['Move: Battle', 'Declare War', 'Demand Tribute'],
        'factions':  ['The Boundless Steppe', 'The Final Word', 'The Wandering Crown', 'The Ancient Wilds', 'The Winter Wolves','The Yew Heart'],
        'radar': {'military_solutions': 5, 'economy_generators': 1, 'faith_management': 3, 'doubt_warfare': 2,
                  'political_control': 2, 'board_presence': 5, 'degenerate_punishment': 4},
    },
    'Ithiss': {
        'type': 'pure', 'domains': ['Cunning'],
        'monuments': ["Thieves' Guild", 'Aristocratic Court', 'Outlaw Rookery', 'Outrider Intercept Post'],
        'wonders':   ['High Chancery'],
        'actions':   ['Raze', 'Foster Rebellion', 'Intercept Caravan'],
        'factions':  ['The Bandit King', 'The Crimson Tide', 'The Smoldering Crown', 'The Illusionists'],
        'radar': {'military_solutions': 2, 'economy_generators': 3, 'faith_management': 1, 'doubt_warfare': 5,
                  'political_control': 3, 'board_presence': 2, 'degenerate_punishment': 5},
    },
    'Lenavorites': {
        'type': 'pure', 'domains': ['Piety'],
        'monuments': ['Papal Palace', 'Inquisitorial Palace'],
        'wonders':   ['The Eternal Sepulchre'],
        'actions':   ['Tithe', 'Send Missionaries', 'Spread Truth'],
        'factions':  ['The Sacred Throne', 'The Undying Flame','The Iron Faith', 'The Hermit Crown'],
        'radar': {'military_solutions': 2, 'economy_generators': 3, 'faith_management': 5, 'doubt_warfare': 3,
                  'political_control': 3, 'board_presence': 1, 'degenerate_punishment': 3},
    },
    # ---- pairs ----
    'Belvareth': {
        'type': 'pair', 'domains': ['Piety', 'Prowess'],
        'monuments': ["Preceptory of the Knight's Templar", 'Royal Pavilion'],
        'wonders':   ['The Eternal Sepulchre', 'Colossus'],
        'actions':   ['Sacred War', 'Move: Battle', 'Spread Truth'],
        'factions':  ['The Bloodied Cross', 'The Blazing Standard', 'The Undying Flame', 'The Iron Faith'],
        'radar': {'military_solutions': 5, 'economy_generators': 2, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 2, 'board_presence': 3, 'degenerate_punishment': 2},
    },
    'Vorghith': {
        'type': 'pair', 'domains': ['Prowess', 'Cunning'],
        'monuments': ['Ministry of Military Strategy', 'Outrider Intercept Post'],
        'wonders':   ['Colossus', 'High Chancery'],
        'actions':   ['Pillage', 'Intercept Caravan', 'Move: March'],
        'factions':  ["The Squatters' Crown", 'The Winter Wolves', 'The Bandit King','The Smoldering Crown'],
        'radar': {'military_solutions': 4, 'economy_generators': 2, 'faith_management': 1, 'doubt_warfare': 4,
                  'political_control': 3, 'board_presence': 4, 'degenerate_punishment': 5},
    },
    'Drakteni': {
        'type': 'pair', 'domains': ['Prowess', 'Industry'],
        'monuments': ['Advanced Blast Furnace', 'Ministry of Military Strategy', 'Artillery Park'],
        'wonders':   ['Colossus'],
        'actions':   ['Move: Lay Siege', 'Build', 'Demand Tribute'],
        'factions':  ['The Battering Ram', 'The Yew Heart', 'The Sublime Gate', 'The Final Word'],
        'radar': {'military_solutions': 5, 'economy_generators': 4, 'faith_management': 2, 'doubt_warfare': 2,
                  'political_control': 3, 'board_presence': 4, 'degenerate_punishment': 2},
    },
    'Prezish': {
        'type': 'pair', 'domains': ['Cunning', 'Industry'],
        'monuments': ['Aristocratic Court', "Thieves' Guild", 'Manor House'],
        'wonders':   ['The Grand Exchange'],
        'actions':   ['Intercept Caravan', 'Sign Treaty: Trade Agreement', 'Pursue'],
        'factions':  ['The Merchant Republics', 'The Gilded Path', 'The Grand Compact', 'The Crimson Tide'],
        'radar': {'military_solutions': 2, 'economy_generators': 5, 'faith_management': 2, 'doubt_warfare': 4,
                  'political_control': 3, 'board_presence': 1, 'degenerate_punishment': 3},
    },
    'Shassolin': {
        'type': 'pair', 'domains': ['Cunning', 'Piety'],
        'monuments': ['Senate Hall', 'Inquisitorial Palace', 'Aristocratic Court'],
        'wonders':   ['High Chancery'],
        'actions':   ['Send Missionaries', 'Tithe', 'Destabilize'],
        'factions':  ['The Ashen Vale','The Forked Tongue', "The Iron Faith"],
        'radar': {'military_solutions': 2, 'economy_generators': 2, 'faith_management': 4, 'doubt_warfare': 5,
                  'political_control': 4, 'board_presence': 1, 'degenerate_punishment': 5},
    },
    'Madekites': {
        'type': 'pair', 'domains': ['Piety', 'Industry'],
        'monuments': ['Office of Works', 'Papal Palace'],
        'wonders':   ['The Eternal Sepulchre', 'The Grand Exchange'],
        'actions':   ['Build', 'Pursue', 'Spread Truth'],
        'factions':  ['The Iron Faith', 'The Gilded Crescent', 'The Tunnellers', 'The Verdant Kingdom'],
        'radar': {'military_solutions': 3, 'economy_generators': 5, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 2, 'board_presence': 1, 'degenerate_punishment': 3},
    },
    # ---- triples ----
    'Cailendroffs': {
        'type': 'triple', 'domains': ['Piety', 'Prowess', 'Cunning'],
        'monuments': ['Imperial Palace', 'Royal Pavilion', "Preceptory of the Knight's Templar", 'Aristocratic Court'],
        'wonders':   ['Colossus', 'High Chancery'],
        'actions':   ['Sacred War', 'Declare War', 'Negotiate'],
        'factions':  ['The Crowned Star', 'The Entwined Crown', 'The Hermit Crown', 'The Bloodied Cross'],
        'radar': {'military_solutions': 4, 'economy_generators': 1, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 4, 'board_presence': 4, 'degenerate_punishment': 3},
    },
    'Sarkopekt': {
        'type': 'triple', 'domains': ['Cunning', 'Industry', 'Prowess'],
        'monuments': ['Outrider Intercept Post', 'Ministry of Military Strategy', 'Advanced Blast Furnace'],
        'wonders':   ['Colossus', 'The Grand Exchange'],
        'actions':   ['Move: Battle', 'Demand Tribute', 'Sabotage'],
        'factions':  ['The Broken Banner', 'The Sublime Gate', 'The Iron Shore', 'The Boundless Steppe', 'The Ancient Wilds',
                      'The Battering Ram'],
        'radar': {'military_solutions': 4, 'economy_generators': 4, 'faith_management': 1, 'doubt_warfare': 3,
                  'political_control': 2, 'board_presence': 5, 'degenerate_punishment': 5},
    },
    'Ossensteins': {
        'type': 'triple', 'domains': ['Cunning', 'Piety', 'Industry'],
        'monuments': ['Office of Works', 'Inquisitorial Palace'],
        'wonders':   ['The Grand Exchange', 'High Chancery'],
        'actions':   ['Tithe', 'Destabilize', 'Build'],
        'factions':  ['The Hall of Masks', 'The Forked Tongue', 'The Velvet Hand', 'The Illusionists', 'The Illuminated Order',
                      'The Eternal Court'],
        'radar': {'military_solutions': 1, 'economy_generators': 5, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 5, 'board_presence': 1, 'degenerate_punishment': 4},
    },
    'Voldrastel': {
        'type': 'triple', 'domains': ['Piety', 'Industry', 'Prowess'],
        'monuments': ['Senate Hall', 'Ministry of Military Strategy', "Preceptory of the Knight's Templar"],
        'wonders':   ['The Grand Exchange', 'The Eternal Sepulchre'],
        'actions':   ['Tithe', 'Muster', 'Repair'],
        'factions':  ['The Iron Throne', 'The Grand Compact', 'The Pale Throne', 'The Merchant Republics'],
        'radar': {'military_solutions': 3, 'economy_generators': 4, 'faith_management': 4, 'doubt_warfare': 1,
                  'political_control': 3, 'board_presence': 3, 'degenerate_punishment': 2},
    },
    # ---- centre ----
    'Astravantheliad': {
        'type': 'centre', 'domains': ['Piety', 'Prowess', 'Cunning', 'Industry'],
        'monuments': ['Senate Hall', 'Studium Generale'],
        'wonders':   ['High Chancery'],
        'actions':   ['Negotiate', 'Sign Treaty', 'End Treaty'],
        'factions':  ['The Dukedom', 'The Eternal Court', 'The Illuminated Order', 'The Luminous Court',
                      'The Inner Circle'],
        'radar': {'military_solutions': 2, 'economy_generators': 3, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 5, 'board_presence': 2, 'degenerate_punishment': 3},
    },
}


# ── NODES — THE master node graph. EDIT HERE (CSVs are retired/exported). ──
# Per node: rules text (type/unlock/mastery_req/innate/mastery/builds_into),
# 'escalation' = Escalation talent-tree view (presence = membership),
# The legacy 'engine' field is retired (Oct 19 2026): the sim reads HOLDING_SIM, which is derived
# from SIMPLE_NODES text (innate / unlock / efficient / root / monument) — see the bottom of this file.
NODES = {
    "Quarry": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "-",
        "innate": "+500; Natural; Craft +1",
        "mastery": "",
        "builds_into": ["Masonry", "Market Square"],
        "monument": False},
    "Salt Works": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "-",
        "innate": "+500; Natural; Craft +1",
        "mastery": "",
        "builds_into": ["Smokehouse", "Harbor", "Reliquary", "Levy Hall", "Butchery", "Market Square", "Supply Depot"],
        "monument": False},
    "Apiary": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "-",
        "innate": "+500; Natural; Craft +1",
        "mastery": "",
        "builds_into": ["Chandlery", "Alchemy", "Vineyard", "Orchard", "Meadery", "Market Square"],
        "monument": False},
    "Peat Bog": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "-",
        "innate": "+500; Natural; Craft +1",
        "mastery": "",
        "builds_into": ["Alchemy", "Herb Garden", "Vineyard", "Orchard", "Market Square"],
        "monument": False},
    "Forestry": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "-",
        "innate": "+500; Natural; Craft +1",
        "mastery": "",
        "builds_into": ["Carpentry", "Kiln", "Charcoal Burner", "Market Square"],
        "monument": False},
    "Fishmongery": {
        "type": "Raw Materials",
        "unlock": "Water Settlement",
        "mastery_req": "-",
        "innate": "+500; Natural; Craft +2",
        "mastery": "",
        "builds_into": ["Harbor", "Market Square"],
        "monument": False},
    "Mine": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "-",
        "innate": "+500; Natural; Craft +1",
        "mastery": "",
        "builds_into": ["Furnace", "Jewelry Foundry", "Market Square"],
        "monument": False},
    "Arable Land": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "-",
        "innate": "+500; Natural; Craft +1",
        "mastery": "",
        "builds_into": ["Granary", "Herb Garden", "Animal Husbandry", "Bakery", "Vineyard", "Orchard", "Saddlery", "Market Square", "Artisan Workshop"],
        "monument": False},
    "Common Land": {
        "type": "Raw Materials",
        "unlock": "-",
        "mastery_req": "-",
        "innate": "+1000; Natural, Doubt +1",
        "mastery": "",
        "builds_into": ["Workyard", "Burgages", "Market Square"],
        "monument": False},
    "Herb Garden": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land or Peat Bog",
        "innate": "+500; Natural",
        "mastery": "Craft +1",
        "efficient": "Arable Land",
        "builds_into": ["Apothecary", "Spice Merchant", "Infirmary"],
        "monument": False,
    },
    "Animal Husbandry": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land",
        "innate": "Natural, Unlock Crude armor and shield.",
        "mastery": "+500",
        "efficient": "Arable Land",
        "builds_into": ["Saddlery", "Tannery", "Stable", "Weavery", "Butchery"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Gambeson armor"}, "row": 1, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
    },
    "Saddlery": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land + Animal Husbandry + Stable",
        "innate": "+500; Natural",
        "mastery": "Speed +1; Unlocks Lance (Still requires Tier Unlock)",
        "efficient": ["Stable", "Caravanery"],
        "builds_into": [],
        "monument": False,
    },
    "Vineyard": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land + Apiary or Peat Bog",
        "innate": "+500; Natural",
        "mastery": "+500 in Fall",
        "builds_into": ["Winery"],
        "monument": False},
    "Orchard": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land + Apiary or Peat Bog",
        "innate": "+800; Natural",
        "mastery": "+400 in Fall",
        "builds_into": ["Cidery"],
        "monument": False},
    "Carpentry": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Forestry",
        "innate": "Build Timer -1",
        "mastery": "+300; Craft +1",
        "efficient": "Forestry",
        "builds_into": ["Joinery", "Fletchery", "Artisan Workshop", "Trade Guild", "Shipyard", "Stable", "Mill"],
        "monument": False,
    },
    "Alchemy": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Apiary or Peat Bog",
        "innate": "+500",
        "mastery": "Craft +1",
        "efficient": "Peat Bog",
        "builds_into": ["Academy", "Infirmary", "Toxicarium", "Apothecary"],
        "monument": False,
    },
    "Masonry": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Quarry",
        "innate": "Build Timer -1",
        "mastery": "Craft +1",
        "efficient": "Quarry",
        "builds_into": ["Courtyard", "Episcopal Court", "Trade Guild", "Citadel", "Mill"],
        "monument": False},
    "Butchery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Animal Husbandry + Smokehouse + Salt Works",
        "innate": "Natural; +500",
        "mastery": "Upkeep -200; Craft +1",
        "efficient": "Smokehouse",
        "builds_into": [],
        "monument": False,
    },
    "Bakery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Arable Land + Mill",
        "innate": "Natural; Faith +1",
        "mastery": "+500; Craft +2",
		"efficient": "Mill",
        "builds_into": ["Mill"],
        "monument": False},
    "Weavery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Merchant Quarter + Animal Husbandry",
        "innate": "+500",
        "mastery": "+500; Craft +2",
        "efficient": "Market Square",
        "builds_into": ["Artisan Workshop", "Mill"],
        "monument": False},
    "Fletchery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Carpentry",
        "innate": "Unlocks Ranged Weapons",
        "mastery": "Upkeep -200",
        "efficient": "Carpentry",
        "builds_into": ["Tiltyard"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Ranged weapons"}, "row": 1, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
    },
    "Chandlery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Apiary",
        "innate": "Craft +1",
        "mastery": "Authority -1 to Cunning envoys targeting you",
        "efficient": "Apiary",
        "builds_into": ["Reliquary", "Pilgrimage Site"],
        "monument": False},
    "Tannery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Animal Husbandry",
        "innate": "Natural; Unlocks Cast armor & shield.",
        "mastery": "Upkeep -200; Craft +1",
        "efficient": "Animal Husbandry",
        "builds_into": ["Armory"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Leather armor"}, "row": 2, "gate": None, "requires_all": ["Animal Husbandry"], "requires_any": [], "extra_req": ""},
    },
    "Joinery": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "Carpentry",
        "innate": "unlocks Shields",
        "mastery": "Upkeep -200",
        "efficient": "Carpentry",
        "builds_into": ["Winery", "Cidery"],
        "monument": False,
        "escalation": {"standing": "Rising Industry", "ranks": {1: "Shields"}, "row": 2, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
    },
    "Furnace": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Mine",
        "innate": "Unlocks Cast Weapons",
        "mastery": "+500",
        "efficient": "Mine",
        "builds_into": ["Blacksmith", "Jewelry Foundry"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Cast weapons"}, "row": 1, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
    },
    "Blacksmith": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "Furnace",
        "innate": "Craft +1",
        "mastery": "Unlocks Wrought Tier",
        "efficient": "Furnace",
        "builds_into": ["Forge", "Armory", "Stable", "Siege Works", "Master Workshop", "Gilded Foundry"],
        "monument": False,
        "escalation": {"standing": "Rising Industry", "ranks": {1: "Wrought weapons"}, "row": 2, "gate": None, "requires_all": ["Furnace"], "requires_any": [], "extra_req": ""},
    },
    "Jewelry Foundry": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Mine + Merchant Quarter + Furnace",
        "innate": "+500; Authority +1 to Cunning envoys targeting this player",
        "mastery": "+800; Craft +2 ",
        "efficient": "Gilded Foundry",
        "builds_into": [],
        "monument": False},
    "Armory": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "Tannery + Blacksmith",
        "innate": "Unlock Wrought armor & shield",
        "mastery": "Upkeep -300; Craft +1",
        "efficient": "Tannery",
        "builds_into": ["Gilded Foundry"],
        "monument": False,
        "escalation": {"standing": "Rising Industry", "ranks": {1: "Chainmail"}, "row": 3, "gate": None, "requires_all": ["Tannery"], "requires_any": [], "extra_req": ""},
    },
    "Master Workshop": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Blacksmith",
        "innate": "Upkeep -200; Craft +1",
        "mastery": "Add Serrated to Weapons",
        "efficient": "Forge",
        "builds_into": ["Advanced Blast Furnace", "Artillery Park"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: "Serrated"}, "row": 5, "gate": None, "requires_all": ["Stable"], "requires_any": [], "extra_req": ""},
    },
    "Gilded Foundry": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Armory + Blacksmith",
        "innate": f"{PLANISHING}: Your to-Save can't be reduced beyond {CAP_THR}+.",
        "mastery": "Unlock Forged armor and shield. Craft +1.",
        "efficient": "Armory",
        "builds_into": ["Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: f"Full Plate + {PLANISHING}"}, "row": 5, "gate": None, "requires_all": ["Stable"], "requires_any": [], "extra_req": ""},
    },
    "Smokehouse": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Kiln + Charcoal Burner or Salt Works",
        "innate": "Natural; Craft +2",
        "mastery": "Upkeep -500",
        "efficient": ["Salt Works","Charcoal Burner"],
        "builds_into": ["Supply Depot", "Butchery"],
        "monument": False,
    },
    "Workyard": {
        "type": "Craft",
        "unlock": "—",
        "mastery_req": "Common Land",
        "innate": "Natural; Doubt +1; +500",
        "mastery": "+500",
        "efficient": "Common Land",
        "builds_into": ["Census Hall", "Storehouse"],
        "monument": False},
    "Storehouse": {
        "type": "Craft",
        "unlock": "Sovereign Industry",
        "mastery_req": "Workyard + Shipyard",
        "innate": "Doubt +1; +600",
        "mastery": "Build Timer -2; +600",
        "efficient": "Shipyard",
        "builds_into": ["Office of Works"],
        "monument": False},
    "Meadery": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Apiary + Inn",
        "innate": "Natural; Faith +1",
        "mastery": "Speed +2 in Winter",
        "efficient": "Apiary",
        "builds_into": [],
        "monument": False},
    "Winery": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Vineyard + Joinery",
        "innate": "Natural; +800",
        "mastery": "Craft +3",
        "efficient": "Vineyard",
        "builds_into": ["Manor House"],
        "monument": False},
    "Cidery": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Orchard + Joinery + Inn",
        "innate": "Natural; Faith +1",
        "mastery": "+800; Craft +1",
        "efficient": "Orchard",
        "builds_into": [],
        "monument": False},
    "Market Square": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "2 Raw Materials",
        "innate": "Craft +2",
        "mastery": "+500",
        "efficient": "Courtyard",
        "builds_into": ["Inn", "Merchant Quarter", "Census Hall", "Thieves' Guild", "Caravanery", "Black Market", "Manor House"],
        "monument": False},
    "Inn": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Caravanery + Market Square",
        "innate": "Faith +1 for trading partners with Craft 3+",
        "mastery": "Faith +1",
        "efficient": ["Market Square", "Merchant Quarter"],
        "builds_into": ["Meadery", "Cidery", "Courier Network", "Smuggler's Nook"],
        "monument": False},
    "Spice Merchant": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Caravanery + Merchant Quarter + Herb Garden",
        "innate": "Natural; +500; Authority +1 to Cunning envoys targeting you",
        "mastery": "+500; Craft +2",
        "efficient": "Herb Garden",
        "builds_into": [],
        "monument": False},
    "Harbor": {
        "type": "Craft",
        "unlock": "Water Settlement",
        "mastery_req": "Fishmongery + Salt Works",
        "innate": "+500; Craft +2",
        "mastery": "Extort 200 per player without Harbor",
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
        "builds_into": ["Money Lending", "Court Artists", "Spice Merchant", "Jewelry Foundry", "Weavery", "Caravanery"],
        "monument": False},
    "Money Lending": {
        "type": "Power",
        "unlock": "Established Industry",
        "mastery_req": "Merchant Quarter",
        "innate": "Extort 1000",
        "mastery": "May loan money to Trade Partners at 100 per 1000/turn interest(minimum 100); on Default: Perform Demand Tribute",
        "efficient": "Merchant Quarter",
        "builds_into": ["Aristocratic Court"],
        "monument": False},
    "Census Hall": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Workyard + Market Square",
        "innate": "Doubt +1; +500",
        "mastery": "+500",
        "efficient": "Market Square",
        "builds_into": ["Office of Works"],
        "monument": False},
    "Caravanery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Market Square or Merchant Quarter + Stable",
        "innate": "Natural; Authority -1 to Intercept Caravan actions targeting your settlements",
        "mastery": "Craft +2; Speed -2 to non-allied players in your Province.",
        "efficient": "Stable",
        "builds_into": ["Inn", "Spice Merchant", "Courier Network", "Toll House", "Outrider Intercept Post"],
        "monument": False,
    },
    "Stable": {
        "type": "Civic",
        "unlock": "1 Rising",
        "mastery_req": "Animal Husbandry + Blacksmith or Carpentry",
        "innate": "Speed +1; Natural",
        "mastery": "Speed +1; Unlocks Cavalry Spear (Still requires Tier Unlock)",
        "efficient": "Animal Husbandry",
        "builds_into": ["Saddlery", "Advanced Blast Furnace", "Caravanery"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Cavalry weapons"}, "row": 4, "gate": 3, "requires_all": [], "requires_any": ["Forge", "Armory"], "extra_req": ""},
    },
    "Shipyard": {
        "type": "Craft",
        "unlock": "Established Industry, Water Settlement",
        "mastery_req": "Carpentry + Harbor",
        "innate": "Craft +2",
        "mastery": "Craft +2; Water Territory treated as Grassland for movement",
        "efficient": "Harbor",
        "builds_into": ["Storehouse"],
        "monument": False},
    "Coliseum": {
        "type": "Civic",
        "unlock": "Rising Prowess",
        "mastery_req": "Conditioning Field",
        "innate": "Faith +1 while at War",
        "mastery": "Unlocks Man-at-Arms for Muster",
        "efficient": "Conditioning Field",
        "builds_into": ["Tiltyard", "Grand Tournament"],
        "monument": False,
        "escalation": {"standing": "Rising Prowess", "ranks": {1: "Man-at-Arms unlock"}, "row": 2, "gate": None, "requires_all": ["Conditioning Field"], "requires_any": [], "extra_req": ""},
    },
    "Interrogation Chambers": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Episcopal Court",
        "innate": "Extort 500",
        "mastery": "Cunning actions targeting this player that cause Doubt are reduced by 2.",
        "efficient": "Episcopal Court",
        "builds_into": ["Execution Dock"],
        "monument": False},
    "Abbey": {
        "type": "Civic",
        "unlock": "Established Piety",
        "mastery_req": "Episcopal Court + Academy",
        "innate": "Once per turn: Authority +1 another player's Piety Envoy",
        "mastery": "Morale +1",
        "efficient": "Academy",
        "builds_into": ["Monastery"],
        "monument": False,
    },
    "Reliquary": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Salt Works + Chandlery + Cathedral",
        "innate": "+500",
        "mastery": "First Doubt each Empire Phase reduced by 1 (min 0)",
        "efficient": "Chandlery",
        "builds_into": ["Pilgrimage Site"],
        "monument": False},
    "Monastery": {
        "type": "Power",
        "unlock": "Established Piety",
        "mastery_req": "Abbey",
        "innate": "Authority -1 to Piety envoys targeting you",
        "mastery": "Other players can't Oppose your Piety Envoys",
        "efficient": "Abbey",
        "builds_into": ["Inquisitorial Palace", "Papal Palace"],
        "monument": False,
    },
    "Bell Tower": {
        "type": "Civic",
        "unlock": "1 Established",
        "mastery_req": "Jester's Court",
        "innate": "Influence +1 each Empire Phase",
        "mastery": "Authority +1 to envoys sent during the Council Phase.",
        "efficient": "Jester's Court",
        "builds_into": ["Embassy"],
        "monument": False},
    "Execution Dock": {
        "type": "Civic",
        "unlock": "Established Piety",
        "mastery_req": "Interrogation Chambers",
        "innate": "Authority -1 to Foster Rebellion actions targeting your settlements",
        "mastery": "Players who target you or your settlements with actions that cause doubt gain Doubt +2",
        "efficient": "Interrogation Chambers",
        "builds_into": ["Inquisitorial Palace", "Imperial Palace"],
        "monument": False},
    "Hospitaller": {
        "type": "Power",
        "unlock": "Established Piety",
        "mastery_req": "Apothecary + Infirmary",
        "innate": "Recover improved by +1",
        "mastery": f"Enduring: Successful Recovered rolls do not count towards the panic check threshold.",
        "efficient": "Infirmary",
        "builds_into": ["Preceptory of the Knight's Templar"],
        "monument": False,
        "escalation": {"standing": "Established Piety", "ranks": {1: f"Recover 6; {ENDURING}"}, "row": 4, "gate": None, "requires_all": ["Infirmary"], "requires_any": [], "extra_req": ""},
    },
    "Jester's Court": {
        "type": "Civic",
        "unlock": "1 Rising",
        "mastery_req": "Courtyard",
        "innate": "First Oppose on your Envoy each turn: reduce by 1",
        "mastery": "Second Oppose on your Envoy each turn: reduce by 1",
        "efficient": "Courtyard",
        "builds_into": ["Bell Tower"],
        "monument": False},
    "Embassy": {
        "type": "Civic",
        "unlock": "1 Established",
        "mastery_req": "Bell Tower + Jester's Court",
        "innate": "Authority +1 to Diplomacy Envoys",
        "mastery": "Whenever a player performs a Diplomacy Envoy targeting you, that envoy cannot be Opposed.",
        "efficient": "Jester's Court",
        "builds_into": ["Senate Hall"],
        "monument": False},
    "Granary": {
        "type": "Civic",
        "unlock": "Rising Industry",
        "mastery_req": "Arable Land",
        "innate": "Upkeep -500; Natural",
        "mastery": "Armies and Garrisons gain Endurance while Besieged",
        "efficient": "Arable Land",
        "builds_into": ["Supply Depot", "Citadel"],
        "monument": False},
    "Academy": {
        "type": "Civic",
        "unlock": "1 Rising",
        "mastery_req": "Library + Alchemy",
        "innate": "Authority +1 to Council Envoys",
        "mastery": "Authority +1 to non-Council Envoys",
        "efficient": "Alchemy",
        "builds_into": ["University", "Abbey", "War College", "Forgery Workshop", "Toxicarium", "College of Engineering", "Ministry of Military Strategy", "Studium Generale"],
        "monument": False,
    },
    "Courtyard": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Masonry",
        "innate": "Craft +1",
        "mastery": "Faith +1",
        "efficient": ["Masonry"],
        "builds_into": ["Conditioning Field", "Jester's Court", "Market Square"],
        "monument": False},
    "Episcopal Court": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Masonry",
        "innate": "Faith +1",
        "mastery": "Reduce the first instance of Doubt each Empire Phase by 1, min 0.",
        "builds_into": ["Interrogation Chambers", "Abbey"],
        "monument": False,
		"efficient": "Courtyard"},
    "Conditioning Field": {
        "type": "Civic",
        "unlock": "Rising Prowess",
        "mastery_req": "Courtyard",
        "innate": "Faith +1 while not at War",
        "mastery": "Armies gain Nimble",
        "efficient": "Courtyard",
        "builds_into": ["Coliseum", "Grand Tournament"],
        "monument": False,
        "escalation": {"standing": "Untested Prowess", "ranks": {1: "Nimble"}, "row": 1, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
    },
    "Grand Tournament": {
        "type": "Civic",
        "unlock": "Established Prowess",
        "mastery_req": "Coliseum + Conditioning Field",
        "innate": "Faith +1; Improve Parry by +1.",
        "mastery": "3x per Envoy Phase: exchange 500 gold for Influence +1; Armies gain Riposte",
        "efficient": "Coliseum",
        "builds_into": ["Royal Pavilion"],
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Riposte"}, "row": 4, "gate": None, "requires_all": ["Coliseum"], "requires_any": [], "extra_req": ""},
    },
    "Apothecary": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Herb Garden + Alchemy",
        "innate": "+300",
        "mastery": f"Gain Recover {RECOVER_BASE}, or improve Recover by +1.",
        "efficient": "Alchemy",
        "builds_into": ["Hospitaller"],
        "monument": False,
        "escalation": {"standing": "Untested Piety", "ranks": {1: "Recover 8"}, "row": 1, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
    },
    "Infirmary": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Alchemy + Herb Garden",
        "innate": "+500",
        "mastery": "Improve Recover by +1",
        "efficient": "Apothecary",
        "builds_into": ["Hospitaller"],
        "monument": False,
        "escalation": {"standing": "Untested Piety", "ranks": {1: "Recover 7"}, "row": 2, "gate": None, "requires_all": ["Apothecary"], "requires_any": [], "extra_req": ""},
    },
    "Supply Depot": {
        "type": "Civic",
        "unlock": "Rising Industry",
        "mastery_req": "Granary or Smokehouse + Salt Works",
        "innate": "Craft +2",
        "mastery": "May Muster an Army in a Settlement under Siege and its Muster Timers count down.",
        "efficient": "Granary",
        "builds_into": ["Citadel"],
        "monument": False},
    "Artisan Workshop": {
        "type": "Civic",
        "unlock": "Established Industry",
        "mastery_req": "Carpentry + Arable Land + Weavery",
        "innate": "+500",
        "mastery": "+500; Faith +1",
        "efficient": "Weavery",
        "builds_into": ["Court Artists"],
        "monument": False},
    "University": {
        "type": "Power",
        "unlock": "1 Established",
        "mastery_req": "Academy",
        "innate": "May spend one additional Influence per Support or Oppose",
        "mastery": "Influence +1 per Domain you are Rising",
        "efficient": "Academy",
        "builds_into": ["Studium Generale"],
        "monument": False,
    },
    "Trade Guild": {
        "type": "Civic",
        "unlock": "Rising Industry",
        "mastery_req": "Masonry or Carpentry",
        "innate": "No Upkeep on Primitive Infrastructure",
        "mastery": "No Upkeep on Developed Infrastructure",
        "efficient": "Masonry",
        "builds_into": ["College of Engineering"],
        "monument": False},
    "Court Artists": {
        "type": "Civic",
        "unlock": "Established Industry",
        "mastery_req": "Merchant Quarter + Artisan Workshop",
        "innate": "Extort 500; Faith +1",
        "mastery": "Extort 500; Targets of Extort from this Court Artist gain Faith +1",
        "efficient": "Artisan Workshop",
        "builds_into": ["Aristocratic Court"],
        "monument": False},
    "Courier Network": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Caravanery + Inn",
        "innate": "Once per turn: Authority -1 on Target Envoy",
        "mastery": "Once per turn: successfully Performed Personal Envoy can be Performed next turn; send 1 fewer Envoys next turn",
        "efficient": "Inn",
        "builds_into": ["Toll House", "Beacon Towers", "Outlaw Rookery", "Cipher Chamber"],
        "monument": False},
    "Toll House": {
        "type": "Civic",
        "unlock": "—",
        "mastery_req": "Caravanery + Courier Network",
        "innate": "Natural; Once per turn when an Army ends a Move action within your Province: Perform a Diplomacy action targeting that army's player",
        "mastery": "Extort 2000 when non-Allied Army ends a Move action within your Province",
        "efficient": "Caravanery",
        "builds_into": ["Beacon Towers"],
        "monument": False},
    "College of Engineering": {
        "type": "Power",
        "unlock": "Established Industry",
        "mastery_req": "Academy + Trade Guild",
        "innate": "No Upkeep on Sophisticated Infrastructure",
        "mastery": "Build Timer -2",
        "efficient": "Trade Guild",
        "builds_into": ["Office of Works"],
        "monument": False},
    "Secret Cellar": {
        "type": "Energy",
        "unlock": "Rising Cunning",
        "mastery_req": "Smuggler's Nook",
        "innate": "Natural; Failed Cunning envoys Recoup 500 Gold",
        "mastery": "Passed Cunning envoys Recoup 500 Gold",
        "efficient": ["Secrecy","Thieves' Guild", "Outlaw Rookery", "Outrider Intercept Post"],
        "builds_into": ["Smuggler's Nook", "Forgery Workshop", "Forgotten Catacombs", "Thieves' Guild"],
        "monument": False},
    "Smuggler's Nook": {
        "type": "Secrecy",
        "unlock": "Established Cunning",
        "mastery_req": "Secret Cellar + Inn",
        "innate": "gain Immune Uprising (Bandit Camp Spawn at -5PO)",
        "mastery": "Bandit Camps in your Outlaw Country don't target you and instead target other players randomly.",
        "efficient": ["Inn", "Courier Network", "Secret Cellar"],
        "builds_into": ["Thieves' Guild", "Outlaw Rookery", "Secret Cellar", "Black Market"],
        "monument": False},
    "Black Market": {
        "type": "Secrecy",
        "unlock": "Established Cunning",
        "mastery_req": "Market Square + Smuggler's Nook",
        "innate":  "When another player Extorts gold from any source: Extort 200 per 1000 (minimum 100) from that player at the end of that resolution.",
        "mastery": "When another player Recoups gold from any source: Extort 200 per 1000 (minimum 100) from that player at the end of that resolution.",
        "efficient": ["Smuggler's Nook", "Secret Cellar"],
        "builds_into": ["Thieves' Guild"],
        "monument": False},
    "Forgery Workshop": {
        "type": "Secrecy",
        "unlock": "Established Cunning",
        "mastery_req": "Academy + Secret Cellar",
        "innate": "Extort 300 anytime a player Opposes an Envoy of yours",
        "mastery": "Once per Envoy Phase: attempt another Cunning Envoy targeting a different player if your Cunning Envoy Failed",
        "efficient": ["Academy", "University", "Secret Cellar"],
        "builds_into": ["Aristocratic Court", "Cipher Chamber"],
        "monument": False},
    "Toxicarium": {
        "type": "Secrecy",
        "unlock": "Rising Cunning",
        "mastery_req": "Academy + Alchemy",
        "innate": "Weapons gain Poison",
        "mastery": "All Endorsed Cunning actions give an additional Doubt +1 to Target",
        "efficient": ["Alchemy", "Forgotten Catacombs"],
        "builds_into": ["Outlaw Rookery"],
        "monument": False,
        "escalation": {"standing": "Rising Cunning", "ranks": {1: "Poison"}, "row": 2, "gate": None, "requires_all": [], "requires_any": [], "extra_req": ""},
    },
    "Pilgrimage Site": {
        "type": "Energy",
        "unlock": "Established Piety",
        "mastery_req": "Reliquary + Chandlery",
        "innate": "Natural; Extort 500 every player without a Pilgrimage Site",
        "mastery": "Doubt +1 to all other players without a Pilgrimage Site",
        "efficient": "Reliquary",
        "builds_into": ["Preceptory of the Knight's Templar", "Papal Palace"],
        "monument": False,
    },
    "Beacon Towers": {
        "type": "Energy",
        "unlock": "Rising Prowess",
        "mastery_req": "Courier Network + Toll House",
        "innate": "Natural; At the Start of the Empire Phase, you may select an Army within your Province and move it up to its modified Speed.",
        "mastery": "Whenever a non-allied Army ends a Move action within your Province, you may immediately perform a Move action",
        "efficient": "Toll House",
        "builds_into": [],
        "monument": False},
    "Forgotten Catacombs": {
        "type": "Secrecy",
        "unlock": "Rising Cunning",
        "mastery_req": "Secret Cellar",
        "innate": "Whenever you are the target of Extort, reduce the Extort amount by 100.",
        "mastery": "Cunning envoys against you can't be Endorsed",
        "efficient": "Secret Cellar",
        "builds_into": [],
        "monument": False},
    "Charcoal Burner": {
        "type": "Energy",
        "unlock": "Established Industry",
        "mastery_req": "Forestry + Kiln",
        "innate": "Natural",
        "mastery": "+500",
        "efficient": ["Forestry", "Kiln"],
        "builds_into": ["Smokehouse"],
        "monument": False},
    "Mill": {
        "type": "Energy",
        "unlock": "Rising Industry",
        "mastery_req": "Bakery/Weavery/Forge/Carpentry/Masonry",
        "innate": "Natural",
        "mastery": "+500",
        "efficient": ["Bakery", "Weavery", "Forge", "Carpentry","Masonry"],
        "builds_into": ["Bakery","Manor House"],
        "monument": False},
    "Kiln": {
        "type": "Energy",
        "unlock": "Rising Industry",
        "mastery_req": "Forestry",
        "innate": "Natural",
        "mastery": "+500",
        "efficient": "Forestry",
        "builds_into": ["Smokehouse", "Charcoal Burner"],
        "monument": False},
    "Burgages": {
        "type": "Energy",
        "unlock": "-",
        "mastery_req": "Common Land",
        "innate": "+200; Natural",
        "mastery": "Faith +1",
        "efficient": "Common Land",
        "builds_into": [],
        "monument": False},
    "Levy Hall": {
        "type": "Power",
        "unlock": "Rising Prowess",
        "mastery_req": "Garrison + Salt Works",
        "innate":  "Natural; Upkeep -1000 while an Army is within Range 0 of a Settlement you Control",
        "mastery": "Upkeep -1000 while an Army is within Range 0 of a Settlement you Control",
        "builds_into": ["War College"],
        "efficient": "Butchery",
        "monument": False,
    },
    "Siege Works": {
        "type": "Power",
        "unlock": "Rising Prowess",
        "mastery_req": "Blacksmith",
        "innate": "Siege Timer -1",
        "mastery": "Siege Timer -1; Siege Timers count down in Winter",
        "builds_into": ["Siege Camp"],
        "monument": False},
    "Siege Camp": {
        "type": "Power",
        "unlock": "Established Prowess",
        "mastery_req": "Siege Works",
        "innate": "Siege Timer -1",
        "mastery": "Armies gain Immune Strained during Lay Siege",
        "efficient": "Siege Works",
        "builds_into": ["Artillery Park"],
        "monument": False},
    "Citadel": {
        "type": "Power",
        "unlock": "Established Industry",
        "mastery_req": "Masonry + Granary or Supply Depot",
        "innate": "Siege Timer +1",
        "mastery": "Siege Timer +2, Controlled Settlements gain Reach +1",
        "efficient": ["Granary", "Supply Depot"],
        "builds_into": ["Imperial Palace"],
        "monument": False},
    "War College": {
        "type": "Power",
        "unlock": "Established Prowess",
        "mastery_req": "Levy Hall + Academy",
        "innate": "Gain Influence +2 while At War",
        "mastery": "Unlocks Sergeants for Muster",
        "efficient": "Academy",
        "builds_into": ["Ministry of Military Strategy"],
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Sergeant unlock"}, "row": 4, "gate": None, "requires_all": ["Coliseum"], "requires_any": [], "extra_req": ""},
    },
    "Forge": {
        "type": "Power",
        "unlock": "Established Industry",
        "mastery_req": "Blacksmith",
        "innate": "Craft +2",
        "mastery": "Unlocks Forged Tier",
        "efficient": "Blacksmith",
        "builds_into": ["Mill", "Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: "Forged weapons"}, "row": 3, "gate": None, "requires_all": ["Blacksmith"], "requires_any": [], "extra_req": ""},
    },
    "Tiltyard": {
        "type": "Power",
        "unlock": "Established Prowess",
        "mastery_req": "Fletchery + Coliseum",
        "innate": "Armies may be equipped with a Ranged and a Melee Weapon simultaneously; If so, the army gains Unwieldy",
        "mastery": "Your armies gain Immune Unwieldy. Also, may equip two of the same 1H Melee Weapon to gain Dual Wield.",
        "builds_into": ["Royal Pavilion"],
        "efficient": "Fletchery",
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Dual-equip; Immune Unwieldy; Dual Wield (two of a kind)"}, "row": 4, "gate": None, "requires_all": ["Coliseum"], "requires_any": [], "extra_req": ""},
    },
    "Office of Works": {
        "type": "Monument",
        "unlock": "Sovereign Industry",
        "mastery_req": "College of Engineering + Storehouse",
        "innate": "Settlements & allied armies inside them are not affected by 'Settlements being Besieged' restrictions.",
        "mastery": "Siege Timer +2; Build Timer -2",
        "efficient": "College of Engineering",
        "builds_into": [],
        "monument": True},
    "Royal Pavilion": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "Grand Tournament + Tiltyard",
        "innate": "Armies gain Immune Strained. Improve Parry by +1",
        "mastery": "Gain +1 to Strike. Deadly, & Cleave also trigger Focused Strikes on a natural 8+.",
		"efficient": "Tiltyard",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Prowess", "ranks": {1: "Immune Strain; Drilled"}, "row": 6, "gate": None, "requires_all": ["Tiltyard", "Grand Tournament"], "requires_any": [], "extra_req": ""},
    },
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
        "mastery": "Settlements you Siege can't Sally Forth. Siege Timer -1.",
        "efficient": "Siege Camp",
        "builds_into": [],
        "monument": True,
    },
    "Ministry of Military Strategy": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "Academy + War College",
        "innate": "Always gains Seize the Initiative, and your opponent doesn't; max initiative is increased to 3",
        "mastery": "Gain Drilled.",
        "efficient": "War College",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Prowess", "ranks": {1: "Always Seize the Initiative; your maximum initiative increases to 3.", 2: "Deadly, & Cleave also trigger on a natural 8+."}, "row": 6, "gate": None, "requires_all": ["War College"], "requires_any": [], "extra_req": ""},
    },
    "Thieves' Guild": {
        "type": "Monument",
        "unlock": "Sovereign Cunning",
        "mastery_req": "Market Square + Smuggler's Nook + Secret Cellar + Black Market",
        "innate": "Whenever another player performs a Cunning action, you may recoup 1000 gold",
        "mastery": "Extort 25% of Trade Income from players who don't trade with you",
        "efficient": ["Black Market", "Secret Cellar"],
        "builds_into": [],
        "monument": True},
    "Senate Hall": {
        "type": "Monument",
        "unlock": "1 Sovereign",
        "mastery_req": "Embassy + Library + Town Hall",
        "innate": "Faith +1, gain Influence +1 per other player each Empire Phase",
        "mastery": "Once per Envoy Phase: before players vote on an Envoy you choose, you may Condemn it if it's an At War player's Envoy, or Endorse it if it's an Ally's Envoy",
        "efficient": "Embassy",
        "builds_into": [],
        "monument": True},
    "Papal Palace": {
        "type": "Monument",
        "unlock": "Sovereign Piety",
        "mastery_req": "Monastery + Pilgrimage Site",
        "innate": "Your Piety actions that cause doubt cause an additional doubt. You no longer pay cost for Piety Envoys.",
        "mastery": "Each Empire Phase, Tithe every other player with lower Piety, resolved in the Extort step.",
        "efficient": ["Monastery"],
        "builds_into": [],
        "monument": True},
    "Inquisitorial Palace": {
        "type": "Monument",
        "unlock": "Sovereign Piety",
        "mastery_req": "Execution Dock + Monastery",
        "innate": "Doubt +1; Unlocks Grand Vizier which uses your Public Order instead of your Cunning value.",
        "mastery": "You may use your Piety Value as Cunning Value for Grand Vizier.",
        "efficient": "Monastery",
        "builds_into": [],
        "monument": True},
    "Preceptory of the Knight's Templar": {
        "type": "Monument",
        "unlock": "Sovereign Piety + Established Prowess",
        "mastery_req": "Pilgrimage Site + Hospitaller",
        "innate": f"Armies gain {CRUSADER}: Automatically pass the first Panic Check of every Battle.",
        "mastery": "Unlocks Knight's Templar for Muster",
        "efficient": "Pilgrimage Site",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Piety", "ranks": {1: f"{CRUSADER}", 2: "Knight Templar unlock"}, "row": 6, "gate": None, "requires_all": ["Hospitaller"], "requires_any": [], "extra_req": "Established Prowess"},
    },
    "Manor House": {
        "type": "Monument",
        "unlock": "Established Industry",
        "mastery_req": "Hamlet + Market Square",
        "innate": "Natural; Gain +100 gold for each active natural specialization.",
        "mastery": "Gain +200 gold for each active natural specialization.",
        "efficient": "Natural",
        "builds_into": [],
        "monument": True},
    "Aristocratic Court": {
        "type": "Monument",
        "unlock": "Sovereign Cunning",
        "mastery_req": "Money Lending + Forgery Workshop + Court Artists",
        "innate": "Each Empire Phase, Extort 500 from each non-allied player with a lower Cunning value.",
        "mastery": "Your Vote counts as 2 votes toward Domain selection during the Council Phase.",
        "efficient": ["Court Artists","Money Lending"],
        "builds_into": [],
        "monument": True},
    "Studium Generale": {
        "type": "Monument",
        "unlock": "4 Established",
        "mastery_req": "University + Academy",
        "innate": "Influence +1 per Established Standing",
        "mastery": "May gain one Sovereign Domain effect without spending the Domain Points",
        "efficient": "University",
        "builds_into": [],
        "monument": True},
    "Outlaw Rookery": {
        "type": "Monument",
        "unlock": "Sovereign Cunning",
        "mastery_req": "Smuggler's Nook + Toxicarium + Courier Network",
        "innate": "Both Bandit Camps & you have Authority +1 on Cunning actions.",
        "mastery": "Endorsed Foster Rebellion places Bandit Camps with 25 retinues instead of 10.",
        "efficient": "Smuggler's Nook",
        "builds_into": [],
        "monument": True},
    "Advanced Blast Furnace": {
        "type": "Monument",
        "unlock": "Sovereign Industry",
        "mastery_req": "Gilded Foundry + Master Workshop + Forge + Stable",
        "innate": "Upkeep -500",
        "mastery": "Crafted Tier Unlocked; Craft +2",
        "efficient": "Master Workshop",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Industry", "ranks": {1: "Crafted tier"}, "row": 6, "gate": None, "requires_all": ["Stable", "Master Workshop", "Gilded Foundry"], "requires_any": [], "extra_req": ""},
    },
    "Cipher Chamber": {
        "type": "Secrecy",
        "unlock": "Established Cunning",
        "mastery_req": "Forgery Workshop + Courier Network",
        "innate": "Once per turn when a player Sends an Envoy: that player must declare the specific Action & target they would Perform if the Envoy Passes (including sub-Actions). If it Passes, they must Perform that declared Action at the declared target.",
        "mastery": "Once per turn: select any active Timer you did not select last turn; increase it by 2.",
        "efficient": "Forgery Workshop",
        "builds_into": ["Outrider Intercept Post"],
        "monument": False,
    },
    "Outrider Intercept Post": {
        "type": "Monument",
        "unlock": "Sovereign Cunning",
        "mastery_req": "Caravanery + Cipher Chamber",
        "innate": "In the first Skirmish of every Battle, your opponent plays their Tactic Card face up before you select your own.",
        "mastery": "Every Skirmish, you may force your opponent to reveal their Tactic Card they selected before you select your own.",
        "efficient": "Cipher Chamber",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Cunning", "ranks": {1: "First Skirmish: see enemy Tactic before choosing", 2: "Every Skirmish: see enemy Tactic before choosing"}, "row": 6, "gate": None, "requires_all": ["Toxicarium"], "requires_any": [], "extra_req": ""},
    }
    
}
SIMPLE_NODES = {
    "Quarry": {
        "group": "g_raw",
        "root": True,
        "unlock": "-",
        "innate": "+500; Natural; Craft +1",
        "builds_into": ["Masonry"],
        "monument": False},
    "Salt Works": {
        "group": "g_raw",
        "root": True,
        "unlock": "-",
        "innate": "+500; Natural; Craft +1",
        "builds_into": ["Smokehouse","Workyard"],
        "monument": False},
    "Apiary": {
        "group": "g_raw",
        "root": True,
        "unlock": "-",
        "innate": "+500; Natural; Craft +1",
        "builds_into": ["Chandlery", "Meadery"],
        "monument": False},
    "Peat Bog": {
        "group": "g_raw",
        "root": True,
        "unlock": "-",
        "innate": "+500; Natural; Craft +1",
        "builds_into": ["Alchemy"],
        "monument": False},
    "Forestry": {
        "group": "g_raw",
        "root": True,
        "unlock": "-",
        "innate": "+500; Natural; Craft +1",
        "builds_into": ["Carpentry", "Charcoal Burner", "Kiln"],
        "monument": False},
    "Fishmongery": {
        "group": "g_raw",
        "root": True,
        "unlock": "-",
        "innate": "+500; Natural; Craft +2",
        "builds_into": ["Harbor"],
        "monument": False},
    "Mine": {
        "group": "g_raw",
        "root": True,
        "unlock": "-",
        "innate": "+500; Natural; Craft +1",
        "builds_into": ["Furnace","Siege Works"],
        "monument": False},
    "Arable Land": {
        "group": "g_raw",
        "root": True,
        "unlock": "-",
        "innate": "+500; Natural; Craft +1",
        "efficient": ["Hamlet"],          # may start a Hamlet (Hamlet = location token, not a Holding)
        "builds_into": ["Herb Garden", "Animal Husbandry", "Granary", "Orchard","Vineyard"],
        "monument": False},
    "Common Land": {
        "group": "g_raw",
        "root": True,
        "unlock": "-",
        "innate": "+1000; Natural, Doubt +1",
        "efficient": ["Hamlet"],          # may start a Hamlet (Hamlet = location token, not a Holding)
        "builds_into": ["Workyard", "Burgages"],
        "monument": False},
    "Herb Garden": {
        "group": "g_husbandry",
        "unlock": "-",
        "innate": "+1000; Natural; Craft +1",
        "efficient": "Arable Land",
        "builds_into": ["Spice Merchant"],
        "monument": False},
    "Animal Husbandry": {
        "group": "g_husbandry",
        "unlock": "-",
        "innate": "Natural, Unlock Crude armor and shield. Upkeep -500",
        "efficient": "Arable Land",
        "builds_into": ["Tannery", "Stable"],
        "monument": False},
    "Saddlery": {
        "group": "g_husbandry",
        "unlock": "-",
        "innate": "+500; Natural; Speed +2; Unlocks Lance (Still requires Tier Unlock)",
        "efficient": ["Stable", "Caravanery"],
        "builds_into": [],
        "monument": False},
    "Vineyard": {
        "group": "g_husbandry",
        "unlock": "-",
        "innate": "+500; Natural; +1500 in Fall",
        "efficient": "Arable Land",
        "builds_into": ["Winery"],
        "monument": False},
    "Orchard": {
        "group": "g_husbandry",
        "unlock": "-",
        "innate": "+1500; Natural; +500 in Fall",
        "efficient": "Arable Land",
        "builds_into": ["Cidery"],
        "monument": False},
    "Carpentry": {
        "group": "g_arms",
        "unlock": "-",
        "innate": "Build Timer -1; +500; Craft +1",
        "efficient": "Forestry",
        "builds_into": ["Fletchery", "Joinery", "Mill","Siege Works"],
        "monument": False},
    "Alchemy": {
        "group": "g_commerce",
        "unlock": "-",
        "innate": "+500; Craft +2",
        "efficient": "Peat Bog",
        "builds_into": ["Academy", "Apothecary", "Toxicarium"],
        "monument": False},
    "Masonry": {
        "group": "g_works",
        "unlock": "-",
        "innate": "No Upkeep on Primitive Infrastructure; Build Timer -1",
        "efficient": "Quarry",
        "builds_into": ["Granary", "Trade Guild", "Abbey","Mill"],
        "monument": False},
    "Butchery": {
        "group": "g_logistics",
        "unlock": "-",
        "innate": "Natural; +500; Upkeep -500; Craft +1",
        "efficient": ["Salt Works", "Charcoal Burner"],
        "builds_into": ["Smokehouse"],
        "monument": False},
    "Bakery": {
        "group": "g_husbandry",
        "unlock": "-",
        "innate": "Natural; Faith +1; +1000; Craft +2",
        "efficient": "Meadery",
        "builds_into": ["Mill"],
        "monument": False},
    "Weavery": {
        "group": "g_commerce",
        "unlock": "-",
        "innate": "+2000; Craft +2",
        "efficient": "Market Square",
        "builds_into": ["Artisan Workshop", "Mill"],
        "monument": False},
    "Fletchery": {
        "group": "g_arms",
        "unlock": "-",
        "innate": "Unlocks Ranged Weapons; Upkeep -200",
        "efficient": "Carpentry",
        "builds_into": ["Tiltyard"],
        "monument": False},
    "Chandlery": {
        "group": "g_devotion",
        "unlock": "-",
        "innate": "Craft +1; Authority -1 to Cunning actions targeting you",
        "efficient": "Apiary",
        "builds_into": ["Reliquary"],
        "monument": False},
    "Tannery": {
        "group": "g_arms",
        "unlock": "-",
        "innate": "Natural; Unlocks Cast armor & shield. Upkeep -500; Craft +1",
        "efficient": ["Animal Husbandry","Joinery"],
        "builds_into": ["Armory"],
        "monument": False},
    "Joinery": {
        "group": "g_arms",
        "unlock": "Rising Industry",
        "innate": "unlocks Shields; Upkeep -500",
        "efficient": "Carpentry",
        "builds_into": ["Tannery"],
        "monument": False},
    "Furnace": {
        "group": "g_arms",
        "unlock": "-",
        "innate": "Unlocks Cast Weapons; +500",
        "efficient": "Mine",
        "builds_into": ["Blacksmith"],
        "monument": False},
    "Blacksmith": {
        "group": "g_arms",
        "unlock": "Rising Industry",
        "innate": "Craft +1; +500; Unlocks Wrought Weapons",
        "efficient": "Furnace",
        "builds_into": ["Forge"],
        "monument": False},
    "Jewelry Foundry": {
        "group": "g_commerce",
        "unlock": "-",
        "innate": "+2000; Authority +1 to Cunning actions targeting this player; Craft +5",
        "efficient": "Gilded Foundry",
        "builds_into": [],
        "monument": False},
    "Armory": {
        "group": "g_arms",
        "unlock": "Rising Industry",
        "innate": "Unlock Wrought armor & shield; Upkeep -500; Craft +1",
        "efficient": ["Tannery", "Blacksmith"],
        "builds_into": ["Gilded Foundry"],
        "monument": False},
    "Master Workshop": {
        "group": "g_arms",
        "unlock": "Established Industry",
        "innate": "Upkeep -500; Craft +1; Add Serrated to Weapons",
        "efficient": "Forge",
        "builds_into": ["Advanced Blast Furnace"],
        "monument": False},
    "Gilded Foundry": {
        "group": "g_arms",
        "unlock": "Established Industry",
        "innate": "Upkeep -500; Unlock Forged armor & shield.",
        "efficient": "Armory",
        "builds_into": ["Jewelry Foundry", "Court Armoury"],
        "monument": False},
    "Smokehouse": {
        "group": "g_logistics",
        "unlock": "-",
        "innate": "Natural; Craft +2; Upkeep -500",
        "efficient": ["Butchery"],
        "builds_into": ["Levy Hall"],
        "monument": False},
    "Workyard": {
        "group": "g_works",
        "unlock": "—",
        "innate": "Natural; Doubt +1; +1000",
        "efficient": ["Common Land","Salt Works"],
        "builds_into": ["Burgages"],
        "monument": False},
    "Storehouse": {
        "group": "g_works",
        "unlock": "Established Industry",
        "innate": "Natural; Doubt +1; +2000; Build Timer -1",
        "efficient": ["Census Hall"],
        "builds_into": ["Office of Works"],
        "monument": False},
    "Meadery": {
        "group": "g_husbandry",
        "unlock": "Established Industry",
        "innate": "Natural; Faith +1; Speed +2 in Winter",
        "efficient": "Apiary",
        "builds_into": ["Bakery"],
        "monument": False},
    "Winery": {
        "group": "g_husbandry",
        "unlock": "Established Industry",
        "innate": "Natural; +800; Craft +3",
        "efficient": "Vineyard",
        "builds_into": ["Manor House"],
        "monument": False},
    "Cidery": {
        "group": "g_husbandry",
        "unlock": "Established Industry",
        "innate": "Natural; Faith +1; +800; Craft +1",
        "efficient": "Orchard",
        "builds_into": [],
        "monument": False},
    "Market Square": {
        "group": "g_commerce",
        "unlock": "Rising Industry",
        "infrastructure_req": "Hitching Post",
        "innate": "Craft +2; +500",
        "efficient": "Courtyard",
        "builds_into": ["Inn", "Merchant Quarter", "Census Hall"],
        "monument": False},
    "Inn": {
        "group": "g_court",
        "root": True,
        "unlock": "-",
        "infrastructure_req": "Hitching Post",
        "innate": "Faith +1 per Trade Partner with Craft 3+, and each of those partners gains Faith +1; Influence +1",
        "builds_into": ["Courier Network", "Smuggler's Nook"],
        "monument": False},
    "Spice Merchant": {
        "group": "g_commerce",
        "unlock": "-",
        "innate": "Natural; +1000; Authority +1 to Cunning actions targeting you; Craft +4",
        "efficient": "Herb Garden",
        "builds_into": [],
        "monument": False},
    "Harbor": {
        "group": "g_commerce",
        "unlock": "-",
        "innate": "Craft +2; Can Trade; Extort 500 per player without Harbor",
        "efficient": "Fishmongery",
        "builds_into": ["Shipyard"],
        "monument": False},
    "Merchant Quarter": {
        "group": "g_commerce",
        "unlock": "Rising Industry",
        "innate": "+500; Trade Partners gain Craft +2",
        "efficient": ["Market Square","Courtyard"],
        "builds_into": ["Money Lending"],
        "monument": False},
    "Money Lending": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "Extort 1000; Once per turn, you may loan money to Trade Partners at 100 per 1000/turn interest (minimum 100); on Default: Perform Demand Tribute",
        "efficient": ["Court Artists","Merchant Quarter"],
        "builds_into": ["Aristocratic Court"],
        "monument": False},
    "Census Hall": {
        "group": "g_works",
        "unlock": "-",
        "innate": "Natural; Doubt +1; +1000",
        "efficient": "Burgages",
        "builds_into": ["Office of Works"],
        "monument": False},
    "Caravanery": {
        "group": "g_logistics",
        "unlock": "-",
        "innate": "Natural; Authority -2 to Intercept Caravan actions targeting your settlements; Craft +2; Speed -2 to non-allied armies in your Province.",
        "efficient": ["Saddlery", "Stable"],
        "builds_into": ["Saddlery", "Toll House"],
        "monument": False},
    "Stable": {
        "group": "g_arms",
        "unlock": "1 Rising",
        "innate": "Speed +1; Natural; Unlocks Cavalry Spear (Still requires Tier Unlock)",
        "efficient": "Animal Husbandry",
        "builds_into": ["Saddlery", "Caravanery"],
        "monument": False},
    "Shipyard": {
        "group": "g_commerce",
        "unlock": "Rising Industry",
        "innate": "Craft +4; Can Trade; Water Territory treated as Grassland for movement",
        "efficient": "Harbor",
        "builds_into": ["Storehouse"],
        "monument": False},
    "Coliseum": {
        "group": "g_logistics",
        "unlock": "Rising Prowess",
        "innate": "Faith +1 while at War; Unlocks Man-at-Arms for Muster",
        "efficient": "Conditioning Field",
        "builds_into": ["Grand Tournament"],
        "monument": False},
    "Interrogation Chambers": {
        "group": "g_devotion",
        "unlock": "Rising Piety",
        "innate": "Extort 500; Actions targeting this player that cause Doubt are reduced by 1, to a minimum of 0.",
        "efficient": "Episcopal Court",
        "builds_into": ["Execution Dock"],
        "monument": False},
    "Priory": {
        "group": "g_devotion",
        "unlock": "Rising Piety",
        "innate": "Faith +2",
        "efficient": "Masonry",
        "builds_into": ["Abbey"],
        "monument": False},
    "Abbey": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "innate": "Once per Envoy Phase: Authority +2 another player's Piety Envoy; Authority -1 to Piety actions targeting you",
        "efficient": "Priory",
        "builds_into": ["Monastery"],
        "monument": False},
    "Reliquary": {
        "group": "g_devotion",
        "unlock": "Rising Piety",
        "infrastructure_req": "Cathedral",
        "innate": "+500; First two Doubt each Empire Phase reduced by 1",
        "efficient": "Chandlery",
        "builds_into": ["Pilgrimage Site"],
        "monument": False},
    "Monastery": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "infrastructure_req": "Cathedral",
        "innate": "Reach +1; Other players with lower Piety value can't Oppose your Piety Envoys",
        "efficient": ["Abbey"],
        "builds_into": ["Papal Palace"],
        "monument": False},
    "Execution Dock": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "innate": "Authority -2 to Foster Rebellion actions targeting your settlements; Players who target you or your Settlements with actions that would cause Doubt before modifiers gain Doubt +1",
        "efficient": "Interrogation Chambers",
        "builds_into": ["Inquisitorial Palace"],
        "monument": False},
    "Hospitaller": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "innate": "Recover improved by +1; Enduring: Successful Recovered rolls do not count towards the panic check threshold.",
        "efficient": "Infirmary",
        "builds_into": [],
        "monument": False},
    "Jester's Court": {
        "group": "g_court",
        "unlock": "1 Rising",
        "innate": "First and second Oppose on an Envoy of yours each Envoy Phase: reduce by 1",
        "efficient": "Courtyard",
        "builds_into": ["Bell Tower"],
        "monument": False},
    "Bell Tower": {
        "group": "g_court",
        "unlock": "1 Established",
        "innate": "Influence +1 each Empire Phase; Authority +1 to envoys sent during the Council Phase.",
        "efficient": "Jester's Court",
        "builds_into": ["Embassy"],
        "monument": False},
    "Embassy": {
        "group": "g_court",
        "unlock": "1 Established",
        "infrastructure_req": "Town Hall",
        "innate": "Diplomacy Envoys cannot Fail; Other non-vassal players gain Faith +1 per Signed Treaty with you besides Peace.",
        "efficient": "Bell Tower",
        "builds_into": ["Senate Hall"],
        "monument": False},
    "Granary": {
        "group": "g_works",
        "unlock": "Rising Industry",
        "innate": "Upkeep -500; Armies and Garrisons within controlled Settlements gain Immune Strained.",
        "efficient": "Masonry",
        "builds_into": ["Supply Depot", "Citadel"],
        "monument": False},
    "Academy": {
        "group": "g_court",
        "unlock": "1 Rising",
        "infrastructure_req": "Library",
        "innate": "Authority +1 to Council Envoys; gain Influence +1 each Empire Phase",
        "efficient": "Alchemy",
        "builds_into": ["University", "Forgery Workshop"],
        "monument": False},
    "Courtyard": {
        "group": "g_commerce",
        "root": True,
        "unlock": "-",
        "infrastructure_req": "Town Hall",
        "innate": "Craft +1; Faith +1",
        #"efficient": "Masonry",
        "builds_into": ["Market Square", "Jester's Court", "Episcopal Court", "Conditioning Field"],
        "monument": False},
    "Episcopal Court": {
        "group": "g_devotion",
        "unlock": "Rising Piety",
        "innate": "Faith +1; Reduce the first instance of Doubt each Empire Phase by 1, min 0.",
        "efficient": "Courtyard",
        "builds_into": ["Interrogation Chambers"],
        "monument": False},
    "Conditioning Field": {
        "group": "g_logistics",
        "unlock": "Rising Prowess",
        "infrastructure_req": "Muster Field",
        "innate": "Faith +1 while not at War; Armies gain Nimble",
        "efficient": ["Courtyard", "Common Land"],
        "builds_into": ["Coliseum"],
        "monument": False},
    "Grand Tournament": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        "innate": "Reach +1, 3x per Envoy Phase: exchange 500 gold for Influence +1; Armies gain Riposte & Improve Parry by +1.",
        "efficient": ["Coliseum","Tiltyard"],
        "builds_into": [],
        "monument": False},
    "Apothecary": {
        "group": "g_devotion",
        "unlock": "-",
        "innate": f'+300; Gain Recover {RECOVER_BASE}, or improve Recover by +1.',
        "efficient": "Alchemy",
        "builds_into": ["Infirmary"],
        "monument": False},
    "Infirmary": {
        "group": "g_devotion",
        "unlock": "Rising Piety",
        "innate": "+500; Improve Recover by +1",
        "efficient": "Apothecary",
        "builds_into": ["Hospitaller"],
        "monument": False},
    "Supply Depot": {
        "group": "g_works",
        "unlock": "Rising Industry",
        "innate": "Craft +2; May Muster an Army in a Settlement under Siege and its Muster Timers count down.",
        "efficient": "Granary",
        "builds_into": ["Citadel"],
        "monument": False},
    "Artisan Workshop": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "+1000; Faith +1",
        "efficient": "Weavery",
        "builds_into": ["Court Artists"],
        "monument": False},
    "University": {
        "group": "g_court",
        "unlock": "1 Established",
        "infrastructure_req": "Library",
        "innate": "May spend one additional Influence per Support or Oppose; Influence +1 per Domain you are Rising",
        "efficient": "Academy",
        "builds_into": ["Forgery Workshop","Studium Generale","Ministry of Military Strategy"],
        "monument": False},
    "Trade Guild": {
        "group": "g_works",
        "unlock": "Rising Industry",
        "innate": "No Upkeep on Developed Infrastructure; Build Timer -1",
        "efficient": "Masonry",
        "builds_into": ["College of Engineering"],
        "monument": False},
    "Court Artists": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "Extort 500 twice; Targets of Extort from Court Artist gain Faith +1",
        "efficient": "Artisan Workshop",
        "builds_into": ["Money Lending"],
        "monument": False},
    "Courier Network": {
        "group": "g_court",
        "unlock": "-",
        "innate": "Once per Envoy Phase before voting: Authority -1 on Target Envoy; Once per Envoy Phase: select a Personal Action you performed this turn. Next turn, you may perform that action in the Empire Phase, but you send 1 fewer Envoy next turn.",
        "efficient": "Inn",
        "builds_into": ["Smuggler's Nook"],
        "monument": False},
    "Toll House": {
        "group": "g_secrecy",
        "unlock": "Rising Cunning",
        "innate": "Natural, Extort 2000 when non-Allied Army ends a Move action within your Province; Once per turn: when an Army ends a Move action within your Province, Perform a Diplomacy action targeting that army's player",
        "efficient": ["Caravanery"],
        "builds_into": ["Beacon Towers"],
        "monument": False},
    "College of Engineering": {
        "group": "g_works",
        "unlock": "Established Industry",
        "innate": "No Upkeep on Sophisticated Infrastructure; Build Timer -1",
        "efficient": "Trade Guild",
        "builds_into": ["Masons' Guild"],
        "monument": False},
    "Masons' Guild": {
        "group": "g_works",
        "unlock": "Established Industry",
        "innate": "No Upkeep on Prodigious Infrastructure; Build Timer -2",
        "efficient": "College of Engineering",
        "builds_into": ["Office of Works"],
        "monument": False},
    "Secret Cellar": {
        "group": "g_secrecy",
        "unlock": "Rising Cunning",
        "innate": "Natural; Passed Cunning envoys Recoup 500 Gold; Endorsed Cunning envoys Recoup 1000 Gold",
        "efficient": ["Inn","Courier Network"],
        "builds_into": ["Courier Network","Forgotten Catacombs"],
        "monument": False},
    "Smuggler's Nook": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "gain Immune Uprising (Bandit Camp Spawn at -5PO); Bandit Camps in your Outlaw Country don't target you and instead target other players randomly.",
        "efficient": ["Courier Network"],
        "builds_into": ["Black Market", "Syndicate Hub"],
        "monument": False},
    "Syndicate Hub": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "Whenever a Bandit Camp within your Province Extorts, you Extort the Bandit Camp for half the amount.",
        "efficient": ["Smuggler's Nook"],
        "builds_into": ["Smuggler's Nook"],
        "monument": False},
    "Black Market": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "When another player Extorts gold from any source: Extort 200 per 1000 (minimum 100) from that player at the end of that resolution. When another player Recoups gold from any source: Extort 200 per 1000 (minimum 100) from that player at the end of that resolution.",
        "efficient": ["Smuggler's Nook"],
        "builds_into": ["Thieves' Guild"],
        "monument": False},
    "Forgery Workshop": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "Extort 300 anytime a player Opposes an Envoy of yours; Once per Envoy Phase: attempt another Cunning Envoy if your Cunning Envoy Failed. If it Passes or is Endorsed, it must target a different player.",
        "efficient": ["University", "Academy"],
        "builds_into": ["Cipher Chamber"],
        "monument": False},
    "Toxicarium": {
        "group": "g_secrecy",
        "unlock": "Rising Cunning",
        "innate": "Weapons gain Poison; Endorsed Cunning actions give an additional Doubt +1 to Target",
        "efficient": ["Alchemy", "Forgotten Catacombs"],
        "builds_into": ["Charnel House"],
        "monument": False},
    "Charnel House": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "Indecisive, Aimless, & Recession effects are doubled for all players",
        "efficient": ["Toxicarium"],
        "builds_into": ["Plague Pit"],
        "monument": False},
    "Plague Pit": {
        "group": "g_secrecy",
        "unlock": "Sovereign Cunning",
        "innate": "Cunning actions give an additional Doubt +1 to Target; No longer affected by all Public Order effects (positive or negative). This player cannot be the target of a Convert action.",
        "efficient": ["Charnel House"],
        "builds_into": [],
        "monument": True},
    "Pilgrimage Site": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "infrastructure_req": "Cathedral",
        "innate": "Natural; Extort 500 every player without a Pilgrimage Site; Doubt +1 to all other players without a Pilgrimage Site",
        "efficient": "Reliquary",
        "builds_into": ["Unforgotten Shrine"],
        "monument": False},
    "Unforgotten Shrine": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "infrastructure_req": "Cathedral",
        "innate": "When your Piety actions give their target Faith, it gains Faith +1 more; when they give Doubt, it gains Doubt +1 more.",
        "efficient": "Pilgrimage Site",
        "builds_into": ["Exalted Basilica"],
        "monument": False},
    "Beacon Towers": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "Natural; At the Start of the Empire Phase, you may select an Army within your Province and move it up to its modified Speed. Whenever a non-allied Army ends a Move action within your Province, you may immediately perform a Move action",
        "efficient": "Toll House",
        "builds_into": ["Outrider Intercept Post"],
        "monument": False},
    "Forgotten Catacombs": {
        "group": "g_secrecy",
        "unlock": "Rising Cunning",
        "innate": "Cunning actions targeting you can't be Endorsed",
        "efficient": "Secret Cellar",
        "builds_into": ["Toxicarium"],
        "monument": False},
    "Charcoal Burner": {
        "group": "g_logistics",
        "unlock": "Established Industry",
        "innate": "Natural; +500",
        "efficient": ["Forestry", "Kiln"],
        "builds_into": ["Smokehouse"],
        "monument": False},
    "Mill": {
        "group": "g_husbandry",
        "unlock": "Rising Industry",
        "innate": "Natural; +1000",
        "efficient": ["Bakery", "Weavery", "Forge", "Carpentry", "Masonry"],
        "builds_into": ["Bakery"],
        "monument": False},
    "Kiln": {
        "group": "g_logistics",
        "unlock": "Rising Industry",
        "innate": "Natural; +500",
        "efficient": "Forestry",
        "builds_into": ["Charcoal Burner"],
        "monument": False},
    "Burgages": {
        "group": "g_works",
        "unlock": "-",
        "innate": "Natural; Faith +1",
        "efficient": ["Workyard"],
        "builds_into": ["Census Hall"],
        "monument": False},
    "Levy Hall": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        "infrastructure_req": "Garrison",
        "innate": "Natural, Speed +1; Upkeep -2000 while an Army is within Range 0 of a Settlement you Control",
        "efficient": "Smokehouse",
        "builds_into": ["Baggage Train"],
        "monument": False},
    "Baggage Train": {
        "group": "g_logistics",
        "unlock": "Sovereign Prowess",
        "innate": "Natural; Armies do not pay Upkeep while in your Province. Upkeep -2000 while not in your Province. At the Start of the Empire Phase, you may perform a Move action.",
        "efficient": "Levy Hall",
        "builds_into": [],
        "monument": True},
    "Siege Camp": {
        "group": "g_logistics",
        "unlock": "Rising Prowess",
        "innate": "Siege Timer -1; Armies gain Immune Strained during Lay Siege",
        "efficient": ["Carpentry","Mine"],
        "builds_into": ["Battery Park"],
        "monument": False},
    "Siege Works": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        "innate": "Siege Timer -2; Siege Timers count down in Winter",
        "efficient": "Siege Camp",
        "builds_into": ["Battery Park"],
        "monument": False},
    "Battery Park": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        "innate": "Your Siege Timers increment twice each turn.",
        "efficient": ["Siege Works"],
        "builds_into": ["Artillery Park"],
        "monument": False},
    "Citadel": {
        "group": "g_works",
        "unlock": "Established Industry",
        "infrastructure_req": "Stone Walls",
        "innate": "Siege Timer +3, Controlled Settlements gain Reach +1",
        "efficient": ["Supply Depot"],
        "builds_into": ["Castle Hall"],
        "monument": False},
    "Castle Hall": {
        "group": "g_works",
        "unlock": "Established Industry",
        "innate": "Doubt +1; Tax Income is Doubled.",
        "efficient": ["Citadel"],
        "builds_into": ["Imperial Palace"],
        "monument": False},
    "War College": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        "infrastructure_req": "Library",
        "innate": "Gain Influence +2 while At War; Unlocks Sergeants for Muster",
        "efficient": "University",
        "builds_into": ["Ministry of Military Strategy"],
        "monument": False},
    "Forge": {
        "group": "g_arms",
        "unlock": "Established Industry",
        "innate": "Craft +2; Unlocks Forged Tier Weapons",
        "efficient": "Blacksmith",
        "builds_into": ["Master Workshop", "Mill"],
        "monument": False},
    "Tiltyard": {
        "group": "g_arms",
        "unlock": "Established Prowess",
        "innate": "Armies may be equipped with a Ranged and a Melee Weapon simultaneously; In addition, armies may equip two of the same 1H Melee Weapon to gain Dual Wield.",
        "efficient": "Fletchery",
        "builds_into": ["Grand Tournament"],
        "monument": False},
    "Court Armoury": {
        "group": "g_arms",
        "unlock": "Established Industry",
        "innate": f"{PLANISHING}: Your to-Save can't be reduced beyond {CAP_THR}+. Upkeep -500; Crafted Armor & Shield Unlocked",
        "efficient": "Gilded Foundry",
        "builds_into": [],
        "monument": False},
    "Office of Works": {
        "group": "g_works",
        "unlock": "Sovereign Industry",
        "innate": "Natural; Settlements & allied armies inside them are not affected by 'Settlements being Besieged' restrictions. Siege Timer +2; Build Timer -2",
        "efficient": ["Masons' Guild", "Storehouse"],
        "builds_into": [],
        "monument": True},
    "Royal Pavilion": {
        "group": "g_logistics",
        "unlock": "Sovereign Prowess",
        "innate": "Armies gain Immune Strained, Improve Parry by +1; Gain +1 to Strike. Deadly, & Cleave also trigger Focused Strikes on a natural 8+.",
        "efficient": "Grand Tournament",
        "builds_into": [],
        "monument": True},
    "Imperial Palace": {
        "group": "g_works",
        "unlock": "Sovereign Prowess",
        "innate": "Each Empire Phase, all non-allied players with a lower Prowess value gain Doubt +2. If your Envoy would fail, it passes instead.",
        "efficient": "Castle Hall",
        "builds_into": [],
        "monument": True},
    "Artillery Park": {
        "group": "g_logistics",
        "unlock": "Sovereign Prowess",
        "innate": "Siege Timers ignore Wooden & Stone Walls. Unlocks Arquebus; Settlements you Siege can't Sally Forth. Siege Timer -2.",
        "efficient": "Battery Park",
        "builds_into": [],
        "monument": True},
    "Ministry of Military Strategy": {
        "group": "g_logistics",
        "unlock": "Sovereign Prowess",
        "innate": "Always gains Seize the Initiative, and your opponent doesn't; max initiative is increased to 3; Gain Drilled.",
        "efficient": "War College",
        "builds_into": [],
        "monument": True},
    "Thieves' Guild": {
        "group": "g_secrecy",
        "unlock": "Sovereign Cunning",
        "innate": "Whenever another player performs a Cunning action, you may recoup 1000 gold; Extort half of Trade Income from players who don't trade with you",
        "efficient": ["Black Market"],
        "builds_into": [],
        "monument": True},
    "Senate Hall": {
        "group": "g_court",
        "unlock": "1 Sovereign",
        "infrastructure_req": "Library + Town Hall",
        "innate": "Faith +1, gain Influence +1 per other player each Empire Phase; Once per Envoy Phase: before players vote on an Envoy you choose, you may Condemn it if it's an At War player's Envoy, or Endorse it if it's an Ally's Envoy",
        "efficient": "Embassy",
        "builds_into": [],
        "monument": True},
    "Papal Palace": {
        "group": "g_devotion",
        "unlock": "Sovereign Piety",
        "innate": "You no longer pay cost for Piety Envoys. Each Empire Phase, Tithe every other player with lower Piety, resolved in the Extort step.",
        "efficient": ["Monastery"],
        "builds_into": [],
        "monument": True},
    "Inquisitorial Palace": {
        "group": "g_devotion",
        "unlock": "Sovereign Piety",
        "innate": "Doubt 1; Unlocks Grand Vizier which uses your Piety Value instead of Cunning.; All player actions that cause Doubt are increased by 1. ",
        "efficient": "Execution Dock",
        "builds_into": [],
        "monument": True},
    "Preceptory of the Knight's Templar": {
        "group": "g_devotion",
        "unlock": "Sovereign Piety + Established Prowess",
        "innate": f"Unlocks Knight's Templar for Muster", #Armies gain {CRUSADER}: Automatically pass the first Panic Check of every Battle. 
        "efficient": "Hospitaller",
        "builds_into": [],
        "monument": True},
    "Exalted Basilica": {
        "group": "g_devotion",
        "unlock": "Sovereign Piety",
        "innate": "At the Start of the Empire Phase, you may perform an Endorsed Spread Truth.",
        "efficient": "Unforgotten Shrine",
        "builds_into": [],
        "monument": True},
    "Manor House": {
        "group": "g_husbandry",
        "unlock": "Sovereign Industry",
        "infrastructure_req": "Hamlet",
        "innate": "Natural; Gain +200 gold for each active natural Holding.",
        "efficient": "Natural",
        "builds_into": [],
        "monument": True},
    "Aristocratic Court": {
        "group": "g_commerce",
        "unlock": "Sovereign Industry",
        "innate": "Each Empire Phase, Extort 1000 from each non-allied player with a lower Treasury. Your Vote counts as 2 votes toward Domain selection during the Council Phase.",
        "efficient": ["Court Artists","Money Lending"],
        "builds_into": [],
        "monument": True},
    "Studium Generale": {
        "group": "g_court",
        "unlock": "4 Established",
        "innate": "Influence +1 per Established Standing; May gain one Sovereign Domain effect without spending the Domain Points",
        "efficient": "University",
        "builds_into": [],
        "monument": True},
    "Outlaw Rookery": {
        "group": "g_secrecy",
        "unlock": "Sovereign Cunning",
        "innate": "Both Bandit Camps & you have Authority +1 on Personal Cunning Envoys. Endorsed Foster Rebellion instead places Bandit Armies with 25 retinues.",
        "efficient": "Syndicate Hub",
        "builds_into": [],
        "monument": True},
    "Advanced Blast Furnace": {
        "group": "g_arms",
        "unlock": "Sovereign Industry",
        "innate": "Upkeep -1000; Crafted Weapons Unlocked; Craft +3",
        "efficient": "Master Workshop",
        "builds_into": [],
        "monument": True},
    "Cipher Chamber": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "At the Start of the Empire Phase: select an army you did not select last turn; that army gains Blocked. At the Start of the Empire Phase: select any active Timer you did not select last turn; increase it by 2.",
        "efficient": "Forgery Workshop",
        "builds_into": ["Whispering Undercroft"],
        "monument": False},
    "Whispering Undercroft": {
        "group": "g_secrecy",
        "unlock": "Sovereign Cunning",
        "innate": "You always vote last, after the Host. Once per Envoy Phase when a player sends an Envoy: that player must declare the specific action & target they would Perform if the Envoy passes (including sub-Actions). If it passes, they must Perform that declared action at the declared target.",
        "efficient": "Cipher Chamber",
        "builds_into": [],
        "monument": True},
    "Outrider Intercept Post": {
        "group": "g_secrecy",
        "unlock": "Sovereign Cunning",
        "innate": "Natural; Every Skirmish, you may force your opponent to reveal their Tactic Card they selected before you select your own.",
        "efficient": ["Beacon Towers"],
        "builds_into": [],
        "monument": True},
    "Emporium": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "+1000; Players who trade with you gain Craft +3",
        "efficient": ["Shipyard"],
        "builds_into": [],
        "monument": False},
    "Port Authority": {
        "group": "g_commerce",
        "unlock": "Sovereign Industry",
        "innate": "Gain +100 per Craft",
        "efficient": ["Emporium"],
        "builds_into": [],
        "monument": True}
}
# builds_into is derived: exactly the Holdings that name this one in their `efficient` (Mastery Chain).
for _bn, _bv in SIMPLE_NODES.items():
    _bv["builds_into"] = [_c for _c, _cv in SIMPLE_NODES.items()
                          if _bn in ([_cv["efficient"]] if isinstance(_cv.get("efficient"), str) else (_cv.get("efficient") or []))]

# ── HOLDING GROUPS (SIMPLE) — engine ids neutral; rename a group's label here only. ──
# Each SIMPLE node carries "group" (id); "type" is derived from the label below, so every
# reader of `type` (tiles, wiki, compendium, board) follows a rename. Monuments keep their
# group (shown under the Monument category: type "Monument"); `monument: True` marks them. "root": may take its own Ward / start without a parent.
HOLDING_GROUPS = {
    "g_arms": "Arms",
    "g_logistics": "Logistics",
    "g_works": "Works",
    "g_commerce": "Commerce",
    "g_devotion": "Devotion",
    "g_court": "Court",
    "g_secrecy": "Secrecy",
    "g_husbandry": "Husbandry",
    "g_raw": "Raw Materials",
}
for _hn, _hv in SIMPLE_NODES.items():
    _hv["type"] = "Monument" if _hv.get("monument") else HOLDING_GROUPS[_hv["group"]]
# ── RARITY SCOPE — how many of one Holding / Infrastructure may exist ─────────
#   Settlement = one per Settlement · Empire = one per player · Realm = one per game
# Raw Materials are Settlement, Monuments and Wonders are Realm, everything else is Empire.
# A Realm piece is taken once any player has placed it (under construction included).
SCOPES = ("Settlement", "Empire", "Realm")
SCOPE_BY_TYPE = {"Raw Materials": "Settlement", "Monument": "Realm"}
for _hn, _hv in SIMPLE_NODES.items():
    _hv.setdefault("scope", SCOPE_BY_TYPE.get(_hv["type"], "Empire"))
# Lines: flavour labels for paths through the graph; a Holding may sit in several.
LINE_LABELS = {
    "l_engineering": {"label": "Engineering", "members": ["Quarry", "Masonry", "Trade Guild", "College of Engineering", "Office of Works"]},
    "l_labor": {"label": "Labor", "members": ["Common Land", "Salt Works", "Workyard", "Burgages", "Census Hall", "Storehouse", "Office of Works"]},
    "l_fortification": {"label": "Fortification", "members": ["Masonry", "Granary", "Supply Depot", "Citadel", "Castle Hall", "Imperial Palace"]},
    "l_maritime": {"label": "Maritime", "members": ["Fishmongery", "Harbor", "Shipyard", "Emporium", "Port Authority"]},
    "l_training": {"label": "Training", "members": ["Courtyard", "Common Land", "Conditioning Field", "Coliseum", "Grand Tournament", "Royal Pavilion"]},
    "l_siege": {"label": "Siege", "members": ["Carpentry", "Mine", "Siege Works", "Siege Camp", "Artillery Park"]},
    "l_command": {"label": "Command", "members": ["University", "War College", "Ministry of Military Strategy"]},
    "l_supply": {"label": "Supply", "members": ["Forestry", "Kiln", "Charcoal Burner", "Salt Works", "Butchery", "Smokehouse", "Levy Hall", "Baggage Train"]},
    "l_medical": {"label": "Medical", "members": ["Alchemy", "Apothecary", "Infirmary", "Hospitaller", "Preceptory of the Knight's Templar"]},
    "l_smithing": {"label": "Smithing", "members": ["Mine", "Furnace", "Blacksmith", "Forge", "Master Workshop", "Advanced Blast Furnace"]},
    "l_bulwark": {"label": "Bulwark", "members": ["Animal Husbandry", "Carpentry", "Joinery", "Tannery", "Armory", "Gilded Foundry", "Court Armoury"]},
    "l_archery": {"label": "Archery", "members": ["Forestry", "Carpentry", "Fletchery", "Tiltyard"]},
    "l_cavalry": {"label": "Cavalry", "members": ["Animal Husbandry", "Stable", "Saddlery", "Caravanery"]},
    "l_statecraft": {"label": "Statecraft", "members": ["Courtyard", "Jester's Court", "Bell Tower", "Embassy", "Senate Hall"]},
    "l_trivium": {"label": "Trivium", "members": ["Alchemy", "Academy", "University", "Studium Generale"]},
    "l_smuggling": {"label": "Smuggling", "members": ["Inn", "Courier Network", "Smuggler's Nook", "Syndicate Hub", "Outlaw Rookery"]},
    "l_thievery": {"label": "Thievery", "members": ["Smuggler's Nook", "Black Market", "Thieves' Guild"]},
    "l_whispers": {"label": "Whispers", "members": ["Academy", "University", "Forgery Workshop", "Cipher Chamber", "Whispering Undercroft"]},
    "l_pestilence": {"label": "Pestilence", "members": ["Secret Cellar", "Forgotten Catacombs", "Alchemy", "Toxicarium", "Charnel House", "Plague Pit"]},
    "l_watch": {"label": "Watch", "members": ["Caravanery", "Toll House", "Beacon Towers", "Outrider Intercept Post"]},
    "l_vintage": {"label": "Vintage", "members": ["Arable Land", "Vineyard", "Winery", "Orchard", "Cidery"]},
    "l_hearth": {"label": "Hearth", "members": ["Apiary", "Meadery", "Bakery", "Mill"]},
    "l_spice": {"label": "Spice", "members": ["Arable Land", "Herb Garden", "Spice Merchant"]},
    "l_patronage": {"label": "Patronage", "members": ["Courtyard", "Market Square", "Weavery", "Artisan Workshop", "Court Artists", "Aristocratic Court"]},
    "l_banking": {"label": "Banking", "members": ["Market Square", "Merchant Quarter", "Money Lending", "Aristocratic Court"]},
    "l_pilgrimage": {"label": "Pilgrimage", "members": ["Apiary", "Chandlery", "Reliquary", "Pilgrimage Site", "Exalted Basilica"]},
    "l_cloister": {"label": "Cloister", "members": ["Masonry", "Abbey", "Monastery", "Papal Palace"]},
    "l_inquisition": {"label": "Inquisition", "members": ["Courtyard", "Episcopal Court", "Interrogation Chambers", "Execution Dock", "Inquisitorial Palace"]},
}

def lines_of(name):
    """Line labels containing this Holding."""
    return [d["label"] for d in LINE_LABELS.values() if name in d["members"]]

LEGACY_NODES = NODES
NODES = SIMPLE_NODES if SIMPLE else NODES
# What a pursuit needs besides Standing. SIMPLE: infrastructure_req (settlement
# infrastructure / tags) and placement next to an `efficient` parent.
# Legacy: mastery_req. Outputs read these instead of hard-coding the field.
REQ_KEY   = "infrastructure_req" if SIMPLE else "mastery_req"
REQ_LABEL = "Infrastructure Req" if SIMPLE else "Mastery Req"
# Section/sort order for node `type` (tiles, wiki, compendium).
TYPE_ORDER = (list(HOLDING_GROUPS.values()) + ["Monument"] if SIMPLE else
              ["Raw Materials", "Husbandry", "Energy", "Craft", "Power", "Civic", "Secrecy", "Monument"])
# Display name for the `efficient` field (the data key stays `efficient`).
CHAIN_TERM = "Mastery Chain" if SIMPLE else "Efficient"
# Display name for Pursuits (singular, plural). Data keys, file names and wiki URLs keep "pursuit".
PURSUIT_TERM = ("Holding", "Holdings") if SIMPLE else ("Pursuit", "Pursuits")

def node_parents(name, nodes=None):
    """Prerequisite pursuits of `name` (names present in `nodes`).
    SIMPLE: its efficient parent(s), any one of which allows placement.
    Legacy: the pursuit names in its mastery_req."""
    import re
    nodes = NODES if nodes is None else nodes
    d = nodes.get(name, {}) or {}
    if SIMPLE:
        e = d.get("efficient")
        e = [e] if isinstance(e, str) else list(e or [])
        return [p for p in e if p in nodes]
    req = str(d.get("mastery_req") or "").strip()
    out = []
    if req and req not in ("-", "\u2014"):
        for part in req.split("+"):
            for q in re.split(r"\bor\b|/", part):
                nm = re.sub(r"^\d+\s+", "", q.strip().rstrip(",").strip())
                if nm in nodes and nm not in out:
                    out.append(nm)
    return out
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
        'mechanic_name': 'Siege Specialists',
        'summary': 'Starts with Siege Works',
        'mechanic': 'You begin the game with a Siege Works (no Ward, no upkeep).',
        'pair': 'Siege Camp, Royal Pavilion',
        'complement': 'Senate Hall',
    },
    'The Boundless Steppe': {
        'final_cut': True,
        'inspiration': 'Mongol Horde',
        'feel': 'Fast',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Horsemasters',
        'summary': 'Starts with a Stable',
        'mechanic': "You begin the game with a Stable (no Ward, no upkeep).",
        'pair': 'Saddlery, Royal Pavilion',
        'complement': 'Forge',
    },
    'The Bandit King': {
        'final_cut': True,
        'inspiration': 'Brigands',
        'feel': 'Scrappy',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic_name': 'Friends in Low Places',
        'summary': "Starts with Smuggler's Nook; controls a Bandit Camp; no Piety or Prowess Holdings",
        'mechanic': "You begin the game with a Smuggler's Nook (no Ward, no upkeep, always-active Mastery that can't be deactivated). At the Start of the Empire Phase, you may control one Bandit Camp outside your Territory. When a Bandit Camp is spawned, you may place it in your Outlaw Country instead. You cannot Build Holdings which require Piety or Prowess Standing.",
        'pair': "Thieves' Guild, Saddlery",
        'complement': 'Royal Pavilion',
    },
    'The Crowned Star': {
        'final_cut': True,
        'inspiration': 'Reigning Sovereign',
        'feel': 'Sovereign Voice',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'The Monarch',
        'summary': "Chooses every Council Envoy's Domain; abstains every Personal Envoy",
        'mechanic': "Each Council Phase, you choose every Council Envoy's Domain. You abstain every Personal Envoy.",
        'pair': 'Senate Hall, Aristocratic Court',
        'complement': 'Royal Pavilion',
    },
    'The Crimson Tide': {
        'final_cut': True,
        'inspiration': 'Pirate',
        'feel': 'Pirate Life',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Uncharted Sea Lanes',
        'summary': 'Immune to Intercept Caravan; starts with a Shipyard',
        'mechanic': "Other players can't perform Intercept Caravan on you. You begin the game with a Shipyard (no Ward, no upkeep).",
        'pair': "Shipyard, Thieves' Guild",
        'complement': 'Royal Pavilion',
    },
    'The Entwined Crown': {
        'final_cut': True,
        'inspiration': 'Habsburg Dynasty',
        'feel': 'Diplomatic, Inescapable',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Royal Marriage',
        'summary': 'Once, force an Alliance; members gain Faith and Influence',
        'mechanic': "Once per game, you may join an Alliance without unanimous consent, or form one with a player who isn't in an Alliance. While in that Alliance, each member gains Faith +1 and Influence +1 each Empire Phase.",
        'pair': 'Aristocratic Court, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Eternal Court': {
        'final_cut': True,
        'inspiration': 'Byzantine Empire',
        'feel': 'Patient & Reserved',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Patient Court',
        'summary': 'Banks Influence; up to 5 per Envoy in Zenith',
        'mechanic': "Your unspent Influence isn't discarded in the Rest Phase. While the Era is Zenith, you may spend up to 5 Influence per Envoy while voting, regardless of your Domain Standing.",
        'pair': 'Senate Hall, Aristocratic Court',
        'complement': 'Royal Pavilion',
    },
    'The Final Word': {
        'final_cut': True,
        'inspiration': 'Warlord Council',
        'feel': 'Cold Steel',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'The Decider',
        'summary': 'Ignores At War Doubt and Influence modifiers',
        'mechanic': 'Ignore the innate Doubt and Influence modifiers for being At War.',
        'pair': 'Royal Pavilion, Imperial Palace',
        'complement': 'Senate Hall',
    },
    'The Gilded Crescent': {
        'final_cut': True,
        'inspiration': 'Moorish Caliphate',
        'feel': 'Egalitarian',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Prosperity For All',
        'summary': 'Starts with an Inn',
        'mechanic': "You begin the game with an Inn (no Ward, no upkeep).",
        'pair': 'Meadery & Winery, Studium Generale, Manor House',
        'complement': 'Royal Pavilion',
    },
    'The Gilded Path': {
        'final_cut': False,
        'inspiration': 'Great Income',
        'feel': 'Rich Trader',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic_name': 'Luxury Trades',
        'summary': "Starts with Artisan Workshop; can't refuse trade",
        'mechanic': "You begin the game with an Artisan Workshop (no Ward, no upkeep). You can't refuse a Trade Agreement.",
        'pair': 'Meadery & Winery, Forge',
        'complement': 'Royal Pavilion',
    },
    'The Hermit Crown': {
        'final_cut': True,
        'inspiration': 'Independent',
        'feel': 'Independent',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic_name': 'Independent, but Ambitious',
        'summary': 'Always Abstains; 2 Influence to sway your Envoys by 1; Personal Envoys +1; no votes or Council Envoys',
        'mechanic': "You Abstain on every vote on other players' Envoys, and other players must spend 2 Influence to affect your Envoys by 1. Your Personal Envoys have Authority +1. You can't vote nor send Council Envoys.",
        'pair': 'Aristocratic Court, Inquisitorial Palace',
        'complement': 'Royal Pavilion',
    },
    'The Illuminated Order': {
        'final_cut': True,
        'inspiration': 'Scholarly',
        'feel': 'Knowledge is Power',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Knowledge is Power',
        'summary': 'Influence +1 per 3 Pursuits',
        'mechanic': 'Each Empire Phase, gain Influence +1 for every 3 Pursuits you have.',
        'pair': 'Studium Generale, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Iron Faith': {
        'final_cut': True,
        'inspiration': 'Crusader States',
        'feel': 'Piously Resolute',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Fortress of Faith',
        'summary': 'Sieges against you +2 while Public Order 3+',
        'mechanic': 'While your Public Order is 3 or higher, Lay Siege actions targeting Settlements you Control have Siege Timer +3.',
        'pair': "Siege Camp, Preceptory of the Knight's Templar",
        'complement': 'Senate Hall',
    },
    'The Iron Shore': {
        'final_cut': True,
        'inspiration': 'Norse',
        'feel': 'Scavenger',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Scavengers',
        'summary': 'Spoils win or lose; extorts 2000 from whoever Razes you',
        'mechanic': 'You collect the Spoils of War whether you win or lose a Battle. When you are the target of a Raze action, Extort 2000 from the target that performed the Raze action.',
        'pair': 'Royal Pavilion, Shipyard',
        'complement': 'Forge',
    },
    'The Iron Throne': {
        'final_cut': True,
        'inspiration': 'Defensive',
        'feel': 'Defensive, Impenetrable',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Unimpeachable',
        'summary': "Starts with a Citadel; your Alliance can't Declare War",
        'mechanic': "You begin the game with a Citadel (no Ward, no upkeep). You (and your Alliance) can't perform Declare War or Sacred War actions.",
        'pair': 'Inquisitorial Palace, Senate Hall, Imperial Palace',
        'complement': 'Royal Pavilion',
    },
    'The Merchant Republics': {
        'final_cut': True,
        'inspiration': 'Italian City States',
        'feel': 'Trade Dependent',
        'difficulty': 'Low',
        'strength': 'High',
        'mechanic_name': 'Heart of Trade',
        'summary': 'All trade needs a Trade Agreement with you',
        'mechanic': "You begin the game with Stone Roads (no upkeep, can't be Razed). No player may trade unless they first hold a Trade Agreement with you, or are At War with you. When another player becomes eligible, you must attempt once to Sign a Trade Agreement with them. You can't perform the End Treaty action.",
        'pair': 'Shipyard, Meadery & Winery',
        'complement': 'Royal Pavilion',
    },
    'The Sacred Throne': {
        'final_cut': True,
        'inspiration': 'Papal State',
        'feel': 'Pure and Defensive',
        'difficulty': 'Low',
        'strength': 'High',
        'mechanic_name': 'Sacrosanct',
        'summary': 'Declaring War on you costs Doubt',
        'mechanic': 'When a player Declares War on you, that player and their allies gain Doubt +5.',
        'pair': "Inquisitorial Palace, Preceptory of the Knight's Templar",
        'complement': 'Royal Pavilion',
    },
    'The Tunnellers': {
        'final_cut': True,
        'inspiration': 'Dwarves',
        'feel': 'Mountain Passers',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic_name': 'Tunnellers',
        'summary': 'Move through Mountains; starts with a Mine',
        'mechanic': 'You treat mountain Territory as grassland for movement, and begin the game with a Mine Raw-Material Pursuit (no Ward, no upkeep).',
        'pair': 'Forge, Advanced Blast Furnace',
        'complement': 'Royal Pavilion',
    },
    'The Undying Flame': {
        'final_cut': True,
        'inspiration': 'Martyrs',
        'feel': 'Unconvinced',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic_name': 'Martyrdom',
        'summary': 'Faith from wars and heavy losses; Immune War Weariness',
        'mechanic': f"Your Armies' Morale can't be modified beyond {CAP_THR}+, but still suffer −{FATIGUE_MORALE} per Fatigue Token. Gain Faith +1 for every player you're At War with each Empire Phase, and Faith +1 in every Battle where you lose 20 or more Retinues (win or lose). You gain Immune War Weariness.",
        'pair': "Preceptory of the Knight's Templar, Inquisitorial Palace",
        'complement': 'Royal Pavilion',
    },
    'The Verdant Kingdom': {
        'final_cut': True,
        'inspiration': 'Industry',
        'feel': 'Pure Economy',
        'difficulty': 'Low',
        'strength': 'High',
        'mechanic_name': 'Peaceful & Inventive',
        'summary': 'Gold per Craft level; no war or Cunning actions',
        'mechanic': "You can't Declare War, enter Military Alliances, perform Cunning actions, or build Pursuits that require Prowess or Cunning Standing. Gain 100 gold per total Craft level across all active sources.",
        'pair': 'Forge, Advanced Blast Furnace, Meadery & Winery',
        'complement': 'Senate Hall',
    },
    'The Winter Wolves': {
        'final_cut': True,
        'inspiration': 'Vikings',
        'feel': 'Aggressive, Parasitic',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Pillagers',
        'summary': 'At war, Armies extort their upkeep from at-war Settlements; no Alliances',
        'mechanic': "While At War, your Armies within reach of at-war Settlements Extort their upkeep from that settlement's controller. You cannot join an alliance.",
        'pair': 'Royal Pavilion, Shipyard',
        'complement': 'Forge',
    },
    'The Ancient Wilds': {
        'final_cut': True,
        'inspiration': 'Celtic Kingdoms',
        'feel': 'Oathkeepers',
        'difficulty': 'Medium',
        'strength': 'High',
        'mechanic_name': 'Terrain Negotiators',
        'summary': 'Slows invaders, ignores terrain; must accept first NAPs',
        'mechanic': 'Enemy Armies have Speed -2 in your Province. You ignore all negative terrain Speed modifiers and may trade without Dirt Roads. You must accept the first Non-Aggression Pact each player or Alliance offers you. If that player later joins an Alliance, this is considered satisfied for that Alliance.',
        'pair': 'Royal Pavilion, Saddlery',
        'complement': 'Senate Hall',
    },
    'The Bloodied Cross': {
        'final_cut': True,
        'inspiration': 'Crusading Sect',
        'feel': 'Sacred War Without End',
        'difficulty': 'Medium',
        'strength': 'High',
        'mechanic_name': 'Prophets of War',
        'summary': 'Sacred War at Rising Piety, uncapped; no Convert',
        'mechanic': "You may Sacred War at Rising Piety instead of Sovereign Piety, with no cap on active Sacred Wars. Each player gains Doubt +1 each Empire Phase per Sacred War you're on. You can't perform Convert or Cunning actions.",
        'pair': "Preceptory of the Knight's Templar, Inquisitorial Palace",
        'complement': 'Senate Hall',
    },
    'The Blazing Standard': {
        'final_cut': False,
        'inspiration': 'Teutonic Knight',
        'feel': 'Crusader Feel',
        'difficulty': 'Medium',
        'strength': 'High',
        'mechanic_name': 'Burning Cross',
        'summary': "Starts with a Preceptory; must field 25 Knight's Templar",
        'mechanic': "You begin the game with a Preceptory of the Knight's Templar (no Ward, no upkeep, always-active Mastery). When you Declared War via Sacred War, that player takes a Panic Check at the start of every Battle, after lines are formed. During Envoy Declaration, if you don't have an Army of 25 Knight's Templar, you must send a Prowess Envoy; if it passes, you must muster an Army until it holds 25 Knight's Templar Retinues.",
        'pair': "Preceptory of the Knight's Templar, Royal Pavilion",
        'complement': 'Senate Hall',
    },
    'The Inner Circle': {
        'final_cut': False,
        'inspiration': 'Natural Leader',
        'feel': 'Strength Through Diplomacy',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic_name': 'Palatine',
        'summary': "Allies' Envoys +1; may spend allies' Influence",
        'mechanic': "Each player allied with you has Authority +1 on their Personal Envoys. Once per Envoy Phase, you may spend 1 of an ally's Influence, targeting your own Envoys if you wish.",
        'pair': 'Senate Hall, Aristocratic Court',
        'complement': 'Royal Pavilion',
    },
    'The Luminous Court': {
        'final_cut': False,
        'inspiration': 'Renaissance',
        'feel': 'Civic Soft Power',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic_name': 'Arts & Humanities / Hearts & Minds',
        'summary': 'Civic Pursuits upgraded; no Craft Pursuits',
        'mechanic': "You can't build Industry Pursuits. Your Holdings which require Piety have Craft +2 and cost no Upkeep. You must accept a Peace Treaty if one is offered.",
        'pair': 'Studium Generale, Aristocratic Court, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Grand Compact': {
        'final_cut': False,
        'inspiration': 'Hanseatic League',
        'feel': 'Peace Through Trade',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic_name': 'Mercantile Pact',
        'summary': 'Trade partners must join your war or cut trade',
        'mechanic': 'Players who sign a Trade Agreement with you are considered to be in a Defensive Alliance with you. You cannot perform the Declare War action.',
        'pair': 'Shipyard, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Pale Throne': {
        'final_cut': True,
        'inspiration': 'Undead',
        'feel': 'Undead',
        'difficulty': 'Medium',
        'strength': 'Low',
        'mechanic_name': 'Inexorable',
        'summary': 'Unwieldy, Panic-immune Armies; Public Order capped at 1',
        'mechanic': "Your Armies always have Unwieldy; they also gain Recover 8, Speed -1, and Immune Panic. Your Public Order can't exceed 1.",
        'pair': "Preceptory of the Knight's Templar, Forge",
        'complement': 'Advanced Blast Furnace',
    },
    'The Sublime Gate': {
        'final_cut': False,
        'inspiration': 'Ottoman Empire',
        'feel': 'Mercantile Military',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic_name': 'Integrated Arms',
        'summary': "Musters from Trade Partners' Pursuits",
        'mechanic': "When you perform a Muster action, you may muster Retinues and equipment from your Trade Partners' Pursuits.",
        'pair': 'Forge, Advanced Blast Furnace',
        'complement': 'Royal Pavilion',
    },
    'The Velvet Hand': {
        'final_cut': False,
        'inspiration': 'Patrons',
        'feel': 'Generous Sponsor',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic_name': 'Friends in High Places',
        'summary': 'Rewards players who support your Envoys',
        'mechanic': 'Each Empire Phase, a player who supported a Personal Envoy you sent that passed gains Faith +1; if that Personal Envoy was endorsed, they Extort 500 gold from you.',
        'pair': 'Aristocratic Court, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    'The Ashen Vale': {
        'final_cut': True,
        'inspiration': 'Plague',
        'feel': 'Sickly',
        'difficulty': 'High',
        'strength': 'Low',
        'mechanic_name': 'Pestilence',
        'summary': 'Neighbours gain Doubt; Retinues have Poison',
        'mechanic': "Each bordering player gains Doubt +1 each Empire Phase. Your Settlements have Reach +2, and all your Retinues have Poison. You can't build an Apothecary, Infirmary, or Hospitaller.",
        'pair': "Thieves' Guild, Inquisitorial Palace",
        'complement': 'Royal Pavilion',
    },
    'The Broken Banner': {
        'final_cut': False,
        'inspiration': 'Mercenary',
        'feel': 'Always for Sale',
        'difficulty': 'High',
        'strength': 'Low',
        'mechanic_name': 'The Highest Bidder',
        'summary': "Can't war or be warred on; allied to the highest bidder",
        'mechanic': "You can't Declare War and can't be the target of a Declare War action. Each Empire Phase, you must sign the Military or Defensive Alliance offered by the highest-bidding player, and must be paid each Empire Phase. To overturn your current Alliance, a player must pay more than the prior agreement. You can't sign or end Alliances via a Diplomacy action.",
        'pair': 'Royal Pavilion, Forge',
        'complement': 'Senate Hall',
    },
    'The Forked Tongue': {
        'final_cut': False,
        'inspiration': 'Deceptive',
        'feel': 'Two-Faced',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic_name': 'Masters of Duplicity',
        'summary': 'Unlimited, contradictory Treaties',
        'mechanic': 'You may hold any number of Treaties at once with any number of players, even contradictory ones. Your Treaties are never automatically canceled or voided by game events. When something would normally force a Treaty to cancel, you choose which obligation to honor and keep all your Treaties intact. Other players may still End Treaty with you.',
        'pair': "Thieves' Guild, Senate Hall",
        'complement': 'Royal Pavilion',
    },
    'The Hall of Masks': {
        'final_cut': False,
        'inspiration': 'Doppelganger',
        'feel': 'Shifting Identity',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic_name': 'Mimic',
        'summary': "Takes another player's Faction each turn",
        'mechanic': "At the Start of the Empire Phase, choose another player's Faction; you have that Faction's mechanic this turn. You can't choose that same Faction next turn.",
        'pair': 'Studium Generale, Senate Hall',
        'complement': 'Royal Pavilion',
    },
    
    'The Illusionists': {
        'final_cut': False,
        'inspiration': 'Political Masterminds',
        'feel': 'Subterfuge, Deception',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic_name': 'Double Speak',
        'summary': 'Diplomacy Envoys run on Cunning Standing and may become Cunning actions; no wars or Alliances',
        'mechanic': "Your Diplomacy Envoys use your Cunning Standing for their innate Authority. Whenever your Personal Diplomacy Envoy passes or is endorsed, you may instead perform a Cunning action. You can't perform Declare War or Sacred War actions, and you can't be a member of an Alliance.",
        'pair': "Aristocratic Court, Whispering Undercroft",
        'complement': 'Artillery Park',
    },
    'The Smoldering Crown': {
        'final_cut': True,
        'inspiration': 'Terrorists',
        'feel': 'Aggressive, Destructive',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic_name': 'Reckless',
        'summary': 'Strong Cunning Envoys; Secret Cellar; Prowess Envoys always pass; no Alliances, Diplomacy or Renown into Piety; Industry 3 max',
        'mechanic': "Your Cunning Envoys have Authority +2 when targeting a player with Public Order greater than 1. You begin the game with a Secret Cellar (no Ward, no upkeep). You can't be in an Alliance or perform Diplomacy actions. A Prowess Envoy you send can't fail or be condemned & will instead pass. You cannot put Domain Points into Piety, nor have more than 3 in Industry.",
        'pair': "Thieves' Guild, Inquisitorial Palace",
        'complement': 'Royal Pavilion',
    },
    "The Squatters' Crown": {
        'final_cut': False,
        'inspiration': 'Insurgents',
        'feel': 'Mobile Occupier',
        'difficulty': 'High',
        'strength': 'Medium',
        'mechanic_name': 'Occupy',
        'summary': 'Armies Occupy Settlements instead of holding them',
        'mechanic': "You start with an additional Army; all your Armies begin inside your Settlements. While you're outside a Settlement, you don't control it — to collect taxes or use its Pursuits, end your turn inside it. To Occupy a Settlement, begin a Battle adjacent to it as if Sieging, but instead Battle the Garrison and any Armies at War with you or sharing its owner; if you win (or there's no force to fight), move inside. In the Upkeep Phase, you only pay upkeep on your armies. You count as having all Infrastructure of your Occupied Settlements, and always count as having Craft 5.",
        'pair': 'Royal Pavilion, Saddlery',
        'complement': 'Forge',
    },
    'The Wandering Crown': {
        'final_cut': False,
        'inspiration': 'Nomadic',
        'feel': 'Nomads',
        'difficulty': 'High',
        'strength': 'Medium',
        'mechanic_name': 'Wandering Nomads',
        'summary': 'Armies are Settlements; no Infrastructure, no upkeep',
        'mechanic': "Your Armies function as Settlements — a Band, Tribe, or Horde, upgraded accordingly — count as Settlements with Reach 3, and each has a Muster Field. You may have one additional Army per Era, starting with two. Your Armies don't require troops to exist and can't be besieged. You can't build Infrastructure, but may build Pursuits; Raw Material Pursuits within your Reach are always active and take no Settlement Ward. You may trade so long as your border touches another player's. You may begin a new Army adjacent to any existing Army with a Charter or Muster action. When an Army is destroyed, so is its Settlement. Nomads pay no upkeep.",
        'pair': 'Saddlery, Royal Pavilion',
        'complement': 'Forge',
    },
    'The Dukedom': {
        'final_cut': True,
        'inspiration': 'The Game',
        'feel': 'King of the Castle',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic_name': 'The Duke',
        'summary': 'Hosts the game; attacking the Duke unites the table',
        'mechanic': "The Duke begins the game trading with every player under a Non-Aggression Pact. The Duke can't join Alliances, perform Cunning actions, or Declare War. When a player Declares War on the Duke, that player's Trade Agreements, Non-Aggression Pacts, and Defensive Alliances are immediately and permanently voided (their Military Alliance stays intact), and every other player simultaneously Declares War on that player and their Military Alliance; none of these can be reinstated while At War with the Duke. The Duke sees all private actions, resolves player actions, and manages Bandit Mechanics. If the Duke is eliminated, the game ends. The Duke may optionally choose a Faction.",
        'pair': 'Senate Hall, Aristocratic Court',
        'complement': 'Royal Pavilion, Imperial Palace',
    },
    'The Elder Grove': {
        'final_cut': True,
        'inspiration': 'Elves',
        'feel': 'Cautious Quickfighters',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Wise & Suspicious',
        'summary': 'Doubt +1; faster, Steady Armies; no Alliances',
        'mechanic': "Gain Doubt +1 each Empire Phase. While your Public Order is 1 or higher, your Armies gain Initiative +1, Steady, and Speed +1. You can't be in an Alliance.",
        'pair': 'Forge',
        'complement': 'Inquisitorial Palace',
    },
    'The Yew Heart': {
        'final_cut': True,
        'inspiration': 'English Longbows',
        'feel': 'Skilled Volleys',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Archery is a Way of Life',
        'summary': 'Ranged +1 to Strike; no heavy plate or shields',
        'mechanic': "You begin the game with a Fletchery (no Ward, no upkeep). Your Armies must always have a ranged weapon, and Ranged Weapons gain +1 to Strike. Your Armies can't equip full plate, gothic plate, or shields.",
        'pair': 'Royal Pavilion',
        'complement': 'Senate Hall',
    },
}


# ── INFRASTRUCTURE (Wonders = the Wondrous tier) ───────────────────────────
# Empire-level builds; Wonders are unique (Realm Scope).
# Master source — edit HERE; reference sheets are generated from these dicts.
# Tiered upkeep/build values (e.g. '50/100/200') are strings.
INFRASTRUCTURE = {'Dirt Roads': {'upkeep': 0,
                'upkeep_frequency': '—',
                'empire_bonus': 'Can Trade; If you start a Move action within your Province, gain Speed +1',
                'tier': 'Primitive',
                'build_time': 1,
                'requirement': 'None'},
 'Hitching Post': {'upkeep': 0,
                   'upkeep_frequency': '—',
                   'empire_bonus': 'Craft +1',
                   'tier': 'Primitive',
                   'build_time': 1,
                   'requirement': 'None'},
 'Muster Field': {'upkeep': 100,
                  'upkeep_frequency': 'each Empire Phase',
                  'empire_bonus': 'Can Muster',
                  'tier': 'Primitive',
                  'build_time': 1,
                  'requirement': 'None'},
 'Wooden Walls': {'upkeep': 100,
                  'upkeep_frequency': 'each Empire Phase',
                  'empire_bonus': 'Authority -2 to Raze actions from players targeting your settlements. Authority -1 to Bandit Cunning actions targeting your settlements.',
                  'tier': 'Primitive',
                  'build_time': 1,
                  'requirement': 'None'},
 'Stone Roads': {'upkeep': 200,
                 'upkeep_frequency': 'each Empire Phase',
                 'empire_bonus': 'If you start a Move action within your Province, gain additional Speed +1',
                 'tier': 'Developed',
                 'build_time': 2,
                 'requirement': 'Dirt Roads'},
 'Town Hall': {'upkeep': 200,
               'upkeep_frequency': 'each Empire Phase',
               'empire_bonus': 'Influence +1 each Empire Phase',
               'tier': 'Developed',
               'build_time': 2,
               'requirement': 'One Tier Primitive'},
 'Chapel': {'upkeep': 200,
               'upkeep_frequency': 'each Empire Phase',
               'empire_bonus': 'Faith +1',
               'tier': 'Developed',
               'build_time': 2,
               'requirement': 'One Tier Primitive'},
 'Garrison': {'upkeep': 200,
              'upkeep_frequency': 'each Empire Phase',
              'empire_bonus': 'Local Armies form (10/15/25/50 by Settlement size). All Garrisons share '
                              "Retinues & Equipment. Can't be targeted; may not Sally Forth while under Siege. Do not pay upkeep.",
              'tier': 'Developed',
              'build_time': 2,
              'requirement': 'One Tier Primitive'},
 'Stone Walls': {'upkeep': 300,
                 'upkeep_frequency': 'each Empire Phase',
                 'empire_bonus': 'Authority -2 to Destabilize actions from players targeting your settlements. Authority -1 to Bandit Cunning actions targeting your settlements.',
                 'tier': 'Sophisticated',
                 'build_time': 3,
                 'requirement': 'One Tier Developed + Wooden Walls'},
'Bridges': {'upkeep': 0,
             'upkeep_frequency': '—',
             'empire_bonus': 'Armies cross Water Territory at full movement within your Province; Stone Roads may be built over '
                             'Water',
             'tier': 'Sophisticated',
             'build_time': 3,
             'requirement': 'Stone Roads'},
 'Library': {'upkeep': 300,
             'upkeep_frequency': 'each Empire Phase',
             'empire_bonus': 'Council Envoys you send are always Endorsed',
             'tier': 'Sophisticated',
             'build_time': 3,
             'requirement': 'Town Hall'},
'Road Wardens': {'upkeep': 300,
             'upkeep_frequency': 'each Empire Phase',
             'empire_bonus': 'Authority -1 to Bandit Cunning & Prowess actions targeting your settlements or armies.',
             'tier': 'Sophisticated',
             'build_time': 3,
             'requirement': 'Stone Walls'},
 "Magistrate's Hall": {'upkeep': 400,
                 'upkeep_frequency': 'each Empire Phase',
                 'empire_bonus': 'Gain Tax Income +1000 per Settlement.',
                 'tier': 'Prodigious',
                 'build_time': 4,
                 'requirement': 'Library'},
 'Keep': {'upkeep': 400,
          'upkeep_frequency': 'each Empire Phase',
          'empire_bonus': "When you Muster, reduce the Muster Timer by 1 and immediately gain Retinues equal to the combined muster limit. Siege Timer +1."
                          '',
          'tier': 'Prodigious',
          'build_time': 4,
          'requirement': 'Road Wardens'},
 'Aqueducts': {'upkeep': 400,
          'upkeep_frequency': 'each Empire Phase',
          'empire_bonus': 'Reach +1; Upkeep -500; Build Timer -1; Influence +1'
                          '',
          'tier': 'Prodigious',
          'build_time': 4,
          'requirement': 'Bridges'},
 'Cathedral': {'upkeep': 400,
               'upkeep_frequency': 'each Empire Phase',
               'empire_bonus': 'Faith +2',
               'tier': 'Prodigious',
               'build_time': 4,
               'requirement': 'One Tier Sophisticated + Chapel'},
 # ── Wondrous tier (Wonders): Realm Scope, one per game, built in your capital
 'Colossus': {'upkeep': 500,
              'upkeep_frequency': 'per Wonder',
              'empire_bonus': 'You may support your own Personal Prowess Envoys before other players '
                              'vote. Speed +2; Siege Timer -2, & gain Immune '
                              'Blunder.',
              'tier': 'Wondrous',
              'build_time': 10,
              'requirement': 'Keep'},
 'The Grand Exchange': {'upkeep': 500,
                        'upkeep_frequency': 'per Wonder',
                        'empire_bonus': 'You count as Trading with an additional 2 players. In addition, whenever you generate Trade Income by trading with another player, you generate twice as '
                                        'much for yourself.',
                        'tier': 'Wondrous',
                        'build_time': 10,
                        'requirement': 'Aqueducts'},
 'The Eternal Sepulchre': {'upkeep': 500,
                        'upkeep_frequency': 'per Wonder',
                        'empire_bonus': 'If your Public Order would ever be less than 5, set it to 5 '
                                        'instead. Your Settlements gain Reach +2.',
                        'tier': 'Wondrous',
                        'build_time': 10,
                        'requirement': 'Cathedral'},
 'High Chancery': {'upkeep': 500,
                   'upkeep_frequency': 'per Wonder',
                   'empire_bonus': 'Once per Envoy Phase, you may Endorse one Envoy Sent '
                                   'by yourself after voting.'
                                   '',
                   'tier': 'Wondrous',
                   'build_time': 10,
                   'requirement': "Magistrate's Hall"}
}
               
# Wonders are the Wondrous tier of INFRASTRUCTURE (combined Oct 2026). WONDERS is a derived view for code
# that needs just them; tables and cards list INFRASTRUCTURE only.
WONDERS = {k: v for k, v in INFRASTRUCTURE.items() if v.get("tier") == "Wondrous"}
INFRA_TIERS = ["Primitive", "Developed", "Sophisticated", "Prodigious", "Wondrous"]
for _n, _v in INFRASTRUCTURE.items():
    _v.setdefault("scope", "Realm" if _v.get("tier") == "Wondrous" else "Empire")
# ── EMPIRE RULES (ingested from Rules.docx — new data, nothing replaced) ─────
# Settlement tiers: tax is the WINTER collection (once per 4 turns); wards =
# pursuit slots (1 per tier; Hamlet exception); muster = retinues/turn.
# Presence (PRESENCE_RANGE, below SETTLEMENTS) replaced the per-tier / per-Retinue "aura" values: one flat range for every
# Settlement, Army and Bandit Army (Bandit Camps have none).
SETTLEMENTS = {
    "Hamlet":     {"tier": 0, "sea_variant": None,        "tax_income": 0,     "muster_limit":  0, "build_time": 1, "wards": 3, "reach": 1, "notes": "Natural pursuits only; exactly Range 2 from your capital; may always build Arable Land"},
    "Village":    {"tier": 1, "sea_variant": None,        "tax_income": 2000,  "muster_limit":  5, "build_time": 2, "wards": 1, "reach": 2, "notes": ""},
    "Town":       {"tier": 2, "sea_variant": "Sea Town",  "tax_income": 4000,  "muster_limit": 10, "build_time": 4, "wards": 2, "reach": 4, "notes": ""},
    "City":       {"tier": 3, "sea_variant": "Port",      "tax_income": 6000,  "muster_limit": 25, "build_time": 6, "wards": 3, "reach": 6, "notes": ""},
    "Metropolis": {"tier": 4, "sea_variant": "—",         "tax_income": 8000,  "muster_limit": 50, "build_time": 8, "wards": 4, "reach": 8, "notes": "Capital only, requires Sovereign Industry (Titan of Industry)"},
}

# Presence (Prowess rule): an Army can't move within PRESENCE_RANGE of a non-allied Settlement or Army (Bandit Armies
# included, Bandit Camps not) unless that Move performs a Battle or Lay Siege against it. Board: DATA.rulesConst.PRESENCE_RANGE.
PRESENCE_RANGE = 2
# Settlement Wards. "abstract" (live): Wards are slots inside the Settlement, never placed on the map.
# "range1" (audit variant): each Ward beyond the first occupies a Territory within Range 1 of the Settlement.
# Flip WARD_MODEL to audit; the rules prose reads WARD_RULE ({{VAL:WARD_RULE}}), the board reads DATA.rulesConst.WARD_MODEL.
WARD_MODEL = "abstract"
WARD_RULES = {
    "abstract": ("A Settlement Ward is a slot inside a Settlement that holds one Holding; Wards are never placed on the map. "
                 "A Settlement has one Ward per tier: a Village has {Village}, a Town {Town}, a City {City} and a Metropolis {Metropolis}. "
                 "A Hamlet has {Hamlet} Wards."),
    "range1":   ("A Settlement Ward is a slot that holds one Holding. A Settlement's first Ward is the Settlement itself; each further "
                 "Ward occupies a Territory within Range 1 of the Settlement and extends its Presence from there. A Settlement has one "
                 "Ward per tier: a Village has {Village}, a Town {Town}, a City {City} and a Metropolis {Metropolis}. A Hamlet has {Hamlet} Wards."),
}
WARD_RULE = WARD_RULES[WARD_MODEL].format(**{k: v["wards"] for k, v in SETTLEMENTS.items()})
# Faith is Fickle (Piety rule): while your Public Order is below this value, you can't target players with Piety actions.
FAITH_FICKLE_PO = 0

# Era progression: shared-Renown thresholds; caps on armies/cities; influence.
ERAS = {
    "Founding":  {"renown": 1,  "armies": 1, "cities": 0, "max_settlements": 2, "influence_per_turn": 1, "max_influence_per_diplomacy_vote": 1, "innate_diplomacy_influence": 1, "council_envoys": 1, "council_actions_per_envoy": 1, "personal_envoys": 1, "actions_per_envoy": 1, "po_scale_neg": 1, "po_scale_pos": 1, "unlocks": ""},
    "Ascension": {"renown": 8,  "armies": 2, "cities": 1, "max_settlements": 3, "influence_per_turn": 2, "max_influence_per_diplomacy_vote": 2, "innate_diplomacy_influence": 2, "council_envoys": 1, "council_actions_per_envoy": 2, "personal_envoys": 1, "actions_per_envoy": 1, "po_scale_neg": 2, "po_scale_pos": 1, "unlocks": "May Declare War"},
    "Eminence":  {"renown": 18, "armies": 3, "cities": 2, "max_settlements": 4, "influence_per_turn": 3, "max_influence_per_diplomacy_vote": 3, "innate_diplomacy_influence": 3, "council_envoys": 1, "council_actions_per_envoy": 2, "personal_envoys": 1, "actions_per_envoy": 2, "po_scale_neg": 3, "po_scale_pos": 1, "unlocks": "May form Military Alliances"},
    "Zenith":    {"renown": 30, "armies": 4, "cities": 3, "max_settlements": 5, "influence_per_turn": 4, "max_influence_per_diplomacy_vote": 4, "innate_diplomacy_influence": 4, "council_envoys": 1, "council_actions_per_envoy": 2, "personal_envoys": 2, "actions_per_envoy": 2, "po_scale_neg": 4, "po_scale_pos": 1, "unlocks": "May form Defensive Alliances"},
}
for _e in ERAS.values():
    _e["envoys"] = (f"{_e['council_envoys']} Council Envoy{'s' if _e['council_envoys'] > 1 else ''}"
                    f" ({_e['council_actions_per_envoy']} action{'s' if _e['council_actions_per_envoy'] > 1 else ''} each)"
                    f" + {_e['personal_envoys']} Personal Envoy{'s' if _e['personal_envoys'] > 1 else ''}"
                    f" ({_e['actions_per_envoy']} action{'s' if _e['actions_per_envoy'] > 1 else ''} each) per turn")

# Public Order track: state name + effect template + base value.
# Scaling by Era: {n} = base x the Era's scale — ERAS[era]["po_scale_neg"] for bands below 0, ["po_scale_pos"] above 0
# (set po_scale_pos > 1 to scale the positive bands too). {s} = plural "s" when n != 1. A band with no {n} never scales.
PO_BANDS = {
    -5: ("Uprising",      "Spawn {n} Bandit Camp{s} in your Outlaw Country", 1),
    -4: ("Recession",     "Tax Income -{n} per Settlement", 1000),
    -3: ("Aimless",       "Speed -{n}", 2),
    -2: ("Indecisive",    "Influence -{n}", 1),
    -1: ("Wavering",      "No effect", None),
     0: ("Neutral",       "No effect", None),
     1: ("Focused",       "No effect", None),
     2: ("Confident",     "Influence +{n}", 1),
     3: ("Motivated",     "Speed +{n}", 1),
     4: ("Economic Boom", "Tax Income +{n} per Settlement", 500),
     5: ("Eureka",        "May perform an Endorsed Industry Action", None),
     #6: ("Devout",        "Influence +1", None),
     #7: ("Pious",         "Immune Deficit", None),
     #8: ("Holy",          "Immune to Spread Gospel", None),
     #9: ("Sanctified",    "Immune to Send Missionaries", None),
    10: ("Living Saints", "Begin Pious Timer Edict", None),
}

def po_scale(level, era="Founding"):
    """The Era multiplier for a Public Order band (1 for Neutral and for bands that don't scale)."""
    e = ERAS.get(era) or ERAS["Founding"]
    if level < 0: return int(e.get("po_scale_neg", 1))
    if level > 0: return int(e.get("po_scale_pos", 1))
    return 1

def po_value(level, era="Founding"):
    """Scaled magnitude of a band's {n} (None if the band has no number)."""
    _nm, _t, base = PO_BANDS[level]
    return None if base is None or "{n}" not in _t else base * po_scale(level, era)

def po_effect(level, era="Founding"):
    """A band's effect text in an Era."""
    _nm, t, _b = PO_BANDS[level]
    n = po_value(level, era)
    return t if n is None else t.replace("{n}", str(n)).replace("{s}", "" if n == 1 else "s")

# Flat (Founding) view for every table that reads (name, effect); PUBLIC_ORDER_BY_ERA for the scaled text.
PUBLIC_ORDER = {k: (v[0], po_effect(k)) for k, v in PO_BANDS.items()}
PUBLIC_ORDER_BY_ERA = {e: {k: (v[0], po_effect(k, e)) for k, v in PO_BANDS.items()} for e in ERAS}

assert (min(PUBLIC_ORDER), max(PUBLIC_ORDER)) == (PO_MIN, PO_MAX), \
    f"PUBLIC_ORDER keys {min(PUBLIC_ORDER)}..{max(PUBLIC_ORDER)} != PO_MIN/PO_MAX {PO_MIN}..{PO_MAX}"

# Innate Faith/Doubt sources (per turn, applied at the Public Order step).
PO_MODIFIERS = {
    "faith": {
        "Lasting Legacy":  "Most recent Battle was Won",
        "Restored Order":  "Destroyed a Bandit Camp last turn",
    },
    "doubt": {
        "Local Unrest":    "Per active Bandit Camp in your Controlled Territory",
        "Deficit":         "Net Income is negative",
        "Insolvency":      "Per consecutive Upkeep Phase with negative Treasury",
        "Border Tension":  "Per other player Army in your Uncontested Territory (not Alliance or NAP)",
        "Invasion":        "Additional per other player Army in your Uncontested Territory at War",
        "State of Alarm":  "If at War",
        "Mounting Panic":  "Per Settlement being Besieged",
		"War Weariness":    "Per consecutive Battle loss"
    },
}

# Domain board: empire-side standing effects (combat-side lives in STANDING_EFFECTS).
DOMAIN_BOARD = {
    "Industry": {
        "Rising":      "Trade Secrets: Perform endorsed Build.",
        "Established": "Grand Architect: May have an additional Settlement. Perform endorsed Charter.",
        "Sovereign":   "Titan of Industry: Your capital may be chartered to a Metropolis. Perform endorsed Charter.",
    },
    "Prowess": {
        "Rising":      "Indomitable: Once per Envoy Phase, you may spend influence on your own Prowess Envoy after all players have voted.",
        "Established": "Edict of War: May have an additional Army. Perform a Muster Action.",
        "Sovereign":   "High Quartermaster: Upkeep -2000. May change equipment on your armies during any upkeep phase where that army is within your Province. No longer lose Influence while at War.",
    },
    "Cunning": {
        "Rising":      "Clandestine Councilor: Once per Envoy Phase, when voting on an Envoy begins, target a player with a lower Cunning value - that player Abstains that Envoy.",
        "Established": "Grand Vizier: Influence +1 each Empire Phase. Players may not target you with Cunning Envoys if your Cunning value is higher.",
        "Sovereign":   "Master Conspirator: Once per Envoy Phase, if your non-Cunning Envoy passes or is endorsed, you may instead perform a Cunning action.",
    },
    "Piety": {
        "Rising":      "Divine Mandate: Faith +1 each Empire Phase.",
        "Established": "One True Gospel: Each Empire Phase, all other non-allied players with a lower Piety value gain Doubt +2.",
        "Sovereign":   "Pillar of Faith: If your Public Order would be set below 3, set it to 3. In addition, may use the Sacred War action.",
    },
    # Influence scaling by standing (Untested/Rising/Established/Sovereign):
    "max_influence_per_vote":  {"Untested": 1, "Rising": 2, "Established": 3, "Sovereign": 4},
    "innate_influence_own_envoys": {"Untested": 1, "Rising": 2, "Established": 3, "Sovereign": 4},
}
_MIV = DOMAIN_BOARD["max_influence_per_vote"]
GLOSSARY["Standing"] = (f"Your tier in a Domain: Untested, Rising ({_ST['Rising']}), Established ({_ST['Established']}), "
                        f"Sovereign ({_ST['Sovereign']}). Sets max Influence per vote "
                        f"({'/'.join(str(_MIV[t]) for t in ('Untested', 'Rising', 'Established', 'Sovereign'))}) and unlocks Domain effects.")

# Seasons (turn cycle of 4; Rest Phase advances Season +1).
SEASONS = {
    "Winter": {"name": "Freezing",    "effect": "All Armies gain Speed -5; Siege Timers don't count down. Tax income collected."},
    "Spring": {"name": "Planting",    "effect": "No Host, Bandit Actions, Trade Income, Council Phase, or Diplomacy Actions. Players don't gain or spend Influence tokens. Bandit Camps Spawn."},
    "Summer": {"name": "Campaigning", "effect": "All Armies gain Speed +3"},
    "Fall":   {"name": "Harvest",     "effect": "Income from Holdings in Hamlets is doubled."},
}

# Trade & income constants (Rules: Trade & Income Rules).
TRADE_RULES = {
    "income_per_craft": 100,                # Trade Income = 100 x host's Craft X, per active agreement
    "requirements": "A signed Trade Agreement, and each player has active Dirt Roads or a Can Trade effect (e.g. Harbor, Shipyard)",
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
BANDIT_CAMP_START = 10
BANDIT_CAMP_GOLD = 2000    # gold in a Bandit Camp's treasury when it spawns
BANDIT_ARMY_THRESHOLD = 25
BANDIT_GROWTH_PER_ERA = {"Founding": 1, "Ascension": 2, "Eminence": 3, "Zenith": 4}
BANDIT_EQUIPMENT_PER_ERA = {"Founding": "Levy: Cudgel + Cloth", "Ascension": "Levy: Arming Sword, Targe Shield, & Leather Armor" , "Eminence": "Man-at-Arms: Halberd + Chainmail", "Zenith": "Man-at-Arms: Battle Axe + Full Plate"}
BANDITS = {
    "Bandit Domain Value": "For every 5 Retinues in the Bandit Camp or Army, the Bandit Camp has +2 Cunning and +2 Prowess.",
    "Bandit Camp": f"A collection of Bandits in Outlaw Country, starting with {BANDIT_CAMP_START} Retinues and {BANDIT_CAMP_GOLD} gold.",
    "Bandit Growth": f"Bandit Camps gain ({'/'.join(str(v) for v in BANDIT_GROWTH_PER_ERA.values())}) Retinues a turn, based on the Era of the Realm.",
    "Bandit Army": f"A Bandit Camp becomes a Bandit Army at {BANDIT_ARMY_THRESHOLD} Retinues. Performs Move actions toward the closest Settlement or Army, laying Siege or Skirmishing if possible, in addition to Bandit Cunning Mechanics. Bandit Armies cannot exceed {BANDIT_ARMY_THRESHOLD}",
    "Spawn a Bandit Camp": "Each Spring, every player gains a Bandit Camp.",
}

TIMERS = {
    "Build Timer":   {"where": "Infrastructure / Settlement Wards / Pursuits", "default": None, "tracks": "Turns until an infrastructure/build completes and becomes Active."},
    "Repair Timer":  {"where": "Damaged Pursuits / Infrastructure", "default": 2, "tracks": "Turns until a Damaged piece is repaired and its effects return."},
    "Truce Timer":   {"where": "Treaties / diplomacy outcomes", "default": 5, "tracks": "Turns remaining until a Truce expires (and related diplomacy restrictions end)."},
    "Siege Timer":   {"where": "Lay Siege", "default": None, "tracks": "Turns remaining until a Siege resolves."},
    "Muster Timer":  {"where": "Muster action", "default": 1, "tracks": "Turns remaining in a Muster; each turn it counts down, the Army gains Retinues up to the combined muster limit."},
    "Sack Timer":    {"where": "After Sacking a Settlement", "default": 2, "tracks": "Cooldown before the same force may Lay Siege again (per Sack rules)."},
    "Capture Timer": {"where": "Capturing a Settlement after Siege", "default": 1, "tracks": "Turns until a Captured Settlement becomes Controlled by the Player with the Capture Timer and applies the listed capture effects."},
    "Convert Timer": {"where": "Convert (Piety action)", "default": None, "tracks": "Turns until a Convert attempt resolves (or fails early if conditions change)."},
}

# ── Chartering / map placement constants (prose-only before; tunable balance) ──
CHARTER_MIN_RANGE   = 4   # min range a new settlement must be from any other settlement
OUTLAW_BUFFER_RANGE = 2   # new settlements must be at least this far from Outlaw Country
HAMLET_RANGE        = 2   # exact range a Hamlet sits from the capital
OUTLAW_COUNTRY_START = 3  # Outlaw Country territories demarcated at game start

# Wild Outlaw Country: neutral zones scattered over the unclaimed board as the last Setup step (after Deploy).
# Each zone is OUTLAW_COUNTRY_START connected Territories (no Water / Mountains), at least Range border_range from every
# player's Province (Settlement Reach) and at least Range spacing from every other Outlaw Country zone.
# count "formula" = floor(players / per_players) + plus; "fill" = as many zones as fit those ranges (capped by max, if set).
# After Setup a Wild zone is ordinary Outlaw Country: a zone is a player's Outlaw Country while any of its Territories is within their Province.
# Wild camps otherwise behave exactly like every other Bandit Camp (the three flags are plumbing; True = same as others).
WILD_OUTLAW = {
    "count": "formula",      # "formula" | "fill"
    "max": None,             # cap on zones in "fill" mode (None = no cap)
    "border_range": 3,       # min Range from any player's Province
    "spacing": 5,            # min Range from any other Outlaw Country zone
    "per_players": 2,        # "formula": floor(players / 2)
    "plus": 1,               # "formula": + 1
    "spring_spawn": True,    # Spring: each Wild zone spawns a Bandit Camp (full zone -> its camps grow instead)
    "spring_growth": True,   # Spring: Wild camps also grow, like every other camp
    "march": True,           # a Wild Bandit Army Marches like every other Bandit Army
}
# Glossary text that quotes a constant defined after GLOSSARY: fill it in here, so the number lives in one place.
GLOSSARY["Outlaw Country"] = GLOSSARY["Outlaw Country"].replace("{OUTLAW_COUNTRY_START}", str(OUTLAW_COUNTRY_START))
def wild_outlaw_count(players):
    return int(players) // WILD_OUTLAW["per_players"] + WILD_OUTLAW["plus"]

# Bandit targeting. "province": a camp targets the players whose Province (Settlement Reach) covers the camp's hex — any of
# those players' Settlements and Armies, nearest first (the Host breaks ties); a camp in nobody's Province takes no action.
# Alternatives kept as plumbing: None = only pieces within Presence (PRESENCE_RANGE) of the camp;
# an integer N = only pieces within Range N of the camp.
BANDIT_CAMP_REACH = "province"

# ── Vassalage ─────────────────────────────────────────────────────────────────
VASSAL_EXCHANGE_CAP = 5000  # max gold a Suzerain/vassal may exchange per Empire Phase
VASSAL_INFLUENCE_TAKE = 3   # first N Influence the vassal generates each turn goes to Suzerain


# Build durations in turns. Infrastructure keyed by its tier name.
BUILD_TIMERS = {
    "Pursuit": 1,
    "Rising Pursuit": 2,
    "Established Pursuit": 3,
    "Monument Pursuit": 4,
    "Village": SETTLEMENTS["Village"]["build_time"],
    "Town": SETTLEMENTS["Town"]["build_time"],
    "City": SETTLEMENTS["City"]["build_time"],
    "Metropolis": SETTLEMENTS["Metropolis"]["build_time"],
    "Wonder": 10,
    "Repair": 2,
    "Infrastructure": {"Primitive": 1, "Developed": 2, "Sophisticated": 3, "Prodigious":4},
}

TERRAIN = {
	"Grassland": {"Effect": "—", "Raw Materials": ["Arable Land", "Apiary"]},
	"Wetlands": {"Effect": "Speed -1 per Territory moved through", "Raw Materials": ["Peat Bog", "Forestry"]},
	"Tundra": {"Effect": "gain Strained", "Raw Materials": ["Quarry", "Salt Works"]},
	"Mountains": {"Effect": "Impassable", "Raw Materials": ["Mine", "Quarry"]},
	"Water": {"Effect": "Must end move after moving over 1 Water Territory (must end on land)", "Raw Materials": ["Fishmongery"]},
	"Forest": {"Effect": "Speed -1 per Territory moved through", "Raw Materials": ["Forestry","Apiary"]},
	"Hill":  {"Effect": "Gains Seize the Initiative. Where Settlements can be chartered."},
}

MOVEMENT_MODIFIERS = {
	"Dirt Roads" : {"Effect": "If you start a Move action within your Province, gain Speed +1"},
	"Stone Roads" : {"Effect": "If you start a Move action within your Province, gain additional Speed +1"},
	"Bridge" : {"Effect": "Immune Water Effect."},
	"Tunneler": {"Effect": "Immune Mountain Effect"},
	"Ancient Wilds": {"Effect": ["Ignore all Speed -X from Terrain", "Other armies gain Speed -2 in your Province."]},
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
    "Era": {"change": "/".join(f"+{e['influence_per_turn']}" for e in sorted(ERAS.values(), key=lambda e: e["renown"])),
            "notes": "Based on the Current Era"},
    "Trading Partners": {"change": "+1", "notes": "Per Trading Partner."},
    "Alliances": {"change": "+1", "notes": "Per Alliance Member."},
    "Infrastructure tier completed": {"change": "+1", "notes": "Per Infrastructure tier fully completed."},
    "Fully Mustered Army": {"change": "+1", "notes": "Per active Army of 25 Retinues."},
    "Condemned Envoy last turn": {"change": "-1", "notes": "Per Condemned Envoy last turn."},
    "At War": {"change": "-3", "notes": "While at War."},
    "Monuments & Wonders": {"change": "+1", "notes": "Per active Monument or Wonder."},
    "Other sources": {"change": "+X", "notes": "From other effects like Pursuits."},
}

# --- Glossary additions (map/spatial, action, and outcome terms) ---
GLOSSARY.update({
    "Border": "Your Province is within or adjacent to another player's Province",
    "Province": "The collection of Contested Territory and Controlled Territory by your Settlement's Reach.",
    "Region": "A collection of Territories of the same Type.",
    "Realm": "The total collection of Regions.",
    "Territory": "1 Hex.",
    "Controlled": "Territory that is within Reach of a Player's Settlement(s).",
    "Contested": "Territory that is Controlled by more than one player's settlement(s).",
    "Uncontested": "Territory that is Controlled by a single Player's Settlement(s).",
    "Uncontrolled": "Territory that is not within Reach of any Player Settlement.",
    "Adjacent": "Range 1.",
    "Next to": "Range 2.",
    "Within": "Range 0.",
    "Range X": "The amount of Territories you must move in order to get from your current position to the specific Territory.",
    "Reach X": "The Range X characteristic which determines what Territories you Control and are in your Province.",
	"Host": "Holds the Host Card; the starting player is the player directly clockwise from the Host, including in Spring. The role passes clockwise each Rest Phase (there is no Host in Spring). The Host collects and distributes Trade Income, resolves Bandit Mechanics, and breaks ties (Council vote, bandit targeting, and any tie not otherwise resolved).",
    "Send an Envoy": "Declare a Domain, spend 1 Envoy.",
    "Perform": "When you Perform an action, immediately do the description of the action. Pay the action's normal Cost.",
    "Resolve": "Determine modified Authority and follow Envoy Resolution Table.",
    "Cost / Pay": "Cost to perform an action, usually in Gold or Doubt.",
    "Fail": "An unsuccessful combat roll or Envoy resolution.",
    "Failed": "Net Authority 0, -1, or -2.",
    "Passed": "Net Authority 1 or 2.",
    "Endorsed": "Net Authority 3+.",
    "Condemned": "Net Authority -3 or less.",
    "Presence": f"Territory within Range {PRESENCE_RANGE} of a Settlement or Army (Bandit Armies included, Bandit Camps not). An Army can't move within the Presence of a non-allied Settlement or Army unless that Move performs a Battle or Lay Siege against it.",
    "Can Trade": "You may take part in trade without active Dirt Roads (you still need a signed Trade Agreement).",
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
ENVOY_OUTCOMES = { #Note, the condemned.split("+")[-1] is the "cost" for cunning piety and industry
    "Prowess":   {"condemned": "Doubt 1 + Armies gain Strain; if already Strained, that army gains Blocked.",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Perform a Move action"},
    "Cunning":   {"condemned": "Doubt 1 + pay 2000, & you cannot Recoup",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Extort 2000"},
    "Piety":     {"condemned": "Doubt 1 + Doubt 1",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Recoup Doubt"},
    "Industry":  {"condemned": "Doubt 1 + pay 2000, & you cannot Recoup",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Recoup 2000"},
    "Diplomacy": {"condemned": "Doubt 1 + you cannot perform or be the target of a diplomacy action this turn or next, unless you are a target of an end treaty action.",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Faith 1"},
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
        'effect': f'Move an Army up to its Speed in Territories. Then choose one: March — move up to {MARCH_MULTIPLIER}× Speed, lose 1 Endurance, take no other action; Battle — end adjacent to an at-war Army not in a Settlement, then begin a Battle; Lay Siege — end adjacent to an at-war Settlement, then begin a Siege.',
        'endorsed': 'Perform another Move action (same or a different Army).',
        'notes': ['Unless the move action was Endorsed, an Army may be the target of only one Move action per turn.', "Presence limits where the Army may move (see Rule: Presence).", "While an Army's Battle or Siege Timer is active, it can't be the target of actions.", "When an Army performs the Battle action, it gains Seize the Initiative in that Battle's first Skirmish."],
    },
    'Declare War': {
        'domain': 'Prowess',
        'cost': 'None',
        'requires': 'Rising Prowess',
        'effect': 'Choose a non-allied player you have no NAP or active truce with. You and that player are now At War, and any Trade Agreements between you end. If the target is in a Defensive Alliance, every member is now At War with you.',
        'endorsed': 'Perform a Move action.',
        'notes': ['If you are in a Military Alliance, then at the start of your next turn every member Declares War on the target and sends 1 fewer Envoy that turn.'],
    },
    'Pillage': {
        'domain': 'Prowess',
        'cost': 'None',
        'requires': 'Rising Prowess',
        'effect': "Choose an army you control within Reach of an at-war player's Settlement without an active Siege Timer. While that army remains within Reach of that Settlement and does not Lay Siege, Battle, or March, it may Extort half of that Settlement's pursuit income in the Extort step. A Settlement may be Pillaged once per Empire Phase. Pillage ends if [war ends / army leaves Reach / Settlement is besieged].",
        'endorsed': 'Perform a Move action.',
    },
    'Muster': {
        'domain': 'Prowess',
        'cost': 'None',
        'requires': '',
        'effect': (f"Choose one: Raise — if you have fewer Armies than your Era allows, place a new Army within a Settlement under your Control; or "
                   f"Reinforce — choose an Army you control. The Army must be within range {MUSTER_RANGE} of a Settlement "
                   f"you Control with an active Muster Field, and at least Range 2 from any non-allied Army unless it is "
                   f"within Range 0 of a Settlement you Control. Choose how many Retinues to recruit (an Army "
                   f"can't exceed {ARMY_MAX_RETINUES}) and set a Muster Timer equal to that number ÷ your combined muster "
                   f"limit, rounded up. Each turn the Muster Timer counts down, the Army gains Retinues up to your "
                   f"combined muster limit and you begin paying their upkeep. You may change the Army's Retinue type "
                   f"and equipment while an army has an active Muster Timer."),
        'endorsed': 'Perform a Move action.',
        'notes': ["Combined muster limit: the total muster limit of your Settlements whose Reach includes the Army's Territory.",
                  "While a Settlement is besieged, its muster limit is 0; an active Muster Timer doesn't count down and may be cancelled at any time."],
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
        'effect': "Choose another player's Settlement, then choose one active Pursuit, active Infrastructure, or active Build Timer in it: that target becomes Damaged, and its effects are inactive until Repaired. A Damaged Build Timer doesn't count down until Repaired. If an active Build Timer hasn't been completed, instead, increase the Timer by 2.",
        'endorsed': 'Extort 2000.',
        'notes': ["A Wonder has Immune Razed and can't be targeted."],
    },
    'Destabilize': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': "Choose a player. In the next Winter phase, during the Extort step, Extort one settlement's tax income. Each settlement can only be Destabilized once per Winter.",
        'endorsed': 'Extort 2000.',
        'notes': ["If multiple players extort the same player, the player with the highest Cunning value chooses which settlement(s) are extorted first. In the event of a tie, or if there are not enough settlements, the Extort value is divided equally."],
    },
    'Sabotage': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': 'Choose an army, that army gains Blocked until the end of next turn.',
        'endorsed': 'Extort 2000.',
        'notes': [],
    },
    
    'Spread Truth': {
        'domain': 'Piety',
        'cost': 'Doubt 1',
        'requires': '',
        'effect': 'Each non-allied player gains Doubt 1. Each allied player gains Faith 1.',
        'endorsed': 'Recoup Doubt.',
    },
    'Send Missionaries': {
        'domain': 'Piety',
        'cost': 'Doubt 1',
        'requires': '',
        'effect': 'Choose a target player or Alliance. If the target is outside your Alliance, each player in it gains Doubt 2. If the target is inside your Alliance, each other allied player gains Faith 2.',
        'endorsed': 'Recoup Doubt.',
    },
    'Tithe': {
        'domain': 'Piety',
        'cost': 'Doubt 1',
        'requires': '',
        'effect': 'Choose a player. Extort 10% of their Treasury (round down to the nearest 100, minimum 0).',
        'endorsed': 'Recoup Doubt.',
    },
    'Convert': {
        'domain': 'Piety',
        'cost': 'Doubt 1',
        'requires': 'Sovereign Piety',
        'effect': f"Choose another player's closest non-capital Settlement; its Public Order must be {PO_MIN} or lower. Lay Siege using only Settlement-type Siege modifiers (Settlement Size and Citadel) and set a Convert Timer. When it reaches 0, the Settlement joins your empire (see Capture).",
        'endorsed': 'Recoup Doubt.',
        'notes': ["If the target's Public Order rises to 1 or higher before the timer reaches 0, the Convert fails and the timer is removed."],
    },
    'Sacred War': {
        'domain': 'Piety',
        'cost': 'Doubt 1',
        'requires': 'Sovereign Piety',
        'effect': 'Declare War on a non-ally you have no NAP or truce with, then immediately perform a Move action with one of your Armies.',
        'endorsed': 'Recoup Doubt.',
        'notes': [
            'While a Sacred War is active, neither player may Declare War on, Sign or End a Treaty with, Negotiate with, or Demand Tribute from the other. All previous treaties are immediately Ended.',
            'You may have only one active Sacred War at a time. It ends only when one of the two players is Vassalized or otherwise removed from the game.',
            'When you perform this action, members of Military and Defensive Alliances are ignored.',
            'If the target of this action is vassalized by any player, the Sacred War can be transferred to the Suzerain if the player who performed the action wishes.',
        ],
    },
    'Build': {
        'domain': 'Industry',
        'cost': '2000 gold',
        'requires': '',
        'effect': 'Choose an unlocked, available Infrastructure and set a Build Timer equal to its build time. When it completes, the Infrastructure becomes active in every Settlement in your Province.',
        'endorsed': 'Recoup 2000.',
        'notes': ['You must have at least one Infrastructure from the prior tier before building the next tier.', 'A Wonder is built in your capital.'],
    },
    'Repair': {
        'domain': 'Industry',
        'cost': '0 gold',
        'requires': '',
        'effect': f'Choose a Damaged Pursuit or Infrastructure in a Settlement you control and set Repair Timer {TIMERS["Repair Timer"]["default"]}. When it reaches 0, choose one: Restore — reactivate it with all effects; Demolish — remove the Pursuit tile from your Empire Tableau.',
        'endorsed': 'Recoup 0.',
    },
    'Pursue': {
        'domain': 'Industry',
        'cost': '2000 gold',
        'requires': '',
        'effect': 'Choose an inactive Settlement Ward you control, then choose a Pursuit whose prerequisites you meet and set a Build Timer equal to its build time (usually 1). When it completes, place the Pursuit in an available Ward slot; its innate effect activates immediately, and its mastery effect activates if all mastery requirements are met.',
        'endorsed': 'Recoup 2000.',
        'notes': ['You may have only 2 Monument Pursuits across your empire.', f'Pursuits have Build Timers according to their required Standing. Ungated: 1, Rising: 2, Established: 3, & Sovereign: 4.'],
    },
    'Charter': {
        'domain': 'Industry',
        'cost': '2000 gold',
        'requires': 'Rising Industry',
        'effect': f'Choose one: Charter a new Village — on uncontrolled or in-province non-water, non-mountain Territory, range {CHARTER_MIN_RANGE}+ from any Settlement and range {OUTLAW_BUFFER_RANGE}+ from Outlaw Country; or Expand a non-City Settlement one tier into an adjacent Territory (Village to Sea/Town, Sea/Town to Port/City, Port/City to Metropolis), adding a Ward.',
        'endorsed': 'Recoup 2000.',
        'notes': ["To upgrade to City or Metropolis you must meet that tier's requirements; otherwise set Build Timer 1."],
    },
    'Sign Treaty': {
        'domain': 'Diplomacy',
        'cost': 'None',
        'requires': '',
        'effect': f'Ask players to agree, then choose one and both sign it: Peace Treaty — end the war, set Truce Timer {TIMERS["Truce Timer"]["default"]}; Trade Agreement — begin trading next turn; Non-Aggression Pact — no Declare War (ending it via End Treaty gives both Truce Timer {TIMERS["Truce Timer"]["default"]}); Alliance — join, form, or invite to a Defensive or Military Alliance.',
        'endorsed': 'Faith +1.',
        'notes': ['When acting on behalf of an Alliance, End Treaty requires all allies to agree.', "A player can't be in more than one Alliance."],
    },
    'Negotiate': {
        'domain': 'Diplomacy',
        'cost': 'None',
        'requires': '',
        'effect': 'Propose terms to a target; they agree or refuse. Terms may include gold, Settlement ownership, Territory, signing or ending a Treaty, or promises (non-binding).',
        'endorsed': 'Faith +1.',
        'notes': ['If a promise goes unfulfilled, the affected player may Declare War on the promiser.', 'Also used to resolve Demand Tribute and Siege surrenders.'],
    },
    'End Treaty': {
        'domain': 'Diplomacy',
        'cost': 'None',
        'requires': '',
        'effect': "Choose a target with whom you have an active Treaty and no active Truce Timer; remove that Treaty. The target doesn't need to agree.",
        'endorsed': 'Faith +1.',
    },
}

# ── TREATIES ────────────────────────────────────────────────────────────────
# The standing agreements players can hold. signed_via is the action; ended_via
# notes how it ends; era is when it unlocks (alliances scale with Era).
TREATIES = {
    "Peace Treaty":      {"signed_via": "Sign Treaty", "effect": f"Ends war between the two players; sets Truce Timer {TIMERS['Truce Timer']['default']}.", "era": "Any"},
    "Trade Agreement":   {"signed_via": "Sign Treaty", "effect": "Begin trading (Trade Income flows from next turn). Requires bordering, and each player has active Dirt Roads or a Can Trade effect.", "era": "Any"},
    "Non-Aggression Pact": {"signed_via": "Sign Treaty", "effect": f"Neither player may Declare War on the other. Ending it via End Treaty gives both a Truce Timer {TIMERS['Truce Timer']['default']}.", "era": "Any"},
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
EDICT_STREAK_TURNS = 5      # consecutive-turn Edicts (Wealth, Living Saints)
_NUMWORD = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten"}
EDICTS = {
    "Sovereign Standing": {"type": "Standing",  "requirement": f"Reach a Sovereign Standing (Domain value {_ST['Sovereign']}) in any Domain."},
    "Monument":           {"type": "Build",     "requirement": "Have an active Mastery Effect of a Monument pursuit."},
    "Wonder":             {"type": "Build",     "requirement": "Complete a World Wonder."},
    "Wealth":             {"type": "Economy",   "turns": EDICT_STREAK_TURNS, "requirement": f"Hold {WEALTH_EDICT_GOLD:,} gold in your Treasury for {_NUMWORD[EDICT_STREAK_TURNS]} consecutive turns."},
    "Vassalize":          {"type": "Conquest",  "requirement": "Vassalize a rival player (control their capital with no other settlements/armies under them)."},
    "Living Saints":      {"type": "Piety",     "turns": EDICT_STREAK_TURNS, "requirement": f"Sustain Public Order {PO_MAX} (Living Saints) for {_NUMWORD[EDICT_STREAK_TURNS]} consecutive turns (Pious Timer)."},
    "Last Alliance Standing": {"type": "Endgame", "requirement": "Be the last alliance standing — the game-ending stop condition."},
}
# Note: consecutive-turn Edicts require the timer to advance each turn; if it
# fails to advance for any reason, remove the timer until restarted.

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
# 2) ARMY upkeep     — sum of each Army's cost (RETINUES[type]["cost"], per Army)
#    minus "Upkeep -X" modifiers. The "Upkeep -X" effects (Levy Hall, Tannery,
#    Armory, Butchery, Fletchery, Smokehouse, ABF, ...) are summed and subtracted
#    once from the total of all Armies (never below 0).
# 3) INFRASTRUCTURE upkeep — the per-settlement upkeep in INFRASTRUCTURE.
#    Trade Guild removes upkeep on Primitive (innate) and Developed (mastery)
#    infrastructure; College of Engineering removes it on Sophisticated.
PURSUIT_UPKEEP_DEFAULT = 100
PURSUIT_UPKEEP_BY_TYPE = {
    "Monument": 300,
    "Power":    200,
    "Energy":   0,
    "Other":    PURSUIT_UPKEEP_DEFAULT,
}
_PU = PURSUIT_UPKEEP_BY_TYPE
_PU_TEXT = (f"Monument {_PU['Monument']}, Power {_PU['Power']}, "
            f"Energy/Natural {_PU['Energy']}, all others {_PU['Other']}")

UPKEEP_TRACKS = {
    "Pursuit":        f"Fixed by pursuit type: {_PU_TEXT}.",
    "Army":           "Σ(each Army's cost by Retinue type) - Upkeep -X. Reduced by Levy Hall, Tannery, Saddlery, Butchery, Smokehouse, Advanced Blast Furnace, High Quartermaster, etc.",
    "Infrastructure": "Per-Empire upkeep in INFRASTRUCTURE. Trade Guild removes Primitive (innate) + Developed (mastery); College of Engineering removes Sophisticated.",
}

# SIMPLE: Holding upkeep & Build Timer by Standing tier of its unlock. Natural: no upkeep (Build Timer unchanged).
HOLDING_TIER_COST = {                     # standing -> (upkeep, build timer)
    None:          (PURSUIT_UPKEEP_DEFAULT, BUILD_TIMERS["Pursuit"]),
    "Rising":      (200, 2),
    "Established": (300, 3),
    "Sovereign":   (400, 4),
}
_STANDINGS = ("Rising", "Established", "Sovereign")

def holding_standing(node):
    """Standing tier from an unlock string ('1 Rising', '4 Established', '-')."""
    n = NODES.get(node, {}) if isinstance(node, str) else (node or {})
    u = str(n.get("unlock", "") or "")
    return next((t for t in _STANDINGS if t in u), None)

def holding_cost(node):
    """(upkeep, build timer) for a Holding — name or node dict."""
    n = NODES.get(node, {}) if isinstance(node, str) else (node or {})
    up, tm = HOLDING_TIER_COST[holding_standing(n)]
    if re.search(r"\bNatural\b", re.sub(r"\*\*", "", str(n.get("innate", "")))):
        up = 0
    return up, tm

def holding_build_time(node):
    return holding_cost(node)[1]

_HTC = HOLDING_TIER_COST
_HOLDING_COST_TEXT = (f"by Standing: Untested {_HTC[None][0]} (Build Timer {_HTC[None][1]}), "
    + ", ".join(f"{t} {_HTC[t][0]} (Build Timer {_HTC[t][1]})" for t in _STANDINGS) + "; Natural 0")
HOLDING_COST_TEXT = _HOLDING_COST_TEXT    # rules prose: {{VAL:HOLDING_COST_TEXT}} (SIMPLE: upkeep + Build Timer by Standing)

def pursuit_upkeep(node):
    """Per-turn upkeep for a node. SIMPLE: by Standing (holding_cost). Legacy: fixed by type.
    node = a NODES entry (dict) or a type string."""
    if SIMPLE and isinstance(node, dict):
        return holding_cost(node)[0]
    if isinstance(node, dict) and re.search(r"\bNatural\b", re.sub(r"\*\*", "", str(node.get("innate", "")))):
        return 0                                   # GLOSSARY["Natural"]: Natural Pursuits do not cost Upkeep
    t = node.get("type") if isinstance(node, dict) else node
    return PURSUIT_UPKEEP_BY_TYPE.get(t, PURSUIT_UPKEEP_DEFAULT)

# 2) ARMY upkeep — formula note (per-retinue costs in RETINUES[*]["cost"]).
ARMY_UPKEEP_NOTE = "Net Army Upkeep = the sum of each Army's cost (by Retinue type) - Upkeep -X modifiers."

# ── ACTION / EMPIRE GOLD COSTS ───────────────────────────────────────────────
# The flat costs the rules attach to actions and siege outcomes.
COSTS = {
    "Pursue action":   f"{ACTIONS['Pursue']['cost']} (the envoy action; pursuit then costs upkeep by type each Empire Phase)",
    "Pursuit upkeep":  f"Each Empire Phase, by type (fixed): {_PU_TEXT}",
    "Army upkeep":     "sum of each Army's cost (by Retinue type) - Upkeep -X modifiers",
    "Infrastructure upkeep": "Per-settlement (see INFRASTRUCTURE); Trade Guild removes Primitive/Developed, College of Engineering removes Sophisticated",

    "Sack":            f"Raze the top-most Holding of each Ward; Extort {SACK_EXTORT_PER_TIER} per settlement tier; reduce settlement by 1 tier; the controller removes one Ward (sacker's choice) and its Holdings; Sack Timer {TIMERS['Sack Timer']['default']}",
    "Tax per tier":    "Winter tax by Settlement tier: " + " / ".join(f"{k} {v['tax_income']}" for k, v in SETTLEMENTS.items()),
    "Trade Income":    "100 x host's Craft X per active Trade Agreement",
}
# "<Domain> action" cost lines are read from ACTIONS (grouped by cost); rerun after ACTIONS changes (SIMPLE overlay).
def _action_costs():
    for _dom in ("Cunning", "Industry", "Piety", "Prowess", "Diplomacy"):
        _g = {}
        for _a, _r in ACTIONS.items():
            if _r.get("domain") == _dom: _g.setdefault(_r.get("cost") or "None", []).append(_a)
        COSTS[f"{_dom} action"] = "; ".join(f"{_c} ({' / '.join(_n)})" for _c, _n in _g.items())
_action_costs()

# phase order (currently only in RULES_reorganized)
PHASES = ("Empire", "Council", "Envoy", "Battle", "Rest")
STARTING_TURN_PHASE_OPENER = PHASES[1]
# ACTIONS["Move"] says "March (move up to 2x Speed)"
STANDING_ARMY_SIEGE_MODIFIER = 1
# economy.py has this as a local constant (EMPIRE_START)
EMPIRE_START_TIERS = ("Town", "Hamlet")
STARTING_TREASURY = 10000

# ── Setup: Ages (Setup step 2) ────────────────────────────────────────────────
# Names/years mirror worldbuilding/renown_worldlore.py AGES["names"] + TIMELINE["age_starts"]
# (Year 0 = the Great Fracture). "rising": the Domain every player starts Rising in;
# None = each player chooses their own. "years": (first, last) starting Year players may pick.
AGES = {
    "Age of Fracture":       {"rising": "Prowess",  "years": (0, 1352)},
    "Age of Plenty":         {"rising": "Industry", "years": (1352, 1942)},
    "Age of the Tetramorph": {"rising": "Piety",    "years": (1942, 3066)},
    "Age of Doubt":          {"rising": "Cunning",  "years": (3066, 4516)},
    "Age of Renown":         {"rising": None,       "years": (4516, 4589)},
}
AGE_YEAR_SEASON = "Spring"   # the Year advances by 1 each time the Season changes to this Season
CAPITAL_EDGE_RANGE = 4       # capital Town is deployed within this range of the board edge (or corner)

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
                        "rule": "Army within Range 0 of the Settlement"},
    "Garrison":        {"value": 1},
    "Wooden Walls":    {"value": 1},
    "Stone Walls":     {"value": 1},
    "Citadel":         {"innate_value": 1, "mastery_value": 1},
}

# ── Missing glossary definitions (CE) ────────────────────────────────────────
GLOSSARY.update({
    PIVOTAL:        f"A natural {FOCUSED_THR}, before modifiers." if FOCUSED_THR == FACES else f"A natural {FOCUSED_THR} or higher, before modifiers.",
    FATIGUE_TOKEN:  f"Each token reduces Morale by {FATIGUE_MORALE}; if your modified Morale is ever {ROUT_THR}+, your army Routs. Tokens stack.",
    "Sally Forth":  "While a settlement you control is besieged and you have an army inside it, you may Sally Forth: Battle in the Battle Phase without performing an action.",
    "War Weariness":"gain Doubt 1 for each consecutive Battle you lose in the Empire Phase.",
    "Settlement Ward": ("A slot in a Settlement that holds one Pursuit; a Settlement has one Ward per tier (a Hamlet has 3 Wards, Natural Pursuits only)."
                        + (" Wards are not placed on the map." if WARD_MODEL == "abstract" else " Each Ward beyond the first occupies a Territory within Range 1 of the Settlement.")),
    "Efficient X":  "While this Pursuit occupies the same Settlement Ward as X (the Raw Material or Pursuit named on its tile), it uses no ward of its own \u2014 the two share one ward. Placed anywhere else, it fills a ward normally. (Core Principle 13.) Note: Two Pursuits that are Efficient with the same Pursuit cannot share a Ward with each other.",
})

# ══════════════════════════════════════════════════════════════════════════════
# DISPLAY LAYER — engine ids stay stable; only printed labels change.
# Add an alias here, never rename an id in NODES/WEAPONS/TIERS/loadouts.
# ══════════════════════════════════════════════════════════════════════════════
import re as _re_disp

# Entity ids -> printed label (weapons, ranged, shields, armor, nodes).
NAME_DISPLAY = {
    "Tundra": "Barrens",          # terrain: key stays Tundra (mapgen kind "tundra"); players read Barrens
    "Spears": "Spear",
    "Pilum": "Throwing Spear",
    "Farm Tools": "Farm Tool",
    "Artillery Park": "Ordinance Yard",
    "Coliseum": "Castle Yard",
    "Javelin": "Throwing Axe",
    "Crafted" : "Tempered",
    "Gambeson": "Padded",
    #"to-hit", "to-Strike",
    #"Recover", "Heal",
    "Preceptory of the Knight's Templar": "Sacred Preceptory",
    "Knight's Templar": "Oathsworn",
    "Knight Templar": "Oathsworn",
    "Recover": "Heal",
    "RECOVER": "HEAL",
    "Recovered" : "Healed",
    "Reliquary": "Reliquary Sanctum",
    "TH": "To Strike",
    "TS": "Armor Save",
    "The Eternal Sepulchre": "The Exalted Archbasilica",
    "Exalted Basilica":"Eternal Sepulchre",
    

    
}

# Equipment tier ids -> printed label. Separate map because tiers are a closed
# set the engine keys on (loadouts.TIER_INDUSTRY_REQ, WEAPONS_BY_TIER, ...).
TIER_DISPLAY = {
    "Crafted": "Tempered",
}
# Per-item tier label, display only. The item keeps its real tier id for the engine
# (Arquebus = Crude: no Industry gate, so Artillery Park + Fletchery are its only unlocks).
# Labels here are never added to TIERS, so loadouts / the board's tier ladder are untouched.
ITEM_TIER_DISPLAY = {
    "Arquebus": "Gunpowder",
}

# Envoy score term. "Influence" = spendable tokens (gain +X Influence, Support/Oppose X);
# the Envoy's score (innate/net value, postfix "Influence ±X" modifiers) prints as TERM_ENVOY_SCORE.
# Convention relied on: postfix "Influence +1" = score modifier; prefix "+1 Influence" = tokens.
TERM_ENVOY_SCORE = "Authority"
_SCORE_RES = [
    (_re_disp.compile(r"\b([Nn]et|[Ii]nnate|[Ss]tarting|Envoy's net|Envoy's|action's) Influence\b"),
     lambda m: f"{m.group(1)} {TERM_ENVOY_SCORE}"),
    # the data writes the Envoy-score modifier as "Authority ±N" ("Influence ±N" is now always Influence tokens);
    # a different TERM_ENVOY_SCORE renames it here
    (_re_disp.compile(r"\bAuthority(\**\s?)([+\-\u2212\u00b1]\s?\d+|[+\-\u2212\u00b1]?X\b)"),
     lambda m: f"{TERM_ENVOY_SCORE}{m.group(1)}{m.group(2)}"),
]

def display_score(s):
    """Rewrite Envoy-score uses of 'Influence' to TERM_ENVOY_SCORE; token uses untouched."""
    if not s or TERM_ENVOY_SCORE == "Influence":
        return s
    s = str(s)
    for rx, rep in _SCORE_RES:
        s = rx.sub(rep, s)
    return s

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


def display_tier(tier, item=None):
    """Player-facing label for a tier id. Handles None/'' (shields).
    Pass the item name to honour a per-item label (ITEM_TIER_DISPLAY)."""
    if item is not None and item in ITEM_TIER_DISPLAY:
        return ITEM_TIER_DISPLAY[item]
    return TIER_DISPLAY.get(tier, tier) if tier else tier


_MINUS_RE = _re_disp.compile(r"(?<![\w\-\u2212/.])-(?=\d|X\b)")   # a signed number: "Speed -2", "-1000"; not "1-3", "x-2"

def display_text(s):
    """Rewrite every alias inside a free-text string — mastery_req, effect and
    note text, escalation ranks. Single pass over a combined pattern, so a
    rename can never cascade into another rename's output."""
    if not s:
        return s
    s = _MINUS_RE.sub("\u2212", display_score(s))
    if _ALIAS_RE is None:
        return s
    def _rep(m):
        k, v = m.group(1), ALIASES[m.group(1)]
        # idempotent: if this match is already part of its own new name (e.g. "Reliquary" inside
        # "Reliquary Sanctum"), leave it — so running the display layer twice never stacks renames
        st = m.string; i = m.start()
        o = v.find(k)
        while o != -1:
            if st[i - o:i - o + len(v)] == v:
                return k
            o = v.find(k, o + 1)
        return v
    return _ALIAS_RE.sub(_rep, str(s))


def display_list(seq, sep=", "):
    """Join an id list (builds_into, prereqs, requires_all) as labels."""
    return sep.join(display(x) for x in (seq or []))


# ── whole-document helpers: alias everything a player READS, never ids/markers/markup ──
_MD_MARKER_RE = _re_disp.compile(r"(\{\{[^}]*\}\})")
_HTML_SPLIT_RE = _re_disp.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", _re_disp.S | _re_disp.I)


def display_md(s):
    """display_text for Markdown prose (rules), leaving {{VAL:}}/{{TABLE:}}/{{DEF:}} markers untouched."""
    if not s or _ALIAS_RE is None:
        return s
    return "".join(p if p.startswith("{{") else display_text(p) for p in _MD_MARKER_RE.split(str(s)))


def display_html(html):
    """display_text for a finished HTML page: only text between tags; tags, attributes (hrefs, ids,
    anchors), <script> and <style> are left as-is."""
    if not html or _ALIAS_RE is None:
        return html
    def _txt(p):   # text between tags: match names whose apostrophe was HTML-escaped (&#x27; / &#39; / &apos;)
        q = _re_disp.sub(r"&#x27;|&#39;|&apos;", "'", p)
        r = display_text(q)
        return p if r == q else r.replace("'", "&#x27;")
    return "".join(p if p.startswith("<") else _txt(p) for p in _HTML_SPLIT_RE.split(str(html)))


def display_obj(o):
    """display_text over every string (dict keys included) in a JSON-able structure."""
    if _ALIAS_RE is None:
        return o
    if isinstance(o, str):
        return display_text(o)
    if isinstance(o, dict):
        return {display_obj(k) if isinstance(k, str) else k: display_obj(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return type(o)(display_obj(x) for x in o)
    return o


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
    (1, 3):  "Raze",
    (4, 5):  "Intercept Caravan",
    (6, 7):  "Sabotage",
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
         1:  "Scout",
         2:  "Ambush",
         3:  "Flank",
    (4, 6):  "Charge",
    (7, 8):  "Fighting Formation",
   (9, 10):  "Defensive Formation",
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
BANDIT_BEHAVIOR["Targeting"] = (
    ("A camp's Cunning action targets the Settlements and Armies of the players whose Province covers the camp"
     if BANDIT_CAMP_REACH == "province" else
     f"A camp's Cunning action targets only a player's Settlement or Army within Range {PRESENCE_RANGE} (Presence) of the camp"
     if BANDIT_CAMP_REACH is None else
     f"A camp's Cunning action targets only a player's Settlement or Army within Range {BANDIT_CAMP_REACH} of the camp")
    + ", nearest first; none: no action. Wild Outlaw Country camps spawn, grow" + (" (not in Spring)" if not WILD_OUTLAW["spring_growth"] else "")
    + " and " + ("March" if WILD_OUTLAW["march"] else "hold instead of Marching") + " like any other camp.")
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

# ── Keyword glossary: entries built from the data (so hovers/wiki stay in step with it) ──────────
import re
GLOSSARY.update({
    "Natural": "Natural Pursuits do not cost Upkeep & can be used in Hamlets.",
    "Upkeep":  (f"Gold you pay each Empire Phase for Armies, Pursuits and Infrastructure. Pursuit upkeep is fixed by type "
                f"({_PU_TEXT}); a Pursuit pays no upkeep while its Build Timer is running. Army upkeep = the sum of each "
                f"Army's cost (by Retinue type) − Upkeep modifiers."),
    "Craft":   (f"Craft Pursuits count toward how much income your Trade Agreements generate — any effect that grants Craft +X. "
                f"For each active Trade Agreement, both players gain {TRADE_RULES['income_per_craft']} × the Host's Craft X."),
    "Efficient": ("A Pursuit is efficient with the Raw Material or Pursuit named on its tile. While it shares a Settlement Ward "
                  "with that piece, it doesn't consume a Ward of its own."),
    "Speed X":         f"An Army's movement range in Territories per Move action. Base Speed value of an army is Speed {RETINUES['Levy']['speed']}",
    "Pursuit":   (f"An object that is placed into a Settlement Ward or onto a Root Pursuit as a result of a "
                  f"{'Build' if SIMPLE else 'Pursue'} action, giving effects which affect your Empire in many ways."),
    "Retinue":   "A single unit within an Army, represented by a single die roll for Strikes, Saves, etc.",
    "At War":    "Cannot trade; can be the target of Siege, Battle, & Pillage actions from players At War with this player.",
    "Equipped":  "The weapon chosen for the Skirmish.",
})
for _k, _v in TIMERS.items():                      # Build Timer, Repair Timer, Truce Timer, …
    GLOSSARY.setdefault(_k, _v["tracks"])

def _tier_items(src, t):
    return [k for k, v in src.items() if k and v.get("tier") == t and k not in ITEM_TIER_DISPLAY]
def _unlockers(tier):
    """[(pursuit, {'weapons','armor','shield'})] from Pursuit text: 'Unlocks Cast Weapons', 'Unlock Wrought armor & shield',
    'Unlocks Forged Tier', 'Crafted Tier Unlocked' (a whole Tier = all three)."""
    out = []
    for n, d in NODES.items():
        for part in ("innate", "mastery"):
            t = re.sub(r"\*\*", "", d.get(part, "") or "").lower(); tl = tier.lower(); c = set()
            if re.search(rf"unlocks?\s+{tl}\s+tier|{tl}\s+tier\s+unlocked", t): c = {"weapons", "armor", "shield"}
            else:
                if re.search(rf"unlocks?\s+{tl}\s+weapons", t): c.add("weapons")
                if re.search(rf"unlocks?\s+{tl}\s+armor", t): c.add("armor")
                if re.search(rf"unlocks?\s+{tl}\s+(armor\s+(&|and)\s+)?shields?", t): c.add("shield")
            if c: out.append((n + ("" if part == "innate" else " (Mastery)"), c))
    return out
def _ulabel(c):
    return "all" if len(c) == 3 else " & ".join(x for x in ("weapons", "armor", "shield") if x in c)
for _t in TIERS:
    _d = TIER_DISPLAY.get(_t, _t)
    _parts = [(lab, _tier_items(src, _t)) for lab, src in
              (("Weapons", WEAPONS), ("Ranged", RANGED), ("Armor", ARMORS), ("Shield", SHIELDS))]
    _u = _unlockers(_t)
    GLOSSARY.setdefault(_d, f"{_d} equipment tier. " + "; ".join(f"{lab}: {', '.join(xs)}" for lab, xs in _parts if xs) + "."
                        + (f" Unlocked by: {', '.join(n + ' (' + _ulabel(c) + ')' for n, c in _u)}." if _u else ""))
    for _lab, _srcs, _cat in (("Weapons", (WEAPONS, RANGED), "weapons"), ("Armor", (ARMORS,), "armor"), ("Shields", (SHIELDS,), "shield")):
        _xs = [x for s in _srcs for x in _tier_items(s, _t)]
        _uu = [n for n, c in _u if _cat in c]
        if _xs:
            GLOSSARY.setdefault(f"{_d} {_lab}", f"{_d}-tier {_lab.lower()}: {', '.join(_xs)}." + (f" Unlocked by: {', '.join(_uu)}." if _uu else ""))
for _lbl in sorted(set(ITEM_TIER_DISPLAY.values())):           # label-only tiers (e.g. Gunpowder)
    _its = [k for k, v in ITEM_TIER_DISPLAY.items() if v == _lbl]
    _req = sorted({r for k in _its for src in (WEAPONS, RANGED, SHIELDS, ARMORS) for r in ((src.get(k) or {}).get("requires") or [])})
    if any(k in RANGED for k in _its):                        # ranged items also need the Ranged Weapons unlock
        _req += [n for n, d in NODES.items() if n not in _req and re.search(r"unlocks?\s+ranged weapons",
                 re.sub(r"\*\*", "", (d.get("innate") or "") + " " + (d.get("mastery") or "")).lower())]
    GLOSSARY.setdefault(_lbl, f"{_lbl} equipment: {', '.join(_its)}." + (f" Unlocked by: {', '.join(_req)}." if _req else ""))
GLOSSARY.setdefault("Ranged Weapons", "Ranged weapons: " + ", ".join(
    f"{k} ({display_tier(v.get('tier'), k)})" for k, v in RANGED.items()) + "."
    + (lambda u: f" Unlocked by: {', '.join(u)}." if u else "")(
        [n for n, d in NODES.items() if re.search(r"unlocks?\s+ranged weapons", re.sub(r"\*\*", "", (d.get("innate") or "") + " " + (d.get("mastery") or "")).lower())]))


# ── Rest Phase gains (turn strip / Table End turn) ─────────────────────────────────────────────
RENOWN_MAX = 30              # Renown stops here; the game continues but no more Renown is gained
RENOWN_PER_TURN = 1          # Rest Phase step 3 "Gain Renown" — the rules don't state an amount; set here
DOMAIN_POINTS_PER_TURN = 1   # Rest Phase step 4 / Key Resources: "Domain Points — earned 1 per turn"
GLOSSARY["Domain Point"] = GLOSSARY["Domain Point"].replace("{DOMAIN_POINTS_PER_TURN}", str(DOMAIN_POINTS_PER_TURN))


# ── SIMPLE overlay ──────────────────────────────────────────────────────────────
# Rules text that changes with the simplified pursuit graph. Runs last so every
# table above exists. Add further SIMPLE-only text overrides here.
if SIMPLE:
    EDICTS["Monument"]["requirement"] = "Have a Monument pursuit."

    # Reference-sheet recommendations (flavour only — CULTURES.monuments, FACTIONS pair/complement)
    # pointed at the SIMPLE Monument set. Legacy keeps its own lists.
    for _cn, _ml in {
        "Trusteki":     ["Office of Works", "Manor House", "Advanced Blast Furnace", "Port Authority"],
        "Kraghs":       ["Royal Pavilion", "Artillery Park", "Ministry of Military Strategy", "Baggage Train"],
        "Ithiss":       ["Thieves' Guild", "Outlaw Rookery", "Whispering Undercroft", "Outrider Intercept Post"],
        "Lenavorites":  ["Papal Palace", "Inquisitorial Palace", "Exalted Basilica"],
        "Belvareth":    ["Preceptory of the Knight's Templar", "Royal Pavilion", "Exalted Basilica"],
        "Vorghith":     ["Outrider Intercept Post", "Baggage Train", "Outlaw Rookery"],
        "Prezish":      ["Aristocratic Court", "Thieves' Guild", "Port Authority"],
        "Shassolin":    ["Senate Hall", "Inquisitorial Palace", "Plague Pit"],
        "Cailendroffs": ["Imperial Palace", "Royal Pavilion", "Preceptory of the Knight's Templar", "Whispering Undercroft"],
        "Sarkopekt":    ["Outrider Intercept Post", "Baggage Train", "Advanced Blast Furnace"],
        "Ossensteins":  ["Office of Works", "Aristocratic Court", "Whispering Undercroft", "Inquisitorial Palace"],
        "Voldrastel":   ["Senate Hall", "Imperial Palace", "Preceptory of the Knight's Templar", "Office of Works"],
        "Madekites":    ["Office of Works", "Papal Palace", "Exalted Basilica", "Port Authority"],
    }.items():
        CULTURES[_cn]["monuments"] = _ml
    # pair = two Monuments the faction plays toward; complement = one more. Monuments only (all 21 in use).
    for _fn, (_pr, _cp) in {
        "The Battering Ram":      ("Artillery Park, Ministry of Military Strategy", "Baggage Train"),
        "The Boundless Steppe":   ("Baggage Train, Royal Pavilion", "Outrider Intercept Post"),
        "The Bandit King":        ("Outlaw Rookery, Thieves' Guild", "Outrider Intercept Post"),
        "The Crowned Star":       ("Aristocratic Court, Senate Hall", "Imperial Palace"),
        "The Crimson Tide":       ("Port Authority, Thieves' Guild", "Outrider Intercept Post"),
        "The Entwined Crown":     ("Senate Hall, Aristocratic Court", "Exalted Basilica"),
        "The Eternal Court":      ("Studium Generale, Senate Hall", "Whispering Undercroft"),
        "The Final Word":         ("Imperial Palace, Royal Pavilion", "Ministry of Military Strategy"),
        "The Gilded Crescent":    ("Manor House, Port Authority", "Office of Works"),
        "The Gilded Path":        ("Port Authority, Aristocratic Court", "Thieves' Guild"),
        "The Hermit Crown":       ("Studium Generale, Whispering Undercroft", "Manor House"),
        "The Illuminated Order":  ("Studium Generale, Office of Works", "Senate Hall"),
        "The Iron Faith":         ("Office of Works, Preceptory of the Knight's Templar", "Papal Palace"),
        "The Iron Shore":         ("Baggage Train, Advanced Blast Furnace", "Royal Pavilion"),
        "The Iron Throne":        ("Office of Works, Papal Palace", "Senate Hall"),
        "The Merchant Republics": ("Port Authority, Thieves' Guild", "Aristocratic Court"),
        "The Sacred Throne":      ("Papal Palace, Exalted Basilica", "Inquisitorial Palace"),
        "The Tunnellers":         ("Advanced Blast Furnace, Office of Works", "Artillery Park"),
        "The Undying Flame":      ("Preceptory of the Knight's Templar, Exalted Basilica", "Royal Pavilion"),
        "The Verdant Kingdom":    ("Port Authority, Manor House", "Advanced Blast Furnace"),
        "The Winter Wolves":      ("Baggage Train, Artillery Park", "Imperial Palace"),
        "The Ancient Wilds":      ("Outrider Intercept Post, Ministry of Military Strategy", "Baggage Train"),
        "The Bloodied Cross":     ("Preceptory of the Knight's Templar, Inquisitorial Palace", "Royal Pavilion"),
        "The Blazing Standard":   ("Royal Pavilion, Imperial Palace", "Exalted Basilica"),
        "The Inner Circle":       ("Senate Hall, Studium Generale", "Aristocratic Court"),
        "The Luminous Court":     ("Exalted Basilica, Office of Works", "Studium Generale"),
        "The Grand Compact":      ("Port Authority, Senate Hall", "Manor House"),
        "The Pale Throne":        ("Plague Pit, Royal Pavilion", "Inquisitorial Palace"),
        "The Sublime Gate":       ("Advanced Blast Furnace, Artillery Park", "Port Authority"),
        "The Velvet Hand":        ("Aristocratic Court, Senate Hall", "Exalted Basilica"),
        "The Ashen Vale":         ("Plague Pit, Inquisitorial Palace", "Outlaw Rookery"),
        "The Broken Banner":      ("Aristocratic Court, Manor House", "Baggage Train"),
        "The Forked Tongue":      ("Whispering Undercroft, Thieves' Guild", "Senate Hall"),
        "The Hall of Masks":      ("Whispering Undercroft, Studium Generale", "Outrider Intercept Post"),
        "The Smoldering Crown":   ("Thieves' Guild, Plague Pit", "Imperial Palace"),
        "The Squatters' Crown":   ("Artillery Park, Baggage Train", "Office of Works"),
        "The Wandering Crown":    ("Outrider Intercept Post, Artillery Park", "Advanced Blast Furnace"),
        "The Dukedom":            ("Senate Hall, Imperial Palace", "Aristocratic Court"),
        "The Elder Grove":        ("Ministry of Military Strategy, Outrider Intercept Post", "Inquisitorial Palace"),
        "The Yew Heart":          ("Royal Pavilion, Ministry of Military Strategy", "Outrider Intercept Post"),
    }.items():
        FACTIONS[_fn]["pair"] = _pr
        if _cp: FACTIONS[_fn]["complement"] = _cp

    GLOSSARY["Root"] = (f"A Holding with no {CHAIN_TERM} requirement: you may start it without controlling a parent. "
                         f"If it is Efficient with a Holding, it may still share that Holding's Settlement Ward.")
    # Holding upkeep / Build Timer follow Standing (HOLDING_TIER_COST), not type.
    UPKEEP_TRACKS["Pursuit"] = f"Each Empire Phase: {_HOLDING_COST_TEXT}."
    COSTS["Pursuit upkeep"] = f"Each Empire Phase: {_HOLDING_COST_TEXT}"
    GLOSSARY["Upkeep"] = GLOSSARY["Upkeep"].replace(f"fixed by type ({_PU_TEXT})", _HOLDING_COST_TEXT)
    ACTIONS["Pursue"]["notes"] = [n for n in ACTIONS["Pursue"]["notes"] if not n.startswith("Power and unique")] + [
        "Build Timer by Standing: Untested " + str(_HTC[None][1]) + ", "
        + ", ".join(f"{t} {_HTC[t][1]}" for t in _STANDINGS) + "."]

    # Faction starters: no Mastery to keep active.
    for _f in FACTIONS.values():
        _m = _f.get("mechanic", "")
        _m = _m.replace(", always-active Mastery that can't be deactivated)", ")")
        _m = _m.replace(", always-active Mastery)", ")")
        _m = _m.replace(" (and their Mastery Effects, if active)", "")
        _m = _m.replace("(no Ward, no upkeep", "(no Ward, Natural")   # faction pursuits are Natural
        _f["mechanic"] = _m

    # Text that pointed at a node's Mastery.
    WEAPONS["Cavalry Spear"]["note"] = WEAPONS["Cavalry Spear"]["note"].replace("Needs Stable Mastery", "Needs Stable")
    WEAPONS["Lance"]["note"] = WEAPONS["Lance"]["note"].replace("Needs Saddlery Mastery", "Needs Saddlery")
    GLOSSARY["Dual-equip"] = "Carry two weapons at once (e.g. melee + ranged). Granted by the Tiltyard."
    UPKEEP_TRACKS["Infrastructure"] = UPKEEP_TRACKS["Infrastructure"].replace(
        "Trade Guild removes Primitive (innate) + Developed (mastery)", "Masonry removes Primitive; Trade Guild removes Developed")
    COSTS["Infrastructure upkeep"] = COSTS["Infrastructure upkeep"].replace(
        "Trade Guild removes Primitive/Developed", "Masonry removes Primitive, Trade Guild removes Developed")
    SIEGE_SOURCE_VALUES["Citadel"] = {"innate_value": 3}      # SIMPLE Citadel: Siege Timer +3
    ACTIONS["Pursue"]["effect"] = ACTIONS["Pursue"]["effect"].replace(
        "its innate effect activates immediately, and its mastery effect activates if all mastery requirements are met.",
        "its effect activates immediately.")

    # Mastery Chain = unlock + free ride (rulings): you may start a Pursuit only while you control one complete
    # line of its chain back to the root, anywhere in your empire (checked only when you start it — carve-out
    # wording pending); sharing a Ward with the immediate parent is the free Ward. A parent lost later just
    # loses its own effect.
    # Actions: Pursue -> Build (Pursuits); Build -> Improve (Infrastructure + Expand); Charter = new Settlement only.
    _old = dict(ACTIONS)
    _pursue = dict(_old["Pursue"]); _infra = dict(_old["Build"]); _charter = dict(_old["Charter"])
    _pursue["effect"] = _pursue["effect"].replace(
        "choose a Pursuit whose prerequisites you meet",
        "choose a Pursuit with one complete line of its " + CHAIN_TERM + " under your control (and meet its other requirements)")
    _improve = dict(_infra)
    _improve["effect"] = ("Choose one: Infrastructure — choose an unlocked, available Infrastructure and set a Build Timer "
        "equal to its build time; when it completes, the Infrastructure becomes active in every Settlement in your Province. "
        "Or Expand a Settlement one tier" + (" into an adjacent Territory" if WARD_MODEL == "range1" else "") + " (Village to Town, Town to City, "
        "City to Metropolis), adding a Ward.")
    _improve["notes"] = [n.replace("when the Build action is performed", "when the Improve action is performed")
                         for n in _infra.get("notes", [])] + list(_charter.get("notes", []))
    _charter["effect"] = ("Charter a new Village — on in-province non-water, non-mountain Territory, "
        "Range 4+ from any Settlement and Range 2+ from Outlaw Country.")
    _charter.pop("notes", None)
    ACTIONS.clear()
    for _k, _v in _old.items():
        if _k == "Build":     ACTIONS["Improve"] = _improve
        elif _k == "Pursue":  ACTIONS["Build"] = _pursue
        elif _k == "Charter": ACTIONS["Charter"] = _charter
        else:                 ACTIONS[_k] = _v
    if "Improve" not in ACTIONS: ACTIONS["Improve"] = _improve
    if "Pursue action" in COSTS:
        _cs = dict(COSTS); COSTS.clear()
        for _k, _v in _cs.items(): COSTS["Build action" if _k == "Pursue action" else _k] = _v
    _action_costs()
    for _c in CULTURES.values():
        if "actions" in _c:
            _c["actions"] = [{"Build": "Improve", "Pursue": "Build"}.get(a, a) for a in _c["actions"]]

    # Glossary: action names + Efficient -> CHAIN_TERM (rulings: unlock anywhere, checked at start; same Settlement = free Ward)
    _g = dict(GLOSSARY); GLOSSARY.clear()
    for _k, _v in _g.items():
        if _k == "Pursue":        GLOSSARY["Build"] = "Build a Pursuit, spending its purchase cost and a Settlement ward (Industry action)."
        elif _k == "Build":       GLOSSARY["Improve"] = "Construct Infrastructure or Expand a Settlement one tier (Industry action)."
        elif _k == "Charter":     GLOSSARY["Charter"] = "Found a new Settlement (Industry action)."
        elif _k == "Efficient X": GLOSSARY[CHAIN_TERM + " X"] = (
            "While this Pursuit occupies the same Settlement Ward as X (the Raw Material or Pursuit named on its tile), "
            "it uses no ward of its own — the two share one ward. Placed anywhere else, it fills a ward normally. "
            "(Core Principle 13.) Note: Two Pursuits that chain from the same Pursuit cannot share a Ward with each other.")
        elif _k == "Efficient":   GLOSSARY[CHAIN_TERM] = (
            "A Pursuit's " + CHAIN_TERM + " is the line of Pursuits it builds from, usually running from a Raw Material "
            "up to a Monument. You may start building a Pursuit only while you control one complete line of its "
            + CHAIN_TERM + ", anywhere in your empire; this is checked only when you start it. A Pursuit placed in the "
            "same Settlement Ward as its immediate parent shares that Ward, and the chain can continue upward the same way. "
            "Each Pursuit carries at most one descendant in its Ward. (Core Principle 13.)")
        else:                     GLOSSARY[_k] = _v

    # No sea variants: water access comes from Fishmongery (fish within Reach) and its Mastery Chain.
    for _sv in SETTLEMENTS.values(): _sv["sea_variant"] = None
    FACTIONS["The Crimson Tide"]["mechanic"] = FACTIONS["The Crimson Tide"]["mechanic"].replace(
        " — even without a Water Settlement", "")

    # Expand lives in Improve now: upgrade grants follow it.
    for _st in ("Established", "Sovereign"):
        DOMAIN_BOARD["Industry"][_st] = DOMAIN_BOARD["Industry"][_st].replace(
            "Perform endorsed Charter.", "Perform endorsed Improve.").replace(
            "may be chartered to a Metropolis", "may be improved to a Metropolis")
    ERAS["Ascension"]["unlocks"] = ERAS["Ascension"]["unlocks"].replace("May resolve Charter Cities", "May Improve Towns to Cities")
    EDICTS["Wonder"] = {**EDICTS["Wonder"], "type": "Improve", "requirement": "Improve Infrastructure via a Wonder."}

    # ── DRAFTS — finish the wording, then uncomment ─────────────────────────
    # Rules prose for SIMPLE lives in RULES_push_simple.md (build_all_CE.bat picks it when SIMPLE=1).
    #
    # Reach also gates Raw Materials (stated rule; board flags it). Draft glossary wording:
    # GLOSSARY["Reach"] = GLOSSARY["Reach"] + " You can only build a Raw Material whose resource lies within your Reach."
    #
    # TODO (Gage): add "Reach +1" to a couple of thin nodes. Candidates from past data:
    #   Interrogation Chambers — innate was empty through Combatv3 (CE now: Extort 500).
    #   Charcoal Burner, Mill, Kiln — legacy innate is "Natural" only.
    #   (Abbey had no empty slot in any version checked.) Board Reach overlay reads "Reach +N"
    #   from active pieces automatically.
    #
    # Eureka (Public Order 5). Note: Piety's action cost is Doubt 1, not gold.
    # PUBLIC_ORDER[5] = ("Eureka", "Once per turn, when you perform an action, you may Recoup its cost.")
    #
    # Fall / Harvest: Husbandry Mastery -> Natural. Natural Pursuits now carry their
    # whole effect (old innate + mastery), so this doubles more than before.
    # SEASONS["Fall"]["effect"] = "Natural Pursuit effects are doubled."
    #

    # ── Pursuit -> PURSUIT_TERM (runs last). Rewrites player-facing string VALUES in the rules tables
    # (dict keys stay: BUILD_TIMERS / COSTS / UPKEEP_TRACKS ids) and adds display aliases so literals in
    # the wiki, compendium, rules docx and PDFs follow (display_html / display_md / display_pdf).
    import re as _re_pt
    _PS, _PP = PURSUIT_TERM
    _PT_SUBS = [(_re_pt.compile(r"\bPursuits\b"), _PP), (_re_pt.compile(r"\bPursuit\b"), _PS),
                (_re_pt.compile(r"(?<![/\w.#-])pursuits(?![\w/#-]|\.\w)"), _PP.lower()),
                (_re_pt.compile(r"(?<![/\w.#-])pursuit(?![\w/#-]|\.\w)"), _PS.lower())]
    def _pt(o):
        if isinstance(o, str):
            for _rx, _to in _PT_SUBS: o = _rx.sub(_to, o)
            return o
        if isinstance(o, dict):
            for _k in list(o): o[_k] = _pt(o[_k])
            return o
        if isinstance(o, list):
            o[:] = [_pt(x) for x in o]; return o
        if isinstance(o, tuple):
            return tuple(_pt(x) for x in o)
        return o
    for _name in [n for n in list(globals()) if n.isupper() and n not in ("LEGACY_NODES",)]:
        _v = globals()[_name]
        if isinstance(_v, (dict, list, tuple)) and _name not in ("NAME_DISPLAY", "TIER_DISPLAY", "ALIASES"):
            globals()[_name] = _pt(_v)
    NAME_DISPLAY.update({"Pursuit": _PS, "Pursuits": _PP, "PURSUIT": _PS.upper(), "PURSUITS": _PP.upper()})
    ALIASES.update({"Pursuit": _PS, "Pursuits": _PP, "PURSUIT": _PS.upper(), "PURSUITS": _PP.upper()})
    _ALIAS_RE = _re_disp.compile(
        r"\b(" + "|".join(_re_disp.escape(k) for k in sorted(ALIASES, key=len, reverse=True)) + r")\b")

# ── Faction names: a faction is named by FACTIONS[k]['mechanic_name'] ("The Decider"); the dict key (the AI name)
# stays the engine id (saved games, CULTURES, pairings). Display layer only: NAME_DISPLAY / ALIASES.
# FACTIONS[k]['summary'] is the one-line gist (reference sheets, board selector); 'mechanic' stays the binding text.
FACTION_NAMES = {k: v["mechanic_name"] for k, v in FACTIONS.items() if v.get("mechanic_name")}
_FN_TXT = repr([NODES, FACTIONS, MOVEMENT_MODIFIERS, INFRASTRUCTURE, WONDERS, GLOSSARY, ACTIONS])
for _k, _v in list(FACTION_NAMES.items()):
    NAME_DISPLAY[_k] = _v; ALIASES[_k] = _v
    if _k.startswith("The ") and _re_disp.search(r"(?<!The )\b" + _re_disp.escape(_k[4:]) + r"\b", _FN_TXT):
        ALIASES[_k[4:]] = _v                                   # bare form where the data uses it ("Ancient Wilds")
# ── Faction -> FACTION_TERM: what players read for "Faction" (cards, rules, wiki, board). Engine ids stay
# (FACTIONS, CULTURES[*]['factions'], board state 'faction', {{TABLE:factions}}); display layer only.
FACTION_TERM = ("Heritage", "Heritages")
if FACTION_TERM[0] != "Faction":
    _FS, _FP = FACTION_TERM
    for _k, _v in {"Faction": _FS, "Factions": _FP, "faction": _FS.lower(), "factions": _FP.lower(),
                   "FACTION": _FS.upper(), "FACTIONS": _FP.upper()}.items():
        NAME_DISPLAY[_k] = _v; ALIASES[_k] = _v
def faction_body(k):
    """A faction's mechanic text (its title is FACTIONS[k]['mechanic_name'], the faction's displayed name)."""
    return str(FACTIONS.get(k, {}).get("mechanic", ""))
_ALIAS_RE = _re_disp.compile(
    r"\b(" + "|".join(_re_disp.escape(k) for k in sorted(ALIASES, key=len, reverse=True)) + r")\b")

# ── Glossary categories: one ordering shared by the rules docx ({{GLOSSARY:Category}}), wiki and board ──
# Constant-keyed terms use their constants; action names follow SIMPLE (Pursue->Build, Build->Improve).
GLOSSARY_CATEGORIES = [
    ('Reading the Rules', ['Perform', 'Resolve', 'Cost / Pay', 'Fail', 'Natural roll', PIVOTAL, 'Host']),
    ('Council & Envoys', ['Influence', 'Authority X', 'Envoy', 'Send an Envoy', 'Personal Envoy', 'Council Phase', 'Council Envoy', 'Vote', 'Support X', 'Oppose X', 'Abstain', 'Net Influence', 'Envoy Outcome', 'Condemned', 'Failed', 'Passed', 'Endorsed']),
    ('Domains & Scoring', ['Renown', 'Domain', 'Domain Point', 'Standing', 'Edict', 'Monument']),
    ('Actions', ['Charter', 'Muster', *(["Build"] if SIMPLE else ["Pursue"]), *(["Improve"] if SIMPLE else ["Build"]), 'Repair', 'Move', 'Demand Tribute', 'Diplomacy']),
    ('Treaties', ['Treaty', 'Alliance', 'At War', 'Vassal', 'Suzerain']),
    ('Economy & Public Order', ['Public Order', 'Faith X', 'Doubt X', 'Extort X', 'Recoup X', 'Upkeep', 'Craft', 'Can Trade', 'War Weariness']),
    ('Settlements & Holdings', ['Settlement Ward', 'Pursuit', *(["Root"] if SIMPLE else []), 'Natural', CHAIN_TERM, CHAIN_TERM + " X"]),
    ('Timers', list(TIMERS)),
    ('Map & Range', ['Realm', 'Region', 'Territory', 'Province', 'Border', 'Controlled', 'Contested', 'Uncontested', 'Uncontrolled', 'Range X', 'Within', 'Adjacent', 'Next to', 'Reach', 'Reach X']),
    ('World', ['Bandit', 'Outlaw Country', 'Wild Outlaw Country', 'Siege', 'Sally Forth']),
    ('Army States', ['Retinue', 'Speed X', 'Presence', 'Blocked', 'Strained']),
    ('Battle Structure', ['Battle', 'Skirmish', 'Attacker / Defender', 'Seize the Initiative', 'Tactic', 'Field', 'Casualty', 'Initiative', BLUNDER, 'Strike', 'to-Strike number', 'AP', 'Save', 'Endurance', 'Fatigued', FATIGUE_TOKEN, 'Morale', 'Break check', 'Panic check', 'Rout', 'Fall Back']),
    ('Combat Keywords — Defense', [PARRY, RIPOSTE, RECOVER, ENDURING, NO_PARRY, MINUS_1_TBH, PLANISHING]),
    ('Combat Keywords — Offense', [SHATTER_ARMOR, CLEAVE, POISON, DESTROY_SHIELD, UNSTOPPABLE, SERRATED]),
    ('Combat Keywords — Handling', ['Equipped', STEADY, UNWIELDY, NIMBLE, DRILLED, TWO_H, DUAL_WIELD, 'Dual-equip', ONE_SHOT]),
    ('Combat Keywords — Immune / Negate', ['Immune [keyword]', 'Negate [keyword]']),
    ('Equipment Tiers', [k for k in map(str, GLOSSARY) if k.split()[0] in {display_tier(x) for x in TIERS} | set(globals().get("ITEM_TIER_DISPLAY", {}).values()) or k == "Ranged Weapons"]),
]

# ── GLOSSARY_SEE: glossary terms whose full rule lives in the rules prose ──
# The rules-doc / wiki glossary tables print the term's first sentence + "See <rule> (<section>)" instead of
# repeating the rule; GLOSSARY keeps the full text for cards, board tooltips and {{TERM:}}/{{DEF:}}.
# Value = anchor id: a {{RULE:id}} marker in the rules md, or a heading slug ("council-phase").
# A (short text, anchor) tuple overrides the first-sentence default. Checked by
# `rule_numbers.py <rules.md> --check` and gen_settlement_board --check-rules. The {{RULE:}} anchors live in
# RULES_push_simple.md only, so the legacy (SIMPLE=0) build keeps full glossary definitions.
GLOSSARY_SEE = {} if not SIMPLE else {
    'Host': 'host',
    'Influence': 'influence', 'Envoy': 'sending-an-envoy', 'Send an Envoy': 'sending-an-envoy',
    'Council Phase': 'council-phase', 'Council Envoy': 'council-envoy',
    'Vote': 'vote', 'Support X': 'vote', 'Oppose X': 'vote', 'Abstain': 'vote',
    **{t: 'envoy-resolution-table' for t in ('Net Influence', 'Envoy Outcome', 'Condemned', 'Failed', 'Passed', 'Endorsed')},
    'Renown': 'renown-track', 'Domain': 'domain-standings', 'Domain Point': 'domain-standings',
    'Standing': 'domain-standings', 'Edict': 'how-to-win-edicts',
    'Charter': 'industry-actions', ("Build" if SIMPLE else "Pursue"): 'industry-actions',
    ("Improve" if SIMPLE else "Build"): 'industry-actions', 'Repair': 'industry-actions',
    'Muster': 'prowess-actions', 'Move': 'prowess-actions', 'Demand Tribute': 'prowess-actions',
    'Diplomacy': 'diplomacy-actions',
    'Treaty': 'treaties-alliances', 'Alliance': 'treaties-alliances', 'Vassal': 'vassalization', 'Suzerain': 'vassalization',
    'Public Order': 'public-order', 'Faith X': 'public-order', 'Doubt X': 'public-order',
    'Upkeep': 'treasury-upkeep', 'Craft': 'who-can-trade', 'Can Trade': 'who-can-trade',
    'War Weariness': 'innate-public-order-modifiers',
    'Settlement Ward': 'settlement-wards', CHAIN_TERM: 'mastery-chain', CHAIN_TERM + " X": 'mastery-chain',
    **({'Root': 'root'} if SIMPLE else {}),
    **{t: 'timers' for t in TIMERS},
    **{t: 'territory-terrain' for t in ('Territory', 'Province', 'Border', 'Controlled', 'Contested', 'Uncontested',
                                         'Uncontrolled', 'Range X', 'Within', 'Adjacent', 'Next to')},
    'Reach': 'settlement-reach', 'Reach X': 'settlement-reach',
    'Bandit': 'bandits', 'Outlaw Country': 'outlaw-country', 'Wild Outlaw Country': 'outlaw-country', 'Siege': 'siege-warfare',
    'Speed X': 'speed', 'Presence': 'rule-presence', 'Blocked': 'blocked-armies',
    'Skirmish': 'the-skirmish-steps', 'Seize the Initiative': 'seize', 'Tactic': 'tactic-matrix', 'Field': 'form-line',
    'Initiative': 'initiative', BLUNDER: 'initiative', 'Strike': 'strike', 'to-Strike number': 'strike',
    'Save': 'defend', 'Panic check': 'panic', 'Endurance': 'fatigue', 'Fatigued': 'fatigue', FATIGUE_TOKEN: 'fatigue',
    'Break check': 'fatigue', 'Rout': 'end-skirmish',
}

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# HOLDING_SIM — Holding semantics for the combat sim, read from SIMPLE_NODES (replaces the retired
# legacy NODES[*]['engine'] field). One text parser shared with the settlement board, so the board
# and the tournament can never read a Holding differently.
#   tags     combat / unlock tokens parsed from 'innate' (holding_combat_tags, sim=True)
#   domain   Standing requirement parsed from 'unlock' ({"Industry": 3}; "*" = any Domain, ruling Oct 19 2026)
#   parents  Mastery Chain parents ('efficient'); a Holding needs one complete line unless 'root'
#   upkeep   Army-upkeep reductions parsed from 'innate' ("Upkeep -N"); conditional clauses count
#            at COND_UPKEEP_FACTOR (the sim has no map — ruling Oct 19 2026)
# ═══════════════════════════════════════════════════════════════════════════════════════════════
COND_UPKEEP_FACTOR = 0.5
_HT_TIER = r"(Crude|Cast|Wrought|Forged|Crafted)"
_HT_RET_NORM = {"Sergeants": "Sergeant", "Knight's Templar": "Knight Templar",
                "Knights Templar": "Knight Templar", "Man at Arms": "Man-at-Arms"}

def _ht_strip(s):
    s = str(s or "").replace("−", "-")
    s = _re_disp.sub(r"\*\*|\*|__", "", s)
    return s.replace("’", "'").strip()

def holding_combat_tags(text, sim=False):
    """Combat / unlock tokens a Holding's text grants (settlement board + combat sim).
    sim=True adds the sim-only tokens the board doesn't act on (tactic reveal, Tiltyard equip rules)."""
    t, out = _ht_strip(text), []
    _I = _re_disp.I
    # unlocks
    if _re_disp.search(r"Unlocks?\s+Ranged\s+Weapons", t, _I): out.append("ranged")
    if _re_disp.search(r"Unlocks?\s+Cavalry\s+Weapons", t, _I): out.append("cavalry")
    for wm in _re_disp.finditer(r"Unlocks?\s+(Cavalry Spear|Lance)\b", t, _I):
        out.append("weapon:" + wm.group(1).title())
    m = _re_disp.search(r"Unlocks?\s+(.+?)\s+for\s+Muster", t, _I)
    if m:
        r = m.group(1).strip()
        out.append("retinue:" + _HT_RET_NORM.get(r, r))
    # gear tiers
    for m in _re_disp.finditer(_HT_TIER + r"\s+armor\s*(?:and|&)\s*shields?", t, _I):
        x = m.group(1).title(); out += ["armor:" + x, "shield:" + x]
    for m in _re_disp.finditer(r"(?:Unlocks?\s+)?" + _HT_TIER + r"(?:\s+Tier)?\s+Weapons", t, _I):
        if _re_disp.search(r"unlock", t[m.start():m.end() + 12], _I): out.append("tier:" + m.group(1).title())
    if _re_disp.search(r"(?<![A-Za-z] )unlocks?\s+Shields\b", t, _I): out.append("tier:Shields")
    # combat keywords
    for pat, tok in ((r"\bPlanishing\b", "Planishing"), (r"\bSerrated\b", "Serrated"), (r"gain\s+Poison", "Poison"),
                     (r"gain\s+Riposte", "Riposte"), (r"\bNimble\b", "Nimble"), (r"\bEnduring\b", "Enduring"),
                     (r"\bDrilled\b", "Drilled"), (r"(?<!Settlements gain )Immune Strained(?! during)", "Immune Strain"),
                     (r"\+1 to Strike", "Strike +1"), (r"max initiative is increased to 3", "MaxInit3"),
                     (r"Always gains Seize the Initiative", "Seize: first"), (r"Righteous Fervour", "Righteous Fervour"),
                     (r"Unlocks Arquebus", "Artillery Park")):
        if _re_disp.search(pat, t, _I): out.append(tok)
    out += ["Parry +1"] * len(_re_disp.findall(r"Improve Parry by \+1", t, _I))
    m = _re_disp.search(r"Focused Strikes on a natural (\d+)\+", t, _I)
    if m: out.append("Crit " + m.group(1))
    m = _re_disp.search(r"Gain Recover (\d+)", t, _I)
    if m: out.append("Recover " + m.group(1))            # base; its "or improve" alternative is not a second grant
    else: out += ["Recover +1"] * len(_re_disp.findall(r"(?:Improve Recover by|Recover improved by)\s*\+1", t, _I))
    if sim:
        if _re_disp.search(r"Every Skirmish, you may force your opponent to reveal", t, _I): out.append("Outrider: every")
        elif _re_disp.search(r"First Skirmish, you may force your opponent to reveal", t, _I): out.append("Outrider: first")
        if _re_disp.search(r"equipped with a Ranged and a Melee Weapon simultaneously", t, _I): out.append("dual-equip")
        if _re_disp.search(r"two of the same 1H Melee Weapon to gain Dual Wield", t, _I): out.append("two-of-same")
    return out

def holding_upkeep(text):
    """Army-upkeep reductions in a Holding's text: [{"amount": N, "factor": f}] or [{"all": True, "factor": f}]."""
    out = []
    for c in _re_disp.split(r";|\.\s+|\.$", _ht_strip(text)):
        cond = bool(_re_disp.search(r"\b(while|if|when)\b", c, _re_disp.I))
        f = COND_UPKEEP_FACTOR if cond else 1.0
        if _re_disp.search(r"\bdo(?:es)? not pay Upkeep\b|\bdon't pay Upkeep\b", c, _re_disp.I):
            out.append({"all": True, "factor": f}); continue
        m = _re_disp.search(r"(?<!No )\bUpkeep\s*-\s*(\d+)", c, _re_disp.I)
        if m:
            out.append({"amount": int(m.group(1)), "factor": f})
    return out

def holding_domain(unlock):
    """'Rising Industry' -> {"Industry": 3}; 'Sovereign Piety + Established Prowess' -> both;
    '1 Rising' / '4 Established' -> {"*": [(threshold, count)]} (any Domain(s))."""
    out = {}
    for part in str(unlock or "").split("+"):
        part = part.strip()
        m = _re_disp.match(r"(Rising|Established|Sovereign)\s+(Industry|Prowess|Cunning|Piety)$", part)
        if m:
            d, v = m.group(2), STANDING_THRESHOLDS[m.group(1)]
            out[d] = max(out.get(d, 0), v); continue
        m = _re_disp.match(r"(\d+)\s+(?:Domains?\s+at\s+)?(Rising|Established|Sovereign)$", part)
        if m:
            out.setdefault("*", []).append((STANDING_THRESHOLDS[m.group(2)], int(m.group(1))))
    return out

def _ht_parents(v):
    e = v.get("efficient") or []
    return [e] if isinstance(e, str) else list(e)

HOLDING_SIM = {
    name: {"tags": holding_combat_tags(v.get("innate", ""), sim=True),
           "domain": holding_domain(v.get("unlock", "")),
           "parents": _ht_parents(v),
           "root": bool(v.get("root")),
           "monument": bool(v.get("monument")) or v.get("scope") == "Realm",
           "upkeep": holding_upkeep(v.get("innate", ""))}
    for name, v in SIMPLE_NODES.items()
}
