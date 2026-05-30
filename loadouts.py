"""
Loadout generator for the combat tournament.

Two entry points:
- `archetype_pool()`: curated pool of representative builds players would actually
  field, covering faction archetypes, spec-pathway endgames, and spec combinations.
- `generate_loadouts(...)`: flexible iterator for custom sweeps.

Naming convention:
  Without ranged:    Sgt/Halberd/Chain [Steadfast, Regen 5]
  With shield:       Sgt/Bastard/Heater/FullPlate
  With ranged:       Sgt/Halberd+Pilum/Chain
  With Tiltyard:     Sgt/Halberd+Pilum/Chain (TY)

Tags shown in brackets are the full extra_tags list (engine sees what name shows).

Engine-recognized extra_tags:
  Combat keywords:    Steady, Nimble, Unwieldy, Drilled, Steadfast, Parry, Poison
  Defensive:          Regenerate, Regenerate 5, Regenerate 4, Regenerate Reroll
  Immunities:         Immune Unwieldy, Immune Poison
  Spec effects:       MW Weapons (-1 AP), GF Armor (incoming AP -1), Cond Field (+1 Endurance)
  Faction flag:       Yew Heart (ranged +1 to Hit)
"""

from collections import namedtuple
from renown_combat import RETINUES, WEAPONS, RANGED, SHIELDS, ARMORS

Loadout = namedtuple("Loadout",
    "name retinue weapon shield armor ranged has_tiltyard size extra_tags upkeep_per_retinue playstyle tiltyard_mastery pursuits military_pursuit_count domain_count")
Loadout.__new__.__defaults__ = (None, True, frozenset(), 0, 0)  # playstyle, tiltyard_mastery, pursuits, mpc, domain_count


def _retinues(rules):
    return rules.retinues if rules is not None else RETINUES


def _weapons(rules):
    return rules.weapons if rules is not None else WEAPONS


def _ranged(rules):
    return rules.ranged if rules is not None else RANGED


def _shields(rules):
    return rules.shields if rules is not None else SHIELDS


def _armors(rules):
    return rules.armors if rules is not None else ARMORS


def _pursuits_info(rules):
    return rules.pursuits_info if rules is not None else PURSUITS_INFO


def _tier_industry_req(rules):
    return rules.tier_industry_req if rules is not None else TIER_INDUSTRY_REQ


def _armor_requires(rules):
    return rules.armor_requires if rules is not None else ARMOR_REQUIRES


def _shield_metal_requires(rules):
    return rules.shield_metal_requires if rules is not None else SHIELD_METAL_REQUIRES


# ==============================================================================
# Tier ordering, abbreviations
# ==============================================================================

TIER_ORDER = ["Crude", "Cast", "Wrought", "Forged", "Crafted"]
TIER_IDX = {t: i for i, t in enumerate(TIER_ORDER)}

RETINUE_TIER = {
    # Minimum tier of gear each retinue uses.
    # Levy: capped at Wrought (cannot use Forged+); enforced in valid_combo.
    # MaA, Sgt, KT: all require Wrought+ minimum, can use Forged or Crafted (with ABF).
    "Levy": 0,
    "Man-at-Arms": 2,
    "Sergeant": 2,
    "Knight Templar": 2,
}

RETINUE_LABEL = {
    "Levy": "Lev",
    "Man-at-Arms": "MaA",
    "Sergeant": "Sgt",
    "Knight Templar": "KT",
}

ARMOR_LABEL = {
    "Cloth": "Cloth",
    "Leather": "Leather",
    "Chainmail": "Chain",
    "Full Plate": "FullPlate",
    "Gothic Plate": "Gothic",
}

SHIELD_LABEL = {
    "Wooden Shield": "Wooden",
    "Kite Shield": "Kite",
    "Scutum Shield": "Scutum",
    "Tower Shield": "Tower",
    "Heater Shield": "Heater",
}

WEAPON_LABEL = {
    "Farm Tools": "FarmTools",
    "Bastard Sword": "Bastard",
    "Battle Axe": "BattleAxe",
    "War Hammer": "WarHammer",
    "Short Sword": "ShortSword",
    "Arming Sword": "Arming",
    "Hunting Bow": "HuntBow",
}

TAG_DISPLAY = {
    "Regenerate":        "Regen",
    "Regenerate 5":      "Regen 5",
    "Regenerate 4":      "Regen 4",
    "Regenerate Reroll": "Reroll",
    "Immune Unwieldy":   "ImmU",
    "Immune Poison":     "ImmP",
    "Apothecary Heal":   "ApoHeal",
    "Cond Field":        "Cond+1",
    "Ministry: every":   "Min:every",
    "Ministry: first":   "Min:first",
    "Ministry: once":    "Min:once",
    "MW Weapons":        "MW",
    "GF Armor":          "GF",
    "Yew Heart":         "YewHeart",
}


def _w_label(w):
    return WEAPON_LABEL.get(w, w)


def _name(retinue, weapon, shield, armor, ranged, has_tiltyard, extra_tags, playstyle=None):
    """Build a human-readable name for a loadout."""
    parts = [RETINUE_LABEL[retinue]]
    if weapon is None and ranged:
        # Pure-ranged: no melee weapon, primary armament is ranged
        parts.append(_w_label(ranged))
    else:
        w_str = _w_label(weapon)
        if ranged:
            w_str = f"{w_str}+{_w_label(ranged)}"
        parts.append(w_str)
    if shield:
        parts.append(SHIELD_LABEL.get(shield, shield))
    parts.append(ARMOR_LABEL.get(armor, armor))
    base = "/".join(parts)
    if has_tiltyard:
        base += " (TY)"
    if extra_tags:
        base += f" [{', '.join(TAG_DISPLAY.get(t, t) for t in extra_tags)}]"
    if playstyle and playstyle != "Random":
        base += f" <{playstyle}>"
    return base


# ==============================================================================
# Validity
# ==============================================================================

def is_2h(weapon_name, rules=None):
    if weapon_name is None:
        return False
    profile = _weapons(rules).get(weapon_name) or _ranged(rules).get(weapon_name)
    return "2H" in profile["tags"]


