# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-11-03 · data VERSION `0.4.9.9.15-d10-STrue` · HEAD `dc1d49d 2026-11-02`

Hand-written orientation: `CLAUDE.md` (same folder). Paths below are relative to the repo root.

## 1. Folder tree

```
./  (12 files)
  0.4.8 Updated Docs/  (7 files)
  0.4.8.1/  (36 files)
  Assets/  (102 files, generated/assets — not indexed)
  CE/  (42 files)
    .claude/  (1 files)
    Combatv4/  (17 files)
      shims/  (6 files)
    Simulator/  (7 files)
      engine/  (3 files)
    Tasks/  (22 files)
    ask-the-bot/  (3 files)
    lab_out/  (432 files, generated/assets — not indexed)
    mapgen/  (18 files)
      maps/  (20 files)
    references/  (54 files)
      board/  (2 files)
        js/  (18 files)
      fonts/  (16 files, generated/assets — not indexed)
      games/  (3 files)
    worldbuilding/  (17 files)
  Combatv3/  (137 files)
    ask-the-bot/  (4 files)
    cards/  (17 files)
    fonts/  (14 files, generated/assets — not indexed)
    lab_out/  (30 files, generated/assets — not indexed)
    mapgen/  (8 files)
    worldbuilding/  (32 files)
  generators/  (22 files)
```

## 2. Source files

