// ---- state: multiplayer dashboard ----
function startDoms(){const u=+ST.Untested||1;return {Industry:u,Prowess:u,Piety:u,Cunning:u};}
// ---- Ages (AGES): starting Year + the Domain every player starts Rising in (null rising = each player picks) ----
const AGE_L=DATA.ages||[];
function ageRec(){return AGE_L.find(a=>a.name===D.age)||null;}
function ageRisingOf(p){const a=ageRec();if(!a)return "";return a.rising||((p&&p.board&&p.board.ageRising)||"");}
function startDomsFor(p){const o=Object.assign({},startDoms()),d=ageRisingOf(p);if(d)o[d]=Math.max(o[d]||0,RIS);return o;}
function startDomTotal(p){return DOMAINS.reduce((a,d)=>a+(startDomsFor(p)[d]||0),0);}
function curYear(){const a=ageRec();if(!a)return null;return (D.year0!=null?+D.year0:a.years[0])+(+D.yearsGone||0);}
function applyAgeStart(){D.players.forEach(p=>{p.board.domains=startDomsFor(p);});}
// EMPIRE_START_TIERS; highest tier is the capital
function startSettlements(){const t=(DATA.startTiers&&DATA.startTiers.length)?DATA.startTiers:["Town","Village","Hamlet"];
  const rank=x=>((DATA.settlements||{})[x]||{}).tier||0;let ci=0;t.forEach((x,i)=>{if(rank(x)>rank(t[ci]))ci=i;});
  return t.map((x,i)=>({id:i+1,tier:x,capital:i===ci}));}
function startSig(){return ((DATA.startTiers&&DATA.startTiers.length)?DATA.startTiers:["Town","Village","Hamlet"]).join(",");}
// a board still in its untouched starting state follows EMPIRE_START_TIERS if the data changes
function reseedIfPristine(b){if(!b)return false;const tiers=(b.settlements||[]).map(x=>x.tier).join(",");
  const pristine=!(b.turn>0)&&!(b.placed||[]).length&&!Object.keys(b.infra||{}).length&&!Object.keys(b.wonders||{}).length&&!(b.armies||[]).length
    &&(b.settlements||[]).every(x=>!(x.bt>0))&&(b.startSig==null||b.startSig===tiers);
  if(pristine&&tiers!==startSig()){b.settlements=startSettlements();b.startSig=startSig();return true;}
  if(b.startSig==null&&pristine)b.startSig=tiers;return false;}
function newBoard(){return {startSig:startSig(),placed:[],settlements:startSettlements(),infra:{},wonders:{},armies:[],
  treasury:(DATA.startTreasury||0),turn:0,autoNet:true,expanded:[],po:0,domains:Object.assign({},startDoms()),edicts:{},edictLog:{},edictTimers:{}};}
function newPlayer(i){const p={id:i,name:"Player "+i,color:PLAYER_COLORS[(i-1)%PLAYER_COLORS.length],board:newBoard()};p.board.domains=startDomsFor(p);return p;}
let D={players:[],active:0,view:"table",renown:1,theme:"pixel",themeV:1,
       map:{seed:"",cols:16,rows:12,markers:[]}};
D.players=[newPlayer(1)];
let S=null;                              // alias to active player's board
let tab="pursuit", activeTypes=new Set(), aid=1, pid=1, sid=1, activeSid=null, catOpen=new Set(), mid=1, mtool="Select";

try{const d=JSON.parse(localStorage.getItem("renown_dash")||"null");if(d&&d.players)D=d;}catch(e){}
// migrate single-board board3 -> player 1
try{
  if(D.players.length===1 && !D.players[0].board.placed.length){
    const old=JSON.parse(localStorage.getItem("renown_board3")||"null");
    if(old){D.players[0].board=Object.assign(newBoard(),old);}
  }
}catch(e){}
function normalizeD(){
  try{(D.players||[]).forEach(p=>reseedIfPristine(p.board));}catch(e){}
  delete D.startDomains;                                   // "Starting universe" retired: new players start Untested (STANDING_THRESHOLDS)
  if(D.themeV!==1){D.theme="pixel";D.themeV=1;}   // Pixel is the default look: one-time switch for devices saved on the old default
  D.theme=D.theme||"pixel"; D.shape=D.shape||"sharp"; D.pursuitView=D.pursuitView||"cards";
  D.players=(D.players&&D.players.length)?D.players:[newPlayer(1)];
  D.players.forEach(p=>{p.board=Object.assign(newBoard(),p.board);
    const dm=p.board.domains||{},nd={};
    Object.keys(dm).forEach(k=>{const v=dm[k];nd[k]=typeof v==="number"?v:(STAND_THRESH[v]||0);});
    p.board.domains=nd; p.board.edicts=p.board.edicts||{};
    p.board.edictLog=p.board.edictLog||{}; p.board.edictTimers=p.board.edictTimers||{};
    // migrate legacy status dropdown: "Complete" -> one logged entry
    Object.keys(p.board.edicts).forEach(k=>{if(p.board.edicts[k]==="Complete"&&!(p.board.edictLog[k]||[]).length)p.board.edictLog[k]=[""];});
    p.board.edicts={};});
  if(typeof D.renown!=="number")D.renown=1;
  if(D.active>=D.players.length)D.active=0;
  D.map=D.map||{seed:"",cols:16,rows:12,markers:[]}; D.map.cells=D.map.cells||{};
}
normalizeD();

function activeBoard(){return D.players[D.active].board;}
function reindex(){
  S=activeBoard();
  aid=1;pid=1;sid=1;
  S.armies=S.armies||[];S.placed=S.placed||[];S.settlements=S.settlements||[];
  S.armies.forEach(a=>{if(a.id>=aid)aid=a.id+1;});
  S.placed.forEach(p=>{if(p.id>=pid)pid=p.id+1;});
  S.settlements.forEach(s=>{if(s.id>=sid)sid=s.id+1;});
  const cp=S.settlements.find(x=>x.capital);activeSid=cp?cp.id:(S.settlements[0]?S.settlements[0].id:null);
}
(D.map.markers||[]).forEach(m=>{if(m.id>=mid)mid=m.id+1;});
reindex();

