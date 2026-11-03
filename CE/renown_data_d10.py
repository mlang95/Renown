# renown_data — single source of truth (CSV/0.4.8 branch, card-verified)
# Edit THIS file; equipment.csv, cards, and docs are generated from it.
import os as _os
# SIMPLE-only. One-stage Holdings, Mastery Chain placement, the Build / Improve actions. Every value below is what
# the game uses; there is no overlay that rewrites it later. The legacy (SIMPLE=0) data is frozen in
# renown_data_d10_legacy.py. SIMPLE stays defined (always True) because the build scripts read it.
SIMPLE = True
# build_all_CE.bat: set PHASES=1|0. On: no Council vote: the Council Phase is the Works Phase (each player performs the Era's
# Industry actions, no Envoy); in Spring the Envoy Phase is the Diplomacy Phase (offers between players; no Envoys), the only one
PHASE_REFORM = _os.environ.get("RENOWN_PHASES", "1") == "1"
vS = "-S"
VERSION = f"0.4.9.9.15-d10{vS}{PHASE_REFORM}"
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
SACK_EXTORT_PER_TIER = 4000
INTERCEPT_EXTORT_PER_CRAFT = 100   # Intercept Caravan: Extort this x target's Craft when they have no Trade Income
WEALTH_EDICT_GOLD    = 50000
MUSTER_RANGE         = 2
MARCH_MULTIPLIER     = 2
PO_MIN               = -10
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
# Standing rank: one number per Standing. Your Envoys in a Domain start at Authority = your rank there, and you may
# Support / Oppose up to your rank on each vote in that Domain (DOMAIN_BOARD's two Influence rows are built from it).
STANDING_RANK = {"Untested": 1, "Rising": 2, "Established": 3, "Sovereign": 4}

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
STRAIN          = "Strained"
MINUS_1_TBH     = "Shielded"
PLANISHING      = "Planishing"
FATIGUE_TOKEN   = "Fatigue Token"
CRUSADER        = "Righteous Fervour"
# Exposed X (player effect): other players may aim an EXPOSED_DOMAIN Envoy at you when it is declared; it gains Authority
# +X and, if it Passes or is Endorsed, its action must target you. Stacks: every Exposed X you have adds its X.
EXPOSED         = "Exposed"
EXPOSED_DOMAIN  = "Cunning"

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
FLORENTINE         = "Florentine"  # Two of the same 1H Melee Weapon gain Dual Wield; grants Parry while Dual Wielding (List Yard).
PIVOTAL = "Focused"


GLOSSARY = {
    STEADY:         "Initiative cannot be reduced by Tactics.",
    UNWIELDY:       "Initiative cannot be improved by Tactics.",
    TWO_H:          "Cannot use a Shield: while a 2H weapon is Equipped, your Shield gives nothing that Skirmish (no Save bonus, Initiative or keywords).",
    SHATTER_ARMOR:  f"On a {PIVOTAL} Strike: that Strike's AP is increased by {DEADLY_AP}, and the defender may Parry or {RECOVER} only with a {PIVOTAL} roll.",
    UNSTOPPABLE:    f"-{UNSTOPPABLE_MOD} to the defender's Parry roll (to a maximum of {CAP_THR}+); a Parry against it can't Riposte.",
    CLEAVE:         f"On a {PIVOTAL} Strike: roll one extra Strike die at your modified to-Strike; a {PIVOTAL} extra die Strikes and rolls another.",
    POISON:         f"When the Defender receives a Strike and rolls a {PIVOTAL} Save, it fails; the resulting wound may only be {RECOVER}ed with a {PIVOTAL} {RECOVER}.",
    NIMBLE:         "Gain Initiative +1 in the first Skirmish of each Battle.",
    DRILLED:        "Does not lose Endurance in the first Skirmish of each Battle.",
    DESTROY_SHIELD: f"On a {PIVOTAL} Strike: the target loses its Shield attributes for the rest of the Battle.",
    BLUNDER:        f"At Initiative {INITIATIVE_MIN}, your to-Strike is set to {BLUNDER_THR}+ (penalties can't make it worse).",
    ONE_SHOT:       "Must be Equipped in the first Skirmish of a Battle, and can't be Equipped after it. Requires a Skirmish Field.",
    #DEFLECT:        "-1 to Parry and Negate Riposte against this weapon's Strikes. (All Ranged weapons have Deflect.)",
    #IMMUNE_PANIC:   "Automatically passes Panic checks.",
    #UNBREAKABLE:    "Immune Break: does not take Break checks while Fatigued.",
    PARRY:          f"If your Army has gained {PARRY}, roll a D{FACES} to attempt to Parry a Strike before an Armor Save. On an {PARRY_BASE}+ (better with Improve Parry), the Strike is Parried and has no further effect.",
    RIPOSTE:        f"If your Army has gained {RIPOSTE} and rolls a Focused Parry against a Melee Weapon's Strike, you Riposte: your opponent immediately takes a Strike from your melee weapon. You can Riposte a Riposte.",
    NO_PARRY:       "While Equipped with this weapon during a Skirmish, you cannot Parry, and so cannot Riposte.",
    RECOVER:        f"If your Army has gained {RECOVER} and a to-Save roll fails, roll a D{FACES} & compare it to your Recover value: a result greater than or equal to your Recover value recovers the Retinue. Recovered Strikes still count toward the Panic check threshold.",
    ENDURING:       "Successfully Recovered Strikes don't count toward the Panic check threshold.",
    SERRATED:       f"A cumulative -{SERRATED_MOD} penalty to the defender's Recover roll.",
    PLANISHING:     f"A {PIVOTAL} Save succeeds, regardless of AP.",
    FATIGUE_TOKEN:  f"Each token reduces Morale -{FATIGUE_MORALE} by. If your modified Morale is ever {ROUT_THR}+, your Army Routs. These effects are cumulative.",
    MINUS_1_TBH:    f"A cumulative -1 penalty to the Strike roll (to a maximum of {CAP_THR}+). Sources: a shield's -1 to Strike.",
	#NEGATE_UNSTOPPABLE: "Cancels the attacker's Parry from Unstoppable: this shield's -1 to Strike still applies, and the attacker's -1 to Parry does not.",
    #MINUS_1_PARRY: "A stacking -1 penalty to the defender's Parry roll (to a maximum of 6+). Sources: Unstoppable, Deflect, and each Fatigue token.",
    DUAL_WIELD: "A failed Strike is rerolled once; the rerolled Strike can be Focused. Dual Wield confers Two-Handed. You cannot reroll successful Strikes.",
    FLORENTINE: f"Your Armies may equip two of the same 1H Melee Weapon to gain {DUAL_WIELD}. While Dual Wielding, your Army gains {PARRY}.",
    "Immune [keyword]": "Can't gain that keyword's effect as it applies to your Army (e.g. Immune Strained, Destroy Shield, Steady, etc.).",
    "Negate [keyword]": "Your opponent can't gain that keyword's effect as it applies to their Army (e.g. Negate Shielded).",

    # ── Combat keywords ported from the Escalation Campaign glossary ──
    "AP":            "Armor Penetration — a weapon's (negative) modifier to the defender's Save roll; the more negative, the harder to save.",
    "Blocked":       "The next Move action this Army Performs fails, and then it loses Blocked. (An Army with Immune Blocked never gains it.)",
    "Strained":      "Initiative -1 every Skirmish (negated by Immune Strained). Does not gain Endurance in the Empire Phase.",
    #"Improved Parry": "Your Parry succeeds on 4+ instead of 5+.",
    #"Heal X":        "At the end of each Skirmish, for every X casualties you took from Strikes, return 1 retinue to your Army.",
    "Seize the Initiative": "Initiative +1 in the first Skirmish. The player who performed the Battle action usually has it; Terrain and the Ministry of Military Strategy can change that.",

    # ── Battle-structure terms (doc glossary, wording updated to current rules) ──
    "Attacker / Defender": "The Attacker performed the Move action that caused the Battle or Lay Siege; the other side is the Defender.",
    "Battle":        "A collection of Skirmishes between two players, continuing until a side's Retinue count is reduced to 0, Routs, or successfully Falls Back, ending the Battle.",
    "Skirmish":      "One round of a Battle, run through the numbered Battle steps; a Battle repeats Skirmishes until it ends.",
    "Casualty":      "A Retinue removed from the Field — from an unsaved Strike or a failed Panic or Break check.",
    "Field":         "Your Retinues in play — front line (up to 10) plus reserve (up to 5). Casualties leave the field at once, lowering its count.",
    "Endurance":     "A side's stamina. Each side that fights loses 1 per Skirmish; at 0 it becomes Fatigued.",
    "Fatigued":      f"A side at 0 Endurance. Each Skirmish its Field takes a Break check, then it gains a Fatigue Token.",
    "Break check":   "Taken by each Fatigued side's Field every Skirmish, just before it gains its Fatigue Token. Roll Morale (5 dice, modified by Fatigue Tokens); failures are Casualties, but a Break check never triggers a Panic check. Unbreakable auto-passes.",
    "Panic check":   "Taken at most once per Skirmish by a side that suffered more than 5 Casualties in that Skirmish (Recovered Strikes count, unless Enduring), after both sides have Struck. Roll Morale (5 dice); Immune Panic auto-passes.",
    "Morale":        f"How steady a Retinue is when tested (lower is steadier; see the Retinue table). Break and Panic checks roll it: a D{FACES} per Retinue in the Field, up to 5 dice, each must meet its modified value; failures are Casualties. If the modified value is ever {ROUT_THR}+, the Army Routs.",
    "Rout":          f"The Army breaks and leaves the Battle. Apply Casualties equal to the remaining Retinues. Whenever an Army's modified Morale value reaches {ROUT_THR}+, it Routs automatically.",
    "Fall Back":     "A controlled retreat that ends the Battle with at least one Retinue left — a partial success.",
    "Strike":        f"A landed hit. Roll a D{FACES}, apply modifiers to the roll, and Strike on a Modified roll >= the to-Strike number. The target may then Parry, Save, and Recover.",
    "to-Strike number": f"The D{FACES} result a Retinue needs to Strike (see the Retinue table; lower is better). Bonuses add to the roll; penalties and Fatigue Tokens subtract. It is never worse than {CAP_THR}+.",
    "Save":          f"The defender's roll to avoid a Casualty: roll a D{FACES}, add the weapon's AP (a negative) and the shield's Save bonus (a positive); the hit is saved on a Modified roll >= the armor value.",
    "Unmodified roll": "The number on the die before any modifiers. Modifiers never change what counts as Unmodified.",
    "Modified roll": "The number on the die after every modifier is applied.",
    "Initiative":    f"Decides who Strikes first each Skirmish (higher first). Runs {INITIATIVE_MIN} to +{INITIATIVE_MAX} (only the Ministry of Military Strategy raises the maximum, to +3). At {INITIATIVE_MIN} or lower you Blunder.",
    "Tactic":        "A choice both players make secretly and reveal together each Skirmish; it can shift Initiative, Strike, and Save rolls.",
    "Dual-equip":    "Carry two weapons at once (e.g. melee + ranged). Granted by the Skirmish Field.",
    "Monument":      "A Domain's capstone Holding, one per game. Having one completes the Monument Edict.",

    # ── Empire keywords (referenced by Pursuits/Factions; DRAFTED — review wording) ──
    "Faith X":       "Gain X Faith: each Faith raises your Public Order track by 1 when resolved.",
    "Doubt X":       "Gain X Doubt: each Doubt lowers your Public Order track by 1 when resolved.",
    "Extort X":      "Take X from the stated source: the gold goes to you instead of its owner. One effect resolving is one Extort of the total it takes, however many players or times it names.",
    "Recoup X":      "Undo up to X of the cost you paid (refund gold, or remove Doubt gained).",

    # ── Council, Influence & Envoys (from Rules; the political loop) ──
    "Influence":     "The political currency: spend it to Support or Oppose Envoys. You gain it each Empire Phase from your Era, Trade Partners, Alliances, war, Holdings and Infrastructure. Influence +X gives X tokens in the Empire Phase unless it names another time.",
    "Authority X":   "An automatic change to an Envoy's Authority from a Holding, Infrastructure or Faction, applied while it's sent and resolved (once the action and target are chosen, if it depends on them).",
    "Envoy":         "The currency of actions: send an Envoy to Perform an action during the Envoy Phase. Council Envoys act on the voted Domain; Personal Envoys are sent by Era progression.",
    "Vote":          "On each Envoy, every player except the sender, in clockwise order from the starting player, must Support, Oppose, or Abstain. No talking during a vote.",
    "Support X":     "Spend X Influence to increase an Envoy's Net Influence.",
    "Oppose X":      "Spend X Influence to decrease an Envoy's Net Influence.",
    "Abstain":       "Decline to spend Influence on a Vote.",
    "Council Phase": "Before Personal Envoys, a brief Forum, then all players vote on a Domain with no talking (clockwise; Host breaks ties). Each then sends a free Council Envoy of that Domain. Council Envoys auto-Abstain and their net Influence cannot drop below 1.",
    "Council Envoy": "A free Envoy resolved in the Council Phase on the voted Domain; auto-Abstained, Net Influence floored at 1.",
    "Intrigue Phase": "The Envoy Phase step after the Forum, before the first Vote. No talking: the starting player uses all of their Intrigue Phase effects, then each player clockwise, ending with the Host. Each choice takes effect at once.",
    "Tally Phase": "The Envoy Phase step after every Envoy has been voted on: Supports, then the Votes of players who vote in the Tally Phase, then Endorsements, then effects that send another Envoy (voted at once). Resolve begins when it ends.",
    "Personal Envoy": "An Envoy you send in the Envoy Phase. How many you get, and how many actions each Performs, rise with the Era.",

    # ── Empire actions ──
    "Settle":        "Found a new Village (Industry action).",
    "Expand":        "Raise a Settlement one tier: Village to Town, Town to City, City to Metropolis (Industry action).",
    "Muster":        "Raise a new Army or Reinforce an existing one near a Settlement you Control, while you have a Muster Field; Retinues arrive each Empire Phase over a Muster Timer (Prowess action).",
    "Build":         "Build a Holding, spending its purchase cost and a Settlement Ward (Industry action).",
    "Improve":       "Build Infrastructure, a Wonder included (Industry action).",
    "Repair":        "Restore a Damaged Holding or Infrastructure, or Demolish it (Industry action).",
    "Move":          "Advance an Army up to its Speed in Territories (Prowess action).",
    "Demand Tribute": "Coerce gold or concessions from another player (Prowess action).",

    # ── Diplomacy & alliances ──
    "Diplomacy":     "Free Envoy actions for forming and ending Treaties and Trade Agreements; resolved before Domain Envoys.",
    "Treaty":        "A standing agreement between players (Trade Agreement, Non-Aggression Pact, Alliance), signed in the Diplomacy Phase.",
    "Alliance":      "A Treaty binding players to mutual support; Military and Defensive Alliances unlock by Era.",
    "Vassal":        "A player subordinated via Vassalization: their chartered Settlements return to them, they mirror the Suzerain's Treaties, count as allied to the Suzerain, and cannot Perform or be targeted by Diplomacy actions.",
    "Suzerain":      "The player who has Vassalized another; the Vassal mirrors their Treaties.",

    # ── Empire state ──
    "Domain":        "One of the four Domains: Industry, Prowess, Cunning, Piety. Spend Domain Points to raise its value; the value sets your Standing there.",
    "Domain Point":  "Gain {DOMAIN_POINTS_PER_TURN} each Rest Phase; spend to raise a Domain value by 1.",
    "Public Order":  f"A track from {PO_MIN} to {PO_MAX}, adjusted each turn by Faith minus Doubt; its band applies cumulative effects (see the Public Order table).",
    "Edict":         "A scoring achievement. Grants the Realm +1 Renown every time one is achieved.",

    # ── World ──
    "Bandit":        "Neutral hostile force; Bandit Camps spawn in Outlaw Country and on low Public Order.",
    "Outlaw Country": "Uncontrollable Territory zones where Bandit Camps spawn ({OUTLAW_COUNTRY_START} Territories each at Setup). A zone is your Outlaw Country while any of its Territories is within your Province. Foster Rebellion expands it when there is no room; otherwise, when there is no room, its Bandit Camps grow instead.",
    "Wild Outlaw Country": "Outlaw Country the Host places outside every Province at Setup. After Setup it works like any other Outlaw Country zone.",
    "Siege":         "An Army holding Adjacent to an at-war Settlement while a Siege Timer counts down to Capture or Sack it.",
}

# ── Pivotal: one word for "an Unmodified FOCUSED_THR" across all combat effects ─────────────
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
MORALE_DICE_MAX     = 5    # dice rolled on a Break or Panic check
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
    "Bill Hook":      {"ap": -1, "init":  0, "tier": "Cast",   "tags":  [TWO_H, NEGATE_SHIELDED]},
    "Daggers":        {"ap":  0, "init":  0, "tier": "Cast",    "tags": [TWO_H, SHATTER_ARMOR, NO_PARRY]},
    "Short Sword":    {"ap":  0, "init":  0, "tier": "Cast",    "tags": [STEADY]},
    "Spears":         {"ap":  0, "init":  1, "tier": "Cast",    "tags": [UNWIELDY, SHATTER_ARMOR], 'note': 'At the beginning of each equipment step, you may choose the 1H or 2H profile.'},
    "2HSpears":       {"ap":  0, "init":  1, "tier": "Cast",    "tags": [TWO_H, STEADY, SHATTER_ARMOR]},
    "Arming Sword":   {"ap": -1, "init":  0, "tier": "Wrought", "tags": [STEADY]},
    "Pike":           {"ap": -2, "init":  1, "tier": "Wrought", "tags": [TWO_H, STEADY, UNWIELDY, SHATTER_ARMOR, NO_PARRY]},
    "Flail":          {"ap": -1, "init":  0, "tier": "Wrought", "tags": [UNWIELDY, UNSTOPPABLE, CLEAVE, NO_PARRY], 'note': 'Cannot Florentine'},
    "Halberd":        {"ap": -2, "init":  0, "tier": "Wrought", "tags": [TWO_H, STEADY]},
    "Battle Axe":     {"ap": -3, "init": -1, "tier": "Wrought", "tags": [TWO_H, UNSTOPPABLE, CLEAVE, NEGATE_SHIELDED]},
    "Cavalry Spear":  {"ap": -2, "init":  1, "tier": "Wrought", "tags": [STEADY, UNWIELDY, UNSTOPPABLE, NO_PARRY], 'note': "Needs Stable; no Tower Shield or Florentine or Ranged Weapon"},
    "Morningstar":    {"ap": -4, "init": -1, "tier": "Forged",  "tags": [CLEAVE, DESTROY_SHIELD], 'note': 'Cannot Florentine'},
    "Bastard Sword":  {"ap": -2, "init":  0, "tier": "Forged",  "tags": [STEADY, SHATTER_ARMOR], 'note': 'At the beginning of each equipment step, you may choose the 1H or 2H profile.'},
    "2HBastard":      {"ap": -2, "init":  0, "tier": "Forged",  "tags": [TWO_H, UNSTOPPABLE, CLEAVE]},
    "War Hammer":     {"ap":-10, "init": -1, "tier": "Forged",  "tags": [TWO_H, STEADY, UNSTOPPABLE, NEGATE_SHIELDED, DESTROY_SHIELD]},
    "Lance":          {"ap": -4, "init":  1, "tier": "Forged",  "tags": [STEADY, UNWIELDY, UNSTOPPABLE, NO_PARRY, DESTROY_SHIELD], 'note': "Needs Saddlery; no Tower Shield, Florentine, Ranged weapon."},
    "Estoc":          {"ap": -3, "init":  0, "tier": "Crafted", "tags": [STEADY, SHATTER_ARMOR, UNSTOPPABLE]},
    "Poleaxe":        {"ap": -5, "init":  0, "tier": "Crafted", "tags": [TWO_H, STEADY, CLEAVE, UNSTOPPABLE, NEGATE_SHIELDED]},
}
# 1H / 2H profiles: an entry named "2H<Name>" is the 2H profile of the weapon named <Name> (or the one weapon
# whose name starts with it: "2HBastard" → "Bastard Sword"). That weapon gets "profile_2h"; it is one item that
# picks its profile each equipment step, and the "2H…" entry is never offered as a weapon of its own.
for _k2 in [k for k in WEAPONS if k.startswith("2H")]:
    _base = [k for k in WEAPONS if not k.startswith("2H") and (k == _k2[2:] or k.startswith(_k2[2:]))]
    _base = [k for k in _base if k == _k2[2:]] or _base
    if len(_base) != 1:
        raise ValueError(f"WEAPONS: 2H profile {_k2!r} matches {_base or 'no weapon'}")
    WEAPONS[_base[0]].setdefault("profile_2h", _k2)
WEAPON_2H_PROFILES = {v["profile_2h"]: k for k, v in WEAPONS.items() if v.get("profile_2h")}   # "2H…" entry → its weapon

