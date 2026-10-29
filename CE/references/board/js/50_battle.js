// ---- Battle ----
const BT=DATA.battle||{tactics:[],matrix:[]};
const TMX={};(BT.matrix||[]).forEach(([a,b,ma,mb])=>{TMX[a+"|"+b]=[ma,mb];});
function newSide(){return {pid:null,aid:null,front:null,adj:{I:0,TH:0,TS:0,M:0,P:0,R:0},cas:0};}
function battle(){D.battle=D.battle||{id:null,sk:1,round:0,dice:true,seize:"",A:newSide(),B:newSide(),rev:null,rolls:{},log:[],start:{}};return D.battle;}
// ---- Battle queue: "battle objects" made from the map (attacker = side A, defender = side B); the Battle view loads one ----
function bq(){D.bqueue=D.bqueue||[];return D.bqueue;}
function bqAdd(o){o.id=Date.now().toString(36)+Math.floor(Math.random()*1e4).toString(36);o.turn=tTurn();bq().push(o);return o;}
function bqSideName(sd){if(sd.kind==="bandit")return "Bandits @ "+sd.camp;const q=pById(sd.pid);if(!q)return "?";
  if(String(sd.aid||"").startsWith("g:")){const st=settById(q,String(sd.aid).slice(2));return q.name+" Garrison · "+(st?(st.name||st.tier):"?");}
  const a=(q.board.armies||[]).find(x=>String(x.id)===String(sd.aid));return q.name+" · "+(a?(a.label||("Army "+a.id)):"?");}
function bqLoad(o){const B=battle();if(B.id&&B.qid!==o.id&&!confirm("A Battle is in progress — replace it?"))return false;
  D.battle=null;const N=battle();N.A=Object.assign(newSide(),JSON.parse(JSON.stringify(o.A)));N.B=Object.assign(newSide(),JSON.parse(JSON.stringify(o.B)));N.seize=o.seize||"";N.qid=o.id;return true;}
// where a battle side stands on the map
function sideHex(sd){if(!sd)return null;if(sd.kind==="bandit")return mapState().camps[sd.camp]?sd.camp:null;const q=pById(sd.pid);if(!q)return null;
  if(String(sd.aid||"").startsWith("g:")){const st=settById(q,String(sd.aid).slice(2));return st?settHex(q,st):null;}
  const a=(q.board.armies||[]).find(x=>String(x.id)===String(sd.aid));return a?armyHex(q,a):null;}
// queue a battle from the map and open it in the Battle view when that view is on
function bqStart(o){bqAdd(o);if(mods().battle){if(!battle().id)bqLoad(o);D.view="battle";flash("Battle queued: "+bqSideName(o.A)+" vs "+bqSideName(o.B));}
  else flash("Battle queued — turn on modules ▸ Battle tab to resolve it");save();render();}
const BLO=DATA.banditLoadouts||{};
function banditArmy(camp){camp.army=camp.army||{retinue:"",endurance:0,fatigue:0,weapon:"",ranged:"None",armor:"",shield:"None",strained:false};
  return new Proxy(camp.army,{get:(t,k)=>k==="count"?camp.n:k==="label"?"Bandits":t[k],
    set:(t,k,v)=>{if(k==="count")camp.n=v;else t[k]=v;return true;}});}
const BANDIT_DEFAULT_RETINUE="Levy";   // ruling: bandits default to Levies, changeable per battle
function armBandits(camp){const a=banditArmy(camp),era=currentEra(),lo=BLO[era];
  // Apply the configured era loadout when this camp first gets armed or the game enters a new era.
  // A battle's manual retinue choice then persists for the rest of that era.
  if(a.loadoutEra===era)return;
  const rn=(lo&&lo.retinue&&EQ.retinues[lo.retinue])?lo.retinue:BANDIT_DEFAULT_RETINUE,rt=EQ.retinues[rn];
  if(rt){a.retinue=rn;a.endurance=rt.endurance;}
  if(lo){a.weapon=lo.weapon||"";a.armor=lo.armor||"";a.shield=lo.shield||"None";}
  a.loadoutEra=era;}
function sideArmy(sd){
  if(sd.kind==="bandit"){const camp=mapState().camps[sd.camp];if(!camp)return {};armBandits(camp);return {p:null,a:banditArmy(camp),camp,bandit:true};}
  const p=D.players.find(q=>String(q.id)===String(sd.pid));if(!p)return {};
  if(String(sd.aid||"").startsWith("g:"))return {p,a:garrisonOf(p,String(sd.aid).slice(2)),garrison:true};
  return {p,a:(p.board.armies||[]).find(x=>String(x.id)===String(sd.aid))};}
function blog(msg){const B=battle();B.log.unshift("S"+B.sk+": "+msg);B.log=B.log.slice(0,80);}
function d10(n){const r=[];for(let i=0;i<n;i++)r.push(1+Math.floor(Math.random()*10));return r;}
function seizeForced(){const B=battle(),h=Y=>!!B&&!!B[Y]&&sideUnlocks(sideArmy(B[Y]).p).mods.some(m=>m.tok==="Seize: first");
  const a=h("A"),b=h("B");return a&&!b?"A":b&&!a?"B":null;}   // "Always gains Seize the Initiative, and your opponent doesn't"
