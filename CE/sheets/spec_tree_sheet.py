"""
Renown — Specialization Tree renderer.

Reads spec_trees.csv and lays out 3 tree panels per LANDSCAPE letter page,
with the capstone on the right and prerequisites flowing left-to-right.

Install:    pip install reportlab
Use from a notebook:
    from spec_tree_sheet import make_pdf
    make_pdf(r"C:\\path\\spec_trees.csv", r"C:\\path\\spec_trees.pdf")

CSV columns:
    tree       - capstone name (used as group key)
    pathology  - the path's flavor name (e.g. "Path of Shadows")
    node       - specialization name
    parents    - semicolon-separated list of parent specs, blank if root
    tier       - Untested / Rising / Established / Sovereign / —
    domain     - Cunning / Prowess / Piety / Industry / Nobility / Civic / Multi / —
    type       - Specialization / Power / Monument / Production / Civic / etc.

Print at 100% / "actual size".
"""

import csv
import re
import os
from collections import defaultdict
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import black, grey, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------- Specs lookup (loaded on demand from specs.csv) ----------
SPECS = {}

# Aliases for renames. If a tree_trees.csv still uses the old name but
# specs.csv has been renamed, the script keeps working until both are updated.
SPEC_ALIASES = {
    'Shipwright': 'Shipyard',
}

# Editorial tree config: capstone pursuit -> pathology (flavor) name.
# This is the ONLY tree data not derivable from renown_data — pathology names
# are pure flavor with no home in NODES. Node membership, parents, tier, domain,
# and type are all derived from renown_data (mastery_req closure + unlock field).
# Seeded from the legacy spec_trees.csv; renamed capstones resolved via SPEC_ALIASES.
TREES = {
    "Butchery": "Path of Butchery",
    "Shipyard": "Path of Seafaring",
    "Siege Camp": "Path of Sieging",
    "Studium Generale": "Path of Influence",
    "Saddlery": "Path of Riding",
    "Manor House": "Path of Farming",
    "Senate Hall": "Path of Diplomacy",
    "Imperial Palace": "Path of Power",
    "Royal Pavilion": "Path of the Champion",
    "Inquisitorial Palace": "Path of Inquisition",
    "Thieves' Guild": "Path of Thievery",
    "Cipher Chamber": "Path of Secrecy",
    "Aristocratic Court": "Path of Kleptocracy",
    "Court Artists": "Path of Income",
    "Beacon Towers": "Path of Territory",
    "Storehouse": "Path of Labor",
    "Ministry of Military Strategy": "Path of Tactics",
    "Advanced Blast Furnace": "Path of Technology",
    "Preceptory of the Knight's Templar": "Path of the Crusade",
}


