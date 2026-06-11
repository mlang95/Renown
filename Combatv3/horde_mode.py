"""
Horde mode — multi-battle limit testing for armies.

Endurance and casualties persist between battles. The army gets +1 endurance
recovery between battles (one turn passing). Fatigue resets between battles.

Three modes:
  - 'survival': fight cycling opponents until wipe. Output: distribution of waves survived.
  - 'fixed':    fight N waves, capture state at each wave. Output: per-wave aggregates.
  - 'escalation': each wave is a tougher opponent. Output: at what tier does the army fail?

Aggregation: each "run" is one independent army-life. Stats aggregate across runs.
"""

import numpy as np
from collections import namedtuple
from renown_combat import RETINUES
from vectorized_combat import run_matchup_vec
from loadouts import Loadout


WaveResult = namedtuple("WaveResult", "wave outcomes avg_size avg_endurance avg_spoils survival_rate")


def _make_endurance_max(loadout):
    """The maximum endurance for this loadout (factoring Cond Field)."""
    base = RETINUES[loadout.retinue]["endurance"]
    if "Cond Field" in loadout.extra_tags:
        base += 1
    return base


def run_horde(army, opponents, n_runs=500, max_waves=15, recovery=True, seed=42,
              max_skirmishes_per_battle=20, replace_between_waves=False):
    """Core horde runner.

    army: Loadout to test.
    opponents: list of Loadouts. If shorter than max_waves, cycles. Each wave's opponent
               is opponents[wave_idx % len(opponents)].
    n_runs: parallel independent runs (different RNG streams).
    max_waves: hard cap; loop stops earlier if all runs wiped.
    recovery: if True, army gains +1 endurance between battles (max cap = original max).
    replace_between_waves: if True, army resets to full size + endurance after each battle.
                           Replacement cost is tracked. Models "muster losses each turn."

    Returns dict with:
      'wave_results': list of WaveResult, one per wave actually fought
      'survival_curve': fraction of runs alive at start of wave k
      'wave_of_wipe': wave at which run wiped (or max_waves+1 if survived)
      'cumulative_spoils': per-run cumulative gold gained
      'cumulative_losses_value': per-run cumulative gold-value of own casualties
      'initial_muster_cost': scalar — cost to muster the army initially
      'per_run_final_size': size at end of last wave
      'per_run_final_endurance': endurance at end of last wave
      'break_even_wave': per-run wave at which cumulative spoils first equals/exceeds total cost
                          (or max_waves+1 if never broke even)
    """
    army_endurance_max = _make_endurance_max(army)
    army_size_max = army.size
    army_per_retinue_cost = RETINUES[army.retinue]["cost"]
    initial_muster_cost = army_size_max * army_per_retinue_cost

    # Strain mechanic: armies that successfully end a battle via Fall Back gain Strain,
    # which blocks the next-turn endurance recovery (+2). Strain falls off after the
    # skipped recovery step. Royal Pavilion grants "Immune Strain" — those armies never
    # gain strain even on successful FB.
    army_has_immune_strain = "Immune Strain" in army.extra_tags

    # Initial state
    a_size = np.full(n_runs, army_size_max, dtype=np.int32)
    a_endurance = np.full(n_runs, army_endurance_max, dtype=np.int8)
    a_strain = np.zeros(n_runs, dtype=bool)  # True = will skip next recovery
    alive = np.ones(n_runs, dtype=bool)
    cumulative_spoils = np.zeros(n_runs, dtype=np.float64)
    cumulative_losses_value = np.zeros(n_runs, dtype=np.float64)  # gold value of own casualties
    cumulative_remuster_cost = np.zeros(n_runs, dtype=np.float64)  # cost if remustering between waves
    wave_of_wipe = np.full(n_runs, max_waves + 1, dtype=np.int32)
    break_even_wave = np.full(n_runs, max_waves + 1, dtype=np.int32)
    has_broken_even = np.zeros(n_runs, dtype=bool)
    # Casualty source tracking across the campaign
    a_total_kills_inflicted = np.zeros(n_runs, dtype=np.int32)   # opponents killed in combat by army
    a_total_shake_inflicted = np.zeros(n_runs, dtype=np.int32)   # opponents lost to shake
    a_total_flee_inflicted  = np.zeros(n_runs, dtype=np.int32)   # opponents lost to flee
    a_total_killed_combat = np.zeros(n_runs, dtype=np.int32)     # own losses to combat
    a_total_killed_shake  = np.zeros(n_runs, dtype=np.int32)     # own losses to shake
    a_total_killed_flee   = np.zeros(n_runs, dtype=np.int32)     # own losses to flee
    # Cause of final wipe: 0=alive, 1=combat, 2=shake, 3=flee
    cause_of_wipe = np.zeros(n_runs, dtype=np.int8)

    wave_results = []
    survival_curve = []

    seed_base = seed

    for wave in range(max_waves):
        survival_curve.append(alive.sum() / n_runs)
        if not alive.any():
            break

        opp = opponents[wave % len(opponents)]
        opp_size = np.full(n_runs, opp.size, dtype=np.int32)
        opp_endurance = np.full(n_runs, _make_endurance_max(opp), dtype=np.int8)

        # Snapshot army size at start of wave (for casualty calculation)
        a_size_pre_wave = a_size.copy()

        result = run_matchup_vec(
            army, opp,
            n_runs=n_runs,
            max_skirmishes=max_skirmishes_per_battle,
            seed=seed_base + wave * 7919,
            return_per_run_state=True,
            a_init_size=a_size,
            a_init_endurance=a_endurance,
            b_init_size=opp_size,
            b_init_endurance=opp_endurance,
            a_playstyle=getattr(army, "playstyle", None),
            b_playstyle=getattr(opp, "playstyle", None),
        )

        # Per-run economic accounting
        opp_killed = opp_size - result["b_final_size"]
        battle_spoils = opp_killed.astype(np.float64) * RETINUES[opp.retinue]["cost"]
        a_lost = a_size_pre_wave - result["a_final_size"]
        battle_losses_value = a_lost.astype(np.float64) * army_per_retinue_cost

        won_mask = (result["outcomes"] == 1) & alive
        cumulative_spoils[won_mask] += battle_spoils[won_mask]
        cumulative_losses_value[alive] += battle_losses_value[alive]

        # Track casualty source totals (only for runs that were alive at start of wave)
        a_total_kills_inflicted[alive] += result["b_killed_combat"][alive]
        a_total_shake_inflicted[alive] += result["b_killed_shake"][alive]
        a_total_flee_inflicted[alive]  += result["b_killed_flee"][alive]
        a_total_killed_combat[alive] += result["a_killed_combat"][alive]
        a_total_killed_shake[alive]  += result["a_killed_shake"][alive]
        a_total_killed_flee[alive]   += result["a_killed_flee"][alive]

        # Record final cause-of-wipe for runs wiped this wave
        wiped_this_wave_mask = alive & (result["a_final_size"] <= 0)
        cause_of_wipe = np.where(wiped_this_wave_mask, result["a_cause_of_wipe"], cause_of_wipe).astype(np.int8)

        # Update army state
        new_size = result["a_final_size"]
        new_endurance = result["a_final_endurance"]

        survived_wave = (new_size > 0) & alive
        wiped_this_wave = alive & (new_size <= 0)
        wave_of_wipe[wiped_this_wave] = wave + 1

        # Replacement mode: refill army to full size, charge cost
        if replace_between_waves:
            # Replace lost retinues for runs that are still alive (survived the wave)
            replace_size = army_size_max - new_size
            replace_cost = replace_size.astype(np.float64) * army_per_retinue_cost
            cumulative_remuster_cost[survived_wave] += replace_cost[survived_wave]
            # Refill
            new_size = np.where(survived_wave, army_size_max, new_size).astype(np.int32)
            new_endurance = np.where(survived_wave, army_endurance_max, new_endurance).astype(np.int8)
            # Don't apply +2 recovery in replacement mode (already at max)
            # Strain still clears since the recovery step is "stepped over"
            a_strain = np.zeros(n_runs, dtype=bool)
        else:
            if recovery:
                # Strain blocks +2 endurance recovery; clears after the skipped step.
                # Surviving runs that are NOT strained: gain +2 endurance (capped at max).
                # Surviving runs that ARE strained: skip recovery, strain falls off.
                gets_recovery = survived_wave & (~a_strain)
                recovered_endurance = np.minimum(new_endurance + 2, army_endurance_max)
                new_endurance = np.where(gets_recovery, recovered_endurance, new_endurance).astype(np.int8)
                # Strain falls off after the recovery step (whether it was applied or skipped).
                a_strain = np.zeros(n_runs, dtype=bool)

        # Apply Strain for the wave just completed: if the army ended this battle via Fall Back
        # AND doesn't have Immune Strain, they gain strain (carried to NEXT wave's recovery step).
        # Only survivors can be strained — wiped armies don't matter.
        if not army_has_immune_strain and "a_ended_by_fallback" in result:
            a_strain = a_strain | (result["a_ended_by_fallback"] & survived_wave)

        a_size = new_size
        a_endurance = new_endurance
        alive = survived_wave

        # Track break-even (cumulative spoils first matches/exceeds total invested cost)
        total_cost = initial_muster_cost + cumulative_remuster_cost
        broke_even_now = (~has_broken_even) & (cumulative_spoils >= total_cost)
        break_even_wave[broke_even_now] = wave + 1
        has_broken_even = has_broken_even | broke_even_now

        wave_results.append(WaveResult(
            wave=wave + 1,
            outcomes=result["outcomes"].copy(),
            avg_size=float(a_size[survived_wave].mean()) if survived_wave.any() else 0.0,
            avg_endurance=float(a_endurance[survived_wave].mean()) if survived_wave.any() else 0.0,
            avg_spoils=float(battle_spoils[won_mask].mean()) if won_mask.any() else 0.0,
            survival_rate=float(survived_wave.sum() / n_runs),
        ))

    while len(survival_curve) < max_waves + 1:
        survival_curve.append(alive.sum() / n_runs)

    return {
        "wave_results": wave_results,
        "survival_curve": np.array(survival_curve),
        "wave_of_wipe": wave_of_wipe,
        "cumulative_spoils": cumulative_spoils,
        "cumulative_losses_value": cumulative_losses_value,
        "cumulative_remuster_cost": cumulative_remuster_cost,
        "initial_muster_cost": initial_muster_cost,
        "break_even_wave": break_even_wave,
        "per_run_final_size": a_size,
        "per_run_final_endurance": a_endurance,
        # Casualty source totals (per run, summed across all waves)
        "total_kills_inflicted_combat": a_total_kills_inflicted,
        "total_kills_inflicted_shake":  a_total_shake_inflicted,
        "total_kills_inflicted_flee":   a_total_flee_inflicted,
        "total_killed_combat": a_total_killed_combat,
        "total_killed_shake":  a_total_killed_shake,
        "total_killed_flee":   a_total_killed_flee,
        "cause_of_wipe": cause_of_wipe,  # 0=alive, 1=combat, 2=shake, 3=flee
        "army": army,
        "n_runs": n_runs,
        "max_waves": max_waves,
        "n_waves_fought": len(wave_results),
        "recovery": recovery,
        "replace_between_waves": replace_between_waves,
    }


