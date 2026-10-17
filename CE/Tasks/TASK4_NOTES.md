# claude_task_4 — what changed, open questions

Data: `renown_data_d10.py` (+ build copy `renown_data.py`). Rules: `RULES_push_simple.md`. Board: `references/gen_settlement_board.py` (+ regenerated `settlement_board.html`).
Checks: `--check-rules` 0 mismatches · `wiki_markers.py` no unresolved markers · Rules.docx, playstyle reference, host sheet build · `node --check` on the board script · parsed-effect diff (all Holdings / Infra / Wonders / Factions, old vs new): only the texts listed below changed · board scenarios (4 players, generated map, Deploy, Wild placement, 3 full turns incl. Spring, Toll House / Beacon Towers move, Double Speak, Master Conspirator, Monastery, Reliquary, Interrogation Chambers, all views, all drawers, 390 px phone) with no JS errors.

## Done

| Item | Change | Where |
|---|---|---|
| Outlaw Country = one thing | Wild zones are ordinary Outlaw Country placed by the Host. A zone is a player's Outlaw Country while any of its Territories is in their Province (a Deploy zone in nobody's Province falls back to its nearest Settlement's owner, so Deploy checks still work). Spring: one camp per zone, any zone (full zone → its camps grow). Uprising / Foster / Smuggler's Nook / Local Unrest read the same ownership. Map: one look (no dashed purple) | data GLOSSARY, RULES (Setup 6, Outlaw Country rewritten, Spawning), board |
| 1 Illusionists | + Ossensteins (`CULTURES`) | data |
| 2 Double Speak | Text normalised (below). Board: Diplomacy Envoys take innate Authority from Cunning Standing (other Envoys unchanged); a Passed Diplomacy Envoy's Perform picker also lists Cunning actions (tagged "Cunning · The Illusionists"), modifiers/riders read the action's Domain; Alliance flag; Declare War / Sacred War restriction flag. Same mechanism now runs Master Conspirator (Sovereign Cunning, Passed or Endorsed non-Cunning Envoy, flagged once per Envoy Phase) | data, board |
| 3 Wild count | `floor(players / 2) + 1` (`WILD_OUTLAW.count "formula"`, `wild_outlaw_count`). 4 players → 3 zones | data, RULES, board |
| 4 Wild March | No change needed: camps outside every Province take no action; they still grow; at 100 they become Bandit Armies that Skirmish > Lay Siege > March. Rules text says so | RULES |
| 5 Timing | Beacon Towers / Baggage Train → `At the Start of the Empire Phase, you may …`. Toll House + Money Lending → `Once per turn` (phase-agnostic). New "Reading These Rules" line defines the four windows (Start of Empire Phase / Each <Phase> / Once per <Phase> / Once per turn). Tracker tags `Once per turn` rows "Any phase" (always lit) | data, RULES, board |
| Your text edits | All reflected in board triggers — see next table | board |
| HUD | One condensed row, label over value: Gold (+net), Influence (what you have this turn), Envoys, Public Order (value · band · F/D combined), Craft, Domains, Armies x/y, Settlements x/y · Wards, Edicts, Flags. Season / Era / Renown / per-turn / retinue text removed. "Hide others" line removed | board |
| Realm | Seat ring → player table above the map (one row per seat: Gold+net, Influence left/pool, Envoys, PO, Armies, Setts, Edicts, 4 Domains coloured by Standing, Status = phase state / vote / countdown; Host, 1st, you badges; sit / stand). Era line above it: Cities + Unlocks. Drawers: Players & Standings dropped; "Renown, Eras & Edicts" → Edicts only (no Renown stepper, no Era table, no starting universe); Diplomacy gets its own drawer when the module is on | board |
| Standings | One domain-board component: per Domain a 1–10 track (Rising / Established / Sovereign boxed) + the Standing effects table (with Battle lines from `STANDING_EFFECTS`). Reference: every player's pawn on their value and on each Standing they hold. Catalog: your tracks (click a cell to set) + your three Standing chips | board |
| Catalog | Root charts only (Type grouping + Arms…Works chips removed; Monument chip kept); ward picker groups by Root too | board |
| Empire | All / Holdings / Infrastructure / Armies bar moved under the name / faction / culture row. **Generate** next to the name (culture's `PLACE_NAMES` bank) | board |
| Cleanup | 11 unreferenced JS functions removed; `D.startDomains` retired (new players start Untested from `STANDING_THRESHOLDS`) | board |

### Text normalised (your edits)

| Piece | Now |
|---|---|
| Double Speak | Your Diplomacy Envoys use your Cunning Standing for their innate Authority. Whenever a Diplomacy Envoy you send Passes, you may instead perform a Cunning action. You can't perform Declare War or Sacred War actions, and you can't be a member of an Alliance. (summary line updated) |
| Beacon Towers (both) | At the Start of the Empire Phase, you may select an Army within your Province … |
| Baggage Train | … At the Start of the Empire Phase, you may perform a Move action. |
| Toll House | Once per turn: when an Army ends a Move action within your Province, Perform a Diplomacy action … |
| Money Lending | Once per turn, you may loan money … interest (minimum 100) … |
| Senate Hall (both) | Once per Envoy Phase: before players vote on an Envoy you choose, you may Condemn it if it's an At War Envoy, or Endorse it if it's an Ally's Envoy |
| Forgery Workshop / Execution Dock | capitalisation only |
| Pillage | "Extort subphase" → "Extort step" (the step's name in the Empire Phase list) |

### Your text edits → how the board triggers them

| Piece | Board |
|---|---|
| Interrogation Chambers: *Actions targeting this player that cause Doubt reduced by 1* | applies to every Domain (was Cunning-only match) |
| Reliquary: *First two Doubt each Empire Phase reduced by 1* | per-instance slots: each Doubt instance uses one slot (Empire Phase sources and action Doubt alike). Test: 2,2,2 → 1,1,2 |
| Monastery: *Other players with lower Piety value can't Oppose* | Oppose blocked only for voters with lower Piety |
| Execution Dock: *would cause Doubt before modifiers* | fires on base Doubt, even if reductions take it to 0 |
| Inn: *Influence +1* | counted in Influence |
| Money Lending: *Once per turn* | ⚑ on a second loan in the same turn |
| Courier Network (new wording) | tracker row + "1 fewer Envoy next turn" hook re-keyed; "perform that action in the Empire Phase" row tagged Empire |
| Toll House | non-allied Army ends a Move in your Province → Extort 2000 applied; Diplomacy-action prompt noted to the owner (once per turn) |
| Beacon Towers | Start-of-Empire row; non-allied Army ends a Move in your Province → "may immediately Move" prompt |
| Clandestine Councilor / Master Conspirator | their Influence +1 rows are gone (read from the text) |
| Indomitable, Forgery Workshop, Senate Hall | tracker rows only (act by hand) |
| Shipyard unlock → Rising Industry | data only |

## HUD — your question

Both are Faith / Doubt that move Public Order at the next Empire Phase; only the source differs. **Faith / Doubt** was your pieces' text (Holdings / Infrastructure "Faith +X", "Doubt +X"); **mods** was the `PO_MODIFIERS` rows (Deficit, Local Unrest, War Weariness, Lasting Legacy, Border Tension, …) plus other players' effects aimed at you. 0/0 with mods +1 = no piece Faith/Doubt, one modifier row of Faith. The PO cell now shows one combined F / D; the tooltip itemises both.

## Behaviour changes to know

- Spring spawns per **zone**: previously one per player + one per Wild zone, so a Wild zone inside your Reach could take two in one Spring.
- A zone touching two Provinces is both players' Outlaw Country (Uprising / Foster can land there for either; Nook carve-out excludes every Nook owner).
- Moving into another player's Province can now cost you 2000 (Toll House) automatically.
- Catalog ignores a stored "Type" grouping preference.
- Old saves: `startDomains` is dropped on load.

## Questions

| # | Topic | Question |
|---|---|---|
| 1 | Double Speak | "Passes" = Passed only (board), or Passed or Endorsed (Master Conspirator's wording)? |
| 2 | Envoy-Phase limits vs Council Envoys | Abbey, Courier Network (−1), Whispering Undercroft, High Chancery, Senate Hall say "Once per Envoy Phase", so Council Envoys (Council Phase) are out of reach. Intended, or should any be "Once per turn"? |
| 3 | Toll House | The Diplomacy clause says "an Army" (allied too, not your own); the Extort says non-Allied. Intended split? |
| 4 | Senate Hall | "At War Envoy" = an Envoy from a player At War with you? |
| 5 | Generate | Uses the culture's settlement-name bank. Want a separate ruler / house-name bank in worldlore? |
| 6 | Seats | Seat count stays a Host setting (default 6 → empty rows). Default seats = player count? |
| 7 | HUD | Keep Edicts in the HUD (also in the Edicts drawer)? |
| 8 | Domain markers | Pawns in player colour now. Swap for a sprite once `sprites.py` has a player-tinted figure? |

## Board code — structure

`gen_settlement_board.py` (8.1k lines) = one Python generator + one HTML template string.

| Block | Lines | What |
|---|---|---|
| Python | ~990 | `load` data → `build` records (`classify` atoms, `combine_parts`, `envoy_fx` for Envoy effects), `tree_payload`, `rules_payload` / `phase_steps` (rules md → HTML), `battle_data`, `bandit_loadouts`, place-name + sprite payloads, font subsetting, `check_rules`; `main` → `render_html` (template + `DATA` JSON + mapgen JS + fonts) |
| CSS | ~620 | theme tokens, per-view layout, phone media queries |
| HTML | ~200 | top bar (views, players, undo, ⋯) · turn strip · HUD · setup panel · Empire (Catalog / Board / Ledger) · Reference · Battle · Realm container |
| JS | ~6.2k | one script, sections below |

| JS section | Role |
|---|---|
| State & sync | `D` (whole game) + `S` (active board alias); `save` → localStorage + debounced `push` (per-part versions, 409 merge) + undo + activity log; `poll` |
| Table engine | `tSim` replays timestamped votes into the current Envoy; `tPlan`, pre-votes, timeouts; `tApply` / `resolveEnvoy` + `AA` action automation (costs, Faith / Doubt, effects, flags) |
| Empire model | settlements / wards, catalog, unlocks, Scope, infra requirements, armies, ledger totals, PO, Influence |
| Realm | `renderTable`, `tPanel` (phase card + your actions), drawers (summary, chronicle, timers, bandits, map tools, edicts, diplomacy) |
| Map | generator bridge, Reach / Territory, inspector, movement, sieges, bandits |
| Effect plumbing | `srcText` / `srcMatch` regex over active pieces' text at runtime; `boardFx` from Python-parsed `fx` |
| Rules mechanics | extort, loans, first Doubt, sieges / capture / sack, muster |
| Battle | queue, calculator, rolls; display layer, hover keywords, chat, builds |

## Optimisation / organisation findings

| # | Finding | Measured / count | Proposal |
|---|---|---|---|
| 1 | Every change re-renders the whole view | Realm 110 ms (map SVG string 16–23 ms, rest DOM rebuild), Reference 75 ms, Empire 26 ms; 189 `render()` call sites | Keep the map SVG node; redraw only overlays / pieces. Render drawers only while open (Edicts / Diplomacy already do) |
| 2 | `render()` calls `save()` | every render: localStorage write of `D`, undo record, debounced server push | Save only on mutations; render stays pure |
| 3 | Effect text parsed by regex in two places | Python `envoy_fx` + 47 `srcMatch` / 15 `srcHas` / 9 `SM` JS call sites, each re-splitting text | One Python-side effect registry (kind, values, timing window, trigger) shipped in `DATA`; JS reads fields, not text. Also gives `check_rules`-style "unparsed clause" reports |
| 4 | 6.2k lines of JS inside a Python raw string | no lint / highlighting; 17 lines > 400 chars | Move to `references/board/*.js` + `board.css`; generator concatenates (output stays one HTML file) |
| 5 | Duplicate code | `field()` defined twice (army / garrison cards); seat status logic was duplicated in seats + HUD others (now one table) | Shared card builders |
| 6 | Mixed event wiring | 29 document listeners + 169 `onclick=` assignments after `innerHTML` | Delegated `data-act` handlers only |
| 7 | Dead code | 11 functions removed this pass | Keep `node --check` + an unreferenced-function scan in the build |
| 8 | Internal names lag the UI | view ids `table` / `viewTable` = Realm, `board` = Empire, "Pursuit" in code | Rename in the split (item 4) |

## UX overhaul — options (pick any)

| # | Area | Option |
|---|---|---|
| 1 | Navigation | Realm = play, Empire = inspect / edit, Reference = rules. Battle becomes a modal over Realm (no tab) |
| 2 | Action dock | Right panel shows only what this phase lets *you* do: Council vote → Envoy declaration → vote / pre-vote → Perform → Domain Points. Influence, loans, extort targets, once-per rows appear as cards only in the phase they apply |
| 3 | Map-first | Click a Settlement → Build / Improve / Repair / Charter card; click an Army → Move / Muster / Siege / Pillage. Inspector becomes that card |
| 4 | One inbox | Flags, prompts (Toll House, Beacon Towers, Courier next turn), once-per reminders and notifications in one top-bar inbox with resolve / ignore; replaces flagbox / note / flash scatter |
| 5 | HUD drill-down | Click a HUD cell → popover breakdown (Gold, Influence, PO). Then the Ledger column shrinks to Treasury steppers + PO track, or folds into the popovers |
| 6 | Player table | Click a row → view that empire read-only (spectate); hover → mini card (holdings, armies) |
| 7 | One log | Merge Log, Summary, Chronicle, Timers & history into one Turn log with filters (mine / envoys / bandits / timers / story) |
| 8 | Drawers 6 → 3 | Turn log · Edicts · Tools (map setup, bandit controls, diplomacy matrix, timers) |
| 9 | Setup | Setup panel as a stepper that closes after Begin Turn 1 |
| 10 | Empire | All / Holdings / Infrastructure / Armies bar also filters the catalog; settlement cards show wards as chips; "Board" heading + clear / export / import → ⋯ menu; "hide combat/other" → filter chip |
| 11 | Host | Host controls collapse into the phase card when you're Host; hidden otherwise |
| 12 | Pre-votes | Inline on each Envoy row in the table instead of a separate panel |
| 13 | Spectators | Hide controls instead of disabling them; read-only badge |
| 14 | Phone | Bottom tab bar (Realm / Empire / Reference) + sticky phase pill (phase + End turn) |
| 15 | Battle teaching | Tactic matrix phrased as "you win if…" per pairing, with the opponent's choice shown as the column |

My order if you want one: 2 → 4 → 1 → 7/8 → 3 → 5 (2 and 4 remove the most tab-switching; 3 needs the Build / Improve / Repair actions from task 1).

## Files

`CE/TASK4_NOTES.md` (this) · `CE/renown_data_d10.py` · `CE/renown_data.py` · `CE/RULES_push_simple.md` · `CE/references/gen_settlement_board.py` · `CE/references/settlement_board.html` (built here; `rebuild_board.bat` regenerates it)
