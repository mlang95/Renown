# State of play: Nov 8 2026

Snapshot of today's combat-lab work. Nothing is committed yet.

**Edge** = a build's win rate minus the average win rate of builds at the same budget. All runs below are holding-first, TI 19–20, 1,600 builds, optimal play, 25 runs.

---

## 1. In the data now (`renown_data_d10.py`)

### Prowess / arms tree

| Line | Chain | Notes |
|---|---|---|
| Archery | Forestry → Fletchery → **Training Grounds** → **Archery Butts** → **Skirmish Field** → **Ballistarium** (M) | Ballistarium: "Deadly +1 (Ranged Weapons); Unlocks Pilum regardless of Tier Unlock". Immune One-Shot dropped. |
| Tournament | Courtyard → Conditioning Field → Coliseum → Grand Tournament → List Yard → Royal Pavilion (M) | Coliseum gains Immune Strained. Royal Pavilion: "Deadly +1; Cleave +1; gain Steady". |
| Siege | Forestry → Siege Camp → Siege Works → Battery Park → **Abatis Field** (restored) → Artillery Park (M) | 6 steps |
| Weapons | Furnace → Blacksmith → **Finery → Forge** (swapped) → Master Workshop → ABF (M) | Jewelry Foundry now hangs off Forge |
| **Armour** | Forestry → Joinery → Tannery → Armory → Gilded Foundry → Court Armoury (M) | Armour only: Cast / Wrought / Forged / Crafted. Animal Husbandry → Tannery is a 5-step, no-Shield route. |
| **Shields** (new) | Forestry → Joinery → **Shieldwright** → **Buckler School** → **Pavisiers' Yard** → **College of Arms** (M) | See below |
| Cavalry | … → Farriery → Marshal Tiltyard (M) | Tiltyard: "Unlocks Lances regardless of Tier Unlock; Armies must be equipped with Lance". **Initiative +1 removed.** |

Forestry absorbed Carpentry (deprecated). Fighting School is deprecated. Display names: Forestry → "Carpentry", Coliseum → "Drill Yard".

### Shield line

| Holding | Text |
|---|---|
| Joinery | Supply −500; Unlocks Buckler Shield |
| Shieldwright | Shield Initiative penalty reduced by 1; Unlocks Targe Shield |
| Buckler School | Unlocks Kite Shield; Armies Equipped with a 2H Weapon may Equip a Buckler Shield |
| Pavisiers' Yard | Unlocks Tower Shield; Unlocks **Leather**; gain **Shield Wall** |
| College of Arms (M) | Unlocks Heater Shield; Unlocks **Chainmail** |

Full Plate now comes only from the Gilded Foundry. Buckler School has no armour.

**Shield Wall** (`SHIELD_WALL`): in Defensive Formation with a Shield Equipped, incoming AP −1. It stacks with Articulated.

### Gear

| Item | Stats |
|---|---|
| Buckler | Save +1, Init 0 |
| Targe | Save +1, Init −1, Unwieldy, Shielded |
| Kite | Save +1, **Init 0**, Shielded (Steady removed) |
| Tower | Save +1, Init −2, Unwieldy, Crude, **Shielded 3** (Steady removed) |
| Heater | **Save +2**, Init −1, **Shielded 2, Immune Destroy Shield** |
| Chainmail / Full Plate | 6+ / 4+ |
| Gothic Plate | **3+, Articulated** (= the old Fluted: incoming AP −1, plus Immune Strained) |
| Lance | **AP −4**, Init +1, Steady, Unwieldy, Unstoppable, Awkward, **Deadly** |
| Morningstar | AP −3, **Cleave only** (Unwieldy and Destroy Shield removed) |
| Poleaxe / War Hammer | Destroy Shield removed; both keep Hook 2 |
| **Destroy Shield** | now only on thrown weapons: Throwing Axe (Javelin) and Throwing Spear (Pilum) |
| Cavalry Spear | **AP −2**, … Deadly |
| Halberd | AP −3, Init +1, 2H, Unstoppable, Hook 1 |
| Swords (data) | Short 0 · Arming −1 · Bastard −2 · Estoc −2 (Steady, Deadly, Unstoppable) |
| Knight Templar | **Endurance 2** |

### Lab tooling (`Combatv4/`, `run_tournament*`)

- **Filler filter.** Builds owning a Holding they don't use are dropped (`idle_holdings`).
- **Shield tier rule retired.** One-handed weapons can carry any unlocked Shield. One-handed weapons still need a Shield or Florentine.
- **Pool reuse.** `POOL_CSV` (blank / `last` / a path) and `ALLOW_STALE` in the `.bat`. A reused pool is checked against the data.
- **Pool cache.** `POOL_CACHE=1`: an unchanged tree and gear rules reuse the pool from `lab_out\_pool_cache`.
- **Engines and board** support Shield Init, Buckler 2H, Shield Wall, Articulated, named armour and Shield unlocks, and stacking AP reduction.
- **Pool Shield choice.** The pool builder now offers every unlocked Shield that no other unlocked Shield strictly beats. Before, it took only the top of a fixed ladder, which hid the Kite.
- **`Combatv4/swap_test.py`** (new). Answers "what is one change worth, all else equal?" It fights a build and its one-change twin against the same fixed panel, either instantly (expected casualties) or with `--sim` (win rate). Examples:
  - `--swap shield "Kite Shield" "Tower Shield"`
  - `--add-tag "Shake +1" --where pursuit=Armory`
  - `--variant SHIELDS "Kite Shield" '{"tags":["Shielded 2"]}'`

  Use it instead of tournament edge for item and keyword questions.

