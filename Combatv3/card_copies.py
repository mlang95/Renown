#!/usr/bin/env python3
"""card_copies.py — print-quantity logic for pursuit cards, driven by the spec
tree in renown_data.

Rule (agreed):
  copies(node) = fan_out(node) + (PLAYERS - BASE_PLAYERS),  capped at 2*PLAYERS
  Monuments are always 1 (unique).
fan_out = number of DISTINCT, DISSIMILAR terminal endpoints reachable downstream
via builds_into. "Dissimilar" = distinct (type, domain) of the terminal node, so
a generic feeding multiple build styles (e.g. Courtyard -> Jester's Court AND the
martial line) scores high; a node feeding one chain to one capstone scores 1.
"""
import sys
sys.path.insert(0, ".")
import renown_data as rd

BASE_PLAYERS = 2

def _downstream(name, nodes, seen=None):
    seen = seen or set()
    for child in nodes.get(name, {}).get("builds_into", []) or []:
        if child in seen or child not in nodes:
            continue
        seen.add(child)
        _downstream(child, nodes, seen)
    return seen

def _terminals(name, nodes):
    """Reachable nodes that themselves build into nothing (the endpoints)."""
    down = _downstream(name, nodes)
    return {d for d in down if not (nodes.get(d, {}).get("builds_into") or [])}

def _style(node):
    """A terminal's 'style' = (type, dominant domain) — defines dissimilarity."""
    t = node.get("type", "")
    dom = node.get("engine", {}).get("domain") or {}
    d = max(dom, key=dom.get) if dom else node.get("unlock", "").split()[-1] if node.get("unlock") else ""
    return (t, d)

def fan_out(name, nodes):
    terms = _terminals(name, nodes)
    if not terms:
        return 1  # itself terminal: feeds only its own one style
    styles = {_style(nodes[t]) for t in terms if t in nodes}
    return max(1, len(styles))

def copies(name, nodes, players):
    n = nodes[name]
    if n.get("type") == "Monument":
        return 1
    raw = fan_out(name, nodes) + (players - BASE_PLAYERS)
    return max(1, min(raw, 2 * players))

def copy_map(mode="renown", players=2):
    nodes = rd.get_data(mode)
    return {name: copies(name, rd.NODES, players) for name in nodes}

if __name__ == "__main__":
    players = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    cm = copy_map("renown", players)
    tot = sum(cm.values())
    print(f"PLAYERS={players}: {len(cm)} pursuits -> {tot} printed cards")
    top = sorted(cm.items(), key=lambda x: -x[1])[:12]
    print("highest fan-out (most copies):")
    for n, c in top:
        print(f"  {c:>2}x  {n}  (fan-out {fan_out(n, rd.NODES)})")
    ones = [n for n, c in cm.items() if c == 1]
    print(f"single-copy cards: {len(ones)} (monuments + terminals)")