let PC={};                              // name -> count (derived, active board)
function pActive(p){return !(p.bt>0)&&!(p.dmg>0);}
// ---- ignorable flags: hidden while the same flag persists; shown again if it changes, or clears and returns ----
let IGN_N=0,IGN_DIRTY=false;
// S.ign[key] = [ignored texts]: several live flags may share one key (numbers stripped), so each keeps its own ignore
function ignHas(key,sig){const v=(S.ign||{})[key];return Array.isArray(v)?v.includes(sig):v===sig;}
function flagState(key,active,sig){S.ign=S.ign||{};
  if(!active){if(key in S.ign){delete S.ign[key];IGN_DIRTY=true;}return "off";}
  if(ignHas(key,sig)){IGN_N++;return "ignored";}
  if(key in S.ign&&!Array.isArray(S.ign[key])){delete S.ign[key];IGN_DIRTY=true;}   // changed since it was ignored → show again
  return "on";}
function ignBtn(key,sig){const b=document.createElement("button");b.className="ignb";b.textContent="ignore";
  b.title="Hide this flag until it changes, or clears and comes back";
  b.onclick=e=>{e.stopPropagation();S.ign=S.ign||{};const v=S.ign[key],L=Array.isArray(v)?v:(v!=null?[v]:[]);if(!L.includes(sig))L.push(sig);S.ign[key]=L;save();render();};return b;}
function ignNote(){const el=document.getElementById("ignNote");if(!el)return;
  el.innerHTML=IGN_N?' · '+IGN_N+' flag'+(IGN_N>1?'s':'')+' ignored <a href="#" id="ignShow">show</a>':'';
  const a=document.getElementById("ignShow");if(a)a.onclick=e=>{e.preventDefault();S.ign={};save();render();};
  if(IGN_DIRTY){IGN_DIRTY=false;save();}}
// ---- Pursuit unlock (Domain Standing) — flags only, never blocks ----
const ST_ORDER=["Untested","Rising","Established","Sovereign"];
function unlockStatus(n,b){b=b||S;const raw=((R[n]||{}).unlock_raw||"").trim();
  if(!raw||raw==="-"||raw==="\u2014")return {ok:true,toks:[],missing:[]};
  const dv=b.domains||{},rank=d=>ST_ORDER.indexOf(domBand(dv[d]||0)),toks=[];
  raw.split(/\s*[+,]\s*/).filter(Boolean).forEach(t=>{let m;
    if(m=t.match(/^(Rising|Established|Sovereign)\s+(Industry|Prowess|Cunning|Piety)$/i)){const need=ST_ORDER.indexOf(m[1][0].toUpperCase()+m[1].slice(1).toLowerCase()),d=m[2][0].toUpperCase()+m[2].slice(1).toLowerCase();
      toks.push({t,ok:rank(d)>=need,why:d+" is "+domBand(dv[d]||0)});}
    else if(m=t.match(/^(\d+)\s+(Rising|Established|Sovereign)$/i)){const need=ST_ORDER.indexOf(m[2][0].toUpperCase()+m[2].slice(1).toLowerCase()),have=T_DOMS.filter(d=>rank(d)>=need).length;
      toks.push({t,ok:have>=+m[1],why:have+"/"+m[1]+" Domains at "+m[2]+"+"});}
    else toks.push({t,ok:null,why:"check manually"});});
  return {ok:toks.every(x=>x.ok!==false),manual:toks.some(x=>x.ok===null),toks,missing:toks.filter(x=>x.ok===false).map(x=>x.t+" ("+x.why+")")};}
// catalog search matches the engine id OR its display name (NAME_DISPLAY)
function nameHit(n,q){if(!q)return true;if(n.toLowerCase().includes(q))return true;const d=window.dispName?window.dispName(n):n;return d!==n&&d.toLowerCase().includes(q);}
function missTxt(list){return list.map(n=>{const q=(S.placed||[]).find(x=>x.name===n&&!pActive(x));
  return q?n+(q.bt>0?" (building, "+q.bt+")":" (damaged, "+q.dmg+")"):n;}).join("  +  ");}
function recomputePC(){PC={};S.placed.forEach(p=>{if(pActive(p))PC[p.name]=(PC[p.name]||0)+1;});}
const BTM=DATA.buildTimers||{},TMR=DATA.timers||{};
const REPAIR_T=((TMR["Repair Timer"]||{}).default)||BTM.Repair||2;
// "Build Timer ±X" on your active Pursuits (Innate, or Mastery when earned) adjusts the default Build Timer of new
// Pursuits, Infrastructure, Wonders and Settlements (charter / upgrade); they stack; never below 0 (a Timer at 0 resolves immediately).
function buildTimerMod(){return withBoard(S,()=>{const have=new Set(Object.keys(PC)),{earned}=computeEarned(have);let mod=0;const src=[];
  Object.keys(PC).forEach(n=>{[["h:",true,""],["hm:",!!earned[n]," (M)"]].forEach(([k,on,tag])=>{if(!on)return;
    efxOf(k+n,"build_timer").forEach(x=>{const v=(x[1]==="+"?1:-1)*(+x[2]);mod+=v;src.push(n+tag+" "+(v>0?"+":"\u2212")+Math.abs(v));});});});
  return {mod,src};});}
