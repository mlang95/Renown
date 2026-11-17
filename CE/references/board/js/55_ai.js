// ---- AI players: culture-driven bots for seats marked AI (and, later, the headless simulator) ----
// Priorities and per-culture profiles come from the data (AI_PRIORITIES, AI_PROFILES, AI_FAITH_AVOID, AI_DIPLOMACY,
// AI_DOMAIN_POINTS). Each decision returns its choice plus a one-line reason, kept on the seat (PT(p).aiNote) for tuning.
// Decisions: Domain Points (Rest Phase), Council vote, Envoy placement, Perform (incl. Army Moves and AI-to-AI treaties),
// and Support / Oppose with Influence sized by memory (PT(p).aiMem).
function aiOn(p){return !!(p&&p.board&&PT(p).ai);}
function aiProfile(p){return ((RC.AI_PROFILES||{})[(p.board||{}).culture||""])||null;}
// the client that acts for AI seats: offline / hot-seat, the admin, or the Host's own device
// the device that runs AI seats: the Host's; with an AI Host, the device of the first seated human with a claim
function aiHumanDriver(){return seated().find(q=>!aiOn(q)&&claimOf(q))||null;}
function aiDriver(){if(!lockOn()||ADMIN)return true;const h=hostP();if(h&&!aiOn(h))return sameP(meP(),h);const d=aiHumanDriver();return !!d&&mine(d);}
function aiNote(p,txt){PT(p).aiNote={turn:tTurn(),txt};}

// ---- economy: cash positive until next Winter ----
// projected Treasury after each turn from the next Season up to and including Winter, with `extra` more upkeep per turn;
// ok = it never drops below 0
function aiCashOutlook(p,extra){const b=p.board,i0=SEAS_ORDER.indexOf(curSeason()),g0=+b.treasury||0;let g=g0,low=g;
  for(let k=1;k<=SEAS_ORDER.length;k++){const s=SEAS_ORDER[(i0+k)%SEAS_ORDER.length];g+=Math.round(seasonNet(b,s).net||0)-(extra||0);low=Math.min(low,g);if(s==="Winter")break;}
  return {ok:g>=g0,low,end:g,flow:g-g0};}   // cash positive: up to and including next Winter's tax, income covers costs (other turns may bleed)

// ---- memory: how each other player has treated this bot (votes on its Envoys, actions aimed at it, war, treaties) ----
function aiMem(p){const x=PT(p);x.aiMem=x.aiMem||{rel:{},seen:{}};return x.aiMem;}
function aiRel(p,q){return +(aiMem(p).rel[String(q.id)]||0);}
function aiRelAdd(p,q,n){const m=aiMem(p),k=String(q.id);m.rel[k]=Math.max(-20,Math.min(20,(+m.rel[k]||0)+n));}
// read this phase's resolved Envoys once each
function aiLearn(p,R){const m=aiMem(p);
  withSlots(R.envoys||[]).forEach(E=>{const key=tTurn()+":"+E.id;if(!E.done||m.seen[key])return;m.seen[key]=1;
    if(sameP(E.owner,p))(E.votes||[]).forEach(v=>{if(v.self||sameP(v.who,p))return;if(v.a==="S")aiRelAdd(p,v.who,+v.x||1);if(v.a==="O")aiRelAdd(p,v.who,-(+v.x||1));});
    else{const r=((tCur(E.owner).perform)||{})[E.id];if(r&&String(r.target)===String(p.id)&&(E.out==="Passed"||E.out==="Endorsed")){
      const A=(DATA.actions||{})[r.action]||{},hostile=/Cunning|Prowess|Piety/.test(A.domain||"")&&!/Sign Treaty|Negotiate/.test(r.action);
      aiRelAdd(p,E.owner,hostile?-2:+1);}}});
  Object.keys(m.seen).forEach(k=>{if(+k.split(":")[0]<tTurn()-1)delete m.seen[k];});}

// ---- Domain Points: one Standing at a time ----
const AI_TIERS=[["Rising",RIS],["Established",EST],["Sovereign",SOV]];
// Standings named in an unlock text ("Sovereign Cunning + Established Piety"), each expanded to the Standings below it
// "N Established" (any N Domains at that Standing): with a seat p, its lean's Domains first, then the highest others
function aiStandSteps(txt,p){const out=[],re=/(Rising|Established|Sovereign)\s+(Industry|Prowess|Cunning|Piety)/gi,T=String(txt||"");let m;
  const push=(dom,t)=>{for(let j=0;j<=t;j++)out.push({dom,tier:AI_TIERS[j][0],th:AI_TIERS[j][1]});},ti=w=>AI_TIERS.findIndex(x=>x[0].toLowerCase()===w.toLowerCase());
  while((m=re.exec(T)))push(m[2][0].toUpperCase()+m[2].slice(1).toLowerCase(),ti(m[1]));
  const any=/(\d+)\s+(?:Domains?\s+at\s+)?(Rising|Established|Sovereign)/i.exec(T);
  if(any){const dv=d=>p?+((p.board.domains||{})[d])||0:0,lean=p?aiLean(p):[];
    DOMAINS.slice().sort((x,y)=>((lean.indexOf(x)+1||99)-(lean.indexOf(y)+1||99))||dv(y)-dv(x)).slice(0,+any[1]).forEach(d=>push(d,ti(any[2])));}
  return out;}
const aiHas=(b,s)=>(+((b.domains||{})[s.dom])||0)>=s.th;
// ---- path tree (AI_PATH): a Root takes a Ward and each later Holding rides its parent free, so a seat's Wards are its chains.
// Each game a seat ranks its culture's Domains in a random order (its lean: lead, second …; Rising Industry stays open to every
// culture), aims its chains at the culture Monuments its lean reaches soonest, and walks each chain with the board's own Ambitions
// path (planGoal: the cheapest Holding line back to a Root, the Infrastructure it needs, the Standing each step unlocks at)
//   chains  Monument chains worked at once      leadW  weight of a lead-Domain point (the lead goes Sovereign anyway)
//   offW    weight of a point outside the culture's Domains (Rising Industry counts 1)
//   gearAt  aiGearNeed at which the gear branch opens (Prowess cultures always keep one)
const AI_PATH_DEF={chains:2,leadW:0.5,offW:2,gearAt:0.3};
function aiPathCfg(){return Object.assign({},AI_PATH_DEF,RC.AI_PATH||{},globalThis.AI_PATH_OVERRIDE||{});}
function aiLean(p){const x=PT(p),c=(p.board||{}).culture||"";if(x.aiLean&&x.aiLean.c===c)return x.aiLean.d;
  const L=aiDoms(p).slice();for(let i=L.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[L[i],L[j]]=[L[j],L[i]];}
  x.aiLean={c,d:L};return L;}
const aiLeanIdx=(p,d)=>{const i=aiLean(p).indexOf(d);return i<0?99:i;};
function aiDPCost(p,steps){const b=p.board,need={},C=aiPathCfg();steps.forEach(s=>{need[s.dom]=Math.max(need[s.dom]||0,s.th);});
  return Object.keys(need).reduce((t,d)=>{const gap=Math.max(0,need[d]-(+((b.domains||{})[d])||0)),k=aiLeanIdx(p,d);
    return t+gap*(k===0?C.leadW:k<99?1+0.25*k:d==="Industry"&&need[d]<=RIS?1:C.offW);},0);}
// the seat's Monument chains, best first: [{t, g (planGoal), dp, score}]; cached until its Holdings, Domains or the turn change
const AI_PLAN_C={};
function aiPlan(p){const b=p.board,key=[tTurn(),b.culture,(b.placed||[]).map(q=>q.name+(q.bt>0?"*":"")).join(","),JSON.stringify(b.domains||{}),aiLean(p).join("")].join("|");
  const c=AI_PLAN_C[p.id];if(c&&c.key===key)return c.L;
  const mine=n=>(b.placed||[]).some(x=>x.name===n),pr=aiProfile(p)||{};
  const L=(pr.monuments||[]).filter(t=>R[t]&&!mine(t)).map(t=>{const g=withBoard(b,()=>planGoal(t,planCtx()));if(g.taken)return null;
    const dp=aiDPCost(p,aiStandSteps(R[t].unlock_raw,p));return {t,g,dp,score:dp+0.7*g.left};}).filter(Boolean).sort((x,y)=>x.score-y.score);
  AI_PLAN_C[p.id]={key,L};return L;}
// the gear branch: while the seat's best kit falls short of this Era's Bandit Army (aiGearNeed) — or it is a Prowess culture — one
// chain aims at the Holding that upgrades its kit soonest (a Retinue counts most: Coliseum, War College …)
function aiGearChain(p){const b=p.board,key=[tTurn(),b.culture,(b.placed||[]).map(q=>q.name+(q.bt>0?"*":"")).join(","),JSON.stringify(b.domains||{})].join("|"),c=AI_PLAN_C["g"+p.id];
  if(c&&c.key===key)return c.v;let v=null;
  if(aiGearNeed(p)>=+aiPathCfg().gearAt||(aiProfile(p)||{}).prowess_coded){const kit=aiKit(p),mine=n=>(b.placed||[]).some(x=>x.name===n);
    v=Object.keys(ARMYSRC||{}).filter(n=>R[n]&&!mine(n)&&aiGearGain(p,n,kit)).map(t=>{const g=withBoard(b,()=>planGoal(t,planCtx()));if(g.taken)return null;
      // what the upgrade buys: the fight value against this Era's Bandit Army with that piece, over the current kit's
      const gain=aiGearGain(p,t,kit),ref=aiBanditRef(),me=Object.assign({count:+EQ.army_max||25},kit),fv0=aiFightValue(me,ref);
      const rm=gain.match(/Man-at-Arms|Sergeant|Knight Templar/),up=rm?aiFightValue(Object.assign({},me,{retinue:rm[0]}),ref)/Math.max(0.05,fv0):1.15;
      const dp=aiDPCost(p,aiStandSteps(R[t].unlock_raw,p));return {t,g,gear:true,dp,score:(dp+0.7*g.left)/Math.max(0.1,up-1)};})
      .filter(Boolean).sort((x,y)=>x.score-y.score)[0]||null;}
  AI_PLAN_C["g"+p.id]={key,v};return v;}
const aiChains=p=>{const L=aiPlan(p).slice(0,aiPathCfg().chains),g=aiGearChain(p);
  if(g&&!L.some(c=>c.t===g.t))L.splice(aiBanditThreat(p)>=0.4||aiGearNeed(p)>=0.5?0:L.length,0,g);return L;};
// steps the chains can take now: name → {t, rank, frac (share of the chain done), k ("h" Holding / "i" Infrastructure)}
function aiChainNow(p){const m=new Map();aiChains(p).forEach((c,rank)=>{const fr=c.g.total?c.g.done/c.g.total:0;
  c.g.h.concat(c.g.i).forEach(s=>{if(s.st==="now"&&!m.has(s.n))m.set(s.n,{t:c.t,rank,frac:fr,k:s.k});});});return m;}
// the Standings the next blocked step of each chain needs
function aiChainStand(p){const out=[];aiChains(p).forEach(c=>{const s=c.g.h.find(x=>x.st!=="done"&&x.st!=="building");
  if(s&&s.st==="blocked"){const st=aiStandSteps((R[s.n]||{}).unlock_raw,p).filter(x=>!aiHas(p.board,x));if(st.length)out.push({why:"chain to "+c.t+": "+s.n,steps:st});}});return out;}
// free Wards across built Settlements, and chains not yet started (their Root still to place)
function aiFreeWards(p){return withBoard(p.board,()=>S.settlements.filter(s=>!settUnbuilt(s)).reduce((t,s)=>t+Math.max(0,wardUse(s.id).free),0));}
const aiUnrooted=p=>aiChains(p).filter(c=>c.g.h.length&&c.g.h[0].st!=="done"&&c.g.h[0].st!=="building").length;
// Holdings in a chain's line whose one rider slot the chain's next step needs (a host carries one rider)
function aiReserved(p){const R_=new Set();aiChains(p).forEach(c=>{const h=c.g.h;for(let i=0;i<h.length-1;i++)if(h[i].st==="done"&&h[i+1].st!=="done"&&h[i+1].st!=="building")R_.add(h[i].n);});return R_;}
// the culture's next Monument: the head of its chain plan; with no plan, the first in its profile nobody has placed (one per game)
function aiNextMonument(p){const pr=aiProfile(p);if(!pr)return null;const c=aiPlan(p)[0];if(c)return c.t;
  return (pr.monuments||[]).find(n=>R[n]&&!D.players.some(q=>(q.board.placed||[]).some(x=>x.name===n)))||null;}
// a rival's effect that gives this player Doubt each turn while its Domain value is lower ("each other non-allied player with a
// lower Piety value gains Doubt +2"): the Domain value that stops it, while that Doubt is at least AI_SPINE.matchDoubt a turn
function aiDoubtMatch(p){const b=p.board,dv=d=>+((b.domains||{})[d])||0;let best=null;
  D.players.forEach(q=>{if(sameP(q,p)||alliedP(p,q))return;
    epSources(q.board).filter(x=>x.kind==="lower"&&x.side==="doubt").forEach(x=>{const dom=x.dom,n=x.val,th=+((q.board.domains||{})[dom])||0;
      if(n>=aiSpine().matchDoubt&&dv(dom)<th&&th<=SOV&&(!best||n>best.n))best={dom,th,n,why:"stop "+q.name+"'s "+x.src+" (Doubt +"+n+"): match "+dom+" "+th};});});
  return best;}
