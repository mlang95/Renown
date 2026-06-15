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
from renown_combat import RETINUES, WEAPONS, RANGED, SHIELDS, ARMORS

Loadout = namedtuple("Loadout",
    "name retinue weapon shield armor ranged has_tiltyard size extra_tags upkeep_per_retinue playstyle tiltyard_mastery pursuits military_pursuit_count domain_count")
Loadout.__new__.__defaults__ = (None, True, frozenset(), 0, 0)  # playstyle, tiltyard_mastery, pursuits, mpc, domain_count


# ==============================================================================
# Tier ordering, abbreviations
# ==============================================================================

TIER_ORDER = ["Crude", "Cast", "Wrought", "Forged", "Crafted"]
TIER_IDX = {t: i for i, t in enumerate(TIER_ORDER)}

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
        base += " (TY)"   # marks an actual dual-equip, not mere Tiltyard ownership

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
        # 4-domain standing tuple
        _, dom, _ = compute_pursuit_cost(P)
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
    - Pure-ranged exception: Farm Tools + ranged represents a ranged-focused build.
    """
    if is_2h(weapon) and shield is not None:
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
# PURSUITS_INFO — rebuilt from specs.csv (combat-relevant specs only).
# Per spec: prereqs (=Mastery Requirement pursuits), domain (Unlock standing R3/E6/S10),
#   innate_tags (granted when spec present), mastery_tags (granted only when mastery_req ⊆ build),
#   mastery_req (pursuits gating the mastery effect — LOCAL, not transitive),
#   efficient (this spec's mastery makes that target spec cost 0 MPC if both present),
#   upkeep_effects (flat -200 per -5, -500 per -10, stacking).
# Economic prereqs not in this dict (Academy, Mine, Herb Garden, etc.) are the closure boundary:
#   treated as satisfied, never added to builds.
def _pursuits_info_from_renown_data():
    """Build the sim's pursuit table from renown_data.NODES 'engine' fields —
    the single source of truth. Each engine entry carries the sim semantics
    (cost/prereqs/domain/innate_tags/mastery_tags/mastery_req/efficient/
    upkeep_effects); 'alias' is the short key the sim uses internally."""
    from renown_data import NODES
    out = {}
    for node_name, node in NODES.items():
        eng = node.get("engine")
        if not eng:
            continue
        key = eng.get("alias", node_name)
        out[key] = {k: v for k, v in eng.items() if k != "alias"}
    # Override 'efficient' from the canonical text-parsed graph (single source of
    # truth = the "**Efficient X**" markup), keyed by sim alias, so the MPC
    # discount sees ALL 46 links — not the partial engine.efficient mirror.
    from renown_data import EFFICIENT, NODES as _N
    def _alias(name):
        return _N.get(name, {}).get("engine", {}).get("alias", name)
    for src, tgt in EFFICIENT.items():
        k = _alias(src)
        if k in out:
            out[k]["efficient"] = _alias(tgt)
    return out


PURSUITS_INFO = _pursuits_info_from_renown_data()

# Tier → Industry domain requirement (Rising/Established/Sovereign mapping)
TIER_INDUSTRY_REQ = {"Crude": 0, "Cast": 0, "Wrought": 3, "Forged": 6, "Crafted": 10}

# Mapping from tier pursuit → gear tier string
TIER_PURSUIT_TO_TIER = {None: "Crude", "Furnace": "Cast", "Blacksmith": "Wrought",
                        "Forge": "Forged", "ABF": "Crafted"}


def _gear_tier_idx(loadout_weapon, loadout_shield, loadout_armor, loadout_ranged):
    """Return the highest tier index used by any gear piece on this loadout."""
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
    """The player's retinue is DETERMINED by what's built — not chosen separately.

    Rules:
      - Full Preceptory MASTERY (Preceptory + its full mastery_req: Monastery,
        Pilgrimage Site, Hospitaller, Abbey) + Preceptory KT → Knight Templar
      - War College (without full Preceptory) → Sergeant  [no longer needs Coliseum]
      - Coliseum alone (no War College) → Man-at-Arms
      - Nothing → Levy

    NOTE: War College is depegged from Coliseum. A Sergeant build need not carry
    Coliseum. If a Sergeant wants the Tiltyard chain (which requires Coliseum), they
    must buy Coliseum separately. Coliseum now appears mainly on Man-at-Arms builds
    and on Sergeants/KTs that specifically want the Tiltyard/Royal Pavilion line.
    """
    precep_mastery = set(PURSUITS_INFO["Preceptory"]["mastery_req"])  # Monastery, Pilgrimage Site, Hospitaller, Abbey
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


def armor_satisfied(armor_name, pursuits):
    """True if the loadout's pursuits include a building that unlocks the given armor."""
    required = ARMOR_REQUIRES.get(armor_name, set())
    if not required:
        return True  # no building needed (Cloth)
    return bool(required & pursuits)


def shield_satisfied(shield_name, pursuits):
    """True if the loadout has Joinery AND any of the metal-craft buildings the shield needs.
    Wooden Shield needs only Joinery (no metal)."""
    if "Joinery" not in pursuits:
        return False
    required_metal = SHIELD_METAL_REQUIRES.get(shield_name, set())
    if not required_metal:
        return True  # only Joinery needed (Wooden Shield)
    return bool(required_metal & pursuits)


import renown_data as rd


_POOL_MONUMENTS = frozenset(
    (rd.NODES[n].get("engine", {}).get("alias", n))
    for n, v in rd.NODES.items()
    if (v.get("type") == "Monument" or v.get("monument"))
) | {"Ministry of Military Strategy"}  # canonical name (post-normalization)


