"""optimal_play.py — opponent-aware "Optimal" Tactic play for the batch tournament (mode="optimal").

Public information: both players see each other's whole army (Retinue, gear, keywords, Holdings) before
choosing; only the Tactic is hidden until the reveal (unless an Outrider Intercept Post reveals it first).
So for every pairing the optimal player solves the Skirmish as a simultaneous zero-sum game:

  payoff[i, j] = expected casualties A inflicts - expected casualties A takes, for one Skirmish
                 at full strength, A playing Tactic i and B playing Tactic j (Fall Back excluded).

The expected values follow the engine's own Skirmish order (batch_engine.run_batch_random):
Initiative after Tactic mods with the Steady / Unwieldy clamps, max Initiative, Strained and Seize already
in the base value; Blunder at -2 (or "Blunder first"), Immune Blunder; strike order (the side striking first
removes front-line Retinues before the other strikes, refilled from reserve); to-Strike with the cap rules
(Strike +N, Tactic TH, Shielded / Negate Shielded, Blunder clamp); Cleave / Deadly / Crit N on
the dice; Parry first, then the Save (AP, Shield, Tactic TS, Planishing cap, Poison), then Recover; Riposte.

Each side then plays its equilibrium mix of that game (regret matching). Initiative therefore only pulls
weight when it changes who strikes first, keeps a side off the Blunder floor, or sets up a Tactic cell
that hurts the opponent: a side that can never strike first and can't be pushed to -2 (or is Immune
Blunder) puts no value on Initiative, without a separate rule.

Outrider Intercept Post: the revealed side plays its maximin Tactic (best worst case, knowing it will be
answered); the Outrider side plays the best response to it.

    import optimal_play as OP
    OP.explain(la, lb)            # both mixes, the payoff table and the initiative read for one pairing
"""
import numpy as np
from dice_config import clamp_init
import combat_primitives as _cp

from dice_config import FACES, FOCUSED_THR, CAP_THR, AUTO_PASS_FLOOR, PARRY_BASE, DEADLY_AP, UNSTOPPABLE_MOD

_AP = AUTO_PASS_FLOOR if AUTO_PASS_FLOOR is not None else 1
N_TAC = 6                    # Fall Back (index 6) is never part of the optimal mix
ITERS = 600                  # regret-matching iterations (exploitability < ~0.05 casualties on this game size)


# ── dice helpers (vectorised over any array shape) ──────────────────────────────────────────────────
def _p_ge(t):
    """P(d FACES >= t) with t an integer array; t <= 1 -> 1, t > FACES -> 0."""
    t = np.asarray(t, dtype=np.float64)
    return np.clip((FACES + 1 - t) / FACES, 0.0, 1.0)


def _p_lt(t):
    return 1.0 - _p_ge(t)


