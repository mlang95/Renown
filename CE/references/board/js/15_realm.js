// ===================== REALM: the play surface =====================
// Left: era line · player table · map (terrain layer kept, pieces redrawn) · drawers (Turn log · Edicts · Tools).
// Right: the phase card (Host controls fold into it for the Host) and the action dock — only what this phase lets you do.
// Rendering is by region: each region's HTML is compared with what is on screen and replaced only when it changed (patch),
// so open <details>, scroll and the map's terrain survive re-renders. Clicks go through one delegated listener per event
// type: an element carries data-do="<name>" (+ data-* arguments) and DO[name](el, event) runs. Nothing is re-wired per render.
const DO={};
function doFire(name,el,e){const f=DO[name];if(!f)return false;f(el,e);return true;}
document.addEventListener("click",e=>{const el=e.target.closest("[data-do]");if(!el||el.matches("select,input,textarea"))return;
  if(el.tagName==="A")e.preventDefault();doFire(el.dataset.do,el,e);});
document.addEventListener("change",e=>{const el=e.target;if(!el.matches||!el.matches("[data-do]")||!el.matches("select,input,textarea"))return;doFire(el.dataset.do,el,e);});
function patch(el,html){if(!el||el._h===html)return false;el.innerHTML=html;el._h=html;return true;}
function rlCommit(){save();renderTable();}
function pOf(el,k){return pById(el.dataset[k||"who"]);}
function standingPhaseActions(p){const pt=p&&PT(p),pending=pt&&pt.standingPending||{};Object.keys(pending).forEach(k=>{if(pending[k].due<tTurn())delete pending[k];});return dbActive(p&&p.board).flatMap(x=>{const m=String(x.text||"").match(STANDING_ACT_RE);if(!m)return [];
  const action=m[1]||m[2],source=x.free?"Studium Generale · "+x.name:x.name,key=standingKey(x),id="STANDING:"+key;
  if(!pending[key]||pending[key].due!==tTurn())return [];
  return [{x,action,fin:m[1]?"Endorsed":"Passed",source,key,id,env:{id,owner:p,dom:x.dom,council:false,votes:[],net:3,out:m[1]?"Endorsed":"Passed",done:true,standingAction:action,standingSource:source}}];});}
function activeCipherTimers(){const out=[];realmTimers().forEach((t,i)=>{if(t.n>0)out.push({ref:{kind:"realm",i},key:"realm:"+String(t.id!=null?t.id:[t.type,t.kind,t.by,t.tp,t.sid,t.aid,t.uid,t.label].join("|")),label:(t.label||t.type)+" · "+t.n});});
  D.players.forEach(p=>{const b=p.board;(b.placed||[]).forEach(x=>{if(x.bt>0)out.push({ref:{kind:"placed",pid:String(p.id),id:String(x.id),field:"bt"},key:"placed:"+p.id+":"+x.id+":bt",label:p.name+" · "+x.name+" Build · "+x.bt});
      if(x.dmg>0&&x.rep)out.push({ref:{kind:"placed",pid:String(p.id),id:String(x.id),field:"dmg"},key:"placed:"+p.id+":"+x.id+":dmg",label:p.name+" · "+x.name+" Repair · "+x.dmg});});
    (b.settlements||[]).forEach(x=>{if(x.bt>0)out.push({ref:{kind:"settlement",pid:String(p.id),id:String(x.id),field:"bt"},key:"settlement:"+p.id+":"+x.id,label:p.name+" · "+(x.name||x.tier)+" Build · "+x.bt});});
    Object.keys(b.itimer||{}).forEach(n=>{if(b.itimer[n]>0)out.push({ref:{kind:"infra",pid:String(p.id),name:n,field:"itimer"},key:"infra:"+p.id+":"+n+":itimer",label:p.name+" · "+n+" Build · "+b.itimer[n]});});
    Object.keys(b.idmg||{}).forEach(n=>{if(b.idmg[n]>0&&b.irep&&b.irep[n])out.push({ref:{kind:"infra",pid:String(p.id),name:n,field:"idmg"},key:"infra:"+p.id+":"+n+":idmg",label:p.name+" · "+n+" Repair · "+b.idmg[n]});});});return out;}
function cipherTimerResolve(ref){if(!ref)return null;if(ref.kind==="realm")return realmTimers()[+ref.i]||null;const p=pById(ref.pid);if(!p)return null;let x;
  if(ref.kind==="placed")x=(p.board.placed||[]).find(y=>String(y.id)===String(ref.id));
  else if(ref.kind==="settlement")x=(p.board.settlements||[]).find(y=>String(y.id)===String(ref.id));
  else if(ref.kind==="infra")return {get n(){return +(p.board[ref.field]||{})[ref.name]||0;},set n(v){p.board[ref.field]=p.board[ref.field]||{};p.board[ref.field][ref.name]=v;}};
  if(!x)return null;return {get n(){return +x[ref.field]||0;},set n(v){x[ref.field]=v;}};}
function empireHoldingHTML(p){if(!p||tPhase()!=="empire")return "";const pt=PT(p),used=pt.holdingActs||{},out=[],allArmies=D.players.flatMap(q=>(q.board.armies||[]).map(a=>({p:q,a,k:armyHex(q,a)}))).filter(x=>x.k),ownArmies=allArmies.filter(x=>sameP(x.p,p)),territory=terrOwners();
  const moves=srcMatch(p.board,"start_empire_move").map(x=>({src:x.n,key:"move:"+x.n,province:false})).concat(srcMatch(p.board,"beacon_start_move").map(x=>({src:x.n,key:"beacon:"+x.n,province:true})));
  moves.forEach(m=>{if(+used[m.key]===tTurn())return;const avail=ownArmies.filter(x=>!armyBlocked(x.p,x.a)&&(!m.province||(territory[x.k]&&territory[x.k].has(String(p.id)))));
    out.push('<div class="tb-row"><span style="flex:1">'+esc(m.src)+(m.province?' · Army in your Province':' · Move action')+'</span>'+ (avail.length?avail.map(x=>'<button data-do="holdMove" data-who="'+p.id+'" data-key="'+esc(m.key)+'" data-pid="'+x.p.id+'" data-aid="'+esc(x.a.id)+'">'+esc(x.p.name)+' · '+esc(armyName(x.a))+' ▸</button>').join(""):'<span class="note">No eligible unblocked Army on the map.</span>')+'</div>');});
  const cb=srcMatch(p.board,"cipher_block_army"),ct=srcMatch(p.board,"cipher_timer_plus");if(cb.length&&+used.cipherArmy!==tTurn()){
    const last=pt.cipherArmy||{},opts=allArmies.filter(x=>!(last.turn===tTurn()-1&&last.id===String(x.p.id)+":"+String(x.a.id)));
    out.push('<div class="tb-row"><span style="flex:1">Cipher Chamber · give an Army Blocked</span>'+ (opts.length?'<select id="cipherArmyPick">'+opts.map(x=>'<option value="'+x.p.id+':'+esc(x.a.id)+'">'+esc(x.p.name)+' · '+esc(armyName(x.a))+'</option>').join("")+'</select><button data-do="cipherArmy" data-who="'+p.id+'">apply</button>':'<span class="note">No different Army from last turn.</span>')+'</div>');}
  if(ct.length&&+used.cipherTimer!==tTurn()){
    const last=pt.cipherTimer||{},timers=activeCipherTimers().filter(x=>!(last.turn===tTurn()-1&&last.id===x.key));
    out.push('<div class="tb-row"><span style="flex:1">Cipher Chamber · increase an active Timer by '+(+ct[0].m[1]||2)+'</span>'+ (timers.length?'<select id="cipherTimerPick">'+timers.map(x=>'<option value="'+esc(JSON.stringify(x.ref))+'">'+esc(x.label)+'</option>').join("")+'</select><button data-do="cipherTimer" data-who="'+p.id+'" data-n="'+(+ct[0].m[1]||2)+'">increase</button>':'<span class="note">No different active Timer from last turn.</span>')+'</div>');}
  const cd=pt.courierDeferred;if(cd&&cd.due<=tTurn()&&!cd.done)out.push('<div class="tb-row"><span style="flex:1">Courier Network · perform deferred '+esc(cd.act)+(cd.target?' → '+esc(pById(cd.target)?.name||'target'):'')+'</span><button data-do="courierDeferred" data-who="'+p.id+'">perform ▸</button></div>');
  const bs=srcMatch(p.board,"start_empire_spread");if(bs.length&&+used.exaltedSpread!==tTurn())out.push('<div class="tb-row"><span style="flex:1">Exalted Basilica · Endorsed Spread Truth</span><button data-do="basilicaSpread" data-who="'+p.id+'">perform ▸</button></div>');
  const st=(p.board.placed||[]).filter(x=>x.name==="Studium Generale"&&pActive(x)&&!x.fac),chosen=pt.studiumEffects||{};
  st.filter(x=>!chosen[String(x.id)]).forEach(x=>{const avail=T_DOMS.filter(d=>((p.board.domains||{})[d]||0)<SOV&&!Object.keys(chosen).some(k=>chosen[k]===d));
    out.push('<div class="tb-row"><span style="flex:1">Studium Generale · choose one free Sovereign Domain effect</span>'+ (avail.length?'<select id="studiumDomain-'+esc(x.id)+'">'+avail.map(d=>'<option value="'+d+'">'+d+' · '+esc(String((DBOARD[d]||{}).Sovereign||"").split(":").slice(1).join(":").trim())+'</option>').join("")+'</select><button data-do="studiumChoose" data-who="'+p.id+'" data-id="'+esc(x.id)+'">gain effect</button>':'<span class="note">No unselected Sovereign Domain effects available.</span>')+'</div>');});
  standingPhaseActions(p).forEach(z=>{let control;if(z.action==="Move"){const pick="stMovePick-"+String(p.id).replace(/[^A-Za-z0-9_-]/g,"")+"-"+z.key.replace(/[^A-Za-z0-9_-]/g,"-"),arms=ownArmies.filter(x=>!armyBlocked(x.p,x.a));
      control=arms.length?'<select id="'+pick+'">'+arms.map(x=>'<option value="'+esc(x.a.id)+'">'+esc(x.p.name)+' · '+esc(armyName(x.a))+'</option>').join("")+'</select><button data-do="standingMove" data-who="'+p.id+'" data-key="'+esc(z.key)+'" data-pick="'+pick+'">choose Army ▸</button>':'<span class="note">No eligible unblocked Army on the map.</span>';
    }else control=pfForm(z.env,null,"empire");
    out.push('<div class="tb-row"><span style="flex:1">'+esc(z.source)+' · '+esc(z.fin)+" "+esc(z.action)+" (Domain Standing)"+'</span>'+control+'</div>');});
  const automatic=epRows(p.board).filter(x=>x.auto&&x.n>0);if(automatic.length)out.push('<details class="tb-row"><summary class="note">Automatic Empire Phase Faith/Doubt effects ('+automatic.length+')</summary>'+automatic.map(x=>'<div class="note">'+esc(x.k)+': '+esc(x.side)+" +"+x.n+(x.desc?' · '+esc(x.desc):'')+'</div>').join("")+'</details>');
  const ds=dbActive(p.board);if(ds.length)out.push('<details class="tb-row"><summary class="note">Active Domain Standing effects ('+ds.length+')</summary>'+ds.map(x=>'<div class="note">'+esc(x.free?'Studium Generale · '+x.name:x.name+' ('+x.tier+' '+x.dom+')')+': '+esc(x.text)+'</div>').join("")+'</details>');
  return out.length?dockCard("Empire Phase effect stack — "+esc(p.name),out.join("")):"";}
