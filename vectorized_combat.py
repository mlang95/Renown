"""
Vectorized matchup runner.

Runs N battles of a single matchup in parallel using numpy. State is held as
arrays of shape (N,) representing the per-run battle state. All die rolls,
tactic picks, and casualty math are vectorized across the N runs.

Drop-in replacement for the loop-based run_matchup in tournament.py:
    from vectorized_combat import run_matchup_vec
    result = run_matchup_vec(ld_a, ld_b, n_runs=100)
"""

import numpy as np
from renown_combat import (
    RETINUES, WEAPONS, RANGED, SHIELDS, ARMORS,
    TACTIC_MATRIX, TACTICS,
)


# ===== Precomputed tactic tables (built lazily on first use) =====

_tactic_tables = None

def _build_tactic_tables():
    """Return dict of 7x7 numpy arrays indexed by (a_tac_idx, b_tac_idx)."""
    n = len(TACTICS)
    a_I  = np.zeros((n, n), dtype=np.int8)
    a_TH = np.zeros((n, n), dtype=np.int8)
    a_TS = np.zeros((n, n), dtype=np.int8)
    b_I  = np.zeros((n, n), dtype=np.int8)
    b_TH = np.zeros((n, n), dtype=np.int8)
    b_TS = np.zeros((n, n), dtype=np.int8)
    end  = np.zeros((n, n), dtype=bool)
    no_combat = np.zeros((n, n), dtype=bool)
    # For no_combat cells, whether endurance is still spent this skirmish.
    # Default True for safety; Scout/Scout and Ambush/Ambush set False.
    no_combat_endurance = np.zeros((n, n), dtype=bool)
    for i, t_a in enumerate(TACTICS):
        for j, t_b in enumerate(TACTICS):
            a_mods, b_mods = TACTIC_MATRIX[(t_a, t_b)]
            a_I[i, j]  = a_mods["I"]
            a_TH[i, j] = a_mods["TH"]
            a_TS[i, j] = a_mods["TS"]
            b_I[i, j]  = b_mods["I"]
            b_TH[i, j] = b_mods["TH"]
            b_TS[i, j] = b_mods["TS"]
            end[i, j]  = a_mods.get("end", False) or b_mods.get("end", False)
            no_combat[i, j] = a_mods.get("no_combat", False) or b_mods.get("no_combat", False)
            # endurance_loss only matters if no_combat fired. If EITHER side flagged
            # endurance_loss=True for this no_combat cell, troops still spend endurance.
            no_combat_endurance[i, j] = no_combat[i, j] and (
                a_mods.get("endurance_loss", True) or b_mods.get("endurance_loss", True)
            )
    return {
        "a_I": a_I, "a_TH": a_TH, "a_TS": a_TS,
        "b_I": b_I, "b_TH": b_TH, "b_TS": b_TS,
        "end": end,
        "no_combat": no_combat,
        "no_combat_endurance": no_combat_endurance,
    }


def get_tactic_tables():
    """Build (and cache) tactic mod lookup tables. Call invalidate_tactic_tables() after editing TACTIC_MATRIX."""
    global _tactic_tables
    if _tactic_tables is None:
        _tactic_tables = _build_tactic_tables()
    return _tactic_tables


def invalidate_tactic_tables():
    """Force rebuild on next use. Call this after installing the normalized matrix."""
    global _tactic_tables
    _tactic_tables = None


# ===== Loadout → static stats =====

class StaticArmy:
    """Bundles a Loadout's static-per-run stats for the inner loop."""
    def __init__(self, loadout, is_attacker):
        ld = loadout
        ret = RETINUES[ld.retinue]
        self.size_start = ld.size
        self.to_hit = ret["to_hit"]
        # Conditioning Field mastery: +1 Max Endurance
        endurance_bonus = 1 if "Cond Field" in ld.extra_tags else 0
        self.endurance_start = ret["endurance"] + endurance_bonus
        self.shaking = ret["shaking"]
        self.unshakable = ret["unshakable"]
        self.armor_save = ARMORS[ld.armor]["save"]
        # Shield can be destroyed mid-battle; track shield_bonus as starting value
        self.shield_bonus_start = SHIELDS[ld.shield]["save_bonus"] if ld.shield else 0
        # Shield -1TBH (Scutum, Tower, Heater): attacker must roll +1 higher to
        # hit this unit. Stored as a positive value (attacker's target_th +=
        # this). Disappears if shield is destroyed.
        shield_tags = SHIELDS[ld.shield]["tags"] if ld.shield else []
        self.shield_tbh_penalty_start = 1 if "-1TBH" in shield_tags else 0
        self.has_shield = ld.shield is not None
        # Immune Destroy Shield (Heater): this shield cannot be destroyed by Destroy Shield.
        self.shield_immune = "Immune Destroy Shield" in shield_tags
        self.is_attacker = is_attacker
        self.has_tiltyard = ld.has_tiltyard
        self.ranged = ld.ranged
        # Master Workshop mastery: -1 AP to weapons (more lethal)
        mw_bonus = -1 if "MW Weapons" in ld.extra_tags else 0
        # Gilded Foundry mastery: -1 AP from incoming strikes (better effective save)
        self.gf_armor = "GF Armor" in ld.extra_tags
        # Yew Heart faction: ranged weapons gain +1 to Hit
        self.yew_heart = "Yew Heart" in ld.extra_tags
        # ── Weapon resolution ──────────────────────────────────────────
        # Renown rules:
        # 1. Every soldier carries Farm Tools as a baseline fallback (used when
        #    no real melee is equipped, e.g. pure-ranged loadouts).
        # 2. Ranged weapons fire skirmish 1. Multi-shot bows (no "One Shot" tag)
        #    fire every skirmish if no separate melee competes for hands.
        #    One-Shot ranged (Javelin, Pilum) fires once.
        # 3. Dual-equip (real melee + ranged) REQUIRES Tiltyard.
        #    - With Tiltyard + one-shot ranged: S1 = volley, S2+ = real melee
        #    - Without Tiltyard + one-shot ranged: only the one-shot is carried;
        #      after S1, fall back to Farm Tools (no real melee available)
        # 4. tiltyard_mastery distinguishes innate Tiltyard (Unwieldy applies)
        #    from mastered Tiltyard (Immune Unwieldy). Defaults to True.
        melee_weapon_name = ld.weapon if ld.weapon else "Farm Tools"
        melee_profile = WEAPONS[melee_weapon_name]
        # Bastard Sword has two profiles:
        #   - With shield (1H mode): the WEAPONS['Bastard Sword'] entry (Shatter Armor, Steady)
        #   - 2H mode: the WEAPONS['2HBastard'] entry (Cleave, Unwieldy, 2H)
        # Plain 'Bastard Sword' requires a shield and fights 1H; if the shield is destroyed
        # mid-battle it switches to the 2HBastard profile (per-run, in the skirmish loop).
        # The standalone '2HBastard' weapon is always-2H from the start.
        # Sourcing the 2H profile from the dict (not inline) lets it be tuned in renown_combat.py.
        _bastard_2h = WEAPONS.get("2HBastard", {
            "ap": -3, "init": 0, "tags": ["Cleave", "Unwieldy", "2H"], "tier": "Forged"})
        self.is_bastard_dual_profile = (melee_weapon_name == "Bastard Sword" and ld.shield is not None)
        bastard_2h_profile = None
        if melee_weapon_name == "Bastard Sword" and ld.shield is None:
            # (Should not occur once the generator requires a shield for plain Bastard,
            #  but kept defensive: a shieldless 'Bastard Sword' fights as 2HBastard.)
            melee_profile = dict(_bastard_2h)
        elif self.is_bastard_dual_profile:
            # Keep 1H profile as primary; precompute the 2H profile for per-run fallback.
            bastard_2h_profile = dict(_bastard_2h)
        has_real_melee = ld.weapon is not None and ld.weapon != "Farm Tools"

        if ld.ranged:
            ranged_profile = RANGED[ld.ranged]
            ranged_is_one_shot = "One Shot" in ranged_profile["tags"]
        else:
            ranged_profile = None
            ranged_is_one_shot = False

        # Tiltyard mastery: only meaningful when has_tiltyard is True
        tiltyard_mastery = getattr(ld, 'tiltyard_mastery', True) and ld.has_tiltyard

        # Pure-ranged loadout: multi-shot ranged + no real melee.
        # Use ranged stats every skirmish.
        is_pure_ranged_multi = (ld.ranged is not None
                                and not ranged_is_one_shot
                                and not has_real_melee)

        # Tiltyard adaptive flag (used by run_matchup_tiltyard_adaptive wrapper).
        # Only meaningful when dual-equipped with mastery.
        self.tiltyard_adaptive = (has_real_melee
                                  and ld.ranged is not None
                                  and tiltyard_mastery)

        # First-skirmish stats
        if ld.ranged:
            self.ap_first = ranged_profile["ap"] + mw_bonus
            self.init_first = ranged_profile["init"]
            self.tags_first = self._compute_tags(ranged_profile, ld.shield, ld, has_both=has_real_melee, first=True)
        else:
            self.ap_first = melee_profile["ap"] + mw_bonus
            self.init_first = melee_profile["init"]
            self.tags_first = self._compute_tags(melee_profile, ld.shield, ld, has_both=False, first=True)

        # Normal-skirmish stats (skirmishes 2+)
        if is_pure_ranged_multi:
            # Multi-shot bow keeps firing — ranged stats for every skirmish
            self.ap_normal = ranged_profile["ap"] + mw_bonus
            self.init_normal = ranged_profile["init"]
            self.tags_normal = self._compute_tags(ranged_profile, ld.shield, ld, has_both=False, first=False)
        else:
            # Standard: melee for S2+. This covers:
            #   - Melee-only: use melee weapon every skirmish
            #   - One-shot + Tiltyard + real melee: S2+ uses real melee
            #   - One-shot without real melee (Farm Tools + one-shot): S2+ uses
            #     Farm Tools (melee_weapon_name resolves to Farm Tools in that case)
            self.ap_normal = melee_profile["ap"] + mw_bonus
            self.init_normal = melee_profile["init"]
            self.tags_normal = self._compute_tags(melee_profile, ld.shield, ld, has_both=bool(ld.ranged) and has_real_melee, first=False)
        # ───────────────────────────────────────────────────────────────
        # Bastard dual: precompute the 2H tag sets for per-run override
        # when the shield is destroyed mid-battle.
        if self.is_bastard_dual_profile and bastard_2h_profile is not None:
            # 2H mode: no shield (so don't include shield tags), no shield save bonus
            self.tags_first_2h = self._compute_tags(bastard_2h_profile, None, ld, has_both=False, first=True)
            self.tags_normal_2h = self._compute_tags(bastard_2h_profile, None, ld, has_both=False, first=False)
        else:
            self.tags_first_2h = None
            self.tags_normal_2h = None
        # Convenience: derived flags for the inner loop
        self.shield_init = SHIELDS[ld.shield]["init"] if ld.shield else 0

    @staticmethod
    def _compute_tags(weapon_profile, shield_name, ld, has_both, first):
        tags = set(weapon_profile["tags"]) | set(ld.extra_tags)
        if shield_name:
            tags |= set(SHIELDS[shield_name]["tags"])
        # Armor-granted initiative tags (Full Plate: Immune Nimble; Gothic: + Immune Steady)
        tags |= set(ARMORS[ld.armor].get("tags", []))
        # Dual-equip Unwieldy: applies when carrying BOTH a real melee weapon
        # (not Farm Tools) AND a ranged weapon AND Tiltyard is innate (not mastered).
        # Tiltyard mastery grants Immune Unwieldy. Without any Tiltyard, dual-equip
        # isn't possible (enforced at loadout filter), so this branch only fires
        # for Tiltyard-innate loadouts.
        has_real_melee = ld.weapon is not None and ld.weapon != "Farm Tools"
        tiltyard_is_mastery = ld.has_tiltyard and getattr(ld, 'tiltyard_mastery', True)
        if has_both and has_real_melee and ld.ranged and not tiltyard_is_mastery:
            if "Immune Unwieldy" not in ld.extra_tags:
                tags.add("Unwieldy")
        if "Immune Unwieldy" in ld.extra_tags:
            tags.discard("Unwieldy")
        # Immune Steady (heavy armor) cancels the weapon's Steady init-floor.
        if "Immune Steady" in tags:
            tags.discard("Steady")
        return tags

    def base_init(self, first):
        i = self.init_first if first else self.init_normal
        i += self.shield_init
        tags = self.tags_first if first else self.tags_normal
        # Nimble grants +1 first-skirmish init — unless suppressed by Immune Nimble (heavy armor).
        if "Nimble" in tags and "Immune Nimble" not in tags and first:
            i += 1
        if self.is_attacker and first:
            i += 1
        return i

    def weapon_ap(self, first):
        return self.ap_first if first else self.ap_normal

    def tags(self, first):
        return self.tags_first if first else self.tags_normal