---

## 2. Tested in memory only (not in the data)

| Change | Status |
|---|---|
| Sword AP buff: Short −1, Arming −2, Bastard −2 + Deadly, Estoc −3 + Deadly | **Used as the baseline**, but not written into the data |
| Armory "gain Shake +1" | Promising (see results). Needs a parser line before it can go in the data. |

---

## 3. Same-pool test results (one change each)

| Change | Effect on its target | Verdict |
|---|---|---|
| Sword AP buff | each sword about +0.02 | keep (baseline) |
| Arming Sword + Deadly | +0.034 | best sword lever |
| Steady on Short/Arming Sword | about 0 | no |
| Steady on Bastard Sword | +0.001 | no (Steady ≈ 0 under optimal play) |
| Gothic 4+ (with Articulated) | Gothic −0.072, Court Armoury −0.072 | overcorrects |
| Gothic 3+, Articulated = Immune Strained only | Gothic −0.067 | AP reduction ≈ 1 point of Save |
| Full Plate Strained | Full Plate −0.022, College −0.021, Tiltyard −0.010 | mild |
| Lance without Deadly | Lance −0.046 | |
| Tiltyard without Initiative +1 | Tiltyard −0.034 | **adopted** |
| Armory Shake +1 | Armory builds +0.054, even across Retinues; armour line turns positive | promising |
| Shielded +1 step (Targe/Kite/Heater 2, Tower 3), no College immunity | Tower +0.029, Targe/Kite +0.015, Heater −0.010 | partly adopted (Heater 2, Tower 3) |
| Tuned set: Lance AP −4, Tiltyard without Init +1, Kite Init 0, Shield values as above (fresh pool) | Tiltyard +0.304 → +0.049, Lance +0.254 → +0.081 | **Lance in order** |
| Destroy Shield on thrown weapons only | Shields destroyed 11.9% → 7.3% of battles; edges within ±0.002 | adopted for design reasons |
| Swap test: Kite → Shielded 2 (30 builds × 150 opponents) | win rate +0.027 ± 0.006 | one Shielded step ≈ +0.03 against a real field |

**How to read edge.** Changes that touch most of the field (for example every Shield) cancel out in edge, because those builds mostly fight each other. Edge also credits a build's partners to each Holding, and is distorted by pool artifacts. Today found three: filler builds, the old shield-tier rule, and the fixed Shield ladder. Use the swap test for item and keyword questions.

**Monuments, separated with a regression** (each Monument's own effect on win rate, plus or minus its error):

| Monument | Own effect |
|---|---|
| Marshal Tiltyard | +0.17 ± 0.04 |
| Court Armoury | +0.16 |
| College of Arms | +0.14 |
| Ministry | +0.08 |
| Ballistarium | +0.08 |
| Artillery Park | +0.06 |
| ABF | +0.03 |
| Royal Pavilion | −0.02 |
| Outrider | −0.12 |

The Court Armoury is held back by its chain cost, not by what it gives.

Strikes cause about 72% of casualties, a little above the 65–70% target.

---

## 4. Open decisions

1. **Done:** Pavisiers' Yard → Leather, College of Arms → Chainmail. Not yet tested in a tournament.
2. **Lance and the Heater.** Ban the Heater for the Lance? Probably not needed now.
2b. **Parked idea:** Shields drop Save for Shielded and Initiative only, possibly with a Deflect rule (incoming AP −1). Check the existing `DEFLECT` constant first. The intended split: ABF = weapons, armour line = Save, Shield line = how hard you are to hit.
3. **Sword buffs.** Write them into the data? Also: Arming Sword Deadly?
4. **Armory Shake +1.** Write it into the data? This needs a parser line and a fresh pool.
5. **Rules prose.** Add the Buckler School exception to the line "while a 2H weapon is Equipped your Shield gives nothing".
6. **Missing pieces.** Sprites for Shieldwright, Buckler School, Pavisiers' Yard, College of Arms, Training Grounds and Ballistarium; the College of Arms in a culture's Monument list; the board AI giving a Buckler to 2H armies.
7. **Checkpoint.** A commit on its own branch (not `main`). Note that `build_all_CE.bat` force-pushes HEAD.

**Not yet run:** a tournament on the latest data (Morningstar, thrown-only Destroy Shield, Shield-line armour, new Shield choice in pools). It needs a fresh pool, about 17 minutes plus the battles.

**Backups of the data before each round:** see the scratchpad folder from this session (`renown_data_d10_pre_*.py`).