def _normalize_pool_tokens(pursuits):
    """Map the archetype pool's short Ministry tokens onto the canonical pursuit.

    Pool emits "Ministry" (base) and "Ministry Mastery" (mastery upgrade). The
    real node is "Ministry of Military Strategy"; its mastery tags fire when its
    mastery_req {University, War College} are present. So:
      "Ministry"          -> add the canonical node
      "Ministry Mastery"  -> add the canonical node AND University (satisfies mastery)
    Both tokens are removed after mapping.
    """
    p = set(pursuits)
    if "Ministry" in p or "Ministry Mastery" in p:
        p.discard("Ministry")
        if "Ministry Mastery" in p:
            p.discard("Ministry Mastery")
            p.add("University")          # the missing half of mastery_req
        p.add("Ministry of Military Strategy")
    return p


def compute_pursuit_cost(pursuits):
    """Compute (MPC, domain_dict, tags_set) from a pursuit set under the CSV-derived model.

    TAGS — innate vs mastery:
      * A spec's innate_tags are granted whenever the spec is present.
      * A spec's mastery_tags are granted ONLY when every pursuit in its mastery_req is also
        present (the mastery gate is LOCAL — those prereqs need only be present, not themselves
        mastered). Mastery without innate is impossible; innate without mastery is fine.

    MPC (settlement space) vs TOTAL INVESTMENT (action economy):
      * total_investment = raw count of pursuits (every pursuit = 1; computed separately, see
        analysis.total_investment). NOT returned here.
      * MPC = pursuit count minus each satisfied "Efficient X": if a spec's mastery is satisfied
        and grants Efficient<Target>, and Target is in the build, Target costs 0 MPC. Each such
        discount removes 1 from MPC. total_investment is unaffected by Efficient-X.

    Economic prereqs not in PURSUITS_INFO (Academy, Mine, Herb Garden, ...) are the closure
    boundary: ignored here (treated as satisfied, never costed).

    Returns (mpc, domain_dict, tags_set).
    """
    P = set(pursuits)
    known = [p for p in P if p in PURSUITS_INFO]

    def mastered(p):
        mreq = PURSUITS_INFO[p].get("mastery_req", [])
        return all(r in P for r in mreq)

    # ── MPC: start at count of known pursuits, subtract satisfied Efficient-X discounts ──
    discounted = set()
    for p in known:
        tgt = PURSUITS_INFO[p].get("efficient")
        if tgt and mastered(p) and tgt in P and tgt in PURSUITS_INFO:
            discounted.add(tgt)   # target spec costs 0 MPC (space) thanks to this efficiency
    mpc = len(known) - len(discounted)

    # ── Domain requirements (max across pursuits; floor from gear tier) ──
    domain = {"Industry": 0, "Prowess": 0, "Piety": 0, "Cunning": 0}
    for p in known:
        for d, v in PURSUITS_INFO[p].get("domain", {}).items():
            domain[d] = max(domain[d], v)
    tier_str = derive_tier_from_pursuits(pursuits)
    domain["Industry"] = max(domain["Industry"], TIER_INDUSTRY_REQ[tier_str])

    # ── Tags: innate always; mastery only when mastery_req satisfied ──
    tags = set()
    for p in known:
        info = PURSUITS_INFO[p]
        tags.update(info.get("innate_tags", []))
        if mastered(p):
            tags.update(info.get("mastery_tags", []))

    # Outrider: mastery (reveal every skirmish) supersedes the innate once/battle reveal.
    if "Outrider: every" in tags:
        tags.discard("Outrider: once")

    # 'tier:*' entries are informational (which gear tier the spec unlocks); the engine derives
    # the actual gear tier from the equipped weapon/armor, so drop them from the combat tag set.
    tags = {t for t in tags if not t.startswith("tier:")}

    # ── Domain-standing SELF tags (conferred by reaching a standing in a domain) ──
    # Standings: Rising=3, Established=6, Sovereign=10. These apply to the build itself.
    #   Rising Prowess (>=3)      -> Immune Blocked (immune to the first-skirmish -1 init debuff)
    #   Established Prowess (>=6)  -> Parry (failed-save second chance, 5+)
    # (Opponent-applied Cunning debuffs — Established Cunning->opp Blocked, Sovereign Cunning->opp
    #  Strain — are NOT here; they're applied at matchup resolution in the engine, since they depend
    #  on the opponent. They're surfaced via the 'confers:*' marker tags below so the engine can read
    #  a build's Cunning standing without recomputing domains.)
    if domain["Prowess"] >= 3:
        tags.add("Immune Blocked")
    if domain["Prowess"] >= 6:
        tags.add("Parry")
    #   Established Piety (>=6)    -> +1 Morale ("Shake +1": -1 to the effective Morale target,
    #                                  which also delays the Fatigue rout clock by one token)
    if domain["Piety"] >= 6:
        tags.add("Shake +1")
    # Marker tags (not combat effects themselves) telling the engine what this build inflicts on its
    # opponent. The engine strips 'confers:*' from the build's own effective tags and instead adds the
    # named debuff to the OPPONENT's tags at matchup setup.
    if domain["Cunning"] >= 6:
        tags.add("confers:Blocked")
    if domain["Cunning"] >= 10:
        tags.add("confers:Strain")

    return mpc, domain, tags





