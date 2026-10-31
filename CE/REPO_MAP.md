# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-10-31 · data VERSION `0.4.9.9.13-d10-S` · HEAD `2a416f43 2026-10-30`

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
    built/  (0 files)
    lab_out/  (730 files, generated/assets — not indexed)
    mapgen/  (18 files)
      maps/  (20 files)
    references/  (54 files)
      board/  (2 files)
        js/  (17 files)
      fonts/  (16 files, generated/assets — not indexed)
      games/  (2 files)
    tmp/  (0 files)
    wiki/  (0 files)
    worldbuilding/  (17 files)
  Combatv3/  (137 files)
    ask-the-bot/  (4 files)
    cards/  (17 files)
    fonts/  (14 files, generated/assets — not indexed)
    lab_out/  (36 files, generated/assets — not indexed)
    mapgen/  (8 files)
    wiki/  (83 files)
    worldbuilding/  (32 files)
  RenownWiki/  (94 files)
    mapgen/  (1 files)
  generators/  (22 files)
```

## 2. Source files

| File | Lines | Purpose |
|---|---|---|
| `REPO_MAP.md` | 810 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `renown_data_d10.py` | 4740 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `0.4.8 Updated Docs\equipment-0.4.8.csv` | 38 | columns: Name,Category,Tier,AP,Initiative,Save,Effects,Cost,To Hit,Endurance,Shaking,Specialization Unlock,Note |
| `0.4.8 Updated Docs\factions-0.4.8.csv` | 42 | columns: Inspiration,AI Name,Feel,Difficulty,Strength,Mechanic,Pair,Complement |
| `0.4.8 Updated Docs\specs-0.4.8.csv` | 107 | columns: Pursuits,Type,Unlock Requirement,Mastery Requirement,Innate Effects,Mastery Effect,Builds Into |
| `0.4.8.1\ESCALATION_master.md` | 214 | RENOWN — ESCALATION CAMPAIGN |
| `0.4.8.1\build_all.bat` | 83 | build_all.bat — regenerate everything downstream of renown_data.py. |
| `0.4.8.1\build_escalation.py` | 34 | build_escalation.py — fill {{TABLE:x}} markers in the authored Escalation |
| `0.4.8.1\build_escalation_campaign_pdf.py` | 506 | Build ESCALATION_CAMPAIGN.pdf. Portrait main doc + a merged LANDSCAPE two-player Domain Board page. |
| `0.4.8.1\card_copies.py` | 69 | card_copies.py — print-quantity logic for pursuit cards, driven by the spec |
| `0.4.8.1\card_sheet.py` | 634 | Renown — Specialization card sheet generator. |
| `0.4.8.1\economy.py` | 161 | economy.py — per-turn gold model for Renown builds, derived from renown_data. |
| `0.4.8.1\equipment.csv` | 39 | columns: Name,Category,Tier,AP,Initiative,Save,Effects,Cost,To Hit,Endurance,Shaking,Specialization Unlock,Note |
| `0.4.8.1\equipment_sheet.py` | 670 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `0.4.8.1\escalation_tables.py` | 60 | escalation_tables.py — generate the Escalation Campaign's data tables from |
| `0.4.8.1\export_csvs.py` | 73 | export_csvs.py — export renown_data.py to CSVs for spreadsheet VIEWING. |
| `0.4.8.1\faction_sheet.py` | 423 | Renown — Faction card sheet generator. |
| `0.4.8.1\gen_compendium.py` | 196 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `0.4.8.1\generate_cards.py` | 90 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `0.4.8.1\income_profile.py` | 117 | income_profile.py — classify a build's economy by SOURCE, tag its inflation |
| `0.4.8.1\loadouts.py` | 1915 | Loadout generator for the combat tournament. |
| `0.4.8.1\monument_viability.py` | 123 | monument_viability.py — for every Monument, test the two viability constraints: |
| `0.4.8.1\render_trees.py` | 92 | Render the Escalation talent trees from nodes_escalation.csv to a |
| `0.4.8.1\renown_combat.py` | 495 | Renown combat simulator. |
| `0.4.8.1\renown_data.py` | 1929 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `0.4.8.1\spec_tree_sheet.py` | 1036 | Renown — Specialization Tree renderer. |
| `0.4.8.1\specs.csv` | 107 | columns: Pursuits,Type,Unlock Requirement,Mastery Requirement,Innate Effects,Mastery Effect,Builds Into |
| `0.4.8.1\tactic_sheet.py` | 430 | Renown — Tactic card sheet generator (v3). |
| `0.4.8.1\two_monument_builds.py` | 118 | two_monument_builds.py — for the monument cap of 2, generate every viable |
| `0.4.8.1\verify_engine.py` | 253 | verify_engine.py — golden-case tests for the Escalation combat engine. |
| `CE\AUDIT_2026-10-30.md` | 90 | Consistency audit — 30 Oct 2026 |
| `CE\CHANGES.md` | 77 | Changes in this bundle |
| `CE\CLAUDE.md` | 69 | CLAUDE.md — Renown repo orientation (lives in `CE/`; paths below are relative to `CE/`) |
| `CE\COMPREHENSIVE_RULES_OUTLINE.md` | 180 | Renown — Comprehensive Rules: outline |
| `CE\ENVOY_WINDOW_REVIEW.md` | 89 | Envoy timing windows — review list |
| `CE\HOLDING_MECHANICS_AUDIT.md` | 54 | Holding Mechanics Audit |
| `CE\INFLUENCE_WORDING_AUDIT.md` | 76 | Influence / Authority wording audit |
| `CE\PLAYSTYLE_REVIEW.md` | 105 | Playstyle reference — fit review (SIMPLE build, 2026-10-30) |
| `CE\PRONOUN_WORDING_AUDIT.md` | 85 | "You / this player / the target" wording audit |
| `CE\REPO_MAP.md` | 954 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE\RULES_push.md` | 649 | Renown |
| `CE\RULES_push_simple.md` | 699 | Renown |
| `CE\RULES_reorganized_6.md` | 638 | Renown |
| `CE\SIMPLE_NODES.PY` | 1 |  |
| `CE\TASK8_NOTES.md` | 152 | claude_task_8 — what changed, open items |
| `CE\TASK9_NOTES.md` | 83 | claude_task_9 — Rules.docx pass: what changed, open items |
| `CE\build_all_CE.bat` | 531 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE\ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\infra.py` | 109 |  |
| `CE\keyword_bloat_v2.md` | 101 | Keyword Bloat — v2 |
| `CE\parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE\patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE\rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE\renown_data.py` | 3975 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d10.py` | 3975 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d10_legacy.py` | 5076 | renown_data_d10_legacy — FROZEN 2026-10-30. The legacy (SIMPLE=0) data: innate + mastery Pursuits, the |
| `CE\renown_data_d8.py` | 2801 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_server.bat` | 16 | renown_server.bat - (re)start the Renown board server in WSL. |
| `CE\repo_map.py` | 250 | repo_map.py — write REPO_MAP.md next to this file (CE/, beside CLAUDE.md): a generated index of the Renown repo for |
| `CE\run_tournament_d10.bat` | 108 | Renown d10 tournament runner  —  CE build |
| `CE\run_tournament_d10.py` | 131 | run_tournament_d10.py — run the Renown tournament against the d10 build. |
| `CE\sprites.py` | 6046 | sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene). |
| `CE\verify_d10.py` | 168 | verify_d10.py — prove the CE wiring is live before spending hours on a run. |
| `CE\.claude\launch.json` | 185 |  |
| `CE\Combatv4\analysis.py` | 2125 | Analysis module for tournament results. |
| `CE\Combatv4\batch_engine.py` | 1629 | Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays, |
| `CE\Combatv4\combat_kernel_d10.py` | 268 | combat_kernel.py — SHARED numba kernels for both combat engines. |
| `CE\Combatv4\combat_morale_d10.py` | 155 | combat_morale.py — SHARED morale phase for both combat engines (C2, subsystem 2). |
| `CE\Combatv4\combat_primitives_d10.py` | 147 | combat_primitives.py — SHARED rules-math layer for both combat engines (C2). |
| `CE\Combatv4\dice_config.py` | 116 | dice_config — single source for die size across both combat engines. |
| `CE\Combatv4\loadouts.py` | 1187 | Loadout generator for the combat tournament. |
| `CE\Combatv4\make_d10_data.py` | 172 | Generate renown_data_d10.py from renown_data_CE.py. |
| `CE\Combatv4\make_d10_engines.py` | 143 | Generate *_d10.py engine files with FACES parameterised. |
| `CE\Combatv4\normalized_matrix.py` | 277 | Normalized symmetric tactic matrix. |
| `CE\Combatv4\playstyles.py` | 784 | Playstyle module — playstyles drive tactic selection in combat. |
| `CE\Combatv4\renown_combat_d10.py` | 563 | Renown combat simulator. |
| `CE\Combatv4\run_tournament.py` | 197 | Standalone Renown tournament runner. |
| `CE\Combatv4\tactics_analysis.py` | 54 | Tactics analysis helpers for the Renown Combat Lab. |
| `CE\Combatv4\tournament_vec.py` | 356 | Vectorized tournament runner — same interface as tournament.py but ~4x faster |
| `CE\Combatv4\vectorized_combat_d10.py` | 1981 | Vectorized matchup runner. |
| `CE\Combatv4\shims\combat_kernel.py` | 15 | SHIM — do not edit. Redirects `import combat_kernel` to combat_kernel_d10. |
| `CE\Combatv4\shims\combat_morale.py` | 15 | SHIM — do not edit. Redirects `import combat_morale` to combat_morale_d10. |
| `CE\Combatv4\shims\combat_primitives.py` | 15 | SHIM — do not edit. Redirects `import combat_primitives` to combat_primitives_d10. |
| `CE\Combatv4\shims\renown_combat.py` | 15 | SHIM — do not edit. Redirects `import renown_combat` to renown_combat_d10. |
| `CE\Combatv4\shims\renown_data.py` | 15 | SHIM — do not edit. Redirects `import renown_data` to renown_data_d10. |
| `CE\Combatv4\shims\vectorized_combat.py` | 15 | SHIM — do not edit. Redirects `import vectorized_combat` to vectorized_combat_d10. |
| `CE\Simulator\analyse_sim.py` | 307 | analyse_sim.py — turn a simulator run (lab_out/sim/<TAG>/games.jsonl) into tables, a report and end screens. |
| `CE\Simulator\compare_runs.py` | 38 | compare_runs.py — Bandit and army headline numbers, side by side, for simulator runs in lab_out/sim/. |
| `CE\Simulator\probe_boards.js` | 21 | probe_boards.js — end-of-game board quality per player: Wards used / capacity, efficient riders (Holdings that use no Ward), |
| `CE\Simulator\probe_build.js` | 24 | probe_build.js — every few turns of one all-AI game: can each bot Build, and what beats Build in its scoring? |
| `CE\Simulator\run_sim.bat` | 84 | Renown game simulator  —  CE build |
| `CE\Simulator\sim_runner.js` | 82 | sim_runner.js — run many all-AI games in parallel (worker threads) and write every game's record to games.jsonl. |
| `CE\Simulator\trace_game.js` | 26 | trace_game.js — play one all-AI game and print, turn by turn, what each bot considered and chose. |
| `CE\Simulator\engine\dom_shim.js` | 81 | dom_shim.js — a do-nothing browser for running the settlement board's script headless. |
| `CE\Simulator\engine\load_board.js` | 38 | load_board.js — read the built settlement board once and hand back its script, ready to run in a sandbox. |
| `CE\Simulator\engine\sim_core.js` | 276 | sim_core.js — appended inside the settlement board's script (same scope: D, tSim, aiTick, roll, … are all in reach). |
| `CE\Tasks\Claude_task_9.txt` | 28 |  |
| `CE\Tasks\ENVOY_WINDOW_REVIEW.md` | 86 | Envoy timing windows — review list |
| `CE\Tasks\MAPGEN_COVERAGE.md` | 28 | Map generator — Holding / Monument coverage by region preset |
| `CE\Tasks\PROPOSALS_new_things.md` | 275 | Proposals — "New things to consider" + rules syntax pass |
| `CE\Tasks\REPO_MAP.md` | 870 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE\Tasks\SYNTAX_SWEEP.md` | 343 | Rules syntax sweep — canon applied |
| `CE\Tasks\TASK2_NOTES.md` | 82 | claude_task_2 — what changed, open questions |
| `CE\Tasks\TASK3_NOTES.md` | 43 | claude_task_3 — what changed, open questions |
| `CE\Tasks\TASK4_NOTES.md` | 139 | claude_task_4 — what changed, open questions |
| `CE\Tasks\TASK5_NOTES.md` | 74 | claude_task_5 — what changed, open items |
| `CE\Tasks\TASK6_NOTES.md` | 72 | claude_task_6 — what changed, open items |
| `CE\Tasks\TASK7_NOTES.md` | 36 | claude_task_7 — what changed, open items |
| `CE\Tasks\TASK8_NOTES.md` | 127 | claude_task_8 — what changed, open items |
| `CE\Tasks\WIKI_RULES_RESTRUCTURE.md` | 79 | Wiki rules — restructure draft (proposal, not applied) |
| `CE\Tasks\claude_task.txt` | 85 |  |
| `CE\Tasks\claude_task_2.txt` | 68 |  |
| `CE\Tasks\claude_task_3.txt` | 24 |  |
| `CE\Tasks\claude_task_4.txt` | 44 |  |
| `CE\Tasks\claude_task_5.txt` | 23 |  |
| `CE\Tasks\claude_task_6.txt` | 51 |  |
| `CE\Tasks\claude_task_7.txt` | 18 |  |
| `CE\Tasks\claude_task_8.txt` | 17 |  |
| `CE\ask-the-bot\equipment_table.csv` | 38 | columns: Item,Type,Tier,AP_or_Save,Init,Keywords |
| `CE\ask-the-bot\factions_table.csv` | 41 | columns: Faction,Difficulty,Strength,Mechanic |
| `CE\ask-the-bot\renown_faq.txt` | 514 |  |
| `CE\mapgen\app_shell.html` | 732 | Renown — Map Generator |
| `CE\mapgen\build_board.py` | 451 | build_board.py - print-and-tape Renown board from a procedural map. |
| `CE\mapgen\build_mapapp.py` | 212 | build_mapapp.py - assemble renown-maps.html from its sources. |
| `CE\mapgen\gen.js` | 2005 | gen.js — Renown regional map generator, JS port. |
| `CE\mapgen\gen_cli.js` | 20 | gen_cli.js - run gen.js from Python (mapgen_regional.generate_region), so the app, the settlement |
| `CE\mapgen\gen_settlement_board.py` | 5268 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE\mapgen\hexgen.py` | 258 | hexgen.py — generate the Renown hex asset set as standalone SVGs. |
| `CE\mapgen\hexmap.py` | 85 | hexmap.py — the territory graph (C1). |
| `CE\mapgen\hexstyle.py` | 270 | hexstyle.py - the ONE source for how a board looks. |
| `CE\mapgen\mapgen.py` | 908 | mapgen.py — procedural Renown map generator. |
| `CE\mapgen\mapgen_regional.py` | 254 | mapgen_regional.py — preset-driven map generation for Renown, through gen.js. |
| `CE\mapgen\presets.js` | 1609 | presets.js - GENERATED from region_presets.py. Do not hand-edit. */ |
| `CE\mapgen\region_presets.py` | 514 | region_presets.py — regional map-generation presets for Renown. |
| `CE\mapgen\renown-maps.html` | 4344 | Renown — Map Generator |
| `CE\references\build_compendium.js` | 133 | build_compendium.js — render the Compendium .docx from renown_data JSON, |
| `CE\references\build_compendium.py` | 394 | build_compendium2.py — redesigned Compendium .docx from compendium_data.json. |
| `CE\references\build_wiki.py` | 1644 | build_wiki.py — multi-page linked HTML wiki from RULES.md + renown_data. |
| `CE\references\card_copies.py` | 68 | card_copies.py — print-quantity logic for pursuit cards, driven by the spec |
| `CE\references\card_sheet.py` | 679 | Renown — Specialization card sheet generator. |
| `CE\references\ce_paths.py` | 123 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\references\combat_sheet.py` | 352 | combat_sheet.py — Renown combat quick-reference (print & laminate). |
| `CE\references\combine_docx.py` | 257 | combine_docx.py — append the Compendium after the Rules doc as one book: |
| `CE\references\compendium_data.json` | 3273 |  |
| `CE\references\display_pdf.py` | 90 | display_pdf.py — NAME_DISPLAY for every reportlab sheet (cards, tiles, equipment, combat). |
| `CE\references\docx_tables.py` | 688 | docx_tables.py — generate Word table fragments (OOXML) from renown_data. |
| `CE\references\domain_board.py` | 341 | domain_board.py - landscape Domain Standing Board. |
| `CE\references\effect_registry.py` | 391 | effect_registry.py -- every rules-text pattern the settlement board acts on, matched once at build time. |
| `CE\references\equipment_sheet.py` | 691 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `CE\references\faction_sheet.py` | 447 | Renown — Faction card sheet generator. |
| `CE\references\faq_export.py` | 439 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `CE\references\gen_compendium.py` | 185 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `CE\references\gen_layout.py` | 374 | gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data. |
| `CE\references\gen_layout_roots.py` | 123 | gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it. |
| `CE\references\gen_settlement_board.py` | 1059 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE\references\generate_cards.py` | 93 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `CE\references\host_sheet.py` | 452 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `CE\references\infra_board.py` | 134 | infra_board.py - landscape Infrastructure Board. |
| `CE\references\keyword_audit.py` | 96 | Exact per-strike-die model of the Renown CE strike chain (rules text as written), |
| `CE\references\layout.json` | 1421 |  |
| `CE\references\layout_roots.json` | 1372 |  |
| `CE\references\layout_simple.json` | 1536 |  |
| `CE\references\lobby.html` | 102 | Renown |
| `CE\references\md_to_docx.py` | 342 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `CE\references\package-lock.json` | 205 |  |
| `CE\references\package.json` | 6 |  |
| `CE\references\parity_efx.js` | 54 | parity_efx.js — replays effect_registry.py's patterns with JavaScript RegExp, the way the board used to read text at |
| `CE\references\patch_pursuit_domains.py` | 58 | patch_pursuit_domains.py |
| `CE\references\playstyle_reference.py` | 463 | playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture). |
| `CE\references\pursuit_tiles.py` | 284 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `CE\references\reference_sheets.py` | 873 | Renown — Reference sheet generators. |
| `CE\references\render_tree.py` | 272 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `CE\references\rule_numbers.py` | 267 | rule_numbers.py — MTG-style rule numbers for the rules markdown, computed at render time. |
| `CE\references\server.py` | 679 | Renown settlement-board server  —  stdlib only, no pip installs. |
| `CE\references\settlement_board.html` | — | generated HTML (2010 KB) |
| `CE\references\settlement_mats.py` | 302 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `CE\references\spec_tree_sheet.py` | 1184 | Renown — Specialization Tree renderer. |
| `CE\references\svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `CE\references\sync_derived.py` | 88 | sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES. |
| `CE\references\tactic_sheet.py` | 446 | Renown — Tactic card sheet generator (v3). |
| `CE\references\wiki_markers.py` | 291 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
| `CE\references\world.txt` | 1517 |  |
| `CE\references\worldtxt.py` | 328 | worldtxt.py — parse the hand-maintained world.txt lore book into structured |
| `CE\references\board\body.html` | 216 |  |
| `CE\references\board\js\00_core.js` | 51 | __DATA__*/; |
| `CE\references\board\js\10_table.js` | 958 | ===================== TABLE: seating, Council & Envoy phases ===================== |
| `CE\references\board\js\15_realm.js` | 499 | ===================== REALM: the play surface ===================== |
| `CE\references\board\js\16_tally.js` | 132 | ===================== INTRIGUE & TALLY PHASES (RULES: Envoy Phase steps 3 and 5) ===================== |
| `CE\references\board\js\17_diplo_step.js` | 131 | ===================== DIPLOMACY STEP (PHASE_REFORM): offers between players ===================== |
| `CE\references\board\js\20_state.js` | 607 | ---- state: multiplayer dashboard ---- |
| `CE\references\board\js\30_empire.js` | 1723 | ---- catalog ---- |
| `CE\references\board\js\40_realm_data.js` | 397 | ---- Dashboards view ---- |
| `CE\references\board\js\50_battle.js` | 1024 | ---- Battle ---- |
| `CE\references\board\js\52_battlefield.js` | 183 | ---- Battle field: a top-down view between the two datasheets ---- |
| `CE\references\board\js\55_ai.js` | 499 | ---- AI players: culture-driven bots for seats marked AI (and, later, the headless simulator) ---- |
| `CE\references\board\js\60_map.js` | 1174 | ---- Map view ---- |
| `CE\references\board\js\70_rules.js` | 614 | ===================== EFFECT PLUMBING: the effect registry (references/effect_registry.py) ===================== |
| `CE\references\board\js\80_scene_shell.js` | 483 | ---- pixel scene: every settlement of the active player, drawn from sprites.py (every theme) ---- |
| `CE\references\board\js\85_ux.js` | 102 | ===================== CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper ===================== |
| `CE\references\board\js\86_welcome.js` | 108 | ===================== WELCOME: seats + profile (server games) ===================== |
| `CE\references\board\js\90_app.js` | 382 | ===================== UNDO / REDO ===================== |
| `CE\worldbuilding\book.json` | 2070 |  |
| `CE\worldbuilding\build_docx.js` | 147 | map image: RENOWN_MAP (set by build_all_CE.bat), else map7.png beside this |
| `CE\worldbuilding\draft.txt` | 220 |  |
| `CE\worldbuilding\gen_book_json.py` | 214 | gen_book_json.py |
| `CE\worldbuilding\gen_cultures.py` | 1014 | gen_cultures.py |
| `CE\worldbuilding\gen_draft.py` | 50 | gen_draft.py |
| `CE\worldbuilding\gen_intro.py` | 62 | gen_intro.py |
| `CE\worldbuilding\gen_pdf.py` | 422 | gen_pdf.py |
| `CE\worldbuilding\intro.txt` | 270 |  |
| `CE\worldbuilding\package-lock.json` | 205 |  |
| `CE\worldbuilding\package.json` | 6 |  |
| `CE\worldbuilding\renown_worldlore.py` | 3746 | renown_worldlore.py |
| `CE\worldbuilding\world.txt` | 1481 |  |
| `CE\worldbuilding\world_design.txt` | 2341 |  |
| `Combatv3\BATCH_STATUS.md` | 963 | v3 Batched Engine — Status |
| `Combatv3\ESCALATION_CAMPAIGN.md` | 260 | RENOWN — ESCALATION CAMPAIGN |
| `Combatv3\ESCALATION_master.md` | 211 | RENOWN — ESCALATION CAMPAIGN |
| `Combatv3\RULES.md` | 839 | Renown |
| `Combatv3\RULES_reorganized.md` | 636 | Renown |
| `Combatv3\RULES_reorganized_2.md` | 598 | Renown |
| `Combatv3\RULES_reorganized_5.md` | 633 | Renown |
| `Combatv3\RULES_reorganized_6.md` | 648 | Renown |
| `Combatv3\analysis.py` | 2108 | Analysis module for tournament results. |
| `Combatv3\batch_engine (2).py` | 1519 | Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays, |
| `Combatv3\batch_engine.py` | 1549 | Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays, |
| `Combatv3\build_all.bat` | 249 | build_all.bat - regenerate everything downstream of renown_data.py. |
| `Combatv3\build_compendium.js` | 133 | build_compendium.js — render the Compendium .docx from renown_data JSON, |
| `Combatv3\build_compendium.py` | 368 | build_compendium.py — render the Compendium .docx from compendium_data.json, |
| `Combatv3\build_docs.py` | 74 | build_docs.py — fill {{TABLE:name}}, {{GLOSSARY}}, and {{DEF:term}} markers in an |
| `Combatv3\build_escalation.py` | 34 | build_escalation.py — fill {{TABLE:x}} markers in the authored Escalation |
| `Combatv3\build_escalation_campaign_pdf.py` | 462 | Build ESCALATION_CAMPAIGN.pdf. Portrait main doc + a merged LANDSCAPE two-player Domain Board page. |
| `Combatv3\build_talent_tree5.py` | 360 | build_talent_tree.py - pursuit tech tree as a series of SEPARATE flowcharts. |
| `Combatv3\build_wiki.py` | 1418 | build_wiki.py — multi-page linked HTML wiki from RULES.md + renown_data. |
| `Combatv3\card_copies.py` | 69 | card_copies.py — print-quantity logic for pursuit cards, driven by the spec |
| `Combatv3\card_sheet.py` | 669 | Renown — Specialization card sheet generator. |
| `Combatv3\combat_kernel.py` | 234 | combat_kernel.py — SHARED numba kernels for both combat engines. |
| `Combatv3\combat_morale.py` | 152 | combat_morale.py — SHARED morale phase for both combat engines (C2, subsystem 2). |
| `Combatv3\combat_primitives.py` | 149 | combat_primitives.py — SHARED rules-math layer for both combat engines (C2). |
| `Combatv3\combat_sheet.py` | 340 | combat_sheet.py — Renown combat quick-reference (print & laminate). |
| `Combatv3\combine_docx.py` | 194 | combine_docx.py — append the Compendium after the Rules doc as one book: |
| `Combatv3\compendium_data.json` | 3353 |  |
| `Combatv3\docx_tables.py` | 403 | docx_tables.py — generate Word table fragments (OOXML) from renown_data. |
| `Combatv3\domain_board.py` | 315 | domain_board.py - landscape Domain Standing Board. |
| `Combatv3\economy.py` | 161 | economy.py — per-turn gold model for Renown builds, derived from renown_data. |
| `Combatv3\equipment.csv` | 39 | columns: Name,Category,Tier,AP,Initiative,Save,Effects,Cost,To Hit,Endurance,Shaking,Specialization Unlock,Note |
| `Combatv3\equipment_sheet.py` | 683 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `Combatv3\escalation_tables.py` | 60 | escalation_tables.py — generate the Escalation Campaign's data tables from |
| `Combatv3\export_csvs.py` | 73 | export_csvs.py — export renown_data.py to CSVs for spreadsheet VIEWING. |
| `Combatv3\faction_sheet.py` | 436 | Renown — Faction card sheet generator. |
| `Combatv3\factions_table.csv` | 42 | columns: Faction,Difficulty,Strength,Mechanic |
| `Combatv3\faq_export.py` | 425 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `Combatv3\gauntlet_run.bat` | 17 | Fixed-gauntlet power-level run — tests EVERY build vs a fixed panel (linear, fast). |
| `Combatv3\gauntlet_run.py` | 154 | Fixed-gauntlet power-level runner. |
| `Combatv3\gen_compendium.py` | 197 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `Combatv3\gen_escalation_nodes.py` | 45 | gen_escalation_nodes.py — regenerate nodes_escalation.csv from renown_data.NODES |
| `Combatv3\gen_nodes.py` | 14 | RETIRED — renown_data.py is now the hand-edited master for the node graph. |
| `Combatv3\generate_cards.bat` | 31 | Renown card generator — regenerates every deck from renown_data.py. |
| `Combatv3\generate_cards.py` | 90 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `Combatv3\generate_rules_truth.py` | 231 | generate_rules_truth.py — emits RULES_TRUTH.md, the single source of truth for Renown combat |
| `Combatv3\horde_mode.py` | 569 | Horde mode — multi-battle limit testing for armies. |
| `Combatv3\host_sheet.py` | 446 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `Combatv3\income_profile.py` | 117 | income_profile.py — classify a build's economy by SOURCE, tag its inflation |
| `Combatv3\infra_board.py` | 127 | infra_board.py - landscape Infrastructure Board. |
| `Combatv3\infra_strip.py` | 148 | infra_strip.py - infrastructure ownership grid. Names as column headers once |
| `Combatv3\layout.json` | 1403 |  |
| `Combatv3\layout_manifest.json` | 1403 |  |
| `Combatv3\loadouts.py` | 1782 | Loadout generator for the combat tournament. |
| `Combatv3\loadouts2.py` | 1283 | Loadout generator for the combat tournament. |
| `Combatv3\mapgen.py` | 795 | mapgen.py — procedural Renown map generator. |
| `Combatv3\md_to_docx.py` | 223 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `Combatv3\monument_viability.py` | 123 | monument_viability.py — for every Monument, test the two viability constraints: |
| `Combatv3\new 3.txt` | 91 |  |
| `Combatv3\nodes_escalation.csv` | 28 | columns: Name,Domain,Standing,Rank,Effect,Requires_All,Requires_Any,Extra_Req,Monument |
| `Combatv3\normalized_matrix.py` | 277 | Normalized symmetric tactic matrix. |
| `Combatv3\parity_harness.py` | 27 | parity_harness.py |
| `Combatv3\patch_pursuit_domains.py` | 57 | patch_pursuit_domains.py |
| `Combatv3\playstyle_reference.py` | 218 | playstyle_reference.py - one-page (landscape Letter) playstyle reference card. |
| `Combatv3\playstyles.py` | 784 | Playstyle module — playstyles drive tactic selection in combat. |
| `Combatv3\pursuit_review.html` | 122 | Renown Pursuit Review |
| `Combatv3\pursuit_review.py` | 196 | pursuit_review.py — generate a single self-contained HTML page for reviewing |
| `Combatv3\pursuit_tiles.py` | 267 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `Combatv3\reference_sheets.py` | 886 | Renown — Reference sheet generators. |
| `Combatv3\render_tree.py` | 249 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `Combatv3\render_trees.py` | 92 | Render the Escalation talent trees from nodes_escalation.csv to a |
| `Combatv3\render_trees_2x2.py` | 211 | render_trees_2x2.py — render the Escalation talent tree as FOUR per-domain |
| `Combatv3\renown_combat.py` | 562 | Renown combat simulator. |
| `Combatv3\renown_data.py` | 2574 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `Combatv3\renown_data_ce.py` | 2681 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `Combatv3\renown_faq.txt` | 372 |  |
| `Combatv3\retinue_gear_leaderboard.py` | 108 | ============================================================================ |
| `Combatv3\routes_DISCARDED.py` | 158 | routes.py - new-player route sheet. |
| `Combatv3\run_tournament.bat` | 39 | Renown tournament runner — edit the values below, then double-click or run from cmd. |
| `Combatv3\run_tournament.py` | 197 | Standalone Renown tournament runner. |
| `Combatv3\sensitivity_sweep.py` | 226 | Input x Output sensitivity sweep for Renown combat. |
| `Combatv3\settlement_mats.py` | 290 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `Combatv3\spec_tree_sheet.py` | 1160 | Renown — Specialization Tree renderer. |
| `Combatv3\svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `Combatv3\tactic_eval.py` | 159 | Tactic matrix evaluator — per-statline 6x6 (Fall Back excluded). |
| `Combatv3\tactic_init_threshold.py` | 156 | Threshold-conditioned tactic eval — where the gear->init coupling ACTUALLY decides games. |
| `Combatv3\tactic_pruning.py` | 147 | Tactic-pruning eval (marginal-edge version) — does EQUIPMENT shape which tactics are worth picking? |
| `Combatv3\tactic_sheet.py` | 443 | Renown — Tactic card sheet generator (v3). |
| `Combatv3\tactics_analysis.py` | 54 | Tactics analysis helpers for the Renown Combat Lab. |
| `Combatv3\tournament_vec.py` | 359 | Vectorized tournament runner — same interface as tournament.py but ~4x faster |
| `Combatv3\two_monument_builds.py` | 118 | two_monument_builds.py — for the monument cap of 2, generate every viable |
| `Combatv3\vectorized_combat.py` | 1831 | Vectorized matchup runner. |
| `Combatv3\verify_engine.py` | 253 | verify_engine.py — golden-case tests for the Escalation combat engine. |
| `Combatv3\verify_loadouts.py` | 228 | Local verification: does the optimized loadouts.py produce a pool IDENTICAL to the |
| `Combatv3\verify_step1.py` | 31 | Step-1 gate: run on YOUR machine with numba ON, after wiping the cache. |
| `Combatv3\verify_step2.py` | 33 | Step-2 gate: run on YOUR machine with numba ON, cache wiped. |
| `Combatv3\wiki_markers.py` | 211 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
| `Combatv3\worldtxt.py` | 328 | worldtxt.py — parse the hand-maintained world.txt lore book into structured |
| `Combatv3\ask-the-bot\equipment_table.csv` | 37 | columns: Item,Type,Tier,AP_or_Save,Init,Keywords |
| `Combatv3\ask-the-bot\factions_table.csv` | 42 | columns: Faction,Difficulty,Strength,Mechanic |
| `Combatv3\ask-the-bot\faq_export.py` | 350 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `Combatv3\ask-the-bot\renown_faq.txt` | 465 |  |
| `Combatv3\mapgen\build_board.py` | 294 | build_board.py - print-and-tape Renown board from a procedural map. |
| `Combatv3\mapgen\hexgen.py` | 281 | hexgen.py — generate the Renown hex asset set as standalone SVGs. |
| `Combatv3\wiki\actions-ref.html` | 18 | Actions — Renown |
| `Combatv3\wiki\bandits-ref.html` | 18 | Bandits — Renown |
| `Combatv3\wiki\domain-board-ref.html` | 18 | Domain Board — Renown |
| `Combatv3\wiki\domain-cunning.html` | 18 | Cunning Pursuits — Renown |
| `Combatv3\wiki\domain-industry.html` | 18 | Industry Pursuits — Renown |
| `Combatv3\wiki\domain-piety.html` | 18 | Piety Pursuits — Renown |
| `Combatv3\wiki\domain-prowess.html` | 18 | Prowess Pursuits — Renown |
| `Combatv3\wiki\economy-ref.html` | 18 | Economy Reference — Renown |
| `Combatv3\wiki\edicts-ref.html` | 18 | Edicts — Renown |
| `Combatv3\wiki\envoy-outcomes-ref.html` | 18 | Envoy Outcomes — Renown |
| `Combatv3\wiki\equipment-ref.html` | 18 | Equipment — Renown |
| `Combatv3\wiki\eras-ref.html` | 18 | Eras — Renown |
| `Combatv3\wiki\escalation-pursuits.html` | 18 | Escalation Combat Pursuits — Renown |
| `Combatv3\wiki\escalation-rules.html` | 18 | Escalation Battle Rules — Renown |
| `Combatv3\wiki\escalation.html` | 18 | Escalation Campaign — Renown |
| `Combatv3\wiki\factions.html` | 18 | Factions — Renown |
| `Combatv3\wiki\glossary.html` | 18 | Glossary — Renown |
| `Combatv3\wiki\index.html` | 18 | Renown Rules — Renown |
| `Combatv3\wiki\infrastructure-ref.html` | 18 | Infrastructure — Renown |
| `Combatv3\wiki\keywords-ref.html` | 18 | Combat Keywords — Renown |
| `Combatv3\wiki\lore-ages.html` | 18 | The Timeline — Renown |
| `Combatv3\wiki\lore-cultures.html` | 18 | The Fifteen — Renown |
| `Combatv3\wiki\lore-darkness.html` | 18 | The Age of Darkness — Renown |
| `Combatv3\wiki\lore-map.html` | 18 | The Map — Renown |
| `Combatv3\wiki\lore.html` | 18 | The World of Vaelohk — Renown |
| `Combatv3\wiki\paths.html` | 18 | Build Paths — Renown |
| `Combatv3\wiki\public-order-ref.html` | 18 | Public Order — Renown |
| `Combatv3\wiki\pursuits.html` | 18 | Pursuits — Renown |
| `Combatv3\wiki\reference-tables.html` | 18 | Reference Tables — Renown |
| `Combatv3\wiki\rules-action-mechanics.html` | 37 | Action Mechanics — Renown |
| `Combatv3\wiki\rules-armies.html` | 34 | Armies — Renown |
| `Combatv3\wiki\rules-bandits.html` | 55 | Bandits — Renown |
| `Combatv3\wiki\rules-battle-phase.html` | 58 | Battle Phase — Renown |
| `Combatv3\wiki\rules-core-principles.html` | 68 | Core Principles — Renown |
| `Combatv3\wiki\rules-council-phase.html` | 20 | Council Phase — Renown |
| `Combatv3\wiki\rules-cunning-actions.html` | 22 | Cunning Actions — Renown |
| `Combatv3\wiki\rules-diplomacy-actions.html` | 20 | Diplomacy Actions — Renown |
| `Combatv3\wiki\rules-diplomacy-treaties.html` | 42 | Diplomacy &amp; Treaties — Renown |
| `Combatv3\wiki\rules-domains-standings.html` | 26 | Domains &amp; Standings — Renown |
| `Combatv3\wiki\rules-empire-phase.html` | 52 | Empire Phase — Renown |
| `Combatv3\wiki\rules-envoy-phase.html` | 21 | Envoy Phase — Renown |
| `Combatv3\wiki\rules-industry-actions.html` | 21 | Industry Actions — Renown |
| `Combatv3\wiki\rules-influence.html` | 21 | Influence — Renown |
| `Combatv3\wiki\rules-infrastructure.html` | 28 | Infrastructure — Renown |
| `Combatv3\wiki\rules-introduction.html` | 64 | Introduction — Renown |
| `Combatv3\wiki\rules-piety-actions.html` | 19 | Piety Actions — Renown |
| `Combatv3\wiki\rules-player-setup.html` | 26 | Player Setup — Renown |
| `Combatv3\wiki\rules-prowess-actions.html` | 19 | Prowess Actions — Renown |
| `Combatv3\wiki\rules-public-order.html` | 24 | Public Order — Renown |
| `Combatv3\wiki\rules-renown.html` | 19 | Renown — Renown |
| `Combatv3\wiki\rules-rest-phase.html` | 39 | Rest Phase — Renown |
| `Combatv3\wiki\rules-seasons.html` | 20 | Seasons — Renown |
| `Combatv3\wiki\rules-settlements.html` | 28 | Settlements — Renown |
| `Combatv3\wiki\rules-siege-warfare.html` | 54 | Siege Warfare — Renown |
| `Combatv3\wiki\rules-table-setup.html` | 24 | Table Setup — Renown |
| `Combatv3\wiki\rules-territory-terrain.html` | 22 | Territory &amp; Terrain — Renown |
| `Combatv3\wiki\rules-the-turn.html` | 20 | The Turn — Renown |
| `Combatv3\wiki\rules-trade-income.html` | 34 | Trade &amp; Income — Renown |
| `Combatv3\wiki\rules-treasury-upkeep.html` | 29 | Treasury &amp; Upkeep — Renown |
| `Combatv3\wiki\search.js` | 7 |  |
| `Combatv3\wiki\seasons-ref.html` | 18 | Seasons — Renown |
| `Combatv3\wiki\settlements-ref.html` | 18 | Settlements — Renown |
| `Combatv3\wiki\standing-established.html` | 18 | Established Tier — Renown |
| `Combatv3\wiki\standing-rising.html` | 18 | Rising Tier — Renown |
| `Combatv3\wiki\standing-sovereign.html` | 18 | Sovereign Tier — Renown |
| `Combatv3\wiki\systems-ref.html` | 18 | Timers, Influence &amp; PO — Renown |
| `Combatv3\wiki\tactic-matrix-ref.html` | 18 | Tactic Matrix — Renown |
| `Combatv3\wiki\terrain-ref.html` | 18 | Terrain &amp; Movement — Renown |
| `Combatv3\wiki\treaties-ref.html` | 18 | Treaties &amp; Alliances — Renown |
| `Combatv3\wiki\turn-sequence.html` | 18 | Turn Sequence — Renown |
| `Combatv3\wiki\type-civic.html` | 18 | Civic — Renown |
| `Combatv3\wiki\type-craft.html` | 18 | Craft — Renown |
| `Combatv3\wiki\type-energy.html` | 18 | Energy — Renown |
| `Combatv3\wiki\type-husbandry.html` | 18 | Husbandry — Renown |
| `Combatv3\wiki\type-monument.html` | 19 | Monument — Renown |
| `Combatv3\wiki\type-power.html` | 18 | Power — Renown |
| `Combatv3\wiki\type-raw-materials.html` | 18 | Raw Materials — Renown |
| `Combatv3\wiki\type-secrecy.html` | 18 | Secrecy — Renown |
| `Combatv3\wiki\ui.js` | 26 | ── theme toggle (head script already applied the stored/system theme) ── |
| `Combatv3\wiki\wonders-ref.html` | 18 | Wonders — Renown |
| `Combatv3\worldbuilding\New Text Document.txt` | 1 |  |
| `Combatv3\worldbuilding\book.json` | 1805 |  |
| `Combatv3\worldbuilding\build_docx.js` | 142 | ---- title |
| `Combatv3\worldbuilding\coastline.py` | 54 | coastline.py - metaball landmass outline. Sum of a few offset circular fields; |
| `Combatv3\worldbuilding\cultures.txt` | 791 |  |
| `Combatv3\worldbuilding\draft.txt` | 220 |  |
| `Combatv3\worldbuilding\gen_book_json.py` | 214 | gen_book_json.py |
| `Combatv3\worldbuilding\gen_cultures.py` | 1014 | gen_cultures.py |
| `Combatv3\worldbuilding\gen_draft.py` | 50 | gen_draft.py |
| `Combatv3\worldbuilding\gen_intro.py` | 62 | gen_intro.py |
| `Combatv3\worldbuilding\gen_pdf.py` | 416 | gen_pdf.py |
| `Combatv3\worldbuilding\intro.txt` | 306 |  |
| `Combatv3\worldbuilding\renown_worldlore - Copy.py` | 1470 | renown_worldlore.py |
| `Combatv3\worldbuilding\renown_worldlore.md` | 266 | Renown — World Lore Framework |
| `Combatv3\worldbuilding\renown_worldlore.py` | 3364 | renown_worldlore.py |
| `Combatv3\worldbuilding\world.py` | 58 | world.py - fixed macro-geography of the setting. |
| `Combatv3\worldbuilding\world.txt` | 1517 |  |
| `Combatv3\worldbuilding\world_design.txt` | 2377 |  |
| `Combatv3\worldbuilding\world_map.py` | 74 | world_map.py - schematic map with organic (radial-fBm) coastlines. |
| `RenownWiki\actions-ref.html` | 22 | Actions — Renown |
| `RenownWiki\bandits-ref.html` | 22 | Bandits — Renown |
| `RenownWiki\board.html` | 22 | Board Emulator — Renown |
| `RenownWiki\domain-board-ref.html` | 22 | Domain Board — Renown |
| `RenownWiki\domain-cunning.html` | 22 | Cunning Holdings — Renown |
| `RenownWiki\domain-industry.html` | 22 | Industry Holdings — Renown |
| `RenownWiki\domain-piety.html` | 22 | Piety Holdings — Renown |
| `RenownWiki\domain-prowess.html` | 22 | Prowess Holdings — Renown |
| `RenownWiki\economy-ref.html` | 22 | Economy Reference — Renown |
| `RenownWiki\edicts-ref.html` | 22 | Edicts — Renown |
| `RenownWiki\envoy-outcomes-ref.html` | 22 | Envoy Outcomes — Renown |
| `RenownWiki\equipment-ref.html` | 22 | Equipment — Renown |
| `RenownWiki\eras-ref.html` | 22 | Eras — Renown |
| `RenownWiki\escalation-pursuits.html` | 22 | Escalation Combat Holdings — Renown |
| `RenownWiki\escalation-rules.html` | 22 | Escalation Battle Rules — Renown |
| `RenownWiki\escalation.html` | 22 | Escalation Campaign — Renown |
| `RenownWiki\factions.html` | 22 | Heritages — Renown |
| `RenownWiki\glossary.html` | 22 | Glossary — Renown |
| `RenownWiki\index.html` | 22 | Renown Rules — Renown |
| `RenownWiki\infrastructure-ref.html` | 22 | Infrastructure — Renown |
| `RenownWiki\keywords-ref.html` | 22 | Combat Keywords — Renown |
| `RenownWiki\lore-ages.html` | 22 | The Timeline — Renown |
| `RenownWiki\lore-cultures.html` | 22 | The Fifteen — Renown |
| `RenownWiki\lore-darkness.html` | 22 | The Age of Darkness — Renown |
| `RenownWiki\lore-map.html` | 22 | The Map — Renown |
| `RenownWiki\lore.html` | 22 | The World of Vaelohk — Renown |
| `RenownWiki\maps.html` | 22 | Map Generator — Renown |
| `RenownWiki\paths.html` | 22 | Build Paths — Renown |
| `RenownWiki\public-order-ref.html` | 22 | Public Order — Renown |
| `RenownWiki\pursuits.html` | 22 | Holdings — Renown |
| `RenownWiki\reference-tables.html` | 22 | Reference Tables — Renown |
| `RenownWiki\rules-action-mechanics.html` | 43 | Action Mechanics — Renown |
| `RenownWiki\rules-armies.html` | 35 | Armies — Renown |
| `RenownWiki\rules-armor.html` | 24 | Armor — Renown |
| `RenownWiki\rules-bandits.html` | 62 | Bandits — Renown |
| `RenownWiki\rules-battle-phase.html` | 67 | Battle Phase — Renown |
| `RenownWiki\rules-core-principles.html` | 82 | Core Principles — Renown |
| `RenownWiki\rules-cunning-actions.html` | 23 | Cunning Actions — Renown |
| `RenownWiki\rules-diplomacy-actions.html` | 24 | Diplomacy Actions — Renown |
| `RenownWiki\rules-diplomacy-treaties.html` | 47 | Diplomacy &amp; Treaties — Renown |
| `RenownWiki\rules-domains-standings.html` | 30 | Domains &amp; Standings — Renown |
| `RenownWiki\rules-factions.html` | 23 | Heritages — Renown |
| `RenownWiki\rules-holdings.html` | 24 | Holdings — Renown |
| `RenownWiki\rules-index.html` | 23 | Index — Renown |
| `RenownWiki\rules-industry-actions.html` | 27 | Industry Actions — Renown |
| `RenownWiki\rules-influence.html` | 25 | Influence — Renown |
| `RenownWiki\rules-infrastructure.html` | 31 | Infrastructure — Renown |
| `RenownWiki\rules-introduction.html` | 47 | Introduction — Renown |
| `RenownWiki\rules-melee-weapons.html` | 23 | Melee Weapons — Renown |
| `RenownWiki\rules-piety-actions.html` | 25 | Piety Actions — Renown |
| `RenownWiki\rules-player-setup.html` | 29 | Player Setup — Renown |
| `RenownWiki\rules-prowess-actions.html` | 25 | Prowess Actions — Renown |
| `RenownWiki\rules-public-order.html` | 29 | Public Order — Renown |
| `RenownWiki\rules-ranged-weapons.html` | 23 | Ranged Weapons — Renown |
| `RenownWiki\rules-reading-these-rules.html` | 35 | Reading These Rules — Renown |
| `RenownWiki\rules-renown.html` | 24 | Renown — Renown |
| `RenownWiki\rules-resources.html` | 31 | Resources — Renown |
| `RenownWiki\rules-seasons.html` | 24 | Seasons — Renown |
| `RenownWiki\rules-settlements.html` | 33 | Settlements — Renown |
| `RenownWiki\rules-setup-order.html` | 33 | Setup Order — Renown |
| `RenownWiki\rules-shields.html` | 23 | Shields — Renown |
| `RenownWiki\rules-siege-warfare.html` | 58 | Siege Warfare — Renown |
| `RenownWiki\rules-table-setup.html` | 26 | Table Setup — Renown |
| `RenownWiki\rules-territory-terrain.html` | 28 | Territory &amp; Terrain — Renown |
| `RenownWiki\rules-the-turn.html` | 78 | The Turn — Renown |
| `RenownWiki\rules-trade-income.html` | 39 | Trade &amp; Income — Renown |
| `RenownWiki\rules-treasury-upkeep.html` | 35 | Treasury &amp; Upkeep — Renown |
| `RenownWiki\search.js` | 7 |  |
| `RenownWiki\seasons-ref.html` | 22 | Seasons — Renown |
| `RenownWiki\settlement_board.html` | — | generated HTML (2010 KB) |
| `RenownWiki\settlements-ref.html` | 22 | Settlements — Renown |
| `RenownWiki\standing-established.html` | 22 | Established Tier — Renown |
| `RenownWiki\standing-rising.html` | 22 | Rising Tier — Renown |
| `RenownWiki\standing-sovereign.html` | 22 | Sovereign Tier — Renown |
| `RenownWiki\systems-ref.html` | 22 | Timers, Influence &amp; PO — Renown |
| `RenownWiki\tactic-matrix-ref.html` | 22 | Tactic Matrix — Renown |
| `RenownWiki\terrain-ref.html` | 22 | Terrain &amp; Movement — Renown |
| `RenownWiki\treaties-ref.html` | 22 | Treaties &amp; Alliances — Renown |
| `RenownWiki\turn-sequence.html` | 22 | Turn Sequence — Renown |
| `RenownWiki\type-arms.html` | 22 | Arms — Renown |
| `RenownWiki\type-commerce.html` | 22 | Commerce — Renown |
| `RenownWiki\type-court.html` | 22 | Court — Renown |
| `RenownWiki\type-devotion.html` | 22 | Devotion — Renown |
| `RenownWiki\type-husbandry.html` | 22 | Husbandry — Renown |
| `RenownWiki\type-logistics.html` | 22 | Logistics — Renown |
| `RenownWiki\type-monument.html` | 22 | Monument — Renown |
| `RenownWiki\type-raw-materials.html` | 22 | Raw Materials — Renown |
| `RenownWiki\type-secrecy.html` | 22 | Secrecy — Renown |
| `RenownWiki\type-works.html` | 22 | Works — Renown |
| `RenownWiki\ui.js` | 42 | theme toggle (head script already applied the stored/default theme) |
| `RenownWiki\mapgen\renown-maps.html` | 4344 | Renown — Map Generator |
| `generators\equipment.csv` | 38 | columns: Name,Category,Tier,AP,Initiative,Save,Effects,Cost,Strike,Endurance,Morale,Pursuit Unlock,Note |
| `generators\factions.csv` | 42 | columns: Inspiration,AI Name,Feel,Difficulty,Strength,Mechanic,Pair,Complement |
| `generators\infrastructure.csv` | 18 | columns: Name,Category,Upkeep,Upkeep Frequency,Empire Bonus,Tier,Build Time,Requirement |
| `generators\spec_tree_sheet.py` | 1159 | Renown — Specialization Tree renderer. |
| `generators\spec_trees.csv` | 269 | columns: tree,pathology,node,parents,tier,domain,type |
| `generators\specs.csv` | 107 | columns: Pursuits,Type,Unlock Requirement,Mastery Requirement,Innate Effects,Mastery Effect,Builds Into |
| `generators\specs_escalation.csv` | 39 | columns: Pursuits,Type,Unlock Requirement,Mastery Requirement,Innate Effects,Mastery Effect,Builds Into |
| `generators\update_compendium.py` | 535 | update_compendium.py — drives Compendium.docx from the canonical CSVs. |

