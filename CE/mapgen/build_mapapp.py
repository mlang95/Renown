#!/usr/bin/env python3
"""build_mapapp.py - assemble renown-maps.html from its sources.

Three inputs are baked into one self-contained page:

    app_shell.html    markup, styles, UI wiring   (/*__GEN__*/ /*__PRESETS__*/
                                                   /*__TERRAIN__*/ placeholders)
    gen.js            the generator, JS port
    region_presets.py -> presets.js               (generated, never hand-edited)
    renown_data.py    -> the terrain effects table (generated)

Run it from the folder holding the mapgen files. renown_data is imported from
the PARENT folder by default, so a CE build picks up CE rules and a D6 build
picks up D6 rules without either one reaching into the other.

    python build_mapapp.py                 # -> renown-maps.html
    python build_mapapp.py --data ..       # explicit renown_data location
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def presets_js():
    sys.path.insert(0, HERE)
    import region_presets as rp
    out = {}
    for name in rp.names():
        q = rp.get(name)
        q["palette"] = sorted(q["palette"])
        q["buffers"] = [list(b) for b in q.get("buffers", [])]
        for f in ("band", "scatter", "massif", "perimeter"):
            q[f] = {k: [list(x) if isinstance(x, tuple) else x for x in v]
                    if isinstance(v, (list, tuple)) else v
                    for k, v in (q.get(f) or {}).items()}
        for f in ("shares", "morphology", "resource_min", "art"):
            q[f] = q.get(f) or {}
        c = q.get("carve")
        if c:
            c = dict(c)
            for k in ("mazes", "rivers", "islands", "island_size", "islets", "gap"):
                if k in c and isinstance(c[k], tuple):
                    c[k] = list(c[k])
            q["carve"] = c
        b = q.get("border", 0)

        def conv(v):
            if isinstance(v, dict):
                return {k: (list(x) if isinstance(x, tuple) else x)
                        for k, x in v.items()}
            return list(v) if isinstance(v, tuple) else v
        q["border"] = ({k: conv(v) for k, v in b.items()}
                       if isinstance(b, dict) else conv(b))
        out[name] = q
    body = json.dumps(out, indent=1)
    return ("/* presets.js - GENERATED from region_presets.py. Do not hand-edit. */\n"
            "(function(root){root.RenownPresets=" + body + ";})"
            "(typeof module!=='undefined'&&module.exports?module.exports:"
            "(typeof window!=='undefined'?window:globalThis));\n"), len(out)


def find_data(explicit=None):
    """Locate the renown_data.py that governs THIS build.

    Layouts differ: D6 keeps mapgen/ beside renown_data.py, while CE is
    CE/{combatv4,mapgen,lab_out} with the data a folder over. Guessing wrong is
    silent and bad — a CE app would show D6 terrain effects with nothing to
    indicate it — so this searches, reports what it found, and refuses rather
    than falling back to whatever happens to be importable.
    """
    seen = []
    for c in [explicit,
              os.path.join(HERE, "..", "combatv4"),   # CE/{combatv4,mapgen}
              os.path.join(HERE, ".."),               # data one folder up
              HERE,                                   # data beside the app
              os.getcwd()]:
        if not c:
            continue
        c = os.path.abspath(c)
        if c in seen:
            continue
        seen.append(c)
        if os.path.exists(os.path.join(c, "renown_data.py")):
            return c
    raise SystemExit(
        "build_mapapp: renown_data.py not found. Looked in:\n  "
        + "\n  ".join(seen)
        + "\nPass --data <folder> if it lives somewhere else.")


def terrain_ref(data_dir):
    """Terrain effects, read from the located renown_data.py. Stamped with the
    folder it came from so a mis-sourced table is visible in the app."""
    sys.path.insert(0, os.path.abspath(data_dir))
    import renown_data as rd
    return {
        "terrain": rd.TERRAIN,
        "tactical": rd.TACTICAL_TERRAIN,
        "tactical_global": list(getattr(rd, "TACTICAL_GLOBAL", [])),
        "movement": getattr(rd, "MOVEMENT_MODIFIERS", {}),
        "version": str(getattr(rd, "VERSION", "?")),
        "source": os.path.basename(os.path.abspath(data_dir)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=None,
                    help="folder containing renown_data.py "
                         "(default: search ../combatv4, .., then this folder)")
    ap.add_argument("--out", default=os.path.join(HERE, "renown-maps.html"))
    a = ap.parse_args()

    shell = open(os.path.join(HERE, "app_shell.html"), encoding="utf-8").read()
    gen = open(os.path.join(HERE, "gen.js"), encoding="utf-8").read()
    pjs, npre = presets_js()
    open(os.path.join(HERE, "presets.js"), "w", encoding="utf-8").write(pjs)
    ref = terrain_ref(find_data(a.data))

    for token in ("/*__GEN__*/", "/*__PRESETS__*/", "/*__TERRAIN__*/"):
        if token not in shell:
            raise SystemExit(f"app_shell.html is missing {token}")
    html = (shell.replace("/*__TERRAIN__*/", json.dumps(ref, separators=(",", ":")))
                 .replace("/*__GEN__*/", gen)
                 .replace("/*__PRESETS__*/", pjs))
    open(a.out, "w", encoding="utf-8").write(html)
    print(f"  map app -> {os.path.relpath(a.out, HERE)}  "
          f"({len(html)//1024} KB, {npre} presets, "
          f"terrain from {ref['source']}/renown_data.py v{ref['version']})")


if __name__ == "__main__":
    main()