def compute_effective_upkeep(loadout):
    """Compute per-retinue upkeep AFTER all pursuit-based reductions.

    Walks the loadout's pursuits, applies flat reductions and conditional
    reductions (based on equipped shield, ranged weapon, or armor type).
    Returns the reduced per-retinue cost. Floor of 200 to prevent free retinues.

    Conditionals checked:
      - "if_shield": active when loadout.shield is not None
      - "if_ranged": active when loadout.ranged is not None
      - "if_armor_in": active when loadout.armor in the listed armor set
    """
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
    # Levy Hall + Butchery synergy: a Levy Hall paired with a Butchery upgrades from
    # -200 to -500 (the extra -300 on top of Levy Hall's base -200 flat).
    if "Levy Hall" in loadout.pursuits and "Butchery" in loadout.pursuits:
        reduction += 300
    # Floor at 200 gold per retinue to prevent free troops
    return max(200, base - reduction)


# ──────────────────────────────────────────────────────────────────────────
# Pursuit-set enumeration: which pursuit sets are valid (no waste, no
# unsatisfied prereqs)?
# ──────────────────────────────────────────────────────────────────────────
# A pursuit set is valid if:
#   - All structural prereqs are met (e.g., MW requires Forge or ABF)
#   - No pursuit is "wasted" in the sense the user described (e.g., Stable
#     without Forge/ABF would never be built since Lance needs Forged)

