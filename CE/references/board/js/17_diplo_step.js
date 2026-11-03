// ===================== DIPLOMACY STEP (PHASE_REFORM): offers between players =====================
// Runs as Spring's Envoy Phase (the Diplomacy Phase, ENVOY_PHASE_SPRING), the only one of the year (RC.FORUM_DOMAIN would add one to every non-Spring
// Envoy Phase, after Envoy Declaration, before the Intrigue Phase). Players send offers (a Treaty, or Negotiate terms); an accepted offer is a Passed Diplomacy action for both and the
// Treaty is signed at once. Each player completes up to dsCap() agreements, each with a different partner; End Treaty needs no
// answer and uses one too. At the cap, or on Pass, a player is done: their open offers are withdrawn and offers to them declined.
// No Diplomacy Envoys, Authority or Influence: those are deprecated under PHASE_REFORM.
function dsOn(){if(!RC.PHASE_REFORM)return false;const ph=tPhase();return (ph==="envoy"&&(isSpring()?springDiplo():!!RC.FORUM_DOMAIN))||(ph==="council"&&councilDomNow()==="Diplomacy");}
function dsKey(){return tTurn()+":"+tPhase();}
function DS(){if(!D.dstep||D.dstep.key!==dsKey())D.dstep={key:dsKey(),offers:[],acts:[],pass:{},n:0,emb:{}};D.dstep.emb=D.dstep.emb||{};return D.dstep;}
function dsCap(){return isSpring()?Math.max(1,+eraRec().diplomacy_agreements||1):Math.max(1,+RC.FORUM_ACTIONS||1);}
function dsWho(){return tOrder().filter(p=>!isVassal(p.id));}                   // Vassals take no Diplomacy actions
function dsAgreed(p){const id=String(p.id);return DS().offers.filter(o=>(o.status==="accepted"||o.status==="failed")&&(o.from===id||o.to===id));}
function dsUsed(p){return dsAgreed(p).length+DS().acts.filter(a=>a.pid===String(p.id)).length;}
function dsPartner(p,q){const a=String(p.id),b=String(q.id);return dsAgreed(p).some(o=>(o.from===a&&o.to===b)||(o.from===b&&o.to===a));}
function dsDone(p){return !!DS().pass[String(p.id)]||dsUsed(p)>=dsCap();}
function dsAllDone(){return dsWho().every(dsDone)&&!dsEmb().some(dsEmbDue);}   // Embassy holders decide last
// Treaties p may offer q now (the Realm Diplomacy panel's rules; anything it would flag is still offered, with the flag)
function dsTypes(p,q){const x=effPair(p.id,q.id),L=[];if(x.household)return L;
  if(x.war)L.push("Peace Treaty");if(!x.war&&!x.trade)L.push("Trade Agreement");if(!x.war&&!x.nap)L.push("Non-Aggression Pact");
  ["Military","Defensive"].forEach(t=>{if(!x.war&&!sameAlliance(String(p.id),String(q.id))&&allianceOK(t))L.push(t+" Alliance");});
  return L.concat(["Negotiate"]);}
function dsFlag(p,q,type){if(type!=="Trade Agreement")return "";return (!hasRoad(p.id)||!hasRoad(q.id))?"needs Can Trade":"";}
// the Treaty state between some players, kept with each agreement so an Embassy can make it fail (put it back)
function dsSnap(ids){const d=diplo(),o={pairs:{},member:{},alliances:JSON.stringify(d.alliances)};ids=ids.map(String);
  ids.forEach((a,i)=>ids.slice(i+1).forEach(b=>{if(a===b)return;const k=pk(a,b);o.pairs[k]=d.pairs[k]?JSON.stringify(d.pairs[k]):null;}));
  ids.forEach(id=>{const t=topSuz(id);o.member[t]=d.member[t]??null;});return o;}
function dsRestore(sn){const d=diplo();Object.keys(sn.pairs).forEach(k=>{if(sn.pairs[k])d.pairs[k]=JSON.parse(sn.pairs[k]);else delete d.pairs[k];});
  Object.keys(sn.member).forEach(t=>{if(sn.member[t]==null)delete d.member[t];else d.member[t]=sn.member[t];});d.alliances=JSON.parse(sn.alliances);}