def valid_combo(retinue, weapon, shield, armor, ranged, has_tiltyard, allow_tier_mismatch=2, rules=None):
    """Filter for sensible combinations.
    - 2H melee disallows shields.
    - 1H melee REQUIRES a shield (except Bastard Sword, which has both profiles).
      Farm Tools is exempt as the universal sidearm fallback in pure-ranged builds.
    - 1H melee: shield tier must be >= weapon tier (universal rule).
      Note: the "shield tier == weapon tier without ABF" rule is path-specific
      and enforced in archetype_pool() by restricting shield_options per path.
    - Lance disallows Tower Shield.
    - Poleaxe cannot be used by Levy (rules).
    - Equipment tier must be >= retinue tier (no downgrades).
    - Levy cannot use Forged or Crafted-tier equipment (capped at Wrought).
    - "One Shot" ranged (Javelin, Pilum) requires Tiltyard.
    - Dual-equip (real melee + ranged) REQUIRES Tiltyard.
    - Pure-ranged exception: Farm Tools + ranged represents a ranged-focused build.
    """
    weapons = _weapons(rules)
    ranged_table = _ranged(rules)
    shields = _shields(rules)
    armors = _armors(rules)
    if is_2h(weapon, rules=rules) and shield is not None:
        return False
    # Lance restrictions: cannot use Tower (too unwieldy on horse) or Wooden (too cheap).
    # Lance CAN use Kite, Scutum, or Heater Shield.
    if weapon == "Lance" and shield in ("Tower Shield", "Wooden Shield"):
        return False
    # Crossbow restriction: when Crossbow is equipped (pure-ranged or dual-equip),
    # the only allowed shield is Tower Shield (pavise-style). Other shields forbidden.
    # If the melee weapon can't pair with Tower (e.g. Lance), the loadout must run
    # shieldless — that's a deliberate trade-off (Lance+Crossbow = no shield).
    if ranged == "Crossbow" and shield is not None and shield != "Tower Shield":
        return False
    if weapon == "Poleaxe" and retinue == "Levy":
        return False

    # Plain 'Bastard Sword' must ALWAYS carry a shield (it's the 1H profile that only
    # swaps to 2HBastard if the shield is destroyed). A shieldless Bastard is invalid —
    # the always-2H form is the separate '2HBastard' weapon. This also blocks
    # Bastard+Crossbow (which would be shieldless), forcing 2HBastard+Crossbow instead.
    if weapon == "Bastard Sword" and shield is None:
        return False

    # 1H weapons (no "2H" tag) require a shield, except Farm Tools.
    # Additional exception: when Crossbow is equipped, 1H weapons may run shieldless
    # if their shield options are incompatible with the Crossbow→Tower rule
    # (e.g., Lance can use Tower? No — so Lance+Crossbow runs shieldless).
    if (weapon != "Farm Tools"
            and not is_2h(weapon, rules=rules)
            and shield is None
            and ranged != "Crossbow"):
        return False

    # 1H + shield: shield tier must be >= weapon tier
    # Exception: Lance is exempt from the tier rule (only the explicit forbidden-shield
    # list above applies). Lance can use Kite, Scutum, or Heater regardless of weapon tier.
    if shield is not None and not is_2h(weapon, rules=rules) and weapon != "Farm Tools" and weapon != "Lance":
        weapon_tier_idx = TIER_IDX.get(weapons[weapon]["tier"], 0)
        shield_tier_idx = TIER_IDX.get(shields[shield]["tier"], 0)
        if shield_tier_idx < weapon_tier_idx:
            return False

    # "One Shot" ranged weapons (Javelin, Pilum) require Tiltyard.
    if ranged is not None and "One Shot" in ranged_table[ranged].get("tags", []):
        if not has_tiltyard:
            return False

    # Dual-equip requires Tiltyard. Real melee + ranged without Tiltyard is invalid.
    has_real_melee = weapon != "Farm Tools"
    if has_real_melee and ranged is not None and not has_tiltyard:
        return False

    retinue_idx = RETINUE_TIER[retinue]
    armor_tier_idx = TIER_IDX[armors[armor]["tier"]]
    FORGED_IDX = TIER_IDX["Forged"]
    CRAFTED_IDX = TIER_IDX["Crafted"]

    # Pure-ranged loadout: weapon is Farm Tools fallback, real weapon is ranged.
    # Tier-check against the ranged weapon instead of Farm Tools.
    if weapon == "Farm Tools" and ranged is not None:
        ranged_tier_idx = TIER_IDX.get(ranged_table[ranged]["tier"], 0)
        if ranged_tier_idx < retinue_idx:
            return False
        if armor_tier_idx < retinue_idx:
            return False
        # Levy cap at Wrought (never Forged or Crafted)
        if retinue == "Levy":
            if ranged_tier_idx >= FORGED_IDX:
                return False
            if armor_tier_idx >= FORGED_IDX:
                return False
            if shield is not None:
                shield_tier_idx = TIER_IDX.get(shields[shield]["tier"], 0)
                if shield_tier_idx >= FORGED_IDX:
                    return False
        return True

    weapon_tier_idx = TIER_IDX.get(weapons[weapon]["tier"], 0)

    # Equipment tier >= retinue tier
    if weapon_tier_idx < retinue_idx:
        return False
    if armor_tier_idx < retinue_idx:
        return False

    # Levy cap at Wrought: Levy cannot use Forged or Crafted gear at all.
    if retinue == "Levy":
        if weapon_tier_idx >= FORGED_IDX:
            return False
        if armor_tier_idx >= FORGED_IDX:
            return False
        if shield is not None:
            shield_tier_idx = TIER_IDX.get(shields[shield]["tier"], 0)
            if shield_tier_idx >= FORGED_IDX:
                return False

    # Dual-equip: ranged tier check (ranged weapon must also be tier-appropriate)
    if has_real_melee and ranged is not None:
        ranged_tier_idx = TIER_IDX.get(ranged_table[ranged]["tier"], 0)
        if ranged_tier_idx < retinue_idx:
            return False
        # Levy ranged cap at Wrought
        if retinue == "Levy" and ranged_tier_idx >= FORGED_IDX:
            return False

    return True


# ==============================================================================
# Generator
# ==============================================================================

def generate_loadouts(
    retinue_options=None,
    weapon_options=None,
    shield_options=None,
    armor_options=None,
    ranged_options=None,
    tiltyard_options=(False,),
    tiltyard_mastery=True,
    sizes=(50,),
    tag_sets=((),),  # tuple of tag-tuples
    playstyles=(None,),  # tuple of playstyle names. None = Random.
    allow_tier_mismatch=2,
    rules=None,
):
    """Yield valid Loadouts across the given option lists.

    tag_sets: a tuple of tag-tuples. Each tag-tuple is the COMPLETE extra_tags
    for that loadout. Pass `((),)` for vanilla only.
    playstyles: tuple of playstyle names. Each loadout will be replicated under each style.
    """
    retinues = _retinues(rules)
    weapons = _weapons(rules)
    shields = _shields(rules)
    armors = _armors(rules)
    ranged_table = _ranged(rules)
    retinue_options  = retinue_options  or list(retinues.keys())
    weapon_options   = weapon_options   or list(weapons.keys())
    shield_options   = shield_options   or list(shields.keys())
    armor_options    = armor_options    or list(armors.keys())
    ranged_options   = ranged_options   or [None] + list(ranged_table.keys())

    out = []
    for ret in retinue_options:
        for w in weapon_options:
            for s in shield_options:
                for a in armor_options:
                    for r in ranged_options:
                        for ty in tiltyard_options:
                            if ty and r is None:
                                continue
                            if not valid_combo(ret, w, s, a, r, ty, allow_tier_mismatch, rules=rules):
                                continue
                            for size in sizes:
                                for tag_tuple in tag_sets:
                                    for ps in playstyles:
                                        upkeep = retinues[ret]["cost"]
                                        tags = list(tag_tuple)
                                        name = _name(ret, w, s, a, r, ty, tags, playstyle=ps)
                                        out.append(Loadout(
                                            name=name,
                                            retinue=ret, weapon=w, shield=s, armor=a,
                                            ranged=r, has_tiltyard=ty, size=size,
                                            extra_tags=tags,
                                            upkeep_per_retinue=upkeep,
                                            playstyle=ps,
                                            tiltyard_mastery=tiltyard_mastery,
                                        ))
    return out


# ==============================================================================
# Build kits — tag bundles representing real spec/faction combinations
# ==============================================================================
# Each kit is a tuple of extra_tags that an army would have if the listed
# specs/factions are active. Use as `tag_sets=(BUILD_KITS["Pre + RP"],)` etc.

