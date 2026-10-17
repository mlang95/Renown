# Proposals — "New things to consider" + rules syntax pass

Format per item: **Now** (what the data, rules, and board do today) · **Options** · **Trade-offs** · **Needs your call**.
Nothing here is implemented.

---

## 1. Scale negative Public Order effects by Era

**Now:** `PUBLIC_ORDER` uses flat values: −2 → −1 Influence, −3 → Speed −2, −4 → −1000 Tax per Settlement, −5 → 1 Bandit Camp. Era Influence income scales 1→4 (`ERAS.influence_per_turn`). `BANDIT_GROWTH_PER_ERA` already scales 1/2/3/4.

**Options:**
- **A (your example):** each Era gets a multiplier of 1, 2, 3, or 4. Negative bands multiply by it.
  - Ascension: −2 Influence, Speed −4, −2000 Tax, 2 camps.
  - Implementation: write the values as `{n}` templates in `PUBLIC_ORDER` and add `po_scale` to `ERAS`. Rules and board both read from these.
- **B:** scale the positive bands the same way (+2 → +2 Influence in Ascension, and so on). The PO track then stays symmetric.
- **C:** scale Influence and Tax only. Speed and camps stay flat.

**Trade-offs:**
- In Zenith, Uprising spawns 4 camps. The "full → grow" rule turns the excess into growth, so it stays bounded.
- Speed −8 in Zenith makes an army immobile (Levy speed is 5). That may be the intent; flag it.
- A punishes low PO harder late but leaves high PO no more rewarding. B keeps the incentive balanced.

**Needs your call:** A, B, or C. Should Speed and camps scale at all?

---

## 2. Merge the Empire and Rest phases

**Now:** Rest = discard Envoys/Influence → Season +1 → Renown → Domain Point → pass Host → next Empire. Empire step 1 activates Standing effects.

**Options:**
- **A — Merge:** the Empire Phase opens with the Rest steps (discard, Season, Renown, Domain Point, Host), then the current Empire steps.
  - Effect order is unchanged: the new Standing is still active before income.
  - Turn 1 skips the Rest block.
- **B — Keep Rest, rename it "Upkeep":** the board treats Rest as a short checkpoint that is still required, and the Domain Point gate already lives there.
- **C — Merge on the board only:** the board shows one phase with a two-step header. The rules keep 5 phases.

**Trade-offs:**
- A has one fewer phase to track and the same order.
- A loses the pause after battles, where siege outcomes, vassal returns ("end of the Rest Phase"), and the Host pass settle.
- A changes rules text that points at "end of the Rest Phase" (Vassalage step 2) and "before the Rest Phase" (Siege).
- The board's Domain Point gate (`dpOwed` blocks End Turn) would move to the first step of Empire.

**Needs your call:** A, B, or C. Under A, which anchor do Vassal returns and Siege resolution use?

---

## 3. Auras decide bandit targets

**Now:**
- `RETINUES.aura` (Levy 1, MaA/Sergeant/Templar 2) and `SETTLEMENTS.aura` (Hamlet 3, …) exist in the data.
- On the board, auras only **block Bandit Army movement**: bandits can't path through or end in another piece's aura.
- `BANDIT_BEHAVIOR` targets by priority and range: "Skirmish > Lay Siege > March; Host breaks range ties". On the board, ties are broken at random and flagged.
- Cunning-roll targets (Intercept, Raze, Destabilize) are the nearest eligible Settlement (`byDist`). Aura plays no part.

**Options:**
- **A — Aura = threat:** a camp targets whoever has the most aura overlapping it. Ties go to the nearest piece, then the Host.
- **B — Aura = protection:** a camp can't target pieces inside another piece's aura, so bandits pick soft targets. This rewards spreading garrisons.
- **C — Aura = trigger range:** a Cunning action fires only against settlements whose aura reaches the camp. This replaces Host choice.

**Trade-offs:**
- A is deterministic and removes the Host's tie-break role.
- B creates real positional play.
- C is the smallest rules change.
- All three replace nearest-first and random tie-breaks. The rules text says the Host breaks ties, so the rules change either way.

**Needs your call:** A, B, or C, or a combination such as C for Cunning actions plus A for army moves.

---

## 4. Outlaw zones in the middle of the map

**Now:** 3 Outlaw Country territories per player at setup. They are within range 1 of each other and range 2+ from any Settlement (`OUTLAW_COUNTRY_START`, `OUTLAW_BUFFER_RANGE`). In practice they sit near each player.

