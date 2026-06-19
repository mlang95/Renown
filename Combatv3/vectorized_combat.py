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
from renown_data import (
    RETINUES, WEAPONS, RANGED, SHIELDS, ARMORS,
    TACTIC_MATRIX, TACTICS,
)
# Keyword constants — engine reads these VARIABLES, not string literals, so that
# renaming a keyword's display value in renown_data propagates here automatically
# (kills the string-drift bug class). Morale keywords (Rally/Resolute/Steadfast/
# Unshakable/Zealot) are intentionally NOT imported — they're slated for removal and
# stay as literals for now.
from renown_data import (
    SHATTER_ARMOR, CLEAVE, DEFLECT, DESTROY_SHIELD, DRILLED, DUAL_WIELD, HALFSWORD,
    MINUS_1_TBH, MINUS_1_PARRY, NEGATE_RIPOSTE, NEGATE_SHIELDED, NEGATE_TEMPERED, NEGATE_UNSTOPPABLE,
    NIMBLE, ONE_SHOT, PARRY, PLANISHING, POISON, RECOVER, RIPOSTE, SERRATED,
    STEADY, STRAIN, TWO_H, UNBREAKABLE, UNSTOPPABLE, UNWIELDY, ENDURING,
    IMMUNE_DESTROY_SHIELD, IMMUNE_STRAIN, IMMUNE_UNWIELDY,
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
        # Conditioning Field mastery: +1 Max Endurance.
        # Royal Pavilion's Immune Strain innate ALSO grants +1 Max Endurance (stacks with Cond Field).
        endurance_bonus = 0
        if "Cond Field" in ld.extra_tags:
            endurance_bonus += 1
        # NOTE: Royal Pavilion's Immune Strain no longer grants +1 endurance (reverted in v2).
        self.endurance_start = ret["endurance"] + endurance_bonus
        # Ministry of Military Strategy innate: maximum initiative ceiling raised to 3 (default 2).
        self.max_init = 3 if ({"MaxInit3", "Crit 5", "Crit 4"} & set(ld.extra_tags)) else 2
        self.shaking = ret["shaking"]
        self.unshakable = ret.get("unbreakable", False)  # break-immunity flag; named .unshakable for legacy
        # Abbey: "Shake +1" tag = +1 to the shaken die roll, i.e. -1 to the effective shake
        # target (a morale buff — easier to pass the shaken test). Stored as a positive amount
        # that is SUBTRACTED from the per-run shake target.
        self.shake_bonus = 1 if "Shake +1" in ld.extra_tags else 0
        self.armor_save = ARMORS[ld.armor]["save"]
        # Shield can be destroyed mid-battle; track shield_bonus as starting value
        self.shield_bonus_start = SHIELDS[ld.shield]["save_bonus"] if ld.shield else 0
        # Shield -1TBH (Scutum, Tower, Heater): attacker must roll +1 higher to
        # hit this unit. Stored as a positive value (attacker's target_th +=
        # this). Disappears if shield is destroyed.
        shield_tags = SHIELDS[ld.shield]["tags"] if ld.shield else []
        self.shield_tbh_penalty_start = 1 if (MINUS_1_TBH in shield_tags) else 0
        # Shield -1TH (Tower): the heavy shield hampers the BEARER's own attacks — their
        # target-to-hit is +1 (harder for them to land hits). Stored positive, like TBH.
        # A drawback that offsets the shield's strong defense. Disappears if shield destroyed.
        self.shield_th_penalty_start = 1 if ("-1TH" in shield_tags) else 0  # bearer self-penalty; no current shield carries it
        self.has_shield = ld.shield is not None
        # Immune Destroy Shield (Heater): this shield cannot be destroyed by Destroy Shield.
        self.shield_immune = IMMUNE_DESTROY_SHIELD in shield_tags
        # Whether the shield itself is the source of Unwieldy (Tower). Used so that destroying the
        # shield also lifts its Unwieldy init-clamp — a destroyed shield returns ALL its negatives.
        self.shield_unwieldy = UNWIELDY in shield_tags
        self._shield_tags_for_unwieldy = shield_tags  # stash for unwieldy_non_shield (computed below)
        self.is_attacker = is_attacker
        self.has_tiltyard = ld.has_tiltyard
        self.ranged = ld.ranged
        # (-1 AP "MW Weapons" mechanic retired. Master Workshop / ABF now grant Rend instead,
        # which is handled in the save/regen path. No AP bonus here.)
        mw_bonus = 0
        # Gilded Foundry mastery: -1 AP from incoming strikes (better effective save)
        # Planishing (Gilded Foundry mastery): the armor save target can never be pushed
        # beyond 6+ by AP — including Deadly's AP -5. ("GF Armor" kept as a legacy alias.)
        self.planishing = (PLANISHING in ld.extra_tags) or ("GF Armor" in ld.extra_tags)
        self.gf_armor = self.planishing  # legacy alias — batch_engine/notebooks read this name
        # ABF (Advanced Blast Furnace innate): your weapons gain -1 AP, and incoming
        # attacks' AP is reduced by 1 — applied to the WEAPON's AP, i.e. before
        # Deadly's -5 stacks on top (a Deadly proc into an ABF defender = (AP+1) - 5).
        self.abf = "ABF" in ld.extra_tags
        # Flat +1 Initiative (Ministry rank 2).
        self.init_bonus = 1 if "+1I" in ld.extra_tags else 0
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
            "ap": -3, "init": 0, "tags": [CLEAVE, UNWIELDY, TWO_H], "tier": "Forged"})
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
            ranged_is_one_shot = ONE_SHOT in ranged_profile["tags"]
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
        # Whether this army's ATTACK is a ranged strike, per phase (drives the new parry rules:
        # ranged = -1 to defender Parry capped at 6+, and a parry vs ranged never ripostes).
        self.uses_ranged_first = ld.ranged is not None
        self.uses_ranged_normal = is_pure_ranged_multi

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
        # Whether Unwieldy comes from a NON-shield source (weapon, armor, or dual-equip). If so,
        # destroying the shield must NOT lift the Unwieldy init-clamp. Set subtraction is WRONG here
        # (Unwieldy from armor and from the shield are the same string, so removing the shield's tag
        # would also drop the armor's). Instead check the non-shield sources directly.
        _wpn_unw = ld.weapon is not None and (UNWIELDY in WEAPONS.get(ld.weapon, {}).get("tags", []))
        _arm_unw = UNWIELDY in ARMORS.get(ld.armor, {}).get("tags", [])
        _has_real_melee = ld.weapon is not None and ld.weapon != "Farm Tools"
        _ty_mastery = ld.has_tiltyard and getattr(ld, "tiltyard_mastery", True)
        _dual_unw = (bool(ld.ranged) and _has_real_melee and ld.has_tiltyard and not _ty_mastery
                     and IMMUNE_UNWIELDY not in ld.extra_tags)
        _extra_unw = UNWIELDY in ld.extra_tags
        self.unwieldy_non_shield = bool(_wpn_unw or _arm_unw or _dual_unw or _extra_unw)
        # Convenience: derived flags for the inner loop
        self.shield_init = SHIELDS[ld.shield]["init"] if ld.shield else 0

    @staticmethod
    def _compute_tags(weapon_profile, shield_name, ld, has_both, first):
        tags = set(weapon_profile["tags"]) | set(ld.extra_tags)
        # Retinue-innate keywords (e.g. Knight Templar: Unshakable + Steadfast). Steadfast as a
        # tag is what the Rout check reads, so a retinue with steadfast=True never Routs.
        # Morale-keyword data keys -> tags (the masks read tags). A retinue sets ONE of these.
        _ret = RETINUES[ld.retinue]
        if _ret.get("steadfast", False):
            tags.add("Steadfast")
        if _ret.get("unshakable", False):
            tags.add("Unshakable")
        if _ret.get("unbreakable", False):
            tags.add(UNBREAKABLE)
        if _ret.get("zealot", False):
            tags.add("Zealot")
        if _ret.get("rally", False):
            tags.add("Rally")
        if _ret.get("resolute", False):
            tags.add("Resolute")
        if shield_name:
            tags |= set(SHIELDS[shield_name]["tags"])
        # Armor-granted initiative tags (e.g. Full Plate: Immune Nimble).
        tags |= set(ARMORS[ld.armor].get("tags", []))
        # Dual-equip Unwieldy: applies when carrying BOTH a real melee weapon (not Farm Tools) AND
        # a ranged weapon. Negated by 'Immune Unwieldy' (Tiltyard mastery), which is the source of
        # truth here — the tiltyard_mastery flag is set inconsistently across generators, so we read
        # the mastery TAG instead. Melee-only / ranged-only builds never get dual-equip Unwieldy.
        has_real_melee = ld.weapon is not None and ld.weapon != "Farm Tools"
        is_dual_equipping = has_both and has_real_melee and bool(ld.ranged)
        if is_dual_equipping:
            tags.add(UNWIELDY)
        # Immune Unwieldy (Tiltyard mastery) negates ALL Unwieldy — dual-equip, weapon-intrinsic
        # (Halberd/Pike/etc.), AND armor-intrinsic (Chainmail/Full Plate). It is a general immunity.
        if IMMUNE_UNWIELDY in tags:
            tags.discard(UNWIELDY)
        # Immune Steady (deprecated — no armor grants it anymore). Branch kept harmless in case
        # a build injects the tag manually; cancels the weapon's Steady init-floor if present.
        if "Immune Steady" in tags:
            tags.discard(STEADY)
        return tags

    def base_init(self, first):
        i = self.init_first if first else self.init_normal
        i += self.shield_init
        tags = self.tags_first if first else self.tags_normal
        # Nimble grants +1 first-skirmish init — unless suppressed by Immune Nimble (heavy armor).
        if NIMBLE in tags and "Immune Nimble" not in tags and first:
            i += 1
        if self.is_attacker and first:
            i += 1
        # Strain: -1 initiative (combat-phase effect). Negated by Immune Strain (Royal Pavilion).
        if STRAIN in tags and IMMUNE_STRAIN not in tags:
            i -= 1
        # Blocked: -1 initiative in the FIRST skirmish only — unless Immune Blocked (Rising Prowess).
        if "Blocked" in tags and "Immune Blocked" not in tags and first:
            i -= 1
        # Blocked Blunder (experimental Cunning rework): force a BLUNDER in skirmish 1 by
        # dropping Initiative to the -2 floor that turn (to-Strike becomes 6+). Immune Blocked negates.
        if "Blocked Blunder" in tags and "Immune Blocked" not in tags and first:
            i = min(i, -2)
        # Ministry mastery (MinInit+1): flat +1 initiative every skirmish.
        if "MinInit+1" in tags:
            i += 1
        # Test-only parametric init modifier: a tag like "TestInit+2" or "TestInit-1" applies a
        # flat delta every skirmish. Used by the controlled initiative sweep (analysis) to vary
        # ONLY initiative on a fixed chassis. No effect in normal play (tag never generated).
        for _t in tags:
            if _t.startswith("TestInit"):
                try:
                    i += int(_t[len("TestInit"):])
                except ValueError:
                    pass
                break
        return i + self.init_bonus

    def weapon_ap(self, first):
        return self.ap_first if first else self.ap_normal

    def tags(self, first):
        return self.tags_first if first else self.tags_normal


