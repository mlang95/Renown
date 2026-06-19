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


def build_save_clips(n, save_target, def_planishing, atk_ignores_tempered):
    """Normal + Deadly save-target arrays, with the Planishing (Tempered) cap.

    Deadly strikes resolve at save_target + 5 (Deadly's AP -5). Planishing caps
    BOTH at 6+ (no auto-fail from AP) UNLESS the attacker carries Negate Tempered
    (atk_ignores_tempered), which lets AP push the save past 6+ to auto-fail.

    def_planishing / atk_ignores_tempered: scalar-or-array (n,). The cap is applied
    per-element (np.where), so a batch block with a mix of Planishing and non-
    Planishing defenders — or Negate-Tempered and normal attackers — resolves
    each slot correctly.

    Returns (save_clip (n,) int64, deadly_save_clip (n,) int64, auto_pass_save (n,) bool).
    """
    save_t = _as_int_arr(save_target, n)
    save_clipped = np.clip(save_t, 2, 7)            # 7 = impossible (auto-fail)
    deadly_clipped = np.clip(save_t + 5, 2, 7)      # Deadly: AP -5

    planish = _as_bool_arr(def_planishing, n)
    ignores = _as_bool_arr(atk_ignores_tempered, n)
    # Tempered cap applies where defender has Planishing AND attacker does NOT ignore it.
    cap_active = planish & (~ignores)
    save_clipped = np.where(cap_active, np.minimum(save_clipped, 6), save_clipped)
    deadly_clipped = np.where(cap_active, np.minimum(deadly_clipped, 6), deadly_clipped)

    auto_pass_save = save_t < 2
    return (save_clipped.astype(np.int64).copy(),
            deadly_clipped.astype(np.int64).copy(),
            auto_pass_save.astype(np.bool_).copy())


def build_parry_thr(n, def_parry_improved, atk_unstoppable, atk_is_ranged,
                    atk_has_deflect, def_fat):
    """Per-element Parry threshold array vs NORMAL hits.

    Base 5+ (4+ with Improved Parry), +1 vs Unstoppable, +1 vs Deflect (all ranged
    carry Deflect; Daggers/Estoc/Ministry carry it explicitly), +1 per Fatigue token,
    capped at 6+ (a natural 6 can always Parry). Deadly strikes Parry only on a
    natural 6 — that's handled in the kernel, not here.

    All inputs scalar-or-array (n,). Returns parry_thr (n,) int64.
    Also returns the per-element `deflect` mask so the caller can suppress riposte.
    """
    improved = _as_bool_arr(def_parry_improved, n)
    unstop = _as_bool_arr(atk_unstoppable, n)
    ranged = _as_bool_arr(atk_is_ranged, n)
    deflect_tag = _as_bool_arr(atk_has_deflect, n)
    fat = _as_int_arr(def_fat, n) if def_fat is not None else np.zeros(n, dtype=np.int64)

    deflect = deflect_tag | ranged   # ranged always Deflects
    base = np.where(improved, 4, 5).astype(np.int64)
    parry_thr = base + unstop.astype(np.int64) + deflect.astype(np.int64) + fat
    parry_thr = np.minimum(parry_thr, 6).astype(np.int64)
    return parry_thr.copy(), deflect


def build_regen_thr(n, def_regen_threshold, def_fat):
    """Per-element Recover threshold array. 0 = no Recover.

    Base threshold (already incl. Serrated worsening, computed in the gather via
    _regen_threshold), worsened by +1 per Fatigue token, capped at 6+. 0 stays 0.

    def_regen_threshold: None, scalar, or (n,) array. def_fat: scalar-or-array (n,).
    Returns regen_thr (n,) int64.
    """
    fat = _as_int_arr(def_fat, n) if def_fat is not None else np.zeros(n, dtype=np.int64)
    if def_regen_threshold is None:
        raw = np.zeros(n, dtype=np.int64)
    else:
        a = np.asarray(def_regen_threshold)
        if a.ndim == 0:
            raw = np.full(n, int(a), dtype=np.int64)
        else:
            raw = a.astype(np.int64)
    # Decode Enduring: a NEGATIVE threshold signals the Enduring keyword (encoded in
    # _regen_threshold). Magnitude is the normal (Serrated-adjusted) pre-fatigue threshold.
    enduring = raw < 0
    regen_base = np.abs(raw)
    # CANONICAL (matches batch_engine): Recover switches OFF entirely while Fatigued, rather than
    # degrading — EXCEPT Enduring units, which still get a flat 6+ Recover while Fatigued.
    # Pre-fatigue everyone recovers at their base threshold. (Aligns vec to batch: batch passes
    # the raw threshold and lets this function own all fatigue/Enduring logic.)
    fresh = (regen_base > 0) & (fat == 0)
    fatigued_enduring = (regen_base > 0) & (fat > 0) & enduring
    regen_thr = np.where(fresh, regen_base, np.where(fatigued_enduring, 6, 0))
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
