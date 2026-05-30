import pytest

import tournament_vec  # noqa: F401 - installs normalized matrix used by tournament runs
import loadouts
from rules_config import RulesConfig, default_rules
from vectorized_combat import run_matchup_vec


def _levy():
    return loadouts.Loadout(
        name="Lev/FarmTools/Cloth",
        retinue="Levy",
        weapon="Farm Tools",
        shield=None,
        armor="Cloth",
        ranged=None,
        has_tiltyard=False,
        size=20,
        extra_tags=[],
        upkeep_per_retinue=20,
        playstyle=None,
        tiltyard_mastery=True,
        pursuits=frozenset(),
        military_pursuit_count=0,
        domain_count=0,
    )


def test_default_rules_match_rules_none_fixed_seed():
    rules = default_rules()
    a = _levy()
    b = _levy()
    baseline = run_matchup_vec(a, b, n_runs=20, seed=1234)
    explicit = run_matchup_vec(a, b, n_runs=20, seed=1234, rules=rules)
    keys = ["a_wins", "b_wins", "mut_wipe", "indecisive", "avg_a_rem", "avg_b_rem", "avg_skirm"]
    assert {k: baseline[k] for k in keys} == {k: explicit[k] for k in keys}


def test_scenario_roundtrip_and_validation(tmp_path):
    rules = default_rules()
    rules.name = "Cost tweak"
    rules.retinues["Levy"]["cost"] = 25
    path = tmp_path / "scenario.json"

    rules.to_json(path)
    loaded = RulesConfig.from_json(path)

    assert loaded.name == "Cost tweak"
    assert loaded.retinues["Levy"]["cost"] == 25

    data = loaded.to_dict()
    data["weapons"]["New Weapon"] = {"ap": 0, "init": 0, "tags": [], "tier": "Crude"}
    with pytest.raises(ValueError):
        RulesConfig.from_dict(data)


def test_rules_recalculate_loadout_upkeep():
    rules = default_rules()
    rules.retinues["Levy"]["cost"] = 25
    ld = _levy()

    assert loadouts.compute_effective_upkeep(ld) == 20
    assert loadouts.compute_effective_upkeep(ld, rules=rules) == 25


def test_validation_rejects_unknown_tags():
    rules = default_rules()
    rules.weapons["Farm Tools"]["tags"] = ["Typo Tag"]

    with pytest.raises(ValueError, match="unknown tags"):
        rules.validate()


def test_validation_rejects_unknown_pursuit_references():
    rules = default_rules()
    rules.pursuits_info["Levy Hall"]["prereqs"] = ["Missing Pursuit"]

    with pytest.raises(ValueError, match="unknown pursuits"):
        rules.validate()


def test_validation_rejects_unknown_upkeep_armor_references():
    rules = default_rules()
    rules.pursuits_info["Levy Hall"]["upkeep_effects"] = [
        {"if_armor_in": [["Imaginary Armor"], 5]}
    ]

    with pytest.raises(ValueError, match="unknown armor"):
        rules.validate()