# ===== Vectorized strike resolution =====

# DEPRECATED: Deadly (formerly Shatter Armor) is now always Parry/Recover-on-natural-6 —
# handled inside _saves_kernel. Toggle kept only so old notebooks don't crash on import.
SHATTER_PIERCES_PARRY = True
# Experiment toggle: if True, Parry is rolled BEFORE the armor save (hit -> parry -> save -> regen)
# instead of the default (hit -> save -> parry -> regen). Does not change casualties; raises ripostes.
# Save-ordering is now single-sourced in combat_kernel (SPEC B = parry-first).
from combat_kernel import PARRY_BEFORE_SAVE

# Army-scale constants. HALF-SCALE is now the default game: front 10 / reserve 5 / shake 5,
# with size-25 builds. (Old full-scale was 20/10/10 at size 50.) At 10 attack dice the chance
# of zero natural-6s is ~16% (vs ~3% at 20), so Destroy Shield / Shatter / Cleave are no longer
# near-automatic each skirmish. To revert to full scale: set 20/10/10 and regenerate size-50 pools.
FRONT_CAP = 10
RESERVE_CAP = 5
SHAKE_CAP = 5


# ── Shared combat kernels (single source of truth) ──────────────────────────
# The three per-die kernels live in combat_kernel.py so batch_engine and this
# engine run IDENTICAL logic. Editing a kernel? Wipe the numba cache before
# trusting results (see combat_kernel.py header).
from combat_kernel import (
    _HAS_NUMBA, _njit,
    _strikes_kernel, _strikes_kernel_dual, _saves_kernel,
)
# Shared rules-math primitives (Deflect, Negate Tempered, Deadly clips, parry/
# recover thresholds) — extracted so the math can't drift between engines.
import combat_primitives as _cp
# signature: atk_crit5=False  →  atk_crit_floor=6
def _roll_strikes_vec(rng, n, target_th, front_line, atk_tags, defender_has_shield_flag,
                     defender_shield_destroyed, atk_bastard_2h_mask=None, atk_tags_2h=None,
                     defender_shield_immune=False, atk_crit_floor=6):
    """For each of n runs, roll up to 20 dice (front_line per run cap), count strikes.
    Returns: strikes (n,) (incl. Cleave extra hits), deadly_strikes (n,), destroyed_shield (n,)

    Deadly (formerly Shatter Armor): proc'd strikes resolve at AP -5 and can only be
    Parried/Recovered on a natural 6 (handled in the saves kernel).
    Cleave: each proc rolls ONE additional Strike die at the modified to-Strike value.
    atk_crit5 (Ministry rank 2): procs also fire on a natural 5 when the 5 is a hit.
    defender_shield_immune: shield carries Immune Destroy Shield (Heater) — cannot be destroyed.
    """
    target_th_orig = np.asarray(target_th)
    target_th = np.clip(target_th_orig, 2, 7)  # 7 means auto-fail
    auto_fail = (target_th >= 7)
    auto_pass = (target_th_orig < 2)

    front_line = np.asarray(front_line, dtype=np.int64)
    rolls = rng.integers(1, 7, size=(n, 20), dtype=np.int8)
    cleave_rolls = rng.integers(1, 7, size=(n, 20), dtype=np.int8)

    has_dual = atk_bastard_2h_mask is not None and atk_tags_2h is not None

    af = np.broadcast_to(auto_fail, (n,)).astype(np.bool_).copy()
    ap = np.broadcast_to(auto_pass, (n,)).astype(np.bool_).copy()
    th_clip = np.broadcast_to(target_th, (n,)).astype(np.int64).copy()

    def _deadly_in(tags):
        # Halfsword uses the same proc-strike machinery as Deadly (natural-6 strikes
        # get special handling); the halfsword_mode flag at the save step reinterprets
        # those procs as the Halfsword bundle instead of the Deadly bundle.
        return (SHATTER_ARMOR in tags) or ("Shatter Armor" in tags) or (HALFSWORD in tags)

    if has_dual:
        deadly_base = _deadly_in(atk_tags)
        deadly_2h = _deadly_in(atk_tags_2h)
        run_has_deadly = np.where(atk_bastard_2h_mask, deadly_2h, deadly_base)
        cleave_base = (CLEAVE in atk_tags)
        cleave_2h = (CLEAVE in atk_tags_2h)
        run_has_cleave = np.where(atk_bastard_2h_mask, cleave_2h, cleave_base)
        strikes, deadly_strikes, proc_count = _strikes_kernel_dual(
            rolls, cleave_rolls, front_line, th_clip, af, ap,
            run_has_deadly.astype(np.bool_).copy(), run_has_cleave.astype(np.bool_).copy(),
            int(atk_crit_floor))
    else:
        strikes, deadly_strikes, proc_count = _strikes_kernel(
            rolls, cleave_rolls, front_line, th_clip, af, ap,
            _deadly_in(atk_tags), bool(CLEAVE in atk_tags), int(atk_crit_floor),
            bool(DUAL_WIELD in atk_tags))

    # Destroy Shield: any proc destroys defender's shield (if not already destroyed, not immune).
    destroyed_shield = np.zeros(n, dtype=bool)
    if DESTROY_SHIELD in atk_tags and defender_has_shield_flag and not defender_shield_immune:
        destroyed_shield = (proc_count > 0) & (~defender_shield_destroyed)

    return strikes, deadly_strikes, destroyed_shield


def _abf_effective_ap(ap, attacker_abf, defender_abf):
    """ABF package AP math. Outgoing first (attacker's weapons gain -1 AP), then the
    defender's incoming reduction (+1, toward 0) CLAMPED at 0 — reducing a 0-AP
    attack cannot push it positive. Applied to the weapon AP itself, so Deadly's
    +5 in the saves kernel stacks on this adjusted value (per ruling)."""
    eff = ap - (1 if attacker_abf else 0)
    if defender_abf:
        eff = np.minimum(eff + 1, 0)
    return eff


def _regen_threshold(def_tags, atk_tags=None):
    """Return the defender's Recover threshold (4, 5, or 6), or None if no Recover.
    Accepts 'Recover'/'Recover 6/5/4' (and legacy 'Regenerate' forms). Lowest wins.

    Serrated (attacker keyword, legacy 'Rend'): worsens the Recover roll by 1 per source,
    capped at 6+ (a natural 6 always has a chance — Serrated can no longer fully negate)."""
    thresholds = []
    for t in def_tags:
        if t in (RECOVER, "Recover 6", "Regenerate", "Regenerate 6"):
            thresholds.append(6)
        elif t in ("Recover 5", "Regenerate 5"):
            thresholds.append(5)
        elif t in ("Recover 4", "Regenerate 4"):
            thresholds.append(4)
    if not thresholds:
        return None
    thr = min(thresholds)
    if atk_tags is not None:
        serr = sum(2 for t in atk_tags if t in (SERRATED, "Rend"))
        if serr:
            thr = min(6, thr + serr)
    # Enduring (Hospitaller mastery): Recover still gets a 6+ save while Fatigued. Encoded as a
    # NEGATIVE threshold so it flows through both engines' single regen path (build_regen_thr)
    # without threading a new param; build_regen_thr decodes the sign. Magnitude = the normal
    # (Serrated-adjusted) pre-fatigue threshold; sign = Enduring.
    if ENDURING in def_tags:
        return -thr
    return thr


def _has_regen_reroll(tags):
    """Hospitaller mastery — re-roll failed Regenerate rolls."""
    return "Regenerate Reroll" in tags


