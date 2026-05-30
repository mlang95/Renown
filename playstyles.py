"""
Playstyle module — playstyles drive tactic selection in combat.

A playstyle is a function that, given the current battle state, returns a probability
distribution over the 7 tactics: Scout, Ambush, Flank, Charge, Fighting Formation,
Defensive Formation, Fall Back.

The selection model is "two-tier 70/30": the primary tactic (or weighted set) is picked
~70% of the time, and the remaining 30% is spread across the other tactics. This mixes
intentional play with realistic player noise.

Adaptive playstyles inspect state (own size, opponent size, fatigue, etc.) and can shift
their preferred tactic mid-battle.

**Fall Back**: a tactical retreat. Versus Scout/Ambush/Defensive Formation/Fall Back, the
battle ENDS this skirmish (clean withdrawal). Versus Charge, you take -1I and +1 To Be Hit
(you get run down on the way out). Versus Fighting Formation, +1 To Be Hit. Versus Flank,
you actually do well (+1I, +1 To Hit). Strategy: use when you want to escape and the
opponent is unlikely to be pressing aggressively.

**Ministry of Military Strategy** (Sovereign Prowess monument, 200g, requires University + War College).

**Canonical design (final)**: **Once per battle, may pay Doubt 1** to have opponent reveal
their Tactic Card before you select yours. Modeled in sim as 'Ministry: once', which fires
on the first skirmish (the optimal skirmish to activate — charge bonuses and ranged volleys
land there).

The 'every' and 'first' variants are kept in the codebase for balance analysis only:
- `Ministry: every` was the initial reading — every skirmish gets counter-pick. Sim showed
  this produces ~65pt win-rate swings, more than 2x Preceptory's effect. Too strong.
- `Ministry: first` and `Ministry: once` are mechanically identical in sim (both fire only
  first skirmish). Both produce ~15pt swings, comparable to Preceptory's effect.

**Doubt cost is NOT modeled in combat sim** — it's a turn-level resource cost. When
interpreting `Ministry: once` results, remember the player must spend Doubt 1 per battle
to activate, creating Piety pressure.

**Mutual cancellation**: if both sides have the monument, neither effect fires (mutual reveal cancels).

Sim implementation: detect 'Ministry: <variant>' tag on loadout's extra_tags.

Engine integration: vectorized_combat.run_matchup_vec() accepts `a_playstyle` and
`b_playstyle` parameters. If None, falls back to uniform random (current behavior).
Ministry is engaged via the loadout's `extra_tags` containing 'Ministry of Strategy'
plus 'Ministry: every', 'Ministry: first', or 'Ministry: once' for the variant.
"""

import numpy as np
from renown_combat import TACTICS, TACTIC_MATRIX, RETINUES


# Indices for clarity
SCOUT, AMBUSH, FLANK, CHARGE, FIGHTING, DEFENSIVE, FALL_BACK = range(7)

TACTIC_NAMES = TACTICS  # alias for readability


# ==============================================================================
# Counter table — Ministry of Strategy uses this for counter-picking
# ==============================================================================

def _score_for_attacker(a_mods, b_mods):
    """Net advantage score for attacker. Higher = better outcome."""
    if a_mods.get('end') or b_mods.get('end'):
        return 0.0  # battle ends, neutral
    score = 0.0
    score += a_mods.get('I', 0) * 2.0
    score += a_mods.get('TH', 0) * 1.5
    score += a_mods.get('TBH', 0) * 1.5
    score += a_mods.get('TS', 0) * 1.5
    score -= b_mods.get('I', 0) * 2.0
    score -= b_mods.get('TH', 0) * 1.5
    score -= b_mods.get('TBH', 0) * 1.5
    score -= b_mods.get('TS', 0) * 1.5
    return score


def _rules_tactics(rules):
    return rules.tactics if rules is not None else TACTICS


def _rules_tactic_matrix(rules):
    return rules.tactic_matrix if rules is not None else TACTIC_MATRIX


def _rules_static_playstyles(rules):
    return rules.static_playstyles if rules is not None else STATIC_PLAYSTYLES


def _rules_adaptive_playstyles(rules):
    return rules.adaptive_playstyles if rules is not None else ADAPTIVE_PLAYSTYLES


