"""SHIM — do not edit. Redirects `import combat_morale` to combat_morale_d10.

CE/Combatv4/shims sits first on sys.path, so the verbatim copies of loadouts,
playstyles, batch_engine, normalized_matrix, tournament_vec and run_tournament
transparently get the d10 build without any source changes — meaning they can be
re-copied straight from Combatv3 whenever those files change.

Replacing sys.modules here (rather than re-exporting names) keeps module
identity intact and makes lazy imports work, and because it is a real file on
disk it survives Windows 'spawn' when batch_engine forks its workers.
"""
import sys, importlib

sys.modules[__name__] = importlib.import_module("combat_morale_d10")