# ===== Vectorized strike resolution =====

def _roll_strikes_vec(rng, n, target_th, front_line, atk_tags, defender_has_shield_flag,
                     defender_shield_destroyed, atk_bastard_2h_mask=None, atk_tags_2h=None,
                     defender_shield_immune=False):
    """For each of n runs, roll up to 20 dice (front_line per run cap), count strikes.
    Returns: strikes (n,), shatter_strikes (n,), cleave_extra (n,), destroyed_shield (n,)

    If atk_bastard_2h_mask is provided, runs where the mask is True use atk_tags_2h
    instead of atk_tags for Shatter Armor/Cleave/Destroy Shield checks (i.e., the
    Bastard wielder has switched to 2H mode because their shield was destroyed).

    defender_shield_immune: if True, the defender's shield carries "Immune Destroy Shield"
    (e.g. Heater) and cannot be destroyed — the Destroy Shield keyword has no effect on it.
    """
    # Auto-fail: if target_th > 6, no strikes possible
    # Auto-pass: if target_th < 2, every die in use is a guaranteed strike
    # (mirrors save behavior — symmetric extremes).
    target_th_orig = target_th
    target_th = np.clip(target_th, 2, 7)  # 7 means auto-fail
    auto_fail = target_th >= 7
    auto_pass = target_th_orig < 2  # per-run boolean: this run's hits all land

    # Roll 20 dice per run (max front line size). Mask out runs where target is auto-fail.
    rolls = rng.integers(1, 7, size=(n, 20), dtype=np.int8)  # 1..6 inclusive
    # die_index < front_line per run determines which dice "count"
    die_idx = np.arange(20)[None, :]  # (1, 20)
    die_in_use = die_idx < front_line[:, None]  # (n, 20)

    # A die is a strike if (auto-pass for the run) OR (roll >= target AND not auto-fail);
    # always requires die_in_use.
    is_strike = die_in_use & (
        auto_pass[:, None]
        | ((rolls >= target_th[:, None]) & (~auto_fail[:, None]))
    )
    strikes = is_strike.sum(axis=1).astype(np.int32)

    # Strike-related sixes for keyword effects (Shatter, Cleave, Destroy Shield).
    # Even when auto-passing, dice are still rolled to check for natural 6s — these
    # are the "crit" triggers and only fire on actual 6 rolls (not bonus auto-strikes).
    is_six = (rolls == 6) & is_strike
    six_count = is_six.sum(axis=1).astype(np.int32)

    has_dual = atk_bastard_2h_mask is not None and atk_tags_2h is not None

    # Shatter Armor: 1H Bastard has it, 2H Bastard doesn't.
    if has_dual:
        shatter_base = ("Shatter Armor" in atk_tags)
        shatter_2h = ("Shatter Armor" in atk_tags_2h)
        # Per-run: True if THIS run's mode has Shatter
        run_has_shatter = np.where(atk_bastard_2h_mask, shatter_2h, shatter_base)
        shatter_strikes = np.where(run_has_shatter, six_count, 0).astype(np.int32)
    elif "Shatter Armor" in atk_tags:
        shatter_strikes = six_count
    else:
        shatter_strikes = np.zeros(n, dtype=np.int32)

    # Cleave: 2H Bastard has it, 1H Bastard doesn't.
    if has_dual:
        cleave_base = ("Cleave" in atk_tags)
        cleave_2h = ("Cleave" in atk_tags_2h)
        run_has_cleave = np.where(atk_bastard_2h_mask, cleave_2h, cleave_base)
        cleave_extra = np.where(run_has_cleave, six_count, 0).astype(np.int32)
    elif "Cleave" in atk_tags:
        cleave_extra = six_count
    else:
        cleave_extra = np.zeros(n, dtype=np.int32)

    # Destroy Shield: any 6 destroys defender's shield (if not already destroyed,
    # and not immune — Heater's "Immune Destroy Shield" cannot be broken).
    destroyed_shield = np.zeros(n, dtype=bool)
    if "Destroy Shield" in atk_tags and defender_has_shield_flag and not defender_shield_immune:
        any_six = is_six.any(axis=1)
        destroyed_shield = any_six & (~defender_shield_destroyed)

    return strikes + cleave_extra, shatter_strikes, destroyed_shield


def _regen_threshold(def_tags, atk_tags=None):
    """Return the defender's Regenerate save threshold (4, 5, or 6), or None if no Regenerate.
    Tags can be 'Regenerate' (=6), 'Regenerate 6', 'Regenerate 5', or 'Regenerate 4'.
    If multiple are present, the lowest threshold (strongest) wins.

    Rend (attacker keyword): worsens the defender's regenerate save by 1 (higher threshold),
    capped at 7+ — a 7+ regen save is impossible on a d6, so Rend can fully negate Regenerate.
    Each Rend on the attacker adds +1 (stacking), clamped to 7.
    """
    thresholds = []
    for t in def_tags:
        if t == "Regenerate" or t == "Regenerate 6":
            thresholds.append(6)
        elif t == "Regenerate 5":
            thresholds.append(5)
        elif t == "Regenerate 4":
            thresholds.append(4)
    if not thresholds:
        return None
    thr = min(thresholds)
    if atk_tags is not None:
        rend = sum(1 for t in atk_tags if t == "Rend")
        if rend:
            thr = min(7, thr + rend)
    return thr


