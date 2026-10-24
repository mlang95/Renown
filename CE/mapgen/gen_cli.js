#!/usr/bin/env node
/* gen_cli.js - run gen.js from Python (mapgen_regional.generate_region), so the app, the settlement
   board and print all generate with the same code: one seed, one board.
   stdin : {"presets_js": <presets.js source>, "region": <preset name>, "over": {...}, "attempts": n}
           presets_js is built fresh from region_presets.py (build_mapapp.presets_js), never a stale file.
   stdout: {"map": <exportMap>, "params": <merged preset params>, "violations": [...]} */
const fs = require('fs'), vm = require('vm'), path = require('path');
const inp = JSON.parse(fs.readFileSync(0, 'utf8'));
const box = {};
vm.runInNewContext(inp.presets_js, { window: box, globalThis: box });
globalThis.RenownRules = box.RenownRules || {};
const G = require(path.join(__dirname, 'gen.js')).RenownGen;
const preset = (box.RenownPresets || {})[inp.region];
if (!preset) { process.stderr.write('unknown region ' + JSON.stringify(inp.region) + '\n'); process.exit(2); }
const over = inp.over || {};
const res = G.generateRegion(preset, over, inp.attempts || 12);
const seed = over.seed !== undefined ? over.seed : res.params.seed;
process.stdout.write(JSON.stringify({ map: G.exportMap(res.map, res.params, seed, res.violations),
                                      params: res.params, violations: res.violations || [] }));
