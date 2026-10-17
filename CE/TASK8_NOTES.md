# claude_task_8 — what changed, open items

Response to TASK7_NOTES + claude_task_8. Answers used: faction fields into FACTIONS · "FACTIONS updated" = board handles each mechanic · final cut strict + reassign proposals (below, not applied) · Fall doubles flat + Fall-only gold of Hamlet Holdings (no scaling gold).
Checks: `--check-rules` 0 mismatches · `wiki_markers.py` no unresolved markers · Rules.docx builds · faction cards / playstyle PDFs build · FAQ export · `--effects-report` 0 to review, 93/94 patterns used (`fac_type_bonus` = old Luminous Court wording, kept) · `node parity_efx.js` OK 13777 checks, 0 differences · page script `node --check` OK · browser (Chromium, server + file): faction picker, Standings, Battle terrain, Realm table, 390 px phone — no JS errors.

## Done

| Item | Change | Where |
|---|---|---|
| Battle terrain | Tile column = pixel hex (map fill + scattered SCATTER prop sprites, same as the map); glyph swatch only if sprites absent | `60_map.js` (`pxSwatch`, `propPaths`, `mapScatter(..., inline)`) |
| Pips → heraldry | `pTok`: heraldry flag if the player has a culture, else the colour pip — never both. Realm table, player chips, Diplomacy, timers, Turn log, Battle headers, map inspector, Place bar, setup checklist | `80_scene_shell.js` (`pTok`), `10_table.js` (`tName`), `15_realm.js`, `30_empire.js`, `40_realm_data.js`, `50_battle.js`, `60_map.js`, `board.css` |
| Tactic matrix | Collapsible removed; Reference nav "Tactics & Skirmish rules" | `50_battle.js`, `10_table.js` |
| Standings + Domain table | One table: track points underlaid behind each Standing (Rising 1–3, Established 4–6, Sovereign 7–10); viewer's points fill; cell lights (glow, title coloured) at the threshold; every player's marker under its point. Scrolls sideways on phone | `50_battle.js` (`standingEffectsHTML`), `board.css` |
| Final cut | Selector offers final-cut factions only (culture filter still applies); a non-final current pick stays listed, marked | `30_empire.js` (`facOffered`) |
| Faction data | FACTIONS[k] gains `mechanic_name`, `summary`; `mechanic` no longer carries "Name:"; FACTION_SUMMARIES removed; FACTION_NAMES from `mechanic_name`. Cards / compendium / FAQ csv / playstyle read the new fields (printed text unchanged) | `renown_data_d10.py`, `faction_sheet.py`, `gen_compendium.py`, `faq_export.py`, `playstyle_reference.py`, `gen_settlement_board.py` |
| Summary on hover | Faction picker is a list (not a native select): hover / focus / arrow keys show the summary. Faction box collapsed shows the summary under the name | `30_empire.js` (`facPicker`, `renderFaction`), `board.css` |
| Name swap | NAME_DISPLAY already had it; verified: "The Eternal Sepulchre" → "The Exalted Archbasilica", "Exalted Basilica" → "Eternal Sepulchre", no cascade (data + board) | — |
| SEASONS | Fall: `Income from Holdings in <tier>s …doubled` → each active Holding in a Hamlet earns its flat gold + Fall-only gold again (Ledger, season strip, End turn). Old `<Type> Income is doubled` still read. Spring: Support/Oppose with Influence flags "players don't spend Influence tokens". Winter Speed −5 / no Siege tick / Spring no Bandit actions: already read from text | `30_empire.js` (`tierGoldFor`, `seasonDblGold`), `15_realm.js` |

## Faction mechanics on the board (final cut)