# ==============================================================================
# Three modes
# ==============================================================================

def run_survival(army, opponent, n_runs=500, max_waves=20, recovery=True, seed=42,
                 replace_between_waves=False):
    """Fight the same opponent over and over until wipe."""
    return run_horde(army, [opponent], n_runs=n_runs, max_waves=max_waves, recovery=recovery,
                    seed=seed, replace_between_waves=replace_between_waves)


def run_fixed(army, opponent, n_battles=5, n_runs=500, recovery=True, seed=42,
              replace_between_waves=False):
    """Fight N waves of the same opponent. Returns state at every wave."""
    return run_horde(army, [opponent], n_runs=n_runs, max_waves=n_battles, recovery=recovery,
                    seed=seed, replace_between_waves=replace_between_waves)


def run_escalation(army, opponent_ladder, n_runs=500, recovery=True, seed=42,
                   replace_between_waves=False):
    """Each wave is a different opponent (escalating difficulty)."""
    return run_horde(army, opponent_ladder, n_runs=n_runs, max_waves=len(opponent_ladder),
                    recovery=recovery, seed=seed, replace_between_waves=replace_between_waves)


# ==============================================================================
# Summary helpers
# ==============================================================================

def summarize_horde(result, name=None):
    """Print a brief summary of a horde result."""
    army = result["army"]
    label = name or army.name
    wow = result["wave_of_wipe"]
    n_runs = result["n_runs"]
    max_waves = result["max_waves"]
    n_survived_all = int((wow > max_waves).sum())

    print(f"=" * 80)
    print(f"HORDE: {label}")
    print(f"  n_runs={n_runs}, max_waves={max_waves}, recovery={'on' if result['recovery'] else 'off'}")
    print(f"-" * 80)
    print(f"  Median waves survived: {np.median(wow):.0f}")
    print(f"  Mean waves survived:   {wow.mean():.1f}")
    print(f"  P(survives 3 waves):   {(wow > 3).sum()/n_runs:.0%}")
    print(f"  P(survives 5 waves):   {(wow > 5).sum()/n_runs:.0%}")
    print(f"  P(survives all {max_waves}): {n_survived_all/n_runs:.0%}")
    print(f"  Mean cumulative spoils: {result['cumulative_spoils'].mean():.0f}")
    print(f"-" * 80)
    print(f"  Per-wave breakdown:")
    print(f"    {'Wave':>4}  {'Survive%':>8}  {'Avg Size':>8}  {'Avg End':>7}  {'Avg Spoils':>10}")
    for wr in result["wave_results"]:
        print(f"    {wr.wave:>4}  {wr.survival_rate*100:>7.1f}%  "
              f"{wr.avg_size:>8.1f}  {wr.avg_endurance:>7.1f}  {wr.avg_spoils:>10.0f}")


