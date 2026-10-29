"""
Loadout generator for the combat tournament.
Two entry points:
- `archetype_pool()`: curated pool of representative builds players would actually
  field, covering faction archetypes, spec-pathway endgames, and spec combinations.
- `generate_loadouts(...)`: flexible iterator for custom sweeps.
Naming convention:
  Without ranged:    Sgt/Halberd/Chain [Steadfast, Regen 5]
  With shield:       Sgt/Bastard/Heater/FullPlate
  With ranged:       Sgt/Halberd+Javelin/Chain
  With Tiltyard:     Sgt/Halberd+Javelin/Chain (TY)
Tags shown in brackets are the full extra_tags list (engine sees what name shows).
Engine-recognized extra_tags:
  Combat keywords:    Steady, Nimble, Unwieldy, Drilled, Steadfast, Parry, Poison
  Defensive:          Regenerate, Regenerate 5, Regenerate 4, Regenerate Reroll (engine-supported, no longer granted by any spec)
  Immunities:         Immune Unwieldy, Immune Poison
  Spec effects:       Rend (worsens enemy Regenerate), GF Armor (incoming AP -1), Cond Field (+1 Endurance)
  Faction flag:       Yew Heart (ranged +1 to Hit)
"""
from collections import namedtuple
from renown_data import RETINUES, WEAPONS, RANGED, SHIELDS, ARMORS
import renown_data as _rd_st
# Standing thresholds from data; fallback keeps this file copy-compatible with Combatv3 (D6) data.
_ST = getattr(_rd_st, "STANDING_THRESHOLDS", {"Untested": 1, "Rising": 3, "Established": 6, "Sovereign": 10})
_RIS, _EST, _SOV = _ST["Rising"], _ST["Established"], _ST["Sovereign"]
# Keyword constants so tag-injection sites point at VARIABLES, not literals (rename-safe).
from renown_data import (
    SHATTER_ARMOR, CLEAVE, DEFLECT, DESTROY_SHIELD, DRILLED, DUAL_WIELD, HALFSWORD,
    MINUS_1_TBH, MINUS_1_PARRY, NEGATE_RIPOSTE, NEGATE_TEMPERED, NEGATE_UNSTOPPABLE,
    NIMBLE, ONE_SHOT, PARRY, PLANISHING, POISON, RECOVER, RIPOSTE, SERRATED,
    STEADY, STRAIN, TWO_H, UNBREAKABLE, UNSTOPPABLE, UNWIELDY,
    IMMUNE_DESTROY_SHIELD, IMMUNE_STRAIN, IMMUNE_UNWIELDY,
)
from dice_config import RECOVER_BASE
Loadout = namedtuple("Loadout",
    "name retinue weapon shield armor ranged has_tiltyard size extra_tags upkeep_per_retinue playstyle tiltyard_mastery pursuits military_pursuit_count domain_count")
Loadout.__new__.__defaults__ = (None, True, frozenset(), 0, 0)  # playstyle, tiltyard_mastery, pursuits, mpc, domain_count
# ==============================================================================
# Tier ordering, abbreviations
# ==============================================================================
TIER_ORDER = ["Crude", "Cast", "Wrought", "Forged", "Crafted"]
TIER_IDX = {t: i for i, t in enumerate(TIER_ORDER)}
# Stable-gated cavalry weapons. These are charge weapons: they may NOT dual-equip
# a ranged weapon, and may NOT take the Tiltyard two-of-same Dual Wield path.
# Keyed here once so the rule is enforced consistently in valid_combo,
# _structural_legal, and the archetype_pool two-of-same block.
STABLE_WEAPONS = frozenset({"Lance", "Cavalry Spear"})
# Default army size. Half-scale game: 25 troops (front 10 / reserve 5). Old full-scale was 50.
# CSV pools that store an explicit size are overridden to this on load unless the size differs
# intentionally; regenerated pools use this directly.
DEFAULT_ARMY_SIZE = 25
RETINUE_TIER = {
    # Legacy ordering index (kept for sorting/labels only).
    # NO tier floors or caps — gear access is gated by infrastructure pursuits, not retinue.
    "Levy": 0,
    "Man-at-Arms": 1,
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
    "Buckler Shield": "Buckler",
    "Targe Shield": "Targe",
    "Kite Shield": "Kite",
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
    "Recover 8":         "Rec 8",
    "Recover 7":         "Rec 7",
    "Recover 6":         "Rec 6",
    "Recover 5":         "Rec 5",
    "Recover 4":         "Rec 4",
    SERRATED:          "Serr",
    PLANISHING:          "Temp",   # tag value is "Tempered" (PLANISHING constant); display abbrev = Temp
    "Crit 5":            "Crit5",
    "+1I":               "+1I",
    "Immune Panic":      "ImmPanic",
    IMMUNE_UNWIELDY:   "ImmU",
    "Immune Poison":     "ImmP",
    "Apothecary Heal":   "ApoHeal",
    "Cond Field":        "CFM",
    "Outrider: every":   "Outr:every",
    "Outrider: first_two": "Outr:1-2",
    "Outrider: first":   "Outr:first",
    "Outrider: once":    "Outr:once",
    "Seize: first_two":  "Seize:1-2",
    "Seize: first":      "Seize:1st",
    "Seize: every":      "Seize:every",
    "Immune Tactic TH": "ImmTacTH",
    "Rend":        "Rend",
    "GF Armor":          "GF",
    "Shake +1":          "Shake+1",
    "Yew Heart":         "YewHeart",
    DUAL_WIELD:        "DW",
}
def _w_label(w):
    return WEAPON_LABEL.get(w, w)
# Monument abbreviations for the name bracket: first two letters of each word (skipping "of"),
# ABF keeps its established acronym. Duplicates would be extended by one letter (none currently).
_MON_ABBR = {
    "Royal Pavilion": "RoPa",
    "Advanced Blast Furnace": "ABF",
    "Preceptory of the Knight's Templar": "Pr",
    "Ministry of Military Strategy": "MiMiSt",
    "Outrider Intercept Post": "OuInPo",
}
# Tags absorbed into the domain-standing tuple (they ARE the standing's grant):
_DOMAIN_TAGS = {"Immune Blocked", PARRY, "confers:Blocked", "confers:Strain"}
def _standing_letter(v):
    return "S" if v >= _SOV else ("E" if v >= _EST else ("R" if v >= _RIS else "N"))
