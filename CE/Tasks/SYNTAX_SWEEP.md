# Rules syntax sweep — canon applied

Scope: every string literal in `renown_data_d10.py` (tokenizer pass, code untouched) + prose in `RULES_push_simple.md` ({{markers}} untouched).

## Canon

| # | Rule | Form |
|---|---|---|
| 1 | Stat changes | `Stat +N` / `Stat -N` (stat first, signed). `Influence ±N` = Influence tokens; the Envoy-score modifier is written `Authority ±N` |
| 2 | Minus | ASCII `-` in data; `display_text` prints U+2212 for signed numbers / `-X` (docx, wiki, PDFs) |
| 3 | Timing | `each Empire Phase` (recurring) · `once per turn` (limited) · `once per <Phase>` (phase-limited). `Once/turn`, `/turn`, `per Empire Phase`, `every turn` removed |
| 4 | Distance | `Range N`; `within Range N of <piece>`; `within your Reach`; `within your Province` |
| 5 | Actions | `Perform an Endorsed <Action>` |
| 6 | Clauses | `;` joins effects of one source (between stat atoms) |
| 7 | Naming | keys stay canonical (`Pursuit`); prose goes through the display layer |

## Parser updates (so nothing silently stops matching)

| Where | Change |
|---|---|
| `gen_settlement_board.py` · `AUTH_RE` | Envoy score = `Authority ±N` (was postfix `Influence ±N`) |
| `envoy_fx` | score patterns accept `Authority` (legacy `Influence` tolerated); pool patterns accept `Influence +N` and `each Empire Phase` |
| `classify` | `once per` counts as conditional; `Stat +N each Empire Phase` stays flat |
| JS · `dispScore` | renames `Authority ±N` (not `Influence ±N`) to the score term |
| JS regexes | Province (4), range-0 upkeep, `Raw Material … within your Reach`, `Influence +N each Empire Phase` (Town Hall-style rows, Royal Marriage), first-Doubt `each turn`, `per/each Empire Phase` (2), `Initiative +1`, Bandit `Authority +N on Cunning Envoys` |
| `renown_data` · `display_score` / `display_text` | score rewrite keyed to `Authority`; signed-number minus prettified |
| GLOSSARY | key `Influence X` → `Authority X` (category list updated) |

## Verification