**Options:**
- **A — Shared wild zones:** add N neutral Outlaw Countries (for example players ÷ 2), seeded in the interior with distance from all starts maximised. Camps there belong to no player's PO.
- **B — Bias player zones inward:** keep per-player zones, but place them on the far side of the player's capital, toward map centre.
- **C — Both:** per-player zones plus 1–2 central zones that grow faster.

**Trade-offs:**
- A needs new ownership rules: Local Unrest and Uprising are currently keyed to "your" Outlaw Country.
- B is placement only, with no rules change.
- C raises total bandit pressure.

**Needs your call:** Do neutral zones exist? If yes, what triggers their spawns, since no player's PO feeds them?

---

## 5. Culture / self-made filter

**Now:** `CULTURES` has 15 entries (4 pure, 6 pair, 4 triple, 1 centre). Each lists its domains, monuments, wonders, actions, factions, and a radar profile. The board has no culture concept. "Self-made" isn't in the data.

**Options:**
- **A — Derived culture:** the board infers culture from the Domain Point pattern, matching the dominant 1–4 domains to a culture. "Self-made" means no culture is locked.
- **B — Chosen culture:** a dropdown on the player card.
  - The Holding tree, Reference, and catalog dim anything outside the culture's domains, monuments, and wonders.
  - "Self-made" shows everything.
- **C — Filter only:** a per-viewer UI filter with no game effect.

**Trade-offs:**
- A needs no new input but can flip mid-game.
- B is explicit and easy to read.
- C has zero rules impact.
- Whether choosing a culture has game effects is a design decision; none are stated in the data.

**Needs your call:** Is culture a game choice or a view filter? What does self-made mean mechanically, if anything?

---

## 6. Generated town names

**Now:**
- `worldbuilding/renown_worldlore.py` has person-name grammars for each pure culture, for example "[name] of the [Warband]".
- It also has map `naming_registers`: constructed, overt-grim, understated-grim, and plain-centre.
- There are no place-name banks.

**Proposal:**
- Add `PLACE_NAMES[culture] = {patterns, syllables/roots}` to worldlore.
- The board generates a name when a Settlement is chartered, from the culture (option 5A or 5B) or from the map register for self-made players.
- Names can be edited, and they go into the turn story (item 7).

**Needs your call:** The name banks are lore. I need you to write them, or approve a draft for each culture. I won't invent them unasked.

---

## 7. Story-style turn summary

**Now:** the Summary log records per-line facts: Empire/Timers, Bandits by Outlaw Country, Envoys, Notices, and Domain Points.

**Proposal:**
- **Event filter:** keep only macro events.
  - Monument or Wonder completed
  - War declared or peace made
  - Non-bandit Battle (won or lost)
  - Settlement sacked, captured, or converted
  - Envoy Condemned
  - Era change
  - Capital besieged
  - Vassalage
  - Camp becomes a Bandit Army
- **Templates:** one sentence template per event type, with 2–3 variants each, drawn from data (names, places, seasons). For example: "In the Winter of Turn 7, the Vorghith host broke the walls of Quiet Hollow."
- **Chronicle:** a per-game list stored in `D.chron`, shown on the Table and exportable as markdown.

**Trade-offs:** templates need tone guidance from you (register, tense). If they're kept data-side, you can edit them without code.

**Needs your call:** confirm the event list and the voice.

---

## 8. UX overhaul

**Now:** four views — Empire (review), Table (play), Realm (dashboard; also the Diplomacy module), and Reference.

**Proposal (your direction, made concrete):**

| View | Holds |
|---|---|
| **Realm** (renamed Table) | sticky phase bar · map (centre) · your action panel (contextual to phase) · seats/Host · Summary/Chronicle drawer |
| **Empire** | scene · holdings/infra/armies bars · settlement cards (with plates) · flags |
| **Reference** | as is |

- Everything in today's Realm view moves elsewhere:
  - player table → seats hover and an "all players" drawer
  - treaties → seat menu
- **Contextual action panel:** shows only what the current phase allows for you, such as the pre-vote, Build/Improve/Repair, Muster, Extort targets, and DP spend. This is where the "play as all players" testing mode fits: a seat switcher inside the panel.
- **Map-first interactions:** click a settlement for its plate and actions; click an army to move, muster, or siege.

**Order:** start with the action panel (largest win, no rules impact), then move Realm into it, then remove the Realm tab.

**Needs your call:** the layout table above, and whether phones get the map or the panel first.

---

## 9. Map generation under Scope and Reach

