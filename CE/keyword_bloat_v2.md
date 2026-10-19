# Keyword Bloat — v2

**Measure.** Printed terms per equipment row: Weapons + Ranged + Shields, from `renown_data_d10.py`.

| | Total terms | Items over 3 |
|---|---|---|
| Now | 110 | 15 |
| Layer 1 (exact, no rule change) | 66 | 4 |
| Layer 2 (+ two folds) | 59 | 3 |

**Method.** `references/keyword_audit.py` enumerates, exactly, the rules-as-written strike chain per strike die:
- Strike → Parry → Save → Recover, plus Cleave, Deadly, Unstoppable and Riposte.
- Run over 1,344 defender configurations, at each to-Strike value (3/4/5/6).
- Defender configuration = armor × shield × Parry none/8/7/6 × Riposte × Recover none/8/7/6 × Planishing.
- The engine's hidden ranged Deflect is excluded.

---

## Layer 1 — exact (110 → 66)

### 1a. Ranged category rule
Every Ranged weapon is Unstoppable and Awkward, so these move into one category rule (R1, unchanged from last pass).

### 1b. Inert tags — the audit finds no matchup where they change anything

| Item | Tag | Why it does nothing |
|---|---|---|
| All 6 Ranged | Negate Riposte | Riposte only answers a Melee Strike. 0% of matchups. |
| War Hammer | Destroy Shield | AP −10 already makes every Save impossible (best case: 4+ armor with +2 shield needs a natural 12), and it already Negates Shielded. 0% of strike-chain matchups. The only residue is that the target shield's Steady/Unwieldy is lost for the rest of the Battle. |

### 1c. Bundles — exact shorthand for tag sets that always travel together
Names are placeholders. The engine keeps the full tag list, expanded at import.

| Bundle | = | Items |
|---|---|---|
| Thrown | Steady, Deadly, Negate Shielded, Destroy Shield, One-Shot | Javelin, Pilum (identical tag sets) |
| Polearm | Steady, Unwieldy, Awkward | Pike, Cavalry Spear, Lance |
| Great | 2H, Unwieldy | Cudgel, Pitchfork, Halberd, Battle Axe, 2HBastard, War Hammer, Arquebus |
| Crushing | Unstoppable, Cleave | Flail, Battle Axe, 2HBastard, Poleaxe |

## Layer 2 — two folds with measured deltas (66 → 59)

| Change | Who it moves | Size |
|---|---|---|
| **Fold Negate Riposte into Unstoppable**: "Unstoppable: −2 to the defender's Parry roll; a Parry against it can't Riposte." | Flail, Battle Axe, 2HBastard and Poleaxe *gain* it. Cavalry Spear *loses* it (it isn't Unstoppable). The keyword is deleted. | At most 0.08 ripostes per die, and only against an army that has Riposte (Grand Tournament). |
| **Cut Negate Planishing** | Estoc, Poleaxe, Arquebus | Mean +0.007 / +0.010 / +0.013 casualties per die across the grid. Matters only against a Court Armoury army, and only where the weapon's AP pushes the Save beyond 10+. |

## Per item

| Item | Now | L1 | L2 | L2 terms |
|---|---|---|---|---|
| Farm Tools | 1 | 1 | 1 | Awkward |
| Cudgel | 3 | 2 | 2 | Great, Awkward |
| Pitchfork | 3 | 2 | 2 | Great, Awkward |
| Daggers | 2 | 2 | 2 | 2H, Deadly |
| Short Sword | 1 | 1 | 1 | Steady |
| Spears | 1 | 1 | 1 | Unwieldy |
| Arming Sword | 1 | 1 | 1 | Steady |
| Pike | 5 | 3 | 3 | Polearm, 2H, Deadly |
| Flail | 4 | 3 | 3 | Crushing, Unwieldy, Awkward |
| Halberd | 2 | 1 | 1 | Great |
| Battle Axe | 5 | 3 | 3 | Great, Crushing, Negate Shielded |
| Cavalry Spear | 4 | 2 | 1 | Polearm |
| Morningstar | 2 | 2 | 2 | Cleave, Destroy Shield |
| Bastard Sword | 1 | 1 | 1 | Steady |
| 2HBastard | 4 | 2 | 2 | Great, Crushing |
| War Hammer | 7 | 5 | 4 | Great, Deadly, Unstoppable, Negate Shielded |
| Lance | 7 | 5 | 4 | Polearm, Deadly, Unstoppable, Destroy Shield |
| Estoc | 5 | 5 | 3 | Steady, Deadly, Unstoppable |
| Poleaxe | 6 | 5 | 4 | Crushing, 2H, Steady, Negate Shielded |
| Hunting Bow | 4 | 1 | 1 | 2H |
| Longbow | 5 | 2 | 2 | 2H, Deadly |
| Javelin | 8 | 1 | 1 | Thrown |
| Crossbow | 6 | 3 | 3 | Unwieldy, Deadly, Negate Shielded |
| Pilum | 8 | 1 | 1 | Thrown |
| Arquebus | 7 | 3 | 2 | Great, Negate Shielded |
| Shields (4 with tags) | 2 each | 2 | 2 | unchanged |

## What's left

What remains is two whole subsystems, not individual keywords.

- **Parry interaction** — Awkward, Unstoppable, Negate Riposte. These only matter against an army that has gained Parry.
- **Shield interaction** — Shielded, Negate Shielded, Destroy Shield, Immune Destroy Shield.

Cutting either subsystem is the next lever. Its balance cost belongs to the tournament, not to this audit.

## Implementation (when approved)

Same mechanism as R1:
- `BUNDLES = {...}` in the data.
- Each row stores `own_tags`, which hold the bundle names, for display.
- `tags` is expanded at import, so the engine reads it unchanged.
- The six renderers switch to `rd.shown_tags(x)`.

Layer 2 also needs:
- Engine side: `UNSTOPPABLE` implies `NEGATE_RIPOSTE` at expansion.
- Data side: delete `NEGATE_TEMPERED` from the 3 rows.

`keyword_audit.py` re-runs the numbers after any change.
