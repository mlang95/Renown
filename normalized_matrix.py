"""
Normalized symmetric tactic matrix.

For each unique pair (X, Y), I encode ONE interaction. The matrix entry for both
(X, Y) and (Y, X) describes the same exchange, swapping which side is row/column.

Effects per pair:
  I_for_X = initiative differential. X gets +N, Y gets -N.
  hit_for_X = net hit-exchange shift for X. When X attacks Y, X hits easier by N.
              When Y attacks X, Y hits harder by N (so X is harder to be hit).
              Encoded as TH=N on X-side mods, TBH=N on Y-side mods (functionally equivalent in code).
  save_for_X = save shift. When X is hit, X saves better by N. (TS effect.)
  end = battle ends on this matchup.

I'll derive both (X, Y) and (Y, X) cells from this single definition.
"""

import random
from renown_combat import (
    make_army, monte_carlo, TACTICS,
    random_tactic_picker, fixed_tactic_picker,
)
import renown_combat


def _m(I=0, TH=0, TBH=0, TS=0, end=False, no_combat=False):
    return {"I": I, "TH": TH, "TBH": TBH, "TS": TS, "end": end, "no_combat": no_combat}


# For each unordered pair, encode the canonical interaction.
# (winner, loser): describes how much advantage winner gets.
# (init_diff, hit_diff, save_diff) where positive favors winner.