// Faction mechanic text -> army tokens (same tokens as Holdings). Conditions in the text are honoured; nothing is named.
function facCombat(b){const f=FAC[(b||{}).faction||""];if(!f)return [];const t=String(f.mechanic||""),out=[],src=(b.faction||"")+" (faction)";
  const add=tok=>out.push({tok,node:src,via:"faction"});
  if(/Armies always have Unwieldy/i.test(t))add("Always Unwieldy");
  if(/can't gain Immune Unwieldy/i.test(t))add("No Immune Unwieldy");
  if(/(?:Armies|they)[^.]*?\bRecover \+1/i.test(t))add("Recover +1");
  {const rm=t.match(/(?:Armies|they)[^.]*?\bRecover (\d+)\b/i);if(rm)add("Recover "+rm[1]);}         // set base ("gain Recover 8")
  if(/(?:Armies|they)[^.]*?\bImmune Panic/i.test(t))add("Immune Panic");
  if(/Retinues have Poison/i.test(t))add("Poison");
  if(/Ranged Weapons (?:have|gain) \+1 to Strike/i.test(t))add("Ranged Strike +1");
  const m=t.match(/While your Public Order is (-?\d+) or higher, your Armies (?:have|gain) ([^.]+)/i);
  if(m&&(b.po||0)>=+m[1]){if(/\+1 Initiative|Initiative \+1/i.test(m[2]))add("Init +1");if(/\bSteady\b/i.test(m[2]))add("Steady");}
  return out;}
function sideUnlocks(p){return p?withBoard(p.board,()=>{const have=new Set(Object.keys(PC));const {earned}=computeEarned(have);
    // "Gain Immune Awkward" (List Yard): board-only token, read from the Holding's text
    const awk=Object.keys(PC).filter(n=>(PC[n]||0)>0&&/Immune Awkward/i.test(String((R[n]||{}).combo||""))).map(n=>({tok:"Immune Awkward",node:n,via:"innate"}));
    return {mods:armyUnlocks(earned).mods.concat(facCombat(p.board),awk),outInnate:(PC["Outrider Intercept Post"]||0)>0,outMastery:!!earned["Outrider Intercept Post"]};})
    :{mods:[],outInnate:false,outMastery:false};}
// combat standing effects (STANDING_EFFECTS) by Domain value; bandits use their camp's Domain value (Prowess = Cunning = banditDomain)
function sideDomains(sd,p){if(sd.kind==="bandit"){const cp=mapState().camps[sd.camp],v=cp?banditDomain(cp.n):0;return {Prowess:v,Cunning:v};}return (p&&p.board.domains)||{};}
function standingFxOf(dv){const out=[],F=BT.standingFx||{},TH={Rising:RIS,Established:EST,Sovereign:SOV};
  Object.keys(F).forEach(k=>{const [d,t]=k.split("|");if((dv[d]||0)>=TH[t])out.push({d,t,text:F[k]});});return out;}
// ---- Equipment (declared with the Tactic; only Equipped gear counts) ----
let EQSEL={};                                   // this device's pending choice per side, before it is submitted
// gear permissions from Holding text: carry Ranged + Melee ("dual-equip", Skirmish Field) · Dual Wield ("Florentine", List Yard)
function hasArmyTok(p,tok){return !!p&&withBoard(p.board,()=>!!armyTokHolder(tok));}
function eqOptions(X){const B=battle(),{p,a}=sideArmy(B[X]);if(!a)return {opts:["melee"],bastard:false};fixBastard(a);
  const r=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,real=!!a.weapon&&a.weapon!=="Farm Tools",
        one=!!r&&(r.tags||[]).includes("One-Shot"),sk1=(B.sk||1)===1,bastard=a.weapon==="Bastard Sword";
  let opts;
  if(!r)opts=["melee"];
  else if(one)opts=sk1?["ranged"]:["melee"];            // One-Shot: must be Equipped in the first Skirmish, never after
  else if(!real)opts=["ranged"];                         // ranged-only (Farm Tools sidearm) keeps firing
  else opts=["ranged","melee"];                          // carries both (dual-equip)
  return {opts,bastard,dual:!!r&&real,carry:hasArmyTok(p,"dual-equip"),flor:hasArmyTok(p,"Florentine"),one};}
function eqCode(X){const o=eqOptions(X),s=EQSEL[X]||{},m=o.opts.includes(s.mode)?s.mode:o.opts[0],a=sideArmy(battle()[X]).a||{};
  const b2h=s.b2h!=null?s.b2h:(a.b2h!=null?!!a.b2h:!(a.shield&&a.shield!=="None"));   // default: 2H without a shield
  return m+(o.bastard&&m==="melee"&&b2h?":2H":"");}
function eqNow(X){const B=battle(),rv=B.rev&&B.rev.sk===B.sk?B.rev:null,o=eqOptions(X);
  let code=rv&&rv["eq"+X]?rv["eq"+X]:eqCode(X);const [mode,prof]=code.split(":");
  const m=o.opts.includes(mode)?mode:o.opts[0];return {mode:m,b2h:prof==="2H"&&o.bastard&&m==="melee",revealed:!!(rv&&rv["eq"+X])};}
// Dual Wield applies only to the 1H melee weapon (never the ranged one) and not while a Shield is in use
function dualOn(a,shDest){return !!a.dual&&canDualWield(a.weapon)&&(!a.shield||a.shield==="None"||!!shDest);}
function eqWeapon(a,e,shDest){if(!a)return {ap:0};const r=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,w=EQ.weapons[a.weapon]||{};
  if(e.mode==="ranged"&&r)return r;
  if(dualOn(a,shDest))return Object.assign({},w,{tags:[].concat(w.tags||[],["2H","Dual Wield"])});   // two of the same melee weapon: Dual Wield confers 2H
  if(a.weapon==="Bastard Sword"&&(e.b2h||shDest))return EQ.bastard2h||w;              // 2H profile (also forced once the shield is gone)
  return w;}
// Random Tactic: uniform over the Tactics other than Fall Back (as the sim's Random mode), limited to
// those an equipped weapon allows when its note says "May only use …" (e.g. Arquebus).
// Weapon-imposed Tactic limit (RANGED[*].tactics_allowed, e.g. Arquebus): applies while that weapon is the one
// Equipped this Skirmish — same rule as Combatv4 (tactic_mask_ranged). Returns the allowed list, or null.
function tacAllowed(X){const B=battle(),{a}=sideArmy(B[X]||{});if(!a)return null;
  const w=eqWeapon(a,eqNow(X),!!((B.shDest||{})[X]));
  if(Array.isArray(w.tactics_allowed)&&w.tactics_allowed.length)return w.tactics_allowed.filter(t=>BT.tactics.includes(t));
  const n=String(w.note||"");if(/May only use/i.test(n)){const ok=BT.tactics.filter(t=>n.includes(t));if(ok.length)return ok;}
  return null;}
function tacOK(X,t){const al=tacAllowed(X);return !al||al.includes(t);}
function randomTacticPool(X){let pool=BT.tactics.filter(t=>t!=="Fall Back");const al=tacAllowed(X);
  if(al){const nf=al.filter(t=>t!=="Fall Back");pool=nf.length?nf:al;}
  return pool;}
function sideCalc(X){
  const B=battle(),sd=B[X],o=B[X==="A"?"B":"A"],{p,a}=sideArmy(sd);if(!a)return null;
  const eo=sideArmy(o).a;
  if(!p&&!a.retinue)return null;
  const u=sideUnlocks(p);
  const rt=EQ.retinues[a.retinue]||{},w=EQ.weapons[a.weapon]||{},r=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,
        ar=EQ.armors[a.armor]||{},shRaw=EQ.shields[(a.shield==="None"||!a.shield)?"null":a.shield]||{save_bonus:0,init:0,tags:[]};
  const O=X==="A"?"B":"A",shDest=!!((B.shDest||{})[X]);
  const eqX=eqNow(X),wpn=eqWeapon(a,eqX,shDest),is2H=(wpn.tags||[]).includes("2H"),dualW=(wpn.tags||[]).includes("Dual Wield");
  const shOff=is2H&&!!a.shield&&a.shield!=="None";                          // 2H: "Cannot use a Shield" — not Equipped this Skirmish
  const sh=(shDest||shOff)?{save_bonus:0,init:0,tags:[]}:shRaw;              // a destroyed or unequipped shield gives nothing
  const eqO=eqNow(O),eShD=!!((B.shDest||{})[O]);
  let ewpn={ap:0},ewm={ap:0};if(eo){ewpn=eqWeapon(eo,eqO,eShD);ewm=eqWeapon(eo,{mode:"melee",b2h:eqO.b2h},eShD);}   // Riposte = melee weapon
  const strikePlus=u.mods.filter(m=>m.tok==="Strike +1").length,initPlus=u.mods.filter(m=>m.tok==="Init +1").length;
  const rev=B.rev&&B.rev.sk===B.sk?B.rev:null,cell=rev?TMX[rev.A+"|"+rev.B]:null,tm=cell?(X==="A"?cell[0]:cell[1]):{I:0,TH:0,TS:0};
  const forced=seizeForced(),seize=B.sk===1&&(forced?forced===X:B.seize===X)?1:0;
  // Unwieldy: Initiative can't be improved by Tactics (clamp a positive Tactic I to 0) unless Immune Unwieldy.
  // tmEff = the Tactic modifiers that actually apply (display); tmBlk = what was blocked and why.
  // Steady: a negative Tactic I is clamped to 0. Same rule as Combatv4/batch_engine.py.
  const eqInfo=eqOptions(X),dualCarry=eqInfo.dual;                            // carrying both (no longer gives Unwieldy)
  const hasM=tok=>u.mods.some(m=>m.tok===tok);
  const eqTags=[].concat(wpn.tags||[],ar.tags||[],sh.tags||[],rt.tags||[],hasM("Always Unwieldy")?["Unwieldy"]:[],hasM("Steady")?["Steady"]:[]);
  const unw=eqTags.includes("Unwieldy")&&(hasM("No Immune Unwieldy")||!hasM("Immune Unwieldy")),stdy=eqTags.includes("Steady");
  let tmI=tm.I||0,tmNote="";
  if(unw&&tmI>0){tmNote="Unwieldy: ignores the Tactic's +"+tmI+" Initiative";tmI=0;}
  if(stdy&&tmI<0){tmNote="Steady: ignores the Tactic's −"+(-tmI)+" Initiative";tmI=0;}
  const mt=new Set(u.mods.map(m=>m.tok).concat(eqTags));
  // the opponent's Standing effects aimed at this side (STANDING_EFFECTS: "Opponent gains Strain" / "… Blunder in the first Skirmish")
  // this side's own Standing effects (STANDING_EFFECTS: "Immune Blunder", "Immune Panic")
  const sFx=standingFxOf(sideDomains(sd,p)),immBlunder=sFx.some(f=>/Immune Blunder/i.test(f.text)),stImmPanic=sFx.some(f=>/Immune Panic/i.test(f.text));
  const oFx=standingFxOf(sideDomains(o,sideArmy(o).p)),oStrain=oFx.find(f=>/Opponent gains Strain/i.test(f.text)),
        oBlunder=(B.sk||1)===1?oFx.find(f=>/Opponent gains Blunder in the first Skirmish/i.test(f.text)):null;
  const strainI=((effStrained(p,a)||(oStrain&&!immuneStrainIn(p,a)))&&!mt.has("Immune Strain"))?-1:0;   // Strain: −1 Init unless Immune Strain (or inside a controlled Settlement: Granary)
  const maxI=(mt.has("MaxInit3")||[...mt].some(t=>/^Crit /.test(t)))?INIT_MAX+1:INIT_MAX;   // Ministry: ceiling +1
  const rawI=(wpn.init||0)+(sh.init||0)+initPlus+tmI+seize+strainI+sd.adj.I;
  const I=Math.max(INIT_MIN,Math.min(maxI,rawI)),blunder=!immBlunder&&(I<=INIT_MIN||!!oBlunder);
  // where Initiative comes from, part by part (datasheet breakdown); a Tactic modifier its gear ignores is listed as ignored
  const initParts=[[eqX.mode==="ranged"?a.ranged:(a.weapon||"weapon"),wpn.init||0]];
  if(sh.init)initParts.push([a.shield,sh.init]);
  u.mods.filter(m=>m.tok==="Init +1").forEach(m=>initParts.push([m.node||"Init +1",1]));
  if(tm.I)initParts.push(["Tactic",tmNote?tm.I:tmI,tmNote?"ignored ("+tmNote.split(":")[0]+")":""]);
  if(seize)initParts.push(["Seize",seize]);
  if(strainI)initParts.push(["Strained"+(a.strained?"":siegeStrains(p,a)?" (Besieged)":oStrain?" (enemy "+oStrain.t+" "+oStrain.d+")":""),strainI]);
  if(sd.adj.I)initParts.push(["Duke adjust",sd.adj.I]);
  // to-Strike (same order as Combatv4): base − improving, capped at CAP; Blunder clamps to CAP (Fatigue tokens only worsen Morale);
  // then worsening mods (enemy Shielded, own shield −1TH, negative Tactic TH) can push past CAP (auto-fail).
  const CAP=BT.capThr||10,tacTH=tm.TH||0;
  const th1=(mt.has("+1TH")?1:0)+(mt.has("+1TH first")&&B.sk===1?1:0)+(mt.has("+1TH after_first")&&B.sk>1?1:0);
  const rngPlus=eqX.mode==="ranged"?u.mods.filter(m=>m.tok==="Ranged Strike +1").length:0;   // e.g. "Ranged Weapons have +1 to Strike"
  const improve=strikePlus+rngPlus+th1+Math.max(tacTH,0);
  const eShOff=(ewpn.tags||[]).includes("2H");                 // enemy's 2H Equipped: its Shield gives nothing this Skirmish
  const esh=(eo&&!((B.shDest||{})[O])&&!eShOff)?(EQ.shields[(eo.shield==="None"||!eo.shield)?"null":eo.shield]||{tags:[]}):{tags:[]};
  const eShielded=(esh.tags||[]).includes("Shielded")&&!mt.has("Negate Shielded");
  const worsen=(eShielded?1:0)+((sh.tags||[]).includes("-1TH")?1:0)+(mt.has("Immune Tactic TH")?0:Math.max(-tacTH,0));
  let pre=Math.min((rt.to_hit||0)-improve,CAP);if(blunder)pre=Math.max(pre,CAP);
  let toStrike=pre+worsen-sd.adj.TH;
  // Save: Planishing: AP can't push the save past CAP+
  // (normal or Deadly) unless the attacker has Negate Planishing. Deadly strikes save at +DEADLY_AP.
  const FACES_=BT.faces||10,FOC=BT.focusedThr||10,DAP=BT.deadlyAp??5;
  const plan=mt.has("Planishing")||mt.has("GF Armor");
  const eTags=new Set([].concat(ewpn.tags||[]));
  const planOn=plan&&!eTags.has("Negate Planishing")&&!eTags.has("Negate Tempered");
  const saveRaw=(ar.save||0)-(ewpn.ap||0)-(sh.save_bonus||0)-(tm.TS||0)-sd.adj.TS;
  const save=planOn?Math.min(saveRaw,CAP):Math.min(saveRaw,FACES_+1);   // FACES+1 = auto-fail
  const deadlyRaw=Math.min(saveRaw+DAP,FACES_+1),deadlySave=planOn?Math.min(deadlyRaw,CAP):deadlyRaw;
  const saveVs=wp=>{const tg=new Set([].concat(wp.tags||[])),po=plan&&!tg.has("Negate Planishing")&&!tg.has("Negate Tempered"),
    raw=(ar.save||0)-(wp.ap||0)-(sh.save_bonus||0)-(tm.TS||0)-sd.adj.TS;return po?Math.min(raw,CAP):Math.min(raw,FACES_+1);};
  const saveMelee=saveVs(ewm);                                  // vs a Riposte (always the riposting side's melee weapon)
  // own strike profile (Focused procs)
  const critN=[...mt].map(t=>(t.match(/^Crit (\d+)$/)||[])[1]).filter(Boolean).map(Number);
  const critFloor=Math.min(FOC,...critN);
  const wTags=new Set([].concat(wpn.tags||[]));
  const hasDeadly=wTags.has("Deadly"),hasCleave=wTags.has("Cleave"),hasDestroy=wTags.has("Destroy Shield");
  const trig=[];
  if(tmNote)trig.push(tmNote);
  if(shDest)trig.push("Shield destroyed: its save, Init and tags are gone");
  if(eShielded)trig.push("Enemy Shielded: +1 to-Strike");
  else if((esh.tags||[]).includes("Shielded")&&mt.has("Negate Shielded"))trig.push("Negate Shielded: enemy Shielded ignored");
  if(mt.has("Immune Tactic TH")&&tacTH<0)trig.push("Immune Tactic TH: Tactic "+tacTH+" ignored");
  if(th1)trig.push("+"+th1+" to-Strike (Ministry)");
  if(rngPlus)trig.push("+"+rngPlus+" to-Strike with Ranged (faction)");
  if(hasM("Always Unwieldy"))trig.push("Faction: always Unwieldy"+(hasM("No Immune Unwieldy")?", can't gain Immune Unwieldy":""));
  if(immBlunder&&(I<=INIT_MIN||oBlunder))trig.push("Immune Blunder (Standing): no Blunder");
  if(blunder)trig.push("Blunder: to-Strike "+CAP+"+ before penalties"+(oBlunder&&I>INIT_MIN?" (enemy "+oBlunder.t+" "+oBlunder.d+", first Skirmish)":""));
  if(a.strained||siegeStrains(p,a)||oStrain)trig.push(strainI?"Strained −1 Init"+(a.strained?"":siegeStrains(p,a)?" (Besieged)":" (enemy "+oStrain.t+" "+oStrain.d+")"):"Immune Strain: no Init loss");
  {const ms=moraleStanding(a);if(ms)trig.push(ms.src+" Morale +"+ms.n+": Morale value −"+ms.n+" (steadier)");}
  {const mp=moralePO(a);if(mp)trig.push(mp.src+" (Public Order) Morale −"+mp.n+": Morale value +"+mp.n);}
  if(maxI>INIT_MAX)trig.push("Init ceiling +"+maxI);
  if(plan)trig.push(planOn?"Planishing: save capped "+CAP+"+"+(saveRaw>CAP||deadlyRaw>CAP?" (was "+saveRaw+"+ / Deadly "+deadlyRaw+"+)":""):"Planishing negated by enemy weapon");
  if(hasDeadly)trig.push("Deadly: strikes on "+critFloor+"+ save at +"+DAP);
  if(hasCleave)trig.push("Cleave: strikes on "+critFloor+"+ roll an extra die");
  if(hasDestroy)trig.push("Destroy Shield: any "+FOC+"+ strike destroys the enemy shield");
  const morale=(c=>c!=null?Math.min(c,effMorale(a)+sd.adj.M):effMorale(a)+sd.adj.M)(moraleCap(a));
  // ---- Parry / Riposte / Recover (defending against O's Strikes) — same model as Combatv4 build_parry_thr / build_regen_thr ----
  const eSd=o,eU=sideUnlocks(sideArmy(eSd).p),eTok=new Set(eU.mods.map(m=>m.tok)),eW=new Set([].concat(ewpn.tags||[])),eRanged=!!(eo&&eo.ranged&&eo.ranged!=="None");
  const sfx=standingFxOf(sideDomains(sd,p)),gainParry=sfx.find(x=>/Gain Parry/i.test(x.text));
  const florP=mt.has("Florentine")&&dualW;                                                 // Florentine: Parry while Dual Wielding
  const awkward=mt.has("Awkward")&&!mt.has("Immune Awkward"),canParry=(!!gainParry||mt.has("Parry")||florP)&&!awkward;       // Awkward: no Parry, so no Riposte
  const parryPlus=u.mods.filter(m=>m.tok==="Parry +1").length,IPM=BT.improvedParryMod??1,UM=BT.unstoppableMod??2;
  const eUnstop=eW.has("Unstoppable"),adjP=+(sd.adj.P||0),adjR=+(sd.adj.R||0),fatN=a.fatigue||0;
  const eWm=new Set([].concat(ewm.tags||[]));
  const parryThr=Math.min(CAP,(BT.parryBase||8)-parryPlus*IPM+(eUnstop?UM:0)-adjP);                 // Fatigue no longer affects Parry
  const parryThrMelee=Math.min(CAP,(BT.parryBase||8)-parryPlus*IPM+(eWm.has("Unstoppable")?UM:0)-adjP);
  const riposte=mt.has("Riposte")&&!eW.has("Negate Riposte")&&!eRanged,riposteMelee=mt.has("Riposte")&&!eWm.has("Negate Riposte");
  // Poison (attacker keyword): a Focused Save fails, and that wound Recovers only on a Focused roll
  const imPz=mt.has("Immune Poison"),ePzAll=eTok.has("Poison");
  const poisoned=!imPz&&(ePzAll||eW.has("Poison")),poisonedMelee=!imPz&&(ePzAll||eWm.has("Poison"));
  const recs=[...mt].map(t=>(t.match(/^Recover (\d+)$/)||[])[1]).filter(Boolean).map(Number);
  const enduring=mt.has("Enduring"),serrN=eU.mods.filter(m=>m.tok==="Serrated").length+(eW.has("Serrated")?1:0),SM=BT.serratedMod??2;
  let recThr=null,recNote="";
  const recPlus=[...u.mods].filter(m=>m.tok==="Recover +1").length;              // each "improve Recover +1" lowers the base by 1
  if(recs.length){const rv=Math.min(...recs)-recPlus,base=Math.min(CAP,rv+serrN*SM);
    recThr=Math.min(CAP,base-adjR);                                                  // Fatigue no longer affects Recover
    recNote="Recover "+rv+"+"+(recPlus?" (base "+Math.min(...recs)+" −"+recPlus+")":"")+(serrN?" · Serrated +"+serrN*SM:"")+(enduring?" · Enduring: Recovered Strikes don't count for Panic":"");}
  if(canParry)trig.push("Parry "+parryThr+"+"+(parryPlus?" (Improved −"+parryPlus*IPM+")":"")+(eUnstop?" · enemy Unstoppable +"+UM:"")+(riposte?" · Riposte on "+FOC:""));
  else if(awkward)trig.push("No Parry: "+(eqX.mode==="ranged"?a.ranged:a.weapon)+" is Awkward");
  else trig.push("No Parry (needs "+(Object.keys(BT.standingFx||{}).find(k=>/Gain Parry/i.test(BT.standingFx[k]))||"Parry").replace("|"," ").split(" ").reverse().join(" ")+")");
  if(poisoned||poisonedMelee)trig.push("Enemy Poison: a "+FOC+" Save fails; Recover it only on "+FOC+(poisoned?"":" (melee only)"));
  if(recNote)trig.push(recNote);
  // Form the line: up to FRONT_LINE_MAX in front, up to RESERVE_MAX in reserve, the rest in camp. This Skirmish's casualties
  // leave the field and reserves step up into the gaps, so the front only shrinks once the reserve is spent.
  const FM=BT.frontMax||10,RM=BT.reserveMax??5,skCas=B.id?(sd.cas||0):0,
        field=Math.max(0,Math.min((a.count||0)+skCas,FM+RM)-skCas);
  const front=Math.min(a.count||0,field,sd.front!=null?sd.front:FM);
  const tags=[...new Set([...eqTags,...u.mods.map(m=>m.tok)])];
  // the Equipped weapon itself is in the datasheet's wargear table; only its conditions are listed as rules
  trig.unshift(...[shOff?"Shield not usable (2H)":"",dualCarry&&!eqInfo.carry&&p?"Carrying both needs "+armyTokNamed("dual-equip"):"",
    dualW&&!eqInfo.flor&&p?"Dual Wield needs Florentine ("+armyTokNamed("Florentine")+")":"",a.dual&&!dualOn(a,shDest)&&eqX.mode!=="ranged"?"Dual Wield off (Shield in use)":""].filter(Boolean));
  return {dualW,immunePanic:mt.has("Immune Panic")||stImmPanic,eqX,shOff,enduring,canParry,parryThr,parryThrMelee,riposte,riposteMelee,saveMelee,poisoned,poisonedMelee,recThr,serrN,p,a,rt,I,rawI,tmNote,initParts,strainI,strainBy:a.strained?"":siegeStrains(p,a)?"Besieged":oStrain&&!immuneStrainIn(p,a)?"enemy "+oStrain.t+" "+oStrain.d:"",tmEff:Object.assign({},tm,{I:tmI,TH:mt.has("Immune Tactic TH")&&tacTH<0?0:tacTH}),tmBlk:[tmNote,mt.has("Immune Tactic TH")&&tacTH<0?"Immune Tactic TH: Tactic "+tacTH+" ignored":""].filter(Boolean),blunder,toStrike,save,saveRaw,deadlySave,planOn,critFloor,hasDeadly,hasCleave,hasDestroy,shDest,trig,morale,front,field,reserve:Math.max(0,field-front),camp:Math.max(0,(a.count||0)-field),skCas,tags,tm,seize,cell:!!cell,outrider:(u.outMastery||(u.outInnate&&B.sk===1)),outMastery:u.outMastery};
}
// hidden picks: server when online, in-page when not
const LOCAL_PICKS={};let PICKS={A:{picked:false},B:{picked:false},revealed:false},PEEK=false,_pickT=null;
function pickKey(){const B=battle();return B.sk*10+(B.round||0)%10;}
function viewerSide(){const B=battle(),me=(D.players[D.active]||{}).id;
  return String(B.A.pid)===String(me)?"A":String(B.B.pid)===String(me)?"B":"-";}
async function loadPicks(){
  const B=battle();if(!B.id)return;
  if(API.online){
    const res=await apiRaw("GET","/api/battle/"+B.id+"/"+pickKey()+"?viewer="+viewerSide()+"&peek="+(PEEK?1:0));
    if(res&&res.status===200&&res.json)PICKS=res.json;
  }else{const L=LOCAL_PICKS[B.id+":"+pickKey()]||{},v=viewerSide(),both=!!(L.A&&L.B),opp=v==="A"?"B":v==="B"?"A":null;
    PICKS={revealed:both};["A","B"].forEach(s=>{PICKS[s]={picked:!!L[s]};if(L[s]&&(both||s===v||(PEEK&&s===opp)))PICKS[s].tactic=L[s];});}
  ["A","B"].forEach(s=>{const v=PICKS[s]&&PICKS[s].tactic;if(v&&v.includes("|")){const [t,e]=v.split("|");PICKS[s].tactic=t;PICKS[s].eq=e;}});
  if(PICKS.revealed&&PICKS.A.tactic&&PICKS.B.tactic&&!(B.rev&&B.rev.sk===B.sk)){
    B.rev={sk:B.sk,A:PICKS.A.tactic,B:PICKS.B.tactic,eqA:PICKS.A.eq||eqCode("A"),eqB:PICKS.B.eq||eqCode("B")};
    blog("Tactics revealed — A: "+B.rev.A+" ("+B.rev.eqA+"), B: "+B.rev.B+" ("+B.rev.eqB+")");save();}
}
async function pickTactic(side,t){
  const B=battle();
  if(!tacOK(side,t)){flash(t+" not allowed with this weapon — "+tacAllowed(side).join(", "));return;}
  const tv=t+"|"+eqCode(side);                                   // Tactic and equipment are submitted together
  if(API.online){const r=await apiRaw("PUT","/api/battle/"+B.id+"/"+pickKey()+"/"+side,{tactic:tv});if(r&&r.status===409)flash("both sides already locked in");}
  else{const k=B.id+":"+pickKey();LOCAL_PICKS[k]=LOCAL_PICKS[k]||{};if(!(LOCAL_PICKS[k].A&&LOCAL_PICKS[k].B))LOCAL_PICKS[k][side]=tv;}
  await loadPicks();render();
}
function mdLite(t){return esc(t||"").replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/\*(.+?)\*/g,"<i>$1</i>").replace(/\n/g,"<br>");}
// long form for the side panel: "-1 Initiative, +1 to Strike" (the matrix table keeps the short codes)
function fmtModLong(m){if(!m)return "—";const L={I:"Initiative",TH:"TH",TS:"TS"},o=[];
  ["I","TH","TS"].forEach(k=>{if(m[k])o.push((m[k]>0?"+":"")+m[k]+" "+L[k]);});
  if(m.no_combat)o.push("no combat");if(m.end)o.push("ends");if(m.strain)o.push("Strained");return o.join(", ")||"no modifier";}
