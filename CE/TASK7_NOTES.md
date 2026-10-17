# claude_task_7 — what changed, open items

Response to TASK6_NOTES. Data (`renown_data_d10.py`) unchanged — your Condemned / Start of the Empire Phase edits were read, not modified.
Checks: `--check-rules` 0 mismatches · `wiki_markers.py` no unresolved markers · Rules.docx builds · host_sheet.pdf builds · FAQ export · `--effects-report` 0 to review, 83/83 patterns used · `node parity_efx.js` OK 13326 checks, 0 differences · page script `node --check` OK · browser drive (Empire view, catalog Available, empty-Ward picker, Build options, Condemned Industry / Diplomacy / Prowess, manual Treasury edits, End turn, PO toggle, 390 px phone) no JS errors.

## Done

| Item | Change | Where |
|---|---|---|
| 1 Activate removed | Empire Phase step list: "Start of the Empire Phase … including one-time Domain Standing effects"; Activate step deleted. Domain Standings: *Perform …* Standing effects are one-time, used at the Start of the next Empire Phase after you reach the Standing; others apply while held, their *Each Empire Phase* effects resolve with the other Each Empire Phase effects | `RULES_push_simple.md` |
| | Board Empire checklist: Start step names one-time Standing effects; "Remaining Each Empire Phase effects" added last. Host sheet + FAQ turn line reworded | `10_table.js`, `host_sheet.py`, `faq_export.py` |
| | "Each Empire Phase (Activate)" window removed from the registry and its JS replay (no data uses it now) | `effect_registry.py`, `parity_efx.js` |
| Condemned | Reads the text after "+" as the Condemn cost: Cunning / Industry pay 2000, no Recoup; Piety Doubt +1 more; Prowess / Diplomacy flagged with their text. "pay the action" text still handled if it comes back | `10_table.js` (`resolveEnvoy`) |
| 2 Infra-req Roots | Courtyard, Inn (any Root whose only unmet check is `infrastructure_req`) listed under Available, picker and Build as "requires Town Hall" / "requires Hitching Post"; + disabled, Build option disabled | `30_empire.js` (`pReqMiss`, `reqRow`), `10_table.js` |
| 2/3 No room | After Start game: Build options with no free Ward are disabled ("→ no free Ward"); Build refuses and flags; catalog add refuses ("no free Ward"). Before Start game unchanged (Unplaced) | `10_table.js`, `30_empire.js` (`addItem`) |
| 4 Hamlet rule | One target rule for Build and the empty-Ward picker: Raw Material in Reach → efficient pairing → Natural to Hamlet → clicked Settlement (picker) → most empty Wards → largest → newest. Auto-placement never puts a non-Natural Holding in a Hamlet (efficient pairing included; e.g. Alchemy with Peat Bog in a Hamlet goes elsewhere). Moving by hand unchanged. Picker shows ⚡ (efficient) or → (elsewhere) target | `30_empire.js` (`autoHamlet`, `smartSid`, `effSpot`, `placeHolding`, `wpRender`) |
| Standings | Catalog Standing names wrap to two lines; three per row kept | `board.css` |
| Ledger seasons | Cells shrink to fit; values compact (+4.5k), full value on hover | `board.css`, `30_empire.js` (`fmtK`) |
| Faith / Doubt | "active only" toggle (default on, per device) hides 0-value rows; count of hidden shown | `40_realm_data.js` |
| Treasury / PO headers | Treasury header shows the amount (visible collapsed) + gold / turn; PO header shows the value + PO / turn (band shown when collapsed). Header text 15 px, numbers 24 px | `body.html`, `board.css`, `30_empire.js`, `40_realm_data.js` |
| Gold log | New Ledger section (collapsed): every Treasury change by turn — Envoy costs (with recoups), Condemned, extorts in/out (Tithe, Pillage, Spoils, Sack, tolls, faction / Holding extorts, by hand), Destabilize / Intercept income, loans, Influence exchange, End-turn income & upkeep split (Income & upkeep, Season, Winter tax, Trade). Edits by hand log as "adjusted" (quick ones merge). In / out totals per turn, running balance. Last 150 kept | `20_state.js` (`tGold`, `glogSync`), `30_empire.js` (`renderGlog`), `10_table.js`, `15_realm.js`, `50_battle.js`, `60_map.js`, `70_rules.js`, `80_scene_shell.js` |

## Follow-up (your answers)

| # | Answer | Change | Where |
|---|---|---|---|
| 1 | Starting Standing → Turn 1 | "(a Standing you start the game with: Turn 1)" | `RULES_push_simple.md` |
| 2 | Recurring Standing effects at Start | All Domain Standing effects resolve at the Start of the Empire Phase (one-time *Perform …* and *Each Empire Phase*); turn summary, checklist, host sheet, FAQ reworded | `RULES_push_simple.md`, `10_table.js`, `host_sheet.py`, `faq_export.py` |
| 3 | "requires X" for non-Roots too | Any Holding with a Root or complete chain line whose only unmet check is `infrastructure_req` (e.g. Conditioning Field from Common Land → "requires Muster Field") | `30_empire.js` (`pReqMiss`) |
| 3b | Build target select | Build option label is the Holding + source only. Second select = target Settlement: every built Settlement, auto-placement pick first and preselected ("auto"), ⚡ efficient marked, free Wards shown; Settlements that can't take it (Hamlet rule, full, Raw Material not in Reach) disabled with the reason. Perform blocked after Start game with no legal target. Map Settlement Build sends that Settlement | `10_table.js` (`buildPlaces`, `runBuild`, `pfForm`), `15_realm.js`, `60_map.js` |
| 4, 5 | No change | — | — |

## Files

`CE/TASK7_NOTES.md` · `CE/RULES_push_simple.md` · `CE/ENVOY_WINDOW_REVIEW.md` · `CE/references/{effect_registry.py,parity_efx.js,host_sheet.py,faq_export.py,settlement_board.html}` · `CE/references/board/{board.css,body.html}` · `CE/references/board/js/{10_table,15_realm,20_state,30_empire,40_realm_data,50_battle,60_map,70_rules,80_scene_shell}.js`
