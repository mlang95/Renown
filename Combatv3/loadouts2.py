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
  Defensive:          Regenerate, Regenerate 5, Regenerate 4, Regenerate Reroll (engine-supported, no longer granted by any spec)
  Immunities:         Immune Unwieldy, Immune Poison
  Spec effects:       Rend (worsens enemy Regenerate), GF Armor (incoming AP -1), Cond Field (+1 Endurance)
  Faction flag:       Yew Heart (ranged +1 to Hit)
"""
from collections import namedtuple
from renown_data import RETINUES, WEAPONS, RANGED, SHIELDS, ARMORS
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
    "Recover 6":         "Rec 6",
    "Recover 5":         "Rec 5",
    "Recover 4":         "Rec 4",
    "Serrated":          "Serr",
    "Planishing":        "Temp",   # internal tag key stays "Planishing"; display abbrev = Tempered
    "Crit 5":            "Crit5",
    "+1I":               "+1I",
    "Immune Panic":      "ImmPanic",
    "Immune Unwieldy":   "ImmU",
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
    "Dual Wield":        "DW",
}
def _w_label(w):
    return WEAPON_LABEL.get(w, w)
# Monument abbreviations for the name bracket: first two letters of each word (skipping "of"),
# ABF keeps its established acronym. Duplicates would be extended by one letter (none currently).
# Suffix: M = mastered, I = innate-only (present but mastery_req not satisfied).
_MON_ABBR = {
    "Royal Pavilion": "RoPa",
    "ABF": "ABF",
    "Preceptory": "Pr",
    "Ministry of Military Strategy": "MiMiSt",
    "Outrider Intercept Post": "OuInPo",
}
# Tags absorbed into the domain-standing tuple (they ARE the standing's grant):
_DOMAIN_TAGS = {"Immune Blocked", "Parry", "confers:Blocked", "confers:Strain"}
def _standing_letter(v):
    return "S" if v >= 10 else ("E" if v >= 6 else ("R" if v >= 3 else "N"))
def _name(retinue, weapon, shield, armor, ranged, has_tiltyard, extra_tags, playstyle=None,
          pursuits=None, domain=None):
    """Build a human-readable name for a loadout.
    Format: RET/WEAPON[+RANGED]/SHIELD/ARMOR (TY) [bracket] <playstyle>
    - Pure-ranged (no real melee weapon — None or the Farm Tools placeholder): the ranged weapon is
      shown AS the weapon (Lev/Longbow/Leather). (TY) only appears when actually dual-equipping.
    - If `pursuits` is given, the bracket is: monument markers first (RoPaM/RoPaI, ABFM, ...), then
      the 4-domain standing tuple (xInd, xProw, xPie, xCun) with x in {N,R,E,S}, then remaining tags.
      Monument-granted tags and domain-standing tags (Immune Blocked/Parry/confers:*) are absorbed
      into the marker/tuple. Without `pursuits`, the legacy flat-tag bracket is used.
    - `domain` (optional): the precomputed domain dict for `pursuits`. If supplied, the standing
      tuple uses it directly instead of recomputing compute_pursuit_cost(P). Output is identical.
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
          and "Dual Wield" in (extra_tags or [])
          and "Dual Wield" not in WEAPONS.get(weapon, {}).get("tags", [])):
        # Tiltyard two-of-same: a non-intrinsic-DW 1H weapon doubled to gain Dual Wield.
        # (Daggers carry DW intrinsically and are excluded by the weapon-tag check.)
        base += " (DW)"
    tags = list(extra_tags) if extra_tags else []
    # Display only the strongest Regenerate tier (engine takes min threshold; dominated tags are noise)
    _regen_rank = {"Regenerate 4": 4, "Regenerate 5": 5, "Regenerate 6": 6, "Regenerate": 6,
                   "Recover 4": 4, "Recover 5": 5, "Recover 6": 6, "Recover": 6}
    _regen_present = [t for t in tags if t in _regen_rank]
    if len(_regen_present) > 1:
        best = min(_regen_present, key=lambda t: _regen_rank[t])
        tags = [t for t in tags if t not in _regen_rank or t == best]
    bracket_items = []
    if pursuits:
        P = set(pursuits)
        hidden = set(_DOMAIN_TAGS)
        # monument markers (first in the bracket), absorbing their granted tags
        for mon in ["Royal Pavilion", "ABF", "Preceptory", "Ministry of Military Strategy",
                    "Outrider Intercept Post"]:
            if mon not in P:
                continue
            info = PURSUITS_INFO[mon]
            mastered = all(r in P for r in info.get("mastery_req", []))
            bracket_items.append(_MON_ABBR[mon] + ("M" if mastered else "I"))
            hidden.update(t for t in info.get("innate_tags", []) if not t.startswith("tier:"))
            if mastered:
                hidden.update(t for t in info.get("mastery_tags", []) if not t.startswith("tier:"))
        # 4-domain standing tuple (use precomputed domain if given; identical otherwise)
        if domain is None:
            _, dom, _ = compute_pursuit_cost(P)
        else:
            dom = domain
        bracket_items.append("({}Ind, {}Prow, {}Pie, {}Cun)".format(
            _standing_letter(dom.get("Industry", 0)), _standing_letter(dom.get("Prowess", 0)),
            _standing_letter(dom.get("Piety", 0)), _standing_letter(dom.get("Cunning", 0))))
        if "Riposte" in tags:
            hidden.add("Improved Parry")
        bracket_items += [TAG_DISPLAY.get(t, t) for t in tags if t not in hidden]
    elif tags:
        # legacy flat bracket (no pursuit info available)
        _display = [t for t in tags
                    if not (t in ("Parry", "Improved Parry") and "Riposte" in tags)]
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
    return ("2H" in tags) or ("Dual Wield" in tags)
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
    - "One Shot" ranged (Javelin, Pilum) requires Tiltyard.
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
            and not is_2h(weapon)
            and shield is None
            and ranged != "Crossbow"):
        return False
    # 1H + shield: shield tier must be >= weapon tier
    # Exception: Lance is exempt from the tier rule (only the explicit forbidden-shield
    # list above applies). Lance can use Kite, Scutum, or Heater regardless of weapon tier.
    if shield is not None and not is_2h(weapon) and weapon != "Farm Tools" and weapon not in ("Lance", "Cavalry Spear"):
        weapon_tier_idx = TIER_IDX.get(WEAPONS[weapon]["tier"], 0)
        shield_tier_idx = TIER_IDX.get(SHIELDS[shield]["tier"], 0)
        if shield_tier_idx < weapon_tier_idx:
            return False
    # "One Shot" ranged weapons (Javelin, Pilum) require Tiltyard.
    if ranged is not None and "One Shot" in RANGED[ranged].get("tags", []):
        if not has_tiltyard:
            return False
    # Dual-equip requires Tiltyard. Real melee + ranged without Tiltyard is invalid.
    has_real_melee = weapon != "Farm Tools"
    if has_real_melee and ranged is not None and not has_tiltyard:
        return False
    retinue_idx = RETINUE_TIER[retinue]
    armor_tier_idx = TIER_IDX[ARMORS[armor]["tier"]]
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
    "Drilled":              ("Drilled",),
    "Nimble":               ("Nimble",),
    "Steady":               ("Steady",),
    "Steadfast":            ("Immune Panic",),                  # Preceptory innate / Undying Flame (legacy preset name)
    "Parry":                ("Parry",),                         # Edict of War (Sovereign Prowess)
    "Cond Field":           ("Cond Field",),                    # Conditioning Field mastery
    "Rend":           ("Serrated",),               # Master Workshop mastery
    "GF Armor":             ("Planishing",),                    # Gilded Foundry mastery
    "Immune Poison":        (),                                 # Apothecary no longer grants Immune Poison (disabled)
    "Apothecary Heal":      ("Apothecary Heal",),               # Apothecary mastery: Heal 1 per 4 cas (Immune Poison removed)
    "Poison":               ("Poison",),                        # Toxicarium innate
    "Immune Unwieldy":      ("Immune Unwieldy",),               # Tiltyard mastery
    # — Regenerate ladder —
    "Regen 6+":             ("Recover 6",),
    "Regen 5+":             ("Recover 5",),
    "Regen 4+":             ("Recover 4",),
    # Hospitaller no longer grants a Recover reroll (now +1/+1); reroll tags are
    # engine-ignored — these presets behave as plain Recover tiers.
    "Regen 6+ Reroll":      ("Recover 6",),
    "Regen 5+ Reroll":      ("Recover 5",),
    "Regen 4+ Reroll":      ("Recover 4",),
    # — Spec combinations (multi-spec pathways) —
    "Royal Pavilion":       ("Drilled", "Nimble"),                                    # RP mastery
    "Preceptory":           ("Immune Panic",),                                        # Preceptory innate
    "Pre + RP":             ("Drilled", "Nimble", "Immune Panic"),
    "Pre + RP + Parry":     ("Drilled", "Nimble", "Immune Panic", "Parry"),
    "RP + Conditioned":     ("Drilled", "Nimble", "Cond Field"),
    "Pre + RP + Cond":      ("Drilled", "Nimble", "Immune Panic", "Cond Field"),
    "MW + GF":              ("Serrated", "Planishing"),
    "Industry Elite":       ("Serrated", "Planishing", "Cond Field"),
    "Apo + Tox":            ("Poison",),
    "Apo + Inf":            ("Recover 6",),
    "Apo + Inf + Hosp":     ("Recover 5",),
    "Apo + Inf + Hosp(M)":  ("Recover 4",),
    # — Faction effects —
    "Pale Throne":          ("Unwieldy", "Recover 6", "Immune Panic"),                # mandatory faction tags
    "Pale Throne + Inf":    ("Unwieldy", "Recover 5", "Immune Panic"),
    "Pale Throne max":      ("Unwieldy", "Recover 4", "Immune Panic"),                # +Inf+Hosp innate
    "Pale Throne max + HM": ("Unwieldy", "Recover 4", "Immune Panic"),                # Hosp mastery: 4+ floor — no gain for PT
    "Pale Throne + MWGF":   ("Unwieldy", "Recover 6", "Immune Panic", "Serrated", "Planishing"),
    "Elder Grove":          ("Nimble", "Steady"),                                     # requires PO 1+
    "Elder Grove + RP":     ("Nimble", "Steady", "Drilled"),
    "Undying Flame":        ("Immune Panic",),                                        # same as Preceptory in-engine
    "Ashen Vale":           ("Poison",),                                              # all retinues poison
    "Yew Heart":            ("Yew Heart",),                                           # ranged +1 to hit
    "Yew Heart TY":         ("Yew Heart", "Immune Unwieldy"),                         # +Tiltyard mastery
    "Blazing Standard":     ("Immune Panic",),                                        # free Preceptory mastery
    # — Ministry of Strategy (Sovereign Prowess monument) —
    # Reveal opponent's tactic before picking yours. Counter-pick with 80% confidence.
    # Three variants test different firing frequencies.
    "Outrider: every":      ("Outrider: every",),                                     # every skirmish (legacy/analysis)
    "Outrider: first":      ("Outrider: first",),                                     # first skirmish only
    "Outrider: once":       ("Outrider: once",),                                      # once per battle (modeled as first)
    # — Endgame meta stack —
    "Crusader King":        ("Drilled", "Nimble", "Steadfast", "Parry", "Rend", "GF Armor", "Cond Field"),
}
# ==============================================================================
# Pursuit cost system — Military Pursuit Count & Domain Count
# ==============================================================================
def _pursuits_info_from_renown_data():
    """Build the sim's pursuit table from renown_data.NODES 'engine' fields."""
    from renown_data import NODES
    out = {}
    for node_name, node in NODES.items():
        eng = node.get("engine")
        if not eng:
            continue
        key = eng.get("alias", node_name)
        out[key] = {k: v for k, v in eng.items() if k != "alias"}
    from renown_data import EFFICIENT, NODES as _N
    def _alias(name):
        return _N.get(name, {}).get("engine", {}).get("alias", name)
    for src, tgt in EFFICIENT.items():
        k = _alias(src)
        if k in out:
            out[k]["efficient"] = _alias(tgt)
    return out
