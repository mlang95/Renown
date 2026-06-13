"""hexmap.py — the territory graph (C1).

Flat-top hexes in odd-q offset coordinates (col, row). Distance via cube
conversion. This is the spine the renderer decorates and Move/Siege traverse.
"""
from __future__ import annotations
from dataclasses import dataclass, field

# odd-q flat-top neighbor deltas, split by column parity
_EVEN = [(+1, 0), (+1, -1), (0, -1), (-1, -1), (-1, 0), (0, +1)]
_ODD = [(+1, +1), (+1, 0), (0, -1), (-1, 0), (-1, +1), (0, +1)]


def neighbors(col, row):
    deltas = _EVEN if col % 2 == 0 else _ODD
    return [(col + dc, row + dr) for dc, dr in deltas]


def _cube(col, row):
    x = col
    z = row - (col - (col & 1)) // 2
    return x, -x - z, z


def distance(a, b):
    ax, ay, az = _cube(*a)
    bx, by, bz = _cube(*b)
    return (abs(ax - bx) + abs(ay - by) + abs(az - bz)) // 2


@dataclass
class Hex:
    col: int
    row: int
    terrain: str = "plains"
    resource: str = None          # wood/stone/salt/grain/ore
    region: int = None            # starting-region id (0..n-1) or None
    owner: str = None             # player name once settled
    settlement: str = None        # tier name once placed

    @property
    def coord(self):
        return (self.col, self.row)

    @property
    def buildable(self):
        return self.terrain in ("plains", "forest", "wetland", "tundra")


@dataclass
class HexMap:
    width: int
    height: int
    cells: dict = field(default_factory=dict)   # (col,row) -> Hex

    @classmethod
    def blank(cls, w, h, fill="plains"):
        m = cls(w, h)
        for c in range(w):
            for r in range(h):
                m.cells[(c, r)] = Hex(c, r, fill)
        return m

    def in_bounds(self, coord):
        c, r = coord
        return 0 <= c < self.width and 0 <= r < self.height

    def get(self, coord) -> Hex:
        return self.cells.get(tuple(coord))

    def neighbors(self, coord):
        return [self.cells[c] for c in neighbors(*coord) if self.in_bounds(c)]

    def all(self):
        return self.cells.values()

    def of_terrain(self, t):
        return [h for h in self.cells.values() if h.terrain == t]

    def count(self, t):
        return sum(1 for h in self.cells.values() if h.terrain == t)

    def within(self, coord, radius):
        return [h for h in self.cells.values() if distance(coord, h.coord) <= radius]