# Pairs are commented with their rules-document semantics
PAIR_RULES = {
    # Self-pairs: No combat this skirmish (battle continues, fatigue still ticks)
    frozenset(["Scout", "Scout"]):                  ("no_combat", None, None, None),
    frozenset(["Ambush", "Ambush"]):                ("no_combat", None, None, None),
    frozenset(["Flank", "Flank"]):                  ("no_combat", None, None, None),

    # Both Charge: simultaneous, both +1TH
    frozenset(["Charge", "Charge"]):                ("both", "TH=1", None, None),

    # Both FF: No bonus
    frozenset(["Fighting Formation", "Fighting Formation"]): ("neutral", None, None, None),

    # Both DF: both +1 to save
    frozenset(["Defensive Formation", "Defensive Formation"]): ("both", None, None, "TS=1"),

    # Both FB: battle ends
    frozenset(["Fall Back", "Fall Back"]):          ("end", None, None, None),

    # ----- Inter-tactic pairs -----

    # Scout vs Ambush: Ambush wins outright (caught off guard). Ambush: +1I, +1TH, -1TBH (Scout exposed)
    # Mirror: Scout: -1I, +1TBH, -1TH ← from R2C1
    # Net: Ambush winner. Init +1, hit +1.
    # Rules:
    #   R1C2 Scout->Ambush: "+1I, +1TH, -1TBH" for Scout (Scout wins??)
    #   R2C1 Ambush->Scout: "-1I, +1TBH, -1TH" for Ambush (Ambush loses??)
    # WAIT - read again: row is attacker.
    #   R1C2: Scout attacker, Ambush defender. Scout gets +1I, +1TH, -1TBH.
    #   R2C1: Ambush attacker, Scout defender. Ambush gets -1I, +1TBH, -1TH.
    # So when Scout is attacker, Scout wins (+1I). When Ambush is attacker, Ambush LOSES (-1I).
    # This says: whoever PICKS Scout vs Ambush, Scout wins. Consistent: Scout always wins vs Ambush.
    # Net winner: Scout. Init +1, hit +1.
    frozenset(["Scout", "Ambush"]):                 ("Scout", 1, 1, 0),

    # Scout vs Flank: Flank wins init.
    #   R1C3: Scout attacker vs Flank: Scout gets -1I.
    #   R3C1: Flank attacker vs Scout: Flank gets +1I.
    # Net: Flank wins init by 1. No hit shift.
    frozenset(["Scout", "Flank"]):                  ("Flank", 1, 0, 0),

    # Scout vs Charge: Charge wins init. Hit-exchange: 
    #   R1C4: Scout->Charge: Scout gets -1I, -1TBH (Scout is easier to be hit by Charge)
    #   R4C1: Charge->Scout: Charge gets +1I, -1TH (Charge hits worse... but Scout taking the strike?)
    # Reading these as mirrors per Gage: both say Charge has init advantage + Scout has hit-exchange penalty.
    # "-1TBH on Scout" and "-1TH on Charge" both = "Charge's strike vs Scout is less effective by 1".
    # WAIT. -1TBH on Scout makes Scout EASIER to be hit (helps Charge). -1TH on Charge makes Charge hit worse (hurts Charge).
    # These are opposite. Gage's interpretation: "-1TH for the row tactic in cell B" should be read as describing the column tactic's
    # equivalent advantage. So cell B's "-1TH on Charge attacker" really means "Scout has -1TH effect against Charge" = Scout penalized.
    # Net: Charge wins init by 1, Charge wins hit by 1.
    frozenset(["Scout", "Charge"]):                 ("Charge", 1, 1, 0),

    # Scout vs FF: FF wins init.
    #   R1C5: Scout->FF: Scout gets -1I, +1TBH (Scout harder to be hit)
    #   R5C1: FF->Scout: FF gets +1I, +1TH (FF hits better)
    # Mirror reading: FF wins init AND hit. Scout's +1TBH conflicts though.
    # Interpretation: Scout's +1TBH = Scout has defensive bonus. FF +1TH = FF has offensive bonus. These cancel.
    # Cleanest: FF wins init only. Hit-exchange: net 0.
    frozenset(["Scout", "Fighting Formation"]):     ("Fighting Formation", 1, 0, 0),

    # Scout vs DF: 
    #   R1C6: Scout->DF: Scout gets +1TH (Scout hits better)
    #   R6C1: DF->Scout: DF gets +1TBH (DF harder to be hit)
    # Mirror reading: Scout hits DF easier OR DF is harder to hit - same effect from both sides.
    # Net: Scout hits DF by 1. No init shift. Single-direction advantage.
    # But who has the advantage? Scout's +1TH = Scout hits easier. DF's +1TBH = DF harder to hit.
    # These are OPPOSITE. Resolution: take it as a wash, no hit shift. Or pick one direction.
    # I'll interpret as net 0 hit shift (it cancels itself): no advantage.
    # Actually wait - if Scout +1TH and DF +1TBH BOTH apply to Scout's strikes against DF, they cancel.
    # When DF strikes back, nothing applies. So net: no effect.
    # That seems like a weird matrix entry. Let me pick: Scout has advantage (since DF is defensive and Scout is recon/info).
    # Net: Scout wins hit by 1.
    frozenset(["Scout", "Defensive Formation"]):    ("Scout", 0, 1, 0),

    # Scout vs FB: Battle ends.
    frozenset(["Scout", "Fall Back"]):              ("end", None, None, None),

    # Ambush vs Flank: Flank wins.
    #   R2C3: Ambush->Flank: Ambush gets -1I, +2TH (Ambush hits well but loses init)
    #   R3C2: Flank->Ambush: Flank gets +1I, +2TBH (Flank harder to be hit AND wins init)
    # Hmm this one is interesting. Both cells have +2 something on the row tactic.
    # Mirror reading: Flank wins init. Ambush has +2 hit (or Flank has +2 defensive = Ambush hits worse).
    # These conflict. Picking Flank as overall winner: Flank +1I, Flank +2 hit-exchange.
    # That's a 3-point swing which is huge. Let me dial down: Flank +1I, +1 hit-exchange.
    frozenset(["Ambush", "Flank"]):                 ("Flank", 1, 1, 0),

    # Ambush vs Charge: Ambush wins.
    #   R2C4: Ambush->Charge: Ambush gets +1I, +1TH (Ambush wins!)
    #   R4C2: Charge->Ambush: Charge gets -1I, +1TBH (Charge loses init, has +1TBH defense)
    # Mirror reading: Ambush wins init + hit. Charge's +1TBH partial defense.
    # Net: Ambush +1I, +1 hit-exchange.
    frozenset(["Ambush", "Charge"]):                ("Ambush", 1, 1, 0),

    # Ambush vs FF: Ambush wins init.
    #   R2C5: Ambush->FF: Ambush gets +1I
    #   R5C2: FF->Ambush: FF gets -1I
    # Net: Ambush +1I. No hit shift.
    frozenset(["Ambush", "Fighting Formation"]):    ("Ambush", 1, 0, 0),

    # Ambush vs DF: Both have +1 TS for attacker (defender saves better).
    #   R2C6: Ambush->DF: "+1 To Enemy Save" - DF saves better
    #   R6C2: DF->Ambush: "+1 To Save" - DF saves better
    # Both consistent: DF saves better. Net: DF +1 save.
    frozenset(["Ambush", "Defensive Formation"]):   ("Defensive Formation", 0, 0, 1),

    # Ambush vs FB: Battle ends.
    frozenset(["Ambush", "Fall Back"]):             ("end", None, None, None),

    # Flank vs Charge: Charge wins init.
    #   R3C4: Flank->Charge: Flank gets -1I
    #   R4C3: Charge->Flank: Charge gets +1I
    # Net: Charge +1I.
    frozenset(["Flank", "Charge"]):                 ("Charge", 1, 0, 0),

    # Flank vs FF: Flank wins.
    #   R3C5: Flank->FF: Flank gets +1I, +1TH
    #   R5C3: FF->Flank: FF gets -1I, +1TBH (FF defensive bonus)
    # Mirror: Flank +1I, +1 hit. FF's +1TBH partial defense.
    # Net: Flank +1I, +1 hit-exchange.
    frozenset(["Flank", "Fighting Formation"]):     ("Flank", 1, 1, 0),

    # Flank vs DF: Flank wins init.
    #   R3C6: Flank->DF: Flank gets +1I
    #   R6C3: DF->Flank: DF gets -1I
    # Net: Flank +1I.
    frozenset(["Flank", "Defensive Formation"]):    ("Flank", 1, 0, 0),

    # Flank vs FB: Flank wins.
    #   R3C7: Flank->FB: Flank gets -1I, -1TH (Flank LOSES?? That's weird vs Fall Back)
    #   R7C3: FB->Flank: FB gets +1I, +1TH
    # Hmm cell R3C7 has Flank LOSING. That contradicts the usual pattern (Flank should catch Fall Back).
    # Looking at R7C3 ("Fall Back attacker vs Flank defender"): FB gets +1I, +1TH. FB wins.
    # So in BOTH cells, Fall Back is favored. That's the canonical interaction: FB wins vs Flank.
    # Thematically: Flank tries to circle around, Fall Back retreats successfully.
    # Net: Fall Back +1I, +1 hit.
    frozenset(["Flank", "Fall Back"]):              ("Fall Back", 1, 1, 0),

    # Charge vs FF: Charge wins.
    #   R4C5: Charge->FF: Charge gets +1TH ("+1 To Hit")
    #   R5C4: FF->Charge: FF gets +1TBH
    # Mirror reading: Charge has hit advantage OR FF has defensive bonus (same effect).
    # Net: Charge +1 hit.
    frozenset(["Charge", "Fighting Formation"]):    ("Charge", 0, 1, 0),

    # Charge vs DF: DF wins hard (the canonical counter).
    #   R4C6: Charge->DF: Charge gets -1I, +1 to Their Save (DF saves better), -1TH
    #   R6C4: DF->Charge: DF gets +1I, +1 to Save, -1TBH
    # Mirror reading: DF wins init + save + hit (Charge -1TH or DF +1TBH = same effect).
    # Net: DF +1I, +1 hit, +1 save. Strong counter.
    frozenset(["Charge", "Defensive Formation"]):   ("Defensive Formation", 1, 1, 1),

    # Charge vs FB: Charge wins (catches the retreat).
    #   R4C7: Charge->FB: Charge gets +1I, +1TH
    #   R7C4: FB->Charge: FB gets -1I, +1TBH (FB defensive bonus)
    # Mirror: Charge wins init + hit. FB has partial defensive bonus.
    # Net: Charge +1I, +1 hit.
    frozenset(["Charge", "Fall Back"]):             ("Charge", 1, 1, 0),

    # FF vs DF: FF wins (aggressive beats purely defensive).
    #   R5C6: FF->DF: FF gets +1TH
    #   R6C5: DF->FF: DF gets +1TBH
    # Mirror: FF hit advantage = same as DF defense bonus (these cancel? or describe same shift?).
    # Per Gage: they're the same mod. Net: FF +1 hit.
    frozenset(["Fighting Formation", "Defensive Formation"]): ("Fighting Formation", 0, 1, 0),

    # FF vs FB: FF wins (presses the retreat).
    #   R5C7: FF->FB: FF gets +1TH
    #   R7C5: FB->FF: FB gets +1TBH
    # Mirror: FF +1 hit.
    frozenset(["Fighting Formation", "Fall Back"]): ("Fighting Formation", 0, 1, 0),

    # DF vs FB: Battle ends.
    frozenset(["Defensive Formation", "Fall Back"]): ("end", None, None, None),
}


