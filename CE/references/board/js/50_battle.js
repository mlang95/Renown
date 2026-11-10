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
  D.battle=null;const N=battle();N.A=Object.assign(newSide(),JSON.parse(JSON.stringify(o.A)));N.B=Object.assign(newSide(),JSON.parse(JSON.stringify(o.B)));N.seize=o.seize||"";N.seizeSet=true;N.qid=o.id;return true;}
// where a battle side stands on the map
function sideHex(sd){if(!sd)return null;if(sd.kind==="bandit")return mapState().camps[sd.camp]?sd.camp:null;const q=pById(sd.pid);if(!q)return null;
  if(String(sd.aid||"").startsWith("g:")){const st=settById(q,String(sd.aid).slice(2));return st?settHex(q,st):null;}
  const a=(q.board.armies||[]).find(x=>String(x.id)===String(sd.aid));return a?armyHex(q,a):null;}
// queue a battle from the map and open it in the Battle view when that view is on
function bqStart(o){bqAdd(o);if(mods().battle){if(!battle().id)bqLoad(o);D.view="battle";flash("Battle queued: "+bqSideName(o.A)+" vs "+bqSideName(o.B));}
  else flash("Battle queued — turn on modules ▸ Battle tab to resolve it");save();render();}
const BLO=DATA.banditLoadouts||{},BLO_HC=DATA.banditLoadoutsHardcore||BLO;
// Hardcore (Host's choice at Setup › Wild Outlaw Country): Hardcore Bandit loadouts, Wild Outlaw Country and Bandit Army Move
function hardcore(){return !!D.hardcore;}
function banLO(){return hardcore()?BLO_HC:BLO;}
function banEquip(){return (hardcore()?(BAN.hardcore||{}).equipment:null)||BAN.equipment||{};}
function banWild(){return (hardcore()?(BAN.hardcore||{}).wild:null)||BAN.wild||{};}
function banditArmy(camp){camp.army=camp.army||{retinue:"",endurance:0,fatigue:0,weapon:"",ranged:"None",armor:"",shield:"None",strained:false};
  return new Proxy(camp.army,{get:(t,k)=>k==="count"?camp.n:k==="label"?"Bandits":t[k],
    set:(t,k,v)=>{if(k==="count")camp.n=v;else t[k]=v;return true;}});}
const BANDIT_DEFAULT_RETINUE="Levy";   // ruling: bandits default to Levies, changeable per battle
// the era whose Bandit loadout this camp uses: the current era, unless an era was picked for it during this era
function banditEra(a){const cur=currentEra();return a.eraPick&&a.eraPickAt===cur&&banLO()[a.eraPick]?a.eraPick:cur;}
function armBandits(camp){const a=banditArmy(camp),era=banditEra(a),lo=banLO()[era],tag=era+(hardcore()?"/hc":"");
  // Apply that era's loadout (retinue and gear) when the camp is first armed, the game enters a new era, or another era is picked.
  if(a.loadoutEra===tag)return;
  const rn=(lo&&lo.retinue&&EQ.retinues[lo.retinue])?lo.retinue:BANDIT_DEFAULT_RETINUE,rt=EQ.retinues[rn];
  if(rt){a.retinue=rn;a.endurance=rt.endurance;}
  if(lo){a.weapon=lo.weapon||"";a.armor=lo.armor||"";a.shield=lo.shield||"None";}
  a.loadoutEra=tag;}
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
// total weapon AP bonus from an army's Holding tokens ("AP -1" per Finery-style text); 0 for none
// "First AP -X" (first Skirmish only; " @<weapon>" = only while that melee weapon is Equipped, e.g. First Charge), as Combatv4
function apMod(u,rng,first,wn){return (u&&u.mods||[]).reduce((s,m)=>{const x=(rng?/^(?:Ranged )?AP ([+-]\d+)$/:/^AP ([+-]\d+)$/).exec(m.tok);if(x)return s+(+x[1]);
  const f=first?/^First AP ([+-]\d+)(?: @(.+))?$/.exec(m.tok):null;return s+(f&&(!f[2]||(!rng&&f[2]===wn))?+f[1]:0);},0);}
function sideUnlocks(p){const u=sideUnlocks0(p);u.outEvery=u.mods.some(m=>m.tok==="Outrider: every");u.outFirst=u.mods.some(m=>m.tok==="Outrider: first");return u;}
// Outrider reveal read from the Holding text ("Every Skirmish, you may force your opponent to reveal…" / "First Skirmish, …")
function sideUnlocks0(p){return p?withBoard(p.board,()=>{const have=new Set(Object.keys(PC));const {earned}=computeEarned(have);
    // "Gain Immune Awkward" (List Yard) comes with the other Holding tokens (holding_combat_tags)
    return {mods:armyUnlocks(earned).mods.concat(facCombat(p.board)),outEvery:false,outFirst:false};})
    :{mods:[],outEvery:false,outFirst:false};}
// combat standing effects (STANDING_EFFECTS) by Domain value; bandits use their camp's Domain value (Prowess = Cunning = banditDomain)
function sideDomains(sd,p){if(sd.kind==="bandit"){const cp=mapState().camps[sd.camp],v=cp?banditDomain(cp.n):0;return {Prowess:v,Cunning:v};}return (p&&p.board.domains)||{};}
function standingFxOf(dv){const out=[],F=BT.standingFx||{},TH={Rising:RIS,Established:EST,Sovereign:SOV};
  Object.keys(F).forEach(k=>{const [d,t]=k.split("|");if((dv[d]||0)>=TH[t])out.push({d,t,text:F[k]});});return out;}
// ---- Equipment (declared with the Tactic; only Equipped gear counts) ----
let EQSEL={};                                   // this device's pending choice per side, before it is submitted
// gear permissions from Holding text: carry Ranged + Melee ("dual-equip", Skirmish Field) · Dual Wield ("Florentine", List Yard)
function hasArmyTok(p,tok){return !!p&&withBoard(p.board,()=>!!armyTokHolder(tok));}
// Guige Strap (Buckler School): a 2H weapon carried beside the 1H weapon + Shield (a.weapon2h), Equipped instead of them
function g2h(a){return a&&a.weapon2h&&a.weapon2h!=="None"&&EQ.weapons[a.weapon2h]?a.weapon2h:"";}
function eqWName(a,e){return e.mode==="ranged"?a.ranged:e.mode==="2h"&&g2h(a)?a.weapon2h:(a.weapon||"");}
function eqOptions(X){const B=battle(),{p,a}=sideArmy(B[X]);if(!a)return {opts:["melee"],bastard:false};fixBastard(a);
  const r=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,real=!!a.weapon&&a.weapon!=="Farm Tools",
        one=!!r&&(r.tags||[]).includes("One-Shot")&&!hasArmyTok(p,"Immune One-Shot"),sk1=(B.sk||1)===1,bastard=!!prof2h(a.weapon);
  let opts;
  if(!r)opts=["melee"];
  else if(one)opts=sk1?["ranged","melee"]:["melee"];    // One-Shot: may be Equipped in the first Skirmish only, never after
  else if(!real)opts=["ranged"];                         // ranged-only (Farm Tools sidearm) keeps firing
  else opts=["ranged","melee"];                          // carries both (dual-equip)
  const flor=hasArmyTok(p,"Florentine");
  if(opts.includes("melee")&&flor&&canDualWield(a.weapon))opts.push("dual");   // Florentine: Dual Wield the 1H this Skirmish
  if(opts.includes("melee")&&g2h(a))opts.push("2h");                             // Guige Strap: the 2H weapon this Skirmish
  return {opts,bastard,dual:!!r&&real,carry:hasArmyTok(p,"dual-equip"),flor,one};}
function eqCode(X){const o=eqOptions(X),s=EQSEL[X]||{},m=o.opts.includes(s.mode)?s.mode:o.opts[0],a=sideArmy(battle()[X]).a||{};
  const b2h=s.b2h!=null?s.b2h:(a.b2h!=null?!!a.b2h:!(a.shield&&a.shield!=="None"));   // default: 2H without a shield
  return m+(o.bastard&&m==="melee"&&b2h?":2H":"");}
function eqNow(X){const B=battle(),rv=B.rev&&B.rev.sk===B.sk?B.rev:null,o=eqOptions(X);
  let code=rv&&rv["eq"+X]?rv["eq"+X]:eqCode(X);const [mode,prof]=code.split(":");
  const m=o.opts.includes(mode)?mode:o.opts[0];return {mode:m,b2h:prof==="2H"&&o.bastard&&m==="melee",revealed:!!(rv&&rv["eq"+X])};}
// Dual Wield: chosen in the equipment step (Florentine), only for a 1H melee weapon that allows it; it confers 2H, so the Shield gives nothing
function dualOn(a,e){return !!e&&e.mode==="dual"&&canDualWield(a.weapon);}
function eqWeapon(a,e,shDest){if(!a)return {ap:0};const r=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,w=EQ.weapons[a.weapon]||{};
  if(e.mode==="ranged"&&r)return r;
  if(e.mode==="2h"&&g2h(a))return EQ.weapons[a.weapon2h];                              // Guige Strap: the 2H weapon
  if(dualOn(a,e))return Object.assign({},w,{tags:[].concat(w.tags||[],["2H","Dual Wield"])});   // two of the same melee weapon: Dual Wield confers 2H
  if(prof2h(a.weapon)&&(e.b2h||shDest))return prof2h(a.weapon);                       // 2H profile (also forced once the shield is gone)
  return w;}
// Random Tactic: uniform over the Tactics other than Fall Back (as the sim's Random mode), limited to
// those an equipped weapon allows when its note says "May only use …" (e.g. Arquebus).
// Weapon-imposed Tactic limit (tactics_allowed, e.g. Arquebus; tactics_banned, e.g. Lance): applies while that weapon is the one
// Equipped this Skirmish — same rule as Combatv4 (tactic_mask_ranged). Returns the allowed list, or null.
function tacAllowedW(X){const B=battle(),{a}=sideArmy(B[X]||{});if(!a)return null;
  const w=eqWeapon(a,eqNow(X),!!((B.shDest||{})[X]));
  if(Array.isArray(w.tactics_allowed)&&w.tactics_allowed.length)return w.tactics_allowed.filter(t=>BT.tactics.includes(t));
  if(Array.isArray(w.tactics_banned)&&w.tactics_banned.length)return BT.tactics.filter(t=>!w.tactics_banned.includes(t));   // e.g. Lance: no Defensive Formation
  const n=String(w.note||"");if(/May only use/i.test(n)){const ok=BT.tactics.filter(t=>n.includes(t));if(ok.length)return ok;}
  return null;}
// Battle-tile limit (TACTICAL_TERRAIN "You may only play A, B, or C", e.g. Forest): Fall Back stays open (TACTICAL_GLOBAL)
function tacAllowedT(){const T=typeof bfTerrain==="function"?bfTerrain():null,e=T&&((TREF.tactical||{})[T.tile]||{}).effect;
  const m=/may only play ([^.]+)/i.exec(String(e||""));if(!m)return null;const ok=BT.tactics.filter(t=>new RegExp("\\b"+t.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+"\\b").test(m[1]));
  return ok.length?ok.concat(BT.tactics.includes("Fall Back")&&!ok.includes("Fall Back")?["Fall Back"]:[]):null;}