RANGED = {
    "Hunting Bow": {"ap":  0, "init":  2, "tier": "Crude",   "tags": [TWO_H, UNSTOPPABLE, NO_PARRY]},
    "Longbow":     {"ap": -1, "init":  2, "tier": "Cast",    "tags": [TWO_H, UNSTOPPABLE, SHATTER_ARMOR, NO_PARRY]},
    "Javelin":     {"ap": -2, "init":  1, "tier": "Wrought", "tags": [STEADY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, DESTROY_SHIELD, ONE_SHOT, NO_PARRY], 'note': 'Cannot Florentine'},
    "Crossbow":    {"ap": -4, "init":  1, "tier": "Forged",  "tags": [TWO_H, UNWIELDY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NO_PARRY]},#'note': "Tower Shield only (no other shield), cannot Dual Wield"
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
    ("Prowess", "Sovereign"): "Immune Blunder",
    ("Piety",   "Rising"): "Morale +1",
    ("Piety", "Sovereign"): "Immune Panic",
    ("Cunning", "Established"): "Opponent gains Strained.", #Remove "Foes gain Blunder in first Skirmish"
    ("Cunning", "Sovereign"):   "Opponent gains Blunder in the first Skirmish.", #Remove "Foes gain Strained"
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
# Battle chronicle (board, Battle view): one line per event, read as the Battle happens. Each list is a set of variants
# (the board picks one); fill-ins: {side} {foe} player / camp names · {troops} {foe_troops} Retinue plurals ·
# {weapon} {armor} {foe_weapon} {foe_armor} · {tactic} {foe_tactic} · {n} dice · {hits} {saved} {lost} {left} {tens} counts ·
# {need} the number to roll · {mod} the roll modifier ("+1", "−1", "no modifier") · {sk} the Skirmish.
# Strike lines pick by how many dice made it: _high (60%+), _mid, _low, _none. Edit freely; unknown fill-ins print as-is.
BATTLE_NARRATION = {
    "plural": {"Levy": "levies", "Man-at-Arms": "men-at-arms", "Sergeant": "sergeants", "Knight Templar": "knights templar"},
    "reveal": ["Skirmish {sk}: {side} commit to {tactic}; {foe} answer with {foe_tactic}.",
               "Skirmish {sk} opens: {tactic} from {side}, {foe_tactic} from {foe}."],
    "first": ["{side} move first.", "{side}'s {troops} are quicker to the blow."],
    "strike_high": ["{side}'s {troops} drive in with {weapon}: {hits} of {n} blows land (needing {need}, {mod}).",
                    "A hard press from {side} — {hits} of {n} {weapon} strikes find their mark."],
    "strike_mid":  ["{side}'s {troops} trade blows with {weapon}; {hits} of {n} land (needing {need}, {mod}).",
                    "{hits} of {side}'s {n} strikes get through the press."],
    "strike_low":  ["{side}'s {troops} swing wide: only {hits} of {n} {weapon} strikes land (needing {need}, {mod}).",
                    "The {foe_troops} hold the line — {side} land just {hits} of {n}."],
    "strike_none": ["Not one of {side}'s {n} strikes lands (needing {need}, {mod}).",
                    "{side}'s {troops} flail at the {foe_troops} and hit nothing."],
    "strike_tens": ["{tens} of them land with full weight ({focus})."],
    "parry":       ["{side}'s {troops} turn aside {saved} of {n} blows.", "Steel rings — {side} parry {saved} of {n}."],
    "parry_none":  ["{side} can't turn a single blow aside."],
    "riposte":     ["{tens} times {side} answer a parry with a riposte."],
    "save_good":   ["{armor} holds: {saved} of {n} saved, {lost} {troops} fall.", "{side}'s {armor} turns {saved} of {n}; {lost} go down."],
    "save_bad":    ["{armor} gives way — {lost} of {side}'s {troops} fall, only {saved} of {n} saved.",
                    "{lost} {troops} of {side} are cut down; their {armor} saves just {saved} of {n}."],
    "save_none":   ["Every blow is turned — {side}'s {armor} saves all {n}."],
    "recover":     ["{saved} of {side}'s fallen {troops} stagger back to their feet."],
    "panic_hold":  ["{side}'s {troops} waver but hold."],
    "panic_lose":  ["Panic runs through {side}'s ranks — {lost} {troops} flee."],
    "break":       ["Exhausted, {side}'s line buckles: {lost} {troops} lost."],
    "skirmish_end":["Skirmish {sk} ends: {side} have {left} {troops} left."],
}
 



# CULTURES: the 15 worldlore cultures as playstyles (replaces PLAYSTYLES).
# Names/domains match renown_worldlore.CULTURES. Read by references/playstyle_reference.py.
# type      : pure | pair | triple | centre
# domains   : culture's domains, lead first (drives banner colours)
# monuments : Monument nodes (NODES type == 'Monument') - standing path is derived from their unlocks
# wonders   : keys of WONDERS
# actions   : "Action" or "Action: mode" - Action must be a key of ACTIONS
# factions  : keys of FACTIONS; every faction maps to at least one culture (duplicates allowed)
# radar     : relative emphasis 1-5 on the seven reference axes
# archetype : playstyle label (tempo x style) (playstyle reference; board culture picker once chosen)
# Culture view filter (settlement board): a player may pick a culture to focus the Holding tree / catalog on its
# Domains, Monuments and Wonders. No game effect. CULTURE_SELF_MADE is the name of "no culture" (everything shown).
CULTURE_SELF_MADE = "Self-made"

CULTURES = {
    # ---- pure ----
    'Trusteki': {
        'type': 'pure', 'domains': ['Industry'], 'archetype': 'Pure Engine',
        'monuments': ['Office of Works', 'Manor House', 'Polish House', 'Port Authority'],
        'wonders':   ['The Grand Exchange', 'High Chancery'],
        'actions':   ['Build', 'Repair', 'Improve'],
        'factions':  ['The Verdant Kingdom', 'The Illuminated Order', 'The Hermit Crown'],
        'mechanic_name': ['Independent, but Ambitious', 'Knowledge is Power', 'Peaceful & Inventive', 'Mercantile Pact', 'Integrated Arms', 'Friends in High Places', 'Tunnellers', 'Prosperity for All', 'Heart of Trade'],
        'radar': {'military_solutions': 3, 'economy_generators': 5, 'faith_management': 3, 'doubt_warfare': 1,
                  'political_control': 3, 'board_presence': 3, 'degenerate_punishment': 2},
    },
    'Kraghs': {
        'type': 'pure', 'domains': ['Prowess'], 'archetype': 'Pure Aggro',
        'monuments': ['Royal Pavilion', 'Marshal Tiltyard', 'Ministry of Military Strategy', 'Baggage Train'],
        'wonders':   ['Colossus'],
        'actions':   ['Move: Battle', 'Declare War', 'Demand Tribute'],
        'factions':  ['The Boundless Steppe', 'The Final Word', 'The Wandering Crown', 'The Ancient Wilds', 'The Winter Wolves','The Yew Heart'],
        'mechanic_name': ['Horsemasters', 'The Decider', 'Pillagers', 'Archery is a Way of Life', 'Terrain Negotiators', 'Occupy', 'Scavengers', 'Siege Specialists', 'The Highest Bidder'],
        'radar': {'military_solutions': 5, 'economy_generators': 1, 'faith_management': 3, 'doubt_warfare': 2,
                  'political_control': 2, 'board_presence': 5, 'degenerate_punishment': 4},
    },
    'Ithiss': {
        'type': 'pure', 'domains': ['Cunning'], 'archetype': 'Pure Tempo',
        'monuments': ["Thieves' Guild", 'Outlaw Rookery', 'Whispering Undercroft', 'Outrider Intercept Post'],
        'wonders':   ['High Chancery'],
        'actions':   ['Raze', 'Foster Rebellion', 'Intercept Caravan'],
        'factions':  ['The Bandit King', 'The Crimson Tide', 'The Illusionists'],
        'mechanic_name': ['Fiends in Low Places', 'Uncharted Sea Lanes', 'Pestilence', 'Masters of Duplicity', 'Mimic', 'Double Speak', 'Knowledge is Power', 'Royal Marriage', 'Friends in High Places'],
        'radar': {'military_solutions': 2, 'economy_generators': 3, 'faith_management': 1, 'doubt_warfare': 5,
                  'political_control': 3, 'board_presence': 2, 'degenerate_punishment': 5},
    },
    'Lenavorites': {
        'type': 'pure', 'domains': ['Piety'], 'archetype': 'Pure Control',
        'monuments': ['Senate Hall', 'Inquisitorial Palace', 'Exalted Basilica', 'Papal Palace'],
        'wonders':   ['The Eternal Sepulchre', 'High Chancery'],
        'actions':   ['Tithe', 'Send Missionaries', 'Spread Truth'],
        'factions':  ['The Sacred Throne', 'The Undying Flame','The Iron Faith', 'The Hermit Crown'],
        'mechanic_name': ['Fortress of Faith', 'Sacrosanct', 'Martyrdom', 'Arts & Humanities / Hearts & Minds', 'Friends in High Places', 'Palatine'],
        'radar': {'military_solutions': 2, 'economy_generators': 3, 'faith_management': 5, 'doubt_warfare': 3,
                  'political_control': 3, 'board_presence': 1, 'degenerate_punishment': 3},
    },
    # ---- pairs ----
    'Belvareth': {
        'type': 'pair', 'domains': ['Piety', 'Prowess'], 'archetype': 'Sustained Tempo',
        'monuments': ["Preceptory of the Knight's Templar", 'Royal Pavilion', 'Exalted Basilica', 'Marshal Tiltyard'],
        'wonders':   ['The Eternal Sepulchre', 'Colossus'],
        'actions':   ['Sacred War', 'Move: Battle', 'Spread Truth'],
        'factions':  ['The Bloodied Cross', 'The Blazing Standard', 'The Undying Flame', 'The Iron Faith'],
        'mechanic_name': ['Prophets of War', 'Inexorable', 'Sacrosanct', 'Fortress of Faith', 'Siege Specialists', 'Wise & Suspicious', 'Martyrdom'],
        'radar': {'military_solutions': 5, 'economy_generators': 2, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 2, 'board_presence': 3, 'degenerate_punishment': 2},
    },
    'Vorghith': {
        'type': 'pair', 'domains': ['Prowess', 'Cunning'], 'archetype': 'Fluid Aggro',
        'monuments': ['Outrider Intercept Post', 'Baggage Train', 'Outlaw Rookery', 'Marshal Tiltyard'],
        'wonders':   ['Colossus'],
        'actions':   ['Pillage', 'Intercept Caravan', 'Move: March'],
        'factions':  ["The Squatters' Crown", 'The Winter Wolves', 'The Bandit King','The Smoldering Crown', 'The Elder Grove'],
        'mechanic_name': ['Pillagers', 'Reckless', 'Wandering Nomads', 'Occupy', 'Horsemasters', 'The Decider', 'Wise & Suspicious'],
        'radar': {'military_solutions': 4, 'economy_generators': 2, 'faith_management': 1, 'doubt_warfare': 4,
                  'political_control': 3, 'board_presence': 4, 'degenerate_punishment': 5},
    },
    'Drakteni': {
        'type': 'pair', 'domains': ['Prowess', 'Industry'], 'archetype': 'Scaling Aggro',
        'monuments': ['Advanced Blast Furnace', 'Ministry of Military Strategy', 'Artillery Park', 'Imperial Palace', 'Baggage Train'],
        'wonders':   ['Colossus'],
        'actions':   ['Move: Lay Siege', 'Improve', 'Demand Tribute'],
        'factions':  ['The Battering Ram', 'The Yew Heart', 'The Sublime Gate', 'The Final Word'],
        'mechanic_name': ['The Decider','Siege Specialists', 'Archery is a Way of Life', 'Integrated Arms', 'Friends in High Places', 'Tunnellers', 'Horsemasters', 'The Monarch'],
        'radar': {'military_solutions': 5, 'economy_generators': 4, 'faith_management': 2, 'doubt_warfare': 2,
                  'political_control': 3, 'board_presence': 4, 'degenerate_punishment': 2},
    },
    'Prezish': {
        'type': 'pair', 'domains': ['Cunning', 'Industry'], 'archetype': 'Sustained Engine',
        'monuments': ['Aristocratic Court', "Thieves' Guild", 'Port Authority', 'Polish House', 'Manor House'],
        'wonders':   ['The Grand Exchange', 'High Chancery'],
        'actions':   ['Intercept Caravan', 'Sign Treaty: Trade Agreement', 'Build'],
        'factions':  ['The Merchant Republics', 'The Gilded Path', 'The Grand Compact', 'The Crimson Tide'],
        'mechanic_name': ['Heart of Trade', 'Mercantile Pact', 'Uncharted Sea Lanes', 'Independent, but Ambitious', 'Royal Marriage', 'Patient Court', 'Friends in High Places', 'Double Speak', 'Masters of Duplicity'],
        'radar': {'military_solutions': 2, 'economy_generators': 5, 'faith_management': 2, 'doubt_warfare': 4,
                  'political_control': 3, 'board_presence': 1, 'degenerate_punishment': 3},
    },
    'Shassolin': {
        'type': 'pair', 'domains': ['Cunning', 'Piety'], 'archetype': 'Sustained Control',
        'monuments': ['Senate Hall', 'Inquisitorial Palace', 'Ossuary Crypt', 'Serfdom'],
        'wonders':   ['High Chancery', 'The Eternal Sepulchre'],
        'actions':   ['Send Missionaries', 'Tithe', 'Destabilize'],
        'factions':  ['The Ashen Vale','The Forked Tongue', "The Iron Faith"],
        'mechanic_name': ['Friends in High Places', 'Royal Marriage', 'Palatine', 'Pestilence', 'Double Speak', 'Arts & Humanities / Hearts & Minds', 'Fortress of Faith', 'Knowledge is Power', 'Patient Court'],
        'radar': {'military_solutions': 2, 'economy_generators': 2, 'faith_management': 4, 'doubt_warfare': 5,
                  'political_control': 4, 'board_presence': 1, 'degenerate_punishment': 5},
    },
    'Madekites': {
        'type': 'pair', 'domains': ['Piety', 'Industry'], 'archetype': 'Scaling Control',
        'monuments': ['Office of Works', 'Papal Palace', 'Exalted Basilica', 'Port Authority', 'Manor House'],
        'wonders':   ['The Eternal Sepulchre', 'The Grand Exchange'],
        'actions':   ['Improve', 'Build', 'Spread Truth'],
        'factions':  ['The Iron Faith', 'The Gilded Crescent', 'The Tunnellers', 'The Verdant Kingdom'],
        'mechanic_name': ['Fortress of Faith', 'Palatine', 'Arts & Humanities / Hearts & Minds', 'Knowledge is Power', 'Prosperity for All', 'Unimpeachable', 'Sacrosanct', 'Peaceful & Inventive', 'Terrain Negotiators'],
        'radar': {'military_solutions': 3, 'economy_generators': 5, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 2, 'board_presence': 1, 'degenerate_punishment': 3},
    },
    # ---- triples ----
    'Cailendroffs': {
        'type': 'triple', 'domains': ['Piety', 'Prowess', 'Cunning'], 'archetype': 'Fluid Control',
        'monuments': ['Inquisitorial Palace', 'Royal Pavilion', "Preceptory of the Knight's Templar", 'Whispering Undercroft'],
        'wonders':   ['Colossus', 'High Chancery'],
        'actions':   ['Sacred War', 'Declare War', 'Negotiate'],
        'factions':  ['The Crowned Star', 'The Entwined Crown', 'The Hermit Crown', 'The Bloodied Cross'],
        'mechanic_name': ['The Monarch', 'Royal Marriage', 'Independent, but Ambitious', 'Prophets of War', 'The Decider', 'Martyrdom', 'Inexorable', 'Integrated Arms', 'Friends in High Places', 'Wise & Suspicious'],
        'radar': {'military_solutions': 4, 'economy_generators': 1, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 4, 'board_presence': 4, 'degenerate_punishment': 3},
    },
    'Sarkopekt': {
        'type': 'triple', 'domains': ['Cunning', 'Industry', 'Prowess'], 'archetype': 'Scaling Tempo',
        'monuments': ['Outrider Intercept Post', 'Baggage Train', 'Advanced Blast Furnace', 'Artillery Park'],
        'wonders':   ['Colossus', 'The Grand Exchange'],
        'actions':   ['Move: Battle', 'Demand Tribute', 'Sabotage'],
        'factions':  ['The Broken Banner', 'The Sublime Gate', 'The Iron Shore', 'The Boundless Steppe', 'The Ancient Wilds',
                      'The Battering Ram'],
        'mechanic_name': ['Siege Specialists', 'Horsemasters', 'Tunnellers', 'Scavengers', 'Terrain Negotiators', 'The Highest Bidder', 'Reckless', 'Occupy', 'Wandering Nomads', 'Archery is a Way of Life', 'The Decider', 'Uncharted Sea Lanes'],
        'radar': {'military_solutions': 4, 'economy_generators': 4, 'faith_management': 1, 'doubt_warfare': 3,
                  'political_control': 2, 'board_presence': 5, 'degenerate_punishment': 5},
    },
    'Ossensteins': {
        'type': 'triple', 'domains': ['Cunning', 'Piety', 'Industry'], 'archetype': 'Scaling Engine',
        'monuments': ['Office of Works', 'Aristocratic Court', 'Whispering Undercroft', 'Studium Generale', 'Ossuary Crypt', 'Exalted Basilica'],
        'wonders':   ['The Grand Exchange', 'High Chancery'],
        'actions':   ['Tithe', 'Destabilize', 'Improve'],
        'factions':  ['The Hall of Masks', 'The Forked Tongue', 'The Velvet Hand', 'The Illusionists', 'The Illuminated Order',
                      'The Eternal Court'],
        'mechanic_name': ['Patient Court', 'Mercantile Pact', 'Knowledge is Power', 'Fortress of Faith', 'Independent, but Ambitious', 'Sacrosanct', 'Heart of Trade', 'Uncharted Sea Lanes', 'Double Speak', 'Friends in Low Places', 'Pestilence'],
        'radar': {'military_solutions': 1, 'economy_generators': 5, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 5, 'board_presence': 1, 'degenerate_punishment': 4},
    },
    'Voldrastel': {
        'type': 'triple', 'domains': ['Piety', 'Industry', 'Prowess'], 'archetype': 'Sustained Aggro',
        'monuments': ['Papal Palace', 'Imperial Palace', "Preceptory of the Knight's Templar", 'Ministry of Military Strategy', 'Port Authority'],
        'wonders':   ['The Grand Exchange', 'The Eternal Sepulchre'],
        'actions':   ['Sacred War', 'Muster', 'Repair'],
        'factions':  ['The Iron Throne', 'The Grand Compact', 'The Pale Throne', 'The Merchant Republics'],
        'mechanic_name': ['Unimpeachable', 'Mercantile Pact', 'Heart of Trade', 'Inexorable', 'Sacrosanct', 'Uncharted Sea Lanes', 'Friends in High Places', 'Siege Specialists', 'Horsemasters', 'The Decider', 'Integrated Arms', 'The Monarch'],
        'radar': {'military_solutions': 3, 'economy_generators': 4, 'faith_management': 4, 'doubt_warfare': 1,
                  'political_control': 3, 'board_presence': 3, 'degenerate_punishment': 2},
    },
    # ---- centre ----
    'Astravantheliad': {
        'type': 'centre', 'domains': ['Piety', 'Prowess', 'Cunning', 'Industry'], 'archetype': 'Fluid Tempo',
        'monuments': ['Senate Hall', 'Studium Generale', 'Aristocratic Court', 'Office of Works'],
        'wonders':   ['High Chancery', 'The Grand Exchange', 'The Eternal Sepulchre', 'Colossus'],
        'actions':   ['Negotiate', 'Sign Treaty', 'End Treaty'],
        'factions':  ['The Dukedom', 'The Eternal Court', 'The Illuminated Order', 'The Luminous Court',
                      'The Inner Circle'],
        'mechanic_name': ['Patient Court', 'Knowledge is Power', 'The Duke', 'Royal Marriage', 'Heart of Trade', 'Friends in High Places', 'The Monarch', 'Peaceful & Inventive', 'Palatine', 'Masters of Duplicity','Luxury Trades'],
        'radar': {'military_solutions': 2, 'economy_generators': 3, 'faith_management': 4, 'doubt_warfare': 3,
                  'political_control': 5, 'board_presence': 2, 'degenerate_punishment': 3},
    },
}


# ── NODES — THE master Holding graph. EDIT HERE. ──
# Per Holding: group (a HOLDING_GROUPS id; `type` is derived from it), root, unlock (Standing gate), innate (the
# Holding's effect), efficient (its Mastery Chain parent(s); `builds_into` is derived), monument, deprecated.
# terrain: Territory types (TERRAIN keys) that supply it — empty or absent = no requirement; otherwise one of them
# must lie within the Reach of the Settlement it's built in. TERRAIN "Raw Materials" and the map generator's resource
# placement are derived from this (main terrain first — see below TERRAIN).
# The sim reads HOLDING_SIM, which is derived from this text at the bottom of this file.
NODES = {
    "Quarry": {
        "group": "g_raw",
        "root": True,
        "terrain": ["Tundra", "Mountains"],
        "unlock": "-",
        "natural": True,
        "innate": "Gold +500; Craft +1",
        "monument": False},
    "Salt Works": {
        "group": "g_raw",
        "root": True,
        "terrain": ["Wetlands", "Tundra"],
        "unlock": "-",
        "natural": True,
        "innate": "Gold +500; Craft +1",
        "monument": False},
    "Apiary": {
        "group": "g_raw",
        #"root": True,
        #"deprecated": True,
        "unlock": "-",
        "natural": True,
        "innate": "Gold +500; Craft +1",
        "efficient": ["Hamlet"],
        "monument": False},
    "Peat Bog": {
        "group": "g_raw",
        "root": True,
        "terrain": ["Wetlands"],
        "unlock": "-",
        "natural": True,
        "innate": "Gold +500; Craft +1",
        "monument": False},
    "Forestry": {
        "group": "g_raw",
        "root": True,
        "terrain": ["Forest"],
        "unlock": "-",
        "natural": True,
        "innate": "Gold +500; Craft +1",
        "monument": False},
    "Fishmongery": {
        "group": "g_raw",
        "root": True,
        "terrain": ["Water"],
        "unlock": "-",
        "natural": True,
        "innate": "Gold +500; Craft +2",
        "monument": False},
    "Furnace": {
        "group": "g_raw",
        "root": True,
        "terrain": ["Mountains"],
        "unlock": "-",
        "natural": True,
        "innate": "Gold +500; Unlocks Cast Weapons",
        "monument": False},
    "Arable Land": {              # DEPRECATED: not a root and nothing builds into it, so it can't be played; its old
        "group": "g_raw",         # dependents build into a Hamlet instead
        "deprecated": True,
        "unlock": "-",
        "natural": True,
        "innate": "+500",
        "efficient": [],
        "monument": False},
    "Common Land": {
        "group": "g_raw",
        "root": True,
        "deprecated":True,
        "unlock": "-",
        "natural": True,
        "innate": "Gold +1000; Doubt +1",
        "efficient": ["Hamlet"],          # may start a Hamlet (Hamlet = location token, not a Holding)
        "monument": False},
    "Plant Nursery": {
        "group": "g_husbandry",
        "unlock": "-",
        "natural": True,
        "innate": "Craft +4",
        "efficient": "Hamlet",
        "monument": False},
    "Herb Garden": {
        "group": "g_husbandry",
        "unlock": "Rising Industry",
        "natural": True,
        "innate": "Gold +1000; Craft +2",
        "efficient": "Plant Nursery",
        "monument": False},
    "Animal Husbandry": {
        "group": "g_husbandry",
        "root": True,
        "terrain": [],
        "unlock": "-",
        "natural": True,
        "innate": "Supply -500; Unlocks Crude armor & shield",
        "efficient": "Hamlet",
        "monument": False},
    "Saddlery": {
        "group": "g_husbandry",
        "unlock": "1 Established",
        "natural": True,
        "innate": "Gold +500; Craft +2; Speed +1; Unlocks Lance (Still requires Tier Unlock)",
        "efficient": ["Stable"],
        "monument": False},
    "Avenery": {
        "group": "g_husbandry",
        "unlock": "1 Established",
        "natural": True,
        "innate": "Gold +500; Speed +1",
        "efficient": ["Saddlery"],
        "monument": False},
    "Farriery": {
        "group": "g_husbandry",
        "unlock": "Established Prowess",
        "natural": True,
        "innate": "Gold +500; Speed +1; Unlocks Cavalry Spears regardless of Tier Unlock",
        "efficient": ["Avenery"],
        "monument": False},
    "Marshal Tiltyard": {
        "group": "g_husbandry",
        "unlock": "Sovereign Prowess",
        "natural": True,
        "innate": "Initiative +1; Unlocks Lances regardless of Tier Unlock; Armies must be equipped with Lance",
        "efficient": ["Farriery"],
        "monument": True},
    "Vine Nursery": {
        "group": "g_husbandry",
        "unlock": "-",
        "natural": True,
        "innate": "Gold +1000 in Fall",
        "efficient": "Hamlet",
        "monument": False},
    "Vineyard": {
        "group": "g_husbandry",
        "unlock": "Rising Industry",
        "natural": True,
        "innate": "Gold +2000 in Fall",
        "efficient": "Vine Nursery",
        "monument": False},
    "Arboretum": {
        "group": "g_husbandry",
        "unlock": "-",
        "natural": True,
        "innate": "Gold +500",
        "efficient": "Hamlet",
        "monument": False},
    "Orchard": {
        "group": "g_husbandry",
        "unlock": "Rising Industry",
        "natural": True,
        "innate": "Gold +1000; Gold +500 in Fall",
        "efficient": "Arboretum",
        "monument": False},
    "Carpentry": {
        "group": "g_arms",
        "unlock": "-",
        "innate": "Gold +500; Craft +1; Build Timer -1",
        "efficient": "Forestry",
        "monument": False},
    "Alchemy": {
        "group": "g_commerce",
        "unlock": "-",
        "innate": "Gold +500; Craft +2",
        "efficient": "Peat Bog",
        "monument": False},
    "Masonry": {
        "group": "g_works",
        "unlock": "-",
        "innate": "Build Timer -1; No Upkeep on Primitive Infrastructure",
        "efficient": "Quarry",
        "monument": False},
    "Butchery": {
        "group": "g_logistics",
        "unlock": "-",
        "natural": True,
        "innate": "Craft +3; Supply -500",
        "efficient": ["Salt Works", "Animal Husbandry"],
        "monument": False},
    "Arable Land": {
        "group": "g_husbandry",
        "unlock": "-",
        "natural": True,
        "innate": "Gold +500",
        "efficient": "Hamlet",
        "monument": False}, 
    "Bakery": {
        "group": "g_husbandry",
        "unlock": "Rising Industry",
        "natural": True,
        "innate": "Gold +500; Faith +1",
        "efficient": "Arable Land",
        "monument": False},
    "Weavery": {
        "group": "g_commerce",
        "deprecated": True,
        "unlock": "-",
        "innate": "+1000; Craft +3",
        "efficient": "Market Square",
        "builds_into": ["Artisan Workshop", "Mill"],
        "monument": False},
    "Fletchery": {
        "group": "g_arms",
        "unlock": "Rising Prowess",
        "innate": "Supply -500; Unlocks Ranged Weapons",
        "efficient": "Carpentry",
        "monument": False},
    "Chandlery": {
        "group": "g_devotion",
        "unlock": "-",
        "innate": "Craft +1; Authority -1 on Cunning actions targeting you",
        "efficient": "Forestry",
        "monument": False},
    "Tannery": {
        "group": "g_arms",
        "unlock": "-",
        "natural": True,
        "innate": "Craft +1; Supply -500; Unlocks Cast armor & shield",
        "efficient": ["Animal Husbandry","Joinery"],
        "monument": False},
    "Joinery": {
        "group": "g_arms",
        "unlock": "Rising Industry",
        "innate": "Supply -500; Unlocks Shields",
        "efficient": ["Carpentry","Salt Works", "Furnace"],
        "monument": False},
    #"Furnace": {
    #    "group": "g_arms",
    #    "unlock": "-",
    #    "innate": "Unlocks Cast Weapons; +500",
    #    "efficient": "Mine",
    #    "builds_into": ["Blacksmith"],
    #    "monument": False},
    "Blacksmith": {
        "group": "g_arms",
        "unlock": "Rising Industry",
        "innate": "Craft +2; Supply -500; Unlocks Wrought Weapons",
        "efficient": "Furnace",
        "monument": False},
    "Finery": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "Craft +3; Weapons gain -1AP",
        "efficient": ["Forge"],
        "monument": False}, 
    "Jewelry Foundry": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": f"Gold +2000; Craft +5; {EXPOSED} 1",
        "efficient": ["Finery"],
        "monument": False},
    "Polish House": {
        "group": "g_commerce",
        "unlock": "Sovereign Industry",
        "infrastructure_req": "Aqueducts",
        "innate": f"Gold +3000; Craft +10; {EXPOSED} 1",
        "efficient": "Jewelry Foundry",
        "monument": True},
    "Armory": {
        "group": "g_arms",
        "unlock": "Rising Industry",
        "innate": "Craft +3; Unlocks Wrought armor & shield",
        "efficient": ["Tannery"],
        "monument": False},
    "Master Workshop": {
        "group": "g_arms",
        "unlock": "Established Industry",
        "innate": "Craft +2; Supply -500; Add Serrated to Weapons",
        "efficient": "Finery",
        "monument": False},
    "Gilded Foundry": {
        "group": "g_arms",
        "unlock": "Established Industry",
        "innate": "Supply -1000; Unlocks Forged armor & shield",
        "efficient": "Armory",
        "monument": False},
    "Smokehouse": {
        "group": "g_logistics",
        "unlock": "Rising Prowess",
        "natural": True,
        "innate": "Craft +2; Supply -1000",
        "efficient": ["Charcoal Burner"],
        "monument": False},
    "Workyard": {
        "group": "g_works",
        "unlock": "Rising Cunning",
        "natural": True,
        "innate": "Gold +1000; Doubt +1",
        "efficient": ["Salt Works"],
        "monument": False},
    "Storehouse": {
        "group": "g_works",
        "unlock": "Established Cunning",
        "natural": True,
        "innate": "Upkeep -2000; Doubt +1; Build Timer -1",
        "efficient": ["Census Hall"],
        "monument": False},
    "Brewhouse": {
        "group": "g_husbandry",
        "unlock": "Rising Industry",
        "natural": True,
        "innate": "Gold +2500 in Winter",
        "efficient": "Apiary",
        "monument": False},
    "Meadery": {
        "group": "g_husbandry",
        "unlock": "Rising Industry",
        "natural": True,
        "innate": "Gold +2500 in Winter; Faith +1; Speed +5 in Winter",
        "efficient": "Brewhouse",
        "monument": False},
    "Winery": {
        "group": "g_husbandry",
        "unlock": "Established Industry",
        "natural": True,
        "innate": "Craft +5",
        "efficient": "Vineyard",
        "monument": False},
    "Cidery": {
        "group": "g_husbandry",
        "unlock": "Established Industry",
        "natural": True,
        "innate": "Gold +500; Craft +1; Faith +1",
        "efficient": "Orchard",
        "monument": False},
    "Market Square": {
        "group": "g_commerce",
        "unlock": "Rising Industry",
        "infrastructure_req": "Town Square",
        "innate": "Gold +500; Craft +2",
        "efficient": "Courtyard",
        "monument": False},
    "Inn": {
        "group": "g_court",
        "root": True,
        "terrain": [],
        "unlock": "-",
        "infrastructure_req": "Town Square",
        "natural": True,
        "innate": "Gold +500; Influence +1; Faith +1 per Trade Partner with Craft 5+, and those Trade Partners gain Faith +1",
        "monument": False},
    "Spice Merchant": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "natural": True,
        "innate": f"Gold +1500; Craft +4; {EXPOSED} 1",
        "efficient": "Herb Garden",
        "monument": False},
    "Harbor": {
        "group": "g_commerce",
        "unlock": "Rising Industry",
        "innate": "Can Trade; Craft +2; Extort 500 per player without Harbor",
        "efficient": "Fishmongery",
        "monument": False},
    "Merchant Quarter": {
        "group": "g_commerce",
        "unlock": "Rising Industry",
        "infrastructure_req": "Magistrate's Hall",
        "innate": "Craft +5; Trade Partners gain Craft +3",
        "efficient": ["Courtyard"],
        "monument": False},
    "Money Lending": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "Once per Empire Phase, you may loan money to another player at 100 per 1000/turn interest (minimum 100); on Default: Perform Demand Tribute; Extort 1000",
        "efficient": ["Merchant Quarter"],
        "monument": False},
    "Esteemed Bank": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "Each Empire Phase, Gain 1000 per 10000 in Treasury",
        "efficient": ["Money Lending"],
        "monument": False},
    "Census Hall": {
        "group": "g_works",
        "unlock": "Established Cunning",
        "natural": True,
        "innate": "Gold +1000; Craft +3; Doubt +1",
        "efficient": "Burgages",
        "monument": False},
    "Caravanery": {
        "group": "g_logistics",
        "unlock": "-",
        "natural": True,
        "innate": "Authority -2 on Intercept Caravan actions targeting you; Speed -2 to non-allied Armies in your Province",
        "efficient": ["Courier Network"],
        "monument": False},
    "Stable": {
        "group": "g_arms",
        "unlock": "1 Rising",
        "natural": True,
        "innate": "Speed +2; Unlocks Cavalry Spear (Still requires Tier Unlock)",
        "efficient": ["Animal Husbandry","Inn"],
        "monument": False},
    "Ropewalk": {
        "group": "g_logistics",
        "unlock": "Rising Prowess",
        "innate": "Gold +500; Supply -500",
        "efficient": "Harbor",
        "monument": False},
    "Sail Loft": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        "innate": "Gold +500; Upkeep -500",
        "efficient": "Ropewalk",
        "monument": False},
    "Shipyard": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "Upkeep -500; Craft +4; Water Territory treated as Grassland for movement",
        "efficient": "Sail Loft",
        "monument": False},
    "False Lights": {
        "group": "g_secrecy",
        "unlock": "Rising Cunning",
        "innate": "Non-allied Armies that Move onto a Water Territory in your Province gain Blocked",
        "efficient": "Harbor",
        "monument": False},
    "Corsair Haven": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "Whenever a player who isn't your Trade Partner receives Trade Income, they gain Doubt +1",
        "efficient": "False Lights",
        "monument": False},
    "Fish Weir": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "Gold +2500 in Spring",
        "efficient": "Harbor",
        "monument": False},
    "Cooperage": {
        "group": "g_works",
        "unlock": "Established Industry",
        "innate": "Supply -500; Craft +5",
        "efficient": "Fish Weir",
        "monument": False},
    "Coliseum": {
        "group": "g_logistics",
        "unlock": "Rising Prowess",
        "infrastructure_req": "Muster Field",
        "innate": "Faith +1 while at War; Unlocks Man-at-Arms for Muster",
        "efficient": "Conditioning Field",
        "monument": False},
    "Interrogation Chambers": {
        "group": "g_devotion",
        "unlock": "Rising Piety",
        "innate": "Extort 500; Doubt from actions targeting you is reduced by 1 (minimum 0)",
        "efficient": "Episcopal Court",
        "monument": False},
    "Stew Pond": {
        "group": "g_devotion",
        "unlock": "-",
        "innate": "Upkeep -1000",
        "efficient": "Fishmongery",
        "monument": False},
    "Priory": {
        "group": "g_devotion",
        "unlock": "Rising Piety",
        "innate": "Faith +1; If your Piety Envoy would be Condemned, it Fails instead",
        "efficient": ["Masonry", "Stew Pond"],
        "monument": False},
    "Abbey": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "innate": "Upkeep -500; Authority -2 on Piety actions targeting you", #Once per Envoy Phase: Authority +2 another player's Piety Envoy;
        "efficient": "Priory",
        "monument": False},
    "Reliquary": {
        "group": "g_devotion",
        "unlock": "Rising Piety",
        "innate": "Faith +1; First two Doubt each turn reduced by 1",
        "efficient": "Chandlery",
        "monument": False},
    "Monastery": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "infrastructure_req": "Chapel",
        "innate": "Influence +2; Your Settlements gain Reach +2", #Other players with lower Piety value can't Oppose your Piety Envoys
        "efficient": ["Abbey"],
        "monument": False},
    "Execution Dock": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "innate": "Authority -2 on Foster Rebellion actions targeting you; Players whose actions targeting you would cause Doubt (before modifiers) gain Doubt +1",
        "efficient": "Interrogation Chambers",
        "monument": False},
    "Hospitaller": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "infrastructure_req": "Chapel",
        "innate": "Recover improved by +1; Enduring: Successful Recovered rolls do not count towards the panic check threshold",
        "efficient": "Infirmary",
        "monument": False},
    "Jester's Court": {
        "group": "g_court",
        "unlock": "Rising Piety",
        "infrastructure_req": "Town Square",
        "innate": "First and second Oppose on an Envoy of yours each Envoy Phase: reduce by 1",
        "efficient": "Courtyard",
        "monument": False},
    "Bell Tower": {
        "group": "g_court",
        "unlock": "Rising Piety",
        "innate": "Influence +1; Upkeep -500",
        "efficient": "Jester's Court",
        "monument": False},
    "Embassy": {
        "group": "g_court",
        "unlock": "Established Piety",
        "infrastructure_req": "Library",
        "innate": "Once per Diplomacy Phase, you may cause a Diplomacy action to fail; Other non-vassal players gain Faith +1 per Signed Treaty with you besides Peace",
        "efficient": "Bell Tower",
        "monument": False},
    "Granary": {
        "group": "g_works",
        "deprecated": True,
        "unlock": "Rising Industry",
        "innate": "Supply -1000; Armies and Garrisons within your Settlements gain Immune Strained.",
        "efficient": "",
        "monument": False},
    "Academy": {
        "group": "g_court",
        "unlock": "1 Established",
        #"infrastructure_req": "Library",
        "innate": "Influence +2",
        "efficient": "Alchemy",
        "monument": False},
    "Courtyard": {
        "group": "g_commerce",
        "root": True,
        "terrain": [],
        "unlock": "-",
        "infrastructure_req": "Town Square",
        "innate": "Craft +1; Faith +1",
        #"efficient": "Masonry",
        "monument": False},
    "Episcopal Court": {
        "group": "g_devotion",
        "unlock": "Rising Piety",
        #"infrastructure_req": "Town Square",
        "innate": "Faith +1; Reduce the first instance of Doubt each turn by 1, min 0",
        "efficient": "Courtyard",
        "monument": False},
    "Conditioning Field": {
        "group": "g_logistics",
        "unlock": "Rising Prowess",
        "innate": "Faith +1 while not at War; Armies gain Nimble",
        "efficient": ["Courtyard"],
        "monument": False},
    "Grand Tournament": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        "innate": "Reach +1; Armies gain Riposte & Improve Parry by +1", #3x in the Intrigue Phase: exchange 500 gold for Influence +1;
        "efficient": ["Coliseum"],
        "monument": False},
    "Apothecary": {
        "group": "g_devotion",
        "unlock": "Rising Piety",
        "innate": f'Gold +500; Gain Recover {RECOVER_BASE}, or improve Recover by +1',
        "efficient": ["Alchemy","Chandlery"],
        "monument": False},
    "Infirmary": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "innate": "Supply -500; Improve Recover by +1",
        "efficient": "Apothecary",
        "monument": False},
    "Supply Depot": {
        "group": "g_works",
        "unlock": "Rising Industry",
        "innate": "Upkeep -500; Supply -500; Armies and Garrisons within your Settlements gain Immune Strained",
        "efficient": "Masonry",
        "monument": False},
    "Artisan Workshop": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "Gold +1000; Faith +1",
        "efficient": "Market Square",
        "monument": False},
    "University": {
        "group": "g_court",
        "unlock": "2 Established",
        #"infrastructure_req": "Town Hall",
        "innate": "Influence +1 per Domain you are Rising; Max Influence +1 on every Envoy",
        "efficient": "Academy",
        "monument": False},
    "Collegium Archives": {
        "group": "g_court",
        "unlock": "2 Established",
        "infrastructure_req": "Library",
        "innate": "Influence +1 per Established Standing; Authority +1 on every Envoy",
        "efficient": "University",
        "monument": False},
    "Trade Guild": {
        "group": "g_works",
        "unlock": "Rising Industry",
        "innate": "Repair Timer -1; No Upkeep on Developed Infrastructure",
        "efficient": "Masonry",
        "monument": False},
    "Court Artists": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "Extort 500 twice; Targets of Extort from Court Artist gain Faith +1",
        "efficient": "Artisan Workshop",
        "monument": False},
    "Courier Network": {
        "group": "g_court",
        "unlock": "-",
        "natural": True,
        "innate": "In the Intrigue Phase: Authority -1 on one Envoy", # Once per Envoy Phase: select a Personal Action you performed this turn. Next turn, you may perform that action in the Empire Phase, but you send 1 fewer Envoy next turn.
        "efficient": ["Inn","Animal Husbandry"],
        "monument": False},
    "Toll House": {
        "group": "g_secrecy",
        "unlock": "Rising Cunning",
        "natural": True,
        "innate": "Extort 1000 when non-allied Army ends a Move action within your Province", # Once per turn: when an Army ends a Move action within your Province, Perform a Diplomacy action targeting that army's player; 
        "efficient": ["Caravanery"],
        "monument": False},
    "College of Engineering": {
        "group": "g_works",
        "unlock": "Established Industry",
        "innate": "Build Timer -1; No Upkeep on Sophisticated Infrastructure",
        "efficient": "Trade Guild",
        "monument": False},
    "Masons' Guild": {
        "group": "g_works",
        "unlock": "Established Industry",
        "innate": "Build Timer -1; No Upkeep on Prodigious Infrastructure",
        "efficient": "College of Engineering",
        "monument": False},
    "Secret Cellar": {
        "group": "g_secrecy",
        "unlock": "Rising Cunning",
        "natural": True,
        "innate": "Passed Cunning envoys Recoup 500 Gold; Endorsed Cunning envoys Recoup 1000 Gold",
        "efficient": ["Inn"],#"Courier Network"
        "monument": False},
    "Smuggler's Nook": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "Whenever a Bandit Camp within your Province Extorts, you Extort the Bandit Camp for half the amount",
        "efficient": ["Secret Cellar"],
        "monument": False},
    "Syndicate Hub": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "Both Bandit Camps & you have Authority +1 on Personal Cunning Envoys; Endorsed Foster Rebellion instead places Bandit Armies with 25 retinues",
        "efficient": ["Rogue Network"],
        "monument": False},
    "Rogue Network": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "Whenever any player or Bandit performs a Cunning action, it Extorts 1000 more from its target",
        "efficient": ["Smuggler's Nook"],
        "monument": False},
    "Black Market": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "Whenever another player Extorts or Recoups Gold, Extort 500 from that player; Extorts from a Black Market don't trigger Black Market",
        "efficient": ["Smuggler's Nook", "Corsair Haven"],
        "monument": False},
    "Dark Scriptorium": {
        "group": "g_secrecy",
        "unlock": "Rising Cunning",
        "innate": "Extort 300 anytime a player Opposes an Envoy of yours",
        "efficient": ["Alchemy"],
        "monument": False},
    "Forgery Workshop": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "At the end of the Tally Phase, if a Cunning Envoy you sent Failed, you may send another Cunning Envoy",
        "efficient": ["Dark Scriptorium"],
        "monument": False},
    "Toxicarium": {
        "group": "g_secrecy",
        "unlock": "Rising Cunning",
        "innate": "Weapons gain Poison; Endorsed Cunning envoys give an additional Doubt +1 to Target",
        "efficient": ["Alchemy", "Forgotten Catacombs", "Masonry"],
        "monument": False},
    "Charnel House": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "All Piety actions that give Doubt give an additional Doubt +1",
        "efficient": ["Toxicarium"],
        "monument": False},
    "Plague Pit": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "Indecisive, Aimless, & Recession effects are doubled for all players; Immune Wavering Devotion",#Cunning actions give an additional Doubt +1 to Target; 
        "efficient": ["Charnel House"],
        "monument": False},
    "Ossuary Crypt": {
        "group": "g_secrecy",
        "unlock": "Sovereign Cunning + Established Piety",
        "infrastructure_req": "Chapel",
        "innate": "No longer affected by all Public Order effects (positive or negative); Convert actions can't target you",#Convert actions can't target you
        "efficient": ["Plague Pit"],
        "monument": True},
    "Pilgrimage Site": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "innate": "Faith +1; Extort 500 from each other player without a Pilgrimage Site; each other player without a Pilgrimage Site gains Doubt +1", # 
        "efficient": "Reliquary",
        "monument": False},
    "Unforgotten Shrine": {
        "group": "g_devotion",
        "unlock": "Established Piety",
        "innate": "When your Piety actions give their target Faith, it gains Faith +1 more; when they give Doubt, it gains Doubt +1 more",
        "efficient": "Pilgrimage Site",
        "monument": False},
    "Beacon Towers": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "infrastructure_req": "Dirt Roads",
        "natural": True,
        "innate": "At the Start of the Empire Phase, you may select an Army within your Province and move it up to its modified Speed; Whenever a non-allied Army ends a Move action within your Province, you may immediately perform a Move action",
        "efficient": "Toll House",
        "monument": False},
    "Forgotten Catacombs": {
        "group": "g_secrecy",
        "unlock": "Rising Cunning",
        "innate": "Cunning actions targeting you can't be Endorsed",
        "efficient": "Inn",
        "monument": False},
    "Charcoal Burner": {
        "group": "g_logistics",
        "unlock": "-",
        "natural": True,
        "innate": "Gold +1000",
        "efficient": ["Butchery"],
        "monument": False},
    "Mill": {
        "group": "g_husbandry",
        "unlock": "Rising Industry",
        "natural": True,
        "innate": "Supply -500; Upkeep -500",
        "efficient": ["Bakery", "Forge", "Carpentry", "Masonry"],
        "monument": False},
    #"Kiln": {
    #    "group": "g_logistics",
    #    "unlock": "Rising Industry",
    #    "innate": "Natural; +500",
    #    "efficient": ["Forestry","Carpentry"],
    #    "builds_into": ["Charcoal Burner"],
    #    "monument": False},
    "Burgages": {
        "group": "g_works",
        "unlock": "Rising Cunning",
        "natural": True,
        "innate": "Faith +1; Upkeep -500",
        "efficient": ["Workyard"],
        "monument": False},
    "Levy Hall": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        #"infrastructure_req": "Garrison",
        "natural": True,
        "innate": "Speed +1; Supply -2000 while an Army is within Range 0 of a Settlement you Control",
        "efficient": "Smokehouse",
        "monument": False},
    "Baggage Train": {
        "group": "g_logistics",
        "unlock": "Sovereign Prowess",
        "infrastructure_req": "Bridges",
        "natural": True,
        "innate": "Supply -2000; At the Start of the Empire Phase, you may perform a Move action; Gain Immune Blocked",
        "efficient": "Levy Hall",
        "monument": True},
    "Siege Camp": {
        "group": "g_logistics",
        "unlock": "Rising Prowess",
        "innate": "Siege Timer -1; Armies gain Immune Strained during Lay Siege",
        "efficient": ["Carpentry","Furnace"],
        "monument": False},
    "Siege Works": {
        "group": "g_logistics",
        "unlock": "Rising Prowess",
        "innate": "Siege Timer -1; Siege Timers count down in Winter",
        "efficient": "Siege Camp",
        "monument": False},
    "Battery Park": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        "innate": "Your Siege Timers count down twice each turn instead of once",
        "efficient": ["Siege Works"],
        "monument": False},
    "Abatis Field": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        "innate": "Siege Timer -1; Settlements you Siege can't Sally Forth",
        "efficient": ["Battery Park"],
        "monument": False},
    "Citadel": {
        "group": "g_works",
        "unlock": "Established Industry",
        "infrastructure_req": "Stone Walls",
        "innate": "Siege Timer +4; May Muster an Army in a Settlement under Siege and its Muster Timers count down",
        "efficient": ["Supply Depot"],
        "monument": False},
    "Tenebrous Oubliette": {
        "group": "g_works",
        "unlock": "Established Cunning",
        "innate": "Reach +1; Whenever another player within your Province Supports, reduce that Support by 2",
        "efficient": ["Citadel"],
        "monument": False},
    "Black Hold": {
        "group": "g_works",
        "unlock": "Sovereign Cunning + Established Industry",
        "innate": "Reach +2; Whenever another player within your Province sends a Personal Envoy, it gains Authority -2",
        "efficient": ["Tenebrous Oubliette"],
        "monument": True},
    "Fortified Church": {
        "group": "g_works",
        "unlock": "Established Piety",
        "innate": "Garrisons gain Immune Fatigue; Immune Mounting Panic; Immune War Weariness; Immune Invasion",
        "efficient": ["Citadel"],
        "monument": False},
    "Sacristy Redoubt": {
        "group": "g_works",
        "unlock": "Sovereign Piety + Established Industry",
        "innate": "Whenever a Siege Timer against a Settlement you Control counts down, the sieging Army gains Fatigue +1; Your Settlements gain Immune Raze",
        "efficient": ["Fortified Church"],
        "monument": True},    
    "Castle Hall": {
        "group": "g_works",
        "unlock": "Established Prowess",
        "innate": "Doubt +1; Upkeep -1000; Tax Income is Doubled; Your Settlements gain Reach +2",
        "efficient": ["Citadel"],
        "monument": False},
    "War College": {
        "group": "g_logistics",
        "unlock": "Established Prowess",
        #"infrastructure_req": "Library",
        "innate": "Influence +2 while At War; Unlocks Sergeants for Muster",
        "efficient": "University",
        "monument": False},
    "Forge": {
        "group": "g_arms",
        "unlock": "Established Industry",
        "innate": "Craft +2; Unlocks Forged Tier Weapons",
        "efficient": "Blacksmith",
        "monument": False},
    "Skirmish Field": {
        "group": "g_arms",
        "unlock": "Rising Prowess",
        "innate": "Armies may be equipped with a Ranged and a Melee Weapon simultaneously; Unlocks Longbow regardless of Unlock Tier",
        "efficient": "Fletchery",
        "monument": False},
    "List Yard": {
        "group": "g_arms",
        "unlock": "Established Prowess",
        "innate": "Gain Immune Awkward; gain Florentine",
        "efficient": "Skirmish Field",
        "monument": False},
    "Fighting School": {
        "group": "g_arms",
        "unlock": "Established Prowess",
        "innate": "+1 to Strike; gain Immune Unwieldy",
        "efficient": "List Yard",
        "monument": False},
    "Court Armoury": {
        "group": "g_arms",
        "unlock": "Sovereign Industry",
        "innate": f"{PLANISHING}: Your to-Save can't be reduced beyond {CAP_THR}+; Unlocks Crafted Armor & Shield", #Supply -500; 
        "efficient": "Gilded Foundry",
        "monument": True},
    "Serfdom": {
        "group": "g_works",
        "unlock": "Sovereign Cunning",
        "infrastructure_req": "Magistrate's Hall",
        "natural": True,
        "innate": "Build Timer -2; Gold +500 per Doubt",
        "efficient": ["Storehouse"],
        "monument": True},
    "Office of Works": {
        "group": "g_works",
        "unlock": "Sovereign Industry",
        "infrastructure_req": "Aqueducts",
        "natural": True,
        "innate": "Siege Timer +2; Build Timer -2; Settlements & allied Armies inside them are not affected by 'Settlements being Besieged' restrictions",
        "efficient": ["Masons' Guild"],
        "monument": True},
    "Royal Pavilion": {
        "group": "g_logistics",
        "unlock": "Sovereign Prowess",
        "innate": "Armies gain Immune Strained; Improve Parry by +1; Deadly, & Cleave also trigger Focused Strikes on an Unmodified 8+",
        "efficient": ["Grand Tournament","Fighting School"],
        "monument": True},
    "Imperial Palace": {
        "group": "g_works",
        "unlock": "Sovereign Prowess + Established Industry",
        "infrastructure_req": "Keep",
        "innate": "If your Envoy would fail, it passes instead; Each Empire Phase, each non-allied player with a lower Prowess value gains Doubt +2",
        "efficient": "Castle Hall",
        "monument": True},
    "Artillery Park": {
        "group": "g_logistics",
        "unlock": "Sovereign Prowess + Established Industry",
        #"infrastructure_req": "Magistrate's Hall",
        "innate": "Siege Timers ignore Wooden & Stone Walls; Unlocks Arquebus",
        "efficient": "Abatis Field",
        "monument": True},
    "Ministry of Military Strategy": {
        "group": "g_logistics",
        "unlock": "Sovereign Prowess",
        "infrastructure_req": "Library",
        "innate": "Always gains Seize the Initiative, and your opponent doesn't; max initiative is increased to 3; Gain Drilled",
        "efficient": "War College",
        "monument": True},
    "Thieves' Guild": {
        "group": "g_secrecy",
        "unlock": "Sovereign Cunning + Established Industry",
        "innate": "Whenever you Extort 500 or more, Gold +500",
        "efficient": ["Black Market"],
        "monument": True},
    "Senate Hall": {
        "group": "g_court",
        "unlock": "Sovereign Piety",
        "infrastructure_req": "Library",
        "innate": "Faith +1; Influence +1 per other player; In the Intrigue Phase, you may Condemn an At War player's Envoy or Endorse an Ally's Envoy",
        "efficient": "Embassy",
        "monument": True},
    "Papal Palace": {
        "group": "g_devotion",
        "unlock": "Sovereign Piety + Established Industry",
        "infrastructure_req": "Cathedral",
        "innate": "Each Empire Phase, Tithe each other player with lower Piety, resolved in the Extort step; You no longer pay cost for Piety Envoys",
        "efficient": ["Monastery"],
        "monument": True},
    "Inquisitorial Palace": {
        "group": "g_devotion",
        "unlock": "Sovereign Piety + Rising Cunning",
        "infrastructure_req": "Cathedral",
        "innate": "Doubt +1; Unlocks Grand Vizier which uses your Piety Value instead of Cunning; All player actions that cause Doubt are increased by 1",
        "efficient": "Execution Dock",
        "monument": True},
    "Preceptory of the Knight's Templar": {
        "group": "g_devotion",
        "unlock": "Sovereign Piety + Established Prowess",
        "infrastructure_req": "Keep",
        "innate": f"While a Sacred War is active, gain 3 Faith during each Empire Phase; Unlocks Knight's Templar for Muster", #Armies gain {CRUSADER}: Automatically pass the first Panic Check of every Battle. 
        "efficient": "Hospitaller",
        "monument": True},
    "Exalted Basilica": {
        "group": "g_devotion",
        "unlock": "Sovereign Piety",
        "infrastructure_req": "Cathedral",
        "innate": "Gold +300 per Faith; At the Start of the Empire Phase, you may perform an Endorsed Spread Truth",
        "efficient": "Unforgotten Shrine",
        "monument": True},
    "Manor House": {
        "group": "g_husbandry",
        "unlock": "Sovereign Industry",
        "infrastructure_req": "Aqueducts",
        "natural": True,
        "innate": "Gold +100 per active Natural Holding",
        "efficient": "Natural",
        "monument": True},
    "Aristocratic Court": {
        "group": "g_commerce",
        "unlock": "Sovereign Industry + Rising Cunning",
        "infrastructure_req": "Magistrate's Hall",
        "innate": "Whenever another player performs a Diplomacy action targeting another player, Extort 3000 from both players",
        "efficient": ["Court Artists","Esteemed Bank"],
        "monument": True},
    "Studium Generale": {
        "group": "g_court",
        "unlock": "3 Established",
        "infrastructure_req": "Library",
        "innate": "Influence +1 per Established Standing; May gain one Sovereign Domain effect without spending the Domain Points",
        "efficient": "Collegium Archives",
        "monument": True},
    "Outlaw Rookery": {
        "group": "g_secrecy",
        "unlock": "Sovereign Cunning",
        "innate": "Each Empire Phase, Extort the whole Treasury of every Bandit Camp within your Province; Bandit Camps and Armies within your Province don't target you and instead target another player at random", #gain Immune Uprising (your Uprising spawns no Bandit Camps); 
        "efficient": "Syndicate Hub",
        "monument": True},
    "Advanced Blast Furnace": {
        "group": "g_arms",
        "unlock": "Sovereign Industry + Rising Prowess",
        "infrastructure_req": "Aqueducts",
        "innate": "Craft +5; Supply -1000; Unlocks Crafted Weapons",
        "efficient": "Master Workshop",
        "monument": True},
    "Cipher Chamber": {
        "group": "g_secrecy",
        "unlock": "Established Cunning",
        "innate": "At the Start of the Empire Phase, choose one: select an army you did not select last turn; that army gains Blocked; or select any active Timer you did not select last turn; increase it by 2",
        "efficient": "Forgery Workshop",
        "monument": False},
    "Whispering Undercroft": {
        "group": "g_secrecy",
        "unlock": "Sovereign Cunning",
        "innate": "In the Intrigue Phase, choose a Personal Envoy: its sender must declare the specific action & target they would Perform if it passes (including sub-Actions). If it passes, they must Perform that declared action at the declared target; You cast all of your votes in the Tally Phase",
        "efficient": "Cipher Chamber",
        "monument": True},
    "Outrider Intercept Post": {
        "group": "g_secrecy",
        "unlock": "Sovereign Cunning + Rising Prowess",
        "infrastructure_req": "Stone Roads",
        "natural": True,
        "innate": "Every Skirmish, you may force your opponent to reveal their Tactic Card they selected before you select your own",
        "efficient": ["Beacon Towers"],
        "monument": True},
    "Emporium": {
        "group": "g_commerce",
        "unlock": "Established Industry",
        "innate": "Gold +1000; Trade Partners gain Craft +3",
        "efficient": ["Cooperage"],
        "monument": False},
    "Port Authority": {
        "group": "g_commerce",
        "unlock": "Sovereign Industry",
        "infrastructure_req": "Magistrate's Hall",
        "innate": "Craft +10; Gold +100 per Craft",
        "efficient": ["Emporium"],
        "monument": True},
    "Fleet Anchorage": {
        "group": "g_logistics",
        "unlock": "Sovereign Prowess + Established Industry",
        "innate": "If your Army begins a Move adjacent to a Water Territory, it may end that Move adjacent to any Water Territory connected to it; If your Army wins a Battle, it Reinforces 10 Retinues of its current type at once (no cost or Muster Timer, up to the Army's Retinue cap)",
        "efficient": ["Shipyard"],
        "monument": True}
}
# Deprecated Holdings ("deprecated": True) stay written above but leave play: every reader of NODES / NODES
# (board, trees, cards, wiki, sim) skips them. Saved boards holding one count it for nothing.
DEPRECATED_NODES = {_n: NODES.pop(_n) for _n in [_k for _k, _v in NODES.items() if _v.get("deprecated")]}
# builds_into is derived: exactly the Holdings that name this one in their `efficient` (Mastery Chain).
for _bn, _bv in NODES.items():
    _bv["builds_into"] = [_c for _c, _cv in NODES.items()
                          if _bn in ([_cv["efficient"]] if isinstance(_cv.get("efficient"), str) else (_cv.get("efficient") or []))]

