"""
combat_primitives.py — SHARED rules-math layer for both combat engines (C2).

This is the layer that DRIFTED between vectorized_combat and batch_engine. It owns
everything DOWNSTREAM of each engine's tag gather: turning per-element primitives
(parry flags, regen thresholds, attacker keywords, save targets) into the exact
arrays the numba kernels consume.

Design contract — EVERYTHING here is ARRAY-NATIVE over the leading dimension n:
  - vectorized_combat passes n = n_runs           (one matchup, many runs)
  - batch_engine     passes n = npairs * n_runs   (many matchups, many runs)
The helpers never branch on Python scalars for per-element quantities; scalar
inputs are broadcast to (n,) and all decisions are np.where / arithmetic. This is
the difference from the old vectorized wrappers (which used `if atk_unstoppable`)
that made them un-shareable.

GATHER stays per-engine (vectorized resolves single tag sets; batch resolves
lists of tag sets). This module starts AFTER the gather, from primitive arrays.

Extracted from vectorized_combat._roll_saves_vec / _roll_strikes_vec (canonical).
"""
import numpy as np
from dice_config import (FACES, FOCUSED_THR, ROUT_THR, CAP_THR, AUTO_PASS_FLOOR,
                         PARRY_BASE, RECOVER_BASE, DEADLY_AP, DEADLY_MODE,
                         UNSTOPPABLE_MOD, IMPROVED_PARRY_MOD)
_AP_FLOOR = AUTO_PASS_FLOOR if AUTO_PASS_FLOOR is not None else 1


def _as_bool_arr(x, n):
    """Broadcast a scalar-or-array to a (n,) bool array (copy, contiguous)."""
    a = np.asarray(x)
    if a.ndim == 0:
        return np.full(n, bool(a), dtype=np.bool_)
    return np.broadcast_to(a, (n,)).astype(np.bool_).copy()


def _as_int_arr(x, n):
    """Broadcast a scalar-or-array to a (n,) int64 array (copy, contiguous)."""
    a = np.asarray(x)
    if a.ndim == 0:
        return np.full(n, int(a), dtype=np.int64)
    return np.broadcast_to(a, (n,)).astype(np.int64).copy()


def crit_floor_from_tags_scalar(tags):
    """Scalar helper for the per-matchup engine: a single tag set → crit floor int.
    4 if 'Crit 4', else 5 if 'Crit 5', else 6 (natural-6 only)."""
    if "Crit 4" in tags:
        return 4
    if "Crit 5" in tags:
        return 5
    return 6


def shielded_value(shield_tags):
    """Shielded strength of a shield: 'Shielded N' (e.g. Tower: Shielded 2) wins, plain 'Shielded' = 1, else 0."""
    best = 0
    for t in shield_tags or ():
        t = str(t)
        if t.startswith("Shielded "):
            try:
                best = max(best, int(t.split()[1]))
            except (IndexError, ValueError):
                pass
        elif t == "Shielded":
            best = max(best, 1)
    return best


def hook_value(tags):
    """How many points of the defender's Shielded the attacker ignores: 'Hook N' -> N;
    'Negate Shielded' (legacy) ignores all of it."""
    best = 0
    for t in tags or ():
        t = str(t)
        if t == "Negate Shielded":
            return 99
        if t.startswith("Hook "):
            try:
                best = max(best, int(t.split()[1]))
            except (IndexError, ValueError):
                pass
    return best


def fluted_ap(ap, def_fluted):
    """Fluted (defender's armor): incoming AP reduced by 1, toward 0 — AP 0 stays 0.
    Applied to the AP a Strike carries (melee, Ranged or Riposte). Scalar-or-array."""
    # def_fluted may be a count (Articulated 1 + Shield Wall 1 = 2): each point reduces AP by 1, never past 0
    if np.ndim(def_fluted) == 0:
        return np.minimum(ap + int(def_fluted), 0) if def_fluted else ap
    n = np.asarray(def_fluted).astype(np.int64)
    return np.where(n > 0, np.minimum(ap + n, 0), ap)


