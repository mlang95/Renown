// ---- AI players: culture-driven bots for seats marked AI (and, later, the headless simulator) ----
// Priorities and per-culture profiles come from the data (AI_PRIORITIES, AI_PROFILES, AI_FAITH_AVOID, AI_DIPLOMACY,
// AI_DOMAIN_POINTS). Each decision returns its choice plus a one-line reason, kept on the seat (PT(p).aiNote) for tuning.
// Decisions: Domain Points (Rest Phase), Council vote, Envoy placement, Perform (incl. Army Moves and AI-to-AI treaties),
// and Support / Oppose with Influence sized by memory (PT(p).aiMem).
function aiOn(p){return !!(p&&p.board&&PT(p).ai);}
function aiProfile(p){return ((RC.AI_PROFILES||{})[(p.board||{}).culture||""])||null;}
// the client that acts for AI seats: offline / hot-seat, the admin, or the Host's own device
function aiDriver(){return !lockOn()||ADMIN||sameP(meP(),hostP());}
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
function aiStandSteps(txt){const out=[],re=/(Rising|Established|Sovereign)\s+(Industry|Prowess|Cunning|Piety)/gi;let m;
  while((m=re.exec(String(txt||"")))){const t=AI_TIERS.findIndex(x=>x[0].toLowerCase()===m[1].toLowerCase());
    for(let j=0;j<=t;j++)out.push({dom:m[2][0].toUpperCase()+m[2].slice(1).toLowerCase(),tier:AI_TIERS[j][0],th:AI_TIERS[j][1]});}
  return out;}
const aiHas=(b,s)=>(+((b.domains||{})[s.dom])||0)>=s.th;
// the culture's next Monument: the first one in its profile that the board knows and nobody has placed (Monuments are one per game)
function aiNextMonument(p){const pr=aiProfile(p);if(!pr)return null;
  return (pr.monuments||[]).find(n=>R[n]&&!D.players.some(q=>(q.board.placed||[]).some(x=>x.name===n)))||null;}
// goals in priority order, each a list of Standing steps; the first unmet step (lowest tier first within a goal) is the target
function aiStandGoals(p){const pr=aiProfile(p),G=[];
  const cash=aiCashOutlook(p);
  if(!cash.ok)G.push({why:"economy (Treasury "+cash.low.toLocaleString()+" before Winter)",steps:aiStandSteps("Rising Industry")});
  if(aiBanditThreat(p)>=0.4)G.push({why:"Bandits (Prowess Envoys pass)",steps:aiStandSteps("Rising Prowess")});
  // Builds blocked by full Wards with gold sitting idle: Rising Industry opens Settle / Expand (any culture may take it)
  {const L=buildOpts(p).filter(o=>o.v.startsWith("b:")),full=L.length?L.filter(o=>/no free Ward/.test(o.label)).length/L.length:0;
    if(full>=0.5&&(+p.board.treasury||0)>=10000)G.push({why:"room to Build (Settle / Expand)",steps:aiStandSteps("Rising Industry")});}
  if(aiSurvival(p).ok&&pr){const done=(p.board.edictLog||{})["Sovereign Standing"]||[],dv=d=>+((p.board.domains||{})[d])||0;
    const d=pr.domains.filter(x=>!done.includes(x)&&dv(x)<SOV).sort((x,y)=>dv(y)-dv(x))[0];
    if(d)G.push({why:"Edict: Sovereign "+d,steps:aiStandSteps("Sovereign "+d)});}
  const mon=aiNextMonument(p);if(mon)G.push({why:"Monument "+mon,steps:aiStandSteps(R[mon].unlock_raw)});
  if(pr)G.push({why:"culture Domains",steps:pr.domains.flatMap(d=>aiStandSteps("Sovereign "+d))});
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
  const ds=(pr?pr.domains:T_DOMS).filter(d=>T_DOMS.includes(d));
  const d=ds.slice().sort((x,y)=>dv(y)-dv(x))[0]||T_DOMS[0];return {dom:d,why:"strongest culture Domain"};}

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
  if(!x.trade)return "Trade Agreement";
  if(!x.nap&&!pp.prowess_coded)return "Non-Aggression Pact";
  if(!alliedP(p,q)&&allianceOK("Defensive"))return "Defensive Alliance";
  return null;}