def _rules_mechanics(rules):
    return getattr(rules, "mechanics", None)


def _build_counter_table(rules=None):
    """For each opponent tactic, return the index of the best counter-tactic."""
    tactics = _rules_tactics(rules)
    tactic_matrix = _rules_tactic_matrix(rules)
    table = np.zeros(7, dtype=np.int8)
    for opp_idx, opp_tac in enumerate(tactics):
        best_score = -1e9
        best_idx = 0
        for my_idx, my_tac in enumerate(tactics):
            key = (my_tac, opp_tac)
            if key not in tactic_matrix:
                continue
            a_mods, b_mods = tactic_matrix[key]
            s = _score_for_attacker(a_mods, b_mods)
            if s > best_score:
                best_score = s
                best_idx = my_idx
        table[opp_idx] = best_idx
    return table


# Lazily built so it reflects the current TACTIC_MATRIX
_counter_table_cache = None

def get_counter_table(rules=None):
    """Returns 1D int array [counter_for_opp_tac_0, ..., counter_for_opp_tac_6]."""
    if rules is not None:
        cached = getattr(rules, "_counter_table_cache", None)
        if cached is None:
            cached = _build_counter_table(rules)
            setattr(rules, "_counter_table_cache", cached)
        return cached
    global _counter_table_cache
    if _counter_table_cache is None:
        _counter_table_cache = _build_counter_table()
    return _counter_table_cache


def invalidate_counter_table(rules=None):
    if rules is not None:
        setattr(rules, "_counter_table_cache", None)
        return
    global _counter_table_cache
    _counter_table_cache = None


def ministry_counter_weights(opp_tac_idx, n_runs, counter_weight=None, rules=None):
    """Given the opponent's chosen tactic indices (shape n_runs), return weights for the
    Ministry-side tactic selection.
    
    counter_weight=0.8: 80% chance to play the optimal counter, 20% spread among the
    other 6 tactics. Returns shape (n_runs, 7).
    """
    if counter_weight is None:
        mech = _rules_mechanics(rules)
        counter_weight = mech.ministry_counter_weight if mech is not None else 0.8
    counters = get_counter_table(rules)  # int array of length 7
    counter_indices = counters[opp_tac_idx]  # shape (n_runs,)
    weights = np.full((n_runs, 7), (1 - counter_weight) / 6, dtype=np.float64)
    # Set the counter index to counter_weight for each run
    weights[np.arange(n_runs), counter_indices] = counter_weight
    return weights


def _weights_from_primaries(primaries, primary_weight=0.7):
    """Build a probability vector over 7 tactics.
    primaries: list of tactic indices. primary_weight is split evenly among them; remainder
    spread evenly across all other tactics.
    """
    n_tactics = 7
    w = np.zeros(n_tactics, dtype=np.float64)
    if not primaries:
        # No primary -> uniform random
        return np.full(n_tactics, 1/n_tactics, dtype=np.float64)
    per_primary = primary_weight / len(primaries)
    for p in primaries:
        w[p] = per_primary
    non_primary = [i for i in range(n_tactics) if i not in primaries]
    if non_primary:
        per_other = (1 - primary_weight) / len(non_primary)
        for i in non_primary:
            w[i] = per_other
    # Normalize for numeric safety
    return w / w.sum()


# ==============================================================================
# Static playstyles (no state-dependence)
# ==============================================================================
# Each is a dict with: name, primaries (list of indices), description.
# These are the "base" playstyles for non-adaptive selection.