BUILD_KITS = {
    # — Baseline —
    "Vanilla":              (),

    # — Single spec masteries / domain effects —
    "Drilled":              ("Drilled",),
    "Nimble":               ("Nimble",),
    "Steady":               ("Steady",),
    "Steadfast":            ("Steadfast",),                     # Preceptory innate / Undying Flame
    "Parry":                ("Parry",),                         # Edict of War (Sovereign Prowess)
    "Cond Field":           ("Cond Field",),                    # Conditioning Field mastery
    "MW Weapons":           ("MW Weapons",),                    # Master Workshop mastery
    "GF Armor":             ("GF Armor",),                      # Gilded Foundry mastery
    "Immune Poison":        (),                                 # Apothecary no longer grants Immune Poison (disabled)
    "Apothecary Heal":      ("Apothecary Heal",),               # Apothecary mastery: Heal 1 per 4 cas (Immune Poison removed)
    "Poison":               ("Poison",),                        # Toxicarium innate
    "Immune Unwieldy":      ("Immune Unwieldy",),               # Tiltyard mastery

    # — Regenerate ladder —
    "Regen 6+":             ("Regenerate",),
    "Regen 5+":             ("Regenerate 5",),
    "Regen 4+":             ("Regenerate 4",),
    "Regen 6+ Reroll":      ("Regenerate", "Regenerate Reroll"),
    "Regen 5+ Reroll":      ("Regenerate 5", "Regenerate Reroll"),
    "Regen 4+ Reroll":      ("Regenerate 4", "Regenerate Reroll"),

    # — Spec combinations (multi-spec pathways) —
    "Royal Pavilion":       ("Drilled", "Nimble"),                                    # RP mastery
    "Preceptory":           ("Steadfast",),                                           # Preceptory innate
    "Pre + RP":             ("Drilled", "Nimble", "Steadfast"),
    "Pre + RP + Parry":     ("Drilled", "Nimble", "Steadfast", "Parry"),
    "RP + Conditioned":     ("Drilled", "Nimble", "Cond Field"),
    "Pre + RP + Cond":      ("Drilled", "Nimble", "Steadfast", "Cond Field"),
    "MW + GF":              ("MW Weapons", "GF Armor"),
    "Industry Elite":       ("MW Weapons", "GF Armor", "Cond Field"),
    "Apo + Tox":            ("Poison",),
    "Apo + Inf":            ("Regenerate",),
    "Apo + Inf + Hosp":     ("Regenerate 5",),
    "Apo + Inf + Hosp(M)":  ("Regenerate 5", "Regenerate Reroll"),

    # — Faction effects —
    "Pale Throne":          ("Unwieldy", "Regenerate", "Steadfast"),                  # mandatory faction tags
    "Pale Throne + Inf":    ("Unwieldy", "Regenerate 5", "Steadfast"),
    "Pale Throne max":      ("Unwieldy", "Regenerate 4", "Steadfast"),                # +Inf+Hosp innate
    "Pale Throne max + RR": ("Unwieldy", "Regenerate 4", "Regenerate Reroll", "Steadfast"),
    "Pale Throne + MWGF":   ("Unwieldy", "Regenerate", "Steadfast", "MW Weapons", "GF Armor"),

    "Elder Grove":          ("Nimble", "Steady"),                                     # requires PO 1+
    "Elder Grove + RP":     ("Nimble", "Steady", "Drilled"),

    "Undying Flame":        ("Steadfast",),                                           # same as Preceptory in-engine
    "Ashen Vale":           ("Poison",),                                              # all retinues poison
    "Yew Heart":            ("Yew Heart",),                                           # ranged +1 to hit
    "Yew Heart TY":         ("Yew Heart", "Immune Unwieldy"),                         # +Tiltyard mastery
    "Blazing Standard":     ("Steadfast",),                                           # free Preceptory mastery

    # — Ministry of Strategy (Sovereign Prowess monument) —
    # Reveal opponent's tactic before picking yours. Counter-pick with 80% confidence.
    # Three variants test different firing frequencies.
    "Ministry: every":      ("Ministry: every",),                                     # every skirmish
    "Ministry: first":      ("Ministry: first",),                                     # first skirmish only
    "Ministry: once":       ("Ministry: once",),                                      # once per battle (modeled as first)

    # — Endgame meta stack —
    "Crusader King":        ("Drilled", "Nimble", "Steadfast", "Parry", "MW Weapons", "GF Armor", "Cond Field"),
}


# ==============================================================================
# Pursuit cost system — Military Pursuit Count & Domain Count
# ==============================================================================
# Each Loadout's "Military Pursuit Count" is the total building-cost of the
# pursuits a player must have invested in to field this loadout. A player has a
# fixed budget (default 13 points); spending more on military pursuits means
# spending less on income, faith, etc. Domain Count tracks domain investment.

# Pursuit catalog: cost, prereqs, domain requirements, granted tags, upkeep effects.
#
# upkeep_effect: per-retinue gold reduction. Three forms:
#   - {"flat": N}             → -N flat per retinue while pursuit is owned
#   - {"if_shield": N}        → -N per retinue if loadout has a shield
#   - {"if_ranged": N}        → -N per retinue if loadout has a ranged weapon
#   - {"if_armor_in": ([armors], N)} → -N per retinue if loadout's armor is in the list
#   Multiple effects stack (a pursuit may have both flat and conditional).
PURSUITS_INFO = {
    # ─ Prowess line ─
    "Coliseum":       {"cost": 1, "prereqs": [],
                       "domain": {"Prowess": 3},
                       "tags": ["Cond Field"]},                # +1 Max Endurance + MaA unlock
    "Levy Hall":      {"cost": 1, "prereqs": [],
                       "domain": {"Prowess": 3},
                       "tags": [],
                       "upkeep_effects": [{"flat": 5}]},        # -5 upkeep per retinue (army-wide)
    "War College":    {"cost": 2, "prereqs": [],
                       "domain": {"Prowess": 6},
                       "tags": []},                            # Sgt unlock (independent of Coliseum)
    "Ministry":       {"cost": 1, "prereqs": ["War College"],
                       "domain": {"Prowess": 10},
                       "tags": ["Seize: first"]},               # Seize the Initiative (1st skirmish; opponent never gets it). Mastery → Seize: every
    "Ministry Mastery": {"cost": 0, "prereqs": ["Ministry"],
                       "domain": {"Prowess": 10},
                       "tags": ["Seize: every"]},               # mastery upgrade: Seize EVERY skirmish (cost folded; mastery = full dedicated buildings)
    "Carpentry":      {"cost": 1, "prereqs": [],
                       "domain": {},
                       "tags": []},                            # non-combat; prereq for Joinery, Fletchery
    "Fletchery":      {"cost": 1, "prereqs": ["Carpentry"],
                       "domain": {},
                       "tags": [],
                       "upkeep_effects": [{"if_ranged": 5}]},   # -5 if loadout has ranged weapon
    "Tiltyard":       {"cost": 1, "prereqs": ["Fletchery", "Coliseum"],
                       "domain": {"Prowess": 6},
                       "tags": ["Immune Unwieldy"]},
    "Royal Pavilion": {"cost": 1, "prereqs": ["Tiltyard"],
                       "domain": {"Prowess": 10},
                       "tags": ["Drilled", "Nimble", "Immune Strain"]},
    # ─ Industry line (tier pursuits — exactly one represents the tier used) ─
    "Animal Husbandry":{"cost": 1, "prereqs": [],
                       "domain": {},
                       "tags": []},                            # cheap base for Butchery/Tannery; free if Stable
    "Stable":         {"cost": 2, "prereqs": [],
                       "domain": {},
                       "tags": []},                            # Lance unlock; implicitly grants Animal Husbandry
    "Butchery":       {"cost": 2, "prereqs": ["Animal Husbandry", "Tannery"],
                       "domain": {},
                       "tags": [],
                       "upkeep_effects": [{"flat": 5}]},
    "Smokehouse":     {"cost": 0, "prereqs": ["Butchery"],
                       "domain": {},
                       "tags": [],
                       "upkeep_effects": [{"flat": 5}]},        # free with Butchery
    "Tannery":        {"cost": 1, "prereqs": ["Animal Husbandry"],
                       "domain": {},
                       "tags": [],
                       "upkeep_effects": [{"flat": 5}]},        # Leather/Kite unlock; flat -5
    "Joinery":        {"cost": 1, "prereqs": ["Carpentry"],
                       "domain": {"Industry": 3},
                       "tags": [],
                       "upkeep_effects": [{"if_shield": 5}]},   # shields require Joinery; -5 if shielded
    "Furnace":        {"cost": 1, "prereqs": [],
                       "domain": {},
                       "tags": []},                            # Cast tier
    "Blacksmith":     {"cost": 1, "prereqs": [],
                       "domain": {"Industry": 3},
                       "tags": []},                            # Wrought tier
    "Armory":         {"cost": 1, "prereqs": ["Tannery", "Blacksmith"],
                       "domain": {"Industry": 3},
                       "tags": [],
                       "upkeep_effects": [{"flat": 5}]},        # Chainmail/Scutum unlock; flat -5
    "Forge":          {"cost": 1, "prereqs": [],
                       "domain": {"Industry": 6},
                       "tags": []},                            # Forged tier
    "Master Workshop":{"cost": 1, "prereqs": ["Forge"],
                       "domain": {"Industry": 6},
                       "tags": ["MW Weapons"],
                       "upkeep_effects": [{"flat": 5}]},
    "MWRend":         {"cost": 1, "prereqs": ["Forge"],
                       "domain": {"Industry": 6},
                       "tags": ["Rend"],
                       "upkeep_effects": [{"flat": 5}]},        # TEST pursuit: Rend instead of MW's AP-1; xor with Master Workshop
    "Gilded Foundry": {"cost": 1, "prereqs": ["Armory"],
                       "domain": {"Industry": 6},
                       "tags": ["GF Armor"],
                       "upkeep_effects": [{"flat": 5}]},
    "ABF":            {"cost": 1, "prereqs": ["Stable", "Master Workshop", "Gilded Foundry"],
                       "domain": {"Industry": 10},
                       "tags": ["MW Weapons", "GF Armor"],
                       "upkeep_effects": [{"flat": 5}]},        # Crafted tier; base 1, 0 if Forge (efficiency line)
    # ─ Cunning line ─
    "Toxicarium":     {"cost": 2, "prereqs": [],
                       "domain": {"Cunning": 3},
                       "tags": ["Poison"]},                    # Rising Cunning; Poison on weapons
    "Caravanery":     {"cost": 1, "prereqs": [],
                       "domain": {"Cunning": 6},
                       "tags": []},                            # Established Cunning building (Outrider prereq)
    "Cipher Chamber": {"cost": 1, "prereqs": [],
                       "domain": {"Cunning": 6},
                       "tags": []},                            # Established Cunning building (Outrider prereq)
    "Outrider Intercept Post": {"cost": 1, "prereqs": ["Caravanery", "Cipher Chamber"],
                       "domain": {"Cunning": 10},
                       "tags": ["Ministry: once"]},            # Sovereign Cunning monument; tactic-reveal once/battle. Base 1.
    "Outrider Mastery": {"cost": 2, "prereqs": ["Outrider Intercept Post"],
                       "domain": {"Cunning": 10},
                       "tags": ["Ministry: every"]},           # mastery upgrade (+2 → total 3): tactic-reveal EVERY skirmish
    # ─ Piety line ─
    "Apothecary":     {"cost": 1, "prereqs": [],
                       "domain": {},
                       "tags": ["Apothecary Heal"]},
    "Infirmary":      {"cost": 1, "prereqs": [],
                       "domain": {},
                       "tags": ["Regenerate 5"]},
    "Hospitaller":    {"cost": 1, "prereqs": [],
                       "domain": {"Piety": 6},
                       "tags": []},
    "Preceptory":     {"cost": 1, "prereqs": [],
                       "domain": {"Piety": 10, "Prowess": 6},
                       "tags": ["Steadfast"]},
    "Preceptory KT":  {"cost": 2, "prereqs": ["Preceptory", "Hospitaller"],
                       "domain": {"Piety": 10, "Prowess": 6},
                       "tags": []},
}

