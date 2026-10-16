# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-10-16 · data VERSION `0.4.9.9.13-d10-SIMPLE` · HEAD `2e43639 2026-10-16`

Hand-written orientation: `CLAUDE.md` (same folder). Paths below are relative to the repo root.

## 1. Folder tree

```
./  (11 files)
  0.4.8 Updated Docs/  (7 files)
  0.4.8.1/  (36 files)
  Assets/  (102 files, generated/assets — not indexed)
  CE/  (43 files)
    Combatv4/  (18 files)
      shims/  (6 files)
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
| `CE\ENVOY_WINDOW_REVIEW.md` | 102 | Envoy timing windows — review list |
| `CE\MAPGEN_COVERAGE.md` | 28 | Map generator — Holding / Monument coverage by region preset |
| `CE\PROPOSALS_new_things.md` | 275 | Proposals — "New things to consider" + rules syntax pass |
| `CE\REPO_MAP.md` | 866 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE\RULES_push.md` | 649 | Renown |
| `CE\RULES_push_simple.md` | 730 | Renown |
| `CE\RULES_reorganized_6.md` | 638 | Renown |
| `CE\SIMPLE_NODES.PY` | 1 |  |
| `CE\SYNTAX_SWEEP.md` | 343 | Rules syntax sweep — canon applied |
| `CE\TASK2_NOTES.md` | 82 | claude_task_2 — what changed, open questions |
| `CE\TASK3_NOTES.md` | 43 | claude_task_3 — what changed, open questions |
| `CE\TASK4_NOTES.md` | 139 | claude_task_4 — what changed, open questions |
| `CE\TASK5_NOTES.md` | 74 | claude_task_5 — what changed, open items |
| `CE\build_all_CE.bat` | 506 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE\ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\claude_task.txt` | 85 |  |
| `CE\claude_task_2.txt` | 68 |  |
| `CE\claude_task_3.txt` | 24 |  |
| `CE\claude_task_4.txt` | 44 |  |
| `CE\claude_task_5.txt` | 23 |  |
| `CE\claude_task_6.txt` | 51 |  |
| `CE\infra.py` | 109 |  |
| `CE\parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE\patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE\rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE\renown_data.py` | 4621 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d10.py` | 4621 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d8.py` | 2801 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_server.bat` | 16 | renown_server.bat - (re)start the Renown board server in WSL. |
| `CE\repo_map.py` | 250 | repo_map.py — write REPO_MAP.md next to this file (CE/, beside CLAUDE.md): a generated index of the Renown repo for |
| `CE\run_tournament_d10.bat` | 108 | Renown d10 tournament runner  —  CE build |
| `CE\run_tournament_d10.py` | 131 | run_tournament_d10.py — run the Renown tournament against the d10 build. |
| `CE\sprites.py` | 2696 | sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene). |
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
| `CE\ask-the-bot\equipment_table.csv` | 38 | columns: Item,Type,Tier,AP_or_Save,Init,Keywords |
| `CE\ask-the-bot\factions_table.csv` | 43 | columns: Faction,Difficulty,Strength,Mechanic |
| `CE\ask-the-bot\renown_faq.txt` | 499 |  |
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
| `CE\references\effect_registry.py` | 306 | effect_registry.py -- every rules-text pattern the settlement board acts on, matched once at build time. |
| `CE\references\equipment_sheet.py` | 691 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `CE\references\faction_sheet.py` | 447 | Renown — Faction card sheet generator. |
| `CE\references\faq_export.py` | 440 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `CE\references\gen_compendium.py` | 184 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `CE\references\gen_layout.py` | 374 | gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data. |
| `CE\references\gen_layout_roots.py` | 123 | gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it. |
| `CE\references\gen_settlement_board.py` | 1048 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE\references\generate_cards.py` | 93 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `CE\references\host_sheet.py` | 452 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `CE\references\infra_board.py` | 134 | infra_board.py - landscape Infrastructure Board. |
| `CE\references\layout.json` | 1421 |  |
| `CE\references\layout_roots.json` | 1344 |  |
| `CE\references\layout_simple.json` | 1517 |  |
| `CE\references\md_to_docx.py` | 329 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `CE\references\package-lock.json` | 205 |  |
| `CE\references\package.json` | 6 |  |
| `CE\references\parity_efx.js` | 54 | parity_efx.js — replays effect_registry.py's patterns with JavaScript RegExp, the way the board used to read text at |
| `CE\references\patch_pursuit_domains.py` | 58 | patch_pursuit_domains.py |
| `CE\references\playstyle_reference.py` | 396 | playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture). |
| `CE\references\pursuit_tiles.py` | 282 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `CE\references\reference_sheets.py` | 811 | Renown — Reference sheet generators. |
| `CE\references\render_tree.py` | 272 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `CE\references\server.py` | 501 | Renown settlement-board server  —  stdlib only, no pip installs. |
| `CE\references\settlement_board.html` | — | generated HTML (1371 KB) |
| `CE\references\settlement_mats.py` | 296 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `CE\references\spec_tree_sheet.py` | 1183 | Renown — Specialization Tree renderer. |
| `CE\references\svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `CE\references\sync_derived.py` | 116 | sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES. |
| `CE\references\tactic_sheet.py` | 446 | Renown — Tactic card sheet generator (v3). |
| `CE\references\wiki_markers.py` | 290 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
| `CE\references\world.txt` | 1517 |  |
| `CE\references\worldtxt.py` | 328 | worldtxt.py — parse the hand-maintained world.txt lore book into structured |
| `CE\references\board\body.html` | 207 |  |
| `CE\references\board\js\00_core.js` | 48 | __DATA__*/; |
| `CE\references\board\js\10_table.js` | 734 | ===================== TABLE: seating, Council & Envoy phases ===================== |
| `CE\references\board\js\15_realm.js` | 349 | ===================== REALM: the play surface ===================== |
| `CE\references\board\js\20_state.js` | 488 | ---- state: multiplayer dashboard ---- |
| `CE\references\board\js\30_empire.js` | 1507 | ---- catalog ---- |
| `CE\references\board\js\40_realm_data.js` | 383 | ---- Dashboards view ---- |
| `CE\references\board\js\50_battle.js` | 621 | ---- Battle ---- |
| `CE\references\board\js\60_map.js` | 981 | ---- Map view ---- |
| `CE\references\board\js\70_rules.js` | 475 | ===================== EFFECT PLUMBING: the effect registry (references/effect_registry.py) ===================== |
| `CE\references\board\js\80_scene_shell.js` | 415 | ---- pixel scene: every settlement of the active player, drawn from sprites.py (every theme) ---- |
| `CE\references\board\js\85_ux.js` | 96 | ===================== CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper ===================== |
| `CE\references\board\js\90_app.js` | 362 | ===================== UNDO / REDO ===================== |
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
| `RenownWiki\factions.html` | 19 | Factions — Renown |
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
| `RenownWiki\rules-factions.html` | 20 | Factions — Renown |
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
| `RenownWiki\rules-the-turn.html` | 107 | The Turn — Renown |
| `RenownWiki\rules-trade-income.html` | 36 | Trade &amp; Income — Renown |
| `RenownWiki\rules-treasury-upkeep.html` | 32 | Treasury &amp; Upkeep — Renown |
| `RenownWiki\search.js` | 7 |  |
| `RenownWiki\seasons-ref.html` | 19 | Seasons — Renown |
| `RenownWiki\settlement_board.html` | — | generated HTML (1371 KB) |
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
| `FACTION_SUMMARIES` | 608 | dict | 41 |
| `NODES` | 659 | dict | 120 |
| `SIMPLE_NODES` | 1693 | dict | 120 |
| `HOLDING_GROUPS` | 2562 | dict | 9 |
| `SCOPES` | 2579 | tuple | 3 |
| `SCOPE_BY_TYPE` | 2580 | dict | 2 |
| `LINE_LABELS` | 2584 | dict | 28 |
| `lines_of` | 2615 | function |  |
| `LEGACY_NODES` | 2619 | dict | 108 |
| `REQ_KEY` | 2624 | str | 'infrastructure_req' |
| `REQ_LABEL` | 2625 | str | 'Infrastructure Req' |
| `TYPE_ORDER` | 2627 | list | 10 |
| `CHAIN_TERM` | 2630 | str | 'Mastery Chain' |
| `PURSUIT_TERM` | 2632 | tuple | 2 |
| `node_parents` | 2634 | function |  |
| `get_data` | 2654 | function |  |
| `FACTIONS` | 2664 | dict | 41 |
| `INFRASTRUCTURE` | 3083 | dict | 20 |
| `WONDERS` | 3218 | dict | 4 |
| `INFRA_TIERS` | 3219 | list | 5 |
| `SETTLEMENTS` | 3227 | dict | 5 |
| `ERAS` | 3236 | dict | 4 |
| `PO_BANDS` | 3251 | dict | 12 |
| `po_scale` | 3270 | function |  |
| `po_value` | 3277 | function |  |
| `po_effect` | 3282 | function |  |
| `PUBLIC_ORDER` | 3289 | dict | 12 |
| `PUBLIC_ORDER_BY_ERA` | 3290 | dict | 4 |
| `PO_MODIFIERS` | 3296 | dict | 2 |
| `DOMAIN_BOARD` | 3314 | dict | 6 |
| `SEASONS` | 3345 | dict | 4 |
| `TRADE_RULES` | 3353 | dict | 4 |
| `efficient_graph` | 3365 | function |  |
| `EFFICIENT_MULTI` | 3375 | dict | 111 |
| `EFFICIENT` | 3376 | dict | 111 |
| `BANDIT_CAMP_START` | 3384 | int | 10 |
| `BANDIT_CAMP_GOLD` | 3385 | int | 2000 |
| `BANDIT_ARMY_THRESHOLD` | 3386 | int | 25 |
| `BANDIT_GROWTH_PER_ERA` | 3387 | dict | 4 |
| `BANDIT_EQUIPMENT_PER_ERA` | 3388 | dict | 4 |
| `BANDITS` | 3389 | dict | 5 |
| `TIMERS` | 3397 | dict | 8 |
| `CHARTER_MIN_RANGE` | 3409 | int | 4 |
| `OUTLAW_BUFFER_RANGE` | 3410 | int | 2 |
| `HAMLET_RANGE` | 3411 | int | 2 |
| `OUTLAW_COUNTRY_START` | 3412 | int | 3 |
| `WILD_OUTLAW` | 3420 | dict | 9 |
| `wild_outlaw_count` | 3433 | function |  |
| `BANDIT_CAMP_REACH` | 3440 | str | 'province' |
| `VASSAL_EXCHANGE_CAP` | 3443 | int | 5000 |
| `VASSAL_INFLUENCE_TAKE` | 3444 | int | 3 |
| `BUILD_TIMERS` | 3448 | dict | 11 |
| `TERRAIN` | 3462 | dict | 7 |
| `MOVEMENT_MODIFIERS` | 3472 | dict | 6 |
| `TACTICAL_TERRAIN` | 3484 | dict | 7 |
| `TACTICAL_GLOBAL` | 3500 | list | 1 |
| `INFLUENCE_GAIN` | 3502 | dict | 9 |
| `ENVOY_OUTCOME_THRESHOLDS` | 3556 | dict | 4 |
| `ENVOY_OUTCOMES` | 3565 | dict | 5 |
| `ACTIONS` | 3587 | dict | 22 |
| `TREATIES` | 3777 | dict | 5 |
| `ALLIANCE_RULES` | 3785 | list | 3 |
| `EDICT_STREAK_TURNS` | 3795 | int | 5 |
| `EDICTS` | 3797 | dict | 7 |
| `BANDIT_BEHAVIOR` | 3811 | dict | 8 |
| `PURSUIT_UPKEEP_DEFAULT` | 3834 | int | 100 |
| `PURSUIT_UPKEEP_BY_TYPE` | 3835 | dict | 4 |
| `UPKEEP_TRACKS` | 3845 | dict | 3 |
| `HOLDING_TIER_COST` | 3852 | dict | 4 |
| `holding_standing` | 3860 | function |  |
| `holding_cost` | 3866 | function |  |
| `holding_build_time` | 3874 | function |  |
| `pursuit_upkeep` | 3881 | function |  |
| `ARMY_UPKEEP_NOTE` | 3892 | str | "Net Army Upkeep = the sum of each Army' |
| `COSTS` | 3896 | dict | 12 |
| `PHASES` | 3916 | tuple | 5 |
| `STARTING_TURN_PHASE_OPENER` | 3917 | str | 'Council' |
| `STANDING_ARMY_SIEGE_MODIFIER` | 3919 | int | 1 |
| `EMPIRE_START_TIERS` | 3921 | tuple | 2 |
| `STARTING_TREASURY` | 3922 | int | 10000 |
| `AGES` | 3928 | dict | 5 |
| `AGE_YEAR_SEASON` | 3935 | str | 'Spring' |
| `CAPITAL_EDGE_RANGE` | 3936 | int | 4 |
| `BOARD_SIZES` | 3938 | dict | 3 |
| `SIEGE_CALCULUS` | 3944 | dict | 2 |
| `SIEGE_SOURCE_VALUES` | 3959 | dict | 6 |
| `NAME_DISPLAY` | 3986 | dict | 64 |
| `TIER_DISPLAY` | 4014 | dict | 1 |
| `ITEM_TIER_DISPLAY` | 4020 | dict | 1 |
| `TERM_ENVOY_SCORE` | 4027 | str | 'Authority' |
| `display_score` | 4037 | function |  |
| `ALIASES` | 4047 | dict | 66 |
| `display` | 4057 | function |  |
| `display_tier` | 4062 | function |  |
| `display_text` | 4072 | function |  |
| `display_list` | 4095 | function |  |
| `display_md` | 4105 | function |  |
| `display_html` | 4112 | function |  |
| `display_obj` | 4124 | function |  |
| `undisplay` | 4137 | function |  |
| `verify_aliases` | 4146 | function |  |
| `BANDIT_FACES` | 4170 | int | 10 |
| `BANDIT_CUNNING_MIN` | 4171 | int | 10 |
| `die_table_ranges` | 4174 | function |  |
| `die_table_rows` | 4182 | function |  |
| `die_table_text` | 4190 | function |  |
| `die_table_lookup` | 4198 | function |  |
| `die_table_verify` | 4205 | function |  |
| `die_table_weights` | 4224 | function |  |
| `BANDIT_CUNNING_TABLE` | 4234 | dict | 5 |
| `bandit_cunning_ranges` | 4242 | function |  |
| `bandit_cunning_rows` | 4243 | function |  |
| `bandit_cunning_lookup` | 4244 | function |  |
| `bandit_cunning_text` | 4246 | function |  |
| `BANDIT_TACTIC_TABLE` | 4252 | dict | 6 |
| `BANDIT_TACTICS` | 4260 | list | 6 |
| `bandit_tactic_ranges` | 4262 | function |  |
| `bandit_tactic_rows` | 4263 | function |  |
| `bandit_tactic_lookup` | 4264 | function |  |
| `verify_bandit_tables` | 4267 | function |  |
| `RENOWN_MAX` | 4363 | int | 30 |
| `RENOWN_PER_TURN` | 4364 | int | 1 |
| `DOMAIN_POINTS_PER_TURN` | 4365 | int | 1 |
| `FACTION_NAMES` | 4587 | dict | 41 |
| `faction_body` | 4594 | function |  |
| `GLOSSARY_CATEGORIES` | 4603 | list | 17 |

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
| 161 | ### Council Phase |
| 173 | ### Envoy Phase |
| 184 | ### Battle Phase |
| 188 | ### Rest Phase |
| 202 | # Seasons |
| 208 | # Setup |
| 210 | ## Table Setup |
| 215 | ## Setup Order |
| 224 | ### Ages |
| 230 | ## Player Setup |
| 237 | # Actions & Voting |
| 239 | ## Action Mechanics |
| 241 | ### Sending an Envoy |
| 245 | ### Resolving an Envoy |
| 277 | ## Influence |
| 285 | ## Prowess Actions |
| 289 | ## Cunning Actions |
| 293 | ## Piety Actions |
| 297 | ## Industry Actions |
| 301 | ### Rule: Ulterior Motive |
| 305 | ## Diplomacy Actions |
| 311 | ### Rule: Diplomatic Mission |
| 317 | # Domains & Standings |
| 319 | ### Domain Standings |
| 329 | ### Standing & Influence |
| 342 | # Diplomacy & Treaties |
| 344 | ### Treaties & Alliances |
| 352 | ### Vassalization |
| 374 | # Empire Building |
| 376 | ## Settlements |
| 382 | ### Settlement Wards |
| 386 | ### Chartering Settlements |
| 390 | ### Settlement Reach |
| 394 | ### Hamlets |
| 400 | ## Infrastructure |
| 420 | ## Territory & Terrain |
| 436 | # Economy |
| 438 | ## Public Order |
| 448 | ### Innate Public Order Modifiers |
| 452 | ## Treasury & Upkeep |
| 462 | ### Insolvency & Bankruptcy |
| 475 | ## Trade & Income |
| 477 | ### Who Can Trade & Income |
| 492 | ### Income Types |
| 500 | # Armies |
| 502 | ### Armies Overview |
| 512 | ### Mustering |
| 522 | ### Blocked Armies |
| 528 | # Battles & Sieges |
| 530 | ## Battle Phase |
| 532 | ### Begin Battle |
| 534 | ### Begin Skirmish |
| 542 | ### How a Battle Resolves |
| 546 | ### Begin the Battle — Seize the Initiative |
| 550 | ### The Skirmish Steps |
| 574 | ### Resolve Battle |
| 582 | ### End Battle |
| 584 | ### Tactic Matrix |
| 598 | ## Siege Warfare |
| 604 | ### Siege Timer |
| 610 | ### Beginning a Siege |
| 620 | ### Resolving a Siege |
| 633 | # Bandits |
| 635 | ### Outlaw Country |
| 644 | ### Spawning Bandit Camps |
| 650 | ### Growing Bandit Camps |
| 654 | ### Bandit Armaments by Era |
| 658 | ### Bandit Growth by Era |
| 662 | ### Bandit Info |
| 682 | ### Bandit Army Behavior |
| 694 | ### Attacking a Bandit Camp |
| 700 | # Holdings |
| 704 | # Equipment |
| 706 | ## Melee Weapons |
| 710 | ## Ranged Weapons |
| 714 | ## Shields |
| 718 | ## Armor |
| 724 | # Factions |
| 728 | # Index |

