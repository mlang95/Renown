# Renown
 A turn-based strategy game of empire building, diplomacy, and domain mastery.

{{TOC}}

# Introduction

Within the Realm, Empires expand, specialize, confer, and when diplomacy fails—battle. You will lead your humble Province to greatness. **Settle** new Villages and **Expand** them, **build** your economy, and **negotiate** your way to victory. Will your religion dominate the **Realm**? Will your economy grow until your wealth is undeniable? Can you build a **world wonder**? Can you **extort** your way to victory? Pick your Faction, command your Domain, and pursue your Craft in this political grand strategy, where every action you attempt can be **endorsed** or **condemned** by your allies and other players.

### Game Synopsis

**Renown** is a turn-based political strategy game for 1–7 players (3+ preferred) set in a medieval world of competing lords. Each player controls a growing empire — Settlements, Armies, and Holdings — but the game's central tension isn't military. It's political.

Every action you want to take has to survive a vote. When you move your Army, build a road, or sabotage a rival, every other player at the table gets to spend political Influence to support or bury it. The strength of your relationships, the Alliances you've built, and the favors you're owed decide whether your plans succeed — not just your resources.

Between votes, you're managing a medieval economy: taxing Settlements, building Holding chains from Raw Materials into production and on to powerful Holdings and Monuments, trading with neighbors, and keeping your Public Order stable enough that your people don't descend into open rebellion. Stretch too thin and your Armies can't march, your tax income plummets, and your enemies smell blood.

Combat exists and matters — sieging Settlements, clashing Armies in tactical Skirmishes with a tactic-versus-tactic matrix — but war is expensive, politically punishing, and rarely the fastest path to victory. You can win by building a Wonder, holding {{VAL:WEALTH_EDICT_GOLD}} gold in your Treasury for five consecutive turns, vassalizing a rival, sustaining Living Saints-level devotion for five turns, or simply outlasting every Alliance but your own.

The Duke variant adds a GM-like referee who manages Bandits, resolves disputes, enables Private Actions and asymmetric information, creates global events and enemies, and keeps the world breathing around the players.

This game is for:

1. Friends looking for rich, deep mechanics to immerse and invest themselves in.

2. Advanced board game players who want their favorite components of many games combined in one.

3. Players who want a TTRPG experience: the Duke as GM, asymmetric information, private actions, and many more crunchy, flavorful mechanics.

### How to Win (Edicts)

Whichever player has completed the most **Edicts** from the list below when the Last Alliance Standing condition is met wins the game.

When an Edict is completed, increase the Renown tracker by 1. Any player may complete any Edict multiple times.

{{TABLE:edicts}}

An Edict that requires consecutive turns uses a timer that must advance each turn. If for any reason it doesn't advance, remove the timer until it's restarted.

### Game Structure

A game of Renown runs over many turns, grouped into four Eras. Each Era grants bonuses to all players once it becomes active, and an Era becomes active once the Renown tracker equals its requirement.{{IDX:Era}}

{{TABLE:eras}}

# Core Rules

## Reading These Rules

A few conventions make every rule in this book read the same way:

- **may** marks something optional. If a rule doesn't say *may*, it's mandatory.
- **can't** and **doesn't** are hard stops (see Core Principle 2).
- Effects are written by *when* they apply: **While X** is always on; **When X** / **At X** happens once, at that moment; an action's **Cost / Effect / Endorsed** happens when you take the action.
- Limits are written by *window*: **At the Start of the Empire Phase** happens once, in that step; **Each <Phase>** happens every time that phase does; **Once per <Phase>** can be used once, only during that phase; **Once per turn** can be used once, in any phase — a trigger such as *when an Army ends a Move action* fires in whichever phase the Move happens.
- **Choose one:** marks a set of options from which you pick exactly one.
- *Italic text is reminder, example, or strategy — it explains the rule but never changes it; the plain-text rule governs.*
- Capitalized terms (Army, Envoy, Standing, Holding, Treaty…) are defined terms — each section closes with a glossary of the terms it introduces, and the Index at the back lists every term with its page numbers.

{{GLOSSARY:Reading the Rules}}

## Core Principles

1. **Granted Power.** Any mechanic not explicitly described doesn't function.

2. **Specific over general.** A more specific rule overrides a general one.
    2.1 *Example: Inquisitorial Palace ≥ Established Cunning > general Cunning rule.*
    2.2 When two effects conflict, the one that says can't (or doesn't) takes precedence over one that says you may or must.

3. **Public information.** All information is public: resources, Domains, Treaties, Armies, Holdings, and Garrisons are known to all players.

4. **Once per turn, same target.** A once-per-turn effect can't be used on the same target twice in a turn.

5. **One effect per Holding.** A Holding has a single effect, active while the Holding is active.

6. **Damaged means inactive.** A Damaged Holding or Infrastructure has no effect.

7. **Timer 0 resolves immediately.** Any Timer whose initial value is 0 or less resolves at once.

8. **Do as much as possible.** Follow as much of an effect as you can; ignore any part you can't carry out.

9. **Dice.**
    9.1 If a roll is modified beyond {{VAL:CAP_THR}}+, it automatically fails.
    9.2 You can't re-roll a re-roll, and you can't re-roll a successful roll.
    9.3 Effects that occur on a 1 or {{VAL:FACES}} occur on unmodified rolls of 1 or {{VAL:FACES}}.

10. **Rounding (denomination of 100).**
    10.1 When a gold amount isn't divisible by 100, round down to the nearest 100, minimum 0.
    10.2 If your Treasury is negative, round up to the nearest 100 instead.

11. **Order of operations.** When adding and multiplying, add all values first, then multiply. If several things multiply against the same sum, add the multiplication values together first.

12. **Equal values.** If one value equals a second, and the second equals a third, then the first and third are equal.