function tacAllowed(X){const w=tacAllowedW(X),t=tacAllowedT();if(!w)return t;if(!t)return w;const both=w.filter(x=>t.includes(x));return both.length?both:w;}
// TACTICAL_GLOBAL "Any player may Fall Back after the first Skirmish": Fall Back is off the table in Skirmish 1
const FB_LATE=(BT.tacticalGlobal||[]).some(s=>/Fall Back after the first Skirmish/i.test(s));
// a side whose Holding text says "You may Fall Back in the first Skirmish" (Outrider Intercept Post) is exempt
function fbFirstOK(X){const B=battle();return !!B&&!!B[X]&&sideUnlocks(sideArmy(B[X]).p).mods.some(m=>m.tok==="Fall Back: first");}
function tacTooEarly(t,X){return FB_LATE&&t==="Fall Back"&&battle().sk<=1&&!(X&&fbFirstOK(X));}
function tacOK(X,t){const al=tacAllowed(X);return (!al||al.includes(t))&&!tacTooEarly(t,X);}
function tacWhyNot(X,t){if(tacTooEarly(t,X))return "not in the first Skirmish";const T=tacAllowedT();return T&&!T.includes(t)?"not on this terrain ("+bfTerrain().tile+")":"not with your weapon";}
function randomTacticPool(X){let pool=BT.tactics.filter(t=>t!=="Fall Back");const al=tacAllowed(X);
  if(al){const nf=al.filter(t=>t!=="Fall Back");pool=nf.length?nf:al.filter(t=>tacOK(X,t));}
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
  const buck2h=a.shield==="Buckler Shield"&&!dualW&&u.mods.some(m=>m.tok==="Buckler 2H");   // Buckler School
  const shOff=is2H&&!!a.shield&&a.shield!=="None"&&!buck2h;                 // 2H: "Cannot use a Shield" — not Equipped this Skirmish
  const sh0=(shDest||shOff)?{save_bonus:0,init:0,tags:[]}:shRaw;             // a destroyed or unequipped shield gives nothing
  const sh=(sh0.init<0&&u.mods.some(m=>m.tok==="Shield Init +1"))?Object.assign({},sh0,{init:sh0.init+1}):sh0;   // Shieldwright
  const eqO=eqNow(O),eShD=!!((B.shDest||{})[O]);
  let ewpn={ap:0},ewm={ap:0};if(eo){ewpn=eqWeapon(eo,eqO,eShD);ewm=eqWeapon(eo,{mode:eqO.mode==="ranged"?"melee":eqO.mode,b2h:eqO.b2h},eShD);}   // Riposte = the Equipped melee weapon (the 1H one while firing)
  const strikePlus=u.mods.filter(m=>m.tok==="Strike +1").length,initPlus=u.mods.filter(m=>m.tok==="Init +1").length;
  const rev=B.rev&&B.rev.sk===B.sk?B.rev:null,cell=rev?TMX[rev.A+"|"+rev.B]:null,tm0=cell?(X==="A"?cell[0]:cell[1]):{I:0,TH:0,TS:0};
  const swall=!!(rev&&(X==="A"?rev.A:rev.B)==="Defensive Formation"&&!(shDest||shOff)&&!!a.shield&&a.shield!=="None"&&u.mods.some(m=>m.tok==="Shield Wall")),
        tm=tm0;                                                              // Shield Wall (Pavisiers' Yard): incoming AP -1 in Defensive Formation
  const forced=seizeForced(),seize=B.sk===1&&(forced?forced===X:B.seize===X)?1:0,   // Ministry: always Seizes, its opponent never
        hillI=onHill(X)?1:0;                                                            // Hill: +1 Initiative every Skirmish (TACTICAL_TERRAIN)
  // Unwieldy: Initiative can't be improved by Tactics (clamp a positive Tactic I to 0) unless Immune Unwieldy.
  // tmEff = the Tactic modifiers that actually apply (display); tmBlk = what was blocked and why.
  // Steady: a negative Tactic I is clamped to 0. Same rule as Combatv4/batch_engine.py.
  const eqInfo=eqOptions(X),dualCarry=eqInfo.dual;                            // carrying both (no longer gives Unwieldy)
  const hasM=tok=>u.mods.some(m=>m.tok===tok);
  const eqTags=[].concat(wpn.tags||[],ar.tags||[],sh.tags||[],rt.tags||[],hasM("Always Unwieldy")?["Unwieldy"]:[],hasM("Steady")?["Steady"]:[],
        (ar.tags||[]).includes("Articulated")?["Immune Strained"]:[]);   // Articulated = Fluted + Immune Strained
  const unw=eqTags.includes("Unwieldy")&&(hasM("No Immune Unwieldy")||!hasM("Immune Unwieldy")),stdy=eqTags.includes("Steady");
  let tmI=tm.I||0,tmNote="";
  if(unw&&tmI>0){tmNote="Unwieldy: ignores the Tactic's +"+tmI+" Initiative";tmI=0;}
  if(stdy&&tmI<0){tmNote="Steady: ignores the Tactic's −"+(-tmI)+" Initiative";tmI=0;}
  const mt=new Set(u.mods.map(m=>m.tok).concat(eqTags));
  // the opponent's Standing effects aimed at this side (STANDING_EFFECTS: "Opponent gains Strained" / "… Blunder in the first Skirmish")
  // this side's own Standing effects (STANDING_EFFECTS: "Immune Blunder", "Immune Panic")
  const sFx=standingFxOf(sideDomains(sd,p)),immBlunder=sFx.some(f=>/Immune Blunder/i.test(f.text)),stImmPanic=sFx.some(f=>/Immune Panic/i.test(f.text));
  const oFx=standingFxOf(sideDomains(o,sideArmy(o).p)),oStrain=oFx.find(f=>/Opponent gains Strained/i.test(f.text)),
        oBlunder=(B.sk||1)===1?oFx.find(f=>/Opponent gains Blunder in the first Skirmish/i.test(f.text)):null;
  const strainI=((effStrained(p,a)||(oStrain&&!immuneStrainIn(p,a)))&&!mt.has("Immune Strained"))?-1:0;   // Strained: −1 Init unless Immune Strained (or inside a controlled Settlement: Granary)
  const maxI=mt.has("MaxInit3")?INIT_MAX+1:INIT_MAX;   // Ministry of Military Strategy only: ceiling +1
  const rawI=(wpn.init||0)+(sh.init||0)+initPlus+tmI+seize+hillI+strainI+sd.adj.I;
  // INIT_CAP_FIRST: bonuses are capped at the maximum, then penalties apply · INIT_FLOOR off: no lower limit (Blunder at INIT_MIN or lower)
  const negI=[wpn.init||0,sh.init||0,initPlus,tmI,seize,hillI,strainI,sd.adj.I].reduce((s,v)=>s+Math.min(v,0),0);
  const I0=INIT_CAP_FIRST?Math.min(maxI,rawI-negI)+negI:Math.min(maxI,rawI);
  const I=INIT_FLOOR?Math.max(INIT_MIN,I0):I0,blunder=!immBlunder&&(I<=INIT_MIN||!!oBlunder);
  // where Initiative comes from, part by part (datasheet breakdown); a Tactic modifier its gear ignores is listed as ignored
  const initParts=[[eqWName(a,eqX)||"weapon",wpn.init||0]];
  if(sh.init)initParts.push([a.shield,sh.init]);
  u.mods.filter(m=>m.tok==="Init +1").forEach(m=>initParts.push([m.node||"Init +1",1]));
  if(tm.I)initParts.push(["Tactic",tmNote?tm.I:tmI,tmNote?"ignored ("+tmNote.split(":")[0]+")":""]);
  if(seize)initParts.push(["Seize",seize]);if(hillI)initParts.push(["Hill",hillI]);
  if(strainI)initParts.push(["Strained"+(a.strained?"":siegeStrains(p,a)?" (Besieged)":oStrain?" (enemy "+oStrain.t+" "+oStrain.d+")":""),strainI]);
  if(sd.adj.I)initParts.push(["Duke adjust",sd.adj.I]);
  // to-Strike (same order as Combatv4): base − improving, capped at CAP; Blunder clamps to CAP (Fatigue tokens only worsen Morale);
  // then worsening mods (enemy Shielded, own shield Ponderous, negative Tactic TH) apply, and the result is capped at CAP+ (never an auto-fail).
  const CAP=BT.capThr||10,tacTH=tm.TH||0;
  const th1=(mt.has("+1TH")?1:0)+(mt.has("+1TH first")&&B.sk===1?1:0)+(mt.has("+1TH after_first")&&B.sk>1?1:0);
  const rngPlus=eqX.mode==="ranged"?u.mods.filter(m=>m.tok==="Ranged Strike +1").length:0;   // e.g. "Ranged Weapons have +1 to Strike"
  const terrR=eqX.mode==="ranged"&&onGrass(X)?1:0;                                          // Open Field (a Hill counts): Ranged +1 to Strike
  const improve=strikePlus+rngPlus+terrR+th1+Math.max(tacTH,0);
  const eShOff=(ewpn.tags||[]).includes("2H")&&!(eo&&eo.shield==="Buckler Shield"&&!(ewpn.tags||[]).includes("Dual Wield")
        &&sideUnlocks(sideArmy(o).p).mods.some(m=>m.tok==="Buckler 2H"));   // enemy's 2H Equipped: its Shield gives nothing this Skirmish (Buckler School excepted)
  const esh=(eo&&!((B.shDest||{})[O])&&!eShOff)?(EQ.shields[(eo.shield==="None"||!eo.shield)?"null":eo.shield]||{tags:[]}):{tags:[]};
  // Shielded N (Heater: Shielded 2, Tower: Shielded 3) vs the attacker's Hook X (Negate Shielded = all of it)
  const shVal=tg=>[].concat(tg||[]).reduce((b,t)=>{const m=String(t).match(/^Shielded (\d+)$/);return m?Math.max(b,+m[1]):t==="Shielded"?Math.max(b,1):b;},0);
  const hookV=[...mt].reduce((b,t)=>t==="Negate Shielded"?99:(m=>m?Math.max(b,+m[1]):b)(String(t).match(/^Hook (\d+)$/)),0);
  const eShN=shVal(esh.tags),eShEff=Math.max(0,eShN-hookV),eShielded=eShEff>0;
  const worsen=eShEff+((sh.tags||[]).includes("Ponderous")?1:0)+(mt.has("Immune Tactic TH")?0:Math.max(-tacTH,0));
  let pre=Math.min((rt.to_hit||0)-improve,CAP);if(blunder)pre=Math.max(pre,CAP);
  let toStrike=Math.min(pre+worsen-sd.adj.TH,CAP);
  // Save: Riveted (Armory ward; was Planishing): AP can't push the save past CAP+
  // (normal or Deadly) unless the attacker has Negate Riveted. Deadly strikes save at +DEADLY_AP.
  const FACES_=BT.faces||10,FOC=BT.focusedThr||10,DAP=BT.deadlyAp??5;
  const plan=mt.has("Riveted")||mt.has("GF Armor");
  const eTags=new Set([].concat(ewpn.tags||[]));
  const planOn=plan&&!eTags.has("Negate Riveted")&&!eTags.has("Negate Tempered");
  const eUap=sideUnlocks(sideArmy(o).p),sk1AP=(B.sk||1)===1,eApMod=apMod(eUap,!!(eqO&&eqO.mode==="ranged"),sk1AP,eo?eqWName(eo,eqO):""),
        eApModM=apMod(eUap,false,sk1AP,eo?eqWName(eo,{mode:eqO.mode==="ranged"?"melee":eqO.mode}):""),apOwn=apMod(u,eqX.mode==="ranged",sk1AP,eqWName(a,eqX));                     // "AP -N" (Finery: Weapons gain -1AP): more negative = more AP
  // Fluted (armor): incoming AP reduced by 1 toward 0 (Ranged and Riposte too), applied after Deadly; AP 0 unaffected.
  const flutN=((ar.tags||[]).includes("Articulated")?1:0)+(swall?1:0),flut=flutN>0,flAP=ap=>flutN?Math.min(ap+flutN,0):ap;   // Articulated (was Fluted) + Shield Wall
  const saveNoFl=(ar.save||0)-((ewpn.ap||0)+eApMod)-(sh.save_bonus||0)-(tm.TS||0)-sd.adj.TS;
  const saveRaw=(ar.save||0)-flAP((ewpn.ap||0)+eApMod)-(sh.save_bonus||0)-(tm.TS||0)-sd.adj.TS;
  const save=planOn?Math.min(saveRaw,CAP):Math.min(saveRaw,FACES_+1);   // FACES+1 = auto-fail
  // Deadly: "set" (Version D) = the Strike HAS AP −DAP (Fluted −1 of it), no Recover; "additional" = +DAP on top of the weapon
  const dSet=BT.deadlyMode==="set";
  const deadlyRaw=Math.min(dSet?(ar.save||0)+DAP-flutN-(sh.save_bonus||0)-(tm.TS||0)-sd.adj.TS:saveNoFl+DAP-flutN,FACES_+1),deadlySave=planOn?Math.min(deadlyRaw,CAP):deadlyRaw;
  const saveVs=wp=>{const tg=new Set([].concat(wp.tags||[])),po=plan&&!tg.has("Negate Riveted")&&!tg.has("Negate Tempered"),
    raw=(ar.save||0)-flAP((wp.ap||0)+eApModM)-(sh.save_bonus||0)-(tm.TS||0)-sd.adj.TS;return po?Math.min(raw,CAP):Math.min(raw,FACES_+1);};
  const saveMelee=saveVs(ewm);                                  // vs a Riposte (always the riposting side's melee weapon)
  // own strike profile (Focused procs)
  const critN=[...mt].map(t=>(t.match(/^Crit (\d+)$/)||[])[1]).filter(Boolean).map(Number);
  const critPlus=[...mt].reduce((s,t)=>{const m=String(t).match(eqX.mode==="ranged"?/^(?:Ranged )?Crit \+(\d+)$/:/^Crit \+(\d+)$/);return s+(m?+m[1]:0);},0);
  const critFloor=Math.min(FOC,...critN)-critPlus;
  const wTags=new Set([].concat(wpn.tags||[]));
  const wk=k=>wTags.has(k)||mt.has(k);   // weapon keyword, or granted by a Holding ("Gain Deadly")
  const hasDeadly=wk("Deadly"),hasCleave=wk("Cleave"),hasDestroy=wk("Destroy Shield");
  const trig=[];
  if(tmNote)trig.push(tmNote);
  if(shDest)trig.push("Shield destroyed: its save, Init and tags are gone");
  if(eShielded)trig.push("Enemy Shielded"+(eShN>1?" "+eShN:"")+": +"+eShEff+" to-Strike"+(hookV&&hookV<99?" (Hook "+hookV+" ignores "+Math.min(hookV,eShN)+")":""));
  else if(eShN&&hookV)trig.push((hookV>=99?"Negate Shielded":"Hook "+hookV)+": enemy Shielded ignored");
  if(mt.has("Immune Tactic TH")&&tacTH<0)trig.push("Immune Tactic TH: Tactic "+tacTH+" ignored");
  if(th1)trig.push("+"+th1+" to-Strike (Ministry)");
  if(rngPlus)trig.push("+"+rngPlus+" to-Strike with Ranged (faction)");
  if(apOwn)trig.push("Weapons "+apOwn+" AP ("+u.mods.filter(m=>/^AP -\d+$/.test(m.tok)).map(m=>m.node).join(", ")+")");
  if(terrR)trig.push((onHill(X)?"Hill (Open Field)":"Open Field")+": Ranged Weapons +1 to Strike");
  if(hasM("Always Unwieldy"))trig.push("Faction: always Unwieldy"+(hasM("No Immune Unwieldy")?", can't gain Immune Unwieldy":""));
  if(immBlunder&&(I<=INIT_MIN||oBlunder))trig.push("Immune Blunder (Standing): no Blunder");
  if(blunder)trig.push("Blunder: to-Strike "+CAP+"+ before penalties"+(oBlunder&&I>INIT_MIN?" (enemy "+oBlunder.t+" "+oBlunder.d+", first Skirmish)":""));
  if(a.strained||siegeStrains(p,a)||oStrain)trig.push(strainI?"Strained −1 Init"+(a.strained?"":siegeStrains(p,a)?" (Besieged)":" (enemy "+oStrain.t+" "+oStrain.d+")"):"Immune Strained: no Init loss");
  {const ms=moraleStanding(a);if(ms)trig.push(ms.src+" Morale +"+ms.n+": Morale value −"+ms.n+" (steadier)");}
  {const mp=moralePO(a);if(mp)trig.push(mp.src+" (Public Order) Morale −"+mp.n+": Morale value +"+mp.n);}
  if(maxI>INIT_MAX)trig.push("Init ceiling +"+maxI);
  if(plan)trig.push(planOn?"Riveted: save capped "+CAP+"+"+(saveRaw>CAP||deadlyRaw>CAP?" (was "+saveRaw+"+ / Deadly "+deadlyRaw+"+)":""):"Riveted negated by enemy weapon");
  if(flut)trig.push(((ar.tags||[]).includes("Articulated")?"Articulated":"")+(swall?((ar.tags||[]).includes("Articulated")?" + ":"")+"Shield Wall":"")+": enemy AP reduced by "+flutN);
  if(hasDeadly)trig.push(BT.deadlyMode==="set"?"Deadly: strikes on "+critFloor+"+ are AP −"+DAP+", Parried only on "+FOC+", can't be Recovered":"Deadly: strikes on "+critFloor+"+ save at +"+DAP);
  if(hasCleave)trig.push("Cleave: strikes on "+critFloor+"+ roll an extra die");
  if(hasDestroy)trig.push("Destroy Shield: any "+FOC+"+ strike destroys the enemy shield");
  const morale=(c=>c!=null?Math.min(c,effMorale(a)+sd.adj.M):effMorale(a)+sd.adj.M)(moraleCap(a));
  // ---- Parry / Riposte / Recover (defending against O's Strikes) — same model as Combatv4 build_parry_thr / build_regen_thr ----
  const eSd=o,eU=sideUnlocks(sideArmy(eSd).p),eTok=new Set(eU.mods.map(m=>m.tok)),eW=new Set([].concat(ewpn.tags||[])),eRanged=!!(eo&&eo.ranged&&eo.ranged!=="None"&&eqO&&eqO.mode==="ranged");   // Negate Riposte only while their Ranged weapon is Equipped
  const sfx=standingFxOf(sideDomains(sd,p)),gainParry=sfx.find(x=>/Gain Parry/i.test(x.text));
  const crudeSh=(sh.tags||[]).includes("Crude"),crude=wTags.has("Crude")||crudeSh,awkward=crude||(mt.has("Awkward")&&!mt.has("Immune Awkward")),canParry=(!!gainParry||mt.has("Parry"))&&!awkward;       // Awkward: no Parry, so no Riposte · Crude: same, and Immune Awkward doesn't help
  const parryPlus=u.mods.filter(m=>m.tok==="Parry +1").length,IPM=BT.improvedParryMod??1,UM=BT.unstoppableMod??2;
  const eUnstop=eW.has("Unstoppable")||eTok.has("Unstoppable"),adjP=+(sd.adj.P||0),adjR=+(sd.adj.R||0),fatN=a.fatigue||0;
  const eWm=new Set([].concat(ewm.tags||[]));
  const parryThr=Math.min(CAP,(BT.parryBase||8)-parryPlus*IPM+(eUnstop?UM:0)-adjP);                 // Fatigue no longer affects Parry
  const parryThrMelee=Math.min(CAP,(BT.parryBase||8)-parryPlus*IPM+(eWm.has("Unstoppable")?UM:0)-adjP);
  const ripP=mt.has("Riposte +1"),hasRip=mt.has("Riposte"),eNegRip=eTok.has("Negate Riposte"),riposte=hasRip&&!eW.has("Negate Riposte")&&!eNegRip&&!eRanged,riposteMelee=hasRip&&!eWm.has("Negate Riposte")&&!eNegRip;   // Dual Wield: Riposte +1 (a parrying 9 also Ripostes)
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
  if(canParry)trig.push("Parry "+parryThr+"+"+(parryPlus?" (Improved −"+parryPlus*IPM+")":"")+(eUnstop?" · enemy Unstoppable +"+UM:"")+(riposte?" · Riposte on "+(ripP?(FOC-1)+"+":FOC):"")+(dualW?" · Dual Wield: failed Parries re-rolled (a reroll can't Riposte)":""));
  else if(awkward)trig.push("No Parry: "+(crudeSh&&!wTags.has("Crude")?a.shield:eqWName(a,eqX))+" is "+(crude?"Crude":"Awkward"));
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
    dualW&&!eqInfo.flor&&p?"Dual Wield needs Florentine ("+armyTokNamed("Florentine")+")":""].filter(Boolean));
  // the Strike and Save targets part by part, for the explainers: [label, change to the target] (a lower target is easier)
  const wName=eqWName(a,eqX)||"melee weapon",eWName=eo?(eqWName(eo,eqO)||"melee weapon"):"",
        nodes=tok=>u.mods.filter(m=>m.tok===tok).map(m=>m.node).filter(Boolean).join(", ");
  const strikeParts=[[(a.retinue||"Retinue")+" base",rt.to_hit||0]];
  if(strikePlus)strikeParts.push(["Strike +1"+(nodes("Strike +1")?" ("+nodes("Strike +1")+")":""),-strikePlus]);
  if(rngPlus)strikeParts.push(["Ranged Strike +1",-rngPlus]);if(terrR)strikeParts.push([(onHill(X)?"Hill":"Open Field")+" (Ranged)",-terrR]);
  if(th1)strikeParts.push(["Ministry",-th1]);if(tacTH>0)strikeParts.push(["Tactic",-tacTH]);
  if(eShielded)strikeParts.push(["their "+eo.shield+" (Shielded"+(eShN>1?" "+eShN:"")+(eShEff<eShN?", Hook −"+(eShN-eShEff):"")+")",eShEff]);if((sh.tags||[]).includes("Ponderous"))strikeParts.push(["your "+a.shield+" (Ponderous)",1]);
  if(tacTH<0&&!mt.has("Immune Tactic TH"))strikeParts.push(["Tactic",-tacTH]);if(sd.adj.TH)strikeParts.push(["Duke adjust",-sd.adj.TH]);
  if(blunder)strikeParts.push(["Blunder: no better than "+CAP+"+",0]);
  if(pre+worsen-sd.adj.TH>CAP)strikeParts.push(["no worse than "+CAP+"+",0]);
  const eAP=(ewpn.ap||0)+eApMod,saveParts=[[(a.armor||"Cloth")+" base",ar.save||0]];
  if(eAP)saveParts.push(["their "+(eWName||"weapon")+" (AP "+String(eAP).replace("-","−")+")",-eAP]);if(flut&&eAP<0)saveParts.push([(a.armor||"armor")+" (Articulated)",-1]);if(sh.save_bonus)saveParts.push([a.shield,-sh.save_bonus]);
  if(tm.TS)saveParts.push(["Tactic",-tm.TS]);if(sd.adj.TS)saveParts.push(["Duke adjust",-sd.adj.TS]);
  if(planOn&&saveRaw>CAP)saveParts.push(["Riveted: no worse than "+CAP+"+",0]);
  return {dualW,ripP,immunePanic:mt.has("Immune Panic")||stImmPanic,eqX,shOff,enduring,canParry,parryThr,parryThrMelee,riposte,riposteMelee,saveMelee,poisoned,poisonedMelee,recThr,serrN,p,a,rt,I,rawI,tmNote,initParts,strainI,strainBy:a.strained?"":siegeStrains(p,a)?"Besieged":oStrain&&!immuneStrainIn(p,a)?"enemy "+oStrain.t+" "+oStrain.d:"",tmEff:Object.assign({},tm,{I:tmI,TH:mt.has("Immune Tactic TH")&&tacTH<0?0:tacTH}),tmBlk:[tmNote,mt.has("Immune Tactic TH")&&tacTH<0?"Immune Tactic TH: Tactic "+tacTH+" ignored":""].filter(Boolean),blunder,toStrike,save,saveRaw,deadlySave,planOn,critFloor,hasDeadly,hasCleave,hasDestroy,shDest,trig,apOwn,morale,front,field,reserve:Math.max(0,field-front),camp:Math.max(0,(a.count||0)-field),skCas,tags,tm,seize,cell:!!cell,outrider:(u.outEvery||(u.outFirst&&B.sk===1)),outEvery:u.outEvery,
    wName,wpn,eWName,strikeParts,saveParts,ar};
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
  ["A","B"].forEach(s=>{const v=PICKS[s]&&PICKS[s].tactic;if(v&&v.includes("|")){const [t,e,w]=v.split("|");PICKS[s].tactic=t;PICKS[s].eq=e;PICKS[s].swap=w==="S";}});
  if(PICKS.revealed&&PICKS.A.tactic&&PICKS.B.tactic&&!(B.rev&&B.rev.sk===B.sk)){
    B.rev={sk:B.sk,A:PICKS.A.tactic,B:PICKS.B.tactic,eqA:PICKS.A.eq||eqCode("A"),eqB:PICKS.B.eq||eqCode("B")};
    // Heritage "before Tactics are revealed, you may swap your Tactic with your opponent's" (chosen blind with the pick)
    {const sw=["A","B"].filter(X=>PICKS[X].swap&&sideSwaps(X));if(sw.length===1){const t=B.rev.A;B.rev.A=B.rev.B;B.rev.B=t;blog(sideNm(sw[0])+" swaps Tactics ("+sideSwaps(sw[0])+")");}}
    blog("Tactics revealed — A: "+B.rev.A+" ("+B.rev.eqA+"), B: "+B.rev.B+" ("+B.rev.eqB+")");
    narrate("reveal","A",{tactic:B.rev.A,foe_tactic:B.rev.B});{const cA=sideCalc("A"),cB=sideCalc("B");if(cA&&cB&&cA.I!==cB.I)narrate("first",cA.I>cB.I?"A":"B");}save();}
}
// Bandit side on the bandit table: roll its Tactic (d FACES on BAN.tacticTable) and lock it in
function banditRollTactic(X){const v=1+Math.floor(Math.random()*(BAN.faces||10)),t=dieLookup(BAN.tacticTable,v);
  blog(X+" bandits roll d"+(BAN.faces||10)+": "+v+" → "+t);save();return pickTactic(X,t);}
