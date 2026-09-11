# v3 Batched Engine — Status

## MAJOR FINDING (affects the REAL tournament, not just the batch)
`load_pool_from_csv` read a nonexistent "tags" column instead of "extra_tags", **silently
stripping ALL extra_tags** from every CSV-loaded loadout. Any tournament run from loadouts.csv
had Ministry/Outrider/Poison/Rend/Regenerate/Cond Field DISABLED. FIXED in loadouts.py;
loadouts.csv regenerated comma-separated. **Re-run any analysis that used the old CSV.**

## Batched engine — what works
`batch_engine.py`: resolves a BLOCK of matchups in one set of arrays, both modes, plus
run_tournament_batched (full round-robin → master matchups.csv w/ mode column). ~7-8x faster.

## Correctness — now noise-floor accurate EXCEPT one cross-term
Validated against the per-matchup engine. Noise floor (engine vs itself, diff seed):
corr 0.9939, mean_d +0.17. The batch now MATCHES this on:
- **Plain builds** (no tags): corr 0.9965, bias +0.21%
- **Non-Outrider pool** (all other tags active): corr 0.9961, bias +0.14%
- **Outrider-vs-Outrider**: corr 0.9974, bias -0.3%

Bugs found & fixed this session (in order):
1. **CSV tag-stripping** (above) — biggest, affects real tournaments.
2. **Seize the Initiative**: was always given to A; now the random 50/50 initiator split,
   per-slot, with innate-Ministry override (forces its holder to seize, single +1 not +2,
   denies opponent). Also fixed B-side Ministry losing its seize.
3. **Apothecary Heal**: was missing; added (heal 1/4 prev-skirmish casualties at skirmish
   start, capped at start size).
4. **Outrider counter-pick**: was unimplemented in the loop (thought inert, but the CSV fix
   activated it for 509 builds). Now wired in: when a side's Outrider fires, it plays the
   weapon-aware best-response (0.8 weight) to the opponent's revealed pick, matching the
   per-matchup engine's _counter_weights_from_table.

## REMAINING RESIDUAL (small, characterized)
Full mixed-pool bias (all tags active, multi-seed): **-1.5% ± 0.3, corr 0.988** vs a noise
floor of +0.04%, corr 0.9954. So a small STABLE ~1.5% residual remains above noise.

Component breakdown (each multi-seed verified):
- Plain / non-Outrider / Outrider-vs-Outrider pools: all at the noise floor (bias <0.3%,
  corr 0.996). These are correct.
- The residual lives ENTIRELY in the **Outrider-vs-non-Outrider cross term.** Multi-seed
  mean_d there is -0.15±0.11 (A=Outrider) and -0.44±0.70 (B=Outrider) — both noise-DOMINATED
  (std >= mean), but the high variance of Outrider counter-picking (outcomes concentrate on
  specific tactic pairs) drags the aggregate correlation from 0.995 to 0.988 and leaves a
  ~1.5% net lean. The Outrider counter TABLES and WEIGHTS are bit-identical to the reference
  (verified both A and B orientations); the residual is an RNG-consumption-ORDER artifact:
  the reference draws B-then-A (or A-then-B) conditional on who has Outrider, while the batch
  always draws A-then-B then overrides, so downstream strike/save dice land on different runs.
  Closing it fully would require restructuring the per-slot RNG flow to be conditional
  (complex, risky) for a <2% effect that is mostly variance, not bias.

## How to use it
- **Authoritative absolute win rates → per-matchup engine (vectorized_combat)** on the FIXED
  csv. Unaffected by any batch issue.
- **Fast relative iteration → batch.** Now accurate to the noise floor for everything except
  matchups pitting an Outrider build against a non-Outrider build, where the Outrider side
  reads a few % strong. Rankings/trends are reliable.

## Next step to close it
Match the reference's tactic-reveal order exactly: in the batch's Outrider branch, draw the
non-Outrider side's tactic, then sample the Outrider counter from THAT, without the extra
random draw for the Outrider side. Verify the cross-term bias drops to noise.

## Not handled
- Bastard Sword dual-profile mid-battle 2H switch (85 builds).
- Yew Heart first-skirmish ranged +1TH.

## Update — retinue matrices, MPC expansion, Outrider playstyle, confound filtering

- **Outrider playstyle** (playstyles.py): new NEVER_FB adaptive playstyle. `assign_default_playstyle`
  routes any `Outrider:` build to it. Isolates the monument's counter-pick value with no retreat
  behavior layered on. Re-measured monument delta (chassis fixed, tag toggled): +0.004 (first/once),
  +0.017 (first_two), +0.046 (every) — modest vs Royal Pavilion (+0.23) / Preceptory→KT (+0.18).
- **Shield-destroyed stat FIXED** (batch_engine.py): the rate was hardcoded 0.0 in both the parquet
  table builder and CSV writer ("not tracked yet"); the mechanic always fired in-sim. Now recorded
  per-run. Validated: Destroy-Shield weapon vs Wooden = 1.0, plain = 0.0, Immune (Heater) = 0.0.
- **Expanded pool loadouts_4_13.csv**: MPC [4,13], 5670 builds, all size 50. FULL pool is ~36+ hr/mode,
  so the notebook STRATIFIES (STRATIFY_PER_MPC, default 80 → ~800 builds, ~70 min/mode @50 runs),
  balanced across retinues within each MPC bucket.
- **analysis.py** new functions:
  - `retinue_matchup_matrices(df)` → dict of AxB retinue matrices (win rate, mutual-wipe, indecisive,
    avg_skirm, combat kills both sides, shake kills, rout kills, shield-destroyed, n).
  - `top_performers_by_mpc(summary, top_n, metric)` and `mpc_summary_table(summary)`.
  - `filter_confounds(df, drop_mutual_wipes, decisive_only, exclude_mirror_gear, same_mpc,
    mpc_tolerance, min_decisive_rate)` — controls the mutual-wipe / mirror-gear / unequal-MPC
    confounds. Decisive-only + mirror-excluded correctly puts Sergeant (0.63) above MaA (0.60).
- **Notebook**: config now points at loadouts_4_13.csv with STRATIFY_PER_MPC; sections 10/11/12 added
  (retinue matrices, per-MPC leaderboards, confound-reduced views). All cells verified headless.

## Note on the army-size question
Every build in the standard pool is size 50 (front line min(20,size)=20, reserves min(10,size-20)=10).
The engine supports other sizes (horde mode), but the round-robin pool is uniform 50.

## Fatigue / shaking / rout rewrite + new retinue stats (proposal implemented)

NEW RETINUE STATS (edit in renown_combat.RETINUES — both engines read from there):
  Levy 5+/5+/3 | Man-at-Arms 4+/5+/4 | Sergeant 4+/4+/4 | Knight Templar 3+/Unshakable/2 (+Steadfast)
  (format = to-hit / shaking / endurance)

NEW FATIGUE MODEL:
- Endurance drains 1/skirmish. When it hits 0 (and each exhausted skirmish after), a shaking test
  fires at the PRE-token target, THEN a fatigue token is gained (test-then-token, same skirmish).
- Each fatigue token = -1 to-hit (worsening, capped so target never exceeds 6+ from fatigue alone;
  other negatives applied AFTER the cap can push to 7+ auto-miss) AND -1 to shake (i.e. +1 to the
  shake target, UNCAPPED).
- ROUT: when the shake target is modified to 7+ (base shaking + fat >= 7), the test can't succeed →
  whole army flees (Destroyed). Steadfast prevents Rout; Unshakable never tests so never reaches 7+.
- Projected rout timeline (mirror, Defender): Levy R5 (2 tokens), MaA R6 (2), Sergeant R7 (3),
  KT never (Unshakable+Steadfast). Verified in both engines.

Implementation: vectorized_combat.py (per-matchup) + batch_engine.py (tournament) updated identically.
_shaking_test_vec / _shake_batch now accept a per-run shake target array (base+fat). To-hit 6+ cap
ordering unchanged (already correct: base+positive+fatigue clamped to 6, then negatives can reach 7+).
VALIDATED: numba==numpy exact; batch vs per-matchup engine mean bias -0.5% (sampling noise).
Balanced-pool retinue ladder under new rules: KT 0.773 > Sgt 0.513 > MaA 0.368 > Levy 0.020.

To iterate on retinue values: edit renown_combat.RETINUES, reload modules, re-run. No engine edits needed.

## Current tuned stats (saved) — retinue stats + min(10) shake volume

RETINUES (renown_combat.py — to-hit / shaking / endurance):
  Levy 4+/4+/2 | Man-at-Arms 3+/4+/3 | Sergeant 2+/3+/3 | Knight Templar 2+/Unshakable/2 (+Steadfast)

SHAKE VOLUME: shaken test rolls min(10, size) dice (was min(20, size)). Changed in BOTH engines:
  vectorized_combat.py ~L1336 (a_field/b_field), batch_engine.py ~L634 (a_fieldsz/b_fieldsz).
  Halving the shake dice cut morale bleed; deaths rebalanced toward combat.

RESULTING DEATH MIX (by troops, gear-matched balanced pool, MPC 5+ equilibrium):
  combat ~56% / shake ~31% / rout ~13%  (target was ~55/25/12 — on target).
  Per-retinue: Levy 43/35/22, MaA 50/36/14, Sgt 56/37/7, KT 100/0/0 (elites die fighting, Levy breaks).
  MPC sensitivity: low-MPC is combat-dominated (MPC1 ~75/20/5) because thin gear = short decisive
  fights; morale matters only once gear thickens (MPC5+ hits the target mix). Intended: early game
  = brawl, late game = attrition/nerve. Do NOT tune global average — tune the MPC band that matters.

