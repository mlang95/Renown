# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-10-15 · data VERSION `0.4.9.9.13-d10-SIMPLE` · HEAD `abce216 2026-10-15`

Hand-written orientation: `CLAUDE.md` (same folder). Paths below are relative to the repo root.

## 1. Folder tree

```
./  (11 files)
  0.4.8 Updated Docs/  (7 files)
  0.4.8.1/  (36 files)
  Assets/  (102 files, generated/assets — not indexed)
  CE/  (36 files)
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
| `CE\REPO_MAP.md` | 843 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE\RULES_push.md` | 649 | Renown |
| `CE\RULES_push_simple.md` | 733 | Renown |
| `CE\RULES_reorganized_6.md` | 638 | Renown |
| `CE\SIMPLE_NODES.PY` | 1 |  |
| `CE\SYNTAX_SWEEP.md` | 343 | Rules syntax sweep — canon applied |
| `CE\TASK2_NOTES.md` | 82 | claude_task_2 — what changed, open questions |
| `CE\build_all_CE.bat` | 506 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE\ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\claude_task.txt` | 85 |  |
| `CE\claude_task_2.txt` | 68 |  |
| `CE\claude_task_3.txt` | 24 |  |
| `CE\infra.py` | 109 |  |
| `CE\parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE\patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE\rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE\renown_data.py` | 4603 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d10.py` | 4603 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
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
| `CE\references\gen_settlement_board.py` | 8023 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
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
| `CE\references\settlement_board.html` | — | generated HTML (1289 KB) |
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
| `RenownWiki\rules-reading-these-rules.html` | 29 | Reading These Rules — Renown |
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
| `RenownWiki\settlement_board.html` | — | generated HTML (1289 KB) |
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
| `FACTION_SUMMARIES` | 608 | dict | 40 |
| `NODES` | 658 | dict | 120 |
| `SIMPLE_NODES` | 1692 | dict | 120 |
| `HOLDING_GROUPS` | 2561 | dict | 9 |
| `SCOPES` | 2578 | tuple | 3 |
| `SCOPE_BY_TYPE` | 2579 | dict | 2 |
| `LINE_LABELS` | 2583 | dict | 28 |
| `lines_of` | 2614 | function |  |
| `LEGACY_NODES` | 2618 | dict | 108 |
| `REQ_KEY` | 2623 | str | 'infrastructure_req' |
| `REQ_LABEL` | 2624 | str | 'Infrastructure Req' |
| `TYPE_ORDER` | 2626 | list | 10 |
| `CHAIN_TERM` | 2629 | str | 'Mastery Chain' |
| `PURSUIT_TERM` | 2631 | tuple | 2 |
| `node_parents` | 2633 | function |  |
| `get_data` | 2653 | function |  |
| `FACTIONS` | 2663 | dict | 41 |
| `INFRASTRUCTURE` | 3082 | dict | 20 |
| `WONDERS` | 3217 | dict | 4 |
| `INFRA_TIERS` | 3218 | list | 5 |
| `SETTLEMENTS` | 3226 | dict | 5 |
| `ERAS` | 3235 | dict | 4 |
| `PO_BANDS` | 3250 | dict | 12 |
| `po_scale` | 3269 | function |  |
| `po_value` | 3276 | function |  |
| `po_effect` | 3281 | function |  |
| `PUBLIC_ORDER` | 3288 | dict | 12 |
| `PUBLIC_ORDER_BY_ERA` | 3289 | dict | 4 |
| `PO_MODIFIERS` | 3295 | dict | 2 |
| `DOMAIN_BOARD` | 3313 | dict | 6 |
| `SEASONS` | 3344 | dict | 4 |
| `TRADE_RULES` | 3352 | dict | 4 |
| `efficient_graph` | 3364 | function |  |
| `EFFICIENT_MULTI` | 3374 | dict | 111 |
| `EFFICIENT` | 3375 | dict | 111 |
| `BANDIT_CAMP_START` | 3383 | int | 10 |
| `BANDIT_CAMP_GOLD` | 3384 | int | 2000 |
| `BANDIT_ARMY_THRESHOLD` | 3385 | int | 25 |
| `BANDIT_GROWTH_PER_ERA` | 3386 | dict | 4 |
| `BANDIT_EQUIPMENT_PER_ERA` | 3387 | dict | 4 |
| `BANDITS` | 3388 | dict | 5 |
| `TIMERS` | 3396 | dict | 8 |
| `CHARTER_MIN_RANGE` | 3408 | int | 4 |
| `OUTLAW_BUFFER_RANGE` | 3409 | int | 2 |
| `HAMLET_RANGE` | 3410 | int | 2 |
| `OUTLAW_COUNTRY_START` | 3411 | int | 3 |
| `WILD_OUTLAW` | 3417 | dict | 5 |
| `wild_outlaw_count` | 3424 | function |  |
| `BANDIT_CAMP_REACH` | 3430 | NoneType |  |
| `VASSAL_EXCHANGE_CAP` | 3433 | int | 5000 |
| `VASSAL_INFLUENCE_TAKE` | 3434 | int | 3 |
| `BUILD_TIMERS` | 3438 | dict | 11 |
| `TERRAIN` | 3452 | dict | 7 |
| `MOVEMENT_MODIFIERS` | 3462 | dict | 6 |
| `TACTICAL_TERRAIN` | 3474 | dict | 7 |
| `TACTICAL_GLOBAL` | 3490 | list | 1 |
| `INFLUENCE_GAIN` | 3492 | dict | 9 |
| `ENVOY_OUTCOME_THRESHOLDS` | 3546 | dict | 4 |
| `ENVOY_OUTCOMES` | 3555 | dict | 5 |
| `ACTIONS` | 3577 | dict | 22 |
| `TREATIES` | 3767 | dict | 5 |
| `ALLIANCE_RULES` | 3775 | list | 3 |
| `EDICT_STREAK_TURNS` | 3785 | int | 5 |
| `EDICTS` | 3787 | dict | 7 |
| `BANDIT_BEHAVIOR` | 3801 | dict | 8 |
| `PURSUIT_UPKEEP_DEFAULT` | 3824 | int | 100 |
| `PURSUIT_UPKEEP_BY_TYPE` | 3825 | dict | 4 |
| `UPKEEP_TRACKS` | 3835 | dict | 3 |
| `HOLDING_TIER_COST` | 3842 | dict | 4 |
| `holding_standing` | 3850 | function |  |
| `holding_cost` | 3856 | function |  |
| `holding_build_time` | 3864 | function |  |
| `pursuit_upkeep` | 3871 | function |  |
| `ARMY_UPKEEP_NOTE` | 3882 | str | "Net Army Upkeep = the sum of each Army' |
| `COSTS` | 3886 | dict | 12 |
| `PHASES` | 3902 | tuple | 5 |
| `STARTING_TURN_PHASE_OPENER` | 3903 | str | 'Council' |
| `STANDING_ARMY_SIEGE_MODIFIER` | 3905 | int | 1 |
| `EMPIRE_START_TIERS` | 3907 | tuple | 2 |
| `STARTING_TREASURY` | 3908 | int | 10000 |
| `AGES` | 3914 | dict | 5 |
| `AGE_YEAR_SEASON` | 3921 | str | 'Spring' |
| `CAPITAL_EDGE_RANGE` | 3922 | int | 4 |
| `BOARD_SIZES` | 3924 | dict | 3 |
| `SIEGE_CALCULUS` | 3930 | dict | 2 |
| `SIEGE_SOURCE_VALUES` | 3945 | dict | 6 |
| `NAME_DISPLAY` | 3972 | dict | 64 |
| `TIER_DISPLAY` | 4000 | dict | 1 |
| `ITEM_TIER_DISPLAY` | 4006 | dict | 1 |
| `TERM_ENVOY_SCORE` | 4013 | str | 'Authority' |
| `display_score` | 4023 | function |  |
| `ALIASES` | 4033 | dict | 66 |
| `display` | 4043 | function |  |
| `display_tier` | 4048 | function |  |
| `display_text` | 4058 | function |  |
| `display_list` | 4081 | function |  |
| `display_md` | 4091 | function |  |
| `display_html` | 4098 | function |  |
| `display_obj` | 4110 | function |  |
| `undisplay` | 4123 | function |  |
| `verify_aliases` | 4132 | function |  |
| `BANDIT_FACES` | 4156 | int | 10 |
| `BANDIT_CUNNING_MIN` | 4157 | int | 10 |
| `die_table_ranges` | 4160 | function |  |
| `die_table_rows` | 4168 | function |  |
| `die_table_text` | 4176 | function |  |
| `die_table_lookup` | 4184 | function |  |
| `die_table_verify` | 4191 | function |  |
| `die_table_weights` | 4210 | function |  |
| `BANDIT_CUNNING_TABLE` | 4220 | dict | 5 |
| `bandit_cunning_ranges` | 4228 | function |  |
| `bandit_cunning_rows` | 4229 | function |  |
| `bandit_cunning_lookup` | 4230 | function |  |
| `bandit_cunning_text` | 4232 | function |  |
| `BANDIT_TACTIC_TABLE` | 4238 | dict | 6 |
| `BANDIT_TACTICS` | 4246 | list | 6 |
| `bandit_tactic_ranges` | 4248 | function |  |
| `bandit_tactic_rows` | 4249 | function |  |
| `bandit_tactic_lookup` | 4250 | function |  |
| `verify_bandit_tables` | 4253 | function |  |
| `RENOWN_MAX` | 4346 | int | 30 |
| `RENOWN_PER_TURN` | 4347 | int | 1 |
| `DOMAIN_POINTS_PER_TURN` | 4348 | int | 1 |
| `FACTION_NAMES` | 4569 | dict | 41 |
| `faction_body` | 4576 | function |  |
| `GLOSSARY_CATEGORIES` | 4585 | list | 17 |

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
- **{{VAL}}** (86): `AGE_YEAR_SEASON`, `ARMY_MAX_RETINUES`, `BANDITS.Bandit Domain Value`, `BANDIT_ARMY_THRESHOLD`, `BANDIT_CAMP_GOLD`, `BANDIT_CAMP_START`, `BANDIT_CUNNING_MIN`, `BANDIT_FACES`, `BLUNDER_THR`, `CAPITAL_EDGE_RANGE`, `CAP_THR`, `CHARTER_MIN_RANGE`, `DICE_PROVENANCE`, `DOMAIN_BOARD.innate_influence_own_envoys.Established`, `DOMAIN_BOARD.innate_influence_own_envoys.Rising`, `DOMAIN_BOARD.innate_influence_own_envoys.Sovereign`, `DOMAIN_BOARD.innate_influence_own_envoys.Untested`, `DOMAIN_BOARD.max_influence_per_vote.Established`, `DOMAIN_BOARD.max_influence_per_vote.Rising`, `DOMAIN_BOARD.max_influence_per_vote.Sovereign`, `DOMAIN_BOARD.max_influence_per_vote.Untested`, `DOMAIN_POINTS_PER_TURN`, `ENDURANCE_REGAIN`, `ERAS.Ascension.innate_diplomacy_influence`, `ERAS.Ascension.max_influence_per_diplomacy_vote`, `ERAS.Eminence.innate_diplomacy_influence`, `ERAS.Eminence.max_influence_per_diplomacy_vote`, `ERAS.Founding.innate_diplomacy_influence`, `ERAS.Founding.max_influence_per_diplomacy_vote`, `ERAS.Founding.renown`, `ERAS.Zenith.innate_diplomacy_influence`, `ERAS.Zenith.max_influence_per_diplomacy_vote`, `FACES`, `FATIGUE_MORALE`, `FOCUSED_THR`, `FRONT_LINE_MAX`, `HAMLET_RANGE`, `INITIATIVE_MAX`, `INITIATIVE_MIN`, `MORALE_DICE_MAX`, `OUTLAW_BUFFER_RANGE`, `OUTLAW_COUNTRY_START`, `PANIC_CASUALTY_THRESHOLD`, `PARRY_BASE`, `PO_MAX`, `PO_MIN`, `PURSUIT_UPKEEP_BY_TYPE.Energy`, `PURSUIT_UPKEEP_BY_TYPE.Monument`, `PURSUIT_UPKEEP_BY_TYPE.Other`, `PURSUIT_UPKEEP_BY_TYPE.Power`, `RENOWN_PER_TURN`, `RESERVE_MAX`, `RETINUES.Knight Templar.cost`, `RETINUES.Knight Templar.to_hit`, `RETINUES.Levy.cost`, `RETINUES.Levy.to_hit`, `RETINUES.Man-at-Arms.cost`, `RETINUES.Man-at-Arms.to_hit`, `RETINUES.Sergeant.cost`, `RETINUES.Sergeant.to_hit`, `ROUT_THR`, `SACK_EXTORT_PER_TIER`, `SETTLEMENTS.City.wards`, `SETTLEMENTS.Hamlet.wards`, `SETTLEMENTS.Metropolis.reach`, `SETTLEMENTS.Metropolis.wards`, `SETTLEMENTS.Town.wards`, `SETTLEMENTS.Village.reach`, `SETTLEMENTS.Village.wards`, `SIEGE_CALCULUS.Lay Siege.floor`, `SIEGE_SOURCE_VALUES.Stone Walls.value`, `SIEGE_SOURCE_VALUES.Wooden Walls.value`, `STANDING_THRESHOLDS.Established`, `STANDING_THRESHOLDS.Rising`, `STANDING_THRESHOLDS.Sovereign`, `STANDING_THRESHOLDS.Untested`, `STARTING_TREASURY`, `STARTING_TURN_PHASE_OPENER`, `TIMERS.Capture Timer.default`, `TIMERS.Sack Timer.default`, `TRADE_RULES.income_per_craft`, `VASSAL_EXCHANGE_CAP`, `VASSAL_INFLUENCE_TAKE`, `WEALTH_EDICT_GOLD`, `WILD_OUTLAW.per_players`, `WILD_OUTLAW.plus`
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
| 74 | ## Core Principles |
| 113 | ## The Turn |
| 125 | ### Timers |
| 133 | ### Empire Phase |
| 159 | ### Council Phase |
| 171 | ### Envoy Phase |
| 182 | ### Battle Phase |
| 186 | ### Rest Phase |
| 200 | # Seasons |
| 206 | # Setup |
| 208 | ## Table Setup |
| 213 | ## Setup Order |
| 222 | ### Ages |
| 228 | ## Player Setup |
| 235 | # Actions & Voting |
| 237 | ## Action Mechanics |
| 239 | ### Sending an Envoy |
| 243 | ### Resolving an Envoy |
| 275 | ## Influence |
| 283 | ## Prowess Actions |
| 287 | ## Cunning Actions |
| 291 | ## Piety Actions |
| 295 | ## Industry Actions |
| 299 | ### Rule: Ulterior Motive |
| 303 | ## Diplomacy Actions |
| 309 | ### Rule: Diplomatic Mission |
| 315 | # Domains & Standings |
| 317 | ### Domain Standings |
| 327 | ### Standing & Influence |
| 340 | # Diplomacy & Treaties |
| 342 | ### Treaties & Alliances |
| 350 | ### Vassalization |
| 372 | # Empire Building |
| 374 | ## Settlements |
| 380 | ### Settlement Wards |
| 384 | ### Chartering Settlements |
| 388 | ### Settlement Reach |
| 392 | ### Hamlets |
| 398 | ## Infrastructure |
| 418 | ## Territory & Terrain |
| 434 | # Economy |
| 436 | ## Public Order |
| 446 | ### Innate Public Order Modifiers |
| 450 | ## Treasury & Upkeep |
| 460 | ### Insolvency & Bankruptcy |
| 473 | ## Trade & Income |
| 475 | ### Who Can Trade & Income |
| 490 | ### Income Types |
| 498 | # Armies |
| 500 | ### Armies Overview |
| 510 | ### Mustering |
| 520 | ### Blocked Armies |
| 526 | # Battles & Sieges |
| 528 | ## Battle Phase |
| 530 | ### Begin Battle |
| 532 | ### Begin Skirmish |
| 540 | ### How a Battle Resolves |
| 544 | ### Begin the Battle — Seize the Initiative |
| 548 | ### The Skirmish Steps |
| 572 | ### Resolve Battle |
| 580 | ### End Battle |
| 582 | ### Tactic Matrix |
| 596 | ## Siege Warfare |
| 602 | ### Siege Timer |
| 608 | ### Beginning a Siege |
| 618 | ### Resolving a Siege |
| 631 | # Bandits |
| 633 | ### Outlaw Country |
| 639 | ### Wild Outlaw Country |
| 645 | ### Spawning Bandit Camps |
| 651 | ### Growing Bandit Camps |
| 655 | ### Bandit Armaments by Era |
| 659 | ### Bandit Growth by Era |
| 663 | ### Bandit Info |
| 683 | ### Bandit Army Behavior |
| 697 | ### Attacking a Bandit Camp |
| 703 | # Holdings |
| 707 | # Equipment |
| 709 | ## Melee Weapons |
| 713 | ## Ranged Weapons |
| 717 | ## Shields |
| 721 | ## Armor |
| 727 | # Factions |
| 731 | # Index |

