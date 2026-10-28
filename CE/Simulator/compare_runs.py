"""compare_runs.py — Bandit and army headline numbers, side by side, for simulator runs in lab_out/sim/.

    python compare_runs.py <tag> [<tag> ...]
"""
import sys, json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent / "lab_out" / "sim"
rows = []
for tag in sys.argv[1:]:
    games = [json.loads(l) for l in open(ROOT / tag / "games.jsonl", encoding="utf8")]
    n = len(games); bat = []; camps = {}; sacks = 0; acts = []; armies = []; gold_lost = 0; income = 0; po = []
    for g in games:
        for b in g["rec"]["battles"]:
            ps = "A" if "pid" in b["A"] else "B"; bs = "B" if ps == "A" else "A"
            if "bandit" in b[bs]: bat.append((b["src"], b["win"] == ps))
        for x in g["rec"]["turns"]:
            if x["t"] in (10, 20, 30, 40): camps.setdefault(x["t"], []).append(x["camps"])
            armies.append(x["armies"]); po.append(x["po"])
        sacks += sum(1 for e in g["rec"]["events"] if e["kind"] == "sack")
        acts += [a for _, _, _, a, _ in g["rec"]["envoys"]]
        for t, p, k, v in g["rec"]["ledger"]:
            if k == "Extorted by Bandits": gold_lost -= v
            if v > 0 and not k.startswith("~"): income += v
    B = pd.DataFrame(bat, columns=["src", "won"]); A = pd.Series(acts)
    att = B[B.src == "vs Bandits"]; dfd = B[B.src != "vs Bandits"]
    S = pd.read_csv(ROOT / tag / "seats.csv")
    rows.append({"run": tag, "games": n,
                 "attacks/game": round(len(att) / n, 1), "attack win": f"{att.won.mean():.0%}" if len(att) else "-",
                 "defences/game": round(len(dfd) / n, 1), "defence win": f"{dfd.won.mean():.0%}" if len(dfd) else "-",
                 "camps t10/20/30/40": "/".join(str(round(sum(camps[t]) / len(camps[t]))) for t in sorted(camps)),
                 "sacks/game": round(sacks / n), "gold lost": f"{gold_lost / max(1, income):.1%}",
                 "armies/player": round(sum(armies) / len(armies), 2),
                 "Move%": f"{(A == 'Move').mean():.1%}", "Muster%": f"{(A == 'Muster').mean():.1%}", "Build%": f"{(A == 'Build').mean():.1%}",
                 "PO": round(sum(po) / len(po), 1), "edicts": round(S.edicts.mean(), 2), "treasury": round(S.treasury.mean())})
print(pd.DataFrame(rows).set_index("run").T.to_string())