## 3. Data index — `CE\renown_data_d10.py`

Copied to `CE/renown_data.py` by the build (DIE=d10); every script imports `renown_data`.

| Name | Line | Type | Size / value |
|---|---|---|---|
| `SIMPLE` | 7 | bool | True |
| `PHASE_REFORM` | 10 | bool | True |
| `VERSION` | 12 | str | '0.4.9.9.13-d10-S' |
| `BLUNDER_THR` | 40 | int | 10 |
| `DICE_PROVENANCE` | 41 | str | 'd10 / Focused 10+ / Parry 8+ / Recover  |
| `SACK_EXTORT_PER_TIER` | 44 | int | 2000 |
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
| `GLOSSARY` | 124 | dict | 170 |
| `MORALE_GLOSSARY` | 256 | dict | 4 |
| `ARMY_MAX_RETINUES` | 282 | int | 25 |
| `FRONT_LINE_MAX` | 283 | int | 10 |
| `RESERVE_MAX` | 284 | int | 5 |
| `MORALE_DICE_MAX` | 285 | int | 5 |
| `PANIC_CASUALTY_THRESHOLD` | 286 | int | 5 |
| `ENDURANCE_REGAIN` | 287 | int | 2 |
| `RETINUES` | 291 | dict | 4 |
| `WEAPONS` | 298 | dict | 19 |
| `RANGED` | 320 | dict | 6 |
| `SHIELDS` | 330 | dict | 6 |
| `ARMORS` | 339 | dict | 6 |
| `TIERS` | 350 | list | 5 |
| `TIER_UNLOCK` | 351 | dict | 5 |
| `STANDING_EFFECTS` | 362 | dict | 6 |
| `TACTIC_MATRIX` | 387 | dict | 49 |
| `TACTICS` | 446 | list | 7 |
| `TACTIC_NOTES` | 448 | dict | 0 |
| `BATTLE_NARRATION` | 454 | dict | 19 |
| `CULTURE_SELF_MADE` | 497 | str | 'Self-made' |
| `CULTURES` | 499 | dict | 15 |
| `NODES` | 664 | dict | 128 |
| `DEPRECATED_NODES` | 1555 | dict | 3 |
| `HOLDING_GROUPS` | 1565 | dict | 9 |
| `SCOPES` | 1582 | tuple | 3 |
| `SCOPE_BY_TYPE` | 1583 | dict | 2 |
| `LINE_LABELS` | 1587 | dict | 28 |
| `lines_of` | 1618 | function |  |
| `REQ_KEY` | 1624 | str | 'infrastructure_req' |
| `REQ_LABEL` | 1625 | str | 'Infrastructure Req' |
| `TYPE_ORDER` | 1627 | list | 10 |
| `CHAIN_TERM` | 1629 | str | 'Mastery Chain' |
| `SHUTTER_TERM` | 1631 | str | 'Shuttered' |
| `UPKEEP_TERM` | 1635 | str | 'Upkeep' |
| `SUPPLY_TERM` | 1636 | str | 'Supply' |
| `PURSUIT_TERM` | 1638 | tuple | 2 |
| `node_parents` | 1640 | function |  |
| `get_data` | 1648 | function |  |
| `MONUMENT_SUMMARY` | 1657 | dict | 24 |
| `WONDER_SUMMARY` | 1686 | dict | 4 |
| `FACTIONS` | 1696 | dict | 39 |
| `DEPRECATED_FACTIONS` | 2195 | dict | 2 |
| `INFRASTRUCTURE` | 2205 | dict | 20 |
| `WONDERS` | 2331 | dict | 4 |
| `INFRA_TIERS` | 2332 | list | 5 |
| `SETTLEMENTS` | 2340 | dict | 5 |
| `PRESENCE_RANGE` | 2351 | int | 2 |
| `WARD_MODEL` | 2355 | str | 'range1' |
| `WARD_RULES` | 2356 | dict | 2 |
| `WARD_RULE` | 2364 | str | 'A Settlement Ward is a slot that holds  |
| `FAITH_FICKLE_PO` | 2366 | int | 0 |
| `ERAS` | 2369 | dict | 4 |
| `PO_BANDS` | 2389 | dict | 11 |
| `po_scale` | 2408 | function |  |
| `po_value` | 2415 | function |  |
| `po_effect` | 2420 | function |  |
| `PUBLIC_ORDER` | 2427 | dict | 11 |
| `PUBLIC_ORDER_BY_ERA` | 2428 | dict | 4 |
| `PO_MODIFIERS` | 2434 | dict | 2 |
| `DOMAIN_BOARD` | 2452 | dict | 6 |
| `SEASONS` | 2489 | dict | 4 |
| `TRADE_REQUIRES_BORDER` | 2498 | bool | False |
| `TRADE_RULES` | 2499 | dict | 6 |
| `efficient_graph` | 2514 | function |  |
| `EFFICIENT_MULTI` | 2524 | dict | 119 |
| `EFFICIENT` | 2525 | dict | 119 |
| `BANDIT_CAMP_START` | 2533 | int | 10 |
| `BANDIT_CAMP_GOLD` | 2534 | int | 2000 |
| `BANDIT_ARMY_THRESHOLD` | 2535 | int | 25 |
| `BANDIT_GROWTH_PER_ERA` | 2536 | dict | 4 |
| `BANDIT_EQUIPMENT_PER_ERA` | 2537 | dict | 4 |
| `BANDITS` | 2538 | dict | 5 |
| `TIMERS` | 2546 | dict | 8 |
| `CHARTER_MIN_RANGE` | 2558 | int | 4 |
| `OUTLAW_BUFFER_RANGE` | 2559 | int | 2 |
| `HAMLET_RANGE` | 2560 | int | 2 |
| `OUTLAW_COUNTRY_START` | 2561 | int | 3 |
| `WILD_OUTLAW` | 2569 | dict | 9 |
| `wild_outlaw_count` | 2582 | function |  |
| `BANDIT_CAMP_REACH` | 2589 | str | 'province' |
| `VASSAL_EXCHANGE_CAP` | 2592 | int | 5000 |
| `VASSAL_INFLUENCE_TAKE` | 2593 | int | 3 |
| `BUILD_TIMERS` | 2597 | dict | 11 |
| `PURSUIT_UPKEEP_DEFAULT` | 2612 | int | 100 |
| `HOLDING_TIER_COST` | 2614 | dict | 4 |
| `holding_standing` | 2622 | function |  |
| `holding_cost` | 2628 | function |  |
| `holding_build_time` | 2636 | function |  |
| `HOLDING_COST_TEXT` | 2642 | str | 'by Standing: Untested 100 (Build Timer  |
| `TERRAIN` | 2645 | dict | 7 |
| `MOVEMENT_MODIFIERS` | 2655 | dict | 6 |
| `TACTICAL_TERRAIN` | 2667 | dict | 7 |
| `TACTICAL_GLOBAL` | 2683 | list | 1 |
| `INFLUENCE_GAIN` | 2685 | dict | 9 |
| `ENVOY_OUTCOME_THRESHOLDS` | 2741 | dict | 4 |
| `CUNNING_EXTORT` | 2760 | int | 4000 |
| `CUNNING_EXTORT_ENDORSED` | 2761 | int | 2000 |
| `ENVOY_OUTCOMES` | 2762 | dict | 5 |
| `ACTIONS` | 2785 | dict | 23 |
| `TREATIES` | 2987 | dict | 5 |
| `ALLIANCE_RULES` | 2995 | list | 3 |
| `EDICT_STREAK_TURNS` | 3005 | int | 5 |
| `GAME_TURN_LIMIT` | 3006 | int | 50 |
| `EDICT_UNIQUE` | 3009 | bool | False |
| `EDICT_UNIQUE_RULE` | 3010 | str | 'Each Domain, Monument, or Wonder counts |
| `EDICTS` | 3013 | dict | 7 |
| `BANDIT_BEHAVIOR` | 3027 | dict | 8 |
| `PURSUIT_UPKEEP_BY_TYPE` | 3050 | dict | 4 |
| `UPKEEP_TRACKS` | 3060 | dict | 3 |
| `pursuit_upkeep` | 3067 | function |  |
| `ARMY_UPKEEP_NOTE` | 3078 | str | "Net Army Supply = the sum of each Army' |
| `COSTS` | 3082 | dict | 12 |
| `COUNCIL_DOMAIN` | 3104 | str | 'Industry' |
| `COUNCIL_DOMAIN_SPRING` | 3105 | str | 'Diplomacy' |
| `FORUM_DOMAIN` | 3106 | str | 'Diplomacy' |
| `FORUM_ACTIONS` | 3107 | int | 1 |
| `PHASES` | 3108 | tuple | 5 |
| `STARTING_TURN_PHASE_OPENER` | 3109 | str | 'End of Empire' |
| `STANDING_ARMY_SIEGE_MODIFIER` | 3111 | int | 1 |
| `EMPIRE_START_TIERS` | 3113 | tuple | 2 |
| `STARTING_TREASURY` | 3114 | int | 10000 |
| `SETUP_CAPITAL_PICKS` | 3117 | int | 1 |
| `SETUP_HAMLET_PICKS` | 3118 | int | 1 |
| `SETUP_HAMLET_HOLDINGS` | 3119 | tuple | 1 |
| `SETUP_HAMLET_TEXT` | 3120 | str | 'Common Land' |
| `HAMLET_REPEATABLE` | 3122 | tuple | 1 |
| `HAMLET_REPEATABLE_TEXT` | 3123 | str | 'Common Land' |
| `AGES` | 3129 | dict | 5 |
| `AGE_YEAR_SEASON` | 3136 | str | 'Spring' |
| `AGE_YEAR_ROLL_MEAN` | 3139 | float | 0.45 |
| `AGE_YEAR_ROLL_SD` | 3140 | float | 0.16666666666666666 |
| `CAPITAL_EDGE_RANGE` | 3141 | int | 4 |
| `BOARD_SIZES` | 3143 | dict | 3 |
| `SIEGE_CALCULUS` | 3149 | dict | 2 |
| `SIEGE_SOURCE_VALUES` | 3164 | dict | 3 |
| `NAME_DISPLAY` | 3195 | dict | 76 |
| `TIER_DISPLAY` | 3232 | dict | 1 |
| `ITEM_TIER_DISPLAY` | 3238 | dict | 1 |
| `TERM_ENVOY_SCORE` | 3245 | str | 'Authority' |
| `display_score` | 3255 | function |  |
| `ALIASES` | 3265 | dict | 78 |
| `display` | 3275 | function |  |
| `display_tier` | 3280 | function |  |
| `display_text` | 3290 | function |  |
| `display_list` | 3313 | function |  |
| `display_md` | 3323 | function |  |
| `display_html` | 3330 | function |  |
| `display_obj` | 3342 | function |  |
| `undisplay` | 3355 | function |  |
| `verify_aliases` | 3364 | function |  |
| `BANDIT_FACES` | 3388 | int | 10 |
| `BANDIT_CUNNING_MIN` | 3389 | int | 10 |
| `die_table_ranges` | 3392 | function |  |
| `die_table_rows` | 3400 | function |  |
| `die_table_text` | 3408 | function |  |
| `die_table_lookup` | 3416 | function |  |
| `die_table_verify` | 3423 | function |  |
| `die_table_weights` | 3442 | function |  |
| `BANDIT_CUNNING_TABLE` | 3452 | dict | 4 |
| `bandit_cunning_ranges` | 3459 | function |  |
| `bandit_cunning_rows` | 3460 | function |  |
| `bandit_cunning_lookup` | 3461 | function |  |
| `bandit_cunning_text` | 3463 | function |  |
| `BANDIT_TACTIC_TABLE` | 3470 | dict | 6 |
| `BANDIT_TACTICS` | 3478 | list | 6 |
| `bandit_tactic_ranges` | 3480 | function |  |
| `bandit_tactic_rows` | 3481 | function |  |
| `bandit_tactic_lookup` | 3482 | function |  |
| `verify_bandit_tables` | 3485 | function |  |
| `RENOWN_MAX` | 3585 | int | 30 |
| `RENOWN_PER_TURN` | 3586 | int | 1 |
| `DOMAIN_POINTS_PER_TURN` | 3587 | int | 1 |
| `AI_DOMAIN_POINTS` | 3593 | str | 'Spend Domain Points one Standing at a t |
| `AI_PRIORITIES` | 3595 | list | 8 |
| `AI_FAITH_AVOID` | 3606 | list | 5 |
| `AI_STYLE` | 3629 | dict | 3 |
| `AI_ARCHETYPE` | 3652 | dict | 8 |
| `AI_PO_GOLD` | 3666 | int | 800 |
| `AI_MUSTER` | 3668 | dict | 3 |
| `AI_DIPLOMACY` | 3670 | dict | 4 |
| `FACTION_NAMES` | 3712 | dict | 39 |
| `FACTION_TERM` | 3720 | tuple | 2 |
| `faction_body` | 3726 | function |  |
| `GLOSSARY_CATEGORIES` | 3767 | list | 19 |
| `WIKI_NOLINK` | 3795 | list | 6 |
| `GLOSSARY_SEE` | 3804 | dict | 108 |
| `COND_UPKEEP_FACTOR` | 3850 | float | 0.5 |
| `holding_combat_tags` | 3860 | function |  |
| `holding_upkeep` | 3907 | function |  |
| `holding_domain` | 3920 | function |  |
| `HOLDING_SIM` | 3939 | dict | 128 |
| `AI_PROFILES` | 3951 | dict | 15 |