def _best_response_table(tab, me_static, opp_static, me_first, opp_first):
    """Weapon-aware Outrider counter table for ONE matchup.

    Returns a length-7 int array: for each opponent tactic index, the index of MY best
    response tactic. "Best" = maximizes my expected NET advantage in the revealed skirmish,
    computed from the SAME tactic mods combat uses (`tab`) plus this matchup's real combat
    quantities (base init, to-hit, AP vs the opponent's armor+shield). This makes the
    Outrider play the actual best response for the specific weapons on the table, and it
    respects the two things the old global heuristic missed:
      - the initiative TRIP CLIFF (a tactic that pushes me to init <= -2 means I deal 0;
        a tactic that pushes the opponent to <= -2 means they deal 0),
      - AP vs the defender's save (my kill rate per hit depends on my AP and their armor+shield).

    me_first / opp_first: whether to read first-skirmish stats (Nimble/Seize/ranged etc.).
    Computed once per matchup at setup; pure scalar arithmetic over the 7x7 grid (cheap).
    """
    n = 7
    # Static quantities for this matchup (the revealed skirmish).
    me_base_init = me_static.base_init(me_first)
    opp_base_init = opp_static.base_init(opp_first)
    me_to_hit = me_static.to_hit
    opp_to_hit = opp_static.to_hit
    me_ap = me_static.weapon_ap(me_first)
    opp_ap = opp_static.weapon_ap(opp_first)
    # Defender save targets (lower = tougher). Shield bonus + armor; AP raises the chance to fail.
    # My strikes hit the OPPONENT: their effective save = opp_armor - my_ap - opp_shield_bonus.
    opp_save_vs_me = opp_static.armor_save - opp_static.shield_bonus_start
    me_save_vs_opp = me_static.armor_save - me_static.shield_bonus_start
    # Shield -1TBH raises the attacker's target-to-hit by +1 (harder to hit a shielded foe).
    me_tbh_from_opp = opp_static.shield_tbh_penalty_start   # I face their shield
    opp_tbh_from_me = me_static.shield_tbh_penalty_start     # they face my shield
    me_th_self = me_static.shield_th_penalty_start           # my own heavy shield hampers me
    opp_th_self = opp_static.shield_th_penalty_start         # their own heavy shield hampers them
    # Front line size cancels out of the argmax (same scale both sides per cell), use 20.
    FRONT = 20.0

    def p_hit(target_th):
        # need d6 >= target_th; clamp to [2,6] playable, 7+ = auto-miss, <2 = auto-hit region
        t = max(2, min(7, target_th))
        if target_th >= 7: return 0.0
        return (7 - t) / 6.0  # rolls t..6 succeed

    def p_fail_save(save_target):
        # defender fails (casualty) if roll < save_target; save_target<2 = auto-pass (0 fail)
        if save_target < 2: return 0.0
        s = min(7, save_target)
        return (s - 1) / 6.0  # rolls 1..s-1 fail

    a_I, a_TH, b_I, b_TH = tab["a_I"], tab["a_TH"], tab["b_I"], tab["b_TH"]
    end = tab["end"]; no_combat = tab["no_combat"]

    counter = np.zeros(n, dtype=np.int8)
    for opp_tac in range(n):
        best_score = -1e18
        best_my = 0
        found_engaging = False
        for my_tac in range(n):
            # tab is indexed [a_tac, b_tac] with A as "me" here (Outrider counter side = A side
            # of the table). The caller passes tab already oriented so me=A, opp=B.
            # SKIP tactics that end the battle / avoid combat (Fall Back): the Outrider counter
            # is choosing how to FIGHT the revealed pick. Fall Back forfeits the win (it can
            # never win), so it must never be selected as a "best response" — even when every
            # engaging option is a losing exchange, fighting retains a chance; Fall Back is a
            # guaranteed loss. (This was the bug: Fall Back scored -0.01 and won the argmax
            # whenever all real tactics scored worse, ~18% of cells.)
            if end[my_tac, opp_tac] or no_combat[my_tac, opp_tac]:
                continue
            found_engaging = True
            my_init = max(-2, min(me_static.max_init, me_base_init + int(a_I[my_tac, opp_tac])))
            op_init = max(-2, min(opp_static.max_init, opp_base_init + int(b_I[my_tac, opp_tac])))
            my_tripped = my_init <= -2
            op_tripped = op_init <= -2
            # my expected kills on the opponent this skirmish.
            # Tripped (init <= -2) = BLUNDER: still fights, but to-hit clamped to 6+ best (not 0
            # kills). This matches the real combat loop (a_th_pre = max(.,6) when tripped), so the
            # Outrider decision model doesn't over-avoid low-init states.
            my_th = me_to_hit - int(a_TH[my_tac, opp_tac]) + me_tbh_from_opp + me_th_self
            if my_tripped:
                my_th = max(my_th, 6)
            my_kills = FRONT * p_hit(my_th) * p_fail_save(opp_save_vs_me - me_ap)
            # opponent expected kills on me
            op_th = opp_to_hit - int(b_TH[my_tac, opp_tac]) + opp_tbh_from_me + opp_th_self
            if op_tripped:
                op_th = max(op_th, 6)
            op_kills = FRONT * p_hit(op_th) * p_fail_save(me_save_vs_opp - opp_ap)
            score = my_kills - op_kills
            if score > best_score:
                best_score = score
                best_my = my_tac
        counter[opp_tac] = best_my
    return counter


def _counter_weights_from_table(counter_tbl, opp_tac_idx, n_runs, counter_weight=0.8):
    """Build (n_runs, 7) tactic weights for the Outrider side from a per-matchup best-response
    table. For each run, look up the best response to that run's opponent tactic and put
    `counter_weight` on it, spreading the remainder across the other six tactics.
    """
    counter_indices = counter_tbl[opp_tac_idx]  # shape (n_runs,)
    weights = np.full((n_runs, 7), (1 - counter_weight) / 6.0, dtype=np.float64)
    weights[np.arange(n_runs), counter_indices] = counter_weight
    return weights


def _roll_saves_vec(rng, n, save_target, n_strikes, shatter_strikes, atk_has_poison, def_has_parry, def_regen_threshold, def_has_regen_reroll=False, atk_unstoppable=False, def_has_riposte=False, def_parry_improved=False, def_can_parry_shatter=False, atk_is_ranged=False, def_fat=None, def_planishing=False, def_crit5=False, atk_has_deflect=False, atk_has_halfsword=False, atk_ignores_tempered=False):
    """For each of n runs with n_strikes hits to resolve, return (casualties, ripostes).
    Saves roll d6; saves on roll >= save_target (lower = better).
    Deadly strikes (shatter_strikes count): resolve at save_target +5 (Deadly's AP -5),
      and can only be Parried or Recovered on a NATURAL 6.
    Planishing (def_planishing): the save target can never exceed 6+ (no auto-fail from AP),
      for both normal and Deadly strikes.
    Poison: a natural 6 to Save fails.
    Parry: pre/post-save per PARRY_BEFORE_SAVE. Threshold = 5+ (4+ Improved), worsened by
      +1 vs Unstoppable, +1 vs ranged, +1 per Fatigue token (def_fat), capped at 6+.
    Recover: threshold from _regen_threshold (incl. Serrated), worsened by Fatigue, capped 6+.
    def_crit5 (defender's Ministry rank 2): a natural-5 Parry that succeeds also Ripostes.
    (def_has_regen_reroll / def_can_parry_shatter are legacy parameters, ignored.)
    """
    max_strikes = int(n_strikes.max()) if n_strikes.any() else 0
    if max_strikes == 0:
        return np.zeros(n, dtype=np.int32), np.zeros(n, dtype=np.int32)
    max_strikes = min(max_strikes, 40)

    # ── Build kernel primitives via the SHARED rules-math layer (combat_primitives) ──
    # Identical math to the batch engine; this is the C2 single-source. All inputs are
    # broadcast to (n,) inside the helpers, so the per-matchup scalars here and the
    # per-slot arrays in batch resolve through the same code.
    save_clip_arr, deadly_clip_arr, ap_arr = _cp.build_save_clips(
        n, save_target, def_planishing, atk_ignores_tempered)
    parry_thr_arr, deflect = _cp.build_parry_thr(
        n, def_parry_improved, atk_unstoppable, atk_is_ranged, atk_has_deflect, def_fat)
    regen_thr_arr = _cp.build_regen_thr(n, def_regen_threshold, def_fat)

    parry_mask = _cp._as_bool_arr(def_has_parry, n)
    riposte_mask = _cp.build_riposte_mask(n, def_has_riposte, deflect)
    n_strikes_arr = np.asarray(n_strikes, dtype=np.int64)
    deadly_arr = np.asarray(shatter_strikes, dtype=np.int64)

    any_parry = bool(parry_mask.any())
    any_regen = bool((regen_thr_arr > 0).any())

    rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8)
    parry_rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8) if any_parry \
        else np.zeros((n, max_strikes), dtype=np.int8)
    regen_rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8) if any_regen \
        else np.zeros((n, max_strikes), dtype=np.int8)

    rip5_arr = np.zeros(n, dtype=np.bool_)   # Crit 5 widens Cleave/Deadly only — not Riposte (deprecated)

    casualties, ripostes = _saves_kernel(
        rolls, parry_rolls, regen_rolls,
        n_strikes_arr, deadly_arr, save_clip_arr, deadly_clip_arr, ap_arr,
        _cp._as_bool_arr(atk_has_poison, n), parry_mask, parry_thr_arr, regen_thr_arr,
        riposte_mask, rip5_arr,
        bool(PARRY_BEFORE_SAVE), bool(atk_has_halfsword))
    return casualties, ripostes


def _shaking_test_vec(rng, n, field_size, shaking_value, mask):
    """Per-run shaking test. Each retinue in field rolls; flees if roll < shaking_value.
    Only runs in `mask` actually do the test.
    `shaking_value` may be a scalar OR a per-run array (n,) — the latter lets fatigue raise the
    shake target per run (each fatigue token = -1 to shake, i.e. +1 to the target).
    Returns casualties (n,).
    """
    sv = np.asarray(shaking_value)
    if sv.ndim == 0:
        if not mask.any() or int(sv) < 1:
            return np.zeros(n, dtype=np.int32)
        sv = np.full(n, int(sv), dtype=np.int64)
    else:
        if not mask.any():
            return np.zeros(n, dtype=np.int32)
        sv = sv.astype(np.int64)
    max_field = int(field_size.max())
    if max_field == 0:
        return np.zeros(n, dtype=np.int32)
    rolls = rng.integers(1, 7, size=(n, max_field), dtype=np.int8)
    field_idx = np.arange(max_field)[None, :]
    in_field = field_idx < field_size[:, None]
    flees = (rolls < sv[:, None]) & in_field & mask[:, None]
    return flees.sum(axis=1).astype(np.int32)


# ===== Main matchup loop =====

