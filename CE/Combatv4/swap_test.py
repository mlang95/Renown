#!/usr/bin/env python3
"""swap_test.py — what is one change worth, all else equal?

Takes builds from a saved pool, makes an identical twin of each with ONE thing changed, and fights original
and twin against the same fixed panel of opponents (both sides of the table, Monument-sharing pairs skipped
as in the tournament). The difference is the change's value for those builds; it doesn't depend on pool
composition and doesn't cancel out when most of the field carries the same gear.

Two measures:
  analytic  expected casualties dealt minus taken per Skirmish at both sides' optimal Tactic mix
            (optimal_play.precompute, exact dice odds, no simulation; seconds)
  sim       win rate from full battles (batch engine, optimal play; minutes)

Changes (one per run):
  --swap shield "Kite Shield" "Tower Shield"      swap an item (shield / armor / weapon / ranged)
  --add-tag "Shake +1"   /   --remove-tag "Init +1"   add or remove an army keyword (a Holding's effect)
  --variant SHIELDS "Kite Shield" '{"tags": ["Shielded 2"]}'
                                                  the twin uses a modified copy of the item; the panel keeps
                                                  the original (tests a stat change on its own)
Subjects: --where weapon=Bastard Sword --where pursuit=Armory ... (default: every build the change applies to).

Run from CE/ (paths via ce_paths):
  python Combatv4/swap_test.py --swap shield "Kite Shield" "Tower Shield"
  python Combatv4/swap_test.py --add-tag "Shake +1" --where pursuit=Armory --sim
"""
import argparse, glob, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import ce_paths  # noqa: E402
ce_paths.install(verbose=False)
import numpy as np  # noqa: E402

_KIND_DICT = {"shield": "SHIELDS", "armor": "ARMORS", "weapon": "WEAPONS", "ranged": "RANGED"}
_FIELD = {"SHIELDS": "shield", "ARMORS": "armor", "WEAPONS": "weapon", "RANGED": "ranged"}


def apply_variant(spec):
    """spec = [DICT, item, overrides]: add '<item> (test)' to that dict = item updated with overrides. Returns its name."""
    import renown_data as rd
    d, item, over = spec
    table = getattr(rd, d)
    new = f"{item} (test)"
    e = dict(table[item]); e.update(over)
    table[new] = e
    return new


def _worker_init(variant):
    if variant:
        apply_variant(variant)


def _sim_block(args):
    pairs, n_runs, seed = args
    import batch_engine as BE
    res = BE.run_batch_random(pairs, n_runs=n_runs, seed=seed, mode="optimal")
    n = res["a_wins"] + res["b_wins"] + res["mut_wipe"] + res.get("indecisive", 0)
    return (res["a_wins"] / np.maximum(n, 1)).astype(float), (res["b_wins"] / np.maximum(n, 1)).astype(float)


