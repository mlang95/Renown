# Renown — Comprehensive Rules: outline

Two books from one source, the way MTG has the Comprehensive Rules and a starter rulebook:

| Book | Purpose | Built from |
|---|---|---|
| **Comprehensive Rules (CR)** | Every rule, numbered, unambiguous; the reference for disputes and for the board/engine | new `CE/RULES_comprehensive.md` + the same `{{VAL}}` / `{{TABLE}}` / `{{GLOSSARY}}` markers |
| **Quick Start (QS)** | Learn-to-play in one sitting; omits edge cases, points to CR numbers | new `CE/RULES_quickstart.md`, same markers |

`RULES_push_simple.md` stays the source until the CR exists, then becomes the QS or is retired — your call.

## Numbering convention (MTG style)
- `NNN.` section · `NNN.n` rule · `NNN.na` sub-rule. Example: `501.3b`.
- Numbers are written in the md, never auto-generated (they must stay stable across versions).
- A check script fails the build on duplicates, gaps in a sequence, and dangling cross-references (`see 604.2`).
- Every number the data holds is a `{{VAL:}}`; every list (actions, holdings, timers) is a marker.
- Each section ends with its `{{GLOSSARY:Category}}` table; the Index lists rule numbers as well as pages.

## Section map
Status: **have** = existing rules text covers it · **part** = covered but not to CR precision · **gap** = no rule text yet.
Source = current heading in `RULES_push_simple.md` (line) or data name.