function whisperGateHTML(R){
  if(R.waiting==="whisper-declare"){const E=R.whisperEnvoy;if(!E)return "";const p=E.owner;if(!canAct(p))return dockCard("Whispering Undercroft",'<div class="note">Waiting for '+esc(p.name)+' to declare '+esc(E.dom)+' action and target.</div>');
    return dockCard("Whispering Undercroft — declaration required",'<div class="note">'+esc(R.whisperBy&&R.whisperBy.name||"A player")+' selected '+esc(p.name)+"'s "+esc(E.dom)+" Envoy. Declare the specific action, target, and sub-action now. If it passes or is endorsed, this choice will be locked in."+'</div>'+pfForm(E,null,"whisper"),"now");}
  return "";}
function forgeRetryHTML(R,p){if(!p||R.waiting!=="tally-retry"||!sameP(p,R.tallyWho))return "";if(!canAct(p))return dockCard("Tally Phase — retry",'<div class="note">Waiting for '+esc(p.name)+' to decide on a Forgery Workshop retry.</div>');
  const src=srcMatch(p.board,"forge_retry")[0].n;return dockCard("Tally Phase — "+esc(src)+" · "+esc(p.name),'<div class="note">A Cunning Envoy you sent Failed. Send another Cunning Envoy? It is voted on now.</div>'+
    R.retryFailed.map(E=>'<div class="tb-row"><span style="flex:1">'+esc(E.dom)+" Envoy · net "+E.net+' · Failed</span><button data-do="forgeRetry" data-who="'+p.id+'" data-env="'+esc(E.id)+'">send another Cunning Envoy</button></div>').join("")+
    '<div class="tb-row"><button data-do="retryPass" data-who="'+p.id+'">skip</button></div>',"now");}
function courierDeferHTML(R,p){if(!p||tPhase()!=="envoy"||!canAct(p)||!srcMatch(p.board,"courier_defer").length)return "";const pt=PT(p);if((pt.holdingActs||{}).courierDefer===tTurn()||(pt.courierDeferred&&!pt.courierDeferred.done))return "";
  const rows=R.envoys.filter(E=>sameP(E.owner,p)&&!E.council&&E.done&&E.out!=="Failed"&&E.out!=="Condemned").map(E=>{const pe=performEval(E);if(!pe||!(pe.out==="Passed"||pe.out==="Endorsed")||!pe.rec.action)return "";
    const target=pe.tgt?" → "+pe.tgt.name:"";return '<div class="tb-row"><span style="flex:1">'+esc(E.dom)+" · "+esc(pe.rec.action)+esc(target)+"</span><button data-do=\"courierDeferChoose\" data-who=\""+p.id+"\" data-env=\""+esc(E.id)+"\">defer to next Empire Phase</button></div>";}).filter(Boolean);
  return rows.length?dockCard("Courier Network — choose a Performed Personal Envoy",rows.join("")):"";}
DO.holdMove=el=>{const p=pOf(el),q=pById(el.dataset.pid),a=q&&(q.board.armies||[]).find(x=>String(x.id)===String(el.dataset.aid)),key=el.dataset.key;
  if(!p||!q||!a||!canAct(p)||tPhase()!=="empire")return;const pt=PT(p),used=pt.holdingActs||{};if(+used[key]===tTurn())return;
  if(key.startsWith("beacon:")&&!(terrOwners()[armyHex(q,a)]||new Set()).has(String(p.id))){flash("Beacon Towers can only move an Army in your Province");return;}
  if(armyBlocked(q,a)){flash("That Army is Blocked");return;}pt.holdMove={turn:tTurn(),key,aid:String(a.id),armyPid:String(q.id),holderPid:String(p.id)};SEL={pid:String(q.id),aid:String(a.id)};INSP=armyHex(q,a);save();render();flash(p.name+": select a lit hex to perform the Move");};
DO.cipherArmy=el=>{const p=pOf(el),v=(document.getElementById("cipherArmyPick")||{}).value||"",[pid,aid]=v.split(":"),q=pById(pid),a=q&&(q.board.armies||[]).find(x=>String(x.id)===aid);if(!p||!a||!canAct(p)||tPhase()!=="empire")return;
  const pt=PT(p),last=pt.cipherArmy||{};if(last.turn===tTurn()-1&&last.id===v){flash("Choose a different Army than last turn");return;}a.blocked=true;a.blockedT=tTurn();pt.cipherArmy={turn:tTurn(),id:v};pt.holdingActs=pt.holdingActs||{};pt.holdingActs.cipherArmy=tTurn();noteAdd(p,"Cipher Chamber: "+armyName(a)+" gains Blocked");save();render();};
DO.cipherTimer=el=>{const p=pOf(el),raw=(document.getElementById("cipherTimerPick")||{}).value;if(!p||!canAct(p)||tPhase()!=="empire")return;let ref;try{ref=JSON.parse(raw);}catch(e){return;}const t=cipherTimerResolve(ref);if(!t||!(t.n>0))return;
  const key=activeCipherTimers().find(x=>JSON.stringify(x.ref)===JSON.stringify(ref))?.key||JSON.stringify(ref),pt=PT(p),last=pt.cipherTimer||{};if(last.turn===tTurn()-1&&last.id===key){flash("Choose a different Timer than last turn");return;}
  const n=Math.max(1,+el.dataset.n||2);t.n+=n;pt.cipherTimer={turn:tTurn(),id:key};pt.holdingActs=pt.holdingActs||{};pt.holdingActs.cipherTimer=tTurn();noteAdd(p,"Cipher Chamber: Timer +"+n);save();render();};
DO.cunningRecoup=el=>{const p=pOf(el),key=el.dataset.key;if(!p)return;const c=tCurW(p),r=(c.cunningRecoups||[]).find(x=>x.key===key);if(!r||r.claimed||r.turn!==tTurn()||!canAct(p))return;
  if(!srcMatch(p.board,"recoup_on_cunning").some(x=>x.n===r.src))return;tGold(p.board,+r.amount,"Thieves' Guild Recoup · "+r.act);r.claimed=true;noteAdd(p,"Thieves' Guild: Recoup "+(+r.amount).toLocaleString()+" gold after "+r.act);save();render();};
DO.basilicaSpread=el=>{const p=pOf(el);if(!p||!canAct(p)||tPhase()!=="empire"||!srcMatch(p.board,"start_empire_spread").length)return;
  const pt=PT(p);pt.holdingActs=pt.holdingActs||{};if(+pt.holdingActs.exaltedSpread===tTurn())return;
  const E={id:"BASILICA:"+p.id+":"+tTurn(),owner:p,dom:"Piety",council:false,votes:[],net:3,out:"Endorsed",done:true},res=resolveEnvoy(E,{rec:{action:"Spread Truth",target:""}},"Endorsed"),c=tCurW(p);c.applied=c.applied||{};
  c.applied[E.id]={out:"Endorsed",dom:"Piety · Exalted Basilica",act:"Spread Truth",fx:res.fx,flags:res.flags};pt.holdingActs.exaltedSpread=tTurn();save();render();};
DO.studiumChoose=el=>{const p=pOf(el),id=String(el.dataset.id),d=(document.getElementById("studiumDomain-"+id)||{}).value,st=p&&(p.board.placed||[]).find(x=>String(x.id)===id&&x.name==="Studium Generale"&&pActive(x)&&!x.fac);
  if(!p||!st||!T_DOMS.includes(d)||((p.board.domains||{})[d]||0)>=SOV||Object.keys(PT(p).studiumEffects||{}).some(k=>PT(p).studiumEffects[k]===d)||!canAct(p)||tPhase()!=="empire"||((PT(p).studiumEffects||{})[id]))return;
  const fx=(DBOARD[d]||{}).Sovereign;if(!fx)return;const pt=PT(p);pt.studiumEffects=pt.studiumEffects||{};pt.studiumEffects[id]=d;
  if(STANDING_ACT_RE.test(String(fx))){pt.standingPending=pt.standingPending||{};pt.standingPending[standingKey({free:true,id})]={due:tTurn()};}
  noteAdd(p,"Studium Generale: gained "+String(fx).split(":")[0]+" (free Sovereign "+d+" effect)");save();render();};
DO.standingMove=el=>{const p=pOf(el),key=el.dataset.key,z=p&&standingPhaseActions(p).find(x=>x.key===key),raw=(document.getElementById(el.dataset.pick)||{}).value,a=p&&(p.board.armies||[]).find(x=>String(x.id)===String(raw));
  if(!p||!z||z.action!=="Move"||!a||!canAct(p)||tPhase()!=="empire"||armyBlocked(p,a))return;
  const pt=PT(p);if(pt.holdMove&&pt.holdMove.turn===tTurn()){flash("Finish the pending Move action first");return;}
  pt.holdMove={turn:tTurn(),key:z.key,aid:String(a.id),armyPid:String(p.id),holderPid:String(p.id)};SEL={pid:String(p.id),aid:String(a.id)};INSP=armyHex(p,a);save();render();flash(p.name+": select a lit hex to perform the Domain Standing Move");};
