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

**Outrider Intercept Post** (Sovereign Cunning monument) — tactic-reveal. (The Ministry building now grants Seize only; the reveal mechanic moved here.)

**Canonical design (final)**: **Once per battle, may pay Doubt 1** to have opponent reveal
their Tactic Card before you select yours. Modeled in sim as 'Outrider: once', which fires
on the first skirmish (the optimal skirmish to activate — charge bonuses and ranged volleys
land there).

The 'every' and 'first' variants are kept in the codebase for balance analysis only:
- `Outrider: every` was the initial reading — every skirmish gets counter-pick. Sim showed
  this produces ~65pt win-rate swings, more than 2x Preceptory's effect. Too strong.
- `Outrider: first` and `Outrider: once` are mechanically identical in sim (both fire only
  first skirmish). Both produce ~15pt swings, comparable to Preceptory's effect.

**Doubt cost is NOT modeled in combat sim** — it's a turn-level resource cost. When
interpreting `Outrider: once` results, remember the player must spend Doubt 1 per battle
to activate, creating Piety pressure.

**Mutual cancellation**: if both sides have the monument, neither effect fires (mutual reveal cancels).

Sim implementation: detect 'Outrider: <variant>' tag on loadout's extra_tags.

Engine integration: vectorized_combat.run_matchup_vec() accepts `a_playstyle` and
`b_playstyle` parameters. If None, falls back to uniform random (current behavior).
Ministry is engaged via the loadout's `extra_tags` containing 'Ministry of Strategy'
plus 'Outrider: every', 'Outrider: first', or 'Outrider: once' for the variant.
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


def _build_counter_table():
    """For each opponent tactic, return the index of the best counter-tactic."""
    table = np.zeros(7, dtype=np.int8)
    for opp_idx, opp_tac in enumerate(TACTICS):
        best_score = -1e9
        best_idx = 0
        for my_idx, my_tac in enumerate(TACTICS):
            key = (my_tac, opp_tac)
            if key not in TACTIC_MATRIX:
                continue
            a_mods, b_mods = TACTIC_MATRIX[key]
            s = _score_for_attacker(a_mods, b_mods)
            if s > best_score:
                best_score = s
                best_idx = my_idx
        table[opp_idx] = best_idx
    return table


# Lazily built so it reflects the current TACTIC_MATRIX
_counter_table_cache = None

def get_counter_table():
    """Returns 1D int array [counter_for_opp_tac_0, ..., counter_for_opp_tac_6]."""
    global _counter_table_cache
    if _counter_table_cache is None:
        _counter_table_cache = _build_counter_table()
    return _counter_table_cache


def invalidate_counter_table():
    global _counter_table_cache
    _counter_table_cache = None


def outrider_counter_weights(opp_tac_idx, n_runs, counter_weight=0.8):
    """Given the opponent's chosen tactic indices (shape n_runs), return weights for the
    Ministry-side tactic selection.
    
    counter_weight=0.8: 80% chance to play the optimal counter, 20% spread among the
    other 6 tactics. Returns shape (n_runs, 7).
    """
    counters = get_counter_table()  # int array of length 7
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
        "description": "Drag the fight out, force fatigue on the opponent. Rewards heal-over-time.",
        "good_for": "Regenerate / Apothecary-Heal stacks (non-KT) — long battles maximize heal ticks.",
        "initiate_rate": 0.35,  # defensive — wants long battles on their terms
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


def adaptive_outrider_weights(state, n_runs):
    """Base distribution for an Outrider build on skirmishes where the counter-pick does NOT
    fire. Outrider's value is winning the REVEALED skirmish, so when not countering it plays a
    balanced engaging mix (Fighting Formation / Flank / Charge) that protects initiative and
    never retreats. Fall Back is forced to 0 by NEVER_FB membership; this just sets the engaging
    shape. Kept state-independent so the Outrider playstyle isolates the MONUMENT's effect rather
    than adding a second adaptive behavior on top.
    """
    w = _weights_from_primaries([FIGHTING, FLANK, CHARGE], primary_weight=0.75)
    return np.tile(w, (n_runs, 1))


def adaptive_skirmisher_weights(state, n_runs):
    """Scout/Flank offense that bails only when the army is about to be wiped.
    Lighter on Fall Back than Evasive (which also retreats when merely low or fatigued):
      - Critically low size (<= 8 retinues): heavy Fall Back (70% weight)
      - Otherwise: Skirmisher offense (Scout/Flank — avoid committed fights)

    Identity: stay mobile and keep fighting; only break off to avoid an outright wipe.
    """
    skirmisher = _weights_from_primaries([SCOUT, FLANK])
    bail = _weights_from_primaries([FALL_BACK, SCOUT], primary_weight=0.7)
    critical = state["a_size"] <= 8
    out = np.tile(skirmisher, (n_runs, 1))
    out[critical] = bail
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