# ── HOLDING GROUPS — engine ids neutral; rename a group's label here only. ──
# Each Holding carries "group" (id); "type" is derived from the label below, so every
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
for _hn, _hv in {**NODES, **DEPRECATED_NODES}.items():
    _hv["type"] = "Monument" if _hv.get("monument") else HOLDING_GROUPS[_hv["group"]]
# ── RARITY SCOPE — how many of one Holding / Infrastructure may exist ─────────
#   Settlement = one per Settlement · Empire = one per player · Realm = one per game
# Raw Materials are Settlement, Monuments and Wonders are Realm, everything else is Empire.
# A Realm piece is taken once any player has placed it (under construction included).
SCOPES = ("Settlement", "Empire", "Realm")
SCOPE_BY_TYPE = {"Raw Materials": "Settlement", "Monument": "Realm"}
for _hn, _hv in {**NODES, **DEPRECATED_NODES}.items():
    _hv.setdefault("scope", SCOPE_BY_TYPE.get(_hv["type"], "Empire"))
# Lines: flavour labels for paths through the graph; a Holding may sit in several.
LINE_LABELS = {
    "l_engineering": {"label": "Engineering", "members": ["Quarry", "Masonry", "Trade Guild", "College of Engineering", "Office of Works"]},
    "l_labor": {"label": "Labor", "members": ["Common Land", "Salt Works", "Workyard", "Burgages", "Census Hall", "Storehouse", "Serfdom"]},
    "l_fortification": {"label": "Fortification", "members": ["Masonry", "Granary", "Supply Depot", "Citadel", "Castle Hall", "Imperial Palace"]},
    "l_maritime": {"label": "Maritime", "members": ["Fishmongery", "Harbor", "Fish Weir", "Cooperage", "Emporium", "Port Authority"]},
    "l_armada": {"label": "Armada", "members": ["Harbor", "Ropewalk", "Sail Loft", "Shipyard", "Fleet Anchorage"]},
    "l_piracy": {"label": "Piracy", "members": ["Harbor", "False Lights", "Corsair Haven", "Black Market", "Thieves' Guild"]},
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
    "l_smuggling": {"label": "Smuggling", "members": ["Inn", "Courier Network", "Smuggler's Nook", "Rogue Network", "Syndicate Hub", "Outlaw Rookery"]},
    "l_thievery": {"label": "Thievery", "members": ["Smuggler's Nook", "Black Market", "Thieves' Guild"]},
    "l_whispers": {"label": "Whispers", "members": ["Academy", "University", "Forgery Workshop", "Cipher Chamber", "Whispering Undercroft"]},
    "l_pestilence": {"label": "Pestilence", "members": ["Secret Cellar", "Forgotten Catacombs", "Alchemy", "Toxicarium", "Charnel House", "Plague Pit"]},
    "l_watch": {"label": "Watch", "members": ["Caravanery", "Toll House", "Beacon Towers", "Outrider Intercept Post"]},
    "l_vintage": {"label": "Vintage", "members": ["Vineyard", "Winery", "Orchard", "Cidery"]},
    "l_hearth": {"label": "Hearth", "members": ["Apiary", "Meadery", "Bakery", "Mill"]},
    "l_spice": {"label": "Spice", "members": ["Herb Garden", "Spice Merchant"]},
    "l_patronage": {"label": "Patronage", "members": ["Courtyard", "Market Square", "Weavery", "Artisan Workshop", "Court Artists", "Aristocratic Court"]},
    "l_banking": {"label": "Banking", "members": ["Market Square", "Merchant Quarter", "Money Lending", "Aristocratic Court"]},
    "l_pilgrimage": {"label": "Pilgrimage", "members": ["Apiary", "Chandlery", "Reliquary", "Pilgrimage Site", "Exalted Basilica"]},
    "l_cloister": {"label": "Cloister", "members": ["Masonry", "Abbey", "Monastery", "Papal Palace"]},
    "l_fastday": {"label": "Fast Day", "members": ["Fishmongery", "Stew Pond", "Priory", "Abbey", "Monastery", "Papal Palace"]},
    "l_inquisition": {"label": "Inquisition", "members": ["Courtyard", "Episcopal Court", "Interrogation Chambers", "Execution Dock", "Inquisitorial Palace"]},
}

