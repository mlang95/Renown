# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-10-18 · data VERSION `0.4.9.9.13-d10-SIMPLE` · HEAD `49204d0 2026-10-17`

Hand-written orientation: `CLAUDE.md` (same folder). Paths below are relative to the repo root.

## 1. Folder tree

```
./  (11 files)
  0.4.8 Updated Docs/  (7 files)
  0.4.8.1/  (36 files)
  Assets/  (102 files, generated/assets — not indexed)
  CE/  (31 files)
    Combatv4/  (18 files)
      shims/  (6 files)
    Tasks/  (20 files)
    ask-the-bot/  (3 files)
    lab_out/  (465 files, generated/assets — not indexed)
    mapgen/  (17 files)
      maps/  (20 files)
    references/  (51 files)
      board/  (2 files)
        js/  (12 files)
      fonts/  (16 files, generated/assets — not indexed)
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
  RenownWiki/  (93 files)
    mapgen/  (1 files)
  generators/  (22 files)
```

## 2. Source files

| File | Lines | Purpose |
|---|---|---|
| `REPO_MAP.md` | 810 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
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
| `CE\CLAUDE.md` | 66 | CLAUDE.md — Renown repo orientation (lives in `CE/`; paths below are relative to `CE/`) |
| `CE\COMPREHENSIVE_RULES_OUTLINE.md` | 180 | Renown — Comprehensive Rules: outline |
| `CE\ENVOY_WINDOW_REVIEW.md` | 86 | Envoy timing windows — review list |
| `CE\REPO_MAP.md` | 874 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE\RULES_push.md` | 649 | Renown |
| `CE\RULES_push_simple.md` | 729 | Renown |
| `CE\RULES_reorganized_6.md` | 638 | Renown |
| `CE\SIMPLE_NODES.PY` | 1 |  |
| `CE\TASK8_NOTES.md` | 152 | claude_task_8 — what changed, open items |
| `CE\build_all_CE.bat` | 506 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE\ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\infra.py` | 109 |  |
| `CE\parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE\patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE\rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE\renown_data.py` | 4677 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d10.py` | 4677 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d8.py` | 2801 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_server.bat` | 16 | renown_server.bat - (re)start the Renown board server in WSL. |
| `CE\repo_map.py` | 250 | repo_map.py — write REPO_MAP.md next to this file (CE/, beside CLAUDE.md): a generated index of the Renown repo for |
| `CE\run_tournament_d10.bat` | 108 | Renown d10 tournament runner  —  CE build |
| `CE\run_tournament_d10.py` | 131 | run_tournament_d10.py — run the Renown tournament against the d10 build. |
| `CE\sprites.py` | 3051 | sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene). |
| `CE\verify_d10.py` | 169 | verify_d10.py — prove the CE wiring is live before spending hours on a run. |
| `CE\Combatv4\analysis.py` | 2125 | Analysis module for tournament results. |
| `CE\Combatv4\batch_engine.py` | 1633 | Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays, |
| `CE\Combatv4\combat_kernel_d10.py` | 268 | combat_kernel.py — SHARED numba kernels for both combat engines. |
| `CE\Combatv4\combat_morale_d10.py` | 155 | combat_morale.py — SHARED morale phase for both combat engines (C2, subsystem 2). |
| `CE\Combatv4\combat_primitives_d10.py` | 147 | combat_primitives.py — SHARED rules-math layer for both combat engines (C2). |
| `CE\Combatv4\dice_config.py` | 116 | dice_config — single source for die size across both combat engines. |
| `CE\Combatv4\loadouts.py` | 1841 | Loadout generator for the combat tournament. |
| `CE\Combatv4\make_d10_data.py` | 172 | Generate renown_data_d10.py from renown_data_CE.py. |
| `CE\Combatv4\make_d10_engines.py` | 143 | Generate *_d10.py engine files with FACES parameterised. |
| `CE\Combatv4\normalized_matrix.py` | 277 | Normalized symmetric tactic matrix. |
| `CE\Combatv4\playstyles.py` | 784 | Playstyle module — playstyles drive tactic selection in combat. |
| `CE\Combatv4\renown_combat_d10.py` | 563 | Renown combat simulator. |
| `CE\Combatv4\renown_data.py` | 2715 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\Combatv4\run_tournament.py` | 197 | Standalone Renown tournament runner. |
| `CE\Combatv4\tactics_analysis.py` | 54 | Tactics analysis helpers for the Renown Combat Lab. |
| `CE\Combatv4\tournament_vec.py` | 359 | Vectorized tournament runner — same interface as tournament.py but ~4x faster |
| `CE\Combatv4\vectorized_combat_d10.py` | 1992 | Vectorized matchup runner. |
| `CE\Combatv4\shims\combat_kernel.py` | 15 | SHIM — do not edit. Redirects `import combat_kernel` to combat_kernel_d10. |
| `CE\Combatv4\shims\combat_morale.py` | 15 | SHIM — do not edit. Redirects `import combat_morale` to combat_morale_d10. |
| `CE\Combatv4\shims\combat_primitives.py` | 15 | SHIM — do not edit. Redirects `import combat_primitives` to combat_primitives_d10. |
| `CE\Combatv4\shims\renown_combat.py` | 15 | SHIM — do not edit. Redirects `import renown_combat` to renown_combat_d10. |
| `CE\Combatv4\shims\renown_data.py` | 15 | SHIM — do not edit. Redirects `import renown_data` to renown_data_d10. |
| `CE\Combatv4\shims\vectorized_combat.py` | 15 | SHIM — do not edit. Redirects `import vectorized_combat` to vectorized_combat_d10. |
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
| `CE\ask-the-bot\renown_faq.txt` | 500 |  |
| `CE\mapgen\app_shell.html` | 667 | Renown — Map Generator |
| `CE\mapgen\build_board.py` | 442 | build_board.py - print-and-tape Renown board from a procedural map. |
| `CE\mapgen\build_mapapp.py` | 192 | build_mapapp.py - assemble renown-maps.html from its sources. |
| `CE\mapgen\gen.js` | 1677 | gen.js — Renown regional map generator, JS port. |
| `CE\mapgen\gen_settlement_board.py` | 5268 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE\mapgen\hexgen.py` | 258 | hexgen.py — generate the Renown hex asset set as standalone SVGs. |
| `CE\mapgen\hexmap.py` | 85 | hexmap.py — the territory graph (C1). |
| `CE\mapgen\hexstyle.py` | 270 | hexstyle.py - the ONE source for how a board looks. |
| `CE\mapgen\mapgen.py` | 863 | mapgen.py — procedural Renown map generator. |
| `CE\mapgen\mapgen_regional.py` | 1930 | mapgen_regional.py — preset-driven map generation for Renown. |
| `CE\mapgen\presets.js` | 1392 | presets.js - GENERATED from region_presets.py. Do not hand-edit. */ |
| `CE\mapgen\region_presets.py` | 471 | region_presets.py — regional map-generation presets for Renown. |
| `CE\mapgen\renown-maps.html` | 3734 | Renown — Map Generator |
| `CE\references\build_compendium.js` | 133 | build_compendium.js — render the Compendium .docx from renown_data JSON, |
| `CE\references\build_compendium.py` | 394 | build_compendium2.py — redesigned Compendium .docx from compendium_data.json. |
| `CE\references\build_wiki.py` | 1498 | build_wiki.py — multi-page linked HTML wiki from RULES.md + renown_data. |
| `CE\references\card_copies.py` | 69 | card_copies.py — print-quantity logic for pursuit cards, driven by the spec |
| `CE\references\card_sheet.py` | 679 | Renown — Specialization card sheet generator. |
| `CE\references\ce_paths.py` | 123 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\references\combat_sheet.py` | 352 | combat_sheet.py — Renown combat quick-reference (print & laminate). |
| `CE\references\combine_docx.py` | 257 | combine_docx.py — append the Compendium after the Rules doc as one book: |
| `CE\references\compendium_data.json` | 3273 |  |
| `CE\references\display_pdf.py` | 90 | display_pdf.py — NAME_DISPLAY for every reportlab sheet (cards, tiles, equipment, combat). |
| `CE\references\docx_tables.py` | 540 | docx_tables.py — generate Word table fragments (OOXML) from renown_data. |
| `CE\references\domain_board.py` | 341 | domain_board.py - landscape Domain Standing Board. |
| `CE\references\effect_registry.py` | 319 | effect_registry.py -- every rules-text pattern the settlement board acts on, matched once at build time. |
| `CE\references\equipment_sheet.py` | 691 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `CE\references\faction_sheet.py` | 447 | Renown — Faction card sheet generator. |
| `CE\references\faq_export.py` | 439 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `CE\references\gen_compendium.py` | 185 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `CE\references\gen_layout.py` | 374 | gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data. |
| `CE\references\gen_layout_roots.py` | 123 | gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it. |
| `CE\references\gen_settlement_board.py` | 1050 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE\references\generate_cards.py` | 93 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `CE\references\host_sheet.py` | 452 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `CE\references\infra_board.py` | 134 | infra_board.py - landscape Infrastructure Board. |
| `CE\references\layout.json` | 1421 |  |
| `CE\references\layout_roots.json` | 1352 |  |
| `CE\references\layout_simple.json` | 1525 |  |
| `CE\references\md_to_docx.py` | 329 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `CE\references\package-lock.json` | 205 |  |
| `CE\references\package.json` | 6 |  |
| `CE\references\parity_efx.js` | 54 | parity_efx.js — replays effect_registry.py's patterns with JavaScript RegExp, the way the board used to read text at |
| `CE\references\patch_pursuit_domains.py` | 58 | patch_pursuit_domains.py |
| `CE\references\playstyle_reference.py` | 395 | playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture). |
| `CE\references\pursuit_tiles.py` | 282 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `CE\references\reference_sheets.py` | 811 | Renown — Reference sheet generators. |
| `CE\references\render_tree.py` | 272 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `CE\references\server.py` | 501 | Renown settlement-board server  —  stdlib only, no pip installs. |
| `CE\references\settlement_board.html` | — | generated HTML (1428 KB) |
| `CE\references\settlement_mats.py` | 296 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `CE\references\spec_tree_sheet.py` | 1183 | Renown — Specialization Tree renderer. |
| `CE\references\svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `CE\references\sync_derived.py` | 116 | sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES. |
| `CE\references\tactic_sheet.py` | 446 | Renown — Tactic card sheet generator (v3). |
| `CE\references\wiki_markers.py` | 290 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
| `CE\references\world.txt` | 1517 |  |
| `CE\references\worldtxt.py` | 328 | worldtxt.py — parse the hand-maintained world.txt lore book into structured |
| `CE\references\board\body.html` | 214 |  |
| `CE\references\board\js\00_core.js` | 49 | __DATA__*/; |
| `CE\references\board\js\10_table.js` | 761 | ===================== TABLE: seating, Council & Envoy phases ===================== |
| `CE\references\board\js\15_realm.js` | 353 | ===================== REALM: the play surface ===================== |
| `CE\references\board\js\20_state.js` | 504 | ---- state: multiplayer dashboard ---- |
| `CE\references\board\js\30_empire.js` | 1641 | ---- catalog ---- |
| `CE\references\board\js\40_realm_data.js` | 388 | ---- Dashboards view ---- |
| `CE\references\board\js\50_battle.js` | 623 | ---- Battle ---- |
| `CE\references\board\js\60_map.js` | 1000 | ---- Map view ---- |
| `CE\references\board\js\70_rules.js` | 480 | ===================== EFFECT PLUMBING: the effect registry (references/effect_registry.py) ===================== |
| `CE\references\board\js\80_scene_shell.js` | 440 | ---- pixel scene: every settlement of the active player, drawn from sprites.py (every theme) ---- |
| `CE\references\board\js\85_ux.js` | 97 | ===================== CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper ===================== |
| `CE\references\board\js\90_app.js` | 363 | ===================== UNDO / REDO ===================== |
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
| `RenownWiki\actions-ref.html` | 19 | Actions — Renown |
| `RenownWiki\bandits-ref.html` | 19 | Bandits — Renown |
| `RenownWiki\board.html` | 19 | Board Emulator — Renown |
| `RenownWiki\domain-board-ref.html` | 19 | Domain Board — Renown |
| `RenownWiki\domain-cunning.html` | 19 | Cunning Holdings — Renown |
| `RenownWiki\domain-industry.html` | 19 | Industry Holdings — Renown |
| `RenownWiki\domain-piety.html` | 19 | Piety Holdings — Renown |
| `RenownWiki\domain-prowess.html` | 19 | Prowess Holdings — Renown |
| `RenownWiki\economy-ref.html` | 19 | Economy Reference — Renown |
| `RenownWiki\edicts-ref.html` | 19 | Edicts — Renown |
| `RenownWiki\envoy-outcomes-ref.html` | 19 | Envoy Outcomes — Renown |
| `RenownWiki\equipment-ref.html` | 19 | Equipment — Renown |
| `RenownWiki\eras-ref.html` | 19 | Eras — Renown |
| `RenownWiki\escalation-pursuits.html` | 19 | Escalation Combat Holdings — Renown |
| `RenownWiki\escalation-rules.html` | 19 | Escalation Battle Rules — Renown |
| `RenownWiki\escalation.html` | 19 | Escalation Campaign — Renown |
| `RenownWiki\factions.html` | 19 | Heritages — Renown |
| `RenownWiki\glossary.html` | 19 | Glossary — Renown |
| `RenownWiki\index.html` | 19 | Renown Rules — Renown |
| `RenownWiki\infrastructure-ref.html` | 19 | Infrastructure — Renown |
| `RenownWiki\keywords-ref.html` | 19 | Combat Keywords — Renown |
| `RenownWiki\lore-ages.html` | 19 | The Timeline — Renown |
| `RenownWiki\lore-cultures.html` | 19 | The Fifteen — Renown |
| `RenownWiki\lore-darkness.html` | 19 | The Age of Darkness — Renown |
| `RenownWiki\lore-map.html` | 19 | The Map — Renown |
| `RenownWiki\lore.html` | 19 | The World of Vaelohk — Renown |
| `RenownWiki\maps.html` | 19 | Map Generator — Renown |
| `RenownWiki\paths.html` | 19 | Build Paths — Renown |
| `RenownWiki\public-order-ref.html` | 19 | Public Order — Renown |
| `RenownWiki\pursuits.html` | 19 | Holdings — Renown |
| `RenownWiki\reference-tables.html` | 19 | Reference Tables — Renown |
| `RenownWiki\rules-action-mechanics.html` | 39 | Action Mechanics — Renown |
| `RenownWiki\rules-armies.html` | 32 | Armies — Renown |
| `RenownWiki\rules-armor.html` | 21 | Armor — Renown |
| `RenownWiki\rules-bandits.html` | 62 | Bandits — Renown |
| `RenownWiki\rules-battle-phase.html` | 84 | Battle Phase — Renown |
| `RenownWiki\rules-core-principles.html` | 77 | Core Principles — Renown |
| `RenownWiki\rules-cunning-actions.html` | 20 | Cunning Actions — Renown |
| `RenownWiki\rules-diplomacy-actions.html` | 24 | Diplomacy Actions — Renown |
| `RenownWiki\rules-diplomacy-treaties.html` | 44 | Diplomacy &amp; Treaties — Renown |
| `RenownWiki\rules-domains-standings.html` | 28 | Domains &amp; Standings — Renown |
| `RenownWiki\rules-factions.html` | 20 | Heritages — Renown |
| `RenownWiki\rules-holdings.html` | 20 | Holdings — Renown |
| `RenownWiki\rules-index.html` | 20 | Index — Renown |
| `RenownWiki\rules-industry-actions.html` | 22 | Industry Actions — Renown |
| `RenownWiki\rules-influence.html` | 22 | Influence — Renown |
| `RenownWiki\rules-infrastructure.html` | 28 | Infrastructure — Renown |
| `RenownWiki\rules-introduction.html` | 55 | Introduction — Renown |
| `RenownWiki\rules-melee-weapons.html` | 20 | Melee Weapons — Renown |
| `RenownWiki\rules-piety-actions.html` | 20 | Piety Actions — Renown |
| `RenownWiki\rules-player-setup.html` | 25 | Player Setup — Renown |
| `RenownWiki\rules-prowess-actions.html` | 20 | Prowess Actions — Renown |
| `RenownWiki\rules-public-order.html` | 25 | Public Order — Renown |
| `RenownWiki\rules-ranged-weapons.html` | 20 | Ranged Weapons — Renown |
| `RenownWiki\rules-reading-these-rules.html` | 30 | Reading These Rules — Renown |
| `RenownWiki\rules-renown.html` | 22 | Renown — Renown |
| `RenownWiki\rules-seasons.html` | 21 | Seasons — Renown |
| `RenownWiki\rules-settlements.html` | 30 | Settlements — Renown |
| `RenownWiki\rules-setup-order.html` | 30 | Setup Order — Renown |
| `RenownWiki\rules-shields.html` | 20 | Shields — Renown |
| `RenownWiki\rules-siege-warfare.html` | 55 | Siege Warfare — Renown |
| `RenownWiki\rules-table-setup.html` | 23 | Table Setup — Renown |
| `RenownWiki\rules-territory-terrain.html` | 26 | Territory &amp; Terrain — Renown |
| `RenownWiki\rules-the-turn.html` | 106 | The Turn — Renown |
| `RenownWiki\rules-trade-income.html` | 36 | Trade &amp; Income — Renown |
| `RenownWiki\rules-treasury-upkeep.html` | 32 | Treasury &amp; Upkeep — Renown |
| `RenownWiki\search.js` | 7 |  |
| `RenownWiki\seasons-ref.html` | 19 | Seasons — Renown |
| `RenownWiki\settlement_board.html` | — | generated HTML (1428 KB) |
| `RenownWiki\settlements-ref.html` | 19 | Settlements — Renown |
| `RenownWiki\standing-established.html` | 19 | Established Tier — Renown |
| `RenownWiki\standing-rising.html` | 19 | Rising Tier — Renown |
| `RenownWiki\standing-sovereign.html` | 19 | Sovereign Tier — Renown |
| `RenownWiki\systems-ref.html` | 19 | Timers, Influence &amp; PO — Renown |
| `RenownWiki\tactic-matrix-ref.html` | 19 | Tactic Matrix — Renown |
| `RenownWiki\terrain-ref.html` | 19 | Terrain &amp; Movement — Renown |
| `RenownWiki\treaties-ref.html` | 19 | Treaties &amp; Alliances — Renown |
| `RenownWiki\turn-sequence.html` | 19 | Turn Sequence — Renown |
| `RenownWiki\type-arms.html` | 19 | Arms — Renown |
| `RenownWiki\type-commerce.html` | 19 | Commerce — Renown |
| `RenownWiki\type-court.html` | 19 | Court — Renown |
| `RenownWiki\type-devotion.html` | 19 | Devotion — Renown |
| `RenownWiki\type-husbandry.html` | 19 | Husbandry — Renown |
| `RenownWiki\type-logistics.html` | 19 | Logistics — Renown |
| `RenownWiki\type-monument.html` | 19 | Monument — Renown |
| `RenownWiki\type-raw-materials.html` | 19 | Raw Materials — Renown |
| `RenownWiki\type-secrecy.html` | 19 | Secrecy — Renown |
| `RenownWiki\type-works.html` | 19 | Works — Renown |
| `RenownWiki\ui.js` | 26 | theme toggle (head script already applied the stored/default theme) |
| `RenownWiki\mapgen\renown-maps.html` | 3734 | Renown — Map Generator |
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
| `VERSION` | 6 | str | '0.4.9.9.13-d10-SIMPLE' |
| `BLUNDER_THR` | 34 | int | 10 |
| `DICE_PROVENANCE` | 35 | str | 'd10 / Focused 10+ / Parry 8+ / Recover  |
| `SACK_EXTORT_PER_TIER` | 38 | int | 2000 |
| `WEALTH_EDICT_GOLD` | 39 | int | 50000 |
| `MUSTER_RANGE` | 40 | int | 2 |
| `MARCH_MULTIPLIER` | 41 | int | 2 |
| `PO_MIN` | 42 | int | -5 |
| `PO_MAX` | 43 | int | 10 |
| `INITIATIVE_MIN` | 44 | int | -2 |
| `INITIATIVE_MAX` | 45 | int | 2 |
| `STANDING_THRESHOLDS` | 46 | dict | 4 |
| `STEADY` | 57 | str | 'Steady' |
| `UNWIELDY` | 58 | str | 'Unwieldy' |
| `TWO_H` | 59 | str | '2H' |
| `SHATTER_ARMOR` | 60 | str | 'Deadly' |
| `UNSTOPPABLE` | 61 | str | 'Unstoppable' |
| `CLEAVE` | 62 | str | 'Cleave' |
| `POISON` | 63 | str | 'Poison' |
| `NIMBLE` | 64 | str | 'Nimble' |
| `DRILLED` | 65 | str | 'Drilled' |
| `DESTROY_SHIELD` | 66 | str | 'Destroy Shield' |
| `BLUNDER` | 67 | str | 'Blunder' |
| `ONE_SHOT` | 68 | str | 'One-Shot' |
| `DEFLECT` | 69 | str | 'Deflect' |
| `IMMUNE_PANIC` | 70 | str | 'Immune Panic' |
| `UNBREAKABLE` | 71 | str | 'Unbreakable' |
| `PARRY` | 72 | str | 'Parry' |
| `RIPOSTE` | 73 | str | 'Riposte' |
| `NO_PARRY` | 74 | str | 'Awkward' |
| `RECOVER` | 75 | str | 'Recover' |
| `SERRATED` | 76 | str | 'Serrated' |
| `SERRATED_MOD` | 77 | int | 2 |
| `ENDURING` | 78 | str | 'Enduring' |
| `STRAIN` | 79 | str | 'Strain' |
| `MINUS_1_TBH` | 80 | str | 'Shielded' |
| `PLANISHING` | 81 | str | 'Planishing' |
| `FATIGUE_TOKEN` | 82 | str | 'Fatigue Token' |
| `CRUSADER` | 83 | str | 'Righteous Fervour' |
| `IMMUNE` | 85 | str | 'Immune' |
| `immune` | 86 | function |  |
| `NEGATE` | 91 | str | 'Negate' |
| `negate` | 92 | function |  |
| `IMMUNE_DESTROY_SHIELD` | 98 | str | 'Immune Destroy Shield' |
| `IMMUNE_UNWIELDY` | 99 | str | 'Immune Unwieldy' |
| `IMMUNE_STRAIN` | 100 | str | 'Immune Strain' |
| `NEGATE_UNSTOPPABLE` | 102 | str | 'Immune Unstoppable' |
| `NEGATE_TEMPERED` | 104 | str | 'Negate Planishing' |
| `NEGATE_RIPOSTE` | 105 | str | 'Negate Riposte' |
| `NEGATE_SHIELDED` | 106 | str | 'Negate Shielded' |
| `MINUS_1_PARRY` | 107 | str | '-1 to Parry' |
| `HALFSWORD` | 108 | str | 'Halfsword' |
| `DUAL_WIELD` | 109 | str | 'Dual Wield' |
| `FLORENTINE` | 110 | str | 'Florentine' |
| `PIVOTAL` | 111 | str | 'Focused' |
| `GLOSSARY` | 114 | dict | 157 |
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
| `STANDING_EFFECTS` | 362 | dict | 4 |
| `TACTIC_MATRIX` | 385 | dict | 49 |
| `TACTICS` | 444 | list | 7 |
| `TACTIC_NOTES` | 446 | dict | 0 |
| `CULTURE_SELF_MADE` | 462 | str | 'Self-made' |
| `CULTURES` | 464 | dict | 15 |
| `NODES` | 616 | dict | 121 |
| `SIMPLE_NODES` | 1650 | dict | 121 |
| `HOLDING_GROUPS` | 2527 | dict | 9 |
| `SCOPES` | 2544 | tuple | 3 |
| `SCOPE_BY_TYPE` | 2545 | dict | 2 |
| `LINE_LABELS` | 2549 | dict | 28 |
| `lines_of` | 2580 | function |  |
| `LEGACY_NODES` | 2584 | dict | 108 |
| `REQ_KEY` | 2589 | str | 'infrastructure_req' |
| `REQ_LABEL` | 2590 | str | 'Infrastructure Req' |
| `TYPE_ORDER` | 2592 | list | 10 |
| `CHAIN_TERM` | 2595 | str | 'Mastery Chain' |
| `PURSUIT_TERM` | 2597 | tuple | 2 |
| `node_parents` | 2599 | function |  |
| `get_data` | 2619 | function |  |
| `FACTIONS` | 2629 | dict | 41 |
| `INFRASTRUCTURE` | 3130 | dict | 20 |
| `WONDERS` | 3265 | dict | 4 |
| `INFRA_TIERS` | 3266 | list | 5 |
| `SETTLEMENTS` | 3274 | dict | 5 |
| `ERAS` | 3283 | dict | 4 |
| `PO_BANDS` | 3298 | dict | 12 |
| `po_scale` | 3317 | function |  |
| `po_value` | 3324 | function |  |
| `po_effect` | 3329 | function |  |
| `PUBLIC_ORDER` | 3336 | dict | 12 |
| `PUBLIC_ORDER_BY_ERA` | 3337 | dict | 4 |
| `PO_MODIFIERS` | 3343 | dict | 2 |
| `DOMAIN_BOARD` | 3361 | dict | 6 |
| `SEASONS` | 3392 | dict | 4 |
| `TRADE_RULES` | 3400 | dict | 4 |
| `efficient_graph` | 3412 | function |  |
| `EFFICIENT_MULTI` | 3422 | dict | 112 |
| `EFFICIENT` | 3423 | dict | 112 |
| `BANDIT_CAMP_START` | 3431 | int | 10 |
| `BANDIT_CAMP_GOLD` | 3432 | int | 2000 |
| `BANDIT_ARMY_THRESHOLD` | 3433 | int | 25 |
| `BANDIT_GROWTH_PER_ERA` | 3434 | dict | 4 |
| `BANDIT_EQUIPMENT_PER_ERA` | 3435 | dict | 4 |
| `BANDITS` | 3436 | dict | 5 |
| `TIMERS` | 3444 | dict | 8 |
| `CHARTER_MIN_RANGE` | 3456 | int | 4 |
| `OUTLAW_BUFFER_RANGE` | 3457 | int | 2 |
| `HAMLET_RANGE` | 3458 | int | 2 |
| `OUTLAW_COUNTRY_START` | 3459 | int | 3 |
| `WILD_OUTLAW` | 3467 | dict | 9 |
| `wild_outlaw_count` | 3480 | function |  |
| `BANDIT_CAMP_REACH` | 3487 | str | 'province' |
| `VASSAL_EXCHANGE_CAP` | 3490 | int | 5000 |
| `VASSAL_INFLUENCE_TAKE` | 3491 | int | 3 |
| `BUILD_TIMERS` | 3495 | dict | 11 |
| `TERRAIN` | 3509 | dict | 7 |
| `MOVEMENT_MODIFIERS` | 3519 | dict | 6 |
| `TACTICAL_TERRAIN` | 3531 | dict | 7 |
| `TACTICAL_GLOBAL` | 3547 | list | 1 |
| `INFLUENCE_GAIN` | 3549 | dict | 9 |
| `ENVOY_OUTCOME_THRESHOLDS` | 3603 | dict | 4 |
| `ENVOY_OUTCOMES` | 3612 | dict | 5 |
| `ACTIONS` | 3634 | dict | 22 |
| `TREATIES` | 3824 | dict | 5 |
| `ALLIANCE_RULES` | 3832 | list | 3 |
| `EDICT_STREAK_TURNS` | 3842 | int | 5 |
| `EDICTS` | 3844 | dict | 7 |
| `BANDIT_BEHAVIOR` | 3858 | dict | 8 |
| `PURSUIT_UPKEEP_DEFAULT` | 3881 | int | 100 |
| `PURSUIT_UPKEEP_BY_TYPE` | 3882 | dict | 4 |
| `UPKEEP_TRACKS` | 3892 | dict | 3 |
| `HOLDING_TIER_COST` | 3899 | dict | 4 |
| `holding_standing` | 3907 | function |  |
| `holding_cost` | 3913 | function |  |
| `holding_build_time` | 3921 | function |  |
| `pursuit_upkeep` | 3928 | function |  |
| `ARMY_UPKEEP_NOTE` | 3939 | str | "Net Army Upkeep = the sum of each Army' |
| `COSTS` | 3943 | dict | 12 |
| `PHASES` | 3963 | tuple | 5 |
| `STARTING_TURN_PHASE_OPENER` | 3964 | str | 'Council' |
| `STANDING_ARMY_SIEGE_MODIFIER` | 3966 | int | 1 |
| `EMPIRE_START_TIERS` | 3968 | tuple | 2 |
| `STARTING_TREASURY` | 3969 | int | 10000 |
| `AGES` | 3975 | dict | 5 |
| `AGE_YEAR_SEASON` | 3982 | str | 'Spring' |
| `CAPITAL_EDGE_RANGE` | 3983 | int | 4 |
| `BOARD_SIZES` | 3985 | dict | 3 |
| `SIEGE_CALCULUS` | 3991 | dict | 2 |
| `SIEGE_SOURCE_VALUES` | 4006 | dict | 6 |
| `NAME_DISPLAY` | 4033 | dict | 71 |
| `TIER_DISPLAY` | 4062 | dict | 1 |
| `ITEM_TIER_DISPLAY` | 4068 | dict | 1 |
| `TERM_ENVOY_SCORE` | 4075 | str | 'Authority' |
| `display_score` | 4085 | function |  |
| `ALIASES` | 4095 | dict | 73 |
| `display` | 4105 | function |  |
| `display_tier` | 4110 | function |  |
| `display_text` | 4120 | function |  |
| `display_list` | 4143 | function |  |
| `display_md` | 4153 | function |  |
| `display_html` | 4160 | function |  |
| `display_obj` | 4172 | function |  |
| `undisplay` | 4185 | function |  |
| `verify_aliases` | 4194 | function |  |
| `BANDIT_FACES` | 4218 | int | 10 |
| `BANDIT_CUNNING_MIN` | 4219 | int | 10 |
| `die_table_ranges` | 4222 | function |  |
| `die_table_rows` | 4230 | function |  |
| `die_table_text` | 4238 | function |  |
| `die_table_lookup` | 4246 | function |  |
| `die_table_verify` | 4253 | function |  |
| `die_table_weights` | 4272 | function |  |
| `BANDIT_CUNNING_TABLE` | 4282 | dict | 5 |
| `bandit_cunning_ranges` | 4290 | function |  |
| `bandit_cunning_rows` | 4291 | function |  |
| `bandit_cunning_lookup` | 4292 | function |  |
| `bandit_cunning_text` | 4294 | function |  |
| `BANDIT_TACTIC_TABLE` | 4300 | dict | 6 |
| `BANDIT_TACTICS` | 4308 | list | 6 |
| `bandit_tactic_ranges` | 4310 | function |  |
| `bandit_tactic_rows` | 4311 | function |  |
| `bandit_tactic_lookup` | 4312 | function |  |
| `verify_bandit_tables` | 4315 | function |  |
| `RENOWN_MAX` | 4411 | int | 30 |
| `RENOWN_PER_TURN` | 4412 | int | 1 |
| `DOMAIN_POINTS_PER_TURN` | 4413 | int | 1 |
| `FACTION_NAMES` | 4637 | dict | 41 |
| `FACTION_TERM` | 4645 | tuple | 2 |
| `faction_body` | 4651 | function |  |
| `GLOSSARY_CATEGORIES` | 4659 | list | 17 |