# Tier → Industry domain requirement (Rising/Established/Sovereign mapping)
TIER_INDUSTRY_REQ = {"Crude": 0, "Cast": 0, "Wrought": 3, "Forged": 6, "Crafted": 10}

# Mapping from tier pursuit → gear tier string
TIER_PURSUIT_TO_TIER = {None: "Crude", "Furnace": "Cast", "Blacksmith": "Wrought",
                        "Forge": "Forged", "ABF": "Crafted"}


def _gear_tier_idx(loadout_weapon, loadout_shield, loadout_armor, loadout_ranged, rules=None):
    """Return the highest tier index used by any gear piece on this loadout."""
    weapons = _weapons(rules)
    ranged_table = _ranged(rules)
    shields = _shields(rules)
    armors = _armors(rules)
    max_idx = 0
    if loadout_weapon and loadout_weapon != "Farm Tools":
        max_idx = max(max_idx, TIER_IDX.get(weapons[loadout_weapon]["tier"], 0))
    if loadout_armor:
        max_idx = max(max_idx, TIER_IDX.get(armors[loadout_armor]["tier"], 0))
    if loadout_shield:
        max_idx = max(max_idx, TIER_IDX.get(shields[loadout_shield]["tier"], 0))
    if loadout_ranged:
        max_idx = max(max_idx, TIER_IDX.get(ranged_table[loadout_ranged].get("tier", "Crude"), 0))
    return max_idx


def derive_retinue_from_pursuits(pursuits, rules=None):
    """The player's retinue is DETERMINED by what's built — not chosen separately.

    Rules:
      - Full Preceptory (Preceptory + Preceptory KT + Hospitaller) → Knight Templar
      - War College (without full Preceptory) → Sergeant  [no longer needs Coliseum]
      - Coliseum alone (no War College) → Man-at-Arms
      - Nothing → Levy

    NOTE: War College is depegged from Coliseum. A Sergeant build need not carry
    Coliseum. If a Sergeant wants the Tiltyard chain (which requires Coliseum), they
    must buy Coliseum separately. Coliseum now appears mainly on Man-at-Arms builds
    and on Sergeants/KTs that specifically want the Tiltyard/Royal Pavilion line.
    """
    has_full_precep = ({"Preceptory", "Preceptory KT", "Hospitaller"} <= pursuits)
    if has_full_precep:
        return "Knight Templar"
    if "War College" in pursuits:
        return "Sergeant"
    if "Coliseum" in pursuits:
        return "Man-at-Arms"
    return "Levy"


def derive_tier_from_pursuits(pursuits, rules=None):
    """The WEAPON gear tier is DETERMINED by the tier pursuit built (highest one wins).

    NOTE: As of the building-driven gating rules, tier pursuits gate ONLY weapons.
    Armor tier is gated by armor-craft buildings (Tannery/Armory/GF/ABF) and shield
    tier is gated by Joinery + the appropriate metal building. See ARMOR_REQUIRES
    and SHIELD_METAL_REQUIRES below.

    Rules (weapons):
      - ABF → Crafted (only)
      - Forge → Forged (only)
      - Blacksmith → Wrought (only)
      - Furnace → Cast (only)
      - Nothing → Crude
    """
    if "ABF" in pursuits:
        return "Crafted"
    if "Forge" in pursuits:
        return "Forged"
    if "Blacksmith" in pursuits:
        return "Wrought"
    if "Furnace" in pursuits:
        return "Cast"
    return "Crude"


# Armor → required armor-craft building. Cloth is free (no building).
# ABF subsumes GF subsumes Armory subsumes Tannery in the craft ladder, so a higher
# building should satisfy a lower armor too (any player with ABF can field Leather,
# Chainmail, Full Plate, AND Gothic Plate). This is enforced as set-membership.
ARMOR_REQUIRES = {
    "Cloth":        set(),                                              # no building required
    "Leather":      {"Tannery", "Armory", "Gilded Foundry", "ABF"},     # any of these
    "Chainmail":    {"Armory", "Gilded Foundry", "ABF"},
    "Full Plate":   {"Gilded Foundry", "ABF"},
    "Gothic Plate": {"ABF"},
}

# Shield → required metal-craft building (besides Joinery, which all shields need).
# Wooden Shield uses no metal — just Joinery. Higher metal-craft buildings subsume
# lower ones (Armory satisfies Kite's Tannery requirement, GF satisfies Scutum's
# Armory, etc.).
SHIELD_METAL_REQUIRES = {
    "Wooden Shield":  set(),                                              # no metal building
    "Kite Shield":    {"Tannery", "Armory", "Gilded Foundry", "ABF"},
    "Scutum Shield":  {"Armory", "Gilded Foundry", "ABF"},
    "Tower Shield":   {"Gilded Foundry", "ABF"},
    "Heater Shield":  {"ABF"},
}


def armor_satisfied(armor_name, pursuits, rules=None):
    """True if the loadout's pursuits include a building that unlocks the given armor."""
    required = _armor_requires(rules).get(armor_name, set())
    if not required:
        return True  # no building needed (Cloth)
    return bool(required & pursuits)


def shield_satisfied(shield_name, pursuits, rules=None):
    """True if the loadout has Joinery AND any of the metal-craft buildings the shield needs.
    Wooden Shield needs only Joinery (no metal)."""
    if "Joinery" not in pursuits:
        return False
    required_metal = _shield_metal_requires(rules).get(shield_name, set())
    if not required_metal:
        return True  # only Joinery needed (Wooden Shield)
    return bool(required_metal & pursuits)


