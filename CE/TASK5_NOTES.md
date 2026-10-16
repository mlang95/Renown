# claude_task_5 — what changed, open items

Data: `renown_data_d10.py` (+ build copy `renown_data.py`). Rules: `RULES_push_simple.md`. Board: `references/gen_settlement_board.py` now assembles the page from `references/board/` (`board.css`, `body.html`, `js/*.js`) + `references/effect_registry.py`. Sprites: `sprites.py`.
Checks: `--check-rules` 0 mismatches · `wiki_markers.py` no unresolved markers · Rules.docx builds · `sprites.py --check` 0 problems (272 sprites) · `node parity_efx.js settlement_board.html` OK 13729 checks, 0 differences · old-vs-new parsed-effect equivalence 0 differences · 4-player drive (setup stepper → turns, Envoys, Perform, map actions, battle modal, spectate, inbox, HUD popovers, 390 px phone) no JS errors.

## Done

| Item | Change | Where |
|---|---|---|
| Chapel sprite | Chapel drawn in the Cathedral slot (in front of the core); Cathedral replaces it when built. Sheet centre-slot order includes the Chapel variant | `80_scene_shell.js`, `sprites.py` |
| Wonders | Each Wonder takes its own slot in the widened city (`WON_GAP` layout); 4 Wonders render side by side, no overlap | `80_scene_shell.js` |
| Diplomatic Mission ("Ulterior motive") | Only a Passed / Endorsed Diplomacy Envoy whose action fails allows a Mission; Failed / Condemned → none. Board: Mission offered only after Perform → "declined / failed" | RULES, `10_table.js` (`missionWhy`) |
| 1 Double Speak | Passed **or Endorsed** (Master Conspirator wording). Board offers Cunning actions on Endorsed too | data, board |
| 2 Envoy windows | `ENVOY_WINDOW_REVIEW.md`: 12 clauses limited to one Phase with no Personal / Council predicate (to review), 19 with no window (both), all 41 Envoy clauses. Windows are read from the text (`effect_registry.window_of`), so wording can change at will; regenerate with `--effects-report` | `ENVOY_WINDOW_REVIEW.md`, registry |
| 3 Toll House | No change | — |
| 4 Senate Hall | "At War Envoy" → "At War player's Envoy" (innate + mastery) | data |
| 5 Generate | Also next to each settlement name (culture's settlement bank, both) | `30_empire.js` |
| 6 Seats | Default and floor = player count | `10_table.js` (`seatFloor`) |
| 7 Edicts | Kept in HUD | — |
| 8 Sprites | Heraldry: shield in player colour + culture charge (15 charges, luminance-swapped). Shown on Domain track pawns, player table, Empire header, map banners. Build warns if a culture has no `her:` sprite | `sprites.py`, board |

### UX overhaul (1–15)

| # | Done as |
|---|---|
| 1 | Nav = Realm / Empire / Reference. Battle tab gone → modal over Realm (close button, Escape) |
| 2 | Action dock: phase card + only this phase's actions for you; Influence, loans, extort targets, once-per rows appear only in their Phase (`onceHTML(p,ph)`) |
| 3 | Map-first: Settlement → Build / Improve / Repair / Charter; Army card → Muster. Each opens the matching Envoy / action |
| 4 | One inbox (top bar, badge): flags, prompts, once-per reminders; resolve / ignore. Replaces flagbox / note scatter; toasts go through one `#flash` + log |
| 5 | HUD cells open popover breakdowns (Gold, Influence, PO, …); Ledger column narrowed, its stores moved into the HUD popovers |
| 6 | Player table: click row → spectate that empire (read-only badge, back button); hover → mini card |
| 7 | One Turn log with filters (mine / envoys / bandits / timers / story); Summary / Chronicle / history panels removed |
| 8 | Drawers → Turn log · Edicts · Tools |
| 9 | Setup stepper; closes after Begin Turn 1 |
| 10 | Empire filter bar also filters the catalog; wards as chips; clear / export / import → ⋯ menu; hide-combat → filter chip |
| 11 | Host controls folded into the phase card, hidden for non-Hosts |
| 12 | Pre-votes inline on Envoy rows |
| 13 | Spectators: controls hidden, read-only badge |
| 14 | Phone: bottom tab bar + sticky phase pill (phase + End turn) |
| 15 | Tactic matrix phrased "you win if…" per pairing, opponent's choice as column |

### Optimisation (1–6)

| # | Done as | Result |
|---|---|---|
| 1 | Map: terrain layer cached, only overlay / pieces redrawn; drawer bodies render only while open; `patch(el,html)` skips unchanged regions | `render()` 17–28 → 2 ms, `renderTable()` 2.1 → 0.1 ms, DOM 1065 → 597 nodes (fresh page, setup state, 1400 px, Chromium) |
| 2 | `render()` pure; mutations mark dirty, `saveIfDirty` writes once per event | no localStorage / undo / push per render |
| 3 | `effect_registry.py`: 86 patterns matched at build → `DATA.efx`; JS reads hits via `srcMatch(board,"id")` / `efxOf` / `hitOf` (all 71 old call sites migrated). Once-per rows, can't-restrictions, Speed clauses also from Python. `parity_efx.js` proves JS-regex replay = Python hits | `DATA.efx` 37 KB |
| 4 | Board split out of the Python string: `board.css` 695, `body.html` 206, 12 JS files 6.4k lines; generator 8.1k → 1.05k lines. Output still one HTML | — |
| 5 | Shared `loadoutFields` replaces the duplicate army / garrison `field()` | — |
| 6 | Delegated `data-do` handlers (77) for Realm, dock, inbox, map actions, battle modal | 141 element `onclick` remain (Empire builders, battle calculator, map inspector) |

## Behaviour changes to know

- Default view on load is Realm; Battle opens as a modal.
- Seat count can't go below the player count.
- Diplomatic Mission now needs Passed / Endorsed + failed action; old "any failed Diplomacy Envoy" path removed.
- Flags no longer show on the Empire board — they're in the inbox.
- Page size 1.32 → 2.0 MB: the committed page was built without fontTools, so it lacked the embedded EB Garamond (≈590 KB). Not new; built here with the font.

## Flags

| # | Topic | Detail |
|---|---|---|
| 1 | Eternal Sepulchre | Text "would ever be less than, 5 set it to 5" — stray comma, so `po_floor` never matches (pre-existing). Fix wording or confirm |
| 2 | Dead registry patterns | `piety_extra_doubt`, `po_mod_double`, `no_season_slow` match no current text (wording changed or piece gone). Listed in `ENVOY_WINDOW_REVIEW.md` → Registry coverage |
| 3 | Remaining text readers | Display-only: faction mechanic Holding-name parse (`30_empire.js`), Condemned "pay the action" check (`10_table.js`). Not in the registry |
| 4 | COMPREHENSIVE_RULES_OUTLINE | Gap 605 (Condemned = fail for Mission?) answered and removed; 508 updated |
| 5 | `build_all_CE.bat` / `rebuild_board.bat` | Both run `gen_settlement_board.py` inside `references/`; `board/` is located from the script's folder and `effect_registry.py` imports from it, so both bats work unchanged. Shipped `settlement_board.html` is built with `rebuild_board.bat`'s `PYTHONPATH` (Combatv4 + CE). Preflight file list doesn't name them; parity / effects-report not in the bat |

## Files

`CE/TASK5_NOTES.md` · `CE/ENVOY_WINDOW_REVIEW.md` · `CE/renown_data_d10.py` · `CE/renown_data.py` · `CE/RULES_push_simple.md` · `CE/sprites.py` · `CE/CLAUDE.md` · `CE/COMPREHENSIVE_RULES_OUTLINE.md` · `CE/REPO_MAP.md` · `CE/repo_map.py` · `CE/references/gen_settlement_board.py` · `CE/references/effect_registry.py` · `CE/references/parity_efx.js` · `CE/references/settlement_board.html` · `CE/references/board/**`