PURSUITS_INFO = _pursuits_info_from_renown_data()
TIER_INDUSTRY_REQ = {"Crude": 0, "Cast": 0, "Wrought": 3, "Forged": 6, "Crafted": 10}
TIER_PURSUIT_TO_TIER = {None: "Crude", "Furnace": "Cast", "Blacksmith": "Wrought",
                        "Forge": "Forged", "ABF": "Crafted"}
def _gear_tier_idx(loadout_weapon, loadout_shield, loadout_armor, loadout_ranged):
    max_idx = 0
    if loadout_weapon and loadout_weapon != "Farm Tools":
        max_idx = max(max_idx, TIER_IDX.get(WEAPONS[loadout_weapon]["tier"], 0))
    if loadout_armor:
        max_idx = max(max_idx, TIER_IDX.get(ARMORS[loadout_armor]["tier"], 0))
    if loadout_shield:
        max_idx = max(max_idx, TIER_IDX.get(SHIELDS[loadout_shield]["tier"], 0))
    if loadout_ranged:
        max_idx = max(max_idx, TIER_IDX.get(RANGED[loadout_ranged].get("tier", "Crude"), 0))
    return max_idx
def derive_retinue_from_pursuits(pursuits):
    precep_mastery = set(PURSUITS_INFO["Preceptory"]["mastery_req"])
    has_full_precep = ("Preceptory" in pursuits and "Preceptory KT" in pursuits
                       and precep_mastery <= set(pursuits))
    if has_full_precep:
        return "Knight Templar"
    if "War College" in pursuits:
        return "Sergeant"
    if "Coliseum" in pursuits:
        return "Man-at-Arms"
    return "Levy"