// the side's player holds a "swap your Tactic with your opponent's" Heritage: its name, else ""
const SWAP_SEL={};
function sideSwaps(X){const sd=battle()[X]||{};if(sd.kind==="bandit"||String(sd.aid||"").startsWith("g:"))return "";const p=sd.pid!=null?pById(sd.pid):null;return p&&srcHas(p.board,"swap_tactic")?p.board.faction:"";}
async function pickTactic(side,t){
  const B=battle();
  if(!tacOK(side,t)){
    if((B[side]||{}).kind==="bandit"){const pool=randomTacticPool(side);if(!pool.length)return;const t2=pool[Math.floor(Math.random()*pool.length)];blog(side+" bandits can't play "+t+" ("+tacWhyNot(side,t)+") → "+t2);t=t2;}
    else{flash(t+" "+tacWhyNot(side,t)+" — "+(tacAllowed(side)||[]).join(", "));return;}}
  const tv=t+"|"+eqCode(side)+(SWAP_SEL[side]&&sideSwaps(side)?"|S":"");   // Tactic and equipment (and a blind Tactic swap) are submitted together
  if(API.online){const r=await apiRaw("PUT","/api/battle/"+B.id+"/"+pickKey()+"/"+side,{tactic:tv});if(r&&r.status===409)flash("both sides already locked in");}
  else{const k=B.id+":"+pickKey();LOCAL_PICKS[k]=LOCAL_PICKS[k]||{};if(!(LOCAL_PICKS[k].A&&LOCAL_PICKS[k].B))LOCAL_PICKS[k][side]=tv;}
  await loadPicks();
  // the other side locked in: Bandits on the bandit table roll theirs at once
  const O=side==="A"?"B":"A",od=B[O]||{};
  if(B[side].kind!=="bandit"&&od.kind==="bandit"&&!od.tmode&&!(PICKS[O]||{}).picked&&!(B.rev&&B.rev.sk===B.sk)){await banditRollTactic(O);return;}
  render();
}
function mdLite(t){return esc(t||"").replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/\*(.+?)\*/g,"<i>$1</i>").replace(/\n/g,"<br>");}
// long form for the side panel: "-1 Initiative, +1 to Strike" (the matrix table keeps the short codes)
function fmtModLong(m){if(!m)return "—";const L={I:"Initiative",TH:"TH",TS:"TS"},o=[];
  ["I","TH","TS"].forEach(k=>{if(m[k])o.push((m[k]>0?"+":"")+m[k]+" "+L[k]);});
  if(m.no_combat)o.push("no combat");if(m.end)o.push("ends");if(m.strain)o.push("Strained");return o.join(", ")||"no modifier";}
function fmtMod(m){if(!m)return"—";const o=[];["I","TH","TS"].forEach(k=>{if(m[k])o.push(k+" "+(m[k]>0?"+":"")+m[k]);});
  if(m.no_combat)o.push("no combat");if(m.end)o.push("ends");if(m.strain)o.push("Strained");return o.join(" ")||"·";}
// roll modifiers go on the dice, not the target: a die shows its natural roll + mod and succeeds at base+ (same maths as
// natural >= target, with mod = base - target); positive is good. Filled = made it, outlined gold = a natural 10 (Focused).
const sgnD=m=>m>0?"+"+m:m<0?"\u2212"+(-m):"±0";
function dieRow(dice,target,mod){const FOC=BT.focusedThr||10;mod=mod||0;return dice.map(v=>'<span class="dq'+(v>=target?' ok':'')+(v>=FOC?' ten':'')+'" title="rolled '+v+(mod?' '+sgnD(mod)+' = '+(v+mod):'')+(v>=target?' — made it':' — missed')+(v>=FOC?' · a natural 10 (Focused)':'')+'">'+(v+mod)+'</span>').join('');}
const DQ_KEY='<span class="note dq-key"><span class="dq ok">7</span> made it · <span class="dq">3</span> missed · <span class="dq ok ten">10</span> natural 10</span>';
function rollNeed(t,base){const F=BT.faces||10,m=base-t;return t>F?"can't succeed (it would need more than an Unmodified "+F+")":"need <b>"+base+"+</b>"+(m?" · each die "+sgnD(m):"");}
function rollHTML(X){const R=(battle().rolls||{})[X];if(!R)return"";const base=R.base!=null?R.base:R.target,mod=base-R.target;
  const word=R.kind==="Strike"?(R.succ===1?"hit":"hits"):R.kind==="Parry"?"parried":R.kind==="Save"?"saved":R.kind==="Recover"?"recovered":"held";
  let h=esc(R.rr?"Dual Wield re-roll":R.cleave?"Cleave":R.kind)+' — '+rollNeed(R.target,base)+': '+dieRow(R.dice,R.target,mod)+' → <b>'+R.succ+'</b> '+word+(R.kind==="Strike"&&R.deadly?' · <b>'+R.deadly+'</b> Deadly':'');
  if(R.dl)h+='<br>Deadly — '+rollNeed(R.dl.target,base)+': '+dieRow(R.dl.dice,R.dl.target,base-R.dl.target)+' → <b>'+R.dl.succ+'</b> '+word;
  if(R.cas!=null)h+='<br>Casualties: <b>'+R.cas+'</b>';
  return '<div class="note" style="margin-top:4px">'+h+' '+DQ_KEY+'</div>';}
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
    st("Init",sg(c.I),INIT_LIMIT_TXT+(c.tmNote?" · "+c.tmNote:""),c.rawI!==c.I?"raw "+sg(c.rawI):c.tmNote?c.tmNote.split(":")[0]:"")+
    st("Strike",tgt(c.toStrike),"",c.toStrike>F?"auto-fail":c.blunder?"Blunder":"",c.blunder||c.toStrike>F)+
    st("Save",tgt(c.save),"armor − enemy AP − shield − TS"+(c.planOn?" · Riveted cap":""),c.save>F?"auto-fail":c.planOn&&c.saveRaw>c.save?"capped":"",c.save>F)+
    (oc&&oc.hasDeadly?st("vs Deadly",tgt(c.deadlySave),(BT.deadlyMode==="set"?"Deadly strikes: AP −"+(BT.deadlyAp??10):"Deadly strikes: save +"+(BT.deadlyAp??5))+(c.planOn?", Riveted cap":""),c.deadlySave>F?"auto-fail":"",c.deadlySave>F):"")+
    st("Parry",c.canParry?c.parryThr+"+":"—",c.canParry?"vs enemy Strikes; Deadly: "+(BT.focusedThr||10)+" only; vs Riposte "+c.parryThrMelee+"+":"no Parry")+
    st("Recover",c.recThr!=null?c.recThr+"+":"—","after a failed Save; Deadly: "+(BT.deadlyMode==="set"?"can't be Recovered":(BT.focusedThr||10)+" only"))+
    st("Morale",c.morale+"+","",c.morale>=11?"Rout":"",c.morale>=11)+
    st("End.",a.endurance||0,"Endurance")+st("Fatigue",a.fatigue||0)+'</div>';
  {const sg2=v=>(v>0?"+":v<0?"\u2212":"")+Math.abs(v),parts=c.initParts.map(([n,v,why])=>esc(n)+' '+(why?'<s>'+sg2(v)+'</s> '+esc(why):sg2(v))).join(' · ');
   h+='<div class="ds-mods ds-init"><span><b>Init</b> '+parts+' = <b>'+sg(c.I)+'</b>'+(c.rawI!==c.I?' ('+INIT_LIMIT_TXT+')':'')+'</span></div>';
   // Morale value (lower is steadier): Retinue base, Standing (Morale +N lowers it), Fatigue tokens and Public Order raise it
   const ms=moraleStanding(a),mp=moralePO(a),fat=a.fatigue||0,FMo=BT.fatigueMorale??2,cap=moraleCap(a),mo=[[a.retinue||"base",moraleBase(a),1]];
   if(ms)mo.push([ms.src+" Morale +"+ms.n,-ms.n]);if(fat)mo.push(["Fatigue ×"+fat,FMo*fat]);if(mp)mo.push([mp.src,mp.n]);if(sd.adj.M)mo.push(["Duke adjust",sd.adj.M]);
   h+='<div class="ds-mods ds-init"><span><b>Morale</b> '+mo.map(([n,v,b])=>esc(n)+' '+(b?v+'+':sg2(v))).join(' · ')+' = <b>'+c.morale+'+</b>'+(cap!=null?' (capped '+cap+'+)':'')+'</span></div>';}
  h+='<div class="ds-mods"><span>Tactic: '+(c.cell?esc(fmtModLong(c.tmEff)+c.tmBlk.map(t=>' · '+t).join('')):'pending')+'</span>'+
    (c.strainBy?'<label title="from '+esc(c.strainBy)+', not the Army\'s own Strained"><input type="checkbox" checked disabled> Strained ('+esc(c.strainBy)+(c.strainI?'':', Immune')+')</label>'
      :'<label><input type="checkbox" class="bstr" data-x="'+X+'"'+(a.strained?' checked':'')+'> Strained'+(a.strained&&!c.strainI?' (Immune)':'')+'</label>')+'</div>';
  // wargear: base profiles (before modifiers); Equipped weapon first, the carried alternative dimmed
  const rw=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,mw=EQ.weapons[a.weapon]||null,ar=EQ.armors[a.armor]||{},
        sh=(a.shield&&a.shield!=="None")?EQ.shields[a.shield]:null,onR=c.eqX.mode==="ranged"&&!!rw,shown=new Set();
  // one item: name row (AP / Init / Save), then its traits on a line of their own
  const row=(n,nm,it,ap,ini,sv,on,fl,ex)=>{const tg=dispTags(it.tags,!!(EQ.ranged||{})[n]),cl=[on?'':'off',tg.length?'has-trt':''].filter(Boolean).join(' ');
    return '<tr'+(cl?' class="'+cl+'"':'')+(it.tier?' title="'+esc(it.tier_label||it.tier)+'"':'')+'><td>'+
      (SPR&&SPR.S["eq:"+n]?'<span class="ic">'+eqSVG(n,20)+'</span>':'')+esc(nm)+(fl?'<span class="st">'+fl+'</span>':'')+(ex||'')+'</td><td>'+ap+'</td><td>'+ini+'</td><td>'+sv+'</td></tr>'+
      (tg.length?'<tr class="trt'+(on?'':' off')+'"><td colspan="4">'+tg.map(t=>{shown.add(t);return kwc(t);}).join("")+'</td></tr>':'');};
  const wrow=(n,nm,it,on,fl)=>row(n,nm,it,(it.ap||0)+(c.apOwn||0),sg(it.init),"—",on,fl),two=!!(rw&&mw&&!(onR&&a.weapon==="Farm Tools"));
  let g='';const w2n=g2h(a),w2=w2n?EQ.weapons[w2n]:null;
  if(w2&&mw){const on2=c.eqX.mode==="2h";                                       // Guige Strap: the Equipped set first
    if(on2)g+=wrow(w2n,w2n,w2,true,"equipped")+wrow(a.weapon,a.weapon,mw,false,"carried");
    else g+=wrow(a.weapon,a.weapon+(c.dualW?" ×2":""),mw,true,"equipped")+wrow(w2n,w2n,w2,false,"carried");}
  else if(onR){g+=wrow(a.ranged,a.ranged,rw,true,two?"equipped":"");if(two)g+=wrow(a.weapon,a.weapon,mw,false,"carried");}
  else{if(mw)g+=wrow(a.weapon,a.weapon+(c.eqX.b2h?" (2H)":"")+(c.dualW?" ×2":""),c.eqX.b2h&&prof2h(a.weapon)?prof2h(a.weapon):mw,true,two?"equipped":"");if(rw)g+=wrow(a.ranged,a.ranged,rw,false,"carried");}
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
      :(pk2.picked?'':'<div class="note">Bandits roll their Tactic when the other side locks in.</div>');
  }
  else if(B.id&&(mine||!API.online||tmode==="manual")&&tmode!=="random"&&!(B.rev&&B.rev.sk===B.sk)){
    {const eo_=eqOptions(X),cur=eqNow(X);
      if(eo_.opts.length>1||eo_.bastard)h+='<div style="margin-top:4px;display:flex;gap:6px;align-items:center"><span class="note">Equipment</span>'+
        (eo_.opts.length>1?'<select class="beq" data-x="'+X+'"'+(pk2.picked?' disabled':'')+'>'+eo_.opts.map(m=>'<option value="'+m+'"'+(cur.mode===m?' selected':'')+'>'+(m==="ranged"?esc(a.ranged)+(!((EQ.ranged[a.ranged]||{}).tags||[]).includes("2H")&&a.shield&&a.shield!=="None"?' + '+esc(a.shield):''):m==="dual"?'Florentine: two '+esc(a.weapon):m==="2h"?esc(a.weapon2h):esc(a.weapon||"melee")+(a.shield&&a.shield!=="None"?' + '+esc(a.shield):''))+'</option>').join('')+'</select>':'')+
        (eo_.bastard?'<select class="beqb" data-x="'+X+'"'+(pk2.picked?' disabled':'')+'><option value="1H"'+(cur.b2h?'':' selected')+'>1H</option><option value="2H"'+(cur.b2h?' selected':'')+'>2H</option></select>':'')+
        '<span class="note">submitted with your Tactic</span></div>';
      else if(eo_.one&&eo_.opts[0]==="ranged")h+='<div class="note" style="margin-top:4px">One-Shot: '+esc(a.ranged)+(!((EQ.ranged[a.ranged]||{}).tags||[]).includes("2H")&&a.shield&&a.shield!=="None"?' + '+esc(a.shield):'')+' is Equipped this Skirmish.</div>';}
    if(sideCalc(O)&&sideCalc(O).outrider&&!pk2.picked)h+='<div class="note" style="color:var(--order)">Opponent has Outrider: pick first — your Tactic is shown to them.</div>';
    h+='<div class="tcards">'+BT.tactics.map(t=>{const ok=tacOK(X,t),on=pk2.tactic===t||(!pk2.picked&&TAC_SEL[X]===t);return '<button class="btac tcard'+(on?' on':'')+'" data-x="'+X+'" data-t="'+esc(t)+'"'+(ok&&!pk2.picked?'':' disabled'+(ok?'':' title="'+tacWhyNot(X,t)+'"'))+'>'+(ok?tacCardBody(X,t):'<b>'+esc(t)+'</b><div class="note">'+tacWhyNot(X,t)+'</div>')+'</button>';}).join('')+
      (!pk2.picked&&sideSwaps(X)?'<label class="note" title="'+esc(sideSwaps(X))+'"><input type="checkbox" class="bswap" data-x="'+X+'"'+(SWAP_SEL[X]?' checked':'')+'> swap Tactics with the opponent</label> ':'')+
      (!pk2.picked?'<button class="btlock" data-x="'+X+'"'+(TAC_SEL[X]&&tacOK(X,TAC_SEL[X])?'':' disabled')+'>Lock in'+(TAC_SEL[X]?' '+esc(TAC_SEL[X]):'')+'</button>':'')+'</div>'+
      (tacAllowed(X)?'<div class="note">'+(tacAllowedT()?esc(bfTerrain().tile)+(tacAllowedW(X)?' + weapon':'')+' allows only: ':'Equipped weapon allows only: ')+tacAllowed(X).map(esc).join(", ")+'</div>':'')+tacDetailHTML(X,pk2.tactic||TAC_SEL[X]);
    if(mine&&c.outrider)h+='<div style="margin-top:4px"><button id="bpeek"'+(PEEK?' disabled':'')+'>Outrider: reveal opponent'+(op.picked?'':' (once they pick)')+'</button> <span class="note">'+(c.outEvery?'every Skirmish':'first Skirmish')+'</span></div>';
  }
  return h+'</div>';}
// ---- explainers: what a Tactic pairing does to both sides' numbers, and what the next roll is for ----
// whatIf(tA,tB): both sides' sideCalc as if those Tactics were revealed this Skirmish (B.rev swapped in and restored); memoised per render
const WHATIF=new Map();
function whatIf(tA,tB){const B=battle(),k=B.sk+"|"+tA+"|"+tB;if(WHATIF.has(k))return WHATIF.get(k);
  const had=Object.prototype.hasOwnProperty.call(B,"rev"),old=B.rev;let r;
  try{B.rev={sk:B.sk,A:tA,B:tB};r={A:sideCalc("A"),B:sideCalc("B"),cell:TMX[tA+"|"+tB]||null};}finally{if(had)B.rev=old;else delete B.rev;}
  WHATIF.set(k,r);return r;}
function recFx(sv){return (BT.deadlyMode==="set"?0:(sv.d||0))+(sv.pz||0);}   // Focused-only Recover dice
// chance one Strike die from att becomes a casualty on def: hit, not Parried, not Saved, not Recovered (Deadly: Parry / Recover on a 10
// only, Save at the Deadly target); Cleave's chain of extra dice counted. An estimate for comparing Tactics, not a rule.
function woundChance(att,def){const F=BT.faces||10,FOC=BT.focusedThr||10,pge=t=>t>F?0:Math.max(0,Math.min(1,(F-t+1)/F));
  const pp=x=>def.dualW?1-(1-x)*(1-x):x,through=dl=>(1-(def.canParry?pp(pge(dl?FOC:def.parryThr)):0))*(1-pge(dl?def.deadlySave:def.save))*(1-(def.recThr!=null?(dl&&BT.deadlyMode==="set"?0:pge(dl?FOC:def.recThr)):0));
  let p=0;for(let v=1;v<=F;v++){if(att.toStrike>F||v<att.toStrike)continue;const crit=v>=att.critFloor,dl=att.hasDeadly&&crit;p+=through(dl)/F;
    if(att.hasCleave&&crit){const pc=pge(Math.max(att.toStrike,att.critFloor)),chain=1/(1-Math.min(pc,0.95));   // expected Cleave dice per Focused Strike
      for(let e=1;e<=F;e++)if(e>=att.toStrike)p+=chain*through(att.hasDeadly&&e>=att.critFloor)/F/F;}}
  return p;}