function fmtMod(m){if(!m)return"—";const o=[];["I","TH","TS"].forEach(k=>{if(m[k])o.push(k+" "+(m[k]>0?"+":"")+m[k]);});
  if(m.no_combat)o.push("no combat");if(m.end)o.push("ends");if(m.strain)o.push("Strained");return o.join(" ")||"·";}
function dieRow(dice,target){return dice.map(v=>'<span style="display:inline-block;min-width:18px;text-align:center;border:1px solid var(--line);margin:1px;'+(v>=target?'background:var(--sel);font-weight:700':'opacity:.6')+'">'+v+'</span>').join('');}
function rollHTML(X){const R=(battle().rolls||{})[X];if(!R)return"";
  if(R.dl||R.deadly||R.cas!=null||(R.extra&&R.extra.length)){const F=BT.faces||10;
    return '<div class="note" style="margin-top:4px">'+esc(R.rr?"Dual Wield re-roll":R.kind)+' vs '+(R.target>F?'auto-fail':R.target+'+')+': '+dieRow(R.dice,R.target)+
      (R.extra&&R.extra.length?' · Cleave '+dieRow(R.extra,R.target):'')+' → <b>'+R.succ+'</b>'+(R.kind==="Strike"?' strike(s)'+(R.deadly?' · <b>'+R.deadly+'</b> Deadly':''):R.kind==="Parry"?' parried':' saved')+
      (R.dl?'<br>Deadly (set aside) vs '+(R.dl.target>F?'auto-fail':R.dl.target+'+')+': '+dieRow(R.dl.dice,R.dl.target)+' → <b>'+R.dl.succ+'</b> '+(R.kind==="Parry"?'parried':'saved'):'')+
      (R.cas!=null?'<br>Casualties: <b>'+R.cas+'</b>':'')+'</div>';}
  return '<div class="note" style="margin-top:4px">'+esc(R.rr?"Dual Wield re-roll":R.kind)+' vs '+(R.target>(BT.faces||10)?'auto-fail':R.target+'+')+': '+R.dice.slice().sort((x,y)=>y-x).map(v=>'<span style="display:inline-block;min-width:18px;text-align:center;border:1px solid var(--line);margin:1px;'+(v>=R.target?'background:var(--sel);font-weight:700':'opacity:.6')+'">'+v+'</span>').join('')+
    ' → <b>'+R.succ+'</b> succeed, <b>'+(R.dice.length-R.succ)+'</b> fail'+(R.nat10?' · nat 10 ×'+R.nat10:'')+'</div>';}
// pixel strip for a Battle side: retinue sprite in the owner's colour, then its gear (same sprites as the map plate)
function battleSprites(sd,pl){if(!SPR)return "";const {a}=sideArmy(sd)||{};if(!a)return "";
  const col=pl?pl.color:"#8b2b2b",rk="army:"+(a.retinue||BANDIT_DEFAULT_RETINUE),g=armyGear(a);
  return '<div class="bspr" style="display:flex;align-items:flex-end;gap:4px;margin:4px 0">'+(SPR.S[rk]?sprSVG(rk,48,false,col):"")+g.map(n=>'<span title="'+esc(n)+'">'+eqSVG(n,28)+'</span>').join("")+
    '<span class="note" style="margin-left:4px">'+esc(a.retinue||"")+' ×'+(a.count||0)+'</span></div>';}
