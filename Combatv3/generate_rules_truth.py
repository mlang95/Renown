#!/usr/bin/env python3
"""
generate_rules_truth.py — emits RULES_TRUTH.md, the single source of truth for Renown combat
rules/attributes AS IMPLEMENTED IN CODE.

Purpose: auditing out-of-date design documents (Rulebook / Quick Start / Compendium / References /
Advanced Rules) against the live simulation. Re-run after ANY code change:
    python generate_rules_truth.py
Numeric facts (stat tables, pursuits, tactic matrix, constants) are read LIVE from the code and
cannot drift. Keyword semantics are curated in ONE place below (KEYWORDS dict) — update them here
when an engine mechanic changes.

For a future Claude session: read RULES_TRUTH.md top-to-bottom; every line is a checkable claim.
The SOURCE HASHES header tells you whether the .py files changed since generation (if hashes
mismatch, regenerate before trusting).
"""
import sys, hashlib, datetime, io
sys.path.insert(0, ".")
import renown_combat as rc
import loadouts as L
import vectorized_combat as vc

SRC_FILES = ["renown_combat.py", "loadouts.py", "vectorized_combat.py", "batch_engine.py"]

# ──────────────────────────────────────────────────────────────────────────────
# Curated keyword semantics — the ONE hand-maintained block. Each entry is the
# engine-true rule in document-ready language. Update alongside engine changes.
# ──────────────────────────────────────────────────────────────────────────────
KEYWORDS = {
  "— GEAR / WEAPON TAGS —": None,
  "2H": "Two-handed: cannot be combined with a shield (generation constraint; Bastard Sword dual-profile is the exception: 1H+shield until the shield is destroyed, then 2H stats).",
  "Unwieldy": "Clamps POSITIVE tactic initiative modifiers to 0 — the unit's initiative cannot be IMPROVED by tactics. NOT a flat init penalty (the weapon/shield/armor 'init' stat is separate). Any Unwieldy source enables the clamp; sources: weapon, armor, shield, or dual-equipping (real melee + ranged) WITHOUT Tiltyard mastery. 'Immune Unwieldy' (Tiltyard mastery) removes the clamp; a destroyed shield lifts it only if the shield was the SOLE Unwieldy source.",
  "Steady": "Clamps NEGATIVE tactic initiative modifiers to 0 — the unit's initiative cannot be REDUCED by tactics. A unit with BOTH Steady and Unwieldy (e.g. Cavalry Spear, 1H Bastard) has its tactic-init locked in both directions (immune to tactic init changes).",
  "Nimble": "Acts at +1 initiative in the FIRST skirmish only.",
  "Shatter Armor": "A natural-6 to-hit is a Shatter strike: it bypasses the armor save entirely (auto-fails the save). Parryable ONLY by a defender with Riposte, and only on a natural-6 parry (see Riposte). Without Riposte, Shatter is unparryable.",
  "Cleave": "Each natural-6 to-hit generates one extra strike.",
  "Destroy Shield": "On a natural-6 to-hit vs a shielded defender, the defender's shield is destroyed for the rest of the battle (loses save bonus, -1TBH, init effects). Blocked by 'Immune Destroy Shield' (Heater).",
  "Unstoppable": "v2: the attacker ignores the defender's shield -1TBH penalty ONLY. Does NOT ignore tactic to-hit penalties. Also: -1 to the DEFENDER's Parry against this attacker (5+ -> 6+; Improved 4+ -> 5+).",
  "One Shot": "Ranged weapon fires in the first skirmish only; later skirmishes use the melee weapon (or Farm Tools if none).",
  "Deflect": "(All ranged weapons.) Parrying a ranged strike: -1 to Parry, applied AFTER Unstoppable, threshold CAPPED at 6+ (penalties can never push a normal-hit parry past 6+). A parry vs a ranged strike ONLY parries — it NEVER triggers a Riposte (including the Riposte 6+ parry vs a ranged Shatter hit: the 6 negates, no counter).",
  "-1TBH": "Shield property: the ATTACKER striking this shield-bearer suffers +1 to their target to-hit (i.e. -1 to-hit). Zeroed if the attacker is Unstoppable or the shield is destroyed.",
  "Shield -1TH (Tower own-side)": "Tower-class shields also hamper the BEARER's own attacks (+1 to own target to-hit). Not affected by enemy Unstoppable; disappears if the shield is destroyed.",
  "Immune Destroy Shield": "Shield cannot be destroyed (Heater).",
  "— DEFENSE / RESOLUTION TAGS —": None,
  "Parry": "(Established Prowess, domain Prowess >= 6.) When a hit fails the armor save, roll d6: 5+ negates the hit. Penalties: attacker Unstoppable -1 (needs 6+), ranged strike -1 (Deflect), stacked in that order, CAPPED at 6+. Disabled while fatigued.",
  "Improved Parry": "(Grand Tournament innate.) Normal-hit parry threshold improved by 1: 4+ base; 5+ vs Unstoppable; 5+ vs ranged; 6+ vs Unstoppable ranged (cap). No effect on Shatter. Implies Parry.",
  "Riposte": "(Grand Tournament mastery.) A parry die of EXACTLY 6 negates the hit AND strikes the attacker back once (resolved immediately at the riposter's weapon AP; single clean strikes, no Cleave/Shatter; the counter resolves as melee). Riposte also grants a 6+ parry against SHATTER hits — the 6 is the riposte. Exceptions: a parry vs a RANGED strike never ripostes; ripostes do not themselves riposte; disabled while fatigued.",
  "Regenerate N": "When a hit fails save (and parry), roll d6: N+ negates. Disabled while fatigued. 'Regenerate Reroll' (Hospitaller mastery): one reroll of a failed Regenerate die.",
  "Apothecary Heal": "Post-battle/per-battle heal effect (Apothecary chain).",
  "Poison": "Defender's armor save FAILS on a natural 6 (in addition to normal failures). Blocked by Immune Poison.",
  "— ACCURACY / INITIATIVE TAGS —": None,
  "+1TH": "-1 to the bearer's target to-hit, every skirmish. Applied PRE-CAP (offsets fatigue under the 6+ ceiling) and offsets tactic/shield penalties one-for-one in the final sum. Can push target below 2 -> auto-hit.",
  "+1TH first / +1TH after_first": "LEGACY tags (engine-supported, no longer granted by anything): -1 target to-hit in skirmish 1 only / in skirmishes 2+ only.",
  "Immune Tactic TH": "(Ministry innate.) Ignores ALL tactic-sourced -1TH — both enemy-imposed and the self-penalty of the bearer's own tactic. (All 6 TH-penalty pairings in the tactic matrix land on the side playing Ambush or Charge.) Shield TBH and own-shield TH unaffected.",
  "Seize: first": "(Ministry innate.) The bearer gains Seize the Initiative (+1 initiative) in the FIRST skirmish; the opponent never gets it. Mutual Ministry cancels.",
  "MaxInit3 / MinInit+1": "(Ministry mastery.) Initiative clamps: bearer's initiative ceiling 3 / floor raised by 1. Measured near-cosmetic.",
  "Yew Heart": "-1 target to-hit in the first skirmish when using a ranged weapon.",
  "— MORALE / STAMINA TAGS —": None,
  "Unshakable": "(KT retinue / Preceptory innate.) Exempt from shaken (exhaustion) morale tests. (Open design question: also exempts Waver as implemented.)",
  "Drilled": "(Royal Pavilion mastery.) No endurance loss in skirmish 1.",
  "Cond Field": "(Conditioning Field, self-mastering.) +1 endurance.",
  "Shake +1": "Worsens the bearer's shaking threshold by +1 (kit tag).",
  "Steadfast": "Morale-related kit tag (see playstyles/kits).",
  "Immune Strain / confers:Blocked / confers:Strain / Immune Blocked": "Cunning/Prowess standing economy tags: Rising Prowess (3) grants Immune Blocked; Cunning 6/10 confer Blocked/Strain on opponents; Royal Pavilion innate grants Immune Strain.",
  "— OTHER —": None,
  "GF Armor": "(Gilded Foundry mastery.) Incoming AP reduced by 1 (your armor saves vs effective ap+1).",
  "Rend": "(Master Workshop mastery.) Weapon-damage rider (see engine).",
  "Outrider: once/first/first_two/every": "(Outrider Intercept Post.) Tactic-reveal counter-pick: see the opponent's tactic and best-respond (innate: once/first skirmish; mastery: first two; 'every' legacy). Mutual Outrider cancels.",
}