// goals in priority order, each a list of Standing steps; the first unmet step (lowest tier first within a goal) is the target
function aiStandGoals(p){const pr=aiProfile(p),G=[];
  const cash=aiCashOutlook(p);
  if(!cash.ok)G.push({why:"economy (Treasury "+cash.low.toLocaleString()+" before Winter)",steps:aiStandSteps("Rising Industry")});
  if(aiBanditThreat(p)>=0.4)G.push({why:"Bandits (Prowess Envoys pass)",steps:aiStandSteps("Rising Prowess")});
  {const m=aiDoubtMatch(p);if(m)G.unshift({why:m.why,steps:[{dom:m.dom,tier:"match",th:m.th}]});}
  // Builds blocked by full Wards with gold sitting idle: Rising Industry opens Settle / Expand (any culture may take it)
  {const L=buildOpts(p).filter(o=>o.v.startsWith("b:")),full=L.length?L.filter(o=>/no free Ward/.test(o.label)).length/L.length:0;
    if(full>=0.5&&(+p.board.treasury||0)>=aiSpine().expandGold)G.push({why:"room to Build (Settle / Expand)",steps:aiStandSteps("Rising Industry")});}
  aiChainStand(p).forEach(x=>G.push(x));                                                 // the next step of each Monument chain
  if(aiSurvival(p).ok&&pr&&!edictDone(p.board,"Sovereign Standing")){const dv=d=>+((p.board.domains||{})[d])||0;
    const d=aiLean(p).filter(x=>dv(x)<SOV)[0];                                             // the lead first
    if(d)G.push({why:"Edict: Sovereign "+d,steps:aiStandSteps("Sovereign "+d)});}
  const mon=aiNextMonument(p);if(mon)G.push({why:"Monument "+mon,steps:aiStandSteps(R[mon].unlock_raw,p)});
  if(pr)G.push({why:"culture Domains",steps:aiLean(p).flatMap(d=>aiStandSteps("Sovereign "+d))});
  return G;}
function aiPickDomain(p){const b=p.board,tg=PT(p).aiDP;
  if(tg&&!aiHas(b,tg)&&(+((b.domains||{})[tg.dom])||0)<SOV)return {dom:tg.dom,why:"working on "+tg.tier+" "+tg.dom+" ("+tg.why+")"};   // finish the Standing in progress
  for(const g of aiStandGoals(p)){const st=g.steps.slice().sort((x,y)=>x.th-y.th).find(s=>!aiHas(b,s));
    if(st){PT(p).aiDP={dom:st.dom,tier:st.tier,th:st.th,why:g.why};return {dom:st.dom,why:st.tier+" "+st.dom+" for "+g.why};}}
  const left=DOMAINS.filter(d=>(+((b.domains||{})[d])||0)<SOV);
  return left.length?{dom:left[0],why:"nothing needed — "+left[0]}:{dom:null,why:"every Domain at its maximum"};}
function aiSpendDP(p){let n=0;while((p.board.dp||0)>0){const c=aiPickDomain(p);if(!dpSpend(p,c.dom))break;aiNote(p,"Domain Point → "+(c.dom||"skip")+": "+c.why);n++;}return n;}

// ---- Council vote: the Domain that serves the top unmet priority ----
function aiCouncilPick(p){const b=p.board,pr=aiProfile(p),dv=d=>+((b.domains||{})[d])||0;
  if(!aiCashOutlook(p).ok)return {dom:"Industry",why:"economy"};
  {const th=aiBanditThreat(p);if(th>=0.4)return {dom:"Prowess",why:"Bandits (threat "+th.toFixed(2)+"): a sure Prowess action to Muster or Move"};}
  const tg=PT(p).aiDP;if(tg&&!aiHas(b,tg)&&T_DOMS.includes(tg.dom))return {dom:tg.dom,why:tg.tier+" "+tg.dom+" ("+tg.why+")"};
  const ds=(pr?aiLean(p):T_DOMS).filter(d=>T_DOMS.includes(d));
  const d=ds[0]||T_DOMS[0];return {dom:d,why:"lead Domain this game"};}

// ---- shared reads ----
const aiDv=(p,d)=>+(((p.board||{}).domains||{})[d])||0;
const aiMil=p=>(p.board.armies||[]).reduce((t,a)=>t+(+a.count||0),0);
const aiLike=(p,q)=>{const a=aiProfile(p),b=aiProfile(q);return !!(a&&b&&a.domains.some(d=>b.domains.includes(d)));};
const aiDoms=p=>(aiProfile(p)||{}).domains||[];
function aiEraAllows(txt){const ce=ERAS[currentEra()]||{};return Object.keys(ERAS).some(e=>(ERAS[e].renown||0)<=(ce.renown||0)&&new RegExp(txt,"i").test(ERAS[e].unlocks||""));}
// a rival worth hurting: at war, outpacing this bot on Edicts, or remembered as hostile
function aiFoe(p,q){if(effPair(p.id,q.id).war)return "at war";if(alliedP(p,q))return "";
  if(edictTotal(q)>edictTotal(p))return "ahead on Edicts ("+edictTotal(q)+" vs "+edictTotal(p)+")";if(aiRel(p,q)<=-3)return "hostile ("+aiRel(p,q)+")";return "";}
function aiFriend(p,q){const x=effPair(p.id,q.id);return alliedP(p,q)||x.trade||x.nap||aiRel(p,q)>=3;}
// gold a Holding makes each turn (flat innate gold) less its upkeep
function aiHoldNet(n){const r=R[n]||{};let g=0;(r.innate||[]).forEach(a=>{if(a.cat==="gold"&&a.flat&&!a.season&&!a.scale)g+=+a.val||0;});
  const up=r.upkeep!=null?r.upkeep:NATURAL.has(n)?0:((PUP.byType||{})[r.type]??PUP.def??0);return g-up;}
// Public Order a Holding moves each turn (flat innate Faith − Doubt); its value in gold for a bot is that × AI_PO_GOLD
function aiHoldPO(n){let v=0;((R[n]||{}).innate||[]).forEach(a=>{if(!a.flat||a.season||a.scale)return;if(a.cat==="faith")v+=+a.val||0;if(a.cat==="doubt")v-=+a.val||0;});return v;}
function aiHoldValue(n){return aiHoldNet(n)+aiHoldPO(n)*(+RC.AI_PO_GOLD||0);}
// Public Order band the plan must stay above (AI_FAITH_AVOID), given what the plan needs
function aiFaithFloor(p,needs){let k=-Infinity;(RC.AI_FAITH_AVOID||[]).forEach(([band,when])=>{if(when==="always"||when==="economy"||needs[when])k=Math.max(k,band);});return k;}
function aiBuildPick(p,econ){const L=buildOpts(p).filter(o=>o.v.startsWith("b:")&&!o.dis).map(o=>o.v.slice(2));if(!L.length)return null;
  const pr=aiProfile(p),mon=aiNextMonument(p),doms=pr?pr.domains:[];
  if(!econ&&mon&&L.includes(mon))return {sub:"b:"+mon,why:"Monument "+mon};
  const sc=n=>aiHoldValue(n)+(doms.includes(holdDom(n))?(econ?0:500):0);
  const n=L.slice().sort((a,b)=>sc(b)-sc(a))[0];return {sub:"b:"+n,why:(econ?"income: ":"Holding: ")+n+" (net "+aiHoldNet(n)+"/turn)"};}
function aiImprovePick(p){const L=improveOpts(p).filter(o=>o.v!=="hand");if(!L.length)return null;
  const walls=Object.keys(mapState().camps||{}).length?L.find(o=>/Walls/i.test(o.v)):null;
  const o=walls||L.find(x=>x.v.startsWith("i:"))||L[0];return {sub:o.v,why:(walls?"Bandits: ":"Infrastructure: ")+o.v.slice(2)};}

// ---- treaties: only between two AI seats, and only when the target would accept ----
function aiTreatyType(p,q){const x=effPair(p.id,q.id),pp=aiProfile(p)||{};
  if(x.war)return "Peace Treaty";
  if(pp.prowess_coded&&(aiProfile(q)||{}).prowess_coded&&!alliedP(p,q)){
    if(allianceOK("Military"))return "Military Alliance";if(!x.nap)return "Non-Aggression Pact";}
  if(!x.trade&&hasRoad(p.id)&&hasRoad(q.id))return "Trade Agreement";   // Trade Agreement: both need Can Trade
  if(!x.nap&&!pp.prowess_coded)return "Non-Aggression Pact";
  if(!alliedP(p,q)&&allianceOK("Defensive"))return "Defensive Alliance";
  return null;}
// would AI q accept `type` from p? Reasons: desire for war, income from trade, like-minded cultures, memory
function aiTreatyAccept(q,p,type){const dq=aiDoms(q),rel=aiRel(q,p),like=aiLike(q,p),wantsWar=(aiProfile(q)||{}).prowess_coded&&aiMil(q)>aiMil(p);
  if(rel<=-3)return {ok:false,why:"remembers "+p.name+" as hostile ("+rel+")"};
  if(type==="Peace Treaty")return wantsWar?{ok:false,why:"winning the war"}:{ok:true,why:aiCashOutlook(q).ok?"war isn't paying":"economy"};
  if(type==="Trade Agreement"){if(!hasRoad(p.id)||!hasRoad(q.id))return {ok:false,why:"needs Can Trade"};if(dq.some(d=>d==="Industry"||d==="Piety"))return {ok:true,why:"trade income"};
    if(!aiCashOutlook(q).ok)return {ok:true,why:"needs income"};if(dq.includes("Cunning"))return edictTotal(p)>edictTotal(q)?{ok:false,why:p.name+" is ahead"}:{ok:true,why:"useful for now"};
    return like?{ok:true,why:"like-minded"}:{ok:false,why:"no gain"};}
  if(type==="Non-Aggression Pact")return wantsWar?{ok:false,why:"wants war with weaker "+p.name}:{ok:true,why:"safety"};
  if(type==="Military Alliance"||type==="Defensive Alliance"){if(diplo().member[topSuz(q.id)])return {ok:false,why:"already in an Alliance"};
    if(like||rel>=3)return {ok:true,why:like?"like-minded":"trusted ("+rel+")"};
    if(dq.includes("Cunning")&&aiMil(p)>aiMil(q))return {ok:true,why:"side with the stronger"};return {ok:false,why:"no reason to ally"};}
  return {ok:false,why:"unknown treaty"};}
function aiApplyTreaty(p,q,type){const x=pairOf(p.id,q.id),d=diplo();
  if(type==="Peace Treaty"){x.war=false;x.sacredWar=false;x.truce=TRUCE_LEN;}
  else if(type==="Trade Agreement")x.trade=true;
  else if(type==="Non-Aggression Pact")x.nap=true;
  else{const t=type.split(" ")[0];let g=d.member[topSuz(p.id)];
    if(!g||(d.alliances[g]||{}).type!==t){let n=1;while(d.alliances[String(n)])n++;g=String(n);d.alliances[g]={type:t};d.member[topSuz(p.id)]=g;}
    d.member[topSuz(q.id)]=g;}
  aiRelAdd(p,q,2);aiRelAdd(q,p,2);}

// ---- Armies: outfit with the best Retinue and gear unlocked (AI_MUSTER); offensive = 2H, defensive = 1H + Shield ----
function aiOffensive(p){return !!(aiProfile(p)||{}).prowess_coded||D.players.some(q=>!sameP(q,p)&&effPair(p.id,q.id).war);}
function aiKit(p){return withBoard(p.board,()=>{const have=new Set(Object.keys(PC)),u=armyUnlocks(computeEarned(have).earned),T=EQ.tiers||[],ti=t=>t==null?-1:T.indexOf(t);
  const ret=Object.keys(EQ.retinues).filter(n=>u.retinues.has(n)).sort((a,b)=>(+EQ.retinues[b].cost||0)-(+EQ.retinues[a].cost||0)||(+EQ.retinues[a].to_hit||9)-(+EQ.retinues[b].to_hit||9))[0]||"Levy";
  const wOK=n=>{const it=EQ.weapons[n];return !EQ.prof2hOf[n]&&(tierOK(it.tier,u.wTiers)||u.anyTier.has(n))&&reqMet(it,u)&&weaponUnlockMet(n,u)&&lanceOnlyOK(n,u,true);},is2H=n=>(EQ.weapons[n].tags||[]).includes("2H");
  const best=L=>L.sort((a,b)=>ti(EQ.weapons[b].tier)-ti(EQ.weapons[a].tier)||(+EQ.weapons[a].ap||0)-(+EQ.weapons[b].ap||0))[0];
  const W=Object.keys(EQ.weapons).filter(wOK),off=aiOffensive(p);
  const weapon=(off?best(W.filter(is2H)):best(W.filter(n=>!is2H(n))))||best(W.slice())||"Farm Tools";
  const armor=Object.keys(EQ.armors).filter(n=>n==="Cloth"||u.armors.has(n)).sort((a,b)=>(+EQ.armors[a].save||99)-(+EQ.armors[b].save||99))[0]||"Cloth";
  const st=unlockedShieldTiers(u),sh=off||is2H(weapon)?"None":(Object.keys(EQ.shields).filter(k=>k!=="null"&&u.shields&&tierOK(EQ.shields[k].tier,st))
    .sort((a,b)=>(+EQ.shields[b].save_bonus||0)-(+EQ.shields[a].save_bonus||0)||ti(EQ.shields[b].tier)-ti(EQ.shields[a].tier))[0]||"None");
  return {retinue:ret,weapon,armor,shield:sh,ranged:"None",off};});}