| Faction | Was | Now | Where |
|---|---|---|---|
| Bandit King | "cannot Build Holdings which require Piety or Prowess" not read | flagged per Holding | `30_empire.js` (`factionFlags`) |
| Smoldering Crown | Renown limits not read | flags Piety above Untested, Industry > 3 | `factionFlags`; registry `no_renown_into`, `domain_max` |
| Winter Wolves | "cannot join an alliance" missed by the Alliance check | Alliance flag | registry `no_alliance`, `envoy_fx` |
| Crimson Tide | restriction wrongly flagged Crimson Tide's own Intercept Caravan | flags others targeting it | registry `cant_on_you`, CANT_SKIP (+ parity copy) |
| Merchant Republics | "can't be Razed" flagged its own Raze action | fixed; trade gate: no trade income without a Trade Agreement with them (or At War with them); line explains | CANT_SKIP; registry `trade_gate`; `tradeRaw` |
| Iron Throne | "(and your Alliance)" ignored | allies flagged on Declare / Sacred War | registry `ally_cant`; `actRestrict` |
| Sacred Throne | none | Declare War / Sacred War on them: attacker + allies Doubt +5 | registry `war_on_you_doubt`; `warOnFac` |
| Iron Shore | Raze extort not read | Raze on them extorts 2000 from the razer | registry `raze_extort`; Raze action |
| Tunnellers | mountains Impassable for them | mountain moves as grassland (no Strain) | registry `mountain_grass`; `70_rules.js` |
| Battering Ram | none | Improve → Citadel flags "must Siege it as an Edict" | registry `build_edict`; `runImprove` |
| Dukedom | none | war on the Duke flags the treaty voiding / everyone Declares War (by hand) | registry `duke_war` |
| Luminous Court (not final) | craft / no-upkeep bonus lost after its wording change | reads "Holdings which require Piety" | registry `fac_dom_bonus`; `facTypeBonus` |

Already handled, verified: Crowned Star, Hermit Crown, Eternal Court, Final Word, Illuminated Order, Iron Faith, Undying Flame, Verdant Kingdom, Ancient Wilds, Bloodied Cross, Pale Throne, Ashen Vale, Elder Grove, Yew Heart, Entwined Crown, Boundless Steppe (start pieces).
Not automated (social / Host): Bandit King camp control, Ancient Wilds NAP acceptance, Dukedom starting NAPs + trade, Merchant Republics "must attempt to Sign".

## Your call

**CULTURES — final-cut reassign (Strict + reassign; nothing applied).** Basis: overlap of the faction's pair / complement Monuments with the culture's Monuments, and no clash with the culture's Domains.

| Culture | Final now | Add |
|---|---|---|
| Ossensteins | 0 | The Merchant Republics, The Iron Faith, The Illuminated Order |
| Prezish | 1 | The Crimson Tide (2 overlaps) |
| Sarkopekt | 1 | The Boundless Steppe (2), The Ancient Wilds (2), The Battering Ram |
Avoid: Verdant Kingdom (no Cunning actions) in Cunning cultures; Smoldering Crown (Industry ≤ 3) in Industry cultures.

**CULTURES — other flags.**

| Culture | Issue | Suggest |
|---|---|---|
| Trusteki | lists all 4 Wonders (others 1–2) | The Grand Exchange (+ Colossus) |
| Ossensteins | no Piety Monument; no Industry action | + Inquisitorial Palace; swap Intercept Caravan → Build / Improve |
| Voldrastel | no Industry Monument; no Piety action | + Office of Works; Sign Treaty → Tithe / Spread Truth |
| Sarkopekt | actions have no Cunning / Industry | Negotiate → Intercept Caravan or Improve |
| Prezish | no Industry action (2 Diplomacy) | Negotiate → Build |
| Madekites | 2 Monuments (others 3–4) | + Exalted Basilica or Port Authority |
| Cailendroffs | Colossus only, 3 Domains | + The Eternal Sepulchre or High Chancery |
| Radar | no tournament data per culture; values only changed if the above are applied | — |

**Summaries out of date** (kept as written; proposed text):

