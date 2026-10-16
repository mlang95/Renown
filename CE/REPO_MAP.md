# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-10-16 · data VERSION `0.4.9.9.13-d10-SIMPLE` · HEAD `fc286ed 2026-10-16`

Hand-written orientation: `CLAUDE.md` (same folder). Paths below are relative to the repo root.

## 1. Folder tree

```
./  (11 files)
  0.4.8 Updated Docs/  (7 files)
  0.4.8.1/  (36 files)
  Assets/  (102 files, generated/assets — not indexed)
  CE/  (40 files)
    Combatv4/  (18 files)
      shims/  (6 files)
    ask-the-bot/  (3 files)
    lab_out/  (465 files, generated/assets — not indexed)
    mapgen/  (17 files)
      maps/  (20 files)
    references/  (49 files)
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
| `CE\CLAUDE.md` | 64 | CLAUDE.md — Renown repo orientation (lives in `CE/`; paths below are relative to `CE/`) |
| `CE\COMPREHENSIVE_RULES_OUTLINE.md` | 181 | Renown — Comprehensive Rules: outline |
| `CE\MAPGEN_COVERAGE.md` | 28 | Map generator — Holding / Monument coverage by region preset |
| `CE\PROPOSALS_new_things.md` | 275 | Proposals — "New things to consider" + rules syntax pass |
| `CE\REPO_MAP.md` | 845 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE\RULES_push.md` | 649 | Renown |
| `CE\RULES_push_simple.md` | 730 | Renown |
| `CE\RULES_reorganized_6.md` | 638 | Renown |
| `CE\SIMPLE_NODES.PY` | 1 |  |
| `CE\SYNTAX_SWEEP.md` | 343 | Rules syntax sweep — canon applied |
| `CE\TASK2_NOTES.md` | 82 | claude_task_2 — what changed, open questions |
| `CE\TASK3_NOTES.md` | 43 | claude_task_3 — what changed, open questions |
| `CE\TASK4_NOTES.md` | 139 | claude_task_4 — what changed, open questions |
| `CE\build_all_CE.bat` | 506 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE\ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\claude_task.txt` | 85 |  |
| `CE\claude_task_2.txt` | 68 |  |
| `CE\claude_task_3.txt` | 24 |  |
| `CE\claude_task_4.txt` | 44 |  |
| `CE\claude_task_5.txt` | 23 |  |
| `CE\infra.py` | 109 |  |
| `CE\parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE\patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE\rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE\renown_data.py` | 4621 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d10.py` | 4621 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d8.py` | 2801 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_server.bat` | 16 | renown_server.bat - (re)start the Renown board server in WSL. |
| `CE\repo_map.py` | 242 | repo_map.py — write REPO_MAP.md next to this file (CE/, beside CLAUDE.md): a generated index of the Renown repo for |
| `CE\run_tournament_d10.bat` | 108 | Renown d10 tournament runner  —  CE build |
| `CE\run_tournament_d10.py` | 131 | run_tournament_d10.py — run the Renown tournament against the d10 build. |
| `CE\sprites.py` | 2639 | sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene). |
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
| `CE\references\equipment_sheet.py` | 691 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `CE\references\faction_sheet.py` | 447 | Renown — Faction card sheet generator. |
| `CE\references\faq_export.py` | 440 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `CE\references\gen_compendium.py` | 184 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `CE\references\gen_layout.py` | 374 | gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data. |
| `CE\references\gen_layout_roots.py` | 123 | gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it. |
| `CE\references\gen_settlement_board.py` | 8063 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE\references\generate_cards.py` | 93 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `CE\references\host_sheet.py` | 452 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `CE\references\infra_board.py` | 134 | infra_board.py - landscape Infrastructure Board. |
| `CE\references\layout.json` | 1421 |  |
| `CE\references\layout_roots.json` | 1344 |  |
| `CE\references\layout_simple.json` | 1517 |  |
| `CE\references\md_to_docx.py` | 329 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `CE\references\package-lock.json` | 205 |  |
| `CE\references\package.json` | 6 |  |
| `CE\references\patch_pursuit_domains.py` | 58 | patch_pursuit_domains.py |
| `CE\references\playstyle_reference.py` | 396 | playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture). |
| `CE\references\pursuit_tiles.py` | 282 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `CE\references\reference_sheets.py` | 811 | Renown — Reference sheet generators. |
| `CE\references\render_tree.py` | 272 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `CE\references\server.py` | 501 | Renown settlement-board server  —  stdlib only, no pip installs. |
| `CE\references\settlement_board.html` | — | generated HTML (1299 KB) |
| `CE\references\settlement_mats.py` | 296 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `CE\references\spec_tree_sheet.py` | 1183 | Renown — Specialization Tree renderer. |
| `CE\references\svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `CE\references\sync_derived.py` | 116 | sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES. |
| `CE\references\tactic_sheet.py` | 446 | Renown — Tactic card sheet generator (v3). |
| `CE\references\wiki_markers.py` | 290 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
| `CE\references\world.txt` | 1517 |  |
| `CE\references\worldtxt.py` | 328 | worldtxt.py — parse the hand-maintained world.txt lore book into structured |
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
| `RenownWiki\settlement_board.html` | — | generated HTML (1299 KB) |
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

