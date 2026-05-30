"""
Runtime rules configuration for balance experiments.

RulesConfig is intentionally an overlay-friendly deep copy of the current module
defaults. Existing simulator calls continue to use module globals when
``rules=None``; dashboard and scenario runs can pass an explicit RulesConfig.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field, fields
import json
from pathlib import Path
from typing import Any


SCENARIO_VERSION = 1
NONE_KEY = "__none__"
TACTIC_KEY_SEP = "||"
TIER_VALUES = ("Crude", "Cast", "Wrought", "Forged", "Crafted")
DOMAIN_KEYS = ("Industry", "Prowess", "Piety", "Cunning")
ENGINE_TAGS = {
    "2H",
    "+1TH",
    "-1TBH",
    "Apothecary Heal",
    "Cleave",
    "Cond Field",
    "Destroy Shield",
    "Drilled",
    "GF Armor",
    "Immune Destroy Shield",
    "Immune Nimble",
    "Immune Poison",
    "Immune Steady",
    "Immune Strain",
    "Immune Unwieldy",
    "Ministry: every",
    "Ministry: first",
    "Ministry: once",
    "MW Weapons",
    "Nimble",
    "Parry",
    "Poison",
    "Regenerate",
    "Regenerate 4",
    "Regenerate 5",
    "Regenerate 6",
    "Regenerate Reroll",
    "Rend",
    "Seize: every",
    "Seize: first",
    "Shatter Armor",
    "Steadfast",
    "Steady",
    "Unshakable",
    "Unstoppable",
    "Unwieldy",
    "Yew Heart",
}


@dataclass
class MechanicsConfig:
    initiative_min: int = -2
    initiative_max: int = 2
    front_line_cap: int = 20
    reserve_cap: int = 10
    field_cap: int = 25
    max_skirmishes: int = 20
    rout_threshold: int = 7
    parry_threshold: int = 5
    regen_rend_delta: int = 1
    regen_rend_cap: int = 7
    ministry_counter_weight: float = 0.8
    fatigue_fallback_weight_fat1: float = 0.15
    fatigue_fallback_weight_fat2plus: float = 0.40
    apothecary_heal_casualties_per_retinue: int = 4


@dataclass
class RulesConfig:
    version: int = SCENARIO_VERSION
    name: str = "Untitled scenario"
    description: str = ""
    retinues: dict[str, dict[str, Any]] = field(default_factory=dict)
    weapons: dict[str, dict[str, Any]] = field(default_factory=dict)
    ranged: dict[str, dict[str, Any]] = field(default_factory=dict)
    shields: dict[Any, dict[str, Any]] = field(default_factory=dict)
    armors: dict[str, dict[str, Any]] = field(default_factory=dict)
    tactics: list[str] = field(default_factory=list)
    tactic_matrix: dict[tuple[str, str], tuple[dict[str, Any], dict[str, Any]]] = field(default_factory=dict)
    pursuits_info: dict[str, dict[str, Any]] = field(default_factory=dict)
    build_kits: dict[str, list[str]] = field(default_factory=dict)
    tier_industry_req: dict[str, int] = field(default_factory=dict)
    armor_requires: dict[str, set[str]] = field(default_factory=dict)
    shield_metal_requires: dict[str, set[str]] = field(default_factory=dict)
    static_playstyles: dict[str, dict[str, Any]] = field(default_factory=dict)
    adaptive_playstyles: dict[str, dict[str, Any]] = field(default_factory=dict)
    mechanics: MechanicsConfig = field(default_factory=MechanicsConfig)

    def validate(self) -> None:
        """Validate v1 constraints: scenarios may edit existing objects, not add/remove them."""
        defaults = default_rules()
        checks = [
            ("retinues", self.retinues, defaults.retinues),
            ("weapons", self.weapons, defaults.weapons),
            ("ranged", self.ranged, defaults.ranged),
            ("shields", self.shields, defaults.shields),
            ("armors", self.armors, defaults.armors),
            ("pursuits_info", self.pursuits_info, defaults.pursuits_info),
            ("build_kits", self.build_kits, defaults.build_kits),
            ("static_playstyles", self.static_playstyles, defaults.static_playstyles),
            ("adaptive_playstyles", self.adaptive_playstyles, defaults.adaptive_playstyles),
        ]
        for label, current, default in checks:
            _assert_same_keys(label, current.keys(), default.keys())
        if list(self.tactics) != list(defaults.tactics):
            raise ValueError("v1 scenarios may edit tactic values but may not add/remove/reorder tactics")
        _assert_same_keys("tactic_matrix", self.tactic_matrix.keys(), defaults.tactic_matrix.keys())
        _validate_references(self, defaults)

        if self.mechanics.initiative_min > self.mechanics.initiative_max:
            raise ValueError("initiative_min must be <= initiative_max")
        if self.mechanics.front_line_cap < 1:
            raise ValueError("front_line_cap must be >= 1")
        if self.mechanics.reserve_cap < 0:
            raise ValueError("reserve_cap must be >= 0")
        if self.mechanics.field_cap < 1:
            raise ValueError("field_cap must be >= 1")
        if self.mechanics.max_skirmishes < 1:
            raise ValueError("max_skirmishes must be >= 1")
        if self.mechanics.apothecary_heal_casualties_per_retinue < 1:
            raise ValueError("apothecary_heal_casualties_per_retinue must be >= 1")
        if not 0 <= self.mechanics.ministry_counter_weight <= 1:
            raise ValueError("ministry_counter_weight must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "retinues": _json_clean(self.retinues),
            "weapons": _json_clean(self.weapons),
            "ranged": _json_clean(self.ranged),
            "shields": _json_clean(_encode_none_keys(self.shields)),
            "armors": _json_clean(self.armors),
            "tactics": list(self.tactics),
            "tactic_matrix": _encode_tactic_matrix(self.tactic_matrix),
            "pursuits_info": _json_clean(self.pursuits_info),
            "build_kits": _json_clean(self.build_kits),
            "tier_industry_req": _json_clean(self.tier_industry_req),
            "armor_requires": _json_clean(self.armor_requires),
            "shield_metal_requires": _json_clean(self.shield_metal_requires),
            "static_playstyles": _json_clean(self.static_playstyles),
            "adaptive_playstyles": _json_clean(self.adaptive_playstyles),
            "mechanics": asdict(self.mechanics),
        }

    def to_json(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def from_json(cls, path: str | Path) -> "RulesConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RulesConfig":
        base = default_rules()
        if data.get("version", SCENARIO_VERSION) != SCENARIO_VERSION:
            raise ValueError(f"Unsupported scenario version: {data.get('version')}")

        base.name = data.get("name", base.name)
        base.description = data.get("description", base.description)
        _replace_table(base, "retinues", data)
        _replace_table(base, "weapons", data)
        _replace_table(base, "ranged", data)
        if "shields" in data:
            base.shields = _decode_none_keys(data["shields"])
        _replace_table(base, "armors", data)
        if "tactics" in data:
            base.tactics = list(data["tactics"])
        if "tactic_matrix" in data:
            base.tactic_matrix = _decode_tactic_matrix(data["tactic_matrix"])
        _replace_table(base, "pursuits_info", data)
        _replace_table(base, "build_kits", data)
        _replace_table(base, "tier_industry_req", data)
        if "armor_requires" in data:
            base.armor_requires = {k: set(v) for k, v in data["armor_requires"].items()}
        if "shield_metal_requires" in data:
            base.shield_metal_requires = {k: set(v) for k, v in data["shield_metal_requires"].items()}
        if "static_playstyles" in data:
            base.static_playstyles = _merge_playstyles(base.static_playstyles, data["static_playstyles"])
        if "adaptive_playstyles" in data:
            base.adaptive_playstyles = _merge_playstyles(base.adaptive_playstyles, data["adaptive_playstyles"])
        if "mechanics" in data:
            base.mechanics = _mechanics_from_dict(data["mechanics"])

        base.validate()
        return base


def default_rules() -> RulesConfig:
    import loadouts
    import playstyles
    import renown_combat

    adaptive = deepcopy(playstyles.ADAPTIVE_PLAYSTYLES)
    return RulesConfig(
        name="Default rules",
        retinues=deepcopy(renown_combat.RETINUES),
        weapons=deepcopy(renown_combat.WEAPONS),
        ranged=deepcopy(renown_combat.RANGED),
        shields=deepcopy(renown_combat.SHIELDS),
        armors=deepcopy(renown_combat.ARMORS),
        tactics=list(renown_combat.TACTICS),
        tactic_matrix=deepcopy(renown_combat.TACTIC_MATRIX),
        pursuits_info=deepcopy(loadouts.PURSUITS_INFO),
        build_kits={k: list(v) for k, v in deepcopy(loadouts.BUILD_KITS).items()},
        tier_industry_req=deepcopy(loadouts.TIER_INDUSTRY_REQ),
        armor_requires={k: set(v) for k, v in loadouts.ARMOR_REQUIRES.items()},
        shield_metal_requires={k: set(v) for k, v in loadouts.SHIELD_METAL_REQUIRES.items()},
        static_playstyles=deepcopy(playstyles.STATIC_PLAYSTYLES),
        adaptive_playstyles=adaptive,
        mechanics=MechanicsConfig(),
    )


def _assert_same_keys(label: str, current_keys, default_keys) -> None:
    current = set(current_keys)
    default = set(default_keys)
    added = sorted(str(k) for k in current - default)
    removed = sorted(str(k) for k in default - current)
    if added or removed:
        raise ValueError(f"{label} cannot add/remove keys in v1. added={added}, removed={removed}")


def _replace_table(base: RulesConfig, name: str, data: dict[str, Any]) -> None:
    if name in data:
        setattr(base, name, deepcopy(data[name]))


def _mechanics_from_dict(data: dict[str, Any]) -> MechanicsConfig:
    allowed = {f.name for f in fields(MechanicsConfig)}
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"Unknown mechanics keys: {sorted(unknown)}")
    values = asdict(MechanicsConfig())
    values.update(data)
    return MechanicsConfig(**values)


def _merge_playstyles(defaults: dict[str, dict[str, Any]], incoming: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    _assert_same_keys("playstyles", incoming.keys(), defaults.keys())
    merged = deepcopy(defaults)
    for name, values in incoming.items():
        runtime_func = merged[name].get("func")
        merged[name].update(deepcopy(values))
        if runtime_func is not None:
            merged[name]["func"] = runtime_func
    return merged


def known_tags(rules: RulesConfig | None = None) -> list[str]:
    source = rules if rules is not None else default_rules()
    tags = set(ENGINE_TAGS)
    for table in (source.weapons, source.ranged, source.shields, source.armors, source.pursuits_info):
        for profile in table.values():
            tags.update(profile.get("tags", []))
    for values in source.build_kits.values():
        tags.update(values)
    return sorted(tags)


def _validate_references(rules: RulesConfig, defaults: RulesConfig) -> None:
    valid_tags = set(known_tags(defaults))
    valid_pursuits = set(defaults.pursuits_info)
    valid_armors = set(defaults.armors)
    valid_tactics = set(range(len(defaults.tactics)))
    valid_domains = set(DOMAIN_KEYS)

    for label, table in [
        ("weapons", rules.weapons),
        ("ranged", rules.ranged),
        ("shields", rules.shields),
        ("armors", rules.armors),
    ]:
        for name, profile in table.items():
            tier = profile.get("tier")
            if tier is not None and tier not in TIER_VALUES:
                raise ValueError(f"{label}.{name}.tier must be one of {TIER_VALUES}")
            _assert_known_tags(f"{label}.{name}.tags", profile.get("tags", []), valid_tags)

    for name, profile in rules.pursuits_info.items():
        bad_prereqs = set(profile.get("prereqs", [])) - valid_pursuits
        if bad_prereqs:
            raise ValueError(f"pursuits_info.{name}.prereqs has unknown pursuits: {sorted(bad_prereqs)}")
        bad_domains = set(profile.get("domain", {})) - valid_domains
        if bad_domains:
            raise ValueError(f"pursuits_info.{name}.domain has unknown domains: {sorted(bad_domains)}")
        _assert_known_tags(f"pursuits_info.{name}.tags", profile.get("tags", []), valid_tags)
        for effect in profile.get("upkeep_effects", []):
            _validate_upkeep_effect(name, effect, valid_armors)

    for name, tags in rules.build_kits.items():
        _assert_known_tags(f"build_kits.{name}", tags, valid_tags)

    for name, profile in rules.static_playstyles.items():
        primaries = profile.get("primaries", [])
        if any(p not in valid_tactics for p in primaries):
            raise ValueError(f"static_playstyles.{name}.primaries has invalid tactic indexes")
        rate = float(profile.get("initiate_rate", 0.5))
        if not 0 <= rate <= 1:
            raise ValueError(f"static_playstyles.{name}.initiate_rate must be between 0 and 1")
    for name, profile in rules.adaptive_playstyles.items():
        rate = float(profile.get("initiate_rate", 0.5))
        if not 0 <= rate <= 1:
            raise ValueError(f"adaptive_playstyles.{name}.initiate_rate must be between 0 and 1")


def _assert_known_tags(label: str, tags: list[str], valid_tags: set[str]) -> None:
    bad = set(tags) - valid_tags
    if bad:
        raise ValueError(f"{label} has unknown tags: {sorted(bad)}")


def _validate_upkeep_effect(pursuit_name: str, effect: dict[str, Any], valid_armors: set[str]) -> None:
    allowed = {"flat", "if_shield", "if_ranged", "if_armor_in"}
    keys = set(effect)
    if not keys or keys - allowed:
        raise ValueError(f"pursuits_info.{pursuit_name}.upkeep_effects has invalid effect keys: {sorted(keys)}")
    if "if_armor_in" in effect:
        armors, amount = effect["if_armor_in"]
        bad_armors = set(armors) - valid_armors
        if bad_armors:
            raise ValueError(f"pursuits_info.{pursuit_name}.if_armor_in has unknown armor: {sorted(bad_armors)}")
        int(amount)
    for key in ("flat", "if_shield", "if_ranged"):
        if key in effect:
            int(effect[key])


def _json_clean(value: Any) -> Any:
    if callable(value):
        return None
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k == "func" or callable(v):
                continue
            out[str(k) if k is not None else NONE_KEY] = _json_clean(v)
        return out
    if isinstance(value, (list, tuple)):
        return [_json_clean(v) for v in value]
    if isinstance(value, set):
        return sorted(_json_clean(v) for v in value)
    return value


def _encode_none_keys(data: dict[Any, Any]) -> dict[str, Any]:
    return {NONE_KEY if k is None else k: v for k, v in data.items()}


def _decode_none_keys(data: dict[str, Any]) -> dict[Any, Any]:
    return {None if k == NONE_KEY else k: v for k, v in data.items()}


def _encode_tactic_matrix(matrix: dict[tuple[str, str], tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    return {
        f"{a}{TACTIC_KEY_SEP}{b}": [_json_clean(a_mods), _json_clean(b_mods)]
        for (a, b), (a_mods, b_mods) in matrix.items()
    }


def _decode_tactic_matrix(data: dict[str, Any]) -> dict[tuple[str, str], tuple[dict[str, Any], dict[str, Any]]]:
    out = {}
    for key, value in data.items():
        if TACTIC_KEY_SEP not in key:
            raise ValueError(f"Invalid tactic matrix key: {key}")
        a, b = key.split(TACTIC_KEY_SEP, 1)
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError(f"Invalid tactic matrix value for {key}")
        out[(a, b)] = (dict(value[0]), dict(value[1]))
    return out