## 4. Build steps — `CE\build_all_CE.bat`

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

## 5. Rules markers — `CE\RULES_push_simple.md`

- **{{TABLE}}** (29): `edicts`, `eras`, `timers`, `seasons`, `ages`, `net_influence`, `envoy_outcomes`, `influence_gain`, `domain_board`, `treaties`, `settlements`, `infrastructure`, `build_timers`, `terrain`, `public_order`, `po_modifiers`, `trade_rules`, `retinues`, `tactic_matrix`, `siege_calculus`, `bandits_by_era`, `bandit_cunning`, `bandit_tactics`, `holdings`, `weapons`, `ranged`, `shields`, `armor`, `factions`
- **{{GLOSSARY}}** (18): `Reading the Rules`, `Turn & Phases`, `Envoys & Voting`, `Actions`, `Domains & Scoring`, `Treaties`, `Settlements & Holdings`, `Map & Range`, `Economy & Public Order`, `Army States`, `Battle Structure`, `Combat Keywords — Defense`, `Combat Keywords — Offense`, `Combat Keywords — Handling`, `Combat Keywords — Immune / Negate`, `War`, `World`, `Equipment Tiers`
- **{{ACTIONS}}** (5): `Diplomacy`, `Prowess`, `Cunning`, `Piety`, `Industry`
- **{{LIST}}** (1): `ALLIANCE_RULES`
- **{{TERM}}** (1): `Speed X`
- **{{IDX}}** (31): `Era`, `Empire Phase`, `End of Empire Phase`, `Envoy Phase`, `Council Phase`, `Battle Phase`, `Rest Phase`, `Intrigue Phase`, `Tally Phase`, `Season`, `Age`, `Standing Rank`, `Max Influence`, `Settlement`, `Hamlet`, `Infrastructure`, `Primitive`, `Developed`, `Sophisticated`, `Prodigious`, `Wondrous`, `Wonder`, `Treasury`, `Revenue`, `Trade Agreement`, `Army`, `Garrison`, `Lay Siege`, `Capture`, `Sack`, `Bandit Camp`
- **{{VAL}}** (93): `AGE_YEAR_SEASON`, `ARMY_MAX_RETINUES`, `BANDITS.Bandit Domain Value`, `BANDIT_ARMY_THRESHOLD`, `BANDIT_CAMP_GOLD`, `BANDIT_CAMP_START`, `BANDIT_CUNNING_MIN`, `BANDIT_FACES`, `BLUNDER_THR`, `CAPITAL_EDGE_RANGE`, `CAP_THR`, `CHAIN_TERM`, `COUNCIL_DOMAIN`, `DOMAIN_BOARD.innate_influence_own_envoys.Untested`, `DOMAIN_POINTS_PER_TURN`, `EDICT_UNIQUE_RULE`, `ENDURANCE_REGAIN`, `ERAS.Ascension.rank`, `ERAS.Eminence.diplomacy_agreements`, `ERAS.Eminence.rank`, `ERAS.Founding.diplomacy_agreements`, `ERAS.Founding.rank`, `ERAS.Founding.renown`, `ERAS.Zenith.rank`, `FACES`, `FAITH_FICKLE_PO`, `FATIGUE_MORALE`, `FOCUSED_THR`, `FORUM_ACTIONS`, `FRONT_LINE_MAX`, `GAME_TURN_LIMIT`, `HAMLET_RANGE`, `HAMLET_REPEATABLE_TEXT`, `HOLDING_COST_TEXT`, `INFRASTRUCTURE.Cathedral.empire_bonus`, `INFRASTRUCTURE.Library.requirement`, `INFRASTRUCTURE.Magistrate's Hall.requirement`, `INITIATIVE_MAX`, `INITIATIVE_MIN`, `MORALE_DICE_MAX`, `OUTLAW_BUFFER_RANGE`, `OUTLAW_COUNTRY_START`, `PANIC_CASUALTY_THRESHOLD`, `PARRY_BASE`, `PO_MAX`, `PO_MIN`, `PRESENCE_RANGE`, `RENOWN_PER_TURN`, `RESERVE_MAX`, `RETINUES.Knight Templar.cost`, `RETINUES.Knight Templar.to_hit`, `RETINUES.Levy.cost`, `RETINUES.Levy.to_hit`, `RETINUES.Man-at-Arms.cost`, `RETINUES.Man-at-Arms.to_hit`, `RETINUES.Sergeant.cost`, `RETINUES.Sergeant.to_hit`, `ROUT_THR`, `SACK_EXTORT_PER_TIER`, `SETTLEMENTS.City.garrison`, `SETTLEMENTS.Hamlet.wards`, `SETTLEMENTS.Metropolis.garrison`, `SETTLEMENTS.Metropolis.reach`, `SETTLEMENTS.Town.garrison`, `SETTLEMENTS.Village.garrison`, `SETTLEMENTS.Village.reach`, `SETUP_HAMLET_TEXT`, `SHUTTER_TERM`, `SIEGE_CALCULUS.Lay Siege.floor`, `STANDING_RANK.Established`, `STANDING_RANK.Rising`, `STANDING_RANK.Sovereign`, `STANDING_RANK.Untested`, `STANDING_THRESHOLDS.Established`, `STANDING_THRESHOLDS.Rising`, `STANDING_THRESHOLDS.Sovereign`, `STANDING_THRESHOLDS.Untested`, `STARTING_TREASURY`, `STARTING_TURN_PHASE_OPENER`, `SUPPLY_TERM`, `TIMERS.Capture Timer.default`, `TIMERS.Sack Timer.default`, `TRADE_RULES.border_rule`, `TRADE_RULES.income_per_craft`, `UPKEEP_TERM`, `VASSAL_EXCHANGE_CAP`, `VASSAL_INFLUENCE_TAKE`, `WARD_RULE`, `WEALTH_EDICT_GOLD`, `WILD_OUTLAW.border_range`, `WILD_OUTLAW.per_players`, `WILD_OUTLAW.plus`, `WILD_OUTLAW.spacing`
- **docx_tables.REGISTRY** (32): `ages`, `armor`, `bandit_armaments`, `bandit_cunning`, `bandit_growth`, `bandit_tactics`, `bandits_by_era`, `build_timers`, `domain_board`, `edicts`, `envoy_outcomes`, `eras`, `factions`, `holdings`, `influence_gain`, `infrastructure`, `net_influence`, `po_modifiers`, `public_order`, `ranged`, `retinues`, `seasons`, `settlements`, `shields`, `siege_calculus`, `tactic_matrix`, `tactical_terrain`, `terrain`, `timers`, `trade_rules`, `treaties`, `weapons`

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
| 164 | ### Envoy Phase |
| 179 | ### Battle Phase |
| 183 | ### Rest Phase |
| 192 | # Seasons |
| 198 | # Setup |
| 200 | ## Table Setup |
| 205 | ## Setup Order |
| 214 | ### Ages |
| 220 | ## Player Setup |
| 228 | # Actions & Voting |
| 230 | ## Action Mechanics |
| 232 | ### Sending an Envoy |
| 236 | ### Resolving an Envoy |
| 252 | ### Envoy Resolution Table |
| 268 | ## Influence |
| 276 | ## Diplomacy Actions |
| 285 | ## Prowess Actions |
| 289 | ### Rule: Commanding Presence |
| 293 | ## Cunning Actions |
| 297 | ## Piety Actions |
| 301 | ### Rule: Wavering Devotion |
| 305 | ## Industry Actions |
| 309 | ### Rule: Ulterior Motive |
| 317 | # Domains & Standings |
| 319 | ### Domain Standings |
| 325 | ### Standing Rank |
| 329 | ### Domain Identities & Traits |
| 335 | # Diplomacy & Treaties |
| 337 | ### Treaties & Alliances |
| 345 | ### Vassalization |
| 367 | # Empire Building |
| 369 | ## Settlements |
| 375 | ### Settlement Wards |
| 379 | ### Chartering Settlements |
| 383 | ### Settlement Reach |
| 387 | ### Hamlets |
| 393 | ## Infrastructure |
| 413 | ## Territory & Terrain |
| 427 | # Economy |
| 429 | ## Public Order |
| 441 | ### Innate Public Order Modifiers |
| 445 | ## Treasury & Upkeep |
| 455 | ### Insolvency & Bankruptcy |
| 468 | ## Trade & Income |
| 470 | ### Who Can Trade |
| 485 | ### Income Types |
| 493 | # Armies |
| 495 | ### Armies Overview |
| 501 | ### Garrisons |
| 505 | ### Mustering |
| 515 | ### Blocked Armies |
| 521 | # Battles & Sieges |
| 523 | ## Battle Phase |
| 527 | ### Beginning a Battle |
| 533 | ### The Skirmish Steps |
| 551 | ### Ending a Battle |
| 556 | ### Tactic Matrix |
| 570 | ## Siege Warfare |
| 575 | ### Siege Timer |
| 581 | ### Beginning a Siege |
| 591 | ### Resolving a Siege |
| 605 | # Bandits |
| 607 | ### Outlaw Country |
| 616 | ### Spawning Bandit Camps |
| 622 | ### Growing Bandit Camps |
| 628 | ### Bandit Rules |
| 644 | ### Bandit Army Behavior |
| 656 | ### Attacking a Bandit Camp |
| 666 | # Holdings |
| 672 | # Equipment |
| 674 | ## Melee Weapons |
| 678 | ## Ranged Weapons |
| 682 | ## Shields |
| 686 | ## Armor |
| 692 | # Factions |
| 696 | # Index |

