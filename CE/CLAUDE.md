# CLAUDE.md — Renown repo orientation (lives in `CE/`; paths below are relative to `CE/`)

Read this, then `REPO_MAP.md` (generated index: tree, file purposes, data names with line numbers,
build steps, rules markers, board functions). Open individual files only after the map says where to look.

## What this repo is
Renown — 3–7 player medieval political strategy tabletop game. Rules, cards, boards, wiki and a
settlement-board web app are all generated from one Python data file.

## Builds (separate, no cross-dependencies)
| Folder | Build | Notes |
|---|---|---|
| `CE/` (here) | D10 / current | `build_all_CE.bat` — the live build |
| `../Combatv3/` | D6 / deprecated | own `build_all.bat`; don't import across |
| `../0.4.8.1/`, `../0.4.8 Updated Docs/`, `../generators/` | archived | reference only |

## Source of truth (CE)
| File | Role |
|---|---|
| `renown_data_d10.py` | **edit this.** Build copies it to `renown_data.py` (DIE=d10). `renown_data_d8.py` / `renown_data_CE.py` / `Combatv4/renown_data.py` are other variants / stale copies |
| `RULES_push_simple.md` | rules prose (SIMPLE=1). Numbers/tables come from data via markers — never type a number the data holds |
| `renown_data.py` | build output copy; same content as d10 after a build |
| `worldbuilding/renown_worldlore.py` | lore source (CE keeps its own lore copy; drift from Combatv3 is intended) |

`SIMPLE` (env `RENOWN_SIMPLE`, default on) switches Pursuit→Holding naming, action names
(Pursue→Build, Build→Improve) and other SIMPLE overrides at the bottom of the data file.
Display layer: `NAME_DISPLAY` / `ALIASES` / `TERM_ENVOY_SCORE` rename what players read
(`display_text`, `display_md`); dict keys stay canonical (e.g. glossary key `Pursuit` prints "Holding").

## Rules markdown markers (rendered by `references/md_to_docx.py`, wiki via `wiki_markers.py`)
| Marker | Source |
|---|---|
| `{{VAL:PATH.key}}` | scalar from data |
| `{{TABLE:name}}` | `docx_tables.REGISTRY` |
| `{{ACTIONS:Domain}}` | `ACTIONS` |
| `{{LIST:NAME}}` | list in data |
| `{{GLOSSARY:Category}}` | `GLOSSARY_CATEGORIES` (in data) |
| `{{TERM:x}}` / `{{IDX:x}}` | inline definition / index entry |
| `{{TOC}}` / `{{INDEX}}` / `{{COLS:n}}` | print furniture |
The Compendium is retired: its chapters render inside Rules.docx.

## Main pipelines (`references/` unless noted)
| Output | Script |
|---|---|
| Rules.docx | `md_to_docx.py` + `docx_tables.py` |
| Wiki | `build_wiki.py` + `wiki_markers.py` |
| Settlement board | `gen_settlement_board.py` → `settlement_board.html`, served by `server.py` (stdlib, SQLite) |
| Cards / sheets / boards | `generate_cards.py`, `domain_board.py`, `infra_board.py`, `settlement_mats.py`, `host_sheet.py`, … |
| Simulation | `Combatv4/` — `vectorized_combat_d10.py`, `batch_engine.py`, `loadouts.py`, `dice_config.py` (not `renown_combat*.py`) |

Checks: `python gen_settlement_board.py --data ../renown_data_d10.py --rules ../RULES_push_simple.md --check-rules`
(0 mismatches expected); `python wiki_markers.py ../RULES_push_simple.md` (no unresolved markers).
Run scripts from `references/` with `PYTHONPATH` set to this folder.

## Working rules
- Never invent mechanics or numbers; flag data/rules inconsistencies instead of resolving them silently.
- Propose → confirm → build for design or structural changes.
- Board rule checks are flags, not locks. No unrequested explanatory text in generated tools.
- Validate: parse check + import/run + render (docx → PDF, board in a browser).
- Balance questions: tournament data first (`run_tournament_d10.bat`).

## Regenerating the map
`python repo_map.py` → `REPO_MAP.md` (this folder) (also runs in `build_all_CE.bat` before the repo push).