def adaptive_vanguard_weights(state, n_runs):
    """Disciplined aggression — presses hard with INITIATIVE-SAFE tactics.

    The combat-sim finding: Charge and Ambush (the standard aggressive tactics) are exactly
    the ones that can LOWER your own initiative against the wrong counter (Charge → -1I/-1S
    into an Ambush). For a high-AP but initiative-fragile weapon (War Hammer init -1, Poleaxe
    init 0 with Immune-Steady stripping its floor), trading those tactics risks the -2 trip
    cliff where it can't strike at all — wasting its huge AP.

    Vanguard presses with Fighting Formation (disciplined, keeps +1TH, no init gamble) and
    Flank (gains init in most matchups), so the weapon stays aggressive AND keeps its
    initiative above the cliff. Like Pressure, it conserves (Defensive) when its own
    endurance is critical so it doesn't fatigue into Rout.

    Best for: War Hammer, Poleaxe, Battle Axe — high-AP crushers whose initiative is shaky
    and who therefore can't afford Charge's downside, but who must keep hitting.
    """
    press = _weights_from_primaries([FIGHTING, FLANK])          # aggressive, init-safe
    conserve = _weights_from_primaries([DEFENSIVE, FIGHTING])   # survive fatigue
    own_critical = state["a_end"] <= 1
    out = np.tile(press, (n_runs, 1))
    out[own_critical] = conserve
    return out


def adaptive_alpha_weights(state, n_runs):
    """Alpha-strike doctrine — for One-Shot ranged (Javelin, Pilum).

    One-Shot weapons fire ONCE, on the first skirmish, then the wielder is in melee with
    no further volley. So the build maximizes first-skirmish damage (Ambush/Charge to
    land the volley with a to-hit/initiative edge), then — volley spent — shifts to a
    defensive/positional stance to survive the melee it can no longer alpha.

    State proxy for "volley spent": after skirmish 1, own endurance has ticked down from
    its start. We approximate "first skirmish" as full endurance (a_end at max 3); once
    a_end < 3 the volley is gone and we play conservatively.

    Best for: Javelin (Wrought), Pilum (Crafted) — the One-Shot Unstoppable ranged.
    """
    alpha = _weights_from_primaries([AMBUSH, CHARGE])           # land the volley hard
    after = _weights_from_primaries([DEFENSIVE, FIGHTING])      # survive the melee after
    volley_spent = state["a_end"] < 3
    out = np.tile(alpha, (n_runs, 1))
    out[volley_spent] = after
    return out


def adaptive_anchor_weights(state, n_runs):
    """Anchor doctrine — for initiative-fragile heavies that must NOT drop to the trip floor.

    The initiative analysis established that init <= -2 = no strike back (a hard cliff),
    and that Gothic Plate (Immune Steady) STRIPS the Steady floor so slow/heavy weapons can
    be dragged below base init by enemy tactics. A build that is one tactic-swing away from
    the -2 cliff cannot afford to trade tactics that risk lowering its initiative — it plays
    Defensive/Fighting Formation to hold position and avoid being out-maneuvered to the floor,
    only pressing (Charge) once the opponent is weak enough that the exchange is safe.

    Best for: Poleaxe/Lance/Bastard in Gothic Plate (Immune Steady, no init floor), and
    other slow heavies whose initiative is precarious.
    """
    hold = _weights_from_primaries([FIGHTING, DEFENSIVE])      # hold initiative, don't get out-positioned
    press = _weights_from_primaries([CHARGE, AMBUSH])          # safe to commit once opp is weak
    opp_weak = (state["b_size"] <= 15) | (state["b_end"] <= 0)
    out = np.tile(hold, (n_runs, 1))
    out[opp_weak] = press
    return out