## 6. Settlement board — `CE\references\gen_settlement_board.py` + `CE\references\board\js/*.js` (+ `board.css`, `body.html`)

Payload keys passed to the HTML as `DATA` (65): `records`, `naturalNames`, `externalTokens`, `simple`, `chainTerm`, `pursuitTerm`, `infra`, `wonders`, `armySrc`, `equip`, `glossary`, `domainBoard`, `publicOrder`, `domainBoardFx`, `poByEra`, `wikiBase`, `wikiHome`, `tree`, `rulebook`, `limits`, `eras`, `edicts`, `envoyOutcomes`, `outcomeThresh`, `startPhase`, `actions`, `phaseRules`, `phaseSteps`, `rulesConst`, `ages`, `domains`, `standings`, `tradePerCraft`, `noTradeSeason`, `renownPerTurn`, `dpPerTurn`, `settlements`, `battle`, `terrainRef`, `banditLoadouts`, `bandits`, `treaties`, `allianceRules`, `startTiers`, `startTreasury`, `pursuitUpkeep`, `buildTimers`, `infraTiers`, `timers`, `seasons`, `poModifiers`, `vassalInfluenceTake`, `aliases`, `scoreTerm`, `costs`, `influenceGain`, `siege`, `factions`, `cultures`, `cultureSelf`, `placeNames`, `warnings`, `version`, `sprites`, `efx`

