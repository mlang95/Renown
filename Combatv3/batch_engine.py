"""
Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays,
removing the per-matchup Python dispatch overhead that bottlenecks the per-matchup engine.

Strategy: build a StaticArmy per distinct loadout (reusing ALL of its already-computed
fields — AP, base_init, tags, etc.), then GATHER those fields into per-battle-slot arrays.
The skirmish loop then runs once over all slots. Random playstyle first (uniform tactics);
playstyle/Outrider batching layered on after validation.

This module imports the existing engine pieces so the combat RULES are identical — we only
change the data layout (per-slot arrays instead of per-call scalars).
"""
import os as _os
# ── CRITICAL (Windows commit-limit fix) ──────────────────────────────────────────────────────
# Each spawned worker initializes numba. By default numba/LLVM spins up a threadpool sized to the
# CPU count and reserves a large block of virtual memory (Windows COMMIT) per process — several GB
# each. With 14 workers that reserved ~112 GB of commit and exhausted the 128 GB commit limit, so a
# tiny allocation failed even though physical RAM was ~45% free. This is WHY a run that worked with a
# warm numba cache (cheap kernel LOAD) breaks after an edit invalidates the cache (expensive parallel
# COMPILE in every worker). Capping numba/LLVM to a single thread collapses that per-process
# reservation. Must be set BEFORE numba is imported (directly or via vectorized_combat).
_os.environ.setdefault("NUMBA_NUM_THREADS", "1")
_os.environ.setdefault("NUMBA_THREADING_LAYER", "workqueue")
_os.environ.setdefault("OMP_NUM_THREADS", "1")
_os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
_os.environ.setdefault("MKL_NUM_THREADS", "1")
# ─────────────────────────────────────────────────────────────────────────────────────────────
import numpy as np
import renown_combat
from renown_combat import TACTICS
import vectorized_combat as vc
from vectorized_combat import StaticArmy, get_tactic_tables
try:
    import numba
    _HAVE_NUMBA = True
except Exception:
    _HAVE_NUMBA = False

# The 9 runtime tags tested inside the loop (besides what's baked into base_init).
RUNTIME_TAGS = ["+1TH", "+1TH first", "+1TH after_first", "Immune Tactic TH", "Drilled", "Immune Unwieldy", "Parry", "Poison",
                "Steady", "Unshakable", "Unstoppable", "Unwieldy"]


def _regen_threshold_for(tags_set, opp_tags_set):
    """Mirror vectorized_combat._regen_threshold using already-resolved tag sets."""
    return vc._regen_threshold(tags_set, opp_tags_set)


def pack_side(loadouts, is_attacker):
    """Given a list of loadouts (one per battle slot), build a dict of per-slot arrays
    by GATHERING each loadout's StaticArmy fields. No re-derivation of rules."""
    n = len(loadouts)
    armies = [StaticArmy(ld, is_attacker=is_attacker) for ld in loadouts]

    P = {}
    # Scalar combat stats
    P["to_hit"]      = np.array([a.to_hit for a in armies], dtype=np.int64)
    P["armor_save"]  = np.array([a.armor_save for a in armies], dtype=np.int64)
    P["shaking"]     = np.array([a.shaking for a in armies], dtype=np.int64)
    P["shake_bonus"] = np.array([a.shake_bonus for a in armies], dtype=np.int64)  # Abbey: -1 to shake target
    P["max_init"]    = np.array([a.max_init for a in armies], dtype=np.int64)
    P["endurance_start"] = np.array([a.endurance_start for a in armies], dtype=np.int64)
    P["size_start"]  = np.array([a.size_start for a in armies], dtype=np.int64)
    P["unshakable"]  = np.array([a.unshakable for a in armies], dtype=np.bool_)
    P["has_shield"]  = np.array([a.has_shield for a in armies], dtype=np.bool_)
    P["shield_immune"] = np.array([a.shield_immune for a in armies], dtype=np.bool_)
    P["shield_bonus_start"] = np.array([a.shield_bonus_start for a in armies], dtype=np.int64)
    P["shield_tbh_penalty_start"] = np.array([a.shield_tbh_penalty_start for a in armies], dtype=np.int64)
    P["shield_th_penalty_start"]  = np.array([a.shield_th_penalty_start for a in armies], dtype=np.int64)
    # Variant B (destroyed shield returns ALL its negatives): need the shield's init penalty and
    # whether the shield is the sole Unwieldy source, to undo them on destroyed runs.
    P["shield_init"] = np.array([a.shield_init for a in armies], dtype=np.int64)
    P["shield_unwieldy"] = np.array([a.shield_unwieldy for a in armies], dtype=np.bool_)
    P["unwieldy_non_shield"] = np.array([a.unwieldy_non_shield for a in armies], dtype=np.bool_)
    P["gf_armor"]    = np.array([a.gf_armor for a in armies], dtype=np.bool_)
    P["yew_heart"]   = np.array([a.yew_heart for a in armies], dtype=np.bool_)
    P["has_ranged"]  = np.array([a.ranged is not None for a in armies], dtype=np.bool_)
    P["is_bastard_dual"] = np.array([a.is_bastard_dual_profile for a in armies], dtype=np.bool_)
    # base_init(True) with is_attacker=True is the SEIZE value (+1 first skirmish); with
    # is_attacker=False it's the no-seize value. These must be built explicitly from BOTH
    # StaticArmy variants — NOT from `armies` (whose is_attacker depends on the call), or a
    # Ministry build on the B side would lose its Seize +1. The batch picks per-slot below.
    armies_seize   = [StaticArmy(ld, is_attacker=True)  for ld in loadouts]
    armies_noseize = [StaticArmy(ld, is_attacker=False) for ld in loadouts]
    P["ap_first"]    = np.array([a.ap_first for a in armies], dtype=np.int64)
    P["ap_normal"]   = np.array([a.ap_normal for a in armies], dtype=np.int64)
    P["binit_first_seize"]   = np.array([a.base_init(True)  for a in armies_seize],   dtype=np.int64)
    P["binit_first_noseize"] = np.array([a.base_init(True)  for a in armies_noseize], dtype=np.int64)
    P["binit_normal"]= np.array([a.base_init(False) for a in armies], dtype=np.int64)
    # Ministry innate Seize mode per slot (None/"first"/"first_two"/"every")
    def _seize_mode(tags):
        if "Seize: first_two" in tags: return "first_two"
        if "Seize: every" in tags: return "every"
        if "Seize: first" in tags: return "first"
        return None
    P["seize_mode"] = [_seize_mode(ld.extra_tags) for ld in loadouts]
    P["apo_heal"] = np.array([("Apothecary Heal" in ld.extra_tags) for ld in loadouts], dtype=np.bool_)
    # Runtime tag flags, first and normal (the loop tests these per skirmish)
    for t in RUNTIME_TAGS:
        key = t.replace(" ", "_").replace("+", "p")
        P[f"first_{key}"]  = np.array([t in a.tags_first  for a in armies], dtype=np.bool_)
        P[f"normal_{key}"] = np.array([t in a.tags_normal for a in armies], dtype=np.bool_)
    # Shatter/Cleave/Destroy Shield (first/normal) for strike resolution
    for t in ["Shatter Armor", "Cleave", "Destroy Shield"]:
        key = t.replace(" ", "_")
        P[f"first_{key}"]  = np.array([t in a.tags_first  for a in armies], dtype=np.bool_)
        P[f"normal_{key}"] = np.array([t in a.tags_normal for a in armies], dtype=np.bool_)
    # Keep the StaticArmy objects + tag sets around for regen/parry resolution per slot
    P["_armies"] = armies
    P["tags_first"]  = [a.tags_first for a in armies]
    P["tags_normal"] = [a.tags_normal for a in armies]
    # Per-phase ranged-attack flags (ranged: -1 to defender Parry capped at 6+, never riposted)
    P["first_is_ranged"]  = np.array([a.uses_ranged_first  for a in armies], dtype=np.bool_)
    P["normal_is_ranged"] = np.array([a.uses_ranged_normal for a in armies], dtype=np.bool_)
    return P


if __name__ == "__main__":
    # Validate packing reproduces StaticArmy scalars exactly on a sample.
    import sys, random
    sys.path.insert(0, "/home/claude/v3")
    import loadouts, playstyles
    pool = loadouts.archetype_pool(csv_path="/home/claude/v3/loadouts.csv")
    random.seed(1)
    sample = [ld._replace(playstyle=playstyles.assign_default_playstyle(ld)) for ld in random.sample(pool, 50)]
    Pa = pack_side(sample, is_attacker=True)
    # Spot-check 5 slots against fresh StaticArmy
    ok = True
    for i in [0, 10, 25, 40, 49]:
        sa = StaticArmy(sample[i], is_attacker=True)
        checks = [
            ("to_hit", Pa["to_hit"][i], sa.to_hit),
            ("armor_save", Pa["armor_save"][i], sa.armor_save),
            ("ap_first", Pa["ap_first"][i], sa.ap_first),
            ("binit_first", Pa["binit_first_seize"][i], sa.base_init(True)),
            ("binit_normal", Pa["binit_normal"][i], sa.base_init(False)),
            ("max_init", Pa["max_init"][i], sa.max_init),
            ("first_Steady", Pa["first_Steady"][i], "Steady" in sa.tags_first),
            ("first_Unstoppable", Pa["first_Unstoppable"][i], "Unstoppable" in sa.tags_first),
        ]
        for name, packed, ref in checks:
            if packed != ref:
                ok = False; print(f"  MISMATCH slot {i} {name}: packed={packed} ref={ref}")
    print("PACKING VALIDATED — all spot checks match" if ok else "PACKING HAS ERRORS")


# ──────────────────────────────────────────────────────────────────────────
# Batched strike/save resolution: per-slot flag arrays instead of a tag set.
# These mirror _roll_strikes_vec / _roll_saves_vec but vectorize the tag tests.
# ──────────────────────────────────────────────────────────────────────────

if _HAVE_NUMBA:
    @numba.njit(cache=True)
    def _strikes_kernel(target_th, auto_fail, auto_pass, front_line, rolls):
        n = rolls.shape[0]
        strikes = np.zeros(n, np.int32); sixes = np.zeros(n, np.int32)
        for i in range(n):
            fl = front_line[i]; tt = target_th[i]; af = auto_fail[i]; ap = auto_pass[i]
            sc = 0; sx = 0
            for j in range(fl):
                r = rolls[i, j]
                if ap or ((r >= tt) and (not af)):
                    sc += 1
                    if r == 6:
                        sx += 1
            strikes[i] = sc; sixes[i] = sx
        return strikes, sixes

    @numba.njit(cache=True)
    def _saves_kernel(n_strikes, shatter, sc, af, ap, pois, rolls,
                      pm, parry_rolls, rt, regen_rolls, rr, reroll_rolls, shatter_parry_thr,
                      parry_thr, riposte_on):
        n = n_strikes.shape[0]; out = np.zeros(n, np.int32); rip = np.zeros(n, np.int32)
        for i in range(n):
            ns = n_strikes[i]; shat = shatter[i]; sci = sc[i]; afi = af[i]; api = ap[i]; poi = pois[i]
            pmi = pm[i]; rti = rt[i]; rri = rr[i]; cnt = 0; rc = 0
            pthr = parry_thr[i]; ripi = riposte_on[i]; sthr = shatter_parry_thr[i]
            for j in range(ns):
                r = rolls[i, j]
                is_shat = j < shat
                if is_shat:
                    failed = True
                else:
                    failed = (((r < sci) or afi) and (not api)) or (r == 6 and poi)
                if not failed:
                    continue
                # Shatter hits use shatter_parry_thr (6 if defender has Riposte, else 7=unparryable);
                # normal hits use pthr (5; 6 vs Unstoppable; 4 if Improved Parry). A natural-6 parry
                # also triggers a riposte. 7 => never parries.
                thr = sthr if is_shat else pthr
                if pmi and thr <= 6 and parry_rolls[i, j] >= thr:
                    if ripi and parry_rolls[i, j] == 6:
                        rc += 1
                    continue
                if rti > 0:
                    if regen_rolls[i, j] >= rti:
                        continue
                    if rri and reroll_rolls[i, j] >= rti:
                        continue
                cnt += 1
            out[i] = cnt; rip[i] = rc
        return out, rip

    @numba.njit(cache=True)
    def _shake_kernel(field_size, shaking_value, mask, rolls):
        n = rolls.shape[0]; out = np.zeros(n, np.int32)
        for i in range(n):
            if not mask[i]:
                continue
            fs = field_size[i]; sv = shaking_value[i]; cnt = 0
            for j in range(fs):
                if rolls[i, j] < sv:
                    cnt += 1
            out[i] = cnt
        return out


