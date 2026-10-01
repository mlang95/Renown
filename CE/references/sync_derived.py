#!/usr/bin/env python3
"""sync_derived.py — re-derive the fields that MIRROR the pursuit text, after you edit NODES.

    python sync_derived.py [path/to/renown_data_d10.py]        # rewrites the file in place

The node TEXT is the source of truth. This rewrites two derived fields from each node's
"mastery_req" text, and reports (never edits) anything it can't derive:

  builds_into          A lists B exactly when A is named in B's Mastery requirement
                       ("2 Raw Materials" → every Raw Materials pursuit feeds it).
  engine.mastery_req   the AND-list the sim uses to decide Mastery, in sim names (engine.alias).
                       "A or B" parts and non-pursuits (Library, Keep, Hamlet…) can't be written
                       as an AND-list, so they are left out (the sim treats them as met) and listed.

Reported only: engine.prereqs entries that no longer appear in the node's Mastery requirement.
Everything else in the file is left byte-for-byte as it was.
"""
import importlib.util, json, re, sys, os

PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renown_data_d10.py")


def load(path):
    sp = importlib.util.spec_from_file_location("_rd_sync", path)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def node_span(src, name, order, i, start):
    k1 = "    " + json.dumps(name, ensure_ascii=False) + ": {"; k2 = "    '" + name + "': {"
    s0 = src.find(k1, start); s0 = s0 if s0 != -1 else src.find(k2, start)
    if i + 1 < len(order):
        n = order[i + 1]
        e1 = "    " + json.dumps(n, ensure_ascii=False) + ": {"; e2 = "    '" + n + "': {"
        e = src.find(e1, s0 + 1); e = e if e != -1 else src.find(e2, s0 + 1)
    else:
        e = src.find("\n}", s0)
    return s0, e


def main():
    rd = load(PATH); N = rd.NODES
    names = sorted(N, key=len, reverse=True)
    alias = {k: (v.get("engine") or {}).get("alias", k) for k, v in N.items() if v.get("engine")}

    def find(t):
        out, t2 = [], t
        for x in names:
            m = re.search(r"(?<![\w'])" + re.escape(x) + r"(?![\w'])", t2, re.I)
            if m:
                out.append((m.start(), x)); t2 = t2[:m.start()] + "#" * len(x) + t2[m.end():]
        return [x for _, x in sorted(out)]

    # builds_into from mastery_req
    feeds = {k: [] for k in N}
    for b, v in N.items():
        mr = re.sub(r"\*", "", str(v.get("mastery_req") or ""))
        src = find(mr)
        m = re.search(r"\d+\s+(" + "|".join(re.escape(t) for t in {w.get("type") for w in N.values() if w.get("type")}) + r")", mr)
        if m:
            src += [k for k, w in N.items() if w.get("type") == m.group(1) and k != b]
        for a in src:
            if a != b and b not in feeds[a]:
                feeds[a].append(b)

    # engine mastery_req from mastery_req text
    eng_new, notes = {}, []
    for k, v in N.items():
        if not v.get("engine"): continue
        txt = re.sub(r"\*", "", str(v.get("mastery_req") or "")).strip()
        new = []
        for g in ([x.strip() for x in txt.split("+")] if txt not in ("", "-", "\u2014") else []):
            if len(re.split(r"\s+or\s+|/", g)) > 1:
                notes.append(f"  {k}: '{g}' is either/or — left out of engine.mastery_req"); continue
            f = find(g)
            if not f:
                notes.append(f"  {k}: '{g}' is not a pursuit — left out of engine.mastery_req"); continue
            new += [alias.get(n, n) for n in f]
        eng_new[k] = new
        rev = {a: n for n, a in alias.items()}
        stale = [p for p in v["engine"].get("prereqs", []) if rev.get(p, p) not in txt]
        if stale:
            notes.append(f"  {k}: engine.prereqs {stale} not in its Mastery requirement ('{txt}') — check")

    src = open(PATH, encoding="utf-8").read()
    order = list(N); pos = src.index("NODES = {"); changed = []
    for i, name in enumerate(order):
        s0, e = node_span(src, name, order, i, pos); pos = s0 + 1
        blk = src[s0:e]; blk0 = blk
        old = list(N[name].get("builds_into") or [])
        newb = [x for x in old if x in feeds[name]] + [x for x in feeds[name] if x not in old]
        if old != newb:
            m = re.search(r'"builds_into":\s*\[[^\]]*\]', blk)
            if m:
                blk = blk[:m.start()] + '"builds_into": ' + json.dumps(newb, ensure_ascii=False) + blk[m.end():]
                changed.append(f"  builds_into  {name}: -{[x for x in old if x not in newb]} +{[x for x in newb if x not in old]}")
        if name in eng_new and list(N[name]["engine"].get("mastery_req", [])) != eng_new[name]:
            j = blk.find('"engine":'); jl = blk.find("\n", j); line = blk[j:jl]
            m = re.search(r'"mastery_req":\s*\[[^\]]*\]', line)
            if m:
                line = line[:m.start()] + '"mastery_req": ' + json.dumps(eng_new[name], ensure_ascii=False) + line[m.end():]
                blk = blk[:j] + line + blk[jl:]
                changed.append(f"  engine.mastery_req  {name}: {N[name]['engine'].get('mastery_req', [])} -> {eng_new[name]}")
        if blk != blk0:
            src = src[:s0] + blk + src[e:]
    open(PATH, "w", encoding="utf-8").write(src)
    load(PATH)   # must still import
    print(f"{PATH}: {len(changed)} field(s) updated")
    print("\n".join(changed) if changed else "  (nothing to change)")
    if notes:
        print("Not derivable / to check:"); print("\n".join(notes))


if __name__ == "__main__":
    main()