| Faction | Summary now | Proposed |
|---|---|---|
| Crowned Star | …your Envoys −1 | Chooses every Council Envoy's Domain; abstains every Personal Envoy |
| Hermit Crown | …your Envoys cost double to sway | Always Abstains; 2 Influence to sway your Envoys by 1; Personal Envoys +1; no votes or Council Envoys |
| Smoldering Crown | Strong Cunning Envoys; no Alliances or Diplomacy | + Secret Cellar; Prowess Envoys always pass; no Renown into Piety, Industry ≤ 3 |
| Bandit King | Starts with Smuggler's Nook; controls a Bandit Camp | + no Piety or Prowess Holdings |
| Iron Shore | Spoils win or lose; recoups lost Retinues | Spoils win or lose; extorts 2000 from whoever Razes you |
| Winter Wolves | No upkeep in at-war Territory; ignores Winter Speed | At war, Armies extort their upkeep from at-war Settlements; no Alliances |

**Other flags.**
- Sprites: `wonder:The Eternal Sepulchre` (stepped tomb) now reads "Exalted Archbasilica"; `monument:Exalted Basilica` reads "Eternal Sepulchre". Swap the art? (`sprites.py`)
- SEASONS Fall grammar: "Income from Holdings in Hamlets are doubled" → "is doubled" (board reads either).
- `patch_cultures.py` (not in the build) still writes FACTION_SUMMARIES — retire it or re-run it never.

## Files

`CE/TASK8_NOTES.md` · `CE/renown_data_d10.py` · `CE/sprites.py` · `CE/ENVOY_WINDOW_REVIEW.md` · `CE/references/{effect_registry.py,parity_efx.js,gen_settlement_board.py,faction_sheet.py,gen_compendium.py,faq_export.py,playstyle_reference.py,settlement_board.html}` · `CE/references/board/board.css` · `CE/references/board/js/{00_core,10_table,15_realm,20_state,30_empire,40_realm_data,50_battle,60_map,70_rules,80_scene_shell}.js`

## Follow-up (your answers)

| Item | Change | Where |
|---|---|---|
| Ossensteins | + The Illuminated Order, The Eternal Court (Patient Court) | `renown_data_d10.py` CULTURES |
| Prezish | + The Crimson Tide | same |
| Sarkopekt | + The Boundless Steppe, The Ancient Wilds, The Battering Ram | same |
| Summaries | Crowned Star, Hermit Crown, Smoldering Crown, Bandit King, Iron Shore, Winter Wolves rewritten as proposed | `renown_data_d10.py` FACTIONS |
| Art swap | `monument:Exalted Basilica` (reads Eternal Sepulchre) = stepped tomb; `wonder:The Eternal Sepulchre` (reads Exalted Archbasilica) = basilica | `sprites.py` |
| New sprites | Priory (chapel + cloister arcade), Masons' Guild (stone guildhall + sign) — were falling back to their group sprite; now 99/99 Holdings have their own | `sprites.py` |
| Monument toggle | Catalog shows every Monument as one flat list, sorted by displayed name; no Root groups | `30_empire.js` (`renderList`) |

Not changed (no answer): other CULTURES flags (wonders / monuments / actions), Fall "are" → "is", `patch_cultures.py`.
Checks re-run: `--check-rules` 0 · wiki markers none unresolved · effects 0 to review · parity 0 differences · `node --check` OK · `sprites.py --check` 0 problems · browser no JS errors.

## Follow-up 2 (CULTURES flags)

Found already in the data when I started (your edits, kept as written): Ossensteins `Intercept Caravan` → `Build` (prints **Improve** under SIMPLE; `Pursue` would print Build), + Inquisitorial Palace · Voldrastel `Sign Treaty` → `Tithe`, + Office of Works · Sarkopekt `Negotiate` → `Sabotage` · Prezish `Negotiate` → `Pursue` (prints Build) · Cailendroffs + High Chancery.

| Item | Change | Where |
|---|---|---|
| Madekites | Monuments + Exalted Basilica, Port Authority (SIMPLE list) | `renown_data_d10.py` SIMPLE CULTURES monuments |
| Trusteki | not listed — unchanged (still 4 Wonders) | — |
| Catalog wrap | Unlock label wraps to its own lines (max ~half the row, right-aligned); the name keeps whole words (min width), so "Sacred Preceptory" no longer breaks mid-word | `board.css` (`.row .rtop .nm / .meta`) |

**Radar** (one step each, from the changes above):