## 6. Settlement board — `CE\references\gen_settlement_board.py` + `CE\references\board\js/*.js` (+ `board.css`, `body.html`)

Payload keys passed to the HTML as `DATA` (68): `records`, `naturalNames`, `externalTokens`, `simple`, `chainTerm`, `pursuitTerm`, `infra`, `wonders`, `armySrc`, `equip`, `glossary`, `domainBoard`, `publicOrder`, `domainBoardFx`, `poByEra`, `wikiBase`, `wikiHome`, `tree`, `rulebook`, `limits`, `eras`, `edicts`, `envoyOutcomes`, `outcomeThresh`, `startPhase`, `actions`, `phaseRules`, `phaseSteps`, `rulesConst`, `ages`, `domains`, `standings`, `tradePerCraft`, `noTradeSeason`, `tradeBorder`, `renownPerTurn`, `dpPerTurn`, `settlements`, `battle`, `terrainRef`, `banditLoadouts`, `bandits`, `treaties`, `allianceRules`, `startTiers`, `startTreasury`, `pursuitUpkeep`, `buildTimers`, `infraTiers`, `timers`, `seasons`, `poModifiers`, `vassalInfluenceTake`, `aliases`, `scoreTerm`, `costs`, `influenceGain`, `siege`, `factions`, `cultures`, `monSummary`, `wonSummary`, `cultureSelf`, `placeNames`, `warnings`, `version`, `sprites`, `efx`

