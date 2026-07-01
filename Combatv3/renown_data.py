# renown_data — single source of truth (CSV/0.4.8 branch, card-verified)
# Edit THIS file; equipment.csv, cards, and docs are generated from it.
VERSION = "0.4.9.2.7"
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
ONE_SHOT        = "One Shot"
DEFLECT         = "Deflect"
IMMUNE_PANIC    = "Immune Panic"
UNBREAKABLE     = "Unbreakable"
PARRY           = "Parry"
RIPOSTE         = "Riposte"
RECOVER         = "Recover"
SERRATED        = "Serrated"
ENDURING        = "Enduring"   # Recover still gets a 6+ save while Fatigued (exception to off-when-fatigued)
STRAIN          = "Strain"
MINUS_1_TBH     = "Shielded"
PLANISHING      = "Tempered"
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

NEGATE_TEMPERED    = "Negate Tempered"
NEGATE_RIPOSTE     = "Negate Riposte"
NEGATE_SHIELDED    = negate(MINUS_1_TBH)   # "Negate Shielded": attacker ignores defender's Shielded (-1 to Strike)
MINUS_1_PARRY      = "-1 to Parry"
HALFSWORD          = "Halfsword"   # RESERVED — engine path intact, no weapon carries it (shelved)
DUAL_WIELD         = "Dual Wield"
FLORENTINE         = "Florentine"  # Parry survives Fatigue: degrades to 6+ but is never disabled. Grants Parry. Only active while Dual Wielding.
PIVOTAL = "Focused"


GLOSSARY = {
    STEADY:         "Initiative cannot be reduced by Tactics.",
    UNWIELDY:       "Initiative cannot be improved by Tactics.",
    TWO_H:          "Cannot use a Shield.",
    SHATTER_ARMOR:  f"On a {PIVOTAL} Strike: increase AP by -5, and the defender may Parry or {RECOVER} only with a {PIVOTAL} roll.",
    UNSTOPPABLE:    f"Parried only by a {PIVOTAL} roll.",
    CLEAVE:         f"On a {PIVOTAL} Strike: roll one extra Strike die at your modified to-Strike.",
    POISON:         f"When the Defender receives a Strike and rolls a {PIVOTAL} Save, it fails; the resulting wound may only be {RECOVER}ed with a {PIVOTAL} {RECOVER}.",
    NIMBLE:         "Gain +1 Initiative in the first Skirmish of each Battle.",
    DRILLED:        "Does not lose Endurance in the first Skirmish of each Battle.",
    DESTROY_SHIELD: f"On a {PIVOTAL} Strike: the target loses its Shield attributes for the rest of the Battle.",
    BLUNDER:        "At Initiative -2 or lower, your to-Strike is set to 6+, before other negative modifiers.",
    ONE_SHOT:       "May only be Equipped in the first Skirmish of a Battle. Requires a Tiltyard.",
    #DEFLECT:        "-1 to Parry and Negate Riposte against this weapon's Strikes. (All Ranged weapons have Deflect.)",
    #IMMUNE_PANIC:   "Automatically passes Panic checks.",
    #UNBREAKABLE:    "Immune Break: does not take Break checks while Fatigued.",
    PARRY:          "While not Fatigued, roll a d6 to attempt to Parry a Strike before the Save. On a 5+, the Strike is Parried.",
    RIPOSTE:        "While not Fatigued, if you Focused a Parry against a Melee Weapon's Strike, you Riposte: your opponent immediately takes a Strike from your melee weapon. You can Riposte a Riposte.",
    RECOVER:        "While not Fatigued, if a to-Save roll fails, roll a d6: a result of X+ Recovers the retinue.",
    SERRATED:       "-2 to Recover against this weapon's Strikes (worsens the defender's Recover roll by 2).",
    PLANISHING:     f"A {PIVOTAL} Save succeeds, regardless of AP.",
    FATIGUE_TOKEN:  "Each token is -1 to your Strike to a maximum of 6+; and Morale -1 (uncapped). If your modified Morale is ever 7+, your army Routs. Tokens stack.",
    MINUS_1_TBH:    "A stacking -1 penalty to the Strike roll (to a maximum of 6+). Sources: a shield's -1 to Strike.",
	#NEGATE_UNSTOPPABLE: "Cancels the attacker's Parry from Unstoppable: this shield's -1 to Strike still applies, and the attacker's -1 to Parry does not.",
    NEGATE_TEMPERED: "Ignores Tempered: this weapon's AP can reduce the target's Save past 6+ (to auto-fail), defeating the Tempered floor.",
    NEGATE_RIPOSTE: "The target's Parry can never Riposte this weapon's Strikes (a natural 6 Parry still cancels the Strike, but no counter-Strike follows).",
    #MINUS_1_PARRY: "A stacking -1 penalty to the defender's Parry roll (to a maximum of 6+). Sources: Unstoppable, Deflect, and each Fatigue token.",
    DUAL_WIELD: "A Strike die that fails to Strike is rerolled once; the reroll can Focused Strike. Dual Wield confers 2H (both hands on weapons — no Shield). You cannot reroll successful Strikes.",
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
    "Morale":        "How steady a retinue is when tested (lower is steadier; see the retinue table). Break and Panic checks roll it: a D6 per retinue in the field, up to 5 dice, each must meet its modified value; failures are casualties. If the modified value is ever 7+, the army Routs.",
    "Rout":          "The army breaks and leaves the Battle (you lose it). Whenever an army's modified Morale value reaches 7 or more, it Routs automatically.",
    "Fall Back":     "A controlled retreat that ends the Battle with at least one retinue left — a partial success.",
    "Strike":        "A landed hit. Roll a D6, apply modifiers to the roll, and Strike on a result >= the to-Strike number. The target may then Parry, Save, and Recover.",
    "to-Strike number": "The D6 result a retinue needs to Strike (see the retinue table; lower is better). Bonuses add to the roll; penalties and Fatigue tokens subtract.",
    "Save":          "The defender's roll to avoid a casualty: roll a D6, add the weapon's AP (a negative) and the shield's Save bonus (a positive); the hit is saved on a result >= the armor value.",
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
                    "effect at each band is given by ENVOY_OUTCOMES; an action's own endorsed bonus overrides "
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
    "Domain Point":  "Gained 1 per Rest Phase; spend to raise a Domain value by 1.",
    "Standing":      "Your tier in a Domain: Untested, Rising (3), Established (6), Sovereign (10). Sets max Influence per vote (1/2/3/4) and unlocks Domain effects.",
    "Public Order":  "A track from -5 to 10, adjusted each turn by Faith minus Doubt; its band applies cumulative effects (see the Public Order table).",
    "Reach":         "How far a Settlement projects control, in Territories (by tier). Calculated like Range X",
    "Edict":         "A scoring achievement / win path: reach a Sovereign Standing, complete a Monument, or fulfill a victory condition (Wonder, wealth, Vassalize, Living Saints, Last Standing).",

    # ── World ──
    "Bandit":        "Neutral hostile force; Bandit Camps spawn in Outlaw Country and on low Public Order.",
    "Outlaw Country": "Uncontrollable territories in your starting region where Bandit Camps spawn, starting at 3 and expanding if there is no room to place new Bandit Camps.",
    "Siege":         "Sieging a Settlement with an Army to capture it; does not increment in Winter.",
}

# ── Pivotal: one word for "a natural 6" across all combat effects ─────────────
# Pure synonym — Pivotal carries no mechanics of its own; each keyword does the work.
# Swap the term anywhere by editing this one string. Must be defined before use;
# this .update() form can be pasted anywhere after GLOSSARY and the constants exist.
PIVOTAL = "Focused"


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
#                Fatigue token; failures are casualties. Target 7+ is unmakeable = Rout.
#   Panic check: a side that took >5 casualties this Skirmish rolls once after it
#                Strikes back. (Handled by Immune Panic, not by these four.)
# ─────────────────────────────────────────────────────────────────────────────
MORALE_GLOSSARY = {
    "Unbreakable": "Skips the Break check entirely while Fatigued: never rolls, never takes "
                   "break casualties. BUT still Routs if the morale target climbs to 7+ from "
                   "accumulated Fatigue. Stands fully immune, then collapses all at once — and "
                   "because it stays full-size up to the Rout, it loses MORE soldiers when it "
                   "finally breaks than a unit that bled down gradually.",
    "Unshakable":  "Caps the morale target at 6 permanently. Still TAKES every Break and Panic "
                   "check each Skirmish (keeps bleeding casualties at a 6+ roll), but the target "
                   "can never reach 7, so it NEVER Routs. Bends and bleeds forever, never shatters. "
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
    "Levy":           {"cost": 1000, "to_hit": 4, "endurance": 3, "shaking": 5, "unbreakable": False, "speed": 3, "max_size": ARMY_MAX_RETINUES},
    "Man-at-Arms":    {"cost": 2000, "to_hit": 3, "endurance": 4, "shaking": 5, "unbreakable": False, "speed": 2, "max_size": ARMY_MAX_RETINUES},
    "Sergeant":       {"cost": 2500, "to_hit": 2, "endurance": 3, "shaking": 4, "unbreakable": False, "speed": 2, "max_size": ARMY_MAX_RETINUES},
    "Knight Templar": {"cost": 3000, "to_hit": 3, "endurance": 3, "shaking": 3, "unbreakable": False, "speed": 2, "max_size": ARMY_MAX_RETINUES},
}



