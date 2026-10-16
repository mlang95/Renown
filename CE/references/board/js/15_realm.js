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
    return '<td class="num rt-d st'+i+'" title="'+esc(d+" "+v+" · "+st)+'">'+v+'</td>';}).join('');}
function realmTableHTML(R){const sm=seatMap(),n=tSeats(),me=meP(),hp=hostP(),sp=R.ord[0]||null,cw=R.cur?R.cur.who:null,ph=tPhase(),E=R.curEnvoy,EE=ERAS[currentEra()]||{};
  const bst=Math.max(0,...D.players.map(edictTotal)),sg=v=>(v>0?"+":v<0?"−":"")+Math.abs(v).toLocaleString(),sl=seatsLocked();
  let rows='';
  for(let i=0;i<n;i++){const p=sm[i];
    if(!p){rows+='<tr class="rt-empty"><td class="num">'+(i+1)+'</td><td colspan="14"><span class="note">empty seat</span> '+(sl||!me?'':'<button data-do="sit" data-i="'+i+'" class="tb-mini">sit here</button>')+'</td></tr>';continue;}
    const h=hudData(p),pool=R.pool[p.id]??inflPool(p),left=pool-(R.spent[p.id]||0),dv=p.board.domains||{};
    const dsum=DOMAINS.reduce((a,d)=>a+(+dv[d]||0),0),dmax=startDomTotal(p)+((D.renown||1)-1);
    let st='';
    if(ph==="envoy"&&TB().phaseTs){const dc=tCur(p).decl||{};
      if(R.waiting==="declare")st=dc.lock?'<span class="pos">declared ✓</span>':'<span class="note">declaring…</span>';
      else{const nn=dc.n||{};st=T_ALL.filter(d=>+nn[d]>0).map(d=>d.slice(0,3)+" ×"+nn[d]).join(" · ");}}
    if(ph==="council"&&TB().phaseTs&&!R.councilDom){const lv=R.log.find(l=>l.kind==="cvote"&&sameP(l.who,p));
      st=lv?(lv.dom?'voted <b>'+lv.dom+'</b>':'no vote'):sameP(p,cw)?'<b>voting…</b> <span class="tbcd"></span>':'';}
    if(E){if(sameP(E.owner,p))st='sending <b>'+esc(E.dom)+'</b>';
      else{const v=E.votes.find(q=>sameP(q.who,p));st=v?tVoteTxt(v):sameP(p,cw)?'<b>to act</b> <span class="tbcd"></span>':'<span class="note">…</span>';}}
    const cls=["rt-row"];if(sameP(p,cw))cls.push("act");if(sameP(p,me))cls.push("me");
    rows+='<tr class="'+cls.join(" ")+'" data-do="spectate" data-who="'+p.id+'" data-hov="'+p.id+'"><td class="num">'+(i+1)+'</td>'+
      '<td class="rt-p">'+heraldOf(p,16)+tName(p)+
        (sameP(p,hp)?' <span class="tb-b h" title="'+(isSpring()?'Host token — no Host in Spring':'Host')+'">'+(isSpring()?'Host token':'♔ Host')+'</span>':'')+
        (sameP(p,sp)?' <span class="tb-b s" title="Starting player">1st</span>':'')+(sameP(p,me)?' <span class="tb-b">you</span>':'')+
        ((!sl&&sameP(p,me))||ADMIN?' <button data-do="stand" data-who="'+p.id+'" class="tb-mini">stand</button>':'')+'</td>'+
      '<td class="num">'+fmtG(h.gold)+' <span class="'+(h.net<0?"neg":"pos")+'">'+sg(h.net)+'</span></td>'+
      '<td class="num">'+left+'<span class="note">/'+pool+'</span></td>'+
      '<td class="num">'+personalEnvoys(p)+'</td>'+
      '<td class="num" title="'+esc(h.band)+'">'+(h.po>0?"+":"")+h.po+'</td>'+
      '<td class="num">'+h.armies+(h.armyCap!=null?'<span class="note">/'+h.armyCap+'</span>':'')+'</td>'+
      '<td class="num">'+h.setts+(h.settCap!=null?'<span class="note">/'+h.settCap+'</span>':'')+'</td>'+
      '<td class="num"'+(h.edicts===bst&&bst>0?' style="color:var(--income);font-weight:700"':'')+'>'+h.edicts+(h.edicts===bst&&bst>0?' ★':'')+'</td>'+
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
document.addEventListener("mouseover",e=>{const tr=e.target.closest&&e.target.closest("#viewTable tr[data-hov]"),box=document.getElementById("rlHover");if(!box)return;
  if(!tr){if(!e.target.closest||!e.target.closest("#rlHover"))box.hidden=true;return;}
  const p=pById(tr.dataset.hov);if(!p){box.hidden=true;return;}
  if(box._p!==tr.dataset.hov){box.innerHTML=miniCardHTML(p);box._p=tr.dataset.hov;}
  const r=tr.getBoundingClientRect(),hr=document.getElementById("viewTable").querySelector(".rl").getBoundingClientRect();
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
  if(hc){const i=T_PH.indexOf(ph),nx=T_PH[(i+1)%T_PH.length],vt=ph==="council"||ph==="envoy";
    h+='<div class="rl-hostbar">'+(vt?'<button data-do="begin">'+(t.phaseTs?'Restart':'Begin')+' '+esc(T_PHL[ph].replace(" Phase",""))+'</button>':'')+
      (R.cur?'<button data-do="skip" title="current voter abstains">Skip current</button>':'')+
      '<button data-do="phase" data-ph="'+nx+'">'+esc(T_PHL[nx].replace(" Phase",""))+' ▸</button>'+
      (ph==="rest"?'<button data-do="endturn" class="on">End turn</button>':'')+'</div>'+
      '<details class="rl-hostset" id="rlHostSet" data-keep="0"'+(rlOpen("rlHostSet",false)?' open':'')+'><summary class="note">Host settings</summary>'+
      '<div class="tb-row"><span class="note" style="flex:1">Phase</span>'+T_PH.map(p2=>'<button data-do="phase" data-ph="'+p2+'"'+(p2===ph?' class="on"':'')+'>'+T_PHL[p2].replace(" Phase","")+'</button>').join("")+'</div>'+
      '<div class="tb-row"><span style="flex:1">Host</span><select data-do="host">'+seated().map(p=>'<option value="'+p.id+'"'+(sameP(p,hostP())?' selected':'')+'>'+esc(p.name)+'</option>').join("")+'</select></div>'+
      '<div class="tb-row"><span style="flex:1">Seats</span><input data-do="seats" type="number" min="'+seatFloor()+'" max="12" value="'+tSeats()+'" style="width:60px"></div>'+
      '<div class="tb-row"><span style="flex:1">Vote timer (s, 0 = off)</span><input data-do="timer" type="number" min="0" max="300" value="'+tTimer()+'" style="width:60px"></div>'+
      '<div class="tb-row"><label><input type="checkbox" data-do="boardend"'+(boardEndOn()?" checked":"")+'> End turn also runs every board\'s end turn (timers, net gold if auto-apply is on, Public Order, Endurance)</label></div>'+
      '<div class="tb-row"><label><input type="checkbox" data-do="autores"'+(autoRes()?" checked":"")+'> Auto-resolve actions (costs, Faith / Doubt, effects)</label></div>'+
      '<div class="tb-row"><button data-do="autoseat"'+(seatsLocked()?' disabled':'')+'>Auto-seat unseated players</button></div></details>';}
  {const pr=(DATA.phaseRules||{})[ph];if(pr)h+='<details class="tb-rules"><summary class="note">Rules — '+esc(T_PHL[ph])+'</summary><div class="note" style="text-align:left;margin-top:4px">'+mdLite(pr)+'</div></details>';}
  h+='<div class="rl-you note">You: '+(me?tName(me):'—')+(lockOn()?'':' · <label><input type="checkbox" data-do="hotseat"'+(HOTSEAT?" checked":"")+'> hot-seat (act for anyone)</label>')+'</div>';
  return h+'</div>';}
DO.begin=()=>tSetPhase(tPhase());
DO.phase=el=>tSetPhase(el.dataset.ph);
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
  if(vt)R.envoys.filter(E2=>(E2.out==="Passed"||E2.out==="Endorsed")&&canAct(E2.owner)&&(HOTSEAT||sameP(E2.owner,me))).forEach(E2=>{
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
  if(ph==="empire"){h+=dockCard("Empire Phase",empireChecklistHTML());h+=extortTargetsHTML(qp);
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
  // 11. once-per effects usable now, loans
  h+=onceHTML(qp,ph);h+=loansHTML(qp);
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
DO.cvote=el=>{const c=tCurW(pOf(el));if(el.dataset.dom)c.council={dom:el.dataset.dom,ts:tnow()};else delete c.council;rlCommit();};
DO.tie=el=>{TB().councilTie={dom:el.dataset.dom,turn:tTurn(),ts:tnow()};rlCommit();};
DO.decl=el=>{const c=tCurW(pOf(el));c.decl=c.decl||{};c.decl.n=c.decl.n||{};const d=el.dataset.dom;c.decl.n[d]=Math.max(0,(+c.decl.n[d]||0)+(+el.dataset.dv));rlCommit();};
DO.declock=el=>{const c=tCurW(pOf(el));c.decl=c.decl||{n:{}};c.decl.lock=tnow();rlCommit();};
DO.declunlock=el=>{const c=tCurW(pOf(el));if(c.decl)delete c.decl.lock;rlCommit();};
DO.vote=el=>{const p=pOf(el),E=tSim().curEnvoy;if(!E)return;const x=el.dataset.a==="A"?0:+(document.getElementById("tbAmt")||{}).value||1;tCurW(p).votes[E.id]={a:el.dataset.a,x,ts:tnow()};rlCommit();};
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
  if(!f||!to||sameP(f,to))return;const t=extortGold({b:f.board},{b:to.board},amt);flash(to.name+" extorts "+t.toLocaleString()+" from "+f.name+(t<amt?" (all they had)":""));rlCommit();};
DO.exto=el=>{const p=pOf(el);if(!p)return;p.board.exTo=p.board.exTo||{};if(el.value)p.board.exTo[el.dataset.exto]=el.value;else delete p.board.exTo[el.dataset.exto];rlCommit();};
DO.battleopen=el=>{const o=bq().find(x=>x.id===el.dataset.q);if(o&&!bqLoad(o))return;D.view="battle";save();render();};
// Perform (stage 2): picker, Perform, accept a fail, edit, pending done, declined at the table (Diplomatic Mission)
DO.pf=el=>{const [id,k]=el.dataset.pf.split("|");const d=PF[id]=PF[id]||{};d[k]=el.value;if(k==="action"){delete d.target;delete d.sub;}if(k==="target")delete d.sub;renderTable();};
DO.perf=el=>{const p=pOf(el),c=tCurW(p),id=el.dataset.env;c.perform=c.perform||{};
  const d=PF[id]||{},old=c.perform[id]||{},E=(tSim().envoys||[]).find(x=>x.id===id),tg=old.lock?String(old.lock.target||""):old.edit&&old.target?old.target:(d.target||"");
  const ev=E&&d.action?comboEval(E,d.action,tg):null;
  if(ev&&!ev.ok){const L=old.lock||{target:tg,tried:[],out:ev.out,net:ev.adj};if(!L.tried.includes(d.action))L.tried.push(d.action);c.perform[id]={lock:L,ts:tnow()};delete PF[id];rlCommit();return;}
  c.perform[id]={action:d.action||"",target:tg,sub:d.sub||"",ts:tnow()};delete PF[id];rlCommit();};
DO.pffail=el=>{const c=tCurW(pOf(el));c.perform=c.perform||{};const L=(c.perform[el.dataset.env]||{}).lock||{};
  c.perform[el.dataset.env]={failAccept:1,target:L.target||"",failOut:L.out||"Failed",failNet:L.net,tried:L.tried||[],ts:tnow()};rlCommit();};
DO.pendone=el=>{const p=pOf(el);if(p){p.board.pending=(p.board.pending||[]).filter(x=>x.id!==el.dataset.env);rlCommit();}};
DO.perfedit=el=>{const c=tCurW(pOf(el));c.perform=c.perform||{};const r=c.perform[el.dataset.env]||{};c.perform[el.dataset.env]=Object.assign({},r,{edit:1});rlCommit();};
DO.declined=el=>{const c=tCurW(pOf(el));c.perform=c.perform||{};const r=c.perform[el.dataset.env]||{};
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
    const h=H[t];if(h&&h.rows)h.rows.forEach(r=>add(t,"timers",[r.pid],'<span class="pdot" style="background:'+r.color+'"></span><b>'+esc(r.name)+'</b> end of turn: Gold '+(r.net<0?'':'+')+(+r.net||0).toLocaleString()+' · PO '+r.p0+' → '+r.p1+((r.done||[]).length?' · '+r.done.map(kwify).join(' · '):'')));});
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
