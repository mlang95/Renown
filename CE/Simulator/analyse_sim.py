"""analyse_sim.py — turn a simulator run (lab_out/sim/<TAG>/games.jsonl) into tables, a report and end screens.

    python analyse_sim.py <run folder> [--end-screens N]

Writes into the run folder:
  games.csv        one row per game (map, players, Age, winner, run time, diagnostics)
  seats.csv        one row per player per game (culture, faction, archetype, result, economy, military, diplomacy, faith, edicts, build order)
  turns.parquet    every player's snapshot every turn (the time series behind the charts)
  ledger.csv       gold / Faith / Doubt flows by game, player and reason
  report.html      the cross-game report (cultures, archetypes, factions, maps, player counts, Craft value, build paths, timelines, diagnostics)
  report.md        the same headline tables as text
  endscreens/      one end-of-game screen per game (first N games), RTS style
"""
import sys, json, math, io, html, argparse, collections
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- load
def load(run):
    games, seats, turns, ledger, envoys, battles, events, flags, stuck = [], [], [], [], [], [], [], [], []
    with open(run / "games.jsonl", encoding="utf8") as f:
        for line in f:
            g = json.loads(line); c = g["cfg"]; gid = c["game"]; R = g["rec"]
            cul = {p["pid"]: p for p in g["players"]}
            games.append(dict(game=gid, players=c["players"], map=c["map"], age=g.get("age", ""), turns=g["turns"], end=g.get("endReason", ""), renown=g["renown"], era=g["era"],
                              winner=g["winner"], winner_culture=cul.get(g["winner"], {}).get("culture", ""), ms=g["ms"],
                              stuck=len(R.get("stuck", [])), flags=len(R.get("flags", [])), battles=len(R.get("battles", []))))
            for p in g["players"]:
                seats.append(dict(game=gid, players=c["players"], map=c["map"], age=g.get("age", ""), pid=p["pid"], seat=p["seat"], culture=p["culture"],
                                  faction=p["faction"], archetype=p["archetype"], deploy_flags=len((p.get("deploy") or {}).get("flags") or [])))
            for r in R["turns"]:
                r = dict(r); r["game"] = gid; r["players"] = c["players"]; r["map"] = c["map"]; r["culture"] = cul[r["pid"]]["culture"]
                r["built"] = "|".join(r.get("built") or []); r["improved"] = "|".join(r.get("improved") or [])
                r["acts_n"] = len(r.get("acts") or []); r["acts_pass"] = sum(1 for a in r.get("acts") or [] if a[2] in ("Passed", "Endorsed"))
                r["edictKinds"] = json.dumps(r.get("edictKinds") or {}); r["tiers"] = json.dumps(r.get("tiers") or {})
                r["survivalWhy"] = "|".join(r.get("survivalWhy") or []); r.pop("acts", None)
                turns.append(r)
            ledger += [dict(game=gid, t=t, pid=pid, cat=k, v=v) for t, pid, k, v in R["ledger"]]
            envoys += [dict(game=gid, t=t, pid=pid, dom=d, act=a, out=o) for t, pid, d, a, o in R["envoys"]]
            for b in R["battles"]:
                b = dict(b); b["game"] = gid; b["tactics"] = json.dumps(b["tactics"]); b["A"] = json.dumps(b["A"]); b["B"] = json.dumps(b["B"]); battles.append(b)
            events += [dict(e, game=gid) for e in R["events"]]
            flags += [dict(game=gid, t=t, pid=pid, act=a, flag=fl) for t, pid, a, fl in R.get("flags", [])]
            stuck += [dict(s, game=gid) for s in R.get("stuck", [])]
    D = lambda L: pd.DataFrame(L)
    return D(games), D(seats), D(turns), D(ledger), D(envoys), D(battles), D(events), D(flags), D(stuck)

