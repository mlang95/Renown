// sim_runner.js — run many all-AI games in parallel (worker threads) and write every game's record to games.jsonl.
// Grid: player counts × maps, GAMES games per cell; cultures dealt from a shuffled deck so every culture sees play evenly.
//   node sim_runner.js --players 3,4,5 --maps Default,"Bleak Highlands" --games 20 --turns 30 --workers 7 --tag test
// Options (all optional): --players --maps (names, or "all") --games --turns --workers --seed --age (name | random)
//   --cultures (random | list, cycled) --tag --out --board (built settlement_board.html) --stop-max-renown (0/1) --limit (debug: stop after N games)
"use strict";
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");
const fs = require("fs"), path = require("path"), os = require("os");

if (!isMainThread) {
  // ---- worker: compile the board once, then a fresh world per game ----
  const { newWorld } = require("./engine/load_board");
  parentPort.on("message", async job => {
    if (job === "exit") process.exit(0);
    let res;
    try { const w = newWorld(job.seed, workerData.board); res = await w.SIM.run(job.cfg); res = JSON.parse(JSON.stringify(res)); }
    catch (e) { res = { error: String(e && e.stack || e).split("\n").slice(0, 4).join(" | "), cfg: job.cfg }; }
    parentPort.postMessage({ id: job.id, res });
  });
  return;
}

function args() {
  const a = process.argv.slice(2), o = {};
  for (let i = 0; i < a.length; i++) if (a[i].startsWith("--")) { const k = a[i].slice(2); const v = a[i + 1] && !a[i + 1].startsWith("--") ? a[++i] : "1"; o[k] = v; }
  return o;
}
function mulberry(seed) { let t = seed >>> 0; return () => { t += 0x6D2B79F5; let r = Math.imul(t ^ t >>> 15, 1 | t); r ^= r + Math.imul(r ^ r >>> 7, 61 | r); return ((r ^ r >>> 14) >>> 0) / 4294967296; }; }
function shuffle(L, rnd) { L = L.slice(); for (let i = L.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [L[i], L[j]] = [L[j], L[i]]; } return L; }

(async () => {
  const A = args(), { newWorld, CE } = require("./engine/load_board");
  const board = A.board || process.env.RENOWN_SIM_BOARD || path.join(CE, "references", "settlement_board.html");
  // read the menus (maps, cultures, ages) from the board itself
  const probe = newWorld(1, board), vm = require("vm");
  const menu = JSON.parse(vm.runInContext("JSON.stringify({maps:Object.keys(MP),cultures:Object.keys(RC.AI_PROFILES||{}),ages:AGE_L.map(a=>a.name),sizes:BOARD_SIZE})", probe));
  const players = String(A.players || "4").split(",").map(Number).filter(n => menu.sizes[n]);
  const maps = !A.maps || A.maps === "all" ? menu.maps : String(A.maps).split(",").map(s => s.trim()).filter(m => menu.maps.includes(m));
  const games = +A.games || 10, turns = +A.turns || 50, seed = +A.seed || 1, workers = Math.max(1, +A.workers || Math.max(1, os.cpus().length - 1));
  const cultures = !A.cultures || A.cultures === "random" ? menu.cultures : String(A.cultures).split(",").map(s => s.trim()).filter(c => menu.cultures.includes(c));
  const tag = A.tag || ("sim_" + new Date().toISOString().slice(0, 16).replace(/[-:T]/g, ""));
  const out = A.out || path.join(CE, "lab_out", "sim", tag);
  fs.mkdirSync(out, { recursive: true });
  if (!players.length || !maps.length || !cultures.length) { console.log("nothing to run: players", players, "maps", maps, "cultures", cultures); process.exit(1); }

  // ---- the job list: every (players, map) cell × games; cultures dealt from a reshuffled deck ----
  const rnd = mulberry(seed), jobs = [];let deck = [];
  const deal = n => { const pick = []; while (pick.length < n) { if (!deck.length) deck = shuffle(cultures, rnd); const c = deck.shift(); if (!pick.includes(c) || cultures.length < n) pick.push(c); } return pick; };
  for (const n of players) for (const m of maps) for (let g = 0; g < games; g++) {
    const id = jobs.length;
    jobs.push({ id, seed: Math.floor(rnd() * 2 ** 31) + 1, cfg: { game: id, players: n, map: m, mapSeed: Math.floor(rnd() * 1e6), age: A.age || "random", cultures: deal(n), turns, stopAtMaxRenown: A["stop-max-renown"] === "1", wild: A.wild !== "0" } });
  }
  if (+A.limit) jobs.length = Math.min(jobs.length, +A.limit);
  fs.writeFileSync(path.join(out, "config.json"), JSON.stringify({ tag, wild: A.wild !== "0", board, boardMtime: fs.statSync(board).mtimeMs, players, maps, games, turns, seed, workers, cultures, age: A.age || "random", jobs: jobs.length, started: new Date().toISOString() }, null, 2));
  console.log(`${jobs.length} games · players ${players.join(",")} · ${maps.length} map(s) · ${turns} turns · ${workers} workers → ${out}`);

  const sink = fs.createWriteStream(path.join(out, "games.jsonl"));
  let next = 0, done = 0, errs = 0; const t0 = Date.now();
  await new Promise(resolve => {
    const pool = [];
    const feed = w => { if (next < jobs.length) w.postMessage(jobs[next++]); else { w.postMessage("exit"); if (pool.every(x => x.idle)) resolve(); } };
    for (let i = 0; i < Math.min(workers, jobs.length); i++) {
      const w = new Worker(__filename, { workerData: { board } }); w.idle = false; pool.push(w);
      w.on("message", ({ id, res }) => {
        if (res.error) { errs++; fs.appendFileSync(path.join(out, "errors.log"), JSON.stringify(res) + "\n"); }
        else sink.write(JSON.stringify(res) + "\n");
        done++;
        if (done % Math.max(1, Math.floor(jobs.length / 20)) === 0 || done === jobs.length) {
          const el = (Date.now() - t0) / 1000, eta = el / done * (jobs.length - done);
          console.log(`  ${done}/${jobs.length} games · ${errs} errors · ${el.toFixed(0)}s elapsed · ~${eta.toFixed(0)}s left`);
        }
        feed(w);
      });
      w.on("exit", () => { w.idle = true; if (pool.every(x => x.idle)) resolve(); });
      w.on("error", e => { errs++; console.log("worker error", e.message); w.idle = true; if (pool.every(x => x.idle)) resolve(); });
      feed(w);
    }
  });
  sink.end();
  console.log(`done: ${done - errs} games, ${errs} errors, ${((Date.now() - t0) / 1000).toFixed(0)}s → ${path.join(out, "games.jsonl")}`);
})();
