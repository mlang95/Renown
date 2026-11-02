# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-11-02 · data VERSION `0.4.9.9.15-d10-STrue` · HEAD `6d435ea 2026-11-02`

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
| `CE/build_all_CE.bat` | 531 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE/ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE/infra.py` | 109 |  |
| `CE/keyword_bloat_v2.md` | 101 | Keyword Bloat — v2 |
| `CE/parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE/patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE/rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE/renown_data.py` | 4448 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_data_d10.py` | 4448 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_data_d10_legacy.py` | 5076 | renown_data_d10_legacy — FROZEN 2026-10-30. The legacy (SIMPLE=0) data: innate + mastery Pursuits, the |
| `CE/renown_data_d8.py` | 2801 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_server.bat` | 16 | renown_server.bat - (re)start the Renown board server in WSL. |
| `CE/repo_map.py` | 250 | repo_map.py — write REPO_MAP.md next to this file (CE/, beside CLAUDE.md): a generated index of the Renown repo for |
| `CE/run_tournament_d10.bat` | 108 | Renown d10 tournament runner  —  CE build |
| `CE/run_tournament_d10.py` | 131 | run_tournament_d10.py — run the Renown tournament against the d10 build. |
| `CE/sprites.py` | 6468 | sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene). |
| `CE/verify_d10.py` | 168 | verify_d10.py — prove the CE wiring is live before spending hours on a run. |
| `CE/.claude/launch.json` | 233 |  |
| `CE/Combatv4/analysis.py` | 2125 | Analysis module for tournament results. |
| `CE/Combatv4/batch_engine.py` | 1658 | Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays, |
| `CE/Combatv4/combat_kernel_d10.py` | 268 | combat_kernel.py — SHARED numba kernels for both combat engines. |
| `CE/Combatv4/combat_morale_d10.py` | 155 | combat_morale.py — SHARED morale phase for both combat engines (C2, subsystem 2). |
| `CE/Combatv4/combat_primitives_d10.py` | 147 | combat_primitives.py — SHARED rules-math layer for both combat engines (C2). |
| `CE/Combatv4/dice_config.py` | 116 | dice_config — single source for die size across both combat engines. |
| `CE/Combatv4/loadouts.py` | 1189 | Loadout generator for the combat tournament. |
| `CE/Combatv4/make_d10_data.py` | 172 | Generate renown_data_d10.py from renown_data_CE.py. |
| `CE/Combatv4/make_d10_engines.py` | 143 | Generate *_d10.py engine files with FACES parameterised. |
| `CE/Combatv4/normalized_matrix.py` | 277 | Normalized symmetric tactic matrix. |
| `CE/Combatv4/playstyles.py` | 784 | Playstyle module — playstyles drive tactic selection in combat. |
| `CE/Combatv4/renown_combat_d10.py` | 563 | Renown combat simulator. |
| `CE/Combatv4/run_tournament.py` | 197 | Standalone Renown tournament runner. |
| `CE/Combatv4/tactics_analysis.py` | 54 | Tactics analysis helpers for the Renown Combat Lab. |
| `CE/Combatv4/tournament_vec.py` | 356 | Vectorized tournament runner — same interface as tournament.py but ~4x faster |
| `CE/Combatv4/vectorized_combat_d10.py` | 1976 | Vectorized matchup runner. |
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
| `CE/references/effect_registry.py` | 421 | effect_registry.py -- every rules-text pattern the settlement board acts on, matched once at build time. |
| `CE/references/equipment_sheet.py` | 691 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `CE/references/faction_sheet.py` | 447 | Renown — Faction card sheet generator. |
| `CE/references/faq_export.py` | 444 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `CE/references/gen_compendium.py` | 185 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `CE/references/gen_layout.py` | 374 | gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data. |
| `CE/references/gen_layout_roots.py` | 123 | gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it. |
| `CE/references/gen_settlement_board.py` | 1074 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
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
| `CE/references/settlement_board.html` | — | generated HTML (2162 KB) |
| `CE/references/settlement_mats.py` | 302 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `CE/references/spec_tree_sheet.py` | 1184 | Renown — Specialization Tree renderer. |
| `CE/references/svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `CE/references/sync_derived.py` | 88 | sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES. |
| `CE/references/tactic_sheet.py` | 446 | Renown — Tactic card sheet generator (v3). |
| `CE/references/wiki_markers.py` | 296 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
| `CE/references/world.txt` | 1517 |  |
| `CE/references/worldtxt.py` | 328 | worldtxt.py — parse the hand-maintained world.txt lore book into structured |
| `CE/references/board/body.html` | 216 |  |
| `CE/references/board/js/00_core.js` | 54 | __DATA__*/; |
| `CE/references/board/js/10_table.js` | 1009 | ===================== TABLE: seating, Council & Envoy phases ===================== |
| `CE/references/board/js/15_realm.js` | 567 | ===================== REALM: the play surface ===================== |
| `CE/references/board/js/16_tally.js` | 132 | ===================== INTRIGUE & TALLY PHASES (RULES: Envoy Phase steps 3 and 5) ===================== |
| `CE/references/board/js/17_diplo_step.js` | 131 | ===================== DIPLOMACY STEP (PHASE_REFORM): offers between players ===================== |
| `CE/references/board/js/20_state.js` | 625 | ---- state: multiplayer dashboard ---- |
| `CE/references/board/js/30_empire.js` | 1782 | ---- catalog ---- |
| `CE/references/board/js/35_plan.js` | 100 | ---- Plans (this device only): goal Holdings / Infrastructure / Wonders per player, in priority order. Each goal's path is worked |
| `CE/references/board/js/40_realm_data.js` | 409 | ---- Dashboards view ---- |
| `CE/references/board/js/50_battle.js` | 1145 | ---- Battle ---- |
| `CE/references/board/js/52_battlefield.js` | 183 | ---- Battle field: a top-down view between the two datasheets ---- |
| `CE/references/board/js/55_ai.js` | 501 | ---- AI players: culture-driven bots for seats marked AI (and, later, the headless simulator) ---- |
| `CE/references/board/js/60_map.js` | 1308 | ---- Map view ---- |
| `CE/references/board/js/70_rules.js` | 653 | ===================== EFFECT PLUMBING: the effect registry (references/effect_registry.py) ===================== |
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
| `IMMUNE` | 95 | str | 'Immune' |
| `immune` | 96 | function |  |
| `NEGATE` | 101 | str | 'Negate' |
| `negate` | 102 | function |  |
| `IMMUNE_DESTROY_SHIELD` | 108 | str | 'Immune Destroy Shield' |
| `IMMUNE_UNWIELDY` | 109 | str | 'Immune Unwieldy' |
| `IMMUNE_STRAIN` | 110 | str | 'Immune Strained' |
| `NEGATE_UNSTOPPABLE` | 112 | str | 'Immune Unstoppable' |
| `NEGATE_TEMPERED` | 114 | str | 'Negate Planishing' |
| `NEGATE_RIPOSTE` | 115 | str | 'Negate Riposte' |
| `NEGATE_SHIELDED` | 116 | str | 'Negate Shielded' |
| `MINUS_1_PARRY` | 117 | str | '-1 to Parry' |
| `HALFSWORD` | 118 | str | 'Halfsword' |
| `DUAL_WIELD` | 119 | str | 'Dual Wield' |
| `FLORENTINE` | 120 | str | 'Florentine' |
| `PIVOTAL` | 121 | str | 'Focused' |
| `GLOSSARY` | 124 | dict | 192 |
| `MORALE_GLOSSARY` | 257 | dict | 4 |
| `ARMY_MAX_RETINUES` | 283 | int | 25 |
| `FRONT_LINE_MAX` | 284 | int | 10 |
| `RESERVE_MAX` | 285 | int | 5 |
| `MORALE_DICE_MAX` | 286 | int | 5 |
| `PANIC_CASUALTY_THRESHOLD` | 287 | int | 5 |
| `ENDURANCE_REGAIN` | 288 | int | 2 |
| `RETINUES` | 292 | dict | 4 |
| `WEAPONS` | 299 | dict | 21 |
| `WEAPON_2H_PROFILES` | 331 | dict | 2 |
| `RANGED` | 333 | dict | 6 |
| `SHIELDS` | 343 | dict | 6 |
| `ARMORS` | 352 | dict | 6 |
| `TIERS` | 363 | list | 5 |
| `TIER_UNLOCK` | 364 | dict | 5 |
| `STANDING_EFFECTS` | 375 | dict | 6 |
| `TACTIC_MATRIX` | 400 | dict | 49 |
| `TACTICS` | 459 | list | 7 |
| `TACTIC_NOTES` | 461 | dict | 0 |
| `BATTLE_NARRATION` | 467 | dict | 19 |
| `CULTURE_SELF_MADE` | 510 | str | 'Self-made' |
| `CULTURES` | 512 | dict | 15 |
| `NODES` | 680 | dict | 147 |
| `DEPRECATED_NODES` | 1708 | dict | 3 |
| `HOLDING_GROUPS` | 1718 | dict | 9 |
| `SCOPES` | 1735 | tuple | 3 |
| `SCOPE_BY_TYPE` | 1736 | dict | 2 |
| `LINE_LABELS` | 1740 | dict | 31 |
| `lines_of` | 1774 | function |  |
| `REQ_KEY` | 1780 | str | 'infrastructure_req' |
| `REQ_LABEL` | 1781 | str | 'Infrastructure Req' |
| `TYPE_ORDER` | 1783 | list | 10 |
| `CHAIN_TERM` | 1785 | str | 'Mastery Chain' |
| `SHUTTER_TERM` | 1787 | str | 'Shuttered' |
| `UPKEEP_TERM` | 1791 | str | 'Upkeep' |
| `SUPPLY_TERM` | 1792 | str | 'Supply' |
| `PURSUIT_TERM` | 1794 | tuple | 2 |
| `node_parents` | 1796 | function |  |
| `get_data` | 1804 | function |  |
| `MONUMENT_SUMMARY` | 1813 | dict | 25 |
| `WONDER_SUMMARY` | 1843 | dict | 4 |
| `FACTIONS` | 1853 | dict | 58 |
| `DEPRECATED_FACTIONS` | 2594 | dict | 3 |
| `INFRASTRUCTURE` | 2604 | dict | 20 |
| `WONDERS` | 2730 | dict | 4 |
| `INFRA_TIERS` | 2731 | list | 5 |
| `SETTLEMENTS` | 2739 | dict | 5 |
| `PRESENCE_RANGE` | 2750 | int | 2 |
| `WARD_MODEL` | 2754 | str | 'range1' |
| `WARD_RULES` | 2755 | dict | 2 |
| `WARD_RULE` | 2763 | str | 'A Settlement Ward is a slot that holds  |
| `FAITH_FICKLE_PO` | 2765 | int | 0 |
| `ERAS` | 2768 | dict | 4 |
| `PO_BANDS` | 2788 | dict | 11 |
| `po_scale` | 2807 | function |  |
| `po_value` | 2814 | function |  |
| `po_effect` | 2819 | function |  |
| `PUBLIC_ORDER` | 2826 | dict | 11 |
| `PUBLIC_ORDER_BY_ERA` | 2827 | dict | 4 |
| `PO_MODIFIERS` | 2833 | dict | 2 |
| `DOMAIN_BOARD` | 2851 | dict | 6 |
| `SEASONS` | 2888 | dict | 4 |
| `TRADE_REQUIRES_BORDER` | 2897 | bool | True |
| `TRADE_RULES` | 2898 | dict | 6 |
| `efficient_graph` | 2913 | function |  |
| `EFFICIENT_MULTI` | 2923 | dict | 139 |
| `EFFICIENT` | 2924 | dict | 139 |
| `BANDIT_CAMP_START` | 2932 | int | 10 |
| `BANDIT_CAMP_GOLD` | 2933 | int | 2000 |
| `BANDIT_ARMY_THRESHOLD` | 2934 | int | 25 |
| `BANDIT_GROWTH_PER_ERA` | 2935 | dict | 4 |
| `BANDIT_EQUIPMENT_PER_ERA` | 2936 | dict | 4 |
| `HARDCORE_BANDIT_EQUIPMENT_PER_ERA` | 2940 | dict | 4 |
| `HARDCORE_WILD_OUTLAW` | 2943 | dict | 9 |
| `BANDITS` | 2954 | dict | 5 |
| `TIMERS` | 2962 | dict | 8 |
| `CHARTER_MIN_RANGE` | 2974 | int | 4 |
| `OUTLAW_BUFFER_RANGE` | 2975 | int | 2 |
| `HAMLET_RANGE` | 2976 | int | 2 |
| `OUTLAW_COUNTRY_START` | 2977 | int | 3 |
| `WILD_OUTLAW` | 2985 | dict | 9 |
| `wild_outlaw_count` | 2998 | function |  |
| `BANDIT_CAMP_REACH` | 3005 | str | 'province' |
| `VASSAL_EXCHANGE_CAP` | 3008 | int | 5000 |
| `VASSAL_INFLUENCE_TAKE` | 3009 | int | 3 |
| `BUILD_TIMERS` | 3013 | dict | 11 |
| `PURSUIT_UPKEEP_DEFAULT` | 3028 | int | 100 |
| `HOLDING_TIER_COST` | 3030 | dict | 4 |
| `holding_standing` | 3038 | function |  |
| `holding_cost` | 3044 | function |  |
| `holding_build_time` | 3052 | function |  |
| `HOLDING_COST_TEXT` | 3058 | str | 'by Standing: Untested 100 (Build Timer  |
| `TERRAIN` | 3061 | dict | 7 |
| `MOVEMENT_MODIFIERS` | 3082 | dict | 6 |
| `TACTICAL_TERRAIN` | 3094 | dict | 7 |
| `TACTICAL_GLOBAL` | 3110 | list | 1 |
| `INFLUENCE_GAIN` | 3112 | dict | 8 |
| `ENVOY_OUTCOME_THRESHOLDS` | 3168 | dict | 4 |
| `CUNNING_EXTORT` | 3187 | int | 2000 |
| `CUNNING_EXTORT_ENDORSED` | 3188 | int | 2000 |
| `CUNNING_DOUBT` | 3189 | int | 1 |
| `ENVOY_OUTCOMES` | 3190 | dict | 5 |
| `ACTIONS` | 3213 | dict | 24 |
| `TREATIES` | 3423 | dict | 5 |
| `ALLIANCE_RULES` | 3431 | list | 3 |
| `EDICT_STREAK_TURNS` | 3441 | int | 5 |
| `GAME_TURN_LIMIT` | 3442 | int | 50 |
| `EDICT_UNIQUE` | 3445 | bool | False |
| `EDICT_UNIQUE_RULE` | 3446 | str | 'Each Domain, Monument, or Wonder counts |
| `IMPERIUM_REQUIREMENT` | 3452 | dict | 5 |
| `EDICTS` | 3459 | dict | 8 |
| `BANDIT_BEHAVIOR` | 3475 | dict | 9 |
| `PURSUIT_UPKEEP_BY_TYPE` | 3499 | dict | 4 |
| `UPKEEP_TRACKS` | 3509 | dict | 3 |
| `pursuit_upkeep` | 3516 | function |  |
| `ARMY_UPKEEP_NOTE` | 3527 | str | "Net Army Supply = the sum of each Army' |
| `COSTS` | 3531 | dict | 12 |
| `COUNCIL_DOMAIN` | 3554 | str | 'Industry' |
| `COUNCIL_DOMAIN_SPRING` | 3555 | str | 'Industry' |
| `ENVOY_PHASE_SPRING` | 3556 | str | 'Diplomacy' |
| `FORUM_DOMAIN` | 3557 | NoneType |  |
| `FORUM_ACTIONS` | 3558 | int | 1 |
| `PHASES` | 3559 | tuple | 5 |
| `STARTING_TURN_PHASE_OPENER` | 3560 | str | 'Works' |
| `EMPIRE_START_TIERS` | 3564 | tuple | 2 |
| `STARTING_TREASURY` | 3565 | int | 10000 |
| `SETUP_CAPITAL_PICKS` | 3568 | int | 2 |
| `SETUP_HAMLET_PICKS` | 3569 | int | 0 |
| `SETUP_HAMLET_HOLDINGS` | 3570 | tuple | 1 |
| `SETUP_HAMLET_TEXT` | 3571 | str | 'Common Land' |
| `HAMLET_REPEATABLE` | 3573 | tuple | 1 |
| `HAMLET_REPEATABLE_TEXT` | 3574 | str | 'Common Land' |
| `AGES` | 3580 | dict | 5 |
| `AGE_YEAR_SEASON` | 3587 | str | 'Spring' |
| `AGE_YEAR_ROLL_MEAN` | 3590 | float | 0.45 |
| `AGE_YEAR_ROLL_SD` | 3591 | float | 0.16666666666666666 |
| `CAPITAL_EDGE_RANGE` | 3592 | int | 4 |
| `BOARD_SIZES` | 3594 | dict | 3 |
| `SIEGE_CALCULUS` | 3600 | dict | 2 |
| `SIEGE_SOURCE_VALUES` | 3615 | dict | 2 |
| `PO_GLOSS_TERMS` | 3640 | list | 19 |
| `NAME_DISPLAY` | 3659 | dict | 94 |
| `TIER_DISPLAY` | 3696 | dict | 1 |
| `ITEM_TIER_DISPLAY` | 3702 | dict | 1 |
| `TERM_ENVOY_SCORE` | 3709 | str | 'Authority' |
| `display_score` | 3719 | function |  |
| `ALIASES` | 3729 | dict | 97 |
| `display` | 3739 | function |  |
| `display_tier` | 3744 | function |  |
| `display_text` | 3754 | function |  |
| `display_list` | 3777 | function |  |
| `display_md` | 3787 | function |  |
| `display_html` | 3794 | function |  |
| `display_obj` | 3806 | function |  |
| `undisplay` | 3819 | function |  |
| `verify_aliases` | 3828 | function |  |
| `BANDIT_FACES` | 3852 | int | 10 |
| `BANDIT_CUNNING_MIN` | 3853 | int | 10 |
| `die_table_ranges` | 3856 | function |  |
| `die_table_rows` | 3864 | function |  |
| `die_table_text` | 3872 | function |  |
| `die_table_lookup` | 3880 | function |  |
| `die_table_verify` | 3887 | function |  |
| `die_table_weights` | 3906 | function |  |
| `BANDIT_CUNNING_TABLE` | 3916 | dict | 4 |
| `bandit_cunning_ranges` | 3923 | function |  |
| `bandit_cunning_rows` | 3924 | function |  |
| `bandit_cunning_lookup` | 3925 | function |  |
| `bandit_cunning_text` | 3927 | function |  |
| `BANDIT_TACTIC_TABLE` | 3934 | dict | 6 |
| `BANDIT_TACTICS` | 3942 | list | 6 |
| `bandit_tactic_ranges` | 3944 | function |  |
| `bandit_tactic_rows` | 3945 | function |  |
| `bandit_tactic_lookup` | 3946 | function |  |
| `verify_bandit_tables` | 3949 | function |  |
| `RENOWN_MAX` | 4049 | int | 30 |
| `RENOWN_PER_TURN` | 4050 | int | 1 |
| `DOMAIN_POINTS_PER_TURN` | 4051 | int | 1 |
| `AI_DOMAIN_POINTS` | 4057 | str | 'Spend Domain Points one Standing at a t |
| `AI_PRIORITIES` | 4059 | list | 8 |
| `AI_FAITH_AVOID` | 4070 | list | 5 |
| `AI_STYLE` | 4093 | dict | 3 |
| `AI_ARCHETYPE` | 4116 | dict | 8 |
| `AI_PO_GOLD` | 4130 | int | 800 |
| `AI_MUSTER` | 4132 | dict | 3 |
| `AI_DIPLOMACY` | 4134 | dict | 4 |
| `FACTION_NAMES` | 4176 | dict | 58 |
| `FACTION_TERM` | 4184 | tuple | 2 |
| `faction_body` | 4190 | function |  |
| `GLOSSARY_CATEGORIES` | 4231 | list | 19 |
| `WIKI_NOLINK` | 4260 | list | 6 |
| `GLOSSARY_SEE` | 4269 | dict | 109 |
| `COND_UPKEEP_FACTOR` | 4315 | float | 0.5 |
| `holding_combat_tags` | 4325 | function |  |
| `holding_upkeep` | 4372 | function |  |
| `holding_domain` | 4385 | function |  |
| `HOLDING_SIM` | 4404 | dict | 147 |
| `AI_PROFILES` | 4416 | dict | 15 |

## 4. Build steps — `CE/build_all_CE.bat`

| Label | Line | Scripts | Echo |
|---|---|---|---|
| `:maps` | 240 | `build_mapapp.py` | --- Map generator app ---; skipped - build_mapapp.py not ported |
| `:cards` | 260 | `generate_cards.py` | --- Cards ---; skipped - generate_cards.py not ported |
| `:docs` | 275 | `md_to_docx.py`, `combat_sheet.py`, `spec_tree_sheet.py`, `playstyle_reference.py`, `pursuit_tiles.py`, `gen_layout.py`, `render_tree.py`, `svg_to_pdf.py`, `domain_board.py`, `infra_board.py`, `settlement_mats.py`, `gen_layout_roots.py`, `gen_settlement_board.py`, `faq_export.py`, `host_sheet.py` | --- Docs ---; Rules - with Holdings, Equipment, Factions, glossary, index...; Combat quick-reference sheet...; Specialization trees...; Playstyle reference...; Pursuit ward-tiles...; Pursuit tech tree |
| `:wiki` | 317 | `build_wiki.py` | --- Wiki ---; skipped - build_wiki.py not ported; skipped - wiki_markers.py not ported, build_wiki imports it; skipped - %RULES_MD% not found; Wiki build FAILED - skipping repo push.; Syncing into %WI |
| `:pushrepo` | 372 | `repo_map.py` | --- Push repo (v%VERSION%, DIE=%DIE%) -^> %REPO_DIR% ---; Git LFS not installed ^(https://git-lfs.com^) - skipping repo push so a; large file can't be committed without LFS. Install once, then re-run. |
| `:end` | 450 | — | Done. Press any key to close. |
| `:board` | 460 | `build_board.py` | --- Board ---; skipped - build_board.py not ported; Board -^> %BOARD_OUT% |
| `:tactical` | 479 | `build_board.py` | --- Tactical board ---; skipped - build_board.py not ported; Tactical board -^> %TAC_OUT% |
| `:lore` | 501 | `gen_cultures.py`, `gen_intro.py`, `gen_draft.py`, `gen_pdf.py`, `gen_book_json.py` | --- Lore (world documents from renown_worldlore.py) ---; skipped - %DIR_LORE%\gen_cultures.py not ported; Lore -^> %LORE_OUT% |

## 5. Rules markers — `CE/RULES_push_simple.md`

- **{{TABLE}}** (30): `edicts`, `eras`, `timers`, `seasons`, `ages`, `net_influence`, `envoy_outcomes`, `influence_gain`, `domain_board`, `treaties`, `settlements`, `infrastructure`, `build_timers`, `terrain`, `public_order`, `po_modifiers`, `trade_rules`, `retinues`, `tactic_matrix`, `siege_calculus`, `bandits_by_era`, `bandit_cunning`, `bandit_armaments_hardcore`, `bandit_tactics`, `holdings`, `weapons`, `ranged`, `shields`, `armor`, `factions`
- **{{GLOSSARY}}** (18): `Reading the Rules`, `Turn & Phases`, `Envoys & Voting`, `Actions`, `Domains & Scoring`, `Treaties`, `Settlements & Holdings`, `Map & Range`, `Economy & Public Order`, `Army States`, `Battle Structure`, `Combat Keywords — Defense`, `Combat Keywords — Offense`, `Combat Keywords — Handling`, `Combat Keywords — Immune / Negate`, `War`, `World`, `Equipment Tiers`
- **{{ACTIONS}}** (5): `Diplomacy`, `Prowess`, `Cunning`, `Piety`, `Industry`
- **{{LIST}}** (1): `ALLIANCE_RULES`
- **{{TERM}}** (1): `Speed X`
- **{{IDX}}** (32): `Era`, `Empire Phase`, `Works Phase`, `Envoy Phase`, `Council Phase`, `Diplomacy Phase`, `Battle Phase`, `Rest Phase`, `Intrigue Phase`, `Tally Phase`, `Season`, `Age`, `Standing Rank`, `Max Influence`, `Settlement`, `Hamlet`, `Infrastructure`, `Primitive`, `Developed`, `Sophisticated`, `Prodigious`, `Wondrous`, `Wonder`, `Treasury`, `Revenue`, `Trade Agreement`, `Army`, `Garrison`, `Lay Siege`, `Capture`, `Sack`, `Bandit Camp`
- **{{VAL}}** (93): `AGE_YEAR_SEASON`, `ARMY_MAX_RETINUES`, `BANDITS.Bandit Domain Value`, `BANDIT_ARMY_THRESHOLD`, `BANDIT_CAMP_GOLD`, `BANDIT_CAMP_START`, `BANDIT_CUNNING_MIN`, `BANDIT_FACES`, `BLUNDER_THR`, `CAPITAL_EDGE_RANGE`, `CAP_THR`, `CHAIN_TERM`, `COUNCIL_DOMAIN`, `DOMAIN_BOARD.innate_influence_own_envoys.Untested`, `DOMAIN_POINTS_PER_TURN`, `EDICT_UNIQUE_RULE`, `ENDURANCE_REGAIN`, `ERAS.Ascension.rank`, `ERAS.Eminence.diplomacy_agreements`, `ERAS.Eminence.rank`, `ERAS.Founding.diplomacy_agreements`, `ERAS.Founding.rank`, `ERAS.Founding.renown`, `ERAS.Zenith.rank`, `FACES`, `FAITH_FICKLE_PO`, `FATIGUE_MORALE`, `FOCUSED_THR`, `FRONT_LINE_MAX`, `GAME_TURN_LIMIT`, `HAMLET_RANGE`, `HARDCORE_WILD_OUTLAW.border_range`, `HARDCORE_WILD_OUTLAW.spacing`, `HOLDING_COST_TEXT`, `INFRASTRUCTURE.Cathedral.empire_bonus`, `INFRASTRUCTURE.Library.requirement`, `INFRASTRUCTURE.Magistrate's Hall.requirement`, `INITIATIVE_MAX`, `INITIATIVE_MIN`, `MORALE_DICE_MAX`, `OUTLAW_BUFFER_RANGE`, `OUTLAW_COUNTRY_START`, `PANIC_CASUALTY_THRESHOLD`, `PARRY_BASE`, `PO_MAX`, `PO_MIN`, `PRESENCE_RANGE`, `RENOWN_PER_TURN`, `RESERVE_MAX`, `RETINUES.Knight Templar.cost`, `RETINUES.Knight Templar.to_hit`, `RETINUES.Levy.cost`, `RETINUES.Levy.to_hit`, `RETINUES.Man-at-Arms.cost`, `RETINUES.Man-at-Arms.to_hit`, `RETINUES.Sergeant.cost`, `RETINUES.Sergeant.to_hit`, `ROUT_THR`, `SACK_EXTORT_PER_TIER`, `SETTLEMENTS.City.garrison`, `SETTLEMENTS.Hamlet.wards`, `SETTLEMENTS.Metropolis.garrison`, `SETTLEMENTS.Metropolis.reach`, `SETTLEMENTS.Town.garrison`, `SETTLEMENTS.Village.garrison`, `SETTLEMENTS.Village.reach`, `SETUP_CAPITAL_PICKS`, `SHUTTER_TERM`, `SIEGE_CALCULUS.Lay Siege.floor`, `STANDING_RANK.Established`, `STANDING_RANK.Rising`, `STANDING_RANK.Sovereign`, `STANDING_RANK.Untested`, `STANDING_THRESHOLDS.Established`, `STANDING_THRESHOLDS.Rising`, `STANDING_THRESHOLDS.Sovereign`, `STANDING_THRESHOLDS.Untested`, `STARTING_TREASURY`, `STARTING_TURN_PHASE_OPENER`, `SUPPLY_TERM`, `TIMERS.Capture Timer.default`, `TIMERS.Sack Timer.default`, `TRADE_RULES.border_rule`, `TRADE_RULES.income_per_craft`, `UPKEEP_TERM`, `VASSAL_EXCHANGE_CAP`, `VASSAL_INFLUENCE_TAKE`, `WARD_RULE`, `WEALTH_EDICT_GOLD`, `WILD_OUTLAW.border_range`, `WILD_OUTLAW.per_players`, `WILD_OUTLAW.plus`, `WILD_OUTLAW.spacing`
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

