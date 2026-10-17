# claude_task_6 — what changed, open items

Prompt says "response to TASK4_NOTES"; the Sepulchre / display-only / registry items answer TASK5_NOTES flags, so both were used.

Data: `renown_data_d10.py` (+ build copy `renown_data.py`). Board: `references/gen_settlement_board.py`, `references/effect_registry.py`, `references/board/**`, rebuilt `references/settlement_board.html`. Also `ENVOY_WINDOW_REVIEW.md`, `REPO_MAP.md`.
Checks: `--check-rules` 0 mismatches · `wiki_markers.py` no unresolved markers · Rules.docx builds · `--effects-report` 0 to review, 83/83 patterns used · `node parity_efx.js` OK 13326 checks, 0 differences · `node --check` · browser drive (4 players, generated map, Deploy, Wild placement, Build action, ward picker, all HUD popovers, Realm drawers, phases incl. Spring, End turn, spectate, Duke, Battle view, 390 px phone) no JS errors.

## Done

| Item | Change | Where |
|---|---|---|
| Catalog: Monument + Available / All | One line | `30_empire.js` |
| Catalog: 3 Standings | One line per Domain (chips shrink, full text on hover) | `board.css` |
| Spectators | Values stay on show read-only: Treasury, Settlement names, player name, culture, faction | `board.css`, `30_empire.js`, `body.html` |
| Upkeep breakdown | "Gold / turn" back in the Ledger (it had moved into the HUD popover only), plus INCOME by source (each Holding / Infra / Wonder with flat gold, scaling, Season, Winter tax, Trade) and COSTS (Holdings ×N, Infrastructure & Wonders ×N, Armies ×N, reductions), Net. Same rows in the HUD Gold popover and the player-table Gold hover | `30_empire.js` (`goldBreak`), `85_ux.js`, `body.html` |
| Factions by culture | Faction list = the culture's `CULTURES[*].factions` (Self-made = all; current pick stays listed). Culture select now before faction. Flag if faction isn't the culture's | generator payload, `30_empire.js` |
| Names | Generator skips every name on show (all Settlement names + player names). Unnamed Settlements get a default name on load, Start / New game, board clear, + player, and when a map piece links to a Settlement | `30_empire.js`, `60_map.js`, `80_scene_shell.js`, `90_app.js` |
| Battle before start | Battle tab in the top nav until Start game; afterwards with the Battle module (unchanged) | `body.html`, `30_empire.js` |
| Legal = "Available" | Scope + Standing, Root or one complete Mastery Chain line, `infrastructure_req`, Raw Material resource in Reach (per Settlement when one is chosen). Used by catalog Available, empty-Ward picker, Build action | `30_empire.js` (`pLegal`) |
| Empty-Ward click | Lists legal Holdings that fit that Ward or pair efficiently elsewhere (⚡ Settlement shown). Efficient pairing wins; otherwise the clicked Ward | `30_empire.js` (`effSpot`, `wpPlace`) |
| Build action (Realm) | Lists every legal Holding with its target ("Masonry · from Quarry → Rustwick"); non-Roots first. Target: Raw Material resource in Reach → efficient pairing → Natural to Hamlet → most empty Wards → largest tier → newest | `10_table.js`, `30_empire.js` (`smartSid`) |
| Status icons | 2× on Army / Settlement plates and Settlement marks; hover shows the status text | `60_map.js` |
| Status text | Intercept Caravan: "the next turn <player> is Host, their Trade Income goes to <who>" (+ "this turn" when they're Host). Destabilize reworded the same way. Trade line names the interceptor (was always "bandits") | `60_map.js`, `30_empire.js` |
| Sepulchre | Already matches after your comma fix (`po_floor`) | — |
| Personal | Texts: Outlaw Rookery, Colossus, Inner Circle (Palatine), Velvet Hand, Illusionists (Cunning-action clause) now say Personal. "Once per Envoy Phase" clauses (Abbey … Cunning Sovereign) read as Personal by Phase — no text change; report shows "personal (by Phase)" | data, `effect_registry.window_of`, `envoy_fx` |
| Registry | `piety_extra_doubt` + `piety_doubt_or_faith` → `basilica_amp` (Exalted Basilica: target gains Faith +1 and Doubt +1, applied on Piety actions). `po_mod_double` removed (Charnel House was already handled by `po_band_double`). `no_season_slow` removed (Meadery's Speed +2 in Winter already applies via Speed rows) | `effect_registry.py`, `10_table.js`, `40_realm_data.js`, `70_rules.js`, `80_scene_shell.js` |
| Duke End turn | DUKE badge + End turn in one right-hand group; phase steps shrink instead of wrapping | `80_scene_shell.js`, `board.css` |
| Player table hover | Each cell shows its descriptors like the PO hover: Gold (income / costs), Influence sources, Envoys, PO (Faith / Doubt sources), Armies, Settlements (Wards), Edicts, each Domain (value, Standing, active Standing effects). Empire mini card on the name cell only | `15_realm.js`, `80_scene_shell.js` (`hudTips`), `90_app.js` |
| Wild Outlaw Country | `border_range` 5 → 3. Seeds nearest the map centre first, zones grow compactly round the seed | data, `60_map.js` |
| Wild placer | "Wild Outlaw" tool removed. Outlaw Country tool: joins a neighbouring Wild zone; outside every Province starts one (Host only) | `60_map.js` |
| Spring | No Council Phase: next phase from Empire is Envoy; Council skipped in the phase bar; Council vote blocked | `10_table.js`, `15_realm.js`, `80_scene_shell.js`, `85_ux.js` |
| 8/7 Domain status | Allowed total counts the Rest Phase Domain Point before End turn raises Renown | `15_realm.js` |

## Answers

**Diplomacy as a Council vote option** — no change. Rules: the Council votes on a Domain (Industry / Prowess / Cunning / Piety); Diplomacy isn't a Domain (free Envoy actions resolved before Domain Envoys).

**Display-only text readers (examples)**

| Reader | Example |
|---|---|
| Faction mechanic Holding-name parse (`factionFlags`, `30_empire.js`) | The Ashen Vale: "You can't build an Apothecary, Infirmary, or Hospitaller." The board regexes the faction text at run time and flags any of those placed. Flag only; not in `effect_registry`, so `parity_efx` / effects-report don't see it |
| Condemned "pay the action" (`10_table.js`) | Cunning / Piety Condemned outcome: "Doubt 1 + pay the action's cost". If no action was recorded, the board reads that text and flags "Condemned: pay the cost of the Cunning action you'd have performed" |

**Start of the Empire Phase vs Activate** (current data)

| Window | Piece | Clause |
|---|---|---|
| Start of the Empire Phase | Beacon Towers | you may select an Army within your Province and move it up to its modified Speed |
| | Baggage Train | you may perform a Move action |
| | The Bandit King | you may control one Bandit Camp outside your Territory |
| Each Empire Phase (Activate) | Exalted Basilica | you may perform an Endorsed Spread Truth |
| | Cipher Chamber | select an army you did not select last turn |
| | Cipher Chamber | select any active Timer you did not select last turn |

Rules order: Start of the Empire Phase → Activate (Standing effects, then "(Activate)" effects) → Season. Nothing resolves between them, so one step works ("Start of the Empire Phase: resolve those effects, then Standing effects"). Only difference left is Standing effects resolving after the Move effects.

## Questions

| # | Topic | Question |
|---|---|---|
| 1 | Start / Activate | Merge into one step and reword "Each Empire Phase (Activate)" → "At the Start of the Empire Phase"? Standing effects before or after? |
| 2 | Courtyard / Inn | Roots, but `infrastructure_req` Town Hall / Hitching Post — they show under Available / Build only once those are active. Keep the requirement, or make Root mean "no requirement at all"? |
| 3 | Build with no free Ward | Legal Holdings with nowhere to go still list as "→ no free Ward" (placed Unplaced). Hide them instead? |
| 4 | Ward picker | Natural Holdings: efficient pairing first, then the clicked Ward (your wording). The Build action sends them to a Hamlet. Same rule for both? |
| 5 | Wild range | `border_range` 3 set as you suggested; `spacing` still 5 |
| 6 | Velvet Hand | Second clause "if that Envoy was endorsed…" still has no predicate (it refers back to the Personal Envoy) — fine as is? |

## Files

`CE/TASK6_NOTES.md` · `CE/renown_data_d10.py` · `CE/renown_data.py` · `CE/ENVOY_WINDOW_REVIEW.md` · `CE/REPO_MAP.md` · `CE/references/gen_settlement_board.py` · `CE/references/effect_registry.py` · `CE/references/settlement_board.html` · `CE/references/board/board.css` · `CE/references/board/body.html` · `CE/references/board/js/{10_table,15_realm,30_empire,40_realm_data,60_map,70_rules,80_scene_shell,85_ux,90_app}.js`
