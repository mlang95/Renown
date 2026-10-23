// ===================== EFFECT PLUMBING: the effect registry (references/effect_registry.py) =====================
// Every rules-text pattern the board acts on is matched once at build time; DATA.efx[source][id] = the hits, one
// [whole, group1, …] array per clause. Sources: h:<Holding> · hm:<Holding Mastery> · i:<Infra> · w:<Wonder> · f:/F:<Faction>.
// Per-clause rows: _once (once-per tracker), _cant (restrictions), _sp / _spo (Speed), _win (timing window).
// active sources of a board, in reading order: [{n, k}] (Holdings, Infrastructure, Wonders, faction)
function srcKeys(b){if(!b)return [];return withBoard(b,()=>{const L=[];
  Object.keys(PC).forEach(n=>L.push({n,k:"h:"+n}));
  Object.keys(S.infra||{}).filter(infraOn).forEach(n=>L.push({n,k:"i:"+n}));
  Object.keys(S.wonders||{}).filter(infraOn).forEach(n=>L.push({n,k:"w:"+n}));
  if(S.faction&&EFX["f:"+S.faction])L.push({n:S.faction,k:"f:"+S.faction});
  return L;});}
// every hit of registry pattern `id` on b's active pieces: [{n, m}] (m = [whole match, group1, …], a fresh copy)
function srcMatch(b,id){const out=[];srcKeys(b).forEach(x=>efxOf(x.k,id).forEach(m=>out.push({n:x.n,m:m.slice()})));return out;}
function srcHas(b,id){return srcMatch(b,id).length>0;}
// per-clause rows of one kind (_once, _cant, _win) on b's active pieces: [{n, r}]
function srcRows(b,kind){const out=[];srcKeys(b).forEach(x=>efxOf(x.k,kind).forEach(r=>out.push({n:x.n,r})));return out;}

const NUMV=s=>parseInt(String(s).replace(/\s/g,"").replace("−","-"),10);
// players whose Reach is within range 1 of this player's Reach (Border)
function bordersOf(p){const M=mapState(),g=M.grid;if(!g||!p)return [];const own=reachOwners(M,g.width,g.height),mine=new Set(),by={};
  Object.keys(own).forEach(k=>own[k].forEach(id=>{(by[id]=by[id]||new Set()).add(k);if(String(id)===String(p.id))mine.add(k);}));
  return D.players.filter(q=>!sameP(q,p)&&by[q.id]&&[...by[q.id]].some(k=>mine.has(k)||hexNb(k).some(n=>mine.has(n))));}
// ---- Public Order: caps and floors from text ("can't exceed N", "would ever be less than N set it to M") ----
function poCap(b){const c=srcMatch(b,"po_cap").map(x=>+x.m[1]);return c.length?Math.min(...c):null;}
function poTextFloor(b){const f=srcMatch(b,"po_floor");
  return f.length?f.map(x=>({src:x.n,kind:"floor",below:+x.m[1],to:+x.m[2]})).reduce((a,x)=>x.to>a.to?x:a):null;}
// ---- Siege Timer modifiers from text ----
function siegeTextMods(def,att){const rows=[];
  if(def){srcMatch(def.board,"siege_def_plus").filter(x=>x.n!=="Citadel").forEach(x=>rows.push({src:x.n+" (defender)",val:+x.m[1]}));
    srcMatch(def.board,"siege_def_po")
      .forEach(x=>{if((def.board.po||0)>=+x.m[1])rows.push({src:x.n+" (PO "+x.m[1]+"+)",val:+x.m[2]});});}
  if(att)srcMatch(att.board,"siege_att_minus").forEach(x=>rows.push({src:x.n+" (besieger)",val:-x.m[1]}));
  const noWalls=att?srcMatch(att.board,"siege_ignore_walls").map(x=>x.n):[];
  return {rows,noWalls};}
function siegeWinterOK(t){const by=pById(t.by);return !!by&&srcHas(by.board,"siege_winter");}
function siegeDoubleOK(t){const by=pById(t.by);return !!by&&srcHas(by.board,"siege_double");}   // Battery Park: the besieger's Siege Timers count down twice each turn
// ---- action restrictions & riders (shown as flags; hard restrictions are enforced after game start) ----
function actRestrict(owner,action,target){const a=(DATA.actions||{})[action]||{},out=[];
  const hit=(c)=>{const lc=c.toLowerCase();return lc.includes(action.toLowerCase())||(a.domain&&new RegExp("\\b"+a.domain+" actions","i").test(c));};
  srcRows(owner.board,"_cant").forEach(x=>{if(hit(x.r))out.push(x.n+": can't "+x.r.trim());});
  // Faith is Fickle: while your Public Order is below FAITH_FICKLE_PO you can't target players or their Settlements with Piety actions
  if(target&&!sameP(target,owner)&&a.domain==="Piety"&&!srcHas(owner.board,"piety_target_bypass")&&RC.FAITH_FICKLE_PO!=null&&(+owner.board.po||0)<+RC.FAITH_FICKLE_PO)
    out.push("Faith is Fickle: "+owner.name+"'s Public Order is below "+RC.FAITH_FICKLE_PO+" — can't target players or their Settlements with Piety actions");
  if(target&&a.domain==="Industry"){const bs=(target.board.settlements||[]).filter(s=>settBesieged(target,s.id));
    if(bs.length)out.push(target.name+": "+bs.map(s=>s.name||s.tier).join(", ")+" besieged — Industry actions can't target "+(bs.length>1?"them":"it"));}
  if(target)srcMatch(target.board,"cant_target").forEach(x=>{if(x.m[1].toLowerCase().includes(action.toLowerCase()))out.push(target.name+" ("+x.n+"): can't be targeted by "+action);});
  if(target){const h=facHit(target.board,"cant_on_you");if(h&&h[1].toLowerCase().includes(action.toLowerCase()))out.push(target.name+" ("+target.board.faction+"): can't be targeted by "+action);}
  D.players.forEach(q=>{if(sameP(q,owner)||!sameAlliance(String(q.id),String(owner.id)))return;const h=facHit(q.board,"ally_cant");
    if(h&&h[1].toLowerCase().includes(action.toLowerCase()))out.push(q.name+" ("+q.board.faction+"): your Alliance can't perform "+action);});
  return out;}
function actRiders(owner,action,target){const a=(DATA.actions||{})[action]||{},dom=a.domain||"",out=[];
  srcMatch(owner.board,"rider_extra").forEach(x=>{if(x.m[2].toLowerCase()===dom.toLowerCase()||/piety actions cause/i.test(x.m[1])&&dom==="Piety")out.push(x.n+": "+x.m[1]);});
  if(dom==="Piety")D.players.forEach(p=>srcMatch(p.board,"piety_extra_doubt").forEach(x=>out.push(x.n+" · "+p.name+": +"+x.m[1]+" Doubt to target")));
  srcMatch(owner.board,"rider_your_extra").forEach(x=>{if(x.m[2].toLowerCase()===dom.toLowerCase())out.push(x.n+": "+x.m[1]);});
  srcMatch(owner.board,"basilica_amp").forEach(x=>{if(x.m[1].toLowerCase()===dom.toLowerCase())out.push(x.n+": Faith +"+x.m[2]+" more where it gives Faith, Doubt +"+x.m[3]+" more where it gives Doubt");});
  srcMatch(owner.board,"no_envoy_cost").forEach(x=>{if(x.m[1].toLowerCase()===dom.toLowerCase())out.push(x.n+": no cost");});
  D.players.forEach(q=>srcMatch(q.board,"doubt_all_plus_t").forEach(x=>out.push(q.name+" · "+x.n+": "+x.m[1])));
  if(target){srcMatch(target.board,"doubt_target_minus_t").forEach(x=>{if(!x.m[2]||x.m[2].toLowerCase()===dom.toLowerCase())out.push(target.name+" · "+x.n+": "+x.m[1]);});
    srcMatch(target.board,"doubt_backlash_t").forEach(x=>out.push(target.name+" · "+x.n+": "+x.m[1]));}
  return [...new Set(out)];}

// ===================== ARMY STATES · GARRISONS · ONCE-PER-TURN EFFECTS =====================
function settById(p,sid){return (p.board.settlements||[]).find(s=>String(s.id)===String(sid))||null;}
// Settlements & allied armies inside them ignore "Settlements being Besieged" restrictions (Office of Works)
function besiegeExempt(p){return srcHas(p.board,"besiege_exempt");}
function settBesieged(p,sid){return sid!=null&&siegeOn(p.id,sid)&&!besiegeExempt(p);}
// the live Siege (or Sack) this Army is conducting
function armySieging(p,a){return realmTimers().find(t=>(t.kind==="siege"||t.kind==="capture")&&String(t.by)===String(p.id)&&t.aid!=null&&String(t.aid)===String(a.id))||null;}
// an Army inside (range 0) a Settlement under Siege
function armyBesieged(p,a){return (a.sid!=null&&siegeOn(p.id,a.sid))||(!!a.inAlly&&siegeOn(a.inAlly.pid,a.inAlly.sid));}
function armyStateTags(p,a){const t=[];
  {const x=armyInside(p,a);if(x)t.push({k:"in",txt:"In "+(x.s.name||x.s.tier)+(sameP(x.q,p)?"":" ("+x.q.name+")")});else if(a.sid!=null)t.push({k:"in",txt:"In ?"});}
  const sg=armySieging(p,a);if(sg)t.push({k:"sieging",txt:(sg.kind==="capture"?"Capturing":"Laying Siege")+" — "+(sg.label||"")+
    (srcHas(p.board,"immune_strain_siege")&&sg.kind==="siege"?" · Immune Strained":"")});
  if(armyBesieged(p,a)){t.push({k:"besieged",txt:"Besieged"+(armyBesiegeExempt(p,a)?"":" · Blocked except Sally Forth")});
  }
  {const im=immuneStrainIn(p,a);if(im)t.push({k:"note",txt:im+": Immune Strained (inside a controlled Settlement)"});}
  if(a.sackT)t.push({k:"sack",txt:"Sacking · Blocked & Strained until the Sack Timer resolves"});
  return t;}