## 6. Settlement board — `CE\references\gen_settlement_board.py`

Payload keys passed to the HTML as `DATA` (63): `records`, `naturalNames`, `externalTokens`, `simple`, `chainTerm`, `pursuitTerm`, `infra`, `wonders`, `armySrc`, `equip`, `glossary`, `domainBoard`, `publicOrder`, `poByEra`, `wikiBase`, `wikiHome`, `tree`, `rulebook`, `limits`, `eras`, `edicts`, `envoyOutcomes`, `outcomeThresh`, `startPhase`, `actions`, `phaseRules`, `phaseSteps`, `rulesConst`, `ages`, `domains`, `standings`, `tradePerCraft`, `noTradeSeason`, `renownPerTurn`, `dpPerTurn`, `settlements`, `battle`, `terrainRef`, `banditLoadouts`, `bandits`, `treaties`, `allianceRules`, `startTiers`, `startTreasury`, `pursuitUpkeep`, `buildTimers`, `infraTiers`, `timers`, `seasons`, `poModifiers`, `vassalInfluenceTake`, `aliases`, `scoreTerm`, `costs`, `influenceGain`, `siege`, `factions`, `cultures`, `cultureSelf`, `placeNames`, `warnings`, `version`, `sprites`

Python: `load`:27, `strip_md`:34, `has_cond`:76, `to_int`:79, `classify`:82, `_iv`:149, `envoy_fx`:150, `combine_parts`:230, `combine_effects`:271, `rules_payload`:275, `tree_payload`:333, `parse_effects`:367, `parse_mreq`:373, `classify_req_token`:381, `build`:390, `font_faces`:534, `_pursuit_term_template`:559, `render_html`:567, `_style_js`:575, `place_names_payload`:586, `sprite_payload`:605, `find_mapgen`:627, `check_rules`:7694, `_val`:7812, `rules_section`:7821, `phase_steps`:7840, `battle_data`:7854, `bandit_loadouts`:7875, `main`:7923