**Now:**
- Terrain Raw Materials:

  | Terrain | Raw Materials |
  |---|---|
  | Grassland | Arable, Apiary |
  | Forest | Forestry, Apiary |
  | Wetlands | Peat Bog, Forestry |
  | Tundra | Quarry, Salt Works |
  | Mountains | Mine, Quarry |
  | Water | Fishmongery |

- Common Land is buildable anywhere.
- Under the claim rule, a Settlement holds at most one Raw Material per distinct terrain type in its Reach.
- The generator still has a "Barrens" type (Quarry, Salt Works) that the data doesn't list. This was flagged earlier.

**Reachable Holdings by terrain mix** (via `builds_into` from the available raws plus Common Land/Inn/Courtyard/Manor House). This is an upper bound: it ignores AND-requirements.

| Raws from | Holdings reachable (of 119) |
|---|---|
| none (Common Land only) | 40 |
| Water | 45 |
| Tundra | 58 |
| Grassland / Mountains / Forest | 66 |
| Wetlands | 73 |
| Forest + Grassland ("Dreadwood") | 80 |
| best pair (Grassland + Wetlands) | 94 |
| best triple (Grassland + Wetlands + Mountains) | 113 |
| all | 119 |

**Holdings lost if one raw is missing:**

| Raw | Holdings lost |
|---|---|
| Peat Bog | 14 |
| Arable | 14 |
| Quarry | 13 |
| Apiary | 7 |
| Forestry | 7 |
| Mine | 6 |
| Fishmongery | 5 |
| Salt Works | 1 |

**Options:**
- **A — Start quality floor:** score each start by the distinct terrain types within Town Reach. Require ≥3, including one of Wetlands, Grassland, or Tundra (the high-yield raws).
- **B — Thematic speckle:** seed small off-biome patches (1–3 hexes) inside large uniform regions, for example a bog in Dreadwood or a scree slope in the grassland. This raises the distinct-terrain count without changing a region's identity.
- **C — New small terrains:** for example Hills, or Barrens made official.
  - This means new TERRAIN rows with Raw Material lists.
  - It's a data and rules change that needs your design.
- **D — Rebalance raw lists:** Salt Works unlocks 1 Holding, so Tundra is weak. Consider whether its list or the Salt Works chain should change.

**Needs your call:**
- A and B are generator-only; I can build them.
- C and D are design changes.
- Confirm that Barrens should be removed from the generator, or added to TERRAIN.

---

## 10. Rules syntax pass

**Counts across data + `RULES_push_simple.md`:**

| Pattern | Count |
|---|---|
| `Stat +N` ("Faith +1") | 224 |
| `+N Stat` ("+1 Faith") | 25 |
| hyphen minus `-N` | 151 |
| unicode minus `−N` | 27 |
| "Pursuit(s)" (raw text, display-aliased) | 83 |
| "Holding(s)" | 60 |
| "per turn" / "each Empire Phase" / "per Empire Phase" / "every turn" | 21 / 4 / 6 / 1 |
| "Range X" / "within range" / "in/within Reach" | 4 / 6 / 11 |
| "Once per turn" / "once per Envoy Phase" | 7 / 1 |

**Proposed canon** (regex-friendly and readable):
1. **Stat changes:** `Stat +N` / `Stat −N`, with the stat first and a signed number. Use `Stat +N per X` for scaled values.
2. **Minus:** use the ASCII `-` in data, and let the renderer print `−`. One form makes regexes simpler.
3. **Timing words:**

   | Use | When |
   |---|---|
   | `each Empire Phase` | recurring, once per turn |
   | `once per turn` | limited use |
   | `once per <Phase>` | phase-limited |

   Drop "every turn" and "per Empire Phase".
4. **Distance:** `Range N` for distance, `within your Reach` for Reach, and `within Range N of <piece>` for anchors.
5. **Actions:** `Perform <Action>` and `Perform an Endorsed <Action>`. Optional uses start with "May".
6. **Clauses:** `;` joins effects of one source; `.` ends a sentence. The board splits on both.
7. **Naming:** keep canonical keys ("Pursuit") in the data; prose uses the display layer only. The 83 raw "Pursuit" hits need checking: they're either display-aliased or should be "Holding".

**Process:**
1. A script lists every non-canonical hit with file and line, and proposes a rewrite.
2. You approve it in batches.
3. Apply the batch.
4. Re-run `--check-rules` and the markers check, and diff the board's parsed effects before and after so no regex silently loses a match.

**Needs your call:** approve the canon above, or edit it, before the sweep.