def _name(retinue, weapon, shield, armor, ranged, has_tiltyard, extra_tags, playstyle=None,
          pursuits=None):
    """Build a human-readable name for a loadout.
    Format: RET/WEAPON[+RANGED]/SHIELD/ARMOR (TY) [bracket] <playstyle>
    - Pure-ranged (no real melee weapon — None or the Farm Tools placeholder): the ranged weapon is
      shown AS the weapon (Lev/Longbow/Leather). (TY) only appears when actually dual-equipping.
    - If `pursuits` is given, the bracket is: monument markers first (RoPaM/RoPaI, ABFM, ...), then
      the 4-domain standing tuple (xInd, xProw, xPie, xCun) with x in {N,R,E,S}, then remaining tags.
      Monument-granted tags and domain-standing tags (Immune Blocked/Parry/confers:*) are absorbed
      into the marker/tuple. Without `pursuits`, the legacy flat-tag bracket is used.
    - Riposte implies the parry kit (Parry from Established Prowess, Improved Parry from the Grand
      Tournament innate), so both are hidden whenever Riposte is shown. Display-only."""
    parts = [RETINUE_LABEL[retinue]]
    pure_ranged = ranged and (weapon is None or weapon == "Farm Tools")
    if pure_ranged:
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
    if has_tiltyard and ranged and not pure_ranged:
        base += " (TY)"   # marks an actual dual-equip (melee + ranged)
    elif (has_tiltyard and not ranged and weapon and weapon != "Farm Tools"
          and DUAL_WIELD in (extra_tags or [])
          and DUAL_WIELD not in WEAPONS.get(weapon, {}).get("tags", [])):
        # Tiltyard two-of-same: a non-intrinsic-DW 1H weapon doubled to gain Dual Wield.
        # (Daggers carry DW intrinsically and are excluded by the weapon-tag check.)
        base += " (DW)"
    tags = list(extra_tags) if extra_tags else []
    # Display only the strongest Regenerate tier (engine takes min threshold; dominated tags are noise)
    _regen_rank = {"Regenerate 4": 4, "Regenerate 5": 5, "Regenerate 6": 6, "Regenerate": RECOVER_BASE,
                   "Recover 4": 4, "Recover 5": 5, "Recover 6": 6, "Recover 7": 7, "Recover 8": 8, RECOVER: RECOVER_BASE}
    _regen_present = [t for t in tags if t in _regen_rank]
    if len(_regen_present) > 1:
        best = min(_regen_present, key=lambda t: _regen_rank[t])
        tags = [t for t in tags if t not in _regen_rank or t == best]
    bracket_items = []
    if pursuits:
        P = set(pursuits)
        hidden = set(_DOMAIN_TAGS)
        # monument markers (first in the bracket), absorbing their granted tags
        for mon in sorted(P & _POOL_MONUMENTS):
            info = PURSUITS_INFO[mon]
            if not [t for t in info["innate_tags"] if not t.startswith(_INFO_PREFIX) and t not in _INFO_EXACT]:
                continue                                   # monuments with no combat effect stay out of the name
            bracket_items.append(_MON_ABBR.get(mon) or "".join(
                w[:2] for w in mon.replace("'s", "").split() if w.lower() not in ("of", "the")))
            hidden.update(_ENGINE_TOKEN.get(t, t) for t in info["innate_tags"])
        # 4-domain standing tuple
        _, dom, _ = compute_pursuit_cost(P)
        bracket_items.append("({}Ind, {}Prow, {}Pie, {}Cun)".format(
            _standing_letter(dom.get("Industry", 0)), _standing_letter(dom.get("Prowess", 0)),
            _standing_letter(dom.get("Piety", 0)), _standing_letter(dom.get("Cunning", 0))))
        if RIPOSTE in tags:
            hidden.add("Improved Parry")
        bracket_items += [TAG_DISPLAY.get(t, t) for t in tags if t not in hidden]
    elif tags:
        # legacy flat bracket (no pursuit info available)
        _display = [t for t in tags
                    if not (t in (PARRY, "Improved Parry") and RIPOSTE in tags)]
        bracket_items = [TAG_DISPLAY.get(t, t) for t in _display]
    if bracket_items:
        base += f" [{', '.join(bracket_items)}]"
    if playstyle and playstyle != "Random":
        base += f" <{playstyle}>"
    return base
# ==============================================================================
# Validity
# ==============================================================================
def is_2h(weapon_name):
    if weapon_name is None:
        return False
    profile = WEAPONS.get(weapon_name) or RANGED.get(weapon_name)
    if profile is None:
        # Weapon name not in either table (e.g. a renamed/removed profile still referenced by a
        # build-kit list). It can't be two-handed if it doesn't exist; don't crash the generator.
        return False
    tags = profile.get("tags", [])
    # Dual Wield confers 2H (both hands on weapons) — a Dual Wield weapon never carries a shield.
    return (TWO_H in tags) or (DUAL_WIELD in tags)
def ranged_satisfied(ranged, pursuits):
    """True if the build unlocks this ranged weapon: a Holding whose text 'Unlocks Ranged Weapons'
    (Fletchery), plus any Holdings the RANGED profile lists in 'requires' (Arquebus: Artillery Park)."""
    if ranged is None:
        return True
    if "ranged" not in _tokens(pursuits):
        return False
    return all(req in pursuits for req in RANGED.get(ranged, {}).get("requires", []))