STATIC_PLAYSTYLES = {
    "Random": {
        "primaries": [],   # uniform
        "description": "Uniform random — baseline (current engine behavior)",
        "good_for": "control / baseline",
        "initiate_rate": 0.50,  # 50/50 baseline
    },
    "Aggressor": {
        "primaries": [CHARGE, AMBUSH],
        "description": "Pushes initiative and to-hit. Good for high-AP weapons.",
        "good_for": "Poleaxe, Halberd, Bastard Sword. Front-loaded damage.",
        "initiate_rate": 0.80,  # aggressive — wants to attack
    },
    "Skirmisher": {
        "primaries": [SCOUT, FLANK],
        "description": "Flexible positioning, avoids committed fights.",
        "good_for": "Mobile light troops, weapons that benefit from initiative.",
        "initiate_rate": 0.55,  # opportunistic — flanks when advantageous
    },
    "Defender": {
        "primaries": [DEFENSIVE, FIGHTING],
        "description": "Maximize saves and survival. Best with heavy armor + shields.",
        "good_for": "Tower Shield turtles, Gothic Plate KT, attrition builds.",
        "initiate_rate": 0.30,  # turtle — prefers to be attacked
    },
    "Ranger": {
        "primaries": [AMBUSH, FLANK],
        "description": "First-skirmish punch via ranged volley + position.",
        "good_for": "Yew Heart, Tiltyard ranged builds.",
        "initiate_rate": 0.65,  # initiates often to leverage ranged volley
    },
    "Cavalry": {
        "primaries": [CHARGE],
        "description": "All-in on charge bonuses (Lance synergy).",
        "good_for": "Lance + Full Plate. Wins or dies on the charge.",
        "initiate_rate": 0.85,  # cavalry doctrine — charges
    },
    "Attritionist": {
        "primaries": [DEFENSIVE, SCOUT],
        "description": "Drag the fight out. Force fatigue on the opponent.",
        "good_for": "Pale Throne, Regen-stack builds, Unshakable armies.",
        "initiate_rate": 0.35,  # defensive — wants long battles on their terms
    },
    "Berserker": {
        "primaries": [CHARGE, AMBUSH],
        "description": "Maximum lethality on first skirmishes. Glass cannon.",
        "good_for": "Poleaxe Gothic, MW Weapons stacks. Win in 3 skirmishes or lose.",
        "initiate_rate": 0.90,  # all-in aggressive
    },
    "Cautious": {
        "primaries": [FALL_BACK, SCOUT],
        "description": "Fall Back as primary tactic. Never commits to a fight.",
        "good_for": "Sacrificial scout armies, decoys, harassment forces.",
        "initiate_rate": 0.20,  # deeply defensive — rarely initiates
    },
}


# ==============================================================================
# Adaptive playstyles — state-aware tactic selection
# ==============================================================================
# An adaptive playstyle returns a different primary set based on battle state.
# State is provided as numpy arrays of length n_runs (so the choice is per-run).
#
# Each adaptive returns: weights_array of shape (n_runs, 7).

def _broadcast_weights(weights_for_state, n_runs, condition_mask):
    """Given a per-state weight tuple list, broadcast to shape (n_runs, 7).
    weights_for_state: list of (mask, weights_7) pairs. Last entry should be the default.
    """
    out = np.zeros((n_runs, 7), dtype=np.float64)
    remaining = np.ones(n_runs, dtype=bool)
    for mask, w in weights_for_state:
        actual = mask & remaining
        out[actual] = w
        remaining = remaining & ~mask
    return out


def adaptive_finisher_weights(state, n_runs):
    """Aggressor that switches to all-Charge when opponent is at low retinues.
    Triggers: opponent size <= 15 retinues -> all-Charge.
    Otherwise: standard Aggressor (Charge/Ambush).
    """
    base = _weights_from_primaries([CHARGE, AMBUSH])
    finish = _weights_from_primaries([CHARGE], primary_weight=0.9)
    opp_low = state["b_size"] <= 15
    out = np.tile(base, (n_runs, 1))
    out[opp_low] = finish
    return out


def adaptive_patient_weights(state, n_runs):
    """Defender that presses when opponent is shaken or at low size.
    Triggers:
      - opponent at <=15 retinues OR fatigued (endurance == 0): switch to Aggressor
      - otherwise: Defender
    """
    base = _weights_from_primaries([DEFENSIVE, FIGHTING])
    press = _weights_from_primaries([CHARGE, AMBUSH])
    opp_weak = (state["b_size"] <= 15) | (state["b_end"] <= 0)
    out = np.tile(base, (n_runs, 1))
    out[opp_weak] = press
    return out


def adaptive_pressure_weights(state, n_runs):
    """Aggressor that switches to Defender when own endurance is critical.
    Use case: high-lethality builds (Poleaxe Gothic) that want to charge early
    but slow down when fatigue threatens their own survival.
    """
    base = _weights_from_primaries([CHARGE, AMBUSH])
    conserve = _weights_from_primaries([DEFENSIVE, FIGHTING])
    own_critical = state["a_end"] <= 1
    out = np.tile(base, (n_runs, 1))
    out[own_critical] = conserve
    return out