function armyBlocked(p,a){return !!a.blocked||!!a.sackT||(armyBesieged(p,a)&&!armyBesiegeExempt(p,a));}
// ---- Garrisons: local Armies inside each Settlement while Garrison Infrastructure is active ----
// sizes from the Garrison text "Local Armies form (10/15/25/50 by Settlement size)", in Settlement tier order
function garrisonSizes(){const m=hitOf("i:Garrison","garrison_sizes");if(!m)return {};
  const v=m[1].split("/").map(x=>+x.trim()),SET=DATA.settlements||{},tiers=Object.keys(SET).filter(t=>(+SET[t].tier||0)>0).sort((a,b)=>SET[a].tier-SET[b].tier),o={};
  tiers.forEach((t,i)=>{if(v[i]!=null&&!isNaN(v[i]))o[t]=v[i];});return o;}
function hasGarrisons(b){return withBoard(b,()=>Object.keys(S.infra||{}).some(n=>infraOn(n)&&!!hitOf("i:"+n,"garrison")));}
// all Garrisons share one Retinue type and equipment
function garrisonGear(b){b.garrison=b.garrison||{retinue:"Levy",weapon:"Farm Tools",ranged:"None",armor:"Cloth",shield:"None"};return b.garrison;}
function garrisonOf(p,sid){const b=p.board,s=settById(p,sid);if(!s||!hasGarrisons(b)||settUnbuilt(s))return null;const sz=garrisonSizes()[s.tier];if(!sz)return null;
  b.garrisons=b.garrisons||{};let g=b.garrisons[s.id];
  if(!g){const rt=EQ.retinues[garrisonGear(b).retinue]||{};g=b.garrisons[s.id]={id:"g"+s.id,count:sz,endurance:rt.endurance||0,fatigue:0};}
  Object.assign(g,garrisonGear(b),{label:"Garrison · "+(s.name||s.tier),garrison:true,sid:s.id,size:sz});return g;}
function garrisonsOf(p){return (p.board.settlements||[]).map(s=>garrisonOf(p,s.id)).filter(Boolean);}
function garrisonCard(u){const b=S,p=playerOfBoard(b);if(!p||!hasGarrisons(b))return null;const gs=garrisonsOf(p),G=garrisonGear(b);
  const card=document.createElement("div");card.className="acard";
  card.innerHTML='<div class="top"><b>Garrisons</b> <span class="note">shared Retinue &amp; equipment · no upkeep · can’t be targeted</span></div>';
  const lo=loadoutFields(G,u);
  card.appendChild(lo);
  const tb=document.createElement("div");tb.className="status";
  gs.forEach(g=>{const row=document.createElement("div");row.className="bcrow";row.style.margin="2px 0";
    const sb=settBesieged(p,g.sid);
    row.innerHTML='<span style="min-width:150px">'+esc(g.label.replace("Garrison · ",""))+'</span>';
    const inp=document.createElement("input");inp.type="number";inp.min="0";inp.max=String(EQ.army_max||25);inp.value=String(g.count||0);inp.style.width="56px";
    inp.onchange=()=>{g.count=Math.max(0,Math.round(+inp.value)||0);save();render();};row.appendChild(inp);
    row.appendChild(document.createTextNode(" / "+g.size+" "));
    const rf=document.createElement("button");rf.textContent="reform";rf.title="set to "+g.size;rf.onclick=()=>{g.count=g.size;g.fatigue=0;save();render();};row.appendChild(rf);
    if(sb){const bd=document.createElement("span");bd.className="badge noearn";bd.textContent="Besieged · can’t Sally Forth";row.appendChild(bd);}
    tb.appendChild(row);});
  card.appendChild(tb);return card;}
// ---- once-per-turn / "may" effects on a player's active pieces: a used-this-turn toggle each (no automation) ----
// rows from the registry (_once): c = the limited part of the clause ("Reach +1, 3x/turn: …" → the per-turn part),
// ph = the phase it belongs to ("turn" = any phase, resets when the turn ends), x = an exchange's numbers, w = its timing window
// Active Domain Standings add their "Once per <Phase>" rows (s:<Domain>:<Standing>), except those the Table already
// tracks itself (domainBoardFx "instead": Master Conspirator)
function standingOnceRows(b){const out=[];dbActive(b).forEach(x=>{if((((DATA.domainBoardFx||{})[x.dom]||{})[x.tier]||[]).some(f=>f.k==="instead"))return;
  efxOf("s:"+x.dom+":"+x.tier,"_once").forEach(r=>out.push({n:x.free?"Studium Generale · "+x.name:x.name,r}));});return out;}
function onceEffects(p){return srcRows(p.board,"_once").concat(standingOnceRows(p.board)).map(({n,r})=>({n,c:r.c,key:(n+"|"+r.c).slice(0,90),game:r.game,x:r.x,ph:r.ph,w:r.w}));}
function onceState(p,game){const t=PT(p);if(game){t.onceG=t.onceG||{};return t.onceG;}
  if(!t.once||t.once.turn!==tTurn())t.once={turn:tTurn(),u:{}};return t.once.u;}
// Once-per / "may" card for the action dock: rows whose window is this phase, or any phase ("turn"); rows without a window
// (standing permissions) fold under "always". ph = the phase shown (default: the current one).
function onceWindowNow(e,ph){return !!e.ph&&(e.ph===ph||e.ph==="turn");}
function onceHTML(p,ph){ph=ph||tPhase();const L=onceEffects(p);if(!L.length)return "";
  const tag=e=>e.ph?' <span class="ph-tag'+(onceWindowNow(e,ph)?' now':'')+'">'+esc(e.ph==="turn"?"Any phase":(T_PHL[e.ph]||e.ph).replace(" Phase",""))+'</span>':'';
  const row=e=>{const st=onceState(p,e.game),u=+st[e.key]||0;
    if(e.x){const mx=+e.x[1];return '<div class="tb-row"><span style="flex:1">'+esc(e.n)+': '+esc(e.c)+tag(e)+'</span><b>'+u+'/'+mx+'</b>'+
      '<button data-do="xch" data-k="'+esc(e.key)+'" data-who="'+p.id+'"'+(u>=mx||!canAct(p)?' disabled':'')+'>exchange</button></div>';}
    return '<div class="tb-row"><label style="flex:1"><input type="checkbox" data-do="once" data-k="'+esc(e.key)+'" data-game="'+(e.game?1:0)+'" data-who="'+p.id+'"'+(u?' checked':'')+(canAct(p)?'':' disabled')+'> '+
      esc(e.n)+': '+esc(e.c)+(e.game?' <span class="note">(per game)</span>':'')+tag(e)+'</label></div>';};
  const now=L.filter(e=>onceWindowNow(e,ph)),other=L.filter(e=>!e.ph);
  if(!now.length&&!other.length)return "";
  return '<div class="tot dock"><div class="dk-h">Once per · '+esc(T_PHL[ph].replace(" Phase",""))+' — '+esc(p.name)+'</div>'+(now.length?now.map(row).join(''):'<div class="note">Nothing limited to this phase.</div>')+
    (other.length?'<details><summary class="note">always ('+other.length+')</summary>'+other.map(row).join('')+'</details>':'')+'</div>';}
function onceUse(p,key,game,on){const st=onceState(p,game);
  if(on){st[key]=1;noteAdd(p,key.split("|")[0]+" used");flash(p.name+": "+key.split("|")[0]+" used");}else delete st[key];
  const oe=onceEffects(p).find(x=>x.key===key),nm=oe?oe.n:"",fw=oe&&/Performed next turn|select a Personal Action you performed this turn/i.test(oe.c)?srcMatch(p.board,"envoy_next_fewer").find(x=>x.n===nm):null;
  if(fw){if(on)PT(p).envNext={turn:tTurn()+1,n:-(+fw.m[1]),src:nm};else delete PT(p).envNext;}}
DO.once=el=>{const p=pById(el.dataset.who);if(!p)return;onceUse(p,el.dataset.k,el.dataset.game==="1",el.checked);save();render();};
DO.xch=el=>{const p=pById(el.dataset.who);if(!p)return;const e=onceEffects(p).find(x=>x.key===el.dataset.k);if(!e||!e.x)return;
  const st=onceState(p,false),u=+st[e.key]||0,gold=+e.x[2],inf=+(e.x[3]||e.x[4]);if(u>=+e.x[1])return;
  if((p.board.treasury||0)<gold){flash(p.name+": not enough gold");return;}
  tGold(p.board,-gold,e.n+": exchange for Influence +"+inf);const c=tCurW(p);c.inflAdj=(+c.inflAdj||0)+inf;st[e.key]=u+1;flash(p.name+": −"+gold+" gold → +"+inf+" Influence");noteAdd(p,e.n+": −"+gold+" gold → +"+inf+" Influence");save();render();};