ADAPTIVE_PLAYSTYLES = {
    "Outrider": {
        "func": adaptive_outrider_weights,
        "description": "Outrider monument: counter-picks the revealed tactic; engaging mix otherwise. Never Falls Back.",
        "good_for": "Outrider Intercept Post builds — isolates the monument's counter-pick value.",
        "initiate_rate": 0.60,
    },
    "Skirmisher": {
        "func": adaptive_skirmisher_weights,
        "description": "Scout/Flank offense; Falls Back only when critically wounded (<=8) to avoid a wipe.",
        "good_for": "Mobile light troops, weapons that benefit from initiative.",
        "initiate_rate": 0.55,
    },
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
    "Alpha": {
        "func": adaptive_alpha_weights,
        "description": "Alpha-strike — maximizes the first-skirmish volley (One-Shot ranged), then plays defensively once the volley is spent.",
        "good_for": "Javelin, Pilum — One-Shot Unstoppable ranged.",
        "initiate_rate": 0.78,  # initiates to land the alpha volley
    },
    "Anchor": {
        "func": adaptive_anchor_weights,
        "description": "Initiative-protection — holds position (Fighting/Defensive) to avoid being dragged to the -2 trip floor, presses only when opponent is weak.",
        "good_for": "Low-AP init-fragile heavies (2HBastard in Full Plate) that can't punch through fast and must protect their initiative.",
        "initiate_rate": 0.45,  # measured — protects its initiative
    },
    "Vanguard": {
        "func": adaptive_vanguard_weights,
        "description": "Disciplined aggression — presses with initiative-safe tactics (Fighting/Flank) instead of Charge/Ambush, so a high-AP fragile-init weapon keeps hitting without risking the -2 cliff.",
        "good_for": "War Hammer, Poleaxe, Battle Axe — high-AP crushers with shaky initiative.",
        "initiate_rate": 0.70,  # aggressive but disciplined
    },
}


ALL_PLAYSTYLES = list(STATIC_PLAYSTYLES.keys()) + list(ADAPTIVE_PLAYSTYLES.keys())


def get_initiate_rate(playstyle_name):
    """Return the probability that a player with this playstyle initiates a battle
    (and thus typically gains Seize the Initiative). Defaults to 0.5 if unknown.

    Aggressive playstyles (Aggressor, Berserker, Cavalry) initiate ~75-90% of the time.
    Defensive playstyles (Defender, Cautious, Evasive, Attritionist) initiate ~20-35%.
    This drives the "who plays white" assignment in matchups when attacker_mode='playstyle'.
    """
    if playstyle_name is None or playstyle_name == "Random":
        return 0.50
    if playstyle_name in STATIC_PLAYSTYLES:
        return STATIC_PLAYSTYLES[playstyle_name].get("initiate_rate", 0.50)
    if playstyle_name in ADAPTIVE_PLAYSTYLES:
        return ADAPTIVE_PLAYSTYLES[playstyle_name].get("initiate_rate", 0.50)
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


def _apply_fatigue_fb_rule(weights, a_fat, n_runs):
    """Re-shape a (n_runs, 7) weight matrix so each row uses the canonical
    fatigue-conditional Fall Back rule:
      fat == 0:  0% FB; row's FB weight goes to the other 6 tactics proportionally
      fat == 1:  15% FB; row's non-FB weights scaled so non-FB total = 85%
      fat >= 2:  40% FB; row's non-FB weights scaled so non-FB total = 60%
    Preserves each playstyle's distribution shape among non-FB tactics.
    """
    if np.isscalar(a_fat):
        a_fat = np.full(n_runs, a_fat, dtype=np.int8)

    target_fb = np.zeros(n_runs, dtype=np.float64)
    target_fb[a_fat == 1] = 0.15
    target_fb[a_fat >= 2] = 0.40

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
    "Aggressor", "Cavalry",                            # static
    "Finisher", "Patient", "Pressure", "Unshakable",   # adaptive
    "Anchor", "Vanguard",                              # adaptive (committed)
    "Defender", "Ranger", "Attritionist",              # static — fight to the death (no FB)
    "Outrider",                                         # monument — never retreats; counter-picks instead
}

# Playstyles that intentionally manage Fall Back in their own logic —
# exempt from any external FB adjustment.
FB_INTENTIONAL_PLAYSTYLES = {
    "Evasive", "Opportunist", "Hit-and-Run", "Alpha",  # adaptive (conditional FB)
    "Skirmisher",                                       # adaptive (critical-only FB)
}