// one Tactic pairing from X's side: who strikes first, both targets, expected casualties each way
function tacPair(X,mine,theirs){const O=X==="A"?"B":"A",w=X==="A"?whatIf(mine,theirs):whatIf(theirs,mine),cx=w[X],co=w[O];if(!cx||!co)return null;
  const cell=w.cell?(X==="A"?w.cell:[w.cell[1],w.cell[0]]):null,ends=!!(cell&&(cell[0].end||cell[1].end)),none=!!(cell&&cell[0].no_combat);
  return {cx,co,ends,none,strain:!!(cell&&cell[0].strain),first:cx.I>co.I?"you":cx.I<co.I?"they":"together",
    deal:ends||none?0:cx.front*woundChance(cx,co),take:ends||none?0:co.front*woundChance(co,cx)};}
const tgtTxt=v=>v>(BT.faces||10)?"can't":v+"+";
// a Tactic's motifs in words, from the matrix: [key, label, +1 good for you / −1 bad / 0 neither]. Initiative is read against theirs.
const TAC_MOTIF=[["iU","Gain Initiative",1],["iD","Lose Initiative",-1],["iS","Initiative swings",0],["sU","Gain Strike",1],["sD","Lose Strike",-1],
  ["vU","Gain Save",1],["vD","Lose Save",-1],["fsU","Foe gains Strike",-1],["fsD","Foe loses Strike",1],["fvU","Foe gains Save",-1],["fvD","Foe loses Save",1],
  ["end","Ends the Battle",0],["str","Gain Strained",-1],["fstr","Foe gains Strained",1],["none","No combat",0]];
function cellMotifs(mine,their){const k=[];if(!mine||!their)return k;
  if(mine.end){k.push("end");if(mine.strain)k.push("str");if(their.strain)k.push("fstr");return k;}if(mine.no_combat)return ["none"];
  const r=(mine.I||0)-(their.I||0);if(r>0)k.push("iU");if(r<0)k.push("iD");
  [["TH","s"],["TS","v"]].forEach(([f,p])=>{if(mine[f]>0)k.push(p+"U");if(mine[f]<0)k.push(p+"D");if(their[f]>0)k.push("f"+p+"U");if(their[f]<0)k.push("f"+p+"D");});return k;}
const motifChip=key=>{const m=TAC_MOTIF.find(x=>x[0]===key);return '<span class="tc-m" style="color:'+(m[2]>0?'var(--income)':m[2]<0?'var(--upkeep)':'var(--dim)')+'">'+esc(m[1])+'</span>';};
function tacCells(X,t,u){const c=TMX[X==="A"?t+"|"+u:u+"|"+t];return c?(X==="A"?c:[c[1],c[0]]):[null,null];}
function tacCardBody(X,t){const O=X==="A"?"B":"A",opp=BT.tactics.filter(u=>tacOK(O,u)),L=opp.map(u=>Object.assign({u},tacPair(X,t,u)||{})).filter(r=>r.cx);
  if(!L.length)return '<b>'+esc(t)+'</b>';
  // a motif shows when it comes up against about a third of the Tactics they could play; gain and lose of the same thing keep the larger
  const n={};opp.forEach(u=>cellMotifs(...tacCells(X,t,u)).forEach(k=>{n[k]=(n[k]||0)+1;}));const thr=Math.max(1,Math.round(opp.length/3)),on=k=>(n[k]||0)>=thr;
  [["iU","iD","iS"],["sU","sD"],["vU","vD"],["fsU","fsD"],["fvU","fvD"]].forEach(([u,d,s])=>{if(!on(u)||!on(d))return;
    if(n[u]>n[d])delete n[d];else if(n[d]>n[u])delete n[u];else{if(s)n[s]=n[u];delete n[u];delete n[d];}});
  const keys=TAC_MOTIF.map(m=>m[0]).filter(on).sort((a,b)=>{const g=k=>TAC_MOTIF.find(m=>m[0]===k)[2];return g(b)-g(a);});
  const fight=L.filter(r=>!r.ends&&!r.none),f1=v=>v.toFixed(1);
  let h='<b>'+esc(t)+'</b>'+((BT.tacticNotes||{})[t]?' <span class="note">'+esc(BT.tacticNotes[t])+'</span>':'')+'<div class="tc-l">'+keys.map(motifChip).join(' · ')+'</div>';
  if(!fight.length)return h;
  const best=fight.reduce((m,r)=>r.deal-r.take>m.deal-m.take?r:m),worst=fight.reduce((m,r)=>r.deal-r.take<m.deal-m.take?r:m);
  if(ADMIN){const avgD=fight.reduce((s,r)=>s+r.deal,0)/fight.length,avgT=fight.reduce((s,r)=>s+r.take,0)/fight.length,edge=avgD-avgT;
    h+='<div class="tc-l" style="color:'+(edge>0.05?'var(--income)':edge<-0.05?'var(--upkeep)':'var(--dim)')+'">≈ deal '+f1(avgD)+' · take '+f1(avgT)+'</div>';}
  return h+'<div class="tc-l note">best vs '+esc(best.u)+' · worst vs '+esc(worst.u)+'</div>';}
// the picked (or hovered-in) Tactic, against every Tactic they can play: where each number comes from
function tacDetailHTML(X,t){if(!t)return '<div class="note" style="margin-top:4px">Pick a card to see it against each Tactic they could play.</div>';
  const O=X==="A"?"B":"A",c0=sideCalc(X),opp=BT.tactics.filter(u=>tacOK(O,u)),f1=v=>v.toFixed(1),seen=(PICKS[O]||{}).tactic;
  // the number to roll after everything, coloured for you: green = better for you than the base, red = worse
  const col=g=>g>0?'var(--income)':g<0?'var(--upkeep)':'inherit';
  const dm=(L,eff,mine)=>'<td style="color:'+col((mine?1:-1)*(L[0][1]-Math.min(eff,(BT.faces||10)+1)))+'">'+tgtTxt(eff)+'</td>';
  const rows=opp.map(u=>{const r=tacPair(X,t,u);if(!r)return "";
    return '<tr'+(seen===u?' class="on"':'')+'><td>'+esc(u)+(seen===u?' <b>(their pick)</b>':'')+'</td><td>'+cellMotifs(...tacCells(X,t,u)).map(motifChip).join(' · ')+'</td>'+
      (r.ends||r.none?'<td colspan="'+(ADMIN?6:5)+'"></td>':
      '<td style="color:'+col(r.first==="you"?1:r.first==="they"?-1:0)+'">'+r.first+'</td>'+dm(r.cx.strikeParts,r.cx.toStrike,1)+dm(r.co.saveParts,r.co.save,0)+dm(r.co.strikeParts,r.co.toStrike,0)+dm(r.cx.saveParts,r.cx.save,1)+
      (ADMIN?'<td style="color:'+col(r.deal-r.take)+'">'+f1(r.deal)+' / '+f1(r.take)+'</td>':''))+'</tr>';}).join("");
  return '<div class="tc-detail"><div class="note"><b>'+esc(t)+'</b> with your '+esc(c0.rt&&c0.a.retinue||"")+' ×'+c0.front+' in front, '+esc(c0.wName)+', '+esc(c0.a.armor||"Cloth")+(c0.a.shield&&c0.a.shield!=="None"&&!c0.shOff?' + '+esc(c0.a.shield):'')+'</div>'+
    '<table class="dtable" style="font-size:11px;margin-top:4px"><thead><tr><th>If they play</th><th>What happens</th><th>First</th><th>Your Strike</th><th>Their Save</th><th>Their Strike</th><th>Your Save</th>'+(ADMIN?'<th>≈ deal / take</th>':'')+'</tr></thead><tbody>'+rows+'</tbody></table></div>';}
// the next roll for side X, in words: what is rolled, with which gear, the number needed and why, and what a 10 does
function rollGuideHTML(X){const B=battle(),fl=bFlow(),c=sideCalc(X);if(!c||!B.dice||!B.id)return "";const O=X==="A"?"B":"A",co=sideCalc(O),F=BT.faces||10,FOC=BT.focusedThr||10;
  // the same steps the buttons offer: a step the flow allows but this side can't take (no Dual Wield, Parry, Recover …) is skipped
  const can=fl?fl.can[X]:{},sv=(B.sv||{})[X],T=BT.panicThreshold||5,pn=(B[X].cas||0)+(c.enduring?0:(B[X].rcv||0)),
    has={strike:1,cleave:1,dual:0,parry:c.canParry,rip:ripN(X)>0,save:1,recover:c.recThr!=null&&sv&&sv.sk===B.sk&&(sv.n+recFx(sv))>0,panic:!c.immunePanic&&pn>=T,brk:1},
    k=["strike","cleave","dual","parry","rip","save","recover","panic","brk"].find(f=>can[f]&&has[f]);if(!k)return "";
  // parts are [label, change to the target]; on the dice that is the opposite sign (Tactic +1 to Strike = each die +1)
  const dmods=(L,eff)=>{const base=L[0][1],m=base-eff,ls=L.slice(1).filter(([,v])=>v).map(([n,v])=>esc(n)+' '+sgnD(-v)),cap=L.slice(1).filter(([,v])=>!v).map(([n])=>esc(n)),
      sum=-L.slice(1).reduce((a,[,v])=>a+v,0);return {base,m,txt:(ls.length?ls.join(' · '):'no modifiers')+(cap.length?' · '+cap.join(' · '):'')+(sum!==m&&!cap.length?' · limited to '+sgnD(m):'')};};
  const ic=incoming(X),inc=ic.n+ic.d;let h="";
  if(k==="cleave"){const sm=dmods(c.strikeParts,c.toStrike),fl=c.critFloor<FOC?c.critFloor+'+':'10';
    h='<b>Cleave</b> — roll '+cleaveN(X)+' Strike '+(cleaveN(X)===1?'die':'dice')+'. Each <b>'+sm.base+'+</b> (each die <b>'+sgnD(sm.m)+'</b>) is another hit'+(c.hasDeadly?' (Deadly on '+fl+')':'')+
      '; each '+fl+' also earns another Cleave die.';}
  else if(k==="strike"||k==="dual"){const tens=[];
    if(c.hasDeadly)tens.push('<b>Deadly</b> — their Save die for that hit gets '+sgnD(-(BT.deadlyAp??5)));
    if(c.hasCleave)tens.push('<b>Cleave</b> — roll another Strike die (and again on each Focused Cleave)');if(c.hasDestroy)tens.push('<b>Destroy Shield</b> — their shield is broken for the rest of the Battle');
    const ap=(c.wpn.ap||0);
    const sm=dmods(c.strikeParts,c.toStrike);
    h='<b>Strike</b> — roll '+(k==="dual"?((B.strk||{})[X]||{}).miss+' re-roll dice (Dual Wield)':c.front+' dice, one per '+esc(c.a.retinue||"Retinue")+' in your front line')+'. '+esc(c.a.retinue||"Your Retinue")+' hit on <b>'+sm.base+'+</b>, each die <b>'+sgnD(sm.m)+'</b>'+(c.toStrike>F?" — it can't hit":'')+'.'+
      '<div class="note">Modifiers: '+sm.txt+'.</div>'+
      '<div class="note">Your '+esc(c.wName)+': '+(ap?'AP '+sgnD(ap)+' — each of their Save dice '+sgnD(ap):'no AP')+(c.wpn.init?' · Initiative '+sgnD(c.wpn.init):'')+'.</div>'+
      '<div class="note">'+(c.critFloor<FOC?c.critFloor+'+':'10s')+' (Focused): '+(tens.length?tens.join('; '):'just a hit — your '+esc(c.wName)+' has no Focused effect')+'.</div>';}
  else if(k==="parry"||k==="rip"){h='<b>Parry</b> — roll one die per hit coming at you ('+(k==="rip"?ripN(X):inc)+'). Each <b>'+tgtTxt(c.parryThr)+'</b> turns a hit aside'+(ic.d?'; Deadly hits only on a 10':'')+'.'+
      (c.dualW?' Dual Wield: each failed Parry is re-rolled once; a re-rolled Parry can\'t Riposte.':'')+
      (c.riposte?'<div class="note">'+(c.ripP?(FOC-1)+'s and 10s':'10s')+': <b>Riposte</b> — you strike back once with your '+esc(c.a.weapon||"melee weapon")+'.</div>':'<div class="note">10s: just a Parry.</div>');}
  else if(k==="save"){const vm=dmods(c.saveParts,c.save);h='<b>Save</b> — roll one die per hit that got through ('+inc+'). Your '+esc(c.a.armor||"Cloth")+' saves on <b>'+vm.base+'+</b>, each die <b>'+sgnD(vm.m)+'</b>'+(c.save>F?" — it can't save":'')+'; every failed Save is a casualty.'+
      '<div class="note">Modifiers: '+vm.txt+'.'+(ic.d?' Deadly hits ('+ic.d+'): each die '+sgnD(vm.base-c.deadlySave)+'.':'')+'</div>'+
      '<div class="note">10s: '+(c.poisoned?'<b>fail</b> — their weapon is Poisoned':'just a Save')+'.</div>';}
  else if(k==="recover")h='<b>Recover</b> — each failed Save gets one more die: <b>'+tgtTxt(c.recThr)+'</b> and that '+esc(c.a.retinue||"Retinue")+' is back on its feet'+(c.enduring?'':' (it still counts toward Panic)')+'.';
  else h='<b>'+(k==="panic"?'Panic':'Break')+' check</b> — roll '+(BT.moraleDiceMax||5)+' dice; each below <b>'+c.morale+'</b> costs a '+esc(c.a.retinue||"Retinue")+'.'+
      (k==="panic"?'<div class="note">Rolled because this Skirmish\'s casualties reached '+(BT.panicThreshold||5)+'.</div>':'<div class="note">Rolled because Endurance hit 0.</div>');
  return '<div class="roll-guide"><span class="rg-k">next</span> '+h+'</div>';}
// ---- battle chronicle: BATTLE_NARRATION lines filled from what just happened (B.narr), read under the battlefield ----
const NARR=BT.narration||{};
function narrPl(r){const P=NARR.plural||{};return P[r]||(r?String(r).toLowerCase()+(/s$/i.test(r)?"":"s"):"troops");}
function narrDisp(n){return n&&window.dispName?dispName(n):(n||"");}
function narrate(key,X,vals){const L=NARR[key];if(!L||!L.length)return;const B=battle(),O=X==="A"?"B":"A",c=sideCalc(X)||{},co=sideCalc(O)||{},a=c.a||{},ea=co.a||{};
  const v=Object.assign({side:sideNm(X),foe:sideNm(O),troops:narrPl(a.retinue),foe_troops:narrPl(ea.retinue),weapon:narrDisp(c.wName),armor:narrDisp(a.armor),
    foe_weapon:narrDisp(co.wName),foe_armor:narrDisp(ea.armor),sk:B.sk},vals||{});
  const t=L[((B.narr||[]).length*7+key.length)%L.length].replace(/\{(\w+)\}/g,(m,k)=>v[k]!=null?String(v[k]):m);
  B.narr=(B.narr||[]).concat([{sk:B.sk,X,t}]).slice(-150);}
// after a roll: remember its base (the number to roll before modifiers) and tell it
function rollMeta(X,c){const B=battle(),R=(B.rolls||{})[X];if(!R||R.base!=null)return;
  R.base=R.kind==="Strike"?c.strikeParts[0][1]:R.kind==="Save"?c.saveParts[0][1]:R.kind==="Parry"?(BT.parryBase||8):R.target;
  const n=R.dice.length+(R.dl?R.dl.dice.length:0),succ=R.succ+(R.dl?R.dl.succ:0),
    need=R.target>(BT.faces||10)?"the impossible":R.base+"+",mod=R.base===R.target?"no modifier":sgnD(R.base-R.target)+" each";
  if(R.kind==="Strike"&&R.cleave)return;
  if(R.kind==="Strike"){const q=n?succ/n:0;narrate(!succ?"strike_none":q>=0.6?"strike_high":q>=0.35?"strike_mid":"strike_low",X,{n,hits:succ,need,mod});
    const f=[c.hasDeadly&&"Deadly",c.hasCleave&&"Cleave",c.hasDestroy&&"Destroy Shield"].filter(Boolean);if(R.nat10&&f.length)narrate("strike_tens",X,{tens:R.nat10,focus:f.join(", ")});}
  else if(R.kind==="Parry"){narrate(c.canParry?"parry":"parry_none",X,{n,saved:succ});if(R.nat10&&c.riposte)narrate("riposte",X,{tens:R.nat10});}
  else if(R.kind==="Save")narrate(R.cas===0?"save_none":succ>=R.cas?"save_good":"save_bad",X,{n,saved:succ,lost:R.cas});
  else if(R.kind==="Recover")narrate("recover",X,{saved:succ});
  else if(R.kind==="Break")narrate("break",X,{lost:R.cas});
  else narrate(n-succ?"panic_lose":"panic_hold",X,{lost:n-succ});}
function chronicleHTML(){const B=battle(),L=B.narr||[];if(!L.length)return "";let sk=null;
  return '<details class="bchron" open><summary><b>Chronicle</b> <span class="note">'+L.length+' lines</span></summary><div class="bchron-b">'+
    L.map(x=>(x.sk!==sk?'<div class="bchron-sk">Skirmish '+(sk=x.sk)+'</div>':'')+'<p style="--pc:'+(((sideArmy(B[x.X])||{}).p||{}).color||"#888")+'">'+esc(x.t)+'</p>').join("")+'</div></details>';}