## 6. Settlement board — `CE\references\gen_settlement_board.py`

Payload keys passed to the HTML as `DATA` (64): `records`, `naturalNames`, `externalTokens`, `simple`, `chainTerm`, `pursuitTerm`, `infra`, `wonders`, `armySrc`, `equip`, `glossary`, `domainBoard`, `publicOrder`, `domainBoardFx`, `poByEra`, `wikiBase`, `wikiHome`, `tree`, `rulebook`, `limits`, `eras`, `edicts`, `envoyOutcomes`, `outcomeThresh`, `startPhase`, `actions`, `phaseRules`, `phaseSteps`, `rulesConst`, `ages`, `domains`, `standings`, `tradePerCraft`, `noTradeSeason`, `renownPerTurn`, `dpPerTurn`, `settlements`, `battle`, `terrainRef`, `banditLoadouts`, `bandits`, `treaties`, `allianceRules`, `startTiers`, `startTreasury`, `pursuitUpkeep`, `buildTimers`, `infraTiers`, `timers`, `seasons`, `poModifiers`, `vassalInfluenceTake`, `aliases`, `scoreTerm`, `costs`, `influenceGain`, `siege`, `factions`, `cultures`, `cultureSelf`, `placeNames`, `warnings`, `version`, `sprites`

Python: `load`:27, `strip_md`:34, `has_cond`:76, `to_int`:79, `classify`:82, `_iv`:149, `envoy_fx`:150, `combine_parts`:250, `combine_effects`:291, `rules_payload`:295, `tree_payload`:353, `parse_effects`:387, `parse_mreq`:393, `classify_req_token`:401, `build`:410, `font_faces`:554, `_pursuit_term_template`:579, `render_html`:587, `_style_js`:595, `place_names_payload`:606, `sprite_payload`:625, `find_mapgen`:647, `check_rules`:7732, `_val`:7850, `rules_section`:7859, `phase_steps`:7878, `battle_data`:7892, `bandit_loadouts`:7913, `main`:7961

JS sections: TABLE: seating, Council & Envoy phases :1530, Action automation: Perform picker + resolution :1764,  :4833, Inspect tool :5825, EFFECT PLUMBING: read rule text on a player's active pieces + faction :6502, ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS :6549, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :6643, UNDO / REDO :7361, ACTIVITY LOG :7399, GAME: save · load · new :7463, HOVER KEYWORDS :7509

JS functions (763, name:line):

