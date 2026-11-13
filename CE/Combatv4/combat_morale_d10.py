"""
combat_morale.py — SHARED morale phase for both combat engines (C2, subsystem 2).

Single source for the end-of-skirmish morale resolution so it can't drift between
vectorized_combat (one matchup x N runs) and batch_engine (many matchups x N runs).

FULLY VECTORIZED — no per-element Python. Every operation is numpy array math over the
leading dimension n, so batch keeps its speed (n = npairs*n_runs) and vec uses n = n_runs.
The only RNG calls are the shaking-test roller, passed in by the caller (vec passes
_shaking_test_vec, batch passes _shake_batch) — both have signature
    roller(rng, n, field_size, shake_target, mask) -> casualties (n,).

RESHAPED MORALE MODEL (canonical):
  Order at end of skirmish (AFTER both sides' strikes, BEFORE fatigue-token accrual):
    1. PANIC check  — trigger: net combat casualties >= PANIC_THRESHOLD (5) this skirmish. Field min(5,size).
                      Exempt: Steadfast (Immune Panic). Target >=ROUT_THR -> panic-rout.
    2. BREAK check  — trigger: exhausted (endurance 0), EVERY such skirmish, at the
                      PRE-token shake target. Field min(5,size). Exempt from the TEST:
                      Unshakable (Immune Break) — but the target still climbs with fatigue,
                      so Unshakable still ROUTS at >=ROUT_THR. Target >=ROUT_THR -> break-rout.
    3. ROUT         — any side whose shake target >=ROUT_THR via panic-rout or break-rout: whole
                      army flees (size -> 0). Nothing prevents rout.
  Fatigue-token accrual happens in the CALLER, after this returns (break reads pre-token target).

  Cause-of-wipe codes (unchanged): 1=combat (caller-set), 2=break/shaken, 3=rout, 4=panic/waver.
  Panic is attributed before break (panic fires first); a wipe is tagged by whichever test
  actually removed the last retinue.

SHAKE_CAP (field cap) is passed in so both engines share the same constant.
"""
import numpy as np
from dice_config import (FACES, FOCUSED_THR, ROUT_THR, CAP_THR, AUTO_PASS_FLOOR,
                         PARRY_BASE, RECOVER_BASE, DEADLY_AP)


# Canonical panic trigger: net combat casualties AT LEAST the data's PANIC_CASUALTY_THRESHOLD (5 or more, Nov 10 2026).
# RENOWN_PANIC_THRESHOLD overrides it for tests (6 = the old "more than 5"); workers inherit the environment.
import os as _os_pt
import renown_data as _rd_pt
PANIC_THRESHOLD = int(_os_pt.environ.get("RENOWN_PANIC_THRESHOLD", getattr(_rd_pt, "PANIC_CASUALTY_THRESHOLD", 5)))   # trigger: net_combat >= this


def _morale_target(shaking, fat, shake_bonus, zealot_mask=None, morale_cap_mask=None):
    """Pre-token shake target (same value panic and break both read this skirmish)."""
    shaking_arr = np.asarray(shaking)
    target = (shaking_arr + np.asarray(fat).astype(np.int64) - np.asarray(shake_bonus)).astype(np.int64)
    # Zealot: morale target cannot be modified at all — locked at base `shaking` (fatigue tokens
    # and shake_bonus/Abbey do nothing). Applied before any other modifier.
    if zealot_mask is not None:
        _zb = np.broadcast_to(shaking_arr, target.shape).astype(np.int64)
        target = np.where(np.asarray(zealot_mask, dtype=bool), _zb, target).astype(np.int64)
    # Unshakable: morale target can never be reduced beyond 6+ (cap at 6). These units still
    # TAKE panic & break tests every skirmish (they bleed at 6+), but can never reach the >=7
    # rout threshold — they attrit, they don't shatter. Distinct from Unbreakable (skips the
    # Break test but still routs at >=7).
    if morale_cap_mask is not None:
        target = np.where(np.asarray(morale_cap_mask, dtype=bool), np.minimum(target, CAP_THR), target).astype(np.int64)
    return target