def run_matchup_vec(ld_a, ld_b, n_runs=100, max_skirmishes=20, seed=None, alternate_attacker=True,
                    a_init_size=None, b_init_size=None, a_init_endurance=None, b_init_endurance=None,
                    return_per_run_state=False,
                    a_playstyle=None, b_playstyle=None,
                    attacker_mode="balanced",
                    fb_min_skirmish=1,
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

    # === Domain-standing OPPONENT debuffs (confers:*) ===
    # A build with Established Cunning carries a "confers:Blocked" marker; Sovereign Cunning carries
    # "confers:Strain". These are NOT self-effects — they debuff the OPPONENT. Here we transfer them:
    # strip 'confers:X' from each side's own tags and add X to the OTHER side's extra_tags, so the
    # rest of the engine (which reads extra_tags) applies Blocked/Strain to the correct army. Done
    # once, before any StaticArmy is built.
    def _apply_confers(ld_self, ld_opp):
        confers = {t.split(":", 1)[1] for t in ld_self.extra_tags if t.startswith("confers:")}
        self_clean = frozenset(t for t in ld_self.extra_tags if not t.startswith("confers:"))
        ld_self2 = ld_self._replace(extra_tags=self_clean)
        if confers:
            ld_opp2 = ld_opp._replace(extra_tags=frozenset(set(ld_opp.extra_tags) | confers))
        else:
            ld_opp2 = ld_opp
        return ld_self2, ld_opp2
    if any(t.startswith("confers:") for t in ld_a.extra_tags) or \
       any(t.startswith("confers:") for t in ld_b.extra_tags):
        # apply A's confers to B, then B's confers to A (order independent — disjoint targets)
        ld_a, ld_b = _apply_confers(ld_a, ld_b)
        ld_b, ld_a = _apply_confers(ld_b, ld_a)

    tab = get_tactic_tables()
    # Lazy import to avoid circular dependency
    from playstyles import resolve_playstyle_weights, sample_tactic_indices, outrider_counter_weights
    try:
        from playstyles import get_initiate_rate
    except ImportError:
        # Older playstyles.py without per-playstyle initiate rates.
        # Default to 0.5 for all playstyles (neutral 50/50 split).
        def get_initiate_rate(_playstyle):
            return 0.5

    # === Tactic-reveal (Outrider Intercept Post / legacy Ministry tag) detection ===
    # Tag forms (now granted by Outrider Intercept Post, a Cunning monument):
    #   "Outrider: every"  - counter-picks every skirmish (legacy/analysis)
    #   "Outrider: first"  - counter-picks first skirmish only
    #   "Outrider: once"   - counter-picks once per battle (modeled as first; base)
    # If neither side has the tag, behavior is unchanged. (Tag name kept for engine compat.)
    def _outrider_mode(tags):
        for t in tags:
            if t == "Outrider: first_two": return "first_two"
            if t == "Outrider: every": return "every"
            if t == "Outrider: first": return "first"
            if t == "Outrider: once":  return "once"
        return None
    a_outrider = _outrider_mode(ld_a.extra_tags)
    b_outrider = _outrider_mode(ld_b.extra_tags)
    # Mutual tactic-reveal cancels (per design).
    if a_outrider and b_outrider:
        a_outrider = b_outrider = None

    # === Seize the Initiative (Ministry of Military Strategy) detection ===
    # "Seize: first"     - Ministry base: Seize the +1 on the FIRST skirmish only; opponent never gets it.
    # "Seize: first_two" - Ministry mastery (all required buildings): Seize on the FIRST TWO
    #                      skirmishes (skirmish 1 and 2); opponent never gets it.
    # "Seize: every"     - legacy/analysis only: Seize EVERY skirmish. Kept for A/B comparison.
    def _seize_mode(tags):
        if "Seize: first_two" in tags: return "first_two"
        if "Seize: every" in tags: return "every"
        if "Seize: first" in tags: return "first"
        return None
    a_seize_mode = _seize_mode(ld_a.extra_tags)
    b_seize_mode = _seize_mode(ld_b.extra_tags)
    a_has_ministry_innate = a_seize_mode is not None
    b_has_ministry_innate = b_seize_mode is not None
    # Persistent (every-skirmish) seize — legacy "every" only. "first_two" is handled in the
    # skirmish loop (it applies to skirmish index 1 specifically, not all subsequent skirmishes).
    a_seize_persistent = (a_seize_mode == "every")
    b_seize_persistent = (b_seize_mode == "every")
    # Second-skirmish seize: Ministry mastery grants Seize on skirmish 2 (index 1) as well as
    # skirmish 1. ("every" also covers skirmish 2, so include it.)
    a_seize_second = (a_seize_mode in ("first_two", "every"))
    b_seize_second = (b_seize_mode in ("first_two", "every"))

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

    # Second-skirmish seize only applies when this side actually retains its Seize claim
    # (Ministry-innate AND not both-have, since two Ministries cancel). Ministry is a unique
    # building so both-have never occurs in practice, but keep it consistent.
    both_ministry = a_has_ministry_innate and b_has_ministry_innate
    a_seize_second = a_seize_second and not both_ministry
    b_seize_second = b_seize_second and not both_ministry

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

    # Weapon-aware Outrider counter tables (computed once per matchup). When a side has the
    # Outrider Intercept Post, it sees the opponent's tactic and plays the BEST RESPONSE for
    # THIS specific weapon matchup — not a global heuristic. tab is indexed [a_tac, b_tac];
    # for A's table "me"=A so we pass tab as-is; for B's table we pass a transposed/oriented
    # view so "me"=B (swap a_*/b_* mod roles) by building a B-oriented tab.
    a_counter_tbl = None
    b_counter_tbl = None
    if a_outrider is not None:
        a_counter_tbl = _best_response_table(tab, a_static, b_static, me_first=True, opp_first=True)
    if b_outrider is not None:
        # Orient tab so "me"=B: swap the a_/b_ mod arrays and transpose so index is [b_tac, a_tac].
        tab_b = {"a_I": tab["b_I"].T, "a_TH": tab["b_TH"].T,
                 "b_I": tab["a_I"].T, "b_TH": tab["a_TH"].T,
                 "end": tab["end"].T, "no_combat": tab["no_combat"].T}
        b_counter_tbl = _best_response_table(tab_b, b_static, a_static, me_first=True, opp_first=True)


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
    # Rally: persistent per-battle "first break check already auto-passed" flags (reset each battle).
    a_break_used = np.zeros(n_runs, dtype=bool)
    b_break_used = np.zeros(n_runs, dtype=bool)
    a_panic_used = np.zeros(n_runs, dtype=bool)
    b_panic_used = np.zeros(n_runs, dtype=bool)
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
    # Combat-only casualties from the previous skirmish — the heal trigger reads these (heal cannot
    # restore shake/rout losses), and Trigger 2 nets this skirmish's combat losses against the heal.
    a_prev_combat_casualties = np.zeros(n_runs, dtype=np.int32)
    b_prev_combat_casualties = np.zeros(n_runs, dtype=np.int32)
    a_has_apo_heal = "Apothecary Heal" in ld_a.extra_tags
    b_has_apo_heal = "Apothecary Heal" in ld_b.extra_tags

    # Casualty source tracking (cumulative across the battle, per run)
    a_kill_cas_total  = np.zeros(n_runs, dtype=np.int32)   # losses to combat strikes
    b_kill_cas_total  = np.zeros(n_runs, dtype=np.int32)
    a_shake_cas_total = np.zeros(n_runs, dtype=np.int32)   # losses to shaking test
    b_shake_cas_total = np.zeros(n_runs, dtype=np.int32)
    a_waver_cas_total = np.zeros(n_runs, dtype=np.int32)   # losses to the Waver test (>5 net combat)
    b_waver_cas_total = np.zeros(n_runs, dtype=np.int32)
    a_rout_cas_total  = np.zeros(n_runs, dtype=np.int32)   # losses to Army Rout (whole army)
    b_rout_cas_total  = np.zeros(n_runs, dtype=np.int32)
    # Cause-of-wipe: 0=alive/indecisive, 1=combat, 2=shake, 3=rout
    a_cause_of_wipe = np.zeros(n_runs, dtype=np.int8)
    b_cause_of_wipe = np.zeros(n_runs, dtype=np.int8)

    # ── Hit / save / strike-order accumulators (for the analysis matrix) ──
    # Hits: strikes are dice that landed (a_strikes_initial = A's landed hits this skirmish). We can't
    # cheaply recover "attempts" from the vectorized roller, so HIT RATE is reported as avg landed
    # hits per skirmish (a proxy for offensive output), not hits/attempts. Saves: a defender's
    # save rate = 1 - (failed saves / incoming hits) = 1 - casualties/strikes. Strike order: count
    # runs by who struck first on each skirmish (A-first / simultaneous / B-first), summed over the
    # battle then normalized to rates at the end.
    a_hits_total   = np.zeros(n_runs, dtype=np.int64)   # A's landed strikes (offense)
    b_hits_total   = np.zeros(n_runs, dtype=np.int64)   # B's landed strikes
    a_incoming     = np.zeros(n_runs, dtype=np.int64)   # strikes A had to save against (B's hits)
    b_incoming     = np.zeros(n_runs, dtype=np.int64)   # strikes B had to save against (A's hits)
    a_failed_saves = np.zeros(n_runs, dtype=np.int64)   # A's casualties from saves (failed)
    b_failed_saves = np.zeros(n_runs, dtype=np.int64)
    sk_a_first = np.zeros(n_runs, dtype=np.int64)       # skirmishes A struck first
    sk_simul   = np.zeros(n_runs, dtype=np.int64)       # skirmishes simultaneous
    sk_b_first = np.zeros(n_runs, dtype=np.int64)       # skirmishes B struck first
    sk_engaged = np.zeros(n_runs, dtype=np.int64)       # skirmishes that actually engaged
    # First-skirmish-only (sk==0) tallies: A's kills dealt, A's deaths taken, A's saves made.
    fs_a_kills  = np.zeros(n_runs, dtype=np.int64)   # casualties A inflicted on B in skirmish 0
    fs_a_deaths = np.zeros(n_runs, dtype=np.int64)   # casualties A took in skirmish 0
    fs_a_incoming = np.zeros(n_runs, dtype=np.int64) # hits A had to save vs in skirmish 0
    fs_a_failed   = np.zeros(n_runs, dtype=np.int64) # A's failed saves in skirmish 0

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
        # Riposte counter-damage this skirmish (reset each iteration; set in the save blocks below).
        a_riposte_casualties = np.zeros(n_runs, dtype=np.int32)
        b_riposte_casualties = np.zeros(n_runs, dtype=np.int32)

        # Apothecary mastery: at start of skirmish (after first), heal 1 retinue per 4 COMBAT
        # casualties taken in the previous skirmish. Cannot heal above size cap. Only active runs
        # heal (wiped runs stay wiped — per-run mask, not per-matchup). Heal applies ONLY to combat
        # losses — shake/rout casualties cannot be healed (they fled, they're gone).
        a_heal = np.zeros(n_runs, dtype=np.int32)
        b_heal = np.zeros(n_runs, dtype=np.int32)
        if not first:
            if a_has_apo_heal:
                a_heal = np.where(active, a_prev_combat_casualties // 4, 0).astype(np.int32)
                a_size = np.minimum(a_size + a_heal, ld_a.size).astype(np.int32)
            if b_has_apo_heal:
                b_heal = np.where(active, b_prev_combat_casualties // 4, 0).astype(np.int32)
                b_size = np.minimum(b_size + b_heal, ld_b.size).astype(np.int32)

        # Static stats for this skirmish
        a_tags = a_static.tags(first)
        b_tags = b_static.tags(first)
        # Is each side's attack this skirmish a RANGED strike? (first skirmish: yes if any ranged
        # equipped; later skirmishes: only pure-ranged multi-shot keeps firing.)
        a_atk_is_ranged = a_static.uses_ranged_first if first else a_static.uses_ranged_normal
        b_atk_is_ranged = b_static.uses_ranged_first if first else b_static.uses_ranged_normal
        a_ap = a_static.weapon_ap(first)
        b_ap = b_static.weapon_ap(first)
        a_base_init = a_base_init_first if first else a_base_init_norm
        b_base_init = b_base_init_first if first else b_base_init_norm
        # Ministry mastery ("Seize: first_two"): the Seize +1 also applies on the SECOND
        # skirmish (index 1). a_base_init_norm already includes the +1 for the legacy "every"
        # mode (a_seize_persistent); for "first_two" we add it only on skirmish index 1.
        if sk == 1:
            if a_seize_second and not a_seize_persistent:
                a_base_init = (a_base_init + 1).astype(np.int8)
            if b_seize_second and not b_seize_persistent:
                b_base_init = (b_base_init + 1).astype(np.int8)

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

        # Fall Back availability gate: FB is unavailable as a tactic before
        # skirmish index `fb_min_skirmish` (default 0 = always available). When
        # gated out, its weight is zeroed and the remaining tactics renormalize,
        # so the player simply picks another tactic that skirmish.
        if sk < fb_min_skirmish:
            a_weights = a_weights.copy(); a_weights[:, FB_IDX] = 0.0
            b_weights = b_weights.copy(); b_weights[:, FB_IDX] = 0.0

        # === Outrider Intercept Post tactic-reveal (counter-pick) ===
        # Determine if Ministry fires this skirmish for either side.
        #   "once"/"first" → skirmish 1 only (innate)
        #   "first_two"    → skirmishes 1 and 2 (Outrider mastery)
        #   "every"        → every skirmish (legacy/analysis)
        a_outrider_fires = (a_outrider == "every") or (a_outrider in ("first", "once") and first) \
                           or (a_outrider == "first_two" and sk <= 1)
        b_outrider_fires = (b_outrider == "every") or (b_outrider in ("first", "once") and first) \
                           or (b_outrider == "first_two" and sk <= 1)

        if a_outrider_fires:
            # B picks first (from its playstyle), A plays the weapon-aware best response.
            b_tac = sample_tactic_indices(b_weights, rng)
            a_weights = _counter_weights_from_table(a_counter_tbl, b_tac, n_runs, counter_weight=0.8)
            a_tac = sample_tactic_indices(a_weights, rng)
        elif b_outrider_fires:
            # A picks first, B plays the weapon-aware best response.
            a_tac = sample_tactic_indices(a_weights, rng)
            b_weights = _counter_weights_from_table(b_counter_tbl, a_tac, n_runs, counter_weight=0.8)
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
        a_immune_unwieldy = IMMUNE_UNWIELDY in a_tags
        b_immune_unwieldy = IMMUNE_UNWIELDY in b_tags
        # "Shield is the SOLE Unwieldy source" — true when the shield carries Unwieldy and there is no
        # OTHER Unwieldy contributor (weapon/armor/dual-equip). Only then does destroying the shield
        # lift the Unwieldy init-clamp (a destroyed shield returns ALL its negatives).
        a_shield_only_unwieldy = a_static.shield_unwieldy and not a_static.unwieldy_non_shield
        b_shield_only_unwieldy = b_static.shield_unwieldy and not b_static.unwieldy_non_shield
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
            if STEADY in a_tags:
                a_I_mod = np.where(a_I_mod < 0, 0, a_I_mod)
            if UNWIELDY in a_tags and not a_immune_unwieldy:
                # A destroyed shield lifts its OWN Unwieldy clamp — but only on runs where the shield
                # is destroyed AND the shield is the sole Unwieldy source (weapon/armor/dual-equip
                # Unwieldy must still clamp). a_shield_only_unwieldy is True when removing the shield
                # leaves no other Unwieldy source.
                if a_static.shield_unwieldy and a_shield_only_unwieldy:
                    a_clamp = a_I_mod > 0
                    a_I_mod = np.where(a_clamp & (~a_shield_destroyed), 0, a_I_mod)
                else:
                    a_I_mod = np.where(a_I_mod > 0, 0, a_I_mod)
        if b_bastard_2h_mask is not None:
            b_in_1h = ~b_bastard_2h_mask
            b_in_2h = b_bastard_2h_mask
            b_I_mod = np.where(b_in_1h & (b_I_mod < 0), 0, b_I_mod)
            if not b_immune_unwieldy:
                b_I_mod = np.where(b_in_2h & (b_I_mod > 0), 0, b_I_mod)
        else:
            if STEADY in b_tags:
                b_I_mod = np.where(b_I_mod < 0, 0, b_I_mod)
            if UNWIELDY in b_tags and not b_immune_unwieldy:
                if b_static.shield_unwieldy and b_shield_only_unwieldy:
                    b_clamp = b_I_mod > 0
                    b_I_mod = np.where(b_clamp & (~b_shield_destroyed), 0, b_I_mod)
                else:
                    b_I_mod = np.where(b_I_mod > 0, 0, b_I_mod)

        # Variant B: a destroyed shield returns its initiative penalty too (the shield is gone, so is
        # its drag). Add back shield_init on destroyed runs so the bearer isn't left slower than if
        # they'd carried no shield at all.
        a_init_restore = np.where(a_shield_destroyed, -a_static.shield_init, 0).astype(np.int64)
        b_init_restore = np.where(b_shield_destroyed, -b_static.shield_init, 0).astype(np.int64)
        # Init ceiling is per-unit (Ministry innate raises it to 3); floor is -2 (Blunder).
        a_init = np.clip(a_base_init + a_I_mod + a_init_restore, -2, a_static.max_init)
        b_init = np.clip(b_base_init + b_I_mod + b_init_restore, -2, b_static.max_init)

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
        a_front = np.minimum(FRONT_CAP, a_size).astype(np.int8)
        b_front = np.minimum(FRONT_CAP, b_size).astype(np.int8)
        a_reserves = np.minimum(RESERVE_CAP, np.maximum(0, a_size - FRONT_CAP))
        b_reserves = np.minimum(RESERVE_CAP, np.maximum(0, b_size - FRONT_CAP))

        # To-hit targets (Yew Heart: ranged weapons +1 to hit, only on first skirmish with ranged equipped)
        yew_hit_bonus_a = -1 if (a_static.yew_heart and first and a_static.ranged) else 0
        yew_hit_bonus_b = -1 if (b_static.yew_heart and first and b_static.ranged) else 0
        # Weapon-intrinsic +1TH tag (e.g., Hunting Bow): -1 to target_th = easier to hit.
        # Applies whenever the weapon with the tag is the active weapon (so it's already
        # gated by skirmish via the tag set — on dual-equip, tags_normal switches to the
        # melee profile and the +1TH disappears; on pure-ranged it persists every skirmish).
        weapon_th_bonus_a = -1 if "+1TH" in a_tags else 0
        weapon_th_bonus_b = -1 if "+1TH" in b_tags else 0
        # First-skirmish-only +1TH (Ministry innate): -1 to target_th on the FIRST skirmish only.
        first_th_bonus_a = -1 if ("+1TH first" in a_tags and first) else 0
        first_th_bonus_b = -1 if ("+1TH first" in b_tags and first) else 0
        # After-first +1TH (Ministry mastery): -1 to target_th on every skirmish EXCEPT the first.
        # Combined with the innate first-skirmish +1TH, a mastered Ministry has -1 TH in ALL skirmishes
        # but never -2 in skirmish 1 (the two never overlap).
        rest_th_bonus_a = -1 if ("+1TH after_first" in a_tags and not first) else 0
        rest_th_bonus_b = -1 if ("+1TH after_first" in b_tags and not first) else 0
        # Shield -1TBH: defender's shield raises attacker's target_th by +1.
        # (This is now the ONLY source of "TBH" — the tactic matrix no longer carries
        # TBH; it expresses such effects directly as TH on the affected side.)
        # Disappears if the shield is destroyed mid-battle.
        b_shield_tbh = np.where(b_shield_destroyed, 0, b_static.shield_tbh_penalty_start)
        a_shield_tbh = np.where(a_shield_destroyed, 0, a_static.shield_tbh_penalty_start)
        # Shield -1TH (Tower): raises the BEARER's own target_th by +1 (hampers their attacks).
        # Lives on the bearer's side, and disappears if the bearer's shield is destroyed.
        # NOT affected by Unstoppable (Unstoppable ignores penalties imposed BY the enemy /
        # the enemy's shield; this is the bearer's own equipment drawback).
        a_shield_th_self = np.where(a_shield_destroyed, 0, a_static.shield_th_penalty_start)
        b_shield_th_self = np.where(b_shield_destroyed, 0, b_static.shield_th_penalty_start)
        # Unstoppable: attacker ignores to-hit PENALTIES from tactics & equipment.
        #   - Equipment: defender's shield -1TBH (the b_shield_tbh / a_shield_tbh term) is zeroed.
        #   - Tactics: any negative TH_mod (penalty that would raise target_th) is clamped to 0,
        #     so enemy defensive tactics can't lower the attacker's accuracy. Positive bonuses kept.
        # Fatigue and the attacker's own bonuses (+1TH, Yew) are unaffected.
        # Unstoppable (v2): ONLY ignores the defender's shield -1TBH penalty. It does NOT
        # ignore tactic to-hit penalties anymore — enemy defensive tactics still lower the
        # attacker's accuracy. Fatigue and the attacker's own bonuses are unaffected.
        a_unstoppable = UNSTOPPABLE in a_tags
        b_unstoppable = UNSTOPPABLE in b_tags
        a_th_mod_eff = a_TH_mod
        b_th_mod_eff = b_TH_mod
        # Negate Unstoppable (shield tag): cancels the attacker's Unstoppable entirely —
        # the defender's -1 to Strike survives (here), and the attacker's -1 to Parry is
        # suppressed at the save call site below.
        b_negate_unstoppable = NEGATE_UNSTOPPABLE in b_tags   # B is the defender vs A's strike
        a_negate_unstoppable = NEGATE_UNSTOPPABLE in a_tags
        # Negate Shielded (atomized out of Unstoppable): attacker ignores the defender's
        # Shielded (-1 to Strike). Keyed off NEGATE_SHIELDED in BOTH engines now. Previously vec
        # keyed this off (a_unstoppable OR "Immune Tactic TH") — the Immune-Tactic-TH coupling was
        # a vec-only divergence vs batch (batch only used Unstoppable), and vec's own comment said
        # Immune Tactic TH should NOT affect shield TBH. Unstoppable now drives ONLY the parry penalty.
        a_negshield = NEGATE_SHIELDED in a_tags
        b_negshield = NEGATE_SHIELDED in b_tags
        a_shield_tbh_eff = (b_shield_tbh * 0) if a_negshield else b_shield_tbh
        b_shield_tbh_eff = (a_shield_tbh * 0) if b_negshield else a_shield_tbh
        # === To-hit with the FATIGUE 6+ CAP ===
        # Rule: fatigue can never push the target-to-hit past 6+ (a fatigued unit always still
        # hits on a natural 6). The cap is applied to (base + improving mods + fatigue). Then
        # WORSENING mods (tactic -1TH, shield -1TBH/own-shield TH) apply ON TOP and CAN push the
        # target to 7+ (auto-miss). Improving mods (weapon/tactic +1TH, Yew) apply BEFORE the cap,
        # so a +1TH weapon offsets fatigue (keeps a fatigued unit at 5+ rather than 6+).
        #   improving (lower target): yew, weapon +1TH, positive tactic TH
        #   worsening (raise target): own/enemy shield TH, negative tactic TH
        a_th_improve = yew_hit_bonus_a + weapon_th_bonus_a + first_th_bonus_a + rest_th_bonus_a - np.maximum(a_th_mod_eff, 0)
        b_th_improve = yew_hit_bonus_b + weapon_th_bonus_b + first_th_bonus_b + rest_th_bonus_b - np.maximum(b_th_mod_eff, 0)
        # Immune Tactic TH (experimental Ministry mastery variant): ignores ALL tactic-sourced
        # -1TH — both enemy-imposed (e.g. Fighting Formation vs your Charge) and the self-penalty
        # of your own tactic (e.g. Ambush's own TH-1). Shield TBH/own-shield TH unaffected.
        a_tac_worsen = np.maximum(-a_th_mod_eff, 0) * (0 if "Immune Tactic TH" in a_tags else 1)
        b_tac_worsen = np.maximum(-b_th_mod_eff, 0) * (0 if "Immune Tactic TH" in b_tags else 1)
        a_th_worsen = a_shield_tbh_eff + a_shield_th_self + a_tac_worsen
        b_th_worsen = b_shield_tbh_eff + b_shield_th_self + b_tac_worsen
        # base + improving + fatigue, capped at 6 (the fatigue ceiling)
        a_th_pre = np.minimum(a_static.to_hit + a_th_improve + a_fat, 6)
        b_th_pre = np.minimum(b_static.to_hit + b_th_improve + b_fat, 6)
        # BLUNDER (init <= -2): clamp to 6+ at this step too (sets a too-good to-hit down to 6+),
        # then worsening mods can push beyond. Same mechanic as the fatigue cap.
        a_th_pre = np.where(a_tripped, np.maximum(a_th_pre, 6), a_th_pre)
        b_th_pre = np.where(b_tripped, np.maximum(b_th_pre, 6), b_th_pre)
        # Worsening mods apply after the cap and CAN exceed 6 → 7+ (auto-miss).
        a_target_th = a_th_pre + a_th_worsen
        b_target_th = b_th_pre + b_th_worsen
        # Save targets. Gilded Foundry mastery: incoming AP -1 (effective save improves by 1)
        # We model this by reducing the effective AP applied to the save target.
        # (Planishing no longer reduces AP; it caps the save target at 6+ inside _roll_saves_vec.)
        # ABF: outgoing weapons gain -1 AP (AP is negative; better = -1); incoming attacks
        # are reduced by 1 (toward 0). Applied to the weapon AP itself, so Deadly's +5 in
        # the saves kernel stacks on the ABF-adjusted target, per the ruling.
        b_ap_vs_a = _abf_effective_ap(b_ap, b_static.abf, a_static.abf)
        a_ap_vs_b = _abf_effective_ap(a_ap, a_static.abf, b_static.abf)
        a_save_target_against_b = (a_static.armor_save - b_ap_vs_a)
        a_save_target_against_b -= np.where(a_shield_destroyed, 0, a_static.shield_bonus_start)
        a_save_target_against_b = a_save_target_against_b - a_TS_mod
        b_save_target_against_a = (b_static.armor_save - a_ap_vs_b)
        b_save_target_against_a -= np.where(b_shield_destroyed, 0, b_static.shield_bonus_start)
        b_save_target_against_a = b_save_target_against_a - b_TS_mod

        # Immune Poison: defender's Apothecary innate blocks Poison effect
        a_effective_poison = (POISON in a_tags) and ("Immune Poison" not in b_tags)
        b_effective_poison = (POISON in b_tags) and ("Immune Poison" not in a_tags)

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
            defender_shield_immune=b_static.shield_immune, atk_crit_floor=(4 if "Crit 4" in a_tags else (5 if "Crit 5" in a_tags else 6)),
        )
        # Mask: only count strikes from runs where A actually fights this skirmish
        # BLUNDER: init<=-2 no longer prevents striking; instead to_hit is set to 6+ (handled below).
        a_fights = proceed & (a_size > 0)
        a_strikes_initial = np.where(a_fights, a_strikes_initial, 0)
        a_shatter = np.where(a_fights, a_shatter, 0)
        a_destroys_shield = a_destroys_shield & a_fights

        # B saves against A's strikes
        b_casualties, b_ripostes = _roll_saves_vec(
            rng, n_runs, b_save_target_against_a, a_strikes_initial, a_shatter,
            atk_has_poison=a_effective_poison,
            def_has_parry=(((PARRY in b_tags) | ("Improved Parry" in b_tags))),
            def_regen_threshold=_regen_threshold(b_tags, a_tags),
            def_has_regen_reroll=_has_regen_reroll(b_tags),
            atk_unstoppable=(a_unstoppable and not b_negate_unstoppable),
            def_has_riposte=((RIPOSTE in b_tags)),
            def_parry_improved=("Improved Parry" in b_tags),
            def_can_parry_shatter=(RIPOSTE in b_tags),
            atk_is_ranged=a_atk_is_ranged,
            atk_has_deflect=(DEFLECT in a_tags),
            atk_has_halfsword=(HALFSWORD in a_tags),
            atk_ignores_tempered=(NEGATE_TEMPERED in a_tags),
        
            def_fat=b_fat, def_planishing=b_static.planishing, def_crit5=("Crit 5" in b_tags),
        )
        b_casualties = np.minimum(b_casualties, b_front).astype(np.int32)
        # RIPOSTE: B parried some of A's hits on a natural 6 → B strikes A back, once per trigger, at
        # B's weapon AP. Single clean strikes: no Cleave/Shatter (shatter=0). B's Unstoppable reduces
        # A's parry; B's Rend worsens A's regen (both via b_tags as the riposter). A's poison N/A
        # (B is striking). Resolve and add to A's casualties this skirmish.
        if np.any(b_ripostes > 0):
            a_rip_cas, _ = _roll_saves_vec(
                rng, n_runs, a_save_target_against_b, b_ripostes, np.zeros(n_runs, dtype=np.int64),
                atk_has_poison=b_effective_poison,
                def_has_parry=(((PARRY in a_tags) | ("Improved Parry" in a_tags))),
                def_regen_threshold=_regen_threshold(a_tags, b_tags),
                def_has_regen_reroll=_has_regen_reroll(a_tags),
                atk_unstoppable=(b_unstoppable and not a_negate_unstoppable),
                def_has_riposte=False,   # ripostes do not themselves riposte
                def_parry_improved=("Improved Parry" in a_tags),
            
            def_fat=a_fat, def_planishing=a_static.planishing, def_crit5=("Crit 5" in a_tags),
        )
            a_riposte_casualties = np.minimum(a_rip_cas, a_front).astype(np.int32)
        else:
            a_riposte_casualties = np.zeros(n_runs, dtype=np.int32)

        # Now apply A's destroy-shield effect immediately (affects subsequent saves in this skirmish? No, only future skirmishes)
        # Per rules, shield destroyed for the rest of skirmish/battle. Apply now.
        b_shield_destroyed = b_shield_destroyed | a_destroys_shield

        # B's strike: depends on whether B is back-striking (a_first) or initial striker (b_first/simul)
        # Compute B's reduced front line for a_first cases
        b_front_after_a_strike = np.maximum(0, b_front - b_casualties)
        # Refill from reserves
        b_front_refilled = np.minimum(FRONT_CAP, b_front_after_a_strike + b_reserves)
        # In a_first cases, B uses b_front_refilled. In b_first/simul cases, B uses full b_front.
        b_effective_front = np.where(a_first_mask, b_front_refilled, b_front).astype(np.int8)

        b_fights = proceed & ((b_size - b_casualties) > 0 | b_first_mask | simul_mask)
        # If b lost everyone to A's first strike, b_size - b_casualties might be 0
        b_alive_for_strike = np.where(a_first_mask, (b_size - b_casualties) > 0, b_size > 0)
        b_fights = proceed & b_alive_for_strike

        b_strikes, b_shatter, b_destroys_shield = _roll_strikes_vec(
            rng, n_runs, b_target_th, b_effective_front, b_tags,
            a_static.has_shield, a_shield_destroyed,
            atk_bastard_2h_mask=b_bastard_2h_mask, atk_tags_2h=b_tags_2h,
            defender_shield_immune=a_static.shield_immune,
            atk_crit_floor=(4 if "Crit 4" in b_tags else (5 if "Crit 5" in b_tags else 6)),
        )
        b_strikes = np.where(b_fights, b_strikes, 0)
        b_shatter = np.where(b_fights, b_shatter, 0)
        b_destroys_shield = b_destroys_shield & b_fights

        a_casualties, a_ripostes = _roll_saves_vec(
            rng, n_runs, a_save_target_against_b, b_strikes, b_shatter,
            atk_has_poison=b_effective_poison,
            def_has_parry=(((PARRY in a_tags) | ("Improved Parry" in a_tags))),
            def_regen_threshold=_regen_threshold(a_tags, b_tags),
            def_has_regen_reroll=_has_regen_reroll(a_tags),
            atk_unstoppable=(b_unstoppable and not a_negate_unstoppable),
            def_has_riposte=((RIPOSTE in a_tags)),
            def_parry_improved=("Improved Parry" in a_tags),
            def_can_parry_shatter=(RIPOSTE in a_tags),
            atk_is_ranged=b_atk_is_ranged,
            atk_has_deflect=(DEFLECT in b_tags),
            atk_has_halfsword=(HALFSWORD in b_tags),
            atk_ignores_tempered=(NEGATE_TEMPERED in b_tags),
        
            def_fat=a_fat, def_planishing=a_static.planishing, def_crit5=("Crit 5" in a_tags),
        )
        a_casualties = np.minimum(a_casualties, a_front).astype(np.int32)
        # RIPOSTE: A parried some of B's hits on a natural 6 → A strikes B back at A's weapon AP.
        if np.any(a_ripostes > 0):
            b_rip_cas, _ = _roll_saves_vec(
                rng, n_runs, b_save_target_against_a, a_ripostes, np.zeros(n_runs, dtype=np.int64),
                atk_has_poison=a_effective_poison,
                def_has_parry=((PARRY in b_tags)),
                def_regen_threshold=_regen_threshold(b_tags, a_tags),
                def_has_regen_reroll=_has_regen_reroll(b_tags),
                atk_unstoppable=(a_unstoppable and not b_negate_unstoppable),
                def_has_riposte=False,
            
            def_fat=b_fat, def_planishing=b_static.planishing, def_crit5=("Crit 5" in b_tags),
        )
            b_riposte_casualties = np.minimum(b_rip_cas, b_front).astype(np.int32)
        else:
            b_riposte_casualties = np.zeros(n_runs, dtype=np.int32)

        # For b_first cases, A's strike happens AFTER B's. We computed A_strikes using
        # FULL a_front. That overcounts in b_first cases where A's front line was reduced.
        # We need to recompute A's strike for b_first cases with reduced front line.
        # The cleanest fix: zero out a_strikes for b_first cases and recompute.
        recompute_a = b_first_mask
        if recompute_a.any():
            a_front_after_b = np.maximum(0, a_front - a_casualties)
            a_reserves_avail = a_reserves
            a_front_refilled = np.minimum(FRONT_CAP, a_front_after_b + a_reserves_avail)
            a_effective_front_after_b = np.where(recompute_a, a_front_refilled, a_front).astype(np.int8)

            # Recompute A's strikes for the b_first cases
            new_a_strikes, new_a_shatter, new_a_destroys = _roll_strikes_vec(
                rng, n_runs, a_target_th, a_effective_front_after_b, a_tags,
                b_static.has_shield, b_shield_destroyed,
                atk_bastard_2h_mask=a_bastard_2h_mask, atk_tags_2h=a_tags_2h,
                defender_shield_immune=b_static.shield_immune,
                atk_crit_floor=(4 if "Crit 4" in a_tags else (5 if "Crit 5" in a_tags else 6)),
            )
            a_alive_for_back = a_front_after_b + a_reserves_avail > 0
            new_a_fights = recompute_a & a_alive_for_back
            # Update A's strikes only for recompute cases
            a_strikes_initial = np.where(recompute_a, np.where(new_a_fights, new_a_strikes, 0), a_strikes_initial)
            a_shatter = np.where(recompute_a, np.where(new_a_fights, new_a_shatter, 0), a_shatter)
            a_destroys_shield = np.where(recompute_a, new_a_destroys & new_a_fights, a_destroys_shield)

            # Recompute B's casualties using updated a_strikes for b_first runs
            new_b_casualties, new_b_ripostes = _roll_saves_vec(
                rng, n_runs, b_save_target_against_a, a_strikes_initial, a_shatter,
                atk_has_poison=a_effective_poison,
                def_has_parry=((PARRY in b_tags)),
                def_regen_threshold=_regen_threshold(b_tags, a_tags),
                def_has_regen_reroll=_has_regen_reroll(b_tags),
                atk_unstoppable=(a_unstoppable and not b_negate_unstoppable),
                def_has_riposte=((RIPOSTE in b_tags)),
                def_parry_improved=("Improved Parry" in b_tags),
                def_can_parry_shatter=(RIPOSTE in b_tags),
                atk_is_ranged=a_atk_is_ranged,
                atk_has_deflect=(DEFLECT in a_tags),
                atk_has_halfsword=(HALFSWORD in a_tags),
                atk_ignores_tempered=(NEGATE_TEMPERED in a_tags),
            
            def_fat=b_fat, def_planishing=b_static.planishing, def_crit5=("Crit 5" in b_tags),
        )
            new_b_casualties = np.minimum(new_b_casualties, b_front).astype(np.int32)
            b_casualties = np.where(recompute_a, new_b_casualties, b_casualties)
            b_shield_destroyed = b_shield_destroyed | (a_destroys_shield & recompute_a)
            # Recompute B's riposte vs A for the recomputed runs
            if np.any((new_b_ripostes > 0) & recompute_a):
                new_a_rip, _ = _roll_saves_vec(
                    rng, n_runs, a_save_target_against_b, new_b_ripostes, np.zeros(n_runs, dtype=np.int64),
                    atk_has_poison=b_effective_poison,
                    def_has_parry=((PARRY in a_tags)),
                    def_regen_threshold=_regen_threshold(a_tags, b_tags),
                    def_has_regen_reroll=_has_regen_reroll(a_tags),
                    atk_unstoppable=(b_unstoppable and not a_negate_unstoppable),
                    def_has_riposte=False,
                    def_parry_improved=("Improved Parry" in a_tags),
                
            def_fat=a_fat, def_planishing=a_static.planishing, def_crit5=("Crit 5" in a_tags),
        )
                new_a_rip = np.minimum(new_a_rip, a_front).astype(np.int32)
                a_riposte_casualties = np.where(recompute_a, new_a_rip, a_riposte_casualties)

        # Apply destroys-shield from B's strikes
        a_shield_destroyed = a_shield_destroyed | b_destroys_shield

        # Apply casualties to sizes. Riposte counter-damage (a_riposte_casualties = damage A takes
        # from B's riposte; b_riposte_casualties = damage B takes from A's riposte) added here, gated
        # to active runs.
        a_rip = np.where(active, a_riposte_casualties, 0).astype(np.int32)
        b_rip = np.where(active, b_riposte_casualties, 0).astype(np.int32)
        # Each initiative-step bundle is already capped at the front line (10) per side via the
        # _roll_saves_vec min(_, front) on each component. Here we additionally cap the COMBINED
        # per-skirmish combat losses at the FIELD = front+reserve (FRONT_CAP+RESERVE_CAP = 15): the
        # rear is "at camp", not present, and cannot die this skirmish. Panic+break then draw from
        # whatever field budget remains (passed to the morale module below).
        FIELD_CAP = FRONT_CAP + RESERVE_CAP
        a_casualties = np.minimum(a_casualties + a_rip, FIELD_CAP).astype(np.int32)
        b_casualties = np.minimum(b_casualties + b_rip, FIELD_CAP).astype(np.int32)
        a_pre_combat_size = a_size.copy()
        b_pre_combat_size = b_size.copy()
        a_size = np.maximum(0, a_size - a_casualties)
        b_size = np.maximum(0, b_size - b_casualties)

        # Track combat casualties (capped at actual size lost)
        a_combat_lost = a_pre_combat_size - a_size
        b_combat_lost = b_pre_combat_size - b_size
        a_kill_cas_total += a_combat_lost
        b_kill_cas_total += b_combat_lost

        # ── Accumulate hit / save / strike-order stats for the analysis matrix ──
        # a_strikes_initial = A's landed hits this skirmish; b_strikes = B's landed hits.
        # b_casualties / a_casualties = failed saves (= casualties from those hits).
        # Strike order from the masks (mutually exclusive per active run).
        _eng = active & ((a_size + a_casualties > 0) | (b_size + b_casualties > 0))
        a_hits_total   += np.where(active, a_strikes_initial, 0).astype(np.int64)
        b_hits_total   += np.where(active, b_strikes, 0).astype(np.int64)
        b_incoming     += np.where(active, a_strikes_initial, 0).astype(np.int64)  # A's hits land on B
        a_incoming     += np.where(active, b_strikes, 0).astype(np.int64)
        b_failed_saves += np.where(active, b_casualties, 0).astype(np.int64)
        a_failed_saves += np.where(active, a_casualties, 0).astype(np.int64)
        sk_a_first += (active & a_first_mask).astype(np.int64)
        sk_b_first += (active & b_first_mask).astype(np.int64)
        sk_simul   += (active & simul_mask).astype(np.int64)
        sk_engaged += active.astype(np.int64)
        if first:
            # A's kills on B = B's combat losses; A's deaths = A's combat losses this skirmish.
            fs_a_kills    += np.where(active, b_combat_lost, 0).astype(np.int64)
            fs_a_deaths   += np.where(active, a_combat_lost, 0).astype(np.int64)
            fs_a_incoming += np.where(active, b_strikes, 0).astype(np.int64)  # hits A saved against
            fs_a_failed   += np.where(active, a_casualties, 0).astype(np.int64)
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
        a_loses_end = active & ~((DRILLED in a_tags) and first) & (a_size > 0) & (~no_combat_free)
        b_loses_end = active & ~((DRILLED in b_tags) and first) & (b_size > 0) & (~no_combat_free)
        # already fatigued → gain fatigue token instead of endurance loss
        a_already_fat = a_fat > 0
        b_already_fat = b_fat > 0
        # Endurance loss only where not already fatigued
        a_loses_end_actual = a_loses_end & ~a_already_fat
        b_loses_end_actual = b_loses_end & ~b_already_fat
        a_end = a_end - a_loses_end_actual.astype(np.int8)
        b_end = b_end - b_loses_end_actual.astype(np.int8)
        # NOTE: fatigue-token accrual now happens AFTER the shaking test below, so the shaking
        # test fires at the PRE-token shake target on the skirmish endurance hits 0 (per rules:
        # "endurance hits 0 → take a shaken test, which then gives a fatigue token"). The token
        # increment for exhausted runs is applied after the test/rout block.

        # ── MORALE PHASE (shared, single-sourced in combat_morale) ──────────────────
        # Canonical order: PANIC (>5 net combat) -> BREAK (exhausted, pre-token target) -> ROUT.
        # Fully reshaped model; identical code runs in batch_engine. Steadfast = Immune Panic,
        # Unshakable = Immune Break (still routs at >=7). net combat = combat_lost - heal.
        import combat_morale as _cm
        a_net_combat = np.maximum(0, a_combat_lost - a_heal)
        b_net_combat = np.maximum(0, b_combat_lost - b_heal)
        a_steadfast = ("Immune Panic" in a_tags) or ("Steadfast" in a_tags)
        b_steadfast = ("Immune Panic" in b_tags) or ("Steadfast" in b_tags)
        a_unbreak = a_static.unshakable or (UNBREAKABLE in a_tags)
        a_morale_cap = ("Unshakable" in a_tags)
        a_zealot = ("Zealot" in a_tags); a_rally = ("Rally" in a_tags); a_resolute = ("Resolute" in a_tags)
        b_unbreak = b_static.unshakable or (UNBREAKABLE in b_tags)
        b_morale_cap = ("Unshakable" in b_tags)
        b_zealot = ("Zealot" in b_tags); b_rally = ("Rally" in b_tags); b_resolute = ("Resolute" in b_tags)
        _aM = _cm.resolve_side_morale(
            rng, n_runs, _shaking_test_vec, SHAKE_CAP,
            a_size, a_end, a_fat, active, ending,
            a_net_combat, a_static.shaking, a_static.shake_bonus,
            np.full(n_runs, bool(a_unbreak)), np.full(n_runs, bool(a_steadfast)),
            a_cause_of_wipe, a_waver_cas_total, a_shake_cas_total, a_rout_cas_total,
            field_budget=a_combat_lost, field_cap=(FRONT_CAP + RESERVE_CAP),
            morale_cap_mask=np.full(n_runs, bool(a_morale_cap)),
            zealot_mask=np.full(n_runs, bool(a_zealot)),
            steadfast_firstpass_mask=np.full(n_runs, bool(a_rally)), break_used=a_break_used,
            resolute_firstpass_mask=np.full(n_runs, bool(a_resolute)), panic_used=a_panic_used)
        _bM = _cm.resolve_side_morale(
            rng, n_runs, _shaking_test_vec, SHAKE_CAP,
            b_size, b_end, b_fat, active, ending,
            b_net_combat, b_static.shaking, b_static.shake_bonus,
            np.full(n_runs, bool(b_unbreak)), np.full(n_runs, bool(b_steadfast)),
            b_cause_of_wipe, b_waver_cas_total, b_shake_cas_total, b_rout_cas_total,
            field_budget=b_combat_lost, field_cap=(FRONT_CAP + RESERVE_CAP),
            morale_cap_mask=np.full(n_runs, bool(b_morale_cap)),
            zealot_mask=np.full(n_runs, bool(b_zealot)),
            steadfast_firstpass_mask=np.full(n_runs, bool(b_rally)), break_used=b_break_used,
            resolute_firstpass_mask=np.full(n_runs, bool(b_resolute)), panic_used=b_panic_used)
        a_size = _aM["size"]; a_cause_of_wipe = _aM["cause"]
        a_waver_cas_total = _aM["cas_panic_total"]; a_shake_cas_total = _aM["cas_break_total"]; a_rout_cas_total = _aM["cas_rout_total"]
        a_exhausted = _aM["exhausted"]; a_break_used = _aM["break_used"]; a_panic_used = _aM["panic_used"]; a_shake_lost = _aM["break_lost"]; a_waver_lost = _aM["panic_lost"]
        b_size = _bM["size"]; b_cause_of_wipe = _bM["cause"]
        b_waver_cas_total = _bM["cas_panic_total"]; b_shake_cas_total = _bM["cas_break_total"]; b_rout_cas_total = _bM["cas_rout_total"]
        b_exhausted = _bM["exhausted"]; b_break_used = _bM["break_used"]; b_panic_used = _bM["panic_used"]; b_shake_lost = _bM["break_lost"]; b_waver_lost = _bM["panic_lost"]

        # Per-skirmish logging (first `log_skirmishes` skirmishes only)
        if skirmish_log is not None and sk < log_skirmishes:
            first_striker = np.where(a_first_mask, 1, np.where(b_first_mask, -1, 0)).astype(np.int8)
            skirmish_log.append({
                "skirmish": sk + 1,
                "a_casualties": (a_combat_lost + a_shake_lost + a_waver_lost).astype(np.int32).copy(),
                "b_casualties": (b_combat_lost + b_shake_lost + b_waver_lost).astype(np.int32).copy(),
                "a_combat": a_combat_lost.astype(np.int32).copy(),
                "b_combat": b_combat_lost.astype(np.int32).copy(),
                "a_shake": a_shake_lost.astype(np.int32).copy(),
                "b_shake": b_shake_lost.astype(np.int32).copy(),
                "a_waver": a_waver_lost.astype(np.int32).copy(),
                "b_waver": b_waver_lost.astype(np.int32).copy(),
                "first_striker": first_striker.copy(),
                "active": active.copy(),
            })

        # Heal next skirmish reads COMBAT-only casualties; prev-casualties bookkeeping.
        a_prev_combat_casualties = a_combat_lost.copy()
        b_prev_combat_casualties = b_combat_lost.copy()
        a_skirm_cas = a_skirm_cas + a_shake_lost + a_waver_lost
        b_skirm_cas = b_skirm_cas + b_shake_lost + b_waver_lost
        a_prev_casualties = a_skirm_cas
        b_prev_casualties = b_skirm_cas
        # (Per the rule, retinues each become a casualty — equivalent to size→0.)

        # === Fatigue token accrual (AFTER the shaking test / rout, per the timeline) ===
        # An exhausted side gains 1 fatigue token at the end of every skirmish it spent at 0
        # endurance — this is what raises next skirmish's to-hit (-1, capped 6+) and shake (-1).
        # Cap tokens at a sane ceiling to avoid overflow; effect already saturates (to-hit caps
        # at 6+, and a non-Steadfast side has already routed by the time the shake target hits 7).
        a_fat = np.minimum(a_fat + (a_exhausted & active & (~ending)).astype(np.int8), 99).astype(np.int8)
        b_fat = np.minimum(b_fat + (b_exhausted & active & (~ending)).astype(np.int8), 99).astype(np.int8)

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
        "avg_a_killed_waver":  float(a_waver_cas_total.mean()),
        "avg_a_killed_rout":   float(a_rout_cas_total.mean()),
        "avg_a_killed_flee":   float(a_rout_cas_total.mean()),  # alias (legacy)
        "avg_b_killed_combat": float(b_kill_cas_total.mean()),
        "avg_b_killed_shake":  float(b_shake_cas_total.mean()),
        "avg_b_killed_waver":  float(b_waver_cas_total.mean()),
        "avg_b_killed_rout":   float(b_rout_cas_total.mean()),
        "avg_b_killed_flee":   float(b_rout_cas_total.mean()),  # alias (legacy)
        # Cause-of-wipe distribution
        "a_wipe_combat": int((a_cause_of_wipe == 1).sum()),
        "a_wipe_shake":  int((a_cause_of_wipe == 2).sum()),
        "a_wipe_waver":  int((a_cause_of_wipe == 4).sum()),
        "a_wipe_rout":   int((a_cause_of_wipe == 3).sum()),
        "a_wipe_flee":   int((a_cause_of_wipe == 3).sum()),  # alias (legacy)
        "b_wipe_combat": int((b_cause_of_wipe == 1).sum()),
        "b_wipe_shake":  int((b_cause_of_wipe == 2).sum()),
        "b_wipe_waver":  int((b_cause_of_wipe == 4).sum()),
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

        # ── Hit / save / strike-order rates (averaged across runs) ──
        # avg hits per engaged skirmish (offensive output proxy)
        "a_hits_per_skirm": float((a_hits_total / np.maximum(1, sk_engaged)).mean()),
        "b_hits_per_skirm": float((b_hits_total / np.maximum(1, sk_engaged)).mean()),
        # save rate = 1 - failed_saves / incoming_hits (defensive durability)
        "a_save_rate": float((1.0 - a_failed_saves / np.maximum(1, a_incoming)).mean()),
        "b_save_rate": float((1.0 - b_failed_saves / np.maximum(1, b_incoming)).mean()),
        # strike-order rates (fraction of engaged skirmishes A struck first / simul / B first)
        "a_strike_first_rate": float((sk_a_first / np.maximum(1, sk_engaged)).mean()),
        "simul_rate":          float((sk_simul   / np.maximum(1, sk_engaged)).mean()),
        "a_strike_last_rate":  float((sk_b_first / np.maximum(1, sk_engaged)).mean()),
        # First-skirmish-only (opening clash) tallies, averaged across runs:
        "fs_a_kills":  float(fs_a_kills.mean()),    # avg kills A dealt B in skirmish 0
        "fs_a_deaths": float(fs_a_deaths.mean()),   # avg casualties A took in skirmish 0
        "fs_a_save_rate": float((1.0 - fs_a_failed / np.maximum(1, fs_a_incoming)).mean()),  # A's save rate, skirmish 0
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
        if ONE_SHOT in RANGED[ld.ranged]["tags"]:
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