// a newly raised Army (not yet outfitted) takes the kit; its Endurance starts at the new Retinue's
function aiGearRank(kind,n){const T=EQ.tiers||[],ti=t=>t==null?-1:T.indexOf(t);
  if(kind==="weapon"){const w=EQ.weapons[n]||{};return ti(w.tier)*100-(+w.ap||0);}
  if(kind==="armor"){const a=EQ.armors[n]||{};return 100-(+a.save||99);}
  const sh=EQ.shields[n==="None"?"null":n]||{};return n==="None"?-1:(+sh.save_bonus||0)*100+ti(sh.tier);}
// a newly raised Army takes the full kit (its Retinue, Endurance and upkeep included); an existing Army is re-equipped whenever
// better gear of its kind is unlocked — weapon, armour and Shield only, never its Retinue type, and never mid-Battle
function aiOutfit(p){let n=0;const B=battle(),inBattle=a=>!!B.id&&["A","B"].some(X=>B[X]&&String(B[X].pid)===String(p.id)&&String(B[X].aid)===String(a.id));
  (p.board.armies||[]).forEach(a=>{if(inBattle(a))return;const k=aiKit(p);if(!a.aiKit&&PT(p).aiRaiseRet&&EQ.retinues[PT(p).aiRaiseRet])k.retinue=PT(p).aiRaiseRet;const rt=EQ.retinues[k.retinue]||{};
    if(!a.aiKit){Object.assign(a,{retinue:k.retinue,weapon:k.weapon,armor:k.armor,shield:k.shield,ranged:k.ranged,aiKit:k.off?"offensive":"defensive"});
      if(!(+a.count>0)||a.endurance==null||(+a.endurance||0)<(+rt.endurance||0))a.endurance=+rt.endurance||a.endurance;a.upkeep=+rt.cost||a.upkeep;n++;
      aiNote(p,(a.label||("Army "+a.id))+" outfitted ("+a.aiKit+"): "+[k.retinue,k.weapon,k.armor,k.shield!=="None"?k.shield:""].filter(Boolean).join(", "));return;}
    const up=[];
    if(aiGearRank("weapon",k.weapon)>aiGearRank("weapon",a.weapon)){a.weapon=k.weapon;up.push(k.weapon);}
    if(aiGearRank("armor",k.armor)>aiGearRank("armor",a.armor)){a.armor=k.armor;up.push(k.armor);}
    if(k.shield!==a.shield&&(k.shield==="None"?(EQ.weapons[a.weapon]||{}).tags&&EQ.weapons[a.weapon].tags.includes("2H"):aiGearRank("shield",k.shield)>aiGearRank("shield",a.shield))){a.shield=k.shield;up.push(k.shield==="None"?"no Shield (2H)":k.shield);}
    if(up.length){n++;aiNote(p,(a.label||("Army "+a.id))+" re-equipped: "+up.join(", "));}});
  return n;}
// ---- Armies: Move like a Bandit Army (Battle > Lay Siege > March), toward Bandits and players at war ----
function aiMoveTargets(p){const M=mapState(),own=terrOwners(),T=Object.keys(M.camps||{}).filter(k=>!M.camps[k].out).map(k=>({k,n:+M.camps[k].n||0,mine:!!(own[k]&&own[k].has(String(p.id))),why:(+M.camps[k].n>=(BAN.armyThreshold||25)?"Bandit Army":"Bandit Camp")+" ("+(+M.camps[k].n||0)+") @ "+k}));
  Object.keys(M.cells).forEach(k=>{const c=M.cells[k],q=cellPlayer(c);if(q&&!sameP(q,p)&&effPair(p.id,q.id).war)T.push({k,why:q.name+(c.type==="Army"?"'s Army":"'s Settlement")});});return T;}
function aiMovable(p){return (p.board.armies||[]).filter(a=>(+a.endurance||0)>0&&!(a.muster&&a.muster.n>0)&&!armyHeld(p,a)&&armyHex(p,a)&&(+a.count||0)>0);}
// an Army hunts only at full strength (Muster to EQ.army_max first) and only engages what it outnumbers
const aiFull=a=>(+a.count||0)>=(+EQ.army_max||25);
// ---- opening spine (AI_SPINE): the rules a strong opening follows, each a knob so it can be loosened ----
//   engage     fight value (below) an Army needs before it attacks
//   huntMin    Retinues an Army needs before it hunts (it need not be full)
//   faithPO    while Bandit camps are out and Public Order is at or below this, Faith Holdings serve the faith priority fully
//   expandGold Treasury at which full Wards send the next Domain Point to Rising Industry (Settle / Expand)
//   matchDoubt a rival's "lower Domain value gains Doubt" effect this strong a turn is matched with Domain Points
//   defend     a Bandit Army this many hexes from one of the seat's Settlements is met before any hunt (0 = off)
//   books      1 = an Insolvent seat cuts as the rules order it (Disband Armies, then Shutter) and restores what it can pay
//   pillageEngage  fight value an Army needs to Battle a Bandit Army Pillaging one of the seat's Settlements
//   retire     1 = raise Armies of a better Retinue as it unlocks and disband the weakest once the new one is full
const AI_SPINE_DEF={engage:1.3,huntMin:10,faithPO:0,expandGold:4000,matchDoubt:2,defend:4,books:1,pillageEngage:0.6,retire:1};
function aiSpine(){return Object.assign({},AI_SPINE_DEF,RC.AI_SPINE||{},globalThis.AI_SPINE_OVERRIDE||{});}
// fight value of Army a against Army b: Lanchester square law on expected casualties per Skirmish. Each side's rate is its
// front line (10 at most) × chance to Strike (to-Strike after the target's Shielded, less Hook) × chance the target's Save
// fails (armour after AP and Shield bonus), scaled by its whole size. Above 1 = a favours itself.
function aiKitOf(a){return {ret:a.retinue||"Levy",w:a.weapon||"Farm Tools",ar:a.armor||"Cloth",sh:a.shield&&a.shield!=="None"?a.shield:"null",n:+a.count||0};}
function aiHitRate(x,y){const r=EQ.retinues[x.ret]||{},w=EQ.weapons[x.w]||{},ys=EQ.shields[y.sh]||{},F=BT.faces||10;
  const tag=(L,re)=>{for(const t of L||[]){const m=String(t).match(re);if(m)return m[1]!=null?+m[1]:1;}return 0;};
  const shielded=tag(ys.tags,/^Shielded(?: (\d+))?$/),hook=(ys.tags||[]).includes("Immune Hook")?0:tag(w.tags,/^Hook (\d+)$/);
  const toHit=Math.min(F,(+r.to_hit||6)+Math.max(0,shielded-hook));
  const need=(+(EQ.armors[y.ar]||{}).save||F)-(+w.ap||0)-(+ys.save_bonus||0);           // AP is negative: it raises what the Save needs
  return Math.max(0,Math.min(1,(F+1-toHit)/F))*(1-Math.max(0,Math.min(1,(F+1-need)/F)));}
function aiFightValue(a,b){const x=aiKitOf(a),y=aiKitOf(b),fx=Math.min(x.n,10),fy=Math.min(y.n,10);
  return (aiHitRate(x,y)*fx*x.n+1e-9)/(aiHitRate(y,x)*fy*y.n+1e-9);}
// would Army a take on side B (a Bandit camp {kind:"bandit",camp} or a player's Army {pid,aid})?
function aiBeats(a,B){const o=B&&sideArmy(B).a;if(!o||!(+o.count>0))return !!o;return (+a.count||0)>=aiSpine().huntMin&&aiFightValue(a,o)>=aiSpine().engage;}
// gold cost of an action, read from its Cost text ("4000 gold")
function aiActCost(act){const m=String(((DATA.actions||{})[act]||{}).cost||"").match(/(\d[\d,]*)\s*gold/i);return m?+m[1].replace(/,/g,""):0;}
// ---- gear climb: this Era's Bandit Army (its loadout at BANDIT_ARMY_THRESHOLD Retinues) against the seat's best full Army ----
function aiBanditRef(){const lo=(banLO()||{})[currentEra()]||{},rn=lo.retinue&&EQ.retinues[lo.retinue]?lo.retinue:BANDIT_DEFAULT_RETINUE;
  return {retinue:rn,weapon:lo.weapon||"",armor:lo.armor||"",shield:lo.shield||"None",count:BAN.armyThreshold||25};}
// 0 = the best kit already beats it by AI_SPINE.engage; 1 = far short (gear Holdings and Retinues gain weight)
function aiGearNeed(p){const k=aiKit(p),v=aiFightValue({retinue:k.retinue,weapon:k.weapon,armor:k.armor,shield:k.shield,count:+EQ.army_max||25},aiBanditRef()),e=aiSpine().engage;
  return Math.max(0,Math.min(1,2*(e-v)/e));}
// ---- home defence: Bandit Armies within AI_SPINE.defend hexes of the seat's Settlements, nearest first ----
function aiHomeThreats(p){const M=mapState(),cap=BAN.armyThreshold||25,r=+aiSpine().defend||0,out=[];if(!r)return out;
  const S_=mapSetts().filter(x=>String(x.cell.player)===String(p.id));
  Object.keys(M.camps||{}).forEach(k=>{const cp=M.camps[k];if(!(+cp.n>=cap))return;
    S_.forEach(x=>{const d=hexDist(hk(x.k),hk(k)),pill=!!(cp.pillage&&String(cp.pillage.tp)===String(p.id)&&String(cp.pillage.sid)===String(x.cell.sid));
      if(d<=r||pill)out.push({k,n:+cp.n,sk:x.k,sid:x.cell.sid,d,pill});});});
  return out.sort((a,b)=>b.pill-a.pill||a.d-b.d||b.n-a.n);}
// a Pillage runs "until it fights a Battle or leaves": a Battle ends it even if lost, so a Pillaging Bandit Army is engaged at the
// lower bar AI_SPINE.pillageEngage
const aiDefBeats=(a,t)=>{const B={kind:"bandit",camp:t.k},o=sideArmy(B).a;if(!t.pill)return aiBeats(a,B);
  return !!o&&(+a.count||0)>=aiSpine().huntMin&&aiFightValue(a,o)>=aiSpine().pillageEngage;};
function aiMoveTo(p,a,h){const view=D.view;SEL={pid:String(p.id),aid:String(a.id)};let ok=false;try{ok=moveArmyTo(h);}finally{SEL=null;D.view=view;}return ok;}
// meet the nearest threat: an Army that beats it Battles it (now, or Moves to engage); if none can, the nearest Army not already
// inside goes into the threatened Settlement (it then fights the Siege with the Walls). keep = Armies holding a threatened Settlement
function aiDefend(p){const T=aiHomeThreats(p),keep=new Set();if(!T.length)return {msg:"",keep};const A=aiMovable(p),nm=a=>a.label||("Army "+a.id);
  T.forEach(t=>A.forEach(a=>{const x=armyInside(p,a);if(x&&String(x.s.id)===String(t.sid))keep.add(a);}));
  for(const t of T){const B={kind:"bandit",camp:t.k},o=sideArmy(B).a;
    for(const a of A.filter(a=>aiDefBeats(a,t)).sort((x,y)=>aiFightValue(y,o)-aiFightValue(x,o))){
      const E=engageTargets(p,a).find(e=>e.kind==="battle"&&e.B&&e.B.camp===t.k);
      if(E){bqAdd({kind:"battle",A:{pid:String(p.id),aid:String(a.id)},B:E.B,seize:E.seize,src:E.src});return {msg:nm(a)+": defend "+t.sk+" — Battle "+E.label,keep};}
      const k=armyHex(p,a),mi=k&&moveRange(p,a,k),d=mi&&mi.dest?Object.keys(mi.dest).map(h=>Object.assign({h},mi.dest[h])).filter(d=>d.engage&&d.engage.kind==="battle"&&d.engage.B&&d.engage.B.camp===t.k).sort((x,y)=>x.cost-y.cost)[0]:null;
      if(d&&aiMoveTo(p,a,d.h))return {msg:nm(a)+" → "+d.h+": defend "+t.sk+" — Battle Bandit Army ("+t.n+")",keep};}
    if(A.some(a=>keep.has(a))||t.pill)continue;                                           // already held; walls don't stop a Pillage
    for(const a of A.slice().sort((x,y)=>hexDist(hk(armyHex(p,x)),hk(t.sk))-hexDist(hk(armyHex(p,y)),hk(t.sk)))){if(armyInside(p,a))continue;
      const k=armyHex(p,a),mi=k&&moveRange(p,a,k);if(!mi||!mi.dest)continue;const D_=Object.keys(mi.dest).map(h=>Object.assign({h},mi.dest[h]));
      const inn=D_.find(d=>d.enter&&String(d.enter.pid)===String(p.id)&&String(d.enter.sid)===String(t.sid));
      if(inn&&aiMoveTo(p,a,inn.h)){keep.add(a);return {msg:nm(a)+" → "+inn.h+": holds "+(inn.enter.name||"Settlement")+" against a Bandit Army ("+t.n+")",keep};}
      const d0=hexDist(hk(k),hk(t.sk)),c=D_.filter(d=>!d.engage&&!d.enter).sort((x,y)=>hexDist(hk(x.h),hk(t.sk))-hexDist(hk(y.h),hk(t.sk))||x.cost-y.cost)[0];
      if(c&&hexDist(hk(c.h),hk(t.sk))<d0&&aiMoveTo(p,a,c.h))return {msg:nm(a)+" → "+c.h+": back to defend "+t.sk,keep};}}
  return {msg:"",keep};}