def derive_tier_from_pursuits(pursuits):
    if "ABF" in pursuits:
        return "Crafted"
    if "Forge" in pursuits:
        return "Forged"
    if "Blacksmith" in pursuits:
        return "Wrought"
    if "Furnace" in pursuits:
        return "Cast"
    return "Crude"
ARMOR_REQUIRES = {
    "Cloth":        set(),
    "Leather":      {"Tannery", "Armory", "Gilded Foundry", "ABF"},
    "Chainmail":    {"Armory", "Gilded Foundry", "ABF"},
    "Full Plate":   {"Gilded Foundry", "ABF"},
    "Gothic Plate": {"ABF"},
}
SHIELD_METAL_REQUIRES = {
    "Wooden Shield":  set(),
    "Kite Shield":    {"Tannery", "Armory", "Gilded Foundry", "ABF"},
    "Scutum Shield":  {"Armory", "Gilded Foundry", "ABF"},
    "Tower Shield":   {"Gilded Foundry", "ABF"},
    "Heater Shield":  {"ABF"},
}
def armor_satisfied(armor_name, pursuits):
    required = ARMOR_REQUIRES.get(armor_name, set())
    if not required:
        return True
    return bool(required & pursuits)
def shield_satisfied(shield_name, pursuits):
    if "Joinery" not in pursuits:
        return False
    required_metal = SHIELD_METAL_REQUIRES.get(shield_name, set())
    if not required_metal:
        return True
    return bool(required_metal & pursuits)
import renown_data as rd
_POOL_MONUMENTS = frozenset(
    (rd.NODES[n].get("engine", {}).get("alias", n))
    for n, v in rd.NODES.items()
    if (v.get("type") == "Monument" or v.get("monument"))
) | {"Ministry of Military Strategy"}
def _normalize_pool_tokens(pursuits):
    p = set(pursuits)
    if "Ministry" in p or "Ministry Mastery" in p:
        p.discard("Ministry")
        if "Ministry Mastery" in p:
            p.discard("Ministry Mastery")
            p.add("University")
        p.add("Ministry of Military Strategy")
    return p
def compute_pursuit_cost(pursuits):
    P = set(pursuits)
    known = [p for p in P if p in PURSUITS_INFO]
    def mastered(p):
        mreq = PURSUITS_INFO[p].get("mastery_req", [])
        return all(r in P for r in mreq)
    discounted = set()
    for p in known:
        tgt = PURSUITS_INFO[p].get("efficient")
        if tgt and mastered(p) and tgt in P and tgt in PURSUITS_INFO:
            discounted.add(tgt)
    mpc = len(known) - len(discounted)
    domain = {"Industry": 0, "Prowess": 0, "Piety": 0, "Cunning": 0}
    for p in known:
        for d, v in PURSUITS_INFO[p].get("domain", {}).items():
            domain[d] = max(domain[d], v)
    tier_str = derive_tier_from_pursuits(pursuits)
    domain["Industry"] = max(domain["Industry"], TIER_INDUSTRY_REQ[tier_str])
    tags = set()
    for p in known:
        info = PURSUITS_INFO[p]
        tags.update(info.get("innate_tags", []))
        if mastered(p):
            tags.update(info.get("mastery_tags", []))
    if "Outrider: every" in tags:
        tags.discard("Outrider: once")
    tags = {t for t in tags if not t.startswith("tier:")}
    if domain["Prowess"] >= 3:
        tags.add("Immune Blocked")
    if domain["Prowess"] >= 6:
        tags.add("Parry")
    if domain["Piety"] >= 6:
        tags.add("Shake +1")
    if domain["Cunning"] >= 6:
        tags.add("confers:Blocked")
    if domain["Cunning"] >= 10:
        tags.add("confers:Strain")
    return mpc, domain, tags
def compute_effective_upkeep(loadout):
    base = RETINUES[loadout.retinue]["cost"]
    reduction = 0
    has_shield = loadout.shield is not None
    has_ranged = loadout.ranged is not None
    for p in loadout.pursuits:
        effects = PURSUITS_INFO.get(p, {}).get("upkeep_effects", [])
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
    if "Levy Hall" in loadout.pursuits and "Butchery" in loadout.pursuits:
        reduction += 300
    return max(200, base - reduction)
def _pursuit_set_is_valid(pursuits):
    has_forge_or_abf = ("Forge" in pursuits) or ("ABF" in pursuits)
    has_animal_husbandry = ("Animal Husbandry" in pursuits) or ("Stable" in pursuits)
    if "ABF" in pursuits:
        if not (("Master Workshop" in pursuits) or ("MWRend" in pursuits)):
            return False
        if "Stable" not in pursuits or "Gilded Foundry" not in pursuits:
            return False
    if "Outrider Intercept Post" in pursuits:
        if not ({"Caravanery", "Cipher Chamber"} <= pursuits):
            return False
    if "Outrider Mastery" in pursuits and "Outrider Intercept Post" not in pursuits:
        return False
    if ("Caravanery" in pursuits or "Cipher Chamber" in pursuits) and "Outrider Intercept Post" not in pursuits:
        return False
    if "Ministry of Military Strategy" in pursuits and "War College" not in pursuits:
        return False
    if "Joinery" in pursuits and "Carpentry" not in pursuits:
        return False
    if "Fletchery" in pursuits and "Carpentry" not in pursuits:
        return False
    if "Tiltyard" in pursuits and not ({"Fletchery", "Coliseum"} <= pursuits):
        return False
    if "Royal Pavilion" in pursuits and "Tiltyard" not in pursuits and "Grand Tournament" not in pursuits:
        return False
    if "Tannery" in pursuits and not has_animal_husbandry:
        return False
    if "Butchery" in pursuits and (not has_animal_husbandry or "Tannery" not in pursuits):
        return False
    if "Smokehouse" in pursuits and "Butchery" not in pursuits:
        return False
    has_blacksmith_tier = ("Blacksmith" in pursuits) or has_forge_or_abf
    if "Armory" in pursuits and ("Tannery" not in pursuits or not has_blacksmith_tier):
        return False
    if "Master Workshop" in pursuits and "Blacksmith" not in pursuits:
        return False
    if "Gilded Foundry" in pursuits and "Armory" not in pursuits:
        return False
    if "Preceptory KT" in pursuits and not (
            {"Preceptory"} | set(PURSUITS_INFO["Preceptory"]["mastery_req"]) <= set(pursuits)):
        return False
    if "Stable" in pursuits and not has_forge_or_abf:
        return False
    return True
