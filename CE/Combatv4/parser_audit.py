"""parser_audit.py — does every token the Holding-text parser emits actually do its job in the engine?

For each combat token in renown_data.HOLDING_SIM (plus the Domain-standing tokens from STANDING_EFFECTS):
  1. static: which packed engine fields (batch_engine.pack_side, what the tournament reads) change
     when the token is added to an otherwise identical army
  2. effect: win-rate shift in a context where the token should matter (e.g. Crit 8 on a Cleave weapon,
     Planishing against a War Hammer), using the batch tournament engine, both sides as attacker
  3. verdict: OK (moved the engine and the win rate in the expected direction), INERT (no field moved),
     WIRED, SMALL (fields moved, win rate within noise), WRONG WAY (win rate moved against the holder)

    from parser_audit import audit
    df = audit()                 # ~1 min
    df = audit(n_runs=4000)      # tighter

Run from Combatv4 with shims first on sys.path (same as the notebook).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.dirname(_HERE), _HERE, os.path.join(_HERE, "shims")):
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

import numpy as np
import pandas as pd
import renown_data as rd
import loadouts as L
import batch_engine as BE

# token -> (description of the test context, holder overrides, opponent overrides, holder extra tags kept on both arms)
# overrides are Loadout field dicts; "tags" adds context tags to BOTH arms of the holder (with/without token).
_BASE = dict(retinue="Sergeant", weapon="Arming Sword", shield="Buckler Shield", armor="Chainmail", ranged=None)
CONTEXT = {
    "Strike +1":       ("plain", {}, {}, []),
    "Init +1":         ("plain", {}, {}, []),
    "AP -1":           ("vs Full Plate", {}, {"armor": "Full Plate"}, []),
    "Parry +1":        ("holder has Parry", {}, {}, ["Parry"]),
    "Parry":           ("plain", {}, {}, []),
    "Crit 8":          ("holder: Battle Axe (Cleave)", {"weapon": "Battle Axe", "shield": None}, {}, []),
    "Drilled":         ("plain", {}, {}, []),
    "Nimble":          ("plain", {}, {}, []),
    "Immune Strained": ("holder is Strained", {}, {}, ["Strained"]),
    "MaxInit3":        ("both sides Init +1 & Nimble (holder can reach 3)", {}, {"tags": ["Init +1", "Nimble"]},
                        ["Init +1", "Nimble"]),
    "Seize: first":    ("plain", {}, {}, []),
    "Planishing":      ("vs War Hammer, holder Gothic Plate", {"armor": "Gothic Plate"},
                        {"weapon": "War Hammer", "shield": None}, []),
    "Poison":          ("vs Gothic Plate", {}, {"armor": "Gothic Plate"}, []),
    "Serrated":        ("vs Recover 6", {}, {"tags": ["Recover 6"]}, []),
    "Recover 8":       ("plain", {}, {}, []),
    "Enduring":        ("holder has Recover 6", {}, {}, ["Recover 6"]),
    "Riposte":         ("holder has Parry", {}, {}, ["Parry"]),
    "Florentine":      ("holder Dual Wield Arming Swords, no shield", {"shield": None}, {}, ["Dual Wield"]),
    "Immune Awkward":  ("holder Spears (Awkward) + Parry", {"weapon": "Spears"}, {}, ["Parry"]),
    "Immune Unwieldy": ("holder Pike (Unwieldy) vs Halberd (init 1)", {"weapon": "Pike", "shield": None},
                        {"weapon": "Halberd", "shield": None}, []),
    "Outrider: every": ("plain", {}, {}, []),
    "Immune Blunder":  ("opponent confers Blunder first", {}, {"tags": ["confers:Blunder first"]}, []),
    "Immune Panic":    ("plain", {}, {}, []),
    "Shake +1":        ("plain", {}, {}, []),
    "confers:Strained":       ("plain", {}, {}, []),
    "confers:Blunder first":  ("plain", {}, {}, []),
}


def _ld(name, over, tags):
    f = dict(_BASE)
    f.update({k: v for k, v in over.items() if k != "tags"})
    t = set(over.get("tags", [])) | set(tags)
    return L.Loadout(name=name, retinue=f["retinue"], weapon=f["weapon"], shield=f["shield"], armor=f["armor"],
                     ranged=f["ranged"], has_tiltyard=False, size=L.DEFAULT_ARMY_SIZE,
                     extra_tags=frozenset(t), upkeep_per_retinue=0)


def _packed(ld, opp=None):
    P = BE.pack_side([ld], is_attacker=False)
    out = {}
    if opp is not None:                      # per-pairing reads: Recover / Parry / Riposte / Florentine thresholds
        Po = BE.pack_side([opp], is_attacker=False)
        for skl, d in BE._precompute_regen_parry(P, Po).items():
            for k, v in d.items():
                side = "self" if k.startswith("a_") else "opp"
                out[f"{skl}_{k[2:]}({side})"] = v[0].item()
        _, _, a_ct, _ = BE._precompute_outrider_tables([(ld, opp)], P, Po)
        out["outrider_table(pair)"] = None if a_ct[0] is None else a_ct[0].tolist()
    for k, v in P.items():
        if k.startswith("_") or k in ("tags_first", "tags_normal", "seize_mode"):
            continue
        if isinstance(v, np.ndarray):
            out[k] = v[0].tolist() if v.ndim > 1 else v[0].item()
    out["seize_mode"] = P["seize_mode"][0]
    return out


def _wr(holder, opp, n_runs, seed):
    r = BE.run_batch_random([(holder, opp), (opp, holder)], n_runs=n_runs, seed=seed)
    w = r["a_wins"][0] + r["b_wins"][1]
    l = r["b_wins"][0] + r["a_wins"][1]
    return w / max(1, w + l), w + l


def token_sources():
    """{token: [Holdings]} for every combat token the parser emits (gear gates excluded),
    plus the Domain-standing tokens."""
    src = {}
    for n, h in rd.HOLDING_SIM.items():
        for t in h["tags"]:
            if t.startswith(L._INFO_PREFIX) or t in L._INFO_EXACT:
                continue
            t = L._ENGINE_TOKEN.get(t, t)
            if t == "Recover +1":
                continue                        # a rung on Recover N, audited through "Recover 8"
            src.setdefault(t, []).append(n)
    for (d, st), text in getattr(rd, "STANDING_EFFECTS", {}).items():
        for tag in L.standing_tags({d: L._ST[st]}):
            src.setdefault(tag, []).append(f"{st} {d}")
    return src


def audit(n_runs=2000, seed=11, show=True):
    rows = []
    for tok, holders in sorted(token_sources().items()):
        ctx = CONTEXT.get(tok)
        if ctx is None:
            rows.append(dict(token=tok, holdings=", ".join(holders), context="(no test context)",
                             fields_changed="", wr_without=np.nan, wr_with=np.nan, delta=np.nan, verdict="UNTESTED"))
            continue
        label, hover, oover, keep = ctx
        a0 = _ld("without", hover, keep)
        a1 = _ld("with", hover, list(keep) + [tok])
        opp = _ld("opp", oover, [])
        p0, p1 = _packed(a0, opp), _packed(a1, opp)
        changed = sorted(k for k in p1 if p0.get(k) != p1[k])
        if tok.startswith("confers:"):
            # confers tags are moved onto the opponent at pairing time, so the holder's own pack can't show them
            o0 = _packed(_ld("o", oover, [])); o1 = _packed(_ld("o", oover, [tok.split(":", 1)[1]]))
            changed = ["(opponent) " + k for k in o1 if o0.get(k) != o1[k]]
        w0, n0 = _wr(a0, opp, n_runs, seed)
        w1, n1 = _wr(a1, opp, n_runs, seed)
        se = np.sqrt(w0 * (1 - w0) / max(1, n0) + w1 * (1 - w1) / max(1, n1))
        d = w1 - w0
        if not changed:
            verdict = "INERT"
        elif abs(d) < 2 * se:
            verdict = "WIRED, SMALL"
        elif d < 0:
            verdict = "WRONG WAY"
        else:
            verdict = "OK"
        rows.append(dict(token=tok, holdings=", ".join(holders), context=label, fields_changed=", ".join(changed),
                         wr_without=round(w0, 3), wr_with=round(w1, 3), delta=round(d, 3), verdict=verdict))
    df = pd.DataFrame(rows)
    if show:
        with pd.option_context("display.max_colwidth", 80, "display.width", 250):
            from display_lab import disp_df
            print(disp_df(df).to_string(index=False))
    return df


# Rules text (renown_data.GLOSSARY) the engine does not follow as written. Kept here so the audit prints them;
# these are flags for the designer, not fixes.
RULE_GAPS = [
    # (keyword, rules text, what the engine does instead). Resolved Nov 2026: Cleave chains in combat_kernel,
    # Riposte-a-Riposte in both engines (_riposte_chain_vec / _riposte_chain_batch), and Unstoppable no
    # longer claims to stop Riposte in GLOSSARY.
]


def rule_gaps(show=True):
    df = pd.DataFrame(RULE_GAPS, columns=["keyword", "rules text", "engine"])
    if show:
        with pd.option_context("display.max_colwidth", 120, "display.width", 250):
            from display_lab import disp_df
            print(disp_df(df).to_string(index=False))
    return df


if __name__ == "__main__":
    audit()
    print()
    rule_gaps()