function withBuildMod(base){if(!(base>0))return {t:base||0,base:base||0,mod:0,src:[]};const m=buildTimerMod();return {t:Math.max(0,base+m.mod),base,mod:m.mod,src:m.src};}
function pursuitBaseTime(n){const r=R[n]||{};if(r.build_time!=null)return r.build_time;const t=r.type;return t==="Power"?(BTM["Power Pursuit"]??BTM.Pursuit):t==="Monument"?(BTM["Monument Pursuit"]??BTM.Pursuit):(BTM.Pursuit||0);}
function infraBaseTime(n){if(WON[n])return BTM.Wonder||0;const i=INFRA[n];return i?(((BTM.Infrastructure||{})[i.tier])||0):0;}
function pursuitBuildTime(n){return withBuildMod(pursuitBaseTime(n)).t;}
function infraBuildTime(n){return withBuildMod(infraBaseTime(n)).t;}
function buildNote(base){const b=withBuildMod(base);return b.mod?" · Build Timer "+b.base+" → "+b.t+" ("+b.src.join(", ")+")":"";}
function settBaseTime(t){return BTM[t]??(((DATA.settlements||{})[t]||{}).build_time)??0;}
function settBuildTime(t){return withBuildMod(settBaseTime(t)).t;}
function itm(){S.itimer=S.itimer||{};S.idmg=S.idmg||{};S.facInfra=S.facInfra||[];}
function infraOn(n){itm();return !!(S.infra[n]||S.wonders[n])&&!(S.itimer[n]>0)&&!(S.idmg[n]>0);}
function gameStarted(){return (S.turn||0)>0;}
// ---- Gold log (Ledger): every Treasury change with its reason. tGold() records a change; changes made any other way (typing the
// Treasury, the ± buttons, an older client) are picked up by glogSync() as "adjusted" (quick successive ones merge) ----
const GLOG_MAX=150;
function glogTurn(){try{return tTurn();}catch(e){return 0;}}
function glogSea(){try{return curSeason();}catch(e){return "";}}
function glogPush(b,d,why){b.glog=b.glog||[];const t=glogTurn(),last=b.glog[b.glog.length-1],now=Date.now();
  if(why==="adjusted"&&last&&last.why==="adjusted"&&last.t===t&&now-(last.ts||0)<8000){last.d+=d;last.bal=+b.treasury||0;last.ts=now;if(!last.d)b.glog.pop();}
  else b.glog.push({t,s:glogSea(),d,why:String(why||""),bal:+b.treasury||0,ts:now});
  if(b.glog.length>GLOG_MAX)b.glog.splice(0,b.glog.length-GLOG_MAX);b.gseen=+b.treasury||0;}
function glogSync(b){if(!b)return;const t=+b.treasury||0;if(b.gseen==null){b.gseen=t;return;}if(t!==b.gseen)glogPush(b,t-b.gseen,"adjusted");}
function tGold(b,d,why){d=Math.round(+d||0);if(!b||!d)return 0;glogSync(b);b.treasury=(+b.treasury||0)+d;glogPush(b,d,why);return d;}
function boardOwnerName(b){const p=(D.players||[]).find(q=>q.board===b);return p?p.name:"";}
// One player's end-of-turn bookkeeping (treasury button and the Table's End turn share this).
// ---- Empire Phase, in rules order (RULES: The Turn › Empire Phase). Stages run per board; empirePhase() runs them
// across every board so realm-wide steps (Siege / Muster / Sack / Capture timers, Bandits, Extort) fall in sequence.
function empTimers(b){b.turn=(b.turn||0)+1;return tickTimers(b);}                        // Build, Repair
function empEconomy(b){const sn=seasonNet(b),net=Math.round(sn.net||0),g0=b.treasury||0;
  if(b.autoNet){const sea=curSeason(),part=[["Income & upkeep",Math.round(sn.base||0)],[sea+" (Season)",Math.round(sn.seasonal||0)],["Winter tax",Math.round(sn.tax||0)],["Trade",Math.round(sn.trade||0)]];
    part[0][1]+=net-part.reduce((t,x)=>t+x[1],0);part.forEach(([k,v])=>tGold(b,v,k));}   // Winter tax, income, trade, upkeep (if auto-apply is on)
  b.insolv=(b.treasury||0)<0?(+b.insolv||0)+1:0;                              // "Insolvency": consecutive Upkeep with negative Treasury
  return {sn,net,g0};}
function empPO(b,done){const m=boardMetrics(b),p0=b.po||0,fd=m.po||0,pm=poModTotal(b);let dpo=fd+pm;
  // each Doubt source is one instance; the turn's first-Doubt slots reduce the first instances, one slot each
  const inst=[m.doubt||0].concat(poModRows(b).filter(r=>r.side==="doubt").map(r=>r.n)).filter(n=>n>0),fr=firstDoubtRed(b),sl=fr.slots.slice();
  let cut=0;inst.forEach(n=>{if(sl.length)cut+=Math.min(n,sl.shift());});
  if(cut>0){dpo+=cut;done.push("first Doubt −"+cut+" ("+fr.src.join(", ")+")");}
  b.fd={turn:b.turn,slots:sl};
  b.po=applyPOFloor(b,Math.max(PO_MIN,Math.min(PO_MAX,p0+dpo)));return {fd,pm,p0};}
// "Armies and Garrisons within controlled Settlements gain Immune Strained" (Granary): an Army inside one of its owner's Settlements, or a Garrison
function immuneStrainIn(p,a){if(!p||!a||a.sackT)return null;const x=a.garrison?{q:p}:armyInside(p,a);if(!x)return null;   // whose Settlement it is decides
  const m=srcMatch(x.q.board,"immune_strain_home")[0];return m?m.n+(sameP(x.q,p)?"":" · "+x.q.name):null;}
// a Settlement under Siege gives its Armies and Garrison Strained (ruling); Granary-type Immune Strained, or a faction not affected by
// Besieged restrictions, prevents it. effStrained = what Strained means right now (Battle Init, Endurance regain, display).
function siegeStrains(p,a){if(!p||!a||besiegeExempt(p))return false;return a.garrison?(a.sid!=null&&siegeOn(p.id,a.sid)):armyBesieged(p,a);}
function effStrained(p,a){if(!a||immuneStrainIn(p,a))return false;return !!a.strained||siegeStrains(p,a);}
function empArmies(b){let regained=0,cleared=0;const pl=playerOfBoard(b),isc=!!pl&&srcHas(b,"immune_strain_siege");
  (b.armies||[]).forEach(a=>{if(isc&&a.strained&&!a.sackT){const sg=armySieging(pl,a);if(sg&&sg.kind==="siege")a.strained=false;}
    if(a.strained&&pl&&immuneStrainIn(pl,a))a.strained=false;
    if(pl&&siegeStrains(pl,a)&&!immuneStrainIn(pl,a))a.strained=true;if(!a.strained){a.endurance=(a.endurance||0)+EQ.endurance_regain;regained++;}else cleared++;a.strained=false;
    if(pl&&siegeStrains(pl,a)&&!immuneStrainIn(pl,a))a.strained=true;});
  return {regained,cleared};}
function endRow(b,done,ec,po,ar){return {turn:b.turn,net:ec.net,tax:ec.sn.tax,seasonal:ec.sn.seasonal,trade:ec.sn.trade,season:curSeason(),applied:!!b.autoNet,
  g0:ec.g0,g1:b.treasury||0,fd:po.fd,pm:po.pm,p0:po.p0,p1:b.po,done,regained:ar.regained,regain:EQ.endurance_regain,cleared:ar.cleared};}