def _load_loadouts_from_csv(csv_path):
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
            size = DEFAULT_ARMY_SIZE
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
# ── PERF: module-level constants hoisted out of archetype_pool's hot loop ──
_WEAPONS_BY_TIER = {
    "Crude":   ["Cudgel", "Farm Tools"],
    "Cast":    ["Daggers", "Short Sword", "Spears"],
    "Wrought": ["Arming Sword", "Pike", "Flail", "Halberd", "Battle Axe"],
    "Forged":  ["Bastard Sword", "2HBastard", "Morningstar", "War Hammer"],
    "Crafted": ["Poleaxe", "Estoc"],
}
_RANGED_BY_TIER = {
    "Crude":   ["Hunting Bow"],
    "Cast":    ["Longbow"],
    "Wrought": ["Javelin"],
    "Forged":  ["Crossbow"],
    "Crafted": ["Pilum"],
}
_CRAFTED_1H_FALLBACK = ["Bastard Sword", "Morningstar"]
_SHIELD_LADDER = ["Heater Shield", "Tower Shield", "Scutum Shield", "Kite Shield", "Wooden Shield"]
_ARMOR_LADDER = ["Gothic Plate", "Full Plate", "Chainmail", "Leather", "Cloth"]
def _melee_options_for_tier(t):
    """Melee weapons available at gear tier t (Crafted adds Forged-1H fallbacks). Output identical
    to the former nested def; hoisted to module level so it isn't rebuilt per mask iteration."""
    if t == "Crafted":
        return _WEAPONS_BY_TIER["Crafted"] + _CRAFTED_1H_FALLBACK
    return _WEAPONS_BY_TIER[t]