Python: `load`:27, `strip_md`:34, `has_cond`:78, `to_int`:81, `classify`:84, `_iv`:154, `envoy_fx`:155, `combine_parts`:279, `combine_effects`:320, `rules_payload`:324, `tree_payload`:383, `parse_effects`:417, `parse_mreq`:423, `classify_req_token`:431, `build`:440, `font_faces`:543, `_pursuit_term_template`:568, `render_html`:576, `_style_js`:584, `place_names_payload`:595, `sprite_payload`:616, `find_mapgen`:638, `_board_template`:653, `check_rules`:667, `_val`:795, `council_heading`:804, `rules_section`:808, `phase_steps`:827, `battle_data`:844, `bandit_loadouts`:866, `effects_report`:919, `main`:950

JS sections: TABLE: seating, Council & Envoy phases :10_table.js:1, Action automation: Perform picker + resolution :10_table.js:324, REALM: the play surface :15_realm.js:1, INTRIGUE & TALLY PHASES (RULES: Envoy Phase steps 3 and 5) :16_tally.js:1, DIPLOMACY STEP (PHASE_REFORM): offers between players :17_diplo_step.js:1,  :40_realm_data.js:283, Inspect tool :60_map.js:328, EFFECT PLUMBING: the effect registry (references/effect_registry.py) :70_rules.js:1, ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS :70_rules.js:67, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :70_rules.js:162, CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper :85_ux.js:1, WELCOME: seats + profile (server games) :86_welcome.js:1, UNDO / REDO :90_app.js:1, ACTIVITY LOG :90_app.js:43, GAME: save · load · new :90_app.js:102, HOVER KEYWORDS :90_app.js:153