Python: `load`:27, `strip_md`:34, `has_cond`:76, `to_int`:79, `classify`:82, `_iv`:149, `envoy_fx`:150, `combine_parts`:250, `combine_effects`:291, `rules_payload`:295, `tree_payload`:353, `parse_effects`:387, `parse_mreq`:393, `classify_req_token`:401, `build`:410, `font_faces`:554, `_pursuit_term_template`:579, `render_html`:587, `_style_js`:595, `place_names_payload`:606, `sprite_payload`:626, `find_mapgen`:648, `_board_template`:663, `check_rules`:676, `_val`:794, `rules_section`:803, `phase_steps`:822, `battle_data`:836, `bandit_loadouts`:857, `effects_report`:905, `main`:935

JS sections: TABLE: seating, Council & Envoy phases :10_table.js:1, Action automation: Perform picker + resolution :10_table.js:242, REALM: the play surface :15_realm.js:1,  :40_realm_data.js:261, Inspect tool :60_map.js:257, EFFECT PLUMBING: the effect registry (references/effect_registry.py) :70_rules.js:1, ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS :70_rules.js:53, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :70_rules.js:137, CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper :85_ux.js:1, UNDO / REDO :90_app.js:1, ACTIVITY LOG :90_app.js:39, GAME: save · load · new :90_app.js:98, HOVER KEYWORDS :90_app.js:144