| File | Lines | Purpose |
|---|---|---|
| `REPO_MAP.md` | 810 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `renown_data_d10.py` | 4740 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `0.4.8 Updated Docs/equipment-0.4.8.csv` | 38 | columns: Name,Category,Tier,AP,Initiative,Save,Effects,Cost,To Hit,Endurance,Shaking,Specialization Unlock,Note |
| `0.4.8 Updated Docs/factions-0.4.8.csv` | 42 | columns: Inspiration,AI Name,Feel,Difficulty,Strength,Mechanic,Pair,Complement |
| `0.4.8 Updated Docs/specs-0.4.8.csv` | 107 | columns: Pursuits,Type,Unlock Requirement,Mastery Requirement,Innate Effects,Mastery Effect,Builds Into |
| `0.4.8.1/ESCALATION_master.md` | 214 | RENOWN — ESCALATION CAMPAIGN |
| `0.4.8.1/build_all.bat` | 83 | build_all.bat — regenerate everything downstream of renown_data.py. |
| `0.4.8.1/build_escalation.py` | 34 | build_escalation.py — fill {{TABLE:x}} markers in the authored Escalation |
| `0.4.8.1/build_escalation_campaign_pdf.py` | 506 | Build ESCALATION_CAMPAIGN.pdf. Portrait main doc + a merged LANDSCAPE two-player Domain Board page. |
| `0.4.8.1/card_copies.py` | 69 | card_copies.py — print-quantity logic for pursuit cards, driven by the spec |
| `0.4.8.1/card_sheet.py` | 634 | Renown — Specialization card sheet generator. |
| `0.4.8.1/economy.py` | 161 | economy.py — per-turn gold model for Renown builds, derived from renown_data. |
| `0.4.8.1/equipment.csv` | 39 | columns: Name,Category,Tier,AP,Initiative,Save,Effects,Cost,To Hit,Endurance,Shaking,Specialization Unlock,Note |
| `0.4.8.1/equipment_sheet.py` | 670 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `0.4.8.1/escalation_tables.py` | 60 | escalation_tables.py — generate the Escalation Campaign's data tables from |
| `0.4.8.1/export_csvs.py` | 73 | export_csvs.py — export renown_data.py to CSVs for spreadsheet VIEWING. |
| `0.4.8.1/faction_sheet.py` | 423 | Renown — Faction card sheet generator. |
| `0.4.8.1/gen_compendium.py` | 196 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `0.4.8.1/generate_cards.py` | 90 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `0.4.8.1/income_profile.py` | 117 | income_profile.py — classify a build's economy by SOURCE, tag its inflation |
| `0.4.8.1/loadouts.py` | 1915 | Loadout generator for the combat tournament. |
| `0.4.8.1/monument_viability.py` | 123 | monument_viability.py — for every Monument, test the two viability constraints: |
| `0.4.8.1/render_trees.py` | 92 | Render the Escalation talent trees from nodes_escalation.csv to a |
| `0.4.8.1/renown_combat.py` | 495 | Renown combat simulator. |
| `0.4.8.1/renown_data.py` | 1929 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `0.4.8.1/spec_tree_sheet.py` | 1036 | Renown — Specialization Tree renderer. |
| `0.4.8.1/specs.csv` | 107 | columns: Pursuits,Type,Unlock Requirement,Mastery Requirement,Innate Effects,Mastery Effect,Builds Into |
| `0.4.8.1/tactic_sheet.py` | 430 | Renown — Tactic card sheet generator (v3). |
| `0.4.8.1/two_monument_builds.py` | 118 | two_monument_builds.py — for the monument cap of 2, generate every viable |
| `0.4.8.1/verify_engine.py` | 253 | verify_engine.py — golden-case tests for the Escalation combat engine. |
| `CE/AUDIT_2026-10-30.md` | 90 | Consistency audit — 30 Oct 2026 |
| `CE/CHANGES.md` | 77 | Changes in this bundle |
| `CE/CLAUDE.md` | 69 | CLAUDE.md — Renown repo orientation (lives in `CE/`; paths below are relative to `CE/`) |
| `CE/COMPREHENSIVE_RULES_OUTLINE.md` | 180 | Renown — Comprehensive Rules: outline |
| `CE/ENVOY_WINDOW_REVIEW.md` | 88 | Envoy timing windows — review list |
| `CE/HOLDING_MECHANICS_AUDIT.md` | 54 | Holding Mechanics Audit |
| `CE/INFLUENCE_WORDING_AUDIT.md` | 76 | Influence / Authority wording audit |
| `CE/PLAYSTYLE_REVIEW.md` | 105 | Playstyle reference — fit review (SIMPLE build, 2026-10-30) |
| `CE/PRONOUN_WORDING_AUDIT.md` | 85 | "You / this player / the target" wording audit |
| `CE/REPO_MAP.md` | 969 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE/RULES_push.md` | 649 | Renown |
| `CE/RULES_push_simple.md` | 723 | Renown |
| `CE/RULES_reorganized_6.md` | 638 | Renown |
| `CE/SIMPLE_NODES.PY` | 1 |  |
| `CE/TASK8_NOTES.md` | 152 | claude_task_8 — what changed, open items |
| `CE/TASK9_NOTES.md` | 83 | claude_task_9 — Rules.docx pass: what changed, open items |
| `CE/build_all_CE.bat` | 526 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE/ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE/infra.py` | 109 |  |
| `CE/keyword_bloat_v2.md` | 101 | Keyword Bloat — v2 |
| `CE/parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE/patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE/rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE/renown_data.py` | 4206 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_data_d10.py` | 4206 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_data_d10_legacy.py` | 5076 | renown_data_d10_legacy — FROZEN 2026-10-30. The legacy (SIMPLE=0) data: innate + mastery Pursuits, the |
| `CE/renown_data_d8.py` | 2801 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_server.bat` | 16 | renown_server.bat - (re)start the Renown board server in WSL. |
| `CE/repo_map.py` | 250 | repo_map.py — write REPO_MAP.md next to this file (CE/, beside CLAUDE.md): a generated index of the Renown repo for |
| `CE/run_tournament_d10.bat` | 110 | Renown d10 tournament runner  —  CE build |
| `CE/run_tournament_d10.py` | 131 | run_tournament_d10.py — run the Renown tournament against the d10 build. |
| `CE/sprites.py` | 6336 | sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene). |
| `CE/verify_d10.py` | 168 | verify_d10.py — prove the CE wiring is live before spending hours on a run. |
| `CE/.claude/launch.json` | 233 |  |
| `CE/Combatv4/analysis.py` | 2125 | Analysis module for tournament results. |
| `CE/Combatv4/batch_engine.py` | 1660 | Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays, |
| `CE/Combatv4/combat_kernel_d10.py` | 268 | combat_kernel.py — SHARED numba kernels for both combat engines. |
| `CE/Combatv4/combat_morale_d10.py` | 155 | combat_morale.py — SHARED morale phase for both combat engines (C2, subsystem 2). |
| `CE/Combatv4/combat_primitives_d10.py` | 147 | combat_primitives.py — SHARED rules-math layer for both combat engines (C2). |
| `CE/Combatv4/dice_config.py` | 116 | dice_config — single source for die size across both combat engines. |
| `CE/Combatv4/loadouts.py` | 1264 | Loadout generator for the combat tournament. |
| `CE/Combatv4/make_d10_data.py` | 172 | Generate renown_data_d10.py from renown_data_CE.py. |
| `CE/Combatv4/make_d10_engines.py` | 143 | Generate *_d10.py engine files with FACES parameterised. |
| `CE/Combatv4/normalized_matrix.py` | 277 | Normalized symmetric tactic matrix. |
| `CE/Combatv4/playstyles.py` | 784 | Playstyle module — playstyles drive tactic selection in combat. |
| `CE/Combatv4/renown_combat_d10.py` | 563 | Renown combat simulator. |
| `CE/Combatv4/run_tournament.py` | 200 | Standalone Renown tournament runner. |
| `CE/Combatv4/tactics_analysis.py` | 54 | Tactics analysis helpers for the Renown Combat Lab. |
| `CE/Combatv4/tournament_vec.py` | 356 | Vectorized tournament runner — same interface as tournament.py but ~4x faster |
| `CE/Combatv4/vectorized_combat_d10.py` | 1979 | Vectorized matchup runner. |
| `CE/Combatv4/shims/combat_kernel.py` | 15 | SHIM — do not edit. Redirects `import combat_kernel` to combat_kernel_d10. |
| `CE/Combatv4/shims/combat_morale.py` | 15 | SHIM — do not edit. Redirects `import combat_morale` to combat_morale_d10. |
| `CE/Combatv4/shims/combat_primitives.py` | 15 | SHIM — do not edit. Redirects `import combat_primitives` to combat_primitives_d10. |
| `CE/Combatv4/shims/renown_combat.py` | 15 | SHIM — do not edit. Redirects `import renown_combat` to renown_combat_d10. |
| `CE/Combatv4/shims/renown_data.py` | 15 | SHIM — do not edit. Redirects `import renown_data` to renown_data_d10. |
| `CE/Combatv4/shims/vectorized_combat.py` | 15 | SHIM — do not edit. Redirects `import vectorized_combat` to vectorized_combat_d10. |
| `CE/Simulator/analyse_sim.py` | 307 | analyse_sim.py — turn a simulator run (lab_out/sim/<TAG>/games.jsonl) into tables, a report and end screens. |
| `CE/Simulator/compare_runs.py` | 38 | compare_runs.py — Bandit and army headline numbers, side by side, for simulator runs in lab_out/sim/. |
| `CE/Simulator/probe_boards.js` | 21 | probe_boards.js — end-of-game board quality per player: Wards used / capacity, efficient riders (Holdings that use no Ward), |
| `CE/Simulator/probe_build.js` | 24 | probe_build.js — every few turns of one all-AI game: can each bot Build, and what beats Build in its scoring? |
| `CE/Simulator/run_sim.bat` | 86 | Renown game simulator  —  CE build |
| `CE/Simulator/sim_runner.js` | 82 | sim_runner.js — run many all-AI games in parallel (worker threads) and write every game's record to games.jsonl. |
| `CE/Simulator/trace_game.js` | 26 | trace_game.js — play one all-AI game and print, turn by turn, what each bot considered and chose. |
| `CE/Simulator/engine/dom_shim.js` | 81 | dom_shim.js — a do-nothing browser for running the settlement board's script headless. |
| `CE/Simulator/engine/load_board.js` | 38 | load_board.js — read the built settlement board once and hand back its script, ready to run in a sandbox. |
| `CE/Simulator/engine/sim_core.js` | 277 | sim_core.js — appended inside the settlement board's script (same scope: D, tSim, aiTick, roll, … are all in reach). |
| `CE/Tasks/Claude_task_9.txt` | 28 |  |
| `CE/Tasks/ENVOY_WINDOW_REVIEW.md` | 86 | Envoy timing windows — review list |
| `CE/Tasks/MAPGEN_COVERAGE.md` | 28 | Map generator — Holding / Monument coverage by region preset |
| `CE/Tasks/PROPOSALS_new_things.md` | 275 | Proposals — "New things to consider" + rules syntax pass |
| `CE/Tasks/REPO_MAP.md` | 870 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE/Tasks/SYNTAX_SWEEP.md` | 343 | Rules syntax sweep — canon applied |
| `CE/Tasks/TASK2_NOTES.md` | 82 | claude_task_2 — what changed, open questions |
| `CE/Tasks/TASK3_NOTES.md` | 43 | claude_task_3 — what changed, open questions |
| `CE/Tasks/TASK4_NOTES.md` | 139 | claude_task_4 — what changed, open questions |
| `CE/Tasks/TASK5_NOTES.md` | 74 | claude_task_5 — what changed, open items |
| `CE/Tasks/TASK6_NOTES.md` | 72 | claude_task_6 — what changed, open items |
| `CE/Tasks/TASK7_NOTES.md` | 36 | claude_task_7 — what changed, open items |
| `CE/Tasks/TASK8_NOTES.md` | 127 | claude_task_8 — what changed, open items |
| `CE/Tasks/WIKI_RULES_RESTRUCTURE.md` | 79 | Wiki rules — restructure draft (proposal, not applied) |
| `CE/Tasks/claude_task.txt` | 85 |  |
| `CE/Tasks/claude_task_2.txt` | 68 |  |
| `CE/Tasks/claude_task_3.txt` | 24 |  |
| `CE/Tasks/claude_task_4.txt` | 44 |  |
| `CE/Tasks/claude_task_5.txt` | 23 |  |
| `CE/Tasks/claude_task_6.txt` | 51 |  |
| `CE/Tasks/claude_task_7.txt` | 18 |  |
| `CE/Tasks/claude_task_8.txt` | 17 |  |
| `CE/ask-the-bot/equipment_table.csv` | 40 | columns: Item,Type,Tier,AP_or_Save,Init,Keywords |
| `CE/ask-the-bot/factions_table.csv` | 40 | columns: Faction,Difficulty,Strength,Mechanic |
| `CE/ask-the-bot/renown_faq.txt` | 556 |  |
| `CE/mapgen/app_shell.html` | 732 | Renown — Map Generator |
| `CE/mapgen/build_board.py` | 451 | build_board.py - print-and-tape Renown board from a procedural map. |
| `CE/mapgen/build_mapapp.py` | 235 | build_mapapp.py - assemble renown-maps.html from its sources. |
| `CE/mapgen/gen.js` | 1999 | gen.js — Renown regional map generator, JS port. |
| `CE/mapgen/gen_cli.js` | 20 | gen_cli.js - run gen.js from Python (mapgen_regional.generate_region), so the app, the settlement |
| `CE/mapgen/gen_settlement_board.py` | 5268 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE/mapgen/hexgen.py` | 258 | hexgen.py — generate the Renown hex asset set as standalone SVGs. |
| `CE/mapgen/hexmap.py` | 85 | hexmap.py — the territory graph (C1). |
| `CE/mapgen/hexstyle.py` | 270 | hexstyle.py - the ONE source for how a board looks. |
| `CE/mapgen/mapgen.py` | 908 | mapgen.py — procedural Renown map generator. |
| `CE/mapgen/mapgen_regional.py` | 254 | mapgen_regional.py — preset-driven map generation for Renown, through gen.js. |
| `CE/mapgen/presets.js` | 1609 | presets.js - GENERATED from region_presets.py. Do not hand-edit. */ |
| `CE/mapgen/region_presets.py` | 514 | region_presets.py — regional map-generation presets for Renown. |
| `CE/mapgen/renown-maps.html` | 4338 | Renown — Map Generator |
| `CE/references/build_compendium.js` | 133 | build_compendium.js — render the Compendium .docx from renown_data JSON, |
| `CE/references/build_compendium.py` | 394 | build_compendium2.py — redesigned Compendium .docx from compendium_data.json. |
| `CE/references/build_wiki.py` | 1650 | build_wiki.py — multi-page linked HTML wiki from RULES.md + renown_data. |
| `CE/references/card_copies.py` | 68 | card_copies.py — print-quantity logic for pursuit cards, driven by the spec |
| `CE/references/card_sheet.py` | 679 | Renown — Specialization card sheet generator. |
| `CE/references/ce_paths.py` | 123 | ce_paths.py — path bootstrap for the d10 build. |
| `CE/references/combat_sheet.py` | 352 | combat_sheet.py — Renown combat quick-reference (print & laminate). |
| `CE/references/combine_docx.py` | 257 | combine_docx.py — append the Compendium after the Rules doc as one book: |
| `CE/references/compendium_data.json` | 3273 |  |
| `CE/references/display_pdf.py` | 90 | display_pdf.py — NAME_DISPLAY for every reportlab sheet (cards, tiles, equipment, combat). |
| `CE/references/docx_tables.py` | 692 | docx_tables.py — generate Word table fragments (OOXML) from renown_data. |
| `CE/references/domain_board.py` | 341 | domain_board.py - landscape Domain Standing Board. |
| `CE/references/effect_registry.py` | 412 | effect_registry.py -- every rules-text pattern the settlement board acts on, matched once at build time. |
| `CE/references/equipment_sheet.py` | 691 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `CE/references/faction_sheet.py` | 447 | Renown — Faction card sheet generator. |
| `CE/references/faq_export.py` | 444 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `CE/references/gen_compendium.py` | 185 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `CE/references/gen_layout.py` | 374 | gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data. |
| `CE/references/gen_layout_roots.py` | 123 | gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it. |
| `CE/references/gen_settlement_board.py` | 1072 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE/references/generate_cards.py` | 93 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `CE/references/host_sheet.py` | 456 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `CE/references/infra_board.py` | 134 | infra_board.py - landscape Infrastructure Board. |
| `CE/references/keyword_audit.py` | 96 | Exact per-strike-die model of the Renown CE strike chain (rules text as written), |
| `CE/references/layout.json` | 1421 |  |
| `CE/references/layout_roots.json` | 1698 |  |
| `CE/references/layout_simple.json` | 1948 |  |
| `CE/references/lobby.html` | 102 | Renown |
| `CE/references/md_to_docx.py` | 342 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `CE/references/package-lock.json` | 205 |  |
| `CE/references/package.json` | 6 |  |
| `CE/references/parity_efx.js` | 54 | parity_efx.js — replays effect_registry.py's patterns with JavaScript RegExp, the way the board used to read text at |
| `CE/references/patch_pursuit_domains.py` | 58 | patch_pursuit_domains.py |
| `CE/references/playstyle_reference.py` | 463 | playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture). |
| `CE/references/pursuit_tiles.py` | 284 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `CE/references/reference_sheets.py` | 873 | Renown — Reference sheet generators. |
| `CE/references/render_tree.py` | 272 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `CE/references/rule_numbers.py` | 267 | rule_numbers.py — MTG-style rule numbers for the rules markdown, computed at render time. |
| `CE/references/server.py` | 679 | Renown settlement-board server  —  stdlib only, no pip installs. |
| `CE/references/settlement_board.html` | — | generated HTML (2089 KB) |
| `CE/references/settlement_mats.py` | 302 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `CE/references/spec_tree_sheet.py` | 1184 | Renown — Specialization Tree renderer. |
| `CE/references/svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `CE/references/sync_derived.py` | 88 | sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES. |
| `CE/references/tactic_sheet.py` | 446 | Renown — Tactic card sheet generator (v3). |
| `CE/references/wiki_markers.py` | 296 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
| `CE/references/world.txt` | 1517 |  |
| `CE/references/worldtxt.py` | 328 | worldtxt.py — parse the hand-maintained world.txt lore book into structured |
| `CE/references/board/body.html` | 216 |  |
| `CE/references/board/js/00_core.js` | 56 | __DATA__*/; |
| `CE/references/board/js/10_table.js` | 998 | ===================== TABLE: seating, Council & Envoy phases ===================== |
| `CE/references/board/js/15_realm.js` | 521 | ===================== REALM: the play surface ===================== |
| `CE/references/board/js/16_tally.js` | 132 | ===================== INTRIGUE & TALLY PHASES (RULES: Envoy Phase steps 3 and 5) ===================== |
| `CE/references/board/js/17_diplo_step.js` | 131 | ===================== DIPLOMACY STEP (PHASE_REFORM): offers between players ===================== |
| `CE/references/board/js/20_state.js` | 621 | ---- state: multiplayer dashboard ---- |
| `CE/references/board/js/30_empire.js` | 1746 | ---- catalog ---- |
| `CE/references/board/js/35_plan.js` | 100 | ---- Plans (this device only): goal Holdings / Infrastructure / Wonders per player, in priority order. Each goal's path is worked |
| `CE/references/board/js/40_realm_data.js` | 403 | ---- Dashboards view ---- |
| `CE/references/board/js/50_battle.js` | 1107 | ---- Battle ---- |
| `CE/references/board/js/52_battlefield.js` | 190 | ---- Battle field: a top-down view between the two datasheets ---- |
| `CE/references/board/js/55_ai.js` | 500 | ---- AI players: culture-driven bots for seats marked AI (and, later, the headless simulator) ---- |
| `CE/references/board/js/60_map.js` | 1262 | ---- Map view ---- |
| `CE/references/board/js/70_rules.js` | 644 | ===================== EFFECT PLUMBING: the effect registry (references/effect_registry.py) ===================== |
| `CE/references/board/js/80_scene_shell.js` | 487 | ---- pixel scene: every settlement of the active player, drawn from sprites.py (every theme) ---- |
| `CE/references/board/js/85_ux.js` | 102 | ===================== CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper ===================== |
| `CE/references/board/js/86_welcome.js` | 108 | ===================== WELCOME: seats + profile (server games) ===================== |
| `CE/references/board/js/90_app.js` | 382 | ===================== UNDO / REDO ===================== |
| `CE/worldbuilding/book.json` | 2070 |  |
| `CE/worldbuilding/build_docx.js` | 147 | map image: RENOWN_MAP (set by build_all_CE.bat), else map7.png beside this |
| `CE/worldbuilding/draft.txt` | 220 |  |
| `CE/worldbuilding/gen_book_json.py` | 214 | gen_book_json.py |
| `CE/worldbuilding/gen_cultures.py` | 1014 | gen_cultures.py |
| `CE/worldbuilding/gen_draft.py` | 50 | gen_draft.py |
| `CE/worldbuilding/gen_intro.py` | 62 | gen_intro.py |
| `CE/worldbuilding/gen_pdf.py` | 422 | gen_pdf.py |
| `CE/worldbuilding/intro.txt` | 270 |  |
| `CE/worldbuilding/package-lock.json` | 205 |  |
| `CE/worldbuilding/package.json` | 6 |  |
| `CE/worldbuilding/renown_worldlore.py` | 3746 | renown_worldlore.py |
| `CE/worldbuilding/world.txt` | 1481 |  |
| `CE/worldbuilding/world_design.txt` | 2341 |  |
| `Combatv3/BATCH_STATUS.md` | 963 | v3 Batched Engine — Status |
| `Combatv3/ESCALATION_CAMPAIGN.md` | 260 | RENOWN — ESCALATION CAMPAIGN |
| `Combatv3/ESCALATION_master.md` | 211 | RENOWN — ESCALATION CAMPAIGN |
| `Combatv3/RULES.md` | 839 | Renown |
| `Combatv3/RULES_reorganized.md` | 636 | Renown |
| `Combatv3/RULES_reorganized_2.md` | 598 | Renown |
| `Combatv3/RULES_reorganized_5.md` | 633 | Renown |
| `Combatv3/RULES_reorganized_6.md` | 648 | Renown |
| `Combatv3/analysis.py` | 2108 | Analysis module for tournament results. |
| `Combatv3/batch_engine (2).py` | 1519 | Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays, |
| `Combatv3/batch_engine.py` | 1549 | Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays, |
| `Combatv3/build_all.bat` | 249 | build_all.bat - regenerate everything downstream of renown_data.py. |
| `Combatv3/build_compendium.js` | 133 | build_compendium.js — render the Compendium .docx from renown_data JSON, |
| `Combatv3/build_compendium.py` | 368 | build_compendium.py — render the Compendium .docx from compendium_data.json, |
| `Combatv3/build_docs.py` | 74 | build_docs.py — fill {{TABLE:name}}, {{GLOSSARY}}, and {{DEF:term}} markers in an |
| `Combatv3/build_escalation.py` | 34 | build_escalation.py — fill {{TABLE:x}} markers in the authored Escalation |
| `Combatv3/build_escalation_campaign_pdf.py` | 462 | Build ESCALATION_CAMPAIGN.pdf. Portrait main doc + a merged LANDSCAPE two-player Domain Board page. |
| `Combatv3/build_talent_tree5.py` | 360 | build_talent_tree.py - pursuit tech tree as a series of SEPARATE flowcharts. |
| `Combatv3/build_wiki.py` | 1418 | build_wiki.py — multi-page linked HTML wiki from RULES.md + renown_data. |
| `Combatv3/card_copies.py` | 69 | card_copies.py — print-quantity logic for pursuit cards, driven by the spec |
| `Combatv3/card_sheet.py` | 669 | Renown — Specialization card sheet generator. |
| `Combatv3/combat_kernel.py` | 234 | combat_kernel.py — SHARED numba kernels for both combat engines. |
| `Combatv3/combat_morale.py` | 152 | combat_morale.py — SHARED morale phase for both combat engines (C2, subsystem 2). |
| `Combatv3/combat_primitives.py` | 149 | combat_primitives.py — SHARED rules-math layer for both combat engines (C2). |
| `Combatv3/combat_sheet.py` | 340 | combat_sheet.py — Renown combat quick-reference (print & laminate). |
| `Combatv3/combine_docx.py` | 194 | combine_docx.py — append the Compendium after the Rules doc as one book: |
| `Combatv3/compendium_data.json` | 3353 |  |
| `Combatv3/docx_tables.py` | 403 | docx_tables.py — generate Word table fragments (OOXML) from renown_data. |
| `Combatv3/domain_board.py` | 315 | domain_board.py - landscape Domain Standing Board. |
| `Combatv3/economy.py` | 161 | economy.py — per-turn gold model for Renown builds, derived from renown_data. |
| `Combatv3/equipment.csv` | 39 | columns: Name,Category,Tier,AP,Initiative,Save,Effects,Cost,To Hit,Endurance,Shaking,Specialization Unlock,Note |
| `Combatv3/equipment_sheet.py` | 683 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `Combatv3/escalation_tables.py` | 60 | escalation_tables.py — generate the Escalation Campaign's data tables from |
| `Combatv3/export_csvs.py` | 73 | export_csvs.py — export renown_data.py to CSVs for spreadsheet VIEWING. |
| `Combatv3/faction_sheet.py` | 436 | Renown — Faction card sheet generator. |
| `Combatv3/factions_table.csv` | 42 | columns: Faction,Difficulty,Strength,Mechanic |
| `Combatv3/faq_export.py` | 425 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `Combatv3/gauntlet_run.bat` | 17 | Fixed-gauntlet power-level run — tests EVERY build vs a fixed panel (linear, fast). |
| `Combatv3/gauntlet_run.py` | 154 | Fixed-gauntlet power-level runner. |
| `Combatv3/gen_compendium.py` | 197 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `Combatv3/gen_escalation_nodes.py` | 45 | gen_escalation_nodes.py — regenerate nodes_escalation.csv from renown_data.NODES |
| `Combatv3/gen_nodes.py` | 14 | RETIRED — renown_data.py is now the hand-edited master for the node graph. |
| `Combatv3/generate_cards.bat` | 31 | Renown card generator — regenerates every deck from renown_data.py. |
| `Combatv3/generate_cards.py` | 90 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `Combatv3/generate_rules_truth.py` | 231 | generate_rules_truth.py — emits RULES_TRUTH.md, the single source of truth for Renown combat |
| `Combatv3/horde_mode.py` | 569 | Horde mode — multi-battle limit testing for armies. |
| `Combatv3/host_sheet.py` | 446 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `Combatv3/income_profile.py` | 117 | income_profile.py — classify a build's economy by SOURCE, tag its inflation |
| `Combatv3/infra_board.py` | 127 | infra_board.py - landscape Infrastructure Board. |
| `Combatv3/infra_strip.py` | 148 | infra_strip.py - infrastructure ownership grid. Names as column headers once |
| `Combatv3/layout.json` | 1403 |  |
| `Combatv3/layout_manifest.json` | 1403 |  |
| `Combatv3/loadouts.py` | 1782 | Loadout generator for the combat tournament. |
| `Combatv3/loadouts2.py` | 1283 | Loadout generator for the combat tournament. |
| `Combatv3/mapgen.py` | 795 | mapgen.py — procedural Renown map generator. |
| `Combatv3/md_to_docx.py` | 223 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `Combatv3/monument_viability.py` | 123 | monument_viability.py — for every Monument, test the two viability constraints: |
| `Combatv3/new 3.txt` | 91 |  |
| `Combatv3/nodes_escalation.csv` | 28 | columns: Name,Domain,Standing,Rank,Effect,Requires_All,Requires_Any,Extra_Req,Monument |
| `Combatv3/normalized_matrix.py` | 277 | Normalized symmetric tactic matrix. |
| `Combatv3/parity_harness.py` | 27 | parity_harness.py |
| `Combatv3/patch_pursuit_domains.py` | 57 | patch_pursuit_domains.py |
| `Combatv3/playstyle_reference.py` | 218 | playstyle_reference.py - one-page (landscape Letter) playstyle reference card. |
| `Combatv3/playstyles.py` | 784 | Playstyle module — playstyles drive tactic selection in combat. |
| `Combatv3/pursuit_review.html` | 122 | Renown Pursuit Review |
| `Combatv3/pursuit_review.py` | 196 | pursuit_review.py — generate a single self-contained HTML page for reviewing |
| `Combatv3/pursuit_tiles.py` | 267 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `Combatv3/reference_sheets.py` | 886 | Renown — Reference sheet generators. |
| `Combatv3/render_tree.py` | 249 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `Combatv3/render_trees.py` | 92 | Render the Escalation talent trees from nodes_escalation.csv to a |
| `Combatv3/render_trees_2x2.py` | 211 | render_trees_2x2.py — render the Escalation talent tree as FOUR per-domain |
| `Combatv3/renown_combat.py` | 562 | Renown combat simulator. |
| `Combatv3/renown_data.py` | 2574 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `Combatv3/renown_data_ce.py` | 2681 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `Combatv3/renown_faq.txt` | 372 |  |
| `Combatv3/retinue_gear_leaderboard.py` | 108 | ============================================================================ |
| `Combatv3/routes_DISCARDED.py` | 158 | routes.py - new-player route sheet. |
| `Combatv3/run_tournament.bat` | 39 | Renown tournament runner — edit the values below, then double-click or run from cmd. |
| `Combatv3/run_tournament.py` | 197 | Standalone Renown tournament runner. |
| `Combatv3/sensitivity_sweep.py` | 226 | Input x Output sensitivity sweep for Renown combat. |
| `Combatv3/settlement_mats.py` | 290 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `Combatv3/spec_tree_sheet.py` | 1160 | Renown — Specialization Tree renderer. |
| `Combatv3/svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `Combatv3/tactic_eval.py` | 159 | Tactic matrix evaluator — per-statline 6x6 (Fall Back excluded). |
| `Combatv3/tactic_init_threshold.py` | 156 | Threshold-conditioned tactic eval — where the gear->init coupling ACTUALLY decides games. |
| `Combatv3/tactic_pruning.py` | 147 | Tactic-pruning eval (marginal-edge version) — does EQUIPMENT shape which tactics are worth picking? |
| `Combatv3/tactic_sheet.py` | 443 | Renown — Tactic card sheet generator (v3). |
| `Combatv3/tactics_analysis.py` | 54 | Tactics analysis helpers for the Renown Combat Lab. |
| `Combatv3/tournament_vec.py` | 359 | Vectorized tournament runner — same interface as tournament.py but ~4x faster |
| `Combatv3/two_monument_builds.py` | 118 | two_monument_builds.py — for the monument cap of 2, generate every viable |
| `Combatv3/vectorized_combat.py` | 1831 | Vectorized matchup runner. |
| `Combatv3/verify_engine.py` | 253 | verify_engine.py — golden-case tests for the Escalation combat engine. |
| `Combatv3/verify_loadouts.py` | 228 | Local verification: does the optimized loadouts.py produce a pool IDENTICAL to the |
| `Combatv3/verify_step1.py` | 31 | Step-1 gate: run on YOUR machine with numba ON, after wiping the cache. |
| `Combatv3/verify_step2.py` | 33 | Step-2 gate: run on YOUR machine with numba ON, cache wiped. |
| `Combatv3/wiki_markers.py` | 211 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
| `Combatv3/worldtxt.py` | 328 | worldtxt.py — parse the hand-maintained world.txt lore book into structured |
| `Combatv3/ask-the-bot/equipment_table.csv` | 37 | columns: Item,Type,Tier,AP_or_Save,Init,Keywords |
| `Combatv3/ask-the-bot/factions_table.csv` | 42 | columns: Faction,Difficulty,Strength,Mechanic |
| `Combatv3/ask-the-bot/faq_export.py` | 350 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `Combatv3/ask-the-bot/renown_faq.txt` | 465 |  |
| `Combatv3/mapgen/build_board.py` | 294 | build_board.py - print-and-tape Renown board from a procedural map. |
| `Combatv3/mapgen/hexgen.py` | 281 | hexgen.py — generate the Renown hex asset set as standalone SVGs. |
| `Combatv3/worldbuilding/New Text Document.txt` | 1 |  |
| `Combatv3/worldbuilding/book.json` | 1805 |  |
| `Combatv3/worldbuilding/build_docx.js` | 142 | ---- title |
| `Combatv3/worldbuilding/coastline.py` | 54 | coastline.py - metaball landmass outline. Sum of a few offset circular fields; |
| `Combatv3/worldbuilding/cultures.txt` | 791 |  |
| `Combatv3/worldbuilding/draft.txt` | 220 |  |
| `Combatv3/worldbuilding/gen_book_json.py` | 214 | gen_book_json.py |
| `Combatv3/worldbuilding/gen_cultures.py` | 1014 | gen_cultures.py |
| `Combatv3/worldbuilding/gen_draft.py` | 50 | gen_draft.py |
| `Combatv3/worldbuilding/gen_intro.py` | 62 | gen_intro.py |
| `Combatv3/worldbuilding/gen_pdf.py` | 416 | gen_pdf.py |
| `Combatv3/worldbuilding/intro.txt` | 306 |  |
| `Combatv3/worldbuilding/renown_worldlore - Copy.py` | 1470 | renown_worldlore.py |
| `Combatv3/worldbuilding/renown_worldlore.md` | 266 | Renown — World Lore Framework |
| `Combatv3/worldbuilding/renown_worldlore.py` | 3364 | renown_worldlore.py |
| `Combatv3/worldbuilding/world.py` | 58 | world.py - fixed macro-geography of the setting. |
| `Combatv3/worldbuilding/world.txt` | 1517 |  |
| `Combatv3/worldbuilding/world_design.txt` | 2377 |  |
| `Combatv3/worldbuilding/world_map.py` | 74 | world_map.py - schematic map with organic (radial-fBm) coastlines. |
| `generators/equipment.csv` | 38 | columns: Name,Category,Tier,AP,Initiative,Save,Effects,Cost,Strike,Endurance,Morale,Pursuit Unlock,Note |
| `generators/factions.csv` | 42 | columns: Inspiration,AI Name,Feel,Difficulty,Strength,Mechanic,Pair,Complement |
| `generators/infrastructure.csv` | 18 | columns: Name,Category,Upkeep,Upkeep Frequency,Empire Bonus,Tier,Build Time,Requirement |
| `generators/spec_tree_sheet.py` | 1159 | Renown — Specialization Tree renderer. |
| `generators/spec_trees.csv` | 269 | columns: tree,pathology,node,parents,tier,domain,type |
| `generators/specs.csv` | 107 | columns: Pursuits,Type,Unlock Requirement,Mastery Requirement,Innate Effects,Mastery Effect,Builds Into |
| `generators/specs_escalation.csv` | 39 | columns: Pursuits,Type,Unlock Requirement,Mastery Requirement,Innate Effects,Mastery Effect,Builds Into |
| `generators/update_compendium.py` | 535 | update_compendium.py — drives Compendium.docx from the canonical CSVs. |