DO.standingPerform=el=>{const p=pOf(el),z=p&&standingPhaseActions(p).find(x=>x.id===el.dataset.env);if(!p||!z||!canAct(p)||tPhase()!=="empire")return;
  const pt=PT(p);pt.holdingActs=pt.holdingActs||{};if(+pt.holdingActs[z.key]===tTurn())return;const d=PF[z.id]||{},a=d.action||"",sp=pfSpec(a),tg=String(d.target||""),T=pfTargets(z.env,a).find(x=>x.v===tg);
  const subs=pfSubs(p,a,tg),pls=sp.place?sp.place(p,d.sub):null;if(a!==z.action||!T||!T.legal||(subs&&!subs.some(x=>x.v===d.sub&&!x.dis))||(pls&&pls.length&&!pls.some(x=>x.v===d.place&&!x.dis))){flash("Choose a legal "+z.action+" action before resolving this Standing effect");return;}
  const rec={action:a,target:tg,sub:d.sub||"",place:d.place||""},res=resolveEnvoy(z.env,{rec},z.fin),c=tCurW(p);c.applied=c.applied||{};
  c.applied[z.id]={out:z.fin,dom:z.source+" (Domain Standing)",act:a,fx:res.fx,flags:res.flags};pt.holdingActs[z.key]=tTurn();delete pt.standingPending[z.key];noteAdd(p,z.source+": "+z.fin+" "+a+(T.label&&T.label!=="—"?" → "+T.label:""));delete PF[z.id];save();render();};
DO.whisperDeclare=el=>{const p=pOf(el),R=tSim(),E=R.whisperEnvoy;if(!p||!E||!sameP(p,E.owner)||R.waiting!=="whisper-declare"||!canAct(p))return;const d=PF[E.id]||{},a=d.action||"",sp=pfSpec(a),tg=String(d.target||""),T=pfTargets(E,a).find(x=>x.v===tg);
  const subs=pfSubs(p,a,tg),pls=sp.place?sp.place(p,d.sub):null;if(!a||!T||!T.legal||(subs&&!subs.some(x=>x.v===d.sub&&!x.dis))||(pls&&pls.length&&!pls.some(x=>x.v===d.place&&!x.dis))){flash("Choose a legal action, target, and sub-action before declaring");return;}
  const c=tCurW(p);c.perform=c.perform||{};c.perform[E.id]={action:a,target:tg,sub:d.sub||"",place:d.place||"",whisperLock:{by:R.whisperBy&&String(R.whisperBy.id)||"",turn:tTurn()},ts:tnow()};
  const h=R.whisperBy;if(h){const u=PT(h).whisperUse;if(u&&u.turn===tTurn())u.done=true;}delete PT(p).whisperDeclare;delete PF[E.id];save();render();};
DO.forgeRetry=el=>{const p=pOf(el),R=tSim(),E=R.envoys.find(x=>x.id===el.dataset.env&&p&&sameP(x.owner,p));if(!p||!E||!canAct(p)||R.waiting!=="tally-retry"||!sameP(p,R.tallyWho)||E.dom!=="Cunning"||!E.done||E.out!=="Failed"||!srcMatch(p.board,"forge_retry").length||(PT(p).forgeRetry&&PT(p).forgeRetry.turn===tTurn()))return;
  const failedRec=(tCur(p).perform||{})[E.id]||{},old=failedRec.target?String(failedRec.target):R.envoys.filter(x=>sameP(x.owner,p)&&x.dom==="Cunning"&&x.id!==E.id).map(x=>{const z=(tCur(p).perform||{})[x.id];return z&&z.target?String(z.target):"";}).filter(Boolean).pop()||"";
  PT(p).forgeRetry={turn:tTurn(),from:E.id,excludeTarget:old,src:srcMatch(p.board,"forge_retry")[0].n};tCurW(p).retryDec={send:true,ts:tnow()};save();render();};
DO.retryPass=el=>{const p=pOf(el),R=tSim();if(!p||R.waiting!=="tally-retry"||!sameP(p,R.tallyWho)||!canAct(p))return;tCurW(p).retryDec={send:false,ts:tnow()};rlCommit();};
DO.courierDeferChoose=el=>{const p=pOf(el),R=tSim(),E=R.envoys.find(x=>x.id===el.dataset.env&&p&&sameP(x.owner,p)),pe=E&&performEval(E);if(!p||!E||!pe||!pe.rec.action||!canAct(p)||tPhase()!=="envoy"||!srcMatch(p.board,"courier_defer").length)return;
  if(!(pe.out==="Passed"||pe.out==="Endorsed"))return;const pt=PT(p);pt.courierDeferred={due:tTurn()+1,act:pe.rec.action,dom:E.dom,target:pe.rec.target||"",sub:pe.rec.sub||"",place:pe.rec.place||"",src:srcMatch(p.board,"courier_defer")[0].n,from:E.id,done:false};
  const oe=onceEffects(p).find(x=>/Performed next turn|select a Personal Action you performed this turn/i.test(x.c));if(oe)onceUse(p,oe.key,oe.game,true);else{const f=srcMatch(p.board,"envoy_next_fewer")[0];if(f)pt.envNext={turn:tTurn()+1,n:-(+f.m[1]),src:f.n};}
  pt.holdingActs=pt.holdingActs||{};pt.holdingActs.courierDefer=tTurn();save();render();};
DO.courierDeferred=el=>{const p=pOf(el);if(!p||!canAct(p)||tPhase()!=="empire")return;const pt=PT(p),cd=pt.courierDeferred;if(!cd||cd.done||cd.due>tTurn())return;
  const E={id:"COURIER:"+p.id+":"+tTurn(),owner:p,dom:cd.dom,council:false,votes:[],net:1,out:"Passed",done:true},rec={action:cd.act,target:cd.target,sub:cd.sub,place:cd.place},res=resolveEnvoy(E,{rec},"Passed"),c=tCurW(p);c.applied=c.applied||{};
  c.applied[E.id]={out:"Passed",dom:cd.dom+" · Courier Network",act:cd.act,fx:res.fx,flags:res.flags};cd.done=true;save();render();};

// ---- drawers: open state per device; bodies render only while open ----
var RL_OPEN=new Set(["rlLog"]),RL_SHUT=new Set(),RL_MAP=false;
try{const v=localStorage.getItem("renown_rl_open");if(v)RL_OPEN=new Set(JSON.parse(v));const w=localStorage.getItem("renown_rl_shut");if(w)RL_SHUT=new Set(JSON.parse(w));
  RL_MAP=localStorage.getItem("renown_rl_map")==="1";}catch(e){}
function rlOpen(id,def){return def?!RL_SHUT.has(id):RL_OPEN.has(id);}
function rlToggle(d){if(d.open){RL_OPEN.add(d.id);RL_SHUT.delete(d.id);}else{RL_OPEN.delete(d.id);RL_SHUT.add(d.id);}
  try{localStorage.setItem("renown_rl_open",JSON.stringify([...RL_OPEN]));localStorage.setItem("renown_rl_shut",JSON.stringify([...RL_SHUT]));}catch(e){}
  if(D.view==="table")setTimeout(renderTable,0);}
document.addEventListener("toggle",e=>{const d=e.target;if(d&&d.dataset&&d.dataset.keep!=null&&d.id){if(rlOpen(d.id,d.dataset.keep==="1")!==d.open)rlToggle(d);}},true);

function renderTable(){
  const host=document.getElementById("viewTable");if(!host)return;
  const R=tSim();T_SIG=tSig(R);
  if(!host.querySelector(".rl"))host.innerHTML='<div class="rl"><div class="rl-grid"><div class="rl-main"><div id="rlTable"></div>'+
    '<button class="rl-maptog" data-do="maptog" data-nav="1"></button><div class="tb-felt rl-felt" id="rlFelt"><div id="rlBar"></div><div class="tb-map" id="rlMap"></div><div id="rlCard"></div></div>'+
    '<div id="viewRealm"></div></div><div class="rl-side"><div id="rlPhase"></div><div id="rlDock"></div></div></div><div id="rlHover" class="rl-hover" hidden></div></div>';
  {const rl=host.querySelector(".rl");rl.classList.toggle("wide",TB_WIDE);rl.classList.toggle("rl-mapon",RL_MAP);rl.querySelector(".rl-maptog").textContent=RL_MAP?"Hide map":"Show map";}
  const $=id=>host.querySelector("#"+id),M=mapState(),hasMap=!!(M.grid||Object.keys(M.cells).length);
  patch($("rlTable"),realmTableHTML(R));
  renderRealmMap($("rlMap"),M,hasMap);
  const w1=patch($("rlBar"),hasMap?mapBarHTML():""),w2=patch($("rlCard"),inspHTML());
  patch($("rlPhase"),phaseCardHTML(R));
  patch($("rlDock"),dockHTML(R));
  const w3=patch($("viewRealm"),drawersHTML(R));
  if(rlOpen("rlEdicts",false))try{renderRenown();}catch(e){console.warn("edicts",e);}
  if(rlOpen("rlTools",false)&&mods().diplomacy)try{renderDash();}catch(e){console.warn("diplomacy",e);}
  if(w1||w2||w3){wireMap(host);wireInsp(host);if(w3){wireBanditAuto(host);wireDashExtras($("viewRealm"));}}
  tCountdown(R);}

// ---- map region: the terrain layer is rebuilt only when the map itself changes; pieces and overlays every render ----
function renderRealmMap(box,M,hasMap){
  box.classList.toggle("zm",!MAPZ.fit);
  if(!hasMap){box._key=null;patch(box,'<div class="note" style="padding:12px">No map — Tools ▸ Map setup.</div>');return;}
  const L=mapLayers(M);let sv=box.querySelector("svg.rmap");
  if(!sv||box._key!==L.key){box.innerHTML='<svg class="rmap" viewBox="0 0 '+L.W.toFixed(0)+' '+L.H.toFixed(0)+'" style="display:block"><defs>'+L.defs+'</defs><g class="mp-base">'+L.base+'</g><g class="mp-ov"></g></svg>';
    box._key=L.key;box._h=null;sv=box.querySelector("svg.rmap");}
  if(MAPZ.fit){sv.setAttribute("width","100%");sv.setAttribute("height","100%");sv.setAttribute("preserveAspectRatio","xMidYMid meet");}
  else{sv.setAttribute("width",(L.W*L.z).toFixed(0));sv.setAttribute("height",(L.H*L.z).toFixed(0));sv.removeAttribute("preserveAspectRatio");}
  const ov=sv.querySelector(".mp-ov");if(ov._h!==L.over){ov.innerHTML=L.over;ov._h=L.over;}}