# ---------------------------------------------------------------- per-seat summary (the end-screen numbers)
def seat_table(games, seats, turns, ledger, envoys, battles, events):
    T = turns.sort_values(["game", "pid", "t"])
    last = T.groupby(["game", "pid"]).tail(1).set_index(["game", "pid"])
    agg = T.groupby(["game", "pid"]).agg(po_mean=("po", "mean"), po_min=("po", "min"), uprising_turns=("po", lambda s: int((s <= -10).sum())),
        survival=("survival", "mean"), craft_mean=("craft", "mean"), trade_mean=("trade", "mean"), net_mean=("net", "mean"), treasury_peak=("treasury", "max"),
        armies_max=("armies", "max"), retinues_max=("retinues", "max"), envoys=("envoys", "sum"), acts=("acts_n", "sum"), acts_pass=("acts_pass", "sum"),
        support=("support", "sum"), oppose=("oppose", "sum"), wars_max=("wars", "max"), trade_pacts=("trade_pacts", "max"))
    first_ed = T[T.edicts > 0].groupby(["game", "pid"]).t.min().rename("first_edict_turn")
    order = T[T.built != ""].groupby(["game", "pid"]).built.apply(lambda s: " > ".join("|".join(s).split("|")[:6])).rename("build_order")
    S = seats.set_index(["game", "pid"]).join(last[["edicts", "treasury", "settlements", "holdings", "infra", "wonders", "monuments", "vassal", "ind", "pro", "cun", "pie"]])
    S = S.join(agg).join(first_ed).join(order)
    if len(ledger):
        L = ledger.copy(); gold = L[~L.cat.str.startswith("~")]
        S = S.join(gold[gold.v > 0].groupby(["game", "pid"]).v.sum().rename("gold_in")).join((-gold[gold.v < 0].groupby(["game", "pid"]).v.sum()).rename("gold_out"))
        S = S.join(gold[gold.cat.str.contains("Trade", case=False)].groupby(["game", "pid"]).v.sum().rename("trade_total"))
        S = S.join(gold[gold.cat.str.contains("tax", case=False)].groupby(["game", "pid"]).v.sum().rename("tax_total"))
        S = S.join(gold[gold.cat.str.contains("Extort", case=False) & (gold.v > 0)].groupby(["game", "pid"]).v.sum().rename("extort_in"))
        S = S.join((-gold[gold.cat.str.contains("Extort", case=False) & (gold.v < 0)].groupby(["game", "pid"]).v.sum()).rename("extort_out"))
        S = S.join(L[L.cat == "~doubt"].groupby(["game", "pid"]).v.sum().rename("doubt_from_actions")).join(L[L.cat == "~faith"].groupby(["game", "pid"]).v.sum().rename("faith_from_actions"))
    if len(battles):
        rows = []
        for b in battles.itertuples():
            for X, O in (("A", "B"), ("B", "A")):
                sd = json.loads(getattr(b, X))
                if "pid" in sd:
                    rows.append(dict(game=b.game, pid=int(sd["pid"]), fought=1, bwon=int(b.win == X), blost=int(b.win == O), vs_bandits=int("bandit" in json.loads(getattr(b, O))),
                                     cas_taken=getattr(b, "cas" + X), cas_dealt=getattr(b, "cas" + O)))
        if rows:
            Bt = pd.DataFrame(rows).groupby(["game", "pid"]).sum()
            S = S.join(Bt)
    if len(events):
        ev = events
        for kind, col in (("treaty", "treaties"), ("war", "wars_declared")):
            e = ev[ev.kind == kind]
            if len(e):
                S = S.join(e.groupby(["game", "a"]).size().rename(col).rename_axis(["game", "pid"]))
    S = S.reset_index()
    for col in ("gold_in", "gold_out", "trade_total", "tax_total", "extort_in", "extort_out", "fought", "bwon", "blost", "vs_bandits", "cas_taken", "cas_dealt",
                "treaties", "wars_declared", "doubt_from_actions", "faith_from_actions"):
        S[col] = S[col].fillna(0) if col in S else 0
    S["pass_rate"] = (S.acts_pass / S.acts.replace(0, np.nan)).round(3)
    # result: most Edicts, then Treasury (vassals last)
    S["score"] = S.edicts * 1e7 + S.treasury.clip(lower=-9e6) - S.vassal.astype(int) * 1e9
    S["rank"] = S.groupby("game").score.rank(ascending=False, method="min").astype(int)
    S["victory"] = (S["rank"] == 1).astype(int)
    S["norm_rank"] = 1 - (S["rank"] - 1) / (S.players - 1).clip(lower=1)        # 1 = first, 0 = last, comparable across player counts
    return S