def instant_panic(rng, n, roller, shake_cap, size, fat, mask, net_combat, shaking, shake_bonus, steadfast_mask,
                  field_used, field_cap=15, morale_cap_mask=None, zealot_mask=None,
                  resolute_firstpass_mask=None, panic_used=None):
    """The rule (RENOWN_PANIC_TIMING=instant, the default): the Panic check taken as soon as the side that was
    struck first has lost PANIC_THRESHOLD (5) or more, before it Strikes back. Same trigger, target, Resolute and rout as
    the end-of-Skirmish check; `size` is the side's size after the opening Strike.
    Returns dict(cas=, rout=, done=, panic_used=): done = the check was taken (no second one this Skirmish)."""
    target = _morale_target(shaking, fat, shake_bonus, zealot_mask, morale_cap_mask)
    trig = (net_combat >= PANIC_THRESHOLD) & (size > 0) & (~steadfast_mask) & np.asarray(mask, dtype=bool)
    done = trig.copy()
    if resolute_firstpass_mask is not None and panic_used is not None:
        free = trig & np.asarray(resolute_firstpass_mask, dtype=bool) & (~panic_used)
        panic_used = panic_used | free
        trig = trig & (~free)
    test = trig & (target <= FACES)
    cas = roller(rng, n, np.minimum(shake_cap, size), target, test)
    cas = np.minimum(np.minimum(cas, size), np.maximum(0, field_cap - np.asarray(field_used).astype(np.int64)))
    rout = trig & (target >= ROUT_THR)
    return dict(cas=cas.astype(np.int64), rout=rout, done=done, panic_used=panic_used)