// one board on its own (board view "End turn")
function boardEndTurn(b){const done=empTimers(b);{const p=playerOfBoard(b);if(p)musterTick(p).forEach(x=>done.push(x));}
  const ec=empEconomy(b),po=empPO(b,done),ar=empArmies(b);return endRow(b,done,ec,po,ar);}
// realm timers of the given types count down (Siege Timers don't in Winter)
function tickRealm(types){const w=curSeason()==="Winter";realmTimers().forEach(x=>{if(!types.includes(x.type))return;if(w&&x.type==="Siege Timer"&&!siegeWinterOK(x))return;if(x.n>0)x.n--;});}
const TIMER_ORDER=["Build Timer","Repair Timer","Truce Timer","Siege Timer","Muster Timer","Sack Timer","Capture Timer"];
// Sabotage: "gains Blocked until the end of next turn" — set in turn T, gone when turn T+2's Empire Phase begins
function expireBlocks(){const M=mapState(),out=[];Object.keys(M.cells).forEach(k=>{const c=M.cells[k];if(c.blocked&&c.blockedT!=null&&tTurn()-c.blockedT>=2){delete c.blocked;delete c.blockedT;out.push("Army @ "+k+": Blocked (Sabotage) ends");}});
  D.players.forEach(p=>(p.board.armies||[]).forEach(a=>{if(a.blocked&&a.blockedT!=null&&tTurn()-a.blockedT>=2){delete a.blocked;delete a.blockedT;out.push(p.name+" · "+(a.label||("Army "+a.id))+": Blocked (Sabotage) ends");}}));return out;}
function empirePhase(){const P=D.players,done={},log=[];P.forEach(p=>done[p.id]=[]);expireBlocks().forEach(x=>log.push(x));
  // 1-2. Standing effects are live; the Season was set in the Rest Phase.
  // 3. Timers, in order: Build, Repair (boards) · Truce, Siege (realm) · Muster (Armies) · Sack, Capture (realm) · any other realm timer
  P.forEach(p=>empTimers(p.board).forEach(x=>done[p.id].push(x)));tickRealm(["Build Timer","Repair Timer"]);
  tickRealm(["Truce Timer","Siege Timer"]);
  P.forEach(p=>musterTick(p).forEach(x=>done[p.id].push(x)));tickRealm(["Muster Timer"]);
  tickRealm(["Sack Timer","Capture Timer"]);
  tickRealm(Object.keys(TMR).filter(k=>!TIMER_ORDER.includes(k)));
  // 4. resolve timers that reached 0
  resolveRealm().forEach(x=>log.push(x));
  // 5. Host resolves Bandit Mechanics (diverted gold is measured before income, credited after)
  if(banditAuto()){BST()._t=tTurn();runBanditMechanics();}
  const skims=banditSkims();   // Destabilize (bandit or player) / Intercept Caravan settle every Empire Phase, auto or not
  // 6. Influence & Envoys: computed live from the new Era / Season
  // 7-8. Winter tax, income & upkeep (trade inside)
  const ec={};P.forEach(p=>ec[p.id]=empEconomy(p.board));
  // 9. Extort
  runAutoExtort().forEach(x=>log.push(x));runLoans().forEach(x=>log.push(x));runPillage().forEach(x=>log.push(x));if(skims.length)creditSkims(skims).forEach(x=>log.push(x));delete BST()._t;
  // 10. innate Public Order modifiers (first Doubt reductions)
  const po={};P.forEach(p=>po[p.id]=empPO(p.board,done[p.id]));
  // 11. Endurance; Strained clears (Sack keeps its Army Strained)
  const ar={};P.forEach(p=>ar[p.id]=empArmies(p.board));sackLocks();
  return {rows:P.map(p=>Object.assign({pid:String(p.id),name:p.name,color:p.color},endRow(p.board,done[p.id],ec[p.id],po[p.id],ar[p.id]))),log};}
function tickTimers(b){const done=[],pl=playerOfBoard(b),bs=sid=>!!pl&&settBesieged(pl,sid);
  (b.placed||[]).forEach(p=>{if(bs(p.sid))return;if(p.bt>0){p.bt--;if(!p.bt)done.push("built "+p.name);}if(p.dmg>0&&p.rep){p.dmg--;if(!p.dmg){delete p.rep;done.push("repaired "+p.name);}}});
  ["itimer","idmg"].forEach(k=>{const o=b[k]||{},rp=b.irep||{};Object.keys(o).forEach(n=>{if(k==="idmg"&&!rp[n])return;o[n]--;if(o[n]<=0){delete o[n];if(k==="idmg")delete rp[n];done.push((k==="itimer"?"built ":"repaired ")+n);}});});
  (b.settlements||[]).forEach(s=>{if(bs(s.id))return;if(s.bt>0){s.bt--;if(!s.bt)done.push(settFinish(pl,s));}});
  return done;}
// pursuit upkeep: PURSUIT_UPKEEP_BY_TYPE, else PURSUIT_UPKEEP_DEFAULT; faction pieces pay none
const PUP=DATA.pursuitUpkeep||{byType:{},def:0};
// faction "Your <Type>[ & <Type>] Pursuits|Holdings have Craft +N[ and cost no Upkeep]" (Luminous Court)
// or "Your Holdings which require <Domain> have Craft +N[ and cost no Upkeep]" (Luminous Court, current wording); has(name) = the bonus applies
function facTypeBonus(b){const fk="f:"+((b||{}).faction||""),m=hitOf(fk,"fac_type_bonus");
  if(m){const types=m[1].split(/\s*(?:&|,|\band\b)\s*/).map(x=>x.trim()).filter(Boolean);return {types,has:n=>types.includes((R[n]||{}).type),craft:+m[2],free:!!m[3]};}
  const d=hitOf(fk,"fac_dom_bonus");return d?{dom:d[1],has:n=>holdDom(n).toLowerCase()===d[1].toLowerCase(),craft:+d[2],free:!!d[3]}:null;}
function pursuitUpkeep(p){if(p.fac||!pActive(p)||NATURAL.has(p.name))return 0;   // faction, inactive (building / Damaged / repairing), or Natural
  {const tb=facTypeBonus(S);if(tb&&tb.free&&tb.has(p.name))return 0;}
  const r=R[p.name]||{};if(r.upkeep!=null)return r.upkeep;const t=r.type;return (PUP.byType&&t in PUP.byType)?PUP.byType[t]:(PUP.def||0);}
