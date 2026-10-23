// ===================== INTRIGUE & TALLY PHASES (RULES: Envoy Phase steps 3 and 5) =====================
// Both run inside tSim as timed slots, like votes: a slot per player (Intrigue "IN:", Tally Supports "TS:", Endorsements "TE:",
// retries "TR:"), each recorded in that player's turn record (tCur) and replayed on every render.
// Intrigue (after Forum, before the first vote): starting player to Host, each uses all of their Intrigue effects, then Done.
// Tally (after every Envoy is voted): 5.1 Supports (Indomitable) · 5.2 players who vote in the Tally Phase (Whispering Undercroft)
// cast every vote · 5.3 Endorsements (High Chancery) · 5.4 retries (Forgery Workshop), voted at once. Resolve waits for the end.
function tallyVoter(p){return !!p&&srcHas(p.board,"tally_votes");}
// a Domain Standing's registry hit (s:<Domain>:<Standing>) on b's active Standings, Studium Generale's free one included
function standingHit(b,id){for(const x of dbActive(b)){const m=efxOf("s:"+x.dom+":"+x.tier,id)[0];if(m)return {m,src:x.free?"Studium Generale · "+x.name:x.name};}return null;}
function tallySupportOf(p){const h=standingHit(p.board,"tally_support");return h?{dom:h.m[1],src:h.src}:null;}
function tallyEndorseOf(p){const h=srcMatch(p.board,"tally_endorse")[0];return h?h.n:"";}
// Resolve: Envoy Phase actions wait for the end of the Tally Phase; Diplomacy stays open during the vote (Rule: Diplomatic Mission)
function resolveOpen(R,E){return !R||R.ph!=="envoy"||!!R.tallied||!!E.council||E.dom==="Diplomacy";}
// what a player can do in the Intrigue Phase (they get a slot only if they hold one of these)
function intrigueKinds(p){const L=[];
  if(standingHit(p.board,"intrigue_silence"))L.push("silence");
  if(srcMatch(p.board,"courier_auth_minus").length)L.push("courier");
  if(srcMatch(p.board,"senate_intervene").length)L.push("senate");
  if(srcMatch(p.board,"whisper_declare").length)L.push("whisper");
  if(srcMatch(p.board,"colossus_self").length)L.push("colossus");
  if(onceEffects(p).some(e=>e.ph==="intrigue"&&e.x))L.push("exchange");
  return L;}
// Clandestine Councilor: [{who, src}] players made to Abstain on E
function intrigueSilenced(E){const out=[];D.players.forEach(p=>{const c=tCur(p).clandestine;if(c&&c.envoy===E.id){const q=pById(c.target);if(q)out.push({who:q,src:c.src+" ("+p.name+")"});}});return out;}
function whisperPending(R){const w=D.players.map(p=>({p,x:PT(p).whisperDeclare})).find(o=>o.x&&o.x.turn===tTurn()&&R.plan.some(E=>E.id===o.x.envoy));
  return w?{E:R.plan.find(E=>E.id===w.x.envoy),by:pById(w.x.by)}:null;}
function intrigueRun(R,ord,runSlot){R.stage="intrigue";
  const gate=()=>{const w=whisperPending(R);if(!w)return false;R.waiting="whisper-declare";R.whisperEnvoy=w.E;R.whisperBy=w.by;return true;};   // a Whispering Undercroft declaration is made at once
  for(const p of ord){if(gate())return false;if(!intrigueKinds(p).length)continue;
    const r=runSlot("IN:"+p.id,p,tCur(p).intrigue);if(!r){R.waiting="intrigue";R.intrigueWho=p;return false;}}
  if(gate())return false;
  // Colossus: the Supports committed in the Intrigue Phase are spent now, before the first vote (own per-vote limit)
  ord.forEach(p=>{const cs=srcMatch(p.board,"colossus_self")[0],rec=tCur(p).selfSup||{};if(!cs)return;
    Object.keys(rec).forEach(id=>{const E=R.plan.find(x=>x.id===id&&sameP(x.owner,p)&&!x.council&&x.dom.toLowerCase()===cs.m[2].toLowerCase());if(!E)return;
      const x=Math.max(0,Math.min(+rec[id]||0,voteCap(p,E.dom,false),R.pool[p.id]-R.spent[p.id]));if(!x)return;
      R.spent[p.id]+=x;(R.selfSup[id]=R.selfSup[id]||[]).push({x,src:cs.n});});});
  R.stage="vote";return true;}
