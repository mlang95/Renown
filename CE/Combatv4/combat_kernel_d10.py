"""
combat_kernel.py — SHARED numba kernels for both combat engines.

These three kernels are the SINGLE SOURCE OF TRUTH for per-die strike and save
resolution. Both vectorized_combat (one matchup x N runs) and batch_engine
(many matchups x N runs) import them. The kernels loop over the leading
dimension `n` and DO NOT care whether n is n_runs or npairs*n_runs — gather and
scatter stay in each engine, only this inner math is shared.

Extracted VERBATIM from vectorized_combat.py (the canonical, verified engine).
Behavior-preserving: deprecated paths (halfsword_mode, riposte_on5) are CARRIED
FORWARD inert, not removed — removing them is a separate cleanup gated by its own
parity run.

After ANY edit to a kernel here, wipe the numba cache before trusting results:
    set NUMBA_CACHE_DIR=C:\\numba_cache   (must be set in the launching shell)
    rmdir /s /q C:\\numba_cache
"""
import numpy as np
from dice_config import (FACES, FOCUSED_THR, ROUT_THR, CAP_THR, AUTO_PASS_FLOOR,
                         PARRY_BASE, RECOVER_BASE, DEADLY_AP)


# ── Canonical save-resolution ordering (single source) ──────────────────────
# True  = SPEC B: parry first (every hit), riposte on a successful parry, then
#         armor save on un-parried hits, then recover. (Deadly still parries &
#         recovers on a Focused roll (>= FOCUSED_THR) only; Deadly can be riposted
#         unless the attacker has Deflect / Negate Riposte.)
# False = legacy: save first, parry only failed saves. (Was the engine default;
#         it was WRONG vs the rulebook — do not use.)
PARRY_BEFORE_SAVE = True

# ── Numba acceleration (optional) ──────────────────────────────────────────
# JIT the numeric cores when numba is available; otherwise transparent NumPy
# fallback (identical results, slower). Only primitives reach the kernel.
try:
    from numba import njit as _njit
    _HAS_NUMBA = True
except Exception:  # numba not installed → transparent fallback
    _HAS_NUMBA = False
    def _njit(*a, **k):
        def _wrap(f):
            return f
        return _wrap


@_njit(cache=True)
def _strikes_kernel(rolls, cleave_rolls, front_line, target_th_clip, auto_fail, auto_pass,
                    has_deadly, has_cleave, crit_floor, reroll_misses=False):
    """Per-run strike resolution. rolls/cleave_rolls: (n,20) int8.
    Proc = roll >= crit_floor (6 = natural-6 only; 5 = Crit5; 4 = Crit4).
    Deadly: proc'd strikes are Deadly (resolved at AP-5, parry/recover nat-6 only).
    Cleave: each proc rolls an additional Strike die at the modified to-Strike value. An extra
    die that Strikes and procs (>= crit_floor) is Deadly when the weapon is, and rolls another
    extra die, and so on (Cleave chains). The first extra die is cleave_rolls[r, d]; chained
    dice come from cleave_rolls[r, maxd:] (callers allocate that pool only when a Cleave
    weapon is present, so non-Cleave runs draw exactly as before). A Focused extra Strike
    counts as a Focused Strike for Destroy Shield.
    Destroy Shield (proc_count) fires on a NATURAL 6 ONLY — Crit floor widens Deadly/Cleave, not it.
    reroll_misses (dual-wield): a die that fails to Strike is rerolled once (using the
    spare cleave_rolls die); the reroll can hit and can itself be a Deadly proc. Mutually
    exclusive with Cleave at the engine level (a weapon won't carry both).
    Returns strikes, deadly_strikes, proc_count (proc_count drives Destroy Shield)."""
    n = rolls.shape[0]
    maxd = rolls.shape[1]
    strikes = np.zeros(n, dtype=np.int32)
    deadly = np.zeros(n, dtype=np.int32)
    procs = np.zeros(n, dtype=np.int32)
    for r in range(n):
        fl = front_line[r]
        th = target_th_clip[r]
        af = auto_fail[r]
        ap = auto_pass[r]
        s = 0
        dl = 0
        pc = 0
        kk = maxd                     # next unused Cleave chain die (columns >= maxd of cleave_rolls)
        for d in range(maxd):
            if d >= fl:
                break
            roll = rolls[r, d]
            is_strike = ap or (roll >= th and not af)
            if not is_strike:
                if reroll_misses and not af:
                    rr = cleave_rolls[r, d]
                    if rr >= th:
                        s += 1
                        if rr >= FOCUSED_THR:
                            pc += 1
                        if has_deadly and rr >= crit_floor:
                            dl += 1
                continue
            s += 1
            is_proc = (roll >= crit_floor)
            if roll >= FOCUSED_THR:
                pc += 1
            if is_proc:
                if has_deadly:
                    dl += 1
                if has_cleave:
                    # Cleave chains: a Focused extra die Strikes and rolls another (pool past column maxd)
                    extra = cleave_rolls[r, d]
                    while ap or (extra >= th and not af):
                        s += 1
                        if extra >= FOCUSED_THR:
                            pc += 1
                        if extra < crit_floor:
                            break
                        if has_deadly:
                            dl += 1
                        if kk >= cleave_rolls.shape[1]:
                            break
                        extra = cleave_rolls[r, kk]
                        kk += 1
        strikes[r] = s
        deadly[r] = dl
        procs[r] = pc
    return strikes, deadly, procs