Python: `load`:27, `strip_md`:34, `has_cond`:78, `to_int`:81, `classify`:84, `_iv`:154, `envoy_fx`:155, `combine_parts`:272, `combine_effects`:313, `rules_payload`:317, `tree_payload`:376, `parse_effects`:410, `parse_mreq`:416, `classify_req_token`:424, `build`:433, `font_faces`:533, `_pursuit_term_template`:558, `render_html`:566, `_style_js`:574, `place_names_payload`:585, `sprite_payload`:606, `find_mapgen`:628, `_board_template`:643, `check_rules`:657, `_val`:785, `council_heading`:794, `rules_section`:798, `phase_steps`:817, `battle_data`:834, `bandit_loadouts`:856, `effects_report`:909, `main`:940

JS sections: TABLE: seating, Council & Envoy phases :10_table.js:1, Action automation: Perform picker + resolution :10_table.js:307, REALM: the play surface :15_realm.js:1, INTRIGUE & TALLY PHASES (RULES: Envoy Phase steps 3 and 5) :16_tally.js:1, DIPLOMACY STEP (PHASE_REFORM): offers between players :17_diplo_step.js:1,  :40_realm_data.js:271, Inspect tool :60_map.js:280, EFFECT PLUMBING: the effect registry (references/effect_registry.py) :70_rules.js:1, ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS :70_rules.js:64, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :70_rules.js:159, CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper :85_ux.js:1, WELCOME: seats + profile (server games) :86_welcome.js:1, UNDO / REDO :90_app.js:1, ACTIVITY LOG :90_app.js:43, GAME: save · load · new :90_app.js:102, HOVER KEYWORDS :90_app.js:153