function tallyRun(R,ord,runSlot,applyVote,finish,envoyRun){R.stage="tally";const main=R.plan.filter(E=>!E.retry);
  // 5.1 Supports: Indomitable — one of your own Envoys of its Domain, its own per-vote limit
  for(const p of ord){const o=tallySupportOf(p);if(!o)continue;const own=main.filter(E=>sameP(E.owner,p)&&!E.council&&!E.fixed&&E.dom.toLowerCase()===o.dom.toLowerCase());if(!own.length)continue;
    const r=runSlot("TS:"+p.id,p,tCur(p).tallySup);if(!r){R.waiting="tally-support";R.tallyWho=p;R.tallyOpt=Object.assign({own},o);return false;}
    const rec=r.rec||{},E=own.find(x=>x.id===rec.envoy);
    if(E&&+rec.x>0){const x=Math.max(0,Math.min(+rec.x,voteCap(p,E.dom,false),R.pool[p.id]-R.spent[p.id]));
      if(x){E.sup+=x;R.spent[p.id]+=x;E.votes.push({who:p,a:"S",x,eff:x,self:true,src:o.src,tally:true});finish(E);}}}
  // 5.2 Tally votes: each player who votes in the Tally Phase votes on every Envoy, in the Vote order
  for(const h of ord.filter(tallyVoter))for(const E of main){if(E.council||E.fixed||sameP(E.owner,h)||fxOf(h,"noVote").length)continue;
    const sl=intrigueSilenced(E).find(s=>sameP(s.who,h));if(sl){E.votes.push({who:h,a:"A",x:0,eff:0,auto:true,silenced:sl.src,tally:true});continue;}
    const r=runSlot(E.id+">"+h.id,h,tCur(h).votes[E.id]);if(!r){R.curEnvoy=E;R.waiting="tally-vote";return false;}
    applyVote(E,h,r);finish(E);}
  // 5.3 Endorsements: High Chancery — one Envoy you sent becomes Endorsed
  for(const p of ord){const src=tallyEndorseOf(p);if(!src)continue;const own=main.filter(E=>sameP(E.owner,p)&&!E.council&&!E.fixed);if(!own.length)continue;
    const r=runSlot("TE:"+p.id,p,tCur(p).tallyEnd);if(!r){R.waiting="tally-endorse";R.tallyWho=p;R.tallyOpt={own,src};return false;}
    const E=own.find(x=>x.id===(r.rec||{}).envoy);if(E){E.endorsedBy=src+" ("+p.name+")";finish(E);}}
  // 5.4 End of the Tally Phase: Forgery Workshop retries, voted at once
  for(const p of ord){if(!srcMatch(p.board,"forge_retry").length)continue;const failed=main.filter(E=>sameP(E.owner,p)&&E.dom==="Cunning"&&E.out==="Failed");if(!failed.length)continue;
    const r=runSlot("TR:"+p.id,p,tCur(p).retryDec);if(!r){R.waiting="tally-retry";R.tallyWho=p;R.retryFailed=failed;return false;}}
  for(const E of R.plan.filter(E=>E.retry))if(!envoyRun(E))return false;
  R.tallied=true;R.stage="resolve";return true;}

