"""
Renown combat simulator.

Models a Skirmish:
  - tactics chosen (face-down), revealed simultaneously
  - initiative computed (weapon + tactic mods + keywords)
  - higher initiative side strikes first (sequential); ties strike simultaneously
  - rolls-to-hit: 1 die per retinue in front line (max 20), needs >= to_hit
  - rolls-to-save: 1 die per strike, needs >= (armor_save - AP + shield_bonus)
  - keyword interactions resolved
  - end of skirmish: -1 endurance (unless Drilled+first), fatigue tokens, shaking tests

Battle: loop skirmishes until withdrawal/wipe/flee.
"""

import random
from dataclasses import dataclass, field
from typing import Optional


# ---------- Static data ----------

# renown_data — single source of truth (CSV/0.4.8 branch, card-verified)
# Edit THIS file; equipment.csv, cards, and docs are generated from it.

# ── Keyword constants ─────────────────────────────────────────────────────
# Rename a keyword here and it renames everywhere (GLOSSARY keys, tags, cards).
# renown_data — single source of truth (CSV/0.4.8 branch, card-verified)
# Edit THIS file; equipment.csv, cards, and docs are generated from it.

# ── Keyword constants ─────────────────────────────────────────────────────
# Rename a keyword here and it renames everywhere (GLOSSARY keys, tags, cards).
from renown_data import (
    RETINUES, WEAPONS, RANGED, SHIELDS, ARMORS,
    TACTIC_MATRIX, TACTICS,
    STEADY, UNWIELDY, TWO_H, SHATTER_ARMOR, UNSTOPPABLE, CLEAVE, POISON,
    NIMBLE, DRILLED, DESTROY_SHIELD, BLUNDER, ONE_SHOT, DEFLECT,
    IMMUNE_PANIC, UNBREAKABLE, PARRY, RIPOSTE, RECOVER, SERRATED, STRAIN,
    MINUS_1_TBH, PLANISHING, GLOSSARY,
)

# ---------- Army definition ----------