def load_specs(specs_csv=None):
    """Populate SPECS from renown_data.NODES — the single source of truth.
    Rows carry the same keys the CSV had, so the renderer is unchanged.
    Legacy: pass a specs.csv path to load from CSV instead."""
    global SPECS
    SPECS = {}
    if specs_csv and os.path.exists(specs_csv):
        with open(specs_csv, newline='', encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                SPECS[r['Pursuits'].strip()] = r
        return
    from renown_data import NODES
    for name, n in NODES.items():
        SPECS[name] = {
            'Pursuits': name,
            'Type': n.get('type', ''),
            'Unlock Requirement': n.get('unlock', ''),
            'Mastery Requirement': n.get('mastery_req', ''),
            'Innate Effects': n.get('innate', ''),
            'Mastery Effect': n.get('mastery', ''),
            'Builds Into': ', '.join(n.get('builds_into', [])),
        }


def _resolve_spec_name(name):
    """Return the canonical SPECS key for `name`, honoring SPEC_ALIASES."""
    if name in SPECS:
        return name
    aliased = SPEC_ALIASES.get(name)
    if aliased and aliased in SPECS:
        return aliased
    return None


def _get_spec(name):
    """Lookup a spec by name (with alias fallback). Returns dict or None."""
    canonical = _resolve_spec_name(name)
    return SPECS.get(canonical) if canonical else None


def _is_known_spec(name):
    return _resolve_spec_name(name) is not None


def _strip_md(text):
    """Strip **bold** markdown and normalize whitespace."""
    t = re.sub(r'\*\*([^*]+)\*\*', r'\1', text or '')
    return ' '.join(t.split()) or '—'


def _smart_combine(innate, mastery):
    """Combine an innate and mastery string into one concise summary.

    Splits both into atomic clauses, sums duplicate numeric modifiers, dedupes
    repeated keywords (e.g. "Efficient X" or "Faith 1"), and preserves unique
    clauses. Returns a single string suitable for one footer line."""

    if not innate and not mastery:
        return '—'

    # Tokenize on commas and semicolons, stripping markdown
    def tokenize(s):
        if not s or s.strip() == '—':
            return []
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        # split on , or ; — but NOT on commas inside parenthetical clauses
        parts = []
        buf = ''
        depth = 0
        for ch in s:
            if ch == '(':
                depth += 1
                buf += ch
            elif ch == ')':
                depth -= 1
                buf += ch
            elif ch in ',;' and depth == 0:
                if buf.strip():
                    parts.append(buf.strip())
                buf = ''
            else:
                buf += ch
        if buf.strip():
            parts.append(buf.strip())
        return parts

    clauses = tokenize(innate) + tokenize(mastery)

    # Patterns that should sum/stack
    # Group 1: plain signed-integer gold like "+300" or "-200"
    # Group 2: signed-integer keyword like "Faith 1", "Doubt 2", "Influence -1"
    # Group 3: Efficient X — dedup
    # Everything else — keep verbatim, dedupe identicals

    gold_total = 0
    keyword_totals = {}   # e.g. {'Faith': 3, 'Doubt': 1}
    efficient_set = set()
    natural_present = False
    other_clauses = []
    seen_others = set()

    KEYWORD_PATTERN = re.compile(r'^(Faith|Doubt|Influence|Build Timer|Upkeep|Move|Endurance|Reach|Siege Timer|Speed|Maximum Endurance|Hit|Save|To Hit|Craft||AP|Initiative|Maintain [A-Za-z &]+)\s*([+\u2212-]?\s*\d+)$', re.IGNORECASE)

    for cl in clauses:
        cl_clean = cl.strip().rstrip('.')
        # Normalize unicode minus
        cl_norm = cl_clean.replace('\u2212', '-')

        # Pure gold (just a number, possibly signed)
        m_gold = re.match(r'^([+\-]?\d+)$', cl_norm)
        if m_gold:
            gold_total += int(m_gold.group(1))
            continue

        # Efficient X (dedupe)
        m_eff = re.match(r'^Efficient\s+(.+)$', cl_norm)
        if m_eff:
            efficient_set.add(m_eff.group(1).strip())
            continue

        # Natural (boolean, dedup)
        if cl_norm.lower() == 'natural':
            natural_present = True
            continue

        # Stackable keyword + number (Faith 1, Doubt 2, Influence -1, etc.)
        m_kw = KEYWORD_PATTERN.match(cl_norm)
        if m_kw:
            kw = m_kw.group(1).strip()
            # Canonicalize plural variations
            canon = kw
            if canon.lower() in ('trade specializations', 'trading specialization', 'trading specializations'):
                canon = 'Craft'
            num_str = m_kw.group(2).replace(' ', '')
            if num_str.startswith('+'):
                num_str = num_str[1:]
            try:
                val = int(num_str)
            except ValueError:
                # Fallback: treat as opaque
                if cl_clean not in seen_others:
                    other_clauses.append(cl_clean)
                    seen_others.add(cl_clean)
                continue
            keyword_totals[canon] = keyword_totals.get(canon, 0) + val
            continue

        # Default: keep verbatim, dedupe identicals
        if cl_clean not in seen_others:
            other_clauses.append(cl_clean)
            seen_others.add(cl_clean)

    # Reassemble
    out_parts = []
    if gold_total:
        out_parts.append(f"{'+' if gold_total > 0 else ''}{gold_total}")
    for kw, total in keyword_totals.items():
        sign = '+' if total > 0 else ''
        out_parts.append(f"{kw} {sign}{total}")
    if natural_present:
        out_parts.append("Natural")
    for eff in sorted(efficient_set):
        out_parts.append(f"Efficient {eff}")
    out_parts.extend(other_clauses)

    return ', '.join(out_parts) if out_parts else '—'


def _parse_requirements(spec_name):
    """Parse a spec's Mastery Requirement field; return list of names that are
    themselves specs (skips Infrastructure, settlements, etc.). Splits on '+'
    and on 'or' alternatives."""
    spec = _get_spec(spec_name)
    if spec is None:
        return []
    req_str = spec.get('Mastery Requirement', '') or ''
    if not req_str or req_str.strip() == '-':
        return []
    parts = []
    for p in req_str.split('+'):
        for q in re.split(r'\bor\b', p):
            name = q.strip().rstrip(',').strip()
            # Drop numeric prefixes like "2 Raw Materials" or "3 Productions"
            name = re.sub(r'^\d+\s+', '', name)
            if name and _is_known_spec(name):
                parts.append(name)
    # De-dupe preserving order
    seen, out = set(), []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _extract_income(text):
    """Find gold income amounts in effect text. Heuristic: signed integers with
    absolute value >= 100 are gold (Influence/Trade Spec/etc. are small numbers)."""
    if not text:
        return 0
    total = 0
    for m in re.finditer(r'([+-]?\d+)', text):
        v = int(m.group(1))
        if abs(v) >= 100:
            total += v
    return total


def _draw_text_fit(c, x, y, max_w, text, font, size):
    """Draw text, truncating with ellipsis if it exceeds max_w."""
    if stringWidth(text, font, size) <= max_w:
        c.setFont(font, size)
        c.drawString(x, y, text)
        return
    # Truncate
    ell = '\u2026'
    while text and stringWidth(text + ell, font, size) > max_w:
        text = text[:-1]
    c.setFont(font, size)
    c.drawString(x, y, text.rstrip(' ,;:') + ell)


def build_summary_lines(tree_name, nodes):
    """Return (lines, incomes) for the 3 farthest-right specialization nodes.

    HARD RULE: select the 3 rightmost nodes in the tree. Never more.

      1. Compute column rank = longest path from any root.
      2. Filter out: bucket placeholders, Raw Materials, Base type, nodes
         not in specs.csv.
      3. Take top 3 by (rank DESC, name ASC).
      4. Display order: (rank ASC, name ASC). Last entry rendered as 'capstone'.
    """
    rank = {}
    def get_rank(n, visiting=None):
        visiting = visiting or set()
        if n in rank:
            return rank[n]
        if n in visiting:
            return 0
        visiting = visiting | {n}
        parents = [p for p in nodes[n].get('parents', []) if p in nodes]
        rank[n] = 0 if not parents else 1 + max(get_rank(p, visiting) for p in parents)
        return rank[n]
    for n in nodes:
        get_rank(n)

    EXCLUDE_TYPES = {'raw materials', 'base', 'rawbucket', 'energybucket'}
    eligible = [
        n for n in nodes
        if nodes[n].get('type', '').lower() not in EXCLUDE_TYPES
        and _is_known_spec(n)
    ]
    if not eligible:
        return [], {}

    eligible.sort(key=lambda n: (-rank[n], n.lower()))
    top = eligible[:3]
    top.sort(key=lambda n: (rank[n], n.lower()))

    lines = []
    incomes = {}
    for i, name in enumerate(top):
        spec = _get_spec(name)
        if spec is None:
            continue
        innate = spec.get('Innate Effects', '') or ''
        mastery = spec.get('Mastery Effect', '') or ''
        income = _extract_income(innate) + _extract_income(mastery)
        combined = _smart_combine(innate, mastery)
        display_name = _resolve_spec_name(name) or name
        kind = 'capstone' if i == len(top) - 1 else 'requirement'
        lines.append((kind, display_name, combined))
        incomes[display_name] = income

    return lines, incomes


def _wrap_summary_text(text, font, size, max_w):
    """Wrap text into lines that fit within max_w. No ellipsing."""
    words = (text or '').split()
    if not words:
        return [""]
    lines = [words[0]]
    for w in words[1:]:
        cand = lines[-1] + " " + w
        if stringWidth(cand, font, size) <= max_w:
            lines[-1] = cand
        else:
            lines.append(w)
    return lines


def _summary_wrapped_line_count(lines, incomes, font_size, avail_w):
    """Pre-calculate total wrapped-line count for a summary band, so the
    caller can reserve enough vertical space before drawing."""
    total = 0
    for kind, name, text in lines:
        income = incomes.get(name, 0)
        if income > 0:
            badge = f"\u2295 +{income} gold"
        elif income < 0:
            badge = f"\u2296 {income} gold"
        else:
            badge = ""
        badge_w = stringWidth(badge, "Helvetica-Bold", font_size) if badge else 0
        label = f"{name}: "
        label_w = stringWidth(label, "Helvetica-Bold", font_size)
        body_avail = avail_w - label_w - (badge_w + 6 if badge else 0)
        body_font = "Helvetica-Bold" if kind == 'capstone' else "Helvetica"
        wrapped = _wrap_summary_text(text, body_font, font_size, body_avail)
        total += len(wrapped)
    return total


def draw_summary_band(c, x, y, w, h, lines, incomes, font_size=6.5):
    """Render summary lines top-to-bottom inside (x, y, w, h).

    Each spec's body text wraps to multiple lines as needed (no ellipsing).
    Continuation lines are indented to align with the spec's body column.
    The per-spec income badge sits on the right of the FIRST line.
    """
    if not lines:
        return
    line_h = font_size + 1.6
    cur_y = y + h - font_size
    for kind, name, text in lines:
        income = incomes.get(name, 0)
        if income > 0:
            badge = f"\u2295 +{income} gold"
        elif income < 0:
            badge = f"\u2296 {income} gold"
        else:
            badge = ""
        badge_w = stringWidth(badge, "Helvetica-Bold", font_size) if badge else 0

        label = f"{name}: "
        label_w = stringWidth(label, "Helvetica-Bold", font_size)
        body_avail = w - label_w - (badge_w + 6 if badge else 0)
        body_font = "Helvetica-Bold" if kind == 'capstone' else "Helvetica"
        body_lines = _wrap_summary_text(text, body_font, font_size, body_avail)

        # First line: label + first body line + (badge on right)
        c.setFont("Helvetica-Bold", font_size)
        if kind == 'capstone':
            c.setFillColor(HexColor("#5C2A1E"))
        c.drawString(x, cur_y, label)
        c.setFillColor(black)
        c.setFont(body_font, font_size)
        c.drawString(x + label_w, cur_y, body_lines[0])
        if badge:
            c.setFont("Helvetica-Bold", font_size)
            c.setFillColor(HexColor("#8C6A1A"))
            c.drawRightString(x + w, cur_y, badge)
            c.setFillColor(black)
        cur_y -= line_h

        # Continuation lines (indented to align with body column)
        # Once we're past the first line, the body can use the full width
        # since the badge only lives on line 1.
        full_avail = w - label_w
        cont_lines = body_lines[1:]
        if cont_lines:
            # Re-wrap the continuation text using the wider available width
            cont_text = ' '.join(cont_lines)
            cont_lines = _wrap_summary_text(cont_text, body_font, font_size, full_avail)
            for cont in cont_lines:
                c.setFont(body_font, font_size)
                c.drawString(x + label_w, cur_y, cont)
                cur_y -= line_h


# ---------- Layout ----------
PAGE_W, PAGE_H = landscape(letter)  # 11" x 8.5"
PAGE_MARGIN = 0.4 * inch
PANELS_PER_PAGE = 3
PANEL_GAP = 0.10 * inch

PANEL_W = PAGE_W - 2 * PAGE_MARGIN
PANEL_H = (PAGE_H - 2 * PAGE_MARGIN - (PANELS_PER_PAGE - 1) * PANEL_GAP) / PANELS_PER_PAGE

# Box geometry inside a panel
BOX_W = 1.05 * inch
BOX_H = 0.36 * inch
COL_GAP = 0.30 * inch  # horizontal space between tier columns
ROW_GAP = 0.06 * inch  # vertical space between sibling boxes

# ---------- Colors ----------
DOMAIN_COLORS = {
    "prowess":  HexColor("#B23A3A"),
    "cunning":  HexColor("#5B3A8C"),
    "piety":    HexColor("#C9A227"),
    "industry": HexColor("#3A7A4A"),
    "nobility": HexColor("#2A4D7F"),
    "civic":    HexColor("#7A6A4A"),
    "multi":    HexColor("#8C6A1A"),
    "—":        HexColor("#888888"),
}
CAPSTONE_BORDER = HexColor("#1A1A1A")  # near-black, thick — distinct from any domain
PANEL_TITLE = HexColor("#2A2A2A")
ARROW_COLOR = HexColor("#C8C8C8")
RAW_BG = HexColor("#F0EFEC")
ENERGY_BG = HexColor("#FCEBC5")  # warm amber — Energy spec type

NODE_TYPE_BORDER = {
    "Monument": 1.6,
    "Power":    1.2,
    "default":  0.6,
}


# ---------- CSV reading ----------
# Bucket merge: collapse all Raw Materials in a tree into one node, and all
# Energy specs (except a small exclusion list, and never the capstone itself)
# into another. These two buckets always live at the leftmost columns.
ENERGY_EXCLUDE_FROM_MERGE = frozenset(['Secret Cellar', 'Pilgrimage Site'])
BUCKET_RAW_KEY = '__RAW_MATERIALS__'
BUCKET_ENERGY_KEY = '__ENERGY_SOURCES__'


def merge_buckets_in_tree(tree_name, nodes):
    """Mutate `nodes` in place: replace Raw Material specs with one bucket node
    and applicable Energy specs with another. Returns
        {bucket_key: [member spec names in display order]}."""

    raw_members = sorted(
        n for n in nodes
        if nodes[n].get('type', '').lower() in ('raw materials', 'base')
    )
    energy_members = sorted(
        n for n in nodes
        if nodes[n].get('type', '').lower() == 'energy'
        and n not in ENERGY_EXCLUDE_FROM_MERGE
        and n != tree_name              # never merge the capstone itself
    )

    do_raw = len(raw_members) >= 2
    do_energy = len(energy_members) >= 2

    if not do_raw and not do_energy:
        return {}

    raw_set = set(raw_members) if do_raw else set()
    energy_set = set(energy_members) if do_energy else set()

    def remap(parent):
        if parent in raw_set:
            return BUCKET_RAW_KEY
        if parent in energy_set:
            return BUCKET_ENERGY_KEY
        return parent

    # Remap parent references on the remaining (non-merged) nodes
    for n, data in nodes.items():
        if n in raw_set or n in energy_set:
            continue
        new_parents, seen = [], set()
        for p in data.get('parents', []):
            rp = remap(p)
            if rp and rp not in seen:
                new_parents.append(rp)
                seen.add(rp)
        data['parents'] = new_parents

    # Drop the merged nodes
    for n in list(raw_set | energy_set):
        del nodes[n]

    # Insert bucket placeholder nodes
    buckets = {}
    if do_raw:
        nodes[BUCKET_RAW_KEY] = {
            'parents': [],
            'tier': '—',
            'domain': '—',
            'type': 'RawBucket',
        }
        buckets[BUCKET_RAW_KEY] = raw_members

    if do_energy:
        # Energy bucket sits in the column after raw (or first column if no raw)
        energy_parents = [BUCKET_RAW_KEY] if do_raw else []
        nodes[BUCKET_ENERGY_KEY] = {
            'parents': energy_parents,
            'tier': '—',
            'domain': '—',
            'type': 'EnergyBucket',
        }
        buckets[BUCKET_ENERGY_KEY] = energy_members

    return buckets


def _rd_parse_parents(node, NODES):
    """Parse a node's mastery_req into a list of prerequisite spec names that
    exist in NODES. Splits on '+' and 'or'; drops numeric prefixes."""
    req = (NODES.get(node, {}).get("mastery_req") or "").strip()
    if not req or req == "-":
        return []
    out = []
    for p in req.split("+"):
        for q in re.split(r"\bor\b", p):
            nm = re.sub(r"^\d+\s+", "", q.strip().rstrip(",").strip())
            if nm in NODES and nm not in out:
                out.append(nm)
    return out


def _rd_tier_domain(node, NODES):
    """Derive (tier, domain) from a node's unlock field (e.g. 'Sovereign Prowess')."""
    u = (NODES.get(node, {}).get("unlock") or "").strip()
    tier = next((t for t in ("Untested", "Rising", "Established", "Sovereign") if t in u), "—")
    dom = next((d for d in ("Industry", "Prowess", "Cunning", "Piety", "Nobility", "Civic") if d in u), "—")
    return tier, dom


def read_trees_from_renown_data():
    """Build the tree structures from renown_data.NODES — the single source of
    truth. Each tree is a capstone (see TREES) plus its mastery_req ancestor
    closure. parents/tier/domain/type derive from NODES; pathology comes from
    the editorial TREES config. Returns the same shape read_trees() produces."""
    from renown_data import NODES
    trees = {}
    for capstone, pathology in TREES.items():
        cap = _resolve_spec_name(capstone) or capstone
        if cap not in NODES:
            continue  # renamed/absent capstone — skip rather than crash
        # mastery_req ancestor closure
        members, stack = set(), [cap]
        while stack:
            n = stack.pop()
            if n in members:
                continue
            members.add(n)
            for p in _rd_parse_parents(n, NODES):
                if p not in members:
                    stack.append(p)
        nodes = {}
        for n in members:
            tier, dom = _rd_tier_domain(n, NODES)
            # parents within this tree only (layout uses in-tree edges)
            parents = [p for p in _rd_parse_parents(n, NODES) if p in members]
            nodes[n] = {
                "parents": parents,
                "tier": tier,
                "domain": dom,
                "type": NODES[n].get("type", ""),
            }
        # Key the tree by the canonical capstone name (matches a node, so the
        # renderer treats it as the capstone and forces it rightmost).
        trees[cap] = {"pathology": pathology, "nodes": nodes}
    # Apply the same bucket merge (Raw Materials / Energy collapsing) as the CSV path
    for tree_name, tree_data in trees.items():
        tree_data["buckets"] = merge_buckets_in_tree(tree_name, tree_data["nodes"])
    return trees


def read_trees(csv_path):
    trees = {}  # tree_name -> {"pathology": str, "nodes": {node: data}, "buckets": {}}
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            tree = row["tree"].strip()
            if tree not in trees:
                trees[tree] = {"pathology": row["pathology"].strip(), "nodes": {}}
            parents = [p.strip() for p in row["parents"].split(";") if p.strip()]
            trees[tree]["nodes"][row["node"].strip()] = {
                "parents": parents,
                "tier":    row["tier"].strip(),
                "domain":  row["domain"].strip(),
                "type":    row["type"].strip(),
            }

    # Apply bucket merge per tree
    for tree_name, tree_data in trees.items():
        tree_data["buckets"] = merge_buckets_in_tree(tree_name, tree_data["nodes"])

    return trees


# ---------- Layout: rank nodes by longest path from a root ----------
def compute_layout(tree_name, nodes):
    """Return dict: node -> (col, row) where col = rank from roots, row = vertical slot."""
    # Build child map for arrow drawing
    children = defaultdict(set)
    for n, data in nodes.items():
        for p in data["parents"]:
            if p in nodes:
                children[p].add(n)

    # Buckets reserve specific columns at the left
    has_raw_bucket = BUCKET_RAW_KEY in nodes
    has_energy_bucket = BUCKET_ENERGY_KEY in nodes
    target_raw_col = 0 if has_raw_bucket else None
    if has_energy_bucket:
        target_energy_col = 1 if has_raw_bucket else 0
    else:
        target_energy_col = None
    reserved_cols = set()
    if has_raw_bucket:
        reserved_cols.add(target_raw_col)
    if has_energy_bucket:
        reserved_cols.add(target_energy_col)

    def skip_reserved(c):
        """Return the smallest column >= c that isn't reserved."""
        while c in reserved_cols:
            c += 1
        return c

    # Topological rank: 1 + max(parent rank), then bumped past any reserved column.
    # Buckets are anchored to their target columns.
    rank = {}

    def get_rank(n, visiting=None):
        if visiting is None:
            visiting = set()
        if n in rank:
            return rank[n]
        if n in visiting:
            return 0  # cycle guard
        visiting = visiting | {n}

        # Anchor bucket nodes
        if n == BUCKET_RAW_KEY and has_raw_bucket:
            rank[n] = target_raw_col
            return rank[n]
        if n == BUCKET_ENERGY_KEY and has_energy_bucket:
            rank[n] = target_energy_col
            return rank[n]

        parents = [p for p in nodes[n]["parents"] if p in nodes]
        if not parents:
            base = 0
        else:
            base = 1 + max(get_rank(p, visiting) for p in parents)
        rank[n] = skip_reserved(base)
        return rank[n]

    for n in nodes:
        get_rank(n)

    # Force capstone (the tree_name) to be in the rightmost column
    if tree_name in nodes:
        max_rank = max(rank.values())
        rank[tree_name] = max_rank

    # Identify capstone nodes. If tree_name matches a node, that's the *only*
    # capstone. If it doesn't match (e.g. "Meadery & Winery" tree where no node
    # is named that), fall back to all rightmost terminal nodes as capstones.
    max_rank = max(rank.values())
    capstone_nodes = set()
    if tree_name in nodes:
        capstone_nodes.add(tree_name)
    else:
        rightmost = {n for n, r in rank.items() if r == max_rank and not children.get(n)}
        capstone_nodes.update(rightmost)
    # Buckets are never "capstones" even if they end up in the rightmost column
    capstone_nodes.discard(BUCKET_RAW_KEY)
    capstone_nodes.discard(BUCKET_ENERGY_KEY)

    # Group by rank
    columns = defaultdict(list)
    for n, r in rank.items():
        columns[r].append(n)

    # Sort each column: capstone last, buckets always at top, otherwise alphabetic.
    def sort_key(x):
        is_capstone = (x == tree_name)
        is_bucket = x in (BUCKET_RAW_KEY, BUCKET_ENERGY_KEY)
        # Buckets first (False sorts before True), then alphabetic, capstone last
        return (is_capstone, not is_bucket, x.lower())
    for r in columns:
        columns[r].sort(key=sort_key)

    # Assign (col, row)
    layout = {}
    for col_idx in sorted(columns.keys()):
        for row_idx, n in enumerate(columns[col_idx]):
            layout[n] = (col_idx, row_idx)

    n_cols = max(columns.keys()) + 1
    col_heights = {c: len(columns[c]) for c in columns}

    return layout, n_cols, col_heights, children, capstone_nodes


# ---------- Drawing helpers ----------
def _wrap_to_box(text, font, size, box_w, padding=4):
    """Wrap text to fit within box_w. Returns list of lines (max 2)."""
    avail = box_w - 2 * padding
    words = text.split()
    if not words:
        return [""]
    lines = [words[0]]
    for w in words[1:]:
        candidate = lines[-1] + " " + w
        if stringWidth(candidate, font, size) <= avail:
            lines[-1] = candidate
        else:
            lines.append(w)
    if len(lines) > 2:
        # Try smaller font fallback handled at draw-time; here just keep all but caller may shrink
        lines = lines[:2]
    return lines


def _fit_box_text(text, box_w, max_lines=2, font="Helvetica-Bold", start=8.5, floor=6.0):
    """Find a font size that fits text in the box at <= max_lines."""
    size = start
    while size >= floor:
        lines = _wrap_to_box(text, font, size, box_w)
        if len(lines) <= max_lines and all(stringWidth(l, font, size) <= box_w - 8 for l in lines):
            return lines, size
        size -= 0.5
    # Last resort: hard truncate
    lines = _wrap_to_box(text, font, floor, box_w)[:max_lines]
    if lines and stringWidth(lines[-1] + "\u2026", font, floor) > box_w - 8:
        while lines[-1] and stringWidth(lines[-1] + "\u2026", font, floor) > box_w - 8:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "\u2026"
    return lines, floor


def draw_bucket_box(c, x, y, w, h, kind, members):
    """Draw a tall multi-spec bucket box listing all merged members."""
    is_raw = (kind == 'raw')
    bg = RAW_BG if is_raw else ENERGY_BG

    c.setFillColor(bg)
    c.setStrokeColor(grey if is_raw else black)
    c.setLineWidth(0.6 if is_raw else 0.9)
    c.rect(x, y, w, h, stroke=1, fill=1)

    # Title strip at top
    title = "Raw Materials" if is_raw else "Energy"
    title_font = "Helvetica-Bold"
    title_size = 7.0
    title_strip_h = 12.0
    title_band_y = y + h - title_strip_h

    # Subtle divider under title
    c.setStrokeColor(HexColor("#BBBBBB"))
    c.setLineWidth(0.3)
    c.line(x + 3, title_band_y, x + w - 3, title_band_y)
    c.setStrokeColor(black)

    c.setFillColor(HexColor("#5C2A1E") if not is_raw else HexColor("#555555"))
    c.setFont(title_font, title_size)
    c.drawCentredString(x + w / 2, title_band_y + 3, title)

    # Members list, vertically centered in the remaining space
    avail_top = title_band_y - 2
    avail_bot = y + 3
    avail_h = max(avail_top - avail_bot, 0)
    n = max(len(members), 1)

    # Find a font size that fits the longest member name within width
    max_text_w = w - 6
    font_name = "Helvetica"
    font_size = 6.8
    longest = max(members, key=lambda m: stringWidth(m, font_name, font_size)) if members else ""
    while font_size > 4.6 and stringWidth(longest, font_name, font_size) > max_text_w:
        font_size -= 0.2
    line_h = font_size + 1.6

    # Vertically center the list within the avail band
    total_h = n * line_h
    if total_h > avail_h:
        # Shrink line_h slightly to fit (rare for trees with 6+ raw members)
        line_h = max(font_size + 0.6, avail_h / n)
        total_h = n * line_h

    block_top = avail_top - (avail_h - total_h) / 2

    c.setFillColor(black)
    c.setFont(font_name, font_size)
    for i, m in enumerate(members):
        baseline_y = block_top - (i + 1) * line_h + (line_h - font_size) / 2
        c.drawCentredString(x + w / 2, baseline_y, m)


def draw_node_box(c, x, y, w, h, node, data, is_capstone=False):
    ntype = data.get("type", "")
    # Bucket nodes get their own renderer
    if ntype == "RawBucket":
        members = data.get("_members", [])
        draw_bucket_box(c, x, y, w, h, 'raw', members)
        return
    if ntype == "EnergyBucket":
        members = data.get("_members", [])
        draw_bucket_box(c, x, y, w, h, 'energy', members)
        return

    domain = (data.get("domain") or "—").lower()
    accent = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["—"])
    is_raw = ntype.lower() in ("raw materials", "base")
    is_energy = ntype.lower() == "energy"

    # Background
    if is_raw:
        c.setFillColor(RAW_BG)
        c.setStrokeColor(grey)
        c.setLineWidth(0.5)
        c.rect(x, y, w, h, stroke=1, fill=1)
    elif is_capstone:
        # Capstone wins over Energy if it ever happens; Energy capstones get
        # both: amber fill + heavy black border
        c.setFillColor(ENERGY_BG if is_energy else white)
        c.setStrokeColor(CAPSTONE_BORDER)
        c.setLineWidth(2.2)
        c.rect(x, y, w, h, stroke=1, fill=1)
    else:
        c.setFillColor(ENERGY_BG if is_energy else white)
        c.setStrokeColor(black)
        c.setLineWidth(NODE_TYPE_BORDER.get(ntype, NODE_TYPE_BORDER["default"]))
        c.rect(x, y, w, h, stroke=1, fill=1)

    # Domain accent stripe at top
    if not is_raw:
        c.setFillColor(accent)
        c.rect(x, y + h - 2.5, w, 2.5, stroke=0, fill=1)

    # Node name — apply alias resolution so renamed specs display canonically
    display_node = _resolve_spec_name(node) or node
    lines, size = _fit_box_text(display_node, w, max_lines=2, font="Helvetica-Bold")
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", size)
    n_lines = len(lines)
    line_h = size + 1.2
    block_h = n_lines * line_h
    text_y = y + (h - block_h) / 2 + (n_lines - 1) * line_h - 1
    if is_raw:
        c.setFillColor(HexColor("#666666"))
    cx = x + w / 2
    for i, line in enumerate(lines):
        c.drawCentredString(cx, text_y - i * line_h, line)

    # Tier badge bottom-right (small)
    tier = data.get("tier", "")
    if tier and tier != "—":
        badge = tier[0]  # U / R / E / S
        c.setFillColor(accent)
        c.setFont("Helvetica-Bold", 5.5)
        c.drawRightString(x + w - 2.5, y + 1.5, badge)

    c.setFillColor(black)