function noteAdd(p,msg){const c=tCurW(p);c.notes=(c.notes||[]).concat([msg]).slice(-20);}
// ---- Recoup on a performed action ("Passed / Endorsed <Domain> envoys Recoup N Gold"); capped at the gold cost paid ----
function recoupNote(owner,action,out){const a=(DATA.actions||{})[action]||{},dom=a.domain||"",cm=/(\d+)\s*gold/i.exec(a.cost||""),cost=cm?+cm[1]:0;
  const hits=srcMatch(owner.board,"recoup_envoy").filter(x=>x.m[2].toLowerCase()===dom.toLowerCase());
  const pick=(out==="Endorsed"&&hits.find(x=>x.m[1]==="Endorsed"))||hits.find(x=>x.m[1]==="Passed");if(!pick||!(out==="Passed"||out==="Endorsed"))return "";
  const r=Math.min(+pick.m[3],cost);return pick.n+": Recoup "+r.toLocaleString()+(cost?"":" (no gold cost)");}

// ===================== RULES MECHANICS: extort · siege outcomes · muster · first Doubt · movement =====================
const RC=DATA.rulesConst||{};
function blackMarketReact(p,amount,id,kind){if(!p||amount<=0)return [];const out=[];
  D.players.forEach(h=>{if(sameP(h,p))return;srcMatch(h.board,id).forEach(x=>{
    const fee=Math.max(+x.m[3]||0,Math.floor(amount/(+x.m[2]||1))*(+x.m[1]||0)),paid=Math.min(fee,Math.max(0,+p.board.treasury||0));
    if(paid){tGold(p.board,-paid,"Black Market "+kind+" reaction · "+x.n);tGold(h.board,paid,"Black Market "+kind+" reaction · "+x.n);
      out.push(h.name+" extorts "+paid.toLocaleString()+" from "+p.name+" ("+x.n+")");}
  });});return out;}
// ---- Extort: always a transfer of gold that exists; never takes the source below 0 ----
// from / to: {b:board} or {camp:banditCamp}. Returns the amount moved.
function extortGold(from,to,amt,why){
  const have=Math.max(0,from.camp?(+from.camp.gold||0):(+from.b.treasury||0)),t=Math.max(0,Math.min(Math.round(+amt||0),have));
  const nm=x=>!x?"":x.camp?"Bandits":(x.name||boardOwnerName(x.b)),w=why?" ("+why+")":"";
  if(from.camp)from.camp.gold=have-t;else tGold(from.b,-t,"Extorted"+(to?" by "+nm(to):"")+w);
  if(to){if(to.camp)to.camp.gold=(+to.camp.gold||0)+t;else tGold(to.b,t,"Extort from "+nm(from)+w);}
  // Reaction transfers are ledgered directly and tagged, so they cannot recurse.
  if(t&&to&&!to.camp&&to.b){const extorter=D.players.find(p=>p.board===to.b);if(extorter)blackMarketReact(extorter,t,"black_market_extort","Extort");}
  return t;}
// Danegeld: "While At War, your Armies within reach of at-war Settlements Extort their upkeep from that settlement's controller".
// One row per Army standing in Territory reached by an at-war player's Settlements; that player pays the Army's upkeep
// (the first such player if several reach the hex).
function danegeldRows(me){if(!me||!mapState().grid||!srcHas(me.board,"danegeld"))return [];const pid=String(me.id),g=mapState().grid,own=reachOwners(mapState(),g.width,g.height),rows=[];
  (me.board.armies||[]).forEach(a=>{const k=armyHex(me,a);if(!k||!own[k])return;const id=[...own[k]].find(x=>String(x)!==pid&&effPair(pid,x).war);
    const from=id!=null?pById(id):null,amt=armyUpkeep(a);if(from&&amt)rows.push({from,amt,army:a});});
  return rows;}
// "Extort N per player without X" on active pieces → the players without X pay (auto, Empire Phase)
// ---- Loans ("May loan money to Trade Partners at N per M/turn interest (minimum K); on Default: Perform Demand Tribute") ----
function loans(){D.loans=D.loans||[];return D.loans;}
function loanTerms(b){const x=srcMatch(b,"loan_terms")[0];
  if(!x)return null;const d=srcMatch(b,"loan_default").find(y=>y.n===x.n);
  return {per:+x.m[1],of:+x.m[2],min:+x.m[3],src:x.n,def:d?d.m[1].trim():"Demand Tribute"};}
function loanInterest(L){const lp=pById(L.from),t=lp?loanTerms(lp.board):null;if(!t)return 0;return Math.max(t.min,Math.floor(L.amt/t.of)*t.per);}
function runLoans(){const out=[];loans().forEach(L=>{const lp=pById(L.from),bp=pById(L.to);if(!lp||!bp)return;const t=loanTerms(lp.board);
  if(!t){out.push("Loan "+lp.name+" → "+bp.name+": no active lending Holding — no interest");return;}
  const due=loanInterest(L),pay=Math.min(due,Math.max(0,+bp.board.treasury||0));tGold(bp.board,-pay,"Loan interest to "+lp.name);tGold(lp.board,pay,"Loan interest from "+bp.name);
  if(pay<due){lp.board.loanDefaults=(lp.board.loanDefaults||[]).concat([{turn:tTurn(),pid:String(bp.id),short:due-pay}]).slice(-10);
    out.push(bp.name+" defaults on "+lp.name+"'s loan (paid "+pay.toLocaleString()+" of "+due.toLocaleString()+") — "+lp.name+": Perform "+t.def);}
  else out.push(bp.name+" pays "+lp.name+" "+pay.toLocaleString()+" interest ("+t.src+")");});return out;}
function loansHTML(qp){const t=loanTerms(qp.board),mine=loans().filter(L=>String(L.from)===String(qp.id)||String(L.to)===String(qp.id));if(!t&&!mine.length)return "";
  const tp=D.players.filter(q=>!sameP(q,qp)&&effPair(qp.id,q.id).trade);
  let h='<div class="tot dock"><div class="dk-h">Loans — '+esc(qp.name)+'</div>';
  if(t)h+=tp.length?'<div class="tb-row"><select id="lnTo">'+tp.map(q=>'<option value="'+q.id+'">'+esc(q.name)+'</option>').join("")+'</select>'+
      '<input id="lnAmt" type="number" min="'+t.of+'" step="'+t.of+'" value="'+t.of+'" style="width:80px"><button data-do="lend" data-who="'+qp.id+'">lend</button><span class="note">'+t.per+' per '+t.of+'/turn (min '+t.min+')</span></div>':
    '<div class="note">No Trade Partners to lend to.</div>';
  if(t&&srcHas(qp.board,"loan_once")&&loans().some(L=>String(L.from)===String(qp.id)&&L.turn===tTurn()))h+='<div class="flagbox">⚑ '+esc(t.src)+': once per turn — already lent this turn</div>';
  h+=mine.map(L=>{const lp=pById(L.from),bp=pById(L.to);return '<div class="tb-row"><span style="flex:1">'+esc(lp?lp.name:"?")+' → '+esc(bp?bp.name:"?")+' <b>'+(+L.amt).toLocaleString()+'</b> <span class="note">interest '+loanInterest(L).toLocaleString()+'/turn</span></span>'+
    (bp&&canAct(bp)?'<button data-do="lnrepay" data-ln="'+L.id+'">repay</button>':'')+(lp&&canAct(lp)?'<button data-do="lnforgive" data-ln="'+L.id+'">forgive</button>':'')+'</div>';}).join("");
  return h+'</div>';}
DO.lend=el=>{const lp=pById(el.dataset.who),bp=pById(document.getElementById("lnTo").value),amt=Math.max(0,Math.round(+document.getElementById("lnAmt").value||0));
  if(!lp||!bp||!amt)return;if((+lp.board.treasury||0)<amt){flash(lp.name+": not enough gold");return;}
  tGold(lp.board,-amt,"Loan to "+bp.name);tGold(bp.board,amt,"Loan from "+lp.name);loans().push({id:"ln"+Date.now().toString(36),from:String(lp.id),to:String(bp.id),amt,turn:tTurn()});
  noteAdd(lp,"lent "+amt.toLocaleString()+" to "+bp.name);save();render();};
DO.lnrepay=el=>{const L=loans().find(x=>x.id===el.dataset.ln);if(!L)return;const lp=pById(L.from),bp=pById(L.to);
  if((+bp.board.treasury||0)<L.amt){flash(bp.name+": not enough gold to repay");return;}tGold(bp.board,-L.amt,"Loan repaid to "+lp.name);tGold(lp.board,+L.amt,"Loan repaid by "+bp.name);
  D.loans=loans().filter(x=>x!==L);noteAdd(bp,"repaid "+(+L.amt).toLocaleString()+" to "+lp.name);save();render();};