WEAPONS = {
    "Farm Tools":     {"ap":  0, "init":  0, "tier": "Crude",   "tags": []},
    "Cudgel":         {"ap": -1, "init": -1, "tier": "Crude",   "tags": [TWO_H, UNWIELDY]},
    "Pitchfork":      {"ap":  0, "init":  1, "tier": "Crude",   "tags": [TWO_H, UNWIELDY]},
    "Daggers":        {"ap":  0, "init":  1, "tier": "Cast",    "tags": [TWO_H, DUAL_WIELD, SHATTER_ARMOR], 'note': "A paired light blade; dual-wields innately (rerolls missed Strikes). No shield."},
    "Short Sword":    {"ap": -1, "init":  0, "tier": "Cast",    "tags": []},
    "Spears":         {"ap": -1, "init":  1, "tier": "Cast",    "tags": [TWO_H, UNWIELDY]},
    "Arming Sword":   {"ap": -1, "init":  0, "tier": "Wrought", "tags": [STEADY]},
    "Pike":           {"ap": -2, "init":  1, "tier": "Wrought", "tags": [TWO_H, UNWIELDY, SHATTER_ARMOR]},
    "Flail":          {"ap": -1, "init":  0, "tier": "Wrought", "tags": [UNWIELDY, CLEAVE]},
    "Halberd":        {"ap": -3, "init":  0, "tier": "Wrought", "tags": [TWO_H, UNWIELDY]},
    "Battle Axe":     {"ap": -2, "init":  0, "tier": "Wrought", "tags": [TWO_H, UNWIELDY, CLEAVE, NEGATE_SHIELDED]},
    "Cavalry Spear":  {"ap": -2, "init":  0, "tier": "Wrought", "tags": [STEADY, UNWIELDY, NEGATE_RIPOSTE], 'note': "Needs Stable; no Tower Shield or Dual Wield or Ranged Weapon"},
    "Morningstar":    {"ap": -3, "init": -1, "tier": "Forged",  "tags": [UNWIELDY, CLEAVE, DESTROY_SHIELD]},
    "Bastard Sword":  {"ap": -3, "init":  0, "tier": "Forged",  "tags": [STEADY, SHATTER_ARMOR]},
    "2HBastard":      {"ap": -3, "init":  0, "tier": "Forged",  "tags": [TWO_H, UNWIELDY, CLEAVE]},
    "War Hammer":     {"ap": -8, "init": -1, "tier": "Forged",  "tags": [TWO_H, UNWIELDY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_RIPOSTE, DESTROY_SHIELD]},
    "Lance":          {"ap": -4, "init":  1, "tier": "Forged",  "tags": [STEADY, UNWIELDY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_RIPOSTE], 'note': "Needs Stable; no Tower Shield or Dual Wield"},
    "Estoc":          {"ap": -3, "init":  1, "tier": "Crafted", "tags": [STEADY, SHATTER_ARMOR, NEGATE_RIPOSTE, NEGATE_TEMPERED]},
    "Poleaxe":        {"ap": -3, "init":  1, "tier": "Crafted", "tags": [TWO_H, STEADY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_TEMPERED]},
}

RANGED = {
    "Hunting Bow": {"ap":  0, "init":  2, "tier": "Crude",   "tags": [TWO_H, NEGATE_RIPOSTE]},
    "Longbow":     {"ap": -1, "init":  2, "tier": "Cast",    "tags": [TWO_H, NEGATE_RIPOSTE]},
    "Javelin":     {"ap": -2, "init":  1, "tier": "Wrought", "tags": [STEADY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_RIPOSTE, ONE_SHOT]},
    "Crossbow":    {"ap": -4, "init":  0, "tier": "Forged",  "tags": [UNWIELDY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_RIPOSTE, ONE_SHOT], 'note': "Tower Shield only (no other shield)"},
    "Pilum":       {"ap": -3, "init":  1, "tier": "Crafted", "tags": [STEADY, SHATTER_ARMOR, UNSTOPPABLE, NEGATE_SHIELDED, NEGATE_RIPOSTE, DESTROY_SHIELD, ONE_SHOT]},
}

SHIELDS = {
    None:            {"save_bonus": 0, "init":  0, "tier": None,     "tags": []},
    "Buckler Shield":{"save_bonus": 1, "init":  0, "tier": "Crude",  "tags": []},
    "Targe Shield":  {"save_bonus": 0, "init": -1, "tier": "Cast",   "tags": [STEADY, MINUS_1_TBH]},
    "Kite Shield":   {"save_bonus": 1, "init": -1, "tier": "Wrought","tags": [UNWIELDY, MINUS_1_TBH]},
    "Tower Shield":  {"save_bonus": 2, "init": -1, "tier": "Forged", "tags": [UNWIELDY, MINUS_1_TBH]},
    "Heater Shield": {"save_bonus": 2, "init":  0, "tier": "Crafted","tags": [MINUS_1_TBH, IMMUNE_DESTROY_SHIELD]},
}