def valid_combo(retinue, weapon, shield, armor, ranged, has_tiltyard, allow_tier_mismatch=2):
    """Filter for sensible combinations.
    - 2H melee disallows shields.
    - 1H melee REQUIRES a shield (except Bastard Sword, which has both profiles).
      Farm Tools is exempt as the universal sidearm fallback in pure-ranged builds.
    - 1H melee: shield tier must be >= weapon tier (universal rule).
      Note: the "shield tier == weapon tier without ABF" rule is path-specific
      and enforced in archetype_pool() by restricting shield_options per path.
    - Lance disallows Tower Shield.
    - Poleaxe cannot be used by Levy (rules).
    - One-Shot ranged (Javelin, Crossbow) requires Tiltyard.
    - Dual-equip (real melee + ranged) REQUIRES Tiltyard.
    - Stable (cavalry) weapons cannot dual-equip a ranged weapon (charge weapons).
    - Pure-ranged exception: Farm Tools + ranged represents a ranged-focused build.
    """
    if is_2h(weapon) and shield is not None:
        return False
    # Stable cavalry weapons (Lance, Cavalry Spear) are charge weapons: no dual-equip
    # with a ranged weapon. (DW two-of-same is blocked separately in archetype_pool.)
    if weapon in STABLE_WEAPONS and ranged is not None:
        return False
    # Lance restrictions: cannot use Tower (too unwieldy on horse) or Wooden (too cheap).
    # Lance CAN use Kite, Scutum, or Heater Shield.
    if weapon in ("Lance", "Cavalry Spear") and shield == "Tower Shield":
        return False
    # (Crossbow is 2H like the other bows: no Crossbow-specific shield rule.)
    if weapon == "Poleaxe" and retinue == "Levy":
        return False
    # Plain 'Bastard Sword' must ALWAYS carry a shield (it's the 1H profile that only
    # swaps to 2HBastard if the shield is destroyed). A shieldless Bastard is invalid —
    # the always-2H form is the separate '2HBastard' weapon. This also blocks
    # Bastard+Crossbow (which would be shieldless), forcing 2HBastard+Crossbow instead.
    if weapon == "Bastard Sword" and shield is None:
        return False
    # 1H weapons (no "2H" tag) require a shield, except Farm Tools.
    if (weapon != "Farm Tools"
            and not is_2h(weapon)
            and shield is None):
        return False
    # 1H + shield: shield tier must be >= weapon tier
    # Exception: Lance is exempt from the tier rule (only the explicit forbidden-shield
    # list above applies). Lance can use Kite, Scutum, or Heater regardless of weapon tier.
    if shield is not None and not is_2h(weapon) and weapon != "Farm Tools" and weapon not in ("Lance", "Cavalry Spear"):
        weapon_tier_idx = TIER_IDX.get(WEAPONS[weapon]["tier"], 0)
        shield_tier_idx = TIER_IDX.get(SHIELDS[shield]["tier"], 0)
        if shield_tier_idx < weapon_tier_idx:
            return False
    # One-Shot ranged weapons (Javelin, Crossbow) require Tiltyard.
    if ranged is not None and ONE_SHOT in RANGED[ranged].get("tags", []):
        if not has_tiltyard:
            return False
    # Dual-equip requires Tiltyard. Real melee + ranged without Tiltyard is invalid.
    has_real_melee = weapon != "Farm Tools"
    if has_real_melee and ranged is not None and not has_tiltyard:
        return False
    retinue_idx = RETINUE_TIER[retinue]
    armor_tier_idx = TIER_IDX.get(ARMORS[armor]["tier"], -1)   # tier None (Cloth) = below Crude
    FORGED_IDX = TIER_IDX["Forged"]
    CRAFTED_IDX = TIER_IDX["Crafted"]
    # Pure-ranged loadout: weapon is Farm Tools fallback, real weapon is ranged.
    if weapon == "Farm Tools" and ranged is not None:
        return True
    weapon_tier_idx = TIER_IDX.get(WEAPONS[weapon]["tier"], 0)
    # NO retinue tier floors or caps — gear access is gated by infrastructure (tier pursuits),
    # not retinue. MPC/TI spread is an emergent property of gameplay trajectories, so the
    # validation pool samples the full retinue x gear cross.
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
    sizes=(DEFAULT_ARMY_SIZE,),
    tag_sets=((),),  # tuple of tag-tuples
    playstyles=(None,),  # tuple of playstyle names. None = Random.
    allow_tier_mismatch=2,
):
    """Yield valid Loadouts across the given option lists.
    tag_sets: a tuple of tag-tuples. Each tag-tuple is the COMPLETE extra_tags
    for that loadout. Pass `((),)` for vanilla only.
    playstyles: tuple of playstyle names. Each loadout will be replicated under each style.
    """
    retinue_options  = retinue_options  or list(RETINUES.keys())
    weapon_options   = weapon_options   or list(WEAPONS.keys())
    shield_options   = shield_options   or list(SHIELDS.keys())
    armor_options    = armor_options    or list(ARMORS.keys())
    ranged_options   = ranged_options   or [None] + list(RANGED.keys())
    out = []
    for ret in retinue_options:
        for w in weapon_options:
            for s in shield_options:
                for a in armor_options:
                    for r in ranged_options:
                        for ty in tiltyard_options:
                            if ty and r is None:
                                continue
                            if not valid_combo(ret, w, s, a, r, ty, allow_tier_mismatch):
                                continue
                            for size in sizes:
                                for tag_tuple in tag_sets:
                                    for ps in playstyles:
                                        upkeep = RETINUES[ret]["cost"]
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
    DRILLED:              (DRILLED,),
    NIMBLE:               (NIMBLE,),
    STEADY:               (STEADY,),
    "Steadfast":            ("Immune Panic",),                  # Preceptory innate / Undying Flame (legacy preset name)
    PARRY:                (PARRY,),                         # Edict of War (Sovereign Prowess)
    "Cond Field":           ("Cond Field",),                    # Conditioning Field mastery
    "Rend":           (SERRATED,),               # Master Workshop mastery
    "GF Armor":             (PLANISHING,),                      # Gilded Foundry mastery
    "Immune Poison":        (),                                 # Apothecary no longer grants Immune Poison (disabled)
    "Apothecary Heal":      ("Apothecary Heal",),               # Apothecary mastery: Heal 1 per 4 cas (Immune Poison removed)
    POISON:               (POISON,),                        # Toxicarium innate
    IMMUNE_UNWIELDY:      (IMMUNE_UNWIELDY,),               # Tiltyard mastery
    # — Recover ladder (d10; tags read literally as N+) —
    "Recover 8+":           ("Recover 8",),                     # Apothecary mastery
    "Recover 7+":           ("Recover 7",),                     # Infirmary mastery
    "Recover 6+":           ("Recover 6",),                     # Hospitaller innate
    # — Spec combinations (multi-spec pathways) —
    "Royal Pavilion":       (DRILLED, NIMBLE),                                    # RP mastery
    "Preceptory":           ("Immune Panic",),                                        # Preceptory innate
    "Pre + RP":             (DRILLED, NIMBLE, "Immune Panic"),
    "Pre + RP + Parry":     (DRILLED, NIMBLE, "Immune Panic", PARRY),
    "RP + Conditioned":     (DRILLED, NIMBLE, "Cond Field"),
    "Pre + RP + Cond":      (DRILLED, NIMBLE, "Immune Panic", "Cond Field"),
    "MW + GF":              (SERRATED, PLANISHING),
    "Industry Elite":       (SERRATED, PLANISHING, "Cond Field"),
    "Apo + Tox":            (POISON,),
    "Apo + Inf":            ("Recover 6",),
    "Apo + Inf + Hosp":     ("Recover 5",),
    "Apo + Inf + Hosp(M)":  ("Recover 4",),
    # — Faction effects —
    "Pale Throne":          (UNWIELDY, "Recover 6", "Immune Panic"),                # mandatory faction tags
    "Pale Throne + Inf":    (UNWIELDY, "Recover 5", "Immune Panic"),
    "Pale Throne max":      (UNWIELDY, "Recover 4", "Immune Panic"),                # +Inf+Hosp innate
    "Pale Throne max + HM": (UNWIELDY, "Recover 4", "Immune Panic"),                # Hosp mastery: 4+ floor — no gain for PT
    "Pale Throne + MWGF":   (UNWIELDY, "Recover 6", "Immune Panic", SERRATED, PLANISHING),
    "Elder Grove":          (NIMBLE, STEADY),                                     # requires PO 1+
    "Elder Grove + RP":     (NIMBLE, STEADY, DRILLED),
    "Undying Flame":        ("Immune Panic",),                                        # same as Preceptory in-engine
    "Ashen Vale":           (POISON,),                                              # all retinues poison
    "Yew Heart":            ("Yew Heart",),                                           # ranged +1 to hit
    "Yew Heart TY":         ("Yew Heart", IMMUNE_UNWIELDY),                         # +Tiltyard mastery
    "Blazing Standard":     ("Immune Panic",),                                        # free Preceptory mastery
    # — Ministry of Strategy (Sovereign Prowess monument) —
    # Reveal opponent's tactic before picking yours. Counter-pick with 80% confidence.
    # Three variants test different firing frequencies.
    "Outrider: every":      ("Outrider: every",),                                     # every skirmish (legacy/analysis)
    "Outrider: first":      ("Outrider: first",),                                     # first skirmish only
    "Outrider: once":       ("Outrider: once",),                                      # once per battle (modeled as first)
    # — Endgame meta stack —
    "Crusader King":        (DRILLED, NIMBLE, "Steadfast", PARRY, "Rend", "GF Armor", "Cond Field"),
}
# ==============================================================================
# Holding model — Military Pursuit Count & Domain Count
# ==============================================================================
# Everything here is read from renown_data.HOLDING_SIM, which the data file derives from the
# SIMPLE_NODES text ('innate' / 'unlock' / 'efficient' / 'root' / 'monument'). The legacy
# per-node 'engine' field (hand-written sim tags, prereqs, per-Retinue upkeep, aliases) is retired.
#
#   tags      'innate' text -> tokens (renown_data.holding_combat_tags). Unlock tokens
#             (tier:/armor:/shield:/weapon:/retinue:/ranged/dual-equip/Florentine) gate gear;
#             the rest are combat keywords handed to the engine.
#   lines     a Holding needs one complete Mastery Chain line ('efficient' parents, any one of
#             them, recursively) unless it is a Root. Parents that aren't Holdings (Hamlet, ...)
#             are settlement conditions and count as met.
#   MPC       Settlement Wards used: every Holding takes a Ward unless it shares its immediate
#             parent's Ward (each Holding carries at most one descendant in its Ward).
#   domain    Standing requirements from 'unlock'; "1 Rising" etc. = any Domain (met by the
#             build's highest Domains).
#   upkeep    Army upkeep = the Retinue type's cost - "Upkeep -N" in the build's text;
#             conditional clauses count at renown_data.COND_UPKEEP_FACTOR.
import re as _re
from collections import Counter as _Counter
import renown_data as rd