JS sections: TABLE: seating, Council & Envoy phases :1458, Action automation: Perform picker + resolution :1684,  :4789, Inspect tool :5822, EFFECT PLUMBING: read rule text on a player's active pieces + faction :6470, ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS :6517, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :6606, UNDO / REDO :7323, ACTIVITY LOG :7361, GAME: save · load · new :7425, HOVER KEYWORDS :7471

JS functions (754, name:line):

```
fixBastard:1422 dispScore:1429 POB:1448 poNum:1449 tnow:1469 noteServerDate:1470 lockOn:1478 claimOf:1479 mine:1480 myClaimP:1481 canEdit:1482 boardEndOn:1484 TB:1485 tSeats:1486 tTimer:1487 tTurn:1488 tPhase:1489 PT:1491 tCur:1492 tCurW:1493 sameP:1494 meP:1495 canAct:1496 seatMap:1499 seated:1503 isSpring:1504 hostP:1505 voteOrd:1507 tOrder:1508 canHost:1509 seatsLocked:1510 tStand:1513 eraRec:1514 diploInf:1515 diploCap:1516 eraActions:1517 boardFx:1520 fxOf:1532 scopeOk:1533 sgn:1534 fxLabel:1535 atWarPair:1547 opposeBlock:1548 innateParts:1552 modSum:1558 innateInf:1560 voteCap:1561 inflPool:1564 personalEnvoys:1565 councilEnvoys:1566 tOutcome:1567 outText:1569 tPlan:1572 domStarted:1586 tSim:1589 performEval:1655 comboEval:1661 failPassFx:1670 actionsOf:1671 actReqFlag:1673 actInfoHTML:1677 actCost:1688 domCost:1690 addFaith:1691 alliedP:1692 allyGroup:1693 topPair:1694 actDoubt:1697 musterOpts:1752 runMuster:1757 buildOpts:1769 runBuild:1773 improveOpts:1777 runImprove:1783 runCharter:1789 repairOpts:1794 runRepair:1797 settName:1801 warOn:1802 grandVizier:1806 pfSpec:1809 pfTargets:1811 pfSubs:1821 pfSubLabel:1822 evTxt:1824 pfForm:1828 boardCounts:1861 pendingOf:1863 apLines:1865 resolveEnvoy:1868 autoRes:1903 tApply:1904 tSetPhase:1914 grantDP:1916 dpOwed:1917 tEndTurn:1918 setSeats:1938 tAutoSeat:1943 tSig:1949 tName:1952 tVoteTxt:1953 envBadges:1954 innateTxt:1960 tOutCls:1962 tHistHtml:1963 tPerformHtml:1975 summaryLines:1994 summaryHTML:2007 chronOn:2017 chron:2018 chronSnap:2021 chronTick:2028 chronDate:2038 chronicleHTML:2039 empireChecklistHTML:2047 treeSave:2057 mapRaws:2067 refRawAvail:2070 treeHTML:2074 rulebookHTML:2140 linkifyRules:2143 renderReference:2147 renderTable:2160 tbFit:2237 tPanel:2243 preVoteHTML:2334 tWire:2344 tCountdown:2410 applyTheme:2425 applySkin:2437 startDoms:2443 ageRec:2446 ageRisingOf:2447 startDomsFor:2448 startDomTotal:2449 curYear:2450 applyAgeStart:2451 startSettlements:2453 startSig:2456 reseedIfPristine:2458 newBoard:2463 newPlayer:2465 normalizeD:2481 activeBoard:2501 reindex:2502 pActive:2515 ignHas:2519 flagState:2520 ignBtn:2525 ignNote:2528 unlockStatus:2534 nameHit:2545 missTxt:2546 recomputePC:2548 buildTimerMod:2553 withBuildMod:2557 pursuitBaseTime:2558 infraBaseTime:2559 pursuitBuildTime:2560 infraBuildTime:2561 buildNote:2562 settBaseTime:2563 settBuildTime:2564 itm:2565 infraOn:2566 gameStarted:2567 empTimers:2571 empEconomy:2572 empPO:2576 immuneStrainIn:2582 siegeStrains:2586 effStrained:2587 empArmies:2588 endRow:2594 boardEndTurn:2597 tickRealm:2600 expireBlocks:2603 empirePhase:2605 tickTimers:2628 facTypeBonus:2636 pursuitUpkeep:2638 withBoard:2641 setOnline:2657 clone:2667 jeq:2668 isObj:2669 merge3:2671 splitD:2680 joinD:2686 save:2710 editing:2748 cvar:2768 fmt:2769 cap:2770 settUnbuilt:2774 unbuiltMeta:2775 settMeta:2776 pinSettCell:2777 settExpand:2778 settFinish:2779 settTier:2782 occupants:2783 hamletOK:2784 hamletRoot:2787 hamletFits:2788 effList:2795 effLabel:2800 exemptionsOf:2801 wardExemptions:2810 isFreeRider:2811 wardUse:2812 canPlace:2823 capitalSett:2842 setCapital:2843 isCityPlus:2845 dbActive:2846 capBonus:2850 eraCapBase:2851 eraCap:2852 capSrc:2853 cityCount:2854 eraAllows:2856 rslug:2864 boardFlags:2865 hasMetropolis:2898 onBoard:2899 scopeOf:2901 realmHolder:2902 scopeBlock:2903 nextTier:2908 autoFill:2910 buildFilters:2931 catSave:2940 catFor:2944 pAvail:2948 iAvail:2949 catUpkeep:2950 seg:2951 renderList:2953 wardPick:3004 wpRender:3006 wpPlace:3024 pursuitRow:3028 sub:3039 tip:3041 itemRow:3042 flash:3050 addInfraByName:3052 placeHolding:3058 addItem:3079 removeInstance:3089 removeOneByName:3090 addByName:3095 addPursuitByName:3096 moveInstance:3097 infraReqToks:3113 infraTokStatus:3119 infraReqStatus:3133 infraValid:3138 infraActive:3145 infraReqLinesHTML:3146 masteryInfraToks:3150 masteryInfraHTML:3151 annotReqTok:3158 optionMet:3163 reqStatus:3171 instStatus:3178 chainLine:3185 simpleReq:3194 simpleReqHTML:3206 computeEarned:3214 atomEl:3232 atomsBlock:3241 render:3254 renderTopBar:3309 toggleEmpty:3351 settBar:3354 sfxNorm:3368 sfxLabel:3369 settFx:3378 settFxPanel:3401 renderPursuitBoard:3408 wardPiles:3524 wardGrid:3536 unitFor:3563 tryMove:3568 scrollHost:3601 dropTargetAt:3602 clearDropHL:3610 armDrag:3611 beginDrag:3628 dragMove:3642 dragEnd:3654 factionFree:3664 setFaction:3668 facGearFlags:3677 factionFlags:3683 facSelectHTML:3694 culSelectHTML:3700 cultureOf:3704 holdDom:3705 cultureSet:3709 cultureKeep:3714 cultureKeepWonder:3715 derivedCulture:3717 nameCulture:3719 usedSettNames:3720 genPlaceName:3721 nameSett:3727 renderFaction:3728 timerCtl:3735 placementSelect:3740 contribAcc:3755 contribChips:3758 accChips:3759 pursuitDetail:3767 quickChip:3791 buildsIntoRow:3795 nextLinksSummary:3797 nextLinksHTML:3799 pursuitTable:3807 pursuitCard:3834 renderInfraSection:3922 armyUnlocks:3967 unlockedShieldTiers:3999 tierOK:4003 gloss:4004 glossLookup:4013 openModal:4022 closeModal:4026 kwChipHTML:4027 esc:4028 inspectKeyword:4029 inspectItem:4051 optionList:4074 renderArmy:4089 armyCard:4122 reqMet:4235 weaponUnlockMet:4238 moraleBase:4240 armyUpkeep:4241 moraleCap:4243 effMorale:4245 isRouted:4246 armyVals:4249 armyStats:4257 noUpkeepTiers:4284 holdsActive:4286 playersWithout:4288 calcMetrics:4290 computeTotals:4344 poTaxMod:4372 taxDouble:4377 winterTax:4378 occupyTaxOnly:4387 settInside:4388 settTax:4389 tradeIncome:4392 tradeRaw:4401 seasonNet:4409 husbandryGoldFor:4413 SEASON_DBL_TYPE:4415 boardMetrics:4416 poBandName:4423 poActiveKeys:4425 poActiveEffects:4427 poImmune:4434 poDoubled:4435 renderPO:4437 curSeason:4457 stepSeason:4458 playerOfBoard:4461 igVal:4462 eraIdx:4463 playerAtWar:4464 influenceRowsBase:4465 influenceRows:4496 influenceTotal:4501 poModRows:4504 totTipSimple:4531 totTip:4534 epSources:4545 topSuz:4557 royalMarriage:4560 sameAlliance:4565 poFloor:4568 applyPOFloor:4569 epRows:4570 poModTotal:4583 dpButtons:4584 renderDP:4587 renderMiniStand:4595 renderInfluence:4608 renderPOMods:4611 siegeState:4619 siegeCalc:4620 siegeHTML:4637 realmTimers:4652 timerAddHTML:4653 boardTimerRows:4657 siegeResolveHTML:4663 activeTimersHTML:4669 timersHTML:4675 seasonsHTML:4681 costsHTML:4684 wireDashExtras:4687 renderDash:4715 domBand:4750 standingsBoardHTML:4751 mods:4791 diplo:4796 pk:4797 isVassal:4799 vassalsOf:4800 effPair:4801 pairOf:4804 pname:4805 allianceLabel:4806 pboard:4807 hasRoad:4808 eraRank:4811 allianceEra:4812 allianceOK:4813 pairFlags:4814 dStatus:4821 diploHTML:4825 wireDiplo:4881 newSide:4913 battle:4914 bq:4916 bqAdd:4917 bqSideName:4918 bqLoad:4921 sideHex:4924 bqStart:4928 banditArmy:4931 armBandits:4935 sideArmy:4940 blog:4945 d10:4946 seizeForced:4947 facCombat:4950 sideUnlocks:4962 sideDomains:4966 standingFxOf:4967 hasTiltyard:4971 eqOptions:4972 eqCode:4981 eqNow:4984 eqWeapon:4987 tacAllowed:4995 tacOK:5000 randomTacticPool:5001 sideCalc:5004 pickKey:5114 viewerSide:5115 mdLite:5137 fmtModLong:5139 fmtMod:5142 dieRow:5144 rollHTML:5145 battleSprites:5154 sideHTML:5158 tacEdge:5247 tacticExplainHTML:5250 battleRulesHTML:5262 renderBattle:5269 incoming:5295 roll:5298 ripN:5354 addRip:5355 setPendCas:5356 pendCas:5357 applyCas:5358 endSkirmish:5359 endBattle:5375 wireBattle:5392 edictTimerLen:5440 edictChoices:5442 edictTotal:5448 edictOwners:5449 bumpRenown:5450 edictBoardHTML:5451 wireEdicts:5479 currentEra:5493 standingEffectsHTML:5498 renderRenown:5513 mapClimate:5574 mapPal:5579 tLum:5582 tTone:5584 tLighten:5585 tGlyph:5588 tSwatch:5593 mapState:5600 hexDist:5601 decodeGrid:5604 seedCode:5614 generateMap:5615 parseSeedCode:5623 mapZoom:5634 reachBonus:5640 reachOwners:5649 reachResources:5661 rawReachStatus:5670 settReachHexes:5677 rawClaims:5689 mapSprId:5711 mapSprDefs:5712 tMix:5721 hStr:5726 rng32:5727 mapScatter:5728 mapSpr:5745 eqSVG:5751 sprSVG:5753 stIcon:5761 armyGear:5762 armyUFor:5764 armyStatLine:5765 cellArmyVals:5766 plateStatus:5769 plateBox:5771 mapPlate:5773 settPlate:5784 settBehind:5795 settInsideMarks:5799 mapBarHTML:5814 terrOwners:5825 terrFlags:5827 unrestCamps:5833 intrudersOf:5835 settReach:5839 settEcon:5841 pillageCheck:5850 pillageTargets:5854 runPillage:5857 armyStatus:5864 mapMarkers:5877 inspHTML:5888 inspHead:5891 inspCell:5894 g:5895 inspCan:5896 inspArmy:5897 settStatus:5917 settStatusMarks:5927 inspSett:5932 inspCamp:5959 engageTargets:5971 wireInsp:5977 mapSVG:5997 outlawReport:6084 banditDomain:6095 banditAutoHTML:6096 armyName:6105 syncMapTiers:6107 mapLinkBad:6113 mapLinksHTML:6114 wireBanditAuto:6125 banditAuto:6131 BST:6132 bLog:6133 hk:6135 mapSetts:6136 cellPlayer:6137 cellSett:6139 mapArmies:6142 cellArmy:6143 cellTitle:6146 byDist:6150 isWild:6152 wildZones:6153 outlawOwner:6154 outlawOf:6156 campWild:6159 wildCount:6160 placeWildOutlaw:6163 pieceAura:6181 campInRange:6183 hexFree:6184 spawnCamp:6185 growCamps:6187 expandOutlaw:6191 immuneUprising:6194 banditTargetMods:6195 cunningAction:6197 endorsedExtort:6198 banditAct:6199 runBanditMechanics:6228 banditSpeed:6247 banditAuraList:6249 banditRun:6256 moveCamp:6264 banditSiegeTimer:6265 banditMoves:6267 banditSkims:6296 creditSkims:6301 envoyOutcome:6307 banditCunningHTML:6312 dieLookup:6329 terrainTablesHTML:6332 mapToolsHTML:6353 banditPanelHTML:6387 mapAsP:6403 mapEditBlock:6404 mapGuard:6414 guarded:6416 wireMap:6417 srcText:6472 srcMatch:6479 srcHas:6480 bordersOf:6483 poCap:6487 poTextFloor:6488 siegeTextMods:6491 siegeWinterOK:6498 actRestrict:6500 actRiders:6508 settById:6518 besiegeExempt:6520 settBesieged:6521 armySieging:6523 armyBesieged:6525 armyStateTags:6526 armyBlocked:6535 garrisonSizes:6538 hasGarrisons:6541 garrisonGear:6543 garrisonOf:6544 garrisonsOf:6548 garrisonCard:6549 onceEffects:6578 onceState:6581 onceHTML:6583 wireOnce:6589 noteAdd:6599 recoupNote:6601 extortGold:6610 danegeldRows:6619 loans:6625 loanTerms:6626 loanInterest:6629 runLoans:6630 loansHTML:6636 autoExtortRows:6645 extortSlots:6654 exTargets:6658 extortTargetsHTML:6659 runAutoExtort:6662 firstDoubtRed:6683 gainDoubt:6687 siegeOn:6693 besiegedCount:6694 pById:6695 nextId:6696 captureTransfer:6697 sackApply:6708 resolveRealm:6719 sackLocks:6724 armyHex:6728 settHex:6729 musterLimit:6730 musterTick:6736 hasMusterField:6744 charterFlags:6747 selArmy:6770 canMoveArmy:6771 canEnterSett:6773 armyInside:6775 enterCheck:6778 freeHexNear:6780 kickOut:6783 armiesInside:6786 terrPen:6788 terrBlocked:6789 terrWaterStop:6790 terrStrain:6791 spClauses:6793 spVal:6794 provinceOf:6795 moveTraits:6797 speedOf:6802 hexNb:6834 auraSources:6838 moveRange:6847 moveInfo:6878 moveStops:6881 moveArmyTo:6885 moveOverlay:6901 movePanelHTML:6914 set:6925 computeAll:6926 sceneInfra:6941 wardChains:6947 sceneLots:6954 renderEsBar:6965 sceneArmies:6970 renderScene:6976 renderSettlements:7082 lockTarget:7145 lockBlock:7154 adminUI:7171 firstHostOpen:7187 firstHostBtn:7188 hudSign:7195 hudData:7196 renderHUD:7203 ageStripHTML:7236 setupOn:7250 renderSetup:7251 renderTurnStrip:7271 syncBoardEndBtn:7303 mnavSync:7319 undoSnap:7327 undoRecord:7329 undoRebase:7335 undoScoped:7336 undoApply:7337 doUndo:7350 doRedo:7351 undoButtons:7352 actSnap:7365 actRebase:7366 actJoin:7368 actSchedule:7371 fmtG:7372 boardDiff:7373 actFlush:7405 activityHtml:7418 gameAllowed:7427 gameData:7428 refreshGames:7429 gameReplace:7432 newGameState:7436 isReady:7459 readyCheck:7460 gslug:7473 kwify:7485 wikiA:7496 gkHtml:7497 openFromHash:7514 setLift:7540 gkShow:7549 gkHide:7553 gkFor:7554 chatHdr:7612 chatTargets:7618 chatParse:7620 chatColor:7628 chatLine:7629 chatRender:7633 chatSys:7639 chatComplete:7654
```