| Check | Result |
|---|---|
| Parsed effects (Python: atoms, envoy fx) over all 120 Holdings, 16 Infra, 4 Wonders, 41 Factions — before vs after | identical except Beacon Towers + High Chancery: their `Once per turn` clause is now marked conditional (was misread as unconditional) |
| 267 board JS regex literals run on every changed data string, old vs new text | no lost matches on effect text (only comma-list splitters and glossary-only leading-number tests, which don't read effect clauses) |
| `--check-rules` | 0 mismatches |
| `wiki_markers.py` | no unresolved markers |

## Left as-is (needs a call)

- `At the start of each turn, …` (Tithe, Mimic), `Each turn, you may …` allowances, Jester's `each turn` window, `Domain Points — earned 1 per turn`.
- `COSTS['Tax per tier']`: "500 gold per settlement tier per turn (collected in Winter)" — doesn't match SETTLEMENTS tax_income.
- `Grand Tournament`: `3x/turn: exchange …` (see Once per <Phase> table in TASK2_NOTES.md).

## Change log (221 rewrites)

### stat first: ±N Stat → Stat ±N (27)

- data:122: `Gain +1 Initiative ` → `Gain Initiative `; `Gain +1 Initiative in the firs` → `Gain Initiative +1 in the firs`
- data:149: `-1 Initiative i` → `Initiative -`; `-1 Initiative in the firs` → `Initiative -1 in the firs`
- data:150: `-1 Initiative e` → `Initiative -`; `-1 Initiative every Skirm` → `Initiative -1 every Skirm`
- data:153: ` the player gains +1 Initiative i` → ` the player gains Initiative +`; `ains +1 Initiative in the firs` → `r gains Initiative +1 in the firs`
- data:646: `+1 Influence pe` → `Influence +1`; `+1 Influence per 3 Pursu` → `Influence +1 per 3 Pursu`
- data:1144: `+1 Influence/tu` → `Influence +1`; `+1 Influence/turn` → `Influence +1/turn`
- data:1291: `+1 Influence pe` → `Influence +1`; `+1 Influence per Domain ` → `Influence +1 per Domain `
- data:1492: `Gain +2 Influence w` → `Gain Influence +`; `Gain +2 Influence while At Wa` → `Gain Influence +2 while At Wa`
- data:1588: `Faith +1, gain +1 Influence pe` → `Faith +1, gain Influence +1`; ` gain +1 Influence per other p` → `+1, gain Influence +1 per other p`
- data:1644: `+1 Influence pe` → `Influence +1`; `+1 Influence per Establi` → `Influence +1 per Establi`
- data:2087: `+1 Influence/tu` → `Influence +1`; `+1 Influence/turn; Autho` → `Influence +1/turn; Autho`
- data:2110: `ncil Envoys; gain +1 Influence pe` → `ncil Envoys; gain Influence +1`; `gain +1 Influence per turn` → `s; gain Influence +1 per turn`
- data:2177: `upport or Oppose; +1 Influence pe` → `upport or Oppose; Influence +1`; `pose; +1 Influence per Domain ` → ` Oppose; Influence +1 per Domain `
- data:2377: `Gain +2 Influence w` → `Gain Influence +`; `Gain +2 Influence while At Wa` → `Gain Influence +2 while At Wa`
- data:2448: `Faith +1, gain +1 Influence pe` → `Faith +1, gain Influence +1`; ` gain +1 Influence per other p` → `+1, gain Influence +1 per other p`
- data:2498: `+1 Influence pe` → `Influence +1`; `+1 Influence per Establi` → `Influence +1 per Establi`
- data:2720: `ains Faith +1 and +1 Influence pe` → `ains Faith +1 and Influence +1`; ` and +1 Influence per turn.` → ` +1 and Influence +1 per turn.`
- data:2780: `: Each turn, gain +1 Influence fo` → `: Each turn, gain Influence +1`; ` gain +1 Influence for every 3` → `rn, gain Influence +1 for every 3`
- data:3061: ` your Armies gain +1 Initiative, ` → ` your Armies gain Initiative +`; `gain +1 Initiative, Steady, an` → `es gain Initiative +1, Steady, an`
- data:3114: `+1 Influence pe` → `Influence +1`; `+1 Influence per turn` → `Influence +1 per turn`
- data:3158: `Gain +1000 Tax Income ` → `Gain Tax Income `; `n +1000 Tax Income per Settlem` → `Gain Tax Income +1000 per Settlem`
- data:3171: `, Build Timer -1, +1 Influence` → `, Build Timer -1, Influence +1`; `r -1, +1 Influence` → `imer -1, Influence +1`
- data:3325: `estine Councilor: +1 Influence pe` → `estine Councilor: Influence +1`; `ilor: +1 Influence per turn. O` → `uncilor: Influence +1 per turn. O`
- data:3326: `Grand Vizier: +1 Influence pe` → `Grand Vizier: Influence +1`; `zier: +1 Influence per turn. P` → ` Vizier: Influence +1 per turn. P`
- data:3327: `ster Conspirator: +1 Influence pe` → `ster Conspirator: Influence +1`; `ator: +1 Influence per turn. O` → `pirator: Influence +1 per turn. O`
- rules:522: ` Blocked Army has −1 Initiative i` → ` Blocked Army has Initiative −`; ` has −1 Initiative in the firs` → `rmy has Initiative −1 in the firs`
- rules:546: ` the player gains +1 Initiative i` → ` the player gains Initiative +`; `ains +1 Initiative in the firs` → `r gains Initiative +1 in the firs`

### timing: You gain it each turn → each Empire Phase (1)

- data:186: ` You gain it each turn from your` → ` You gain it each Empire Phase fro`; `u gain it each turn from your E` → `gain it each Empire Phase from your E`

### score: Influence ±N → Authority ±N (35)

- data:187: `Influence X` → `Authority X`; `Influence X` → `Authority X`
- data:193: `port, Oppose, and Influence X. The` → `port, Oppose, and Authority X. `; ` Oppose, and Influence X. The tota` → `rt, Oppose, and Authority X. The tota`
- data:853: `Influence −1 to ` → `Authority −1 `; `Influence −1 to Cunni` → `Authority −1 to Cunni`
- data:905: `+500; Influence +1 to ` → `+500; Authority +1 `; `+500; Influence +1 to Cunni` → `+500; Authority +1 to Cunni`
- data:1020: `Natural; +500; Influence +1 to ` → `Natural; +500; Authority +1 `; `tural; +500; Influence +1 to Cunni` → `Natural; +500; Authority +1 to Cunni`
- data:1065: `Natural; Influence -1 to ` → `Natural; Authority -1 `; `Natural; Influence -1 to Inter` → `Natural; Authority -1 to Inter`
- data:1115: `Once/turn: Influence +1 ano` → `Once/turn: Authority +1 `; `Once/turn: Influence +1 another ` → `Once/turn: Authority +1 another `
- data:1134: `Influence −1 to ` → `Authority −1 `; `Influence −1 to Piety` → `Authority −1 to Piety`
- data:1145: `Influence +1 to ` → `Authority +1 `; `Influence +1 to envoy` → `Authority +1 to envoy`
- data:1153: `Influence -1 to ` → `Authority -1 `; `Influence -1 to Foste` → `Authority -1 to Foste`
- data:1182: `Influence +1 to ` → `Authority +1 `; `Influence +1 to Diplo` → `Authority +1 to Diplo`
- data:1200: `Influence +1 to ` → `Authority +1 `; `Influence +1 to Counc` → `Authority +1 to Counc`
- data:1201: `Influence +1 to ` → `Authority +1 `; `Influence +1 to non-C` → `Authority +1 to non-C`
- data:1318: `Once/turn: Influence −1 on ` → `Once/turn: Authority −1 `; `Once/turn: Influence −1 on Targe` → `Once/turn: Authority −1 on Targe`
- data:1653: ` Camps & you have Influence +1 on ` → ` Camps & you have Authority +1 `; `s & you have Influence +1 on Cunni` → `amps & you have Authority +1 on Cunni`
- data:1845: `Craft +1; Influence −1 to ` → `Craft +1; Authority −1 `; `Craft +1; Influence −1 to Cunni` → `Craft +1; Authority −1 to Cunni`
- data:1880: `+2000; Influence +1 to ` → `+2000; Authority +1 `; `+2000; Influence +1 to Cunni` → `+2000; Authority +1 to Cunni`
- data:1966: `Natural; +1000; Influence +1 to ` → `Natural; +1000; Authority +1 `; `ural; +1000; Influence +1 to Cunni` → `Natural; +1000; Authority +1 to Cunni`
- data:2001: `Natural; Influence -2 to ` → `Natural; Authority -2 `; `Natural; Influence -2 to Inter` → `Natural; Authority -2 to Inter`
- data:2043: `Once/turn: Influence +2 ano` → `Once/turn: Authority +2 `; `Once/turn: Influence +2 another ` → `Once/turn: Authority +2 another `; `er's Piety Envoy; Influence −1 to ` → `er's Piety Envoy; Authority −1 `; `Piety Envoy; Influence −1 to Piety` → `'s Piety Envoy; Authority −1 to Piety`
- data:2066: `Influence -2 to ` → `Authority -2 `; `Influence -2 to Foste` → `Authority -2 to Foste`
- data:2087: `1 Influence/turn; Influence +1 to ` → `1 Influence/turn; Authority +1 `; `luence/turn; Influence +1 to envoy` → `Influence/turn; Authority +1 to envoy`
- data:2110: `Influence +1 to ` → `Authority +1 `; `Influence +1 to Counc` → `Authority +1 to Counc`
- data:2198: `rn before voting: Influence −1 on ` → `rn before voting: Authority −1 `; `fore voting: Influence −1 on Targe` → ` before voting: Authority −1 on Targe`
- data:2505: ` Camps & you have Influence +1 on ` → ` Camps & you have Authority +1 `; `s & you have Influence +1 on Cunni` → `amps & you have Authority +1 on Cunni`
- data:2770: `sonal Envoys have Influence +1. Yo` → `sonal Envoys have Authority +1.`; ` Envoys have Influence +1. You can` → `nal Envoys have Authority +1. You can`
- data:2910: `lied with you has Influence +1 on ` → `lied with you has Authority +1 `; `with you has Influence +1 on their` → `ed with you has Authority +1 on their`
- data:3021: `nning Envoys have Influence +2 whe` → `nning Envoys have Authority +2 `; ` Envoys have Influence +2 when tar` → `ing Envoys have Authority +2 when tar`
- data:3102: `Influence -2 to ` → `Authority -2 `; `Influence -2 to Raze ` → `Authority -2 to Raze `; `your settlements. Influence -1 to ` → `your settlements. Authority -1 `; `settlements. Influence -1 to Bandi` → `ur settlements. Authority -1 to Bandi`
- data:3133: `Influence -2 to ` → `Authority -2 `; `Influence -2 to Desta` → `Authority -2 to Desta`; `your settlements. Influence -1 to ` → `your settlements. Authority -1 `; `settlements. Influence -1 to Bandi` → `ur settlements. Authority -1 to Bandi`
- data:3152: `Influence -1 to ` → `Authority -1 `; `Influence -1 to Bandi` → `Authority -1 to Bandi`
- data:4583: `Influence X` → `Authority X`; `Influence X` → `Authority X`
- rules:167: ` though automatic Influence ±X mod` → ` though automatic Authority ±X `; `gh automatic Influence ±X modifier` → `hough automatic Authority ±X modifier`
- rules:245: `lus any automatic Influence ±X mod` → `lus any automatic Authority ±X `; `ny automatic Influence ±X modifier` → `s any automatic Authority ±X modifier`
- rules:319: ` your Envoys gain Influence +1. Th` → ` your Envoys gain Authority +1.`; ` Envoys gain Influence +1. This co` → `our Envoys gain Authority +1. This co`

### timing: Retinues arrive each turn → each Empire Phase (1)

- data:206: `inues arrive each turn over a Mu` → `inues arrive each Empire Phase ove`; `es arrive each turn over a Must` → ` arrive each Empire Phase over a Must`

### clause: stat atoms joined with ;  (41)

- data:663: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:671: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:679: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:687: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:695: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:703: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:711: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:719: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:727: `+1000, Natural, Do` → `+1000; Natural, Do`
- data:735: `+500, Natural` → `+500; Natural`
- data:756: `+500, Natural` → `+500; Natural`
- data:768: `+500, Natural` → `+500; Natural`
- data:776: `+800, Natural` → `+800; Natural`
- data:957: `Natural; Doubt +1, +500` → `Natural; Doubt +1; +500`
- data:966: `Doubt +1, +600` → `Doubt +1; +600`
- data:967: `Build Timer -2, +600` → `Build Timer -2; +600`
- data:1075: `Speed +1, Natural` → `Speed +1; Natural`
- data:1191: `Upkeep -500, Natural` → `Upkeep -500; Natural`
- data:1282: `+500, Faith +1` → `+500; Faith +1`
- data:1447: `+200, Natural` → `+200; Natural`
- data:1697: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:1704: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:1711: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:1718: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:1725: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:1732: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:1739: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:1746: `+500, Natural; Cr` → `+500; Natural; Cr`
- data:1754: `+1000, Natural, Do` → `+1000; Natural, Do`
- data:1761: `+1000, Natural; Cr` → `+1000; Natural; Cr`
- data:1775: `+500, Natural; Sp` → `+500; Natural; Sp`
- data:1782: `+500, Natural; +1` → `+500; Natural; +1`
- data:1789: `+1500, Natural; +5` → `+1500; Natural; +5`
- data:1796: `ild Timer -1; +500, Craft +1` → `ild Timer -1; +500; Craft +1`
- data:1873: `Craft +1, +500; Unloc` → `Craft +1; +500; Unloc`
- data:1915: `Natural; Doubt +1, +1000` → `Natural; Doubt +1; +1000`
- data:1922: `Natural; Doubt +1, +2000; Buil` → `Natural; Doubt +1; +2000; Buil`
- data:2008: `Speed +1, Natural; Un` → `Speed +1; Natural; Un`
- data:2169: `+1000, Faith +1` → `+1000; Faith +1`
- data:3171: `Reach +1, Upkeep -500` → `Reach +1; Upkeep -500`; `ch +1, Upkeep -500, Build Timer` → `ch +1; Upkeep -500; Build Timer`; `00, Build Timer -1, Influence +` → `00; Build Timer -1; Influence +`
- data:3186: `vote. Speed +2, Siege Timer` → `vote. Speed +2; Siege Timer`

### minus: − → - (26)

- data:784: `Build Timer −1` → `Build Timer -1`
- data:804: `Build Timer −1` → `Build Timer -1`
- data:853: `Authority −1 to Cunning` → `Authority -1 to Cunning`
- data:967: `Build Timer −2, +600` → `Build Timer -2, +600`
- data:1134: `Authority −1 to Piety e` → `Authority -1 to Piety e`
- data:1318: `e/turn: Authority −1 on Target ` → `e/turn: Authority -1 on Target `
- data:1337: `Build Timer −2` → `Build Timer -2`
- data:1466: `Siege Timer −1` → `Siege Timer -1`
- data:1467: `Siege Timer −1; Sieges In` → `Siege Timer -1; Sieges In`
- data:1474: `Siege Timer −1` → `Siege Timer -1`
- data:1555: `orth. Siege Timer −1.` → `orth. Siege Timer -1.`
- data:1796: `Build Timer −1; +500, Cra` → `Build Timer -1; +500, Cra`
- data:1810: `ture; Build Timer −1` → `ture; Build Timer -1`
- data:1845: `aft +1; Authority −1 to Cunning` → `aft +1; Authority -1 to Cunning`
- data:1922: `2000; Build Timer −1` → `2000; Build Timer -1`
- data:2043: ` Envoy; Authority −1 to Piety a` → ` Envoy; Authority -1 to Piety a`
- data:2184: `ture; Build Timer −1` → `ture; Build Timer -1`
- data:2198: `voting: Authority −1 on Target ` → `voting: Authority -1 on Target `
- data:2212: `ture; Build Timer −1` → `ture; Build Timer -1`
- data:2219: `ture; Build Timer −2` → `ture; Build Timer -2`
- data:2347: `Siege Timer −2; Sieges In` → `Siege Timer -2; Sieges In`
- data:2354: `Siege Timer −1; Armies ga` → `Siege Timer -1; Armies ga`
- data:2426: `orth. Siege Timer −1.` → `orth. Siege Timer -1.`
- data:2880: `Armies have Speed −2 in your Pr` → `Armies have Speed -2 in your Pr`
- data:2940: ` Recover 8, Speed −1, and Immun` → ` Recover 8, Speed -1, and Immun`
- rules:522: `my has Initiative −1 in the fir` → `my has Initiative -1 in the fir`

### stat spacing: Stat±N → Stat ±N (7)

- data:785: `+300; Craft+1` → `+300; Craft +1`
- data:795: `Craft+1` → `Craft +1`
- data:805: `Craft+1` → `Craft +1`
- data:814: `Upkeep -200; Craft+1` → `Upkeep -200; Craft +1`
- data:1796: `er −1; +500, Craft+1` → `er −1; +500, Craft +1`
- data:1803: `+500; Craft+2` → `+500; Craft +2`
- data:1817: `Upkeep -500; Craft+1` → `Upkeep -500; Craft +1`

### timing: Once/turn → Once per turn (16)

- data:1115: `Once/turn: Author` → `Once per turn: Author`
- data:1318: `Once/turn: Author` → `Once per turn: Author`
- data:1319: `Once/turn: succes` → `Once per turn: succes`
- data:1327: `Natural; Once/turn when an` → `Natural; Once per turn when an`
- data:1373: `Once/turn: attemp` → `Once per turn: attemp`
- data:1589: `Once/turn: Before` → `Once per turn: Before`
- data:1673: `Once/turn when a ` → `Once per turn when a `
- data:1674: `Once/turn: select` → `Once per turn: select`
- data:2043: `Once/turn: Author` → `Once per turn: Author`
- data:2198: `Once/turn before ` → `Once per turn before `; `Target Envoy; Once/turn: succes` → `Target Envoy; Once per turn: succes`
- data:2205: `hin Province; Once/turn: when a` → `hin Province; Once per turn: when a`
- data:2254: `voy of yours; Once/turn: attemp` → `voy of yours; Once per turn: attemp`
- data:2340: ` in Province. Once/turn, you ma` → ` in Province. Once per turn, you ma`
- data:2448: `yer per Turn; Once/turn: Before` → `yer per Turn; Once per turn: Before`
- data:2519: `Once/turn: select` → `Once per turn: select`; `ains Blocked. Once/turn: select` → `ains Blocked. Once per turn: select`
- data:2526: `ter the Host. Once/turn when a ` → `ter the Host. Once per turn when a `

### timing: First Doubt per turn → each turn (2)

- data:1126: `First Doubt per turn redu` → `First Doubt each turn re`; `First Doubt per turn reduce` → `First Doubt each turn reduce`
- data:2051: `+500; First Doubt per turn redu` → `+500; First Doubt each turn re`; `00; First Doubt per turn reduce` → `500; First Doubt each turn reduce`

### timing: Stat ±N/turn → each Empire Phase (2)

- data:1144: `Influence +1/turn` → `Influence +1 each Empire Phase`; `Influence +1/turn` → `ence +1 each Empire Phase`
- data:2087: `Influence +1/turn; Authorit` → `Influence +1 each Empire Phase; Au`; `Influence +1/turn; Authority ` → `ence +1 each Empire Phase; Authority `

### distance: within/in Province → your Province (15)

- data:1327: `Move action within Province: P` → `Move action within your Province: P`
- data:1328: `ove action within Province` → `ove action within your Province`
- data:1402: `ct an Army within Province and` → `ct an Army within your Province and`
- data:1403: `ove action within Province, yo` → `ove action within your Province, yo`
- data:2205: `ove action within Province; On` → `ove action within your Province; On`; `Move action within Province: P` → `Move action within your Province: P`
- data:2240: `Bandit Camp within Province Ex` → `Bandit Camp within your Province Ex`
- data:2290: `ect an Army within Province an` → `ect an Army within your Province an`; `ove action within Province, yo` → `ove action within your Province, yo`
- data:2340: `y Upkeep while in Province. Up` → `y Upkeep while in your Province. Up`; `-2000 while not in Province. O` → `-2000 while not in your Province. O`
- data:3084: `ove action within Province, ga` → `ove action within your Province, ga`
- data:3108: `Move action within Province, g` → `Move action within your Province, g`
- data:3139: `l movement within Province; St` → `l movement within your Province; St`
- data:3322: `at army is within Province. No` → `at army is within your Province. No`
- data:3463: `ove action within Province, ga` → `ove action within your Province, ga`
- data:3464: `Move action within Province, g` → `Move action within your Province, g`
- data:3467: ` gain Speed -2 in Province.` → ` gain Speed -2 in your Province.`

### distance: range 0 of controlled settlement (3)

- data:1456: `ep -1000 while an army is range` → `ep -1000 while an Army is withi`; ` while an army is range 0 of co` → ` while an Army is within Range 0 of a `; `rmy is range 0 of controlled settlement` → `within Range 0 of a Settlement `; `e 0 of controlled settlement` → `thin Range 0 of a Settlement yo`; `trolled settlement` → ` 0 of a Settlement you Control`
- data:1457: `ep -1000 while an army is range` → `ep -1000 while an Army is withi`; ` while an army is range 0 of co` → ` while an Army is within Range 0 of a `; `rmy is range 0 of controlled settlement` → `within Range 0 of a Settlement `; `e 0 of controlled settlement` → `thin Range 0 of a Settlement yo`; `trolled settlement` → ` 0 of a Settlement you Control`
- data:2333: `ep -2000 while an army is range` → `ep -2000 while an Army is withi`; ` while an army is range 0 of co` → ` while an Army is within Range 0 of a `; `rmy is range 0 of controlled settlement` → `within Range 0 of a Settlement `; `e 0 of controlled settlement` → `thin Range 0 of a Settlement yo`; `trolled settlement` → ` 0 of a Settlement you Control`

### timing: Influence +N per turn → each Empire Phase (8)

- data:1588: ` per other player per Turn` → ` per other player each Empire Phase`; `per other player per Turn` → `er player each Empire Phase`; `er other player per Turn` → `player each Empire Phase`; ` other player per Turn` → `layer each Empire Phase`
- data:2110: `gain Influence +1 per turn` → `gain Influence +1 each Empire Phase`; `ain Influence +1 per turn` → `luence +1 each Empire Phase`; `in Influence +1 per turn` → `nce +1 each Empire Phase`; ` Influence +1 per turn` → `ce +1 each Empire Phase`
- data:2448: ` per other player per Turn; On` → ` per other player each Empire Phase; `; `per other player per Turn; Onc` → `er player each Empire Phase; Onc`; `er other player per Turn; Once ` → `player each Empire Phase; Once`; ` other player per Turn; Once per t` → `layer each Empire Phase; Once per t`
- data:2720: ` and Influence +1 per turn.` → ` and Influence +1 each Empire Phase.`; `and Influence +1 per turn.` → `luence +1 each Empire Phase.`; `nd Influence +1 per turn.` → `nce +1 each Empire Phase.`; ` Influence +1 per turn.` → `ce +1 each Empire Phase.`
- data:3114: `Influence +1 per turn` → `Influence +1 each Empire Phase`; `Influence +1 per turn` → `luence +1 each Empire Phase`; `Influence +1 per turn` → `nce +1 each Empire Phase`; `Influence +1 per turn` → `ce +1 each Empire Phase`
- data:3325: `lor: Influence +1 per turn. On` → `lor: Influence +1 each Empire Phase. `; `or: Influence +1 per turn. Onc` → `luence +1 each Empire Phase. Onc`; `r: Influence +1 per turn. Once ` → `nce +1 each Empire Phase. Once`; ` Influence +1 per turn. Once per E` → `ce +1 each Empire Phase. Once per E`
- data:3326: `ier: Influence +1 per turn. Pl` → `ier: Influence +1 each Empire Phase. `; `er: Influence +1 per turn. Pla` → `luence +1 each Empire Phase. Pla`; `r: Influence +1 per turn. Playe` → `nce +1 each Empire Phase. Play`; ` Influence +1 per turn. Players ma` → `ce +1 each Empire Phase. Players ma`
- data:3327: `tor: Influence +1 per turn. On` → `tor: Influence +1 each Empire Phase. `; `or: Influence +1 per turn. Onc` → `luence +1 each Empire Phase. Onc`; `r: Influence +1 per turn. Once ` → `nce +1 each Empire Phase. Once`; ` Influence +1 per turn. Once per t` → `ce +1 each Empire Phase. Once per t`

### timing: Every turn, perform Endorsed → Once per turn, perform an Endorsed (1)

- data:2476: `additional Faith. Every turn, pe` → `additional Faith. Once per turn, per`; `tional Faith. Every turn, perfo` → `al Faith. Once per turn, perfo`; `very turn, perform Endorsed Sp` → ` per turn, perform an Endorsed Sp`

### timing: Each turn, gain → Each Empire Phase, gain (2)

- data:2780: `ge is Power: Each turn, gain Inf` → `ge is Power: Each Empire Phase, ga`; `is Power: Each turn, gain Influ` → ` Power: Each Empire Phase, gain Influ`
- rules:277: `Each turn, gain Inf` → `Each Empire Phase, ga`; `Each turn, gain Influ` → `Each Empire Phase, gain Influ`

### timing: per Empire Phase → each Empire Phase (4)

- data:2850: `ou're At War with per Empire Ph` → `ou're At War with each Empire `; `'re At War with per Empire Phas` → `u're At War with each Empire Phas`
- data:2890: `er gains Doubt +1 per Empire Ph` → `er gains Doubt +1 each Empire `; ` gains Doubt +1 per Empire Phas` → `r gains Doubt +1 each Empire Phas`
- data:2970: `er gains Doubt +1 per Empire Ph` → `er gains Doubt +1 each Empire `; ` gains Doubt +1 per Empire Phas` → `r gains Doubt +1 each Empire Phas`
- data:3061: `us: Gain Doubt +1 per Empire Ph` → `us: Gain Doubt +1 each Empire `; `: Gain Doubt +1 per Empire Phas` → `s: Gain Doubt +1 each Empire Phas`

### distance: Raw Material Pursuits within Reach → within your Reach (1)

- data:3041: `l Pursuits within Reach are al` → `l Pursuits within your Reach are al`

### timing: upkeep_frequency per Turn → each Empire Phase (13)

- data:3095: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3101: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3107: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3113: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3119: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3125: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3132: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3145: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3151: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3157: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3163: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3170: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`
- data:3177: `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`; `per Turn` → `each Empire Phase`

### distance: exactly range 2 from capital (1)

- data:3227: `its only; exactly range 2 from ` → `its only; exactly Range 2 from `; `actly range 2 from capital; ma` → `actly Range 2 from your capital; ma`

### distance: range N → Range N (7)

- data:3607: `eld, and at least range 2 from ` → `eld, and at least Range 2 from `
- data:4466: `range 4+ from` → `Range 4+ from`; `ny Settlement and range 2+ from` → `ny Settlement and Range 2+ from`
- rules:382: `t be adjacent to (range 1); a T` → `t be adjacent to (Range 1); a T`
- rules:390: ` Territory within range 1 of th` → ` Territory within Range 1 of th`
- rules:420: `another, you move range 1. To b` → `another, you move Range 1. To b`; `in a Territory is range 0; adja` → `in a Territory is Range 0; adja`; `ge 0; adjacent is range 1; next` → `ge 0; adjacent is Range 1; next`; `nge 1; next to is range 2.` → `nge 1; next to is Range 2.`
- rules:635: `gion, each within range 1 of at` → `gion, each within Range 1 of at`
- rules:637: `sible, place them range 2 from ` → `sible, place them Range 2 from `

### distance: within (range 0) a Settlement (2)

- data:3608: `within (range 0) a Se` → `within Range 0 of a `; `within (range 0) a Settlemen` → `within Range 0 of a Settlemen`
- rules:514: `an Army is within (range 0) a Se` → `an Army is within Range 0 of a `; `is within (range 0) a Settlemen` → ` is within Range 0 of a Settlemen`

### distance: province → Province (4)

- data:3712: `ettlement in your province.` → `ettlement in your Province.`
- data:4460: `ettlement in your province. ` → `ettlement in your Province. `
- rules:386: ` place it in your province, at ` → ` place it in your Province, at `
- rules:390: `u Control in your province: at ` → `u Control in your Province: at `

### timing: Per turn (upkeep text) → Each Empire Phase (1)

- data:3888: `Per turn by ` → `Each Empire Phase, by ty`; `Per turn by t` → `Each Empire Phase, by type (`; `Per turn by type (fi` → `Each Empire Phase, by type (fi`

### distance: army at range 0 of the settlement (1)

- data:3948: `army at range` → `Army within R`; `army at range 0 of` → `Army within Range 0`; `army at range 0 of ` → `Army within Range 0 of `; `army at range 0 of th` → `Army within Range 0 of th`; `at range 0 of the settlement` → `in Range 0 of the Settlement`
### manual (not in the pass above)

- RULES_push_simple.md: `range {{VAL:…}}` → `Range {{VAL:…}}` (5; the pass skips text that ends at a marker).
- renown_data_d10.py SIMPLE overlay: `UPKEEP_TRACKS["Pursuit"]`, `COSTS["Pursuit upkeep"]` f-strings `Per turn {…}` → `Each Empire Phase: {…}`.
- docx_tables / wiki_markers `po_modifiers`: `Faith 1` / `Doubt 1` → `Faith +1` / `Doubt +1`.