DO.cell=el=>mapCellClick(el.dataset.cell);

// ---- player table: one row per seat. Click a row: view that Empire (read-only unless it's yours). Hover: a mini card ----
function domCells(b){const dv=b.domains||{};
  return DOMAINS.map(d=>{const v=+dv[d]||0,st=domBand(v),i=["Untested","Rising","Established","Sovereign"].indexOf(st);
    const L=[d+" "+v+" · "+st].concat(dbActive(b).filter(x=>x.dom===d).map(x=>"  "+x.tier+": "+x.text));
    return '<td class="num rt-d st'+i+'" data-tipl="'+esc(L.join("\n"))+'">'+v+'</td>';}).join('');}
function realmTableHTML(R){const sm=seatMap(),n=tSeats(),me=meP(),hp=hostP(),sp=R.ord[0]||null,cw=R.cur?R.cur.who:null,ph=tPhase(),E=R.curEnvoy,EE=ERAS[currentEra()]||{};
  const bst=Math.max(0,...D.players.map(edictTotal)),sg=v=>(v>0?"+":v<0?"−":"")+Math.abs(v).toLocaleString(),sl=seatsLocked();
  let rows='';
  for(let i=0;i<n;i++){const p=sm[i];
    if(!p){rows+='<tr class="rt-empty"><td class="num">'+(i+1)+'</td><td colspan="14"><span class="note">empty seat</span> '+(sl||!me?'':'<button data-do="sit" data-i="'+i+'" class="tb-mini">sit here</button>')+'</td></tr>';continue;}
    const h=hudData(p),pool=R.pool[p.id]??inflPool(p),left=pool-(R.spent[p.id]||0),dv=p.board.domains||{};
    // Domain values allowed: start + 1 per Renown gained; the Rest Phase's Domain Point is spent before End turn raises Renown
    const dsum=DOMAINS.reduce((a,d)=>a+(+dv[d]||0),0),dmax=startDomTotal(p)+((D.renown||1)-1)+(TB().dpGiven===tTurn()?(DATA.dpPerTurn??1):0);
    const tp=hudTips(p,h),tl=k=>' data-tipl="'+esc(tp[k])+'"';
    let st='';
    if(ph==="envoy"&&TB().phaseTs){const dc=tCur(p).decl||{};
      if(R.waiting==="declare")st=dc.lock?'<span class="pos">declared ✓</span>':'<span class="note">declaring…</span>';
      else{const nn=dc.n||{};st=T_ALL.filter(d=>+nn[d]>0).map(d=>d.slice(0,3)+" ×"+nn[d]).join(" · ");}}
    if(ph==="council"&&TB().phaseTs&&!R.councilDom){const lv=R.log.find(l=>l.kind==="cvote"&&sameP(l.who,p));
      st=lv?(lv.dom?'voted <b>'+lv.dom+'</b>':'no vote'):sameP(p,cw)?'<b>voting…</b> <span class="tbcd"></span>':'';}
    if(E){if(sameP(E.owner,p))st='sending <b>'+esc(E.dom)+'</b>';
      else{const v=E.votes.find(q=>sameP(q.who,p));st=v?tVoteTxt(v):sameP(p,cw)?'<b>to act</b> <span class="tbcd"></span>':'<span class="note">…</span>';}}
    const cls=["rt-row"];if(sameP(p,cw))cls.push("act");if(sameP(p,me))cls.push("me");
    rows+='<tr class="'+cls.join(" ")+'" data-do="spectate" data-who="'+p.id+'"><td class="num">'+(i+1)+'</td>'+
      '<td class="rt-p" data-hov="'+p.id+'">'+tName(p)+
        (sameP(p,hp)?' <span class="tb-b h" title="'+(isSpring()?'Host token — no Host in Spring':'Host')+'">'+(isSpring()?'Host token':'♔ Host')+'</span>':'')+
        (sameP(p,sp)?' <span class="tb-b s" title="Starting player">1st</span>':'')+(sameP(p,me)?' <span class="tb-b">you</span>':'')+
        ((!sl&&sameP(p,me))||ADMIN?' <button data-do="stand" data-who="'+p.id+'" class="tb-mini">stand</button>':'')+'</td>'+
      '<td class="num"'+tl("gold")+'>'+fmtG(h.gold)+' <span class="'+(h.net<0?"neg":"pos")+'">'+sg(h.net)+'</span></td>'+
      '<td class="num"'+tl("infl")+'>'+left+'<span class="note">/'+pool+'</span></td>'+
      '<td class="num"'+tl("env")+'>'+personalEnvoys(p)+'</td>'+
      '<td class="num"'+tl("po")+'>'+(h.po>0?"+":"")+h.po+'</td>'+
      '<td class="num"'+tl("armies")+'>'+h.armies+(h.armyCap!=null?'<span class="note">/'+h.armyCap+'</span>':'')+'</td>'+
      '<td class="num"'+tl("setts")+'>'+h.setts+(h.settCap!=null?'<span class="note">/'+h.settCap+'</span>':'')+'</td>'+
      '<td class="num"'+tl("edicts")+(h.edicts===bst&&bst>0?' style="color:var(--income);font-weight:700"':'')+'>'+h.edicts+(h.edicts===bst&&bst>0?' ★':'')+'</td>'+
      domCells(p.board)+
      '<td class="rt-st">'+(dsum>dmax?'<span class="neg" title="Domain values '+dsum+' > '+dmax+' allowed">⚠ '+dsum+'/'+dmax+'</span> ':'')+st+'</td></tr>';}
  const unl=EE.unlocks&&EE.unlocks!=="—"?esc(EE.unlocks):'—',unseated=D.players.filter(p=>!Object.values(sm).includes(p));
  return '<div class="rt-wrap"><div class="rt-era note"><b>'+esc(currentEra())+'</b> · Cities <b>'+(EE.cities??'?')+'</b> · Unlocks: '+unl+
      (unseated.length?' · <span>Not seated: '+unseated.map(p=>esc(p.name)).join(", ")+'</span>':'')+'</div>'+
    '<div class="rt-scroll"><table class="dtable rtable"><thead><tr><th>#</th><th>Player</th><th>Gold</th><th title="Influence left / this turn">Infl</th><th>Envoys</th><th title="Public Order">PO</th><th>Armies</th><th title="Settlements">Setts</th><th>Edicts</th>'+
    DOMAINS.map(d=>'<th class="rt-dh" style="--dc:'+DOMC[d]+'" title="'+d+'">'+d.slice(0,3)+'</th>').join('')+'<th>Status</th></tr></thead><tbody>'+rows+'</tbody></table></div></div>';}
DO.sit=el=>{const p=meP();if(!p)return;const x=PT(p);x.seat=+el.dataset.i;x.seatTs=tnow();rlCommit();};
DO.stand=(el,e)=>{e.stopPropagation();const p=pOf(el)||meP(),x=PT(p);delete x.seat;delete x.seatTs;rlCommit();};
// spectate: open that player's Empire; read-only unless it's yours (or you act for everyone: hot-seat / the Duke)
let SPECTATE=null,SPEC_FROM=null;
function spectating(){return SPECTATE!=null&&D.view==="board"&&String((D.players[D.active]||{}).id)===String(SPECTATE);}
DO.spectate=(el,e)=>{if(e.target.closest("button,select,input,a"))return;const p=pOf(el);if(!p)return;
  const me=meP();SPEC_FROM=me?String(me.id):null;SPECTATE=(sameP(p,me)||HOTSEAT||ADMIN)?null:String(p.id);D.active=D.players.indexOf(p);D.view="board";reindex();render();renderList();window.scrollTo(0,0);};
DO.unspectate=()=>{SPECTATE=null;const me=pById(SPEC_FROM)||meP();if(me)D.active=D.players.indexOf(me);reindex();render();renderList();};
// hover mini card
document.addEventListener("mouseover",e=>{const tr=e.target.closest&&e.target.closest("#viewTable [data-hov]"),box=document.getElementById("rlHover");if(!box)return;
  if(!tr){if(!e.target.closest||!e.target.closest("#rlHover"))box.hidden=true;return;}
  const p=pById(tr.dataset.hov);if(!p){box.hidden=true;return;}
  if(box._p!==tr.dataset.hov){box.innerHTML=miniCardHTML(p);box._p=tr.dataset.hov;}
  const r=tr.closest("tr").getBoundingClientRect(),hr=document.getElementById("viewTable").querySelector(".rl").getBoundingClientRect();
  box.style.left=Math.max(8,Math.min(r.left-hr.left+180,hr.width-300))+"px";box.style.top=(r.bottom-hr.top+4)+"px";box.hidden=false;});
document.addEventListener("mouseleave",e=>{if(e.target&&e.target.id==="viewTable"){const b=document.getElementById("rlHover");if(b)b.hidden=true;}},true);
function miniCardHTML(p){const b=p.board,S_=b.settlements||[],cul=b.culture||"";
  const hold=sid=>(b.placed||[]).filter(q=>String(q.sid)===String(sid)&&!q.fac).map(q=>q.name+(q.bt>0?" ("+q.bt+")":q.dmg>0?" ✕":""));
  return '<div class="mc-h">'+heraldOf(p,20)+'<b>'+esc(p.name)+'</b> <span class="note">'+esc(b.faction||"")+(cul?' · '+esc(cul):'')+'</span></div>'+
    S_.map(s=>{const L=hold(s.id);return '<div class="mc-s"><b>'+(s.capital?'★ ':'')+esc(s.name||s.tier)+'</b> <span class="note">'+esc(s.tier)+'</span>'+
      (L.length?'<div class="mc-l">'+L.map(esc).join(' · ')+'</div>':'')+'</div>';}).join("")+
    (Object.keys(b.infra||{}).length?'<div class="mc-s"><span class="note">Infrastructure</span> '+Object.keys(b.infra).map(esc).join(' · ')+'</div>':'')+
    (Object.keys(b.wonders||{}).length?'<div class="mc-s"><span class="note">Wonders</span> '+Object.keys(b.wonders).map(esc).join(' · ')+'</div>':'')+
    '<div class="mc-s">'+((b.armies||[]).length?(b.armies||[]).map(a=>esc((a.label||"Army "+a.id)+" · "+(a.retinue||"")+" ×"+(a.count||0))).join('<br>'):'<span class="note">no Armies</span>')+'</div>';}