// unit datasheet for a Battle side: header (sprite, retinue ×count), stat line, modifiers, wargear table, rules in play, keywords;
// the Duke can open the manual adjusters (counts, enemy/other effects)
const BADJ={};
function datasheetHTML(X,c,pl){
  const B=battle(),sd=B[X],a=c.a,F=BT.faces||10,sg=v=>(v>0?"+":"")+(v||0),tgt=v=>v>F?"—":v+"+",
        rt=c.rt||{},rk="army:"+(a.retinue||BANDIT_DEFAULT_RETINUE),kwc=t=>'<span class="kw" data-tok="'+esc(t)+'">'+esc(t)+'</span>';
  let h='<div class="ds"><div class="ds-hd">'+(SPR&&SPR.S[rk]?sprSVG(rk,48,false,pl?pl.color:"#8b2b2b"):'')+
    '<div><div class="ds-name">'+esc(a.retinue||"")+' <span class="ds-n">×'+(a.count||0)+'</span></div>'+
    '<div class="ds-sub">Front '+c.front+' · Reserve '+c.reserve+' · Camp '+c.camp+' · base Strike '+(rt.to_hit??"?")+'+ · Morale '+(rt.shaking??"?")+'+</div></div>'+
    (ADMIN?'<button class="bdsadj'+(BADJ[X]?' on':'')+'" data-x="'+X+'" title="Duke: manual adjust">±</button>':'')+'</div>';
  // stat line (after Tactic / enemy / keyword modifiers)
  const st=(k,v,t,sub,bad)=>'<div class="ds-st'+(bad?' bad':'')+'" title="'+esc(t||"")+'"><span class="k">'+k+'</span><b>'+v+'</b>'+(sub?'<i>'+sub+'</i>':'')+'</div>',
        oc=sideCalc(X==="A"?"B":"A");
  h+='<div class="ds-stats">'+
    st("Init",sg(c.I),"clamped "+INIT_MIN+"..+"+INIT_MAX+(c.tmNote?" · "+c.tmNote:""),c.rawI!==c.I?"raw "+sg(c.rawI):c.tmNote?c.tmNote.split(":")[0]:"")+
    st("Strike",tgt(c.toStrike),"",c.toStrike>F?"auto-fail":c.blunder?"Blunder":"",c.blunder||c.toStrike>F)+
    st("Save",tgt(c.save),"armor − enemy AP − shield − TS"+(c.planOn?" · Planishing cap":""),c.save>F?"auto-fail":c.planOn&&c.saveRaw>c.save?"capped":"",c.save>F)+
    (oc&&oc.hasDeadly?st("vs Deadly",tgt(c.deadlySave),"Deadly strikes: save +"+(BT.deadlyAp??5)+(c.planOn?", Planishing cap":""),c.deadlySave>F?"auto-fail":"",c.deadlySave>F):"")+
    st("Parry",c.canParry?c.parryThr+"+":"—",c.canParry?"vs enemy Strikes; Deadly: "+(BT.focusedThr||10)+" only; vs Riposte "+c.parryThrMelee+"+":"no Parry")+
    st("Recover",c.recThr!=null?c.recThr+"+":"—","after a failed Save; Deadly: "+(BT.focusedThr||10)+" only")+
    st("Morale",c.morale+"+","",c.morale>=11?"Rout":"",c.morale>=11)+
    st("End.",a.endurance||0,"Endurance")+st("Fatigue",a.fatigue||0)+'</div>';
  {const sg2=v=>(v>0?"+":v<0?"\u2212":"")+Math.abs(v),parts=c.initParts.map(([n,v,why])=>esc(n)+' '+(why?'<s>'+sg2(v)+'</s> '+esc(why):sg2(v))).join(' · ');
   h+='<div class="ds-mods ds-init"><span><b>Init</b> '+parts+' = <b>'+sg(c.I)+'</b>'+(c.rawI!==c.I?' (limit '+INIT_MIN+' to +'+INIT_MAX+')':'')+'</span></div>';}
  h+='<div class="ds-mods"><span>Tactic: '+(c.cell?esc(fmtModLong(c.tmEff)+c.tmBlk.map(t=>' · '+t).join('')):'pending')+'</span>'+
    (c.strainBy?'<label title="from '+esc(c.strainBy)+', not the Army\'s own Strained"><input type="checkbox" checked disabled> Strained ('+esc(c.strainBy)+(c.strainI?'':', Immune')+')</label>'
      :'<label><input type="checkbox" class="bstr" data-x="'+X+'"'+(a.strained?' checked':'')+'> Strained'+(a.strained&&!c.strainI?' (Immune)':'')+'</label>')+'</div>';
  // wargear: base profiles (before modifiers); Equipped weapon first, the carried alternative dimmed
  const rw=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,mw=EQ.weapons[a.weapon]||null,ar=EQ.armors[a.armor]||{},
        sh=(a.shield&&a.shield!=="None")?EQ.shields[a.shield]:null,onR=c.eqX.mode==="ranged"&&!!rw,shown=new Set();
  // one item: name row (AP / Init / Save), then its traits on a line of their own
  const row=(n,nm,it,ap,ini,sv,on,fl,ex)=>{const tg=it.tags||[],cl=[on?'':'off',tg.length?'has-trt':''].filter(Boolean).join(' ');
    return '<tr'+(cl?' class="'+cl+'"':'')+(it.tier?' title="'+esc(it.tier_label||it.tier)+'"':'')+'><td>'+
      (SPR&&SPR.S["eq:"+n]?'<span class="ic">'+eqSVG(n,20)+'</span>':'')+esc(nm)+(fl?'<span class="st">'+fl+'</span>':'')+(ex||'')+'</td><td>'+ap+'</td><td>'+ini+'</td><td>'+sv+'</td></tr>'+
      (tg.length?'<tr class="trt'+(on?'':' off')+'"><td colspan="4">'+tg.map(t=>{shown.add(t);return kwc(t);}).join("")+'</td></tr>':'');};
  const wrow=(n,nm,it,on,fl)=>row(n,nm,it,it.ap||0,sg(it.init),"—",on,fl),two=!!(rw&&mw&&!(onR&&a.weapon==="Farm Tools"));
  let g='';
  if(onR){g+=wrow(a.ranged,a.ranged,rw,true,two?"equipped":"");if(two)g+=wrow(a.weapon,a.weapon,mw,false,"carried");}
  else{if(mw)g+=wrow(a.weapon,a.weapon+(c.eqX.b2h?" (2H)":"")+(c.dualW?" ×2":""),c.eqX.b2h&&EQ.bastard2h?EQ.bastard2h:mw,true,two?"equipped":"");if(rw)g+=wrow(a.ranged,a.ranged,rw,false,"carried");}
  if(sh)g+=row(a.shield,a.shield,sh,"—",sh.init?sg(sh.init):"—","+"+(sh.save_bonus||0),!(c.shOff||c.shDest),c.shOff?"off: 2H":"",
    B.id?'<label class="st"><input type="checkbox" class="bshd" data-x="'+X+'"'+(c.shDest?' checked':'')+'> destroyed</label>':'');
  g+=row(a.armor||"Cloth",a.armor||"Cloth",ar,"—",ar.init?sg(ar.init):"—",ar.save!=null?ar.save+"+":"—",true,"");
  h+='<table class="ds-tbl"><tr><th>Wargear</th><th>AP</th><th>Init</th><th>Save</th></tr>'+g+'</table>';
  if(c.trig.length)h+='<div class="ds-sec">Rules in play</div><ul class="ds-rules">'+c.trig.map(t=>{const i=t.indexOf(": ");
    return '<li>'+(i>0?'<b>'+esc(t.slice(0,i))+'</b> '+esc(t.slice(i+2)):esc(t))+'</li>';}).join('')+'</ul>';
  const kw=c.tags.filter(t=>!shown.has(t));
  if(kw.length)h+='<div class="ds-kw"><span class="k">KEYWORDS</span>'+kw.map(kwc).join('')+'</div>';
  if(ADMIN&&BADJ[X]){
    const num=(f,val,lbl)=>'<span class="dctrl"><span class="note">'+lbl+'</span><button class="badj" data-x="'+X+'" data-f="'+f+'" data-d="-1">−</button><span class="dcv">'+val+'</span><button class="badj" data-x="'+X+'" data-f="'+f+'" data-d="1">+</button></span>';
    h+='<div class="ds-adj"><div class="dctrls">'+num("count",a.count||0,"retinues")+num("front",c.front,"front")+num("endurance",a.endurance||0,"end.")+num("fatigue",a.fatigue||0,"fatigue")+'</div>'+
      '<div class="dctrls"><span class="note">enemy/other effects:</span>'+num("adj.I",sd.adj.I,"I")+num("adj.TH",sd.adj.TH,"TH")+num("adj.TS",sd.adj.TS,"TS")+num("adj.M",sd.adj.M,"Morale")+num("adj.P",sd.adj.P||0,"Parry")+num("adj.R",sd.adj.R||0,"Recover")+'</div></div>';}
  return h+'</div>';
}
// Tactic picker (above the field): choose a Tactic to move your own line into it on this device, then Lock in to submit it
// with the Equipment choice. The other side's choice stays hidden until both are locked in.
let TAC_SEL={};
function tacticPickHTML(X){
  const B=battle(),sd=B[X],c=sideCalc(X),v=viewerSide(),mine=v===X,O=X==="A"?"B":"A";if(!c)return "";const a=c.a;
  let h='<div class="btac-side" data-side="'+X+'">';
  const pk2=PICKS[X]||{},op=PICKS[O]||{};
  h+='<div class="btac-h"><b>'+X+' · Tactic</b> '+(pk2.tactic?'<span class="badge earn">'+esc(pk2.tactic)+'</span>':(pk2.picked?'<span class="badge tier">picked (hidden)</span>':'<span class="note">not picked</span>'))+'</div>';
  const tmode=sd.tmode||"";                                   // "", "manual" or "random"
  if(B.id&&!(B.rev&&B.rev.sk===B.sk)&&!pk2.picked){
    const segB=(v,l)=>'<button class="btmode" data-x="'+X+'" data-m="'+v+'"'+(tmode===v?' style="border-color:var(--ink);font-weight:600"':'')+'>'+l+'</button>';
    h+='<div style="margin-top:4px;display:flex;gap:4px;align-items:center"><span class="note">Tactic entry</span>'+
      segB("",sd.kind==="bandit"?"bandit table":(mine||!API.online?"player":"player (hidden)"))+segB("manual","manual")+segB("random","random")+'</div>';
    if(tmode==="random")h+='<div style="margin-top:4px"><button class="btrand" data-x="'+X+'">roll random Tactic</button> <span class="note">'+esc(randomTacticPool(X).join(", "))+'</span></div>';
  }
  if(B.id&&sd.kind==="bandit"&&!tmode&&!(B.rev&&B.rev.sk===B.sk)){
    h+=op.picked&&!pk2.picked?'<div style="margin-top:4px"><button class="bbroll" data-x="'+X+'">roll bandit tactic (d'+(BAN.faces||10)+')</button></div>'
      :(pk2.picked?'':'<div class="note">Bandits roll their Tactic once the other side has picked.</div>');
  }
  else if(B.id&&(mine||!API.online||tmode==="manual")&&tmode!=="random"&&!(B.rev&&B.rev.sk===B.sk)){
    {const eo_=eqOptions(X),cur=eqNow(X);
      if(eo_.opts.length>1||eo_.bastard)h+='<div style="margin-top:4px;display:flex;gap:6px;align-items:center"><span class="note">Equipment</span>'+
        (eo_.opts.length>1?'<select class="beq" data-x="'+X+'"'+(pk2.picked?' disabled':'')+'>'+eo_.opts.map(m=>'<option value="'+m+'"'+(cur.mode===m?' selected':'')+'>'+(m==="ranged"?esc(a.ranged):esc(a.weapon||"melee"))+'</option>').join('')+'</select>':'')+
        (eo_.bastard?'<select class="beqb" data-x="'+X+'"'+(pk2.picked?' disabled':'')+'><option value="1H"'+(cur.b2h?'':' selected')+'>1H</option><option value="2H"'+(cur.b2h?' selected':'')+'>2H</option></select>':'')+
        '<span class="note">submitted with your Tactic</span></div>';
      else if(eo_.one&&eo_.opts[0]==="ranged")h+='<div class="note" style="margin-top:4px">One-Shot: '+esc(a.ranged)+' is Equipped this Skirmish.</div>';}
    if(sideCalc(O)&&sideCalc(O).outrider&&!pk2.picked)h+='<div class="note" style="color:var(--order)">Opponent has Outrider: pick first — your Tactic is shown to them.</div>';
    h+='<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:4px">'+BT.tactics.map(t=>{const ok=tacOK(X,t),on=pk2.tactic===t||(!pk2.picked&&TAC_SEL[X]===t);return '<button class="btac'+(on?' on':'')+'" data-x="'+X+'" data-t="'+esc(t)+'"'+(ok&&!pk2.picked?'':' disabled'+(ok?'':' title="not allowed with the Equipped weapon"'))+'>'+esc(t)+'</button>';}).join('')+
      (!pk2.picked?'<button class="btlock" data-x="'+X+'"'+(TAC_SEL[X]&&tacOK(X,TAC_SEL[X])?'':' disabled')+'>Lock in'+(TAC_SEL[X]?' '+esc(TAC_SEL[X]):'')+'</button>':'')+'</div>'+
      (tacAllowed(X)?'<div class="note">Equipped weapon allows only: '+tacAllowed(X).map(esc).join(", ")+'</div>':'');
    if(mine&&c.outrider)h+='<div style="margin-top:4px"><button id="bpeek"'+(PEEK?' disabled':'')+'>Outrider: reveal opponent'+(op.picked?'':' (once they pick)')+'</button> <span class="note">'+(c.outMastery?'mastery: every Skirmish':'innate: first Skirmish')+'</span></div>';
  }
  return h+'</div>';}
function sideHTML(X){
  const B=battle(),sd=B[X],c=sideCalc(X),v=viewerSide(),mine=v===X,O=X==="A"?"B":"A";
  let h='<div class="tot bside" data-side="'+X+'"><h3 style="font-size:14px">Side '+X+(X==="A"?" (attacker)":"")+'</h3>'+
    '<div style="display:flex;gap:6px;flex-wrap:wrap;margin:6px 0"><select class="bsel" data-x="'+X+'" data-f="pid"><option value="">player…</option>'+
    D.players.map(p=>'<option value="'+p.id+'"'+(sd.kind!=="bandit"&&String(p.id)===String(sd.pid)?' selected':'')+'>'+esc(p.name)+'</option>').join('')+
    Object.keys(mapState().camps).map(k=>{const cp=mapState().camps[k];return '<option value="bandit:'+k+'"'+(sd.kind==="bandit"&&sd.camp===k?' selected':'')+'>☠ Bandit '+(cp.n>=(BAN.armyThreshold||25)?'Army':'Camp')+' @ '+k+' ('+cp.n+')</option>';}).join('')+'</select>';
  if(sd.kind==="bandit"){const {a}=sideArmy(sd),lo=BLO[currentEra()]||{};
    h+=a?'<select class="bret" data-x="'+X+'"><option value="">retinue…</option>'+Object.keys(EQ.retinues).map(r=>'<option value="'+esc(r)+'"'+(a.retinue===r?' selected':'')+'>'+esc(r)+'</option>').join('')+'</select></div>'+
      '<div class="note">Armed for '+esc(currentEra())+': '+esc(((BAN.equipment||{})[currentEra()])||'—')+' → '+esc([a.weapon,a.armor,a.shield].filter(x=>x&&x!=="None").join(', '))+
      ((lo.unmatched||[]).length?' <span style="color:var(--upkeep)">· not found in equipment data: '+esc(lo.unmatched.join(', '))+'</span>':'')+
      '<br>Retinue follows the era loadout; you can change it for this era.</div>':'<div class="note">camp removed from map</div>';
    if(!c)return h+'</div>';}
  const pl=sd.kind==="bandit"?null:D.players.find(p=>String(p.id)===String(sd.pid));
  if(sd.kind!=="bandit")h+='<select class="bsel" data-x="'+X+'" data-f="aid"><option value="">army…</option>'+(pl?(pl.board.armies||[]).map(a=>'<option value="'+a.id+'"'+(String(a.id)===String(sd.aid)?' selected':'')+'>'+esc(a.label||("Army "+a.id))+' — '+esc(a.retinue||"")+' ×'+(a.count||0)+'</option>').join('')+
      garrisonsOf(pl).map(g=>'<option value="g:'+g.sid+'"'+(String(sd.aid)==="g:"+g.sid?' selected':'')+'>'+esc(g.label)+' — '+esc(g.retinue||"")+' ×'+(g.count||0)+'</option>').join(''):'')+'</select></div>';
  if(!c)return h+battleSprites(sd,pl)+'<div class="note">Pick a player and one of their armies.</div></div>';
  const a=c.a;
  h+=datasheetHTML(X,c,pl);
  return h+'</div>';
}
// roll / casualty buttons for one side, in the command bar above the field once both Tactics are revealed
function actionsHTML(X){
  const B=battle(),sd=B[X],c=sideCalc(X),O=X==="A"?"B":"A";if(!c)return "";const a=c.a,nm=sd.kind==="bandit"?"Bandits":(a.label||((sideArmy(sd).p||{}).name)||X);
  let h='<div class="btac-side" data-side="'+X+'"><div class="btac-h"><b>'+esc(nm)+'</b></div>';
  // dice
  if(B.dice&&B.id){
    const oc=sideCalc(O),ic=incoming(X),inc=ic.n+ic.d;
    h+='<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:8px">'+
      '<button class="broll'+(strikeDue(X)?' go':'')+'" data-x="'+X+'" data-k="Strike">Strike ×'+c.front+'</button>'+
      ((st=>c.dualW&&st&&st.sk===B.sk&&st.miss?'<button class="broll" data-x="'+X+'" data-k="DualWield">Dual Wield re-roll ×'+st.miss+'</button>':'')((B.strk||{})[X]))+
      (c.canParry?'<button class="broll" data-x="'+X+'" data-k="Parry">Parry ×'+inc+'</button>':'')+
      '<button class="broll" data-x="'+X+'" data-k="Save">Save ×'+inc+(ic.d?' ('+ic.d+' Deadly)':'')+'</button>'+
      (ripN(X)?(c.canParry?'<button class="broll" data-x="'+X+'" data-k="RipParry">Parry Riposte ×'+ripN(X)+'</button>':'')+'<button class="broll" data-x="'+X+'" data-k="RipSave">Save vs Riposte ×'+ripN(X)+'</button>':'')+
      ((sv=>{const fx=sv?(sv.d||0)+(sv.pz||0):0;return sv&&sv.sk===B.sk&&(sv.n+fx)&&c.recThr!=null?'<button class="broll" data-x="'+X+'" data-k="Recover"'+(c.recThr==null?' title="no Recover"':'')+'>Recover ×'+(sv.n+fx)+(fx?' ('+fx+' on '+(BT.focusedThr||10)+' only)':'')+'</button>':'';})((B.sv||{})[X]))+
      '<button class="broll" data-x="'+X+'" data-k="Morale">Morale ×'+Math.min(c.front,BT.moraleDiceMax||5)+'</button>'+
      '<input type="number" min="0" value="'+inc+'" class="bn" data-x="'+X+'" style="width:52px" title="dice count override for Parry/Save">'+
      '</div>'+rollHTML(X);
  }
  h+='<div style="display:flex;gap:4px;align-items:center;margin-top:6px"><span class="note">casualties</span><input type="number" min="0" value="'+pendCas(X)+'" class="bcas" data-x="'+X+'" style="width:52px"><button class="bcasgo" data-x="'+X+'">apply</button>'+
    (()=>{const cc=sideCalc(X)||{},rc=cc.enduring?0:(sd.rcv||0),pn=(sd.cas||0)+rc,imP=!!cc.immunePanic;   // Enduring: Recovered Strikes don't count
      return '<span class="note">this Skirmish: '+(sd.cas||0)+(sd.rcv?(cc.enduring?' ('+sd.rcv+' Recovered — Enduring, not counted)':' + '+sd.rcv+' Recovered = '+pn)+' for Panic':'')+(imP?' · Immune Panic':'')+((!imP&&BT.panicThreshold&&pn>BT.panicThreshold)?' — <b style="color:var(--upkeep)">Panic check after both sides Strike</b>':'')+'</span>';})()+'</div>';
  // Endurance reaching 0 at end of Skirmish → Break check + Fatigue token (endSkirmish)
  if(B.id){const cell=B.rev&&B.rev.sk===B.sk?TMX[B.rev.A+"|"+B.rev.B]:null,tm=cell?cell[X==="A"?0:1]:null,e=a.endurance||0,e2=Math.max(0,e-((!tm||tm.endurance_loss!==false)?1:0));
    if(e2===0)h+='<div class="note" style="margin-top:6px;padding:6px;border:1px solid var(--upkeep);border-radius:var(--radius)"><b style="color:var(--upkeep)">Fatigued at end of Skirmish</b> — Endurance '+e+' → 0. '+
      'Break check: '+Math.min(c.front,BT.moraleDiceMax||5)+'d10 vs '+c.morale+'+, failures are casualties ('+(B.dice?'rolled when you press end Skirmish':'roll it after end Skirmish')+'). Then +1 Fatigue token.</div>';}
  return h+'</div>';
}
// the Strike due next this Skirmish: whoever fights first (both on equal Initiative), then the other side once it has struck
function strikeDue(X){const B=battle(),O=X==="A"?"B":"A",c=sideCalc(X),oc=sideCalc(O),st=k=>!!((B.strk||{})[k]&&B.strk[k].sk===B.sk);
  if(!c||!oc||!(B.rev&&B.rev.sk===B.sk)||st(X))return false;return c.I>=oc.I||st(O);}