DO.lnforgive=el=>{const L=loans().find(x=>x.id===el.dataset.ln);if(!L)return;D.loans=loans().filter(x=>x!==L);noteAdd(pById(L.from),"forgave the loan to "+((pById(L.to)||{}).name||"?"));save();render();};
function autoExtortRows(b){const me=playerOfBoard(b);if(!me)return [];
  return withBoard(b,()=>{const rows=[],have=new Set(Object.keys(PC)),earned=SIMPLE?{}:computeEarned(have).earned;
    const scan=(atoms,q,src)=>(atoms||[]).forEach(a=>{if(a.cat==="extort"&&a.val&&a.without){
      const nm=String(a.without).replace(/\.$/,"").trim();
      D.players.filter(o=>!sameP(o,me)&&!holdsActive(o.board,nm)).forEach(o=>rows.push({from:o,amt:a.val*q,src}));}});
    Object.keys(PC).forEach(n=>{const r=R[n]||{};scan(r.innate,PC[n],n);if(earned[n])scan(r.mastery,PC[n],n+" (Mastery)");});
    Object.keys(S.infra||{}).filter(infraOn).forEach(n=>scan((INFRA[n]||{}).atoms,1,n));
    return rows;});}
// one slot per Extort: "Extort 500 twice" = two slots of 500. Targets are kept on the board (b.exTo) and carry over turn to turn.
function extortSlots(b){return withBoard(b,()=>{const L=[];Object.keys(PC).forEach(n=>{
    efxOf("h:"+n,"extort_slot").forEach(m=>{for(let i=0;i<PC[n]*(m[2]?2:1);i++)L.push({key:n+"#"+i,src:n,amt:+m[1]});});});return L;});}
// each Extort picks its own target; an unset slot defaults to the target of the Extort before it
function exTargets(b){const T=b.exTo||{},o={};let last=null;extortSlots(b).forEach(x=>{const v=T[x.key]!=null&&T[x.key]!==""?T[x.key]:last;o[x.key]=v;if(v!=null&&v!=="")last=v;});return o;}
function extortTargetsHTML(qp){const L=extortSlots(qp.board);if(!L.length)return "";const T=exTargets(qp.board);
  return '<div class="tot dock"><div class="dk-h">Extort targets — '+esc(qp.name)+' <span class="note">each Empire Phase</span></div>'+L.map(x=>'<div class="tb-row"><span style="flex:1">'+esc(x.src)+' · '+x.amt.toLocaleString()+'</span>'+
    '<select data-do="exto" data-exto="'+esc(x.key)+'" data-who="'+qp.id+'"'+(canAct(qp)?'':' disabled')+'><option value="">— choose —</option>'+D.players.filter(q=>!sameP(q,qp)).map(q=>'<option value="'+q.id+'"'+(String(T[x.key])===String(q.id)?' selected':'')+'>'+esc(q.name)+'</option>').join("")+'</select></div>').join("")+'</div>';}
function runAutoExtort(){const out=[],treasuryAtStart=new Map(D.players.map(p=>[String(p.id),Math.max(0,+p.board.treasury||0)]));
  {const tm=/Extort (\d+)% of their Treasury/i.exec(((DATA.actions||{}).Tithe||{}).effect||""),pct=tm?+tm[1]:0;
   if(pct)D.players.forEach(p=>srcMatch(p.board,"tithe_lower").forEach(x=>{const metrics=x.m[1].split(/\s+or\s+/i).map(m=>m.toLowerCase()),metricValue=(q,m)=>m==="public order"?(+q.board.po||0):(+((q.board.domains||{})[m.replace(/^\w/,c=>c.toUpperCase())])||0);
     D.players.forEach(q=>{if(sameP(q,p)||!metrics.some(m=>metricValue(q,m)<metricValue(p,m)))return;
       const amt=Math.floor(Math.max(0,q.board.treasury||0)*pct/100/100)*100,t=extortGold({b:q.board},{b:p.board},amt,x.n);
       if(t)out.push(p.name+" tithes "+t.toLocaleString()+" from "+q.name+" — "+x.n);});}));}
  D.players.forEach(p=>srcMatch(p.board,"extort_lower_treasury").forEach(x=>D.players.forEach(q=>{
    if(sameP(q,p)||alliedP(p,q)||(treasuryAtStart.get(String(q.id))||0)>=(treasuryAtStart.get(String(p.id))||0))return;
    const t=extortGold({b:q.board},{b:p.board},+x.m[1],x.n);
    if(t)out.push(p.name+" extorts "+t.toLocaleString()+" from "+q.name+" — "+x.n);
  })));
  D.players.forEach(p=>srcMatch(p.board,"extort_half_trade").forEach(x=>D.players.forEach(q=>{
    if(sameP(q,p)||effPair(p.id,q.id).trade)return;const amt=Math.floor(tradeIncome(q.board).total/2/100)*100;if(amt<=0)return;
    const t=extortGold({b:q.board},{b:p.board},amt,x.n);out.push(p.name+" extorts "+t.toLocaleString()+" from "+q.name+" — "+x.n);})));
  D.players.forEach(p=>danegeldRows(p).forEach(x=>{const t=extortGold({b:x.from.board},{b:p.board},x.amt,"army upkeep");
    out.push(p.name+" extorts "+t.toLocaleString()+(t<x.amt?" (of "+x.amt.toLocaleString()+")":"")+" army upkeep from "+x.from.name+" — "+p.board.faction);}));
  D.players.forEach(p=>{const T=exTargets(p.board),hit={};extortSlots(p.board).forEach(x=>{const q=pById(T[x.key]);
      if(!q||sameP(q,p)){out.push(p.name+": "+x.src+" Extort "+x.amt.toLocaleString()+" — no target chosen");return;}
      const t=extortGold({b:q.board},{b:p.board},x.amt,x.src);out.push(p.name+" extorts "+t.toLocaleString()+(t<x.amt?" (of "+x.amt.toLocaleString()+")":"")+" from "+q.name+" — "+x.src);(hit[x.src]=hit[x.src]||[]).push(q);});
    Object.keys(hit).forEach(n=>srcMatch(p.board,"extort_target_faith").filter(x=>x.n===n).forEach(x=>hit[n].forEach(q=>{addFaith(q.board,+x.m[2]);out.push(q.name+": Faith +"+x.m[2]+" ("+n+")");})));});
  D.players.forEach(p=>autoExtortRows(p.board).forEach(x=>{const t=extortGold({b:x.from.board},{b:p.board},x.amt,x.src);
    out.push(p.name+" extorts "+t.toLocaleString()+(t<x.amt?" (of "+x.amt.toLocaleString()+")":"")+" from "+x.from.name+" — "+x.src);}));
  return out;}

// ---- First Doubt each turn: "First Doubt each Empire Phase reduced by N" / "First two Doubt each Empire Phase reduced by N" /
// "Reduce the first instance of Doubt … by N". Each instance of Doubt uses up one slot: "first two … by 1" = two slots of 1.
function firstDoubtRed(b){return withBoard(b,()=>{let r=0;const src=[],slots=[];
  Object.keys(PC).forEach(n=>{const m=hitOf("h:"+n,"first_doubt");if(!m)return;
    const cnt=m[1]?(NUMWORD[m[1].toLowerCase()]||+m[1]||1):1,v=+(m[2]||m[3]);for(let i=0;i<cnt*PC[n];i++)slots.push(v);r+=v*cnt*PC[n];src.push(n);});
  return {r,src,slots};});}
function fdState(b,turn){if(!b.fd||b.fd.turn!==turn)b.fd={turn,slots:firstDoubtRed(b).slots};
  if(!Array.isArray(b.fd.slots))b.fd.slots=(+b.fd.left>0)?[+b.fd.left]:[];return b.fd;}
// apply Doubt n to board b now; the turn's first Doubt instance(s) are reduced, whatever the phase (slots reset each turn)
function gainDoubt(b,n,turn){n=Math.max(0,+n||0);if(!n)return 0;turn=turn??tTurn();
  const st=fdState(b,turn);if(st.slots.length){const cut=Math.min(n,st.slots.shift());n-=cut;}
  b.po=applyPOFloor(b,Math.max(PO_MIN,Math.min(PO_MAX,(b.po||0)-n)));return n;}

// ---- Sieges (realm timers with kind:"siege"): besieged Settlements, Capture, Sack ----
function siegeOn(pid,sid){return realmTimers().some(t=>t.kind==="siege"&&String(t.tp)===String(pid)&&String(t.sid)===String(sid));}
function endSettlementSieges(pid,sid){const T=realmTimers();for(let i=T.length-1;i>=0;i--)if(T[i].kind==="siege"&&String(T[i].tp)===String(pid)&&String(T[i].sid)===String(sid))T.splice(i,1);}
function besiegedCount(p){return (p.board.settlements||[]).filter(s=>siegeOn(p.id,s.id)).length;}
function pById(id){return D.players.find(q=>String(q.id)===String(id))||null;}
function nextId(list){return list.reduce((m,x)=>typeof x.id==="number"&&x.id>=m?x.id+1:m,1);}
function captureTransfer(t){const from=pById(t.tp),to=pById(t.by);if(!from||!to)return "Capture: player missing";
  const fb=from.board,tb=to.board,s=(fb.settlements||[]).find(x=>String(x.id)===String(t.sid));if(!s)return "Capture: Settlement gone";
  tb.settlements=tb.settlements||[];tb.placed=tb.placed||[];
  const nid=nextId(tb.settlements),old=s.id;let pid0=nextId(tb.placed);
  fb.settlements=fb.settlements.filter(x=>x!==s);s.id=nid;s.capital=false;tb.settlements.push(s);
  const moved=(fb.placed||[]).filter(q=>q.sid===old);fb.placed=(fb.placed||[]).filter(q=>q.sid!==old);
  moved.forEach(q=>{q.id=pid0++;q.sid=nid;tb.placed.push(q);});
  const M=mapState();Object.keys(M.cells).forEach(k=>{const c=M.cells[k];if(c.type!=="Army"&&String(c.player)===String(from.id)&&String(c.sid)===String(old)){c.player=to.id;c.sid=nid;}});
  if(D.players.indexOf(from)===D.active||D.players.indexOf(to)===D.active)reindex();
  chron("capture",{player:to.name,other:from.name,settlement:s.name||s.tier});
  return to.name+" captures "+(s.name||s.tier)+" from "+from.name+" ("+moved.length+" Holding"+(moved.length===1?"":"s")+")";}