def resolve_playstyle_weights(playstyle_name, state, n_runs):
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
    if playstyle_name is None or playstyle_name == "Random":
        # Random: uniform over the 6 non-Fall-Back tactics. Fall Back is NOT used by Random
        # play — only playstyles that specifically manage it (Evasive/Cautious/Hit-and-Run/
        # Opportunist) ever choose it. No fatigue-conditional Fall Back here.
        weights = np.zeros((n_runs, 7), dtype=np.float64)
        weights[:, :6] = 1 / 6
        return weights

    if playstyle_name in STATIC_PLAYSTYLES:
        primaries = STATIC_PLAYSTYLES[playstyle_name]["primaries"]
        w = _weights_from_primaries(primaries)
        weights = np.tile(w, (n_runs, 1))
    elif playstyle_name in ADAPTIVE_PLAYSTYLES:
        weights = ADAPTIVE_PLAYSTYLES[playstyle_name]["func"](state, n_runs)
    else:
        raise ValueError(f"Unknown playstyle: {playstyle_name}")

    if playstyle_name in NEVER_FB_PLAYSTYLES:
        return _apply_no_fb_rule(weights, n_runs)
    if playstyle_name in FB_INTENTIONAL_PLAYSTYLES:
        return weights
    # Default: fatigue rule (same as Random)
    return _apply_fatigue_fb_rule(weights, state["a_fat"], n_runs)


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