// ---- Insolvency & Bankruptcy (RULES), as the seat's player does it: while the Treasury is below 0 and the books don't balance (base
// income short of costs), Disband Armies one at a time, cheapest Supply first; then set pieces Shuttered — Wonders, Monuments,
// Infrastructure, non-Natural Holdings, highest Upkeep first. A Shuttered piece comes back once the Treasury and income pay for it.
function aiDisband(p,a){const M=mapState();Object.keys(M.cells).forEach(k=>{const c=M.cells[k];if(c.type==="Army"&&String(c.player)===String(p.id)&&String(c.aid)===String(a.id))delete M.cells[k];});
  p.board.armies=(p.board.armies||[]).filter(x=>x!==a);D.bqueue=bq().filter(o=>![o.A,o.B].some(s=>s&&String(s.pid)===String(p.id)&&String(s.aid)===String(a.id)));}
// retire: once an Army of a better Retinue is at full strength, the weakest-Retinue Army is disbanded (its Supply pays for the new one);
// at the Era's Army cap, with no Bandit Army at the door and the better Army affordable, the weakest is disbanded first to make room
function aiRetire(p){if(!+aiSpine().retire)return 0;const b=p.board,A=(b.armies||[]).filter(a=>(+a.count||0)>0||(a.muster&&a.muster.n>0)),rc=a=>+((EQ.retinues[a.retinue]||{}).cost)||0;
  if(!A.length)return 0;const B=battle(),busy=a=>!!B.id&&["A","B"].some(X=>B[X]&&String(B[X].pid)===String(p.id)&&String(B[X].aid)===String(a.id));
  const weak=A.slice().sort((x,y)=>rc(x)-rc(y))[0];if(!weak||busy(weak))return 0;
  if(A.some(a=>a!==weak&&rc(a)>rc(weak)&&aiFull(a))&&A.length>=2){aiDisband(p,weak);aiNote(p,"Retire "+(weak.label||("Army "+weak.id))+" ("+weak.retinue+"): replaced by a full Army of a better Retinue");return 1;}
  const best=aiKit(p).retinue,capA=withBoard(b,()=>eraCap("armies"));
  if(capA!=null&&(b.armies||[]).length>=capA&&(+((EQ.retinues[best]||{}).cost)||0)>rc(weak)&&!A.some(a=>a.retinue===best)&&!aiHomeThreats(p).length
     &&aiCashOutlook(p,(+((EQ.retinues[best]||{}).cost)||0)-rc(weak)).ok){aiDisband(p,weak);aiNote(p,"Retire "+(weak.label||("Army "+weak.id))+" ("+weak.retinue+") to raise "+best+" (Army cap)");return 1;}
  return 0;}
function aiBooks(p){if(!+aiSpine().books)return 0;const b=p.board,base=()=>Math.round(seasonNet(b).base||0);let n=0;
  const pieces=()=>withBoard(b,()=>{itm();const L=[],freeT=noUpkeepTiers();
    Object.keys(S.wonders||{}).forEach(k=>L.push({g:0,k,up:(WON[k]||{}).upkeep||0,on:infraOn(k),shut:!!S.ishut[k],set:v=>{if(v)S.ishut[k]=1;else delete S.ishut[k];}}));
    S.placed.forEach(x=>{if(x.fac||NATURAL.has(x.name)||x.bt>0||x.dmg>0)return;const was=x.shut;x.shut=false;const up=pursuitUpkeep(x);x.shut=was;
      L.push({g:(R[x.name]||{}).monument?1:3,k:x.name,up,on:!x.shut,shut:!!x.shut,set:v=>{if(v)x.shut=true;else delete x.shut;}});});
    Object.keys(S.infra||{}).forEach(k=>{if(S.facInfra.includes(k)||(INFRA[k]&&freeT[INFRA[k].tier])||S.itimer[k]>0||S.idmg[k]>0)return;
      L.push({g:2,k,up:(INFRA[k]||{}).upkeep||0,on:!S.ishut[k],shut:!!S.ishut[k],set:v=>{if(v)S.ishut[k]=1;else delete S.ishut[k];}});});
    return L.filter(x=>x.up>0);});
  if((+b.treasury||0)<0){
    while(base()<0&&(b.armies||[]).length){const a=b.armies.slice().sort((x,y)=>armyUpkeep(x)-armyUpkeep(y))[0];aiDisband(p,a);n++;aiNote(p,"Insolvent: Disband "+(a.label||("Army "+a.id))+" ("+armyUpkeep(a)+" "+SUPPLY()+")");}
    for(const x of pieces().filter(x=>x.on).sort((x,y)=>x.g-y.g||y.up-x.up)){if(base()>=0)break;withBoard(b,()=>x.set(true));n++;aiNote(p,"Insolvent: "+x.k+" Shuttered ("+x.up+" "+UPKEEP()+")");}}
  else if(!b.insolvent)for(const x of pieces().filter(x=>x.shut).sort((x,y)=>x.up-y.up)){
    if((+b.treasury||0)<x.up||base()-x.up<0)break;withBoard(b,()=>x.set(false));n++;aiNote(p,x.k+" restored");}
  return n;}
function aiEngageSize(o){if(!o||!o.B)return Infinity;if(o.B.kind==="bandit"){const cp=mapState().camps[o.B.camp];return cp?+cp.n||0:Infinity;}
  const q=pById(o.B.pid),a=q&&(q.board.armies||[]).find(x=>String(x.id)===String(o.B.aid));return a?+a.count||0:Infinity;}
function aiMove(p){const df=aiDefend(p);if(df.msg)return df.msg;
  const T=aiMoveTargets(p);if(!T.length)return "no target";
  const engage=(a)=>{const E=engageTargets(p,a).filter(t=>t.kind==="battle"&&aiBeats(a,t.B));   // RULES: end adjacent, then Battle
    const t=E.sort((x,y)=>aiEngageSize(x)-aiEngageSize(y))[0];if(!t)return null;bqAdd({kind:"battle",A:{pid:String(p.id),aid:String(a.id)},B:t.B,seize:t.seize,src:t.src});return t.label;};
  for(const a of aiMovable(p).filter(a=>!df.keep.has(a)).sort((x,y)=>(+y.count||0)-(+x.count||0))){
    {const e=engage(a);if(e)return (a.label||("Army "+a.id))+": Battle "+e;}                    // already beside something it can beat
    const k=armyHex(p,a),mi=moveRange(p,a,k);if(!mi||!mi.dest)continue;const D_=Object.keys(mi.dest).map(h=>Object.assign({h},mi.dest[h]));
    const eng=t=>D_.filter(d=>d.engage&&d.engage.kind===t&&(t!=="battle"||aiBeats(a,d.engage.B))).sort((x,y)=>x.cost-y.cost)[0];
    let pick=eng("battle"),why=pick?"Battle: "+pick.engage.label:"";
    if(!pick&&(aiFull(a)||((aiProfile(p)||{}).prowess_coded&&(+a.count||0)>=15))){pick=eng("siege");why=pick?"Lay Siege: "+pick.engage.label:"";}
    if(!pick){const huntable=T.filter(t=>t.n==null||aiBeats(a,{kind:"bandit",camp:t.k}));
      const warFirst=(aiProfile(p)||{}).prowess_coded&&aiBanditThreat(p)<0.6,isWar=t=>t.n==null;   // war targets carry no camp size
      const tg=huntable.slice().sort((x,y)=>(warFirst?(isWar(y)-isWar(x)):0)||(y.mine-x.mine)||((y.n||0)-(x.n||0))||hexDist(hk(k),hk(x.k))-hexDist(hk(k),hk(y.k)))[0];
      if(tg){const d0=hexDist(hk(k),hk(tg.k));
        const c=D_.filter(d=>!d.engage&&!d.enter).sort((x,y)=>hexDist(hk(x.h),hk(tg.k))-hexDist(hk(y.h),hk(tg.k))||x.cost-y.cost)[0];
        if(c&&hexDist(hk(c.h),hk(tg.k))<d0){pick=c;why="March toward "+tg.why;}}}
    if(!pick)continue;
    const view=D.view;SEL={pid:String(p.id),aid:String(a.id)};const ok=moveArmyTo(pick.h);SEL=null;D.view=view;
    if(ok&&pick.engage&&pick.engage.kind==="siege"){   // Lay Siege: the Move fills the Siege calculator; start its Siege Timer as the player would
      const q=pById(pick.engage.tp),st=q&&settById(q,pick.engage.sid),sg=siegeState();
      if(q&&st&&!siegeOn(q.id,st.id)){sg.mode="Lay Siege";sg.tp=String(q.id);sg.sid=st.id;sg.by=String(p.id);sg.aid=String(a.id);sg.army=armiesInside(q,st).length>0;
        const c=siegeCalc();realmTimers().push({type:"Siege Timer",label:p.name+" → "+q.name+" · "+(st.name||st.tier),n:c.total,kind:"siege",tp:q.id,sid:st.id,by:p.id,aid:a.id});
        return (a.label||("Army "+a.id))+" → "+pick.h+": "+why+" · Siege Timer "+c.total;}}
    if(ok){const e=pick.engage?null:engage(a);return (a.label||("Army "+a.id))+" → "+pick.h+": "+why+(e?" · Battle "+e:"");}}
  return "no Army can reach a target";}

// ---- Envoys: every action of every Domain is scored against the priorities it serves ----
// weight of a priority = its place in AI_PRIORITIES (first = highest); an action's value for a priority is 0..1 (how much it
// helps × how much that priority is needed now). score = best weighted value + a third of the others.
// Edicts stay last while survival is in question; once it's met (aiSurvival) they rise to the top
function aiPrioW(k,surv){const L=(RC.AI_PRIORITIES||[]).map(x=>x[0]),i=L.indexOf(k);if(i<0)return 0;return k==="edicts"&&surv?L.length+0.5:L.length-i;}
function aiScore(serves,surv){const v=Object.keys(serves).map(k=>aiPrioW(k,surv)*serves[k]).filter(x=>x>0).sort((a,b)=>b-a);return v.length?v[0]+v.slice(1).reduce((t,x)=>t+x/3,0):0;}
const aiTop=(serves,surv)=>Object.keys(serves).sort((a,b)=>aiPrioW(b,surv)*serves[b]-aiPrioW(a,surv)*serves[a])[0]||"";
// survival: cash positive to Winter, Public Order clear of its floor, no war, and Bandits answered (no camps, or an Army)
function aiSurvival(p){const b=p.board,why=[];if(!aiCashOutlook(p).ok)why.push("economy");
  if((+b.po||0)-1<=aiFaithFloor(p,{}))why.push("faith");
  if(D.players.some(q=>!sameP(q,p)&&effPair(p.id,q.id).war))why.push("war");
  if(aiBanditThreat(p)>=0.4)why.push("bandits");
  return {ok:!why.length,why};}
// chance an Envoy of `dom` passes: the bot's innate Influence plus how each other player is expected to vote on it
// (AI seats: their actual vote rule; others: this bot's memory of them)
function aiPassChance(p,dom){let net=innateInf(p,dom,false);
  D.players.forEach(q=>{if(sameP(q,p)||!seated().includes(q))return;const cap=Math.max(1,voteCap(q,dom,false));
    if(aiOn(q)){const v=aiVoteWant(q,{owner:p,dom,council:false});net+=v.a==="S"?v.x:v.a==="O"?-v.x:0;return;}
    if(effPair(p.id,q.id).war||aiRel(p,q)<=-3)net-=cap;else if(aiFriend(p,q))net+=1;});
  let c=net>=ETH.Endorsed?1.15:net>=ETH.Passed+1?1:net>=ETH.Passed?0.75:net>ETH.Condemned?0.35:0.1;
  if(dom==="Industry"&&!D.players.some(q=>!sameP(q,p)&&effPair(p.id,q.id).war))c=Math.max(c,1);   // at peace nobody bothers to Oppose Industry
  return {net,c};}
// ---- Archetype (AI_ARCHETYPE): "<pace> <style>" words merged into one set of multipliers ----
function aiArch(p){const A=RC.AI_ARCHETYPE||{},w=String((aiProfile(p)||{}).archetype||"").split(/\s+/),out={prio:{},tags:{},reserve:0,lead:1,need_amp:1,vote:1,name:w.join(" ")};
  w.forEach(k=>{const e=A[k];if(!e)return;Object.entries(e.prio||{}).forEach(([x,v])=>out.prio[x]=(out.prio[x]||1)*v);Object.entries(e.tags||{}).forEach(([x,v])=>out.tags[x]=(out.tags[x]||1)*v);
    out.reserve+=+e.reserve||0;out.lead*=+e.lead||1;out.need_amp*=+e.need_amp||1;out.vote*=+e.vote||1;});return out;}