// a Settlement's Wards: each Ward is the Holding in its slot plus the chain riding it (bottom → top); faction pieces take no Ward
function sackWards(p,s){return withBoard(p.board,()=>{const occ=occupants(s.id),ex=exemptionsOf(occ),host=ex.hostOf||{},on={};
  occ.forEach(o=>{if(ex.has(o.id)){const h=host[o.id];(on[h]=on[h]||[]).push(o);}});
  return occ.filter(o=>!o.fac&&!ex.has(o.id)).map(b=>{const ch=[b];let c=b,g=64;while(g--){const r=(on[c.name]||[]).find(x=>!x.fac&&!ch.includes(x));if(!r)break;ch.push(r);c=r;}return ch;});});}
// Sack: raze (Damage) the top-most Holding of each Ward; the controller removes every Holding of one Ward the sacker chooses,
// then that Ward leaves play; extort SACK_EXTORT_PER_TIER per tier; the Settlement drops a tier; Sack Timer; the Army is Blocked & Strained
function sackApply(i,wardIdx){const T=realmTimers(),t=T[i];if(!t)return;const from=pById(t.tp),to=pById(t.by);if(!from||!to)return;
  const fb=from.board,s=(fb.settlements||[]).find(x=>String(x.id)===String(t.sid));if(!s)return;
  const tierN=+((DATA.settlements||{})[s.tier]||{}).tier||0,log=[];chron("sack",{player:to.name,other:from.name,settlement:s.name||s.tier});
  const W=sackWards(from,s),gone=W[+wardIdx]||[],rm=new Set(gone.map(q=>String(q.id)));
  const razed=W.filter((w,k)=>k!==+wardIdx&&w.length).map(w=>w[w.length-1]);
  razed.forEach(q=>{q.dmg=REPAIR_T;});                                                                    // top-most Holding of each Ward: Damaged
  if(razed.length)log.push("razed "+razed.map(q=>q.name).join(", "));
  fb.placed=(fb.placed||[]).filter(q=>!rm.has(String(q.id)));                                            // the chosen Ward's Holdings leave play
  if(gone.length)log.push("Ward removed: "+gone.map(q=>q.name).join(" + "));
  const ti=TIER_CHAIN.indexOf(s.tier);if(ti>0){log.push(s.tier+" → "+TIER_CHAIN[ti-1]);s.tier=TIER_CHAIN[ti-1];}else log.push(s.tier+" stays "+s.tier);
  const x=extortGold({b:fb},{b:to.board},(+RC.SACK_EXTORT_PER_TIER||0)*tierN,"Sack");log.push("extort "+x.toLocaleString());
  const a=(to.board.armies||[]).find(z=>String(z.id)===String(t.aid)),uid="sk"+Date.now();
  if(a){a.blocked=true;a.strained=true;a.sackT=uid;}
  T.push({type:"Sack Timer",kind:"sack",uid,by:to.id,aid:t.aid,label:to.name+" · sacked "+from.name+"'s "+(s.name||s.tier),n:+((TMR["Sack Timer"]||{}).default)||1});endSettlementSieges(t.tp,t.sid);
  flash("Sack: "+log.join(" · "));}
// Bandit sieges always sack after winning their resolution battle; use the first Ward as the automatic choice.
function banditSack(t){if(!t||!t.bandit)return "";const from=pById(t.tp),s=from&&(from.board.settlements||[]).find(x=>String(x.id)===String(t.sid));
  const M=mapState(),camp=Object.values(M.camps||{}).find(c=>String(c.uid)===String(t.bandit));if(!from||!s||!camp)return "Bandit Sack: target or camp missing";
  const fb=from.board,tierN=+((DATA.settlements||{})[s.tier]||{}).tier||0,log=[],W=sackWards(from,s),gone=W[0]||[],rm=new Set(gone.map(q=>String(q.id)));
  const razed=W.slice(1).filter(w=>w.length).map(w=>w[w.length-1]);razed.forEach(q=>{q.dmg=REPAIR_T;});
  if(razed.length)log.push("razed "+razed.map(q=>q.name).join(", "));
  fb.placed=(fb.placed||[]).filter(q=>!rm.has(String(q.id)));if(gone.length)log.push("Ward removed: "+gone.map(q=>q.name).join(" + "));
  const ti=TIER_CHAIN.indexOf(s.tier);if(ti>0){log.push(s.tier+" → "+TIER_CHAIN[ti-1]);s.tier=TIER_CHAIN[ti-1];}
  const extorted=extortGold({b:fb},{camp},(+RC.SACK_EXTORT_PER_TIER||0)*tierN,"Bandit Sack");log.push("extort "+extorted.toLocaleString()+" to Bandit Treasury");
  camp.sackTarget=String(t.tp)+":"+String(t.sid);
  const a=banditArmy(camp),uid="bsk"+Date.now();a.blocked=true;a.strained=true;a.sackT=uid;
  T.push({type:"Sack Timer",kind:"sack",uid,bandit:t.bandit,label:"Bandits · sacked "+from.name+"'s "+(s.name||s.tier),n:+((TMR["Sack Timer"]||{}).default)||1});
  return "Bandit Sack: "+log.join(" · ");}
function resolveRealm(){const T=realmTimers(),out=[];
  for(let i=T.length-1;i>=0;i--){const t=T[i];if(t.n>0)continue;
    if(t.kind==="capture"){out.push(captureTransfer(t));T.splice(i,1);}
    else if(t.kind==="sack"){D.players.forEach(p=>(p.board.armies||[]).forEach(a=>{if(a.sackT===t.uid){a.blocked=false;delete a.sackT;}}));
      if(t.bandit)Object.values(mapState().camps||{}).forEach(c=>{const a=c.army;if(a&&a.sackT===t.uid){a.blocked=false;delete a.sackT;}});
      out.push("Sack Timer resolved: "+t.label);T.splice(i,1);}}
  return out;}
function sackLocks(){const live=new Set(realmTimers().filter(t=>t.kind==="sack").map(t=>t.uid));
  D.players.forEach(p=>(p.board.armies||[]).forEach(a=>{if(a.sackT&&live.has(a.sackT))a.strained=true;}));}

// ---- Muster: timer = ceil(Retinues ÷ combined muster limit); each tick the Army gains up to the limit ----
function armyHex(p,a){{const x=armyInside(p,a),k=x?settHex(x.q,x.s):null;if(k)return k;}const M=mapState();return Object.keys(M.cells).find(k=>{const c=M.cells[k];return c.type==="Army"&&String(c.player)===String(p.id)&&cellArmy(k).a===a;})||null;}
function settHex(p,s){const M=mapState();return Object.keys(M.cells).find(k=>{const c=M.cells[k];return c.type!=="Army"&&String(c.player)===String(p.id)&&cellSett(k).s===s;})||null;}
function musterLimit(p,a){const k=armyHex(p,a),rb=reachBonus(p).b,out={lim:0,src:[],paused:[],onMap:!!k};
  (p.board.settlements||[]).forEach(s=>{if(settUnbuilt(s))return;const st=(DATA.settlements||{})[s.tier]||{},ml=+st.muster_limit||0;if(!ml)return;
    let ok=!k;if(k){const sk=settHex(p,s);ok=!!sk&&hexDist(hk(sk),hk(k))<=(+st.reach||0)+rb;}
    if(!ok)return;if(siegeOn(p.id,s.id)&&!srcHas(p.board,"muster_besieged")){out.paused.push(s.name||s.tier);return;}
    out.lim+=ml;out.src.push((s.name||s.tier)+" "+ml);});
  return out;}
function musterTick(p){const out=[];(p.board.armies||[]).forEach(a=>{const m=a.muster;if(!m||!(m.n>0))return;
  const L=musterLimit(p,a),room=Math.max(0,(EQ.army_max||25)-(a.count||0)),g=Math.min(L.lim,m.n,room);
  if(g>0){a.count=(a.count||0)+g;m.n-=g;}
  if(!room)m.n=0;
  m.t=m.n>0&&L.lim>0?Math.ceil(m.n/L.lim):0;
  out.push((a.label||("Army "+a.id))+": mustered +"+g+(m.n>0?" ("+m.n+" left"+(L.lim?"":" — paused, no muster limit")+")":" — done")+(L.paused.length?" · besieged: "+L.paused.join(", "):""));
  if(!(m.n>0))delete a.muster;});
  return out;}
function hasMusterField(b){return withBoard(b,()=>Object.keys(S.infra||{}).some(n=>infraOn(n)&&!!hitOf("i:"+n,"muster_field")));}

