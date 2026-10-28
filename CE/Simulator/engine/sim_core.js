// sim_core.js — appended inside the settlement board's script (same scope: D, tSim, aiTick, roll, … are all in reach).
// Drives one all-AI game: setup (map, Age, culture, faction, Deploy, Starting Holdings, Wild Outlaw Country, check-in),
// then every phase of every turn through the board's own rules and AI, resolving Battles with the board's dice.
// Records a per-turn snapshot of every player plus event streams (gold ledger, Envoys, Battles, treaties, wars, Edicts).
var SIM = (function () {
  const REC = { turns: [], ledger: [], envoys: [], battles: [], events: [], stuck: [], flags: [] };
  const SEEN = {};                                                                          // pid -> placed ids / infra already recorded
  let CUR_T = 0;
  // ---- event taps: wrap the board's own functions so every gold / Faith / Doubt movement is booked ----
  const pidOf = b => { const p = (D.players || []).find(q => q.board === b); return p ? p.id : null; };
  const cat = why => String(why || "").split(/[:·(]/)[0].trim().slice(0, 40) || "other";
  const _tGold = tGold;
  tGold = function (b, v, why) { const r = _tGold.apply(this, arguments); if (v) REC.ledger.push([CUR_T, pidOf(b), cat(why), Math.round(+v || 0)]); return r; };
  const _gainDoubt = gainDoubt;
  gainDoubt = function (b, n) { const r = _gainDoubt.apply(this, arguments); REC.ledger.push([CUR_T, pidOf(b), "~doubt", +r || 0]); return r; };
  const _addFaith = addFaith;
  addFaith = function (b, n) { const r = _addFaith.apply(this, arguments); REC.ledger.push([CUR_T, pidOf(b), "~faith", +r || 0]); return r; };
  const _warOn = warOn;
  warOn = function (c, o, q) { const was = effPair(o.id, q.id).war; const r = _warOn.apply(this, arguments); if (!was && effPair(o.id, q.id).war) REC.events.push({ t: CUR_T, kind: "war", a: o.id, b: q.id }); return r; };
  const _aiApplyTreaty = aiApplyTreaty;
  aiApplyTreaty = function (p, q, type) { REC.events.push({ t: CUR_T, kind: "treaty", a: p.id, b: q.id, type }); return _aiApplyTreaty.apply(this, arguments); };
  render = function () {}; renderTable = function () {}; renderBattle = function () {};   // nothing to draw
  flash = function () {};
  save = function () {};                                                                    // no storage between steps
  const RNG = () => Math.random();

  // ---- setup ----
  function edgeDist(g, k) { const a = hk(k), W = +g.width, H = +g.height; let d = 1e9;
    for (let c = 0; c < W; c++) for (const r of [0, H - 1]) d = Math.min(d, hexDist(a, [c, r]));
    for (let r = 0; r < H; r++) for (const c of [0, W - 1]) d = Math.min(d, hexDist(a, [c, r])); return d; }
  function deploy(p, i, zones) {
    const M = mapState(), g = M.grid, V = decodeGrid(g), z = zones[i] || { hexes: [], towns: [], anchor: [0, 0] };
    const land = k => { const h = V.hex[k]; return !!h && h.t !== "water" && h.t !== "mountain" && !terrBlocked(h.t); };
    const others = zones.filter((_, j) => j !== i && j < D.players.length).map(x => x.anchor);
    const ctr = [Math.floor((+g.width - 1) / 2), Math.floor((+g.height - 1) / 2)];
    const ce = RC.CAPITAL_EDGE_RANGE != null ? +RC.CAPITAL_EDGE_RANGE : 99, hr = +RC.HAMLET_RANGE || 2, ob = +RC.OUTLAW_BUFFER_RANGE || 2, osz = +BAN.outlawStart || 3;
    const towns = new Set((z.towns || []).map(x => x.join(",")));
    // the Town: in the seat's start zone, near the board edge and on / beside Hills, as far from the other seats as possible
    const nearHill = k => V.hex[k] && V.hex[k].hill ? 2 : hexNb(k).some(n => V.hex[n] && V.hex[n].hill) ? 1 : 0;
    const cand = [...new Set((z.hexes || []).map(x => x.join(",")).concat([...towns]))].filter(k => land(k) && hexFree(k) && edgeDist(g, k) <= ce)
      .map(k => ({ k, s: nearHill(k) * 1.5 - edgeDist(g, k) * 0.8 + Math.min(99, ...others.map(a => hexDist(hk(k), a))) * 0.25 + (towns.has(k) ? 1 : 0) + RNG() * 0.1 }))
      .sort((a, b) => b.s - a.s);
    for (const c of cand.slice(0, 12)) {
      M.cells[c.k] = { type: "Town", player: p.id };
      // the Hamlet: exactly HAMLET_RANGE away, toward the middle of the map (deploying "in front")
      const hams = Object.keys(V.hex).filter(k => land(k) && hexFree(k) && hexDist(hk(k), hk(c.k)) === hr)
        .sort((a, b) => hexDist(hk(a), ctr) - hexDist(hk(b), ctr) + (RNG() - 0.5) * 0.2);
      for (const hm of hams.slice(0, 6)) {
        M.cells[hm] = { type: "Hamlet", player: p.id }; syncMapTiers();
        if (outlaw(p, c.k, hm, ob, osz, land, ctr)) { const fl = charterFlags(p).filter(f => /^(Setup|Settle)/.test(f)); if (!fl.length) return { town: c.k, hamlet: hm }; clearOutlaw(p); }
        delete M.cells[hm];
      }
      delete M.cells[c.k];
    }
    // fallback: any legal-looking spot, flags allowed (counted)
    const k = cand[0] && cand[0].k; if (!k) return null; M.cells[k] = { type: "Town", player: p.id };
    const hm = Object.keys(V.hex).find(x => land(x) && hexFree(x) && hexDist(hk(x), hk(k)) === hr); if (hm) M.cells[hm] = { type: "Hamlet", player: p.id };
    syncMapTiers(); outlaw(p, k, hm, ob, osz, land, ctr); return { town: k, hamlet: hm, flags: charterFlags(p) };
  }
  // Outlaw Country: seeded exactly OUTLAW_BUFFER_RANGE off the capital, more than that from the Hamlet, grown inside the Province
  function outlaw(p, cap, ham, ob, size, land, ctr) {
    const M = mapState(), own = terrOwners(), mine = k => own[k] && own[k].has(String(p.id));
    const setts = mapSetts().map(x => x.k), ok = k => land(k) && hexFree(k) && !M.outlaw[k] && mine(k) && (!ham || hexDist(hk(k), hk(ham)) > ob) && setts.every(s => hexDist(hk(k), hk(s)) >= ob);
    const seeds = Object.keys(own).filter(k => ok(k) && hexDist(hk(k), hk(cap)) === ob).sort((a, b) => hexDist(hk(b), ctr) - hexDist(hk(a), ctr));   // behind the capital first
    for (const s of seeds) { const zone = [s]; M.outlaw[s] = true;
      while (zone.length < size) { const nx = [...new Set(zone.flatMap(hexNb))].filter(ok).sort((a, b) => hexDist(hk(a), hk(s)) - hexDist(hk(b), hk(s)))[0]; if (!nx) break; M.outlaw[nx] = true; zone.push(nx); }
      if (zone.length >= size) return true; zone.forEach(k => delete M.outlaw[k]); }
    return false;
  }
  function clearOutlaw(p) { const M = mapState(), own = terrOwners(); Object.keys(M.outlaw).forEach(k => { if (M.outlaw[k] === true && own[k] && own[k].has(String(p.id))) delete M.outlaw[k]; }); }
  function startHoldings(p) {
    withBoard(p.board, () => {
      const cap = capitalSett(), ham = S.settlements.find(s => s.tier === "Hamlet");
      const best = L => L.sort((a, b) => aiHoldValue(b) - aiHoldValue(a) || RNG() - 0.5)[0];          // gold and the Public Order it costs
      for (let i = 0; i < (+RC.SETUP_CAPITAL_PICKS || 0) && cap; i++) { const n = best(Object.keys(R).filter(n => setupRawOK(n, cap.id))); if (n) placeHolding(n, null, cap.id); }
      for (let i = 0; i < (+RC.SETUP_HAMLET_PICKS || 0) && ham; i++) { const n = best((RC.SETUP_HAMLET_HOLDINGS || []).filter(n => canPlace(n, ham.id).ok)); if (n) placeHolding(n, null, ham.id); }
    });
  }
  function setup(cfg) {
    const n = cfg.players | 0, sz = BOARD_SIZE[n] || [26, 21];
    D.players = []; for (let i = 1; i <= n; i++) D.players.push(newPlayer(i));
    HOTSEAT = true;                                                                         // one device acts for every seat
    D.renown = 1; D.started = true; D.tbl = { seats: n, auto: true, boardEnd: true, skip: {}, turn: 1, phase: "empire" };
    D.map = { seed: "", cols: sz[0], rows: sz[1], markers: [], cells: {}, outlaw: {}, camps: {}, wards: {} };
    if (!generateMap(cfg.map, cfg.mapSeed, n, sz[0], sz[1])) throw new Error("map generator failed: " + cfg.map);
    const age = cfg.age === "random" || !cfg.age ? AGE_L[Math.floor(RNG() * AGE_L.length)] : AGE_L.find(a => a.name === cfg.age);
    if (age) { D.age = age.name; D.year0 = rollAgeYear(age); }
    D.players.forEach((p, i) => {
      const b = p.board, cul = cfg.cultures[i];
      b.culture = cul; const pr = (RC.AI_PROFILES || {})[cul] || {};
      if (age && !age.rising) b.ageRising = (pr.domains || [])[0];
      const fs = [...(cultureFactions(b) || Object.keys(FAC))], fn = cfg.factions && cfg.factions[i] || fs[Math.floor(RNG() * fs.length)];
      const pS = S; S = b; try { setFaction(fn); } finally { S = pS; }
      PT(p).seat = i; PT(p).ai = true; PT(p).auto = true;
    });
    applyAgeStart();
    TB().host = String(D.players[0].id); TB().hostSet = true; BST().auto = true;
    const zones = (mapState().grid.start_zones || []).slice().sort((a, b) => a.seat - b.seat);
    const dep = D.players.map((p, i) => deploy(p, i, zones));
    syncMapTiers(); D.players.forEach(startHoldings);
    if (cfg.wild !== false) placeWildOutlaw(); else mapState().wildSeeded = true;          // WILD_OUTLAW=0: no Wild Outlaw Country
    D.players.forEach(p => { checkinFD(p).forEach(r => { if (r.side === "faith") addFaith(r.q.board, r.n); else gainDoubt(r.q.board, r.n); }); PT(p).checkin = { turn: 1, fx: [] }; });
    D.players.forEach(p => (p.board.settlements || []).forEach(s => nameSett(p, s)));
    reindex();
    tSetPhase("empire");
    return dep;
  }

  // ---- Battles: resolve every queued one with the board's dice; AI sides pick Tactics, Bandits roll their table ----
  function sideAlive(X) { const { a } = sideArmy(battle()[X]); return !!a && (+a.count || 0) > 0 && !(a.retinue && isRouted(a)); }
  async function fight(o) {
    if (!bqLoad(o)) return null;
    const B = battle(); B.id = "sim" + REC.battles.length; B.sk = 1; B.round = 0; B.rev = null; B.rolls = {}; B.strk = {}; B.par = {}; B.shDest = {}; B.log = []; B.dice = true; B.aiPk = {};
    Object.keys(LOCAL_PICKS).forEach(k => delete LOCAL_PICKS[k]);
    const start = { A: (sideArmy(B.A).a || {}).count || 0, B: (sideArmy(B.B).a || {}).count || 0 }, cas = { A: 0, B: 0 }, tac = [];
    let end = null;
    for (let sk = 0; sk < 15 && !end; sk++) {
      for (const X of ["A", "B"]) {
        const sd = B[X];
        if (sd.kind === "bandit") { const v = 1 + Math.floor(RNG() * (BAN.faces || 10)); await pickTactic(X, dieLookup(BAN.tacticTable, v)); }
        else { const r = aiPickTactic(X) || { t: (BT.tactics || [])[0] }; await pickTactic(X, r.t); }
      }
      await loadPicks();
      if (!(B.rev && B.rev.sk === B.sk)) { end = "no reveal"; break; }
      tac.push([B.rev.A, B.rev.B]);
      const cell = TMX[B.rev.A + "|" + B.rev.B] || [{}, {}];
      if (!cell[0].no_combat && !cell[1].no_combat) {
        for (const [X, O] of [["A", "B"], ["B", "A"]]) {           // casualties apply after both sides fight
          roll(X, "Strike"); const oc = sideCalc(O); if (!oc) continue;
          if (oc.canParry) roll(O, "Parry");
          roll(O, "Save"); if (oc.recThr != null) roll(O, "Recover");
          if (ripN(X)) { if (sideCalc(X).canParry) roll(X, "RipParry"); roll(X, "RipSave"); }
        }
        for (const X of ["A", "B"]) { const n = pendCas(X); if (n) { applyCas(X, n); cas[X] += n; } }
        const pt = BT.panicThreshold || 5;
        for (const X of ["A", "B"]) { const sd = B[X], c = sideCalc(X); if (!c || c.immunePanic) continue; const pn = (sd.cas || 0) + (c.enduring ? 0 : (sd.rcv || 0));
          if (pn > pt && sideAlive(X)) { roll(X, "Morale"); const n = pendCas(X); if (n) { applyCas(X, n); cas[X] += n; } } }
      }
      const fb = cell[0].end || cell[1].end;
      endSkirmish();
      const aA = sideAlive("A"), aB = sideAlive("B");
      if (!aA || !aB) end = !aA && !aB ? "mutual" : aA ? "A" : "B";
      else if (fb) end = "fall back";
    }
    const win = end === "A" || end === "B" ? end : null;
    const side = X => { const sd = B[X]; return sd.kind === "bandit" ? { bandit: sd.camp } : { pid: sd.pid, aid: sd.aid }; };
    const rec = { t: CUR_T, src: o.src || "", A: side("A"), B: side("B"), startA: start.A, startB: start.B, casA: cas.A, casB: cas.B, skirmishes: tac.length, end: end || "limit", win, tactics: tac };
    // a player's Siege Battle: winning it leads to Capture (RULES › Siege Timer); losing breaks the Siege (Bandit Sieges: endBattle)
    const sgT = o.kind === "siege" && o.A && o.A.pid != null ? realmTimers().findIndex(t => t.kind === "siege" && String(t.by) === String(o.A.pid) && String(t.aid) === String(o.A.aid)) : -1;
    endBattle(win);
    if (sgT >= 0) { const T = realmTimers(), t = T[sgT];
      if (t && win === "A") { T.splice(sgT, 1, { type: "Capture Timer", kind: "capture", tp: t.tp, sid: t.sid, by: t.by, aid: t.aid, label: t.label, n: +((TMR["Capture Timer"] || {}).default) || 1 });
        REC.events.push({ t: CUR_T, kind: "capture", a: +o.A.pid, b: +t.tp }); }
      else if (t) T.splice(sgT, 1); }
    if (o.kind === "siege" && o.A && o.A.kind === "bandit" && win === "A") REC.events.push({ t: CUR_T, kind: "sack", b: +o.B.pid, by: "bandits", what: "after a Siege Battle" });
    bq().splice(0, bq().length, ...bq().filter(x => x.id !== o.id));
    REC.battles.push(rec); return rec;
  }
  // ---- Sieges whose Timer reached 0 (RULES › Siege Timer): a defender inside → Battle; else the besieger wins at once.
  // Bandits Sack (the board's Bandit Sack); a player besieger Captures. This is the Host's button press, done for the table.
  function siegesDue() {
    const T = realmTimers(); let n = 0;
    for (let i = T.length - 1; i >= 0; i--) {
      const t = T[i]; if (t.kind !== "siege" || +t.n > 0 || t.simDone === tTurn()) continue;
      const q = pById(t.tp), st = q && settById(q, t.sid); if (!q || !st) { T.splice(i, 1); continue; }
      const def = armiesInside(q, st).find(x => (+x.a.count || 0) > 0), g = garrisonOf(q, st.id);
      const B = def ? { pid: String(def.p.id), aid: String(def.a.id) } : g && (+g.count || 0) > 0 ? { pid: String(q.id), aid: "g:" + st.id } : null;
      if (t.bandit) {
        const M = mapState(), ck = Object.keys(M.camps).find(k => M.camps[k].uid === t.bandit);
        if (!ck) { T.splice(i, 1); continue; }
        if (B) { t.simDone = tTurn(); bqAdd({ kind: "siege", A: { kind: "bandit", camp: ck }, B, seize: "", src: "Bandit Siege" }); }
        else { const msg = banditSack(t); endSettlementSieges(t.tp, t.sid); banditReturn(ck);   /* the Army goes home after the Siege */ REC.events.push({ t: CUR_T, kind: "sack", b: q.id, by: "bandits", what: String(msg).slice(0, 120) }); }
        n++;
      } else if (t.by != null) {
        const by = pById(t.by);
        if (B && t.aid != null) { t.simDone = tTurn(); bqAdd({ kind: "siege", A: { pid: String(t.by), aid: String(t.aid) }, B, seize: "", src: "Siege resolution" }); }
        else { T.splice(i, 1, { type: "Capture Timer", kind: "capture", tp: t.tp, sid: t.sid, by: t.by, aid: t.aid, label: t.label, n: +((TMR["Capture Timer"] || {}).default) || 1 });
          REC.events.push({ t: CUR_T, kind: "capture", a: by ? by.id : null, b: q.id }); }
        n++;
      }
    }
    return n;
  }
  async function battles() { siegesDue(); let n = 0; while (bq().length && n < 40) { await fight(bq()[0]); n++; } return n; }

  // ---- phases ----
  async function settle(ph) {
    let last = "";
    for (let i = 0; i < 80; i++) {
      const R = tSim(); if (autoRes()) tApply(R);
      const ch = aiTick();
      if (ph === "battle") { await battles(); }
      const R2 = tSim();
      if (ph !== "council" && ph !== "envoy") { if (!ch) break; continue; }
      if (R2.done) { if (autoRes()) tApply(R2); if (!aiTick()) break; continue; }
      const key = (R2.cur && R2.cur.key) || R2.waiting || "";
      if (!ch && key === last) {                                    // nobody can move it on: skip that slot (counted)
        REC.stuck.push({ t: CUR_T, ph, key, waiting: R2.waiting || "" });
        if (R2.cur) TB().skip[R2.cur.key] = tnow();
        else if (R2.waiting === "declare") (R2.declPending || []).forEach(p => { const c = tCurW(p); c.decl = c.decl || { n: {} }; c.decl.lock = tnow(); });
        else if (R2.waiting === "tie") { const c = (R2.tieCands || T_DOMS)[0]; TB().councilTie = { turn: tTurn(), dom: c, ts: tnow() }; }
        else break;
      }
      last = key;
    }
  }
  // ---- per-turn snapshot of every player ----
  function snap() {
    const era = currentEra(), M = mapState();
    D.players.forEach(p => {
      const b = p.board, m = withBoard(b, () => { const have = new Set(Object.keys(PC)); const { earned, tc } = computeEarned(have); return calcMetrics(have, earned, tc); });
      const sn = seasonNet(b), c = tCur(p), ap = Object.values(c.applied || {}), votes = Object.values(c.votes || {});
      const dv = b.domains || {}, el = b.edictLog || {}, pair = q => effPair(p.id, q.id), others = D.players.filter(q => q !== p);
      const sett = b.settlements || [], tiers = {}; sett.forEach(s => tiers[s.tier] = (tiers[s.tier] || 0) + 1);
      REC.turns.push({
        t: CUR_T, season: curSeason(), era, renown: D.renown, pid: p.id,
        treasury: Math.round(+b.treasury || 0), net: Math.round(sn.net || 0), base: Math.round(sn.base || 0), tax: Math.round(sn.tax || 0), trade: Math.round(sn.trade || 0), seasonal: Math.round(sn.seasonal || 0),
        gold: Math.round(m.gold || 0), infraUp: Math.round(m.infraUp || 0), pursUp: Math.round(m.pursUp || 0), armyUp: Math.round(m.netArmy || 0), extort: Math.round(m.extort || 0),
        craft: m.craft || 0, infl: inflPool(p), po: +b.po || 0, faith: m.faith || 0, doubt: m.doubt || 0,
        ind: +dv.Industry || 0, pro: +dv.Prowess || 0, cun: +dv.Cunning || 0, pie: +dv.Piety || 0,
        edicts: edictTotal(p), edictKinds: Object.fromEntries(Object.keys(el).filter(k => el[k].length).map(k => [k, el[k].length])),
        armies: (b.armies || []).length, retinues: (b.armies || []).reduce((t, a) => t + (+a.count || 0), 0),
        settlements: sett.length, tiers, holdings: (b.placed || []).length, holdingsActive: (b.placed || []).filter(x => pActive(x)).length,
        infra: Object.keys(b.infra || {}).filter(k => b.infra[k]).length, wonders: Object.keys(b.wonders || {}).filter(k => b.wonders[k]).length,
        monuments: (b.placed || []).filter(x => R[x.name] && R[x.name].monument).length,
        envoys: Object.values((c.decl || {}).n || {}).reduce((t, v) => t + (+v || 0), 0),
        acts: ap.map(x => [x.dom || "", x.act || "", x.out || ""]),
        support: votes.filter(v => v.a === "S").reduce((t, v) => t + (+v.x || 0), 0), oppose: votes.filter(v => v.a === "O").reduce((t, v) => t + (+v.x || 0), 0),
        wars: others.filter(q => pair(q).war).length, trade_pacts: others.filter(q => pair(q).trade).length, naps: others.filter(q => pair(q).nap).length,
        allied: !!diplo().member[topSuz(p.id)], vassal: !!isVassal(p.id),
        survival: aiSurvival(p).ok, survivalWhy: aiSurvival(p).why, camps: Object.keys(M.camps || {}).length,
        note: (PT(p).aiNote || {}).txt || "",
      });
      REC.envoys.push(...ap.map(x => [CUR_T, p.id, x.dom || "", x.act || "", x.out || ""]));
      ap.forEach(x => (x.flags || []).forEach(f => REC.flags.push([CUR_T, p.id, x.act || "", String(f).slice(0, 80)])));
      // build order: Holdings, Infrastructure and Wonders new since the last snapshot
      const sn_ = SEEN[p.id] = SEEN[p.id] || { h: new Set(), i: new Set() }, row = REC.turns[REC.turns.length - 1];
      row.built = (b.placed || []).filter(x => !sn_.h.has(x.id)).map(x => { sn_.h.add(x.id); return x.name; });
      row.improved = Object.keys(b.infra || {}).concat(Object.keys(b.wonders || {})).filter(k => (b.infra[k] || b.wonders[k]) && !sn_.i.has(k)).map(k => { sn_.i.add(k); return k; });
    });
  }
  async function playTurn() {
    CUR_T = tTurn();
    let ph = tPhase();
    while (ph !== "rest") { await settle(ph); const nx = tNext(ph); tSetPhase(nx); ph = nx; }
    await settle("rest");
    snap();
    const before = D.players.map(p => edictTotal(p));
    tEndTurn();
    if (tPhase() === "rest") { D.players.forEach(p => { while ((p.board.dp || 0) > 0 && dpSpend(p, null)); }); tEndTurn(); }   // unspendable points
    D.players.forEach((p, i) => { const d = edictTotal(p) - before[i]; if (d > 0) REC.events.push({ t: CUR_T, kind: "edict", a: p.id, n: d }); });
  }
  async function run(cfg) {
    const t0 = Date.now(), dep = setup(cfg);
    const players = D.players.map((p, i) => ({ pid: p.id, seat: i, culture: p.board.culture, faction: p.board.faction || "", archetype: ((RC.AI_PROFILES || {})[p.board.culture] || {}).archetype || "", deploy: dep[i] }));
    // the game runs until Last Alliance Standing (every independent player in one Alliance, or only one left) or the turn limit;
    // Renown stops at its maximum but the game goes on
    const lastAlliance = () => { const live = D.players.filter(p => !isVassal(p.id)); return new Set(live.map(p => diplo().member[topSuz(p.id)] || "solo:" + p.id)).size <= 1; };
    let turns = 0, endReason = "turn limit";
    const limit = Math.min(+cfg.turns || 1e9, +RC.GAME_TURN_LIMIT || 1e9);                  // GAME_TURN_LIMIT: the rules' last turn
    for (; turns < limit; turns++) { await playTurn(); if (lastAlliance()) { endReason = "Last Alliance Standing"; turns++; break; }
      if (cfg.stopAtMaxRenown && D.renown >= (+RC.RENOWN_MAX || 30)) { endReason = "Renown maximum (optional stop)"; turns++; break; } }
    const fin = D.players.map(p => ({ pid: p.id, edicts: edictTotal(p), treasury: Math.round(+p.board.treasury || 0), settlements: (p.board.settlements || []).length, vassal: !!isVassal(p.id) }));
    const best = Math.max(...fin.map(f => f.edicts)), lead = fin.filter(f => f.edicts === best && !f.vassal).sort((a, b) => b.treasury - a.treasury);
    return { cfg, players, turns, endReason, renown: D.renown, era: currentEra(), age: D.age || "", winner: lead.length ? lead[0].pid : null, final: fin, ms: Date.now() - t0, rec: REC };
  }
  return { run, setup, playTurn, REC };
})();
globalThis.SIM = SIM;