# ---------------------------------------------------------------- charts
def svg_fig(fig):
    b = io.StringIO(); fig.savefig(b, format="svg", bbox_inches="tight"); plt.close(fig)
    s = b.getvalue(); return s[s.find("<svg"):]
def line_chart(df, x, y, by, title, ylabel):
    fig, ax = plt.subplots(figsize=(9, 3.6))
    for k, g in df.groupby(by):
        m = g.groupby(x)[y].mean(); ax.plot(m.index, m.values, label=str(k), linewidth=1.4)
    ax.set_title(title, fontsize=10); ax.set_xlabel(x); ax.set_ylabel(ylabel); ax.grid(alpha=.25)
    ax.legend(fontsize=7, ncol=3, frameon=False, loc="upper left", bbox_to_anchor=(1, 1))
    return svg_fig(fig)
def bar_chart(series, title, xlabel):
    fig, ax = plt.subplots(figsize=(9, max(2.2, .28 * len(series) + .8)))
    s = series.sort_values(); ax.barh([str(i) for i in s.index], s.values, color="#6a8caf"); ax.set_title(title, fontsize=10); ax.set_xlabel(xlabel); ax.grid(axis="x", alpha=.25)
    return svg_fig(fig)

# ---------------------------------------------------------------- the report
def table_html(df, fmt=None, max_rows=60):
    df = df.head(max_rows)
    return df.to_html(classes="t", float_format=(fmt or (lambda v: f"{v:,.2f}")), border=0, na_rep="—")

