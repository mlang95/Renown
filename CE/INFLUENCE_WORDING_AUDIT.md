# Influence / Authority wording audit

Every clause in Holdings, Infrastructure, Wonders, Heritages, Domain Standings, Actions and Seasons that mentions
Influence, Authority or vote limits (44 clauses). **Status (2026-10-26): A, B and C applied**, with "Max Influence" in place of "Vote cap", Spice Merchant / Jewelry Foundry kept as drawbacks, and The Illusionists' Max Influence following your Cunning rank. Parser patterns updated to match.

## The three templates

| Kind | Template | Meaning |
|---|---|---|
| Influence tokens | **Influence +X** (optionally `per …`, `while …`) | Gain X Influence tokens in the Empire Phase. A clause that names another time (e.g. Grand Tournament's Intrigue Phase exchange) happens then instead. |
| Envoy score | **Authority ±X on …** | Applies while an Envoy is sent and resolved; one that depends on the action or target applies once those are chosen. Never written as "Influence". |
| Vote limit | **Max Influence +X on …** | Raises how much you may Support or Oppose on one vote (base = your Standing rank). Glossary term. |

## Already fit — no change

| Source | Clause |
|---|---|
| Inn, Monastery, Aqueducts | Influence +1 |
| University | Influence +1 per Domain you are Rising |
| Studium Generale | Influence +1 per Established Standing |
| Grand Tournament | 3x in the Intrigue Phase: exchange 500 gold for Influence +1 *(names its own time)* |
| Courier Network | In the Intrigue Phase: Authority −1 on one Envoy |
| Outlaw Rookery | Both Bandit Camps & you have Authority +1 on Personal Cunning Envoys |
| The Hermit Crown | Your Personal Envoys have Authority +1 · other players must spend 2 Influence to affect your Envoys by 1 |
| The Inner Circle | Each player allied with you has Authority +1 on their Personal Envoys · Once per Envoy Phase, you may spend 1 of an ally's Influence… |
| The Final Word | Ignore the innate Doubt and Influence modifiers for being At War |
| The Eternal Court | Your unspent Influence isn't discarded in the Rest Phase |
| Prowess Sovereign | No longer lose Influence while at War |
| Indomitable (Prowess Rising) | In the Tally Phase, you may Support one of your own Prowess Envoys |
| Jester's Court | First and second Oppose on an Envoy of yours each Envoy Phase: reduce by 1 |
| Forgery Workshop | Extort 300 anytime a player Opposes an Envoy of yours |
| Spring | Players don't gain or spend Influence tokens |

## Suggested rewrites

### A. "each Empire Phase" is now implied — trim it (optional, for one consistent form)

| Source | Now | Suggested |
|---|---|---|
| Bell Tower | Influence +1 each Empire Phase | Influence +1 |
| Academy | gain Influence +1 each Empire Phase | Influence +1 |
| Town Hall | Influence +1 each Empire Phase | Influence +1 |
| Grand Vizier (Cunning Established) | Influence +1 each Empire Phase | Influence +1 |
| Senate Hall | Faith +1, gain Influence +1 per other player each Empire Phase | Faith +1; Influence +1 per other player |
| The Illuminated Order | Each Empire Phase, gain Influence +1 for every 3 Holdings you have | Influence +1 per 3 Holdings you have |
| War College | Gain Influence +2 while At War | Influence +2 while At War |
| The Entwined Crown | …each member gains Faith +1 and Influence +1 each Empire Phase | *keep* — "each Empire Phase" also times the Faith |

### B. Authority — one preposition ("on"), and say whose Envoys

| Source | Now | Suggested |
|---|---|---|
| Bell Tower | Authority +1 to envoys sent during the Council Phase | Authority +1 on your Council Envoys *(same as Academy's)* |
| Academy | Authority +1 to Council Envoys | Authority +1 on your Council Envoys |
| Chandlery | Authority −1 to Cunning actions targeting you | Authority −1 on Cunning actions targeting you |
| Spice Merchant | Authority +1 to Cunning actions targeting you | **Check:** this *helps* Cunning actions against you — intended as a drawback? |
| Jewelry Foundry | Authority +1 to Cunning actions targeting this player | **Check:** "this player" = you? Same drawback question as Spice Merchant |
| Abbey | Authority −1 to Piety actions targeting you | Authority −1 on Piety actions targeting you |
| Caravanery | Authority −2 to Intercept Caravan actions targeting your settlements | Authority −2 on Intercept Caravan actions targeting your Settlements |
| Execution Dock | Authority −2 to Foster Rebellion actions targeting your settlements | Authority −2 on Foster Rebellion actions targeting your Settlements |
| Wooden Walls | Authority −2 to Raze actions from players targeting your settlements · Authority −1 to Bandit Cunning actions targeting your settlements | Authority −2 on Raze actions targeting your Settlements · Authority −1 on Bandit Cunning actions targeting your Settlements |
| Stone Walls | Authority −2 to Destabilize actions from players targeting your settlements · Authority −1 to Bandit Cunning actions … | Authority −2 on Destabilize actions targeting your Settlements · Authority −1 on Bandit Cunning actions targeting your Settlements |
| Road Wardens | Authority −1 to Bandit Cunning & Prowess actions targeting your settlements or armies | Authority −1 on Bandit Cunning & Prowess actions targeting your Settlements or Armies |
| The Smoldering Crown | Your Cunning Envoys have Authority +2 when targeting a player with Public Order greater than 1 | Authority +2 on your Cunning Envoys targeting a player with Public Order 2 or higher |
| The Illusionists | Your Diplomacy Envoys use your Cunning Standing for their innate Authority | Your Diplomacy Envoys start at Authority equal to your Cunning rank *(vote cap stays the Era's — or should it follow too?)* |

### C. Vote limits → "Max Influence"

| Source | Now | Suggested |
|---|---|---|
| University | May spend one additional Influence per Support or Oppose | Max Influence +1 on every Envoy |
| The Eternal Court | While the Era is Zenith, you may spend up to 5 Influence per Envoy while voting, regardless of your Domain Standing | While the Era is Zenith, your Max Influence is 5 on every Envoy |

Board note: the board's parser reads several of these phrasings; any rewrite you approve gets its parser pattern updated
in the same change, and `--effects-report` / `parity_efx.js` confirm nothing stopped matching.