function sideHTML(X){
  const B=battle(),sd=B[X],c=sideCalc(X),v=viewerSide(),mine=v===X,O=X==="A"?"B":"A";
  let h='<div class="tot bside" data-side="'+X+'"><h3 style="font-size:14px">Side '+X+(X==="A"?" (attacker)":"")+'</h3>'+
    '<div style="display:flex;gap:6px;flex-wrap:wrap;margin:6px 0"><select class="bsel" data-x="'+X+'" data-f="pid"><option value="">player…</option>'+
    D.players.map(p=>'<option value="'+p.id+'"'+(sd.kind!=="bandit"&&String(p.id)===String(sd.pid)?' selected':'')+'>'+esc(p.name)+'</option>').join('')+
    Object.keys(mapState().camps).map(k=>{const cp=mapState().camps[k];return '<option value="bandit:'+k+'"'+(sd.kind==="bandit"&&sd.camp===k?' selected':'')+'>☠ Bandit '+(cp.n>=(BAN.armyThreshold||25)?'Army':'Camp')+' @ '+k+' ('+cp.n+')</option>';}).join('')+'</select>';
  if(sd.kind==="bandit"){const {a}=sideArmy(sd),era=a?banditEra(a):currentEra(),lo=banLO()[era]||{};
    h+=a?'<select class="bera" data-x="'+X+'">'+Object.keys(ERAS).map(e=>'<option value="'+esc(e)+'"'+(era===e?' selected':'')+'>'+esc(e)+(e===currentEra()?' (current)':'')+'</option>').join('')+'</select></div>'+
      '<div class="note">Armed for '+esc(era)+': '+esc((banEquip()[era])||'—')+' → '+esc([a.retinue,a.weapon,a.armor,a.shield].filter(x=>x&&x!=="None").join(', '))+
      ((lo.unmatched||[]).length?' <span style="color:var(--upkeep)">· not found in equipment data: '+esc(lo.unmatched.join(', '))+'</span>':'')+'</div>':'<div class="note">camp removed from map</div>';
    if(!c)return h+'</div>';}
  const pl=sd.kind==="bandit"?null:D.players.find(p=>String(p.id)===String(sd.pid));
  if(sd.kind!=="bandit")h+='<select class="bsel" data-x="'+X+'" data-f="aid"><option value="">army…</option>'+(pl?(pl.board.armies||[]).map(a=>'<option value="'+a.id+'"'+(String(a.id)===String(sd.aid)?' selected':'')+'>'+esc(a.label||("Army "+a.id))+' — '+esc(a.retinue||"")+' ×'+(a.count||0)+'</option>').join('')+
      garrisonsOf(pl).map(g=>'<option value="g:'+g.sid+'"'+(String(sd.aid)==="g:"+g.sid?' selected':'')+'>'+esc(g.label)+' — '+esc(g.retinue||"")+' ×'+(g.count||0)+'</option>').join(''):'')+'</select></div>';
  if(!c)return h+battleSprites(sd,pl)+'<div class="note">Pick a player and one of their armies.</div></div>';
  const a=c.a;
  h+=datasheetHTML(X,c,pl);
  return h+'</div>';
}
// an army's name for the Battle view: its label, else its player's name; Bandits; else Side A / B
// Fortified Church: the side is its owner's Garrison and the owner has "Garrisons gain Immune Fatigue"
function fatigueImmune(X){const sa=sideArmy(battle()[X]||{});return !!(sa.garrison&&sa.p&&srcHas(sa.p.board,"immune_fatigue_garrison"));}
// a side whose Endurance reaches 0 at the end of this Skirmish (Fatigued: Break check, then a Fatigue token)
function fatiguesNow(X){const B=battle(),c=sideCalc(X);if(!B.id||!c||fatigueImmune(X))return false;const cell=B.rev&&B.rev.sk===B.sk?TMX[B.rev.A+"|"+B.rev.B]:null,
  tm=cell?cell[X==="A"?0:1]:null;return Math.max(0,(c.a.endurance||0)-((!tm||tm.endurance_loss!==false)?1:0))===0;}
function sideNm(X){const B=battle(),sd=B[X]||{};if(sd.kind==="bandit")return "Bandits";const sa=sideArmy(sd),a=sa.a;return (a&&a.label)||(sa.p&&sa.p.name)||("Side "+X);}
// Skirmish flow (rules: Initiative, Strike, Defend, Panic check) while dice are emulated: what each side may roll now.
// The higher Initiative Strikes first; the defender Parries (if able), Saves, Recovers (if able); the Striker answers any Riposte;
// casualties leave the field before the other side Strikes back. On a tie both Strike and casualties wait until both have fought.
// The Panic check comes once both sides have fought. The Duke can roll out of order.
function bFlow(){const B=battle(),sk=B.sk,C={A:sideCalc("A"),B:sideCalc("B")};
  if(!B.id||!B.dice||!C.A||!C.B||!(B.rev&&B.rev.sk===sk))return null;
  const O=X=>X==="A"?"B":"A",cell=TMX[B.rev.A+"|"+B.rev.B]||[{},{}],nc=!!(cell[0].no_combat||cell[1].no_combat);
  const on=(o,X)=>!!(o&&o[X]&&o[X].sk===sk),struck=X=>on(B.strk,X)&&!cleaveN(X),parried=X=>on(B.par,X),saved=X=>(B.svd||{})[X]===sk,pend=X=>pendCas(X);
  const able=X=>(C[X].a.count||0)>0&&C[X].front>0,inc=X=>{const i=incoming(X);return i.n+i.d;};
  const recDue=X=>{const sv=(B.sv||{})[X];return !!sv&&sv.sk===sk&&C[X].recThr!=null&&(sv.n+recFx(sv))>0;};
  const defDone=X=>struck(O(X))&&(saved(X)||inc(X)===0)&&!recDue(X)&&!ripN(O(X));        // X's defence against the other side's Strike
  const tie=C.A.I===C.B.I,first=tie?null:(C.A.I>C.B.I?"A":"B"),second=first&&O(first);
  const done1=X=>!able(X)||(struck(X)&&defDone(O(X)));                                     // X has fought (or can't)
  const fought=nc||(done1("A")&&done1("B")&&(tie||(!pend("A")&&!pend("B"))));
  const T=BT.panicThreshold||5,pn=X=>{const sd=B[X];return (sd.cas||0)+(C[X].enduring?0:(sd.rcv||0));};
  const panicDue=X=>able(X)&&!C[X].immunePanic&&pn(X)>=T&&(B.pnk||{})[X]!==sk;
  const can={A:{},B:{}};
  ["A","B"].forEach(X=>{const o=O(X),k=can[X];
    k.strike=!nc&&!on(B.strk,X)&&able(X)&&(tie||X===first||(struck(first)&&defDone(X)&&!pend(X)&&!pend(first)));
    k.cleave=cleaveN(X)>0;k.dual=struck(X)&&!parried(o)&&!saved(o);
    k.parry=struck(o)&&C[X].canParry&&!parried(X)&&!saved(X)&&inc(X)>0;
    k.save=struck(o)&&!saved(X)&&inc(X)>0&&(!C[X].canParry||parried(X));
    k.recover=recDue(X);k.rip=ripN(X)>0;
    k.apply=pend(X)>0&&!k.rip&&!k.parry&&!k.save&&!k.recover&&(!tie||(done1("A")&&done1("B")));
    k.panic=fought&&panicDue(X);k.panicLater=!fought&&!C[X].immunePanic&&pn(X)>T;});
  const P=["A","B"].filter(panicDue),brkDue=X=>able(X)&&fatiguesNow(X)&&(B.brk||{})[X]?.sk!==sk;
  ["A","B"].forEach(X=>{can[X].brk=fought&&!P.length&&!pend("A")&&!pend("B")&&brkDue(X);});
  const BR=["A","B"].filter(X=>can[X].brk),done=fought&&!P.length&&!pend("A")&&!pend("B")&&!BR.length;
  // what is due next, in words
  const nm=X=>'<b>'+esc(sideNm(X))+'</b>';let msg="";
  if(nc)msg="No combat this Skirmish";
  else{const ord=tie?["A","B"]:[first,second];
    for(const X of ord){const k=can[X],ko=can[O(X)];
      if(k.strike){msg=nm(X)+(tie?" and "+nm(O(X))+" Strike":X===first?" Strikes first":" Strikes back");break;}
      if(k.cleave){msg=nm(X)+" rolls Cleave";break;}
      if(ko.parry||ko.save||ko.recover){msg=nm(O(X))+" defends: "+(ko.parry?"Parry":ko.save?"Save":"Recover");break;}
      if(k.rip){msg=nm(X)+" answers the Riposte";break;}
      if(can.A.apply||can.B.apply){msg="Apply casualties: "+["A","B"].filter(Y=>can[Y].apply).map(nm).join(", ");break;}}
    if(!msg&&P.length)msg="Panic check: "+P.map(nm).join(", ");
    if(!msg&&BR.length)msg="Break check (Endurance 0): "+BR.map(nm).join(", ");
    if(!msg&&(can.A.apply||can.B.apply))msg="Apply casualties: "+["A","B"].filter(Y=>can[Y].apply).map(nm).join(", ");}
  if(!msg&&done)msg="Skirmish resolved";
  return {can,done,fought,nc,tie,first,msg};}
// roll / casualty buttons for one side, in the command bar above the field once both Tactics are revealed
function actionsHTML(X){
  const B=battle(),sd=B[X],c=sideCalc(X),O=X==="A"?"B":"A";if(!c)return "";const a=c.a,fl=bFlow(),k=fl&&!ADMIN?fl.can[X]:null;
  const g=(f,req)=>(k&&!k[f]?' disabled':'')+'',cls=f=>'broll'+(fl&&fl.can[X][f]?' go':'');
  let h='<div class="btac-side" data-side="'+X+'"><div class="btac-h"><b>'+esc(sideNm(X))+'</b></div>';
  if(B.dice&&B.id){
    const ic=incoming(X),inc=ic.n+ic.d,T=BT.panicThreshold||5,pn=(sd.cas||0)+(c.enduring?0:(sd.rcv||0));
    h+='<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:8px">'+
      '<button class="'+cls("strike")+'" data-x="'+X+'" data-k="Strike"'+g("strike")+'>Strike ×'+c.front+'</button>'+
      (cleaveN(X)?'<button class="'+cls("cleave")+'" data-x="'+X+'" data-k="Cleave"'+g("cleave")+'>Cleave ×'+cleaveN(X)+'</button>':'')+
      
      (c.canParry?'<button class="'+cls("parry")+'" data-x="'+X+'" data-k="Parry"'+g("parry")+'>Parry ×'+inc+'</button>':'')+
      '<button class="'+cls("save")+'" data-x="'+X+'" data-k="Save"'+g("save")+'>Save ×'+inc+(ic.d?' ('+ic.d+' Deadly)':'')+'</button>'+
      (ripN(X)?(c.canParry?'<button class="'+cls("rip")+'" data-x="'+X+'" data-k="RipParry">Parry Riposte ×'+ripN(X)+'</button>':'')+'<button class="'+cls("rip")+'" data-x="'+X+'" data-k="RipSave">Save vs Riposte ×'+ripN(X)+'</button>':'')+
      ((sv=>{const fx=sv?recFx(sv):0;return sv&&sv.sk===B.sk&&(sv.n+fx)&&c.recThr!=null?'<button class="'+cls("recover")+'" data-x="'+X+'" data-k="Recover">Recover ×'+(sv.n+fx)+(fx?' ('+fx+' on '+(BT.focusedThr||10)+' only)':'')+'</button>':'';})((B.sv||{})[X]))+
      (!c.immunePanic&&pn>=T?'<button class="'+cls("panic")+'" data-x="'+X+'" data-k="Morale"'+g("panic")+'>Panic check ×'+(BT.moraleDiceMax||5)+'</button>':'')+
      (fatiguesNow(X)&&!((B.brk||{})[X]&&B.brk[X].sk===B.sk)?'<button class="'+cls("brk")+'" data-x="'+X+'" data-k="Break"'+g("brk")+'>Break check ×'+(BT.moraleDiceMax||5)+'</button>':'')+
      '<input type="number" min="0" value="'+inc+'" class="bn" data-x="'+X+'" style="width:52px" title="dice count override for Parry/Save">'+
      '</div>'+((g_,r_)=>g_||r_?'<details class="bdice"><summary class="note">dice detail</summary>'+g_+r_+'</details>':'')(rollGuideHTML(X),rollHTML(X));   // the Skirmish log above reads easier; the dice stay one click away
  }
  h+='<div style="display:flex;gap:4px;align-items:center;margin-top:6px"><span class="note">casualties</span><input type="number" min="0" value="'+pendCas(X)+'" class="bcas" data-x="'+X+'" style="width:52px"><button class="bcasgo'+(fl&&fl.can[X].apply?' go':'')+'" data-x="'+X+'"'+(k&&!k.apply?' disabled':'')+'>apply</button>'+
    (()=>{const cc=sideCalc(X)||{},rc=cc.enduring?0:(sd.rcv||0),pn=(sd.cas||0)+rc,imP=!!cc.immunePanic;   // Enduring: Recovered Strikes don't count
      return '<span class="note">this Skirmish: '+(sd.cas||0)+(sd.rcv?(cc.enduring?' ('+sd.rcv+' Recovered — Enduring, not counted)':' + '+sd.rcv+' Recovered = '+pn)+' for Panic':'')+(imP?' · Immune Panic':'')+((!imP&&BT.panicThreshold&&pn>BT.panicThreshold)?' — <b style="color:var(--upkeep)">Panic check after both sides Strike</b>':'')+'</span>';})()+'</div>';
  // Endurance reaching 0 this Skirmish → Break check (rolled after the Panic checks) + Fatigue token at End Skirmish
  if(B.id&&fatiguesNow(X)){const e=a.endurance||0,bd=(B.brk||{})[X],rolled=bd&&bd.sk===B.sk;
    h+='<div class="note" style="margin-top:6px;padding:6px;border:1px solid var(--upkeep);border-radius:var(--radius)"><b style="color:var(--upkeep)">Fatigued at end of Skirmish</b> — Endurance '+e+' → 0. '+
      (rolled?'Break check: '+bd.lost+' casualties ('+bd.n+'d10 vs '+bd.target+'+)':'Break check: '+(BT.moraleDiceMax||5)+'d10 vs '+c.morale+'+, failures are casualties ('+(B.dice?'roll it after the Panic checks':'roll it after end Skirmish')+')')+'. Then +1 Fatigue token.</div>';}
  return h+'</div>';
}
// the Battle's result once a Skirmish has ended it (rules: End the Skirmish): wiped out or Routed loses; both = no winner;
// a Fall Back ends it without naming a winner. Waits for any Break check still to roll.
// what both sides still owe before a Battle can end and name a winner: casualties to apply, Panic checks, Break checks
function battleOwed(){const B=battle();if(!B.id)return "";const L=[];
  ["A","B"].forEach(X=>{if(pendCas(X)>0)L.push(sideNm(X)+": apply casualties");});
  panicOwed().forEach(X=>L.push(sideNm(X)+": Panic check"));
  {const fl=bFlow();if(fl)["A","B"].forEach(X=>{if(fl.can[X].brk)L.push(sideNm(X)+": Break check");});}
  if(B.endRep&&B.endRep.sk===B.sk)B.endRep.rows.forEach(r=>{if(r.brk&&r.brk.pending)L.push(sideNm(r.X)+": Break check");});
  return [...new Set(L)].join(", ");}
function battleOutcome(){const B=battle(),R=B.endRep&&B.endRep.sk===B.sk?B.endRep:null;if(!B.id||!R||R.rows.some(r=>r.brk&&r.brk.pending))return null;
  const lost={},why={};
  ["A","B"].forEach(X=>{const r=R.rows.find(x=>x.X===X),c=sideCalc(X),n=c?(c.a.count||0):0;
    if(n<=0||(r&&r.wiped)){lost[X]=1;why[X]="is wiped out";}else if(r&&r.rout){lost[X]=1;why[X]="Routs";}});
  if(lost.A&&lost.B)return {win:"",why};if(lost.A)return {win:"B",why};if(lost.B)return {win:"A",why};
  const fb=R.rows.filter(r=>r.fb&&r.tac==="Fall Back").map(r=>r.X);
  return fb.length?{win:null,fb,why}:null;}
function resultHTML(oc){const B=battle(),nm=X=>esc(sideNm(X));let h='<div class="bcmd bresult">';
  const pl=X=>B[X].kind==="bandit",reasons=["A","B"].filter(X=>oc.why[X]).map(X=>nm(X)+' '+(pl(X)?{"Routs":"Rout","is wiped out":"are wiped out"}[oc.why[X]]:oc.why[X]));
  if(oc.win===null){
    h+='<div class="bcmd-t">'+oc.fb.map(nm).join(" and ")+' Fall'+(oc.fb.length>1?'':'s')+' Back: the Battle ends</div>'+
      '<div class="note">The rules don\'t name a winner for a Fall Back.</div><div class="bcmd-row">'+
      '<button class="bFinish" data-w="A">'+nm("A")+' won</button><button class="bFinish" data-w="B">'+nm("B")+' won</button><button class="bFinish" data-w="">No winner</button></div>';}
  else{
    h+='<div class="bcmd-t">'+(oc.win?nm(oc.win)+' wins the Battle':'No winner')+'</div><div>'+reasons.join(' · ')+'</div>';
    if(oc.win){const L=oc.win==="A"?"B":"A",lc=sideCalc(L),cost=+((lc&&lc.rt&&lc.rt.cost)||0);
      if(B[L].kind!=="bandit")h+='<div>Spoils of War: '+nm(oc.win)+' Extorts up to '+cost.toLocaleString()+' ('+esc((lc&&lc.a.retinue)||"")+' cost)</div>';
      else{const M=mapState(),cp=M.camps[B[L].camp]||{},home=cp.home&&M.camps[cp.home]&&M.camps[cp.home].out===cp.uid?M.camps[cp.home]:null,
          gold=(+cp.gold||0)+(home?(+home.gold||0):0);
        h+='<div>The Bandits are destroyed: '+nm(oc.win)+' Extorts their whole Treasury ('+gold.toLocaleString()+', Spoils of War included)'+(home?', and their camp @ '+esc(cp.home)+' goes with them':'')+'</div>';}}
    ["A","B"].forEach(X=>{if(oc.why[X]&&B[X].kind!=="bandit"&&!String(B[X].aid||"").startsWith("g:"))h+='<div>'+nm(X)+(oc.why[X]==="Routs"?' is destroyed and':'')+' leaves the map</div>';});
    h+='<div class="note">Fatigue tokens are removed.</div><button class="bFinish go" data-w="'+(oc.win||"")+'">Finish battle</button>';}
  return h+'</div>';}
