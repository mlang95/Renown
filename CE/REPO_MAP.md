# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-10-09 · data VERSION `0.4.9.9.11-d10-SIMPLE` · HEAD `65cde17 2026-10-09`

Hand-written orientation: `CLAUDE.md` (same folder). Paths below are relative to the repo root.

## 1. Folder tree

```
./  (11 files)
  0.4.8 Updated Docs/  (7 files)
  0.4.8.1/  (36 files)
  Assets/  (102 files, generated/assets — not indexed)
  CE/  (25 files)
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
| `CE\REPO_MAP.md` | 814 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
| `CE\RULES_push.md` | 649 | Renown |
| `CE\RULES_push_simple.md` | 724 | Renown |
| `CE\RULES_reorganized_6.md` | 638 | Renown |
| `CE\build_all_CE.bat` | 506 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE\ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE\parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE\patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE\rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE\renown_data.py` | 4475 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d10.py` | 4475 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_data_d8.py` | 2801 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE\renown_server.bat` | 16 | renown_server.bat - (re)start the Renown board server in WSL. |
| `CE\repo_map.py` | 242 | repo_map.py — write REPO_MAP.md next to this file (CE/, beside CLAUDE.md): a generated index of the Renown repo for |
| `CE\run_tournament_d10.bat` | 108 | Renown d10 tournament runner  —  CE build |
| `CE\run_tournament_d10.py` | 131 | run_tournament_d10.py — run the Renown tournament against the d10 build. |
| `CE\sprites.py` | 1612 | sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene). |
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
| `CE\ask-the-bot\factions_table.csv` | 42 | columns: Faction,Difficulty,Strength,Mechanic |
| `CE\ask-the-bot\renown_faq.txt` | 491 |  |
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
| `CE\references\docx_tables.py` | 537 | docx_tables.py — generate Word table fragments (OOXML) from renown_data. |
| `CE\references\domain_board.py` | 321 | domain_board.py - landscape Domain Standing Board. |
| `CE\references\equipment_sheet.py` | 691 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `CE\references\faction_sheet.py` | 447 | Renown — Faction card sheet generator. |
| `CE\references\faq_export.py` | 446 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `CE\references\gen_compendium.py` | 184 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `CE\references\gen_layout.py` | 374 | gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data. |
| `CE\references\gen_layout_roots.py` | 123 | gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it. |
| `CE\references\gen_settlement_board.py` | 6718 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE\references\generate_cards.py` | 93 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `CE\references\host_sheet.py` | 452 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `CE\references\infra_board.py` | 130 | infra_board.py - landscape Infrastructure Board. |
| `CE\references\layout.json` | 1421 |  |
| `CE\references\layout_roots.json` | 1328 |  |
| `CE\references\layout_simple.json` | 1501 |  |
| `CE\references\md_to_docx.py` | 329 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `CE\references\package-lock.json` | 205 |  |
| `CE\references\package.json` | 6 |  |
| `CE\references\patch_pursuit_domains.py` | 58 | patch_pursuit_domains.py |
| `CE\references\playstyle_reference.py` | 396 | playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture). |
| `CE\references\pursuit_tiles.py` | 282 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `CE\references\reference_sheets.py` | 891 | Renown — Reference sheet generators. |
| `CE\references\render_tree.py` | 272 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `CE\references\server.py` | 329 | Renown settlement-board server  —  stdlib only, no pip installs. |
| `CE\references\settlement_board.html` | — | generated HTML (1084 KB) |
| `CE\references\settlement_mats.py` | 293 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `CE\references\spec_tree_sheet.py` | 1183 | Renown — Specialization Tree renderer. |
| `CE\references\svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `CE\references\sync_derived.py` | 116 | sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES. |
| `CE\references\tactic_sheet.py` | 446 | Renown — Tactic card sheet generator (v3). |
| `CE\references\wiki_markers.py` | 287 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
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
| `RenownWiki\rules-territory-terrain.html` | 25 | Territory &amp; Terrain — Renown |
| `RenownWiki\rules-the-turn.html` | 106 | The Turn — Renown |
| `RenownWiki\rules-trade-income.html` | 36 | Trade &amp; Income — Renown |
| `RenownWiki\rules-treasury-upkeep.html` | 32 | Treasury &amp; Upkeep — Renown |
| `RenownWiki\search.js` | 7 |  |
| `RenownWiki\seasons-ref.html` | 19 | Seasons — Renown |
| `RenownWiki\settlement_board.html` | — | generated HTML (1084 KB) |
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
| `VERSION` | 6 | str | '0.4.9.9.11-d10-SIMPLE' |
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
| `GLOSSARY` | 114 | dict | 155 |
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
| `CULTURES` | 457 | dict | 15 |
| `FACTION_SUMMARIES` | 601 | dict | 40 |
| `NODES` | 651 | dict | 118 |
| `SIMPLE_NODES` | 1685 | dict | 118 |
| `HOLDING_GROUPS` | 2540 | dict | 9 |
| `LINE_LABELS` | 2554 | dict | 28 |
| `lines_of` | 2585 | function |  |
| `LEGACY_NODES` | 2589 | dict | 108 |
| `REQ_KEY` | 2594 | str | 'infrastructure_req' |
| `REQ_LABEL` | 2595 | str | 'Infrastructure Req' |
| `TYPE_ORDER` | 2597 | list | 10 |
| `CHAIN_TERM` | 2600 | str | 'Mastery Chain' |
| `PURSUIT_TERM` | 2602 | tuple | 2 |
| `node_parents` | 2604 | function |  |
| `get_data` | 2624 | function |  |
| `FACTIONS` | 2634 | dict | 40 |
| `INFRASTRUCTURE` | 3042 | dict | 12 |
| `WONDERS` | 3119 | dict | 4 |
| `SETTLEMENTS` | 3152 | dict | 5 |
| `ERAS` | 3161 | dict | 4 |
| `PUBLIC_ORDER` | 3174 | dict | 12 |
| `PO_MODIFIERS` | 3197 | dict | 2 |
| `DOMAIN_BOARD` | 3215 | dict | 6 |
| `SEASONS` | 3246 | dict | 4 |
| `TRADE_RULES` | 3254 | dict | 4 |
| `efficient_graph` | 3266 | function |  |
| `EFFICIENT_MULTI` | 3276 | dict | 109 |
| `EFFICIENT` | 3277 | dict | 109 |
| `BANDIT_CAMP_START` | 3285 | int | 5 |
| `BANDIT_ARMY_THRESHOLD` | 3286 | int | 25 |
| `BANDIT_GROWTH_PER_ERA` | 3287 | dict | 4 |
| `BANDIT_EQUIPMENT_PER_ERA` | 3288 | dict | 4 |
| `BANDITS` | 3289 | dict | 5 |
| `TIMERS` | 3297 | dict | 8 |
| `CHARTER_MIN_RANGE` | 3309 | int | 4 |
| `OUTLAW_BUFFER_RANGE` | 3310 | int | 2 |
| `HAMLET_RANGE` | 3311 | int | 2 |
| `OUTLAW_COUNTRY_START` | 3312 | int | 3 |
| `VASSAL_EXCHANGE_CAP` | 3315 | int | 5000 |
| `VASSAL_INFLUENCE_TAKE` | 3316 | int | 3 |
| `BUILD_TIMERS` | 3320 | dict | 11 |
| `TERRAIN` | 3334 | dict | 7 |
| `MOVEMENT_MODIFIERS` | 3344 | dict | 6 |
| `TACTICAL_TERRAIN` | 3356 | dict | 7 |
| `TACTICAL_GLOBAL` | 3372 | list | 1 |
| `INFLUENCE_GAIN` | 3374 | dict | 10 |
| `ENVOY_OUTCOME_THRESHOLDS` | 3428 | dict | 4 |
| `ENVOY_OUTCOMES` | 3437 | dict | 5 |
| `ACTIONS` | 3459 | dict | 22 |
| `TREATIES` | 3649 | dict | 5 |
| `ALLIANCE_RULES` | 3657 | list | 3 |
| `EDICT_STREAK_TURNS` | 3667 | int | 5 |
| `EDICTS` | 3669 | dict | 7 |
| `BANDIT_BEHAVIOR` | 3683 | dict | 7 |
| `PURSUIT_UPKEEP_DEFAULT` | 3706 | int | 100 |
| `PURSUIT_UPKEEP_BY_TYPE` | 3707 | dict | 4 |
| `UPKEEP_TRACKS` | 3717 | dict | 3 |
| `HOLDING_TIER_COST` | 3724 | dict | 4 |
| `holding_standing` | 3732 | function |  |
| `holding_cost` | 3738 | function |  |
| `holding_build_time` | 3746 | function |  |
| `pursuit_upkeep` | 3753 | function |  |
| `ARMY_UPKEEP_NOTE` | 3764 | str | "Net Army Upkeep = the sum of each Army' |
| `COSTS` | 3768 | dict | 12 |
| `PHASES` | 3784 | tuple | 5 |
| `STARTING_TURN_PHASE_OPENER` | 3785 | str | 'Council' |
| `STANDING_ARMY_SIEGE_MODIFIER` | 3787 | int | 1 |
| `EMPIRE_START_TIERS` | 3789 | tuple | 2 |
| `STARTING_TREASURY` | 3790 | int | 10000 |
| `AGES` | 3796 | dict | 5 |
| `AGE_YEAR_SEASON` | 3803 | str | 'Spring' |
| `CAPITAL_EDGE_RANGE` | 3804 | int | 4 |
| `BOARD_SIZES` | 3806 | dict | 3 |
| `SIEGE_CALCULUS` | 3812 | dict | 2 |
| `SIEGE_SOURCE_VALUES` | 3827 | dict | 6 |
| `NAME_DISPLAY` | 3854 | dict | 62 |
| `TIER_DISPLAY` | 3881 | dict | 1 |
| `ITEM_TIER_DISPLAY` | 3887 | dict | 1 |
| `TERM_ENVOY_SCORE` | 3894 | str | 'Authority' |
| `display_score` | 3902 | function |  |
| `ALIASES` | 3912 | dict | 64 |
| `display` | 3922 | function |  |
| `display_tier` | 3927 | function |  |
| `display_text` | 3935 | function |  |
| `display_list` | 3958 | function |  |
| `display_md` | 3968 | function |  |
| `display_html` | 3975 | function |  |
| `display_obj` | 3987 | function |  |
| `undisplay` | 4000 | function |  |
| `verify_aliases` | 4009 | function |  |
| `BANDIT_FACES` | 4033 | int | 10 |
| `BANDIT_CUNNING_MIN` | 4034 | int | 10 |
| `die_table_ranges` | 4037 | function |  |
| `die_table_rows` | 4045 | function |  |
| `die_table_text` | 4053 | function |  |
| `die_table_lookup` | 4061 | function |  |
| `die_table_verify` | 4068 | function |  |
| `die_table_weights` | 4087 | function |  |
| `BANDIT_CUNNING_TABLE` | 4097 | dict | 5 |
| `bandit_cunning_ranges` | 4105 | function |  |
| `bandit_cunning_rows` | 4106 | function |  |
| `bandit_cunning_lookup` | 4107 | function |  |
| `bandit_cunning_text` | 4109 | function |  |
| `BANDIT_TACTIC_TABLE` | 4115 | dict | 6 |
| `BANDIT_TACTICS` | 4123 | list | 6 |
| `bandit_tactic_ranges` | 4125 | function |  |
| `bandit_tactic_rows` | 4126 | function |  |
| `bandit_tactic_lookup` | 4127 | function |  |
| `verify_bandit_tables` | 4130 | function |  |
| `RENOWN_MAX` | 4218 | int | 30 |
| `RENOWN_PER_TURN` | 4219 | int | 1 |
| `DOMAIN_POINTS_PER_TURN` | 4220 | int | 1 |
| `FACTION_NAMES` | 4441 | dict | 40 |
| `faction_body` | 4448 | function |  |
| `GLOSSARY_CATEGORIES` | 4457 | list | 17 |

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
- **{{VAL}}** (83): `AGE_YEAR_SEASON`, `ARMY_MAX_RETINUES`, `BANDITS.Bandit Domain Value`, `BANDIT_ARMY_THRESHOLD`, `BANDIT_CAMP_START`, `BANDIT_CUNNING_MIN`, `BANDIT_FACES`, `BLUNDER_THR`, `CAPITAL_EDGE_RANGE`, `CAP_THR`, `CHARTER_MIN_RANGE`, `DICE_PROVENANCE`, `DOMAIN_BOARD.innate_influence_own_envoys.Established`, `DOMAIN_BOARD.innate_influence_own_envoys.Rising`, `DOMAIN_BOARD.innate_influence_own_envoys.Sovereign`, `DOMAIN_BOARD.innate_influence_own_envoys.Untested`, `DOMAIN_BOARD.max_influence_per_vote.Established`, `DOMAIN_BOARD.max_influence_per_vote.Rising`, `DOMAIN_BOARD.max_influence_per_vote.Sovereign`, `DOMAIN_BOARD.max_influence_per_vote.Untested`, `DOMAIN_POINTS_PER_TURN`, `ENDURANCE_REGAIN`, `ERAS.Ascension.innate_diplomacy_influence`, `ERAS.Ascension.max_influence_per_diplomacy_vote`, `ERAS.Eminence.innate_diplomacy_influence`, `ERAS.Eminence.max_influence_per_diplomacy_vote`, `ERAS.Founding.innate_diplomacy_influence`, `ERAS.Founding.max_influence_per_diplomacy_vote`, `ERAS.Founding.renown`, `ERAS.Zenith.innate_diplomacy_influence`, `ERAS.Zenith.max_influence_per_diplomacy_vote`, `FACES`, `FATIGUE_MORALE`, `FOCUSED_THR`, `FRONT_LINE_MAX`, `HAMLET_RANGE`, `INITIATIVE_MAX`, `INITIATIVE_MIN`, `MORALE_DICE_MAX`, `OUTLAW_BUFFER_RANGE`, `OUTLAW_COUNTRY_START`, `PANIC_CASUALTY_THRESHOLD`, `PARRY_BASE`, `PO_MAX`, `PO_MIN`, `PURSUIT_UPKEEP_BY_TYPE.Energy`, `PURSUIT_UPKEEP_BY_TYPE.Monument`, `PURSUIT_UPKEEP_BY_TYPE.Other`, `PURSUIT_UPKEEP_BY_TYPE.Power`, `RENOWN_PER_TURN`, `RESERVE_MAX`, `RETINUES.Knight Templar.cost`, `RETINUES.Knight Templar.to_hit`, `RETINUES.Levy.cost`, `RETINUES.Levy.to_hit`, `RETINUES.Man-at-Arms.cost`, `RETINUES.Man-at-Arms.to_hit`, `RETINUES.Sergeant.cost`, `RETINUES.Sergeant.to_hit`, `ROUT_THR`, `SACK_EXTORT_PER_TIER`, `SETTLEMENTS.City.wards`, `SETTLEMENTS.Hamlet.wards`, `SETTLEMENTS.Metropolis.reach`, `SETTLEMENTS.Metropolis.wards`, `SETTLEMENTS.Town.wards`, `SETTLEMENTS.Village.reach`, `SETTLEMENTS.Village.wards`, `SIEGE_CALCULUS.Lay Siege.floor`, `SIEGE_SOURCE_VALUES.Stone Walls.value`, `SIEGE_SOURCE_VALUES.Wooden Walls.value`, `STANDING_THRESHOLDS.Established`, `STANDING_THRESHOLDS.Rising`, `STANDING_THRESHOLDS.Sovereign`, `STANDING_THRESHOLDS.Untested`, `STARTING_TREASURY`, `STARTING_TURN_PHASE_OPENER`, `TIMERS.Capture Timer.default`, `TIMERS.Sack Timer.default`, `TRADE_RULES.income_per_craft`, `VASSAL_EXCHANGE_CAP`, `VASSAL_INFLUENCE_TAKE`, `WEALTH_EDICT_GOLD`
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
| 640 | ### Spawning Bandit Camps |
| 646 | ### Growing Bandit Camps |
| 650 | ### Bandit Armaments by Era |
| 654 | ### Bandit Growth by Era |
| 658 | ### Bandit Info |
| 676 | ### Bandit Army Behavior |
| 688 | ### Attacking a Bandit Camp |
| 694 | # Holdings |
| 698 | # Equipment |
| 700 | ## Melee Weapons |
| 704 | ## Ranged Weapons |
| 708 | ## Shields |
| 712 | ## Armor |
| 718 | # Factions |
| 722 | # Index |

## 6. Settlement board — `CE\references\gen_settlement_board.py`

Payload keys passed to the HTML as `DATA` (58): `records`, `naturalNames`, `externalTokens`, `simple`, `chainTerm`, `pursuitTerm`, `infra`, `wonders`, `armySrc`, `equip`, `glossary`, `domainBoard`, `publicOrder`, `wikiBase`, `wikiHome`, `tree`, `rulebook`, `limits`, `eras`, `edicts`, `envoyOutcomes`, `outcomeThresh`, `startPhase`, `actions`, `phaseRules`, `phaseSteps`, `rulesConst`, `ages`, `domains`, `standings`, `tradePerCraft`, `noTradeSeason`, `renownPerTurn`, `dpPerTurn`, `settlements`, `battle`, `terrainRef`, `banditLoadouts`, `bandits`, `treaties`, `allianceRules`, `startTiers`, `startTreasury`, `pursuitUpkeep`, `buildTimers`, `timers`, `seasons`, `poModifiers`, `vassalInfluenceTake`, `aliases`, `scoreTerm`, `costs`, `influenceGain`, `siege`, `factions`, `warnings`, `version`, `sprites`

Python: `load`:27, `strip_md`:34, `has_cond`:76, `to_int`:79, `classify`:82, `_iv`:149, `envoy_fx`:150, `combine_parts`:231, `combine_effects`:272, `rules_payload`:276, `tree_payload`:334, `parse_effects`:368, `parse_mreq`:374, `classify_req_token`:382, `build`:391, `font_faces`:532, `_pursuit_term_template`:557, `render_html`:565, `_style_js`:573, `sprite_payload`:584, `find_mapgen`:606, `check_rules`:6395, `_val`:6513, `rules_section`:6522, `phase_steps`:6541, `battle_data`:6555, `bandit_loadouts`:6575, `main`:6623

JS sections: TABLE: seating, Council & Envoy phases :1369,  :4215, EFFECT PLUMBING: read rule text on a player's active pieces + faction :5375, ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS :5422, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :5506, UNDO / REDO :6090, ACTIVITY LOG :6128, GAME: save · load · new :6192, HOVER KEYWORDS :6238

JS functions (573, name:line):

```
fixBastard:1336 dispScore:1343 tnow:1380 noteServerDate:1381 lockOn:1389 claimOf:1390 mine:1391 myClaimP:1392 canEdit:1393 boardEndOn:1395 TB:1396 tSeats:1397 tTimer:1398 tTurn:1399 tPhase:1400 PT:1402 tCur:1403 tCurW:1404 sameP:1405 meP:1406 canAct:1407 seatMap:1410 seated:1414 isSpring:1415 hostP:1416 voteOrd:1418 tOrder:1419 canHost:1420 seatsLocked:1421 tStand:1424 eraRec:1425 diploInf:1426 diploCap:1427 eraActions:1428 boardFx:1431 fxOf:1443 scopeOk:1444 sgn:1445 fxLabel:1446 atWarPair:1458 opposeBlock:1459 innateParts:1463 modSum:1469 innateInf:1471 voteCap:1472 inflPool:1475 personalEnvoys:1476 councilEnvoys:1477 tOutcome:1478 outText:1480 tPlan:1483 domStarted:1497 tSim:1500 performEval:1564 failPassFx:1575 actionsOf:1576 actReqFlag:1578 actInfoHTML:1582 tApply:1589 tSetPhase:1601 tEndTurn:1603 tAutoSeat:1618 tSig:1624 tName:1626 tVoteTxt:1627 envBadges:1628 innateTxt:1634 tOutCls:1636 tHistHtml:1637 tPerformHtml:1649 empireChecklistHTML:1669 treeSave:1679 treeHTML:1686 rulebookHTML:1750 linkifyRules:1753 renderReference:1757 renderTable:1769 tPanel:1840 tWire:1938 tCountdown:1985 applyTheme:2000 applySkin:2012 startDoms:2018 ageRec:2021 ageRisingOf:2022 startDomsFor:2023 startDomTotal:2024 curYear:2025 applyAgeStart:2026 startSettlements:2028 startSig:2031 reseedIfPristine:2033 newBoard:2038 newPlayer:2040 normalizeD:2056 activeBoard:2076 reindex:2077 pActive:2090 flagState:2093 ignBtn:2098 ignNote:2101 unlockStatus:2107 nameHit:2118 missTxt:2119 recomputePC:2121 buildTimerMod:2126 withBuildMod:2130 pursuitBaseTime:2131 infraBaseTime:2132 pursuitBuildTime:2133 infraBuildTime:2134 buildNote:2135 settBaseTime:2136 settBuildTime:2137 itm:2138 infraOn:2139 gameStarted:2140 empTimers:2144 empEconomy:2145 empPO:2149 empArmies:2154 endRow:2157 boardEndTurn:2160 tickRealm:2163 empirePhase:2165 tickTimers:2187 facTypeBonus:2195 pursuitUpkeep:2197 withBoard:2200 setOnline:2216 clone:2226 jeq:2227 isObj:2228 merge3:2230 splitD:2239 joinD:2245 save:2269 editing:2306 cvar:2326 fmt:2327 cap:2328 settMeta:2331 settTier:2332 occupants:2333 hamletOK:2334 hamletRoot:2337 hamletFits:2338 effList:2345 effLabel:2350 exemptionsOf:2351 wardExemptions:2360 isFreeRider:2361 wardUse:2362 canPlace:2373 capitalSett:2391 setCapital:2392 isCityPlus:2394 dbActive:2395 capBonus:2399 eraCapBase:2400 eraCap:2401 capSrc:2402 cityCount:2403 eraAllows:2405 rslug:2413 boardFlags:2414 hasMetropolis:2436 onBoard:2437 nextTier:2438 autoFill:2440 buildFilters:2461 catSave:2470 catFor:2473 pAvail:2477 iAvail:2478 catUpkeep:2479 seg:2480 renderList:2482 pursuitRow:2532 sub:2543 tip:2545 itemRow:2546 flash:2554 addInfraByName:2556 addItem:2559 removeInstance:2587 removeOneByName:2588 addByName:2593 addPursuitByName:2594 moveInstance:2595 infraReqToks:2610 infraTokStatus:2616 infraReqStatus:2630 infraValid:2635 infraActive:2642 infraReqLinesHTML:2643 masteryInfraToks:2647 masteryInfraHTML:2648 annotReqTok:2655 optionMet:2660 reqStatus:2668 instStatus:2675 chainLine:2682 simpleReq:2691 simpleReqHTML:2703 computeEarned:2711 atomEl:2729 atomsBlock:2738 render:2751 renderTopBar:2804 toggleEmpty:2844 settBar:2847 sfxNorm:2861 sfxLabel:2862 settFx:2871 settFxPanel:2894 renderPursuitBoard:2901 wardPiles:3013 wardGrid:3025 unitFor:3052 tryMove:3057 scrollHost:3090 dropTargetAt:3091 clearDropHL:3099 armDrag:3100 beginDrag:3117 dragMove:3131 dragEnd:3143 factionFree:3153 setFaction:3157 facGearFlags:3166 factionFlags:3172 facSelectHTML:3183 renderFaction:3187 timerCtl:3194 placementSelect:3199 contribAcc:3214 contribChips:3217 accChips:3218 pursuitDetail:3226 quickChip:3250 buildsIntoRow:3254 nextLinksSummary:3256 nextLinksHTML:3258 pursuitTable:3266 pursuitCard:3293 renderInfraSection:3380 armyUnlocks:3425 unlockedShieldTiers:3457 tierOK:3461 gloss:3462 glossLookup:3471 openModal:3480 closeModal:3484 kwChipHTML:3485 esc:3486 inspectKeyword:3487 inspectItem:3509 optionList:3532 renderArmy:3546 armyCard:3579 reqMet:3691 weaponUnlockMet:3694 moraleBase:3696 armyUpkeep:3697 moraleCap:3699 effMorale:3701 isRouted:3702 armyStats:3704 noUpkeepTiers:3736 holdsActive:3738 playersWithout:3740 calcMetrics:3742 computeTotals:3796 poTaxMod:3824 taxDouble:3829 winterTax:3830 settTax:3836 tradeIncome:3839 tradeRaw:3845 seasonNet:3853 husbandryGoldFor:3857 SEASON_DBL_TYPE:3859 boardMetrics:3860 poBandName:3867 poActiveKeys:3869 poActiveEffects:3871 poImmune:3878 poDoubled:3879 renderPO:3881 curSeason:3901 stepSeason:3902 playerOfBoard:3905 igVal:3906 eraIdx:3907 playerAtWar:3908 influenceRowsBase:3909 influenceRows:3939 influenceTotal:3944 poModRows:3947 totTip:3966 epSources:3977 topSuz:3989 royalMarriage:3992 sameAlliance:3997 poFloor:4000 applyPOFloor:4001 epRows:4002 poModTotal:4015 dpButtons:4016 renderDP:4019 renderMiniStand:4026 renderInfluence:4039 renderPOMods:4042 siegeState:4050 siegeCalc:4051 siegeHTML:4068 realmTimers:4083 timerAddHTML:4084 boardTimerRows:4088 siegeResolveHTML:4094 activeTimersHTML:4099 timersHTML:4105 seasonsHTML:4111 costsHTML:4114 wireDashExtras:4117 renderDash:4141 domBand:4176 standingsBoardHTML:4177 mods:4217 diplo:4222 pk:4223 isVassal:4225 vassalsOf:4226 effPair:4227 pairOf:4230 pname:4231 allianceLabel:4232 pboard:4233 hasRoad:4234 eraRank:4237 allianceEra:4238 allianceOK:4239 pairFlags:4240 dStatus:4247 diploHTML:4251 wireDiplo:4307 newSide:4339 battle:4340 banditArmy:4342 armBandits:4346 sideArmy:4351 blog:4356 d10:4357 seizeForced:4358 facCombat:4361 sideUnlocks:4373 sideDomains:4377 standingFxOf:4378 hasTiltyard:4382 eqOptions:4383 eqCode:4392 eqNow:4395 eqWeapon:4398 tacAllowed:4406 tacOK:4411 randomTacticPool:4412 sideCalc:4415 pickKey:4525 viewerSide:4526 mdLite:4548 fmtModLong:4550 fmtMod:4553 dieRow:4555 rollHTML:4556 sideHTML:4564 battleRulesHTML:4651 renderBattle:4658 incoming:4680 roll:4683 ripN:4739 addRip:4740 setPendCas:4741 pendCas:4742 applyCas:4743 endSkirmish:4744 endBattle:4760 wireBattle:4775 edictTimerLen:4820 edictChoices:4822 edictTotal:4828 edictOwners:4829 bumpRenown:4830 edictBoardHTML:4831 wireEdicts:4859 currentEra:4873 standingEffectsHTML:4878 renderRenown:4893 mapClimate:4954 mapPal:4959 tLum:4962 tTone:4964 tLighten:4965 tGlyph:4968 tSwatch:4973 mapState:4980 hexDist:4981 decodeGrid:4984 seedCode:4994 generateMap:4995 parseSeedCode:5003 mapZoom:5012 reachBonus:5018 reachOwners:5027 reachResources:5039 rawReachStatus:5046 mapSVG:5052 outlawReport:5116 banditDomain:5127 banditAutoHTML:5128 armyName:5137 mapLinkBad:5138 mapLinksHTML:5139 wireBanditAuto:5150 BST:5154 bLog:5155 hk:5156 mapSetts:5157 cellPlayer:5158 cellSett:5160 mapArmies:5163 cellArmy:5164 cellTitle:5167 byDist:5170 outlawOwner:5171 outlawOf:5172 hexFree:5173 spawnCamp:5174 growCamps:5176 expandOutlaw:5179 immuneUprising:5182 banditTargetMods:5183 cunningAction:5185 endorsedExtort:5186 banditAct:5187 runBanditMechanics:5209 banditSkims:5220 creditSkims:5225 envoyOutcome:5229 banditCunningHTML:5234 dieLookup:5251 terrainTablesHTML:5254 mapToolsHTML:5275 banditPanelHTML:5308 mapAsP:5324 mapEditBlock:5325 wireMap:5336 srcText:5377 srcMatch:5384 srcHas:5385 bordersOf:5388 poCap:5392 poTextFloor:5393 siegeTextMods:5396 siegeWinterOK:5403 actRestrict:5405 actRiders:5413 settById:5423 besiegeExempt:5425 settBesieged:5426 armySieging:5428 armyBesieged:5430 armyStateTags:5431 armyBlocked:5439 garrisonSizes:5442 hasGarrisons:5445 garrisonGear:5447 garrisonOf:5448 garrisonsOf:5452 garrisonCard:5453 onceEffects:5482 onceState:5485 onceHTML:5487 wireOnce:5493 recoupNote:5501 extortGold:5510 danegeldRows:5519 autoExtortRows:5524 runAutoExtort:5532 firstDoubtRed:5549 gainDoubt:5553 siegeOn:5559 besiegedCount:5560 pById:5561 nextId:5562 captureTransfer:5563 sackApply:5573 resolveRealm:5584 sackLocks:5589 armyHex:5593 settHex:5594 musterLimit:5595 musterTick:5601 hasMusterField:5609 charterFlags:5612 terrPen:5636 terrBlocked:5637 terrWaterStop:5638 terrStrain:5639 spClauses:5641 spVal:5642 provinceOf:5643 moveTraits:5645 speedOf:5650 hexNb:5678 moveRange:5680 moveInfo:5694 moveArmyTo:5696 moveOverlay:5701 movePanelHTML:5708 set:5719 computeAll:5720 sceneInfra:5735 wardChains:5741 sceneLots:5748 renderScene:5758 renderSettlements:5853 lockTarget:5916 lockBlock:5925 adminUI:5942 firstHostOpen:5958 firstHostBtn:5959 hudSign:5966 hudData:5967 renderHUD:5974 ageStripHTML:6006 setupOn:6020 renderSetup:6021 renderTurnStrip:6038 syncBoardEndBtn:6070 mnavSync:6086 undoSnap:6094 undoRecord:6096 undoRebase:6102 undoScoped:6103 undoApply:6104 doUndo:6117 doRedo:6118 undoButtons:6119 actSnap:6132 actRebase:6133 actJoin:6135 actSchedule:6138 fmtG:6139 boardDiff:6140 actFlush:6172 activityHtml:6185 gameAllowed:6194 gameData:6195 refreshGames:6196 gameReplace:6199 newGameState:6203 isReady:6226 readyCheck:6227 gslug:6240 kwify:6252 wikiA:6263 gkHtml:6264 openFromHash:6281 setLift:6307 gkShow:6316 gkHide:6320 gkFor:6321
```
