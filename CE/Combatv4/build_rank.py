"""build_rank.py — find, group and explain the top-performing builds of a tournament run.

Reads the tournament outputs (summary{suffix}.csv + matchups{suffix}.parquet) and produces:

  builds(S)                    one row per build: TI (Holdings, + Domain points if include_domain),
                               core Holdings, weapon keywords, family key
  head_to_head(M, names)       build x build win-share matrix (both seatings combined)
  rank(S, M)                   per build: win rate, TI-adjusted edge (vs builds at the same TI),
                               robustness (worst-decile matchup, hard counters, share of field beaten),
                               win rate vs the top quartile
  families(R)                  builds grouped by Retinue + core Holdings + weapon keywords
  strengths(R, M, name)        what one build beats / loses to, by opponent attribute
  archetypes(R, H, k)          builds clustered by matchup profile; each cluster's defining features,
                               strengths and weaknesses, and the cluster-vs-cluster win table
  attribute_table(S)           the investment-controlled attribute harness with collinear rows merged
                               (Crit 8 + Immune Strained -> one Royal Pavilion row, etc.)
  export_explorer(R, H, path)  self-contained HTML build explorer

TI = total investment = Holdings in the build; include_domain=True adds the Domain points its standings
cost (Rising 3 / Established 6 / Sovereign 10 per Domain, from renown_data.STANDING_THRESHOLDS).
"""
import json
import re
import warnings

import numpy as np
import pandas as pd

WR = "win_rate"
warnings.filterwarnings("ignore", message="(Mean of empty slice|All-NaN slice)")


# ── build table ────────────────────────────────────────────────────────────────────────────────────
def _loadouts():
    import loadouts as L
    return L


def _holding_info():
    """{Holding: (is_combat, is_gear_only)} from HOLDING_SIM."""
    L = _loadouts()
    out = {}
    for n, h in L._SIM.items():
        eng = [t for t in h["tags"] if not (t.startswith(L._INFO_PREFIX) or t in L._INFO_EXACT)]
        out[n] = bool(eng)
    return out


def _weapon_kw(weapon, ranged):
    import renown_data as rd
    k = set()
    for name, table in ((weapon, rd.WEAPONS), (ranged, rd.RANGED)):
        if isinstance(name, str) and name in table:
            k |= set(table[name].get("tags", []))
    return k


SIGNATURE_KW = ["Deadly", "Cleave", "Unstoppable", "Destroy Shield", "Negate Shielded", "Steady", "Unwieldy",
                "One-Shot", "2H", "Awkward", "Crude"]


def builds(S, include_domain=True):
    """One row per build with TI, core Holdings, keyword signature and family key."""
    L = _loadouts()
    combat = _holding_info()
    flor = {h for h, d in L._SIM.items() if "Florentine" in d["tags"]}
    T = S.copy()
    for c in ("shield", "ranged", "pursuits", "tags"):
        if c in T.columns:
            T[c] = T[c].astype(object).where(T[c].notna(), "")
    cache = {}

    def per(p):
        if p not in cache:
            P = frozenset(x for x in str(p).split("|") if x)
            _, dom, _ = L.compute_pursuit_cost(P)
            core = sorted(h for h in P if combat.get(h) and h not in flor) + sorted(h for h in P if h in flor)
            cache[p] = (len(P), int(sum(dom.values())), " + ".join(core) or "(no combat Holdings)",
                        sum(1 for h in P if L._SIM.get(h, {}).get("monument")))
        return cache[p]

    vals = T["pursuits"].map(per)
    T["total_investment"] = vals.map(lambda v: v[0])
    T["domain_points"] = vals.map(lambda v: v[1])
    T["ti"] = T["total_investment"] + (T["domain_points"] if include_domain else 0)
    T["core"] = vals.map(lambda v: v[2])
    T["monuments"] = vals.map(lambda v: v[3])
    kw = [_weapon_kw(w, r) for w, r in zip(T["weapon"], T["ranged"])]
    T["weapon_kw"] = [",".join(k for k in SIGNATURE_KW if k in s) for s in kw]
    T["dual_wield"] = T["tags"].str.contains("Dual Wield", regex=False)
    T["gear"] = (T["weapon"].fillna("").astype(str) + np.where(T["dual_wield"], " x2", "")
                 + np.where(T["shield"] != "", " / " + T["shield"].astype(str), "")
                 + np.where(T["ranged"] != "", " + " + T["ranged"].astype(str), "") + " / " + T["armor"].astype(str))
    T["family"] = T["retinue"].astype(str) + " | " + T["core"] + " | " + T["weapon_kw"].replace("", "-")
    return T


