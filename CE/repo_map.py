#!/usr/bin/env python3
"""repo_map.py — write REPO_MAP.md at the repo root: a generated index of the Renown repo for
Claude (and humans) to read instead of crawling GitHub file by file.

Contents (all derived, nothing hand-written — hand-written orientation lives in CLAUDE.md):
  1. folder tree with file counts (node_modules, lab_out, caches, binaries summarised)
  2. every source file: lines + its one-line purpose (module docstring / first comment / first heading)
  3. CE data index: every top-level name in the CE data file, its line, type and size
  4. build_all_CE.bat steps: labels, echo lines, scripts called
  5. rules md markers ({{TABLE}}, {{GLOSSARY}}, {{ACTIONS}}, {{LIST}}, {{VAL}}) and the docx_tables registry
  6. settlement board: payload keys passed to the HTML, JS function index with line numbers

Usage:  python repo_map.py [repo_root]      (default: the git root above this file)
Run by build_all_CE.bat before :pushrepo so the map ships with every push.
"""
import ast, os, re, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".ipynb_checkpoints", ".vscode", ".idea"}
SUMMARY_DIRS = {"lab_out", "Assets", "fonts"}           # counted, not listed file by file
SRC_EXT = {".py", ".bat", ".js", ".md", ".json", ".csv", ".txt", ".html", ".yml", ".yaml"}
BIG_HTML = 200_000                                        # generated HTML: list, don't read for purpose
DATA_FILE = os.path.join("CE", "renown_data_d10.py")
RULES_MD = os.path.join("CE", "RULES_push_simple.md")
BAT = os.path.join("CE", "build_all_CE.bat")
BOARD = os.path.join("CE", "references", "gen_settlement_board.py")
DOCX_TABLES = os.path.join("CE", "references", "docx_tables.py")


def git_root(start):
    d = start
    while True:
        if os.path.isdir(os.path.join(d, ".git")): return d
        p = os.path.dirname(d)
        if p == d: return os.path.dirname(start)
        d = p


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as fh: return fh.read()
    except OSError:
        return ""