def compute_pursuit_cost(pursuits, rules=None):
    """Compute cost, domain requirements, and granted tags from a pursuit set.

    Cost model: every pursuit innately costs 1. A pursuit costs 0 if its upstream
    EFFICIENCY-LINE parent is already in the set — you're extending an existing
    production line rather than standing up a new building. The efficiency chains:

        Blacksmith → Forge → ABF            (smithing / weapon-tier line)
        Tannery   → Armory → Gilded Foundry (hide / metal armor line)
        Animal Husbandry → Stable           (livestock line)

    So e.g. with Blacksmith in the set, Forge costs 0; and with Forge present, ABF
    costs 0 — the whole Blacksmith→Forge→ABF line costs just 1 (Blacksmith's base).
    Discounts stack down the chain.

    MW and MWRend are mutually exclusive (enforced in validity); each costs 1.

    Returns (total_cost, domain_dict, tags_set).
    """
    pursuits_info = _pursuits_info(rules)
    pursuits_for_cost = set(pursuits)

    # Efficiency lines: {downstream: upstream_parent}. Downstream costs 0 if parent present.
    EFFICIENCY_PARENT = {
        "Forge":          "Blacksmith",
        "ABF":            "Forge",
        "Armory":         "Tannery",
        "Gilded Foundry": "Armory",
        "Stable":         "Animal Husbandry",
        "Infirmary":      "Apothecary",
    }

    total_cost = 0
    for p in pursuits_for_cost:
        parent = EFFICIENCY_PARENT.get(p)
        if parent is not None and parent in pursuits_for_cost:
            cost_p = 0   # extending an existing line — free
        else:
            cost_p = pursuits_info[p]["cost"]
        total_cost += cost_p

    # Domain requirements
    domain = {"Industry": 0, "Prowess": 0, "Piety": 0, "Cunning": 0}
    for p in pursuits:
        for d, v in pursuits_info[p]["domain"].items():
            domain[d] = max(domain[d], v)
    # Industry requirement may also come from the actual gear tier
    tier_str = derive_tier_from_pursuits(pursuits, rules=rules)
    domain["Industry"] = max(domain["Industry"], _tier_industry_req(rules)[tier_str])

    # Granted tags
    tags = set()
    for p in pursuits:
        tags.update(pursuits_info[p]["tags"])

    # Hospitaller mastery: full stack adds Regenerate Reroll
    if "Hospitaller" in pursuits and "Apothecary" in pursuits and "Infirmary" in pursuits:
        tags.add("Regenerate Reroll")

    # Workshop variant resolution: MWRend chose the Rend workshop, so it replaces the
    # MW Weapons (AP-1) tag that ABF would otherwise grant. A build never has both
    # MW Weapons and Rend — the workshop is built one way.
    if "MWRend" in pursuits:
        tags.discard("MW Weapons")
        tags.add("Rend")

    # Mastery upgrades replace their base tag (never emit both base + mastery).
    if "Ministry Mastery" in pursuits:
        tags.discard("Seize: first")          # mastery → Seize every (already added)
    if "Outrider Mastery" in pursuits:
        tags.discard("Ministry: once")        # mastery → tactic-reveal every (already added)

    return total_cost, domain, tags


def compute_effective_upkeep(loadout, rules=None):
    """Compute per-retinue upkeep AFTER all pursuit-based reductions.

    Walks the loadout's pursuits, applies flat reductions and conditional
    reductions (based on equipped shield, ranged weapon, or armor type).
    Returns the reduced per-retinue cost. Floor of 5 to prevent free retinues.

    Conditionals checked:
      - "if_shield": active when loadout.shield is not None
      - "if_ranged": active when loadout.ranged is not None
      - "if_armor_in": active when loadout.armor in the listed armor set
    """
    base = _retinues(rules)[loadout.retinue]["cost"]
    reduction = 0
    has_shield = loadout.shield is not None
    has_ranged = loadout.ranged is not None
    for p in loadout.pursuits:
        effects = _pursuits_info(rules).get(p, {}).get("upkeep_effects", [])
        for eff in effects:
            if "flat" in eff:
                reduction += eff["flat"]
            if "if_shield" in eff and has_shield:
                reduction += eff["if_shield"]
            if "if_ranged" in eff and has_ranged:
                reduction += eff["if_ranged"]
            if "if_armor_in" in eff:
                armors, amount = eff["if_armor_in"]
                if loadout.armor in armors:
                    reduction += amount
    # Floor at 5 gold per retinue to prevent free troops
    return max(5, base - reduction)


# ──────────────────────────────────────────────────────────────────────────
# Pursuit-set enumeration: which pursuit sets are valid (no waste, no
# unsatisfied prereqs)?
# ──────────────────────────────────────────────────────────────────────────
# A pursuit set is valid if:
#   - All structural prereqs are met (e.g., MW requires Forge or ABF)
#   - No pursuit is "wasted" in the sense the user described (e.g., Stable
#     without Forge/ABF would never be built since Lance needs Forged)

def _pursuit_set_is_valid(pursuits, rules=None):
    # Prereq satisfaction (a pursuit's prereqs must be in the set, with subsumption)
    has_forge_or_abf = ("Forge" in pursuits) or ("ABF" in pursuits)
    # Stable implicitly grants Animal Husbandry (no explicit AH needed if Stable present)
    has_animal_husbandry = ("Animal Husbandry" in pursuits) or ("Stable" in pursuits)
    # Master Workshop and MWRend are mutually exclusive — a workshop is built one way
    # or the other (AP-1 vs Rend). MWRend is a TEST pursuit for comparison.
    if "Master Workshop" in pursuits and "MWRend" in pursuits:
        return False
    # ABF requires a Master Workshop OR MWRend (either workshop variant satisfies it),
    # plus Stable + Gilded Foundry.
    if "ABF" in pursuits:
        if not (("Master Workshop" in pursuits) or ("MWRend" in pursuits)):
            return False
        if "Stable" not in pursuits or "Gilded Foundry" not in pursuits:
            return False
    # Outrider Intercept Post requires both Cunning buildings.
    if "Outrider Intercept Post" in pursuits:
        if not ({"Caravanery", "Cipher Chamber"} <= pursuits):
            return False
    # Mastery upgrades require their base monument.
    if "Outrider Mastery" in pursuits and "Outrider Intercept Post" not in pursuits:
        return False
    if "Ministry Mastery" in pursuits and "Ministry" not in pursuits:
        return False
    # Caravanery / Cipher Chamber are only useful as Outrider prereqs — don't allow them
    # to appear without Outrider (no wasted Cunning buildings).
    if ("Caravanery" in pursuits or "Cipher Chamber" in pursuits) and "Outrider Intercept Post" not in pursuits:
        return False
    # War College is depegged from Coliseum (no prereq). Sergeant via War College alone.
    # Ministry requires War College
    if "Ministry" in pursuits and "War College" not in pursuits:
        return False
    # Carpentry: no prereq, but Joinery/Fletchery require it
    if "Joinery" in pursuits and "Carpentry" not in pursuits:
        return False
    if "Fletchery" in pursuits and "Carpentry" not in pursuits:
        return False
    # Tiltyard requires Fletchery + Coliseum
    if "Tiltyard" in pursuits and not ({"Fletchery", "Coliseum"} <= pursuits):
        return False
    # Royal Pavilion requires Tiltyard
    if "Royal Pavilion" in pursuits and "Tiltyard" not in pursuits:
        return False
    # Tannery requires Animal Husbandry (Stable counts as substitute)
    if "Tannery" in pursuits and not has_animal_husbandry:
        return False
    # Butchery requires Animal Husbandry + Tannery
    if "Butchery" in pursuits and (not has_animal_husbandry or "Tannery" not in pursuits):
        return False
    # Smokehouse requires Butchery (Smokehouse is built into a Butchery)
    if "Smokehouse" in pursuits and "Butchery" not in pursuits:
        return False
    # Armory requires Tannery + Blacksmith (Forge/ABF count as Blacksmith via subsumption)
    has_blacksmith_tier = ("Blacksmith" in pursuits) or has_forge_or_abf
    if "Armory" in pursuits and ("Tannery" not in pursuits or not has_blacksmith_tier):
        return False
    # Master Workshop requires Forge or ABF (ABF auto-includes MW, but if MW is
    # in the set, the player needs Forge tier minimum)
    if "Master Workshop" in pursuits and not has_forge_or_abf:
        return False
    # Gilded Foundry now requires Armory (Tannery+Blacksmith path) + Forge/ABF
    if "Gilded Foundry" in pursuits and (not has_forge_or_abf or "Armory" not in pursuits):
        return False
    # Preceptory KT requires Preceptory + Hospitaller
    if "Preceptory KT" in pursuits and not ({"Preceptory", "Hospitaller"} <= pursuits):
        return False
    # Stable is only useful for Lance, which requires Forged tier. Skip otherwise.
    if "Stable" in pursuits and not has_forge_or_abf:
        return False
    # If ABF in pursuits, Stable/MW/GF are auto-included; pruning duplicates in cost.
    return True