_SIM = rd.HOLDING_SIM
_INFO_PREFIX = ("tier:", "armor:", "shield:", "weapon:", "retinue:", "anytier:")
_INFO_EXACT = {"ranged", "cavalry", "dual-equip", "Artillery Park", "Init +1", "Lance only"}   # board-only (Marshal Tiltyard)   # "Florentine" both gates Dual Wield and reaches the engine
_ENGINE_TOKEN = {"Righteous Fervour": "Resolute"}     # text keyword -> engine tag of the same rule
_BONUS_TOKEN = _re.compile(r"^(\w+) \+(\d+)$")

# Kept under its old name for callers; now a pure view of HOLDING_SIM (no mastery: every tag is innate).
PURSUITS_INFO = {n: {"cost": 1, "domain": dict(h["domain"]), "innate_tags": list(h["tags"]),
                     "mastery_tags": [], "mastery_req": [], "prereqs": list(h["parents"]),
                     "root": h["root"], "monument": h["monument"], "upkeep": list(h["upkeep"])}
                 for n, h in _SIM.items()}


def _tokens(pursuits):
    return {t for p in pursuits if p in _SIM for t in _SIM[p]["tags"]}


def _holders(token):
    """Holdings whose text grants `token`, cheapest line first (deterministic)."""
    hs = [n for n, h in _SIM.items() if token in h["tags"]]
    return sorted(hs, key=lambda n: (len(_line(n, frozenset()) or ()), n))


def _holder(token):
    hs = _holders(token)
    return hs[0] if hs else None


# ── Mastery Chain lines ──────────────────────────────────────────────────────
def _line(name, have, stack=()):
    """Smallest set of Holdings to add so `name` stands on one complete line (None = no line)."""
    if name in have and _line_ok(name, have):  # present AND standing on a line (cycles: Saddlery<->Caravanery)
        return frozenset()
    h = _SIM.get(name)
    if h is None:
        return frozenset()                      # not a Holding (Hamlet, 'Natural', ...): a settlement condition
    if h["root"] or not h["parents"]:
        return frozenset([name])
    best = None
    for p in h["parents"]:
        if p in stack:
            continue
        sub = _line(p, have, stack + (name,))
        if sub is not None and (best is None or len(sub) < len(best)):
            best = sub
    return None if best is None else best | {name}


def _line_ok(name, P, stack=()):
    """True if `name` has one complete line inside P."""
    h = _SIM.get(name)
    if h is None or h["root"] or not h["parents"]:
        return True
    for p in h["parents"]:
        if p in stack:
            continue
        if p not in _SIM or (p in P and _line_ok(p, P, stack + (name,))):
            return True
    return False


def prereq_closure(pursuits):
    """The set plus the cheapest complete line for every Holding in it."""
    out = set(pursuits)
    changed = True
    while changed:
        changed = False
        for p in sorted(out):
            if _line_ok(p, out):
                continue
            add = _line(p, frozenset(out - {p}))           # cheapest line under p, given what's built
            if add and not add <= out:
                out |= add
                changed = True
    return out


def master_effect_closure(pursuits):
    """No Mastery in the Holding model — identity (kept for callers)."""
    return set(pursuits)


def _needed_by_line(h, P):
    """True if some other Holding in P loses its only line without h."""
    rest = set(P) - {h}
    return any(not _line_ok(q, rest) for q in rest)


def _pursuit_set_is_valid(pursuits):
    P = set(pursuits)
    return all(_line_ok(p, P) for p in P)


# ── what a pursuit set unlocks ───────────────────────────────────────────────
def derive_retinue_from_pursuits(pursuits):
    """Strongest Retinue whose 'Unlocks X for Muster' is in the build (RETINUES order); else Levy."""
    toks, best = _tokens(pursuits), next(iter(RETINUES))
    for r in RETINUES:
        if "retinue:" + r in toks:
            best = r
    return best


def derive_tier_from_pursuits(pursuits):
    """Highest weapon tier unlocked ('Unlocks X Weapons'); Crude needs nothing."""
    toks, best = _tokens(pursuits), TIER_ORDER[0]
    for t in TIER_ORDER:
        if "tier:" + t in toks:
            best = t
    return best


def armor_satisfied(armor_name, pursuits):
    """Armor of tier T needs a Holding with 'Unlock T armor & shield'; tierless armor (Cloth) is free."""
    tier = ARMORS[armor_name]["tier"]
    return tier is None or ("armor:" + tier) in _tokens(pursuits)


def shield_satisfied(shield_name, pursuits):
    """A shield needs 'unlocks Shields' (Joinery) AND its tier's 'Unlock T armor & shield' Holding."""
    toks = _tokens(pursuits)
    return "tier:Shields" in toks and ("shield:" + SHIELDS[shield_name]["tier"]) in toks


_POOL_MONUMENTS = frozenset(n for n, h in _SIM.items() if h["monument"])


def _normalize_pool_tokens(pursuits):
    """Pool tokens are real Holding names now — identity (kept for callers)."""
    return set(pursuits)


def _ward_count(P):
    """Settlement Wards used: each Holding shares its immediate parent's Ward when that parent is
    present and isn't already carrying a descendant."""
    carried, shared = set(), 0
    for p in sorted(P):
        h = _SIM.get(p)
        if not h:
            continue
        for par in h["parents"]:
            if par in P and par in _SIM and par not in carried:
                carried.add(par)
                shared += 1
                break
    return sum(1 for p in P if p in _SIM) - shared