def archetype_pool(min_pursuit_cost=5, max_pursuit_cost=10, csv_path=None, budget_metric="mpc", max_monuments=2,
                   _independent_options=None):
    """Enumerate loadouts. CSV mode loads a frozen pool; generator mode derives builds from
    pursuit-set enumeration. (Behavior unchanged; this revision only adds output-preserving
    performance work: hoisted constants, a precomputed prereq-closure table, and a memo cache
    on the closure+validity+cost resolution of each pre-closure pursuit set.)

    `_independent_options` is a test-only hook: pass a smaller option list to exercise the same
    code paths on a tractable powerset (the diff harness uses it). Default None = full list."""
    if csv_path is not None:
        return _load_loadouts_from_csv(csv_path)
    # ── Industry forks (explicit chain rungs for the pathology comparison) ──
    INDUSTRY_PATHS = []
    INDUSTRY_PATHS.append(set())                                    # Crude
    INDUSTRY_PATHS.append({"Furnace"})                              # Cast
    INDUSTRY_PATHS.append({"Blacksmith"})                           # Wrought
    INDUSTRY_PATHS.append({"Blacksmith", "Master Workshop"})        # Wrought + Serrated
    INDUSTRY_PATHS.append({"Blacksmith", "Armory", "Gilded Foundry"})  # Wrought + Planishing
    INDUSTRY_PATHS.append({"Blacksmith", "Forge"})                  # Forged, no MW
    INDUSTRY_PATHS.append({"Blacksmith", "Forge", "Master Workshop"})  # Forged + Serrated
    INDUSTRY_PATHS.append({"Blacksmith", "Forge", "Armory", "Gilded Foundry"})  # Forged + Planishing
    INDUSTRY_PATHS.append({"Blacksmith", "Forge", "Armory", "Gilded Foundry", "Master Workshop"})  # Forged + both
    INDUSTRY_PATHS.append({"Stable", "Blacksmith", "Forge", "Master Workshop", "Armory", "Gilded Foundry", "ABF"})  # full line
    RETINUE_CHAINS = [
        frozenset(),
        frozenset(["Coliseum"]),
        frozenset(["War College"]),
        frozenset(["Preceptory", "Preceptory KT", "Hospitaller", "Abbey",
                   "Monastery", "Pilgrimage Site"]),
    ]
    INDEPENDENT_OPTIONS = [
        "Levy Hall",
        "Joinery",
        "Fletchery",
        "Tiltyard",
        "Stable",
        "Royal Pavilion",
        "Grand Tournament",
        "Ministry",
        "Ministry Mastery",
        "Outrider Intercept Post",
        "Outrider Mastery",
        "Tannery",
        "Armory",
        "Butchery",
        "Toxicarium",
        "Full Hospitaller",
        "Preceptory",
        "Abbey",
    ]
    if _independent_options is not None:
        INDEPENDENT_OPTIONS = list(_independent_options)
    AUTO_INCLUDED = {
        "Carpentry":         ["Joinery", "Fletchery"],
        "Animal Husbandry":  ["Tannery", "Butchery"],
        "Smokehouse":        ["Butchery"],
        "Coliseum":          ["Tiltyard", "Royal Pavilion"],
        "Tannery":           ["Armory"],
        "Armory":            ["Tannery"],
        "Ministry":          ["Ministry Mastery"],
        "Caravanery":        ["Outrider Intercept Post"],
        "Cipher Chamber":    ["Outrider Intercept Post"],
        "Outrider Intercept Post": ["Outrider Mastery"],
    }
    n_opts = len(INDEPENDENT_OPTIONS)
    # ── PERF: memo cache keyed on the post-normalize, pre-closure pursuit frozenset. ──
    seen_keys = {}
    for industry_path in INDUSTRY_PATHS:
        tier_str = derive_tier_from_pursuits(industry_path)
        # tier_str only depends on industry_path → compute the per-tier melee list once here.
        melee_for_tier = _melee_options_for_tier(tier_str)
        ranged_at_or_below = _ranged_at_or_below(tier_str, _RANGED_BY_TIER)
        industry_set = set(industry_path)
        for ret_chain in RETINUE_CHAINS:
            ret_seed = set(ret_chain) | industry_set
            for mask in range(1 << n_opts):
                opt_set = frozenset(INDEPENDENT_OPTIONS[i] for i in range(n_opts)
                                    if mask & (1 << i))
                pursuits = set(ret_seed) | set(opt_set)
                if "Full Hospitaller" in pursuits:
                    pursuits.discard("Full Hospitaller")
                    pursuits.update(("Apothecary", "Infirmary", "Hospitaller"))
                for forced, deps in AUTO_INCLUDED.items():
                    if forced == "Armory" and not (
                        "Blacksmith" in pursuits or "Forge" in pursuits or "ABF" in pursuits
                    ):
                        continue
                    if any(d in pursuits for d in deps):
                        pursuits.add(forced)
                pursuits = _normalize_pool_tokens(pursuits)
                # closure (precomputed prereq table + direct mastery-req pull) then validity + cost
                pursuits = master_effect_closure(prereq_closure(pursuits))
                if not _pursuit_set_is_valid(pursuits):
                    continue
                total_cost, domain, tags = compute_pursuit_cost(pursuits)
                retinue_guess = derive_retinue_from_pursuits(pursuits)
                budget = len(pursuits) if budget_metric == "total" else total_cost
                if budget > max_pursuit_cost or budget < min_pursuit_cost:
                    continue
                if sum(1 for m in _POOL_MONUMENTS if m in pursuits) > max_monuments:
                    continue
                has_stable_explicit = "Stable" in opt_set
                has_fletch = "Fletchery" in pursuits
                has_ty = "Tiltyard" in pursuits
                arms_options = []
                if has_stable_explicit and has_ty:
                    arms_options.append(("Lance", None, False))
                    arms_options.append(("Cavalry Spear", None, False))
                    for w in melee_for_tier:
                        for r in ranged_at_or_below:
                            arms_options.append((w, r, True))
                elif has_stable_explicit:
                    arms_options.append(("Lance", None, False))
                    arms_options.append(("Cavalry Spear", None, False))
                    for w in melee_for_tier:
                        arms_options.append((w, None, False))
                elif has_fletch and has_ty:
                    for w in melee_for_tier:
                        for r in ranged_at_or_below:
                            arms_options.append((w, r, True))
                elif has_fletch:
                    for r in ranged_at_or_below:
                        arms_options.append((None, r, False))
                else:
                    for w in melee_for_tier:
                        arms_options.append((w, None, False))
                dual_wield_weapons = set()
                if has_ty:
                    for w in melee_for_tier:
                        if w == "Farm Tools" or is_2h(w) or w in STABLE_WEAPONS:
                            continue
                        arms_options.append((w, None, True))
                        dual_wield_weapons.add(w)
                for weapon, ranged, ty in arms_options:
                    is_two_of_same = (weapon in dual_wield_weapons and ranged is None and ty)
                    if ranged == "Crossbow":
                        w_init = WEAPONS[weapon]["init"] if weapon and weapon != "Farm Tools" else 0
                        opts = [None]
                        if (shield_satisfied("Tower Shield", pursuits)
                                and w_init + SHIELDS["Tower Shield"]["init"] >= -1):
                            opts.append("Tower Shield")
                        shield_opts = opts
                    elif weapon is None or is_2h(weapon) or is_two_of_same:
                        shield_opts = [None]
                    else:
                        w_init = (WEAPONS.get(weapon, {}).get("init", 0)
                                  if weapon and weapon != "Farm Tools"
                                  else (RANGED.get(ranged, {}).get("init", 0) if ranged else 0))
                        best_shield = None
                        for s in _SHIELD_LADDER:
                            if not shield_satisfied(s, pursuits):
                                continue
                            if w_init + SHIELDS[s]["init"] < -1:
                                continue
                            best_shield = s
                            break
                        shield_opts = [best_shield] if best_shield else [None]
                    armor_opts = [next((a for a in _ARMOR_LADDER
                                        if armor_satisfied(a, pursuits)), "Cloth")]
                    for shield in shield_opts:
                        for armor in armor_opts:
                            if not is_two_of_same and not valid_combo(
                                    retinue_guess, weapon or "Farm Tools", shield, armor, ranged, ty):
                                continue
                            if shield is not None and not shield_satisfied(shield, pursuits):
                                continue
                            if not armor_satisfied(armor, pursuits):
                                continue
                            if ranged is not None and "Fletchery" not in pursuits:
                                continue
                            requires_joinery = (
                                weapon is not None and weapon != "Farm Tools"
                                and not is_2h(weapon)
                                and not is_two_of_same
                                and ranged != "Crossbow"
                            )
                            if requires_joinery and "Joinery" not in pursuits:
                                continue
                            domain_count = sum(domain.values())
                            if domain_count > 30:
                                continue
                            build_tags = set(tags)
                            if is_two_of_same:
                                build_tags.add("Dual Wield")
                            tags_tuple = tuple(sorted(build_tags))
                            obs_key = (retinue_guess, weapon, shield, armor, ranged, ty, tags_tuple)
                            if obs_key in seen_keys and seen_keys[obs_key][0] <= total_cost:
                                continue
                            name = _name(retinue_guess, weapon, shield, armor, ranged, ty,
                                         sorted(build_tags), playstyle=None, pursuits=pursuits,
                                         domain=domain)
                            ld = Loadout(
                                name=name,
                                retinue=retinue_guess, weapon=weapon, shield=shield, armor=armor,
                                ranged=ranged, has_tiltyard=ty, size=DEFAULT_ARMY_SIZE,
                                extra_tags=sorted(build_tags),
                                upkeep_per_retinue=0,
                                playstyle=None,
                                tiltyard_mastery=True,
                                pursuits=pursuits,
                                military_pursuit_count=total_cost,
                                domain_count=domain_count,
                            )
                            ld = ld._replace(upkeep_per_retinue=compute_effective_upkeep(ld))
                            seen_keys[obs_key] = (total_cost, ld)
    return [v[1] for v in seen_keys.values()]
