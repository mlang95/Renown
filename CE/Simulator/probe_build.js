// probe_build.js — every few turns of one all-AI game: can each bot Build, and what beats Build in its scoring?
//   node probe_build.js [turns] [every] [seed]
"use strict";
const { newWorld } = require("./engine/load_board");
const vm = require("vm");
const [turns = 30, every = 6, seed = 21] = process.argv.slice(2).map(Number);
const w = newWorld(seed);
w.SIM.setup({ players: 4, map: "Default", mapSeed: seed, age: "random", cultures: ["Trusteki", "Kraghs", "Ithiss", "Lenavorites"], turns, wild: false });
const probe = `D.players.map(p=>{const b=p.board,opts=buildOpts(p).filter(o=>o.v.startsWith("b:")),legal=opts.filter(o=>!o.dis);
  const free=withBoard(b,()=>S.settlements.filter(s=>!settUnbuilt(s)).map(s=>(s.name||s.tier).slice(0,8)+":"+wardUse(s.id).free).join(" "));
  const C=aiCandidates(p),bc=C.filter(c=>c.act==="Build"),pi=aiPassChance(p,"Industry");
  return {cul:b.culture,gold:b.treasury,holdings:b.placed.length,legal:legal.length+"/"+opts.length,noWard:opts.filter(o=>/no free Ward/.test(o.label)).length,
    req:opts.filter(o=>/requires/.test(o.label)).length,free,pass:pi.c+" (net "+pi.net+")",bestBuild:bc[0]?bc[0].score.toFixed(1)+" "+bc[0].sub.slice(2)+" ["+bc[0].prio+"]":"-",
    top:C.slice(0,3).map(c=>c.score.toFixed(1)+" "+c.act+" ["+c.prio+"]").join(", "),envoys:personalEnvoys(p),plan:((PT(p).aiPlan||{}).list||[]).map(x=>x.act).join("+")};})`;
(async () => {
  for (let t = 1; t <= turns; t++) {
    await w.SIM.playTurn();
    if (t % every) continue;
    console.log(`--- after turn ${t} (${vm.runInContext("currentEra()", w)})`);
    for (const r of vm.runInContext(probe, w))
      console.log(`${r.cul.padEnd(12)} gold ${String(r.gold).padStart(6)} holdings ${String(r.holdings).padStart(2)} legal ${r.legal} (no Ward ${r.noWard}, requirement ${r.req}) | free Wards ${r.free} | Industry pass ${r.pass} | Envoys ${r.envoys} plan ${r.plan}\n     best Build ${r.bestBuild} | top ${r.top}`);
  }
})();
