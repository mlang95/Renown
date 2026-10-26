# "You / this player / the target" wording audit

Scope: every Holding, Infrastructure, Wonder, Heritage, Domain Standing and Action text.
**Applied already:** the conventions below are in *Reading These Rules* and the glossary ("Targeting you"), and the Bandit lines
(Wooden Walls, Stone Walls, Road Wardens) now read "…targeting you". **Status (2026-10-26): every rewrite below applied** (not the optional Actions section). The Iron Shore extorts "the attacker"; The Bloodied Cross hits each *other* player. Parser patterns updated; parser hits unchanged apart from the reworded text.

## The standard

| Say | Means | Don't say |
|---|---|---|
| **you / your** | the player whose Holding, Infrastructure, Faction or Standing it is | this player, the player, its owner |
| **targeting you** | you *and* what you own (Settlements, Armies, Holdings) | targeting you or your Settlements, targeting this player |
| **your Settlements / your Armies** | the ones you Control (a Settlement you don't currently Control isn't yours) | controlled Settlements, Settlements you Control |
| **another player** | one player other than you | a player (when you're excluded) |
| **each other player** | every player but you | all other players, every other player, other players (as a group) |
| **each player** | every player, you included | — (use only when you're included) |
| **the target** | the player or piece an action chose | that player (fine only right after "Choose a player" in the same sentence) |
| **non-allied** | lower-case, always | non-Allied |
| **Army / Settlement** | capitalized defined terms | army, armies, settlement |

## Fixes that change how a rule reads

| Source | Now | Suggested | Why |
|---|---|---|---|
| Caravanery | Authority −2 on Intercept Caravan actions targeting your Settlements | Authority −2 on Intercept Caravan actions targeting you | Intercept Caravan targets a *player* ("Choose a player"), so the current wording never applies |
| Execution Dock | Authority −2 on Foster Rebellion actions targeting your Settlements | Authority −2 on Foster Rebellion actions targeting you | Same: Foster Rebellion targets a player |
| The Iron Shore | When you are the target of a Raze action, Extort 2000 from the target that performed the Raze action | When a Raze action targets you, Extort 2000 from the player who performed it | "the target" here is actually the attacker |
| The Bloodied Cross | Each player gains Doubt +1 each Empire Phase per Sacred War you're on | **Check:** each *other* player, or you too? | "each player" includes you |

## Owner wording ("this player" → you)

| Source | Now | Suggested |
|---|---|---|
| Interrogation Chambers | Actions targeting this player that cause Doubt are reduced by 1, to a minimum of 0 | Doubt from actions targeting you is reduced by 1 (minimum 0) |
| Plague Pit | This player cannot be the target of a Convert action | Convert actions can't target you |
| Execution Dock | Players who target you or your Settlements with actions that would cause Doubt before modifiers gain Doubt +1 | Players whose actions targeting you would cause Doubt (before modifiers) gain Doubt +1 |

## "targeting your Settlements" → "targeting you" (same meaning under the new convention)

| Source | Now | Suggested |
|---|---|---|
| Wooden Walls | Authority −2 on Raze actions from players targeting your Settlements | Authority −2 on Raze actions from players targeting you |
| Stone Walls | Authority −2 on Destabilize actions from players targeting your Settlements | Authority −2 on Destabilize actions from players targeting you |
| The Iron Faith | …Lay Siege actions targeting Settlements you Control have Siege Timer +3 | …Lay Siege actions targeting you have Siege Timer +3 |

## "Controlled" → "your"

| Source | Now | Suggested |
|---|---|---|
| Granary | Armies and Garrisons within controlled Settlements gain Immune Strained | Armies and Garrisons within your Settlements gain Immune Strained |
| Citadel | Controlled Settlements gain Reach +1 | Your Settlements gain Reach +1 |
| The Winter Wolves | …Extort their upkeep from that settlement's controller | …Extort their upkeep from that Settlement's owner |

## Groups of other players

| Source | Now | Suggested |
|---|---|---|
| Pilgrimage Site | Extort 500 every player without a Pilgrimage Site · Doubt +1 to all other players without a Pilgrimage Site | Extort 500 from each other player without a Pilgrimage Site · each other player without a Pilgrimage Site gains Doubt +1 |
| Papal Palace | Tithe every other player with lower Piety | Tithe each other player with lower Piety |
| Senate Hall | Influence +1 per other player | *OK* |
| Smuggler's Nook | …instead target other players randomly | …instead target another player at random |
| One True Gospel (Piety Established) | all other non-allied players with a lower Piety value gain Doubt +2 | each other non-allied player with a lower Piety value gains Doubt +2 |
| Imperial Palace | all non-allied players with a lower Prowess value gain Doubt +2 | each non-allied player with a lower Prowess value gains Doubt +2 |
| Aristocratic Court | Extort 1000 from each non-allied player with a lower Treasury | *OK* |
| The Hermit Crown | You Abstain on every vote on other players' Envoys, and other players must spend 2 Influence… | *OK* ("other players'" possessive reads fine) |

## Capitalization

| Source | Now | Suggested |
|---|---|---|
| Toll House | non-Allied Army | non-allied Army |
| Caravanery | non-allied armies in your Province | non-allied Armies in your Province |
| Office of Works | Settlements & allied armies inside them | Settlements & allied Armies inside them |
| High Quartermaster (Prowess Sovereign) | May change equipment on your armies during any upkeep phase where that army is within Province | May change equipment on your Armies during any Upkeep step while that Army is within your Province |
| The Squatters' Crown | you only pay upkeep on your armies | you only pay upkeep on your Armies |

## Actions (optional — they read fine today)

Actions introduce their target with "Choose a player" and then say *they / their / that player*. That's clear inside one action;
the only suggestion is to say **the target** once it's chosen, e.g. Intercept Caravan "The next turn the target is Host, Extort their Trade Income".
Left as-is unless you want them uniform.

Parser note: every row above that the board reads (defend, Doubt reduction, Siege Timer, Tithe/Extort groups) gets its pattern
updated in the same change, checked with `--effects-report` and `parity_efx.js`.