def compare_hordes(results, names=None):
    """Side-by-side comparison of multiple horde results.
    results: list of horde result dicts.
    names: optional list of labels (defaults to army.name).
    Returns a DataFrame.
    """
    import pandas as pd
    rows = []
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        wow = r["wave_of_wipe"]
        max_waves = r["max_waves"]
        be = r["break_even_wave"]
        spoils = r["cumulative_spoils"]
        losses_value = r["cumulative_losses_value"]
        remuster = r["cumulative_remuster_cost"]
        initial_cost = r["initial_muster_cost"]
        net_profit = spoils - initial_cost - remuster
        cost_per_kill_denom = np.where(spoils > 0, spoils / RETINUES[r["army"].retinue]["cost"], 1)  # not exact, but a proxy
        rows.append({
            "army": name,
            "median_waves": np.median(wow),
            "mean_waves": wow.mean(),
            "p_survive_3": (wow > 3).sum() / r["n_runs"],
            "p_survive_5": (wow > 5).sum() / r["n_runs"],
            "p_survive_all": (wow > max_waves).sum() / r["n_runs"],
            "mean_spoils": spoils.mean(),
            "mean_losses_value": losses_value.mean(),
            "initial_muster_cost": initial_cost,
            "mean_remuster_cost": remuster.mean(),
            "mean_net_profit": net_profit.mean(),
            "median_break_even": np.median(be),
            "p_breaks_even": (be <= max_waves).sum() / r["n_runs"],
            "spoils_per_loss_value": spoils.mean() / max(losses_value.mean(), 1),
        })
    return pd.DataFrame(rows)


