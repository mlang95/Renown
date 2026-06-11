# renown_data — single source of truth (CSV/0.4.8 branch, card-verified)
# Edit THIS file; equipment.csv, cards, and docs are generated from it.

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
STRAIN          = "Strain"
MINUS_1_TBH     = "-1 to Strike"
PLANISHING      = "Planishing"
FATIGUE_TOKEN   = "Fatigue Token"

IMMUNE = "Immune"
def immune(keyword):
    """Immunity to a keyword, referencing the canonical name so renames
    propagate. immune(DESTROY_SHIELD) -> 'Immune Destroy Shield'."""
    return f"{IMMUNE} {keyword}"

# convenience aliases for the immunities currently in use
IMMUNE_DESTROY_SHIELD = immune(DESTROY_SHIELD)
IMMUNE_UNWIELDY       = immune(UNWIELDY)
IMMUNE_STRAIN         = immune(STRAIN)

GLOSSARY = {
    STEADY:         "Initiative cannot be reduced by Tactics.",
    UNWIELDY:       "Initiative cannot be improved by Tactics.",
    TWO_H:          "Cannot use a Shield.",
    SHATTER_ARMOR:  "On a natural 6 to Strike, increase the AP by -5. Can only be Parried or Recovered on a natural 6.",
    UNSTOPPABLE:    "Ignore the target shield's -1 to Strike; the target's Parry is -1 against you.",
    CLEAVE:         "On a natural 6 to Strike, you may roll an additional Strike die at your modified Strike value.",
    POISON:         "A natural 6 to Save against this Retinue's Strikes fails.",
    NIMBLE:         "Gain +1 Initiative in the first Skirmish of each Battle.",
    DRILLED:        "Does not lose Endurance in the first Skirmish of each Battle.",
    DESTROY_SHIELD: "On a natural 6 to Strike, target loses Shield attributes for the rest of the Battle.",
    BLUNDER:        "At Initiative -2 or lower, your to-Strike is set to 6+, before other negative modifiers.",
    ONE_SHOT:       "May only be Equipped in the first Skirmish of a Battle. Requires a Tiltyard.",
    DEFLECT:        "Ranged Strikes are -1 to Parry and can never be Riposted.",
    IMMUNE_PANIC:   "Automatically passes Panic checks.",
    UNBREAKABLE:    "Immune Break: does not take Break checks while Fatigued.",
    PARRY:          "Roll a d6 to cancel a Strike before the Save on a 5+ (a natural 6 is a Riposte). -1 versus Unstoppable, versus ranged, and per Fatigue token (to a maximum of 6+).",
    RIPOSTE:        "If you roll a natural 6 on a Parry from a Melee Weapon's Strike, you Riposte: your opponent immediately takes a Strike from your equipped weapon. You can Riposte a Riposte.",
    RECOVER:        "If a to-Save roll fails, roll a d6: a result of X+ saves the retinue. Worsened by Fatigue and Serrated, to a maximum of 6+.",
    SERRATED:       "Your Strikes worsen the enemy's Recover roll by 1.",
    PLANISHING:     "Your armor Save cannot be reduced beyond a 6+.",
    FATIGUE_TOKEN:  "Each token is -1 to your Strike, Parry, and Recover rolls, to a maximum of 6+; and Morale -1 (uncapped). If your modified Morale is ever 7+, your army Routs. Tokens stack.",
    MINUS_1_TBH:    "Attackers Striking this shield-bearer take -1 to the Strike roll.",
    "Immune [keyword]": "Cancels that keyword as it applies to you (e.g. Immune Unwieldy, Strain, Destroy Shield).",

    # ── Combat keywords ported from the Escalation Campaign glossary ──
    "AP":            "Armor Penetration — a weapon's (negative) modifier to the defender's Save roll; the more negative, the harder to save.",
    "Blocked":       "-1 Initiative in the first Skirmish (negated by Immune Blocked).",
    "Strained":      "-1 Initiative every Skirmish (negated by Immune Strain).",
    "Improved Parry": "Your Parry succeeds on 4+ instead of 5+.",
    "Heal X":        "At the end of each Skirmish, for every X casualties you took from Strikes, return 1 retinue to your Army.",
    "Seize the Initiative": "Won by the roll-off at the start of the Battle — the winner of their last Battle adds +1 to the roll. You become the Attacker and gain +1 Initiative in the first Skirmish. Some Tactics and the Ministry monument also grant it.",

    # ── Battle-structure terms (doc glossary, wording updated to current rules) ──
    "Attacker / Defender": "Set by the roll-off. Each Skirmish the Attacker declares equipment first; the Defender then responds.",
    "Battle":        "One fight between two players, resolved as a series of Skirmishes until a side is wiped out, Routs, or Falls Back.",
    "Skirmish":      "One round of a Battle, run through the numbered Battle steps; a Battle repeats Skirmishes until it ends.",
    "Casualty":      "A retinue removed from the field — from an unsaved Strike or a failed Panic or Break check.",
    "Field":         "Your retinues in play — front line (up to 10) plus reserve (up to 5). Casualties leave the field at once, lowering its count.",
    "Endurance":     "A side's stamina. Each side that fights loses 1 per Skirmish; at 0 it becomes Fatigued.",
    "Fatigued":      "A side at 0 Endurance. It cannot Parry, Riposte or Recover; each Skirmish its field takes a Break check, then it gains a Fatigue token.",
    "Break check":   "Taken by each Fatigued side's field every Skirmish, just before it gains its Fatigue token. Roll Morale (up to 5 dice, modified by Fatigue tokens); failures are casualties, but a Break check never triggers a Panic check. Unbreakable auto-passes.",
    "Panic check":   "Taken at most once per Skirmish by a side that suffered 5 or more casualties in that Skirmish, before it Strikes back. Roll Morale (up to 5 dice); Immune Panic auto-passes.",
    "Morale":        "How steady a retinue is when tested (lower is steadier; see the retinue table). Break and Panic checks roll it: a D6 per retinue in the field, up to 5 dice, each must meet its modified value; failures are casualties. If the modified value is ever 7+, the army Routs.",
    "Rout":          "The army breaks and leaves the Battle (you lose it). Whenever an army's modified Morale value reaches 7 or more, it Routs automatically.",
    "Fall Back":     "A controlled retreat that ends the Battle with at least one retinue left — a partial success.",
    "Strike":        "A landed hit. Roll a D6, apply modifiers to the roll, and Strike on a result >= the to-Strike number. The target may then Parry, Save, and Recover.",
    "to-Strike number": "The D6 result a retinue needs to Strike (see the retinue table; lower is better). Bonuses add to the roll; penalties and Fatigue tokens subtract.",
    "Save":          "The defender's roll to avoid a casualty: roll a D6, add the weapon's AP (a negative) and the shield's Save bonus (a positive); the hit is saved on a result >= the armor value.",
    "Natural roll":  "The number on the die before any modifiers. Modifiers never change what counts as 'natural'.",
    "Initiative":    "Decides who Strikes first each Skirmish (higher first). Runs -2 to +2 (Ministry can raise the maximum to +3). At -2 or lower you Blunder.",
    "Tactic":        "A choice both players make secretly and reveal together each Skirmish; it can shift Initiative and Strike rolls.",
    "Dual-equip":    "Carry two weapons at once (e.g. melee + ranged). Granted by the Tiltyard, which also gives Unwieldy until its mastery removes it.",
    "Edict":         "A scoring achievement: reach a Sovereign Standing, or complete a Monument.",
    "Monument":      "A Domain's capstone Pursuit. Completing one scores its Edict and grants a powerful effect.",

    # ── Empire keywords (referenced by Pursuits/Factions; DRAFTED — review wording) ──
    "Faith X":       "Gain X Faith: each Faith raises your Public Order track by 1 when resolved.",
    "Doubt X":       "Gain X Doubt: each Doubt lowers your Public Order track by 1 when resolved.",
    "Extort X":      "Take X from the stated source: the gold goes to you instead of its owner.",
    "Recoup":        "Regain the stated cost in gold after paying it.",
    "Speed":         "An Army's movement allowance in Territories per Move action.",

    # ── Council, Influence & Envoys (from Rules; the political loop) ──
    "Influence":     "The political currency of voting. Spend it to Support or Oppose Envoys. You gain it each turn from your Era, innate modifiers (trade partners, alliances, war), Pursuits, and Infrastructure.",
    "Influence X":   "An automatic +X (or -X) to an Envoy's net Influence from a Pursuit, Infrastructure, or Faction.",
    "Envoy":         "The currency of actions: send an Envoy to perform an action during the Envoy Phase. Council Envoys act on the voted Domain; Personal Envoys are sent by Era progression.",
    "Vote":          "On each Envoy, every player in clockwise order from the starting player must Support, Oppose, or Abstain.",
    "Support X":     "Spend X Influence to increase an Envoy's net Influence.",
    "Oppose X":      "Spend X Influence to decrease an Envoy's net Influence.",
    "Abstain":       "Decline to spend Influence on a vote.",
    "Net Influence": "The sum of an Envoy's starting Influence (1+ by Standing) and all Support, Oppose, and Influence X. The total sets the outcome: -3 or less Condemned, 0 or less Failed (gain Doubt 1), 1+ passes.",
    "Endorsed":      "An Envoy that passes with high net Influence, triggering its endorsed effect (and a Domain's Rising/Established/Sovereign endorsement).",
    "Condemned":     "An Envoy whose net Influence is -3 or less: it fails and you resolve that Domain's Condemn effect.",
    "Council Phase": "Before Personal Envoys, all players vote on a Domain (clockwise; Host breaks ties). Each then sends a free Council Envoy of that Domain. Council Envoys auto-Abstain and their net Influence cannot drop below 1.",
    "Council Envoy": "A free Envoy resolved in the Council Phase on the voted Domain; auto-Abstained, net Influence floored at 1.",
    "Personal Envoy": "An Envoy you send in the Envoy Phase to perform an action; count and reach scale with Era.",

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
    "Public Order":  "A track from -5 to 7, adjusted each turn by Faith minus Doubt; its band applies cumulative effects (see the Public Order table).",
    "Reach":         "How far a Settlement projects control, in Territories (by tier).",
    "Edict":         "A scoring achievement / win path: reach a Sovereign Standing, complete a Monument, or fulfill a victory condition (Wonder, wealth, Vassalize, Living Saints, Last Standing).",

    # ── World ──
    "Bandit":        "Neutral hostile force; Bandit Camps spawn in Outlaw Country and on low Public Order.",
    "Outlaw Country": "Three uncontrollable territories in your starting region where Bandit Camps spawn.",
    "Siege":         "Investing a Settlement with an Army to capture it; does not increment in Winter.",
}