@_njit(cache=True)
def _strikes_kernel_dual(rolls, cleave_rolls, front_line, target_th_clip, auto_fail, auto_pass,
                         run_has_deadly, run_has_cleave, crit_floor, run_reroll_misses):
    """Per-run variant of _strikes_kernel: deadly / cleave / Dual-Wield reroll flags are arrays
    (Bastard dual profile in vectorized; every slot in batch_engine). Same per-die logic."""
    n = rolls.shape[0]
    maxd = rolls.shape[1]
    strikes = np.zeros(n, dtype=np.int32)
    deadly = np.zeros(n, dtype=np.int32)
    procs = np.zeros(n, dtype=np.int32)
    for r in range(n):
        fl = front_line[r]; th = target_th_clip[r]; af = auto_fail[r]; ap = auto_pass[r]
        hd = run_has_deadly[r]; hc = run_has_cleave[r]
        s = 0; dl = 0; pc = 0
        kk = maxd                     # next unused Cleave chain die (columns >= maxd of cleave_rolls)
        for d in range(maxd):
            if d >= fl:
                break
            roll = rolls[r, d]
            if not (ap or (roll >= th and not af)):
                if run_reroll_misses[r] and not af:      # Dual Wield: a failed Strike is rerolled once
                    rr = cleave_rolls[r, d]
                    if rr >= th:
                        s += 1
                        if rr >= FOCUSED_THR:
                            pc += 1
                        if hd and rr >= crit_floor:
                            dl += 1
                continue
            s += 1
            if roll >= FOCUSED_THR:
                pc += 1
            if roll >= crit_floor:
                if hd:
                    dl += 1
                if hc:
                    # Cleave chains: a Focused extra die Strikes and rolls another (pool past column maxd)
                    extra = cleave_rolls[r, d]
                    while ap or (extra >= th and not af):
                        s += 1
                        if extra >= FOCUSED_THR:
                            pc += 1
                        if extra < crit_floor:
                            break
                        if hd:
                            dl += 1
                        if kk >= cleave_rolls.shape[1]:
                            break
                        extra = cleave_rolls[r, kk]
                        kk += 1
        strikes[r] = s; deadly[r] = dl; procs[r] = pc
    return strikes, deadly, procs