def _side(P, RP, skl, me, opp_P):
    """Per-pair arrays for one side in one phase. me = 'a' or 'b' (key prefix in RP)."""
    g = lambda k: np.asarray(P[k])
    s = {}
    s["to_hit"] = g("to_hit"); s["armor"] = g("armor_save"); s["max_init"] = g("max_init")
    s["size"] = g("size_start"); s["parry_bonus"] = g("parry_bonus")
    s["strike_bonus"] = g("strike_bonus_first" if skl == "first" and "strike_bonus_first" in P else "strike_bonus")
    s["ap"] = g(f"ap_{skl}"); s["ap_melee"] = g("ap_melee"); s["unstop_melee"] = g("unstop_melee")
    s["shield_off"] = g(f"shield_off_{skl}")
    s["shield_bonus"] = np.where(s["shield_off"], 0, g("shield_bonus_start"))
    s["swall"] = (g("shield_wall") if "shield_wall" in P else np.zeros_like(s["shield_off"], dtype=bool)) & ~s["shield_off"]   # Pavisiers' Yard
    s["tbh"] = np.where(s["shield_off"], 0, g("shield_tbh_penalty_start"))      # what the OPPONENT suffers
    s["th_self"] = np.where(s["shield_off"], 0, g("shield_th_penalty_start"))
    for k, key in (("steady", "Steady"), ("unw", "Unwieldy"), ("imunw", "Immune_Unwieldy"),
                   ("unstop", "Unstoppable"), ("negshield", "Negate_Shielded"), ("immtac", "Immune_Tactic_TH"),
                   ("blunder_first", "Blunder_first"), ("imm_blunder", "Immune_Blunder"),
                   ("cleave", "Cleave"), ("dw", "Dual_Wield"), ("deflect_tag", "Deflect"),
                   ("planish", "Planishing"), ("negtemp", "NegateTempered")):
        s[k] = g(f"{skl}_{key}")
    s["deadly"] = g(f"{skl}_Deadly"); s["crit"] = g(f"{skl}_crit_floor")
    s["ranged"] = g(f"{skl}_is_ranged")
    s["hook"] = g(f"{skl}_hook")   # Hook N / Negate Shielded (99)
    s["rp1"] = g(f"{skl}_Riposte_p1") if f"{skl}_Riposte_p1" in P else np.zeros_like(g(f"{skl}_Deadly"), dtype=bool)   # Riposte +1
    s["foe_parry"] = g(f"foe_parry_{skl}") if f"foe_parry_{skl}" in P else np.zeros_like(s["ranged"], dtype=np.int64)
    s["negrip"] = g(f"{skl}_Negate_Riposte")   # Negate Riposte (e.g. a Holding): the defender cannot Riposte its Strikes
    s["fluted"] = g("fluted") if "fluted" in P else np.zeros_like(s["ranged"], dtype=bool)   # armor: incoming AP -1
    s["unw_active"] = s["unw"] & ~s["imunw"]
    rp = RP[skl]
    s["parry"] = rp[f"{me}_parry"]; s["regen"] = rp[f"{me}_regen"]; s["riposte"] = rp[f"{me}_riposte"]
    tags = P[f"tags_{skl}"]; otags = opp_P[f"tags_{skl}"]
    s["poison"] = np.array([("Poison" in t) and ("Immune Poison" not in o) for t, o in zip(tags, otags)])
    return s


def _cas_per_strike(def_s, atk_s, save_t, deadly_frac, atk_unstop, atk_ranged, atk_deflect, atk_poison,
                    atk_negtemp, deadly_shift=0, atk_negrip=False, atk_fp=0):
    """Expected casualties per landed Strike on the defender, and expected Ripostes per Strike."""
    # save targets (Planishing caps both at CAP_THR unless the attacker Negates it)
    cap = def_s["planish"] & ~atk_negtemp
    sc = np.where(cap, np.minimum(save_t, CAP_THR), save_t)
    dsc_raw = save_t + DEADLY_AP + deadly_shift   # deadly_shift: Fluted after Deadly (AP 0 case)
    dsc = np.where(cap, np.minimum(dsc_raw, CAP_THR), dsc_raw)
    auto_pass = save_t < _AP
    # parry thresholds
    no_rip = atk_deflect | atk_ranged | atk_negrip   # Ranged / Negate Riposte block Riposte; only a Deflect tag worsens Parry
    pthr = PARRY_BASE - def_s["parry_bonus"] + UNSTOPPABLE_MOD * atk_unstop + atk_deflect + atk_fp   # 11+ = no Parry (_p_ge -> 0)
    pm = def_s["parry"]
    dw = def_s["dw"]                     # Dual Wield: a failed Parry is rerolled once; FOCUSED_THR-1 also Ripostes
    q_n, q_d = _p_ge(pthr), _p_ge(np.maximum(FOCUSED_THR, pthr))   # Deadly: at best a Focused roll
    pp_n = np.where(pm, np.where(dw, 1 - (1 - q_n) ** 2, q_n), 0.0)
    pp_d = np.where(pm, np.where(dw, 1 - (1 - q_d) ** 2, q_d), 0.0)
    rthr = def_s["regen"]
    has_rec = rthr > 0
    p_rec = np.where(has_rec, _p_ge(np.minimum(rthr, CAP_THR)), 0.0)
    p_rec_foc = np.where(has_rec, _p_ge(FOCUSED_THR), 0.0)
    p_foc = _p_ge(FOCUSED_THR)
    # normal strike: fails on roll < sc (unless auto-pass); Poison also fails a Focused save roll
    f_plain = np.where(auto_pass, 0.0, _p_lt(sc))
    f_poison = np.where(atk_poison, np.where(auto_pass, p_foc, _p_ge(np.maximum(FOCUSED_THR, sc))), 0.0)
    cas_n = (1 - pp_n) * (f_plain * (1 - p_rec) + f_poison * (1 - p_rec_foc))
    f_d = _p_lt(dsc)
    f_dp = np.where(atk_poison, _p_ge(np.maximum(FOCUSED_THR, dsc)), 0.0)
    cas_d = (1 - pp_d) * (f_d + f_dp) * (1 - (0.0 if _cp.DEADLY_NO_RECOVER else p_rec_foc))   # Version D: no Recover
    cas = (1 - deadly_frac) * cas_n + deadly_frac * cas_d
    rip_ok = def_s["riposte"] & ~no_rip
    q_r = _p_ge(np.maximum(pthr, np.where(def_s["rp1"], FOCUSED_THR - 1, FOCUSED_THR)))   # a parrying roll that Ripostes (Riposte +1: 9)
    rip_n = np.where(dw, q_r * (2 - q_n), q_r)                                  # reroll: first roll, or the reroll
    rip = np.where(rip_ok, (1 - deadly_frac) * np.where(pm, rip_n, 0.0)
                   + deadly_frac * pp_d, 0.0)
    return cas, rip