def analytic_values(pairs):
    """Per pair (A, B): expected net casualties per Skirmish for A at the optimal mixes: (first Skirmish, later)."""
    import batch_engine as BE, vectorized_combat as vc, optimal_play as OP

    def conf(s, o):
        c = {t.split(":", 1)[1] for t in s.extra_tags if t.startswith("confers:")}
        return (s._replace(extra_tags=frozenset(t for t in s.extra_tags if not t.startswith("confers:"))),
                o._replace(extra_tags=frozenset(set(o.extra_tags) | c)) if c else o)
    A, B = [], []
    for la, lb in pairs:
        la2, lb2 = conf(la, lb); lb2, la2 = conf(lb2, la2)
        la2, lb2 = vc.resolve_equipment(la2, lb2)
        A.append(la2); B.append(lb2)
    Pa = BE.pack_side(A, True); Pb = BE.pack_side(B, False)
    RP = BE._precompute_regen_parry(Pa, Pb)
    tab = vc.get_tactic_tables()
    pre = OP.precompute(Pa, Pb, RP, Pa["binit_first_seize"], Pa["binit_first_noseize"], Pb["binit_first_seize"],
                        Pb["binit_first_noseize"], Pa["binit_normal"], Pb["binit_normal"], tab, vc.FRONT_CAP, vc.RESERVE_CAP)
    first = (np.asarray(pre["first_a"]["value"]) + np.asarray(pre["first_b"]["value"])) / 2
    return first, np.asarray(pre["normal"]["value"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--swap", nargs=3, metavar=("KIND", "FROM", "TO"))
    g.add_argument("--add-tag")
    g.add_argument("--remove-tag")
    g.add_argument("--variant", nargs=3, metavar=("DICT", "ITEM", "JSON"))
    ap.add_argument("--where", action="append", default=[], help="field=value (retinue/weapon/shield/armor/ranged/pursuit)")
    ap.add_argument("--pool", default=None, help="pool CSV (default: newest in lab_out/_pool_cache)")
    ap.add_argument("--subjects", type=int, default=150, help="max builds to test (random sample)")
    ap.add_argument("--panel", type=int, default=300, help="opponents in the fixed panel")
    ap.add_argument("--sim", action="store_true", help="also run full battles (win rate)")
    ap.add_argument("--runs", type=int, default=25)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    import loadouts as L, renown_data as rd
    pool_path = args.pool or max(glob.glob(os.path.join(os.path.dirname(HERE), "lab_out", "_pool_cache", "*.csv")),
                                 key=os.path.getmtime)
    pool = L._load_loadouts_from_csv(pool_path)
    print(f"pool: {pool_path} ({len(pool)} builds)")

    variant = None
    if args.variant:
        d, item, js = args.variant
        variant = [d, item, json.loads(js)]
        test_name = apply_variant(variant)
        field, frm, to = _FIELD[d], item, test_name
        label = f"{item} -> {item} with {js}"
    elif args.swap:
        kind, frm, to = args.swap
        field = kind
        label = f"{kind}: {frm} -> {to}"
    else:
        field = None
        label = f"add {args.add_tag}" if args.add_tag else f"remove {args.remove_tag}"

    def matches(ld):
        for w in args.where:
            k, v = w.split("=", 1)
            if k == "pursuit":
                if v not in ld.pursuits:
                    return False
            elif str(getattr(ld, k) or "") != v:
                return False
        if field:
            return (getattr(ld, field) or "") == frm
        if args.add_tag:
            return args.add_tag not in ld.extra_tags
        return args.remove_tag in ld.extra_tags

    def twin(ld):
        if field:
            t = ld._replace(**{field: to}, name=ld.name + " |swap")
            if field in ("shield", "weapon", "armor", "ranged"):
                w, sh = t.weapon, t.shield
                b2h = sh == "Buckler Shield" and L._true_2h(w) and "Buckler 2H" in t.extra_tags
                if not b2h and not L._structural_legal(w or "Farm Tools", sh, t.armor, t.ranged, t.has_tiltyard):
                    return None
            return t
        tags = set(ld.extra_tags)
        tags = tags | {args.add_tag} if args.add_tag else tags - {args.remove_tag}
        return ld._replace(extra_tags=frozenset(tags), name=ld.name + " |swap")

    rng = random.Random(args.seed)
    cands = [ld for ld in pool if matches(ld)]
    subj, twins, skipped = [], [], 0
    for ld in rng.sample(cands, min(len(cands), args.subjects * 3)):
        t = twin(ld)
        if t is None:
            skipped += 1
            continue
        subj.append(ld); twins.append(t)
        if len(subj) >= args.subjects:
            break
    if not subj:
        sys.exit(f"no builds match ({len(cands)} candidates, {skipped} swaps illegal)")
    panel = rng.sample(pool, min(len(pool), args.panel))
    mons = L._POOL_MONUMENTS
    print(f"change: {label}\nsubjects: {len(subj)} builds ({len(cands)} matched, {skipped} skipped as illegal) | panel: {len(panel)}")

    def pairs_for(builds):
        P, idx = [], []
        for i, ld in enumerate(builds):
            for op in panel:
                if op.name == ld.name.replace(" |swap", "") or (set(ld.pursuits) & set(op.pursuits) & mons):
                    continue
                P.append((ld, op)); P.append((op, ld)); idx += [(i, 0), (i, 1)]
        return P, idx

    import pandas as pd
    rows = pd.DataFrame({"retinue": [s.retinue for s in subj], "weapon": [s.weapon or "-" for s in subj],
                         "shield": [s.shield or "-" for s in subj], "armor": [s.armor for s in subj]})
    t0 = time.time()
    for tag, builds in (("orig", subj), ("twin", twins)):
        P, idx = pairs_for(builds)
        f, nrm = analytic_values(P)
        sgn = np.array([1 if side == 0 else -1 for _, side in idx])       # value is for A; flip when the build is B
        s = pd.DataFrame({"i": [i for i, _ in idx], "first": f * sgn, "later": nrm * sgn}).groupby("i").mean()
        rows[f"{tag}_first"] = s["first"].values; rows[f"{tag}_later"] = s["later"].values
    print(f"analytic done in {time.time() - t0:.0f}s")

    if args.sim:
        from multiprocessing import Pool
        t0 = time.time()
        for tag, builds in (("orig", subj), ("twin", twins)):
            P, idx = pairs_for(builds)
            blocks = [(P[k:k + 4000], args.runs, args.seed + k) for k in range(0, len(P), 4000)]
            with Pool(args.workers, initializer=_worker_init, initargs=(variant,)) as pp:
                out = pp.map(_sim_block, blocks)
            aw = np.concatenate([o[0] for o in out]); bw = np.concatenate([o[1] for o in out])
            wr = np.array([aw[k] if side == 0 else bw[k] for k, (_, side) in enumerate(idx)])
            rows[f"{tag}_wr"] = pd.DataFrame({"i": [i for i, _ in idx], "wr": wr}).groupby("i").wr.mean().values
        print(f"battles done in {time.time() - t0:.0f}s")

    rows["d_first"] = rows.twin_first - rows.orig_first
    rows["d_later"] = rows.twin_later - rows.orig_later
    cols = ["d_first", "d_later"]
    if args.sim:
        rows["d_wr"] = rows.twin_wr - rows.orig_wr
        cols.append("d_wr")
    pd.set_option("display.width", 200)
    se = lambda s: s.std(ddof=1) / max(len(s), 1) ** 0.5
    print("\n== overall (change in net casualties per Skirmish, first / later; win rate if --sim) ==")
    print("  " + "  ".join(f"{c} {rows[c].mean():+.3f} ±{se(rows[c]):.3f}" for c in cols))
    if args.sim:
        print(f"  win rate: {rows.orig_wr.mean():.3f} -> {rows.twin_wr.mean():.3f}")
    for by in ("retinue", "weapon", "shield", "armor"):
        if rows[by].nunique() > 1:
            t = rows.groupby(by)[cols].agg(["mean"]).round(3); t.columns = cols
            t.insert(0, "n", rows.groupby(by).size())
            print(f"\n== by {by} ==\n{t.sort_values(cols[-1], ascending=False).to_string()}")


if __name__ == "__main__":
    main()