function withBoard(b,fn){const pS=S,pPC=PC;S=b;recomputePC();const r=fn();S=pS;PC=pPC;return r;}

// ---- persistence: server API (same-origin) with localStorage fallback ----
const API={online:null};
let TOKEN="";try{TOKEN=localStorage.getItem("renown_token")||"";}catch(e){}
async function apiFetch(method,path,body){
  try{
    const h={};if(body!==undefined)h["Content-Type"]="application/json";if(TOKEN)h["X-Renown-Token"]=TOKEN;
    const r=await fetch(path,{method,headers:h,body:body!==undefined?JSON.stringify(body):undefined});noteServerDate(r);
    if(r.status===401){setOnline(false);const t=document.getElementById("srvStat");if(t)t.textContent="unauthorized — check access token";return null;}
    if(!r.ok)throw 0;
    setOnline(true);
    const ct=r.headers.get("content-type")||"";
    return ct.includes("json")?await r.json():await r.text();
  }catch(e){setOnline(false);return null;}
}
function setOnline(ok){if(API.online===ok)return;API.online=ok;
  const el=document.getElementById("srvDot");if(el){el.style.background=ok?cvar("--income"):cvar("--dim2");}
  const t=document.getElementById("srvStat");if(t)t.textContent=ok?"server connected":"local cache (no server)";}
// ---- multi-client sync ----
// State splits into parts: "shared" (everything but per-browser UI keys + roster) and
// "board:<id>" per player. Only changed parts are written, each against the version it
// was based on; a stale write gets 409 and is 3-way merged. Polling pulls others' edits.
const LOCAL_KEYS=new Set(["active","view","theme","themeV","shape","pursuitView"]);
const POLL_MS=2500;
const SYNC={ready:false,rev:0,base:{},ver:{},pushing:false,dirty:false};
function clone(o){return o===undefined?undefined:JSON.parse(JSON.stringify(o));}
function jeq(a,b){return JSON.stringify(a)===JSON.stringify(b);}
function isObj(o){return o!==null&&typeof o==="object"&&!Array.isArray(o);}
// 3-way merge: keep local edits, take remote edits, numeric fields combine deltas
function merge3(b,l,r){
  if(jeq(l,b))return clone(r);
  if(jeq(r,b))return clone(l);
  if(isObj(l)&&isObj(r)){const out={},bb=isObj(b)?b:{};
    new Set([...Object.keys(l),...Object.keys(r),...Object.keys(bb)]).forEach(k=>{
      const v=merge3(bb[k],l[k],r[k]);if(v!==undefined)out[k]=v;});return out;}
  if(typeof l==="number"&&typeof r==="number"&&typeof b==="number")return r+(l-b);
  return clone(l);
}
function splitD(){
  const parts={},shared={roster:{}};
  Object.keys(D).forEach(k=>{if(!LOCAL_KEYS.has(k)&&k!=="players")shared[k]=D[k];});
  D.players.forEach(p=>{shared.roster[String(p.id)]={name:p.name,color:p.color};parts["board:"+p.id]=p.board;});
  parts.shared=shared;return clone(parts);
}
function joinD(parts){
  const act=(D.players[D.active]||{}).id,sh=parts.shared||{};
  const preAct={};(D.players||[]).forEach(p=>{try{preAct[p.id]=actSnap(p.board);}catch(e){}});
  const preSh=JSON.stringify([D.renown,D.season]);
  Object.keys(D).forEach(k=>{if(!LOCAL_KEYS.has(k))delete D[k];});
  Object.keys(sh).forEach(k=>{if(k!=="roster")D[k]=clone(sh[k]);});
  const ids=Object.keys(sh.roster||{}).sort((a,b)=>(+a)-(+b));
  D.players=ids.map(id=>({id:isNaN(+id)?id:+id,name:sh.roster[id].name,color:sh.roster[id].color,
    board:clone(parts["board:"+id])||newBoard()}));
  normalizeD();
  const ix=D.players.findIndex(p=>p.id===act);D.active=ix>=0?ix:Math.min(D.active||0,D.players.length-1);
  actJoin(preAct,preSh);
  undoRebase();
}
async function apiRaw(method,path,body){
  try{
    const h={};if(body!==undefined)h["Content-Type"]="application/json";if(TOKEN)h["X-Renown-Token"]=TOKEN;
    const r=await fetch(path,{method,headers:h,body:body!==undefined?JSON.stringify(body):undefined});noteServerDate(r);
    if(r.status===401){setOnline(false);const t=document.getElementById("srvStat");if(t)t.textContent="unauthorized — check access token";return null;}
    setOnline(true);
    return {status:r.status,json:await r.json().catch(()=>null)};
  }catch(e){setOnline(false);return null;}
}
// save() commits a mutation: chronicle diff, undo step, activity log, localStorage, debounced server push.
// render() never saves. A handler that changes D without calling save() is caught by saveIfDirty after the event.
let _saveT=null,_savedSig=null;
function save(){
  try{chronTick();}catch(e){}
  try{(D.players||[]).forEach(p=>glogSync(p.board));}catch(e){}
  undoRecord();if(!ACT.saving)actSchedule();
  try{_savedSig=JSON.stringify(D);localStorage.setItem("renown_dash",_savedSig);}catch(e){}
  clearTimeout(_saveT);_saveT=setTimeout(push,400);
}
function saveIfDirty(){let s=null;try{s=JSON.stringify(D);}catch(e){return;}if(s!==_savedSig)save();}
{let t=null;const later=()=>{clearTimeout(t);t=setTimeout(saveIfDirty,60);};
  ["click","change","input","pointerup","keyup","drop"].forEach(ty=>document.addEventListener(ty,later));}