def report(run, games, S, turns, ledger, envoys, battles, events, flags, stuck):
    out, md = [], []
    def sec(title, body, note=""):
        out.append(f"<section><h2>{html.escape(title)}</h2>{('<p class=note>' + html.escape(note) + '</p>') if note else ''}{body}</section>")
    n_games, pcs = len(games), sorted(games.players.unique())
    cfg = json.loads((run / "config.json").read_text(encoding="utf8")) if (run / "config.json").exists() else {}
    head = f"{n_games} games · players {', '.join(map(str, pcs))} · {games.map.nunique()} map(s) · up to {cfg.get('turns', '?')} turns · {games.ms.sum() / 1000:,.0f}s of simulation"
    md += [f"# Simulator run {run.name}", "", head, ""]

    # cultures
    C = S.groupby("culture").agg(seats=("game", "size"), win_pct=("victory", "mean"), norm_rank=("norm_rank", "mean"), edicts=("edicts", "mean"),
        first_edict=("first_edict_turn", "mean"), treasury=("treasury", "mean"), net_per_turn=("net_mean", "mean"), survival=("survival", "mean"),
        po_mean=("po_mean", "mean"), uprising_turns=("uprising_turns", "mean"), pass_rate=("pass_rate", "mean"), retinues_max=("retinues_max", "mean"),
        battles=("fought", "mean"), battles_won=("bwon", "mean"), treaties=("treaties", "mean")).sort_values("norm_rank", ascending=False)
    C["win_pct"] *= 100; C["survival"] *= 100
    sec("Cultures", table_html(C) + bar_chart(C.norm_rank, "Average finishing position (1 = first, 0 = last)", "normalised rank"),
        "Finishing position is by Edicts, then Treasury; vassals last. 'survival' is the share of turns the AI's survival checks were all met.")
    md += ["## Cultures", C.round(2).to_markdown(), ""]
    # by player count
    P = S.pivot_table(index="culture", columns="players", values="norm_rank", aggfunc="mean").round(3)
    sec("Cultures by player count (average finishing position)", table_html(P, lambda v: f"{v:.2f}"))
    md += ["## Cultures by player count", P.to_markdown(), ""]
    # archetype / faction / seat / map
    for col, title in (("archetype", "Archetypes"), ("faction", "Factions")):
        A = S.groupby(col).agg(seats=("game", "size"), win_pct=("victory", "mean"), norm_rank=("norm_rank", "mean"), edicts=("edicts", "mean"), treasury=("treasury", "mean")).sort_values("norm_rank", ascending=False)
        A["win_pct"] *= 100; sec(title, table_html(A)); md += [f"## {title}", A.round(2).to_markdown(), ""]
    Se = S.groupby(["players", "seat"]).norm_rank.mean().unstack().round(3)
    sec("Seat order (average finishing position by seat)", table_html(Se, lambda v: f"{v:.2f}"), "Seat 0 is the first Host.")
    M = S.groupby(["map", "culture"]).norm_rank.mean().unstack().round(2)
    sec("Maps × cultures (average finishing position)", table_html(M, lambda v: f"{v:.2f}"))
    G = games.groupby("map").agg(games=("game", "size"), turns=("turns", "mean"), battles=("battles", "mean"), stuck=("stuck", "mean"), flags=("flags", "mean"))
    sec("Maps", table_html(G))

    # Craft value by player count
    rows = []
    for n, g in S.groupby("players"):
        g = g.dropna(subset=["craft_mean"])
        if len(g) < 5 or g.craft_mean.std() == 0: continue
        rows.append(dict(players=n, seats=len(g), craft_mean=g.craft_mean.mean(),
                         r_trade=g[["craft_mean", "trade_total"]].corr(method="spearman").iloc[0, 1],
                         r_income=g[["craft_mean", "gold_in"]].corr(method="spearman").iloc[0, 1],
                         r_rank=g[["craft_mean", "norm_rank"]].corr(method="spearman").iloc[0, 1],
                         trade_per_craft=(g.trade_total.sum() / max(1e-9, g.craft_mean.sum()))))
    if rows:
        K = pd.DataFrame(rows).set_index("players")
        sec("Craft value by player count", table_html(K),
            "Spearman correlations between a player's average Craft and its trade income, total income and finishing position, per player count. "
            "Rising values with more players mean Craft matters more in bigger games.")
        md += ["## Craft value by player count", K.round(3).to_markdown(), ""]

    # build paths: what the top finishers built that the bottom ones didn't
    if "build_order" in S:
        bp = []
        for cul, g in S.groupby("culture"):
            top, bot = g[g.norm_rank >= .5], g[g.norm_rank < .5]
            if len(top) < 2 or len(bot) < 2: continue
            def share(df):
                c = collections.Counter(); [c.update(set(str(o).split(" > "))) for o in df.build_order.dropna()]
                return {k: v / max(1, len(df)) for k, v in c.items() if k and k != "nan"}
            st, sb = share(top), share(bot)
            lift = sorted(((st.get(k, 0) - sb.get(k, 0), k) for k in set(st) | set(sb)), reverse=True)
            common = collections.Counter(" > ".join(str(o).split(" > ")[:3]) for o in top.build_order.dropna()).most_common(2)
            bp.append(dict(culture=cul, top_seats=len(top), helped=", ".join(f"{k} (+{d:.0%})" for d, k in lift[:4] if d > 0),
                           hurt=", ".join(f"{k} ({d:.0%})" for d, k in lift[::-1][:3] if d < 0), top_openings=" · ".join(f"{o} ×{n}" for o, n in common)))
        if bp:
            B = pd.DataFrame(bp).set_index("culture")
            sec("Viable build paths", table_html(B), "Early Holdings (first six built) more common among a culture's top-half finishers than its bottom half, and the most common openings of the top half.")
            md += ["## Viable build paths", B.to_markdown(), ""]

    # action mix and pass rates
    if len(envoys):
        E = envoys.merge(S[["game", "pid", "culture"]], on=["game", "pid"])
        E["pass"] = E.out.isin(["Passed", "Endorsed"])
        mix = E.groupby(["culture", "act"]).size().unstack(fill_value=0)
        mix = (mix.T / mix.sum(axis=1)).T.round(3)
        top_cols = mix.mean().sort_values(ascending=False).index[:12]
        sec("Action mix by culture (share of performed actions)", table_html(mix[top_cols], lambda v: f"{v:.0%}"))
        pr = E.groupby("dom")["pass"].mean().sort_values()
        sec("Envoy pass rate by Domain", bar_chart(pr, "share Passed or Endorsed", "pass rate"))

    # edicts
    if len(turns):
        ek = collections.Counter(); first = collections.defaultdict(list)
        last = turns.sort_values("t").groupby(["game", "pid"]).tail(1)
        for r in last.itertuples():
            for k, v in json.loads(r.edictKinds).items(): ek[(r.culture, k)] += v
        if ek:
            Ek = pd.Series(ek).unstack(fill_value=0)
            Ek = (Ek.T / S.groupby("culture").size()).T.round(2)
            sec("Edicts completed per game by culture and kind", table_html(Ek))

    # timelines
    for y, title, lab in (("treasury", "Treasury by turn", "gold"), ("net", "Net income per turn", "gold"), ("po", "Public Order by turn", "PO"),
                          ("edicts", "Edicts by turn", "Edicts"), ("retinues", "Retinues by turn", "Retinues"), ("holdings", "Holdings by turn", "Holdings"),
                          ("craft", "Craft by turn", "Craft")):
        if y in turns: sec(title, line_chart(turns, "t", y, "culture", title + " (mean per culture)", lab))
    if len(turns):
        sec("Treasury by turn and player count", line_chart(turns, "t", "treasury", "players", "Treasury by player count", "gold"))

    # diagnostics
    diag = []
    if len(flags): diag.append("<h3>Effects the board leaves to a human (not played)</h3>" + table_html(flags.groupby("flag").size().sort_values(ascending=False).rename("count").to_frame(), lambda v: f"{v:,.0f}", 25))
    if len(stuck): diag.append("<h3>Vote slots the simulator had to skip</h3>" + table_html(stuck.groupby(["ph", "waiting"]).size().rename("count").to_frame(), lambda v: f"{v:,.0f}"))
    dep = S.deploy_flags.sum()
    diag.append(f"<p>Deploy rule flags: {int(dep)} across {len(S)} seats. Errors: see errors.log if present.</p>")
    sec("Diagnostics", "".join(diag))

    css = """body{font:13px/1.45 system-ui,Segoe UI,sans-serif;margin:24px auto;max-width:1180px;padding:0 16px;color:#1d232b;background:#fafaf7}
h1{font-size:22px}h2{font-size:16px;border-bottom:1px solid #ccd;padding-bottom:4px;margin-top:28px}.note{color:#667;font-size:12px}
table.t{border-collapse:collapse;font-size:12px;margin:6px 0}table.t th,table.t td{padding:3px 8px;border-bottom:1px solid #e4e4ea;text-align:right}
table.t th:first-child,table.t td:first-child{text-align:left}svg{max-width:100%;height:auto}"""
    page = f"<!doctype html><html><head><meta charset=utf-8><title>Renown sim — {html.escape(run.name)}</title><style>{css}</style></head><body><h1>Renown simulator — {html.escape(run.name)}</h1><p>{html.escape(head)}</p>{''.join(out)}</body></html>"
    (run / "report.html").write_text(page, encoding="utf8")
    (run / "report.md").write_text("\n".join(md), encoding="utf8")