// your edge in one matchup: Initiative over theirs, and how much lower your TH / TS targets are than theirs; Strained / ends noted
function tacEdge(a,b){const c=TMX[a+"|"+b];if(!c)return null;const [m,o]=c;
  const v=((+m.I||0)-(+o.I||0))+((+o.TH||0)-(+m.TH||0))+((+o.TS||0)-(+m.TS||0))+(o.strain?1:0)-(m.strain?1:0);return {m,o,v};}
let TAC_PICK=null;
// Teaching view of the Tactic matrix: rows = your Tactic, columns = theirs. Each pairing reads "ahead / even / behind" by your edge
// (your Initiative over theirs + how much lower your To-Hit / To-Save targets are, ±1 for Strained), and the chosen row is spelled
// out: "you come out ahead if they play …".
function tacticExplainHTML(){const T=BT.tactics||[],N=BT.tacticNotes||{};if(!T.length)return "";const pick=T.includes(TAC_PICK)?TAC_PICK:T[0];
  const col=v=>v>0?"var(--income)":v<0?"var(--upkeep)":"var(--dim)",word=v=>v>0?"ahead":v<0?"behind":"even",sg=v=>v?(v>0?" +":" \u2212")+Math.abs(v):"";
  let h='<details class="tot" id="tacEx" open><summary><b>Tactics — who comes out ahead</b> <span class="note">row = your Tactic · column = the Tactic they play · ahead = your Initiative and lower To-Hit / To-Save targets beat theirs</span></summary>';
  h+='<div style="overflow-x:auto"><table class="dtable tacx" style="font-size:11px"><thead><tr><th>You play ↓ · they play →</th>'+T.map(t=>'<th>'+esc(t)+'</th>').join("")+'</tr></thead><tbody>'+
    T.map(a=>'<tr'+(a===pick?' class="on"':'')+'><th><a href="#" data-tac="'+esc(a)+'">'+esc(a)+'</a></th>'+T.map(b=>{const e=tacEdge(a,b);if(!e)return '<td></td>';
      const sp=(e.m.end||e.o.end)?" ⏹":e.m.no_combat?" ∅":"";return '<td style="color:'+col(e.v)+';font-weight:700;text-align:center" title="'+esc(a+" vs "+b+" — you: "+fmtModLong(e.m)+" · they: "+fmtModLong(e.o))+'">'+word(e.v)+sg(e.v)+sp+'</td>';}).join("")+'</tr>').join("")+'</tbody></table></div>';
  const E=T.map(b=>({b,e:tacEdge(pick,b)})).filter(x=>x.e),grp=f=>E.filter(x=>f(x.e.v)).map(x=>x.b);
  const ah=grp(v=>v>0),ev=grp(v=>v===0),bh=grp(v=>v<0),lst=L=>L.length?L.map(esc).join(", "):"—";
  h+='<div style="margin-top:8px"><b>Play '+esc(pick)+'</b>'+(N[pick]?' <span class="note">— '+esc(N[pick])+'</span>':'')+'</div>'+
    '<div class="tac-sum"><div><span class="pos">You come out ahead</span> if they play '+lst(ah)+'.</div><div><span class="note">Even</span> if they play '+lst(ev)+'.</div><div><span class="neg">You fall behind</span> if they play '+lst(bh)+'.</div></div>'+
    '<table class="dtable" style="font-size:12px;margin-top:4px"><thead><tr><th>If they play</th><th></th><th>You get</th><th>They get</th></tr></thead><tbody>'+
    E.map(({b,e})=>'<tr><td>'+esc(b)+'</td><td style="color:'+col(e.v)+';font-weight:700">'+word(e.v)+sg(e.v)+'</td><td>'+esc(fmtModLong(e.m))+'</td><td>'+esc(fmtModLong(e.o))+'</td></tr>').join("")+'</tbody></table></details>';
  return h;}
document.addEventListener("click",e=>{const a=e.target.closest("[data-tac]");if(!a)return;e.preventDefault();TAC_PICK=a.dataset.tac;render();});
function battleRulesHTML(){let h=tacticExplainHTML();
  h+='<details class="tot"><summary><b>Rules — Skirmish steps</b></summary><div class="note" style="margin-top:6px">'+mdLite(BT.seize)+'<br><br>'+mdLite(BT.steps)+'<br><br><b>Ending a Battle</b><br>'+mdLite(BT.resolve)+
    ((BT.tacticalGlobal||[]).length?'<br><br>'+BT.tacticalGlobal.map(esc).join('<br>'):'')+'</div></details>';
  return h;}
function renderBattle(){
  const host=document.getElementById("viewBattle"),B=battle();
  const Q=bq();
  let h='<div class="bm-card"><div class="bm-h"><h2>Battle</h2><button data-do="battleclose" data-nav="1" title="back to the Realm">✕</button></div>'+
    (Q.length?'<div class="tot bqlist"><div class="lbl">BATTLES TO RESOLVE · '+Q.length+'</div>'+Q.map(o=>'<div class="bqrow'+(B.qid===o.id?' on':'')+'">'+stIcon(o.kind==="sally"?"besieged":o.kind==="siege"?"sieging":"battle",16)+
      '<span><b>A</b> '+esc(bqSideName(o.A))+' <span class="note">vs</span> <b>B</b> '+esc(bqSideName(o.B))+'</span><span class="note">'+esc(o.src||"")+(o.seize?' · Seize: '+o.seize:'')+' · turn '+o.turn+'</span>'+
      (B.qid===o.id?'<span class="badge earn">loaded</span>':'<button data-bq-load="'+o.id+'">load</button>')+'<button class="rm" data-bq-del="'+o.id+'" title="remove">✕</button></div>').join("")+'</div>':'')+
    '<div class="toolbar"><button id="bStart">'+(B.id?'restart battle':'start battle')+'</button>'+
    '<span class="note">Skirmish <b>'+(B.id?B.sk:'—')+'</b></span>'+
    (seizeForced()?'<span class="note">Seize the Initiative: '+seizeForced()+' (Ministry)</span> ':'')+'<label class="note">Seize the Initiative: <select id="bSeize"><option value="">—</option><option value="A"'+(B.seize==="A"?" selected":"")+'>A</option><option value="B"'+(B.seize==="B"?" selected":"")+'>B</option></select></label>'+
    '<label class="note"><input type="checkbox" id="bDice"'+(B.dice?' checked':'')+'> emulate dice</label>'+
    (B.id?'<button id="bReset">reset picks</button><button id="bEndSk" style="border-color:var(--order)">end Skirmish ▸</button><span class="note">end Battle:</span><button class="bEndB" data-w="A" style="border-color:var(--upkeep)">A won</button><button class="bEndB" data-w="B" style="border-color:var(--upkeep)">B won</button><button class="bEndB" data-w="" style="border-color:var(--upkeep)">no winner</button>':'')+'</div>';
  const v=viewerSide();
  h+='<div class="note" style="margin-bottom:6px">Viewing as <b>'+esc((D.players[D.active]||{}).name||"?")+'</b>'+(v==="-"?' (spectator — switch player in the top bar to pick)':' = side '+v)+(API.online?'':' · no server: picks stay on this device (pass-and-play)')+'</div>';
  if(B.rev&&B.rev.sk===B.sk){const cell=TMX[B.rev.A+"|"+B.rev.B];
    h+='<div class="tot"><b>Revealed:</b> A '+esc(B.rev.A)+' ('+fmtMod(cell&&cell[0])+') · B '+esc(B.rev.B)+' ('+fmtMod(cell&&cell[1])+')</div>';}
  if(B.id&&B.endRep&&B.endRep.sk===B.sk&&B.endRep.rows.length)
    h+='<div class="tot" style="border-color:var(--order)"><b>End of Skirmish '+(B.sk-1)+'</b>'+B.endRep.rows.map(r=>'<div class="note" style="margin-top:4px"><b>'+r.X+'</b> Endurance '+r.e0+' → '+r.e1+
      (r.brk?' · <b style="color:var(--upkeep)">Fatigued</b> · Break check '+r.brk.n+'d10 vs '+r.brk.target+'+: '+(r.brk.dice?dieRow(r.brk.dice,r.brk.target)+' → <b>'+r.brk.lost+'</b> casualties':'<button class="bBrk" data-x="'+r.X+'" style="border-color:var(--upkeep)">roll Break check</button>')+
        ' · Fatigue token '+r.fat+' → Morale '+r.m1+'+':'')+(r.rout?' · <b style="color:var(--upkeep)">ROUTS</b>':'')+(r.wiped?' · <b>wiped out</b>':'')+'</div>').join('')+'</div>';
  const cA=sideCalc("A"),cB=sideCalc("B");
  if(cA&&cB)h+='<div class="note" style="margin-bottom:6px">'+(cA.I===cB.I?'<b>Simultaneous</b> — both sides Strike with their full front line':'Strikes first: <b>'+(cA.I>cB.I?"A":"B")+'</b>')+' (I '+cA.I+' vs '+cB.I+')</div>';
  const vs=viewerSide(),bs=BSIDE||(vs==="A"||vs==="B"?vs:"A");
  h+='<div class="bside-nav"><button data-bs="A"'+(bs==="A"?' class="on"':'')+'>Side A</button><button data-bs="B"'+(bs==="B"?' class="on"':'')+'>Side B</button><button data-bs="AB"'+(bs==="AB"?' class="on"':'')+'>Both</button></div>';
  h+='<div class="bsides bgrid" data-bs="'+bs+'">'+sideHTML("A")+'<div class="bfield-col">'+(B.id?'<div class="btacs">'+(B.rev&&B.rev.sk===B.sk?actionsHTML("A")+actionsHTML("B"):tacticPickHTML("A")+tacticPickHTML("B"))+'</div>':'')+'<div id="bfield"></div></div>'+sideHTML("B")+'</div>';
  h+='<div class="tot"><h3 style="font-size:13px">Log</h3><div class="note">'+(B.log||[]).map(esc).join('<br>')+'</div></div>';
  h+=tacticExplainHTML().replace('id="tacEx" open','id="tacExB"')+siegeHTML()+'<div class="note" style="margin:8px 0">Skirmish rules are in <a href="#" data-goto="reference#refBattle">Reference ▸</a></div></div>';
  host.innerHTML=h;bfMount(host);wireBattle(host);wireDashExtras(host);
}
// Incoming strikes still to resolve against side X (after any Parry), split normal / Deadly
function incoming(X){const B=battle(),O=X==="A"?"B":"A",S_=B.strk&&B.strk[O];if(!S_||S_.sk!==B.sk)return {n:0,d:0};
  const pr=(B.par||{})[X];const pn=pr&&pr.sk===B.sk?pr:{p:0,pd:0};
  return {n:Math.max(0,S_.succ-S_.deadly-pn.p),d:Math.max(0,S_.deadly-pn.pd)};}