## 3. Data index — `CE/renown_data_d10.py`

Copied to `CE/renown_data.py` by the build (DIE=d10); every script imports `renown_data`.

| Name | Line | Type | Size / value |
|---|---|---|---|
| `SIMPLE` | 7 | bool | True |
| `PHASE_REFORM` | 10 | bool | True |
| `VERSION` | 12 | str | '0.4.9.9.15-d10-STrue' |
| `BLUNDER_THR` | 40 | int | 10 |
| `DICE_PROVENANCE` | 41 | str | 'd10 / Focused 10+ / Parry 8+ / Recover  |
| `SACK_EXTORT_PER_TIER` | 44 | int | 4000 |
| `INTERCEPT_EXTORT_PER_CRAFT` | 45 | int | 100 |
| `WEALTH_EDICT_GOLD` | 46 | int | 50000 |
| `MUSTER_RANGE` | 47 | int | 2 |
| `MARCH_MULTIPLIER` | 48 | int | 2 |
| `PO_MIN` | 49 | int | -10 |
| `PO_MAX` | 50 | int | 10 |
| `INITIATIVE_MIN` | 51 | int | -2 |
| `INITIATIVE_MAX` | 52 | int | 2 |
| `STANDING_THRESHOLDS` | 53 | dict | 4 |
| `STANDING_RANK` | 62 | dict | 4 |
| `STEADY` | 67 | str | 'Steady' |
| `UNWIELDY` | 68 | str | 'Unwieldy' |
| `TWO_H` | 69 | str | '2H' |
| `SHATTER_ARMOR` | 70 | str | 'Deadly' |
| `UNSTOPPABLE` | 71 | str | 'Unstoppable' |
| `CLEAVE` | 72 | str | 'Cleave' |
| `POISON` | 73 | str | 'Poison' |
| `NIMBLE` | 74 | str | 'Nimble' |
| `DRILLED` | 75 | str | 'Drilled' |
| `DESTROY_SHIELD` | 76 | str | 'Destroy Shield' |
| `BLUNDER` | 77 | str | 'Blunder' |
| `ONE_SHOT` | 78 | str | 'One-Shot' |
| `DEFLECT` | 79 | str | 'Deflect' |
| `IMMUNE_PANIC` | 80 | str | 'Immune Panic' |
| `UNBREAKABLE` | 81 | str | 'Unbreakable' |
| `PARRY` | 82 | str | 'Parry' |
| `RIPOSTE` | 83 | str | 'Riposte' |
| `NO_PARRY` | 84 | str | 'Awkward' |
| `RECOVER` | 85 | str | 'Recover' |
| `SERRATED` | 86 | str | 'Serrated' |
| `SERRATED_MOD` | 87 | int | 2 |
| `ENDURING` | 88 | str | 'Enduring' |
| `STRAIN` | 89 | str | 'Strained' |
| `MINUS_1_TBH` | 90 | str | 'Shielded' |
| `PLANISHING` | 91 | str | 'Planishing' |
| `FATIGUE_TOKEN` | 92 | str | 'Fatigue Token' |
| `CRUSADER` | 93 | str | 'Righteous Fervour' |
| `EXPOSED` | 96 | str | 'Exposed' |
| `EXPOSED_DOMAIN` | 97 | str | 'Cunning' |
| `EXPOSED_AUTH` | 98 | int | 1 |
| `IMMUNE` | 100 | str | 'Immune' |
| `immune` | 101 | function |  |
| `NEGATE` | 106 | str | 'Negate' |
| `negate` | 107 | function |  |
| `IMMUNE_DESTROY_SHIELD` | 113 | str | 'Immune Destroy Shield' |
| `IMMUNE_UNWIELDY` | 114 | str | 'Immune Unwieldy' |
| `IMMUNE_STRAIN` | 115 | str | 'Immune Strained' |
| `NEGATE_UNSTOPPABLE` | 117 | str | 'Immune Unstoppable' |
| `NEGATE_TEMPERED` | 119 | str | 'Negate Planishing' |
| `NEGATE_RIPOSTE` | 120 | str | 'Negate Riposte' |
| `NEGATE_SHIELDED` | 121 | str | 'Negate Shielded' |
| `MINUS_1_PARRY` | 122 | str | '-1 to Parry' |
| `HALFSWORD` | 123 | str | 'Halfsword' |
| `DUAL_WIELD` | 124 | str | 'Dual Wield' |
| `FLORENTINE` | 125 | str | 'Florentine' |
| `PIVOTAL` | 126 | str | 'Focused' |
| `GLOSSARY` | 129 | dict | 193 |
| `MORALE_GLOSSARY` | 262 | dict | 4 |
| `ARMY_MAX_RETINUES` | 288 | int | 25 |
| `FRONT_LINE_MAX` | 289 | int | 10 |
| `RESERVE_MAX` | 290 | int | 5 |
| `MORALE_DICE_MAX` | 291 | int | 5 |
| `PANIC_CASUALTY_THRESHOLD` | 292 | int | 5 |
| `ENDURANCE_REGAIN` | 293 | int | 2 |
| `RETINUES` | 297 | dict | 4 |
| `WEAPONS` | 304 | dict | 21 |
| `WEAPON_2H_PROFILES` | 336 | dict | 2 |
| `RANGED` | 338 | dict | 6 |
| `SHIELDS` | 348 | dict | 6 |
| `ARMORS` | 357 | dict | 6 |
| `TIERS` | 368 | list | 5 |
| `TIER_UNLOCK` | 369 | dict | 5 |
| `STANDING_EFFECTS` | 380 | dict | 6 |
| `TACTIC_MATRIX` | 405 | dict | 49 |
| `TACTICS` | 464 | list | 7 |
| `TACTIC_NOTES` | 466 | dict | 0 |
| `BATTLE_NARRATION` | 472 | dict | 19 |
| `CULTURE_SELF_MADE` | 515 | str | 'Self-made' |
| `CULTURES` | 517 | dict | 15 |
| `NODES` | 685 | dict | 147 |
| `DEPRECATED_NODES` | 1713 | dict | 3 |
| `HOLDING_GROUPS` | 1723 | dict | 9 |
| `SCOPES` | 1740 | tuple | 3 |
| `SCOPE_BY_TYPE` | 1741 | dict | 2 |
| `LINE_LABELS` | 1745 | dict | 31 |
| `lines_of` | 1779 | function |  |
| `REQ_KEY` | 1785 | str | 'infrastructure_req' |
| `REQ_LABEL` | 1786 | str | 'Infrastructure Req' |
| `TYPE_ORDER` | 1788 | list | 10 |
| `CHAIN_TERM` | 1790 | str | 'Mastery Chain' |
| `SHUTTER_TERM` | 1792 | str | 'Shuttered' |
| `UPKEEP_TERM` | 1796 | str | 'Upkeep' |
| `SUPPLY_TERM` | 1797 | str | 'Supply' |
| `PURSUIT_TERM` | 1799 | tuple | 2 |
| `node_parents` | 1801 | function |  |
| `get_data` | 1809 | function |  |
| `MONUMENT_SUMMARY` | 1818 | dict | 25 |
| `WONDER_SUMMARY` | 1848 | dict | 4 |
| `FACTIONS` | 1858 | dict | 38 |
| `DEPRECATED_FACTIONS` | 2358 | dict | 3 |
| `INFRASTRUCTURE` | 2368 | dict | 20 |
| `WONDERS` | 2494 | dict | 4 |
| `INFRA_TIERS` | 2495 | list | 5 |
| `SETTLEMENTS` | 2503 | dict | 5 |
| `PRESENCE_RANGE` | 2514 | int | 2 |
| `WARD_MODEL` | 2518 | str | 'range1' |
| `WARD_RULES` | 2519 | dict | 2 |
| `WARD_RULE` | 2527 | str | 'A Settlement Ward is a slot that holds  |
| `FAITH_FICKLE_PO` | 2529 | int | 0 |
| `ERAS` | 2532 | dict | 4 |
| `PO_BANDS` | 2552 | dict | 11 |
| `po_scale` | 2571 | function |  |
| `po_value` | 2578 | function |  |
| `po_effect` | 2583 | function |  |
| `PUBLIC_ORDER` | 2590 | dict | 11 |
| `PUBLIC_ORDER_BY_ERA` | 2591 | dict | 4 |
| `PO_MODIFIERS` | 2597 | dict | 2 |
| `DOMAIN_BOARD` | 2615 | dict | 6 |
| `SEASONS` | 2652 | dict | 4 |
| `TRADE_RULES` | 2661 | dict | 6 |
| `efficient_graph` | 2675 | function |  |
| `EFFICIENT_MULTI` | 2685 | dict | 139 |
| `EFFICIENT` | 2686 | dict | 139 |
| `BANDIT_CAMP_START` | 2694 | int | 10 |
| `BANDIT_CAMP_GOLD` | 2695 | int | 2000 |
| `BANDIT_ARMY_THRESHOLD` | 2696 | int | 25 |
| `BANDIT_GROWTH_PER_ERA` | 2697 | dict | 4 |
| `BANDIT_EQUIPMENT_PER_ERA` | 2698 | dict | 4 |
| `HARDCORE_BANDIT_EQUIPMENT_PER_ERA` | 2702 | dict | 4 |
| `HARDCORE_WILD_OUTLAW` | 2705 | dict | 9 |
| `BANDITS` | 2716 | dict | 5 |
| `TIMERS` | 2724 | dict | 8 |
| `CHARTER_MIN_RANGE` | 2736 | int | 4 |
| `OUTLAW_BUFFER_RANGE` | 2737 | int | 2 |
| `HAMLET_RANGE` | 2738 | int | 2 |
| `OUTLAW_COUNTRY_START` | 2739 | int | 3 |
| `WILD_OUTLAW` | 2747 | dict | 9 |
| `wild_outlaw_count` | 2760 | function |  |
| `BANDIT_CAMP_REACH` | 2767 | str | 'province' |
| `VASSAL_EXCHANGE_CAP` | 2770 | int | 5000 |
| `VASSAL_INFLUENCE_TAKE` | 2771 | int | 3 |
| `BUILD_TIMERS` | 2775 | dict | 11 |
| `PURSUIT_UPKEEP_DEFAULT` | 2790 | int | 100 |
| `HOLDING_TIER_COST` | 2792 | dict | 4 |
| `holding_standing` | 2800 | function |  |
| `holding_cost` | 2806 | function |  |
| `holding_build_time` | 2814 | function |  |
| `HOLDING_COST_TEXT` | 2820 | str | 'by Standing: Untested 100 (Build Timer  |
| `TERRAIN` | 2823 | dict | 7 |
| `MOVEMENT_MODIFIERS` | 2844 | dict | 6 |
| `TACTICAL_TERRAIN` | 2856 | dict | 7 |
| `TACTICAL_GLOBAL` | 2872 | list | 1 |
| `INFLUENCE_GAIN` | 2874 | dict | 9 |
| `ENVOY_OUTCOME_THRESHOLDS` | 2932 | dict | 4 |
| `CUNNING_EXTORT` | 2951 | int | 2000 |
| `CUNNING_EXTORT_ENDORSED` | 2952 | int | 2000 |
| `CUNNING_DOUBT` | 2953 | int | 1 |
| `ENVOY_OUTCOMES` | 2954 | dict | 5 |
| `ACTIONS` | 2977 | dict | 23 |
| `TREATIES` | 3179 | dict | 5 |
| `ALLIANCE_RULES` | 3187 | list | 3 |
| `EDICT_STREAK_TURNS` | 3197 | int | 5 |
| `GAME_TURN_LIMIT` | 3198 | int | 50 |
| `EDICT_UNIQUE` | 3201 | bool | False |
| `EDICT_UNIQUE_RULE` | 3202 | str | 'Each Domain, Monument, or Wonder counts |
| `IMPERIUM_REQUIREMENT` | 3208 | dict | 5 |
| `EDICTS` | 3215 | dict | 8 |
| `BANDIT_BEHAVIOR` | 3231 | dict | 9 |
| `PURSUIT_UPKEEP_BY_TYPE` | 3255 | dict | 4 |
| `UPKEEP_TRACKS` | 3265 | dict | 3 |
| `pursuit_upkeep` | 3272 | function |  |
| `ARMY_UPKEEP_NOTE` | 3283 | str | "Net Army Supply = the sum of each Army' |
| `COSTS` | 3287 | dict | 12 |
| `COUNCIL_DOMAIN` | 3310 | str | 'Industry' |
| `COUNCIL_DOMAIN_SPRING` | 3311 | str | 'Industry' |
| `ENVOY_PHASE_SPRING` | 3312 | str | 'Diplomacy' |
| `FORUM_DOMAIN` | 3313 | NoneType |  |
| `FORUM_ACTIONS` | 3314 | int | 1 |
| `PHASES` | 3315 | tuple | 5 |
| `STARTING_TURN_PHASE_OPENER` | 3316 | str | 'Works' |
| `STANDING_ARMY_SIEGE_MODIFIER` | 3318 | int | 1 |
| `EMPIRE_START_TIERS` | 3320 | tuple | 2 |
| `STARTING_TREASURY` | 3321 | int | 10000 |
| `SETUP_CAPITAL_PICKS` | 3324 | int | 2 |
| `SETUP_HAMLET_PICKS` | 3325 | int | 0 |
| `SETUP_HAMLET_HOLDINGS` | 3326 | tuple | 1 |
| `SETUP_HAMLET_TEXT` | 3327 | str | 'Common Land' |
| `HAMLET_REPEATABLE` | 3329 | tuple | 1 |
| `HAMLET_REPEATABLE_TEXT` | 3330 | str | 'Common Land' |
| `AGES` | 3336 | dict | 5 |
| `AGE_YEAR_SEASON` | 3343 | str | 'Spring' |
| `AGE_YEAR_ROLL_MEAN` | 3346 | float | 0.45 |
| `AGE_YEAR_ROLL_SD` | 3347 | float | 0.16666666666666666 |
| `CAPITAL_EDGE_RANGE` | 3348 | int | 4 |
| `BOARD_SIZES` | 3350 | dict | 3 |
| `SIEGE_CALCULUS` | 3356 | dict | 2 |
| `SIEGE_SOURCE_VALUES` | 3371 | dict | 3 |
| `PO_GLOSS_TERMS` | 3398 | list | 19 |
| `NAME_DISPLAY` | 3417 | dict | 74 |
| `TIER_DISPLAY` | 3454 | dict | 1 |
| `ITEM_TIER_DISPLAY` | 3460 | dict | 1 |
| `TERM_ENVOY_SCORE` | 3467 | str | 'Authority' |
| `display_score` | 3477 | function |  |
| `ALIASES` | 3487 | dict | 76 |
| `display` | 3497 | function |  |
| `display_tier` | 3502 | function |  |
| `display_text` | 3512 | function |  |
| `display_list` | 3535 | function |  |
| `display_md` | 3545 | function |  |
| `display_html` | 3552 | function |  |
| `display_obj` | 3564 | function |  |
| `undisplay` | 3577 | function |  |
| `verify_aliases` | 3586 | function |  |
| `BANDIT_FACES` | 3610 | int | 10 |
| `BANDIT_CUNNING_MIN` | 3611 | int | 10 |
| `die_table_ranges` | 3614 | function |  |
| `die_table_rows` | 3622 | function |  |
| `die_table_text` | 3630 | function |  |
| `die_table_lookup` | 3638 | function |  |
| `die_table_verify` | 3645 | function |  |
| `die_table_weights` | 3664 | function |  |
| `BANDIT_CUNNING_TABLE` | 3674 | dict | 4 |
| `bandit_cunning_ranges` | 3681 | function |  |
| `bandit_cunning_rows` | 3682 | function |  |
| `bandit_cunning_lookup` | 3683 | function |  |
| `bandit_cunning_text` | 3685 | function |  |
| `BANDIT_TACTIC_TABLE` | 3692 | dict | 6 |
| `BANDIT_TACTICS` | 3700 | list | 6 |
| `bandit_tactic_ranges` | 3702 | function |  |
| `bandit_tactic_rows` | 3703 | function |  |
| `bandit_tactic_lookup` | 3704 | function |  |
| `verify_bandit_tables` | 3707 | function |  |
| `RENOWN_MAX` | 3807 | int | 30 |
| `RENOWN_PER_TURN` | 3808 | int | 1 |
| `DOMAIN_POINTS_PER_TURN` | 3809 | int | 1 |
| `AI_DOMAIN_POINTS` | 3815 | str | 'Spend Domain Points one Standing at a t |
| `AI_PRIORITIES` | 3817 | list | 8 |
| `AI_FAITH_AVOID` | 3828 | list | 5 |
| `AI_STYLE` | 3851 | dict | 3 |
| `AI_ARCHETYPE` | 3874 | dict | 8 |
| `AI_PO_GOLD` | 3888 | int | 800 |
| `AI_MUSTER` | 3890 | dict | 3 |
| `AI_DIPLOMACY` | 3892 | dict | 4 |
| `FACTION_NAMES` | 3934 | dict | 38 |
| `FACTION_TERM` | 3942 | tuple | 2 |
| `faction_body` | 3948 | function |  |
| `GLOSSARY_CATEGORIES` | 3989 | list | 19 |
| `WIKI_NOLINK` | 4018 | list | 6 |
| `GLOSSARY_SEE` | 4027 | dict | 109 |
| `COND_UPKEEP_FACTOR` | 4073 | float | 0.5 |
| `holding_combat_tags` | 4083 | function |  |
| `holding_upkeep` | 4130 | function |  |
| `holding_domain` | 4143 | function |  |
| `HOLDING_SIM` | 4162 | dict | 147 |
| `AI_PROFILES` | 4174 | dict | 15 |