DECISIVE LADDER (gear-matched): KT .75 > Sgt ~.50-.53 > MaA ~.40 > Levy ~.00. MaA↔Sgt is the
  close step (~.63 decisive) — keep it that way; Levy@5+ to-hit blows the MaA/Sgt gap open to .84, so
  Levy stays at 4+.

Rules context (from earlier this session): fatigue token = -1 to-hit (cap 6+) AND -1 shake (uncapped);
  shaken test at pre-token target the skirmish endurance hits 0, then token; rout when shake target
  modified to 7+; Steadfast exempts rout, Unshakable exempts shaken test (KT both). All in both engines.

## Shatter-pierces-parry A/B toggle (added, default OFF)

Flag: vectorized_combat.SHATTER_PIERCES_PARRY (single source of truth; batch reads vc.SHATTER_PIERCES_PARRY).
  False (default) = current rules: Parry can negate a shatter strike.
  True = a Shatter Armor strike (natural-6 to-hit; shatter == six_count) CANNOT be parried.
Wired into both engines (njit kernels + numpy fallbacks). numba==numpy exact in BOTH flag states.

A/B result (Shatter attacker vs Parry defender, per-matchup, attacker win-rate delta True-vs-False):
  Spears +18.5, Poleaxe +14.0, Pike +7.2, Bastard +6.8, Lance +5.5.
  Swing tracks reliance on shatter strikes: low-AP shatter weapons (Spears/Poleaxe) gain most;
  high-AP (Lance/Bastard) already pierce armor on normal hits so gain least. Targeted anti-Parry buff.
Batch verified on explicit Spears-vs-Parry pair: ATK 94/500 -> 181/500 when flag on.
Left as a toggle defaulting to current rules (option A) — not made permanent.

## HALF-SCALE game (pushed as new default)

Army halved: size 25, FRONT_CAP 10, RESERVE_CAP 5, SHAKE_CAP 5 (was 50/20/10/10).
- Constants live in vectorized_combat.py (FRONT_CAP/RESERVE_CAP/SHAKE_CAP); batch_engine reads vc.* .
- loadouts.DEFAULT_ARMY_SIZE = 25; CSV loader and both generators use it (existing size-50 CSVs are
  overridden to 25 on load). To revert to full scale: set caps 20/10/10 + DEFAULT_ARMY_SIZE 50.

Rationale: at 10 attack dice P(>=1 natural-6)=0.84 vs 0.97 at 20, so Destroy Shield / Shatter /
Cleave are no longer near-automatic each skirmish — they can whiff. Halves table footprint /
component count too.

A/B findings (broad random pool, full vs half):
- Death mix, decisiveness, mutual rate essentially unchanged in realistic (uneven) matchups.
- Casualty variance up only ~4% (CV .373->.387); kurtosis down slightly (-0.29 -> -0.40) — the
  higher per-roll variance only matters in near-mirror matchups, where the underdog gains a few
  points of upset chance (e.g. MaA-vs-Sgt .057->.087, Sgt-vs-KT .120->.171). Blowouts stay pinned.
- Retinue ladder fully preserved (KT > Sgt > MaA > Levy, same gaps).
- Runtime ~17% faster (battles clip low-yield tail skirmishes; fatigue/morale clock is fixed in
  skirmish-index while per-skirmish kill counts scale with army size).
- Half-scale death mix (broad pool): combat .675 / shake .247 / rout .078 — shake landed on the ~25%
  target (fewer shake dice = less morale bleed).
numba==numpy exact verified at half scale. Shatter-pierces-parry toggle still default OFF.

## Abbey MPC + Preceptory KT cost change

New pursuit "Abbey": cost 1, requires Piety 3, grants tag "Shake +1" (= +1 to the shaken die roll
= -1 to the effective shake target; a morale BUFF). Independent MPC AND a required prereq for
Preceptory KT. Preceptory KT cost dropped 2 -> 1.

Engine wiring (both engines): StaticArmy.shake_bonus reads "Shake +1" from extra_tags; per-run
shake target = shaking + fatigue - shake_bonus (floored naturally by the <=6 test / >=7 rout gates).
batch packs P["shake_bonus"], tiles + subtracts at the shake-target line. numba==numpy exact.
Validated: Sergeant w/ Shake+1 shake-deaths 3.90->2.84, mirror win rate .39->.54.

loadouts.py: Abbey in PURSUITS_INFO (Piety line); Preceptory KT prereqs now
[Preceptory, Hospitaller, Abbey] @ cost 1; valid_combo enforces Abbey for Preceptory KT; KT base
seed + has_full_precep include Abbey; Abbey added to INDEPENDENT_OPTIONS; TAG_DISPLAY "Shake+1".
NOTE: as an independent option Abbey attaches to ~40% of generated builds across ALL retinues
(morale buff not KT-exclusive). All KT builds now include Abbey (required). Tune generation
frequency if Abbey should be rarer / KT-adjacent.

## Data dicts + tactic matrix updated (latest paste) + balanced_validation_pool

DICTS (renown_combat.py) synced to latest: MaA shaking 3->4; Flail ap -2->-1; Battle Axe ap -5->-3
+Cleave+Unwieldy; Morningstar +Unwieldy+Shatter; War Hammer +Shatter; Longbow ap -3->-2 (drop Steady);
Hunting Bow/Pilum +Shatter; Cloth +Nimble; Leather +Steady. TACTIC_MATRIX replaced (49 entries).
numba==numpy exact, engine clean.

NEW GENERATOR: loadouts.balanced_validation_pool(mpc_min=4, mpc_max=13, per_cell=None, seed=2026,
  keep_shield_tier_rule=True). Large validation pool:
  - balanced per (retinue x MPC bucket); per_cell caps each cell (e.g. 25) for exact balance.
  - IGNORES retinue tier floors/caps (every retinue x every tier, like fullcross) for clean
    retinue comparison.
  - full legal weapon x armor x shield cross, tiers INDEPENDENT (Forged weapon + Cloth armor ok).
  - structural weapon rules enforced via valid_combo: 2H/no-shield, OneShot->Tiltyard,
    Lance/CavSpear no Tower, Crossbow Tower-only + no Lance/CavSpear.
  - TIER-CEILING VARIES INDEPENDENT OF MPC: each build's pursuit set encodes a smithing stop
    (Furnace/Blacksmith/Forge/ABF) + armor/metal stop, padded with filler pursuits to hit exact MPC.
    So at a given MPC you get both Wrought-capped (blacksmith-only) and Forged/Crafted builds.
  - keep_shield_tier_rule=True keeps shield-tier>=weapon-tier (fullcross precedent); set False to drop.
  Validated: per_cell=25 -> 993 builds, cells<=25, ~250/retinue, numba==numpy exact.

OPEN / FLAGGED:
  - High-MPC cells (11-13) slightly under-fill (fewer gear configs reach them via filler) — raise
    the FILLER list or lower per_cell if you need them packed.
  - Cast-tier weapons (Daggers/Short Sword/Spears) and pure-ranged are thin in the cross; can widen.
  - kept shield-tier>=weapon-tier; say if you want it dropped for more shield combos.

## CORRECTION: removed tier rules from balanced_validation_pool

ERROR FIXED: the pool was still applying tier rules Gage had said to remove. Two sources:
(1) keep_shield_tier_rule defaulted True (shield-tier>=weapon-tier — never a real generation rule,
only a temporary pool-deflation device); (2) it called valid_combo() which ALSO enforces retinue
tier floors, the Levy Wrought cap, and its own internal shield-tier check.

FIX: balanced_validation_pool now uses a new _structural_legal() helper that enforces ONLY the four
specified generation rules (2H/no-shield, OneShot->Tiltyard, Lance/CavSpear->no Tower/Wooden,
Crossbow->Tower-only + no Lance/CavSpear) — NO tier floors/caps, NO shield-tier rule.
keep_shield_tier_rule now defaults False.

EFFECT: pool grows to ~20,210 uncapped (every retinue x every tier x full legal gear cross). Every
1H weapon now spans all legal shields (Arming Sword gets Wooden/Kite, Short Sword exists, etc.). This
resolved the Cavalry Spear 63%-winrate confound: Cav Spear was the only Wrought 1H weapon allowed cheap
shields (others were tier-blocked); now all weapons are on equal footing.
20,210 builds = ~408M pairs (NOT runnable). Use per_cell: 40->1600 builds/~3M pairs, 60->2400/~6M.
numba==numpy exact, engine clean.

## Fixed-gauntlet power-level runner (gauntlet_run.py + .bat)

For "is each build over/underpowered" — replaces quadratic round-robin with LINEAR pool-vs-panel.
Tests EVERY build against one FIXED, (retinue x MPC)-balanced opponent panel, so every build gets a
comparable "win rate vs the field" number. 20,210 builds x 80 panel = ~1.6M matchups (~12 min) vs the
408M-pair round-robin that's unrunnable. Output gauntlet_power.csv (one row/build: win_rate, decisive,
death mix, survivors, MPC, gear) + gauntlet_panel.csv (the fixed panel). Smoke test: 1600 builds x 60
panel in 73s; KT tops at .99, Levy/Farm-Tools at 0.0, Cavalry Spear correctly mid-pack (detier fix held).
Run: python gauntlet_run.py --balanced --per-cell none --gauntlet 80 --runs 60  (or gauntlet_run.bat).

