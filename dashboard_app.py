"""
Streamlit rules sandbox for local Renown balance experiments.

Run with:
    python -m streamlit run dashboard_app.py
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
import json
import os
import random
import signal
import subprocess
import sys
import time
from typing import Any

import numpy as np
import pandas as pd

# Import tournament_vec before default_rules so the dashboard mirrors the notebook's
# normalized tactic matrix baseline.
import tournament_vec  # noqa: F401
import loadouts
import playstyles
from rules_config import DOMAIN_KEYS, TIER_VALUES, RulesConfig, default_rules, known_tags
from vectorized_combat import invalidate_tactic_tables, run_matchup_vec

try:
    import streamlit as st
except ModuleNotFoundError:  # Allows smoke imports before dashboard deps are installed.
    st = None


OUT_ROOT = Path("lab_out_dashboard")
SCENARIO_DIR = OUT_ROOT / "scenarios"
RUN_DIR = OUT_ROOT / "runs"
UNIQUE_BUILDINGS = ("ABF", "Royal Pavilion", "Preceptory", "Ministry", "Outrider Intercept Post")
FULL_RUN_TYPES = {
    "all_compute": "All compute sections",
    "main": "Main tournament",
    "playstyle": "Playstyle tournament",
    "forced_tactics": "Forced tactics sweep",
    "horde": "Horde survival sweep",
}
TERMINAL_JOB_STATUSES = {"complete", "failed", "cancelled"}
RETINUE_COLORS = {
    "Levy": "#777777",
    "Man-at-Arms": "#2f80ed",
    "Sergeant": "#c79a00",
    "Knight Templar": "#c43c39",
}


def loadout_identity(ld):
    return (
        ld.retinue,
        ld.weapon or "",
        ld.shield or "",
        ld.armor,
        ld.ranged or "",
        bool(ld.has_tiltyard),
        tuple(sorted(ld.extra_tags)),
        tuple(sorted(getattr(ld, "pursuits", frozenset()))),
    )


def loadout_chart_fields(ld, prefix=""):
    return {
        f"{prefix}retinue": ld.retinue,
        f"{prefix}weapon": ld.weapon or "",
        f"{prefix}shield": ld.shield or "None",
        f"{prefix}armor": ld.armor,
        f"{prefix}ranged": ld.ranged or "None",
        f"{prefix}tiltyard": bool(ld.has_tiltyard),
        f"{prefix}playstyle": ld.playstyle or "Random",
        f"{prefix}tags": ",".join(ld.extra_tags),
        f"{prefix}pursuits": "|".join(sorted(getattr(ld, "pursuits", frozenset()))),
        f"{prefix}mpc": getattr(ld, "military_pursuit_count", 0),
        f"{prefix}domain": getattr(ld, "domain_count", 0),
        f"{prefix}upkeep": getattr(ld, "upkeep_per_retinue", 0),
    }


def pool_to_frame(pool):
    return pd.DataFrame([
        {
            "name": ld.name,
            "retinue": ld.retinue,
            "weapon": ld.weapon or "",
            "shield": ld.shield or "",
            "armor": ld.armor,
            "ranged": ld.ranged or "",
            "tiltyard": bool(ld.has_tiltyard),
            "size": ld.size,
            "upkeep": ld.upkeep_per_retinue,
            "mpc": getattr(ld, "military_pursuit_count", 0),
            "domain": getattr(ld, "domain_count", 0),
            "tags": ",".join(ld.extra_tags),
            "pursuits": "|".join(sorted(getattr(ld, "pursuits", frozenset()))),
            "playstyle": ld.playstyle or "Random",
        }
        for ld in pool
    ])


def matchup_summary(result, n_runs):
    decisive = result["a_wins"] + result["b_wins"]
    return {
        "a_wins": result["a_wins"],
        "b_wins": result["b_wins"],
        "mut_wipe": result["mut_wipe"],
        "indecisive": result["indecisive"],
        "win_rate": result["a_wins"] / n_runs if n_runs else 0.0,
        "decisive_win_rate": result["a_wins"] / decisive if decisive else 0.0,
        "avg_skirm": result["avg_skirm"],
        "avg_a_rem": result["avg_a_rem"],
        "avg_b_rem": result["avg_b_rem"],
    }


def invalidate_rule_caches(rules):
    invalidate_tactic_tables(rules)
    playstyles.invalidate_counter_table(rules)


def rules_payload(rules):
    return json.dumps(rules.to_dict(), sort_keys=True)


def int_cell(value, default=0):
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass
    return int(value)


def float_cell(value, default=0.0):
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass
    return float(value)


def selected_list(value):
    if isinstance(value, (list, tuple, set)):
        return [str(v) for v in value if str(v)]
    if value is None:
        return []
    try:
        if pd.isna(value):
            return []
    except (TypeError, ValueError):
        pass
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [str(v) for v in parsed if str(v)]
        return [v.strip() for v in raw.split(",") if v.strip()]
    return []


def tier_value(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    return text or None


def read_json(path):
    path = Path(path)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def full_run_dirs():
    if not RUN_DIR.exists():
        return []
    return sorted(
        [p for p in RUN_DIR.iterdir() if p.is_dir() and (p / "config.json").exists()],
        key=lambda p: p.name,
        reverse=True,
    )


def format_run_label(run_dir):
    config = read_json(run_dir / "config.json") or {}
    progress = read_json(run_dir / "progress.json") or {}
    run_type = FULL_RUN_TYPES.get(config.get("run_type"), config.get("run_type", "unknown"))
    status = progress.get("status", "unknown")
    return f"{run_dir.name} | {run_type} | {status}"


def create_full_run_config(
    rules,
    run_type,
    n_workers,
    seed,
    n_runs_main,
    n_runs_playstyle,
    n_runs_forced,
    n_runs_horde,
    forced_sample_size,
    horde_sample_size,
    horde_waves,
):
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUN_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    rules_path = run_dir / "rules.json"
    rules.to_json(rules_path)
    config = {
        "run_id": run_id,
        "run_type": run_type,
        "rules_path": str(rules_path),
        "output_dir": str(run_dir),
        "n_workers": int(n_workers),
        "seed": int(seed),
        "n_runs_main": int(n_runs_main),
        "n_runs_playstyle": int(n_runs_playstyle),
        "n_runs_forced": int(n_runs_forced),
        "n_runs_horde": int(n_runs_horde),
        "forced_sample_size": int(forced_sample_size),
        "horde_sample_size": int(horde_sample_size),
        "horde_waves": int(horde_waves),
        "storage_format": "parquet",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    config_path = run_dir / "config.json"
    write_json(config_path, config)
    write_json(run_dir / "progress.json", {
        "status": "queued",
        "phase": "queued",
        "completed": 0,
        "total": 1,
        "elapsed_sec": 0,
        "eta_sec": 0,
        "matchups_per_sec": 0,
        "battles_per_sec": 0,
        "current_label": "",
        "last_update": datetime.now().isoformat(timespec="seconds"),
        "error": "",
        "pid": None,
        "artifacts": {},
    })
    return run_dir, config_path


def launch_full_run(config_path, run_dir):
    log_path = Path(run_dir) / "run.log"
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    log_file = open(log_path, "ab")
    try:
        proc = subprocess.Popen(
            [sys.executable, "dashboard_full_run.py", "--config", str(config_path)],
            cwd=str(Path.cwd()),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
        )
    finally:
        log_file.close()
    progress = read_json(Path(run_dir) / "progress.json") or {}
    progress["pid"] = str(proc.pid)
    progress["status"] = "queued"
    write_json(Path(run_dir) / "progress.json", progress)
    return proc.pid


def request_full_run_cancel(run_dir):
    run_dir = Path(run_dir)
    (run_dir / "cancel.request").write_text(datetime.now().isoformat(timespec="seconds"), encoding="utf-8")


def force_terminate_pid(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), signal.SIGTERM)
        return True
    except (OSError, ValueError):
        return False


def tail_text(path, max_bytes=12000):
    path = Path(path)
    if not path.exists():
        return ""
    with open(path, "rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek(max(0, size - max_bytes))
        return handle.read().decode("utf-8", errors="replace")


def available_parquet_tables(run_dir):
    data_dir = Path(run_dir) / "data"
    tables = []
    table_specs = [
        ("Summary: main", "full_summary", data_dir / "summary_main.parquet"),
        ("Summary: playstyle", "full_summary", data_dir / "summary_playstyle.parquet"),
        ("Tactic matrix: main", "full_tactic_matrix", data_dir / "tactic_matrix_main.parquet"),
        ("Tactic matrix: playstyle", "full_tactic_matrix", data_dir / "tactic_matrix_playstyle.parquet"),
        ("Forced tactics", "forced_tactics", data_dir / "forced_tactics.parquet"),
        ("Horde survival", "horde_summary", data_dir / "horde_survival.parquet"),
        ("Matchups: main", "matchups_dataset", data_dir / "matchups_main"),
        ("Matchups: playstyle", "matchups_dataset", data_dir / "matchups_playstyle"),
    ]
    for label, kind, path in table_specs:
        if path.exists():
            tables.append({"label": label, "kind": kind, "path": path})
    return tables


def parquet_schema_columns(path):
    try:
        import pyarrow.dataset as ds
    except ModuleNotFoundError:
        return []
    dataset = ds.dataset(str(path), format="parquet")
    return dataset.schema.names


def read_matchup_dataset(path, columns, a_name="", b_name="", limit=5000):
    import pyarrow.dataset as ds

    dataset = ds.dataset(str(path), format="parquet")
    filter_expr = None
    if a_name:
        filter_expr = ds.field("a_name") == a_name
    if b_name:
        expr = ds.field("b_name") == b_name
        filter_expr = expr if filter_expr is None else filter_expr & expr
    scanner = dataset.scanner(columns=columns or None, filter=filter_expr)
    try:
        table = scanner.head(int(limit))
    except AttributeError:
        table = scanner.to_table().slice(0, int(limit))
    return table.to_pandas()


if st is not None:
    @st.cache_data(show_spinner=False)
    def cached_base_pool():
        return loadouts.archetype_pool()

    @st.cache_data(show_spinner=True)
    def cached_scenario_pool(payload):
        rules = RulesConfig.from_dict(json.loads(payload))
        invalidate_rule_caches(rules)
        return loadouts.archetype_pool(rules=rules)
else:
    def cached_base_pool():
        return loadouts.archetype_pool()

    def cached_scenario_pool(payload):
        rules = RulesConfig.from_dict(json.loads(payload))
        invalidate_rule_caches(rules)
        return loadouts.archetype_pool(rules=rules)


def scenario_pool(rules):
    return cached_scenario_pool(rules_payload(rules))


def paired_matchup(base_a, base_b, scenario_a, scenario_b, scenario_rules, n_runs, seed):
    baseline = run_matchup_vec(
        base_a, base_b, n_runs=n_runs, seed=seed,
        a_playstyle=base_a.playstyle, b_playstyle=base_b.playstyle,
    )
    scenario = run_matchup_vec(
        scenario_a, scenario_b, n_runs=n_runs, seed=seed,
        a_playstyle=scenario_a.playstyle, b_playstyle=scenario_b.playstyle,
        rules=scenario_rules,
    )
    b = matchup_summary(baseline, n_runs)
    s = matchup_summary(scenario, n_runs)
    return pd.DataFrame([
        {"run": "baseline", **b},
        {"run": "scenario", **s},
        {"run": "delta", **{k: s[k] - b[k] for k in b}},
    ])


def unique_conflict(ld_a, ld_b):
    pa = getattr(ld_a, "pursuits", frozenset())
    pb = getattr(ld_b, "pursuits", frozenset())
    return any(building in pa and building in pb for building in UNIQUE_BUILDINGS)


def paired_sample_tournament(base_pool, scenario_pool_, scenario_rules, n_runs, seed):
    base_by_key = {loadout_identity(ld): ld for ld in base_pool}
    scen_by_key = {loadout_identity(ld): ld for ld in scenario_pool_}
    common_keys = [k for k in base_by_key if k in scen_by_key]
    rows = []
    for i, key_a in enumerate(common_keys):
        base_a = base_by_key[key_a]
        scen_a = scen_by_key[key_a]
        b_wins = s_wins = b_losses = s_losses = 0
        b_total = s_total = 0
        for j, key_b in enumerate(common_keys):
            base_b = base_by_key[key_b]
            scen_b = scen_by_key[key_b]
            if i != j and (unique_conflict(base_a, base_b) or unique_conflict(scen_a, scen_b)):
                continue
            run_seed = seed + i * len(common_keys) + j
            b_res = run_matchup_vec(base_a, base_b, n_runs=n_runs, seed=run_seed,
                                    a_playstyle=base_a.playstyle, b_playstyle=base_b.playstyle)
            s_res = run_matchup_vec(scen_a, scen_b, n_runs=n_runs, seed=run_seed,
                                    a_playstyle=scen_a.playstyle, b_playstyle=scen_b.playstyle,
                                    rules=scenario_rules)
            b_wins += b_res["a_wins"]
            b_losses += b_res["b_wins"]
            b_total += n_runs
            s_wins += s_res["a_wins"]
            s_losses += s_res["b_wins"]
            s_total += n_runs
        b_wr = b_wins / b_total if b_total else 0.0
        s_wr = s_wins / s_total if s_total else 0.0
        rows.append({
            "name": base_a.name,
            **loadout_chart_fields(base_a, "baseline_"),
            **loadout_chart_fields(scen_a, "scenario_"),
            "retinue": base_a.retinue,
            "weapon": base_a.weapon or "",
            "shield": base_a.shield or "None",
            "armor": base_a.armor,
            "ranged": base_a.ranged or "None",
            "playstyle": base_a.playstyle or "Random",
            "mpc": getattr(base_a, "military_pursuit_count", 0),
            "domain": getattr(base_a, "domain_count", 0),
            "upkeep": getattr(base_a, "upkeep_per_retinue", 0),
            "baseline_win_rate": b_wr,
            "scenario_win_rate": s_wr,
            "delta_win_rate": s_wr - b_wr,
            "baseline_decisive_rate": (b_wins + b_losses) / b_total if b_total else 0.0,
            "scenario_decisive_rate": (s_wins + s_losses) / s_total if s_total else 0.0,
            "delta_decisive_rate": (
                ((s_wins + s_losses) / s_total if s_total else 0.0)
                - ((b_wins + b_losses) / b_total if b_total else 0.0)
            ),
            "matchups": b_total // n_runs if n_runs else 0,
        })
    return pd.DataFrame(rows).sort_values("delta_win_rate", ascending=False)


def with_forced_tactic_playstyles(rules):
    rules_copy = deepcopy(rules)
    for idx, tactic in enumerate(rules_copy.tactics):
        weights = [0.0] * len(rules_copy.tactics)
        weights[idx] = 1.0
        rules_copy.static_playstyles[f"_Forced_{idx}"] = {
            "primaries": [idx],
            "weights": weights,
            "initiate_rate": 0.5,
            "disable_fatigue_fallback": True,
            "description": f"Forced {tactic}",
        }
    return rules_copy


def forced_tactic_name(idx):
    return f"_Forced_{idx}"


def paired_tactic_heatmap(base_a, base_b, scenario_a, scenario_b, scenario_rules, n_runs, seed):
    base_rules = with_forced_tactic_playstyles(default_rules())
    scen_rules = with_forced_tactic_playstyles(scenario_rules)
    invalidate_rule_caches(base_rules)
    invalidate_rule_caches(scen_rules)

    rows = []
    n_tactics = len(base_rules.tactics)
    for i, a_tactic in enumerate(base_rules.tactics):
        for j, b_tactic in enumerate(base_rules.tactics):
            run_seed = seed + i * n_tactics + j
            baseline = run_matchup_vec(
                base_a, base_b,
                n_runs=n_runs,
                seed=run_seed,
                a_playstyle=forced_tactic_name(i),
                b_playstyle=forced_tactic_name(j),
                rules=base_rules,
            )
            scenario = run_matchup_vec(
                scenario_a, scenario_b,
                n_runs=n_runs,
                seed=run_seed,
                a_playstyle=forced_tactic_name(i),
                b_playstyle=forced_tactic_name(j),
                rules=scen_rules,
            )
            b_wr = baseline["a_wins"] / n_runs if n_runs else 0.0
            s_wr = scenario["a_wins"] / n_runs if n_runs else 0.0
            b_indec = baseline["indecisive"] / n_runs if n_runs else 0.0
            s_indec = scenario["indecisive"] / n_runs if n_runs else 0.0
            rows.append({
                "a_tactic": a_tactic,
                "b_tactic": b_tactic,
                "baseline_win_rate": b_wr,
                "scenario_win_rate": s_wr,
                "delta_win_rate": s_wr - b_wr,
                "baseline_indecisive_rate": b_indec,
                "scenario_indecisive_rate": s_indec,
                "delta_indecisive_rate": s_indec - b_indec,
            })
    return pd.DataFrame(rows)


def paired_horde(base_army, scenario_army, base_opponents, scenario_opponents, scenario_rules,
                 n_runs, max_waves, seed, recovery=True):
    import horde_mode

    baseline = horde_mode.run_horde(
        base_army, base_opponents,
        n_runs=n_runs,
        max_waves=max_waves,
        recovery=recovery,
        seed=seed,
        rules=default_rules(),
    )
    scenario = horde_mode.run_horde(
        scenario_army, scenario_opponents,
        n_runs=n_runs,
        max_waves=max_waves,
        recovery=recovery,
        seed=seed,
        rules=scenario_rules,
    )
    summary = horde_mode.compare_hordes(
        [baseline, scenario],
        names=["baseline", "scenario"],
        rules=scenario_rules,
    )
    return summary, {"baseline": baseline, "scenario": scenario}


def edit_retinues(rules):
    rows = [{"name": name, **profile} for name, profile in rules.retinues.items()]
    edited = st.data_editor(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_order=["name", "cost", "to_hit", "endurance", "shaking", "unshakable"],
        column_config={
            "name": st.column_config.TextColumn("Name", disabled=True, pinned=True),
            "cost": st.column_config.NumberColumn("Cost", min_value=0, step=1, required=True),
            "to_hit": st.column_config.NumberColumn("To hit", min_value=1, step=1, required=True),
            "endurance": st.column_config.NumberColumn("Endurance", min_value=1, step=1, required=True),
            "shaking": st.column_config.NumberColumn("Shaking", min_value=0, step=1, required=True),
            "unshakable": st.column_config.CheckboxColumn("Unshakable"),
        },
        key="retinues_editor",
    )
    for _, row in edited.iterrows():
        name = row["name"]
        rules.retinues[name] = {
            "cost": int_cell(row["cost"]),
            "to_hit": int_cell(row["to_hit"], 1),
            "endurance": int_cell(row["endurance"], 1),
            "shaking": int_cell(row["shaking"]),
            "unshakable": bool(row["unshakable"]),
        }


def edit_equipment_table(label, table, numeric_fields):
    rows = []
    for name, profile in table.items():
        rows.append({
            "name": "" if name is None else name,
            **{field: profile.get(field) for field in numeric_fields},
            "tier": profile.get("tier") or "",
            "tags": list(profile.get("tags", [])),
        })
    column_config = {
        "name": st.column_config.TextColumn("Name", disabled=True, pinned=True),
        "tier": st.column_config.SelectboxColumn("Tier", options=["", *TIER_VALUES]),
        "tags": st.column_config.MultiselectColumn(
            "Tags",
            options=known_tags(),
            accept_new_options=False,
        ),
    }
    for field in numeric_fields:
        column_config[field] = st.column_config.NumberColumn(field, step=1, required=True)
    edited = st.data_editor(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_order=["name", *numeric_fields, "tier", "tags"],
        column_config=column_config,
        key=f"{label}_editor",
    )
    next_table = {}
    for _, row in edited.iterrows():
        name = None if row["name"] == "" and label == "shields" else row["name"]
        profile = {field: int_cell(row[field]) for field in numeric_fields}
        profile["tier"] = tier_value(row["tier"])
        profile["tags"] = selected_list(row["tags"])
        next_table[name] = profile
    table.clear()
    table.update(next_table)


UPKEEP_EFFECT_TYPES = ("flat", "if_shield", "if_ranged", "if_armor_in")


def upkeep_effect_rows(effects):
    rows = []
    for effect in effects:
        for effect_type, value in effect.items():
            armors = []
            amount = value
            if effect_type == "if_armor_in":
                armors, amount = value
            rows.append({
                "type": effect_type,
                "amount": int_cell(amount),
                "armors": list(armors),
            })
    return pd.DataFrame(rows, columns=["type", "amount", "armors"])


def rows_to_upkeep_effects(edited):
    effects = []
    for _, row in edited.iterrows():
        effect_type = str(row.get("type", "") or "").strip()
        if effect_type not in UPKEEP_EFFECT_TYPES:
            continue
        amount = int_cell(row.get("amount"))
        if effect_type == "if_armor_in":
            armors = selected_list(row.get("armors"))
            if not armors:
                continue
            effects.append({"if_armor_in": [armors, amount]})
        else:
            effects.append({effect_type: amount})
    return effects


def signed_value(value):
    value = int_cell(value)
    return f"+{value}" if value > 0 else str(value)


def side_mod_summary(mods):
    parts = []
    for key, label in [("I", "Init"), ("TH", "Hit"), ("TS", "Save")]:
        value = int_cell(mods.get(key, 0))
        if value:
            parts.append(f"{label} {signed_value(value)}")
    return ", ".join(parts) if parts else "No modifier"


def flow_summary(a_mods, b_mods):
    ends = a_mods.get("end", False) or b_mods.get("end", False)
    no_combat = a_mods.get("no_combat", False) or b_mods.get("no_combat", False)
    spends_endurance = no_combat and (
        a_mods.get("endurance_loss", True) or b_mods.get("endurance_loss", True)
    )
    parts = []
    if ends:
        parts.append("Battle ends")
    if no_combat:
        parts.append("No combat, endurance spent" if spends_endurance else "No combat, no endurance")
    return "; ".join(parts) if parts else "Combat proceeds"


def tactic_matrix_overview(rules):
    rows = []
    for a_tactic in rules.tactics:
        row = {"A tactic": a_tactic}
        for b_tactic in rules.tactics:
            a_mods, b_mods = rules.tactic_matrix[(a_tactic, b_tactic)]
            summary = f"A: {side_mod_summary(a_mods)} | B: {side_mod_summary(b_mods)}"
            flow = flow_summary(a_mods, b_mods)
            if flow != "Combat proceeds":
                summary = f"{summary} | {flow}"
            row[b_tactic] = summary
        rows.append(row)
    return pd.DataFrame(rows).set_index("A tactic")


def selected_tactic_preview(a_tactic, b_tactic, a_mods, b_mods):
    return pd.DataFrame([
        {
            "side": "A",
            "tactic": a_tactic,
            "initiative bonus": signed_value(a_mods.get("I", 0)),
            "hit bonus": signed_value(a_mods.get("TH", 0)),
            "save bonus": signed_value(a_mods.get("TS", 0)),
        },
        {
            "side": "B",
            "tactic": b_tactic,
            "initiative bonus": signed_value(b_mods.get("I", 0)),
            "hit bonus": signed_value(b_mods.get("TH", 0)),
            "save bonus": signed_value(b_mods.get("TS", 0)),
        },
    ])


def edit_pursuits(rules):
    rows = []
    for name, profile in rules.pursuits_info.items():
        domain = profile.get("domain", {})
        rows.append({
            "name": name,
            "cost": profile.get("cost", 0),
            "prereqs": list(profile.get("prereqs", [])),
            **{f"domain_{domain_key}": int(domain.get(domain_key, 0)) for domain_key in DOMAIN_KEYS},
            "tags": list(profile.get("tags", [])),
        })
    pursuit_options = list(rules.pursuits_info)
    edited = st.data_editor(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_order=["name", "cost", "prereqs", *[f"domain_{d}" for d in DOMAIN_KEYS], "tags"],
        column_config={
            "name": st.column_config.TextColumn("Name", disabled=True, pinned=True),
            "cost": st.column_config.NumberColumn("Cost", min_value=0, step=1, required=True),
            "prereqs": st.column_config.MultiselectColumn(
                "Prereqs",
                options=pursuit_options,
                accept_new_options=False,
            ),
            **{
                f"domain_{domain_key}": st.column_config.NumberColumn(
                    domain_key,
                    min_value=0,
                    step=1,
                    required=True,
                )
                for domain_key in DOMAIN_KEYS
            },
            "tags": st.column_config.MultiselectColumn(
                "Tags",
                options=known_tags(),
                accept_new_options=False,
            ),
        },
        key="pursuits_editor",
    )
    next_table = {}
    for _, row in edited.iterrows():
        domain = {
            domain_key: int_cell(row[f"domain_{domain_key}"])
            for domain_key in DOMAIN_KEYS
            if int_cell(row[f"domain_{domain_key}"])
        }
        existing = rules.pursuits_info[row["name"]]
        next_table[row["name"]] = {
            "cost": int_cell(row["cost"]),
            "prereqs": selected_list(row["prereqs"]),
            "domain": domain,
            "tags": selected_list(row["tags"]),
        }
        if existing.get("upkeep_effects"):
            next_table[row["name"]]["upkeep_effects"] = existing["upkeep_effects"]
    rules.pursuits_info = next_table

    pursuit_name = st.selectbox("Upkeep effects", pursuit_options, key="upkeep_pursuit_editor")
    edited_effects = st.data_editor(
        upkeep_effect_rows(rules.pursuits_info[pursuit_name].get("upkeep_effects", [])),
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "type": st.column_config.SelectboxColumn("Type", options=UPKEEP_EFFECT_TYPES, required=True),
            "amount": st.column_config.NumberColumn("Amount", min_value=0, step=1, required=True),
            "armors": st.column_config.MultiselectColumn(
                "Armors",
                options=list(rules.armors),
                accept_new_options=False,
            ),
        },
        key="upkeep_effects_editor",
    )
    effects = rows_to_upkeep_effects(edited_effects)
    if effects:
        rules.pursuits_info[pursuit_name]["upkeep_effects"] = effects
    else:
        rules.pursuits_info[pursuit_name].pop("upkeep_effects", None)


def edit_tactic_matrix(rules):
    with st.expander("Tactic matrix overview", expanded=True):
        st.dataframe(
            pd.DataFrame([
                {"field": "Init", "meaning": "initiative modifier", "positive": "acts earlier"},
                {"field": "Hit", "meaning": "to-hit modifier", "positive": "easier to hit"},
                {"field": "Save", "meaning": "armor save modifier", "positive": "easier to save"},
            ]),
            use_container_width=True,
            hide_index=True,
        )
        st.dataframe(tactic_matrix_overview(rules), use_container_width=True, height=300)

    a_tactic = st.selectbox("A tactic", rules.tactics, key="a_tactic_editor")
    b_tactic = st.selectbox("B tactic", rules.tactics, key="b_tactic_editor")
    a_mods, b_mods = deepcopy(rules.tactic_matrix[(a_tactic, b_tactic)])

    st.dataframe(
        selected_tactic_preview(a_tactic, b_tactic, a_mods, b_mods),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(flow_summary(a_mods, b_mods))

    flow_cols = st.columns(3)
    pair_end = flow_cols[0].checkbox(
        "Battle ends",
        value=bool(a_mods.get("end", False) or b_mods.get("end", False)),
        help="If enabled, this tactic pairing ends the battle after tactics are revealed.",
    )
    pair_no_combat = flow_cols[1].checkbox(
        "No combat",
        value=bool(a_mods.get("no_combat", False) or b_mods.get("no_combat", False)),
        help="If enabled, no strikes, shaking, or rout are resolved for this skirmish.",
    )
    pair_endurance_loss = flow_cols[2].checkbox(
        "Spend endurance on no combat",
        value=bool(a_mods.get("endurance_loss", True) or b_mods.get("endurance_loss", True)),
        help="Only applies when no combat is enabled.",
    )

    cols = st.columns(2)
    for side, mods, col in [("A", a_mods, cols[0]), ("B", b_mods, cols[1])]:
        with col:
            st.subheader(side)
            mods["I"] = st.number_input(
                f"{side} initiative bonus",
                value=int(mods.get("I", 0)),
                step=1,
                help="Positive values make this side more likely to strike first.",
            )
            mods["TH"] = st.number_input(
                f"{side} hit bonus",
                value=int(mods.get("TH", 0)),
                step=1,
                help="Positive values lower this side's required hit roll; negative values raise it.",
            )
            mods["TS"] = st.number_input(
                f"{side} save bonus",
                value=int(mods.get("TS", 0)),
                step=1,
                help="Positive values lower this side's required armor save roll; negative values raise it.",
            )
            mods["end"] = pair_end
            mods["no_combat"] = pair_no_combat
            mods["endurance_loss"] = pair_endurance_loss
    rules.tactic_matrix[(a_tactic, b_tactic)] = (a_mods, b_mods)
    invalidate_rule_caches(rules)


def edit_playstyles(rules):
    tactic_names = rules.tactics
    static_rows = []
    for name, profile in rules.static_playstyles.items():
        static_rows.append({
            "name": name,
            "primaries": [tactic_names[i] for i in profile.get("primaries", [])],
            "initiate_rate": float(profile.get("initiate_rate", 0.5)),
        })
    edited_static = st.data_editor(
        pd.DataFrame(static_rows),
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "name": st.column_config.TextColumn("Name", disabled=True, pinned=True),
            "primaries": st.column_config.MultiselectColumn(
                "Primary tactics",
                options=tactic_names,
                accept_new_options=False,
            ),
            "initiate_rate": st.column_config.NumberColumn(
                "Initiate rate",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                required=True,
            ),
        },
        key="static_ps_editor",
    )
    for _, row in edited_static.iterrows():
        primaries = [tactic_names.index(tactic) for tactic in selected_list(row["primaries"])]
        rules.static_playstyles[row["name"]]["primaries"] = primaries
        rules.static_playstyles[row["name"]]["initiate_rate"] = float_cell(row["initiate_rate"], 0.5)

    adaptive_rows = [
        {"name": name, "initiate_rate": float(profile.get("initiate_rate", 0.5))}
        for name, profile in rules.adaptive_playstyles.items()
    ]
    edited_adaptive = st.data_editor(
        pd.DataFrame(adaptive_rows),
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "name": st.column_config.TextColumn("Name", disabled=True, pinned=True),
            "initiate_rate": st.column_config.NumberColumn(
                "Initiate rate",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                required=True,
            ),
        },
        key="adaptive_ps_editor",
    )
    for _, row in edited_adaptive.iterrows():
        rules.adaptive_playstyles[row["name"]]["initiate_rate"] = float_cell(row["initiate_rate"], 0.5)


def edit_mechanics(rules):
    mech = rules.mechanics
    cols = st.columns(3)
    with cols[0]:
        mech.initiative_min = st.number_input("Initiative min", value=mech.initiative_min, step=1)
        mech.initiative_max = st.number_input("Initiative max", value=mech.initiative_max, step=1)
        mech.front_line_cap = st.number_input("Front line cap", min_value=1, value=mech.front_line_cap, step=1)
        mech.reserve_cap = st.number_input("Reserve cap", min_value=0, value=mech.reserve_cap, step=1)
    with cols[1]:
        mech.field_cap = st.number_input("Field cap", min_value=1, value=mech.field_cap, step=1)
        mech.max_skirmishes = st.number_input("Max skirmishes", min_value=1, value=mech.max_skirmishes, step=1)
        mech.rout_threshold = st.number_input("Rout threshold", value=mech.rout_threshold, step=1)
        mech.parry_threshold = st.number_input("Parry threshold", min_value=2, max_value=7, value=mech.parry_threshold, step=1)
    with cols[2]:
        mech.regen_rend_delta = st.number_input("Rend regen penalty", min_value=0, value=mech.regen_rend_delta, step=1)
        mech.regen_rend_cap = st.number_input("Rend regen cap", min_value=2, value=mech.regen_rend_cap, step=1)
        mech.ministry_counter_weight = st.slider("Ministry counter weight", 0.0, 1.0, float(mech.ministry_counter_weight), 0.01)
        mech.apothecary_heal_casualties_per_retinue = st.number_input("Apo heal ratio", min_value=1, value=mech.apothecary_heal_casualties_per_retinue, step=1)
    mech.fatigue_fallback_weight_fat1 = st.slider("Fall Back weight at fatigue 1", 0.0, 1.0, float(mech.fatigue_fallback_weight_fat1), 0.01)
    mech.fatigue_fallback_weight_fat2plus = st.slider("Fall Back weight at fatigue 2+", 0.0, 1.0, float(mech.fatigue_fallback_weight_fat2plus), 0.01)


def rules_explorer_tab():
    rows = [
        ("Static data", "retinues, weapons, ranged, shields, armor, tactics", "renown_combat tables"),
        ("Derived loadouts", "retinue, tier, gear, tags, MPC, domain, upkeep", "loadouts pursuit graph"),
        ("Runtime combat", "initiative, front line, saves, fatigue, rout, keyword effects", "vectorized_combat inner loop"),
        ("Tactic choice", "static/adaptive playstyle weights and Ministry counters", "playstyles"),
        ("Analysis", "upkeep, spoils, win rates, derived metrics", "analysis"),
    ]
    st.dataframe(pd.DataFrame(rows, columns=["surface", "contains", "source"]), use_container_width=True)


def scenario_editor_tab(rules):
    rules.name = st.text_input("Scenario name", value=rules.name)
    rules.description = st.text_area("Description", value=rules.description, height=80)
    section = st.radio(
        "Edit section",
        ["Mechanics", "Retinues", "Weapons", "Ranged", "Shields", "Armor", "Pursuits", "Tactic Matrix", "Playstyles"],
        horizontal=True,
    )
    if section == "Mechanics":
        edit_mechanics(rules)
    elif section == "Retinues":
        edit_retinues(rules)
    elif section == "Weapons":
        edit_equipment_table("weapons", rules.weapons, ["ap", "init"])
    elif section == "Ranged":
        edit_equipment_table("ranged", rules.ranged, ["ap", "init"])
    elif section == "Shields":
        edit_equipment_table("shields", rules.shields, ["save_bonus", "init"])
    elif section == "Armor":
        edit_equipment_table("armors", rules.armors, ["save"])
    elif section == "Pursuits":
        edit_pursuits(rules)
    elif section == "Tactic Matrix":
        edit_tactic_matrix(rules)
    elif section == "Playstyles":
        edit_playstyles(rules)

    cols = st.columns(4)
    with cols[0]:
        if st.button("Validate"):
            try:
                rules.validate()
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Scenario is valid.")
    with cols[1]:
        if st.button("Reset"):
            st.session_state.rules = default_rules()
            st.rerun()
    with cols[2]:
        filename = f"{rules.name.strip().replace(' ', '_') or 'scenario'}.json"
        if st.button("Save JSON"):
            path = SCENARIO_DIR / filename
            try:
                rules.to_json(path)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success(f"Saved {path}")
    with cols[3]:
        uploaded = st.file_uploader("Load JSON", type=["json"])
        if uploaded is not None:
            try:
                data = json.loads(uploaded.getvalue().decode("utf-8"))
                st.session_state.rules = RulesConfig.from_dict(data)
            except (json.JSONDecodeError, ValueError) as exc:
                st.error(str(exc))
            else:
                st.rerun()


def loadout_preview_tab(rules):
    base_pool = cached_base_pool()
    scen_pool = scenario_pool(rules)
    base_df = pool_to_frame(base_pool)
    scen_df = pool_to_frame(scen_pool)
    cols = st.columns(4)
    cols[0].metric("Baseline loadouts", len(base_df))
    cols[1].metric("Scenario loadouts", len(scen_df), len(scen_df) - len(base_df))
    cols[2].metric("Baseline avg upkeep", round(base_df["upkeep"].mean(), 2))
    cols[3].metric("Scenario avg upkeep", round(scen_df["upkeep"].mean(), 2), round(scen_df["upkeep"].mean() - base_df["upkeep"].mean(), 2))

    st.dataframe(
        scen_df.groupby(["retinue", "mpc"]).size().reset_index(name="loadouts"),
        use_container_width=True,
    )
    query = st.text_input("Filter loadouts")
    shown = scen_df
    if query:
        shown = shown[shown.apply(lambda row: query.lower() in " ".join(map(str, row.values)).lower(), axis=1)]
    st.dataframe(shown.head(300), use_container_width=True)


def sandbox_tab(rules):
    base_pool = cached_base_pool()
    scen_pool = scenario_pool(rules)
    base_by_key = {loadout_identity(ld): ld for ld in base_pool}
    scen_by_key = {loadout_identity(ld): ld for ld in scen_pool}
    common_keys = [k for k in base_by_key if k in scen_by_key]
    common_names = [base_by_key[k].name for k in common_keys]

    name_to_key = {base_by_key[k].name: k for k in common_keys}
    mode = st.radio(
        "Run mode",
        ["Single matchup", "Sampled tournament", "Forced tactic sweep", "Horde survival"],
        horizontal=True,
        key="sandbox_run_mode",
    )
    n_runs = st.number_input("Runs per matchup", min_value=1, max_value=1000, value=50, step=10)
    seed = st.number_input("Seed", min_value=1, value=2026, step=1)
    status_box = st.empty()

    if mode == "Single matchup":
        a_name = st.selectbox("A loadout", common_names, index=0)
        b_name = st.selectbox("B loadout", common_names, index=min(1, len(common_names) - 1))
        if st.button("Run matchup"):
            key_a = name_to_key[a_name]
            key_b = name_to_key[b_name]
            status_box.info(f"Running paired matchup: {int(n_runs):,} baseline battles + {int(n_runs):,} scenario battles.")
            with st.spinner("Running matchup..."):
                df = paired_matchup(
                    base_by_key[key_a], base_by_key[key_b],
                    scen_by_key[key_a], scen_by_key[key_b],
                    rules, int(n_runs), int(seed),
                )
            st.session_state.last_result = df
            st.session_state.last_result_kind = "single"
            st.session_state.last_horde_details = None
            status_box.success("Matchup complete.")
            st.dataframe(df, use_container_width=True)
    elif mode == "Sampled tournament":
        base_df = pool_to_frame([base_by_key[k] for k in common_keys])
        retinues = st.multiselect("Retinues", sorted(base_df["retinue"].unique()), default=sorted(base_df["retinue"].unique()))
        min_mpc, max_mpc = int(base_df["mpc"].min()), int(base_df["mpc"].max())
        mpc_range = st.slider("MPC range", min_mpc, max_mpc, (min_mpc, max_mpc))
        sample_size = st.number_input("Sample size", min_value=2, max_value=min(80, len(common_keys)), value=min(12, len(common_keys)), step=1)
        if st.button("Run sample"):
            eligible = [
                k for k in common_keys
                if base_by_key[k].retinue in retinues
                and mpc_range[0] <= getattr(base_by_key[k], "military_pursuit_count", 0) <= mpc_range[1]
            ]
            if not eligible:
                status_box.warning("No eligible loadouts match the selected filters.")
                return
            rng = random.Random(int(seed))
            sample_keys = rng.sample(eligible, min(int(sample_size), len(eligible)))
            sample_n = len(sample_keys)
            matchups = sample_n * sample_n
            status_box.info(
                f"Running sampled tournament: {sample_n} loadouts, "
                f"{matchups:,} paired matchups, {matchups * int(n_runs) * 2:,} total battles."
            )
            progress = st.progress(0.0, text="Preparing sampled tournament...")
            with st.spinner("Running sampled tournament..."):
                progress.progress(0.1, text="Simulating baseline and scenario matchups...")
                result = paired_sample_tournament(
                    [base_by_key[k] for k in sample_keys],
                    [scen_by_key[k] for k in sample_keys],
                    rules,
                    int(n_runs),
                    int(seed),
                )
                progress.progress(0.9, text="Preparing result table...")
            st.session_state.last_result = result
            st.session_state.last_result_kind = "sampled_tournament"
            st.session_state.last_horde_details = None
            progress.progress(1.0, text="Sample complete.")
            status_box.success(f"Sample complete: {len(result)} loadouts summarized.")
            st.dataframe(result, use_container_width=True)
    elif mode == "Forced tactic sweep":
        st.caption("Runs every opening tactic pair for one matchup. The heatmap visual is shown on the Results tab.")
        a_name = st.selectbox("A loadout", common_names, index=0, key="tactic_a_loadout")
        b_name = st.selectbox("B loadout", common_names, index=min(1, len(common_names) - 1), key="tactic_b_loadout")
        if st.button("Run forced tactic sweep"):
            key_a = name_to_key[a_name]
            key_b = name_to_key[b_name]
            total_cells = len(rules.tactics) * len(rules.tactics)
            status_box.info(
                f"Running forced tactic sweep: {total_cells} tactic cells, "
                f"{total_cells * int(n_runs) * 2:,} total battles."
            )
            progress = st.progress(0.0, text="Preparing forced tactic sweep...")
            with st.spinner("Running forced tactic sweep..."):
                progress.progress(0.1, text="Simulating forced tactic cells...")
                result = paired_tactic_heatmap(
                    base_by_key[key_a], base_by_key[key_b],
                    scen_by_key[key_a], scen_by_key[key_b],
                    rules,
                    int(n_runs),
                    int(seed),
                )
                progress.progress(0.9, text="Preparing heatmap rows...")
            st.session_state.last_result = result
            st.session_state.last_result_kind = "tactic_heatmap"
            st.session_state.last_horde_details = None
            progress.progress(1.0, text="Forced tactic sweep complete.")
            status_box.success("Forced tactic sweep complete. Open Results to view the heatmaps.")
            st.dataframe(result, use_container_width=True)
    else:
        army_name = st.selectbox("Army", common_names, index=0, key="horde_army")
        default_opponents = common_names[: min(5, len(common_names))]
        opponent_names = st.multiselect("Opponent cycle", common_names, default=default_opponents)
        max_waves = st.number_input("Max waves", min_value=1, max_value=30, value=8, step=1)
        recovery = st.checkbox("Recover endurance between waves", value=True)
        if st.button("Run horde survival"):
            if not opponent_names:
                st.warning("Select at least one opponent.")
                return
            army_key = name_to_key[army_name]
            opponent_keys = [name_to_key[name] for name in opponent_names]
            status_box.info(
                f"Running horde survival: {int(max_waves)} waves, "
                f"{int(n_runs) * int(max_waves) * 2:,} total wave-battles."
            )
            progress = st.progress(0.0, text="Preparing horde survival...")
            with st.spinner("Running horde survival..."):
                progress.progress(0.1, text="Simulating baseline and scenario horde runs...")
                summary, details = paired_horde(
                    base_by_key[army_key],
                    scen_by_key[army_key],
                    [base_by_key[key] for key in opponent_keys],
                    [scen_by_key[key] for key in opponent_keys],
                    rules,
                    int(n_runs),
                    int(max_waves),
                    int(seed),
                    bool(recovery),
                )
                progress.progress(0.9, text="Preparing horde summary...")
            st.session_state.last_result = summary
            st.session_state.last_result_kind = "horde"
            st.session_state.last_horde_details = details
            progress.progress(1.0, text="Horde survival complete.")
            status_box.success("Horde survival complete.")
            st.dataframe(summary, use_container_width=True)


def full_runs_tab(rules):
    st.subheader("Start Full Run")
    config_cols = st.columns(4)
    with config_cols[0]:
        run_type = st.selectbox(
            "Run type",
            list(FULL_RUN_TYPES),
            index=list(FULL_RUN_TYPES).index("all_compute"),
            format_func=lambda value: FULL_RUN_TYPES[value],
            key="full_run_type",
        )
        n_workers = st.number_input(
            "Workers",
            min_value=1,
            max_value=max(1, os.cpu_count() or 1),
            value=min(28, max(1, os.cpu_count() or 28)),
            step=1,
            key="full_run_workers",
        )
        seed = st.number_input("Seed", min_value=1, value=2026, step=1, key="full_run_seed")
    with config_cols[1]:
        n_runs_main = st.number_input("Main runs/matchup", min_value=1, value=100, step=10, key="full_run_n_runs_main")
        n_runs_playstyle = st.number_input(
            "Playstyle runs/matchup",
            min_value=1,
            value=100,
            step=10,
            key="full_run_n_runs_playstyle",
        )
    with config_cols[2]:
        n_runs_forced = st.number_input(
            "Forced tactic runs/cell",
            min_value=1,
            value=100,
            step=10,
            key="full_run_n_runs_forced",
        )
        forced_sample_size = st.number_input(
            "Forced sample size",
            min_value=1,
            value=60,
            step=5,
            key="full_run_forced_sample_size",
        )
    with config_cols[3]:
        n_runs_horde = st.number_input(
            "Horde runs/loadout",
            min_value=1,
            value=50,
            step=10,
            key="full_run_n_runs_horde",
        )
        horde_sample_size = st.number_input(
            "Horde sample size",
            min_value=1,
            value=60,
            step=5,
            key="full_run_horde_sample_size",
        )
        horde_waves = st.number_input("Horde waves", min_value=1, value=8, step=1, key="full_run_horde_waves")

    if st.button("Start full run", type="primary", key="full_run_start"):
        try:
            run_dir, config_path = create_full_run_config(
                rules,
                run_type,
                int(n_workers),
                int(seed),
                int(n_runs_main),
                int(n_runs_playstyle),
                int(n_runs_forced),
                int(n_runs_horde),
                int(forced_sample_size),
                int(horde_sample_size),
                int(horde_waves),
            )
            pid = launch_full_run(config_path, run_dir)
        except Exception as exc:
            st.error(str(exc))
        else:
            st.success(f"Started {run_dir.name} as PID {pid}.")
            st.rerun()

    st.divider()
    st.subheader("Run Monitor")
    run_dirs = full_run_dirs()
    if not run_dirs:
        st.info("No full-run jobs yet.")
        return

    selected = st.selectbox("Run", run_dirs, format_func=format_run_label, key="full_run_selected_run")
    progress = read_json(selected / "progress.json") or {}
    config = read_json(selected / "config.json") or {}
    status = progress.get("status", "unknown")
    completed = int(progress.get("completed") or 0)
    total = int(progress.get("total") or 0)
    ratio = completed / total if total else 0.0

    metric_cols = st.columns(5)
    metric_cols[0].metric("Status", status)
    metric_cols[1].metric("Phase", progress.get("phase", ""))
    metric_cols[2].metric("Progress", f"{completed}/{total}")
    metric_cols[3].metric("Battles/sec", progress.get("battles_per_sec", 0))
    metric_cols[4].metric("ETA sec", progress.get("eta_sec", 0))
    st.progress(min(1.0, max(0.0, ratio)), text=progress.get("current_label", ""))

    button_cols = st.columns(4)
    with button_cols[0]:
        if st.button("Refresh", key="full_run_refresh"):
            st.rerun()
    with button_cols[1]:
        if status not in TERMINAL_JOB_STATUSES and st.button("Cancel job", key="full_run_cancel"):
            request_full_run_cancel(selected)
            st.warning("Cancel requested. The worker will stop at the next progress checkpoint.")
    with button_cols[2]:
        if status not in TERMINAL_JOB_STATUSES and st.button("Force terminate", key="full_run_force_terminate"):
            if force_terminate_pid(progress.get("pid")):
                request_full_run_cancel(selected)
                progress["status"] = "cancelled"
                progress["phase"] = "cancelled"
                progress["last_update"] = datetime.now().isoformat(timespec="seconds")
                write_json(selected / "progress.json", progress)
                st.warning("Terminate signal sent.")
            else:
                st.error("Could not terminate that PID.")
    with button_cols[3]:
        auto_refresh = st.checkbox("Auto-refresh", value=False, key="full_run_auto_refresh")

    if progress.get("error"):
        st.error(progress["error"])

    with st.expander("Run config", expanded=False):
        st.json(config)
    with st.expander("Latest log", expanded=False):
        st.code(tail_text(selected / "run.log"), language="text")

    st.subheader("Load Completed Results")
    tables = available_parquet_tables(selected)
    if not tables:
        st.info("No parquet outputs are available yet.")
    else:
        table = st.selectbox("Parquet table", tables, format_func=lambda item: item["label"], key="full_run_parquet_table")
        if table["kind"] == "matchups_dataset":
            schema_cols = parquet_schema_columns(table["path"])
            default_cols = [c for c in ["a_name", "b_name", "a_wins", "b_wins", "indecisive", "a_retinue", "b_retinue"] if c in schema_cols]
            columns = st.multiselect("Columns", schema_cols, default=default_cols, key="full_run_matchup_columns")
            filter_cols = st.columns(3)
            with filter_cols[0]:
                a_filter = st.text_input("A name exact filter", key="full_run_matchup_a_filter")
            with filter_cols[1]:
                b_filter = st.text_input("B name exact filter", key="full_run_matchup_b_filter")
            with filter_cols[2]:
                limit = st.number_input(
                    "Row limit",
                    min_value=1,
                    max_value=100000,
                    value=5000,
                    step=1000,
                    key="full_run_matchup_row_limit",
                )
            load_label = "Load matchup sample"
        else:
            columns = []
            a_filter = b_filter = ""
            limit = 0
            load_label = "Load table into Results"

        if st.button(load_label, key="full_run_load_table"):
            try:
                if table["kind"] == "matchups_dataset":
                    result = read_matchup_dataset(table["path"], columns, a_filter, b_filter, limit)
                else:
                    result = pd.read_parquet(table["path"], engine="pyarrow")
            except Exception as exc:
                st.error(str(exc))
            else:
                st.session_state.last_result = result
                st.session_state.last_result_kind = table["kind"]
                st.session_state.last_horde_details = None
                st.success(f"Loaded {table['label']} ({len(result):,} rows). Open Results to chart or export.")

    if auto_refresh and status not in TERMINAL_JOB_STATUSES:
        time.sleep(2)
        st.rerun()


def get_pyplot():
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        st.warning("Install matplotlib to render notebook-style charts.")
        return None
    return plt


def plot_barh(series, title, xlabel, color="#4a90e2"):
    plt = get_pyplot()
    if plt is None or series.empty:
        return
    series = series.dropna()
    fig, ax = plt.subplots(figsize=(9, max(3, min(8, 0.35 * len(series)))))
    labels = [str(idx)[:70] for idx in series.index]
    ax.barh(labels, series.values, color=color, alpha=0.85)
    ax.axvline(0, color="black", linewidth=0.8, alpha=0.6)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid(alpha=0.25, axis="x")
    ax.invert_yaxis()
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def plot_winrate_scatter(df):
    plt = get_pyplot()
    if plt is None:
        return
    fig, ax = plt.subplots(figsize=(8, 7))
    for retinue, sub in df.groupby("retinue"):
        color = RETINUE_COLORS.get(retinue, "#555555")
        ax.scatter(
            sub["baseline_win_rate"],
            sub["scenario_win_rate"],
            s=34,
            alpha=0.65,
            label=retinue,
            color=color,
        )
    hi = max(0.55, df[["baseline_win_rate", "scenario_win_rate"]].max().max())
    lo = min(0.0, df[["baseline_win_rate", "scenario_win_rate"]].min().min())
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1, alpha=0.6)
    ax.axhline(0.5, color="gray", linestyle=":", linewidth=1)
    ax.axvline(0.5, color="gray", linestyle=":", linewidth=1)
    ax.set_xlabel("Baseline win rate")
    ax.set_ylabel("Scenario win rate")
    ax.set_title("Baseline vs scenario win rate")
    ax.legend()
    ax.grid(alpha=0.25)
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def pareto_frontier(df, x_col, y_col):
    frontier = []
    best = -1.0
    for _, row in df.sort_values(x_col).iterrows():
        if row[y_col] > best:
            best = row[y_col]
            frontier.append(row)
    return pd.DataFrame(frontier)


def plot_cost_frontier(df):
    plt = get_pyplot()
    if plt is None:
        return
    chart_df = df.copy()
    chart_df["baseline_army_upkeep"] = chart_df["baseline_upkeep"] * 50
    chart_df["scenario_army_upkeep"] = chart_df["scenario_upkeep"] * 50
    frontier = pareto_frontier(chart_df, "scenario_army_upkeep", "scenario_win_rate")

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(
        chart_df["baseline_army_upkeep"],
        chart_df["baseline_win_rate"],
        color="#999999",
        alpha=0.28,
        s=24,
        label="baseline",
    )
    for retinue, sub in chart_df.groupby("retinue"):
        ax.scatter(
            sub["scenario_army_upkeep"],
            sub["scenario_win_rate"],
            color=RETINUE_COLORS.get(retinue, "#555555"),
            alpha=0.6,
            s=30,
            label=f"scenario {retinue}",
        )
    if not frontier.empty:
        ax.plot(
            frontier["scenario_army_upkeep"],
            frontier["scenario_win_rate"],
            "k--",
            linewidth=1.4,
            alpha=0.7,
            label="scenario frontier",
        )
    ax.axhline(0.5, color="black", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("Army upkeep for 50 retinues")
    ax.set_ylabel("Win rate")
    ax.set_title("Cost-efficiency frontier")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    st.pyplot(fig, width="stretch")
    plt.close(fig)
    if not frontier.empty:
        st.dataframe(
            frontier[["name", "retinue", "weapon", "scenario_army_upkeep", "scenario_win_rate"]].tail(15),
            use_container_width=True,
            hide_index=True,
        )


def plot_full_cost_frontier(df):
    plt = get_pyplot()
    if plt is None or df.empty:
        return
    chart_df = df.copy()
    if "army_upkeep" not in chart_df:
        chart_df["army_upkeep"] = chart_df["upkeep_per_retinue"] * chart_df["size"]
    frontier = pareto_frontier(chart_df, "army_upkeep", "win_rate")
    fig, ax = plt.subplots(figsize=(10, 7))
    for retinue, sub in chart_df.groupby("retinue"):
        ax.scatter(
            sub["army_upkeep"],
            sub["win_rate"],
            color=RETINUE_COLORS.get(retinue, "#555555"),
            alpha=0.55,
            s=28,
            label=retinue,
        )
    if not frontier.empty:
        ax.plot(frontier["army_upkeep"], frontier["win_rate"], "k--", linewidth=1.4, alpha=0.7, label="frontier")
    ax.axhline(0.5, color="black", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("Army upkeep")
    ax.set_ylabel("Win rate")
    ax.set_title("Cost-efficiency frontier")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def render_full_summary_charts(df):
    if df.empty:
        st.info("No rows to chart.")
        return
    cols = st.columns(4)
    cols[0].metric("Loadouts", f"{len(df):,}")
    cols[1].metric("Mean win rate", f"{df['win_rate'].mean():.1%}")
    cols[2].metric("Best win rate", f"{df['win_rate'].max():.1%}")
    cols[3].metric("Mean decisive", f"{df['decisive_rate'].mean():.1%}" if "decisive_rate" in df else "n/a")

    st.subheader("Top Loadouts")
    st.dataframe(
        df.nlargest(min(25, len(df)), "win_rate")[
            ["name", "retinue", "weapon", "shield", "armor", "win_rate", "decisive_win_rate", "army_upkeep", "military_pursuit_count"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Retinue And Equipment")
    tabs = st.tabs(["Retinue", "Weapon", "Armor", "Shield", "MPC"])
    for tab, group_col in zip(tabs[:4], ["retinue", "weapon", "armor", "shield"]):
        with tab:
            grouped = (
                df.groupby(group_col)
                .agg(n=("name", "count"), win_rate=("win_rate", "mean"), decisive_win_rate=("decisive_win_rate", "mean"))
                .sort_values("win_rate", ascending=False)
            )
            st.dataframe(grouped, use_container_width=True)
            plot_barh(grouped["win_rate"].head(20), f"Mean win rate by {group_col}", "Win rate")
    with tabs[4]:
        mpc = df.groupby("military_pursuit_count")[["win_rate", "decisive_win_rate"]].mean()
        st.line_chart(mpc)

    st.subheader("Cost Efficiency")
    plot_full_cost_frontier(df)


def render_single_result_charts(result):
    base = result[result["run"].isin(["baseline", "scenario"])]
    if base.empty:
        return
    st.subheader("Outcome Breakdown")
    outcomes = base.set_index("run")[["a_wins", "b_wins", "mut_wipe", "indecisive"]].T
    st.bar_chart(outcomes)
    delta = result[result["run"] == "delta"]
    if not delta.empty:
        st.subheader("Metric Deltas")
        delta_cols = ["win_rate", "decisive_win_rate", "avg_skirm", "avg_a_rem", "avg_b_rem"]
        st.bar_chart(delta.set_index("run")[[c for c in delta_cols if c in delta.columns]].T)


def render_sampled_tournament_charts(df):
    cols = st.columns(4)
    cols[0].metric("Loadouts", len(df))
    cols[1].metric("Baseline WR", f"{df['baseline_win_rate'].mean():.1%}")
    cols[2].metric("Scenario WR", f"{df['scenario_win_rate'].mean():.1%}", f"{df['delta_win_rate'].mean():+.1%}")
    cols[3].metric("Improved", f"{(df['delta_win_rate'] > 0).mean():.0%}")

    st.subheader("Win-Rate Shift")
    plot_winrate_scatter(df)

    top_n = min(15, len(df))
    left, right = st.columns(2)
    with left:
        boosted = df.nlargest(top_n, "delta_win_rate").set_index("name")["delta_win_rate"]
        plot_barh(boosted, "Biggest buffs", "Delta win rate", "#2ca02c")
    with right:
        nerfed = df.nsmallest(top_n, "delta_win_rate").sort_values("delta_win_rate", ascending=True).set_index("name")["delta_win_rate"]
        plot_barh(nerfed, "Biggest nerfs", "Delta win rate", "#d62728")

    st.subheader("Group Deltas")
    group_tabs = st.tabs(["Retinue", "Weapon", "Armor", "Shield", "Ranged", "Playstyle"])
    for tab, group_col in zip(group_tabs, ["retinue", "weapon", "armor", "shield", "ranged", "playstyle"]):
        with tab:
            grouped = (
                df.groupby(group_col)
                .agg(
                    n=("name", "count"),
                    baseline_win_rate=("baseline_win_rate", "mean"),
                    scenario_win_rate=("scenario_win_rate", "mean"),
                    delta_win_rate=("delta_win_rate", "mean"),
                    delta_decisive_rate=("delta_decisive_rate", "mean"),
                )
                .sort_values("delta_win_rate", ascending=False)
            )
            st.dataframe(grouped, use_container_width=True)
            plot_barh(grouped["delta_win_rate"].head(20), f"Mean delta by {group_col}", "Delta win rate")

    st.subheader("MPC, Domain, And Cost")
    mpc = df.groupby("mpc")[["baseline_win_rate", "scenario_win_rate", "delta_win_rate"]].mean()
    domain = df.groupby("domain")[["baseline_win_rate", "scenario_win_rate", "delta_win_rate"]].mean()
    cols = st.columns(2)
    with cols[0]:
        st.line_chart(mpc[["baseline_win_rate", "scenario_win_rate"]])
        st.bar_chart(mpc["delta_win_rate"])
    with cols[1]:
        st.line_chart(domain[["baseline_win_rate", "scenario_win_rate"]])
        st.bar_chart(domain["delta_win_rate"])
    plot_cost_frontier(df)


def plot_tactic_heatmap(df, value_col, title, tactics, cmap="RdYlGn", symmetric=False):
    plt = get_pyplot()
    if plt is None:
        pivot = df.pivot(index="a_tactic", columns="b_tactic", values=value_col).reindex(index=tactics, columns=tactics)
        st.dataframe(pivot.round(3), use_container_width=True)
        return
    pivot = df.pivot(index="a_tactic", columns="b_tactic", values=value_col).reindex(index=tactics, columns=tactics)
    values = pivot.values
    if symmetric:
        max_abs = np.nanmax(np.abs(values)) if np.isfinite(values).any() else 0.1
        vmin, vmax = -max_abs, max_abs
    elif "win_rate" in value_col:
        vmin, vmax = 0.0, 1.0
    else:
        vmin, vmax = 0.0, np.nanmax(values) if np.isfinite(values).any() else 1.0
    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(values, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(tactics)))
    ax.set_xticklabels(tactics, rotation=45, ha="right")
    ax.set_yticks(range(len(tactics)))
    ax.set_yticklabels(tactics)
    ax.set_xlabel("B tactic")
    ax.set_ylabel("A tactic")
    ax.set_title(title)
    for i in range(len(tactics)):
        for j in range(len(tactics)):
            value = values[i, j]
            if not np.isnan(value):
                ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax)
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def render_tactic_heatmap_charts(df, tactics):
    st.subheader("Forced Tactic Sweep Heatmaps")
    tabs = st.tabs(["Scenario WR", "Baseline WR", "Delta WR", "Indecisive", "Marginal"])
    with tabs[0]:
        plot_tactic_heatmap(df, "scenario_win_rate", "Scenario forced tactic win rate", tactics)
    with tabs[1]:
        plot_tactic_heatmap(df, "baseline_win_rate", "Baseline forced tactic win rate", tactics)
    with tabs[2]:
        plot_tactic_heatmap(df, "delta_win_rate", "Scenario minus baseline win rate", tactics, cmap="RdYlGn", symmetric=True)
    with tabs[3]:
        plot_tactic_heatmap(df, "scenario_indecisive_rate", "Scenario indecisive rate", tactics, cmap="Reds")
    with tabs[4]:
        marginal = (
            df.groupby("a_tactic")
            .agg(
                baseline_win_rate=("baseline_win_rate", "mean"),
                scenario_win_rate=("scenario_win_rate", "mean"),
                delta_win_rate=("delta_win_rate", "mean"),
            )
            .reindex(tactics)
        )
        st.dataframe(marginal, use_container_width=True)
        st.bar_chart(marginal[["baseline_win_rate", "scenario_win_rate"]])
        st.bar_chart(marginal["delta_win_rate"])


def render_full_tactic_matrix_charts(df, tactics):
    if "a_win_rate" in df.columns:
        tabs = st.tabs(["A win rate", "Stalemate", "Marginal"])
        with tabs[0]:
            plot_tactic_heatmap(df, "a_win_rate", "A win rate by opening tactic", tactics)
        with tabs[1]:
            plot_tactic_heatmap(df, "stalemate_rate", "Stalemate rate by opening tactic", tactics, cmap="Reds")
        with tabs[2]:
            marginal = (
                df.groupby("a_tactic")
                .agg(avg_win_rate=("a_win_rate", "mean"), stalemate_rate=("stalemate_rate", "mean"))
                .reindex(tactics)
            )
            st.dataframe(marginal, use_container_width=True)
            st.bar_chart(marginal)
    else:
        tabs = st.tabs(["Forced win rate", "Indecisive", "Marginal"])
        with tabs[0]:
            plot_tactic_heatmap(df, "win_rate", "Forced tactic win rate", tactics)
        with tabs[1]:
            plot_tactic_heatmap(df, "indecisive_rate", "Forced tactic indecisive rate", tactics, cmap="Reds")
        with tabs[2]:
            marginal = (
                df.groupby("a_tactic")
                .agg(avg_win_rate=("win_rate", "mean"), indecisive_rate=("indecisive_rate", "mean"))
                .reindex(tactics)
            )
            st.dataframe(marginal, use_container_width=True)
            st.bar_chart(marginal)


def horde_wave_frame(details):
    rows = []
    for label, result in details.items():
        cumulative_spoils = 0.0
        for wave_result in result["wave_results"]:
            cumulative_spoils += wave_result.avg_spoils * wave_result.survival_rate
            rows.append({
                "run": label,
                "wave": wave_result.wave,
                "survival_rate": wave_result.survival_rate,
                "avg_size": wave_result.avg_size,
                "avg_endurance": wave_result.avg_endurance,
                "avg_spoils": wave_result.avg_spoils,
                "cumulative_spoils_proxy": cumulative_spoils,
            })
    return pd.DataFrame(rows)


def horde_survival_frame(details):
    rows = []
    for label, result in details.items():
        for wave, survival_rate in enumerate(result["survival_curve"]):
            rows.append({"run": label, "wave": wave, "survival_rate": survival_rate})
    return pd.DataFrame(rows)


def horde_cause_frame(details):
    cause_labels = {0: "alive", 1: "combat", 2: "shake", 3: "flee"}
    rows = []
    for label, result in details.items():
        max_waves = result["max_waves"]
        wipe_wave = result["wave_of_wipe"]
        causes = result["cause_of_wipe"].copy()
        causes[wipe_wave > max_waves] = 0
        counts = pd.Series(causes).map(cause_labels).value_counts(normalize=True)
        for cause in ["alive", "combat", "shake", "flee"]:
            rows.append({"run": label, "cause": cause, "rate": counts.get(cause, 0.0)})
    return pd.DataFrame(rows)


def horde_break_even_frame(details):
    rows = []
    for label, result in details.items():
        max_waves = result["max_waves"]
        clipped = np.minimum(result["break_even_wave"], max_waves + 1)
        counts = pd.Series(clipped).value_counts(normalize=True).sort_index()
        for wave, rate in counts.items():
            rows.append({
                "run": label,
                "wave": "never" if wave == max_waves + 1 else str(int(wave)),
                "rate": rate,
            })
    return pd.DataFrame(rows)


def render_horde_charts(summary, details):
    cols = st.columns(4)
    scenario = summary[summary["army"] == "scenario"]
    baseline = summary[summary["army"] == "baseline"]
    if not scenario.empty and not baseline.empty:
        s = scenario.iloc[0]
        b = baseline.iloc[0]
        cols[0].metric("Survive all", f"{s['p_survive_all']:.0%}", f"{s['p_survive_all'] - b['p_survive_all']:+.0%}")
        cols[1].metric("Mean waves", f"{s['mean_waves']:.2f}", f"{s['mean_waves'] - b['mean_waves']:+.2f}")
        cols[2].metric("Net profit", f"{s['mean_net_profit']:.0f}", f"{s['mean_net_profit'] - b['mean_net_profit']:+.0f}")
        cols[3].metric("Break-even", f"{s['p_breaks_even']:.0%}", f"{s['p_breaks_even'] - b['p_breaks_even']:+.0%}")

    survival = horde_survival_frame(details)
    waves = horde_wave_frame(details)
    causes = horde_cause_frame(details)
    break_even = horde_break_even_frame(details)

    st.subheader("Survival Curves")
    st.line_chart(survival.pivot(index="wave", columns="run", values="survival_rate"))

    st.subheader("Wave State")
    wave_tabs = st.tabs(["Average Size", "Average Endurance", "Spoils Proxy"])
    with wave_tabs[0]:
        st.line_chart(waves.pivot(index="wave", columns="run", values="avg_size"))
    with wave_tabs[1]:
        st.line_chart(waves.pivot(index="wave", columns="run", values="avg_endurance"))
    with wave_tabs[2]:
        st.line_chart(waves.pivot(index="wave", columns="run", values="cumulative_spoils_proxy"))

    st.subheader("Cause Of Wipe")
    st.bar_chart(causes.pivot(index="cause", columns="run", values="rate"))

    st.subheader("Break-Even Distribution")
    st.bar_chart(break_even.pivot(index="wave", columns="run", values="rate").fillna(0))


def render_horde_summary_charts(df):
    if df.empty:
        st.info("No horde rows to chart.")
        return
    cols = st.columns(4)
    cols[0].metric("Loadouts", f"{len(df):,}")
    cols[1].metric("Mean survive all", f"{df['p_survive_all'].mean():.0%}")
    cols[2].metric("Mean waves", f"{df['mean_waves'].mean():.2f}")
    cols[3].metric("Mean net profit", f"{df['mean_net_profit'].mean():.0f}")

    st.subheader("Top Horde Survivors")
    st.dataframe(
        df.nlargest(min(25, len(df)), "p_survive_all")[
            ["name", "retinue", "weapon", "shield", "armor", "mpc", "p_survive_all", "mean_waves", "mean_net_profit"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    tabs = st.tabs(["Retinue", "MPC", "Survival vs Profit"])
    with tabs[0]:
        grouped = df.groupby("retinue").agg(
            n=("name", "count"),
            p_survive_all=("p_survive_all", "mean"),
            mean_waves=("mean_waves", "mean"),
            mean_net_profit=("mean_net_profit", "mean"),
        ).sort_values("p_survive_all", ascending=False)
        st.dataframe(grouped, use_container_width=True)
        plot_barh(grouped["p_survive_all"], "Mean survival by retinue", "P(survive all)")
    with tabs[1]:
        mpc = df.groupby("mpc")[["p_survive_all", "mean_waves", "mean_net_profit"]].mean()
        st.line_chart(mpc)
    with tabs[2]:
        plt = get_pyplot()
        if plt is not None:
            fig, ax = plt.subplots(figsize=(9, 6))
            for retinue, sub in df.groupby("retinue"):
                ax.scatter(
                    sub["mean_net_profit"],
                    sub["p_survive_all"],
                    color=RETINUE_COLORS.get(retinue, "#555555"),
                    alpha=0.65,
                    s=32,
                    label=retinue,
                )
            ax.set_xlabel("Mean net profit")
            ax.set_ylabel("P(survive all)")
            ax.set_title("Horde economy vs survival")
            ax.grid(alpha=0.25)
            ax.legend(fontsize=8)
            st.pyplot(fig, width="stretch")
            plt.close(fig)


def infer_result_kind(result):
    if "a_tactic" in result.columns and "b_tactic" in result.columns:
        if "baseline_win_rate" not in result.columns:
            return "full_tactic_matrix"
        return "tactic_heatmap"
    if "army" in result.columns and "p_survive_all" in result.columns:
        return "horde"
    if "p_survive_all" in result.columns and "mean_waves" in result.columns:
        return "horde_summary"
    if "delta_win_rate" in result.columns and "name" in result.columns:
        return "sampled_tournament"
    if "win_rate" in result.columns and "military_pursuit_count" in result.columns:
        return "full_summary"
    if {"a_name", "b_name", "a_wins", "b_wins"} <= set(result.columns):
        return "matchups_dataset"
    if "run" in result.columns:
        return "single"
    return "unknown"


def results_tab(rules):
    result = st.session_state.get("last_result")
    if result is None:
        st.info("No sandbox result yet.")
        return
    kind = st.session_state.get("last_result_kind") or infer_result_kind(result)

    chart_tab, data_tab = st.tabs(["Charts", "Data & Export"])
    with chart_tab:
        if kind == "single":
            render_single_result_charts(result)
        elif kind == "sampled_tournament":
            render_sampled_tournament_charts(result)
        elif kind == "tactic_heatmap":
            render_tactic_heatmap_charts(result, rules.tactics)
        elif kind == "horde":
            details = st.session_state.get("last_horde_details")
            if details:
                render_horde_charts(result, details)
            else:
                st.info("Horde detail arrays are not available for this result.")
        elif kind == "full_summary":
            render_full_summary_charts(result)
        elif kind in ("full_tactic_matrix", "forced_tactics"):
            render_full_tactic_matrix_charts(result, rules.tactics)
        elif kind == "horde_summary":
            render_horde_summary_charts(result)
        elif kind == "matchups_dataset":
            st.info("Loaded matchup detail sample. Use the data tab for inspection and CSV export.")
            numeric = result.select_dtypes(include=[np.number])
            if not numeric.empty:
                st.dataframe(numeric.describe().T, use_container_width=True)
        else:
            numeric = result.select_dtypes(include=[np.number])
            if not numeric.empty:
                st.bar_chart(numeric)

    with data_tab:
        st.dataframe(result, use_container_width=True)

        csv = result.to_csv(index=False).encode("utf-8")
        st.download_button("Download result CSV", csv, "dashboard_result.csv", "text/csv")
        if st.button("Save result CSV"):
            RUN_DIR.mkdir(parents=True, exist_ok=True)
            path = RUN_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            result.to_csv(path, index=False)
            rules.to_json(path.with_suffix(".scenario.json"))
            st.success(f"Saved {path}")


def main():
    if st is None:
        raise RuntimeError("Streamlit is not installed. Run: python -m pip install -r requirements-dashboard.txt")

    st.set_page_config(page_title="Renown Rules Sandbox", layout="wide")
    SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if "rules" not in st.session_state:
        st.session_state.rules = default_rules()

    rules = st.session_state.rules
    st.title("Renown Rules Sandbox")
    tabs = st.tabs(["Rules Explorer", "Scenario Editor", "Loadout Preview", "Sandbox Runs", "Full Runs", "Results"])
    with tabs[0]:
        rules_explorer_tab()
    with tabs[1]:
        scenario_editor_tab(rules)
    with tabs[2]:
        loadout_preview_tab(rules)
    with tabs[3]:
        sandbox_tab(rules)
    with tabs[4]:
        full_runs_tab(rules)
    with tabs[5]:
        results_tab(rules)


if __name__ == "__main__":
    main()