```
fixBastard:1494 dispScore:1501 POB:1520 poNum:1521 tnow:1541 noteServerDate:1542 lockOn:1550 claimOf:1551 mine:1552 myClaimP:1553 canEdit:1554 boardEndOn:1556 TB:1557 tSeats:1558 tTimer:1559 tTurn:1560 tPhase:1561 PT:1563 tCur:1564 tCurW:1565 sameP:1566 meP:1567 canAct:1568 seatMap:1571 seated:1575 isSpring:1576 hostP:1577 voteOrd:1579 tOrder:1580 canHost:1581 seatsLocked:1582 tStand:1585 eraRec:1586 diploInf:1587 diploCap:1588 eraActions:1589 boardFx:1592 fxOf:1605 scopeOk:1606 sgn:1607 fxLabel:1608 atWarPair:1623 opposeBlock:1624 domAsFx:1631 innateParts:1632 modSum:1638 innateInf:1640 voteCap:1641 inflPool:1644 personalEnvoys:1645 councilEnvoys:1646 tOutcome:1647 outText:1649 tPlan:1652 domStarted:1666 tSim:1669 performEval:1735 comboEval:1741 failPassFx:1750 actionsOf:1751 actReqFlag:1753 actInfoHTML:1757 actCost:1768 domCost:1770 addFaith:1771 alliedP:1772 allyGroup:1773 topPair:1774 actDoubt:1777 musterOpts:1832 runMuster:1837 buildOpts:1849 runBuild:1853 improveOpts:1857 runImprove:1863 runCharter:1869 repairOpts:1874 runRepair:1877 settName:1881 warOn:1882 grandVizier:1886 pfSpec:1889 pfTargets:1891 pfSubs:1901 pfSubLabel:1902 evTxt:1904 insteadFx:1909 actDom:1910 pfActs:1911 pfInsteadSrc:1912 pfForm:1913 boardCounts:1946 pendingOf:1948 apLines:1950 resolveEnvoy:1953 autoRes:1990 tApply:1991 tSetPhase:2001 grantDP:2003 dpOwed:2004 tEndTurn:2005 setSeats:2025 tAutoSeat:2030 tSig:2036 tName:2039 tVoteTxt:2040 envBadges:2041 innateTxt:2047 tOutCls:2049 tHistHtml:2050 tPerformHtml:2062 summaryLines:2081 summaryHTML:2094 chronOn:2104 chron:2105 chronSnap:2108 chronTick:2115 chronDate:2125 chronicleHTML:2126 empireChecklistHTML:2134 treeSave:2144 mapRaws:2154 refRawAvail:2157 treeHTML:2161 rulebookHTML:2228 linkifyRules:2231 renderReference:2235 renderTable:2248 domCells:2319 realmTableHTML:2322 rlOpen:2361 rlToggle:2362 tbFit:2370 tPanel:2376 preVoteHTML:2470 tWire:2480 tCountdown:2546 applyTheme:2561 applySkin:2573 startDoms:2579 ageRec:2582 ageRisingOf:2583 startDomsFor:2584 startDomTotal:2585 curYear:2586 applyAgeStart:2587 startSettlements:2589 startSig:2592 reseedIfPristine:2594 newBoard:2599 newPlayer:2601 normalizeD:2616 activeBoard:2636 reindex:2637 pActive:2650 ignHas:2654 flagState:2655 ignBtn:2660 ignNote:2663 unlockStatus:2669 nameHit:2680 missTxt:2681 recomputePC:2683 buildTimerMod:2688 withBuildMod:2692 pursuitBaseTime:2693 infraBaseTime:2694 pursuitBuildTime:2695 infraBuildTime:2696 buildNote:2697 settBaseTime:2698 settBuildTime:2699 itm:2700 infraOn:2701 gameStarted:2702 empTimers:2706 empEconomy:2707 empPO:2711 immuneStrainIn:2719 siegeStrains:2723 effStrained:2724 empArmies:2725 endRow:2731 boardEndTurn:2734 tickRealm:2737 expireBlocks:2740 empirePhase:2742 tickTimers:2765 facTypeBonus:2773 pursuitUpkeep:2775 withBoard:2778 setOnline:2794 clone:2804 jeq:2805 isObj:2806 merge3:2808 splitD:2817 joinD:2823 save:2847 editing:2885 cvar:2905 fmt:2906 cap:2907 settUnbuilt:2911 unbuiltMeta:2912 settMeta:2913 pinSettCell:2914 settExpand:2915 settFinish:2916 settTier:2919 occupants:2920 hamletOK:2921 hamletRoot:2924 hamletFits:2925 effList:2932 effLabel:2937 exemptionsOf:2938 wardExemptions:2947 isFreeRider:2948 wardUse:2949 canPlace:2960 capitalSett:2979 setCapital:2980 isCityPlus:2982 dbActive:2983 capBonus:2987 eraCapBase:2988 eraCap:2989 capSrc:2990 cityCount:2991 eraAllows:2993 rslug:3001 boardFlags:3002 onBoard:3035 scopeOf:3037 realmHolder:3038 scopeBlock:3039 nextTier:3044 autoFill:3046 buildFilters:3067 catSave:3077 pAvail:3082 iAvail:3083 catUpkeep:3084 seg:3085 renderList:3087 wardPick:3137 wpRender:3139 wpPlace:3157 pursuitRow:3161 sub:3172 tip:3174 itemRow:3175 flash:3183 addInfraByName:3185 placeHolding:3191 addItem:3212 removeInstance:3222 addPursuitByName:3223 moveInstance:3224 infraReqToks:3240 infraTokStatus:3246 infraReqStatus:3260 infraValid:3265 infraActive:3272 infraReqLinesHTML:3273 masteryInfraToks:3277 masteryInfraHTML:3278 annotReqTok:3285 optionMet:3290 reqStatus:3298 instStatus:3305 chainLine:3312 simpleReq:3321 simpleReqHTML:3333 computeEarned:3341 atomEl:3359 atomsBlock:3368 render:3381 renderTopBar:3434 toggleEmpty:3480 sfxNorm:3489 sfxLabel:3490 settFx:3499 settFxPanel:3522 renderPursuitBoard:3529 wardPiles:3645 wardGrid:3657 unitFor:3684 tryMove:3689 scrollHost:3722 dropTargetAt:3723 clearDropHL:3731 armDrag:3732 beginDrag:3749 dragMove:3763 dragEnd:3775 factionFree:3785 setFaction:3789 facGearFlags:3798 factionFlags:3804 facSelectHTML:3815 culSelectHTML:3821 cultureOf:3825 holdDom:3826 cultureSet:3830 cultureKeep:3835 cultureKeepWonder:3836 derivedCulture:3838 nameCulture:3840 usedSettNames:3841 genPlaceName:3842 nameSett:3848 renderFaction:3849 timerCtl:3856 placementSelect:3861 contribAcc:3876 contribChips:3879 accChips:3880 pursuitDetail:3888 quickChip:3912 buildsIntoRow:3916 nextLinksHTML:3918 pursuitTable:3926 pursuitCard:3953 renderInfraSection:4041 armyUnlocks:4086 unlockedShieldTiers:4118 tierOK:4122 gloss:4123 glossLookup:4132 openModal:4141 closeModal:4145 kwChipHTML:4146 esc:4147 inspectKeyword:4148 inspectItem:4170 optionList:4193 renderArmy:4208 armyCard:4241 reqMet:4354 weaponUnlockMet:4357 moraleBase:4359 armyUpkeep:4360 moraleCap:4362 effMorale:4364 isRouted:4365 armyVals:4368 armyStats:4376 noUpkeepTiers:4403 holdsActive:4405 playersWithout:4407 calcMetrics:4409 computeTotals:4463 poTaxMod:4491 taxDouble:4496 winterTax:4497 occupyTaxOnly:4506 settInside:4507 settTax:4508 tradeIncome:4511 tradeRaw:4520 seasonNet:4528 husbandryGoldFor:4532 SEASON_DBL_TYPE:4534 boardMetrics:4535 poBandName:4542 poActiveKeys:4544 poActiveEffects:4546 poImmune:4553 poDoubled:4554 renderPO:4556 curSeason:4576 stepSeason:4577 playerOfBoard:4580 igVal:4581 eraIdx:4582 playerAtWar:4583 influenceRowsBase:4584 influenceRows:4615 influenceTotal:4620 poModRows:4623 totTipSimple:4650 totTip:4653 epSources:4664 topSuz:4676 royalMarriage:4679 sameAlliance:4684 poFloor:4687 applyPOFloor:4688 epRows:4689 poModTotal:4702 dpButtons:4703 renderDP:4706 renderMiniStand:4714 renderInfluence:4728 renderPOMods:4731 siegeState:4739 siegeCalc:4740 siegeHTML:4757 realmTimers:4772 timerAddHTML:4773 boardTimerRows:4777 siegeResolveHTML:4783 activeTimersHTML:4789 seasonsHTML:4795 costsHTML:4798 wireDashExtras:4801 renderDash:4829 domBand:4832 mods:4835 diplo:4840 pk:4841 isVassal:4843 vassalsOf:4844 effPair:4845 pairOf:4848 pname:4849 allianceLabel:4850 pboard:4851 hasRoad:4852 eraRank:4855 allianceEra:4856 allianceOK:4857 pairFlags:4858 dStatus:4866 diploHTML:4870 wireDiplo:4926 newSide:4958 battle:4959 bq:4961 bqAdd:4962 bqSideName:4963 bqLoad:4966 sideHex:4969 bqStart:4973 banditArmy:4976 armBandits:4980 sideArmy:4985 blog:4990 d10:4991 seizeForced:4992 facCombat:4995 sideUnlocks:5007 sideDomains:5011 standingFxOf:5012 hasTiltyard:5016 eqOptions:5017 eqCode:5026 eqNow:5029 eqWeapon:5032 tacAllowed:5040 tacOK:5045 randomTacticPool:5046 sideCalc:5049 pickKey:5159 viewerSide:5160 mdLite:5182 fmtModLong:5184 fmtMod:5187 dieRow:5189 rollHTML:5190 battleSprites:5199 sideHTML:5203 tacEdge:5292 tacticExplainHTML:5295 battleRulesHTML:5307 renderBattle:5314 incoming:5340 roll:5343 ripN:5399 addRip:5400 setPendCas:5401 pendCas:5402 applyCas:5403 endSkirmish:5404 endBattle:5420 wireBattle:5437 edictTimerLen:5485 edictChoices:5487 edictTotal:5493 edictOwners:5494 bumpRenown:5495 edictBoardHTML:5496 wireEdicts:5524 currentEra:5538 pMark:5546 domTrackHTML:5548 standingEffectsHTML:5554 renderRenown:5565 mapClimate:5584 mapPal:5589 tLum:5592 tTone:5594 tLighten:5595 tGlyph:5598 tSwatch:5603 mapState:5610 hexDist:5611 decodeGrid:5614 seedCode:5624 generateMap:5625 parseSeedCode:5633 mapZoom:5645 reachBonus:5651 reachOwners:5660 reachResources:5672 settReachHexes:5682 rawClaims:5694 mapSprId:5716 mapSprDefs:5717 tMix:5726 hStr:5731 rng32:5732 mapScatter:5733 mapSpr:5750 eqSVG:5756 sprSVG:5758 stIcon:5766 armyGear:5767 armyUFor:5769 plateStatus:5772 plateBox:5774 mapPlate:5776 settPlate:5787 settBehind:5798 settInsideMarks:5802 mapBarHTML:5817 terrOwners:5828 terrFlags:5830 unrestCamps:5836 intrudersOf:5838 settReach:5842 settEcon:5844 pillageCheck:5853 pillageTargets:5857 runPillage:5860 armyStatus:5867 mapMarkers:5880 inspHTML:5891 inspHead:5894 inspCell:5897 g:5898 inspCan:5899 inspArmy:5900 settStatus:5920 settStatusMarks:5930 inspSett:5935 inspCamp:5962 engageTargets:5974 wireInsp:5980 mapSVG:6000 outlawReport:6087 banditDomain:6098 banditAutoHTML:6099 armyName:6108 syncMapTiers:6110 mapLinkBad:6116 mapLinksHTML:6117 wireBanditAuto:6128 banditAuto:6134 BST:6135 bLog:6136 hk:6138 mapSetts:6139 cellPlayer:6140 cellSett:6142 mapArmies:6145 cellArmy:6146 cellTitle:6149 byDist:6153 isWild:6157 wildZones:6158 outlawZones:6160 zoneOf:6165 zoneOwners:6166 outlawOwners:6171 outlawOwner:6173 outlawOf:6175 campWild:6177 wildCount:6179 wildDone:6180 placeWildOutlaw:6185 rescatterWild:6206 pieceAura:6209 campInRange:6213 hexFree:6216 spawnCamp:6217 growCamps:6219 expandOutlaw:6223 immuneUprising:6226 banditTargetMods:6227 cunningAction:6229 endorsedExtort:6230 banditAct:6231 runBanditMechanics:6260 banditSpeed:6279 banditAuraList:6281 banditRun:6288 moveCamp:6296 banditSiegeTimer:6297 banditMoves:6299 banditSkims:6328 creditSkims:6333 envoyOutcome:6339 banditCunningHTML:6344 dieLookup:6361 terrainTablesHTML:6364 mapToolsHTML:6385 banditPanelHTML:6419 mapAsP:6435 mapEditBlock:6436 mapGuard:6446 guarded:6448 wireMap:6449 srcText:6504 srcMatch:6511 srcHas:6512 bordersOf:6515 poCap:6519 poTextFloor:6520 siegeTextMods:6523 siegeWinterOK:6530 actRestrict:6532 actRiders:6540 settById:6550 besiegeExempt:6552 settBesieged:6553 armySieging:6555 armyBesieged:6557 armyStateTags:6558 armyBlocked:6567 garrisonSizes:6570 hasGarrisons:6573 garrisonGear:6575 garrisonOf:6576 garrisonsOf:6580 garrisonCard:6581 oncePhase:6611 onceEffects:6614 onceState:6617 onceHTML:6619 wireOnce:6626 noteAdd:6636 recoupNote:6638 extortGold:6647 danegeldRows:6656 loans:6662 loanTerms:6663 loanInterest:6666 runLoans:6667 loansHTML:6673 autoExtortRows:6683 extortSlots:6692 exTargets:6696 extortTargetsHTML:6697 runAutoExtort:6700 firstDoubtRed:6722 fdState:6726 gainDoubt:6729 siegeOn:6734 besiegedCount:6735 pById:6736 nextId:6737 captureTransfer:6738 sackApply:6749 resolveRealm:6760 sackLocks:6765 armyHex:6769 settHex:6770 musterLimit:6771 musterTick:6777 hasMusterField:6785 charterFlags:6788 selArmy:6811 canMoveArmy:6812 canEnterSett:6814 armyInside:6816 enterCheck:6819 freeHexNear:6821 kickOut:6824 armiesInside:6827 terrPen:6829 terrBlocked:6830 terrWaterStop:6831 terrStrain:6832 spClauses:6834 spVal:6835 provinceOf:6836 moveTraits:6838 speedOf:6843 hexNb:6875 auraSources:6879 moveRange:6888 moveInfo:6919 moveStops:6922 moveEndTriggers:6927 moveArmyTo:6936 moveOverlay:6952 movePanelHTML:6965 set:6976 computeAll:6977 sceneInfra:6992 wardChains:6998 sceneLots:7005 renderEsBar:7016 sceneArmies:7021 renderScene:7027 renderSettlements:7134 lockTarget:7197 lockBlock:7206 adminUI:7219 firstHostOpen:7235 firstHostBtn:7236 hudSign:7242 hudData:7243 renderHUD:7251 ageStripHTML:7272 setupOn:7286 renderSetup:7287 renderTurnStrip:7308 syncBoardEndBtn:7340 mnavSync:7356 undoSnap:7365 undoRecord:7367 undoRebase:7373 undoScoped:7374 undoApply:7375 doUndo:7388 doRedo:7389 undoButtons:7390 actSnap:7403 actRebase:7404 actJoin:7406 actSchedule:7409 fmtG:7410 boardDiff:7411 actFlush:7443 activityHtml:7456 gameAllowed:7465 gameData:7466 refreshGames:7467 gameReplace:7470 newGameState:7474 isReady:7497 readyCheck:7498 gslug:7511 kwify:7523 wikiA:7534 gkHtml:7535 openFromHash:7552 setLift:7578 gkShow:7587 gkHide:7591 gkFor:7592 chatHdr:7650 chatTargets:7656 chatParse:7658 chatColor:7666 chatLine:7667 chatRender:7671 chatSys:7677 chatComplete:7692
```