13. **Mastery Chain.** A Holding's Mastery Chain is the line of Holdings it builds from, usually running from a Raw Material up to a Monument. {{RULE:mastery-chain}}
    13.1 You may start building a Holding only while you control one complete line of its Mastery Chain, anywhere in your empire; this is checked only when you start it.
    13.2 A Root Holding has no Mastery Chain requirement. {{RULE:root}}
    13.3 A Holding placed in the same Settlement Ward as its immediate parent shares that Ward, and the chain can continue upward the same way. Each Holding carries at most one descendant in its Ward.
    13.4 You can't build a Holding onto one whose Build Timer is still active. A Damaged Holding under a Repair Timer can still be built onto.

14. **Scope.** Each Holding and Infrastructure has a Scope that limits how many of it can exist.
    14.1 *Settlement* — one per Settlement (Raw Materials).
    14.2 *Empire* — one per player (every other Holding and Infrastructure).
    14.3 *Realm* — one per game (Monuments and Wonders). A Realm piece is taken once any player has placed it, including while it's under construction.

## Resources

- **Gold / Treasury** — your spendable wealth. Pays for Actions, upkeep, and Muster recruitment. Running out triggers Insolvency (see Treasury & Upkeep).
- **Domain Points** — gain {{VAL:DOMAIN_POINTS_PER_TURN}} each Rest Phase and spend it to raise a Domain value by 1 (see Domains & Standings).
- **Influence** — the weight you bring to Envoy votes: spend it to Support or Oppose other players' Envoys (see Actions & Voting).
- **Renown** — the score of the table. Gained each Rest Phase and by completing Edicts; it sets the Era. {{RULE:renown-track}}
- **Public Order** — the stability of your realm, raised by Faith and lowered by Doubt. Its band sets ongoing effects (see Public Order).
- **Faith** — devotion, generated mostly by Piety Holdings; each Faith raises your Public Order by 1.
- **Doubt** — instability; each Doubt lowers your Public Order by 1. Some powerful Holdings cost you Doubt; Cunning and Piety actions give it to others.

## The Turn

Each turn runs through five phases in order, then passes the Host and repeats:

1. **Empire Phase**{{IDX:Empire Phase}} — Start of the Empire Phase effects, the Season, Timers, Bandit Mechanics, Influence & Envoys, income and upkeep, Public Order.
2. **Council Phase**{{IDX:Council Phase}} — a Council vote on a Domain; each player then performs one action of that Domain.
3. **Envoy Phase**{{IDX:Envoy Phase}} — send all Envoys, a Forum, the Intrigue Phase, vote on every Envoy, the Tally Phase, then resolve them all (Diplomacy → Prowess → Cunning → Piety → Industry).
4. **Battle Phase**{{IDX:Battle Phase}} — Skirmishes, Sieges, and Battles resolve.
5. **Rest Phase**{{IDX:Rest Phase}} — cleanup, advance the Season, score Renown, spend one Domain Point, pass the Host.

**The Host.** Each turn except Spring, one player is the Host. The starting player is always the player directly clockwise from the Host token, including in Spring. The role passes clockwise each Rest Phase (except in Spring). The Host runs most of the Empire Phase's administration: collecting and distributing Trade Income, resolving Bandit Mechanics, and breaking ties (Council vote, Bandit targeting, and anything not otherwise resolvable). The Host Card carries the step-by-step detail. {{RULE:host}}

### Timers

Many actions set a Timer to a number of turns. Each Empire Phase, every active Timer counts down by 1; when a Timer reaches 0 it resolves and is removed (a Timer set to 0 or less resolves immediately). Each action states its own Timer's length — the named types (Build, Repair, Muster, Siege, Sack, Capture, Convert, Truce) are labels for *what* resolves; the rule is the same for all of them.

{{TABLE:timers}}

