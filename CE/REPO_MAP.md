# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-10-28 · data VERSION `0.4.9.9.13-d10-S` · HEAD `d620b0e 2026-10-28`

Hand-written orientation: `CLAUDE.md` (same folder). Paths below are relative to the repo root.

## 1. Folder tree

```
./  (12 files)
  0.4.8 Updated Docs/  (7 files)
  0.4.8.1/  (36 files)
  Assets/  (102 files, generated/assets — not indexed)
  CE/  (39 files)
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
    references/  (53 files)
      board/  (2 files)
        js/  (14 files)
      fonts/  (16 files, generated/assets — not indexed)
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
| `CE\CHANGES.md` | 77 | Changes in this bundle |
| `CE\CLAUDE.md` | 68 | CLAUDE.md — Renown repo orientation (lives in `CE/`; paths below are relative to `CE/`) |
| `CE\COMPREHENSIVE_RULES_OUTLINE.md` | 180 | Renown — Comprehensive Rules: outline |
| `CE\ENVOY_WINDOW_REVIEW.md` | 80 | Envoy timing windows — review list |
| `CE\HOLDING_MECHANICS_AUDIT.md` | 54 | Holding Mechanics Audit |
| `CE\INFLUENCE_WORDING_AUDIT.md` | 76 | Influence / Authority wording audit |
| `CE\PRONOUN_WORDING_AUDIT.md` | 85 | "You / this player / the target" wording audit |
| `CE\REPO_MAP.md` | 944 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE\RULES_push.md` | 649 | Renown |
| `CE\RULES_push_simple.md` | 688 | Renown |
| `CE\RULES_reorganized_6.md` | 638 | Renown |
| `CE\SIMPLE_NODES.PY` | 1 |  |
| `CE\TASK8_NOTES.md` | 152 | claude_task_8 — what changed, open items |
| `CE\TASK9_NOTES.md` | 83 | claude_task_9 — Rules.docx pass: what changed, open items |
| `CE\build_all_CE.bat` | 525 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE\ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\infra.py` | 109 |  |
| `CE\keyword_bloat_v2.md` | 101 | Keyword Bloat — v2 |
| `CE\parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE\patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE\rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE\renown_data.py` | 5111 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d10.py` | 5111 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d8.py` | 2801 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_server.bat` | 16 | renown_server.bat - (re)start the Renown board server in WSL. |
| `CE\repo_map.py` | 250 | repo_map.py — write REPO_MAP.md next to this file (CE/, beside CLAUDE.md): a generated index of the Renown repo for |
| `CE\run_tournament_d10.bat` | 108 | Renown d10 tournament runner  —  CE build |
| `CE\run_tournament_d10.py` | 131 | run_tournament_d10.py — run the Renown tournament against the d10 build. |
| `CE\sprites.py` | 5816 | sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene). |
| `CE\verify_d10.py` | 168 | verify_d10.py — prove the CE wiring is live before spending hours on a run. |
| `CE\.claude\launch.json` | 43 |  |
| `CE\Combatv4\analysis.py` | 2125 | Analysis module for tournament results. |
| `CE\Combatv4\batch_engine.py` | 1633 | Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays, |
| `CE\Combatv4\combat_kernel_d10.py` | 268 | combat_kernel.py — SHARED numba kernels for both combat engines. |
| `CE\Combatv4\combat_morale_d10.py` | 155 | combat_morale.py — SHARED morale phase for both combat engines (C2, subsystem 2). |
| `CE\Combatv4\combat_primitives_d10.py` | 147 | combat_primitives.py — SHARED rules-math layer for both combat engines (C2). |
| `CE\Combatv4\dice_config.py` | 116 | dice_config — single source for die size across both combat engines. |
| `CE\Combatv4\loadouts.py` | 1214 | Loadout generator for the combat tournament. |
| `CE\Combatv4\make_d10_data.py` | 172 | Generate renown_data_d10.py from renown_data_CE.py. |
| `CE\Combatv4\make_d10_engines.py` | 143 | Generate *_d10.py engine files with FACES parameterised. |
| `CE\Combatv4\normalized_matrix.py` | 277 | Normalized symmetric tactic matrix. |
| `CE\Combatv4\playstyles.py` | 784 | Playstyle module — playstyles drive tactic selection in combat. |
| `CE\Combatv4\renown_combat_d10.py` | 563 | Renown combat simulator. |
| `CE\Combatv4\run_tournament.py` | 197 | Standalone Renown tournament runner. |
| `CE\Combatv4\tactics_analysis.py` | 54 | Tactics analysis helpers for the Renown Combat Lab. |
| `CE\Combatv4\tournament_vec.py` | 356 | Vectorized tournament runner — same interface as tournament.py but ~4x faster |
| `CE\Combatv4\vectorized_combat_d10.py` | 1992 | Vectorized matchup runner. |
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
| `CE\Simulator\engine\sim_core.js` | 270 | sim_core.js — appended inside the settlement board's script (same scope: D, tSim, aiTick, roll, … are all in reach). |
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
| `CE\ask-the-bot\factions_table.csv` | 43 | columns: Faction,Difficulty,Strength,Mechanic |
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
| `CE\references\build_wiki.py` | 1643 | build_wiki.py — multi-page linked HTML wiki from RULES.md + renown_data. |
| `CE\references\card_copies.py` | 68 | card_copies.py — print-quantity logic for pursuit cards, driven by the spec |
| `CE\references\card_sheet.py` | 679 | Renown — Specialization card sheet generator. |
| `CE\references\ce_paths.py` | 123 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\references\combat_sheet.py` | 352 | combat_sheet.py — Renown combat quick-reference (print & laminate). |
| `CE\references\combine_docx.py` | 257 | combine_docx.py — append the Compendium after the Rules doc as one book: |
| `CE\references\compendium_data.json` | 3273 |  |
| `CE\references\display_pdf.py` | 90 | display_pdf.py — NAME_DISPLAY for every reportlab sheet (cards, tiles, equipment, combat). |
| `CE\references\docx_tables.py` | 688 | docx_tables.py — generate Word table fragments (OOXML) from renown_data. |
| `CE\references\domain_board.py` | 341 | domain_board.py - landscape Domain Standing Board. |
| `CE\references\effect_registry.py` | 359 | effect_registry.py -- every rules-text pattern the settlement board acts on, matched once at build time. |
| `CE\references\equipment_sheet.py` | 691 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `CE\references\faction_sheet.py` | 447 | Renown — Faction card sheet generator. |
| `CE\references\faq_export.py` | 439 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `CE\references\gen_compendium.py` | 185 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `CE\references\gen_layout.py` | 374 | gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data. |
| `CE\references\gen_layout_roots.py` | 123 | gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it. |
| `CE\references\gen_settlement_board.py` | 1033 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE\references\generate_cards.py` | 93 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `CE\references\host_sheet.py` | 452 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `CE\references\infra_board.py` | 134 | infra_board.py - landscape Infrastructure Board. |
| `CE\references\keyword_audit.py` | 96 | Exact per-strike-die model of the Renown CE strike chain (rules text as written), |
| `CE\references\layout.json` | 1421 |  |
| `CE\references\layout_roots.json` | 1380 |  |
| `CE\references\layout_simple.json` | 1539 |  |
| `CE\references\md_to_docx.py` | 342 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `CE\references\package-lock.json` | 205 |  |
| `CE\references\package.json` | 6 |  |
| `CE\references\parity_efx.js` | 54 | parity_efx.js — replays effect_registry.py's patterns with JavaScript RegExp, the way the board used to read text at |
| `CE\references\patch_pursuit_domains.py` | 58 | patch_pursuit_domains.py |
| `CE\references\playstyle_reference.py` | 457 | playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture). |
| `CE\references\pursuit_tiles.py` | 278 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `CE\references\reference_sheets.py` | 873 | Renown — Reference sheet generators. |
| `CE\references\render_tree.py` | 272 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `CE\references\rule_numbers.py` | 250 | rule_numbers.py — MTG-style rule numbers for the rules markdown, computed at render time. |
| `CE\references\server.py` | 501 | Renown settlement-board server  —  stdlib only, no pip installs. |
| `CE\references\settlement_board.html` | — | generated HTML (1816 KB) |
| `CE\references\settlement_mats.py` | 302 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `CE\references\spec_tree_sheet.py` | 1183 | Renown — Specialization Tree renderer. |
| `CE\references\svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `CE\references\sync_derived.py` | 88 | sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES. |
| `CE\references\tactic_sheet.py` | 446 | Renown — Tactic card sheet generator (v3). |
| `CE\references\wiki_markers.py` | 291 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
| `CE\references\world.txt` | 1517 |  |
| `CE\references\worldtxt.py` | 328 | worldtxt.py — parse the hand-maintained world.txt lore book into structured |
| `CE\references\board\body.html` | 214 |  |
| `CE\references\board\js\00_core.js` | 51 | __DATA__*/; |
| `CE\references\board\js\10_table.js` | 832 | ===================== TABLE: seating, Council & Envoy phases ===================== |
| `CE\references\board\js\15_realm.js` | 464 | ===================== REALM: the play surface ===================== |
| `CE\references\board\js\16_tally.js` | 132 | ===================== INTRIGUE & TALLY PHASES (RULES: Envoy Phase steps 3 and 5) ===================== |
| `CE\references\board\js\20_state.js` | 554 | ---- state: multiplayer dashboard ---- |
| `CE\references\board\js\30_empire.js` | 1692 | ---- catalog ---- |
| `CE\references\board\js\40_realm_data.js` | 397 | ---- Dashboards view ---- |
| `CE\references\board\js\50_battle.js` | 704 | ---- Battle ---- |
| `CE\references\board\js\55_ai.js` | 498 | ---- AI players: culture-driven bots for seats marked AI (and, later, the headless simulator) ---- |
| `CE\references\board\js\60_map.js` | 1108 | ---- Map view ---- |
| `CE\references\board\js\70_rules.js` | 539 | ===================== EFFECT PLUMBING: the effect registry (references/effect_registry.py) ===================== |
| `CE\references\board\js\80_scene_shell.js` | 478 | ---- pixel scene: every settlement of the active player, drawn from sprites.py (every theme) ---- |
| `CE\references\board\js\85_ux.js` | 97 | ===================== CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper ===================== |
| `CE\references\board\js\90_app.js` | 368 | ===================== UNDO / REDO ===================== |
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
| `CE\worldbuilding\renown_worldlore.py` | 3608 | renown_worldlore.py |
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
| `RenownWiki\rules-core-principles.html` | 81 | Core Principles — Renown |
| `RenownWiki\rules-cunning-actions.html` | 23 | Cunning Actions — Renown |
| `RenownWiki\rules-diplomacy-actions.html` | 25 | Diplomacy Actions — Renown |
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
| `RenownWiki\rules-siege-warfare.html` | 57 | Siege Warfare — Renown |
| `RenownWiki\rules-table-setup.html` | 26 | Table Setup — Renown |
| `RenownWiki\rules-territory-terrain.html` | 28 | Territory &amp; Terrain — Renown |
| `RenownWiki\rules-the-turn.html` | 78 | The Turn — Renown |
| `RenownWiki\rules-trade-income.html` | 39 | Trade &amp; Income — Renown |
| `RenownWiki\rules-treasury-upkeep.html` | 35 | Treasury &amp; Upkeep — Renown |
| `RenownWiki\search.js` | 7 |  |
| `RenownWiki\seasons-ref.html` | 22 | Seasons — Renown |
| `RenownWiki\settlement_board.html` | — | generated HTML (1816 KB) |
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
| `SIMPLE` | 4 | bool | True |
| `VERSION` | 6 | str | '0.4.9.9.13-d10-S' |
| `BLUNDER_THR` | 34 | int | 10 |
| `DICE_PROVENANCE` | 35 | str | 'd10 / Focused 10+ / Parry 8+ / Recover  |
| `SACK_EXTORT_PER_TIER` | 38 | int | 2000 |
| `INTERCEPT_EXTORT_PER_CRAFT` | 39 | int | 100 |
| `WEALTH_EDICT_GOLD` | 40 | int | 50000 |
| `MUSTER_RANGE` | 41 | int | 2 |
| `MARCH_MULTIPLIER` | 42 | int | 2 |
| `PO_MIN` | 43 | int | -10 |
| `PO_MAX` | 44 | int | 10 |
| `INITIATIVE_MIN` | 45 | int | -2 |
| `INITIATIVE_MAX` | 46 | int | 2 |
| `STANDING_THRESHOLDS` | 47 | dict | 4 |
| `STANDING_RANK` | 56 | dict | 4 |
| `STEADY` | 61 | str | 'Steady' |
| `UNWIELDY` | 62 | str | 'Unwieldy' |
| `TWO_H` | 63 | str | '2H' |
| `SHATTER_ARMOR` | 64 | str | 'Deadly' |
| `UNSTOPPABLE` | 65 | str | 'Unstoppable' |
| `CLEAVE` | 66 | str | 'Cleave' |
| `POISON` | 67 | str | 'Poison' |
| `NIMBLE` | 68 | str | 'Nimble' |
| `DRILLED` | 69 | str | 'Drilled' |
| `DESTROY_SHIELD` | 70 | str | 'Destroy Shield' |
| `BLUNDER` | 71 | str | 'Blunder' |
| `ONE_SHOT` | 72 | str | 'One-Shot' |
| `DEFLECT` | 73 | str | 'Deflect' |
| `IMMUNE_PANIC` | 74 | str | 'Immune Panic' |
| `UNBREAKABLE` | 75 | str | 'Unbreakable' |
| `PARRY` | 76 | str | 'Parry' |
| `RIPOSTE` | 77 | str | 'Riposte' |
| `NO_PARRY` | 78 | str | 'Awkward' |
| `RECOVER` | 79 | str | 'Recover' |
| `SERRATED` | 80 | str | 'Serrated' |
| `SERRATED_MOD` | 81 | int | 2 |
| `ENDURING` | 82 | str | 'Enduring' |
| `STRAIN` | 83 | str | 'Strain' |
| `MINUS_1_TBH` | 84 | str | 'Shielded' |
| `PLANISHING` | 85 | str | 'Planishing' |
| `FATIGUE_TOKEN` | 86 | str | 'Fatigue Token' |
| `CRUSADER` | 87 | str | 'Righteous Fervour' |
| `IMMUNE` | 89 | str | 'Immune' |
| `immune` | 90 | function |  |
| `NEGATE` | 95 | str | 'Negate' |
| `negate` | 96 | function |  |
| `IMMUNE_DESTROY_SHIELD` | 102 | str | 'Immune Destroy Shield' |
| `IMMUNE_UNWIELDY` | 103 | str | 'Immune Unwieldy' |
| `IMMUNE_STRAIN` | 104 | str | 'Immune Strain' |
| `NEGATE_UNSTOPPABLE` | 106 | str | 'Immune Unstoppable' |
| `NEGATE_TEMPERED` | 108 | str | 'Negate Planishing' |
| `NEGATE_RIPOSTE` | 109 | str | 'Negate Riposte' |
| `NEGATE_SHIELDED` | 110 | str | 'Negate Shielded' |
| `MINUS_1_PARRY` | 111 | str | '-1 to Parry' |
| `HALFSWORD` | 112 | str | 'Halfsword' |
| `DUAL_WIELD` | 113 | str | 'Dual Wield' |
| `FLORENTINE` | 114 | str | 'Florentine' |
| `PIVOTAL` | 115 | str | 'Focused' |
| `GLOSSARY` | 118 | dict | 165 |
| `MORALE_GLOSSARY` | 261 | dict | 4 |
| `ARMY_MAX_RETINUES` | 287 | int | 25 |
| `FRONT_LINE_MAX` | 288 | int | 10 |
| `RESERVE_MAX` | 289 | int | 5 |
| `MORALE_DICE_MAX` | 290 | int | 5 |
| `PANIC_CASUALTY_THRESHOLD` | 291 | int | 5 |
| `ENDURANCE_REGAIN` | 292 | int | 2 |
| `RETINUES` | 296 | dict | 4 |
| `WEAPONS` | 303 | dict | 19 |
| `RANGED` | 325 | dict | 6 |
| `SHIELDS` | 335 | dict | 6 |
| `ARMORS` | 344 | dict | 6 |
| `TIERS` | 355 | list | 5 |
| `TIER_UNLOCK` | 356 | dict | 5 |
| `STANDING_EFFECTS` | 367 | dict | 6 |
| `TACTIC_MATRIX` | 392 | dict | 49 |
| `TACTICS` | 451 | list | 7 |
| `TACTIC_NOTES` | 453 | dict | 0 |
| `CULTURE_SELF_MADE` | 470 | str | 'Self-made' |
| `CULTURES` | 472 | dict | 15 |
| `NODES` | 638 | dict | 129 |
| `SIMPLE_NODES` | 1666 | dict | 129 |
| `HOLDING_GROUPS` | 2629 | dict | 9 |
| `SCOPES` | 2646 | tuple | 3 |
| `SCOPE_BY_TYPE` | 2647 | dict | 2 |
| `LINE_LABELS` | 2651 | dict | 28 |
| `lines_of` | 2682 | function |  |
| `LEGACY_NODES` | 2686 | dict | 108 |
| `REQ_KEY` | 2691 | str | 'infrastructure_req' |
| `REQ_LABEL` | 2692 | str | 'Infrastructure Req' |
| `TYPE_ORDER` | 2694 | list | 10 |
| `CHAIN_TERM` | 2697 | str | 'Mastery Chain' |
| `PURSUIT_TERM` | 2699 | tuple | 2 |
| `node_parents` | 2701 | function |  |
| `get_data` | 2721 | function |  |
| `MONUMENT_SUMMARY` | 2730 | dict | 21 |
| `WONDER_SUMMARY` | 2756 | dict | 4 |
| `FACTIONS` | 2766 | dict | 41 |
| `INFRASTRUCTURE` | 3267 | dict | 20 |
| `WONDERS` | 3400 | dict | 4 |
| `INFRA_TIERS` | 3401 | list | 5 |
| `SETTLEMENTS` | 3409 | dict | 5 |
| `PRESENCE_RANGE` | 3420 | int | 2 |
| `WARD_MODEL` | 3424 | str | 'range1' |
| `WARD_RULES` | 3425 | dict | 2 |
| `WARD_RULE` | 3433 | str | 'A Settlement Ward is a slot that holds  |
| `FAITH_FICKLE_PO` | 3435 | int | 0 |
| `ERAS` | 3438 | dict | 4 |
| `PO_BANDS` | 3455 | dict | 11 |
| `po_scale` | 3474 | function |  |
| `po_value` | 3481 | function |  |
| `po_effect` | 3486 | function |  |
| `PUBLIC_ORDER` | 3493 | dict | 11 |
| `PUBLIC_ORDER_BY_ERA` | 3494 | dict | 4 |
| `PO_MODIFIERS` | 3500 | dict | 2 |
| `DOMAIN_BOARD` | 3518 | dict | 6 |
| `SEASONS` | 3556 | dict | 4 |
| `TRADE_REQUIRES_BORDER` | 3565 | bool | False |
| `TRADE_RULES` | 3566 | dict | 6 |
| `efficient_graph` | 3581 | function |  |
| `EFFICIENT_MULTI` | 3591 | dict | 119 |
| `EFFICIENT` | 3592 | dict | 119 |
| `BANDIT_CAMP_START` | 3600 | int | 10 |
| `BANDIT_CAMP_GOLD` | 3601 | int | 2000 |
| `BANDIT_ARMY_THRESHOLD` | 3602 | int | 25 |
| `BANDIT_GROWTH_PER_ERA` | 3603 | dict | 4 |
| `BANDIT_EQUIPMENT_PER_ERA` | 3604 | dict | 4 |
| `BANDITS` | 3605 | dict | 5 |
| `TIMERS` | 3613 | dict | 8 |
| `CHARTER_MIN_RANGE` | 3625 | int | 4 |
| `OUTLAW_BUFFER_RANGE` | 3626 | int | 2 |
| `HAMLET_RANGE` | 3627 | int | 2 |
| `OUTLAW_COUNTRY_START` | 3628 | int | 3 |
| `WILD_OUTLAW` | 3636 | dict | 9 |
| `wild_outlaw_count` | 3649 | function |  |
| `BANDIT_CAMP_REACH` | 3656 | str | 'province' |
| `VASSAL_EXCHANGE_CAP` | 3659 | int | 5000 |
| `VASSAL_INFLUENCE_TAKE` | 3660 | int | 3 |
| `BUILD_TIMERS` | 3664 | dict | 11 |
| `TERRAIN` | 3678 | dict | 7 |
| `MOVEMENT_MODIFIERS` | 3688 | dict | 6 |
| `TACTICAL_TERRAIN` | 3700 | dict | 7 |
| `TACTICAL_GLOBAL` | 3716 | list | 1 |
| `INFLUENCE_GAIN` | 3718 | dict | 9 |
| `ENVOY_OUTCOME_THRESHOLDS` | 3777 | dict | 4 |
| `CUNNING_EXTORT` | 3787 | int | 2000 |
| `CUNNING_EXTORT_ENDORSED` | 3788 | int | 4000 |
| `ENVOY_OUTCOMES` | 3789 | dict | 5 |
| `ACTIONS` | 3812 | dict | 23 |
| `TREATIES` | 4010 | dict | 5 |
| `ALLIANCE_RULES` | 4018 | list | 3 |
| `EDICT_STREAK_TURNS` | 4028 | int | 5 |
| `GAME_TURN_LIMIT` | 4029 | int | 50 |
| `EDICT_UNIQUE` | 4032 | bool | False |
| `EDICT_UNIQUE_RULE` | 4033 | str | 'Each Domain, Monument, or Wonder counts |
| `EDICTS` | 4036 | dict | 7 |
| `BANDIT_BEHAVIOR` | 4050 | dict | 8 |
| `PURSUIT_UPKEEP_DEFAULT` | 4073 | int | 100 |
| `PURSUIT_UPKEEP_BY_TYPE` | 4074 | dict | 4 |
| `UPKEEP_TRACKS` | 4084 | dict | 3 |
| `HOLDING_TIER_COST` | 4091 | dict | 4 |
| `holding_standing` | 4099 | function |  |
| `holding_cost` | 4105 | function |  |
| `holding_build_time` | 4113 | function |  |
| `HOLDING_COST_TEXT` | 4119 | str | 'by Standing: Untested 100 (Build Timer  |
| `pursuit_upkeep` | 4121 | function |  |
| `ARMY_UPKEEP_NOTE` | 4132 | str | "Net Army Upkeep = the sum of each Army' |
| `COSTS` | 4136 | dict | 12 |
| `PHASES` | 4156 | tuple | 5 |
| `STARTING_TURN_PHASE_OPENER` | 4157 | str | 'Council' |
| `STANDING_ARMY_SIEGE_MODIFIER` | 4159 | int | 1 |
| `EMPIRE_START_TIERS` | 4161 | tuple | 2 |
| `STARTING_TREASURY` | 4162 | int | 10000 |
| `SETUP_CAPITAL_PICKS` | 4165 | int | 1 |
| `SETUP_HAMLET_PICKS` | 4166 | int | 1 |
| `SETUP_HAMLET_HOLDINGS` | 4167 | tuple | 2 |
| `SETUP_HAMLET_TEXT` | 4168 | str | 'Common Land or Arable Land' |
| `HAMLET_REPEATABLE` | 4170 | tuple | 2 |
| `HAMLET_REPEATABLE_TEXT` | 4171 | str | 'Common Land or Arable Land' |
| `AGES` | 4177 | dict | 5 |
| `AGE_YEAR_SEASON` | 4184 | str | 'Spring' |
| `AGE_YEAR_ROLL_MEAN` | 4187 | float | 0.45 |
| `AGE_YEAR_ROLL_SD` | 4188 | float | 0.16666666666666666 |
| `CAPITAL_EDGE_RANGE` | 4189 | int | 4 |
| `BOARD_SIZES` | 4191 | dict | 3 |
| `SIEGE_CALCULUS` | 4197 | dict | 2 |
| `SIEGE_SOURCE_VALUES` | 4212 | dict | 3 |
| `NAME_DISPLAY` | 4242 | dict | 71 |
| `TIER_DISPLAY` | 4272 | dict | 1 |
| `ITEM_TIER_DISPLAY` | 4278 | dict | 1 |
| `TERM_ENVOY_SCORE` | 4285 | str | 'Authority' |
| `display_score` | 4295 | function |  |
| `ALIASES` | 4305 | dict | 73 |
| `display` | 4315 | function |  |
| `display_tier` | 4320 | function |  |
| `display_text` | 4330 | function |  |
| `display_list` | 4353 | function |  |
| `display_md` | 4363 | function |  |
| `display_html` | 4370 | function |  |
| `display_obj` | 4382 | function |  |
| `undisplay` | 4395 | function |  |
| `verify_aliases` | 4404 | function |  |
| `BANDIT_FACES` | 4428 | int | 10 |
| `BANDIT_CUNNING_MIN` | 4429 | int | 10 |
| `die_table_ranges` | 4432 | function |  |
| `die_table_rows` | 4440 | function |  |
| `die_table_text` | 4448 | function |  |
| `die_table_lookup` | 4456 | function |  |
| `die_table_verify` | 4463 | function |  |
| `die_table_weights` | 4482 | function |  |
| `BANDIT_CUNNING_TABLE` | 4492 | dict | 4 |
| `bandit_cunning_ranges` | 4499 | function |  |
| `bandit_cunning_rows` | 4500 | function |  |
| `bandit_cunning_lookup` | 4501 | function |  |
| `bandit_cunning_text` | 4503 | function |  |
| `BANDIT_TACTIC_TABLE` | 4510 | dict | 6 |
| `BANDIT_TACTICS` | 4518 | list | 6 |
| `bandit_tactic_ranges` | 4520 | function |  |
| `bandit_tactic_rows` | 4521 | function |  |
| `bandit_tactic_lookup` | 4522 | function |  |
| `verify_bandit_tables` | 4525 | function |  |
| `RENOWN_MAX` | 4621 | int | 30 |
| `RENOWN_PER_TURN` | 4622 | int | 1 |
| `DOMAIN_POINTS_PER_TURN` | 4623 | int | 1 |
| `AI_DOMAIN_POINTS` | 4629 | str | 'Spend Domain Points one Standing at a t |
| `AI_PRIORITIES` | 4631 | list | 8 |
| `AI_FAITH_AVOID` | 4642 | list | 5 |
| `AI_STYLE` | 4665 | dict | 3 |
| `AI_ARCHETYPE` | 4688 | dict | 8 |
| `AI_PO_GOLD` | 4702 | int | 800 |
| `AI_MUSTER` | 4704 | dict | 3 |
| `AI_DIPLOMACY` | 4706 | dict | 4 |
| `FACTION_NAMES` | 4919 | dict | 41 |
| `FACTION_TERM` | 4927 | tuple | 2 |
| `faction_body` | 4933 | function |  |
| `GLOSSARY_CATEGORIES` | 4941 | list | 17 |
| `WIKI_NOLINK` | 4963 | list | 6 |
| `GLOSSARY_SEE` | 4972 | dict | 90 |
| `COND_UPKEEP_FACTOR` | 5012 | float | 0.5 |
| `holding_combat_tags` | 5022 | function |  |
| `holding_upkeep` | 5063 | function |  |
| `holding_domain` | 5076 | function |  |
| `HOLDING_SIM` | 5095 | dict | 129 |
| `AI_PROFILES` | 5107 | dict | 15 |

## 4. Build steps — `CE\build_all_CE.bat`

| Label | Line | Scripts | Echo |
|---|---|---|---|
| `:maps` | 234 | `build_mapapp.py` | --- Map generator app ---; skipped - build_mapapp.py not ported |
| `:cards` | 254 | `generate_cards.py` | --- Cards ---; skipped - generate_cards.py not ported |
| `:docs` | 269 | `md_to_docx.py`, `combat_sheet.py`, `spec_tree_sheet.py`, `playstyle_reference.py`, `pursuit_tiles.py`, `gen_layout.py`, `render_tree.py`, `svg_to_pdf.py`, `domain_board.py`, `infra_board.py`, `settlement_mats.py`, `gen_layout_roots.py`, `gen_settlement_board.py`, `faq_export.py`, `host_sheet.py` | --- Docs ---; Rules - with Holdings, Equipment, Factions, glossary, index...; Combat quick-reference sheet...; Specialization trees...; Playstyle reference...; Pursuit ward-tiles...; Pursuit tech tree |
| `:wiki` | 311 | `build_wiki.py` | --- Wiki ---; skipped - build_wiki.py not ported; skipped - wiki_markers.py not ported, build_wiki imports it; skipped - %RULES_MD% not found; Wiki build FAILED - skipping repo push.; Syncing into %WI |
| `:pushrepo` | 366 | `repo_map.py` | --- Push repo (v%VERSION%, DIE=%DIE%) -^> %REPO_DIR% ---; Git LFS not installed ^(https://git-lfs.com^) - skipping repo push so a; large file can't be committed without LFS. Install once, then re-run. |
| `:end` | 444 | — | Done. Press any key to close. |
| `:board` | 454 | `build_board.py` | --- Board ---; skipped - build_board.py not ported; Board -^> %BOARD_OUT% |
| `:tactical` | 473 | `build_board.py` | --- Tactical board ---; skipped - build_board.py not ported; Tactical board -^> %TAC_OUT% |
| `:lore` | 495 | `gen_cultures.py`, `gen_intro.py`, `gen_draft.py`, `gen_pdf.py`, `gen_book_json.py` | --- Lore (world documents from renown_worldlore.py) ---; skipped - %DIR_LORE%\gen_cultures.py not ported; Lore -^> %LORE_OUT% |

## 5. Rules markers — `CE\RULES_push_simple.md`

- **{{TABLE}}** (29): `edicts`, `eras`, `timers`, `seasons`, `ages`, `net_influence`, `envoy_outcomes`, `influence_gain`, `domain_board`, `treaties`, `settlements`, `infrastructure`, `build_timers`, `terrain`, `public_order`, `po_modifiers`, `trade_rules`, `retinues`, `tactic_matrix`, `siege_calculus`, `bandits_by_era`, `bandit_cunning`, `bandit_tactics`, `holdings`, `weapons`, `ranged`, `shields`, `armor`, `factions`
- **{{GLOSSARY}}** (16): `Reading the Rules`, `Council & Envoys`, `Actions`, `Domains & Scoring`, `Treaties`, `Settlements & Holdings`, `Map & Range`, `Economy & Public Order`, `Army States`, `Battle Structure`, `Combat Keywords — Defense`, `Combat Keywords — Offense`, `Combat Keywords — Handling`, `Combat Keywords — Immune / Negate`, `World`, `Equipment Tiers`
- **{{ACTIONS}}** (5): `Diplomacy`, `Prowess`, `Cunning`, `Piety`, `Industry`
- **{{LIST}}** (1): `ALLIANCE_RULES`
- **{{TERM}}** (1): `Speed X`
- **{{IDX}}** (30): `Era`, `Empire Phase`, `Council Phase`, `Envoy Phase`, `Battle Phase`, `Rest Phase`, `Intrigue Phase`, `Tally Phase`, `Season`, `Age`, `Standing Rank`, `Max Influence`, `Settlement`, `Hamlet`, `Infrastructure`, `Primitive`, `Developed`, `Sophisticated`, `Prodigious`, `Wondrous`, `Wonder`, `Treasury`, `Revenue`, `Trade Agreement`, `Army`, `Garrison`, `Lay Siege`, `Capture`, `Sack`, `Bandit Camp`
- **{{VAL}}** (82): `AGE_YEAR_SEASON`, `ARMY_MAX_RETINUES`, `BANDITS.Bandit Domain Value`, `BANDIT_ARMY_THRESHOLD`, `BANDIT_CAMP_GOLD`, `BANDIT_CAMP_START`, `BANDIT_CUNNING_MIN`, `BANDIT_FACES`, `BLUNDER_THR`, `CAPITAL_EDGE_RANGE`, `CAP_THR`, `DOMAIN_BOARD.innate_influence_own_envoys.Untested`, `DOMAIN_POINTS_PER_TURN`, `EDICT_UNIQUE_RULE`, `ENDURANCE_REGAIN`, `ERAS.Ascension.rank`, `ERAS.Eminence.rank`, `ERAS.Founding.rank`, `ERAS.Founding.renown`, `ERAS.Zenith.rank`, `FACES`, `FAITH_FICKLE_PO`, `FATIGUE_MORALE`, `FOCUSED_THR`, `FRONT_LINE_MAX`, `GAME_TURN_LIMIT`, `HAMLET_RANGE`, `HAMLET_REPEATABLE_TEXT`, `HOLDING_COST_TEXT`, `INITIATIVE_MAX`, `INITIATIVE_MIN`, `MORALE_DICE_MAX`, `OUTLAW_BUFFER_RANGE`, `OUTLAW_COUNTRY_START`, `PANIC_CASUALTY_THRESHOLD`, `PARRY_BASE`, `PO_MAX`, `PO_MIN`, `PRESENCE_RANGE`, `RENOWN_PER_TURN`, `RESERVE_MAX`, `RETINUES.Knight Templar.cost`, `RETINUES.Knight Templar.to_hit`, `RETINUES.Levy.cost`, `RETINUES.Levy.to_hit`, `RETINUES.Man-at-Arms.cost`, `RETINUES.Man-at-Arms.to_hit`, `RETINUES.Sergeant.cost`, `RETINUES.Sergeant.to_hit`, `ROUT_THR`, `SACK_EXTORT_PER_TIER`, `SETTLEMENTS.City.garrison`, `SETTLEMENTS.Hamlet.wards`, `SETTLEMENTS.Metropolis.garrison`, `SETTLEMENTS.Metropolis.reach`, `SETTLEMENTS.Town.garrison`, `SETTLEMENTS.Village.garrison`, `SETTLEMENTS.Village.reach`, `SETUP_HAMLET_TEXT`, `SIEGE_CALCULUS.Lay Siege.floor`, `STANDING_RANK.Established`, `STANDING_RANK.Rising`, `STANDING_RANK.Sovereign`, `STANDING_RANK.Untested`, `STANDING_THRESHOLDS.Established`, `STANDING_THRESHOLDS.Rising`, `STANDING_THRESHOLDS.Sovereign`, `STANDING_THRESHOLDS.Untested`, `STARTING_TREASURY`, `STARTING_TURN_PHASE_OPENER`, `TIMERS.Capture Timer.default`, `TIMERS.Sack Timer.default`, `TRADE_RULES.border_rule`, `TRADE_RULES.income_per_craft`, `VASSAL_EXCHANGE_CAP`, `VASSAL_INFLUENCE_TAKE`, `WARD_RULE`, `WEALTH_EDICT_GOLD`, `WILD_OUTLAW.border_range`, `WILD_OUTLAW.per_players`, `WILD_OUTLAW.plus`, `WILD_OUTLAW.spacing`
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
| 110 | ## Resources |
| 120 | ## The Turn |
| 132 | ### Timers |
| 140 | ### Empire Phase |
| 152 | ### Council Phase |
| 158 | ### Envoy Phase |
| 173 | ### Battle Phase |
| 177 | ### Rest Phase |
| 184 | # Seasons |
| 190 | # Setup |
| 192 | ## Table Setup |
| 197 | ## Setup Order |
| 206 | ### Ages |
| 212 | ## Player Setup |
| 220 | # Actions & Voting |
| 222 | ## Action Mechanics |
| 224 | ### Sending an Envoy |
| 228 | ### Resolving an Envoy |
| 244 | ### Envoy Resolution Table |
| 260 | ## Influence |
| 268 | ## Diplomacy Actions |
| 272 | ### Rule: Diplomatic Mission |
| 276 | ## Prowess Actions |
| 280 | ### Rule: Commanding Presence |
| 284 | ## Cunning Actions |
| 288 | ## Piety Actions |
| 292 | ### Rule: Wavering Devotion |
| 296 | ## Industry Actions |
| 300 | ### Rule: Ulterior Motive |
| 308 | # Domains & Standings |
| 310 | ### Domain Standings |
| 316 | ### Standing Rank |
| 320 | ### Domain Identities & Traits |
| 326 | # Diplomacy & Treaties |
| 328 | ### Treaties & Alliances |
| 336 | ### Vassalization |
| 358 | # Empire Building |
| 360 | ## Settlements |
| 366 | ### Settlement Wards |
| 370 | ### Chartering Settlements |
| 374 | ### Settlement Reach |
| 378 | ### Hamlets |
| 384 | ## Infrastructure |
| 404 | ## Territory & Terrain |
| 418 | # Economy |
| 420 | ## Public Order |
| 432 | ### Innate Public Order Modifiers |
| 436 | ## Treasury & Upkeep |
| 446 | ### Insolvency & Bankruptcy |
| 459 | ## Trade & Income |
| 461 | ### Who Can Trade |
| 476 | ### Income Types |
| 484 | # Armies |
| 486 | ### Armies Overview |
| 492 | ### Garrisons |
| 496 | ### Mustering |
| 506 | ### Blocked Armies |
| 512 | # Battles & Sieges |
| 514 | ## Battle Phase |
| 518 | ### Beginning a Battle |
| 524 | ### The Skirmish Steps |
| 542 | ### Ending a Battle |
| 547 | ### Tactic Matrix |
| 561 | ## Siege Warfare |
| 566 | ### Siege Timer |
| 572 | ### Beginning a Siege |
| 582 | ### Resolving a Siege |
| 594 | # Bandits |
| 596 | ### Outlaw Country |
| 605 | ### Spawning Bandit Camps |
| 611 | ### Growing Bandit Camps |
| 617 | ### Bandit Rules |
| 633 | ### Bandit Army Behavior |
| 645 | ### Attacking a Bandit Camp |
| 655 | # Holdings |
| 661 | # Equipment |
| 663 | ## Melee Weapons |
| 667 | ## Ranged Weapons |
| 671 | ## Shields |
| 675 | ## Armor |
| 681 | # Factions |
| 685 | # Index |

## 6. Settlement board — `CE\references\gen_settlement_board.py` + `CE\references\board\js/*.js` (+ `board.css`, `body.html`)

Payload keys passed to the HTML as `DATA` (66): `records`, `naturalNames`, `externalTokens`, `simple`, `chainTerm`, `pursuitTerm`, `infra`, `wonders`, `armySrc`, `equip`, `glossary`, `domainBoard`, `publicOrder`, `domainBoardFx`, `poByEra`, `wikiBase`, `wikiHome`, `tree`, `rulebook`, `limits`, `eras`, `edicts`, `envoyOutcomes`, `outcomeThresh`, `startPhase`, `actions`, `phaseRules`, `phaseSteps`, `rulesConst`, `ages`, `domains`, `standings`, `tradePerCraft`, `noTradeSeason`, `tradeBorder`, `renownPerTurn`, `dpPerTurn`, `settlements`, `battle`, `terrainRef`, `banditLoadouts`, `bandits`, `treaties`, `allianceRules`, `startTiers`, `startTreasury`, `pursuitUpkeep`, `buildTimers`, `infraTiers`, `timers`, `seasons`, `poModifiers`, `vassalInfluenceTake`, `aliases`, `scoreTerm`, `costs`, `influenceGain`, `siege`, `factions`, `cultures`, `cultureSelf`, `placeNames`, `warnings`, `version`, `sprites`, `efx`

Python: `load`:27, `strip_md`:34, `has_cond`:76, `to_int`:79, `classify`:82, `_iv`:149, `envoy_fx`:150, `combine_parts`:261, `combine_effects`:302, `rules_payload`:306, `tree_payload`:365, `parse_effects`:399, `parse_mreq`:405, `classify_req_token`:413, `build`:422, `font_faces`:516, `_pursuit_term_template`:541, `render_html`:549, `_style_js`:557, `place_names_payload`:568, `sprite_payload`:588, `find_mapgen`:610, `_board_template`:625, `check_rules`:639, `_val`:767, `rules_section`:776, `phase_steps`:795, `battle_data`:812, `bandit_loadouts`:833, `effects_report`:885, `main`:916

JS sections: TABLE: seating, Council & Envoy phases :10_table.js:1, Action automation: Perform picker + resolution :10_table.js:269, REALM: the play surface :15_realm.js:1, INTRIGUE & TALLY PHASES (RULES: Envoy Phase steps 3 and 5) :16_tally.js:1,  :40_realm_data.js:271, Inspect tool :60_map.js:280, EFFECT PLUMBING: the effect registry (references/effect_registry.py) :70_rules.js:1, ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS :70_rules.js:64, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :70_rules.js:150, CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper :85_ux.js:1, UNDO / REDO :90_app.js:1, ACTIVITY LOG :90_app.js:39, GAME: save · load · new :90_app.js:98, HOVER KEYWORDS :90_app.js:149

JS functions (997, name:file:line):

```
fixBastard:00_core.js:8 dispScore:00_core.js:15 presR:00_core.js:33 POB:00_core.js:36 poNum:00_core.js:37 efxOf:00_core.js:48 hitOf:00_core.js:49 facHit:00_core.js:50 tnow:10_table.js:12 noteServerDate:10_table.js:13 lockOn:10_table.js:21 claimOf:10_table.js:22 mine:10_table.js:23 myClaimP:10_table.js:24 canEdit:10_table.js:25 boardEndOn:10_table.js:27 TB:10_table.js:28 seatFloor:10_table.js:30 tSeats:10_table.js:31 tTimer:10_table.js:32 tTurn:10_table.js:33 tBegun:10_table.js:34 tPhase:10_table.js:35 PT:10_table.js:37 tCur:10_table.js:38 tCurW:10_table.js:39 sameP:10_table.js:40 meP:10_table.js:41 canAct:10_table.js:42 seatMap:10_table.js:45 seated:10_table.js:49 isSpring:10_table.js:50 hostP:10_table.js:51 voteOrd:10_table.js:54 tOrder:10_table.js:55 canHost:10_table.js:56 seatsLocked:10_table.js:57 tStand:10_table.js:60 eraRec:10_table.js:61 diploInf:10_table.js:62 diploCap:10_table.js:63 eraActions:10_table.js:64 envSlots:10_table.js:67 slotOpen:10_table.js:69 withSlots:10_table.js:70 boardFx:10_table.js:73 fxOf:10_table.js:86 scopeOk:10_table.js:87 sgn:10_table.js:88 fxLabel:10_table.js:89 atWarPair:10_table.js:105 opposeBlock:10_table.js:106 domAsFx:10_table.js:113 innateParts:10_table.js:114 modSum:10_table.js:120 innateInf:10_table.js:122 voteCap:10_table.js:123 inflPool:10_table.js:126 personalEnvoys:10_table.js:127 councilEnvoys:10_table.js:128 tOutcome:10_table.js:129 outText:10_table.js:131 tPlan:10_table.js:134 missionWhy:10_table.js:152 domStarted:10_table.js:155 whisperEligibleEnvoys:10_table.js:156 tSim:10_table.js:159 performEval:10_table.js:240 comboEval:10_table.js:246 failPassFx:10_table.js:255 actionsOf:10_table.js:256 actReqFlag:10_table.js:258 actInfoHTML:10_table.js:262 actCost:10_table.js:273 domCost:10_table.js:275 addFaith:10_table.js:276 alliedP:10_table.js:277 allyGroup:10_table.js:278 topPair:10_table.js:279 actDoubt:10_table.js:282 musterOpts:10_table.js:338 runMuster:10_table.js:343 buildOpts:10_table.js:356 buildPlaces:10_table.js:364 runBuild:10_table.js:368 improveOpts:10_table.js:374 expandOpts:10_table.js:379 runExpand:10_table.js:383 runImprove:10_table.js:387 runSettle:10_table.js:392 repairOpts:10_table.js:397 runRepair:10_table.js:400 settName:10_table.js:404 warOnFac:10_table.js:407 warOn:10_table.js:411 grandVizier:10_table.js:415 pfSpec:10_table.js:418 pfHardFlags:10_table.js:419 pfTargets:10_table.js:429 pfSubs:10_table.js:440 pfSubLabel:10_table.js:441 evTxt:10_table.js:443 insteadFx:10_table.js:448 actDom:10_table.js:449 pfActs:10_table.js:450 pfInsteadSrc:10_table.js:451 pfForm:10_table.js:452 boardCounts:10_table.js:487 pendingOf:10_table.js:489 apLines:10_table.js:491 resolveEnvoy:10_table.js:494 autoRes:10_table.js:553 tApply:10_table.js:554 tNext:10_table.js:567 tSetPhase:10_table.js:568 tRestartPhase:10_table.js:571 tAdd30:10_table.js:576 grantDP:10_table.js:579 dpOwed:10_table.js:580 tEndTurn:10_table.js:581 setSeats:10_table.js:601 tAutoSeat:10_table.js:606 tSig:10_table.js:612 tName:10_table.js:615 tVoteTxt:10_table.js:616 envBadges:10_table.js:617 innateTxt:10_table.js:623 tOutCls:10_table.js:625 tPerformHtml:10_table.js:626 summaryLines:10_table.js:648 chronOn:10_table.js:665 chron:10_table.js:666 chronSnap:10_table.js:669 chronTick:10_table.js:676 chronDate:10_table.js:686 empireChecklistHTML:10_table.js:687 treeSave:10_table.js:697 mapRaws:10_table.js:707 refRawAvail:10_table.js:710 treeHTML:10_table.js:714 rulebookHTML:10_table.js:781 linkifyRules:10_table.js:784 renderReference:10_table.js:788 tCountdown:10_table.js:801 applyTheme:10_table.js:816 applySkin:10_table.js:828 doFire:15_realm.js:8 patch:15_realm.js:12 rlCommit:15_realm.js:13 pOf:15_realm.js:14 standingPhaseActions:15_realm.js:15 activeCipherTimers:15_realm.js:19 cipherTimerResolve:15_realm.js:25 empWin:15_realm.js:31 empireHoldingHTML:15_realm.js:32 whisperGateHTML:15_realm.js:54 forgeRetryHTML:15_realm.js:58 courierDeferHTML:15_realm.js:62 rlOpen:15_realm.js:115 rlToggle:15_realm.js:116 renderTable:15_realm.js:121 renderRealmMap:15_realm.js:141 domCells:15_realm.js:153 realmTableHTML:15_realm.js:157 spectating:15_realm.js:199 miniCardHTML:15_realm.js:211 phaseCardHTML:15_realm.js:221 dockCard:15_realm.js:272 dockHTML:15_realm.js:273 envoyQueueHTML:15_realm.js:346 inflCardHTML:15_realm.js:365 drawersHTML:15_realm.js:420 turnLogItems:15_realm.js:432 turnLogHTML:15_realm.js:452 realmTimersBrief:15_realm.js:461 tallyVoter:16_tally.js:7 standingHit:16_tally.js:9 tallySupportOf:16_tally.js:10 tallyEndorseOf:16_tally.js:11 resolveOpen:16_tally.js:13 intrigueKinds:16_tally.js:15 intrigueSilenced:16_tally.js:24 whisperPending:16_tally.js:25 intrigueRun:16_tally.js:27 tallyRun:16_tally.js:38 envLabel:16_tally.js:61 tsId:16_tally.js:62 tRow:16_tally.js:63 envSel:16_tally.js:64 amtSel:16_tally.js:65 intrigueHTML:16_tally.js:66 tallyHTML:16_tally.js:94 inTurn:16_tally.js:109 selVal:16_tally.js:110 tallyTurn:16_tally.js:125 startDoms:20_state.js:2 ageRec:20_state.js:5 ageRisingOf:20_state.js:6 startDomsFor:20_state.js:7 startDomTotal:20_state.js:8 curYear:20_state.js:9 rollAgeYear:20_state.js:11 applyAgeStart:20_state.js:14 startSettlements:20_state.js:16 startSig:20_state.js:19 reseedIfPristine:20_state.js:21 newBoard:20_state.js:26 newPlayer:20_state.js:28 normalizeD:20_state.js:44 activeBoard:20_state.js:67 reindex:20_state.js:68 pActive:20_state.js:81 ignHas:20_state.js:85 flagState:20_state.js:86 ignBtn:20_state.js:91 ignNote:20_state.js:94 unlockStatus:20_state.js:100 nameHit:20_state.js:111 missTxt:20_state.js:112 recomputePC:20_state.js:114 buildTimerMod:20_state.js:119 withBuildMod:20_state.js:123 pursuitBaseTime:20_state.js:124 infraBaseTime:20_state.js:125 pursuitBuildTime:20_state.js:126 infraBuildTime:20_state.js:127 buildNote:20_state.js:128 settBaseTime:20_state.js:129 settBuildTime:20_state.js:130 itm:20_state.js:131 infraOn:20_state.js:132 checkinAct:20_state.js:134 gameStarted:20_state.js:135 glogTurn:20_state.js:139 glogSea:20_state.js:140 glogPush:20_state.js:141 glogSync:20_state.js:145 tGold:20_state.js:146 boardOwnerName:20_state.js:151 empTimers:20_state.js:155 empEconomy:20_state.js:156 empPO:20_state.js:162 immuneStrainIn:20_state.js:170 siegeStrains:20_state.js:174 endMax:20_state.js:176 capEnd:20_state.js:177 effStrained:20_state.js:178 empArmies:20_state.js:179 endRow:20_state.js:186 boardEndTurn:20_state.js:189 stepRealmTimer:20_state.js:193 tickRealm:20_state.js:194 expireBlocks:20_state.js:197 empirePhase:20_state.js:199 tickTimers:20_state.js:222 facTypeBonus:20_state.js:231 pursuitUpkeep:20_state.js:234 withBoard:20_state.js:237 setOnline:20_state.js:253 clone:20_state.js:263 jeq:20_state.js:264 isObj:20_state.js:265 merge3:20_state.js:267 splitD:20_state.js:276 joinD:20_state.js:282 save:20_state.js:308 saveIfDirty:20_state.js:316 editing:20_state.js:351 cvar:20_state.js:371 fmt:20_state.js:372 cap:20_state.js:373 settUnbuilt:20_state.js:377 unbuiltMeta:20_state.js:378 settMeta:20_state.js:379 pinSettCell:20_state.js:380 settExpand:20_state.js:381 settFinish:20_state.js:382 settTier:20_state.js:385 occupants:20_state.js:386 hamletOK:20_state.js:387 hamletRoot:20_state.js:390 hamletFits:20_state.js:391 effList:20_state.js:400 effLabel:20_state.js:405 exemptionsOf:20_state.js:406 wardExemptions:20_state.js:415 isFreeRider:20_state.js:416 wardUse:20_state.js:417 canPlace:20_state.js:428 hamletRepeat:20_state.js:446 setupRawOK:20_state.js:449 setupHoldFlags:20_state.js:450 capitalSett:20_state.js:463 setCapital:20_state.js:464 isCityPlus:20_state.js:466 dbActive:20_state.js:467 standingKey:20_state.js:473 armStanding:20_state.js:474 capBonus:20_state.js:479 eraCapBase:20_state.js:480 eraCap:20_state.js:481 capSrc:20_state.js:482 cityCount:20_state.js:483 eraAllows:20_state.js:485 rslug:20_state.js:493 boardFlags:20_state.js:494 onBoard:20_state.js:529 scopeOf:20_state.js:531 realmHolder:20_state.js:532 scopeBlock:20_state.js:533 nextTier:20_state.js:538 autoFill:20_state.js:540 buildFilters:30_empire.js:8 monChip:30_empire.js:10 catSave:30_empire.js:16 catGroups:30_empire.js:33 catRows:30_empire.js:35 pAvail:30_empire.js:39 legalCtx:30_empire.js:43 rawRes:30_empire.js:45 rawInSett:30_empire.js:46 rawOK:30_empire.js:50 pLegal:30_empire.js:51 pReqMiss:30_empire.js:56 autoHamlet:30_empire.js:59 autoOK:30_empire.js:60 effSpot:30_empire.js:62 facRide:30_empire.js:69 smartSid:30_empire.js:70 iAvail:30_empire.js:77 catUpkeep:30_empire.js:78 seg:30_empire.js:79 renderList:30_empire.js:81 wardPick:30_empire.js:135 wpRender:30_empire.js:137 wpPlace:30_empire.js:160 settLbl:30_empire.js:165 reqRow:30_empire.js:167 pursuitRow:30_empire.js:169 sub:30_empire.js:180 tip:30_empire.js:182 itemRow:30_empire.js:183 flash:30_empire.js:193 addInfraByName:30_empire.js:195 placeHolding:30_empire.js:201 addItem:30_empire.js:222 removeInstance:30_empire.js:233 addPursuitByName:30_empire.js:234 moveInstance:30_empire.js:235 infraReqToks:30_empire.js:251 infraTokStatus:30_empire.js:257 infraReqStatus:30_empire.js:271 infraValid:30_empire.js:276 infraActive:30_empire.js:283 infraReqLinesHTML:30_empire.js:284 masteryInfraToks:30_empire.js:288 masteryInfraHTML:30_empire.js:289 annotReqTok:30_empire.js:296 optionMet:30_empire.js:301 reqStatus:30_empire.js:309 instStatus:30_empire.js:316 chainLine:30_empire.js:323 simpleReq:30_empire.js:332 simpleReqHTML:30_empire.js:344 computeEarned:30_empire.js:352 atomEl:30_empire.js:370 atomsBlock:30_empire.js:379 render:30_empire.js:392 renderTopBar:30_empire.js:452 toggleEmpty:30_empire.js:499 sfxNorm:30_empire.js:508 sfxLabel:30_empire.js:509 settFx:30_empire.js:518 settFxPanel:30_empire.js:541 renderPursuitBoard:30_empire.js:548 wardPiles:30_empire.js:657 wardGrid:30_empire.js:669 unitFor:30_empire.js:696 tryMove:30_empire.js:701 scrollHost:30_empire.js:735 dropTargetAt:30_empire.js:736 clearDropHL:30_empire.js:744 armDrag:30_empire.js:745 beginDrag:30_empire.js:762 dragMove:30_empire.js:776 dragEnd:30_empire.js:788 herPicker:30_empire.js:797 factionFree:30_empire.js:808 setFaction:30_empire.js:812 facGearFlags:30_empire.js:821 dualFlags:30_empire.js:827 factionFlags:30_empire.js:831 cultureFactions:30_empire.js:848 facOffered:30_empire.js:855 facPicker:30_empire.js:857 culSelectHTML:30_empire.js:874 cultureOf:30_empire.js:878 holdDom:30_empire.js:879 cultureSet:30_empire.js:883 cultureKeep:30_empire.js:888 cultureKeepWonder:30_empire.js:889 derivedCulture:30_empire.js:891 nameCulture:30_empire.js:893 usedSettNames:30_empire.js:895 genPlaceName:30_empire.js:896 nameSett:30_empire.js:902 nameAllSetts:30_empire.js:904 renderFaction:30_empire.js:905 timerCtl:30_empire.js:913 placementSelect:30_empire.js:918 contribAcc:30_empire.js:933 contribChips:30_empire.js:936 accChips:30_empire.js:937 pursuitDetail:30_empire.js:945 quickChip:30_empire.js:969 buildsIntoRow:30_empire.js:973 nextLinksHTML:30_empire.js:975 pursuitTable:30_empire.js:983 pursuitCard:30_empire.js:1010 renderInfraSection:30_empire.js:1098 armyUnlocks:30_empire.js:1143 unlockedShieldTiers:30_empire.js:1175 tierOK:30_empire.js:1179 gloss:30_empire.js:1180 glossLookup:30_empire.js:1189 openModal:30_empire.js:1198 closeModal:30_empire.js:1202 kwChipHTML:30_empire.js:1203 esc:30_empire.js:1204 inspectKeyword:30_empire.js:1205 inspectItem:30_empire.js:1227 optionList:30_empire.js:1250 loadoutFields:30_empire.js:1266 canDualWield:30_empire.js:1284 renderArmy:30_empire.js:1286 armyCard:30_empire.js:1319 reqMet:30_empire.js:1413 weaponUnlockMet:30_empire.js:1416 moraleBase:30_empire.js:1418 armyUpkeep:30_empire.js:1419 moraleCap:30_empire.js:1421 moraleStanding:30_empire.js:1424 moralePO:30_empire.js:1427 effMorale:30_empire.js:1429 isRouted:30_empire.js:1430 armyVals:30_empire.js:1433 armyStats:30_empire.js:1441 noUpkeepTiers:30_empire.js:1468 holdsActive:30_empire.js:1470 playersWithout:30_empire.js:1472 calcMetrics:30_empire.js:1474 computeTotals:30_empire.js:1532 poTaxMod:30_empire.js:1563 taxDouble:30_empire.js:1568 winterTax:30_empire.js:1569 occupyTaxOnly:30_empire.js:1578 settInside:30_empire.js:1579 settTax:30_empire.js:1580 tradeIncome:30_empire.js:1583 tradeRaw:30_empire.js:1592 goldBreak:30_empire.js:1606 treasLive:30_empire.js:1620 fmtK:30_empire.js:1622 renderGlog:30_empire.js:1624 goldBreakHTML:30_empire.js:1631 goldBreakTxt:30_empire.js:1635 seasonNet:30_empire.js:1636 husbandryGoldFor:30_empire.js:1640 SEASON_DBL_TIER:30_empire.js:1644 tierGoldFor:30_empire.js:1646 seasonDblGold:30_empire.js:1650 SEASON_DBL_TYPE:30_empire.js:1651 boardMetrics:30_empire.js:1652 poCurKey:30_empire.js:1660 poBandName:30_empire.js:1661 poActiveKeys:30_empire.js:1663 poActiveEffects:30_empire.js:1665 poImmune:30_empire.js:1672 poDoubled:30_empire.js:1673 renderPO:30_empire.js:1675 curSeason:40_realm_data.js:4 stepSeason:40_realm_data.js:5 playerOfBoard:40_realm_data.js:8 igVal:40_realm_data.js:9 eraIdx:40_realm_data.js:10 playerAtWar:40_realm_data.js:11 influenceRowsBase:40_realm_data.js:12 influenceRows:40_realm_data.js:43 influenceTotal:40_realm_data.js:48 poModRows:40_realm_data.js:51 totTipSimple:40_realm_data.js:78 totTip:40_realm_data.js:81 epSources:40_realm_data.js:92 topSuz:40_realm_data.js:105 royalMarriage:40_realm_data.js:108 sameAlliance:40_realm_data.js:113 poFloor:40_realm_data.js:116 applyPOFloor:40_realm_data.js:117 epRows:40_realm_data.js:118 poModTotal:40_realm_data.js:131 dpButtons:40_realm_data.js:132 renderDP:40_realm_data.js:135 dpSpend:40_realm_data.js:138 renderMiniStand:40_realm_data.js:145 renderInfluence:40_realm_data.js:159 renderPOMods:40_realm_data.js:163 siegeState:40_realm_data.js:175 siegeCalc:40_realm_data.js:176 siegeHTML:40_realm_data.js:194 realmTimers:40_realm_data.js:209 timerAddHTML:40_realm_data.js:210 boardTimerRows:40_realm_data.js:214 siegeResolveHTML:40_realm_data.js:220 activeTimersHTML:40_realm_data.js:227 seasonsHTML:40_realm_data.js:233 costsHTML:40_realm_data.js:236 wireDashExtras:40_realm_data.js:239 renderDash:40_realm_data.js:267 domBand:40_realm_data.js:270 mods:40_realm_data.js:273 diplo:40_realm_data.js:278 pk:40_realm_data.js:279 isVassal:40_realm_data.js:281 vassalsOf:40_realm_data.js:282 effPair:40_realm_data.js:283 pairOf:40_realm_data.js:286 pname:40_realm_data.js:287 allianceLabel:40_realm_data.js:288 pboard:40_realm_data.js:289 tradeBorderOK:40_realm_data.js:291 hasRoad:40_realm_data.js:292 eraRank:40_realm_data.js:295 allianceEra:40_realm_data.js:296 allianceOK:40_realm_data.js:297 pairFlags:40_realm_data.js:298 dStatus:40_realm_data.js:307 diploHTML:40_realm_data.js:311 wireDiplo:40_realm_data.js:368 newSide:50_battle.js:4 battle:50_battle.js:5 bq:50_battle.js:7 bqAdd:50_battle.js:8 bqSideName:50_battle.js:9 bqLoad:50_battle.js:12 sideHex:50_battle.js:15 bqStart:50_battle.js:19 banditArmy:50_battle.js:22 armBandits:50_battle.js:26 sideArmy:50_battle.js:34 blog:50_battle.js:39 d10:50_battle.js:40 seizeForced:50_battle.js:41 facCombat:50_battle.js:44 sideUnlocks:50_battle.js:56 sideDomains:50_battle.js:60 standingFxOf:50_battle.js:61 hasTiltyard:50_battle.js:65 eqOptions:50_battle.js:66 eqCode:50_battle.js:75 eqNow:50_battle.js:78 dualOn:50_battle.js:82 eqWeapon:50_battle.js:83 tacAllowed:50_battle.js:92 tacOK:50_battle.js:97 randomTacticPool:50_battle.js:98 sideCalc:50_battle.js:101 pickKey:50_battle.js:216 viewerSide:50_battle.js:217 mdLite:50_battle.js:239 fmtModLong:50_battle.js:241 fmtMod:50_battle.js:244 dieRow:50_battle.js:246 rollHTML:50_battle.js:247 battleSprites:50_battle.js:256 sideHTML:50_battle.js:260 tacEdge:50_battle.js:353 tacticExplainHTML:50_battle.js:359 battleRulesHTML:50_battle.js:373 renderBattle:50_battle.js:377 incoming:50_battle.js:407 roll:50_battle.js:410 ripN:50_battle.js:470 addRip:50_battle.js:471 setPendCas:50_battle.js:473 pendCas:50_battle.js:474 applyCas:50_battle.js:475 endSkirmish:50_battle.js:476 endBattle:50_battle.js:496 wireBattle:50_battle.js:530 edictTimerLen:50_battle.js:578 edictChoices:50_battle.js:580 edictTotal:50_battle.js:586 edictOwners:50_battle.js:587 bumpRenown:50_battle.js:588 edictCond:50_battle.js:593 edictHeld:50_battle.js:597 edictPend:50_battle.js:602 edictIsPending:50_battle.js:603 edictTick:50_battle.js:605 edictTaken:50_battle.js:610 edictWatch:50_battle.js:611 checkEdicts:50_battle.js:615 edictNewsText:50_battle.js:623 edictBoardHTML:50_battle.js:624 wireEdicts:50_battle.js:653 currentEra:50_battle.js:667 pMark:50_battle.js:675 domTrackHTML:50_battle.js:677 standingEffectsHTML:50_battle.js:686 renderRenown:50_battle.js:699 aiOn:55_ai.js:6 aiProfile:55_ai.js:7 aiDriver:55_ai.js:9 aiNote:55_ai.js:10 aiCashOutlook:55_ai.js:15 aiMem:55_ai.js:20 aiRel:55_ai.js:21 aiRelAdd:55_ai.js:22 aiLearn:55_ai.js:24 aiStandSteps:55_ai.js:35 aiNextMonument:55_ai.js:41 aiStandGoals:55_ai.js:44 aiPickDomain:55_ai.js:57 aiSpendDP:55_ai.js:63 aiCouncilPick:55_ai.js:66 aiEraAllows:55_ai.js:78 aiFoe:55_ai.js:80 aiFriend:55_ai.js:82 aiHoldNet:55_ai.js:84 aiHoldPO:55_ai.js:87 aiHoldValue:55_ai.js:88 aiFaithFloor:55_ai.js:90 aiBuildPick:55_ai.js:91 aiImprovePick:55_ai.js:96 aiTreatyType:55_ai.js:101 aiTreatyAccept:55_ai.js:110 aiApplyTreaty:55_ai.js:121 aiOffensive:55_ai.js:131 aiKit:55_ai.js:132 aiGearRank:55_ai.js:143 aiOutfit:55_ai.js:149 aiMoveTargets:55_ai.js:161 aiMovable:55_ai.js:163 aiEngageSize:55_ai.js:168 aiMove:55_ai.js:170 aiPrioW:55_ai.js:199 aiScore:55_ai.js:200 aiSurvival:55_ai.js:203 aiPassChance:55_ai.js:210 aiArch:55_ai.js:218 aiStyle:55_ai.js:222 aiGearGain:55_ai.js:224 aiHoldTags:55_ai.js:231 aiActTags:55_ai.js:245 aiFaithNeed:55_ai.js:262 aiBanditThreat:55_ai.js:271 aiBanditNear:55_ai.js:278 aiSit:55_ai.js:281 aiCandidates:55_ai.js:291 aiIntents:55_ai.js:386 aiDeclare:55_ai.js:394 aiPlanFor:55_ai.js:400 aiPerform:55_ai.js:402 aiVoteWant:55_ai.js:421 aiVoteAll:55_ai.js:434 aiTacticEval:55_ai.js:447 aiTacticU:55_ai.js:453 aiTacticStance:55_ai.js:459 aiPickTactic:55_ai.js:465 aiBattleTick:55_ai.js:475 aiTick:55_ai.js:481 aiAfterRender:55_ai.js:496 mapClimate:60_map.js:17 mapPal:60_map.js:22 tLum:60_map.js:25 tTone:60_map.js:27 tLighten:60_map.js:28 tGlyph:60_map.js:31 tSwatch:60_map.js:36 mapState:60_map.js:43 hexDist:60_map.js:44 decodeGrid:60_map.js:47 seedCode:60_map.js:57 generateMap:60_map.js:58 parseSeedCode:60_map.js:66 mapZoom:60_map.js:78 reachBonus:60_map.js:84 reachOwners:60_map.js:93 resShown:60_map.js:107 nodesMode:60_map.js:108 reachResources:60_map.js:110 settReachHexes:60_map.js:120 rawClaims:60_map.js:131 mapSprId:60_map.js:153 mapSprDefs:60_map.js:154 tMix:60_map.js:164 hStr:60_map.js:169 rng32:60_map.js:170 mapScatter:60_map.js:171 propPaths:60_map.js:190 pxSwatch:60_map.js:194 mapSpr:60_map.js:199 eqSVG:60_map.js:205 sprSVG:60_map.js:207 stIcon:60_map.js:216 armyGear:60_map.js:217 armyUFor:60_map.js:219 stDedup:60_map.js:224 stIconSVG:60_map.js:226 plateStatus:60_map.js:228 plateBox:60_map.js:229 mapPlate:60_map.js:231 settPlate:60_map.js:242 settBehind:60_map.js:253 settInsideMarks:60_map.js:257 mapBarHTML:60_map.js:272 terrOwners:60_map.js:283 terrFlags:60_map.js:285 unrestCamps:60_map.js:291 intrudersOf:60_map.js:293 settReach:60_map.js:297 settEcon:60_map.js:299 pillageCheck:60_map.js:308 pillageTargets:60_map.js:312 runPillage:60_map.js:315 armyStatus:60_map.js:328 mapMarkers:60_map.js:341 inspHTML:60_map.js:352 inspHead:60_map.js:355 inspCell:60_map.js:358 g:60_map.js:359 inspCan:60_map.js:360 inspArmy:60_map.js:361 settStatus:60_map.js:381 settStatusMarks:60_map.js:391 inspSett:60_map.js:395 envoyFor:60_map.js:431 settActionsHTML:60_map.js:434 armyMusterBtn:60_map.js:445 inspCamp:60_map.js:456 engageTargets:60_map.js:468 wireInsp:60_map.js:474 mapLayers:60_map.js:501 mapSVG:60_map.js:598 outlawReport:60_map.js:600 banditDomain:60_map.js:611 campKey:60_map.js:613 banditAutoHTML:60_map.js:615 armyName:60_map.js:624 syncMapTiers:60_map.js:626 mapLinkBad:60_map.js:633 mapLinksHTML:60_map.js:634 wireBanditAuto:60_map.js:645 banditAuto:60_map.js:651 BST:60_map.js:652 bLog:60_map.js:653 hk:60_map.js:655 mapSetts:60_map.js:656 cellPlayer:60_map.js:657 cellSett:60_map.js:659 mapArmies:60_map.js:662 cellArmy:60_map.js:663 cellTitle:60_map.js:666 byDist:60_map.js:670 isWild:60_map.js:674 wildZones:60_map.js:675 outlawZones:60_map.js:677 zoneOf:60_map.js:682 zoneOwners:60_map.js:683 outlawOwners:60_map.js:688 outlawOwner:60_map.js:690 outlawOf:60_map.js:692 campWild:60_map.js:694 wildCount:60_map.js:696 wildDone:60_map.js:697 placeWildOutlaw:60_map.js:703 rescatterWild:60_map.js:725 pieceAura:60_map.js:729 wardMap:60_map.js:735 wardsOf:60_map.js:736 wardRoom:60_map.js:737 wardFill:60_map.js:739 wardCand:60_map.js:741 presHexes:60_map.js:745 wardAuto:60_map.js:749 wardPrune:60_map.js:759 wardMarks:60_map.js:761 campInRange:60_map.js:773 settleWhere:60_map.js:778 hexFree:60_map.js:782 spawnCamp:60_map.js:783 growCamps:60_map.js:785 expandOutlaw:60_map.js:790 immuneUprising:60_map.js:793 banditTargetMods:60_map.js:794 cunningAction:60_map.js:796 endorsedExtort:60_map.js:797 banditAct:60_map.js:798 runBanditMechanics:60_map.js:828 banditSpeed:60_map.js:848 banditAuraList:60_map.js:850 banditRun:60_map.js:857 moveCamp:60_map.js:865 moveBandit:60_map.js:868 banditReturn:60_map.js:876 banditSiegeTimer:60_map.js:881 banditMoves:60_map.js:883 banditSkims:60_map.js:916 creditSkims:60_map.js:924 envoyOutcome:60_map.js:931 banditCunningHTML:60_map.js:936 dieLookup:60_map.js:953 terrainTablesHTML:60_map.js:956 mapToolsHTML:60_map.js:979 banditPanelHTML:60_map.js:1013 mapAsP:60_map.js:1029 mapEditBlock:60_map.js:1030 mapGuard:60_map.js:1039 guarded:60_map.js:1041 mapCellClick:60_map.js:1043 wireMap:60_map.js:1069 srcKeys:70_rules.js:6 srcMatch:70_rules.js:13 srcHas:70_rules.js:14 srcRows:70_rules.js:16 bordersOf:70_rules.js:20 poCap:70_rules.js:24 poTextFloor:70_rules.js:25 siegeTextMods:70_rules.js:28 siegeWinterOK:70_rules.js:35 siegeDoubleOK:70_rules.js:36 actRestrict:70_rules.js:38 actRiders:70_rules.js:53 settById:70_rules.js:65 besiegeExempt:70_rules.js:67 settBesieged:70_rules.js:68 armySieging:70_rules.js:70 armyBesieged:70_rules.js:72 armyStateTags:70_rules.js:73 armyBlocked:70_rules.js:82 garrisonSizes:70_rules.js:85 hasGarrisons:70_rules.js:86 garrisonGear:70_rules.js:88 garrisonOf:70_rules.js:89 garrisonsOf:70_rules.js:93 garrisonCard:70_rules.js:94 standingOnceRows:70_rules.js:115 onceEffects:70_rules.js:117 onceState:70_rules.js:118 onceWindowNow:70_rules.js:122 onceHTML:70_rules.js:123 onceUse:70_rules.js:134 noteAdd:70_rules.js:143 recoupNote:70_rules.js:145 blackMarketReact:70_rules.js:152 extortGold:70_rules.js:160 danegeldRows:70_rules.js:171 loans:70_rules.js:177 loanTerms:70_rules.js:178 loanInterest:70_rules.js:181 runLoans:70_rules.js:182 loansHTML:70_rules.js:188 autoExtortRows:70_rules.js:206 extortSlots:70_rules.js:215 exTargets:70_rules.js:218 extortTargetsHTML:70_rules.js:219 runAutoExtort:70_rules.js:222 firstDoubtRed:70_rules.js:248 fdState:70_rules.js:252 gainDoubt:70_rules.js:255 siegeOn:70_rules.js:260 endSettlementSieges:70_rules.js:261 besiegedCount:70_rules.js:262 pById:70_rules.js:263 nextId:70_rules.js:264 captureTransfer:70_rules.js:265 sackWards:70_rules.js:277 sackApply:70_rules.js:282 banditSack:70_rules.js:298 resolveRealm:70_rules.js:310 sackLocks:70_rules.js:317 armyHex:70_rules.js:321 settHex:70_rules.js:322 musterLimit:70_rules.js:323 musterTick:70_rules.js:330 hasMusterField:70_rules.js:338 charterFlags:70_rules.js:341 selArmy:70_rules.js:364 canMoveArmy:70_rules.js:365 armyBesiegeExempt:70_rules.js:367 canEnterSett:70_rules.js:369 armyInside:70_rules.js:371 enterCheck:70_rules.js:374 freeHexNear:70_rules.js:376 kickOut:70_rules.js:379 armiesInside:70_rules.js:382 terrPen:70_rules.js:384 terrBlocked:70_rules.js:385 terrWaterStop:70_rules.js:386 terrStrain:70_rules.js:387 provinceOf:70_rules.js:389 moveTraits:70_rules.js:391 speedOf:70_rules.js:394 hexNb:70_rules.js:426 auraSources:70_rules.js:430 moveRange:70_rules.js:440 moveInfo:70_rules.js:475 moveStops:70_rules.js:478 moveEndTriggers:70_rules.js:483 moveArmyTo:70_rules.js:492 moveOverlay:70_rules.js:512 movePanelHTML:70_rules.js:525 set:70_rules.js:536 computeAll:70_rules.js:537 sceneInfra:80_scene_shell.js:14 wardChains:80_scene_shell.js:20 sceneLots:80_scene_shell.js:27 renderEsBar:80_scene_shell.js:40 sceneArmies:80_scene_shell.js:48 renderScene:80_scene_shell.js:55 renderSettlements:80_scene_shell.js:170 lockTarget:80_scene_shell.js:233 lockBlock:80_scene_shell.js:242 adminUI:80_scene_shell.js:255 firstHostOpen:80_scene_shell.js:271 firstHostBtn:80_scene_shell.js:272 hudSign:80_scene_shell.js:278 hudData:80_scene_shell.js:279 hudTips:80_scene_shell.js:288 renderHUD:80_scene_shell.js:301 ageStripHTML:80_scene_shell.js:321 setupOn:80_scene_shell.js:335 renderSetup:80_scene_shell.js:336 checkedIn:80_scene_shell.js:363 checkinFD:80_scene_shell.js:364 checkinTxt:80_scene_shell.js:370 checkinHTML:80_scene_shell.js:371 setupHoldHTML:80_scene_shell.js:378 renderTurnStrip:80_scene_shell.js:398 syncBoardEndBtn:80_scene_shell.js:430 mnavSync:80_scene_shell.js:446 herName:80_scene_shell.js:456 herKey:80_scene_shell.js:457 lumOf:80_scene_shell.js:458 herMix:80_scene_shell.js:462 herN:80_scene_shell.js:464 herPaths:80_scene_shell.js:465 heraldOf:80_scene_shell.js:470 mapBanner:80_scene_shell.js:473 pTok:80_scene_shell.js:476 inboxItems:85_ux.js:10 renderInbox:85_ux.js:23 evIn:85_ux.js:41 hudPopBack:85_ux.js:55 hudPopFill:85_ux.js:57 hudPop:85_ux.js:83 hudPopClose:85_ux.js:84 renderChrome:85_ux.js:90 undoSnap:90_app.js:5 undoRecord:90_app.js:7 undoRebase:90_app.js:13 undoScoped:90_app.js:14 undoApply:90_app.js:15 doUndo:90_app.js:28 doRedo:90_app.js:29 undoButtons:90_app.js:30 actSnap:90_app.js:43 actRebase:90_app.js:44 actJoin:90_app.js:46 actSchedule:90_app.js:49 fmtG:90_app.js:50 boardDiff:90_app.js:51 actFlush:90_app.js:83 gameAllowed:90_app.js:100 gameData:90_app.js:101 refreshGames:90_app.js:102 gameReplace:90_app.js:105 newGameState:90_app.js:110 isReady:90_app.js:136 readyCheck:90_app.js:137 gslug:90_app.js:151 kwify:90_app.js:163 wikiA:90_app.js:174 gkHtml:90_app.js:175 openFromHash:90_app.js:192 setLift:90_app.js:218 gkShow:90_app.js:227 gkHide:90_app.js:231 gkFor:90_app.js:232 chatHdr:90_app.js:291 chatTargets:90_app.js:297 chatParse:90_app.js:299 chatColor:90_app.js:307 chatLine:90_app.js:308 chatRender:90_app.js:312 chatSys:90_app.js:318 chatComplete:90_app.js:333
```