def lines_of(name):
    """Line labels containing this Holding."""
    return [d["label"] for d in LINE_LABELS.values() if name in d["members"]]

# What a Holding needs besides Standing: infrastructure_req (settlement infrastructure / tags) and placement next
# to an `efficient` parent. Outputs read these instead of hard-coding the field.
REQ_KEY   = "infrastructure_req"
REQ_LABEL = "Infrastructure Req"
# Section/sort order for node `type` (tiles, wiki, compendium).
TYPE_ORDER = list(HOLDING_GROUPS.values()) + ["Monument"]
# Display name for the `efficient` field (the data key stays `efficient`).
CHAIN_TERM = "Mastery Chain"
# Display name for a Holding / Infrastructure set inactive for unpaid upkeep (Insolvency). Rules print it via {{VAL:SHUTTER_TERM}}.
SHUTTER_TERM = "Shuttered"
# Cost words. UPKEEP_TERM: what Holdings and Infrastructure cost each Empire Phase; SUPPLY_TERM: what Armies cost.
# Rules print them via {{VAL:UPKEEP_TERM}} / {{VAL:SUPPLY_TERM}}. Effects read "<UPKEEP_TERM> -X" (lowers Holding and
# Infrastructure costs), "No <UPKEEP_TERM> on <Tier> Infrastructure", and "<SUPPLY_TERM> -X" (lowers Army costs).
UPKEEP_TERM = "Upkeep"
SUPPLY_TERM = "Supply"
# Display name for Pursuits (singular, plural). Data keys, file names and wiki URLs keep "pursuit".
PURSUIT_TERM = ("Holding", "Holdings")

def node_parents(name, nodes=None):
    """Prerequisite Holdings of `name` (names present in `nodes`): its efficient parent(s), any one of which
    allows placement."""
    nodes = NODES if nodes is None else nodes
    d = nodes.get(name, {}) or {}
    e = d.get("efficient")
    e = [e] if isinstance(e, str) else list(e or [])
    return [p for p in e if p in nodes]
def get_data(mode="renown"):
    """Return the node set for a game mode. 'escalation' = the combat subset
    (nodes carrying an 'escalation' key); 'renown' = everything."""
    if mode == "escalation":
        return {k: v for k, v in NODES.items() if "escalation" in v}
    return dict(NODES)

# One-line Monument summaries (playstyle reference). The gist of each Monument's
# innate text, for choosing a playstyle (no numbers) — edit the Monument first, then this line.
MONUMENT_SUMMARY = {
    "Ossuary Crypt":                      "Piety Actions Spread Doubt, Target Anyone with Piety",
    "Baggage Train":                      "Cheaper Armies, Can't be Blocked",
    "Serfdom":                            "Gold from Doubt, Builds Faster",
    "Office of Works":                    "Ignores Siege Restrictions, Harder to Siege, Builds Faster",
    "Royal Pavilion":                     "Unyielding, Deadlier Armies",
    "Imperial Palace":                    "Weaker Rivals Gain Doubt, Your Envoys Can't Fail",
    "Artillery Park":                     "Faster Sieges, Unlocks Gunpowder",
    "Ministry of Military Strategy":      "Professional Tactical Army",
    "Thieves' Guild":                     "Profits from Every Extort",
    "Senate Hall":                        "Faith & Influence Income, Sways Envoys for Allies",
    "Papal Palace":                       "Free Piety Envoys, Tithes Less Pious Rivals",
    "Inquisitorial Palace":               "Amplifies All Doubt, Piety-Powered Grand Vizier",
    "Preceptory of the Knight's Templar": "Unlocks Knight's Templar, Faith from Sacred War",
    "Exalted Basilica":                   "Spreads Truth Every Turn",
    "Manor House":                        "Gold from Natural Holdings",
    "Aristocratic Court":                 "Extorts Both Sides of Rivals' Diplomacy",
    "Studium Generale":                   "Influence from Broad Standing, Free Sovereign Effect",
    "Outlaw Rookery":                     "Your Bandits Work for you.",
    "Advanced Blast Furnace":             "Cheaper Supply, Best Weapons",
    "Whispering Undercroft":              "Votes Last, Forces Rivals to Show Their Hand",
    "Outrider Intercept Post":            "Sees Opponents' Tactic Cards First",
    "Port Authority":                     "Gold from Craft",
    "Fleet Anchorage":                    "Armies Sail Between Waters, Reinforce on Victory",
    "Polish House":                       "Massive Income... and Attention",
    "Marshal Tiltyard":                   "Shock Cavalry",
}