def _strike_dice(tt, s):
    """(strikes per die, Deadly fraction of those strikes) for to-Strike tt (pairs x 6 x 6)."""
    auto = tt < _AP
    ph = np.where(auto, 1.0, _p_ge(tt))
    crit = s["crit"][:, None, None]
    pc = np.where(auto, _p_ge(crit), _p_ge(np.maximum(tt, crit)))        # strike AND proc
    ph0, pc0 = ph, np.minimum(pc, 0.999)                                    # one extra (Cleave) die
    clv = s["cleave"][:, None, None]
    # Cleave chains: each proc rolls an extra die, and an extra die that procs rolls another, so a proc
    # brings 1 / (1 - pc0) extra dice on average: ph0 / (1 - pc0) extra Strikes, pc0 / (1 - pc0) of them procs.
    strikes = ph + np.where(clv, pc * ph0 / (1 - pc0), 0.0)
    dead = s["deadly"][:, None, None]
    deadly = np.where(dead, pc + np.where(clv, pc * pc0 / (1 - pc0), 0.0), 0.0)
    frac = np.where(strikes > 0, np.clip(deadly / np.maximum(strikes, 1e-9), 0, 1), 0.0)
    return strikes, frac


def payoff(Pa, Pb, RP, skl, a_bi, b_bi, tab, front_cap, reserve_cap):
    """(npairs, 6, 6) expected net casualties for A; also returns the per-cell initiative arrays."""
    first = skl == "first"
    A = _side(Pa, RP, skl, "a", Pb)
    B = _side(Pb, RP, skl, "b", Pa)
    T = slice(0, N_TAC)
    aI = tab["a_I"][T, T][None]; bI = tab["b_I"][T, T][None]
    aTH = tab["a_TH"][T, T][None]; bTH = tab["b_TH"][T, T][None]
    aTS = tab["a_TS"][T, T][None]; bTS = tab["b_TS"][T, T][None]
    # Shield Wall (Pavisiers' Yard): in Defensive Formation with the Shield Equipped, incoming AP -1 more
    # (Articulated count + Shield Wall, per Tactic cell: A's Tactic is axis 1, B's axis 2)
    _dfa = (np.arange(N_TAC) == _DF_IDX)
    A_fl = np.asarray(A["fluted"]).astype(np.int64)[:, None, None] + (np.asarray(A["swall"])[:, None, None] & _dfa[None, :, None])
    B_fl = np.asarray(B["fluted"]).astype(np.int64)[:, None, None] + (np.asarray(B["swall"])[:, None, None] & _dfa[None, None, :])
    no_combat = tab["no_combat"][T, T][None]
    x = lambda v: np.asarray(v)[:, None, None]
    # Initiative (Steady: negative Tactic mods -> 0; Unwieldy: positive -> 0)
    aIm = np.where(x(A["steady"]) & (aI < 0), 0, aI); aIm = np.where(x(A["unw_active"]) & (aIm > 0), 0, aIm)
    bIm = np.where(x(B["steady"]) & (bI < 0), 0, bI); bIm = np.where(x(B["unw_active"]) & (bIm > 0), 0, bIm)
    a_init = clamp_init(x(a_bi) + aIm, x(Pa[f"binit_neg_{skl}"]) + np.minimum(aIm, 0), x(A["max_init"]), np)
    b_init = clamp_init(x(b_bi) + bIm, x(Pb[f"binit_neg_{skl}"]) + np.minimum(bIm, 0), x(B["max_init"]), np)
    a_trip = ((a_init <= -2) | (x(A["blunder_first"]) & first)) & ~x(A["imm_blunder"])
    b_trip = ((b_init <= -2) | (x(B["blunder_first"]) & first)) & ~x(B["imm_blunder"])

    def to_strike(S, O, TH, trip):
        improve = -x(S["strike_bonus"]) - np.maximum(TH, 0)
        worsen = np.maximum(x(O["tbh"]) - x(S["hook"]), 0) + x(S["th_self"]) + np.where(x(S["immtac"]), 0, np.maximum(-TH, 0))
        pre = np.minimum(x(S["to_hit"]) + improve, CAP_THR)
        pre = np.where(trip, np.maximum(pre, CAP_THR), pre)
        return np.minimum(pre + worsen, CAP_THR)

    a_tt = to_strike(A, B, aTH, a_trip)
    b_tt = to_strike(B, A, bTH, b_trip)
    a_str, a_df = _strike_dice(a_tt, A)
    b_str, b_df = _strike_dice(b_tt, B)
    # saves: defender armour - attacker AP - defender shield - defender's Tactic TS
    # (Fluted defender: incoming AP -1 toward 0; Deadly gets the after-Deadly shift)
    b_sv = x(B["armor"]) - _cp.fluted_ap(x(A["ap"]), B_fl) - x(B["shield_bonus"]) - bTS
    a_sv = x(A["armor"]) - _cp.fluted_ap(x(B["ap"]), A_fl) - x(A["shield_bonus"]) - aTS
    b_cas_ps, b_rip_ps = _cas_per_strike({k: x(v) for k, v in B.items()}, A, b_sv, a_df, x(A["unstop"]), x(A["ranged"]),
                                         x(A["deflect_tag"]), x(A["poison"]), x(A["negtemp"]),
                                         _cp.deadly_shift(x(A["ap"]), B_fl), x(A["negrip"]), x(A["foe_parry"]))
    a_cas_ps, a_rip_ps = _cas_per_strike({k: x(v) for k, v in A.items()}, B, a_sv, b_df, x(B["unstop"]), x(B["ranged"]),
                                         x(B["deflect_tag"]), x(B["poison"]), x(B["negtemp"]),
                                         _cp.deadly_shift(x(B["ap"]), A_fl), x(B["negrip"]), x(B["foe_parry"]))
    # Riposte: a clean Strike from the riposter's melee weapon back onto the striker
    a_rip_sv = x(A["armor"]) - _cp.fluted_ap(x(B["ap_melee"]), A_fl) - x(A["shield_bonus"]) - aTS
    b_rip_sv = x(B["armor"]) - _cp.fluted_ap(x(A["ap_melee"]), B_fl) - x(B["shield_bonus"]) - bTS
    zero = np.zeros_like(a_df)
    # per Riposte Strike received: casualties, and the chance it is Riposted back (a Riposte is a melee Strike)
    a_cas_rip, a_rr = _cas_per_strike({k: x(v) for k, v in A.items()}, B,
                                      a_rip_sv, zero, x(B["unstop_melee"]), x(np.zeros_like(B["ranged"])),
                                      x(np.zeros_like(B["ranged"])), x(B["poison"]), x(B["negtemp"]), 0, x(B["negrip"]))
    b_cas_rip, b_rr = _cas_per_strike({k: x(v) for k, v in B.items()}, A,
                                      b_rip_sv, zero, x(A["unstop_melee"]), x(np.zeros_like(A["ranged"])),
                                      x(np.zeros_like(A["ranged"])), x(A["poison"]), x(A["negtemp"]), 0, x(A["negrip"]))
    g = 1.0 / (1.0 - np.minimum(a_rr * b_rr, 0.95))        # the exchange goes back and forth (geometric)
    a_front = np.minimum(front_cap, x(A["size"])).astype(float)
    b_front = np.minimum(front_cap, x(B["size"])).astype(float)
    a_res = np.minimum(reserve_cap, np.maximum(0, x(A["size"]) - front_cap)).astype(float)
    b_res = np.minimum(reserve_cap, np.maximum(0, x(B["size"]) - front_cap)).astype(float)

    def kills(front, strikes, cas_ps, cap):
        return np.minimum(front * strikes * cas_ps, cap)

    a_first = a_init > b_init
    b_first = b_init > a_init
    kA0 = kills(a_front, a_str, b_cas_ps, b_front)                    # A's kills if A strikes at full front
    kB0 = kills(b_front, b_str, a_cas_ps, a_front)
    b_front_after = np.minimum(front_cap, np.maximum(0, b_front - kA0) + b_res)
    a_front_after = np.minimum(front_cap, np.maximum(0, a_front - kB0) + a_res)
    kB = np.where(a_first, kills(b_front_after, b_str, a_cas_ps, a_front), kB0)
    kA = np.where(b_first, kills(a_front_after, a_str, b_cas_ps, b_front), kA0)
    # Riposte exchanges: B's Ripostes off A's Strikes, and A's off B's; each can be Riposted back
    rB = np.where(b_first, a_front_after, a_front) * a_str * b_rip_ps      # Ripostes B makes
    rA = np.where(a_first, b_front_after, b_front) * b_str * a_rip_ps      # Ripostes A makes
    a_rip_taken = g * (rB * a_cas_rip + rA * b_rr * a_cas_rip)
    b_rip_taken = g * (rA * b_cas_rip + rB * a_rr * b_cas_rip)
    net = (kA + b_rip_taken) - (kB + a_rip_taken)
    net = np.where(no_combat, 0.0, net)
    return net, {"a_init": a_init, "b_init": b_init, "a_trip": a_trip, "b_trip": b_trip, "kA": kA, "kB": kB}