// "Whenever another player performs a Diplomacy action targeting another player, Extort N from both players" (Aristocratic Court):
// on a Passed action only, so what it took is kept on the action ([{h, v, t}]) and handed back if an Embassy makes it fail
function dsCourt(p,q){const took=[];D.players.forEach(h=>{if(sameP(h,p)||sameP(h,q))return;srcMatch(h.board,"diplo_extort").forEach(x=>[p,q].forEach(v=>{
    const t=extortGold({b:v.board},{b:h.board},+x.m[1],x.n);if(t)took.push({h:String(h.id),v:String(v.id),t,src:x.n});dsLog(h.name+" extorts "+t.toLocaleString()+" from "+v.name+" ("+x.n+")",[h,v]);}));});
  return took;}
function dsCourtRefund(took){(took||[]).forEach(x=>{const h=pById(x.h),v=pById(x.v);if(!h||!v)return;const back=Math.min(x.t,Math.max(0,+h.board.treasury||0));
  tGold(h.board,-back,x.src+" · refund (failed)");tGold(v.board,back,x.src+" · refund (failed)");dsLog(x.src+": "+back.toLocaleString()+" returned to "+v.name+" — the action failed",[h,v]);});}
// Embassy: once per Diplomacy step, make one Diplomacy action fail (its Treaty change is undone; both players have still used it)
function dsEmb(){return D.players.filter(h=>srcMatch(h.board,"embassy_fail").length>0);}
function dsFailable(){const S=DS();return S.offers.filter(o=>o.status==="accepted"&&o.prev).map(o=>({id:o.id,label:pname(o.from)+" – "+pname(o.to)+": "+o.type}))
  .concat(S.acts.filter(a=>!a.failed&&a.prev).map(a=>({id:a.id,label:pname(a.pid)+": end "+a.what+(a.with?" with "+pname(a.with):"")})));}
function dsEmbDue(h){return !DS().emb[String(h.id)]&&dsFailable().length>0;}
function dsFail(h,id){const S=DS();if(S.emb[String(h.id)])return false;const o=S.offers.find(x=>x.id===id&&x.status==="accepted"),a=S.acts.find(x=>x.id===id&&!x.failed),it=o||a;
  if(!it||!it.prev)return false;dsRestore(it.prev);dsCourtRefund(it.court);it.court=[];if(o)o.status="failed";else a.failed=true;S.emb[String(h.id)]="used";
  const who=o?[pById(o.from),pById(o.to)]:[pById(a.pid)].concat(a.with?[pById(a.with)]:[]);dsLog("Diplomacy: "+h.name+"'s Embassy makes it fail — "+(o?pname(o.from)+" – "+pname(o.to)+": "+o.type:pname(a.pid)+": end "+a.what),[h].concat(who.filter(Boolean)));return true;}
// sign a Treaty between p and q (the Realm Diplomacy panel's effects)
function applyTreaty(p,q,type){const x=pairOf(p.id,q.id),d=diplo();
  if(type==="Peace Treaty"){x.war=false;x.sacredWar=false;x.truce=TRUCE_LEN;}
  else if(type==="Trade Agreement")x.trade=true;
  else if(type==="Non-Aggression Pact")x.nap=true;
  else if(/ Alliance$/.test(type)){const t=type.split(" ")[0];let g=d.member[topSuz(p.id)];
    if(!g||(d.alliances[g]||{}).type!==t){let n=1;while(d.alliances[String(n)])n++;g=String(n);d.alliances[g]={type:t};d.member[topSuz(p.id)]=g;}
    d.member[topSuz(q.id)]=g;}}
// what p could end: one line per Treaty with another player (End Treaty: no Truce Timer running, the target needn't agree)
function dsEnds(p){const L=[];D.players.forEach(q=>{if(sameP(p,q))return;const x=effPair(p.id,q.id);if(x.household||x.truce>0)return;
    if(x.trade)L.push({q,t:"Trade Agreement"});if(x.nap)L.push({q,t:"Non-Aggression Pact"});});
  const g=diplo().member[topSuz(p.id)];if(g)L.push({q:null,t:allianceLabel(g)});return L;}