# One-line Wonder summaries (playstyle reference). The gist of each Wonder's
# empire_bonus, for choosing a playstyle (no numbers) — edit the Wonder first, then this line.
WONDER_SUMMARY = {
    "Colossus":              "Backs Its Own Prowess Envoys, Faster Armies & Sieges, Immune Blunder",
    "The Grand Exchange":    "Trades with More Players, Double Trade Income",
    "The Eternal Sepulchre": "Public Order Never Falls Low, Wider Reach",
    "High Chancery":         "Endorses One of Its Own Envoys",
}

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
        'summary': 'Starts with Siege Camp',
        'mechanic': 'You begin the game with a Siege Camp (no Ward, Natural).',
        'pair': 'Artillery Park, Ministry of Military Strategy',
        'complement': 'Baggage Train',
    },
    'The Boundless Steppe': {
        'final_cut': True,
        'inspiration': 'Mongol Horde',
        'feel': 'Fast',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Horsemasters',
        'summary': 'Starts with a Stable',
        'mechanic': "You begin the game with a Stable (no Ward, Natural).",
        'pair': 'Baggage Train, Marshal Tiltyard',
        'complement': 'Outrider Intercept Post',
    },
    'The Bandit King': {
        'final_cut': True,
        'inspiration': 'Brigands',
        'feel': 'Scrappy',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic_name': 'Friends in Low Places',
        'summary': "Starts with Smuggler's Nook; controls a Bandit Camp; no Piety or Prowess Holdings",
        'mechanic': "You begin the game with a Smuggler's Nook (no Ward, Natural). At the Start of the Empire Phase, you may control one Bandit Camp outside your Territory. When a Bandit Camp is spawned, you may place it in your Outlaw Country instead. You cannot Build Holdings which require Piety or Prowess Standing.",
        'pair': "Outlaw Rookery, Thieves' Guild",
        'complement': 'Outrider Intercept Post',
    },
    'The Crowned Star': {
        'final_cut': True,
        'inspiration': 'Reigning Sovereign',
        'feel': 'Sovereign Voice',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'The Monarch',
        'deprecated': True,   # its Council-vote mechanic has nothing to act on under PHASE_REFORM
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
        'summary': 'Immune to Intercept Caravan; starts with a Harbor',
        'mechanic': "Other players can't perform Intercept Caravan on you. You begin the game with a Harbor (no Ward, Natural).",
        'pair': "Port Authority, Thieves' Guild",
        'complement': 'Outrider Intercept Post',
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
        'pair': 'Senate Hall, Aristocratic Court',
        'complement': 'Whispering Undercroft',
    },
    'The Eternal Court': {
        'final_cut': True,
        'inspiration': 'Byzantine Empire',
        'feel': 'Patient & Reserved',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Patient Court',
        'summary': 'Banks Influence; up to 5 per Envoy in Zenith',
        'mechanic': "Your unspent Influence isn't discarded in the Rest Phase. While the Era is Zenith, your Max Influence is 5 on every Envoy.",
        'pair': 'Studium Generale, Senate Hall',
        'complement': 'Whispering Undercroft',
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
        'pair': 'Imperial Palace, Royal Pavilion',
        'complement': 'Ministry of Military Strategy',
    },
    'The Gilded Crescent': {
        'final_cut': True,
        'inspiration': 'Moorish Caliphate',
        'feel': 'Egalitarian',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Prosperity For All',
        'summary': 'Starts with an Inn',
        'mechanic': "You begin the game with an Inn (no Ward, Natural).",
        'pair': 'Manor House, Port Authority',
        'complement': 'Office of Works',
    },
    'The Gilded Path': {
        'final_cut': False,
        'inspiration': 'Great Income',
        'feel': 'Rich Trader',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic_name': 'Luxury Trades',
        'summary': "Starts with Artisan Workshop; can't refuse trade",
        'mechanic': "You begin the game with an Artisan Workshop (no Ward, Natural). You can't refuse a Trade Agreement.",
        'pair': 'Port Authority, Aristocratic Court',
        'complement': "Thieves' Guild",
    },
    'The Hermit Crown': {
        'final_cut': False,
        'deprecated': True,
        'inspiration': 'Independent',
        'feel': 'Independent',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic_name': 'Independent, but Ambitious',
        'summary': 'Always Abstains; 2 Influence to sway your Envoys by 1; Personal Envoys +1; no votes or Council Envoys',
        'mechanic': "You Abstain on every vote on other players' Envoys, and other players must spend 2 Influence to affect your Envoys by 1. Your Personal Envoys have Authority +1. You can't vote nor send Council Envoys.",
        'pair': 'Studium Generale, Whispering Undercroft',
        'complement': 'Manor House',
    },
    'The Illuminated Order': {
        'final_cut': True,
        'inspiration': 'Scholarly',
        'feel': 'Knowledge is Power',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Knowledge is Power',
        'summary': 'Influence +1 per 3 Holdings',
        'mechanic': 'Influence +1 per 3 Holdings you have.',
        'pair': 'Studium Generale, Office of Works',
        'complement': 'Senate Hall',
    },
    'The Iron Faith': {
        'final_cut': True,
        'inspiration': 'Crusader States',
        'feel': 'Piously Resolute',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Fortress of Faith',
        'summary': 'Sieges against you +2 while Public Order 3+',
        'mechanic': 'While your Public Order is 4 or higher, Lay Siege actions targeting you have Siege Timer +3.',
        'pair': "Office of Works, Preceptory of the Knight's Templar",
        'complement': 'Papal Palace',
    },
    'The Iron Shore': {
        'final_cut': True,
        'inspiration': 'Norse',
        'feel': 'Scavenger',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Scavengers',
        'summary': 'Spoils win or lose; extorts 2000 from whoever Razes you',
        'mechanic': 'You collect the Spoils of War whether you win or lose a Battle. When a Raze action targets you, Extort 2000 from the attacker.',
        'pair': 'Baggage Train, Advanced Blast Furnace',
        'complement': 'Royal Pavilion',
    },
    'The Iron Throne': {
        'final_cut': True,
        'inspiration': 'Defensive',
        'feel': 'Defensive, Impenetrable',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Unimpeachable',
        'summary': "Starts with a Citadel; your Alliance can't Declare War",
        'mechanic': "You begin the game with a Citadel (no Ward, Natural). You (and your Alliance) can't perform Declare War or Sacred War actions.",
        'pair': 'Office of Works, Papal Palace',
        'complement': 'Exalted Basilica',
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
        'pair': "Port Authority, Thieves' Guild",
        'complement': 'Aristocratic Court',
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
        'pair': 'Exalted Basilica, Inquisitorial Palace',
        'complement': 'Papal Palace',
    },
    'The Tunnellers': {
        'final_cut': True,
        'inspiration': 'Dwarves',
        'feel': 'Mountain Passers',
        'difficulty': 'Low',
        'strength': 'Low',
        'mechanic_name': 'Tunnellers',
        'summary': 'Move through Mountains; starts with a Furnace',
        'mechanic': 'You treat mountain Territory as grassland for movement, and begin the game with a Furnace Raw-Material Holding (no Ward, Natural).',
        'pair': 'Advanced Blast Furnace, Office of Works',
        'complement': 'Artillery Park',
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
        'pair': "Preceptory of the Knight's Templar, Exalted Basilica",
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
        'mechanic': "You can't Declare War, enter Military Alliances, perform Cunning actions, or build Holdings that require Prowess or Cunning Standing. Gain 100 gold per total Craft level across all active sources.",
        'pair': 'Port Authority, Manor House',
        'complement': 'Polish House',
    },
    'The Winter Wolves': {
        'final_cut': True,
        'inspiration': 'Vikings',
        'feel': 'Aggressive, Parasitic',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Pillagers',
        'summary': 'At war, Armies extort their upkeep from at-war Settlements; no Alliances',
        'mechanic': "While At War, your Armies within reach of at-war Settlements Extort their upkeep from that Settlement's owner. You cannot join an alliance.",
        'pair': 'Baggage Train, Royal Pavilion',
        'complement': 'Outlaw Rookery',
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
        'pair': 'Outrider Intercept Post, Ministry of Military Strategy',
        'complement': 'Baggage Train',
    },
    'The Bloodied Cross': {
        'final_cut': True,
        'inspiration': 'Crusading Sect',
        'feel': 'Sacred War Without End',
        'difficulty': 'Medium',
        'strength': 'High',
        'mechanic_name': 'Prophets of War',
        'summary': 'Sacred War at Rising Piety, uncapped; no Convert',
        'mechanic': "You may Sacred War at Rising Piety instead of Sovereign Piety, with no cap on active Sacred Wars. Each other player gains Doubt +1 each Empire Phase per Sacred War you're on. You can't perform Convert or Cunning actions.",
        'pair': "Preceptory of the Knight's Templar, Marshal Tiltyard",
        'complement': 'Exalted Basilica',
    },
    'The Blazing Standard': {
        'final_cut': False,
        'inspiration': 'Teutonic Knight',
        'feel': 'Crusader Feel',
        'difficulty': 'Medium',
        'strength': 'High',
        'mechanic_name': 'Burning Cross',
        'summary': "Starts with a Preceptory; must field 25 Knight's Templar",
        'mechanic': "You begin the game with a Preceptory of the Knight's Templar (no Ward, Natural). When you Declared War via Sacred War, that player takes a Panic Check at the start of every Battle, after lines are formed. During Envoy Declaration, if you don't have an Army of 25 Knight's Templar, you must send a Prowess Envoy; if it passes, you must muster an Army until it holds 25 Knight's Templar Retinues.",
        'pair': 'Royal Pavilion, Imperial Palace',
        'complement': 'Exalted Basilica',
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
        'pair': 'Senate Hall, Studium Generale',
        'complement': 'Aristocratic Court',
    },
    'The Luminous Court': {
        'final_cut': False,
        'inspiration': 'Renaissance',
        'feel': 'Civic Soft Power',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic_name': 'Arts & Humanities / Hearts & Minds',
        'summary': 'Civic Holdings upgraded; no Craft Holdings',
        'mechanic': "You can't build Industry Holdings. Your Holdings which require Piety have Craft +2 and cost no Upkeep. You must accept a Peace Treaty if one is offered.",
        'pair': 'Exalted Basilica, Office of Works',
        'complement': 'Studium Generale',
    },
    'The Grand Compact': {
        'final_cut': True,
        'inspiration': 'Hanseatic League',
        'feel': 'Peace Through Trade',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic_name': 'Mercantile Pact',
        'summary': 'Trade partners must join your war or cut trade',
        'mechanic': 'Players who sign a Trade Agreement with you are considered to be in a Defensive Alliance with you. You cannot perform the Declare War action.',
        'pair': 'Port Authority, Aristocratic Court',
        'complement': 'Manor House',
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
        'pair': 'Ossuary Crypt, Royal Pavilion',
        'complement': "Preceptory of the Knight's Templar",
    },
    'The Sublime Gate': {
        'final_cut': True,
        'inspiration': 'Ottoman Empire',
        'feel': 'Mercantile Military',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic_name': 'Integrated Arms',
        'summary': "Musters from Trade Partners' Holdings",
        'mechanic': "When you perform a Muster action, you may muster Retinues and equipment from your Trade Partners' Holdings.",
        'pair': 'Advanced Blast Furnace, Artillery Park',
        'complement': 'Port Authority',
    },
    'The Velvet Hand': {
        'final_cut': True,
        'inspiration': 'Patrons',
        'feel': 'Generous Sponsor',
        'difficulty': 'Medium',
        'strength': 'Medium',
        'mechanic_name': 'Friends in High Places',
        'summary': 'Rewards players who support your Envoys',
        'mechanic': 'Each Empire Phase, a player who supported a Personal Envoy you sent that passed gains Faith +1; if that Personal Envoy was endorsed, they Extort 500 gold from you.',
        'pair': 'Aristocratic Court, Senate Hall',
        'complement': 'Imperial Palace',
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
        'pair': 'Ossuary Crypt, Inquisitorial Palace',
        'complement': 'Outlaw Rookery',
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
        'pair': 'Aristocratic Court, Manor House',
        'complement': 'Baggage Train',
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
        'pair': "Whispering Undercroft, Thieves' Guild",
        'complement': 'Senate Hall',
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
        'pair': 'Whispering Undercroft, Studium Generale',
        'complement': 'Outrider Intercept Post',
    },
    
    'The Illusionists': {
        'deprecated': True,   # its mechanic is Diplomacy Envoys, which PHASE_REFORM removes
        'final_cut': False,
        'inspiration': 'Political Masterminds',
        'feel': 'Subterfuge, Deception',
        'difficulty': 'High',
        'strength': 'High',
        'mechanic_name': 'Double Speak',
        'summary': 'Diplomacy Envoys run on Cunning Standing and may become Cunning actions; no wars or Alliances',
        'mechanic': "Your Diplomacy Envoys start at Authority equal to your Cunning rank, and your Max Influence on Diplomacy Envoys is your Cunning rank. Whenever your Personal Diplomacy Envoy passes or is endorsed, you may instead perform a Cunning action. You can't perform Declare War or Sacred War actions, and you can't be a member of an Alliance.",
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
        'mechanic': "Authority +1 on your Cunning actions targeting a player with Public Order 2 or higher. You begin the game with a Secret Cellar (no Ward, Natural). You can't be in an Alliance or participate in the Diplomacy Phase. A Prowess Envoy you send can't fail or be condemned & will instead pass. You cannot put Domain Points into Piety, nor have more than 6 in Industry.",
        'pair': 'Outlaw Rookery, Marshal Tiltyard',
        'complement': 'Outrider Intercept Post',
    },
    "The Squatters' Crown": {
        'final_cut': False,
        'inspiration': 'Insurgents',
        'feel': 'Mobile Occupier',
        'difficulty': 'High',
        'strength': 'Medium',
        'mechanic_name': 'Occupy',
        'summary': 'Armies Occupy Settlements instead of holding them',
        'mechanic': "You start with an additional Army; all your Armies begin inside your Settlements. While you're outside a Settlement, you don't control it — to collect taxes or use its Holdings, end your turn inside it. To Occupy a Settlement, begin a Battle adjacent to it as if Sieging, but instead Battle the Garrison and any Armies at War with you or sharing its owner; if you win (or there's no force to fight), move inside. In the Upkeep Phase, you only pay upkeep on your Armies. You count as having all Infrastructure of your Occupied Settlements, and always count as having Craft 5.",
        'pair': 'Artillery Park, Baggage Train',
        'complement': 'Office of Works',
    },
    'The Wandering Crown': {
        'final_cut': False,
        'inspiration': 'Nomadic',
        'feel': 'Nomads',
        'difficulty': 'High',
        'strength': 'Medium',
        'mechanic_name': 'Wandering Nomads',
        'summary': 'Armies are Settlements; no Infrastructure, no upkeep',
        'mechanic': "Your Armies function as Settlements — a Band, Tribe, or Horde, upgraded accordingly — count as Settlements with Reach 3, and each has a Muster Field. You may have one additional Army per Era, starting with two. Your Armies don't require troops to exist and can't be besieged. You can't build Infrastructure, but may build Holdings; Raw Material Holdings within your Reach are always active and take no Settlement Ward. You may trade so long as your border touches another player's. You may begin a new Army adjacent to any existing Army with a Settle or Muster action. When an Army is destroyed, so is its Settlement. Nomads pay no upkeep.",
        'pair': 'Outrider Intercept Post, Artillery Park',
        'complement': 'Advanced Blast Furnace',
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
        'pair': 'Senate Hall, Studium Generale',
        'complement': 'Aristocratic Court',
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
        'pair': 'Outrider Intercept Post, Marshal Tiltyard',
        'complement': 'Royal Pavilion',
    },
    'The Yew Heart': {
        'final_cut': True,
        'inspiration': 'English Longbows',
        'feel': 'Skilled Volleys',
        'difficulty': 'Low',
        'strength': 'Medium',
        'mechanic_name': 'Archery is a Way of Life',
        'summary': 'Ranged +1 to Strike; no heavy plate or shields',
        'mechanic': "You begin the game with a Fletchery (no Ward, Natural). Your Armies must always have a ranged weapon, and Ranged Weapons gain +1 to Strike. Your Armies can't equip full plate, gothic plate, or shields.",
        'pair': 'Royal Pavilion, Ministry of Military Strategy',
        'complement': 'Outrider Intercept Post',
    },
}
# Deprecated factions ('deprecated': True) stay written above but leave play: lifted out of FACTIONS, and their mechanic
# names dropped from every culture's mechanic_name list (the board offers a culture's factions from that list).
DEPRECATED_FACTIONS = {_f: FACTIONS.pop(_f) for _f in [_k for _k, _v in FACTIONS.items() if _v.get("deprecated")]}
_dep_mech = {_v.get("mechanic_name") for _v in DEPRECATED_FACTIONS.values()} - {_v.get("mechanic_name") for _v in FACTIONS.values()}
for _c in CULTURES.values():
    if isinstance(_c.get("mechanic_name"), list): _c["mechanic_name"] = [_m for _m in _c["mechanic_name"] if _m not in _dep_mech]


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
 'Town Square': {'upkeep': 0,
                   'upkeep_frequency': '—',
                   'empire_bonus': 'Craft +2',
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
                  'empire_bonus': "Siege Timer +1; Authority -2 on Raze actions from players targeting you; Authority -1 on Bandit Cunning actions targeting you",
                  'tier': 'Primitive',
                  'build_time': 1,
                  'requirement': 'None'},
 'Stone Roads': {'upkeep': 200,
                 'upkeep_frequency': 'each Empire Phase',
                 'empire_bonus': 'If you start a Move action within your Province, gain additional Speed +2',
                 'tier': 'Developed',
                 'build_time': 2,
                 'requirement': 'Dirt Roads'},
 'Town Hall': {'upkeep': 200,
               'upkeep_frequency': 'each Empire Phase',
               'empire_bonus': 'Upkeep -500',
               'tier': 'Developed',
               'build_time': 2,
               'requirement': 'Town Square'},
'Garrison': {'upkeep': 200,
                  'upkeep_frequency': 'each Empire Phase',
                  'empire_bonus': "Each of your Settlements gains Muster Limit +5; Your Settlements gain Garrisons & Presence",
                  'tier': 'Developed',
                  'build_time': 2,
                  'requirement': 'Muster Field'},
 'Stone Walls': {'upkeep': 200,
                 'upkeep_frequency': 'each Empire Phase',
                 'empire_bonus': "Siege Timer +1; Authority -2 on Destabilize actions from players targeting you; Authority -1 on Bandit Cunning actions targeting you",
                 'tier': 'Developed',
                 'build_time': 2,
                 'requirement': 'Wooden Walls'},
'March-Tower': {'upkeep': 300,
               'upkeep_frequency': 'each Empire Phase',
               'empire_bonus': "Instead of performing a Move action, you may have a Garrison Battle a Bandit Camp, Bandit Army, or an Army you're At War with within its Presence",
               'tier': 'Sophisticated',
               'build_time': 3,
               'requirement': 'Garrison'},
'Bridges': {'upkeep': 0,
             'upkeep_frequency': '—',
             'empire_bonus': 'Armies cross Water Territory at full movement within your Province; Stone Roads may be built over '
                             'Water',
             'tier': 'Sophisticated',
             'build_time': 3,
             'requirement': 'Stone Roads'},
 'Library': {'upkeep': 300,
             'upkeep_frequency': 'each Empire Phase',
             'empire_bonus': "Influence +2; Max Influence +1",
             'tier': 'Sophisticated',
             'build_time': 3,
             'requirement': 'Town Hall'},
'Chapel': {'upkeep': 300,
             'upkeep_frequency': 'each Empire Phase',
             'empire_bonus': 'Faith +1',
             'tier': 'Sophisticated',
             'build_time': 3,
             'requirement': 'Stone Walls'}, #One Tier Developed
 "Magistrate's Hall": {'upkeep': 400,
                 'upkeep_frequency': 'each Empire Phase',
                 'empire_bonus': "Tax Income +1000 per Settlement",
                 'tier': 'Prodigious',
                 'build_time': 4,
                 'requirement': 'Library'},
 'Keep': {'upkeep': 400,
          'upkeep_frequency': 'each Empire Phase',
          'empire_bonus': "Siege Timer +1; When you Muster, reduce the Muster Timer by 1 and immediately gain Retinues equal to the combined muster limit; Presence +1",
          'tier': 'Prodigious',
          'build_time': 4,
          'requirement': 'March-Tower'},
 'Aqueducts': {'upkeep': 400,
          'upkeep_frequency': 'each Empire Phase',
          'empire_bonus': "Reach +2; Build Timer -1; Supply -1000; Upkeep -1000",
          'tier': 'Prodigious',
          'build_time': 4,
          'requirement': 'Bridges'},#One Tier Sophisticated
 'Cathedral': {'upkeep': 400,
               'upkeep_frequency': 'each Empire Phase',
               'empire_bonus': 'Faith +1',
               'tier': 'Prodigious',
               'build_time': 4,
               'requirement': 'Chapel'},
 # ── Wondrous tier (Wonders): Realm Scope, one per game, built in your capital
 'Colossus': {'upkeep': 500,
              'upkeep_frequency': 'per Wonder',
              'empire_bonus': "Speed +2; Siege Timer -2; Gain Immune Blunder; In the Intrigue Phase, you may support your own Personal Prowess Envoys before other players vote",
              'tier': 'Wondrous',
              'build_time': 10,
              'requirement': 'Keep'},
 'The Grand Exchange': {'upkeep': 500,
                        'upkeep_frequency': 'per Wonder',
                        'empire_bonus': "You count as having 2 more Trade Partners. In addition, whenever you generate Trade Income from a Trade Partner, you generate twice as much for yourself",
                        'tier': 'Wondrous',
                        'build_time': 10,
                        'requirement': 'Aqueducts'},
 'The Eternal Sepulchre': {'upkeep': 500,
                        'upkeep_frequency': 'per Wonder',
                        'empire_bonus': "If your Public Order would ever be less than 6, set it to 6 instead; Your Settlements gain Reach +2",
                        'tier': 'Wondrous',
                        'build_time': 10,
                        'requirement': 'Cathedral'},
 'High Chancery': {'upkeep': 500,
                   'upkeep_frequency': 'per Wonder',
                   'empire_bonus': "Upkeep -2000; In the Tally Phase, you may Endorse one Envoy you sent",
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
    "Hamlet":     {"tier": 0, "garrison": 0, "siege_timer": 0, "sea_variant": None,        "tax_income": 0,     "muster_limit":  0, "build_time": 1, "wards": 3, "reach": 1, "notes": "Natural holdings only; Placed at start of game Range 2 from capital."},
    "Village":    {"tier": 1, "garrison": 10, "siege_timer": 1, "sea_variant": None,        "tax_income": 2000,  "muster_limit":  5, "build_time": 2, "wards": 1, "reach": 2, "notes": ""},
    "Town":       {"tier": 2, "garrison": 15, "siege_timer": 2, "sea_variant": None,        "tax_income": 4000,  "muster_limit": 10, "build_time": 4, "wards": 2, "reach": 4, "notes": ""},
    "City":       {"tier": 3, "garrison": 25, "siege_timer": 3, "sea_variant": None,        "tax_income": 6000,  "muster_limit": 25, "build_time": 6, "wards": 3, "reach": 6, "notes": ""},
    "Metropolis": {"tier": 4, "garrison": 50, "siege_timer": 4, "sea_variant": None,         "tax_income": 8000,  "muster_limit": 50, "build_time": 8, "wards": 4, "reach": 8, "notes": "Capital only, requires Sovereign Industry (Titan of Industry)"},
}

# Presence (Prowess rule): an Army can't move within PRESENCE_RANGE of a non-allied Army (Bandit Armies included, Bandit
# Camps not) or a non-allied Settlement whose owner has a Garrison, unless that Move performs a Battle or Lay Siege against it.
# Presence +N (Keep) raises the Range of its owner's Settlement Presence. Board: DATA.rulesConst.PRESENCE_RANGE; Garrison / Keep via effect_registry.
PRESENCE_RANGE = 1
# Settlement Wards. "abstract": Wards are slots inside the Settlement, never placed on the map.
# "range1" (live): each Ward occupies a Territory within Range 1 of the Settlement.
# Switch WARD_MODEL between them; the rules prose reads WARD_RULE ({{VAL:WARD_RULE}}), the board reads DATA.rulesConst.WARD_MODEL.
WARD_MODEL = "range1"
WARD_RULES = {
    "abstract": ("A Settlement Ward is a slot inside a Settlement that holds one Holding; Wards are never placed on the map. "
                 "A Settlement has one Ward per tier: a Village has {Village}, a Town {Town}, a City {City} and a Metropolis {Metropolis}. "
                 "A Hamlet has {Hamlet} Wards."),
    "range1":   ("A Settlement Ward is a slot that holds one Holding. Each Ward occupies a Territory within Range 1 of its "
                 "Settlement. A Settlement has one "
                 "Ward per tier: a Village has {Village}, a Town {Town}, a City {City} and a Metropolis {Metropolis}. A Hamlet has {Hamlet} Wards."),
}
WARD_RULE = WARD_RULES[WARD_MODEL].format(**{k: v["wards"] for k, v in SETTLEMENTS.items()})
# Wavering Devotion (Piety rule): while your Public Order is below this value, you can't send Piety Envoys.
FAITH_FICKLE_PO = 0

# Era progression: shared-Renown thresholds; caps on armies/cities; influence.
ERAS = {
    "Founding":  {"renown": 1,  "armies": 1, "cities": 0, "max_settlements": 2, "influence_per_turn": 1, "rank": 1, "council_envoys": 1, "council_actions_per_envoy": 1, "personal_envoys": 1, "actions_per_envoy": 1, "po_scale_neg": 1, "po_scale_pos": 1, "unlocks": ""},
    "Ascension": {"renown": 8,  "armies": 2, "cities": 1, "max_settlements": 3, "influence_per_turn": 2, "rank": 2, "council_envoys": 1, "council_actions_per_envoy": 2, "personal_envoys": 1, "actions_per_envoy": 1, "po_scale_neg": 2, "po_scale_pos": 1, "unlocks": "May Declare War"},
    "Eminence":  {"renown": 18, "armies": 3, "cities": 2, "max_settlements": 4, "influence_per_turn": 3, "rank": 3, "council_envoys": 1, "council_actions_per_envoy": 2, "personal_envoys": 1, "actions_per_envoy": 2, "po_scale_neg": 3, "po_scale_pos": 1, "unlocks": "May form Military Alliances"},
    "Zenith":    {"renown": 30, "armies": 4, "cities": 3, "max_settlements": 5, "influence_per_turn": 4, "rank": 4, "council_envoys": 1, "council_actions_per_envoy": 2, "personal_envoys": 2, "actions_per_envoy": 2, "po_scale_neg": 4, "po_scale_pos": 1, "unlocks": "May form Defensive Alliances"},
}
# PHASE_REFORM, Spring's Diplomacy Phase: how many agreements a player may complete (each with a different partner)
for _en, _n in {"Founding": 1, "Ascension": 1, "Eminence": 2, "Zenith": 2}.items():
    ERAS[_en]["diplomacy_agreements"] = _n
for _e in ERAS.values():
    # Diplomacy has no Standing: its Envoys use the Era's rank (start Authority, and the cap per Diplomacy vote)
    _e["innate_diplomacy_influence"] = _e["max_influence_per_diplomacy_vote"] = _e["rank"]
    _e["envoys"] = (f"{_e['council_envoys']} Council Envoy{'s' if _e['council_envoys'] > 1 else ''}"
                    f" ({_e['council_actions_per_envoy']} action{'s' if _e['council_actions_per_envoy'] > 1 else ''} each)"
                    f" + {_e['personal_envoys']} Personal Envoy{'s' if _e['personal_envoys'] > 1 else ''}"
                    f" ({_e['actions_per_envoy']} action{'s' if _e['actions_per_envoy'] > 1 else ''} each) per turn")

# Public Order track: state name + effect template + base value.
# Scaling by Era: {n} = base x the Era's scale — ERAS[era]["po_scale_neg"] for bands below 0, ["po_scale_pos"] above 0
# (set po_scale_pos > 1 to scale the positive bands too). {s} = plural "s" when n != 1. A band with no {n} never scales.
PO_BANDS = {
    # bands every 2 steps (values between bands sit in the band nearer Neutral; bands stack toward Neutral)
   -10: ("Uprising",      "Spawn {n} Bandit Camp{s} in your Outlaw Country", 1),
    -8: ("Recession",     "Tax Income -{n} per Settlement", 1000),
    -6: ("Aimless",       "Speed -{n}", 2),
    -4: ("Indecisive",    "Influence -{n}", 1),
    -2: ("Shaken",        "No effect", None),
     0: ("Neutral",       "No effect", None),
     2: ("Confident",     "Influence +{n}", 1),
     4: ("Motivated",     "Speed +{n}", 1),
     6: ("Economic Boom", "Tax Income +{n} per Settlement", 500),
     8: ("Eureka",        "Each Empire Phase, may perform an Endorsed Industry Action", None),
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
        "Deficit":         "Per consecutive Upkeep Phase with negative Income",
        "Bankruptcy":      "Per consecutive Upkeep Phase with negative Treasury",
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
        "Established": "Grand Architect: May have an additional Settlement. Perform endorsed Settle.",
        "Sovereign":   "Titan of Industry: Your capital may Expand to a Metropolis. Perform endorsed Expand.",
    },
    "Prowess": {
        "Rising":      "Indomitable: In the Tally Phase, you may Support one of your own Prowess Envoys.",
        "Established": "Edict of War: May have an additional Army. Perform a Muster Action.",
        "Sovereign":   "High Quartermaster: Supply -2000. May change equipment on your Armies during any Upkeep step while that Army is within your Province. No longer lose Influence while at War.",
    },
    "Cunning": {
        "Rising":      "Clandestine Councilor: In the Intrigue Phase, target an Envoy and a player with a lower Cunning value - that player Abstains that Envoy.",
        "Established": "Grand Vizier: Influence +1. Players may not target you with Cunning actions if your Cunning value is higher.",
        "Sovereign":   "Master Conspirator: Once per Envoy Phase, if your non-Cunning Envoy passes or is endorsed, you may instead perform a Cunning action.",
    },
    "Piety": {
        "Rising":      "Divine Mandate: Faith +1 each Empire Phase.",
        "Established": "One True Gospel: Each Empire Phase, each other non-allied player with a lower Piety value gains Doubt +2.",
        "Sovereign":   "Pillar of Faith: If your Public Order would be set below 4, set it to 4. In addition, may use the Sacred War action.",
    },
    # Influence scaling by standing (Untested/Rising/Established/Sovereign):
    "max_influence_per_vote":  dict(STANDING_RANK),
    "innate_influence_own_envoys": dict(STANDING_RANK),
}
# the rules print one rank per Standing; if these two rows ever differ, the rules' Standing Rank text needs both numbers
assert DOMAIN_BOARD["max_influence_per_vote"] == DOMAIN_BOARD["innate_influence_own_envoys"], "Standing rank split: update RULES Standing Rank"
GLOSSARY["Standing"] = ((f"How far you've risen in a Domain, set by its value: Untested, Rising ({_ST['Rising']}+), Established ({_ST['Established']}+), "
                        f"Sovereign ({_ST['Sovereign']}+). Each has a Standing Rank and its own Domain effects."))
GLOSSARY["Max Influence"] = ("The most Influence you may spend to Support or Oppose on one Vote: your Standing Rank in that Domain "
                             "(the Era's rank on Diplomacy Envoys). Max Influence +X raises it.")
GLOSSARY["Standing Rank"] = (f"Untested {STANDING_RANK['Untested']}, Rising {STANDING_RANK['Rising']}, Established "
                             f"{STANDING_RANK['Established']}, Sovereign {STANDING_RANK['Sovereign']}. Your Envoys in a Domain start at "
                             f"Authority equal to your Standing Rank there; on each Vote in that Domain you may Support or Oppose up to your Standing Rank (your Max Influence). "
                             f"Diplomacy uses the Era's rank.")

