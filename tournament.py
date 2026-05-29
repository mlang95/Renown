"""
Tournament runner: pair every loadout against every other, 100 sims each.

Outputs:
- Per-matchup CSV: a_name, b_name, a_wins, b_wins, mut_wipe, indecisive, avg_skirm, avg_a_rem, avg_b_rem
- Per-loadout summary: total wins, total losses, win rate, avg survivors, gold-efficiency
- Top/bottom dominant strategies
"""

import csv
import random
import time
import sys
from pathlib import Path

import renown_combat
from renown_combat import make_army, run_battle, random_tactic_picker
from normalized_matrix import build_normalized_matrix
from loadouts import archetype_pool, Loadout

# Install the normalized symmetric matrix
new_matrix = build_normalized_matrix()
renown_combat.TACTIC_MATRIX.clear()
renown_combat.TACTIC_MATRIX.update(new_matrix)


def loadout_to_army(ld: Loadout, name_suffix: str, is_attacker: bool = False):
    return make_army(
        name=f"{ld.name}{name_suffix}",
        retinue=ld.retinue,
        weapon=ld.weapon,
        shield=ld.shield,
        armor=ld.armor,
        size=ld.size,
        extra_tags=list(ld.extra_tags),
        ranged=ld.ranged,
        has_tiltyard=ld.has_tiltyard,
        is_attacker=is_attacker,
    )


def run_matchup(ld_a: Loadout, ld_b: Loadout, n_runs: int = 100, max_skirmishes: int = 20):
    """Run n_runs battles. Alternate which side is the attacker to neutralize that variable."""
    a_wins = b_wins = mut_wipe = indec = 0
    skirm_total = 0
    a_rem_total = b_rem_total = 0

    for i in range(n_runs):
        # Alternate attacker role each run
        a_is_atk = (i % 2 == 0)
        a = loadout_to_army(ld_a, " (A)", is_attacker=a_is_atk)
        b = loadout_to_army(ld_b, " (B)", is_attacker=not a_is_atk)

        result = run_battle(a, b, random_tactic_picker(), random_tactic_picker(),
                            max_skirmishes=max_skirmishes, verbose=False)
        outcome = result["outcome"]
        if outcome == "a_wins":
            a_wins += 1
        elif outcome == "b_wins":
            b_wins += 1
        elif outcome == "mutual_wipe":
            mut_wipe += 1
        else:
            indec += 1
        skirm_total += result["skirmishes"]
        a_rem_total += result["a_remaining"]
        b_rem_total += result["b_remaining"]

    return {
        "a_wins": a_wins,
        "b_wins": b_wins,
        "mut_wipe": mut_wipe,
        "indecisive": indec,
        "avg_skirm": skirm_total / n_runs,
        "avg_a_rem": a_rem_total / n_runs,
        "avg_b_rem": b_rem_total / n_runs,
    }