def _pursuit_set_is_valid(pursuits):
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
    if False:  # Ministry mastery handled via mastery_req after normalization
        return False
    # Caravanery / Cipher Chamber are only useful as Outrider prereqs — don't allow them
    # to appear without Outrider (no wasted Cunning buildings).
    if ("Caravanery" in pursuits or "Cipher Chamber" in pursuits) and "Outrider Intercept Post" not in pursuits:
        return False
    # War College is depegged from Coliseum (no prereq). Sergeant via War College alone.
    # Ministry requires War College
    if "Ministry of Military Strategy" in pursuits and "War College" not in pursuits:
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
    # Preceptory KT requires Preceptory MASTERED (Monastery + Pilgrimage Site + Hospitaller + Abbey)
    if "Preceptory KT" in pursuits and not (
            {"Preceptory"} | set(PURSUITS_INFO["Preceptory"]["mastery_req"]) <= set(pursuits)):
        return False
    # Stable is only useful for Lance, which requires Forged tier. Skip otherwise.
    if "Stable" in pursuits and not has_forge_or_abf:
        return False
    # If ABF in pursuits, Stable/MW/GF are auto-included; pruning duplicates in cost.
    return True


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

            ty_raw = str(row.get("tiltyard", "False")).strip().lower()
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
      - tags: union of pursuit-granted tags; full Hospitaller mastery = Regenerate 4

    Note on ABF: ABF (Crafted) is a 5pt all-inclusive package. It subsumes
    Stable + MW + GF + Forge. ABF in pursuits does NOT auto-imply explicit
    Stable purchase, so ABF players can still choose between Poleaxe (Crafted)
    or — if they also explicitly bought Stable — Lance (Forged). The "Stable
    → Lance" rule applies only to explicit Stable purchases.
    """
    # ── CSV mode ──────────────────────────────────────────────────────────
    if csv_path is not None:
        return _load_loadouts_from_csv(csv_path)

    pool = []

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
        frozenset(["Preceptory", "Preceptory KT", "Hospitaller", "Abbey",
                   "Monastery", "Pilgrimage Site"]),                   # KT (Preceptory mastered)
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
        "Grand Tournament",          # standalone: mastery (req Conditioning Field + Coliseum) grants Riposte
        "Ministry",
        "Ministry Mastery",          # Seize first TWO skirmishes (mastery upgrade)
        "Outrider Intercept Post",   # Cunning monument: tactic-reveal once/battle
        "Outrider Mastery",          # tactic-reveal first TWO skirmishes (mastery upgrade)
        # Master Workshop grants Rend (the -1 AP mechanic is retired). MWRend was its duplicate
        # and is no longer generated; ABF also grants Rend (see compute_pursuit_cost).
        "Master Workshop",   # grants Rend; the workshop variant generated
        "Gilded Foundry",
        "Tannery",       # -5 flat + -5 if cloth/leather; auto-bundles with Armory (shared slot)
        # NOTE: Armory is NOT a separate option — it auto-bundles with Tannery.
        "Butchery",      # -5 flat; needs Animal Husbandry + Tannery
        "Toxicarium",    # Rising Cunning; Poison tag on weapons
        # Health-stack collapsed: 'Full Hospitaller' represents the full
        # Apothecary + Infirmary + Hospitaller bundle (3pt, all the tags).
        "Full Hospitaller",
        "Preceptory",
        "Abbey",          # Piety 3; grants Shake +1 (morale buff). Independent MPC; also a
                          # prereq for Preceptory KT. Can attach to any retinue's build.
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
            retinue_guess = derive_retinue_from_pursuits(ret_chain)
            # NO retinue tier floors or caps — full retinue x tier cross.

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

                # Normalize pool tokens onto canonical node names before validity/cost.
                # The pool enumerates "Ministry"/"Ministry Mastery"; the node is keyed
                # "Ministry of Military Strategy" and its mastery (Crit 5/+1I/MaxInit3)
                # fires when mastery_req {University, War College} are present.
                pursuits = _normalize_pool_tokens(pursuits)

                # Validate prereqs (no auto-promote — explicit purchases must
                # have their prereqs satisfied or the combo is skipped)
                if not _pursuit_set_is_valid(pursuits):
                    continue

                # Re-derive retinue from the FINAL pursuit set (after auto-includes).
                # Post-depeg, Coliseum only enters via the MaA seed or the Tiltyard
                # auto-include; re-deriving guarantees the stored label matches the
                # actual pursuits (e.g., a Tiltyard MaA that gains Coliseum stays MaA,
                # and nothing is silently mislabeled).
                retinue_guess = derive_retinue_from_pursuits(pursuits)
                # NO retinue tier floors or caps (retinue re-derived post auto-includes).

                # Cost check: pool restricted to [min_pursuit_cost, max_pursuit_cost] on the
                # chosen budget metric:
                #   budget_metric="mpc"   -> MPC (pursuit count minus Efficient-X discounts)
                #   budget_metric="total" -> total investment (raw pursuit count, no discounts)
                total_cost, domain, tags = compute_pursuit_cost(pursuits)
                budget = len(pursuits) if budget_metric == "total" else total_cost
                if budget > max_pursuit_cost or budget < min_pursuit_cost:
                    continue

                # Max 2 monuments per loadout (unique one-per-game buildings). A player
                # realistically commits to at most a couple of these capstones.
                # Monument cap (parameterized). Set derived from renown_data flags,
                # mapped to the sim's aliases; counts canonical names post-normalization.
                if sum(1 for m in _POOL_MONUMENTS if m in pursuits) > max_monuments:
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
                    # Cavalry weapons (Lance Forged, Cavalry Spear Wrought) + Ranged at tier
                    for r in _ranged_at_or_below(tier_str, RANGED_BY_TIER):
                        arms_options.append(("Lance", r, True))
                        arms_options.append(("Cavalry Spear", r, True))
                    # ALSO offer the tier's melee weapons + ranged (Stable doesn't FORCE Lance;
                    # it UNLOCKS it). Without this, Crafted builds — which require Stable via
                    # ABF — could never field Poleaxe (the only Crafted melee weapon).
                    for w in melee_options_for_tier(tier_str):
                        for r in _ranged_at_or_below(tier_str, RANGED_BY_TIER):
                            arms_options.append((w, r, True))
                elif has_stable_explicit:
                    arms_options.append(("Lance", None, False))
                    arms_options.append(("Cavalry Spear", None, False))
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
                        w_init = WEAPONS[weapon]["init"] if weapon and weapon != "Farm Tools" else 0
                        opts = [None]
                        if (shield_satisfied("Tower Shield", pursuits)
                                and w_init + SHIELDS["Tower Shield"]["init"] >= -1):
                            opts.append("Tower Shield")
                        shield_opts = opts
                    elif weapon is None or is_2h(weapon):
                        shield_opts = [None]
                    else:
                        # Highest available shield by DEFENSIVE value, but skip any shield
                        # that would push base initiative below -1 (weapon init + shield init).
                        # Step down the defensive ladder until a building-satisfied shield
                        # keeps base init >= -1. E.g. Morningstar(-1)+Tower(-1) = -2 is skipped;
                        # falls to the next legal shield (Kite/Heater at init 0 → total -1).
                        w_init = (WEAPONS.get(weapon, {}).get("init", 0)
                                  if weapon and weapon != "Farm Tools"
                                  else (RANGED.get(ranged, {}).get("init", 0) if ranged else 0))
                        best_shield = None
                        for s in SHIELD_LADDER:
                            if not shield_satisfied(s, pursuits):
                                continue
                            if w_init + SHIELDS[s]["init"] < -1:
                                continue   # would break the init floor; try a lower-tier shield
                            best_shield = s
                            break
                        shield_opts = [best_shield] if best_shield else [None]

                    # Armor options: highest building-satisfied tier. Cloth is the fallback
                    # if no armor-craft building is present.
                    ARMOR_LADDER = ["Gothic Plate","Full Plate","Chainmail","Leather","Cloth"]
                    armor_opts = [next((a for a in ARMOR_LADDER
                                        if armor_satisfied(a, pursuits)), "Cloth")]

                    for shield in shield_opts:
                        for armor in armor_opts:
                            if not valid_combo(retinue_guess, weapon or "Farm Tools",
                                                shield, armor, ranged, ty):
                                continue
                            # Cross-validation: equipment requires specific pursuits.
                            # Shields require Joinery PLUS a metal-craft building based on tier.
                            # Wooden Shield needs only Joinery.
                            if shield is not None and not shield_satisfied(shield, pursuits):
                                continue
                            # Armor requires its armor-craft building. Cloth is free.
                            if not armor_satisfied(armor, pursuits):
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
                                and not is_2h(weapon)
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
                                         list(tags), playstyle=None, pursuits=pursuits)
                            ld = Loadout(
                                name=name,
                                retinue=retinue_guess, weapon=weapon, shield=shield, armor=armor,
                                ranged=ranged, has_tiltyard=ty, size=DEFAULT_ARMY_SIZE,
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
      - 1H melee (except Farm Tools) requires a shield, UNLESS Crossbow forces it shieldless.
      - Bastard Sword (1H profile) must carry a shield.
      - Lance / Cavalry Spear cannot use Tower Shield (Wooden is allowed).
      - Crossbow: only Tower Shield allowed (or shieldless); not with Lance/Cavalry Spear.
      - One Shot ranged (Javelin, Pilum) requires Tiltyard.
      - Dual-equip (real melee + ranged) requires Tiltyard.
    """
    if is_2h(weapon) and shield is not None:
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
    """Large validation pool, balanced per (retinue x MPC bucket), spanning ALL gear tiers and the
    full legal weapon/armor/shield cross — IGNORING retinue tier floors/caps (every retinue can take
    every tier, like the fullcross pool) so retinue effects can be compared cleanly.

    Tier-ceiling-independent-of-MPC: each build encodes a smithing stopping point (Furnace=Cast,
    Blacksmith=Wrought, Forge=Forged, ABF=Crafted) and an armor/shield stopping point via its pursuit
    set, then is padded with filler independent pursuits to hit the exact target MPC. So at a given MPC
    you get both "climbed smithing -> Forged/Crafted gear" and "stopped at Blacksmith -> Wrought-capped,
    spent MPC elsewhere" builds. Structural weapon rules (2H/OneShot/Lance/Crossbow) are always enforced
    via valid_combo; the retinue floor/cap is bypassed by passing retinue="Sergeant" to valid_combo for
    the structural check only (its floor is low enough not to block any tier here) then re-labeling.

    Args:
      per_cell: target builds per (retinue, MPC) cell. None = keep all legal, then the caller can
                stratify. An int caps each cell (random sample) for an exactly-balanced pool.
      keep_shield_tier_rule: OFF by default. The shield-tier>=weapon-tier rule was only ever a
                temporary pool-deflation device, NOT a real generation rule. Leave False for the
                full legal cross. (True is available only for legacy comparison.)

    Returns a list of Loadout. military_pursuit_count is the (filler-padded) target MPC.
    """
    import random as _random
    from collections import defaultdict
    rng = _random.Random(seed)
    RETS = ["Levy", "Man-at-Arms", "Sergeant", "Knight Templar"]

    # Smithing path -> (weapon tier unlocked, pursuit set, base MPC of the path)
    SMITH_PATHS = {
        "Crude":   ([], 0),
        "Cast":    (["Furnace"], 1),
        "Wrought": (["Blacksmith"], 1),
        "Forged":  (["Blacksmith", "Forge"], 1),          # efficiency line: total 1
        "Crafted": (["Blacksmith", "Forge", "ABF"], 1),   # total 1
    }
    # Armor/shield metal path -> pursuit set + base MPC. Joinery (cost 1) needed for any shield.
    # Tannery->Armory->Gilded Foundry is an efficiency line (total 1 from Tannery).
    METAL_PATHS = {
        None:            ([], 0),                                   # Cloth, no shield
        "Tannery":       (["Animal Husbandry", "Tannery"], 2),      # Leather; AH cost1 + Tannery cost1
        "Armory":        (["Animal Husbandry", "Tannery", "Armory"], 2),       # Chainmail
        "Gilded Foundry":(["Animal Husbandry", "Tannery", "Armory", "Gilded Foundry"], 2),  # Full Plate
        "ABF":           (["Animal Husbandry", "Tannery", "Armory", "Gilded Foundry", "ABF"], 2),  # Gothic Plate (Crafted armor) needs ABF
    }
    # Filler independent pursuits (cost 1 each, no tier effect) to pad MPC up to target.
    # Filler = cheap, build-agnostic pursuits used only to pad to a target MPC. EXCLUDED:
    #  - Outrider chain (Cipher Chamber, Caravanery, Outrider posts) — only built FOR the Outrider.
    #  - War College — its only effect is the Sergeant unlock; as filler it would convert random
    #    builds to Sergeant and skew the pool. Appears only on deliberately-built Sergeant loadouts.
    #  - Hospitaller — does nothing alone; only enters bundled with a regen stack (see below).
    #  - Apothecary — now a deliberate REGEN-TIER pursuit (regen axis below), not random filler.
    # FILLER (lowest priority): combat-tag specs a build takes with spare MPC. Coliseum REMOVED
    # (it's a retinue unlock now). Regen is handled separately via REGEN_LADDER (partial climb).
    FILLER = ["Master Workshop", "Toxicarium", "Stable", "Butchery", "Smokehouse"]
    FILLER = [f for f in FILLER if f in PURSUITS_INFO]

    armor_for_tier = {"Crude": "Cloth", "Cast": "Leather", "Wrought": "Chainmail",
                      "Forged": "Full Plate", "Crafted": "Gothic Plate"}
    shield_tiers = {None: None, "Crude": "Wooden Shield", "Cast": "Kite Shield",
                    "Wrought": "Scutum Shield", "Forged": "Tower Shield", "Crafted": "Heater Shield"}

    cells = defaultdict(list)   # (retinue, mpc) -> list of loadouts

    weapons_by_tier = defaultdict(list)
    for w, d in WEAPONS.items():
        weapons_by_tier[d["tier"]].append(w)
    ranged_by_tier = defaultdict(list)
    for r, d in RANGED.items():
        ranged_by_tier[d["tier"]].append(r)
    TIER_AT_OR_BELOW = {t: TIER_ORDER[:i + 1] for i, t in enumerate(TIER_ORDER)}

    def shield_options(weapon, smith_tier):
        # shields whose tier <= smith ceiling, plus None. Structural rules (2H, Lance, Crossbow)
        # are handled by valid_combo downstream.
        opts = [None]
        for st in TIER_AT_OR_BELOW[smith_tier]:
            sh = shield_tiers.get(st)
            if sh:
                opts.append(sh)
        return list(dict.fromkeys(opts))

    # Enumerate gear configs: weapon (any tier) x armor (ANY tier) x shield (ANY tier) — full legal
    # cross, tiers independent (a Forged weapon may pair with Cloth armor, etc.). The smith/metal
    # PURSUIT paths are derived later from whichever tiers the gear actually uses.
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
    # pure-ranged + dual-equip (need Tiltyard) — FULL cross for maximum gear coverage
    for ranged in RANGED:
        for armor_tier in TIER_ORDER:
            armor = armor_for_tier[armor_tier]
            # pure ranged (Farm Tools + ranged)
            if _structural_legal("Farm Tools", None, armor, ranged, has_tiltyard=True):
                gear_configs.append(("Farm Tools", None, armor, ranged))
            # dual-equip: EVERY melee weapon x EVERY shield x this ranged x this armor
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

    # For each gear config, derive the smith+metal pursuit base set from the tiers the gear USES,
    # pad with filler to each target MPC, emit one build per retinue.
    for (weapon, shield, armor, ranged) in gear_configs:
        # smith path = highest weapon/ranged tier present (weapons need the smithing line)
        wtier = WEAPONS[weapon]["tier"] if weapon in WEAPONS else "Crude"
        if ranged is not None:
            wtier = TIER_ORDER[max(TIER_IDX[wtier], TIER_IDX[RANGED[ranged]["tier"]])]
        smith_set, _ = SMITH_PATHS[wtier]
        atier = ARMORS[armor]["tier"]
        # METAL path is ARMOR-ONLY now (Gilded Foundry only for Full Plate, ABF only for Gothic).
        # Shields do NOT use the metal line — they use the SMITH line (below).
        metal_by_armor = {"Crude": None, "Cast": "Tannery", "Wrought": "Armory",
                          "Forged": "Gilded Foundry", "Crafted": "ABF"}
        metal_name = metal_by_armor[atier]
        metal_set = list(METAL_PATHS[metal_name][0]) if metal_name else []

        # SHIELD buildings: Joinery (+ Carpentry prereq) plus buildings by shield tier:
        #   Wooden = Joinery only
        #   Kite   = Joinery + Blacksmith
        #   Scutum = Joinery + Blacksmith + Armory
        #   Tower  = Joinery + Blacksmith + Forge
        #   Heater = Joinery + Blacksmith + ABF
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

        # Tiltyard line: a RANGED weapon still needs the tiltyard to be EQUIPPABLE (dual-equip
        # enabler), so ranged gear forces Tiltyard+Fletchery into the gear base. (Tiltyard also
        # appears as a Retinue Upgrade for melee builds — see UPGRADES below.)
        has_ty = ranged is not None
        ty_set = ["Carpentry", "Fletchery", "Coliseum", "Tiltyard"] if has_ty else []

        gear_base = set(smith_set) | set(metal_set) | set(shield_set) | set(ty_set)

        # ── CATEGORY DEFINITIONS ───────────────────────────────────────────────────────────────
        # Priority for filling MPC: Retinue Unlock >= Retinue Upgrade > Gear > Filler.
        # Retinue Unlock: the spec whose MASTERY unlocks the retinue (flat mastery_req, no cascade).
        RETINUE_UNLOCK = {"Levy": [], "Man-at-Arms": ["Coliseum"],
                          "Sergeant": ["War College"], "Knight Templar": ["Preceptory"]}
        # Retinue Upgrade: <=1 per build. Conditioning Field strongly preferred (>=2/3 of slots).
        # Preceptory here = the NON-KT innate-Unshakable case (KT gets it via unlock instead).
        # Tiltyard is NOT here — it's only for ranged+melee dual-equip (handled in the gear path).
        # Grand Tournament is a STANDALONE upgrade: its mastery (req Conditioning Field + Coliseum)
        # grants Riposte. It's also Royal Pavilion's prerequisite, so a build can take GT alone (Riposte,
        # no RP) OR go all the way to RP (Riposte + Drilled + Nimble). Including it here lets non-RP
        # builds carry Riposte.
        UPGRADES = ["Conditioning Field", "Royal Pavilion", "Ministry of Military Strategy",
                    "Outrider Intercept Post", "Preceptory", "Grand Tournament"]
        # Monuments get the 1/3-innate-only treatment (skip mastery_req → only innate fires) to expose
        # the innate-vs-mastery value jump. ABF excluded (its innate does nothing relevant).
        MONUMENTS_SPLIT = {"Royal Pavilion", "Ministry of Military Strategy", "Outrider Intercept Post", "Preceptory"}
        # Filler (lowest priority): Coliseum removed (it's a retinue unlock). Regen enters here as a
        # partial-tree climb (Apothecary→Infirmary→Hospitaller), stopping when MPC runs out.
        REGEN_LADDER = ["Apothecary", "Infirmary", "Hospitaller"]

        def flat_mastery_seed(spec):
            """spec + the pursuits named in its mastery_req (flat, no closure)."""
            s = {spec}
            if spec in PURSUITS_INFO:
                s |= set(PURSUITS_INFO[spec].get("mastery_req", []))
            return s

        for ret in RETS:
            # 1) RETINUE UNLOCK (mandatory). KT always MASTERS Preceptory (needs the KT unlock).
            unlock_seed = set()
            for u in RETINUE_UNLOCK[ret]:
                unlock_seed |= flat_mastery_seed(u)

            # 2) RETINUE UPGRADE: <=1. Conditioning Field >=2/3 of the time; else a random other
            #    upgrade. Each upgrade rolled across several builds so all appear in the data.
            for _u_try in range(3):   # a few upgrade variants per (gear,retinue) for sampling breadth
                if rng.random() < 2/3:
                    upgrade = "Conditioning Field"
                else:
                    upgrade = rng.choice([u for u in UPGRADES if u != "Conditioning Field"])
                # Preceptory upgrade only makes sense on NON-KT (KT already has it via unlock).
                if upgrade == "Preceptory" and ret == "Knight Templar":
                    upgrade = "Conditioning Field"

                # 1/3 of monument-upgrade builds are INNATE-ONLY (skip mastery_req). ABF/Cond Field
                # are not in MONUMENTS_SPLIT so they always master.
                innate_only = (upgrade in MONUMENTS_SPLIT) and (rng.random() < 1/3)
                if innate_only:
                    upgrade_seed = {upgrade}                       # innate only — no mastery_req
                else:
                    upgrade_seed = flat_mastery_seed(upgrade)      # innate + mastery

                base_seed_set = unlock_seed | upgrade_seed
                gear_full = master_effect_closure(prereq_closure(gear_base))
                base_set = gear_full | base_seed_set
                base_cost, _, _ = compute_pursuit_cost(base_set) if base_set else (0, {}, set())

                for target_mpc in range(mpc_min, mpc_max + 1):
                    if base_cost > target_mpc:
                        continue
                    # 3) FILLER (lowest priority): climb the regen ladder partially (Apothecary →
                    # Infirmary → Hospitaller, in order) then other filler, adding items one at a
                    # time and recomputing the ACTUAL closed cost (each regen spec pulls its economic
                    # mastery-req via closure, so cost can jump >1). Stop when we hit target_mpc.
                    regen_avail = [r for r in REGEN_LADDER if r not in base_set]
                    other_filler = [f for f in FILLER if f not in base_set]
                    rng.shuffle(other_filler)
                    menu = regen_avail + other_filler   # regen first so partial stacks are coherent
                    chosen = []
                    cur_cost = base_cost
                    for f in menu:
                        if cur_cost >= target_mpc:
                            break
                        trial = master_effect_closure(
                            prereq_closure(gear_base | set(chosen + [f]))) | base_seed_set
                        tc, _, _ = compute_pursuit_cost(trial)
                        if tc > target_mpc:
                            continue   # this item overshoots; try a cheaper one
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
                                 pursuits=pursuit_set)
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

    # Balance: optionally cap each (retinue, mpc) cell to per_cell via random sample.
    out = []
    for key, builds in cells.items():
        # dedupe by gear+tags+MPC within the cell
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