JS functions (794, name:file:line):

```
fixBastard:00_core.js:8 dispScore:00_core.js:15 POB:00_core.js:34 poNum:00_core.js:35 efxOf:00_core.js:46 hitOf:00_core.js:47 tnow:10_table.js:12 noteServerDate:10_table.js:13 lockOn:10_table.js:21 claimOf:10_table.js:22 mine:10_table.js:23 myClaimP:10_table.js:24 canEdit:10_table.js:25 boardEndOn:10_table.js:27 TB:10_table.js:28 seatFloor:10_table.js:30 tSeats:10_table.js:31 tTimer:10_table.js:32 tTurn:10_table.js:33 tPhase:10_table.js:34 PT:10_table.js:36 tCur:10_table.js:37 tCurW:10_table.js:38 sameP:10_table.js:39 meP:10_table.js:40 canAct:10_table.js:41 seatMap:10_table.js:44 seated:10_table.js:48 isSpring:10_table.js:49 hostP:10_table.js:50 voteOrd:10_table.js:52 tOrder:10_table.js:53 canHost:10_table.js:54 seatsLocked:10_table.js:55 tStand:10_table.js:58 eraRec:10_table.js:59 diploInf:10_table.js:60 diploCap:10_table.js:61 eraActions:10_table.js:62 boardFx:10_table.js:65 fxOf:10_table.js:78 scopeOk:10_table.js:79 sgn:10_table.js:80 fxLabel:10_table.js:81 atWarPair:10_table.js:96 opposeBlock:10_table.js:97 domAsFx:10_table.js:104 innateParts:10_table.js:105 modSum:10_table.js:111 innateInf:10_table.js:113 voteCap:10_table.js:114 inflPool:10_table.js:117 personalEnvoys:10_table.js:118 councilEnvoys:10_table.js:119 tOutcome:10_table.js:120 outText:10_table.js:122 tPlan:10_table.js:125 missionWhy:10_table.js:141 domStarted:10_table.js:144 tSim:10_table.js:147 performEval:10_table.js:213 comboEval:10_table.js:219 failPassFx:10_table.js:228 actionsOf:10_table.js:229 actReqFlag:10_table.js:231 actInfoHTML:10_table.js:235 actCost:10_table.js:246 domCost:10_table.js:248 addFaith:10_table.js:249 alliedP:10_table.js:250 allyGroup:10_table.js:251 topPair:10_table.js:252 actDoubt:10_table.js:255 musterOpts:10_table.js:310 runMuster:10_table.js:315 buildOpts:10_table.js:327 runBuild:10_table.js:331 improveOpts:10_table.js:335 runImprove:10_table.js:341 runCharter:10_table.js:347 repairOpts:10_table.js:352 runRepair:10_table.js:355 settName:10_table.js:359 warOn:10_table.js:360 grandVizier:10_table.js:364 pfSpec:10_table.js:367 pfTargets:10_table.js:369 pfSubs:10_table.js:379 pfSubLabel:10_table.js:380 evTxt:10_table.js:382 insteadFx:10_table.js:387 actDom:10_table.js:388 pfActs:10_table.js:389 pfInsteadSrc:10_table.js:390 pfForm:10_table.js:391 boardCounts:10_table.js:424 pendingOf:10_table.js:426 apLines:10_table.js:428 resolveEnvoy:10_table.js:431 autoRes:10_table.js:468 tApply:10_table.js:469 tSetPhase:10_table.js:479 grantDP:10_table.js:481 dpOwed:10_table.js:482 tEndTurn:10_table.js:483 setSeats:10_table.js:503 tAutoSeat:10_table.js:508 tSig:10_table.js:514 tName:10_table.js:517 tVoteTxt:10_table.js:518 envBadges:10_table.js:519 innateTxt:10_table.js:525 tOutCls:10_table.js:527 tPerformHtml:10_table.js:528 summaryLines:10_table.js:549 chronOn:10_table.js:566 chron:10_table.js:567 chronSnap:10_table.js:570 chronTick:10_table.js:577 chronDate:10_table.js:587 empireChecklistHTML:10_table.js:588 treeSave:10_table.js:598 mapRaws:10_table.js:608 refRawAvail:10_table.js:611 treeHTML:10_table.js:615 rulebookHTML:10_table.js:682 linkifyRules:10_table.js:685 renderReference:10_table.js:689 tCountdown:10_table.js:702 applyTheme:10_table.js:717 applySkin:10_table.js:729 doFire:15_realm.js:8 patch:15_realm.js:12 rlCommit:15_realm.js:13 pOf:15_realm.js:14 rlOpen:15_realm.js:20 rlToggle:15_realm.js:21 renderTable:15_realm.js:26 renderRealmMap:15_realm.js:46 domCells:15_realm.js:58 realmTableHTML:15_realm.js:61 spectating:15_realm.js:100 miniCardHTML:15_realm.js:112 phaseCardHTML:15_realm.js:122 dockCard:15_realm.js:171 dockHTML:15_realm.js:172 envoyQueueHTML:15_realm.js:235 inflCardHTML:15_realm.js:254 drawersHTML:15_realm.js:305 turnLogItems:15_realm.js:317 turnLogHTML:15_realm.js:337 realmTimersBrief:15_realm.js:346 startDoms:20_state.js:2 ageRec:20_state.js:5 ageRisingOf:20_state.js:6 startDomsFor:20_state.js:7 startDomTotal:20_state.js:8 curYear:20_state.js:9 applyAgeStart:20_state.js:10 startSettlements:20_state.js:12 startSig:20_state.js:15 reseedIfPristine:20_state.js:17 newBoard:20_state.js:22 newPlayer:20_state.js:24 normalizeD:20_state.js:39 activeBoard:20_state.js:59 reindex:20_state.js:60 pActive:20_state.js:73 ignHas:20_state.js:77 flagState:20_state.js:78 ignBtn:20_state.js:83 ignNote:20_state.js:86 unlockStatus:20_state.js:92 nameHit:20_state.js:103 missTxt:20_state.js:104 recomputePC:20_state.js:106 buildTimerMod:20_state.js:111 withBuildMod:20_state.js:115 pursuitBaseTime:20_state.js:116 infraBaseTime:20_state.js:117 pursuitBuildTime:20_state.js:118 infraBuildTime:20_state.js:119 buildNote:20_state.js:120 settBaseTime:20_state.js:121 settBuildTime:20_state.js:122 itm:20_state.js:123 infraOn:20_state.js:124 gameStarted:20_state.js:125 empTimers:20_state.js:129 empEconomy:20_state.js:130 empPO:20_state.js:134 immuneStrainIn:20_state.js:142 siegeStrains:20_state.js:146 effStrained:20_state.js:147 empArmies:20_state.js:148 endRow:20_state.js:154 boardEndTurn:20_state.js:157 tickRealm:20_state.js:160 expireBlocks:20_state.js:163 empirePhase:20_state.js:165 tickTimers:20_state.js:188 facTypeBonus:20_state.js:196 pursuitUpkeep:20_state.js:198 withBoard:20_state.js:201 setOnline:20_state.js:217 clone:20_state.js:227 jeq:20_state.js:228 isObj:20_state.js:229 merge3:20_state.js:231 splitD:20_state.js:240 joinD:20_state.js:246 save:20_state.js:272 saveIfDirty:20_state.js:278 editing:20_state.js:313 cvar:20_state.js:333 fmt:20_state.js:334 cap:20_state.js:335 settUnbuilt:20_state.js:339 unbuiltMeta:20_state.js:340 settMeta:20_state.js:341 pinSettCell:20_state.js:342 settExpand:20_state.js:343 settFinish:20_state.js:344 settTier:20_state.js:347 occupants:20_state.js:348 hamletOK:20_state.js:349 hamletRoot:20_state.js:352 hamletFits:20_state.js:353 effList:20_state.js:360 effLabel:20_state.js:365 exemptionsOf:20_state.js:366 wardExemptions:20_state.js:375 isFreeRider:20_state.js:376 wardUse:20_state.js:377 canPlace:20_state.js:388 capitalSett:20_state.js:407 setCapital:20_state.js:408 isCityPlus:20_state.js:410 dbActive:20_state.js:411 capBonus:20_state.js:415 eraCapBase:20_state.js:416 eraCap:20_state.js:417 capSrc:20_state.js:418 cityCount:20_state.js:419 eraAllows:20_state.js:421 rslug:20_state.js:429 boardFlags:20_state.js:430 onBoard:20_state.js:463 scopeOf:20_state.js:465 realmHolder:20_state.js:466 scopeBlock:20_state.js:467 nextTier:20_state.js:472 autoFill:20_state.js:474 buildFilters:30_empire.js:8 catSave:30_empire.js:18 pAvail:30_empire.js:23 iAvail:30_empire.js:24 catUpkeep:30_empire.js:25 seg:30_empire.js:26 renderList:30_empire.js:28 wardPick:30_empire.js:78 wpRender:30_empire.js:80 wpPlace:30_empire.js:98 pursuitRow:30_empire.js:102 sub:30_empire.js:113 tip:30_empire.js:115 itemRow:30_empire.js:116 flash:30_empire.js:126 addInfraByName:30_empire.js:128 placeHolding:30_empire.js:134 addItem:30_empire.js:155 removeInstance:30_empire.js:165 addPursuitByName:30_empire.js:166 moveInstance:30_empire.js:167 infraReqToks:30_empire.js:183 infraTokStatus:30_empire.js:189 infraReqStatus:30_empire.js:203 infraValid:30_empire.js:208 infraActive:30_empire.js:215 infraReqLinesHTML:30_empire.js:216 masteryInfraToks:30_empire.js:220 masteryInfraHTML:30_empire.js:221 annotReqTok:30_empire.js:228 optionMet:30_empire.js:233 reqStatus:30_empire.js:241 instStatus:30_empire.js:248 chainLine:30_empire.js:255 simpleReq:30_empire.js:264 simpleReqHTML:30_empire.js:276 computeEarned:30_empire.js:284 atomEl:30_empire.js:302 atomsBlock:30_empire.js:311 render:30_empire.js:324 renderTopBar:30_empire.js:378 toggleEmpty:30_empire.js:425 sfxNorm:30_empire.js:434 sfxLabel:30_empire.js:435 settFx:30_empire.js:444 settFxPanel:30_empire.js:467 renderPursuitBoard:30_empire.js:474 wardPiles:30_empire.js:583 wardGrid:30_empire.js:595 unitFor:30_empire.js:622 tryMove:30_empire.js:627 scrollHost:30_empire.js:660 dropTargetAt:30_empire.js:661 clearDropHL:30_empire.js:669 armDrag:30_empire.js:670 beginDrag:30_empire.js:687 dragMove:30_empire.js:701 dragEnd:30_empire.js:713 factionFree:30_empire.js:723 setFaction:30_empire.js:727 facGearFlags:30_empire.js:736 factionFlags:30_empire.js:742 facSelectHTML:30_empire.js:753 culSelectHTML:30_empire.js:759 cultureOf:30_empire.js:763 holdDom:30_empire.js:764 cultureSet:30_empire.js:768 cultureKeep:30_empire.js:773 cultureKeepWonder:30_empire.js:774 derivedCulture:30_empire.js:776 nameCulture:30_empire.js:778 usedSettNames:30_empire.js:779 genPlaceName:30_empire.js:780 nameSett:30_empire.js:786 renderFaction:30_empire.js:787 timerCtl:30_empire.js:794 placementSelect:30_empire.js:799 contribAcc:30_empire.js:814 contribChips:30_empire.js:817 accChips:30_empire.js:818 pursuitDetail:30_empire.js:826 quickChip:30_empire.js:850 buildsIntoRow:30_empire.js:854 nextLinksHTML:30_empire.js:856 pursuitTable:30_empire.js:864 pursuitCard:30_empire.js:891 renderInfraSection:30_empire.js:979 armyUnlocks:30_empire.js:1024 unlockedShieldTiers:30_empire.js:1056 tierOK:30_empire.js:1060 gloss:30_empire.js:1061 glossLookup:30_empire.js:1070 openModal:30_empire.js:1079 closeModal:30_empire.js:1083 kwChipHTML:30_empire.js:1084 esc:30_empire.js:1085 inspectKeyword:30_empire.js:1086 inspectItem:30_empire.js:1108 optionList:30_empire.js:1131 loadoutFields:30_empire.js:1147 renderArmy:30_empire.js:1161 armyCard:30_empire.js:1194 reqMet:30_empire.js:1288 weaponUnlockMet:30_empire.js:1291 moraleBase:30_empire.js:1293 armyUpkeep:30_empire.js:1294 moraleCap:30_empire.js:1296 effMorale:30_empire.js:1298 isRouted:30_empire.js:1299 armyVals:30_empire.js:1302 armyStats:30_empire.js:1310 noUpkeepTiers:30_empire.js:1337 holdsActive:30_empire.js:1339 playersWithout:30_empire.js:1341 calcMetrics:30_empire.js:1343 computeTotals:30_empire.js:1397 poTaxMod:30_empire.js:1425 taxDouble:30_empire.js:1430 winterTax:30_empire.js:1431 occupyTaxOnly:30_empire.js:1440 settInside:30_empire.js:1441 settTax:30_empire.js:1442 tradeIncome:30_empire.js:1445 tradeRaw:30_empire.js:1454 seasonNet:30_empire.js:1462 husbandryGoldFor:30_empire.js:1466 SEASON_DBL_TYPE:30_empire.js:1468 boardMetrics:30_empire.js:1469 poBandName:30_empire.js:1476 poActiveKeys:30_empire.js:1478 poActiveEffects:30_empire.js:1480 poImmune:30_empire.js:1487 poDoubled:30_empire.js:1488 renderPO:30_empire.js:1490 curSeason:40_realm_data.js:4 stepSeason:40_realm_data.js:5 playerOfBoard:40_realm_data.js:8 igVal:40_realm_data.js:9 eraIdx:40_realm_data.js:10 playerAtWar:40_realm_data.js:11 influenceRowsBase:40_realm_data.js:12 influenceRows:40_realm_data.js:43 influenceTotal:40_realm_data.js:48 poModRows:40_realm_data.js:51 totTipSimple:40_realm_data.js:78 totTip:40_realm_data.js:81 epSources:40_realm_data.js:92 topSuz:40_realm_data.js:104 royalMarriage:40_realm_data.js:107 sameAlliance:40_realm_data.js:112 poFloor:40_realm_data.js:115 applyPOFloor:40_realm_data.js:116 epRows:40_realm_data.js:117 poModTotal:40_realm_data.js:130 dpButtons:40_realm_data.js:131 renderDP:40_realm_data.js:134 renderMiniStand:40_realm_data.js:142 renderInfluence:40_realm_data.js:156 renderPOMods:40_realm_data.js:159 siegeState:40_realm_data.js:167 siegeCalc:40_realm_data.js:168 siegeHTML:40_realm_data.js:185 realmTimers:40_realm_data.js:200 timerAddHTML:40_realm_data.js:201 boardTimerRows:40_realm_data.js:205 siegeResolveHTML:40_realm_data.js:211 activeTimersHTML:40_realm_data.js:217 seasonsHTML:40_realm_data.js:223 costsHTML:40_realm_data.js:226 wireDashExtras:40_realm_data.js:229 renderDash:40_realm_data.js:257 domBand:40_realm_data.js:260 mods:40_realm_data.js:263 diplo:40_realm_data.js:268 pk:40_realm_data.js:269 isVassal:40_realm_data.js:271 vassalsOf:40_realm_data.js:272 effPair:40_realm_data.js:273 pairOf:40_realm_data.js:276 pname:40_realm_data.js:277 allianceLabel:40_realm_data.js:278 pboard:40_realm_data.js:279 hasRoad:40_realm_data.js:280 eraRank:40_realm_data.js:283 allianceEra:40_realm_data.js:284 allianceOK:40_realm_data.js:285 pairFlags:40_realm_data.js:286 dStatus:40_realm_data.js:294 diploHTML:40_realm_data.js:298 wireDiplo:40_realm_data.js:354 newSide:50_battle.js:4 battle:50_battle.js:5 bq:50_battle.js:7 bqAdd:50_battle.js:8 bqSideName:50_battle.js:9 bqLoad:50_battle.js:12 sideHex:50_battle.js:15 bqStart:50_battle.js:19 banditArmy:50_battle.js:22 armBandits:50_battle.js:26 sideArmy:50_battle.js:31 blog:50_battle.js:36 d10:50_battle.js:37 seizeForced:50_battle.js:38 facCombat:50_battle.js:41 sideUnlocks:50_battle.js:53 sideDomains:50_battle.js:57 standingFxOf:50_battle.js:58 hasTiltyard:50_battle.js:62 eqOptions:50_battle.js:63 eqCode:50_battle.js:72 eqNow:50_battle.js:75 eqWeapon:50_battle.js:78 tacAllowed:50_battle.js:86 tacOK:50_battle.js:91 randomTacticPool:50_battle.js:92 sideCalc:50_battle.js:95 pickKey:50_battle.js:205 viewerSide:50_battle.js:206 mdLite:50_battle.js:228 fmtModLong:50_battle.js:230 fmtMod:50_battle.js:233 dieRow:50_battle.js:235 rollHTML:50_battle.js:236 battleSprites:50_battle.js:245 sideHTML:50_battle.js:249 tacEdge:50_battle.js:338 tacticExplainHTML:50_battle.js:344 battleRulesHTML:50_battle.js:358 renderBattle:50_battle.js:365 incoming:50_battle.js:391 roll:50_battle.js:394 ripN:50_battle.js:450 addRip:50_battle.js:451 setPendCas:50_battle.js:452 pendCas:50_battle.js:453 applyCas:50_battle.js:454 endSkirmish:50_battle.js:455 endBattle:50_battle.js:471 wireBattle:50_battle.js:488 edictTimerLen:50_battle.js:536 edictChoices:50_battle.js:538 edictTotal:50_battle.js:544 edictOwners:50_battle.js:545 bumpRenown:50_battle.js:546 edictBoardHTML:50_battle.js:547 wireEdicts:50_battle.js:575 currentEra:50_battle.js:589 pMark:50_battle.js:597 domTrackHTML:50_battle.js:599 standingEffectsHTML:50_battle.js:605 renderRenown:50_battle.js:616 mapClimate:60_map.js:17 mapPal:60_map.js:22 tLum:60_map.js:25 tTone:60_map.js:27 tLighten:60_map.js:28 tGlyph:60_map.js:31 tSwatch:60_map.js:36 mapState:60_map.js:43 hexDist:60_map.js:44 decodeGrid:60_map.js:47 seedCode:60_map.js:57 generateMap:60_map.js:58 parseSeedCode:60_map.js:66 mapZoom:60_map.js:78 reachBonus:60_map.js:84 reachOwners:60_map.js:93 reachResources:60_map.js:105 settReachHexes:60_map.js:115 rawClaims:60_map.js:126 mapSprId:60_map.js:148 mapSprDefs:60_map.js:149 tMix:60_map.js:158 hStr:60_map.js:163 rng32:60_map.js:164 mapScatter:60_map.js:165 mapSpr:60_map.js:182 eqSVG:60_map.js:188 sprSVG:60_map.js:190 stIcon:60_map.js:198 armyGear:60_map.js:199 armyUFor:60_map.js:201 plateStatus:60_map.js:204 plateBox:60_map.js:206 mapPlate:60_map.js:208 settPlate:60_map.js:219 settBehind:60_map.js:230 settInsideMarks:60_map.js:234 mapBarHTML:60_map.js:249 terrOwners:60_map.js:260 terrFlags:60_map.js:262 unrestCamps:60_map.js:268 intrudersOf:60_map.js:270 settReach:60_map.js:274 settEcon:60_map.js:276 pillageCheck:60_map.js:285 pillageTargets:60_map.js:289 runPillage:60_map.js:292 armyStatus:60_map.js:299 mapMarkers:60_map.js:312 inspHTML:60_map.js:323 inspHead:60_map.js:326 inspCell:60_map.js:329 g:60_map.js:330 inspCan:60_map.js:331 inspArmy:60_map.js:332 settStatus:60_map.js:352 settStatusMarks:60_map.js:362 inspSett:60_map.js:367 envoyFor:60_map.js:398 settActionsHTML:60_map.js:401 armyMusterBtn:60_map.js:412 inspCamp:60_map.js:423 engageTargets:60_map.js:435 wireInsp:60_map.js:441 mapLayers:60_map.js:465 mapSVG:60_map.js:562 outlawReport:60_map.js:564 banditDomain:60_map.js:575 banditAutoHTML:60_map.js:576 armyName:60_map.js:585 syncMapTiers:60_map.js:587 mapLinkBad:60_map.js:593 mapLinksHTML:60_map.js:594 wireBanditAuto:60_map.js:605 banditAuto:60_map.js:611 BST:60_map.js:612 bLog:60_map.js:613 hk:60_map.js:615 mapSetts:60_map.js:616 cellPlayer:60_map.js:617 cellSett:60_map.js:619 mapArmies:60_map.js:622 cellArmy:60_map.js:623 cellTitle:60_map.js:626 byDist:60_map.js:630 isWild:60_map.js:634 wildZones:60_map.js:635 outlawZones:60_map.js:637 zoneOf:60_map.js:642 zoneOwners:60_map.js:643 outlawOwners:60_map.js:648 outlawOwner:60_map.js:650 outlawOf:60_map.js:652 campWild:60_map.js:654 wildCount:60_map.js:656 wildDone:60_map.js:657 placeWildOutlaw:60_map.js:662 rescatterWild:60_map.js:683 pieceAura:60_map.js:686 campInRange:60_map.js:690 hexFree:60_map.js:693 spawnCamp:60_map.js:694 growCamps:60_map.js:696 expandOutlaw:60_map.js:700 immuneUprising:60_map.js:703 banditTargetMods:60_map.js:704 cunningAction:60_map.js:706 endorsedExtort:60_map.js:707 banditAct:60_map.js:708 runBanditMechanics:60_map.js:737 banditSpeed:60_map.js:756 banditAuraList:60_map.js:758 banditRun:60_map.js:765 moveCamp:60_map.js:773 banditSiegeTimer:60_map.js:774 banditMoves:60_map.js:776 banditSkims:60_map.js:805 creditSkims:60_map.js:810 envoyOutcome:60_map.js:816 banditCunningHTML:60_map.js:821 dieLookup:60_map.js:838 terrainTablesHTML:60_map.js:841 mapToolsHTML:60_map.js:862 banditPanelHTML:60_map.js:896 mapAsP:60_map.js:912 mapEditBlock:60_map.js:913 mapGuard:60_map.js:923 guarded:60_map.js:925 mapCellClick:60_map.js:927 wireMap:60_map.js:942 srcKeys:70_rules.js:6 srcMatch:70_rules.js:13 srcHas:70_rules.js:14 srcRows:70_rules.js:16 bordersOf:70_rules.js:20 poCap:70_rules.js:24 poTextFloor:70_rules.js:25 siegeTextMods:70_rules.js:28 siegeWinterOK:70_rules.js:35 actRestrict:70_rules.js:37 actRiders:70_rules.js:44 settById:70_rules.js:54 besiegeExempt:70_rules.js:56 settBesieged:70_rules.js:57 armySieging:70_rules.js:59 armyBesieged:70_rules.js:61 armyStateTags:70_rules.js:62 armyBlocked:70_rules.js:71 garrisonSizes:70_rules.js:74 hasGarrisons:70_rules.js:77 garrisonGear:70_rules.js:79 garrisonOf:70_rules.js:80 garrisonsOf:70_rules.js:84 garrisonCard:70_rules.js:85 onceEffects:70_rules.js:104 onceState:70_rules.js:105 onceWindowNow:70_rules.js:109 onceHTML:70_rules.js:110 onceUse:70_rules.js:121 noteAdd:70_rules.js:130 recoupNote:70_rules.js:132 extortGold:70_rules.js:141 danegeldRows:70_rules.js:149 loans:70_rules.js:155 loanTerms:70_rules.js:156 loanInterest:70_rules.js:159 runLoans:70_rules.js:160 loansHTML:70_rules.js:166 autoExtortRows:70_rules.js:184 extortSlots:70_rules.js:193 exTargets:70_rules.js:196 extortTargetsHTML:70_rules.js:197 runAutoExtort:70_rules.js:200 firstDoubtRed:70_rules.js:221 fdState:70_rules.js:225 gainDoubt:70_rules.js:228 siegeOn:70_rules.js:233 besiegedCount:70_rules.js:234 pById:70_rules.js:235 nextId:70_rules.js:236 captureTransfer:70_rules.js:237 sackApply:70_rules.js:248 resolveRealm:70_rules.js:259 sackLocks:70_rules.js:264 armyHex:70_rules.js:268 settHex:70_rules.js:269 musterLimit:70_rules.js:270 musterTick:70_rules.js:276 hasMusterField:70_rules.js:284 charterFlags:70_rules.js:287 selArmy:70_rules.js:310 canMoveArmy:70_rules.js:311 canEnterSett:70_rules.js:313 armyInside:70_rules.js:315 enterCheck:70_rules.js:318 freeHexNear:70_rules.js:320 kickOut:70_rules.js:323 armiesInside:70_rules.js:326 terrPen:70_rules.js:328 terrBlocked:70_rules.js:329 terrWaterStop:70_rules.js:330 terrStrain:70_rules.js:331 provinceOf:70_rules.js:333 moveTraits:70_rules.js:335 speedOf:70_rules.js:338 hexNb:70_rules.js:371 auraSources:70_rules.js:375 moveRange:70_rules.js:384 moveInfo:70_rules.js:415 moveStops:70_rules.js:418 moveEndTriggers:70_rules.js:423 moveArmyTo:70_rules.js:432 moveOverlay:70_rules.js:448 movePanelHTML:70_rules.js:461 set:70_rules.js:472 computeAll:70_rules.js:473 sceneInfra:80_scene_shell.js:14 wardChains:80_scene_shell.js:20 sceneLots:80_scene_shell.js:27 renderEsBar:80_scene_shell.js:40 sceneArmies:80_scene_shell.js:48 renderScene:80_scene_shell.js:55 renderSettlements:80_scene_shell.js:166 lockTarget:80_scene_shell.js:229 lockBlock:80_scene_shell.js:238 adminUI:80_scene_shell.js:251 firstHostOpen:80_scene_shell.js:267 firstHostBtn:80_scene_shell.js:268 hudSign:80_scene_shell.js:274 hudData:80_scene_shell.js:275 renderHUD:80_scene_shell.js:283 ageStripHTML:80_scene_shell.js:303 setupOn:80_scene_shell.js:317 renderSetup:80_scene_shell.js:318 renderTurnStrip:80_scene_shell.js:346 syncBoardEndBtn:80_scene_shell.js:378 mnavSync:80_scene_shell.js:394 herKey:80_scene_shell.js:402 lumOf:80_scene_shell.js:403 herPaths:80_scene_shell.js:406 heraldOf:80_scene_shell.js:410 mapBanner:80_scene_shell.js:413 inboxItems:85_ux.js:10 renderInbox:85_ux.js:23 evIn:85_ux.js:41 hudPopBack:85_ux.js:55 hudPopFill:85_ux.js:57 hudPop:85_ux.js:82 hudPopClose:85_ux.js:83 renderChrome:85_ux.js:89 undoSnap:90_app.js:5 undoRecord:90_app.js:7 undoRebase:90_app.js:13 undoScoped:90_app.js:14 undoApply:90_app.js:15 doUndo:90_app.js:28 doRedo:90_app.js:29 undoButtons:90_app.js:30 actSnap:90_app.js:43 actRebase:90_app.js:44 actJoin:90_app.js:46 actSchedule:90_app.js:49 fmtG:90_app.js:50 boardDiff:90_app.js:51 actFlush:90_app.js:83 gameAllowed:90_app.js:100 gameData:90_app.js:101 refreshGames:90_app.js:102 gameReplace:90_app.js:105 newGameState:90_app.js:109 isReady:90_app.js:132 readyCheck:90_app.js:133 gslug:90_app.js:146 kwify:90_app.js:158 wikiA:90_app.js:169 gkHtml:90_app.js:170 openFromHash:90_app.js:187 setLift:90_app.js:213 gkShow:90_app.js:222 gkHide:90_app.js:226 gkFor:90_app.js:227 chatHdr:90_app.js:285 chatTargets:90_app.js:291 chatParse:90_app.js:293 chatColor:90_app.js:301 chatLine:90_app.js:302 chatRender:90_app.js:306 chatSys:90_app.js:312 chatComplete:90_app.js:327
```
