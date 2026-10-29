// ===================== TABLE: seating, Council & Envoy phases =====================
// Everything the sequence needs is derived (tSim) from: shared D.tbl (seats, host, phase, phase start,
// timer, host overrides) + each player's own board.tbl (seat, council vote, declaration, votes, mods).
// Each client writes only its own board part (hot-seat excepted); the Host alone writes D.tbl.
const T_DOMS=["Prowess","Cunning","Piety","Industry"];                 // resolution order after Diplomacy
const T_ALL=["Diplomacy"].concat(T_DOMS);
const EOUT=DATA.envoyOutcomes||{};
const ETH=Object.assign({Condemned:-3,Failed:0,Passed:1,Endorsed:3},DATA.outcomeThresh||{});
const T_PH=["empire","council","envoy","battle","rest"];
const T_PHL={empire:"Empire Phase",council:"Council Phase",envoy:"Envoy Phase",battle:"Battle Phase",rest:"Rest Phase"};
let SKEW=0,SKEW_N=0;                                                    // server clock − local clock (ms)
function tnow(){return Date.now()+SKEW;}
function noteServerDate(r){try{const d=Date.parse(r.headers.get("date")||"");if(isNaN(d))return;
  const s=d+500-Date.now();SKEW=SKEW_N?Math.round(SKEW*0.8+s*0.2):s;SKEW_N++;}catch(e){}}
let HOTSEAT=false;try{HOTSEAT=localStorage.getItem("renown_hotseat")==="1";}catch(e){}
// The Duke (admin; per browser session): acts for anyone and has every Host control. Unlocked by the server's RENOWN_DUKE_PIN.
let ADMIN=false;try{ADMIN=sessionStorage.getItem("renown_admin")==="1";}catch(e){}
// ---- player claims (server games): a device claims one player; only that device, or the Duke, can change that player.
// A device with no claim is a spectator. Off-server (local file) nothing is locked.
let DEV="";try{DEV=localStorage.getItem("renown_dev")||"";if(!DEV){DEV=Math.random().toString(36).slice(2,10)+Date.now().toString(36);localStorage.setItem("renown_dev",DEV);}}catch(e){DEV="t"+Math.random().toString(36).slice(2,10);}
function lockOn(){try{return !!SYNC.ready&&!ADMIN&&!!D.started;}catch(e){return false;}}   // restrictions begin at Start game
function claimOf(p){return (p&&p.board&&p.board.claim)||null;}
function mine(p){const c=claimOf(p);return !!c&&c.dev===DEV;}
function myClaimP(){return (D.players||[]).find(mine)||null;}
function canEdit(p){return !lockOn()||mine(p);}

function boardEndOn(){return TB().boardEnd!==false;}   // default ON
function TB(){D.tbl=D.tbl||{};D.tbl.skip=D.tbl.skip||{};return D.tbl;}
// seat count: the Host's setting, never below the players in the game; unset = one seat per player (or up to the highest taken seat)
function seatFloor(){return Math.max(1,D.players.length);}
function tSeats(){const v=+TB().seats;if(v)return Math.max(v,seatFloor());let hi=0;D.players.forEach(p=>{const s=PT(p).seat;if(Number.isInteger(s))hi=Math.max(hi,s+1);});return Math.max(seatFloor(),hi);}
function tTimer(){const v=TB().timer;return v===undefined?20:Math.max(0,+v||0);}
function tTurn(){return +TB().turn||1;}
function tBegun(){return tTurn()>1||!!TB().begun;}   // set when the Host begins Turn 1's first phase
function tPhase(){const t=TB();if(T_PH.includes(t.phase))return t.phase;
  const sp=String(DATA.startPhase||"Council").toLowerCase();return T_PH.includes(sp)?sp:"council";}
function PT(p){const b=p.board;b.tbl=b.tbl||{};b.tbl.mods=b.tbl.mods||{};return b.tbl;}
function tCur(p){const x=PT(p);return (x.cur&&x.cur.turn===tTurn())?x.cur:{turn:tTurn(),votes:{}};}
function tCurW(p){const x=PT(p);if(!x.cur||x.cur.turn!==tTurn())x.cur={turn:tTurn(),votes:{}};x.cur.votes=x.cur.votes||{};return x.cur;}
function sameP(a,b){return !!a&&!!b&&String(a.id)===String(b.id);}
function meP(){return (lockOn()&&myClaimP())||D.players[D.active];}
function canAct(p){return HOTSEAT||ADMIN||(lockOn()?mine(p):sameP(meP(),p));}

// ---- seating (seat index increases clockwise; ties on a seat go to whoever sat first) ----
function seatMap(){const n=tSeats(),m={};
  D.players.map(p=>({p,x:PT(p)})).filter(o=>Number.isInteger(o.x.seat)&&o.x.seat>=0&&o.x.seat<n)
    .sort((a,b)=>(a.x.seatTs||0)-(b.x.seatTs||0)||String(a.p.id).localeCompare(String(b.p.id)))
    .forEach(o=>{if(!m[o.x.seat])m[o.x.seat]=o.p;});return m;}
function seated(){const m=seatMap();return Object.keys(m).map(Number).sort((a,b)=>a-b).map(i=>m[i]);}
function isSpring(){return curSeason()==="Spring";}   // SEASONS.Spring: no Host, Council Phase, Diplomacy actions or Influence gain
function hostP(){const s=seated();return s.find(p=>String(p.id)===String(TB().host))||s[0]||null;}
// "You always vote last, after the Host" (Whispering Undercroft): holders move behind the Host, keeping their relative order
// players who vote in the Tally Phase (Whispering Undercroft) go last on an Envoy voted then (a Forgery Workshop retry)
function voteOrd(ord){const last=ord.filter(p=>fxOf(p,"voteLast").length||tallyVoter(p));return last.length?ord.filter(p=>!last.includes(p)).concat(last):ord;}
function tOrder(){const s=seated();if(!s.length)return [];const i=s.indexOf(hostP());return s.slice(i+1).concat(s.slice(0,i+1));}
function canHost(){const h=hostP();return HOTSEAT||ADMIN||(!h&&(!lockOn()||!!myClaimP()))||(!!h&&(lockOn()?mine(h):sameP(meP(),h)));}
function seatsLocked(){if(ADMIN)return false;const ph=tPhase();return (ph==="council"||ph==="envoy")&&!!TB().phaseTs;}

// ---- influence, standings, envoys ----
function tStand(p,dom){return domBand((p.board.domains||{})[dom]||0);}
function eraRec(){return ERAS[currentEra()]||{};}
function diploInf(){const e=eraRec();return e.innate_diplomacy_influence??(eraIdx()+1);}
function diploCap(){const e=eraRec();return e.max_influence_per_diplomacy_vote??diploInf();}
function eraActions(council){const e=eraRec();return Math.max(1,+(council?e.council_actions_per_envoy:e.actions_per_envoy)||1);}
// an Envoy that performs more than one action this Era: the Envoy itself is action 1; actions 2..n are copies with id "<id>#<k>",
// each with its own Perform record, offered once the action before it has been performed
function envSlots(E){if(E.slot||!(E.out==="Passed"||E.out==="Endorsed"))return [];const n=eraActions(E.council);
  const L=Array.from({length:n-1},(_,i)=>Object.assign({},E,{id:E.id+"#"+(i+2),slot:i+2,slots:n,base:E}));
  const b=endorsedBonus(E);if(b)L.push(Object.assign({},E,{id:E.id+"#"+(n+1),slot:n+1,slots:n,base:E,bonus:b,out:"Passed"}));
  return L;}
// Endorsed "Perform a <Domain|action> action" (ENVOY_OUTCOMES / the action's own endorsed text): one more action after the Envoy's own,
// offered as the next slot once those are performed. It is Passed, never Endorsed again. → {dom} or {act}, or null
function endorsedBonus(E){const pe=performEval(E);if(!pe||pe.out!=="Endorsed")return null;const A=(DATA.actions||{})[pe.rec.action]||{};
  const m=/Perform (?:another|an?) (\w+) action/i.exec(String(A.endorsed||((EOUT[E.dom]||{}).endorsed)||""));if(!m)return null;
  const w=m[1].toLowerCase(),dom=["Prowess","Cunning","Piety","Industry","Diplomacy"].find(d=>d.toLowerCase()===w);
  if(dom)return {dom};const act=Object.keys(DATA.actions||{}).find(a=>a.toLowerCase()===w);return act?{act}:null;}
function slotLabel(E){return E.bonus?" · Endorsed: "+(E.bonus.dom?"a "+E.bonus.dom:E.bonus.act)+" action":E.slot?" · action "+E.slot+"/"+E.slots:"";}
function slotOpen(X){const r=((tCur(X.owner).perform)||{})[X.slot>2?X.base.id+"#"+(X.slot-1):X.base.id];return !!r&&(!!r.action||!!r.failAccept)&&!r.edit;}
function withSlots(L){return L.flatMap(E=>[E].concat(envSlots(E).filter(slotOpen)));}
// ---- Pursuit / Infrastructure effects on Envoys (parsed server-side into innate_fx / mastery_fx / fx) ----
const FX_CACHE={};
function boardFx(p){if(!p)return [];const b=p.board;
  const key=JSON.stringify([b.placed||[],b.infra||{},b.wonders||{},b.facInfra||[],b.domains||{},b.faction||"",(b.tbl||{}).studiumEffects||{}]);
  const c=FX_CACHE[p.id];if(c&&c.key===key)return c.fx;
  const fx=withBoard(b,()=>{const have=new Set(Object.keys(PC));const {earned}=computeEarned(have),L=[];
    Object.keys(PC).forEach(n=>{const r=R[n]||{},q=PC[n];
      (r.innate_fx||[]).forEach(f=>L.push(Object.assign({src:n,q},f)));
      if(earned[n])(r.mastery_fx||[]).forEach(f=>L.push(Object.assign({src:n+" (Mastery)",q},f)));});
    Object.keys(S.infra||{}).filter(infraOn).forEach(n=>((INFRA[n]||{}).fx||[]).forEach(f=>L.push(Object.assign({src:n,q:1},f))));
    Object.keys(S.wonders||{}).filter(infraOn).forEach(n=>((WON[n]||{}).fx||[]).forEach(f=>L.push(Object.assign({src:n,q:1},f))));
    ((FAC[S.faction||""]||{}).fx||[]).forEach(f=>L.push(Object.assign({src:S.faction,q:1},f)));
    dbActive(b).forEach(x=>(((DATA.domainBoardFx||{})[x.dom]||{})[x.tier]||[]).forEach(f=>L.push(Object.assign({src:x.free?"Studium Generale · "+x.name:x.name,q:1},f))));   // unlocked Standing effects
    return L;});
  FX_CACHE[p.id]={key,fx};return fx;}
function fxOf(p,k){return boardFx(p).filter(f=>f.k===k);}
function scopeOk(f,council){return !f.scope||f.scope==="all"||(f.scope==="council")===!!council;}
function sgn(v){return (v<0?"\u2212":"+")+Math.abs(v);}
function fxLabel(f){const v=f.val*(f.q||1);
  if(f.k==="envoy")return sgn(v)+" Influence to "+(f.scope==="council"?"Council ":f.scope==="personal"?"Personal ":"")+(f.dom==="All"?"":f.dom+" ")+"Envoys";
  if(f.k==="cap")return "Max Influence "+sgn(v);
  if(f.k==="act")return sgn(v)+" Influence to your "+f.dom+" actions (on Perform)";
  if(f.k==="defend")return sgn(v)+" Influence to "+(f.dom?f.dom+" actions":f.action)+" targeting you (on Perform)";
  if(f.k==="pool")return sgn(v)+" Influence/turn "+({Rising:"per Rising+ Domain",Established:"per Established+ Domain",others:"per other player",war:"while At War"}[f.per]||"");
  if(f.k==="jester")return (f.n===1?"First":"Second")+" Oppose on your Envoys: −"+f.val;
  if(f.k==="noOppose")return "No Oppose on your "+f.dom+" Envoys"+(f.lower?" from players with lower "+f.lower:"");
  if(f.k==="failPass")return "Your Failed "+(f.dom?f.dom+" ":"")+"Envoys pass instead (not Condemned)";
  if(f.k==="noEndorse")return f.dom+" actions targeting you can't be Endorsed";
  if(f.k==="voteLast")return "You vote last (after the Host)";
  if(f.k==="capAs")return "Your "+f.dom+" Standing rank sets your Max Influence on "+f.for+" Envoys";
  if(f.k==="domAs")return "Your "+f.dom+" Standing sets the innate "+SCORE+" of your "+((f.for||"All")==="All"?"Domain":f.for)+" Envoys";
  if(f.k==="instead")return (f.notFrom?"non-"+f.from:f.from)+" Envoy "+f.outs.join(" / ")+": may perform a "+f.to+" action instead"+(f.once?" (once per "+(f.once==="turn"?"turn":T_PHL[f.once]||f.once)+")":"");
  if(f.k==="noAlliance")return "Can't be in an Alliance";
  return f.k;}
function atWarPair(a,b){if(!a||!b)return false;return !!effPair(a.id,b.id).war;}
function opposeBlock(v,E){  // reason v can't Oppose E, or ""
  if(E.dom==="Industry"&&!atWarPair(v,E.owner))return "Ulterior Motive: only while at war with "+E.owner.name;
  {const f=fxOf(E.owner,"noOppose").find(f=>f.dom===E.dom&&(!f.lower||((v.board.domains||{})[f.lower]||0)<((E.owner.board.domains||{})[f.lower]||0)));
   if(f)return f.src+": can't Oppose"+(f.lower?" (lower "+f.lower+")":"");}
  return "";}
// Standing that sets an Envoy's innate value: its own Domain, unless an effect substitutes another ("domAs", e.g. Double Speak:
// "Your Diplomacy Envoys use your Cunning Standing"). Diplomacy Envoys otherwise keep their Era value (they have no Domain value).
function domAsFx(p,dom){return fxOf(p,"domAs").find(f=>(f.for||"All")===dom||((f.for||"All")==="All"&&dom!=="Diplomacy"))||null;}
function innateParts(p,dom,council){const f0=domAsFx(p,dom),idom=f0?f0.dom:dom,era=dom==="Diplomacy"&&!f0;
  const parts=[{src:era?currentEra()+" (Era)":tStand(p,idom)+(f0?" "+idom+" ("+f0.src+")":""),val:era?diploInf():((DBOARD.innate_influence_own_envoys||{})[tStand(p,idom)]||0)}];
  fxOf(p,"envoy").filter(f=>(f.dom==="All"||f.dom===dom)&&scopeOk(f,council)&&!(f.noSpring&&isSpring())).forEach(f=>parts.push({src:f.src,val:f.val*f.q}));
  D.players.forEach(q=>{if(sameP(q,p)||!sameAlliance(String(q.id),String(p.id)))return;fxOf(q,"allyEnvoy").filter(f=>scopeOk(f,council)).forEach(f=>parts.push({src:q.name+": "+f.src,val:f.val*f.q}));});
  Object.values(PT(p).mods).filter(m=>m&&m.kind==="envoy"&&(m.dom==="All"||m.dom===dom)&&scopeOk(m,council)).forEach(m=>parts.push({src:m.label||"manual",val:+m.val||0}));
  return parts;}
function modSum(p,kind,dom,council){return Object.values(PT(p).mods).filter(m=>m&&m.kind===kind&&(m.dom==="All"||m.dom===dom)&&(!m.scope||m.scope==="all"||(m.scope==="council")===!!council))
  .reduce((a,m)=>a+(+m.val||0),0);}
function innateInf(p,dom,council){return innateParts(p,dom,council).reduce((a,x)=>a+x.val,0);}
function voteCap(p,dom,council){const ca=fxOf(p,"capAs").find(f=>f.for===dom),base=ca?((DBOARD.max_influence_per_vote||{})[tStand(p,ca.dom)]||0):dom==="Diplomacy"?diploCap():((DBOARD.max_influence_per_vote||{})[tStand(p,dom)]||0);
  const v=Math.max(0,base+modSum(p,"cap",dom,council)+fxOf(p,"cap").reduce((a,f)=>a+f.val*f.q,0));
  const ce=fxOf(p,"capEra").filter(f=>f.era===currentEra()).reduce((a,f)=>Math.max(a,f.val),0);return Math.max(v,ce);}