def _load_loadouts_from_csv(csv_path, rules=None):
    """Load loadouts from a CSV produced by an earlier archetype_pool() export.

    Expected columns (extras are ignored, missing optional cols default safely):
      name, retinue, weapon, shield, armor, ranged, tiltyard, size, tags,
      military_pursuit_count, domain_count, pursuits, upkeep_per_retinue

    Empty-string values for `weapon`, `shield`, `ranged` become None.
    `tags` is comma-separated; `pursuits` is pipe-separated.
    `tiltyard` accepts "True"/"False"/"1"/"0".
    """
    import csv
    pool = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            retinue = row["retinue"]
            weapon = row.get("weapon", "") or None
            shield = row.get("shield", "") or None
            ranged = row.get("ranged", "") or None
            armor = row["armor"]

            ty_raw = str(row.get("tiltyard", "False")).strip().lower()
            has_tiltyard = ty_raw in ("true", "1", "yes")

            size = int(row.get("size") or 50)
            tags_str = row.get("tags", "") or ""
            extra_tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            mpc = int(row.get("military_pursuit_count") or 0)
            dc = int(row.get("domain_count") or 0)
            pursuits_str = row.get("pursuits", "") or ""
            pursuits = frozenset(p.strip() for p in pursuits_str.split("|") if p.strip())

            upkeep = int(row.get("upkeep_per_retinue") or _retinues(rules)[retinue]["cost"])

            pool.append(Loadout(
                name=row["name"],
                retinue=retinue, weapon=weapon, shield=shield, armor=armor,
                ranged=ranged, has_tiltyard=has_tiltyard, size=size,
                extra_tags=extra_tags,
                upkeep_per_retinue=upkeep,
                playstyle=None,
                tiltyard_mastery=True,
                pursuits=pursuits,
                military_pursuit_count=mpc,
                domain_count=dc,
            ))
    return pool


