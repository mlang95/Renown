// probe_boards.js — end-of-game board quality per player: Wards used / capacity, efficient riders (Holdings that use no Ward),
// Mastery earned, and Holdings that could have ridden a host but sit in their own Ward.
//   node probe_boards.js [turns] [seed] [players]
"use strict";
const { newWorld } = require("./engine/load_board");
const vm = require("vm");
const [turns = 35, seed = 41, n = 4] = process.argv.slice(2).map(Number);
const C = ["Trusteki", "Kraghs", "Ithiss", "Lenavorites", "Belvareth", "Prezish", "Madekites"].slice(0, n);
const w = newWorld(seed);
w.SIM.run({ players: n, map: "Default", mapSeed: seed, age: "random", cultures: C, turns, wild: false }).then(r => {
  const out = vm.runInContext(`D.players.map(p=>withBoard(p.board,()=>{
    const setts=S.settlements.filter(s=>!settUnbuilt(s));let cap=0,used=0;setts.forEach(s=>{const u=wardUse(s.id);cap+=u.cap;used+=u.used;});
    const placed=S.placed.filter(x=>x.sid!=null&&x.sid!=="faction"),riders=placed.filter(isFreeRider);
    const couldRide=placed.filter(x=>!isFreeRider(x)&&effList(x.name).length).length;
    const {earned}=computeEarned(new Set(Object.keys(PC)));
    return {cul:p.board.culture,setts:setts.map(s=>s.tier).join(","),wards:used+"/"+cap,holdings:placed.length,riders:riders.length,
      couldRideButDont:couldRide,mastery:Object.keys(earned).filter(k=>earned[k]).length,edicts:edictTotal(p),gold:p.board.treasury};}))`, w);
  console.log("turns", r.turns, r.endReason);
  for (const x of out) console.log(`${x.cul.padEnd(12)} settlements ${x.setts.padEnd(32)} Wards ${x.wards.padEnd(6)} Holdings ${String(x.holdings).padStart(2)} riding free ${String(x.riders).padStart(2)} | could ride but use a Ward ${x.couldRideButDont} | Mastery earned ${x.mastery} | Edicts ${x.edicts} | gold ${x.gold}`);
});