function inflPool(p){const c=PT(p).carry;return influenceTotal(p.board)+(+tCur(p).inflAdj||0)+(c&&c.turn===tTurn()?+c.n||0:0);}
function personalEnvoys(p){const e=eraRec(),nx=PT(p).envNext;return Math.max(0,(+e.personal_envoys||1)+(+tCur(p).envAdj||0)+(nx&&nx.turn===tTurn()?+nx.n||0:0));}
function councilEnvoys(){return Math.max(0,+eraRec().council_envoys||1);}
function tOutcome(net){if(net<=ETH.Condemned)return "Condemned";if(net<=ETH.Failed)return "Failed";
  if(net>=ETH.Endorsed)return "Endorsed";return "Passed";}
function outText(dom,out){return ((EOUT[dom]||{})[String(out).toLowerCase()])||"";}

// ---- the plan: ordered envoys for the current phase ----
function tPlan(ph,ord,councilDom){const L=[];
  if(ph==="council"&&isSpring())return L;
  if(ph==="council"){const nc=councilEnvoys();ord.forEach(p=>{if(fxOf(p,"noCouncil").length)return;for(let k=0;k<nc;k++)L.push({id:"C:"+p.id+(k?":"+k:""),owner:p,dom:councilDom||null,council:true,k});});return L;}
  if(ph!=="envoy"||!ord.every(p=>(tCur(p).decl||{}).lock))return L;
  const cnt=(p,d)=>Math.max(0,+(((tCur(p).decl||{}).n||{})[d])||0);
  if(!isSpring())ord.forEach(p=>{for(let k=0;k<cnt(p,"Diplomacy");k++)L.push({id:"E:"+p.id+":Diplomacy:"+k,owner:p,dom:"Diplomacy",k});});
  // Diplomatic Mission: an extra Envoy in another Domain, sent after a Diplomacy Envoy (rules: Rule: Diplomatic Mission)
  const dip=new Set(L.map(E=>E.id));   // the source Envoy must exist this turn (its Failed outcome is checked when the Mission is chosen)
  const mis=p=>Object.entries(tCur(p).mission||{}).filter(([src,d])=>T_DOMS.includes(d)&&dip.has(src)).map(([src,d])=>({src,d}));
  T_DOMS.forEach(d=>{ord.slice().sort((a,b)=>((b.board.domains||{})[d]||0)-((a.board.domains||{})[d]||0)||ord.indexOf(a)-ord.indexOf(b))
    .forEach(p=>{for(let k=0;k<cnt(p,d);k++)L.push({id:"E:"+p.id+":"+d+":"+k,owner:p,dom:d,k});
      mis(p).filter(m=>m.d===d).forEach(m=>L.push({id:"M:"+m.src,owner:p,dom:d,k:0,mission:m.src}));});});
  ord.forEach(p=>{const f=PT(p).forgeRetry;if(!f||f.turn!==tTurn())return;const i=L.findIndex(E=>E.id===f.from&&sameP(E.owner,p));if(i<0)return;
    L.splice(i+1,0,{id:"FR:"+f.from,owner:p,dom:"Cunning",k:0,retry:true,excludeTarget:f.excludeTarget||""});});
  return L;}
// a Domain's Envoys have started voting once any of them is resolved or current
// Diplomatic Mission (RULES › Rule: Diplomatic Mission): the Diplomacy Envoy passed or was endorsed but its action failed —
// after post-Envoy modifiers, or declined at the table (no one signs). A Failed / Condemned Envoy allows none.
function missionWhy(E2){if(!E2||E2.dom!=="Diplomacy"||!(E2.out==="Passed"||E2.out==="Endorsed"))return "";
  const rec=((tCur(E2.owner).perform)||{})[E2.id]||{};if(rec.declined)return "action declined";
  const pe=performEval(E2);return pe&&(pe.out==="Failed"||pe.out==="Condemned")?"action "+pe.out.toLowerCase():"";}
function domStarted(R,d){return R.envoys.some(E=>E.dom===d&&!E.council&&(E.done||R.curEnvoy===E));}
function whisperEligibleEnvoys(R){return (R.plan||[]).filter(E=>!E.council&&!PT(E.owner).whisperDeclare&&!(((tCur(E.owner).perform||{})[E.id]||{}).whisperLock));}

// ---- simulation: walk every slot in order, apply pre-votes / timeouts, stop at the first open slot ----
function tSim(){
  const t=TB(),ph=tPhase(),ord=tOrder(),now=tnow(),TM=tTimer()*1000;
  const R={ph,ord,log:[],envoys:[],cur:null,curEnvoy:null,spent:{},pool:{},resolved:new Set(),plan:[],councilDom:null,selfSup:{},stage:""};
  ord.forEach(p=>{R.spent[p.id]=0;R.pool[p.id]=inflPool(p);});
  if(ph!=="council"&&ph!=="envoy"){R.done=true;return R;}
  if(ph==="council"&&isSpring()){R.done=true;R.spring=true;return R;}
  if(!ord.length){R.waiting="seat";return R;}
  if(!t.phaseTs){R.waiting="start";return R;}
  let clock=t.phaseTs;
  function runSlot(key,who,rec){
    const start=clock,ov=(t.deadlines||{})[key],ext=(t.extraTime||{})[key]||0,dl=ov!=null?+ov:(TM>0?start+TM+ext:Infinity),sk=t.skip[key];let res=null;
    if(rec&&rec.ts<=start)res={rec,end:start,pre:true};
    else if(rec&&rec.ts<=dl&&!(sk&&sk>=start&&rec.ts>sk))res={rec,end:rec.ts};
    else if(sk&&sk>=start)res={rec:null,end:sk,forced:true};
    else if(PT(who).auto)res={rec:null,end:start,auto:true};
    else if(now>=dl)res={rec:null,end:dl,timeout:true};
    if(!res){R.cur={key,who,start,deadline:dl};return null;}
    R.resolved.add(key);clock=Math.max(clock,res.end);return res;}
  // one vote on E (Support / Oppose / Abstain), clamped to the voter's cap and the Influence left; the Tally Phase reuses it
  function applyVote(E,v,r){let a="A",x=0;
    if(r.rec&&(r.rec.a==="S"||r.rec.a==="O")&&!fxOf(v,"alwaysAbstain").length){
      const room=Math.max(0,R.pool[v.id]-R.spent[v.id]);
      x=Math.max(0,Math.min(+r.rec.x||0,voteCap(v,E.dom,E.council),room));a=x>0?r.rec.a:"A";
      if(a==="O"&&opposeBlock(v,E)){a="A";x=0;}}
    let eff=x;if(a==="O"){E.oppN++;const j=E.jest[E.oppN]||0;eff=Math.max(0,x-j);if(j&&x>0){const js=fxOf(E.owner,"jester").find(f=>f.n===E.oppN);(E.notes=E.notes||[]).push((js?js.src:"Jester's Court")+": "+v.name+"'s Oppose "+x+" counts "+eff);}}
    const vc=fxOf(E.owner,"voteCost").reduce((m,f)=>Math.max(m,f.val),1);   // Hermit Crown: N Influence moves the Envoy by 1
    const sx=Math.floor(x/vc);eff=Math.floor(eff/vc);
    if(a==="S")E.sup+=sx;else if(a==="O")E.opp+=eff;R.spent[v.id]+=x;
    E.votes.push({who:v,a,x,eff,pre:!!r.pre,timeout:!!r.timeout,forced:!!r.forced,auto:!!r.auto,tally:R.stage==="tally"});}
  // E's net and outcome from its votes so far (run again after every Tally Phase change)
  function finish(E){let net=E.innate+E.sup-E.opp;if(E.council)net=Math.max(1,net);       // Council Envoys can't fail
    E.net=net;E.out=tOutcome(net);delete E.saved;
    const fp=failPassFx(E);if(fp&&(E.out==="Failed"||(E.out==="Condemned"&&fp.condemned))){E.out="Passed";E.saved=fp.src;}   // Condemned only where the text says so
    if(E.council&&fxOf(E.owner,"councilEndorse").length&&(E.out==="Passed"||E.out==="Endorsed")){E.out="Endorsed";E.saved=fxOf(E.owner,"councilEndorse")[0].src;}
    if(E.endorsedBy){E.out="Endorsed";E.saved=E.endorsedBy;}                                // Tally Phase Endorse (High Chancery)
    E.done=true;}
  function envoyRun(E){
    E.innate=innateInf(E.owner,E.dom,E.council);E.votes=[];E.sup=0;E.opp=0;E.oppN=0;R.envoys.push(E);
    const courier=D.players.map(p=>({p,x:PT(p).courierTarget})).find(o=>o.x&&o.x.turn===tTurn()&&o.x.envoy===E.id);
    if(courier){E.innate-=1;(E.notes=E.notes||[]).push("Courier Network ("+courier.p.name+"): Authority −1");}
    const senate=ph==="envoy"&&!E.council&&D.players.map(p=>({p,x:PT(p).senateChoice})).find(o=>o.x&&o.x.turn===tTurn()&&o.x.envoy===E.id);
    if(senate){E.net=senate.x.out==="Condemned"?ETH.Condemned:ETH.Endorsed;E.out=senate.x.out;E.done=true;E.fixed=true;E.saved=senate.x.src;E.notes=(E.notes||[]).concat([senate.x.src+" ("+senate.p.name+"): "+senate.x.out+" in the Intrigue Phase"]);R.log.push({kind:"envoy",E});return true;}
    E.jest={};fxOf(E.owner,"jester").forEach(f=>E.jest[f.n]=(E.jest[f.n]||0)+f.val);
    (R.selfSup[E.id]||[]).forEach(s=>{E.sup+=s.x;E.votes.push({who:E.owner,a:"S",x:s.x,eff:s.x,self:true,src:s.src});});   // Intrigue Phase: Colossus
    const silent=intrigueSilenced(E);                                                    // Intrigue Phase: Clandestine Councilor
    for(const v of (E.council?[]:voteOrd(ord))){if(sameP(v,E.owner))continue;
      if(fxOf(v,"noVote").length){E.votes.push({who:v,a:"A",x:0,eff:0,auto:true});continue;}   // Council Envoys auto-Abstain: no votes
      const sl=silent.find(s=>sameP(s.who,v));if(sl){E.votes.push({who:v,a:"A",x:0,eff:0,auto:true,silenced:sl.src});continue;}
      if(!E.retry&&tallyVoter(v))continue;                                               // casts this vote in the Tally Phase
      const r=runSlot(E.id+">"+v.id,v,tCur(v).votes[E.id]);
      if(!r){R.curEnvoy=E;return false;}
      applyVote(E,v,r);}
    finish(E);R.log.push({kind:"envoy",E});return true;}
  if(ph==="council"){
    const tally={};
    for(const p of voteOrd(ord)){if(fxOf(p,"noVote").length){R.log.push({kind:"cvote",who:p,dom:null,auto:true});continue;}
      const r=runSlot("CV:"+p.id,p,tCur(p).council);if(!r)return R;
      const d=r.rec&&T_DOMS.includes(r.rec.dom)?r.rec.dom:null,w=fxOf(p,"councilVotes").reduce((m,f)=>Math.max(m,f.val),1);
      if(d)tally[d]=(tally[d]||0)+w;if(d&&fxOf(p,"councilChoose").length)R.chooser={p,d};
      R.log.push({kind:"cvote",who:p,dom:d,pre:!!r.pre,timeout:!!r.timeout,forced:!!r.forced,auto:!!r.auto});}
    R.tally=tally;
    const mx=Math.max(0,...Object.values(tally)),top=T_DOMS.filter(d=>mx>0&&tally[d]===mx);
    let dom=R.chooser?R.chooser.d:(top.length===1?top[0]:null);
    // a tie is broken by the Host's own vote; only when that vote isn't one of the tied Domains (or there's no Host) does the Host pick
    if(!dom){const hp=hostP(),hv=hp?(R.log.find(x=>x.kind==="cvote"&&sameP(x.who,hp))||{}).dom:null;if(hv&&top.includes(hv)){dom=hv;R.tieBy={who:hp,dom:hv,cands:top.slice()};}}
    if(!dom){const tie=t.councilTie,cand=top.length?top:T_DOMS.slice();
      if(tie&&tie.turn===tTurn()&&cand.includes(tie.dom)){dom=tie.dom;clock=Math.max(clock,+tie.ts||clock);}
      else{R.waiting="tie";R.tieCands=cand;return R;}}
    R.councilDom=dom;R.plan=tPlan(ph,ord,dom);
    for(const E of R.plan)if(!envoyRun(E))return R;
    R.done=true;return R;}
  const pend=ord.filter(p=>!(tCur(p).decl||{}).lock);
  if(pend.length){R.waiting="declare";R.declPending=pend;return R;}
  clock=Math.max(clock,...ord.map(p=>+tCur(p).decl.lock||0));
  R.plan=tPlan(ph,ord,null);
  if(!intrigueRun(R,ord,runSlot))return R;                         // 3. Intrigue Phase
  for(const E of R.plan){if(E.retry)continue;if(!envoyRun(E))return R;}   // 4. Vote (retries are voted at the end of the Tally Phase)
  if(!tallyRun(R,ord,runSlot,applyVote,finish,envoyRun))return R; // 5. Tally Phase
  R.done=true;return R;}

// ---- stage 2: Perform — action + target are chosen only after the Envoy passes ----
function performEval(E){if(!(E.out==="Passed"||E.out==="Endorsed"))return null;
  const rec=((tCur(E.owner).perform)||{})[E.id];if(!rec)return null;
  if(rec.failAccept)return {rec,tgt:rec.target?pById(rec.target):null,parts:[],adj:rec.failNet??E.net,out:rec.failOut||"Failed",accepted:true};   // the would-be fail stands
  if(!rec.action)return null;
  return Object.assign({rec},comboEval(E,rec.action,rec.target));}
// post-Envoy Influence modifiers for one action + target (RULES: they apply once the action and target are chosen)
function comboEval(E,action,tid){const tgt=tid&&!String(tid).startsWith("al:")?D.players.find(p=>String(p.id)===String(tid)):null,parts=[],ad=actDom(action,E);
  fxOf(E.owner,"act").filter(f=>f.dom===ad&&(f.tgtPOabove==null||(tgt&&(tgt.board.po||0)>f.tgtPOabove))).forEach(f=>parts.push({src:f.src,val:f.val*f.q}));
  if(tgt)fxOf(tgt,"defend").filter(f=>(f.dom&&f.dom===ad)||(f.action&&f.action.toLowerCase()===String(action).toLowerCase()))
    .forEach(f=>parts.push({src:tgt.name+": "+f.src,val:f.val*f.q}));
  let adj=E.net+parts.reduce((a,x)=>a+x.val,0);if(E.council)adj=Math.max(1,adj);
  let out=tOutcome(adj);                                             // full thresholds: can reach Condemned
  let saved=null;const fp=failPassFx(E);if(fp&&(out==="Failed"||(out==="Condemned"&&fp.condemned))){out="Passed";saved=fp.src;}
  if(E.bonus&&out==="Endorsed")out="Passed";   // an Endorsed bonus action is not Endorsed again
  let capped=null;if(out==="Endorsed"&&tgt){const ne=fxOf(tgt,"noEndorse").find(f=>f.dom===E.dom);if(ne){out="Passed";capped=tgt.name+": "+ne.src;}}   // "<Dom> actions targeting you can't be Endorsed"
  return {tgt,parts,adj,out,saved,capped,ok:out==="Passed"||out==="Endorsed"};}
function failPassFx(E){return fxOf(E.owner,"failPass").find(f=>!f.dom||f.dom===E.dom)||null;}
function actionsOf(dom){return Object.keys(DATA.actions||{}).filter(k=>(DATA.actions[k]||{}).domain===dom);}
// "Rising Prowess" style requirement vs the player's Standing — a flag, not a lock
function actReqFlag(p,name){const r=String(((DATA.actions||{})[name]||{}).requires||"").trim();if(!r)return "";
  const m=/^(Rising|Established|Sovereign)\s+(\w+)$/.exec(r);if(!m)return r;
  const ORD=["Untested","Rising","Established","Sovereign"],have=tStand(p,m[2]);
  return ORD.indexOf(have)>=ORD.indexOf(m[1])?"":r+" (has "+have+")";}