// ---- cards ----
function envLabel(E){return E.owner.name+" · "+E.dom+" Envoy"+(E.retry?" (retry)":" "+((+E.k||0)+1));}
function tsId(s){return String(s).replace(/[^A-Za-z0-9_-]/g,"-");}
function tRow(label,ctrl){return '<div class="tb-row"><span style="flex:1">'+label+'</span>'+(ctrl||"")+'</div>';}
function envSel(id,L){return '<select id="'+id+'">'+L.map(E=>'<option value="'+esc(E.id)+'">'+esc(envLabel(E))+'</option>').join("")+'</select>';}
function amtSel(id,n){return n>0?'<select id="'+id+'">'+Array.from({length:n},(_,i)=>'<option>'+(i+1)+'</option>').join("")+'</select>':"";}
function intrigueHTML(R){if(R.waiting!=="intrigue"||!R.intrigueWho)return "";const p=R.intrigueWho;
  if(!canAct(p))return dockCard("Intrigue Phase",'<div class="note">Waiting for '+esc(p.name)+' to use their Intrigue effects.</div>');
  const c=tCur(p),pt=PT(p),plan=R.plan.filter(E=>!E.council&&!E.retry),rows=[],k=tsId(p.id),
        room=Math.max(0,(R.pool[p.id]||0)-(R.spent[p.id]||0)-Object.values(c.selfSup||{}).reduce((a,x)=>a+(+x||0),0));   // less what Colossus has committed
  intrigueKinds(p).forEach(kind=>{
    if(kind==="silence"){const s=standingHit(p.board,"intrigue_silence"),dom=s.m[1],mine=(p.board.domains||{})[dom]||0,u=c.clandestine;
      if(u){const E=plan.find(x=>x.id===u.envoy),q=pById(u.target);rows.push(tRow(esc(s.src)+': '+esc(q?q.name:"?")+' Abstains on '+esc(E?envLabel(E):"?"),'<span class="note">used</span>'));return;}
      const tg=D.players.filter(q=>!sameP(q,p)&&((q.board.domains||{})[dom]||0)<mine);
      rows.push(tRow(esc(s.src)+': a player with a lower '+esc(dom)+' value Abstains on an Envoy',tg.length&&plan.length?envSel("inSilE-"+k,plan)+
        '<select id="inSilP-'+k+'">'+tg.map(q=>'<option value="'+q.id+'">'+esc(q.name)+' ('+esc(dom)+' '+((q.board.domains||{})[dom]||0)+')</option>').join("")+'</select><button data-do="inSilence" data-who="'+p.id+'">silence</button>':'<span class="note">no player with a lower '+esc(dom)+' value</span>'));}
    if(kind==="courier"){const src=srcMatch(p.board,"courier_auth_minus")[0].n,u=pt.courierTarget&&pt.courierTarget.turn===tTurn()?pt.courierTarget:null;
      if(u){const E=plan.find(x=>x.id===u.envoy);rows.push(tRow(esc(src)+': Authority −1 on '+esc(E?envLabel(E):"?"),'<span class="note">used</span>'));return;}
      rows.push(tRow(esc(src)+': Authority −1 on one Envoy',plan.length?envSel("inCouE-"+k,plan)+'<button data-do="inCourier" data-who="'+p.id+'">apply</button>':''));}
    if(kind==="senate"){const src=srcMatch(p.board,"senate_intervene")[0].n,u=pt.senateChoice&&pt.senateChoice.turn===tTurn()?pt.senateChoice:null;
      if(u){const E=plan.find(x=>x.id===u.envoy);rows.push(tRow(esc(src)+': '+esc(u.out)+' '+esc(E?envLabel(E):"?"),'<span class="note">used</span>'));return;}
      const opts=plan.filter(E=>!sameP(E.owner,p)).map(E=>atWarPair(p,E.owner)?{E,out:"Condemned"}:alliedP(p,E.owner)?{E,out:"Endorsed"}:null).filter(Boolean);
      rows.push(tRow(esc(src)+': Condemn an At War player\'s Envoy or Endorse an Ally\'s',opts.length?'<select id="inSenE-'+k+'">'+opts.map(o=>'<option value="'+esc(o.E.id)+'|'+o.out+'">'+(o.out==="Condemned"?"Condemn ":"Endorse ")+esc(envLabel(o.E))+'</option>').join("")+'</select><button data-do="inSenate" data-who="'+p.id+'">apply</button>':'<span class="note">no At War or allied Envoy</span>'));}
    if(kind==="whisper"){const src=srcMatch(p.board,"whisper_declare")[0].n,u=pt.whisperUse&&pt.whisperUse.turn===tTurn()?pt.whisperUse:null;
      if(u){const E=plan.find(x=>x.id===u.envoy);rows.push(tRow(esc(src)+': '+esc(E?envLabel(E):"?")+' must declare its action','<span class="note">used</span>'));return;}
      const L=whisperEligibleEnvoys(R).filter(E=>!E.retry&&!sameP(E.owner,p));
      rows.push(tRow(esc(src)+': a sender declares the action and target they would Perform',L.length?envSel("inWhiE-"+k,L)+'<button data-do="inWhisper" data-who="'+p.id+'">choose</button>':'<span class="note">no eligible Envoy</span>'));}
    if(kind==="colossus"){const cs=srcMatch(p.board,"colossus_self")[0],dom=cs.m[2],sel=c.selfSup||{};
      plan.filter(E=>sameP(E.owner,p)&&E.dom.toLowerCase()===dom.toLowerCase()).forEach(E=>{const x=+sel[E.id]||0,cap=Math.min(voteCap(p,E.dom,false),room+x);
        rows.push(tRow(esc(cs.n)+': Support '+esc(envLabel(E))+(x?' · <b>'+x+'</b> committed':''),x?'<button data-do="inColossus" data-who="'+p.id+'" data-env="'+esc(E.id)+'" data-x="0">clear</button>':(cap>0?amtSel("inColX-"+tsId(E.id),cap)+'<button data-do="inColossus" data-who="'+p.id+'" data-env="'+esc(E.id)+'" class="pos">Support</button>':'<span class="note">no Influence available</span>')));});}
    if(kind==="exchange")onceEffects(p).filter(e=>e.ph==="intrigue"&&e.x).forEach(e=>{const u=+onceState(p,e.game)[e.key]||0,mx=+e.x[1];
      rows.push(tRow(esc(e.n)+': '+esc(e.c),'<b>'+u+'/'+mx+'</b><button data-do="xch" data-k="'+esc(e.key)+'" data-who="'+p.id+'"'+(u>=mx?' disabled':'')+'>exchange</button>'));});});
  rows.push('<div class="tb-row"><button data-do="inDone" data-who="'+p.id+'" class="on">Done</button><span class="note">'+room+' Influence left</span></div>');
  return dockCard("Intrigue Phase — "+esc(p.name)+' <span class="tbcd"></span>',rows.join(""),"now");}