// a player is done: withdraw what they offered, decline what was offered to them
function dsClose(p){const S=DS(),id=String(p.id);S.offers.forEach(o=>{if(o.status!=="open")return;if(o.from===id)o.status="withdrawn";else if(o.to===id)o.status="declined";});}
function dsLog(msg,ps){ps.forEach(p=>noteAdd(p,msg));}
function dsOffer(p,q,type,terms){const S=DS();if(dsDone(p)||dsDone(q)||dsPartner(p,q))return false;
  S.offers.push({id:"o"+(++S.n),from:String(p.id),to:String(q.id),type,terms:terms||"",status:"open",ts:tnow()});return true;}
function dsAccept(o){const S=DS(),p=pById(o.from),q=pById(o.to);if(!p||!q||o.status!=="open"||dsDone(p)||dsDone(q)||dsPartner(p,q))return false;
  o.prev=dsSnap([o.from,o.to]);o.status="accepted";if(o.type!=="Negotiate")applyTreaty(p,q,o.type);o.court=dsCourt(p,q);
  dsLog("Diplomacy: "+p.name+" and "+q.name+" — "+(o.type==="Negotiate"?"agreed terms: "+(o.terms||"(none written)")+" (carry them out by hand; promises aren't binding)":o.type+" signed"),[p,q]);
  [p,q].forEach(x=>{if(dsDone(x))dsClose(x);});return true;}
function dsEnd(p,e){const S=DS();if(dsDone(p))return false;const prev=dsSnap(e.q?[p.id,e.q.id]:[p.id]);
  if(e.q){const x=pairOf(p.id,e.q.id);if(e.t==="Trade Agreement")x.trade=false;else{x.nap=false;x.truce=TRUCE_LEN;}}
  else{const d=diplo();delete d.member[topSuz(p.id)];Object.keys(d.alliances).forEach(k=>{if(!Object.values(d.member).includes(k))delete d.alliances[k];});}
  S.acts.push({id:"a"+(++S.n),pid:String(p.id),act:"End Treaty",what:e.t,with:e.q?String(e.q.id):"",prev});if(e.q)S.acts[S.acts.length-1].court=dsCourt(p,e.q);
  dsLog("Diplomacy: "+p.name+" ends "+(e.q?"the "+e.t+" with "+e.q.name:e.t),e.q?[p,e.q]:[p]);if(dsDone(p))dsClose(p);return true;}
// ---- the pop-up card (dock): offers in, offers out, a new offer, End Treaty, Pass; and everyone's progress ----
let DS_SEL={};
function dsEmbHTML(p){if(!p||!canAct(p)||!srcMatch(p.board,"embassy_fail").length)return "";const S=DS(),id=String(p.id),u=S.emb[id];
  if(u)return '<div class="lbl">Embassy</div><div class="note">'+(u==="used"?"used this step":"let them stand")+'</div>';
  const F=dsFailable(),end=dsWho().every(dsDone);if(!F.length)return '<div class="lbl">Embassy</div><div class="note">Nothing to make fail yet.</div>';
  return '<div class="lbl">Embassy <span class="note">— once this step, make one Diplomacy action fail (both players still used it)</span></div>'+
    F.map(f=>'<div class="tb-row"><span style="flex:1">'+esc(f.label)+'</span><button data-do="dsFail" data-o="'+f.id+'" data-who="'+id+'">make it fail</button></div>').join("")+
    (end?'<div class="tb-row"><button data-do="dsEmbSkip" data-who="'+id+'">let them stand</button></div>':'');}