# Effect-bearing specs: their mastery grants a real combat TAG (not a tier/retinue marker). For a
# build that contains one of these, we pull its DIRECT mastery_req (one level, incl. economic specs
# like Herb Garden) so the mastery effect actually fires. Pure tier/retinue-unlock specs are NOT
# here — their "mastery" is the tier/retinue gate, handled separately.
_EFFECT_BEARING_MASTERY = {
    "Conditioning Field", "Ministry of Military Strategy", "Tiltyard", "Royal Pavilion",
    "Master Workshop", "Gilded Foundry", "Outrider Intercept Post",
    "Apothecary", "Infirmary", "Hospitaller", "Grand Tournament",
}


def master_effect_closure(pursuits):
    """For each effect-bearing spec present, add its DIRECT mastery_req specs (one level, no deeper
    chaining) so the spec's mastery tag fires. This is the ONLY route by which economic specs
    (Herb Garden, Alchemy, Grand Tournament, University) enter a combat build — and only to enable
    a mastery the build is meant to have. They then count toward MPC and total_investment.
    """
    out = set(pursuits)
    for p in list(out):
        if p in _EFFECT_BEARING_MASTERY and p in PURSUITS_INFO:
            for req in PURSUITS_INFO[p].get("mastery_req", []):
                out.add(req)   # direct only; do NOT recurse into req's own prereqs
    return out