function actInfoHTML(p,name,tgt){const a=(DATA.actions||{})[name];if(!a)return "";const fl=actReqFlag(p,name),rs=actRestrict(p,name,tgt),rd=actRiders(p,name,tgt);
  return (fl?'<div class="flagbox" style="margin-top:4px">⚑ requires '+esc(fl)+'</div>':'')+rs.map(x=>'<div class="flagbox" style="margin-top:4px">⚑ '+esc(x)+'</div>').join('')+
    (rd.length?'<div class="note" style="margin-top:4px">'+rd.map(esc).join('<br>')+'</div>':'')+
    '<div class="note" style="margin-top:4px">'+(a.cost&&a.cost!=="None"?'<b>Cost:</b> '+esc(a.cost)+' · ':'')+(a.requires?'<b>Requires:</b> '+esc(a.requires)+' · ':'')+
    '<b>Effect:</b> '+mdLite(a.effect||"")+(a.endorsed?'<br><b>Endorsed:</b> '+mdLite(a.endorsed):'')+
    ((a.notes||[]).length?'<br>'+a.notes.map(x=>'• '+mdLite(x)).join('<br>'):'')+'</div>';}
// ---- optional auto-resolve: Faith/Doubt in the outcome text → owner's Public Order (owner's client applies once) ----
// ===================== Action automation: Perform picker + resolution =====================
// Resolves only what the rules state plainly; anything needing table agreement, a free choice or unclear wording is
// left as a ⚑ note for the players. Effects apply once (marked in tCur(owner).applied), on the owner's client.
const PF={};   // per-Envoy picker draft (this client only)
function actCost(action){const c=String(((DATA.actions||{})[action]||{}).cost||"");const g=/(\d+)\s*gold/i.exec(c),d=/Doubt\s*(\d+)/i.exec(c);
  return {gold:g?+g[1]:0,doubt:d?+d[1]:0,txt:c&&c!=="None"?c:""};}
function domCost(dom){const L=actionsOf(dom).map(a=>JSON.stringify(actCost(a)));return L.length&&L.every(x=>x===L[0])?JSON.parse(L[0]):null;}   // same cost for every action
function addFaith(b,n){if(n>0)b.po=applyPOFloor(b,Math.max(PO_MIN,Math.min(PO_MAX,(b.po||0)+n)));return n;}
function alliedP(a,b){if(sameP(a,b))return true;return !!effPair(a.id,b.id).household||sameAlliance(String(a.id),String(b.id));}
function allyGroup(gid){const d=diplo();return D.players.filter(q=>d.member[topSuz(q.id)]===gid);}
function topPair(a,b){return pairOf(topSuz(a.id),topSuz(b.id));}
const SM=(b,re)=>srcMatch(b,re);
// Doubt an action causes to one player, with the rules-text riders that change it
function actDoubt(o,dom,q,base,isTarget,notes){let n=base;if(n<=0)return 0;
  D.players.forEach(h=>SM(h.board,"doubt_all_plus").forEach(x=>{n+=+x.m[1];notes.push(h.name+" · "+x.n+": +"+x.m[1]+" Doubt to "+q.name);}));
  if(isTarget)SM(q.board,"doubt_target_minus").forEach(x=>{if(!x.m[1]||x.m[1].toLowerCase()===dom.toLowerCase()){n=Math.max(0,n-(+x.m[2]));notes.push(q.name+" · "+x.n+": −"+x.m[2]+" Doubt");}});
  return n;}
// ---- what each action needs and does ----
const AA={
  "Move":{tgt:"none",run:c=>c.flag("Move the Army on the map: Select ▸ your Army ▸ a lit hex")},
  "Muster":{tgt:"none",sub:o=>musterOpts(o),run:c=>runMuster(c)},
  "Demand Tribute":{tgt:"player",run:c=>c.flag("Negotiate terms with "+c.q.name+"; if refused, Declare War")},
  "Declare War":{tgt:"player",elig:(o,q)=>{const x=effPair(o.id,q.id);return x.household||sameAlliance(String(o.id),String(q.id))?"allied":x.war?"already at war":x.nap?"Non-Aggression Pact":x.truce>0?"truce "+x.truce:"";},
    run:c=>{warOn(c,c.o,c.q,true);warOnFac(c);const mil=diplo().member[topSuz(c.o.id)];if(mil&&(diplo().alliances[mil]||{}).type==="Military")c.flag("Military Alliance: next turn each member Declares War on "+c.q.name+" and sends 1 fewer Envoy");}},
  "Pillage":{tgt:"player",elig:(o,q)=>effPair(o.id,q.id).war?"":"not at war",
    sub:(o,q)=>(o.board.armies||[]).flatMap(a=>pillageTargets(o,a).filter(t=>sameP(t.q,q)).map(t=>({v:a.id+"|"+t.s.id,label:(a.label||("Army "+a.id))+" → "+(t.s.name||t.s.tier)}))),
    run:c=>{const [aid,sid]=c.sub.split("|"),a=(c.o.board.armies||[]).find(x=>String(x.id)===aid);if(!a)return;a.pillage={tp:String(c.q.id),sid};c.log((a.label||"Army "+a.id)+" Pillages "+settName(c.q,sid)+" (each Empire Phase)");}},
  "Intercept Caravan":{tgt:"player",elig:(o,q)=>BST().ic[q.id]?"already intercepted":"",
    run:c=>{BST().ic[c.q.id]={by:String(c.o.id)};c.log(c.q.name+"'s trade income goes to "+c.o.name+" the next turn they're Host"+((DATA.rulesConst||{}).INTERCEPT_EXTORT_PER_CRAFT?" (none: Extort "+DATA.rulesConst.INTERCEPT_EXTORT_PER_CRAFT+" × Craft)":""));}},
  "Foster Rebellion":{tgt:"player",run:c=>{const rk=c.out==="Endorsed"?srcMatch(c.o.board,"foster_endorsed")[0]:null,n=rk?+rk.m[1]:10;
    BST().foster.push({pid:String(c.q.id),by:String(c.o.id),n});c.log("Next Bandit Mechanics: "+n+"-Retinue Bandit "+(n>=(BAN.armyThreshold||25)?"Army":"Camp")+" in "+c.q.name+"'s Outlaw Country"+(rk?" ("+rk.n+")":""));}},
  "Raze":{tgt:"player",sub:(o,q)=>{const L=[];(q.board.placed||[]).filter(x=>!x.fac&&pActive(x)&&x.sid!=null&&x.sid!=="faction").forEach(x=>L.push({v:"h:"+x.id,label:x.name+" · "+settName(q,x.sid)}));
      withBoard(q.board,()=>Object.keys(S.infra||{}).filter(infraOn).forEach(n=>L.push({v:"i:"+n,label:n+" (Infrastructure)"})));return L;},
    run:c=>{const [k,v]=[c.sub.slice(0,1),c.sub.slice(2)],b=c.q.board;
      if(k==="h"){const x=(b.placed||[]).find(y=>String(y.id)===v);if(x){x.dmg=REPAIR_T;delete x.rep;c.log(c.q.name+"'s "+x.name+" is Damaged (inactive until Repaired)");}}
      else{b.idmg=b.idmg||{};b.idmg[v]=REPAIR_T;if(b.irep)delete b.irep[v];c.log(c.q.name+"'s "+v+" is Damaged (inactive until Repaired)");}
      const rx=facHit(b,"raze_extort");if(rx){const t=extortGold({b:c.o.board},{b},+rx[1],c.q.board.faction);c.log(c.q.name+" ("+c.q.board.faction+") extorts "+t.toLocaleString()+" from "+c.o.name);}}},
  "Destabilize":{tgt:"player",sub:(o,q)=>(q.board.settlements||[]).filter(st=>!BST().dest[q.id+":"+st.id]).map(st=>({v:String(st.id),label:(st.name||st.tier)+" · tax "+settTax(q.board,st).toLocaleString()})),
    run:c=>{BST().dest[c.q.id+":"+c.sub]={by:String(c.o.id)};c.log("Next Winter: "+settName(c.q,c.sub)+"'s tax income goes to "+c.o.name);
      if(Object.keys(BST().dest).some(k=>k.startsWith(c.q.id+":")&&k!==c.q.id+":"+c.sub))c.flag("Several Destabilizes on "+c.q.name+": highest Cunning chooses first; ties split the Extort");}},
  // Sabotage: a player's Army, or (no player target) a Bandit Army — "b:<camp hex>"; its Extort comes out of that camp's treasury
  "Sabotage":{tgt:"player",opt:true,optLabel:"a Bandit Army",subNone:o=>banditArmyKeys().map(k=>({v:"b:"+k,label:"Bandit Army @ "+k+" ("+(+mapState().camps[k].n)+" Retinues)"})),
    sub:(o,q)=>{const M=mapState(),L=[];Object.keys(M.cells).forEach(k=>{const x=M.cells[k];if(x.type!=="Army"||String(x.player)!==String(q.id)||x.blocked)return;const a=cellArmy(k).a;L.push({v:"c:"+k,label:(a?(a.label||"Army "+a.id):"Army")+" @ "+k});});
      (q.board.armies||[]).filter(a=>armyInside(q,a)&&!a.blocked).forEach(a=>L.push({v:"a:"+a.id,label:(a.label||"Army "+a.id)+" (inside "+(armyInside(q,a).s.name||armyInside(q,a).s.tier)+")"}));return L;},
    run:c=>{const k=c.sub.slice(2);if(c.sub[0]==="b"){const cp=mapState().camps[k];if(cp){cp.blocked=true;cp.blockedT=tTurn();c.log("Bandit Army @ "+k+" is Blocked until the end of turn "+(tTurn()+1));}return;}
      if(c.sub[0]==="c"){const x=mapState().cells[k];if(x){x.blocked=true;x.blockedT=tTurn();}}else{const a=(c.q.board.armies||[]).find(y=>String(y.id)===k);if(a){a.blocked=true;a.blockedT=tTurn();}}
      c.log(c.q.name+"'s Army is Blocked until the end of turn "+(tTurn()+1));}},
  "Spread Truth":{tgt:"none",run:c=>D.players.forEach(q=>{if(sameP(q,c.o))return;if(alliedP(c.o,q))c.faith(q,1);else c.doubt(q,1,false);})},
  "Send Missionaries":{tgt:"player+alliance",run:c=>{const d=diplo(),mine=d.member[topSuz(c.o.id)];
      const inside=c.al?c.al===mine:(c.q&&sameAlliance(String(c.o.id),String(c.q.id)));
      if(inside)D.players.forEach(q=>{if(!sameP(q,c.o)&&alliedP(c.o,q))c.faith(q,2);});
      else (c.al?allyGroup(c.al):[c.q]).forEach(q=>c.doubt(q,2,true));}},
  "Tithe":{tgt:"player",run:c=>{const m=/Extort (\d+)%/i.exec(((DATA.actions||{}).Tithe||{}).effect||""),pct=m?+m[1]:0,amt=Math.floor(Math.max(0,+c.q.board.treasury||0)*pct/100/100)*100,
      t=extortGold({b:c.q.board},{b:c.o.board},amt,"Tithe");c.log("Tithe: extort "+t.toLocaleString()+" from "+c.q.name);}},
  "Convert":{tgt:"player",run:c=>{const sg=siegeState();sg.mode="Convert";sg.tp=String(c.q.id);sg.sid=null;
      c.flag("Set the Convert Timer in the Siege calculator (Battle tab): "+c.q.name+"'s closest non-capital Settlement, Public Order −5 or lower");}},
  "Sacred War":{tgt:"player",elig:(o,q)=>AA["Declare War"].elig(o,q),
    run:c=>{const x=topPair(c.o,c.q);if(x){x.war=true;x.sacredWar=true;x.trade=false;x.nap=false;}c.log(c.o.name+" and "+c.q.name+" are At War (Sacred War); their treaties end");warOnFac(c);
      c.flag("Perform a Move action with one of your Armies");c.flag("Sacred War restrictions (no treaties, negotiation or tribute between you) aren't tracked");}},
  "Improve":{tgt:"none",sub:o=>improveOpts(o),run:c=>runImprove(c)},
  "Build":{tgt:"none",sub:o=>buildOpts(o),place:(o,sub)=>buildPlaces(o,sub),run:c=>runBuild(c)},
  "Settle":{tgt:"none",run:c=>runSettle(c)},
  "Expand":{tgt:"none",sub:o=>expandOpts(o),run:c=>runExpand(c)},
  "Repair":{tgt:"none",sub:o=>repairOpts(o),run:c=>runRepair(c)},
  "Sign Treaty":{tgt:"player",run:c=>c.flag("Agree a treaty with "+c.q.name+", then set it in the Diplomacy panel (Realm)")},
  "Negotiate":{tgt:"player",run:c=>c.flag("Agree terms with "+c.q.name+" and apply them by hand")},
  "End Treaty":{tgt:"player",elig:(o,q)=>{const x=effPair(o.id,q.id);return !(x.trade||x.nap)?"no Trade Agreement or NAP":x.truce>0?"truce "+x.truce:"";},
    sub:(o,q)=>{const x=effPair(o.id,q.id),L=[];if(x.trade)L.push({v:"trade",label:"Trade Agreement"});if(x.nap)L.push({v:"nap",label:"Non-Aggression Pact (truce "+TRUCE_LEN+")"});return L;},
    run:c=>{const x=topPair(c.o,c.q);if(!x)return;if(c.sub==="trade"){x.trade=false;c.log("Trade Agreement with "+c.q.name+" ends");}
      else if(c.sub==="nap"){x.nap=false;x.truce=TRUCE_LEN;c.log("NAP with "+c.q.name+" ends · Truce Timer "+TRUCE_LEN);}}},
};
// Muster (Prowess): Raise a new Army in a Settlement you Control, or Reinforce one; the Muster Timer then runs on the Army card
function musterOpts(o){const b=o.board,L=[],mx=EQ.army_max||25,cap=withBoard(b,()=>eraCap("armies")),n=(b.armies||[]).length;
  (b.armies||[]).forEach(a=>{const room=Math.max(0,mx-(a.count||0));if(room>0)L.push({v:"r:"+a.id,label:"Reinforce "+(a.label||("Army "+a.id))+" (+"+Math.min(room,MUSTER_DEFAULT)+")"});});
  (b.settlements||[]).filter(s=>!settUnbuilt(s)).forEach(s=>{const occ=armiesInside(o,s).length;
    L.push({v:"n:"+s.id,label:"Raise in "+(s.name||s.tier)+(occ?" · occupied":"")+(cap!=null&&n>=cap?" · ⚑ "+n+"/"+cap+" Armies":"")});});
  return L;}
function runMuster(c){const o=c.o,b=o.board,k=c.sub.slice(0,1),v=c.sub.slice(2),mx=EQ.army_max||25;let a=null;b.armies=b.armies||[];
  if(k==="n"){const L=EQ.retinues.Levy||{},s=settById(o,v),id=b.armies.reduce((m,x)=>Math.max(m,+x.id||0),0)+1;
    a={id,label:"",upkeep:L.cost||0,retinue:"Levy",count:0,endurance:L.endurance||0,fatigue:0,weapon:"Farm Tools",ranged:"None",armor:"Cloth",shield:"None",strained:false,blunder:false,open:true};
    if(s)a.sid=s.id;b.armies.push(a);c.log(o.name+" raises Army "+id+" in "+(s?(s.name||s.tier):"?"));
    const cap=withBoard(b,()=>eraCap("armies"));if(cap!=null&&b.armies.length>cap)c.flag("Armies "+b.armies.length+" / "+cap+" allowed in "+currentEra());
    if(s&&armiesInside(o,s).length>1)c.flag((s.name||s.tier)+": more than one Army inside");}
  else a=b.armies.find(x=>String(x.id)===v);
  if(!a){c.flag("Muster: Army not found");return;}
  const L=musterLimit(o,a),n=Math.min(MUSTER_DEFAULT,Math.max(0,mx-(a.count||0)));a.muster={n,t:L.lim?Math.ceil(n/L.lim):0};
  c.log((a.label||("Army "+a.id))+": Muster "+n+" · Muster Timer "+a.muster.t+(L.lim?" (limit "+L.lim+")":" · no muster limit in reach"));
  if(!hasMusterField(b))c.flag("Mustering without an active Muster Field");}