def plot_economic_curves(results, names=None, title="Economic Profile Over Waves"):
    """Plot cumulative net profit (spoils - costs) over wave count."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        # Reconstruct per-wave cumulative spoils from wave_results
        waves = [wr.wave for wr in r["wave_results"]]
        cumulative = np.cumsum([wr.avg_spoils * wr.survival_rate for wr in r["wave_results"]])
        # Net profit = cumulative spoils - initial muster cost
        net = cumulative - r["initial_muster_cost"]
        ax.plot(waves, net, marker='o', label=f"{name} (initial: {r['initial_muster_cost']:.0f}g)", linewidth=2)
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5, label='Break-even')
    ax.set_xlabel("Wave")
    ax.set_ylabel("Cumulative net profit (gold)")
    ax.set_title(title)
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def plot_break_even_distribution(results, names=None, title="Break-Even Wave Distribution"):
    """Histogram showing at which wave each army recoups its initial muster cost.
    Bars at right edge = 'never broke even within max_waves'.
    """
    import matplotlib.pyplot as plt
    n_armies = len(results)
    fig, ax = plt.subplots(figsize=(11, 6))
    max_waves = max(r["max_waves"] for r in results)
    bins = np.arange(0, max_waves + 3) - 0.5
    width = 0.8 / n_armies
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        be = r["break_even_wave"]
        # Clip at max_waves+1 for "never"
        clipped = np.minimum(be, max_waves + 1)
        offset = (i - (n_armies - 1) / 2) * width
        counts, _ = np.histogram(clipped, bins=bins)
        ax.bar(np.arange(0, max_waves + 2) + offset, counts / r["n_runs"] * 100,
               width=width, label=name, alpha=0.85)
    ax.set_xlabel("Wave (last column = 'never within max waves')")
    ax.set_ylabel("% of runs")
    ax.set_title(title)
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    return fig


def cost_efficiency_table(results, names=None):
    """Per-army cost-efficiency metrics: net profit, ROI, spoils per gold invested, etc."""
    import pandas as pd
    rows = []
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        spoils = r["cumulative_spoils"]
        remuster = r["cumulative_remuster_cost"]
        initial = r["initial_muster_cost"]
        total_cost = initial + remuster
        net = spoils - total_cost
        roi = (spoils / total_cost - 1) * 100  # percent
        rows.append({
            "army": name,
            "initial_cost": initial,
            "mean_spoils": spoils.mean(),
            "mean_total_cost": total_cost.mean(),
            "mean_net": net.mean(),
            "mean_ROI_%": roi.mean(),
            "p_profitable": (net > 0).sum() / r["n_runs"],
            "spoils_per_initial_g": spoils.mean() / initial if initial > 0 else 0,
        })
    return pd.DataFrame(rows).sort_values("mean_ROI_%", ascending=False)


def sustainability_table(results, names=None):
    """Per-army sustainability — how durable across waves."""
    import pandas as pd
    rows = []
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        wow = r["wave_of_wipe"]
        max_waves = r["max_waves"]
        # Wave at which 50% of runs have wiped
        survival_curve = r["survival_curve"]
        below_50 = np.where(survival_curve < 0.5)[0]
        wave_50pct_dead = int(below_50[0]) if len(below_50) > 0 else max_waves + 1
        # Mean final endurance among survivors
        final_size = r["per_run_final_size"]
        final_end = r["per_run_final_endurance"]
        survivors_mask = final_size > 0
        mean_final_end = float(final_end[survivors_mask].mean()) if survivors_mask.any() else 0.0
        rows.append({
            "army": name,
            "median_waves": np.median(wow),
            "mean_waves": wow.mean(),
            "wave_50pct_dead": wave_50pct_dead,
            "p_survives_all": (wow > max_waves).sum() / r["n_runs"],
            "survivors_final_size": float(final_size[survivors_mask].mean()) if survivors_mask.any() else 0.0,
            "survivors_final_end": mean_final_end,
        })
    return pd.DataFrame(rows).sort_values("mean_waves", ascending=False)


def casualty_breakdown(results, names=None):
    """Where did losses come from? Across the campaign, what % of casualties
    were combat / shake / flee, both for the army (own losses) and against the enemies?
    """
    import pandas as pd
    rows = []
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        own_combat = r["total_killed_combat"].mean()
        own_shake = r["total_killed_shake"].mean()
        own_flee = r["total_killed_flee"].mean()
        own_total = own_combat + own_shake + own_flee
        enemy_combat = r["total_kills_inflicted_combat"].mean()
        enemy_shake = r["total_kills_inflicted_shake"].mean()
        enemy_flee = r["total_kills_inflicted_flee"].mean()
        enemy_total = enemy_combat + enemy_shake + enemy_flee
        rows.append({
            "army": name,
            "own_losses_total": own_total,
            "own_pct_combat": (own_combat / own_total * 100) if own_total else 0,
            "own_pct_shake": (own_shake / own_total * 100) if own_total else 0,
            "own_pct_flee": (own_flee / own_total * 100) if own_total else 0,
            "enemy_killed_total": enemy_total,
            "enemy_pct_combat": (enemy_combat / enemy_total * 100) if enemy_total else 0,
            "enemy_pct_shake": (enemy_shake / enemy_total * 100) if enemy_total else 0,
            "enemy_pct_flee": (enemy_flee / enemy_total * 100) if enemy_total else 0,
            "kill_ratio": enemy_total / own_total if own_total else float('inf'),
        })
    return pd.DataFrame(rows).sort_values("kill_ratio", ascending=False)


def cause_of_wipe_breakdown(results, names=None):
    """How did each army die? Returns % of runs that wiped from each cause."""
    import pandas as pd
    rows = []
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        cow = r["cause_of_wipe"]
        n_runs = r["n_runs"]
        rows.append({
            "army": name,
            "pct_alive_end": (cow == 0).sum() / n_runs * 100,
            "pct_wiped_combat": (cow == 1).sum() / n_runs * 100,
            "pct_wiped_shake": (cow == 2).sum() / n_runs * 100,
            "pct_wiped_flee": (cow == 3).sum() / n_runs * 100,
        })
    return pd.DataFrame(rows)


def plot_cause_of_wipe(results, names=None, title="How Each Army Died"):
    """Stacked bar chart: % of runs wiped by each cause."""
    import matplotlib.pyplot as plt
    n_armies = len(results)
    fig, ax = plt.subplots(figsize=(10, 6))
    armies_labels = []
    alive_pct = []
    combat_pct = []
    shake_pct = []
    flee_pct = []
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        cow = r["cause_of_wipe"]
        n_runs = r["n_runs"]
        armies_labels.append(name)
        alive_pct.append((cow == 0).sum() / n_runs * 100)
        combat_pct.append((cow == 1).sum() / n_runs * 100)
        shake_pct.append((cow == 2).sum() / n_runs * 100)
        flee_pct.append((cow == 3).sum() / n_runs * 100)
    x = np.arange(n_armies)
    ax.bar(x, alive_pct, label="Survived all waves", color="#2ca02c")
    ax.bar(x, combat_pct, bottom=alive_pct, label="Wiped by combat", color="#d62728")
    bottom2 = np.array(alive_pct) + np.array(combat_pct)
    ax.bar(x, shake_pct, bottom=bottom2, label="Wiped by shake", color="#ff7f0e")
    bottom3 = bottom2 + np.array(shake_pct)
    ax.bar(x, flee_pct, bottom=bottom3, label="Wiped by flee", color="#9467bd")
    ax.set_xticks(x)
    ax.set_xticklabels(armies_labels, rotation=20, ha="right")
    ax.set_ylabel("% of runs")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_ylim(0, 105)
    plt.tight_layout()
    return fig


def plot_survival_curves(results, names=None, title="Horde Survival Curves"):
    """Plot survival % over wave count for multiple armies."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        curve = r["survival_curve"]
        waves = np.arange(len(curve))
        ax.plot(waves, curve * 100, marker='o', label=name, linewidth=2)
    ax.set_xlabel("Wave")
    ax.set_ylabel("% of runs still alive")
    ax.set_title(title)
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-2, 102)
    plt.tight_layout()
    return fig


