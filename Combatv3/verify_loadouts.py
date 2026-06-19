"""
Local verification: does the optimized loadouts.py produce a pool IDENTICAL to the
pre-perf original? Run this on your machine (kotr env) from the Combatv3 folder:

    python verify_loadouts.py

It reconstructs the ORIGINAL archetype_pool inline (fixpoint closure, no memo, no
domain= passthrough) and diffs the full pool signature against the optimized module
across three configs. Prints IDENTICAL=True/False + timing/speedup for each.
If all three say IDENTICAL=True, the perf rewrite is output-preserving -> ship it.
"""
import time
import loadouts2 as L


# --- ORIGINAL prereq_closure: O(n^2) fixpoint (what the optimized _PREREQ_CLOSURE replaced) ---
def prereq_closure_ORIG(pursuits):
    out = set(pursuits)
    changed = True
    while changed:
        changed = False
        for p in list(out):
            if p not in L.PURSUITS_INFO:
                continue
            for pre in L.PURSUITS_INFO[p].get("prereqs", []):
                if pre in L.PURSUITS_INFO and pre not in out:
                    out.add(pre)
                    changed = True
    return out


def archetype_pool_ORIG(min_pursuit_cost=5, max_pursuit_cost=10,
                        budget_metric="mpc", max_monuments=2):
    """Verbatim pre-perf generator: nested melee fn, per-iteration constants,
    fixpoint closure, no memo, _name called WITHOUT domain=."""
    WEAPONS, RANGED, SHIELDS = L.WEAPONS, L.RANGED, L.SHIELDS
    WEAPONS_BY_TIER = {
        "Crude": ["Cudgel", "Farm Tools"], "Cast": ["Daggers", "Short Sword", "Spears"],
        "Wrought": ["Arming Sword", "Pike", "Flail", "Halberd", "Battle Axe"],
        "Forged": ["Bastard Sword", "2HBastard", "Morningstar", "War Hammer"],
        "Crafted": ["Poleaxe", "Estoc"]}
    RANGED_BY_TIER = {"Crude": ["Hunting Bow"], "Cast": ["Longbow"], "Wrought": ["Javelin"],
                      "Forged": ["Crossbow"], "Crafted": ["Pilum"]}
    INDUSTRY_PATHS = [set(), {"Furnace"}, {"Blacksmith"},
                      {"Blacksmith", "Master Workshop"},
                      {"Blacksmith", "Armory", "Gilded Foundry"},
                      {"Blacksmith", "Forge"},
                      {"Blacksmith", "Forge", "Master Workshop"},
                      {"Blacksmith", "Forge", "Armory", "Gilded Foundry"},
                      {"Blacksmith", "Forge", "Armory", "Gilded Foundry", "Master Workshop"},
                      {"Stable", "Blacksmith", "Forge", "Master Workshop", "Armory",
                       "Gilded Foundry", "ABF"}]
    RETINUE_CHAINS = [frozenset(), frozenset(["Coliseum"]), frozenset(["War College"]),
                      frozenset(["Preceptory", "Preceptory KT", "Hospitaller", "Abbey",
                                 "Monastery", "Pilgrimage Site"])]
    INDEPENDENT_OPTIONS = ["Levy Hall", "Joinery", "Fletchery", "Tiltyard", "Stable",
                           "Royal Pavilion", "Grand Tournament", "Ministry", "Ministry Mastery",
                           "Outrider Intercept Post", "Outrider Mastery", "Tannery", "Armory",
                           "Butchery", "Toxicarium", "Full Hospitaller", "Preceptory", "Abbey"]
    AUTO_INCLUDED = {"Carpentry": ["Joinery", "Fletchery"],
                     "Animal Husbandry": ["Tannery", "Butchery"], "Smokehouse": ["Butchery"],
                     "Coliseum": ["Tiltyard", "Royal Pavilion"], "Tannery": ["Armory"],
                     "Armory": ["Tannery"], "Ministry": ["Ministry Mastery"],
                     "Caravanery": ["Outrider Intercept Post"],
                     "Cipher Chamber": ["Outrider Intercept Post"],
                     "Outrider Intercept Post": ["Outrider Mastery"]}
    seen_keys = {}
    for industry_path in INDUSTRY_PATHS:
        tier_str = L.derive_tier_from_pursuits(industry_path)

        def melee_options_for_tier(t):
            CRAFTED_1H_FALLBACK = ["Bastard Sword", "Morningstar"]
            if t == "Crafted":
                return WEAPONS_BY_TIER["Crafted"] + CRAFTED_1H_FALLBACK
            return WEAPONS_BY_TIER[t]

        for ret_chain in RETINUE_CHAINS:
            for mask in range(1 << len(INDEPENDENT_OPTIONS)):
                opt_set = frozenset(INDEPENDENT_OPTIONS[i]
                                    for i in range(len(INDEPENDENT_OPTIONS)) if mask & (1 << i))
                pursuits = set(ret_chain) | set(opt_set) | set(industry_path)
                if "Full Hospitaller" in pursuits:
                    pursuits.discard("Full Hospitaller")
                    pursuits.update(("Apothecary", "Infirmary", "Hospitaller"))
                for forced, deps in AUTO_INCLUDED.items():
                    if forced == "Armory" and not (
                            "Blacksmith" in pursuits or "Forge" in pursuits or "ABF" in pursuits):
                        continue
                    if any(d in pursuits for d in deps):
                        pursuits.add(forced)
                pursuits = L._normalize_pool_tokens(pursuits)
                pursuits = L.master_effect_closure(prereq_closure_ORIG(pursuits))
                if not L._pursuit_set_is_valid(pursuits):
                    continue
                total_cost, domain, tags = L.compute_pursuit_cost(pursuits)
                retinue_guess = L.derive_retinue_from_pursuits(pursuits)
                budget = len(pursuits) if budget_metric == "total" else total_cost
                if budget > max_pursuit_cost or budget < min_pursuit_cost:
                    continue
                if sum(1 for m in L._POOL_MONUMENTS if m in pursuits) > max_monuments:
                    continue
                has_stable_explicit = "Stable" in opt_set
                has_fletch = "Fletchery" in pursuits
                has_ty = "Tiltyard" in pursuits
                arms_options = []
                if has_stable_explicit and has_ty:
                    arms_options.append(("Lance", None, False))
                    arms_options.append(("Cavalry Spear", None, False))
                    for w in melee_options_for_tier(tier_str):
                        for r in L._ranged_at_or_below(tier_str, RANGED_BY_TIER):
                            arms_options.append((w, r, True))
                elif has_stable_explicit:
                    arms_options.append(("Lance", None, False))
                    arms_options.append(("Cavalry Spear", None, False))
                    for w in melee_options_for_tier(tier_str):
                        arms_options.append((w, None, False))
                elif has_fletch and has_ty:
                    for w in melee_options_for_tier(tier_str):
                        for r in L._ranged_at_or_below(tier_str, RANGED_BY_TIER):
                            arms_options.append((w, r, True))
                elif has_fletch:
                    for r in L._ranged_at_or_below(tier_str, RANGED_BY_TIER):
                        arms_options.append((None, r, False))
                else:
                    for w in melee_options_for_tier(tier_str):
                        arms_options.append((w, None, False))
                dual_wield_weapons = set()
                if has_ty:
                    for w in melee_options_for_tier(tier_str):
                        if w == "Farm Tools" or L.is_2h(w) or w in L.STABLE_WEAPONS:
                            continue
                        arms_options.append((w, None, True))
                        dual_wield_weapons.add(w)
                for weapon, ranged, ty in arms_options:
                    is_two_of_same = (weapon in dual_wield_weapons and ranged is None and ty)
                    SHIELD_LADDER = ["Heater Shield", "Tower Shield", "Scutum Shield",
                                     "Kite Shield", "Wooden Shield"]
                    if ranged == "Crossbow":
                        w_init = WEAPONS[weapon]["init"] if weapon and weapon != "Farm Tools" else 0
                        opts = [None]
                        if (L.shield_satisfied("Tower Shield", pursuits)
                                and w_init + SHIELDS["Tower Shield"]["init"] >= -1):
                            opts.append("Tower Shield")
                        shield_opts = opts
                    elif weapon is None or L.is_2h(weapon) or is_two_of_same:
                        shield_opts = [None]
                    else:
                        w_init = (WEAPONS.get(weapon, {}).get("init", 0)
                                  if weapon and weapon != "Farm Tools"
                                  else (RANGED.get(ranged, {}).get("init", 0) if ranged else 0))
                        best = None
                        for s in SHIELD_LADDER:
                            if not L.shield_satisfied(s, pursuits):
                                continue
                            if w_init + SHIELDS[s]["init"] < -1:
                                continue
                            best = s
                            break
                        shield_opts = [best] if best else [None]
                    ARMOR_LADDER = ["Gothic Plate", "Full Plate", "Chainmail", "Leather", "Cloth"]
                    armor_opts = [next((a for a in ARMOR_LADDER
                                        if L.armor_satisfied(a, pursuits)), "Cloth")]
                    for shield in shield_opts:
                        for armor in armor_opts:
                            if not is_two_of_same and not L.valid_combo(
                                    retinue_guess, weapon or "Farm Tools", shield, armor, ranged, ty):
                                continue
                            if shield is not None and not L.shield_satisfied(shield, pursuits):
                                continue
                            if not L.armor_satisfied(armor, pursuits):
                                continue
                            if ranged is not None and "Fletchery" not in pursuits:
                                continue
                            requires_joinery = (weapon is not None and weapon != "Farm Tools"
                                                and not L.is_2h(weapon) and not is_two_of_same
                                                and ranged != "Crossbow")
                            if requires_joinery and "Joinery" not in pursuits:
                                continue
                            domain_count = sum(domain.values())
                            if domain_count > 30:
                                continue
                            build_tags = set(tags)
                            if is_two_of_same:
                                build_tags.add("Dual Wield")
                            tags_tuple = tuple(sorted(build_tags))
                            obs_key = (retinue_guess, weapon, shield, armor, ranged, ty, tags_tuple)
                            if obs_key in seen_keys and seen_keys[obs_key][0] <= total_cost:
                                continue
                            name = L._name(retinue_guess, weapon, shield, armor, ranged, ty,
                                           sorted(build_tags), playstyle=None, pursuits=pursuits)
                            ld = L.Loadout(
                                name=name, retinue=retinue_guess, weapon=weapon, shield=shield,
                                armor=armor, ranged=ranged, has_tiltyard=ty,
                                size=L.DEFAULT_ARMY_SIZE, extra_tags=sorted(build_tags),
                                upkeep_per_retinue=0, playstyle=None, tiltyard_mastery=True,
                                pursuits=frozenset(pursuits), military_pursuit_count=total_cost,
                                domain_count=domain_count)
                            ld = ld._replace(upkeep_per_retinue=L.compute_effective_upkeep(ld))
                            seen_keys[obs_key] = (total_cost, ld)
    return [v[1] for v in seen_keys.values()]