# ---------------------------------------------------------------- end screens (RTS style)
PCOL = ["#4caf50", "#ef5350", "#42a5f5", "#ffb300", "#ab47bc", "#26c6da", "#ec407a"]
def mini_chart(T, y, title, w=560, h=170):
    if T.empty or y not in T: return ""
    tmin, tmax = T.t.min(), max(T.t.max(), T.t.min() + 1); lo, hi = float(T[y].min()), float(T[y].max()); hi = hi if hi > lo else lo + 1
    X = lambda t: 40 + (t - tmin) / (tmax - tmin) * (w - 50); Y = lambda v: h - 22 - (v - lo) / (hi - lo) * (h - 40)
    s = [f'<svg viewBox="0 0 {w} {h}" class=ch><text x=40 y=12 class=ct>{html.escape(title)}</text>',
         f'<line x1=40 y1={h-22} x2={w-10} y2={h-22} class=ax /><text x=4 y={Y(hi)+4:.0f} class=tk>{hi:,.0f}</text><text x=4 y={Y(lo)+4:.0f} class=tk>{lo:,.0f}</text>']
    if lo < 0 < hi: s.append(f'<line x1=40 y1={Y(0):.1f} x2={w-10} y2={Y(0):.1f} class=zero />')
    for i, (pid, g) in enumerate(T.groupby("pid")):
        pts = " ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in zip(g.t, g[y]))
        s.append(f'<polyline points="{pts}" fill=none stroke="{PCOL[(int(pid) - 1) % len(PCOL)]}" stroke-width=2 />')
    s.append(f'<text x={w-10} y={h-6} class=tk text-anchor=end>turn {tmax}</text></svg>'); return "".join(s)

