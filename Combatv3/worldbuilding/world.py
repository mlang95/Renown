#!/usr/bin/env python
# world.py - fixed macro-geography of the setting.
# Continents anchor Domains (Heartlands). Pair-Guild archipelagos seat between
# their two parent Domains and gradient inward toward the Center; the Center
# hosts the triple/quad Guilds (Polymath) and the Court.
from dataclasses import dataclass, field
from itertools import combinations

WATER_RATIO = 0.40

@dataclass
class Landmass:
    name: str
    kind: str                  # central_island | continent | archipelago
    domain: str | None = None
    pair: tuple | None = None
    seats: list = field(default_factory=list)
    gradient_to_center: bool = False

@dataclass
class World:
    water_ratio: float = WATER_RATIO
    landmasses: list = field(default_factory=list)
    def center(self):       return next((l for l in self.landmasses if l.kind=="central_island"), None)
    def heartlands(self):   return [l for l in self.landmasses if l.kind=="continent"]
    def archipelagos(self): return [l for l in self.landmasses if l.kind=="archipelago"]

CORNER = {"Industry":"NW","Prowess":"NE","Cunning":"SW","Piety":"SE"}
ADJACENT = {("Industry","Prowess"),("Industry","Cunning"),("Prowess","Piety"),("Cunning","Piety")}
def is_adjacent(a,b): return (a,b) in ADJACENT or (b,a) in ADJACENT

LM = [
    # Center = convergence basin: pair-chains gradient inward and blend here,
    # producing triples (three chains meet) and Polymath (all four).
    Landmass("The Center","central_island",seats=["Triple","Polymath","Court","Anomaly"]),
    Landmass("Industry Continent","continent","Industry",seats=["Heartland"]),
    Landmass("Prowess Continent","continent","Prowess",seats=["Heartland"]),
    Landmass("Cunning Continent","continent","Cunning",seats=["Heartland"]),
    Landmass("Piety Continent","continent","Piety",seats=["Heartland"]),
]
for a,b in combinations(["Industry","Prowess","Cunning","Piety"],2):
    edge = is_adjacent(a,b)
    LM.append(Landmass(
        f"{a[:3]}-{b[:3]} Archipelago","archipelago",pair=(a,b),
        seats=["Border"] + ([] if edge else ["March"]),
        gradient_to_center=True))          # every pair chain reaches inward
WORLD = World(landmasses=LM)

if __name__ == "__main__":
    w=WORLD
    print(f"water {int(w.water_ratio*100)}%  land {int((1-w.water_ratio)*100)}%")
    print("center :", w.center().name, w.center().seats)
    print("corners:", [(l.domain,CORNER[l.domain]) for l in w.heartlands()])
    for l in w.archipelagos():
        a,b=l.pair
        print(f"  {a[:3]}x{b[:3]:8} {'edge' if is_adjacent(a,b) else 'diag'}  ->center  seats={l.seats}")
    print("triples/quad seat -> The Center (gradient convergence of pair chains)")