async function push(){
  if(!SYNC.ready)return;
  if(SYNC.pushing){SYNC.dirty=true;return;}
  SYNC.pushing=true;SYNC.dirty=false;
  try{
    for(let attempt=0;attempt<5;attempt++){
      const parts=splitD();let conflict=false;
      const keys=new Set([...Object.keys(parts),...Object.keys(SYNC.base)]);
      for(const k of keys){
        const del=!(k in parts);
        if(!del&&jeq(parts[k],SYNC.base[k]))continue;
        const res=del?await apiRaw("DELETE","/api/part/"+encodeURIComponent(k),{base:SYNC.ver[k]||0})
                     :await apiRaw("PUT","/api/part/"+encodeURIComponent(k),{data:parts[k],base:SYNC.ver[k]||0});
        if(!res)return;                                   // offline: localStorage still holds it
        if(res.status===200){
          if(del){delete SYNC.base[k];delete SYNC.ver[k];}
          else{SYNC.base[k]=parts[k];SYNC.ver[k]=res.json.version;}
        }else if(res.status===409){                       // someone wrote first: merge, retry
          const srv=res.json.data===null?undefined:res.json.data;
          const merged=merge3(SYNC.base[k],del?undefined:parts[k],srv);
          if(merged&&srv&&k.startsWith("board:")&&srv.claim&&!jeq(srv.claim,(SYNC.base[k]||{}).claim))merged.claim=clone(srv.claim);   // first claim wins
          SYNC.base[k]=srv;SYNC.ver[k]=res.json.version;
          if(srv===undefined){delete SYNC.base[k];delete SYNC.ver[k];}
          const cur=splitD();if(merged===undefined)delete cur[k];else cur[k]=merged;
          joinD(cur);conflict=true;
        }
      }
      if(!conflict)break;
      reindex();render();
    }
  }finally{SYNC.pushing=false;if(SYNC.dirty)push();}
}
function editing(){const a=document.activeElement;
  return a&&!a.closest("#chatDock")&&(a.tagName==="TEXTAREA"||a.tagName==="SELECT"||(a.tagName==="INPUT"&&!["button","checkbox","radio","color","file"].includes(a.type)));}
async function poll(){
  if(!SYNC.ready||SYNC.pushing||editing())return;
  const res=await apiRaw("GET","/api/state?since="+SYNC.rev);
  if(!res||res.status!==200||!res.json||!res.json.changed)return;
  if(SYNC.pushing||editing())return;                  // user acted while request was in flight
  const j=res.json,cur=splitD();let touched=false;
  Object.keys(j.parts).forEach(k=>{const srv=j.parts[k];
    if(SYNC.ver[k]===srv.version)return;
    const m=merge3(SYNC.base[k],cur[k],srv.data);
    SYNC.base[k]=clone(srv.data);SYNC.ver[k]=srv.version;
    if(!jeq(m,cur[k])){cur[k]=m;touched=true;}});
  Object.keys(SYNC.base).forEach(k=>{if(!j.keys.includes(k)){          // removed remotely
    const unchanged=jeq(cur[k],SYNC.base[k]);delete SYNC.base[k];delete SYNC.ver[k];
    if(unchanged&&k in cur){delete cur[k];touched=true;}}});
  SYNC.rev=j.rev;
  if(touched){joinD(cur);reindex();render();renderList();}
  if(!jeq(splitD(),SYNC.base))save();
}
function cvar(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim();}
function fmt(n){return (n>0?"+":"")+Math.round(n).toLocaleString();}
function cap(s){return s.charAt(0).toUpperCase()+s.slice(1);}

// ---- settlement / ward helpers ----
// a new Settlement under construction has no effects until built; an upgrade keeps its old tier (s.up = {to}) until its Build Timer ends
function settUnbuilt(s){return !!s&&s.bt>0&&!s.up;}
function unbuiltMeta(t){return Object.assign({},(DATA.settlements||{})[t]||{},{wards:0,tax_income:0,muster_limit:0,reach:0,aura:0});}
function settMeta(sid){const s=S.settlements.find(x=>x.id===sid);return s?(settUnbuilt(s)?unbuiltMeta(s.tier):DATA.settlements[s.tier]):null;}
function pinSettCell(p,s){if(!p||!s)return;const k=settHex(p,s);if(k){const c=mapState().cells[k];if(c&&c.sid==null)c.sid=s.id;}}
function settExpand(p,s,nt){const t=gameStarted()?settBuildTime(nt):0;pinSettCell(p,s);if(t>0){s.up={to:nt};s.bt=t;}else s.tier=nt;}
function settFinish(p,s){if(!s.up)return "finished "+(s.name||s.tier||"settlement");
  const k=p?settHex(p,s):null,from=s.tier;s.tier=s.up.to;delete s.up;
  if(k){const c=mapState().cells[k];if(c){c.type=s.tier;c.sid=s.id;}}return "upgraded "+(s.name||from)+" → "+s.tier;}
function settTier(sid){const s=S.settlements.find(x=>x.id===sid);return s?s.tier:null;}
function occupants(sid){return S.placed.filter(p=>p.sid===sid);}
function hamletOK(name){return NATURAL.has(name);}   // Hamlets take Natural Pursuits only (riders included: a rider must be Natural too)
// SIMPLE: a Hamlet is started only by a Pursuit whose efficient list names "Hamlet"; anything else in a
// Hamlet must have one of its efficient parents there. Faction pursuits count as Natural.
function hamletRoot(name){return effLabel(name).some(e=>/^hamlet$/i.test(String(e)));}
function hamletFits(name,present){return hamletRoot(name)||effList(name).some(h=>present.has(h));}
// efficient forms CHAINS not branches: each pursuit hosts at most ONE efficient rider.
// exemptionsOf(occ): set of occupant ids that ride free (one rider per source), for an explicit occupant list.
// "efficient" may list several sources (efficient with ANY one of them). Each source hosts at most one rider;
// riders claim hosts newest-drop first (then oldest id), preferring the host they were dropped onto.
// entries may name a Pursuit, or a group: "Natural" (any Natural Pursuit) or a Pursuit type ("Husbandry", "Raw Materials"…)
const EFF_CACHE={};
function effList(n){if(EFF_CACHE[n])return EFF_CACHE[n];const e=(R[n]||{}).efficient,raw=Array.isArray(e)?e:(e?[e]:[]),out=[];
  raw.forEach(x=>{if(R[x])out.push(x);
    else if(/^natural$/i.test(x))Object.keys(R).filter(k=>NATURAL.has(k)).forEach(k=>out.push(k));
    else Object.keys(R).filter(k=>R[k].type===x).forEach(k=>out.push(k));});
  return EFF_CACHE[n]=out.filter((x,i,a)=>x!==n&&a.indexOf(x)===i);}