def solve(M, a_mask=None, b_mask=None, iters=ITERS):
    """Equilibrium mixes of the zero-sum games M (npairs, 6, 6), row player maximises.
    Regret matching+ with averaged strategies. masks (npairs, 6) bool: allowed Tactics.
    Returns (x (npairs,6), y (npairs,6), value (npairs,))."""
    n, k, _ = M.shape
    am = np.ones((n, k), bool) if a_mask is None else a_mask
    bm = np.ones((n, k), bool) if b_mask is None else b_mask
    scale = np.maximum(np.abs(M).max(axis=(1, 2)), 1e-9)[:, None]
    Mn = M / scale[:, :, None]
    Ra = np.zeros((n, k)); Rb = np.zeros((n, k))
    xs = np.zeros((n, k)); ys = np.zeros((n, k))
    x = am / am.sum(1, keepdims=True); y = bm / bm.sum(1, keepdims=True)
    for t in range(iters):
        ua = np.einsum("nij,nj->ni", Mn, y)            # row payoffs
        ub = -np.einsum("nij,ni->nj", Mn, x)           # column payoffs
        va = (x * ua).sum(1, keepdims=True); vb = (y * ub).sum(1, keepdims=True)
        Ra = np.maximum(0, Ra + (ua - va)) * am
        Rb = np.maximum(0, Rb + (ub - vb)) * bm
        sa = Ra.sum(1, keepdims=True); sb = Rb.sum(1, keepdims=True)
        x = np.where(sa > 0, Ra / np.where(sa > 0, sa, 1), am / am.sum(1, keepdims=True))
        y = np.where(sb > 0, Rb / np.where(sb > 0, sb, 1), bm / bm.sum(1, keepdims=True))
        w = t + 1                                      # linear averaging (RM+)
        xs += w * x; ys += w * y
    xs /= xs.sum(1, keepdims=True); ys /= ys.sum(1, keepdims=True)
    val = np.einsum("ni,nij,nj->n", xs, M, ys)
    return xs, ys, val