def _ranged_at_or_below(tier_str, table):
    order = ["Crude", "Cast", "Wrought", "Forged", "Crafted"]
    idx = order.index(tier_str)
    out = []
    for t in order[:idx + 1]:
        out.extend(table[t])
    return out
def _structural_legal(weapon, shield, armor, ranged, has_tiltyard):
    if is_2h(weapon) and shield is not None:
        return False
    if weapon in STABLE_WEAPONS and ranged is not None:
        return False
    if weapon in ("Lance", "Cavalry Spear") and shield == "Tower Shield":
        return False
    if ranged == "Crossbow":
        if shield is not None and shield != "Tower Shield":
            return False
        if weapon in ("Lance", "Cavalry Spear"):
            return False
    if weapon == "Bastard Sword" and shield is None:
        return False
    if (weapon != "Farm Tools" and not is_2h(weapon) and shield is None and ranged != "Crossbow"):
        return False
    if ranged is not None and "One Shot" in RANGED[ranged].get("tags", []) and not has_tiltyard:
        return False
    if weapon != "Farm Tools" and ranged is not None and not has_tiltyard:
        return False
    return True
def balanced_validation_pool(mpc_min=4, mpc_max=13, per_cell=None, seed=2026,
                             keep_shield_tier_rule=False, verbose=False):
    import random as _random
    from collections import defaultdict
    rng = _random.Random(seed)
    RETS = ["Levy", "Man-at-Arms", "Sergeant", "Knight Templar"]
    SMITH_PATHS = {
        "Crude":   ([], 0),
        "Cast":    (["Furnace"], 1),
        "Wrought": (["Blacksmith"], 1),
        "Forged":  (["Blacksmith", "Forge"], 1),
        "Crafted": (["Blacksmith", "Forge", "ABF"], 1),
    }
    METAL_PATHS = {
        None:            ([], 0),
        "Tannery":       (["Animal Husbandry", "Tannery"], 2),
        "Armory":        (["Animal Husbandry", "Tannery", "Armory"], 2),
        "Gilded Foundry":(["Animal Husbandry", "Tannery", "Armory", "Gilded Foundry"], 2),
        "ABF":           (["Animal Husbandry", "Tannery", "Armory", "Gilded Foundry", "ABF"], 2),
    }
    FILLER = ["Master Workshop", "Toxicarium", "Stable", "Butchery", "Smokehouse"]
    FILLER = [f for f in FILLER if f in PURSUITS_INFO]
    armor_for_tier = {"Crude": "Cloth", "Cast": "Leather", "Wrought": "Chainmail",
                      "Forged": "Full Plate", "Crafted": "Gothic Plate"}
    shield_tiers = {None: None, "Crude": "Wooden Shield", "Cast": "Kite Shield",
                    "Wrought": "Scutum Shield", "Forged": "Tower Shield", "Crafted": "Heater Shield"}
    cells = defaultdict(list)
    weapons_by_tier = defaultdict(list)
    for w, d in WEAPONS.items():
        weapons_by_tier[d["tier"]].append(w)
    ranged_by_tier = defaultdict(list)
    for r, d in RANGED.items():
        ranged_by_tier[d["tier"]].append(r)
    TIER_AT_OR_BELOW = {t: TIER_ORDER[:i + 1] for i, t in enumerate(TIER_ORDER)}
    def shield_options(weapon, smith_tier):
        opts = [None]
        for st in TIER_AT_OR_BELOW[smith_tier]:
            sh = shield_tiers.get(st)
            if sh:
                opts.append(sh)
        return list(dict.fromkeys(opts))
    gear_configs = []
    all_shields = [None] + [shield_tiers[t] for t in TIER_ORDER]
    for weapon, wd in WEAPONS.items():
        for armor_tier in TIER_ORDER:
            armor = armor_for_tier[armor_tier]
            for shield in dict.fromkeys(all_shields):
                if not _structural_legal(weapon, shield, armor, None, has_tiltyard=False):
                    continue
                if keep_shield_tier_rule and shield is not None and not is_2h(weapon) \
                   and weapon not in ("Lance", "Cavalry Spear", "Farm Tools"):
                    if TIER_IDX.get(SHIELDS[shield]["tier"], 0) < TIER_IDX.get(WEAPONS[weapon]["tier"], 0):
                        continue
                gear_configs.append((weapon, shield, armor, None))
    for ranged in RANGED:
        for armor_tier in TIER_ORDER:
            armor = armor_for_tier[armor_tier]
            if _structural_legal("Farm Tools", None, armor, ranged, has_tiltyard=True):
                gear_configs.append(("Farm Tools", None, armor, ranged))
            for weapon in WEAPONS:
                if weapon == "Farm Tools":
                    continue
                for shield in dict.fromkeys(all_shields):
                    if not _structural_legal(weapon, shield, armor, ranged, has_tiltyard=True):
                        continue
                    if keep_shield_tier_rule and shield is not None and not is_2h(weapon) \
                       and weapon not in ("Lance", "Cavalry Spear"):
                        if TIER_IDX.get(SHIELDS[shield]["tier"], 0) < TIER_IDX.get(WEAPONS[weapon]["tier"], 0):
                            continue
                    gear_configs.append((weapon, shield, armor, ranged))
    if verbose:
        print(f"gear configs: {len(gear_configs)}")
    for (weapon, shield, armor, ranged) in gear_configs:
        wtier = WEAPONS[weapon]["tier"] if weapon in WEAPONS else "Crude"
        if ranged is not None:
            wtier = TIER_ORDER[max(TIER_IDX[wtier], TIER_IDX[RANGED[ranged]["tier"]])]
        smith_set, _ = SMITH_PATHS[wtier]
        atier = ARMORS[armor]["tier"]
        metal_by_armor = {"Crude": None, "Cast": "Tannery", "Wrought": "Armory",
                          "Forged": "Gilded Foundry", "Crafted": "ABF"}
        metal_name = metal_by_armor[atier]
        metal_set = list(METAL_PATHS[metal_name][0]) if metal_name else []
        shield_set = []
        if shield is not None:
            shield_set = ["Carpentry", "Joinery"]
            shield_bld = {
                "Wooden Shield": [],
                "Kite Shield":   ["Blacksmith"],
                "Scutum Shield": ["Blacksmith", "Armory"],
                "Tower Shield":  ["Blacksmith", "Forge"],
                "Heater Shield": ["Blacksmith", "ABF"],
            }
            shield_set += shield_bld.get(shield, [])
        has_ty = ranged is not None
        ty_set = ["Carpentry", "Fletchery", "Coliseum", "Tiltyard"] if has_ty else []
        gear_base = set(smith_set) | set(metal_set) | set(shield_set) | set(ty_set)
        RETINUE_UNLOCK = {"Levy": [], "Man-at-Arms": ["Coliseum"],
                          "Sergeant": ["War College"], "Knight Templar": ["Preceptory"]}
        UPGRADES = ["Conditioning Field", "Royal Pavilion", "Ministry of Military Strategy",
                    "Outrider Intercept Post", "Preceptory", "Grand Tournament"]
        MONUMENTS_SPLIT = {"Royal Pavilion", "Ministry of Military Strategy", "Outrider Intercept Post", "Preceptory"}
        REGEN_LADDER = ["Apothecary", "Infirmary", "Hospitaller"]
        def flat_mastery_seed(spec):
            s = {spec}
            if spec in PURSUITS_INFO:
                s |= set(PURSUITS_INFO[spec].get("mastery_req", []))
            return s
        for ret in RETS:
            unlock_seed = set()
            for u in RETINUE_UNLOCK[ret]:
                unlock_seed |= flat_mastery_seed(u)
            for _u_try in range(3):
                if rng.random() < 2/3:
                    upgrade = "Conditioning Field"
                else:
                    upgrade = rng.choice([u for u in UPGRADES if u != "Conditioning Field"])
                if upgrade == "Preceptory" and ret == "Knight Templar":
                    upgrade = "Conditioning Field"
                innate_only = (upgrade in MONUMENTS_SPLIT) and (rng.random() < 1/3)
                if innate_only:
                    upgrade_seed = {upgrade}
                else:
                    upgrade_seed = flat_mastery_seed(upgrade)
                base_seed_set = unlock_seed | upgrade_seed
                gear_full = master_effect_closure(prereq_closure(gear_base))
                base_set = gear_full | base_seed_set
                base_cost, _, _ = compute_pursuit_cost(base_set) if base_set else (0, {}, set())
                for target_mpc in range(mpc_min, mpc_max + 1):
                    if base_cost > target_mpc:
                        continue
                    regen_avail = [r for r in REGEN_LADDER if r not in base_set]
                    other_filler = [f for f in FILLER if f not in base_set]
                    rng.shuffle(other_filler)
                    menu = regen_avail + other_filler
                    chosen = []
                    cur_cost = base_cost
                    for f in menu:
                        if cur_cost >= target_mpc:
                            break
                        trial = master_effect_closure(
                            prereq_closure(gear_base | set(chosen + [f]))) | base_seed_set
                        tc, _, _ = compute_pursuit_cost(trial)
                        if tc > target_mpc:
                            continue
                        chosen.append(f)
                        cur_cost = tc
                    pursuit_set = (master_effect_closure(
                        prereq_closure(gear_base | set(chosen))) | base_seed_set)
                    cost, domain, tags = compute_pursuit_cost(pursuit_set)
                    if cost != target_mpc:
                        continue
                    tags = set(tags)
                    dom_count = int(sum(domain.values()))
                    eff_ret = ret
                    name = _name(eff_ret, weapon, shield, armor, ranged, has_ty, sorted(tags),
                                 pursuits=pursuit_set, domain=domain)
                    ld = Loadout(
                        name=name + f"|M{target_mpc}",
                        retinue=eff_ret, weapon=weapon, shield=shield, armor=armor, ranged=ranged,
                        has_tiltyard=has_ty, size=DEFAULT_ARMY_SIZE,
                        extra_tags=frozenset(tags), upkeep_per_retinue=0,
                        playstyle=None, tiltyard_mastery=False, pursuits=frozenset(pursuit_set),
                        military_pursuit_count=target_mpc, domain_count=dom_count,
                    )
                    ld = ld._replace(upkeep_per_retinue=compute_effective_upkeep(ld))
                    cells[(eff_ret, target_mpc)].append(ld)
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
_EFFECT_BEARING_MASTERY = {
    "Conditioning Field", "Ministry of Military Strategy", "Tiltyard", "Royal Pavilion",
    "Master Workshop", "Gilded Foundry", "Outrider Intercept Post",
    "Apothecary", "Infirmary", "Hospitaller", "Grand Tournament",
}
def master_effect_closure(pursuits):
    out = set(pursuits)
    for p in list(out):
        if p in _EFFECT_BEARING_MASTERY and p in PURSUITS_INFO:
            for req in PURSUITS_INFO[p].get("mastery_req", []):
                out.add(req)
    return out