def compute_pursuit_cost(pursuits):
    """(MPC, domain_dict, tags) for a Holding set.
    MPC = Settlement Wards used (see _ward_count); total investment = Holding count (analysis.py).
    Tags: every Holding's text tokens. '+N' bonuses stack ('Parry +1' twice -> 'Parry +2');
    'Recover N' is the base and each 'Recover +1' improves it by one rung."""
    P = set(pursuits)
    known = [p for p in P if p in _SIM]
    mpc = _ward_count(P)
    domain = {"Industry": 0, "Prowess": 0, "Piety": 0, "Cunning": 0}
    anyreq = []
    for p in known:
        for d, v in _SIM[p]["domain"].items():
            if d == "*":
                anyreq += v
            else:
                domain[d] = max(domain[d], v)
    for thr, count in sorted(anyreq):                  # "1 Rising" etc.: met by the highest Domains
        for d in sorted(domain, key=lambda k: -domain[k])[:count]:
            domain[d] = max(domain[d], thr)
    counts = _Counter(t for p in known for t in _SIM[p]["tags"])
    tags = set()
    for t, c in counts.items():
        if t.startswith(_INFO_PREFIX) or t in _INFO_EXACT or t.startswith("Recover "):
            continue
        m = _BONUS_TOKEN.match(t)
        if m:
            tags.add(f"{m.group(1)} +{int(m.group(2)) * c}")
            continue
        tags.add(_ENGINE_TOKEN.get(t, t))
    bases = [int(t.split()[1]) for t in counts if _re.match(r"^Recover \d+$", t)]
    if bases:
        tags.add(f"Recover {min(bases) - counts.get('Recover +1', 0)}")
    # ── Domain-standing SELF tags (unchanged from the legacy model; see DOMAIN_BOARD) ──
    if domain["Prowess"] >= _RIS:
        tags.add("Immune Blocked")
    if domain["Prowess"] >= _EST:
        tags.add(PARRY)
    if domain["Piety"] >= _EST:
        tags.add("Shake +1")
    if domain["Cunning"] >= _EST:
        tags.add("confers:Blocked")
    if domain["Cunning"] >= _SOV:
        tags.add("confers:Strain")
    return mpc, domain, tags


def compute_effective_upkeep(loadout):
    """Army upkeep (per Army, the batch engine's 'army cost'): the Retinue type's cost minus every
    'Upkeep -N' in the build's Holdings; conditional clauses count at COND_UPKEEP_FACTOR. Floor 0."""
    base = RETINUES[loadout.retinue]["cost"]
    red = 0.0
    for p in loadout.pursuits:
        for e in (_SIM.get(p) or {}).get("upkeep", []):
            red += base * e["factor"] if e.get("all") else e["amount"] * e["factor"]
    return max(0, int(round(base - red)))


def gear_requirements(weapon, shield, armor, ranged, two_of_same=False):
    """Unlock tokens a gear choice needs (the text tokens of the Holdings that unlock it)."""
    need = set()
    tiers = [WEAPONS[weapon]["tier"]] if weapon in WEAPONS else []
    if ranged:
        tiers.append(RANGED[ranged]["tier"])
    top = max(tiers, key=lambda t: TIER_IDX.get(t, 0)) if tiers else TIER_ORDER[0]
    if top != TIER_ORDER[0]:
        need.add("tier:" + top)
    if weapon in ("Cavalry Spear", "Lance"):
        need.add("weapon:" + weapon)
    if shield:
        need |= {"tier:Shields", "shield:" + SHIELDS[shield]["tier"]}
    if ARMORS[armor]["tier"]:
        need.add("armor:" + ARMORS[armor]["tier"])
    if ranged:
        need.add("ranged")
    if (ranged and weapon not in (None, "Farm Tools")) or (ranged and ONE_SHOT in RANGED[ranged].get("tags", [])):
        need.add("dual-equip")
    if two_of_same:
        need.add(rd.FLORENTINE)
    return need


def gear_seed(weapon, shield, armor, ranged, two_of_same=False):
    """Holdings that unlock a gear choice (one holder per token), plus RANGED 'requires' Holdings."""
    seed = {_holder(t) for t in gear_requirements(weapon, shield, armor, ranged, two_of_same)}
    seed.discard(None)
    if ranged:
        seed |= set(RANGED[ranged].get("requires", []))
    return seed