def _has_regen_reroll(tags):
    """Hospitaller mastery — re-roll failed Regenerate rolls."""
    return "Regenerate Reroll" in tags


def _roll_saves_vec(rng, n, save_target, n_strikes, shatter_strikes, atk_has_poison, def_has_parry, def_regen_threshold, def_has_regen_reroll):
    """For each of n runs with n_strikes hits to resolve, return casualties (n,).
    Saves roll d6; saves on roll >= save_target (lower = better).
    Shatter: first `shatter_strikes` hits auto-pass to casualty.
    Poison: on a 6 to save, fail.
    Parry: if save fails, roll d6, 5+ negates.
    Regenerate: if save fails, roll d6, threshold+ negates. None = no Regenerate.
    Regen reroll: failed Regenerate may be re-rolled once (Hospitaller mastery).
    """
    # Max strikes any run can have = front_line cap = 20 + cleave bonus. Cap at 40 for safety.
    max_strikes = int(n_strikes.max()) if n_strikes.any() else 0
    if max_strikes == 0:
        return np.zeros(n, dtype=np.int32)
    max_strikes = min(max_strikes, 40)

    save_clipped = np.clip(save_target, 2, 7)
    auto_fail_save = save_clipped >= 7
    auto_pass_save = save_target < 2

    # Roll dice for all possible strikes (max_strikes per run); mask later
    rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8)
    strike_idx = np.arange(max_strikes)[None, :]  # (1, max_strikes)
    strike_in_use = strike_idx < n_strikes[:, None]  # (n, max_strikes)
    is_shatter = strike_idx < shatter_strikes[:, None]  # (n, max_strikes)

    # Determine which strikes failed save
    # For shatter strikes: auto-fail save (casualty).
    # For normal strikes: roll < save_target = fail.
    # Auto-fail save (target >= 7) → all normal strikes fail.
    # Auto-pass save (target < 2) → all normal strikes pass (unless poison rolled a 6).
    normal_fail = (rolls < save_clipped[:, None])
    if auto_fail_save.any():
        normal_fail = normal_fail | auto_fail_save[:, None]
    if auto_pass_save.any():
        normal_fail = normal_fail & (~auto_pass_save[:, None])
    if atk_has_poison:
        normal_fail = normal_fail | (rolls == 6)
    failed = (is_shatter | (normal_fail & strike_in_use & ~is_shatter)) & strike_in_use

    if def_has_parry:
        parry_rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8)
        parry_save = (parry_rolls >= 5) & failed
        failed = failed & (~parry_save)
    if def_regen_threshold is not None:
        regen_rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8)
        regen_save = (regen_rolls >= def_regen_threshold) & failed
        if def_has_regen_reroll:
            # Re-roll for strikes that failed the regenerate (still in failed mask)
            still_failed = failed & (~regen_save)
            reroll_rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8)
            reroll_save = (reroll_rolls >= def_regen_threshold) & still_failed
            regen_save = regen_save | reroll_save
        failed = failed & (~regen_save)

    casualties = failed.sum(axis=1).astype(np.int32)
    return casualties


def _shaking_test_vec(rng, n, field_size, shaking_value, mask):
    """Per-run shaking test. Each retinue in field rolls; flees if roll < shaking_value.
    Only runs in `mask` actually do the test.
    Returns casualties (n,).
    """
    if not mask.any() or shaking_value < 1:
        return np.zeros(n, dtype=np.int32)
    max_field = int(field_size.max())
    if max_field == 0:
        return np.zeros(n, dtype=np.int32)
    rolls = rng.integers(1, 7, size=(n, max_field), dtype=np.int8)
    field_idx = np.arange(max_field)[None, :]
    in_field = field_idx < field_size[:, None]
    flees = (rolls < shaking_value) & in_field & mask[:, None]
    return flees.sum(axis=1).astype(np.int32)


# ===== Main matchup loop =====