def archetype_pool(min_pursuit_cost=5, max_pursuit_cost=10, csv_path=None, rules=None):
    """Enumerate loadouts. Two modes:

      1. CSV mode (`csv_path` given): load loadouts directly from a CSV file
         produced by an earlier run. Useful for reproducibility — work from a
         frozen, pre-computed pool instead of regenerating.

      2. Generator mode (default): derive loadouts from pursuit-set enumeration
         per the rules below.

    Generator mode derives everything from the pursuit set:

    Player decision = which pursuits to build. Everything else is derived:
      - retinue: derive_retinue_from_pursuits
      - tier: derive_tier_from_pursuits
      - arms:
          * EXPLICIT Stable in pursuits → Lance forced (Lance is Forged tier)
            + Tiltyard → Lance + Ranged dual-equip
            + no Tiltyard → Lance only
          * Fletchery + Tiltyard (no Stable) → melee at tier + Ranged
          * Fletchery only (no Tiltyard, no Stable) → ranged only (weapon=None,
            sim uses Farm Tools as placeholder)
          * Nothing → melee at tier only
      - shield: at tier, only for 1H melee weapons (Lance special: Kite/Scutum)
      - armor: at tier
      - tags: union of pursuit-granted tags + Regenerate Reroll for full Hospitaller

    Note on ABF: ABF (Crafted) is a 5pt all-inclusive package. It subsumes
    Stable + MW + GF + Forge. ABF in pursuits does NOT auto-imply explicit
    Stable purchase, so ABF players can still choose between Poleaxe (Crafted)
    or — if they also explicitly bought Stable — Lance (Forged). The "Stable
    → Lance" rule applies only to explicit Stable purchases.
    """
    # ── CSV mode ──────────────────────────────────────────────────────────
    if csv_path is not None:
        return _load_loadouts_from_csv(csv_path, rules=rules)

    pool = []
    weapons = _weapons(rules)
    ranged_table = _ranged(rules)
    shields = _shields(rules)

    # ── Gear tables ──────────────────────────────────────────────────────
    # Weapons by tier (melee), respecting weapon spec tier exactly.
    WEAPONS_BY_TIER = {
        "Crude":   ["Cudgel", "Farm Tools"],
        "Cast":    ["Daggers", "Short Sword", "Spears"],
        "Wrought": ["Arming Sword", "Pike", "Flail", "Halberd", "Battle Axe"],
        "Forged":  ["Bastard Sword", "2HBastard", "Morningstar", "War Hammer"],  # Lance handled via Stable
        "Crafted": ["Poleaxe"],                                       # Only Poleaxe is Crafted
    }
    ARMOR_BY_TIER = {
        "Crude":   ["Cloth"],
        "Cast":    ["Leather"],
        "Wrought": ["Chainmail"],
        "Forged":  ["Full Plate"],
        "Crafted": ["Gothic Plate"],
    }
    SHIELDS_BY_TIER = {
        "Crude":   ["Wooden Shield"],
        "Cast":    ["Kite Shield"],
        "Wrought": ["Scutum Shield"],
        "Forged":  ["Tower Shield"],
        "Crafted": ["Heater Shield"],
    }
    RANGED_BY_TIER = {
        "Crude":   ["Hunting Bow"],
        "Cast":    ["Longbow"],
        "Wrought": ["Javelin"],
        "Forged":  ["Crossbow"],
        "Crafted": ["Pilum"],
    }

    TIER_PURSUITS = [None, "Furnace", "Blacksmith", "Forge", "ABF"]
    RETINUE_CHAINS = [
        frozenset(),                                                   # Levy
        frozenset(["Coliseum"]),                                       # MaA
        frozenset(["War College"]),                                    # Sgt (depegged from Coliseum)
        frozenset(["Preceptory", "Preceptory KT", "Hospitaller"]),     # KT
    ]
    INDEPENDENT_OPTIONS = [
        # Coliseum is NOT a free option — it comes from the MaA retinue seed, or is
        # force-added when Tiltyard is selected (Tiltyard requires Coliseum). Listing it
        # here would let it attach to Levy/Sgt seeds and silently promote/mislabel them.
        "Levy Hall",     # Rising Prowess; -5 upkeep flat
        "Joinery",       # Rising Industry; shield unlock; -5 upkeep if shielded; needs Carpentry
        "Fletchery",     # ranged unlock; -5 upkeep if ranged; needs Carpentry
        "Tiltyard",      # dual-equip + Immune Unwieldy (force-adds Coliseum as prereq)
        "Stable",        # Lance unlock; implicitly grants Animal Husbandry
        "Royal Pavilion",
        "Ministry",
        "Ministry Mastery",          # Seize every skirmish (mastery upgrade)
        "Outrider Intercept Post",   # Cunning monument: tactic-reveal once/battle
        "Outrider Mastery",          # tactic-reveal every skirmish (mastery upgrade)
        "Master Workshop",
        "MWRend",        # TEST pursuit: Rend variant of Master Workshop (xor with MW)
        "Gilded Foundry",
        "Tannery",       # -5 flat + -5 if cloth/leather; auto-bundles with Armory (shared slot)
        # NOTE: Armory is NOT a separate option — it auto-bundles with Tannery.
        "Butchery",      # -5 flat; needs Animal Husbandry + Tannery
        "Toxicarium",    # Rising Cunning; Poison tag on weapons
        # Health-stack collapsed: 'Full Hospitaller' represents the full
        # Apothecary + Infirmary + Hospitaller bundle (3pt, all the tags).
        "Full Hospitaller",
        "Preceptory",
    ]
    # Pursuits that get auto-included when one of their dependents is sampled.
    # These never appear as standalone choices but are added to the pursuit set
    # whenever a dependent is present. Costs are still applied (per PURSUITS_INFO).
    AUTO_INCLUDED = {
        "Carpentry":         ["Joinery", "Fletchery"],         # Carpentry forced when either present
        "Animal Husbandry":  ["Tannery", "Butchery"],          # Stable also implies it (handled in cost)
        "Smokehouse":        ["Butchery"],                     # free with Butchery (0 cost)
        # Tiltyard chain requires Coliseum — force it in so Sgt/KT who take Tiltyard
        # pay for Coliseum (they don't get it from their retinue seed post-depeg).
        "Coliseum":          ["Tiltyard", "Royal Pavilion"],
        # Tannery and Armory share a building slot — players build them together when both
        # are useful. If either is sampled, include the other (combined cost is 1 per the
        # shared-slot rule in compute_pursuit_cost). This cuts the search tree on this axis.
        "Tannery":           ["Armory"],
        "Armory":            ["Tannery"],
        # Ministry mastery forces base Ministry; Outrider chain dependencies.
        "Ministry":          ["Ministry Mastery"],
        "Caravanery":        ["Outrider Intercept Post"],
        "Cipher Chamber":    ["Outrider Intercept Post"],
        "Outrider Intercept Post": ["Outrider Mastery"],
    }

    seen_keys = {}

    for tier_p in TIER_PURSUITS:
        tier_str = TIER_PURSUIT_TO_TIER[tier_p]
        for ret_chain in RETINUE_CHAINS:
            retinue_guess = derive_retinue_from_pursuits(ret_chain, rules=rules)
            # Levy capped at Wrought; MaA+ uses Wrought minimum
            if retinue_guess == "Levy" and tier_str in ("Forged", "Crafted"):
                continue
            if retinue_guess != "Levy" and tier_str in ("Crude", "Cast"):
                continue
            # Sergeant and Knight Templar require Forge minimum (Forged tier or better).
            # The investment in higher-tier muster justifies high-tier equipment.
            if retinue_guess in ("Sergeant", "Knight Templar") and tier_str in ("Wrought",):
                continue

            for mask in range(1 << len(INDEPENDENT_OPTIONS)):
                opt_set = frozenset(INDEPENDENT_OPTIONS[i] for i in range(len(INDEPENDENT_OPTIONS))
                                     if mask & (1 << i))
                pursuits = set(ret_chain) | set(opt_set)
                if tier_p:
                    pursuits.add(tier_p)
                # Expand the "Full Hospitaller" macro into its three component pursuits.
                if "Full Hospitaller" in pursuits:
                    pursuits.discard("Full Hospitaller")
                    pursuits.update(("Apothecary", "Infirmary", "Hospitaller"))
                # Auto-include forced prereqs (Carpentry for Joinery/Fletchery,
                # Animal Husbandry for Tannery/Butchery, Smokehouse free with Butchery).
                for forced, deps in AUTO_INCLUDED.items():
                    # Tannery↔Armory bundle: ONLY auto-include Armory if Blacksmith-tier or
                    # higher metallurgy is present (Armory's prereq). Otherwise the bundle
                    # would force the loadout into Wrought tier and block Cast-tier Leather
                    # builds. The reverse direction (Armory→Tannery) always fires.
                    if forced == "Armory" and not (
                        "Blacksmith" in pursuits or "Forge" in pursuits or "ABF" in pursuits
                    ):
                        continue
                    if any(d in pursuits for d in deps):
                        pursuits.add(forced)

                # Validate prereqs (no auto-promote — explicit purchases must
                # have their prereqs satisfied or the combo is skipped)
                if not _pursuit_set_is_valid(pursuits, rules=rules):
                    continue

                # Re-derive retinue from the FINAL pursuit set (after auto-includes).
                # Post-depeg, Coliseum only enters via the MaA seed or the Tiltyard
                # auto-include; re-deriving guarantees the stored label matches the
                # actual pursuits (e.g., a Tiltyard MaA that gains Coliseum stays MaA,
                # and nothing is silently mislabeled).
                retinue_guess = derive_retinue_from_pursuits(pursuits, rules=rules)
                # Re-apply the Levy/tier gating now that retinue is final.
                if retinue_guess == "Levy" and tier_str in ("Forged", "Crafted"):
                    continue
                if retinue_guess != "Levy" and tier_str in ("Crude", "Cast"):
                    continue
                if retinue_guess in ("Sergeant", "Knight Templar") and tier_str == "Wrought":
                    continue

                # Cost check: pool restricted to MPC in [min_pursuit_cost, max_pursuit_cost].
                # Default range is [5, 13] — players will realistically have at least 5pts
                # of military buildings, and 13 is the upper budget cap.
                total_cost, domain, tags = compute_pursuit_cost(pursuits, rules=rules)
                if total_cost > max_pursuit_cost or total_cost < min_pursuit_cost:
                    continue

                # Max 2 monuments per loadout (unique one-per-game buildings). A player
                # realistically commits to at most a couple of these capstones.
                _MONUMENTS = ("ABF", "Royal Pavilion", "Preceptory",
                              "Ministry", "Outrider Intercept Post")
                if sum(1 for m in _MONUMENTS if m in pursuits) > 2:
                    continue

                # ── Derive arms ──
                # "Stable → Lance" rule only fires on EXPLICIT Stable purchase
                has_stable_explicit = "Stable" in opt_set
                has_fletch = "Fletchery" in pursuits
                has_ty = "Tiltyard" in pursuits
                has_abf = "ABF" in pursuits

                # Determine (weapon, ranged, has_ty) options for this pursuit set.
                #
                # Crafted-tier players have a special wrinkle: the spec has no Crafted
                # 1H melee weapon (only Poleaxe is Crafted, and it's 2H). A Crafted player
                # who wants a shield must "downgrade" to a Forged 1H weapon but keeps
                # their Crafted shield (Heater) and Crafted armor (Gothic). The Crafted
                # tag (e.g. MW Weapons) still applies to the 1H weapon since the player
                # has access to Crafted-quality equipment.
                CRAFTED_1H_FALLBACK = ["Bastard Sword", "Morningstar"]  # Forged tier 1H

                def melee_options_for_tier(t):
                    """Melee weapons available to a player at gear tier t.
                    Crafted players have Poleaxe (2H Crafted) OR a Forged 1H weapon
                    paired with Crafted shield/armor.
                    """
                    if t == "Crafted":
                        return WEAPONS_BY_TIER["Crafted"] + CRAFTED_1H_FALLBACK
                    return WEAPONS_BY_TIER[t]

                arms_options = []
                if has_stable_explicit and has_ty:
                    # Lance + Ranged at tier
                    for r in _ranged_at_or_below(tier_str, RANGED_BY_TIER):
                        arms_options.append(("Lance", r, True))
                    # ALSO offer the tier's melee weapons + ranged (Stable doesn't FORCE Lance;
                    # it UNLOCKS it). Without this, Crafted builds — which require Stable via
                    # ABF — could never field Poleaxe (the only Crafted melee weapon).
                    for w in melee_options_for_tier(tier_str):
                        for r in _ranged_at_or_below(tier_str, RANGED_BY_TIER):
                            arms_options.append((w, r, True))
                elif has_stable_explicit:
                    arms_options.append(("Lance", None, False))
                    # Stable unlocks Lance but doesn't preclude the tier's own melee weapons.
                    for w in melee_options_for_tier(tier_str):
                        arms_options.append((w, None, False))
                elif has_fletch and has_ty:
                    # Dual-equip: melee at gear tier + ranged
                    for w in melee_options_for_tier(tier_str):
                        for r in _ranged_at_or_below(tier_str, RANGED_BY_TIER):
                            arms_options.append((w, r, True))
                elif has_fletch:
                    # Ranged-only
                    for r in _ranged_at_or_below(tier_str, RANGED_BY_TIER):
                        arms_options.append((None, r, False))
                else:
                    # Melee-only
                    for w in melee_options_for_tier(tier_str):
                        arms_options.append((w, None, False))

                # ── Enumerate shields and armor ──
                for weapon, ranged, ty in arms_options:
                    # Shield: highest-tier shield available for this combo.
                    # - 2H weapon: no shield.
                    # - Lance: Crafted → Heater (highest for Lance); Forged → Scutum
                    #   (Tower forbidden, so Scutum is highest available); lower tiers
                    #   also use Scutum if Wrought or shield at tier otherwise.
                    # - 1H melee: shield at player's gear tier.
                    # - Ranged-only (weapon is None): no shield.
                    # Shield options under building-driven gating: pick the HIGHEST shield
                    # the building set unlocks. Like the previous "always highest available"
                    # rule, but driven by buildings instead of weapon tier. Players who
                    # didn't invest in higher metallurgy get a lower shield.
                    #
                    # Crossbow exception: when ranged=Crossbow, the only allowed shield is
                    # Tower (pavise). We generate two variants when possible:
                    #   - With Tower Shield (if building-satisfied AND melee allows Tower)
                    #   - Without shield (Lance+Crossbow, pure-Crossbow without Tower buildings)
                    # valid_combo enforces the Tower-only rule downstream.
                    SHIELD_LADDER = ["Heater Shield","Tower Shield","Scutum Shield",
                                     "Kite Shield","Wooden Shield"]
                    if ranged == "Crossbow":
                        # Crossbow restricts shields: Tower only, or None. But honor the
                        # init floor — if weapon+Tower would be < -1 base init (e.g.
                        # Morningstar -1 + Tower -1 = -2), Tower isn't offered; the loadout
                        # runs shieldless instead (no lower shield is legal with Crossbow).
                        w_init = weapons[weapon]["init"] if weapon and weapon != "Farm Tools" else 0
                        opts = [None]
                        if (shield_satisfied("Tower Shield", pursuits, rules=rules)
                                and w_init + shields["Tower Shield"]["init"] >= -1):
                            opts.append("Tower Shield")
                        shield_opts = opts
                    elif weapon is None or is_2h(weapon, rules=rules):
                        shield_opts = [None]
                    else:
                        # Highest available shield by DEFENSIVE value, but skip any shield
                        # that would push base initiative below -1 (weapon init + shield init).
                        # Step down the defensive ladder until a building-satisfied shield
                        # keeps base init >= -1. E.g. Morningstar(-1)+Tower(-1) = -2 is skipped;
                        # falls to the next legal shield (Kite/Heater at init 0 → total -1).
                        w_init = weapons[weapon]["init"] if weapon and weapon != "Farm Tools" else \
                                 (ranged_table[ranged]["init"] if ranged else 0)
                        best_shield = None
                        for s in SHIELD_LADDER:
                            if not shield_satisfied(s, pursuits, rules=rules):
                                continue
                            if w_init + shields[s]["init"] < -1:
                                continue   # would break the init floor; try a lower-tier shield
                            best_shield = s
                            break
                        shield_opts = [best_shield] if best_shield else [None]

                    # Armor options: highest building-satisfied tier. Cloth is the fallback
                    # if no armor-craft building is present.
                    ARMOR_LADDER = ["Gothic Plate","Full Plate","Chainmail","Leather","Cloth"]
                    armor_opts = [next((a for a in ARMOR_LADDER
                                        if armor_satisfied(a, pursuits, rules=rules)), "Cloth")]

                    for shield in shield_opts:
                        for armor in armor_opts:
                            if not valid_combo(retinue_guess, weapon or "Farm Tools",
                                                shield, armor, ranged, ty, rules=rules):
                                continue
                            # Cross-validation: equipment requires specific pursuits.
                            # Shields require Joinery PLUS a metal-craft building based on tier.
                            # Wooden Shield needs only Joinery.
                            if shield is not None and not shield_satisfied(shield, pursuits, rules=rules):
                                continue
                            # Armor requires its armor-craft building. Cloth is free.
                            if not armor_satisfied(armor, pursuits, rules=rules):
                                continue
                            # Ranged weapons require Fletchery (carpentry-based ranged
                            # production; Carpentry is a Fletchery prereq).
                            if ranged is not None and "Fletchery" not in pursuits:
                                continue
                            # 1H melee weapons require Joinery (the woodworking that produces
                            # hafts/grips). Exemptions:
                            #   - Farm Tools (improvised) and 2H/ranged weapons.
                            #   - Crossbow loadouts: a Crossbow forces Tower-only/no-shield, and
                            #     Lance+Crossbow has NO legal shield at all, so requiring Joinery
                            #     on these makes no sense.
                            # (Plain 'Bastard Sword' now always has a shield → covered by the
                            #  shield's own Joinery requirement. '2HBastard' is 2H → exempt here.)
                            requires_joinery = (
                                weapon is not None and weapon != "Farm Tools"
                                and not is_2h(weapon, rules=rules)
                                and ranged != "Crossbow"
                            )
                            if requires_joinery and "Joinery" not in pursuits:
                                continue
                            tags_tuple = tuple(sorted(tags))
                            obs_key = (retinue_guess, weapon, shield, armor, ranged, ty, tags_tuple)
                            if obs_key in seen_keys and seen_keys[obs_key][0] <= total_cost:
                                continue
                            domain_count = sum(domain.values())
                            if domain_count > 26:
                                continue   # cap total domain investment at 26 (avoids all-in late-game builds)
                            name = _name(retinue_guess, weapon, shield, armor, ranged, ty,
                                         list(tags), playstyle=None)
                            ld = Loadout(
                                name=name,
                                retinue=retinue_guess, weapon=weapon, shield=shield, armor=armor,
                                ranged=ranged, has_tiltyard=ty, size=50,
                                extra_tags=sorted(tags),
                                upkeep_per_retinue=0,  # placeholder; reset below
                                playstyle=None,
                                tiltyard_mastery=True,
                                pursuits=frozenset(pursuits),
                                military_pursuit_count=total_cost,
                                domain_count=domain_count,
                            )
                            # Compute upkeep AFTER construction (needs loadout object
                            # so the conditional reductions can inspect equipment).
                            ld = ld._replace(upkeep_per_retinue=compute_effective_upkeep(ld, rules=rules))
                            seen_keys[obs_key] = (total_cost, ld)
    return [v[1] for v in seen_keys.values()]