def draw_arrow(c, x1, y1, x2, y2):
    """Draw a subtle connecting line from (x1,y1) to (x2,y2).
    No arrowhead — direction is implied by left-to-right tree flow."""
    c.setStrokeColor(ARROW_COLOR)
    c.setLineWidth(0.35)
    c.line(x1, y1, x2, y2)
    c.setStrokeColor(black)


# ---------- Panel ----------
def draw_panel(c, x, y, tree_name, tree_data):
    nodes = tree_data["nodes"]
    pathology = tree_data["pathology"]

    # Panel border
    c.setStrokeColor(grey)
    c.setLineWidth(0.4)
    c.rect(x, y, PANEL_W, PANEL_H)

    # Title bar
    title_h = 0.30 * inch
    title_y = y + PANEL_H - title_h
    c.setFillColor(HexColor("#F5F2EC"))
    c.rect(x, title_y, PANEL_W, title_h, stroke=0, fill=1)
    c.setFillColor(PANEL_TITLE)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x + 8, title_y + title_h / 2 - 2, pathology.upper())

    # Capstone name on the right of the title bar. Resolve renames via SPEC_ALIASES
    # so a CSV still using the old name still surfaces the canonical one.
    display_tree_name = _resolve_spec_name(tree_name) or tree_name
    cap_label = f"\u2192  {display_tree_name}"
    c.setFont("Helvetica-BoldOblique", 11)
    c.setFillColor(HexColor("#5C2A1E"))
    c.drawRightString(x + PANEL_W - 8, title_y + title_h / 2 - 2, cap_label)
    c.setFillColor(black)

    # Build summary lines (3 rightmost specs, capstone at bottom)
    summary_lines, summary_incomes = build_summary_lines(tree_name, nodes)
    summary_font = 6.0
    summary_line_h = summary_font + 1.6
    # Pre-calc total wrapped lines so we reserve enough space for full text.
    summary_total_lines = _summary_wrapped_line_count(
        summary_lines, summary_incomes, summary_font, PANEL_W - 16
    ) if summary_lines else 0
    summary_h = (summary_total_lines * summary_line_h + 3) if summary_total_lines else 0

    # Tree area — shrunk to leave room for the summary band at the bottom
    tree_x = x + 8
    tree_y = y + 6 + summary_h
    tree_w = PANEL_W - 16
    tree_h = PANEL_H - title_h - 12 - summary_h

    # Footer band sits between tree_y and panel bottom
    footer_x = tree_x
    footer_y = y + 4
    footer_w = tree_w
    footer_h = summary_h

    # Layout nodes
    layout, n_cols, col_heights, children, capstone_nodes = compute_layout(tree_name, nodes)

    # Buckets dict from read_trees, accessed via tree_data closure
    buckets = tree_data.get("buckets", {}) or {}

    # Identify "wide" columns: any non-bucket column with >= 6 rows gets split
    # into 2 sub-columns of ceil(h/2) and floor(h/2). Bucket-bearing columns
    # never split (buckets span the full column height by design).
    WIDE_THRESHOLD = 6
    bucket_cols = {layout[n][0] for n in (BUCKET_RAW_KEY, BUCKET_ENERGY_KEY) if n in layout}
    wide_cols = {
        col: h for col, h in col_heights.items()
        if h >= WIDE_THRESHOLD and col not in bucket_cols
    }

    # Effective heights after splitting (used for box-size calc)
    effective_heights = {
        col: ((h + 1) // 2 if col in wide_cols else h)
        for col, h in col_heights.items()
    }
    max_col_h = max(effective_heights.values())

    # Effective column count: wide cols consume 2 horizontal slots
    n_cols_effective = sum(2 if col in wide_cols else 1 for col in col_heights)

    avail_w = tree_w
    avail_h = tree_h

    box_w = min(BOX_W, (avail_w - (n_cols_effective - 1) * COL_GAP) / max(n_cols_effective, 1))
    box_h = min(BOX_H, (avail_h - (max_col_h - 1) * ROW_GAP) / max(max_col_h, 1))
    box_w = max(box_w, 0.7 * inch)
    box_h = max(box_h, 0.26 * inch)

    # Build a column-rank → x-offset map. Wide columns consume 2 slots.
    col_x_offsets = {}
    cur_off = 0
    for col_idx in sorted(col_heights.keys()):
        col_x_offsets[col_idx] = cur_off
        cur_off += 2 * (box_w + COL_GAP) if col_idx in wide_cols else (box_w + COL_GAP)
    used_w = cur_off - COL_GAP
    start_x = tree_x + (tree_w - used_w) / 2

    # Full column height (used by bucket nodes — they always span their column)
    full_col_h = max_col_h * box_h + (max_col_h - 1) * ROW_GAP

    # Position each node
    positions = {}
    for node, (col, row) in layout.items():
        if node in buckets:
            # Bucket: span the full column height
            bx = start_x + col_x_offsets[col]
            col_start_y = tree_y + (tree_h - full_col_h) / 2
            by = col_start_y
            positions[node] = (bx, by, box_w, full_col_h)
        elif col in wide_cols:
            # Wide column: split into 2 sub-columns of half height
            h = col_heights[col]
            half = (h + 1) // 2  # top sub-column gets the extra row when odd
            if row < half:
                sub_col, sub_row, sub_h = 0, row, half
            else:
                sub_col, sub_row, sub_h = 1, row - half, h - half
            bx = start_x + col_x_offsets[col] + sub_col * (box_w + COL_GAP)
            col_used_h = sub_h * box_h + (sub_h - 1) * ROW_GAP
            col_start_y = tree_y + (tree_h - col_used_h) / 2
            by = col_start_y + (sub_h - 1 - sub_row) * (box_h + ROW_GAP)
            positions[node] = (bx, by, box_w, box_h)
        else:
            h = col_heights[col]
            col_used_h = h * box_h + (h - 1) * ROW_GAP
            col_start_y = tree_y + (tree_h - col_used_h) / 2
            bx = start_x + col_x_offsets[col]
            by = col_start_y + (h - 1 - row) * (box_h + ROW_GAP)
            positions[node] = (bx, by, box_w, box_h)

    # Arrows removed — column position implies dependency direction.

    # Draw boxes
    for node, (bx, by, bw, bh) in positions.items():
        is_cap = (node in capstone_nodes)
        node_data = dict(nodes[node])  # shallow copy so we can inject _members
        if node in buckets:
            node_data["_members"] = buckets[node]
        draw_node_box(c, bx, by, bw, bh, node, node_data, is_capstone=is_cap)

    # Draw summary band at bottom (top specs' innates/masteries)
    if summary_h > 0:
        # Faint separator above footer band
        c.setStrokeColor(HexColor("#CCCCCC"))
        c.setLineWidth(0.3)
        c.line(footer_x, footer_y + footer_h + 1, footer_x + footer_w, footer_y + footer_h + 1)
        c.setStrokeColor(black)
        draw_summary_band(c, footer_x, footer_y, footer_w, footer_h, summary_lines, summary_incomes, font_size=summary_font)


# ---------- Cut marks between panels ----------
def draw_cut_marks(c, panel_top_y_list):
    """Draw small tick marks between panels at the side margins."""
    c.setStrokeColor(grey)
    c.setLineWidth(0.25)
    tick = 0.12 * inch
    for y in panel_top_y_list:
        # left
        c.line(PAGE_MARGIN - 0.05 * inch, y, PAGE_MARGIN - 0.05 * inch - tick, y)
        # right
        c.line(PAGE_W - PAGE_MARGIN + 0.05 * inch, y, PAGE_W - PAGE_MARGIN + 0.05 * inch + tick, y)
    c.setStrokeColor(black)


def make_pdf(csv_path=None, pdf_path=None, specs_csv=None):
    """Render the spec-tree sheet. By default reads renown_data (single source
    of truth). Pass csv_path to use a legacy spec_trees.csv instead.
    Usage: make_pdf(pdf_path="spec_trees.pdf")  # renown_data
           make_pdf("spec_trees.csv", "spec_trees.pdf")  # legacy CSV
    """
    # Allow make_pdf("out.pdf") positional shorthand when reading renown_data.
    if pdf_path is None and csv_path and csv_path.lower().endswith(".pdf"):
        csv_path, pdf_path = None, csv_path
    if pdf_path is None:
        pdf_path = "spec_trees.pdf"

    use_csv = bool(csv_path) and os.path.exists(csv_path)
    if use_csv:
        # Auto-detect specs.csv adjacent to the spec_trees csv if not given
        if specs_csv is None:
            candidate = os.path.join(os.path.dirname(csv_path) or '.', 'specs.csv')
            if os.path.exists(candidate):
                specs_csv = candidate
        load_specs(specs_csv)
        trees = read_trees(csv_path)
    else:
        load_specs(None)                      # populate SPECS from renown_data
        trees = read_trees_from_renown_data()  # build trees from renown_data

    tree_items = list(trees.items())

    c = canvas.Canvas(pdf_path, pagesize=landscape(letter))

    for i, (tree_name, tree_data) in enumerate(tree_items):
        slot = i % PANELS_PER_PAGE
        if slot == 0 and i > 0:
            # Cut marks for finished page
            draw_cut_marks(c, _page_panel_separators())
            c.showPage()

        # Panel position (top to bottom)
        panel_y = PAGE_H - PAGE_MARGIN - (slot + 1) * PANEL_H - slot * PANEL_GAP
        draw_panel(c, PAGE_MARGIN, panel_y, tree_name, tree_data)

    # Final page cut marks
    draw_cut_marks(c, _page_panel_separators())
    c.save()

    n_pages = (len(tree_items) + PANELS_PER_PAGE - 1) // PANELS_PER_PAGE
    src = "spec_trees.csv" if use_csv else "renown_data"
    print(f"Wrote {pdf_path}  ({len(tree_items)} trees from {src}, {n_pages} page(s))")


def _page_panel_separators():
    """Y-coordinates between panels for cut tick marks."""
    seps = []
    for i in range(1, PANELS_PER_PAGE):
        y = PAGE_H - PAGE_MARGIN - i * PANEL_H - (i - 1) * PANEL_GAP - PANEL_GAP / 2
        seps.append(y)
    return seps

if __name__ == "__main__":
    import sys
    # Usage:
    #   python spec_tree_sheet.py [out.pdf]                  -> read renown_data
    #   python spec_tree_sheet.py spec_trees.csv [out.pdf]   -> legacy CSV
    args = sys.argv[1:]
    if len(args) == 1 and args[0].lower().endswith(".pdf"):
        make_pdf(pdf_path=args[0])
    elif len(args) >= 2:
        make_pdf(args[0], args[1])
    elif len(args) == 1:
        make_pdf(args[0], "spec_trees.pdf")
    else:
        make_pdf(pdf_path="spec_trees.pdf")