## Tactic matrix evaluator (tactic_eval.py)

Forces every (a_tactic, b_tactic) in the 6x6 non-Fall-Back grid for 4 representative statlines (Levy/
MaA/Sgt/KT, same gear so the tactic effect is isolated). Per cell: a_win_rate, casualty diff, decisive
rate, survivors + DETERMINISTIC mechanical mods read from TACTIC_MATRIX (a_I/b_I + init_adv = who strikes
first, a_TH/b_TH = who hits harder, a_TS/b_TS = who saves better). Flags A's best-response per defender
column. Output tactic_eval.csv. Fall Back excluded (mostly end=True, a disengage mechanic — analyze
separately). Run: python tactic_eval.py --runs 400.

FINDING (first run): Defensive Formation is globally dominant as the A tactic across ALL statlines
(avg win 0.84-0.95, strongest row for every statline), Charge is weakest (0.24-0.30). Spread 0.58-0.71
= the tactic layer is NOT balanced; Defensive Formation is close to a dominant strategy. Flank/Flank =
NaN (no_combat mirror). Worth review before final tactic card balance.

## Tactic-pruning eval (tactic_pruning.py) + one-sided force in batch_engine

batch_engine: mode="forced" now accepts force_a/force_b = -1 = that side plays RANDOM mix (uniform
over 6 non-FB). Enables "tactic X into the field" (force A, B random).

tactic_pruning.py: for each gear archetype, force A's tactic across all 7, B plays random mix, vs a
(retinue x MPC)-balanced panel. Reports per archetype: ranking, LIVE set (within --live-band of top),
DEAD set (>--dead-band below top). Runs hand-picked archetypes + pool-derived KMeans clusters.