### 100. Game Concepts
| # | Rule | Source | Status |
|---|---|---|---|
| 100 | General (players, goal, the Realm) | Introduction 7, Game Synopsis 11 | part |
| 101 | Golden rules (Granted Power, specific over general, can't beats may, do as much as possible) | Core Principles 74 | have |
| 102 | Players, Alliances, the Host, the Duke | The Turn 113 (Host), Treaties 331 | part |
| 103 | Starting the game | Setup 206–222 | have |
| 104 | Ending the game; Edicts; winning | How to Win 31, `EDICTS` | part |
| 105 | Domains and Standings | Domains & Standings 304, `STANDING_THRESHOLDS`, `DOMAIN_BOARD` | have |
| 106 | Resources: Gold, Influence, Authority, Faith, Doubt, Public Order, Renown, Domain Points | Key Resources 47, `TERM_ENVOY_SCORE`, `RENOWN_MAX` | part |
| 107 | Numbers: X, rounding, dice, natural rolls, Focused, caps | Core Principles 9–11, `FACES`, `CAP_THR` | have |
| 108 | Reading rules text: may / must / can't, While / When / At, Cost / Effect / Endorsed, reminder text | Reading These Rules 61 | have |
| 109 | Ownership and Control (pieces, Settlements, Territory) | scattered (Reach 377, Capture 609) | gap |
| 110 | Timers: set, count down, resolve at 0, order | Timers 125, `TIMERS` | part |
| 111 | Range, Territory, Reach, Province | Territory & Terrain 411, `{{GLOSSARY:Map & Range}}` | have |

### 200. Components
| # | Rule | Source | Status |
|---|---|---|---|
| 201 | Settlements and tiers | Settlements 363, `SETTLEMENTS` | have |
| 202 | Settlement Wards | 369 | part |
| 203 | Holdings (types, Natural, Root, Mastery Chain) | Core Principle 14, `NODES`, `TYPE_ORDER` | part |
| 204 | Infrastructure and tiers | 387, `INFRASTRUCTURE` | have |
| 205 | Wonders and Monuments | 387, `WONDERS` | have |
| 206 | Armies and Retinues | Armies 489, `RETINUES`, `ARMY_MAX_RETINUES` | have |
| 207 | Equipment and keywords | Equipment 688, keyword glossary | have |
| 208 | Tactics | Tactic Matrix 573, `TACTICS` | have |
| 209 | Factions | Factions 708, `FACTIONS` | have |
| 210 | Bandit Camps and Bandit Armies | Bandits 622 | have |
| 211 | Tokens and markers (Host, Fatigue, Debt, Blocked, Strained, Damaged) | scattered | gap |

### 300. The Map
| # | Rule | Source | Status |
|---|---|---|---|
| 301 | Realm, Region, Territory | glossary | have |
| 302 | Terrain and its effects | `TERRAIN` table | have |
| 303 | Controlled / Contested / Uncontrolled; Province; Border | 411, glossary | have |
| 304 | Outlaw Country | 624 | have |
| 305 | Chartering placement (ranges, terrain, Hamlet) | 373, 381, `CHARTER_MIN_RANGE`, `HAMLET_RANGE` | have |

### 400. Turn Structure
| # | Rule | Source | Status |
|---|---|---|---|
| 400 | General: phases, starting player, Host | The Turn 113 | have |
| 401 | Empire Phase — numbered steps 401.1–401.12, in order | Empire Phase 133 | part (order of steps listed; ordering *within* a step undefined) |
| 402 | Council Phase | 159 | have |
| 403 | Envoy Phase | 171 | have |
| 404 | Battle Phase | 182 | part |
| 405 | Rest Phase | 186 | have |
| 406 | Seasons (Spring exceptions as numbered rules) | Seasons 200, `SEASONS` | part |
| 407 | Eras | Game Structure 41, `ERAS` | have |

### 500. Envoys, Voting and Actions
| # | Rule | Source | Status |
|---|---|---|---|
| 501 | Sending an Envoy | 228 | have |
| 502 | Authority (an Envoy's score) | 232, `DOMAIN_BOARD` | have |
| 503 | Voting: order, Support / Oppose / Abstain, caps | 232–246 | have |
| 504 | Net Authority and outcomes | `{{TABLE:net_influence}}`, `ENVOY_OUTCOMES` | have |
| 505 | Performing an action; choosing targets | 248–256 | part |
| 506 | Costs | `COSTS`, action `cost` | part |
| 507 | Endorsed and Condemned effects | `{{TABLE:envoy_outcomes}}` | have |
| 508 | Special rules: Ulterior Motive, Diplomatic Mission | 288, 298 | have |
| 509–513 | Action lists by Domain | `{{ACTIONS:*}}` | have |

### 600. Effects and Timing
| # | Rule | Source | Status |
|---|---|---|---|
| 601 | Static (While), triggered (When / At), one-shot effects | Reading These Rules 61 | part |
| 602 | Once per turn; "first X each turn"; stacking to the player's benefit | Principle 4, Public Order 427 | part |
| 603 | Simultaneous effects: who chooses order | — | gap |
| 604 | Damaged, Repaired, Razed | Principle 6, Raze action | part |
| 605 | Extort and Recoup (transfer only; never below 0) | glossary | part |
| 606 | Immune / Negate | keyword glossary | have |

### 700. Economy
| # | Rule | Source | Status |
|---|---|---|---|
| 701 | Treasury, Revenue, Upkeep | 441 | have |
| 702 | Taxes and Seasons | 481, `SEASONS` | have |
| 703 | Trade | 464, `TRADE_RULES` | have |
| 704 | Insolvency and Bankruptcy | 451 | have |
| 705 | Public Order bands and modifiers | 427, `PUBLIC_ORDER`, `PO_MODIFIERS` | have |

### 800. Diplomacy
| # | Rule | Source | Status |
|---|---|---|---|
| 801 | Treaties, Alliances, Trade Agreements, NAPs | 331, `TREATIES`, `ALLIANCE_RULES` | have |
| 802 | War: Declare War, At War, Truce | Declare War action, Truce Timer | part |
| 803 | Vassalization | 339 | have |

### 900. Armies and Movement
| # | Rule | Source | Status |
|---|---|---|---|
| 901 | Mustering | Mustering 501, Muster action | have |
| 902 | Speed and its modifiers | `Speed X`, Seasons, roads, Holdings | part |
| 903 | Moving: legal hexes, terrain cost, Water, Impassable | `TERRAIN`, `MOVEMENT_MODIFIERS` | part |
| 904 | March, Battle, Lay Siege modes | Move action | have |
| 905 | Army states: Blocked, Strained, Fatigued, Routed | 511, glossary | have |

### 1000. Battle
| # | Rule | Source | Status |
|---|---|---|---|
| 1001 | Beginning a Battle; Attacker / Defender; Seize the Initiative | 521–537 | have |
| 1002 | Skirmish steps 1002.1–1002.11 | 539 | have |
| 1003 | Strikes, Saves, Parry, Riposte, Recover | 539, keyword glossary | have |
| 1004 | Morale, Panic, Break, Rout, Fall Back | 539, glossary | have |
| 1005 | Ending a Battle; Spoils of War; War Weariness | 563 | part |
| 1006 | Battle terrain | `TACTICAL_TERRAIN` | part |

### 1100. Sieges
| # | Rule | Source | Status |
|---|---|---|---|
| 1101 | Laying Siege; Siege Timer | 593–607, `SIEGE_CALCULUS` | have |
| 1102 | Resolving: negotiate, Battle, Capture, Sack | 609 | part |
| 1103 | Sally Forth; Garrisons | glossary, Garrison Infrastructure | part |

### 1200. Bandits
| # | Rule | Source | Status |
|---|---|---|---|
| 1201 | Spawning and growth | 630–646 | have |
| 1202 | Bandit Domain value, actions, tactics | 648, `BANDIT_*` tables | have |
| 1203 | Bandit Army behaviour; attacking camps | 666–682 | have |

### 1300. Variants
| # | Rule | Source | Status |
|---|---|---|---|
| 1301 | The Duke | Game Synopsis 19 | gap |
| 1302 | Quick Start differences | — | gap |
| 1303 | Player-count adjustments | `BOARD_SIZES` | gap |

### Glossary · Index (rule numbers + pages) · Changelog per VERSION

## Quick Start book (candidate contents — you choose what to cut)
1. What you're doing (1 page: Edicts, Renown, the four Domains)
2. Setup (`EMPIRE_START_TIERS`, `STARTING_TREASURY`)
3. A turn on one page (the five phases, one line each)
4. Sending and voting on Envoys (the core loop, with one worked example)
5. The most-used actions per Domain (candidates: Move, Charter, Build, Sign Treaty)
6. Money and Public Order in one table
7. Fighting: a one-page Skirmish summary (points to CR 1000)
8. "When this comes up, see CR ###" list (Sieges, Bandits, Vassals, Insolvency, Seasons)

## Gaps the CR has to settle (questions for you, not rules)
| CR | Question |
|---|---|
| 109 | Who controls a captured Settlement's Holdings while the Capture Timer runs? |
| 401 | Inside one Empire Phase step, in what order do players / effects resolve (e.g. two Extorts, two timers hitting 0)? |
| 402 / 406 | In Spring, does the Host token still set the starting player (board assumes yes)? |
| 603 | When effects trigger at the same time, who orders them — active player, Host, each owner? |
| 605 | Is Condemned a "fail" for Diplomatic Mission (board assumes yes)? |
| 903 | Can an Army move through hexes holding other Armies, Settlements or Bandit Camps? Can it end on them? |
| 903 | Tundra "gain Strained": on entering, passing through, or ending the move there (board: passing through)? |
| 902 | Speed effects with conditions (e.g. Elder Grove) — any that should apply automatically? |
| 1005 | Spoils of War when the loser Falls Back or Routs — same as destroyed? |
| 1102 | Sack: Wards are counted, not placed — what defines "one Ward's Holdings" (a chain sharing a Ward)? |
| 1103 | What happens to the defender's Armies / Garrison inside a Captured Settlement? |
| 1301 | Duke rules: none exist in the rules file yet |