# ── PERF: precompute each combat spec's full transitive prereq closure once at import. ──
# prereq_closure() then becomes a flat union of these frozensets instead of an O(n^2)
# while-fixpoint re-run on every candidate. The closure it produces is byte-for-byte the
# same set the old fixpoint produced (same combat-spec-only prereq graph).
_EMPTY = frozenset()
def _build_prereq_closure_table():
    table = {}
    def closure_of(node, stack):
        if node in table:
            return table[node]
        if node not in PURSUITS_INFO:
            return _EMPTY
        acc = set()
        for pre in PURSUITS_INFO[node].get("prereqs", []):
            if pre in PURSUITS_INFO:
                acc.add(pre)
                if pre not in stack:           # guard against any accidental cycle
                    acc |= closure_of(pre, stack | {pre})
        fs = frozenset(acc)
        table[node] = fs
        return fs
    for n in PURSUITS_INFO:
        closure_of(n, {n})
    return table
_PREREQ_CLOSURE = _build_prereq_closure_table()
def prereq_closure(pursuits):
    """Input set plus the transitive closure of COMBAT-RELEVANT prerequisites. Uses a
    precomputed per-node closure table (built once at import); result is identical to the
    former fixpoint implementation."""
    out = set(pursuits)
    for p in pursuits:
        c = _PREREQ_CLOSURE.get(p)
        if c:
            out |= c
    return out