function roll(X,kind,nOverride){
  const B=battle(),c=sideCalc(X);if(!c)return;const O=X==="A"?"B":"A",FACES_=BT.faces||10,FOC=BT.focusedThr||10;
  B.strk=B.strk||{};B.par=B.par||{};B.shDest=B.shDest||{};
  const inc=incoming(X);
  if(kind==="Strike"||kind==="DualWield"){
    // Dual Wield: each failed Strike is rerolled once (the reroll can be Focused); successes are never rerolled
    const rr=kind==="DualWield",prev=(B.strk||{})[X];if(rr&&!(prev&&prev.sk===B.sk&&prev.miss)){blog(X+": no failed Strikes to re-roll");save();render();return;}
    const n=rr?prev.miss:c.front,target=c.toStrike,af=target>FACES_,dice=d10(n),extra=[];let succ=0,deadly=0,procs=0;
    dice.forEach(v=>{if(af||v<target)return;succ++;if(v>=FOC)procs++;
      if(v>=c.critFloor){if(c.hasDeadly)deadly++;
        if(c.hasCleave){const e=d10(1)[0];extra.push(e);if(!af&&e>=target){succ++;if(c.hasDeadly&&e>=c.critFloor)deadly++;}}}});
    const miss=rr||af?0:dice.filter(v=>v<target).length;
    if(rr)B.strk[X]={sk:B.sk,succ:prev.succ+succ,deadly:prev.deadly+deadly,procs:prev.procs+procs,miss:0};
    else{B.strk[X]={sk:B.sk,succ,deadly,procs,miss};delete B.par[O];}
    B.rolls[X]={kind:"Strike",rr,target,dice:dice.sort((x,y)=>y-x),succ,nat10:procs,deadly,extra};
    blog(X+(rr?" Dual Wield re-roll ":" Strike ")+n+"d10 vs "+target+"+ ["+dice.join(",")+"]"+(extra.length?" + Cleave ["+extra.join(",")+"]":"")+" → "+succ+" strike(s)"+(deadly?" ("+deadly+" Deadly)":"")+(rr?" · total "+B.strk[X].succ:""));
    const {a:ea}=sideArmy(B[O]);const esh=ea&&ea.shield&&ea.shield!=="None"?EQ.shields[ea.shield]:null;
    if(c.hasDestroy&&procs&&esh&&!(esh.tags||[]).includes("Immune Destroy Shield")&&!B.shDest[O]){B.shDest[O]=true;blog(O+"'s "+ea.shield+" is DESTROYED");}
  }else if(kind==="Parry"){
    const tot=nOverride!=null?nOverride:inc.n+inc.d,d=Math.min(inc.d,tot),nn=tot-d,T=c.parryThr;
    const ok=c.canParry,dn=d10(nn),dd=d10(d),p=ok?dn.filter(v=>v>=T).length:0,pd=ok?dd.filter(v=>v>=FOC).length:0;   // no Parry: every Parry fails
    if(!ok)blog(X+" has no Parry — all Parries fail");
    const rip=ok&&c.riposte?dn.filter(v=>v>=FOC).length+pd:0;
    if(rip){addRip(O,rip);blog(X+" Ripostes ×"+rip+" → "+O+" takes "+rip+" Strike(s) from "+X+"'s melee weapon");}
    B.par[X]={sk:B.sk,p:p+((B.par[X]&&B.par[X].sk===B.sk)?B.par[X].p:0),pd:pd+((B.par[X]&&B.par[X].sk===B.sk)?B.par[X].pd:0)};
    B.rolls[X]={kind,target:ok?T:99,dice:dn.sort((x,y)=>y-x),succ:p,nat10:ok?dn.filter(v=>v>=FOC).length:0,
      dl:d?{target:ok?FOC:99,dice:dd.sort((x,y)=>y-x),succ:pd}:null};
    blog(X+" Parry "+nn+"d10 vs "+(ok?T+"+":"auto-fail")+" ["+dn.join(",")+"] → "+p+" parried"+(d?" · Deadly "+d+"d10 vs "+FOC+"+ ["+dd.join(",")+"] → "+pd+" parried":""));
  }else if(kind==="Save"){
    const tot=nOverride!=null?nOverride:inc.n+inc.d,d=Math.min(inc.d,tot),nn=tot-d;
    const T=c.save,TD=c.deadlySave,dn=d10(nn),dd=d10(d),pz=c.poisoned?FOC:99;
    const s1=T>FACES_?0:dn.filter(v=>v>=T&&v<pz).length,s2=TD>FACES_?0:dd.filter(v=>v>=TD&&v<pz).length,pz1=dn.filter(v=>v>=pz).length;
    B.rolls[X]={kind,target:T,dice:dn.sort((x,y)=>y-x),succ:s1,nat10:0,dl:d?{target:TD,dice:dd.sort((x,y)=>y-x),succ:s2}:null,cas:(nn-s1)+(d-s2)};
    B.sv=B.sv||{};B.sv[X]={sk:B.sk,n:nn-s1-pz1,pz:pz1,d:d-s2};setPendCas(X,(nn-s1)+(d-s2));
    {const lost=dn.filter(v=>v>=pz&&v>=T).length+dd.filter(v=>v>=pz&&v>=TD).length;if(lost)blog(X+": "+lost+" Save(s) of "+FOC+" fail to Poison");}
    blog(X+" Save "+nn+"d10 vs "+T+"+ ["+dn.join(",")+"] → "+s1+" saved"+(d?" · Deadly "+d+"d10 vs "+(TD>FACES_?"auto-fail":TD+"+")+" ["+dd.join(",")+"] → "+s2+" saved":"")+" → "+((nn-s1)+(d-s2))+" casualties");
  }else if(kind==="Recover"){
    const sv=(B.sv||{})[X],fx=sv?(sv.d||0)+(sv.pz||0):0;if(!sv||sv.sk!==B.sk||!(sv.n+fx)){blog(X+": no failed Saves to Recover");save();render();return;}
    if(c.recThr==null){blog(X+" has no Recover");save();render();return;}
    const T=c.recThr,dn=d10(sv.n),dd=d10(fx),r1=T>FACES_?0:dn.filter(v=>v>=T).length,r2=dd.filter(v=>v>=FOC).length,left=(sv.n-r1)+(fx-r2);
    B.rolls[X]={kind,target:T,dice:dn.sort((x,y)=>y-x),succ:r1,nat10:0,dl:fx?{target:FOC,dice:dd.sort((x,y)=>y-x),succ:r2}:null,cas:left};
    B.sv[X]={sk:B.sk,n:0,pz:0,d:0};setPendCas(X,pendCas(X)-((sv.n+fx)-left));
    if(!c.enduring)B[X].rcv=(B[X].rcv||0)+((sv.n+fx)-left);                           // still counts toward the Panic threshold
    blog(X+" Recover "+sv.n+"d10 vs "+T+"+ ["+dn.join(",")+"] → "+r1+" recovered"+(fx?" · Deadly/Poisoned "+fx+"d10 vs "+FOC+"+ ["+dd.join(",")+"] → "+r2+" recovered":"")+" → "+left+" casualties");
  }else if(kind==="RipParry"||kind==="RipSave"){
    const pr=ripN(X);if(!pr){blog(X+": no Riposte Strikes pending");save();render();return;}
    if(kind==="RipParry"){if(!c.canParry){blog(X+" has no Parry — Riposte Strikes can't be Parried");save();render();return;}const T=c.parryThrMelee,dn=d10(pr),p=dn.filter(v=>v>=T).length,back=c.riposteMelee?dn.filter(v=>v>=FOC).length:0;
      B.rip[X].n=pr-p;B.rolls[X]={kind:"Parry",target:T,dice:dn.sort((x,y)=>y-x),succ:p,nat10:back};
      blog(X+" Parries Riposte "+pr+"d10 vs "+T+"+ ["+dn.join(",")+"] → "+p+" parried");if(back){addRip(O,back);blog(X+" Ripostes the Riposte ×"+back+" → "+O+" takes "+back+" Strike(s)");}}
    else{const T=c.saveMelee,dn=d10(pr),pz=c.poisonedMelee?FOC:99,s1=T>FACES_?0:dn.filter(v=>v>=T&&v<pz).length,pz1=dn.filter(v=>v>=pz).length,f=pr-s1;
      B.rolls[X]={kind:"Save",target:T,dice:dn.sort((x,y)=>y-x),succ:s1,nat10:0,cas:f};delete B.rip[X];
      B.sv=B.sv||{};const o0=(B.sv[X]&&B.sv[X].sk===B.sk)?B.sv[X]:{n:0,pz:0,d:0};B.sv[X]={sk:B.sk,n:o0.n+f-pz1,pz:(o0.pz||0)+pz1,d:o0.d};setPendCas(X,pendCas(X)+f);
      blog(X+" Saves vs Riposte (melee) "+pr+"d10 vs "+(T>FACES_?"auto-fail":T+"+")+" ["+dn.join(",")+"] → "+s1+" saved"+(pz1?" ("+pz1+" Poisoned)":"")+" → "+f+" casualties");}
  }else{
    const n=Math.min(c.front,BT.moraleDiceMax||5),target=c.morale,dice=d10(n).sort((x,y)=>y-x),succ=dice.filter(v=>v>=target).length;
    B.rolls[X]={kind,target,dice,succ,nat10:0};setPendCas(X,Math.min(n-succ,c.a.count||0),true);
    blog(X+" Morale "+n+"d10 vs "+target+"+ ["+dice.join(",")+"] → "+succ+" succeed, "+(n-succ)+" casualties");
  }
  save();render();
}
function ripN(X){const B=battle(),r=(B.rip||{})[X];return r&&r.sk===B.sk?r.n:0;}
function addRip(X,n){const B=battle();B.rip=B.rip||{};B.rip[X]={sk:B.sk,n:ripN(X)+n};}
// mor: casualties from a Morale (Panic / Break) check — they don't count toward the Panic threshold
function setPendCas(X,n,mor){const B=battle();B.pendCas=B.pendCas||{};B.pendCas[X]={sk:B.sk,n:Math.max(0,n|0),mor:!!mor};}
function pendCas(X){const B=battle(),p=(B.pendCas||{})[X];return p&&p.sk===B.sk?p.n:0;}
function applyCas(X,n){const B_=battle(),p=(B_.pendCas||{})[X],mor=!!(p&&p.sk===B_.sk&&p.mor);if(B_.pendCas)delete B_.pendCas[X];const {a}=sideArmy(battle()[X]);if(!a||!n)return;n=Math.min(n,a.count||0);a.count-=n;if(!mor)battle()[X].cas=(battle()[X].cas||0)+n;blog(X+" loses "+n+" retinue(s)"+(mor?" (Morale)":"")+" → "+a.count);save();render();}
// Break check (end of Skirmish, Endurance 0): r.brk.n d10 vs r.brk.target+, each failure is a casualty (not counted toward Panic)
function rollBreak(X,r,a){const dice=d10(r.brk.n).sort((x,y)=>y-x),lost=Math.min(dice.filter(v=>v<r.brk.target).length,a.count||0);
  a.count-=lost;r.brk.dice=dice;r.brk.lost=lost;delete r.brk.pending;if((a.count||0)===0)r.wiped=true;
  blog(X+" Break check "+r.brk.n+"d10 vs "+r.brk.target+"+ ["+dice.join(",")+"] → "+lost+" casualties"+(r.wiped?" — wiped out":""));}
function rollBreakBtn(X){const B=battle(),r=B.endRep&&B.endRep.sk===B.sk&&B.endRep.rows.find(x=>x.X===X&&x.brk&&x.brk.pending),{a}=sideArmy(B[X]);
  if(!r||!a)return;rollBreak(X,r,a);save();render();}