# ── head-to-head ──────────────────────────────────────────────────────────────────────────────────
def head_to_head(M, names=None):
    """(H, N) — H[i, j] = build i's win share against build j over both seatings (NaN = never met),
    N[i, j] = decisive battles behind it."""
    a = M["a_name"].astype(str).to_numpy(); b = M["b_name"].astype(str).to_numpy()
    if names is None:
        names = sorted(set(a) | set(b))
    idx = {n: i for i, n in enumerate(names)}
    ia = np.array([idx.get(x, -1) for x in a]); ib = np.array([idx.get(x, -1) for x in b])
    ok = (ia >= 0) & (ib >= 0)
    ia, ib = ia[ok], ib[ok]
    aw = M["a_wins"].to_numpy(float)[ok]; bw = M["b_wins"].to_numpy(float)[ok]
    n = len(names)
    W = np.zeros((n, n)); D = np.zeros((n, n))
    np.add.at(W, (ia, ib), aw); np.add.at(W, (ib, ia), bw)
    np.add.at(D, (ia, ib), aw + bw); np.add.at(D, (ib, ia), aw + bw)
    with np.errstate(invalid="ignore", divide="ignore"):
        H = np.where(D > 0, W / D, np.nan)
    np.fill_diagonal(H, np.nan)
    return pd.DataFrame(H, index=names, columns=names), pd.DataFrame(D, index=names, columns=names)


# ── ranking ────────────────────────────────────────────────────────────────────────────────────────
def rank(S, M, include_domain=True, ti_band=2, counter_thr=0.35, top_q=0.75):
    """Per-build ranking table. Columns:
       win_rate        overall
       ti_edge         win rate minus the mean of builds within +-ti_band TI (the budget-fair edge)
       ti_pct          percentile of win rate among those same-budget builds
       vs_top          win share against the top quartile of the field (by win rate)
       worst_decile    win share at this build's 10th-percentile matchup (robustness: how bad its bad days are)
       hard_counters   share of opponents it wins < counter_thr against
       field_beaten    share of opponents it beats (> 0.5)
       robust          mean of the ranks of worst_decile, field_beaten and (1 - hard_counters), 0-1
    Returns (R, H)."""
    T = builds(S, include_domain=include_domain)
    names = T["name"].astype(str).tolist()
    seen = set(M["a_name"].astype(str)) | set(M["b_name"].astype(str))
    miss = sum(1 for n in names if n not in seen)
    if miss:
        import warnings
        warnings.warn(f"{miss} of {len(names)} summary builds never appear in the matchups — "
                      "are summary and matchups from the same run?")
    H, D = head_to_head(M, names)
    Hv = H.to_numpy()
    T = T.set_index(T["name"].astype(str))
    wr = T[WR].to_numpy(float)
    ti = T["ti"].to_numpy(float)
    near = np.abs(ti[:, None] - ti[None, :]) <= ti_band
    T["ti_edge"] = wr - (near * wr[None, :]).sum(1) / near.sum(1)
    T["ti_pct"] = [(wr[near[i]] < wr[i]).mean() for i in range(len(wr))]
    top = wr >= np.quantile(wr, top_q)
    with np.errstate(invalid="ignore"):
        T["vs_top"] = np.nanmean(np.where(top[None, :], Hv, np.nan), axis=1)
        T["worst_decile"] = np.nanquantile(Hv, 0.10, axis=1)
        met = (~np.isnan(Hv)).sum(1)
        T["hard_counters"] = (np.nan_to_num(Hv, nan=1) < counter_thr).sum(1) / np.maximum(1, met)
        T["field_beaten"] = (np.nan_to_num(Hv, nan=0) > 0.5).sum(1) / np.maximum(1, met)
    pr = lambda s: s.rank(pct=True)
    T["robust"] = (pr(T["worst_decile"]) + pr(T["field_beaten"]) + pr(-T["hard_counters"])) / 3
    T["opponents_met"] = met
    return T.reset_index(drop=True), H


RANK_COLS = ["name", "retinue", "gear", "core", "ti", "win_rate", "ti_edge", "ti_pct", "vs_top",
             "worst_decile", "hard_counters", "field_beaten", "robust"]