// before the Battle: who Seizes the Initiative; Start lights up once that is set
// the terrain under a side's own army: a Hill (+1 Initiative every Skirmish), any grassland = Open Field (Ranged +1 to Strike)
function sideTile(X){const B=battle(),g=mapState().grid,k=sideHex(B[X]);if(!g||!k)return null;return decodeGrid(g).hex[k]||null;}
function onHill(X){const h=sideTile(X);return !!(h&&h.hill);}
function onGrass(X){const h=sideTile(X);return !!(h&&h.t==="plains");}
// who Seizes unless the players choose otherwise: the Ministry always; in a Forest the defender (side B)
function seizeDefault(){const f=seizeForced();if(f)return f;const T=bfTerrain();return T&&T.tile==="Forest"?"B":null;}
function seizeHTML(){const B=battle();if(!sideCalc("A")||!sideCalc("B"))return '<div class="bcmd"><div class="bcmd-t">Pick both armies</div></div>';
  const f=seizeForced(),cur=f||(B.seizeSet?(B.seize||""):seizeDefault()),T=bfTerrain(),TT=T&&(TREF.tactical||{})[T.tile],tr=TT&&/Seize/i.test(TT.effect||"")?T.tile+": "+TT.effect:"",
        hl=["A","B"].filter(onHill).map(X=>sideNm(X)+" is on a Hill: +1 Initiative every Skirmish");
  const btn=(v,l)=>'<button class="bseize'+(cur===v?' on':'')+'" data-v="'+v+'"'+(f?' disabled':'')+'>'+esc(l)+'</button>';
  return '<div class="bcmd bseizebox"><div class="bcmd-t">Seize the Initiative</div><div class="bcmd-row">'+btn("A",sideNm("A"))+btn("B",sideNm("B"))+btn("","Neither")+'</div>'+
    (f?'<div class="note">'+esc(sideNm(f))+' Seizes (Ministry), whatever the terrain</div>':'')+(tr&&!f?'<div class="note">'+esc(tr)+'</div>':'')+hl.map(t=>'<div class="note">'+esc(t)+'</div>').join('')+
    '<button id="bStartGo" class="bstart'+(cur!=null?' go':'')+'"'+(cur!=null?'':' disabled')+'>Start battle</button></div>';}
function bCmdHTML(){const B=battle();if(!B.id)return seizeHTML();
  const oc=battleOutcome();if(oc)return resultHTML(oc);
  if(!(B.rev&&B.rev.sk===B.sk))return '<div class="btacs">'+tacticPickHTML("A")+tacticPickHTML("B")+'</div>';
  const fl=bFlow();
  return (fl?'<div class="bflow"><span>'+fl.msg+'</span><button class="bEndSk2'+(fl.done?' go':'')+'">End Skirmish ▸</button></div>':'')+
    '<div class="btacs">'+actionsHTML("A")+actionsHTML("B")+'</div>';}
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
function renderBattle(){WHATIF.clear();
  const host=document.getElementById("viewBattle"),B=battle();
  const Q=bq();
  let h='<div class="bm-card"><div class="bm-h"><h2>Battle</h2><button data-do="battleclose" data-nav="1" title="back to the Realm">✕</button></div>'+
    (Q.length?'<div class="tot bqlist"><div class="lbl">BATTLES TO RESOLVE · '+Q.length+'</div>'+Q.map(o=>'<div class="bqrow'+(B.qid===o.id?' on':'')+'">'+stIcon(o.kind==="sally"?"besieged":o.kind==="siege"?"sieging":"battle",16)+
      '<span><b>A</b> '+esc(bqSideName(o.A))+' <span class="note">vs</span> <b>B</b> '+esc(bqSideName(o.B))+'</span><span class="note">'+esc(o.src||"")+(o.seize?' · Seize: '+o.seize:'')+' · turn '+o.turn+'</span>'+
      (B.qid===o.id?'<span class="badge earn">loaded</span>':'<button data-bq-load="'+o.id+'">load</button>')+'<button class="rm" data-bq-del="'+o.id+'" title="remove">✕</button></div>').join("")+'</div>':'')+
    '<div class="toolbar">'+(B.id?'<button id="bStart">restart battle</button>':'')+
    '<span class="note">Skirmish <b>'+(B.id?B.sk:'—')+'</b></span>'+
    (B.id?'<span class="note">Seized: <b>'+esc((s=>s?sideNm(s):"neither")(seizeForced()||B.seize))+'</b></span>':'')+
    '<label class="note"><input type="checkbox" id="bDice"'+(B.dice?' checked':'')+'> emulate dice</label>'+
    (B.id?'<button id="bReset">reset picks</button><button id="bEndSk" style="border-color:var(--order)">end Skirmish ▸</button><span class="note">end Battle:</span><button class="bEndB" data-w="A" style="border-color:var(--upkeep)">'+esc(sideNm("A"))+' won</button><button class="bEndB" data-w="B" style="border-color:var(--upkeep)">'+esc(sideNm("B"))+' won</button><button class="bEndB" data-w="" style="border-color:var(--upkeep)">no winner</button>':'')+'</div>';
  const v=viewerSide();
  h+='<div class="note" style="margin-bottom:6px">Viewing as <b>'+esc((D.players[D.active]||{}).name||"?")+'</b>'+(v==="-"?' (spectator — switch player in the top bar to pick)':' = side '+v)+(API.online?'':' · no server: picks stay on this device (pass-and-play)')+'</div>';
  if(B.id)h+=battleGlanceHTML();
  if(B.id&&B.endRep&&B.endRep.sk===B.sk&&B.endRep.rows.length)
    h+='<div class="tot" style="border-color:var(--order)"><b>End of Skirmish '+(B.sk-1)+'</b>'+B.endRep.rows.map(r=>'<div class="note" style="margin-top:4px"><b>'+r.X+'</b> Endurance '+r.e0+' → '+r.e1+
      (r.brk?' · <b style="color:var(--upkeep)">Fatigued</b> · Break check '+r.brk.n+'d10 vs '+r.brk.target+'+: '+(r.brk.dice?dieRow(r.brk.dice,r.brk.target)+' → <b>'+r.brk.lost+'</b> casualties':'<button class="bBrk" data-x="'+r.X+'" style="border-color:var(--upkeep)">roll Break check</button>')+
        ' · Fatigue token '+r.fat+' → Morale '+r.m1+'+':'')+(r.rout?' · <b style="color:var(--upkeep)">ROUTS</b>':'')+(r.wiped?' · <b>wiped out</b>':'')+'</div>').join('')+'</div>';
  const cA=sideCalc("A"),cB=sideCalc("B");
  if(cA&&cB&&!B.id)h+='<div class="note" style="margin-bottom:6px">'+(cA.I===cB.I?'<b>Simultaneous</b> — both sides Strike with their full front line':'Strikes first: <b>'+(cA.I>cB.I?"A":"B")+'</b>')+' (I '+cA.I+' vs '+cB.I+')</div>';
  const vs=viewerSide(),bs=BSIDE||(vs==="A"||vs==="B"?vs:"A");
  h+='<div class="bside-nav"><button data-bs="A"'+(bs==="A"?' class="on"':'')+'>Side A</button><button data-bs="B"'+(bs==="B"?' class="on"':'')+'>Side B</button><button data-bs="AB"'+(bs==="AB"?' class="on"':'')+'>Both</button></div>';
  h+='<div class="bsides bgrid" data-bs="'+bs+'">'+sideHTML("A")+'<div class="bfield-col">'+bCmdHTML()+'<div id="bfield"></div>'+chronicleHTML()+'</div>'+sideHTML("B")+'</div>';
  h+='<div class="tot"><h3 style="font-size:13px">Log</h3><div class="note">'+(B.log||[]).map(esc).join('<br>')+'</div></div>';
  h+=tacticExplainHTML().replace('id="tacEx" open','id="tacExB"')+siegeHTML()+'<div class="note" style="margin:8px 0">Skirmish rules are in <a href="#" data-goto="reference#refBattle">Reference ▸</a></div></div>';
  host.innerHTML=h;bfMount(host);wireBattle(host);wireDashExtras(host);
}
// ---- Battle at a glance: the Skirmish as pictures — the two Tactics face off, who Strikes first, each side's troops (front /
// reserve / camp / fallen), Morale and Endurance, and every roll of this Skirmish as a row of dice (lit = success) with its outcome
function battleGlanceHTML(){const B=battle(),cA=sideCalc("A"),cB=sideCalc("B");if(!cA||!cB)return "";const rev=B.rev&&B.rev.sk===B.sk?B.rev:null,cell=rev?TMX[rev.A+"|"+rev.B]:null;
  const col=X=>{const sd=B[X],p=sd&&sd.pid!=null?pById(sd.pid):null;return (p&&p.color)||(X==="A"?"#4a8ad8":"#c8302a");};
  const pk=X=>{const P=(PICKS||{})[X]||{};return rev?'<span class="gl-tac">'+esc(rev[X])+'</span>':P.picked?'<span class="gl-tac wait">🔒 locked</span>':'<span class="gl-tac wait">choosing…</span>';};
  const md=(m)=>{if(!m)return "";const L=[];if(m.I)L.push((m.I>0?"+":"")+m.I+" Init");if(m.TH)L.push((m.TH>0?"+":"")+m.TH+" to Strike");if(m.TS)L.push((m.TS>0?"+":"")+m.TS+" to Save");if(m.strain)L.push("Strained");if(m.end)L.push("ends the Battle");if(m.no_combat)L.push("no combat");return L.join(" · ");};
  const troops=(X,c)=>{const a=c.a,st=+((B.start||{})[X]||0)||(+a.count||0),fallen=Math.max(0,st-(+a.count||0)),tot=Math.max(1,st),f=+c.front||0,r=+c.reserve||0,cp=Math.max(0,(+a.count||0)-f-r);
    const seg=(n,cls,t)=>n>0?'<i class="'+cls+'" style="flex:'+n+'" title="'+t+' '+n+'"></i>':'';
    return '<div class="gl-bar">'+seg(f,"f","front")+seg(r,"r","reserve")+seg(cp,"c","camp")+seg(fallen,"x","fallen")+'</div><div class="gl-cnt"><span>⚔ front '+f+'</span><span>reserve '+r+'</span><span>camp '+cp+'</span>'+(fallen?'<span class="neg">✝ '+fallen+' fallen</span>':'')+'</div>';};
  const sk=(X,c)=>{const sd=B[X]||{},cas=(+sd.cas||0),pt=+BT.panicThreshold||5,e=+(c.a.endurance||0),e0=+((EQ.retinues[c.a.retinue]||{}).endurance)||Math.max(e,3);
    return '<div class="gl-stats"><span title="Morale: roll this or higher; Routs at '+(BT.routThr||11)+'+">❤ Morale <b>'+c.morale+'+</b></span>'+
      '<span title="Endurance (0 = Fatigued at the end of the Skirmish)">⧗ '+"■".repeat(Math.min(e,8))+'<span class="dim">'+"□".repeat(Math.max(0,Math.min(e0,8)-e))+'</span></span>'+
      '<span title="casualties this Skirmish; '+pt+' or more = Panic check" class="'+(cas>=pt?'neg':'')+'">☠ '+cas+'/'+pt+(cas>=pt?' Panic!':'')+'</span>'+(c.a.fatigue?'<span class="neg">Fatigue '+c.a.fatigue+'</span>':'')+'</div>';};
  const side=X=>{const c=X==="A"?cA:cB;return '<div class="gl-side" style="--sc:'+col(X)+'"><div class="gl-nm"><b>'+esc(sideNm(X))+'</b> '+pk(X)+'</div>'+(cell?'<div class="gl-md note">'+esc(md(X==="A"?cell[0]:cell[1]))+'</div>':'')+troops(X,c)+sk(X,c)+'</div>';};
  const first=cA.I===cB.I?'<div class="gl-first">⇆ <b>Simultaneous</b><span class="note">Init '+cA.I+' = '+cB.I+'</span></div>':
    '<div class="gl-first">'+(cA.I>cB.I?'<b>'+esc(sideNm("A"))+'</b> ⇒':'⇐ <b>'+esc(sideNm("B"))+'</b>')+'<span class="note">strikes first · Init '+cA.I+' vs '+cB.I+'</span></div>';
  // the exchange: each roll as dice (lit = success), with what it did
  const EV=B.gl&&B.gl.sk===B.sk?B.gl.ev:[],PV=B.gl&&B.gl.sk<B.sk&&B.gl.ev.length?B.gl:(B.glPrev&&B.glPrev.sk<B.sk?B.glPrev:null);
  const dice=e=>(e.dice||[]).map(v=>{const ok=e.kind==="Morale"||e.kind==="Break"?v>=e.target:v>=e.target;return '<i class="gl-d'+(ok?' ok':'')+(v>=(BT.focusedThr||10)&&/Strike/.test(e.kind)?' crit':'')+'" title="'+v+'">'+v+'</i>';}).join("");
  const res=e=>{const k=e.kind;if(k==="Fall")return '<b class="neg">✝ '+e.n+' fall</b>';
    if(/Strike/.test(k))return '<b>'+(e.succ||0)+' hit'+(e.succ===1?'':'s')+'</b>'+(e.cleave?' <span class="note">(Cleave)</span>':'');
    if(k==="Parry")return '<b>'+(e.succ||0)+' parried</b>';if(k==="Save")return '<b>'+(e.succ||0)+' saved</b>'+(e.cas!=null?' · <span class="neg">'+e.cas+' unsaved</span>':'');
    if(k==="Recover")return '<b>'+(e.succ||0)+' recovered</b>';if(k==="Morale"||k==="Panic")return '<b>Panic</b> · <span class="neg">'+((e.dice||[]).length-(e.succ||0))+' flee</span>';
    if(k==="Break")return '<b>Break</b> · <span class="neg">'+(e.cas||0)+' lost</span>';return '<b>'+(e.succ||0)+'</b>';};
  const verb=k=>({Strike:"Strike",Save:"Save",Parry:"Parry",Recover:"Recover",Morale:"Panic check",Break:"Break check",Fall:"Casualties"}[k]||k);
  const rows=L=>L.map(e=>'<div class="gl-row" style="--sc:'+col(e.X)+'"><span class="gl-who">'+esc(sideNm(e.X))+'</span><span class="gl-k">'+verb(e.kind)+(e.target&&e.target<99&&e.kind!=="Fall"?' <span class="note">'+e.target+'+</span>':e.target>=99?' <span class="note">can\'t</span>':'')+'</span><span class="gl-dice">'+dice(e)+'</span><span class="gl-res">'+res(e)+'</span></div>').join("");
  const ex=(EV.length?'<div class="gl-ex">'+rows(EV)+'</div>':
    '<div class="note gl-wait">'+(rev?'Roll Strikes below — each roll shows up here as dice.':'Both sides pick a Tactic; they are revealed together.')+'</div>')+
    (PV?'<details class="gl-prev"><summary class="note">Skirmish '+PV.sk+' — how it went ('+PV.ev.filter(e=>e.kind==="Fall").map(e=>esc(sideNm(e.X))+" ✝"+e.n).join(", ")+')</summary><div class="gl-ex">'+rows(PV.ev)+'</div></details>':'');
  return '<div class="tot gl"><div class="gl-top">'+side("A")+'<div class="gl-mid"><div class="gl-sk">Skirmish '+B.sk+'</div>'+(rev?'<div class="gl-vs">'+esc(rev.A)+' <span class="note">vs</span> '+esc(rev.B)+'</div>':'<div class="gl-vs note">tactics hidden</div>')+first+'</div>'+side("B")+'</div>'+ex+'</div>';}
// Incoming strikes still to resolve against side X (after any Parry), split normal / Deadly
function incoming(X){const B=battle(),O=X==="A"?"B":"A",S_=B.strk&&B.strk[O];if(!S_||S_.sk!==B.sk)return {n:0,d:0};
  const pr=(B.par||{})[X];const pn=pr&&pr.sk===B.sk?pr:{p:0,pd:0};
  return {n:Math.max(0,S_.succ-S_.deadly-pn.p),d:Math.max(0,S_.deadly-pn.pd)};}
// every roll and casualty of the current Skirmish, in order, for the at-a-glance strip: B.gl = {sk, ev:[{X, kind, target, dice, succ, cas, n}]}
let GL_HOLD=null;   // casualties applied inside a roll are listed after that roll
function glPush(e){const B=battle();if(!B.id)return;if(GL_HOLD&&e.kind==="Fall"){GL_HOLD.push(e);return;}if(!B.gl||B.gl.sk!==B.sk){if(B.gl&&B.gl.ev.length)B.glPrev=B.gl;B.gl={sk:B.sk,ev:[]};}B.gl.ev.push(e);}
function roll(X,kind,nOverride){const B=battle(),before=B.rolls&&B.rolls[X];GL_HOLD=[];let held;try{rollCore(X,kind,nOverride);}finally{held=GL_HOLD;GL_HOLD=null;}const r=B.rolls&&B.rolls[X];
  if(r&&r!==before)glPush({X,kind:r.kind||kind,cleave:!!r.cleave,target:r.target,dice:(r.dice||[]).slice(0,30),succ:r.succ,cas:r.cas,nat10:r.nat10||0});held.forEach(glPush);}