def _ranged_at_or_below(tier_str, table):
    """Ranged weapons at or below the given gear tier."""
    order = ["Crude", "Cast", "Wrought", "Forged", "Crafted"]
    idx = order.index(tier_str)
    out = []
    for t in order[:idx + 1]:
        out.extend(table[t])
    return out


def with_playstyle(loadout, playstyle):
    """Return a copy of `loadout` with a different playstyle (and updated name).
    Useful for one-off comparisons.
    """
    new_name = _name(loadout.retinue, loadout.weapon, loadout.shield, loadout.armor,
                     loadout.ranged, loadout.has_tiltyard, loadout.extra_tags,
                     playstyle=playstyle)
    return loadout._replace(name=new_name, playstyle=playstyle)


def kt_twins(pool, rules=None):
    """For every KT loadout in `pool`, create a twin that's the SAME KT retinue & equipment
    but assigned the equipment-natural NON-Unshakable playstyle (computed by temporarily
    treating the loadout as a non-KT to bypass the KT→Unshakable rule).

    Purpose: isolate the playstyle effect WITHIN KT. We can ask "does
    KT/Bastard/Tower/FullPlate perform better as Unshakable or as Patient?" while
    holding the retinue and equipment constant.

    Returns the new twins only — does not modify or include the original pool.

    Notes:
      - Twins are still Knight Templar (rout-immune stat preserved). Only the playstyle
        changes.
      - The natural playstyle is derived by running assign_default_playstyle on a
        temporary copy with retinue set to "Sergeant" (matches KT's premium gear tier
        and bypasses the KT→Unshakable first-rule). This gives the equipment-based
        playstyle the loadout "would have" if it weren't KT.
      - Twin gets a " (NaturalPS)" suffix so it's distinguishable in CSVs.
    """
    from playstyles import assign_default_playstyle
    twins = []
    for ld in pool:
        if ld.retinue != "Knight Templar":
            continue
        # Spoof retinue to Sergeant to derive the equipment-natural playstyle
        spoof = ld._replace(retinue="Sergeant")
        natural_ps = assign_default_playstyle(spoof, rules=rules)
        # If somehow the natural playstyle is still Unshakable (shouldn't happen with
        # current rules, but be defensive), skip — no useful twin to create.
        if natural_ps == "Unshakable":
            continue
        new_name = _name(ld.retinue, ld.weapon, ld.shield, ld.armor,
                         ld.ranged, ld.has_tiltyard, ld.extra_tags,
                         playstyle=natural_ps) + " (NaturalPS)"
        twin = ld._replace(name=new_name, playstyle=natural_ps)
        twins.append(twin)
    return twins


def cross_playstyle_pool(base_pool, playstyles):
    """Take a base pool and cross every loadout with every playstyle.
    Output: len(base_pool) * len(playstyles) loadouts.
    Used for "8 playstyles × 216 loadouts" sweep tournaments.
    """
    out = []
    for ld in base_pool:
        for ps in playstyles:
            out.append(with_playstyle(ld, ps))
    return out


def optimal_playstyle_pool(base_pool, rules=None):
    """For each loadout in `base_pool`, assign its heuristic optimal playstyle.
    Returns a new pool the same size, each loadout tagged with one chosen style.
    """
    from playstyles import assign_default_playstyle
    return [with_playstyle(ld, assign_default_playstyle(ld, rules=rules)) for ld in base_pool]


if __name__ == "__main__":
    pool = archetype_pool()
    print(f"Generated {len(pool)} loadouts")
    print()
    print("Sample (first 30):")
    for ld in pool[:30]:
        print(f"  {ld.name}")
    print(f"  ... ({len(pool) - 30} more)")
    print()
    print(f"Tournament size: {len(pool)} × {len(pool)} = {len(pool)**2:,} matchups")
    print(f"At 100 runs/matchup: {len(pool)**2 * 100:,} battles")