@dataclass
class Army:
    name: str
    retinue: str
    weapon: str
    shield: Optional[str]
    armor: str
    size: int  # current retinue count
    # Tiltyard dual-wield support
    ranged: Optional[str] = None  # secondary ranged weapon; One Shot weapons used round 1 only
    has_tiltyard: bool = False    # negates dual-wield Unwieldy penalty
    is_attacker: bool = False     # army that declared the Skirmish gets +1I on first skirmish (bypasses Unwieldy)
    # Extras
    extra_tags: list = field(default_factory=list)  # army-level keywords from specs
    # Battle state
    endurance: int = 0
    fatigue: int = 0
    skirmish_count: int = 0
    spent: bool = False  # withdrew/wiped/fled
    ranged_used: bool = False      # ranged weapon already fired this battle (one use)
    _ranged_active: bool = False   # set per-skirmish by decide_ranged(); read by active_weapon

    def __post_init__(self):
        if self.endurance == 0:
            self.endurance = RETINUES[self.retinue]["endurance"]

    def to_hit(self):
        return RETINUES[self.retinue]["to_hit"]

    def shaking(self):
        return RETINUES[self.retinue]["shaking"]

    def unshakable(self):
        return RETINUES[self.retinue]["unshakable"]

    def armor_save(self):
        return ARMORS[self.armor]["save"]

    def shield_bonus(self):
        if self.shield is None:
            return 0
        return SHIELDS[self.shield]["save_bonus"]

    def active_weapon(self, first_skirmish: bool):
        """Which weapon profile is active this skirmish.
        The firing decision is made ONCE per skirmish by decide_ranged() (which has the
        opponent in scope) and cached in self._ranged_active. This method just reads it,
        so all the downstream per-skirmish methods stay opponent-free.
        Ranged timing rules:
          - One Shot (Javelin, Crossbow, Pilum): fire in the FIRST skirmish only, then melee.
          - Non-One-Shot (Hunting Bow, Longbow): ONE use per battle, fired on the first skirmish
            where the bow would flip initiative (melee_init <= opp_init < bow_init); melee otherwise.
        """
        if self.ranged and self._ranged_active:
            return ("ranged", self.ranged)
        return ("melee", self.weapon)

    def _ranged_is_one_shot(self):
        if not self.ranged:
            return False
        return "One Shot" in RANGED[self.ranged].get("tags", [])

    def _base_init_with(self, kind: str, first_skirmish: bool):
        """Base (pre-tactic) clamped initiative if this army fought with the given weapon
        kind ('melee' or 'ranged') this skirmish. Mirrors base_initiative's bonuses but lets
        us compare the melee vs ranged profile without committing _ranged_active first."""
        if kind == "ranged" and self.ranged:
            prof = RANGED[self.ranged]
        else:
            prof = WEAPONS[self.weapon]
            kind = "melee"
        i = prof["init"] + self.shield_init()
        # Nimble / attacker bonuses apply regardless of which weapon is up.
        if "Nimble" in set(self.extra_tags) and first_skirmish:
            i += 1
        if self.is_attacker and first_skirmish:
            i += 1
        return max(-2, min(2, i))

    def decide_ranged(self, opponent: "Army", first_skirmish: bool):
        """Set self._ranged_active for THIS skirmish, consuming the ranged weapon if fired.
        Called once at skirmish start, before tactics/initiative resolution.
          - No ranged, or already used  -> melee.
          - One Shot                    -> active iff first_skirmish.
          - Bow (1 use/battle)          -> active iff melee_init <= opp_init < bow_init
                                           (all base, clamped, pre-tactic). Once fired, spent.
        """
        self._ranged_active = False
        if not self.ranged or self.ranged_used:
            return
        if self._ranged_is_one_shot():
            if first_skirmish:
                self._ranged_active = True
                self.ranged_used = True
            return
        # Non-One-Shot bow: fire only on the skirmish where it strictly flips initiative.
        melee_init = self._base_init_with("melee", first_skirmish)
        bow_init = self._base_init_with("ranged", first_skirmish)
        opp_init = opponent._base_init_with("melee", first_skirmish)
        if melee_init <= opp_init < bow_init:
            self._ranged_active = True
            self.ranged_used = True

    def weapon_profile(self, first_skirmish: bool):
        kind, name = self.active_weapon(first_skirmish)
        if kind == "ranged":
            return RANGED[name]
        return WEAPONS[name]

    def weapon_ap(self, first_skirmish: bool = False):
        return self.weapon_profile(first_skirmish)["ap"]

    def weapon_init(self, first_skirmish: bool = False):
        return self.weapon_profile(first_skirmish)["init"]

    def shield_init(self):
        if self.shield is None:
            return 0
        return SHIELDS[self.shield]["init"]

    def all_tags(self, first_skirmish: bool = False):
        tags = set(self.weapon_profile(first_skirmish)["tags"]) | set(self.extra_tags)
        if self.shield is not None:
            tags |= set(SHIELDS[self.shield]["tags"])
        # Dual-wield Unwieldy if both melee and ranged are equipped without Tiltyard
        if self.ranged and self.weapon and not self.has_tiltyard:
            if "Immune Unwieldy" not in self.extra_tags:
                tags.add("Unwieldy")
        if "Immune Unwieldy" in self.extra_tags:
            tags.discard("Unwieldy")
        return tags

    def base_initiative(self, first_skirmish: bool):
        i = self.weapon_init(first_skirmish) + self.shield_init()
        tags = self.all_tags(first_skirmish)
        if "Nimble" in tags and first_skirmish:
            i += 1
        # Skirmish-initiator bonus: +1I on the first skirmish regardless of Unwieldy
        if self.is_attacker and first_skirmish:
            i += 1
        return i

    def front_line(self):
        return min(20, self.size)

    def reserves(self):
        return min(5, max(0, self.size - 20))

    def field(self):
        return min(25, self.size)


# ---------- Combat resolution ----------

def resolve_initiative(a: Army, b: Army, a_tactic: str, b_tactic: str, first_skirmish: bool):
    """Return final initiative for each side after weapon + tactic mods, respecting Steady/Unwieldy."""
    base_a = a.base_initiative(first_skirmish)
    base_b = b.base_initiative(first_skirmish)
    a_mods, b_mods = TACTIC_MATRIX[(a_tactic, b_tactic)]

    # Steady/Unwieldy constraints — but Unwieldy does NOT block the attacker-initiator's first-skirmish +1I
    def apply_init(army: Army, base: int, mod: int):
        tags = army.all_tags(first_skirmish)
        if mod < 0 and "Steady" in tags:
            mod = 0
        if mod > 0 and "Unwieldy" in tags:
            mod = 0
        return base + mod

    a_init = apply_init(a, base_a, a_mods["I"])
    b_init = apply_init(b, base_b, b_mods["I"])
    a_init = max(-2, min(2, a_init))
    b_init = max(-2, min(2, b_init))
    return a_init, b_init, a_mods, b_mods