def run_tournament(pool, n_runs=100, output_dir="."):
    out_dir = Path(output_dir)
    out_dir.mkdir(exist_ok=True)

    n_loadouts = len(pool)
    n_matchups = n_loadouts * n_loadouts
    print(f"Running tournament: {n_loadouts} loadouts × {n_loadouts} = {n_matchups:,} matchups × {n_runs} runs")
    print(f"Estimated total battles: {n_matchups * n_runs:,}")

    random.seed(2026)
    start = time.time()

    # Matchup CSV
    matchup_path = out_dir / "matchups.csv"
    summary = {ld.name: {"wins": 0, "losses": 0, "mut_wipe": 0, "indecisive": 0,
                          "rem_self": 0.0, "rem_opp": 0.0, "n_battles": 0,
                          "loadout": ld} for ld in pool}

    with open(matchup_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "a_name", "b_name",
            "a_wins", "b_wins", "mut_wipe", "indecisive",
            "avg_skirm", "avg_a_rem", "avg_b_rem",
            "a_retinue", "a_weapon", "a_shield", "a_armor", "a_ranged", "a_tiltyard", "a_size", "a_tags",
            "b_retinue", "b_weapon", "b_shield", "b_armor", "b_ranged", "b_tiltyard", "b_size", "b_tags",
        ])
        for i, ld_a in enumerate(pool):
            for j, ld_b in enumerate(pool):
                r = run_matchup(ld_a, ld_b, n_runs=n_runs)
                writer.writerow([
                    ld_a.name, ld_b.name,
                    r["a_wins"], r["b_wins"], r["mut_wipe"], r["indecisive"],
                    f"{r['avg_skirm']:.2f}", f"{r['avg_a_rem']:.2f}", f"{r['avg_b_rem']:.2f}",
                    ld_a.retinue, ld_a.weapon, ld_a.shield or "", ld_a.armor, ld_a.ranged or "", ld_a.has_tiltyard, ld_a.size, ",".join(ld_a.extra_tags),
                    ld_b.retinue, ld_b.weapon, ld_b.shield or "", ld_b.armor, ld_b.ranged or "", ld_b.has_tiltyard, ld_b.size, ",".join(ld_b.extra_tags),
                ])
                # Aggregate summary (skip self-matchups for win-rate calc)
                if i != j:
                    sa = summary[ld_a.name]
                    sa["wins"] += r["a_wins"]
                    sa["losses"] += r["b_wins"]
                    sa["mut_wipe"] += r["mut_wipe"]
                    sa["indecisive"] += r["indecisive"]
                    sa["rem_self"] += r["avg_a_rem"]
                    sa["rem_opp"] += r["avg_b_rem"]
                    sa["n_battles"] += n_runs
            # Progress
            elapsed = time.time() - start
            done_frac = (i + 1) / n_loadouts
            eta = elapsed / done_frac - elapsed if done_frac > 0 else 0
            print(f"  [{i+1}/{n_loadouts}] {ld_a.name:<40} | elapsed {elapsed:.0f}s, eta {eta:.0f}s", flush=True)

    # Summary CSV
    summary_path = out_dir / "summary.csv"
    with open(summary_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name", "retinue", "weapon", "shield", "armor", "ranged", "tiltyard", "size", "tags",
            "wins", "losses", "mut_wipe", "indecisive", "n_battles",
            "win_rate", "loss_rate", "decisive_rate",
            "avg_self_survivors", "avg_opp_survivors", "kill_efficiency",
            "upkeep_per_retinue", "army_upkeep",
            "wins_per_1000_upkeep",
        ])
        for name, s in summary.items():
            ld = s["loadout"]
            n = max(1, s["n_battles"])
            win_rate = s["wins"] / n
            loss_rate = s["losses"] / n
            decisive_rate = (s["wins"] + s["losses"] + s["mut_wipe"]) / n
            avg_self_rem = s["rem_self"] / max(1, n // 100)  # n_battles = 100 * n_opponents
            avg_opp_rem = s["rem_opp"] / max(1, n // 100)
            kill_eff = (avg_self_rem - avg_opp_rem) if (avg_self_rem + avg_opp_rem) else 0
            army_upkeep = ld.upkeep_per_retinue * ld.size
            wins_per_1k = s["wins"] / (army_upkeep / 1000) if army_upkeep else 0
            writer.writerow([
                name, ld.retinue, ld.weapon, ld.shield or "", ld.armor, ld.ranged or "", ld.has_tiltyard, ld.size, ",".join(ld.extra_tags),
                s["wins"], s["losses"], s["mut_wipe"], s["indecisive"], s["n_battles"],
                f"{win_rate:.4f}", f"{loss_rate:.4f}", f"{decisive_rate:.4f}",
                f"{avg_self_rem:.2f}", f"{avg_opp_rem:.2f}", f"{kill_eff:.2f}",
                ld.upkeep_per_retinue, army_upkeep,
                f"{wins_per_1k:.2f}",
            ])

    elapsed = time.time() - start
    print(f"\nDone. {n_matchups * n_runs:,} battles in {elapsed:.0f}s")
    print(f"  Matchups CSV: {matchup_path}")
    print(f"  Summary CSV:  {summary_path}")
    return summary_path, matchup_path


if __name__ == "__main__":
    n_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    pool = archetype_pool()
    print(f"Pool size: {len(pool)} loadouts")
    run_tournament(pool, n_runs=n_runs)