CORE_MATH = """
DICE & FRONTAGE
- ATTACKS = 1 per retinue in the FRONT LINE (after reserves move up), max FRONT_CAP = {front}.
  Army "size" is a RETINUE COUNT (half-scale game), NOT a soldier count. There is NO soldiers/5
  conversion in the engine.
- Front cap {front}, reserve cap RESERVE_CAP = {reserve}; reserves refill the front between strike
  exchanges. Morale (shake/waver) tests roll over the field up to SHAKE_CAP = {shakecap}.

TO-HIT ASSEMBLY (per side, per skirmish)
- target = min( base_to_hit + improving + fatigue , 6 ) + worsening
  improving (lower target): weapon +1TH, Ministry +1TH, Yew, positive tactic TH
  worsening (raise target): enemy shield -1TBH (unless attacker Unstoppable), own Tower -1TH,
                            negative tactic TH (unless Immune Tactic TH)
- FATIGUE CAP: fatigue can never push the target past 6+ on its own; worsening mods apply AFTER the
  cap and CAN reach 7+ (auto-miss).
- AUTO-HIT: if the FINAL target (before clipping) is < 2, every die hits. (KT base to-hit 1 auto-hits
  unless a penalty pushes it back to 2+.)
- BLUNDER: initiative <= -2 clamps that side's to-hit to 6+ (then worsening can push past).
- Dice cap: target clipped to [2,7] for rolling; 7+ = auto-miss.

SAVE / RESOLUTION ORDER (per hit)
- save target = armor_save - weapon_ap - shield_bonus (if alive) +/- tactic TS; clip [2,7];
  <2 auto-saves... (engine: auto-pass if raw < 2; >=7 auto-fails). Poison: natural-6 save fails.
- SHATTER strikes (attacker natural-6 with Shatter Armor) skip the save (auto-fail).
- Order: HIT -> ARMOR SAVE -> (fail) PARRY -> (fail) REGENERATE -> casualty.
  (PARRY_BEFORE_SAVE experimental toggle = {pbs}: if True, parry first; casualties identical,
  ripostes rise. DEFAULT OFF — documents should describe save-then-parry.)

PARRY THRESHOLD MATRIX (normal hits; cap 6+)
  plain Parry:    melee 5+ | Unstoppable 6+ | ranged 6+ | Unstoppable+ranged 6+ (cap)
  Improved Parry: melee 4+ | Unstoppable 5+ | ranged 5+ | Unstoppable+ranged 6+ (cap)
  SHATTER hits:   6+ with Riposte (the 6 IS the riposte; vs ranged it only parries) | unparryable without.

FATIGUE & MORALE
- Endurance: lose 1 per fought skirmish (Drilled exempts skirmish 1; some tactic pairings are
  no-combat and may or may not cost endurance — see tactic matrix 'no_combat_endurance').
- At endurance 0: unit is FATIGUED — to-hit worsens per fatigue (capped 6+), Parry/Riposte/Regenerate
  disabled, exhaustion (shaken) morale tests each skirmish vs 'shaking' value (Unshakable exempt).
- Waver: heavy-loss morale break (separate trigger; Unshakable exempt as implemented).
- Rout: post-break casualties.

RIPOSTE COUNTER RESOLUTION
- Each parry die of exactly 6 (with Riposte, vs a MELEE strike) = 1 counter-strike at the riposter's
  weapon AP, resolved immediately; defender's parry/regen apply; counters cannot be riposted.
"""