function diploStepHTML(p){if(!dsOn())return "";const S=DS(),W=dsWho();if(!W.length)return "";const cap=dsCap(),me=p&&W.some(q=>sameP(q,p))?p:null;
  const st='<div class="note">'+W.map(q=>pTok(q,12)+esc(q.name)+' '+dsUsed(q)+'/'+cap+(dsDone(q)?' <b class="pos">✓</b>':'')).join(' · ')+'</div>';
  const head="Diplomacy — "+(cap>1?"up to "+cap+" agreements, each with a different player":"one agreement")+(isSpring()?" (Spring)":"");
  const embWait=W.every(dsDone)?dsEmb().filter(dsEmbDue):[];
  const st2=st+(embWait.length?'<div class="note">Waiting for '+embWait.map(h=>esc(h.name)).join(", ")+' to use their Embassy or let the agreements stand.</div>':'');
  if(!me||!canAct(me))return dockCard(head,st2+'<div class="note">'+(dsAllDone()?'Done.':'Waiting for offers to be made and answered.')+'</div>'+dsEmbHTML(p),"now");
  const id=String(me.id),done=dsDone(me),pn=x=>esc(pname(x)),
    lab=o=>'<b>'+esc(o.type)+'</b>'+(o.terms?' <i>“'+esc(o.terms)+'”</i>':'');
  let h=st2+'<div class="tb-row note">You: '+dsUsed(me)+'/'+cap+(done?' — <b>done</b>':'')+'</div>';
  const inc=S.offers.filter(o=>o.to===id);
  if(inc.length)h+='<div class="lbl">Offers to you</div>'+inc.map(o=>{const q=pById(o.from),ok=o.status==="open"&&!done&&q&&!dsDone(q)&&!dsPartner(me,q),fl=q?dsFlag(q,me,o.type):"";
    return '<div class="tb-row"><span style="flex:1">'+pn(o.from)+' offers '+lab(o)+(fl?' <span class="neg">⚑ '+esc(fl)+'</span>':'')+'</span>'+
      (o.status==="open"?'<button data-do="dsAcc" data-o="'+o.id+'" data-who="'+id+'"'+(ok?'':' disabled')+'>accept</button><button data-do="dsDec" data-o="'+o.id+'" data-who="'+id+'">decline</button>':'<span class="note">'+o.status+'</span>')+'</div>';}).join("");
  const out=S.offers.filter(o=>o.from===id);
  if(out.length)h+='<div class="lbl">Your offers</div>'+out.map(o=>'<div class="tb-row"><span style="flex:1">to '+pn(o.to)+': '+lab(o)+'</span>'+
    (o.status==="open"?'<button data-do="dsWd" data-o="'+o.id+'" data-who="'+id+'">withdraw</button>':'<span class="note">'+o.status+'</span>')+'</div>').join("");
  if(!done){const tg=D.players.filter(q=>!sameP(q,me)&&!isVassal(q.id)&&!dsDone(q)&&!dsPartner(me,q)&&!S.offers.some(o=>o.status==="open"&&o.from===id&&o.to===String(q.id)));
    const sel=DS_SEL[id]=DS_SEL[id]||{},to=tg.find(q=>String(q.id)===sel.to)||tg[0],types=to?dsTypes(me,to):[];if(to)sel.to=String(to.id);
    if(!types.includes(sel.type))sel.type=types[0];
    if(to&&types.length)h+='<div class="lbl">Make an offer</div><div class="tb-row"><select data-do="dsSel" data-k="to" data-who="'+id+'">'+tg.map(q=>'<option value="'+q.id+'"'+(sameP(q,to)?' selected':'')+'>'+esc(q.name)+'</option>').join("")+'</select>'+
      '<select data-do="dsSel" data-k="type" data-who="'+id+'">'+types.map(t=>'<option'+(t===sel.type?' selected':'')+'>'+esc(t)+'</option>').join("")+'</select>'+
      (sel.type==="Negotiate"?'<input data-do="dsSel" data-k="terms" data-who="'+id+'" placeholder="terms: gold, Settlements, promises…" value="'+esc(sel.terms||"")+'" style="flex:1;min-width:140px">':'')+
      '<button data-do="dsSend" data-who="'+id+'">send ▸</button>'+(dsFlag(me,to,sel.type)?' <span class="neg">⚑ '+esc(dsFlag(me,to,sel.type))+'</span>':'')+'</div>';
    const E=dsEnds(me);if(E.length)h+='<div class="lbl">End Treaty <span class="note">(no answer needed; uses an action)</span></div><div class="tb-row">'+E.map((e,i)=>'<button data-do="dsEndT" data-i="'+i+'" data-who="'+id+'">end '+esc(e.t)+(e.q?' with '+esc(e.q.name):'')+'</button>').join("")+'</div>';
    h+='<div class="tb-row"><button data-do="dsPass" data-who="'+id+'">pass — done for this step</button></div>';}
  return dockCard(head,h+dsEmbHTML(me),"now");}
DO.dsSel=el=>{const id=el.dataset.who;DS_SEL[id]=DS_SEL[id]||{};DS_SEL[id][el.dataset.k]=el.value;if(el.tagName!=="INPUT")renderTable();};
DO.dsSend=el=>{const p=pOf(el),sel=DS_SEL[el.dataset.who]||{},q=pById(sel.to);if(!p||!q||!canAct(p))return;
  if(!dsOffer(p,q,sel.type,sel.terms)){flash("Can't offer that now");return;}sel.terms="";rlCommit();};