# Seasons (turn cycle of 4; Rest Phase advances Season +1).
SEASONS = {
    "Winter": {"name": "Freezing",    "effect": "All Armies gain Speed -5; Siege Timers don't count down. Tax income collected."},
    "Spring": {"name": "Planting",    "effect": "No Host, Bandit Actions, Trade Income, Council Phase, or Diplomacy Actions. Players don't gain or spend Influence tokens. Bandit Camps Spawn."},
    "Summer": {"name": "Campaigning", "effect": "All Armies gain Speed +3"},
    "Fall":   {"name": "Harvest",     "effect": "Income from Holdings in Hamlets is doubled."},
}

# Trade & income constants (Rules: Trade & Income Rules).
# Trade Agreements need Can Trade on both players (Dirt Roads, Harbor, …); bordering is not required.
TRADE_RULES = {
    "income_per_craft": 100,                # Trade Income = 100 x host's Craft X, per active agreement
    "requirements": "A signed Trade Agreement, and each player has a Can Trade effect (e.g. Dirt Roads, Harbor)",
    "requires_border": False,
    "border_rule": "",                      # rules prose, Who Can Trade
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
BANDIT_EQUIPMENT_PER_ERA = {"Founding": "Levy: Farm Tools + Cloth", "Ascension": "Levy: Bill Hook + Gambeson", "Eminence": "Man-at-Arms: Spears + Kite Shield + Leather", "Zenith": "Man-at-Arms: Halberd + Chainmail"}
# Hardcore (a per-game choice the Host makes at Setup › Wild Outlaw Country): Wild Outlaw Country follows
# HARDCORE_WILD_OUTLAW instead of WILD_OUTLAW, Bandits are armed from HARDCORE_BANDIT_EQUIPMENT_PER_ERA, and Bandit
# Armies Move by BANDIT_BEHAVIOR["Hardcore Army Behavior"].
HARDCORE_BANDIT_EQUIPMENT_PER_ERA = {"Founding": "Levy: Pitchfork + Gambeson", "Ascension": "Man-at-Arms: Spears + Targe Shield + Leather",
                                    "Eminence": "Man-at-Arms: Halberd + Chainmail", "Zenith": "Sergeant: Bastard Sword + Tower Shield + Full Plate"}
                                    
HARDCORE_WILD_OUTLAW = {
    "count": "fill",      # "formula" | "fill"
    "max": 1,             # cap on zones in "fill" mode (None = no cap)
    "border_range": 1,       # min Range from any player's Province
    "spacing": 4,            # min Range from any other Outlaw Country zone
    "per_players": 0,        # "formula": floor(players / 2)
    "plus": 0,               # "formula": + 1
    "spring_spawn": True,    # Spring: each Wild zone spawns a Bandit Camp (full zone -> its camps grow instead)
    "spring_growth": True,   # Spring: Wild camps also grow, like every other camp
    "march": True,           # a Wild Bandit Army Marches like every other Bandit Army
}
BANDITS = {
    "Bandit Domain Value": "For every 5 Retinues in the Bandit Camp or Army, the Bandit Camp has +2 Cunning and +2 Prowess.",
    "Bandit Camp": f"A collection of Bandits in Outlaw Country, starting with {BANDIT_CAMP_START} Retinues and {BANDIT_CAMP_GOLD} gold.",
    "Bandit Growth": f"Bandit Camps gain ({'/'.join(str(v) for v in BANDIT_GROWTH_PER_ERA.values())}) Retinues a turn, based on the Era of the Realm.",
    "Bandit Army": f"A Bandit Camp at {BANDIT_ARMY_THRESHOLD} Retinues sends out a Bandit Army of {BANDIT_ARMY_THRESHOLD}; the camp stays, and the Army returns to it after each Battle to re-muster. Performs Move actions toward the Settlement with the highest Holding income, Battling or Pillaging if possible, in addition to Bandit Cunning Mechanics. Bandit Armies cannot exceed {BANDIT_ARMY_THRESHOLD}",
    "Spawn a Bandit Camp": "Each Spring, every player gains a Bandit Camp.",
}

TIMERS = {
    "Build Timer":   {"where": "Infrastructure / Settlement Wards / Holdings", "default": None, "tracks": "Turns until a Holding, Infrastructure or Settlement finishes building and becomes active."},
    "Repair Timer":  {"where": "Damaged Holdings / Infrastructure", "default": None, "tracks": "Turns until a Damaged piece is repaired and its effects return."},   # default = BUILD_TIMERS["Repair"] (set below)
    "Truce Timer":   {"where": "Treaties / diplomacy outcomes", "default": 5, "tracks": "Turns until a Truce ends; until then neither player may Declare War on the other or End a Treaty with them."},
    "Siege Timer":   {"where": "Lay Siege", "default": None, "tracks": "Turns until a Siege resolves; it doesn't count down in Winter."},
    "Muster Timer":  {"where": "Muster action", "default": 1, "tracks": "Turns until a Muster completes; each turn it counts down, the Army gains Retinues up to the combined Muster Limit."},
    "Sack Timer":    {"where": "After Sacking a Settlement", "default": 2, "tracks": "Turns until the sacking Army may Move or Lay Siege again."},
    "Capture Timer": {"where": "Capturing a Settlement after Siege", "default": 1, "tracks": "Turns until a Captured Settlement comes under your Control."},
    "Convert Timer": {"where": "Convert (Piety action)", "default": None, "tracks": "Turns until a Convert attempt resolves; it fails early if conditions change."},
}

# ── Chartering / map placement constants (prose-only before; tunable balance) ──
CHARTER_MIN_RANGE   = 4   # map generator spacing for start-zone Towns (Settle itself needs Grassland)
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
    "count": "fill",      # "formula" | "fill"
    "max": 0,             # cap on zones in "fill" mode (None = no cap)
    "border_range": 3,       # min Range from any player's Province
    "spacing": 5,            # min Range from any other Outlaw Country zone
    "per_players": 0,        # "formula": floor(players / 2)
    "plus": 0,               # "formula": + 1
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
    "Pursuit": 0,
    "Rising Pursuit": 1,
    "Established Pursuit": 2,
    "Monument Pursuit": 3,
    "Village": SETTLEMENTS["Village"]["build_time"],
    "Town": SETTLEMENTS["Town"]["build_time"],
    "City": SETTLEMENTS["City"]["build_time"],
    "Metropolis": SETTLEMENTS["Metropolis"]["build_time"],
    "Wonder": 10,
    "Repair": 1,
    "Infrastructure": {"Primitive": 1, "Developed": 2, "Sophisticated": 3, "Prodigious":4},
}

# Base Holding upkeep (Untested); HOLDING_TIER_COST below sets the rest by Standing.
PURSUIT_UPKEEP_DEFAULT = 100
# Holding upkeep & Build Timer by Standing tier of its unlock. Natural: no upkeep (Build Timer unchanged).
HOLDING_TIER_COST = {                     # standing -> (upkeep, build timer)
    None:          (PURSUIT_UPKEEP_DEFAULT, BUILD_TIMERS["Pursuit"]),
    "Rising":      (200, BUILD_TIMERS["Rising Pursuit"]),
    "Established": (300, BUILD_TIMERS["Established Pursuit"]),
    "Sovereign":   (400, BUILD_TIMERS["Monument Pursuit"]),
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
    if n.get("natural"):
        up = 0
    return up, tm

def holding_build_time(node):
    return holding_cost(node)[1]

_HTC = HOLDING_TIER_COST
_HOLDING_COST_TEXT = (f"by Standing: Untested {_HTC[None][0]} (Build Timer {_HTC[None][1]}), "
    + ", ".join(f"{t} {_HTC[t][0]} (Build Timer {_HTC[t][1]})" for t in _STANDINGS) + "; Natural 0")
HOLDING_COST_TEXT = _HOLDING_COST_TEXT    # rules prose: {{VAL:HOLDING_COST_TEXT}}
TIMERS["Repair Timer"]["default"] = BUILD_TIMERS["Repair"]

TERRAIN = {
	"Grassland": {"Effect": "Where Settlements can be chartered (a Hill counts)."},
	"Wetlands": {"Effect": "Speed -1 per Territory moved through"},
	"Tundra": {"Effect": "gain Strained"},
	"Mountains": {"Effect": "Impassable"},
	"Water": {"Effect": "Must end move after moving over 1 Water Territory (must end on land)"},
	"Forest": {"Effect": "Speed -1 per Territory moved through"},
	"Hill":  {"Effect": "Gains Seize the Initiative."},
}
# TERRAIN "Raw Materials" is collected from each Holding's 'terrain' list (NODES): Holdings that name the terrain earlier in
# their own list come first, then NODES order. The map generator places a terrain's first Holding on every patch of it
# and the rest on large patches only, so list a Holding's main terrain first.
for _n, _v in NODES.items():
    for _t in _v.get("terrain") or []:
        if _t not in TERRAIN:
            raise ValueError(f"NODES[{_n!r}]['terrain'] names {_t!r}; use one of {sorted(TERRAIN)}")
for _t, _tv in TERRAIN.items():
    if _t != "Hill":    # a Hill counts as Grassland
        _tv["Raw Materials"] = sorted((_n for _n, _v in NODES.items() if not _v.get("deprecated") and _t in (_v.get("terrain") or [])),
                                      key=lambda _n: NODES[_n]["terrain"].index(_t))   # stable: ties keep NODES order

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
                   "effect": "If you Battle while your army is on a Hill, gain +1 Initiative every Skirmish. A Hill counts as Open Field: Ranged Weapons gain +1 to Strike."},
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
    "Trade Partners": {"change": "+1", "notes": "Per Trade Partner."},
    "Alliances": {"change": "+1", "notes": "Per Alliance Member."},
    "Infrastructure tier completed": {"change": "+0", "notes": "Per Infrastructure tier fully completed."},
    "Fully Mustered Army": {"change": "+1", "notes": "Per active Army of 25 Retinues."},
    "Condemned Envoy last turn": {"change": "-1", "notes": "Per Condemned Envoy last turn."},
    "At War": {"change": "-3", "notes": "While at War."},
    "Monuments & Wonders": {"change": "+1", "notes": "Per active Monument or Wonder."},
    "Other sources": {"change": "+X", "notes": "From other effects like Holdings."},
}

# --- Glossary additions (map/spatial, action, and outcome terms) ---
GLOSSARY.update({
    "Border": "You border a player when your Province is within or Adjacent to theirs.",
    "Province": "Every Territory your Settlements' Reach covers, Contested or not.",
    "Region": "A collection of Territories of the same Type.",
    "Realm": "The total collection of Regions.",
    "Territory": "1 Hex.",
    "Controlled": "Territory that is within Reach of a Player's Settlement(s).",
    "Contested": "Territory that is Controlled by more than one player's Settlement(s).",
    "Uncontested": "Territory that is Controlled by a single Player's Settlement(s).",
    "Uncontrolled": "Territory that is not within Reach of any Player Settlement.",
    "Adjacent": "Range 1.",
    "Next to": "Range 2.",
    "Within": "Range 0.",
    "Range X": "The amount of Territories you must move in order to get from your current position to the specific Territory.",
    "Reach X": "How far a Settlement controls, set by its tier: every Territory within Range X of it is in your Province.",
	"Host": "Holds the Host Card; the starting player is the player directly clockwise from the Host, including in Spring. The role passes clockwise each Rest Phase (there is no Host in Spring). The Host collects and distributes Trade Income, resolves Bandit Mechanics, and breaks ties (Council vote, Bandit targeting, and any tie not otherwise resolved).",
    "Targeting you": "An effect or action targeting you also targets what you own: your Settlements, Armies and Holdings.",
    "Perform": "When you Perform an action, immediately do the description of the action. Pay the action's normal Cost.",
    "Resolve": "Read an Envoy's Net Influence on the Envoy Resolution table and carry out the result.",
    "Cost / Pay": "Cost to Perform an action, usually in Gold or Doubt.",
    "Presence": (f"Territory within Range {PRESENCE_RANGE} of a non-allied Army (Bandit Armies included, Bandit Camps not), "
                 f"or of a Settlement while its owner has a Garrison. Presence +N raises the Range of its owner's Settlement Presence by N. "
                 f"An Army can't move within a non-allied Presence unless that Move Performs a Battle against it; a Battle or "
                 f"Lay Siege may pass through the Presence of its target only, and can't end within any other non-allied Presence."),
    f"{EXPOSED} X": (f"In the Envoy Phase, a player may target you with a {EXPOSED_DOMAIN} Envoy. If they do, that Envoy gains "
                     f"Authority +X. If it Passes or is Endorsed, its action must target you. Stacks: add together every {EXPOSED} X you have."),
    "Can Trade": "You may take part in trade (you still need a signed Trade Agreement). Required by both players of a Trade Agreement; Dirt Roads give it.",
})
# ============================================================================
# NEW STRUCTURES — paste into renown_data.py and modify as needed.
# Built from RULES.md (v0.4.8.3.1). Schemas chosen to be generator-friendly:
# the wiki / FAQ / compendium can iterate these the same way they do NODES.
# ============================================================================