ARMORS = {
    "Cloth":       {"save": 7, "tier": "Crude",   "tags": []},
    "Leather":     {"save": 5, "tier": "Cast",    "tags": []},
    "Chainmail":   {"save": 4, "tier": "Wrought", "tags": []},
    "Full Plate":  {"save": 3, "tier": "Forged",  "tags": []},
    "Gothic Plate":{"save": 2, "tier": "Crafted", "tags": ["Immune Unwieldy"]},
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
    ("Prowess", "Established"): "Parry",
    ("Piety",   "Established"): "+1 Morale",
    ("Cunning", "Established"): "Foes gain Blunder in first Skirmish",
    ("Cunning", "Sovereign"):   "Foes gain Strain",
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
    ("Ambush", "Defensive Formation"):             (_m(TH=-1), _m(TS=1)),
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
    ("Charge", "Defensive Formation"):             (_m(I=-1, TS=-1), _m(I=1, TH=1, TS=1)),
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
    ("Defensive Formation", "Ambush"):             (_m(TS=1), _m(TH=-1)),
    ("Defensive Formation", "Flank"):              (_m(I=-1, TS=1), _m(I=1)),
    ("Defensive Formation", "Charge"):             (_m(I=1, TH=1, TS=1), _m(I=-1, TS=-1)),
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
        "innate": "+100, **Natural**",
        "mastery": "+300",
        "builds_into": ["Saddlery", "Tannery", "Stable", "Weavery", "Butchery"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Saddlery": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land + Animal Husbandry + Stable",
        "innate": "+200, **Natural**",
        "mastery": "**Upkeep -200**; Speed +1",
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
        "escalation": {"standing": "Untested Prowess", "ranks": {1: "Ranged weapons"}, "requires_all": [], "requires_any": [], "extra_req": ""},
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
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Leather armor"}, "requires_all": [], "requires_any": [], "extra_req": ""},
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
        "escalation": {"standing": "Rising Industry", "ranks": {1: "Shields"}, "requires_all": ["Tannery"], "requires_any": [], "extra_req": ""},
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
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Cast weapons"}, "requires_all": [], "requires_any": [], "extra_req": ""},
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
        "escalation": {"standing": "Rising Industry", "ranks": {1: "Wrought weapons"}, "requires_all": ["Furnace"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Furnace"], "domain": {"Industry": 3}, "innate_tags": [], "mastery_tags": ["tier:Wrought"], "mastery_req": ["Furnace"], "efficient": "Furnace"}},
    "Jewelry Foundry": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Mine + Merchant Quarter + Furnace",
        "innate": "+200; Craft +2",
        "mastery": "+500; **Influence +2** to Cunning Envoys targeting this player",
        "efficient": "Gilded Foundry",
        "builds_into": [],
        "monument": False},
    "Armory": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "Tannery + Blacksmith",
        "innate": "**Unlock Wrought** armor & shield",
        "mastery": "**Upkeep -200**; Craft +1",
        "efficient": "Tannery",
        "builds_into": ["Gilded Foundry"],
        "monument": False,
        "escalation": {"standing": "Rising Industry", "ranks": {1: "Chainmail"}, "requires_all": ["Joinery"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Tannery", "Blacksmith"], "domain": {"Industry": 3}, "innate_tags": ["tier:Chainmail"], "mastery_tags": [], "mastery_req": ["Tannery", "Blacksmith"], "efficient": "Tannery", "upkeep_effects": [{"flat": 200}]}},
    "Master Workshop": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Blacksmith",
        "innate": "**Upkeep -200**; Craft +1",
        "mastery": "Add **Serrated** to Weapons",
        "builds_into": ["Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: "Serrated"}, "requires_all": ["Forge"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Blacksmith"], "domain": {"Industry": 6}, "innate_tags": [], "mastery_tags": ["Serrated"], "mastery_req": ["Blacksmith"], "upkeep_effects": [{"flat": 200}]}},
    "Gilded Foundry": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Armory + Blacksmith",
        "innate": "Unlock **Forged** armor and shield.",
        "mastery": f"{PLANISHING}: Your to Save modifier cannot be reduced beyond 6+; Craft +1",
        "efficient": "Armory",
        "builds_into": ["Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: f"Full Plate + {PLANISHING}"}, "requires_all": ["Armory"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Armory"], "domain": {"Industry": 6}, "innate_tags": ["tier:FullPlate"], "mastery_tags": [PLANISHING], "mastery_req": ["Armory","Blacksmith"]}},
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
        "mastery_req": "College of Engineering + Workyard + Shipyard",
        "innate": "**Doubt +2**, +600",
        "mastery": "**Build Timer −2**",
        "builds_into": [],
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
        "innate": "**Faith +1**, +300",
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
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Cavalry weapons"}, "requires_all": [], "requires_any": [], "extra_req": ""},
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
        "escalation": {"standing": "Rising Prowess", "ranks": {1: "Man-at-Arms unlock"}, "requires_all": ["Conditioning Field"], "requires_any": [], "extra_req": ""},
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
        "mastery": "Morale +1.",
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
        "builds_into": ["Pilgrimage Site"],
        "monument": False},
    "Monastery": {
        "type": "Power",
        "unlock": "Established Piety",
        "mastery_req": "Abbey",
        "innate": "**Influence −1** to Piety actions targeting you",
        "mastery": "Other players cannot Oppose your Piety Envoys",
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
        "mastery": "gain Enduring: Your recovers cannot be reduced beyond a 6+ while Fatigued.",
        "efficient": "Infirmary",
        "builds_into": ["Preceptory of the Knight's Templar"],
        "monument": False,
        "escalation": {"standing": "Established Piety", "ranks": {1: f"Recover 4+; {ENDURING}"}, "requires_all": ["Infirmary"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Apothecary", "Infirmary"], "domain": {"Piety": 6}, "innate_tags": ["Recover 4"], "mastery_tags": [ENDURING], "mastery_req": ["Apothecary", "Infirmary"]}},
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
        "builds_into": ["Conditioning Field", "Jester's Court"],
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
        "escalation": {"standing": "Untested Prowess", "ranks": {1: "Nimble"}, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Courtyard"], "domain": {"Prowess": 3}, "innate_tags": [], "mastery_tags": ["Nimble"], "mastery_req": []}},
    "Grand Tournament": {
        "type": "Civic",
        "unlock": "Established Prowess",
        "mastery_req": "Coliseum + Conditioning Field",
        "innate": "**Faith +1**",
        "mastery": "3x/turn: exchange 500 gold for **1 Influence**; Armies gain **Riposte**",
        "efficient": "Coliseum",
        "builds_into": ["Royal Pavilion"],
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Riposte"}, "requires_all": ["Coliseum"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {"Prowess": 6}, "innate_tags": [], "mastery_tags": ["Riposte"], "mastery_req": ["Conditioning Field", "Coliseum"], "efficient": "Coliseum"}},
    "Apothecary": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Herb Garden + Alchemy",
        "innate": "+300",
        "mastery": "Gain Recover 6, or improve Recover by +1.",
        "efficient": "Alchemy",
        "builds_into": ["Infirmary", "Hospitaller"],
        "monument": False,
        "escalation": {"standing": "Untested Piety", "ranks": {1: "Recover 6"}, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": ["Recover 6"], "mastery_req": ["Herb Garden"]}},
    "Infirmary": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Alchemy + Herb Garden",
        "innate": "+200",
        "mastery": "Improve Recover by +1",
        "efficient": "Apothecary",
        "builds_into": ["Hospitaller"],
        "monument": False,
        "escalation": {"standing": "Untested Piety", "ranks": {1: "Recover 5"}, "requires_all": ["Apothecary"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Apothecary"], "domain": {}, "innate_tags": [], "mastery_tags": ["Recover 5"], "mastery_req": ["Alchemy", "Herb Garden"], "efficient": "Apothecary", "upkeep_effects": [{"flat": 100}]}},
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
        "builds_into": ["Court Artist"],
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
        "builds_into": ["Toll House", "Beacon Towers"],
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
        "builds_into": ["Storehouse"],
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
        "innate": "gain Immune Local Unrest (-1PO per Bandit Camp)",
        "mastery": "Bandit Camps in your Outlaw Country don't target you and target other players instead randomly.",
        "efficient": "Secret Cellar",
        "builds_into": ["Thieves' Guild"],
        "monument": False},
    "Black Market": {
        "type": "Secrecy",
        "unlock": "Established Cunning",
        "mastery_req": "Market Square + Smuggler's Nook",
        "innate": "When another player **Extorts** gold from any source: **Extort 200** per 1000 (minimum 100) from that player at the end of that resolution.",
        "mastery": "When another player **Recoups** gold from any source: **Extort 200** per 1000 (minimum 100) from that player at the end of that resolution.",
        "efficient": "Market Square",
        "builds_into": [],
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
        "builds_into": [],
        "monument": False,
        "escalation": {"standing": "Rising Cunning", "ranks": {1: "Poison"}, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Academy", "Alchemy"], "domain": {"Cunning": 3}, "innate_tags": ["Poison"], "mastery_tags": [], "mastery_req": ["Academy", "Alchemy"], "upkeep_effects": [{"flat": 100}]}},
    "Pilgrimage Site": {
        "type": "Energy",
        "unlock": "Rising Piety",
        "mastery_req": "Reliquary + Chandlery",
        "innate": "**Extort 200** every player without a Pilgrimage Site",
        "mastery": "**Doubt +1** to all other players without a Pilgrimage Site",
        "efficient": "Reliquary",
        "builds_into": ["Preceptory of the Knight's Templar"],
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
        "mastery": "Cunning actions against you cannot be **Endorsed**",
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
        "innate": "**Upkeep -200**",
        "mastery": "**Upkeep -300**",
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
        "builds_into": [],
        "monument": False},
    "Citadel": {
        "type": "Power",
        "unlock": "Established Prowess",
        "mastery_req": "Masonry + Granary",
        "innate": "**Siege Timer +1**",
        "mastery": "**Siege Timer +1**, Controlled Settlements gain **Reach +1**",
        "efficient": "Granary",
        "builds_into": ["Imperial Palace"],
        "monument": False},
    "War College": {
        "type": "Power",
        "unlock": "Established Prowess",
        "mastery_req": "Coliseum + Levy Hall + Academy",
        "innate": "Gain **+2 Influence** while At War",
        "mastery": "Unlocks **Sergeants** for Muster",
        "efficient": "Academy",
        "builds_into": ["Ministry of Military Strategy"],
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Sergeant unlock"}, "requires_all": ["Coliseum"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Coliseum", "Levy Hall", "Academy"], "domain": {"Prowess": 6}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Coliseum", "Levy Hall", "Academy"], "efficient": "Academy"}},
    "Forge": {
        "type": "Power",
        "unlock": "Established Industry",
        "mastery_req": "Blacksmith",
        "innate": "Craft +1",
        "mastery": "Unlocks **Forged** Tier",
        "efficient": "Blacksmith",
        "builds_into": ["Master Workshop", "Gilded Foundry", "Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: "Forged weapons"}, "requires_all": ["Blacksmith"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Blacksmith"], "domain": {"Industry": 6}, "innate_tags": [], "mastery_tags": ["tier:Forged"], "mastery_req": ["Blacksmith"], "efficient": "Blacksmith"}},
    "Tiltyard": {
        "type": "Power",
        "unlock": "Established Prowess",
        "mastery_req": "Fletchery + Coliseum",
        "innate": "Armies may be Equipped with a second weapon (a Ranged and a Melee Weapon); the army gains **Unwieldy**",
        "mastery": "Armies gain **Immune Unwieldy**, and may instead equip two of the same 1H Melee Weapon to gain **Dual Wield**, **2H** & **Florentine**: May Parry on a natural 6 while Fatigued.",
        "builds_into": ["Royal Pavilion"],
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Dual-equip; Immune Unwieldy; Dual Wield (two of a kind)"}, "requires_all": ["Fletchery"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Fletchery", "Coliseum"], "domain": {"Prowess": 6}, "innate_tags": [], "mastery_tags": ["Immune Unwieldy", "Florentine"], "mastery_req": ["Fletchery", "Coliseum"]}},
    "Royal Pavilion": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "Grand Tournament + Tiltyard",
        "innate": "Armies gain **Immune Strained**",
        "mastery": "Armies gain **Drilled**",
		"efficient": "Tiltyard",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Prowess", "ranks": {1: "Immune Strain; Drilled"}, "requires_all": ["Tiltyard", "Grand Tournament"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Tiltyard"], "domain": {"Prowess": 10}, "innate_tags": ["Immune Strain"], "mastery_tags": [ "Drilled"], "mastery_req": ["Grand Tournament", "Tiltyard"]}},
    "Imperial Palace": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "Citadel + Execution Dock",
        "innate": "Gain **Immune Border Tension & Invasion**",
        "mastery": "Non-Military Alliance players that border you gain **Doubt +2**",
        "efficient": "Citadel",
        "builds_into": [],
        "monument": True},
    "Ministry of Military Strategy": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "University + War College",
        "innate": "Always gains **Seize the Initiative**, and your opponent doesn't. gain Immune Tactic -1 to Strike",
        "mastery": "Gain +1I & max initiative is 3; Deadly, & Cleave also trigger Focused Strikes on a natural 5.",
        "efficient": "War College",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Prowess", "ranks": {1: "Always Seize the Initiative;  Immune Tactic -1 to Strike", 2: "Gain +1I; your maximum initiative increases to 3. Deadly, & Cleave also trigger on a natural 5."}, "requires_all": ["War College"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {"Prowess": 10}, "innate_tags": ["Seize: first", "Immune Tactic TH"], "mastery_tags": ["Crit 5", "+1I", "MaxInit3"], "mastery_req": ["University", "War College"]}},
    "Thieves' Guild": {
        "type": "Monument",
        "unlock": "Sovereign Cunning",
        "mastery_req": "Market Square + Smuggler's Nook + Secret Cellar",
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
        "mastery_req": "Monastery + Pilgrimage Site + Hospitaller + Abbey",
        "innate": f"Armies gain **{CRUSADER}**: Automatically pass the first Panic Check of every Battle.",
        "mastery": "Unlocks **Knight's Templar** for Muster",
        "efficient": "Monastery",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Piety", "ranks": {1: f"{CRUSADER}", 2: "Knight Templar unlock"}, "requires_all": ["Hospitaller"], "requires_any": [], "extra_req": "Established Prowess"},
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
        "unlock": "Sovereign Industry",
        "mastery_req": "Money Lending + Forgery Workshop + Court Artists",
        "innate": "**Doubt +1** per player who earns more Income than you each turn in the Income step.",
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
    "Advanced Blast Furnace": {
        "type": "Monument",
        "unlock": "Sovereign Industry",
        "mastery_req": "Gilded Foundry + Master Workshop + Blacksmith + Stable",
        "innate": "**Upkeep -500**",
        "mastery": "**Crafted** Tier Unlocked; Craft +2",
        "efficient": "Forge",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Industry", "ranks": {1: "Crafted tier"}, "requires_all": ["Master Workshop", "Gilded Foundry"], "requires_any": [], "extra_req": ""},
        "engine": {"alias": "ABF", "cost": 1, "prereqs": ["Gilded Foundry", "Master Workshop", "Blacksmith", "Stable"], "domain": {"Industry": 10}, "innate_tags": ["ABF"], "mastery_tags": ["tier:Crafted"], "mastery_req": ["Gilded Foundry", "Master Workshop", "Blacksmith", "Stable"], "efficient": "Forge", "upkeep_effects": [{"flat": 500}]}},
    "Cipher Chamber": {
        "type": "Power",
        "unlock": "Sovereign Cunning",
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
        "escalation": {"standing": "Sovereign Cunning", "ranks": {1: "See enemy Tactic before choosing"}, "requires_all": ["Toxicarium"], "requires_any": [], "extra_req": ""},
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
    'The Battering Ram': {'final_cut': True,
                          'inspiration': 'Siege-focused',
                          'feel': 'Offensive, Arrogant',
                          'difficulty': 'Low',
                          'strength': 'Medium',
                          'mechanic': 'Siege Specialist: You begin the game with a Siege Works (no ward, no upkeep, always active Mastery). If a player builds a Citadel, you must Siege it as a Personal Win Condition.',
                          'pair': 'Siege Camp, Royal Pavilion',
                          'complement': 'Senate Hall'},
    'The Boundless Steppe': {'final_cut': False,
                             'inspiration': 'Mongol Horde',
                             'feel': 'Fast',
                             'difficulty': 'Low',
                             'strength': 'Medium',
                             'mechanic': 'Horsemasters: Begin the game with a Stable which does not occupy a Settlement ward, cost Upkeep, and counts as an activated Mastery Effect which cannot be deactivated.',
                             'pair': 'Saddlery, Royal Pavilion',
                             'complement': 'Forge'},
    'The Bandit King': {'final_cut': True,
                        'inspiration': 'Brigands',
                        'feel': 'Scrappy',
                        'difficulty': 'Low',
                        'strength': 'Low',
                        'mechanic': "Friends in Low Places: You begin the game with a Smuggler's Nook which does not occupy a Settlement ward, nor cost upkeep. You always gain its Mastery Effect, which cannot be deactivated. In addition, you may control one Bandit Camp outside your territory each turn. Every turn a Bandit Camp is generated, you may place it in your Outlaw Country instead.",
                        'pair': "Thieves' Guild, Saddlery",
                        'complement': 'Royal Pavilion'},
    'The Crowned Star': {'final_cut': True,
                         'inspiration': 'Reigning Sovereign',
                         'feel': 'Sovereign Voice',
                         'difficulty': 'Low',
                         'strength': 'Medium',
                         'mechanic': "The Monarch: Each Turn, you choose each Council Envoy's Domain. All Envoys you send gain Influence -1.",
                         'pair': 'Senate Hall, Aristocratic Court',
                         'complement': 'Royal Pavilion'},
    'The Crimson Tide': {'final_cut': False,
                         'inspiration': 'Pirate',
                         'feel': 'Pirate Life',
                         'difficulty': 'Low',
                         'strength': 'Medium',
                         'mechanic': 'Sea Lanes: Other players cannot perform Intercept Caravan on you. You begin the game with a Shipyard that does not occupy a Settlement ward, does not cost upkeep, and always has the Mastery Effect, even if you do not have a Water Settlement.',
                         'pair': "Shipyard, Thieves' Guild",
                         'complement': 'Royal Pavilion'},
    'The Entwined Crown': {'final_cut': True,
                           'inspiration': 'Habsburg Dynasty',
                           'feel': 'Diplomatic, Inescapable',
                           'difficulty': 'Low',
                           'strength': 'Medium',
                           'mechanic': 'Royal Marriage: Once per game, you may join an Alliance without unanimous consent, or form an Alliance with a player who is not in one. Whoever is in that Alliance gains Faith +1 and +1 Influence per turn.',
                           'pair': 'Aristocratic Court, Senate Hall',
                           'complement': 'Royal Pavilion'},
    'The Eternal Court': {'final_cut': True,
                          'inspiration': 'Byzantine Empire',
                          'feel': 'Patient & Reserved',
                          'difficulty': 'Low',
                          'strength': 'Medium',
                          'mechanic': 'Patient Court: Your influence is never wasted — unspent influence is not discarded in the Rest Phase. Once the Era is Zenith, you have a cap of 5 on influence you spend per envoy, regardless of your Domain Standing.',
                          'pair': 'Senate Hall, Aristocratic Court',
                          'complement': 'Royal Pavilion'},
    'The Final Word': {'final_cut': False,
                       'inspiration': 'Warlord Council',
                       'feel': 'Cold Steel',
                       'difficulty': 'Low',
                       'strength': 'Medium',
                       'mechanic': 'The Decider: Ignore the Innate Doubt & Influence Modifiers that are triggered for being at War.',
                       'pair': 'Royal Pavilion, Imperial Palace',
                       'complement': 'Senate Hall'},
    'The Gilded Crescent': {'final_cut': False,
                            'inspiration': 'Moorish Caliphate',
                            'feel': 'Egalitarian',
                            'difficulty': 'Low',
                            'strength': 'Medium',
                            'mechanic': 'Prosperity For All: Begin the game with an Inn which does not occupy a Settlement ward, cost Upkeep, and counts as an activated Mastery Effect which cannot be deactivated.',
                            'pair': 'Meadery & Winery, Studium Generale',
                            'complement': 'Royal Pavilion'},
    'The Gilded Path': {'final_cut': False,
                        'inspiration': 'Great Income',
                        'feel': 'Rich Trader',
                        'difficulty': 'Low',
                        'strength': 'Low',
                        'mechanic': 'Silk Road: You begin the game with an Artisan Workshop (no ward, no upkeep, always active Mastery). However, you cannot refuse a Trade Agreement.',
                        'pair': 'Meadery & Winery, Forge',
                        'complement': 'Royal Pavilion'},
    'The Hermit Crown': {'final_cut': False,
                         'inspiration': 'Independent',
                         'feel': 'Independent',
                         'difficulty': 'Low',
                         'strength': 'Low',
                         'mechanic': "Independent, but Ambitious: You Abstain every Vote on other players' Envoys, and other players must use 2 Influence to affect your Envoys by 1. Gain Influence +1 to all Personal Envoys. You cannot vote on Council Envoys.",
                         'pair': 'Studium Generale, Saddlery',
                         'complement': 'Royal Pavilion'},
    'The Illuminated Order': {'final_cut': False,
                              'inspiration': 'Scholarly',
                              'feel': 'Knowledge is Power',
                              'difficulty': 'Low',
                              'strength': 'Medium',
                              'mechanic': 'Knowledge is Power: For every 3 Pursuits, gain +1 Influence each turn.',
                              'pair': 'Studium Generale, Senate Hall',
                              'complement': 'Royal Pavilion'},
    'The Iron Faith': {'final_cut': True,
                       'inspiration': 'Crusader States',
                       'feel': 'Piously Resolute',
                       'difficulty': 'Low',
                       'strength': 'Medium',
                       'mechanic': 'Fortress of Faith: While Public Order is greater than or equal to 3, Lay Siege actions targeting Settlements you Control have Siege Timer +2.',
                       'pair': "Siege Camp, Preceptory of the Knight's Templar",
                       'complement': 'Senate Hall'},
    'The Iron Shore': {'final_cut': True,
                       'inspiration': 'Norse',
                       'feel': 'Scavenger',
                       'difficulty': 'Low',
                       'strength': 'Medium',
                       'mechanic': 'Scavengers: Whether you win or lose a battle, collect the Spoils of War. You may also recoup the cost of the retinues received as Casualties in that Battle. Lastly, whenever you perform the Rrpair action, recoup its cost, even if it only passed.',
                       'pair': 'Royal Pavilion, Shipyard',
                       'complement': 'Forge'},
    'The Iron Throne': {'final_cut': True,
                        'inspiration': 'Defensive',
                        'feel': 'Defensive, Impenetrable',
                        'difficulty': 'Low',
                        'strength': 'Medium',
                        'mechanic': 'Unimpeachable: Begin the game with a Citadel (no ward, no upkeep, always active Mastery). You (or your alliance) cannot perform Declare War or Crusade.',
                        'pair': 'Inquisitorial Palace, Senate Hall',
                        'complement': 'Royal Pavilion'},
    'The Merchant Republics': {'final_cut': True,
                               'inspiration': 'Italian City States',
                               'feel': 'Trade Dependent',
                               'difficulty': 'Low',
                               'strength': 'High',
                               'mechanic': 'Heart of Trade: Begin the game with Stone Roads infrastructure, do not pay Upkeep, and cannot be Razed. In order for any player to be able to trade, they must trade with this player first, unless at War with this player. As soon as another player is eligible, you must attempt to Sign a Trade Agreement once with that player. You may not perform the End Treaty Diplomacy action.',
                               'pair': 'Shipyard, Meadery & Winery',
                               'complement': 'Royal Pavilion'},
    'The Sacred Throne': {'final_cut': True,
                          'inspiration': 'Papal State',
                          'feel': 'Pure and Defensive',
                          'difficulty': 'Low',
                          'strength': 'High',
                          'mechanic': 'Sacrosanct: Players who declare war on you (and their allies) gain an additional Doubt +1.',
                          'pair': "Inquisitorial Palace, Preceptory of the Knight's Templar",
                          'complement': 'Royal Pavilion'},
    'The Tunnellers': {'final_cut': True,
                       'inspiration': 'Dwarves',
                       'feel': 'Mountain Passers',
                       'difficulty': 'Low',
                       'strength': 'Low',
                       'mechanic': 'Tunnellers: You treat mountain territory like grasslands for purposes of movement, and begin the game with a Mine raw material pursuit (no ward, no upkeep, always active Mastery).',
                       'pair': 'Forge, Advanced Blast Furnace',
                       'complement': 'Royal Pavilion'},
    'The Undying Flame': {'final_cut': True,
                          'inspiration': 'Martyrs',
                          'feel': 'Unconvinced',
                          'difficulty': 'Low',
                          'strength': 'Low',
                          'mechanic': "Martyrdom: Your armies Morale cannot be modified beyond 6+, but your armies continue to suffer −1 from Fatigue Tokens. Gain Faith +1 for every player you're at War with and every Battle where you lose 20 or more retinues, win or loss. Gain Immune War Weariness",
                          'pair': "Preceptory of the Knight's Templar, Inquisitorial Palace",
                          'complement': 'Royal Pavilion'},
    'The Verdant Kingdom': {'final_cut': True,
                            'inspiration': 'Industry',
                            'feel': 'Pure Economy',
                            'difficulty': 'Low',
                            'strength': 'High',
                            'mechanic': 'Peaceful & Inventive: You cannot declare war, enter Military Alliances, perform Cunning actions, or build Pursuits that require Prowess or Cunning Standing. In the Income step, gain 100 gold for each Craft Mastery Effect you have active.',
                            'pair': 'Forge, Advanced Blast Furnace, Meadery & Winery',
                            'complement': 'Senate Hall'},
    'The Winter Wolves': {'final_cut': False,
                          'inspiration': 'Vikings',
                          'feel': 'Aggressive, Parasitic',
                          'difficulty': 'Low',
                          'strength': 'Medium',
                          'mechanic': "Danegeld: Your armies do not pay upkeep in enemy territory when you're at war — the enemy player pays the upkeep instead. Do not gain Speed −1 in Winter.",
                          'pair': 'Royal Pavilion, Shipyard',
                          'complement': 'Forge'},
    'The Ancient Wilds': {'final_cut': True,
                          'inspiration': 'Celtic Kingdoms',
                          'feel': 'Oathkeepers',
                          'difficulty': 'Medium',
                          'strength': 'High',
                          'mechanic': 'Highlander Way: Enemy armies gain Speed −1 in your Province. You ignore all Terrain Speed modifiers and may trade without Dirt Roads. You must accept the first Non-Aggression Pact offered by each player or Alliance. If that player later joins an alliance, this condition is considered satisfied for that alliance.',
                          'pair': 'Royal Pavilion, Saddlery',
                          'complement': 'Senate Hall'},
    'The Bloodied Cross': {'final_cut': True,
                           'inspiration': 'Crusading Sect',
                           'feel': 'Holy War Without End',
                           'difficulty': 'Medium',
                           'strength': 'High',
                           'mechanic': 'Prophets of War: May Crusade at Rising Piety instead of Sovereign Piety, and do not have a cap on how many Crusades you may have active. All players receive Doubt +1 per Crusade you are on. You cannot perform convert actions.',
                           'pair': "Preceptory of the Knight's Templar, Inquisitorial Palace",
                           'complement': 'Senate Hall'},
    'The Blazing Standard': {'final_cut': False,
                             'inspiration': 'Teutonic Knight',
                             'feel': 'Crusader Feel',
                             'difficulty': 'Medium',
                             'strength': 'High',
                             'mechanic': "Burning Cross: You begin the game with a Preceptory of the Knight's Templar (no ward, no upkeep, always active Mastery). If you Declared War via Crusade, that player must take a Panic Check at the beginning of every battle after lines are formed. If during the Prowess Envoy phase you do not have an army with 25 Knight's Templars, you must attempt to send an envoy. If it passes, you must muster an army until it has 25 retinues of Knight's Templar.",
                             'pair': "Preceptory of the Knight's Templar, Royal Pavilion",
                             'complement': 'Senate Hall'},
    'The Inner Circle': {'final_cut': True,
                         'inspiration': 'Natural Leader',
                         'feel': 'Strength Through Diplomacy',
                         'difficulty': 'Medium',
                         'strength': 'Medium',
                         'mechanic': 'Palatine: Players who are allied with you gain Influence +1 to their envoys, but you may spend 1 of their Influence each turn, targeting your own envoys if you wish.',
                         'pair': 'Senate Hall, Aristocratic Court',
                         'complement': 'Royal Pavilion'},
    'The Luminous Court': {'final_cut': True,
                           'inspiration': 'Renaissance',
                           'feel': 'Civic Soft Power',
                           'difficulty': 'Medium',
                           'strength': 'Medium',
                           'mechanic': 'Arts & Humanities / Hearts & Minds: Cannot pursue Craft Pursuits. Civic Pursuits gain Craft +1. All Civic Pursuits do not cost Upkeep. This Player must accept a Peace Treaty if offered one.',
                           'pair': 'Studium Generale, Aristocratic Court, Senate Hall',
                           'complement': 'Royal Pavilion'},
    'The Grand Compact': {'final_cut': False,
                          'inspiration': 'Hanseatic League',
                          'feel': 'Peace Through Trade',
                          'difficulty': 'Medium',
                          'strength': 'Medium',
                          'mechanic': 'Mercantile Pact: If anyone Declares War on you, players with Trade Agreements with you must Declare War back or End Trade Agreement.',
                          'pair': 'Shipyard, Senate Hall',
                          'complement': 'Royal Pavilion'},
    'The Pale Throne': {'final_cut': True,
                        'inspiration': 'Undead',
                        'feel': 'Undead',
                        'difficulty': 'Medium',
                        'strength': 'Low',
                        'mechanic': 'Inexorable: Your armies always have Unwieldy and cannot gain Immune Unwieldy, but also gain Recover +1, Speed −1, and Immune Panic. Your Public Order cannot exceed 1.',
                        'pair': "Preceptory of the Knight's Templar, Forge",
                        'complement': 'Advanced Blast Furnace'},
    'The Sublime Gate': {'final_cut': False,
                         'inspiration': 'Ottoman Empire',
                         'feel': 'Mercantile Military',
                         'difficulty': 'Medium',
                         'strength': 'Medium',
                         'mechanic': "Integrated Arms: You may Muster retinues and equipment from your Trade Partners' Pursuits (and Mastery Effects, if active) for their cost when you perform a muster action.",
                         'pair': 'Forge, Advanced Blast Furnace',
                         'complement': 'Royal Pavilion'},
    'The Velvet Hand': {'final_cut': False,
                        'inspiration': 'Patrons',
                        'feel': 'Generous Sponsor',
                        'difficulty': 'Medium',
                        'strength': 'Medium',
                        'mechanic': 'Friends in High Places: At the beginning of the turn, players gain Faith +1 if they supported an envoy you sent and it was passed. And, if it was endorsed, they Extort 500 gold per Era.',
                        'pair': 'Aristocratic Court, Senate Hall',
                        'complement': 'Royal Pavilion'},
    'The Ashen Vale': {'final_cut': True,
                       'inspiration': 'Plague',
                       'feel': 'Sickly',
                       'difficulty': 'High',
                       'strength': 'Low',
                       'mechanic': 'Pestilence: Each bordering player gains Doubt +1, your settlements gain Reach +1, and all retinues gain Poison. You may not pursue an Apothecary, Infirmary, or Hospitaller.',
                       'pair': "Thieves' Guild, Inquisitorial Palace",
                       'complement': 'Royal Pavilion'},
    'The Broken Banner': {'final_cut': False,
                          'inspiration': 'Mercenary',
                          'feel': 'Always for Sale',
                          'difficulty': 'High',
                          'strength': 'Low',
                          'mechanic': 'The Highest Bidder: You cannot Declare War and cannot be the Target of a Declare War action. However you must sign any Military or Defensive Alliance offered to you by the highest bidding player each turn and must be paid each turn. In order to overturn an existing alliance, the player must pay a higher amount than the prior agreement. You cannot sign or end alliances via a Diplomacy action.',
                          'pair': 'Royal Pavilion, Forge',
                          'complement': 'Senate Hall'},
    'The Forked Tongue': {'final_cut': True,
                          'inspiration': 'Deceptive',
                          'feel': 'Two-Faced',
                          'difficulty': 'High',
                          'strength': 'High',
                          'mechanic': 'Masters of Duplicity: You may hold any number of treaties simultaneously with any number of players, regardless of contradiction. Your treaties are never automatically canceled or voided by game events. When a situation arises that would normally force a treaty to be canceled, you may choose which obligation to honor, keeping all other treaties intact. Other players may still end their treaties with you via the End Treaty action.',
                          'pair': "Thieves' Guild, Senate Hall",
                          'complement': 'Royal Pavilion'},
    'The Hall of Masks': {'final_cut': False,
                          'inspiration': 'Doppelganger',
                          'feel': 'Shifting Identity',
                          'difficulty': 'High',
                          'strength': 'High',
                          'mechanic': "Mimic: At the beginning of every player's turn, pick another player's Faction. You gain that Faction for this turn. Next turn, you cannot select that Faction.",
                          'pair': 'Studium Generale, Senate Hall',
                          'complement': 'Royal Pavilion'},
    'The Smoldering Crown': {'final_cut': True,
                             'inspiration': 'Terrorists',
                             'feel': 'Aggressive, Destructive',
                             'difficulty': 'High',
                             'strength': 'Medium',
                             'mechanic': 'Reckless: Gain Influence +2 to all Cunning Envoys when targeting a Player with PO > 0. You begin the game with a Secret Cellar (no ward, no upkeep, always active Mastery). Cannot be in an alliance. Cannot perform Diplomacy actions. If you Send a Prowess envoy, it cannot fail — if condemned, it passes.',
                             'pair': "Thieves' Guild, Inquisitorial Palace",
                             'complement': 'Royal Pavilion'},
    "The Squatters' Crown": {'final_cut': False,
                             'inspiration': 'Insurgents',
                             'feel': 'Mobile Occupier',
                             'difficulty': 'High',
                             'strength': 'Medium',
                             'mechanic': 'Occupy: You start the game with an additional army. All must begin the game placed inside your settlements. You do not control your settlements when you leave them. To collect taxes or use Pursuits, end your turn inside that Settlement. To Occupy a Settlement, begin a Battle adjacent to the city like a Siege — instead, you Battle against the Garrison and Armies at war with you or owned by the same owner. If you win (or there is no force to fight), move inside. In the Upkeep Phase, only pay upkeep on equipment. You count as having all Infrastructure of Occupied Settlements and always count as 3 Trading Pursuits. When you leave a Settlement, you may not re-enter it until you Occupy another Settlement and a Trade Agreement is signed.',
                             'pair': 'Royal Pavilion, Saddlery',
                             'complement': 'Forge'},
    'The Wandering Crown': {'final_cut': True,
                            'inspiration': 'Nomadic',
                            'feel': 'Nomads',
                            'difficulty': 'High',
                            'strength': 'Medium',
                            'mechanic': "Wandering Nomads: Your armies function as settlements, classified as a Band, Tribe, or Horde and upgraded accordingly. You may have one additional army per Era, starting with two. Armies do not require troops to exist and cannot be besieged. Nomads cannot build infrastructure but may build pursuits. Raw Material pursuits within Reach are always considered active and do not take a settlement ward. Each army is considered to have a Muster Field. You may trade so long as your border touches another player's border. Armies count as settlements with a Reach of 3. When an army is destroyed, so is its settlement. You may begin a new army adjacent to any existing army by using either the Charter Settlement or Muster Army actions. Nomads do not pay any upkeep.",
                            'pair': 'Saddlery, Royal Pavilion',
                            'complement': 'Forge'},
    'The Dukedom': {'final_cut': True,
                    'inspiration': 'The Game',
                    'feel': 'King of the Castle',
                    'difficulty': 'High',
                    'strength': 'High',
                    'mechanic': "The Great Arbiter: The Duke begins the game trading with all players under a Non-Aggression Pact. The Duke cannot join alliances, perform Cunning actions, or Declare War. If a player declares war on the Duke, that player's Trade Agreements, Non-Aggression Pacts, and Defensive Alliances are immediately and permanently voided. Their Military Alliance remains intact. All other players simultaneously declare war on that player and their Military Alliance. These cannot be reinstated while at war with the Duke. The Duke sees all private actions, resolves player actions, and manages Bandit Mechanics. If the Duke is eliminated, the game ends. The Duke may optionally choose a faction.",
                    'pair': 'Senate Hall, Aristocratic Court',
                    'complement': 'Royal Pavilion, Imperial Palace'},
    'The Elder Grove': {'final_cut': True,
                        'inspiration': 'Elves',
                        'feel': 'Cautious Quickfighters',
                        'difficulty': 'Low',
                        'strength': 'Medium',
                        'mechanic': 'Wise & Suspicious: Gain Doubt +1; If Public Order is 1+, armies gain +1I, Steady, and Speed +1. Cannot be a member of an alliance.',
                        'pair': 'Forge',
                        'complement': 'Inquisitorial Palace'},
    'The Yew Heart': {'final_cut': True,
                      'inspiration': 'English Longbows',
                      'feel': 'Skilled Volleys',
                      'difficulty': 'Low',
                      'strength': 'Medium',
                      'mechanic': "Archery is a Way of Life: You begin the game with a Fletchery which does not occupy a Settlement ward, nor cost upkeep. You always gain its Mastery Effect, which cannot be deactivated. In addition, your armies must always be equipped with a ranged weapon. Ranged Weapons gain +1 to Strike. Cannot  be equipped with full plate or articulated gothic plate. Cannot use shields. Cannot build a Preceptory of Knight's Templar.",
                      'pair': 'Royal Pavilion',
                      'complement': 'Senate Hall'},
}


# ── INFRASTRUCTURE & WONDERS ───────────────────────────────────────────────
# Empire-level builds (per-settlement infrastructure + unique Wonders).
# Master source — edit HERE; reference sheets are generated from these dicts.
# Tiered upkeep/build values (e.g. '50/100/200') are strings.
INFRASTRUCTURE = {'Dirt Roads': {'upkeep': 0,
                'upkeep_frequency': '—',
                'empire_bonus': 'Can Trade; place Dirt Road Territories in Province; ignore Terrain Speed Modifiers',
                'tier': 'Primitive',
                'build_time': 2,
                'requirement': 'None'},
 'Hitching Post': {'upkeep': 0,
                   'upkeep_frequency': '—',
                   'empire_bonus': 'Craft +1',
                   'tier': 'Primitive',
                   'build_time': 2,
                   'requirement': 'None'},
 'Muster Field': {'upkeep': 100,
                  'upkeep_frequency': '—',
                  'empire_bonus': 'Can Muster',
                  'tier': 'Primitive',
                  'build_time': 2,
                  'requirement': 'None'},
 'Wooden Walls': {'upkeep': 100,
                  'upkeep_frequency': '—',
                  'empire_bonus': '**Influence -1** to **Raze actions** targeting your **settlements**',
                  'tier': 'Primitive',
                  'build_time': 2,
                  'requirement': 'None'},
 'Stone Roads': {'upkeep': 100,
                 'upkeep_frequency': '—',
                 'empire_bonus': 'Ignore Terrain Speed Modifiers; if you start turn on Stone Road gain Speed '
                                 '+2; replaces Dirt Roads',
                 'tier': 'Developed',
                 'build_time': 3,
                 'requirement': 'Dirt Roads'},
 'Town Hall': {'upkeep': 100,
               'upkeep_frequency': '—',
               'empire_bonus': '+1 Influence per turn',
               'tier': 'Developed',
               'build_time': 3,
               'requirement': 'One Tier Primitive'},
 'Bridges': {'upkeep': 0,
             'upkeep_frequency': '—',
             'empire_bonus': 'Armies cross Water Territory at full movement; Stone Roads may be built over '
                             'Water',
             'tier': 'Developed',
             'build_time': 3,
             'requirement': 'One Tier Primitive + Stone Roads'},
 'Garrison': {'upkeep': '200',
              'upkeep_frequency': '—',
              'empire_bonus': 'Local Armies form (10/15/25 by Settlement size). All Garrisons share '
                              'Equipment. Cannot be targeted; may Sally Forth.',
              'tier': 'Developed',
              'build_time': 3,
              'requirement': 'Muster Field'},
 'Stone Walls': {'upkeep': 100,
                 'upkeep_frequency': '—',
                 'empire_bonus': '**Influence -1** to **Destabilize actions** targeting your **settlements**',
                 'tier': 'Sophisticated',
                 'build_time': 4,
                 'requirement': 'One Tier Developed + Wooden Walls'},
 'Keep': {'upkeep': 100,
          'upkeep_frequency': '—',
          'empire_bonus': 'May Muster from Garrison in addition to normal Muster Limits. If so set Garrison '
                          'to 0 and Muster Timer 1. Garrison returns to full when resolved.',
          'tier': 'Sophisticated',
          'build_time': 4,
          'requirement': 'Garrison'},
 'Cathedral': {'upkeep': 100,
               'upkeep_frequency': '—',
               'empire_bonus': 'Faith +1',
               'tier': 'Sophisticated',
               'build_time': 4,
               'requirement': 'Requires 1+ City'},
 'Library': {'upkeep': 200,
             'upkeep_frequency': '—',
             'empire_bonus': 'Influence +1 to Council Envoys',
             'tier': 'Sophisticated',
             'build_time': 4,
             'requirement': 'Town Hall'}}

WONDERS = {'Colossus': {'upkeep': 500,
              'upkeep_frequency': 'per Wonder',
              'empire_bonus': 'You may **support** your own **prowess envoys** before other **players '
                              'vote**. **Armies** move **Speed +2** **Siege Timer -2** gain **Immune '
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
    "Village":    {"tier": 1, "sea_variant": None,        "tax_income": 2000,  "muster_limit": 5, "build_time": 1, "wards": 1, "reach": 1, "notes": ""},
    "Town":       {"tier": 2, "sea_variant": "Sea Town",  "tax_income": 4000,  "muster_limit": 10, "build_time": 2, "wards": 2, "reach": 2, "notes": ""},
    "City":       {"tier": 3, "sea_variant": "Port",      "tax_income": 6000,  "muster_limit": 25, "build_time": 3, "wards": 3, "reach": 3, "notes": ""},
    "Metropolis": {"tier": 4, "sea_variant": "—","tax_income": 10000, "muster_limit": 25, "build_time": 5, "wards": 4, "reach": 4, "notes": "Capital only, requires Sovereign Industry (Titan of Industry)"},
}

# Era progression: shared-Renown thresholds; caps on armies/cities; influence.
ERAS = {
    "Founding":  {"renown": 0,  "armies": 1, "cities": 0, "influence_per_turn": 1, "innate_diplomacy_influence": 0, "envoys": "1 Council + 1 Personal Envoy per turn", "unlocks": ""},
    "Ascension": {"renown": 8,  "armies": 2, "cities": 1, "influence_per_turn": 2, "innate_diplomacy_influence": 1, "envoys": "Council Envoys perform 2 actions of that domain", "unlocks": "May resolve Charter Cities"},
    "Eminence":  {"renown": 18, "armies": 3, "cities": 2, "influence_per_turn": 3, "innate_diplomacy_influence": 2, "envoys": "Personal Envoys perform 2 actions of that domain", "unlocks": "May form Military Alliances"},
    "Zenith":    {"renown": 30, "armies": 4, "cities": 3, "influence_per_turn": 4, "innate_diplomacy_influence": 3, "envoys": "Send 2 Personal Envoys per turn", "unlocks": "May form Defensive Alliances"},
}

# Public Order track (−5..7): state name + effect.
PUBLIC_ORDER = {
    -5: ("Uprising",      "Bandit Camp spawns in your Outlaw Country"),
    -4: ("Recession",     "-1000 Tax Income per Settlement"),
    -3: ("Aimless",       "Speed -1"),
    -2: ("Indecisive",    "-1 Influence"),
    -1: ("Wavering",      "No effect"),
     0: ("Neutral",       "No effect"),
     1: ("Focused",       "No effect"),
     2: ("Confident",     "+1 Influence"),
     3: ("Motivated",     "Speed +1"),
     4: ("Economic Boom", "Tax income +500 per settlement"),
     5: ("Eureka",        "Activate 1 Mastery"),
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
        "Rising":      "Indominable: Once per turn, if you have not sent an Envoy, you may perform a Prowess action; send 1 fewer Envoy this turn (min 0). May use Declare War action.",
        "Established": "Edict of War: All armies gain Parry. Gain Immune State of Alarm (No longer gain Doubt while at War).",
        "Sovereign":   "High Quartermaster: Upkeep -2000. No longer lose Influence while at War. May change equipment on your armies during any upkeep phase where that army is within Province.",
    },
    "Cunning": {
        "Rising":      "Clandestine Councilor: Once per turn, when another player's Envoy is Sent, target a player - that player Abstains.",
        "Established": "Grand Vizier: Players may not target you with Cunning Envoys if your Cunning value is higher. When you perform a Skirmish action, your opponent gains Blunder in the first Skirmish of that Battle.",
        "Sovereign":   "Master Conspirator: Once per turn, if your non-Cunning Envoy passes or is Endorsed, you may instead perform a Cunning action. In Battle, your opponent gains Strained each Skirmish.",
    },
    "Piety": {
        "Rising":      "Divine Mandate: Faith +2.",
        "Established": "Prophet of Retribution: All other players gain Doubt +2 while your Public Order is positive.",
        "Sovereign":   "Pillar of Faith: If your Public Order would go below 3, set it to 3. May use the Crusade action.",
    },
    # Influence scaling by standing (Untested/Rising/Established/Sovereign):
    "max_influence_per_vote":  {"Untested": 1, "Rising": 2, "Established": 3, "Sovereign": 4},
    "innate_influence_own_envoys": {"Untested": 0, "Rising": 1, "Established": 2, "Sovereign": 3},
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
    "requirements": "Players must border each other, have active Dirt Road infrastructure, and a signed Trade Agreement",
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
BANDIT_GROWTH_PER_ERA = {"Founding": 1, "Ascension": 2, "Eminence": 5, "Zenith": 10}

BANDITS = {
    "Bandit Domain Value": "For every 5 Retinues in the Bandit Camp or Army, the Bandit Camp has +1 Cunning and +1 Prowess.",
    "Bandit Camp": f"A collection of Bandits in Outlaw Country, starting with {BANDIT_CAMP_START} Retinues.",
    "Bandit Growth": f"Bandit Camps gain ({'/'.join(str(v) for v in BANDIT_GROWTH_PER_ERA.values())}) Retinues a turn, based on the Era of the Realm.",
    "Bandit Army": f"A Bandit Camp becomes a Bandit Army at {BANDIT_ARMY_THRESHOLD} Retinues. Performs Move actions toward the closest Settlement or Army, laying Siege or Skirmishing if possible, in addition to Bandit Cunning Mechanics. Bandit Armies cannot exceed {BANDIT_ARMY_THRESHOLD}",
    "Spawn a Bandit Camp": "Each Spring, every player gains a Bandit Camp.",
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
VASSAL_EXCHANGE_CAP = 2000  # max gold a Suzerain/vassal may exchange per Empire Phase
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
	"Water": {"Effect": "Must end move after passing over 1 Water Territory (must end on land)", "Raw Materials": ["Fishmongery"]},
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
                   "effect": "Must end Move after crossing 1 Water Territory. Cannot Skirmish or Siege move."},
}
TACTICAL_GLOBAL = ["Any player may Fall Back after the first Skirmish."]

INFLUENCE_GAIN = {
    "Era": {"change": "+1/+2/+3/+4", "notes": "Based on the Current Era"},
    "Trading Partners": {"change": "+1", "notes": "Per Trading Partner."},
    "Alliances": {"change": "+1", "notes": "Per Alliance Member."},
    "Infrastructure tier completed": {"change": "+1", "notes": "Per Infrastructure tier fully completed."},
    "Cunning Standing": {"change": "+1", "notes": "Flat bonus if you have the Cunning Standing."},
    "Fully Mustered Army": {"change": "+1", "notes": "Per active Army of 25 Retinues."},
    "Condemned Envoy last turn": {"change": "-1", "notes": "Per Condemned Envoy last turn."},
    "At War": {"change": "-3", "notes": "While at War."},
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
    "adjacent": "Range 1.",
    "next to": "Range 2.",
    "within": "Range 0.",
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
    # ── PROWESS ──
    "Move": {
        "domain": "Prowess", "cost": "None", "requires": "",
        "effect": "Move an Army up to its Speed in Territories, then choose: March (move up to 2x Speed, −1 Endurance, no other action), Skirmish (end adjacent to a non-allied Army not in a settlement → Battle, Seize the Initiative +1I Skirmish 1), Lay Siege (end adjacent to an at-war settlement → Siege), or Muster (within range 3 of your settlements, not within range 1 of a non-ally, with an active Muster Field → recruit up to combined muster limit; may swap retinues between adjacent allied armies and change equipment).",
        "endorsed": "Perform another Move action (same or different Army).",
        "notes": ["Each Army may be the target of only one Move action per turn.",
                  "Strained armies do not gain +1 Endurance at the start of next turn.",
                  "An Army that Skirmished/Sieged/Mustered cannot act again until that battle/siege/muster timer ends.",
                  "An Army that Skirmished gains +1I in the first Skirmish."]},
    "Declare War": {
        "domain": "Prowess", "cost": "None", "requires": "Rising Prowess",
        "effect": "Choose a non-allied player you have no NAP or active truce with. Both players are now At War. Trade Agreements between you end.",
        "endorsed": "Perform a Move action.",
        "notes": ["If target is in a Defensive Alliance, all members are now at war with you.",
                  "If you are in a Military Alliance, all members Declare War on the target next turn and send 1 fewer envoy next turn."]},
    "Demand Tribute": {
        "domain": "Prowess", "cost": "None", "requires": "",
        "effect": "Choose a non-allied player with no NAP. Negotiate: Target agrees → sign a NAP or Alliance (target's choice of offered terms); Target refuses or fails terms → immediately Declare War on them.",
        "endorsed": "Perform a Move action.",
        "notes": ["Terms may include gold, settlements, territory, treaties, or promises. Promises are unenforceable, but unfulfilled promises trigger the refusal clause."]},
    # ── CUNNING ──
    "Intercept Caravan": {
        "domain": "Cunning", "cost": "2000 gold", "requires": "",
        "effect": "Choose a player. The next turn they are Host, Extort their Trade Income.",
        "endorsed": "Extort 2000.",
        "notes": ["Affects only a single turn's trade income; normal income resumes after."]},
    "Foster Rebellion": {
        "domain": "Cunning", "cost": "2000 gold", "requires": "",
        "effect": "Choose a player. At the next Bandit Mechanic Phase, place a Bandit Camp with 10 retinues in their Outlaw Country.",
        "endorsed": "Extort 2000.",
        "notes": ["If their Outlaw Country has no room, increase it by one territory and spawn there."]},
    "Raze": {
        "domain": "Cunning", "cost": "2000 gold", "requires": "",
        "effect": "Choose another player's settlement. Select one active Pursuit, active Infrastructure, or active Build Timer there — it becomes Damaged; its effects are inactive until Repaired. A damaged Build Timer does not increment until Repaired.",
        "endorsed": "Extort 2000.",
        "notes": ["Wonders have Immune Razed and cannot be targeted."]},
    "Destabilize": {
        "domain": "Cunning", "cost": "2000 gold", "requires": "",
        "effect": "Choose a player. Extort their Tax Income at the beginning of next turn.",
        "endorsed": "Extort 2000.",
        "notes": ["Affects only the next single turn's tax income.",
                  "Act of War: if a Cunning envoy is Condemned while targeting a NAP partner, they may immediately Declare War on the condemned player."]},
    # ── PIETY ──
    "Spread Gospel": {
        "domain": "Piety", "cost": "Doubt 1", "requires": "",
        "effect": "All non-allied players gain Doubt 1. All allied players gain Faith 1.",
        "endorsed": "Gain Faith 1.", "notes": []},
    "Send Missionaries": {
        "domain": "Piety", "cost": "Doubt 1", "requires": "",
        "effect": "Choose a target player or alliance. Outside your alliance → all players in the target alliance gain Doubt 2. Inside your alliance → all other allied players gain Faith 2.",
        "endorsed": "Gain Faith 1.", "notes": []},
    "Tithe": {
        "domain": "Piety", "cost": "Doubt 1", "requires": "",
        "effect": "Choose a player. Extort 10% of their treasury (round down to nearest 100, min 0).",
        "endorsed": "Gain Faith 1.", "notes": []},
    "Convert": {
        "domain": "Piety", "cost": "Doubt 1", "requires": "",
        "effect": "Choose another player's closest non-capital settlement; they must have Public Order −5 or lower. Lay Siege using only settlement-type siege modifiers (Wooden Walls, Stone Walls, Citadel, Garrison, Standing Army) and set a Convert Timer. At 0, the settlement joins your empire (see Capture).",
        "endorsed": "Gain Faith 1.",
        "notes": ["If the target's Public Order rises to 1+ before the timer hits 0, the Convert fails and the timer is removed."]},
    "Crusade": {
        "domain": "Piety", "cost": "Doubt 1", "requires": "Sovereign Piety",
        "effect": "Declare War on a non-ally with no NAP or truce, then immediately perform a Move action with one of your armies.",
        "endorsed": "Gain Faith 1.",
        "notes": ["While a Crusade is active, neither player may Declare War, Sign/End Treaty, Negotiate, or Demand Tribute against each other.",
                  "A player may only be on one active Crusade at a time. It ends only when one involved player is Vassalized."]},
    # ── INDUSTRY ──
    "Build": {
        "domain": "Industry", "cost": "2000 gold", "requires": "",
        "effect": "Choose an unlocked, available Infrastructure; set a Build Timer equal to its build time. On completion it becomes active in all settlements in your province.",
        "endorsed": "Recoup 2000.",
        "notes": ["You must have at least one infrastructure from the prior tier before building the next tier.",
                  "Only one active Build Timer at a time.",
                  "Wonders are built in your capital and require all other infrastructure active when the Build action is performed."]},
    "Repair": {
        "domain": "Industry", "cost": "2000 gold", "requires": "",
        "effect": "Choose a damaged Pursuit or Infrastructure in a settlement you control; set Repair Timer 2. At 0, choose: Restore (reactivate with all effects) or Demolish (remove it, freeing the ward).",
        "endorsed": "Recoup 2000.", "notes": []},
    "Pursue": {
        "domain": "Industry", "cost": "2000 gold", "requires": "",
        "effect": "Choose an inactive settlement ward you control. Select a Pursuit whose prerequisites you meet; set a Build Timer equal to its build time (usually 1). On completion, place the Pursuit; innate effects activate immediately, mastery if all mastery reqs met.",
        "endorsed": "Recoup 2000.",
        "notes": ["You may have only 2 Monument pursuits across your empire.",
                  "Power and unique pursuits have Build Timer +1; Monuments +2; all others Build Timer 1."]},
    "Charter": {
        "domain": "Industry", "cost": "2000 gold", "requires": "",
        "effect": "Choose: Charter a new Village (uncontrolled or in-province non-water/mountain territory, range 4+ from any settlement, not within range 2 of Outlaw Country); Charter a Hamlet (if none, range 2 from capital, non-water/mountain — a Hamlet always allows pursuing Arable Land even if that raw material is not in its region); or Expand an existing non-city settlement by one tier into an adjacent territory (Village → Sea/Town, Sea/Town → Port/City, Port/City → Metropolis), adding a ward.",
        "endorsed": "Recoup 2000.",
        "notes": ["To upgrade to City or Metropolis you must meet that tier's requirements; otherwise set Build Timer 1.",
                  "Hamlets always allow pursuing Arable Land."]},
    # ── DIPLOMACY ──
    "Sign Treaty": {
        "domain": "Diplomacy", "cost": "None", "requires": "",
        "effect": "Ask players to agree; choose one and both sign one of: Peace Treaty (end war, truce timer 5), Trade Agreement (begin trading next turn), Non-Aggression Pact (no Declare War; ending it via End Treaty gives both truce timer 5), or Alliance (join/form/invite to Defensive or Military Alliance).",
        "endorsed": "Perform a Diplomacy action.",
        "notes": ["Acting on behalf of an alliance, End Treaty requires all allies to agree.",
                  "A player may not be in more than one alliance (exception: Masters of Duplicity)."]},
    "Negotiate": {
        "domain": "Diplomacy", "cost": "None", "requires": "",
        "effect": "Propose terms to a target; they agree or refuse. Terms may include gold, settlement ownership, territory, treaty sign/end, or promises (non-binding).",
        "endorsed": "Perform a Diplomacy action.",
        "notes": ["Unfulfilled promises let the affected player Declare War on the promiser.",
                  "Also used (automatically, no envoy) to resolve Demand Tribute and siege surrenders."]},
    "End Treaty": {
        "domain": "Diplomacy", "cost": "None", "requires": "",
        "effect": "Choose a target with an active treaty signed with you; that treaty is removed. Does not require the target to agree.",
        "endorsed": "Perform a Diplomacy action.", "notes": []},
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
    "A player cannot be in more than one alliance at a time (exception: Masters of Duplicity).",
    "An alliance may cast out a member via End Treaty if all others agree.",
]

# ── EDICTS / WIN CONDITIONS ──────────────────────────────────────────────────
# Completing an Edict raises the Renown tracker by 1. Any Edict may be completed
# multiple times. Whoever has completed the most when the Last Alliance Standing
# condition is met wins.
EDICTS = {
    "Sovereign Standing": {"type": "Standing",  "requirement": "Reach a Sovereign Standing (Domain value 10) in any Domain."},
    "Monument":           {"type": "Build",     "requirement": "Complete (build) a Monument pursuit."},
    "Wonder":             {"type": "Build",     "requirement": "Complete a World Wonder."},
    "Wealth":             {"type": "Economy",   "requirement": "Generate 10,000 gold per turn for five consecutive turns."},
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
    "Domain Value":  "+1 Cunning and +1 Prowess per 5 retinues in the camp (e.g. 30 retinues = 6 Cunning = Established).",
    "At War":        "All players are At War with all bandits. Players Abstain all bandit actions, but innate modifiers can still cause them to Fail.",
    "Cunning Roll":  "If 10+ retinues in camp, roll a d3 each turn: 1 = Intercept Caravan, 2 = Raze, 3 = Destabilize.",
    "Treasury":      "Bandit camps keep Extorted gold in their treasury and pay no costs or upkeep. Destroying a camp/army Extorts its treasury.",
    "Army Behavior": "After bandit mechanics, a Bandit Army performs a Move: Skirmish (player army in range) > Lay Siege (player settlement in range) > March (toward closest army/settlement). Host breaks range ties.",
    "Attacking":     "Move to end adjacent to a camp; another player rolls bandit tactics (d6, 7 = Fall Back) and resolves to-hit/save as a Battle. Bandits never Fall Back but may Flee. Extort the camp's gold if destroyed.",
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
    "Pursuit":        "Fixed by pursuit type: Monument 300, Power 200, Energy 0, all others 100. Luminous Court zeroes Civic-pursuit upkeep.",
    "Army":           "retinue count x (retinue cost - Upkeep -X). Reduced by Levy Hall (-200/-300), Tannery/Armory/Saddlery/Butchery/Fletchery/Smokehouse (-200), ABF (-500), High Quartermaster (-2000).",
    "Infrastructure": "Per-settlement upkeep in INFRASTRUCTURE. Trade Guild removes Primitive (innate) + Developed (mastery); College of Engineering removes Sophisticated.",
}

# 1) PURSUIT upkeep — fixed by type.
PURSUIT_UPKEEP_BY_TYPE = {
    "Monument": 300,
    "Power":    200,
    "Energy":   0,
}
PURSUIT_UPKEEP_DEFAULT = 100

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
    "Pursuit upkeep":  "Per turn by type (fixed): Monument 300, Power 200, Energy 0, all others 100",
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