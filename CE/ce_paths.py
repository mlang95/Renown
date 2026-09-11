"""ce_paths.py — path bootstrap for the d10 build.

CE is fully self-contained. Nothing here reaches into Combatv3; the d6 tree can
be moved, renamed or deleted without affecting these runs.

    Game\\
      Combatv3\\                     <- d6 build, untouched, never imported
      CE\\
        renown_data_d10.py          <- the d10 data (edit AP here)
        run_tournament_d10.bat      <- double-click entry point
        run_tournament_d10.py
        ce_paths.py
        verify_d10.py
        lab_out\\                    <- parquet/csv output, one subfolder per run
        Combatv4\\
          dice_config.py            <- the single dice knob
          shims\\                    <- redirect modules
          *_d10.py                  <- patched engines
          loadouts.py               <- verbatim copies of the unmodified pipeline
          playstyles.py
          batch_engine.py
          normalized_matrix.py
          tournament_vec.py
          run_tournament.py

Search order is Combatv4/shims -> CE -> Combatv4, so `import renown_data` inside
a verbatim copy resolves to renown_data_d10. Because the copies are byte-identical
to Combatv3's, refreshing them later is a straight file copy — no re-patching.

PYTHONPATH is exported so multiprocessing workers spawned by batch_engine
resolve modules the same way on Windows.
"""
import os
import sys

CE_DIR = os.path.dirname(os.path.abspath(__file__))
V4_DIR = os.path.join(CE_DIR, "Combatv4")
SHIM_DIR = os.path.join(V4_DIR, "shims")
OUT_DIR = os.path.join(CE_DIR, "lab_out")

_ORDER = [SHIM_DIR, CE_DIR, V4_DIR]

# renown_data_d10.py is located rather than pinned: build_all.bat and the
# tournament runner disagree about where it should sit, so whichever of these
# holds it wins and that folder goes on the path. Everything else has a fixed home.
DATA_SEARCH = [CE_DIR, V4_DIR, os.path.join(CE_DIR, "data"), os.path.dirname(CE_DIR)]

REQUIRED = {
    V4_DIR: ["dice_config.py", "vectorized_combat_d10.py", "combat_kernel_d10.py",
             "combat_morale_d10.py", "combat_primitives_d10.py", "renown_combat_d10.py",
             "loadouts.py", "playstyles.py", "batch_engine.py",
             "normalized_matrix.py", "tournament_vec.py", "run_tournament.py"],
    SHIM_DIR: ["renown_data.py", "vectorized_combat.py", "combat_kernel.py",
               "combat_morale.py", "combat_primitives.py", "renown_combat.py"],
}


def find_data():
    """Return the folder containing renown_data_d10.py, or None."""
    for d in DATA_SEARCH:
        if os.path.isfile(os.path.join(d, "renown_data_d10.py")):
            return d
    return None


def install(verbose: bool = True) -> str:
    missing_dirs = [p for p in _ORDER if not os.path.isdir(p)]
    if missing_dirs:
        raise RuntimeError("ce_paths: missing folder(s):\n  " + "\n  ".join(missing_dirs))

    gaps = []
    for d, files in REQUIRED.items():
        for f in files:
            if not os.path.isfile(os.path.join(d, f)):
                gaps.append(os.path.join(d, f))
    if gaps:
        raise RuntimeError("ce_paths: missing file(s):\n  " + "\n  ".join(gaps))

    data_dir = find_data()
    if data_dir is None:
        raise RuntimeError(
            "ce_paths: renown_data_d10.py not found. Looked in:\n  "
            + "\n  ".join(DATA_SEARCH))
    if data_dir not in _ORDER:
        _ORDER.append(data_dir)

    for p in reversed(_ORDER):
        while p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)

    existing = os.environ.get("PYTHONPATH", "")
    parts = list(_ORDER)
    if existing:
        parts += [p for p in existing.split(os.pathsep) if p and p not in parts]
    os.environ["PYTHONPATH"] = os.pathsep.join(parts)

    os.makedirs(OUT_DIR, exist_ok=True)

    if verbose:
        print("ce_paths: data     =", os.path.join(data_dir, "renown_data_d10.py"))
        print("ce_paths: search order")
        for p in _ORDER:
            print("   ", p)
        print("ce_paths: OUT_DIR =", OUT_DIR)
    return OUT_DIR


def assert_isolated():
    """Fail if anything resolved out of a Combatv3 (or other) tree."""
    import renown_data, vectorized_combat, combat_kernel, combat_morale
    import combat_primitives, renown_combat, loadouts, playstyles, batch_engine

    strays = []
    for name, mod in [("renown_data", renown_data), ("vectorized_combat", vectorized_combat),
                      ("combat_kernel", combat_kernel), ("combat_morale", combat_morale),
                      ("combat_primitives", combat_primitives), ("renown_combat", renown_combat),
                      ("loadouts", loadouts), ("playstyles", playstyles),
                      ("batch_engine", batch_engine)]:
        path = os.path.abspath(getattr(mod, "__file__", ""))
        if not path.startswith(CE_DIR):
            strays.append(f"{name} <- {path}")
    if strays:
        raise RuntimeError("ce_paths: modules loaded from OUTSIDE the CE tree:\n  " + "\n  ".join(strays))
    return True


def assert_d10():
    """Confirm the d10 build is live — structurally, not against fixed values.

    An earlier version asserted specific retinue and armor numbers; every time
    those were tuned the runner refused to start. It now checks only what must be
    true of ANY d10 build: the data is a -d10 file, its dice constants agree with
    dice_config, and every combat threshold is rollable on the configured die.
    """
    import renown_data as rd
    import dice_config as dc

    problems = []
    if getattr(rd, "FACES", None) != dc.FACES:
        problems.append(f"renown_data.FACES={getattr(rd, 'FACES', None)} vs dice_config.FACES={dc.FACES}")
    if not str(getattr(rd, "VERSION", "")).endswith("-d10"):
        problems.append(f"renown_data.VERSION={getattr(rd, 'VERSION', None)!r} (expected a -d10 build)")

    lo = dc.AUTO_PASS_FLOOR if dc.AUTO_PASS_FLOOR is not None else 1
    for n, v in rd.RETINUES.items():
        for k in ("to_hit", "shaking"):
            if not (lo <= v[k] <= dc.FACES):
                problems.append(f"{n}.{k}={v[k]} outside {lo}..{dc.FACES}")
    for n, v in rd.ARMORS.items():
        if not (lo <= v["save"] <= dc.FACES):
            problems.append(f"armor {n} save={v['save']} outside {lo}..{dc.FACES}")

    # A d6 file leaking in is the failure this is really guarding against: on d6 the
    # worst armor is 7, so nothing would ever be near FACES.
    if max(v["save"] for v in rd.ARMORS.values()) <= 7 and dc.FACES == 10:
        problems.append("no armor save above 7 — this looks like the d6 data file")

    if problems:
        raise RuntimeError("ce_paths.assert_d10 FAILED:\n  " + "\n  ".join(problems))
    return True