def maximin(M, mask, rows=True):
    """Pure maximin Tactic for the revealed side. rows=True: A (maximise min over columns)."""
    if rows:
        worst = np.where(mask[:, :, None], M, np.inf).min(axis=2)
        worst = np.where(mask, worst, -np.inf)
        return worst.argmax(axis=1)
    worst = np.where(mask[:, None, :], M, -np.inf).max(axis=1)        # B minimises A's best
    worst = np.where(mask, worst, np.inf)
    return worst.argmin(axis=1)


def precompute(Pa, Pb, RP, a_bi_first_seize, a_bi_first_noseize, b_bi_first_seize, b_bi_first_noseize,
               a_bi_normal, b_bi_normal, tab, front_cap, reserve_cap):
    """Per-pair optimal mixes and Outrider answers for the three Skirmish states:
    'first_a' (A holds Seize), 'first_b' (B holds Seize), 'normal'.
    Returns {state: dict(x, y, M, a_maximin, b_maximin)}."""
    out = {}
    tm_a = np.asarray(Pa["tac_mask"])[:, :N_TAC]; tm_b = np.asarray(Pb["tac_mask"])[:, :N_TAC]
    for state, skl, abi, bbi in (("first_a", "first", a_bi_first_seize, b_bi_first_noseize),
                                 ("first_b", "first", a_bi_first_noseize, b_bi_first_seize),
                                 ("normal", "normal", a_bi_normal, b_bi_normal)):
        am = np.where(np.asarray(Pa[f"{skl}_tac_restricted"])[:, None], tm_a, True)
        bm = np.where(np.asarray(Pb[f"{skl}_tac_restricted"])[:, None], tm_b, True)
        M, _ = payoff(Pa, Pb, RP, skl, abi, bbi, tab, front_cap, reserve_cap)
        x, y, v = solve(M, am, bm)
        out[state] = dict(x=x, y=y, M=M, value=v, a_mask=am, b_mask=bm,
                          a_maximin=maximin(M, am, rows=True), b_maximin=maximin(M, bm, rows=False))
    return out


