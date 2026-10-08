# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)

Generated 2026-10-08 · data VERSION `0.4.9.9.10-d10-SIMPLE` · HEAD `74fa5ad 2026-10-08`

Hand-written orientation: `CLAUDE.md`. This file is derived from the files themselves.

## 1. Folder tree

```
./  (12 files)
  0.4.8 Updated Docs/  (7 files)
  0.4.8.1/  (36 files)
  Assets/  (102 files, generated/assets — not indexed)
  CE/  (22 files)
    Combatv4/  (18 files)
      shims/  (6 files)
    ask-the-bot/  (3 files)
    lab_out/  (419 files, generated/assets — not indexed)
    mapgen/  (17 files)
      maps/  (20 files)
    references/  (49 files)
      fonts/  (14 files, generated/assets — not indexed)
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
| `CLAUDE.md` | 64 | CLAUDE.md — Renown repo orientation |
| `REPO_MAP.md` | 636 | REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`) |
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
| `CE/COMPREHENSIVE_RULES_OUTLINE.md` | 181 | Renown — Comprehensive Rules: outline |
| `CE/RULES_push.md` | 649 | Renown |
| `CE/RULES_push_simple.md` | 715 | Renown |
| `CE/RULES_reorganized_6.md` | 638 | Renown |
| `CE/build_all_CE.bat` | 506 | build_all_CE.bat - regenerate everything downstream of the CE data file. |
| `CE/ce_paths.py` | 161 | ce_paths.py — path bootstrap for the d10 build. |
| `CE/parity_d10.py` | 41 | parity_d10.py — batch_engine and vectorized_combat must agree within dice noise. |
| `CE/patch_cultures.py` | 245 | patch_cultures.py - replace the PLAYSTYLES block (or an existing CULTURES block) |
| `CE/rebuild_board.bat` | 20 | rebuild_board.bat - regenerate only the settlement board (no full build). |
| `CE/renown_data.py` | 4425 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_data_CE.py` | 2718 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_data_d10.py` | 4425 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_data_d8.py` | 2801 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/renown_server.bat` | 16 | renown_server.bat - (re)start the Renown board server in WSL. |
| `CE/repo_map.py` | 242 | repo_map.py — write REPO_MAP.md at the repo root: a generated index of the Renown repo for |
| `CE/run_tournament_d10.bat` | 108 | Renown d10 tournament runner  —  CE build |
| `CE/run_tournament_d10.py` | 131 | run_tournament_d10.py — run the Renown tournament against the d10 build. |
| `CE/verify_d10.py` | 169 | verify_d10.py — prove the CE wiring is live before spending hours on a run. |
| `CE/Combatv4/analysis.py` | 2125 | Analysis module for tournament results. |
| `CE/Combatv4/batch_engine.py` | 1633 | Batched matchup engine (v3) — resolves MANY matchups x n_runs in one set of arrays, |
| `CE/Combatv4/combat_kernel_d10.py` | 268 | combat_kernel.py — SHARED numba kernels for both combat engines. |
| `CE/Combatv4/combat_morale_d10.py` | 155 | combat_morale.py — SHARED morale phase for both combat engines (C2, subsystem 2). |
| `CE/Combatv4/combat_primitives_d10.py` | 147 | combat_primitives.py — SHARED rules-math layer for both combat engines (C2). |
| `CE/Combatv4/dice_config.py` | 116 | dice_config — single source for die size across both combat engines. |
| `CE/Combatv4/loadouts.py` | 1841 | Loadout generator for the combat tournament. |
| `CE/Combatv4/make_d10_data.py` | 172 | Generate renown_data_d10.py from renown_data_CE.py. |
| `CE/Combatv4/make_d10_engines.py` | 143 | Generate *_d10.py engine files with FACES parameterised. |
| `CE/Combatv4/normalized_matrix.py` | 277 | Normalized symmetric tactic matrix. |
| `CE/Combatv4/playstyles.py` | 784 | Playstyle module — playstyles drive tactic selection in combat. |
| `CE/Combatv4/renown_combat_d10.py` | 563 | Renown combat simulator. |
| `CE/Combatv4/renown_data.py` | 2715 | renown_data — single source of truth (CSV/0.4.8 branch, card-verified) |
| `CE/Combatv4/run_tournament.py` | 197 | Standalone Renown tournament runner. |
| `CE/Combatv4/tactics_analysis.py` | 54 | Tactics analysis helpers for the Renown Combat Lab. |
| `CE/Combatv4/tournament_vec.py` | 359 | Vectorized tournament runner — same interface as tournament.py but ~4x faster |
| `CE/Combatv4/vectorized_combat_d10.py` | 1992 | Vectorized matchup runner. |
| `CE/Combatv4/shims/combat_kernel.py` | 15 | SHIM — do not edit. Redirects `import combat_kernel` to combat_kernel_d10. |
| `CE/Combatv4/shims/combat_morale.py` | 15 | SHIM — do not edit. Redirects `import combat_morale` to combat_morale_d10. |
| `CE/Combatv4/shims/combat_primitives.py` | 15 | SHIM — do not edit. Redirects `import combat_primitives` to combat_primitives_d10. |
| `CE/Combatv4/shims/renown_combat.py` | 15 | SHIM — do not edit. Redirects `import renown_combat` to renown_combat_d10. |
| `CE/Combatv4/shims/renown_data.py` | 15 | SHIM — do not edit. Redirects `import renown_data` to renown_data_d10. |
| `CE/Combatv4/shims/vectorized_combat.py` | 15 | SHIM — do not edit. Redirects `import vectorized_combat` to vectorized_combat_d10. |
| `CE/ask-the-bot/equipment_table.csv` | 38 | columns: Item,Type,Tier,AP_or_Save,Init,Keywords |
| `CE/ask-the-bot/factions_table.csv` | 42 | columns: Faction,Difficulty,Strength,Mechanic |
| `CE/ask-the-bot/renown_faq.txt` | 487 |  |
| `CE/mapgen/app_shell.html` | 667 | Renown — Map Generator |
| `CE/mapgen/build_board.py` | 442 | build_board.py - print-and-tape Renown board from a procedural map. |
| `CE/mapgen/build_mapapp.py` | 192 | build_mapapp.py - assemble renown-maps.html from its sources. |
| `CE/mapgen/gen.js` | 1677 | gen.js — Renown regional map generator, JS port. |
| `CE/mapgen/gen_settlement_board.py` | 5268 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE/mapgen/hexgen.py` | 258 | hexgen.py — generate the Renown hex asset set as standalone SVGs. |
| `CE/mapgen/hexmap.py` | 85 | hexmap.py — the territory graph (C1). |
| `CE/mapgen/hexstyle.py` | 270 | hexstyle.py - the ONE source for how a board looks. |
| `CE/mapgen/mapgen.py` | 863 | mapgen.py — procedural Renown map generator. |
| `CE/mapgen/mapgen_regional.py` | 1930 | mapgen_regional.py — preset-driven map generation for Renown. |
| `CE/mapgen/presets.js` | 1392 | presets.js - GENERATED from region_presets.py. Do not hand-edit. */ |
| `CE/mapgen/region_presets.py` | 471 | region_presets.py — regional map-generation presets for Renown. |
| `CE/mapgen/renown-maps.html` | 3734 | Renown — Map Generator |
| `CE/references/build_compendium.js` | 133 | build_compendium.js — render the Compendium .docx from renown_data JSON, |
| `CE/references/build_compendium.py` | 394 | build_compendium2.py — redesigned Compendium .docx from compendium_data.json. |
| `CE/references/build_wiki.py` | 1505 | build_wiki.py — multi-page linked HTML wiki from RULES.md + renown_data. |
| `CE/references/card_copies.py` | 69 | card_copies.py — print-quantity logic for pursuit cards, driven by the spec |
| `CE/references/card_sheet.py` | 679 | Renown — Specialization card sheet generator. |
| `CE/references/ce_paths.py` | 123 | ce_paths.py — path bootstrap for the d10 build. |
| `CE/references/combat_sheet.py` | 352 | combat_sheet.py — Renown combat quick-reference (print & laminate). |
| `CE/references/combine_docx.py` | 257 | combine_docx.py — append the Compendium after the Rules doc as one book: |
| `CE/references/compendium_data.json` | 3273 |  |
| `CE/references/display_pdf.py` | 90 | display_pdf.py — NAME_DISPLAY for every reportlab sheet (cards, tiles, equipment, combat). |
| `CE/references/docx_tables.py` | 531 | docx_tables.py — generate Word table fragments (OOXML) from renown_data. |
| `CE/references/domain_board.py` | 321 | domain_board.py - landscape Domain Standing Board. |
| `CE/references/equipment_sheet.py` | 691 | Renown — Equipment, Infrastructure, Alliance & Retinue card sheet generator. |
| `CE/references/faction_sheet.py` | 445 | Renown — Faction card sheet generator. |
| `CE/references/faq_export.py` | 446 | faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat |
| `CE/references/gen_compendium.py` | 184 | gen_compendium.py — generate the Compendium reference as JSON tables from |
| `CE/references/gen_layout.py` | 374 | gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data. |
| `CE/references/gen_layout_roots.py` | 123 | gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it. |
| `CE/references/gen_settlement_board.py` | 6063 | gen_settlement_board.py  --  Renown settlement-board emulator generator. |
| `CE/references/generate_cards.py` | 93 | generate_cards.py — one entry point for ALL card generation, driven entirely |
| `CE/references/host_sheet.py` | 452 | host_sheet.py - Host Card, front & back (landscape Letter), generated from |
| `CE/references/infra_board.py` | 130 | infra_board.py - landscape Infrastructure Board. |
| `CE/references/layout.json` | 1421 |  |
| `CE/references/layout_roots.json` | 1337 |  |
| `CE/references/layout_simple.json` | 1489 |  |
| `CE/references/md_to_docx.py` | 329 | md_to_docx.py — render a prose Markdown rules doc to a styled .docx, injecting |
| `CE/references/package-lock.json` | 205 |  |
| `CE/references/package.json` | 6 |  |
| `CE/references/patch_pursuit_domains.py` | 58 | patch_pursuit_domains.py |
| `CE/references/playstyle_reference.py` | 396 | playstyle_reference.py - culture playstyle reference (landscape Letter, banner per culture). |
| `CE/references/pursuit_tiles.py` | 282 | pursuit_tiles.py - print-and-play ward tiles for every pursuit, from renown_data. |
| `CE/references/reference_sheets.py` | 891 | Renown — Reference sheet generators. |
| `CE/references/render_tree.py` | 272 | render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout). |
| `CE/references/server.py` | 329 | Renown settlement-board server  —  stdlib only, no pip installs. |
| `CE/references/settlement_board.html` | — | generated HTML (794 KB) |
| `CE/references/settlement_mats.py` | 293 | settlement_mats.py - modular ward mats. One Settlement mat (Village -> City, 3 |
| `CE/references/spec_tree_sheet.py` | 1183 | Renown — Specialization Tree renderer. |
| `CE/references/svg_to_pdf.py` | 63 | svg_to_pdf.py - combine SVG pages into ONE PDF. |
| `CE/references/sync_derived.py` | 116 | sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES. |
| `CE/references/tactic_sheet.py` | 446 | Renown — Tactic card sheet generator (v3). |
| `CE/references/wiki_markers.py` | 287 | wiki_markers.py — resolve the {{...}} markers used by the docx rules pipeline |
| `CE/references/world.txt` | 1517 |  |
| `CE/references/worldtxt.py` | 328 | worldtxt.py — parse the hand-maintained world.txt lore book into structured |
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
| `CE/worldbuilding/renown_worldlore.py` | 3385 | renown_worldlore.py |
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
| `SIMPLE` | 4 | bool | True |
| `VERSION` | 6 | str | '0.4.9.9.10-d10-SIMPLE' |
| `BLUNDER_THR` | 34 | int | 10 |
| `DICE_PROVENANCE` | 35 | str | 'd10 / Focused 10+ / Parry 8+ / Recover  |
| `SACK_EXTORT_PER_TIER` | 38 | int | 1000 |
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
| `EMPIRE_START_TIERS` | 3789 | tuple | 3 |
| `STARTING_TREASURY` | 3790 | int | 10000 |
| `BOARD_SIZES` | 3792 | dict | 3 |
| `SIEGE_CALCULUS` | 3798 | dict | 2 |
| `SIEGE_SOURCE_VALUES` | 3813 | dict | 6 |
| `NAME_DISPLAY` | 3840 | dict | 19 |
| `TIER_DISPLAY` | 3864 | dict | 1 |
| `ITEM_TIER_DISPLAY` | 3870 | dict | 1 |
| `TERM_ENVOY_SCORE` | 3877 | str | 'Authority' |
| `display_score` | 3885 | function |  |
| `ALIASES` | 3895 | dict | 19 |
| `display` | 3905 | function |  |
| `display_tier` | 3910 | function |  |
| `display_text` | 3918 | function |  |
| `display_list` | 3941 | function |  |
| `display_md` | 3951 | function |  |
| `display_html` | 3958 | function |  |
| `display_obj` | 3970 | function |  |
| `undisplay` | 3983 | function |  |
| `verify_aliases` | 3992 | function |  |
| `BANDIT_FACES` | 4016 | int | 10 |
| `BANDIT_CUNNING_MIN` | 4017 | int | 10 |
| `die_table_ranges` | 4020 | function |  |
| `die_table_rows` | 4028 | function |  |
| `die_table_text` | 4036 | function |  |
| `die_table_lookup` | 4044 | function |  |
| `die_table_verify` | 4051 | function |  |
| `die_table_weights` | 4070 | function |  |
| `BANDIT_CUNNING_TABLE` | 4080 | dict | 5 |
| `bandit_cunning_ranges` | 4088 | function |  |
| `bandit_cunning_rows` | 4089 | function |  |
| `bandit_cunning_lookup` | 4090 | function |  |
| `bandit_cunning_text` | 4092 | function |  |
| `BANDIT_TACTIC_TABLE` | 4098 | dict | 5 |
| `BANDIT_TACTICS` | 4105 | list | 5 |
| `bandit_tactic_ranges` | 4107 | function |  |
| `bandit_tactic_rows` | 4108 | function |  |
| `bandit_tactic_lookup` | 4109 | function |  |
| `verify_bandit_tables` | 4112 | function |  |
| `RENOWN_MAX` | 4200 | int | 30 |
| `RENOWN_PER_TURN` | 4201 | int | 1 |
| `DOMAIN_POINTS_PER_TURN` | 4202 | int | 1 |
| `GLOSSARY_CATEGORIES` | 4406 | list | 17 |

## 4. Build steps — `CE/build_all_CE.bat`

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

## 5. Rules markers — `CE/RULES_push_simple.md`

- **{{TABLE}}** (30): `edicts`, `eras`, `timers`, `seasons`, `net_influence`, `envoy_outcomes`, `influence_gain`, `domain_board`, `treaties`, `settlements`, `infrastructure`, `wonders`, `build_timers`, `terrain`, `public_order`, `po_modifiers`, `trade_rules`, `retinues`, `tactic_matrix`, `siege_calculus`, `bandit_armaments`, `bandit_growth`, `bandit_cunning`, `bandit_tactics`, `holdings`, `weapons`, `ranged`, `shields`, `armor`, `factions`
- **{{GLOSSARY}}** (16): `Reading the Rules`, `Council & Envoys`, `Actions`, `Domains & Scoring`, `Treaties`, `Settlements & Holdings`, `Map & Range`, `Economy & Public Order`, `Army States`, `Battle Structure`, `Combat Keywords — Defense`, `Combat Keywords — Offense`, `Combat Keywords — Handling`, `Combat Keywords — Immune / Negate`, `World`, `Equipment Tiers`
- **{{ACTIONS}}** (5): `Prowess`, `Cunning`, `Piety`, `Industry`, `Diplomacy`
- **{{LIST}}** (1): `ALLIANCE_RULES`
- **{{TERM}}** (1): `Speed X`
- **{{IDX}}** (22): `Era`, `Empire Phase`, `Council Phase`, `Envoy Phase`, `Battle Phase`, `Rest Phase`, `Season`, `Settlement`, `Hamlet`, `Infrastructure`, `Primitive`, `Developed`, `Sophisticated`, `Wonder`, `Treasury`, `Revenue`, `Trade Agreement`, `Army`, `Lay Siege`, `Capture`, `Sack`, `Bandit Camp`
- **{{VAL}}** (81): `ARMY_MAX_RETINUES`, `BANDITS.Bandit Domain Value`, `BANDIT_ARMY_THRESHOLD`, `BANDIT_CAMP_START`, `BANDIT_CUNNING_MIN`, `BANDIT_FACES`, `BLUNDER_THR`, `CAP_THR`, `CHARTER_MIN_RANGE`, `DICE_PROVENANCE`, `DOMAIN_BOARD.innate_influence_own_envoys.Established`, `DOMAIN_BOARD.innate_influence_own_envoys.Rising`, `DOMAIN_BOARD.innate_influence_own_envoys.Sovereign`, `DOMAIN_BOARD.innate_influence_own_envoys.Untested`, `DOMAIN_BOARD.max_influence_per_vote.Established`, `DOMAIN_BOARD.max_influence_per_vote.Rising`, `DOMAIN_BOARD.max_influence_per_vote.Sovereign`, `DOMAIN_BOARD.max_influence_per_vote.Untested`, `DOMAIN_POINTS_PER_TURN`, `ENDURANCE_REGAIN`, `ERAS.Ascension.innate_diplomacy_influence`, `ERAS.Ascension.max_influence_per_diplomacy_vote`, `ERAS.Eminence.innate_diplomacy_influence`, `ERAS.Eminence.max_influence_per_diplomacy_vote`, `ERAS.Founding.innate_diplomacy_influence`, `ERAS.Founding.max_influence_per_diplomacy_vote`, `ERAS.Founding.renown`, `ERAS.Zenith.innate_diplomacy_influence`, `ERAS.Zenith.max_influence_per_diplomacy_vote`, `FACES`, `FATIGUE_MORALE`, `FOCUSED_THR`, `FRONT_LINE_MAX`, `HAMLET_RANGE`, `INITIATIVE_MAX`, `INITIATIVE_MIN`, `MORALE_DICE_MAX`, `OUTLAW_BUFFER_RANGE`, `OUTLAW_COUNTRY_START`, `PANIC_CASUALTY_THRESHOLD`, `PARRY_BASE`, `PO_MAX`, `PO_MIN`, `PURSUIT_UPKEEP_BY_TYPE.Energy`, `PURSUIT_UPKEEP_BY_TYPE.Monument`, `PURSUIT_UPKEEP_BY_TYPE.Other`, `PURSUIT_UPKEEP_BY_TYPE.Power`, `RENOWN_PER_TURN`, `RESERVE_MAX`, `RETINUES.Knight Templar.cost`, `RETINUES.Knight Templar.to_hit`, `RETINUES.Levy.cost`, `RETINUES.Levy.to_hit`, `RETINUES.Man-at-Arms.cost`, `RETINUES.Man-at-Arms.to_hit`, `RETINUES.Sergeant.cost`, `RETINUES.Sergeant.to_hit`, `ROUT_THR`, `SACK_EXTORT_PER_TIER`, `SETTLEMENTS.City.wards`, `SETTLEMENTS.Hamlet.wards`, `SETTLEMENTS.Metropolis.reach`, `SETTLEMENTS.Metropolis.wards`, `SETTLEMENTS.Town.wards`, `SETTLEMENTS.Village.reach`, `SETTLEMENTS.Village.wards`, `SIEGE_CALCULUS.Lay Siege.floor`, `SIEGE_SOURCE_VALUES.Stone Walls.value`, `SIEGE_SOURCE_VALUES.Wooden Walls.value`, `STANDING_THRESHOLDS.Established`, `STANDING_THRESHOLDS.Rising`, `STANDING_THRESHOLDS.Sovereign`, `STANDING_THRESHOLDS.Untested`, `STARTING_TREASURY`, `STARTING_TURN_PHASE_OPENER`, `TIMERS.Capture Timer.default`, `TIMERS.Sack Timer.default`, `TRADE_RULES.income_per_craft`, `VASSAL_EXCHANGE_CAP`, `VASSAL_INFLUENCE_TAKE`, `WEALTH_EDICT_GOLD`
- **docx_tables.REGISTRY** (31): `armor`, `bandit_armaments`, `bandit_cunning`, `bandit_growth`, `bandit_tactics`, `build_timers`, `domain_board`, `edicts`, `envoy_outcomes`, `eras`, `factions`, `holdings`, `influence_gain`, `infrastructure`, `net_influence`, `po_modifiers`, `public_order`, `ranged`, `retinues`, `seasons`, `settlements`, `shields`, `siege_calculus`, `tactic_matrix`, `tactical_terrain`, `terrain`, `timers`, `trade_rules`, `treaties`, `weapons`, `wonders`

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
| 215 | ## Player Setup |
| 224 | # Actions & Voting |
| 226 | ## Action Mechanics |
| 228 | ### Sending an Envoy |
| 232 | ### Resolving an Envoy |
| 264 | ## Influence |
| 272 | ## Prowess Actions |
| 276 | ## Cunning Actions |
| 280 | ## Piety Actions |
| 284 | ## Industry Actions |
| 288 | ### Rule: Ulterior Motive |
| 292 | ## Diplomacy Actions |
| 298 | ### Rule: Diplomatic Mission |
| 304 | # Domains & Standings |
| 306 | ### Domain Standings |
| 316 | ### Standing & Influence |
| 329 | # Diplomacy & Treaties |
| 331 | ### Treaties & Alliances |
| 339 | ### Vassalization |
| 361 | # Empire Building |
| 363 | ## Settlements |
| 369 | ### Settlement Wards |
| 373 | ### Chartering Settlements |
| 377 | ### Settlement Reach |
| 381 | ### Hamlets |
| 387 | ## Infrastructure |
| 411 | ## Territory & Terrain |
| 425 | # Economy |
| 427 | ## Public Order |
| 437 | ### Innate Public Order Modifiers |
| 441 | ## Treasury & Upkeep |
| 451 | ### Insolvency & Bankruptcy |
| 464 | ## Trade & Income |
| 466 | ### Who Can Trade & Income |
| 481 | ### Income Types |
| 489 | # Armies |
| 491 | ### Armies Overview |
| 501 | ### Mustering |
| 511 | ### Blocked Armies |
| 517 | # Battles & Sieges |
| 519 | ## Battle Phase |
| 521 | ### Begin Battle |
| 523 | ### Begin Skirmish |
| 531 | ### How a Battle Resolves |
| 535 | ### Begin the Battle — Seize the Initiative |
| 539 | ### The Skirmish Steps |
| 563 | ### Resolve Battle |
| 571 | ### End Battle |
| 573 | ### Tactic Matrix |
| 587 | ## Siege Warfare |
| 593 | ### Siege Timer |
| 599 | ### Beginning a Siege |
| 609 | ### Resolving a Siege |
| 622 | # Bandits |
| 624 | ### Outlaw Country |
| 630 | ### Spawning Bandit Camps |
| 636 | ### Growing Bandit Camps |
| 640 | ### Bandit Armaments by Era |
| 644 | ### Bandit Growth by Era |
| 648 | ### Bandit Info |
| 666 | ### Bandit Army Behavior |
| 678 | ### Attacking a Bandit Camp |
| 684 | # Holdings |
| 688 | # Equipment |
| 690 | ## Melee Weapons |
| 694 | ## Ranged Weapons |
| 698 | ## Shields |
| 702 | ## Armor |
| 708 | # Factions |
| 712 | # Index |

## 6. Settlement board — `CE/references/gen_settlement_board.py`

Payload keys passed to the HTML as `DATA` (55): `records`, `naturalNames`, `externalTokens`, `simple`, `chainTerm`, `pursuitTerm`, `infra`, `wonders`, `armySrc`, `equip`, `glossary`, `domainBoard`, `publicOrder`, `wikiBase`, `wikiHome`, `tree`, `rulebook`, `limits`, `eras`, `edicts`, `envoyOutcomes`, `outcomeThresh`, `startPhase`, `actions`, `phaseRules`, `rulesConst`, `domains`, `standings`, `tradePerCraft`, `noTradeSeason`, `renownPerTurn`, `dpPerTurn`, `settlements`, `battle`, `terrainRef`, `banditLoadouts`, `bandits`, `treaties`, `allianceRules`, `startTiers`, `startTreasury`, `pursuitUpkeep`, `buildTimers`, `timers`, `seasons`, `poModifiers`, `vassalInfluenceTake`, `aliases`, `scoreTerm`, `costs`, `influenceGain`, `siege`, `factions`, `warnings`, `version`

Python: `load`:27, `strip_md`:34, `has_cond`:76, `to_int`:79, `classify`:82, `_iv`:149, `envoy_fx`:150, `combine_parts`:225, `combine_effects`:266, `rules_payload`:270, `tree_payload`:328, `parse_effects`:362, `parse_mreq`:368, `classify_req_token`:376, `build`:385, `font_faces`:525, `_pursuit_term_template`:550, `render_html`:558, `_style_js`:566, `find_mapgen`:577, `check_rules`:5760, `_val`:5878, `rules_section`:5887, `battle_data`:5906, `bandit_loadouts`:5926, `main`:5973

JS sections: TABLE: seating, Council & Envoy phases :1279,  :3928, EFFECT PLUMBING: read rule text on a player's active pieces + faction :5070, RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement :5115, UNDO / REDO :5467, ACTIVITY LOG :5505, GAME: save · load · new :5569, HOVER KEYWORDS :5603

JS functions (510, name:line):

```
fixBastard:1246 dispScore:1253 tnow:1290 noteServerDate:1291 boardEndOn:1297 TB:1298 tSeats:1299 tTimer:1300 tTurn:1301 tPhase:1302 PT:1304 tCur:1305 tCurW:1306 sameP:1307 meP:1308 canAct:1309 seatMap:1312 seated:1316 isSpring:1317 hostP:1318 voteOrd:1320 tOrder:1321 canHost:1322 seatsLocked:1323 tStand:1326 eraRec:1327 diploInf:1328 diploCap:1329 eraActions:1330 boardFx:1333 fxOf:1345 scopeOk:1346 sgn:1347 fxLabel:1348 atWarPair:1360 opposeBlock:1361 innateParts:1365 modSum:1371 innateInf:1373 voteCap:1374 inflPool:1377 personalEnvoys:1378 councilEnvoys:1379 tOutcome:1380 outText:1382 tPlan:1385 domStarted:1399 tSim:1402 performEval:1464 failPassFx:1475 actionsOf:1476 actReqFlag:1478 actInfoHTML:1482 tApply:1489 tSetPhase:1501 tEndTurn:1503 tAutoSeat:1517 tSig:1523 tName:1525 tVoteTxt:1526 envBadges:1527 innateTxt:1533 tOutCls:1535 tHistHtml:1536 tPerformHtml:1548 empireChecklistHTML:1567 treeSave:1577 treeHTML:1584 rulebookHTML:1648 linkifyRules:1651 renderReference:1655 renderTable:1667 tPanel:1738 tWire:1835 tCountdown:1881 applyTheme:1895 applySkin:1906 startDoms:1912 startSettlements:1914 startSig:1917 reseedIfPristine:1919 newBoard:1924 newPlayer:1926 normalizeD:1942 activeBoard:1961 reindex:1962 pActive:1975 flagState:1978 ignBtn:1983 ignNote:1986 unlockStatus:1992 nameHit:2003 missTxt:2004 recomputePC:2006 buildTimerMod:2011 withBuildMod:2015 pursuitBaseTime:2016 infraBaseTime:2017 pursuitBuildTime:2018 infraBuildTime:2019 buildNote:2020 settBaseTime:2021 settBuildTime:2022 itm:2023 infraOn:2024 gameStarted:2025 empTimers:2029 empEconomy:2030 empPO:2034 empArmies:2039 endRow:2042 boardEndTurn:2045 tickRealm:2048 empirePhase:2050 tickTimers:2072 pursuitUpkeep:2079 withBoard:2081 setOnline:2097 clone:2107 jeq:2108 isObj:2109 merge3:2111 splitD:2120 joinD:2126 save:2150 editing:2186 cvar:2206 fmt:2207 cap:2208 settMeta:2211 settTier:2212 occupants:2213 hamletOK:2214 hamletRoot:2217 hamletFits:2218 effList:2225 effLabel:2230 exemptionsOf:2231 wardExemptions:2240 isFreeRider:2241 wardUse:2242 canPlace:2253 capitalSett:2271 setCapital:2272 isCityPlus:2274 dbActive:2275 capBonus:2279 eraCapBase:2280 eraCap:2281 capSrc:2282 cityCount:2283 eraAllows:2285 rslug:2293 boardFlags:2294 hasMetropolis:2316 onBoard:2317 nextTier:2318 autoFill:2320 buildFilters:2341 renderList:2347 itemRow:2388 flash:2395 addInfraByName:2397 addItem:2400 removeInstance:2425 removeOneByName:2426 addByName:2431 addPursuitByName:2432 moveInstance:2433 infraReqToks:2448 infraTokStatus:2454 infraReqStatus:2468 infraValid:2473 infraActive:2480 infraReqLinesHTML:2481 masteryInfraToks:2485 masteryInfraHTML:2486 annotReqTok:2493 optionMet:2498 reqStatus:2506 instStatus:2513 chainLine:2520 simpleReq:2528 simpleReqHTML:2540 computeEarned:2549 atomEl:2567 atomsBlock:2576 render:2589 renderTopBar:2636 toggleEmpty:2662 settBar:2665 renderPursuitBoard:2674 wardPiles:2777 wardGrid:2789 unitFor:2816 tryMove:2821 scrollHost:2854 dropTargetAt:2855 clearDropHL:2863 armDrag:2864 beginDrag:2881 dragMove:2895 dragEnd:2907 factionFree:2917 setFaction:2921 facGearFlags:2930 factionFlags:2936 renderFaction:2942 timerCtl:2951 placementSelect:2956 contribChips:2970 pursuitDetail:2981 nextLinksSummary:3005 nextLinksHTML:3007 pursuitTable:3015 pursuitCard:3042 renderInfraSection:3124 armyUnlocks:3169 unlockedShieldTiers:3201 tierOK:3205 gloss:3206 glossLookup:3215 openModal:3224 closeModal:3228 kwChipHTML:3229 esc:3230 inspectKeyword:3231 inspectItem:3253 optionList:3276 renderArmy:3290 armyCard:3320 reqMet:3425 weaponUnlockMet:3428 moraleBase:3430 armyUpkeep:3431 moraleCap:3433 effMorale:3435 isRouted:3436 armyStats:3438 noUpkeepTiers:3473 holdsActive:3475 playersWithout:3477 calcMetrics:3479 computeTotals:3530 poTaxMod:3559 taxDouble:3564 winterTax:3565 settTax:3571 tradeIncome:3574 tradeRaw:3580 seasonNet:3588 husbandryGoldFor:3592 SEASON_DBL_TYPE:3594 boardMetrics:3595 poBandName:3602 poActiveKeys:3604 poActiveEffects:3606 poImmune:3613 poDoubled:3614 renderPO:3616 curSeason:3631 stepSeason:3632 playerOfBoard:3635 igVal:3636 eraIdx:3637 playerAtWar:3638 influenceRowsBase:3639 influenceRows:3668 influenceTotal:3673 poModRows:3676 totTip:3686 epSources:3697 topSuz:3709 sameAlliance:3710 poFloor:3713 applyPOFloor:3714 epRows:3715 poModTotal:3728 dpButtons:3729 renderDP:3732 renderMiniStand:3739 renderInfluence:3752 renderPOMods:3755 siegeState:3763 siegeCalc:3764 siegeHTML:3781 realmTimers:3796 timerAddHTML:3797 boardTimerRows:3801 siegeResolveHTML:3807 activeTimersHTML:3812 timersHTML:3818 seasonsHTML:3824 costsHTML:3827 wireDashExtras:3830 renderDash:3854 domBand:3888 standingsBoardHTML:3889 mods:3930 diplo:3935 pk:3936 isVassal:3938 vassalsOf:3939 effPair:3940 pairOf:3943 pname:3944 allianceLabel:3945 pboard:3946 hasRoad:3947 eraRank:3950 allianceEra:3951 allianceOK:3952 pairFlags:3953 dStatus:3960 diploHTML:3964 wireDiplo:4020 newSide:4052 battle:4053 banditArmy:4055 armBandits:4059 sideArmy:4064 blog:4068 d10:4069 seizeForced:4070 facCombat:4073 sideUnlocks:4084 sideDomains:4088 standingFxOf:4089 hasTiltyard:4093 eqOptions:4094 eqCode:4103 eqNow:4106 eqWeapon:4109 tacAllowed:4117 tacOK:4122 randomTacticPool:4123 sideCalc:4126 pickKey:4236 viewerSide:4237 mdLite:4259 fmtModLong:4261 fmtMod:4264 dieRow:4266 rollHTML:4267 sideHTML:4275 battleRulesHTML:4361 renderBattle:4368 incoming:4390 roll:4393 ripN:4449 addRip:4450 setPendCas:4451 pendCas:4452 applyCas:4453 endSkirmish:4454 endBattle:4470 wireBattle:4485 edictTimerLen:4530 edictChoices:4532 edictTotal:4538 edictOwners:4539 bumpRenown:4540 edictBoardHTML:4541 wireEdicts:4569 currentEra:4583 standingEffectsHTML:4588 renderRenown:4603 mapClimate:4664 mapPal:4669 tLum:4672 tTone:4674 tLighten:4675 tGlyph:4678 tSwatch:4683 mapState:4690 hexDist:4691 decodeGrid:4694 seedCode:4704 generateMap:4705 parseSeedCode:4713 mapZoom:4722 reachBonus:4728 reachOwners:4737 reachResources:4749 rawReachStatus:4756 mapSVG:4762 outlawReport:4824 banditDomain:4835 banditAutoHTML:4836 armyName:4845 mapLinkBad:4846 mapLinksHTML:4847 wireBanditAuto:4858 BST:4862 bLog:4863 hk:4864 mapSetts:4865 cellPlayer:4866 cellSett:4868 mapArmies:4871 cellArmy:4872 cellTitle:4875 byDist:4878 outlawOwner:4879 outlawOf:4880 hexFree:4881 spawnCamp:4882 growCamps:4884 expandOutlaw:4887 immuneUprising:4890 banditTargetMods:4891 cunningAction:4893 endorsedExtort:4894 banditAct:4895 runBanditMechanics:4917 banditSkims:4928 creditSkims:4933 envoyOutcome:4937 banditCunningHTML:4942 dieLookup:4959 terrainTablesHTML:4962 mapToolsHTML:4983 banditPanelHTML:5016 wireMap:5031 srcText:5072 srcMatch:5079 srcHas:5080 bordersOf:5083 poCap:5087 poTextFloor:5088 siegeTextMods:5091 siegeWinterOK:5098 actRestrict:5100 actRiders:5106 extortGold:5119 autoExtortRows:5125 runAutoExtort:5133 firstDoubtRed:5148 gainDoubt:5152 siegeOn:5158 besiegedCount:5159 pById:5160 nextId:5161 captureTransfer:5162 sackApply:5172 resolveRealm:5183 sackLocks:5188 armyHex:5192 settHex:5193 musterLimit:5194 musterTick:5200 hasMusterField:5208 charterFlags:5211 terrPen:5225 terrBlocked:5226 terrWaterStop:5227 terrStrain:5228 spClauses:5230 spVal:5231 provinceOf:5232 moveTraits:5234 speedOf:5239 hexNb:5267 moveRange:5269 moveInfo:5283 moveArmyTo:5285 moveOverlay:5290 movePanelHTML:5297 set:5308 computeAll:5309 renderSettlements:5312 adminUI:5371 firstHostOpen:5387 firstHostBtn:5388 hudSign:5395 hudData:5396 renderHUD:5403 renderTurnStrip:5431 syncBoardEndBtn:5447 mnavSync:5463 undoSnap:5471 undoRecord:5473 undoRebase:5479 undoScoped:5480 undoApply:5481 doUndo:5494 doRedo:5495 undoButtons:5496 actSnap:5509 actRebase:5510 actJoin:5512 actSchedule:5515 fmtG:5516 boardDiff:5517 actFlush:5549 activityHtml:5562 gameAllowed:5571 gameData:5572 refreshGames:5573 gameReplace:5576 newGameState:5580 gslug:5605 kwify:5617 wikiA:5628 gkHtml:5629 openFromHash:5646 setLift:5672 gkShow:5681 gkHide:5685 gkFor:5686
```