# ── ENVOY OUTCOMES ───────────────────────────────────────────────────────
# Resolution bands for a Sent Envoy, by Net Influence (starting Influence by
# Standing + all Support/Oppose/Influence X):
#   Condemned : Net <= Condemned   (resolve the domain's Condemn effect)
#   Failed    : Net <= Failed      (gain Doubt 1)
#   Passed    : Net >= Passed
#   Endorsed  : Net >= Endorsed    (Passed + the domain's endorsed bonus)
ENVOY_OUTCOME_THRESHOLDS = {
    "Condemned": -4,
    "Failed":     0,
    "Passed":     1,
    "Endorsed":   4,
}
# Outcome glossary entries read the bands above
_ET = ENVOY_OUTCOME_THRESHOLDS
GLOSSARY.update({
    "Net Influence": (f"An Envoy's starting Influence (your Standing Rank) plus every Support, Oppose and Authority X. It sets the outcome: {_ET['Condemned']} or less Condemned, {_ET['Condemned'] + 1} to {_ET['Failed']} Failed (gain Doubt 1), {_ET['Passed']} to {_ET['Endorsed'] - 1} Passed, {_ET['Endorsed']}+ Endorsed. Each Domain's result per outcome is in the Envoy Outcome table."),
    "Condemned": f"Net Authority {_ET['Condemned']} or less.",
    "Failed":    f"Net Authority {_ET['Condemned'] + 1} to {_ET['Failed']}.",
    "Passed":    f"Net Authority {_ET['Passed']} to {_ET['Endorsed'] - 1}.",
    "Endorsed":  f"Net Authority {_ET['Endorsed']}+.",
})
# Per-domain effect at each outcome band. Prowess Condemn is a combat penalty
# (Strained; an Army already Strained gains Blocked) rather than Doubt+Cost,
# since Prowess actions carry no gold/doubt cost.
# Cunning actions Extort from their target: CUNNING_EXTORT when Passed, CUNNING_EXTORT_ENDORSED (in place of it) when Endorsed.
CUNNING_EXTORT          = 2000
CUNNING_EXTORT_ENDORSED = 2000
CUNNING_DOUBT           = 1      # Passed or Endorsed, a Cunning action's target also gains this Doubt
ENVOY_OUTCOMES = { #Note, the condemned.split("+")[-1] is the "cost" for cunning piety and industry
    "Prowess":   {"condemned": "Doubt 1 + each of your Armies gains Strained; an Army that already has Strained gains Blocked.",
                  "failed": "Doubt 1", "passed": "Perform the action", "endorsed": "Perform a Prowess action"},
    "Cunning":   {"condemned": "Doubt 1 + pay 2000, & you cannot Recoup",
                  "failed": "Doubt 1", "passed": f"Perform the action; its target gains Doubt +{CUNNING_DOUBT}; Extort {CUNNING_EXTORT} from its target",
                  "endorsed": f"Extort {CUNNING_EXTORT_ENDORSED} from its target instead"},
    "Piety":     {"condemned": "Doubt 1 + pay Doubt 1, & you cannot Recoup",
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
        'endorsed': 'Perform a Prowess action.',
        'notes': ['Unless the move action was Endorsed, an Army may be the target of only one Move action per turn.', "Presence limits where the Army may move (see Rule: Commanding Presence).", "While an Army's Battle or Siege Timer is active, it can't be the target of actions.", "When an Army performs the Battle action, it gains Seize the Initiative in that Battle's first Skirmish."],
    },
    'Declare War': {
        'domain': 'Prowess',
        'cost': 'None',
        'requires': 'Rising Prowess',
        'effect': 'Choose a non-allied player you have no NAP or active truce with. You and that player are now At War, and any Trade Agreements between you end. If the target is in a Defensive Alliance, every member is now At War with you.',
        'endorsed': 'Perform a Prowess action.',
        'notes': ['If you are in a Military Alliance, then at the start of your next turn every member Declares War on the target and sends 1 fewer Envoy that turn.'],
    },
    'Pillage': {
        'domain': 'Prowess',
        'cost': 'None',
        'requires': 'Rising Prowess',
        'effect': "Choose an army you control within Reach of an at-war player's Settlement without an active Siege Timer. While that army remains within Reach of that Settlement and does not Lay Siege, Battle, or March, it may Extort that Settlement's holding income in the Extort step. A Settlement may be Pillaged once per Empire Phase. Pillage ends if [war ends / army leaves Reach / Settlement is besieged].",
        'endorsed': 'Perform a Prowess action.',
    },
    'Muster': {
        'domain': 'Prowess',
        'cost': 'None',
        'requires': '',
        'effect': (f"Choose one: Raise — if you have fewer Armies than your Era allows, place a new Army within a Settlement under your Control; or "
                   f"Reinforce — choose an Army you control. The Army must be within range {MUSTER_RANGE} of a Settlement "
                   f"you Control, while you have an active Muster Field, and at least Range 2 from any non-allied Army unless it is "
                   f"within Range 0 of a Settlement you Control. Choose how many Retinues to recruit (an Army "
                   f"can't exceed {ARMY_MAX_RETINUES}) and set a Muster Timer equal to that number ÷ your combined muster "
                   f"limit, rounded up. Each turn the Muster Timer counts down, the Army gains Retinues up to your "
                   f"combined muster limit and you begin paying their upkeep. You may change the Army's Retinue type "
                   f"and equipment while an army has an active Muster Timer. Reinforcing an Army that already has an active "
                   f"Muster Timer instead hurries it: reduce that Muster Timer by 1, and the Army gains Retinues up to your "
                   f"combined muster limit at once."),
        'endorsed': 'Perform a Prowess action.',
        'notes': ["Combined muster limit: the total muster limit of your Settlements whose Reach includes the Army's Territory.",
                  "While a Settlement is besieged, its muster limit is 0; an active Muster Timer doesn't count down and may be cancelled at any time."],
    },
    'Demand Tribute': {
        'domain': 'Prowess',
        'cost': 'None',
        'requires': '',
        'effect': 'Choose a non-allied player you have no NAP with, then negotiate terms. If the target agrees, sign a NAP or Alliance (the target picks among the offered terms). If the target refuses, or later fails to meet the terms, immediately Declare War on them.',
        'endorsed': 'Perform a Prowess action.',
        'notes': ['Terms may include gold, Settlements, Territory, Treaties, or promises. A promise is unenforceable, but breaking one counts as failing the terms.'],
    },
    'Intercept Caravan': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': f'Extort {CUNNING_EXTORT} from its target. Then, choose a player. The next turn that player is Host, Extort their Trade Income. If they have no Trade Income that turn, instead Extort {INTERCEPT_EXTORT_PER_CRAFT} per their Craft.',
        'endorsed': f'Extort {CUNNING_EXTORT_ENDORSED}.',
        'notes': ["This affects only a single turn's trade income; normal income resumes afterward."],
    },
    'Foster Rebellion': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': f'Extort {CUNNING_EXTORT} from its target. Then, choose a player. At the next Bandit Mechanics step, place a Bandit Camp of 10 Retinues in their Outlaw Country.',
        'endorsed': f'Extort {CUNNING_EXTORT_ENDORSED}.',
        'notes': ["If that player's Outlaw Country has no room, expand it by one Territory and spawn there instead."],
    },
    'Raze': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': f"Extort {CUNNING_EXTORT} from its target. Then, choose another player's Settlement, then choose active Infrastructure in it, or the top-most Holding of one of its Wards that isn't Damaged or under a Build Timer: it becomes Damaged, and its effects are inactive until Repaired. If the top-most Holding of a Ward is under a Build Timer, you may choose it instead and increase that Build Timer by 2.",
        'endorsed': f'Extort {CUNNING_EXTORT_ENDORSED}.',
        'notes': ["A Wonder has Immune Razed and can't be targeted."],
    },
    'Destabilize': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': f"Extort {CUNNING_EXTORT} from its target. Then, choose a player. In the next Winter phase, during the Extort step, Extort one settlement's tax income. Each settlement can only be Destabilized once per Winter.",
        'endorsed': f'Extort {CUNNING_EXTORT_ENDORSED}.',
        'notes': ["If multiple players extort the same player, the player with the highest Cunning value chooses which settlement(s) are extorted first. In the event of a tie, or if there are not enough settlements, the Extort value is divided equally."],
    },
    'Sabotage': {
        'domain': 'Cunning',
        'cost': '2000 gold',
        'requires': '',
        'effect': f'Extort {CUNNING_EXTORT} from its target. Then, choose an army, that army gains Blocked.',
        'endorsed': f'Extort {CUNNING_EXTORT_ENDORSED}.',
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
    'Improve': {
        'domain': 'Industry',
        'cost': '2000 gold',
        'requires': '',
        'effect': 'Choose an unlocked, available Infrastructure and set a Build Timer equal to its build time. When it completes, the Infrastructure becomes active in every Settlement in your Province.',
        'endorsed': 'Recoup 2000.',
        'notes': ['You must have at least one Infrastructure from the prior tier before building the next tier.', 'A Wonder is built in your capital; you build one Wonder at a time.'],
    },
    'Repair': {
        'domain': 'Industry',
        'cost': '0 gold',
        'requires': '',
        'effect': f'Choose a Damaged Holding or Infrastructure in a Settlement you control and set Repair Timer {TIMERS["Repair Timer"]["default"]}. When it reaches 0, choose one: Restore — reactivate it with all effects; Demolish — remove the Holding tile from your Empire Tableau.',
        'endorsed': 'Recoup 0.',
    },
    'Build': {
        'domain': 'Industry',
        'cost': '2000 gold',
        'requires': '',
        'effect': f'Choose an inactive Settlement Ward you control, then choose a Holding with one complete line of its {CHAIN_TERM} under your control (and meet its other requirements) and set a Build Timer equal to its build time (usually 1). When it completes, place the Holding in an available Ward slot; its effect activates immediately.',
        'endorsed': 'Recoup 2000.',
        'notes': ['You may have only 1 Monument Holdings per settlement.',
                  "Build Timer by Standing: Untested " + str(_HTC[None][1]) + ", "
                  + ", ".join(f"{t} {_HTC[t][1]}" for t in _STANDINGS) + "."],
    },
    'Settle': {
        'domain': 'Industry',
        'cost': '4000 gold',
        'requires': 'Rising Industry',
        'effect': f'Charter a new Village on Grassland in your Province or within the Presence of one of your Armies, range {OUTLAW_BUFFER_RANGE}+ from Outlaw Country, and set a Build Timer 2.',
        'endorsed': 'Recoup 2000.',
        'notes': [],
    },
    'Expand': {
        'domain': 'Industry',
        'cost': '4000 gold',
        'requires': 'Rising Industry',
        'effect': "Increase a Settlement by one tier (Village to Town, Town to City, City to Metropolis), raising its Wards, Tax income, Muster Limit and Reach.",
        'endorsed': 'Recoup 2000.',
        'notes': ["To upgrade to City or Metropolis you must meet that era requirement; otherwise set Build Timer 1."],
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
    "Trade Agreement":   {"signed_via": "Sign Treaty", "effect": "Begin trading (Trade Income flows from next turn). Requires a Can Trade effect for each player.", "era": "Any"},
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
# Completing an Edict raises the Renown tracker by 1. Each player may complete each
# Edict once ("unique": once per game, first player only). Whoever has completed the most when the Last Alliance Standing
# condition is met wins.
EDICT_STREAK_TURNS = 5      # consecutive-turn Edicts (Wealth, Living Saints, Imperium)
GAME_TURN_LIMIT = 50        # the game ends after this turn if Last Alliance Standing hasn't ended it first
# Toggle: a Domain / Monument / Wonder counts toward an Edict once per game (first player) or once per player
# (build_all_CE.bat: set EDICT_UNIQUE=1|0).
EDICT_UNIQUE = _os.environ.get("RENOWN_EDICT_UNIQUE", "0") == "1"
EDICT_UNIQUE_RULE = ("Each Domain, Monument, or Wonder counts toward an Edict only once per game, for the first player to complete it."
                     if EDICT_UNIQUE else "Each Domain, Monument, or Wonder counts toward an Edict once per player.")
_NUMWORD = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten"}

# Imperium: % of the Realm's Territories (every hex, Water and Impassable included) under your Uncontested Control,
# by player count ("5+" = five or more players; fewer players than the smallest key use that key's %)
IMPERIUM_REQUIREMENT = {"1": 65,
                        "2": 50,
                        "3": 45,
                        "4": 40,
                       "5+": 35}
_IMPERIUM_TEXT = (" / ".join(str(v) for v in IMPERIUM_REQUIREMENT.values()) + "% of the Realm's Territories under your Uncontested Control ("
                  + " / ".join(IMPERIUM_REQUIREMENT) + " players)")
EDICTS = {
    "Sovereign Standing": {"type": "Standing",  "requirement": f"Reach a Sovereign Standing (Domain value {_ST['Sovereign']}) in any Domain."},
    "Monument":           {"type": "Build",     "requirement": "Have a Monument holding."},
    "Wonder":             {"type": "Improve",   "requirement": "Complete a Wondrous Infrastructure."},
    "Wealth":             {"type": "Economy",   "turns": EDICT_STREAK_TURNS, "requirement": f"Hold {WEALTH_EDICT_GOLD:,} gold in your Treasury for {_NUMWORD[EDICT_STREAK_TURNS]} consecutive turns."},
    "Vassalize":          {"type": "Conquest",  "requirement": "Vassalize a rival player (control their capital with no other settlements/armies under them)."},
    "Living Saints":      {"type": "Piety",     "turns": EDICT_STREAK_TURNS, "requirement": f"Sustain Public Order {PO_MAX} (Living Saints) for {_NUMWORD[EDICT_STREAK_TURNS]} consecutive turns (Pious Timer)."},
    "Imperium":           {"type": "Control",   "turns": EDICT_STREAK_TURNS, "unique": True, "by_players": IMPERIUM_REQUIREMENT,
                           "requirement": f"Have at least {_IMPERIUM_TEXT} for {_NUMWORD[EDICT_STREAK_TURNS]} consecutive turns. Only the first player to complete it scores it."},
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
    "Cunning Roll":  "",   # set below from BANDIT_CUNNING_TABLE (bandit_cunning_text)
    "Treasury":      "Bandit camps keep Extorted gold in their treasury and pay no costs or upkeep. Winning a Battle against a camp or army destroys it and Extorts its whole treasury (an army's includes its camp's).",
    "Army Behavior": "After bandit mechanics, a Bandit Army performs a Move: Battle (player army in range) > Pillage (the player settlement with the highest Holding income in range by a direct route, one Presence doesn't make longer: its Holding income each Empire Phase) > March (along a direct route toward the player settlement with the highest Holding income, stopping short of Presence rather than going around it). Host breaks ties. After each Battle it doesn't lose, the Army returns to its camp; losing a Battle destroys it and its camp.",
    "Hardcore Army Behavior": "With Hardcore on, a Bandit Army's Move is instead: Pillage (the player settlement with the highest Holding income, the closest of them, if it's in range); if it isn't: Battle (the closest player army in range) > Lay Siege (the closest player settlement in range) > March (toward that highest-income settlement). Host breaks ties.",
    "Attacking":     "Move to end adjacent to a camp; another player rolls bandit tactics (D{FACES}; a Focused result = Fall Back) and resolves to-strike/save as a Battle. Bandits never Fall Back but may Rout as normal. Winning the Battle destroys the camp and Extorts its whole treasury.",
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
PURSUIT_UPKEEP_BY_TYPE = {   # legacy fallback for a bare type string (pursuit_upkeep); Holdings cost by Standing
    "Monument": 300,
    "Power":    200,
    "Energy":   0,
    "Other":    PURSUIT_UPKEEP_DEFAULT,
}
_PU = PURSUIT_UPKEEP_BY_TYPE
_PU_TEXT = (f"Monument {_PU['Monument']}, Power {_PU['Power']}, "
            f"Energy/Natural {_PU['Energy']}, all others {_PU['Other']}")

UPKEEP_TRACKS = {
    f"Holdings ({UPKEEP_TERM})": f"Each Empire Phase: {_HOLDING_COST_TEXT}.",
    f"Armies ({SUPPLY_TERM})": f"Σ(each Army's cost by Retinue type) - {SUPPLY_TERM} -X. Reduced by Levy Hall, Tannery, Saddlery, Butchery, Smokehouse, Advanced Blast Furnace, High Quartermaster, etc.",
    f"Infrastructure ({UPKEEP_TERM})": f"Listed per Infrastructure; {UPKEEP_TERM} -X lowers Holding and Infrastructure {UPKEEP_TERM}. Masonry removes Primitive; Trade Guild removes Developed; College of Engineering removes Sophisticated.",
}


def pursuit_upkeep(node):
    """Per-turn upkeep: a NODES entry (dict) costs by Standing (holding_cost); a bare type string reads
    PURSUIT_UPKEEP_BY_TYPE."""
    if isinstance(node, dict):
        return holding_cost(node)[0]
    if isinstance(node, dict) and node.get("natural"):
        return 0                                   # GLOSSARY["Natural"]: Natural Pursuits do not cost Upkeep
    t = node.get("type") if isinstance(node, dict) else node
    return PURSUIT_UPKEEP_BY_TYPE.get(t, PURSUIT_UPKEEP_DEFAULT)

# 2) ARMY upkeep — formula note (per-retinue costs in RETINUES[*]["cost"]).
ARMY_UPKEEP_NOTE = f"Net Army {SUPPLY_TERM} = the sum of each Army's cost (by Retinue type) - {SUPPLY_TERM} -X modifiers."

# ── ACTION / EMPIRE GOLD COSTS ───────────────────────────────────────────────
# The flat costs the rules attach to actions and siege outcomes.
COSTS = {
    "Build action":    f"{ACTIONS['Build']['cost']} (the Envoy action; the Holding then pays Holding upkeep each Empire Phase)",
    "Pursuit upkeep":  f"Each Empire Phase: {_HOLDING_COST_TEXT}",
    "Army upkeep":     f"sum of each Army's cost (by Retinue type) - {SUPPLY_TERM} -X modifiers",
    "Infrastructure upkeep": "Per-settlement (see INFRASTRUCTURE); Masonry removes Primitive, Trade Guild removes Developed, College of Engineering removes Sophisticated",

    "Sack":            f"Raze the top-most Holding of each Ward; Extort {SACK_EXTORT_PER_TIER} per settlement tier; reduce settlement by 1 tier; the controller removes one Ward (sacker's choice) and its Holdings; Sack Timer {TIMERS['Sack Timer']['default']}",
    "Tax per tier":    "Winter tax by Settlement tier: " + " / ".join(f"{k} {v['tax_income']}" for k, v in SETTLEMENTS.items()),
    "Trade Income":    "100 x host's Craft X per active Trade Agreement",
}
# "<Domain> action" cost lines are read from ACTIONS (grouped by cost).
def _action_costs():
    for _dom in ("Cunning", "Industry", "Piety", "Prowess", "Diplomacy"):
        _g = {}
        for _a, _r in ACTIONS.items():
            if _r.get("domain") == _dom: _g.setdefault(_r.get("cost") or "None", []).append(_a)
        COSTS[f"{_dom} action"] = "; ".join(f"{_c} ({' / '.join(_n)})" for _c, _n in _g.items())
_action_costs()

# phase order (currently only in RULES_reorganized)
# PHASE_REFORM: the Works Phase performs COUNCIL_DOMAIN actions (no vote, no Envoy), Spring included (COUNCIL_DOMAIN_SPRING);
# in Spring the Envoy Phase is the Diplomacy Phase (ENVOY_PHASE_SPRING), the only time Diplomacy actions happen.
# FORUM_DOMAIN: a Diplomacy step in the Envoy Phase's Forum as well, FORUM_ACTIONS agreement(s); None = a plain Forum.
COUNCIL_DOMAIN = "Industry" if PHASE_REFORM else None
COUNCIL_DOMAIN_SPRING = "Industry" if PHASE_REFORM else None   # Spring's Works Phase: the same Industry actions
ENVOY_PHASE_SPRING = "Diplomacy" if PHASE_REFORM else None     # Spring's Envoy Phase: the Diplomacy Phase instead (no Envoys)
FORUM_DOMAIN = None                   # Diplomacy only in Spring: the Envoy Phase keeps a plain Forum
FORUM_ACTIONS = 1
PHASES = ("Empire", "Works" if PHASE_REFORM else "Council", "Envoy", "Battle", "Rest")
STARTING_TURN_PHASE_OPENER = PHASES[1]
# ACTIONS["Move"] says "March (move up to 2x Speed)"
STANDING_ARMY_SIEGE_MODIFIER = 1
# economy.py has this as a local constant (EMPIRE_START)
EMPIRE_START_TIERS = ("Town", "Hamlet")
STARTING_TREASURY = 10000
# Setup › Player Setup: Starting Holdings, placed free and built before Turn 1: SETUP_CAPITAL_PICKS eligible Raw Material
# Holdings in the capital, and SETUP_HAMLET_PICKS of SETUP_HAMLET_HOLDINGS in the Hamlet (0 = the Hamlet starts empty)
SETUP_CAPITAL_PICKS = 2
SETUP_HAMLET_PICKS = 0
SETUP_HAMLET_HOLDINGS = ("Common Land",)
SETUP_HAMLET_TEXT = " or ".join(SETUP_HAMLET_HOLDINGS)
# Hamlets › special rule: a Hamlet may hold more than one of these (an exception to Settlement Scope, one per Settlement)
HAMLET_REPEATABLE = ("Common Land",)
HAMLET_REPEATABLE_TEXT = " or ".join(HAMLET_REPEATABLE)

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
# Board: picking an Age before Turn 1 rolls its starting Year, normally distributed over the Age's "years" range —
# mean at this fraction of the range, standard deviation this fraction of its span, clamped to the range
AGE_YEAR_ROLL_MEAN = 0.45
AGE_YEAR_ROLL_SD = 1 / 6
CAPITAL_EDGE_RANGE = 4       # capital Town is deployed within this range of the board edge (or corner)

BOARD_SIZES = {
    "Tight":    {3: (12,10), 4: (16,12), 5: (18,14), 6: (20,16)},
    "Standard": {3: (18,14), 4: (20,16), 5: (22,18), 6: (24,20)},
    "Campaign": {3: (30,24), 4: (30,24), 5: (30,24), 6: (30,24)},
}

SIEGE_CALCULUS = {
    "Lay Siege": {
        "settlement_sources": ["Settlement Size", "Citadel", "Standing Army"],   # + every "Siege Timer +X" in the defender's text
        "attacker_sources": True,      # Siege Works, Siege Camp, army effects
        "floor": 1,
    },
    "Convert": {
        "settlement_sources": ["Settlement Size", "Citadel"],
        "attacker_sources": False,     # settlement-type modifiers only
        "floor": 1,
    },
}

# Where each listed source's value lives. Every other defender source is its own "Siege Timer +X" text (Infrastructure,
# Holdings, Heritage); Citadel is listed because it counts only in the Settlement it's in (value from its text).
SIEGE_SOURCE_VALUES = {
    "Settlement Size": {"from": "SETTLEMENTS", "field": "siege_timer"},
    "Standing Army":   {"from": "board_state", "value": STANDING_ARMY_SIEGE_MODIFIER,
                        "rule": "Army within Range 0 of the Settlement"},
    "Citadel":         {"from": "text"},
}

# ── Missing glossary definitions (CE) ────────────────────────────────────────
GLOSSARY.update({
    PIVOTAL:        f"An Unmodified {FOCUSED_THR}." if FOCUSED_THR == FACES else f"An Unmodified {FOCUSED_THR} or higher.",
    FATIGUE_TOKEN:  f"Each token reduces Morale by {FATIGUE_MORALE}; if your modified Morale is ever {ROUT_THR}+, your Army Routs. Tokens stack.",
    "Sally Forth":  "While a Settlement you control is besieged and you have an Army or Garrison inside it, you may Sally Forth: Battle in the Battle Phase without performing an action.",
    "Garrison":     ("An Army that exists within each of your Settlements while you have the Garrison Infrastructure, sized by that Settlement's Garrison value ("
                     + ", ".join(f"{t} {v['garrison']}" for t, v in SETTLEMENTS.items() if v.get("garrison")) + " Retinues). "
                     "Garrisons can't Perform actions or be targeted by actions, and may Sally Forth while their Settlement is under Siege. "
                     f"Garrisons have cost and {SUPPLY_TERM} 0 and don't count toward your Army limit. All your Garrisons share the same "
                     "Retinue type and equipment, and gain the benefits of all unlocked keywords that apply to your Armies."),
    "War Weariness":"Doubt 1 each Empire Phase per consecutive Battle you've lost.",
    "Wavering Devotion": f"While your Public Order is below {FAITH_FICKLE_PO}, you can't send Piety Envoys.",
    "Settlement Ward": ("A slot in a Settlement that holds one Holding; a Settlement has one Ward per tier (a Hamlet has 3 Wards, Natural Holdings only)."
                        + (" Wards are not placed on the map." if WARD_MODEL == "abstract" else " Each Ward occupies a Territory within Range 1 of the Settlement.")),
    CHAIN_TERM + " X": ((f"On a Holding tile: placed in the same Settlement Ward as X (the Raw Material or Holding named on it), it shares "
                        f"that Ward instead of taking its own. See {CHAIN_TERM}.")),
})

# ── Glossary: Public Order bands and modifiers, Tax Income, Convert — read from PO_BANDS / PO_MODIFIERS / SETTLEMENTS / ACTIONS ──
_PO_SC = {lvl: [int(e.get("po_scale_neg" if lvl < 0 else "po_scale_pos", 1)) for e in ERAS.values()] for lvl in PO_BANDS if lvl}
PO_GLOSS_TERMS = [nm for lvl, (nm, t, _b) in sorted(PO_BANDS.items()) if t != "No effect"] + [k for v in PO_MODIFIERS.values() for k in v]
GLOSSARY.update({
    nm: (f"Public Order band ({'+' if lvl > 0 else ''}{lvl}{'' if lvl in (PO_MIN, PO_MAX) else ' or lower' if lvl < 0 else ' or higher'}): {po_effect(lvl)}"
         + (f", scaled by Era (" + " / ".join(f"×{x}" for x in _PO_SC[lvl]) + f" from {next(iter(ERAS))} to {list(ERAS)[-1]})"
            if b is not None and "{n}" in t and any(x != 1 for x in _PO_SC[lvl]) else "") + ".")
    for lvl, (nm, t, b) in PO_BANDS.items() if t != "No effect"})
GLOSSARY.update({k: f"{side.title()} 1 each Empire Phase: {d[0].lower() + d[1:]}." for side, v in PO_MODIFIERS.items() for k, d in v.items()
                 if k not in GLOSSARY})   # War Weariness keeps its own entry
GLOSSARY["Tax Income"] = (f"Gold each {TRADE_RULES['tax_season']} from each of your Settlements by tier: "
                          + ", ".join(f"{k} {v['tax_income']}" for k, v in SETTLEMENTS.items() if v.get("tax_income")) + ".")
GLOSSARY["Convert"] = f"A {ACTIONS['Convert']['domain']} action ({ACTIONS['Convert']['requires']}). {ACTIONS['Convert']['effect']}"

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
    "Artillery Park": "Ordnance Yard",
    "Coliseum": "Drill Yard",
    "Javelin": "Throwing Axe",
    "Crafted" : "Tempered",
    #"Gambeson": "Padded",
    #"to-hit", "to-Strike",
    #"Recover", "Heal",
    "Preceptory of the Knight's Templar": "Sacred Preceptory",
    "Knight's Templar": "Oathsworn Knight",
    "Knight Templar": "Oathsworn Knight",
    "Recover": "Heal",
    "RECOVER": "HEAL",
    "Recovered" : "Healed",
    "Reliquary": "Reliquary Sanctum",
    "TH": "To Strike",
    "TS": "Armor Save",
    "The Eternal Sepulchre": "The Exalted Basilica",
    "Exalted Basilica":"Eternal Sepulchre",
    "High Chancery": "The Grand Tribunal",   # Wonder atop Town Hall -> Library -> Magistrate's Hall
    "Embassy": "Chancery",                   # Statecraft line: an embassy's office; refuses to seal a Diplomacy action
    "Storehouse":"Labor Fief",
    "Census Hall":"Tally House",
    "Burgages":"Villein Hovels",
    "The Grand Exchange":"The Center of Commerce",

    

    
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
    (1, 4):  "Raze",
    (5, 6):  "Intercept Caravan",
    (7, 8):  "Sabotage",
    (9, 10): "Destabilize",
}

def bandit_cunning_ranges(faces=None): return die_table_ranges(BANDIT_CUNNING_TABLE, faces)
def bandit_cunning_rows(faces=None):   return die_table_rows(BANDIT_CUNNING_TABLE, faces)
def bandit_cunning_lookup(roll, faces=None): return die_table_lookup(BANDIT_CUNNING_TABLE, roll, faces)

def bandit_cunning_text(faces=None):
    faces = BANDIT_FACES if faces is None else faces
    return (f"If {BANDIT_CUNNING_MIN}+ retinues in camp, roll a d{faces} each turn: "
            f"{die_table_text(BANDIT_CUNNING_TABLE, faces)}.")
BANDIT_BEHAVIOR["Cunning Roll"] = bandit_cunning_text()      # the d10 table is the rule; the prose follows it

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
    f"Battle. Bandits never Fall Back but may Rout as normal. Winning the Battle destroys the camp and Extorts its whole treasury."
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
    "Natural": f"A Holding property: it pays no {UPKEEP_TERM} and may be built in a Hamlet.",
    SUPPLY_TERM: ((f"Gold you pay each Empire Phase for your Armies: each Army's cost by Retinue type, minus every "
                   f"{SUPPLY_TERM} -X (never below 0). Holdings and Infrastructure pay {UPKEEP_TERM} instead.")),
    UPKEEP_TERM: ((f"Gold you pay each Empire Phase for your Holdings and Infrastructure. Holding {UPKEEP_TERM} {_HOLDING_COST_TEXT}; "
                   f"each Infrastructure lists its own. Nothing is paid while a piece is inactive (being built, Damaged, under Repair "
                   f"or {SHUTTER_TERM}). {UPKEEP_TERM} -X lowers the total, never below 0.")),
    "Craft":   ((f"Your trade value, from every effect that gives Craft +X. For each active Trade Agreement, both players gain "
                f"{TRADE_RULES['income_per_craft']} × the Host's Craft.")),
    CHAIN_TERM: ("A Holding's " + CHAIN_TERM + " is the line of Holdings it builds from, usually running from a Raw Material "
                 "up to a Monument. You may start building a Holding only while you control one complete line of its "
                 + CHAIN_TERM + ", anywhere in your empire; this is checked only when you start it. A Holding placed in the "
                 "same Settlement Ward as its immediate parent shares that Ward, and the chain can continue upward the same way. "
                 "Each Holding carries at most one descendant in its Ward. (Core Principle 13.)"),
    SHUTTER_TERM: (f"A Holding or Infrastructure set inactive while you're Insolvent because its {UPKEEP_TERM} went unpaid. "
                   f"It gives no effect and pays no {UPKEEP_TERM}, but its {UPKEEP_TERM} still counts toward what you owe. It's restored at "
                   f"any Yields & Expenditures step where you can pay its {UPKEEP_TERM}. If it becomes Damaged, it's no longer {SHUTTER_TERM}."),
    "Speed X":         f"An Army's movement in Territories per Move action. Base Speed is {RETINUES['Levy']['speed']}.",
    "Pursuit":   (f"A building you Build into a Settlement Ward, or into its {CHAIN_TERM} parent's Ward. Its effect applies while it's active."),
    "Retinue":   "A single unit within an Army, represented by a single die roll for Strikes, Saves, etc.",
    "At War":    "Two players At War can't trade, and may Battle, Lay Siege on and Pillage each other.",
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
GLOSSARY["Root"] = (f"A Holding with no {CHAIN_TERM} requirement: you may start it without controlling a parent. "
                    f"If it names a {CHAIN_TERM} parent, it may still share that Holding's Settlement Ward.")


# ── Rest Phase gains (turn strip / Table End turn) ─────────────────────────────────────────────
RENOWN_MAX = 30              # Renown stops here; the game continues but no more Renown is gained
RENOWN_PER_TURN = 1          # Rest Phase step 3 "Gain Renown" — the rules don't state an amount; set here
DOMAIN_POINTS_PER_TURN = 1   # Rest Phase step 4 / Key Resources: "Domain Points — earned 1 per turn"
# Most Domain Points one player gains over the game (independent of Renown, which also rises with Edicts).
# Points also stop once Renown is at RENOWN_MAX, and while every Domain is at its maximum (Sovereign).
# DOMAIN_MAX = RENOWN_MAX - 1 matches one point per Renown step from the start.
DOMAIN_MAX = 20
GLOSSARY["Domain Point"] = (GLOSSARY["Domain Point"].replace("{DOMAIN_POINTS_PER_TURN}", str(DOMAIN_POINTS_PER_TURN))
                            + f" You gain none once you have gained {DOMAIN_MAX}, once Renown is at {RENOWN_MAX}, or while every Domain is at its maximum.")

# ── AI PLAYERS (draft) ───────────────────────────────────────────────────────
# Decision priorities shared by every AI player, highest first. A culture changes HOW a priority is met
# (its Domains, actions, Monuments), not the order. Read by the board's bot seats and the headless simulator.
AI_DOMAIN_POINTS = ("Spend Domain Points one Standing at a time, toward whatever the next priority needs. "
                    "Any culture may take Rising Industry if a priority needs it.")
AI_PRIORITIES = [
    ("economy",    "Be cash positive until next Winter: build income, cut upkeep, or spend less — in the culture's own ways."),
    ("bandits",    "Manage Bandits: build Cunning Holdings, Armies, Walls and modifiers against them; weighted by the local threat."),
    ("faith",      "Keep Public Order above the bands that hurt the plan (AI_FAITH_AVOID)."),
    ("diplomacy",  "Treat with like-minded cultures (AI_DIPLOMACY by Domain)."),
    ("holdings",   "Build the Holdings the priorities above (and Monuments / Edicts below) need."),
    ("infra",      "Build Infrastructure that helps those priorities."),
    ("monuments",  "Build up toward the culture's Monuments."),
    ("edicts",     "Act toward Edicts (e.g. Declare War to Vassalize)."),
]
# Public Order band (PO_BANDS key) to stay above, and when: always, or only while that band's effect matters to the plan
AI_FAITH_AVOID = [
    (-10, "always"),
    (-8,  "economy"),      # Recession: tax income — avoid when it keeps the economy priority met
    (-6,  "speed"),        # Aimless: Speed — when the plan needs Armies to move
    (-4,  "influence"),    # Indecisive: Influence — when the plan needs Influence
    (-2,  "battle"),       # Shaken — before Battle actions
]
# How each Domain meets a priority (a culture with several Domains uses all of its Domains' ways). Tags the AI scores:
#   holding_income  Build Holdings that make gold          trade          Trade Agreements, trade Holdings
#   infra_upkeep    Holdings that cut Infrastructure upkeep army_upkeep   Holdings with Upkeep -N (Armies)
#   bandit_hunt     Armies hunting Bandit Camps             battle         winning Battles / Declare War
#   pillage         Pillage                                 sack           Lay Siege to (sack / capture) Settlements
#   extort          Cunning actions and Extort Holdings     damage         Raze / Sabotage / Intercept / Destabilize
#   hamlet_income   basic (root) Holdings that make gold    tithe          Tithe
#   low_costs       low-upkeep builds
#   po_cheap        raise Public Order as high as it goes, only through cheap means (low upkeep or paying Holdings)
#   po_saints       raise it to the maximum (Living Saints Edict)   po_above_rivals  keep it above every rival's
#   martial_lowers  war, Moves and Pillage to drag rivals down       cunning_lowers   Cunning actions against rivals
#   war_lowers      war and Doubt actions to lower others'          po_control       Piety actions as leverage on others
#   po_insulate     Holdings that shield you from Doubt
#   walls           Walls (Improve)                         ignore_siege   Holdings against Sieges (Office of Works)
#   equip_armies    combat Holdings for better-equipped Armies   train / basic_armies  Muster
#   harness         Bandit Holdings and Foster Rebellion
AI_STYLE = {
    "economy": {
        "Industry": ["holding_income", "trade", "infra_upkeep", "army_upkeep"],
        "Prowess":  ["bandit_hunt", "army_upkeep", "battle", "pillage", "holding_income", "sack", "infra_upkeep"],
        "Cunning":  ["extort", "damage", "holding_income", "trade"],
        "Piety":    ["hamlet_income", "tithe", "trade", "low_costs", "infra_upkeep"],
    },
    "faith": {
        "Industry": ["po_cheap"],
        "Prowess":  ["po_above_rivals", "martial_lowers"],
        "Piety":    ["po_saints", "po_control"],
        "Cunning":  ["po_above_rivals", "cunning_lowers", "po_insulate"],
    },
    "bandits": {
        "Industry": ["walls", "ignore_siege", "equip_armies"],
        "Prowess":  ["train", "bandit_hunt"],
        "Cunning":  ["harness"],
        "Piety":    ["walls", "basic_armies"],
    },
}
# Archetype (CULTURES[...]["archetype"] = "<pace> <style>") in the AI loop — DRAFT weights, tune freely.
#   prio: × a priority's value · tags: × an action carrying that style tag · reserve: gold kept back when planning
#   lead: × actions in the culture's lead Domain · need_amp: × the most-needed of economy / faith / bandits · vote: × Influence spent
AI_ARCHETYPE = {
    # pace
    "Pure":      {"lead": 1.3},                                                     # leans on its one Domain
    "Sustained": {"reserve": 4000, "tags": {"low_costs": 1.3}},                     # steady: low upkeep, a cash cushion
    "Fluid":     {"need_amp": 1.4},                                                 # follows whatever is most pressing
    "Scaling":   {"prio": {"holdings": 1.3, "infra": 1.3, "monuments": 1.3, "economy": 0.9}},   # invests now, pays later
    # style
    "Engine":    {"prio": {"economy": 1.2, "holdings": 1.3, "infra": 1.2}},
    "Aggro":     {"tags": {"battle": 1.3, "martial_lowers": 1.3, "pillage": 1.3, "sack": 1.3, "bandit_hunt": 1.2}},
    "Tempo":     {"tags": {"damage": 1.2, "cunning_lowers": 1.2, "extort": 1.2}, "prio": {"bandits": 1.1}},
    "Control":   {"prio": {"faith": 1.2, "diplomacy": 1.2}, "tags": {"po_control": 1.3}, "vote": 1.5},
}
# Gold per turn a bot treats as equal to 1 Public Order per turn when weighing Holdings (Doubt +1 costs this much, Faith +1
# is worth it). DRAFT — tune with the simulator.
AI_PO_GOLD = 800
# Mustering: the best Retinue and gear unlocked; an offensive Army takes a 2H weapon, a defensive one a 1H weapon and a Shield
AI_MUSTER = {"offensive_when": "Prowess culture or at war", "offensive": "2H", "defensive": "1H + Shield"}
# Diplomacy temperament by Domain; a culture with several Domains mixes them
AI_DIPLOMACY = {
    "Prowess":  "Military Alliances with Prowess players, or anyone who helps the economy or faith priorities; "
                "Declare War on militarily weaker empires.",
    "Industry": "Trade with everyone.",
    "Piety":    "Trade readily.",
    "Cunning":  "Opportunist: works the others' deals and changes sides whenever it is placed to benefit.",
}
# AI_PROFILES is built at the end of this file, from CULTURES.


# ── DRAFTS — finish the wording, then uncomment ─────────────────────────
# Rules prose lives in RULES_push_simple.md.
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


# ── Pursuit -> PURSUIT_TERM: the data above says "Holding". These display aliases make literals that still say
# "Pursuit" elsewhere (wiki, compendium, rules docx, PDFs, dict keys such as GLOSSARY["Pursuit"]) print "Holding".
_PS, _PP = PURSUIT_TERM
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
# Constant-keyed terms use their constants.
# ── Glossary: turn, war, economy and empire terms (after ERAS, SEASONS, SETTLEMENTS, INFRA_TIERS) ──
GLOSSARY.update({
    "Renown":          (f"The shared progress track. Gain {RENOWN_PER_TURN} per Rest Phase; thresholds raise the Era ("
                        + ", ".join(f"{k} {v['renown']}" for k, v in ERAS.items() if v["renown"] > 1) + ")."),
    "Era":             f"The stage of the game, set by Renown: {', '.join(ERAS)}. It sets Envoys, Influence and other limits.",
    "Season":          f"{', '.join(SEASONS)}: one per turn, each with its own effect; the Rest Phase advances it.",
    "Empire Phase":    f"The first phase of the turn: Timers, Bandits, Influence and Envoys, income, {SUPPLY_TERM} and {UPKEEP_TERM}, then Public Order.",
    "Envoy Phase":     "Every player sends their Envoys; they are voted on, then resolved Domain by Domain.",
    "Battle Phase":    "Battles and Sieges begun this turn resolve.",
    "Rest Phase":      "The end of the turn: discard unused Envoys and Influence, advance the Season, score Renown and a Domain Point, pass the Host.",
    "Treasury":        "The gold you Control.",
    "Insolvent":       (f"You couldn't cover a cost in full: pay what you can, disband Armies, then set buildings {SHUTTER_TERM}. "
                        "Build Timers halt. It ends once your Treasury is above 0 and you can pay everything you owe."),
    "Bankrupt":        ("Insolvent with nothing left to cut: your Treasury goes negative by the debt. You can't spend gold (no actions with a "
                        "gold cost) or be Extorted, and Revenue pays the debt first. It ends when your Treasury reaches 0."),
    "Trade Agreement": "A Treaty that lets two players trade. While both can trade, each gets Trade Income each turn either of them is Host.",
    "Trade Partner":   "A player you have a Trade Agreement with and can trade with.",
    "Settlement":      ("A Village, Town, City or Metropolis (or your Hamlet). It earns Tax Income each Winter, holds Holdings in its Wards, "
                        "has a Muster Limit, and controls Territory by its Reach."),
    "Hamlet":          f"Your farmland Settlement, placed at setup: no Tax Income or Muster Limit, {SETTLEMENTS['Hamlet']['wards']} Wards for Natural Holdings only.",
    "Army":            f"Retinues on the map under your Control. Armies Move, Battle and Lay Siege, and pay {SUPPLY_TERM} by Retinue type.",
    "Infrastructure":  (f"An empire-wide building that applies to every Settlement you have. {len(INFRA_TIERS)} tiers, {INFRA_TIERS[0]} "
                        f"to {INFRA_TIERS[-1]}; each needs one active Infrastructure of the tier below."),
    "Wonder":          "Wondrous-tier Infrastructure, one per game. Several players may build the same Wonder; the first to finish takes it.",
    "Damaged":         f"A Holding or Infrastructure hit by Raze, Sack or Bandits: it has no effect and pays no {UPKEEP_TERM} until Repaired.",
    "Lay Siege":       "A Move that ends Adjacent to an at-war Settlement, starting its Siege Timer.",
    "Capture":         "When a Siege resolves in your favor: set a Capture Timer; when it resolves, the Settlement comes under your Control.",
    "Sack":            (f"When a Siege resolves in your favor: Damage the top Holding of each Ward, Extort {SACK_EXTORT_PER_TIER} per "
                        "Settlement tier, reduce it one tier and remove one Ward."),
    "Pillage":         ("A Prowess action: while your Army stays within Reach of an at-war Settlement, it Extorts that "
                        "Settlement's Holding income each Empire Phase, until it Battles, Lays Siege or Marches."),
})

GLOSSARY_CATEGORIES = [
    ('Reading the Rules', ['Targeting you', 'Perform', 'Resolve', 'Cost / Pay', 'Unmodified roll', 'Modified roll', PIVOTAL]),
    ('Turn & Phases', ['Host', 'Era', 'Season', 'Empire Phase', 'Council Phase', 'Envoy Phase', 'Intrigue Phase', 'Tally Phase',
                       'Battle Phase', 'Rest Phase']),
    ('Envoys & Voting', ['Influence', 'Authority X', 'Envoy', 'Personal Envoy', 'Council Envoy', 'Vote', 'Support X', 'Oppose X',
                         'Max Influence', 'Abstain', 'Net Influence', 'Condemned', 'Failed', 'Passed', 'Endorsed', EXPOSED + ' X']),
    ('Domains & Scoring', ['Renown', 'Domain', 'Domain Point', 'Standing', 'Standing Rank', 'Edict']),
    ('Actions', ['Muster', 'Build', 'Improve', 'Repair', 'Settle', 'Expand', 'Move', 'Demand Tribute', 'Diplomacy', 'Convert']),
    ('Treaties', ['Treaty', 'Alliance', 'Vassal', 'Suzerain']),
    ('War', ['At War', 'Lay Siege', 'Siege', 'Capture', 'Sack', 'Pillage', 'Sally Forth']),
    ('Economy & Public Order', ['Treasury', SUPPLY_TERM, UPKEEP_TERM, 'Insolvent', 'Bankrupt', SHUTTER_TERM, 'Trade Agreement', 'Trade Partner',
                                'Craft', 'Can Trade', 'Public Order', 'Faith X', 'Doubt X', 'Extort X', 'Recoup X', 'Tax Income', 'Wavering Devotion']
                               + PO_GLOSS_TERMS),
    ('Settlements & Holdings', ['Settlement', 'Hamlet', 'Settlement Ward', 'Pursuit', 'Root', 'Natural', 'Monument', CHAIN_TERM,
                                CHAIN_TERM + " X", 'Infrastructure', 'Wonder', 'Damaged']),
    ('Timers', list(TIMERS)),
    ('Map & Range', ['Realm', 'Region', 'Territory', 'Province', 'Border', 'Controlled', 'Contested', 'Uncontested', 'Uncontrolled', 'Range X', 'Within', 'Adjacent', 'Next to', 'Reach X']),
    ('World', ['Bandit', 'Outlaw Country', 'Wild Outlaw Country']),
    ('Army States', ['Army', 'Retinue', 'Garrison', 'Speed X', 'Presence', 'Blocked', 'Strained']),
    ('Battle Structure', ['Battle', 'Skirmish', 'Attacker / Defender', 'Seize the Initiative', 'Tactic', 'Field', 'Casualty', 'Initiative', BLUNDER, 'Strike', 'to-Strike number', 'AP', 'Save', 'Endurance', 'Fatigued', FATIGUE_TOKEN, 'Morale', 'Break check', 'Panic check', 'Rout', 'Fall Back']),
    ('Combat Keywords — Defense', [PARRY, RIPOSTE, RECOVER, ENDURING, MINUS_1_TBH, PLANISHING]),
    ('Combat Keywords — Offense', [SHATTER_ARMOR, CLEAVE, POISON, DESTROY_SHIELD, UNSTOPPABLE, SERRATED]),
    ('Combat Keywords — Handling', ['Equipped', STEADY, UNWIELDY, NIMBLE, DRILLED, TWO_H, DUAL_WIELD, 'Dual-equip', FLORENTINE, NO_PARRY, ONE_SHOT]),
    ('Combat Keywords — Immune / Negate', ['Immune [keyword]', 'Negate [keyword]']),
    ('Equipment Tiers', [k for k in map(str, GLOSSARY) if k.split()[0] in {display_tier(x) for x in TIERS} | set(globals().get("ITEM_TIER_DISPLAY", {}).values()) or k == "Ranged Weapons"]),
]

# ── WIKI_NOLINK: glossary terms that read as everyday words; the wiki never auto-links them in prose ──
# (they keep their glossary entry; link them by hand if a sentence needs it)
WIKI_NOLINK = ["Within", "Adjacent", "Next to", "Perform", "Save", "Field"]

# ── GLOSSARY_SEE: glossary terms whose full rule lives in the rules prose ──
# The rules-doc / wiki glossary tables print the term's first sentence + "See <rule> (<section>)" instead of
# repeating the rule; GLOSSARY keeps the full text for cards, board tooltips and {{TERM:}}/{{DEF:}}.
# Value = anchor id: a {{RULE:id}} marker in the rules md, or a heading slug ("council-phase").
# A (short text, anchor) tuple overrides the first-sentence default. Checked by
# `rule_numbers.py <rules.md> --check` and gen_settlement_board --check-rules. The {{RULE:}} anchors live in
# RULES_push_simple.md.
GLOSSARY_SEE = {
    'Host': 'host',
    'Influence': 'influence', 'Envoy': 'sending-an-envoy',
    'Council Phase': 'council-phase', 'Council Envoy': 'council-envoy', 'Intrigue Phase': 'intrigue', 'Tally Phase': 'tally',
    'Vote': 'vote', 'Support X': 'vote', 'Oppose X': 'vote', 'Abstain': 'vote',
    **{t: 'envoy-resolution-table' for t in ('Net Influence', 'Condemned', 'Failed', 'Passed', 'Endorsed')},
    'Renown': 'renown-track', 'Domain': 'domain-standings', 'Domain Point': 'domain-standings',
    'Standing': 'domain-standings', 'Edict': 'how-to-win-edicts',
    'Settle': 'industry-actions', 'Expand': 'industry-actions', 'Build': 'industry-actions',
    'Improve': 'industry-actions', 'Repair': 'industry-actions',
    'Muster': 'prowess-actions', 'Move': 'prowess-actions', 'Demand Tribute': 'prowess-actions',
    'Diplomacy': 'diplomacy-actions',
    'Treaty': 'treaties-alliances', 'Alliance': 'treaties-alliances', 'Vassal': 'vassalization', 'Suzerain': 'vassalization',
    'Public Order': 'public-order', 'Faith X': 'public-order', 'Doubt X': 'public-order',
    SUPPLY_TERM: 'treasury-upkeep', UPKEEP_TERM: 'treasury-upkeep', SHUTTER_TERM: 'insolvency-bankruptcy', 'Craft': 'who-can-trade', 'Can Trade': 'who-can-trade',
    'War Weariness': 'innate-public-order-modifiers',
    'Settlement Ward': 'settlement-wards', CHAIN_TERM: 'mastery-chain', CHAIN_TERM + " X": 'mastery-chain',
    'Root': 'root',
    **{t: 'timers' for t in TIMERS},
    **{t: 'territory-terrain' for t in ('Territory', 'Province', 'Border', 'Controlled', 'Contested', 'Uncontested',
                                         'Uncontrolled', 'Range X', 'Within', 'Adjacent', 'Next to')},
    'Reach X': 'settlement-reach',
    'Bandit': 'bandits', 'Outlaw Country': 'outlaw-country', 'Wild Outlaw Country': 'outlaw-country', 'Siege': 'siege-warfare',
    'Speed X': 'speed', 'Presence': 'rule-commanding-presence', 'Wavering Devotion': 'rule-wavering-devotion', 'Blocked': 'blocked-armies',
    'Skirmish': 'the-skirmish-steps', 'Seize the Initiative': 'seize', 'Tactic': 'tactic-matrix', 'Field': 'form-line',
    'Initiative': 'initiative', BLUNDER: 'initiative', 'Strike': 'strike', 'to-Strike number': 'strike',
    'Save': 'defend', 'Panic check': 'panic', 'Endurance': 'fatigue', 'Fatigued': 'fatigue', FATIGUE_TOKEN: 'fatigue',
    'Break check': 'fatigue', 'Rout': 'end-skirmish',
    'Era': 'game-structure', 'Season': 'seasons', 'Empire Phase': 'empire-phase', 'Envoy Phase': 'envoy-phase',
    'Rest Phase': 'rest-phase', 'Treasury': 'treasury-upkeep', 'Insolvent': 'insolvency-bankruptcy',
    'Bankrupt': 'insolvency-bankruptcy', 'Trade Agreement': 'who-can-trade', 'Trade Partner': 'who-can-trade',
    'Settlement': 'settlements', 'Hamlet': 'hamlets', 'Infrastructure': 'infrastructure', 'Wonder': 'infrastructure',
    'Army': 'armies-overview', 'Lay Siege': 'beginning-a-siege', 'Capture': 'resolving-a-siege', 'Sack': 'resolving-a-siege',
    'Pillage': 'prowess-actions',
}

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# HOLDING_SIM — Holding semantics for the combat sim, read from NODES (replaces the retired
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
    for wm in _re_disp.finditer(r"Unlocks?\s+(Cavalry Spear|Lance)s?\b", t, _I):
        out.append("weapon:" + wm.group(1).title())
    # "Unlocks Lances regardless of Tier Unlock" (Marshal Tiltyard, Farriery, Skirmish Field): that item ignores its tier
    for wm in _re_disp.finditer(r"Unlocks?\s+([A-Z][\w ]*?)s?\s+regardless of (?:Tier Unlock|Unlock Tier)", t):
        out.append("anytier:" + wm.group(1).strip().title())
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
                     (r"\bDrilled\b", "Drilled"), (r"(?<!Settlements gain )Immune Strained(?! during)", IMMUNE_STRAIN),
                     (r"\+1 to Strike", "Strike +1"), (r"\bgain\s+Immune Unwieldy", IMMUNE_UNWIELDY), (r"\bgain\s+Immune Awkward", "Immune Awkward"), (r"max initiative is increased to 3", "MaxInit3"),
                     (r"Always gains Seize the Initiative", "Seize: first"), (r"Righteous Fervour", "Righteous Fervour"),
                     (r"Unlocks Arquebus", "Artillery Park"), (r"(?:^|;\s*)Initiative \+1\b", "Init +1"),
                     (r"Armies must be equipped with (?:a )?Lance", "Lance only")):
        if _re_disp.search(pat, t, _I): out.append(tok)
    if _re_disp.search(r"two of the same 1H Melee Weapon to gain Dual Wield|\bgain\s+Florentine\b", t, _I): out.append(FLORENTINE)
    m = _re_disp.search(r"Weapons gain (-\d+)\s*AP\b", t, _I)      # e.g. Finery: "Weapons gain -1AP"
    if m: out.append("AP " + m.group(1))
    out += ["Parry +1"] * len(_re_disp.findall(r"Improve Parry by \+1", t, _I))
    m = _re_disp.search(r"Focused Strikes on an? (?:natural|Unmodified) (\d+)\+", t, _I)
    if m: out.append("Crit " + m.group(1))
    m = _re_disp.search(r"Gain Recover (\d+)", t, _I)
    if m: out.append("Recover " + m.group(1))            # base; its "or improve" alternative is not a second grant
    else: out += ["Recover +1"] * len(_re_disp.findall(r"(?:Improve Recover by|Recover improved by)\s*\+1", t, _I))
    if sim:
        if _re_disp.search(r"Every Skirmish, you may force your opponent to reveal", t, _I): out.append("Outrider: every")
        elif _re_disp.search(r"First Skirmish, you may force your opponent to reveal", t, _I): out.append("Outrider: first")
        if _re_disp.search(r"equipped with a Ranged and a Melee Weapon simultaneously", t, _I): out.append("dual-equip")
    return out

def holding_upkeep(text):
    """Army-upkeep reductions in a Holding's text: [{"amount": N, "factor": f}] or [{"all": True, "factor": f}]."""
    out = []
    for c in _re_disp.split(r";|\.\s+|\.$", _ht_strip(text)):
        cond = bool(_re_disp.search(r"\b(while|if|when)\b", c, _re_disp.I))
        f = COND_UPKEEP_FACTOR if cond else 1.0
        if _re_disp.search(rf"\bdo(?:es)? not pay {SUPPLY_TERM}\b|\bdon't pay {SUPPLY_TERM}\b", c, _re_disp.I):
            out.append({"all": True, "factor": f}); continue
        m = _re_disp.search(rf"(?<!No )\b{SUPPLY_TERM}\s*-\s*(\d+)", c, _re_disp.I)
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
    for name, v in NODES.items()
}