// ---- Settle placement (flags): min range, Outlaw buffer, terrain, Hamlet range from the capital ----
function charterFlags(p){const M=mapState(),g=M.grid,f=[];if(!g)return f;const V=decodeGrid(g);
  const mine=mapSetts().filter(x=>String(x.cell.player)===String(p.id)),all=mapSetts(),cap=(p.board.settlements||[]).find(s=>s.capital);
  const capK=cap?settHex(p,cap):null;
  mine.forEach(x=>{const h=V.hex[x.k],nm=x.cell.type+" @ "+x.k;
    if(h&&(h.t==="mountain"||h.t==="water"))f.push("Settle: "+nm+" is on "+(RULE_NAME[h.t]||h.t));
    else if(h&&x.cell.type==="Village"&&h.t!=="plains")f.push("Settle: "+nm+" is on "+(RULE_NAME[h.t]||h.t)+" (Villages are settled on grassland only)");
    if(x.cell.type==="Hamlet"){if(capK&&RC.HAMLET_RANGE!=null&&hexDist(hk(x.k),hk(capK))!==+RC.HAMLET_RANGE)f.push("Settle: Hamlet @ "+x.k+" is range "+hexDist(hk(x.k),hk(capK))+" from the capital (must be "+RC.HAMLET_RANGE+")");}
    else if(RC.CHARTER_MIN_RANGE!=null)all.forEach(y=>{if(y.k===x.k||y.cell.type==="Hamlet")return;const d=hexDist(hk(x.k),hk(y.k));
      if(d<+RC.CHARTER_MIN_RANGE)f.push("Settle: "+[x.cell.type+" @ "+x.k,y.cell.type+" @ "+y.k].sort().join(" and ")+" are range "+d+" apart (min "+RC.CHARTER_MIN_RANGE+")");});
    if(RC.OUTLAW_BUFFER_RANGE!=null)Object.keys(M.outlaw).forEach(o=>{const d=hexDist(hk(x.k),hk(o));if(d<+RC.OUTLAW_BUFFER_RANGE)f.push("Settle: "+nm+" is range "+d+" from Outlaw Country @ "+o+" (min "+RC.OUTLAW_BUFFER_RANGE+")");});});
  // Setup › Deploy (checked on Turn 1): capital near the board edge; Outlaw Country seeded off the capital, clear of the Hamlet
  if(tTurn()===1&&capK){const ca=hk(capK),W=+g.width||0,H=+g.height||0,ob=+RC.OUTLAW_BUFFER_RANGE;
    if(RC.CAPITAL_EDGE_RANGE!=null&&W&&H){let ed=1e9;
      for(let c=0;c<W;c++)for(let r=0;r<H;r++){if(c>0&&r>0&&c<W-1&&r<H-1)continue;ed=Math.min(ed,hexDist(ca,[c,r]));}
      if(ed>+RC.CAPITAL_EDGE_RANGE)f.push("Setup: capital @ "+capK+" is range "+ed+" from the board edge (max "+RC.CAPITAL_EDGE_RANGE+")");}
    const oc=outlawOf(p).filter(o=>!isWild(o));
    if(oc.length&&RC.OUTLAW_BUFFER_RANGE!=null){
      if(!oc.some(o=>hexDist(hk(o),ca)===ob))f.push("Setup: no Outlaw Country is exactly range "+ob+" from the capital @ "+capK);
      mine.filter(x=>x.cell.type==="Hamlet").forEach(x=>oc.forEach(o=>{const d=hexDist(hk(o),hk(x.k));
        if(d<=ob)f.push("Setup: Outlaw Country @ "+o+" is range "+d+" from Hamlet @ "+x.k+" (must be more than "+ob+")");}));}}
  return [...new Set(f)];}

// ---- Movement: Speed from data, legal hexes by terrain (Speed −X per Territory, Impassable, Water stop) ----
let SEL=null,MOVEMARCH=false,MOVEADJ=0;
function selArmy(){if(!SEL)return null;const p=pById(SEL.pid),a=p&&(p.board.armies||[]).find(x=>String(x.id)===String(SEL.aid));if(!a){SEL=null;return null;}return {p,a};}
function canMoveArmy(p){return !lockOn()||ADMIN||(!!myClaimP()&&String(myClaimP().id)===String(p.id));}
// Office of Works protects allied Armies while they occupy one of its protected Settlements.
function armyBesiegeExempt(p,a){const inside=armyInside(p,a);return !!inside&&besiegeExempt(inside.q);}
// Settlements an Army may enter (ruling): its owner's, or an Alliance member's / same household
function canEnterSett(p,q){if(!p||!q)return false;if(sameP(p,q))return true;const x=effPair(p.id,q.id);return !!x.household||sameAlliance(String(p.id),String(q.id));}
// the Settlement an Army is inside: own (a.sid) or allied (a.inAlly = {pid, sid})
function armyInside(p,a){if(a.sid!=null){const s=settById(p,a.sid);return s?{q:p,s}:null;}
  if(a.inAlly){const q=pById(a.inAlly.pid),s=q&&settById(q,a.inAlly.sid);return s?{q,s}:null;}return null;}
// one Army per Settlement (ruling): enter if empty; the controller's own Army may enter one an ally holds — the ally is pushed out (range 1)
function enterCheck(p,a,q,s){if(!canEnterSett(p,q))return {ok:false};const occ=armiesInside(q,s).filter(o=>o.a!==a);if(!occ.length)return {ok:true};
  if(sameP(p,q)&&occ.every(o=>!sameP(o.p,q)))return {ok:true,kick:occ.map(o=>({pid:String(o.p.id),aid:String(o.a.id)}))};return {ok:false,why:"occupied"};}
function freeHexNear(k){const M=mapState(),V=decodeGrid(M.grid),seen=new Set([k]);let ring=[k];
  for(let r=0;r<6&&ring.length;r++){const nx=[];for(const x of ring)for(const n of hexNb(x)){if(seen.has(n))continue;seen.add(n);const h=V.hex[n];if(!h)continue;
      if(!terrBlocked(h.t)&&!terrWaterStop(h.t)&&!M.cells[n]&&!M.camps[n])return n;nx.push(n);}ring=nx;}return null;}
function kickOut(q,s,list){const M=mapState(),sk=settHex(q,s),out=[];(list||[]).forEach(o=>{const p=pById(o.pid),a=p&&(p.board.armies||[]).find(x=>String(x.id)===String(o.aid));if(!a)return;
  delete a.inAlly;
  const k=sk?freeHexNear(sk):null;if(k)M.cells[k]={type:"Army",player:p.id,aid:a.id};out.push((a.label||("Army "+a.id))+" ("+p.name+")"+(k?" → "+k:" — no free hex: off the map"));});return out;}
function armiesInside(q,s){const out=[];D.players.forEach(p=>(p.board.armies||[]).forEach(a=>{const x=armyInside(p,a);if(x&&sameP(x.q,q)&&String(x.s.id)===String(s.id))out.push({p,a});}));return out;}
const T_EFF=Object.fromEntries(Object.entries(TREF.terrain||{}).map(([k,v])=>[k,String(v.Effect||"")]));
function terrPen(t){const m=/Speed\s*[-−](\d+)\s*per Territory/i.exec(T_EFF[RULE_NAME[t]]||"");return m?+m[1]:0;}
function terrBlocked(t){return /Impassable/i.test(T_EFF[RULE_NAME[t]]||"");}
function terrWaterStop(t){return /Must end move/i.test(T_EFF[RULE_NAME[t]]||"");}
function terrStrain(t){return /gain Strained/i.test(T_EFF[RULE_NAME[t]]||"");}

function provinceOf(p){const M=mapState(),g=M.grid;if(!g)return new Set();const own=reachOwners(M,g.width,g.height),s=new Set();
  Object.keys(own).forEach(k=>{if(own[k].has(String(p.id)))s.add(k);});return s;}
function moveTraits(p){return withBoard(p.board,()=>{const ks=Object.keys(PC).map(n=>"h:"+n).concat(Object.keys(S.infra||{}).filter(infraOn).map(n=>"i:"+n)),fk="F:"+(S.faction||"");
  const any=id=>ks.some(k=>efxOf(k,id).length);
  return {shipyard:any("shipyard"),bridges:any("bridges"),ignoreTerrain:!!hitOf(fk,"ignore_terrain"),mtnGrass:!!hitOf(fk,"mountain_grass"),fk};});}