DO.dsAcc=el=>{const p=pOf(el),o=DS().offers.find(x=>x.id===el.dataset.o);if(!p||!o||o.to!==String(p.id)||!canAct(p))return;if(!dsAccept(o)){flash("That offer can't be accepted now");return;}rlCommit();};
DO.dsDec=el=>{const p=pOf(el),o=DS().offers.find(x=>x.id===el.dataset.o);if(!p||!o||o.to!==String(p.id)||!canAct(p)||o.status!=="open")return;o.status="declined";rlCommit();};
DO.dsWd=el=>{const p=pOf(el),o=DS().offers.find(x=>x.id===el.dataset.o);if(!p||!o||o.from!==String(p.id)||!canAct(p)||o.status!=="open")return;o.status="withdrawn";rlCommit();};
DO.dsEndT=el=>{const p=pOf(el),e=p&&dsEnds(p)[+el.dataset.i];if(!p||!e||!canAct(p))return;dsEnd(p,e);rlCommit();};
DO.dsFail=el=>{const p=pOf(el);if(!p||!canAct(p)||!srcMatch(p.board,"embassy_fail").length)return;if(!dsFail(p,el.dataset.o)){flash("That can't be made to fail now");return;}rlCommit();};
DO.dsEmbSkip=el=>{const p=pOf(el);if(!p||!canAct(p))return;DS().emb[String(p.id)]="skip";rlCommit();};
DO.dsPass=el=>{const p=pOf(el);if(!p||!canAct(p))return;DS().pass[String(p.id)]=true;dsClose(p);rlCommit();};
// AI seat: accept the best acceptable offer, decline the rest; with nothing open of its own, offer its preferred Treaty once
// (aiTreatyType / aiTreatyAccept, the same reasoning as before); then pass. Returns true when it changed something.
function aiDiploStep(p){if(!dsOn())return false;const S=DS(),id=String(p.id);let ch=false;
  if(srcMatch(p.board,"embassy_fail").length&&dsEmbDue(p)&&dsWho().every(dsDone)){
    const pick=dsFailable().find(f=>{const o=S.offers.find(x=>x.id===f.id),a=S.acts.find(x=>x.id===f.id),ids=o?[o.from,o.to]:[a.pid,a.with].filter(Boolean);
      const ps=ids.map(pById).filter(Boolean);return !ps.some(q=>sameP(q,p)||alliedP(p,q))&&ps.some(q=>aiFoe(p,q));});
    if(pick){dsFail(p,pick.id);aiNote(p,"Embassy: made "+pick.label+" fail");}else S.emb[id]="skip";return true;}
  if(dsDone(p))return false;
  S.offers.filter(o=>o.status==="open"&&o.to===id).forEach(o=>{const q=pById(o.from);if(!q)return;
    const a=o.type==="Negotiate"?{ok:false}:aiTreatyAccept(p,q,o.type);if(a.ok&&!dsDone(p)&&dsAccept(o)){aiRelAdd(p,q,2);aiRelAdd(q,p,2);aiNote(p,"Accepted "+o.type+" from "+q.name+": "+a.why);}
    else if(o.status==="open"){o.status="declined";aiNote(p,"Declined "+o.type+" from "+q.name+(a.why?": "+a.why:""));}ch=true;});
  if(dsDone(p))return ch;
  if(S.offers.some(o=>o.status==="open"&&o.from===id))return ch;                        // waiting for an answer
  const tried=new Set(S.offers.filter(o=>o.from===id).map(o=>o.to));
  const c=D.players.filter(q=>!sameP(q,p)&&!isVassal(q.id)&&!dsDone(q)&&!dsPartner(p,q)&&!tried.has(String(q.id))).map(q=>({q,t:aiTreatyType(p,q)})).filter(x=>x.t&&dsTypes(p,x.q).includes(x.t));
  if(c.length&&!tried.size){dsOffer(p,c[0].q,c[0].t,"");aiNote(p,"Offered "+c[0].t+" to "+c[0].q.name);return true;}
  S.pass[id]=true;dsClose(p);return true;}