def _roll_strikes_batch(rng, n, target_th, front_line, has_shatter, has_cleave,
                        has_destroy, def_has_shield, def_shield_destroyed, def_shield_immune):
    """Batched strikes. has_shatter/has_cleave/has_destroy/def_* are per-slot arrays (n,).
    The per-die counting is done in a numba kernel (bit-identical to the vectorized version:
    same RNG draws, same logic) to avoid the (n,20) boolean temporaries."""
    target_th_orig = target_th
    target_th_c = np.clip(target_th, 2, 7)
    auto_fail = target_th_c >= 7
    auto_pass = target_th_orig < 2
    rolls = rng.integers(1, 7, size=(n, 20), dtype=np.int8)
    if _HAVE_NUMBA:
        strikes, six_count = _strikes_kernel(target_th_c.astype(np.int64), auto_fail, auto_pass,
                                             front_line.astype(np.int64), rolls)
    else:
        die_idx = np.arange(20)[None, :]
        die_in_use = die_idx < front_line[:, None]
        is_strike = die_in_use & (auto_pass[:, None] | ((rolls >= target_th_c[:, None]) & (~auto_fail[:, None])))
        strikes = is_strike.sum(axis=1).astype(np.int32)
        six_count = ((rolls == 6) & is_strike).sum(axis=1).astype(np.int32)
    shatter_strikes = np.where(has_shatter, six_count, 0).astype(np.int32)
    cleave_extra = np.where(has_cleave, six_count, 0).astype(np.int32)
    can_destroy = has_destroy & def_has_shield & (~def_shield_immune)
    destroyed_shield = can_destroy & (six_count > 0) & (~def_shield_destroyed)
    return strikes + cleave_extra, shatter_strikes, destroyed_shield


def _roll_saves_batch(rng, n, save_target, n_strikes, shatter_strikes,
                      atk_poison, parry_mask, regen_thr, regen_reroll_mask,
                      atk_unstoppable=None, def_riposte=None,
                      def_parry_improved=None, def_can_parry_shatter=None, atk_is_ranged=None):
    """Batched saves. atk_poison/parry_mask/regen_reroll_mask per-slot bool (n,);
    regen_thr per-slot int (n,), 0 = no regen. Returns (casualties, ripostes), both (n,) int32.
    atk_unstoppable (n,) bool: where True the defender's parry needs 6+ not 5+ (Unstoppable -1 parry).
    def_riposte (n,) bool: where True, each parry die rolling EXACTLY 6 yields one riposte strike back.
    def_parry_improved (n,) bool: Improved Parry — normal-hit parry threshold improved by 1 (Unstoppable
      still applies). def_can_parry_shatter (n,) bool: Riposte — Shatter hits parryable on a natural 6
      (=riposte); otherwise Shatter is unparryable (threshold 7). Both default all-False."""
    max_strikes = int(n_strikes.max()) if n_strikes.any() else 0
    if max_strikes == 0:
        return np.zeros(n, dtype=np.int32), np.zeros(n, dtype=np.int32)
    max_strikes = min(max_strikes, 40)
    if atk_unstoppable is None:
        atk_unstoppable = np.zeros(n, dtype=np.bool_)
    if def_riposte is None:
        def_riposte = np.zeros(n, dtype=np.bool_)
    if def_parry_improved is None:
        def_parry_improved = np.zeros(n, dtype=np.bool_)
    if def_can_parry_shatter is None:
        def_can_parry_shatter = np.zeros(n, dtype=np.bool_)
    if atk_is_ranged is None:
        atk_is_ranged = np.zeros(n, dtype=np.bool_)
    # Parry threshold vs normal hits: base 5 (4 with Improved Parry), +1 if attacker Unstoppable,
    # +1 if the strike is RANGED, CAPPED at 6 (a 6 always has a chance). Shatter: 6 with Riposte
    # (already at cap) else 7 = unparryable.
    parry_thr = (5 - def_parry_improved.astype(np.int64)
                   + atk_unstoppable.astype(np.int64)
                   + atk_is_ranged.astype(np.int64))
    parry_thr = np.minimum(parry_thr, 6)
    shatter_parry_thr = np.where(def_can_parry_shatter, 6, 7).astype(np.int64)  # Riposte parries Shatter on 6
    # A parry vs a RANGED strike never triggers a riposte (it only parries).
    def_riposte = def_riposte & ~atk_is_ranged
    save_clipped = np.clip(save_target, 2, 7)
    auto_fail_save = save_clipped >= 7
    auto_pass_save = save_target < 2
    rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8)
    # Generate parry/regen/reroll rolls in the SAME conditional order as the vectorized version
    # so the RNG stream (and therefore the result) is bit-identical.
    if parry_mask.any():
        parry_rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8)
    else:
        parry_rolls = np.zeros((n, max_strikes), dtype=np.int8)
    thr = np.where(regen_thr > 0, regen_thr, 7).astype(np.int64)
    has_regen = (regen_thr > 0).any()
    if has_regen:
        regen_rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8)
        if regen_reroll_mask.any():
            reroll_rolls = rng.integers(1, 7, size=(n, max_strikes), dtype=np.int8)
        else:
            reroll_rolls = np.zeros((n, max_strikes), dtype=np.int8)
    else:
        regen_rolls = np.zeros((n, max_strikes), dtype=np.int8)
        reroll_rolls = np.zeros((n, max_strikes), dtype=np.int8)
    if _HAVE_NUMBA:
        return _saves_kernel(n_strikes.astype(np.int64), shatter_strikes.astype(np.int64),
                             save_clipped.astype(np.int64), auto_fail_save, auto_pass_save, atk_poison,
                             rolls, parry_mask, parry_rolls, thr, regen_rolls, regen_reroll_mask, reroll_rolls,
                             shatter_parry_thr, parry_thr, def_riposte.astype(np.bool_))
    # pure-numpy fallback
    strike_idx = np.arange(max_strikes)[None, :]
    strike_in_use = strike_idx < n_strikes[:, None]
    is_shatter = strike_idx < shatter_strikes[:, None]
    normal_fail = (rolls < save_clipped[:, None]) | auto_fail_save[:, None]
    normal_fail = normal_fail & (~auto_pass_save[:, None])
    normal_fail = normal_fail | ((rolls == 6) & atk_poison[:, None])
    failed = (is_shatter | (normal_fail & strike_in_use & ~is_shatter)) & strike_in_use
    ripostes = np.zeros(n, dtype=np.int32)
    if parry_mask.any():
        # Shatter hits parryable only where def_can_parry_shatter (threshold 6); else unparryable.
        thr_normal = parry_thr[:, None]
        parry_ok_normal = (parry_rolls >= thr_normal) & (~is_shatter)
        parry_ok_shatter = is_shatter & def_can_parry_shatter[:, None] & (parry_rolls >= 6)
        parried = (parry_ok_normal | parry_ok_shatter) & failed & parry_mask[:, None]
        # riposte: a parry die that is exactly 6, on a defender with Riposte
        rip_hits = parried & (parry_rolls == 6) & def_riposte[:, None]
        ripostes = rip_hits.sum(axis=1).astype(np.int32)
        failed = failed & (~parried)
    if has_regen:
        thr2 = thr[:, None]
        regen_save = (regen_rolls >= thr2) & failed
        if regen_reroll_mask.any():
            still = failed & (~regen_save)
            regen_save = regen_save | ((reroll_rolls >= thr2) & still & regen_reroll_mask[:, None])
        failed = failed & (~regen_save)
    return failed.sum(axis=1).astype(np.int32), ripostes


def _precompute_regen_parry(Pa, Pb):
    """Per-slot regen thresholds (A defending vs B's tags, and B vs A) and parry/reroll flags.
    Uses the StaticArmy tag sets gathered in pack_side. Done once per block (not per skirmish)
    because tags_first/normal regen content doesn't change mid-battle — but the regen THRESHOLD
    depends on the opponent's Rend, so it's a per-slot pair value. We compute for first & normal.
    """
    n = len(Pa["_armies"])
    out = {}
    for skl in ("first", "normal"):
        a_tags_list = Pa["tags_first"] if skl == "first" else Pa["tags_normal"]
        b_tags_list = Pb["tags_first"] if skl == "first" else Pb["tags_normal"]
        a_regen = np.zeros(n, dtype=np.int64)
        b_regen = np.zeros(n, dtype=np.int64)
        a_parry = np.zeros(n, dtype=np.bool_)
        b_parry = np.zeros(n, dtype=np.bool_)
        a_reroll = np.zeros(n, dtype=np.bool_)
        b_reroll = np.zeros(n, dtype=np.bool_)
        a_riposte = np.zeros(n, dtype=np.bool_)
        b_riposte = np.zeros(n, dtype=np.bool_)
        a_imp_parry = np.zeros(n, dtype=np.bool_)
        b_imp_parry = np.zeros(n, dtype=np.bool_)
        for i in range(n):
            at, bt = a_tags_list[i], b_tags_list[i]
            ra = vc._regen_threshold(at, bt)   # A regenerates, B's Rend worsens it
            rb = vc._regen_threshold(bt, at)
            a_regen[i] = ra if ra is not None else 0
            b_regen[i] = rb if rb is not None else 0
            a_parry[i] = ("Parry" in at) or ("Improved Parry" in at)
            b_parry[i] = ("Parry" in bt) or ("Improved Parry" in bt)
            a_reroll[i] = vc._has_regen_reroll(at)
            b_reroll[i] = vc._has_regen_reroll(bt)
            a_riposte[i] = ("Riposte" in at)
            b_riposte[i] = ("Riposte" in bt)
            a_imp_parry[i] = ("Improved Parry" in at)
            b_imp_parry[i] = ("Improved Parry" in bt)
        out[skl] = dict(a_regen=a_regen, b_regen=b_regen, a_parry=a_parry, b_parry=b_parry,
                        a_reroll=a_reroll, b_reroll=b_reroll,
                        a_riposte=a_riposte, b_riposte=b_riposte,
                        a_imp_parry=a_imp_parry, b_imp_parry=b_imp_parry)
    return out