function rollCore(X,kind,nOverride){
  const B=battle(),c=sideCalc(X);if(!c)return;const O=X==="A"?"B":"A",FACES_=BT.faces||10,FOC=BT.focusedThr||10;
  B.strk=B.strk||{};B.par=B.par||{};B.shDest=B.shDest||{};
  const inc=incoming(X);
  if(kind==="Strike"||kind==="DualWield"){
    // Dual Wield: each failed Strike is rerolled once (the reroll can be Focused); successes are never rerolled
    const rr=kind==="DualWield",prev=(B.strk||{})[X];if(rr&&!(prev&&prev.sk===B.sk&&prev.miss)){blog(X+": no failed Strikes to re-roll");save();render();return;}
    // Cleave: each Focused Strike earns a Cleave die, rolled as its own step (roll "Cleave") before the other side defends
    const n=rr?prev.miss:c.front,target=c.toStrike,af=target>FACES_,dice=d10(n);let succ=0,deadly=0,procs=0,cl=0;
    dice.forEach(v=>{if(af||v<target)return;succ++;if(v>=FOC)procs++;
      if(v>=c.critFloor){if(c.hasDeadly)deadly++;if(c.hasCleave)cl++;}});
    const miss=rr||af?0:dice.filter(v=>v<target).length;
    if(rr)B.strk[X]={sk:B.sk,succ:prev.succ+succ,deadly:prev.deadly+deadly,procs:prev.procs+procs,miss:0};
    else{B.strk[X]={sk:B.sk,succ,deadly,procs,miss};delete B.par[O];if(B.clv)delete B.clv[X];}
    if(cl)addCleave(X,cl);
    B.rolls[X]={kind:"Strike",rr,target,dice:dice.sort((x,y)=>y-x),succ,nat10:procs,deadly};
    blog(X+(rr?" Dual Wield re-roll ":" Strike ")+n+"d10 vs "+target+"+ ["+dice.join(",")+"] → "+succ+" strike(s)"+(deadly?" ("+deadly+" Deadly)":"")+(cl?" · Cleave ×"+cl+" to roll":"")+(rr?" · total "+B.strk[X].succ:""));
    const {a:ea}=sideArmy(B[O]);const esh=ea&&ea.shield&&ea.shield!=="None"?EQ.shields[ea.shield]:null;
    if(c.hasDestroy&&procs&&esh&&!(esh.tags||[]).includes("Immune Destroy Shield")&&!hasArmyTok(sideArmy(B[O]).p,"Immune Destroy Shield")&&!B.shDest[O]){B.shDest[O]=true;blog(O+"'s "+ea.shield+" is DESTROYED");}
  }else if(kind==="Cleave"){
    const n=cleaveN(X),st=(B.strk||{})[X];if(!n||!st||st.sk!==B.sk){blog(X+": no Cleave dice to roll");save();render();return;}
    const target=c.toStrike,af=target>FACES_,dice=d10(n).sort((x,y)=>y-x);let succ=0,deadly=0,procs=0,cl=0;
    dice.forEach(v=>{if(af||v<target)return;succ++;if(v>=FOC)procs++;if(v>=c.critFloor){if(c.hasDeadly)deadly++;cl++;}});
    st.succ+=succ;st.deadly+=deadly;st.procs+=procs;B.clv[X]={sk:B.sk,n:cl};
    B.rolls[X]={kind:"Strike",cleave:true,target,dice,succ,nat10:procs,deadly};
    blog(X+" Cleave "+n+"d10 vs "+target+"+ ["+dice.join(",")+"] → "+succ+" strike(s)"+(deadly?" ("+deadly+" Deadly)":"")+(cl?" · Cleave ×"+cl+" more":"")+" · total "+st.succ);
    const {a:ea}=sideArmy(B[O]);const esh=ea&&ea.shield&&ea.shield!=="None"?EQ.shields[ea.shield]:null;
    if(c.hasDestroy&&procs&&esh&&!(esh.tags||[]).includes("Immune Destroy Shield")&&!hasArmyTok(sideArmy(B[O]).p,"Immune Destroy Shield")&&!B.shDest[O]){B.shDest[O]=true;blog(O+"'s "+ea.shield+" is DESTROYED");}
  }else if(kind==="Parry"){
    const tot=nOverride!=null?nOverride:inc.n+inc.d,d=Math.min(inc.d,tot),nn=tot-d,T=c.parryThr;
    const ok=c.canParry;let dn=d10(nn),dd=d10(d),rrN=[],rrD=[];                       // rrN/rrD: Dual Wield rerolls (they can't Riposte)
    if(ok&&c.dualW){const fn=dn.filter(v=>v<T),fd=dd.filter(v=>v<FOC);                // Dual Wield: each failed Parry is re-rolled once
      if(fn.length+fd.length){const rn=d10(fn.length),rd=d10(fd.length);rrN=rn;rrD=rd;dn=dn.filter(v=>v>=T).concat(rn);dd=dd.filter(v=>v>=FOC).concat(rd);
        blog(X+" re-rolls "+(fn.length+fd.length)+" failed Parr"+(fn.length+fd.length===1?"y":"ies")+" (Dual Wield) ["+rn.concat(rd).join(",")+"]");}}
    const p=ok?dn.filter(v=>v>=T).length:0,pd=ok?dd.filter(v=>v>=FOC).length:0;   // no Parry: every Parry fails
    if(!ok)blog(X+" has no Parry — all Parries fail");
    const RT=c.ripP?FOC-1:FOC,rp=a=>a.filter(v=>v>=Math.max(T,RT)).length,ripN0=ok?rp(dn)-rp(rrN):0;  // Riposte +1: a parrying 9 also Ripostes
    const rip=ok&&c.riposte?ripN0+pd-rrD.filter(v=>v>=FOC).length:0;                  // a rerolled Parry can't Riposte
    if(rip){addRip(O,rip);blog(X+" Ripostes ×"+rip+" → "+O+" takes "+rip+" Strike(s) from "+X+"'s melee weapon");}
    B.par[X]={sk:B.sk,p:p+((B.par[X]&&B.par[X].sk===B.sk)?B.par[X].p:0),pd:pd+((B.par[X]&&B.par[X].sk===B.sk)?B.par[X].pd:0)};
    B.rolls[X]={kind,target:ok?T:99,dice:dn.sort((x,y)=>y-x),succ:p,nat10:ripN0,
      dl:d?{target:ok?FOC:99,dice:dd.sort((x,y)=>y-x),succ:pd}:null};
    blog(X+" Parry "+nn+"d10 vs "+(ok?T+"+":"auto-fail")+" ["+dn.join(",")+"] → "+p+" parried"+(d?" · Deadly "+d+"d10 vs "+FOC+"+ ["+dd.join(",")+"] → "+pd+" parried":""));
  }else if(kind==="Save"){
    const tot=nOverride!=null?nOverride:inc.n+inc.d,d=Math.min(inc.d,tot),nn=tot-d;
    const T=c.save,TD=c.deadlySave,dn=d10(nn),dd=d10(d),pz=c.poisoned?FOC:99;
    const s1=T>FACES_?0:dn.filter(v=>v>=T&&v<pz).length,s2=TD>FACES_?0:dd.filter(v=>v>=TD&&v<pz).length,pz1=dn.filter(v=>v>=pz).length;
    B.rolls[X]={kind,target:T,dice:dn.sort((x,y)=>y-x),succ:s1,nat10:0,dl:d?{target:TD,dice:dd.sort((x,y)=>y-x),succ:s2}:null,cas:(nn-s1)+(d-s2)};
    B.sv=B.sv||{};B.sv[X]={sk:B.sk,n:nn-s1-pz1,pz:pz1,d:d-s2};B.svd=B.svd||{};B.svd[X]=B.sk;setPendCas(X,(nn-s1)+(d-s2)+ripCasN(X));   // + Riposte casualties not yet applied
    {const lost=dn.filter(v=>v>=pz&&v>=T).length+dd.filter(v=>v>=pz&&v>=TD).length;if(lost)blog(X+": "+lost+" Save(s) of "+FOC+" fail to Poison");}
    blog(X+" Save "+nn+"d10 vs "+T+"+ ["+dn.join(",")+"] → "+s1+" saved"+(d?" · Deadly "+d+"d10 vs "+(TD>FACES_?"auto-fail":TD+"+")+" ["+dd.join(",")+"] → "+s2+" saved":"")+" → "+((nn-s1)+(d-s2))+" casualties");
  }else if(kind==="Recover"){
    const sv=(B.sv||{})[X],fx=sv?recFx(sv):0,dLost=sv&&BT.deadlyMode==="set"?(sv.d||0):0;if(!sv||sv.sk!==B.sk||!(sv.n+fx)){blog(X+": no failed Saves to Recover");save();render();return;}
    if(c.recThr==null){blog(X+" has no Recover");save();render();return;}
    const T=c.recThr,dn=d10(sv.n),dd=d10(fx),r1=T>FACES_?0:dn.filter(v=>v>=T).length,r2=dd.filter(v=>v>=FOC).length,left=(sv.n-r1)+(fx-r2);
    B.rolls[X]={kind,target:T,dice:dn.sort((x,y)=>y-x),succ:r1,nat10:0,dl:fx?{target:FOC,dice:dd.sort((x,y)=>y-x),succ:r2}:null,cas:left};
    B.sv[X]={sk:B.sk,n:0,pz:0,d:0};setPendCas(X,pendCas(X)-((sv.n+fx)-left));
    if(!c.enduring)B[X].rcv=(B[X].rcv||0)+((sv.n+fx)-left);                           // still counts toward the Panic threshold
    blog(X+" Recover "+sv.n+"d10 vs "+T+"+ ["+dn.join(",")+"] → "+r1+" recovered"+(fx?" · "+(BT.deadlyMode==="set"?"Poisoned ":"Deadly/Poisoned ")+fx+"d10 vs "+FOC+"+ ["+dd.join(",")+"] → "+r2+" recovered":"")+(dLost?" · "+dLost+" Deadly can't be Recovered":"")+" → "+(left+dLost)+" casualties");
  }else if(kind==="RipParry"||kind==="RipSave"){
    const pr=ripN(X);if(!pr){blog(X+": no Riposte Strikes pending");save();render();return;}
    if(kind==="RipParry"){if(!c.canParry){blog(X+" has no Parry — Riposte Strikes can't be Parried");save();render();return;}const T=c.parryThrMelee;let dn=d10(pr);
      let rr=[];if(c.dualW){const fn=dn.filter(v=>v<T).length;if(fn){const rn=d10(fn);rr=rn;dn=dn.filter(v=>v>=T).concat(rn);blog(X+" re-rolls "+fn+" failed Parr"+(fn===1?"y":"ies")+" (Dual Wield) ["+rn.join(",")+"]");}}
      const RT2=Math.max(T,c.ripP?FOC-1:FOC),p=dn.filter(v=>v>=T).length,back=c.riposteMelee?dn.filter(v=>v>=RT2).length-rr.filter(v=>v>=RT2).length:0;   // Riposte +1, not Dual Wield, Ripostes on a 9; a rerolled Parry can't Riposte
      B.rip[X].n=pr-p;B.rolls[X]={kind:"Parry",target:T,dice:dn.sort((x,y)=>y-x),succ:p,nat10:back};
      blog(X+" Parries Riposte "+pr+"d10 vs "+T+"+ ["+dn.join(",")+"] → "+p+" parried");if(back){addRip(O,back);blog(X+" Ripostes the Riposte ×"+back+" → "+O+" takes "+back+" Strike(s)");}}
    else{const T=c.saveMelee,dn=d10(pr),pz=c.poisonedMelee?FOC:99,s1=T>FACES_?0:dn.filter(v=>v>=T&&v<pz).length,pz1=dn.filter(v=>v>=pz).length,f=pr-s1;
      B.rolls[X]={kind:"Save",target:T,dice:dn.sort((x,y)=>y-x),succ:s1,nat10:0,cas:f};delete B.rip[X];
      B.sv=B.sv||{};const o0=(B.sv[X]&&B.sv[X].sk===B.sk)?B.sv[X]:{n:0,pz:0,d:0};B.sv[X]={sk:B.sk,n:o0.n+f-pz1,pz:(o0.pz||0)+pz1,d:o0.d};setPendCas(X,pendCas(X)+f);B.ripCas=B.ripCas||{};B.ripCas[X]={sk:B.sk,n:ripCasN(X)+f};
      blog(X+" Saves vs Riposte (melee) "+pr+"d10 vs "+(T>FACES_?"auto-fail":T+"+")+" ["+dn.join(",")+"] → "+s1+" saved"+(pz1?" ("+pz1+" Poisoned)":"")+" → "+f+" casualties");}
  }else if(kind==="Break"){
    const n=(BT.moraleDiceMax||5),target=c.morale,dice=d10(n).sort((x,y)=>y-x),lost=Math.min(dice.filter(v=>v<target).length,c.a.count||0);
    c.a.count-=lost;B.brk=B.brk||{};B.brk[X]={sk:B.sk,n,target,dice,lost};B.rolls[X]={kind:"Break",target,dice,succ:n-dice.filter(v=>v<target).length,nat10:0,cas:lost};
    blog(X+" Break check "+n+"d10 vs "+target+"+ ["+dice.join(",")+"] → "+lost+" casualties");
  }else{
    {const pc=pendCas(X),pm=(B.pendCas||{})[X];if(pc>0&&!(pm&&pm.mor)){blog(X+": "+pc+" pending casualties applied before the Panic check");applyCasNow(X,pc);}}
    const n=(BT.moraleDiceMax||5),target=c.morale,dice=d10(n).sort((x,y)=>y-x),succ=dice.filter(v=>v>=target).length;
    B.rolls[X]={kind,target,dice,succ,nat10:0};B.pnk=B.pnk||{};B.pnk[X]=B.sk;setPendCas(X,Math.min(n-succ,c.a.count||0),true);
    blog(X+" Morale "+n+"d10 vs "+target+"+ ["+dice.join(",")+"] → "+succ+" succeed, "+(n-succ)+" casualties");
  }
  rollMeta(X,c);autoApplyCas();save();render();
}
// casualties apply themselves once they're final (the flow's "apply" step: no Parry, Save, Recover or Riposte still to roll for that side)
function autoApplyCas(){for(let i=0;i<3;i++){const fl=bFlow();if(!fl)return;let any=false;
  ["A","B"].forEach(X=>{const n=pendCas(X);if(fl.can[X].apply&&n>0){applyCasNow(X,n);any=true;}});if(!any)return;}}
// Cleave dice waiting to be rolled this Skirmish (each Focused Strike, and each Focused Cleave hit, earns one)
function cleaveN(X){const B=battle(),r=(B.clv||{})[X];return r&&r.sk===B.sk?r.n:0;}
function addCleave(X,n){const B=battle();B.clv=B.clv||{};B.clv[X]={sk:B.sk,n:cleaveN(X)+n};}
function ripN(X){const B=battle(),r=(B.rip||{})[X];return r&&r.sk===B.sk?r.n:0;}
function addRip(X,n){const B=battle();B.rip=B.rip||{};B.rip[X]={sk:B.sk,n:ripN(X)+n};}
// mor: casualties from a Morale (Panic / Break) check — they don't count toward the Panic threshold
function setPendCas(X,n,mor){const B=battle();B.pendCas=B.pendCas||{};B.pendCas[X]={sk:B.sk,n:Math.max(0,n|0),mor:!!mor};}
function pendCas(X){const B=battle(),p=(B.pendCas||{})[X];return p&&p.sk===B.sk?p.n:0;}
// Riposte casualties this side took and hasn't applied yet (kept so its own later Save adds to them rather than replacing them)
function ripCasN(X){const B=battle(),r=(B.ripCas||{})[X];return r&&r.sk===B.sk?r.n:0;}
function applyCasNow(X,n){if(n>0)glPush({X,kind:"Fall",n});const B_=battle(),p=(B_.pendCas||{})[X],mor=!!(p&&p.sk===B_.sk&&p.mor);if(B_.pendCas)delete B_.pendCas[X];if(B_.ripCas)delete B_.ripCas[X];
  const {a}=sideArmy(B_[X]);if(!a||!n)return;n=Math.min(n,a.count||0);a.count-=n;if(!mor)B_[X].cas=(B_[X].cas||0)+n;blog(X+" loses "+n+" retinue(s)"+(mor?" (Morale)":"")+" → "+a.count);}
function applyCas(X,n){if(n>0)glPush({X,kind:"Fall",n});const B_=battle(),p=(B_.pendCas||{})[X],mor=!!(p&&p.sk===B_.sk&&p.mor);if(B_.pendCas)delete B_.pendCas[X];if(B_.ripCas)delete B_.ripCas[X];const {a}=sideArmy(battle()[X]);if(!a||!n)return;n=Math.min(n,a.count||0);a.count-=n;if(!mor)battle()[X].cas=(battle()[X].cas||0)+n;blog(X+" loses "+n+" retinue(s)"+(mor?" (Morale)":"")+" → "+a.count);save();render();}
// Break check (end of Skirmish, Endurance 0): r.brk.n d10 vs r.brk.target+, each failure is a casualty (not counted toward Panic)
function rollBreak(X,r,a){const dice=d10(r.brk.n).sort((x,y)=>y-x),lost=Math.min(dice.filter(v=>v<r.brk.target).length,a.count||0);
  a.count-=lost;r.brk.dice=dice;r.brk.lost=lost;delete r.brk.pending;if((a.count||0)===0)r.wiped=true;
  blog(X+" Break check "+r.brk.n+"d10 vs "+r.brk.target+"+ ["+dice.join(",")+"] → "+lost+" casualties"+(r.wiped?" — wiped out":""));}
function rollBreakBtn(X){const B=battle(),r=B.endRep&&B.endRep.sk===B.sk&&B.endRep.rows.find(x=>x.X===X&&x.brk&&x.brk.pending),{a}=sideArmy(B[X]);
  if(!r||!a)return;rollBreak(X,r,a);save();render();}
// what must be resolved before the Skirmish (and so the Battle) can end: casualties applied, Panic checks rolled (emulated dice)
function panicOwed(){const B=battle();if(!B.id||!B.dice)return [];const T=BT.panicThreshold||5;
  return ["A","B"].filter(X=>{const c=sideCalc(X),sd=B[X];if(!c||c.immunePanic||(c.a.count||0)<=0||(c.a.retinue&&isRouted(c.a)))return false;
    return (sd.cas||0)+(c.enduring?0:(sd.rcv||0))>=T&&(B.pnk||{})[X]!==B.sk;});}