def adaptive_unshakable_weights(state, n_runs):
    """Attritionist that stays committed regardless of fatigue (because it can't Rout).
    Same as static Attritionist — listed here to clarify intent for Unshakable builds.
    """
    base = _weights_from_primaries([DEFENSIVE, SCOUT])
    out = np.tile(base, (n_runs, 1))
    return out


def adaptive_evasive_weights(state, n_runs):
    """Tries to Fall Back when in trouble.
    Triggers (escalating):
      - Critically low size (<= 8 retinues): all-in on Fall Back (90% weight)
      - Low size (<= 15 retinues) OR fatigued: heavy Fall Back (60% weight)
      - Otherwise: Skirmisher (Scout/Flank — avoid committed fights)

    Strategy: preserve the army; let the opponent commit to a chase if they want
    casualties. Pairs well with light/fast troops and Yew Heart factions.
    """
    skirmisher = _weights_from_primaries([SCOUT, FLANK])
    cautious_retreat = _weights_from_primaries([FALL_BACK, SCOUT], primary_weight=0.6)
    desperate_retreat = _weights_from_primaries([FALL_BACK], primary_weight=0.9)

    critical = state["a_size"] <= 8
    low = (state["a_size"] <= 15) | (state["a_end"] <= 0)
    out = np.tile(skirmisher, (n_runs, 1))
    out[low] = cautious_retreat
    out[critical] = desperate_retreat  # critical takes priority
    return out


def adaptive_opportunist_weights(state, n_runs):
    """Aggressor that Falls Back only when about to Rout.
    Triggers:
      - Own pre-tactic to-hit reaches Rout threshold (fatigue makes hit roll 7+):
        try to Fall Back to end the battle cleanly.
      - Otherwise: standard Aggressor.

    Use case: cheap troops that want to fight aggressively but escape before Rout fires.
    Note: this is a 'last chance' escape — once at Rout threshold, the next skirmish kills
    the army outright unless Fall Back resolves first.
    """
    aggressor = _weights_from_primaries([CHARGE, AMBUSH])
    last_chance = _weights_from_primaries([FALL_BACK], primary_weight=0.85)
    # The Rout threshold check: base to-hit + fatigue >= 7. Without knowing army to_hit
    # directly (it's in StaticArmy, not state), we approximate using fatigue level >= 2
    # (which would push most armies to 7+).
    high_fatigue = state["a_fat"] >= 2
    out = np.tile(aggressor, (n_runs, 1))
    out[high_fatigue] = last_chance
    return out


def adaptive_hit_and_run_weights(state, n_runs):
    """Skirmisher that Falls Back as soon as it's done meaningful damage.
    Triggers:
      - Opponent already reduced by >40% (we measure by absolute size <= 30):
        Fall Back to bank the win.
      - Otherwise: Skirmisher offense.

    Strategy: punch hard with Ambush/Flank, withdraw on a positive trade.
    Best for ranged builds (Yew Heart) and Levy/MaA armies that want clean wins.
    """
    skirmisher_aggressive = _weights_from_primaries([AMBUSH, FLANK])
    withdraw = _weights_from_primaries([FALL_BACK, SCOUT], primary_weight=0.65)
    # "Opponent meaningfully damaged" — heuristic threshold
    opp_damaged = state["b_size"] <= 30
    out = np.tile(skirmisher_aggressive, (n_runs, 1))
    out[opp_damaged] = withdraw
    return out