// ---- Domain styles (AI_STYLE): which ways of meeting economy / faith / bandits this culture uses ----
function aiStyle(p,k){const S_=((RC.AI_STYLE||{})[k])||{},out=new Set();aiDoms(p).forEach(d=>(S_[d]||[]).forEach(t=>out.add(t)));return out;}
// would Holding n upgrade this bot's Army kit? (ARMYSRC tokens: tier:<weapon tier>, armor:<tier>, retinue:<name>) — the gear path
function aiGearGain(p,n,kit){const src=ARMYSRC[n];if(!src)return "";const T=EQ.tiers||[],ti=t=>T.indexOf(t),out=[];
  const wt=ti((EQ.weapons[kit.weapon]||{}).tier),at=ti((EQ.armors[kit.armor]||{}).tier),rc=+((EQ.retinues[kit.retinue]||{}).cost)||0;
  [].concat(src.innate||[],src.mastery||[]).map(String).forEach(t=>{const [k,v]=t.split(":");
    if(k==="tier"&&ti(v)>wt)out.push(v+" weapons");if(k==="armor"&&ti(v)>at)out.push(v+" armour");
    if(k==="retinue"&&(+((EQ.retinues[v]||{}).cost)||0)>rc)out.push(v);});
  return out.join(", ");}
// a Holding's style tags, read from its own text
function aiHoldTags(n){const r=R[n]||{},t=String(r.innate_raw||""),T=new Set(),net=aiHoldNet(n),up=r.upkeep!=null?+r.upkeep:0;
  if(net>0){T.add("holding_income");if(r.root)T.add("hamlet_income");}
  if(/infrastructure[^.;]*upkeep|upkeep[^.;]*infrastructure/i.test(t))T.add("infra_upkeep");
  if(new RegExp(SUPPLY()+"\\s*-\\s*\\d","i").test(t))T.add("army_upkeep");
  if(/Extort/i.test(t))T.add("extort");
  if(/Can Trade|Trade Income|Trade Partner/i.test(t))T.add("trade");
  if(/Doubt[^.;]*(reduced|Immune)|Immune[^.;]*Doubt/i.test(t))T.add("po_insulate");
  if((r.innate||[]).some(a=>a.cat==="faith"&&(+a.val||0)>0)||/Faith \+\d/i.test(t))T.add("faith_gain");
  if(/Bandit/i.test(t))T.add("harness");
  if(/Siege/i.test(t))T.add("ignore_siege");
  if((r.innate||[]).some(a=>a.cat==="combat"))T.add("equip_armies");
  if(up<=100)T.add("low_costs");
  return T;}
// an action's style tags
function aiActTags(c){const T=new Set();const A=c.act;
  if(A==="Build"&&c.sub){aiHoldTags(c.sub.slice(2)).forEach(t=>T.add(t));if(c.gear)T.add("equip_armies");}
  if(A==="Sign Treaty"&&c.treaty==="Trade Agreement")T.add("trade");
  if(A==="Tithe")T.add("tithe");
  if(A==="Pillage")T.add("pillage");
  if(A==="Declare War"){T.add("battle");T.add("war_lowers");T.add("martial_lowers");}
  if(A==="Move"){if(c.bandit)T.add("bandit_hunt");if(c.siege)T.add("sack");if(c.war){T.add("battle");T.add("martial_lowers");}}
  if(A==="Pillage")T.add("martial_lowers");
  if(c.dom==="Cunning"&&c.tgt)T.add("cunning_lowers");
  if(A==="Muster"){T.add("train");T.add("basic_armies");if(c.bandit)T.add("bandit_hunt");}
  if(c.dom==="Cunning")T.add("extort");
  if(/Raze|Sabotage|Intercept Caravan|Destabilize/.test(A))T.add("damage");
  if(A==="Foster Rebellion")T.add("harness");
  if(A==="Spread Truth"||(A==="Send Missionaries"&&!String(c.tgt||"").startsWith("al:"))){T.add("po_control");T.add("war_lowers");}
  if(A==="Improve"&&/Walls/i.test(c.sub||""))T.add("walls");
  return T;}
// how much this bot needs Public Order work, by its faith style
function aiFaithNeed(p,st){const po=+p.board.po||0,gap=Math.max(0,PO_MAX-po)/Math.max(1,PO_MAX-PO_MIN),rv=Math.max(-99,...D.players.filter(q=>!sameP(q,p)&&seated().includes(q)).map(q=>+q.board.po||0));let n=0;
  if(st.has("po_saints")&&po<PO_MAX)n=Math.max(n,0.5+gap);                          // Piety: all the way to Living Saints
  if(st.has("po_cheap")&&po<PO_MAX)n=Math.max(n,0.3+gap);                           // Industry: as high as it goes, cheaply
  if(st.has("po_above_rivals"))n=Math.max(n,po<=rv?0.9:0.2);                        // Prowess / Cunning: stay above the rivals
  if(st.has("po_insulate")&&po<0)n=Math.max(n,0.7);
  if(st.has("po_control"))n=Math.max(n,0.3);                                         // Piety uses Public Order as leverage
  return Math.min(1,n);}
// Bandit threat to this player, 0..1 — kill camps before they become Armies: each camp in its Province or Outlaw Country counts
// more the closer it is to BANDIT_ARMY_THRESHOLD; then Bandit Armies within reach of its Settlements (Range 6) and Bandit Sieges on them
function aiBanditThreat(p){const M=mapState(),own=terrOwners(),mine=new Set(outlawOf(p)),setts=mapSetts().filter(x=>String(x.cell.player)===String(p.id)).map(x=>hk(x.k)),cap=BAN.armyThreshold||25,
    eraW=1+0.25*Math.max(0,Object.keys(ERAS).indexOf(currentEra()));   // Founding ×1 … Zenith ×1.75
  let local=0,near=0;Object.keys(M.camps||{}).forEach(k=>{const cp=M.camps[k],n=+cp.n||0;
    if(!cp.out&&!cp.home&&(mine.has(k)||(own[k]&&own[k].has(String(p.id)))))local+=(0.25+0.5*Math.min(1,n/cap))*eraW;
    if(n>=cap&&setts.some(s=>hexDist(s,hk(k))<=6))near++;});
  const sieges=realmTimers().filter(t=>t.kind==="siege"&&t.bandit&&String(t.tp)===String(p.id)).length+Object.values(M.camps||{}).filter(c=>c.pillage&&String(c.pillage.tp)===String(p.id)).length;   // Bandit Sieges or Pillages on its Settlements
  return Math.min(1,local+0.4*near+0.8*sieges);}
function aiBanditNear(p){const M=mapState(),cap=BAN.armyThreshold||25,setts=mapSetts().filter(x=>String(x.cell.player)===String(p.id)).map(x=>hk(x.k));
  return Object.keys(M.camps||{}).some(k=>+M.camps[k].n>=cap&&setts.some(s=>hexDist(s,hk(k))<=6));}
// the situation every scorer reads, computed once per decision
function aiSit(p){const b=p.board,others=D.players.filter(q=>!sameP(q,p)&&seated().includes(q)),cash=aiCashOutlook(p),h=hudData(p);
  const foes=others.map(q=>({q,why:aiFoe(p,q)})).filter(x=>x.why).sort((x,y)=>(effPair(p.id,y.q.id).war?1:0)-(effPair(p.id,x.q.id).war?1:0)||edictTotal(y.q)-edictTotal(x.q));
  const pass={};T_ALL.forEach(d=>pass[d]=aiPassChance(p,d));
  const W=+RC.WEALTH_EDICT_GOLD||0;
  return {b,others,cash,econ:cash.ok?(aiDoms(p).includes("Industry")?0.6:0.3):1,doms:aiDoms(p),pr:aiProfile(p)||{},foes,war:others.filter(q=>effPair(p.id,q.id).war),
    camps:Object.keys(mapState().camps||{}).length,bthreat:aiBanditThreat(p),h,po:+b.po||0,surv:aiSurvival(p),pass,
    wealth:W>0?Math.min(1,Math.max(0,+b.treasury||0)/W):0,saints:Math.max(0,+b.po||0)/PO_MAX,
    spare:Math.min(1,Math.max(0,+b.treasury||0)/15000),                                 // gold sitting idle wants investing
    gearNeed:aiGearNeed(p),                                                              // the best kit can't take this Era's Bandit Army
    wardFull:(()=>{const L=buildOpts(p).filter(o=>o.v.startsWith("b:"));return L.length?L.filter(o=>/no free Ward/.test(o.label)).length/L.length:0;})()};}