@_njit(cache=True)
def _saves_kernel3(rolls, parry_rolls, regen_rolls,
                  n_strikes, deadly_strikes, save_clip, deadly_save_clip, auto_pass_save,
                  atk_has_poison, parry_mask, parry_thr, regen_thr,
                  riposte_mask, riposte_on5, parry_reroll, parry_rolls2,
                  parry_before_save=False, halfsword_mode=False, deadly_no_recover=False):
    """Per-run save resolution. All roll arrays (n,max_strikes) int8.
    save_clip / deadly_save_clip: per-run save targets (2..7; 7 = impossible).
      Deadly strikes resolve at deadly_save_clip (normal target worsened by Deadly's AP -5;
      Planishing caps both at CAP_THR).
    parry_thr: per-run Parry threshold (base PARRY_BASE/-1 + 2*Unstoppable + ranged/Deflect, capped CAP_THR; Fatigue no longer applies).
      Deadly strikes can only be Parried on a Focused roll (>= FOCUSED_THR).
    regen_thr: per-run Recover threshold (0 = none; base + Serrated, capped CAP_THR; Fatigue no longer applies).
      Deadly strikes can only be Recovered on a Focused roll (>= FOCUSED_THR), or never when
      deadly_no_recover (DEADLY_MODE 'set').
    riposte_on5: Dual Wield — a Parry roll of FOCUSED_THR-1 that parries also Ripostes (per run).
    parry_reroll / parry_rolls2: Dual Wield — a failed Parry roll is rerolled once, from parry_rolls2
      (n,max_strikes); the reroll can Riposte.
    halfsword_mode: DEPRECATED; carried forward inert (never set True by current callers).
    Returns (casualties (n,), ripostes (n,), recovered (n,)) — recovered = Strikes a failed Save
    let through that the Recover roll then saved (they still count toward Panic unless Enduring)."""
    n = rolls.shape[0]
    maxs = rolls.shape[1]
    casualties = np.zeros(n, dtype=np.int32)
    ripostes = np.zeros(n, dtype=np.int32)
    recovered = np.zeros(n, dtype=np.int32)
    for r in range(n):
        ns = n_strikes[r]
        dl = deadly_strikes[r]
        sc = save_clip[r]
        dsc = deadly_save_clip[r]
        ap = auto_pass_save[r]
        pmask = parry_mask[r]
        pthr = parry_thr[r]
        rip_on = riposte_mask[r]
        rip5 = riposte_on5[r]
        prr = parry_reroll[r]
        rthr = regen_thr[r]   # 0 = no Recover for this run
        poi = atk_has_poison[r]   # per-row: attacker's effective Poison vs this defender
        fails = 0
        rip = 0
        rec = 0
        for d in range(maxs):
            if d >= ns:
                break
            is_proc = d < dl
            is_deadly = is_proc and not halfsword_mode
            is_half = is_proc and halfsword_mode
            # Halfsword: parry -1 (thr+1) ; Deadly: parry on natural 6 only ; else base
            if is_half:
                pthr_eff = CAP_THR if (pthr + 1) > CAP_THR else (pthr + 1)
            elif is_deadly:
                # Nov 9 2026: at best a Focused roll; a normal target already past it (11+ = can't Parry) still applies
                pthr_eff = FOCUSED_THR if pthr < FOCUSED_THR else pthr
            else:
                pthr_eff = pthr
            # ── PARRY-FIRST ordering (experiment toggle) ──
            if parry_before_save and pmask and pthr_eff <= FACES:
                pr = parry_rolls[r, d]
                if prr and pr < pthr_eff:          # Dual Wield: a failed Parry is rerolled once
                    pr = parry_rolls2[r, d]
                if pr >= pthr_eff:
                    if (not is_half) and rip_on and (pr >= FOCUSED_THR or (rip5 and pr >= FOCUSED_THR - 1 and pthr_eff <= FOCUSED_THR - 1)):
                        rip += 1
                    continue
            # ── Armor save (Halfsword strikes allow NO save) ──
            roll = rolls[r, d]
            poison_kill = False
            if is_half:
                failed = True
            else:
                tgt = dsc if is_deadly else sc
                failed = (roll < tgt)
                if ap and not is_deadly:
                    failed = False
                if poi and roll >= FOCUSED_THR:
                    failed = True
                    poison_kill = True
            if not failed:
                continue
            # ── Default ordering: Parry after a failed save ──
            if (not parry_before_save) and pmask and pthr_eff <= FACES:
                pr = parry_rolls[r, d]
                if prr and pr < pthr_eff:          # Dual Wield: a failed Parry is rerolled once
                    pr = parry_rolls2[r, d]
                if pr >= pthr_eff:
                    if (not is_half) and rip_on and (pr >= FOCUSED_THR or (rip5 and pr >= FOCUSED_THR - 1 and pthr_eff <= FOCUSED_THR - 1)):
                        rip += 1
                    continue
            # ── Recover (Halfsword: -1 to Recover, i.e. thr+1) ──
            if rthr > 0:
                rr = regen_rolls[r, d]
                if is_half:
                    rthr_eff = CAP_THR if (rthr + 1) > CAP_THR else (rthr + 1)
                    if rr >= rthr_eff:
                        rec += 1
                        continue
                elif is_deadly:
                    if (not deadly_no_recover) and rr >= FOCUSED_THR:
                        rec += 1
                        continue
                elif poison_kill:
                    if rr >= FOCUSED_THR:        # Poison wounds: Recover only on a Focused roll
                        rec += 1
                        continue
                elif rr >= rthr:
                    rec += 1
                    continue
            fails += 1
        casualties[r] = fails
        ripostes[r] = rip
        recovered[r] = rec
    return casualties, ripostes, recovered


@_njit(cache=True)
def _saves_kernel(rolls, parry_rolls, regen_rolls,
                  n_strikes, deadly_strikes, save_clip, deadly_save_clip, auto_pass_save,
                  atk_has_poison, parry_mask, parry_thr, regen_thr,
                  riposte_mask, riposte_on5, parry_before_save=False, halfsword_mode=False):
    """Compatibility wrapper: (casualties, ripostes), no Parry reroll. See _saves_kernel3."""
    c, rp, _rc = _saves_kernel3(rolls, parry_rolls, regen_rolls,
                                n_strikes, deadly_strikes, save_clip, deadly_save_clip, auto_pass_save,
                                atk_has_poison, parry_mask, parry_thr, regen_thr,
                                riposte_mask, riposte_on5, np.zeros(rolls.shape[0], dtype=np.bool_), parry_rolls,
                                parry_before_save, halfsword_mode)
    return c, rp