function effLabel(n){const e=(R[n]||{}).efficient;return (Array.isArray(e)?e:(e?[e]:[]));}
function exemptionsOf(occ){
  const present=new Set(occ.map(o=>o.name)),taken={__by:{}},free=new Set();free.hostOf={};
  occ.filter(o=>effList(o.name).some(h=>h!==o.name&&present.has(h)))
     .sort((a,b)=>(b.ride||0)-(a.ride||0)||a.id-b.id)
     .forEach(o=>{const loops=h=>{let c=h,g=64;while(c&&g--){if(c===o.name)return true;const rid=taken.__by[c];c=rid!=null?free.hostOf[rid]:null;}return false;};
       const hs=effList(o.name).filter(h=>h!==o.name&&present.has(h)&&!taken[h]&&!loops(h));   // no riding something that (transitively) rides you
       const h=(o.rideOn&&hs.includes(o.rideOn))?o.rideOn:hs[0];if(!h)return;taken[h]=o.id;taken.__by[o.name]=o.id;free.add(o.id);free.hostOf[o.id]=h;});
  return free;
}
function wardExemptions(sid){ return exemptionsOf(occupants(sid)); }
function isFreeRider(p){ return p.sid!=null && wardExemptions(p.sid).has(p.id); }
function wardUse(sid){ // {cap, used, free, typeBad}
  const meta=settMeta(sid), cap=meta?meta.wards:0, occ=occupants(sid), tier=settTier(sid);
  const exempt=exemptionsOf(occ);
  let typeBad=false;const badNames=[];
  if(SIMPLE){const present=new Set(occ.map(o=>o.name));occ.forEach(p=>{if(tier==="Hamlet"&&!hamletFits(p.name,new Set([...present].filter(x=>x!==p.name)))){typeBad=true;badNames.push(p.name);}});}
  else occ.forEach(p=>{ if(tier==="Hamlet"&&!hamletOK(p.name)){typeBad=true;badNames.push(p.name);} });
  const used=occ.filter(o=>!o.fac&&!exempt.has(o.id)).length;   // faction pieces take no Ward
  return {cap, used, free:cap-used, typeBad,badNames};
}
// can pursuit `name` be placed into settlement sid?  simulate the resulting ward count,
// so adding a PARENT later (which lets an existing tile ride it) is allowed even when full.
function canPlace(name, sid){
  if(sid==null)return {ok:true};
  if(sid!=="faction"&&scopeOf(name)==="Settlement"&&occupants(sid).some(o=>o.name===name))return {ok:false,why:"one "+name+" per Settlement"};
  if(sid==="faction"){const sim=occupants("faction").concat([{id:1e9,name}]),ex=exemptionsOf(sim);
    return ex.has(1e9)?{ok:true,rider:true}:{ok:false,why:"not efficient with a free faction piece"};}
  const tier=settTier(sid);
  const meta=settMeta(sid), cap=meta?meta.wards:0;
  const sim=occupants(sid).concat([{id:1e9,name}]);   // hypothetical (high id → existing riders keep their slot)
  const exempt=exemptionsOf(sim);
  if(tier==="Hamlet"){
    if(SIMPLE){if(!hamletFits(name,new Set(occupants(sid).map(o=>o.name))))return {ok:false,why:"Hamlets start with "+(Object.keys(R).filter(hamletRoot).join(" / ")||"efficient-Hamlet Pursuits")+"; others need an efficient parent there"};}
    else if(!hamletOK(name))return {ok:false,why:"Hamlets hold Natural Pursuits only"};}
  const used=sim.filter(o=>!o.fac&&!exempt.has(o.id)).length;
  if(used<=cap)return {ok:true, rider:exempt.has(1e9)};
  return {ok:false, why:"no free ward slot (efficient slot taken — chains, can't branch)"};
}

// ---- uniqueness + tier progression ----
const TIER_CHAIN=["Village","Town","City","Metropolis"];
function capitalSett(){return S.settlements.find(s=>s.capital)||null;}
function setCapital(id){S.settlements.forEach(s=>{s.capital=(s.id===id);});}
// ---- era / legality flags (ERAS caps; SETTLEMENTS notes) ----
function isCityPlus(t){return TIER_CHAIN.indexOf(t)>=TIER_CHAIN.indexOf("City");}
function dbActive(b){const out=[],dv=(b||S).domains||{};[["Rising",RIS],["Established",EST],["Sovereign",SOV]].forEach(([t,th])=>
  DOMAINS.forEach(d=>{const e=DBOARD[d];if(e&&typeof e==="object"&&e[t]&&(dv[d]||0)>=th)out.push({dom:d,tier:t,name:String(e[t]).split(":")[0].trim(),text:String(e[t])});}));return out;}