def roll_to_hit_and_save(attacker: Army, defender: Army, atk_mods, def_mods, first_skirmish: bool, override_front=None):
    """One side rolls to hit; defender rolls to save. Returns casualties dealt to defender.
    override_front: if set, use this as the attacker's front line size (for within-skirmish tracking)."""
    th_mod = atk_mods["TH"]
    fatigue_mod = attacker.fatigue

    base_th = attacker.to_hit()
    target_th = base_th - th_mod + fatigue_mod

    if target_th > 6:
        return 0
    if target_th < 2:
        target_th = 2

    front = override_front if override_front is not None else attacker.front_line()
    if front <= 0:
        return 0

    atk_tags = attacker.all_tags(first_skirmish)

    strikes = 0
    shatter_strikes = 0
    cleave_extra = 0
    destroyed_shield = False

    for _ in range(front):
        roll = random.randint(1, 6)
        if roll >= target_th:
            strikes += 1
            if roll == 6:
                if "Shatter Armor" in atk_tags:
                    shatter_strikes += 1
                if "Cleave" in atk_tags:
                    cleave_extra += 1
                if "Destroy Shield" in atk_tags and defender.shield is not None and not destroyed_shield:
                    destroyed_shield = True
        elif roll == 1:
            pass

    strikes += cleave_extra

    if destroyed_shield:
        defender.shield = None

    base_save = defender.armor_save()
    ap = attacker.weapon_ap(first_skirmish)
    save_target = base_save - ap
    save_target -= defender.shield_bonus() if not destroyed_shield else 0
    save_target += atk_mods["TS"]
    save_target -= def_mods["TS"]

    def_tags = defender.all_tags(first_skirmish)

    casualties = 0
    for i in range(strikes):
        is_shatter = i < shatter_strikes
        if is_shatter:
            failed = True
            roll = None
        else:
            if save_target > 6:
                failed = True
                roll = None
            elif save_target < 2:
                if "Poison" in atk_tags:
                    roll = random.randint(1, 6)
                    failed = (roll == 6)
                else:
                    failed = False
                    roll = None
            else:
                roll = random.randint(1, 6)
                if "Poison" in atk_tags and roll == 6:
                    failed = True
                else:
                    failed = roll < save_target

        if failed:
            if "Parry" in def_tags:
                if random.randint(1, 6) >= 5:
                    continue
            # Regenerate: tier from tags. "Regenerate" / "Regenerate 6" = 6+, "Regenerate 5" = 5+, "Regenerate 4" = 4+
            regen_threshold = None
            for t in def_tags:
                if t == "Regenerate" or t == "Regenerate 6":
                    regen_threshold = 6 if regen_threshold is None else min(regen_threshold, 6)
                elif t == "Regenerate 5":
                    regen_threshold = 5 if regen_threshold is None else min(regen_threshold, 5)
                elif t == "Regenerate 4":
                    regen_threshold = 4 if regen_threshold is None else min(regen_threshold, 4)
            if regen_threshold is not None:
                r = random.randint(1, 6)
                saved = r >= regen_threshold
                if not saved and "Regenerate Reroll" in def_tags:
                    saved = random.randint(1, 6) >= regen_threshold
                if saved:
                    continue
            casualties += 1

    # Cap casualties at defender's front line (within-skirmish tracked, else fall back to size-based)
    def_front = getattr(defender, "_sk_front", defender.front_line())
    casualties = min(casualties, def_front)
    return casualties


def shaking_test(army: Army):
    """Roll 1 die per retinue in remaining field; each roll BELOW shaking value = casualty.
    Unshakable = Immune Shaken (exempt here). Steadfast = Immune Waver ONLY — it does NOT
    exempt the Shaken test. (NOTE: this reference engine has no Waver test; production
    engines implement it.)"""
    tags = army.all_tags(False)
    if army.unshakable() or "Unshakable" in tags:
        return 0
    field = army.field()
    casualties = 0
    sv = army.shaking()
    for _ in range(field):
        roll = random.randint(1, 6)
        if roll < sv:
            casualties += 1
    return casualties