| Culture | Axis | Was → Now | Why |
|---|---|---|---|
| Ossensteins | doubt_warfare | 4 → 3 | Intercept Caravan dropped |
| | faith_management | 3 → 4 | + Inquisitorial Palace, Tithe |
| | political_control | 4 → 5 | + Eternal Court, Illuminated Order |
| Voldrastel | political_control | 4 → 3 | Sign Treaty dropped |
| | faith_management | 3 → 4 | + Tithe |
| Sarkopekt | political_control | 3 → 2 | Negotiate dropped |
| | degenerate_punishment | 4 → 5 | + Sabotage |
| | board_presence | 4 → 5 | + Boundless Steppe, Ancient Wilds, Battering Ram |
| Prezish | political_control | 4 → 3 | Negotiate dropped |
| Madekites | economy_generators | 4 → 5 | + Port Authority |
| Cailendroffs | political_control | 3 → 4 | + High Chancery |

Still open: Fall "are" → "is", `patch_cultures.py`.
Checks re-run: `--check-rules` 0 · wiki markers none unresolved · effects 0 to review · parity 0 differences · playstyle reference builds · browser no JS errors.

## Follow-up 3 (Piety rider split)

Data = your upload (Unforgotten Shrine split from Exalted Basilica; Fall "is doubled").

| Item | Change | Where |
|---|---|---|
| Piety rider | "When your Piety actions give their target Faith, it gains Faith +1 more; when they give Doubt, it gains Doubt +1 more": adds +1 only to what the action gave, to each player it gave it to (Spread Truth: allies Faith +1 more, others Doubt +1 more). Was: Faith +1 and Doubt +1 to the target, always | registry `basilica_amp` (whole-text scope — the clause split cut it at ";"), `10_table.js` (`resolveEnvoy`: tracks Faith given, `faithTo`) |
| Rider preview | Envoy action riders list the Shrine line | `70_rules.js` (`actRiders`) |
| Sprite | Unforgotten Shrine (wayside shrine, candle, offerings); 100/100 Holdings own art | `sprites.py` |
| Charts | layout.json / layout_simple.json / layout_roots.json regenerated for the new node (tree PDF skipped here: no svglib) | `references/` |

Verified: Spread Truth → each non-ally Doubt +1, then Doubt +1 more, no Faith; Send Missionaries (outside your Alliance) → Doubt +2, then +1 more.
Unused registry patterns (old wording, harmless): `rider_your_extra`, `fac_type_bonus`.
Checks: `--check-rules` 0 · wiki markers none unresolved · effects 0 to review · parity 0 differences · `node --check` OK · `sprites.py --check` 0 problems.

## Follow-up 4 (scene, factions, heraldry)

| Item | Change | Where |
|---|---|---|
| Eternal Sepulchre art | Grand shrine on the Pilgrimage Site's mound: stone cross, gabled tomb-shrine, glowing niche, candles | `sprites.py` (`monument:Exalted Basilica`) |
| Wonders | Redrawn 32 px tall (Colossus: crowned bronze figure, torch, spear; Grand Exchange: colonnade + gold dome; Archbasilica: twin bell towers, rose window; High Chancery: clock tower + wings). Drawn behind the Settlement, raised 5 px, foundation filled down; tuck behind the core, alternate sides, overlap. One Wonder no longer widens the lot | `sprites.py` (S32), `80_scene_shell.js` (`wonOffsets`, `WON_TUCK / WON_OVER / WON_LIFT / WON_HAZE`) |
| Holdings in the scene | Spread evenly across the lot (≤ 24 px apart) instead of bunched in the centre | `80_scene_shell.js` |
| Faction list | "all cultures" checkbox: every final-cut faction whatever the culture (per device) | `30_empire.js` (`FAC_ALL`) |
| Self-made heraldry | No culture → the player card shield opens a grid of all 15 charges in the player's colour; pick saved on the board (`board.heraldry`), used everywhere heraldry shows; a culture's own charge overrides it | `30_empire.js` (`herPicker`), `80_scene_shell.js` (`herCharge`), `board.css` |
