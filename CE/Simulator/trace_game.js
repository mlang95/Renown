// trace_game.js — play one all-AI game and print, turn by turn, what each bot considered and chose.
//   node trace_game.js [players] [turns] [seed] [map] [cultures,comma,separated]
// For tuning the AI: the top-scored options, the declared Envoys, Armies, gold, Public Order and Bandit threat per seat.
"use strict";
const { newWorld } = require("./engine/load_board");
const vm = require("vm");
const [n = 4, turns = 15, seed = 21, map = "Default", cul] = process.argv.slice(2);
const cultures = cul ? cul.split(",") : ["Trusteki", "Kraghs", "Ithiss", "Lenavorites", "Belvareth", "Prezish", "Madekites"].slice(0, +n);
const w = newWorld(+seed);
vm.runInContext(`(function(){globalThis.__tr=[];const _d=aiDeclare;aiDeclare=function(p){
  const C=aiCandidates(p).slice(0,6).map(c=>c.score.toFixed(1)+" "+c.act+(c.sub?"("+String(c.sub).slice(2,22)+")":"")+" ["+c.prio+"]");
  const r=_d.apply(this,arguments);const pl=(PT(p).aiPlan||{}).list||[];
  __tr.push({t:tTurn(),p:p.board.culture,gold:p.board.treasury,po:p.board.po,armies:(p.board.armies||[]).map(a=>a.count+(a.muster&&a.muster.n>0?"+m":"")).join(","),
    threat:aiBanditThreat(p).toFixed(2),cash:aiCashOutlook(p).ok?"ok":"neg",top:C,plan:pl.map(x=>x.dom[0]+":"+x.act)});return r;};})()`, w);
w.SIM.setup({ players: +n, map, mapSeed: +seed, age: "random", cultures, turns: +turns, wild: false });
(async () => {
  for (let t = 0; t < +turns; t++) await w.SIM.playTurn();
  const L = vm.runInContext("__tr", w);
  let last = 0;
  for (const r of L) {
    if (r.t !== last) { console.log(`\n=== turn ${r.t}  camps ${vm.runInContext("Object.keys(mapState().camps).length", w)}`); last = r.t; }
    console.log(`${r.p.padEnd(12)} gold ${String(r.gold).padStart(6)} PO ${String(r.po).padStart(3)} cash ${r.cash} threat ${r.threat} armies [${r.armies}]  plan ${r.plan.join(" ")}`);
    console.log(`   top: ${r.top.join(" · ")}`);
  }
})();