def weights_for_slots(pre, a_seizes, first, n_runs):
    """(N,7) weights for A and B this Skirmish, tiled from per-pair mixes."""
    def pick(key):
        if first:
            v = np.where(a_seizes[:, None], np.repeat(pre["first_a"][key], n_runs, axis=0),
                         np.repeat(pre["first_b"][key], n_runs, axis=0))
        else:
            v = np.repeat(pre["normal"][key], n_runs, axis=0)
        return v
    xa = pick("x"); yb = pick("y")
    wa = np.zeros((xa.shape[0], 7)); wb = np.zeros((yb.shape[0], 7))
    wa[:, :N_TAC] = xa; wb[:, :N_TAC] = yb
    return wa, wb


def outrider_answer(pre, a_seizes, first, n_runs, revealed_side):
    """When `revealed_side` ('a' or 'b') is forced to reveal: (revealed tactic, answering tactic) per slot."""
    st = None if first else "normal"
    def tile(key, s):
        return np.repeat(pre[s][key], n_runs, axis=0)
    if first:
        Mx = np.where(a_seizes[:, None, None], tile("M", "first_a"), tile("M", "first_b"))
        amin = np.where(a_seizes, tile("a_maximin", "first_a"), tile("a_maximin", "first_b"))
        bmin = np.where(a_seizes, tile("b_maximin", "first_a"), tile("b_maximin", "first_b"))
        am = np.where(a_seizes[:, None], tile("a_mask", "first_a"), tile("a_mask", "first_b"))
        bm = np.where(a_seizes[:, None], tile("b_mask", "first_a"), tile("b_mask", "first_b"))
    else:
        Mx = tile("M", st); amin = tile("a_maximin", st); bmin = tile("b_maximin", st)
        am = tile("a_mask", st); bm = tile("b_mask", st)
    idx = np.arange(Mx.shape[0])
    if revealed_side == "b":              # A has the Outrider
        bt = bmin
        at = np.where(am, Mx[idx, :, bt], -np.inf).argmax(axis=1)
        return bt, at
    at = amin
    bt = np.where(bm, Mx[idx, at, :], np.inf).argmin(axis=1)
    return at, bt