// candidates: {dom, act, tgt, sub, treaty, serves:{priority:value}, cost, doubt, why}
function aiCandidates(p){const s=aiSit(p),b=s.b,C=[],add=(dom,act,o)=>C.push(Object.assign({dom,act,cost:0,doubt:0},o));
  const like=d=>s.doms.includes(d)?1:0.6,foe=s.foes[0],foeQ=foe&&foe.q,fp=foe?(effPair(p.id,foeQ.id).war?"diplomacy":edictTotal(foeQ)>edictTotal(p)?"edicts":"diplomacy"):"";
  // Industry
  const CN=aiChainNow(p),scarce=aiFreeWards(p)<=aiUnrooted(p),RSV=aiReserved(p),have=new Set((b.placed||[]).map(x=>x.name));   // chain steps open now; Wards left only for the chains' own Roots
  {const L=buildOpts(p).filter(o=>o.v.startsWith("b:")&&!o.dis).map(o=>o.v.slice(2)),mons=new Set(aiChains(p).filter(c=>!c.gear).map(c=>c.t)),mon=aiNextMonument(p),kit=aiKit(p);
    L.forEach(n=>{const net=aiHoldNet(n),po=aiHoldPO(n),val=aiHoldValue(n),dm=s.doms.includes(holdDom(n)),gear=aiGearGain(p,n,kit),cs=CN.get(n);
      const rides=withBoard(b,()=>{const sd=smartSid(n);return sd!=null&&!!canPlace(n,sd).rider;}),opens=((R[n]||{}).builds_into||[]).filter(x=>R[x]).length;
      const armyCut=s.pr.prowess_coded&&new RegExp(SUPPLY()+"\\s*-\\s*\\d","i").test(String((R[n]||{}).innate_raw||""))&&(b.armies||[]).length>0;   // Prowess: cheaper Armies
      // a Holding that adds Doubt every turn counts against the faith priority — harder the lower Public Order already is
      let pen=po<0?aiPrioW("faith")*0.5*(-po)*(s.po<=0?1:0.6):0;
      if((R[n]||{}).root&&!cs&&!rides&&scarce)pen+=aiPrioW("holdings")*0.6;               // a stray Root would take a chain's Ward
      {const hs=effList(n).filter(h=>have.has(h));if(!cs&&hs.length&&hs.every(h=>RSV.has(h)))pen+=aiPrioW("holdings")*0.8;}   // nor ride a host the chain needs
      // a Holding that upgrades the Army kit answers Bandits (and war): Bandit gear climbs with the Era
      add("Industry","Build",{sub:"b:"+n,cost:2000,pen,gear:!!gear,serves:{faith:po>0&&s.po<=aiSpine().faithPO?1:0,economy:val>0&&net>0?Math.max(0.5,s.econ)*Math.min(1,val/1000):0,holdings:Math.min(1,(dm?0.8:0.5)*like("Industry")+0.5*s.spare+(rides?0.3:0)+Math.min(0.2,0.05*opens)+(armyCut?0.4:0)+(cs?0.6-0.2*cs.rank:0)+(gear?0.3*s.gearNeed:0)),
          monuments:mons.has(n)||n===mon?1:cs?Math.max(0.4,0.7+0.3*cs.frac-0.15*cs.rank):0,
          bandits:gear||(cs&&(aiGearChain(p)||{}).t===cs.t)?(s.pr.prowess_coded?0.6:0.3)+0.6*s.bthreat+0.6*s.gearNeed:0,diplomacy:gear&&(s.war.length||s.pr.prowess_coded)?0.6:0},
        why:(mons.has(n)?"Monument ":cs?"chain to "+cs.t+": ":"Build ")+n+" (net "+net+"/turn"+(po?", PO "+(po>0?"+":"")+po+"/turn":"")+(gear?", unlocks "+gear:"")+(rides?", rides free":"")+(armyCut?", cuts Army upkeep":"")+")"});});}
  {const L=improveOpts(p).filter(o=>o.v!=="hand"),w=L.find(o=>o.v.startsWith("w:")&&!o.wb),ip=aiImprovePick(p);
    if(w)add("Industry","Improve",{sub:w.v,cost:2000,serves:{edicts:1,infra:0.8},why:"Wonder "+w.v.slice(2)+" (Edict)"});
    // every Infrastructure option, scored by what its own text does: Garrisons / Keeps / Walls / Bandit Authority answer the
    // Bandit threat; Craft / tax / trade / upkeep the economy; Faith; Influence and Envoys
    L.filter(o=>o.v.startsWith("i:")).forEach(o=>{const n=o.v.slice(2),t=String((INFRA[n]||{}).effect_raw||""),e={infra:0.6},ci=CN.get(n);
      if(ci)e.monuments=Math.max(0.3,0.5+0.4*ci.frac-0.15*ci.rank);                           // Infrastructure a Monument chain needs
      const bd=/Garrison/i.test(t)?1:/Muster/i.test(t)&&/Keep/i.test(n)?0.8:/Walls/i.test(n)?0.7:/Bandit/i.test(t)?0.6:/Can Muster/i.test(t)?0.5:0;
      if(bd)e.bandits=bd*Math.max(s.camps?0.3:0,s.bthreat);
      if(/Craft|Tax Income|Can Trade/i.test(t)||new RegExp(SUPPLY()+"\\s*-|"+UPKEEP()+"\\s*-","i").test(t))e.economy=s.econ*0.7;
      if(/Faith \+/i.test(t))e.faith=0.6;
      if(/Influence|Envoy/i.test(t))e.diplomacy=0.4;
      add("Industry","Improve",{sub:o.v,cost:2000,serves:e,why:"Improve "+n+" ("+t.slice(0,60)+")"});});}
  if(!expediteWhy(p))add("Industry","Expedite",{serves:{holdings:0.6,economy:s.econ*0.3},why:"Expedite: nothing else to do in Industry"});
  {const L=repairOpts(p).filter(o=>o.v!=="hand");if(L.length)add("Industry","Repair",{sub:L[0].v,serves:{holdings:1,economy:s.econ*0.6},why:"Repair "+L[0].label});}
  if(aiDv(p,"Industry")>=RIS){
    if(s.h.settCap==null||s.h.setts<s.h.settCap)add("Industry","Settle",{cost:aiActCost("Settle"),serves:{economy:s.econ*0.7,holdings:Math.min(1,0.6+0.6*s.wardFull+0.3*s.spare)},why:"new Settlement ("+s.h.setts+"/"+(s.h.settCap??"?")+")"});
    const x=expandOpts(p).find(o=>o.v!=="hand"&&!/⚑/.test(o.label));if(x)add("Industry","Expand",{sub:x.v,cost:aiActCost("Expand"),serves:{economy:s.econ*0.8,holdings:Math.min(1,0.5+0.6*s.wardFull+0.3*s.spare)},why:"Expand "+x.label});}
  // Piety (each costs Doubt 1)
  {const rich=s.others.slice().sort((x,y)=>(+y.board.treasury||0)-(+x.board.treasury||0))[0];
    const drastic=!s.cash.ok&&(+b.treasury||0)<2000;                                   // Industry Tithes only when something is badly wrong
    if(rich&&(+rich.board.treasury||0)>=1000&&(!s.doms.includes("Industry")||drastic))add("Piety","Tithe",{tgt:String(rich.id),doubt:1,serves:{economy:s.econ*Math.min(1,(+rich.board.treasury||0)/20000)},why:"Tithe "+rich.name});}
  if(foeQ)add("Piety","Send Missionaries",{tgt:String(foeQ.id),doubt:1,serves:{[fp]:like("Piety")},why:"Doubt 2 on "+foeQ.name+" ("+foe.why+")"});
  {const g=diplo().member[topSuz(p.id)];if(g&&s.po<=0)add("Piety","Send Missionaries",{tgt:"al:"+g,doubt:1,serves:{faith:0.3},why:"Faith 2 to the Alliance"});}
  {const non=s.others.filter(q=>!alliedP(p,q));if(non.length&&s.foes.length>=non.length)add("Piety","Spread Truth",{doubt:1,serves:{diplomacy:0.6*like("Piety")},why:"Doubt on every non-ally"});}
  if(aiDv(p,"Piety")>=SOV&&foeQ&&effPair(p.id,foeQ.id).war)add("Piety","Convert",{tgt:String(foeQ.id),doubt:1,serves:{edicts:0.8,diplomacy:0.5},why:"Convert "+foeQ.name});
  // Cunning (each costs 2000; Passed Extorts CUNNING_EXTORT back from the target)
  if(foeQ){const q=foeQ,war=effPair(p.id,q.id).war,ex=+RC.CUNNING_EXTORT||0,lc=like("Cunning");
    if(war&&(q.board.armies||[]).length)add("Cunning","Sabotage",{tgt:String(q.id),cost:2000,serves:{diplomacy:lc},why:"Block "+q.name+"'s Army"});
    if((q.board.placed||[]).length&&!srcHas(q.board,"immune_raze"))add("Cunning","Raze",{tgt:String(q.id),cost:2000,serves:{[fp]:0.9*lc},why:"Raze "+q.name+" ("+foe.why+")"});
    add("Cunning","Intercept Caravan",{tgt:String(q.id),cost:2000,serves:{[fp]:0.6*lc,economy:s.econ*(tradeRaw(q.board).total>ex?0.6:0.2)},why:"Intercept "+q.name+"'s trade"});
    add("Cunning","Destabilize",{tgt:String(q.id),cost:2000,serves:{[fp]:0.5*lc,economy:s.econ*0.4},why:"Destabilize "+q.name+" (Winter tax)"});
    // Foster Rebellion grows Outlaw Country when it's full: only a Cunning culture harnesses it, and only while Bandits aren't on its own doorstep
    if(s.camps&&s.doms.includes("Cunning")&&s.bthreat<0.3)add("Cunning","Foster Rebellion",{tgt:String(q.id),cost:2000,serves:{[fp]:0.7*lc},why:"Bandits on "+q.name});}
  // Prowess
  {const arms=b.armies||[],up=+((EQ.retinues[aiKit(p).retinue]||EQ.retinues.Levy||{}).cost)||0,mt=aiMoveTargets(p),mv=aiMovable(p);
    // raise an Army: the first when Bandits, war or a Prowess culture call for one; another (up to the Era's cap) when the Bandit threat
    // is high and every Army already raised is full or still mustering
    const live=arms.filter(a=>(+a.count||0)>0||(a.muster&&a.muster.n>0)),capA=withBoard(b,()=>eraCap("armies")),
      wantMore=live.length>0&&(s.bthreat>=0.6||s.pr.prowess_coded)&&live.every(a=>aiFull(a)||(a.muster&&a.muster.n>0))&&(capA==null||arms.length<capA);
    // a better Retinue unlocked than the weakest Army's: raise one of it (aiRetire then disbands the weak Army once the new one is full)
    const rc=a=>+((EQ.retinues[a.retinue]||{}).cost)||0,bestR=aiKit(p).retinue,weakA=live.slice().sort((x,y)=>rc(x)-rc(y))[0],
      upg=+aiSpine().retire&&weakA&&(+((EQ.retinues[bestR]||{}).cost)||0)>rc(weakA)&&!live.some(a=>a.retinue===bestR);
    if((!live.length&&(s.camps||s.war.length||s.pr.prowess_coded))||wantMore||upg){const mo=musterOpts(p).find(o=>o.v.startsWith("n:"));
      const rets=Object.keys(EQ.retinues).filter(n=>withBoard(b,()=>armyUnlocks(computeEarned(new Set(Object.keys(PC))).earned).retinues.has(n)))
        .sort((x,y)=>(+EQ.retinues[y].cost||0)-(+EQ.retinues[x].cost||0)),afford=rets.find(n=>aiCashOutlook(p,+EQ.retinues[n].cost||0).ok);
      const onlyUpg=upg&&live.length&&!wantMore;   // raised only to replace a weaker Army: worth it only as the better Retinue
      if(mo&&afford&&(!onlyUpg||afford===bestR)){PT(p).aiRaiseRet=afford;add("Prowess","Muster",{sub:mo.v,why2:afford,serves:{bandits:Math.max(s.camps?0.4:0,s.bthreat,onlyUpg?0.5+0.5*s.gearNeed:0),diplomacy:s.war.length?1:0.4*like("Prowess")},why:"raise an Army of "+afford+(onlyUpg?" (replaces "+(weakA.label||("Army "+weakA.id))+", "+weakA.retinue+")":"")});}}
    // Muster first: an under-strength Army (or an exhausted one) is Reinforced before it goes anywhere
    const tired=arms.find(a=>(+a.count||0)>0&&(!aiFull(a)||!((+a.endurance||0)>0))&&!(a.muster&&a.muster.n>0)),ro=tired&&musterOpts(p).find(o=>o.v==="r:"+tired.id);
    if(ro)add("Prowess","Muster",{sub:ro.v,bandit:!!s.camps,serves:{bandits:Math.min(1,Math.max(s.camps?0.4:0,s.bthreat)*(aiBanditNear(p)?1.4:1)),diplomacy:s.war.length?0.8:0.3},why:"Reinforce "+(tired.label||("Army "+tired.id))+" to full strength ("+(+tired.count||0)+"/"+(+EQ.army_max||25)+")"});
    const hunt=mt.some(t=>t.mine&&t.n!=null&&mv.some(a=>aiBeats(a,{kind:"bandit",camp:t.k})));
    if(mt.length&&mv.some(a=>aiFull(a)||mt.some(t=>t.n!=null&&aiBeats(a,{kind:"bandit",camp:t.k}))))add("Prowess","Move",{bandit:!!s.camps,war:s.war.length>0,siege:s.war.length>0,pen:hunt?-aiPrioW("bandits")*0.6:0,serves:{bandits:s.camps?Math.min(1,Math.max(hunt?0.9:0.5,s.bthreat)*(1+0.5*Math.max(0,...mt.filter(t=>t.mine&&!t.home).map(t=>(t.n||0)/(BAN.armyThreshold||25))))):0,diplomacy:s.war.length?0.9:0,edicts:s.war.length?0.4:0},why:"Move toward "+mt[0].why});
    {const ht=aiHomeThreats(p);if(ht.length&&mv.length&&!mv.every(a=>{const x=armyInside(p,a);return x&&String(x.s.id)===String(ht[0].sid);}))
      add("Prowess","Move",{bandit:true,serves:{bandits:1},why:"defend "+ht[0].sk+" against a Bandit Army ("+ht[0].n+") "+ht[0].d+" hexes off"});}
    if(s.war.length&&mv.length)add("Prowess","Pillage",{tgt:String(s.war[0].id),serves:{economy:s.econ*0.7,diplomacy:0.4},why:"Pillage "+s.war[0].name});
    if(s.doms.includes("Prowess")&&aiEraAllows("Declare War")&&aiDv(p,"Prowess")>=RIS){
      const weak=s.others.filter(q=>!alliedP(p,q)&&!effPair(p.id,q.id).war&&!effPair(p.id,q.id).nap&&aiMil(q)<aiMil(p)).sort((x,y)=>aiMil(x)-aiMil(y))[0];
      if(weak)add("Prowess","Declare War",{tgt:String(weak.id),serves:{diplomacy:0.9,edicts:0.6},why:"war on weaker "+weak.name+" ("+aiMil(weak)+" vs "+aiMil(p)+" Retinues)",war:1});}
    if(!s.cash.ok&&s.pr.prowess_coded){const q=s.others.filter(q=>!alliedP(p,q)&&aiMil(q)<aiMil(p)).sort((x,y)=>(+y.board.treasury||0)-(+x.board.treasury||0))[0];
      if(q)add("Prowess","Demand Tribute",{tgt:String(q.id),serves:{economy:0.8},why:"Tribute from weaker "+q.name});}}
  // Diplomacy: treaties only with AI seats that would accept (and aren't already proposing to us)
  if(!RC.PHASE_REFORM)s.others.filter(aiOn).forEach(q=>{const t=aiTreatyType(p,q);if(!t)return;const theirs=aiPlanFor(q,"Diplomacy");
    if(theirs&&theirs.act==="Sign Treaty"&&String(theirs.tgt)===String(p.id))return;const ac=aiTreatyAccept(q,p,t);if(!ac.ok)return;
    const tr=t==="Trade Agreement",pc=t==="Peace Treaty";
    add("Diplomacy","Sign Treaty",{tgt:String(q.id),treaty:t,serves:{diplomacy:1,economy:tr?s.econ*0.7:pc&&!s.cash.ok?0.6:0},why:t+" with "+q.name+" ("+q.name+": "+ac.why+")"});});
  if(s.doms.includes("Cunning")&&!RC.PHASE_REFORM)s.others.forEach(q=>{const x=effPair(p.id,q.id);if((x.trade||x.nap)&&aiFoe(p,q))add("Diplomacy","End Treaty",{tgt:String(q.id),serves:{diplomacy:0.7},why:"turn on "+q.name+" ("+aiFoe(p,q)+")"});});
  // Domain styles: an action done the culture's way serves that priority (economy / faith / bandits) and counts ×1.3
  const ST={economy:aiStyle(p,"economy"),faith:aiStyle(p,"faith"),bandits:aiStyle(p,"bandits")},need={economy:s.econ,faith:aiFaithNeed(p,ST.faith),bandits:Math.max(s.camps?0.3:0.1,s.bthreat)};
  C.forEach(c=>{const T=aiActTags(c);c.tags=[...T];
    if(T.has("faith_gain")&&need.faith>0&&(!ST.faith.has("po_cheap")||T.has("low_costs")||T.has("holding_income")))c.serves.faith=Math.max(c.serves.faith||0,need.faith*0.8);
    ["economy","faith","bandits"].forEach(k=>{const hit=[...T].filter(t=>ST[k].has(t));if(!hit.length)return;
      c.serves[k]=Math.max(c.serves[k]||0,need[k]*0.6)*1.3;c.style=(c.style||[]).concat(hit);});});
  // Edicts reached through the other priorities: Monument (Build), Wonder (Improve), Wealth (gold), Living Saints (Faith), Vassalize (war)
  C.forEach(c=>{const e=c.serves;
    if(c.act==="Build"&&e.monuments)e.edicts=Math.max(e.edicts||0,1);
    if(e.economy>0&&s.wealth>=0.5)e.edicts=Math.max(e.edicts||0,0.6*s.wealth);
    if(e.faith>0&&s.saints>=0.6)e.edicts=Math.max(e.edicts||0,0.6*s.saints);});
  // archetype: priority and tag multipliers, the lead Domain, and the most pressing need
  const AR=aiArch(p),top=["economy","faith","bandits"].sort((x,y)=>need[y]-need[x])[0];
  C.forEach(c=>{const e=c.serves;Object.keys(e).forEach(k=>{e[k]*=(AR.prio[k]||1)*(k===top?AR.need_amp:1);});
    const tm=Math.max(1,...(c.tags||[]).map(t=>AR.tags[t]||1));c.arch=(tm>1?tm:1)*(c.dom===s.doms[0]?AR.lead:1);});
  if(!s.doms.includes("Cunning"))for(let i=C.length-1;i>=0;i--)if(C[i].dom==="Cunning")C.splice(i,1);   // only Cunning cultures act through Cunning
  // too noticed: when this bot's own Cunning or Piety Envoys are expected to be Opposed down (pass chance < 50%), it lies low —
  // those actions count half, and Industry (Build / Improve / Settle / Expand / Repair) counts more
  const noticed=["Cunning","Piety"].filter(d=>s.doms.includes(d)&&(s.pass[d]||{c:1}).c<0.5);
  if(noticed.length)C.forEach(c=>{if(noticed.includes(c.dom))c.lieLow=0.5;
    else if(c.dom==="Industry"){c.serves.holdings=Math.min(1,(c.serves.holdings||0)+0.3);c.serves.economy=Math.max(c.serves.economy||0,0.4);c.lieLow=1.15;}});
  C.forEach(c=>{const pc=s.pass[c.dom]||{net:0,c:1};c.score=Math.max(0,aiScore(c.serves,s.surv.ok)-(c.pen||0))*pc.c*c.arch*(c.lieLow||1);c.prio=aiTop(c.serves,s.surv.ok);c.net=pc.net;});
  return C.filter(c=>c.score>0).sort((x,y)=>y.score-x.score);}
