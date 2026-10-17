# claude_task_3 — what changed, open questions

Data: `renown_data_d10.py` (+ build copy `renown_data.py`). Rules: `RULES_push_simple.md`. Board: `references/gen_settlement_board.py` (+ regenerated `settlement_board.html`). Host card: `references/host_sheet.py`.
Checks: `--check-rules` 0 mismatches · `wiki_markers.py` no unresolved markers · Rules.docx → PDF, wiki, playstyle reference, host sheet, domain board, settlement mats, FAQ build · parsed-effect diff (all Holdings / Infra / Factions, old vs new): no flat totals changed · board scenario (4 players, map, Deploy, Wild scatter, Spring spawn, camp actions, Wild March, Council → Envoy flow, all drawers, view switches) with no JS errors.

## Done

| Item | Change | Where |
|---|---|---|
| Scroll flicker | Cause: header compacted at scrollY > 60 → page got shorter → scroll clamped back under 60 → header expanded → loop (163 ↔ 287 px every frame). Scroll listener and `hdrc` CSS removed; header never changes size on scroll. Its height is measured by ResizeObserver → `--tbh` (Empire columns, Realm map/side panel size off it). Phones: header scrolls away (not sticky). Test: header height / scrollY / `--tbh` sampled 30 frames after wheel 20–300 px, 5 viewports × 3 views: old 4 unstable cases, new 0 | board CSS/JS |
| UX overhaul | **Realm** (was Table) = seat strip + map (left), sticky right panel: phase card → your actions (Council vote, declare, vote, Mission, DP, pre-votes, phase-limited effects, loans, extort) → Log → folded Influence/modifiers → Host controls. Drawers under the map (open state per device): Players & Standings, Renown/Eras/Edicts (old Realm tab, rendered only while open), Summary, Chronicle, Timers & history, Bandits, Map setup & tools. Old Realm tab removed (`realm` links/HUD tiles now open those drawers). Top bar: views · player chips · turn strip · one-line HUD; theme/shape/modules moved into ⋯; Setup panel moved below the header. Player name/colour/Faction/Culture/claim → player card at the top of Empire. Phone: action panel first, map behind a toggle. "wide" map toggle now off by default (new storage key) | board |
| Wild Outlaw Country (1–5) | Placed post-Deploy: scattered over unclaimed board, every hex Range 5+ from any Province and Range 5+ from other Outlaw Country zones, no water/mountain; farthest-first seeds, random ties; count = as many as fit (`WILD_OUTLAW.count "fill"`, optional `max`; `"formula"` keeps ceil(p/2)+1). Setup row: place ▸ / redo (clears camp-free Wild zones). Wild camps spawn, grow (incl. Spring) and March like others (flags kept, now True). Camp targeting (`BANDIT_CAMP_REACH = "province"`): players whose Province covers the camp → all their Settlements & Armies, nearest first; nobody's Province → no action. Smuggler's Nook carve-out unchanged | data, board, RULES (Setup 6, Wild Outlaw Country, Bandit Info, Army Behavior) |
| 7 Culture | Hidden in both catalog and Reference tree (empty charts drop out) | board |
| 10 Syntax | `At the start of each turn` → `Each Empire Phase` (Papal Palace Tithe, Velvet Hand); first-Doubt `at start of turn` / `each turn` → `each Empire Phase` (Episcopal Court, Reliquary); Jester `each Envoy Phase`; Crowned Star `Each Council Phase`; Broken Banner `Each Empire Phase` (×2); Domain Points `earned {{VAL}} each Rest Phase` + glossary from `DOMAIN_POINTS_PER_TURN`. Rules last step: "Resolve any remaining Each Empire Phase effects" | data, RULES, board regexes |
| 11 Costs | `COSTS` "<Domain> action" lines built from `ACTIONS` costs (rerun after the SIMPLE rename); "Tax per tier" from `SETTLEMENTS.tax_income`; "Pursue/Build action" cost from `ACTIONS` | data |
| 12 Glossary | Outlaw Country "starting at" filled from `OUTLAW_COUNTRY_START` | data |
| 13 Phases | New Empire step 1 **Start of the Empire Phase** (Activate is now step 2: Standings, then `Each Empire Phase (Activate)` effects). Start: Mimic, Friends in Low Places. Activate: Exalted Basilica, Cipher Chamber (both clauses). Once per Envoy Phase: Abbey, Grand Tournament (`3x per Envoy Phase`), Courier Network (both), Toll House, Forgery Workshop, Beacon Towers, Baggage Train, Senate Hall, Whispering Undercroft, High Chancery, Palatine. Board tracker tags each row with its phase (highlighted when current); exchange parser reads the new Grand Tournament text; host card + Empire checklist list the new step | data, RULES, board, host_sheet |
| Illusionists | Culture Ithiss; `FACTION_SUMMARIES` line (playstyle reference shows it). Board: Double Speak parsed (`domAs`) → innate Authority of every Domain Envoy (Personal + Council) uses Cunning Standing (Diplomacy keeps Era value); alliance ban parsed (`noAlliance`) → Diplomacy flag when an Illusionists / Elder Grove / Smoldering Crown / Dukedom player shares an Alliance (flag, not lock) | data, board |

## Behaviour changes to know

- A player's own Outlaw Country camps only act while they sit in someone's Province (normally the owner's; a Foster-expanded hex outside all Reach goes quiet).
- Wild Bandit Armies March from the interior toward the closest player like any Bandit Army (task 2's "dormant until settled" no longer holds for Armies; Wild camps still can't act until inside a Province).
- `COSTS["Industry action"]` now reads "2000 gold (Improve / Build / Charter); 0 gold (Repair)" — old text listed Repair at 2000; `ACTIONS` says 0.
- Claiming a player (server games) is on the Empire player card now, not the top bar.

## Questions

| # | Topic | Question |
|---|---|---|
| 1 | Illusionists culture | Mapped to Ithiss only. Also Shassolin (Cunning/Piety) or Astravantheliad (political control 5)? |
| 2 | Double Speak | Diplomacy Envoys keep the Era innate (they have no Domain value). Council Envoys use Cunning Standing. Correct? Text says "innate Influence" (prints as innate Authority via the display layer) and lowercase "cunning" — binding text left as written |
| 3 | Wild count | Fill gave 5–6 zones on a 26×21, 4-player map. Keep fill, cap it (`WILD_OUTLAW.max`), or back to formula? |
| 4 | Wild March | Confirm Wild Bandit Armies March at players from anywhere (see above), or March only once inside a Province? |
| 5 | Move holdings | Beacon Towers / Baggage Train set to Once per Envoy Phase (Move is an Envoy-phase action). Move them to Activate instead? |
| 6 | Other Activate fits | Candidates read the same way: Toll House (reaction, stays Envoy), Courier Network carry-over (stays Envoy). Nothing else found that "performs" at turn start |
| 7 | Phone header | Header now scrolls away on phones. Want a slim sticky phase pill (phase + End turn) there? |
| 8 | Realm drawers | Default open: Summary only. Any others open by default? |

## Files

`CE/TASK3_NOTES.md` (this) · `CE/renown_data_d10.py` · `CE/renown_data.py` · `CE/RULES_push_simple.md` · `CE/references/gen_settlement_board.py` · `CE/references/settlement_board.html` (built here; embeds the EB Garamond faces, ~600 KB more than your Windows build — `rebuild_board.bat` regenerates it) · `CE/references/host_sheet.py`
