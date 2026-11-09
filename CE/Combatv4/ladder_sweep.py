#!/usr/bin/env python3
"""ladder_sweep.py — is the tier ladder wrong, or are individual items wrong?

For one gear kind (weapon / ranged / armor / shield), takes a fixed sample of builds from a saved pool and,
for EVERY item of that kind fielded in the pool, makes a twin of each build carrying that item instead
(Holdings, Retinue and the rest of the kit unchanged; structurally illegal twins are skipped). Original and
twins fight the same fixed opponent panel, so each item's value is measured on the same builds at the same
spend — the cost axis drops out.

Reading the result:
  per item   value_first / value_later = change in net casualties per Skirmish vs the build's own item
             (analytic, exact dice odds at both sides' optimal Tactic mix); d_wr = win-rate change (--sim)
  per tier   mean item value and the spread between items in that tier
  verdict    tier step (gap between neighbouring tier means) vs within-tier spread:
             steps small or negative with tight tiers  -> the ladder (tier stats vs tier cost) is off
             steps fine but tiers wide                -> individual items are off

Run from CE/:
  python Combatv4/ladder_sweep.py --kind weapon
  python Combatv4/ladder_sweep.py --kind all --sim --subjects 120 --panel 200
Output: lab_out/ladder_<kind>[_TAG]/ladder_<kind>.csv (+ printed tables)
"""
import argparse, glob, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
CE = os.path.dirname(HERE)
sys.path.insert(0, CE)
sys.path.insert(0, HERE)
import ce_paths  # noqa: E402
ce_paths.install(verbose=False)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

KINDS = {"weapon": "WEAPONS", "ranged": "RANGED", "armor": "ARMORS", "shield": "SHIELDS"}


def apply_extras(extras):
    """extras = [[DICT, item, overrides, label], ...]: add each '<item> [label]' to its dict. Returns the names."""
    import renown_data as rd
    names = []
    for d, item, over, label in extras:
        table = getattr(rd, d)
        name = f"{item} [{label}]"
        e = dict(table[item]); e.update(over)
        table[name] = e
        tier_shown = getattr(rd, "ITEM_TIER_DISPLAY", None)
        if tier_shown is not None and item in tier_shown:
            tier_shown[name] = tier_shown[item]
        names.append(name)
    return names


def strip_tags(prefixes):
    """Remove every keyword starting with one of these prefixes from all gear (e.g. 'Hook' -> a world without Hook)."""
    import renown_data as rd
    for d in KINDS.values():
        for v in getattr(rd, d).values():
            if isinstance(v, dict) and "tags" in v:
                v["tags"] = [t for t in v["tags"] if not any(str(t).startswith(p) for p in prefixes)]


def _worker_init(extras, strip=()):
    import ce_paths as _cp
    _cp.install(verbose=False)
    if strip:
        strip_tags(strip)
    if extras:
        apply_extras(extras)


_LOSS = (("strike", "killed_combat"), ("panic", "killed_waver"), ("break", "killed_shake"), ("rout", "killed_rout"))


def _sim_block_losses(args):
    """Battles for a block of pairs: win rate plus each side's own losses by cause and battle length."""
    pairs, n_runs, seed = args
    import batch_engine as BE
    res = BE.run_batch_random(pairs, n_runs=n_runs, seed=seed, mode="optimal")
    n = np.maximum(res["a_wins"] + res["b_wins"] + res["mut_wipe"] + res.get("indecisive", 0), 1)
    out = {"a_wr": res["a_wins"] / n, "b_wr": res["b_wins"] / n, "skirm": np.asarray(res["avg_skirm"], float)}
    for short, key in _LOSS:
        out["a_" + short] = np.asarray(res["avg_a_" + key], float)
        out["b_" + short] = np.asarray(res["avg_b_" + key], float)
    return out


def _tier(d, item):
    import renown_data as rd
    item = item.split(" [")[0] if item not in getattr(rd, d) else item
    shown = getattr(rd, "ITEM_TIER_DISPLAY", {}).get(item)       # label-only tiers (Arquebus = Gunpowder)
    return shown or getattr(rd, d)[item].get("tier")