def top_builds(R, by="win_rate", n=25, min_ti=None, max_ti=None, retinue=None, per_family=1):
    """Top builds by a column; per_family caps how many builds of one family appear (None = no cap)."""
    X = R
    if min_ti is not None:
        X = X[X["ti"] >= min_ti]
    if max_ti is not None:
        X = X[X["ti"] <= max_ti]
    if retinue is not None:
        X = X[X["retinue"] == retinue]
    X = X.sort_values(by, ascending=False)
    if per_family:
        X = X.groupby("family", sort=False).head(per_family)
    return X[RANK_COLS + ["family"]].head(n).round(3)


def best_per_ti(R, by="win_rate"):
    """The best build at each TI value, with its robustness."""
    i = R.groupby("ti")[by].idxmax()
    return R.loc[i, RANK_COLS].set_index("ti").round(3)


def families(R, min_n=1):
    """Builds grouped by Retinue + core Holdings + weapon keywords."""
    g = R.groupby("family")
    F = pd.DataFrame({
        "n": g.size(), "retinue": g["retinue"].first(), "core": g["core"].first(), "weapon_kw": g["weapon_kw"].first(),
        "ti_min": g["ti"].min(), "ti_max": g["ti"].max(),
        "best_wr": g[WR].max(), "median_wr": g[WR].median(), "mean_ti_edge": g["ti_edge"].mean(),
        "best_robust": g["robust"].max(),
        "best_build": g.apply(lambda d: d.loc[d[WR].idxmax(), "gear"]),
    })
    return F[F["n"] >= min_n].sort_values("mean_ti_edge", ascending=False).round(3)


# ── strengths / weaknesses ─────────────────────────────────────────────────────────────────────────
def _opp_features(R):
    """Boolean opponent classes used to describe matchups (all read from the build row)."""
    import renown_data as rd
    f = {}
    for a in sorted(R["armor"].dropna().unique()):
        f[f"armor: {a}"] = R["armor"] == a
    for r in sorted(R["retinue"].unique()):
        f[f"retinue: {r}"] = R["retinue"] == r
    f["shield"] = R["shield"] != ""
    f["no shield"] = R["shield"] == ""
    f["ranged"] = R["ranged"] != ""
    kw = R["weapon_kw"].str.split(",")
    for k in SIGNATURE_KW:
        f[f"weapon: {k}"] = kw.map(lambda s, k=k: k in s)
    tags = R["tags"].astype(str)
    for t in ("Parry", "Riposte", "Poison", "Riveted", "Serrated", "Crit 8", "Immune Panic", "Drilled",
              "Nimble", "Outrider: every", "Immune Blunder", "Dual Wield"):
        f[f"has {t}"] = tags.str.contains(re.escape(t))
    f["Recover"] = tags.str.contains(r"Recover \d")
    f["Seize (Ministry)"] = tags.str.contains("Seize")
    return pd.DataFrame(f, index=R.index)


def strengths(R, H, name, min_n=8, top=6):
    """What one build does better / worse against than its own average, by opponent class.
    Returns (table, text)."""
    i = R.index[R["name"] == name][0]
    row = H.loc[name].reindex(R["name"]).to_numpy()
    base = np.nanmean(row)
    F = _opp_features(R)
    rows = []
    for c in F.columns:
        m = F[c].to_numpy() & ~np.isnan(row)
        if m.sum() < min_n:
            continue
        v = row[m].mean()
        se = row[m].std(ddof=1) / np.sqrt(m.sum()) if m.sum() > 1 else np.nan
        rows.append({"opponent": c, "n": int(m.sum()), "win_share": v, "vs_own_avg": v - base, "se": se})
    T = pd.DataFrame(rows)
    if T.empty:
        return T, ""
    T = T[np.abs(T["vs_own_avg"]) > 2 * T["se"].fillna(0)].sort_values("vs_own_avg", ascending=False)
    st = T[T["vs_own_avg"] > 0].head(top); wk = T[T["vs_own_avg"] < 0].tail(top).iloc[::-1]
    fmt = lambda d: ", ".join(f"{r.opponent} ({r.win_share:.0%})" for r in d.itertuples()) or "-"
    from display_lab import D
    text = D(f"{R.loc[i, 'retinue']} {R.loc[i, 'gear']} [{R.loc[i, 'core']}]  avg {base:.0%}\n"
             f"  strong vs: {fmt(st)}\n  weak vs:   {fmt(wk)}")
    return T.round(3), text