def fluted_deadly_shift(ap, def_fluted):
    """Deadly-target correction for Fluted, which applies AFTER Deadly's extra AP.
    The engines pass the Fluted-reduced normal save target, and the Deadly target is built as
    normal + DEADLY_AP. That is right when AP < 0 (the -1 was already taken). When AP == 0 the
    normal target had nothing to reduce, but AP 0 + Deadly is negative, so Fluted still takes 1:
    shift the Deadly target by -1 there. Returns 0/-1, scalar-or-array."""
    # with a count n: the normal target already took min(n, -AP); the Deadly AP takes the rest
    n = np.asarray(def_fluted).astype(np.int64)
    taken = np.minimum(n, np.maximum(-np.asarray(ap), 0))
    r = -(n - taken)
    return int(r) if np.ndim(r) == 0 else r


def deadly_shift(ap, def_fluted):
    """Shift added to (normal save target + DEADLY_AP) to get the Deadly save target.
    DEADLY_MODE "additional" (default): Deadly adds DEADLY_AP to the Strike's AP, Fluted after -> fluted_deadly_shift.
    DEADLY_MODE "set": a Deadly Strike HAS AP -DEADLY_AP (e.g. 10), replacing the weapon's AP; Fluted then
      takes 1 (AP -10 -> -9). The normal target already holds the (Fluted) weapon AP, so swap it out:
      deadly = armor + DEADLY_AP - fl - shield - TS = normal + eff_ap + DEADLY_AP - fl."""
    if DEADLY_MODE == "set":
        fl = np.asarray(def_fluted).astype(np.int64)
        return fluted_ap(ap, def_fluted) - fl
    return fluted_deadly_shift(ap, def_fluted)


DEADLY_NO_RECOVER = (DEADLY_MODE == "set")   # Version D: a Deadly Strike can't be Recovered


def build_save_clips(n, save_target, def_planishing, atk_ignores_tempered, deadly_shift=0):
    """Normal + Deadly save-target arrays, with the Planishing (Tempered) cap.

        Deadly strikes resolve at save_target + DEADLY_AP (default +3, additive). Planishing caps

    DEADLY_MODE "set" (Version D, Nov 7 2026) is wired through deadly_shift(): the engines pass it as
    `deadly_shift`, and the kernel drops Recover for Deadly Strikes (DEADLY_NO_RECOVER).
    BOTH at 6+ (no auto-fail from AP) UNLESS the attacker carries Negate Tempered
    (atk_ignores_tempered), which lets AP push the save past 6+ to auto-fail.

    def_planishing / atk_ignores_tempered: scalar-or-array (n,). The cap is applied
    per-element (np.where), so a batch block with a mix of Planishing and non-
    Planishing defenders — or Negate-Tempered and normal attackers — resolves
    each slot correctly.

    Returns (save_clip (n,) int64, deadly_save_clip (n,) int64, auto_pass_save (n,) bool).
    """
    save_t = _as_int_arr(save_target, n)
    save_clipped = np.clip(save_t, _AP_FLOOR, FACES + 1) # FACES+1 = auto-fail
    deadly_clipped = np.clip(save_t + DEADLY_AP + _as_int_arr(deadly_shift, n), _AP_FLOOR, FACES + 1)

    planish = _as_bool_arr(def_planishing, n)
    ignores = _as_bool_arr(atk_ignores_tempered, n)
    # Tempered cap applies where defender has Planishing AND attacker does NOT ignore it.
    cap_active = planish & (~ignores)
    save_clipped = np.where(cap_active, np.minimum(save_clipped, CAP_THR), save_clipped)
    deadly_clipped = np.where(cap_active, np.minimum(deadly_clipped, CAP_THR), deadly_clipped)

    auto_pass_save = save_t < _AP_FLOOR
    return (save_clipped.astype(np.int64).copy(),
            deadly_clipped.astype(np.int64).copy(),
            auto_pass_save.astype(np.bool_).copy())