def assign_default_playstyle(loadout):
    """Smart heuristic: map a loadout to its best-fit playstyle, using initiative,
    AP, armor, the new keywords (Unstoppable / Destroy Shield / One-Shot / Poison /
    Rend), and retinue. Grounded in the combat-sim findings:

      - Initiative is a CLIFF at -2 (init <= -2 = no strike back), not a slope. A build
        whose base init is precarious must play to protect it (Anchor).
      - AP saturates and can't crack shield walls; Destroy Shield / Unstoppable are the
        keywords that beat shields, so those weapons WANT to engage shielded heavies
        (Breaker), not skirmish.
      - One-Shot ranged (Javelin/Pilum) is pure alpha-strike: max first skirmish, then
        survive (Alpha).
      - KT rout-immunity compounds with attrition ONLY on defensive equipment; aggressive
        KT equipment plays its equipment-natural role and keeps the stat for free.

    Returns a playstyle name (static or adaptive). Adaptive playstyles are preferred where
    state-awareness helps; static where the build's plan is unconditional.
    """
    tags = set(loadout.extra_tags)
    weapon = loadout.weapon
    ranged = loadout.ranged
    armor = loadout.armor
    ret = loadout.retinue
    shield = loadout.shield

    # Pull stats for init/AP/keyword reasoning (from the live tables).
    try:
        from renown_combat import WEAPONS, RANGED, SHIELDS
    except Exception:
        WEAPONS = RANGED = SHIELDS = {}

    def _wstat(key, default=0):
        if weapon and weapon != "Farm Tools" and weapon in WEAPONS:
            return WEAPONS[weapon].get(key, default)
        if ranged and ranged in RANGED:
            return RANGED[ranged].get(key, default)
        return default

    w_tags = set(_wstat("tags", []))
    if ranged and ranged in RANGED:
        w_tags |= set(RANGED[ranged].get("tags", []))
    w_init = _wstat("init", 0)
    w_ap = _wstat("ap", 0)
    sh_init = SHIELDS[shield]["init"] if (shield and shield in SHIELDS) else 0
    base_init = w_init + sh_init

    has_unstoppable   = "Unstoppable" in w_tags
    has_destroy       = "Destroy Shield" in w_tags
    has_oneshot       = "One Shot" in w_tags
    has_shatter       = "Shatter Armor" in w_tags
    has_poison        = "Poison" in tags
    has_rend          = "Rend" in tags
    is_heavy_armor    = armor in ("Full Plate", "Gothic Plate")
    has_shield        = shield is not None

    # ── 0. Outrider Intercept Post → dedicated Outrider playstyle. The monument's value is the
    #     reactive counter-pick; this playstyle never Falls Back so the measured win rate reflects
    #     the monument, not a retreat behavior layered on top. Highest priority. ──
    if any(t.startswith("Outrider:") for t in tags):
        return "Outrider"

    # ── 1. One-Shot ranged → Alpha, but ONLY when the volley is the primary plan:
    #     pure-ranged (no melee) or a weak melee sidearm (AP > -3). A dual-equip build
    #     with a strong melee weapon (e.g. War Hammer + Javelin) should fire the volley
    #     then keep fighting with the real weapon — it falls through to the melee role
    #     below (Breaker/Pressure/etc.), not Alpha's volley-then-turtle. ──
    if has_oneshot and (weapon is None or weapon == "Farm Tools" or w_ap > -3):
        return "Alpha"

    # ── 2. Lance → Cavalry (Lance is so Charge-specific it overrides everything else). ──
    if weapon == "Lance":
        return "Cavalry"

    # ── 3. Pure-ranged (no melee) → Ranger (non-KT) / Unshakable (KT attritionist). ──
    if weapon is None and not ranged:
        # truly weaponless: defensive attritionist
        return "Unshakable" if ret == "Knight Templar" else "Ranger"
    if weapon is None and ranged:
        # sustained ranged (not One-Shot — that's caught above): volley + reposition
        return "Unshakable" if ret == "Knight Templar" else "Ranger"

    # ── 4. (Shield-breaking is an equipment EFFECT, not a playstyle.) Destroy Shield /
    #     Unstoppable weapons (War Hammer, Morningstar, Battle Axe, Poleaxe — note Poleaxe
    #     has Unstoppable, ignoring the shield's -1TBH, but NOT Destroy Shield) do their
    #     shield-cracking automatically in combat resolution regardless of tactics. Against
    #     a non-shield target they behave like any aggressive crusher. So they get NO special
    #     playstyle here — they route to the normal AP-based aggressive roles below
    #     (Pressure for high-AP 2H that must manage endurance, else Aggressor). ──

    # ── 5. Knight Templar with DEFENSIVE equipment → Unshakable. Rout-immunity compounds
    #     with attrition only on defensive shapes (Tower, or weaponless handled above). ──
    if ret == "Knight Templar" and shield == "Tower Shield":
        return "Unshakable"

    # ── 6. Initiative-fragile heavy. A slow/heavy weapon whose base init is precarious
    #     (<= 0) AND which lacks a Steady floor (no Steady tag, or Gothic Plate strips it via
    #     Immune Steady) can be dragged to the -2 trip cliff where it can't strike. Split by
    #     offensive power:
    #       - HIGH-AP crusher (AP <= -4): its whole value is the big AP, so it MUST keep
    #         hitting — press with initiative-SAFE tactics (Fighting/Flank) → Vanguard.
    #       - LOW-AP fragile (AP > -4): can't punch through fast anyway → protect the floor
    #         defensively → Anchor.
    # NOTE: Gothic Plate no longer strips Steady (Immune Steady deprecated). A Steady weapon
    # keeps its init-floor in any armor, so steady_floor depends only on the weapon's tags.
    steady_floor = ("Steady" in w_tags)
    init_fragile_heavy = is_heavy_armor and base_init <= 0 and not steady_floor and not has_shield
    if init_fragile_heavy:
        return "Vanguard" if w_ap <= -4 else "Anchor"

    # ── 6b. Heal-over-time stacks (Regenerate / Apothecary Heal), non-KT, no shield →
    #     Attritionist. These builds gain value from LONG battles (more heal ticks), so they
    #     drag the fight out and force fatigue rather than ending it fast. Checked before the
    #     aggressive fallbacks so a regen build isn't sent to Aggressor (which wastes heal).
    #     KT heal-stacks use Unshakable; shielded heal-stacks use Patient/Defender below. ──
    has_heal = ("Apothecary Heal" in tags) or any("Regenerate" in t for t in tags)
    if has_heal and ret != "Knight Templar" and not has_shield:
        return "Attritionist"

    # ── 7. Tower Shield turtle (non-KT) → Defender. ──
    if shield == "Tower Shield":
        return "Defender"

    # ── 8. Heavy armor + shield → Patient (defend, then exploit when opponent cracks). ──
    if is_heavy_armor and has_shield:
        return "Patient"

    # ── 9. High-AP heavy 2H melee → Pressure (charge early, conserve when own endurance
    #     drops so the lethal weapon doesn't over-extend into fatigue/Rout). ──
    if w_ap <= -4 and "2H" in w_tags:
        return "Pressure"

    # ── 10. Cheap fragile Levy in light armor → Evasive (can't win a stand-up fight). ──
    if ret == "Levy" and armor in ("Cloth", "Leather"):
        return "Evasive"

    # ── 11. MaA without Steadfast → Opportunist (aggressive trades, escape before Rout). ──
    if ret == "Man-at-Arms" and "Steadfast" not in tags:
        return "Opportunist"

    # ── 12. Heavy melee (good AP) → Aggressor. ──
    if w_ap <= -3:
        return "Aggressor"

    # ── 13. Fast/light melee → Skirmisher (positioning over committed fights). ──
    if base_init >= 1 or weapon in ("Short Sword", "Arming Sword", "Spears", "Cudgel",
                                     "Daggers", "Flail", "Pike"):
        return "Skirmisher"

    # ── 14. Default → Aggressor. ──
    return "Aggressor"