## 4. Build steps — `CE\build_all_CE.bat`

| Label | Line | Scripts | Echo |
|---|---|---|---|
| `:maps` | 222 | `build_mapapp.py` | --- Map generator app ---; skipped - build_mapapp.py not ported |
| `:cards` | 242 | `generate_cards.py` | --- Cards ---; skipped - generate_cards.py not ported |
| `:docs` | 257 | `md_to_docx.py`, `combat_sheet.py`, `spec_tree_sheet.py`, `playstyle_reference.py`, `pursuit_tiles.py`, `gen_layout.py`, `render_tree.py`, `svg_to_pdf.py`, `domain_board.py`, `infra_board.py`, `settlement_mats.py`, `gen_layout_roots.py`, `gen_settlement_board.py`, `faq_export.py`, `host_sheet.py` | --- Docs ---; Rules - with Holdings, Equipment, Factions, glossary, index...; Combat quick-reference sheet...; Specialization trees...; Playstyle reference...; Pursuit ward-tiles...; Pursuit tech tree |
| `:wiki` | 299 | `build_wiki.py` | --- Wiki ---; skipped - build_wiki.py not ported; skipped - wiki_markers.py not ported, build_wiki imports it; skipped - %RULES_MD% not found; Wiki build FAILED - skipping repo push.; Syncing into %WI |
| `:pushrepo` | 354 | `repo_map.py` | --- Push repo (v%VERSION%, DIE=%DIE%) -^> %REPO_DIR% ---; Git LFS not installed ^(https://git-lfs.com^) - skipping repo push so a; large file can't be committed without LFS. Install once, then re-run. |
| `:end` | 426 | — | Done. Press any key to close. |
| `:board` | 436 | `build_board.py` | --- Board ---; skipped - build_board.py not ported; Board -^> %BOARD_OUT% |
| `:tactical` | 454 | `build_board.py` | --- Tactical board ---; skipped - build_board.py not ported; Tactical board -^> %TAC_OUT% |
| `:lore` | 476 | `gen_cultures.py`, `gen_intro.py`, `gen_draft.py`, `gen_pdf.py`, `gen_book_json.py` | --- Lore (world documents from renown_worldlore.py) ---; skipped - %DIR_LORE%\gen_cultures.py not ported; Lore -^> %LORE_OUT% |

## 5. Rules markers — `CE\RULES_push_simple.md`

- **{{TABLE}}** (30): `edicts`, `eras`, `timers`, `seasons`, `ages`, `net_influence`, `envoy_outcomes`, `influence_gain`, `domain_board`, `treaties`, `settlements`, `infrastructure`, `build_timers`, `terrain`, `public_order`, `po_modifiers`, `trade_rules`, `retinues`, `tactic_matrix`, `siege_calculus`, `bandit_armaments`, `bandit_growth`, `bandit_cunning`, `bandit_tactics`, `holdings`, `weapons`, `ranged`, `shields`, `armor`, `factions`
- **{{GLOSSARY}}** (16): `Reading the Rules`, `Council & Envoys`, `Actions`, `Domains & Scoring`, `Treaties`, `Settlements & Holdings`, `Map & Range`, `Economy & Public Order`, `Army States`, `Battle Structure`, `Combat Keywords — Defense`, `Combat Keywords — Offense`, `Combat Keywords — Handling`, `Combat Keywords — Immune / Negate`, `World`, `Equipment Tiers`
- **{{ACTIONS}}** (5): `Prowess`, `Cunning`, `Piety`, `Industry`, `Diplomacy`
- **{{LIST}}** (1): `ALLIANCE_RULES`
- **{{TERM}}** (1): `Speed X`
- **{{IDX}}** (25): `Era`, `Empire Phase`, `Council Phase`, `Envoy Phase`, `Battle Phase`, `Rest Phase`, `Season`, `Age`, `Settlement`, `Hamlet`, `Infrastructure`, `Primitive`, `Developed`, `Sophisticated`, `Prodigious`, `Wondrous`, `Wonder`, `Treasury`, `Revenue`, `Trade Agreement`, `Army`, `Lay Siege`, `Capture`, `Sack`, `Bandit Camp`
- **{{VAL}}** (88): `AGE_YEAR_SEASON`, `ARMY_MAX_RETINUES`, `BANDITS.Bandit Domain Value`, `BANDIT_ARMY_THRESHOLD`, `BANDIT_CAMP_GOLD`, `BANDIT_CAMP_START`, `BANDIT_CUNNING_MIN`, `BANDIT_FACES`, `BLUNDER_THR`, `CAPITAL_EDGE_RANGE`, `CAP_THR`, `CHARTER_MIN_RANGE`, `DICE_PROVENANCE`, `DOMAIN_BOARD.innate_influence_own_envoys.Established`, `DOMAIN_BOARD.innate_influence_own_envoys.Rising`, `DOMAIN_BOARD.innate_influence_own_envoys.Sovereign`, `DOMAIN_BOARD.innate_influence_own_envoys.Untested`, `DOMAIN_BOARD.max_influence_per_vote.Established`, `DOMAIN_BOARD.max_influence_per_vote.Rising`, `DOMAIN_BOARD.max_influence_per_vote.Sovereign`, `DOMAIN_BOARD.max_influence_per_vote.Untested`, `DOMAIN_POINTS_PER_TURN`, `ENDURANCE_REGAIN`, `ERAS.Ascension.innate_diplomacy_influence`, `ERAS.Ascension.max_influence_per_diplomacy_vote`, `ERAS.Eminence.innate_diplomacy_influence`, `ERAS.Eminence.max_influence_per_diplomacy_vote`, `ERAS.Founding.innate_diplomacy_influence`, `ERAS.Founding.max_influence_per_diplomacy_vote`, `ERAS.Founding.renown`, `ERAS.Zenith.innate_diplomacy_influence`, `ERAS.Zenith.max_influence_per_diplomacy_vote`, `FACES`, `FATIGUE_MORALE`, `FOCUSED_THR`, `FRONT_LINE_MAX`, `HAMLET_RANGE`, `INITIATIVE_MAX`, `INITIATIVE_MIN`, `MORALE_DICE_MAX`, `OUTLAW_BUFFER_RANGE`, `OUTLAW_COUNTRY_START`, `PANIC_CASUALTY_THRESHOLD`, `PARRY_BASE`, `PO_MAX`, `PO_MIN`, `PURSUIT_UPKEEP_BY_TYPE.Energy`, `PURSUIT_UPKEEP_BY_TYPE.Monument`, `PURSUIT_UPKEEP_BY_TYPE.Other`, `PURSUIT_UPKEEP_BY_TYPE.Power`, `RENOWN_PER_TURN`, `RESERVE_MAX`, `RETINUES.Knight Templar.cost`, `RETINUES.Knight Templar.to_hit`, `RETINUES.Levy.cost`, `RETINUES.Levy.to_hit`, `RETINUES.Man-at-Arms.cost`, `RETINUES.Man-at-Arms.to_hit`, `RETINUES.Sergeant.cost`, `RETINUES.Sergeant.to_hit`, `ROUT_THR`, `SACK_EXTORT_PER_TIER`, `SETTLEMENTS.City.wards`, `SETTLEMENTS.Hamlet.wards`, `SETTLEMENTS.Metropolis.reach`, `SETTLEMENTS.Metropolis.wards`, `SETTLEMENTS.Town.wards`, `SETTLEMENTS.Village.reach`, `SETTLEMENTS.Village.wards`, `SIEGE_CALCULUS.Lay Siege.floor`, `SIEGE_SOURCE_VALUES.Stone Walls.value`, `SIEGE_SOURCE_VALUES.Wooden Walls.value`, `STANDING_THRESHOLDS.Established`, `STANDING_THRESHOLDS.Rising`, `STANDING_THRESHOLDS.Sovereign`, `STANDING_THRESHOLDS.Untested`, `STARTING_TREASURY`, `STARTING_TURN_PHASE_OPENER`, `TIMERS.Capture Timer.default`, `TIMERS.Sack Timer.default`, `TRADE_RULES.income_per_craft`, `VASSAL_EXCHANGE_CAP`, `VASSAL_INFLUENCE_TAKE`, `WEALTH_EDICT_GOLD`, `WILD_OUTLAW.border_range`, `WILD_OUTLAW.per_players`, `WILD_OUTLAW.plus`, `WILD_OUTLAW.spacing`
- **docx_tables.REGISTRY** (31): `ages`, `armor`, `bandit_armaments`, `bandit_cunning`, `bandit_growth`, `bandit_tactics`, `build_timers`, `domain_board`, `edicts`, `envoy_outcomes`, `eras`, `factions`, `holdings`, `influence_gain`, `infrastructure`, `net_influence`, `po_modifiers`, `public_order`, `ranged`, `retinues`, `seasons`, `settlements`, `shields`, `siege_calculus`, `tactic_matrix`, `tactical_terrain`, `terrain`, `timers`, `trade_rules`, `treaties`, `weapons`

Headings:

| Line | Heading |
|---|---|
| 1 | # Renown |
| 7 | # Introduction |
| 11 | ### Game Synopsis |
| 31 | ### How to Win (Edicts) |
| 41 | ### Game Structure |
| 47 | ### Key Resources |
| 59 | # Core Rules |
| 61 | ## Reading These Rules |
| 75 | ## Core Principles |
| 114 | ## The Turn |
| 126 | ### Timers |
| 134 | ### Empire Phase |
| 160 | ### Council Phase |
| 172 | ### Envoy Phase |
| 183 | ### Battle Phase |
| 187 | ### Rest Phase |
| 201 | # Seasons |
| 207 | # Setup |
| 209 | ## Table Setup |
| 214 | ## Setup Order |
| 223 | ### Ages |
| 229 | ## Player Setup |
| 236 | # Actions & Voting |
| 238 | ## Action Mechanics |
| 240 | ### Sending an Envoy |
| 244 | ### Resolving an Envoy |
| 276 | ## Influence |
| 284 | ## Prowess Actions |
| 288 | ## Cunning Actions |
| 292 | ## Piety Actions |
| 296 | ## Industry Actions |
| 300 | ### Rule: Ulterior Motive |
| 304 | ## Diplomacy Actions |
| 310 | ### Rule: Diplomatic Mission |
| 316 | # Domains & Standings |
| 318 | ### Domain Standings |
| 328 | ### Standing & Influence |
| 341 | # Diplomacy & Treaties |
| 343 | ### Treaties & Alliances |
| 351 | ### Vassalization |
| 373 | # Empire Building |
| 375 | ## Settlements |
| 381 | ### Settlement Wards |
| 385 | ### Chartering Settlements |
| 389 | ### Settlement Reach |
| 393 | ### Hamlets |
| 399 | ## Infrastructure |
| 419 | ## Territory & Terrain |
| 435 | # Economy |
| 437 | ## Public Order |
| 447 | ### Innate Public Order Modifiers |
| 451 | ## Treasury & Upkeep |
| 461 | ### Insolvency & Bankruptcy |
| 474 | ## Trade & Income |
| 476 | ### Who Can Trade & Income |
| 491 | ### Income Types |
| 499 | # Armies |
| 501 | ### Armies Overview |
| 511 | ### Mustering |
| 521 | ### Blocked Armies |
| 527 | # Battles & Sieges |
| 529 | ## Battle Phase |
| 531 | ### Begin Battle |
| 533 | ### Begin Skirmish |
| 541 | ### How a Battle Resolves |
| 545 | ### Begin the Battle — Seize the Initiative |
| 549 | ### The Skirmish Steps |
| 573 | ### Resolve Battle |
| 581 | ### End Battle |
| 583 | ### Tactic Matrix |
| 597 | ## Siege Warfare |
| 603 | ### Siege Timer |
| 609 | ### Beginning a Siege |
| 619 | ### Resolving a Siege |
| 632 | # Bandits |
| 634 | ### Outlaw Country |
| 643 | ### Spawning Bandit Camps |
| 649 | ### Growing Bandit Camps |
| 653 | ### Bandit Armaments by Era |
| 657 | ### Bandit Growth by Era |
| 661 | ### Bandit Info |
| 681 | ### Bandit Army Behavior |
| 693 | ### Attacking a Bandit Camp |
| 699 | # Holdings |
| 703 | # Equipment |
| 705 | ## Melee Weapons |
| 709 | ## Ranged Weapons |
| 713 | ## Shields |
| 717 | ## Armor |
| 723 | # Factions |
| 727 | # Index |

## 6. Settlement board — `CE\references\gen_settlement_board.py` + `CE\references\board\js/*.js` (+ `board.css`, `body.html`)

Payload keys passed to the HTML as `DATA` (65): `records`, `naturalNames`, `externalTokens`, `simple`, `chainTerm`, `pursuitTerm`, `infra`, `wonders`, `armySrc`, `equip`, `glossary`, `domainBoard`, `publicOrder`, `domainBoardFx`, `poByEra`, `wikiBase`, `wikiHome`, `tree`, `rulebook`, `limits`, `eras`, `edicts`, `envoyOutcomes`, `outcomeThresh`, `startPhase`, `actions`, `phaseRules`, `phaseSteps`, `rulesConst`, `ages`, `domains`, `standings`, `tradePerCraft`, `noTradeSeason`, `renownPerTurn`, `dpPerTurn`, `settlements`, `battle`, `terrainRef`, `banditLoadouts`, `bandits`, `treaties`, `allianceRules`, `startTiers`, `startTreasury`, `pursuitUpkeep`, `buildTimers`, `infraTiers`, `timers`, `seasons`, `poModifiers`, `vassalInfluenceTake`, `aliases`, `scoreTerm`, `costs`, `influenceGain`, `siege`, `factions`, `cultures`, `cultureSelf`, `placeNames`, `warnings`, `version`, `sprites`, `efx`

Python: `load`:27, `strip_md`:34, `has_cond`:76, `to_int`:79, `classify`:82, `_iv`:149, `envoy_fx`:150, `combine_parts`:250, `combine_effects`:291, `rules_payload`:295, `tree_payload`:353, `parse_effects`:387, `parse_mreq`:393, `classify_req_token`:401, `build`:410, `font_faces`:554, `_pursuit_term_template`:579, `render_html`:587, `_style_js`:595, `place_names_payload`:606, `sprite_payload`:626, `find_mapgen`:648, `_board_template`:663, `check_rules`:676, `_val`:794, `rules_section`:803, `phase_steps`:822, `battle_data`:836, `bandit_loadouts`:857, `effects_report`:905, `main`:936

JS sections: TABLE: seating, Council & Envoy phases :10_table.js:1, Action automation: Perform picker + resolution :10_table.js:242, REALM: the play surface :15_realm.js:1,  :40_realm_data.js:266, Inspect tool :60_map.js:273, EFFECT PLUMBING: the effect registry (references/effect_registry.py) :70_rules.js:1, ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS :70_rules.js:57, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :70_rules.js:141, CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper :85_ux.js:1, UNDO / REDO :90_app.js:1, ACTIVITY LOG :90_app.js:39, GAME: save · load · new :90_app.js:98, HOVER KEYWORDS :90_app.js:144

JS functions (839, name:file:line):

```
fixBastard:00_core.js:8 dispScore:00_core.js:15 POB:00_core.js:34 poNum:00_core.js:35 efxOf:00_core.js:46 hitOf:00_core.js:47 facHit:00_core.js:48 tnow:10_table.js:12 noteServerDate:10_table.js:13 lockOn:10_table.js:21 claimOf:10_table.js:22 mine:10_table.js:23 myClaimP:10_table.js:24 canEdit:10_table.js:25 boardEndOn:10_table.js:27 TB:10_table.js:28 seatFloor:10_table.js:30 tSeats:10_table.js:31 tTimer:10_table.js:32 tTurn:10_table.js:33 tPhase:10_table.js:34 PT:10_table.js:36 tCur:10_table.js:37 tCurW:10_table.js:38 sameP:10_table.js:39 meP:10_table.js:40 canAct:10_table.js:41 seatMap:10_table.js:44 seated:10_table.js:48 isSpring:10_table.js:49 hostP:10_table.js:50 voteOrd:10_table.js:52 tOrder:10_table.js:53 canHost:10_table.js:54 seatsLocked:10_table.js:55 tStand:10_table.js:58 eraRec:10_table.js:59 diploInf:10_table.js:60 diploCap:10_table.js:61 eraActions:10_table.js:62 boardFx:10_table.js:65 fxOf:10_table.js:78 scopeOk:10_table.js:79 sgn:10_table.js:80 fxLabel:10_table.js:81 atWarPair:10_table.js:96 opposeBlock:10_table.js:97 domAsFx:10_table.js:104 innateParts:10_table.js:105 modSum:10_table.js:111 innateInf:10_table.js:113 voteCap:10_table.js:114 inflPool:10_table.js:117 personalEnvoys:10_table.js:118 councilEnvoys:10_table.js:119 tOutcome:10_table.js:120 outText:10_table.js:122 tPlan:10_table.js:125 missionWhy:10_table.js:141 domStarted:10_table.js:144 tSim:10_table.js:147 performEval:10_table.js:213 comboEval:10_table.js:219 failPassFx:10_table.js:228 actionsOf:10_table.js:229 actReqFlag:10_table.js:231 actInfoHTML:10_table.js:235 actCost:10_table.js:246 domCost:10_table.js:248 addFaith:10_table.js:249 alliedP:10_table.js:250 allyGroup:10_table.js:251 topPair:10_table.js:252 actDoubt:10_table.js:255 musterOpts:10_table.js:310 runMuster:10_table.js:315 buildOpts:10_table.js:328 buildPlaces:10_table.js:336 runBuild:10_table.js:340 improveOpts:10_table.js:346 runImprove:10_table.js:352 runCharter:10_table.js:359 repairOpts:10_table.js:364 runRepair:10_table.js:367 settName:10_table.js:371 warOnFac:10_table.js:374 warOn:10_table.js:378 grandVizier:10_table.js:382 pfSpec:10_table.js:385 pfTargets:10_table.js:387 pfSubs:10_table.js:397 pfSubLabel:10_table.js:398 evTxt:10_table.js:400 insteadFx:10_table.js:405 actDom:10_table.js:406 pfActs:10_table.js:407 pfInsteadSrc:10_table.js:408 pfForm:10_table.js:409 boardCounts:10_table.js:444 pendingOf:10_table.js:446 apLines:10_table.js:448 resolveEnvoy:10_table.js:451 autoRes:10_table.js:493 tApply:10_table.js:494 tNext:10_table.js:505 tSetPhase:10_table.js:506 grantDP:10_table.js:508 dpOwed:10_table.js:509 tEndTurn:10_table.js:510 setSeats:10_table.js:530 tAutoSeat:10_table.js:535 tSig:10_table.js:541 tName:10_table.js:544 tVoteTxt:10_table.js:545 envBadges:10_table.js:546 innateTxt:10_table.js:552 tOutCls:10_table.js:554 tPerformHtml:10_table.js:555 summaryLines:10_table.js:576 chronOn:10_table.js:593 chron:10_table.js:594 chronSnap:10_table.js:597 chronTick:10_table.js:604 chronDate:10_table.js:614 empireChecklistHTML:10_table.js:615 treeSave:10_table.js:625 mapRaws:10_table.js:635 refRawAvail:10_table.js:638 treeHTML:10_table.js:642 rulebookHTML:10_table.js:709 linkifyRules:10_table.js:712 renderReference:10_table.js:716 tCountdown:10_table.js:729 applyTheme:10_table.js:744 applySkin:10_table.js:756 doFire:15_realm.js:8 patch:15_realm.js:12 rlCommit:15_realm.js:13 pOf:15_realm.js:14 rlOpen:15_realm.js:20 rlToggle:15_realm.js:21 renderTable:15_realm.js:26 renderRealmMap:15_realm.js:46 domCells:15_realm.js:58 realmTableHTML:15_realm.js:62 spectating:15_realm.js:103 miniCardHTML:15_realm.js:115 phaseCardHTML:15_realm.js:125 dockCard:15_realm.js:174 dockHTML:15_realm.js:175 envoyQueueHTML:15_realm.js:238 inflCardHTML:15_realm.js:257 drawersHTML:15_realm.js:309 turnLogItems:15_realm.js:321 turnLogHTML:15_realm.js:341 realmTimersBrief:15_realm.js:350 startDoms:20_state.js:2 ageRec:20_state.js:5 ageRisingOf:20_state.js:6 startDomsFor:20_state.js:7 startDomTotal:20_state.js:8 curYear:20_state.js:9 applyAgeStart:20_state.js:10 startSettlements:20_state.js:12 startSig:20_state.js:15 reseedIfPristine:20_state.js:17 newBoard:20_state.js:22 newPlayer:20_state.js:24 normalizeD:20_state.js:39 activeBoard:20_state.js:59 reindex:20_state.js:60 pActive:20_state.js:73 ignHas:20_state.js:77 flagState:20_state.js:78 ignBtn:20_state.js:83 ignNote:20_state.js:86 unlockStatus:20_state.js:92 nameHit:20_state.js:103 missTxt:20_state.js:104 recomputePC:20_state.js:106 buildTimerMod:20_state.js:111 withBuildMod:20_state.js:115 pursuitBaseTime:20_state.js:116 infraBaseTime:20_state.js:117 pursuitBuildTime:20_state.js:118 infraBuildTime:20_state.js:119 buildNote:20_state.js:120 settBaseTime:20_state.js:121 settBuildTime:20_state.js:122 itm:20_state.js:123 infraOn:20_state.js:124 gameStarted:20_state.js:125 glogTurn:20_state.js:129 glogSea:20_state.js:130 glogPush:20_state.js:131 glogSync:20_state.js:135 tGold:20_state.js:136 boardOwnerName:20_state.js:137 empTimers:20_state.js:141 empEconomy:20_state.js:142 empPO:20_state.js:147 immuneStrainIn:20_state.js:155 siegeStrains:20_state.js:159 effStrained:20_state.js:160 empArmies:20_state.js:161 endRow:20_state.js:167 boardEndTurn:20_state.js:170 tickRealm:20_state.js:173 expireBlocks:20_state.js:176 empirePhase:20_state.js:178 tickTimers:20_state.js:201 facTypeBonus:20_state.js:210 pursuitUpkeep:20_state.js:213 withBoard:20_state.js:216 setOnline:20_state.js:232 clone:20_state.js:242 jeq:20_state.js:243 isObj:20_state.js:244 merge3:20_state.js:246 splitD:20_state.js:255 joinD:20_state.js:261 save:20_state.js:287 saveIfDirty:20_state.js:294 editing:20_state.js:329 cvar:20_state.js:349 fmt:20_state.js:350 cap:20_state.js:351 settUnbuilt:20_state.js:355 unbuiltMeta:20_state.js:356 settMeta:20_state.js:357 pinSettCell:20_state.js:358 settExpand:20_state.js:359 settFinish:20_state.js:360 settTier:20_state.js:363 occupants:20_state.js:364 hamletOK:20_state.js:365 hamletRoot:20_state.js:368 hamletFits:20_state.js:369 effList:20_state.js:376 effLabel:20_state.js:381 exemptionsOf:20_state.js:382 wardExemptions:20_state.js:391 isFreeRider:20_state.js:392 wardUse:20_state.js:393 canPlace:20_state.js:404 capitalSett:20_state.js:423 setCapital:20_state.js:424 isCityPlus:20_state.js:426 dbActive:20_state.js:427 capBonus:20_state.js:431 eraCapBase:20_state.js:432 eraCap:20_state.js:433 capSrc:20_state.js:434 cityCount:20_state.js:435 eraAllows:20_state.js:437 rslug:20_state.js:445 boardFlags:20_state.js:446 onBoard:20_state.js:479 scopeOf:20_state.js:481 realmHolder:20_state.js:482 scopeBlock:20_state.js:483 nextTier:20_state.js:488 autoFill:20_state.js:490 buildFilters:30_empire.js:8 monChip:30_empire.js:10 catSave:30_empire.js:16 pAvail:30_empire.js:21 legalCtx:30_empire.js:25 rawRes:30_empire.js:27 rawInSett:30_empire.js:28 rawOK:30_empire.js:32 pLegal:30_empire.js:33 pReqMiss:30_empire.js:38 autoHamlet:30_empire.js:41 autoOK:30_empire.js:42 effSpot:30_empire.js:44 smartSid:30_empire.js:50 iAvail:30_empire.js:57 catUpkeep:30_empire.js:58 seg:30_empire.js:59 renderList:30_empire.js:61 wardPick:30_empire.js:116 wpRender:30_empire.js:118 wpPlace:30_empire.js:141 settLbl:30_empire.js:146 reqRow:30_empire.js:148 pursuitRow:30_empire.js:150 sub:30_empire.js:161 tip:30_empire.js:163 itemRow:30_empire.js:164 flash:30_empire.js:174 addInfraByName:30_empire.js:176 placeHolding:30_empire.js:182 addItem:30_empire.js:203 removeInstance:30_empire.js:214 addPursuitByName:30_empire.js:215 moveInstance:30_empire.js:216 infraReqToks:30_empire.js:232 infraTokStatus:30_empire.js:238 infraReqStatus:30_empire.js:252 infraValid:30_empire.js:257 infraActive:30_empire.js:264 infraReqLinesHTML:30_empire.js:265 masteryInfraToks:30_empire.js:269 masteryInfraHTML:30_empire.js:270 annotReqTok:30_empire.js:277 optionMet:30_empire.js:282 reqStatus:30_empire.js:290 instStatus:30_empire.js:297 chainLine:30_empire.js:304 simpleReq:30_empire.js:313 simpleReqHTML:30_empire.js:325 computeEarned:30_empire.js:333 atomEl:30_empire.js:351 atomsBlock:30_empire.js:360 render:30_empire.js:373 renderTopBar:30_empire.js:430 toggleEmpty:30_empire.js:477 sfxNorm:30_empire.js:486 sfxLabel:30_empire.js:487 settFx:30_empire.js:496 settFxPanel:30_empire.js:519 renderPursuitBoard:30_empire.js:526 wardPiles:30_empire.js:635 wardGrid:30_empire.js:647 unitFor:30_empire.js:674 tryMove:30_empire.js:679 scrollHost:30_empire.js:712 dropTargetAt:30_empire.js:713 clearDropHL:30_empire.js:721 armDrag:30_empire.js:722 beginDrag:30_empire.js:739 dragMove:30_empire.js:753 dragEnd:30_empire.js:765 herPicker:30_empire.js:774 factionFree:30_empire.js:785 setFaction:30_empire.js:789 facGearFlags:30_empire.js:798 factionFlags:30_empire.js:804 cultureFactions:30_empire.js:819 facOffered:30_empire.js:823 facPicker:30_empire.js:825 culSelectHTML:30_empire.js:842 cultureOf:30_empire.js:846 holdDom:30_empire.js:847 cultureSet:30_empire.js:851 cultureKeep:30_empire.js:856 cultureKeepWonder:30_empire.js:857 derivedCulture:30_empire.js:859 nameCulture:30_empire.js:861 usedSettNames:30_empire.js:863 genPlaceName:30_empire.js:864 nameSett:30_empire.js:870 nameAllSetts:30_empire.js:872 renderFaction:30_empire.js:873 timerCtl:30_empire.js:881 placementSelect:30_empire.js:886 contribAcc:30_empire.js:901 contribChips:30_empire.js:904 accChips:30_empire.js:905 pursuitDetail:30_empire.js:913 quickChip:30_empire.js:937 buildsIntoRow:30_empire.js:941 nextLinksHTML:30_empire.js:943 pursuitTable:30_empire.js:951 pursuitCard:30_empire.js:978 renderInfraSection:30_empire.js:1066 armyUnlocks:30_empire.js:1111 unlockedShieldTiers:30_empire.js:1143 tierOK:30_empire.js:1147 gloss:30_empire.js:1148 glossLookup:30_empire.js:1157 openModal:30_empire.js:1166 closeModal:30_empire.js:1170 kwChipHTML:30_empire.js:1171 esc:30_empire.js:1172 inspectKeyword:30_empire.js:1173 inspectItem:30_empire.js:1195 optionList:30_empire.js:1218 loadoutFields:30_empire.js:1234 renderArmy:30_empire.js:1248 armyCard:30_empire.js:1281 reqMet:30_empire.js:1375 weaponUnlockMet:30_empire.js:1378 moraleBase:30_empire.js:1380 armyUpkeep:30_empire.js:1381 moraleCap:30_empire.js:1383 effMorale:30_empire.js:1385 isRouted:30_empire.js:1386 armyVals:30_empire.js:1389 armyStats:30_empire.js:1397 noUpkeepTiers:30_empire.js:1424 holdsActive:30_empire.js:1426 playersWithout:30_empire.js:1428 calcMetrics:30_empire.js:1430 computeTotals:30_empire.js:1484 poTaxMod:30_empire.js:1515 taxDouble:30_empire.js:1520 winterTax:30_empire.js:1521 occupyTaxOnly:30_empire.js:1530 settInside:30_empire.js:1531 settTax:30_empire.js:1532 tradeIncome:30_empire.js:1535 tradeRaw:30_empire.js:1544 goldBreak:30_empire.js:1558 treasLive:30_empire.js:1572 fmtK:30_empire.js:1574 renderGlog:30_empire.js:1576 goldBreakHTML:30_empire.js:1583 goldBreakTxt:30_empire.js:1587 seasonNet:30_empire.js:1588 husbandryGoldFor:30_empire.js:1592 SEASON_DBL_TIER:30_empire.js:1596 tierGoldFor:30_empire.js:1598 seasonDblGold:30_empire.js:1602 SEASON_DBL_TYPE:30_empire.js:1603 boardMetrics:30_empire.js:1604 poBandName:30_empire.js:1611 poActiveKeys:30_empire.js:1613 poActiveEffects:30_empire.js:1615 poImmune:30_empire.js:1622 poDoubled:30_empire.js:1623 renderPO:30_empire.js:1625 curSeason:40_realm_data.js:4 stepSeason:40_realm_data.js:5 playerOfBoard:40_realm_data.js:8 igVal:40_realm_data.js:9 eraIdx:40_realm_data.js:10 playerAtWar:40_realm_data.js:11 influenceRowsBase:40_realm_data.js:12 influenceRows:40_realm_data.js:43 influenceTotal:40_realm_data.js:48 poModRows:40_realm_data.js:51 totTipSimple:40_realm_data.js:78 totTip:40_realm_data.js:81 epSources:40_realm_data.js:92 topSuz:40_realm_data.js:104 royalMarriage:40_realm_data.js:107 sameAlliance:40_realm_data.js:112 poFloor:40_realm_data.js:115 applyPOFloor:40_realm_data.js:116 epRows:40_realm_data.js:117 poModTotal:40_realm_data.js:130 dpButtons:40_realm_data.js:131 renderDP:40_realm_data.js:134 renderMiniStand:40_realm_data.js:142 renderInfluence:40_realm_data.js:156 renderPOMods:40_realm_data.js:160 siegeState:40_realm_data.js:172 siegeCalc:40_realm_data.js:173 siegeHTML:40_realm_data.js:190 realmTimers:40_realm_data.js:205 timerAddHTML:40_realm_data.js:206 boardTimerRows:40_realm_data.js:210 siegeResolveHTML:40_realm_data.js:216 activeTimersHTML:40_realm_data.js:222 seasonsHTML:40_realm_data.js:228 costsHTML:40_realm_data.js:231 wireDashExtras:40_realm_data.js:234 renderDash:40_realm_data.js:262 domBand:40_realm_data.js:265 mods:40_realm_data.js:268 diplo:40_realm_data.js:273 pk:40_realm_data.js:274 isVassal:40_realm_data.js:276 vassalsOf:40_realm_data.js:277 effPair:40_realm_data.js:278 pairOf:40_realm_data.js:281 pname:40_realm_data.js:282 allianceLabel:40_realm_data.js:283 pboard:40_realm_data.js:284 hasRoad:40_realm_data.js:285 eraRank:40_realm_data.js:288 allianceEra:40_realm_data.js:289 allianceOK:40_realm_data.js:290 pairFlags:40_realm_data.js:291 dStatus:40_realm_data.js:299 diploHTML:40_realm_data.js:303 wireDiplo:40_realm_data.js:359 newSide:50_battle.js:4 battle:50_battle.js:5 bq:50_battle.js:7 bqAdd:50_battle.js:8 bqSideName:50_battle.js:9 bqLoad:50_battle.js:12 sideHex:50_battle.js:15 bqStart:50_battle.js:19 banditArmy:50_battle.js:22 armBandits:50_battle.js:26 sideArmy:50_battle.js:31 blog:50_battle.js:36 d10:50_battle.js:37 seizeForced:50_battle.js:38 facCombat:50_battle.js:41 sideUnlocks:50_battle.js:53 sideDomains:50_battle.js:57 standingFxOf:50_battle.js:58 hasTiltyard:50_battle.js:62 eqOptions:50_battle.js:63 eqCode:50_battle.js:72 eqNow:50_battle.js:75 eqWeapon:50_battle.js:78 tacAllowed:50_battle.js:86 tacOK:50_battle.js:91 randomTacticPool:50_battle.js:92 sideCalc:50_battle.js:95 pickKey:50_battle.js:205 viewerSide:50_battle.js:206 mdLite:50_battle.js:228 fmtModLong:50_battle.js:230 fmtMod:50_battle.js:233 dieRow:50_battle.js:235 rollHTML:50_battle.js:236 battleSprites:50_battle.js:245 sideHTML:50_battle.js:249 tacEdge:50_battle.js:338 tacticExplainHTML:50_battle.js:344 battleRulesHTML:50_battle.js:358 renderBattle:50_battle.js:362 incoming:50_battle.js:388 roll:50_battle.js:391 ripN:50_battle.js:447 addRip:50_battle.js:448 setPendCas:50_battle.js:449 pendCas:50_battle.js:450 applyCas:50_battle.js:451 endSkirmish:50_battle.js:452 endBattle:50_battle.js:468 wireBattle:50_battle.js:485 edictTimerLen:50_battle.js:533 edictChoices:50_battle.js:535 edictTotal:50_battle.js:541 edictOwners:50_battle.js:542 bumpRenown:50_battle.js:543 edictBoardHTML:50_battle.js:544 wireEdicts:50_battle.js:572 currentEra:50_battle.js:586 pMark:50_battle.js:594 domTrackHTML:50_battle.js:596 standingEffectsHTML:50_battle.js:605 renderRenown:50_battle.js:618 mapClimate:60_map.js:17 mapPal:60_map.js:22 tLum:60_map.js:25 tTone:60_map.js:27 tLighten:60_map.js:28 tGlyph:60_map.js:31 tSwatch:60_map.js:36 mapState:60_map.js:43 hexDist:60_map.js:44 decodeGrid:60_map.js:47 seedCode:60_map.js:57 generateMap:60_map.js:58 parseSeedCode:60_map.js:66 mapZoom:60_map.js:78 reachBonus:60_map.js:84 reachOwners:60_map.js:93 reachResources:60_map.js:105 settReachHexes:60_map.js:115 rawClaims:60_map.js:126 mapSprId:60_map.js:148 mapSprDefs:60_map.js:149 tMix:60_map.js:158 hStr:60_map.js:163 rng32:60_map.js:164 mapScatter:60_map.js:165 propPaths:60_map.js:184 pxSwatch:60_map.js:188 mapSpr:60_map.js:193 eqSVG:60_map.js:199 sprSVG:60_map.js:201 stIcon:60_map.js:209 armyGear:60_map.js:210 armyUFor:60_map.js:212 stDedup:60_map.js:217 stIconSVG:60_map.js:219 plateStatus:60_map.js:221 plateBox:60_map.js:222 mapPlate:60_map.js:224 settPlate:60_map.js:235 settBehind:60_map.js:246 settInsideMarks:60_map.js:250 mapBarHTML:60_map.js:265 terrOwners:60_map.js:276 terrFlags:60_map.js:278 unrestCamps:60_map.js:284 intrudersOf:60_map.js:286 settReach:60_map.js:290 settEcon:60_map.js:292 pillageCheck:60_map.js:301 pillageTargets:60_map.js:305 runPillage:60_map.js:308 armyStatus:60_map.js:315 mapMarkers:60_map.js:328 inspHTML:60_map.js:339 inspHead:60_map.js:342 inspCell:60_map.js:345 g:60_map.js:346 inspCan:60_map.js:347 inspArmy:60_map.js:348 settStatus:60_map.js:368 settStatusMarks:60_map.js:378 inspSett:60_map.js:382 envoyFor:60_map.js:413 settActionsHTML:60_map.js:416 armyMusterBtn:60_map.js:427 inspCamp:60_map.js:438 engageTargets:60_map.js:450 wireInsp:60_map.js:456 mapLayers:60_map.js:480 mapSVG:60_map.js:577 outlawReport:60_map.js:579 banditDomain:60_map.js:590 banditAutoHTML:60_map.js:591 armyName:60_map.js:600 syncMapTiers:60_map.js:602 mapLinkBad:60_map.js:608 mapLinksHTML:60_map.js:609 wireBanditAuto:60_map.js:620 banditAuto:60_map.js:626 BST:60_map.js:627 bLog:60_map.js:628 hk:60_map.js:630 mapSetts:60_map.js:631 cellPlayer:60_map.js:632 cellSett:60_map.js:634 mapArmies:60_map.js:637 cellArmy:60_map.js:638 cellTitle:60_map.js:641 byDist:60_map.js:645 isWild:60_map.js:649 wildZones:60_map.js:650 outlawZones:60_map.js:652 zoneOf:60_map.js:657 zoneOwners:60_map.js:658 outlawOwners:60_map.js:663 outlawOwner:60_map.js:665 outlawOf:60_map.js:667 campWild:60_map.js:669 wildCount:60_map.js:671 wildDone:60_map.js:672 placeWildOutlaw:60_map.js:678 rescatterWild:60_map.js:700 pieceAura:60_map.js:703 campInRange:60_map.js:707 hexFree:60_map.js:710 spawnCamp:60_map.js:711 growCamps:60_map.js:713 expandOutlaw:60_map.js:717 immuneUprising:60_map.js:720 banditTargetMods:60_map.js:721 cunningAction:60_map.js:723 endorsedExtort:60_map.js:724 banditAct:60_map.js:725 runBanditMechanics:60_map.js:754 banditSpeed:60_map.js:773 banditAuraList:60_map.js:775 banditRun:60_map.js:782 moveCamp:60_map.js:790 banditSiegeTimer:60_map.js:791 banditMoves:60_map.js:793 banditSkims:60_map.js:822 creditSkims:60_map.js:827 envoyOutcome:60_map.js:833 banditCunningHTML:60_map.js:838 dieLookup:60_map.js:855 terrainTablesHTML:60_map.js:858 mapToolsHTML:60_map.js:881 banditPanelHTML:60_map.js:915 mapAsP:60_map.js:931 mapEditBlock:60_map.js:932 mapGuard:60_map.js:941 guarded:60_map.js:943 mapCellClick:60_map.js:945 wireMap:60_map.js:961 srcKeys:70_rules.js:6 srcMatch:70_rules.js:13 srcHas:70_rules.js:14 srcRows:70_rules.js:16 bordersOf:70_rules.js:20 poCap:70_rules.js:24 poTextFloor:70_rules.js:25 siegeTextMods:70_rules.js:28 siegeWinterOK:70_rules.js:35 actRestrict:70_rules.js:37 actRiders:70_rules.js:47 settById:70_rules.js:58 besiegeExempt:70_rules.js:60 settBesieged:70_rules.js:61 armySieging:70_rules.js:63 armyBesieged:70_rules.js:65 armyStateTags:70_rules.js:66 armyBlocked:70_rules.js:75 garrisonSizes:70_rules.js:78 hasGarrisons:70_rules.js:81 garrisonGear:70_rules.js:83 garrisonOf:70_rules.js:84 garrisonsOf:70_rules.js:88 garrisonCard:70_rules.js:89 onceEffects:70_rules.js:108 onceState:70_rules.js:109 onceWindowNow:70_rules.js:113 onceHTML:70_rules.js:114 onceUse:70_rules.js:125 noteAdd:70_rules.js:134 recoupNote:70_rules.js:136 extortGold:70_rules.js:145 danegeldRows:70_rules.js:154 loans:70_rules.js:160 loanTerms:70_rules.js:161 loanInterest:70_rules.js:164 runLoans:70_rules.js:165 loansHTML:70_rules.js:171 autoExtortRows:70_rules.js:189 extortSlots:70_rules.js:198 exTargets:70_rules.js:201 extortTargetsHTML:70_rules.js:202 runAutoExtort:70_rules.js:205 firstDoubtRed:70_rules.js:226 fdState:70_rules.js:230 gainDoubt:70_rules.js:233 siegeOn:70_rules.js:238 besiegedCount:70_rules.js:239 pById:70_rules.js:240 nextId:70_rules.js:241 captureTransfer:70_rules.js:242 sackApply:70_rules.js:253 resolveRealm:70_rules.js:264 sackLocks:70_rules.js:269 armyHex:70_rules.js:273 settHex:70_rules.js:274 musterLimit:70_rules.js:275 musterTick:70_rules.js:281 hasMusterField:70_rules.js:289 charterFlags:70_rules.js:292 selArmy:70_rules.js:315 canMoveArmy:70_rules.js:316 canEnterSett:70_rules.js:318 armyInside:70_rules.js:320 enterCheck:70_rules.js:323 freeHexNear:70_rules.js:325 kickOut:70_rules.js:328 armiesInside:70_rules.js:331 terrPen:70_rules.js:333 terrBlocked:70_rules.js:334 terrWaterStop:70_rules.js:335 terrStrain:70_rules.js:336 provinceOf:70_rules.js:338 moveTraits:70_rules.js:340 speedOf:70_rules.js:343 hexNb:70_rules.js:375 auraSources:70_rules.js:379 moveRange:70_rules.js:388 moveInfo:70_rules.js:420 moveStops:70_rules.js:423 moveEndTriggers:70_rules.js:428 moveArmyTo:70_rules.js:437 moveOverlay:70_rules.js:453 movePanelHTML:70_rules.js:466 set:70_rules.js:477 computeAll:70_rules.js:478 sceneInfra:80_scene_shell.js:14 wardChains:80_scene_shell.js:20 sceneLots:80_scene_shell.js:27 renderEsBar:80_scene_shell.js:40 sceneArmies:80_scene_shell.js:48 renderScene:80_scene_shell.js:55 renderSettlements:80_scene_shell.js:166 lockTarget:80_scene_shell.js:229 lockBlock:80_scene_shell.js:238 adminUI:80_scene_shell.js:251 firstHostOpen:80_scene_shell.js:267 firstHostBtn:80_scene_shell.js:268 hudSign:80_scene_shell.js:274 hudData:80_scene_shell.js:275 hudTips:80_scene_shell.js:284 renderHUD:80_scene_shell.js:297 ageStripHTML:80_scene_shell.js:317 setupOn:80_scene_shell.js:331 renderSetup:80_scene_shell.js:332 renderTurnStrip:80_scene_shell.js:360 syncBoardEndBtn:80_scene_shell.js:392 mnavSync:80_scene_shell.js:408 herName:80_scene_shell.js:418 herKey:80_scene_shell.js:419 lumOf:80_scene_shell.js:420 herMix:80_scene_shell.js:424 herN:80_scene_shell.js:426 herPaths:80_scene_shell.js:427 heraldOf:80_scene_shell.js:432 mapBanner:80_scene_shell.js:435 pTok:80_scene_shell.js:438 inboxItems:85_ux.js:10 renderInbox:85_ux.js:23 evIn:85_ux.js:41 hudPopBack:85_ux.js:55 hudPopFill:85_ux.js:57 hudPop:85_ux.js:83 hudPopClose:85_ux.js:84 renderChrome:85_ux.js:90 undoSnap:90_app.js:5 undoRecord:90_app.js:7 undoRebase:90_app.js:13 undoScoped:90_app.js:14 undoApply:90_app.js:15 doUndo:90_app.js:28 doRedo:90_app.js:29 undoButtons:90_app.js:30 actSnap:90_app.js:43 actRebase:90_app.js:44 actJoin:90_app.js:46 actSchedule:90_app.js:49 fmtG:90_app.js:50 boardDiff:90_app.js:51 actFlush:90_app.js:83 gameAllowed:90_app.js:100 gameData:90_app.js:101 refreshGames:90_app.js:102 gameReplace:90_app.js:105 newGameState:90_app.js:109 isReady:90_app.js:132 readyCheck:90_app.js:133 gslug:90_app.js:146 kwify:90_app.js:158 wikiA:90_app.js:169 gkHtml:90_app.js:170 openFromHash:90_app.js:187 setLift:90_app.js:213 gkShow:90_app.js:222 gkHide:90_app.js:226 gkFor:90_app.js:227 chatHdr:90_app.js:286 chatTargets:90_app.js:292 chatParse:90_app.js:294 chatColor:90_app.js:302 chatLine:90_app.js:303 chatRender:90_app.js:307 chatSys:90_app.js:313 chatComplete:90_app.js:328
```