def build_parry_thr(n, def_parry_improved, atk_unstoppable, atk_is_ranged,
                    atk_has_deflect, def_fat, atk_negate_riposte=False, atk_parry_pen=0):
    """Per-element Parry threshold array vs NORMAL hits.

    Base PARRY_BASE+ (one rung better with Improved Parry), -2 to Parry vs Unstoppable
    (i.e. +2 to the target), +1 vs an explicit Deflect tag. Uncapped: 11+ = can't Parry (Nov 9 2026).
    Ranged Strikes do NOT worsen Parry (Nov 7 2026: Ranged = Deadly + Unstoppable + Awkward +
    Negate Riposte; Unstoppable already covers their Parry penalty) — they only suppress Riposte. Fatigue no longer affects Parry
    (def_fat kept for call-site compatibility, ignored). Deadly
    strikes Parry only on a Focused roll — handled in the kernel, not here.

    All inputs scalar-or-array (n,). Returns parry_thr (n,) int64.
    Also returns the per-element no-Riposte mask (Deflect tag OR a Ranged Strike) for build_riposte_mask.
    """
    parry_bonus = _as_int_arr(def_parry_improved, n) # 0 = none; each +1 = one rung better
    unstop = _as_bool_arr(atk_unstoppable, n)
    ranged = _as_bool_arr(atk_is_ranged, n)
    deflect_tag = _as_bool_arr(atk_has_deflect, n)
    # Ranged Strikes and a Negate Riposte attacker (e.g. from a Holding) block Riposte; only a Deflect tag worsens Parry
    no_riposte = deflect_tag | ranged | _as_bool_arr(atk_negate_riposte, n)
    base = (PARRY_BASE - parry_bonus).astype(np.int64)
    parry_thr = base + UNSTOPPABLE_MOD * unstop.astype(np.int64) + deflect_tag.astype(np.int64)
    parry_thr = parry_thr + _as_int_arr(atk_parry_pen, n)   # attacker's FoeParry (e.g. a charge); 0 for most
    # Nov 9 2026: no cap. A target above FACES (11+) can't be met: the Strike can't be Parried. Deadly Strikes
    # don't read this target (the kernel Parries them on a Focused roll only), so Unstoppable never stacks onto Deadly.
    parry_thr = parry_thr.astype(np.int64)
    return parry_thr.copy(), no_riposte


def build_regen_thr(n, def_regen_threshold, def_fat):
    """Per-element Recover threshold array. 0 = no Recover.

    Base threshold (already incl. Serrated worsening, computed in the gather via
    _regen_threshold), worsened by +1 per Fatigue token, capped at 6+. 0 stays 0.

    def_regen_threshold: None, scalar, or (n,) array. def_fat: scalar-or-array (n,).
    Returns regen_thr (n,) int64.
    """
    if def_regen_threshold is None:
        raw = np.zeros(n, dtype=np.int64)
    else:
        a = np.asarray(def_regen_threshold)
        if a.ndim == 0:
            raw = np.full(n, int(a), dtype=np.int64)
        else:
            raw = a.astype(np.int64)
    # Fatigue no longer affects Recover (def_fat kept for call-site compatibility, ignored).
    # Enduring is no longer a Recover modifier (it now keeps Recovered Strikes out of the Panic
    # tally — handled by the engines); abs() keeps any legacy negative encoding harmless.
    regen_thr = np.minimum(np.abs(raw), CAP_THR)
    return regen_thr.astype(np.int64).copy()


def build_riposte_mask(n, def_has_riposte, deflect):
    """Per-element riposte mask. A Parry against a Deflect strike never Ripostes,
    so riposte is suppressed wherever `deflect` is True (per-element).

    def_has_riposte: scalar-or-array (n,). deflect: (n,) bool from build_parry_thr.
    Returns riposte_mask (n,) bool.
    """
    rip = _as_bool_arr(def_has_riposte, n)
    rip = rip & (~deflect)
    return rip.copy()