// Build: every Holding you may legally start now (pLegal: Scope, Standing, Mastery Chain line or Root, infrastructure_req, Raw
// Material in Reach), with the Settlement it would go to (smartSid); or place it by hand (pending flag)
function buildOpts(o){return withBoard(o.board,()=>{const ctx=legalCtx(),L=[],gs=gameStarted(),sn=id=>{const s=S.settlements.find(x=>x.id===id);return s?(s.name||s.tier):"no free Ward";};
  NAMES.forEach(n=>{const r=R[n]||{};
    const ln=r.root?null:chainLine(n,ctx.own),src=r.root?(rawRes(n)?"Raw Material":"Root"):"from "+(ln&&ln.length?ln[ln.length-1]:"?");
    if(!pLegal(n,null,ctx)){const miss=pReqMiss(n,null,ctx);if(miss)L.push({v:"b:"+n,root:!!r.root,dis:true,label:n+" · "+src+" · requires "+miss});return;}
    const sd=smartSid(n,ctx);L.push({v:"b:"+n,root:!!r.root,dis:gs&&sd==null,label:n+" · "+src+(sd==null?" · no free Ward":"")});});
  L.sort((a,b)=>a.dis-b.dis||a.root-b.root);
  L.push({v:"hand",label:"place it by hand"});return L;});}
// Build target choices for one Holding (sub "b:<name>"): every built Settlement; the auto-placement target first and preselected
function buildPlaces(o,sub){if(!/^b:/.test(sub||""))return null;const n=sub.slice(2);if(!R[n])return null;return withBoard(o.board,()=>{const ctx=legalCtx(),auto=smartSid(n,ctx),ef=effSpot(n);
  return (facRide(n)?[{v:"faction",auto:auto==="faction",dis:false,label:"Faction · ⚡ efficient"+(auto==="faction"?" · auto":"")}]:[]).concat(S.settlements.filter(s=>!settUnbuilt(s)).map(s=>{const c=canPlace(n,s.id),raw=rawOK(n,s.id,ctx),ok=c.ok&&raw,fr=wardUse(s.id).free;
    return {v:String(s.id),auto:s.id===auto,dis:!ok,label:(s.name||s.tier)+" · "+s.tier+" · "+fr+" free"+(s.id===ef?" · \u26a1 efficient":"")+(s.id===auto?" · auto":"")+(ok?"":" — "+(c.ok?"resource not in Reach":fr<=0?"no free Ward":"can't take it"))};}))
    .sort((a,b)=>b.auto-a.auto||a.dis-b.dis);});}
function runBuild(c){const b=c.o.board;if(c.sub==="hand"){c.pend("no Holding placed yet");return;}
  const n=c.sub.slice(2),blk=withBoard(b,()=>scopeBlock(n,null));if(blk){c.flag(blk);return;}
  const pl=c.place==="faction"?(withBoard(b,()=>facRide(n))?"faction":null):c.place!=null&&c.place!==""?withBoard(b,()=>{const s=S.settlements.find(x=>String(x.id)===String(c.place));return s&&canPlace(n,s.id).ok?s.id:null;}):null;
  const sd0=pl!=null?pl:withBoard(b,()=>smartSid(n));if(sd0==null&&gameStarted()){c.flag("Build: no free Ward for "+n+" — not built");return;}
  const r=withBoard(b,()=>placeHolding(n,null,sd0)),st=r.target!=null?settById(c.o,r.target):null;
  c.log(c.o.name+" builds "+n+(st?" in "+(st.name||st.tier):" — no eligible free Ward, Unplaced")+(r.np.bt>0?" · Build Timer "+r.np.bt:"")+(r.host?" (with "+r.host+")":""));}
function improveOpts(o){return withBoard(o.board,()=>{const L=[];
  Object.keys(INFRA).filter(n=>iAvail("infra",n)).forEach(n=>L.push({v:"i:"+n,label:n+" · "+INFRA[n].tier+" · Build Timer "+infraBuildTime(n)}));
  Object.keys(WON).filter(n=>iAvail("wonder",n)).forEach(n=>L.push({v:"w:"+n,label:n+" · Wonder · Build Timer "+infraBuildTime(n)}));
  L.push({v:"hand",label:"by hand"});return L;});}
// Expand: a Settlement up one tier (Village → Town → City → Metropolis), Era and Standing limits shown as flags
function expandOpts(o){return withBoard(o.board,()=>{const L=[];
  S.settlements.forEach(s=>{if(s.up||settUnbuilt(s))return;const nt=nextTier(s.tier);if(!nt)return;const ea=eraAllows(nt,s.id)||{ok:true};
    L.push({v:"x:"+s.id,label:(s.name||s.tier)+" → "+nt+" · Build Timer "+settBuildTime(nt)+(ea.ok?"":" · ⚑ "+ea.why)});});
  L.push({v:"hand",label:"by hand"});return L;});}
function runExpand(c){const o=c.o,b=o.board,v=c.sub.slice(2);if(c.sub==="hand"||!c.sub){c.pend("no Settlement expanded yet");return;}
  const s=settById(o,v);if(!s){c.flag("Expand: Settlement not found");return;}const nt=nextTier(s.tier);if(!nt){c.flag("Expand: "+(s.name||s.tier)+" is already a Metropolis");return;}
  const ea=withBoard(b,()=>eraAllows(nt,s.id))||{ok:true};if(!ea.ok)c.flag("Expand: "+ea.why);
  withBoard(b,()=>settExpand(o,s,nt));c.log(o.name+" expands "+(s.name||s.tier)+" → "+nt+(s.bt>0?" · Build Timer "+s.bt:""));}
function runImprove(c){const o=c.o,b=o.board,k=c.sub.slice(0,1),v=c.sub.slice(2);if(c.sub==="hand"){c.pend("no Infrastructure placed yet");return;}
  const blk=withBoard(b,()=>scopeBlock(v,null));if(blk){c.flag(blk);return;}
  const t=withBoard(b,()=>{(k==="w"?S.wonders:S.infra)[v]=1;itm();const t=gameStarted()?infraBuildTime(v):0;if(t>0)S.itimer[v]=t;return t;});
  c.log(o.name+" builds "+v+(t>0?" · Build Timer "+t:""));
  D.players.forEach(q=>{const h=facHit(q.board,"build_edict");if(h&&h[1]===v&&!sameP(q,o))c.flag(q.name+" ("+q.board.faction+"): must "+h[2]+" "+o.name+"'s "+v+" as an Edict");});}
function runSettle(c){const o=c.o,b=o.board;b.settlements=b.settlements||[];const s={id:nextId(b.settlements),tier:"Village"};nameSett(o,s);
  const t=withBoard(b,()=>gameStarted()?settBuildTime("Village"):0);if(t>0)s.bt=t;b.settlements.push(s);
  c.log(o.name+" settles a new Village"+(s.name?" — "+s.name:"")+(t>0?" · Build Timer "+t:""));c.flag("Place the Village on the map (Map ▸ Place ▸ Village)");
  const cap=withBoard(b,()=>eraCap("max_settlements"));if(cap!=null&&b.settlements.length>cap)c.flag("Settlements "+b.settlements.length+" / "+cap+" allowed in "+currentEra());}
// Repair: a Damaged piece stays inactive until Repaired; Repair sets its Repair Timer, which then counts down
function repairOpts(o){const b=o.board,L=[];
  (b.placed||[]).filter(q=>q.dmg>0&&!q.rep).forEach(q=>L.push({v:"h:"+q.id,label:q.name+" · "+settName(o,q.sid)}));
  Object.keys(b.idmg||{}).filter(n=>b.idmg[n]>0&&!(b.irep||{})[n]).forEach(n=>L.push({v:"i:"+n,label:n+" (Infrastructure)"}));return L;}
function runRepair(c){const b=c.o.board,k=c.sub.slice(0,1),v=c.sub.slice(2);
  if(k==="h"){const q=(b.placed||[]).find(x=>String(x.id)===v);if(!q){c.flag("Repair: Holding not found");return;}q.dmg=REPAIR_T;q.rep=1;c.log(q.name+": Repair Timer "+REPAIR_T);}
  else{b.idmg=b.idmg||{};b.irep=b.irep||{};b.idmg[v]=REPAIR_T;b.irep[v]=1;c.log(v+": Repair Timer "+REPAIR_T);}
  c.flag("When it completes: Restore (automatic) or Demolish by hand");}
function settName(q,sid){const st=settById(q,sid);return st?(st.name||st.tier):"?";}
// the target's faction: "When a player Declares War on you, that player and their allies gain Doubt +N" (Sacrosanct);
// "When a player Declares War on the Duke, …" (The Great Arbiter) — flagged, resolved by hand
function warOnFac(c){const h=facHit(c.q.board,"war_on_you_doubt");
  if(h)D.players.filter(p=>sameP(p,c.o)||(!sameP(p,c.q)&&sameAlliance(String(p.id),String(c.o.id)))).forEach(p=>{const g=gainDoubt(p.board,+h[1]);
    c.log(p.name+": Doubt +"+h[1]+" ("+c.q.name+" · "+c.q.board.faction+")"+(g<+h[1]?" — "+(+h[1]-g)+" reduced (first Doubt)":""));});
  if(facHit(c.q.board,"duke_war"))c.flag(c.q.name+" ("+c.q.board.faction+"): "+c.o.name+"'s Trade Agreements, Non-Aggression Pacts and Defensive Alliances are void; every other player Declares War on "+c.o.name+" and their Military Alliance");}
function warOn(c,o,q,cascade){const x=topPair(o,q);if(!x)return;if(!x.war)chron("war",{player:o.name,other:q.name,key:pk(topSuz(o.id),topSuz(q.id))});x.war=true;x.sacredWar=false;x.trade=false;c.log(o.name+" and "+q.name+" are At War"+(x.trade===false?"":""));
  if(!cascade)return;const d=diplo(),g=d.member[topSuz(q.id)];if(g&&(d.alliances[g]||{}).type==="Defensive")allyGroup(g).forEach(m=>{if(sameP(m,q)||sameP(m,o))return;const y=topPair(o,m);if(y&&!y.war){y.war=true;y.sacredWar=false;y.trade=false;c.log(m.name+" (Defensive Alliance) is At War with "+o.name);}});}
// Grand Vizier: "Players may not target you with Cunning actions if your Cunning value is higher" — a Holding may unlock it
// on another value ("Unlocks Grand Vizier which uses your Piety Value / Public Order instead of Cunning")
function grandVizier(q){const b=q.board,h=srcMatch(b,"grand_vizier_alt")[0];
  if(h){const piety=/Piety/i.test(h.m[1]);return {val:piety?((b.domains||{}).Piety||0):(b.po||0),what:piety?"Piety":"Public Order",src:h.n};}
  const g=dbActive(b).find(x=>/^Grand Vizier/i.test(x.name));return g?{val:(b.domains||{}).Cunning||0,what:"Cunning",src:g.name}:null;}
function pfSpec(a){return AA[a]||{tgt:"player",opt:true,run:c=>c.flag("Resolve "+a+" by hand")};}
function pfHardFlags(E,a,target){if(!gameStarted()||ADMIN)return [];const o=E.owner,sp=pfSpec(a),qs=typeof target==="string"?(target.startsWith("al:")?allyGroup(target.slice(3)):(pById(target)?[pById(target)]:[])):target?[target]:[],out=actRestrict(o,a,null).slice();
  if(E.retry&&E.excludeTarget&&target&&String(target)===String(E.excludeTarget))out.push("Forgery Workshop: retry must target a different player");
  qs.forEach(q=>{out.push(...actRestrict(o,a,q));if(sp.elig){const why=sp.elig(o,q);if(why)out.push(why);}
    if(actDom(a,E)==="Diplomacy"&&(isVassal(o.id)||isVassal(q.id)))out.push("Vassal: no Diplomacy actions");
    if(actDom(a,E)==="Cunning"){const gv=grandVizier(q),mine_=(o.board.domains||{}).Cunning||0;
      if(gv&&gv.val>mine_)out.push("Grand Vizier ("+gv.src+"): "+q.name+"'s "+gv.what+" "+gv.val+" > your Cunning "+mine_);}});
  const req=String(((DATA.actions||{})[a]||{}).requires||"").trim(),m=/^(Rising|Established|Sovereign)\s+(\w+)$/.exec(req);
  if(m){const ORD=["Untested","Rising","Established","Sovereign"],have=tStand(o,m[2]),freeSov=m[1]==="Sovereign"&&dbActive(o.board).some(x=>x.dom===m[2]&&x.tier==="Sovereign"&&x.free);if(ORD.indexOf(have)<ORD.indexOf(m[1])&&!freeSov)out.push(req+" (has "+have+")");}
  return [...new Set(out.filter(Boolean))];}
// candidate targets for one action, each with its post-Envoy Influence result
function pfTargets(E,a){const sp=pfSpec(a),o=E.owner,dip=actDom(a,E)==="Diplomacy";
  if(sp.tgt==="none")return [Object.assign({v:"",label:"—"},(()=>{const ev=comboEval(E,a,null),fl=pfHardFlags(E,a,null);return {legal:!fl.length,ok:ev.ok&&!fl.length,ev,flag:fl.join("; ")};})())];
  const L=D.players.filter(q=>!sameP(q,o)).map(q=>{const ev=comboEval(E,a,q.id),fl=[sp.elig?sp.elig(o,q):""].concat(actRestrict(o,a,q));
    if(E.retry&&E.excludeTarget&&String(q.id)===String(E.excludeTarget))fl.push("Forgery Workshop: retry must target a different player");
    if(dip&&(isVassal(o.id)||isVassal(q.id)))fl.push("Vassal: no Diplomacy actions");
    if(sp.sub&&!sp.sub(o,q).length)fl.push("nothing eligible");
    if(actDom(a,E)==="Cunning"){const gv=grandVizier(q),mine_=(o.board.domains||{}).Cunning||0;if(gv&&gv.val>mine_)fl.push("Grand Vizier ("+gv.src+"): "+q.name+"'s "+gv.what+" "+gv.val+" > your Cunning "+mine_);}
    const hard=pfHardFlags(E,a,q);return {v:String(q.id),label:q.name,legal:!hard.length,ok:ev.ok&&!hard.length,ev,flag:[...new Set(fl.filter(Boolean))].join("; ")};});
  if(sp.tgt==="player+alliance")Object.keys(diplo().alliances).forEach(g=>{const tid="al:"+g,ev=comboEval(E,a,tid),fl=pfHardFlags(E,a,tid);L.push({v:tid,label:allianceLabel(g)+(diplo().member[topSuz(o.id)]===g?" (yours)":""),legal:!fl.length,ok:ev.ok&&!fl.length,ev,flag:fl.join("; ")});});
  if(sp.opt&&!E.retry)L.unshift(Object.assign({v:"",label:sp.optLabel||"no player target"},(()=>{const ev=comboEval(E,a,null),fl=pfHardFlags(E,a,null);if(sp.subNone&&!sp.subNone(o).length)fl.push("nothing eligible");
    return {legal:!fl.length,ok:ev.ok&&!fl.length,ev,flag:fl.join("; ")};})()));
  return L;}
function pfSubs(o,a,tid){const sp=pfSpec(a);if(!sp.sub)return null;if(sp.tgt==="none")return sp.sub(o,null);const q=tid&&!String(tid).startsWith("al:")?pById(tid):null;return q?sp.sub(o,q):sp.subNone?sp.subNone(o):[];}
function pfSubLabel(o,a,tid,v){const L=pfSubs(o,a,tid)||[],x=L.find(s=>s.v===v);if(x)return x.label;
  const ap=AA[a];if(a==="Raze")return v.slice(2);if(a==="Destabilize"){const q=pById(tid);return q?settName(q,v):v;}return v;}