function endSkirmish(){
  const B=battle();const cell=B.rev&&B.rev.sk===B.sk?TMX[B.rev.A+"|"+B.rev.B]:null,rep=[];
  ["A","B"].forEach((X,i)=>{const c=sideCalc(X);if(!c)return;const a=c.a,tm=cell?cell[i]:null,r={X,e0:a.endurance||0};
    if(!tm||tm.endurance_loss!==false){a.endurance=Math.max(0,(a.endurance||0)-1);}
    r.e1=a.endurance||0;
    if((a.endurance||0)===0){
      const n=Math.min(c.front,BT.moraleDiceMax||5);r.brk={n,target:c.morale};
      if(B.dice)rollBreak(X,r,a);
      else{r.brk.pending=true;blog(X+" Fatigued — Break check due: "+n+"d10 vs "+c.morale+"+");}
      a.fatigue=(a.fatigue||0)+1;r.fat=a.fatigue;r.m1=effMorale(a);blog(X+" gains Fatigue token ("+a.fatigue+") → morale "+effMorale(a)+"+");}
    if(tm&&tm.strain){a.strained=true;blog(X+" becomes Strained");}
    if(tm&&tm.end)blog(X+" tactic ends the Battle (Fall Back)");
    if(effMorale(a)>=(BT.routThr||11)){r.rout=true;blog(X+" ROUTS (morale "+effMorale(a)+"+)");}
    if((a.count||0)===0){r.wiped=true;blog(X+" wiped out");}
    rep.push(r);B[X].cas=0;B[X].rcv=0;});
  B.sk++;B.round=0;B.rev=null;EQSEL={};B.rolls={};B.strk={};B.par={};PEEK=false;B.endRep={sk:B.sk,rows:rep};
  blog("— Skirmish begins —");save();loadPicks().then(render);
}
function endBattle(win){
  const bHome=["A","B"].map(X=>{const sd=battle()[X];if(!sd||sd.kind!=="bandit")return null;const cp=mapState().camps[sd.camp];return cp&&cp.home?{k:sd.camp,home:cp.home,uid:cp.uid}:null;}).filter(Boolean);
  const B=battle(),side=X=>{const sa=sideArmy(B[X]);return sa.bandit?{camp:sa.camp,name:"Bandits"}:sa.p?{b:sa.p.board,name:sa.p.name}:null;};
  const queued=B.qid&&bq().find(x=>x.id===B.qid),banditSiege=queued&&queued.kind==="siege"&&queued.A&&queued.A.kind==="bandit",
    siegeCamp=banditSiege&&mapState().camps[queued.A.camp],siegeUid=siegeCamp&&siegeCamp.uid;
  ["A","B"].forEach(X=>{const c=sideCalc(X);if(!c)return;c.a.fatigue=0;});
  if(win==="A"||win==="B"){const O=win==="A"?"B":"A",oc=sideCalc(O),W=side(win),L=side(O);
    if(oc&&W&&L){const cost=+oc.rt.cost||0,t=extortGold(L,W,cost,"Spoils of War");   // Spoils of War = the defeated Army's Retinue cost (per Army, as its upkeep)
      blog(W.name+" won — Spoils of War: "+(oc.a.retinue||"")+" cost, extort "+t.toLocaleString()+(t<cost?" (of "+cost.toLocaleString()+")":""));
      if(L.camp&&!(+L.camp.n>0)){const M=mapState(),k=Object.keys(M.camps).find(k=>M.camps[k]===L.camp),g=extortGold(L,W,L.camp.gold||0,"destroyed camp");
        blog(W.name+" extorts the destroyed camp's Treasury: "+g.toLocaleString());
        if(k!=null){delete M.camps[k];blog("Bandit Camp @ "+k+" destroyed and removed from play");}
        const uid=L.camp.uid;if(uid){const timers=realmTimers();for(let i=timers.length-1;i>=0;i--)if(timers[i].bandit&&String(timers[i].bandit)===String(uid))timers.splice(i,1);}
        if(k!=null)D.bqueue=bq().filter(o=>![o.A,o.B].some(s=>s&&s.kind==="bandit"&&String(s.camp)===String(k)));}}
    if(W&&W.b){W.b.lossStreak=0;W.b.lastBattle="won";}if(L&&L.b){L.b.lossStreak=(+L.b.lossStreak||0)+1;L.b.lastBattle="lost";}
    if(W&&W.b&&L&&L.b)chron("battle",{winner:W.name,loser:L.name});
    const wc=sideCalc(win);if(L&&L.b&&W&&wc&&srcHas(L.b,"spoils_always")){
      const t2=extortGold(W,L,+wc.rt.cost||0,"Spoils of War");if(t2)blog(L.name+" also collects Spoils of War: "+t2.toLocaleString());}
    [[win,W],[O,L]].forEach(([X,sd])=>{const c=sideCalc(X);if(!sd||!sd.b||!c)return;const lost=Math.max(0,(B.start[X]||0)-(c.a.count||0));
      srcMatch(sd.b,"faith_battle_loss").forEach(x=>{if(lost>=+x.m[2]){sd.b.po=applyPOFloor(sd.b,Math.max(PO_MIN,Math.min(PO_MAX,(sd.b.po||0)+(+x.m[1]))));blog(sd.name+" · "+x.n+": Faith +"+x.m[1]);}});});}
  else blog("Battle ended with no winner");
  // an Army left with no Retinues is wiped out: it leaves the map and any other queued Battle against it is dropped
  ["A","B"].forEach(X=>{const sd=B[X];if(!sd||sd.kind==="bandit"||String(sd.aid||"").startsWith("g:"))return;const {p,a}=sideArmy(sd);if(!p||!a||(+a.count||0)>0)return;
    const M=mapState();Object.keys(M.cells).forEach(k=>{const c=M.cells[k];if(c.type==="Army"&&String(c.player)===String(p.id)&&String(c.aid)===String(a.id))delete M.cells[k];});
    p.board.armies=(p.board.armies||[]).filter(x=>x!==a);blog(p.name+"'s "+armyName(a)+" is wiped out and leaves the map");
    D.bqueue=bq().filter(o=>o.id===B.qid||![o.A,o.B].some(s=>s&&String(s.pid)===String(p.id)&&String(s.aid)===String(a.id)));});
  if(B.qid){D.bqueue=bq().filter(x=>x.id!==B.qid);delete B.qid;}
  if(banditSiege){const T=realmTimers(),i=T.findIndex(t=>t.kind==="siege"&&t.bandit&&String(t.bandit)===String(siegeUid));
    if(i>=0){const t=T[i];if(win==="A"){blog(banditSack(t));endSettlementSieges(t.tp,t.sid);}else T.splice(i,1);}}
  // a Bandit Army goes home after every Battle (survivors re-join its camp); if it was
  // destroyed, its camp is destroyed with it
  bHome.forEach(h=>{const M=mapState();if(M.camps[h.k])banditReturn(h.k);else{const c=M.camps[h.home];if(c&&c.out===h.uid){delete M.camps[h.home];blog("Bandit Camp @ "+h.home+" destroyed with its Army");}}});
  blog("Battle ended — Fatigue tokens removed");B.id=null;B.rev=null;B.rolls={};save();render();
}
function wireBattle(host){
  host.querySelectorAll("[data-bq-load]").forEach(b=>b.onclick=()=>{const o=bq().find(x=>x.id===b.dataset.bqLoad);if(o&&bqLoad(o)){save();render();}});
  host.querySelectorAll("[data-bq-del]").forEach(b=>b.onclick=()=>{D.bqueue=bq().filter(x=>x.id!==b.dataset.bqDel);if(battle().qid===b.dataset.bqDel)delete battle().qid;save();render();});
  const B=battle();
  host.querySelectorAll(".bsel").forEach(s=>s.onchange=()=>{const sd=B[s.dataset.x];
    if(s.dataset.f==="pid"&&s.value.startsWith("bandit:")){sd.kind="bandit";sd.camp=s.value.slice(7);sd.pid=null;sd.aid=null;
      const cp=mapState().camps[sd.camp];if(cp)armBandits(cp);}
    else{if(s.dataset.f==="pid"){sd.kind=null;sd.camp=null;sd.aid=null;}sd[s.dataset.f]=s.value||null;}
    save();render();});
  host.querySelectorAll(".bret").forEach(s=>s.onchange=()=>{const {a}=sideArmy(B[s.dataset.x]);if(!a)return;
    a.retinue=s.value;const rt=EQ.retinues[s.value];if(rt)a.endurance=rt.endurance;save();render();});
  host.querySelectorAll(".bbroll").forEach(b=>b.onclick=()=>{const v=1+Math.floor(Math.random()*(BAN.faces||10)),t=dieLookup(BAN.tacticTable,v);
    blog(b.dataset.x+" bandits roll d"+(BAN.faces||10)+": "+v+" → "+t);save();pickTactic(b.dataset.x,t);});
  const st=host.querySelector("#bStart");if(st)st.onclick=()=>{
    if(!sideCalc("A")||!sideCalc("B")){flash("pick both armies first");return;}
    if(B.id&&!confirm("Restart the battle?"))return;
    ["A","B"].forEach(X=>{if(B[X].kind==="bandit"){const cp=mapState().camps[B[X].camp];if(cp)armBandits(cp);}});
    ["A","B"].forEach(X=>{const sa=sideArmy(B[X]);if(sa&&sa.a&&!sa.bandit)delete sa.a.pillage;});
    B.id=Date.now().toString(36);B.sk=1;B.round=0;B.rev=null;B.rolls={};B.strk={};B.par={};B.sv={};B.rip={};B.pendCas={};B.shDest={};B.log=[];B.endRep=null;PEEK=false;
    B.start={A:sideCalc("A").a.count||0,B:sideCalc("B").a.count||0};B.A.cas=0;B.B.cas=0;B.A.rcv=0;B.B.rcv=0;blog("Battle begins");save();loadPicks().then(render);};
  const sz=host.querySelector("#bSeize");if(sz)sz.onchange=()=>{B.seize=sz.value;save();render();};
  const dc=host.querySelector("#bDice");if(dc)dc.onchange=()=>{B.dice=dc.checked;save();render();};
  const rs=host.querySelector("#bReset");if(rs)rs.onclick=()=>{B.round=(B.round||0)+1;B.rev=null;PEEK=false;blog("Tactic picks reset");save();loadPicks().then(render);};
  const es=host.querySelector("#bEndSk");if(es)es.onclick=()=>{const B=battle(),pb=B.endRep&&B.endRep.sk===B.sk&&B.endRep.rows.filter(r=>r.brk&&r.brk.pending).map(r=>r.X);
    if(pb&&pb.length){flash("Roll the Break check first: "+pb.join(", "));return;}endSkirmish();};
  host.querySelectorAll(".bBrk").forEach(b=>b.onclick=()=>rollBreakBtn(b.dataset.x));
  host.querySelectorAll(".bEndB").forEach(eb=>eb.onclick=()=>{if(confirm("End the battle"+(eb.dataset.w?" — "+eb.dataset.w+" won (Spoils of War)":" with no winner")+"? Removes Fatigue tokens."))endBattle(eb.dataset.w||null);});
  host.querySelectorAll(".btac").forEach(b=>b.onclick=()=>{TAC_SEL[b.dataset.x]=b.dataset.t;render();});
  host.querySelectorAll(".btlock").forEach(b=>b.onclick=()=>{const X=b.dataset.x,t=TAC_SEL[X];if(!t)return;delete TAC_SEL[X];pickTactic(X,t);});
  host.querySelectorAll(".btmode").forEach(b=>b.onclick=()=>{B[b.dataset.x].tmode=b.dataset.m;save();render();});
  host.querySelectorAll(".btrand").forEach(b=>b.onclick=()=>{const X=b.dataset.x,pool=randomTacticPool(X),t=pool[Math.floor(Math.random()*pool.length)];
    blog(X+" random Tactic → picked (hidden until reveal)");pickTactic(X,t);});
  host.querySelectorAll(".beq").forEach(sl=>sl.onchange=()=>{EQSEL[sl.dataset.x]=Object.assign({},EQSEL[sl.dataset.x],{mode:sl.value});render();});
  host.querySelectorAll(".beqb").forEach(sl=>sl.onchange=()=>{EQSEL[sl.dataset.x]=Object.assign({},EQSEL[sl.dataset.x],{b2h:sl.value==="2H"});render();});
  const pe=host.querySelector("#bpeek");if(pe)pe.onclick=()=>{PEEK=true;loadPicks().then(render);};
  host.querySelectorAll(".badj").forEach(b=>b.onclick=()=>{const X=b.dataset.x,f=b.dataset.f,dl=+b.dataset.d,sd=B[X],{a}=sideArmy(sd);
    if(f.startsWith("adj.")){sd.adj[f.slice(4)]=(+sd.adj[f.slice(4)]||0)+dl;}
    else if(f==="front"){const c=sideCalc(X);sd.front=Math.max(0,c.front+dl);}
    else if(a){a[f]=Math.max(0,(a[f]||0)+dl);if(f==="count"&&a.count>EQ.army_max)a.count=EQ.army_max;if(f==="endurance")capEnd(a);}
    save();render();});
  host.querySelectorAll(".bdsadj").forEach(b=>b.onclick=()=>{BADJ[b.dataset.x]=!BADJ[b.dataset.x];render();});
  host.querySelectorAll(".bshd").forEach(cb=>cb.onchange=()=>{B.shDest=B.shDest||{};B.shDest[cb.dataset.x]=cb.checked;blog(cb.dataset.x+"'s shield "+(cb.checked?"destroyed":"restored")+" (manual)");save();render();});
  host.querySelectorAll(".bstr").forEach(cb=>cb.onchange=()=>{const {a}=sideArmy(B[cb.dataset.x]);if(a){a.strained=cb.checked;save();render();}});
  host.querySelectorAll(".broll").forEach(b=>b.onclick=()=>{const X=b.dataset.x,k=b.dataset.k,inp=host.querySelector('.bn[data-x="'+X+'"]');
    roll(X,k,(k==="Parry"||k==="Save")&&inp?Math.max(0,+inp.value||0):null);});
  host.querySelectorAll(".bcasgo").forEach(b=>b.onclick=()=>{const inp=host.querySelector('.bcas[data-x="'+b.dataset.x+'"]');applyCas(b.dataset.x,Math.max(0,+inp.value||0));});
}
setInterval(()=>{if((D.view==="battle")&&battle().id&&!editing()){const before=JSON.stringify(PICKS);loadPicks().then(()=>{if(JSON.stringify(PICKS)!==before)render();});}},2000);
// ---- Edict scoreboard ----
// RULES: any Edict repeatable; each completion = +1 shared Renown; most Edicts wins.
const EDICT_NAMES=Object.keys(EDICTS);
const NUMWORD={one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10};
function edictTimerLen(e){if(+e.turns>0)return +e.turns;const m=/(\w+)\s+consecutive turns/i.exec(e.requirement||"");if(!m)return 0;
  const w=m[1].toLowerCase();return NUMWORD[w]||(+w)||0;}
function edictChoices(name,pi){const e=EDICTS[name]||{};
  if(e.type==="Standing")return DOMAINS.slice();
  if(/monument/i.test(name))return NAMES.filter(n=>R[n]&&R[n].monument);
  if(/wonder/i.test(name))return Object.keys(WON||{});
  if(e.type==="Conquest")return D.players.filter((q,j)=>j!==pi).map(q=>q.name);
  return null;}
