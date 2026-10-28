// load_board.js — read the built settlement board once and hand back its script, ready to run in a sandbox.
// The page is the game engine: rules, AI seats, map generator and data all come from it, so the simulator always
// plays the current build (rebuild the board first: references/gen_settlement_board.py).
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const { makeWindowGlobals } = require("./dom_shim");

const CE = path.resolve(__dirname, "..", "..");
const DEFAULT_BOARD = path.join(CE, "references", "settlement_board.html");

let CACHE = null;
function boardSource(file) {
  file = file || process.env.RENOWN_SIM_BOARD || DEFAULT_BOARD;
  if (CACHE && CACHE.file === file) return CACHE;
  const html = fs.readFileSync(file, "utf8");
  const scripts = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  const app = scripts.find(s => s.includes("const DATA = "));
  if (!app) throw new Error("no board script in " + file);
  const lib = scripts.filter(s => s !== app).join("\n;\n");          // map generator etc.
  const core = fs.readFileSync(path.join(__dirname, "sim_core.js"), "utf8");
  // the driver is appended inside the app's own script so it shares its scope (const / let included)
  const src = lib + "\n;\n" + app + "\n;\n" + core;
  CACHE = { file, src, script: new vm.Script(src, { filename: "settlement_board+sim_core.js" }), mtime: fs.statSync(file).mtimeMs };
  return CACHE;
}
// a fresh, isolated game world: its own globals, its own RNG (seeded), the board initialised offline
function newWorld(seed, file) {
  const { script } = boardSource(file);
  let s = (seed >>> 0) || 1;
  const rng = () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };   // xorshift32
  const g = makeWindowGlobals(rng);
  g.window = g; g.self = g; g.globalThis = g;
  const ctx = vm.createContext(g);
  script.runInContext(ctx);
  return ctx;
}
module.exports = { boardSource, newWorld, CE };
