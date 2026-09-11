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
            f"Fatigue -{FATIGUE_STRIKE}/-{FATIGUE_MORALE} | auto-pass {AUTO_PASS_FLOOR}")


# ── Additional printed thresholds (data-side defaults, engine-visible) ───────
PARRY_BASE    = _env_int("RENOWN_PARRY_BASE", 8)    # base Parry target
RECOVER_BASE  = _env_int("RENOWN_RECOVER_BASE", 8) # worst rung of the Recover ladder
DEADLY_AP     = _env_int("RENOWN_DEADLY_AP", 3)     # additional AP on a Focused Deadly strike