# ── single-pairing inspection ──────────────────────────────────────────────────────────────────────
TACTICS6 = ["Scout", "Ambush", "Flank", "Charge", "Fighting Formation", "Defensive Formation"]
_DF_IDX = TACTICS6.index("Defensive Formation")   # Pavisiers' Yard Save +1


def explain(la, lb, a_seizes=True, show=True):
    """Optimal mixes, payoff table and initiative read for one pairing (A = la)."""
    import pandas as pd
    import batch_engine as BE
    import vectorized_combat as vc
    la2, lb2 = la, lb
    # confers move to the opponent exactly as in the tournament
    def conf(s, o):
        c = {t.split(":", 1)[1] for t in s.extra_tags if t.startswith("confers:")}
        return (s._replace(extra_tags=frozenset(t for t in s.extra_tags if not t.startswith("confers:"))),
                o._replace(extra_tags=frozenset(set(o.extra_tags) | c)) if c else o)
    la2, lb2 = conf(la2, lb2); lb2, la2 = conf(lb2, la2)
    la2, lb2 = vc.resolve_equipment(la2, lb2)
    Pa = BE.pack_side([la2], True); Pb = BE.pack_side([lb2], False)
    RP = BE._precompute_regen_parry(Pa, Pb)
    tab = vc.get_tactic_tables()
    pre = precompute(Pa, Pb, RP, Pa["binit_first_seize"], Pa["binit_first_noseize"], Pb["binit_first_seize"],
                     Pb["binit_first_noseize"], Pa["binit_normal"], Pb["binit_normal"], tab, vc.FRONT_CAP, vc.RESERVE_CAP)
    names = [{"Fighting Formation": "FF", "Defensive Formation": "DF"}.get(t, t) for t in TACTICS6]
    res = {}
    for st in ("first_a" if a_seizes else "first_b", "normal"):
        p = pre[st]
        skl = "first" if st.startswith("first") else "normal"
        abi = Pa["binit_first_seize" if st == "first_a" else "binit_first_noseize"] if skl == "first" else Pa["binit_normal"]
        bbi = Pb["binit_first_noseize" if st == "first_a" else "binit_first_seize"] if skl == "first" else Pb["binit_normal"]
        _, info = payoff(Pa, Pb, RP, skl, abi, bbi, tab, vc.FRONT_CAP, vc.RESERVE_CAP)
        ai, bi_ = info["a_init"][0], info["b_init"][0]
        res[st] = {
            "payoff": pd.DataFrame(p["M"][0], index=names, columns=names).round(2),
            "mix": pd.DataFrame({"A": p["x"][0], "B": p["y"][0]}, index=names).round(2),
            "value": round(float(p["value"][0]), 2),
            "A strikes first in": int((ai > bi_).sum()), "B strikes first in": int((bi_ > ai).sum()),
            "A Blunders in": int(info["a_trip"][0].sum()), "B Blunders in": int(info["b_trip"][0].sum()),
            "A init range": (int(ai.min()), int(ai.max())), "B init range": (int(bi_.min()), int(bi_.max())),
        }
    if show:
        from display_lab import disp_df, D
        try:
            from IPython.display import display, Markdown
            out = lambda t, d: (display(Markdown(f"**{D(t)}**")), display(disp_df(d)))
        except Exception:
            out = lambda t, d: print(f"\n== {D(t)}\n{disp_df(d)}")
        for st, r in res.items():
            out(f"{st}: payoff to A (expected casualties dealt - taken), value {r['value']}", r["payoff"])
            out(f"{st}: optimal mixes", r["mix"])
            print({k: v for k, v in r.items() if k not in ("payoff", "mix")})
    return res