// would AI q accept `type` from p? Reasons: desire for war, income from trade, like-minded cultures, memory
function aiTreatyAccept(q,p,type){const dq=aiDoms(q),rel=aiRel(q,p),like=aiLike(q,p),wantsWar=(aiProfile(q)||{}).prowess_coded&&aiMil(q)>aiMil(p);
  if(rel<=-3)return {ok:false,why:"remembers "+p.name+" as hostile ("+rel+")"};
  if(type==="Peace Treaty")return wantsWar?{ok:false,why:"winning the war"}:{ok:true,why:aiCashOutlook(q).ok?"war isn't paying":"economy"};
  if(type==="Trade Agreement"){if(dq.some(d=>d==="Industry"||d==="Piety"))return {ok:true,why:"trade income"};
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
  const wOK=n=>{const it=EQ.weapons[n];return n!=="2HBastard"&&(tierOK(it.tier,u.wTiers)||u.anyTier.has(n))&&reqMet(it,u)&&weaponUnlockMet(n,u)&&lanceOnlyOK(n,u,true);},is2H=n=>(EQ.weapons[n].tags||[]).includes("2H");
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
function aiMovable(p){return (p.board.armies||[]).filter(a=>(+a.endurance||0)>0&&!(a.muster&&a.muster.n>0)&&!armyBlocked(p,a)&&armyHex(p,a)&&(+a.count||0)>0);}
// an Army hunts only at full strength (Muster to EQ.army_max first) and only engages what it outnumbers
const aiFull=a=>(+a.count||0)>=(+EQ.army_max||25);
// an Army takes on what it outnumbers; a full-strength, properly armed Army (better than Farm Tools) also meets an equal force
const aiCanBeat=(a,n)=>(+a.count||0)>n||(aiFull(a)&&(+a.count||0)>=n&&a.weapon&&a.weapon!=="Farm Tools");
function aiEngageSize(o){if(!o||!o.B)return Infinity;if(o.B.kind==="bandit"){const cp=mapState().camps[o.B.camp];return cp?+cp.n||0:Infinity;}
  const q=pById(o.B.pid),a=q&&(q.board.armies||[]).find(x=>String(x.id)===String(o.B.aid));return a?+a.count||0:Infinity;}
function aiMove(p){const T=aiMoveTargets(p);if(!T.length)return "no target";
  const engage=(a)=>{const E=engageTargets(p,a).filter(t=>t.kind==="battle"&&aiCanBeat(a,aiEngageSize(t)));   // RULES: end adjacent, then Battle
    const t=E.sort((x,y)=>aiEngageSize(x)-aiEngageSize(y))[0];if(!t)return null;bqAdd({kind:"battle",A:{pid:String(p.id),aid:String(a.id)},B:t.B,seize:t.seize,src:t.src});return t.label;};
  for(const a of aiMovable(p).sort((x,y)=>(+y.count||0)-(+x.count||0))){
    {const e=engage(a);if(e)return (a.label||("Army "+a.id))+": Battle "+e;}                    // already beside something it can beat
    const k=armyHex(p,a),mi=moveRange(p,a,k);if(!mi||!mi.dest)continue;const D_=Object.keys(mi.dest).map(h=>Object.assign({h},mi.dest[h]));
    const eng=t=>D_.filter(d=>d.engage&&d.engage.kind===t&&(t!=="battle"||aiCanBeat(a,aiEngageSize(d.engage)))).sort((x,y)=>x.cost-y.cost)[0];
    let pick=eng("battle"),why=pick?"Battle: "+pick.engage.label:"";
    if(!pick&&(aiFull(a)||((aiProfile(p)||{}).prowess_coded&&(+a.count||0)>=15))){pick=eng("siege");why=pick?"Lay Siege: "+pick.engage.label:"";}
    if(!pick){const huntable=T.filter(t=>t.n==null||aiCanBeat(a,t.n));
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
  if(/Upkeep\s*-\s*\d/i.test(t))T.add("army_upkeep");
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
    wardFull:(()=>{const L=buildOpts(p).filter(o=>o.v.startsWith("b:"));return L.length?L.filter(o=>/no free Ward/.test(o.label)).length/L.length:0;})()};}
// candidates: {dom, act, tgt, sub, treaty, serves:{priority:value}, cost, doubt, why}
function aiCandidates(p){const s=aiSit(p),b=s.b,C=[],add=(dom,act,o)=>C.push(Object.assign({dom,act,cost:0,doubt:0},o));
  const like=d=>s.doms.includes(d)?1:0.6,foe=s.foes[0],foeQ=foe&&foe.q,fp=foe?(effPair(p.id,foeQ.id).war?"diplomacy":edictTotal(foeQ)>edictTotal(p)?"edicts":"diplomacy"):"";
  // Industry
  {const L=buildOpts(p).filter(o=>o.v.startsWith("b:")&&!o.dis).map(o=>o.v.slice(2)),mon=aiNextMonument(p),kit=aiKit(p);
    L.forEach(n=>{const net=aiHoldNet(n),po=aiHoldPO(n),val=aiHoldValue(n),dm=s.doms.includes(holdDom(n)),gear=aiGearGain(p,n,kit);
      const rides=withBoard(b,()=>{const sd=smartSid(n);return sd!=null&&!!canPlace(n,sd).rider;}),opens=((R[n]||{}).builds_into||[]).filter(x=>R[x]).length;
      const armyCut=s.pr.prowess_coded&&/Upkeep\s*-\s*\d/i.test(String((R[n]||{}).innate_raw||""))&&(b.armies||[]).length>0;   // Prowess: cheaper Armies
      // a Holding that adds Doubt every turn counts against the faith priority — harder the lower Public Order already is
      const pen=po<0?aiPrioW("faith")*0.5*(-po)*(s.po<=0?1:0.6):0;
      // a Holding that upgrades the Army kit answers Bandits (and war): Bandit gear climbs with the Era
      add("Industry","Build",{sub:"b:"+n,cost:2000,pen,gear:!!gear,serves:{economy:val>0&&net>0?Math.max(0.5,s.econ)*Math.min(1,val/1000):0,holdings:Math.min(1,(dm?0.8:0.5)*like("Industry")+0.5*s.spare+(rides?0.3:0)+Math.min(0.2,0.05*opens)+(armyCut?0.4:0)),monuments:n===mon?1:0,
          bandits:gear?(s.pr.prowess_coded?0.6:0.3)+0.6*s.bthreat:0,diplomacy:gear&&(s.war.length||s.pr.prowess_coded)?0.6:0},
        why:(n===mon?"Monument ":"Build ")+n+" (net "+net+"/turn"+(po?", PO "+(po>0?"+":"")+po+"/turn":"")+(gear?", unlocks "+gear:"")+(rides?", rides free":"")+(armyCut?", cuts Army upkeep":"")+")"});});}
  {const L=improveOpts(p).filter(o=>o.v!=="hand"),w=L.find(o=>o.v.startsWith("w:")),ip=aiImprovePick(p);
    if(w)add("Industry","Improve",{sub:w.v,cost:2000,serves:{edicts:1,infra:0.8},why:"Wonder "+w.v.slice(2)+" (Edict)"});
    // every Infrastructure option, scored by what its own text does: Garrisons / Keeps / Walls / Bandit Authority answer the
    // Bandit threat; Craft / tax / trade / upkeep the economy; Faith; Influence and Envoys
    L.filter(o=>o.v.startsWith("i:")).forEach(o=>{const n=o.v.slice(2),t=String((INFRA[n]||{}).effect_raw||""),e={infra:0.6};
      const bd=/Garrison/i.test(t)?1:/Muster/i.test(t)&&/Keep/i.test(n)?0.8:/Walls/i.test(n)?0.7:/Bandit/i.test(t)?0.6:/Can Muster/i.test(t)?0.5:0;
      if(bd)e.bandits=bd*Math.max(s.camps?0.3:0,s.bthreat);
      if(/Craft|Tax Income|Can Trade|Upkeep\s*-/i.test(t))e.economy=s.econ*0.7;
      if(/Faith \+/i.test(t))e.faith=0.6;
      if(/Influence|Envoy/i.test(t))e.diplomacy=0.4;
      add("Industry","Improve",{sub:o.v,cost:2000,serves:e,why:"Improve "+n+" ("+t.slice(0,60)+")"});});}
  {const L=repairOpts(p).filter(o=>o.v!=="hand");if(L.length)add("Industry","Repair",{sub:L[0].v,serves:{holdings:1,economy:s.econ*0.6},why:"Repair "+L[0].label});}
  if(aiDv(p,"Industry")>=RIS){
    if(s.h.settCap==null||s.h.setts<s.h.settCap)add("Industry","Settle",{cost:2000,serves:{economy:s.econ*0.7,holdings:Math.min(1,0.6+0.6*s.wardFull+0.3*s.spare)},why:"new Settlement ("+s.h.setts+"/"+(s.h.settCap??"?")+")"});
    const x=expandOpts(p).find(o=>o.v!=="hand"&&!/⚑/.test(o.label));if(x)add("Industry","Expand",{sub:x.v,cost:2000,serves:{economy:s.econ*0.8,holdings:Math.min(1,0.5+0.6*s.wardFull+0.3*s.spare)},why:"Expand "+x.label});}
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
    if((q.board.placed||[]).length)add("Cunning","Raze",{tgt:String(q.id),cost:2000,serves:{[fp]:0.9*lc},why:"Raze "+q.name+" ("+foe.why+")"});
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
    if((!live.length&&(s.camps||s.war.length||s.pr.prowess_coded))||wantMore){const mo=musterOpts(p).find(o=>o.v.startsWith("n:"));
      const rets=Object.keys(EQ.retinues).filter(n=>withBoard(b,()=>armyUnlocks(computeEarned(new Set(Object.keys(PC))).earned).retinues.has(n)))
        .sort((x,y)=>(+EQ.retinues[y].cost||0)-(+EQ.retinues[x].cost||0)),afford=rets.find(n=>aiCashOutlook(p,+EQ.retinues[n].cost||0).ok);
      if(mo&&afford){PT(p).aiRaiseRet=afford;add("Prowess","Muster",{sub:mo.v,why2:afford,serves:{bandits:Math.max(s.camps?0.4:0,s.bthreat),diplomacy:s.war.length?1:0.4*like("Prowess")},why:"raise an Army of "+afford});}}
    // Muster first: an under-strength Army (or an exhausted one) is Reinforced before it goes anywhere
    const tired=arms.find(a=>(+a.count||0)>0&&(!aiFull(a)||!((+a.endurance||0)>0))&&!(a.muster&&a.muster.n>0)),ro=tired&&musterOpts(p).find(o=>o.v==="r:"+tired.id);
    if(ro)add("Prowess","Muster",{sub:ro.v,bandit:!!s.camps,serves:{bandits:Math.min(1,Math.max(s.camps?0.4:0,s.bthreat)*(aiBanditNear(p)?1.4:1)),diplomacy:s.war.length?0.8:0.3},why:"Reinforce "+(tired.label||("Army "+tired.id))+" to full strength ("+(+tired.count||0)+"/"+(+EQ.army_max||25)+")"});
    const hunt=mt.some(t=>t.mine&&t.n!=null&&mv.some(a=>aiCanBeat(a,t.n)));
    if(mt.length&&mv.some(a=>aiFull(a)||mt.some(t=>t.n!=null&&aiCanBeat(a,t.n))))add("Prowess","Move",{bandit:!!s.camps,war:s.war.length>0,siege:s.war.length>0,pen:hunt?-aiPrioW("bandits")*0.6:0,serves:{bandits:s.camps?Math.min(1,Math.max(hunt?0.9:0.5,s.bthreat)*(1+0.5*Math.max(0,...mt.filter(t=>t.mine&&!t.home).map(t=>(t.n||0)/(BAN.armyThreshold||25))))):0,diplomacy:s.war.length?0.9:0,edicts:s.war.length?0.4:0},why:"Move toward "+mt[0].why});
    if(s.war.length&&mv.length)add("Prowess","Pillage",{tgt:String(s.war[0].id),serves:{economy:s.econ*0.7,diplomacy:0.4},why:"Pillage "+s.war[0].name});
    if(s.doms.includes("Prowess")&&aiEraAllows("Declare War")&&aiDv(p,"Prowess")>=RIS){
      const weak=s.others.filter(q=>!alliedP(p,q)&&!effPair(p.id,q.id).war&&!effPair(p.id,q.id).nap&&aiMil(q)<aiMil(p)).sort((x,y)=>aiMil(x)-aiMil(y))[0];
      if(weak)add("Prowess","Declare War",{tgt:String(weak.id),serves:{diplomacy:0.9,edicts:0.6},why:"war on weaker "+weak.name+" ("+aiMil(weak)+" vs "+aiMil(p)+" Retinues)",war:1});}
    if(!s.cash.ok&&s.pr.prowess_coded){const q=s.others.filter(q=>!alliedP(p,q)&&aiMil(q)<aiMil(p)).sort((x,y)=>(+y.board.treasury||0)-(+x.board.treasury||0))[0];
      if(q)add("Prowess","Demand Tribute",{tgt:String(q.id),serves:{economy:0.8},why:"Tribute from weaker "+q.name});}}
  // Diplomacy: treaties only with AI seats that would accept (and aren't already proposing to us)
  s.others.filter(aiOn).forEach(q=>{const t=aiTreatyType(p,q);if(!t)return;const theirs=aiPlanFor(q,"Diplomacy");
    if(theirs&&theirs.act==="Sign Treaty"&&String(theirs.tgt)===String(p.id))return;const ac=aiTreatyAccept(q,p,t);if(!ac.ok)return;
    const tr=t==="Trade Agreement",pc=t==="Peace Treaty";
    add("Diplomacy","Sign Treaty",{tgt:String(q.id),treaty:t,serves:{diplomacy:1,economy:tr?s.econ*0.7:pc&&!s.cash.ok?0.6:0},why:t+" with "+q.name+" ("+q.name+": "+ac.why+")"});});
  if(s.doms.includes("Cunning"))s.others.forEach(q=>{const x=effPair(p.id,q.id);if((x.trade||x.nap)&&aiFoe(p,q))add("Diplomacy","End Treaty",{tgt:String(q.id),serves:{diplomacy:0.7},why:"turn on "+q.name+" ("+aiFoe(p,q)+")"});});
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
  C.forEach(c=>{if(c.cost&&c.cost>gold)return;if(c.doubt&&po-c.doubt<=floor)return;if(out.some(x=>x.act===c.act&&String(x.tgt||"")===String(c.tgt||"")&&x.sub===c.sub))return;
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
    let s=sub||"";const sp=pfSpec(act);if(sp.sub&&!s){const S_=pfSubs(p,act,t.v)||[];const f=S_.find(x=>!x.dis&&x.v!=="hand");if(!f)return null;s=f.v;}
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

// ---- the tick: run whatever the AI seats owe in the current phase; true if anything changed ----
function aiTick(){if(!D.started&&!TB().begun)return false;if(!aiDriver())return false;
  const ph=tPhase();let ch=false;
  seated().filter(aiOn).forEach(p=>{
    if(aiOutfit(p))ch=true;
    if(ph==="rest"&&(p.board.dp||0)>0&&aiSpendDP(p))ch=true;
    if(ph==="council"&&TB().phaseTs&&!isSpring()&&!tCur(p).council){const c=aiCouncilPick(p);tCurW(p).council={dom:c.dom,ts:tnow()};aiNote(p,"Council vote → "+c.dom+": "+c.why);ch=true;}
    if(ph==="envoy"&&TB().phaseTs&&!(tCur(p).decl||{}).lock){aiDeclare(p);ch=true;}});
  try{if(aiBattleTick())ch=true;}catch(e){console.warn("ai battle",e);}
  if((ph==="envoy"||ph==="council")&&TB().phaseTs){const R=tSim();
    seated().filter(aiOn).forEach(p=>{aiLearn(p,R);
      if(aiVoteAll(p,R))ch=true;
      withSlots(R.envoys||[]).forEach(E=>{if(!sameP(E.owner,p)||!(E.out==="Passed"||E.out==="Endorsed")||((tCur(p).perform||{})[E.id]))return;
        if(!resolveOpen(R,E))return;aiPerform(p,E);ch=true;});});}
  return ch;}
let AI_BUSY=false;
function aiAfterRender(){if(AI_BUSY)return;AI_BUSY=true;try{if(aiTick()){save();setTimeout(()=>{AI_BUSY=false;render();},0);return;}}catch(e){console.warn("ai",e);}AI_BUSY=false;}
DO.aiseat=(el,e)=>{if(e)e.stopPropagation();const p=pOf(el);if(!p)return;PT(p).ai=el.checked;if(!el.checked)delete PT(p).aiDP;rlCommit();};