FINDING (first run): the live/dead split is NOT differentiating much by archetype. Across almost every
archetype the LIVE set is {Ambush, Flank, Defensive Formation} and DEAD is {Charge, Fall Back}, with
Fighting Formation borderline. The intended "Unwieldy kills Scout" pruning did NOT appear — Scout ranks
similarly mid/low for everyone, and the init-light builds didn't elevate Scout/init tactics as hoped.
This suggests tactic value is currently driven by the TACTIC-MATRIX mods, NOT by gear interactions —
i.e. equipment is NOT yet narrowing the tactic choice. The matrix dominates; gear is a second-order
effect. Design implication: if gear should prune tactics (Unwieldy->no Scout), that coupling needs to
be MADE (e.g. Unwieldy zeroes Scout's init benefit in-engine), because it isn't emergent yet.

## tactic_pruning.py rebuilt: marginal-edge metric + Unwieldy coupling diagnostic

CORRECTION to prior finding: the Unwieldy->Scout coupling IS implemented (batch_engine lines 1080-92:
Unwieldy zeros positive I-mods, Steady zeros negative; verified Scout-edge -0.135 Unwieldy vs +0.192
non-Unwieldy in a direct test). The earlier "coupling isn't wired in" conclusion was WRONG — the field-
average eval was too coarse and my Unwieldy archetypes (War Hammer/Battle Axe init -1) were already
init-floored, confounding the variable.

Rebuilt eval uses edge = win_into_field(tactic) - archetype_mean (removes base power, isolates relative
tactic preference) + a direct coupling diagnostic toggling Unwieldy via Immune Unwieldy injection.

FINDING: coupling delta is small but correct-signed (Lance +0.033, Cav Spear +0.009 Scout-edge gain
when Unwieldy removed). The coupling WORKS but is WEAK at the margin because Scout's +1I is only one of
several drivers and the init ceiling/floor + tactic-matrix mods dominate. The marginal-edge profiles are
still nearly UNIFORM across archetypes (LIVE almost always {Scout,Ambush,Flank,DefForm}, DEAD {Charge,
FallBack}) — i.e. gear does NOT yet meaningfully reshape the live tactic set. The matrix still dominates
tactic value; the init coupling exists but is too small to prune differently by build. To get real
gear-driven pruning, the gear->tactic interactions would need to be STRONGER (bigger init swings, or
gear that gates/boosts specific tactics beyond just init).

## tactic_init_threshold.py — threshold-conditioned init coupling

Confirms Gage's model: tactic init mods are two-sided (A +I, B -I); gear cancels directionally
(Unwieldy zeros your +I, Steady zeros your -I); init only changes the OUTCOME when it flips strike
order (a_init>b_init). Partitions matchups by init-DECISIVE (a +/-1 swing flips strike order) vs
IRRELEVANT, measures Scout win-into-field per partition + Unwieldy toggle within decisive subset.

FINDING: the coupling is REAL and LARGE where it bites — Unwieldy toggle within init-decisive opponents:
LANCE Scout wr ON 0.483 -> OFF 0.611 (delta +0.128); Cav Spear +0.041. The field-average buried this
because most matchups are init-IRRELEVANT (one side dominates init regardless), so the coupling does
nothing there and washes the mean toward zero. So gear DOES narrow tactic choice, but only in the subset
of matchups where init sits on the strike-order boundary. Design lever: to make gear prune tactics more
broadly, init must cross the strike-order threshold in MORE matchups (compress base-init spread, or make
strike-order matter beyond a binary first/second). Verified analytically (StaticArmy.base_init) + sim.

## MEMORY FIX: bounded submission window in run_mode_batched

ROOT CAUSE of the 22.5M-row OOM at 97%: the ProcessPoolExecutor branch submitted ALL ~1100 blocks
up front (for bstart in block_starts: ex.submit). That queued every block's input `pairs` list +
buffered completed futures in memory simultaneously — unbounded, growing the whole run. The 1.24 MiB
allocation that failed was just the straw; the machine was already at its ceiling.

FIX: bounded window — keep at most 2x n_workers blocks in flight, submit a new block each time one
completes (wait FIRST_COMPLETED + backfill). Memory now constant regardless of run length. Output is
bit-identical to serial (block seeds are position-keyed, verified summary match). Matchups were ALREADY
streamed (ParquetWriter, one row group/block) so output was never the problem — it was the input queue.

Also: run main + playstyle SEPARATELY (run_tournament --no-playstyle, then a second run) so the first
run's memory + OS file cache fully releases before the second. And the gauntlet (gauntlet_run.py) avoids
the whole 22.5M round-robin for per-build power: 1.6M matchups, ~12min.

## NOT a bug: A/B symmetry confirmed + domain_count fix

The "~0.44 everywhere" (MPC diagonal, domain mirror, vs-same-MPC line) was NOT an attacker/defender
bias. Verified: identical-build clone fight over 4000 runs = A decisive win rate 0.500 (1543 vs 1544).
The engine is symmetric. The 0.44 is the MUTUAL-WIPE rate (~23% in mirrors) deflating win-rate metrics
that divide by all-outcomes instead of decisive-only. So all relative comparisons this session are sound;
absolute "win rate" reads ~0.39-0.44 in even matchups purely because ~1/4 of fights are mutual kills.
(Design note: 23% mutual wipe in mirrors is high — worth deciding if intended.)

REAL fix shipped: balanced_validation_pool hardcoded domain_count=0 (the flat domain-count chart). Now
derives it from compute_pursuit_cost's domain dict: domain_count = sum(domain.values()). Verified range
3-36, tracks MPC (MPC4 mean 8, MPC13 mean 28). NOTE: validation pool ignores the domain<=26 cap that
archetype_pool enforces, so it can exceed 30 — by design (unconstrained full cross); add a filter if a
30 cap is wanted.

STILL OPEN: MPC saturation past ~6 (combat return on MPC dies after MPC6; cross-MPC matrix confirms 13
vs 6 is ~coinflip). Decide whether high-MPC purchases should buy combat power or are non-combat value.

## total_investment metric (analysis.py) — better win-rate predictor than MPC

Gage's insight: MPC counts military pursuit SLOTS but gives a 0-cost discount for extending an
efficiency line (Blacksmith->Forge->ABF = 1 MPC), so a Crafted-tier weapon (e.g. Poleaxe, needs ABF)
appears at MPC 4 while actually sitting on 6 stood-up pursuits. That decouples MPC from real
investment and flattens the MPC<->winrate correlation. Confirmed: a 4-MPC Poleaxe build has pursuit
set {ABF, Apothecary, Blacksmith, Cipher Chamber, Coliseum, Forge} = 6 pursuits charged as 4 MPC.

FIX: total_investment = len(pursuits) — every pursuit counts 1, no efficiency discount. Added to
per_build_metrics (derived from the "|"-joined a_pursuits string, zero engine changes / no re-run
needed). New investment_vs_winrate(df) returns Pearson+Spearman for MPC vs total_investment plus
per-count win-rate tables.

RESULT (150-build sample): total_investment Pearson r=+0.281 (p=5e-4) vs MPC r=+0.192 (p=1.9e-2) — a
~46% stronger correlation, and it keeps discriminating at the top (inv 14->0.59, 17->0.62) where MPC
plateaus flat past 6. Confirms the hypothesis. Caveat: still only +0.28, so quantity-of-investment is
a real but minority driver — build QUALITY (what you buy) still dominates. Re-run on the full pool for
the stable number; direction (investment > MPC) is clear.

## MW Weapons -> Rend (-1 AP mechanic retired) + ABF chain fix + Outrider filler fix

THREE coupled changes this pass:
1. ABF (Crafted unlock) prereqs corrected to [Stable, Blacksmith, Master Workshop, Gilded Foundry]
   (was [Stable, MWRend, Gilded Foundry]).
2. -1 AP "MW Weapons" mechanic RETIRED entirely. MW Weapons now == Rend everywhere. Master Workshop
   and ABF grant Rend; the mw_bonus -1 AP code in vectorized_combat is removed (mw_bonus=0). MWRend
   retired as a duplicate of Master Workshop (alias kept so old pools load; not generated). All combo/
   monument tuples + analysis tag list updated MW Weapons -> Rend. Verified: no MW Weapons tag in pool,
   Crafted weapon AP == raw (no -1), Rend adds no AP (only worsens enemy Regenerate).
3. Outrider chain (Cipher Chamber, Caravanery, Outrider Intercept Post, Outrider Mastery) REMOVED from
   FILLER — only built when deliberately building the Outrider, never as MPC padding. Verified 0 stray.

BALANCE IMPACT: Crafted-tier weapons changed from -1 AP to Rend — different effect entirely. All prior
weapon findings (Poleaxe/Lance/Pilum dominance) were measured under -1 AP and MUST be re-run. Rend only
matters vs Regenerate builds, so Crafted weapons are now situationally strong rather than flatly +AP —
likely LOWERS Crafted weapon win rates broadly. Re-run weapon analysis + investment_vs_winrate.

Also shipped earlier this pass: analysis.total_investment (every pursuit=1, no efficiency discount) +
investment_vs_winrate() — total investment correlates better with win rate than MPC (Pearson .28 vs .19)
because MPC's 0-cost line-extension discount lets top-tier gear appear at low MPC.

## Conditional filler rules (Option B: filler = realistic spend, but gated)

- War College REMOVED from filler — its only effect is the Sergeant unlock; as filler it converted
  random builds to Sergeant (skewed pool 3x Sergeant). Now appears only on deliberate Sgt/KT builds.
- Ministry REMOVED from filler — requires War College prereq (broken without it) + grants Seize/MaxInit3.
- Hospitaller REMOVED from filler — does nothing without a regen stack; only a Preceptory KT prereq.
- Preceptory KT override: forces retinue -> Knight Templar (and its Hospitaller prereq is exempt from
  any regen requirement — KT path doesn't need regen, deliberately, to measure the inefficiency).
- REMAINING intended filler (Option B realistic spend): Apothecary (Heal, 37%), Coliseum (Cond Field,
  87%), Master Workshop (Rend, 37%), Stable, Butchery, Smokehouse. Retinue dist now even (~3200 each).
  Pool 12,812 builds.

WATCH: Coliseum/Cond Field on 87% = near-universal (not a differentiator). Apothecary Heal + Master
Workshop Rend on 37% each ARE combat-power filler that varies build-to-build — prime suspects if the
MPC/total-investment<->winrate correlation stays weak. Kept by design (Option B), flagged for re-check.

## Shield building rules rewritten + regen tier axis added

SHIELD BUILDINGS (replaces old metal-line mapping): Wooden=Joinery | Kite=Joinery+Blacksmith |
Scutum=Joinery+Blacksmith+Armory | Tower=Joinery+Blacksmith+Forge | Heater=Joinery+Blacksmith+ABF.
Joinery now also pulls Carpentry (prereq). Shields no longer touch the armor metal line, which FIXED
the Gilded Foundry leak (was on Cloth+Tower etc.) — GF is now ARMOR-ONLY (Full Plate/Gothic). Verified:
all 4 rules hold — Wrought weapon never pulls Forge on its own (only Tower/Heater shield or Forged+
ranged); shields always have Joinery; Fletchery/Tiltyard only with a ranged weapon; GF only on Full Plate.

REGEN TIER AXIS: every gear config now crossed against 4 regen tiers (none / Apothecary /
Apothecary+Infirmary / Apothecary+Infirmary+Hospitaller), making regen a deliberate build dimension
instead of random filler. Tags escalate: Heal -> +Regenerate5 -> +Regenerate Reroll. Apothecary removed
from FILLER (now a regen-tier pursuit). Hospitaller appears ONLY in the full-stack tier (all have Regen
Reroll). Pool ~44k builds uncapped (4x from the axis) — USE per_cell for round-robin; gauntlet fine.
Retinue + regen-tier distributions both balanced (~11k each / ~11k per tier).

## Loadout validator + prereq closure enforcement (validity gate)

NEW: validate_loadout(ld) + validate_pool(pool) — a single gate checking every rule (structural gear,
building requirements per tier, efficiency rules, prereqs, optional tier floors). Run after any pool gen
to catch construction bugs automatically instead of by eye.

DECISION: generators must include the FULL prereq chain (not the efficiency shortcut). Added
prereq_closure(pursuits) = transitive closure of all prereqs; balanced_validation_pool now runs base_set
AND final pursuit_set through it. So high-tier gear physically carries its whole chain (a Crafted Poleaxe
= 9 buildings: Blacksmith/Forge/ABF + Master Workshop/Gilded Foundry/Armory/Tannery/Animal Husbandry/
Stable). MPC stays low (cost discount), but total_investment now reflects true cost — exposing the
"Poleaxe at MPC 4 but 9 buildings" cheapness directly.

BUGS the validator caught + fixed:
  1. Forge declared no prereqs but efficiency-map treats it as Blacksmith's child -> added Blacksmith
     as Forge's prereq (closure now pulls the smith line).
  2. METAL_PATHS["ABF"] (Gothic Plate, Crafted armor) OMITTED ABF itself — Gothic + low-tier weapon
     ended up without ABF. Added ABF to the path.
  3. Validator GF rule was too strict (flagged GF when it's a legit ABF prereq) -> allow GF if ABF present.
Result: balanced pool now 0 invalid / 45,814 builds. Retinue + regen tiers balanced. numba==numpy exact.

## PURSUITS_INFO rebuilt from specs.csv (innate/mastery model) — MAJOR

Rebuilt the pursuit catalog from the authoritative specs.csv as source of truth. Combat-relevant
specs only (~31 + 8 minimal economic entries). Structure per spec: prereqs (from Mastery Requirement
col), domain (from Unlock-Requirement STANDING: Rising 3 / Established 6 / Sovereign 10), innate_tags,
mastery_tags, mastery_req, efficient (Efficient-X target), upkeep.

KEY MECHANICS (all confirmed by Gage):
- INNATE vs MASTERY: innate_tags granted when spec present; mastery_tags granted only when the spec's
  mastery_req pursuits are all present (LOCAL gate, not transitive). Mastery without innate impossible.
- MPC vs TOTAL_INVESTMENT: MPC = pursuit count − each satisfied "Efficient X" (a spec's mastery makes
  its efficient-target cost 0 space). total_investment = raw pursuit count (Efficient-X does NOT reduce).
  Verified: Poleaxe build MPC 6 vs total_investment 10 (4 Efficient-X discounts) — the two diverge as
  designed, so total_investment is the honest action-economy predictor.
- Efficiency DIRECTION corrected: higher building discounts the prereq (Forge mastery → Efficient
  Blacksmith), opposite of the old hardcoded EFFICIENCY_PARENT. Replaced that map entirely.
- CLOSURE: prereq_closure adds only COMBAT-relevant prereqs (stops at economic boundary; doesn't pull
  Mine/Courtyard). master_effect_closure pulls the DIRECT mastery_req (one level, incl. economic like
  Herb Garden) for EFFECT-BEARING specs so their mastery tag fires. Minimal entries added for the
  economic mastery-req specs (Herb Garden, Alchemy, University, Grand Tournament, Academy, Monastery,
  Pilgrimage Site) so they count toward MPC + total_investment.
- RETINUE UNLOCK = the spec's MASTERY (Muster): MaA needs Coliseum mastered (→Conditioning Field),
  Sgt needs War College mastered (→Levy Hall+Academy), KT needs Preceptory mastered (→Monastery+
  Pilgrimage Site+Hospitaller+Abbey). Every non-Levy build carries its unlock chain. KT is correctly
  RARE at low MPC (309 builds) — a Sovereign-Piety monument is genuinely that expensive. ACCEPTED.
- Preceptory/Preceptory KT two-spec hack REPLACED by single Preceptory (Steadfast innate, KT mastery).
  MWRend, Ministry Mastery, Outrider split folded into innate/mastery on single specs.
- Master Workshop mastery = Rend (CSV now agrees). Conditioning Field mastery = Cond Field/+1 Max End
  (corrected — was wrongly on Coliseum). Upkeep −5→−200, −10→−500, stacking.

Pool: 27,339 builds, 0 invalid, numba==numpy exact. Retinue dist Levy 11181 / MaA 9275 / Sgt 6574 /
KT 309 (KT thin by design). Regen tiers 0/1/2/3 = 10420/7388/5532/3999.

NOTE: domain standings (Rising/Established/Sovereign) live in PURSUITS_INFO domain dicts and feed
domain_count. Re-run weapon/retinue analysis + investment_vs_winrate under this corrected model — all
prior numbers are stale (cost structure, masteries, retinue costs all changed).

## Unshakable/Steadfast rework + rout-at-7+ fix (mechanic correction)

Per Gage: Unshakable = skip the shaking TEST (no shake casualties) but STILL ROUT once shake target
is modified to 7+. Steadfast = the true rout-immunity. Previously the engine wrongly exempted
Unshakable from rout too ("never tests so never reaches 7+") — but fatigue tokens raise the shake
TARGET independent of testing, so Unshakable units DO reach 7+ and must rout.

Changes:
- vectorized_combat + batch_engine ROUT condition: dropped the `& ~unshakable` exemption. Rout now
  fires at shake-target 7+ for everyone EXCEPT Steadfast. (Fatigue accrual + shake-target growth were
  already independent of the test, so no other change needed.)
- KT retinue: removed `steadfast: True` (kept `unshakable: True`). KT can now rout at 7+.
- Preceptory innate: Steadfast → Unshakable. So KT's morale identity = Unshakable (test-immune, rout
  at 7+), sourced from both the retinue flag and Preceptory.
- Steadfast is now UNSOURCED in the pool (no spec grants it) — remains in the engine as a mechanic.
- playstyle assignment unaffected (KT branch keys on retinue name, not the Steadfast tag).

VERIFIED: Unshakable KT mirror now ends 3000/3000 mutual ROUT (was endless indecisive before) — both
accrue 7 fatigue tokens then rout. validate_pool 0 invalid, numba==numpy exact. This likely REDUCES
KT's dominance and the mutual-wipe/indecisive rates — RE-RUN all analysis.

## FIX: mastery_req is flat presence (no prereq cascade) — KT cost corrected

BUG: the generator ran prereq_closure + master_effect_closure over retinue-unlock mastery_req
pursuits, so Preceptory's mastery_req (Monastery+Pilgrimage+Hospitaller+Abbey) dragged in
Hospitaller's prereqs (Apothecary+Infirmary) and THEIR mastery-reqs (Herb Garden+Alchemy) — a 9-spec
cascade. KT's cheapest build was wrongly MPC 8 and KT+Crafted (MPC 14) exceeded the ceiling, so KT
could never field a Poleaxe.

RULE (Gage): to MASTER a spec you only need the pursuits in its mastery_req column PRESENT. They do
NOT need to be mastered and do NOT pull their own prereq chains. A pursuit (e.g. Hospitaller) can exist
solely to satisfy a mastery gate — inert (no regen) but valid.

FIX:
- Retinue-unlock mastery_req pursuits added FLAT (no closure, no master_effect cascade). Gear+regen
  still get full prereq_closure + master_effect_closure (real build-first tier chains).
- Validator: a pursuit present to satisfy a present spec's mastery_req is exempt from its own prereq
  check (may be inert). Gear-tier validity still enforced via SMITH_REQ/METAL_REQ building checks +
  prereq checks on non-exempt specs — verified a deliberate Poleaxe-without-ABF build still flags.

RESULT: cheapest KT now MPC 5 (Preceptory+Monastery+Pilgrimage+Hospitaller+Abbey, flat). KT 1897 builds
(was 309), MPC 5-13. KT+Poleaxe(Crafted) now exists (15 builds). Pool 28,932, 0 invalid, numba==numpy
exact. Regen tiers balanced. RE-RUN analysis — KT cost/availability changed substantially again.

## FIX: unique-monument matchup guard (was stale after rebuild)

The guard that prevents two builds sharing a one-per-game MONUMENT from fighting (you can't have two
of the same unique monument in a game) had drifted. UNIQUE_BUILDINGS listed "Ministry" (renamed to
"Ministry of Military Strategy" in the rebuild → no longer matched) and was MISSING "Cipher Chamber".
In practice only ABF + Preceptory were firing (the others aren't generated in the validation pool), so
effective behavior was OK — but the list was wrong.

Rebuilt from the CSV's authoritative Type=="Monument" specs (combat-relevant 6), using PURSUITS_INFO
keys: ABF, Royal Pavilion, Preceptory, Ministry of Military Strategy, Outrider Intercept Post,
Cipher Chamber. Confirmed run_mode_batched (the notebook's runner) applies _unique_conflict, so the fix
is live. Verified: two ABF builds blocked, two Preceptory(KT) blocked, ABF-vs-non-monument allowed,
~9% of pairs skipped for shared monument.

## FIX: OOM at high n_runs — adaptive block_size (memory bounded by slot count, not pair count)

Gage hit MemoryError on a 2295-build pool (5M pairs) at n_runs=50, 14 workers — failed allocating a
tiny 19 MiB array, meaning RAM was already exhausted. ROOT CAUSE: block_size was a fixed PAIR count
(20000), but each block allocates arrays of N = block_size * n_runs rows. At n_runs=50 that's 1,000,000
slots/block, and with ~2*n_workers (28) blocks in flight × dozens of N-length arrays, peak memory blew
past 32GB. Memory scaled with n_runs because block_size didn't account for it.

FIX (both run_mode_batched + run_tournament_batched): block_size now DERIVED from slot_budget
(default 300,000): block_size = slot_budget // n_runs. So N per block ≈ 300K regardless of n_runs
(n_runs=50 → 6000 pairs/block; n_runs=100 → 3000). Peak memory now constant. Verbose prints the chosen
block_size + slots/block. Pass block_size= or slot_budget= to override. Verified: the failing config
(n_runs=50) now runs without OOM. NOTE: per-block seed = base_seed + pair_offset, so changing block_size
changes exact dice (not bit-identical to a 20000-block run) but aggregates are statistically identical —
each pair still gets n_runs deterministic battles. If lower memory needed, drop slot_budget (e.g. 150000).

## Auto-sizing slot_budget (memory-aware, tunable) + SLOT_BUDGET knob

Added auto_slot_budget(n_workers) in batch_engine: detects free RAM (psutil if available, else 8GB
fallback) and picks the largest per-block slot budget keeping peak ≈ free*0.55/(220 bytes/slot *
2*n_workers), clamped [80k, 1.2M]. run_mode_batched now AUTO-SIZES when slot_budget=None (new default):
  - 16-24GB free, 14 workers -> hits 1.2M cap -> block_size ~24,000 pairs, est peak ~6.9 GB (full speed)
  - 8GB free -> block_size ~15,000, ~4.4 GB
  - 4GB free -> block_size ~7,700, ~2.2 GB
So a roomy machine runs at full original speed; a constrained one shrinks automatically. The 1.2M cap
prevents the old unbounded OOM. psutil-missing falls back safely (no crash).

Wired through: run_tournament.py gets --slot-budget (default "auto"; or an integer). run_tournament.bat
gets an editable SLOT_BUDGET line ("auto" default; lower e.g. 150000 if RAM-tight, raise e.g. 500000+
for speed). Verbose now prints chosen block_size + estimated peak GB. Passed to BOTH main and playstyle
tournament calls. Verified runs complete without OOM; numba==numpy exact unaffected (block math unchanged).

RUNTIME NOTE for Gage: smaller blocks add ~5-15% overhead (more dispatch/merge cycles), NOT a 3x hit —
the vectorized math dominates. On 32GB the auto-sizer picks ~24k blocks (the old fast size) so you lose
almost nothing while staying crash-safe. Bump SLOT_BUDGET only if you want to push block size past the
1.2M-slot cap.

## Generator restructure: Retinue Unlock >= Retinue Upgrade > Gear > Filler

Added a RETINUE UPGRADE category so all combat monuments/upgrades appear in the data (they were
invisible before — never generated). New build flow per gear config:
1. RETINUE UNLOCK (mandatory): Coliseum->MaA, War College->Sgt, Preceptory->KT (KT always masters it).
2. RETINUE UPGRADE (<=1 per build): {Conditioning Field, Royal Pavilion, Ministry, Outrider, Preceptory}.
   Conditioning Field chosen >=2/3 of the time (broadly useful endurance). Preceptory here = NON-KT
   innate-Unshakable case (so the innate-vs-mastery jump is measurable on non-KT). Tiltyard is NOT an
   upgrade — it's ranged+melee dual-equip only (gear path).
3. GEAR: weapon/armor/shield chains.
4. FILLER (lowest): Master Workshop, Toxicarium, Stable, Butchery, Smokehouse + regen as a PARTIAL
   ladder (Apothecary->Infirmary->Hospitaller, climbed only as far as MPC allows). Coliseum removed
   (it's a retinue unlock). Filler added incrementally with live cost-checking so partial regen tiers
   land on exact MPC.

MONUMENT INNATE-vs-MASTERY: 1/3 of builds containing a monument {Royal Pavilion, Ministry, Outrider,
Preceptory} are INNATE-ONLY (skip mastery_req -> only innate tag fires) to expose the value jump from
standalone to mastered. ABF excluded (innate does nothing). Innate-only = DOMAIN requirement only, NO
building prereqs (validator exempts innate-only monuments + present-for-mastery pursuits from prereq
checks). Conditioning Field is NOT a monument -> always masters (grants Cond Field).

Royal Pavilion's mastery_req includes Tiltyard, so mastered-RP melee builds legitimately carry Tiltyard
(validator allows Tiltyard/Fletchery without ranged when Royal Pavilion present).

VERIFIED: pool 33,430 builds, 0 invalid, numba==numpy exact. All monuments now in data with healthy
innate/mastery samples (RP 0.40, Ministry 0.48, Outrider 0.51 innate-only). Regen partial tiers all
present. RE-RUN analysis — the pool composition changed substantially; Royal Pavilion, Ministry,
Outrider, Toxicarium now appear in the pursuit-effect table.

## FIX #2: OOM recurred — psutil missing → over-sized fallback. Now conservative.

Gage OOM'd again: auto-sizer picked slot_budget=766958 (the old 8GB fallback) because PSUTIL IS NOT
INSTALLED on his Windows Python, so it couldn't read free RAM and assumed 8GB → 767K slots/block × 28
in-flight = 4.4GB est (real footprint higher) → MemoryError.

Hardened auto_slot_budget:
- bytes_per_slot 220 → 700 (realistic PEAK: ~52 N-row arrays + (N,20)/(N,max_strikes) 2D buffers +
  transient _roll_strikes_batch peaks; 220 was far too optimistic).
- psutil-missing fallback 8GB → 3GB (SAFE small assumption — under-size beats OOM).
- safety 0.55 → 0.45, cap 1.2M → 300K, floor 80k → 40k. Returns (budget, have_psutil).
- run_mode_batched prints a ⚠ when psutil is missing, telling Gage to `pip install psutil` or set
  SLOT_BUDGET manually.

New behavior: psutil-missing @ 14 workers → budget 73,956 → est peak 1.3 GB (was 4.4). WITH psutil:
1.8GB (4GB free) → 5.5GB cap (16GB+ free). The 300K cap prevents runaway allocation either way.

DEFINITIVE FIX for Gage: `pip install psutil` enables accurate sizing. Otherwise SLOT_BUDGET=auto now
stays safely small; bump SLOT_BUDGET (e.g. 200000) in the .bat once psutil is installed for full speed.

## NEW: domain-standing → combat tags (Parry, Immune Blocked, opponent Blocked/Strain)

Wired domain STANDINGS to confer combat tags (standings: Rising=3, Established=6, Sovereign=10).
Previously no domain→tag mapping existed, so Parry/Blocked/Strain were dead (the old "Parry correlates"
result in the lab came from the retired archetype_pool COMBO_TAGS, NOT the pursuit model — stale).

In compute_pursuit_cost (loadouts.py), from a build's domain totals:
  - Rising Prowess (>=3)     -> self gains "Immune Blocked"
  - Established Prowess (>=6) -> self gains "Parry"
  - Established Cunning (>=6) -> "confers:Blocked"  (marker — debuffs the OPPONENT)
  - Sovereign Cunning (>=10)  -> "confers:Strain"   (marker — debuffs the OPPONENT)

Opponent debuffs (confers:*) are applied at matchup setup in run_matchup_vec (vectorized_combat.py):
strips confers:X from a side's own tags and adds X to the OPPONENT's extra_tags before StaticArmy is
built. So A's Established Cunning gives B "Blocked" (-1 init first skirmish), A's Sovereign Cunning
gives B "Strain" (-1 init), negated by the opponent's Immune Blocked / Immune Strain respectively.

Engine mechanics already existed (Blocked = -1 init first skirmish only, line ~266; Strain = -1 init,
line ~263; both have Immune negators). Verified: Prowess-6 build gets Parry+Immune Blocked; confers
transfer moves the debuff to the opponent correctly.

⚠ IMPORTANT LIMITATION: this works in the SCALAR path (run_matchup_vec → analyze_loadouts.py, the
custom-CSV analysis tool). The BATCH engine (batch_engine, used by the full tournament) does NOT read
Blocked/Strain/Immune Blocked at all (they're not in its precomputed tag-key list), and its
precompute-per-loadout model can't express the pairwise confers debuff. So for now these four tags are
measurable ONLY via analyze_loadouts.py / run_matchup_vec, not the full batch tournament. Wiring them
into the batch engine (add the tag keys + a per-pair confers injection) is a separate, larger job.

## Unstoppable → -1 enemy Parry; Poleaxe gains Unstoppable

MECHANIC: when an attacker has Unstoppable, the DEFENDER being hit gets -1 to Parry (parry succeeds on
6+ instead of 5+ — roughly halves Parry's value, 33%->17%). Wired via a parry_threshold param in
_saves_kernel + _roll_saves_vec; each save call passes the ATTACKER's Unstoppable flag (a_unstoppable
when B saves vs A, b_unstoppable when A saves vs B, incl. the b_first recompute). Lives in the saves
kernel, so it works in BOTH the scalar (run_matchup_vec / analyze_loadouts) AND batch engines.
numba==numpy still exact.

POLEAXE: gained "Unstoppable" permanently (now Steady/2H/Shatter Armor/Unstoppable, Crafted, AP-3 init+1).

MEASURED (mixed field w/ Parry+non-Parry; Poleaxe Unstoppable):
  vs ALL-Parry enemies:  Unstoppable group avg 0.294 vs non-Unstoppable 0.251  (+0.044 edge)
  mixed field:           0.349 vs 0.353  (~tie, -0.004)
  vs no-Parry:           ~0 difference
So Unstoppable is a CONDITIONAL anti-Parry trait: ~+4.4pp into Parry builds, ~neutral otherwise — no
power creep, no dead weight. Within-group weapon spread (base stats) exceeds the trait's effect:
Poleaxe+UNS 0.339-0.407 (strong base), War Hammer 0.343-0.388, Battle Axe still last 0.201-0.250
(its init-1 + Unwieldy sink it regardless — Unstoppable gives best RELATIVE Parry-resistance but can't
fix its baseline). Battle Axe init-1/Unwieldy remains an open tuning question.

## Battle Axe: dropped Unwieldy (no Steady added)

Battle Axe was bottom-tier (0.250 mixed field) — init-1 + Unwieldy too steep. Tested three versions:
  Unwieldy (orig): 0.250  |  bare (no Unwieldy/no Steady): 0.280  |  Steady-instead: 0.408
Steady overshot (Wrought weapon beating Forged 2HBastard 0.373 — tier inversion). Chose to just DROP
Unwieldy: Battle Axe now [Unstoppable, 2H, Cleave], AP-3 init-1, Wrought. Lands 0.280 — next to Halberd
(0.270), below Pike (0.328) and Forged 2HBastard (0.373). Modest lift off the floor; init-1 kept as its
lone drawback so it respects the tier ladder. Anti-Parry niche (Unstoppable) intact.

## NEW: Riposte (Grand Tournament mastery) + synced weapon tables

WEAPON/RETINUE/SHIELD/ARMOR tables synced to Gage's authoritative spec. Notable: KT shaking 0->2;
Lance/Morningstar/Poleaxe AP->-4; Battle Axe AP-2 [Unstoppable,2H,Cleave,Steady]; Halberd gains
Unwieldy; Cavalry Spear gains Steady (init 1->0); War Hammer Unwieldy->Steady; Crossbow gains
Unstoppable (init-1->0); Tower Shield -1TH->Unwieldy; Short Sword/Spears/Arming Sword drop +1TH/Shatter;
Cloth/Leather lose Nimble/Steady; Full Plate/Gothic LOSE Strain (now Unwieldy/none). Hunting Bow/Longbow
drop +1TH.

GRAND TOURNAMENT corrected: Unlock Established Prowess (Prowess>=6); innate Efficient Coliseum (zeros
Coliseum space); mastery = RIPOSTE; mastery_req = Conditioning Field + Coliseum. Added to
_EFFECT_BEARING_MASTERY so master_effect_closure pulls its reqs.

RIPOSTE mechanic (scalar engine / run_matchup_vec / analyze_loadouts): on each parry die that rolls
EXACTLY 6, the parrying side strikes the attacker back once at the parrier's weapon AP. Single clean
strikes — NO Cleave, NO Shatter Armor (shatter=0). Unstoppable (the riposter's, -1 attacker's parry)
and Rend (worsen attacker's regen) DO apply. Resolves during the defender's save step, same skirmish;
both sides can riposte. Wired via _saves_kernel returning (casualties, ripostes); ripostes resolved as
a follow-up save roll vs the original attacker and added to that skirmish's casualties. Reset per
skirmish; handled in all 3 save sites incl. the b_first recompute.

VERIFIED: Riposte adds real counter-damage (+0.56 opening deaths to attacker in a Bastard mirror vs
Parry+Riposte). Unstoppable into Parry+Riposte does far better (faces fewer parries->fewer ripostes).
Grand Tournament (mastered w/ Cond Field+Coliseum) confers Riposte; appears on 13/716 pool builds via
Royal Pavilion's GT mastery_req. Pool validates 0 invalid.

⚠ LIMITATION (same as domain-tags/Unstoppable-parry): Riposte + the Unstoppable->-1-parry effect live
in the SCALAR engine (run_matchup_vec -> analyze_loadouts.py). The BATCH engine has its OWN separate
_saves_kernel (batch_engine.py line ~147) that does NOT implement Riposte, the -1-parry, or even read
parry_threshold — so full batch tournaments won't reflect these. For Gage's "few loadouts at a time"
testing via analyze_loadouts.py this is fine. Porting to the batch kernel is a separate job.

## FIX #3: OOM at ~52% through a 2.95M-pair run — parent-side result retention (NOT block sizing)

This run got to 1.52M/2.95M pairs then died on a *5 MiB* allocation. A 5 MiB failure on a 32GB machine
is NOT a block-too-big problem — it's monotonic growth in the PARENT process. Per-block worker peak is
only ~64MB and steady-state in-flight (14 workers + numba) is ~3GB, far under 32GB. The leak: in
run_mode_batched's parallel loop, `_consume(bstart, fut.result())` consumed each block's result but the
Future object kept ._result pinned and `fut` was never deleted, so ~760 consumed result dicts (~2MB
each ≈ 1.5GB) plus heap fragmentation from hundreds of multi-MB allocs slowly exhausted RAM until a
fresh contiguous 5MiB request failed.

FIX: in the worker loop, capture res = fut.result(); _consume(...); then `del res; del fut` to drop the
block immediately, `del done_set` and `_gc.collect()` once per wait-batch. Added `gc` import. Verified
end-to-end (workers>1, real pool) — all outputs produced, freeing path clean.

NOTE: the crash traceback was in the Outrider counter-pick `_sample_from_weights` (now that the pool
contains Outrider Intercept Post builds, the `if _any_outrider:` block runs and allocates (N,7) weight
arrays even in random mode). That's just where the final straw landed — the (N,7) arrays are block-local
and correct; the cause was parent retention, not that path. If memory is still tight without psutil,
lower SLOT_BUDGET in the .bat (e.g. 60000) to shrink block_size further.

## FIX #4: startup OOM after editing engine files — stale numba cache → 28-worker compile storm

"Why broken all of a sudden": editing vectorized_combat/batch_engine INVALIDATED numba's cache=True
artifacts. This run died IMMEDIATELY (no progress bars) inside numba compiling _strikes_kernel →
ensure_blas → `import scipy.linalg`. Root cause: the parallel loop launched 2*n_workers = 28 blocks in
flight, so up to 28 worker processes COLD-COMPILED the numba kernels AND imported scipy simultaneously
at startup — a memory spike that OOM'd the pool on launch. The sibling workers' `_pickle.UnpicklingError:
invalid load key` / `could not find MARK` are corrupted IPC reads from workers dying mid-pipe.
(Different from FIX #3, which was parent retention failing at 52%; this fails at 0%.)

FIX (3 parts):
1. _warm_numba_kernels(): run each kernel once on tiny inputs IN THE PARENT before spawning workers, so
   the disk cache is populated and workers LOAD the compiled artifact instead of all recompiling +
   importing scipy at once. Wrapped in try/except (warmup is an optimization, never hard-fails).
2. max_inflight 2*n_workers → n_workers (was 28 on a 14-core box; the comment already said n_workers —
   the 2x was a latent bug doubling peak memory and the startup compile fan-out).
3. (FIX #3 retained) del res/del fut + gc.collect() per wait-batch to keep parent footprint flat.

Verified end-to-end (workers>1, real pool): warmup runs, all outputs produced.

STILL THE ROOT LEVER: psutil is not installed, so sizing falls back to a blind 3GB estimate. After a
clean numba cache exists (this run will build it), subsequent runs won't recompile. If a startup OOM
ever recurs after an edit, it's the recompile storm — the warmup now prevents it. `pip install psutil`
remains the single best fix for accurate sizing.

## FIX #5: STILL OOMing at 300k budget on a 2MiB alloc — model was wrong + verbose lied + a missing fn

psutil IS installed (confirmed: psutil 7.2.2 in the Python39 the .bat uses) and SLOT_BUDGET=auto now works
— the run picked slot_budget=300000. But it STILL OOM'd on a 2.29 MiB allocation. A 2MiB failure with the
math claiming ~5GB peak on a 32GB box means the bytes_per_slot model (220→700) was simply WRONG — real
transient footprint per slot (numba temporaries, np broadcasts, IPC pickling of result arrays, Windows
heap fragmentation) is far higher than any naive array count. Three actions:

1. auto_slot_budget made BRUTALLY conservative: bytes_per_slot 700→2000, safety 0.45→0.35, cap 300k→120k,
   and now divides by n_workers (matching the real in-flight count, was 2*n_workers). Also uses
   free = min(psutil.available, total*0.40) — Windows 'available' reads high while big contiguous allocs
   still fail under fragmentation. On a 32GB box this lands ~120k budget → block_size ~2,400 (vs the 6,000
   that crashed). Pessimistic peak modelled at 2000 B/slot so a 5x error still fits.
2. The verbose print was COSMETICALLY WRONG — hardcoded "{2*n_workers} blocks in flight" and a 700-based
   peak even though max_inflight is n_workers. Fixed to show the true n_workers count + 2000-based peak.
   (This is why earlier logs said "28 blocks in flight" — the message text, not the actual logic.)
3. While editing, auto_slot_budget got accidentally DELETED by a malformed replace (run_mode_batched then
   called a missing function). Restored it.

Verified end-to-end (auto path, workers>1): correct "N blocks in flight" print, all outputs produced.

If it STILL OOMs after this: the machine genuinely doesn't have the free contiguous RAM the run needs —
set SLOT_BUDGET=50000 (or lower) in the .bat and/or drop WORKERS to 8. Smaller blocks + fewer workers is
the bulletproof combination; it trades runtime for completion.

## FIX #6: ROOT CAUSE found — Windows COMMIT-limit exhaustion from numba, accumulating across crashes

Task Manager during a failure: 17.7 GB physical RAM FREE, but Committed = 112/128 GB. A 938 KiB alloc
failing with 17GB free physical RAM = the COMMIT limit (RAM + page file) was exhausted, NOT physical RAM.

WHY "it worked this morning then stopped": three things compounded.
1. numba caches compiled kernels keyed to source-file content. This morning the cache was warm → 14
   workers cheaply LOADED kernels. After Gage copy-pasted the new batch_engine.py, the cache was
   invalidated → every worker COLD-COMPILED, and numba/LLVM reserves several GB of Windows COMMIT per
   process (LLVM arenas + a threadpool sized to CPU count). 14 workers × ~8GB ≈ the 112 GB committed.
2. The .bat never passed --workers, so it defaulted to cpu_count-2 = 14 processes.
3. Each crashed run left COMMIT stranded (workers died mid-compile/mid-IPC — the UnpicklingError/
   "could not find MARK" garbled-pipe errors), so repeated retries ratcheted committed memory UP run
   over run until even tiny allocs failed. A RESTART cleared the stranded commit → "running fine now".
   This is not a per-allocation leak in the tournament code (that would die with the process); it's
   commit reservation accumulating across HARD-CRASHED runs.

FIXES (batch_engine.py + run_tournament.bat):
- NUMBA_NUM_THREADS=1 (+ OMP/OpenBLAS/MKL=1, workqueue layer) set at module top BEFORE numba imports
  (workers re-run module top on spawn, so they inherit it). Collapses the per-process commit
  reservation — the single most important change. With this, even a cold compile in every worker stays
  small, so cache-invalidation after an edit no longer storms.
- Explicit pool teardown in a try/finally: ex.shutdown(wait=True, cancel_futures=True) + del + gc at
  end of run, on success OR error. Verified 0 active child processes after a successful run, so worker
  COMMIT is released at end-of-run instead of lingering until interpreter exit (which was the
  run-over-run ratchet). 3.8 fallback for cancel_futures handled.
- (retained) parent-side _warm_numba_kernels(), in-flight = n_workers, result freeing.
- run_tournament.bat: added WORKERS knob (default 6) and passes --workers; SLOT_BUDGET stays auto.

With NUMBA_NUM_THREADS=1, 14 workers likely fits again — check Task Manager Committed during a run; if
it sits well under the limit, raise WORKERS back up for speed. Editing the engine files invalidates the
numba cache; the first run after an edit recompiles (now cheap, single-thread) and rebuilds the cache.

## FIX #7: Parquet schema clash (a_weapon null vs string) — memory issue GONE, this is unrelated

The memory fixes WORKED: this run processed 139,200 pairs smoothly, ETA stable ~100s, no OOM. It then
died on a totally different, simple bug: ParquetWriter schema mismatch. The first block written locked
a_weapon=string; a LATER block had every A-side weapon = None (a block of weaponless builds — e.g. KT
Unshakable with weapon=None, which the GENERATOR pool / BALANCED=0 path produces), so pyarrow inferred
that column as `null`, clashing with the locked string schema → write_table raised ValueError.

Root: in _block_to_table, a_weapon/b_weapon passed la.weapon straight through (unlike shield/ranged
which already used `or ""`), so an all-None block typed the column as null.

FIX: (1) normalize a_weapon/b_weapon to `la.weapon or ""` (matches shield/ranged + the CSV writer), so
None → "" and the column is never all-null. (2) Belt-and-suspenders: build an EXPLICIT pyarrow schema
(string/int32/float32/int64/bool per column) and pass it to pa.table, so ANY string column that's
all-None in some block stays `string` instead of flipping to `null`. Reproduced the exact all-None-weapon
block and confirmed both blocks now write; None serializes as "".

## Name display: Riposte replaces Parry when both present; Immune Poison confirmed live

Q: Is Immune Poison still in the game? YES — it's the Apothecary innate (the engine reads it; negates
Poison's natural-6 auto-fail). Poison comes from Toxicarium (pursuit), not any weapon. Immune Poison is
mostly inert in practice (Poison is rare — ~3 builds vs ~180 with the immunity in a 30/cell pool) but
it's a real interaction, not a dead tag. Kept.

Q: capturing Unstoppable/Riposte in the loadout name? YES. Riposte + all domain-standing tags (Parry,
Immune Blocked, confers:Blocked/Strain) are in extra_tags and therefore in the name. Unstoppable is a
WEAPON trait (Poleaxe/Battle Axe/War Hammer), so it's encoded by the weapon name, not an extra_tag — no
collision risk (same weapon = same Unstoppable status).

CHANGE (_name in loadouts.py, display-only): when a build has BOTH Riposte and Parry, the name now shows
only Riposte (it implies Parry — same Established-Prowess→Grand-Tournament source, and Riposte triggers
off a natural-6 parry). The extra_tags set is UNTOUCHED, so the engine still sees Parry and both
mechanics resolve normally. Parry-only builds still display Parry. Verified.

## Removed Immune Poison from Apothecary

Apothecary innate_tags ['Immune Poison'] → [] (mastery 'Apothecary Heal' unchanged). Verified:
Apothecary+Herb Garden now confers only Apothecary Heal; 0 pool builds carry Immune Poison; pool valid.
NOTE: nothing grants Immune Poison anymore, so Poison (from Toxicarium) is now uncounterable.

## NEW: four overhauling balance-analysis tools (analysis.py)

For the fine-tuning phase — these answer balance questions the existing toolkit (averages, MPC curves,
tag solo-impacts) can't, focusing on INTERACTIONS and the SHAPE of the win distribution:

1. dominance_frontier(df) -> (frontier_df, dominated_df). Pareto: a build is DOMINATED if another is
   cheaper-or-equal MPC AND wins >2pp more. Dominated = trap picks. Few dominated + smoothly-rising
   frontier = healthy. Long dominated list = wasted design space needing buffs/cost-cuts.
2. cheapest_counter(df, win_threshold=0.55) -> per build, the CHEAPEST opponent that beats it >=thresh.
   counter_mpc_premium>0 = you must overpay to answer it; n_counters==0 = UNCOUNTERABLE (oppressive).
   Sorted worst-first. The systematic version of counters_for across the whole field.
3. tag_synergy_matrix(df, min_support=30) -> pairwise tag synergy = wr(both) - (solo_a+solo_b+baseline).
   Positive = combo over-performs its parts (power-spike, e.g. watch Parry+Riposte); negative = redundancy.
4. intransitivity(df, win_margin=0.55) -> rock-paper-scissors health. Counts directed 3-cycles in the
   win matrix; intransitivity_ratio = cycles / fully-connected-triads. >0.20 healthy RPS depth; ~0 =
   near-solved power ladder (collapses to 'play the top build'). THE single depth-health metric.

All run off the standard matchups df (load_tournament). Verified on a real 90-build run: frontier flagged
87/90 dominated, cheapest_counter found the 1 uncounterable build, synergy + intransitivity both produce
sane numbers. On the full tuned pool these are the charts to drive fine-tuning decisions.

## Tag audit + BATCH PORT of Riposte / Immune Blocked / confers:Blocked / confers:Strain

AUDIT: All real combat tags ARE captured (in the name, scalar engine, and — for most — the batch
engine). Confirmed via source scan: Cond Field/MaxInit3/MinInit+1/GF Armor/Nimble are baked into
StaticArmy scalars (endurance/max_init/base_init/gf_armor), so pack_side carries them into batch even
though they're not in RUNTIME_TAGS. Only tier:* are "unread" — informational, stripped before combat.
The ONE real gap: the four newest tags were scalar-engine-only. Now ported:

BATCH PORT (batch_engine.py):
- _saves_kernel + _roll_saves_batch: added per-slot parry_thr (5 normally; 6 when attacker Unstoppable
  = -1 defender parry) and a def_riposte mask. Returns (casualties, ripostes); a natural-6 parry on a
  Riposte defender yields one riposte. numba AND numpy paths both updated. Warmup call updated.
- _precompute_regen_parry: added a_riposte/b_riposte masks (like a_parry).
- skirmish loop: a_riposte_eff/b_riposte_eff (fatigue-gated, fat==0). All 3 _roll_saves_batch call
  sites (b_cas, a_cas, b_first recompute nb_cas) pass atk_unstoppable + def_riposte and unpack the
  tuple. Riposte counter-damage resolved: B's natural-6 parries strike A back once at B's weapon AP
  (b_ap_vs_a), single clean strikes — no Cleave/Shatter; A's Parry/regen still defend, B's Unstoppable
  still -1's A's parry. Symmetric for A's ripostes onto B. Folded into a_cas/b_cas (capped by front).
- confers injection: per-pair before pack_side, strip confers:X from self + add X to opponent's tags
  (mirrors scalar). base_init already reads Blocked (-1 init first skirmish unless Immune Blocked) and
  Strain (-1 init unless Immune Strain), so the init effect is honored automatically once the tag lands.
  Immune Blocked is a self-tag already in extra_tags → honored by pack_side with no extra work.

VERIFIED: numba==numpy exact (casualties + ripostes). scalar≈batch within MC noise (<=0.010) on
riposte- and confers-carrying builds. Riposte non-inert in batch (Parry-only 0.210 -> Parry+Riposte
0.302 vs aggressor, matching scalar +Parry+Riposte synergy). Full tournament runs clean end-to-end.
=> Full BATCH tournaments now reflect Riposte + domain-standing mechanics. analyze_loadouts.py (scalar)
and the batch engine are now feature-equivalent for combat tags.

## Variant B: destroyed shield returns ALL its negatives (init penalty + Unwieldy clamp)

DECISION: A/B-tested shield counterplay. Shields are STRONG vs the non-Destroy-Shield field (+0.085
Wooden → +0.280 Tower over no-shield), so Destroy Shield is necessary counterplay. Variant A (old) left
a destroyed shield as dead weight — bearer lost save/TBH/TH but KEPT the -1 init penalty (and Tower's
Unwieldy), leaving them strictly WORSE than carrying no shield. Variant B makes destruction a clean
removal: the shield is gone, so are its negatives. Measured effect: +0.078 mean win rate to the
shield-bearer vs Destroy-Shield attackers (Tower vs War Hammer 0.132→0.220; vs Morningstar 0.387→0.457).
Chosen because counterplay should NEUTRALIZE a shield's advantage, not INVERT it into a liability.

IMPLEMENTATION (both engines):
- StaticArmy: added shield_unwieldy (shield carries Unwieldy = Tower) and unwieldy_non_shield (Unwieldy
  from weapon/armor/dual-equip — checked from SOURCES directly, NOT set subtraction, since armor and
  shield Unwieldy are the same string and subtraction would wrongly drop the armor's).
- Scalar (vectorized_combat.py): in the init clamp/clip, a_init_restore = where(shield_destroyed,
  -shield_init, 0) adds the init penalty back on destroyed runs; the Unwieldy positive-init clamp is
  lifted on destroyed runs ONLY when the shield is the sole Unwieldy source (shield_unwieldy &
  ~unwieldy_non_shield).
- Batch (batch_engine.py): same logic ported — packed shield_init/shield_unwieldy/unwieldy_non_shield,
  tiled, a_sh_only_unw mask, restoration applied at the init clip. Destroyed-state read as accumulated
  up to the current skirmish (matches scalar: the skirmish where the shield breaks still uses the
  penalized init; the next skirmish gets it restored).

VERIFIED: scalar shows expected variant-B numbers; scalar≈batch within established MC band (≤0.04);
flags correct (Tower+Chainmail unwieldy_non_shield=True so clamp NOT lifted; Tower+Leather=False so it
IS lifted on destruction). Full tournament runs clean. Ready for a variant-B tournament.

## Heal bug fix + Waver Test (Trigger 2), tracked separately from Shaken

BUG FIX (1): Apothecary Heal was counting COMBAT+SHAKE casualties toward the heal trigger. Heal now
reads COMBAT-only casualties (shake/waver/rout losses can't be healed — those models fled). Both engines.

WAVER TEST (2): a side losing MORE THAN 5 COMBAT casualties in a skirmish (net of that skirmish's heal)
takes an additional morale test at its own shake target — the "Waver Test". Asymmetric pressure: the
side losing the exchange breaks first, converting the symmetric mutual-wipe grind into decisive results.
Combat-only count, heal-offset. If the shake target is already 7+ (can't pass), it's a Waver-rout.
Tracked SEPARATELY from the exhaustion Shaken test — its own accumulator and cause-of-wipe code (4) —
so analysis distinguishes waver from shaken.

EXPOSED THROUGHOUT (waver next to shaken everywhere):
- Engines: run_matchup_vec + run_batch_random return avg_{a,b}_killed_waver and {a,b}_wipe_waver.
- CSV schema: _matchup_header() (tournament_vec) gains avg_*_killed_waver + *_wipe_waver right after the
  shake columns; both the scalar writer and batch _write_block_rows emit them in matching positions;
  batch parquet cast sets updated.
- analysis.battle_overview: kill_mix now has kill_mix_waver_pct alongside combat/shake/rout; pruned-load
  usecols whitelist includes the waver columns.
- Notebook (v9): battle-overview pie is now Combat / Shaken / Waver / Rout, and the narrative names the
  shaken-vs-waver split.

VERIFIED: scalar≈batch within 0.004 on MPC-12 mirror; tournament CSV carries waver; battle_overview
reports a waver slice (~4% in an MPC 8-12 sample); MPC-12 mirror mutual wipe ~0.34 → ~0.23. The waver
test is the asymmetric lever that compresses the high-MPC mutual-wipe spike toward the field average.