function tallyHTML(R){const p=R.tallyWho,w=R.waiting;
  if(w==="tally-vote"&&R.cur)return dockCard("Tally Phase — votes",'<div class="note">'+esc(R.cur.who.name)+' casts their votes now, Envoy by Envoy.</div>');
  if(!p||(w!=="tally-support"&&w!=="tally-endorse"))return "";
  if(!canAct(p))return dockCard("Tally Phase",'<div class="note">Waiting for '+esc(p.name)+'.</div>');
  const o=R.tallyOpt,k=tsId(p.id),room=Math.max(0,(R.pool[p.id]||0)-(R.spent[p.id]||0)),ln=E=>esc(envLabel(E))+' · net '+E.net+' · <b class="'+tOutCls(E.out)+'">'+E.out+'</b>';
  if(w==="tally-support"){const cap=Math.min(voteCap(p,o.dom,false),room);
    return dockCard("Tally Phase — Supports · "+esc(p.name)+' <span class="tbcd"></span>',o.own.map(E=>tRow(ln(E))).join("")+
      tRow(esc(o.src)+': Support one of your own '+esc(o.dom)+' Envoys',cap>0?envSel("tsE-"+k,o.own)+amtSel("tsX-"+k,cap)+'<button data-do="tsSupport" data-who="'+p.id+'" class="pos">Support</button>':'<span class="note">no Influence available</span>')+
      '<div class="tb-row"><button data-do="tsPass" data-who="'+p.id+'">pass</button><span class="note">Cap '+voteCap(p,o.dom,false)+' · '+room+' Influence left</span></div>',"now");}
  const L=o.own.filter(E=>E.out!=="Endorsed");
  return dockCard("Tally Phase — Endorsements · "+esc(p.name)+' <span class="tbcd"></span>',o.own.map(E=>tRow(ln(E))).join("")+
    tRow(esc(o.src)+': Endorse one Envoy you sent',L.length?envSel("teE-"+k,L)+'<button data-do="teEndorse" data-who="'+p.id+'" class="pos">Endorse</button>':'<span class="note">all already Endorsed</span>')+
    '<div class="tb-row"><button data-do="tePass" data-who="'+p.id+'">pass</button></div>',"now");}

// ---- buttons ----
function inTurn(el){const p=pOf(el),R=tSim();return p&&R.waiting==="intrigue"&&sameP(R.intrigueWho,p)&&canAct(p)?{p,R}:null;}
function selVal(id){return (document.getElementById(id)||{}).value||"";}
DO.inSilence=el=>{const t=inTurn(el);if(!t)return;const {p,R}=t,s=standingHit(p.board,"intrigue_silence"),k=tsId(p.id),eid=selVal("inSilE-"+k),q=pById(selVal("inSilP-"+k)),dom=s&&s.m[1];
  if(!s||!q||!R.plan.some(E=>E.id===eid)||((q.board.domains||{})[dom]||0)>=((p.board.domains||{})[dom]||0))return;
  tCurW(p).clandestine={envoy:eid,target:String(q.id),src:s.src,ts:tnow()};noteAdd(p,s.src+": "+q.name+" Abstains on "+envLabel(R.plan.find(E=>E.id===eid)));rlCommit();};
