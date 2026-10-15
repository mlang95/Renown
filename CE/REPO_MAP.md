# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-10-15 · data VERSION `0.4.9.9.12-d10-SIMPLE` · HEAD `c9f7476 2026-10-14`

Hand-written orientation: `CLAUDE.md` (same folder). Paths below are relative to the repo root.

## 1. Folder tree

```
./  (11 files)
  0.4.8 Updated Docs/  (7 files)
  0.4.8.1/  (36 files)
  Assets/  (102 files, generated/assets — not indexed)
  CE/  (28 files)
    Combatv4/  (18 files)
      shims/  (6 files)
    ask-the-bot/  (3 files)
    lab_out/  (466 files, generated/assets — not indexed)
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
  RenownWiki/  (94 files)
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
| `CE\REPO_MAP.md` | 823 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE\RULES_push.md` | 649 | Renown |
| `CE\RULES_push_simple.md` | 726 | Renown |
| `CE\RULES_reorganized_6.md` | 638 | Renown |
| `CE\SIMPLE_NODES.PY` | 1 |  |
| `CE\build_all_CE.bat` | 506 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE\ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\claude_task.txt` | 85 |  |
| `CE\infra.py` | 109 |  |
| `CE\parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE\patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE\rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE\renown_data.py` | 4536 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d10.py` | 4536 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d8.py` | 2801 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_server.bat` | 16 | renown_server.bat - (re)start the Renown board server in WSL. |
| `CE\repo_map.py` | 242 | repo_map.py — write REPO_MAP.md next to this file (CE/, beside CLAUDE.md): a generated index of the Renown repo for |
| `CE\run_tournament_d10.bat` | 108 | Renown d10 tournament runner  —  CE build |
| `CE\run_tournament_d10.py` | 131 | run_tournament_d10.py — run the Renown tournament against the d10 build. |
| `CE\sprites.py` | 2602 | sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene). |
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
| `CE\ask-the-bot\renown_faq.txt` | 498 |  |
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
| `CE\references\build_wiki.py` | 1505 | build_wiki.py — multi-page linked HTML wiki from RULES.md + renown_data. |
| `CE\references\card_copies.py` | 69 | card_copies.py — print-quantity logic for pursuit cards, driven by the spec |
| `CE\references\card_sheet.py` | 679 | Renown — Specialization card sheet generator. |
| `CE\references\ce_paths.py` | 123 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\references\combat_sheet.py` | 352 | combat_sheet.py — Renown combat quick-reference (print & laminate). |
| `CE\references\combine_docx.py` | 257 | combine_docx.py — append the Compendium after the Rules doc as one book: |
| `CE\references\compendium_data.json` | 3273 |  |
| `CE\references\display_pdf.py` | 90 | display_pdf.py — NAME_DISPLAY for every reportlab sheet (cards, tiles, equipment, combat). |
| `CE\references\docx_tables.py` | 539 | docx_tables.py — generate Word table fragments (OOXML) from renown_data. |
| `CE\references\domain_board.py` | 321 | domain_board.py - landscape Domain Standing Board. |
| `CE\references\equipment_sheet.py` | 691 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `CE\references\faction_sheet.py` | 447 | Renown — Faction card sheet generator. |
| `CE\references\faq_export.py` | 446 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `CE\references\gen_compendium.py` | 184 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `CE\references\gen_layout.py` | 374 | gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data. |
| `CE\references\gen_layout_roots.py` | 123 | gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it. |
| `CE\references\gen_settlement_board.py` | 7741 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE\references\generate_cards.py` | 93 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `CE\references\host_sheet.py` | 452 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `CE\references\infra_board.py` | 130 | infra_board.py - landscape Infrastructure Board. |
| `CE\references\layout.json` | 1421 |  |
| `CE\references\layout_roots.json` | 1336 |  |
| `CE\references\layout_simple.json` | 1509 |  |
| `CE\references\md_to_docx.py` | 329 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `CE\references\package-lock.json` | 205 |  |
| `CE\references\package.json` | 6 |  |
| `CE\references\patch_pursuit_domains.py` | 58 | patch_pursuit_domains.py |
| `CE\references\playstyle_reference.py` | 396 | playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture). |
| `CE\references\pursuit_tiles.py` | 282 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `CE\references\reference_sheets.py` | 891 | Renown — Reference sheet generators. |
| `CE\references\render_tree.py` | 272 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `CE\references\server.py` | 501 | Renown settlement-board server  —  stdlib only, no pip installs. |
| `CE\references\settlement_board.html` | — | generated HTML (1235 KB) |
| `CE\references\settlement_mats.py` | 293 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `CE\references\spec_tree_sheet.py` | 1183 | Renown — Specialization Tree renderer. |
| `CE\references\svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `CE\references\sync_derived.py` | 116 | sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES. |
| `CE\references\tactic_sheet.py` | 446 | Renown — Tactic card sheet generator (v3). |
| `CE\references\wiki_markers.py` | 288 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
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
| `CE\worldbuilding\renown_worldlore.py` | 3385 | renown_worldlore.py |
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
| `RenownWiki\rules-bandits.html` | 57 | Bandits — Renown |
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
| `RenownWiki\rules-infrastructure.html` | 30 | Infrastructure — Renown |
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
| `RenownWiki\rules-setup-order.html` | 29 | Setup Order — Renown |
| `RenownWiki\rules-shields.html` | 20 | Shields — Renown |
| `RenownWiki\rules-siege-warfare.html` | 55 | Siege Warfare — Renown |
| `RenownWiki\rules-table-setup.html` | 23 | Table Setup — Renown |
| `RenownWiki\rules-territory-terrain.html` | 26 | Territory &amp; Terrain — Renown |
| `RenownWiki\rules-the-turn.html` | 106 | The Turn — Renown |
| `RenownWiki\rules-trade-income.html` | 36 | Trade &amp; Income — Renown |
| `RenownWiki\rules-treasury-upkeep.html` | 32 | Treasury &amp; Upkeep — Renown |
| `RenownWiki\search.js` | 7 |  |
| `RenownWiki\seasons-ref.html` | 19 | Seasons — Renown |
| `RenownWiki\settlement_board.html` | — | generated HTML (1235 KB) |
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
| `RenownWiki\wonders-ref.html` | 19 | Wonders — Renown |
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
| `VERSION` | 6 | str | '0.4.9.9.12-d10-SIMPLE' |
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
| `GLOSSARY` | 114 | dict | 156 |
| `MORALE_GLOSSARY` | 255 | dict | 4 |
| `ARMY_MAX_RETINUES` | 281 | int | 25 |
| `FRONT_LINE_MAX` | 282 | int | 10 |
| `RESERVE_MAX` | 283 | int | 5 |
| `MORALE_DICE_MAX` | 284 | int | 5 |
| `PANIC_CASUALTY_THRESHOLD` | 285 | int | 5 |
| `ENDURANCE_REGAIN` | 286 | int | 2 |
| `RETINUES` | 290 | dict | 4 |
| `WEAPONS` | 297 | dict | 19 |
| `RANGED` | 319 | dict | 6 |
| `SHIELDS` | 329 | dict | 6 |
| `ARMORS` | 338 | dict | 6 |
| `TIERS` | 349 | list | 5 |
| `TIER_UNLOCK` | 350 | dict | 5 |
| `STANDING_EFFECTS` | 361 | dict | 4 |
| `TACTIC_MATRIX` | 384 | dict | 49 |
| `TACTICS` | 443 | list | 7 |
| `TACTIC_NOTES` | 445 | dict | 0 |
| `CULTURES` | 459 | dict | 15 |
| `FACTION_SUMMARIES` | 603 | dict | 40 |
| `NODES` | 653 | dict | 119 |
| `SIMPLE_NODES` | 1687 | dict | 119 |
| `HOLDING_GROUPS` | 2549 | dict | 9 |
| `SCOPES` | 2566 | tuple | 3 |
| `SCOPE_BY_TYPE` | 2567 | dict | 2 |
| `LINE_LABELS` | 2571 | dict | 28 |
| `lines_of` | 2602 | function |  |
| `LEGACY_NODES` | 2606 | dict | 108 |
| `REQ_KEY` | 2611 | str | 'infrastructure_req' |
| `REQ_LABEL` | 2612 | str | 'Infrastructure Req' |
| `TYPE_ORDER` | 2614 | list | 10 |
| `CHAIN_TERM` | 2617 | str | 'Mastery Chain' |
| `PURSUIT_TERM` | 2619 | tuple | 2 |
| `node_parents` | 2621 | function |  |
| `get_data` | 2641 | function |  |
| `FACTIONS` | 2651 | dict | 41 |
| `INFRASTRUCTURE` | 3070 | dict | 16 |
| `WONDERS` | 3172 | dict | 4 |
| `SETTLEMENTS` | 3211 | dict | 5 |
| `ERAS` | 3220 | dict | 4 |
| `PUBLIC_ORDER` | 3233 | dict | 12 |
| `PO_MODIFIERS` | 3256 | dict | 2 |
| `DOMAIN_BOARD` | 3274 | dict | 6 |
| `SEASONS` | 3305 | dict | 4 |
| `TRADE_RULES` | 3313 | dict | 4 |
| `efficient_graph` | 3325 | function |  |
| `EFFICIENT_MULTI` | 3335 | dict | 110 |
| `EFFICIENT` | 3336 | dict | 110 |
| `BANDIT_CAMP_START` | 3344 | int | 10 |
| `BANDIT_CAMP_GOLD` | 3345 | int | 2000 |
| `BANDIT_ARMY_THRESHOLD` | 3346 | int | 25 |
| `BANDIT_GROWTH_PER_ERA` | 3347 | dict | 4 |
| `BANDIT_EQUIPMENT_PER_ERA` | 3348 | dict | 4 |
| `BANDITS` | 3349 | dict | 5 |
| `TIMERS` | 3357 | dict | 8 |
| `CHARTER_MIN_RANGE` | 3369 | int | 4 |
| `OUTLAW_BUFFER_RANGE` | 3370 | int | 2 |
| `HAMLET_RANGE` | 3371 | int | 2 |
| `OUTLAW_COUNTRY_START` | 3372 | int | 3 |
| `VASSAL_EXCHANGE_CAP` | 3375 | int | 5000 |
| `VASSAL_INFLUENCE_TAKE` | 3376 | int | 3 |
| `BUILD_TIMERS` | 3380 | dict | 11 |
| `TERRAIN` | 3394 | dict | 7 |
| `MOVEMENT_MODIFIERS` | 3404 | dict | 6 |
| `TACTICAL_TERRAIN` | 3416 | dict | 7 |
| `TACTICAL_GLOBAL` | 3432 | list | 1 |
| `INFLUENCE_GAIN` | 3434 | dict | 9 |
| `ENVOY_OUTCOME_THRESHOLDS` | 3488 | dict | 4 |
| `ENVOY_OUTCOMES` | 3497 | dict | 5 |
| `ACTIONS` | 3519 | dict | 22 |
| `TREATIES` | 3709 | dict | 5 |
| `ALLIANCE_RULES` | 3717 | list | 3 |
| `EDICT_STREAK_TURNS` | 3727 | int | 5 |
| `EDICTS` | 3729 | dict | 7 |
| `BANDIT_BEHAVIOR` | 3743 | dict | 7 |
| `PURSUIT_UPKEEP_DEFAULT` | 3766 | int | 100 |
| `PURSUIT_UPKEEP_BY_TYPE` | 3767 | dict | 4 |
| `UPKEEP_TRACKS` | 3777 | dict | 3 |
| `HOLDING_TIER_COST` | 3784 | dict | 4 |
| `holding_standing` | 3792 | function |  |
| `holding_cost` | 3798 | function |  |
| `holding_build_time` | 3806 | function |  |
| `pursuit_upkeep` | 3813 | function |  |
| `ARMY_UPKEEP_NOTE` | 3824 | str | "Net Army Upkeep = the sum of each Army' |
| `COSTS` | 3828 | dict | 12 |
| `PHASES` | 3844 | tuple | 5 |
| `STARTING_TURN_PHASE_OPENER` | 3845 | str | 'Council' |
| `STANDING_ARMY_SIEGE_MODIFIER` | 3847 | int | 1 |
| `EMPIRE_START_TIERS` | 3849 | tuple | 2 |
| `STARTING_TREASURY` | 3850 | int | 10000 |
| `AGES` | 3856 | dict | 5 |
| `AGE_YEAR_SEASON` | 3863 | str | 'Spring' |
| `CAPITAL_EDGE_RANGE` | 3864 | int | 4 |
| `BOARD_SIZES` | 3866 | dict | 3 |
| `SIEGE_CALCULUS` | 3872 | dict | 2 |
| `SIEGE_SOURCE_VALUES` | 3887 | dict | 6 |
| `NAME_DISPLAY` | 3914 | dict | 64 |
| `TIER_DISPLAY` | 3942 | dict | 1 |
| `ITEM_TIER_DISPLAY` | 3948 | dict | 1 |
| `TERM_ENVOY_SCORE` | 3955 | str | 'Authority' |
| `display_score` | 3963 | function |  |
| `ALIASES` | 3973 | dict | 66 |
| `display` | 3983 | function |  |
| `display_tier` | 3988 | function |  |
| `display_text` | 3996 | function |  |
| `display_list` | 4019 | function |  |
| `display_md` | 4029 | function |  |
| `display_html` | 4036 | function |  |
| `display_obj` | 4048 | function |  |
| `undisplay` | 4061 | function |  |
| `verify_aliases` | 4070 | function |  |
| `BANDIT_FACES` | 4094 | int | 10 |
| `BANDIT_CUNNING_MIN` | 4095 | int | 10 |
| `die_table_ranges` | 4098 | function |  |
| `die_table_rows` | 4106 | function |  |
| `die_table_text` | 4114 | function |  |
| `die_table_lookup` | 4122 | function |  |
| `die_table_verify` | 4129 | function |  |
| `die_table_weights` | 4148 | function |  |
| `BANDIT_CUNNING_TABLE` | 4158 | dict | 5 |
| `bandit_cunning_ranges` | 4166 | function |  |
| `bandit_cunning_rows` | 4167 | function |  |
| `bandit_cunning_lookup` | 4168 | function |  |
| `bandit_cunning_text` | 4170 | function |  |
| `BANDIT_TACTIC_TABLE` | 4176 | dict | 6 |
| `BANDIT_TACTICS` | 4184 | list | 6 |
| `bandit_tactic_ranges` | 4186 | function |  |
| `bandit_tactic_rows` | 4187 | function |  |
| `bandit_tactic_lookup` | 4188 | function |  |
| `verify_bandit_tables` | 4191 | function |  |
| `RENOWN_MAX` | 4279 | int | 30 |
| `RENOWN_PER_TURN` | 4280 | int | 1 |
| `DOMAIN_POINTS_PER_TURN` | 4281 | int | 1 |
| `FACTION_NAMES` | 4502 | dict | 41 |
| `faction_body` | 4509 | function |  |
| `GLOSSARY_CATEGORIES` | 4518 | list | 17 |

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

- **{{TABLE}}** (31): `edicts`, `eras`, `timers`, `seasons`, `ages`, `net_influence`, `envoy_outcomes`, `influence_gain`, `domain_board`, `treaties`, `settlements`, `infrastructure`, `wonders`, `build_timers`, `terrain`, `public_order`, `po_modifiers`, `trade_rules`, `retinues`, `tactic_matrix`, `siege_calculus`, `bandit_armaments`, `bandit_growth`, `bandit_cunning`, `bandit_tactics`, `holdings`, `weapons`, `ranged`, `shields`, `armor`, `factions`
- **{{GLOSSARY}}** (16): `Reading the Rules`, `Council & Envoys`, `Actions`, `Domains & Scoring`, `Treaties`, `Settlements & Holdings`, `Map & Range`, `Economy & Public Order`, `Army States`, `Battle Structure`, `Combat Keywords — Defense`, `Combat Keywords — Offense`, `Combat Keywords — Handling`, `Combat Keywords — Immune / Negate`, `World`, `Equipment Tiers`
- **{{ACTIONS}}** (5): `Prowess`, `Cunning`, `Piety`, `Industry`, `Diplomacy`
- **{{LIST}}** (1): `ALLIANCE_RULES`
- **{{TERM}}** (1): `Speed X`
- **{{IDX}}** (23): `Era`, `Empire Phase`, `Council Phase`, `Envoy Phase`, `Battle Phase`, `Rest Phase`, `Season`, `Age`, `Settlement`, `Hamlet`, `Infrastructure`, `Primitive`, `Developed`, `Sophisticated`, `Wonder`, `Treasury`, `Revenue`, `Trade Agreement`, `Army`, `Lay Siege`, `Capture`, `Sack`, `Bandit Camp`
- **{{VAL}}** (84): `AGE_YEAR_SEASON`, `ARMY_MAX_RETINUES`, `BANDITS.Bandit Domain Value`, `BANDIT_ARMY_THRESHOLD`, `BANDIT_CAMP_GOLD`, `BANDIT_CAMP_START`, `BANDIT_CUNNING_MIN`, `BANDIT_FACES`, `BLUNDER_THR`, `CAPITAL_EDGE_RANGE`, `CAP_THR`, `CHARTER_MIN_RANGE`, `DICE_PROVENANCE`, `DOMAIN_BOARD.innate_influence_own_envoys.Established`, `DOMAIN_BOARD.innate_influence_own_envoys.Rising`, `DOMAIN_BOARD.innate_influence_own_envoys.Sovereign`, `DOMAIN_BOARD.innate_influence_own_envoys.Untested`, `DOMAIN_BOARD.max_influence_per_vote.Established`, `DOMAIN_BOARD.max_influence_per_vote.Rising`, `DOMAIN_BOARD.max_influence_per_vote.Sovereign`, `DOMAIN_BOARD.max_influence_per_vote.Untested`, `DOMAIN_POINTS_PER_TURN`, `ENDURANCE_REGAIN`, `ERAS.Ascension.innate_diplomacy_influence`, `ERAS.Ascension.max_influence_per_diplomacy_vote`, `ERAS.Eminence.innate_diplomacy_influence`, `ERAS.Eminence.max_influence_per_diplomacy_vote`, `ERAS.Founding.innate_diplomacy_influence`, `ERAS.Founding.max_influence_per_diplomacy_vote`, `ERAS.Founding.renown`, `ERAS.Zenith.innate_diplomacy_influence`, `ERAS.Zenith.max_influence_per_diplomacy_vote`, `FACES`, `FATIGUE_MORALE`, `FOCUSED_THR`, `FRONT_LINE_MAX`, `HAMLET_RANGE`, `INITIATIVE_MAX`, `INITIATIVE_MIN`, `MORALE_DICE_MAX`, `OUTLAW_BUFFER_RANGE`, `OUTLAW_COUNTRY_START`, `PANIC_CASUALTY_THRESHOLD`, `PARRY_BASE`, `PO_MAX`, `PO_MIN`, `PURSUIT_UPKEEP_BY_TYPE.Energy`, `PURSUIT_UPKEEP_BY_TYPE.Monument`, `PURSUIT_UPKEEP_BY_TYPE.Other`, `PURSUIT_UPKEEP_BY_TYPE.Power`, `RENOWN_PER_TURN`, `RESERVE_MAX`, `RETINUES.Knight Templar.cost`, `RETINUES.Knight Templar.to_hit`, `RETINUES.Levy.cost`, `RETINUES.Levy.to_hit`, `RETINUES.Man-at-Arms.cost`, `RETINUES.Man-at-Arms.to_hit`, `RETINUES.Sergeant.cost`, `RETINUES.Sergeant.to_hit`, `ROUT_THR`, `SACK_EXTORT_PER_TIER`, `SETTLEMENTS.City.wards`, `SETTLEMENTS.Hamlet.wards`, `SETTLEMENTS.Metropolis.reach`, `SETTLEMENTS.Metropolis.wards`, `SETTLEMENTS.Town.wards`, `SETTLEMENTS.Village.reach`, `SETTLEMENTS.Village.wards`, `SIEGE_CALCULUS.Lay Siege.floor`, `SIEGE_SOURCE_VALUES.Stone Walls.value`, `SIEGE_SOURCE_VALUES.Wooden Walls.value`, `STANDING_THRESHOLDS.Established`, `STANDING_THRESHOLDS.Rising`, `STANDING_THRESHOLDS.Sovereign`, `STANDING_THRESHOLDS.Untested`, `STARTING_TREASURY`, `STARTING_TURN_PHASE_OPENER`, `TIMERS.Capture Timer.default`, `TIMERS.Sack Timer.default`, `TRADE_RULES.income_per_craft`, `VASSAL_EXCHANGE_CAP`, `VASSAL_INFLUENCE_TAKE`, `WEALTH_EDICT_GOLD`
- **docx_tables.REGISTRY** (32): `ages`, `armor`, `bandit_armaments`, `bandit_cunning`, `bandit_growth`, `bandit_tactics`, `build_timers`, `domain_board`, `edicts`, `envoy_outcomes`, `eras`, `factions`, `holdings`, `influence_gain`, `infrastructure`, `net_influence`, `po_modifiers`, `public_order`, `ranged`, `retinues`, `seasons`, `settlements`, `shields`, `siege_calculus`, `tactic_matrix`, `tactical_terrain`, `terrain`, `timers`, `trade_rules`, `treaties`, `weapons`, `wonders`

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
| 221 | ### Ages |
| 227 | ## Player Setup |
| 234 | # Actions & Voting |
| 236 | ## Action Mechanics |
| 238 | ### Sending an Envoy |
| 242 | ### Resolving an Envoy |
| 274 | ## Influence |
| 282 | ## Prowess Actions |
| 286 | ## Cunning Actions |
| 290 | ## Piety Actions |
| 294 | ## Industry Actions |
| 298 | ### Rule: Ulterior Motive |
| 302 | ## Diplomacy Actions |
| 308 | ### Rule: Diplomatic Mission |
| 314 | # Domains & Standings |
| 316 | ### Domain Standings |
| 326 | ### Standing & Influence |
| 339 | # Diplomacy & Treaties |
| 341 | ### Treaties & Alliances |
| 349 | ### Vassalization |
| 371 | # Empire Building |
| 373 | ## Settlements |
| 379 | ### Settlement Wards |
| 383 | ### Chartering Settlements |
| 387 | ### Settlement Reach |
| 391 | ### Hamlets |
| 397 | ## Infrastructure |
| 421 | ## Territory & Terrain |
| 437 | # Economy |
| 439 | ## Public Order |
| 449 | ### Innate Public Order Modifiers |
| 453 | ## Treasury & Upkeep |
| 463 | ### Insolvency & Bankruptcy |
| 476 | ## Trade & Income |
| 478 | ### Who Can Trade & Income |
| 493 | ### Income Types |
| 501 | # Armies |
| 503 | ### Armies Overview |
| 513 | ### Mustering |
| 523 | ### Blocked Armies |
| 529 | # Battles & Sieges |
| 531 | ## Battle Phase |
| 533 | ### Begin Battle |
| 535 | ### Begin Skirmish |
| 543 | ### How a Battle Resolves |
| 547 | ### Begin the Battle — Seize the Initiative |
| 551 | ### The Skirmish Steps |
| 575 | ### Resolve Battle |
| 583 | ### End Battle |
| 585 | ### Tactic Matrix |
| 599 | ## Siege Warfare |
| 605 | ### Siege Timer |
| 611 | ### Beginning a Siege |
| 621 | ### Resolving a Siege |
| 634 | # Bandits |
| 636 | ### Outlaw Country |
| 642 | ### Spawning Bandit Camps |
| 648 | ### Growing Bandit Camps |
| 652 | ### Bandit Armaments by Era |
| 656 | ### Bandit Growth by Era |
| 660 | ### Bandit Info |
| 678 | ### Bandit Army Behavior |
| 690 | ### Attacking a Bandit Camp |
| 696 | # Holdings |
| 700 | # Equipment |
| 702 | ## Melee Weapons |
| 706 | ## Ranged Weapons |
| 710 | ## Shields |
| 714 | ## Armor |
| 720 | # Factions |
| 724 | # Index |

## 6. Settlement board — `CE\references\gen_settlement_board.py`

Payload keys passed to the HTML as `DATA` (58): `records`, `naturalNames`, `externalTokens`, `simple`, `chainTerm`, `pursuitTerm`, `infra`, `wonders`, `armySrc`, `equip`, `glossary`, `domainBoard`, `publicOrder`, `wikiBase`, `wikiHome`, `tree`, `rulebook`, `limits`, `eras`, `edicts`, `envoyOutcomes`, `outcomeThresh`, `startPhase`, `actions`, `phaseRules`, `phaseSteps`, `rulesConst`, `ages`, `domains`, `standings`, `tradePerCraft`, `noTradeSeason`, `renownPerTurn`, `dpPerTurn`, `settlements`, `battle`, `terrainRef`, `banditLoadouts`, `bandits`, `treaties`, `allianceRules`, `startTiers`, `startTreasury`, `pursuitUpkeep`, `buildTimers`, `timers`, `seasons`, `poModifiers`, `vassalInfluenceTake`, `aliases`, `scoreTerm`, `costs`, `influenceGain`, `siege`, `factions`, `warnings`, `version`, `sprites`

Python: `load`:27, `strip_md`:34, `has_cond`:76, `to_int`:79, `classify`:82, `_iv`:149, `envoy_fx`:150, `combine_parts`:231, `combine_effects`:272, `rules_payload`:276, `tree_payload`:334, `parse_effects`:368, `parse_mreq`:374, `classify_req_token`:382, `build`:391, `font_faces`:534, `_pursuit_term_template`:559, `render_html`:567, `_style_js`:575, `sprite_payload`:586, `find_mapgen`:608, `check_rules`:7417, `_val`:7535, `rules_section`:7544, `phase_steps`:7563, `battle_data`:7577, `bandit_loadouts`:7598, `main`:7646

JS sections: TABLE: seating, Council & Envoy phases :1436, Action automation: Perform picker + resolution :1662,  :4664, Inspect tool :5646, EFFECT PLUMBING: read rule text on a player's active pieces + faction :6240, ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS :6287, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :6373, UNDO / REDO :7046, ACTIVITY LOG :7084, GAME: save · load · new :7148, HOVER KEYWORDS :7194

JS functions (713, name:line):

```
fixBastard:1403 dispScore:1410 tnow:1447 noteServerDate:1448 lockOn:1456 claimOf:1457 mine:1458 myClaimP:1459 canEdit:1460 boardEndOn:1462 TB:1463 tSeats:1464 tTimer:1465 tTurn:1466 tPhase:1467 PT:1469 tCur:1470 tCurW:1471 sameP:1472 meP:1473 canAct:1474 seatMap:1477 seated:1481 isSpring:1482 hostP:1483 voteOrd:1485 tOrder:1486 canHost:1487 seatsLocked:1488 tStand:1491 eraRec:1492 diploInf:1493 diploCap:1494 eraActions:1495 boardFx:1498 fxOf:1510 scopeOk:1511 sgn:1512 fxLabel:1513 atWarPair:1525 opposeBlock:1526 innateParts:1530 modSum:1536 innateInf:1538 voteCap:1539 inflPool:1542 personalEnvoys:1543 councilEnvoys:1544 tOutcome:1545 outText:1547 tPlan:1550 domStarted:1564 tSim:1567 performEval:1633 comboEval:1639 failPassFx:1648 actionsOf:1649 actReqFlag:1651 actInfoHTML:1655 actCost:1666 domCost:1668 addFaith:1669 alliedP:1670 allyGroup:1671 topPair:1672 actDoubt:1675 musterOpts:1729 runMuster:1734 buildOpts:1746 runBuild:1750 improveOpts:1754 runImprove:1760 runCharter:1766 repairOpts:1771 runRepair:1774 settName:1778 warOn:1779 pfSpec:1781 pfTargets:1783 pfSubs:1792 pfSubLabel:1793 evTxt:1795 pfForm:1799 boardCounts:1832 pendingOf:1834 apLines:1836 resolveEnvoy:1839 autoRes:1873 tApply:1874 tSetPhase:1884 grantDP:1886 dpOwed:1887 tEndTurn:1888 setSeats:1908 tAutoSeat:1913 tSig:1919 tName:1922 tVoteTxt:1923 envBadges:1924 innateTxt:1930 tOutCls:1932 tHistHtml:1933 tPerformHtml:1945 summaryLines:1964 summaryHTML:1974 empireChecklistHTML:1980 treeSave:1990 mapRaws:2000 refRawAvail:2003 treeHTML:2007 rulebookHTML:2072 linkifyRules:2075 renderReference:2079 renderTable:2092 tbFit:2169 tPanel:2175 preVoteHTML:2266 tWire:2276 tCountdown:2331 applyTheme:2346 applySkin:2358 startDoms:2364 ageRec:2367 ageRisingOf:2368 startDomsFor:2369 startDomTotal:2370 curYear:2371 applyAgeStart:2372 startSettlements:2374 startSig:2377 reseedIfPristine:2379 newBoard:2384 newPlayer:2386 normalizeD:2402 activeBoard:2422 reindex:2423 pActive:2436 ignHas:2440 flagState:2441 ignBtn:2446 ignNote:2449 unlockStatus:2455 nameHit:2466 missTxt:2467 recomputePC:2469 buildTimerMod:2474 withBuildMod:2478 pursuitBaseTime:2479 infraBaseTime:2480 pursuitBuildTime:2481 infraBuildTime:2482 buildNote:2483 settBaseTime:2484 settBuildTime:2485 itm:2486 infraOn:2487 gameStarted:2488 empTimers:2492 empEconomy:2493 empPO:2497 immuneStrainIn:2503 siegeStrains:2507 effStrained:2508 empArmies:2509 endRow:2515 boardEndTurn:2518 tickRealm:2521 expireBlocks:2524 empirePhase:2526 tickTimers:2549 facTypeBonus:2557 pursuitUpkeep:2559 withBoard:2562 setOnline:2578 clone:2588 jeq:2589 isObj:2590 merge3:2592 splitD:2601 joinD:2607 save:2631 editing:2668 cvar:2688 fmt:2689 cap:2690 settUnbuilt:2694 unbuiltMeta:2695 settMeta:2696 pinSettCell:2697 settExpand:2698 settFinish:2699 settTier:2702 occupants:2703 hamletOK:2704 hamletRoot:2707 hamletFits:2708 effList:2715 effLabel:2720 exemptionsOf:2721 wardExemptions:2730 isFreeRider:2731 wardUse:2732 canPlace:2743 capitalSett:2762 setCapital:2763 isCityPlus:2765 dbActive:2766 capBonus:2770 eraCapBase:2771 eraCap:2772 capSrc:2773 cityCount:2774 eraAllows:2776 rslug:2784 boardFlags:2785 hasMetropolis:2816 onBoard:2817 scopeOf:2819 realmHolder:2820 scopeBlock:2821 nextTier:2826 autoFill:2828 buildFilters:2849 catSave:2858 catFor:2862 pAvail:2866 iAvail:2867 catUpkeep:2868 seg:2869 renderList:2871 wardPick:2922 wpRender:2924 wpPlace:2942 pursuitRow:2946 sub:2957 tip:2959 itemRow:2960 flash:2968 addInfraByName:2970 placeHolding:2975 addItem:2996 removeInstance:3006 removeOneByName:3007 addByName:3012 addPursuitByName:3013 moveInstance:3014 infraReqToks:3030 infraTokStatus:3036 infraReqStatus:3050 infraValid:3055 infraActive:3062 infraReqLinesHTML:3063 masteryInfraToks:3067 masteryInfraHTML:3068 annotReqTok:3075 optionMet:3080 reqStatus:3088 instStatus:3095 chainLine:3102 simpleReq:3111 simpleReqHTML:3123 computeEarned:3131 atomEl:3149 atomsBlock:3158 render:3171 renderTopBar:3226 toggleEmpty:3266 settBar:3269 sfxNorm:3283 sfxLabel:3284 settFx:3293 settFxPanel:3316 renderPursuitBoard:3323 wardPiles:3439 wardGrid:3451 unitFor:3478 tryMove:3483 scrollHost:3516 dropTargetAt:3517 clearDropHL:3525 armDrag:3526 beginDrag:3543 dragMove:3557 dragEnd:3569 factionFree:3579 setFaction:3583 facGearFlags:3592 factionFlags:3598 facSelectHTML:3609 renderFaction:3613 timerCtl:3620 placementSelect:3625 contribAcc:3640 contribChips:3643 accChips:3644 pursuitDetail:3652 quickChip:3676 buildsIntoRow:3680 nextLinksSummary:3682 nextLinksHTML:3684 pursuitTable:3692 pursuitCard:3719 renderInfraSection:3806 armyUnlocks:3851 unlockedShieldTiers:3883 tierOK:3887 gloss:3888 glossLookup:3897 openModal:3906 closeModal:3910 kwChipHTML:3911 esc:3912 inspectKeyword:3913 inspectItem:3935 optionList:3958 renderArmy:3973 armyCard:4006 reqMet:4119 weaponUnlockMet:4122 moraleBase:4124 armyUpkeep:4125 moraleCap:4127 effMorale:4129 isRouted:4130 armyVals:4133 armyStats:4141 noUpkeepTiers:4168 holdsActive:4170 playersWithout:4172 calcMetrics:4174 computeTotals:4228 poTaxMod:4256 taxDouble:4261 winterTax:4262 occupyTaxOnly:4271 settInside:4272 settTax:4273 tradeIncome:4276 tradeRaw:4282 seasonNet:4290 husbandryGoldFor:4294 SEASON_DBL_TYPE:4296 boardMetrics:4297 poBandName:4304 poActiveKeys:4306 poActiveEffects:4308 poImmune:4315 poDoubled:4316 renderPO:4318 curSeason:4338 stepSeason:4339 playerOfBoard:4342 igVal:4343 eraIdx:4344 playerAtWar:4345 influenceRowsBase:4346 influenceRows:4376 influenceTotal:4381 poModRows:4384 totTipSimple:4406 totTip:4409 epSources:4420 topSuz:4432 royalMarriage:4435 sameAlliance:4440 poFloor:4443 applyPOFloor:4444 epRows:4445 poModTotal:4458 dpButtons:4459 renderDP:4462 renderMiniStand:4470 renderInfluence:4483 renderPOMods:4486 siegeState:4494 siegeCalc:4495 siegeHTML:4512 realmTimers:4527 timerAddHTML:4528 boardTimerRows:4532 siegeResolveHTML:4538 activeTimersHTML:4544 timersHTML:4550 seasonsHTML:4556 costsHTML:4559 wireDashExtras:4562 renderDash:4590 domBand:4625 standingsBoardHTML:4626 mods:4666 diplo:4671 pk:4672 isVassal:4674 vassalsOf:4675 effPair:4676 pairOf:4679 pname:4680 allianceLabel:4681 pboard:4682 hasRoad:4683 eraRank:4686 allianceEra:4687 allianceOK:4688 pairFlags:4689 dStatus:4696 diploHTML:4700 wireDiplo:4756 newSide:4788 battle:4789 bq:4791 bqAdd:4792 bqSideName:4793 bqLoad:4796 sideHex:4799 bqStart:4803 banditArmy:4806 armBandits:4810 sideArmy:4815 blog:4820 d10:4821 seizeForced:4822 facCombat:4825 sideUnlocks:4837 sideDomains:4841 standingFxOf:4842 hasTiltyard:4846 eqOptions:4847 eqCode:4856 eqNow:4859 eqWeapon:4862 tacAllowed:4870 tacOK:4875 randomTacticPool:4876 sideCalc:4879 pickKey:4989 viewerSide:4990 mdLite:5012 fmtModLong:5014 fmtMod:5017 dieRow:5019 rollHTML:5020 sideHTML:5028 tacEdge:5116 tacticExplainHTML:5119 battleRulesHTML:5131 renderBattle:5138 incoming:5164 roll:5167 ripN:5223 addRip:5224 setPendCas:5225 pendCas:5226 applyCas:5227 endSkirmish:5228 endBattle:5244 wireBattle:5260 edictTimerLen:5308 edictChoices:5310 edictTotal:5316 edictOwners:5317 bumpRenown:5318 edictBoardHTML:5319 wireEdicts:5347 currentEra:5361 standingEffectsHTML:5366 renderRenown:5381 mapClimate:5442 mapPal:5447 tLum:5450 tTone:5452 tLighten:5453 tGlyph:5456 tSwatch:5461 mapState:5468 hexDist:5469 decodeGrid:5472 seedCode:5482 generateMap:5483 parseSeedCode:5491 mapZoom:5502 reachBonus:5508 reachOwners:5517 reachResources:5529 rawReachStatus:5538 mapSprId:5546 mapSprDefs:5547 tMix:5556 hStr:5561 rng32:5562 mapScatter:5563 mapSpr:5580 eqSVG:5586 sprSVG:5588 stIcon:5596 armyGear:5597 armyUFor:5599 armyStatLine:5600 cellArmyVals:5601 mapPlate:5604 settBehind:5619 settInsideMarks:5623 mapBarHTML:5638 terrOwners:5649 terrFlags:5651 unrestCamps:5657 intrudersOf:5659 settReach:5663 settEcon:5665 pillageCheck:5674 pillageTargets:5678 runPillage:5681 armyStatus:5688 mapMarkers:5701 inspHTML:5712 inspHead:5715 inspCell:5718 g:5719 inspCan:5720 inspArmy:5721 settStatus:5741 settStatusMarks:5751 inspSett:5756 inspCamp:5782 engageTargets:5794 wireInsp:5800 mapSVG:5818 outlawReport:5903 banditDomain:5914 banditAutoHTML:5915 armyName:5924 syncMapTiers:5926 mapLinkBad:5932 mapLinksHTML:5933 wireBanditAuto:5944 banditAuto:5950 BST:5951 bLog:5952 hk:5954 mapSetts:5955 cellPlayer:5956 cellSett:5958 mapArmies:5961 cellArmy:5962 cellTitle:5965 byDist:5969 outlawOwner:5970 outlawOf:5971 hexFree:5972 spawnCamp:5973 growCamps:5975 expandOutlaw:5978 immuneUprising:5981 banditTargetMods:5982 cunningAction:5984 endorsedExtort:5985 banditAct:5986 runBanditMechanics:6008 banditSpeed:6022 banditAuraList:6024 banditRun:6031 moveCamp:6039 banditSiegeTimer:6040 banditMoves:6042 banditSkims:6070 creditSkims:6075 envoyOutcome:6081 banditCunningHTML:6086 dieLookup:6103 terrainTablesHTML:6106 mapToolsHTML:6127 banditPanelHTML:6160 mapAsP:6176 mapEditBlock:6177 mapGuard:6186 guarded:6188 wireMap:6189 srcText:6242 srcMatch:6249 srcHas:6250 bordersOf:6253 poCap:6257 poTextFloor:6258 siegeTextMods:6261 siegeWinterOK:6268 actRestrict:6270 actRiders:6278 settById:6288 besiegeExempt:6290 settBesieged:6291 armySieging:6293 armyBesieged:6295 armyStateTags:6296 armyBlocked:6305 garrisonSizes:6308 hasGarrisons:6311 garrisonGear:6313 garrisonOf:6314 garrisonsOf:6318 garrisonCard:6319 onceEffects:6348 onceState:6351 onceHTML:6353 wireOnce:6359 noteAdd:6366 recoupNote:6368 extortGold:6377 danegeldRows:6386 autoExtortRows:6391 runAutoExtort:6399 firstDoubtRed:6416 gainDoubt:6420 siegeOn:6426 besiegedCount:6427 pById:6428 nextId:6429 captureTransfer:6430 sackApply:6440 resolveRealm:6451 sackLocks:6456 armyHex:6460 settHex:6461 musterLimit:6462 musterTick:6468 hasMusterField:6476 charterFlags:6479 selArmy:6502 canMoveArmy:6503 canEnterSett:6505 armyInside:6507 enterCheck:6510 freeHexNear:6512 kickOut:6515 armiesInside:6518 terrPen:6520 terrBlocked:6521 terrWaterStop:6522 terrStrain:6523 spClauses:6525 spVal:6526 provinceOf:6527 moveTraits:6529 speedOf:6534 hexNb:6562 auraSources:6566 moveRange:6575 moveInfo:6606 moveStops:6609 moveArmyTo:6613 moveOverlay:6629 movePanelHTML:6642 set:6653 computeAll:6654 sceneInfra:6669 wardChains:6675 sceneLots:6682 renderEsBar:6693 sceneArmies:6698 renderScene:6704 renderSettlements:6808 lockTarget:6871 lockBlock:6880 adminUI:6897 firstHostOpen:6913 firstHostBtn:6914 hudSign:6921 hudData:6922 renderHUD:6929 ageStripHTML:6962 setupOn:6976 renderSetup:6977 renderTurnStrip:6994 syncBoardEndBtn:7026 mnavSync:7042 undoSnap:7050 undoRecord:7052 undoRebase:7058 undoScoped:7059 undoApply:7060 doUndo:7073 doRedo:7074 undoButtons:7075 actSnap:7088 actRebase:7089 actJoin:7091 actSchedule:7094 fmtG:7095 boardDiff:7096 actFlush:7128 activityHtml:7141 gameAllowed:7150 gameData:7151 refreshGames:7152 gameReplace:7155 newGameState:7159 isReady:7182 readyCheck:7183 gslug:7196 kwify:7208 wikiA:7219 gkHtml:7220 openFromHash:7237 setLift:7263 gkShow:7272 gkHide:7276 gkFor:7277 chatHdr:7335 chatTargets:7341 chatParse:7343 chatColor:7351 chatLine:7352 chatRender:7356 chatSys:7362 chatComplete:7377
```
