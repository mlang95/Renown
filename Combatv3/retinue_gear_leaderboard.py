# ============================================================================
# Renown — top equipment builds per retinue × gear style
# ----------------------------------------------------------------------------
# Vanilla pool (NO monuments/masteries) so the only thing varying is GEAR.
# Each build is scored by win-rate vs a BALANCED GAUNTLET: one opponent per
# (retinue × archetype), so the field isn't skewed toward common builds.
# Knobs: equipment lists below, N_RUNS (noise), TOPK (bars per cell).
# To compare REAL builds instead of bare gear, pass tag_sets=(("Ministry...",),)
# into generate_loadouts.
# ============================================================================
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, matplotlib
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
import loadouts as L, batch_engine as be
from renown_data import WEAPONS, DUAL_WIELD

# ---------- config ----------
RETS        = ["Levy", "Man-at-Arms", "Sergeant", "Knight Templar"]
ARMORS_USE  = ["Leather", "Chainmail", "Full Plate"]
SHIELDS_USE = [None, "Buckler Shield", "Targe Shield", "Kite Shield", "Tower Shield", "Heater Shield"]
WEAPONS_USE = ["Farm Tools",                                        # no-melee placeholder (Pure Ranged)
               "Arming Sword", "Spears", "Flail", "Estoc",          # 1H
               "Halberd", "Poleaxe", "Battle Axe", "War Hammer",    # 2H
               "Daggers"]                                           # Dual Wield (intrinsic)
RANGED_USE  = [None, "Longbow", "Crossbow"]
ARCHES      = ["2H", "1H+Shield", "Dual Wield", "Pure Ranged", "Tiltyard R+M"]
N_RUNS, SEED, TOPK = 100, 2026, 5

# ---------- pool ----------
pool = L.generate_loadouts(retinue_options=RETS, weapon_options=WEAPONS_USE,
        shield_options=SHIELDS_USE, armor_options=ARMORS_USE,
        ranged_options=RANGED_USE, tiltyard_options=(False, True))

def is_dw(ld):
    return DUAL_WIELD in WEAPONS.get(ld.weapon, {}).get("tags", []) or DUAL_WIELD in (ld.extra_tags or [])
def archetype(ld):
    has_r, has_m = ld.ranged is not None, ld.weapon not in (None, "Farm Tools")
    if has_r and has_m and ld.has_tiltyard: return "Tiltyard R+M"
    if has_r and not has_m:                 return "Pure Ranged"
    if is_dw(ld):                           return "Dual Wield"
    if L.is_2h(ld.weapon):                  return "2H"
    if ld.shield is not None:               return "1H+Shield"
    return "1H bare"

arts = [archetype(l) for l in pool]
keep = [i for i, a in enumerate(arts) if a in ARCHES]
pool = [pool[i] for i in keep]; arts = [arts[i] for i in keep]

ABBR = {"Cloth": "Cl", "Leather": "Lth", "Chainmail": "Chn", "Full Plate": "FP", "Gothic Plate": "Gth"}
def label(ld):
    p = []
    if ld.ranged: p.append(ld.ranged)
    if ld.weapon and ld.weapon != "Farm Tools": p.append(ld.weapon)
    if ld.shield: p.append("+" + ld.shield.split()[0])
    return (" ".join(p) or "—") + f" · {ABBR.get(ld.armor, ld.armor)}" + (" TY" if ld.has_tiltyard else "")

df = pd.DataFrame({"retinue": [b.retinue for b in pool], "archetype": arts,
                   "label": [label(b) for b in pool]})

# ---------- balanced gauntlet: 1 opponent per (retinue × archetype) ----------
field_idx = [g.sample(1, random_state=SEED).index[0] for _, g in df.groupby(["retinue", "archetype"])]
field = [pool[i] for i in field_idx]
pairs = [(b, f) for b in pool for f in field]
res = be.run_batch_random(pairs, n_runs=N_RUNS, seed=SEED, mode="random")
aw = np.asarray(res["a_wins"]).reshape(len(pool), len(field))
selfm = np.array([[b is f for f in field] for b in pool])
df["wr"] = np.where(selfm, 0, aw).sum(1) / np.maximum(np.where(selfm, 0, N_RUNS).sum(1), 1)

top = df.sort_values("wr", ascending=False).groupby(["retinue", "archetype"]).head(TOPK)
piv = top.groupby(["retinue", "archetype"])["wr"].mean().unstack("archetype").reindex(index=RETS, columns=ARCHES)
print(f"pool={len(pool)}  field={len(field)}  pairs={len(pairs)}")

# ---------- figure: heatmap header + small-multiples bar grid ----------
norm = Normalize(0.15, 0.85); cmap = matplotlib.colormaps["RdYlGn"]
fig = plt.figure(figsize=(20, 13))
gs = GridSpec(len(RETS) + 1, len(ARCHES), height_ratios=[0.85] + [1] * len(RETS), hspace=0.6, wspace=0.32)

axh = fig.add_subplot(gs[0, :])
axh.imshow(piv.values, cmap=cmap, norm=norm, aspect="auto")
axh.set_xticks(range(len(ARCHES))); axh.set_xticklabels(ARCHES, fontsize=10)
axh.set_yticks(range(len(RETS)));   axh.set_yticklabels(RETS, fontsize=10)
axh.set_title("Mean win-rate of the top-5 builds  ·  retinue × gear style", fontsize=13, weight="bold", pad=8)
for i in range(len(RETS)):
    for j in range(len(ARCHES)):
        v = piv.values[i, j]
        if not np.isnan(v): axh.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=11, weight="bold")

for ri, ret in enumerate(RETS):
    for aj, arch in enumerate(ARCHES):
        ax = fig.add_subplot(gs[ri + 1, aj])
        sub = top[(top.retinue == ret) & (top.archetype == arch)].sort_values("wr")
        if len(sub):
            y = list(range(len(sub)))
            ax.barh(y, sub.wr.values, color=[cmap(norm(v)) for v in sub.wr], edgecolor="white", lw=0.5)
            ax.set_yticks(y); ax.set_yticklabels(sub.label.values, fontsize=7)
            for k, v in enumerate(sub.wr.values): ax.text(min(v + 0.01, 0.85), k, f"{v:.0%}", va="center", fontsize=7)
            ax.axvline(0.5, color="0.4", lw=0.6, ls="--")
        else:
            ax.text(0.5, 0.5, "none", ha="center", va="center", transform=ax.transAxes, color="grey"); ax.set_yticks([])
        ax.set_xlim(0, 1); ax.tick_params(labelsize=6); ax.spines[["top", "right"]].set_visible(False)
        if ri == 0: ax.set_title(arch, fontsize=10, weight="bold", pad=6)
        if aj == 0: ax.set_ylabel(ret, fontsize=10, weight="bold")

fig.suptitle("Renown — top equipment builds per retinue  (vanilla: no monuments/masteries, isolates gear)",
             fontsize=15, weight="bold", y=0.995)
plt.show()