// the plan: highest-scoring candidates the bot can pay for; Doubt-costing ones only above its faith floor; one per action+target
function aiIntents(p){const b=p.board,C=aiCandidates(p),out=[],needs={};let gold=(+b.treasury||0)-aiArch(p).reserve,po=+b.po||0;
  C.forEach(c=>{if(c.act==="Move"||c.war){needs.speed=true;needs.battle=true;}if(c.dom==="Diplomacy")needs.influence=true;});
  const floor=aiFaithFloor(p,needs);
  const hostileTo=(x,t)=>String(x.tgt||"")===String(t)&&(x.war||x.act==="Declare War");
  const noPiety=!!pietyBlocked(p);   // Wavering Devotion
  C.forEach(c=>{if(c.cost&&c.cost>gold)return;if(c.dom==="Piety"&&noPiety)return;if(envoyBlocked(p,c.dom)||actRestrict(p,c.act,c.tgt?pById(c.tgt):null).length)return;if(c.doubt&&po-c.doubt<=floor)return;if(out.some(x=>x.act===c.act&&String(x.tgt||"")===String(c.tgt||"")&&x.sub===c.sub))return;
    if(c.act==="Sign Treaty"&&out.some(x=>hostileTo(x,c.tgt)))return;if(c.act==="Declare War"&&out.some(x=>x.act==="Sign Treaty"&&String(x.tgt)===String(c.tgt)))return;   // war or a treaty with someone, not both
    gold-=c.cost;po-=c.doubt;out.push(Object.assign({},c,{floor,why:c.why+" ["+c.prio+" "+c.score.toFixed(1)+", net "+c.net+(c.style?", style: "+[...new Set(c.style)].join("/"):"")+(c.arch>1?", "+aiArch(p).name+" ×"+c.arch.toFixed(2):"")+"]"}));});
  return out;}
function aiDeclare(p){const n=personalEnvoys(p),I=aiIntents(p),pick=I.slice(0,n),c=tCurW(p);
  while(pick.length<n&&pick.length)pick.push(Object.assign({},pick[0]));                    // spare Envoys follow the top intent
  c.decl={n:{},lock:tnow()};pick.forEach(x=>c.decl.n[x.dom]=(c.decl.n[x.dom]||0)+1);
  PT(p).aiPlan={turn:tTurn(),list:pick.map(x=>Object.assign({},x,{used:false}))};
  aiNote(p,"Envoys → "+(pick.map(x=>x.dom+" ("+x.why+")").join(" · ")||"none"));}
// this bot's planned intent for one of its Envoys (by Domain), not yet used
function aiPlanFor(p,dom){const P=PT(p).aiPlan;return P&&P.turn===tTurn()?P.list.find(x=>!x.used&&x.dom===dom):null;}
// Perform: the planned intent for this Envoy's Domain, else any action of the Domain that passes against some target
function aiPerform(p,E){const c=tCurW(p);c.perform=c.perform||{};
  const tryAct=(act,tgt,sub)=>{const T=pfTargets(E,act),t=tgt!=null?T.find(x=>x.v===String(tgt)):T.find(x=>x.ok);if(!t||!t.ok)return null;
    let s=sub||"";const sp=pfSpec(act);if(sp.sub&&!s&&!sp.subOpt){const S_=pfSubs(p,act,t.v)||[];const f=S_.find(x=>!x.dis&&x.v!=="hand");if(!f)return null;s=f.v;}
    const pl_=sp.place?(sp.place(p,s)||[]).find(x=>x.auto&&!x.dis)||(sp.place(p,s)||[]).find(x=>!x.dis):null;
    return {action:act,target:t.v,sub:s,place:pl_?pl_.v:"",ts:tnow()};};
  const it=aiPlanFor(p,E.dom);let rec=it?tryAct(it.act,it.tgt,it.sub):null,why=it?it.why:"",pick=it;
  if(it)it.used=true;
  // otherwise the best-scoring candidate among the actions this Envoy may perform, then any other action that passes
  if(!rec){const acts=pfActs(E);for(const c of aiCandidates(p).filter(c=>acts.includes(c.act))){rec=tryAct(c.act,c.tgt,c.sub);if(rec){why=c.why+" ["+c.prio+" "+c.score.toFixed(1)+"]";pick=c;break;}}}
  const cun=aiDoms(p).includes("Cunning");
  if(!rec)for(const a of pfActs(E).filter(a=>a!=="Sign Treaty"&&a!=="Declare War"&&(cun||actDom(a,E)!=="Cunning"))){rec=tryAct(a,null,null);if(rec){why="fallback";pick=null;break;}}   // no unplanned treaties or wars
  if(!rec&&!cun&&actDom(pfActs(E)[0]||"",E)==="Cunning"){c.perform[E.id]={action:"",declined:tnow(),ts:tnow()};aiNote(p,E.dom+" Envoy: declined — not a Cunning culture");return;}
  if(!rec){c.perform[E.id]={failAccept:1,target:"",failOut:"Failed",failNet:E.net,tried:[],ts:tnow()};aiNote(p,E.dom+" Envoy: no action passes — let it fail");return;}
  c.perform[E.id]=rec;let extra="";
  if(rec.action==="Move")extra=" · "+aiMove(p);
  if(rec.action==="Sign Treaty"&&pick&&pick.treaty){const q=pById(rec.target);if(q&&aiOn(q)){aiApplyTreaty(p,q,pick.treaty);extra=" · "+pick.treaty+" signed";}}
  aiNote(p,E.dom+" Envoy "+E.out+" → "+rec.action+(rec.target?" → "+(pById(rec.target)||{}).name:"")+" ("+why+")"+extra);}
// Support / Oppose another player's Envoy: {a, x wanted, w priority, why}. A treaty partner backs it fully; friends get more
// Influence the better they've treated this bot; foes are Opposed harder the worse it is.
function aiVoteWant(p,E){const o=E.owner,cap=Math.max(1,voteCap(p,E.dom||"Prowess",E.council)),rel=aiRel(p,o),pl=aiOn(o)?aiPlanFor(o,E.dom):null;
  if(pl&&pl.act==="Sign Treaty"){const tq=pById(pl.tgt);
    if(tq&&sameP(tq,p))return {a:"S",x:cap,w:5,why:"treaty "+pl.treaty+" with "+o.name};
    if(tq&&(aiFoe(p,o)||aiFoe(p,tq)))return {a:"O",x:Math.min(cap,2),w:3,why:"block "+o.name+"–"+tq.name+" treaty"};
    return {a:"A",x:0,w:0,why:"not my treaty"};}
  if(effPair(p.id,o.id).war)return {a:"O",x:cap,w:4,why:"at war with "+o.name};
  if(E.dom==="Prowess"&&aiBanditThreat(o)>=0.4)return {a:"A",x:0,w:0,why:o.name+" is dealing with Bandits"};   // Bandits are everyone's problem
  const foe=aiFoe(p,o);if(foe&&!(E.dom==="Industry"&&/^hostile/.test(foe)))return {a:"O",x:Math.min(cap,1+Math.max(0,Math.floor(-rel/3))+(edictTotal(o)>edictTotal(p)?1:0)),w:3,why:o.name+" "+foe};
  if(aiFriend(p,o))return {a:"S",x:Math.min(cap,1+Math.max(0,Math.floor(rel/3))),w:2,why:"friend "+o.name+(rel?" ("+rel+")":"")};
  if(aiLike(p,o))return {a:"S",x:1,w:1,why:"like-minded "+o.name};
  if(E.dom==="Cunning"||E.dom==="Piety")return {a:"O",x:1,w:0.5,why:"default: Oppose a non-friend's "+E.dom+" Envoy ("+o.name+")"};   // the Domains that harass
  return {a:"A",x:0,w:0,why:"no stake"};}
// set pre-votes on every Envoy still to come, highest priority first, within the Influence left this phase
function aiVoteAll(p,R){const pool=Math.max(0,(R.pool[p.id]??inflPool(p))-(R.spent[p.id]||0)),c=tCurW(p),vm=aiArch(p).vote;let room=pool,ch=false;
  Object.keys(c.votes).forEach(id=>{const v=c.votes[id];if(v&&(v.a==="S"||v.a==="O")&&!(R.envoys||[]).some(E=>E.id===id&&E.done))room-=+v.x||0;});
  const W=(R.plan||[]).filter(E=>!E.council&&!sameP(E.owner,p)&&!E.done&&!c.votes[E.id]).map(E=>({E,v:aiVoteWant(p,E)})).sort((x,y)=>y.v.w-x.v.w);
  W.forEach(({E,v})=>{let a=v.a,x=v.a==="A"?0:Math.min(Math.max(1,voteCap(p,E.dom||"Prowess",E.council)),Math.ceil(v.x*vm),room);if(a!=="A"&&x<1){a="A";x=0;}room-=x;c.votes[E.id]={a,x,ts:tnow()};ch=true;
    if(a!=="A")aiNote(p,(a==="S"?"Support ":"Oppose ")+x+" on "+E.owner.name+"'s "+E.dom+" Envoy: "+v.why);});
  return ch;}

// ---- Battle Tactics: read from the battle state, not the culture ----
// Every pairing (my Tactic × theirs) is worked out with the board's own sideCalc, so Steady (a −I Tactic costs nothing),
// Unwieldy (a +I Tactic gains nothing), Blunder at low Initiative and Shields all count as they would in play.
// Utility of a pairing: Initiative edge (striking first / tying / behind) + expected hits landed − expected casualties taken,
// weighted by stance: aggressive (Prowess culture, an offensive 2H build, or out-trading the enemy) leans on damage,
// otherwise on staying in shape. Fall Back only when the battle is being lost badly. The opponent's pick is modelled the same way.
function aiTacticEval(X,tX,tO){const B=battle(),O=X==="A"?"B":"A",keep=B.rev;
  B.rev={sk:B.sk,A:X==="A"?tX:tO,B:X==="A"?tO:tX,eqA:eqCode("A"),eqB:eqCode("B")};
  let c,oc;try{c=sideCalc(X);oc=sideCalc(O);}finally{B.rev=keep;}
  const cell=(TMX[(X==="A"?tX:tO)+"|"+(X==="A"?tO:tX)]||[])[X==="A"?0:1]||{};return {c,oc,cell};}
const aiPHit=t=>Math.max(0,Math.min(1,((BT.faces||10)+1-t)/(BT.faces||10)));
const aiPFail=sv=>Math.max(0,Math.min(1,(sv-1)/(BT.faces||10)));
function aiTacticU(X,tX,tO,st){const {c,oc,cell}=aiTacticEval(X,tX,tO);if(!c||!oc)return 0;
  const dealt=c.front*aiPHit(c.toStrike)*aiPFail(oc.save),taken=oc.front*aiPHit(oc.toStrike)*aiPFail(c.save),n=Math.max(1,c.front);
  let u=st.wI*Math.sign(c.I-oc.I)+st.wD*dealt/n-st.wT*taken/n;
  if(c.blunder)u-=0.5;if(cell.strain)u-=0.3;
  if(cell.end)u+=st.losing?1.5:-2;                                                         // Fall Back: only to escape a lost battle
  return u;}
function aiTacticStance(X){const B=battle(),O=X==="A"?"B":"A",{p,a}=sideArmy(B[X]),oa=sideArmy(B[O]).a,c=sideCalc(X),oc=sideCalc(O);
  const base=c&&oc?{dealt:c.front*aiPHit(c.toStrike)*aiPFail(oc.save),taken:oc.front*aiPHit(oc.toStrike)*aiPFail(c.save)}:{dealt:1,taken:1};
  const off=(p&&(aiProfile(p)||{}).prowess_coded)||((EQ.weapons[(a||{}).weapon]||{}).tags||[]).includes("2H")||base.dealt>base.taken*1.2;
  const losing=!!(a&&oa&&(+a.count||0)*2<(+oa.count||0)&&base.taken>base.dealt);
  const behind=c&&oc&&c.I<oc.I;                                                            // lower Initiative: chasing a tie or the edge matters more
  return {wI:behind?1.2:0.8,wD:off?1.3:0.8,wT:off?0.7:1.2,losing,off};}