def endscreens(run, games, S, turns, battles, events, n):
    od = run / "endscreens"; od.mkdir(exist_ok=True)
    for gid in list(games.game)[:n]:
        g = games[games.game == gid].iloc[0]; Sg = S[S.game == gid].sort_values("rank"); Tg = turns[turns.game == gid]
        name = lambda pid: f"P{pid} " + str(Sg[Sg.pid == pid].culture.iloc[0])
        def tab(rows, cols):
            hd = "".join(f"<th>{html.escape(c)}</th>" for _, c in cols)
            body = "".join("<tr>" + f'<td><span class=dot style="background:{PCOL[(int(r.pid)-1)%len(PCOL)]}"></span>{html.escape(name(r.pid))}</td>' +
                           "".join(f"<td>{(getattr(r, k) if not isinstance(getattr(r, k), float) else (f'{getattr(r, k):,.0f}' if abs(getattr(r, k)) >= 10 else f'{getattr(r, k):,.2f}'))}</td>" for k, _ in cols[1:]) + "</tr>" for r in rows.itertuples())
            return f"<table class=t><tr>{hd}</tr>{body}</table>"
        summary = tab(Sg, [("pid", "Player"), ("rank", "Place"), ("edicts", "Edicts"), ("treasury", "Treasury"), ("settlements", "Settlements"), ("holdings", "Holdings"), ("retinues_max", "Peak Retinues"), ("faction", "Faction"), ("archetype", "Archetype")])
        econ = tab(Sg, [("pid", "Player"), ("gold_in", "Gold earned"), ("gold_out", "Gold spent"), ("treasury_peak", "Peak Treasury"), ("net_mean", "Avg net / turn"), ("tax_total", "Tax"), ("trade_total", "Trade"), ("extort_in", "Extorted in"), ("extort_out", "Extorted out"), ("craft_mean", "Avg Craft")]) + \
            mini_chart(Tg, "treasury", "Treasury") + mini_chart(Tg, "net", "Net income per turn") + mini_chart(Tg, "craft", "Craft")
        mil = tab(Sg, [("pid", "Player"), ("armies_max", "Peak Armies"), ("retinues_max", "Peak Retinues"), ("fought", "Battles"), ("bwon", "Won"), ("blost", "Lost"), ("vs_bandits", "vs Bandits"), ("cas_dealt", "Casualties dealt"), ("cas_taken", "Casualties taken"), ("wars_declared", "Wars declared")]) + \
            mini_chart(Tg, "retinues", "Retinues")
        dip = tab(Sg, [("pid", "Player"), ("envoys", "Envoys"), ("acts", "Actions"), ("pass_rate", "Pass rate"), ("support", "Influence for"), ("oppose", "Influence against"), ("treaties", "Treaties signed"), ("trade_pacts", "Trade partners"), ("wars_max", "Wars at once")])
        fai = tab(Sg, [("pid", "Player"), ("po_mean", "Avg PO"), ("po_min", "Lowest PO"), ("uprising_turns", "Turns at −10"), ("faith_from_actions", "Faith gained"), ("doubt_from_actions", "Doubt gained"), ("survival", "Survival share")]) + mini_chart(Tg, "po", "Public Order")
        edi = tab(Sg, [("pid", "Player"), ("edicts", "Edicts"), ("first_edict_turn", "First Edict turn"), ("ind", "Industry"), ("pro", "Prowess"), ("cun", "Cunning"), ("pie", "Piety"), ("monuments", "Monuments"), ("wonders", "Wonders")]) + mini_chart(Tg, "edicts", "Edicts")
        builds = "".join(f"<li><b>{html.escape(name(r.pid))}</b>: {html.escape(str(r.build_order or '—'))}</li>" for r in Sg.itertuples())
        Bg = battles[battles.game == gid] if len(battles) else pd.DataFrame()
        bl = "".join(f"<li>turn {b.t}: {html.escape(b.A)} vs {html.escape(b.B)} — {html.escape(str(b.win or b.end))} ({b.skirmishes} Skirmishes, casualties {b.casA}/{b.casB})</li>" for b in Bg.itertuples()) or "<li>none</li>"
        Eg = events[events.game == gid] if len(events) else pd.DataFrame()
        el = "".join(f"<li>turn {e.t}: {html.escape(e.kind)} {('P' + str(e.a)) if not pd.isna(e.a) else ''}{(' → P' + str(int(e.b))) if 'b' in Eg and not pd.isna(e.b) else ''} {html.escape(str(e.type)) if 'type' in Eg and isinstance(e.type, str) else ''}</li>" for e in Eg.itertuples()) or "<li>none</li>"
        tabs = [("Summary", summary + f"<h3>Build order (first six)</h3><ul>{builds}</ul>"), ("Economy", econ), ("Military", mil + f"<h3>Battles</h3><ul>{bl}</ul>"),
                ("Diplomacy", dip + f"<h3>Treaties, wars, Edicts</h3><ul>{el}</ul>"), ("Faith", fai), ("Edicts", edi)]
        radios = "".join(f'<input type=radio name=tab id=t{i} {"checked" if i == 0 else ""}><label for=t{i}>{t}</label>' for i, (t, _) in enumerate(tabs))
        panes = "".join(f'<div class=pane id=p{i}>{b}</div>' for i, (_, b) in enumerate(tabs))
        sel = "".join(f"#t{i}:checked~#p{i}" + ("," if i < len(tabs) - 1 else "") for i in range(len(tabs)))
        css = f"""body{{font:13px/1.4 system-ui,Segoe UI,sans-serif;background:#1b1712;color:#efe6d2;margin:0;padding:20px}}h1{{font-size:20px;margin:0 0 4px;color:#f3d48a}}
.sub{{color:#b9a982;margin-bottom:14px}}input{{display:none}}label{{display:inline-block;padding:7px 16px;margin-right:4px;background:#2c251c;border:1px solid #5b4a30;border-bottom:none;cursor:pointer;color:#d8c69b}}
input:checked+label{{background:#3d3223;color:#fff1c9}}.pane{{display:none;background:#3d3223;border:1px solid #5b4a30;padding:14px}}{sel}{{display:block}}
table.t{{border-collapse:collapse;width:100%;margin-bottom:10px}}table.t th{{text-align:right;color:#d9c08a;font-weight:600;padding:5px 8px;border-bottom:1px solid #6b5a3c}}table.t th:first-child,table.t td:first-child{{text-align:left}}
table.t td{{text-align:right;padding:5px 8px;border-bottom:1px solid #4a3e2c}}.dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}}
svg.ch{{width:49%;min-width:320px;background:#2c251c;margin:4px 0;border:1px solid #4a3e2c}}.ct{{fill:#f3d48a;font-size:11px}}.tk{{fill:#b9a982;font-size:9px}}.ax{{stroke:#6b5a3c}}.zero{{stroke:#8a2e2e;stroke-dasharray:3 3}}
h3{{color:#f3d48a;font-size:13px}}ul{{margin:4px 0 8px 18px;padding:0}}"""
        win = Sg.iloc[0]
        page = (f"<!doctype html><html><head><meta charset=utf-8><title>Game {gid} — end screen</title><style>{css}</style></head><body>"
                f"<h1>Game {gid} · {html.escape(name(win.pid))} wins</h1><div class=sub>{html.escape(str(g['map']))} · {g['players']} players · {html.escape(str(g['age']))} · {g['turns']} turns · Renown {g['renown']} ({html.escape(str(g['era']))})</div>"
                f"{radios}{panes}</body></html>")
        (od / f"game_{gid:05d}.html").write_text(page, encoding="utf8")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--end-screens", type=int, default=12); a = ap.parse_args()
    run = Path(a.run)
    games, seats, turns, ledger, envoys, battles, events, flags, stuck = load(run)
    if games.empty: print("no games in", run); return
    S = seat_table(games, seats, turns, ledger, envoys, battles, events)
    games.to_csv(run / "games.csv", index=False); S.to_csv(run / "seats.csv", index=False)
    turns.to_parquet(run / "turns.parquet", index=False)
    if len(ledger): ledger.groupby(["game", "pid", "cat"]).v.sum().reset_index().to_csv(run / "ledger.csv", index=False)
    report(run, games, S, turns, ledger, envoys, battles, events, flags, stuck)
    endscreens(run, games, S, turns, battles, events, a.end_screens)
    print(f"{len(games)} games, {len(S)} seats -> {run / 'report.html'} ; {min(a.end_screens, len(games))} end screens in {run / 'endscreens'}")

if __name__ == "__main__":
    main()