def purpose(path, text):
    """One line describing a file, taken from the file itself."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".py":
        try:
            doc = ast.get_docstring(ast.parse(text))
            if doc: return doc.strip().splitlines()[0].strip()
        except SyntaxError:
            pass
        for ln in text.splitlines()[:15]:
            s = ln.strip()
            if s.startswith("#") and not s.startswith("#!") and len(s) > 3 and "coding" not in s:
                return s.lstrip("# ").strip()
        return ""
    if ext == ".bat":
        for ln in text.splitlines()[:20]:
            s = ln.strip()
            m = re.match(r"(?i)^(rem|::)\s+(.*)", s)
            if m and re.search(r"[A-Za-z]{3}", m.group(2)) and not set(m.group(2)) <= set("=-# "):
                return m.group(2).strip()
        return ""
    if ext == ".md":
        for ln in text.splitlines()[:30]:
            if ln.startswith("#"): return ln.lstrip("# ").strip()
        return ""
    if ext == ".js":
        m = re.search(r"/\*\*?\s*\n?\s*\*?\s*([^\n*][^\n]*)", text[:2000]) or re.search(r"^\s*//\s*(.+)$", text[:2000], re.M)
        return m.group(1).strip() if m else ""
    if ext == ".csv":
        first = text.splitlines()[0] if text else ""
        return "columns: " + first[:150]
    if ext == ".html":
        m = re.search(r"<title>(.*?)</title>", text[:5000], re.S | re.I)
        return m.group(1).strip() if m else ""
    return ""


def tree(root):
    out, files = [], []
    for d, dirs, fs in os.walk(root):
        rel = os.path.relpath(d, root)
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        name = os.path.basename(d) if rel != "." else "."
        if any(part in SUMMARY_DIRS for part in rel.split(os.sep)):
            if os.path.basename(d) in SUMMARY_DIRS:
                n = sum(len(f) for _, _, f in os.walk(d))
                out.append("  " * depth + f"{name}/  ({n} files, generated/assets — not indexed)")
            dirs[:] = []
            continue
        out.append("  " * depth + f"{name}/  ({len(fs)} files)")
        for f in sorted(fs):
            files.append(os.path.join(rel, f) if rel != "." else f)
    return out, files


def data_index(root):
    p = os.path.join(root, DATA_FILE)
    text = read(p)
    if not text: return []
    rows = []
    try:
        tree_ = ast.parse(text)
    except SyntaxError as e:
        return [("(parse error)", str(e), "", "")]
    ns = {}
    try:
        cwd = os.getcwd(); os.chdir(os.path.dirname(p))
        exec(compile(text, p, "exec"), ns)
    except Exception:
        ns = {}
    finally:
        os.chdir(cwd)
    seen = set()
    for node in tree_.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target.id]
        elif isinstance(node, ast.FunctionDef):
            targets = [node.name]
        for t in targets:
            if t.startswith("_") or t in seen: continue
            if not (t.isupper() or isinstance(node, ast.FunctionDef)): continue
            seen.add(t)
            v = ns.get(t)
            typ = "function" if isinstance(node, ast.FunctionDef) else type(v).__name__ if t in ns else "?"
            size = len(v) if isinstance(v, (dict, list, tuple, set)) else (repr(v)[:40] if isinstance(v, (int, float, str, bool)) else "")
            rows.append((t, node.lineno, typ, size))
    return rows


def bat_steps(root):
    text = read(os.path.join(root, BAT))
    rows, cur = [], None
    for i, ln in enumerate(text.splitlines(), 1):
        m = re.match(r"^:([A-Za-z]\w*)\s*$", ln)
        if m:
            cur = {"label": m.group(1), "line": i, "echo": [], "scripts": []}; rows.append(cur); continue
        if cur is None: continue
        e = re.match(r'(?i)^\s*echo\s+(.+)$', ln)
        if e and not e.group(1).startswith("."): cur["echo"].append(e.group(1).strip())
        for s in re.findall(r"%PY%\s+\"?([\w./\\%-]+\.py)", ln):
            if s not in cur["scripts"]: cur["scripts"].append(s.replace("%CE_ROOT%\\", ""))
    return rows


def rules_markers(root):
    text = read(os.path.join(root, RULES_MD))
    kinds = {}
    for k, v in re.findall(r"\{\{(TABLE|GLOSSARY|ACTIONS|LIST|TERM|IDX|COLS)(?::([^}]*))?\}\}", text):
        kinds.setdefault(k, [])
        if v not in kinds[k]: kinds[k].append(v)
    vals = sorted(set(re.findall(r"\{\{VAL:([^}]+)\}\}", text)))
    heads = [(i, ln) for i, ln in enumerate(text.splitlines(), 1) if ln.startswith("#")]
    reg = re.search(r"REGISTRY\s*=\s*\{(.*?)\n\}", read(os.path.join(root, DOCX_TABLES)), re.S)
    registry = sorted(set(re.findall(r'"([a-z_]+)"\s*:', reg.group(1)))) if reg else []
    return kinds, vals, heads, registry


def board_index(root):
    text = read(os.path.join(root, BOARD))
    m = re.search(r"html = render_html\((.*?)\n    \)", text, re.S)
    keys = re.findall(r"(?:^|[\s,(])([a-zA-Z]\w*)=", m.group(1)) if m else []
    funcs = [(i, mm.group(1)) for i, ln in enumerate(text.splitlines(), 1)
             for mm in [re.match(r"^function ([A-Za-z_]\w*)", ln)] if mm]
    secs = [(i, ln.strip("/ =").strip()) for i, ln in enumerate(text.splitlines(), 1) if re.match(r"^// =====", ln)]
    pyfuncs = [(i, mm.group(1)) for i, ln in enumerate(text.splitlines(), 1)
               for mm in [re.match(r"^def (\w+)", ln)] if mm]
    return keys, funcs, secs, pyfuncs


def main():
    root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else git_root(HERE)
    try:
        head = subprocess.run(["git", "-C", root, "log", "-1", "--format=%h %cd", "--date=short"],
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        head = ""
    di = data_index(root)
    version = next((str(v).strip("'") for n, _, _, v in di if n == "VERSION"), "")
    L = ["# REPO_MAP — generated index (do not edit; run `python CE/repo_map.py`)", "",
         f"Generated {datetime.date.today().isoformat()} · data VERSION `{version}` · HEAD `{head}`", "",
         "Hand-written orientation: `CLAUDE.md`. This file is derived from the files themselves.", ""]

    tr, files = tree(root)
    L += ["## 1. Folder tree", "", "```", *tr, "```", ""]

    L += ["## 2. Source files", "", "| File | Lines | Purpose |", "|---|---|---|"]
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext not in SRC_EXT: continue
        p = os.path.join(root, f)
        try: size = os.path.getsize(p)
        except OSError: size = 0
        if ext == ".html" and size > BIG_HTML:
            L.append(f"| `{f}` | — | generated HTML ({size // 1024} KB) |"); continue
        t = read(p)
        L.append(f"| `{f}` | {t.count(chr(10)) + 1} | {purpose(f, t).replace('|', '/')[:160]} |")
    L.append("")

    L += [f"## 3. Data index — `{DATA_FILE}`", "",
          "Copied to `CE/renown_data.py` by the build (DIE=d10); every script imports `renown_data`.", "",
          "| Name | Line | Type | Size / value |", "|---|---|---|---|"]
    L += [f"| `{n}` | {ln} | {t} | {str(s).replace('|', '/')} |" for n, ln, t, s in di] + [""]

    L += [f"## 4. Build steps — `{BAT}`", "", "| Label | Line | Scripts | Echo |", "|---|---|---|---|"]
    for r in bat_steps(root):
        L.append(f"| `:{r['label']}` | {r['line']} | {', '.join('`'+s+'`' for s in r['scripts']) or '—'} | {'; '.join(r['echo'])[:200].replace('|','/')} |")
    L.append("")

    kinds, vals, heads, registry = rules_markers(root)
    L += [f"## 5. Rules markers — `{RULES_MD}`", ""]
    for k in ("TABLE", "GLOSSARY", "ACTIONS", "LIST", "TERM", "IDX"):
        if kinds.get(k): L.append(f"- **{{{{{k}}}}}** ({len(kinds[k])}): " + ", ".join(f"`{x}`" for x in kinds[k] if x))
    L += [f"- **{{{{VAL}}}}** ({len(vals)}): " + ", ".join(f"`{x}`" for x in vals),
          f"- **docx_tables.REGISTRY** ({len(registry)}): " + ", ".join(f"`{x}`" for x in registry), "",
          "Headings:", "", "| Line | Heading |", "|---|---|"]
    L += [f"| {i} | {h.replace('|','/')} |" for i, h in heads] + [""]

    keys, funcs, secs, pyfuncs = board_index(root)
    L += [f"## 6. Settlement board — `{BOARD}`", "",
          f"Payload keys passed to the HTML as `DATA` ({len(keys)}): " + ", ".join(f"`{k}`" for k in keys), "",
          "Python: " + ", ".join(f"`{n}`:{i}" for i, n in pyfuncs), "",
          "JS sections: " + ", ".join(f"{n} :{i}" for i, n in secs), "",
          f"JS functions ({len(funcs)}, name:line):", "", "```",
          " ".join(f"{n}:{i}" for i, n in funcs), "```", ""]

    out = os.path.join(root, "REPO_MAP.md")
    with open(out, "w", encoding="utf-8", newline="\n") as fh: fh.write("\n".join(L))
    print(f"wrote {out}  ({len(files)} files walked, {len(di)} data names, {len(funcs)} board JS functions)")


if __name__ == "__main__":
    main()