ADAPTIVE_PLAYSTYLES = {
    "Finisher": {
        "func": adaptive_finisher_weights,
        "description": "Aggressor that switches to all-Charge once opponent is low (<=15 retinues).",
        "good_for": "High-lethality builds that want to finish weakened enemies quickly.",
        "initiate_rate": 0.80,
    },
    "Patient": {
        "func": adaptive_patient_weights,
        "description": "Defender that presses (Charge/Ambush) when opponent is fatigued or low.",
        "good_for": "Heavy armor builds that wait for opponent to crack, then exploit.",
        "initiate_rate": 0.40,  # patient — picks fights only when ready
    },
    "Pressure": {
        "func": adaptive_pressure_weights,
        "description": "Aggressor that switches to Defender when own endurance critical.",
        "good_for": "Lethality builds (Poleaxe) that want to charge but not over-extend.",
        "initiate_rate": 0.75,
    },
    "Unshakable": {
        "func": adaptive_unshakable_weights,
        "description": "Attritionist with no fear of Rout. Stays Defensive.",
        "good_for": "Knight Templar, Pale Throne, Steadfast armies.",
        "initiate_rate": 0.35,  # defensive doctrine
    },
    "Evasive": {
        "func": adaptive_evasive_weights,
        "description": "Skirmisher that Falls Back when critically wounded (<=8) or fatigued.",
        "good_for": "Fragile armies preserving themselves. Yew Heart, Levy in horde mode.",
        "initiate_rate": 0.30,  # evades — rarely initiates
    },
    "Opportunist": {
        "func": adaptive_opportunist_weights,
        "description": "Aggressor that escapes via Fall Back when about to Rout (fatigue >=2).",
        "good_for": "Cheap troops that want aggressive trades but to escape before Rout fires.",
        "initiate_rate": 0.65,  # aggressive but has an exit
    },
    "Hit-and-Run": {
        "func": adaptive_hit_and_run_weights,
        "description": "Skirmisher (Ambush/Flank) that Falls Back when opponent is damaged (<=30).",
        "good_for": "Ranged builds and small armies banking positive trades.",
        "initiate_rate": 0.55,  # picks fights opportunistically
    },
}


ALL_PLAYSTYLES = list(STATIC_PLAYSTYLES.keys()) + list(ADAPTIVE_PLAYSTYLES.keys())


def get_initiate_rate(playstyle_name, rules=None):
    """Return the probability that a player with this playstyle initiates a battle
    (and thus typically gains Seize the Initiative). Defaults to 0.5 if unknown.

    Aggressive playstyles (Aggressor, Berserker, Cavalry) initiate ~75-90% of the time.
    Defensive playstyles (Defender, Cautious, Evasive, Attritionist) initiate ~20-35%.
    This drives the "who plays white" assignment in matchups when attacker_mode='playstyle'.
    """
    static_playstyles = _rules_static_playstyles(rules)
    adaptive_playstyles = _rules_adaptive_playstyles(rules)
    if playstyle_name is None or playstyle_name == "Random":
        return static_playstyles.get("Random", {}).get("initiate_rate", 0.50)
    if playstyle_name in static_playstyles:
        return static_playstyles[playstyle_name].get("initiate_rate", 0.50)
    if playstyle_name in adaptive_playstyles:
        return adaptive_playstyles[playstyle_name].get("initiate_rate", 0.50)
    return 0.50


# ==============================================================================
# Resolve playstyle to per-skirmish tactic weights
# ==============================================================================

def _apply_no_fb_rule(weights, n_runs):
    """Set Fall Back weight to 0 and redistribute proportionally across non-FB tactics."""
    out = weights.copy()
    non_fb_total = out[:, :6].sum(axis=1)
    safe_total = np.where(non_fb_total > 0, non_fb_total, 1.0)
    scale = 1.0 / safe_total
    out[:, :6] = out[:, :6] * scale[:, None]
    out[:, 6] = 0.0
    return out


def _apply_fatigue_fb_rule(weights, a_fat, n_runs, rules=None):
    """Re-shape a (n_runs, 7) weight matrix so each row uses the canonical
    fatigue-conditional Fall Back rule:
      fat == 0:  0% FB; row's FB weight goes to the other 6 tactics proportionally
      fat == 1:  15% FB; row's non-FB weights scaled so non-FB total = 85%
      fat >= 2:  40% FB; row's non-FB weights scaled so non-FB total = 60%
    Preserves each playstyle's distribution shape among non-FB tactics.
    """
    if np.isscalar(a_fat):
        a_fat = np.full(n_runs, a_fat, dtype=np.int8)
    mech = _rules_mechanics(rules)
    fat1_weight = mech.fatigue_fallback_weight_fat1 if mech is not None else 0.15
    fat2_weight = mech.fatigue_fallback_weight_fat2plus if mech is not None else 0.40

    target_fb = np.zeros(n_runs, dtype=np.float64)
    target_fb[a_fat == 1] = fat1_weight
    target_fb[a_fat >= 2] = fat2_weight

    out = weights.copy()
    non_fb_total = out[:, :6].sum(axis=1)
    target_non_fb_total = 1 - target_fb
    safe_total = np.where(non_fb_total > 0, non_fb_total, 1.0)
    scale = target_non_fb_total / safe_total
    out[:, :6] = out[:, :6] * scale[:, None]
    out[:, 6] = target_fb
    return out


