# Holding Mechanics Audit

Scope: active `SIMPLE_NODES` in `renown_data_d10.py`, as read by `references/gen_settlement_board.py`, with runtime behavior checked in `references/board/js/`. This is an implementation inventory, not a balance or rules-text review.

## Confirmed gaps or partial implementations

| Holding | Text/mechanic | Current status |
|---|---|---|
| Baggage Train | At the Start of the Empire Phase, may perform a Move action | **Implemented in this pass:** the Empire Phase dock offers a Move for one of your unblocked Armies, then consumes the trigger after it moves. |
| Beacon Towers | At the Start of the Empire Phase, choose an Army in your Province and move it up to its modified Speed | **Implemented in this pass:** the dock offers eligible Armies in your Province through the normal modified-Speed map movement. The movement-triggered reaction remains implemented separately. |
| Courier Network | Once per turn, Authority −1 on Target Envoy | **Implemented in this pass:** during an Envoy vote, the holder can apply −1 before the first vote is cast. |
| Courier Network | Select a Personal Action performed this turn and perform it next turn in the Empire Phase; send one fewer Envoy next turn | **Implemented in this pass:** select a successfully performed Personal Envoy action to repeat next Empire Phase; selecting it also applies the parsed Envoy reduction. |
| Thieves' Guild | When another player performs a Cunning action, may recoup 1,000 gold | **Implemented in this pass:** creates a clickable claim for each qualifying action; the holder chooses whether to collect. The separate “half of Trade Income” effect remains implemented at Empire Phase. |
| Syndicate Hub | When a Bandit Camp in your Province Extorts, Extort half that amount from the camp | **Implemented in this pass:** on an Endorsed Bandit Extort, the Hub takes half of the amount from the camp treasury. |
| Black Market | React to another player’s Extort and Recoup, taking 200 per 1,000 (minimum 100) | **Implemented in this pass:** both reactions apply after the gold transfer/Recoup and are recorded in the Treasury ledger. |
| Forgery Workshop | Extort 300 whenever someone Opposes one of your Envoys | **Implemented in this pass:** the completed Envoy applies the Extort to each opposing player and records it in the ledger. |
| Forgery Workshop | On a failed Cunning Envoy, attempt another; if it passes or is endorsed, target a different player | **Implemented in this pass:** after a Failed Cunning Envoy, the holder can add one extra Cunning Envoy to the live queue. Its action must target a player, and it excludes the prior Cunning action target when one was recorded this phase. |
| Artillery Park | Settlements you besiege cannot Sally Forth | **Implemented in this pass:** the map now suppresses Sally Forth and guards the queue action when the besieger has active Artillery Park. Its Arquebus unlock, siege timer modifier, and wall-ignore effect were already parsed. |
| Senate Hall | Once per Envoy Phase, Condemn an at-war player’s chosen Envoy or Endorse an ally’s chosen Envoy before votes | **Implemented in this pass:** eligible holders can intervene before the first vote on a Personal Envoy; the Envoy resolves as Condemned or Endorsed. Faith +1 and Influence +1 per other player are handled. |
| Exalted Basilica | At the Start of the Empire Phase, may perform an Endorsed Spread Truth | **Implemented in this pass:** the Empire Phase dock runs Spread Truth as Endorsed, including its cost/recoup and Piety action riders. |
| Aristocratic Court | Each Empire Phase, Extort 1,000 from each non-allied player with a lower Treasury | **Implemented in this pass:** compares Treasuries at the start of the Extort resolution, then transfers up to 1,000 from each eligible non-ally. Its two Council votes were already parsed separately. |
| Studium Generale | May gain one Sovereign Domain effect without spending Domain Points | **Implemented in this pass:** each active Studium Generale can permanently select one Domain's Sovereign effect without changing Standing or spending a Domain Point. The selected effect is included in existing effect calculations while that Studium remains active. |
| Cipher Chamber | Each Empire Phase, choose a different Army from last turn and give it Blocked | **Implemented in this pass:** tracks last turn’s Army choice and applies the normal Blocked duration. |
| Cipher Chamber | Each Empire Phase, choose a different active Timer from last turn and increase it by 2 | **Implemented in this pass:** the dock lists active realm timers and board-local build/repair timers, and tracks the previous choice. |
| Whispering Undercroft | Before a Personal Envoy vote, require its sender to declare the specific action and target; enforce that declaration if the Envoy passes | **Implemented in this pass:** after Envoy declarations lock and before any votes, the holder can select a Personal Envoy or skip. Its sender must declare the action, target, and sub-action; a passing or endorsed Envoy resolves that locked choice. |
| Office of Works | Settlements and allied Armies inside them ignore “Settlements being Besieged” effects | **Implemented in this pass:** Army siege-blocking/status and Strained checks now honor the Office of Works on the Settlement controller, including when the Army is allied and inside their Settlement. |

## Already wired (examples checked during this pass)

- Senate Hall’s Faith and per-other-player Influence.
- Harbor’s “Extort N per player without X” at Empire Phase.
- Battery Park’s doubled Siege Timer countdown.
- Beacon Towers’ movement-triggered effects and its new Start of Empire Phase Army move.
- Outrider Intercept Post’s Tactic reveal behavior in the battle flow.
- Holding combat tags and unlocks routed through `holding_combat_tags` / `HOLDING_SIM`, including the battle-side tags handled by `50_battle.js`.
- Generic flat Faith, Doubt, Craft, Influence, upkeep, and gold atoms, plus several specialized Envoy, Extort, siege, and Public Order clauses.

## UI changes in this pass

- Moved the once-per controls to the top of the action dock, before vote responses and action prompts. Existing checkboxes and exchange buttons remain interactive.
- Added actionable Empire Phase controls for Baggage Train, Beacon Towers, Cipher Chamber, Exalted Basilica, Studium Generale's selected Sovereign effect, and deferred Courier Network actions.
- Added pre-vote controls for Courier Network, Senate Hall, and Whispering Undercroft; added Forgery Workshop's failed-Envoy retry and clickable Thieves’ Guild Recoup claims.
- Rebuilt `references/settlement_board.html` from the updated source.
- Added an ordered Empire Phase effect stack for active Domain Standing effects: endorsed Build, endorsed Charter, and Muster each get a selectable action form and resolve through the normal action rules, once per source each turn. Active Standings and automatic Faith/Doubt triggers are listed with their source; the Empire Phase log records the automatic source and amount.
- Existing automatic Standing calculations remain in place for Grand Vizier Influence, Divine Mandate Faith, One True Gospel Doubt, High Quartermaster upkeep/war modifiers, and Pillar of Faith's Public Order floor.

## Important limitation in the current tracker

The generic once-per/may list remains a tracker. Mechanics implemented here have separate action controls or resolution hooks; rows still marked as gaps or partial need their own workflows.

## Review note

This pass checks the active simple d10 holdings and the browser-board implementation. It does not certify every legacy/full-data node, every faction or Infrastructure effect, or the separate Python tournament engine. Runtime changes include Black Market Extort/Recoup reactions, Forgery Workshop opposition Extort and retry, Office of Works allied-Army protection, the newly implemented phase actions above, and related UI controls. The selected Studium effect activates the named Sovereign-tier mechanic but does not increase that Domain's Standing, vote cap, or innate Envoy Authority.