AUDIT_CHECKLIST = """
Recent code-side changes documents are MOST LIKELY to contradict (check these first):
 1. RETINUES: endurance ladder is now 3/2/2/1 (Levy/MaA/Sgt/KT); KT to-hit 1 (auto-hits unpenalized);
    Levy shaking 5; Sgt shaking 4. Old docs may say endurance 3 across the board or KT to-hit 2.
 2. Lance now has UNSTOPPABLE. Poleaxe ap is -4 (was -5). War Hammer remains -8.
 3. All ranged weapons carry DEFLECT; the ranged-vs-parry rules (−1 parry after Unstoppable, cap 6+,
    no riposte vs ranged) are new and absent from old docs.
 4. GRAND TOURNAMENT: innate = Improved Parry; mastery = Riposte. Riposte unlock = Grand Tournament
    + Conditioning Field + Coliseum, NET 2 MPC (GT's Efficient zeroes Coliseum), gated on
    Established Prowess. Riposte now parries Shatter on a 6.
 5. MINISTRY OF MILITARY STRATEGY (new spec): innate = Seize: first + Immune Tactic TH;
    mastery = MaxInit3 + MinInit+1 + +1TH (all skirmishes). The old '+1TH first/after_first' split
    is gone from the rules (legacy engine tags only).
 6. Endurance is uniform NOWHERE: docs claiming 'endurance 3 for all retinues' are stale.
 7. Parry source: Established Prowess (Prowess 6); Immune Blocked: Rising Prowess (3).
 8. Tiltyard: innate = ABILITY to dual-equip; dual-equip without mastery = everything Unwieldy;
    mastery ('Immune Unwieldy', req Fletchery+Coliseum) negates ALL Unwieldy.
 9. Unstoppable is v2: ONLY ignores shield -1TBH (not tactic penalties). Old docs may state the
    stronger version.
10. Heater Shield: Immune Destroy Shield + -1TBH, save +1, init 0, Crafted.
11. Name/keyword 'Deflect' is the official term for the ranged-parry interaction.
"""