function endSkirmish(){
  ["A","B"].forEach(X=>{const n=pendCas(X);if(n>0){blog(X+": "+n+" pending casualties applied at End Skirmish");applyCasNow(X,n);}});
  {const P=panicOwed();if(P.length){flash("Panic check first: "+P.map(sideNm).join(", "));save();render();return;}}
  const B=battle();const cell=B.rev&&B.rev.sk===B.sk?TMX[B.rev.A+"|"+B.rev.B]:null,rep=[];
  ["A","B"].forEach((X,i)=>{const c=sideCalc(X);if(!c)return;const a=c.a,tm=cell?cell[i]:null,r={X,e0:a.endurance||0};
    if(!tm||tm.endurance_loss!==false){a.endurance=Math.max(0,(a.endurance||0)-1);}
    r.e1=a.endurance||0;
    if((a.endurance||0)===0&&!fatigueImmune(X)){
      const n=(BT.moraleDiceMax||5),done=(B.brk||{})[X];r.brk={n,target:c.morale};
      if(done&&done.sk===B.sk){Object.assign(r.brk,{n:done.n,target:done.target,dice:done.dice,lost:done.lost});if((a.count||0)===0)r.wiped=true;}
      else if(B.dice)rollBreak(X,r,a);
      else{r.brk.pending=true;blog(X+" Fatigued — Break check due: "+n+"d10 vs "+c.morale+"+");}
      r.m0=effMorale(a);a.fatigue=(a.fatigue||0)+1;r.fat=a.fatigue;r.m1=effMorale(a);blog(X+" gains Fatigue token ("+a.fatigue+") → morale "+effMorale(a)+"+");}
    if(tm&&tm.strain){a.strained=true;blog(X+" becomes Strained");}
    r.tac=B.rev&&B.rev.sk===B.sk?B.rev[X]:null;if(tm&&tm.end){r.fb=true;blog(X+" tactic ends the Battle (Fall Back)");}
    if(effMorale(a)>=(BT.routThr||11)){r.rout=true;blog(X+" ROUTS (morale "+effMorale(a)+"+)");}
    if((a.count||0)===0){r.wiped=true;blog(X+" wiped out");}
    rep.push(r);B[X].cas=0;B[X].rcv=0;});
  rep.forEach(r=>{const a=(sideArmy(B[r.X])||{}).a;narrate("skirmish_end",r.X,{left:a?a.count||0:0});});
  B.sk++;B.round=0;B.rev=null;EQSEL={};delete SWAP_SEL.A;delete SWAP_SEL.B;B.rolls={};B.strk={};B.par={};PEEK=false;B.endRep={sk:B.sk,rows:rep};
  blog("— Skirmish begins —");save();loadPicks().then(render);
}
function endBattle(win){
  const bHome=["A","B"].map(X=>{const sd=battle()[X];if(!sd||sd.kind!=="bandit")return null;const cp=mapState().camps[sd.camp];return cp&&cp.home?{k:sd.camp,home:cp.home,uid:cp.uid}:null;}).filter(Boolean);
  const routedNow={};{const B0=battle(),R=B0.endRep&&B0.endRep.sk===B0.sk?B0.endRep:null;if(R)R.rows.forEach(r=>{if(r.rout)routedNow[r.X]=true;});}
  const B=battle(),side=X=>{const sa=sideArmy(B[X]);return sa.bandit?{camp:sa.camp,name:"Bandits"}:sa.p?{b:sa.p.board,name:sa.p.name}:null;};
  const queued=B.qid&&bq().find(x=>x.id===B.qid),banditSiege=queued&&queued.kind==="siege"&&queued.A&&queued.A.kind==="bandit",
    siegeCamp=banditSiege&&mapState().camps[queued.A.camp],siegeUid=siegeCamp&&siegeCamp.uid;
  ["A","B"].forEach(X=>{const c=sideCalc(X);if(!c)return;c.a.fatigue=0;});
  if(win==="A"||win==="B"){const O=win==="A"?"B":"A",oc=sideCalc(O),W=side(win),L=side(O);
    if(oc&&W&&L){const cost=+oc.rt.cost||0,t=extortGold(L,W,cost,"Spoils of War");   // Spoils of War = the defeated Army's Retinue cost (per Army, as its upkeep)
      blog(W.name+" won — Spoils of War: "+(oc.a.retinue||"")+" cost, extort "+t.toLocaleString()+(t<cost?" (of "+cost.toLocaleString()+")":""));
      // ruling: winning a Battle against Bandits destroys them: extort the whole Treasury and remove the camp
      // (a Bandit Army takes its home camp, and that camp's Treasury, with it)
      if(L.camp){const M=mapState(),k=Object.keys(M.camps).find(k=>M.camps[k]===L.camp),hk=L.camp.home,
          home=hk&&M.camps[hk]&&M.camps[hk].out===L.camp.uid?M.camps[hk]:null,g=extortGold(L,W,L.camp.gold||0,"destroyed camp");
        blog(W.name+" extorts the Bandits' Treasury: "+g.toLocaleString());
        if(k!=null){delete M.camps[k];blog("Bandit "+(hk?"Army":"Camp")+" @ "+k+" destroyed and removed from play");}
        if(home){const g2=extortGold({camp:home,name:"Bandits"},W,home.gold||0,"destroyed camp");delete M.camps[hk];
          blog(W.name+" extorts its home camp's Treasury: "+g2.toLocaleString()+" · Bandit Camp @ "+hk+" destroyed with its Army");}
        const uids=[L.camp.uid,home&&home.uid].filter(Boolean).map(String),timers=realmTimers();
        for(let i=timers.length-1;i>=0;i--)if(timers[i].bandit&&uids.includes(String(timers[i].bandit)))timers.splice(i,1);
        const gone=[k,home?hk:null].filter(x=>x!=null).map(String);
        D.bqueue=bq().filter(o=>![o.A,o.B].some(s=>s&&s.kind==="bandit"&&gone.includes(String(s.camp))));}}
    if(W&&W.b){W.b.lossStreak=0;W.b.lastBattle="won";}if(L&&L.b){L.b.lossStreak=(+L.b.lossStreak||0)+1;L.b.lastBattle="lost";}
    if(W&&W.b&&L&&L.b)chron("battle",{winner:W.name,loser:L.name});
    const wc=sideCalc(win);if(L&&L.b&&W&&wc&&srcHas(L.b,"spoils_always")){
      const t2=extortGold(W,L,+wc.rt.cost||0,"Spoils of War");if(t2)blog(L.name+" also collects Spoils of War: "+t2.toLocaleString());}
    // "If your Army wins a Battle, it Reinforces N Retinues of its current type at once" (Fleet Anchorage): no cost or Muster Timer, up to the cap
    if(W&&W.b&&wc&&wc.a&&!String((B[win]||{}).aid||"").startsWith("g:"))srcMatch(W.b,"win_reinforce").forEach(x=>{const a=wc.a,
        cap=+((EQ.retinues[a.retinue]||{}).max_size)||+RC.ARMY_MAX_RETINUES||25,add=Math.max(0,Math.min(+x.m[1],cap-(+a.count||0)));
      if(add){a.count=(+a.count||0)+add;blog(W.name+" · "+x.n+": Reinforces "+add+" "+(a.retinue||"")+" Retinues");}});
    [[win,W],[O,L]].forEach(([X,sd])=>{const c=sideCalc(X);if(!sd||!sd.b||!c)return;const lost=Math.max(0,(B.start[X]||0)-(c.a.count||0));
      srcMatch(sd.b,"faith_battle_loss").forEach(x=>{if(lost>=+x.m[2]){addFaith(sd.b,+x.m[1]);blog(sd.name+" · "+x.n+": Faith +"+x.m[1]);}});});}
  else blog("Battle ended with no winner");
  // an Army left with no Retinues is wiped out, and an Army that Routs is destroyed: it leaves the map and the Empire pane,
  // and any other queued Battle against it is dropped
  ["A","B"].forEach(X=>{const sd=B[X];if(!sd||sd.kind==="bandit"||String(sd.aid||"").startsWith("g:"))return;const {p,a}=sideArmy(sd);if(!p||!a)return;
    const routed=routedNow[X];if((+a.count||0)>0&&!routed)return;
    const M=mapState();Object.keys(M.cells).forEach(k=>{const c=M.cells[k];if(c.type==="Army"&&String(c.player)===String(p.id)&&String(c.aid)===String(a.id))delete M.cells[k];});
    p.board.armies=(p.board.armies||[]).filter(x=>x!==a);blog(p.name+"'s "+armyName(a)+(routed&&(+a.count||0)>0?" Routs and is destroyed":" is wiped out")+" — removed from the map");
    if(SEL&&String(SEL.pid)===String(p.id)&&String(SEL.aid)===String(a.id))SEL=null;
    D.bqueue=bq().filter(o=>o.id===B.qid||![o.A,o.B].some(s=>s&&String(s.pid)===String(p.id)&&String(s.aid)===String(a.id)));});
  if(B.qid){D.bqueue=bq().filter(x=>x.id!==B.qid);delete B.qid;}
  if(banditSiege){const T=realmTimers(),i=T.findIndex(t=>t.kind==="siege"&&t.bandit&&String(t.bandit)===String(siegeUid));
    if(i>=0){const t=T[i];if(win==="A"){blog(banditSack(t));endSettlementSieges(t.tp,t.sid);}else T.splice(i,1);}}
  // a Bandit Army goes home after every Battle (survivors re-join its camp); if it was
  // destroyed, its camp is destroyed with it
  bHome.forEach(h=>{const M=mapState();if(M.camps[h.k])banditReturn(h.k);else{const c=M.camps[h.home];if(c&&c.out===h.uid){delete M.camps[h.home];blog("Bandit Camp @ "+h.home+" destroyed with its Army");}}});
  blog("Battle ended — Fatigue tokens removed");B.id=null;B.seizeSet=false;B.rev=null;B.rolls={};save();render();
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
  host.querySelectorAll(".bera").forEach(s=>s.onchange=()=>{const sd=B[s.dataset.x],cp=mapState().camps[sd.camp];if(!cp)return;
    const a=banditArmy(cp),cur=currentEra();if(s.value===cur){delete a.eraPick;delete a.eraPickAt;}else{a.eraPick=s.value;a.eraPickAt=cur;}
    armBandits(cp);save();render();});
  host.querySelectorAll(".bbroll").forEach(b=>b.onclick=()=>banditRollTactic(b.dataset.x));
  const startFn=()=>{
    if(!sideCalc("A")||!sideCalc("B")){flash("pick both armies first");return;}
    if(!B.id&&!B.seizeSet&&!seizeForced()){const d=seizeDefault();if(d==null){flash("Choose who Seizes the Initiative first");return;}B.seize=d;B.seizeSet=true;}
    // restart: back to the Seize the Initiative card (choose again, then Start)
    if(B.id){if(!confirm("Restart the battle?"))return;B.id=null;B.sk=1;B.round=0;B.rev=null;B.rolls={};B.strk={};B.par={};B.sv={};B.rip={};B.pendCas={};B.svd={};B.pnk={};B.ripCas={};B.brk={};B.shDest={};B.clv={};B.endRep=null;
      B.seizeSet=false;PEEK=false;TAC_SEL={};blog("Battle restarted");save();render();return;}
    ["A","B"].forEach(X=>{if(B[X].kind==="bandit"){const cp=mapState().camps[B[X].camp];if(cp)armBandits(cp);}});
    ["A","B"].forEach(X=>{const sa=sideArmy(B[X]);if(sa&&sa.a&&!sa.bandit)delete sa.a.pillage;});
    B.id=Date.now().toString(36);B.sk=1;B.round=0;B.rev=null;B.rolls={};B.strk={};B.par={};B.sv={};B.rip={};B.pendCas={};B.svd={};B.pnk={};B.ripCas={};B.brk={};B.shDest={};B.clv={};B.log=[];B.endRep=null;PEEK=false;
    B.start={A:sideCalc("A").a.count||0,B:sideCalc("B").a.count||0};B.A.cas=0;B.B.cas=0;B.A.rcv=0;B.B.rcv=0;blog("Battle begins");save();loadPicks().then(render);};
  host.querySelectorAll("#bStart,#bStartGo").forEach(b=>b.onclick=startFn);
  host.querySelectorAll(".bseize").forEach(b=>b.onclick=()=>{B.seize=b.dataset.v;B.seizeSet=true;save();render();});
  host.querySelectorAll(".bFinish").forEach(b=>b.onclick=()=>{const why=battleOwed();if(why){flash("Before the Battle ends: "+why);return;}endBattle(b.dataset.w||null);});
  const dc=host.querySelector("#bDice");if(dc)dc.onchange=()=>{B.dice=dc.checked;save();render();};
  const rs=host.querySelector("#bReset");if(rs)rs.onclick=()=>{B.round=(B.round||0)+1;B.rev=null;PEEK=false;blog("Tactic picks reset");save();loadPicks().then(render);};
  host.querySelectorAll("#bEndSk,.bEndSk2").forEach(es=>es.onclick=()=>{const B=battle(),pb=B.endRep&&B.endRep.sk===B.sk&&B.endRep.rows.filter(r=>r.brk&&r.brk.pending).map(r=>r.X),fl=bFlow();
    if(fl&&!fl.done){const late=fl.fought&&["A","B"].some(X=>fl.can[X].panic||fl.can[X].apply);   // casualties and Panic checks can't be skipped
      if(late){flash("Resolve first: "+fl.msg.replace(/<[^>]+>/g,""));return;}
      if(!confirm("Still to do: "+fl.msg.replace(/<[^>]+>/g,"")+". End the Skirmish anyway?"))return;}
    if(pb&&pb.length){flash("Roll the Break check first: "+pb.join(", "));return;}endSkirmish();});
  host.querySelectorAll(".bBrk").forEach(b=>b.onclick=()=>rollBreakBtn(b.dataset.x));
  host.querySelectorAll(".bEndB").forEach(eb=>eb.onclick=()=>{const why=battleOwed();if(why){flash("Before the Battle ends: "+why);return;}if(confirm("End the battle"+(eb.dataset.w?" — "+eb.dataset.w+" won (Spoils of War)":" with no winner")+"? Removes Fatigue tokens."))endBattle(eb.dataset.w||null);});
  host.querySelectorAll(".btac").forEach(b=>b.onclick=()=>{TAC_SEL[b.dataset.x]=b.dataset.t;render();});
  host.querySelectorAll(".bswap").forEach(cb=>cb.onchange=()=>{SWAP_SEL[cb.dataset.x]=cb.checked;});
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
// Each player completes each Edict once; a "unique" Edict (Imperium) once per game, for the first player.
// Sovereign Standing / Monument / Wonder: noted the moment one is held (every save); with EDICT_UNIQUE, a Domain / Monument /
// Wonder another player completed it with doesn't count. Wealth and Imperium: their timers advance at Yields & Expenditures;
// Living Saints: at the Public Order step — otherwise the timer is removed; at its length the Edict is pending.
// Vassalize and Last Alliance Standing stay manual.
function edictCond(name,b){const e=EDICTS[name]||{};
  if(name==="Wealth")return +RC.WEALTH_EDICT_GOLD>0&&(b.treasury||0)>=+RC.WEALTH_EDICT_GOLD;
  if(name==="Living Saints")return (b.po||0)>=PO_MAX;
  if(e.by_players){const g=mapState().grid,p=(D.players||[]).find(q=>q.board===b),pct=edictPlayersPct(e);if(!g||!p||!(pct>0))return null;
    return uncontestedCount(p)*100>=pct*g.width*g.height;}   // Realm = every hex on the map
  return null;}
// % for this player count: the largest key ≤ players ("5+" reads as 5); below the smallest key, the smallest
function edictPlayersPct(e){const T=e.by_players||{},n=(D.players||[]).length;let best=null,lo=null;
  Object.keys(T).forEach(k=>{const m=parseInt(k,10);if(isNaN(m))return;
    if(!lo||m<lo[0])lo=[m,+T[k]];if(m<=n&&(!best||m>best[0]))best=[m,+T[k]];});
  return (best||lo||[0,0])[1];}
function uncontestedCount(p){const M=mapState(),g=M.grid;if(!g)return 0;const own=reachOwners(M,g.width,g.height),id=String(p.id);
  return Object.keys(own).filter(k=>own[k].size===1&&own[k].has(id)).length;}
function edictHeld(name,b){const e=EDICTS[name]||{};
  if(e.type==="Standing")return DOMAINS.filter(d=>((b.domains||{})[d]||0)>=SOV);
  if(/monument/i.test(name))return withBoard(b,()=>[...new Set(S.placed.filter(q=>!q.fac&&pActive(q)&&R[q.name]&&R[q.name].monument).map(q=>q.name))]);   // completed by you (a Heritage's starting piece isn't)
  if(/wonder/i.test(name))return Object.keys(b.wonders||{}).filter(n=>b.wonders[n]&&!((b.itimer||{})[n]>0)&&!(b.facInfra||[]).includes(n));
  return null;}
function edictPend(b,name,lab){b.edictPending=b.edictPending||[];b.edictPending.push({name,lab,turn:tTurn()});}
function edictIsPending(b,name,lab){return (b.edictPending||[]).some(x=>x.name===name&&x.lab===lab);}
// completed or pending for this player / closed to this player (done, or a unique Edict someone else has)
function edictDone(b,name){return ((b.edictLog||{})[name]||[]).length>0||(b.edictPending||[]).some(x=>x.name===name);}
// multi Edicts (EDICTS[*].per): one per Domain / Monument / Wonder; "first" = only the first player, "each" = every player once
function edictPer(name){return (EDICTS[name]||{}).per||"";}
function edictClosed(b,name){if(edictPer(name))return false;return edictDone(b,name)||(!!(EDICTS[name]||{}).unique&&(D.players||[]).some(q=>q.board&&edictDone(q.board,name)));}
// timed Edict step (called from empEconomy for Wealth and Imperium, empPO for Living Saints)
function edictTick(b,name){if(!EDICTS[name])return;b.edictTimers=b.edictTimers||{};
  if(edictClosed(b,name)){b.edictTimers[name]=0;return;}
  const tl=edictTimerLen(EDICTS[name]),c=edictCond(name,b);if(!tl||c==null)return;
  if(!c){b.edictTimers[name]=0;return;}
  b.edictTimers[name]=(b.edictTimers[name]||0)+1;if(b.edictTimers[name]>=tl){edictPend(b,name,"");b.edictTimers[name]=0;}}
// held Edicts (every save): the first held Domain / Monument / Wonder goes pending; with EDICT_UNIQUE (build_all_CE.bat
// toggle) one another player already completed this Edict with is skipped
function edictTaken(b,name,l){return ((b.edictLog||{})[name]||[]).includes(l)||edictIsPending(b,name,l);}
function edictWatch(){const P=D.players||[];P.forEach(p=>{const b=p.board;if(!b)return;
  EDICT_NAMES.forEach(name=>{if(edictClosed(b,name))return;const held=edictHeld(name,b);if(!held)return;
    const per=edictPer(name);
    if(per){held.forEach(l=>{if(edictTaken(b,name,l))return;if(per==="first"&&P.some(q=>q.board&&q.board!==b&&edictTaken(q.board,name,l)))return;edictPend(b,name,l);});return;}
    const l=held.find(l=>!(RC.EDICT_UNIQUE&&P.some(q=>q.board&&edictTaken(q.board,name,l))));if(l!=null)edictPend(b,name,l);});});}
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