function speedOf(p,a,startK){const parts=[],notes=[],b=p.board,sea=curSeason(),base=+((EQ.retinues[a.retinue]||{}).speed)||0;
  parts.push([a.retinue+" Speed",base]);
  const tr=moveTraits(p),prov=provinceOf(p),inProv=!!startK&&prov.has(startK);
  const sm=/All Armies gain Speed\s*([+\-−])\s?(\d+)/i.exec((SEAS[sea]||{}).effect||"");
  if(sm)parts.push([sea,(sm[1]==="+"?1:-1)*(+sm[2])]);
  withBoard(b,()=>{
    // registry Speed rows (_sp): k = startProv (only starting in your Province) | others (other players' Armies) | season | cond | plain
    const scan=(key,src)=>efxOf(key,"_sp").forEach(r=>{const c=r.c,v=r.v;
      if(r.k==="startProv"){if(inProv)parts.push([src,v]);else notes.push(src+" "+(v>0?"+":"")+v+" (only starting in your Province)");return;}
      if(r.k==="others")return;                                                                             // affects other players' Armies
      if(r.k==="season"){if(r.s===sea)parts.push([src,v]);else notes.push(src+" "+(v>0?"+":"")+v+" in "+r.s);return;}
      if(r.k==="cond"){notes.push(src+": "+c.trim()+" (not applied)");return;}
      parts.push([src,v]);});
    Object.keys(PC).forEach(n=>scan("h:"+n,n));
    Object.keys(S.infra||{}).filter(infraOn).forEach(n=>scan("i:"+n,n));
    if(S.faction)scan(tr.fk,S.faction);});
  // other players' "Speed −X to non-allied / Enemy Armies in your Province" where this Army starts
  const M=mapState(),g=M.grid;
  if(startK&&g){const own=reachOwners(M,g.width,g.height)[startK]||new Set();
    own.forEach(id=>{if(String(id)===String(p.id))return;const o=pById(id);if(!o)return;
      const war=!!effPair(p.id,o.id).war,ally=sameAlliance(p.id,o.id);
      withBoard(o.board,()=>{const scanO=(key,kind,src)=>efxOf(key,kind).forEach(r=>{if(!r.yp)return;
          if(r.en&&!war)return;if(r.na&&ally)return;parts.push([o.name+": "+src,r.v]);});
        Object.keys(PC).forEach(n=>scanO("h:"+n,"_sp",n));if(S.faction)scanO("F:"+S.faction,"_spo",S.faction);});});}
  // Public Order "Speed ±N" bands (cumulative, Era-scaled; Charnel House-style doubling applies)
  {const dbl=poDoubled(),po=Math.max(PO_MIN,Math.min(PO_MAX,b.po||0));poActiveKeys(po,b).forEach(k=>{const e=POB(k);if(!Array.isArray(e))return;
    const m=String(e[1]).match(/^Speed\s*([+\-\u2212]\s?\d+)$/i);if(!m)return;const v=parseInt(m[1].replace(/\s/g,"").replace("\u2212","-"),10)*(dbl[e[0]]?2:1);
    parts.push(["Public Order: "+e[0]+(dbl[e[0]]?" ×2":""),v]);});}
  if(MOVEADJ)parts.push(["adjust",MOVEADJ]);
  let sp=Math.max(0,parts.reduce((s,x)=>s+x[1],0));
  if(MOVEMARCH){sp*=(+RC.MARCH_MULTIPLIER||2);notes.unshift("March ×"+(+RC.MARCH_MULTIPLIER||2)+" — lose 1 Endurance, no other action");}
  return {speed:sp,parts,notes,tr,prov};}
function hexNb(k){const [c,r]=hk(k);return [[0,-1],[0,1],[1,c%2?0:-1],[1,c%2?1:0],[-1,c%2?0:-1],[-1,c%2?1:0]].map(([oc,orr])=>(c+oc)+","+(r+orr));}
// Dijkstra over (hex, water state): 0 = land, 1 = on Water (must land next), 2 = landed after Water (move ends)
// ---- Presence (PRESENCE_RANGE): Territory within that Range of a non-allied Settlement, Army or Bandit Army can't be entered or
// passed through — except by a Move that ends adjacent to that Settlement / Army to Battle or Lay Siege (its own Presence is lifted for that Move)
function auraSources(p){const M=mapState(),out=[],PR=presR();
  Object.keys(M.cells).forEach(k=>{const c=M.cells[k],q=cellPlayer(c);if(!q||sameP(q,p)||canEnterSett(p,q))return;const war=!!effPair(p.id,q.id).war;
    if(c.type==="Army"){const x=cellArmy(k),r=PR;
      out.push({k,r,kind:"battle",war:war&&!!x.a,label:q.name+" · "+(x.a?(x.a.label||("Army "+x.a.id)):"Army"),B:x.a?{pid:String(q.id),aid:String(x.a.id)}:null});}
    else{const cs=cellSett(k),r=cs.s&&settUnbuilt(cs.s)?0:PR;
      out.push({k,r,kind:"siege",war:war&&!!cs.s&&!siegeOn(q.id,cs.s.id),label:q.name+" · "+(cs.s?(cs.s.name||cs.s.tier):c.type),tp:q.id,sid:cs.s?cs.s.id:null});}});
  Object.keys(M.camps).forEach(k=>{const cp=M.camps[k];if(+cp.n<(BAN.armyThreshold||25))return;
    out.push({k,r:PR,kind:"battle",war:true,bandit:true,label:"Bandit Army @ "+k,B:{kind:"bandit",camp:k}});});
  return out.filter(o=>o.r>0);}
function moveRange(p,a,startK){const M=mapState(),g=M.grid;if(!g||!startK)return null;const V=decodeGrid(g),S_=speedOf(p,a,startK),tr=S_.tr;
  const waterOK=k=>tr.shipyard||(tr.bridges&&S_.prov.has(k));
  const AS=auraSources(p),cov={},hexes=Object.keys(V.hex);
  AS.forEach((o,i)=>{const c=hk(o.k);o.set=new Set(hexes.filter(h=>hexDist(c,hk(h))<=o.r));o.set.forEach(h=>{(cov[h]=cov[h]||[]).push(i);});});
  // ex = Presence(s) lifted for a run: a number or a Set. Starting inside non-allied Presence (ruling): it may be crossed, but the Move must end outside every Presence
  const startIn=new Set(cov[startK]||[]),lift=(...a)=>new Set([...startIn,...a]);
  const blockedX=(h,ex)=>{const L=cov[h];if(!L)return false;const E=ex instanceof Set?ex:new Set([ex]);return L.some(i=>!E.has(i));};
  // one Dijkstra over (hex, water state): 0 land, 1 on Water (must land next), 2 landed after Water (move ends); ex = the Presence lifted for this run
  const run=ex=>{const key=(k,w)=>k+"|"+w,best={},prev={},Q=[[0,startK,0]],reach={};best[key(startK,0)]=0;
    while(Q.length){Q.sort((x,y)=>x[0]-y[0]);const [d,k,w]=Q.shift();if(d>best[key(k,w)])continue;
      if(k!==startK&&w!==1&&(!reach[k]||reach[k].cost>d))reach[k]={cost:d,w,from:key(k,w)};
      if(w===2)continue;
      hexNb(k).forEach(nk=>{const h=V.hex[nk];if(!h)return;const ht=tr.mtnGrass&&h.t==="mountain"?"plains":h.t;   // Tunnellers: mountain moves as grassland
        if(terrBlocked(ht))return;if(nk!==startK&&blockedX(nk,ex))return;
        const water=terrWaterStop(ht)&&!waterOK(nk),pen=tr.ignoreTerrain?0:terrPen(ht);
        let nw;if(w===1){if(water)return;nw=2;}else nw=water?1:0;
        const nd=d+1+pen;if(nd>S_.speed)return;const kk=key(nk,nw);
        if(best[kk]===undefined||nd<best[kk]){best[kk]=nd;prev[kk]=key(k,w);Q.push([nd,nk,nw]);}});}
    const fin=(k,x)=>{const path=[];let cur=x.from;while(cur){path.unshift(cur.split("|")[0]);cur=prev[cur];}
      return Object.assign({},x,{path,strain:path.some(z=>{const h=V.hex[z];return h&&terrStrain(tr.mtnGrass&&h.t==="mountain"?"plains":h.t)&&!tr.ignoreTerrain;})});};
    return {reach,fin};};
  const dest={},base=run(lift());
  Object.keys(base.reach).forEach(k=>{const x=base.reach[k];
    if(startIn.size&&cov[k])return;                                                  // started inside a Presence: end outside all of them
    if(!M.cells[k]&&!M.camps[k])dest[k]=base.fin(k,x);
    else if(M.cells[k]&&M.cells[k].type!=="Army"&&!M.camps[k]){const cs=cellSett(k),ent=cs.s?enterCheck(p,a,cs.p,cs.s):null;
      if(ent&&ent.ok)dest[k]=Object.assign(base.fin(k,x),{enter:{pid:String(cs.p.id),sid:cs.s.id,name:cs.s.name||cs.s.tier,kick:ent.kick||null}});}});
  // Battle / Lay Siege: end adjacent to the target, through its own Presence (other non-allied Presence still blocks)
  AS.forEach((o,i)=>{if(!o.war||(o.kind==="battle"&&!o.B)||hexDist(hk(startK),hk(o.k))>S_.speed+1)return;const R_=run(lift(i));
    hexNb(o.k).forEach(k=>{const x=R_.reach[k];if(!x||k===startK||M.cells[k]||M.camps[k]||blockedX(k,lift(i)))return;   // already adjacent: use Engage in the panel
      if(dest[k]&&dest[k].engage)return;dest[k]=Object.assign(R_.fin(k,x),{engage:o});});});
  return {speed:S_,dest,aura:cov,inAura:startIn.size>0};}
function moveInfo(){const x=selArmy();if(!x)return null;const k=armyHex(x.p,x.a);if(!k)return {p:x.p,a:x.a,k:null,err:"Army is not on the map"};
  return Object.assign({k,p:x.p,a:x.a},moveRange(x.p,x.a,k)||{});}
// an Army that actually moves ends its Muster Timer, its Pillage and the Siege it is laying
function moveStops(p,a){const out=[];if(a.muster&&a.muster.n>0){delete a.muster;out.push("Muster");}else delete a.muster;
  if(a.pillage){delete a.pillage;out.push("Pillage");}
  const T=realmTimers();for(let i=T.length-1;i>=0;i--){const t=T[i];if(t.kind==="siege"&&String(t.by)===String(p.id)&&t.aid!=null&&String(t.aid)===String(a.id)){T.splice(i,1);out.push("Siege"+(t.label?" ("+t.label+")":""));}}
  return out;}