def _load_loadouts_from_csv(csv_path):
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
            ty_raw = str(row.get("has_tiltyard", row.get("tiltyard", "False"))).strip().lower()   # saved pools write has_tiltyard
            has_tiltyard = ty_raw in ("true", "1", "yes")
            size = DEFAULT_ARMY_SIZE
            # The CSV column is "extra_tags" (comma-separated). Older code looked for a
            # nonexistent "tags" column, silently dropping ALL tags (Ministry/Outrider/Cond
            # Field/etc.). Read extra_tags; fall back to "tags" for legacy files.
            tags_str = row.get("extra_tags", row.get("tags", "")) or ""
            extra_tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            mpc = int(row.get("military_pursuit_count") or 0)
            dc = int(row.get("domain_count") or 0)
            pursuits_str = row.get("pursuits", "") or ""
            pursuits = frozenset(p.strip() for p in pursuits_str.split("|") if p.strip())
            upkeep = int(row.get("upkeep_per_retinue") or RETINUES[retinue]["cost"])
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
def archetype_pool(min_pursuit_cost=5, max_pursuit_cost=10, csv_path=None, budget_metric="mpc", max_monuments=2):
    """Enumerate loadouts. Two modes:
      1. CSV mode (`csv_path` given): load a frozen pool exported by an earlier run.
      2. Generator mode (default): enumerate Holding sets and derive everything else from them.
    Generator mode: seeds = a weapon/armor line stopping point x a Retinue unlock x any subset of
    INDEPENDENT_OPTIONS (real Holding names). prereq_closure fills each Holding's cheapest complete
    Mastery Chain line. Then, all from the Holdings' text (renown_data.HOLDING_SIM):
      - retinue: strongest 'Unlocks X for Muster' present (else Levy)
      - weapon tier: highest 'Unlocks X Weapons'; melee at that tier, ranged at or below it
      - cavalry: 'Unlocks Cavalry Spear / Lance' (each still needs its weapon tier)
      - ranged: 'Unlocks Ranged Weapons'; dual-equip / two-of-same Dual Wield: Tiltyard's text
      - shield: 'unlocks Shields' + the tier's 'Unlock X armor & shield'; armor: that tier's unlock
      - tags: every Holding's combat keywords ('+N' bonuses stack, Recover rungs improve)
    Budget: budget_metric "mpc" = Settlement Wards used, "total" = Holding count."""
    # ── CSV mode ──────────────────────────────────────────────────────────
    if csv_path is not None:
        return _load_loadouts_from_csv(csv_path)
    # ── Gear tables (from the data) ──────────────────────────────────────
    WEAPONS_BY_TIER = {t: [] for t in TIER_ORDER}
    for _w, _wd in WEAPONS.items():
        if _w not in STABLE_WEAPONS:                      # cavalry weapons come from their own unlock
            WEAPONS_BY_TIER.setdefault(_wd["tier"], []).append(_w)
    RANGED_BY_TIER = {t: [] for t in TIER_ORDER}
    for _rn, _rw in RANGED.items():
        RANGED_BY_TIER.setdefault(_rw["tier"], []).append(_rn)
    # ── Seeds: real Holding names; every line under them is filled by prereq_closure ──
    # Weapon line x armor line stopping points.
    INDUSTRY_PATHS = [
        set(),
        {"Furnace"},
        {"Blacksmith"},
        {"Blacksmith", "Master Workshop"},
        {"Blacksmith", "Gilded Foundry"},
        {"Forge"},
        {"Forge", "Master Workshop"},
        {"Forge", "Gilded Foundry"},
        {"Forge", "Gilded Foundry", "Master Workshop"},
        {"Advanced Blast Furnace"},
        {"Advanced Blast Furnace", "Court Armoury"},
    ]
    # Retinue seeds: nothing (Levy) + each Holding whose text unlocks a Retinue for Muster.
    RETINUE_CHAINS = [frozenset()] + [frozenset([h]) for r in RETINUES for h in _holders("retinue:" + r)]
    INDEPENDENT_OPTIONS = [
        "Levy Hall", "Joinery", "Fletchery", "Tiltyard", "Stable", "Saddlery",
        "Royal Pavilion", "Grand Tournament", "Ministry of Military Strategy",
        "Outrider Intercept Post", "Tannery", "Armory", "Butchery", "Artillery Park",
        "Toxicarium", "Hospitaller", "Conditioning Field",
    ]
    INDEPENDENT_OPTIONS = [o for o in INDEPENDENT_OPTIONS if o in _SIM]
    seen_keys = {}

    def _sets():
        """Depth-first over option subsets, pruned on the budget: adding a Holding never lowers the
        Ward count or the Holding count, so once a seed is over budget every superset is too."""
        for industry_path in INDUSTRY_PATHS:
            for ret_chain in RETINUE_CHAINS:
                stack = [(0, frozenset(industry_path) | ret_chain)]
                while stack:
                    i, seed = stack.pop()
                    closed = frozenset(prereq_closure(seed))
                    if not _pursuit_set_is_valid(closed):
                        continue
                    cost, domain, tags = compute_pursuit_cost(closed)
                    budget = len(closed) if budget_metric == "total" else cost
                    if budget > max_pursuit_cost:
                        continue
                    if budget >= min_pursuit_cost:
                        yield closed, cost, domain, tags
                    for j in range(i, len(INDEPENDENT_OPTIONS)):
                        if INDEPENDENT_OPTIONS[j] not in closed:
                            stack.append((j + 1, seed | {INDEPENDENT_OPTIONS[j]}))

    _done = set()
    for pursuits, total_cost, domain, tags in _sets():
        if pursuits in _done:
            continue
        _done.add(pursuits)
        if sum(1 for m in _POOL_MONUMENTS if m in pursuits) > max_monuments:
            continue
        retinue_guess = derive_retinue_from_pursuits(pursuits)
        tier_str = derive_tier_from_pursuits(pursuits)
        toks = _tokens(pursuits)
        _ti = TIER_IDX.get(tier_str, -1)
        cav = [w for w in ("Cavalry Spear", "Lance")
               if "weapon:" + w in toks and _ti >= TIER_IDX[WEAPONS[w]["tier"]]]
        has_fletch = "ranged" in toks
        has_ty = "dual-equip" in toks
        has_dw = rd.FLORENTINE in toks
        melee = WEAPONS_BY_TIER[tier_str]
        arms_options = []
        if cav and has_ty:                              # cavalry is melee-only (charge weapons)
            arms_options += [(c, None, False) for c in cav]
            arms_options += [(w, r, True) for w in melee for r in _ranged_at_or_below(tier_str, RANGED_BY_TIER)]
        elif cav:
            arms_options += [(c, None, False) for c in cav] + [(w, None, False) for w in melee]
        elif has_fletch and has_ty:
            arms_options += [(w, r, True) for w in melee for r in _ranged_at_or_below(tier_str, RANGED_BY_TIER)]
        elif has_fletch:
            arms_options += [(None, r, False) for r in _ranged_at_or_below(tier_str, RANGED_BY_TIER)]
        else:
            arms_options += [(w, None, False) for w in melee]
        # Tiltyard two-of-same: a doubled 1H melee weapon gains Dual Wield (no ranged, no shield).
        dual_wield_weapons = set()
        if has_dw:
            for w in melee:
                if w in ("Farm Tools", "Bastard Sword") or is_2h(w) or w in STABLE_WEAPONS:   # Bastard Sword (1H) always carries a shield
                    continue
                arms_options.append((w, None, True))
                dual_wield_weapons.add(w)
        for weapon, ranged, ty in arms_options:
            is_two_of_same = (weapon in dual_wield_weapons and ranged is None and ty)
            SHIELD_LADDER = ["Heater Shield", "Tower Shield", "Kite Shield",
                             "Targe Shield", "Buckler Shield"]
            if weapon is None or is_2h(weapon) or is_two_of_same:
                shield_opts = [None]
            else:
                w_init = WEAPONS.get(weapon, {}).get("init", 0) if weapon != "Farm Tools" else 0
                best_shield = None
                for s in SHIELD_LADDER:
                    if shield_satisfied(s, pursuits) and w_init + SHIELDS[s]["init"] >= -1:
                        best_shield = s
                        break
                shield_opts = [best_shield] if best_shield else [None]
            ARMOR_LADDER = ["Gothic Plate", "Full Plate", "Chainmail", "Leather", "Gambeson", "Cloth"]
            armor_opts = [next((a for a in ARMOR_LADDER if a in ARMORS and armor_satisfied(a, pursuits)),
                               "Cloth")]
            for shield in shield_opts:
                for armor in armor_opts:
                    if not is_two_of_same and not valid_combo(
                            retinue_guess, weapon or "Farm Tools", shield, armor, ranged, ty):
                        continue
                    if shield is not None and not shield_satisfied(shield, pursuits):
                        continue
                    if not armor_satisfied(armor, pursuits) or not ranged_satisfied(ranged, pursuits):
                        continue
                    domain_count = sum(domain.values())
                    if domain_count > 30:
                        continue
                    build_tags = set(tags)
                    if is_two_of_same:
                        build_tags.add(DUAL_WIELD)
                    tags_tuple = tuple(sorted(build_tags))
                    obs_key = (retinue_guess, weapon, shield, armor, ranged, ty, tags_tuple)
                    if obs_key in seen_keys and seen_keys[obs_key][0] <= total_cost:
                        continue
                    name = _name(retinue_guess, weapon, shield, armor, ranged, ty,
                                 sorted(build_tags), playstyle=None, pursuits=pursuits)
                    ld = Loadout(
                        name=name,
                        retinue=retinue_guess, weapon=weapon, shield=shield, armor=armor,
                        ranged=ranged, has_tiltyard=ty, size=DEFAULT_ARMY_SIZE,
                        extra_tags=sorted(build_tags),
                        upkeep_per_retinue=0,
                        playstyle=None,
                        tiltyard_mastery=True,
                        pursuits=frozenset(pursuits),
                        military_pursuit_count=total_cost,
                        domain_count=domain_count,
                    )
                    ld = ld._replace(upkeep_per_retinue=compute_effective_upkeep(ld))
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
def _structural_legal(weapon, shield, armor, ranged, has_tiltyard):
    """ONLY the structural weapon rules — no tier floors/caps, no shield-tier>=weapon-tier.
    These are the rules Gage specified for pool generation:
      - 2H melee cannot use a shield.
      - 1H melee (except Farm Tools) requires a shield.
      - Bastard Sword (1H profile) must carry a shield.
      - Lance / Cavalry Spear cannot use Tower Shield (Wooden is allowed).
      - Stable cavalry weapons (Lance, Cavalry Spear) cannot dual-equip a ranged weapon.
      - One-Shot ranged (Javelin, Crossbow) requires Tiltyard.
      - Dual-equip (real melee + ranged) requires Tiltyard.
    """
    if is_2h(weapon) and shield is not None:
        return False
    # Stable cavalry weapons cannot dual-equip a ranged weapon (charge weapons).
    if weapon in STABLE_WEAPONS and ranged is not None:
        return False
    if weapon in ("Lance", "Cavalry Spear") and shield == "Tower Shield":
        return False
    if weapon == "Bastard Sword" and shield is None:
        return False
    if (weapon != "Farm Tools" and not is_2h(weapon) and shield is None):
        return False
    if ranged is not None and ONE_SHOT in RANGED[ranged].get("tags", []) and not has_tiltyard:
        return False
    if weapon != "Farm Tools" and ranged is not None and not has_tiltyard:
        return False
    return True