RETINUES = {
    "Levy":           {"cost": 1000, "to_hit": 4, "endurance": 3, "shaking": 5, "unbreakable": False},
    "Man-at-Arms":    {"cost": 2000, "to_hit": 3, "endurance": 3, "shaking": 4, "unbreakable": False},
    "Sergeant":       {"cost": 2500, "to_hit": 2, "endurance": 3, "shaking": 4, "unbreakable": False},
    "Knight Templar": {"cost": 3000, "to_hit": 3, "endurance": 3, "shaking": 4, "unbreakable": True},
}

WEAPONS = {
    "Farm Tools":     {"ap":  0, "init":  0, "tier": "Crude",   "tags": []},
    "Cudgel":         {"ap": -1, "init": -1, "tier": "Crude",   "tags": [TWO_H, UNWIELDY]},
    "Pitchfork":      {"ap":  0, "init":  1, "tier": "Crude",   "tags": [TWO_H, UNWIELDY]},
    "Daggers":        {"ap":  0, "init":  1, "tier": "Cast",    "tags": [NIMBLE, TWO_H, SHATTER_ARMOR]},
    "Short Sword":    {"ap": -1, "init":  0, "tier": "Cast",    "tags": [STEADY]},
    "Spears":         {"ap": -1, "init":  1, "tier": "Cast",    "tags": [UNWIELDY]},
    "Arming Sword":   {"ap": -1, "init":  0, "tier": "Wrought", "tags": [STEADY, SHATTER_ARMOR]},
    "Pike":           {"ap": -2, "init":  1, "tier": "Wrought", "tags": [UNWIELDY, SHATTER_ARMOR, TWO_H]},
    "Flail":          {"ap": -2, "init": -1, "tier": "Wrought", "tags": [CLEAVE]},
    "Halberd":        {"ap": -3, "init":  0, "tier": "Wrought", "tags": [TWO_H]},
    "Battle Axe":     {"ap": -2, "init": -1, "tier": "Wrought", "tags": [UNSTOPPABLE, TWO_H, CLEAVE]},
    "Cavalry Spear":  {"ap": -2, "init":  0, "tier": "Wrought", "tags": [UNWIELDY, STEADY], 'note': "Needs Stable; no Tower Shield"},
    "Bastard Sword":  {"ap": -3, "init":  0, "tier": "Forged",  "tags": [STEADY, SHATTER_ARMOR]},
    "2HBastard":      {"ap": -3, "init":  0, "tier": "Forged",  "tags": [CLEAVE, TWO_H, UNWIELDY]},
    "Lance":          {"ap": -4, "init":  1, "tier": "Forged",  "tags": [STEADY, UNWIELDY, SHATTER_ARMOR, UNSTOPPABLE], 'note': "Needs Stable; no Tower Shield"},
    "Morningstar":    {"ap": -3, "init": -1, "tier": "Forged",  "tags": [UNWIELDY, DESTROY_SHIELD, CLEAVE]},
    "War Hammer":     {"ap": -8, "init": -1, "tier": "Forged",  "tags": [UNWIELDY, DESTROY_SHIELD, UNSTOPPABLE, TWO_H, SHATTER_ARMOR]},
    "Poleaxe":        {"ap": -4, "init":  0, "tier": "Crafted", "tags": [STEADY, TWO_H, UNSTOPPABLE, SHATTER_ARMOR, CLEAVE]},
}

RANGED = {
    "Hunting Bow": {"ap": -1, "init":  2, "tier": "Crude",   "tags": [TWO_H, SHATTER_ARMOR, DEFLECT]},
    "Longbow":     {"ap": -2, "init":  2, "tier": "Cast",    "tags": [SHATTER_ARMOR, TWO_H, DEFLECT]},
    "Javelin":     {"ap": -3, "init":  1, "tier": "Wrought", "tags": [SHATTER_ARMOR, STEADY, UNSTOPPABLE, ONE_SHOT, DEFLECT]},
    "Crossbow":    {"ap": -4, "init":  0, "tier": "Forged",  "tags": [SHATTER_ARMOR, UNWIELDY, UNSTOPPABLE, DEFLECT], 'note': "Tower Shield only (no other shield)"},
    "Pilum":       {"ap": -5, "init":  1, "tier": "Crafted", "tags": [STEADY, DESTROY_SHIELD, UNSTOPPABLE, ONE_SHOT, SHATTER_ARMOR, DEFLECT]},
}

SHIELDS = {
    None:            {"save_bonus": 0, "init":  0, "tier": None,      "tags": []},
    "Wooden Shield": {"save_bonus": 1, "init": -1, "tier": "Crude",   "tags": [UNWIELDY]},
    "Kite Shield":   {"save_bonus": 1, "init":  0, "tier": "Cast",    "tags": [STEADY]},
    "Scutum Shield": {"save_bonus": 1, "init": -1, "tier": "Wrought", "tags": [UNWIELDY, MINUS_1_TBH]},
    "Tower Shield":  {"save_bonus": 2, "init": -1, "tier": "Forged",  "tags": [MINUS_1_TBH, UNWIELDY]},
    "Heater Shield": {"save_bonus": 1, "init":  0, "tier": "Crafted", "tags": [MINUS_1_TBH, IMMUNE_DESTROY_SHIELD]},
}

ARMORS = {
    "Cloth":       {"save": 6, "tier": "Crude",   "tags": []},
    "Leather":     {"save": 5, "tier": "Cast",    "tags": []},
    "Chainmail":   {"save": 4, "tier": "Wrought", "tags": []},
    "Full Plate":  {"save": 3, "tier": "Forged",  "tags": []},
    "Gothic Plate":{"save": 2, "tier": "Crafted", "tags": []},
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
    ("Prowess", "Rising"):      "Immune Blocked",
    ("Prowess", "Established"): "Parry",
    ("Piety",   "Established"): "+1 Morale",
    ("Cunning", "Established"): "Foes gain Blocked",
    ("Cunning", "Sovereign"):   "Foes gain Strain",
}
	
# ── Tactics ────────────────────────────────────────────────────────────────
def _m(I=0, TH=0, TS=0, end=False, no_combat=False, endurance_loss=True):
    """Tactic modifier cell.
      I: initiative adjustment (this side's initiative gain)
      TH: to-hit adjustment (this side's to-hit improvement; lower target = better)
      TS: save-target adjustment (this side's save improvement; lower target = better)
      end: battle terminates (indecisive outcome unless one side already wiped).
      no_combat: this skirmish has no engagement (no strikes, no shake, no rout).
      endurance_loss: only meaningful when no_combat=True. If True, armies still spend
        endurance this skirmish (Flank/Flank: maneuvering tires the troops).
        If False, no_combat skirmishes are completely free (n/a in current card set).
    """
    return {"I": I, "TH": TH, "TS": TS,
            "end": end, "no_combat": no_combat, "endurance_loss": endurance_loss}

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
    ("Scout", "Fall Back"):                        (_m(end=True), _m(end=True)),
    # -- Ambush --
    ("Ambush", "Scout"):                           (_m(I=-1, TS=1), _m(I=1)),
    ("Ambush", "Ambush"):                          (_m(I=-1, TS=1), _m(I=-1, TS=1)),
    ("Ambush", "Flank"):                           (_m(I=1, TH=-1), _m(I=-1, TH=1)),
    ("Ambush", "Charge"):                          (_m(I=1, TH=1), _m(I=-1, TS=-1)),
    ("Ambush", "Fighting Formation"):              (_m(I=1, TS=1), _m(I=-1, TS=-1)),
    ("Ambush", "Defensive Formation"):             (_m(TH=-1), _m(TS=1)),
    ("Ambush", "Fall Back"):                       (_m(end=True), _m(end=True)),
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
    ("Defensive Formation", "Fall Back"):          (_m(end=True), _m(end=True)),
    # -- Fall Back --
    ("Fall Back", "Scout"):                        (_m(end=True), _m(end=True)),
    ("Fall Back", "Ambush"):                       (_m(end=True), _m(end=True)),
    ("Fall Back", "Flank"):                        (_m(I=1, TH=1), _m(I=-1)),
    ("Fall Back", "Charge"):                       (_m(I=-1), _m(I=1, TH=1)),
    ("Fall Back", "Fighting Formation"):           (_m(), _m(TH=1)),
    ("Fall Back", "Defensive Formation"):          (_m(end=True), _m(end=True)),
    ("Fall Back", "Fall Back"):                    (_m(end=True), _m(end=True)),
}
 
