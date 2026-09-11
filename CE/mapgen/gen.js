/* gen.js — Renown regional map generator, JS port.
 *
 * Port of mapgen_regional.py + the parts of mapgen.py it depends on.
 * No DOM, no dependencies: runs in node for testing and in the browser for
 * the app. The browser is the ONLY generator — Python renders what this
 * emits — so there is no requirement to match CPython's Mersenne Twister.
 * A seeded mulberry32 is enough, and it makes seeds reproducible here.
 */
(function (root) {
'use strict';

/* ── seeded rng ─────────────────────────────────────────────────────────── */
function RNG(seed) {
  let a = (seed >>> 0) || 1;
  this._next = function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
RNG.prototype.random = function () { return this._next(); };
RNG.prototype.randrange = function (n) { return Math.floor(this._next() * n); };
RNG.prototype.randint = function (a, b) { return a + Math.floor(this._next() * (b - a + 1)); };
RNG.prototype.uniform = function (a, b) { return a + this._next() * (b - a); };
RNG.prototype.choice = function (arr) { return arr[this.randrange(arr.length)]; };
RNG.prototype.sample = function (arr, k) {
  const c = arr.slice();
  for (let i = c.length - 1; i > 0; i--) {
    const j = this.randrange(i + 1); const t = c[i]; c[i] = c[j]; c[j] = t;
  }
  return c.slice(0, Math.min(k, c.length));
};
RNG.prototype.choices = function (arr, w) {
  let tot = 0; for (const x of w) tot += x;
  let r = this._next() * tot;
  for (let i = 0; i < arr.length; i++) { r -= w[i]; if (r <= 0) return arr[i]; }
  return arr[arr.length - 1];
};

/* ── hex core (odd-q, flat-top) ─────────────────────────────────────────── */
const EVEN = [[1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [0, 1]];
const ODD  = [[1, 1], [1, 0], [0, -1], [-1, 0], [-1, 1], [0, 1]];
const CUBE_DIRS = [[1, -1, 0], [1, 0, -1], [0, 1, -1],
                   [-1, 1, 0], [-1, 0, 1], [0, -1, 1]];

const key = (c, r) => c + ',' + r;
function cube(c, r) { const x = c, z = r - ((c - (c & 1)) >> 1); return [x, -x - z, z]; }
function offset(x, y, z) { return [x, z + Math.floor((x - (x & 1)) / 2)]; }
function dist(a, b) {
  const A = cube(a[0], a[1]), B = cube(b[0], b[1]);
  return (Math.abs(A[0] - B[0]) + Math.abs(A[1] - B[1]) + Math.abs(A[2] - B[2])) / 2;
}
function nbrCoords(c, r) {
  const d = (c % 2 === 0) ? EVEN : ODD;
  return d.map(([dc, dr]) => [c + dc, r + dr]);
}

function HexMap(w, h, fill) {
  this.width = w; this.height = h; this.cells = new Map();
  for (let c = 0; c < w; c++) for (let r = 0; r < h; r++)
    this.cells.set(key(c, r), { col: c, row: r, terrain: fill || 'plains',
                                resource: null, region: null, tactical: null });
}
HexMap.prototype.inb = function (co) {
  return co[0] >= 0 && co[0] < this.width && co[1] >= 0 && co[1] < this.height;
};
HexMap.prototype.get = function (co) { return this.cells.get(key(co[0], co[1])); };
HexMap.prototype.all = function () { return Array.from(this.cells.values()); };
HexMap.prototype.nbrs = function (co) {
  const out = [];
  for (const n of nbrCoords(co[0], co[1])) if (this.inb(n)) out.push(this.get(n));
  return out;
};
HexMap.prototype.count = function (t) {
  let n = 0; for (const h of this.cells.values()) if (h.terrain === t) n++; return n;
};
HexMap.prototype.within = function (co, rad) {
  const out = [];
  for (const h of this.cells.values())
    if (dist(co, [h.col, h.row]) <= rad) out.push(h);
  return out;
};

/* ── tables (from mapgen.py) ────────────────────────────────────────────── */
const PARAMS = { width: 32, height: 26, players: 6, seed: 7,
  settlement_range: 5, settlement_range_max: 7, first_settle_range: 4,
  region_core: 2, cluster_cap: 30 };
const MIN_NODE = 5, BIG_NODE = 16;
const MARK_MIN = { forest: 12, wetland: 12, tundra: 5, plains: 5 };
const RESOURCE_BY_TERRAIN = {
  plains: ['arable', 'apiary'], forest: ['forestry', 'apiary'],
  wetland: ['forestry'], tundra: ['quarry', 'salt'], mountain: ['mine', 'quarry'] };
const RESOURCE_MIN = { mine: 3, quarry: 3, arable: 3, forestry: 3, apiary: 2, salt: 2 };
const TOPUP_TERRAINS = { arable: ['plains'], apiary: ['plains', 'forest'],
  forestry: ['forest', 'wetland'], salt: ['tundra'], quarry: ['tundra'], mine: [] };
const MATERIAL_TERRAINS = ['forest', 'mountain', 'tundra', 'wetland', 'water'];
const PASSABLE = ['plains', 'forest', 'wetland', 'tundra'];

const LAYOUTS = {
  1: [[0.5, 0.5]], 2: [[0.18, 0.5], [0.82, 0.5]],
  3: [[0.18, 0.2], [0.82, 0.2], [0.5, 0.82]],
  4: [[0.16, 0.18], [0.84, 0.18], [0.16, 0.82], [0.84, 0.82]],
  5: [[0.16, 0.18], [0.84, 0.18], [0.16, 0.82], [0.84, 0.82], [0.5, 0.5]],
  6: [[0.16, 0.2], [0.5, 0.16], [0.84, 0.2], [0.16, 0.8], [0.5, 0.84], [0.84, 0.8]],
  7: [[0.16, 0.2], [0.5, 0.16], [0.84, 0.2], [0.16, 0.8], [0.5, 0.84], [0.84, 0.8], [0.5, 0.5]] };

/* ── settlement placement (port of mapgen._place_regions) ───────────────── */
function placeRegions(m, p, rng) {
  const n = p.players;
  const fracs = (LAYOUTS[n] || LAYOUTS[6]).slice(0, n);
  const anchors = fracs.map(([fc, fr]) => {
    let c = Math.floor(m.width * fc), r = Math.floor(m.height * fr);
    c = Math.min(m.width - 3, Math.max(2, c + rng.randint(-1, 1)));
    r = Math.min(m.height - 3, Math.max(2, r + rng.randint(-1, 1)));
    return [c, r];
  });
  const SEP = p.settlement_range, SMAX = p.settlement_range_max,
        FIRST = p.first_settle_range;
  const buildable = (c) => m.inb(c) && ['water', 'mountain'].indexOf(m.get(c).terrain) < 0;
  m.settlements = []; m.centers = [];

  fracs.forEach(([fx, fy], rid) => {
    const a = anchors[rid];
    const corner = (Math.abs(fx - 0.5) < 0.12 || Math.abs(fy - 0.5) < 0.12) ? a
      : [fx < 0.5 ? 0 : m.width - 1, fy < 0.5 ? 0 : m.height - 1];
    const interior = m.within(corner, FIRST + 1)
      .filter(h => m.nbrs([h.col, h.row]).length === 6).map(h => [h.col, h.row]);
    let cap = corner;
    if (interior.length) {
      cap = interior.reduce((b, c) => dist(c, corner) < dist(b, corner) ? c : b);
    }
    [cap].concat(m.nbrs(cap).map(h => [h.col, h.row]))
      .forEach(c => { m.get(c).terrain = 'plains'; });

    const pick = (existing) => {
      const cells = m.within(corner, FIRST + SMAX)
        .map(h => [h.col, h.row])
        .filter(c => buildable(c) && existing.every(o => {
          const d = dist(c, o); return d >= SEP && d <= SMAX; }));
      if (!cells.length) return null;
      let best = null, bs = Infinity;
      for (const c of cells) {
        const s = dist(c, corner) + rng.random();
        if (s < bs) { bs = s; best = c; }
      }
      return best;
    };
    let s2 = pick([cap]);
    let s3 = s2 ? pick([cap, s2]) : null;
    if (!s2) s2 = cap;
    if (!s3) s3 = s2;
    const settles = [cap, s2, s3];
    for (const s of settles) {
      const h = m.get(s);
      if (h.terrain === 'water' || h.terrain === 'mountain') h.terrain = 'plains';
      h.region = rid;
    }
    m.settlements.push(settles);
    m.centers.push([Math.round((settles[0][0] + settles[1][0] + settles[2][0]) / 3),
                    Math.round((settles[0][1] + settles[1][1] + settles[2][1]) / 3)]);
    for (const s of settles)
      for (const h of m.within(s, 1)) m.reserved.add(key(h.col, h.row));
    for (const s of settles)
      for (const h of m.within(s, p.region_core))
        if (h.region === null && h.terrain !== 'water') h.region = rid;
  });
  return anchors;
}

/* ── components / spreading ─────────────────────────────────────────────── */
function component(m, start, terrain, visited) {
  const comp = [], stack = [[start.col, start.row]];
  while (stack.length) {
    const c = stack.pop(), k = key(c[0], c[1]);
    if (visited.has(k)) continue;
    const h = m.get(c);
    if (!h || h.terrain !== terrain) continue;
    visited.add(k); comp.push(c);
    for (const nb of m.nbrs(c)) if (!visited.has(key(nb.col, nb.row))) stack.push([nb.col, nb.row]);
  }
  return comp;
}
function spreadPicks(comp, k) {
  let best = comp[0], bs = Infinity;
  for (const c of comp) { let s = 0; for (const x of comp) s += dist(c, x);
    if (s < bs) { bs = s; best = c; } }
  const picks = [best];
  while (picks.length < k && picks.length < comp.length) {
    let far = null, fs = -1;
    for (const c of comp) {
      let mn = Infinity; for (const q of picks) mn = Math.min(mn, dist(c, q));
      if (mn > fs) { fs = mn; far = c; }
    }
    picks.push(far);
  }
  return picks;
}

/* ── borders ────────────────────────────────────────────────────────────── */
function resolveBorders(spec, players, rng, w, h, mirror) {
  const one = (v, length) => {
    let wd, sp;
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      wd = v.width === undefined ? 1 : v.width;
      wd = Array.isArray(wd) ? rng.randint(wd[0], wd[1]) : wd;
      sp = v.span === undefined ? 1 : v.span;
      sp = Array.isArray(sp) ? rng.uniform(sp[0], sp[1]) : sp;
    } else {
      wd = Array.isArray(v) ? rng.randint(v[0], v[1]) : (v || 0);
      sp = 1;
    }
    if (wd <= 0) return [0, 0, -1];
    const run = Math.max(1, Math.round(sp * length));
    const lo = rng.randint(0, Math.max(0, length - run));
    return [wd, lo, lo + run - 1];
  };
  if (typeof spec === 'number') { const o = {}; for (const e of 'nsew') o[e] = spec; spec = o; }
  spec = Object.assign({}, spec);
  if (mirror === 'auto') mirror = players <= 2 ? 'ew' : ([4, 5].indexOf(players) >= 0 ? 'all' : 'ns');
  const out = {};
  if (mirror === 'all') { const v = one(spec.n || 0, w); for (const e of 'nsew') out[e] = v; return out; }
  const pair = mirror === 'ns' ? ['n', 's'] : (mirror === 'ew' ? ['e', 'w'] : null);
  if (pair) {
    const v = one(spec[pair[0]] || 0, pair[0] === 'n' ? w : h);
    out[pair[0]] = v; out[pair[1]] = v;
  }
  for (const e of 'nsew') if (!(e in out)) out[e] = one(spec[e] || 0, 'ns'.indexOf(e) >= 0 ? w : h);
  return out;
}
function borderWater(m, edges) {
  const g = (e) => edges[e] || [0, 0, -1];
  const [wn, ln, hn] = g('n'), [ws, ls, hs] = g('s'), [ww, lw, hw] = g('w'), [we, le, he] = g('e');
  for (const h of m.all()) {
    if ((h.row < wn && h.col >= ln && h.col <= hn) ||
        (m.height - 1 - h.row < ws && h.col >= ls && h.col <= hs) ||
        (h.col < ww && h.row >= lw && h.row <= hw) ||
        (m.width - 1 - h.col < we && h.row >= le && h.row <= he)) h.terrain = 'water';
  }
}

/* ── primitives ─────────────────────────────────────────────────────────── */
function pourSubstrate(m, terrain, skip) {
  for (const h of m.all()) {
    if (h.terrain === 'water' || skip.has(key(h.col, h.row))) continue;
    h.terrain = terrain;
  }
}
function carveClearing(m, centre, radius, terrain) {
  terrain = terrain || 'plains';
  for (const h of m.within(centre, radius)) {
    if (h.terrain !== 'water' && h.terrain !== terrain) {
      m.carved.add(key(h.col, h.row)); h.terrain = terrain;
    }
  }
}
function carveRoute(m, a, b, width, terrain, temp, rng) {
  terrain = terrain || 'plains'; width = width || 1; temp = temp === undefined ? 0.8 : temp;
  let cur = a, laid = 0;
  const budget = 8 * dist(a, b) + 30;
  for (let i = 0; i < budget; i++) {
    const h = m.get(cur);
    if (h && h.terrain !== 'water' && h.terrain !== terrain) {
      m.carved.add(key(cur[0], cur[1])); h.terrain = terrain; laid++;
    }
    if (width > 1) for (const nb of m.nbrs(cur))
      if (nb.terrain !== 'water' && nb.terrain !== terrain) {
        m.carved.add(key(nb.col, nb.row)); nb.terrain = terrain; laid++;
      }
    if (cur[0] === b[0] && cur[1] === b[1]) break;
    const ns = m.nbrs(cur).filter(n => n.terrain !== 'water').map(n => [n.col, n.row]);
    if (!ns.length) break;
    const d0 = dist(cur, b);
    const ws = ns.map(c => Math.exp(-(dist(c, b) - d0) / Math.max(temp, 1e-3)));
    cur = rng.choices(ns, ws);
  }
  return laid;
}
function routeNetwork(m, pts, extra, width, temp, rng) {
  if (pts.length < 2) return;
  const linked = [pts[0]]; const rest = pts.slice(1);
  while (rest.length) {
    let ba = null, bb = null, bd = Infinity, bi = -1;
    linked.forEach(x => rest.forEach((y, j) => {
      const d = dist(x, y); if (d < bd) { bd = d; ba = x; bb = y; bi = j; } }));
    carveRoute(m, ba, bb, width, 'plains', temp, rng);
    linked.push(bb); rest.splice(bi, 1);
  }
  const pairs = [];
  for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++)
    pairs.push([pts[i], pts[j], dist(pts[i], pts[j])]);
  pairs.sort((x, y) => x[2] - y[2]);
  for (let i = 0; i < Math.max(0, extra) && i < pairs.length; i++)
    carveRoute(m, pairs[i][0], pairs[i][1], width, 'plains', temp, rng);
}

/* Rivers: heading momentum, loop cutting, thinning. Both ends off-map. */
function carveRiver(m, count, rng, temp, turnP) {
  temp = temp === undefined ? 1.0 : temp; turnP = turnP === undefined ? 0.38 : turnP;
  const depth = (c) => Math.min(c[0], m.width - 1 - c[0], c[1], m.height - 1 - c[1]);
  const inland = Math.max(2, Math.floor(Math.min(m.width, m.height) / 4));
  const bw = m.borders || {};
  const wet = new Set(['n', 's', 'e', 'w'].filter(e => (bw[e] || [0])[0] > 0));
  const side = (c) => c[1] === 0 ? 'n' : (c[1] === m.height - 1 ? 's'
    : (c[0] === 0 ? 'w' : (c[0] === m.width - 1 ? 'e' : null)));
  const edges = m.all().filter(h => h.col === 0 || h.col === m.width - 1
    || h.row === 0 || h.row === m.height - 1).map(h => [h.col, h.row]);
  if (edges.length < 2) return 0;
  const mouths = edges.concat(edges.filter(c => wet.has(side(c))));
  let laid = 0;
  for (let n = 0; n < count; n++) {
    const a = rng.choice(mouths);
    const far = edges.filter(c => dist(c, a) >= Math.floor(Math.max(m.width, m.height) / 2)
      && depth([Math.floor((c[0] + a[0]) / 2), Math.floor((c[1] + a[1]) / 2)]) >= inland);
    if (!far.length) continue;
    const b = rng.choice(far);
    let path = [a], cur = a, wentInland = false;
    let heading = 0, bd = -1;
    for (let d = 0; d < 6; d++) {
      const o = offset(cube(a[0], a[1])[0] + CUBE_DIRS[d][0],
                       cube(a[0], a[1])[1] + CUBE_DIRS[d][1],
                       cube(a[0], a[1])[2] + CUBE_DIRS[d][2]);
      if (depth(o) > bd) { bd = depth(o); heading = d; }
    }
    const budget = 8 * dist(a, b) + 30;
    for (let i = 0; i < budget; i++) {
      if (rng.random() < turnP) heading = (heading + (rng.random() < 0.5 ? 5 : 1)) % 6;
      else if (rng.random() < (1 / Math.max(temp, 0.2)) * 0.10) {
        let bh = heading, bs = Infinity;
        for (const k of [-1, 0, 1]) {
          const d2 = ((heading + k) % 6 + 6) % 6;
          const cu = cube(cur[0], cur[1]);
          const o = offset(cu[0] + CUBE_DIRS[d2][0], cu[1] + CUBE_DIRS[d2][1], cu[2] + CUBE_DIRS[d2][2]);
          if (dist(o, b) < bs) { bs = dist(o, b); bh = d2; }
        }
        heading = bh;
      }
      const cu = cube(cur[0], cur[1]);
      let nxt = offset(cu[0] + CUBE_DIRS[heading][0], cu[1] + CUBE_DIRS[heading][1],
                       cu[2] + CUBE_DIRS[heading][2]);
      if (!m.inb(nxt)) {
        if (wentInland) break;
        let ok = false;
        for (const k of [1, -1, 2, -2, 3]) {
          const h2 = ((heading + k) % 6 + 6) % 6;
          const cand = offset(cu[0] + CUBE_DIRS[h2][0], cu[1] + CUBE_DIRS[h2][1], cu[2] + CUBE_DIRS[h2][2]);
          if (m.inb(cand) && !path.some(q => q[0] === cand[0] && q[1] === cand[1])) {
            heading = h2; nxt = cand; ok = true; break;
          }
        }
        if (!ok) break;
      }
      const idx = path.findIndex(q => q[0] === nxt[0] && q[1] === nxt[1]);
      if (idx >= 0) { path = path.slice(0, idx + 1); cur = nxt; continue; }
      path.push(nxt); cur = nxt;
      if (depth(cur) >= inland) wentInland = true;
      if (cur[0] === b[0] && cur[1] === b[1] && wentInland) break;
    }
    for (let i = 1; i < path.length - 1;) {
      if (dist(path[i - 1], path[i + 1]) <= 1) path.splice(i, 1); else i++;
    }
    for (const c of path) {
      const h = m.get(c);
      if (h && h.terrain !== 'water') { h.terrain = 'water'; laid++; }
    }
  }
  return laid;
}

/* Flatten confluences: rivers are drawn as layers, so crossings bulge. */
function thinWater(m, protect) {
  let changed = true;
  while (changed) {
    changed = false;
    for (const h of m.all()) {
      if (h.terrain !== 'water' || protect.has(key(h.col, h.row))) continue;
      const wn = m.nbrs([h.col, h.row]).filter(n => n.terrain === 'water')
        .map(n => [n.col, n.row]);
      if (wn.length < 3) continue;
      const seen = new Set(), stack = [wn[0]], me = key(h.col, h.row);
      while (stack.length) {
        const c = stack.pop(), k = key(c[0], c[1]);
        if (seen.has(k) || k === me) continue;
        if (m.get(c).terrain !== 'water') continue;
        seen.add(k);
        for (const nb of m.nbrs(c)) {
          const k2 = key(nb.col, nb.row);
          if (!seen.has(k2) && k2 !== me) stack.push([nb.col, nb.row]);
        }
      }
      if (wn.every(w => seen.has(key(w[0], w[1])))) { h.terrain = 'plains'; changed = true; }
    }
  }
}

function carveMaze(m, count, rng, temp, junctionP) {
  if (count <= 0) return 0;
  const rim = m.all().filter(h => h.terrain !== 'water' &&
    (m.nbrs([h.col, h.row]).some(n => n.terrain === 'water')
      || h.col === 0 || h.col === m.width - 1 || h.row === 0 || h.row === m.height - 1))
    .map(h => [h.col, h.row]);
  if (rim.length < 2) return 0;
  let junction = null;
  if (rng.random() < junctionP) {
    const mid = [Math.floor(m.width / 2), Math.floor(m.height / 2)];
    const plains = m.all().filter(h => h.terrain === 'plains').map(h => [h.col, h.row]);
    const inner = m.all().filter(h => h.terrain !== 'water' && h.terrain !== 'plains'
      && dist([h.col, h.row], mid) <= Math.floor(Math.max(m.width, m.height) / 3))
      .map(h => [h.col, h.row]);
    if (inner.length) {
      let best = null, bs = -Infinity;
      for (const c of inner) {
        let mn = 99; for (const q of plains) mn = Math.min(mn, dist(c, q));
        const s = mn - 0.15 * dist(c, mid);
        if (s > bs) { bs = s; best = c; }
      }
      junction = best;
    }
  }
  let laid = 0; const used = [];
  for (let i = 0; i < count; i++) {
    let pool = rim.filter(c => used.every(u => dist(c, u) >= 6));
    if (!pool.length) pool = rim;
    const a = rng.choice(pool);
    let b = null, bs = -Infinity;
    for (const c of rim) {
      const s = dist(c, a) - 3 * used.filter(u => dist(c, u) < 6).length;
      if (s > bs) { bs = s; b = c; }
    }
    used.push(a, b);
    if (junction) {
      laid += carveRoute(m, a, junction, 1, 'plains', temp, rng);
      laid += carveRoute(m, junction, b, 1, 'plains', temp, rng);
    } else laid += carveRoute(m, a, b, 1, 'plains', temp, rng);
  }
  return laid;
}

function blob(m, seed, size, terrain, ok, buffers, substrate) {
  if (!ok(m.get(seed)) || !clearPW(m, seed, terrain, new Set(), buffers, substrate)) return 0;
  m.get(seed).terrain = terrain;
  const filled = new Set([key(seed[0], seed[1])]);
  const coords = [seed];
  let placed = 1;
  while (placed < size) {
    const frontier = [];
    const fset = new Set();
    for (const c of coords) for (const nb of m.nbrs(c)) {
      const k = key(nb.col, nb.row);
      if (!filled.has(k) && !fset.has(k) && ok(nb)
          && clearPW(m, [nb.col, nb.row], terrain, filled, buffers, substrate)) {
        fset.add(k); frontier.push([nb.col, nb.row]);
      }
    }
    if (!frontier.length) break;
    let nxt = frontier[0], bd = Infinity;
    for (const c of frontier) { const d = dist(seed, c); if (d < bd) { bd = d; nxt = c; } }
    m.get(nxt).terrain = terrain; filled.add(key(nxt[0], nxt[1])); coords.push(nxt); placed++;
  }
  return placed;
}
function clearPW(m, coord, terrain, own, buffers, substrate) {
  for (const nb of m.nbrs(coord)) {
    const t = nb.terrain;
    if (t === 'plains' || t === terrain || t === substrate || own.has(key(nb.col, nb.row))) continue;
    if (buffers.has([terrain, t].sort().join('|'))) return false;
  }
  return true;
}
function stampBlobs(m, terrain, target, ok, buffers, substrate, rng, lo, hi) {
  lo = lo || 9; hi = hi || 16;
  let guard = 0;
  while (m.count(terrain) < target && guard < 400) {
    guard++;
    const cands = m.all().filter(h => ok(h)
      && clearPW(m, [h.col, h.row], terrain, new Set(), buffers, substrate))
      .map(h => [h.col, h.row]);
    if (!cands.length) break;
    const existing = m.all().filter(h => h.terrain === terrain).map(h => [h.col, h.row]);
    const sample = rng.sample(cands, Math.min(cands.length, 80));
    let seed;
    if (existing.length) {
      let bs = -1;
      for (const c of sample) {
        let mn = Infinity; for (const e of existing) mn = Math.min(mn, dist(c, e));
        if (mn > bs) { bs = mn; seed = c; }
      }
    } else seed = rng.choice(sample);
    const want = Math.min(rng.randint(lo, hi), target - m.count(terrain));
    blob(m, seed, Math.max(1, want), terrain, ok, buffers, substrate);
  }
}
function stampBand(m, terrain, target, edge, thickFrac, jitter, ok, rng, span) {
  /* `span` is the fraction of the cross axis a band covers, at a random
     offset. At 1.0 a band reaches edge to edge and is a real wall — right for
     Hermit's Row, whose ranges exist to be held at a narrows. Below 1.0 it is
     a ridge with open ground at one or both ends. Two ridges may share an
     across-position when their spans don't overlap, or partial bands could
     never reach the share target. */
  span = span === undefined ? 1.0 : span;
  const vertical = (edge === 'e' || edge === 'w');
  const across = vertical ? m.width : m.height;
  const cross = vertical ? m.height : m.width;
  const thick = Math.max(1, Math.round(thickFrac * across));
  const used = []; let guard = 0;
  while (m.count(terrain) < target && guard < 30) {
    guard++;
    const sp = Array.isArray(span) ? rng.uniform(span[0], span[1]) : span;
    const run = Math.max(1, Math.round(Math.min(1, sp) * cross));
    const start = rng.randint(0, Math.max(0, cross - run));
    const cands = [];
    for (let p = 2; p < across - 2; p++)
      if (used.every(u => Math.abs(p - u[0]) >= thick + 2
                       || start > u[2] || start + run < u[1])) cands.push(p);
    if (!cands.length) break;
    const pos = rng.choice(cands); used.push([pos, start, start + run]);
    let centre = pos;
    for (let k = start; k < start + run; k++) {
      if (rng.random() < jitter) centre += (rng.random() < 0.5 ? -1 : 1);
      centre = Math.max(1, Math.min(across - 2, centre));
      for (let d = 0; d < thick; d++) {
        const pp = centre + d - Math.floor(thick / 2);
        const co = vertical ? [pp, k] : [k, pp];
        const h = m.get(co);
        if (h && ok(h)) h.terrain = terrain;
      }
    }
  }
}
function stampScatter(m, terrain, count, lo, hi, minSep, ok, rng, chain, chainRange, widen) {
  chain = chain || 0; chainRange = chainRange || 5; widen = widen || 0;
  const seeds = []; let guard = 0;
  while (seeds.length < count && guard < 3000) {
    guard++;
    const cands = m.all().filter(ok).map(h => [h.col, h.row]);
    if (!cands.length) break;
    const c = rng.choice(cands);
    if (seeds.some(s => dist(c, s) < minSep)) continue;
    seeds.push(c);
    blob(m, c, rng.randint(lo, hi), terrain, ok, new Set(), terrain);
  }
  /* Join some peaks into short ridges. Each peak may be joined ONCE: without
     that cap the spurs cascade transitively and a scatter meant to read as
     broken country grows a 20-hex wall. */
  if (chain > 0 && seeds.length > 1) {
    const linked = new Set();
    const kk = (c) => c[0] + ',' + c[1];
    for (const a of seeds) {
      if (linked.has(kk(a)) || rng.random() >= chain) continue;
      const near = seeds.filter(b => kk(b) !== kk(a) && !linked.has(kk(b))
        && dist(a, b) <= chainRange);
      if (!near.length) continue;
      let b = near[0], bd = Infinity;
      for (const q of near) { const d = dist(a, q); if (d < bd) { bd = d; b = q; } }
      linked.add(kk(a)); linked.add(kk(b));
      let cur = a, g = 0;
      while ((cur[0] !== b[0] || cur[1] !== b[1]) && g < 12) {
        g++;
        let step = null, sd = Infinity;
        for (const n of m.nbrs(cur)) {
          const d = dist([n.col, n.row], b);
          if (d < sd) { sd = d; step = [n.col, n.row]; }
        }
        if (!step || dist(step, b) >= dist(cur, b)) break;
        const h = m.get(step);
        if (h && ok(h)) h.terrain = terrain;
        if (widen && rng.random() < widen) {
          for (const nb of m.nbrs(step)) { if (ok(nb)) { nb.terrain = terrain; break; } }
        }
        cur = step;
      }
    }
  }
  return seeds.length;
}
function stampMassif(m, terrain, count, lo, hi, minSep, bbox, keepout, ok, rng) {
  /* Chunky bounded blocks. Any hex that would push the cluster's bounding box
     past `bbox` is refused, so a massif stays a block rather than sprawling
     into a range; `keepout` bars seeding near the board centre, where high
     ground would cut the map in half. */
  const mid = [Math.floor(m.width / 2), Math.floor(m.height / 2)];
  const seeds = []; let guard = 0;
  while (seeds.length < count && guard < 2000) {
    guard++;
    const cands = m.all().filter(h => ok(h) && dist([h.col, h.row], mid) >= keepout)
      .map(h => [h.col, h.row]);
    if (!cands.length) break;
    const c = rng.choice(cands);
    if (seeds.some(s => dist(c, s) < minSep)) continue;
    seeds.push(c);
    if (!ok(m.get(c))) continue;
    m.get(c).terrain = terrain;
    const filled = [c]; const fk = new Set([key(c[0], c[1])]);
    const want = rng.randint(lo, hi);
    while (filled.length < want) {
      let loC = Infinity, hiC = -Infinity, loR = Infinity, hiR = -Infinity;
      for (const f of filled) {
        loC = Math.min(loC, f[0]); hiC = Math.max(hiC, f[0]);
        loR = Math.min(loR, f[1]); hiR = Math.max(hiR, f[1]);
      }
      const frontier = []; const seen = new Set();
      for (const f of filled) for (const nb of m.nbrs(f)) {
        const k = key(nb.col, nb.row);
        if (fk.has(k) || seen.has(k) || !ok(nb)) continue;
        if (Math.max(hiC, nb.col) - Math.min(loC, nb.col) >= bbox) continue;
        if (Math.max(hiR, nb.row) - Math.min(loR, nb.row) >= bbox) continue;
        seen.add(k); frontier.push([nb.col, nb.row]);
      }
      if (!frontier.length) break;
      let nxt = frontier[0], bd = Infinity;
      for (const q of frontier) { const d = dist(c, q); if (d < bd) { bd = d; nxt = q; } }
      m.get(nxt).terrain = terrain; fk.add(key(nxt[0], nxt[1])); filled.push(nxt);
    }
  }
  return seeds.length;
}

function stampPerimeter(m, terrain, count, length, width, depth, ok, rng, jitter) {
  /* Long thin ranges running PARALLEL to the nearest board edge and set back
     from it, so they frame a region along its margins instead of crossing it. */
  jitter = jitter === undefined ? 0.30 : jitter;
  for (let i = 0; i < count; i++) {
    const band = m.all().filter(h => ok(h) && (() => {
      const d = Math.min(h.col, m.width - 1 - h.col, h.row, m.height - 1 - h.row);
      return d >= depth[0] && d <= depth[1];
    })()).map(h => [h.col, h.row]);
    if (!band.length) break;
    const start = rng.choice(band);
    const dd = { w: start[0], e: m.width - 1 - start[0],
                 n: start[1], s: m.height - 1 - start[1] };
    let near = 'w'; for (const k of ['w', 'e', 'n', 's']) if (dd[k] < dd[near]) near = k;
    const vertical = (near === 'w' || near === 'e');
    const step = rng.random() < 0.5 ? -1 : 1;
    const cur = start.slice();
    const run = rng.randint(length[0], length[1]);
    for (let t = 0; t < run; t++) {
      const wdt = rng.randint(width[0], width[1]);
      for (let k = 0; k < wdt; k++) {
        const c = vertical ? [cur[0], cur[1] + k] : [cur[0] + k, cur[1]];
        const h = m.get(c);
        if (h && ok(h)) h.terrain = terrain;
      }
      if (vertical) { cur[1] += step; if (rng.random() < jitter) cur[0] += (rng.random() < 0.5 ? -1 : 1); }
      else { cur[0] += step; if (rng.random() < jitter) cur[1] += (rng.random() < 0.5 ? -1 : 1); }
      if (!m.inb(cur)) break;
    }
  }
}

function stampFringe(m, terrain, target, ok, rng, depth) {
  depth = depth === undefined ? 3 : depth;
  const cands = m.all().filter(ok);
  const d = (h) => Math.min(h.col, m.width - 1 - h.col, h.row, m.height - 1 - h.row);
  cands.sort((a, b) => d(a) - d(b));
  let n = 0;
  for (const h of cands) {
    if (n >= target) break;
    if (d(h) > depth && n >= target * 0.6) break;
    h.terrain = terrain; n++;
  }
  return n;
}

/* ── islands (water substrate) ──────────────────────────────────────────── */
function groupRegions(m, k) {
  const ctrs = m.centers;
  if (k >= ctrs.length) return m.settlements.map(st => st.slice());
  const picks = [ctrs[0]];
  while (picks.length < k) {
    let far = null, fs = -1;
    for (const c of ctrs) {
      let mn = Infinity; for (const q of picks) mn = Math.min(mn, dist(c, q));
      if (mn > fs) { fs = mn; far = c; }
    }
    picks.push(far);
  }
  const groups = picks.map(() => []);
  m.settlements.forEach((st, i) => {
    let bi = 0, bd = Infinity;
    picks.forEach((p, j) => { const d = dist(m.centers[i], p); if (d < bd) { bd = d; bi = j; } });
    groups[bi] = groups[bi].concat(st);
  });
  return groups.filter(g => g.length);
}
function liftIslands(m, groups, sizeRng, rng, islets, landTarget, gap) {
  islets = islets || [0, 0]; landTarget = landTarget === undefined ? 0.55 : landTarget;
  gap = gap || [2, 4];
  let budget = Math.floor(landTarget * m.width * m.height) - m.count('plains');
  for (const grp of groups) {
    let want = Math.floor(rng.randint(sizeRng[0], sizeRng[1]) * Math.max(1, grp.length / 3));
    want = Math.max(grp.length * 8, Math.min(want, Math.floor(budget / Math.max(1, groups.length))));
    const filled = new Set(grp.map(c => key(c[0], c[1])));
    const coords = grp.slice();
    for (const c of grp) { const h = m.get(c); if (h && h.terrain === 'water') h.terrain = 'plains'; }
    const anchor = grp[0];
    for (const c of grp) {
      let cur = c;
      while (!(cur[0] === anchor[0] && cur[1] === anchor[1])) {
        let nx = null, bd = Infinity;
        for (const n of m.nbrs(cur)) { const d = dist([n.col, n.row], anchor);
          if (d < bd) { bd = d; nx = [n.col, n.row]; } }
        if (!nx || dist(nx, anchor) >= dist(cur, anchor)) break;
        const h = m.get(nx); if (h.terrain === 'water') h.terrain = 'plains';
        if (!filled.has(key(nx[0], nx[1]))) { filled.add(key(nx[0], nx[1])); coords.push(nx); }
        cur = nx;
      }
    }
    while (coords.length < want) {
      const frontier = []; const fset = new Set();
      for (const c of coords) for (const nb of m.nbrs(c)) {
        const k = key(nb.col, nb.row);
        if (!filled.has(k) && !fset.has(k) && nb.terrain === 'water') {
          fset.add(k); frontier.push([nb.col, nb.row]);
        }
      }
      if (!frontier.length) break;
      let nxt = frontier[0], bs = Infinity;
      for (const c of frontier) {
        let mn = Infinity; for (const g of grp) mn = Math.min(mn, dist(c, g));
        const s = mn + rng.random() * 2;
        if (s < bs) { bs = s; nxt = c; }
      }
      m.get(nxt).terrain = 'plains'; filled.add(key(nxt[0], nxt[1])); coords.push(nxt);
    }
  }
  const [nIslet, sz] = islets;
  for (let i = 0; i < nIslet; i++) {
    const land = m.all().filter(h => h.terrain !== 'water').map(h => [h.col, h.row]);
    const open = m.all().filter(h => h.terrain === 'water'
      && m.nbrs([h.col, h.row]).every(n => n.terrain === 'water')).map(h => [h.col, h.row]);
    let cands = open.filter(c => {
      let mn = 99; for (const l of land) mn = Math.min(mn, dist(c, l));
      return mn >= gap[0] && mn <= gap[1];
    });
    if (!cands.length) cands = open;
    if (!cands.length) break;
    const seed = rng.choice(cands);
    const filled = new Set([key(seed[0], seed[1])]); const coords = [seed];
    m.get(seed).terrain = 'plains';
    while (coords.length < sz) {
      const frontier = []; const fset = new Set();
      for (const c of coords) for (const nb of m.nbrs(c)) {
        const k = key(nb.col, nb.row);
        if (!fset.has(k) && nb.terrain === 'water') { fset.add(k); frontier.push([nb.col, nb.row]); }
      }
      if (!frontier.length) break;
      let nxt = frontier[0], bs = Infinity;
      for (const c of frontier) { const s = dist(c, seed) + rng.random(); if (s < bs) { bs = s; nxt = c; } }
      m.get(nxt).terrain = 'plains'; filled.add(key(nxt[0], nxt[1])); coords.push(nxt);
    }
  }
}

/* ── housekeeping ───────────────────────────────────────────────────────── */
function cullSmall(m, substrate, palette, exempt) {
  for (const terrain of ['forest', 'wetland', 'tundra']) {
    if (terrain === substrate || palette.indexOf(terrain) < 0 || exempt.indexOf(terrain) >= 0) continue;
    const seen = new Set();
    for (const h of m.all()) if (h.terrain === terrain && !seen.has(key(h.col, h.row))) {
      const comp = component(m, h, terrain, seen);
      if (comp.length < MIN_NODE) for (const c of comp) m.get(c).terrain = 'plains';
    }
  }
}
function capComponents(m, cap, substrate, palette, exempt) {
  for (const terrain of ['forest', 'wetland', 'tundra']) {
    if (terrain === substrate || palette.indexOf(terrain) < 0 || exempt.indexOf(terrain) >= 0) continue;
    const seen = new Set();
    for (const h of m.all()) if (h.terrain === terrain && !seen.has(key(h.col, h.row))) {
      let comp = component(m, h, terrain, seen);
      while (comp.length > cap) {
        const peri = comp.filter(c => m.nbrs(c).some(n => n.terrain === 'plains'));
        if (!peri.length) break;
        let worst = peri[0], bs = -1;
        for (const c of peri) {
          const s = m.nbrs(c).filter(n => n.terrain === 'plains').length;
          if (s > bs) { bs = s; worst = c; }
        }
        m.get(worst).terrain = 'plains';
        comp = comp.filter(c => !(c[0] === worst[0] && c[1] === worst[1]));
      }
    }
  }
}
function reachable(m, start, seaHop) {
  seaHop = seaHop !== false;
  const seen = new Set(), stack = [start];
  while (stack.length) {
    const c = stack.pop(), k = key(c[0], c[1]);
    if (seen.has(k)) continue;
    const h = m.get(c);
    if (!h || PASSABLE.indexOf(h.terrain) < 0) continue;
    seen.add(k);
    for (const nb of m.nbrs(c)) {
      if (seen.has(key(nb.col, nb.row))) continue;
      if (PASSABLE.indexOf(nb.terrain) >= 0) stack.push([nb.col, nb.row]);
      else if (seaHop && nb.terrain === 'water')
        for (const far of m.nbrs([nb.col, nb.row]))
          if (PASSABLE.indexOf(far.terrain) >= 0 && !seen.has(key(far.col, far.row)))
            stack.push([far.col, far.row]);
    }
  }
  return seen;
}
function ensureConnectivity(m, rng) {
  const pts = [].concat.apply([], m.settlements);
  if (!pts.length) return;
  for (let g = 0; g < 20; g++) {
    const reach = reachable(m, pts[0]);
    const orphan = pts.find(s => !reach.has(key(s[0], s[1])));
    if (!orphan) break;
    let target = pts[0], bd = Infinity;
    for (const k of reach) {
      const c = k.split(',').map(Number);
      const d = dist(orphan, c); if (d < bd) { bd = d; target = c; }
    }
    carveRoute(m, orphan, target, 1, 'plains', 0.8, rng);
  }
}
function ensureRegionMaterial(m, p) {
  /* forest/wetland/tundra grow as small patches; mountain is the LAST resort
     and is placed as a single hex. Adding a terrain to a preset's palette to
     dodge this case would put it on every map of that region, whereas the
     shortfall usually hits one region on one seed. */
  const order = ['forest', 'wetland', 'tundra', 'mountain']
    .filter(t => p.palette.indexOf(t) >= 0 && t !== p.substrate);
  const sub = p.substrate;
  const look = (c) => m.carved.has(key(c[0], c[1])) ? sub : m.get(c).terrain;
  for (const settles of m.settlements) {
    const ring = new Set();
    for (const s of settles) {
      ring.add(key(s[0], s[1]));
      for (const n of m.nbrs(s)) ring.add(key(n.col, n.row));
    }
    for (let it = 0; it < 6; it++) {
      let best = settles[0], bn = -1;
      for (const st of settles) {
        const set = new Set();
        for (const h of m.within(st, 2)) {
          const t = look([h.col, h.row]);
          if (MATERIAL_TERRANS_HAS(t)) set.add(t);
        }
        if (set.size > bn) { bn = set.size; best = st; }
      }
      const have = new Set();
      for (const h of m.within(best, 2)) {
        const t = look([h.col, h.row]);
        if (MATERIAL_TERRANS_HAS(t)) have.add(t);
      }
      if (have.size >= 2) break;
      const pick = order.find(t => !have.has(t));
      if (!pick) break;
      const spots = m.within(best, 2).filter(h => !ring.has(key(h.col, h.row))
        && h.terrain === 'plains').map(h => [h.col, h.row]);
      if (!spots.length) break;
      let seed = spots[0], bd = -1;
      for (const c of spots) { const d = dist(c, best); if (d > bd) { bd = d; seed = c; } }
      const targets = pick === 'mountain'
        ? [seed]
        : [seed].concat(m.nbrs(seed).slice(0, 2).map(n => [n.col, n.row]));
      for (const c of targets) {
        const h = m.get(c);
        if (h && h.terrain === 'plains' && !ring.has(key(c[0], c[1]))) h.terrain = pick;
      }
    }
  }
}
function MATERIAL_TERRANS_HAS(t) { return MATERIAL_TERRAINS.indexOf(t) >= 0; }

const HILL_SEP = 4;

function markHills(m, minSep) {
  /* Hills, thinned so no two sit within minSep of each other.

     The raw rule — a plains hex ringed entirely by plains — measures how open
     a map is, not where high ground is: 9% of plains on Lost Woods, 44% on
     Hermit's Row, because any wide field is wall-to-wall "hill". Those are
     plateaus. Candidates are scored by how deep inside their own open ground
     they sit, the deepest is taken as that plateau's summit, and everything
     within minSep of it is dropped. Sparse maps barely change; open ones
     collapse to a handful of summits. */
  minSep = minSep === undefined ? HILL_SEP : minSep;
  for (const h of m.all()) h.tactical = null;
  const cand = m.all().filter(h => {
    const ns = m.nbrs([h.col, h.row]);
    return h.terrain === 'plains' && ns.length === 6
      && ns.every(n => n.terrain === 'plains');
  }).map(h => [h.col, h.row]);
  if (!cand.length) return;
  if (minSep <= 1) { for (const c of cand) m.get(c).tactical = 'hill'; return; }

  // one multi-source BFS from every obstruction gives all depths
  const depth = new Map(); const dq = [];
  for (const h of m.all()) if (h.terrain !== 'plains') {
    depth.set(key(h.col, h.row), 0); dq.push([h.col, h.row]);
  }
  let qi = 0;
  while (qi < dq.length) {
    const c = dq[qi++]; const d = depth.get(key(c[0], c[1]));
    for (const nb of m.nbrs(c)) {
      const k = key(nb.col, nb.row);
      if (!depth.has(k)) { depth.set(k, d + 1); dq.push([nb.col, nb.row]); }
    }
  }
  const dep = (c) => depth.has(key(c[0], c[1])) ? depth.get(key(c[0], c[1])) : 99;
  cand.sort((a, b) => (dep(b) - dep(a)) || (a[0] - b[0]) || (a[1] - b[1]));
  const kept = [];
  for (const c of cand) {
    if (kept.every(k => dist(c, k) >= minSep)) {
      kept.push(c); m.get(c).tactical = 'hill';
    }
  }
}
function resources(m, palette, resMin) {
  for (const h of m.all()) h.resource = null;
  for (const terrain of ['forest', 'wetland', 'tundra', 'plains']) {
    if (palette.indexOf(terrain) < 0) continue;
    const list = RESOURCE_BY_TERRAIN[terrain];
    const prim = list[0], rest = list.slice(1);
    const seen = new Set();
    for (const h of m.all()) if (h.terrain === terrain && !seen.has(key(h.col, h.row))) {
      const comp = component(m, h, terrain, seen);
      if (comp.length < MARK_MIN[terrain]) continue;
      const types = [prim].concat(comp.length >= BIG_NODE ? rest : []);
      spreadPicks(comp, types.length).forEach((c, i) => { if (types[i]) m.get(c).resource = types[i]; });
    }
  }
  if (palette.indexOf('mountain') >= 0) {
    const seen = new Set();
    for (const h of m.all()) if (h.terrain === 'mountain' && !seen.has(key(h.col, h.row))) {
      const comp = component(m, h, 'mountain', seen);
      if (comp.length < 3) continue;
      const types = ['mine'].concat(comp.length >= BIG_NODE ? ['quarry'] : []);
      spreadPicks(comp, types.length).forEach((c, i) => { if (types[i]) m.get(c).resource = types[i]; });
    }
  }
  for (const res of Object.keys(resMin)) {
    const need = resMin[res];
    if (need <= 0) continue;
    let have = m.all().filter(h => h.resource === res).length;
    if (have >= need) continue;
    let cands;
    if (res === 'mine') cands = m.all().filter(h => h.terrain === 'mountain' && !h.resource);
    else if (res === 'quarry') cands = m.all().filter(h =>
      (h.terrain === 'tundra' || h.terrain === 'mountain') && !h.resource);
    else {
      const ts = TOPUP_TERRAINS[res].filter(t => palette.indexOf(t) >= 0);
      cands = m.all().filter(h => ts.indexOf(h.terrain) >= 0 && !h.resource);
    }
    const existing = m.all().filter(h => h.resource === res).map(h => [h.col, h.row]);
    cands = cands.map(h => [h.col, h.row]).sort((a, b) => {
      const f = (c) => { let mn = 999; for (const e of existing) mn = Math.min(mn, dist(c, e)); return -mn; };
      return f(a) - f(b);
    });
    for (const c of cands) { if (have >= need) break; m.get(c).resource = res; have++; }
  }
}

/* ── validator ──────────────────────────────────────────────────────────── */
function validate(m, p) {
  const v = [];
  const resMin = Object.assign({}, RESOURCE_MIN, p.resource_min || {});
  m.settlements.forEach((settles, i) => {
    const uniq = new Set(settles.map(s => key(s[0], s[1])));
    if (uniq.size < 3) v.push(`region ${i}: only ${uniq.size} distinct settlements`);
    for (const s of settles) {
      const t = m.get(s).terrain;
      if (t === 'water' || t === 'mountain') v.push(`region ${i}: settlement on ${t}`);
    }
  });
  const sub = p.substrate;
  const look = (c) => m.carved.has(key(c[0], c[1])) ? sub : m.get(c).terrain;
  m.settlements.forEach((settles, i) => {
    let best = 0;
    for (const st of settles) {
      const set = new Set();
      for (const h of m.within(st, 2)) {
        const t = look([h.col, h.row]);
        if (MATERIAL_TERRANS_HAS(t)) set.add(t);
      }
      best = Math.max(best, set.size);
    }
    if (best < 2) v.push(`region ${i}: only ${best} material terrain(s) within range 2`);
  });
  if ((p.sea_crossing || 'base') === 'shipyard') {
    m.settlements.forEach((settles, i) => {
      const reach = reachable(m, settles[0]);
      if (settles.some(s => !reach.has(key(s[0], s[1]))))
        v.push(`region ${i}: own settlements not mutually reachable`);
    });
  } else {
    const all = [].concat.apply([], m.settlements);
    if (all.length) {
      const reach = reachable(m, all[0]);
      const orph = all.filter(s => !reach.has(key(s[0], s[1])));
      if (orph.length) v.push(`${orph.length} settlement(s) unreachable from region 0`);
    }
    for (const h of m.all()) {
      if (h.terrain !== 'water') continue;
      const runs = m.nbrs([h.col, h.row]).filter(n => n.terrain === 'water').length;
      if (runs >= 5 && h.col > 1 && h.col < m.width - 2 && h.row > 1 && h.row < m.height - 2) {
        v.push('interior open water wider than a one-hex strait'); break;
      }
    }
  }
  if (p.require_hill && !m.all().some(h => h.tactical === 'hill')) v.push('no Hill on the board');
  const have = {};
  for (const h of m.all()) if (h.resource) have[h.resource] = (have[h.resource] || 0) + 1;
  for (const r of Object.keys(resMin))
    if (resMin[r] > 0 && (have[r] || 0) < resMin[r])
      v.push(`resource ${r}: ${have[r] || 0}/${resMin[r]}`);
  return v;
}

/* ── pipeline ───────────────────────────────────────────────────────────── */
function build(p, seed) {
  const rng = new RNG(seed);
  const m = new HexMap(p.width, p.height, 'plains');
  m.reserved = new Set(); m.carved = new Set();
  const palette = p.palette, substrate = p.substrate;
  const buffers = new Set((p.buffers || []).map(b => b.slice().sort().join('|')));
  const tot = p.width * p.height;

  m.borders = resolveBorders(p.border || 0, p.players, rng, p.width, p.height,
                             p.border_mirror || 'ns');
  borderWater(m, m.borders);
  m.rim = new Set(m.all().filter(h => h.terrain === 'water').map(h => key(h.col, h.row)));

  placeRegions(m, p, rng);
  m.settlement_range = p.settlement_range;

  const carve = p.carve || {};
  if (substrate === 'water') {
    pourSubstrate(m, 'water', m.reserved);
    const k = carve.islands ? rng.randint(carve.islands[0], carve.islands[1]) : 3;
    liftIslands(m, groupRegions(m, k), carve.island_size || [60, 90], rng,
                carve.islets || [0, 0], carve.land_target === undefined ? 0.55 : carve.land_target,
                carve.gap || [2, 4]);
  } else if (substrate !== 'plains') {
    pourSubstrate(m, substrate, m.reserved);
    const cr = carve.clearing_radius === undefined ? 1 : carve.clearing_radius;
    const w = carve.width || 1;
    for (const st of m.settlements) for (const s of st) carveClearing(m, s, cr);
    routeNetwork(m, m.centers.slice(), carve.routes || 0, w,
                 carve.temp === undefined ? 0.8 : carve.temp, rng);
    for (let i = 0; i < m.settlements.length; i++)
      for (const s of m.settlements[i]) carveRoute(m, s, m.centers[i], 1, 'plains', 0.5, rng);
    if (carve.mazes)
      carveMaze(m, rng.randint(carve.mazes[0], carve.mazes[1]), rng,
                carve.maze_temp === undefined ? 1.7 : carve.maze_temp,
                carve.junction_p === undefined ? 0.5 : carve.junction_p);
  }

  if (carve.rivers && substrate !== 'water') {
    carveRiver(m, rng.randint(carve.rivers[0], carve.rivers[1]), rng,
               carve.river_temp === undefined ? 1.9 : carve.river_temp);
    thinWater(m, m.rim);
  }

  const accentOver = substrate === 'water' ? 'plains' : substrate;
  const free = (h) => h && h.terrain === accentOver && !m.reserved.has(key(h.col, h.row));

  const shares = Object.entries(p.shares || {}).sort((a, b) => b[1] - a[1]);
  for (const [terrain, share] of shares) {
    if (palette.indexOf(terrain) < 0 || terrain === substrate) continue;
    const target = Math.round(share * tot);
    const morph = (p.morphology || {})[terrain] || 'blob';
    if (morph === 'band') {
      const b = (p.band || {})[terrain] || ['e', 0.10, 0.35];
      stampBand(m, terrain, target, b[0], b[1], b[2], free, rng,
                b.length > 3 ? b[3] : 1.0);
    } else if (morph === 'channels') {
      const b = (p.band || {})[terrain] || ['e', 0, 0.5];
      stampBand(m, terrain, target, b[0], 1 / Math.max(m.width, m.height), b[2],
                free, rng, b.length > 3 ? b[3] : 1.0);
    } else if (morph === 'scatter') {
      const s = (p.scatter || {})[terrain] || [12, 1, 3, 3];
      stampScatter(m, terrain, s[0], s[1], s[2], s[3], free, rng,
                   s[4] || 0, s[5] || 5, s[6] || 0);
    } else if (morph === 'massif') {
      const ms = (p.massif || {})[terrain] || [5, 8, 14, 7, 4, 6];
      stampMassif(m, terrain, ms[0], ms[1], ms[2], ms[3], ms[4], ms[5], free, rng);
    } else if (morph === 'perimeter') {
      const pm = (p.perimeter || {})[terrain] || [4, [8, 16], [1, 2], [1, 6]];
      stampPerimeter(m, terrain, pm[0], pm[1], pm[2], pm[3], free, rng);
    } else if (morph === 'fringe') {
      stampFringe(m, terrain, target, free, rng);
    } else {
      stampBlobs(m, terrain, target, free, buffers, substrate, rng);
    }
  }

  const scattered = Object.keys(p.morphology || {}).filter(t => p.morphology[t] === 'scatter');
  cullSmall(m, substrate, palette, scattered);
  capComponents(m, p.cluster_cap, substrate, palette, scattered);

  for (const st of m.settlements) for (const s of st) {
    const h = m.get(s);
    if (h.terrain === 'water' || h.terrain === 'mountain') h.terrain = 'plains';
  }

  if ((p.sea_crossing || 'base') !== 'shipyard') ensureConnectivity(m, rng);
  else for (const st of m.settlements) {
    const reach = reachable(m, st[0]);
    for (const s of st.slice(1))
      if (!reach.has(key(s[0], s[1]))) carveRoute(m, s, st[0], 1, 'plains', 0.6, rng);
  }
  ensureRegionMaterial(m, p);
  markHills(m, p.hill_sep === undefined ? HILL_SEP : p.hill_sep);
  resources(m, palette, Object.assign({}, RESOURCE_MIN, p.resource_min || {}));
  return m;
}

function generateRegion(preset, over, attempts) {
  attempts = attempts || 12;
  const p = Object.assign({}, PARAMS, preset, over || {});
  let best = null, bestV = null;
  for (let k = 0; k < attempts; k++) {
    const m = build(p, (p.seed + k * 1009) >>> 0);
    const v = validate(m, p);
    if (!v.length) return { map: m, params: p, violations: [] };
    if (bestV === null || v.length < bestV.length) { best = m; bestV = v; }
  }
  return { map: best, params: p, violations: bestV };
}

/* ── export ─────────────────────────────────────────────────────────────── */
const FORMAT_VERSION = 1, GENERATOR_VERSION = '0.1.0';
const T2C = { plains: 'p', forest: 'f', wetland: 'w', tundra: 't', mountain: 'm', water: '~' };

function exportMap(m, p, seed, violations) {
  const terrain = [];
  for (let c = 0; c < m.width; c++) {
    let s = '';
    for (let r = 0; r < m.height; r++) s += T2C[m.get([c, r]).terrain];
    terrain.push(s);
  }
  const res = {}, reg = {};
  for (const h of m.all()) {
    if (h.resource) res[h.col + ',' + h.row] = h.resource;
    if (h.region !== null) reg[h.col + ',' + h.row] = h.region;
  }
  const borders = {};
  for (const k of Object.keys(m.borders || {})) borders[k] = m.borders[k].slice();
  return { format: FORMAT_VERSION, generator: GENERATOR_VERSION,
    preset: p.name || '?', seed: seed, width: m.width, height: m.height,
    players: p.players, substrate: p.substrate, borders: borders,
    terrain: terrain, resources: res, regions: reg,
    settlements: m.settlements.map(r => r.map(s => s.slice())),
    centers: m.centers.map(c => c.slice()),
    settlement_range: m.settlement_range, art: p.art || {},
    violations: violations || [] };
}

const C2T = {}; for (const k of Object.keys(T2C)) C2T[T2C[k]] = k;

function importMap(data) {
  /* Rebuild a board from an exported grid. The GRID is what is restored, not
     the seed — a seed only reproduces a board against the build that made it,
     so re-running the generator would quietly hand back a different map.
     Hills are recomputed rather than stored, so they always agree with the
     terrain they sit on. */
  if (data.format !== FORMAT_VERSION)
    throw new Error('unsupported map format ' + data.format);
  const m = new HexMap(data.width, data.height, 'plains');
  data.terrain.forEach((col, c) => {
    for (let r = 0; r < col.length; r++) {
      const t = C2T[col[r]];
      if (!t) throw new Error('unknown terrain code ' + col[r]);
      m.get([c, r]).terrain = t;
    }
  });
  for (const k of Object.keys(data.resources || {})) {
    const [c, r] = k.split(',').map(Number); m.get([c, r]).resource = data.resources[k];
  }
  for (const k of Object.keys(data.regions || {})) {
    const [c, r] = k.split(',').map(Number); m.get([c, r]).region = data.regions[k];
  }
  m.settlements = (data.settlements || []).map(g => g.map(x => x.slice()));
  m.centers = (data.centers || []).map(x => x.slice());
  m.settlement_range = data.settlement_range;
  m.borders = {};
  for (const k of Object.keys(data.borders || {})) m.borders[k] = data.borders[k].slice();
  markHills(m, data.hill_sep === undefined ? HILL_SEP : data.hill_sep);
  return m;
}

root.RenownGen = { RNG, HexMap, dist, key, generateRegion, exportMap, importMap,
  validate, markHills, PARAMS, RESOURCE_MIN, MATERIAL_TERRAINS };

})(typeof module !== 'undefined' && module.exports ? module.exports : (typeof window !== 'undefined' ? window : globalThis));