// DOMAIN_BOARD "May have an additional City / Settlement / Army" → +1 to the Era cap
const DB_CAP={cities:/additional City/i,max_settlements:/additional Settlement/i,armies:/additional Army/i};
function capBonus(k,b){const re=DB_CAP[k];return re?dbActive(b).filter(x=>re.test(x.text)):[];}
function eraCapBase(k){const E=ERAS[currentEra()]||{};return typeof E[k]==="number"?E[k]:null;}
function eraCap(k){const c=eraCapBase(k);return c==null?null:c+capBonus(k).length;}
function capSrc(k){const b=capBonus(k);return b.length?" (+"+b.length+" "+b.map(x=>x.name).join(", ")+")":"";}
function cityCount(exceptId){return S.settlements.filter(s=>isCityPlus(s.up?s.up.to:s.tier)&&s.id!==exceptId).length;}
// can a settlement (id, or new when id==null) become tier t under the current Era?
function eraAllows(t,id){
  if(isCityPlus(t)&&!(id!=null&&isCityPlus(settTier(id)))){const c=eraCap("cities");
    if(c!=null&&cityCount(id)+1>c)return {ok:false,why:currentEra()+" allows "+c+" Cit"+(c===1?"y":"ies")+capSrc("cities")+(c===0?" — reach Ascension (Renown "+((ERAS.Ascension||{}).renown||"?")+") first":"")};}
  if(t==="Metropolis"&&((S.domains||{}).Industry||0)<SOV)return {ok:false,why:"Metropolis requires Sovereign Industry"};
  return {ok:true};
}
// flags that point at a rules section (rulebook anchors use the same slug as rules_payload)
const FLAG_RULE=[[/^Treasury negative/,"Insolvency & Bankruptcy"],[/^Charter:/,"Chartering Settlements"],[/Muster Field/,"Mustering"]];
function rslug(t){return "rb-"+String(t).toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");}
function boardFlags(){
  const f=[],era=currentEra();
  const cc=cityCount(),cCap=eraCap("cities");if(cCap!=null&&cc>cCap)f.push("Cities "+cc+" / "+cCap+" allowed in "+era+capSrc("cities"));
  const sCap=eraCap("max_settlements");if(sCap!=null&&S.settlements.length>sCap)f.push("Settlements "+S.settlements.length+" / "+sCap+" allowed in "+era+capSrc("max_settlements"));
  {const pl=playerOfBoard(S);if(pl)(S.settlements||[]).forEach(st=>{const n=armiesInside(pl,st).length;if(n>1)f.push((st.name||st.tier)+": "+n+" Armies inside (1 allowed)");});}
  pendingOf(S).forEach(x=>f.push(x.act+" performed (turn "+x.turn+") — "+x.msg));
  const aCap=eraCap("armies");if(aCap!=null&&S.armies.length>aCap)f.push("Armies "+S.armies.length+" / "+aCap+" allowed in "+era+capSrc("armies"));
  if(!capitalSett())f.push("No capital set");
  if((S.treasury||0)<0)f.push("Treasury negative — Insolvency");
  {const me=playerOfBoard(S);if(me){charterFlags(me).forEach(x=>f.push(x));
    if((S.armies||[]).some(a=>a.muster&&a.muster.n>0)&&!hasMusterField(S))f.push("Mustering without an active Muster Field");
    srcMatch(S,"no_alliance").forEach(x=>{if(D.players.some(q=>sameAlliance(String(q.id),String(me.id))))f.push(x.n+": can't be in an Alliance");});}}
  if(S.settlements.filter(s=>s.tier==="Metropolis").length>1)f.push("More than one Metropolis");
  {const nm=[...new Set(S.placed.filter(q=>scopeOf(q.name)==="Realm").map(q=>q.name).concat(Object.keys(S.wonders||{})))];
    nm.forEach(n=>{const h=realmHolder(n);if(h)f.push(n+": "+h.name+" also has it (Realm — one per game)");});
    S.settlements.forEach(s=>{const c={};occupants(s.id).forEach(o=>{if(scopeOf(o.name)==="Settlement")c[o.name]=(c[o.name]||0)+1;});
      Object.keys(c).forEach(n=>{if(c[n]>1)f.push((s.name||s.tier)+": "+c[n]+"× "+n+" (one per Settlement)");});});
    const cnt={};S.placed.filter(q=>scopeOf(q.name)!=="Settlement").forEach(q=>{cnt[q.name]=(cnt[q.name]||0)+1;});
    Object.keys(cnt).forEach(n=>{if(cnt[n]>1)f.push(cnt[n]+"× "+n+" (one per "+(scopeOf(n)==="Realm"?"game":"player")+")");});}
  factionFlags().forEach(x=>f.push(x));
  {const T=exTargets(S),n=extortSlots(S).filter(x=>!T[x.key]).length;if(n)f.push("Extort: "+n+" target"+(n>1?"s":"")+" not chosen (Table ▸ Extort targets)");}
  (S.loanDefaults||[]).forEach(x=>{const t=loanTerms(S);f.push("Loan default (turn "+x.turn+"): "+pname(x.pid)+" — Perform "+(t?t.def:"Demand Tribute"));});
  dbActive(S).forEach(x=>{const m=/(?:^|[.:]\s*)(Perform [^.]+)\./.exec(x.text);if(m)f.push(x.name+" ("+x.tier+" "+x.dom+"): "+m[1]);});
  {const pf=poFloor(S);if(pf&&(S.po||0)<pf.below)f.push("Public Order "+(S.po||0)+" below "+pf.src+" floor "+pf.to);}
  const m=S.settlements.find(s=>s.tier==="Metropolis");
  if(m&&!m.capital)f.push("Metropolis is not the capital (capital only)");
  if(m&&((S.domains||{}).Industry||0)<SOV)f.push("Metropolis without Sovereign Industry");
  S.settlements.forEach(s=>{const wu=wardUse(s.id);if(wu.typeBad)f.push(s.tier+": "+wu.badNames.join(", ")+(wu.badNames.length>1?" aren't":" isn't")+" Natural — Hamlets hold Natural Pursuits only");});
  S.settlements.forEach(s=>{const w=wardUse(s.id);if(w.free<0)f.push(s.tier+": "+(-w.free)+" ward(s) over cap");});
  Object.keys(S.infra).forEach(n=>{const st=infraReqStatus(INFRA[n]);if(!st.ok)f.push(n+": req unmet ("+st.missing.join(", ")+")");});
  Object.keys(S.wonders).forEach(n=>{const st=infraReqStatus(WON[n]);if(!st.ok)f.push(n+": req unmet ("+st.missing.length+" infra missing/invalid)");});
  return f;
}
function onBoard(name){return S.placed.some(p=>p.name===name);}      // one of each name, anywhere
// Scope (rarity): Settlement = one per Settlement · Empire = one per player · Realm = one per game (placed or building counts)
function scopeOf(n){return ((R[n]||INFRA[n]||WON[n]||{}).scope)||"Empire";}
function realmHolder(n,b){b=b||S;return D.players.find(q=>q.board!==b&&((q.board.placed||[]).some(x=>x.name===n)||!!(q.board.infra||{})[n]||!!(q.board.wonders||{})[n]))||null;}
function scopeBlock(n,sid){const sc=scopeOf(n);
  if(sc==="Realm"){const h=realmHolder(n);if(h)return n+": "+h.name+" has it (Realm — one per game)";}
  if(sc==="Settlement")return sid!=null&&occupants(sid).some(o=>o.name===n)?n+": already in this Settlement (one per Settlement)":"";
  if(R[n]&&onBoard(n))return n+" already on board (one per "+(sc==="Realm"?"game":"player")+")";
  return "";}
function nextTier(t){const i=TIER_CHAIN.indexOf(t);return i>=0&&i<TIER_CHAIN.length-1?TIER_CHAIN[i+1]:null;}
// place any Unplaced pursuits into free ward slots (called after adding/expanding a settlement)
function autoFill(){
  let moved=true;
  while(moved){
    moved=false;
    const unplaced=S.placed.filter(p=>p.sid==null);
    for(const p of unplaced){
      for(const s of S.settlements){
        const c=canPlace(p.name,s.id);
        if(c.ok){p.sid=s.id;moved=true;break;}
      }
    }
  }
}