function evTxt(ev){return 'net '+ev.adj+' <b class="'+tOutCls(ev.out)+'">'+ev.out+'</b>';}
// RULES: post-Envoy modifiers apply once the action and target are chosen; on a would-be fail the player may instead perform a
// different action of the same Domain against the same target. Unlocked: every option is open (its result is shown); a failing
// choice locks the target (rec.lock = {target, tried:[actions], out, net}) and only other actions against it stay open.
// "you may instead perform a <Domain> action" (Double Speak, Master Conspirator): effects that open another Domain's actions to this Envoy
function insteadFx(E){if(!E||!E.owner)return [];return fxOf(E.owner,"instead").filter(f=>(f.notFrom?E.dom!==f.from:E.dom===f.from)&&(f.outs||["Passed"]).includes(E.out));}
function actDom(a,E){return ((DATA.actions||{})[a]||{}).domain||(E?E.dom:"");}
function pfActs(E){if(E&&E.standingAction)return actionsOf(E.dom).filter(a=>a.toLowerCase()===String(E.standingAction).toLowerCase());
  if(E&&E.bonus)return E.bonus.act?[E.bonus.act]:actionsOf(E.bonus.dom);const L=actionsOf(E.dom),x=[];insteadFx(E).forEach(f=>actionsOf(f.to).forEach(a=>{if(!L.includes(a)&&!x.includes(a))x.push(a);}));const all=L.concat(x);return E.retry?all.filter(a=>pfSpec(a).tgt==="player"):all;}
function pfInsteadSrc(E,a){if(actDom(a,E)===E.dom)return null;const f=insteadFx(E).find(f=>f.to===actDom(a,E));return f||null;}
function pfForm(E,rec,mode){const o=E.owner,id=E.id,acts=pfActs(E),d=PF[id]=PF[id]||{},L=rec&&rec.lock,W=mode==="whisper",M=mode==="empire";
  const tgtKind=a=>pfSpec(a).tgt==="none"?"none":"player";
  if(L)d.target=String(L.target||"");
  let st=acts.map(a=>{let tg=pfTargets(E,a);if(L)tg=tg.filter(t=>t.v===String(L.target||""));
    const tried=L&&(L.tried||[]).includes(a),ok=L?(!tried&&tg.some(t=>t.ok)):tg.some(t=>t.legal);return {a,tg,ok,tried};});
  if(L){const lk=L.target?"player":"none";st=st.filter(x=>tgtKind(x.a)===lk||(pfSpec(x.a).opt&&!L.target));}
  if(!st.some(x=>x.a===d.action&&x.ok))d.action=(st.find(x=>x.ok)||st[0]||{}).a;
  const cur=st.find(x=>x.a===d.action)||{tg:[]},sp=pfSpec(d.action);
  if(!cur.tg.some(t=>t.v===d.target))d.target=((cur.tg.find(t=>t.legal&&!t.flag)||cur.tg.find(t=>t.legal)||cur.tg[0])||{v:""}).v;
  const T=cur.tg.find(t=>t.v===d.target)||null,subs=pfSubs(o,d.action,d.target);
  if(subs&&!subs.some(x=>x.v===d.sub&&!x.dis))d.sub=(subs.find(x=>!x.dis)||{v:""}).v;
  const pls=sp.place?sp.place(o,d.sub):null;if(pls&&!pls.some(x=>x.v===d.place&&!x.dis))d.place=((pls.find(x=>x.auto&&!x.dis)||pls.find(x=>!x.dis))||{v:""}).v;
  const anyLeft=st.some(x=>x.ok);
  let h='<div class="pform" data-pform="'+esc(id)+'">';
  if(L)h+='<div class="flagbox">⚑ '+esc((L.tried||[]).join(", "))+(L.target?' against '+esc(pname(L.target)):'')+' would be <b>'+esc(L.out)+'</b> (net '+L.net+'). '+
    (anyLeft?'Choose a different '+esc(E.dom)+' action against the same target, or ':'No other '+esc(E.dom)+' action against it passes — ')+
    '<button data-do="pffail" data-env="'+esc(id)+'" data-who="'+o.id+'">accept '+esc(L.out)+'</button></div>';
  if(!L||anyLeft){
    h+='<div class="pfr"><span class="note">'+(W?'Declare':'Perform')+'</span><select data-do="pf" data-pf="'+esc(id)+'|action">'+
      st.map(x=>{const rq=actReqFlag(o,x.a),iv=pfInsteadSrc(E,x.a);return '<option value="'+esc(x.a)+'"'+(x.a===d.action?' selected':'')+(x.ok?'':' disabled')+'>'+esc(x.a)+(iv?' ('+esc(actDom(x.a,E))+' · '+esc(iv.src)+')':'')+(x.tried?' — would fail':!x.ok&&L?' — fails':'')+(rq?' · ⚑ requires '+esc(rq):'')+'</option>';}).join("")+'</select>';
    if(sp.tgt!=="none")h+='<select data-do="pf" data-pf="'+esc(id)+'|target"'+(L?' disabled':'')+'>'+cur.tg.map(t=>'<option value="'+esc(t.v)+'"'+(t.v===d.target?' selected':'')+(t.legal?'':' disabled')+'>'+
        esc(t.label)+(W||M?'':' · net '+t.ev.adj+' '+t.ev.out)+(t.flag?' · ⚑ '+esc(t.flag):'')+'</option>').join("")+'</select>';
    if(subs)h+=subs.length?'<select data-do="pf" data-pf="'+esc(id)+'|sub">'+subs.map(x=>'<option value="'+esc(x.v)+'"'+(x.v===d.sub?' selected':'')+(x.dis?' disabled':'')+'>'+esc(x.label)+'</option>').join("")+'</select>':'<span class="note">nothing eligible</span>';
    if(pls&&pls.length)h+='<select data-do="pf" data-pf="'+esc(id)+'|place" title="where it is placed">'+pls.map(x=>'<option value="'+esc(x.v)+'"'+(x.v===d.place?' selected':'')+(x.dis?' disabled':'')+'>'+esc(x.label)+'</option>').join("")+'</select>';
    const okGo=T&&T.legal&&(!L||T.ok)&&(!subs||subs.some(x=>x.v===d.sub&&!x.dis))&&(!pls||!pls.length||pls.some(x=>x.v===d.place&&!x.dis)||!gameStarted());
    h+='<button data-do="'+(W?'whisperDeclare':M?'standingPerform':'perf')+'" data-env="'+esc(id)+'" data-who="'+o.id+'"'+(okGo?'':' disabled')+'>'+(W?'Declare action &amp; target':M?'resolve effect':'Perform')+'</button></div>';
    if(T&&!W&&!M){const ev=T.ev;h+='<div class="pfx">'+(ev.parts.length?ev.parts.map(x=>esc(x.src)+' '+sgn(x.val)).join(', ')+' → ':'')+evTxt(ev)+
        (ev.saved?' · '+esc(ev.saved)+': Fail → Pass':'')+(ev.capped?' · '+esc(ev.capped)+': Endorsed → Passed':'')+
        (actCost(d.action).txt?' · cost <b>'+esc(actCost(d.action).txt)+'</b>':'')+(T.flag?' · <span class="neg">⚑ '+esc(T.flag)+'</span>':'')+
        (actReqFlag(o,d.action)?' · <span class="neg">⚑ requires '+esc(actReqFlag(o,d.action))+'</span>':'')+
        (!ev.ok&&!L?' · <span class="neg">if chosen, only other '+esc(E.dom)+' actions against this target remain</span>':'')+'</div>';}
    {const rd=actRiders(o,d.action,T&&T.ev.tgt);if(rd.length)h+='<div class="note">'+rd.map(esc).join(' · ')+'</div>';}
    h+='<details><summary class="note">'+esc(d.action||"")+' — rules</summary>'+actInfoHTML(o,d.action||acts[0],T&&T.ev.tgt)+'</details>';}
  return h+'</div>';}
// ---- pending Industry flags: cleared when the build shows up on the board, or by hand ----
function boardCounts(b){return {placed:(b.placed||[]).filter(x=>!x.fac).length,setts:(b.settlements||[]).length,
  infra:Object.keys(b.infra||{}).length+Object.keys(b.wonders||{}).length,tiers:(b.settlements||[]).reduce((t,x)=>t+(+((DATA.settlements||{})[x.tier]||{}).tier||0),0)};}
function pendingOf(b){const n=boardCounts(b);return (b.pending||[]).filter(x=>{const s=x.snap||{};
  if(x.act==="Build")return n.placed<=s.placed;if(x.act==="Settle")return n.setts<=s.setts;if(x.act==="Improve")return n.infra<=s.infra;if(x.act==="Expand")return n.tiers<=s.tiers;return true;});}
function apLines(ap){const L=(ap.fx||[]).map(x=>'<div>'+esc(x)+'</div>').concat((ap.flags||[]).map(x=>'<div class="fl">⚑ '+esc(x)+'</div>'));
  return L.length?'<div class="apl">'+L.join("")+'</div>':'';}
// ---- resolve one Envoy: outcome Faith / Doubt, cost, action effect, Endorsed effect ----
function resolveEnvoy(E,pe,fin){const o=E.owner,act=pe&&pe.rec&&pe.rec.action,A=(DATA.actions||{})[act]||{},fx=[],flags=[],res={f:0,d:0,fx,flags};
  if(!E.slot)E.votes.filter(v=>v.a==="O").forEach(v=>srcMatch(o.board,"forge_oppose_extort").forEach(x=>{const t=extortGold({b:v.who.board},{b:o.board},+x.m[1],x.n);if(t)fx.push(o.name+" extorts "+t.toLocaleString()+" from "+v.who.name+" ("+x.n+")");}));
  const txt=E.slot?"":outText(E.dom,fin),f=+((txt.match(/Faith (\d+)/)||[])[1]||0),dz=+((txt.match(/Doubt (\d+)/)||[])[1]||0);
  if(f){addFaith(o.board,f);res.f=f;fx.push(o.name+": Faith +"+f+" ("+fin+")");}
  if(dz){const n=gainDoubt(o.board,dz);res.d=dz;fx.push(o.name+": Doubt +"+dz+" ("+fin+")"+(n<dz?" — "+(dz-n)+" reduced (first Doubt)":""));}
  const noCost=SM(o.board,"no_envoy_cost").filter(x=>x.m[1].toLowerCase()===E.dom.toLowerCase());
  const pay=(cost,why,recoup)=>{if(noCost.length){fx.push(noCost[0].n+": no cost");return;}let g=cost.gold,dd=cost.doubt,recoupedGold=0;const notes=[];
    (recoup||[]).forEach(r=>{if(r.doubt&&dd){notes.push(r.src+": recoup Doubt");dd=0;}if(r.gold&&g){const k=Math.min(r.gold,g);g-=k;recoupedGold+=k;notes.push(r.src+": recoup "+k.toLocaleString());}});
    if(g)tGold(o.board,-g,(E.dom?E.dom+" Envoy · ":"")+why+(notes.length?" ("+notes.join("; ")+")":""));if(dd)gainDoubt(o.board,dd);
    if(recoupedGold)blackMarketReact(o,recoupedGold,"black_market_recoup","Recoup").forEach(x=>fx.push(x));
    if(cost.gold||cost.doubt)fx.push(o.name+" pays "+why+": "+[cost.gold?cost.gold.toLocaleString()+" gold":"",cost.doubt?"Doubt "+cost.doubt:""].filter(Boolean).join(" + ")+(notes.length?" ("+notes.join("; ")+")":""));};
  if(fin==="Condemned")chron("condemned",{player:o.name,domain:E.dom||""});
  if(fin==="Condemned"){const rest=txt.replace(/^\s*Doubt \d+\s*\+\s*/i,""),gm=/\bpay\s+([\d,]+)/i.exec(rest),dm=/^(?:pay\s+)?Doubt (\d+)/i.exec(rest);   // after the "+": the Condemn cost ("pay 2000", "pay Doubt 1")
    if(/pay the action/i.test(rest)){const tried=pe&&pe.rec&&(pe.rec.tried||[])[0],c=act?actCost(act):tried?actCost(tried):domCost(E.dom);
      if(c)pay(c,"the action's cost (Condemned)");else flags.push("Condemned: pay the cost of the "+E.dom+" action you'd have performed");}
    else if(gm||dm)pay({gold:gm?+gm[1].replace(/,/g,""):0,doubt:dm?+dm[1]:0},"Condemned"+(/cannot Recoup/i.test(rest)?" (no Recoup)":""));
    else if(rest&&rest!==txt)flags.push("Condemned: "+rest);}
  const iv=act?pfInsteadSrc(E,act):null,AD=A.domain||E.dom;
  if((fin==="Passed"||fin==="Endorsed")&&act&&A.domain&&A.domain!==E.dom&&!iv){flags.push(act+" isn't a "+E.dom+" action — resolve by hand");return res;}
  if((fin==="Passed"||fin==="Endorsed")&&act&&gameStarted()){
    const tid=pe.rec.target,blocked=pfHardFlags(E,act,tid||null);
    if(blocked.length){flags.push(act+" blocked: "+blocked.join("; "));return res;}}
  if(iv&&(fin==="Passed"||fin==="Endorsed")){fx.push(iv.src+": "+act+" ("+AD+") instead of a "+E.dom+" action");if(iv.once)flags.push(iv.src+": once per "+(iv.once==="turn"?"turn":(T_PHL[iv.once]||iv.once)));}
  if((fin==="Passed"||fin==="Endorsed")&&act){const sp=pfSpec(act),tid=pe.rec.target,al=String(tid||"").startsWith("al:")?String(tid).slice(3):null,q=al?null:(tid?pById(tid):null),notes=[],doubtTo={},faithTo={},actionTargets=new Map();
    const recoup=[],rawTo={};{const rm=SM(o.board,"recoup_envoy").filter(x=>x.m[2].toLowerCase()===E.dom.toLowerCase());
      const pk=(fin==="Endorsed"&&rm.find(x=>x.m[1]==="Endorsed"))||rm.find(x=>x.m[1]==="Passed");if(pk)recoup.push({src:pk.n,gold:+pk.m[3]});}
    const end=fin==="Endorsed"?String(A.endorsed||((EOUT[E.dom]||{}).endorsed)||""):"";
    if(/Recoup Doubt/i.test(end))recoup.push({src:"Endorsed",doubt:true});{const m=/Recoup (\d+)/i.exec(end);if(m)recoup.push({src:"Endorsed",gold:+m[1]});}
    pay(actCost(act),act,recoup);
    const markActionTarget=p=>{if(p&&p.id!=null)actionTargets.set(String(p.id),p);};
    const ctx={o,q,al,sub:pe.rec.sub||"",place:pe.rec.place||"",E,out:fin,log:x=>fx.push(x),flag:x=>flags.push(x),
      pend:msg=>{const b=o.board;b.pending=b.pending||[];b.pending.push({id:E.id,turn:tTurn(),act,msg,snap:boardCounts(b)});},faith:(p,n,src)=>{markActionTarget(p);addFaith(p.board,n);faithTo[p.id]=(faithTo[p.id]||0)+(+n||0);fx.push(p.name+": Faith +"+n+" ("+act+(src?" · "+src:"")+")");},
      doubt:(p,n,isT,src)=>{markActionTarget(p);const k=actDoubt(o,AD,p,n,isT,notes),g=k?gainDoubt(p.board,k):0;doubtTo[p.id]=(doubtTo[p.id]||0)+k;rawTo[p.id]=(rawTo[p.id]||0)+(+n||0);if(k)fx.push(p.name+": Doubt +"+k+" ("+act+(src?" · "+src:"")+")"+(g<k?" — "+(k-g)+" reduced (first Doubt)":""));}};
    if((sp.tgt==="player"&&!sp.opt&&!q)||(sp.sub&&!ctx.sub))flags.push(act+": no target recorded — resolve by hand");
    else if(sp.run)sp.run(ctx);
    if(AD==="Cunning"){if(q)SM(o.board,"cunning_extra_doubt").forEach(x=>{if(x.m[1]&&fin!=="Endorsed")return;ctx.doubt(q,+x.m[2],true,x.n);});
      D.players.forEach(h=>{if(!sameP(h,o))SM(h.board,"recoup_on_cunning").forEach(x=>{const hc=tCurW(h);hc.cunningRecoups=hc.cunningRecoups||[];const key=E.id+"|"+o.id+"|"+x.n;
        if(!hc.cunningRecoups.some(r=>r.key===key))hc.cunningRecoups.push({key,turn:tTurn(),from:String(o.id),act,src:x.n,amount:+x.m[1],claimed:false});
        flags.push(h.name+" ("+x.n+") may recoup "+(+x.m[1]).toLocaleString()+" gold");});});}
    if(AD==="Piety"){
      // Piety actions can affect a selected player, an Alliance, or several players (e.g. Spread Truth).
      if(q)markActionTarget(q);if(al)allyGroup(al).forEach(markActionTarget);
      D.players.forEach(h=>SM(h.board,"piety_extra_doubt").forEach(x=>actionTargets.forEach(p=>{
        ctx.doubt(p,+x.m[1],true,x.n+" · "+h.name);
      })));
    }
    // "…give their target Faith, it gains Faith +N more; …give Doubt, it gains Doubt +N more": only what the action itself gave, per player it gave it to
    SM(o.board,"basilica_amp").forEach(x=>{if(x.m[1].toLowerCase()!==AD.toLowerCase())return;const gf=Object.assign({},faithTo),gd=Object.assign({},rawTo);
      D.players.forEach(p=>{if(gf[p.id]>0)ctx.faith(p,+x.m[2],x.n);
        if(gd[p.id]>0)ctx.doubt(p,+x.m[3],sameP(p,q),x.n);});});
    if(q)SM(q.board,"doubt_backlash").forEach(x=>{if(!((x.m[1]?rawTo:doubtTo)[q.id]>0))return;x.m[1]=x.m[2];const g=gainDoubt(o.board,+x.m[1]);fx.push(o.name+": Doubt +"+x.m[1]+" ("+q.name+" · "+x.n+")");});
    if(fin==="Endorsed"){const m=/Extort (\d+)/i.exec(end);if(m&&q){const t=extortGold({b:q.board},{b:o.board},+m[1],"Endorsed "+E.dom);fx.push("Endorsed: extort "+t.toLocaleString()+" from "+q.name);}
      else if(m&&campTgt(pe))fx.push("Endorsed: extort "+campExtort(campTgt(pe),o,+m[1],"Endorsed "+E.dom).toLocaleString()+" from the Bandit Army @ "+campTgt(pe));
      else if(m)flags.push("Endorsed: Extort "+m[1]+" — no player target");
      const bn=!E.slot&&endorsedBonus(E);if(bn)flags.push("Endorsed: perform "+(bn.dom?"a "+bn.dom:"a "+bn.act)+" action — offered as the next action");}
    if(fin==="Passed"&&AD==="Cunning"&&+RC.CUNNING_EXTORT){const n=+RC.CUNNING_EXTORT;   // a Passed Cunning action Extorts from its target (Endorsed: the action's larger Extort instead)
      if(q){const t=extortGold({b:q.board},{b:o.board},n,"Passed "+AD);fx.push("Passed: extort "+t.toLocaleString()+" from "+q.name);}
      else if(campTgt(pe))fx.push("Passed: extort "+campExtort(campTgt(pe),o,n,"Passed "+AD).toLocaleString()+" from the Bandit Army @ "+campTgt(pe));
      else flags.push("Passed: Extort "+n+" — no player target");}
    notes.forEach(x=>fx.push(x));}
  return res;}