# Playstyles that NEVER fall back — committed-to-the-fight personalities.
# Suppresses both the natural FB leak and the fatigue-triggered FB rule.
NEVER_FB_PLAYSTYLES = {
    "Aggressor", "Cavalry", "Berserker",        # static
    "Finisher", "Patient", "Pressure", "Unshakable",  # adaptive
}

# Playstyles that intentionally manage Fall Back in their own logic —
# exempt from any external FB adjustment.
FB_INTENTIONAL_PLAYSTYLES = {
    "Cautious",                                 # static (FB as primary)
    "Evasive", "Opportunist", "Hit-and-Run",    # adaptive (conditional FB)
}


def resolve_playstyle_weights(playstyle_name, state, n_runs, rules=None):
    """Return a weight array of shape (n_runs, 7) for the given playstyle and state.
    state: dict with keys 'a_size', 'b_size', 'a_end', 'b_end', 'a_fat', 'b_fat'.

    Three FB policy groups:
      1. NEVER_FB (Aggressor, Cavalry, Berserker, Finisher, Patient, Pressure,
         Unshakable): FB weight forced to 0 every skirmish — fight to the death.
      2. FB_INTENTIONAL (Cautious, Evasive, Opportunist, Hit-and-Run): playstyle's
         own logic manages FB; no external adjustment.
      3. Everything else (Random, Skirmisher, Defender, Ranger, Attritionist):
         apply the canonical fatigue-conditional rule (0% / 15% / 40% at fat 0/1/2+).
    """
    static_playstyles = _rules_static_playstyles(rules)
    adaptive_playstyles = _rules_adaptive_playstyles(rules)
    if playstyle_name is None or playstyle_name == "Random":
        # Random starts uniform over 6 non-FB tactics, then fatigue rule adds FB
        weights = np.zeros((n_runs, 7), dtype=np.float64)
        weights[:, :6] = 1 / 6
        return _apply_fatigue_fb_rule(weights, state["a_fat"], n_runs, rules=rules)

    if playstyle_name in static_playstyles:
        profile = static_playstyles[playstyle_name]
        if "weights" in profile:
            w = np.asarray(profile["weights"], dtype=np.float64)
            w = w / w.sum()
        else:
            primaries = profile["primaries"]
            w = _weights_from_primaries(primaries, profile.get("primary_weight", 0.7))
        weights = np.tile(w, (n_runs, 1))
        if profile.get("disable_fatigue_fallback", False):
            return weights
    elif playstyle_name in adaptive_playstyles:
        weights = adaptive_playstyles[playstyle_name]["func"](state, n_runs)
    else:
        raise ValueError(f"Unknown playstyle: {playstyle_name}")

    if playstyle_name in NEVER_FB_PLAYSTYLES:
        return _apply_no_fb_rule(weights, n_runs)
    if playstyle_name in FB_INTENTIONAL_PLAYSTYLES:
        return weights
    # Default: fatigue rule (same as Random)
    return _apply_fatigue_fb_rule(weights, state["a_fat"], n_runs, rules=rules)


def sample_tactic_indices(weights, rng):
    """Given weights of shape (n_runs, 7), sample one tactic index per run.
    Returns int8 array of shape (n_runs,).
    """
    cumw = np.cumsum(weights, axis=1)
    cumw[:, -1] = 1.0  # avoid numerical issues
    u = rng.random(weights.shape[0])
    idx = (u[:, None] < cumw).argmax(axis=1).astype(np.int8)
    return idx


# ==============================================================================
# Default playstyle assignment based on loadout properties
# ==============================================================================
# Used when generating a "playstyle-aware pool" — assigns each loadout its theoretically
# optimal playstyle based on its equipment/tags. This is the heuristic that powers
# `assign_default_playstyle()` and the playstyle-pool generator.