def sig(pool):
    return sorted((ld.retinue, ld.weapon, ld.shield, ld.armor, ld.ranged, ld.has_tiltyard,
                   tuple(sorted(ld.extra_tags)), ld.upkeep_per_retinue,
                   tuple(sorted(ld.pursuits)), ld.military_pursuit_count, ld.domain_count,
                   ld.name) for ld in pool)


if __name__ == "__main__":
    all_ok = True
    for (mn, mx, bm) in [(5, 10, "mpc"), (3, 20, "total"), (1, 9, "mpc")]:
        t = time.time(); orig = archetype_pool_ORIG(mn, mx, bm); t_o = time.time() - t
        t = time.time()
        opt = L.archetype_pool(min_pursuit_cost=mn, max_pursuit_cost=mx, budget_metric=bm)
        t_n = time.time() - t
        so, sn = sig(orig), sig(opt)
        ident = (so == sn)
        all_ok &= ident
        print(f"[{bm} {mn}-{mx}] orig={len(orig)} opt={len(opt)} IDENTICAL={ident}  "
              f"orig={t_o:.1f}s opt={t_n:.1f}s speedup={t_o/max(t_n,1e-9):.2f}x")
        if not ident:
            os_, ns_ = set(map(tuple, so)), set(map(tuple, sn))
            for x in list(os_ - ns_)[:5]:
                print("   only ORIG:", x[-1])
            for x in list(ns_ - os_)[:5]:
                print("   only OPT :", x[-1])
    print("\n==> SHIP IT" if all_ok else "\n==> DO NOT SHIP — outputs differ")