def run_skirmish(a: Army, b: Army, a_tactic: str, b_tactic: str, first_skirmish: bool, verbose=False):
    """Run a single skirmish. Returns dict with results."""
    # Decide ranged firing FIRST (needs opponent, must precede initiative/weapon reads).
    # Each army's call only reads the opponent's MELEE base init, so order doesn't matter.
    a.decide_ranged(b, first_skirmish)
    b.decide_ranged(a, first_skirmish)

    a_init, b_init, a_mods, b_mods = resolve_initiative(a, b, a_tactic, b_tactic, first_skirmish)

    result = {
        "a_init": a_init, "b_init": b_init,
        "a_tactic": a_tactic, "b_tactic": b_tactic,
        "a_casualties": 0, "b_casualties": 0,
        "ended": False,
    }

    # End-battle tactic outcomes
    if a_mods.get("end") and b_mods.get("end"):
        result["ended"] = True
        if verbose: print(f"  [Skirmish] Both tactics end the battle.")
        return result

    # Tripped: init -2 cannot fight this skirmish
    a_can_fight = a_init > -2
    b_can_fight = b_init > -2

    if verbose:
        print(f"  [Skirmish] {a.name}({a_tactic}, I={a_init}) vs {b.name}({b_tactic}, I={b_init})")

    # Within a skirmish, casualties from the first strike reduce the defender's available front line
    # for their back strike. Reserves (up to 5) automatically refill.
    # Track an effective_front_line per army that resets at skirmish start.
    a._sk_front = min(20, a.size)
    a._sk_reserves = min(5, max(0, a.size - 20))
    b._sk_front = min(20, b.size)
    b._sk_reserves = min(5, max(0, b.size - 20))

    def apply_casualties(target, cas):
        # Remove casualties from front line first; reserves refill automatically.
        target._sk_front = max(0, target._sk_front - cas)
        # Refill from reserves
        needed = 20 - target._sk_front
        refill = min(needed, target._sk_reserves)
        target._sk_front += refill
        target._sk_reserves -= refill
        target.size = max(0, target.size - cas)

    if a_init > b_init:
        if a_can_fight:
            b_cas = roll_to_hit_and_save(a, b, a_mods, b_mods, first_skirmish, override_front=a._sk_front)
            apply_casualties(b, b_cas)
            result["b_casualties"] = b_cas
        if b_can_fight and b.size > 0:
            a_cas = roll_to_hit_and_save(b, a, b_mods, a_mods, first_skirmish, override_front=b._sk_front)
            apply_casualties(a, a_cas)
            result["a_casualties"] = a_cas
    elif b_init > a_init:
        if b_can_fight:
            a_cas = roll_to_hit_and_save(b, a, b_mods, a_mods, first_skirmish, override_front=b._sk_front)
            apply_casualties(a, a_cas)
            result["a_casualties"] = a_cas
        if a_can_fight and a.size > 0:
            b_cas = roll_to_hit_and_save(a, b, a_mods, b_mods, first_skirmish, override_front=a._sk_front)
            apply_casualties(b, b_cas)
            result["b_casualties"] = b_cas
    else:
        # Simultaneous: both strike with their starting front line
        if a_can_fight:
            b_cas = roll_to_hit_and_save(a, b, a_mods, b_mods, first_skirmish, override_front=a._sk_front)
        else:
            b_cas = 0
        if b_can_fight:
            a_cas = roll_to_hit_and_save(b, a, b_mods, a_mods, first_skirmish, override_front=b._sk_front)
        else:
            a_cas = 0
        apply_casualties(a, a_cas)
        apply_casualties(b, b_cas)
        result["a_casualties"] = a_cas
        result["b_casualties"] = b_cas

    a.size = max(0, a.size)
    b.size = max(0, b.size)
    a.skirmish_count += 1
    b.skirmish_count += 1

    # End of skirmish: -1 endurance, unless Drilled+first
    for army in [a, b]:
        if army.size <= 0:
            continue
        loses_end = True
        if "Drilled" in army.all_tags(first_skirmish) and first_skirmish:
            loses_end = False
        if army.fatigue > 0:
            # already fatigued: don't lose endurance, gain fatigue
            army.fatigue += 1
        elif loses_end:
            army.endurance -= 1
            if army.endurance <= 0:
                # become fatigued: shaking test
                army.fatigue = 1
                shake_cas = shaking_test(army)
                army.size = max(0, army.size - shake_cas)
                if verbose:
                    print(f"    {army.name} fatigued! Shaking test: {shake_cas} fled.")

    if verbose:
        print(f"    Casualties: {a.name} -{result['a_casualties']} (now {a.size}), {b.name} -{result['b_casualties']} (now {b.size})")
        print(f"    Endurance: {a.name}={a.endurance}({a.fatigue}f), {b.name}={b.endurance}({b.fatigue}f)")

    return result


def fixed_tactic_picker(tactic: str):
    """Return a picker that always picks the given tactic."""
    return lambda army, opp, first: tactic


def random_tactic_picker():
    """Pick a random tactic each skirmish."""
    return lambda army, opp, first: random.choice(TACTICS)


def smart_tactic_picker():
    """Heuristic: pick based on relative strength."""
    def pick(army, opp, first):
        # Simple heuristic: if outnumbered, prefer Defensive Formation; if even, Fighting Formation; if winning, Charge
        ratio = army.size / max(1, opp.size)
        if ratio < 0.7:
            return random.choice(["Defensive Formation", "Fall Back", "Ambush"])
        elif ratio > 1.3:
            return random.choice(["Charge", "Flank", "Fighting Formation"])
        else:
            return random.choice(["Fighting Formation", "Charge", "Flank", "Ambush"])
    return pick


def run_battle(a: Army, b: Army, a_picker, b_picker, max_skirmishes=20, verbose=False):
    """Run a battle until withdrawal/wipe/end-tactic/limit."""
    skirmish_results = []
    for i in range(max_skirmishes):
        first = (i == 0)
        if a.size <= 0 or b.size <= 0:
            break
        a_tac = a_picker(a, b, first)
        b_tac = b_picker(b, a, first)
        result = run_skirmish(a, b, a_tac, b_tac, first, verbose=verbose)
        skirmish_results.append(result)
        if result.get("ended"):
            break
        if a.size <= 0 or b.size <= 0:
            break

    # Determine outcome
    if a.size <= 0 and b.size <= 0:
        outcome = "mutual_wipe"
    elif a.size <= 0:
        outcome = "b_wins"
    elif b.size <= 0:
        outcome = "a_wins"
    else:
        outcome = "indecisive"

    return {
        "outcome": outcome,
        "skirmishes": len(skirmish_results),
        "a_remaining": a.size,
        "b_remaining": b.size,
        "a_endurance": a.endurance,
        "b_endurance": b.endurance,
        "a_fatigue": a.fatigue,
        "b_fatigue": b.fatigue,
        "details": skirmish_results,
    }


# ---------- Monte Carlo runner ----------

def make_army(name, retinue, weapon, shield, armor, size, extra_tags=None,
              ranged=None, has_tiltyard=False, is_attacker=False):
    return Army(
        name=name, retinue=retinue, weapon=weapon, shield=shield, armor=armor,
        size=size, extra_tags=extra_tags or [],
        ranged=ranged, has_tiltyard=has_tiltyard, is_attacker=is_attacker,
    )


def monte_carlo(a_factory, b_factory, a_picker, b_picker, n_runs=1000, max_skirmishes=20):
    outcomes = {"a_wins": 0, "b_wins": 0, "mutual_wipe": 0, "indecisive": 0}
    skirmish_counts = []
    a_remaining = []
    b_remaining = []
    for _ in range(n_runs):
        a = a_factory()
        b = b_factory()
        result = run_battle(a, b, a_picker, b_picker, max_skirmishes=max_skirmishes, verbose=False)
        outcomes[result["outcome"]] += 1
        skirmish_counts.append(result["skirmishes"])
        a_remaining.append(result["a_remaining"])
        b_remaining.append(result["b_remaining"])

    return {
        "outcomes": outcomes,
        "win_rate_a": outcomes["a_wins"] / n_runs,
        "win_rate_b": outcomes["b_wins"] / n_runs,
        "avg_skirmishes": sum(skirmish_counts) / n_runs,
        "median_skirmishes": sorted(skirmish_counts)[n_runs // 2],
        "max_skirmishes": max(skirmish_counts),
        "min_skirmishes": min(skirmish_counts),
        "avg_a_remaining": sum(a_remaining) / n_runs,
        "avg_b_remaining": sum(b_remaining) / n_runs,
    }


if __name__ == "__main__":
    # Quick sanity check
    random.seed(42)
    a = make_army("A: Sergeants/Halberd/Chain", "Sergeant", "Halberd", None, "Chainmail", 50)
    b = make_army("B: Levy/Cudgel/Cloth", "Levy", "Cudgel", None, "Cloth", 50)
    res = run_battle(a, b, fixed_tactic_picker("Fighting Formation"), fixed_tactic_picker("Fighting Formation"), verbose=True)
    print(f"\nOutcome: {res['outcome']}, skirmishes: {res['skirmishes']}, A: {res['a_remaining']}, B: {res['b_remaining']}")