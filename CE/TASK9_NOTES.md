# claude_task_9 — Rules.docx pass: what changed, open items

Answers used: Faith is Fickle = **acting** player's PO < 0 · Aura term = **Presence** · Wards = **abstract** (audit switch prepared) · Harbor = **Can Trade** (applied; prose + tables updated).
Skipped per prompt: Diplomacy phase rework.
Checks: `--check-rules` 0 mismatches · `wiki_markers.py` no unresolved markers · Rules.docx builds (36 pp, was 41) · wiki builds · `--effects-report` 0 to review · `node parity_efx.js` OK 13853 checks, 0 differences · page script `node --check` OK · Chromium (file): all views render, no JS errors; Faith is Fickle flag fires at PO −1, not at 0; `presR()` = 2.

## Done — prompt items

| Item | Change | Where |
|---|---|---|
| Envoy column (Era table) | Table widths now measured with real EB Garamond metrics; spare width goes to whichever column shortens the table most. Envoys 1285 → 2945 twips | `docx_tables._col_widths`, `_tw`, `_wrap_lines` |
| Wrap short-word columns | Same allocator: "Established Industry", "Alchemy, Forgotten Catacombs" columns wrap so Effect gets the room. Rows can't split across pages (`cantSplit`) | `docx_tables._col_widths`, `_table` |
| Faith is Fickle | `### Rule: Faith is Fickle` under Piety Actions: "While your Public Order is below 0, you can't target players with Piety actions." `FAITH_FICKLE_PO = 0`. Board flags it on any Piety action with a target player | `RULES_push_simple.md`, `renown_data_d10.py`, `70_rules.js` (`actRestrict`), `gen_settlement_board.py` (RULES_CONSTS) |
| Holdings by Standing | Holdings chapter grouped Domain → Standing (Prowess, Cunning, Piety, Industry; Rising → Sovereign), then "Any Domain" (1 Domain at Rising, 4 Domains at Established…). Two requirements = listed under both, "(also …)". Monuments in their Standing group, marked "(Monument)". One column grid for all Holding tables | `docx_tables.holdings` |
| Harbor "Can Trade" | Harbor innate: `Craft +2; Can Trade; Extort 500…`. Glossary **Can Trade**. Trade requirement, Trade Agreement treaty text, "Who Can Trade" prose updated. Board: registry `trade_no_roads` also matches `Can Trade` (Harbor, Shipyard now enable trade); flags read "Dirt Roads or Can Trade" | `renown_data_d10.py` (NODES, TRADE_RULES, TREATIES, GLOSSARY), `effect_registry.py`, `40_realm_data.js` |
| Fail / Resolve | Fail: "An unsuccessful combat roll or Envoy resolution." Resolve unchanged (already matched); `### Envoy Resolution Table` heading added so the glossary reference lands | `renown_data_d10.py`, `RULES_push_simple.md` |
| Aura → Presence | `aura` removed from RETINUES / SETTLEMENTS; `PRESENCE_RANGE = 2`. `### Rule: Presence` under Prowess Actions; Aura paragraph removed from Territory & Terrain; Move note points to the rule; glossary **Presence** (Army States). Board movement, Bandit Army pathing and camp targeting use the flat range; UI text "Presence" | `renown_data_d10.py`, `RULES_push_simple.md`, `00_core.js` (`presR`), `70_rules.js` (`auraSources`), `60_map.js` (`pieceAura`, `banditAuraList`) |
| Wards (abstract) | `WARD_MODEL = "abstract"`; `WARD_RULES` holds both texts ("abstract", "range1"); rules print `{{VAL:WARD_RULE}}`. Improve drops "into an adjacent Territory" unless `range1`. Glossary Settlement Ward follows the model. Board already treats Wards as slots; `WARD_MODEL` passed to `DATA.rulesConst` for the audit | `renown_data_d10.py`, `RULES_push_simple.md`, `gen_settlement_board.py` |
| Siege Timer table | Builds every "Siege Timer +X" from Holding / Infrastructure / Heritage text: adds **Office of Works +2, Keep +2, Fortress of Faith +3 (While PO ≥ 3)**. Attacker list adds **Colossus −2**. Note column names the source kind | `docx_tables.siege_calculus`, `_siege_text_sources` |
| Reading these Rules / Key Resources / Core Principles | Key Resources → **Resources** (one line each, numbers live in their sections). Principle 13 (Influence spending) removed — duplicate of Resolving an Envoy + Standing table. Sub-rules print as `2.1` with no bullet, indented. PEMDAS → **Order of operations**; Transitive property → **Equal values**; Mastery Chain / Scope split into 13.x / 14.x | `RULES_push_simple.md`, `md_to_docx.py` (nested lists), data `(Core Principle 13.)` refs |
| Empire Phase layout | 10 numbered steps with indented `3.1`-style sub-steps (Timers, Bandit Mechanics, Influence & Envoys, Taxes, Income & Upkeep, Public Order, Endurance). Board turn strip: sub-steps folded into each step's tip | `RULES_push_simple.md`, `gen_settlement_board.phase_steps` |
| Bandit tables | Armaments + Growth → one **Bandits by Era** table (Era · Retinues Gained per Turn · Armament). Duplicate `bandit_armaments` builder removed | `docx_tables.bandits_by_era` |
| Negate [keyword] | Immune / Negate glossary = Immune [keyword], Negate [keyword] | `GLOSSARY_CATEGORIES` |
| Tax season | Row removed from Trade table (Tax lives in Seasons / Empire Phase step 6) | `docx_tables.trade_rules` |