## 4. Build steps — `CE/build_all_CE.bat`

| Label | Line | Scripts | Echo |
|---|---|---|---|
| `:maps` | 235 | `build_mapapp.py` | --- Map generator app ---; skipped - build_mapapp.py not ported |
| `:cards` | 255 | `generate_cards.py` | --- Cards ---; skipped - generate_cards.py not ported |
| `:docs` | 270 | `md_to_docx.py`, `combat_sheet.py`, `spec_tree_sheet.py`, `playstyle_reference.py`, `pursuit_tiles.py`, `gen_layout.py`, `render_tree.py`, `svg_to_pdf.py`, `domain_board.py`, `infra_board.py`, `settlement_mats.py`, `gen_layout_roots.py`, `gen_settlement_board.py`, `faq_export.py`, `host_sheet.py` | --- Docs ---; Rules - with Holdings, Equipment, Factions, glossary, index...; Combat quick-reference sheet...; Specialization trees...; Playstyle reference...; Pursuit ward-tiles...; Pursuit tech tree |
| `:wiki` | 312 | `build_wiki.py` | --- Wiki ---; skipped - build_wiki.py not ported; skipped - wiki_markers.py not ported, build_wiki imports it; skipped - %RULES_MD% not found; Wiki build FAILED - skipping repo push.; Syncing into %WI |
| `:pushrepo` | 367 | `repo_map.py` | --- Push repo (v%VERSION%, DIE=%DIE%) -^> %REPO_DIR% ---; Git LFS not installed ^(https://git-lfs.com^) - skipping repo push so a; large file can't be committed without LFS. Install once, then re-run. |
| `:end` | 445 | — | Done. Press any key to close. |
| `:board` | 455 | `build_board.py` | --- Board ---; skipped - build_board.py not ported; Board -^> %BOARD_OUT% |
| `:tactical` | 474 | `build_board.py` | --- Tactical board ---; skipped - build_board.py not ported; Tactical board -^> %TAC_OUT% |
| `:lore` | 496 | `gen_cultures.py`, `gen_intro.py`, `gen_draft.py`, `gen_pdf.py`, `gen_book_json.py` | --- Lore (world documents from renown_worldlore.py) ---; skipped - %DIR_LORE%\gen_cultures.py not ported; Lore -^> %LORE_OUT% |

## 5. Rules markers — `CE/RULES_push_simple.md`

- **{{TABLE}}** (30): `edicts`, `eras`, `timers`, `seasons`, `ages`, `net_influence`, `envoy_outcomes`, `influence_gain`, `domain_board`, `treaties`, `settlements`, `infrastructure`, `build_timers`, `terrain`, `public_order`, `po_modifiers`, `trade_rules`, `retinues`, `tactic_matrix`, `siege_calculus`, `bandits_by_era`, `bandit_cunning`, `bandit_armaments_hardcore`, `bandit_tactics`, `holdings`, `weapons`, `ranged`, `shields`, `armor`, `factions`
- **{{GLOSSARY}}** (18): `Reading the Rules`, `Turn & Phases`, `Envoys & Voting`, `Actions`, `Domains & Scoring`, `Treaties`, `Settlements & Holdings`, `Map & Range`, `Economy & Public Order`, `Army States`, `Battle Structure`, `Combat Keywords — Defense`, `Combat Keywords — Offense`, `Combat Keywords — Handling`, `Combat Keywords — Immune / Negate`, `War`, `World`, `Equipment Tiers`
- **{{ACTIONS}}** (5): `Diplomacy`, `Prowess`, `Cunning`, `Piety`, `Industry`
- **{{LIST}}** (1): `ALLIANCE_RULES`
- **{{TERM}}** (1): `Speed X`
- **{{IDX}}** (32): `Era`, `Empire Phase`, `Works Phase`, `Envoy Phase`, `Council Phase`, `Diplomacy Phase`, `Battle Phase`, `Rest Phase`, `Intrigue Phase`, `Tally Phase`, `Season`, `Age`, `Standing Rank`, `Max Influence`, `Settlement`, `Hamlet`, `Infrastructure`, `Primitive`, `Developed`, `Sophisticated`, `Prodigious`, `Wondrous`, `Wonder`, `Treasury`, `Revenue`, `Trade Agreement`, `Army`, `Garrison`, `Lay Siege`, `Capture`, `Sack`, `Bandit Camp`
- **{{VAL}}** (92): `AGE_YEAR_SEASON`, `ARMY_MAX_RETINUES`, `BANDITS.Bandit Domain Value`, `BANDIT_ARMY_THRESHOLD`, `BANDIT_CAMP_GOLD`, `BANDIT_CAMP_START`, `BANDIT_CUNNING_MIN`, `BANDIT_FACES`, `BLUNDER_THR`, `CAPITAL_EDGE_RANGE`, `CAP_THR`, `CHAIN_TERM`, `COUNCIL_DOMAIN`, `DOMAIN_BOARD.innate_influence_own_envoys.Untested`, `DOMAIN_POINTS_PER_TURN`, `EDICT_UNIQUE_RULE`, `ENDURANCE_REGAIN`, `ERAS.Ascension.rank`, `ERAS.Eminence.diplomacy_agreements`, `ERAS.Eminence.rank`, `ERAS.Founding.diplomacy_agreements`, `ERAS.Founding.rank`, `ERAS.Founding.renown`, `ERAS.Zenith.rank`, `FACES`, `FAITH_FICKLE_PO`, `FATIGUE_MORALE`, `FOCUSED_THR`, `FRONT_LINE_MAX`, `GAME_TURN_LIMIT`, `HAMLET_RANGE`, `HARDCORE_WILD_OUTLAW.border_range`, `HARDCORE_WILD_OUTLAW.spacing`, `HOLDING_COST_TEXT`, `INFRASTRUCTURE.Cathedral.empire_bonus`, `INFRASTRUCTURE.Library.requirement`, `INFRASTRUCTURE.Magistrate's Hall.requirement`, `INITIATIVE_MAX`, `INITIATIVE_MIN`, `MORALE_DICE_MAX`, `OUTLAW_BUFFER_RANGE`, `OUTLAW_COUNTRY_START`, `PANIC_CASUALTY_THRESHOLD`, `PARRY_BASE`, `PO_MAX`, `PO_MIN`, `PRESENCE_RANGE`, `RENOWN_PER_TURN`, `RESERVE_MAX`, `RETINUES.Knight Templar.cost`, `RETINUES.Knight Templar.to_hit`, `RETINUES.Levy.cost`, `RETINUES.Levy.to_hit`, `RETINUES.Man-at-Arms.cost`, `RETINUES.Man-at-Arms.to_hit`, `RETINUES.Sergeant.cost`, `RETINUES.Sergeant.to_hit`, `ROUT_THR`, `SACK_EXTORT_PER_TIER`, `SETTLEMENTS.City.garrison`, `SETTLEMENTS.Hamlet.wards`, `SETTLEMENTS.Metropolis.garrison`, `SETTLEMENTS.Metropolis.reach`, `SETTLEMENTS.Town.garrison`, `SETTLEMENTS.Village.garrison`, `SETTLEMENTS.Village.reach`, `SETUP_CAPITAL_PICKS`, `SHUTTER_TERM`, `SIEGE_CALCULUS.Lay Siege.floor`, `STANDING_RANK.Established`, `STANDING_RANK.Rising`, `STANDING_RANK.Sovereign`, `STANDING_RANK.Untested`, `STANDING_THRESHOLDS.Established`, `STANDING_THRESHOLDS.Rising`, `STANDING_THRESHOLDS.Sovereign`, `STANDING_THRESHOLDS.Untested`, `STARTING_TREASURY`, `STARTING_TURN_PHASE_OPENER`, `SUPPLY_TERM`, `TIMERS.Capture Timer.default`, `TIMERS.Sack Timer.default`, `TRADE_RULES.income_per_craft`, `UPKEEP_TERM`, `VASSAL_EXCHANGE_CAP`, `VASSAL_INFLUENCE_TAKE`, `WARD_RULE`, `WEALTH_EDICT_GOLD`, `WILD_OUTLAW.border_range`, `WILD_OUTLAW.per_players`, `WILD_OUTLAW.plus`, `WILD_OUTLAW.spacing`
- **docx_tables.REGISTRY** (33): `ages`, `armor`, `bandit_armaments`, `bandit_armaments_hardcore`, `bandit_cunning`, `bandit_growth`, `bandit_tactics`, `bandits_by_era`, `build_timers`, `domain_board`, `edicts`, `envoy_outcomes`, `eras`, `factions`, `holdings`, `influence_gain`, `infrastructure`, `net_influence`, `po_modifiers`, `public_order`, `ranged`, `retinues`, `seasons`, `settlements`, `shields`, `siege_calculus`, `tactic_matrix`, `tactical_terrain`, `terrain`, `timers`, `trade_rules`, `treaties`, `weapons`

Headings:

| Line | Heading |
|---|---|
| 1 | # Renown |
| 6 | # Introduction |
| 10 | ### Game Synopsis |
| 30 | ### How to Win (Edicts) |
| 40 | ### Game Structure |
| 46 | # Core Rules |
| 48 | ## Reading These Rules |
| 64 | ## Core Principles |
| 111 | ## Resources |
| 121 | ## The Turn |
| 134 | ### Timers |
| 142 | ### Empire Phase |
| 162 | ### Envoy Phase |
| 177 | ### Diplomacy Phase |
| 182 | ### Battle Phase |
| 186 | ### Rest Phase |
| 195 | # Seasons |
| 201 | # Setup |
| 203 | ## Table Setup |
| 208 | ## Setup Order |
| 217 | ### Ages |
| 223 | ## Player Setup |
| 231 | # Actions & Voting |
| 233 | ## Action Mechanics |
| 235 | ### Sending an Envoy |
| 239 | ### Resolving an Envoy |
| 255 | ### Envoy Resolution Table |
| 271 | ## Influence |
| 279 | ## Diplomacy Actions |
| 288 | ## Prowess Actions |
| 292 | ### Rule: Commanding Presence |
| 296 | ## Cunning Actions |
| 300 | ## Piety Actions |
| 304 | ### Rule: Wavering Devotion |
| 308 | ## Industry Actions |
| 312 | ### Rule: Ulterior Motive |
| 320 | # Domains & Standings |
| 322 | ### Domain Standings |
| 328 | ### Standing Rank |
| 332 | ### Domain Identities & Traits |
| 338 | # Diplomacy & Treaties |
| 340 | ### Treaties & Alliances |
| 348 | ### Vassalization |
| 370 | # Empire Building |
| 372 | ## Settlements |
| 378 | ### Settlement Wards |
| 382 | ### Chartering Settlements |
| 386 | ### Settlement Reach |
| 390 | ### Hamlets |
| 396 | ## Infrastructure |
| 416 | ## Territory & Terrain |
| 430 | # Economy |
| 432 | ## Public Order |
| 444 | ### Innate Public Order Modifiers |
| 448 | ## Treasury & Upkeep |
| 458 | ### Insolvency & Bankruptcy |
| 471 | ## Trade & Income |
| 473 | ### Who Can Trade |
| 488 | ### Income Types |
| 496 | # Armies |
| 498 | ### Armies Overview |
| 504 | ### Garrisons |
| 508 | ### Mustering |
| 518 | ### Blocked Armies |
| 524 | # Battles & Sieges |
| 526 | ## Battle Phase |
| 530 | ### Beginning a Battle |
| 536 | ### The Skirmish Steps |
| 554 | ### Ending a Battle |
| 559 | ### Tactic Matrix |
| 573 | ## Siege Warfare |
| 578 | ### Siege Timer |
| 584 | ### Beginning a Siege |
| 594 | ### Resolving a Siege |
| 608 | # Bandits |
| 610 | ### Outlaw Country |
| 619 | ### Spawning Bandit Camps |
| 625 | ### Growing Bandit Camps |
| 631 | ### Bandit Rules |
| 647 | ### Bandit Army Behavior |
| 659 | ### Hardcore |
| 680 | ### Attacking a Bandit Camp |
| 690 | # Holdings |
| 696 | # Equipment |
| 698 | ## Melee Weapons |
| 702 | ## Ranged Weapons |
| 706 | ## Shields |
| 710 | ## Armor |
| 716 | # Factions |
| 720 | # Index |

## 6. Settlement board — `CE/references/gen_settlement_board.py` + `CE/references/board/js/*.js` (+ `board.css`, `body.html`)

Payload keys passed to the HTML as `DATA` (69): `records`, `naturalNames`, `externalTokens`, `simple`, `chainTerm`, `pursuitTerm`, `infra`, `wonders`, `armySrc`, `equip`, `glossary`, `domainBoard`, `publicOrder`, `domainBoardFx`, `poByEra`, `wikiBase`, `wikiHome`, `tree`, `rulebook`, `limits`, `eras`, `edicts`, `envoyOutcomes`, `outcomeThresh`, `startPhase`, `actions`, `phaseRules`, `phaseSteps`, `rulesConst`, `ages`, `domains`, `standings`, `tradePerCraft`, `noTradeSeason`, `tradeBorder`, `renownPerTurn`, `dpPerTurn`, `settlements`, `battle`, `terrainRef`, `banditLoadouts`, `banditLoadoutsHardcore`, `bandits`, `treaties`, `allianceRules`, `startTiers`, `startTreasury`, `pursuitUpkeep`, `buildTimers`, `infraTiers`, `timers`, `seasons`, `poModifiers`, `vassalInfluenceTake`, `aliases`, `scoreTerm`, `costs`, `influenceGain`, `siege`, `factions`, `cultures`, `monSummary`, `wonSummary`, `cultureSelf`, `placeNames`, `warnings`, `version`, `sprites`, `efx`

Python: `load`:27, `strip_md`:34, `has_cond`:78, `to_int`:81, `classify`:84, `_iv`:154, `envoy_fx`:155, `combine_parts`:277, `combine_effects`:318, `rules_payload`:322, `tree_payload`:381, `parse_effects`:415, `parse_mreq`:421, `classify_req_token`:429, `build`:438, `font_faces`:541, `_pursuit_term_template`:566, `render_html`:574, `_style_js`:582, `place_names_payload`:593, `sprite_payload`:614, `find_mapgen`:636, `_board_template`:651, `check_rules`:665, `_val`:793, `council_heading`:802, `rules_section`:806, `phase_steps`:825, `battle_data`:842, `bandit_loadouts`:864, `effects_report`:917, `main`:948

JS sections: TABLE: seating, Council & Envoy phases :10_table.js:1, Action automation: Perform picker + resolution :10_table.js:334, REALM: the play surface :15_realm.js:1, INTRIGUE & TALLY PHASES (RULES: Envoy Phase steps 3 and 5) :16_tally.js:1, DIPLOMACY STEP (PHASE_REFORM): offers between players :17_diplo_step.js:1,  :40_realm_data.js:279, Inspect tool :60_map.js:332, EFFECT PLUMBING: the effect registry (references/effect_registry.py) :70_rules.js:1, ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS :70_rules.js:65, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :70_rules.js:160, CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper :85_ux.js:1, WELCOME: seats + profile (server games) :86_welcome.js:1, UNDO / REDO :90_app.js:1, ACTIVITY LOG :90_app.js:43, GAME: save · load · new :90_app.js:102, HOVER KEYWORDS :90_app.js:153

JS functions (1231, name:file:line):

```
prof2h:00_core.js:10 fixBastard:00_core.js:11 dispScore:00_core.js:18 presR:00_core.js:36 presRof:00_core.js:38 POB:00_core.js:41 poNum:00_core.js:42 efxOf:00_core.js:53 hitOf:00_core.js:54 facHit:00_core.js:55 razeHoldings:10_table.js:12 razeTimerPlus:10_table.js:16 springDiplo:10_table.js:21 tnow:10_table.js:24 noteServerDate:10_table.js:25 gkey:10_table.js:31 lockOn:10_table.js:38 claimOf:10_table.js:39 mine:10_table.js:40 myClaimP:10_table.js:41 canEdit:10_table.js:42 boardEndOn:10_table.js:44 TB:10_table.js:45 seatFloor:10_table.js:47 tSeats:10_table.js:48 tTimer:10_table.js:49 tTurn:10_table.js:50 tBegun:10_table.js:51 tPhase:10_table.js:52 PT:10_table.js:54 tCur:10_table.js:55 tCurW:10_table.js:56 sameP:10_table.js:57 meP:10_table.js:58 canAct:10_table.js:59 seatMap:10_table.js:62 seated:10_table.js:66 isSpring:10_table.js:67 councilDomNow:10_table.js:69 councilOff:10_table.js:70 hostP:10_table.js:71 voteOrd:10_table.js:74 tOrder:10_table.js:75 canHost:10_table.js:76 seatsLocked:10_table.js:77 tStand:10_table.js:80 eraRec:10_table.js:81 diploInf:10_table.js:82 diploCap:10_table.js:83 eraActions:10_table.js:84 envActions:10_table.js:88 envSlots:10_table.js:89 endorsedBonus:10_table.js:95 slotLabel:10_table.js:99 slotOpen:10_table.js:100 withSlots:10_table.js:101 boardFx:10_table.js:104 fxOf:10_table.js:117 inProvinceOf:10_table.js:119 provFx:10_table.js:121 supCut:10_table.js:123 scopeOk:10_table.js:125 sgn:10_table.js:126 fxLabel:10_table.js:127 atWarPair:10_table.js:146 opposeBlock:10_table.js:147 domAsFx:10_table.js:154 innateParts:10_table.js:155 modSum:10_table.js:161 innateInf:10_table.js:163 voteCap:10_table.js:164 inflPool:10_table.js:167 personalEnvoys:10_table.js:168 councilEnvoys:10_table.js:169 tOutcome:10_table.js:170 outText:10_table.js:172 tPlan:10_table.js:175 missionWhy:10_table.js:193 domStarted:10_table.js:196 whisperEligibleEnvoys:10_table.js:197 tSim:10_table.js:200 performEval:10_table.js:291 comboEval:10_table.js:297 failPassFx:10_table.js:309 condFailFx:10_table.js:310 inviteHolders:10_table.js:315 inviteOf:10_table.js:320 actionsOf:10_table.js:321 actReqFlag:10_table.js:323 actInfoHTML:10_table.js:327 actCost:10_table.js:338 domCost:10_table.js:340 addFaith:10_table.js:341 alliedP:10_table.js:342 allyGroup:10_table.js:343 topPair:10_table.js:344 actDoubt:10_table.js:347 musterOpts:10_table.js:417 runMuster:10_table.js:424 buildOpts:10_table.js:440 buildPlaces:10_table.js:449 runBuild:10_table.js:453 improveOpts:10_table.js:459 expandOpts:10_table.js:465 runExpand:10_table.js:469 runImprove:10_table.js:473 runSettle:10_table.js:479 repairOpts:10_table.js:484 runRepair:10_table.js:487 settName:10_table.js:493 warOnFac:10_table.js:496 warOn:10_table.js:500 grandVizier:10_table.js:504 pfSpec:10_table.js:507 pfHardFlags:10_table.js:508 pfTargets:10_table.js:522 pfSubs:10_table.js:534 pfSubLabel:10_table.js:535 evTxt:10_table.js:537 insteadFx:10_table.js:542 actDom:10_table.js:543 pfActs:10_table.js:544 pfInsteadSrc:10_table.js:546 pfForm:10_table.js:547 boardCounts:10_table.js:582 pendingOf:10_table.js:584 apLines:10_table.js:586 resolveEnvoy:10_table.js:589 campTgt:10_table.js:652 campExtort:10_table.js:653 autoRes:10_table.js:654 tApply:10_table.js:655 recAct:10_table.js:667 actTgtName:10_table.js:669 allActs:10_table.js:670 actsAt:10_table.js:675 actLine:10_table.js:676 realmActsHTML:10_table.js:677 tNext:10_table.js:684 tSetPhase:10_table.js:685 tRestartPhase:10_table.js:688 tAdd30:10_table.js:693 grantDP:10_table.js:696 dpOwed:10_table.js:697 tEndTurn:10_table.js:698 setSeats:10_table.js:718 tAutoSeat:10_table.js:723 tSig:10_table.js:729 tName:10_table.js:732 tVoteTxt:10_table.js:733 envBadges:10_table.js:734 innateTxt:10_table.js:740 tOutCls:10_table.js:742 tPerformHtml:10_table.js:743 summaryLines:10_table.js:765 chronOn:10_table.js:782 chron:10_table.js:783 chronSnap:10_table.js:786 chronTick:10_table.js:793 chronDate:10_table.js:803 empireChecklistHTML:10_table.js:804 treeSave:10_table.js:814 mapRaws:10_table.js:825 refRawAvail:10_table.js:828 refCulture:10_table.js:834 refAvail:10_table.js:835 treeHTML:10_table.js:837 infraTreeHTML:10_table.js:914 rulebookHTML:10_table.js:945 linkifyRules:10_table.js:948 renderReference:10_table.js:952 tCountdown:10_table.js:967 applyTheme:10_table.js:982 applySkin:10_table.js:994 doFire:15_realm.js:8 patch:15_realm.js:12 rlCommit:15_realm.js:13 pOf:15_realm.js:14 standingPhaseActions:15_realm.js:15 holdingEpActions:15_realm.js:20 eurekaKey:15_realm.js:24 eurekaAction:15_realm.js:25 activeCipherTimers:15_realm.js:30 cipherTimerResolve:15_realm.js:36 empWin:15_realm.js:42 empireHoldingHTML:15_realm.js:43 whisperGateHTML:15_realm.js:67 forgeRetryHTML:15_realm.js:71 courierDeferHTML:15_realm.js:75 rlOpen:15_realm.js:128 rlToggle:15_realm.js:129 renderTable:15_realm.js:134 seasonPlateHTML:15_realm.js:155 seasonDock:15_realm.js:159 seasonHerald:15_realm.js:168 renderRealmMap:15_realm.js:174 domCells:15_realm.js:186 realmTableHTML:15_realm.js:192 spectating:15_realm.js:234 miniCardHTML:15_realm.js:246 phaseCardHTML:15_realm.js:256 dockCard:15_realm.js:309 dockHTML:15_realm.js:310 envoyQueueHTML:15_realm.js:384 inflPaneHTML:15_realm.js:406 inflCardHTML:15_realm.js:418 declInviteHTML:15_realm.js:438 drawersHTML:15_realm.js:477 turnLogItems:15_realm.js:489 turnLogHTML:15_realm.js:509 realmTimersBrief:15_realm.js:518 tallyVoter:16_tally.js:7 standingHit:16_tally.js:9 tallySupportOf:16_tally.js:10 tallyEndorseOf:16_tally.js:11 resolveOpen:16_tally.js:13 intrigueKinds:16_tally.js:15 intrigueSilenced:16_tally.js:24 whisperPending:16_tally.js:25 intrigueRun:16_tally.js:27 tallyRun:16_tally.js:38 envLabel:16_tally.js:61 tsId:16_tally.js:62 tRow:16_tally.js:63 envSel:16_tally.js:64 amtSel:16_tally.js:65 intrigueHTML:16_tally.js:66 tallyHTML:16_tally.js:94 inTurn:16_tally.js:109 selVal:16_tally.js:110 tallyTurn:16_tally.js:125 dsOn:17_diplo_step.js:7 dsKey:17_diplo_step.js:8 DS:17_diplo_step.js:9 dsCap:17_diplo_step.js:10 dsWho:17_diplo_step.js:11 dsAgreed:17_diplo_step.js:12 dsUsed:17_diplo_step.js:13 dsPartner:17_diplo_step.js:14 dsDone:17_diplo_step.js:15 dsAllDone:17_diplo_step.js:16 dsTypes:17_diplo_step.js:18 dsFlag:17_diplo_step.js:22 dsSnap:17_diplo_step.js:24 dsRestore:17_diplo_step.js:27 dsCourt:17_diplo_step.js:31 dsCourtRefund:17_diplo_step.js:34 dsEmb:17_diplo_step.js:37 dsFailable:17_diplo_step.js:38 dsEmbDue:17_diplo_step.js:40 dsFail:17_diplo_step.js:41 applyTreaty:17_diplo_step.js:45 dsEnds:17_diplo_step.js:53 dsClose:17_diplo_step.js:57 dsLog:17_diplo_step.js:58 dsOffer:17_diplo_step.js:59 dsAccept:17_diplo_step.js:61 dsEnd:17_diplo_step.js:65 dsEmbHTML:17_diplo_step.js:72 diploStepHTML:17_diplo_step.js:78 aiDiploStep:17_diplo_step.js:116 startDoms:20_state.js:2 ageRec:20_state.js:5 ageRisingOf:20_state.js:6 startDomsFor:20_state.js:7 startDomTotal:20_state.js:8 curYear:20_state.js:9 rollAgeYear:20_state.js:11 applyAgeStart:20_state.js:14 startSettlements:20_state.js:16 startSig:20_state.js:19 reseedIfPristine:20_state.js:21 newBoard:20_state.js:26 newPlayer:20_state.js:28 normalizeD:20_state.js:44 dedupeIds:20_state.js:70 activeBoard:20_state.js:72 reindex:20_state.js:73 pActive:20_state.js:86 dmgMark:20_state.js:88 dmgSrc:20_state.js:89 dmgSrcOf:20_state.js:90 chainOK:20_state.js:92 ignHas:20_state.js:96 flagState:20_state.js:97 ignBtn:20_state.js:102 ignNote:20_state.js:105 unlockStatus:20_state.js:111 nameHit:20_state.js:122 missTxt:20_state.js:123 recomputePC:20_state.js:125 buildTimerMod:20_state.js:130 timerMod:20_state.js:131 withBuildMod:20_state.js:135 pursuitBaseTime:20_state.js:136 infraBaseTime:20_state.js:137 repairTime:20_state.js:139 pursuitBuildTime:20_state.js:140 infraBuildTime:20_state.js:141 buildNote:20_state.js:142 settBaseTime:20_state.js:143 settBuildTime:20_state.js:144 itm:20_state.js:145 infraOn:20_state.js:146 shutToggle:20_state.js:149 shutUpkeep:20_state.js:153 checkinAct:20_state.js:159 gameStarted:20_state.js:160 glogTurn:20_state.js:164 glogSea:20_state.js:165 glogPush:20_state.js:166 glogSync:20_state.js:170 insolvent:20_state.js:173 tGold:20_state.js:175 boardOwnerName:20_state.js:180 empTimers:20_state.js:184 empEconomy:20_state.js:185 empPO:20_state.js:194 immuneStrainIn:20_state.js:206 siegeStrains:20_state.js:210 endMax:20_state.js:212 capEnd:20_state.js:213 effStrained:20_state.js:214 empArmies:20_state.js:215 endRow:20_state.js:222 boardEndTurn:20_state.js:225 stepRealmTimer:20_state.js:229 siegeFatigue:20_state.js:231 tickRealm:20_state.js:235 expireBlocks:20_state.js:239 expireBlocksTimed:20_state.js:240 empirePhase:20_state.js:243 tickTimers:20_state.js:270 facTypeBonus:20_state.js:279 pursuitUpkeep:20_state.js:282 withBoard:20_state.js:285 setOnline:20_state.js:301 clone:20_state.js:311 jeq:20_state.js:312 isObj:20_state.js:313 merge3:20_state.js:315 splitD:20_state.js:324 joinD:20_state.js:330 save:20_state.js:356 saveIfDirty:20_state.js:364 editing:20_state.js:399 cvar:20_state.js:419 fmt:20_state.js:420 cap:20_state.js:421 settUnbuilt:20_state.js:425 unbuiltMeta:20_state.js:426 settMeta:20_state.js:427 pinSettCell:20_state.js:428 settExpand:20_state.js:429 settFinish:20_state.js:430 settTier:20_state.js:433 occupants:20_state.js:434 hamletOK:20_state.js:435 hamletRoot:20_state.js:438 hamletFits:20_state.js:439 effList:20_state.js:448 effLabel:20_state.js:453 exemptionsOf:20_state.js:454 wardExemptions:20_state.js:463 isFreeRider:20_state.js:464 wardUse:20_state.js:465 canPlace:20_state.js:476 hamletRepeat:20_state.js:494 setupRawOK:20_state.js:497 setupHoldFlags:20_state.js:498 capitalSett:20_state.js:511 setCapital:20_state.js:512 isCityPlus:20_state.js:514 dbActive:20_state.js:515 standingKey:20_state.js:521 armStanding:20_state.js:522 capBonus:20_state.js:527 eraCapBase:20_state.js:528 eraCap:20_state.js:529 capSrc:20_state.js:530 cityCount:20_state.js:531 eraAllows:20_state.js:533 rslug:20_state.js:541 boardFlags:20_state.js:542 onBoard:20_state.js:579 scopeOf:20_state.js:581 realmHolder:20_state.js:582 wonderRacing:20_state.js:584 wonderBuilding:20_state.js:586 wonderStart:20_state.js:587 wonderRace:20_state.js:590 scopeBlock:20_state.js:600 nextTier:20_state.js:605 autoFill:20_state.js:607 buildFilters:30_empire.js:8 monChip:30_empire.js:10 catSave:30_empire.js:17 catMode:30_empire.js:19 catAvail:30_empire.js:20 catSeg:30_empire.js:21 catCulKeep:30_empire.js:22 catGroups:30_empire.js:39 catRows:30_empire.js:41 pAvail:30_empire.js:45 legalCtx:30_empire.js:49 rawRes:30_empire.js:51 rawInSett:30_empire.js:52 rawOK:30_empire.js:56 pLegal:30_empire.js:57 pReqMiss:30_empire.js:63 autoHamlet:30_empire.js:66 autoOK:30_empire.js:67 effSpot:30_empire.js:69 facRide:30_empire.js:76 smartSid:30_empire.js:77 iAvail:30_empire.js:84 catUpkeep:30_empire.js:85 seg:30_empire.js:86 renderList:30_empire.js:88 wardPick:30_empire.js:143 wpRender:30_empire.js:145 wpPlace:30_empire.js:168 settLbl:30_empire.js:173 reqRow:30_empire.js:175 pursuitRow:30_empire.js:177 sub:30_empire.js:188 tip:30_empire.js:190 itemRow:30_empire.js:191 flash:30_empire.js:201 addInfraByName:30_empire.js:203 placeHolding:30_empire.js:210 addItem:30_empire.js:231 removeInstance:30_empire.js:242 addPursuitByName:30_empire.js:243 moveInstance:30_empire.js:244 infraReqToks:30_empire.js:260 infraTokStatus:30_empire.js:266 infraReqStatus:30_empire.js:280 infraValid:30_empire.js:285 infraActive:30_empire.js:292 infraReqLinesHTML:30_empire.js:293 masteryInfraToks:30_empire.js:297 masteryInfraHTML:30_empire.js:298 annotReqTok:30_empire.js:305 optionMet:30_empire.js:310 reqStatus:30_empire.js:318 instStatus:30_empire.js:325 chainLine:30_empire.js:332 simpleReq:30_empire.js:341 simpleReqHTML:30_empire.js:353 computeEarned:30_empire.js:361 atomEl:30_empire.js:379 FX_CHIP_TEST:30_empire.js:392 fxParts:30_empire.js:393 effectView:30_empire.js:395 atomsBlock:30_empire.js:406 render:30_empire.js:419 renderTopBar:30_empire.js:479 toggleEmpty:30_empire.js:526 sfxNorm:30_empire.js:535 sfxLabel:30_empire.js:536 settFx:30_empire.js:545 settFxPanel:30_empire.js:568 renderPursuitBoard:30_empire.js:575 wardPiles:30_empire.js:684 wardGrid:30_empire.js:696 unitFor:30_empire.js:723 tryMove:30_empire.js:728 scrollHost:30_empire.js:762 dropTargetAt:30_empire.js:763 clearDropHL:30_empire.js:771 armDrag:30_empire.js:772 beginDrag:30_empire.js:789 dragMove:30_empire.js:803 dragEnd:30_empire.js:815 herPicker:30_empire.js:824 factionFree:30_empire.js:835 setFaction:30_empire.js:839 facGearFlags:30_empire.js:848 armyTokHolder:30_empire.js:855 armyTokNamed:30_empire.js:856 factionFlags:30_empire.js:857 cultureFactions:30_empire.js:874 facOffered:30_empire.js:881 facPicker:30_empire.js:883 culSelectHTML:30_empire.js:900 domStripe:30_empire.js:906 cultureOf:30_empire.js:908 holdDom:30_empire.js:909 cultureSet:30_empire.js:913 cultureKeep:30_empire.js:918 cultureInfra:30_empire.js:921 derivedCulture:30_empire.js:926 nameCulture:30_empire.js:928 usedSettNames:30_empire.js:930 genPlaceName:30_empire.js:931 nameSett:30_empire.js:937 nameAllSetts:30_empire.js:939 renderFaction:30_empire.js:940 dukeCtl:30_empire.js:950 timerCtl:30_empire.js:951 placementSelect:30_empire.js:957 contribAcc:30_empire.js:972 contribChips:30_empire.js:975 accChips:30_empire.js:976 pursuitDetail:30_empire.js:984 quickChip:30_empire.js:1008 buildsIntoRow:30_empire.js:1012 nextLinksHTML:30_empire.js:1014 pursuitTable:30_empire.js:1022 pursuitCard:30_empire.js:1049 renderInfraSection:30_empire.js:1142 armyUnlocks:30_empire.js:1189 unlockedShieldTiers:30_empire.js:1222 tierOK:30_empire.js:1226 gloss:30_empire.js:1227 glossLookup:30_empire.js:1236 openModal:30_empire.js:1245 closeModal:30_empire.js:1249 kwChipHTML:30_empire.js:1250 esc:30_empire.js:1251 inspectKeyword:30_empire.js:1252 inspectItem:30_empire.js:1274 optionList:30_empire.js:1297 loadoutFields:30_empire.js:1313 canDualWield:30_empire.js:1328 weaponForbids:30_empire.js:1330 fixWeaponNotes:30_empire.js:1332 renderArmy:30_empire.js:1335 armyCard:30_empire.js:1368 reqMet:30_empire.js:1462 lanceOnlyOK:30_empire.js:1466 weaponUnlockMet:30_empire.js:1467 moraleBase:30_empire.js:1469 armyUpkeep:30_empire.js:1470 moraleCap:30_empire.js:1472 moraleStanding:30_empire.js:1475 moralePO:30_empire.js:1478 effMorale:30_empire.js:1480 isRouted:30_empire.js:1481 armyVals:30_empire.js:1484 armyStats:30_empire.js:1492 noUpkeepTiers:30_empire.js:1519 holdsActive:30_empire.js:1521 playersWithout:30_empire.js:1523 calcMetrics:30_empire.js:1525 computeTotals:30_empire.js:1586 poTaxMod:30_empire.js:1617 taxDouble:30_empire.js:1622 winterTax:30_empire.js:1623 occupyTaxOnly:30_empire.js:1632 settInside:30_empire.js:1633 settTax:30_empire.js:1634 tradeIncome:30_empire.js:1637 tradeRaw:30_empire.js:1646 goldBreak:30_empire.js:1660 treasLive:30_empire.js:1674 fmtK:30_empire.js:1676 renderGlog:30_empire.js:1678 goldBreakHTML:30_empire.js:1685 goldBreakTxt:30_empire.js:1689 seasonNet:30_empire.js:1690 husbandryGoldFor:30_empire.js:1694 SEASON_DBL_TIER:30_empire.js:1698 tierGoldFor:30_empire.js:1700 seasonDblGold:30_empire.js:1704 SEASON_DBL_TYPE:30_empire.js:1705 boardMetrics:30_empire.js:1706 poCurKey:30_empire.js:1714 poBandName:30_empire.js:1715 poActiveKeys:30_empire.js:1717 poActiveEffects:30_empire.js:1719 poImmune:30_empire.js:1726 poDoubled:30_empire.js:1727 renderPO:30_empire.js:1729 planSave:35_plan.js:7 planKey:35_plan.js:8 planOf:35_plan.js:9 planSet:35_plan.js:10 planToggle:35_plan.js:11 planMove:35_plan.js:12 rawWhere:35_plan.js:14 planHStep:35_plan.js:17 planIStep:35_plan.js:29 planHPath:35_plan.js:39 planIPath:35_plan.js:48 planCtx:35_plan.js:49 planGoal:35_plan.js:51 planGoals:35_plan.js:60 planSteps:35_plan.js:62 planSort:35_plan.js:63 planAdd:35_plan.js:66 planPanel:35_plan.js:69 planPickHTML:35_plan.js:97 planMarks:35_plan.js:98 planCls:35_plan.js:99 curSeason:40_realm_data.js:4 stepSeason:40_realm_data.js:5 nextSeason:40_realm_data.js:6 seaLook:40_realm_data.js:9 seaLine:40_realm_data.js:11 playerOfBoard:40_realm_data.js:14 igVal:40_realm_data.js:15 eraIdx:40_realm_data.js:16 playerAtWar:40_realm_data.js:17 influenceRowsBase:40_realm_data.js:18 influenceRows:40_realm_data.js:49 influenceTotal:40_realm_data.js:54 poModRows:40_realm_data.js:58 totTipSimple:40_realm_data.js:86 totTip:40_realm_data.js:89 epSources:40_realm_data.js:100 topSuz:40_realm_data.js:113 royalMarriage:40_realm_data.js:116 sameAlliance:40_realm_data.js:121 poFloor:40_realm_data.js:124 applyPOFloor:40_realm_data.js:125 epRows:40_realm_data.js:126 poModTotal:40_realm_data.js:139 dpButtons:40_realm_data.js:140 renderDP:40_realm_data.js:143 dpSpend:40_realm_data.js:146 renderMiniStand:40_realm_data.js:153 renderInfluence:40_realm_data.js:167 renderPOMods:40_realm_data.js:171 siegeState:40_realm_data.js:183 siegeCalc:40_realm_data.js:184 siegeHTML:40_realm_data.js:202 realmTimers:40_realm_data.js:217 timerAddHTML:40_realm_data.js:218 boardTimerRows:40_realm_data.js:222 siegeResolveHTML:40_realm_data.js:228 activeTimersHTML:40_realm_data.js:235 seasonsHTML:40_realm_data.js:241 costsHTML:40_realm_data.js:244 wireDashExtras:40_realm_data.js:247 renderDash:40_realm_data.js:275 domBand:40_realm_data.js:278 mods:40_realm_data.js:281 diplo:40_realm_data.js:286 pk:40_realm_data.js:287 isVassal:40_realm_data.js:289 vassalsOf:40_realm_data.js:290 effPair:40_realm_data.js:291 pairOf:40_realm_data.js:294 pname:40_realm_data.js:295 allianceLabel:40_realm_data.js:296 pboard:40_realm_data.js:297 hasRoad:40_realm_data.js:299 eraRank:40_realm_data.js:302 allianceEra:40_realm_data.js:303 allianceOK:40_realm_data.js:304 pairFlags:40_realm_data.js:305 dStatus:40_realm_data.js:313 diploHTML:40_realm_data.js:317 wireDiplo:40_realm_data.js:374 newSide:50_battle.js:4 battle:50_battle.js:5 bq:50_battle.js:7 bqAdd:50_battle.js:8 bqSideName:50_battle.js:9 bqLoad:50_battle.js:12 sideHex:50_battle.js:15 bqStart:50_battle.js:19 hardcore:50_battle.js:23 banLO:50_battle.js:24 banEquip:50_battle.js:25 banWild:50_battle.js:26 banditArmy:50_battle.js:27 banditEra:50_battle.js:32 armBandits:50_battle.js:33 sideArmy:50_battle.js:40 blog:50_battle.js:45 d10:50_battle.js:46 seizeForced:50_battle.js:47 facCombat:50_battle.js:50 apMod:50_battle.js:63 sideUnlocks:50_battle.js:64 sideDomains:50_battle.js:69 standingFxOf:50_battle.js:70 hasArmyTok:50_battle.js:75 eqOptions:50_battle.js:76 eqCode:50_battle.js:87 eqNow:50_battle.js:90 dualOn:50_battle.js:94 eqWeapon:50_battle.js:95 tacAllowed:50_battle.js:104 tacTooEarly:50_battle.js:111 tacOK:50_battle.js:112 tacWhyNot:50_battle.js:113 randomTacticPool:50_battle.js:114 sideCalc:50_battle.js:117 pickKey:50_battle.js:270 viewerSide:50_battle.js:271 banditRollTactic:50_battle.js:287 mdLite:50_battle.js:301 fmtModLong:50_battle.js:303 fmtMod:50_battle.js:306 dieRow:50_battle.js:311 rollNeed:50_battle.js:313 rollHTML:50_battle.js:314 battleSprites:50_battle.js:321 datasheetHTML:50_battle.js:328 tacticPickHTML:50_battle.js:385 whatIf:50_battle.js:418 woundChance:50_battle.js:424 tacPair:50_battle.js:431 cellMotifs:50_battle.js:440 tacCells:50_battle.js:445 tacCardBody:50_battle.js:446 tacDetailHTML:50_battle.js:461 rollGuideHTML:50_battle.js:474 narrPl:50_battle.js:506 narrDisp:50_battle.js:507 narrate:50_battle.js:508 rollMeta:50_battle.js:514 chronicleHTML:50_battle.js:526 sideHTML:50_battle.js:529 fatigueImmune:50_battle.js:550 fatiguesNow:50_battle.js:552 sideNm:50_battle.js:554 bFlow:50_battle.js:559 actionsHTML:50_battle.js:599 battleOwed:50_battle.js:630 battleOutcome:50_battle.js:636 resultHTML:50_battle.js:643 sideTile:50_battle.js:661 onHill:50_battle.js:662 onGrass:50_battle.js:663 seizeDefault:50_battle.js:665 seizeHTML:50_battle.js:666 bCmdHTML:50_battle.js:673 tacEdge:50_battle.js:680 tacticExplainHTML:50_battle.js:686 battleRulesHTML:50_battle.js:700 renderBattle:50_battle.js:704 incoming:50_battle.js:734 roll:50_battle.js:737 autoApplyCas:50_battle.js:813 cleaveN:50_battle.js:816 addCleave:50_battle.js:817 ripN:50_battle.js:818 addRip:50_battle.js:819 setPendCas:50_battle.js:821 pendCas:50_battle.js:822 ripCasN:50_battle.js:824 applyCasNow:50_battle.js:825 applyCas:50_battle.js:827 rollBreak:50_battle.js:829 rollBreakBtn:50_battle.js:832 panicOwed:50_battle.js:835 endSkirmish:50_battle.js:838 endBattle:50_battle.js:860 wireBattle:50_battle.js:905 edictTimerLen:50_battle.js:965 edictChoices:50_battle.js:967 edictTotal:50_battle.js:973 edictOwners:50_battle.js:974 bumpRenown:50_battle.js:975 edictCond:50_battle.js:982 edictPlayersPct:50_battle.js:989 uncontestedCount:50_battle.js:993 edictHeld:50_battle.js:995 edictPend:50_battle.js:1000 edictIsPending:50_battle.js:1001 edictDone:50_battle.js:1003 edictClosed:50_battle.js:1004 edictTick:50_battle.js:1006 edictTaken:50_battle.js:1013 edictWatch:50_battle.js:1014 checkEdicts:50_battle.js:1018 edictNewsText:50_battle.js:1026 edictBoardHTML:50_battle.js:1027 wireEdicts:50_battle.js:1056 currentEra:50_battle.js:1070 pMark:50_battle.js:1078 domTrackHTML:50_battle.js:1080 standingEffectsHTML:50_battle.js:1089 renderRenown:50_battle.js:1102 bfLine:52_battlefield.js:9 bfForm:52_battlefield.js:12 bfXY:52_battlefield.js:20 bfPlace:52_battlefield.js:23 bfTerrain:52_battlefield.js:34 bfSideInfo:52_battlefield.js:38 bfFigure:52_battlefield.js:49 bfGround:52_battlefield.js:53 bfCamp:52_battlefield.js:58 bfBuild:52_battlefield.js:62 bfMount:52_battlefield.js:74 bfUpdate:52_battlefield.js:80 bfGear:52_battlefield.js:109 bfFeedPaint:52_battlefield.js:116 bfToast:52_battlefield.js:120 bfDefLine:52_battlefield.js:126 bfReport:52_battlefield.js:133 bfSeen:52_battlefield.js:142 bfFx:52_battlefield.js:144 bfPick:52_battlefield.js:145 bfEffects:52_battlefield.js:154 aiOn:55_ai.js:6 aiProfile:55_ai.js:7 aiDriver:55_ai.js:9 aiNote:55_ai.js:10 aiCashOutlook:55_ai.js:15 aiMem:55_ai.js:20 aiRel:55_ai.js:21 aiRelAdd:55_ai.js:22 aiLearn:55_ai.js:24 aiStandSteps:55_ai.js:35 aiNextMonument:55_ai.js:41 aiStandGoals:55_ai.js:44 aiPickDomain:55_ai.js:57 aiSpendDP:55_ai.js:63 aiCouncilPick:55_ai.js:66 aiEraAllows:55_ai.js:78 aiFoe:55_ai.js:80 aiFriend:55_ai.js:82 aiHoldNet:55_ai.js:84 aiHoldPO:55_ai.js:87 aiHoldValue:55_ai.js:88 aiFaithFloor:55_ai.js:90 aiBuildPick:55_ai.js:91 aiImprovePick:55_ai.js:96 aiTreatyType:55_ai.js:101 aiTreatyAccept:55_ai.js:110 aiApplyTreaty:55_ai.js:121 aiOffensive:55_ai.js:131 aiKit:55_ai.js:132 aiGearRank:55_ai.js:143 aiOutfit:55_ai.js:149 aiMoveTargets:55_ai.js:161 aiMovable:55_ai.js:163 aiEngageSize:55_ai.js:168 aiMove:55_ai.js:170 aiPrioW:55_ai.js:199 aiScore:55_ai.js:200 aiSurvival:55_ai.js:203 aiPassChance:55_ai.js:210 aiArch:55_ai.js:218 aiStyle:55_ai.js:222 aiGearGain:55_ai.js:224 aiHoldTags:55_ai.js:231 aiActTags:55_ai.js:245 aiFaithNeed:55_ai.js:262 aiBanditThreat:55_ai.js:271 aiBanditNear:55_ai.js:278 aiSit:55_ai.js:281 aiCandidates:55_ai.js:291 aiIntents:55_ai.js:386 aiDeclare:55_ai.js:395 aiPlanFor:55_ai.js:401 aiPerform:55_ai.js:403 aiVoteWant:55_ai.js:422 aiVoteAll:55_ai.js:435 aiTacticEval:55_ai.js:448 aiTacticU:55_ai.js:454 aiTacticStance:55_ai.js:460 aiPickTactic:55_ai.js:466 aiBattleTick:55_ai.js:476 aiTick:55_ai.js:482 aiAfterRender:55_ai.js:498 mapClimate:60_map.js:17 mapPal:60_map.js:22 seaProfile:60_map.js:56 seaPropLook:60_map.js:58 tShift:60_map.js:63 seasonPal:60_map.js:71 tLum:60_map.js:74 tTone:60_map.js:76 tLighten:60_map.js:77 tGlyph:60_map.js:80 tSwatch:60_map.js:85 mapState:60_map.js:92 hexDist:60_map.js:93 decodeGrid:60_map.js:96 seedCode:60_map.js:106 generateMap:60_map.js:107 parseSeedCode:60_map.js:115 mapZoom:60_map.js:127 reachBonus:60_map.js:133 reachOwners:60_map.js:142 resShown:60_map.js:156 nodesMode:60_map.js:157 reachResources:60_map.js:159 settReachHexes:60_map.js:169 rawClaims:60_map.js:180 mapSprId:60_map.js:202 mapSprDefs:60_map.js:203 tMix:60_map.js:213 hStr:60_map.js:218 rng32:60_map.js:219 mapScatter:60_map.js:220 propPaths:60_map.js:242 pxSwatch:60_map.js:246 mapSpr:60_map.js:251 eqSVG:60_map.js:257 sprSVG:60_map.js:259 stIcon:60_map.js:268 armyGear:60_map.js:269 armyUFor:60_map.js:271 stDedup:60_map.js:276 stIconSVG:60_map.js:278 plateStatus:60_map.js:280 plateBox:60_map.js:281 mapPlate:60_map.js:283 settPlate:60_map.js:294 settBehind:60_map.js:305 settInsideMarks:60_map.js:309 mapBarHTML:60_map.js:324 terrOwners:60_map.js:335 terrFlags:60_map.js:337 unrestCamps:60_map.js:343 intrudersOf:60_map.js:345 settReach:60_map.js:349 settEcon:60_map.js:351 pillageCheck:60_map.js:360 pillageTargets:60_map.js:364 runPillage:60_map.js:367 armyStatus:60_map.js:380 mapMarkers:60_map.js:395 inspHTML:60_map.js:406 inspHead:60_map.js:409 inspCell:60_map.js:412 g:60_map.js:413 inspCan:60_map.js:414 inspArmy:60_map.js:415 settStatus:60_map.js:435 settStatusMarks:60_map.js:445 inspSett:60_map.js:449 envoyFor:60_map.js:481 armyMusterBtn:60_map.js:484 inspCamp:60_map.js:495 engageTargets:60_map.js:509 wireInsp:60_map.js:515 mapLayers:60_map.js:540 mapSVG:60_map.js:643 outlawReport:60_map.js:645 banditDomain:60_map.js:656 campKey:60_map.js:658 banditAutoHTML:60_map.js:660 armyName:60_map.js:669 syncMapTiers:60_map.js:671 mapLinkBad:60_map.js:678 mapLinksHTML:60_map.js:679 wireBanditAuto:60_map.js:690 banditAuto:60_map.js:696 BST:60_map.js:697 bLog:60_map.js:698 hk:60_map.js:700 mapSetts:60_map.js:701 cellPlayer:60_map.js:702 cellClaimed:60_map.js:704 pinNewCell:60_map.js:706 cellSett:60_map.js:712 mapArmies:60_map.js:715 cellArmy:60_map.js:716 cellTitle:60_map.js:719 byDist:60_map.js:723 isWild:60_map.js:727 wildZones:60_map.js:728 outlawZones:60_map.js:730 zoneOf:60_map.js:735 zoneOwners:60_map.js:736 outlawOwners:60_map.js:741 outlawOwner:60_map.js:743 outlawOf:60_map.js:745 campWild:60_map.js:747 wildCount:60_map.js:749 wildDone:60_map.js:750 autoDeploy:60_map.js:756 placeWildOutlaw:60_map.js:782 rescatterWild:60_map.js:804 pieceAura:60_map.js:808 wardMap:60_map.js:814 wardsOf:60_map.js:815 wardRoom:60_map.js:816 wardFill:60_map.js:818 wardCand:60_map.js:820 garrisonTargets:60_map.js:826 presHexes:60_map.js:834 wardAuto:60_map.js:838 wardPrune:60_map.js:848 wardMarks:60_map.js:850 campInRange:60_map.js:862 settleWhere:60_map.js:867 hexFree:60_map.js:871 spawnCamp:60_map.js:872 growCamps:60_map.js:874 expandOutlaw:60_map.js:879 immuneUprising:60_map.js:882 banditTargetMods:60_map.js:883 cunningAction:60_map.js:885 endorsedExtort:60_map.js:886 banditSpared:60_map.js:889 banditAct:60_map.js:891 runBanditMechanics:60_map.js:926 banditSpeed:60_map.js:949 banditAuraList:60_map.js:951 banditRun:60_map.js:958 banditFlow:60_map.js:967 moveCamp:60_map.js:971 moveBandit:60_map.js:974 banditReturn:60_map.js:982 banditSiegeTimer:60_map.js:987 banditArmyKeys:60_map.js:990 banditMoves:60_map.js:991 banditSkims:60_map.js:1061 provinceCampExtort:60_map.js:1071 creditSkims:60_map.js:1076 envoyOutcome:60_map.js:1083 banditCunningHTML:60_map.js:1088 dieLookup:60_map.js:1105 terrainTablesHTML:60_map.js:1108 mapToolsHTML:60_map.js:1131 banditPanelHTML:60_map.js:1165 mapAsP:60_map.js:1181 mapEditBlock:60_map.js:1182 mapGuard:60_map.js:1191 guarded:60_map.js:1193 mapCellClick:60_map.js:1195 wireMap:60_map.js:1223 srcKeys:70_rules.js:6 srcMatch:70_rules.js:13 srcHas:70_rules.js:14 srcRows:70_rules.js:16 bordersOf:70_rules.js:20 poCap:70_rules.js:24 poTextFloor:70_rules.js:25 siegeTextMods:70_rules.js:28 siegeWinterOK:70_rules.js:35 siegeDoubleOK:70_rules.js:36 pietyBlocked:70_rules.js:39 actRestrict:70_rules.js:42 actRiders:70_rules.js:54 settById:70_rules.js:66 besiegeExempt:70_rules.js:68 settBesieged:70_rules.js:69 armySieging:70_rules.js:71 armyBesieged:70_rules.js:73 armyStateTags:70_rules.js:74 armyHeld:70_rules.js:84 armyBlocked:70_rules.js:87 immuneBlocked:70_rules.js:88 cellBlocked:70_rules.js:89 blockedMoveFails:70_rules.js:91 garrisonSizes:70_rules.js:95 hasGarrisons:70_rules.js:96 garrisonGear:70_rules.js:98 garrisonOf:70_rules.js:99 garrisonsOf:70_rules.js:103 garrisonCard:70_rules.js:104 standingOnceRows:70_rules.js:125 onceEffects:70_rules.js:127 onceState:70_rules.js:128 onceWindowNow:70_rules.js:132 onceHTML:70_rules.js:133 onceUse:70_rules.js:144 noteAdd:70_rules.js:153 recoupNote:70_rules.js:155 UPKEEP:70_rules.js:162 SUPPLY:70_rules.js:163 blackMarketReact:70_rules.js:166 extortReact:70_rules.js:173 cunningExtortMore:70_rules.js:179 extortGroup:70_rules.js:183 extortGold:70_rules.js:187 danegeldRows:70_rules.js:199 loans:70_rules.js:208 loanReqs:70_rules.js:209 loanTerms:70_rules.js:210 loanInterest:70_rules.js:213 loanOK:70_rules.js:215 lentThisTurn:70_rules.js:216 runLoans:70_rules.js:217 loanAmtIn:70_rules.js:223 loansHTML:70_rules.js:224 lendNow:70_rules.js:245 autoExtortRows:70_rules.js:265 extortSlots:70_rules.js:274 exTargets:70_rules.js:277 extortTargetRows:70_rules.js:278 extortCardHTML:70_rules.js:284 runAutoExtort:70_rules.js:304 firstDoubtRed:70_rules.js:332 fdState:70_rules.js:336 gainDoubt:70_rules.js:339 fdGold:70_rules.js:343 siegeOn:70_rules.js:347 endSettlementSieges:70_rules.js:348 besiegedCount:70_rules.js:349 pById:70_rules.js:350 nextId:70_rules.js:351 captureTransfer:70_rules.js:352 sackWards:70_rules.js:364 sackApply:70_rules.js:369 banditSack:70_rules.js:385 resolveRealm:70_rules.js:397 sackLocks:70_rules.js:404 armyHex:70_rules.js:408 settHex:70_rules.js:409 musterLimit:70_rules.js:410 musterTick:70_rules.js:418 musterStep:70_rules.js:421 hasMusterField:70_rules.js:428 charterFlags:70_rules.js:431 selArmy:70_rules.js:454 canMoveArmy:70_rules.js:455 armyBesiegeExempt:70_rules.js:457 canEnterSett:70_rules.js:459 armyInside:70_rules.js:461 enterCheck:70_rules.js:464 freeHexNear:70_rules.js:466 kickOut:70_rules.js:469 armiesInside:70_rules.js:472 terrPen:70_rules.js:474 terrBlocked:70_rules.js:475 terrWaterStop:70_rules.js:476 terrStrain:70_rules.js:477 provinceOf:70_rules.js:479 moveTraits:70_rules.js:481 speedOf:70_rules.js:484 hexNb:70_rules.js:516 auraSources:70_rules.js:520 moveRange:70_rules.js:530 moveInfo:70_rules.js:572 moveStops:70_rules.js:575 moveEndTriggers:70_rules.js:580 waterBlockers:70_rules.js:590 moveArmyTo:70_rules.js:594 moveOverlay:70_rules.js:617 movePanelHTML:70_rules.js:630 set:70_rules.js:641 computeAll:70_rules.js:642 sceneInfra:80_scene_shell.js:14 wardChains:80_scene_shell.js:20 sceneLots:80_scene_shell.js:27 renderEsBar:80_scene_shell.js:40 sceneArmies:80_scene_shell.js:48 renderScene:80_scene_shell.js:55 renderSettlements:80_scene_shell.js:172 lockTarget:80_scene_shell.js:235 lockBlock:80_scene_shell.js:244 adminUI:80_scene_shell.js:257 firstHostOpen:80_scene_shell.js:273 firstHostBtn:80_scene_shell.js:274 hudSign:80_scene_shell.js:280 hudData:80_scene_shell.js:281 hudTips:80_scene_shell.js:290 renderHUD:80_scene_shell.js:303 ageStripHTML:80_scene_shell.js:323 setupOn:80_scene_shell.js:337 renderSetup:80_scene_shell.js:338 checkedIn:80_scene_shell.js:367 checkinFD:80_scene_shell.js:368 checkinTxt:80_scene_shell.js:374 checkinHTML:80_scene_shell.js:375 setupHoldHTML:80_scene_shell.js:382 renderTurnStrip:80_scene_shell.js:407 syncBoardEndBtn:80_scene_shell.js:439 mnavSync:80_scene_shell.js:455 herName:80_scene_shell.js:465 herKey:80_scene_shell.js:466 lumOf:80_scene_shell.js:467 herMix:80_scene_shell.js:471 herN:80_scene_shell.js:473 herPaths:80_scene_shell.js:474 heraldOf:80_scene_shell.js:479 mapBanner:80_scene_shell.js:482 pTok:80_scene_shell.js:485 inboxItems:85_ux.js:10 renderInbox:85_ux.js:25 evIn:85_ux.js:44 hudPopBack:85_ux.js:59 hudPopFill:85_ux.js:61 hudPop:85_ux.js:88 hudPopClose:85_ux.js:89 renderChrome:85_ux.js:95 welcomeOn:86_welcome.js:11 welcomeLinks:86_welcome.js:15 welcomeClose:86_welcome.js:17 welcomeProfile:86_welcome.js:20 culHer:86_welcome.js:23 domDots:86_welcome.js:26 radarSVG:86_welcome.js:27 heritagesFor:86_welcome.js:35 seatCard:86_welcome.js:37 seatView:86_welcome.js:46 culDetail:86_welcome.js:51 profileView:86_welcome.js:64 welcomeRender:86_welcome.js:74 welcomeClick:86_welcome.js:86 undoSnap:90_app.js:5 undoRecord:90_app.js:7 undoRebase:90_app.js:13 undoScoped:90_app.js:14 undoApply:90_app.js:15 doUndo:90_app.js:32 doRedo:90_app.js:33 undoButtons:90_app.js:34 actSnap:90_app.js:47 actRebase:90_app.js:48 actJoin:90_app.js:50 actSchedule:90_app.js:53 fmtG:90_app.js:54 boardDiff:90_app.js:55 actFlush:90_app.js:87 gameAllowed:90_app.js:104 gameData:90_app.js:105 refreshGames:90_app.js:106 gameReplace:90_app.js:109 newGameState:90_app.js:114 isReady:90_app.js:140 readyCheck:90_app.js:141 gslug:90_app.js:155 kwify:90_app.js:168 wikiA:90_app.js:179 gkHtml:90_app.js:180 openFromHash:90_app.js:199 setLift:90_app.js:230 gkShow:90_app.js:239 gkHide:90_app.js:243 gkFor:90_app.js:244 chatHdr:90_app.js:303 chatTargets:90_app.js:309 chatParse:90_app.js:311 chatColor:90_app.js:319 chatLine:90_app.js:320 chatRender:90_app.js:324 chatSys:90_app.js:330 chatComplete:90_app.js:345
```