def prereq_closure(pursuits):
    """Return the input set plus the transitive closure of COMBAT-RELEVANT prerequisites.

    Closure adds a prereq only if it is itself a combat spec (present in PURSUITS_INFO). Economic
    prereqs (Mine, Academy, Herb Garden, Monastery, ...) are the boundary: they gate the spec in
    the real game but the combat sim treats them as satisfied and never adds them to the build. So
    ABF pulls its combat chain (Blacksmith, Forge, Master Workshop, Gilded Foundry, Armory, Tannery,
    Stable) but NOT Mine/Animal Husbandry; Preceptory pulls nothing economic. Validity/presence
    only — the MPC discount in compute_pursuit_cost applies on top.
    """
    out = set(pursuits)
    changed = True
    while changed:
        changed = False
        for p in list(out):
            if p not in PURSUITS_INFO:
                continue
            for pre in PURSUITS_INFO[p].get("prereqs", []):
                if pre in PURSUITS_INFO and pre not in out:
                    out.add(pre)
                    changed = True
    return out


def validate_loadout(ld, check_tier_floors=False):
    """Check ONE loadout against the full rule set. Returns a list of violation strings (empty = valid).

    Validity is currently maintained by each generator's construction logic; there's no single gate
    every build passes through, so construction gaps (e.g. a shield routing through the wrong building
    line) slip through silently. This is that gate — run it over a pool to catch them automatically.

    Rules checked:
      STRUCTURAL (gear shape, always):
        - 2H weapon -> no shield; 1H (non-Farm Tools) -> needs shield unless Crossbow forces shieldless
        - Bastard Sword 1H -> needs shield
        - Lance/Cavalry Spear -> no Tower Shield
        - Crossbow -> Tower-only or shieldless; not with Lance/Cavalry Spear
        - One-Shot ranged / dual-equip -> requires Tiltyard
      BUILDING REQUIREMENTS (pursuits must back the gear tier):
        - Weapon tier -> smithing line present (Cast=Furnace, Wrought=Blacksmith, Forged=+Forge,
          Crafted=+ABF). Crude needs none.
        - Shield -> Joinery (+Carpentry) + buildings: Wooden=none, Kite=Blacksmith,
          Scutum=Blacksmith+Armory, Tower=Blacksmith+Forge, Heater=Blacksmith+ABF
        - Armor tier -> metal line: Cast=Tannery, Wrought=Armory, Forged=Gilded Foundry, Crafted=ABF
        - Ranged present -> Tiltyard line (Carpentry+Fletchery+Coliseum+Tiltyard)
      EFFICIENCY (no building you don't use):
        - No Fletchery / Tiltyard without a ranged weapon
        - Gilded Foundry only if armor is Full Plate or Gothic (armor-driven only; shields don't pull GF)
        - No shield -> no Joinery
      PREREQUISITES: every pursuit's prereqs must be present in the set.
      (check_tier_floors is retained for API compatibility but is a NO-OP — tier
        floors/caps are removed game-wide; gear is gated by infrastructure pursuits.)
    """
    v = []
    P = set(ld.pursuits)
    w, sh, ar, rg = ld.weapon, ld.shield, ld.armor, ld.ranged

    # ── Structural ──
    if w is not None and is_2h(w) and sh is not None:
        v.append(f"2H weapon {w} has shield {sh}")
    if (w not in (None, "Farm Tools") and not is_2h(w) and sh is None and rg != "Crossbow"):
        v.append(f"1H weapon {w} has no shield")
    if w == "Bastard Sword" and sh is None:
        v.append("Bastard Sword (1H) has no shield")
    if w in ("Lance", "Cavalry Spear") and sh == "Tower Shield":
        v.append(f"{w} cannot use Tower Shield")
    if rg == "Crossbow":
        if sh is not None and sh != "Tower Shield":
            v.append(f"Crossbow with non-Tower shield {sh}")
        if w in ("Lance", "Cavalry Spear"):
            v.append(f"Crossbow with {w}")
    if rg is not None and "One Shot" in RANGED.get(rg, {}).get("tags", []) and not ld.has_tiltyard:
        v.append(f"One-Shot ranged {rg} without Tiltyard")
    if w not in (None, "Farm Tools") and rg is not None and not ld.has_tiltyard:
        v.append(f"dual-equip ({w}+{rg}) without Tiltyard")

    # ── Building requirements ──
    SMITH_REQ = {"Crude": set(), "Cast": {"Furnace"}, "Wrought": {"Blacksmith"},
                 "Forged": {"Blacksmith", "Forge"}, "Crafted": {"Blacksmith", "Forge", "ABF"}}
    # weapon (and ranged) smithing: highest tier of the two must be backed
    wt = WEAPONS.get(w, {}).get("tier", "Crude") if w else "Crude"
    if rg is not None:
        rt = RANGED.get(rg, {}).get("tier", "Crude")
        if TIER_IDX[rt] > TIER_IDX[wt]:
            wt = rt
    # NOTE: a shield may legitimately supply Forge/ABF even for a lower-tier weapon, so the smithing
    # requirement is "the weapon-tier buildings are a subset of what's present", checked leniently.
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

    # ── Efficiency (no unused building) ──
    # Tiltyard (and its Fletchery prereq) normally require a ranged weapon. EXCEPTION: Royal Pavilion
    # masters via Grand Tournament + Tiltyard, so a mastered-RP melee build legitimately carries them.
    _rp_present = "Royal Pavilion" in P
    if "Fletchery" in P and rg is None and not _rp_present:
        v.append("Fletchery without a ranged weapon")
    if ld.has_tiltyard and rg is None and not _rp_present:
        v.append("Tiltyard without a ranged weapon")
    if "Gilded Foundry" in P and ar not in ("Full Plate", "Gothic Plate") and "ABF" not in P:
        # GF is legal for Full/Gothic Plate armor, OR as a prerequisite of ABF (Crafted gear).
        # Only flag it when neither justifies it.
        v.append(f"Gilded Foundry present but armor is {ar} and no ABF (unjustified)")

    # ── Prerequisites (combat-relevant only; economic prereqs are the closure boundary) ──
    # A pursuit present ONLY to satisfy another present spec's mastery_req (e.g. Hospitaller for
    # Preceptory's KT unlock) does NOT require its own prereqs — it can exist inert. Build the set
    # of such "present-for-mastery" pursuits: any pursuit named in the mastery_req of a spec that is
    # itself present in this build.
    present_for_mastery = set()
    for p in P:
        if p in PURSUITS_INFO:
            present_for_mastery |= set(PURSUITS_INFO[p].get("mastery_req", []))
    # Innate-only monuments: a monument present WITHOUT its mastery_req pursuits is "innate-only"
    # (it grants just its innate effect, which needs only a domain standing — NO buildings). So it
    # is exempt from its own prereq check too. Detect: a MONUMENT spec present whose mastery_req is
    # NOT fully satisfied in the build.
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
            continue   # present-for-mastery or innate-only monument — no own-prereq requirement
        for pre in PURSUITS_INFO[p].get("prereqs", []):
            if pre in PURSUITS_INFO and pre not in P:
                v.append(f"pursuit {p} missing prereq {pre}")

    # Tier floors/caps removed game-wide; check_tier_floors is a no-op.

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



    """Return a copy of `loadout` with a different playstyle (and updated name).
    Useful for one-off comparisons.
    """
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