def balanced_validation_pool(mpc_min=4, mpc_max=13, per_cell=None, seed=2026,
                             keep_shield_tier_rule=False, verbose=False):
    """Large validation pool, balanced per (retinue x MPC), spanning ALL gear tiers and the full legal
    weapon/armor/shield cross. Gear first: each gear config's Holdings are the ones whose text unlocks
    it (gear_seed), closed over their Mastery Chain lines; then a Retinue unlock, <=1 upgrade, and
    filler pad the build to each target MPC. Every rule is read from HOLDING_SIM (SIMPLE_NODES text).
    Args:
      per_cell: target builds per (retinue, MPC) cell. None = keep all legal; an int caps each cell.
      keep_shield_tier_rule: legacy comparison only (shield tier >= weapon tier).
    """
    import random as _random
    from collections import defaultdict
    rng = _random.Random(seed)
    RETS = list(RETINUES)[1:]                                    # every unlockable Retinue
    RETINUE_UNLOCK = {r: _holders("retinue:" + r)[:1] for r in RETS}
    UPGRADES = [u for u in ("Conditioning Field", "Royal Pavilion", "Ministry of Military Strategy",
                            "Outrider Intercept Post", "Grand Tournament") if u in _SIM]
    FILLER = [f for f in ("Master Workshop", "Toxicarium", "Stable", "Butchery", "Smokehouse") if f in _SIM]
    REGEN_LADDER = [r for r in ("Apothecary", "Infirmary", "Hospitaller") if r in _SIM]
    armor_for_tier = {}
    for a, d in ARMORS.items():
        if d["tier"]:
            armor_for_tier.setdefault(d["tier"], a)
    shield_tiers = {}
    for s_, d in SHIELDS.items():
        if s_ and d["tier"]:
            shield_tiers.setdefault(d["tier"], s_)
    all_shields = [None] + [shield_tiers[t] for t in TIER_ORDER if t in shield_tiers]
    gear_configs = []
    for weapon in WEAPONS:                                        # melee (+ optional shield)
        for armor_tier in TIER_ORDER:
            armor = armor_for_tier.get(armor_tier)
            if not armor:
                continue
            for shield in all_shields:
                if not _structural_legal(weapon, shield, armor, None, has_tiltyard=False):
                    continue
                if keep_shield_tier_rule and shield is not None and not is_2h(weapon) \
                   and weapon not in ("Lance", "Cavalry Spear", "Farm Tools"):
                    if TIER_IDX.get(SHIELDS[shield]["tier"], 0) < TIER_IDX.get(WEAPONS[weapon]["tier"], 0):
                        continue
                gear_configs.append((weapon, shield, armor, None, False))
    for weapon in WEAPONS:                                        # Tiltyard two-of-same Dual Wield
        if weapon in ("Farm Tools", "Bastard Sword") or is_2h(weapon) or weapon in STABLE_WEAPONS:
            continue
        for armor_tier in TIER_ORDER:
            if armor_for_tier.get(armor_tier):
                gear_configs.append((weapon, None, armor_for_tier[armor_tier], None, True))
    for ranged in RANGED:                                         # pure-ranged + dual-equip
        for armor_tier in TIER_ORDER:
            armor = armor_for_tier.get(armor_tier)
            if not armor:
                continue
            if _structural_legal("Farm Tools", None, armor, ranged, has_tiltyard=True):
                gear_configs.append(("Farm Tools", None, armor, ranged, False))
            for weapon in WEAPONS:
                if weapon == "Farm Tools":
                    continue
                for shield in all_shields:
                    if _structural_legal(weapon, shield, armor, ranged, has_tiltyard=True):
                        gear_configs.append((weapon, shield, armor, ranged, False))
    if verbose:
        print(f"gear configs: {len(gear_configs)}")
    cells = defaultdict(list)
    for weapon, shield, armor, ranged, is_dw in gear_configs:
        gear_base = gear_seed(weapon, shield, armor, ranged, is_dw)
        if None in gear_base:
            continue
        has_ty = "dual-equip" in gear_requirements(weapon, shield, armor, ranged, is_dw) or is_dw
        for ret in RETS:
            for _u_try in range(3):
                upgrade = "Conditioning Field" if rng.random() < 2/3 else rng.choice(
                    [u for u in UPGRADES if u != "Conditioning Field"] or ["Conditioning Field"])
                base_set = prereq_closure(gear_base | set(RETINUE_UNLOCK[ret]) | {upgrade})
                base_cost, _, _ = compute_pursuit_cost(base_set)
                for target_mpc in range(mpc_min, mpc_max + 1):
                    if base_cost > target_mpc:
                        continue
                    regen_avail = [r for r in REGEN_LADDER if r not in base_set]
                    other_filler = [f for f in FILLER if f not in base_set]
                    rng.shuffle(other_filler)
                    chosen, cur_cost = [], base_cost
                    for f in regen_avail + other_filler:
                        if cur_cost >= target_mpc:
                            break
                        tc, _, _ = compute_pursuit_cost(prereq_closure(base_set | set(chosen + [f])))
                        if tc > target_mpc:
                            continue
                        chosen.append(f)
                        cur_cost = tc
                    pursuit_set = prereq_closure(base_set | set(chosen))
                    cost, domain, tags = compute_pursuit_cost(pursuit_set)
                    if cost != target_mpc:
                        continue
                    if sum(1 for m in _POOL_MONUMENTS if m in pursuit_set) > 2:
                        continue
                    if derive_retinue_from_pursuits(pursuit_set) != ret:
                        continue                                  # an upgrade line unlocked a stronger Retinue
                    tags = set(tags)
                    if is_dw:
                        tags.add(DUAL_WIELD)
                    name = _name(ret, weapon, shield, armor, ranged, has_ty, sorted(tags), pursuits=pursuit_set)
                    ld = Loadout(
                        name=name + f"|M{target_mpc}",
                        retinue=ret, weapon=weapon, shield=shield, armor=armor, ranged=ranged,
                        has_tiltyard=has_ty, size=DEFAULT_ARMY_SIZE,
                        extra_tags=frozenset(tags), upkeep_per_retinue=0,
                        playstyle=None, tiltyard_mastery=True, pursuits=frozenset(pursuit_set),
                        military_pursuit_count=target_mpc, domain_count=int(sum(domain.values())),
                    )
                    ld = ld._replace(upkeep_per_retinue=compute_effective_upkeep(ld))
                    cells[(ret, target_mpc)].append(ld)
    out = []
    for key, builds in cells.items():
        uniq = {}
        for b in builds:
            uniq[(b.weapon, b.shield, b.armor, b.ranged, b.has_tiltyard,
                  b.military_pursuit_count, tuple(sorted(b.extra_tags)))] = b
        builds = list(uniq.values())
        if per_cell and len(builds) > per_cell:
            builds = rng.sample(builds, per_cell)
        out.extend(builds)
    if verbose:
        from collections import Counter as _C
        print(f"total builds: {len(out)}")
        print("per retinue:", dict(_C(b.retinue for b in out)))
        print("per MPC:", dict(sorted(_C(b.military_pursuit_count for b in out).items())))
    return out