JS functions (1163, name:file:line):

```
fixBastard:00_core.js:8 dispScore:00_core.js:15 presR:00_core.js:33 POB:00_core.js:36 poNum:00_core.js:37 efxOf:00_core.js:48 hitOf:00_core.js:49 facHit:00_core.js:50 razeTimerPlus:10_table.js:10 tnow:10_table.js:14 noteServerDate:10_table.js:15 gkey:10_table.js:21 lockOn:10_table.js:28 claimOf:10_table.js:29 mine:10_table.js:30 myClaimP:10_table.js:31 canEdit:10_table.js:32 boardEndOn:10_table.js:34 TB:10_table.js:35 seatFloor:10_table.js:37 tSeats:10_table.js:38 tTimer:10_table.js:39 tTurn:10_table.js:40 tBegun:10_table.js:41 tPhase:10_table.js:42 PT:10_table.js:44 tCur:10_table.js:45 tCurW:10_table.js:46 sameP:10_table.js:47 meP:10_table.js:48 canAct:10_table.js:49 seatMap:10_table.js:52 seated:10_table.js:56 isSpring:10_table.js:57 councilDomNow:10_table.js:59 councilOff:10_table.js:60 hostP:10_table.js:61 voteOrd:10_table.js:64 tOrder:10_table.js:65 canHost:10_table.js:66 seatsLocked:10_table.js:67 tStand:10_table.js:70 eraRec:10_table.js:71 diploInf:10_table.js:72 diploCap:10_table.js:73 eraActions:10_table.js:74 envActions:10_table.js:78 envSlots:10_table.js:79 endorsedBonus:10_table.js:85 slotLabel:10_table.js:89 slotOpen:10_table.js:90 withSlots:10_table.js:91 boardFx:10_table.js:94 fxOf:10_table.js:107 scopeOk:10_table.js:108 sgn:10_table.js:109 fxLabel:10_table.js:110 atWarPair:10_table.js:127 opposeBlock:10_table.js:128 domAsFx:10_table.js:135 innateParts:10_table.js:136 modSum:10_table.js:142 innateInf:10_table.js:144 voteCap:10_table.js:145 inflPool:10_table.js:148 personalEnvoys:10_table.js:149 councilEnvoys:10_table.js:150 tOutcome:10_table.js:151 outText:10_table.js:153 tPlan:10_table.js:156 missionWhy:10_table.js:174 domStarted:10_table.js:177 whisperEligibleEnvoys:10_table.js:178 tSim:10_table.js:181 performEval:10_table.js:269 comboEval:10_table.js:275 failPassFx:10_table.js:286 condFailFx:10_table.js:287 inviteHolders:10_table.js:291 inviteOf:10_table.js:293 actionsOf:10_table.js:294 actReqFlag:10_table.js:296 actInfoHTML:10_table.js:300 actCost:10_table.js:311 domCost:10_table.js:313 addFaith:10_table.js:314 alliedP:10_table.js:315 allyGroup:10_table.js:316 topPair:10_table.js:317 actDoubt:10_table.js:320 musterOpts:10_table.js:385 runMuster:10_table.js:392 buildOpts:10_table.js:408 buildPlaces:10_table.js:416 runBuild:10_table.js:420 improveOpts:10_table.js:426 expandOpts:10_table.js:431 runExpand:10_table.js:435 runImprove:10_table.js:439 runSettle:10_table.js:444 repairOpts:10_table.js:449 runRepair:10_table.js:452 settName:10_table.js:458 warOnFac:10_table.js:461 warOn:10_table.js:465 grandVizier:10_table.js:469 pfSpec:10_table.js:472 pfHardFlags:10_table.js:473 pfTargets:10_table.js:484 pfSubs:10_table.js:496 pfSubLabel:10_table.js:497 evTxt:10_table.js:499 insteadFx:10_table.js:504 actDom:10_table.js:505 pfActs:10_table.js:506 pfInsteadSrc:10_table.js:508 pfForm:10_table.js:509 boardCounts:10_table.js:544 pendingOf:10_table.js:546 apLines:10_table.js:548 resolveEnvoy:10_table.js:551 campTgt:10_table.js:612 campExtort:10_table.js:613 autoRes:10_table.js:614 tApply:10_table.js:615 recAct:10_table.js:627 actTgtName:10_table.js:629 allActs:10_table.js:630 actsAt:10_table.js:635 actLine:10_table.js:636 realmActsHTML:10_table.js:637 tNext:10_table.js:644 tSetPhase:10_table.js:645 tRestartPhase:10_table.js:648 tAdd30:10_table.js:653 grantDP:10_table.js:656 dpOwed:10_table.js:657 tEndTurn:10_table.js:658 setSeats:10_table.js:678 tAutoSeat:10_table.js:683 tSig:10_table.js:689 tName:10_table.js:692 tVoteTxt:10_table.js:693 envBadges:10_table.js:694 innateTxt:10_table.js:700 tOutCls:10_table.js:702 tPerformHtml:10_table.js:703 summaryLines:10_table.js:725 chronOn:10_table.js:742 chron:10_table.js:743 chronSnap:10_table.js:746 chronTick:10_table.js:753 chronDate:10_table.js:763 empireChecklistHTML:10_table.js:764 treeSave:10_table.js:774 mapRaws:10_table.js:785 refRawAvail:10_table.js:788 refCulture:10_table.js:794 refAvail:10_table.js:795 treeHTML:10_table.js:797 infraTreeHTML:10_table.js:874 rulebookHTML:10_table.js:905 linkifyRules:10_table.js:908 renderReference:10_table.js:912 tCountdown:10_table.js:927 applyTheme:10_table.js:942 applySkin:10_table.js:954 doFire:15_realm.js:8 patch:15_realm.js:12 rlCommit:15_realm.js:13 pOf:15_realm.js:14 standingPhaseActions:15_realm.js:15 holdingEpActions:15_realm.js:20 eurekaKey:15_realm.js:24 eurekaAction:15_realm.js:25 activeCipherTimers:15_realm.js:30 cipherTimerResolve:15_realm.js:36 empWin:15_realm.js:42 empireHoldingHTML:15_realm.js:43 whisperGateHTML:15_realm.js:67 forgeRetryHTML:15_realm.js:71 courierDeferHTML:15_realm.js:75 rlOpen:15_realm.js:128 rlToggle:15_realm.js:129 renderTable:15_realm.js:134 renderRealmMap:15_realm.js:154 domCells:15_realm.js:166 realmTableHTML:15_realm.js:172 spectating:15_realm.js:214 miniCardHTML:15_realm.js:226 phaseCardHTML:15_realm.js:236 dockCard:15_realm.js:288 dockHTML:15_realm.js:289 envoyQueueHTML:15_realm.js:363 inflPaneHTML:15_realm.js:384 inflCardHTML:15_realm.js:396 declInviteHTML:15_realm.js:416 drawersHTML:15_realm.js:455 turnLogItems:15_realm.js:467 turnLogHTML:15_realm.js:487 realmTimersBrief:15_realm.js:496 tallyVoter:16_tally.js:7 standingHit:16_tally.js:9 tallySupportOf:16_tally.js:10 tallyEndorseOf:16_tally.js:11 resolveOpen:16_tally.js:13 intrigueKinds:16_tally.js:15 intrigueSilenced:16_tally.js:24 whisperPending:16_tally.js:25 intrigueRun:16_tally.js:27 tallyRun:16_tally.js:38 envLabel:16_tally.js:61 tsId:16_tally.js:62 tRow:16_tally.js:63 envSel:16_tally.js:64 amtSel:16_tally.js:65 intrigueHTML:16_tally.js:66 tallyHTML:16_tally.js:94 inTurn:16_tally.js:109 selVal:16_tally.js:110 tallyTurn:16_tally.js:125 dsOn:17_diplo_step.js:7 dsKey:17_diplo_step.js:8 DS:17_diplo_step.js:9 dsCap:17_diplo_step.js:10 dsWho:17_diplo_step.js:11 dsAgreed:17_diplo_step.js:12 dsUsed:17_diplo_step.js:13 dsPartner:17_diplo_step.js:14 dsDone:17_diplo_step.js:15 dsAllDone:17_diplo_step.js:16 dsTypes:17_diplo_step.js:18 dsFlag:17_diplo_step.js:22 dsSnap:17_diplo_step.js:24 dsRestore:17_diplo_step.js:27 dsCourt:17_diplo_step.js:31 dsCourtRefund:17_diplo_step.js:34 dsEmb:17_diplo_step.js:37 dsFailable:17_diplo_step.js:38 dsEmbDue:17_diplo_step.js:40 dsFail:17_diplo_step.js:41 applyTreaty:17_diplo_step.js:45 dsEnds:17_diplo_step.js:53 dsClose:17_diplo_step.js:57 dsLog:17_diplo_step.js:58 dsOffer:17_diplo_step.js:59 dsAccept:17_diplo_step.js:61 dsEnd:17_diplo_step.js:65 dsEmbHTML:17_diplo_step.js:72 diploStepHTML:17_diplo_step.js:78 aiDiploStep:17_diplo_step.js:116 startDoms:20_state.js:2 ageRec:20_state.js:5 ageRisingOf:20_state.js:6 startDomsFor:20_state.js:7 startDomTotal:20_state.js:8 curYear:20_state.js:9 rollAgeYear:20_state.js:11 applyAgeStart:20_state.js:14 startSettlements:20_state.js:16 startSig:20_state.js:19 reseedIfPristine:20_state.js:21 newBoard:20_state.js:26 newPlayer:20_state.js:28 normalizeD:20_state.js:44 dedupeIds:20_state.js:70 activeBoard:20_state.js:72 reindex:20_state.js:73 pActive:20_state.js:86 dmgMark:20_state.js:88 dmgSrc:20_state.js:89 dmgSrcOf:20_state.js:90 chainOK:20_state.js:92 ignHas:20_state.js:96 flagState:20_state.js:97 ignBtn:20_state.js:102 ignNote:20_state.js:105 unlockStatus:20_state.js:111 nameHit:20_state.js:122 missTxt:20_state.js:123 recomputePC:20_state.js:125 buildTimerMod:20_state.js:130 timerMod:20_state.js:131 withBuildMod:20_state.js:135 pursuitBaseTime:20_state.js:136 infraBaseTime:20_state.js:137 repairTime:20_state.js:139 pursuitBuildTime:20_state.js:140 infraBuildTime:20_state.js:141 buildNote:20_state.js:142 settBaseTime:20_state.js:143 settBuildTime:20_state.js:144 itm:20_state.js:145 infraOn:20_state.js:146 shutToggle:20_state.js:149 shutUpkeep:20_state.js:153 checkinAct:20_state.js:159 gameStarted:20_state.js:160 glogTurn:20_state.js:164 glogSea:20_state.js:165 glogPush:20_state.js:166 glogSync:20_state.js:170 insolvent:20_state.js:173 tGold:20_state.js:175 boardOwnerName:20_state.js:180 empTimers:20_state.js:184 empEconomy:20_state.js:185 empPO:20_state.js:192 immuneStrainIn:20_state.js:204 siegeStrains:20_state.js:208 endMax:20_state.js:210 capEnd:20_state.js:211 effStrained:20_state.js:212 empArmies:20_state.js:213 endRow:20_state.js:220 boardEndTurn:20_state.js:223 stepRealmTimer:20_state.js:227 tickRealm:20_state.js:228 expireBlocks:20_state.js:232 expireBlocksTimed:20_state.js:233 empirePhase:20_state.js:236 tickTimers:20_state.js:260 facTypeBonus:20_state.js:269 pursuitUpkeep:20_state.js:272 withBoard:20_state.js:275 setOnline:20_state.js:291 clone:20_state.js:301 jeq:20_state.js:302 isObj:20_state.js:303 merge3:20_state.js:305 splitD:20_state.js:314 joinD:20_state.js:320 save:20_state.js:346 saveIfDirty:20_state.js:354 editing:20_state.js:389 cvar:20_state.js:409 fmt:20_state.js:410 cap:20_state.js:411 settUnbuilt:20_state.js:415 unbuiltMeta:20_state.js:416 settMeta:20_state.js:417 pinSettCell:20_state.js:418 settExpand:20_state.js:419 settFinish:20_state.js:420 settTier:20_state.js:423 occupants:20_state.js:424 hamletOK:20_state.js:425 hamletRoot:20_state.js:428 hamletFits:20_state.js:429 effList:20_state.js:438 effLabel:20_state.js:443 exemptionsOf:20_state.js:444 wardExemptions:20_state.js:453 isFreeRider:20_state.js:454 wardUse:20_state.js:455 canPlace:20_state.js:466 hamletRepeat:20_state.js:484 setupRawOK:20_state.js:487 setupHoldFlags:20_state.js:488 capitalSett:20_state.js:501 setCapital:20_state.js:502 isCityPlus:20_state.js:504 dbActive:20_state.js:505 standingKey:20_state.js:511 armStanding:20_state.js:512 capBonus:20_state.js:517 eraCapBase:20_state.js:518 eraCap:20_state.js:519 capSrc:20_state.js:520 cityCount:20_state.js:521 eraAllows:20_state.js:523 rslug:20_state.js:531 boardFlags:20_state.js:532 onBoard:20_state.js:567 scopeOf:20_state.js:569 realmHolder:20_state.js:570 wonderRacing:20_state.js:572 wonderStart:20_state.js:573 wonderRace:20_state.js:576 scopeBlock:20_state.js:586 nextTier:20_state.js:591 autoFill:20_state.js:593 buildFilters:30_empire.js:8 monChip:30_empire.js:10 catSave:30_empire.js:16 catGroups:30_empire.js:33 catRows:30_empire.js:35 pAvail:30_empire.js:39 legalCtx:30_empire.js:43 rawRes:30_empire.js:45 rawInSett:30_empire.js:46 rawOK:30_empire.js:50 pLegal:30_empire.js:51 pReqMiss:30_empire.js:56 autoHamlet:30_empire.js:59 autoOK:30_empire.js:60 effSpot:30_empire.js:62 facRide:30_empire.js:69 smartSid:30_empire.js:70 iAvail:30_empire.js:77 catUpkeep:30_empire.js:78 seg:30_empire.js:79 renderList:30_empire.js:81 wardPick:30_empire.js:135 wpRender:30_empire.js:137 wpPlace:30_empire.js:160 settLbl:30_empire.js:165 reqRow:30_empire.js:167 pursuitRow:30_empire.js:169 sub:30_empire.js:180 tip:30_empire.js:182 itemRow:30_empire.js:183 flash:30_empire.js:193 addInfraByName:30_empire.js:195 placeHolding:30_empire.js:201 addItem:30_empire.js:222 removeInstance:30_empire.js:233 addPursuitByName:30_empire.js:234 moveInstance:30_empire.js:235 infraReqToks:30_empire.js:251 infraTokStatus:30_empire.js:257 infraReqStatus:30_empire.js:271 infraValid:30_empire.js:276 infraActive:30_empire.js:283 infraReqLinesHTML:30_empire.js:284 masteryInfraToks:30_empire.js:288 masteryInfraHTML:30_empire.js:289 annotReqTok:30_empire.js:296 optionMet:30_empire.js:301 reqStatus:30_empire.js:309 instStatus:30_empire.js:316 chainLine:30_empire.js:323 simpleReq:30_empire.js:332 simpleReqHTML:30_empire.js:344 computeEarned:30_empire.js:352 atomEl:30_empire.js:370 FX_CHIP_TEST:30_empire.js:383 fxParts:30_empire.js:384 effectView:30_empire.js:386 atomsBlock:30_empire.js:397 render:30_empire.js:410 renderTopBar:30_empire.js:470 toggleEmpty:30_empire.js:517 sfxNorm:30_empire.js:526 sfxLabel:30_empire.js:527 settFx:30_empire.js:536 settFxPanel:30_empire.js:559 renderPursuitBoard:30_empire.js:566 wardPiles:30_empire.js:675 wardGrid:30_empire.js:687 unitFor:30_empire.js:714 tryMove:30_empire.js:719 scrollHost:30_empire.js:753 dropTargetAt:30_empire.js:754 clearDropHL:30_empire.js:762 armDrag:30_empire.js:763 beginDrag:30_empire.js:780 dragMove:30_empire.js:794 dragEnd:30_empire.js:806 herPicker:30_empire.js:815 factionFree:30_empire.js:826 setFaction:30_empire.js:830 facGearFlags:30_empire.js:839 armyTokHolder:30_empire.js:846 armyTokNamed:30_empire.js:847 factionFlags:30_empire.js:848 cultureFactions:30_empire.js:865 facOffered:30_empire.js:872 facPicker:30_empire.js:874 culSelectHTML:30_empire.js:891 cultureOf:30_empire.js:895 holdDom:30_empire.js:896 cultureSet:30_empire.js:900 cultureKeep:30_empire.js:905 cultureKeepWonder:30_empire.js:906 derivedCulture:30_empire.js:908 nameCulture:30_empire.js:910 usedSettNames:30_empire.js:912 genPlaceName:30_empire.js:913 nameSett:30_empire.js:919 nameAllSetts:30_empire.js:921 renderFaction:30_empire.js:922 timerCtl:30_empire.js:930 placementSelect:30_empire.js:935 contribAcc:30_empire.js:950 contribChips:30_empire.js:953 accChips:30_empire.js:954 pursuitDetail:30_empire.js:962 quickChip:30_empire.js:986 buildsIntoRow:30_empire.js:990 nextLinksHTML:30_empire.js:992 pursuitTable:30_empire.js:1000 pursuitCard:30_empire.js:1027 renderInfraSection:30_empire.js:1118 armyUnlocks:30_empire.js:1166 unlockedShieldTiers:30_empire.js:1199 tierOK:30_empire.js:1203 gloss:30_empire.js:1204 glossLookup:30_empire.js:1213 openModal:30_empire.js:1222 closeModal:30_empire.js:1226 kwChipHTML:30_empire.js:1227 esc:30_empire.js:1228 inspectKeyword:30_empire.js:1229 inspectItem:30_empire.js:1251 optionList:30_empire.js:1274 loadoutFields:30_empire.js:1290 canDualWield:30_empire.js:1305 weaponForbids:30_empire.js:1307 fixWeaponNotes:30_empire.js:1309 renderArmy:30_empire.js:1312 armyCard:30_empire.js:1345 reqMet:30_empire.js:1439 lanceOnlyOK:30_empire.js:1443 weaponUnlockMet:30_empire.js:1444 moraleBase:30_empire.js:1446 armyUpkeep:30_empire.js:1447 moraleCap:30_empire.js:1449 moraleStanding:30_empire.js:1452 moralePO:30_empire.js:1455 effMorale:30_empire.js:1457 isRouted:30_empire.js:1458 armyVals:30_empire.js:1461 armyStats:30_empire.js:1469 noUpkeepTiers:30_empire.js:1496 holdsActive:30_empire.js:1498 playersWithout:30_empire.js:1500 calcMetrics:30_empire.js:1502 computeTotals:30_empire.js:1563 poTaxMod:30_empire.js:1594 taxDouble:30_empire.js:1599 winterTax:30_empire.js:1600 occupyTaxOnly:30_empire.js:1609 settInside:30_empire.js:1610 settTax:30_empire.js:1611 tradeIncome:30_empire.js:1614 tradeRaw:30_empire.js:1623 goldBreak:30_empire.js:1637 treasLive:30_empire.js:1651 fmtK:30_empire.js:1653 renderGlog:30_empire.js:1655 goldBreakHTML:30_empire.js:1662 goldBreakTxt:30_empire.js:1666 seasonNet:30_empire.js:1667 husbandryGoldFor:30_empire.js:1671 SEASON_DBL_TIER:30_empire.js:1675 tierGoldFor:30_empire.js:1677 seasonDblGold:30_empire.js:1681 SEASON_DBL_TYPE:30_empire.js:1682 boardMetrics:30_empire.js:1683 poCurKey:30_empire.js:1691 poBandName:30_empire.js:1692 poActiveKeys:30_empire.js:1694 poActiveEffects:30_empire.js:1696 poImmune:30_empire.js:1703 poDoubled:30_empire.js:1704 renderPO:30_empire.js:1706 curSeason:40_realm_data.js:4 stepSeason:40_realm_data.js:5 playerOfBoard:40_realm_data.js:8 igVal:40_realm_data.js:9 eraIdx:40_realm_data.js:10 playerAtWar:40_realm_data.js:11 influenceRowsBase:40_realm_data.js:12 influenceRows:40_realm_data.js:43 influenceTotal:40_realm_data.js:48 poModRows:40_realm_data.js:51 totTipSimple:40_realm_data.js:78 totTip:40_realm_data.js:81 epSources:40_realm_data.js:92 topSuz:40_realm_data.js:105 royalMarriage:40_realm_data.js:108 sameAlliance:40_realm_data.js:113 poFloor:40_realm_data.js:116 applyPOFloor:40_realm_data.js:117 epRows:40_realm_data.js:118 poModTotal:40_realm_data.js:131 dpButtons:40_realm_data.js:132 renderDP:40_realm_data.js:135 dpSpend:40_realm_data.js:138 renderMiniStand:40_realm_data.js:145 renderInfluence:40_realm_data.js:159 renderPOMods:40_realm_data.js:163 siegeState:40_realm_data.js:175 siegeCalc:40_realm_data.js:176 siegeHTML:40_realm_data.js:194 realmTimers:40_realm_data.js:209 timerAddHTML:40_realm_data.js:210 boardTimerRows:40_realm_data.js:214 siegeResolveHTML:40_realm_data.js:220 activeTimersHTML:40_realm_data.js:227 seasonsHTML:40_realm_data.js:233 costsHTML:40_realm_data.js:236 wireDashExtras:40_realm_data.js:239 renderDash:40_realm_data.js:267 domBand:40_realm_data.js:270 mods:40_realm_data.js:273 diplo:40_realm_data.js:278 pk:40_realm_data.js:279 isVassal:40_realm_data.js:281 vassalsOf:40_realm_data.js:282 effPair:40_realm_data.js:283 pairOf:40_realm_data.js:286 pname:40_realm_data.js:287 allianceLabel:40_realm_data.js:288 pboard:40_realm_data.js:289 tradeBorderOK:40_realm_data.js:291 hasRoad:40_realm_data.js:292 eraRank:40_realm_data.js:295 allianceEra:40_realm_data.js:296 allianceOK:40_realm_data.js:297 pairFlags:40_realm_data.js:298 dStatus:40_realm_data.js:307 diploHTML:40_realm_data.js:311 wireDiplo:40_realm_data.js:368 newSide:50_battle.js:4 battle:50_battle.js:5 bq:50_battle.js:7 bqAdd:50_battle.js:8 bqSideName:50_battle.js:9 bqLoad:50_battle.js:12 sideHex:50_battle.js:15 bqStart:50_battle.js:19 banditArmy:50_battle.js:22 banditEra:50_battle.js:27 armBandits:50_battle.js:28 sideArmy:50_battle.js:35 blog:50_battle.js:40 d10:50_battle.js:41 seizeForced:50_battle.js:42 facCombat:50_battle.js:45 apMod:50_battle.js:58 sideUnlocks:50_battle.js:59 sideDomains:50_battle.js:65 standingFxOf:50_battle.js:66 hasArmyTok:50_battle.js:71 eqOptions:50_battle.js:72 eqCode:50_battle.js:83 eqNow:50_battle.js:86 dualOn:50_battle.js:90 eqWeapon:50_battle.js:91 tacAllowed:50_battle.js:100 tacOK:50_battle.js:105 randomTacticPool:50_battle.js:106 sideCalc:50_battle.js:109 pickKey:50_battle.js:261 viewerSide:50_battle.js:262 mdLite:50_battle.js:285 fmtModLong:50_battle.js:287 fmtMod:50_battle.js:290 dieRow:50_battle.js:295 rollNeed:50_battle.js:297 rollHTML:50_battle.js:298 battleSprites:50_battle.js:306 datasheetHTML:50_battle.js:313 tacticPickHTML:50_battle.js:370 whatIf:50_battle.js:403 woundChance:50_battle.js:409 tacPair:50_battle.js:415 tacCardBody:50_battle.js:420 tacDetailHTML:50_battle.js:432 rollGuideHTML:50_battle.js:445 narrPl:50_battle.js:474 narrDisp:50_battle.js:475 narrate:50_battle.js:476 rollMeta:50_battle.js:482 chronicleHTML:50_battle.js:493 sideHTML:50_battle.js:496 fatiguesNow:50_battle.js:517 sideNm:50_battle.js:519 bFlow:50_battle.js:524 actionsHTML:50_battle.js:563 battleOutcome:50_battle.js:592 resultHTML:50_battle.js:599 sideTile:50_battle.js:617 onHill:50_battle.js:618 onGrass:50_battle.js:619 seizeDefault:50_battle.js:621 seizeHTML:50_battle.js:622 bCmdHTML:50_battle.js:629 tacEdge:50_battle.js:636 tacticExplainHTML:50_battle.js:642 battleRulesHTML:50_battle.js:656 renderBattle:50_battle.js:660 incoming:50_battle.js:690 roll:50_battle.js:693 autoApplyCas:50_battle.js:759 ripN:50_battle.js:761 addRip:50_battle.js:762 setPendCas:50_battle.js:764 pendCas:50_battle.js:765 ripCasN:50_battle.js:767 applyCasNow:50_battle.js:768 applyCas:50_battle.js:770 rollBreak:50_battle.js:772 rollBreakBtn:50_battle.js:775 endSkirmish:50_battle.js:777 endBattle:50_battle.js:798 wireBattle:50_battle.js:839 edictTimerLen:50_battle.js:898 edictChoices:50_battle.js:900 edictTotal:50_battle.js:906 edictOwners:50_battle.js:907 bumpRenown:50_battle.js:908 edictCond:50_battle.js:913 edictHeld:50_battle.js:917 edictPend:50_battle.js:922 edictIsPending:50_battle.js:923 edictTick:50_battle.js:925 edictTaken:50_battle.js:930 edictWatch:50_battle.js:931 checkEdicts:50_battle.js:935 edictNewsText:50_battle.js:943 edictBoardHTML:50_battle.js:944 wireEdicts:50_battle.js:973 currentEra:50_battle.js:987 pMark:50_battle.js:995 domTrackHTML:50_battle.js:997 standingEffectsHTML:50_battle.js:1006 renderRenown:50_battle.js:1019 bfLine:52_battlefield.js:9 bfForm:52_battlefield.js:12 bfXY:52_battlefield.js:20 bfPlace:52_battlefield.js:23 bfTerrain:52_battlefield.js:34 bfSideInfo:52_battlefield.js:38 bfFigure:52_battlefield.js:49 bfGround:52_battlefield.js:53 bfCamp:52_battlefield.js:58 bfBuild:52_battlefield.js:62 bfMount:52_battlefield.js:74 bfUpdate:52_battlefield.js:80 bfGear:52_battlefield.js:109 bfFeedPaint:52_battlefield.js:114 bfToast:52_battlefield.js:117 bfDefLine:52_battlefield.js:123 bfReport:52_battlefield.js:129 bfSeen:52_battlefield.js:135 bfFx:52_battlefield.js:137 bfPick:52_battlefield.js:138 bfEffects:52_battlefield.js:147 aiOn:55_ai.js:6 aiProfile:55_ai.js:7 aiDriver:55_ai.js:9 aiNote:55_ai.js:10 aiCashOutlook:55_ai.js:15 aiMem:55_ai.js:20 aiRel:55_ai.js:21 aiRelAdd:55_ai.js:22 aiLearn:55_ai.js:24 aiStandSteps:55_ai.js:35 aiNextMonument:55_ai.js:41 aiStandGoals:55_ai.js:44 aiPickDomain:55_ai.js:57 aiSpendDP:55_ai.js:63 aiCouncilPick:55_ai.js:66 aiEraAllows:55_ai.js:78 aiFoe:55_ai.js:80 aiFriend:55_ai.js:82 aiHoldNet:55_ai.js:84 aiHoldPO:55_ai.js:87 aiHoldValue:55_ai.js:88 aiFaithFloor:55_ai.js:90 aiBuildPick:55_ai.js:91 aiImprovePick:55_ai.js:96 aiTreatyType:55_ai.js:101 aiTreatyAccept:55_ai.js:110 aiApplyTreaty:55_ai.js:121 aiOffensive:55_ai.js:131 aiKit:55_ai.js:132 aiGearRank:55_ai.js:143 aiOutfit:55_ai.js:149 aiMoveTargets:55_ai.js:161 aiMovable:55_ai.js:163 aiEngageSize:55_ai.js:168 aiMove:55_ai.js:170 aiPrioW:55_ai.js:199 aiScore:55_ai.js:200 aiSurvival:55_ai.js:203 aiPassChance:55_ai.js:210 aiArch:55_ai.js:218 aiStyle:55_ai.js:222 aiGearGain:55_ai.js:224 aiHoldTags:55_ai.js:231 aiActTags:55_ai.js:245 aiFaithNeed:55_ai.js:262 aiBanditThreat:55_ai.js:271 aiBanditNear:55_ai.js:278 aiSit:55_ai.js:281 aiCandidates:55_ai.js:291 aiIntents:55_ai.js:386 aiDeclare:55_ai.js:394 aiPlanFor:55_ai.js:400 aiPerform:55_ai.js:402 aiVoteWant:55_ai.js:421 aiVoteAll:55_ai.js:434 aiTacticEval:55_ai.js:447 aiTacticU:55_ai.js:453 aiTacticStance:55_ai.js:459 aiPickTactic:55_ai.js:465 aiBattleTick:55_ai.js:475 aiTick:55_ai.js:481 aiAfterRender:55_ai.js:497 mapClimate:60_map.js:17 mapPal:60_map.js:22 tLum:60_map.js:25 tTone:60_map.js:27 tLighten:60_map.js:28 tGlyph:60_map.js:31 tSwatch:60_map.js:36 mapState:60_map.js:43 hexDist:60_map.js:44 decodeGrid:60_map.js:47 seedCode:60_map.js:57 generateMap:60_map.js:58 parseSeedCode:60_map.js:66 mapZoom:60_map.js:78 reachBonus:60_map.js:84 reachOwners:60_map.js:93 resShown:60_map.js:107 nodesMode:60_map.js:108 reachResources:60_map.js:110 settReachHexes:60_map.js:120 rawClaims:60_map.js:131 mapSprId:60_map.js:153 mapSprDefs:60_map.js:154 tMix:60_map.js:164 hStr:60_map.js:169 rng32:60_map.js:170 mapScatter:60_map.js:171 propPaths:60_map.js:190 pxSwatch:60_map.js:194 mapSpr:60_map.js:199 eqSVG:60_map.js:205 sprSVG:60_map.js:207 stIcon:60_map.js:216 armyGear:60_map.js:217 armyUFor:60_map.js:219 stDedup:60_map.js:224 stIconSVG:60_map.js:226 plateStatus:60_map.js:228 plateBox:60_map.js:229 mapPlate:60_map.js:231 settPlate:60_map.js:242 settBehind:60_map.js:253 settInsideMarks:60_map.js:257 mapBarHTML:60_map.js:272 terrOwners:60_map.js:283 terrFlags:60_map.js:285 unrestCamps:60_map.js:291 intrudersOf:60_map.js:293 settReach:60_map.js:297 settEcon:60_map.js:299 pillageCheck:60_map.js:308 pillageTargets:60_map.js:312 runPillage:60_map.js:315 armyStatus:60_map.js:328 mapMarkers:60_map.js:343 inspHTML:60_map.js:354 inspHead:60_map.js:357 inspCell:60_map.js:360 g:60_map.js:361 inspCan:60_map.js:362 inspArmy:60_map.js:363 settStatus:60_map.js:385 settStatusMarks:60_map.js:395 inspSett:60_map.js:399 envoyFor:60_map.js:435 settActionsHTML:60_map.js:438 armyMusterBtn:60_map.js:449 inspCamp:60_map.js:460 engageTargets:60_map.js:473 wireInsp:60_map.js:479 mapLayers:60_map.js:506 mapSVG:60_map.js:603 outlawReport:60_map.js:605 banditDomain:60_map.js:616 campKey:60_map.js:618 banditAutoHTML:60_map.js:620 armyName:60_map.js:629 syncMapTiers:60_map.js:631 mapLinkBad:60_map.js:638 mapLinksHTML:60_map.js:639 wireBanditAuto:60_map.js:650 banditAuto:60_map.js:656 BST:60_map.js:657 bLog:60_map.js:658 hk:60_map.js:660 mapSetts:60_map.js:661 cellPlayer:60_map.js:662 cellClaimed:60_map.js:664 pinNewCell:60_map.js:666 cellSett:60_map.js:672 mapArmies:60_map.js:675 cellArmy:60_map.js:676 cellTitle:60_map.js:679 byDist:60_map.js:683 isWild:60_map.js:687 wildZones:60_map.js:688 outlawZones:60_map.js:690 zoneOf:60_map.js:695 zoneOwners:60_map.js:696 outlawOwners:60_map.js:701 outlawOwner:60_map.js:703 outlawOf:60_map.js:705 campWild:60_map.js:707 wildCount:60_map.js:709 wildDone:60_map.js:710 autoDeploy:60_map.js:716 placeWildOutlaw:60_map.js:742 rescatterWild:60_map.js:764 pieceAura:60_map.js:768 wardMap:60_map.js:774 wardsOf:60_map.js:775 wardRoom:60_map.js:776 wardFill:60_map.js:778 wardCand:60_map.js:780 garrisonBattles:60_map.js:786 presHexes:60_map.js:790 wardAuto:60_map.js:794 wardPrune:60_map.js:804 wardMarks:60_map.js:806 campInRange:60_map.js:818 settleWhere:60_map.js:823 hexFree:60_map.js:827 spawnCamp:60_map.js:828 growCamps:60_map.js:830 expandOutlaw:60_map.js:835 immuneUprising:60_map.js:838 banditTargetMods:60_map.js:839 cunningAction:60_map.js:841 endorsedExtort:60_map.js:842 banditSpared:60_map.js:845 banditAct:60_map.js:847 runBanditMechanics:60_map.js:879 banditSpeed:60_map.js:899 banditAuraList:60_map.js:901 banditRun:60_map.js:908 moveCamp:60_map.js:916 moveBandit:60_map.js:919 banditReturn:60_map.js:927 banditSiegeTimer:60_map.js:932 banditArmyKeys:60_map.js:935 banditMoves:60_map.js:936 banditSkims:60_map.js:973 provinceCampExtort:60_map.js:983 creditSkims:60_map.js:988 envoyOutcome:60_map.js:995 banditCunningHTML:60_map.js:1000 dieLookup:60_map.js:1017 terrainTablesHTML:60_map.js:1020 mapToolsHTML:60_map.js:1043 banditPanelHTML:60_map.js:1077 mapAsP:60_map.js:1093 mapEditBlock:60_map.js:1094 mapGuard:60_map.js:1103 guarded:60_map.js:1105 mapCellClick:60_map.js:1107 wireMap:60_map.js:1135 srcKeys:70_rules.js:6 srcMatch:70_rules.js:13 srcHas:70_rules.js:14 srcRows:70_rules.js:16 bordersOf:70_rules.js:20 poCap:70_rules.js:24 poTextFloor:70_rules.js:25 siegeTextMods:70_rules.js:28 siegeWinterOK:70_rules.js:35 siegeDoubleOK:70_rules.js:36 actRestrict:70_rules.js:38 actRiders:70_rules.js:53 settById:70_rules.js:65 besiegeExempt:70_rules.js:67 settBesieged:70_rules.js:68 armySieging:70_rules.js:70 armyBesieged:70_rules.js:72 armyStateTags:70_rules.js:73 armyHeld:70_rules.js:83 armyBlocked:70_rules.js:86 immuneBlocked:70_rules.js:87 cellBlocked:70_rules.js:88 blockedMoveFails:70_rules.js:90 garrisonSizes:70_rules.js:94 hasGarrisons:70_rules.js:95 garrisonGear:70_rules.js:97 garrisonOf:70_rules.js:98 garrisonsOf:70_rules.js:102 garrisonCard:70_rules.js:103 standingOnceRows:70_rules.js:124 onceEffects:70_rules.js:126 onceState:70_rules.js:127 onceWindowNow:70_rules.js:131 onceHTML:70_rules.js:132 onceUse:70_rules.js:143 noteAdd:70_rules.js:152 recoupNote:70_rules.js:154 UPKEEP:70_rules.js:161 SUPPLY:70_rules.js:162 blackMarketReact:70_rules.js:163 extortGold:70_rules.js:171 danegeldRows:70_rules.js:182 loans:70_rules.js:191 loanReqs:70_rules.js:192 loanTerms:70_rules.js:193 loanInterest:70_rules.js:196 loanOK:70_rules.js:198 lentThisTurn:70_rules.js:199 runLoans:70_rules.js:200 loanAmtIn:70_rules.js:206 loansHTML:70_rules.js:207 lendNow:70_rules.js:228 autoExtortRows:70_rules.js:248 extortSlots:70_rules.js:257 exTargets:70_rules.js:260 extortTargetRows:70_rules.js:261 extortCardHTML:70_rules.js:267 runAutoExtort:70_rules.js:287 firstDoubtRed:70_rules.js:315 fdState:70_rules.js:319 gainDoubt:70_rules.js:322 fdGold:70_rules.js:326 siegeOn:70_rules.js:330 endSettlementSieges:70_rules.js:331 besiegedCount:70_rules.js:332 pById:70_rules.js:333 nextId:70_rules.js:334 captureTransfer:70_rules.js:335 sackWards:70_rules.js:347 sackApply:70_rules.js:352 banditSack:70_rules.js:368 resolveRealm:70_rules.js:380 sackLocks:70_rules.js:387 armyHex:70_rules.js:391 settHex:70_rules.js:392 musterLimit:70_rules.js:393 musterTick:70_rules.js:401 musterStep:70_rules.js:404 hasMusterField:70_rules.js:411 charterFlags:70_rules.js:414 selArmy:70_rules.js:437 canMoveArmy:70_rules.js:438 armyBesiegeExempt:70_rules.js:440 canEnterSett:70_rules.js:442 armyInside:70_rules.js:444 enterCheck:70_rules.js:447 freeHexNear:70_rules.js:449 kickOut:70_rules.js:452 armiesInside:70_rules.js:455 terrPen:70_rules.js:457 terrBlocked:70_rules.js:458 terrWaterStop:70_rules.js:459 terrStrain:70_rules.js:460 provinceOf:70_rules.js:462 moveTraits:70_rules.js:464 speedOf:70_rules.js:467 hexNb:70_rules.js:499 auraSources:70_rules.js:503 moveRange:70_rules.js:513 moveInfo:70_rules.js:548 moveStops:70_rules.js:551 moveEndTriggers:70_rules.js:556 moveArmyTo:70_rules.js:565 moveOverlay:70_rules.js:587 movePanelHTML:70_rules.js:600 set:70_rules.js:611 computeAll:70_rules.js:612 sceneInfra:80_scene_shell.js:14 wardChains:80_scene_shell.js:20 sceneLots:80_scene_shell.js:27 renderEsBar:80_scene_shell.js:40 sceneArmies:80_scene_shell.js:48 renderScene:80_scene_shell.js:55 renderSettlements:80_scene_shell.js:172 lockTarget:80_scene_shell.js:235 lockBlock:80_scene_shell.js:244 adminUI:80_scene_shell.js:257 firstHostOpen:80_scene_shell.js:273 firstHostBtn:80_scene_shell.js:274 hudSign:80_scene_shell.js:280 hudData:80_scene_shell.js:281 hudTips:80_scene_shell.js:290 renderHUD:80_scene_shell.js:303 ageStripHTML:80_scene_shell.js:323 setupOn:80_scene_shell.js:337 renderSetup:80_scene_shell.js:338 checkedIn:80_scene_shell.js:366 checkinFD:80_scene_shell.js:367 checkinTxt:80_scene_shell.js:373 checkinHTML:80_scene_shell.js:374 setupHoldHTML:80_scene_shell.js:381 renderTurnStrip:80_scene_shell.js:403 syncBoardEndBtn:80_scene_shell.js:435 mnavSync:80_scene_shell.js:451 herName:80_scene_shell.js:461 herKey:80_scene_shell.js:462 lumOf:80_scene_shell.js:463 herMix:80_scene_shell.js:467 herN:80_scene_shell.js:469 herPaths:80_scene_shell.js:470 heraldOf:80_scene_shell.js:475 mapBanner:80_scene_shell.js:478 pTok:80_scene_shell.js:481 inboxItems:85_ux.js:10 renderInbox:85_ux.js:25 evIn:85_ux.js:44 hudPopBack:85_ux.js:59 hudPopFill:85_ux.js:61 hudPop:85_ux.js:88 hudPopClose:85_ux.js:89 renderChrome:85_ux.js:95 welcomeOn:86_welcome.js:11 welcomeLinks:86_welcome.js:15 welcomeClose:86_welcome.js:17 welcomeProfile:86_welcome.js:20 culHer:86_welcome.js:23 domDots:86_welcome.js:26 radarSVG:86_welcome.js:27 heritagesFor:86_welcome.js:35 seatCard:86_welcome.js:37 seatView:86_welcome.js:46 culDetail:86_welcome.js:51 profileView:86_welcome.js:64 welcomeRender:86_welcome.js:74 welcomeClick:86_welcome.js:86 undoSnap:90_app.js:5 undoRecord:90_app.js:7 undoRebase:90_app.js:13 undoScoped:90_app.js:14 undoApply:90_app.js:15 doUndo:90_app.js:32 doRedo:90_app.js:33 undoButtons:90_app.js:34 actSnap:90_app.js:47 actRebase:90_app.js:48 actJoin:90_app.js:50 actSchedule:90_app.js:53 fmtG:90_app.js:54 boardDiff:90_app.js:55 actFlush:90_app.js:87 gameAllowed:90_app.js:104 gameData:90_app.js:105 refreshGames:90_app.js:106 gameReplace:90_app.js:109 newGameState:90_app.js:114 isReady:90_app.js:140 readyCheck:90_app.js:141 gslug:90_app.js:155 kwify:90_app.js:168 wikiA:90_app.js:179 gkHtml:90_app.js:180 openFromHash:90_app.js:199 setLift:90_app.js:230 gkShow:90_app.js:239 gkHide:90_app.js:243 gkFor:90_app.js:244 chatHdr:90_app.js:303 chatTargets:90_app.js:309 chatParse:90_app.js:311 chatColor:90_app.js:319 chatLine:90_app.js:320 chatRender:90_app.js:324 chatSys:90_app.js:330 chatComplete:90_app.js:345
```