def validate_loadout(ld, check_tier_floors=False):
    v = []
    P = set(ld.pursuits)
    w, sh, ar, rg = ld.weapon, ld.shield, ld.armor, ld.ranged
    if w is not None and is_2h(w) and sh is not None:
        v.append(f"2H weapon {w} has shield {sh}")
    if (w not in (None, "Farm Tools") and not is_2h(w) and sh is None and rg != "Crossbow"):
        v.append(f"1H weapon {w} has no shield")
    if w == "Bastard Sword" and sh is None:
        v.append("Bastard Sword (1H) has no shield")
    if w in ("Lance", "Cavalry Spear") and sh == "Tower Shield":
        v.append(f"{w} cannot use Tower Shield")
    if w in STABLE_WEAPONS and rg is not None:
        v.append(f"Stable cavalry weapon {w} cannot dual-equip ranged {rg}")
    if rg == "Crossbow":
        if sh is not None and sh != "Tower Shield":
            v.append(f"Crossbow with non-Tower shield {sh}")
        if w in ("Lance", "Cavalry Spear"):
            v.append(f"Crossbow with {w}")
    if rg is not None and "One Shot" in RANGED.get(rg, {}).get("tags", []) and not ld.has_tiltyard:
        v.append(f"One-Shot ranged {rg} without Tiltyard")
    if w not in (None, "Farm Tools") and rg is not None and not ld.has_tiltyard:
        v.append(f"dual-equip ({w}+{rg}) without Tiltyard")
    SMITH_REQ = {"Crude": set(), "Cast": {"Furnace"}, "Wrought": {"Blacksmith"},
                 "Forged": {"Blacksmith", "Forge"}, "Crafted": {"Blacksmith", "Forge", "ABF"}}
    wt = WEAPONS.get(w, {}).get("tier", "Crude") if w else "Crude"
    if rg is not None:
        rt = RANGED.get(rg, {}).get("tier", "Crude")
        if TIER_IDX[rt] > TIER_IDX[wt]:
            wt = rt
    missing_smith = SMITH_REQ[wt] - P
    if missing_smith:
        v.append(f"{w} (tier {wt}) missing smithing {sorted(missing_smith)}")
    if sh is not None:
        if "Joinery" not in P:
            v.append(f"shield {sh} without Joinery")
        if "Carpentry" not in P:
            v.append(f"shield {sh} without Carpentry (Joinery prereq)")
        SHIELD_REQ = {"Wooden Shield": set(), "Kite Shield": {"Blacksmith"},
                      "Scutum Shield": {"Blacksmith", "Armory"},
                      "Tower Shield": {"Blacksmith", "Forge"},
                      "Heater Shield": {"Blacksmith", "ABF"}}
        missing_sh = SHIELD_REQ.get(sh, set()) - P
        if missing_sh:
            v.append(f"shield {sh} missing buildings {sorted(missing_sh)}")
    else:
        if "Joinery" in P:
            v.append("Joinery present but no shield")
    METAL_REQ = {"Crude": set(), "Cast": {"Tannery"}, "Wrought": {"Armory"},
                 "Forged": {"Gilded Foundry"}, "Crafted": {"ABF"}}
    at = ARMORS.get(ar, {}).get("tier", "Crude")
    missing_metal = METAL_REQ[at] - P
    if missing_metal:
        v.append(f"armor {ar} (tier {at}) missing metal {sorted(missing_metal)}")
    if rg is not None:
        for need in ("Carpentry", "Fletchery", "Tiltyard"):
            if need not in P:
                v.append(f"ranged {rg} without {need}")
    _rp_present = "Royal Pavilion" in P
    if "Fletchery" in P and rg is None and not _rp_present:
        v.append("Fletchery without a ranged weapon")
    if ld.has_tiltyard and rg is None and not _rp_present:
        v.append("Tiltyard without a ranged weapon")
    _gf_masters = "Armory" in P and "Blacksmith" in P
    if ("Gilded Foundry" in P and ar not in ("Full Plate", "Gothic Plate")
            and "ABF" not in P and not _gf_masters):
        v.append(f"Gilded Foundry present but armor is {ar}, no ABF, and Planishing unmet (inert)")
    present_for_mastery = set()
    for p in P:
        if p in PURSUITS_INFO:
            present_for_mastery |= set(PURSUITS_INFO[p].get("mastery_req", []))
    _MONUMENTS = {"Royal Pavilion", "Ministry of Military Strategy", "Outrider Intercept Post",
                  "Preceptory", "ABF"}
    innate_only_specs = set()
    for p in P:
        if p in _MONUMENTS and p in PURSUITS_INFO:
            mreq = PURSUITS_INFO[p].get("mastery_req", [])
            if mreq and not all(r in P for r in mreq):
                innate_only_specs.add(p)
    for p in P:
        if p not in PURSUITS_INFO:
            continue
        if p in present_for_mastery or p in innate_only_specs:
            continue
        for pre in PURSUITS_INFO[p].get("prereqs", []):
            if pre in PURSUITS_INFO and pre not in P:
                v.append(f"pursuit {p} missing prereq {pre}")
    return v
def validate_pool(pool, check_tier_floors=False, max_report=20, verbose=True):
    bad = {}
    counts = {}
    for ld in pool:
        vio = validate_loadout(ld, check_tier_floors=check_tier_floors)
        if vio:
            bad[ld.name] = vio
            for msg in vio:
                key = msg.split(" ")[0] + " " + (msg.split(" missing ")[0].split()[-1] if "missing" in msg else "")
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
            print("  ALL VALID")
    return bad
def with_playstyle(loadout, playstyle):
    new_name = _name(loadout.retinue, loadout.weapon, loadout.shield, loadout.armor,
                     loadout.ranged, loadout.has_tiltyard, loadout.extra_tags,
                     playstyle=playstyle, pursuits=loadout.pursuits)
    return loadout._replace(name=new_name, playstyle=playstyle)
def kt_twins(pool):
    from playstyles import assign_default_playstyle
    twins = []
    for ld in pool:
        if ld.retinue != "Knight Templar":
            continue
        spoof = ld._replace(retinue="Sergeant")
        natural_ps = assign_default_playstyle(spoof)
        if natural_ps == "Unshakable":
            continue
        new_name = _name(ld.retinue, ld.weapon, ld.shield, ld.armor,
                         ld.ranged, ld.has_tiltyard, ld.extra_tags,
                         playstyle=natural_ps, pursuits=ld.pursuits) + " (NaturalPS)"
        twin = ld._replace(name=new_name, playstyle=natural_ps)
        twins.append(twin)
    return twins
def cross_playstyle_pool(base_pool, playstyles):
    out = []
    for ld in base_pool:
        for ps in playstyles:
            out.append(with_playstyle(ld, ps))
    return out
def optimal_playstyle_pool(base_pool):
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
    print(f"Tournament size: {len(pool)} x {len(pool)} = {len(pool)**2:,} matchups")
    print(f"At 100 runs/matchup: {len(pool)**2 * 100:,} battles")