def run_batch_random(pairs, n_runs=50, seed=2026, max_skirmishes=40, mode="random",
                     force_a=0, force_b=0, return_first_tactics=False):
    """Resolve a BLOCK of matchups in one set of arrays.
       mode="random"    → uniform-over-6 tactics + fatigue-conditional Fall Back (Random playstyle)
       mode="playstyle" → each slot uses its loadout's assigned playstyle (per-slot weights)
    Returns dict of per-pair result arrays. NOTE: Outrider counter-pick is inert for the
    real pool (no "Outrider:" extra_tag is emitted), matching the per-matchup engine, so
    playstyle mode does NOT run a live counter-pick.
    """
    npairs = len(pairs)
    if npairs == 0:
        return {}
    a_loadouts = [p[0] for p in pairs]
    b_loadouts = [p[1] for p in pairs]
    # === Domain-standing OPPONENT debuffs (confers:*) — mirror the scalar engine ===
    # A build with Established Cunning carries "confers:Blocked"; Sovereign Cunning "confers:Strain".
    # These debuff the OPPONENT, not self. Strip 'confers:X' from each side and add X to the other
    # side's extra_tags BEFORE pack_side builds the StaticArmys — base_init already reads Blocked
    # (-1 init first skirmish unless Immune Blocked) and Strain (-1 init unless Immune Strain), so the
    # init effect is honored automatically once the tag lands on the right army.
    def _apply_confers_pair(ld_self, ld_opp):
        confers = {t.split(":", 1)[1] for t in ld_self.extra_tags if t.startswith("confers:")}
        self_clean = frozenset(t for t in ld_self.extra_tags if not t.startswith("confers:"))
        ld_self2 = ld_self._replace(extra_tags=self_clean)
        ld_opp2 = ld_opp._replace(extra_tags=frozenset(set(ld_opp.extra_tags) | confers)) if confers else ld_opp
        return ld_self2, ld_opp2
    _any_confers = any(any(t.startswith("confers:") for t in ld.extra_tags)
                       for ld in a_loadouts) or \
                   any(any(t.startswith("confers:") for t in ld.extra_tags)
                       for ld in b_loadouts)
    if _any_confers:
        na, nb = [], []
        for la, lb in zip(a_loadouts, b_loadouts):
            la2, lb2 = _apply_confers_pair(la, lb)   # A's confers -> B
            lb2, la2 = _apply_confers_pair(lb2, la2)  # B's confers -> A
            na.append(la2); nb.append(lb2)
        a_loadouts, b_loadouts = na, nb
    Pa = pack_side(a_loadouts, is_attacker=True)
    Pb = pack_side(b_loadouts, is_attacker=False)
    RP = _precompute_regen_parry(Pa, Pb)
    # Outrider counter-pick precompute (per-pair best-response tables + modes). Inert pairs
    # have mode=None and are skipped. Counter index tables are (npairs, 7) per side.
    a_omode, b_omode, a_ct, b_ct = _precompute_outrider_tables(pairs, Pa, Pb)
    _any_outrider = any(m is not None for m in a_omode) or any(m is not None for m in b_omode)
    if _any_outrider:
        # Stack per-pair (7,) counter tables into (npairs,7) arrays; None → identity (unused).
        a_ct_arr = np.array([(c if c is not None else np.arange(7)) for c in a_ct], dtype=np.int64)
        b_ct_arr = np.array([(c if c is not None else np.arange(7)) for c in b_ct], dtype=np.int64)
        # These tables are static across skirmishes, so tile to (N,7) ONCE here rather than
        # re-running np.repeat every skirmish inside the loop.
        pair_ct_a = np.repeat(a_ct_arr, n_runs, axis=0)            # (N,7)
        pair_ct_b = np.repeat(b_ct_arr, n_runs, axis=0)            # (N,7)
    # Per-slot playstyle name arrays (used only in playstyle mode)
    a_ps_slot = np.repeat(np.array([(ld.playstyle or "Random") for ld in a_loadouts]), n_runs)
    b_ps_slot = np.repeat(np.array([(ld.playstyle or "Random") for ld in b_loadouts]), n_runs)

    N = npairs * n_runs                    # total battle slots
    # pair index for each slot (so we can scatter results back per pair)
    pair_of_slot = np.repeat(np.arange(npairs), n_runs)

    def tile(arr):  # (npairs,) -> (N,) by repeating each pair's value n_runs times
        return np.repeat(arr, n_runs)

    rng = np.random.default_rng(seed)
    tab = get_tactic_tables()
    FB_IDX = 6
    TAC = renown_combat.TACTICS

    # Per-slot static arrays (tiled from per-pair)
    a_to_hit = tile(Pa["to_hit"]); b_to_hit = tile(Pb["to_hit"])
    a_armor = tile(Pa["armor_save"]); b_armor = tile(Pb["armor_save"])
    a_shaking = tile(Pa["shaking"]); b_shaking = tile(Pb["shaking"])
    a_shake_bonus = tile(Pa["shake_bonus"]); b_shake_bonus = tile(Pb["shake_bonus"])
    a_maxinit = tile(Pa["max_init"]); b_maxinit = tile(Pb["max_init"])
    a_unshak = tile(Pa["unshakable"]); b_unshak = tile(Pb["unshakable"])
    a_hasshield = tile(Pa["has_shield"]); b_hasshield = tile(Pb["has_shield"])
    a_shimm = tile(Pa["shield_immune"]); b_shimm = tile(Pb["shield_immune"])
    a_shbonus = tile(Pa["shield_bonus_start"]); b_shbonus = tile(Pb["shield_bonus_start"])
    # variant-B shield restoration inputs
    a_shinit = tile(Pa["shield_init"]); b_shinit = tile(Pb["shield_init"])
    a_sh_only_unw = tile(Pa["shield_unwieldy"]) & (~tile(Pa["unwieldy_non_shield"]))
    b_sh_only_unw = tile(Pb["shield_unwieldy"]) & (~tile(Pb["unwieldy_non_shield"]))
    a_shtbh = tile(Pa["shield_tbh_penalty_start"]); b_shtbh = tile(Pb["shield_tbh_penalty_start"])
    a_shth = tile(Pa["shield_th_penalty_start"]); b_shth = tile(Pb["shield_th_penalty_start"])
    a_gf = tile(Pa["gf_armor"]); b_gf = tile(Pb["gf_armor"])
    a_size0 = tile(Pa["size_start"]); b_size0 = tile(Pb["size_start"])

    # first/normal AP, base_init
    a_ap_f = tile(Pa["ap_first"]); a_ap_n = tile(Pa["ap_normal"])
    b_ap_f = tile(Pb["ap_first"]); b_ap_n = tile(Pb["ap_normal"])
    # === Seize the Initiative assignment (matches the per-matchup engine, balanced mode) ===
    # Absent Ministry, the initiator (who gets first-skirmish +1) is a 50/50 split across runs,
    # NOT always A. Ministry ("Seize: ...") overrides: that side always seizes, opponent never
    # does; if BOTH have Ministry the claims cancel and the 50/50 split stands.
    a_min = np.array([m is not None for m in Pa["seize_mode"]], dtype=bool)
    b_min = np.array([m is not None for m in Pb["seize_mode"]], dtype=bool)
    # Per-slot 50/50 initiator split (first half of each pair's runs → A initiates), matching
    # the engine's alternate_attacker split (a_initiates[:n_runs//2]=True per matchup).
    half = n_runs // 2
    init_pattern = np.zeros(n_runs, dtype=bool); init_pattern[:half] = True   # A initiates these runs
    a_initiates = np.tile(init_pattern, npairs)
    a_seizes = a_initiates.copy(); b_seizes = ~a_initiates
    both_min = tile(a_min & b_min)
    a_min_t = tile(a_min); b_min_t = tile(b_min)
    # Single-Ministry override (not both): that side always seizes, opponent never.
    only_a_min = a_min_t & (~b_min_t)
    only_b_min = b_min_t & (~a_min_t)
    a_seizes = np.where(only_a_min, True, np.where(only_b_min, False, a_seizes))
    b_seizes = np.where(only_b_min, True, np.where(only_a_min, False, b_seizes))
    # (both_min → keep the initiate-driven split: the two Ministries cancel.)
    a_bi_f = np.where(a_seizes, tile(Pa["binit_first_seize"]), tile(Pa["binit_first_noseize"]))
    b_bi_f = np.where(b_seizes, tile(Pb["binit_first_seize"]), tile(Pb["binit_first_noseize"]))
    a_bi_n = tile(Pa["binit_normal"]); b_bi_n = tile(Pb["binit_normal"])
    # Seize-second (Ministry mastery "first_two"/"every"): +1 on skirmish index 1 too, only for
    # the side that retained its Seize claim.
    a_seize_second = tile(np.array([m in ("first_two", "every") for m in Pa["seize_mode"]], dtype=bool)) & (~both_min)
    b_seize_second = tile(np.array([m in ("first_two", "every") for m in Pb["seize_mode"]], dtype=bool)) & (~both_min)
    a_seize_persist = tile(np.array([m == "every" for m in Pa["seize_mode"]], dtype=bool))
    b_seize_persist = tile(np.array([m == "every" for m in Pb["seize_mode"]], dtype=bool))
    # "every" seize adds +1 to the normal base_init too (persistent).
    a_bi_n = a_bi_n + a_seize_persist.astype(np.int64)
    b_bi_n = b_bi_n + b_seize_persist.astype(np.int64)

    def tflag(P, skl, tag):
        key = tag.replace(" ", "_").replace("+", "p")
        return tile(P[f"{skl}_{key}"])

    # state
    a_size = a_size0.copy(); b_size = b_size0.copy()
    a_end = tile(Pa["endurance_start"]).copy(); b_end = tile(Pb["endurance_start"]).copy()
    a_fat = np.zeros(N, dtype=np.int64); b_fat = np.zeros(N, dtype=np.int64)
    a_shdest = np.zeros(N, dtype=bool); b_shdest = np.zeros(N, dtype=bool)
    active = (a_size > 0) & (b_size > 0)
    a_cause = np.zeros(N, dtype=np.int8); b_cause = np.zeros(N, dtype=np.int8)
    # casualty totals
    a_kill = np.zeros(N); b_kill = np.zeros(N)
    a_waver = np.zeros(N); b_waver = np.zeros(N)   # losses to the Waver test (>5 net combat)
    a_shake = np.zeros(N); b_shake = np.zeros(N)
    a_rout = np.zeros(N); b_rout = np.zeros(N)
    skirm_count = np.zeros(N, dtype=np.int64)
    # Apothecary Heal: at start of each skirmish after the first, heal 1 retinue per 4
    # casualties taken in the PREVIOUS skirmish (capped at size_start). Per-slot flag.
    a_apo = tile(Pa["apo_heal"]); b_apo = tile(Pb["apo_heal"])
    a_prev_cas = np.zeros(N, dtype=np.int64); b_prev_cas = np.zeros(N, dtype=np.int64)
    # Combat-only prev casualties: heal restores ONLY combat losses (shake/rout can't be healed).
    a_prev_combat = np.zeros(N, dtype=np.int64); b_prev_combat = np.zeros(N, dtype=np.int64)
    # Combat-only prev casualties: heal restores ONLY combat losses (shake/rout can't be healed).
    a_prev_combat = np.zeros(N, dtype=np.int64); b_prev_combat = np.zeros(N, dtype=np.int64)
    a_cap = a_size0.copy(); b_cap = b_size0.copy()

    for sk in range(max_skirmishes):
        active = active & (a_size > 0) & (b_size > 0)
        if not active.any():
            break
        first = (sk == 0)
        skl = "first" if first else "normal"

        # Apothecary mastery: heal at start of skirmish (after first), 1 per 4 prev-skirmish COMBAT
        # casualties, only for active runs, capped at starting size. Heal cannot restore shake/rout.
        a_heal = np.zeros(N, dtype=np.int64); b_heal = np.zeros(N, dtype=np.int64)
        if not first:
            if a_apo.any():
                a_heal = np.where(active & a_apo, a_prev_combat // 4, 0)
                a_size = np.minimum(a_size + a_heal, a_cap)
            if b_apo.any():
                b_heal = np.where(active & b_apo, b_prev_combat // 4, 0)
                b_size = np.minimum(b_size + b_heal, b_cap)

        a_ap = a_ap_f if first else a_ap_n
        b_ap = b_ap_f if first else b_ap_n
        a_bi = a_bi_f if first else a_bi_n
        b_bi = b_bi_f if first else b_bi_n
        # Ministry mastery: Seize also applies on the SECOND skirmish (index 1) for the side
        # that holds the "first_two"/"every" claim (already excludes the persistent "every" path,
        # which baked +1 into a_bi_n above, so guard against double-adding).
        if sk == 1:
            a_bi = a_bi + (a_seize_second & (~a_seize_persist)).astype(np.int64)
            b_bi = b_bi + (b_seize_second & (~b_seize_persist)).astype(np.int64)

        # tags per-slot (first/normal)
        a_steady = tflag(Pa, skl, "Steady"); b_steady = tflag(Pb, skl, "Steady")
        a_unw = tflag(Pa, skl, "Unwieldy"); b_unw = tflag(Pb, skl, "Unwieldy")
        a_imunw = tflag(Pa, skl, "Immune Unwieldy"); b_imunw = tflag(Pb, skl, "Immune Unwieldy")
        a_unstop = tflag(Pa, skl, "Unstoppable"); b_unstop = tflag(Pb, skl, "Unstoppable")
        a_is_rng = tile(Pa[f"{skl}_is_ranged"]); b_is_rng = tile(Pb[f"{skl}_is_ranged"])
        a_immtac = tflag(Pa, skl, "Immune Tactic TH"); b_immtac = tflag(Pb, skl, "Immune Tactic TH")
        a_p1th = tflag(Pa, skl, "+1TH"); b_p1th = tflag(Pb, skl, "+1TH")
        # First-skirmish-only +1TH (Ministry innate): applies only on the first skirmish.
        a_p1th_first = tflag(Pa, skl, "+1TH first") & first
        b_p1th_first = tflag(Pb, skl, "+1TH first") & first
        # After-first +1TH (Ministry mastery): applies on every skirmish except the first.
        a_p1th_rest = tflag(Pa, skl, "+1TH after_first") & (~first)
        b_p1th_rest = tflag(Pb, skl, "+1TH after_first") & (~first)
        a_shat = tflag(Pa, skl, "Shatter Armor"); b_shat = tflag(Pb, skl, "Shatter Armor")
        a_clv = tflag(Pa, skl, "Cleave"); b_clv = tflag(Pb, skl, "Cleave")
        a_dstr = tflag(Pa, skl, "Destroy Shield"); b_dstr = tflag(Pb, skl, "Destroy Shield")

        # === Tactic selection ===
        if mode == "random":
            # Random: uniform over the 6 non-Fall-Back tactics. No Fall Back in Random play
            # (matches playstyles.resolve_playstyle_weights("Random")).
            a_tac = rng.integers(0, 6, size=N)
            b_tac = rng.integers(0, 6, size=N)
        elif mode == "forced":
            # Force a fixed tactic every skirmish. A side with force = -1 plays the RANDOM mix
            # (uniform over the 6 non-Fall-Back tactics) — used for "tactic X into the field".
            a_tac = (np.full(N, int(force_a), dtype=np.int64) if int(force_a) >= 0
                     else rng.integers(0, 6, size=N))
            b_tac = (np.full(N, int(force_b), dtype=np.int64) if int(force_b) >= 0
                     else rng.integers(0, 6, size=N))
        else:
            # PLAYSTYLE: per-slot weights from each loadout's assigned playstyle, rebuilt each
            # skirmish (adaptive playstyles read live per-slot size/endurance/fatigue).
            state_full = {"a_size": a_size, "b_size": b_size, "a_end": a_end,
                          "b_end": b_end, "a_fat": a_fat, "b_fat": b_fat}
            state_full_b = {"a_size": b_size, "b_size": a_size, "a_end": b_end,
                            "b_end": a_end, "a_fat": b_fat, "b_fat": a_fat}
            a_w = _batched_weights(a_ps_slot, state_full, N, rng)
            b_w = _batched_weights(b_ps_slot, state_full_b, N, rng)
            a_tac = _sample_from_weights(a_w, rng)
            b_tac = _sample_from_weights(b_w, rng)

        # === Outrider counter-pick override ===
        # When a side's Outrider fires this skirmish, it reveals the opponent's pick and plays
        # the weapon-aware best response (counter_weight=0.8 on the best-response tactic, rest
        # spread over the other 6). Matches the per-matchup engine. Inert pairs untouched.
        if _any_outrider:
            a_fires = _outrider_fires(a_omode, sk, n_runs)   # (N,) bool
            b_fires = _outrider_fires(b_omode, sk, n_runs)
            # A's Outrider fires: B already picked; A plays best response to B's pick.
            # Match reference _counter_weights_from_table: 0.8 on best response, 0.2/6 on each
            # of the other six tactics, then sample.
            if a_fires.any():
                a_best = pair_ct_a[np.arange(N), b_tac]                 # (N,)
                w = np.full((N, 7), 0.2 / 6.0)
                w[np.arange(N), a_best] = 0.8
                a_counter = _sample_from_weights(w, rng)
                a_tac = np.where(a_fires, a_counter, a_tac)
            if b_fires.any():
                b_best = pair_ct_b[np.arange(N), a_tac]
                w = np.full((N, 7), 0.2 / 6.0)
                w[np.arange(N), b_best] = 0.8
                b_counter = _sample_from_weights(w, rng)
                b_tac = np.where(b_fires, b_counter, b_tac)

        a_I_mod = tab["a_I"][a_tac, b_tac]; a_TH_mod = tab["a_TH"][a_tac, b_tac]; a_TS_mod = tab["a_TS"][a_tac, b_tac]
        b_I_mod = tab["b_I"][a_tac, b_tac]; b_TH_mod = tab["b_TH"][a_tac, b_tac]; b_TS_mod = tab["b_TS"][a_tac, b_tac]
        # Record the ACTUAL first-skirmish tactics (after any Outrider override) for the
        # empirical tactic matrix. Captured once, on the first skirmish.
        if first:
            a_tac0 = a_tac.copy(); b_tac0 = b_tac.copy()
        end_pair = tab["end"][a_tac, b_tac]
        no_combat_pair = tab["no_combat"][a_tac, b_tac]
        no_combat_endurance_pair = tab["no_combat_endurance"][a_tac, b_tac]

        # Steady/Unwieldy init clamps (per-slot, no bastard-dual here yet).
        a_I_mod = np.where(a_steady & (a_I_mod < 0), 0, a_I_mod)
        b_I_mod = np.where(b_steady & (b_I_mod < 0), 0, b_I_mod)
        # Unwieldy positive-init clamp. Variant B: if the shield is the SOLE Unwieldy source, the
        # clamp is lifted on runs where that shield is destroyed (a destroyed shield stops being
        # Unwieldy). Non-shield Unwieldy (weapon/armor/dual) still clamps regardless.
        a_unw_active = a_unw & (~a_imunw) & ~(a_sh_only_unw & a_shdest)
        b_unw_active = b_unw & (~b_imunw) & ~(b_sh_only_unw & b_shdest)
        a_I_mod = np.where(a_unw_active & (a_I_mod > 0), 0, a_I_mod)
        b_I_mod = np.where(b_unw_active & (b_I_mod > 0), 0, b_I_mod)

        # Variant B: a destroyed shield returns its initiative penalty too — add back shield_init on
        # destroyed runs (shield_init is negative for Wooden/Scutum/Tower, so -shield_init cancels it).
        a_init_restore = np.where(a_shdest, -a_shinit, 0)
        b_init_restore = np.where(b_shdest, -b_shinit, 0)
        a_init = np.clip(a_bi + a_I_mod + a_init_restore, -2, a_maxinit)
        b_init = np.clip(b_bi + b_I_mod + b_init_restore, -2, b_maxinit)

        ending = end_pair & active
        no_combat_this = no_combat_pair & active
        proceed = active & (~ending) & (~no_combat_this)

        a_tripped = (a_init <= -2) & proceed
        b_tripped = (b_init <= -2) & proceed
        a_first_mask = (a_init > b_init) & proceed & (~a_tripped)
        b_first_mask = (b_init > a_init) & proceed & (~b_tripped)
        simul_mask = (a_init == b_init) & proceed

        a_front = np.minimum(vc.FRONT_CAP, a_size); b_front = np.minimum(vc.FRONT_CAP, b_size)
        a_res = np.minimum(vc.RESERVE_CAP, np.maximum(0, a_size - vc.FRONT_CAP)); b_res = np.minimum(vc.RESERVE_CAP, np.maximum(0, b_size - vc.FRONT_CAP))

        # to-hit (random mode: Yew only first skirmish w/ ranged — but random pool rarely; include for parity)
        yew_a = 0; yew_b = 0  # Yew Heart handled via tags? It's an extra_tag, not in RUNTIME_TAGS; skip (matches: random uses same)
        # === To-hit with the FATIGUE 6+ CAP (matches vectorized_combat) ===
        wth_a = np.where(a_p1th, -1, 0) + np.where(a_p1th_first, -1, 0) + np.where(a_p1th_rest, -1, 0)
        wth_b = np.where(b_p1th, -1, 0) + np.where(b_p1th_first, -1, 0) + np.where(b_p1th_rest, -1, 0)
        b_tbh = np.where(b_shdest, 0, b_shtbh); a_tbh = np.where(a_shdest, 0, a_shtbh)
        a_th_self = np.where(a_shdest, 0, a_shth); b_th_self = np.where(b_shdest, 0, b_shth)
        a_tbh_eff = np.where(a_unstop, 0, b_tbh)   # Unstoppable v2: only ignores shield TBH
        b_tbh_eff = np.where(b_unstop, 0, a_tbh)
        # improving (lower target): weapon +1TH (wth, =-1), positive tactic TH. (Yew skipped.)
        # worsening (raise target): own/enemy shield TH, negative tactic TH.
        # Cap (base + improving + fatigue) at 6; then worsening mods apply and can reach 7+.
        a_th_improve = wth_a - np.maximum(a_TH_mod, 0)
        b_th_improve = wth_b - np.maximum(b_TH_mod, 0)
        a_tac_worsen = np.where(a_immtac, 0, np.maximum(-a_TH_mod, 0))   # Immune Tactic TH (Ministry innate)
        a_th_worsen = a_tbh_eff + a_th_self + a_tac_worsen
        b_tac_worsen = np.where(b_immtac, 0, np.maximum(-b_TH_mod, 0))
        b_th_worsen = b_tbh_eff + b_th_self + b_tac_worsen
        a_th_pre = np.minimum(a_to_hit + a_th_improve + a_fat, 6)
        b_th_pre = np.minimum(b_to_hit + b_th_improve + b_fat, 6)
        # Blunder: clamp to 6+ at this step (then worsening mods can push beyond).
        a_th_pre = np.where(a_tripped, np.maximum(a_th_pre, 6), a_th_pre)
        b_th_pre = np.where(b_tripped, np.maximum(b_th_pre, 6), b_th_pre)
        a_tt = a_th_pre + a_th_worsen
        b_tt = b_th_pre + b_th_worsen

        b_ap_vs_a = b_ap + np.where(a_gf, 1, 0)
        a_ap_vs_b = a_ap + np.where(b_gf, 1, 0)
        a_sv = a_armor - b_ap_vs_a - np.where(a_shdest, 0, a_shbonus) - a_TS_mod
        b_sv = b_armor - a_ap_vs_b - np.where(b_shdest, 0, b_shbonus) - b_TS_mod

        rr = RP[skl]
        # regen/parry per-slot (tiled)
        a_regen = np.repeat(RP[skl]["a_regen"], n_runs); b_regen = np.repeat(RP[skl]["b_regen"], n_runs)
        a_parry = np.repeat(RP[skl]["a_parry"], n_runs); b_parry = np.repeat(RP[skl]["b_parry"], n_runs)
        a_reroll = np.repeat(RP[skl]["a_reroll"], n_runs); b_reroll = np.repeat(RP[skl]["b_reroll"], n_runs)
        a_riposte = np.repeat(RP[skl]["a_riposte"], n_runs); b_riposte = np.repeat(RP[skl]["b_riposte"], n_runs)
        a_imp_parry = np.repeat(RP[skl]["a_imp_parry"], n_runs); b_imp_parry = np.repeat(RP[skl]["b_imp_parry"], n_runs)
        # fatigue disables parry/regen/riposte
        a_parry_eff = a_parry & (a_fat == 0); b_parry_eff = b_parry & (b_fat == 0)
        a_regen_eff = np.where(a_fat == 0, a_regen, 0); b_regen_eff = np.where(b_fat == 0, b_regen, 0)
        a_riposte_eff = a_riposte & (a_fat == 0); b_riposte_eff = b_riposte & (b_fat == 0)

        # poison per-slot: Poison in attacker's tags AND not Immune Poison in defender's tags
        a_poison = _poison_batch(Pa, Pb, skl, n_runs)
        b_poison = _poison_batch(Pb, Pa, skl, n_runs)

        # A strikes B
        a_strk, a_sh, a_destroys = _roll_strikes_batch(rng, N, a_tt, a_front, a_shat, a_clv, a_dstr,
                                                       b_hasshield, b_shdest, b_shimm)
        a_fights = proceed & (a_size > 0)
        a_strk = np.where(a_fights, a_strk, 0); a_sh = np.where(a_fights, a_sh, 0)
        a_destroys = a_destroys & a_fights
        b_cas, b_rip = _roll_saves_batch(rng, N, b_sv, a_strk, a_sh, a_poison, b_parry_eff, b_regen_eff, b_reroll,
                                         atk_unstoppable=a_unstop, def_riposte=b_riposte_eff,
                                         def_parry_improved=b_imp_parry, def_can_parry_shatter=b_riposte,
                                         atk_is_ranged=a_is_rng)
        b_cas = np.minimum(b_cas, b_front)
        b_shdest = b_shdest | a_destroys
        # B's riposte: each natural-6 parry strikes A back once at B's weapon AP (b_ap_vs_a), single
        # clean strikes — no Cleave/Shatter. B's Unstoppable (b_unstop) still -1's A's parry; A's
        # Parry/regen still defend. Resolve immediately and fold into A's casualties this skirmish.
        a_rip_cas = np.zeros(N, dtype=np.int32)
        if b_riposte_eff.any():
            a_sv_rip = a_armor - b_ap_vs_a - np.where(a_shdest, 0, a_shbonus) - a_TS_mod
            a_rip_cas, _ = _roll_saves_batch(rng, N, a_sv_rip, b_rip, np.zeros(N, np.int32),
                                             np.zeros(N, np.bool_), a_parry_eff, a_regen_eff, a_reroll,
                                             atk_unstoppable=b_unstop, def_riposte=np.zeros(N, np.bool_))

        b_front_after = np.maximum(0, b_front - b_cas)
        b_front_refill = np.minimum(vc.FRONT_CAP, b_front_after + b_res)
        b_eff_front = np.where(a_first_mask, b_front_refill, b_front)
        b_alive = np.where(a_first_mask, (b_size - b_cas) > 0, b_size > 0)
        b_fights = proceed & b_alive
        b_strk, b_sh, b_destroys = _roll_strikes_batch(rng, N, b_tt, b_eff_front, b_shat, b_clv, b_dstr,
                                                       a_hasshield, a_shdest, a_shimm)
        b_strk = np.where(b_fights, b_strk, 0); b_sh = np.where(b_fights, b_sh, 0)
        b_destroys = b_destroys & b_fights
        a_cas, a_rip = _roll_saves_batch(rng, N, a_sv, b_strk, b_sh, b_poison, a_parry_eff, a_regen_eff, a_reroll,
                                         atk_unstoppable=b_unstop, def_riposte=a_riposte_eff,
                                         def_parry_improved=a_imp_parry, def_can_parry_shatter=a_riposte,
                                         atk_is_ranged=b_is_rng)
        a_cas = np.minimum(a_cas, a_front)
        # A's riposte back onto B (A's weapon AP a_ap_vs_b, single clean strikes). Plus any riposte B
        # already dealt to A from A's opening strike (a_rip_cas) folds into A's casualties.
        b_rip_cas = np.zeros(N, dtype=np.int32)
        if a_riposte_eff.any():
            b_sv_rip = b_armor - a_ap_vs_b - np.where(b_shdest, 0, b_shbonus) - b_TS_mod
            b_rip_cas, _ = _roll_saves_batch(rng, N, b_sv_rip, a_rip, np.zeros(N, np.int32),
                                             np.zeros(N, np.bool_), b_parry_eff, b_regen_eff, b_reroll,
                                             atk_unstoppable=a_unstop, def_riposte=np.zeros(N, np.bool_))

        # recompute A for b_first
        recompute_a = b_first_mask
        if recompute_a.any():
            a_front_after = np.maximum(0, a_front - a_cas)
            a_front_refill = np.minimum(vc.FRONT_CAP, a_front_after + a_res)
            a_eff_front = np.where(recompute_a, a_front_refill, a_front)
            na_strk, na_sh, na_destroys = _roll_strikes_batch(rng, N, a_tt, a_eff_front, a_shat, a_clv, a_dstr,
                                                              b_hasshield, b_shdest, b_shimm)
            a_alive_back = (a_front_after + a_res) > 0
            na_fights = recompute_a & a_alive_back
            a_strk = np.where(recompute_a, np.where(na_fights, na_strk, 0), a_strk)
            a_sh = np.where(recompute_a, np.where(na_fights, na_sh, 0), a_sh)
            a_destroys = np.where(recompute_a, na_destroys & na_fights, a_destroys)
            nb_cas, nb_rip = _roll_saves_batch(rng, N, b_sv, a_strk, a_sh, a_poison, b_parry_eff, b_regen_eff, b_reroll,
                                               atk_unstoppable=a_unstop, def_riposte=b_riposte_eff)
            nb_cas = np.minimum(nb_cas, b_front)
            b_cas = np.where(recompute_a, nb_cas, b_cas)
            b_shdest = b_shdest | (a_destroys & recompute_a)
            # recompute B's riposte onto A for the b_first branch
            if b_riposte_eff.any():
                a_sv_rip2 = a_armor - b_ap_vs_a - np.where(a_shdest, 0, a_shbonus) - a_TS_mod
                na_rip_cas, _ = _roll_saves_batch(rng, N, a_sv_rip2, nb_rip, np.zeros(N, np.int32),
                                                  np.zeros(N, np.bool_), a_parry_eff, a_regen_eff, a_reroll,
                                                  atk_unstoppable=b_unstop, def_riposte=np.zeros(N, np.bool_))
                a_rip_cas = np.where(recompute_a, na_rip_cas, a_rip_cas)
        a_shdest = a_shdest | b_destroys

        # Fold riposte counter-damage into each side's casualties (capped by remaining front line).
        # a_rip_cas = damage B's ripostes dealt to A; b_rip_cas = damage A's ripostes dealt to B.
        a_cas = np.minimum(a_cas + a_rip_cas, a_front)
        b_cas = np.minimum(b_cas + b_rip_cas, b_front)

        a_pre = a_size.copy(); b_pre = b_size.copy()
        a_size = np.maximum(0, a_size - a_cas); b_size = np.maximum(0, b_size - b_cas)
        skirm_count = skirm_count + active.astype(np.int64)
        a_clost = a_pre - a_size; b_clost = b_pre - b_size
        a_kill += a_clost; b_kill += b_clost
        a_nd = (a_size <= 0) & (a_cause == 0) & active; b_nd = (b_size <= 0) & (b_cause == 0) & active
        a_cause = np.where(a_nd, 1, a_cause).astype(np.int8); b_cause = np.where(b_nd, 1, b_cause).astype(np.int8)
        a_scas = a_clost.copy(); b_scas = b_clost.copy()

        # endurance / fatigue
        a_drilled = tflag(Pa, skl, "Drilled"); b_drilled = tflag(Pb, skl, "Drilled")
        no_combat_free = no_combat_this & (~no_combat_endurance_pair)
        a_lose = active & (~(a_drilled & first)) & (a_size > 0) & (~no_combat_free)
        b_lose = active & (~(b_drilled & first)) & (b_size > 0) & (~no_combat_free)
        a_afat = a_fat > 0; b_afat = b_fat > 0
        a_lose_act = a_lose & (~a_afat); b_lose_act = b_lose & (~b_afat)
        a_end = a_end - a_lose_act.astype(np.int64); b_end = b_end - b_lose_act.astype(np.int64)
        # Token accrual deferred to AFTER the shaking test/rout (shake test fires at pre-token
        # target on the skirmish endurance hits 0). See token block below.

        # shaking (every exhausted skirmish, field cap 20). Each fatigue token = -1 to shake,
        # i.e. +1 to the per-run shake TARGET = base shaking + current fat (pre-token).
        a_fieldsz = np.minimum(vc.SHAKE_CAP, a_size); b_fieldsz = np.minimum(vc.SHAKE_CAP, b_size)
        a_exh = (a_end <= 0) & (a_size > 0); b_exh = (b_end <= 0) & (b_size > 0)
        a_sh_target = a_shaking + a_fat - a_shake_bonus; b_sh_target = b_shaking + b_fat - b_shake_bonus   # per-run (N,); Abbey lowers it
        a_unsh_eff = a_unshak | tflag(Pa, skl, "Unshakable")
        b_unsh_eff = b_unshak | tflag(Pb, skl, "Unshakable")
        a_can_test = a_exh & (~a_unsh_eff) & (~ending) & active
        b_can_test = b_exh & (~b_unsh_eff) & (~ending) & active
        # Only roll the dice where the target is still makeable (<=6); 7+ becomes a Rout below.
        a_shmask = a_can_test & (a_sh_target <= 6)
        b_shmask = b_can_test & (b_sh_target <= 6)
        a_scas2 = _shake_batch(rng, N, a_fieldsz, a_sh_target, a_shmask)
        b_scas2 = _shake_batch(rng, N, b_fieldsz, b_sh_target, b_shmask)
        a_pre2 = a_size.copy(); b_pre2 = b_size.copy()
        a_size = np.maximum(0, a_size - a_scas2); b_size = np.maximum(0, b_size - b_scas2)
        a_slost = a_pre2 - a_size; b_slost = b_pre2 - b_size
        a_shake += a_slost; b_shake += b_slost
        a_nds = (a_size <= 0) & (a_cause == 0) & active; b_nds = (b_size <= 0) & (b_cause == 0) & active
        a_cause = np.where(a_nds, 2, a_cause).astype(np.int8); b_cause = np.where(b_nds, 2, b_cause).astype(np.int8)

        # === WAVER TEST (Trigger 2) — separate from the exhaustion Shaken test ===
        # >5 COMBAT casualties this skirmish (net of this skirmish's heal) → an extra morale test at
        # the side's shake target. Combat-only count, heal-offset. Tracked in its own waver accumulator
        # and cause code (4). Asymmetric: the side losing the exchange breaks first.
        # Exemption: Steadfast = Immune Waver (Unshakable does NOT exempt — Immune Shaken only).
        a_steadfast = tile(np.array([("Steadfast" in t) for t in (Pa["tags_first"] if first else Pa["tags_normal"])], dtype=bool))
        b_steadfast = tile(np.array([("Steadfast" in t) for t in (Pb["tags_first"] if first else Pb["tags_normal"])], dtype=bool))
        a_netc = np.maximum(0, a_clost - a_heal); b_netc = np.maximum(0, b_clost - b_heal)
        a_wv = (a_netc > 5) & (a_size > 0) & (~a_steadfast) & (~ending) & active
        b_wv = (b_netc > 5) & (b_size > 0) & (~b_steadfast) & (~ending) & active
        a_wvmask = a_wv & (a_sh_target <= 6); b_wvmask = b_wv & (b_sh_target <= 6)
        a_wvfield = np.minimum(vc.SHAKE_CAP, a_size); b_wvfield = np.minimum(vc.SHAKE_CAP, b_size)
        a_wvcas = _shake_batch(rng, N, a_wvfield, a_sh_target, a_wvmask)
        b_wvcas = _shake_batch(rng, N, b_wvfield, b_sh_target, b_wvmask)
        a_prewv = a_size.copy(); b_prewv = b_size.copy()
        a_size = np.maximum(0, a_size - a_wvcas); b_size = np.maximum(0, b_size - b_wvcas)
        a_wvlost = a_prewv - a_size; b_wvlost = b_prewv - b_size
        a_waver += a_wvlost; b_waver += b_wvlost
        a_ndw = (a_size <= 0) & (a_cause == 0) & active & (a_wvlost > 0); b_ndw = (b_size <= 0) & (b_cause == 0) & active & (b_wvlost > 0)
        a_cause = np.where(a_ndw, 4, a_cause).astype(np.int8); b_cause = np.where(b_ndw, 4, b_cause).astype(np.int8)
        # Waver-rout flags (folded into the rout block below)
        a_wv_rout = a_wv & (a_sh_target >= 7); b_wv_rout = b_wv & (b_sh_target >= 7)
        # Heal next skirmish reads COMBAT-only casualties (shake/waver/rout can't be healed).
        a_prev_combat = a_clost.copy(); b_prev_combat = b_clost.copy()
        a_prev_cas = a_scas + a_slost; b_prev_cas = b_scas + b_slost

        # ROUT: shake target modified to 7+ (test cannot succeed → whole army flees).
        # NOTHING prevents Rout. Unshakable skips the Shaken TEST and Steadfast skips the Waver
        # TEST, but both shake TARGETS still climb with fatigue tokens — both rout at 7+.
        a_routs = active & ((a_exh & (a_sh_target >= 7)) | a_wv_rout) & (a_size > 0) & (~ending)
        b_routs = active & ((b_exh & (b_sh_target >= 7)) | b_wv_rout) & (b_size > 0) & (~ending)
        a_rout += np.where(a_routs, a_size, 0); b_rout += np.where(b_routs, b_size, 0)
        a_size = np.where(a_routs, 0, a_size); b_size = np.where(b_routs, 0, b_size)
        a_ndr = a_routs & (a_cause == 0); b_ndr = b_routs & (b_cause == 0)
        a_cause = np.where(a_ndr, 3, a_cause).astype(np.int8); b_cause = np.where(b_ndr, 3, b_cause).astype(np.int8)

        # Fatigue token accrual (AFTER shake/rout): +1 per exhausted skirmish. Raises next
        # skirmish's to-hit (-1, capped 6+) and shake (-1). Cap to avoid overflow.
        a_fat = np.minimum(a_fat + (a_exh & active & (~ending)).astype(np.int64), 99)
        b_fat = np.minimum(b_fat + (b_exh & active & (~ending)).astype(np.int64), 99)

        active = active & (~ending)

    # outcomes
    a_dead = a_size <= 0; b_dead = b_size <= 0
    a_w = (~a_dead) & b_dead; b_w = a_dead & (~b_dead)
    mw = a_dead & b_dead; ind = (~a_dead) & (~b_dead)
    # scatter per-pair
    def per_pair_sum(x): return np.add.reduceat(x, np.arange(0, N, n_runs))
    res = {
        "a_wins": per_pair_sum(a_w.astype(np.int64)),
        "b_wins": per_pair_sum(b_w.astype(np.int64)),
        "mut_wipe": per_pair_sum(mw.astype(np.int64)),
        "indecisive": per_pair_sum(ind.astype(np.int64)),
        "avg_a_rem": per_pair_sum(a_size) / n_runs,
        "avg_b_rem": per_pair_sum(b_size) / n_runs,
        "avg_a_killed_combat": per_pair_sum(a_kill) / n_runs,
        "avg_b_killed_combat": per_pair_sum(b_kill) / n_runs,
        "avg_a_killed_shake": per_pair_sum(a_shake) / n_runs,
        "avg_b_killed_shake": per_pair_sum(b_shake) / n_runs,
        "avg_a_killed_waver": per_pair_sum(a_waver) / n_runs,
        "avg_b_killed_waver": per_pair_sum(b_waver) / n_runs,
        "avg_a_killed_rout": per_pair_sum(a_rout) / n_runs,
        "avg_b_killed_rout": per_pair_sum(b_rout) / n_runs,
        "avg_skirm": per_pair_sum(skirm_count) / n_runs,
        # Fraction of runs in which each side's shield got destroyed (DEFENDER perspective:
        # a_shield_destroyed_rate = how often A's own shield was destroyed by B's Destroy Shield).
        "a_shield_destroyed_rate": per_pair_sum(a_shdest.astype(np.int64)) / n_runs,
        "b_shield_destroyed_rate": per_pair_sum(b_shdest.astype(np.int64)) / n_runs,
        # Wipe-cause counts per matchup: how each side's destruction happened across runs.
        # cause codes: 1=combat, 2=shake, 3=rout. (Counts, summed over the n_runs of each pair.)
        "a_wipe_combat": per_pair_sum((a_cause == 1).astype(np.int64)),
        "a_wipe_shake":  per_pair_sum((a_cause == 2).astype(np.int64)),
        "a_wipe_waver":  per_pair_sum((a_cause == 4).astype(np.int64)),
        "a_wipe_rout":   per_pair_sum((a_cause == 3).astype(np.int64)),
        "b_wipe_combat": per_pair_sum((b_cause == 1).astype(np.int64)),
        "b_wipe_shake":  per_pair_sum((b_cause == 2).astype(np.int64)),
        "b_wipe_waver":  per_pair_sum((b_cause == 4).astype(np.int64)),
        "b_wipe_rout":   per_pair_sum((b_cause == 3).astype(np.int64)),
    }
    if return_first_tactics:
        # Per-run (length-N) arrays for empirical tactic-matrix accumulation.
        res["a_tac0"] = a_tac0
        res["b_tac0"] = b_tac0
        res["a_w_run"] = a_w.astype(np.int8)
        res["b_w_run"] = b_w.astype(np.int8)
    return res


def _shake_batch(rng, n, field_size, shaking_value, mask):
    """Batched shaking: per-slot shaking_value (n,) and field_size (n,)."""
    max_field = int(field_size.max()) if field_size.any() else 0
    if max_field == 0 or not mask.any():
        return np.zeros(n, dtype=np.int32)
    rolls = rng.integers(1, 7, size=(n, max_field), dtype=np.int8)
    if _HAVE_NUMBA:
        return _shake_kernel(field_size.astype(np.int64),
                             shaking_value.astype(np.int64), mask, rolls)
    field_idx = np.arange(max_field)[None, :]
    in_field = field_idx < field_size[:, None]
    flees = (rolls < shaking_value[:, None]) & in_field & mask[:, None]
    return flees.sum(axis=1).astype(np.int32)


def _poison_batch(P_atk, P_def, skl, n_runs):
    """Attacker's effective poison per-slot, tiled to N: Poison in attacker's tags
    AND not Immune Poison in the defender's tags."""
    atk = P_atk["tags_first"] if skl == "first" else P_atk["tags_normal"]
    dfn = P_def["tags_first"] if skl == "first" else P_def["tags_normal"]
    per_pair = np.array([("Poison" in atk[i]) and ("Immune Poison" not in dfn[i])
                         for i in range(len(atk))], dtype=bool)
    return np.repeat(per_pair, n_runs)


# ──────────────────────────────────────────────────────────────────────────
# Playstyle-mode batching: per-slot playstyle weights + Outrider counter-pick.
# ──────────────────────────────────────────────────────────────────────────

def _batched_weights(playstyle_per_slot, state_full, n_slots, rng):
    """Return an (n_slots, 7) tactic-weight matrix where each slot uses its own playstyle.
    Groups slots by playstyle name and calls resolve_playstyle_weights on each subgroup
    with a sliced state, then scatters back. Adaptive playstyles are already vectorized
    over the run axis, so a subgroup call returns (len(subgroup), 7) correctly.
    """
    from playstyles import resolve_playstyle_weights
    out = np.zeros((n_slots, 7), dtype=np.float64)
    unique_ps = set(playstyle_per_slot.tolist()) if hasattr(playstyle_per_slot, "tolist") else set(playstyle_per_slot)
    for ps_name in unique_ps:
        idx = np.where(playstyle_per_slot == ps_name)[0]
        if idx.size == 0:
            continue
        sub_state = {k: v[idx] for k, v in state_full.items()}
        w = resolve_playstyle_weights(ps_name, sub_state, idx.size)
        out[idx] = w
    return out


def _sample_from_weights(weights, rng):
    """Vectorized categorical sample from an (n,7) weight matrix → (n,) tactic indices."""
    cdf = np.cumsum(weights, axis=1)
    cdf = cdf / cdf[:, -1:]                      # normalize
    u = rng.random(weights.shape[0])
    return (u[:, None] < cdf).argmax(axis=1).astype(np.int64)


def _precompute_outrider_tables(pairs, Pa, Pb):
    """For each pair, if a side has Outrider, precompute its (7,) best-response table.
    Returns (a_has_out, b_has_out, a_ct, b_ct, a_mode, b_mode) — per-pair arrays/lists.
    a_ct[i] is a length-7 int array (best response to each opp tactic) or None.
    """
    from vectorized_combat import _best_response_table, get_tactic_tables, StaticArmy
    tab = get_tactic_tables()
    npairs = len(pairs)
    def omode(tags):
        if "Outrider: first_two" in tags: return "first_two"
        if "Outrider: every" in tags: return "every"
        if "Outrider: first" in tags: return "first"
        if "Outrider: once" in tags: return "once"
        return None
    a_mode = []; b_mode = []
    a_ct = [None]*npairs; b_ct = [None]*npairs
    sa_list = Pa["_armies"]; sb_list = Pb["_armies"]
    for i,(la,lb) in enumerate(pairs):
        am = omode(la.extra_tags); bm = omode(lb.extra_tags)
        if am and bm:           # both have it → engine disables both
            am = bm = None
        a_mode.append(am); b_mode.append(bm)
        if am is not None:
            a_ct[i] = _best_response_table(tab, sa_list[i], sb_list[i], me_first=True, opp_first=True)
        if bm is not None:
            tab_b = {"a_I":tab["b_I"].T,"a_TH":tab["b_TH"].T,"b_I":tab["a_I"].T,"b_TH":tab["a_TH"].T,
                     "end":tab["end"].T,"no_combat":tab["no_combat"].T}
            b_ct[i] = _best_response_table(tab_b, sb_list[i], sa_list[i], me_first=True, opp_first=True)
    return a_mode, b_mode, a_ct, b_ct


def _outrider_fires(mode_per_pair, sk, n_runs):
    """Per-slot boolean: does Outrider fire this skirmish? mode_per_pair is a list of
    per-pair mode strings (None/'first'/'first_two'/'every')."""
    first = (sk == 0)
    per_pair = np.array([
        (m == "every") or (m in ("first", "once") and first) or (m == "first_two" and sk <= 1)
        if m is not None else False
        for m in mode_per_pair], dtype=bool)
    return np.repeat(per_pair, n_runs)


def run_batch_playstyle(pairs, n_runs=50, seed=2026, max_skirmishes=40):
    """Playstyle mode: each slot uses its loadout's assigned playstyle. Thin wrapper."""
    return run_batch_random(pairs, n_runs=n_runs, seed=seed,
                            max_skirmishes=max_skirmishes, mode="playstyle")


# ──────────────────────────────────────────────────────────────────────────
# Batched tournament: round-robin in blocks, both modes, one master CSV.
# ──────────────────────────────────────────────────────────────────────────

def run_tournament_batched(pool, n_runs=50, output_dir=".", base_seed=2026,
                           modes=("random", "playstyle"), block_size=None, verbose=True,
                           slot_budget=250_000):
    """Full round-robin using the batched engine. Builds the list of valid (A,B) pairs,
    chunks into blocks, resolves each block in one batched call per mode, and streams rows to a
    single master matchups.csv with a `mode` column. Skips pairs sharing a unique monument.

    block_size is DERIVED from slot_budget (block_size = slot_budget // n_runs) so peak memory per
    block stays bounded regardless of n_runs — a fixed pair count would OOM at high run counts."""
    import csv, time
    from pathlib import Path
    from tournament_vec import _matchup_header, _unique_conflict
    if block_size is None:
        block_size = max(200, slot_budget // max(1, n_runs))
    out_dir = Path(output_dir); out_dir.mkdir(exist_ok=True)
    modes = list(modes)
    npool = len(pool)

    # Build valid pair index list (i,j); skip unique-monument conflicts for i!=j.
    pair_idx = []
    for i in range(npool):
        for j in range(npool):
            if i != j and _unique_conflict(pool[i], pool[j]):
                continue
            pair_idx.append((i, j))
    total = len(pair_idx)
    if verbose:
        print(f"Batched tournament: {npool}x{npool} → {total:,} valid matchups × {n_runs} runs × {len(modes)} modes")
        print(f"  = {total*n_runs*len(modes):,} battles, block_size={block_size}")

    start = time.time()
    matchup_path = out_dir / "matchups.csv"
    f = open(matchup_path, "w", newline=""); w = csv.writer(f); w.writerow(_matchup_header())

    # Per-loadout, per-mode summary accumulators (mirror tournament_vec's summary CSVs so the
    # notebook's downstream cells that read summary_{mode}.csv work unchanged).
    name_to_ld = {ld.name: ld for ld in pool}
    summary = {m: {ld.name: dict(loadout=ld, wins=0, losses=0, mut_wipe=0, indecisive=0,
                                 rem_self=0.0, rem_opp=0.0, n_battles=0) for ld in pool}
               for m in modes}

    done = 0
    for bstart in range(0, total, block_size):
        block = pair_idx[bstart:bstart + block_size]
        pairs = [(pool[i], pool[j]) for (i, j) in block]
        for m_idx, mode in enumerate(modes):
            seed = base_seed + (bstart * len(modes)) + m_idx
            res = run_batch_random(pairs, n_runs=n_runs, seed=seed, mode=mode)
            _write_block_rows(w, pairs, res, mode, n_runs)
            # Accumulate A-side summary for each pair (matches _update_summary; A-side only).
            sm = summary[mode]
            for k, (la, lb) in enumerate(pairs):
                s = sm[la.name]
                s["wins"] += int(res["a_wins"][k]); s["losses"] += int(res["b_wins"][k])
                s["mut_wipe"] += int(res["mut_wipe"][k]); s["indecisive"] += int(res["indecisive"][k])
                s["rem_self"] += float(res["avg_a_rem"][k]); s["rem_opp"] += float(res["avg_b_rem"][k])
                s["n_battles"] += n_runs
        done += len(block)
        if verbose:
            el = time.time() - start
            eta = el / done * (total - done) if done else 0
            print(f"  [{done:,}/{total:,}] elapsed {el:.0f}s eta {eta:.0f}s", flush=True)
    f.close()
    # Write per-mode summaries + a primary summary.csv alias (first mode), like tournament_vec.
    for m in modes:
        _write_batch_summary(summary[m], out_dir / f"summary_{m}.csv", n_runs)
    _write_batch_summary(summary[modes[0]], out_dir / "summary.csv", n_runs)
    if verbose:
        el = time.time() - start
        print(f"Done. {total*n_runs*len(modes):,} battles in {el:.0f}s ({total*n_runs*len(modes)/el:,.0f}/s)")
        print(f"  Master CSV: {matchup_path}")
    return matchup_path


def _block_to_table(pairs, res, mode, n_runs):
    """Build a pyarrow Table for one block's matchup rows (columnar — far faster than
    per-row csv.writerow and writes straight to a Parquet row group)."""
    import pyarrow as pa
    from tournament_vec import _matchup_header
    cols = _matchup_header()
    K = len(pairs)
    def col(name): return res[name]
    data = {
        "a_name": [la.name for la, _ in pairs], "b_name": [lb.name for _, lb in pairs],
        "mode": [mode] * K,
        "a_wins": col("a_wins").astype("int32"), "b_wins": col("b_wins").astype("int32"),
        "mut_wipe": col("mut_wipe").astype("int32"), "indecisive": col("indecisive").astype("int32"),
        "avg_skirm": col("avg_skirm").astype("float32"),
        "avg_a_rem": col("avg_a_rem").astype("float32"), "avg_b_rem": col("avg_b_rem").astype("float32"),
        "avg_a_killed_combat": col("avg_a_killed_combat").astype("float32"),
        "avg_a_killed_shake": col("avg_a_killed_shake").astype("float32"),
        "avg_a_killed_waver": col("avg_a_killed_waver").astype("float32"),
        "avg_a_killed_rout": col("avg_a_killed_rout").astype("float32"),
        "avg_b_killed_combat": col("avg_b_killed_combat").astype("float32"),
        "avg_b_killed_shake": col("avg_b_killed_shake").astype("float32"),
        "avg_b_killed_waver": col("avg_b_killed_waver").astype("float32"),
        "avg_b_killed_rout": col("avg_b_killed_rout").astype("float32"),
        "a_wipe_combat": col("a_wipe_combat").astype("int32"), "a_wipe_shake": col("a_wipe_shake").astype("int32"), "a_wipe_waver": col("a_wipe_waver").astype("int32"), "a_wipe_rout": col("a_wipe_rout").astype("int32"),
        "b_wipe_combat": col("b_wipe_combat").astype("int32"), "b_wipe_shake": col("b_wipe_shake").astype("int32"), "b_wipe_waver": col("b_wipe_waver").astype("int32"), "b_wipe_rout": col("b_wipe_rout").astype("int32"),
        "a_shield_destroyed_rate": col("a_shield_destroyed_rate").astype("float32"),
        "b_shield_destroyed_rate": col("b_shield_destroyed_rate").astype("float32"),
        "a_retinue": [la.retinue for la,_ in pairs], "a_weapon": [la.weapon or "" for la,_ in pairs],
        "a_shield": [la.shield or "" for la,_ in pairs], "a_armor": [la.armor for la,_ in pairs],
        "a_ranged": [la.ranged or "" for la,_ in pairs], "a_tiltyard": [la.has_tiltyard for la,_ in pairs],
        "a_size": [la.size for la,_ in pairs], "a_tags": [",".join(la.extra_tags) for la,_ in pairs],
        "a_playstyle": [la.playstyle or "Random" for la,_ in pairs],
        "b_retinue": [lb.retinue for _,lb in pairs], "b_weapon": [lb.weapon or "" for _,lb in pairs],
        "b_shield": [lb.shield or "" for _,lb in pairs], "b_armor": [lb.armor for _,lb in pairs],
        "b_ranged": [lb.ranged or "" for _,lb in pairs], "b_tiltyard": [lb.has_tiltyard for _,lb in pairs],
        "b_size": [lb.size for _,lb in pairs], "b_tags": [",".join(lb.extra_tags) for _,lb in pairs],
        "b_playstyle": [lb.playstyle or "Random" for _,lb in pairs],
        "a_military_pursuit_count": [getattr(la,"military_pursuit_count",0) for la,_ in pairs],
        "a_domain_count": [getattr(la,"domain_count",0) for la,_ in pairs],
        "a_pursuits": ["|".join(sorted(la.pursuits)) for la,_ in pairs],
        "b_military_pursuit_count": [getattr(lb,"military_pursuit_count",0) for _,lb in pairs],
        "b_domain_count": [getattr(lb,"domain_count",0) for _,lb in pairs],
        "b_pursuits": ["|".join(sorted(lb.pursuits)) for _,lb in pairs],
    }
    # Pin an explicit schema so a column that happens to be all-None in some block (e.g. a block of
    # weaponless builds) doesn't get inferred as `null` and clash with the file's locked schema. The
    # `or ""` normalizations above prevent the common case; this makes it robust for any string column.
    _string_cols = {
        "a_name", "b_name", "mode", "a_retinue", "a_weapon", "a_shield", "a_armor", "a_ranged",
        "a_tags", "a_playstyle", "a_pursuits", "b_retinue", "b_weapon", "b_shield", "b_armor",
        "b_ranged", "b_tags", "b_playstyle", "b_pursuits",
    }
    _int32_cols = {"a_wins", "b_wins", "mut_wipe", "indecisive", "a_wipe_combat", "a_wipe_shake",
                   "a_wipe_waver", "a_wipe_rout", "b_wipe_combat", "b_wipe_shake", "b_wipe_waver", "b_wipe_rout"}
    _float_cols = {"avg_skirm", "avg_a_rem", "avg_b_rem", "avg_a_killed_combat", "avg_a_killed_shake",
                   "avg_a_killed_waver", "avg_a_killed_rout", "avg_b_killed_combat", "avg_b_killed_shake",
                   "avg_b_killed_waver", "avg_b_killed_rout", "a_shield_destroyed_rate", "b_shield_destroyed_rate"}
    _int64_cols = {"a_size", "b_size", "a_military_pursuit_count", "a_domain_count",
                   "b_military_pursuit_count", "b_domain_count"}
    _bool_cols = {"a_tiltyard", "b_tiltyard"}
    def _ptype(c):
        if c in _string_cols: return pa.string()
        if c in _int32_cols:  return pa.int32()
        if c in _float_cols:  return pa.float32()
        if c in _int64_cols:  return pa.int64()
        if c in _bool_cols:   return pa.bool_()
        return None  # let pyarrow infer anything unlisted
    schema = pa.schema([(c, _ptype(c)) for c in cols]) if all(_ptype(c) is not None for c in cols) else None
    if schema is not None:
        return pa.table({c: data[c] for c in cols}, schema=schema)
    return pa.table({c: data[c] for c in cols})


def _write_block_rows(writer, pairs, res, mode, n_runs):
    """Write one matchup row per pair for this mode, matching tournament_vec schema."""
    for k, (la, lb) in enumerate(pairs):
        aw = int(res["a_wins"][k]); bw = int(res["b_wins"][k])
        mw = int(res["mut_wipe"][k]); ind = int(res["indecisive"][k])
        a_mpc = getattr(la, "military_pursuit_count", 0); a_dc = getattr(la, "domain_count", 0)
        b_mpc = getattr(lb, "military_pursuit_count", 0); b_dc = getattr(lb, "domain_count", 0)
        writer.writerow([
            la.name, lb.name, mode,
            aw, bw, mw, ind,
            f"{res['avg_skirm'][k]:.2f}", f"{res['avg_a_rem'][k]:.2f}", f"{res['avg_b_rem'][k]:.2f}",
            f"{res['avg_a_killed_combat'][k]:.2f}", f"{res['avg_a_killed_shake'][k]:.2f}", f"{res['avg_a_killed_waver'][k]:.2f}", f"{res['avg_a_killed_rout'][k]:.2f}",
            f"{res['avg_b_killed_combat'][k]:.2f}", f"{res['avg_b_killed_shake'][k]:.2f}", f"{res['avg_b_killed_waver'][k]:.2f}", f"{res['avg_b_killed_rout'][k]:.2f}",
            res['a_wipe_combat'][k], res['a_wipe_shake'][k], res['a_wipe_waver'][k], res['a_wipe_rout'][k],
            res['b_wipe_combat'][k], res['b_wipe_shake'][k], res['b_wipe_waver'][k], res['b_wipe_rout'][k],
            f"{res['a_shield_destroyed_rate'][k]:.4f}", f"{res['b_shield_destroyed_rate'][k]:.4f}",
            la.retinue, la.weapon, la.shield or "", la.armor, la.ranged or "", la.has_tiltyard, la.size, ",".join(la.extra_tags), la.playstyle or "Random",
            lb.retinue, lb.weapon, lb.shield or "", lb.armor, lb.ranged or "", lb.has_tiltyard, lb.size, ",".join(lb.extra_tags), lb.playstyle or "Random",
            a_mpc, a_dc, "|".join(sorted(la.pursuits)),
            b_mpc, b_dc, "|".join(sorted(lb.pursuits)),
        ])


def _write_batch_summary(summary, summary_path, n_runs):
    """Write a per-loadout summary CSV matching tournament_vec._write_summary's schema, so the
    notebook's summary_{mode}.csv consumers work unchanged."""
    import csv as _csv
    with open(summary_path, "w", newline="") as f:
        writer = _csv.writer(f)
        writer.writerow([
            "name", "retinue", "weapon", "shield", "armor", "ranged", "tiltyard", "size", "tags", "playstyle",
            "wins", "losses", "mut_wipe", "indecisive", "n_battles",
            "win_rate", "loss_rate", "decisive_rate", "decisive_win_rate",
            "avg_self_survivors", "avg_opp_survivors", "kill_efficiency",
            "upkeep_per_retinue", "army_upkeep", "wins_per_1000_upkeep",
            "military_pursuit_count", "domain_count", "pursuits",
        ])
        for name, s in summary.items():
            ld = s["loadout"]
            n = max(1, s["n_battles"])
            win_rate = s["wins"] / n
            loss_rate = s["losses"] / n
            decisive_rate = (s["wins"] + s["losses"] + s["mut_wipe"]) / n
            decisive_total = s["wins"] + s["losses"]
            decisive_win_rate = (s["wins"] / decisive_total) if decisive_total > 0 else 0.0
            n_opps = (n // n_runs) or 1
            avg_self_rem = s["rem_self"] / n_opps
            avg_opp_rem = s["rem_opp"] / n_opps
            kill_eff = avg_self_rem - avg_opp_rem
            army_upkeep = ld.upkeep_per_retinue   # cost is the TOTAL army cost, not per-soldier
            wins_per_1k = s["wins"] / (army_upkeep / 1000) if army_upkeep else 0
            mpc = getattr(ld, "military_pursuit_count", 0)
            dc = getattr(ld, "domain_count", 0)
            pursuits = getattr(ld, "pursuits", frozenset())
            writer.writerow([
                name, ld.retinue, ld.weapon, ld.shield or "", ld.armor, ld.ranged or "", ld.has_tiltyard, ld.size, ",".join(ld.extra_tags), ld.playstyle or "Random",
                s["wins"], s["losses"], s["mut_wipe"], s["indecisive"], s["n_battles"],
                f"{win_rate:.4f}", f"{loss_rate:.4f}", f"{decisive_rate:.4f}", f"{decisive_win_rate:.4f}",
                f"{avg_self_rem:.2f}", f"{avg_opp_rem:.2f}", f"{kill_eff:.2f}",
                ld.upkeep_per_retinue, army_upkeep, f"{wins_per_1k:.2f}",
                mpc, dc, "|".join(sorted(pursuits)),
            ])


def _warm_numba_kernels():
    """Compile (or load) the numba kernels ONCE in the calling process by running each on tiny
    inputs. Populates the on-disk cache so freshly-spawned workers load the compiled artifact
    instead of all recompiling at once (which, after a source edit, spikes memory — each worker
    also imports scipy via numba's registry load — and can OOM the pool at startup). No-op if numba
    isn't available."""
    if not _HAVE_NUMBA:
        return
    try:
        import numpy as _np
        rng = _np.random.default_rng(0)
        n = 4
        # _strikes_kernel
        tt = _np.full(n, 4, _np.int64); af = _np.zeros(n, _np.bool_); ap = _np.zeros(n, _np.bool_)
        fl = _np.full(n, 3, _np.int64); rolls = rng.integers(1, 7, size=(n, 20), dtype=_np.int8)
        _strikes_kernel(tt, af, ap, fl, rolls)
        # _saves_kernel
        ns = _np.full(n, 3, _np.int64); shat = _np.zeros(n, _np.int64)
        sc = _np.full(n, 4, _np.int64); pois = _np.zeros(n, _np.bool_)
        srolls = rng.integers(1, 7, size=(n, 5), dtype=_np.int8)
        pm = _np.zeros(n, _np.bool_); prolls = _np.zeros((n, 5), _np.int8)
        rt = _np.zeros(n, _np.int64); rrolls = _np.zeros((n, 5), _np.int8)
        rr = _np.zeros(n, _np.bool_); rerolls = _np.zeros((n, 5), _np.int8)
        pthr = _np.full(n, 5, _np.int64); ripm = _np.zeros(n, _np.bool_)
        sthr = _np.full(n, 7, _np.int64)   # shatter_parry_thr: 7 = unparryable (matches real calls)
        _saves_kernel(ns, shat, sc, af, ap, pois, srolls, pm, prolls, rt, rrolls, rr, rerolls, sthr, pthr, ripm)
        # _shake_kernel
        fs = _np.full(n, 3, _np.int64); sv = _np.full(n, 3, _np.int64)
        mask = _np.ones(n, _np.bool_); krolls = rng.integers(1, 7, size=(n, 3), dtype=_np.int8)
        _shake_kernel(fs, sv, mask, krolls)
    except Exception as e:
        # Warming is an optimization; if anything about the signatures drifts, don't hard-fail —
        # workers will just compile on demand (the original behavior).
        print(f"  (numba warmup skipped: {e})", flush=True)


def _batch_block_worker(args):
    """Top-level worker (picklable for ProcessPoolExecutor on spawn/Windows). Resolves one block
    of pairs and returns the result dict. Seed is fixed by the block's position so results are
    identical regardless of how blocks are distributed across workers."""
    block_pairs, n_runs, seed, mode = args
    return run_batch_random(block_pairs, n_runs=n_runs, seed=seed, mode=mode,
                            return_first_tactics=True)


def auto_slot_budget(n_workers, bytes_per_slot=2000, safety=0.35, floor=40_000, cap=120_000):
    """Conservative per-block slot budget. Peak ~= slot_budget * bytes_per_slot * n_workers.
        budget = free_bytes * safety / (bytes_per_slot * n_workers)
    bytes_per_slot=2000 is DELIBERATELY pessimistic: earlier 220/700 estimates under-predicted and the
    pool kept OOMing on tiny allocations at 'safe' sizes, so the real transient footprint (numba temps,
    broadcasts, IPC pickling, heap fragmentation) is far higher than a naive array count. 2000 + 120k cap
    keeps blocks small enough that a 5x modelling error still fits. Finishing > a little speed.
    Uses min(available, total*0.4): 'available' can read high on Windows while big contiguous allocs
    still fail. psutil-missing -> blind 2 GB. Override with slot_budget=N / SLOT_BUDGET anytime."""
    have_psutil = False
    try:
        import psutil
        vm = psutil.virtual_memory()
        free = min(vm.available, int(vm.total * 0.40))
        have_psutil = True
    except Exception:
        free = 2 * 1024**3
    budget = int(free * safety / (bytes_per_slot * max(1, n_workers)))
    budget = max(floor, min(cap, budget))
    return budget, have_psutil


def run_mode_batched(pool, mode="random", n_runs=100, output_dir=".", suffix="",
                     base_seed=2026, block_size=None, verbose=True, n_workers=None,
                     slot_budget=None):
    """Run ONE mode (random or playstyle) over the full pool with the batched engine, writing
    the notebook's expected per-mode files:
        matchups{suffix}.csv, summary{suffix}.csv, tactic_matrix{suffix}.csv
    Also builds the empirical first-skirmish tactic matrix from the batched runs.

    n_workers: parallel processes for block resolution. None → max(1, cpu_count()-2). 1 → serial.
    Block seeds are keyed by block position, so the output is bit-identical for any n_workers.

    MEMORY: each block allocates N = block_size * n_runs rows; ~2*n_workers blocks are in flight.
    block_size is DERIVED from slot_budget so peak memory is bounded regardless of n_runs.
    slot_budget=None (default) AUTO-SIZES from free RAM (needs psutil; falls back SMALL/safe without
    it). Pass an int to fix it, or block_size to override. Bigger budget = faster, more memory."""
    import os, csv as _csv, numpy as _np, time as _time, gc as _gc
    from renown_combat import TACTICS as _TACTICS
    import tournament_vec as _tv
    from tournament_vec import _matchup_header
    if n_workers is None:
        n_workers = max(1, (os.cpu_count() or 2) - 2)
    # Auto-size the slot budget from free RAM unless caller fixed slot_budget or block_size.
    _auto_psutil = None
    if slot_budget is None and block_size is None:
        slot_budget, _auto_psutil = auto_slot_budget(n_workers)
    # Derive block_size so N = block_size * n_runs ≈ slot_budget (bounded peak memory per block).
    if block_size is None:
        block_size = max(200, slot_budget // max(1, n_runs))
    out = output_dir
    os.makedirs(out, exist_ok=True)
    pool = [ld._replace(playstyle=__import__("playstyles").assign_default_playstyle(ld))
            if (mode == "playstyle" and (ld.playstyle in (None, "Random"))) else ld for ld in pool]
    n_load = len(pool)
    pair_idx = [(i, j) for i in range(n_load) for j in range(n_load)
                if i != j and not _tv._unique_conflict(pool[i], pool[j])]
    total = len(pair_idx)
    if verbose:
        _peak_gb = (block_size * n_runs * 2000 * n_workers) / 1024**3
        print(f"[batch mode={mode}] {n_load} loadouts → {total:,} pairs × {n_runs} runs "
              f"| n_workers={n_workers}", flush=True)
        print(f"  slot_budget={slot_budget if slot_budget else 'fixed'} → block_size={block_size:,} pairs "
              f"({block_size*n_runs:,} slots/block); est. peak ≈ {_peak_gb:.1f} GB "
              f"({n_workers} blocks in flight)", flush=True)
        if _auto_psutil is False:
            print("  ⚠ psutil not found in THIS Python — used a blind 2 GB estimate. "
                  "(You may have psutil in a different interpreter.)", flush=True)

    summary = {ld.name: dict(loadout=ld, wins=0, losses=0, mut_wipe=0, indecisive=0,
                             rem_self=0.0, rem_opp=0.0, n_battles=0) for ld in pool}
    nT = len(_TACTICS)
    tac_cnt = _np.zeros((nT, nT), dtype=_np.int64)
    tac_aw = _np.zeros((nT, nT), dtype=_np.int64)
    tac_bw = _np.zeros((nT, nT), dtype=_np.int64)

    mpath_csv = os.path.join(out, f"matchups{suffix}.csv")
    mpath_pq = os.path.join(out, f"matchups{suffix}.parquet")
    # Prefer Parquet (~20x smaller, ~9x faster to load; analysis.load_tournament auto-detects
    # the .parquet sibling). Stream one row group per block so memory stays bounded.
    try:
        import pyarrow as _pa, pyarrow.parquet as _pq
        use_pq = True
    except Exception:
        use_pq = False
    pqw = {"w": None}
    w = None; f = None
    if not use_pq:
        f = open(mpath_csv, "w", newline=""); w = _csv.writer(f); w.writerow(_matchup_header())
    start = _time.time(); done = 0

    block_starts = list(range(0, total, block_size))

    def _consume(bstart, res):
        # write rows + accumulate summary & tactic matrix for one finished block
        nonlocal done
        block = pair_idx[bstart:bstart + block_size]
        pairs = [(pool[i], pool[j]) for (i, j) in block]
        if use_pq:
            tbl = _block_to_table(pairs, res, mode, n_runs)
            if pqw["w"] is None:
                pqw["w"] = _pq.ParquetWriter(mpath_pq, tbl.schema, compression="snappy")
            pqw["w"].write_table(tbl)
        else:
            _write_block_rows(w, pairs, res, mode, n_runs)
        for k, (la, lb) in enumerate(pairs):
            s = summary[la.name]
            s["wins"] += int(res["a_wins"][k]); s["losses"] += int(res["b_wins"][k])
            s["mut_wipe"] += int(res["mut_wipe"][k]); s["indecisive"] += int(res["indecisive"][k])
            s["rem_self"] += float(res["avg_a_rem"][k]); s["rem_opp"] += float(res["avg_b_rem"][k])
            s["n_battles"] += n_runs
        _np.add.at(tac_cnt, (res["a_tac0"], res["b_tac0"]), 1)
        _np.add.at(tac_aw, (res["a_tac0"], res["b_tac0"]), res["a_w_run"])
        _np.add.at(tac_bw, (res["a_tac0"], res["b_tac0"]), res["b_w_run"])
        done += len(block)
        if verbose:
            el = _time.time() - start; eta = el / done * (total - done) if done else 0
            print(f"  [{done:,}/{total:,}] {el:.0f}s eta {eta:.0f}s", flush=True)

    if n_workers <= 1:
        for bstart in block_starts:
            block = pair_idx[bstart:bstart + block_size]
            pairs = [(pool[i], pool[j]) for (i, j) in block]
            res = run_batch_random(pairs, n_runs=n_runs, seed=base_seed + bstart, mode=mode,
                                   return_first_tactics=True)
            _consume(bstart, res)
    else:
        from concurrent.futures import ProcessPoolExecutor, FIRST_COMPLETED, wait
        # Warm the numba kernels ONCE in the parent before spawning workers. After an edit the
        # cached compiled artifacts are stale, so otherwise all N workers cold-compile the kernels
        # AND trigger numba's registry load (which imports scipy) simultaneously at startup — a
        # memory spike big enough to OOM the whole pool on launch. Running each kernel once here
        # compiles + writes the disk cache so workers just load it.
        _warm_numba_kernels()
        # Bounded submission window: keep at most n_workers blocks in flight. (Was 2*n_workers,
        # which doubled peak memory — 28 live result dicts + 28 pending pair-lists on a 14-core box.)
        max_inflight = max(2, n_workers)
        ex = ProcessPoolExecutor(max_workers=n_workers)
        try:
            it = iter(block_starts)
            fut_to_bstart = {}
            # prime the window
            for _ in range(max_inflight):
                try:
                    bstart = next(it)
                except StopIteration:
                    break
                block = pair_idx[bstart:bstart + block_size]
                pairs = [(pool[i], pool[j]) for (i, j) in block]
                fut = ex.submit(_batch_block_worker, (pairs, n_runs, base_seed + bstart, mode))
                fut_to_bstart[fut] = bstart
            while fut_to_bstart:
                done_set, _ = wait(list(fut_to_bstart), return_when=FIRST_COMPLETED)
                for fut in done_set:
                    bstart = fut_to_bstart.pop(fut)
                    res = fut.result()
                    _consume(bstart, res)
                    # Free the block's result arrays IMMEDIATELY. ProcessPoolExecutor pins a
                    # future's result inside the Future object until the future is dropped; on a
                    # multi-million-pair run that retention (plus heap fragmentation from hundreds
                    # of multi-MB result dicts) slowly exhausts RAM and a later tiny allocation
                    # fails. Dropping res + the future here keeps the parent's footprint flat.
                    del res
                    del fut
                    # backfill the window with the next block
                    try:
                        nb = next(it)
                    except StopIteration:
                        continue
                    block = pair_idx[nb:nb + block_size]
                    pairs = [(pool[i], pool[j]) for (i, j) in block]
                    f2 = ex.submit(_batch_block_worker, (pairs, n_runs, base_seed + nb, mode))
                    fut_to_bstart[f2] = nb
                del done_set
                _gc.collect()
        finally:
            # Force the worker processes down NOW so Windows reclaims their committed (virtual)
            # memory immediately — on success OR on error. The plain `with` block calls
            # shutdown(wait=True) but doesn't kill_workers; on Windows, numba/LLVM's per-worker
            # commit reservation can linger until the pool is fully torn down. Killing workers and
            # collecting here releases that commit at end-of-run instead of holding it until the
            # interpreter exits (which, across repeated runs, was ratcheting committed memory up).
            try:
                ex.shutdown(wait=True, cancel_futures=True)
            except TypeError:
                ex.shutdown(wait=True)   # Python 3.8 has no cancel_futures
            del ex
            _gc.collect()
    if use_pq:
        if pqw["w"] is not None: pqw["w"].close()
        mpath = mpath_pq
    else:
        f.close(); mpath = mpath_csv
    _write_batch_summary(summary, os.path.join(out, f"summary{suffix}.csv"), n_runs)

    # Tactic matrix CSV (matches tournament_vec's schema/columns).
    tmpath = os.path.join(out, f"tactic_matrix{suffix}.csv")
    with open(tmpath, "w", newline="") as tf:
        tw = _csv.writer(tf)
        tw.writerow(["a_tactic", "b_tactic", "n_battles", "a_wins", "b_wins",
                     "a_win_rate", "b_win_rate", "stalemate_rate"])
        for i, a_t in enumerate(_TACTICS):
            for j, b_t in enumerate(_TACTICS):
                n = int(tac_cnt[i, j]); aw = int(tac_aw[i, j]); bw = int(tac_bw[i, j])
                stale = max(0, n - aw - bw)
                tw.writerow([a_t, b_t, n, aw, bw,
                             f"{(aw/n if n else 0):.4f}", f"{(bw/n if n else 0):.4f}",
                             f"{(stale/n if n else 0):.4f}"])
    if verbose:
        print(f"  wrote {mpath}, summary{suffix}.csv, tactic_matrix{suffix}.csv", flush=True)