TACTICS = ["Scout", "Ambush", "Flank", "Charge", "Fighting Formation", "Defensive Formation", "Fall Back"]
 
 
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
        "innate": "+500, **Natural**, **Doubt 1**",
        "mastery": "",
        "builds_into": ["Workyard", "Burgages"],
        "monument": False},
    "Herb Garden": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land or Peat Bog",
        "innate": "+200, **Natural**",
        "mastery": "",
        "builds_into": ["Apothecary", "Spice Merchant"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Animal Husbandry": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land",
        "innate": "+100, **Natural**",
        "mastery": "300",
        "builds_into": ["Saddlery", "Tannery", "Stable", "Weavery", "Butchery"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Saddlery": {
        "type": "Husbandry",
        "unlock": "-",
        "mastery_req": "Arable Land + Animal Husbandry + Stable",
        "innate": "+200, **Natural**",
        "mastery": "**Upkeep -200**",
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
        "innate": "300",
        "mastery": "**Upkeep -200**; Craft+1",
        "efficient": "Smokehouse",
        "builds_into": ["Smokehouse"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": ["Animal Husbandry", "Tannery"], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Animal Husbandry", "Tannery", "Salt Works"], "upkeep_effects": [{"flat": 500}]}},
    "Bakery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Arable Land + Windmill or Watermill",
        "innate": "300; Faith 1",
        "mastery": "+100; Craft +2",
        "builds_into": [],
        "monument": False},
    "Weavery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Merchant Quarter + Animal Husbandry",
        "innate": "300",
        "mastery": "300; Craft +2",
        "builds_into": ["Artisan Workshop"],
        "monument": False},
    "Fletchery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Forestry + Carpentry",
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
        "innate": "**Unlocks Leather Armor**",
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
        "mastery": "+500; **Influence 2** to Cunning Envoys targeting this Player",
        "efficient": "Gilded Foundry",
        "builds_into": [],
        "monument": False},
    "Armory": {
        "type": "Craft",
        "unlock": "Rising Industry",
        "mastery_req": "Tannery + Blacksmith",
        "innate": "**Unlock Chainmail**; Craft +1",
        "mastery": "**Upkeep -200**",
        "efficient": "Tannery",
        "builds_into": ["Gilded Foundry"],
        "monument": False,
        "escalation": {"standing": "Rising Industry", "ranks": {1: "Chainmail"}, "requires_all": ["Joinery"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Tannery", "Blacksmith"], "domain": {"Industry": 3}, "innate_tags": ["tier:Chainmail"], "mastery_tags": [], "mastery_req": ["Tannery", "Blacksmith"], "efficient": "Tannery", "upkeep_effects": [{"flat": 200}]}},
    "Master Workshop": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Forge + Blacksmith",
        "innate": "**Upkeep -200**; Craft +1",
        "mastery": "Add **Serrated** to Weapons",
        "builds_into": ["Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: "Serrated"}, "requires_all": ["Forge"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Forge", "Blacksmith"], "domain": {"Industry": 6}, "innate_tags": [], "mastery_tags": ["Serrated"], "mastery_req": ["Forge", "Blacksmith"], "upkeep_effects": [{"flat": 200}]}},
    "Gilded Foundry": {
        "type": "Craft",
        "unlock": "Established Industry",
        "mastery_req": "Armory + Blacksmith",
        "innate": "Planishing: your to Save modifier cannot be reduced beyond 6+.",
        "mastery": "**Unlock Plate Armor**; Craft +1",
        "efficient": "Armory",
        "builds_into": ["Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Established Industry", "ranks": {1: "Full Plate + Planishing"}, "requires_all": ["Armory"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Armory", "Blacksmith"], "domain": {"Industry": 6}, "innate_tags": ["tier:FullPlate"], "mastery_tags": ["Planishing"], "mastery_req": ["Armory", "Blacksmith"]}},
    "Smokehouse": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Salt Works + Kiln + Butchery",
        "innate": "300; Craft +1",
        "mastery": "**Upkeep -200**",
        "efficient": "Salt Works",
        "builds_into": ["Supply Depot"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": ["Butchery"], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Salt Works", "Kiln", "Butchery"], "efficient": "Butchery", "upkeep_effects": [{"flat": 200}]}},
    "Workyard": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Common Land",
        "innate": "**Doubt 1**, +400",
        "mastery": "+400",
        "efficient": "Common Land",
        "builds_into": ["Census Hall", "Storehouse"],
        "monument": False},
    "Storehouse": {
        "type": "Craft",
        "unlock": "Sovereign Industry",
        "mastery_req": "College of Engineering + Workyard + Shipyard",
        "innate": "**Doubt 2**, +600",
        "mastery": "**Build Timer −2**",
        "builds_into": [],
        "monument": False},
    "Meadery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Apiary + Inn",
        "innate": "**Faith 1**, +300",
        "mastery": "+200, gain **Speed +1** in **Winter**",
        "efficient": "Apiary",
        "builds_into": [],
        "monument": False},
    "Winery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Vineyard + Joinery",
        "innate": "+400",
        "mastery": "Craft +3",
        "efficient": "Vineyard",
        "builds_into": [],
        "monument": False},
    "Cidery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Orchard + Joinery + Inn",
        "innate": "**Faith 1**, +300",
        "mastery": "300; Craft +1",
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
        "innate": "**Faith 1** for trading partners with Craft 3+",
        "mastery": "**Faith 1**",
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
        "innate": "+400",
        "mastery": "Trade Partners gain Craft +1",
        "efficient": "Market Square",
        "builds_into": ["Money Lending", "Court Artists", "Spice Merchant", "Jewelry Foundry", "Weavery"],
        "monument": False},
    "Money Lending": {
        "type": "Power",
        "unlock": "Established Industry",
        "mastery_req": "Merchant Quarter",
        "innate": "**Extort 500**",
        "mastery": "Loan money to Trade Partners at 10%/turn interest; on Default: Perform **Demand Tribute**",
        "builds_into": ["Court Artists", "Aristocratic Court"],
        "monument": False},
    "Census Hall": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Workyard + Market Square",
        "innate": "**Doubt 1**; Craft +2",
        "mastery": "600",
        "builds_into": [],
        "monument": False},
    "Caravanery": {
        "type": "Craft",
        "unlock": "-",
        "mastery_req": "Market Square or Merchant Quarter",
        "innate": "**Influence -1** to **Intercept Caravan actions** targeting your **settlements**",
        "mastery": "**Craft +2**",
        "builds_into": ["Inn", "Spice Merchant", "Courier Network", "Toll House"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {"Cunning": 6}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Market Square"]}},
    "Stable": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Animal Husbandry + Blacksmith or Carpentry",
        "innate": "Armies **Speed +1**",
        "mastery": "Armies **Speed +1**, ; Unlocks Cavalry Weapons",
        "efficient": "Animal Husbandry",
        "builds_into": ["Saddlery", "Advanced Blast Furnace"],
        "monument": False,
        "escalation": {"standing": "Untested Industry", "ranks": {1: "Cavalry weapons"}, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": ["Animal Husbandry", "Conditioning Field"], "efficient": "Animal Husbandry"}},
    "Shipyard": {
        "type": "Craft",
        "unlock": "Established Industry, Water Settlement",
        "mastery_req": "Carpentry + Harbor",
        "innate": "+1 Trade Specialization",
        "mastery": "Craft +2; Water Territory treated as Grassland for movement",
        "efficient": "Harbor",
        "builds_into": ["Storehouse"],
        "monument": False},
    "Coliseum": {
        "type": "Civic",
        "unlock": "Rising Prowess",
        "mastery_req": "Conditioning Field",
        "innate": "**Faith 1** while At War",
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
        "mastery": "**Doubt 1** to anyone who performs a Cunning action targeting you",
        "efficient": "Episcopal Court",
        "builds_into": ["Execution Dock"],
        "monument": False},
    "Abbey": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Episcopal Court + Academy",
        "innate": "Once/turn: **Influence 1** another Player's Piety Envoy",
        "mastery": "Shaken Tests are improved by 2, to a maximum of 2+.",
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
        "mastery": "**Influence 1** to Piety actions",
        "efficient": "Courtyard",
        "builds_into": ["Embassy"],
        "monument": False},
    "Execution Dock": {
        "type": "Civic",
        "unlock": "Established Piety",
        "mastery_req": "Interrogation Chambers",
        "innate": "**Influence -1** to **Foster Rebellion actions** targeting your **settlements**",
        "mastery": "**Players** who **target** you or your **settlements** with **actions** that cause **doubt** gain **Doubt 1**",
        "builds_into": ["Inquisitorial Palace", "Imperial Palace"],
        "monument": False},
    "Hospitaller": {
        "type": "Civic",
        "unlock": "Established Piety",
        "mastery_req": "Apothecary + Infirmary",
        "innate": "For every 4 casualties in a Skirmish, **Heal 1** at start of next Skirmish",
        "mastery": "**Recover** improved by +1",
        "efficient": "Infirmary",
        "builds_into": ["Preceptory of the Knight's Templar"],
        "monument": False,
        "escalation": {"standing": "Established Piety", "ranks": {1: "Recover +1 / +1"}, "requires_all": ["Infirmary"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Apothecary", "Infirmary"], "domain": {"Piety": 6}, "innate_tags": ["Recover 5"], "mastery_tags": ["Recover 4"], "mastery_req": ["Apothecary", "Infirmary"]}},
    "Jester's Court": {
        "type": "Civic",
        "unlock": "1 Rising",
        "mastery_req": "Courtyard",
        "innate": "",
        "mastery": "First **Oppose** on your Envoy: reduce by 1",
        "efficient": "Courtyard",
        "builds_into": ["Embassy"],
        "monument": False},
    "Embassy": {
        "type": "Civic",
        "unlock": "1 Established",
        "mastery_req": "Bell Tower + Jester's Court",
        "innate": "**Influence 1** to Diplomacy Envoys",
        "mastery": "",
        "efficient": "Jester's Court",
        "builds_into": ["Senate Hall"],
        "monument": False},
    "Granary": {
        "type": "Civic",
        "unlock": "Rising Industry",
        "mastery_req": "Arable Land",
        "innate": "+200",
        "mastery": "Armies and Garrisons gain **Endurance** while Besieged",
        "efficient": "Arable Land",
        "builds_into": ["Supply Depot", "Citadel"],
        "monument": False},
    "Academy": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Library + Alchemy",
        "innate": "**Influence 1** to Council Envoys",
        "mastery": "**Influence 1** to non-Council Envoys",
        "builds_into": ["University", "Abbey", "War College", "Forgery Workshop", "Toxicarium", "College of Engineering"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Courtyard": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Masonry",
        "innate": "+200",
        "mastery": "**Faith 1**",
        "builds_into": ["Conditioning Field", "Jester's Court"],
        "monument": False},
    "Episcopal Court": {
        "type": "Civic",
        "unlock": "Rising Piety",
        "mastery_req": "Masonry",
        "innate": "**Faith 1**",
        "mastery": "+200",
        "builds_into": ["Interrogation Chambers", "Abbey", "Bell Tower"],
        "monument": False},
    "Conditioning Field": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Courtyard",
        "innate": "**Faith 1** while not at War",
        "mastery": "Armies gain **+1 Maximum Endurance**",
        "efficient": "Courtyard",
        "builds_into": ["Coliseum", "Grand Tournament"],
        "monument": False,
        "escalation": {"standing": "Untested Prowess", "ranks": {1: "+1 Endurance"}, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Courtyard"], "domain": {}, "innate_tags": [], "mastery_tags": ["Cond Field"], "mastery_req": []}},
    "Grand Tournament": {
        "type": "Civic",
        "unlock": "Established Prowess",
        "mastery_req": "Coliseum + Conditioning Field",
        "innate": "**Faith 1**, ; Improve **Parry** by 1",
        "mastery": "3x/turn: exchange 500 gold for **1 Influence**; Armies gain **Riposte**",
        "efficient": "Coliseum",
        "builds_into": ["Royal Pavilion"],
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Improved Parry + Riposte"}, "requires_all": ["Coliseum"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {"Prowess": 6}, "innate_tags": ["Improved Parry"], "mastery_tags": ["Riposte"], "mastery_req": ["Conditioning Field", "Coliseum"], "efficient": "Coliseum"}},
    "Apothecary": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Herb Garden + Alchemy",
        "innate": "+300",
        "mastery": "Gain Recover 6, or improve Recover by +1.",
        "efficient": "Alchemy",
        "builds_into": ["Infirmary", "Hospitaller"],
        "monument": False,
        "escalation": {"standing": "Untested Piety", "ranks": {1: "Heal 4"}, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": ["Apothecary Heal"], "mastery_req": ["Herb Garden"]}},
    "Infirmary": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Alchemy + Herb Garden",
        "innate": "",
        "mastery": "Armies gain **Recover** or improve by +1",
        "efficient": "Apothecary",
        "builds_into": ["Hospitaller"],
        "monument": False,
        "escalation": {"standing": "Untested Piety", "ranks": {1: "Recover 6"}, "requires_all": ["Apothecary"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Apothecary"], "domain": {}, "innate_tags": [], "mastery_tags": ["Recover 6"], "mastery_req": ["Alchemy", "Herb Garden"], "efficient": "Apothecary", "upkeep_effects": [{"flat": 100}]}},
    "Supply Depot": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Granary or Smokehouse",
        "innate": "May **Muster** an Army in a Settlement under Siege",
        "mastery": "**+2 Trade Specialization**",
        "efficient": "Granary",
        "builds_into": [],
        "monument": False},
    "Artisan Workshop": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Carpentry + Arable Land + Weavery",
        "innate": "+400, **Faith 1**",
        "mastery": "+200",
        "builds_into": [],
        "monument": False},
    "University": {
        "type": "Power",
        "unlock": "-",
        "mastery_req": "Academy",
        "innate": "May spend one additional **Influence** per Support or Oppose",
        "mastery": "+1 **Influence** per Domain you are Rising",
        "efficient": "Academy",
        "builds_into": ["Studium Generale", "Ministry of Military Strategy", "College of Engineering"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Trade Guild": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Masonry or Carpentry",
        "innate": "No Upkeep on **Primitive Infrastructure**",
        "mastery": "No Upkeep on **Developed Infrastructure**",
        "builds_into": ["College of Engineering"],
        "monument": False},
    "Court Artists": {
        "type": "Civic",
        "unlock": "-",
        "mastery_req": "Merchant Quarter + Money Lending",
        "innate": "**Extort 500**; **Faith 1**",
        "mastery": "**Extort 500**; Target of Extort gains **Faith 1**",
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
        "unlock": "-",
        "mastery_req": "Caravanery + Courier Network",
        "innate": "Once/turn when a non-allied Army ends a Move action within Province: Perform a Diplomacy action",
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
        "innate": "",
        "mastery": "Passed Cunning actions **Recoup 500 Gold**",
        "efficient": "Inn",
        "builds_into": ["Smuggler's Nook", "Forgery Workshop", "Forgotten Catacombs", "Thieves' Guild"],
        "monument": False},
    "Smuggler's Nook": {
        "type": "Secrecy",
        "unlock": "Established Cunning",
        "mastery_req": "Secret Cellar + Inn",
        "innate": "-500",
        "mastery": "Bandit Camps in your Outlaw Country don't target you and target other players instead randomly; no Doubt 1 per Bandit Camp in Outlaw Country",
        "efficient": "Secret Cellar",
        "builds_into": ["Thieves' Guild"],
        "monument": False},
    "Black Market": {
        "type": "Secrecy",
        "unlock": "Established Cunning",
        "mastery_req": "Market Square + Smuggler's Nook",
        "innate": "When another Player **Extorts** gold from any source: **Extort 200** from that Player at the end of that resolution.",
        "mastery": "When another Player **Recoups** gold from any source: **Extort 200** from that Player at the end of that resolution. .",
        "efficient": "Market Square",
        "builds_into": [],
        "monument": False},
    "Forgery Workshop": {
        "type": "Power",
        "unlock": "Established Cunning",
        "mastery_req": "Academy + Secret Cellar",
        "innate": "-100",
        "mastery": "Once/turn: attempt another Cunning Envoy targeting a different Player if your Cunning Envoy Failed",
        "efficient": "Academy",
        "builds_into": ["Aristocratic Court"],
        "monument": False},
    "Toxicarium": {
        "type": "Secrecy",
        "unlock": "Rising Cunning",
        "mastery_req": "Academy + Alchemy",
        "innate": "Weapons have **Poison**",
        "mastery": "All Endorsed Cunning actions give an additional **Doubt 1** to Target and **Extort 1000**",
        "efficient": "Alchemy",
        "builds_into": [],
        "monument": False,
        "escalation": {"standing": "Rising Cunning", "ranks": {1: "Poison"}, "requires_all": [], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Academy", "Alchemy"], "domain": {"Cunning": 3}, "innate_tags": ["Poison"], "mastery_tags": [], "mastery_req": ["Academy", "Alchemy"], "upkeep_effects": [{"flat": 100}]}},
    "Pilgrimage Site": {
        "type": "Energy",
        "unlock": "Rising Piety",
        "mastery_req": "Reliquary + Chandlery",
        "innate": "**Extort 200** every Player without a Pilgrimage Site",
        "mastery": "**Doubt 1** to all other Players without a Pilgrimage Site",
        "efficient": "Reliquary",
        "builds_into": ["Preceptory of the Knight's Templar"],
        "monument": False,
        "engine": {"cost": 1, "prereqs": [], "domain": {"Piety": 3}, "innate_tags": [], "mastery_tags": [], "mastery_req": []}},
    "Beacon Towers": {
        "type": "Energy",
        "unlock": "Rising Prowess",
        "mastery_req": "Courier Network + Toll House",
        "innate": "",
        "mastery": "If non-allied Army ends a Move action within any Controlled or Contested Territory, you may Perform a Move action",
        "efficient": "Toll House",
        "builds_into": [],
        "monument": False},
    "Forgotten Catacombs": {
        "type": "Secrecy",
        "unlock": "Rising Cunning",
        "mastery_req": "Secret Cellar",
        "innate": "",
        "mastery": "Cunning actions against you cannot be **Endorsed**",
        "efficient": "Secret Cellar",
        "builds_into": [],
        "monument": False},
    "Charcoal Burner": {
        "type": "Energy",
        "unlock": "Rising Industry",
        "mastery_req": "Forestry + Kiln",
        "innate": "300",
        "mastery": "",
        "efficient": ["Forestry", "Kiln"],
        "builds_into": [],
        "monument": False},
    "Windmill": {
        "type": "Energy",
        "unlock": "Rising Industry",
        "mastery_req": "Arable Land/Weavery/Forge/Carpentry, Land Settlement",
        "innate": "300",
        "mastery": "",
        "efficient": ["Arable Land", "Weavery", "Forge", "Carpentry"],
        "builds_into": ["Bakery"],
        "monument": False},
    "Watermill": {
        "type": "Energy",
        "unlock": "Rising Industry",
        "mastery_req": "Bakery/Weavery/Forge/Carpentry, Water Settlement",
        "innate": "300",
        "mastery": "",
        "efficient": ["Bakery", "Weavery", "Forge", "Carpentry"],
        "builds_into": ["Bakery"],
        "monument": False},
    "Kiln": {
        "type": "Energy",
        "unlock": "Rising Industry",
        "mastery_req": "Forestry",
        "innate": "+200",
        "mastery": "",
        "efficient": "Forestry",
        "builds_into": ["Smokehouse", "Charcoal Burner"],
        "monument": False},
    "Burgages": {
        "type": "Energy",
        "unlock": "-",
        "mastery_req": "Common Land",
        "innate": "+400",
        "mastery": "**Faith 1**",
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
        "innate": "300",
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
        "innate": "Armies may be Equipped with a Ranged and Melee Weapon; all weapons gain **Unwieldy** when equipped with both",
        "mastery": "Armies gain **Immune Unwieldy**",
        "efficient": "Conditioning Field",
        "builds_into": ["Royal Pavilion"],
        "monument": False,
        "escalation": {"standing": "Established Prowess", "ranks": {1: "Dual-equip; Immune Unwieldy"}, "requires_all": ["Fletchery"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Fletchery", "Coliseum"], "domain": {"Prowess": 6}, "innate_tags": [], "mastery_tags": ["Immune Unwieldy"], "mastery_req": ["Fletchery", "Coliseum"], "efficient": "Conditioning Field"}},
    "Royal Pavilion": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "Grand Tournament + Tiltyard",
        "innate": "Armies gain **Immune Strained**",
        "mastery": "Armies gain **Drilled** & **Nimble**",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Prowess", "ranks": {1: "Immune Strain; Drilled; Nimble"}, "requires_all": ["Tiltyard", "Grand Tournament"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["Tiltyard"], "domain": {"Prowess": 10}, "innate_tags": ["Immune Strain"], "mastery_tags": ["Drilled", "Nimble"], "mastery_req": ["Grand Tournament", "Tiltyard"]}},
    "Imperial Palace": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "Citadel + Execution Dock",
        "innate": "Gain **Immune Border Tension & Invasion**",
        "mastery": "Non-Military Alliance players that border you gain **Doubt 2**",
        "efficient": "Citadel",
        "builds_into": [],
        "monument": True},
    "Ministry of Military Strategy": {
        "type": "Monument",
        "unlock": "Sovereign Prowess",
        "mastery_req": "University + War College",
        "innate": "Always gains **Seize the Initiative**, and your opponent doesn't. Immune -1 to Strike from Tactics.",
        "mastery": "Gain +1I; your maximum initiative increases to 3. Riposte, Destroy Shield, Deadly, & Cleave also trigger on a natural 5.",
        "efficient": "War College",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Prowess", "ranks": {1: "Always Seize the Initiative; ignore -1 to Strike from Tactics", 2: "Effects that trigger on a natural 6 also trigger on a natural 5, so long as the natural 5 would be a successful roll. Gain +1 Initiative; your maximum Initiative is now +3"}, "requires_all": ["War College"], "requires_any": [], "extra_req": ""},
        "engine": {"cost": 1, "prereqs": ["University", "War College"], "domain": {"Prowess": 10}, "innate_tags": ["Seize: first", "Immune Tactic TH"], "mastery_tags": ["Crit 5", "+1I", "MaxInit3"], "mastery_req": ["University", "War College"]}},
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
        "innate": "**Faith 1**, gain **+1 Influence** per other Player per Turn",
        "mastery": "Once/turn: auto-**Condemn** an At War Envoy OR auto-**Endorse** an Ally's Envoy",
        "builds_into": [],
        "monument": True},
    "Inquisitorial Palace": {
        "type": "Monument",
        "unlock": "Sovereign Piety",
        "mastery_req": "Execution Dock + Monastery",
        "innate": "**Doubt 1**; Unlocks **Grand Vizier** which uses your **Public Order** instead of your **Cunning** value.",
        "mastery": "**Piety Value** acts as **Cunning Value** for Grand Vizier",
        "efficient": "Monastery",
        "builds_into": [],
        "monument": True},
    "Preceptory of the Knight's Templar": {
        "type": "Monument",
        "unlock": "Sovereign Piety + Established Prowess",
        "mastery_req": "Monastery + Pilgrimage Site + Hospitaller + Abbey",
        "innate": "Armies gain **Immune Panic**",
        "mastery": "Unlocks **Knight's Templar** for Muster",
        "efficient": "Monastery",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Piety", "ranks": {1: "Immune Panic", 2: "Knight Templar unlock"}, "requires_all": ["Hospitaller"], "requires_any": [], "extra_req": "Established Prowess"},
        "engine": {"alias": "Preceptory", "cost": 1, "prereqs": [], "domain": {"Piety": 10, "Prowess": 6}, "innate_tags": ["Immune Panic"], "mastery_tags": [], "mastery_req": ["Monastery", "Pilgrimage Site", "Hospitaller", "Abbey"]}},
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
        "innate": "**Doubt 1**",
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
        "innate": "**Upkeep -500**; Your weapons gain -1 AP, incoming attack's AP is reduced by 1.",
        "mastery": "**Crafted** Tier Unlocked",
        "efficient": "Forge",
        "builds_into": [],
        "monument": True,
        "escalation": {"standing": "Sovereign Industry", "ranks": {1: "Crafted tier"}, "requires_all": ["Master Workshop", "Gilded Foundry"], "requires_any": [], "extra_req": ""},
        "engine": {"alias": "ABF", "cost": 1, "prereqs": ["Gilded Foundry", "Master Workshop", "Blacksmith", "Stable"], "domain": {"Industry": 10}, "innate_tags": ["ABF"], "mastery_tags": ["tier:Crafted"], "mastery_req": ["Gilded Foundry", "Master Workshop", "Blacksmith", "Stable"], "efficient": "Forge", "upkeep_effects": [{"flat": 500}]}},
    "Cipher Chamber": {
        "type": "Power",
        "unlock": "Sovereign Cunning",
        "mastery_req": "University + Courier Network",
        "innate": "Once/turn when a Player Sends an Envoy: that Player must declare the specific Action they would Perform if the Envoy Passes (including sub-Actions). If it Passes, they must Perform that declared Action. .",
        "mastery": "Once/turn: select any active **Timer** you did not select last turn; increase it by 1.",
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
        "escalation": {"standing": "Sovereign Cunning", "ranks": {1: "See enemy Tactic before choosing; mastery forces reveal"}, "requires_all": ["Toxicarium"], "requires_any": [], "extra_req": ""},
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
FACTIONS = {'The Battering Ram': {'inspiration': 'Siege-focused',
                       'feel': 'Offensive, Arrogant',
                       'difficulty': 'Low',
                       'strength': 'Medium',
                       'mechanic': 'Siege Specialist: You begin the game with a Siege Works (no ward, no '
                                   'upkeep, always active Mastery). If a Player builds a Citadel, you must '
                                   'Siege it as a Personal Win Condition.',
                       'pair': 'Siege Camp, Royal Pavilion',
                       'complement': 'Senate Hall'},
 'The Boundless Steppe': {'inspiration': 'Mongol Horde',
                          'feel': 'Fast',
                          'difficulty': 'Low',
                          'strength': 'Medium',
                          'mechanic': 'Horsemasters: Begin the game with a Stable which does not occupy a '
                                      'Settlement ward, cost Upkeep, and counts as an activated Mastery '
                                      'Effect which cannot be deactivated.',
                          'pair': 'Saddlery, Royal Pavilion',
                          'complement': 'Forge'},
 'The Bandit King': {'inspiration': 'Brigands',
                     'feel': 'Scrappy',
                     'difficulty': 'Low',
                     'strength': 'Low',
                     'mechanic': "Friends in Low Places: You begin the game with a Smuggler's Nook which "
                                 'does not occupy a Settlement ward, nor cost upkeep. You always gain its '
                                 'Mastery Effect, which cannot be deactivated. In addition, you may control '
                                 'one Bandit Camp outside your territory each turn. Every turn a Bandit Camp '
                                 'is generated, you may place it in your Outlaw Country instead.',
                     'pair': "Thieves' Guild, Saddlery",
                     'complement': 'Royal Pavilion'},
 'The Crowned Star': {'inspiration': 'Reigning Sovereign',
                      'feel': 'Sovereign Voice',
                      'difficulty': 'Low',
                      'strength': 'Medium',
                      'mechanic': "The Monarch: Each Turn, you choose each Council Envoy's Domain. All "
                                  'Envoys you send gain Influence -1.',
                      'pair': 'Senate Hall, Aristocratic Court',
                      'complement': 'Royal Pavilion'},
 'The Crimson Tide': {'inspiration': 'Pirate',
                      'feel': 'Pirate Life',
                      'difficulty': 'Low',
                      'strength': 'Medium',
                      'mechanic': 'Sea Lanes: Other Players cannot Perform Intercept Caravan on you. You '
                                  'begin the game with a Shipyard that does not occupy a Settlement ward, '
                                  'does not cost upkeep, and always has the Mastery Effect, even if you do '
                                  'not have a Water Settlement.',
                      'pair': "Shipyard, Thieves' Guild",
                      'complement': 'Royal Pavilion'},
 'The Entwined Crown': {'inspiration': 'Habsburg Dynasty',
                        'feel': 'Diplomatic, Inescapable',
                        'difficulty': 'Low',
                        'strength': 'Medium',
                        'mechanic': 'Royal Marriage: Once per game, you may Join an Alliance without '
                                    'unanimous consent, or Form an Alliance with a Player who is not in one. '
                                    'Whoever is in that Alliance gains Faith 1 and +1 Influence per turn.',
                        'pair': 'Aristocratic Court, Senate Hall',
                        'complement': 'Royal Pavilion'},
 'The Eternal Court': {'inspiration': 'Byzantine Empire',
                       'feel': 'Patient & Reserved',
                       'difficulty': 'Low',
                       'strength': 'Medium',
                       'mechanic': 'Patient Court: Your influence is never wasted — unspent influence is not '
                                   'discarded in the Rest Phase. Once the Era is Zenith, you have a cap of 5 '
                                   'on influence you spend per envoy, regardless of your Domain Standing.',
                       'pair': 'Senate Hall, Aristocratic Court',
                       'complement': 'Royal Pavilion'},
 'The Final Word': {'inspiration': 'Warlord Council',
                    'feel': 'Cold Steel',
                    'difficulty': 'Low',
                    'strength': 'Medium',
                    'mechanic': 'The Decider: Ignore the Innate Doubt & Influence Modifiers that are '
                                'triggered for being at War.',
                    'pair': 'Royal Pavilion, Imperial Palace',
                    'complement': 'Senate Hall'},
 'The Gilded Crescent': {'inspiration': 'Moorish Caliphate',
                         'feel': 'Egalitarian',
                         'difficulty': 'Low',
                         'strength': 'Medium',
                         'mechanic': 'Prosperity For All: Begin the game with an Inn which does not occupy a '
                                     'Settlement ward, cost Upkeep, and counts as an activated Mastery '
                                     'Effect which cannot be deactivated. You always gain trade income on '
                                     'the turn trade is initiated or ended, regardless of who started and '
                                     'who broke the trade agreement.',
                         'pair': 'Meadery & Winery, Studium Generale',
                         'complement': 'Royal Pavilion'},
 'The Gilded Path': {'inspiration': 'Great Income',
                     'feel': 'Rich Trader',
                     'difficulty': 'Low',
                     'strength': 'Low',
                     'mechanic': 'Silk Road: You begin the game with an Artisan Workshop (no ward, no '
                                 'upkeep, always active Mastery). However, you cannot refuse a Trade '
                                 'Agreement.',
                     'pair': 'Meadery & Winery, Forge',
                     'complement': 'Royal Pavilion'},
 'The Hermit Crown': {'inspiration': 'Independent',
                      'feel': 'Independent',
                      'difficulty': 'Low',
                      'strength': 'Low',
                      'mechanic': "Independent, but Ambitious: You Abstain every Vote on other Players' "
                                  'Envoys, and other Players must use 2 Influence to affect your Envoys by '
                                  '1. Gain Influence 1 to all Personal Envoys.',
                      'pair': 'Studium Generale, Saddlery',
                      'complement': 'Royal Pavilion'},
 'The Illuminated Order': {'inspiration': 'Scholarly',
                           'feel': 'Knowledge is Power',
                           'difficulty': 'Low',
                           'strength': 'Medium',
                           'mechanic': 'Knowledge is Power: For every 2 Pursuits, gain +1 Influence each '
                                       'turn.',
                           'pair': 'Studium Generale, Senate Hall',
                           'complement': 'Royal Pavilion'},
 'The Iron Faith': {'inspiration': 'Crusader States',
                    'feel': 'Piously Resolute',
                    'difficulty': 'Low',
                    'strength': 'Medium',
                    'mechanic': 'Fortress of Faith: While Public Order is greater than or equal to 3, Lay '
                                'Siege actions targeting Settlements you Control have Siege Timer +2.',
                    'pair': "Siege Camp, Preceptory of the Knight's Templar",
                    'complement': 'Senate Hall'},
 'The Iron Shore': {'inspiration': 'Norse',
                    'feel': 'Scavenger',
                    'difficulty': 'Low',
                    'strength': 'Medium',
                    'mechanic': 'Scavengers: Whether you Win or Lose a Battle, collect the Spoils of War. '
                                'You may also Recoup the Cost of the Retinues received as Casualties in that '
                                'Battle. Lastly, whenever you perform the Repair action, recoup its cost, '
                                'even if it only passed.',
                    'pair': 'Royal Pavilion, Shipyard',
                    'complement': 'Forge'},
 'The Iron Throne': {'inspiration': 'Defensive',
                     'feel': 'Defensive, Impenetrable',
                     'difficulty': 'Low',
                     'strength': 'Medium',
                     'mechanic': 'Unimpeachable: Begin the game with a Citadel (no ward, no upkeep, always '
                                 'active Mastery). You (or your alliance) cannot perform Declare War or '
                                 'Crusade.',
                     'pair': 'Inquisitorial Palace, Senate Hall',
                     'complement': 'Royal Pavilion'},
 'The Merchant Republics': {'inspiration': 'Italian City States',
                            'feel': 'Trade Dependent',
                            'difficulty': 'Low',
                            'strength': 'High',
                            'mechanic': 'Heart of Trade: Begin the game with Stone Roads infrastructure, do '
                                        'not pay Upkeep, and cannot be Razed. In order for any Player to be '
                                        'able to trade, they must trade with this Player first, unless at '
                                        'War with this Player. As soon as another Player is eligible, you '
                                        'must attempt to Sign a Trade Agreement once with that Player. You '
                                        'may not perform the End Treaty Diplomacy action.',
                            'pair': 'Shipyard, Meadery & Winery',
                            'complement': 'Royal Pavilion'},
 'The Sacred Throne': {'inspiration': 'Papal State',
                       'feel': 'Pure and Defensive',
                       'difficulty': 'Low',
                       'strength': 'High',
                       'mechanic': 'Sacrosanct: Players who declare war on you (and their allies) gain an '
                                   'additional Doubt 1.',
                       'pair': "Inquisitorial Palace, Preceptory of the Knight's Templar",
                       'complement': 'Royal Pavilion'},
 'The Tunnellers': {'inspiration': 'Dwarves',
                    'feel': 'Mountain Passers',
                    'difficulty': 'Low',
                    'strength': 'Low',
                    'mechanic': 'Tunnellers: You treat Mountain Territory like Grasslands for purposes of '
                                'movement, and begin the game with a Mine Raw Pursuit (no ward, no upkeep, '
                                'always active Mastery).',
                    'pair': 'Forge, Advanced Blast Furnace',
                    'complement': 'Royal Pavilion'},
 'The Undying Flame': {'inspiration': 'Martyrs',
                       'feel': 'Unconvinced',
                       'difficulty': 'Low',
                       'strength': 'Low',
                       'mechanic': 'Martyrdom: Your Armies gain Immune Panic, but your armies continue to '
                                   'suffer −1 To Hit from Fatigue Tokens. Gain Faith 1 for every Player '
                                   "you're at War with and every Battle where you lose 20 or more Retinues, "
                                   'win or loss.',
                       'pair': "Preceptory of the Knight's Templar, Inquisitorial Palace",
                       'complement': 'Royal Pavilion'},
 'The Verdant Kingdom': {'inspiration': 'Industry',
                         'feel': 'Pure Economy',
                         'difficulty': 'Low',
                         'strength': 'High',
                         'mechanic': 'Peaceful & Inventive: You cannot declare war, enter Military '
                                     'Alliances, perform Cunning actions, or build Pursuits that require '
                                     'Prowess or Cunning Standing. In the Income step, gain 100 gold for '
                                     'each Craft Mastery Effect you have active.',
                         'pair': 'Forge, Advanced Blast Furnace, Meadery & Winery',
                         'complement': 'Senate Hall'},
 'The Winter Wolves': {'inspiration': 'Vikings',
                       'feel': 'Aggressive, Parasitic',
                       'difficulty': 'Low',
                       'strength': 'Medium',
                       'mechanic': "Danegeld: Your Armies do not pay Upkeep in enemy territory when you're "
                                   'at war — the enemy Player pays the Upkeep instead. Do not gain Speed −1 '
                                   'in Winter.',
                       'pair': 'Royal Pavilion, Shipyard',
                       'complement': 'Forge'},
 'The Ancient Wilds': {'inspiration': 'Celtic Kingdoms',
                       'feel': 'Oathkeepers',
                       'difficulty': 'Medium',
                       'strength': 'High',
                       'mechanic': 'Highlander Way: Enemy armies gain Speed −1 in your Controlled Territory. '
                                   'You ignore all Terrain Speed modifiers and may trade without Dirt Roads. '
                                   'You must accept the first Non-Aggression Pact offered by each Player or '
                                   'Alliance. If that Player later joins an alliance, this condition is '
                                   'considered satisfied for that Alliance.',
                       'pair': 'Royal Pavilion, Saddlery',
                       'complement': 'Senate Hall'},
 'The Bloodied Cross': {'inspiration': 'Crusading Sect',
                        'feel': 'Holy War Without End',
                        'difficulty': 'Medium',
                        'strength': 'High',
                        'mechanic': 'Prophets of War: May Crusade at Rising Piety instead of Sovereign '
                                    'Piety, and do not have a cap on how many Crusades you may have active. '
                                    'All Players receive Doubt 1 per Crusade you are on. You cannot Convert.',
                        'pair': "Preceptory of the Knight's Templar, Inquisitorial Palace",
                        'complement': 'Senate Hall'},
 'The Blazing Standard': {'inspiration': 'Teutonic Knight',
                          'feel': 'Crusader Feel',
                          'difficulty': 'Medium',
                          'strength': 'High',
                          'mechanic': "Burning Cross: You begin the game with a Preceptory of the Knight's "
                                      'Templar (no ward, no upkeep, always active Mastery). If you Declared '
                                      'War via Crusade, that Player must take a Shaken Test at the beginning '
                                      'of every Battle. If during the Prowess Envoy phase you do not have an '
                                      "army with 50 Knight's Templars, you must attempt to send an envoy. If "
                                      'it passes, you must muster an army until it has 50 retinues of '
                                      "Knight's Templar.",
                          'pair': "Preceptory of the Knight's Templar, Royal Pavilion",
                          'complement': 'Senate Hall'},
 'The Inner Circle': {'inspiration': 'Natural Leader',
                      'feel': 'Strength Through Diplomacy',
                      'difficulty': 'Medium',
                      'strength': 'Medium',
                      'mechanic': 'Palatine: Players who are allied with you gain Influence 1 to their '
                                  'envoys, but you may spend 1 of their Influence each turn.',
                      'pair': 'Senate Hall, Aristocratic Court',
                      'complement': 'Royal Pavilion'},
 'The Luminous Court': {'inspiration': 'Renaissance',
                        'feel': 'Civic Soft Power',
                        'difficulty': 'Medium',
                        'strength': 'Medium',
                        'mechanic': 'Arts & Humanities / Hearts & Minds: Cannot Pursue Craft Pursuits. Civic '
                                    'Pursuits gain as Craft +1. All Civic Pursuits do not cost Upkeep. This '
                                    'Player must accept a Peace Treaty if offered one.',
                        'pair': 'Studium Generale, Aristocratic Court, Senate Hall',
                        'complement': 'Royal Pavilion'},
 'The Grand Compact': {'inspiration': 'Hanseatic League',
                       'feel': 'Peace Through Trade',
                       'difficulty': 'Medium',
                       'strength': 'Medium',
                       'mechanic': 'Mercantile Pact: If anyone Declares War on you, Players with Trade '
                                   'Agreements with you must Declare War back or End Trade Agreement.',
                       'pair': 'Shipyard, Senate Hall',
                       'complement': 'Royal Pavilion'},
 'The Pale Throne': {'inspiration': 'Undead',
                     'feel': 'Undead',
                     'difficulty': 'Medium',
                     'strength': 'Low',
                     'mechanic': 'Inexorable: Your armies always have Unwieldy and cannot gain Immune '
                                 'Unwieldy, Recover, Speed −1, and Immune Panic. Your Public Order cannot '
                                 'exceed 1.',
                     'pair': "Preceptory of the Knight's Templar, Forge",
                     'complement': 'Advanced Blast Furnace'},
 'The Sublime Gate': {'inspiration': 'Ottoman Empire',
                      'feel': 'Mercantile Military',
                      'difficulty': 'Medium',
                      'strength': 'Medium',
                      'mechanic': 'Integrated Arms: You may Muster Retinues and Equipment from your Trade '
                                  "Partners' Pursuits (and Mastery Effects, if active) for their Cost.",
                      'pair': 'Forge, Advanced Blast Furnace',
                      'complement': 'Royal Pavilion'},
 'The Velvet Hand': {'inspiration': 'Patrons',
                     'feel': 'Generous Sponsor',
                     'difficulty': 'Medium',
                     'strength': 'Medium',
                     'mechanic': 'Friends in High Places: At the beginning of the turn, Players gain Faith 1 '
                                 'if they Supported an Envoy you Sent and it was Passed. And, if it was '
                                 'Endorsed, they Extort 500 gold per Era.',
                     'pair': 'Aristocratic Court, Senate Hall',
                     'complement': 'Royal Pavilion'},
 'The Ashen Vale': {'inspiration': 'Plague',
                    'feel': 'Sickly',
                    'difficulty': 'High',
                    'strength': 'Low',
                    'mechanic': 'Pestilence: Each bordering Player gains Doubt 1, your settlements gain '
                                'Reach +1, and all Retinues gain Poison. You may not Pursue an Apothecary, '
                                'Infirmary, or Hospitaller.',
                    'pair': "Thieves' Guild, Inquisitorial Palace",
                    'complement': 'Royal Pavilion'},
 'The Broken Banner': {'inspiration': 'Mercenary',
                       'feel': 'Always for Sale',
                       'difficulty': 'High',
                       'strength': 'Low',
                       'mechanic': 'The Highest Bidder: You cannot Declare War and cannot be the Target of a '
                                   'Declare War action. However you must sign any Military or Defensive '
                                   'Alliance offered to you by the highest bidding Player each turn and must '
                                   'be paid each turn. In order to overturn an existing Alliance, the Player '
                                   'must pay a higher amount than the prior agreement. You cannot sign or '
                                   'end alliances via a Diplomacy action.',
                       'pair': 'Royal Pavilion, Forge',
                       'complement': 'Senate Hall'},
 'The Forked Tongue': {'inspiration': 'Deceptive',
                       'feel': 'Two-Faced',
                       'difficulty': 'High',
                       'strength': 'High',
                       'mechanic': 'Masters of Duplicity: You may hold any number of treaties simultaneously '
                                   'with any number of Players, regardless of contradiction. Your treaties '
                                   'are never automatically canceled or voided by game events. When a '
                                   'situation arises that would normally force a treaty to be canceled, you '
                                   'may choose which obligation to honor, keeping all other treaties intact. '
                                   'Other Players may still end their treaties with you via the End Treaty '
                                   'action.',
                       'pair': "Thieves' Guild, Senate Hall",
                       'complement': 'Royal Pavilion'},
 'The Hall of Masks': {'inspiration': 'Doppelganger',
                       'feel': 'Shifting Identity',
                       'difficulty': 'High',
                       'strength': 'High',
                       'mechanic': "Mimic: At the beginning of every Player's turn, pick another Player's "
                                   'Faction. You gain that Faction for this turn. Next turn, you cannot '
                                   'select that Faction.',
                       'pair': 'Studium Generale, Senate Hall',
                       'complement': 'Royal Pavilion'},
 'The Smoldering Crown': {'inspiration': 'Terrorists',
                          'feel': 'Aggressive, Destructive',
                          'difficulty': 'High',
                          'strength': 'Medium',
                          'mechanic': 'Reckless: Gain Influence 2 to all Cunning Envoys when targeting a '
                                      'Player with PO > 0. You begin the game with a Secret Cellar (no ward, '
                                      'no upkeep, always active Mastery). Cannot be in an alliance. Cannot '
                                      'Perform Diplomacy actions. If you Send a Prowess Envoy, it cannot '
                                      'Fail — if Condemned, it Passes but still gains Blocked.',
                          'pair': "Thieves' Guild, Inquisitorial Palace",
                          'complement': 'Royal Pavilion'},
 "The Squatters' Crown": {'inspiration': 'Insurgents',
                          'feel': 'Mobile Occupier',
                          'difficulty': 'High',
                          'strength': 'Medium',
                          'mechanic': 'Occupy: You start the game with an additional army. All must begin '
                                      'the game placed inside your settlements. You do not control your '
                                      'settlements when you leave them. To collect taxes or use Pursuits, '
                                      'end your turn inside that Settlement. To Occupy a Settlement, begin a '
                                      'Battle adjacent to the city like a Siege — instead, you Battle '
                                      'against the Garrison and Armies at war with you or owned by the same '
                                      'owner. If you win (or there is no force to fight), move inside. In '
                                      'the Upkeep Phase, only pay upkeep on equipment. You count as having '
                                      'all Infrastructure of Occupied Settlements and always count as 3 '
                                      'Trading Pursuits. When you leave a Settlement, you may not re-enter '
                                      'it until you Occupy another Settlement and a Trade Agreement is '
                                      'signed.',
                          'pair': 'Royal Pavilion, Saddlery',
                          'complement': 'Forge'},
 'The Wandering Crown': {'inspiration': 'Nomadic',
                         'feel': 'Nomads',
                         'difficulty': 'High',
                         'strength': 'Medium',
                         'mechanic': 'Wandering Nomads: Your armies function as settlements, classified as a '
                                     'Band, Tribe, or Horde and upgraded accordingly. You may have one '
                                     'additional army per Era, starting with two. Armies do not require '
                                     'troops to exist and cannot be besieged. Nomads cannot build '
                                     'infrastructure but may build pursuits. Raw Material pursuits within '
                                     'Reach are always considered active and do not take a settlement ward. '
                                     'Each army is considered to have a Muster Field. You may trade so long '
                                     "as your border touches another Player's border. Armies count as "
                                     'settlements with a Reach of 3. When an army is destroyed, so is its '
                                     'settlement. You may begin a new army adjacent to any existing army by '
                                     'using either the Charter Settlement or Muster Army actions. Nomads do '
                                     'not pay any upkeep.',
                         'pair': 'Saddlery, Royal Pavilion',
                         'complement': 'Forge'},
 'The Dukedom': {'inspiration': 'The Game',
                 'feel': 'King of the Castle',
                 'difficulty': 'High',
                 'strength': 'High',
                 'mechanic': 'The Great Arbiter: The Duke begins the game trading with all Players under a '
                             'Non-Aggression Pact. The Duke cannot join alliances, perform Cunning actions, '
                             "or Declare War. If a Player declares war on the Duke, that Player's Trade "
                             'Agreements, Non-Aggression Pacts, and Defensive Alliances are immediately and '
                             'permanently voided. Their Military Alliance remains intact. All other Players '
                             'simultaneously declare war on that Player and their Military Alliance. These '
                             'cannot be reinstated while at war with the Duke. The Duke sees all private '
                             'actions, resolves Player actions, and manages Bandit Mechanics. If the Duke is '
                             'eliminated, the game ends. The Duke may optionally choose a faction.',
                 'pair': 'Senate Hall, Aristocratic Court',
                 'complement': 'Royal Pavilion, Imperial Palace'},
 'The Elder Grove': {'inspiration': 'Elves',
                     'feel': 'Cautious Quickfighters',
                     'difficulty': 'Low',
                     'strength': 'Medium',
                     'mechanic': 'Wise & Suspicious: Gain Doubt 1; If Public Order is 1+, armies gain '
                                 'Nimble, Steady, and Speed +1. Cannot be a member of an alliance.',
                     'pair': 'Forge',
                     'complement': 'Inquisitorial Palace'},
 'The Yew Heart': {'inspiration': 'English Longbows',
                   'feel': 'Skilled Volleys',
                   'difficulty': 'Low',
                   'strength': 'Medium',
                   'mechanic': 'Archery is a Way of Life: You begin the game with a Fletchery which does not '
                               'occupy a Settlement ward, nor cost upkeep. You always gain its Mastery '
                               'Effect, which cannot be deactivated. In addition, your armies must always be '
                               'equipped with a ranged weapon. Ranged Weapons gain +1 to Hit. Cannot  be '
                               'equipped with plate or articulated gothic plate. Cannot use shields. Cannot '
                               "build a Preceptory of Knight's Templar.",
                   'pair': 'Royal Pavilion',
                   'complement': 'Senate Hall'}}

# ── INFRASTRUCTURE & WONDERS ───────────────────────────────────────────────
# Empire-level builds (per-settlement infrastructure + unique Wonders).
# Master source — edit HERE; reference sheets are generated from these dicts.
# Tiered upkeep/build values (e.g. '50/100/200') are strings.
INFRASTRUCTURE = {'Dirt Roads': {'upkeep': 0,
                'upkeep_frequency': 'per Settlement',
                'empire_bonus': 'Can Trade; place Dirt Road Territories; ignore Terrain Speed Modifiers',
                'tier': 'Primitive',
                'build_time': 2,
                'requirement': 'None'},
 'Hitching Post': {'upkeep': 0,
                   'upkeep_frequency': 'per Settlement',
                   'empire_bonus': 'Craft +1',
                   'tier': 'Primitive',
                   'build_time': 2,
                   'requirement': 'None'},
 'Muster Field': {'upkeep': 50,
                  'upkeep_frequency': 'per Settlement',
                  'empire_bonus': 'Can Muster',
                  'tier': 'Primitive',
                  'build_time': 2,
                  'requirement': 'None'},
 'Wooden Walls': {'upkeep': 50,
                  'upkeep_frequency': 'per Settlement',
                  'empire_bonus': '**Influence -1** to **Raze actions** targeting your **settlements**',
                  'tier': 'Primitive',
                  'build_time': 2,
                  'requirement': 'None'},
 'Stone Roads': {'upkeep': 50,
                 'upkeep_frequency': 'per Settlement',
                 'empire_bonus': 'Ignore Terrain Speed Modifiers; if you start turn on Stone Road gain Speed '
                                 '+2; replaces Dirt Roads',
                 'tier': 'Developed',
                 'build_time': 3,
                 'requirement': 'Dirt Roads'},
 'Town Hall': {'upkeep': 50,
               'upkeep_frequency': 'per Settlement',
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
 'Garrison': {'upkeep': '50/100/200',
              'upkeep_frequency': 'per Settlement',
              'empire_bonus': 'Local Armies form (10/20/30 by Settlement size). All Garrisons share '
                              'Equipment. Cannot be targeted; may Sally Forth.',
              'tier': 'Developed',
              'build_time': 3,
              'requirement': 'Muster Field'},
 'Stone Walls': {'upkeep': 50,
                 'upkeep_frequency': 'per Settlement',
                 'empire_bonus': '**Influence -1** to **Destabilize actions** targeting your **settlements**',
                 'tier': 'Sophisticated',
                 'build_time': 4,
                 'requirement': 'One Tier Developed + Wooden Walls'},
 'Keep': {'upkeep': 50,
          'upkeep_frequency': '—',
          'empire_bonus': 'May Muster from Garrison in addition to normal Muster Limits. If so set Garrison '
                          'to 0 and Muster Timer 1. Garrison returns to full when resolved.',
          'tier': 'Sophisticated',
          'build_time': 4,
          'requirement': 'Garrison'},
 'Cathedral': {'upkeep': 50,
               'upkeep_frequency': 'per Settlement',
               'empire_bonus': 'Faith 1',
               'tier': 'Sophisticated',
               'build_time': 4,
               'requirement': 'Requires 1+ City'},
 'Library': {'upkeep': 50,
             'upkeep_frequency': 'per Settlement',
             'empire_bonus': 'Influence 1 to Council Envoys',
             'tier': 'Sophisticated',
             'build_time': 4,
             'requirement': 'Town Hall'}}

WONDERS = {'Colossus': {'upkeep': 200,
              'upkeep_frequency': 'per Wonder',
              'empire_bonus': 'You may **support** your own **prowess envoys** before other **players '
                              'vote**. **Armies** move **Speed +2** **Siege Timer -2** gain **Immune '
                              'Blocked**.',
              'tier': 'Wonder',
              'build_time': 10,
              'requirement': 'All Infrastructure unlocked'},
 'The Grand Exchange': {'upkeep': 200,
                        'upkeep_frequency': 'per Wonder',
                        'empire_bonus': 'Whenever you generate **Trade Income** you generate **twice as '
                                        'much** for yourself.',
                        'tier': 'Wonder',
                        'build_time': 10,
                        'requirement': 'All Infrastructure unlocked'},
 'The Great Basilica': {'upkeep': 200,
                        'upkeep_frequency': 'per Wonder',
                        'empire_bonus': 'If your **Public Order** would ever be less than 5 set it to 5 '
                                        'instead. Your **Settlements** gain **Reach +1**.',
                        'tier': 'Wonder',
                        'build_time': 10,
                        'requirement': 'All Infrastructure unlocked'},
 'High Chancery': {'upkeep': 200,
                   'upkeep_frequency': 'per Wonder',
                   'empire_bonus': 'Once per turn: automatically **Condemn** or **Endorse** one Envoy Sent '
                                   'by any other Player regardless of **Net Influence** after Influence has '
                                   'been spent, even if it’s a Council Envoy.',
                   'tier': 'Wonder',
                   'build_time': 10,
                   'requirement': 'All Infrastructure unlocked'}}
# ── EMPIRE RULES (ingested from Rules.docx — new data, nothing replaced) ─────
# Settlement tiers: tax is the WINTER collection (once per 4 turns); wards =
# pursuit slots (1 per tier; Hamlet exception); muster = retinues/turn.
SETTLEMENTS = {
    "Hamlet":     {"tier": 0, "sea_variant": None,        "tax_income": 0,     "muster_limit": 0,  "build_time": 1, "wards": 3, "reach": 1, "notes": "Husbandry pursuits only; exactly range 2 from capital; may always pursue Arable Land"},
    "Village":    {"tier": 1, "sea_variant": None,        "tax_income": 2000,  "muster_limit": 10, "build_time": 1, "wards": 1, "reach": 1, "notes": ""},
    "Town":       {"tier": 2, "sea_variant": "Sea Town",  "tax_income": 4000,  "muster_limit": 25, "build_time": 2, "wards": 2, "reach": 2, "notes": ""},
    "City":       {"tier": 3, "sea_variant": "Port",      "tax_income": 6000,  "muster_limit": 50, "build_time": 3, "wards": 3, "reach": 3, "notes": ""},
    "Metropolis": {"tier": 4, "sea_variant": "Metropolis","tax_income": 10000, "muster_limit": 50, "build_time": 5, "wards": 4, "reach": 4, "notes": "Capital only, requires Sovereign Industry (Titan of Industry)"},
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
     6: ("Holy",          "+2 Influence"),
     7: ("Living Saints", "Begin Pious Timer Edict"),
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
        "Border Tension":  "Per other Player Army in your Territory (not Alliance or NAP)",
        "Invasion":        "Additional per other Player Army in your Territory at War",
        "State of Alarm":  "If at War",
        "Mounting Panic":  "Per Settlement being Besieged",
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
        "Established": "Edict of War: All armies gain Parry. No longer gain Doubt while at War.",
        "Sovereign":   "High Quartermaster: Upkeep -2000. No longer lose Influence while at War. May change equipment on your armies during any upkeep phase where that army is within Province.",
    },
    "Cunning": {
        "Rising":      "Clandestine Councilor: Once per turn, when another player's Envoy is Sent, target a player - that player Abstains.",
        "Established": "Grand Vizier: Players may not target you with Cunning Envoys if your Cunning value is higher.",
        "Sovereign":   "Master Conspirator: Once per turn, if your non-Cunning Envoy passes or is Endorsed, you may instead perform a Cunning action.",
    },
    "Piety": {
        "Rising":      "Divine Mandate: Faith 1.",
        "Established": "Prophet of Retribution: All other players gain Doubt 1 while your Public Order is positive.",
        "Sovereign":   "Pillar of Faith: If your Public Order would go below 3, set it to 3. May use the Crusade action.",
    },
    # Influence scaling by standing (Untested/Rising/Established/Sovereign):
    "max_influence_per_vote":  {"Untested": 1, "Rising": 2, "Established": 3, "Sovereign": 4},
    "innate_influence_own_envoys": {"Untested": 0, "Rising": 1, "Established": 2, "Sovereign": 3},
}

# Seasons (turn cycle of 4; Rest Phase advances Season +1).
SEASONS = {
    "Winter": {"name": "Freezing",    "effect": "All Armies gain Speed -1; Sieges do not increment. Tax income collected."},
    "Spring": {"name": "Planting",    "effect": "No Host, Bandits, Trade Income, Council Phase, or Diplomacy Actions. Gain +1 Envoy."},
    "Summer": {"name": "Campaigning", "effect": "All Armies gain Speed +3; all Armies gain Strained."},
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