function edictTotal(p){const L=p.board.edictLog||{};return EDICT_NAMES.reduce((a,k)=>a+((L[k]||[]).length),0);}
function edictOwners(name,label){const o=[];D.players.forEach((q,j)=>{if(((q.board.edictLog||{})[name]||[]).includes(label))o.push("P"+(j+1));});return o;}
function bumpRenown(d){D.renown=Math.max(1,Math.min(+RC.RENOWN_MAX||30,(D.renown||1)+d));}
// Edicts the board can see are checked when they trigger and held as pending; the Rest Phase adds them (+1 Renown each) and announces them.
// Sovereign Standing / Monument / Wonder: noted the moment they're held (every save), once per Domain / Monument / Wonder per player.
// Wealth: its timer advances at Income & Upkeep; Living Saints: at the Public Order step — otherwise the timer is removed; at its
// length the Edict is pending and the timer restarts. Vassalize and Last Alliance Standing stay manual.
function edictCond(name,b){
  if(name==="Wealth")return +RC.WEALTH_EDICT_GOLD>0&&(b.treasury||0)>=+RC.WEALTH_EDICT_GOLD;
  if(name==="Living Saints")return (b.po||0)>=PO_MAX;
  return null;}
function edictHeld(name,b){const e=EDICTS[name]||{};
  if(e.type==="Standing")return DOMAINS.filter(d=>((b.domains||{})[d]||0)>=SOV);
  if(/monument/i.test(name))return withBoard(b,()=>NAMES.filter(n=>R[n]&&R[n].monument&&(PC[n]||0)>0));
  if(/wonder/i.test(name))return Object.keys(b.wonders||{}).filter(n=>b.wonders[n]&&!((b.itimer||{})[n]>0)&&!(b.facInfra||[]).includes(n));
  return null;}
function edictPend(b,name,lab){b.edictPending=b.edictPending||[];b.edictPending.push({name,lab,turn:tTurn()});}
function edictIsPending(b,name,lab){return (b.edictPending||[]).some(x=>x.name===name&&x.lab===lab);}
// timed Edict step (called from empEconomy for Wealth, empPO for Living Saints)
function edictTick(b,name){if(!EDICTS[name])return;const tl=edictTimerLen(EDICTS[name]),c=edictCond(name,b);if(!tl||c==null)return;
  b.edictTimers=b.edictTimers||{};if(!c){b.edictTimers[name]=0;return;}
  b.edictTimers[name]=(b.edictTimers[name]||0)+1;if(b.edictTimers[name]>=tl){edictPend(b,name,"");b.edictTimers[name]=0;}}
// held Edicts (every save): a newly held Domain / Monument / Wonder goes pending — once per player, or once per game
// for the first player when EDICT_UNIQUE (build_all_CE.bat toggle)
function edictTaken(b,name,l){return ((b.edictLog||{})[name]||[]).includes(l)||edictIsPending(b,name,l);}
function edictWatch(){const P=D.players||[];P.forEach(p=>{const b=p.board;if(!b)return;
  EDICT_NAMES.forEach(name=>{const held=edictHeld(name,b);if(!held)return;
    held.forEach(l=>{if(RC.EDICT_UNIQUE?P.some(q=>q.board&&edictTaken(q.board,name,l)):edictTaken(b,name,l))return;edictPend(b,name,l);});});});}
// Rest Phase: pending Edicts are added, Renown +1 each, and announced
function checkEdicts(){edictWatch();const news=[];
  D.players.forEach(p=>{const b=p.board;b.edictLog=b.edictLog||{};
    (b.edictPending||[]).forEach(x=>{(b.edictLog[x.name]=b.edictLog[x.name]||[]).push(x.lab);news.push({p:p.name,name:x.name,lab:x.lab});});
    b.edictPending=[];});
  if(news.length)bumpRenown(news.length);
  TB().edictNews={turn:tTurn(),list:news};
  if(news.length)flash("Edict completed: "+news.map(edictNewsText).join(" · "));
  return news;}
function edictNewsText(n){return n.p+" — "+n.name+(n.lab?" ("+n.lab+")":"");}
function edictBoardHTML(){
  const P=D.players,tot=P.map(edictTotal),best=Math.max(0,...tot);
  let h='<div class="tot" style="max-width:1000px"><h3 style="font-size:13px">Edicts — scoreboard</h3>'+
    '<div style="overflow-x:auto"><table class="dtable edb"><thead><tr><th>Edict</th>'+
    P.map((p,i)=>'<th style="min-width:130px">'+pTok(p,15)+' <span class="note">'+(i+1)+'</span> '+esc(p.name)+'</th>').join('')+
    '</tr></thead><tbody>';
  EDICT_NAMES.forEach((name,ek)=>{const e=EDICTS[name],tl=edictTimerLen(e);
    h+='<tr><td title="'+esc(e.requirement||"")+'"><b>'+esc(name)+'</b><div class="note">'+esc(e.type||"")+(tl?' · '+tl+'-turn timer':'')+'</div></td>';
    P.map((p,pi)=>{const L=(p.board.edictLog||{})[name]||[],ch=edictChoices(name,pi);
      let c='<div style="display:flex;align-items:center;gap:6px"><span class="edn">'+L.length+'</span>';
      if(ch){c+='<select class="edsel" data-pi="'+pi+'" data-ek="'+ek+'" style="max-width:120px"><option value="">+ add…</option>'+
        ch.map(o=>{const own=edictOwners(name,o);return '<option value="'+esc(o)+'">'+esc(o)+(own.length?' ('+own.join(',')+')':'')+'</option>';}).join('')+'</select>';}
      else c+='<button class="edb-act" data-act="add" data-pi="'+pi+'" data-ek="'+ek+'">+</button>';
      c+='</div>';
      {const pd=(p.board.edictPending||[]).filter(x=>x.name===name);if(pd.length)c+='<div class="note" style="margin-top:4px" title="added at the Rest Phase">pending: '+pd.map(x=>esc(x.lab||"✓")).join(", ")+'</div>';}
      if(L.length)c+='<div style="display:flex;flex-wrap:wrap;gap:3px;margin-top:4px">'+
        L.map((lab,ix)=>'<span class="badge tier">'+esc(lab||"✓")+' <a href="#" class="edb-act" data-act="del" data-pi="'+pi+'" data-ek="'+ek+'" data-ix="'+ix+'" style="color:var(--upkeep);text-decoration:none">×</a></span>').join('')+'</div>';
      if(tl){const t=(p.board.edictTimers||{})[name]||0,done=t>=tl;
        c+='<div style="display:flex;align-items:center;gap:4px;margin-top:4px;font-size:11px">'+
          '<span class="note" style="color:'+(done?'var(--income)':'var(--dim)')+'">timer '+t+'/'+tl+'</span>'+
          '<button class="edb-act" data-act="tadd" data-pi="'+pi+'" data-ek="'+ek+'">+1</button>'+
          '<button class="edb-act" data-act="treset" data-pi="'+pi+'" data-ek="'+ek+'">reset</button>'+
          (done?'<button class="edb-act" data-act="claim" data-pi="'+pi+'" data-ek="'+ek+'" style="border-color:var(--income);color:var(--income)">claim</button>':'')+'</div>';}
      h+='<td style="vertical-align:top">'+c+'</td>';});
    h+='</tr>';});
  h+='<tr><td><b>Total</b></td>'+tot.map(t=>'<td class="num" style="font-size:16px;'+(t===best&&best>0?'color:var(--income);font-weight:700':'')+'">'+t+(t===best&&best>0?' ★':'')+'</td>').join('')+'</tr>';
  h+='</tbody></table></div></div>';
  return h;
}
function wireEdicts(host){
  const log=(pi,name)=>{const b=D.players[pi].board;b.edictLog=b.edictLog||{};return b.edictLog[name]=b.edictLog[name]||[];};
  host.querySelectorAll("select.edsel").forEach(sel=>{sel.onchange=()=>{if(!sel.value)return;
    log(+sel.dataset.pi,EDICT_NAMES[+sel.dataset.ek]).push(sel.value);bumpRenown(1);save();render();};});
  host.querySelectorAll(".edb-act").forEach(el=>{el.onclick=ev=>{ev.preventDefault();
    const pi=+el.dataset.pi,name=EDICT_NAMES[+el.dataset.ek],b=D.players[pi].board,act=el.dataset.act;
    b.edictTimers=b.edictTimers||{};
    if(act==="add"||act==="claim"){log(pi,name).push("");bumpRenown(1);}
    else if(act==="del"){log(pi,name).splice(+el.dataset.ix,1);bumpRenown(-1);}
    else if(act==="tadd"){b.edictTimers[name]=(b.edictTimers[name]||0)+1;}
    else if(act==="treset"){b.edictTimers[name]=0;}
    save();render();};});
}
// ---- Renown & Domains view ----
function currentEra(){
  let best=null,bestR=-1;
  Object.keys(ERAS).forEach(e=>{const r=ERAS[e].renown;if(r<=(D.renown||1)&&r>bestR){bestR=r;best=e;}});
  return best||Object.keys(ERAS)[0];
}
// one track per Domain (cells 1..Sovereign, thresholds boxed) + the Standing effects table; markers = players at that value / Standing
const DOMC={Industry:"#4a7fc0",Prowess:"#c0463d",Cunning:"#8d8d9c",Piety:"#d4b23a"};
// a player's marker: a pawn in their colour (seat number on hover)
function pMark(p,i){{const h=heraldOf(p,14);if(h)return '<span class="pmk her" title="'+esc(p.name)+'">'+h+'</span>';}return '<span class="pmk" title="'+esc(p.name)+'"><svg width="11" height="15" viewBox="0 0 11 15"><circle cx="5.5" cy="3.6" r="3" fill="'+p.color+'" stroke="#000a" stroke-width=".8"/>'+
  '<path d="M3 7.2h5l1.4 4.6H1.6z" fill="'+p.color+'" stroke="#000a" stroke-width=".8"/><rect x=".6" y="11.8" width="9.8" height="2.6" rx="1" fill="'+p.color+'" stroke="#000a" stroke-width=".8"/></svg></span>';}
function domTrackHTML(d,ps,editable){const TH={[RIS]:"Rising",[EST]:"Established",[SOV]:"Sovereign"},one=ps.length===1?((ps[0].board.domains||{})[d]||0):null;
  let h='<div class="dbt" style="--dc:'+DOMC[d]+'">';
  for(let v=1;v<=SOV;v++){const at=ps.map((p,i)=>[p,D.players.indexOf(p)]).filter(([p])=>((p.board.domains||{})[d]||0)===v);
    h+='<div class="dbc'+(TH[v]?' th':'')+(one!=null&&v<=one?' on':'')+'"'+(editable?' data-dset="'+d+'|'+v+'"':'')+' title="'+esc(d+" "+v+(TH[v]?" · "+TH[v]:""))+'"><span class="dbn">'+v+'</span>'+
      (one==null&&at.length?'<span class="dbm">'+at.map(([p,i])=>pMark(p,i)).join('')+'</span>':'')+(TH[v]?'<span class="dbl">'+TH[v]+'</span>':'')+'</div>';}
  return h+'</div>';}
// Standings: one table — each Domain row's three Standings, the track points underlaid behind each effect (Rising 1–3,
// Established 4–6, Sovereign 7–10). Points up to the viewer's value fill; the cell lights when the viewer reaches its threshold.
// Every player's marker sits under its point; "held" = some player has reached it.
function standingEffectsHTML(){const ps=D.players,me=meP(),ST3=["Rising","Established","Sovereign"],lo={Rising:1,Established:RIS+1,Sovereign:EST+1};
  let h='<div class="tot dboard"><h3 style="font-size:13px">Standings'+(me?' <span class="note">· lit = '+esc(me.name)+'</span>':'')+'</h3>'+
    '<div class="dbxw"><table class="dtable dbfx dbx"><thead><tr><th>Domain</th>'+ST3.map(t=>'<th>'+t+' ('+STAND_THRESH[t]+')</th>').join('')+'</tr></thead><tbody>';
  DOMAINS.forEach(d=>{const mv=me?((me.board.domains||{})[d]||0):0;
    h+='<tr style="--dc:'+DOMC[d]+'"><th class="dbname">'+d+'</th>'+ST3.map(t=>{const a=lo[t],z=STAND_THRESH[t],n=z-a+1,eff=String((DBOARD[d]||{})[t]||""),ix=eff.indexOf(":"),
      held=ps.some(p=>((p.board.domains||{})[d]||0)>=z),lit=mv>=z,bfx=(BT.standingFx||{})[d+"|"+t];let u='',mk='';
      for(let v=a;v<=z;v++){const at=ps.filter(p=>((p.board.domains||{})[d]||0)===v);
        u+='<span class="dbu'+(v<=mv?' f':'')+(v===z?' th':'')+'">'+v+'</span>';
        mk+='<span class="dbum">'+at.map(p=>pMark(p,D.players.indexOf(p))).join('')+'</span>';}
      return '<td class="dbxc'+(held?' on':'')+(lit?' lit':'')+'"><div class="dbug" style="--n:'+n+'">'+u+'</div>'+
        '<div class="dbe">'+(ix>0?'<b>'+esc(eff.slice(0,ix))+'</b>'+esc(eff.slice(ix)):esc(eff))+'</div>'+(bfx?'<div class="note">Battle: '+esc(bfx)+'</div>':'')+
        '<div class="dbmk" style="--n:'+n+'">'+mk+'</div></td>';}).join('')+'</tr>';});
  return h+'</tbody></table></div></div>';}
function renderRenown(){const host=document.getElementById("viewRenown");if(!host)return;
  host.innerHTML=edictBoardHTML();wireEdicts(document.getElementById("viewRealm")||host);}

DO.battleclose=()=>{D.view="table";save();render();};
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&D.view==="battle"){D.view="table";save();render();}});