# Per-culture profile, read straight from CULTURES (no new numbers): Domains, archetype, signature actions,
# Monuments and Wonders to build toward, and the radar ratings as weights.
AI_PROFILES = {c: {"domains": v["domains"], "archetype": v["archetype"], "actions": v.get("actions", []),
                   "monuments": v.get("monuments", []), "wonders": v.get("wonders", []), "radar": v.get("radar", {}),
                   "prowess_coded": "Prowess" in v["domains"]}
               for c, v in CULTURES.items()}

# ── PHASE_REFORM text (runs last, after GLOSSARY_SEE / NAME_DISPLAY) ──────────────────────────────────────────
if PHASE_REFORM:
    GLOSSARY["Council Phase"] = ("The phase after the Empire Phase: clockwise from the starting player, each player performs the Era's "
                                 "Works actions (Industry), paying each cost. They aren't Envoys: no Influence or votes, and each one Passes.")
    NAME_DISPLAY["Council Phase"] = ALIASES["Council Phase"] = "Works Phase"
    _ALIAS_RE = _re_disp.compile(r"(" + "|".join(_re_disp.escape(k) for k in sorted(ALIASES, key=len, reverse=True)) + r")")   # include the rename
    if "Council Phase" in GLOSSARY_SEE: GLOSSARY_SEE["Council Phase"] = "works-phase"
    # no Council Envoys: the Works Phase performs actions directly
    GLOSSARY.pop("Council Envoy", None); GLOSSARY_SEE.pop("Council Envoy", None)
    GLOSSARY_CATEGORIES = [(c, [t for t in L if t != "Council Envoy"]) for c, L in GLOSSARY_CATEGORIES]
    GLOSSARY["Diplomacy Phase"] = ("Spring's Envoy Phase: no Envoys are sent; players make Diplomacy offers to one another. "
                                   "The only time Diplomacy actions happen.")
    GLOSSARY_SEE["Diplomacy Phase"] = "diplomacy-phase"
    GLOSSARY_CATEGORIES = [(c, (lambda i: L[:i + 1] + ["Diplomacy Phase"] + L[i + 1:])(L.index("Envoy Phase")) if "Envoy Phase" in L else L) for c, L in GLOSSARY_CATEGORIES]
    # no Council vote and no Diplomacy Envoys
    GLOSSARY["Envoy"] = "Your means of acting: declare a Domain and spend 1 Envoy, and if it passes, choose and Perform an action of that Domain. Personal Envoys come from your Era (none in Spring)."
    GLOSSARY["Host"] = GLOSSARY["Host"].replace("(Council vote, ", "(")
    GLOSSARY["Max Influence"] = GLOSSARY["Max Influence"].replace(" (the Era's rank on Diplomacy Envoys)", "")
    GLOSSARY["Standing Rank"] = GLOSSARY["Standing Rank"].replace(" Diplomacy uses the Era's rank.", "")
    GLOSSARY["Diplomacy"] = ("Sign Treaty, Negotiate and End Treaty: offers between players in the Diplomacy Phase "
                             "(Spring's Envoy Phase, the only one each year), not sent as Envoys.")
    SEASONS["Spring"]["effect"] = SEASONS["Spring"]["effect"].replace(
        "Council Phase, or Diplomacy Actions.", "or Envoys: the Diplomacy Phase replaces the Envoy Phase, the only time Diplomacy actions happen.")
    for _e in ERAS.values():
        _e["envoys"] = (f"{_e['council_actions_per_envoy']} Works action{'s' if _e['council_actions_per_envoy'] > 1 else ''}"
                        f" + {_e['personal_envoys']} Personal Envoy{'s' if _e['personal_envoys'] > 1 else ''}"
                        f" ({_e['actions_per_envoy']} action{'s' if _e['actions_per_envoy'] > 1 else ''} each) per turn")