*(Siege shows "—" in this table because it's computed — see Siege Warfare.)*

### Empire Phase

1. **Start of the Empire Phase** — resolve every effect that happens at the Start of the Empire Phase, including Domain Standing effects (see Domain Standings).
2. **Season** — apply this turn's Season effect.
3. **Timers** — count down every active Timer by 1 (Build, Repair, Truce, Siege, Muster, Sack, Capture, in that order), then resolve each Timer that reached 0.
4. **Bandit Mechanics** (the Host resolves) — grow Bandit Camps by the Era; convert any camp of {{VAL:BANDIT_ARMY_THRESHOLD}} Retinues into a Bandit Army; Bandit Camps perform Cunning actions; Bandit Armies perform Move actions; spawn new Bandit Camps (in Spring, from Foster Rebellion, or from an Uprising).
5. **Influence & Envoys** — gain Influence (not in Spring) from the Era, innate modifiers (Trade Partners, Alliances, At War, etc.), Holdings, and Infrastructure; then gain the Era's Envoys.
6. **Income & Upkeep** — in this order: in Winter only, gain tax income from each of your Settlements by tier (see Settlements); gain Holding income; if there is a Host, the Host collects trade income and distributes it among their Trade Partners; pay Army, Holding, Infrastructure, and any other upkeep; resolve Extort effects; check your Treasury for the Wealth Edict condition.
7. **Public Order** — check each innate Faith / Doubt source in the Public Order tables and adjust your Public Order. *(Faith and Doubt from actions are applied the moment they're generated; see Public Order.)*
8. **Endurance** — every Army without **Strained** gains +{{VAL:ENDURANCE_REGAIN}} Endurance; then remove Strained from all Armies. *(An Army can immediately regain these effects after losing them, if applicable.)*
9. **Remaining effects** — resolve any remaining Each Empire Phase effects.

### Council Phase

1. **Forum** — a brief open discussion of which Domain the Council should choose.
2. **Vote** — no talking. Clockwise from the starting player, each player votes for a Domain. The Host's vote breaks a tie; if the Host's vote isn't one of the tied Domains, the Host chooses among them.
3. **Council actions** — clockwise from the starting player, each player sends a free Envoy of that Domain, starting with innate Influence equal to their Domain Standing. Council Envoys **auto-Abstain** — other players can't Support or Oppose them, though automatic Authority ±X modifiers still apply — and their net Influence can't be lower than 1, so they can't fail or be Condemned. A passed Council Envoy performs actions of that Domain equal to the Era's Council actions per Envoy (see Eras). {{RULE:council-envoy}}

### Envoy Phase

1. **Envoy Declaration** — all players place every Envoy they have in the Domains of their choice at the same time, then reveal them together.
2. **Forum** — a brief open discussion of every Envoy on the table: who should be Supported, Opposed, or left alone.
3. **Intrigue Phase**{{IDX:Intrigue Phase}} — no talking. The starting player uses all of their Intrigue Phase effects, then each player clockwise does the same, ending with the Host. Each choice is announced and takes effect at once, before the first vote. {{RULE:intrigue}}
4. **Vote** — no talking. Vote on every Envoy (see Resolving an Envoy): Diplomacy first, clockwise from the starting player; then Prowess → Cunning → Piety → Industry, where within each Domain the sender with the highest Domain value has all of their Envoys of that Domain voted on, then the next highest, and so on (ties clockwise from the starting player). A player whose effect says they cast their votes in the Tally Phase skips this step.
5. **Tally Phase**{{IDX:Tally Phase}} — once every Envoy has been voted on, in this order: {{RULE:tally}}
    5.1 **Supports** — the starting player resolves all of their Tally Phase Supports, then each player clockwise, ending with the Host. Each Support is its own vote, with its own per-vote limit.
    5.2 **Tally votes** — each player who casts their votes in the Tally Phase now votes on every Envoy, in the Vote order.
    5.3 **Endorsements** — the starting player resolves all of their Tally Phase Endorse effects, then each player clockwise, ending with the Host.
    5.4 **End of the Tally Phase** — effects that send another Envoy do so now. Each such Envoy is voted on at once, with players who vote in the Tally Phase voting last, then resolves with the others.
6. **Resolve** — once the Tally Phase ends, resolve each Envoy in the same order: choose and perform its action according to its net Influence.

*All votes are cast before anything resolves, so At War status (for Opposing Industry Envoys) and Treaties are as they stood during the vote.*

### Battle Phase

If a player performed a Battle or Lay Siege Move action this turn, resolve it now — see Battles & Sieges for the full procedure.

### Rest Phase

1. **Discard** any unused Envoy and Influence tokens.
2. **Season** — advance the Season by 1.
3. **Score** — gain {{VAL:RENOWN_PER_TURN}} Renown, then gain and spend {{VAL:DOMAIN_POINTS_PER_TURN}} Domain Point.
4. **Change Host** — rotate the Host token clockwise to the starting player, unless it's Spring.

# Seasons

The Realm cycles through four Seasons.{{IDX:Season}} The current Season's effect is applied during the Empire Phase, and the Rest Phase advances the Season by one. Each time the Season changes to {{VAL:AGE_YEAR_SEASON}}, the Year advances by 1.

{{TABLE:seasons}}

# Setup

## Table Setup

- Domain Board: set Renown to {{VAL:ERAS.Founding.renown}}, set each player's Standing in each Domain to {{VAL:STANDING_THRESHOLDS.Untested}}, set Season to Summer, and set Public Order to 0.
- Tactic Decks, Equipment & Retinue Cards, Holding Tiles, Bandit Camps, and the various tokens.

## Setup Order

1. **Select Map** — choose the Hex Map.
2. **Select Age** — choose an Age and a starting Year within its range (see Ages). Every player starts Rising in that Age's Domain: set that Domain to {{VAL:STANDING_THRESHOLDS.Rising}}. In the Age of Renown, each player chooses their own Rising Domain. Turn 1 takes place in the starting Year.
3. **Select Faction** — pick a Faction Card (optional for new players).
4. **Determine Host** — give the Host Card to the most experienced player. If tied, to whoever wants to Host; if still tied, roll off.
5. **Deploy** — taking turns from the starting player, each player places their capital Town within Range {{VAL:CAPITAL_EDGE_RANGE}} of the board edge or corner. Then each player places their Hamlet exactly Range {{VAL:HAMLET_RANGE}} from their Town. Then each player places their Outlaw Country: its first Territory exactly Range {{VAL:OUTLAW_BUFFER_RANGE}} from their Town, and no Outlaw Country Territory within Range {{VAL:OUTLAW_BUFFER_RANGE}} of their Hamlet.
6. **Wild Outlaw Country** — the Host scatters the remaining Outlaw Country zones over the unclaimed board (see Outlaw Country).

### Ages

An Age{{IDX:Age}} sets the starting Year and which Domain every player starts Rising in.

{{TABLE:ages}}

## Player Setup

- Empire Tableau.
- Collect {{VAL:STARTING_TREASURY}} Gold, 2 Influence Tokens, and 1 Envoy.
- You don't begin the game with any Armies.
- For the first turn, begin at the {{VAL:STARTING_TURN_PHASE_OPENER}} Phase instead of the Empire Phase.

# Actions & Voting

## Action Mechanics

### Sending an Envoy

Envoys are the currency of actions: to perform an action you send an Envoy during the Envoy Phase. Sending costs 1 Envoy, and you must be able to pay the action's cost before you send it. Declare the Domain but not the action — *"I'd like to send a [Domain] Envoy."* Envoys never target: you choose the action, and its target, only after the Envoy passes, so no one knows exactly what will happen until then.

### Resolving an Envoy

Your Envoy begins with Authority equal to your innate Authority in its Domain — Untested {{VAL:DOMAIN_BOARD.innate_influence_own_envoys.Untested}}, Rising {{VAL:DOMAIN_BOARD.innate_influence_own_envoys.Rising}}, Established {{VAL:DOMAIN_BOARD.innate_influence_own_envoys.Established}}, Sovereign {{VAL:DOMAIN_BOARD.innate_influence_own_envoys.Sovereign}} — plus any automatic Authority ±X modifiers. *(These come from your Holdings, Infrastructure, and Faction, and apply on their own; you never spend Influence for them.)* Diplomacy has no Standing; a Diplomacy Envoy begins with Authority set by the Era (Founding {{VAL:ERAS.Founding.innate_diplomacy_influence}}, Ascension {{VAL:ERAS.Ascension.innate_diplomacy_influence}}, Eminence {{VAL:ERAS.Eminence.innate_diplomacy_influence}}, Zenith {{VAL:ERAS.Zenith.innate_diplomacy_influence}}).

Then, clockwise from the starting player and skipping the sender, every other player may respond, with no talking during the vote: {{RULE:vote}}

- **Support X** — spend X of your Influence to raise the Envoy's net Influence.
- **Oppose X** — spend X of your Influence to lower it.
- **Abstain** — spend nothing.

You spend Influence only when you **Support** or **Oppose**; abstaining is free. **You can't vote on your own Envoy.** On a single vote, each player may spend up to their Standing in that Domain (Untested {{VAL:DOMAIN_BOARD.max_influence_per_vote.Untested}}, Rising {{VAL:DOMAIN_BOARD.max_influence_per_vote.Rising}}, Established {{VAL:DOMAIN_BOARD.max_influence_per_vote.Established}}, Sovereign {{VAL:DOMAIN_BOARD.max_influence_per_vote.Sovereign}}). On Diplomacy Envoys the cap is set by the Era instead (Founding {{VAL:ERAS.Founding.max_influence_per_diplomacy_vote}}, Ascension {{VAL:ERAS.Ascension.max_influence_per_diplomacy_vote}}, Eminence {{VAL:ERAS.Eminence.max_influence_per_diplomacy_vote}}, Zenith {{VAL:ERAS.Zenith.max_influence_per_diplomacy_vote}}). Holdings, Infrastructure, and Factions may raise these caps. Unused Influence is discarded in the Rest Phase.

*Each player declares in turn, so the running net Influence is public — later voters can react to it. The Host, sitting just before the starting player, votes last on every Envoy they didn't send.*

*Why this is the heart of the game: at Untested your Envoy starts at {{VAL:DOMAIN_BOARD.innate_influence_own_envoys.Untested}}, and you can't support it yourself — so it can fail if another player opposes you, and be saved if another supports you. Unless players back each other, Envoys fall to cheap opposition; deciding whose actions to lift and whose to bury is the core of every turn.*

### Envoy Resolution Table

Add everything together for the net Influence, then read the outcome:

{{TABLE:net_influence}}

Effects that modify a specific action's Influence — including effects on actions targeting a player — apply after the net Influence is totalled, once the action and its target are chosen. They can raise or lower the result: a would-be pass can become a fail, or be Condemned. On a would-be fail, the player may instead perform a different action of the same Domain targeting the same player or Settlement.

When you perform an action, pay its cost (gold or Doubt) and follow the pass effect. If the action is **endorsed**, also perform the Domain's endorsed effect.

Each outcome resolves differently by Domain — what Condemned, Failed, Passed, and Endorsed each do:

{{TABLE:envoy_outcomes}}

{{GLOSSARY:Council & Envoys}}

## Influence

Each Empire Phase, gain Influence from the following sources:

{{TABLE:influence_gain}}

{{COLS:1}}

## Diplomacy Actions

{{ACTIONS:Diplomacy}}

### Rule: Diplomatic Mission

If your Diplomacy Envoy passes or is endorsed but its action fails, you may send another Envoy in another Domain, resolved in the order it would be resolved alongside other Envoys. A Diplomacy Envoy that fails or is condemned doesn't allow one.

## Prowess Actions

{{ACTIONS:Prowess}}

### Rule: Commanding Presence

An Army can't move within Range {{VAL:PRESENCE_RANGE}} of a non-allied Army — its **Presence** — unless that Move performs a Battle against it. Settlements have Presence while their owner has a Garrison, and Settlement Wards while their owner has a Keep; a Move that performs a Battle or Lay Siege against a Settlement may pass through the Presence of that Settlement and its Wards. Bandit Armies have Presence; Bandit Camps don't. An Army that begins a Move within a non-allied Presence may only move to end outside every Presence (or, if at War, to Battle or Lay Siege); if it can't, it can't move.

## Cunning Actions

{{ACTIONS:Cunning}}

## Piety Actions

{{ACTIONS:Piety}}

### Rule: Wavering Devotion

While your Public Order is below {{VAL:FAITH_FICKLE_PO}}, you can only perform Spread Truth when sending a Piety envoy.

## Industry Actions

{{ACTIONS:Industry}}

### Rule: Ulterior Motive

Unless you are At War with the player sending it, you can't Oppose an Industry Envoy.

{{COLS:2}}

{{GLOSSARY:Actions}}

# Domains & Standings

### Domain Standings

Domains are the identity of your character in Renown. As you gain Renown each turn, you gain a Domain Point, which you may spend in any of the four Domains. Each Domain Point raises your Domain value by 1 in that Domain. When your Domain value reaches *{{VAL:STANDING_THRESHOLDS.Rising}}*, you become Rising in that Domain — you may spend one extra Influence on another player's Envoy of that Domain, and your Envoys gain Authority +1. This continues at a Domain value of *{{VAL:STANDING_THRESHOLDS.Established}}* (Established) and again at *{{VAL:STANDING_THRESHOLDS.Sovereign}}* (Sovereign).

Each Standing you gain in a Domain makes you harder to oppose there and lets you oppose others more easily with your Influence. You also gain a unique effect at each Standing that makes it easier to achieve that Domain's objectives. A Standing effect that lets you perform an action (*Perform …*) is one-time: you use it at the Start of the next Empire Phase after you reach that Standing (a Standing you start the game with: Turn 1). Every other Standing effect applies for as long as you hold that Standing; its *Each Empire Phase* effects resolve at the Start of the Empire Phase.

### Standing & Influence

Your Standing in a Domain sets how much Influence you bring to its Envoys:

| Standing | Innate Influence (your own Envoys) | Max Influence per Vote |
|---|---|---|
| Untested | {{VAL:DOMAIN_BOARD.innate_influence_own_envoys.Untested}} | {{VAL:DOMAIN_BOARD.max_influence_per_vote.Untested}} |
| Rising | {{VAL:DOMAIN_BOARD.innate_influence_own_envoys.Rising}} | {{VAL:DOMAIN_BOARD.max_influence_per_vote.Rising}} |
| Established | {{VAL:DOMAIN_BOARD.innate_influence_own_envoys.Established}} | {{VAL:DOMAIN_BOARD.max_influence_per_vote.Established}} |
| Sovereign | {{VAL:DOMAIN_BOARD.innate_influence_own_envoys.Sovereign}} | {{VAL:DOMAIN_BOARD.max_influence_per_vote.Sovereign}} |

### Domain Identities & Traits

{{TABLE:domain_board}}

{{GLOSSARY:Domains & Scoring}}

# Diplomacy & Treaties

### Treaties & Alliances

{{TABLE:treaties}}

**Alliance Rules:**

{{LIST:ALLIANCE_RULES}}

### Vassalization

To vassalize a player:

1. **Control** that player's capital Settlement while the player has no other Settlements or Armies under their Control.

2. At the end of the Rest Phase, return every Settlement you Control that was chartered by that player to that player. You become their Suzerain, and they become your Vassal.

**While Suzerain:**

- The Vassal immediately ends all existing Treaties and inherits every Treaty the Suzerain holds. For the rest of the game the Vassal's Treaties mirror the Suzerain's exactly — any Treaty the Suzerain signs, ends, or has ended for them applies identically to the Vassal. The Vassal counts as being in a military and defensive Alliance with the Suzerain, but has no say in other players joining the Suzerain's Alliances.
- The Vassal can't perform Diplomacy actions and can't be the target of Diplomacy actions.
- The Suzerain collects:
    - Half of the Vassal's trade income from trading with other players.
    - The first {{VAL:VASSAL_INFLUENCE_TAKE}} Influence the Vassal generates each turn.

**Mutual exchange.** Each Empire Phase, if both players agree, either player may exchange up to {{VAL:VASSAL_EXCHANGE_CAP}} gold, exchange ownership of Settlements, or transfer forces (so long as the Armies are adjacent to each other, or an Army is adjacent to a Garrison), in either direction.

If the Suzerain is vassalized, both the original Vassal and the Suzerain become Vassals of the new Suzerain, and the new Suzerain gains the benefits of each Vassal.

{{GLOSSARY:Treaties}}

# Empire Building

## Settlements

Settlements are the primary vehicle of your Empire.{{IDX:Settlement}} They come in tiers: Village, Town, City, and a capital Metropolis. Each tier provides tax income each Winter, Settlement Wards that a Holding can fill, and a per-turn Muster limit of Retinues. The values per tier are below:

{{TABLE:settlements}}

### Settlement Wards

{{VAL:WARD_RULE}}

### Chartering Settlements

When you Settle a new Village, place it on a Hill that is in your Province or within the Presence of one of your Armies, and at least Range {{VAL:OUTLAW_BUFFER_RANGE}} from any Outlaw Country.

### Settlement Reach

Settlements have a Reach value set by their tier, from {{VAL:SETTLEMENTS.Village.reach}} up to {{VAL:SETTLEMENTS.Metropolis.reach}}. Reach X determines which Territory you Control in your Province: at Reach 1 you Control all Territory within Range 1 of that Settlement. If more than one player Controls a Territory, it's Contested — Controlled by both.

### Hamlets

Hamlets are unique Settlements, placed *exactly* Range {{VAL:HAMLET_RANGE}} from your capital at the start of the game. These small farmland communities produce no tax income or Muster limit, but have {{VAL:SETTLEMENTS.Hamlet.wards}} Settlement Wards. You may only build **Natural** Holdings in a Hamlet, and a Holding in a Hamlet can only share a Ward with its parent if it is itself Natural. You may also build Arable Land in a Hamlet even if that Raw Material isn't in the Hamlet's region.{{IDX:Hamlet}}

{{GLOSSARY:Settlements & Holdings}}

## Infrastructure

Infrastructure is the foundation of your Settlements.{{IDX:Infrastructure}} Each active Infrastructure provides an effect that applies to your entire empire and all its Settlements.

*Example: Wooden Walls protect all Settlements from Bandits and Raze actions, and a Cathedral raises your innate Faith by 2 each turn, regardless of how many Settlements you have.*

Infrastructure comes in 5 ascending tiers.{{IDX:Primitive}}{{IDX:Developed}}{{IDX:Sophisticated}}{{IDX:Prodigious}}{{IDX:Wondrous}} Primitive Infrastructure builds the basic blocks of your empire. Developed Infrastructure expands and replaces some Primitive Infrastructure. Sophisticated Infrastructure allows more powerful effects and helps unlock unique Monument Holdings. Prodigious Infrastructure comes next, and Wondrous Infrastructure — the world Wonders — is the highest tier.

To build any Infrastructure, you need at least one active Infrastructure of the tier below it — so Developed needs one Primitive, Sophisticated needs one Developed (and therefore one Primitive), and so on up to Wondrous. *One Tier Primitive* means any one Primitive Infrastructure. Some Infrastructure also names its own requirement on top of this: a Library needs a Town Hall, and a Cathedral needs a Capital City — so a Cathedral needs one Primitive, one Developed, and a Capital City.

Wonders{{IDX:Wonder}} are the Wondrous tier, with Realm Scope: each is built once per game and needs the Infrastructure named in its requirement. They're Edict-satisfying buildings with very powerful effects. A Wonder exists inside your capital and can't be Razed or Damaged.

The full list of Infrastructure — tiers, build times, upkeep, requirements, and effects:

{{TABLE:infrastructure}}

Build times, in turns, by what you're building:

{{TABLE:build_timers}}

## Territory & Terrain

Territory is the smallest unit of land. To move from one Territory to another, you move Range 1. To be within a Territory is Range 0; adjacent is Range 1; next to is Range 2.

{{TERM:Speed X}} {{RULE:speed}}

Territories carry modifiers by hex type (grassland, forest, barrens, wetlands, water, mountain), and are Uncontrolled, Contested, or Controlled. Territory begins Uncontrolled. By chartering Settlements you Control Territories: each Settlement's Reach X adds every Territory within that Range to your Province. If another player's Settlement Reach reaches any Territory you Control, that Territory is Contested.

To border another player, your Reach must be within or adjacent to their Territory.

{{TABLE:terrain}}

{{GLOSSARY:Map & Range}}

# Economy

## Public Order

Faith and Doubt adjust your Public Order the moment they're generated — each Faith raises it by 1, each Doubt lowers it by 1, applied immediately. Public Order is capped between {{VAL:PO_MIN}} and {{VAL:PO_MAX}}, and your current band's effects (below) are always active at your current value. A band's X is its value in the current Era (the Era columns of the table).

**First Doubt of the turn.** Some effects (e.g. Reliquary, Episcopal Court) reduce *the first Doubt (or first two) you gain each turn, from any source* — each instance of Doubt uses up one reduction. Because Doubt applies immediately, this is whichever Doubt lands first in the turn — usually your innate modifiers in the Empire Phase, but it can be an opponent's action if that resolves first. Track whether you've taken Doubt yet this turn; the marker resets at the Start of each Empire Phase, before innate modifiers apply.

Your innate Public Order modifiers (below) are checked once each turn during the Empire Phase and applied like any other Faith / Doubt.

{{TABLE:public_order}}

### Innate Public Order Modifiers

{{TABLE:po_modifiers}}

## Treasury & Upkeep

Your Treasury is the gold you Control.{{IDX:Treasury}}{{IDX:Revenue}} Each Empire Phase you gain your Revenue (tax, trade, and Holding income) and pay your Upkeep (Armies, Holdings, and Infrastructure); the net lands in your Treasury. Costs you pay during the turn come out of the same Treasury.

**Holding upkeep** and Build Timer follow the Holding's Standing requirement — {{VAL:HOLDING_COST_TEXT}}. Holdings and Infrastructure only pay upkeep while active: none while being built, Damaged, or under repair.

**Army upkeep** = the sum of each Army's cost (by Retinue type) − Upkeep modifiers. Army costs by Retinue type: Levy {{VAL:RETINUES.Levy.cost}}, Man-at-Arms {{VAL:RETINUES.Man-at-Arms.cost}}, Sergeant {{VAL:RETINUES.Sergeant.cost}}, Knight Templar {{VAL:RETINUES.Knight Templar.cost}}.

*Tracking tip: keep three small piles — Treasury, Revenue, Upkeep. When you build something with income or upkeep, add it to the matching pile; when it's Damaged or an Army is disbanded, subtract it. Each turn it's just Treasury + Revenue − Upkeep, with no recounting.*

### Insolvency & Bankruptcy

*This is an exception path — skip it until it happens.*

You go Insolvent the moment your Treasury can't cover a cost in full (at Upkeep, when paying for an action, or when an effect drains your gold). Pay what you can, then cut until the books balance, in this order:

1. **Disband Armies**, one at a time, cheapest-upkeep first, until your Armies are gone.
2. **Set buildings inactive**, highest-tier first (Monuments, then Established & Rising, then all other non-Natural Holdings).

An inactive Holding gives no effect; Holdings built from it are unaffected. An inactive piece is restored at any future Income & Upkeep step where you can pay its upkeep. Build Timers halt while you're Insolvent.

If you've cut everything and a debt still remains, you're Bankrupt: your Treasury goes negative by the unpaid amount (a Debt Marker). While Bankrupt you can't spend gold or be Extorted, and Build Timers stay halted; Revenue pays down the debt first. When your Treasury reaches 0 or above, Bankruptcy ends. *(If you're Vassalized while Bankrupt, the debt is forgiven and your Suzerain pays your Treasury up to a minimum of 0.)*

## Trade & Income

### Who Can Trade

**Who can trade:** a player needs a signed Trade Agreement{{IDX:Trade Agreement}} and either active Dirt Roads or a **Can Trade** effect (e.g. Harbor).

**Craft X:** Craft Holdings count toward how much income your Trade Agreements generate — any effect that grants Craft +X.

**Trade income:** for each active Trade Agreement, both players gain gold equal to {{VAL:TRADE_RULES.income_per_craft}} × the Host's Craft X.

**When income flows:**

- When you sign a Trade Agreement: the player who did *not* perform the Sign Treaty action gets trade income the next time they're Host. Afterwards, both get trade income each turn either of them is Host.
- When you end a Trade Agreement: the player who ended it gets trade income the next time they're Host, then trading ceases.

{{TABLE:trade_rules}}

### Income Types

- **Taxes:** each Winter, in the Income & Upkeep step of the Empire Phase, gain tax income from each of your Settlements by tier, after modifiers.
- **Trade:** see above.
- **Holdings:** gain Holding income in the Income & Upkeep step of the Empire Phase.

{{GLOSSARY:Economy & Public Order}}

# Armies

### Armies Overview

Armies{{IDX:Army}} are collections of Retinues on the Realm, and are the target of Move actions. An Army holds up to {{VAL:ARMY_MAX_RETINUES}} Retinues and up to a single piece of equipment of each type (armor, weapon, shield, and Retinue). Armies cost upkeep each Empire Phase (see Treasury & Upkeep).

While an Army is engaged in a Battle or Lay Siege action started by another player's Army, neither Army can be the target of any actions until that Battle or Lay Siege resolves.

### Mustering

Armies are raised and reinforced with the Muster action (see Prowess Actions).

During the Income & Upkeep step, while an Army is within Range 0 of a Settlement you Control, you may change that Army's equipment to any unlocked equipment.

Retinue types — cost, to-Strike, and base profile:

{{TABLE:retinues}}

### Blocked Armies

A Blocked Army has Initiative -1 in the first Skirmish and can't perform Move actions. An Army gains **Blocked** while it's within a Settlement under Siege, or when it's selected as the result of a condemned Prowess Envoy.

{{GLOSSARY:Army States}}

# Battles & Sieges

## Battle Phase

A Battle is fought as a series of Skirmishes, run through the steps below until one side is wiped out, Routs, or successfully Falls Back. Full keyword detail is in the glossary tables at the end of this section.

### Beginning a Battle

1. **Declare Army** — declare which Army will Skirmish (if more than one is adjacent to either Army in the Battle).

2. **Seize the Initiative** — the player who performed the Battle action usually gains Seize the Initiative, but Terrain and the Ministry of Military Strategy can change that. That player gains Initiative +1 in the first Skirmish. {{RULE:seize}}

### The Skirmish Steps

1. **Form the line.** Each side places up to {{VAL:FRONT_LINE_MAX}} Retinues in its front line — one Strike die each — and may keep up to {{VAL:RESERVE_MAX}} in reserve to replace losses as they fall. An Army of {{VAL:ARMY_MAX_RETINUES}} keeps the remainder in camp; between Skirmishes, camp and reserves refill the front line and reserve to their maximums. {{RULE:form-line}}

2. **Choose Tactics and equipment.** Both players secretly pick one Tactic and, if they have a choice, the equipment they'll use this Skirmish (a Tiltyard Army picks its Ranged or Melee weapon; a Bastard Sword picks its 1H or 2H profile), then reveal together. A One-Shot weapon must be Equipped in the first Skirmish and can't be Equipped after. Only Equipped gear counts: while a 2H weapon is Equipped your Shield gives nothing that Skirmish.

3. **Initiative.** Apply the Initiative and any other modifiers from both Tactics and weapon profiles. Initiative ranges from {{VAL:INITIATIVE_MIN}} to +{{VAL:INITIATIVE_MAX}}. The higher Initiative Strikes first this Skirmish. If tied, both armies strike simultaneously. Resolve this taking turns rolling strikes and saves, but do not apply casualties until both sides have fought. At {{VAL:INITIATIVE_MIN}} or lower you Blunder — your to-Strike is set to {{VAL:BLUNDER_THR}}+, before other negative modifiers. {{RULE:initiative}}

4. **Strike.** The side with the higher Initiative rolls a D{{VAL:FACES}} for each front-line Retinue, applying its modifiers. It Strikes on a result ≥ its to-Strike number (Levy {{VAL:RETINUES.Levy.to_hit}}+, Man-at-Arms {{VAL:RETINUES.Man-at-Arms.to_hit}}+, Sergeant {{VAL:RETINUES.Sergeant.to_hit}}+, Knight Templar {{VAL:RETINUES.Knight Templar.to_hit}}+). A natural {{VAL:FOCUSED_THR}} may trigger Cleave, Deadly, or Destroy Shield. {{RULE:strike}}

5. **Defend.** For each Strike, a defender with Parry may Parry (D{{VAL:FACES}}, {{VAL:PARRY_BASE}}+ cancels; a natural {{VAL:FOCUSED_THR}} Ripostes if the defender has Riposte), then Saves (D{{VAL:FACES}} + the weapon's AP + the shield's bonus ≥ the armor value), then a defender with Recover may Recover (after a failed Save, a final D{{VAL:FACES}} ≥ the Recover value). Unsaved, unrecovered Strikes are casualties, and leave the field at once. Then the other side Strikes, and is defended against, the same way, if able. {{RULE:defend}}

6. **Panic check.** After both sides have Struck, each side that took more than {{VAL:PANIC_CASUALTY_THRESHOLD}} casualties this Skirmish (Strikes it Recovered still count, unless it has Enduring) takes a Panic check: roll its Morale, up to {{VAL:MORALE_DICE_MAX}} dice; failures are casualties. A check ever modified to {{VAL:ROUT_THR}} or more Routs the whole Army. {{RULE:panic}}

7. **Fatigue.** Each side that fought loses 1 Endurance; a side at 0 Endurance is Fatigued. Each Fatigued side's field then takes a Break check — roll a D{{VAL:FACES}} per Retinue in the field, up to {{VAL:MORALE_DICE_MAX}} dice, each ≥ its modified Morale value; failures are casualties, and a Break check never triggers a Panic check — and then gains a Fatigue token: each token is −{{VAL:FATIGUE_MORALE}} to that Army's Morale rolls; tokens stack and last until the Battle ends. A check ever modified to {{VAL:ROUT_THR}} or more Routs the whole Army. {{RULE:fatigue}}

8. **End the Skirmish.** The Battle ends if a side is wiped out, Routs (modified Morale {{VAL:ROUT_THR}}+), or successfully Falls Back. Otherwise refill the lines and begin the next Skirmish. {{RULE:end-skirmish}}

### Ending a Battle

1. **Clean up** — remove all Fatigue tokens.
2. **Spoils of War** — the player who won Extorts the unmodified cost of the opposing Army, by its Retinue type.

### Tactic Matrix

{{TABLE:tactic_matrix}}

{{GLOSSARY:Battle Structure}}

{{GLOSSARY:Combat Keywords — Defense}}

{{GLOSSARY:Combat Keywords — Offense}}

{{GLOSSARY:Combat Keywords — Handling}}

{{GLOSSARY:Combat Keywords — Immune / Negate}}

## Siege Warfare

- When you Lay Siege{{IDX:Lay Siege}} during the Envoy Phase, track the relevant Siege Timer(s).
- When a Siege Timer reaches 0, resolve the Siege before the Rest Phase: negotiate, then Battle if needed, then Capture or Sack.

### Siege Timer

A Siege Timer is the sum of the besieged Settlement's defenses minus the attacker's Siege effects, to a minimum of {{VAL:SIEGE_CALCULUS.Lay Siege.floor}} (no maximum). Every source below stacks — Wooden Walls (+{{VAL:SIEGE_SOURCE_VALUES.Wooden Walls.value}}) and Stone Walls (+{{VAL:SIEGE_SOURCE_VALUES.Stone Walls.value}}) both count.

{{TABLE:siege_calculus}}

### Beginning a Siege

1. End a Move action with your Army adjacent to another player's Settlement you're At War with.

2. Your Army must stay there for the Siege Timer and can't take other actions.

3. If you're attacked while sieging and you Fall Back, the Siege is broken and the Siege Timer is removed from play.

4. While a Settlement is besieged: it can't count Holdings toward Craft X; its Armies gain Blocked except to **Sally Forth**; Timers targeting the Settlement don't count down; and Industry actions can't target it.

### Resolving a Siege

When a Siege Timer reaches 0:

1. If you haven't negotiated yet, negotiate now.

2. If negotiation fails and there's an Army or Garrison inside, Battle in the Battle Phase.

3. If the besieging player wins, or there's no eligible Army or Garrison, choose one:
    - **Capture:**{{IDX:Capture}} set a Capture Timer {{VAL:TIMERS.Capture Timer.default}}. When it resolves, the Settlement comes under your Control — it receives your active Infrastructure effects, and you gain its Holdings, tax income, and Reach.
    - **Sack:**{{IDX:Sack}} Raze the top-most Holding of each Ward in the Settlement, Extort {{VAL:SACK_EXTORT_PER_TIER}} per Settlement tier; reduce the Settlement by 1 tier. Its controller removes all Holdings from one Settlement Ward of the sacking player's choice, then removes that Ward from play. Set a Sack Timer {{VAL:TIMERS.Sack Timer.default}} — you can't Lay Siege again until it resolves. Your Army gains Blocked and Strained until the Sack Timer resolves.

# Bandits

### Outlaw Country

Outlaw Country is zones of Territory no player can Control, where Bandit Camps spawn. Setup places zones in two ways; after Setup, every zone works the same.

- **Your zone (Deploy):** demarcate {{VAL:OUTLAW_COUNTRY_START}} Territories in your starting region, each within Range 1 of at least one other Outlaw Country Territory and at least Range {{VAL:OUTLAW_BUFFER_RANGE}} from any Settlement — the first exactly Range {{VAL:OUTLAW_BUFFER_RANGE}} from your Town, and none within Range {{VAL:OUTLAW_BUFFER_RANGE}} of your Hamlet. If that's not possible, place them Range 2 from your capital Settlement.
- **Wild zones (last Setup step):** the Host scatters more zones over the unclaimed board — the number of players ÷ {{VAL:WILD_OUTLAW.per_players}}, rounded down, + {{VAL:WILD_OUTLAW.plus}}. Each is {{VAL:OUTLAW_COUNTRY_START}} connected Territories, none on mountain or water Territory, at least Range {{VAL:WILD_OUTLAW.border_range}} from every player's Province and at least Range {{VAL:WILD_OUTLAW.spacing}} from every other Outlaw Country zone. Each Province starts the game with exactly one Outlaw Country zone.

A zone is your Outlaw Country while any of its Territories is within your Province. A zone in no player's Province belongs to no one: its camps spawn and grow, but take no action until they're within a player's Province; a camp that grows into a Bandit Army Marches like any other.

### Spawning Bandit Camps

In the Empire Phase each Spring: place a Bandit Camp of {{VAL:BANDIT_CAMP_START}} Bandits (Retinues) with {{VAL:BANDIT_CAMP_GOLD}} gold in each Outlaw Country zone.

*Note: if an Outlaw Country is chosen to receive another Bandit Camp but there's no room to place one, instead each existing Bandit Camp within that outlaw country grows according to the current Era. Foster Rebellion is the exception: it expands that Outlaw Country by one Territory and places the camp there.*

### Growing Bandit Camps

A Bandit Camp{{IDX:Bandit Camp}} grows each Empire Phase by the Era's Retinues per turn, and becomes a Bandit Army when it reaches {{VAL:BANDIT_ARMY_THRESHOLD}} Retinues. Its Retinues carry the Era's armament.

{{TABLE:bandits_by_era}}

### Bandit Rules

Bandits share the same Renown level as players. A Bandit's Domain value is set by the size of its Bandit Camp:

- {{VAL:BANDITS.Bandit Domain Value}}

All players are At War with all Bandits and their camps. Players abstain on all Bandit actions, but innate modifiers can still apply and cause the action to Fail.

While there are {{VAL:BANDIT_CUNNING_MIN}}+ Bandits (Retinues) in a camp, roll a d{{VAL:BANDIT_FACES}} each turn:

{{TABLE:bandit_cunning}}

A camp's action targets the Settlements and Armies of every player whose Province covers the camp, the nearest first. If the camp is in no player's Province, it takes no action.

A Bandit Camp keeps Extorted money in its Treasury and doesn't pay costs, upkeep, or recoup. When you destroy a Bandit Camp or Army, you extort its Treasury.

### Bandit Army Behavior

After Bandit Mechanics resolve, a Bandit Army performs a Move action based on, in order:

1. **Skirmish** — if another player's Army is in range.

2. **Lay Siege** — if another player's Settlement is in range.

3. **March** — toward the closest player's Army or Settlement.

*Note: if range ties, the Host chooses the target.*

### Attacking a Bandit Camp

Use the Move action to end adjacent to a Bandit Camp, then resolve it as a Battle in the Battle Phase. Another player rolls the Bandits' Tactic each Skirmish and makes their to-Strike and Save rolls:

{{TABLE:bandit_tactics}}

Extort the Bandit Camp's gold if it's destroyed. Bandits never Fall Back, but they may Rout as normal.

{{GLOSSARY:World}}

# Holdings

Holdings are listed by the Standing they require, Domain by Domain; Monuments are marked *(Monument)*. A Holding that requires two Standings appears under both.

{{TABLE:holdings}}

# Equipment

## Melee Weapons

{{TABLE:weapons}}

## Ranged Weapons

{{TABLE:ranged}}

## Shields

{{TABLE:shields}}

## Armor

{{TABLE:armor}}

{{GLOSSARY:Equipment Tiers}}

# Factions

{{TABLE:factions}}

# Index

{{INDEX}}