// ---- phase card (Host controls fold in here for the Host; hidden for everyone else) ----
function phaseCardHTML(R){
  const t=TB(),ph=tPhase(),me=meP(),hp=hostP(),cw=R.cur?R.cur.who:null,E=R.curEnvoy,hc=canHost();
  let h='<div class="tot tb-phase rl-phase"><div class="note">Turn '+tTurn()+' · '+esc(curSeason())+' · '+esc(currentEra())+'</div><h2>'+T_PHL[ph]+'</h2>'+
    '<div class="tb-hostline'+(hp&&sameP(hp,me)?' me':'')+'">'+(isSpring()?'Spring — no Host':hp?(sameP(hp,me)?'♔ You are the Host':'♔ Host: '+tName(hp)):'No Host seated')+'</div>';
  if(R.waiting==="seat")h+='<div class="note">Take a seat to begin.</div>';
  else if(R.waiting==="start")h+='<div class="note">Waiting for the Host to begin.</div>';
  else if(R.waiting==="declare")h+='<div>Declare Envoys — '+(R.ord.length-R.declPending.length)+'/'+R.ord.length+' submitted</div>';
  else if(R.waiting==="tie")h+='<div>Council vote tied — <b>'+R.tieCands.join(" / ")+'</b><br><span class="note">'+(hostP()?"the Host's vote isn't one of them — Host breaks the tie":"no Host — break the tie")+'</span></div>';
  else if(ph==="council"&&!R.councilDom&&cw)h+='<div>Council vote: '+tName(cw)+' <span class="tbcd tb-timer"></span></div>';
  if(E){const net=E.council?Math.max(1,E.innate+E.sup-E.opp):E.innate+E.sup-E.opp,o=tOutcome(net);
    h+='<div class="tb-env">'+tName(E.owner)+' → <b>'+esc(E.dom)+'</b>'+(E.council?' <span class="tb-b">Council</span>':'')+(E.mission?' <span class="tb-b">Mission</span>':'')+(eraActions(E.council)>1?' <span class="tb-b">×'+eraActions(E.council)+' actions</span>':'')+
      '<div class="note">'+innateTxt(E)+' · <span class="pos">+'+E.sup+'</span> · <span class="neg">−'+E.opp+'</span></div>'+
      (envBadges(E)?'<div>'+envBadges(E)+'</div>':'')+
      '<div>net <b>'+net+'</b> → <b class="'+tOutCls(o)+'">'+o+'</b> <span class="note">(so far)</span></div>'+
      (cw?'<div class="note">'+tName(cw)+' to act</div><div class="tbcd tb-timer"></div>':'')+'</div>';}
  else if(R.done&&(ph==="council"||ph==="envoy")&&t.phaseTs)h+='<div class="pos">All Envoys resolved.</div>';
  if(R.councilDom)h+='<div class="note">Council Domain: <b>'+R.councilDom+'</b>'+(R.tieBy?' — tie ('+R.tieBy.cands.join(" / ")+') broken by the Host’s vote ('+esc(R.tieBy.who.name)+')':'')+'</div>';
  if(ph==="council"&&isSpring())h+='<div>Spring — no Council Phase.</div>';
  if(ph==="rest")h+='<div class="note">Unused Envoys & Influence are discarded · Season +1 · gain Renown · spend a Domain Point · Host passes clockwise (not in Spring).</div>'+
    (dpOwed().length?'<div>Domain Points to spend: <b>'+dpOwed().map(p=>esc(p.name)+' '+p.board.dp).join(', ')+'</b></div>':'<div class="pos">Domain Points spent.</div>');
  if(hc){const nx=tNext(ph),vt=(ph==="council"&&!isSpring())||ph==="envoy";
    h+='<div class="rl-hostbar">'+(vt?'<button data-do="begin">'+(t.phaseTs?'Restart Phase':'Begin')+'</button>':'')+
      (vt&&R.cur?'<button data-do="add30" title="Give the current voter 30 more seconds; if the timer is off, start a 30-second timer for this vote">Add 30s</button>':'')+
      (R.cur?'<button data-do="skip" title="current voter abstains">Skip current</button>':'')+
      '<button data-do="phase" data-ph="'+nx+'">'+esc(T_PHL[nx].replace(" Phase",""))+' ▸</button>'+
      (ph==="rest"?'<button data-do="endturn" class="on">End turn</button>':'')+'</div>'+
      '<details class="rl-hostset" id="rlHostSet" data-keep="0"'+(rlOpen("rlHostSet",false)?' open':'')+'><summary class="note">Host settings</summary>'+
      '<div class="tb-row"><span class="note" style="flex:1">Phase</span>'+T_PH.filter(p2=>!(p2==="council"&&isSpring())).map(p2=>'<button data-do="phase" data-ph="'+p2+'"'+(p2===ph?' class="on"':'')+'>'+T_PHL[p2].replace(" Phase","")+'</button>').join("")+'</div>'+
      '<div class="tb-row"><span style="flex:1">Host</span><select data-do="host">'+seated().map(p=>'<option value="'+p.id+'"'+(sameP(p,hostP())?' selected':'')+'>'+esc(p.name)+'</option>').join("")+'</select></div>'+
      '<div class="tb-row"><span style="flex:1">Seats</span><input data-do="seats" type="number" min="'+seatFloor()+'" max="12" value="'+tSeats()+'" style="width:60px"></div>'+
      '<div class="tb-row"><span style="flex:1">Vote timer (s, 0 = off)</span><input data-do="timer" type="number" min="0" max="300" value="'+tTimer()+'" style="width:60px"></div>'+
      '<div class="tb-row"><label><input type="checkbox" data-do="boardend"'+(boardEndOn()?" checked":"")+'> End turn also runs every board\'s end turn (timers, net gold if auto-apply is on, Public Order, Endurance)</label></div>'+
      '<div class="tb-row"><label><input type="checkbox" data-do="autores"'+(autoRes()?" checked":"")+'> Auto-resolve actions (costs, Faith / Doubt, effects)</label></div>'+
      '<div class="tb-row"><button data-do="autoseat"'+(seatsLocked()?' disabled':'')+'>Auto-seat unseated players</button></div></details>';}
  {const pr=(DATA.phaseRules||{})[ph];if(pr)h+='<details class="tb-rules"><summary class="note">Rules — '+esc(T_PHL[ph])+'</summary><div class="note" style="text-align:left;margin-top:4px">'+mdLite(pr)+'</div></details>';}
  h+='<div class="rl-you note">You: '+(me?tName(me):'—')+(lockOn()?'':' · <label><input type="checkbox" data-do="hotseat"'+(HOTSEAT?" checked":"")+'> hot-seat (act for anyone)</label>')+'</div>';
  return h+'</div>';}
DO.begin=()=>{if(TB().phaseTs)tRestartPhase();else tSetPhase(tPhase());};
DO.add30=()=>tAdd30();
DO.phase=el=>{if(el.dataset.ph===tPhase()&&TB().phaseTs)tRestartPhase();else tSetPhase(el.dataset.ph);};
DO.skip=()=>{const R=tSim();if(R.cur){TB().skip[R.cur.key]=Math.max(tnow(),R.cur.start);rlCommit();}};
DO.endturn=()=>tEndTurn();
DO.autoseat=()=>tAutoSeat();
DO.host=el=>{TB().host=el.value;TB().hostSet=true;rlCommit();};
DO.seats=el=>{const want=+el.value,n=setSeats(want);if(want<n)flash("Seats can't go below "+n+" (players in the game)");rlCommit();};
DO.timer=el=>{TB().timer=Math.max(0,Math.min(300,+el.value||0));rlCommit();};
DO.boardend=el=>{TB().boardEnd=el.checked;rlCommit();};
DO.autores=el=>{TB().auto=el.checked;rlCommit();};
DO.hotseat=el=>{HOTSEAT=el.checked;try{localStorage.setItem("renown_hotseat",HOTSEAT?"1":"0");}catch(e){}renderTable();};