def build_features(R):
    """What a build IS (own-side features), for describing clusters."""
    F = _opp_features(R).copy()
    F.columns = [c.replace("has ", "") for c in F.columns]
    for b in sorted(R["ti"].unique()):
        pass
    q = R["ti"].quantile([0.33, 0.66]).to_numpy()
    F["low TI"] = R["ti"] <= q[0]
    F["high TI"] = R["ti"] > q[1]
    for h in sorted({x for c in R["core"] for x in c.split(" + ") if x and not x.startswith("(")}):
        F[f"Holding: {h}"] = R["core"].str.contains(re.escape(h))
    return F


def _kmeans(X, k, seed=0, iters=60):
    rng = np.random.default_rng(seed)
    C = X[rng.choice(len(X), k, replace=False)]
    for _ in range(iters):
        d = ((X[:, None, :] - C[None]) ** 2).sum(-1)
        lab = d.argmin(1)
        newC = np.array([X[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
        if np.allclose(newC, C):
            break
        C = newC
    return lab


def archetypes(R, H, k=8, seed=0, top_features=5, show=True):
    """Cluster builds by matchup profile (who they beat), then describe each cluster.
    Returns dict(summary, matrix, labels): summary = per-cluster size, win rate, defining features (most
    over-represented vs the field), strongest and weakest opponent clusters; matrix = cluster-vs-cluster
    mean win share (row vs column)."""
    names = R["name"].tolist()
    Hv = H.reindex(index=names, columns=names).to_numpy()
    X = np.where(np.isnan(Hv), np.nanmean(Hv, axis=1, keepdims=True), Hv)
    X = X - X.mean(1, keepdims=True)                 # profile shape, not overall strength
    lab = _kmeans(X, k, seed)
    F = build_features(R)
    field = F.mean()
    Mx = np.full((k, k), np.nan)
    for i in range(k):
        for j in range(k):
            blk = Hv[np.ix_(lab == i, lab == j)]
            if np.isfinite(blk).any():
                Mx[i, j] = np.nanmean(blk)
    rows = []
    for c in range(k):
        m = lab == c
        if not m.any():
            continue
        lift = (F[m].mean() - field).sort_values(ascending=False)
        lift = lift[(F[m].mean() >= 0.5) & (lift > 0.15)].head(top_features)
        opp = pd.Series(Mx[c], index=range(k)).drop(c, errors="ignore").dropna()
        best = R.loc[m].sort_values(WR, ascending=False).iloc[0]
        rows.append({"cluster": c, "n": int(m.sum()), "mean_wr": R.loc[m, WR].mean(),
                     "is": ", ".join(lift.index) or "(mixed)",
                     "beats": ", ".join(f"C{j} ({v:.0%})" for j, v in opp.sort_values(ascending=False).head(2).items()),
                     "loses to": ", ".join(f"C{j} ({v:.0%})" for j, v in opp.sort_values().head(2).items()),
                     "best build": f"{best['retinue']} {best['gear']} [{best['core']}] {best[WR]:.0%}"})
    summ = pd.DataFrame(rows).set_index("cluster").round(3)
    mat = pd.DataFrame(Mx, index=[f"C{i}" for i in range(k)], columns=[f"C{i}" for i in range(k)]).round(2)
    if show:
        _show("Archetypes (clustered by who they beat)", summ)
        _show("Archetype vs archetype (row win share)", mat)
    return {"summary": summ, "matrix": mat, "labels": pd.Series(lab, index=R.index, name="archetype")}


# ── attribute harness with redundant rows merged ──────────────────────────────────────────────────
def _tag_sources():
    """{engine tag: [Holding / Standing]} to label merged keyword rows."""
    import parser_audit as PA
    return PA.token_sources()


def attribute_table(S, include_domain=True, qbands=4, min_n=3, show=True):
    """The notebook's full-dictionary sensitivity harness (ctrl_prem = edge with spend held fixed),
    with every group of rows that select exactly the same builds merged into one row.
    Merging catches what always travels together in the pool — e.g. Crit 8 / Immune Strained / Parry +1
    (all Royal Pavilion), Gothic Plate / Crafted armor / save 3 / Planishing (Court Armoury), a weapon and
    its own AP value. `source` names the Holding (or Standing) that grants a keyword."""
    import renown_data as rd
    T = builds(S, include_domain=include_domain)
    inv = "ti"
    pool_wr = T[WR].mean(); pool_inv = T[inv].mean()
    T["_band"] = pd.qcut(T[inv], qbands, duplicates="drop")
    band_wr = T.groupby("_band", observed=True)[WR].mean()
    src = _tag_sources()

    def ctrl(mask):
        sub = T[mask]
        if len(sub) < min_n:
            return None
        num = den = 0.0
        for b, s in sub.groupby("_band", observed=True):
            if len(s) < 3:
                continue
            num += len(s) * (s[WR].mean() - band_wr[b]); den += len(s)
        cp = num / den if den else np.nan
        return dict(n=len(sub), wr=sub[WR].mean(), naive=sub[WR].mean() - pool_wr, ctrl_prem=cp,
                    d_inv=sub[inv].mean() - pool_inv, confound=(sub[WR].mean() - pool_wr) - cp)

    items = []                                                  # (label, kind, mask)
    DICT_COL = {"WEAPONS": "weapon", "RANGED": "ranged", "SHIELDS": "shield", "ARMORS": "armor"}
    for dname, col in DICT_COL.items():
        D = getattr(rd, dname)
        for v in sorted(x for x in T[col].dropna().unique() if str(x) not in ("", "nan", "None")):
            items.append((f"{col}: {v}", "item", (T[col] == v).to_numpy()))
        sample = next((v for v in D.values() if isinstance(v, dict)), {})
        for f in [k for k in sample if k not in ("tags", "note", "profile_2h", "requires", "tactics_allowed")]:
            cv = T[col].map(lambda x, f=f, D=D: D.get(x, {}).get(f, np.nan) if x in D else np.nan)
            for v in cv.dropna().unique():
                items.append((f"{col}.{f} = {v}", "field", (cv == v).to_numpy()))

    def tagset(r):
        s = set()
        for dname, col in DICT_COL.items():
            D = getattr(rd, dname); x = r[col]
            if x in D:
                s |= set(map(str, D[x].get("tags", [])))
        s |= {t.strip() for t in str(r["tags"]).split(",") if t.strip()}
        return s
    ts = T.apply(tagset, axis=1)
    for t in sorted({t for s in ts for t in s}):
        items.append((t, "keyword", ts.map(lambda s, t=t: t in s).to_numpy()))
    for v in sorted(T["retinue"].unique()):
        items.append((f"retinue: {v}", "retinue", (T["retinue"] == v).to_numpy()))
    for h in sorted({x for c in T["core"] for x in c.split(" + ") if x and not x.startswith("(")}):
        items.append((f"Holding: {h}", "holding", T["pursuits"].str.split("|").map(lambda p, h=h: h in p).to_numpy()))

    groups = {}
    for label, kind, m in items:
        if m.sum() < min_n:
            continue
        groups.setdefault(m.tobytes(), []).append((label, kind, m))
    order = {"holding": 0, "keyword": 1, "item": 2, "retinue": 3, "field": 4}
    rows = []
    for _, g in groups.items():
        g = sorted(g, key=lambda x: (order[x[1]], x[0]))
        r = ctrl(g[0][2])
        if r is None:
            continue
        kws = [x[0] for x in g if x[1] == "keyword"]
        sources = sorted({s for k in kws for s in src.get(k, [])})
        rows.append({"variable": g[0][0], "same builds as": ", ".join(x[0] for x in g[1:]),
                     "source": ", ".join(sources), "kind": g[0][1], **r})
    out = pd.DataFrame(rows).sort_values("ctrl_prem", ascending=False, na_position="last").reset_index(drop=True)
    num = ["wr", "naive", "ctrl_prem", "d_inv", "confound"]
    out[num] = out[num].round(3)
    if show:
        print(f"variables: {len(items)} -> {len(out)} after merging rows that select the same builds "
              f"| investment axis: TI{' + Domain points' if include_domain else ''}")
        with pd.option_context("display.max_rows", None, "display.width", 250, "display.max_colwidth", 70):
            _show("Attributes by real edge (ctrl_prem); merged rows listed in 'same builds as'", out)
    return out


# ── HTML explorer ──────────────────────────────────────────────────────────────────────────────────
def export_explorer(R, H, path, title="Build Explorer", arche=None, n_matchups=12):
    """Write a self-contained HTML build explorer (no network). Per build: gear, Holdings, keywords,
    ranking columns, best / worst matchups, strengths / weaknesses; filters for Retinue, TI, text."""
    names = R["name"].tolist()
    Hv = H.reindex(index=names, columns=names).to_numpy()
    F = _opp_features(R)
    Fm = F.to_numpy()
    fcols = list(F.columns)
    builds_js = []
    for i, r in R.reset_index(drop=True).iterrows():
        row = Hv[i]
        ok = ~np.isnan(row)
        order = np.argsort(np.where(ok, row, np.nan))
        valid = [j for j in order if ok[j]]
        base = np.nanmean(row) if ok.any() else np.nan
        sw = []
        for c, col in enumerate(fcols):
            m = Fm[:, c] & ok
            if m.sum() >= 8:
                v = row[m].mean(); se = row[m].std(ddof=1) / np.sqrt(m.sum())
                if abs(v - base) > 2 * se:
                    sw.append([col, round(float(v), 3), round(float(v - base), 3)])
        sw.sort(key=lambda x: -x[2])
        builds_js.append({
            "i": int(i), "name": r["name"], "ret": r["retinue"], "gear": r["gear"], "core": r["core"],
            "pursuits": [p for p in str(r["pursuits"]).split("|") if p], "tags": str(r["tags"]),
            "ti": int(r["ti"]), "hold": int(r["total_investment"]), "dom": int(r["domain_points"]),
            "wr": _r(r[WR]), "edge": _r(r["ti_edge"]), "pct": _r(r["ti_pct"]), "top": _r(r["vs_top"]),
            "worst": _r(r["worst_decile"]), "ctr": _r(r["hard_counters"]), "beat": _r(r["field_beaten"]),
            "rob": _r(r["robust"]), "fam": r["family"],
            "arch": (int(arche["labels"].iloc[i]) if arche is not None else None),
            "best": [[int(j), _r(row[j])] for j in valid[::-1][:n_matchups]],
            "worstm": [[int(j), _r(row[j])] for j in valid[:n_matchups]],
            "strong": [x for x in sw if x[2] > 0][:6], "weak": [x for x in sw if x[2] < 0][-6:][::-1],
        })
    payload = {"builds": builds_js}
    if arche is not None:
        payload["arch"] = {"summary": arche["summary"].reset_index().to_dict("records"),
                           "matrix": arche["matrix"].to_dict("split")}
    from display_lab import disp_obj, D
    payload = disp_obj(payload)                     # NAME_DISPLAY on everything the page shows
    html = _EXPLORER.replace("__TITLE__", D(title)).replace("__DATA__", json.dumps(payload, default=_jsd))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


def _r(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), 3)


def _jsd(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    return str(o)


def _show(title, df):
    """Show a table with NAME_DISPLAY applied (ids in the frame itself stay canonical)."""
    from display_lab import disp_df, D
    df = disp_df(df) if hasattr(df, "columns") else df
    try:
        from IPython.display import display, Markdown
        display(Markdown(f"**{D(title)}**"))
        display(df)
    except Exception:
        print(f"\n== {D(title)}\n{df.to_string()}")


_EXPLORER = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#f7f7f5;--panel:#fff;--ink:#1d1d1b;--mute:#6b6b66;--line:#e2e1dc;--acc:#2f5d8a;--good:#2e7d4f;--bad:#b23b3b;--sel:#eaf1f8}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#151514;--panel:#1e1e1c;--ink:#ecebe6;--mute:#9a9a93;--line:#33332f;--acc:#7fb0de;--good:#6cc493;--bad:#e27b7b;--sel:#22303d}}
:root[data-theme="dark"]{--bg:#151514;--panel:#1e1e1c;--ink:#ecebe6;--mute:#9a9a93;--line:#33332f;--acc:#7fb0de;--good:#6cc493;--bad:#e27b7b;--sel:#22303d}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:13px/1.4 system-ui,-apple-system,Segoe UI,sans-serif}
header{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--line);background:var(--panel);position:sticky;top:0;z-index:2}
header h1{font-size:15px;margin:0 12px 0 0}input,select{font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:4px 6px}
nav button{font:inherit;background:none;border:1px solid var(--line);color:var(--ink);border-radius:6px;padding:4px 10px;cursor:pointer}nav button.on{background:var(--acc);color:var(--panel);border-color:var(--acc)}
main{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:12px;padding:12px 16px}
@media (max-width:900px){main{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.scroll{overflow:auto;max-height:calc(100vh - 110px)}table{border-collapse:collapse;width:100%}
th,td{padding:4px 6px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap;font-variant-numeric:tabular-nums}
th{position:sticky;top:0;background:var(--panel);cursor:pointer;user-select:none;color:var(--mute);font-weight:600}
td.n,th.n{text-align:right}tr.row{cursor:pointer}tr.row:hover,tr.sel{background:var(--sel)}
td.wrap{white-space:normal;min-width:180px}.d{padding:12px}.d h2{font-size:14px;margin:0 0 4px}.mute{color:var(--mute)}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:10px 0}.k{border:1px solid var(--line);border-radius:6px;padding:6px}.k b{display:block;font-size:15px}
.pill{display:inline-block;border:1px solid var(--line);border-radius:10px;padding:1px 7px;margin:2px 2px 0 0}
.g{color:var(--good)}.b{color:var(--bad)}h3{font-size:12px;margin:12px 0 4px;color:var(--mute);text-transform:uppercase;letter-spacing:.04em}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}@media (max-width:520px){.two{grid-template-columns:1fr}.grid{grid-template-columns:repeat(2,1fr)}}
.hide{display:none}
</style></head><body>
<header><h1>__TITLE__</h1>
<nav><button data-v="builds" class="on">Builds</button> <button data-v="fam">Families</button> <button data-v="arch">Archetypes</button></nav>
<input id="q" placeholder="search gear / Holding / keyword" size="28">
<select id="ret"><option value="">all Retinues</option></select>
<label>TI <input id="tmin" type="number" style="width:56px"> – <input id="tmax" type="number" style="width:56px"></label>
<label><input id="fam1" type="checkbox"> best per family</label>
<span id="cnt" class="mute"></span></header>
<main><section class="card scroll" id="left"></section><section class="card scroll" id="right"><div class="d mute">Select a build.</div></section></main>
<script>
const D=__DATA__,B=D.builds;let view="builds",sortK="wr",sortD=-1,sel=null;
const pc=v=>v==null?"–":(100*v).toFixed(0)+"%",sg=v=>v==null?"–":(v>=0?"+":"")+(100*v).toFixed(1);
const $=id=>document.getElementById(id);
[...new Set(B.map(b=>b.ret))].sort().forEach(r=>{const o=document.createElement("option");o.textContent=r;$("ret").appendChild(o)});
const cols=[["gear","Gear",0],["ret","Retinue",0],["core","Core Holdings",0,"wrap"],["ti","TI",1],["wr","Win",2],["edge","TI edge",3],["top","vs top",2],["worst","Worst 10%",2],["ctr","Countered",2],["rob","Robust",2]];
function filt(){const q=$("q").value.toLowerCase(),r=$("ret").value,a=+$("tmin").value||-1e9,z=+$("tmax").value||1e9;
 let x=B.filter(b=>(!r||b.ret==r)&&b.ti>=a&&b.ti<=z&&(!q||(b.gear+" "+b.core+" "+b.tags+" "+b.pursuits.join(" ")).toLowerCase().includes(q)));
 x.sort((p,s)=>((p[sortK]??-1e9)>(s[sortK]??-1e9)?1:-1)*sortD);
 if($("fam1").checked){const seen=new Set;x=x.filter(b=>!seen.has(b.fam)&&seen.add(b.fam))}return x}
function fmt(c,b){const v=b[c[0]];return c[2]==2?pc(v):c[2]==3?sg(v):v}
function drawBuilds(){const x=filt();$("cnt").textContent=x.length+" builds";
 let h="<table><tr>"+cols.map(c=>`<th class="${c[2]?"n":""}" data-k="${c[0]}">${c[1]}${sortK==c[0]?(sortD<0?" ▾":" ▴"):""}</th>`).join("")+"</tr>";
 h+=x.slice(0,600).map(b=>`<tr class="row${sel==b.i?" sel":""}" data-i="${b.i}">`+cols.map(c=>`<td class="${c[2]?"n":""} ${c[3]||""}">${fmt(c,b)}</td>`).join("")+"</tr>").join("");
 $("left").innerHTML=h+"</table>";}
function drawFam(){const g={};filt().forEach(b=>{(g[b.fam]=g[b.fam]||[]).push(b)});
 const rows=Object.entries(g).map(([f,a])=>{a.sort((p,s)=>s.wr-p.wr);return{f,n:a.length,best:a[0],med:a[Math.floor(a.length/2)].wr,edge:a.reduce((s,b)=>s+b.edge,0)/a.length}}).sort((p,s)=>s.edge-p.edge);
 $("cnt").textContent=rows.length+" families";
 $("left").innerHTML="<table><tr><th>Family (Retinue | core Holdings | weapon keywords)</th><th class=n>Builds</th><th class=n>Best</th><th class=n>Median</th><th class=n>Mean TI edge</th></tr>"+
 rows.map(r=>`<tr class="row" data-i="${r.best.i}"><td class="wrap">${r.f}</td><td class=n>${r.n}</td><td class=n>${pc(r.best.wr)}</td><td class=n>${pc(r.med)}</td><td class=n>${sg(r.edge)}</td></tr>`).join("")+"</table>";}
function drawArch(){if(!D.arch){$("left").innerHTML='<div class="d mute">No archetypes in this export.</div>';return}
 const s=D.arch.summary,m=D.arch.matrix;$("cnt").textContent=s.length+" archetypes";
 let h="<table><tr><th>#</th><th class=n>Builds</th><th class=n>Mean win</th><th>Is</th><th>Beats</th><th>Loses to</th><th>Best build</th></tr>"+
 s.map(r=>`<tr><td>C${r.cluster}</td><td class=n>${r.n}</td><td class=n>${pc(r.mean_wr)}</td><td class=wrap>${r.is}</td><td>${r.beats}</td><td>${r["loses to"]}</td><td class=wrap>${r["best build"]}</td></tr>`).join("")+"</table>";
 h+="<h3 class='d'>Row vs column win share</h3><table><tr><th></th>"+m.columns.map(c=>`<th class=n>${c}</th>`).join("")+"</tr>"+
 m.data.map((r,i)=>`<tr><th>${m.index[i]}</th>`+r.map(v=>`<td class="n ${v>.55?"g":v<.45?"b":""}">${pc(v)}</td>`).join("")+"</tr>").join("")+"</table>";
 $("left").innerHTML=h;}
function draw(){view=="builds"?drawBuilds():view=="fam"?drawFam():drawArch()}
function mlist(a){return "<table>"+a.map(([j,v])=>`<tr class="row" data-i="${j}"><td class="wrap">${B[j].ret} · ${B[j].gear}<div class=mute>${B[j].core}</div></td><td class="n ${v>.5?"g":"b"}">${pc(v)}</td></tr>`).join("")+"</table>"}
function detail(i){sel=i;const b=B[i];
 const sw=(a,c)=>a.length?a.map(x=>`<span class="pill">${x[0]} <span class="${c}">${pc(x[1])}</span></span>`).join(""):'<span class=mute>–</span>';
 $("right").innerHTML=`<div class="d"><h2>${b.ret} · ${b.gear}</h2><div class="mute">${b.core}</div>
 <div class="grid"><div class="k">Win<b>${pc(b.wr)}</b></div><div class="k">TI edge<b>${sg(b.edge)}</b></div><div class="k">vs top 25%<b>${pc(b.top)}</b></div><div class="k">Robust<b>${pc(b.rob)}</b></div>
 <div class="k">TI<b>${b.ti}</b><span class=mute>${b.hold} Holdings + ${b.dom} Domain</span></div><div class="k">Worst 10%<b>${pc(b.worst)}</b></div><div class="k">Countered by<b>${pc(b.ctr)}</b></div><div class="k">Beats<b>${pc(b.beat)}</b></div></div>
 <h3>Strong vs</h3>${sw(b.strong,"g")}<h3>Weak vs</h3>${sw(b.weak,"b")}
 <h3>Holdings</h3>${b.pursuits.map(p=>`<span class=pill>${p}</span>`).join("")}
 <h3>Keywords</h3><div class=mute>${b.tags||"–"}</div>
 <div class="two"><div><h3>Best matchups</h3>${mlist(b.best)}</div><div><h3>Worst matchups</h3>${mlist(b.worstm)}</div></div></div>`;
 if(view=="builds")drawBuilds();}
document.addEventListener("click",e=>{const t=e.target.closest("th[data-k]");if(t){const k=t.dataset.k;sortD=sortK==k?-sortD:-1;sortK=k;draw();return}
 const r=e.target.closest("tr.row");if(r){detail(+r.dataset.i);return}
 const n=e.target.closest("nav button");if(n){document.querySelectorAll("nav button").forEach(x=>x.classList.toggle("on",x==n));view=n.dataset.v;draw()}});
["q","ret","tmin","tmax","fam1"].forEach(id=>$(id).addEventListener("input",draw));draw();
</script></body></html>"""
