"""dice_config — single source for die size across both combat engines.

Import this; never hardcode a face count. Changing FACES here changes every
threshold, RNG bound, cap clip and rout test in the vectorized and scalar
engines simultaneously.

Values can be overridden per-run via environment variables (RENOWN_FACES,
RENOWN_FOCUSED_THR, RENOWN_FATIGUE_STRIKE, RENOWN_FATIGUE_MORALE,
RENOWN_AUTO_PASS_FLOOR). run_tournament_d10.py sets these so multiprocessing
workers spawned on Windows inherit the same dice settings as the parent —
without them a worker would silently re-read the file defaults and produce
results from a different die than the one you asked for.
"""
import os
import re as _re
_BONUS_STATS = ("Parry", "Save", "Strike", "Shake", "Init", "AP")
_BONUS_RE = _re.compile(r'^(Parry|Save|Strike|Shake|Init|AP)\s*([+-]\d+)$')
_LEGACY = {"+1I": ("Init", 1), "+1TH": ("Strike", 1), "Improved Parry": ("Parry", 1)}
# NB: "Shake +1" is NOT in _LEGACY — it already matches the regex natively.

def parse_bonuses(tags):
    """Sum every '<Stat> +N' tag (+ legacy aliases) into {stat: total}, cumulative.
    +N = better for the wielder for every stat; AP uses -N (more negative = more AP)."""
    out = {s: 0 for s in _BONUS_STATS}
    for t in tags:
        t = str(t).strip()
        if t in _LEGACY:
            s, a = _LEGACY[t]; out[s] += a; continue
        m = _BONUS_RE.match(t)
        if m:
            out[m.group(1)] += int(m.group(2))
    return out

def _env_int(name, default):
    raw = os.environ.get(name)
    if raw is None or str(raw).strip() == "":
        return default
    raw = str(raw).strip()
    if raw.lower() in ("none", "null"):
        return None
    try:
        return int(raw)
    except ValueError:
        return default


# ── Core dice settings ───────────────────────────────────────────────────────
FACES           = _env_int("RENOWN_FACES", 10)                    # die size for every combat roll
FOCUSED_THR     = _env_int("RENOWN_FOCUSED_THR", FACES)           # Focused fires on this natural result or higher
ROUT_THR        = _env_int("RENOWN_ROUT_THR", FACES + 1)          # modified Morale target >= this Routs
CAP_THR         = _env_int("RENOWN_CAP_THR", FACES)               # worst printable target (the "6+" ceiling on d6)
AUTO_PASS_FLOOR = _env_int("RENOWN_AUTO_PASS_FLOOR", 2)           # target below this auto-passes; None deletes the rule
FATIGUE_STRIKE  = _env_int("RENOWN_FATIGUE_STRIKE", 2)            # per-token Strike penalty (magnitude)
FATIGUE_MORALE  = _env_int("RENOWN_FATIGUE_MORALE", 2)            # per-token Morale penalty (magnitude)


# ── Derived helpers ──────────────────────────────────────────────────────────
def p_success(target):
    """Probability one die meets `target`+, honouring the auto-pass floor."""
    if AUTO_PASS_FLOOR is not None and target < AUTO_PASS_FLOOR:
        return 1.0
    if target > FACES:
        return 0.0
    return (FACES - target + 1) / FACES


def p_fail(target):
    return 1.0 - p_success(target)


def describe():
    return (f"d{FACES} | Focused {FOCUSED_THR}+ | Rout {ROUT_THR}+ | cap {CAP_THR}+ | "
            f"Fatigue -{FATIGUE_STRIKE}/-{FATIGUE_MORALE} | auto-pass {AUTO_PASS_FLOOR} | "
            f"Parry {PARRY_BASE}+ | Recover {RECOVER_BASE}+ | "
            f"Deadly {DEADLY_MODE} {DEADLY_AP} | Unstoppable +{UNSTOPPABLE_MOD} | ImpParry -{IMPROVED_PARRY_MOD}")


# ── Additional printed thresholds (data-side defaults, engine-visible) ───────
PARRY_BASE    = _env_int("RENOWN_PARRY_BASE", 8)    # base Parry target
RECOVER_BASE  = _env_int("RENOWN_RECOVER_BASE", 8) # worst rung of the Recover ladder
DEADLY_AP     = _env_int("RENOWN_DEADLY_AP", 3)     # additional AP on a Focused Deadly strike
def _env_str(name, default):
    raw = os.environ.get(name)
    return default if raw is None or str(raw).strip() == "" else str(raw).strip()

DEADLY_MODE        = _env_str("RENOWN_DEADLY_MODE", "additional")  # "additional" = save_t + DEADLY_AP ; "set" = override (see OPEN #1)
UNSTOPPABLE_MOD    = _env_int("RENOWN_UNSTOPPABLE_MOD", 2)         # +N to the defender's Parry target when the attacker is Unstoppable
IMPROVED_PARRY_MOD = _env_int("RENOWN_IMPROVED_PARRY_MOD", 1)      # -N to the defender's own Parry target with Improved Parry