DO.inCourier=el=>{const t=inTurn(el);if(!t)return;const {p,R}=t,h=srcMatch(p.board,"courier_auth_minus")[0],eid=selVal("inCouE-"+tsId(p.id));if(!h||!R.plan.some(E=>E.id===eid))return;
  const pt=PT(p);pt.courierTarget={turn:tTurn(),envoy:eid,src:h.n};pt.holdingActs=pt.holdingActs||{};pt.holdingActs.courierAuth=tTurn();rlCommit();};
DO.inSenate=el=>{const t=inTurn(el);if(!t)return;const {p,R}=t,h=srcMatch(p.board,"senate_intervene")[0],[eid,out]=selVal("inSenE-"+tsId(p.id)).split("|"),E=R.plan.find(x=>x.id===eid);if(!h||!E)return;
  if((out==="Condemned"&&!atWarPair(p,E.owner))||(out==="Endorsed"&&!alliedP(p,E.owner)))return;
  const pt=PT(p);pt.senateChoice={turn:tTurn(),envoy:eid,out,src:h.n};pt.holdingActs=pt.holdingActs||{};pt.holdingActs.senateHall=tTurn();rlCommit();};
DO.inWhisper=el=>{const t=inTurn(el);if(!t)return;const {p,R}=t,E=whisperEligibleEnvoys(R).find(x=>x.id===selVal("inWhiE-"+tsId(p.id)));if(!E||sameP(E.owner,p)||!srcMatch(p.board,"whisper_declare").length)return;
  PT(p).whisperUse={turn:tTurn(),envoy:E.id,done:false};PT(E.owner).whisperDeclare={turn:tTurn(),envoy:E.id,by:String(p.id)};rlCommit();};
DO.inColossus=el=>{const t=inTurn(el);if(!t)return;const {p,R}=t,eid=el.dataset.env,E=R.plan.find(x=>x.id===eid&&sameP(x.owner,p));if(!E)return;
  const x=el.dataset.x==="0"?0:+selVal("inColX-"+tsId(eid))||0,c=tCurW(p);c.selfSup=c.selfSup||{};if(x>0)c.selfSup[eid]=x;else delete c.selfSup[eid];
  if(x>0&&isSpring())flash("Spring — players don't spend Influence tokens");rlCommit();};
DO.inDone=el=>{const t=inTurn(el);if(!t)return;tCurW(t.p).intrigue={ts:tnow()};rlCommit();};
function tallyTurn(el,w){const p=pOf(el),R=tSim();return p&&R.waiting===w&&sameP(R.tallyWho,p)&&canAct(p)?{p,R}:null;}
DO.tsSupport=el=>{const t=tallyTurn(el,"tally-support");if(!t)return;const k=tsId(t.p.id),eid=selVal("tsE-"+k),x=+selVal("tsX-"+k)||0;if(!t.R.tallyOpt.own.some(E=>E.id===eid)||x<=0)return;
  tCurW(t.p).tallySup={envoy:eid,x,ts:tnow()};if(isSpring())flash("Spring — players don't spend Influence tokens");rlCommit();};
DO.tsPass=el=>{const t=tallyTurn(el,"tally-support");if(!t)return;tCurW(t.p).tallySup={ts:tnow()};rlCommit();};
DO.teEndorse=el=>{const t=tallyTurn(el,"tally-endorse");if(!t)return;const eid=selVal("teE-"+tsId(t.p.id));if(!t.R.tallyOpt.own.some(E=>E.id===eid))return;
  tCurW(t.p).tallyEnd={envoy:eid,ts:tnow()};noteAdd(t.p,t.R.tallyOpt.src+": Endorsed "+envLabel(t.R.tallyOpt.own.find(E=>E.id===eid)));rlCommit();};
DO.tePass=el=>{const t=tallyTurn(el,"tally-endorse");if(!t)return;tCurW(t.p).tallyEnd={ts:tnow()};rlCommit();};
