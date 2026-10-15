# claude_task_2 — what changed, open questions

Data: `renown_data_d10.py` (and its build copy `renown_data.py`). Rules: `RULES_push_simple.md`. Board: `references/gen_settlement_board.py` (+ regenerated `settlement_board.html`).
Checks: `--check-rules` 0 mismatches · `wiki_markers.py` clean · Rules.docx → PDF, wiki, domain board, settlement mats/board, host sheet, FAQ all build · board scenario runs (4 players, map, Wild zones, bandit mechanics, culture, chronicle) with no JS errors.

## Done

| Item | Change | Where |
|---|---|---|
| Map plates | Settlement plate = name (★ if capital) + status icons. Army plate = name + gear icons + status icons. Stats (Tax/Reach/Wards/Garrison, Strike/Init/Save/Morale) only in the inspector (click). Hover title: gear + status text | board `mapPlate`, `settPlate`, `cellTitle` |
| Peat Bog on Reference | Yes: no Peat Bog on the map, so its chart only kept nodes reachable from other roots (Forgotten Catacombs → Toxicarium → Plague Pit). Root charts whose Raw Material is off the map are now hidden | board `treeHTML` |
| 1 · PO by Era (A) | `PO_BANDS` templates + `ERAS[*].po_scale_neg` 1/2/3/4, `po_scale_pos` 1/1/1/1 (plumbing: raise to scale positives). `PUBLIC_ORDER` (Founding text) and `PUBLIC_ORDER_BY_ERA` derived. Board reads the current Era: Tax, Influence, **Speed** (PO Speed wasn't applied to movement before), Uprising spawns N camps. Rules table shows X per Era | data, board, docx_tables, wiki_markers, build_wiki, faq_export, settlement_mats, RULES |
| 3 + 4 · Wild Outlaw Country + reach targeting | `WILD_OUTLAW` (count = ceil(players/2)+1; spring_spawn / spring_growth / march flags), `BANDIT_CAMP_REACH` (None = target piece's Aura). Setup step 6 seeds zones (Host button; auto on Begin Turn 1): interior first (beyond CAPITAL_EDGE_RANGE), max distance from pieces/Outlaw Country, OUTLAW_COUNTRY_START hexes, OUTLAW_BUFFER_RANGE clear. Wild hexes: dashed purple border, own place tool. Camps act only on pieces in range (nearest first); none in range → no action. Smuggler's Nook carve-out implemented (wasn't before). Wild Bandit Armies Skirmish/Siege in range, never March | data, board, RULES (Setup 6, Bandits) |
| 5 · Culture filter | Player-bar dropdown, default `CULTURE_SELF_MADE` ("Self-made"). Catalog hides out-of-culture Holdings / Wonders; tree dims them. Culture = its Domains + Domain-free Holdings + its Monuments and their chains. No game effect | data, board |
| 6 · Town names | `PLACE_NAMES` (15 cultures, draft banks from PHONOLOGY + naming registers) in worldlore; Ossensteins borrow other cultures' names half the time. Named at Charter, unnamed ones at Begin Turn 1; 🎲 reroll in the inspector. Self-made = culture matching the highest Domain(s) (all equal → Astravantheliad). Never repeats a lore place or a name in play | worldlore, board |
| 7 · Chronicle | `CHRONICLE` templates (13 events, on/off each) in worldlore; voice from `intro.txt` (the INTRO .docx is an LFS pointer in the repo, unreadable here). Snapshot diff on save + direct hooks; panel under Summary on the Table; export .md | worldlore, board |
| 9 · Map gen analysis | `MAPGEN_COVERAGE.md` — 20 presets × 10 seeds | new file |
| 10 · Syntax sweep | `SYNTAX_SWEEP.md` — canon, 221 rewrites + manual, parser updates, verification | data, RULES, board, docx_tables, wiki_markers |

## Behaviour changes to know

- `Influence ±N` now always means Influence tokens; Envoy-score modifiers are written `Authority ±N` in the data. Display unchanged (TERM_ENVOY_SCORE still renames).
- PO-immune boards (e.g. "No longer affected by all Public Order effects") now skip Uprising spawns too.
- A camp in a player's Outlaw Country with Smuggler's Nook active targets other players at random, any range.
- Wild Territories within your Reach count as your Outlaw Country (Spring spawn, Uprising, Foster Rebellion can land there; Local Unrest counts their camps).
- Rules prose states the current flag values (Wild camps don't grow in Spring, never March); flipping `WILD_OUTLAW` flags needs those two sentences edited.

## Questions

| # | Topic | Question |
|---|---|---|
| 1 | Wild count | Implemented ceil(players/2)+1. Switch to unclaimed-board size? If so, hexes per zone? |
| 2 | Wild growth | Read as: Wild camps grow every non-Spring Season; Spring spawns 1 camp per zone, no growth. Or did "grow" mean the zone gains a Territory each turn? |
| 3 | Wild March | Wild Bandit Armies never March (flag). Keep, or March within some radius? |
| 4 | Camp reach | Targeting uses the target's Aura: every Settlement 3, Levy 1, other Retinues 2. Armies are now rarely in range for Sabotage. Want a camp-side number in `BANDIT_CAMP_REACH` instead (e.g. by camp size)? |
| 5 | Wild ownership | OK that Wild Territories in your Reach take your Spring/Uprising/Foster spawns? |
| 6 | Zenith PO | Uprising 4 camps, Aimless Speed -8 (Levy 5 + Summer 2 = 0). Intended? |
| 7 | Culture | Catalog hides, tree dims. Want hide in both / dim in both? Should the culture also drive Reference recommendations (CULTURES.monuments order)? |
| 8 | Names | Self-made from highest Domain(s), ties of all four → Astravantheliad. OK? Review the banks (worldlore `PLACE_NAMES`). |
| 9 | Chronicle | Tone check on `CHRONICLE` lines; any events to add/drop? War declared from the Diplomacy table (no declarer known) logs a neutral `war_pair` line |
| 10 | Syntax | Convert these too: `At the start of each turn` → `Each Empire Phase`; `Each turn, you may` allowances → `Once per turn, may`; Domain Points "1 per turn"? |
| 11 | Stale | `COSTS['Tax per tier']` "500 gold per settlement tier per turn (collected in Winter)" vs SETTLEMENTS tax_income 2000/4000/6000/8000. Delete or fix? |
| 12 | Stale | GLOSSARY `Outlaw Country` hard-codes "starting at 3" (data holds OUTLAW_COUNTRY_START). |
| 13 | Once per <Phase> | Approve per row below; I'll convert text + board once-tracker together. |

### Once per turn → once per <Phase> candidates

| Kind | Name | Text | Phase |
|---|---|---|---|
| Holding | Abbey | Once per turn: Authority +2 another player's Piety Envoy; | Envoy |
| Holding | Grand Tournament | Reach +1, 3x/turn: exchange 500 gold for 1 Influence; | Envoy (your example) |
| Holding | Courier Network | Once per turn before voting: Authority -1 on Target Envoy; | Envoy |
| Holding | Courier Network | Once per turn: successfully Performed Personal Envoy can be Performed next turn; | Envoy |
| Holding | Toll House | Once per turn: when an Army ends a Move action within your Province: Perform a Diplomacy action targeting that army's player | Envoy (Move action) |
| Holding | Forgery Workshop | Once per turn: attempt another Cunning Envoy targeting a different player if your Cunning Envoy Failed | Envoy |
| Holding | Beacon Towers | Once per turn, you may select an Army within your Province and move it up to its modified Speed. | Envoy (Move action) |
| Holding | Baggage Train | Once per turn, you may perform a Move action. | Envoy (Move action) |
| Holding | Senate Hall | Once per turn: Before players Support or Oppose, you may auto-Condemn an At War Envoy OR auto-Endorse an Ally's Envoy | Envoy |
| Holding | Exalted Basilica | Once per turn, perform an Endorsed Spread Truth. | Envoy |
| Holding | Cipher Chamber | Once per turn: select an army you did not select last turn, that army gains Blocked. | Empire |
| Holding | Cipher Chamber | Once per turn: select any active Timer you did not select last turn; | Empire |
| Holding | Whispering Undercroft | Once per turn when a player sends an Envoy: that player must declare the specific action & target they would Perform if the Envoy passes (including sub-Actions). | Envoy |
| Infra | High Chancery | Once per turn, you may Endorse one Envoy Sent by yourself after voting. | Envoy |
| Faction | Friends in Low Places | Each turn, you may control one Bandit Camp outside your Territory. | ? |
| Faction | Palatine | Each turn, you may spend 1 of an ally's Influence, targeting your own Envoys if you wish. | Envoy |

## UX overhaul (theory, for iteration — nothing built)

| View | Holds |
|---|---|
| Realm (Table renamed) | sticky phase bar · map centre · contextual action panel (only what this phase allows you: pre-vote, Build/Improve/Repair, Muster, Extort targets, DP spend; seat switcher for test mode) · seats/Host · Summary + Chronicle drawer |
| Empire | scene · holdings/infra/armies bars · settlement cards · flags |
| Reference | as is, culture-filtered |

Order: action panel → move Realm (players table → seat hover + all-players drawer; treaties → seat menu) into it → remove the Realm tab.
Map-first: click a Settlement → plate + its actions; click an Army → move / muster / siege (inspector already does most of this).
Phone: panel first, map as a toggle (my lean) — your call.

## Files

`CE/TASK2_NOTES.md` (this) · `CE/SYNTAX_SWEEP.md` · `CE/MAPGEN_COVERAGE.md` · `CE/renown_data_d10.py` · `CE/renown_data.py` · `CE/RULES_push_simple.md` · `CE/worldbuilding/renown_worldlore.py` · `CE/references/gen_settlement_board.py` · `CE/references/settlement_board.html` · `CE/references/docx_tables.py` · `CE/references/wiki_markers.py` · `CE/references/build_wiki.py` · `CE/references/faq_export.py` · `CE/references/settlement_mats.py`