def run_kind(kind, pool, args, out_dir):
    import loadouts as L
    import swap_test as ST
    from display_lab import D
    d = KINDS[kind]
    rng = random.Random(args.seed)

    # Subjects: builds that already carry an item of this kind (a swap, not an add).
    def wanted(ld):
        for w in args.where:
            neg = w.startswith("!")
            k, v = w.lstrip("!").split("=", 1)
            hit = (v in ld.pursuits) if k == "pursuit" else (str(getattr(ld, k) or "") == v)
            if hit == neg:
                return False
        if args.kit == "1h_shield" and (not ld.shield or L.is_2h(ld.weapon)):
            return False
        if args.kit == "2h" and (ld.shield or not L.is_2h(ld.weapon)):
            return False
        return True
    base = [ld for ld in pool if getattr(ld, kind) and wanted(ld)]
    subj = rng.sample(base, min(len(base), args.subjects))
    panel = rng.sample(pool, min(len(pool), args.panel))
    mons = L._POOL_MONUMENTS
    items = sorted({getattr(ld, kind) for ld in pool if getattr(ld, kind)})
    if args.items:
        items = [i for i in items if i in args.items]
    items += [n for n in args.extra_names if n.split(" [")[0] in getattr(__import__("renown_data"), d)
              and any(e[0] == d and n == f"{e[1]} [{e[3]}]" for e in args.extra_specs)]
    print(f"\n######## {kind}: {len(items)} items | subjects {len(subj)} (of {len(base)} carrying one) | panel {len(panel)}")

    def legal(t):
        t = t._replace(**{kind: getattr(t, kind).split(" [")[0]})          # a variant follows its item's rules
        w, sh = t.weapon, t.shield
        b2h = sh == "Buckler Shield" and L._true_2h(w) and "Buckler 2H" in t.extra_tags
        return b2h or L._structural_legal(w or "Farm Tools", sh, t.armor, t.ranged, t.has_tiltyard)

    def pairs_for(builds, orig_names):
        P, idx = [], []
        for i, (ld, on) in enumerate(zip(builds, orig_names)):
            for op in panel:
                if op.name == on or (set(ld.pursuits) & set(op.pursuits) & mons):
                    continue
                P.append((ld, op)); P.append((op, ld)); idx += [(i, 0), (i, 1)]
        return P, idx

    def measure(builds, orig_names):
        P, idx = pairs_for(builds, orig_names)
        f, nrm = ST.analytic_values(P)
        sgn = np.array([1 if side == 0 else -1 for _, side in idx])
        s = pd.DataFrame({"i": [i for i, _ in idx], "first": f * sgn, "later": nrm * sgn}).groupby("i").mean()
        out = {"first": s["first"].values, "later": s["later"].values}
        if args.sim:
            from multiprocessing import Pool
            blocks = [(P[k:k + 4000], args.runs, args.seed + k) for k in range(0, len(P), 4000)]
            with Pool(args.workers, initializer=_worker_init, initargs=(args.extra_specs, tuple(args.strip_tag))) as pp:
                res = pp.map(_sim_block_losses, blocks)
            cat = {k: np.concatenate([o[k] for o in res]) for k in res[0]}
            own = lambda f: np.array([cat["a_" + f][k] if side == 0 else cat["b_" + f][k] for k, (_, side) in enumerate(idx)])
            cols = {"wr": own("wr"), "skirm": cat["skirm"]}
            for short, _ in _LOSS:
                cols["lost_" + short] = own(short)
            g = pd.DataFrame({"i": [i for i, _ in idx], **cols}).groupby("i").mean()
            for c in cols:
                out[c] = g[c].values
        return out

    t0 = time.time()
    orig = measure(subj, [s.name for s in subj])
    print(f"  baseline done ({time.time() - t0:.0f}s)")

    rows = []
    for it in items:
        keep, twins = [], []
        for i, ld in enumerate(subj):
            t = ld._replace(**{kind: it}, name=ld.name + " |ladder")
            if args.drop_shield_2h and kind == "weapon" and L.is_2h(it.split(" [")[0]):
                t = t._replace(shield=None)                                 # 2H twin puts the shield down
            if args.add_shield_1h and kind == "weapon" and not L.is_2h(it.split(" [")[0]) and not t.shield:
                t = t._replace(shield=args.add_shield_1h)                   # 1H twin picks a shield up
            if legal(t):
                keep.append(i); twins.append(t)
        if len(keep) < args.min_n:
            print(f"  {it:<18} skipped: {len(keep)} legal twins (< {args.min_n})")
            continue
        t1 = time.time()
        tw = measure(twins, [subj[i].name for i in keep])
        k = np.array(keep)
        r = {"kind": kind, "item": it, "item_shown": D(it), "tier": D(_tier(d, it) or "none"), "n": len(keep),
             "own_share": float(np.mean([subj[i].__getattribute__(kind) == it for i in keep]))}
        for m in ("first", "later") + (("wr",) if args.sim else ()):
            dv = tw[m] - orig[m][k]
            col = {"first": "value_first", "later": "value_later", "wr": "d_wr"}[m]
            r[col] = dv.mean(); r[col + "_se"] = dv.std(ddof=1) / max(len(dv), 1) ** 0.5
        if args.sim:                                   # own losses by cause and battle length: twin minus original
            for c in ["skirm"] + ["lost_" + sh for sh, _ in _LOSS]:
                r["d_" + c] = float((tw[c] - orig[c][k]).mean())
        rows.append(r)
        print(f"  {it:<18} n={len(keep):<4} later {r['value_later']:+.3f}"
              + (f"  wr {r['d_wr']:+.3f}" if args.sim else "") + f"  ({time.time() - t1:.0f}s)")

    df = pd.DataFrame(rows)
    key = "d_wr" if args.sim else "value_later"
    df = df.sort_values(key, ascending=False).reset_index(drop=True)
    df.to_csv(os.path.join(out_dir, f"ladder_{kind}.csv"), index=False)

    pd.set_option("display.width", 220)
    show = ["item_shown", "tier", "n", "value_first", "value_later"] + (
        ["d_wr", "d_lost_strike", "d_lost_panic", "d_lost_break", "d_lost_rout", "d_skirm"] if args.sim else [])
    print(f"\n== {kind}: item value on the same builds ({key} sorted) ==\n{df[show].round(3).to_string(index=False)}")

    import loadouts as L2
    order = {D(t): i for i, t in enumerate(L2.TIER_ORDER)}
    g = df.groupby("tier")[key].agg(["count", "mean", "std", "min", "max"])
    g["rank"] = [order.get(t, -1) for t in g.index]
    g = g.sort_values("rank").drop(columns="rank")
    g["step"] = g["mean"].diff()
    print(f"\n== {kind}: by tier ({key}) ==\n{g.round(3).to_string()}")
    steps = g["step"].dropna()
    spread = g["std"].dropna()
    if len(steps) and len(spread):
        bad_steps = int((steps <= 0).sum())
        print(f"\n  tier steps <= 0: {bad_steps} of {len(steps)} | mean |step| {steps.abs().mean():.3f}"
              f" vs mean within-tier spread {spread.mean():.3f}")
        if bad_steps and spread.mean() < steps.abs().mean():
            print("  -> tiers are tight but out of order: the ladder (tier stats for their cost) looks off.")
        elif spread.mean() > steps.abs().mean():
            print("  -> items spread wider than the tier steps: individual items matter more than the ladder.")
        else:
            print("  -> ladder in order and tiers fairly tight.")
    return df


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kind", default="weapon", choices=list(KINDS) + ["all"])
    ap.add_argument("--pool", default=None, help="pool CSV (default: newest in lab_out/_pool_cache)")
    ap.add_argument("--subjects", type=int, default=200)
    ap.add_argument("--panel", type=int, default=300)
    ap.add_argument("--min-n", type=int, default=15, help="skip items with fewer legal twins than this")
    ap.add_argument("--sim", action="store_true", help="also run full battles (win rate; much slower)")
    ap.add_argument("--runs", type=int, default=25)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--tag", default="")
    ap.add_argument("--where", action="append", default=[],
                    help="subject filter field=value (retinue/weapon/shield/armor/ranged/pursuit); prefix ! to exclude")
    ap.add_argument("--kit", choices=["any", "1h_shield", "2h"], default="any",
                    help="1h_shield: subjects are 1H + shield builds only; 2h: 2H builds without a shield only")
    ap.add_argument("--add-shield-1h", default=None, help="a 1H weapon twin of a shieldless build picks up this shield (reverse kit swap)")
    ap.add_argument("--drop-shield-2h", action="store_true", help="a 2H weapon twin also drops the build's shield (kit swap)")
    ap.add_argument("--strip-tag", action="append", default=[],
                    help="remove keywords starting with this from all gear and every build, e.g. Hook (whole field)")
    ap.add_argument("--items", nargs="+", default=None, help="only these pool items (default: all fielded)")
    ap.add_argument("--extra", nargs=3, action="append", default=[], metavar=("ITEM", "JSON", "LABEL"),
                    help="test variant of an item of --kind, e.g. --extra \"Cavalry Spear\" '{\"ap\": -2}' ap2")
    args = ap.parse_args()

    import json
    import loadouts as L
    if args.extra and args.kind == "all":
        sys.exit("--extra needs a single --kind")
    args.extra_specs = [[KINDS[args.kind], it, json.loads(js), lab] for it, js, lab in args.extra]
    args.extra_names = apply_extras(args.extra_specs)
    pool_path = args.pool or max(glob.glob(os.path.join(CE, "lab_out", "_pool_cache", "*.csv")), key=os.path.getmtime)
    pool = L._load_loadouts_from_csv(pool_path)
    if args.strip_tag:
        strip_tags(args.strip_tag)
        sp = tuple(args.strip_tag)
        pool = [ld._replace(extra_tags=frozenset(t for t in ld.extra_tags if not str(t).startswith(sp))) for ld in pool]
        print(f"stripped from all gear and builds: {', '.join(args.strip_tag)}")
    print(f"pool: {pool_path} ({len(pool)} builds)")
    kinds = list(KINDS) if args.kind == "all" else [args.kind]
    for k in kinds:
        out_dir = os.path.join(CE, "lab_out", f"ladder_{k}" + (f"_{args.tag}" if args.tag else ""))
        os.makedirs(out_dir, exist_ok=True)
        run_kind(k, pool, args, out_dir)
        print(f"  -> {out_dir}")


if __name__ == "__main__":
    main()