// an Army ended a Move action at hex k: other players' "ends a Move action within your Province" effects (Toll House, Beacon Towers)
function moveEndTriggers(p,k){const own=terrOwners()[k],out=[];if(!own)return out;
  D.players.forEach(q=>{if(sameP(q,p)||!own.has(String(q.id)))return;const ally=alliedP(p,q);
    if(!ally)srcMatch(q.board,"toll_extort").forEach(x=>{const t=extortGold({b:p.board},{b:q.board},+x.m[1],x.n);
      const m=q.name+" extorts "+t.toLocaleString()+" from "+p.name+" ("+x.n+")";out.push(m);noteAdd(q,m);});
    srcMatch(q.board,"toll_diplomacy").forEach(x=>{
      const m=x.n+" ("+q.name+"): may Perform a Diplomacy action targeting "+p.name+" (once per turn)";out.push(m);noteAdd(q,m);});
    if(!ally)srcMatch(q.board,"beacon_move").forEach(x=>{
      const m=x.n+" ("+q.name+"): may immediately perform a Move action";out.push(m);noteAdd(q,m);});});
  return out;}
function moveArmyTo(dk){const mi=moveInfo();if(!mi||!mi.dest||!mi.dest[dk])return false;if(armyBlocked(mi.p,mi.a)){flash("Blocked: this Army cannot perform a Move action");return false;}const M=mapState(),d=mi.dest[dk],p=mi.p,a=mi.a;
  const was=armyInside(p,a),from=was?(was.s.name||was.s.tier):mi.k;
  const ck=Object.keys(M.cells).find(k=>{const c=M.cells[k];return c.type==="Army"&&String(c.player)===String(p.id)&&cellArmy(k).a===a;});
  const old=ck?M.cells[ck]:null;if(ck)delete M.cells[ck];
  delete a.inAlly;delete a.sid;
  let kicked=[];if(d.enter){const eq=pById(d.enter.pid),es=eq&&settById(eq,d.enter.sid);if(d.enter.kick&&es)kicked=kickOut(eq,es,d.enter.kick);
    if(String(d.enter.pid)===String(p.id))a.sid=d.enter.sid;else a.inAlly={pid:d.enter.pid,sid:d.enter.sid};}
  else if(dk!==ck||!old)M.cells[dk]=Object.assign({},old||{},{type:"Army",player:p.id,aid:a.id});else M.cells[dk]=old;
  if(d.strain)a.strained=true;if(MOVEMARCH){a.endurance=Math.max(0,(a.endurance||0)-1);}
  const stopped=(d.enter||dk!==ck)?moveStops(p,a):[],trig=(d.enter||dk!==ck)?moveEndTriggers(p,dk):[];
  const owner=pById(PT(p).holdMove&&PT(p).holdMove.holderPid),hp=owner&&PT(owner).holdMove;if(hp&&hp.turn===tTurn()&&String(hp.aid)===String(a.id)){
    if(String(hp.key).startsWith("standing:"))delete (PT(owner).standingPending||{})[hp.key];
    else{PT(owner).holdingActs=PT(owner).holdingActs||{};PT(owner).holdingActs[hp.key]=tTurn();}
    delete PT(owner).holdMove;noteAdd(owner,hp.key.split(":")[1]+": Move performed by "+armyName(a));}
  flash((a.label||("Army "+a.id))+" moved "+from+" → "+(d.enter?"inside "+d.enter.name:dk)+" ("+d.cost+" of "+mi.speed.speed+")"+(d.strain?" · Strained (Barrens)":"")+(d.w===2?" · Water: move ends":"")+(kicked.length?" · pushed out: "+kicked.join(", "):"")+(stopped.length?" · ends "+stopped.join(", "):"")+(trig.length?" · "+trig.join(" · "):""));
  SEL=null;INSP=dk;
  if(d.engage){const o=d.engage;if(o.kind==="siege"){const sg=siegeState();sg.mode="Lay Siege";sg.tp=String(o.tp);sg.sid=o.sid;sg.by=String(p.id);sg.aid=String(a.id);
      if(mods().battle)D.view="battle";flash("Lay Siege: "+o.label+(mods().battle?" — Siege calculator filled":" — Siege calculator is in the Battle tab"));}
    else bqStart({kind:"battle",A:{pid:String(p.id),aid:String(a.id)},B:o.B,seize:o.bandit?"":"A",src:o.bandit?"vs Bandits":"Battle action"});}
  return true;}
function moveOverlay(R_,dx,dy,pts){const mi=moveInfo();if(!mi||!mi.dest)return "";let s="";
  Object.keys(mi.aura||{}).forEach(k=>{if(mi.dest[k])return;const [c,r]=hk(k),cx=R_+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0);
    s+='<polygon points="'+pts(cx,cy)+'" fill="#b3392f" fill-opacity=".16" stroke="#b3392f" stroke-opacity=".35" stroke-width=".8" pointer-events="none"/>';});
  Object.keys(mi.dest).forEach(k=>{const [c,r]=hk(k),cx=R_+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0),d=mi.dest[k];
    if(d.engage){s+='<polygon data-cell="'+k+'" points="'+pts(cx,cy)+'" fill="#ef5350" fill-opacity=".28" stroke="#ef5350" stroke-width="2.4" style="cursor:pointer"><title>'+k+' · '+(d.engage.kind==="siege"?"Lay Siege":"Battle")+': '+esc(d.engage.label)+' · cost '+d.cost+'</title></polygon>'+
        '<text x="'+cx.toFixed(1)+'" y="'+(cy+3).toFixed(1)+'" text-anchor="middle" font-size="7.5" font-weight="700" fill="#fff" stroke="#111" stroke-width=".4" pointer-events="none">'+(d.engage.kind==="siege"?"siege ":"⚔ ")+d.cost+'</text>';return;}
    if(d.enter){s+='<polygon data-cell="'+k+'" points="'+pts(cx,cy)+'" fill="#f3d38a" fill-opacity=".22" stroke="#f3d38a" stroke-width="2.6" style="cursor:pointer"><title>'+k+' · enter '+esc(d.enter.name)+' · cost '+d.cost+'</title></polygon>'+
        '<text x="'+cx.toFixed(1)+'" y="'+(cy-R_*.55).toFixed(1)+'" text-anchor="middle" font-size="8" font-weight="700" fill="#f3d38a" stroke="#111" stroke-width=".4" pointer-events="none">enter '+d.cost+'</text>';return;}
    s+='<polygon data-cell="'+k+'" points="'+pts(cx,cy)+'" fill="#ffffff" fill-opacity=".38" stroke="#111" stroke-width="1.4" style="cursor:pointer"><title>'+k+' · cost '+d.cost+(d.w===2?' · after Water: move ends':'')+(d.strain?' · Barrens: Strained':'')+'</title></polygon>'+
       '<text x="'+cx.toFixed(1)+'" y="'+(cy+3).toFixed(1)+'" text-anchor="middle" font-size="8" fill="#111" pointer-events="none">'+d.cost+'</text>';});
  const [c,r]=hk(mi.k),cx=R_+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0);
  s+='<polygon points="'+pts(cx,cy)+'" fill="none" stroke="#f3d38a" stroke-width="3" pointer-events="none"/>';
  return s;}
function movePanelHTML(){const mi=moveInfo();if(!mi)return "";
  if(mi.err)return '<div class="flagbox">⚑ '+esc(mi.err)+'</div>';
  const S_=mi.speed,blk=(mapState().cells[mi.k]||{}).blocked||armyBlocked(mi.p,mi.a);
  const v=armyVals(mi.a,armyUFor(mi.p));
  return '<div class="sec">Move</div><div><b>'+esc(armyName(mi.a))+'</b> — Speed <b>'+S_.speed+'</b> <span class="note">('+S_.parts.map(x=>esc(x[0])+' '+(x[1]>0?'+':'')+x[1]).join(' · ')+')</span>'+
    (S_.notes.length?'<div class="note">'+S_.notes.map(esc).join(' · ')+'</div>':'')+
    (blk?'<div class="flagbox">⚑ Blocked: can’t perform Move actions</div>':'')+
    '<div class="bcrow"><label class="note"><input type="checkbox" id="mvMarch" data-nav="1"'+(MOVEMARCH?' checked':'')+'> March</label> adjust <input id="mvAdj" data-nav="1" type="number" value="'+MOVEADJ+'" style="width:46px"> <button id="mvCancel" data-nav="1">cancel</button>'+
    ' <span class="note">'+Object.keys(mi.dest).length+' reachable · click a lit hex'+(Object.values(mi.dest).some(d=>d.enter)?' · gold = enter Settlement':'')+(Object.values(mi.dest).some(d=>d.engage)?' · red = Battle / Lay Siege':'')+(Object.keys(mi.aura||{}).length?' · shaded = non-allied Presence':'')+'</span>'+(mi.inAura?'<div class="note">Inside a non-allied Presence: may only move out of it'+(Object.keys(mi.dest).length?'':' — no exit in reach, can\u2019t move')+'.</div>':'')+'</div></div>';}

let MAPSEL=null;
function set(id,v){const e=document.getElementById(id);if(e)e.textContent=v;}
function computeAll(){recomputePC();const have=new Set(Object.keys(PC));const {earned,craft,tc}=computeEarned(have);computeTotals(have,earned,tc);renderArmy();}