// a Cunning action aimed at a Bandit Army (sub "b:<camp hex>"): its hex, and Extort out of its camp's treasury (an Army away keeps its gold at home; no more than it holds)
function campTgt(pe){const s=String((pe&&pe.rec&&pe.rec.sub)||"");return s.startsWith("b:")&&mapState().camps[s.slice(2)]?s.slice(2):"";}
function campExtort(k,o,n,why){const M=mapState(),c0=M.camps[k],cp=c0&&c0.home&&M.camps[c0.home]?M.camps[c0.home]:c0,t=Math.min(+n||0,Math.max(0,+(cp&&cp.gold)||0));if(!t)return 0;cp.gold-=t;tGold(o.board,t,"Extort from Bandit Army ("+why+")");return t;}
function autoRes(){return TB().auto!==false;}   // default on
function tApply(R){if(!autoRes())return;let ch=false;
  R.log.forEach(l=>{if(l.kind!=="envoy")return;withSlots([l.E]).forEach(E=>{const p=E.owner;
    if(!(HOTSEAT||(lockOn()?mine(p):sameP(meP(),p))))return;
    const c=tCurW(p);c.applied=c.applied||{};if(c.applied[E.id])return;
    if(!resolveOpen(R,E))return;                                                       // Resolve waits for the end of the Tally Phase
    const pe=performEval(E);if(!pe&&(E.out==="Passed"||E.out==="Endorsed"))return;   // wait for Perform
    const fin=pe?pe.out:E.out;c.applied[E.id]={out:fin,f:0,d:0,fx:[],flags:[],dom:E.dom+(E.council?" (Council)":""),act:pe&&pe.rec&&pe.rec.action||"",sub:pe&&pe.rec&&pe.rec.sub?pfSubLabel(p,pe.rec.action,pe.rec.target,pe.rec.sub):""};    // marked first: never applied twice
    if(E.slot)c.applied[E.id].dom+=slotLabel(E);
    Object.assign(c.applied[E.id],resolveEnvoy(E,pe,fin));ch=true;});});
  if(ch)save();}

// ---- host actions ----
// Spring has no Council Phase (SEASONS.Spring): the phase after the Empire Phase is the Envoy Phase
function tNext(ph){const i=T_PH.indexOf(ph);let nx=T_PH[(i+1)%T_PH.length];if(nx==="council"&&isSpring())nx="envoy";return nx;}
function tSetPhase(ph){if(ph==="council"&&isSpring())ph="envoy";const t=TB(),old=tPhase();if(ph!==old||!t.phaseTs){let snap;try{snap=JSON.parse(JSON.stringify(D));if(snap.tbl)delete snap.tbl.phaseStart;}catch(e){snap=null;}t.phaseStart=snap?{phase:ph,turn:tTurn(),data:snap}:null;}
  t.phase=ph;t.begun=true;t.phaseTs=(ph==="council"||ph==="envoy")?tnow():0;t.skip={};t.extraTime={};t.deadlines={};if(ph==="rest")grantDP();
  if(ph==="council")t.councilTie=null;save();render();}
function tRestartPhase(){const t=TB(),s=t.phaseStart,ph=tPhase();if(!s||s.phase!==ph||s.turn!==tTurn()||!s.data){flash("This phase has no saved restart point");return;}
  if(!confirm("Restart the "+T_PHL[ph]+" from its starting state? Votes, declarations, and effects from this phase will be undone."))return;
  const keep={view:D.view,active:D.active,theme:D.theme,themeV:D.themeV};try{D=JSON.parse(JSON.stringify(s.data));}catch(e){flash("Could not restore the phase start");return;}
  Object.keys(keep).forEach(k=>{if(keep[k]!==undefined)D[k]=keep[k];});normalizeD();reindex();Object.keys(PF).forEach(k=>delete PF[k]);const rt=TB();rt.phase=ph;rt.begun=true;rt.phaseTs=tnow();rt.skip={};rt.extraTime={};rt.deadlines={};rt.councilTie=null;rt.phaseStart=s;
  save();render();flash(T_PHL[ph]+" restarted from its saved starting state");}
function tAdd30(){const R=tSim();if(!R.cur)return;const t=TB(),key=R.cur.key;if(t.deadlines&&t.deadlines[key]!=null)t.deadlines[key]=+t.deadlines[key]+30000;
  else if(isFinite(R.cur.deadline)){t.extraTime=t.extraTime||{};t.extraTime[key]=(+t.extraTime[key]||0)+30000;}
  else{t.deadlines=t.deadlines||{};t.deadlines[key]=tnow()+30000;}save();renderTable();}
function grantDP(){const t=TB();if(t.dpGiven===tTurn())return false;t.dpGiven=tTurn();D.players.forEach(p=>{p.board.dp=(p.board.dp||0)+(DATA.dpPerTurn??1);});checkEdicts();return true;}
function dpOwed(){return D.players.filter(p=>(p.board.dp||0)>0);}
function tEndTurn(){{const g=grantDP(),ow=dpOwed();
    if(ow.length&&!(ADMIN&&confirm("Domain Points unspent ("+ow.map(p=>p.name).join(", ")+"). End the turn anyway?"))){
      flash("Spend Domain Points first: "+ow.map(p=>p.name+" "+p.board.dp).join(", "));if(g||tPhase()!=="rest")TB().phase="rest";save();render();return;}}
  const t=TB(),ord=tOrder();
  if(autoRes())D.players.forEach(p=>{const ap=tCur(p).applied||{};p.board.condemned=Object.values(ap).filter(a=>a.out==="Condemned").length;});
  const endedSeason=curSeason(),r0=D.renown||1;
  D.renown=Math.min(+RC.RENOWN_MAX||30,r0+(DATA.renownPerTurn??1));            // Rest Phase 3: gain Renown (stops at RENOWN_MAX)
  // Rest Phase 4: Domain Points were granted when the Rest Phase opened (grantDP); End turn is held above until they're spent
  stepSeason(1);                                                                // new turn's Season: its Empire Phase income applies below
  if(RC.AGE_YEAR_SEASON&&curSeason()===RC.AGE_YEAR_SEASON)D.yearsGone=(+D.yearsGone||0)+1;   // AGE_YEAR_SEASON: the Year advances
  if(curSeason()!=="Spring"&&ord.length>1){t.host=String(ord[0].id);t.hostSet=true;}   // Host passes clockwise (not into Spring) — before income, so trade follows the new Host
  {const R0=tSim();D.players.forEach(p=>{if(fxOf(p,"carry").length)PT(p).carry={turn:tTurn()+1,n:Math.max(0,(R0.pool[p.id]||inflPool(p))-(R0.spent[p.id]||0))};});}
  const ended=tTurn();{const sm=summaryLines(ended);t.hist=t.hist||{};t.hist[ended]=Object.assign(t.hist[ended]||{},{sum:sm});}t.turn=ended+1;t.phase="empire";t.phaseTs=0;t.skip={};t.councilTie=null;   // next turn begins: its Empire Phase
  if(boardEndOn()){const E=empirePhase();
    t.hist=t.hist||{};t.hist[ended]={turn:ended,season:endedSeason,next:curSeason(),renown:[r0,D.renown],rows:E.rows,realm:E.log,sum:(t.hist[ended]||{}).sum||[]};
    Object.keys(t.hist).map(Number).sort((a,b)=>b-a).slice(6).forEach(k=>delete t.hist[k]);}
  else if(banditAuto()){expireBlocks();BST()._t=tTurn();runBanditMechanics();const sk=banditSkims();if(sk.length)creditSkims(sk);delete BST()._t;}
  save();render();}
// change the seat count; never below the lobby's players (or those seated). Shrinking removes empty seats first —
// the highest-numbered empty seat each time — shifting later seats down, so the clockwise order is kept and no one is unseated
function setSeats(want){const cur=tSeats(),floor=seatFloor(),n=Math.max(floor,Math.min(12,+want||floor));
  if(n<cur){const m=seatMap(),row=[];for(let i=0;i<cur;i++)row.push(m[i]||null);
    while(row.length>n){let j=-1;for(let i=row.length-1;i>=0;i--)if(!row[i]){j=i;break;}if(j<0)break;row.splice(j,1);}
    row.forEach((p,i)=>{if(p){const x=PT(p);if(x.seat!==i)x.seat=i;}});}
  TB().seats=n;return n;}
function tAutoSeat(){const m=seatMap(),n=tSeats();let i=0;
  D.players.filter(p=>!Object.values(m).includes(p)).forEach(p=>{while(i<n&&m[i])i++;if(i<n){const x=PT(p);x.seat=i;x.seatTs=tnow();m[i]=p;}});
  save();render();}

// ---- rendering ----
let T_SIG="";
function tSig(R){return [tPhase(),tTurn(),R.waiting||"",R.cur?R.cur.key:"",R.log.length,R.done?1:0,R.councilDom||"",
  D.players.map(p=>Object.keys(tCur(p).applied||{}).length+"/"+Object.keys(tCur(p).perform||{}).length).join(","),
  JSON.stringify(R.spent)].join("|");}
function tName(p){return pTok(p,14)+esc(p.name);}
function tVoteTxt(v){return v.a==="S"?'<span class="pos">+'+v.x+'</span>':v.a==="O"?'<span class="neg">−'+(v.eff!==undefined&&v.eff!==v.x?v.eff+'</span><span class="note"> (paid '+v.x+')</span>':v.x+'</span>'):'<span class="note">'+(v.timeout?"timeout":v.forced?"skipped":"abstain")+'</span>';}
function envBadges(E){const b=[];
  if(E.dom==="Industry")b.push("Ulterior Motive: Oppose only if at war with "+esc(E.owner.name));
  fxOf(E.owner,"noOppose").filter(f=>f.dom===E.dom).forEach(f=>b.push(esc(f.src)+": no Oppose"+(f.lower?" (lower "+esc(f.lower)+")":"")));
  fxOf(E.owner,"jester").forEach(f=>b.push(esc(f.src)+": "+(f.n===1?"1st":"2nd")+" Oppose −"+f.val));
  fxOf(E.owner,"failPass").forEach(f=>b.push(esc(f.src)+": Fail → Pass"));
  return b.map(x=>'<span class="tb-b">'+x+'</span>').join(" ");}
function innateTxt(E){const pts=innateParts(E.owner,E.dom,E.council);
  return 'innate '+E.innate+(pts.length>1?' <span class="note">= '+pts.map(x=>esc(String(x.src))+' '+x.val).join(' + ')+'</span>':'');}
function tOutCls(o){return o==="Endorsed"||o==="Passed"?"pos":"neg";}
function tPerformHtml(E){if(!(E.out==="Passed"||E.out==="Endorsed"))return "";
  const pe=performEval(E),rec=((tCur(E.owner).perform)||{})[E.id]||{},mine=canAct(E.owner),ap=(tCur(E.owner).applied||{})[E.id];
  let h='<div class="tb-perf">';
  if(pe&&pe.accepted){h+='<b class="neg">'+esc(pe.out)+'</b> <span class="note">— '+esc((rec.tried||[]).join(", ")||"no action")+(pe.tgt?' against '+esc(pe.tgt.name):'')+' would fail (net '+pe.adj+')</span>'+(ap?apLines(ap):'');}
  else if(pe&&!rec.edit){const rf=actReqFlag(E.owner,pe.rec.action),rs=actRestrict(E.owner,pe.rec.action,pe.tgt),rd=actRiders(E.owner,pe.rec.action,pe.tgt);
    const rc=recoupNote(E.owner,pe.rec.action,pe.out),sl=pe.rec.sub?pfSubLabel(E.owner,pe.rec.action,pe.rec.target,pe.rec.sub):"";
    h+=(rc?'<span class="tb-b">'+esc(rc)+'</span> ':'')+(rf?'<span class="tb-b">⚑ requires '+esc(rf)+'</span> ':'')+rs.map(x=>'<span class="tb-b">⚑ '+esc(x)+'</span> ').join('')+(rd.length?'<span class="note">'+rd.map(esc).join(' · ')+'</span> ':'')+'Performed <b>'+esc(pe.rec.action)+'</b>'+
      (pe.tgt?' → '+tName(pe.tgt):String(pe.rec.target||"").startsWith("al:")?' → '+esc(allianceLabel(pe.rec.target.slice(3))):'')+(sl?' · '+esc(sl):'')+
      (pe.parts.length?' · '+pe.parts.map(x=>esc(x.src)+' '+sgn(x.val)).join(', ')+' → net <b>'+pe.adj+'</b>':'')+
      ' <b class="'+tOutCls(pe.out)+'">'+pe.out+'</b>'+(pe.saved?' <span class="tb-b">'+esc(pe.saved)+': Fail → Pass</span>':'')+(pe.capped?' <span class="tb-b">'+esc(pe.capped)+': Endorsed → Passed</span>':'');
    if(ap)h+=apLines(ap)+pendingOf(E.owner.board).filter(x=>x.id===E.id).map(x=>'<div class="apl"><div class="fl">⚑ '+esc(x.act+": "+x.msg)+
      (canAct(E.owner)?' <button class="tb-mini" data-do="pendone" data-env="'+esc(x.id)+'" data-who="'+E.owner.id+'">done</button>':'')+'</div></div>').join("");
    else if(pe.out==="Failed"&&mine&&!rec.whisperLock)h+='<div class="note">Would fail — you may instead perform a different '+esc(E.dom)+' action against the same target. '+
      '<button data-do="perfedit" data-env="'+esc(E.id)+'" data-who="'+E.owner.id+'">change action</button></div>';
    else if(mine&&!rec.whisperLock)h+=' <button class="tb-mini" data-do="perfedit" data-env="'+esc(E.id)+'" data-who="'+E.owner.id+'">edit</button>';
    else if(rec.whisperLock)h+='<div class="note">Declared and locked by Whispering Undercroft.</div>';
    if(E.dom==="Diplomacy"&&(mine||rec.declined)&&!rec.whisperLock)h+=' <button class="tb-mini'+(rec.declined?' on':'')+'" data-do="declined" data-env="'+esc(E.id)+'" data-who="'+E.owner.id+'"'+(mine?'':' disabled')+
      ' title="no one agreed: the action fails (Diplomatic Mission)">'+(rec.declined?'declined ✓':'declined')+'</button>';}
  else if(mine)h+=pfForm(E,rec);
  else h+='<span class="note">awaiting '+esc(E.owner.name)+"'s action</span>";
  return h+'</div>';}