def assign_default_playstyle(loadout, rules=None):
    """Heuristic: given a loadout, return the best-fit playstyle name.

    Priority order (first match wins):
      1. Lance → Cavalry (all-in on charge bonuses)
      2. Pure-ranged (no melee weapon) → Ranger (NOT KT — KTs with no weapon
         are routed to Unshakable below, since the "no weapon" KT is a defensive
         attritionist by design)
      3. Knight Templar with defensive equipment → Unshakable
         (Tower Shield OR weapon=None — these are the equipment patterns where
         the rout-immunity stat compounds with attritional play)
      4. Tower Shield → Defender (non-KT turtle)
      5. Heavy armor + shield → Patient (defender with adaptive press)
      6. Poleaxe → Berserker (glass cannon, lethal 2H)
      7. Levy + light armor → Evasive (can't survive a stand-up fight; preserve via FB)
      8. MaA without Steadfast → Opportunist (can escape before Rout)
      9. Heavy 2H/1H melee → Aggressor (Halberd, Bastard, Battle Axe, War Hammer,
         Morningstar) — applies to KT, MaA, Sgt alike
      10. Fast/light melee → Skirmisher
      11. Default → Aggressor

    Design rationale for the KT routing change (was: ALL KT → Unshakable):
      The KT-only stratified tournament showed Unshakable wins for KTs only when
      paired with defensive-shaped equipment. For aggressive equipment (Poleaxe,
      Morningstar+Heater, Lance+Scutum), the equipment-natural playstyle outperformed
      Unshakable by 10-30pp. KT retains its rout-immunity stat regardless of playstyle,
      so an "aggressor KT" still benefits from being structurally unrouutable — it
      just plays the aggressor role instead of defensively.
    """
    tags = set(loadout.extra_tags)
    weapon = loadout.weapon
    armor = loadout.armor
    ret = loadout.retinue
    shield = loadout.shield

    # 1. Lance cavalry — Lance equipment is so specific to Charge that it overrides
    # retinue identity for everyone (KT/Lance still uses Cavalry).
    if weapon == "Lance":
        return "Cavalry"
    # 2. Pure-ranged non-KT build → Ranger. KTs with no weapon get routed to
    # Unshakable below (rule 3) — a no-weapon KT is a different beast from a no-weapon
    # MaA/Sgt because the KT can stand its ground indefinitely without routing.
    if weapon is None and ret != "Knight Templar":
        return "Ranger"
    # 3. Knight Templar with defensive equipment → Unshakable.
    # The equipment patterns that compound well with KT's rout-immunity are:
    #   - Tower Shield: heaviest defensive shield, attritional turtle
    #   - weapon=None: pure-ranged KT (already implicitly defensive — no melee press)
    # Other KT equipment (Poleaxe, Morningstar, Bastard, etc.) gets the equipment-
    # natural playstyle below, retaining the KT rout-immunity stat regardless.
    if ret == "Knight Templar" and (shield == "Tower Shield" or weapon is None):
        return "Unshakable"
    # 4. Tower Shield turtle (non-KT)
    if shield == "Tower Shield":
        return "Defender"
    # 5. Heavy armor + shield → Patient
    if armor in ("Full Plate", "Gothic Plate") and shield is not None:
        return "Patient"
    # 6. Poleaxe glass cannon
    if weapon == "Poleaxe":
        return "Berserker"
    # 7. Cheap fragile Levy → Evasive
    if ret == "Levy" and armor in ("Cloth", "Leather"):
        return "Evasive"
    # 8. MaA without Steadfast → Opportunist
    if ret == "Man-at-Arms" and "Steadfast" not in tags:
        return "Opportunist"
    # 9. Heavy 2H/1H melee → Aggressor
    if weapon in ("Halberd", "Bastard Sword", "Battle Axe", "War Hammer", "Morningstar"):
        return "Aggressor"
    # 10. Fast/light melee → Skirmisher
    if weapon in ("Short Sword", "Arming Sword", "Spears", "Cudgel", "Daggers", "Flail", "Pike"):
        return "Skirmisher"
    # 11. Default
    return "Aggressor"