def resolve_side_morale(rng, n, roller, shake_cap,
                        size, end, fat, active, ending,
                        net_combat, shaking, shake_bonus, unbreakable_mask, steadfast_mask,
                        cause, cas_panic_total, cas_break_total, cas_rout_total,
                        field_budget=None, field_cap=15, morale_cap_mask=None,
                        zealot_mask=None, steadfast_firstpass_mask=None, break_used=None,
                        resolute_firstpass_mask=None, panic_used=None, panic_done=None):
    """Resolve PANIC -> BREAK -> ROUT for ONE side, in place where possible.
    panic_done: runs whose Panic check this Skirmish was already taken (instant Panic) -> no second one.

    All array args are shape (n,). Scalars (shaking) may be scalar or (n,).
    Returns a dict of updated arrays; the caller assigns them back. Pure numpy.

    Args:
      roller(rng,n,field,target,mask)->cas : the engine's shaking-test dice roller.
      size,end,fat : current per-run state (size mutated & returned).
      active,ending : per-run masks (ending = battle ended via tactic this skirmish).
      net_combat : net COMBAT casualties this skirmish (combat_lost - heal, >=0).
      shaking,shake_bonus : base shake target params (target = shaking + fat - shake_bonus).
      unbreakable_mask : Immune Break (skips break TEST; still routs at >=ROUT_THR).
      morale_cap_mask  : Unshakable (target capped at 6; takes tests, never routs).
      steadfast_mask  : Immune Panic (skips panic entirely).
      cause : cause-of-wipe codes (mutated). cas_*_total : accumulators (mutated).

    Returns dict(size=, panic_lost=, break_lost=, rout_lost=, cause=,
                 cas_panic_total=, cas_break_total=, cas_rout_total=, exhausted=).
    """
    target = _morale_target(shaking, fat, shake_bonus, zealot_mask, morale_cap_mask)
    exhausted = (np.asarray(end) <= 0) & (size > 0)
    # Per-skirmish FIELD budget (15 = front+reserve): combat already removed `field_budget`
    # this skirmish; panic+break may only remove up to the remainder. None = uncapped.
    if field_budget is None:
        remaining = np.full(n, 10**9, dtype=np.int64)
    else:
        remaining = np.maximum(0, field_cap - np.asarray(field_budget).astype(np.int64))

    # ── 1. PANIC check (net combat >= PANIC_THRESHOLD) ──────────────────────────────────────────
    panic_trig = (net_combat >= PANIC_THRESHOLD) & (size > 0) & (~steadfast_mask) & (~ending) & active
    if panic_done is not None:
        panic_trig = panic_trig & (~np.asarray(panic_done, dtype=bool))
    panic_checked = panic_trig.copy()                 # checks required this Skirmish (Resolute auto-pass included)
    # Resolute: the FIRST panic check a unit is ever required to take auto-passes (no roll, no
    # casualties); the one-shot is consumed. Parallel to Rally for break checks. `panic_used` is
    # persistent per-battle state carried by the caller across skirmishes.
    if resolute_firstpass_mask is not None and panic_used is not None:
        resolute = np.asarray(resolute_firstpass_mask, dtype=bool)
        panic_free = panic_trig & resolute & (~panic_used)
        panic_used = (panic_used | panic_free)
        panic_trig = panic_trig & (~panic_free)
    panic_test = panic_trig & (target <= FACES)
    panic_field = np.minimum(shake_cap, size)
    panic_cas = roller(rng, n, panic_field, target, panic_test)
    panic_cas = np.minimum(panic_cas, remaining)            # FIELD budget cap
    pre = size.copy()
    size = np.maximum(0, size - panic_cas)
    panic_lost = pre - size
    remaining = np.maximum(0, remaining - panic_lost)
    cas_panic_total = cas_panic_total + panic_lost
    panic_rout = panic_trig & (target >= ROUT_THR)
    # Cause 4 (panic) for runs wiped specifically by the panic test this skirmish.
    newly_panic = (size <= 0) & (cause == 0) & active & (panic_lost > 0)
    cause = np.where(newly_panic, 4, cause).astype(np.int8)

    # ── 2. BREAK check (exhausted, pre-token target) ─────────────────────────────
    break_trig = exhausted & (~unbreakable_mask) & (~ending) & active
    # Rally: the FIRST break check a unit is ever required to take auto-passes (no roll, no
    # casualties); the one-shot is consumed so every later break check is normal. `break_used`
    # is persistent per-battle state (carried by the caller across skirmishes). Distinct from
    # Unbreakable (skips ALL break tests) — Rally only buys the first crisis, keeping `shaking`
    # a live dial for every check after.
    if steadfast_firstpass_mask is not None and break_used is not None:
        rally = np.asarray(steadfast_firstpass_mask, dtype=bool)
        free_pass = break_trig & rally & (~break_used)   # first required check for a Rally unit
        break_used = (break_used | free_pass)
        break_trig = break_trig & (~free_pass)           # that check is auto-passed: no test
    break_test = break_trig & (target <= FACES) & (size > 0)
    break_field = np.minimum(shake_cap, size)
    break_cas = roller(rng, n, break_field, target, break_test)
    break_cas = np.minimum(break_cas, remaining)            # FIELD budget cap
    pre = size.copy()
    size = np.maximum(0, size - break_cas)
    break_lost = pre - size
    remaining = np.maximum(0, remaining - break_lost)
    cas_break_total = cas_break_total + break_lost
    newly_break = (size <= 0) & (cause == 0) & active & (break_lost > 0)
    cause = np.where(newly_break, 2, cause).astype(np.int8)

    # ── 3. ROUT (target >= 7 via either trigger) ─────────────────────────────────
    # Break-rout: exhausted with an unmakeable target (climbed by fatigue). Unshakable caps target
    # at 6 so it never reaches here; Unbreakable skips the TEST but STILL routs at >=7; Rally's
    # auto-passed first check also suppresses that check's rout (it "held"). Panic-rout: >5 net
    # combat with an unmakeable target.
    break_rout = exhausted & (target >= ROUT_THR)
    if steadfast_firstpass_mask is not None and break_used is not None:
        break_rout = break_rout & (~free_pass)   # the rallied first check does not rout
    routs = active & (break_rout | panic_rout) & (size > 0) & (~ending)
    rout_loss = np.where(routs, size, 0)
    cas_rout_total = cas_rout_total + rout_loss
    size = np.where(routs, 0, size)
    newly_rout = routs & (cause == 0)
    cause = np.where(newly_rout, 3, cause).astype(np.int8)

    return dict(size=size, panic_lost=panic_lost, break_lost=break_lost, rout_lost=rout_loss,
                cause=cause, cas_panic_total=cas_panic_total, cas_break_total=cas_break_total,
                cas_rout_total=cas_rout_total, exhausted=exhausted, break_used=break_used,
                panic_used=panic_used, panic_checks=panic_checked)