function aiPickTactic(X){const B=battle(),O=X==="A"?"B":"A",T=(BT.tactics||[]).filter(t=>tacOK(X,t)),TO=(BT.tactics||[]).filter(t=>tacOK(O,t));
  if(!T.length)return null;const me=aiTacticStance(X),them=aiTacticStance(O);
  // their likely pick: softmax of their own utility against our uniform pick
  const ou=TO.map(o=>T.reduce((t,x)=>t+aiTacticU(O,o,x,them),0)/T.length),mx=Math.max(...ou),ew=ou.map(u=>Math.exp((u-mx)/0.6)),sw=ew.reduce((a,b)=>a+b,0),pw=ew.map(e=>e/sw);
  const eu=T.map(t=>TO.reduce((sum,o,i)=>sum+pw[i]*aiTacticU(X,t,o,me),0));
  const order=T.map((t,i)=>({t,u:eu[i]})).sort((a,b)=>b.u-a.u);
  let pick=order[0];if(Math.random()<0.25&&order.length>1){const m2=order[0].u,e2=order.map(x=>Math.exp((x.u-m2)/0.5)),s2=e2.reduce((a,b)=>a+b,0);let r=Math.random()*s2;pick=order.find((x,i)=>(r-=e2[i])<=0)||order[0];}
  const likely=TO.map((o,i)=>({o,w:pw[i]})).sort((a,b)=>b.w-a.w)[0];
  return {t:pick.t,why:(me.off?"aggressive":"steady")+(me.losing?", losing":"")+" · expects "+likely.o+" ("+Math.round(likely.w*100)+"%) · "+order.slice(0,3).map(x=>x.t+" "+x.u.toFixed(2)).join(", ")};}
// pick for any AI side in the open Battle that hasn't picked this Skirmish
function aiBattleTick(){const B=battle();if(!B||!B.id||(B.rev&&B.rev.sk===B.sk))return false;let ch=false;B.aiPk=B.aiPk||{};
  ["A","B"].forEach(X=>{const sd=B[X];if(!sd||sd.kind==="bandit")return;const p=pById(sd.pid);if(!p||!aiOn(p)||(PICKS[X]||{}).picked||B.aiPk[X]===B.id+":"+pickKey())return;
    const r=aiPickTactic(X);if(!r)return;B.aiPk[X]=B.id+":"+pickKey();blog(X+" (AI "+p.name+") picks a Tactic");aiNote(p,"Battle Tactic → "+r.t+": "+r.why);pickTactic(X,r.t);ch=true;});
  return ch;}

// ---- Intrigue & Tally Phase slots: answer this seat's turn so the timer doesn't run down ----
// Intrigue: pass. Tally Support (Indomitable): the cheapest Support that lifts an own Envoy to Passed or Endorsed, else pass.
// Tally Endorse (High Chancery): Endorse an own Envoy that Passed. Forgery retry: pass.
function aiSlotTurn(p,R){const c=tCurW(p),me=q=>q&&sameP(q,p);
  if(R.waiting==="intrigue"&&me(R.intrigueWho)&&!c.intrigue){c.intrigue={ts:tnow()};return true;}
  if(R.waiting==="tally-support"&&me(R.tallyWho)&&!c.tallySup){const room=Math.max(0,(R.pool[p.id]||0)-(R.spent[p.id]||0));let best=null;
    (R.tallyOpt.own||[]).forEach(E=>{const cap=Math.min(voteCap(p,E.dom,false),room);
      [ETH.Passed,ETH.Endorsed].forEach(t=>{const need=t-E.net;if(need>0&&need<=cap&&(!best||need<best.x))best={E,x:need,t};});});
    c.tallySup=best?{envoy:best.E.id,x:best.x,ts:tnow()}:{ts:tnow()};
    if(best)aiNote(p,R.tallyOpt.src+": Support "+best.x+" on own "+best.E.dom+" Envoy");return true;}
  if(R.waiting==="tally-endorse"&&me(R.tallyWho)&&!c.tallyEnd){const E=(R.tallyOpt.own||[]).find(x=>x.out==="Passed");
    c.tallyEnd=E?{envoy:E.id,ts:tnow()}:{ts:tnow()};if(E)aiNote(p,R.tallyOpt.src+": Endorsed "+envLabel(E));return true;}
  if(R.waiting==="tally-retry"&&me(R.tallyWho)&&!c.retryDec){c.retryDec={send:false,ts:tnow()};return true;}
  return false;}

// ---- Setup: an AI seat does its own Setup steps (Rising, faction, Deploy, Starting Holdings, check-in) ----
function aiEdgeDist(g,k){const a=hk(k),W=+g.width,H=+g.height;let d=1e9;
  for(let c=0;c<W;c++)for(const r of [0,H-1])d=Math.min(d,hexDist(a,[c,r]));
  for(let r=0;r<H;r++)for(const c of [0,W-1])d=Math.min(d,hexDist(a,[c,r]));return d;}
function aiClearOutlaw(p){const M=mapState(),own=terrOwners();Object.keys(M.outlaw||{}).forEach(k=>{if(M.outlaw[k]===true&&own[k]&&own[k].has(String(p.id)))delete M.outlaw[k];});}
// the Town: in the seat's start zone, near the board edge and on / beside Hills, far from the other seats; then autoDeploy's
// Hamlet + Outlaw Country; a layout that raises a Setup flag is undone and the next spot tried
function aiDeploy(p){const M=mapState(),g=M.grid;if(!g)return false;const V=decodeGrid(g),seat=seated(),i=seat.findIndex(q=>sameP(q,p));
  const zones=(g.start_zones||[]).slice().sort((a,b)=>a.seat-b.seat),z=zones[i]||null;
  const land=k=>{const h=V.hex[k];return !!h&&h.t!=="water"&&h.t!=="mountain"&&!terrBlocked(h.t);};
  const others=mapSetts().filter(x=>x.cell.type==="Town"&&String(x.cell.player)!==String(p.id)).map(x=>hk(x.k)).concat(zones.filter((_,j)=>j!==i&&j<seat.length).map(x=>x.anchor));
  const ce=RC.CAPITAL_EDGE_RANGE!=null?+RC.CAPITAL_EDGE_RANGE:99,towns=new Set(((z&&z.towns)||[]).map(x=>x.join(",")));
  const nearHill=k=>V.hex[k]&&V.hex[k].hill?2:hexNb(k).some(n=>V.hex[n]&&V.hex[n].hill)?1:0;
  const pool=z?((z.hexes||[]).map(x=>x.join(",")).concat([...towns])):Object.keys(V.hex);
  const cand=[...new Set(pool)].filter(k=>land(k)&&hexFree(k)&&aiEdgeDist(g,k)<=ce)
    .map(k=>({k,s:nearHill(k)*1.5-aiEdgeDist(g,k)*0.8+(others.length?Math.min(99,...others.map(a=>hexDist(hk(k),a))):0)*0.25+(towns.has(k)?1:0)+Math.random()*0.1})).sort((a,b)=>b.s-a.s);
  const bad=()=>charterFlags(p).filter(f=>/^(Setup|Settle)/.test(f)).length>0;
  const undo=k=>{const h=mapSetts().find(x=>String(x.cell.player)===String(p.id)&&x.cell.type==="Hamlet");aiClearOutlaw(p);if(h)delete M.cells[h.k];delete M.cells[k];syncMapTiers();};
  for(const c of cand.slice(0,12)){M.cells[c.k]={type:"Town",player:p.id};pinNewCell(p,c.k);syncMapTiers();
    if(!autoDeploy(p)&&!bad()){aiNote(p,"Setup: Town @ "+c.k);return true;}undo(c.k);}
  const c=cand[0];if(!c)return false;M.cells[c.k]={type:"Town",player:p.id};pinNewCell(p,c.k);syncMapTiers();autoDeploy(p);   // nothing clean: best spot, flags shown
  aiNote(p,"Setup: Town @ "+c.k+" (flagged)");return true;}
function aiSetupHoldings(p){let ch=false;withBoard(p.board,()=>{const cap=capitalSett(),ham=S.settlements.find(s=>s.tier==="Hamlet");
    const best=L=>L.sort((a,b)=>aiHoldValue(b)-aiHoldValue(a)||Math.random()-0.5)[0];
    const fill=(s,n,opts)=>{if(!s)return;for(let got=S.placed.filter(q=>q.setup&&q.sid===s.id).length;got<n;got++){const x=best(opts().filter(o=>canPlace(o,s.id).ok&&!S.placed.some(q=>q.setup&&q.sid===s.id&&q.name===o)));if(!x)break;placeHolding(x,null,s.id);ch=true;}};
    fill(cap,+RC.SETUP_CAPITAL_PICKS||0,()=>NAMES.filter(n=>setupRawOK(n,cap.id)));
    fill(ham,+RC.SETUP_HAMLET_PICKS||0,()=>(RC.SETUP_HAMLET_HOLDINGS||[]).slice());});
  return ch;}
function aiSetupTick(p){const b=p.board,a=ageRec();let ch=false;
  if(!b.culture){const used=new Set(D.players.map(q=>q.board.culture).filter(Boolean)),L=Object.keys(RC.AI_PROFILES||{}).filter(c=>!used.has(c));
    if(L.length){b.culture=L[Math.floor(Math.random()*L.length)];ch=true;}}
  if(a&&!a.rising&&!b.ageRising){const d=aiLean(p)[0]||"Industry";b.ageRising=d;ch=true;}
  if(!b.faction&&b.culture){const fs=[...(cultureFactions(b)||Object.keys(FAC))],fn=fs[Math.floor(Math.random()*fs.length)];
    if(fn){const pS=S;S=b;try{setFaction(fn);}finally{S=pS;}aiNote(p,"Setup: faction "+fn);ch=true;}}
  if(!setupOn())return ch;
  const st=mapSetts().filter(x=>String(x.cell.player)===String(p.id));
  if(mapState().grid&&!st.some(x=>x.cell.type==="Town")){if(aiDeploy(p))ch=true;}
  else if(mapState().grid&&!st.some(x=>x.cell.type==="Hamlet")){autoDeploy(p);ch=true;}
  if(mapSetts().some(x=>String(x.cell.player)===String(p.id)&&x.cell.type==="Hamlet")&&aiSetupHoldings(p))ch=true;
  if(!checkedIn(p)&&!withBoard(b,setupHoldFlags).length&&mapSetts().some(x=>String(x.cell.player)===String(p.id)&&x.cell.type==="Hamlet")){
    const rows=checkinFD(p);rows.forEach(r=>{if(r.side==="faith")addFaith(r.q.board,r.n);else gainDoubt(r.q.board,r.n);});
    PT(p).checkin={turn:tTurn(),fx:rows.map(checkinTxt)};ch=true;}
  return ch;}

// ---- the tick: run whatever the AI seats owe in the current phase; true if anything changed ----
function aiTick(){if(!D.started&&!TB().begun)return false;if(!aiDriver())return false;
  const ph=tPhase();let ch=false;
  if(setupOn())seated().filter(aiOn).forEach(p=>{try{if(aiSetupTick(p))ch=true;}catch(e){console.warn("ai setup",e);}});
  seated().filter(aiOn).forEach(p=>{
    if(!setupOn()&&aiBooks(p))ch=true;
    if(!setupOn()&&ph==="rest"&&aiRetire(p))ch=true;
    if(aiOutfit(p))ch=true;
    if(ph==="rest"&&(p.board.dp||0)>0&&aiSpendDP(p))ch=true;
    if(ph==="council"&&!councilDomNow()&&TB().phaseTs&&!isSpring()&&!tCur(p).council){const c=aiCouncilPick(p);tCurW(p).council={dom:c.dom,ts:tnow()};aiNote(p,"Council vote → "+c.dom+": "+c.why);ch=true;}
    if(ph==="envoy"&&TB().phaseTs&&!springDiplo()&&!(tCur(p).decl||{}).lock){aiDeclare(p);ch=true;}
    if(TB().phaseTs&&dsOn()&&aiDiploStep(p))ch=true;});
  try{if(aiBattleTick())ch=true;}catch(e){console.warn("ai battle",e);}
  if((ph==="envoy"||ph==="council")&&TB().phaseTs){const R=tSim();
    seated().filter(aiOn).forEach(p=>{aiLearn(p,R);
      if(aiVoteAll(p,R))ch=true;
      if(aiSlotTurn(p,R))ch=true;
      withSlots(R.envoys||[]).forEach(E=>{if(!sameP(E.owner,p)||!(E.out==="Passed"||E.out==="Endorsed")||((tCur(p).perform||{})[E.id]))return;
        if(!resolveOpen(R,E))return;aiPerform(p,E);ch=true;});});}
  return ch;}
let AI_BUSY=false;
function aiAfterRender(){if(AI_BUSY)return;AI_BUSY=true;try{if(aiTick()){save();setTimeout(()=>{AI_BUSY=false;render();},0);return;}}catch(e){console.warn("ai",e);}AI_BUSY=false;}
DO.aiseat=(el,e)=>{if(e)e.stopPropagation();const p=pOf(el);if(!p)return;PT(p).ai=el.checked;if(!el.checked)delete PT(p).aiDP;rlCommit();};