def validate_loadout(ld, check_tier_floors=False):
    """Check ONE loadout against the rules. Returns violation strings (empty = valid).
      STRUCTURAL: 2H/1H shield rules, Bastard Sword, cavalry vs Tower / ranged,
                  One-Shot and dual-equip need the Tiltyard.
      UNLOCKS:    every unlock token the gear needs (gear_requirements) is granted by a Holding's
                  text in the build; RANGED 'requires' Holdings are present.
      LINES:      every Holding has one complete Mastery Chain line inside the build.
      EFFICIENCY: no Tiltyard without a ranged weapon or Dual Wield, unless another Holding's line
                  runs through it.
    (check_tier_floors is a no-op, kept for API compatibility.)"""
    v = []
    P = set(ld.pursuits)
    w, sh, ar, rg = ld.weapon, ld.shield, ld.armor, ld.ranged
    _is_dw_build = (DUAL_WIELD in set(ld.extra_tags or []) and w is not None
                    and DUAL_WIELD not in WEAPONS.get(w, {}).get("tags", []))
    if w is not None and is_2h(w) and sh is not None:
        v.append(f"2H weapon {w} has shield {sh}")
    if (w not in (None, "Farm Tools") and not is_2h(w) and sh is None
            and not _is_dw_build):
        v.append(f"1H weapon {w} has no shield")
    if w == "Bastard Sword" and sh is None:
        v.append("Bastard Sword (1H) has no shield")
    if w in STABLE_WEAPONS and sh == "Tower Shield":
        v.append(f"{w} cannot use Tower Shield")
    if w in STABLE_WEAPONS and rg is not None:
        v.append(f"Stable cavalry weapon {w} cannot dual-equip ranged {rg}")
    if rg is not None and ONE_SHOT in RANGED.get(rg, {}).get("tags", []) and not ld.has_tiltyard:
        v.append(f"One-Shot ranged {rg} without Tiltyard")
    if w not in (None, "Farm Tools") and rg is not None and not ld.has_tiltyard:
        v.append(f"dual-equip ({w}+{rg}) without Tiltyard")
    toks = _tokens(P)
    for t in sorted(gear_requirements(w if w in WEAPONS else None, sh, ar, rg, _is_dw_build)):
        if t not in toks:
            v.append(f"gear needs '{t}' — no Holding in the build grants it")
    if rg is not None:
        for req in RANGED.get(rg, {}).get("requires", []):
            if req not in P:
                v.append(f"ranged {rg} requires {req}")
    for p in sorted(P):
        if p in _SIM and not _line_ok(p, P):
            v.append(f"Holding {p} has no complete Mastery Chain line")
    # (Joinery / Fletchery carry 'Upkeep -N' in their text, so they're never idle.)
    if ld.has_tiltyard and rg is None and not _is_dw_build and not _needed_by_line("Tiltyard", P):
        v.append("Tiltyard without a ranged weapon")
    return v


def validate_pool(pool, check_tier_floors=False, max_report=20, verbose=True):
    """Run validate_loadout over a whole pool. Returns {build_name: [violations]} for invalid builds.
    Prints a summary + a sample of violations. Use after generating a pool to catch construction bugs.
    """
    bad = {}
    counts = {}
    for ld in pool:
        vio = validate_loadout(ld, check_tier_floors=check_tier_floors)
        if vio:
            bad[ld.name] = vio
            for msg in vio:
                key = msg.split(" ")[0] + " " + (msg.split(" missing ")[0].split()[-1] if "missing" in msg else "")
                # bucket by a coarse signature for the summary
                sig = msg
                for tok in (ld.weapon or "", ld.shield or "", ld.armor or "", ld.ranged or ""):
                    if tok:
                        sig = sig.replace(tok, "<g>")
                counts[sig] = counts.get(sig, 0) + 1
    if verbose:
        print(f"validate_pool: {len(pool)} builds, {len(bad)} invalid ({100*len(bad)/max(1,len(pool)):.1f}%)")
        if counts:
            print("violation types (coarse):")
            for sig, n in sorted(counts.items(), key=lambda kv: -kv[1])[:max_report]:
                print(f"  {n:6d}  {sig}")
        else:
            print("  ALL VALID ✓")
    return bad
def with_playstyle(loadout, playstyle):
    """Return a copy of `loadout` with a different playstyle (and updated name).
    Useful for one-off comparisons."""
    new_name = _name(loadout.retinue, loadout.weapon, loadout.shield, loadout.armor,
                     loadout.ranged, loadout.has_tiltyard, loadout.extra_tags,
                     playstyle=playstyle, pursuits=loadout.pursuits)
    return loadout._replace(name=new_name, playstyle=playstyle)
def kt_twins(pool):
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
        natural_ps = assign_default_playstyle(spoof)
        # If somehow the natural playstyle is still Unshakable (shouldn't happen with
        # current rules, but be defensive), skip — no useful twin to create.
        if natural_ps == "Unshakable":
            continue
        new_name = _name(ld.retinue, ld.weapon, ld.shield, ld.armor,
                         ld.ranged, ld.has_tiltyard, ld.extra_tags,
                         playstyle=natural_ps, pursuits=ld.pursuits) + " (NaturalPS)"
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
def optimal_playstyle_pool(base_pool):
    """For each loadout in `base_pool`, assign its heuristic optimal playstyle.
    Returns a new pool the same size, each loadout tagged with one chosen style.
    """
    from playstyles import assign_default_playstyle
    return [with_playstyle(ld, assign_default_playstyle(ld)) for ld in base_pool]
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