// ---- action dock: what this phase lets you do, in the order you do it ----
function dockCard(title,body,cls){return body?'<div class="tot dock'+(cls?' '+cls:'')+'"><div class="dk-h">'+title+'</div>'+body+'</div>':"";}
function dockHTML(R){
  const t=TB(),ph=tPhase(),me=meP(),E=R.curEnvoy,cw=R.cur?R.cur.who:null,qp=HOTSEAT?(cw||me):me,vt=(ph==="council"||ph==="envoy")&&t.phaseTs;
  if(!me)return dockCard("Spectating",'<div class="note">Claim a player to act.</div>');
  let h="";
  // Put once-per controls at the top of the action dock, before the current response/action prompts.
  h+=whisperGateHTML(R);
  h+=onceHTML(qp,ph);
  h+=intrigueHTML(R);
  h+=tallyHTML(R);
  h+=courierDeferHTML(R,qp);
  h+=forgeRetryHTML(R,qp);
  {const RCP=(tCur(qp).cunningRecoups||[]).filter(x=>x.turn===tTurn()&&!x.claimed);if(RCP.length)h+=dockCard("Thieves' Guild — Recoup",RCP.map(x=>'<div class="tb-row"><span style="flex:1">'+esc(x.src)+': after '+esc(pById(x.from)?.name||"another player")+"'s "+esc(x.act)+' Cunning action</span><button data-do="cunningRecoup" data-who="'+qp.id+'" data-key="'+esc(x.key)+'">recoup '+(+x.amount).toLocaleString()+'</button></div>').join(""));}
  // 1. Council vote
  if(ph==="council"&&t.phaseTs&&!R.councilDom&&R.waiting!=="tie"){const who=(cw&&canAct(cw)&&R.cur.key.startsWith("CV:"))?cw:me;
    if(!R.resolved.has("CV:"+who.id)&&tOrder().some(p=>sameP(p,who))){const cv=tCur(who).council;
      h+=dockCard("Council vote — "+esc(who.name)+(sameP(who,cw)?' <b>(your turn)</b>':' <span class="note">(queued, applies on your turn)</span>'),
        '<div class="tb-row">'+T_DOMS.map(d=>'<button data-do="cvote" data-dom="'+d+'" data-who="'+who.id+'"'+(cv&&cv.dom===d?' class="on"':'')+'>'+d+'</button>').join("")+
        (cv?'<button data-do="cvote" data-dom="" data-who="'+who.id+'">clear</button>':'')+'</div>',"now");}}
  if(R.waiting==="tie"&&canHost())h+=dockCard("Break the tie (Host)",'<div class="tb-row">'+R.tieCands.map(d=>'<button data-do="tie" data-dom="'+d+'">'+d+'</button>').join("")+'</div>',"now");
  // 2. Envoy declaration
  if(ph==="envoy"&&t.phaseTs&&R.waiting==="declare"){
    const targets=HOTSEAT?R.declPending:(R.declPending.some(p=>sameP(p,me))?[me]:[]);
    targets.slice(0,1).forEach(p=>{const dc=tCur(p).decl||{},nn=dc.n||{},tot=T_ALL.reduce((a,d)=>a+(+nn[d]||0),0),mx=personalEnvoys(p);
      h+=dockCard("Declare Envoys — "+esc(p.name)+' <span class="note">'+tot+'/'+mx+'</span>',(isSpring()?T_DOMS:T_ALL).map(d=>'<div class="tb-row"><span style="min-width:80px">'+d+'</span>'+
        '<button data-do="decl" data-dom="'+d+'" data-dv="-1" data-who="'+p.id+'">−</button><b style="min-width:16px;text-align:center">'+(+nn[d]||0)+'</b>'+
        '<button data-do="decl" data-dom="'+d+'" data-dv="1" data-who="'+p.id+'"'+(tot>=mx?' disabled':'')+'>+</button></div>').join("")+
        '<div class="tb-row"><button data-do="declock" data-who="'+p.id+'" class="on">Submit</button><span class="note">Hidden until everyone submits.</span></div>',"now");});
    if(!HOTSEAT&&(tCur(me).decl||{}).lock)h+=dockCard("Declare Envoys",'<div class="tb-row"><span class="pos">Submitted.</span><button data-do="declunlock" data-who="'+me.id+'">edit</button></div>');}
  // 3. vote on the current Envoy
  if(E&&cw&&canAct(cw)){const room=Math.max(0,(R.pool[cw.id]||0)-(R.spent[cw.id]||0)),capv=Math.min(voteCap(cw,E.dom,E.council),room);
    const cur=+(document.getElementById("tbAmt")||{}).value||1,amt=Math.max(1,Math.min(cur,capv||1)),blk=opposeBlock(cw,E);
    h+=dockCard(esc(cw.name)+" — respond to "+esc(E.owner.name)+"'s "+esc(E.dom)+' Envoy <span class="tbcd"></span>',
      '<div class="tb-row"><button data-do="vote" data-a="A" data-who="'+cw.id+'">Abstain</button>'+
      (capv>0?'<select id="tbAmt">'+Array.from({length:capv},(_,i)=>'<option'+(i+1===amt?' selected':'')+'>'+(i+1)+'</option>').join("")+'</select>'+
        '<button data-do="vote" data-a="S" data-who="'+cw.id+'" class="pos">Support</button>'+(blk?'<span class="note">'+esc(blk)+'</span>':'<button data-do="vote" data-a="O" data-who="'+cw.id+'" class="neg">Oppose</button>'):'<span class="note">no Influence available</span>')+'</div>'+
      (envBadges(E)?'<div>'+envBadges(E)+'</div>':'')+
      '<div class="note">Cap '+voteCap(cw,E.dom,E.council)+' ('+(E.dom==="Diplomacy"?currentEra():tStand(cw,E.dom))+') · '+room+' Influence left</div>',"now");}
  // 4. Perform: your Passed / Endorsed Envoys still waiting for their action
  if(vt)R.envoys.filter(E2=>(E2.out==="Passed"||E2.out==="Endorsed")&&resolveOpen(R,E2)&&canAct(E2.owner)&&(HOTSEAT||sameP(E2.owner,me))).forEach(E2=>{
    const rec=((tCur(E2.owner).perform)||{})[E2.id]||{},ap=(tCur(E2.owner).applied||{})[E2.id];
    if(ap&&!rec.edit&&E2.dom!=="Diplomacy")return;          // performed: shown in the Envoy queue and the Turn log (Diplomacy stays for "declined")
    h+=dockCard("Perform — "+esc(E2.owner.name)+" · "+esc(E2.dom)+(E2.council?" (Council)":"")+' <b class="'+tOutCls(E2.out)+'">'+E2.out+'</b>',tPerformHtml(E2),"now");});
  // 5. Diplomatic Mission (RULES › Rule: Diplomatic Mission)
  if(ph==="envoy"&&t.phaseTs)R.envoys.filter(E2=>E2.dom==="Diplomacy"&&E2.done&&missionWhy(E2)&&canAct(E2.owner)&&(HOTSEAT||sameP(E2.owner,me))).forEach(E2=>{
    const ms=(tCur(E2.owner).mission||{})[E2.id],open=T_DOMS.filter(d=>!domStarted(R,d));
    h+=dockCard("Diplomatic Mission — "+esc(E2.owner.name)+' <span class="note">('+esc(missionWhy(E2))+')</span>','<div class="tb-row">'+
      (ms?'<span>Mission: <b>'+esc(ms)+'</b></span>'+(domStarted(R,ms)?'':'<button data-do="mission" data-dom="" data-src="'+esc(E2.id)+'" data-who="'+E2.owner.id+'">cancel</button>'):
        open.length?open.map(d=>'<button data-do="mission" data-dom="'+d+'" data-src="'+esc(E2.id)+'" data-who="'+E2.owner.id+'">'+d+'</button>').join(""):'<span class="note">every Domain has started voting</span>')+'</div>');});
  // 6. Envoys: the phase's queue, resolved and upcoming, with your pre-votes inline
  if(vt&&tOrder().some(p=>sameP(p,qp)))h+=envoyQueueHTML(R,qp,ph);
  // 7. Influence & Envoys (Council and Envoy Phases)
  if(ph==="council"||ph==="envoy")h+=inflCardHTML(qp);
  // 8. Empire Phase: checklist, Extort targets, Extort by hand
  if(ph==="empire"){h+=empireHoldingHTML(qp);h+=dockCard("Empire Phase",empireChecklistHTML());h+=extortTargetsHTML(qp);
    h+=dockCard("Extort",'<div class="tb-row"><select id="exFrom">'+D.players.map(p=>'<option value="'+p.id+'">'+esc(p.name)+'</option>').join('')+'</select><span class="note">→</span>'+
      '<select id="exTo">'+D.players.map((p,i)=>'<option value="'+p.id+'"'+(i===1?' selected':'')+'>'+esc(p.name)+'</option>').join('')+'</select>'+
      '<input id="exAmt" type="number" min="0" step="100" value="500" style="width:70px"><button data-do="extort">extort</button></div>');}
  // 9. Battle Phase: Battles and Sieges to resolve
  if(ph==="battle"){const Q=bq(),sg=realmTimers().filter(x=>x.kind==="siege");
    h+=dockCard("Battles & Sieges",(Q.length?Q.map(o=>'<div class="tb-row">'+stIcon(o.kind==="sally"?"besieged":o.kind==="siege"?"sieging":"battle",14)+' <span style="flex:1">'+esc(bqSideName(o.A))+' <span class="note">vs</span> '+esc(bqSideName(o.B))+'</span>'+
        (mods().battle?'<button data-do="battleopen" data-q="'+o.id+'">open ▸</button>':'')+'</div>').join(""):'<div class="note">No Battles queued.</div>')+
      (sg.length?'<div class="note" style="margin-top:4px">'+sg.map(x=>esc((x.label||"Siege")+" · "+x.n)).join("<br>")+'</div>':'')+
      (mods().battle?'':'<div class="note">Battle module is off (⋯ ▸ modules).</div>'));}
  // 10. Rest Phase: Domain Points
  if(ph==="rest"){const L=(HOTSEAT||ADMIN?D.players:[me]).filter(p=>p&&(p.board.dp||0)>0);
    L.forEach(p=>{h+=dockCard("Domain Point — "+esc(p.name),'<div class="tb-row" style="flex-wrap:wrap">'+dpButtons(p,D.players.indexOf(p))+'</div>',"now");});}
  // 11. Loans
  h+=loansHTML(qp);
  return h||dockCard("Nothing to do",'<div class="note">Waiting on other players.</div>');}
// the Envoy queue: every Envoy of this phase in resolution order; resolved ones show their result (expand for the votes),
// the current one is highlighted, upcoming ones carry your pre-vote (applied when its turn comes, hidden until then)
function envoyQueueHTML(R,qp,ph){const plan=R.plan.length?R.plan:tPlan(ph,R.ord,R.councilDom),pool=R.pool[qp.id]??inflPool(qp),room=Math.max(0,pool-(R.spent[qp.id]||0));
  if(!plan.length)return dockCard("Envoys",'<div class="note">'+(R.waiting==="declare"?"Envoys appear once everyone has declared.":R.waiting==="tie"?"Waiting for the Council tie-break.":"No Envoys this phase.")+'</div>');
  let planned=0;const done=new Map(R.envoys.map(E=>[E.id,E]));
  const rows=plan.map((E0,i)=>{const E=done.get(E0.id)||E0,cur=R.curEnvoy&&R.curEnvoy.id===E.id,mineE=sameP(E.owner,qp);
    let st="",pv="";
    if(E.done){const pe=performEval(E);st='net '+E.net+' <b class="'+tOutCls(pe?pe.out:E.out)+'">'+(pe?pe.out:E.out)+'</b>'+(pe&&pe.rec&&pe.rec.action?' · '+esc(pe.rec.action):'')+(E.saved?' <span class="tb-b">'+esc(E.saved)+'</span>':'');}
    else if(cur)st='<b>voting</b> <span class="tbcd"></span>';
    if(!E.done&&!E.council&&!mineE&&!R.resolved.has(E.id+">"+qp.id)&&!(R.cur&&R.cur.key===E.id+">"+qp.id)){
      const v=tCur(qp).votes[E.id],a=v?v.a:"",x=v&&(a==="S"||a==="O")?(+v.x||1):0,capv=voteCap(qp,E.dom||"Prowess",E.council),blk=E.dom?opposeBlock(qp,E):"";planned+=x;
      const bt=(k,l,cl,dis)=>'<button data-do="pv" data-env="'+esc(E.id)+'" data-a="'+k+'" data-who="'+qp.id+'" class="'+(a===k?'on ':'')+cl+'"'+(dis?' disabled title="'+esc(dis)+'"':'')+'>'+l+'</button>';
      pv='<span class="pvb">'+bt("","—","")+bt("A","A","")+bt("S","S","pos")+bt("O","O","neg",blk)+'</span>'+
        ((a==="S"||a==="O")?' <button data-do="pvx" data-env="'+esc(E.id)+'" data-dv="-1" data-who="'+qp.id+'">−</button><b class="pvn">'+x+'</b><button data-do="pvx" data-env="'+esc(E.id)+'" data-dv="1" data-who="'+qp.id+'"'+(x>=capv?' disabled':'')+'>+</button><span class="note">/'+capv+'</span>':'');}
    const head='<span class="eq-n">'+(i+1)+'</span>'+tName(E.owner)+' <b>'+esc(E.dom||"Council")+'</b>'+(E.council?' <span class="note">(Council)</span>':'')+(E.mission?' <span class="note">(Mission)</span>':'');
    const detail=E.done?'<div class="note">'+innateTxt(E)+(E.votes.length?'; '+E.votes.map(v=>esc(v.who.name)+' '+tVoteTxt(v)).join(', '):'')+'</div><div class="note">'+kwify(outText(E.dom,E.out))+'</div>'+
      ((E.notes||[]).length?'<div>'+E.notes.map(x=>'<span class="tb-b nt">ⓘ '+esc(x)+'</span>').join(' ')+'</div>':''):"";
    return '<div class="eq'+(cur?' cur':'')+(E.done?' done':'')+(mineE?' mine':'')+'">'+(detail?'<details><summary>'+head+'<span class="eq-st">'+st+'</span></summary>'+detail+'</details>':'<div class="eq-r">'+head+'<span class="eq-st">'+st+'</span></div>')+
      (pv?'<div class="eq-pv">'+pv+'</div>':'')+'</div>';}).join("");
  return dockCard("Envoys"+' <span class="note">'+(planned>room?'<b class="neg">pre-votes '+planned+' / '+room+' Influence</b>':'pre-votes '+planned+' / '+room+' Influence')+'</span>',
    rows+'<label class="note"><input type="checkbox" data-do="autoab" data-who="'+qp.id+'"'+(PT(qp).auto?" checked":"")+'> Auto-abstain when nothing is set</label>',"eqcard");}