JS functions (1253, name:file:line):

```
prof2h:00_core.js:10 fixBastard:00_core.js:11 dispScore:00_core.js:18 presR:00_core.js:36 POB:00_core.js:39 poNum:00_core.js:40 efxOf:00_core.js:51 hitOf:00_core.js:52 facHit:00_core.js:53 razeTimerPlus:10_table.js:10 springDiplo:10_table.js:15 tnow:10_table.js:18 noteServerDate:10_table.js:19 gkey:10_table.js:25 lockOn:10_table.js:32 claimOf:10_table.js:33 mine:10_table.js:34 myClaimP:10_table.js:35 canEdit:10_table.js:36 boardEndOn:10_table.js:38 TB:10_table.js:39 seatFloor:10_table.js:41 tSeats:10_table.js:42 tTimer:10_table.js:43 tTurn:10_table.js:44 tBegun:10_table.js:45 tPhase:10_table.js:46 PT:10_table.js:48 tCur:10_table.js:49 tCurW:10_table.js:50 sameP:10_table.js:51 meP:10_table.js:52 canAct:10_table.js:53 seatMap:10_table.js:56 seated:10_table.js:60 isSpring:10_table.js:61 councilDomNow:10_table.js:63 councilOff:10_table.js:64 hostP:10_table.js:65 voteOrd:10_table.js:68 tOrder:10_table.js:69 canHost:10_table.js:70 seatsLocked:10_table.js:71 tStand:10_table.js:74 eraRec:10_table.js:75 diploInf:10_table.js:76 diploCap:10_table.js:77 eraActions:10_table.js:78 envActions:10_table.js:82 envSlots:10_table.js:83 endorsedBonus:10_table.js:89 slotLabel:10_table.js:93 slotOpen:10_table.js:94 withSlots:10_table.js:95 boardFx:10_table.js:98 fxOf:10_table.js:111 inProvinceOf:10_table.js:113 provFx:10_table.js:115 supCut:10_table.js:117 scopeOk:10_table.js:119 sgn:10_table.js:120 fxLabel:10_table.js:121 atWarPair:10_table.js:140 opposeBlock:10_table.js:141 domAsFx:10_table.js:148 innateParts:10_table.js:149 modSum:10_table.js:155 innateInf:10_table.js:157 voteCap:10_table.js:158 inflPool:10_table.js:161 personalEnvoys:10_table.js:162 councilEnvoys:10_table.js:163 tOutcome:10_table.js:164 outText:10_table.js:166 tPlan:10_table.js:169 missionWhy:10_table.js:187 domStarted:10_table.js:190 whisperEligibleEnvoys:10_table.js:191 tSim:10_table.js:194 performEval:10_table.js:285 comboEval:10_table.js:291 failPassFx:10_table.js:303 condFailFx:10_table.js:304 inviteHolders:10_table.js:308 inviteOf:10_table.js:310 actionsOf:10_table.js:311 actReqFlag:10_table.js:313 actInfoHTML:10_table.js:317 actCost:10_table.js:328 domCost:10_table.js:330 addFaith:10_table.js:331 alliedP:10_table.js:332 allyGroup:10_table.js:333 topPair:10_table.js:334 actDoubt:10_table.js:337 musterOpts:10_table.js:408 runMuster:10_table.js:415 buildOpts:10_table.js:431 buildPlaces:10_table.js:440 runBuild:10_table.js:444 improveOpts:10_table.js:450 expandOpts:10_table.js:456 runExpand:10_table.js:460 runImprove:10_table.js:464 runSettle:10_table.js:471 industryOpen:10_table.js:477 expediteWhy:10_table.js:482 repairOpts:10_table.js:484 runRepair:10_table.js:487 settName:10_table.js:493 warOnFac:10_table.js:496 warOn:10_table.js:500 grandVizier:10_table.js:504 tributeShieldOf:10_table.js:508 tributeShielded:10_table.js:509 pfSpec:10_table.js:511 pfHardFlags:10_table.js:512 pfTargets:10_table.js:528 pfSubs:10_table.js:541 pfSubLabel:10_table.js:542 evTxt:10_table.js:544 insteadFx:10_table.js:549 actDom:10_table.js:550 pfActs:10_table.js:551 pfInsteadSrc:10_table.js:553 pfForm:10_table.js:554 boardCounts:10_table.js:589 pendingOf:10_table.js:591 apLines:10_table.js:593 resolveEnvoy:10_table.js:596 campTgt:10_table.js:663 campExtort:10_table.js:664 autoRes:10_table.js:665 tApply:10_table.js:666 recAct:10_table.js:678 actTgtName:10_table.js:680 allActs:10_table.js:681 actsAt:10_table.js:686 actLine:10_table.js:687 realmActsHTML:10_table.js:688 tNext:10_table.js:695 tSetPhase:10_table.js:696 tRestartPhase:10_table.js:699 tAdd30:10_table.js:704 grantDP:10_table.js:707 dpOwed:10_table.js:708 tEndTurn:10_table.js:709 setSeats:10_table.js:729 tAutoSeat:10_table.js:734 tSig:10_table.js:740 tName:10_table.js:743 tVoteTxt:10_table.js:744 envBadges:10_table.js:745 innateTxt:10_table.js:751 tOutCls:10_table.js:753 tPerformHtml:10_table.js:754 summaryLines:10_table.js:776 chronOn:10_table.js:793 chron:10_table.js:794 chronSnap:10_table.js:797 chronTick:10_table.js:804 chronDate:10_table.js:814 empireChecklistHTML:10_table.js:815 treeSave:10_table.js:825 mapRaws:10_table.js:836 refRawAvail:10_table.js:839 refCulture:10_table.js:845 refAvail:10_table.js:846 treeHTML:10_table.js:848 infraTreeHTML:10_table.js:925 rulebookHTML:10_table.js:956 linkifyRules:10_table.js:959 renderReference:10_table.js:963 tCountdown:10_table.js:978 applyTheme:10_table.js:993 applySkin:10_table.js:1005 doFire:15_realm.js:8 patch:15_realm.js:12 rlCommit:15_realm.js:13 pOf:15_realm.js:14 standingPhaseActions:15_realm.js:15 holdingEpActions:15_realm.js:20 eurekaKey:15_realm.js:25 eurekaCut:15_realm.js:26 eurekaOn:15_realm.js:27 eurekaAction:15_realm.js:28 buildTimersOf:15_realm.js:30 cutBuildTimer:15_realm.js:36 activeCipherTimers:15_realm.js:41 cipherTimerResolve:15_realm.js:47 empWin:15_realm.js:53 empireHoldingHTML:15_realm.js:54 whisperGateHTML:15_realm.js:84 forgeRetryHTML:15_realm.js:88 courierDeferHTML:15_realm.js:92 rlOpen:15_realm.js:156 rlToggle:15_realm.js:157 renderTable:15_realm.js:162 seasonPlateHTML:15_realm.js:183 seasonDock:15_realm.js:187 seasonHerald:15_realm.js:196 renderRealmMap:15_realm.js:202 domCells:15_realm.js:214 realmTableHTML:15_realm.js:220 spectating:15_realm.js:262 miniCardHTML:15_realm.js:274 phaseCardHTML:15_realm.js:284 empireSummaryHTML:15_realm.js:339 dockCard:15_realm.js:355 dockHTML:15_realm.js:356 envoyQueueHTML:15_realm.js:430 inflPaneHTML:15_realm.js:452 inflCardHTML:15_realm.js:464 declInviteHTML:15_realm.js:484 drawersHTML:15_realm.js:523 turnLogItems:15_realm.js:535 turnLogHTML:15_realm.js:555 realmTimersBrief:15_realm.js:564 tallyVoter:16_tally.js:7 standingHit:16_tally.js:9 tallySupportOf:16_tally.js:10 tallyEndorseOf:16_tally.js:11 resolveOpen:16_tally.js:13 intrigueKinds:16_tally.js:15 intrigueSilenced:16_tally.js:24 whisperPending:16_tally.js:25 intrigueRun:16_tally.js:27 tallyRun:16_tally.js:38 envLabel:16_tally.js:61 tsId:16_tally.js:62 tRow:16_tally.js:63 envSel:16_tally.js:64 amtSel:16_tally.js:65 intrigueHTML:16_tally.js:66 tallyHTML:16_tally.js:94 inTurn:16_tally.js:109 selVal:16_tally.js:110 tallyTurn:16_tally.js:125 dsOn:17_diplo_step.js:7 dsKey:17_diplo_step.js:8 DS:17_diplo_step.js:9 dsCap:17_diplo_step.js:10 dsWho:17_diplo_step.js:11 dsAgreed:17_diplo_step.js:12 dsUsed:17_diplo_step.js:13 dsPartner:17_diplo_step.js:14 dsDone:17_diplo_step.js:15 dsAllDone:17_diplo_step.js:16 dsTypes:17_diplo_step.js:18 dsFlag:17_diplo_step.js:22 dsSnap:17_diplo_step.js:24 dsRestore:17_diplo_step.js:27 dsCourt:17_diplo_step.js:31 dsCourtRefund:17_diplo_step.js:34 dsEmb:17_diplo_step.js:37 dsFailable:17_diplo_step.js:38 dsEmbDue:17_diplo_step.js:40 dsFail:17_diplo_step.js:41 applyTreaty:17_diplo_step.js:45 dsEnds:17_diplo_step.js:53 dsClose:17_diplo_step.js:57 dsLog:17_diplo_step.js:58 dsOffer:17_diplo_step.js:59 dsAccept:17_diplo_step.js:61 dsEnd:17_diplo_step.js:65 dsEmbHTML:17_diplo_step.js:72 diploStepHTML:17_diplo_step.js:78 aiDiploStep:17_diplo_step.js:116 startDoms:20_state.js:2 ageRec:20_state.js:5 ageRisingOf:20_state.js:6 startDomsFor:20_state.js:7 startDomTotal:20_state.js:8 curYear:20_state.js:9 rollAgeYear:20_state.js:11 applyAgeStart:20_state.js:14 startSettlements:20_state.js:16 startSig:20_state.js:19 reseedIfPristine:20_state.js:21 newBoard:20_state.js:26 newPlayer:20_state.js:28 normalizeD:20_state.js:44 dedupeIds:20_state.js:70 activeBoard:20_state.js:72 reindex:20_state.js:73 pActive:20_state.js:86 dmgMark:20_state.js:88 dmgSrc:20_state.js:89 dmgSrcOf:20_state.js:90 chainOK:20_state.js:92 ignHas:20_state.js:96 flagState:20_state.js:97 ignBtn:20_state.js:102 ignNote:20_state.js:105 unlockStatus:20_state.js:111 nameHit:20_state.js:122 missTxt:20_state.js:123 recomputePC:20_state.js:125 buildTimerMod:20_state.js:130 timerMod:20_state.js:131 withBuildMod:20_state.js:135 pursuitBaseTime:20_state.js:136 infraBaseTime:20_state.js:137 repairTime:20_state.js:139 pursuitBuildTime:20_state.js:140 infraBuildTime:20_state.js:141 buildNote:20_state.js:142 settBaseTime:20_state.js:143 settBuildTime:20_state.js:144 itm:20_state.js:145 infraOn:20_state.js:146 shutToggle:20_state.js:149 shutUpkeep:20_state.js:153 checkinAct:20_state.js:159 gameStarted:20_state.js:160 glogTurn:20_state.js:164 glogSea:20_state.js:165 glogPush:20_state.js:166 glogSync:20_state.js:170 insolvent:20_state.js:173 tGold:20_state.js:175 boardOwnerName:20_state.js:180 empTimers:20_state.js:184 empEconomy:20_state.js:185 empPO:20_state.js:194 immuneStrainIn:20_state.js:206 siegeStrains:20_state.js:210 endMax:20_state.js:212 capEnd:20_state.js:213 effStrained:20_state.js:214 empArmies:20_state.js:215 endRow:20_state.js:222 boardEndTurn:20_state.js:225 stepRealmTimer:20_state.js:229 siegeFatigue:20_state.js:231 tickRealm:20_state.js:235 expireBlocks:20_state.js:239 expireBlocksTimed:20_state.js:240 empirePhase:20_state.js:243 tickTimers:20_state.js:270 facTypeBonus:20_state.js:279 pursuitUpkeep:20_state.js:282 withBoard:20_state.js:285 setOnline:20_state.js:301 clone:20_state.js:311 jeq:20_state.js:312 isObj:20_state.js:313 merge3:20_state.js:315 splitD:20_state.js:324 joinD:20_state.js:330 save:20_state.js:356 saveIfDirty:20_state.js:364 editing:20_state.js:399 cvar:20_state.js:419 fmt:20_state.js:420 cap:20_state.js:421 settUnbuilt:20_state.js:425 unbuiltMeta:20_state.js:426 settMeta:20_state.js:427 pinSettCell:20_state.js:428 settExpand:20_state.js:429 settFinish:20_state.js:430 settTier:20_state.js:433 occupants:20_state.js:434 hamletOK:20_state.js:435 hamletRoot:20_state.js:438 hamletFits:20_state.js:439 effList:20_state.js:448 effLabel:20_state.js:453 exemptionsOf:20_state.js:454 wardExemptions:20_state.js:463 isFreeRider:20_state.js:464 wardUse:20_state.js:465 needsChain:20_state.js:475 canPlace:20_state.js:478 hamletRepeat:20_state.js:498 setupRawOK:20_state.js:501 setupHoldFlags:20_state.js:502 capitalSett:20_state.js:515 setCapital:20_state.js:516 isCityPlus:20_state.js:518 dbActive:20_state.js:519 standingKey:20_state.js:525 armStanding:20_state.js:526 capBonus:20_state.js:531 eraCapBase:20_state.js:532 eraCap:20_state.js:533 capSrc:20_state.js:534 cityCount:20_state.js:535 eraAllows:20_state.js:537 rslug:20_state.js:545 boardFlags:20_state.js:546 onBoard:20_state.js:583 scopeOf:20_state.js:585 realmHolder:20_state.js:586 wonderRacing:20_state.js:588 wonderBuilding:20_state.js:590 wonderStart:20_state.js:591 wonderRace:20_state.js:594 scopeBlock:20_state.js:604 nextTier:20_state.js:609 autoFill:20_state.js:611 buildFilters:30_empire.js:8 monChip:30_empire.js:10 catSave:30_empire.js:17 catMode:30_empire.js:19 catAvail:30_empire.js:20 catSeg:30_empire.js:21 catCulKeep:30_empire.js:22 catGroups:30_empire.js:39 catRows:30_empire.js:41 pAvail:30_empire.js:45 legalCtx:30_empire.js:49 rawRes:30_empire.js:51 rawInSett:30_empire.js:52 rawOK:30_empire.js:56 pLegal:30_empire.js:57 pReqMiss:30_empire.js:63 autoHamlet:30_empire.js:66 autoOK:30_empire.js:67 effSpot:30_empire.js:69 facRide:30_empire.js:76 smartSid:30_empire.js:77 iAvail:30_empire.js:84 catUpkeep:30_empire.js:85 seg:30_empire.js:86 renderList:30_empire.js:88 wardPick:30_empire.js:143 wpRender:30_empire.js:145 wpPlace:30_empire.js:168 settLbl:30_empire.js:173 reqRow:30_empire.js:175 pursuitRow:30_empire.js:177 sub:30_empire.js:188 tip:30_empire.js:190 itemRow:30_empire.js:191 flash:30_empire.js:201 addInfraByName:30_empire.js:203 placeHolding:30_empire.js:210 addItem:30_empire.js:231 removeInstance:30_empire.js:242 addPursuitByName:30_empire.js:243 moveInstance:30_empire.js:244 infraReqToks:30_empire.js:260 infraTokStatus:30_empire.js:266 infraReqStatus:30_empire.js:280 infraValid:30_empire.js:285 infraActive:30_empire.js:292 infraReqLinesHTML:30_empire.js:293 masteryInfraToks:30_empire.js:297 masteryInfraHTML:30_empire.js:298 annotReqTok:30_empire.js:305 optionMet:30_empire.js:310 reqStatus:30_empire.js:318 instStatus:30_empire.js:325 chainLine:30_empire.js:332 simpleReq:30_empire.js:341 simpleReqHTML:30_empire.js:353 computeEarned:30_empire.js:361 atomEl:30_empire.js:379 FX_CHIP_TEST:30_empire.js:392 fxParts:30_empire.js:393 effectView:30_empire.js:395 atomsBlock:30_empire.js:406 render:30_empire.js:419 renderTopBar:30_empire.js:479 toggleEmpty:30_empire.js:526 sfxNorm:30_empire.js:535 sfxLabel:30_empire.js:536 settFx:30_empire.js:545 settFxPanel:30_empire.js:568 renderPursuitBoard:30_empire.js:575 wardPiles:30_empire.js:685 wardGrid:30_empire.js:697 unitFor:30_empire.js:724 tryMove:30_empire.js:729 scrollHost:30_empire.js:763 dropTargetAt:30_empire.js:764 clearDropHL:30_empire.js:772 armDrag:30_empire.js:773 beginDrag:30_empire.js:790 dragMove:30_empire.js:804 dragEnd:30_empire.js:816 herPicker:30_empire.js:825 factionFree:30_empire.js:836 setFaction:30_empire.js:840 facGearFlags:30_empire.js:849 armyTokHolder:30_empire.js:856 armyTokNamed:30_empire.js:857 factionFlags:30_empire.js:858 cultureFactions:30_empire.js:876 facOffered:30_empire.js:884 facPicker:30_empire.js:886 culSelectHTML:30_empire.js:904 domStripe:30_empire.js:910 cultureOf:30_empire.js:912 holdDom:30_empire.js:913 cultureSet:30_empire.js:917 cultureKeep:30_empire.js:922 cultureInfra:30_empire.js:925 derivedCulture:30_empire.js:930 nameCulture:30_empire.js:932 usedSettNames:30_empire.js:934 genPlaceName:30_empire.js:935 nameSett:30_empire.js:941 nameAllSetts:30_empire.js:943 renderFaction:30_empire.js:944 dukeCtl:30_empire.js:954 timerCtl:30_empire.js:955 placementSelect:30_empire.js:961 contribAcc:30_empire.js:976 contribChips:30_empire.js:979 accChips:30_empire.js:980 pursuitDetail:30_empire.js:988 quickChip:30_empire.js:1012 buildsIntoRow:30_empire.js:1016 nextLinksHTML:30_empire.js:1018 pursuitTable:30_empire.js:1026 pursuitCard:30_empire.js:1053 renderInfraSection:30_empire.js:1146 infraStacks:30_empire.js:1202 infraSummaryEl:30_empire.js:1211 armyUnlocks:30_empire.js:1223 unlockedShieldTiers:30_empire.js:1256 tierOK:30_empire.js:1260 gloss:30_empire.js:1261 glossLookup:30_empire.js:1270 openModal:30_empire.js:1279 closeModal:30_empire.js:1283 kwChipHTML:30_empire.js:1284 esc:30_empire.js:1285 inspectKeyword:30_empire.js:1286 inspectItem:30_empire.js:1308 optionList:30_empire.js:1331 loadoutFields:30_empire.js:1347 canDualWield:30_empire.js:1362 weaponForbids:30_empire.js:1364 fixWeaponNotes:30_empire.js:1366 renderArmy:30_empire.js:1369 armyCard:30_empire.js:1402 reqMet:30_empire.js:1497 lanceOnlyOK:30_empire.js:1501 weaponUnlockMet:30_empire.js:1502 moraleBase:30_empire.js:1504 armyUpkeep:30_empire.js:1505 moraleCap:30_empire.js:1507 moraleStanding:30_empire.js:1510 moralePO:30_empire.js:1513 effMorale:30_empire.js:1515 isRouted:30_empire.js:1516 armyVals:30_empire.js:1519 armyStats:30_empire.js:1527 noUpkeepTiers:30_empire.js:1554 holdsActive:30_empire.js:1556 playersWithout:30_empire.js:1558 calcMetrics:30_empire.js:1560 computeTotals:30_empire.js:1622 poTaxMod:30_empire.js:1653 taxDouble:30_empire.js:1658 winterTax:30_empire.js:1659 occupyTaxOnly:30_empire.js:1668 settInside:30_empire.js:1669 settTax:30_empire.js:1670 tradeIncome:30_empire.js:1673 tradeRaw:30_empire.js:1682 goldBreak:30_empire.js:1696 treasLive:30_empire.js:1710 fmtK:30_empire.js:1712 renderGlog:30_empire.js:1714 goldBreakHTML:30_empire.js:1721 goldBreakTxt:30_empire.js:1725 seasonNet:30_empire.js:1726 husbandryGoldFor:30_empire.js:1730 SEASON_DBL_TIER:30_empire.js:1734 tierGoldFor:30_empire.js:1736 seasonDblGold:30_empire.js:1740 SEASON_DBL_TYPE:30_empire.js:1741 boardMetrics:30_empire.js:1742 poCurKey:30_empire.js:1750 poBandName:30_empire.js:1751 poActiveKeys:30_empire.js:1753 poActiveEffects:30_empire.js:1755 poImmune:30_empire.js:1762 poDoubled:30_empire.js:1763 renderPO:30_empire.js:1765 planSave:35_plan.js:7 planKey:35_plan.js:8 planOf:35_plan.js:9 planSet:35_plan.js:10 planToggle:35_plan.js:11 planMove:35_plan.js:12 rawWhere:35_plan.js:14 planHStep:35_plan.js:17 planIStep:35_plan.js:29 planHPath:35_plan.js:39 planIPath:35_plan.js:48 planCtx:35_plan.js:49 planGoal:35_plan.js:51 planGoals:35_plan.js:60 planSteps:35_plan.js:62 planSort:35_plan.js:63 planAdd:35_plan.js:66 planPanel:35_plan.js:69 planPickHTML:35_plan.js:97 planMarks:35_plan.js:98 planCls:35_plan.js:99 curSeason:40_realm_data.js:4 stepSeason:40_realm_data.js:5 nextSeason:40_realm_data.js:6 seaLook:40_realm_data.js:9 seaLine:40_realm_data.js:11 playerOfBoard:40_realm_data.js:14 igVal:40_realm_data.js:15 eraIdx:40_realm_data.js:16 playerAtWar:40_realm_data.js:17 influenceRowsBase:40_realm_data.js:18 influenceRows:40_realm_data.js:49 influenceTotal:40_realm_data.js:54 poModRows:40_realm_data.js:58 totTipSimple:40_realm_data.js:89 totTip:40_realm_data.js:92 epSources:40_realm_data.js:103 topSuz:40_realm_data.js:116 royalMarriage:40_realm_data.js:119 sameAlliance:40_realm_data.js:124 poFloor:40_realm_data.js:127 applyPOFloor:40_realm_data.js:128 epRows:40_realm_data.js:129 poModTotal:40_realm_data.js:142 dpButtons:40_realm_data.js:143 renderDP:40_realm_data.js:146 dpSpend:40_realm_data.js:149 renderMiniStand:40_realm_data.js:156 renderInfluence:40_realm_data.js:170 renderPOMods:40_realm_data.js:174 siegeState:40_realm_data.js:186 siegeCalc:40_realm_data.js:187 siegeHTML:40_realm_data.js:205 realmTimers:40_realm_data.js:220 timerAddHTML:40_realm_data.js:221 boardTimerRows:40_realm_data.js:225 siegeResolveHTML:40_realm_data.js:231 activeTimersHTML:40_realm_data.js:239 seasonsHTML:40_realm_data.js:245 costsHTML:40_realm_data.js:248 wireDashExtras:40_realm_data.js:251 renderDash:40_realm_data.js:279 domBand:40_realm_data.js:282 mods:40_realm_data.js:285 diplo:40_realm_data.js:290 pk:40_realm_data.js:291 isVassal:40_realm_data.js:293 vassalsOf:40_realm_data.js:294 effPair:40_realm_data.js:295 pairOf:40_realm_data.js:298 pname:40_realm_data.js:299 allianceLabel:40_realm_data.js:300 pboard:40_realm_data.js:301 tradeBorderOK:40_realm_data.js:303 hasRoad:40_realm_data.js:304 eraRank:40_realm_data.js:307 allianceEra:40_realm_data.js:308 allianceOK:40_realm_data.js:309 pairFlags:40_realm_data.js:310 dStatus:40_realm_data.js:319 diploHTML:40_realm_data.js:323 wireDiplo:40_realm_data.js:380 newSide:50_battle.js:4 battle:50_battle.js:5 bq:50_battle.js:7 bqAdd:50_battle.js:8 bqSideName:50_battle.js:9 bqLoad:50_battle.js:12 sideHex:50_battle.js:15 bqStart:50_battle.js:19 hardcore:50_battle.js:23 banLO:50_battle.js:24 banEquip:50_battle.js:25 banWild:50_battle.js:26 banditArmy:50_battle.js:27 banditEra:50_battle.js:32 armBandits:50_battle.js:33 sideArmy:50_battle.js:40 blog:50_battle.js:45 d10:50_battle.js:46 seizeForced:50_battle.js:47 facCombat:50_battle.js:50 apMod:50_battle.js:63 sideUnlocks:50_battle.js:64 sideDomains:50_battle.js:70 standingFxOf:50_battle.js:71 hasArmyTok:50_battle.js:76 eqOptions:50_battle.js:77 eqCode:50_battle.js:88 eqNow:50_battle.js:91 dualOn:50_battle.js:95 eqWeapon:50_battle.js:96 tacAllowedW:50_battle.js:105 tacAllowedT:50_battle.js:111 tacAllowed:50_battle.js:114 tacTooEarly:50_battle.js:117 tacOK:50_battle.js:118 tacWhyNot:50_battle.js:119 randomTacticPool:50_battle.js:120 sideCalc:50_battle.js:123 pickKey:50_battle.js:275 viewerSide:50_battle.js:276 banditRollTactic:50_battle.js:294 sideSwaps:50_battle.js:298 mdLite:50_battle.js:313 fmtModLong:50_battle.js:315 fmtMod:50_battle.js:318 dieRow:50_battle.js:323 rollNeed:50_battle.js:325 rollHTML:50_battle.js:326 battleSprites:50_battle.js:333 datasheetHTML:50_battle.js:340 tacticPickHTML:50_battle.js:397 whatIf:50_battle.js:431 woundChance:50_battle.js:437 tacPair:50_battle.js:444 cellMotifs:50_battle.js:453 tacCells:50_battle.js:458 tacCardBody:50_battle.js:459 tacDetailHTML:50_battle.js:474 rollGuideHTML:50_battle.js:487 narrPl:50_battle.js:519 narrDisp:50_battle.js:520 narrate:50_battle.js:521 rollMeta:50_battle.js:527 chronicleHTML:50_battle.js:539 sideHTML:50_battle.js:542 fatigueImmune:50_battle.js:563 fatiguesNow:50_battle.js:565 sideNm:50_battle.js:567 bFlow:50_battle.js:572 actionsHTML:50_battle.js:612 battleOutcome:50_battle.js:642 resultHTML:50_battle.js:649 sideTile:50_battle.js:667 onHill:50_battle.js:668 onGrass:50_battle.js:669 seizeDefault:50_battle.js:671 seizeHTML:50_battle.js:672 bCmdHTML:50_battle.js:679 tacEdge:50_battle.js:686 tacticExplainHTML:50_battle.js:692 battleRulesHTML:50_battle.js:706 renderBattle:50_battle.js:710 battleGlanceHTML:50_battle.js:740 incoming:50_battle.js:769 glPush:50_battle.js:774 roll:50_battle.js:775 rollCore:50_battle.js:777 autoApplyCas:50_battle.js:853 cleaveN:50_battle.js:856 addCleave:50_battle.js:857 ripN:50_battle.js:858 addRip:50_battle.js:859 setPendCas:50_battle.js:861 pendCas:50_battle.js:862 ripCasN:50_battle.js:864 applyCasNow:50_battle.js:865 applyCas:50_battle.js:867 rollBreak:50_battle.js:869 rollBreakBtn:50_battle.js:872 endSkirmish:50_battle.js:874 endBattle:50_battle.js:895 wireBattle:50_battle.js:944 edictTimerLen:50_battle.js:1003 edictChoices:50_battle.js:1005 edictTotal:50_battle.js:1011 edictOwners:50_battle.js:1012 bumpRenown:50_battle.js:1013 edictCond:50_battle.js:1020 edictPlayersPct:50_battle.js:1027 uncontestedCount:50_battle.js:1031 edictHeld:50_battle.js:1033 edictPend:50_battle.js:1038 edictIsPending:50_battle.js:1039 edictDone:50_battle.js:1041 edictClosed:50_battle.js:1042 edictTick:50_battle.js:1044 edictTaken:50_battle.js:1051 edictWatch:50_battle.js:1052 checkEdicts:50_battle.js:1056 edictNewsText:50_battle.js:1064 edictBoardHTML:50_battle.js:1065 wireEdicts:50_battle.js:1094 currentEra:50_battle.js:1108 pMark:50_battle.js:1116 domTrackHTML:50_battle.js:1118 standingEffectsHTML:50_battle.js:1127 renderRenown:50_battle.js:1140 bfLine:52_battlefield.js:9 bfForm:52_battlefield.js:12 bfXY:52_battlefield.js:20 bfPlace:52_battlefield.js:23 bfTerrain:52_battlefield.js:34 bfSideInfo:52_battlefield.js:38 bfFigure:52_battlefield.js:49 bfGround:52_battlefield.js:53 bfCamp:52_battlefield.js:58 bfBuild:52_battlefield.js:62 bfMount:52_battlefield.js:74 bfUpdate:52_battlefield.js:80 bfGear:52_battlefield.js:109 bfFeedPaint:52_battlefield.js:114 bfToast:52_battlefield.js:117 bfDefLine:52_battlefield.js:123 bfReport:52_battlefield.js:129 bfSeen:52_battlefield.js:135 bfFx:52_battlefield.js:137 bfPick:52_battlefield.js:138 bfEffects:52_battlefield.js:147 aiOn:55_ai.js:6 aiProfile:55_ai.js:7 aiDriver:55_ai.js:9 aiNote:55_ai.js:10 aiCashOutlook:55_ai.js:15 aiMem:55_ai.js:20 aiRel:55_ai.js:21 aiRelAdd:55_ai.js:22 aiLearn:55_ai.js:24 aiStandSteps:55_ai.js:35 aiNextMonument:55_ai.js:41 aiStandGoals:55_ai.js:44 aiPickDomain:55_ai.js:57 aiSpendDP:55_ai.js:63 aiCouncilPick:55_ai.js:66 aiEraAllows:55_ai.js:78 aiFoe:55_ai.js:80 aiFriend:55_ai.js:82 aiHoldNet:55_ai.js:84 aiHoldPO:55_ai.js:87 aiHoldValue:55_ai.js:88 aiFaithFloor:55_ai.js:90 aiBuildPick:55_ai.js:91 aiImprovePick:55_ai.js:96 aiTreatyType:55_ai.js:101 aiTreatyAccept:55_ai.js:110 aiApplyTreaty:55_ai.js:121 aiOffensive:55_ai.js:131 aiKit:55_ai.js:132 aiGearRank:55_ai.js:143 aiOutfit:55_ai.js:149 aiMoveTargets:55_ai.js:161 aiMovable:55_ai.js:163 aiEngageSize:55_ai.js:168 aiMove:55_ai.js:170 aiPrioW:55_ai.js:199 aiScore:55_ai.js:200 aiSurvival:55_ai.js:203 aiPassChance:55_ai.js:210 aiArch:55_ai.js:218 aiStyle:55_ai.js:222 aiGearGain:55_ai.js:224 aiHoldTags:55_ai.js:231 aiActTags:55_ai.js:245 aiFaithNeed:55_ai.js:262 aiBanditThreat:55_ai.js:271 aiBanditNear:55_ai.js:278 aiSit:55_ai.js:281 aiCandidates:55_ai.js:291 aiIntents:55_ai.js:387 aiDeclare:55_ai.js:396 aiPlanFor:55_ai.js:402 aiPerform:55_ai.js:404 aiVoteWant:55_ai.js:423 aiVoteAll:55_ai.js:436 aiTacticEval:55_ai.js:449 aiTacticU:55_ai.js:455 aiTacticStance:55_ai.js:461 aiPickTactic:55_ai.js:467 aiBattleTick:55_ai.js:477 aiTick:55_ai.js:483 aiAfterRender:55_ai.js:499 mapClimate:60_map.js:17 mapPal:60_map.js:22 seaProfile:60_map.js:56 seaPropLook:60_map.js:58 tShift:60_map.js:63 seasonPal:60_map.js:71 tLum:60_map.js:74 tTone:60_map.js:76 tLighten:60_map.js:77 tGlyph:60_map.js:80 tSwatch:60_map.js:85 mapState:60_map.js:92 hexDist:60_map.js:93 decodeGrid:60_map.js:96 seedCode:60_map.js:106 generateMap:60_map.js:107 parseSeedCode:60_map.js:115 mapZoom:60_map.js:127 reachBonus:60_map.js:133 reachOwners:60_map.js:142 resShown:60_map.js:156 nodesMode:60_map.js:157 reachResources:60_map.js:159 settReachHexes:60_map.js:169 rawClaims:60_map.js:180 mapSprId:60_map.js:198 mapSprDefs:60_map.js:199 tMix:60_map.js:209 hStr:60_map.js:214 rng32:60_map.js:215 mapScatter:60_map.js:216 propPaths:60_map.js:238 pxSwatch:60_map.js:242 mapSpr:60_map.js:247 eqSVG:60_map.js:253 sprSVG:60_map.js:255 stIcon:60_map.js:264 armyGear:60_map.js:265 armyUFor:60_map.js:267 stDedup:60_map.js:272 stIconSVG:60_map.js:274 plateStatus:60_map.js:276 plateBox:60_map.js:277 mapPlate:60_map.js:279 settPlate:60_map.js:290 settBehind:60_map.js:301 settInsideMarks:60_map.js:305 mapBarHTML:60_map.js:320 terrOwners:60_map.js:331 terrFlags:60_map.js:333 unrestCamps:60_map.js:339 intrudersOf:60_map.js:341 settReach:60_map.js:345 settEcon:60_map.js:347 pillageOK:60_map.js:357 pillageCheck:60_map.js:358 pillageTargets:60_map.js:362 runPillage:60_map.js:365 armyStatus:60_map.js:378 mapMarkers:60_map.js:393 inspHTML:60_map.js:404 inspHead:60_map.js:407 inspCell:60_map.js:410 g:60_map.js:411 inspCan:60_map.js:412 inspArmy:60_map.js:413 settStatus:60_map.js:433 settStatusMarks:60_map.js:443 inspSett:60_map.js:447 envoyFor:60_map.js:483 settActionsHTML:60_map.js:486 armyMusterBtn:60_map.js:497 inspCamp:60_map.js:508 engageTargets:60_map.js:521 wireInsp:60_map.js:527 mapLayers:60_map.js:554 mapSVG:60_map.js:657 outlawReport:60_map.js:659 banditDomain:60_map.js:670 campKey:60_map.js:672 banditAutoHTML:60_map.js:674 armyName:60_map.js:683 syncMapTiers:60_map.js:685 mapLinkBad:60_map.js:692 mapLinksHTML:60_map.js:693 wireBanditAuto:60_map.js:704 banditAuto:60_map.js:710 BST:60_map.js:711 bLog:60_map.js:712 hk:60_map.js:714 mapSetts:60_map.js:715 cellPlayer:60_map.js:716 cellClaimed:60_map.js:718 pinNewCell:60_map.js:720 cellSett:60_map.js:726 mapArmies:60_map.js:729 cellArmy:60_map.js:730 cellTitle:60_map.js:733 byDist:60_map.js:737 isWild:60_map.js:741 wildZones:60_map.js:742 outlawZones:60_map.js:744 zoneOf:60_map.js:749 zoneOwners:60_map.js:750 outlawOwners:60_map.js:755 outlawOwner:60_map.js:757 outlawOf:60_map.js:759 campWild:60_map.js:761 wildCount:60_map.js:763 wildDone:60_map.js:764 autoDeploy:60_map.js:770 placeWildOutlaw:60_map.js:796 rescatterWild:60_map.js:818 pieceAura:60_map.js:822 wardMap:60_map.js:828 wardsOf:60_map.js:829 wardRoom:60_map.js:830 wardFill:60_map.js:832 wardCand:60_map.js:834 garrisonTargets:60_map.js:840 presHexes:60_map.js:848 wardAuto:60_map.js:852 wardPrune:60_map.js:862 wardMarks:60_map.js:864 campInRange:60_map.js:876 settleWhere:60_map.js:881 hexFree:60_map.js:885 terrainBlock:60_map.js:888 spawnCamp:60_map.js:893 growCamps:60_map.js:895 expandOutlaw:60_map.js:900 immuneUprising:60_map.js:903 banditTargetMods:60_map.js:904 cunningAction:60_map.js:906 endorsedExtort:60_map.js:907 banditSpared:60_map.js:910 banditAct:60_map.js:912 runBanditMechanics:60_map.js:947 banditSpeed:60_map.js:970 banditAuraList:60_map.js:972 banditRun:60_map.js:979 banditFlow:60_map.js:988 moveCamp:60_map.js:992 moveBandit:60_map.js:995 banditReturn:60_map.js:1003 banditSiegeTimer:60_map.js:1008 banditArmyKeys:60_map.js:1011 banditMoves:60_map.js:1012 banditSkims:60_map.js:1082 provinceCampExtort:60_map.js:1092 creditSkims:60_map.js:1097 envoyOutcome:60_map.js:1104 banditCunningHTML:60_map.js:1109 dieLookup:60_map.js:1126 terrainTablesHTML:60_map.js:1129 mapToolsHTML:60_map.js:1152 banditPanelHTML:60_map.js:1186 mapAsP:60_map.js:1202 mapLinkEl:60_map.js:1206 mapShow:60_map.js:1215 mapEditBlock:60_map.js:1218 mapGuard:60_map.js:1227 guarded:60_map.js:1229 mapCellClick:60_map.js:1231 wireMap:60_map.js:1269 srcKeys:70_rules.js:6 srcMatch:70_rules.js:13 srcHas:70_rules.js:14 srcRows:70_rules.js:16 bordersOf:70_rules.js:20 poCap:70_rules.js:24 poTextFloor:70_rules.js:25 siegeTextMods:70_rules.js:28 siegeWinterOK:70_rules.js:35 siegeDoubleOK:70_rules.js:36 envoyBlocked:70_rules.js:40 pietyBlocked:70_rules.js:41 actRestrict:70_rules.js:44 actRiders:70_rules.js:56 settById:70_rules.js:68 besiegeExempt:70_rules.js:70 settBesieged:70_rules.js:71 armySieging:70_rules.js:73 armyBesieged:70_rules.js:75 armyStateTags:70_rules.js:76 armyHeld:70_rules.js:86 armyBlocked:70_rules.js:89 immuneBlocked:70_rules.js:90 cellBlocked:70_rules.js:91 blockedMoveFails:70_rules.js:93 garrisonSizes:70_rules.js:97 hasGarrisons:70_rules.js:98 garrisonGear:70_rules.js:100 garrisonOf:70_rules.js:101 garrisonsOf:70_rules.js:105 garrisonCard:70_rules.js:106 standingOnceRows:70_rules.js:127 onceEffects:70_rules.js:129 onceState:70_rules.js:130 onceWindowNow:70_rules.js:134 onceHTML:70_rules.js:135 onceUse:70_rules.js:146 noteAdd:70_rules.js:155 recoupNote:70_rules.js:157 UPKEEP:70_rules.js:164 SUPPLY:70_rules.js:165 blackMarketReact:70_rules.js:168 extortReact:70_rules.js:175 cunningExtortMore:70_rules.js:181 extortGroup:70_rules.js:185 extortGold:70_rules.js:189 danegeldRows:70_rules.js:201 loans:70_rules.js:210 loanReqs:70_rules.js:211 loanTerms:70_rules.js:212 loanInterest:70_rules.js:215 loanOK:70_rules.js:217 lentThisTurn:70_rules.js:218 runLoans:70_rules.js:219 loanAmtIn:70_rules.js:225 loansHTML:70_rules.js:226 lendNow:70_rules.js:247 autoExtortRows:70_rules.js:267 extortSlots:70_rules.js:276 exTargets:70_rules.js:279 extortTargetRows:70_rules.js:280 extortCardHTML:70_rules.js:286 runAutoExtort:70_rules.js:306 firstDoubtRed:70_rules.js:334 fdState:70_rules.js:338 gainDoubt:70_rules.js:341 fdGold:70_rules.js:345 siegeOn:70_rules.js:349 endSettlementSieges:70_rules.js:350 besiegedCount:70_rules.js:351 pById:70_rules.js:352 nextId:70_rules.js:353 captureTransfer:70_rules.js:354 captureDestroy:70_rules.js:366 sackWards:70_rules.js:374 sackApply:70_rules.js:379 banditSack:70_rules.js:395 resolveRealm:70_rules.js:407 sackLocks:70_rules.js:414 armyHex:70_rules.js:418 settHex:70_rules.js:419 musterLimit:70_rules.js:420 musterTick:70_rules.js:428 musterStep:70_rules.js:431 hasMusterField:70_rules.js:438 charterFlags:70_rules.js:441 selArmy:70_rules.js:464 canMoveArmy:70_rules.js:465 armyBesiegeExempt:70_rules.js:467 canEnterSett:70_rules.js:469 armyInside:70_rules.js:471 enterCheck:70_rules.js:474 freeHexNear:70_rules.js:476 kickOut:70_rules.js:479 armiesInside:70_rules.js:482 terrPen:70_rules.js:484 terrBlocked:70_rules.js:485 terrWaterStop:70_rules.js:486 terrStrain:70_rules.js:487 provinceOf:70_rules.js:489 moveTraits:70_rules.js:491 speedOf:70_rules.js:494 hexNb:70_rules.js:526 auraSources:70_rules.js:530 moveRange:70_rules.js:540 moveInfo:70_rules.js:581 moveStops:70_rules.js:584 moveEndTriggers:70_rules.js:589 waterBlockers:70_rules.js:599 moveArmyTo:70_rules.js:603 moveOverlay:70_rules.js:626 movePanelHTML:70_rules.js:639 set:70_rules.js:650 computeAll:70_rules.js:651 sceneInfra:80_scene_shell.js:14 wardChains:80_scene_shell.js:20 sceneLots:80_scene_shell.js:27 renderEsBar:80_scene_shell.js:40 sceneArmies:80_scene_shell.js:48 renderScene:80_scene_shell.js:55 renderSettlements:80_scene_shell.js:172 lockTarget:80_scene_shell.js:235 lockBlock:80_scene_shell.js:244 adminUI:80_scene_shell.js:257 firstHostOpen:80_scene_shell.js:273 firstHostBtn:80_scene_shell.js:274 hudSign:80_scene_shell.js:280 hudData:80_scene_shell.js:281 hudTips:80_scene_shell.js:290 renderHUD:80_scene_shell.js:303 ageStripHTML:80_scene_shell.js:323 setupOn:80_scene_shell.js:337 renderSetup:80_scene_shell.js:338 checkedIn:80_scene_shell.js:367 checkinFD:80_scene_shell.js:368 checkinTxt:80_scene_shell.js:374 checkinHTML:80_scene_shell.js:375 setupHoldHTML:80_scene_shell.js:382 renderTurnStrip:80_scene_shell.js:407 syncBoardEndBtn:80_scene_shell.js:439 mnavSync:80_scene_shell.js:455 herName:80_scene_shell.js:465 herKey:80_scene_shell.js:466 lumOf:80_scene_shell.js:467 herMix:80_scene_shell.js:471 herN:80_scene_shell.js:473 herPaths:80_scene_shell.js:474 heraldOf:80_scene_shell.js:479 mapBanner:80_scene_shell.js:482 pTok:80_scene_shell.js:485 inboxItems:85_ux.js:10 renderInbox:85_ux.js:25 evIn:85_ux.js:44 hudPopBack:85_ux.js:59 hudPopFill:85_ux.js:61 hudPop:85_ux.js:88 hudPopClose:85_ux.js:89 renderChrome:85_ux.js:95 welcomeOn:86_welcome.js:11 welcomeLinks:86_welcome.js:15 welcomeClose:86_welcome.js:17 welcomeProfile:86_welcome.js:20 culHer:86_welcome.js:23 domDots:86_welcome.js:26 radarSVG:86_welcome.js:27 heritagesFor:86_welcome.js:35 seatCard:86_welcome.js:37 seatView:86_welcome.js:46 culDetail:86_welcome.js:51 profileView:86_welcome.js:64 welcomeRender:86_welcome.js:74 welcomeClick:86_welcome.js:86 undoSnap:90_app.js:5 undoRecord:90_app.js:7 undoRebase:90_app.js:13 undoScoped:90_app.js:14 undoApply:90_app.js:15 doUndo:90_app.js:32 doRedo:90_app.js:33 undoButtons:90_app.js:34 actSnap:90_app.js:47 actRebase:90_app.js:48 actJoin:90_app.js:50 actSchedule:90_app.js:53 fmtG:90_app.js:54 boardDiff:90_app.js:55 actFlush:90_app.js:87 gameAllowed:90_app.js:104 gameData:90_app.js:105 refreshGames:90_app.js:106 gameReplace:90_app.js:109 newGameState:90_app.js:114 isReady:90_app.js:140 readyCheck:90_app.js:141 gslug:90_app.js:155 kwify:90_app.js:168 wikiA:90_app.js:179 gkHtml:90_app.js:180 openFromHash:90_app.js:199 setLift:90_app.js:230 gkShow:90_app.js:239 gkHide:90_app.js:243 gkFor:90_app.js:244 chatHdr:90_app.js:303 chatTargets:90_app.js:309 chatParse:90_app.js:311 chatColor:90_app.js:319 chatLine:90_app.js:320 chatRender:90_app.js:324 chatSys:90_app.js:330 chatComplete:90_app.js:345
```