## Done — table order / homogenising

| Item | Change |
|---|---|
| Domain order | Domain board rows + Envoy Outcome rows follow resolution order (Diplomacy, Prowess, Cunning, Piety, Industry). Action chapters reordered the same way (Diplomacy first) |
| Seasons table | Cycle order from the Year season: Spring, Summer, Fall, Winter (data dict untouched) |
| Domain board | Untested column (all "—") dropped; Max Influence / Innate Influence rows dropped (repeated the Standing & Influence table) |
| Glossary order | Council & Envoys: Condemned, Failed, Passed, Endorsed (ascending, = table). Reading the Rules: action verbs first. Map & Range: + Uncontested (used in PO modifiers) |
| Battle | Empty "Begin Battle" / "End Battle" headings and duplicate "Begin Skirmish" steps removed → **Beginning a Battle** (Declare Army, Seize the Initiative) · Skirmish Steps (step 3 now applies Tactic / weapon modifiers) · **Ending a Battle**. Board plumbing renamed to match |
| Timer verbs | Timers "count down" (was increment / tick down); Edict streak timers "advance"; Siege "Timers … don't count down" |
| Holding upkeep prose | Was "fixed by Holding type: Monument 300, Power 200…" — SIMPLE uses Standing. Now `{{VAL:HOLDING_COST_TEXT}}` (Untested 100 / BT 1 … Sovereign 400 / BT 4; Natural 0) |
| Hamlet wording | "pursue" → "build"; "Husbandry Wards" (glossary) → Natural (matches SETTLEMENTS notes + Hamlets section); "can only be efficient" → "can only share a Ward with its parent" |
| Misc | Armies upkeep duplicate → reference; "Upkeep phase" → Income & Upkeep step; "Bandit Info" → Bandit Rules; Attacking a Bandit Camp deduped (Tactic table sits there); "Domain Identities & Traits" made a heading; "This game is for" list grammar; capitalised defined terms (Settlement, Army, Contested…) |

## Your call / flags (not changed)