function inflCardHTML(qp){const c=tCur(qp),md=PT(qp).mods,afx=boardFx(qp);
  let b='<div class="tb-row"><span style="flex:1">Influence this turn</span><b>'+inflPool(qp)+'</b></div>'+
    '<div class="tb-row"><span style="flex:1" class="note">gain '+influenceTotal(qp.board)+' + adjust</span><button data-do="adj" data-k="inflAdj" data-dv="-1" data-who="'+qp.id+'">−</button><b>'+(+c.inflAdj||0)+'</b><button data-do="adj" data-k="inflAdj" data-dv="1" data-who="'+qp.id+'">+</button></div>'+
    '<div class="tb-row"><span style="flex:1">Personal Envoys</span><b>'+personalEnvoys(qp)+'</b></div>'+
    '<div class="tb-row"><span style="flex:1" class="note">Era + adjust</span><button data-do="adj" data-k="envAdj" data-dv="-1" data-who="'+qp.id+'">−</button><b>'+(+c.envAdj||0)+'</b><button data-do="adj" data-k="envAdj" data-dv="1" data-who="'+qp.id+'">+</button></div>'+
    '<details><summary class="note">Influence breakdown</summary>'+influenceRows(qp.board).filter(r=>r.val||r.cnt).map(r=>'<div class="tb-row"><span style="flex:1">'+kwify(r.k)+(r.cnt>1?' <span class="note">×'+r.cnt+'</span>':'')+'</span><b>'+(r.val>0?'+':'')+r.val+'</b></div>').join('')+'</details>'+
    '<details><summary class="note">From Holdings &amp; Infrastructure ('+afx.length+')</summary>'+(afx.length?afx.map(f=>'<div class="tb-row"><span style="flex:1">'+esc(fxLabel(f))+'</span><span class="note">'+esc(f.src)+(f.q>1?' ×'+f.q:'')+'</span></div>').join(""):'<div class="note">None active.</div>')+'</details>'+
    '<details><summary class="note">Manual modifiers ('+Object.keys(md).length+')</summary>'+Object.keys(md).map(k=>{const m=md[k];return '<div class="tb-row">'+
      '<input data-do="mod" data-mk="'+k+'" data-mf="label" data-who="'+qp.id+'" value="'+esc(m.label||"")+'" placeholder="source" style="flex:1;min-width:80px">'+
      '<select data-do="mod" data-mk="'+k+'" data-mf="kind" data-who="'+qp.id+'"><option value="envoy"'+(m.kind==="envoy"?" selected":"")+'>own Envoys</option><option value="cap"'+(m.kind==="cap"?" selected":"")+'>vote cap</option></select>'+
      '<select data-do="mod" data-mk="'+k+'" data-mf="scope" data-who="'+qp.id+'"><option value="all"'+(!m.scope||m.scope==="all"?" selected":"")+'>all Envoys</option><option value="council"'+(m.scope==="council"?" selected":"")+'>Council</option><option value="personal"'+(m.scope==="personal"?" selected":"")+'>Personal</option></select>'+
      '<select data-do="mod" data-mk="'+k+'" data-mf="dom" data-who="'+qp.id+'">'+["All"].concat(T_ALL).map(d=>'<option'+(m.dom===d?" selected":"")+'>'+d+'</option>').join("")+'</select>'+
      '<input data-do="mod" data-mk="'+k+'" data-mf="val" data-who="'+qp.id+'" type="number" value="'+(+m.val||0)+'" style="width:52px">'+
      '<button data-do="moddel" data-mk="'+k+'" data-who="'+qp.id+'">✕</button></div>';}).join("")+
    '<div class="tb-row"><button data-do="modadd" data-who="'+qp.id+'">+ modifier</button></div></details>';
  return dockCard("Influence &amp; Envoys — "+esc(qp.name),b);}
DO.cvote=el=>{if(isSpring()){flash("Spring — no Council Phase");return;}const c=tCurW(pOf(el));if(el.dataset.dom)c.council={dom:el.dataset.dom,ts:tnow()};else delete c.council;rlCommit();};
DO.tie=el=>{TB().councilTie={dom:el.dataset.dom,turn:tTurn(),ts:tnow()};rlCommit();};
DO.decl=el=>{const c=tCurW(pOf(el));c.decl=c.decl||{};c.decl.n=c.decl.n||{};const d=el.dataset.dom;c.decl.n[d]=Math.max(0,(+c.decl.n[d]||0)+(+el.dataset.dv));rlCommit();};
DO.declock=el=>{const c=tCurW(pOf(el));c.decl=c.decl||{n:{}};c.decl.lock=tnow();rlCommit();};
DO.declunlock=el=>{const c=tCurW(pOf(el));if(c.decl)delete c.decl.lock;rlCommit();};
DO.vote=el=>{const p=pOf(el),E=tSim().curEnvoy;if(!E)return;const x=el.dataset.a==="A"?0:+(document.getElementById("tbAmt")||{}).value||1;tCurW(p).votes[E.id]={a:el.dataset.a,x,ts:tnow()};
  if(x>0&&isSpring())flash("Spring — players don't spend Influence tokens");rlCommit();};   // SEASONS.Spring: flag, not a lock
DO.pv=el=>{const c=tCurW(pOf(el)),id=el.dataset.env,a=el.dataset.a,old=c.votes[id];if(!a)delete c.votes[id];else c.votes[id]={a,x:a==="A"?0:Math.max(1,+(old&&old.x)||1),ts:tnow()};rlCommit();};
DO.pvx=el=>{const p=pOf(el),c=tCurW(p),v=c.votes[el.dataset.env];if(!v||v.a==="A")return;
  const E2=tPlan(tPhase(),tOrder(),tSim().councilDom).find(x=>x.id===el.dataset.env),capv=E2?voteCap(p,E2.dom||"Prowess",E2.council):99;
  c.votes[el.dataset.env]={a:v.a,x:Math.max(1,Math.min(capv,(+v.x||1)+(+el.dataset.dv))),ts:tnow()};rlCommit();};
DO.autoab=el=>{PT(pOf(el)).auto=el.checked;rlCommit();};
DO.mission=el=>{const c=tCurW(pOf(el));c.mission=c.mission||{};if(el.dataset.dom)c.mission[el.dataset.src]=el.dataset.dom;else delete c.mission[el.dataset.src];rlCommit();};
DO.adj=el=>{const c=tCurW(pOf(el));c[el.dataset.k]=(+c[el.dataset.k]||0)+(+el.dataset.dv);rlCommit();};
DO.modadd=el=>{PT(pOf(el)).mods["m"+Date.now()]={label:"",kind:"envoy",scope:"all",dom:"All",val:1};rlCommit();};
DO.mod=el=>{const m=PT(pOf(el)).mods[el.dataset.mk];if(!m)return;m[el.dataset.mf]=el.dataset.mf==="val"?(+el.value||0):el.value;rlCommit();};
DO.moddel=el=>{delete PT(pOf(el)).mods[el.dataset.mk];rlCommit();};
DO.extort=()=>{const f=pById(document.getElementById("exFrom").value),to=pById(document.getElementById("exTo").value),amt=+document.getElementById("exAmt").value||0;
  if(!f||!to||sameP(f,to))return;const t=extortGold({b:f.board},{b:to.board},amt,"by hand");flash(to.name+" extorts "+t.toLocaleString()+" from "+f.name+(t<amt?" (all they had)":""));rlCommit();};