// ---- Summary: what happened this turn, one line per Envoy / Outlaw Country / player ----
function summaryLines(T){const L=[],H=TB().hist||{},h=H[T-1],B=BST();
  if(h){(h.realm||[]).forEach(x=>L.push({k:"Empire",t:x}));(h.rows||[]).forEach(r=>{if((r.done||[]).length)L.push({k:"Timers",t:r.name+": "+r.done.join(" · ")});});}
  const by={};(B.slog||[]).filter(x=>x.t===T).forEach(x=>{const k=x.pid||"-";(by[k]=by[k]||[]).push(x.m);});
  Object.keys(by).forEach(k=>L.push({k:"Bandits",t:(k==="-"?"Bandits":pname(k)+"'s Outlaw Country")+": "+by[k].join(" · ")}));
  D.players.forEach(p=>{const c=PT(p).cur;if(!c||c.turn!==T)return;Object.keys(c.applied||{}).forEach(id=>{const a=c.applied[id];
      L.push({k:"Envoy",t:p.name+" · "+(a.dom||id.split(":")[2]||"Council")+" · "+a.out+(a.act?" · "+a.act+(a.sub?" ("+a.sub+")":""):"")+((a.fx||[]).length?" — "+a.fx.join("; "):"")});});
    (c.notes||[]).forEach(x=>L.push({k:"Notice",t:p.name+" · "+x}));});
  if(T===tTurn()){let R=null;try{R=tSim();}catch(e){R=null;}   // envoys resolved this turn but not applied (auto-resolve off / another client's envoy)
    ((R&&R.log)||[]).forEach(l=>{if(l.kind!=="envoy")return;const E=l.E,p=E.owner,c=p&&PT(p).cur;if(!p||(c&&c.turn===T&&(c.applied||{})[E.id]))return;
      L.push({k:"Envoy",t:p.name+" · "+(E.dom+(E.council?" (Council)":""))+" · "+E.out+(autoRes()?"":" · apply by hand")});});}
  const dp=D.players.map(p=>{const x=(p.board.dpLog||[]).filter(y=>y.turn===T).map(y=>y.dom);return x.length?p.name+" "+x.join(", "):"";}).filter(Boolean);
  if(dp.length)L.push({k:"Domain Points",t:dp.join(" · ")});
  return L;}
// ---- CHRONICLE: macro events as story lines (templates: worldbuilding CHRONICLE; on/off per event there) ----
// Hooks: chronTick() diffs a snapshot on every save (monument, wonder, war_pair, peace, vassal, vassal_end, besieged, era);
// direct calls: warOn (war, the declarer known), endBattle (battle), captureTransfer (capture), sackApply (sack), resolveEnvoy (condemned), growCamps (bandit_army).
const CHR=(DATA.placeNames||{}).chronicle||null;
function chronOn(){return !!D.started||tTurn()>1||(D.players||[]).some(p=>(p.board.turn||0)>0);}
function chron(ev,v){if(!CHR||!chronOn())return;const E=CHR[ev];if(!E||E.on===false||!(E.lines||[]).length)return;
  const vars=Object.assign({era:currentEra()},v||{}),txt=E.lines[Math.floor(Math.random()*E.lines.length)].replace(/\{(\w+)\}/g,(_,k)=>vars[k]!=null?String(vars[k]):"?");
  D.chron=D.chron||[];D.chron.push({t:tTurn(),y:curYear(),s:curSeason(),ev,txt,k:vars.key||null});}
function chronSnap(){const o={era:currentEra(),mon:{},won:{},war:{},vas:{},cap:{}};
  D.players.forEach(p=>{const b=p.board;
    (b.placed||[]).filter(q=>(R[q.name]||{}).monument&&!(q.bt>0)&&!q.fac).forEach(q=>{o.mon[p.id+"|"+q.name]=String(q.sid);});
    Object.keys(b.wonders||{}).filter(n=>b.wonders[n]&&!((b.itimer||{})[n]>0)).forEach(n=>{o.won[p.id+"|"+n]=1;});});
  const d=diplo();Object.keys(d.pairs).forEach(k=>{if(d.pairs[k].war)o.war[k]=1;});Object.keys(d.suzerain).forEach(k=>{if(d.suzerain[k])o.vas[k]=String(d.suzerain[k]);});
  realmTimers().filter(t=>t.kind==="siege").forEach(t=>{const p=pById(t.tp),s=p&&settById(p,t.sid);if(s&&s.capital)o.cap[t.tp+"|"+t.sid]=t.by!=null?String(t.by):"b";});
  return o;}
function chronTick(){if(!CHR||!D.players)return;let n;try{n=chronSnap();}catch(e){return;}const o=D.chronSnap;D.chronSnap=n;if(!o||!chronOn())return;
  const sn=(pid,sid)=>{const p=pById(pid),s=p&&settById(p,sid);return s?(s.name||s.tier):"?";};
  Object.keys(n.mon).filter(k=>!o.mon[k]).forEach(k=>{const [pid,h]=k.split("|");chron("monument",{player:pname(pid),holding:h,settlement:sn(pid,n.mon[k])});});
  Object.keys(n.won).filter(k=>!o.won[k]).forEach(k=>{const [pid,h]=k.split("|");chron("wonder",{player:pname(pid),holding:h});});
  Object.keys(n.war).filter(k=>!o.war[k]&&!(D.chron||[]).some(e=>e.ev==="war"&&e.k===k&&e.t===tTurn())).forEach(k=>{const [a,b]=k.split("|");chron("war_pair",{player:pname(a),other:pname(b)});});
  Object.keys(o.war).filter(k=>!n.war[k]).forEach(k=>{const [a,b]=k.split("|");chron("peace",{player:pname(a),other:pname(b)});});
  Object.keys(n.vas).filter(k=>o.vas[k]!==n.vas[k]).forEach(k=>chron("vassal",{player:pname(k),other:pname(n.vas[k])}));
  Object.keys(o.vas).filter(k=>!n.vas[k]).forEach(k=>chron("vassal_end",{player:pname(k),other:pname(o.vas[k])}));
  Object.keys(n.cap).filter(k=>!o.cap[k]).forEach(k=>{const [pid,sid]=k.split("|");chron("besieged",{player:pname(pid),other:n.cap[k]==="b"?"Bandits":pname(n.cap[k]),settlement:sn(pid,sid)});});
  if(o.era&&n.era!==o.era)chron("era",{era:n.era});}
function chronDate(e){return (e.s||"")+(e.y!=null?", Year "+e.y:"")+" · Turn "+e.t;}
function empireChecklistHTML(){const sea=curSeason(),auto=boardEndOn();
  const L=[["Start of the Empire Phase effects, incl. Domain Standing effects","reference#refStanding","Standings"],["Apply the Season: "+sea,"reference#refSeasons","Reference"],
    ["Timers tick, finished builds resolve","board:board","Board"],["Host resolves Bandits","table#tBanditBox","Bandits"],
    ["Gain Influence & Envoys","",""],sea==="Winter"?["Winter: tax income","board:summary","Totals"]:null,
    ["Income & upkeep","board:summary","Totals"],["Extort (\u201cper player without\u201d is automatic at End turn)","",""],["Public Order (Faith − Doubt)","board:summary","Totals"],["Armies regain Endurance","board:board","Board"],["Remaining Each Empire Phase effects","",""]].filter(Boolean);
  return '<div class="tb-check">'+L.map(x=>'<div>'+esc(x[0])+(x[1]?' <a href="#" data-goto="'+x[1]+'">'+x[2]+' ▸</a>':' <span class="note">(this panel)</span>')+'</div>').join("")+
    '</div>';}
// which tree charts are open (per device); the whole section's state too
let TREE_OPEN=new Set(),TREE_SEC=true;
try{TREE_OPEN=new Set(JSON.parse(localStorage.getItem("renown_tree_open")||"[]"));TREE_SEC=localStorage.getItem("renown_tree_sec")!=="0";}catch(e){}
function treeSave(){try{localStorage.setItem("renown_tree_open",JSON.stringify([...TREE_OPEN]));localStorage.setItem("renown_tree_sec",TREE_SEC?"1":"0");}catch(e){}}
document.addEventListener("click",e=>{
  const sm=e.target.closest("#refTree details.tchart > summary");
  if(sm){const d=sm.parentElement,t=d.dataset.t;if(d.open)TREE_OPEN.delete(t);else TREE_OPEN.add(t);treeSave();return;}   // user toggles only
  const ss=e.target.closest("#refTree > summary");if(ss){TREE_SEC=!ss.parentElement.open;treeSave();return;}
  const rr=e.target.closest("#refRaw");if(rr){REF_RAW=rr.checked;try{localStorage.setItem("renown_refraw",REF_RAW?"1":"0");}catch(_){}render();return;}
  const b=e.target.closest("#refTree [data-tree]");if(b){e.preventDefault();const all=b.dataset.tree==="open";
    document.querySelectorAll("#refTree details.tchart").forEach(d=>{d.open=all;if(all)TREE_OPEN.add(d.dataset.t);else TREE_OPEN.delete(d.dataset.t);});treeSave();}});
// Raw Materials present on the map (terrain or resource nodes, as the Reach check), and every Holding a chain can reach from them
let REF_RAW=true;try{REF_RAW=localStorage.getItem("renown_refraw")!=="0";}catch(e){}
function mapRaws(){const M=mapState(),g=M.grid;if(!g)return null;const V=decodeGrid(g),out=new Set();
  Object.keys(V.hex).forEach(k=>{const h=V.hex[k];if(nodesMode()){if(h.res&&RES_NODE[h.res])out.add(RES_NODE[h.res]);}
    else (((TREF.terrain||{})[RULE_NAME[h.t]]||{})["Raw Materials"]||[]).forEach(n=>out.add(n));});return out;}
function refRawAvail(){if(!REF_RAW)return null;const raws=mapRaws();if(!raws)return null;const mapped=new Set(Object.values(RES_NODE)),ok=new Set();
  NAMES.forEach(n=>{const r=R[n]||{};if(r.root&&(!mapped.has(n)||raws.has(n)))ok.add(n);});
  let ch=true;while(ch){ch=false;NAMES.forEach(n=>{if(ok.has(n))return;const e=effList(n);if((!e.length&&!R[n].root)||e.some(h=>ok.has(h))){ok.add(n);ch=true;}});}
  return ok;}