| # | Item | Note |
|---|---|---|
| 1 | Faith is Fickle scope | Spread Truth has no target; Convert targets a Settlement. Does "target players" include their Settlements? Board flags any Piety action with a target player |
| 2 | Presence vs Hamlet / unbuilt Settlement | Unbuilt Settlements have no Presence (board, unchanged). Hamlets have Presence 2 like any Settlement |
| 3 | `range1` Ward variant | Text drafted only; board doesn't place Ward hexes. Flip `WARD_MODEL` to read it in the rules |
| 4 | SEASONS / glossary "increment" | Winter "Sieges do not increment", glossary Siege "does not increment in Winter" — data text, left as is (board reads it). Suggest "Siege Timers don't count down" |
| 5 | Seize the Initiative glossary | says "first round of combat"; rules say "first Skirmish" |
| 6 | Piety Rising "Shake +1" | "Shake" isn't a defined term (Morale?) |
| 7 | Sack | "raze all Holdings" and "removes all Holdings from one Ward" overlap |
| 8 | Bandits "may flee" | undefined mechanic |
| 9 | Synopsis player count | "1–7 (3+ preferred)" vs CLAUDE.md "3–7" |
| 10 | `build_edict` registry pattern | unmatched — already unmatched at HEAD (no Battering Ram "must Siege it as an Edict" text in data) |
| 11 | Two-column Actions | LibreOffice doesn't balance the last column (blank half page after Industry); Word balances continuous sections |
| 12 | "Ordinance Yard" | prints under that name in Holding / Siege tables (no display alias to Artillery Park) — pre-existing |

## Files

`CE/TASK9_NOTES.md` · `CE/RULES_push_simple.md` · `CE/renown_data_d10.py` (+ `renown_data.py` copy) · `CE/ENVOY_WINDOW_REVIEW.md` · `CE/REPO_MAP.md` · `CE/references/{md_to_docx.py,docx_tables.py,effect_registry.py,gen_settlement_board.py,settlement_board.html}` · `CE/references/board/js/{00_core,30_empire,40_realm_data,50_battle,60_map,70_rules}.js` · built: `Rules.docx`, `Rules.pdf`

## Follow-up 1 (your answers)

Data + rules = your uploads (Seize "first skirmish", Piety Rising "Morale +1", Faith is Fickle "players or their settlements", Bandits "may Rout as normal").

| # | Item | Change | Where |
|---|---|---|---|
| 1 | Faith is Fickle | Board flag text: "can't target players or their Settlements with Piety actions" (fires on any Piety action with a target player, Convert included) | `70_rules.js` |
| 4 | Timer wording | "increment" → "count down" in player text: Winter "Siege Timers don't count down"; glossary Siege; Siege Works / Siege Camp "Siege Timers count down in Winter"; Supply Depot "its Muster Timers count down"; Muster "Muster Timer counts down"; Raze "Damaged Build Timer doesn't count down". Registry `siege_winter` reads old + new wording | `renown_data_d10.py`, `effect_registry.py` |
| 7 | Sack | No change. "Its controller removes all Holdings from one Settlement Ward…, then removes that Ward from play" is in the Sack bullet, Siege Warfare → Resolving a Siege, step 3 | `RULES_push_simple.md` |
| 3, 9–12 | — | Left as is | — |

Checks re-run: `--check-rules` 0 · wiki markers none unresolved · effects 0 to review, 91/94 patterns · parity 0 differences · `node --check` OK · Chromium no JS errors, Fickle flag fires at PO −1 only · Rules.docx 37 pp.

## Follow-up 2 (Sack)

| Item | Change | Where |
|---|---|---|
| Sack rule | "Raze the top-most Holding of each Ward in the Settlement, Extort 2000 per Settlement tier; …" (rest as written) | `RULES_push_simple.md`; COSTS["Sack"] summary | 
| Board Sack | Wards read from the Settlement's chains (Holding in the slot + Holdings riding it, bottom → top; Heritage pieces take no Ward). Sack: top-most Holding of every other Ward → Damaged; the chosen Ward's Holdings leave play; tier −1; extort per tier; Sack Timer; Army Blocked + Strained. Picker = one radio per Ward ("Arable Land → Herb Garden"), was per-Holding checkboxes + raze-all | `70_rules.js` (`sackWards`, `sackApply`), `40_realm_data.js` (`siegeResolveHTML`, Sack button) |

Verified (Chromium): Town with Wards [Arable Land → Herb Garden] and [Quarry], remove Ward 2 → Herb Garden Damaged, Arable Land untouched, Quarry gone, Town → Village.
Checks re-run: `--check-rules` 0 · wiki markers none unresolved · effects 0 to review · parity 0 differences · `node --check` OK · no JS errors.