DO.exto=el=>{const p=pOf(el);if(!p)return;p.board.exTo=p.board.exTo||{};if(el.value)p.board.exTo[el.dataset.exto]=el.value;else delete p.board.exTo[el.dataset.exto];rlCommit();};
DO.battleopen=el=>{const o=bq().find(x=>x.id===el.dataset.q);if(o&&!bqLoad(o))return;D.view="battle";save();render();};
// Perform (stage 2): picker, Perform, accept a fail, edit, pending done, declined at the table (Diplomatic Mission)
DO.pf=el=>{const [id,k]=el.dataset.pf.split("|");if(D.players.some(p=>(tCur(p).perform||{})[id]?.whisperLock)){flash("Whispering Undercroft locked this declared action and target");return;}const d=PF[id]=PF[id]||{};d[k]=el.value;if(k==="action"){delete d.target;delete d.sub;}if(k==="target")delete d.sub;if(k!=="place")delete d.place;renderTable();};
DO.perf=el=>{const p=pOf(el),c=tCurW(p),id=el.dataset.env;c.perform=c.perform||{};
  const R0=tSim(),d=PF[id]||{},old=c.perform[id]||{},E=(R0.envoys||[]).find(x=>x.id===id),tg=old.lock?String(old.lock.target||""):old.edit&&old.target?old.target:(d.target||"");if(old.whisperLock&&(d.action!==old.action||tg!==String(old.target||"")||String(d.sub||"")!==String(old.sub||"")||String(d.place||"")!==String(old.place||""))){flash("Whispering Undercroft locked this declared action and target");return;}
  if(E&&!resolveOpen(R0,E)){flash("Resolve begins once the Tally Phase ends");return;}
  const blocked=E&&d.action?pfHardFlags(E,d.action,tg):[];
  if(blocked.length){flash("Action blocked: "+blocked.join("; "));return;}
  const ev=E&&d.action?comboEval(E,d.action,tg):null;
  if(ev&&!ev.ok){const L=old.lock||{target:tg,tried:[],out:ev.out,net:ev.adj};if(!L.tried.includes(d.action))L.tried.push(d.action);c.perform[id]={lock:L,ts:tnow()};delete PF[id];rlCommit();return;}
  c.perform[id]={action:d.action||"",target:tg,sub:d.sub||"",place:d.place||"",ts:tnow()};delete PF[id];rlCommit();};
DO.pffail=el=>{const c=tCurW(pOf(el));c.perform=c.perform||{};const L=(c.perform[el.dataset.env]||{}).lock||{};
  c.perform[el.dataset.env]={failAccept:1,target:L.target||"",failOut:L.out||"Failed",failNet:L.net,tried:L.tried||[],ts:tnow()};rlCommit();};
DO.pendone=el=>{const p=pOf(el);if(p){p.board.pending=(p.board.pending||[]).filter(x=>x.id!==el.dataset.env);rlCommit();}};
DO.perfedit=el=>{const c=tCurW(pOf(el));c.perform=c.perform||{};const r=c.perform[el.dataset.env]||{};if(r.whisperLock){flash("Whispering Undercroft locked this declared action and target");return;}c.perform[el.dataset.env]=Object.assign({},r,{edit:1});rlCommit();};
DO.declined=el=>{const c=tCurW(pOf(el));c.perform=c.perform||{};const r=c.perform[el.dataset.env]||{};if(r.whisperLock){flash("Whispering Undercroft requires the declared action if the Envoy passes");return;}
  if(r.declined)delete r.declined;else r.declined=tnow();c.perform[el.dataset.env]=r;rlCommit();};

// ---- drawers: Turn log · Edicts · Tools ----
function drawersHTML(R){
  const dr=(id,title,body,sub)=>{const op=rlOpen(id,id==="rlLog");return '<details class="rl-dr" id="'+id+'" data-keep="'+(id==="rlLog"?1:0)+'"'+(op?' open':'')+'><summary><b>'+title+'</b>'+(sub?' <span class="note">'+sub+'</span>':'')+'</summary><div class="rl-db">'+(op?body():'')+'</div></details>';};
  const bst=Math.max(0,...D.players.map(edictTotal));
  return dr("rlLog","Turn log",()=>turnLogHTML(R))+
    dr("rlEdicts","Edicts",()=>'<div id="viewRenown"></div>',bst?"most "+bst:"")+
    dr("rlTools","Tools",()=>'<div class="tb-tools">'+mapToolsHTML()+'</div>'+banditPanelHTML()+
      '<div class="tot">'+timerAddHTML()+'</div>'+activeTimersHTML()+(mods().diplomacy?'<div id="viewDash"></div>':''),"map · bandits · timers"+(mods().diplomacy?" · diplomacy":""));}
// Turn log: one list for the turn (Envoys, Empire Phase, timers, bandits, notices, edits, story), newest turn first; filter chips per device
let LOGF="all";try{LOGF=localStorage.getItem("renown_logf")||"all";}catch(e){}
DO.logf=el=>{LOGF=el.dataset.f;try{localStorage.setItem("renown_logf",LOGF);}catch(e){}renderTable();};
DO.chronmd=()=>{const md="# Chronicle\n\n"+(D.chron||[]).map(x=>"- **"+chronDate(x)+"** — "+x.txt).join("\n")+"\n",a=document.createElement("a");
  a.href=URL.createObjectURL(new Blob([md],{type:"text/markdown"}));a.download="chronicle.md";document.body.appendChild(a);a.click();a.remove();};
function turnLogItems(R){const T=tTurn(),H=TB().hist||{},out=[],me=meP(),idOf=name=>{const p=D.players.find(q=>q.name===name);return p?String(p.id):null;};
  const add=(t,type,who,html)=>out.push({t,type,who:who.filter(Boolean).map(String),html});
  // this phase: live Envoy lines (votes, outcome, action)
  const live=new Set();
  R.log.forEach(l=>{if(l.kind==="cvote"){add(T,"envoys",[l.who.id],tName(l.who)+' Council vote: '+(l.dom?'<b>'+l.dom+'</b>':'<span class="note">'+(l.timeout?"timeout":l.forced?"skipped":"none")+'</span>'));return;}
    const E=l.E,pe=performEval(E),ap=(tCur(E.owner).applied||{})[E.id];live.add(E.id);
    add(T,"envoys",[E.owner.id].concat(pe&&pe.tgt?[pe.tgt.id]:[]),tName(E.owner)+' <b>'+esc(E.dom)+'</b>'+(E.council?' (Council)':'')+(E.mission?' (Diplomatic Mission)':'')+' → net <b>'+E.net+'</b> <b class="'+tOutCls(pe?pe.out:E.out)+'">'+(pe?pe.out:E.out)+'</b>'+
      (pe&&pe.rec&&pe.rec.action?' · '+esc(pe.rec.action)+(pe.tgt?' → '+esc(pe.tgt.name):''):'')+(E.votes.length?'<div class="note">'+E.votes.map(v=>esc(v.who.name)+' '+tVoteTxt(v)).join(', ')+'</div>':'')+(ap?apLines(ap):''));});
  // earlier this turn and past turns: applied Envoys, Empire Phase, timers, bandits, notices, Domain Points
  const sumOf=t=>t===T?summaryLines(T):((H[t]||{}).sum||[]);
  const turns=[T].concat(Object.keys(H).map(Number).filter(k=>k<T).sort((a,b)=>b-a).slice(0,6));
  turns.forEach(t=>{
    D.players.forEach(p=>{const c=PT(p).cur;if(t===T&&c&&c.turn===T)Object.keys(c.applied||{}).forEach(id=>{if(live.has(id))return;const a=c.applied[id];
      add(t,"envoys",[p.id],esc(p.name)+' · '+esc(a.dom||"Council")+' · <b class="'+tOutCls(a.out)+'">'+esc(a.out)+'</b>'+(a.act?' · '+esc(a.act)+(a.sub?' ('+esc(a.sub)+')':''):'')+((a.fx||[]).length?'<div class="note">'+a.fx.map(kwify).join(' · ')+'</div>':''));});});
    sumOf(t).forEach(x=>{if(x.k==="Envoy"&&t===T)return;const ty=x.k==="Bandits"?"bandits":x.k==="Timers"||x.k==="Empire"?"timers":x.k==="Envoy"?"envoys":"notice";
      const who=D.players.filter(p=>String(x.t).includes(p.name)).map(p=>p.id);add(t,ty,who,'<span class="tb-b">'+esc(x.k)+'</span> '+kwify(x.t));});
    const h=H[t];if(h&&h.rows)h.rows.forEach(r=>add(t,"timers",[r.pid],pTok(pById(r.pid)||r,12)+'<b>'+esc(r.name)+'</b> end of turn: Gold '+(r.net<0?'':'+')+(+r.net||0).toLocaleString()+' · PO '+r.p0+' → '+r.p1+((r.done||[]).length?' · '+r.done.map(kwify).join(' · '):'')));});
  (D.chron||[]).filter(e=>turns.includes(e.t)).forEach(e=>add(e.t,"story",[],'<span class="tb-b">'+esc(chronDate(e))+'</span> '+esc(e.txt)));
  D.players.forEach(p=>(p.board.act||[]).filter(e=>turns.includes(e.turn)).forEach(e=>add(e.turn,"edits",[p.id],'<span class="note">'+new Date(e.ts).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})+' · '+esc(p.name)+(e.by?' (by '+esc(e.by)+')':'')+'</span> '+e.lines.map(kwify).join(' · '))));
  return out;}
function turnLogHTML(R){const F=[["all","All"],["mine","Mine"],["envoys","Envoys"],["bandits","Bandits"],["timers","Timers"],["story","Story"]],me=meP(),f=F.some(x=>x[0]===LOGF)?LOGF:"all";
  const keep=x=>f==="all"?true:f==="mine"?!!me&&x.who.includes(String(me.id)):x.type===f;
  const L=turnLogItems(R).filter(keep),by={};L.forEach(x=>{(by[x.t]=by[x.t]||[]).push(x);});
  const ks=Object.keys(by).map(Number).sort((a,b)=>b-a);
  return '<div class="lgf">'+F.map(([k,l])=>'<button data-do="logf" data-f="'+k+'" data-nav="1"'+(k===f?' class="on"':'')+'>'+l+'</button>').join("")+
      ((D.chron||[]).length?'<button data-do="chronmd" data-nav="1" style="margin-left:auto">chronicle .md</button>':'')+'</div>'+
    (f==="timers"||f==="all"?realmTimersBrief():'')+
    (ks.length?ks.map((t,i)=>{const body=by[t].map(x=>'<div class="tb-lg lg-'+x.type+'">'+x.html+'</div>').join("");
      return i===0?'<div class="lg-turn"><div class="lg-th">Turn '+t+(t===tTurn()?' · '+esc(curSeason()):'')+'</div>'+body+'</div>':'<details class="lg-turn"><summary class="lg-th">Turn '+t+' <span class="note">'+by[t].length+'</span></summary>'+body+'</details>';}).join(""):'<div class="note">Nothing yet.</div>');}
function realmTimersBrief(){const T=realmTimers();if(!T.length)return "";
  return '<div class="lg-tm">'+T.map(t=>'<span class="tb-b">'+esc(t.type)+' '+t.n+'</span> '+esc(t.label||"")).join('<br>')+'</div>';}
DO.maptog=()=>{RL_MAP=!RL_MAP;try{localStorage.setItem("renown_rl_map",RL_MAP?"1":"0");}catch(e){}renderTable();};