def dump_table(name, d, cols):
    out = [f"### {name}", "", "| " + " | ".join(["key"] + cols) + " |",
           "|" + "---|" * (len(cols) + 1)]
    for k, v in d.items():
        row = [str(k)]
        for c in cols:
            val = v.get(c, "")
            if isinstance(val, list):
                val = ", ".join(str(x) for x in val) or "—"
            row.append(str(val))
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out) + "\n"

def main():
    buf = io.StringIO(); w = buf.write
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    w(f"# RENOWN — RULES SOURCE OF TRUTH (generated from code)\n\n")
    w(f"Generated: {now}. Regenerate with `python generate_rules_truth.py` after ANY code change.\n\n")
    w("SOURCE HASHES (if these mismatch the current files, REGENERATE before trusting):\n")
    for f in SRC_FILES:
        try:
            h = hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]
        except OSError:
            h = "MISSING"
        w(f"- {f}: `{h}`\n")
    w("\nHow to audit a document: for every stat, keyword, cost, threshold or procedure the document\n"
      "states, find the matching line below; any mismatch = the DOCUMENT is stale (code is truth).\n\n")

    w("## 1. STAT TABLES (live from renown_combat.py)\n\n")
    w(dump_table("RETINUES", rc.RETINUES, ["cost", "to_hit", "endurance", "shaking", "unshakable"]))
    w("\nDerived: to-hit < 2 after modifiers = AUTO-HIT (every die). KT (to-hit 1) auto-hits unless penalized back to 2+.\n\n")
    w(dump_table("WEAPONS (melee)", rc.WEAPONS, ["ap", "init", "tags", "tier"])); w("\n")
    w(dump_table("RANGED", rc.RANGED, ["ap", "init", "tags", "tier"])); w("\n")
    w(dump_table("SHIELDS", {str(k): v for k, v in rc.SHIELDS.items()}, ["save_bonus", "init", "tags", "tier"])); w("\n")
    w(dump_table("ARMORS (save target; lower = better)", rc.ARMORS, ["save", "tier", "tags"])); w("\n")

    w("## 2. KEYWORD SEMANTICS (engine-true definitions)\n\n")
    for k, v in KEYWORDS.items():
        if v is None:
            w(f"\n**{k}**\n\n")
        else:
            w(f"- **{k}** — {v}\n")

    w("\n## 3. CORE COMBAT MATH & RESOLUTION\n")
    w(CORE_MATH.format(front=vc.FRONT_CAP,
                       reserve=vc.RESERVE_CAP, shakecap=vc.SHAKE_CAP,
                       pbs=getattr(vc, "PARRY_BEFORE_SAVE", False)))

    w("\n## 4. TACTIC MATRIX (live; mods: I=initiative, TH=to-hit, TS=target-save; +TH = better accuracy)\n\n")
    w(f"Tactics: {', '.join(rc.TACTICS)}\n\n")
    w("| attacker tactic | defender tactic | attacker mods | defender mods | notes |\n|---|---|---|---|---|\n")
    for (a, d), (am, dm) in rc.TACTIC_MATRIX.items():
        def fmt(m):
            parts = [f"{k}{v:+d}" for k, v in m.items() if k in ("I", "TH", "TS") and v]
            return " ".join(parts) or "—"
        notes = []
        if am.get("end_battle") or dm.get("end_battle"): notes.append("can end battle")
        if am.get("no_combat") or dm.get("no_combat"): notes.append("no combat")
        w(f"| {a} | {d} | {fmt(am)} | {fmt(dm)} | {', '.join(notes)} |\n")

    w("\n## 5. PURSUITS (live from loadouts.PURSUITS_INFO)\n\n")
    w("| pursuit | MPC cost | prereqs | domain unlock | innate tags | mastery tags | mastery req | efficient |\n")
    w("|---|---|---|---|---|---|---|---|\n")
    for p, info in L.PURSUITS_INFO.items():
        dom = ", ".join(f"{k} {v}" for k, v in info.get("domain", {}).items()) or "—"
        w(f"| {p} | {info.get('cost','?')} | {', '.join(info.get('prereqs',[])) or '—'} | {dom} | "
          f"{', '.join(info.get('innate_tags',[])) or '—'} | {', '.join(info.get('mastery_tags',[])) or '—'} | "
          f"{', '.join(info.get('mastery_req',[])) or '—'} | {info.get('efficient','—')} |\n")
    mons = sorted(getattr(L, "_MONUMENTS", []))
    w(f"\nMONUMENTS: {', '.join(mons)}\n")
    w(f"Name-bracket abbreviations: {getattr(L, '_MON_ABBR', {})}\n")

    w("\n## 6. DOMAIN STANDINGS\n\n")
    w("Thresholds: Rising 3 / Established 6 / Sovereign 10 (per domain: Industry, Prowess, Piety, Cunning).\n")
    w("Standing grants: Prowess>=3 -> Immune Blocked; Prowess>=6 -> Parry; Cunning>=6 -> confers:Blocked; Cunning>=10 -> confers:Strain.\n")
    w(f"Equipment tier -> Industry standing floor: {L.TIER_INDUSTRY_REQ}\n")
    w("Equipment unlock chain: Crude -> Cast -> Wrought -> Forged -> Crafted (via smithing pursuits; see derive_tier_from_pursuits).\n")

    w("\n## 7. RIPOSTE UNLOCK (worked example, verified)\n\n")
    P = {"Grand Tournament", "Conditioning Field", "Coliseum"}
    mpc, dom, tags = L.compute_pursuit_cost(P)
    w(f"Pursuits {sorted(P)} -> MPC {mpc}, domain req {dict((k,v) for k,v in dom.items() if v)}, tags {sorted(tags)}.\n")
    w("Dropping ANY of the three removes Riposte. Net 2 MPC because GT's Efficient zeroes Coliseum.\n")

    w("\n## 8. DOCUMENT AUDIT CHECKLIST (recent changes most likely to contradict old docs)\n")
    w(AUDIT_CHECKLIST)

    open("RULES_TRUTH.md", "w").write(buf.getvalue())
    print(f"RULES_TRUTH.md written ({len(buf.getvalue())} chars)")

if __name__ == "__main__":
    main()