def build_normalized_matrix():
    """Build a clean symmetric matrix from PAIR_RULES."""
    matrix = {}
    for x in TACTICS:
        for y in TACTICS:
            key = frozenset([x, y]) if x != y else frozenset([x])
            if x == y:
                key = frozenset([x, y])  # frozenset dedups
            # Look up canonical rule
            rule = None
            for k in PAIR_RULES:
                if k == frozenset([x, y]):
                    rule = PAIR_RULES[k]
                    break
            if rule is None:
                # default: neutral
                matrix[(x, y)] = (_m(), _m())
                continue
            winner, init_adv, hit_adv, save_adv = rule

            if winner == "end":
                matrix[(x, y)] = (_m(end=True), _m(end=True))
            elif winner == "no_combat":
                matrix[(x, y)] = (_m(no_combat=True), _m(no_combat=True))
            elif winner == "neutral":
                matrix[(x, y)] = (_m(), _m())
            elif winner == "both":
                # Special: applies to both
                if init_adv == "TH=1":
                    matrix[(x, y)] = (_m(TH=1), _m(TH=1))
                elif save_adv == "TS=1":
                    matrix[(x, y)] = (_m(TS=1), _m(TS=1))  # both save better
                else:
                    matrix[(x, y)] = (_m(), _m())
            else:
                # winner is X or Y
                I_adv = init_adv or 0
                H_adv = hit_adv or 0
                S_adv = save_adv or 0
                # Init is symmetric (winner +I, loser -I) — these are SEPARATE rolls
                # affecting "who strikes first" and the symmetry is meaningful.
                # Hit advantage is asymmetric: A's TH and B's TBH adjust the SAME
                # die-roll target. Applying TH to both sides double-counts the
                # hit-exchange dimension. So hit_adv goes on the winner's TH only,
                # which makes the winner's strikes more effective without giving
                # the loser an extra penalty on their own strikes.
                if winner == x:
                    x_mods = _m(I=I_adv, TH=H_adv)
                    y_mods = _m(I=-I_adv, TH=0)
                    if S_adv:
                        x_mods["TS"] = S_adv
                    matrix[(x, y)] = (x_mods, y_mods)
                else:  # winner == y
                    y_mods = _m(I=I_adv, TH=H_adv)
                    x_mods = _m(I=-I_adv, TH=0)
                    if S_adv:
                        y_mods["TS"] = S_adv
                    matrix[(x, y)] = (x_mods, y_mods)

    # ── Post-build overrides ───────────────────────────────────────────────
    # Charge's "high risk" identity: -1 TS for Charge in three downside matchups.
    # Charge is committing forward; when the opponent reads it or evades it,
    # the chargers lose form and take harder hits.
    #
    # (Charge, Scout):                Charge -1 TS (Scout sees the charge coming, dodges the impact)
    # (Charge, Ambush):               Charge -1 TS (Charged into a trap)
    # (Charge, Defensive Formation):  Charge -1 TS (Slammed the wall, lost cohesion)
    #
    # When a matchup is X vs Y where one side is Charge, Charge gets TS=-1 in
    # its own attacker entry. The opponent's entry already encodes the matchup
    # win; we only add the additional defensive penalty for Charge.

    def _apply_charge_ts_penalty(charge_opp):
        """Add TS=-1 to Charge's mods in both directions of (Charge, opp)."""
        # Direction 1: (Charge, opp) — Charge is attacker (x)
        a, b = matrix[("Charge", charge_opp)]
        a["TS"] = a.get("TS", 0) - 1
        matrix[("Charge", charge_opp)] = (a, b)
        # Direction 2: (opp, Charge) — Charge is defender (y)
        a, b = matrix[(charge_opp, "Charge")]
        b["TS"] = b.get("TS", 0) - 1
        matrix[(charge_opp, "Charge")] = (a, b)

    for opp in ["Scout", "Ambush", "Defensive Formation"]:
        _apply_charge_ts_penalty(opp)

    # ── Scout buffs: positional defensive awareness ────────────────────────
    # Scout sees things coming. Even in losing matchups, Scout should bleed
    # less than other tactics would in the same spot. Encoded as a -1 TH
    # penalty on the OPPONENT (they hit Scout less effectively), so each card
    # only shows modifiers affecting that card's own player.
    #
    # (Scout, Charge):              Charge -1 TH against Scout
    # (Scout, Flank):               Flank -1 TH against Scout
    # (Scout, Fighting Formation):  FF -1 TH against Scout

    def _apply_scout_defensive_buff(scout_opp):
        """Penalize opponent's TH against Scout by 1 (Scout dodges incoming hits)."""
        a, b = matrix[("Scout", scout_opp)]
        b["TH"] = b.get("TH", 0) - 1
        matrix[("Scout", scout_opp)] = (a, b)
        a, b = matrix[(scout_opp, "Scout")]
        a["TH"] = a.get("TH", 0) - 1
        matrix[(scout_opp, "Scout")] = (a, b)

    for opp in ["Charge"]:
        _apply_scout_defensive_buff(opp)

    # Flank vs Scout: Flank Quick (+1I); Scout Slow but Fortified (-1I, +1S).
    # Flanker wins the angle, but Scout's positional awareness lets them
    # absorb the strikes. Flank still wins the matchup but pays in casualties;
    # at low/mid tiers, mutual wipe is common.
    matrix[("Flank", "Scout")] = (
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": -1, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
    )
    matrix[("Scout", "Flank")] = (
        {"I": -1, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    # Scout vs FF: Scout gains tempo (+1I, no save penalty); FF loses initiative
    # (-1I) but keeps its accuracy (+1TH). Scout out-positions, FF out-strikes —
    # a trade rather than a hard counter.
    matrix[("Scout", "Fighting Formation")] = (
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": -1, "TH": 1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )
    matrix[("Fighting Formation", "Scout")] = (
        {"I": -1, "TH": 1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    # ── Ambush buffs: prepared positions + surprise vs static ──────────────
    # Ambush works on concealment. In its losing matchups (Scout, Flank), the
    # ambushers are spotted but in prepared positions — better saves cushion
    # the inevitable hits.
    # Ambush vs Defensive Formation was a dead matchup (no mods); add TH+1
    # since static formations are the natural target of an ambush.
    #
    # (Ambush, Scout):                Ambush +1 TS (prepared positions soak hits)
    # (Ambush, Flank):                Ambush +1 TS (concealed positions soak hits)
    # (Ambush, Defensive Formation):  Ambush +1 TH (surprise vs static target)

    def _apply_ambush_ts_buff(ambush_opp):
        """Add TS=+1 to Ambush's mods in both directions of (Ambush, opp)."""
        a, b = matrix[("Ambush", ambush_opp)]
        a["TS"] = a.get("TS", 0) + 1
        matrix[("Ambush", ambush_opp)] = (a, b)
        a, b = matrix[(ambush_opp, "Ambush")]
        b["TS"] = b.get("TS", 0) + 1
        matrix[(ambush_opp, "Ambush")] = (a, b)

    for opp in ["Scout", "Flank", "Fighting Formation"]:
        _apply_ambush_ts_buff(opp)

    # Ambush vs DF: Ambush Clumsy (-1H); DF Fortified (+1S). Ambushers strike
    # against a braced shieldwall — surprise gives no init edge against a
    # formation already prepared for the worst, and hits land sloppy. DF saves
    # better but doesn't strike harder; pure defensive trade.
    matrix[("Ambush", "Defensive Formation")] = (
        {"I": 0, "TH": -1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": 0, "TH": 0,  "TBH": 0, "TS": 1, "end": False, "no_combat": False},
    )
    matrix[("Defensive Formation", "Ambush")] = (
        {"I": 0, "TH": 0,  "TBH": 0, "TS": 1, "end": False, "no_combat": False},
        {"I": 0, "TH": -1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    # ── Defensive Formation buffs (v4/v5) ──────────────────────────────────
    # DF was previously the weakest non-Fall-Back tactic. These changes give
    # it a credible identity as the "stand and absorb" formation:
    #
    # Scout vs DF (v5 revised): Scout +1I; DF -1I, +1TS
    #   Scouts get the initiative, but DF's prepared positions absorb hits.
    #   Pure init swing for Scout, defensive save for DF — no offensive trade.
    #
    # FF vs DF: FF +1TH;  DF +1TS
    #   FF's aggressive line hits more often, but DF's saves blunt the damage.
    #   Net: DF can actually hold the line against committed infantry.
    #
    # Flank vs DF (v5 added): Flank +1I; DF -1I, +1TS
    #   Same shape as Scout vs DF — mobility wins init, but DF saves through it.

    matrix[("Scout", "Defensive Formation")] = (
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": -1, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
    )
    matrix[("Defensive Formation", "Scout")] = (
        {"I": -1, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    matrix[("Fighting Formation", "Defensive Formation")] = (
        {"I": 0, "TH": 1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": 0, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
    )
    matrix[("Defensive Formation", "Fighting Formation")] = (
        {"I": 0, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
        {"I": 0, "TH": 1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    matrix[("Flank", "Defensive Formation")] = (
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": -1, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
    )
    matrix[("Defensive Formation", "Flank")] = (
        {"I": -1, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    # ── Charge vs Fighting Formation (v4) ─────────────────────────────────
    # Previously Charge dominated FF 80/6 with a clean +1 TH advantage. That made
    # FF redundant as an aggressive option — it lost to Charge AND beat little else.
    # New: Charge gets initiative (+1I) but its hits are sloppy (-1TH) crashing into
    # a prepared line. FF strikes back cleanly (+1TH) with its disciplined spear-line.
    # Net: FF flips the matchup at MaA/Sgt tiers; KT-tier Charge still wins via raw
    # stats. FF gets a real identity as the "soft counter to Charge."
    matrix[("Charge", "Fighting Formation")] = (
        {"I": 1,  "TH": -1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": -1, "TH": 1,  "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )
    matrix[("Fighting Formation", "Charge")] = (
        {"I": -1, "TH": 1,  "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": 1,  "TH": -1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    # ── v5 cell overrides: tighten the meta ───────────────────────────────
    # Goal: 6 tactics within ~4 points of each other (32-36% avg win), with
    # Charge/Flank as the high-variance tactics and FF/Scout as the stable middle.
    # Fall Back stays at the structural low end as the battle-ender.

    # Scout vs Charge — Scout sees the charge coming, strikes first. Charge
    # commits hard and lands devastating blows on return — heavy lances and
    # plate connect with full weight on light recon. Scout still wins the
    # matchup (light recon picks the angle) but pays casualties for it.
    matrix[("Scout", "Charge")] = (
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": -1, "TH": 1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )
    matrix[("Charge", "Scout")] = (
        {"I": -1, "TH": 1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    # Ambush vs Flank — Ambush strikes first but its hits are wild against the
    # mobile flanker; Flank loses init but lands cleaner counter-strikes.
    # Result: real contest at all tiers, Ambush takes higher tiers, Flank wins
    # at MaA/Sgt-Halberd.
    matrix[("Ambush", "Flank")] = (
        {"I": 1,  "TH": -1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": -1, "TH": 1,  "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )
    matrix[("Flank", "Ambush")] = (
        {"I": -1, "TH": 1,  "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": 1,  "TH": -1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    # Scout vs Ambush — Scout still wins by reading the trap, but Ambush's
    # prepared positions absorb damage (+1 TS). Down from the old 83/1 blowout
    # to a real 51/14 contest with tier-dependent outcomes.
    matrix[("Scout", "Ambush")] = (
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": -1, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
    )
    matrix[("Ambush", "Scout")] = (
        {"I": -1, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
        {"I": 1,  "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    # ── Mirror overrides ───────────────────────────────────────────────────
    # Scout vs Scout: both Quick (+1I). Two recon forces both move fast — they
    # actually engage and resolve rather than ending indecisively.
    matrix[("Scout", "Scout")] = (
        {"I": 1, "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": 1, "TH": 0, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )
    # Ambush vs Ambush: both Slow but Fortified (-1I, +1S). Two prepared
    # positions cancel concealment — both armies dig in, brace, grind it out.
    matrix[("Ambush", "Ambush")] = (
        {"I": -1, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
        {"I": -1, "TH": 0, "TBH": 0, "TS": 1, "end": False, "no_combat": False},
    )
    # FF vs FF: both Slow but Accurate (-1I, +1H). Two disciplined lines crash
    # into each other, neither pivots, both land cleanly. Decisive grind.
    matrix[("Fighting Formation", "Fighting Formation")] = (
        {"I": -1, "TH": 1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
        {"I": -1, "TH": 1, "TBH": 0, "TS": 0, "end": False, "no_combat": False},
    )

    return matrix


def run_test(label, new_matrix):
    """Replace TACTIC_MATRIX temporarily and run experiments."""
    original = dict(renown_combat.TACTIC_MATRIX)
    renown_combat.TACTIC_MATRIX.clear()
    renown_combat.TACTIC_MATRIX.update(new_matrix)

    random.seed(2026)

    print(f"\n{label}")
    print(f"  {'Era':<12} {'A win':<10} {'B win':<10} {'Indecisive':<12} {'Avg skirm':<11} {'Survivors A/B'}")
    for era_label, retinue, weapon, shield, armor in [
        ("Founding",  "Levy",     "Cudgel",       None,         "Cloth"),
        ("Ascension", "Levy",     "Arming Sword", "Kite Shield", "Leather"),
        ("Eminence",  "Sergeant", "Halberd",      None,         "Chainmail"),
        ("Zenith",    "Sergeant", "Battle Axe",   None,         "Full Plate"),
    ]:
        res = monte_carlo(
            lambda r=retinue, w=weapon, s=shield, a=armor: make_army("A", r, w, s, a, 50),
            lambda r=retinue, w=weapon, s=shield, a=armor: make_army("B", r, w, s, a, 50),
            random_tactic_picker(), random_tactic_picker(),
            n_runs=1000,
        )
        print(f"  {era_label:<12} {res['win_rate_a']:<10.1%} {res['win_rate_b']:<10.1%} "
              f"{res['outcomes']['indecisive']/1000:<12.1%} {res['avg_skirmishes']:<11.1f} "
              f"{res['avg_a_remaining']:.1f}/{res['avg_b_remaining']:.1f}")

    renown_combat.TACTIC_MATRIX.clear()
    renown_combat.TACTIC_MATRIX.update(original)


if __name__ == "__main__":
    print("="*80)
    print("NORMALIZED SYMMETRIC MATRIX")
    print("Each pair has ONE canonical interaction. (X,Y) and (Y,X) describe the same exchange.")
    print("="*80)
    new = build_normalized_matrix()

    # Quick check: matrix is now symmetric
    asymmetries = 0
    for x in TACTICS:
        for y in TACTICS:
            if x >= y: continue
            a_xy, b_xy = new[(x, y)]
            a_yx, b_yx = new[(y, x)]
            for k in ["I", "TH", "TBH", "TS", "end"]:
                if a_xy[k] != b_yx[k] or b_xy[k] != a_yx[k]:
                    asymmetries += 1
                    break
    print(f"\nAsymmetric pairs in new matrix: {asymmetries}")

    run_test("Era results with normalized matrix", new)