function treeHTML(){const T=DATA.tree;if(!T)return '<div class="note">No layout.json next to the generator — tree unavailable.</div>';
  const NH0=62,CG=44,RG=10,AV=Math.max(600,((document.getElementById("viewReference")||{}).clientWidth||window.innerWidth)-70),EC=["#2E5A8C","#9E2B25","#1c9c8c","#C6A024","#6A3D8F","#CC6A1A","#3a7d3a","#b5347a","#2b6f9e","#8a6d1a"],E0=T.edges||{},DC={Industry:"#2E5A8C",Prowess:"#9E2B25",Cunning:"#3a3a40",Piety:"#C6A024"};
  // box colour: the Domain of the highest Standing in the unlock (ties: the first listed)
  const dom=n=>{const u=(R[n]||{}).unlock_raw||"";let best="",bk=-1;
    for(const m of u.matchAll(/(Rising|Established|Sovereign)\s+(Industry|Prowess|Cunning|Piety)/g)){const k=ST_ORDER.indexOf(m[1]);if(k>bk){bk=k;best=m[2];}}
    return best||["Industry","Prowess","Cunning","Piety"].find(d=>u.includes(d))||"";};
  const AVS=refRawAvail();
  return T.charts.map(c=>{if(AVS&&R[c.title]&&!AVS.has(c.title))return "";   // a root chart whose Raw Material is off the map: its reachable Holdings show under their other roots
    // the reference tree is the full tree: the culture view filter applies to the catalog only
    const N=Object.fromEntries(Object.entries(c.nodes).filter(([k])=>!AVS||AVS.has(k))),ks=Object.keys(N);if(!ks.length)return "";
    const E={...E0};(c.links||[]).forEach(([p,k])=>{E[p]=(E[p]||[]).concat([k]);});   // chart-only links (e.g. Naturals into Manor House)
    const mc=Math.max(...ks.map(k=>N[k][0])),mr=Math.max(...ks.map(k=>N[k][1]));
    const NW=Math.round(Math.max(150,Math.min(200,(AV-mc*CG)/(mc+1)))),W=(mc+1)*NW+mc*CG;   // boxes shrink to fit the window
    const inner=n=>{const r=R[n]||{},have=(PC[n]||0)>0,us=unlockStatus(n);
      return '<div class="tnh"><span class="gk" data-gk="'+(GK_BY[esc(n)]??"")+'">'+esc(n)+'</span>'+(r.monument?' ◆':'')+(have?' <span class="tb-b">built</span>':'')+
        (r.unlock_raw&&r.unlock_raw!=="-"&&r.unlock_raw!=="\u2014"?' <span class="tnu'+(us.ok?'':' bad')+'" title="Unlock: '+esc(r.unlock_raw)+'">'+(us.ok?'':'🔒')+esc(r.unlock_raw)+'</span>':'')+'</div>'+
        '<div class="tnc">'+(r.combo?kwify(r.combo,n):"—")+'</div>';};
    // one box height per row: the tallest box in that row at this width, so each row stays level and no effect text is cut
    const RH=(()=>{const m=document.createElement("div");m.style.cssText="position:absolute;visibility:hidden;left:-9999px;top:0";
      m.innerHTML=ks.map(n=>'<div class="tn" style="position:static;width:'+NW+'px;height:auto">'+inner(n)+'</div>').join("");
      document.body.appendChild(m);const rh=Array(mr+1).fill(NH0);
      [...m.children].forEach((e,i)=>{const r=N[ks[i]][1];rh[r]=Math.max(rh[r],Math.ceil(e.getBoundingClientRect().height));});m.remove();return rh;})();
    const RY=RH.reduce((a,h,i)=>{a.push(i?a[i-1]+RH[i-1]+RG:0);return a;},[]),nh=k=>RH[N[k][1]];
    const H=RY[mr]+RH[mr]+RG;
    const px=k=>[N[k][0]*(NW+CG),RY[N[k][1]]];let paths="";
    // edges: orthogonal routes with rounded corners; line stops at the arrow base so the head is a clean triangle touching the box
    const AL=7,RAD=5,used=new Set(),slot={};
    const rp=raw=>{const pts=raw.filter((p,i)=>!i||p[0]!==raw[i-1][0]||p[1]!==raw[i-1][1]).filter((p,i,a)=>!(i>0&&i<a.length-1&&((a[i-1][0]===p[0]&&p[0]===a[i+1][0])||(a[i-1][1]===p[1]&&p[1]===a[i+1][1]))));
      let d='M'+pts[0][0]+','+pts[0][1];
      for(let i=1;i<pts.length-1;i++){const [ax,ay]=pts[i-1],[bx,by]=pts[i],[cx,cy]=pts[i+1],l1=Math.hypot(bx-ax,by-ay),l2=Math.hypot(cx-bx,cy-by),r=Math.min(RAD,l1/2,l2/2);
        d+=' L'+(bx-(bx-ax)/l1*r)+','+(by-(by-ay)/l1*r)+' Q'+bx+','+by+' '+(bx+(cx-bx)/l2*r)+','+(by+(cy-by)/l2*r);}
      const e=pts[pts.length-1];return d+' L'+e[0]+','+e[1];};
    const edge=(col,pts,extra)=>{used.add(col);return '<path stroke="'+col+'"'+(extra||'')+' d="'+rp(pts)+'" marker-end="url(#tarw-'+col.slice(1)+')"/>';};
    // incoming forward links share a child's left edge: spread entry points only when there is more than one
    ks.forEach(n=>(E[n]||[]).filter(k=>N[k]&&N[k][0]>N[n][0]).forEach(k=>{(slot[k]=slot[k]||[]).push(n);}));
    // each incoming line enters at its source's height when that falls on the box (straight, no jog), else at the nearest edge band;
    // entries keep source order and stay >= 9px apart
    const EY={};const entryY=(k,n)=>{if(!EY[k]){const by=px(k)[1],lo=by+14,hi=by+nh(k)-10,L=slot[k].slice().sort((a,b)=>N[a][1]-N[b][1]||N[a][0]-N[b][0]),
        y=L.map(q=>Math.min(hi,Math.max(lo,px(q)[1]+nh(q)/2)));for(let i=1;i<y.length;i++)y[i]=Math.max(y[i],y[i-1]+9);
        for(let i=y.length-1;i>=0;i--){if(y[i]>hi)y[i]=hi;if(i<y.length-1&&y[i]>y[i+1]-9)y[i]=y[i+1]-9;}
        EY[k]={};L.forEach((q,i)=>EY[k][q]=y[i]);}return EY[k][n];};
    // routing: try the short route first; if a straight run would cross another box, drop into the gap between rows instead
    const box=ks.map(k=>{const [x,y]=px(k);return [k,x-2,y-2,x+NW+2,y+nh(k)+2];});
    const hit=(pts,skip)=>{for(let i=1;i<pts.length;i++){const [ax,ay]=pts[i-1],[bx_,by_]=pts[i],x0_=Math.min(ax,bx_),x1_=Math.max(ax,bx_),y0_=Math.min(ay,by_),y1_=Math.max(ay,by_);
        for(const [k,l,t,r,b] of box){if(skip.includes(k))continue;if(x1_>l&&x0_<r&&y1_>t&&y0_<b)return true;}}return false;};
    const gapY=(row,down)=>down?RY[row]+RH[row]+RG/2:RY[row]-RG/2;
    const pick=(c,skip)=>c.find(p=>!hit(p,skip))||c[c.length-1];
    ks.forEach(n=>{const kids=(E[n]||[]).filter(k=>N[k]&&N[k][0]>N[n][0]);if(!kids.length)return;
      // each parent gets its own lane (x offset by row) and colour, so merging lines stay traceable
      const [x0,y0]=px(n),x1=x0+NW,y1=y0+nh(n)/2,fx=x1+8+(N[n][1]%4)*5,col=EC[N[n][1]%EC.length];
      kids.forEach(k=>{const [bx,by]=px(k),ey=entryY(k,n),tip=bx-1-AL,gx=bx-16-(N[n][1]%4)*5,down=ey>y1,gy=gapY(N[n][1],down);
        paths+=edge(col,pick([[[x1,y1],[fx,y1],[fx,ey],[tip,ey]],[[x1,y1],[gx,y1],[gx,ey],[tip,ey]],
          [[x1,y1],[fx,y1],[fx,gy],[gx,gy],[gx,ey],[tip,ey]]],[n,k]));});});
    // same-column links: a lane in the gap left of the column (downward and upward links get separate lanes)
    // zag: a link into the box directly above/below (same column, next row) is a straight vertical step
    ks.forEach(n=>(E[n]||[]).filter(k=>N[k]&&N[k][0]===N[n][0]&&Math.abs(N[k][1]-N[n][1])===1).forEach(k=>{const [x0,y0]=px(n),[,by]=px(k),dn=by>y0,cx=x0+Math.round(NW/2),col=EC[N[n][1]%EC.length];
      paths+=edge(col,[[cx,dn?y0+nh(n):y0],[cx,dn?by-1-AL:by+nh(k)+1+AL]]);}));
    ks.forEach(n=>(E[n]||[]).filter(k=>N[k]&&N[k][0]===N[n][0]&&Math.abs(N[k][1]-N[n][1])!==1).forEach(k=>{const [x0,y0]=px(n),[,by]=px(k),dn=by>y0,lx=x0-(dn?14:26),col=EC[N[n][1]%EC.length],
        sy=y0+nh(n)/2+(dn?6:-6),ty=by+nh(k)/2+(dn?-6:6);
      paths+=edge(col,[[x0,sy],[lx,sy],[lx,ty],[x0-1-AL,ty]]);}));
    // backward links (a Mastery that needs a later Holding): dashed, leaving left, running in the row gap, entering the child's right edge
    ks.forEach(n=>(E[n]||[]).filter(k=>N[k]&&N[k][0]<N[n][0]).forEach(k=>{const [x0,y0]=px(n),[bx,by]=px(k),rx=bx+NW+12,col=EC[N[n][1]%EC.length],
        sy=y0+nh(n)-8,ty=by+nh(k)-8,lx=x0-12,down=by>=y0,gy=gapY(N[n][1],down);
      const pts=pick([[[x0,sy],[rx,sy],[rx,ty],[bx+NW+1+AL,ty]],[[x0,sy],[lx,sy],[lx,gy],[rx,gy],[rx,ty],[bx+NW+1+AL,ty]]],[n,k]);
      paths+='<g><title>'+esc(k)+' Mastery needs '+esc(n)+'</title>'+edge(col,pts,' stroke-dasharray="4 3"')+'</g>';}));
    const nodes=ks.map(n=>{const [x,y]=px(n),r=R[n]||{},col=DC[dom(n)]||"#6a6a72",have=(PC[n]||0)>0;
      return '<div class="tn'+(r.monument?' mon':'')+(have?' have':'')+'" style="left:'+x+'px;top:'+y+'px;width:'+NW+'px;height:'+nh(n)+'px;border-color:'+col+'">'+inner(n)+'</div>';}).join("");
    return '<details class="tchart" data-t="'+esc(c.title)+'"'+(TREE_OPEN.has(c.title)?' open':'')+'><summary><b>'+esc(c.title)+'</b> <span class="note">'+ks.length+' Pursuits</span></summary><div class="tscroll"><div class="tcanvas" style="width:'+W+'px;height:'+H+'px">'+
      '<svg width="'+W+'" height="'+H+'"><defs>'+[...used].map(c=>'<marker id="tarw-'+c.slice(1)+'" viewBox="0 0 7 6" refX="0" refY="3" markerWidth="7" markerHeight="6" markerUnits="userSpaceOnUse" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="'+c+'"/></marker>').join("")+'</defs><g fill="none" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="butt">'+paths+'</g></svg>'+nodes+'</div></div></details>';}).join("");}
// rulebook (collapsible, per device); keywords inside the text get hover links
let RB_OPEN=false;try{RB_OPEN=localStorage.getItem("renown_rb_open")==="1";}catch(e){}
document.addEventListener("click",e=>{const sm=e.target.closest("#refRules > summary");if(sm){RB_OPEN=!sm.parentElement.open;try{localStorage.setItem("renown_rb_open",RB_OPEN?"1":"0");}catch(_){}}});
function rulebookHTML(){const RBk=DATA.rulebook;if(!RBk)return '<div class="note">Rulebook not bundled — build with --rules RULES_push_simple.md.</div>';
  return '<div class="rbtoc note">'+RBk.toc.map(t=>'<a href="#" data-goto="reference#'+t[1]+'" class="l'+t[0]+'">'+esc(t[2])+'</a>').join("")+'</div>'+
    '<div class="rbody">'+RBk.html+'</div>';}
function linkifyRules(root){if(!root)return;const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:n=>
    (n.parentElement.closest("a,.gk,h2,h3,h4,h5,h6,code,th")||!n.nodeValue.trim())?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
  const nodes=[];while(w.nextNode())nodes.push(w.currentNode);
  nodes.forEach(n=>{const h=kwify(n.nodeValue);if(h.indexOf('class="gk"')<0)return;const t=document.createElement("template");t.innerHTML=h;n.replaceWith(t.content);});}
function renderReference(){const host=document.getElementById("viewReference");
  const g=(D.map||{}).grid;
  let h='<div style="padding:14px"><h2 style="margin-bottom:8px">Reference</h2>'+
    '<div class="refnav note">'+[["refRules","Rulebook"],["refTree","Pursuit tree"],["refSeasons","Seasons"],["refCosts","Costs"],["refStanding","Standings"],["refTerrain","Terrain & movement"],["refBattle","Tactics & Skirmish rules"]]
      .map(x=>'<a href="#" data-goto="reference#'+x[0]+'">'+x[1]+'</a>').join(' · ')+'</div>';
  h+='<details id="refRules" class="tot"'+(RB_OPEN?' open':'')+'><summary><b style="font-size:14px">Rulebook</b> <span class="note">— RULES_push.md, values from the data</span></summary>'+rulebookHTML()+'</details>';
  h+='<details id="refTree" class="tot"'+(TREE_SEC?' open':'')+'><summary><b style="font-size:14px">Pursuit tree</b></summary>'+
    '<div class="tb-row" style="margin:6px 0"><button data-tree="open">expand all</button><button data-tree="close">collapse all</button>'+
    (mapRaws()?'<label class="note"><input type="checkbox" id="refRaw"'+(REF_RAW?' checked':'')+'> only Holdings the map\'s Raw Materials can start'+(REF_RAW?' ('+(refRawAvail()||new Set()).size+'/'+NAMES.length+')':'')+'</label>':'')+'</div><div class="note">'+(SIMPLE?'':'Innate + Mastery combined (Mastery assumed earned; same stats summed). ')+'Colour = unlock Domain; ◆ = Monument; 🔒 = your Standing doesn\'t meet the unlock yet.</div>'+treeHTML()+'</details>'+
    '<div id="refSeasons">'+seasonsHTML()+'</div><div id="refCosts">'+costsHTML()+'</div>'+
    '<div id="refStanding">'+standingEffectsHTML()+'</div><div id="refTerrain">'+terrainTablesHTML(mapPal(g))+'</div>'+
    '<div id="refBattle">'+battleRulesHTML()+'</div></div>';
  host.innerHTML=h;wireDashExtras(host);linkifyRules(host.querySelector('#refRules .rbody'));}
function tCountdown(R){const els=document.querySelectorAll("#viewTable .tbcd");if(!els.length)return;
  let txt="",near=false;if(R.cur){if(isFinite(R.cur.deadline)){const s=Math.max(0,Math.ceil((R.cur.deadline-tnow())/1000));txt=s+"s remaining";near=s<=5;}else txt="No time limit";}
  els.forEach(e=>{e.textContent=txt;e.classList.toggle("neg",near);});}
setInterval(()=>{if(D.view!=="table")return;const R=tSim();tApply(R);
  if(tSig(R)!==T_SIG&&!editing()){renderTable();return;}tCountdown(R);},500);

const THEMES={
  ink:{},
  parchment:{"--bg":"#efe7d6","--panel":"#f7f0dd","--panel2":"#efe6cd","--line":"#d9cba6","--line2":"#c3b48f","--ink":"#2c2114","--dim":"#6b5c43","--dim2":"#9c8b6a","--chip":"#efe6cd","--barbg":"#d9cba6","--topbar":"#e7dcc2","--sel":"#e3d7b8","--income":"#2e7d32","--craft":"#00838f","--influence":"#6a1b9a","--order":"#b8860b","--upkeep":"#c62828","--season":"#6d4c41","--build":"#3949ab","--battle":"#546e7a","--envoy":"#ad1457","--other":"#7a6f5a","--serif":"'EB Garamond',Georgia,'Iowan Old Style',serif"},
  midnight:{"--bg":"#000000","--panel":"#0b0b0d","--panel2":"#131318","--line":"#2a2a33","--line2":"#3a3a45","--ink":"#f5f5f7","--dim":"#a7a7b2","--dim2":"#6c6c78","--chip":"#0f0f14","--barbg":"#20202a","--topbar":"#000000","--sel":"#1a1a22","--income":"#39d353","--craft":"#22d3ee","--influence":"#c084fc","--order":"#fbbf24","--upkeep":"#f87171","--season":"#a1887f","--build":"#818cf8","--battle":"#94a3b8","--envoy":"#f472b6","--other":"#8a8a96"},
  slate:{"--bg":"#eef1f5","--panel":"#ffffff","--panel2":"#f3f5f9","--line":"#d6dbe3","--line2":"#c3ccd8","--ink":"#1f2430","--dim":"#5b6572","--dim2":"#93a0af","--chip":"#f3f5f9","--barbg":"#dfe4ec","--topbar":"#ffffff","--sel":"#e4e9f1","--income":"#2e7d32","--craft":"#0277bd","--influence":"#6a1b9a","--order":"#c77700","--upkeep":"#c62828","--season":"#795548","--build":"#3949ab","--battle":"#607d8b","--envoy":"#c2185b","--other":"#78889a","--serif":"'EB Garamond',Georgia,'Iowan Old Style',serif","--mono":"ui-monospace,'SF Mono',monospace"},
  royal:{"--bg":"#0c1024","--panel":"#141a38","--panel2":"#1b2450","--line":"#2a356b","--line2":"#37456f","--ink":"#eef1ff","--dim":"#9aa6d6","--dim2":"#5b6aa0","--chip":"#101632","--barbg":"#222c5e","--topbar":"#0a0e20","--sel":"#202a5a","--income":"#5bd6a0","--craft":"#5cc8ff","--influence":"#c9a0ff","--order":"#ffd166","--upkeep":"#ff7a85","--season":"#b0885f","--build":"#8aa0ff","--battle":"#8ea2c8","--envoy":"#ff8ac0","--other":"#8f9bc0"}
};
THEMES.pixel={"--bg":"#0e1220","--panel":"#1d2433","--panel2":"#262f42","--line":"#3b4660","--line2":"#56638a","--ink":"#e6e0d0","--dim":"#9aa6c0","--dim2":"#6a7690","--chip":"#161c28","--barbg":"#2c3548","--topbar":"#0b0e18","--sel":"#2c3548","--income":"#7ccf5a","--craft":"#5ad0e0","--influence":"#c08ae8","--order":"#ffd27a","--upkeep":"#ff6a5a","--season":"#c8946a","--build":"#8aa0ff","--battle":"#9aa6c0","--envoy":"#ff7aa8","--other":"#8a96b0"};
const THEME_VARS=["--bg","--panel","--panel2","--line","--line2","--ink","--dim","--dim2","--income","--craft","--influence","--order","--upkeep","--season","--build","--battle","--envoy","--other","--chip","--barbg","--topbar","--sel","--serif","--mono"];
function applyTheme(name){
  const root=document.documentElement.style;THEME_VARS.forEach(v=>root.removeProperty(v));
  const t=THEMES[name]||{};Object.keys(t).forEach(v=>root.setProperty(v,t[v]));
  document.documentElement.dataset.look=name==="pixel"?"pixel":"";
}
const SKINS={
  rounded:{"--radius":"10px","--radius-sm":"6px","--pill":"999px"},
  soft:{"--radius":"6px","--radius-sm":"4px","--pill":"6px"},
  sharp:{"--radius":"2px","--radius-sm":"2px","--pill":"2px"},
  square:{"--radius":"0px","--radius-sm":"0px","--pill":"0px"}
};
const SKIN_VARS=["--radius","--radius-sm","--pill"];
function applySkin(name){
  const root=document.documentElement.style;SKIN_VARS.forEach(v=>root.removeProperty(v));
  const t=SKINS[name]||SKINS.rounded;Object.keys(t).forEach(v=>root.setProperty(v,t[v]));
}