def plot_size_over_waves(results, names=None, title="Army Size Over Waves (survivors only)"):
    """Plot avg army size remaining at the END of each wave (survivors only)."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        waves = [wr.wave for wr in r["wave_results"]]
        sizes = [wr.avg_size for wr in r["wave_results"]]
        ax.plot(waves, sizes, marker='o', label=name, linewidth=2)
    ax.set_xlabel("Wave")
    ax.set_ylabel("Avg army size (survivors only)")
    ax.set_title(title)
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def plot_spoils_over_waves(results, names=None, title="Cumulative Spoils Over Waves"):
    """Plot cumulative spoils accumulating over wave count."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, r in enumerate(results):
        name = (names[i] if names else r["army"].name)
        # Cumulative spoils per wave = sum of avg_spoils up to wave k, weighted by survival
        waves = [wr.wave for wr in r["wave_results"]]
        # Approximate: each wave contributes avg_spoils * survival_rate to the mean cumulative
        cumulative = np.cumsum([wr.avg_spoils * wr.survival_rate for wr in r["wave_results"]])
        ax.plot(waves, cumulative, marker='o', label=name, linewidth=2)
    ax.set_xlabel("Wave")
    ax.set_ylabel("Mean cumulative spoils (gold)")
    ax.set_title(title)
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig
