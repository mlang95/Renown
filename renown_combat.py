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

RETINUES = {
    "Levy":          {"cost": 20, "to_hit": 5, "endurance": 3, "shaking": 4, "unshakable": False},
    "Man-at-Arms":   {"cost": 35, "to_hit": 4, "endurance": 3, "shaking": 3, "unshakable": False},
    "Sergeant":      {"cost": 55, "to_hit": 3, "endurance": 3, "shaking": 2, "unshakable": False},
    "Knight Templar":{"cost": 80, "to_hit": 2, "endurance": 3, "shaking": 0, "unshakable": True},
}

WEAPONS = {
    "Farm Tools":    {"ap": 0,  "init": 0,  "tags": [],                                      "tier": "Crude"},
    "Cudgel":        {"ap": -2, "init": -1, "tags": ["2H", "Unwieldy"],                      "tier": "Crude"},
    "Daggers":       {"ap": 0,  "init": 1,  "tags": ["Nimble", "2H", "Shatter Armor"],        "tier": "Cast"},
    "Short Sword":   {"ap": -1, "init": 0,  "tags": ["Steady", "Nimble"],                    "tier": "Cast"},
    "Spears":        {"ap": -1, "init": 1,  "tags": ["Unwieldy", "Shatter Armor", "Steady"], "tier": "Cast"},
    "Arming Sword":  {"ap": -2, "init": 0,  "tags": ["Steady", "+1TH"],                      "tier": "Wrought"},
    "Pike":          {"ap": -2, "init": 1,  "tags": ["Steady", "Shatter Armor", "2H"],       "tier": "Wrought"},
    "Flail":         {"ap": -2, "init": 0,  "tags": ["Unwieldy", "Cleave"],                  "tier": "Wrought"},
    "Halberd":       {"ap": -3, "init": 0,  "tags": ["2H"],                                  "tier": "Wrought"},
    "Battle Axe":    {"ap": -5, "init": -1, "tags": ["Unstoppable", "2H"],                   "tier": "Wrought"},
    "Bastard Sword": {"ap": -3, "init": 0,  "tags": ["Shatter Armor", "Steady"],             "tier": "Forged"},
    "2HBastard":     {"ap": -3, "init": 0,  "tags": ["Cleave", "2H", "Unwieldy"],            "tier": "Forged"},
    "Lance":         {"ap": -3, "init": 1,  "tags": ["Steady", "Unwieldy", "Shatter Armor"], "tier": "Forged"},
    "Morningstar":   {"ap": -3, "init": -1, "tags": ["Destroy Shield", "Cleave"],            "tier": "Forged"},
    "War Hammer":    {"ap": -8, "init": -1, "tags": ["Unwieldy", "Destroy Shield", "Unstoppable", "2H"],    "tier": "Forged"},
    "Poleaxe":       {"ap": -4, "init": 0,  "tags": ["Steady", "2H", "Unstoppable"],         "tier": "Crafted"},
}

RANGED = {
    "Hunting Bow": {"ap": -1, "init": 2, "tags": ["2H"],                        "tier": "Crude"},
    "Longbow":     {"ap": -3, "init": 2, "tags": ["Shatter Armor", "2H", "+1TH", "Steady"],                "tier": "Cast"},
    "Javelin":     {"ap": -3, "init": 1, "tags": ["Shatter Armor", "Steady", "Unstoppable", "One Shot"],"tier": "Wrought"},
    "Crossbow":    {"ap": -4, "init": 0, "tags": ["Shatter Armor", "Unwieldy"],  "tier": "Forged"},
    "Pilum":       {"ap": -5, "init": 1, "tags": ["Steady", "Destroy Shield", "Unstoppable", "One Shot"],"tier": "Crafted"},
}

SHIELDS = {
    None:             {"save_bonus": 0, "init": 0,  "tags": [],                  "tier": None},
    "Wooden Shield":  {"save_bonus": 1, "init": -1, "tags": [],                  "tier": "Crude"},
    "Kite Shield":    {"save_bonus": 1, "init": 0,  "tags": ["Steady"],          "tier": "Cast"},
    "Scutum Shield":  {"save_bonus": 1, "init": -1, "tags": ["Steady", "-1TBH"], "tier": "Wrought"},
    "Tower Shield":   {"save_bonus": 2, "init": -1, "tags": ["Unwieldy", "-1TBH"], "tier": "Forged"},
    "Heater Shield":  {"save_bonus": 1, "init": 0,  "tags": ["-1TBH", "Immune Destroy Shield"],           "tier": "Crafted"},
}

ARMORS = {
    "Cloth":     {"save": 6, "tier": "Crude",   "tags": []},
    "Leather":   {"save": 5, "tier": "Cast",    "tags": []},
    "Chainmail": {"save": 4, "tier": "Wrought", "tags": []},
    # Heavy plate is slow: Full Plate is too heavy for the Nimble dart-in (Immune Nimble).
    # Gothic adds Immune Steady on top — heaviest armor also loses the Steady "hold your
    # initiative" floor, so it CAN be dragged below base init by enemy tactics. Both tags
    # are no-ops on builds lacking Nimble / Steady respectively.
    "Full Plate":{"save": 3, "tier": "Forged",  "tags": ["Immune Nimble"]},
    "Gothic Plate":{"save": 2, "tier": "Crafted", "tags": ["Immune Steady", "Immune Nimble"]},
}

# Tactic matrix: TACTICS[attacker][defender] = (mods_for_attacker, mods_for_defender)
# Mods dict keys: I (initiative), TH (to_hit), TS (target save), end_battle (bool)
# NOTE: TBH (To Be Hit) was removed in this revision. The new tactic cards express all
# such effects as "+X to Hit" on the active player's own modifier rather than splitting
# the modifier across both players. Shields that previously carried `-1TBH` now simply
# raise the attacker's to-hit target directly (via shield_tbh_penalty_start).
def _m(I=0, TH=0, TS=0, end=False, no_combat=False, endurance_loss=True):
    """Tactic modifier cell.
      I: initiative adjustment (this side's initiative gain)
      TH: to-hit adjustment (this side's to-hit improvement; lower target = better)
      TS: save-target adjustment (this side's save improvement; lower target = better)
      end: battle terminates (indecisive outcome unless one side already wiped).
      no_combat: this skirmish has no engagement (no strikes, no shake, no rout).
      endurance_loss: only meaningful when no_combat=True. If True, armies still spend
        endurance this skirmish (Flank/Flank: maneuvering tires the troops).
        If False, no_combat skirmishes are completely free (n/a in current card set).
    """
    return {"I": I, "TH": TH, "TS": TS,
            "end": end, "no_combat": no_combat, "endurance_loss": endurance_loss}

# Tactic matrix transcribed verbatim from tactic_cards.pdf. Format is the card-holder's
# perspective: (A_tactic, B_tactic) -> (A's gains/penalties, B's gains/penalties).
# All values express the named side's own modifier (not opponent-relative).
TACTIC_MATRIX = {
    # ── Scout's row ──
    ("Scout", "Scout"):                       (_m(I=1),                _m(I=1)),
    ("Scout", "Ambush"):                      (_m(I=1),                _m(I=-1, TS=1)),
    ("Scout", "Flank"):                       (_m(I=-1, TS=1),         _m(I=1)),
    ("Scout", "Charge"):                      (_m(I=1),                _m(I=-1, TH=1)),
    ("Scout", "Fighting Formation"):          (_m(I=1),                _m(I=-1, TH=1)),
    ("Scout", "Defensive Formation"):         (_m(I=1),                _m(I=-1, TS=1)),
    ("Scout", "Fall Back"):                   (_m(end=True),           _m(end=True)),

    # ── Ambush's row ──
    ("Ambush", "Scout"):                      (_m(I=-1, TS=1),         _m(I=1)),
    ("Ambush", "Ambush"):                     (_m(I=-1, TS=1),         _m(I=-1, TS=1)),
    ("Ambush", "Flank"):                      (_m(I=1, TH=-1),         _m(I=-1, TH=1)),
    ("Ambush", "Charge"):                     (_m(I=1, TH=1),          _m(I=-1, TS=-1)),
    ("Ambush", "Fighting Formation"):         (_m(I=1, TS=1),          _m(I=-1)),
    ("Ambush", "Defensive Formation"):        (_m(TH=-1),              _m(TS=1)),
    ("Ambush", "Fall Back"):                  (_m(end=True),           _m(end=True)),

    # ── Flank's row ──
    ("Flank", "Scout"):                       (_m(I=1),                _m(I=-1, TS=1)),
    ("Flank", "Ambush"):                      (_m(I=-1, TH=1),         _m(I=1, TH=-1)),
    ("Flank", "Flank"):                       (_m(no_combat=True, endurance_loss=True),
                                                _m(no_combat=True, endurance_loss=True)),
    ("Flank", "Charge"):                      (_m(I=-1),               _m(I=1)),
    ("Flank", "Fighting Formation"):          (_m(I=1, TH=1),          _m(I=-1)),
    ("Flank", "Defensive Formation"):         (_m(I=1),                _m(I=-1, TS=1)),
    ("Flank", "Fall Back"):                   (_m(I=-1),               _m(I=1, TH=1)),

    # ── Charge's row ──
    ("Charge", "Scout"):                      (_m(I=-1, TH=1),         _m(I=1)),
    ("Charge", "Ambush"):                     (_m(I=-1, TS=-1),        _m(I=1, TH=1)),
    ("Charge", "Flank"):                      (_m(I=1),                _m(I=-1)),
    ("Charge", "Charge"):                     (_m(TH=1),               _m(TH=1)),
    ("Charge", "Fighting Formation"):         (_m(I=1, TH=-1),         _m(I=-1, TH=1)),
    ("Charge", "Defensive Formation"):        (_m(I=-1, TS=-1),        _m(I=1, TH=1, TS=1)),
    ("Charge", "Fall Back"):                  (_m(I=1, TH=1),          _m(I=-1)),

    # ── Fighting Formation's row ──
    ("Fighting Formation", "Scout"):          (_m(I=-1, TH=1),         _m(I=1)),
    ("Fighting Formation", "Ambush"):         (_m(I=-1),               _m(I=1, TS=1)),
    ("Fighting Formation", "Flank"):          (_m(I=-1),               _m(I=1, TH=1)),
    ("Fighting Formation", "Charge"):         (_m(I=-1, TH=1),         _m(I=1, TH=-1)),
    ("Fighting Formation", "Fighting Formation"): (_m(I=-1, TH=1),     _m(I=-1, TH=1)),
    ("Fighting Formation", "Defensive Formation"): (_m(TH=1),          _m(TS=1)),
    ("Fighting Formation", "Fall Back"):      (_m(TH=1),               _m()),

    # ── Defensive Formation's row ──
    ("Defensive Formation", "Scout"):         (_m(I=-1, TS=1),         _m(I=1)),
    ("Defensive Formation", "Ambush"):        (_m(TS=1),               _m(TH=-1)),
    ("Defensive Formation", "Flank"):         (_m(I=-1, TS=1),         _m(I=1)),
    ("Defensive Formation", "Charge"):        (_m(I=1, TH=1, TS=1),    _m(I=-1, TS=-1)),
    ("Defensive Formation", "Fighting Formation"): (_m(TS=1),          _m(TH=1)),
    ("Defensive Formation", "Defensive Formation"): (_m(TS=1),         _m(TS=1)),
    ("Defensive Formation", "Fall Back"):     (_m(end=True),           _m(end=True)),

    # ── Fall Back's row ──
    ("Fall Back", "Scout"):                   (_m(end=True),           _m(end=True)),
    ("Fall Back", "Ambush"):                  (_m(end=True),           _m(end=True)),
    ("Fall Back", "Flank"):                   (_m(I=1, TH=1),          _m(I=-1)),
    ("Fall Back", "Charge"):                  (_m(I=-1),               _m(I=1, TH=1)),
    ("Fall Back", "Fighting Formation"):      (_m(),                   _m(TH=1)),
    ("Fall Back", "Defensive Formation"):     (_m(end=True),           _m(end=True)),
    ("Fall Back", "Fall Back"):               (_m(end=True),           _m(end=True)),
}

TACTICS = ["Scout", "Ambush", "Flank", "Charge", "Fighting Formation", "Defensive Formation", "Fall Back"]


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
        Tiltyard rules: melee + ranged both equipped; One Shot ranged fires first skirmish only, melee thereafter.
        Without Tiltyard, the dual-equip incurs Unwieldy on both weapons (handled in all_tags).
        """
        if self.ranged and first_skirmish:
            return ("ranged", self.ranged)
        return ("melee", self.weapon)

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
    """Roll 1 die per retinue in remaining field; each roll BELOW shaking value = casualty."""
    tags = army.all_tags(False)
    if army.unshakable() or "Unshakable" in tags:
        return 0
    if "Steadfast" in tags:
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