def run_matchup_vec(ld_a, ld_b, n_runs=100, max_skirmishes=20, seed=None, alternate_attacker=True,
                    a_init_size=None, b_init_size=None, a_init_endurance=None, b_init_endurance=None,
                    return_per_run_state=False,
                    a_playstyle=None, b_playstyle=None,
                    attacker_mode="balanced",
                    log_skirmishes=0):
    """Run n_runs battles in parallel.

    State injection (for horde mode):
      a_init_size / b_init_size: per-run starting size arrays (length n_runs). None = use loadout size.
      a_init_endurance / b_init_endurance: per-run starting endurance arrays. None = use retinue max.
      return_per_run_state: if True, also return per-run final size/endurance arrays.
    Playstyle (for non-random tactic selection):
      a_playstyle / b_playstyle: string name of a playstyle (see playstyles.py). None or
        'Random' = uniform random tactic (default, original behavior).
    Attacker / Seize the Initiative:
      attacker_mode: 'balanced' (default) splits attacker 50/50 across runs (legacy behavior).
        'playstyle' uses each side's initiate_rate from their playstyle — aggressive playstyles
        initiate more often, defensive ones less. This drives Seize the Initiative (+1 init,
        first skirmish only). Ministry of Military Strategy always grants Seize regardless of
        attacker assignment; if both sides have Ministry, neither gets Seize (cancels).
      alternate_attacker: legacy parameter; ignored when attacker_mode is set.

    Returns dict with aggregates, plus per-run state arrays if return_per_run_state=True.
    """
    rng = np.random.default_rng(seed)
    tab = get_tactic_tables()
    # Lazy import to avoid circular dependency
    from playstyles import resolve_playstyle_weights, sample_tactic_indices, ministry_counter_weights
    try:
        from playstyles import get_initiate_rate
    except ImportError:
        # Older playstyles.py without per-playstyle initiate rates.
        # Default to 0.5 for all playstyles (neutral 50/50 split).
        def get_initiate_rate(_playstyle):
            return 0.5

    # === Tactic-reveal (Outrider Intercept Post / legacy Ministry tag) detection ===
    # Tag forms (now granted by Outrider Intercept Post, a Cunning monument):
    #   "Ministry: every"  - counter-picks every skirmish (mastery)
    #   "Ministry: first"  - counter-picks first skirmish only
    #   "Ministry: once"   - counter-picks once per battle (modeled as first; base)
    # If neither side has the tag, behavior is unchanged. (Tag name kept for engine compat.)
    def _ministry_mode(tags):
        for t in tags:
            if t == "Ministry: every": return "every"
            if t == "Ministry: first": return "first"
            if t == "Ministry: once":  return "once"
        return None
    a_ministry = _ministry_mode(ld_a.extra_tags)
    b_ministry = _ministry_mode(ld_b.extra_tags)
    # Mutual tactic-reveal cancels (per design).
    if a_ministry and b_ministry:
        a_ministry = b_ministry = None

    # === Seize the Initiative (Ministry of Military Strategy) detection ===
    # "Seize: first"  - Ministry base: Seize the +1 on the FIRST skirmish; opponent never gets it.
    # "Seize: every"  - Ministry mastery (all required buildings): Seize EVERY skirmish; opponent never gets it.
    def _seize_mode(tags):
        if "Seize: every" in tags: return "every"
        if "Seize: first" in tags: return "first"
        return None
    a_seize_mode = _seize_mode(ld_a.extra_tags)
    b_seize_mode = _seize_mode(ld_b.extra_tags)
    a_has_ministry_innate = a_seize_mode is not None
    b_has_ministry_innate = b_seize_mode is not None
    # Mutual Ministry cancels the Seize claim (both claim → neither gets the override).
    a_seize_persistent = (a_seize_mode == "every")
    b_seize_persistent = (b_seize_mode == "every")

    # ============================================================
    # Seize the Initiative assignment
    # ============================================================
    # "Seize the Initiative: gain +1 in the first Skirmish of a Battle."
    # Typically the player who initiates the Battle gains it.
    # Ministry of Military Strategy: always gain Seize the Initiative.
    # If both sides have Ministry, the Innate effect cancels (mutual claim).
    #
    # attacker_mode='balanced'  -> classic 50/50 split (legacy alternate_attacker=True)
    # attacker_mode='playstyle' -> based on each side's playstyle initiate_rate
    # alternate_attacker=False  -> A is always attacker (legacy direct assignment)
    #
    # In all modes, Ministry overrides the result for its side.
    a_seizes = np.zeros(n_runs, dtype=bool)
    b_seizes = np.zeros(n_runs, dtype=bool)

    if attacker_mode == "playstyle":
        a_rate = get_initiate_rate(a_playstyle)
        b_rate = get_initiate_rate(b_playstyle)
        # Each side rolls independently for whether they "wanted to initiate."
        # If both want to or neither wants to, fall back to relative weights:
        a_wants = rng.random(n_runs) < a_rate
        b_wants = rng.random(n_runs) < b_rate
        # A initiates if A wants and B doesn't, OR if both want and a random
        # tiebreak (weighted by relative rates) lands on A.
        both_want = a_wants & b_wants
        neither_wants = (~a_wants) & (~b_wants)
        only_a = a_wants & ~b_wants
        only_b = ~a_wants & b_wants
        # Tiebreak: relative weight
        denom = a_rate + b_rate if (a_rate + b_rate) > 0 else 1.0
        tiebreak = rng.random(n_runs) < (a_rate / denom)
        a_initiates = only_a | (both_want & tiebreak) | (neither_wants & tiebreak)
        b_initiates = ~a_initiates
    elif alternate_attacker:
        # Classic balanced 50/50 split
        half = n_runs // 2
        a_initiates = np.zeros(n_runs, dtype=bool)
        a_initiates[:half] = True
        b_initiates = ~a_initiates
    else:
        # Legacy: A is always attacker
        a_initiates = np.ones(n_runs, dtype=bool)
        b_initiates = ~a_initiates

    # Innate Seize claims (from initiating the battle)
    a_seizes = a_initiates.copy()
    b_seizes = b_initiates.copy()

    # Ministry override: each side gains Seize regardless of who initiated.
    # If both have Ministry, both claim → mutual cancel (neither gets it).
    if a_has_ministry_innate and b_has_ministry_innate:
        pass  # mutual claim — keep the initiate-driven assignment; the two Ministries
              # cancel each other's Seize claim, and the initiator retains it as normal.
    else:
        if a_has_ministry_innate:
            a_seizes[:] = True
            b_seizes[:] = False  # Ministry "always gains Seize, and your opponent doesn't"
        if b_has_ministry_innate:
            b_seizes[:] = True
            a_seizes[:] = False

    # Build StaticArmy versions for both Seize states
    a_with_seize = StaticArmy(ld_a, is_attacker=True)
    a_no_seize   = StaticArmy(ld_a, is_attacker=False)
    b_with_seize = StaticArmy(ld_b, is_attacker=True)
    b_no_seize   = StaticArmy(ld_b, is_attacker=False)

    # Per-run base init for first skirmish (Seize +1 applies)
    a_base_init_first = np.where(a_seizes, a_with_seize.base_init(True), a_no_seize.base_init(True)).astype(np.int8)
    b_base_init_first = np.where(b_seizes, b_with_seize.base_init(True), b_no_seize.base_init(True)).astype(np.int8)
    # Subsequent skirmishes: normally no Seize. BUT Ministry mastery ("Seize: every")
    # grants persistent Seize — +1 init every skirmish, and the opponent never gets it.
    a_norm_base = a_no_seize.base_init(False)
    b_norm_base = b_no_seize.base_init(False)
    a_base_init_norm = np.full(n_runs, a_norm_base + (1 if a_seize_persistent else 0), dtype=np.int8)
    b_base_init_norm = np.full(n_runs, b_norm_base + (1 if b_seize_persistent else 0), dtype=np.int8)

    # Canonical static refs (Seize only affects first-skirmish init, not anything else)
    a_static = a_no_seize
    b_static = b_no_seize

    # Mutable state arrays — use injected values if provided
    if a_init_size is not None:
        a_size = np.asarray(a_init_size, dtype=np.int32).copy()
    else:
        a_size = np.full(n_runs, ld_a.size, dtype=np.int32)
    if b_init_size is not None:
        b_size = np.asarray(b_init_size, dtype=np.int32).copy()
    else:
        b_size = np.full(n_runs, ld_b.size, dtype=np.int32)
    if a_init_endurance is not None:
        a_end = np.asarray(a_init_endurance, dtype=np.int8).copy()
    else:
        a_end = np.full(n_runs, a_static.endurance_start, dtype=np.int8)
    if b_init_endurance is not None:
        b_end = np.asarray(b_init_endurance, dtype=np.int8).copy()
    else:
        b_end = np.full(n_runs, b_static.endurance_start, dtype=np.int8)
    a_fat = np.zeros(n_runs, dtype=np.int8)
    b_fat = np.zeros(n_runs, dtype=np.int8)
    a_shield_destroyed = np.zeros(n_runs, dtype=bool)
    b_shield_destroyed = np.zeros(n_runs, dtype=bool)
    # Track when a side's battle ended specifically via a successful Fall Back (i.e., that
    # side played FB AND the matrix cell was an "end" outcome). Used downstream by
    # horde_mode to apply Strain (skip next-turn endurance recovery, unless Immune Strain).
    a_ended_by_fb = np.zeros(n_runs, dtype=bool)
    b_ended_by_fb = np.zeros(n_runs, dtype=bool)
    FB_IDX = 6  # Fall Back tactic index (Scout=0, Ambush=1, Flank=2, Charge=3, FF=4, DF=5, FB=6)
    active = np.ones(n_runs, dtype=bool)
    # Runs that start with size=0 are dead immediately
    active = active & (a_size > 0) & (b_size > 0)
    skirm_count = np.zeros(n_runs, dtype=np.int32)
    # Apothecary mastery: heal 1 retinue at start of next skirmish per 4 casualties taken in previous skirmish.
    # Track casualties from the previous skirmish for the heal trigger.
    a_prev_casualties = np.zeros(n_runs, dtype=np.int32)
    b_prev_casualties = np.zeros(n_runs, dtype=np.int32)
    a_has_apo_heal = "Apothecary Heal" in ld_a.extra_tags
    b_has_apo_heal = "Apothecary Heal" in ld_b.extra_tags

    # Casualty source tracking (cumulative across the battle, per run)
    a_kill_cas_total  = np.zeros(n_runs, dtype=np.int32)   # losses to combat strikes
    b_kill_cas_total  = np.zeros(n_runs, dtype=np.int32)
    a_shake_cas_total = np.zeros(n_runs, dtype=np.int32)   # losses to shaking test
    b_shake_cas_total = np.zeros(n_runs, dtype=np.int32)
    a_rout_cas_total  = np.zeros(n_runs, dtype=np.int32)   # losses to Army Rout (whole army)
    b_rout_cas_total  = np.zeros(n_runs, dtype=np.int32)
    # Cause-of-wipe: 0=alive/indecisive, 1=combat, 2=shake, 3=rout
    a_cause_of_wipe = np.zeros(n_runs, dtype=np.int8)
    b_cause_of_wipe = np.zeros(n_runs, dtype=np.int8)

    # Tactic-pair logging.
    # `first_skirm_tactic_pair[i,j]` counts runs where A played tactic i and B played
    # tactic j on the FIRST skirmish — useful for empirical tactic matrix without a
    # separate forced-tactic sweep.
    first_skirm_tactic_pair = np.zeros((7, 7), dtype=np.int32)
    # Also accumulate the per-run outcomes for the first-skirmish tactic pair —
    # i.e. how many of those runs the A-side ultimately won. This lets us build a
    # win-rate matrix conditioned on opening tactics.
    first_skirm_tactic_a_wins = np.zeros((7, 7), dtype=np.int32)
    first_skirm_tactic_b_wins = np.zeros((7, 7), dtype=np.int32)
    # Per-run cache of the first-skirmish tactic indices, set on sk==0:
    first_a_tac = np.zeros(n_runs, dtype=np.int8)
    first_b_tac = np.zeros(n_runs, dtype=np.int8)

    n_tactics = len(TACTICS)

    # Optional per-skirmish logging (first `log_skirmishes` skirmishes). Records, per run:
    # casualties each side took that skirmish (combat + shake) and who struck first
    # (1=A first, -1=B first, 0=simultaneous/neither). Only populated when log_skirmishes>0.
    skirmish_log = [] if log_skirmishes > 0 else None

    for sk in range(max_skirmishes):
        active = active & (a_size > 0) & (b_size > 0)
        if not active.any():
            break
        first = (sk == 0)

        # Apothecary mastery: at start of skirmish (after first), heal 1 retinue per 4 casualties
        # taken in the previous skirmish. Cannot heal above size cap. Only active runs heal
        # (wiped runs stay wiped — per-run mask, not per-matchup).
        if not first:
            if a_has_apo_heal:
                a_heal = np.where(active, a_prev_casualties // 4, 0).astype(np.int32)
                a_size = np.minimum(a_size + a_heal, ld_a.size).astype(np.int32)
            if b_has_apo_heal:
                b_heal = np.where(active, b_prev_casualties // 4, 0).astype(np.int32)
                b_size = np.minimum(b_size + b_heal, ld_b.size).astype(np.int32)

        # Static stats for this skirmish
        a_tags = a_static.tags(first)
        b_tags = b_static.tags(first)
        a_ap = a_static.weapon_ap(first)
        b_ap = b_static.weapon_ap(first)
        a_base_init = a_base_init_first if first else a_base_init_norm
        b_base_init = b_base_init_first if first else b_base_init_norm

        # Bastard Sword adaptive: per-run, if a Bastard+shield user has had their shield
        # destroyed in a prior skirmish, that run uses 2H stats (Cleave/Unwieldy) instead
        # of 1H stats (Shatter/Steady) for the rest of the battle.
        if a_static.is_bastard_dual_profile:
            a_bastard_2h_mask = a_shield_destroyed.copy()
            a_tags_2h = a_static.tags_first_2h if first else a_static.tags_normal_2h
        else:
            a_bastard_2h_mask = None
            a_tags_2h = None
        if b_static.is_bastard_dual_profile:
            b_bastard_2h_mask = b_shield_destroyed.copy()
            b_tags_2h = b_static.tags_first_2h if first else b_static.tags_normal_2h
        else:
            b_bastard_2h_mask = None
            b_tags_2h = None

        # Pick tactics per playstyle (defaults to uniform random if None/Random)
        a_state = {"a_size": a_size, "b_size": b_size, "a_end": a_end, "b_end": b_end, "a_fat": a_fat, "b_fat": b_fat}
        b_state = {"a_size": b_size, "b_size": a_size, "a_end": b_end, "b_end": a_end, "a_fat": b_fat, "b_fat": a_fat}
        a_weights = resolve_playstyle_weights(a_playstyle, a_state, n_runs)
        b_weights = resolve_playstyle_weights(b_playstyle, b_state, n_runs)

        # === Ministry of Strategy counter-pick ===
        # Determine if Ministry fires this skirmish for either side.
        a_ministry_fires = (a_ministry == "every") or (a_ministry in ("first", "once") and first)
        b_ministry_fires = (b_ministry == "every") or (b_ministry in ("first", "once") and first)

        if a_ministry_fires:
            # B picks first, A counter-picks
            b_tac = sample_tactic_indices(b_weights, rng)
            a_weights = ministry_counter_weights(b_tac, n_runs, counter_weight=0.8)
            a_tac = sample_tactic_indices(a_weights, rng)
        elif b_ministry_fires:
            # A picks first, B counter-picks
            a_tac = sample_tactic_indices(a_weights, rng)
            b_weights = ministry_counter_weights(a_tac, n_runs, counter_weight=0.8)
            b_tac = sample_tactic_indices(b_weights, rng)
        else:
            # Standard: simultaneous independent picks
            a_tac = sample_tactic_indices(a_weights, rng)
            b_tac = sample_tactic_indices(b_weights, rng)

        # Cache first-skirmish tactic picks (per-run) for later attribution.
        if first:
            first_a_tac = a_tac.copy()
            first_b_tac = b_tac.copy()

        a_I_mod  = tab["a_I"][a_tac, b_tac]
        a_TH_mod = tab["a_TH"][a_tac, b_tac]
        a_TS_mod = tab["a_TS"][a_tac, b_tac]
        b_I_mod  = tab["b_I"][a_tac, b_tac]
        b_TH_mod = tab["b_TH"][a_tac, b_tac]
        b_TS_mod = tab["b_TS"][a_tac, b_tac]
        end_pair = tab["end"][a_tac, b_tac]
        no_combat_pair = tab["no_combat"][a_tac, b_tac]
        # When no_combat fires, this flag tells us if endurance is still lost (Flank/Flank)
        # vs free (Scout/Scout, Ambush/Ambush).
        no_combat_endurance_pair = tab["no_combat_endurance"][a_tac, b_tac]

        # Steady/Unwieldy — handle per-run for Bastard dual-profile
        # NOTE on Immune Unwieldy: when a unit has the Immune Unwieldy tag (typically from
        # Tiltyard mastery), the Unwieldy positive-init clamp is suppressed in BOTH the
        # normal branch AND the bastard-dual 2H branch.
        a_immune_unwieldy = "Immune Unwieldy" in a_tags
        b_immune_unwieldy = "Immune Unwieldy" in b_tags
        if a_bastard_2h_mask is not None:
            # 1H runs: Steady (clamp negative init to 0). 2H runs: Unwieldy (clamp positive to 0).
            a_in_1h = ~a_bastard_2h_mask
            a_in_2h = a_bastard_2h_mask
            # Steady (only for 1H Bastard runs): negative init mods become 0
            a_I_mod = np.where(a_in_1h & (a_I_mod < 0), 0, a_I_mod)
            # Unwieldy (only for 2H Bastard runs): positive init mods become 0 — unless Immune Unwieldy
            if not a_immune_unwieldy:
                a_I_mod = np.where(a_in_2h & (a_I_mod > 0), 0, a_I_mod)
        else:
            if "Steady" in a_tags:
                a_I_mod = np.where(a_I_mod < 0, 0, a_I_mod)
            if "Unwieldy" in a_tags and not a_immune_unwieldy:
                a_I_mod = np.where(a_I_mod > 0, 0, a_I_mod)
        if b_bastard_2h_mask is not None:
            b_in_1h = ~b_bastard_2h_mask
            b_in_2h = b_bastard_2h_mask
            b_I_mod = np.where(b_in_1h & (b_I_mod < 0), 0, b_I_mod)
            if not b_immune_unwieldy:
                b_I_mod = np.where(b_in_2h & (b_I_mod > 0), 0, b_I_mod)
        else:
            if "Steady" in b_tags:
                b_I_mod = np.where(b_I_mod < 0, 0, b_I_mod)
            if "Unwieldy" in b_tags and not b_immune_unwieldy:
                b_I_mod = np.where(b_I_mod > 0, 0, b_I_mod)

        a_init = np.clip(a_base_init + a_I_mod, -2, 2)
        b_init = np.clip(b_base_init + b_I_mod, -2, 2)

        # End-battle tactic pairs
        ending = end_pair & active
        # Track FB-caused endings per side (the side that played Fall Back AND ended battle this skirmish).
        # Only the 4 "end" cells in the matrix involve FB: Scout/FB, Ambush/FB, DF/FB, FB/FB.
        # So whenever `ending` fires, at least one side played FB. Track which.
        a_ended_by_fb |= ending & (a_tac == FB_IDX)
        b_ended_by_fb |= ending & (b_tac == FB_IDX)
        # No-combat pairs: skirmish produces no strikes but battle continues to next skirmish.
        # (Scout-vs-Scout, Ambush-vs-Ambush, Flank-vs-Flank — armies maneuver but don't engage.)
        no_combat_this_skirm = no_combat_pair & active
        # Active battles that don't end AND aren't no_combat this skirmish (i.e., they fight):
        proceed = active & (~ending) & (~no_combat_this_skirm)

        if not proceed.any() and not no_combat_this_skirm.any():
            active = active & (~ending)
            continue

        # Determine strike order
        a_tripped = (a_init <= -2) & proceed
        b_tripped = (b_init <= -2) & proceed
        a_first_mask = (a_init > b_init) & proceed & (~a_tripped)
        b_first_mask = (b_init > a_init) & proceed & (~b_tripped)
        simul_mask = (a_init == b_init) & proceed

        # Compute front lines (each run independently)
        a_front = np.minimum(20, a_size).astype(np.int8)
        b_front = np.minimum(20, b_size).astype(np.int8)
        a_reserves = np.minimum(10, np.maximum(0, a_size - 20))
        b_reserves = np.minimum(10, np.maximum(0, b_size - 20))

        # To-hit targets (Yew Heart: ranged weapons +1 to hit, only on first skirmish with ranged equipped)
        yew_hit_bonus_a = -1 if (a_static.yew_heart and first and a_static.ranged) else 0
        yew_hit_bonus_b = -1 if (b_static.yew_heart and first and b_static.ranged) else 0
        # Weapon-intrinsic +1TH tag (e.g., Hunting Bow): -1 to target_th = easier to hit.
        # Applies whenever the weapon with the tag is the active weapon (so it's already
        # gated by skirmish via the tag set — on dual-equip, tags_normal switches to the
        # melee profile and the +1TH disappears; on pure-ranged it persists every skirmish).
        weapon_th_bonus_a = -1 if "+1TH" in a_tags else 0
        weapon_th_bonus_b = -1 if "+1TH" in b_tags else 0
        # Shield -1TBH: defender's shield raises attacker's target_th by +1.
        # (This is now the ONLY source of "TBH" — the tactic matrix no longer carries
        # TBH; it expresses such effects directly as TH on the affected side.)
        # Disappears if the shield is destroyed mid-battle.
        b_shield_tbh = np.where(b_shield_destroyed, 0, b_static.shield_tbh_penalty_start)
        a_shield_tbh = np.where(a_shield_destroyed, 0, a_static.shield_tbh_penalty_start)
        # Unstoppable: attacker ignores to-hit PENALTIES from tactics & equipment.
        #   - Equipment: defender's shield -1TBH (the b_shield_tbh / a_shield_tbh term) is zeroed.
        #   - Tactics: any negative TH_mod (penalty that would raise target_th) is clamped to 0,
        #     so enemy defensive tactics can't lower the attacker's accuracy. Positive bonuses kept.
        # Fatigue and the attacker's own bonuses (+1TH, Yew) are unaffected.
        a_unstoppable = "Unstoppable" in a_tags
        b_unstoppable = "Unstoppable" in b_tags
        a_th_mod_eff = np.maximum(a_TH_mod, 0) if a_unstoppable else a_TH_mod
        b_th_mod_eff = np.maximum(b_TH_mod, 0) if b_unstoppable else b_TH_mod
        a_shield_tbh_eff = (b_shield_tbh * 0) if a_unstoppable else b_shield_tbh
        b_shield_tbh_eff = (a_shield_tbh * 0) if b_unstoppable else a_shield_tbh
        a_target_th = a_static.to_hit - a_th_mod_eff + a_fat + yew_hit_bonus_a + weapon_th_bonus_a + a_shield_tbh_eff
        b_target_th = b_static.to_hit - b_th_mod_eff + b_fat + yew_hit_bonus_b + weapon_th_bonus_b + b_shield_tbh_eff
        # Save targets. Gilded Foundry mastery: incoming AP -1 (effective save improves by 1)
        # We model this by reducing the effective AP applied to the save target.
        b_ap_vs_a = b_ap + (1 if a_static.gf_armor else 0)
        a_ap_vs_b = a_ap + (1 if b_static.gf_armor else 0)
        a_save_target_against_b = (a_static.armor_save - b_ap_vs_a)
        a_save_target_against_b -= np.where(a_shield_destroyed, 0, a_static.shield_bonus_start)
        a_save_target_against_b = a_save_target_against_b - a_TS_mod
        b_save_target_against_a = (b_static.armor_save - a_ap_vs_b)
        b_save_target_against_a -= np.where(b_shield_destroyed, 0, b_static.shield_bonus_start)
        b_save_target_against_a = b_save_target_against_a - b_TS_mod

        # Immune Poison: defender's Apothecary innate blocks Poison effect
        a_effective_poison = ("Poison" in a_tags) and ("Immune Poison" not in b_tags)
        b_effective_poison = ("Poison" in b_tags) and ("Immune Poison" not in a_tags)

        # === Resolve strikes ===
        # We compute A's strike count once (depends only on a_front, a target).
        # B's strike count if B has FULL front line (for simul and b_first cases) - one roll set.
        # B's strike count if B has REDUCED front line (for a_first cases) - separate roll set.
        # We then apply casualties in proper order.

        # A's strike on B (always uses a's full starting front line)
        a_strikes_initial, a_shatter, a_destroys_shield = _roll_strikes_vec(
            rng, n_runs, a_target_th, a_front, a_tags,
            b_static.has_shield, b_shield_destroyed,
            atk_bastard_2h_mask=a_bastard_2h_mask, atk_tags_2h=a_tags_2h,
            defender_shield_immune=b_static.shield_immune,
        )
        # Mask: only count strikes from runs where A actually fights this skirmish
        a_fights = proceed & (~a_tripped) & (a_size > 0)
        a_strikes_initial = np.where(a_fights, a_strikes_initial, 0)
        a_shatter = np.where(a_fights, a_shatter, 0)
        a_destroys_shield = a_destroys_shield & a_fights

        # B saves against A's strikes
        b_casualties = _roll_saves_vec(
            rng, n_runs, b_save_target_against_a, a_strikes_initial, a_shatter,
            atk_has_poison=a_effective_poison,
            def_has_parry=("Parry" in b_tags),
            def_regen_threshold=_regen_threshold(b_tags, a_tags),
            def_has_regen_reroll=_has_regen_reroll(b_tags),
        )
        b_casualties = np.minimum(b_casualties, b_front).astype(np.int32)

        # Now apply A's destroy-shield effect immediately (affects subsequent saves in this skirmish? No, only future skirmishes)
        # Per rules, shield destroyed for the rest of skirmish/battle. Apply now.
        b_shield_destroyed = b_shield_destroyed | a_destroys_shield

        # B's strike: depends on whether B is back-striking (a_first) or initial striker (b_first/simul)
        # Compute B's reduced front line for a_first cases
        b_front_after_a_strike = np.maximum(0, b_front - b_casualties)
        # Refill from reserves
        b_front_refilled = np.minimum(20, b_front_after_a_strike + b_reserves)
        # In a_first cases, B uses b_front_refilled. In b_first/simul cases, B uses full b_front.
        b_effective_front = np.where(a_first_mask, b_front_refilled, b_front).astype(np.int8)

        b_fights = proceed & (~b_tripped) & ((b_size - b_casualties) > 0 | b_first_mask | simul_mask)
        # If b lost everyone to A's first strike, b_size - b_casualties might be 0
        b_alive_for_strike = np.where(a_first_mask, (b_size - b_casualties) > 0, b_size > 0)
        b_fights = proceed & (~b_tripped) & b_alive_for_strike

        b_strikes, b_shatter, b_destroys_shield = _roll_strikes_vec(
            rng, n_runs, b_target_th, b_effective_front, b_tags,
            a_static.has_shield, a_shield_destroyed,
            atk_bastard_2h_mask=b_bastard_2h_mask, atk_tags_2h=b_tags_2h,
            defender_shield_immune=a_static.shield_immune,
        )
        b_strikes = np.where(b_fights, b_strikes, 0)
        b_shatter = np.where(b_fights, b_shatter, 0)
        b_destroys_shield = b_destroys_shield & b_fights

        a_casualties = _roll_saves_vec(
            rng, n_runs, a_save_target_against_b, b_strikes, b_shatter,
            atk_has_poison=b_effective_poison,
            def_has_parry=("Parry" in a_tags),
            def_regen_threshold=_regen_threshold(a_tags, b_tags),
            def_has_regen_reroll=_has_regen_reroll(a_tags),
        )
        a_casualties = np.minimum(a_casualties, a_front).astype(np.int32)

        # For b_first cases, A's strike happens AFTER B's. We computed A_strikes using
        # FULL a_front. That overcounts in b_first cases where A's front line was reduced.
        # We need to recompute A's strike for b_first cases with reduced front line.
        # The cleanest fix: zero out a_strikes for b_first cases and recompute.
        recompute_a = b_first_mask
        if recompute_a.any():
            a_front_after_b = np.maximum(0, a_front - a_casualties)
            a_reserves_avail = a_reserves
            a_front_refilled = np.minimum(20, a_front_after_b + a_reserves_avail)
            a_effective_front_after_b = np.where(recompute_a, a_front_refilled, a_front).astype(np.int8)

            # Recompute A's strikes for the b_first cases
            new_a_strikes, new_a_shatter, new_a_destroys = _roll_strikes_vec(
                rng, n_runs, a_target_th, a_effective_front_after_b, a_tags,
                b_static.has_shield, b_shield_destroyed,
                atk_bastard_2h_mask=a_bastard_2h_mask, atk_tags_2h=a_tags_2h,
                defender_shield_immune=b_static.shield_immune,
            )
            a_alive_for_back = a_front_after_b + a_reserves_avail > 0
            new_a_fights = recompute_a & a_alive_for_back & (~a_tripped)
            # Update A's strikes only for recompute cases
            a_strikes_initial = np.where(recompute_a, np.where(new_a_fights, new_a_strikes, 0), a_strikes_initial)
            a_shatter = np.where(recompute_a, np.where(new_a_fights, new_a_shatter, 0), a_shatter)
            a_destroys_shield = np.where(recompute_a, new_a_destroys & new_a_fights, a_destroys_shield)

            # Recompute B's casualties using updated a_strikes for b_first runs
            new_b_casualties = _roll_saves_vec(
                rng, n_runs, b_save_target_against_a, a_strikes_initial, a_shatter,
                atk_has_poison=a_effective_poison,
                def_has_parry=("Parry" in b_tags),
                def_regen_threshold=_regen_threshold(b_tags, a_tags),
                def_has_regen_reroll=_has_regen_reroll(b_tags),
            )
            new_b_casualties = np.minimum(new_b_casualties, b_front).astype(np.int32)
            b_casualties = np.where(recompute_a, new_b_casualties, b_casualties)
            b_shield_destroyed = b_shield_destroyed | (a_destroys_shield & recompute_a)

        # Apply destroys-shield from B's strikes
        a_shield_destroyed = a_shield_destroyed | b_destroys_shield

        # Apply casualties to sizes
        a_pre_combat_size = a_size.copy()
        b_pre_combat_size = b_size.copy()
        a_size = np.maximum(0, a_size - a_casualties)
        b_size = np.maximum(0, b_size - b_casualties)

        # Track combat casualties (capped at actual size lost)
        a_combat_lost = a_pre_combat_size - a_size
        b_combat_lost = b_pre_combat_size - b_size
        a_kill_cas_total += a_combat_lost
        b_kill_cas_total += b_combat_lost
        # Cause-of-wipe: if size hit 0 from this and not already wiped, cause = 1 (combat)
        a_newly_dead_combat = (a_size <= 0) & (a_cause_of_wipe == 0) & active
        b_newly_dead_combat = (b_size <= 0) & (b_cause_of_wipe == 0) & active
        a_cause_of_wipe = np.where(a_newly_dead_combat, 1, a_cause_of_wipe).astype(np.int8)
        b_cause_of_wipe = np.where(b_newly_dead_combat, 1, b_cause_of_wipe).astype(np.int8)

        # Track casualties for Apothecary heal next skirmish (includes shake casualties below)
        a_skirm_cas = a_combat_lost.copy()
        b_skirm_cas = b_combat_lost.copy()

        skirm_count = skirm_count + active.astype(np.int32)

        # === End-of-skirmish: endurance, fatigue, shaking ===
        # Endurance loss rules:
        #   - Drilled + first skirmish: exempt
        #   - no_combat without endurance_loss (Scout/Scout, Ambush/Ambush): exempt
        #   - no_combat WITH endurance_loss (Flank/Flank): NOT exempt — maneuvering tires
        #   - Regular combat skirmishes: lose endurance as normal
        no_combat_free = no_combat_this_skirm & (~no_combat_endurance_pair)
        a_loses_end = active & ~(("Drilled" in a_tags) and first) & (a_size > 0) & (~no_combat_free)
        b_loses_end = active & ~(("Drilled" in b_tags) and first) & (b_size > 0) & (~no_combat_free)
        # already fatigued → gain fatigue token instead of endurance loss
        a_already_fat = a_fat > 0
        b_already_fat = b_fat > 0
        # Endurance loss only where not already fatigued
        a_loses_end_actual = a_loses_end & ~a_already_fat
        b_loses_end_actual = b_loses_end & ~b_already_fat
        a_end = a_end - a_loses_end_actual.astype(np.int8)
        b_end = b_end - b_loses_end_actual.astype(np.int8)
        # Fatigue tokens for already-fatigued armies
        a_fat = a_fat + (a_loses_end & a_already_fat).astype(np.int8)
        b_fat = b_fat + (b_loses_end & b_already_fat).astype(np.int8)
        # Trigger shaking test on transition (endurance newly hit 0)
        a_newly_fat = a_loses_end_actual & (a_end <= 0)
        b_newly_fat = b_loses_end_actual & (b_end <= 0)
        # Set fatigue=1 for newly fatigued
        a_fat = np.where(a_newly_fat, 1, a_fat).astype(np.int8)
        b_fat = np.where(b_newly_fat, 1, b_fat).astype(np.int8)

        # Shaking test (Unshakable exempts; Steadfast does NOT — only Route protection)
        # Skip for runs that ended via tactic pairing (Fall Back withdrew before shake).
        a_field = np.minimum(25, a_size)
        b_field = np.minimum(25, b_size)
        a_shake_cas = _shaking_test_vec(rng, n_runs, a_field, a_static.shaking,
                                         a_newly_fat & ~a_static.unshakable & ~("Unshakable" in a_tags) & ~ending)
        b_shake_cas = _shaking_test_vec(rng, n_runs, b_field, b_static.shaking,
                                         b_newly_fat & ~b_static.unshakable & ~("Unshakable" in b_tags) & ~ending)
        a_pre_shake_size = a_size.copy()
        b_pre_shake_size = b_size.copy()
        a_size = np.maximum(0, a_size - a_shake_cas)
        b_size = np.maximum(0, b_size - b_shake_cas)

        # Track shake casualties
        a_shake_lost = a_pre_shake_size - a_size
        b_shake_lost = b_pre_shake_size - b_size
        a_shake_cas_total += a_shake_lost
        b_shake_cas_total += b_shake_lost

        # Per-skirmish logging (first `log_skirmishes` skirmishes only)
        if skirmish_log is not None and sk < log_skirmishes:
            # who struck first this skirmish: +1 A, -1 B, 0 simultaneous/neither
            first_striker = np.where(a_first_mask, 1, np.where(b_first_mask, -1, 0)).astype(np.int8)
            skirmish_log.append({
                "skirmish": sk + 1,
                "a_casualties": (a_combat_lost + a_shake_lost).astype(np.int32).copy(),
                "b_casualties": (b_combat_lost + b_shake_lost).astype(np.int32).copy(),
                "first_striker": first_striker.copy(),
                "active": active.copy(),
            })
        # Cause-of-wipe from shaking
        a_newly_dead_shake = (a_size <= 0) & (a_cause_of_wipe == 0) & active
        b_newly_dead_shake = (b_size <= 0) & (b_cause_of_wipe == 0) & active
        a_cause_of_wipe = np.where(a_newly_dead_shake, 2, a_cause_of_wipe).astype(np.int8)
        b_cause_of_wipe = np.where(b_newly_dead_shake, 2, b_cause_of_wipe).astype(np.int8)

        # Total casualties this skirmish (for Apothecary heal next skirmish)
        a_skirm_cas = a_skirm_cas + a_shake_lost
        b_skirm_cas = b_skirm_cas + b_shake_lost
        a_prev_casualties = a_skirm_cas
        b_prev_casualties = b_skirm_cas

        # === Army Rout rule ===
        # "When a Retinue's to Hit is modified to be a 7+ before Tactics and
        # equipment modifiers, the Army Routs and counts as Destroyed."
        # Pre-tactic to-hit = base to-hit + fatigue. Threshold = 7.
        # Steadfast prevents Rout (= cannot have To Hit modified to 7+).
        # Unshakable retinues also bypass Rout in this engine (KT compatibility).
        # IMPORTANT: skip Rout check for runs whose battle ended via tactic pairing
        # this skirmish (e.g. Fall Back) — they withdrew before fatigue could finish them.
        a_can_rout = (not a_static.unshakable) and ("Unshakable" not in a_tags) and ("Steadfast" not in a_tags)
        b_can_rout = (not b_static.unshakable) and ("Unshakable" not in b_tags) and ("Steadfast" not in b_tags)
        if a_can_rout:
            a_rout_threshold_hit = (a_static.to_hit + a_fat) >= 7
            a_routs = active & a_rout_threshold_hit & (a_size > 0) & (~ending)
            a_rout_loss = np.where(a_routs, a_size, 0)
            a_rout_cas_total += a_rout_loss
            a_size = np.where(a_routs, 0, a_size)
            a_newly_dead_rout = a_routs & (a_cause_of_wipe == 0)
            a_cause_of_wipe = np.where(a_newly_dead_rout, 3, a_cause_of_wipe).astype(np.int8)
        if b_can_rout:
            b_rout_threshold_hit = (b_static.to_hit + b_fat) >= 7
            b_routs = active & b_rout_threshold_hit & (b_size > 0) & (~ending)
            b_rout_loss = np.where(b_routs, b_size, 0)
            b_rout_cas_total += b_rout_loss
            b_size = np.where(b_routs, 0, b_size)
            b_newly_dead_rout = b_routs & (b_cause_of_wipe == 0)
            b_cause_of_wipe = np.where(b_newly_dead_rout, 3, b_cause_of_wipe).astype(np.int8)
        # (Per the rule, retinues each become a casualty — equivalent to size→0.)

        # Battles that ended via tactic now go inactive
        active = active & (~ending)

    # Determine outcomes
    a_dead = a_size <= 0
    b_dead = b_size <= 0
    a_wins = int((~a_dead & b_dead).sum())
    b_wins = int((a_dead & ~b_dead).sum())
    mut_wipe = int((a_dead & b_dead).sum())
    indecisive = n_runs - a_wins - b_wins - mut_wipe

    # Attribute first-skirmish tactic picks to final outcomes.
    # first_skirm_tactic_pair[i,j] = number of runs that opened with A=i, B=j
    # first_skirm_tactic_a_wins[i,j] = those runs where A ultimately won
    # first_skirm_tactic_b_wins[i,j] = those runs where B ultimately won
    # Mutual wipes and indecisives are counted in `tactic_pair` but neither wins column.
    a_won_mask = ~a_dead & b_dead
    b_won_mask = a_dead & ~b_dead
    for i in range(7):
        for j in range(7):
            cell_mask = (first_a_tac == i) & (first_b_tac == j)
            first_skirm_tactic_pair[i, j]   = int(cell_mask.sum())
            first_skirm_tactic_a_wins[i, j] = int((cell_mask & a_won_mask).sum())
            first_skirm_tactic_b_wins[i, j] = int((cell_mask & b_won_mask).sum())

    result = {
        "a_wins": a_wins,
        "b_wins": b_wins,
        "mut_wipe": mut_wipe,
        "indecisive": indecisive,
        "avg_skirm": float(skirm_count.mean()),
        "avg_a_rem": float(a_size.mean()),
        "avg_b_rem": float(b_size.mean()),
        # Shield destruction rates (proportion of runs where the shield was
        # destroyed at any point in the battle). 0.0 if no shield equipped.
        "a_shield_destroyed_rate": float(a_shield_destroyed.mean()) if a_static.has_shield else 0.0,
        "b_shield_destroyed_rate": float(b_shield_destroyed.mean()) if b_static.has_shield else 0.0,
        # Successful Fall Back rates: proportion of runs where the battle ended specifically
        # because this side played Fall Back into one of the matrix "end" cells
        # (Scout/FB, Ambush/FB, DF/FB, or FB/FB). horde_mode uses these to apply Strain.
        "a_ended_by_fallback_rate": float(a_ended_by_fb.mean()),
        "b_ended_by_fallback_rate": float(b_ended_by_fb.mean()),
        # Casualty source aggregates (mean per run)
        "avg_a_killed_combat": float(a_kill_cas_total.mean()),
        "avg_a_killed_shake":  float(a_shake_cas_total.mean()),
        "avg_a_killed_rout":   float(a_rout_cas_total.mean()),
        "avg_a_killed_flee":   float(a_rout_cas_total.mean()),  # alias (legacy)
        "avg_b_killed_combat": float(b_kill_cas_total.mean()),
        "avg_b_killed_shake":  float(b_shake_cas_total.mean()),
        "avg_b_killed_rout":   float(b_rout_cas_total.mean()),
        "avg_b_killed_flee":   float(b_rout_cas_total.mean()),  # alias (legacy)
        # Cause-of-wipe distribution
        "a_wipe_combat": int((a_cause_of_wipe == 1).sum()),
        "a_wipe_shake":  int((a_cause_of_wipe == 2).sum()),
        "a_wipe_rout":   int((a_cause_of_wipe == 3).sum()),
        "a_wipe_flee":   int((a_cause_of_wipe == 3).sum()),  # alias (legacy)
        "b_wipe_combat": int((b_cause_of_wipe == 1).sum()),
        "b_wipe_shake":  int((b_cause_of_wipe == 2).sum()),
        "b_wipe_rout":   int((b_cause_of_wipe == 3).sum()),
        "b_wipe_flee":   int((b_cause_of_wipe == 3).sum()),  # alias (legacy)
        # First-skirmish tactic pair matrices (3 × 7×7 each).
        # Read: first_skirm_tactic_pair[i,j] is the # of runs that opened with A playing
        # tactic i and B playing tactic j; first_skirm_tactic_a_wins[i,j] is the subset of
        # those runs that A ultimately won. These let downstream code build an empirical
        # tactic matrix from the main tournament without a separate forced-tactic sweep.
        "first_skirm_tactic_pair":   first_skirm_tactic_pair,
        "first_skirm_tactic_a_wins": first_skirm_tactic_a_wins,
        "first_skirm_tactic_b_wins": first_skirm_tactic_b_wins,
    }
    if skirmish_log is not None:
        result["skirmish_log"] = skirmish_log
    if return_per_run_state:
        # per-run outcome encoding: 0=indecisive, 1=a_win, 2=b_win, 3=mut_wipe
        outcome = np.zeros(n_runs, dtype=np.int8)
        outcome[~a_dead & b_dead] = 1
        outcome[a_dead & ~b_dead] = 2
        outcome[a_dead & b_dead] = 3
        result.update({
            "a_final_size": a_size.copy(),
            "b_final_size": b_size.copy(),
            "a_final_endurance": a_end.copy(),
            "b_final_endurance": b_end.copy(),
            "outcomes": outcome,
            "skirm_count": skirm_count.copy(),
            # Per-run casualty source data
            "a_killed_combat": a_kill_cas_total.copy(),
            "a_killed_shake":  a_shake_cas_total.copy(),
            "a_killed_rout":   a_rout_cas_total.copy(),
            "a_killed_flee":   a_rout_cas_total.copy(),  # alias (legacy)
            "b_killed_combat": b_kill_cas_total.copy(),
            "b_killed_shake":  b_shake_cas_total.copy(),
            "b_killed_rout":   b_rout_cas_total.copy(),
            "b_killed_flee":   b_rout_cas_total.copy(),  # alias (legacy)
            "a_cause_of_wipe": a_cause_of_wipe.copy(),
            "b_cause_of_wipe": b_cause_of_wipe.copy(),
            # Per-run flags for successful Fall Back (horde_mode uses these for Strain)
            "a_ended_by_fallback": a_ended_by_fb.copy(),
            "b_ended_by_fallback": b_ended_by_fb.copy(),
        })
    return result


# Drop-in replacement
def run_matchup(ld_a, ld_b, n_runs=100, max_skirmishes=20):
    return run_matchup_vec(ld_a, ld_b, n_runs=n_runs, max_skirmishes=max_skirmishes, alternate_attacker=True)


def run_matchup_tiltyard_adaptive(ld_a, ld_b, n_runs=100, **kwargs):
    """Run a matchup with Tiltyard adaptive weapon selection.

    Mastery Tiltyard rule: after tactics are revealed each skirmish, the player
    chooses melee OR ranged for that skirmish. This wrapper approximates that
    by running the matchup twice — once with each side forced to use their
    melee weapon, once forced to use their ranged-only profile — and selecting
    the side-favorable outcome aggregate.

    The approximation: for each Tiltyard side, the "adaptive" win rate is taken
    as max(melee-only result, ranged-only result). This is an UPPER BOUND on
    actual Tiltyard performance, since a real player picks per-skirmish-per-
    tactic, not per-matchup. In practice this overestimate is small because
    ranged tends to dominate or lose per matchup, not flip skirmish-by-skirmish.

    Returns the better of the two simulations from the perspective of any
    Tiltyard-equipped side. If neither side has Tiltyard, falls back to a
    standard run_matchup_vec call.
    """
    a_adapt = ld_a.has_tiltyard and ld_a.weapon and ld_a.ranged
    b_adapt = ld_b.has_tiltyard and ld_b.weapon and ld_b.ranged
    if not (a_adapt or b_adapt):
        return run_matchup_vec(ld_a, ld_b, n_runs=n_runs, **kwargs)

    # Build melee-only and ranged-only variants of the Tiltyard side(s).
    def melee_only(ld):
        # Drop the ranged weapon → unit uses melee every skirmish
        return ld._replace(ranged=None)

    def ranged_only(ld):
        # Drop the real melee → unit falls back to Farm Tools + multi-shot bow.
        # For one-shot ranged, ranged-only variant doesn't make sense.
        from renown_combat import RANGED
        if "One Shot" in RANGED[ld.ranged]["tags"]:
            return None
        return ld._replace(weapon="Farm Tools")

    # The variants the Tiltyard player can choose from:
    # 1. Dual-equip (volley S1 + melee S2+, no Unwieldy thanks to Tiltyard) — standard sim
    # 2. Melee-only (consistent melee every skirmish, ranged slot wasted)
    # 3. Ranged-only (multi-shot bow every skirmish, melee slot wasted) — only if multi-shot
    ld_a_melee = melee_only(ld_a) if a_adapt else ld_a
    ld_a_ranged = ranged_only(ld_a) if a_adapt else ld_a
    ld_b_melee = melee_only(ld_b) if b_adapt else ld_b
    ld_b_ranged = ranged_only(ld_b) if b_adapt else ld_b

    # Sim variants. Include the dual-equip baseline (standard sim handles
    # ranged S1 + melee S2+ with Unwieldy removed by Tiltyard).
    variants = []
    a_options = [ld_a]  # dual-equip baseline
    if a_adapt:
        a_options.append(ld_a_melee)
        if ld_a_ranged is not None:
            a_options.append(ld_a_ranged)
    b_options = [ld_b]
    if b_adapt:
        b_options.append(ld_b_melee)
        if ld_b_ranged is not None:
            b_options.append(ld_b_ranged)
    for la in a_options:
        for lb in b_options:
            variants.append((la, lb, run_matchup_vec(la, lb, n_runs=n_runs, **kwargs)))

    if not variants:
        return run_matchup_vec(ld_a, ld_b, n_runs=n_runs, **kwargs)

    # Pick the variant where the Tiltyard side wins most.
    # When A is adaptive, the side we optimize is A; if only B is adaptive,
    # we optimize B; if both, we optimize whichever wins more in their best.
    if a_adapt and not b_adapt:
        best = max(variants, key=lambda v: v[2]["a_wins"])
    elif b_adapt and not a_adapt:
        best = max(variants, key=lambda v: v[2]["b_wins"])
    else:
        # Both adaptive — return the variant where adaptive A wins most;
        # caller should also run with the B-favorable choice if needed
        best = max(variants, key=lambda v: v[2]["a_wins"])
    return best[2]
