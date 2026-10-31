// ===================== WELCOME: seats + profile (server games) =====================
// Seats: every player as a card; take an open seat (a claim, first claim wins) or watch. Opens on entering a
// server game when this device holds no claim. Profile: name, colour, culture (the playstyle reference:
// archetype, radar, Monuments, Wonders, actions) and a final-cut Heritage. Culture stays a view filter.
const MSUM=DATA.monSummary||{},WSUM=DATA.wonSummary||{},CSUM=(DATA.placeNames||{}).summaries||{};   // CSUM: lore profile_summary per culture
const RADAR_AX=[["military_solutions","Military"],["economy_generators","Economy"],["faith_management","Faith"],["doubt_warfare","Disruption"],
  ["political_control","Influence"],["board_presence","Board"],["degenerate_punishment","Punish"]];   // playstyle_reference.py AXES
const CUL_TYPES=[["pure","Pure"],["pair","Pair"],["triple","Triple"],["centre","Centre"]];
const WEL={view:null,pid:null,cul:"",game:null};
let WATCH=false;try{WATCH=sessionStorage.getItem(gkey("renown_watch"))==="1";}catch(e){}
function welcomeOn(){try{return !!SYNC.ready;}catch(e){return false;}}
async function welcomeOpen(){if(!welcomeOn())return;
  if(GAME_ID&&!WEL.game){WEL.game=await apiFetch("GET","/api/game");if(WEL.game&&WEL.game.name)document.title=WEL.game.name+" · Renown";}
  welcomeLinks();if(myClaimP()||WATCH||HOTSEAT)return;WEL.view="seat";welcomeRender();}
function welcomeLinks(){const on=welcomeOn(),g=document.getElementById("gamesLink"),b=document.getElementById("profileBtn");
  if(g)g.hidden=!on;if(b){b.hidden=!on;b.textContent=myClaimP()?"Profile":"Seats";}}
function welcomeClose(){WEL.view=null;const el=document.getElementById("welcome");if(el)el.remove();
  const me=myClaimP();if(me){const i=D.players.indexOf(me);if(i>=0&&D.active!==i){D.active=i;SPECTATE=null;reindex();}}
  welcomeLinks();render();renderList();}
function welcomeProfile(p){WEL.view="profile";WEL.pid=p.id;WEL.cul=cultureOf(p.board)||"";
  const i=D.players.indexOf(p);if(i>=0&&D.active!==i){D.active=i;SPECTATE=null;reindex();}welcomeRender();}
// ---- pieces ----
function culHer(n,p,px){const a=n&&HER[n];if(a&&SPR&&SPR.S["her:"+a]){const k="her:"+a;
    return '<svg class="her" width="'+px+'" height="'+px+'" viewBox="0 0 '+herN(k)+' '+herN(k)+'" aria-hidden="true">'+herPaths(k,p.color)+'</svg>';}
  return n?'<span class="wl-noher" style="width:'+px+'px;height:'+px+'px"></span>':(heraldOf(p,px)||pTok(p,px));}
function domDots(ds){return '<span class="wl-doms">'+(ds||[]).map(d=>'<i style="background:'+DOMC[d]+'" title="'+esc(d)+'"></i>').join("")+'</span>';}
function radarSVG(r,col){const n=RADAR_AX.length,cx=110,cy=84,R=60,pt=(i,v)=>{const a=-Math.PI/2+i*2*Math.PI/n;return [cx+Math.cos(a)*R*v/5,cy+Math.sin(a)*R*v/5];},
    poly=f=>RADAR_AX.map((ax,i)=>pt(i,f(ax)).map(x=>x.toFixed(1)).join(",")).join(" ");
  let s='<svg class="wl-radar" viewBox="0 0 220 172" width="220" height="172" role="img" aria-label="playstyle radar">';
  for(let k=1;k<=5;k++)s+='<polygon points="'+poly(()=>k)+'" fill="none" stroke="var(--line2)" stroke-width="'+(k===5?1.2:.6)+'"/>';
  s+='<polygon points="'+poly(([k])=>+(r||{})[k]||0)+'" fill="'+col+'" fill-opacity=".32" stroke="'+col+'" stroke-width="2"/>';
  RADAR_AX.forEach(([k,l],i)=>{const [x,y]=pt(i,6.15),an=Math.abs(x-cx)<6?"middle":x<cx?"end":"start";
    s+='<text x="'+x.toFixed(1)+'" y="'+(y+3).toFixed(1)+'" text-anchor="'+an+'" font-size="10" fill="var(--dim)">'+l+' <tspan fill="var(--ink)">'+(+(r||{})[k]||0)+'</tspan></text>';});
  return s+'</svg>';}
function heritagesFor(n){const k=n?cultureFactions({culture:n}):null;return Object.keys(FAC).filter(f=>FAC[f].final&&(!k||k.has(f)));}
// ---- views ----
function seatCard(p){const cl=claimOf(p),me=mine(p),c=cultureOf(p.board),mc=myClaimP();
  const act=me?'<button class="wl-go" data-wl="profile" data-p="'+esc(p.id)+'">Profile</button><button data-wl="release" data-p="'+esc(p.id)+'">release</button>'
    :cl?(ADMIN?'<button data-wl="clear" data-p="'+esc(p.id)+'">clear claim</button>':'<span class="note">taken</span>')
    :mc?'<span class="note">open</span>':'<button class="wl-go" data-wl="take" data-p="'+esc(p.id)+'">Take seat</button>';
  return '<div class="wl-seat'+(me?" mine":cl?" taken":"")+'" style="--pc:'+esc(p.color)+'">'+
    '<div class="wl-her">'+(heraldOf(p,52)||pTok(p,40))+'</div><div class="wl-sn">'+esc(p.name)+'</div>'+
    '<div class="note">'+(c?esc(c)+' · '+esc(CUL[c].archetype||""):esc(CUL_SELF))+'</div>'+
    (p.board.faction?'<div class="note">'+esc(p.board.faction)+'</div>':'')+
    '<div class="wl-act">'+act+'</div></div>';}
function seatView(){const g=WEL.game||{},me=myClaimP(),add=!D.started&&D.players.length<7&&(ADMIN||canHost());
  return '<div class="wl-head"><h2>'+esc(g.name||"Renown")+'</h2><span class="note">'+(D.started?"Turn "+tTurn():"Setup")+'</span>'+
      '<a class="wl-games" href="/">Games</a><button class="close" data-wl="close" title="close">✕</button></div>'+
    '<div class="wl-seats">'+D.players.map(seatCard).join("")+(add?'<button class="wl-seat wl-add" data-wl="add">+ seat</button>':'')+'</div>'+
    '<div class="wl-foot">'+(me?'<button class="wl-go" data-wl="close">Enter</button>':'<button data-wl="watch">Watch</button>')+'</div>';}
function culDetail(n,p,ed){const b=p.board,chosen=(cultureOf(b)||"")===n,H=heritagesFor(n);
  const row=(nm,sum)=>'<div class="wl-row"><b>'+esc(nm)+'</b>'+(sum?'<span class="note">'+esc(sum)+'</span>':'')+'</div>';
  const her='<h4>Heritage</h4><div class="wl-hers">'+(H.length?H.map(f=>'<button class="wl-hr'+(b.faction===f&&chosen?" on":"")+'" data-wl="her" data-f="'+esc(f)+'"'+(ed?"":" disabled")+'>'+
      '<b>'+esc(f)+'</b>'+(FAC[f].summary?'<span class="wl-hs">'+esc(FAC[f].summary)+'</span>':'')+'</button>').join(""):'<span class="note">—</span>')+'</div>';
  const pick='<button class="wl-go" data-wl="choose"'+(ed&&!chosen?"":" disabled")+'>'+(chosen?"✓ "+esc(n||CUL_SELF):"Choose "+esc(n||CUL_SELF))+'</button>';
  if(!n)return '<div class="wl-dh">'+culHer("",p,44)+'<div><h3>'+esc(CUL_SELF)+'</h3></div>'+pick+'</div>'+her;
  const c=CUL[n],T=(CUL_TYPES.find(t=>t[0]===c.type)||[,c.type])[1];
  return '<div class="wl-dh">'+culHer(n,p,44)+'<div><h3>'+esc(n)+'</h3><span class="note">'+esc(T)+' · '+esc(c.archetype||"")+'</span> '+domDots(c.domains)+'</div>'+pick+'</div>'+
    (CSUM[n]?'<p class="wl-sum">'+esc(CSUM[n])+'</p>':'')+
    '<div class="wl-dgrid"><div>'+radarSVG(c.radar,DOMC[(c.domains||[])[0]]||"var(--ink)")+
      '<h4>Actions</h4><div class="wl-chips">'+(c.actions||[]).map(a=>'<span>'+esc(a)+'</span>').join("")+'</div></div>'+
    '<div><h4>Monuments</h4>'+(c.monuments||[]).map(m=>row(m,MSUM[m])).join("")+
      '<h4>Wonders</h4>'+(c.wonders||[]).map(w=>row(w,WSUM[w])).join("")+'</div></div>'+her;}
function profileView(){const p=pById(WEL.pid);if(!p)return seatView();const ed=canEdit(p),cur=WEL.cul;
  const card=n=>'<button class="wl-cul'+(n===cur?" on":"")+((cultureOf(p.board)||"")===n?" mine":"")+'" data-wl="cul" data-c="'+esc(n)+'">'+culHer(n,p,26)+
    '<span><b>'+esc(n||CUL_SELF)+'</b><span class="note">'+(n?esc(CUL[n].archetype||""):"")+'</span></span>'+(n?domDots(CUL[n].domains):"")+'</button>';
  const groups=CUL_TYPES.map(([t,l])=>{const L=Object.keys(CUL).filter(n=>CUL[n].type===t);return L.length?'<div class="wl-gl note">'+l+'</div>'+L.map(card).join(""):"";}).join("");
  return '<div class="wl-head"><button data-wl="seats" title="seats">←</button><span class="wl-her">'+pTok(p,28)+'</span>'+
      '<input id="wlName" class="keepval" value="'+esc(p.name)+'"'+(ed?"":" disabled")+' aria-label="name">'+
      '<button data-wl="gen"'+(ed?"":" disabled")+'>Generate</button><input id="wlCol" type="color" value="'+esc(p.color)+'"'+(ed?"":" disabled")+' aria-label="colour">'+
      '<span id="wlHerSlot"></span><button class="close" data-wl="close" title="close">✕</button></div>'+
    '<div class="wl-prof"><div class="wl-culs">'+card("")+groups+'</div><div class="wl-detail">'+culDetail(cur,p,ed)+'</div></div>'+
    '<div class="wl-foot"><button class="wl-go" data-wl="close">Done</button></div>';}
function welcomeRender(){if(!WEL.view)return;let el=document.getElementById("welcome");
  if(!el){el=document.createElement("div");el.id="welcome";el.className="modal wl";el.innerHTML='<div class="modalcard wlcard" role="dialog" aria-modal="true"></div>';
    document.body.appendChild(el);el.addEventListener("click",welcomeClick);
    el.addEventListener("keydown",e=>{if(e.key==="Escape")welcomeClose();});}
  const card=el.firstChild,sc=(card.querySelector(".wl-culs")||{}).scrollTop||0,dc=(card.querySelector(".wl-detail")||{}).scrollTop||0;
  card.innerHTML=WEL.view==="profile"?profileView():seatView();
  {const a=card.querySelector(".wl-culs"),d=card.querySelector(".wl-detail");if(a)a.scrollTop=sc;if(d)d.scrollTop=dc;}
  const p=WEL.view==="profile"&&pById(WEL.pid);if(!p)return;const ed=canEdit(p);
  const nm=card.querySelector("#wlName"),col=card.querySelector("#wlCol");
  if(nm){nm.oninput=()=>{p.name=nm.value;};nm.onchange=()=>{save();render();renderList();};}
  if(col)col.onchange=()=>{p.color=col.value;save();render();welcomeRender();};
  const slot=card.querySelector("#wlHerSlot");if(slot&&!cultureOf(p.board)&&HER_ALL.length)slot.appendChild(herPicker(p,ed));}
function welcomeClick(e){if(e.target.id==="welcome"){if(WEL.view==="profile"||myClaimP())welcomeClose();return;}
  const t=e.target.closest("[data-wl]");if(!t||t.disabled)return;const k=t.dataset.wl,p=t.dataset.p!=null?pById(t.dataset.p):pById(WEL.pid);
  if(k==="close")return welcomeClose();
  if(k==="seats"){WEL.view="seat";return welcomeRender();}
  if(k==="watch"){WATCH=true;try{sessionStorage.setItem(gkey("renown_watch"),"1");}catch(_){}return welcomeClose();}
  if(k==="take"&&p&&!claimOf(p)&&!myClaimP()){p.board.claim={dev:DEV,ts:Date.now()};WATCH=false;
    {const x=PT(p),m=seatMap(),n=tSeats();if(!(Number.isInteger(x.seat)&&m[x.seat]===p))for(let i=0;i<n;i++)if(!m[i]){x.seat=i;x.seatTs=tnow();break;}}   // and sit at the Tabletry{sessionStorage.removeItem(gkey("renown_watch"));}catch(_){}
    save();render();flash("you are "+p.name);return welcomeProfile(p);}
  if(k==="profile"&&p)return welcomeProfile(p);
  if((k==="release"&&p&&mine(p))||(k==="clear"&&p&&ADMIN)){if(!confirm((k==="release"?"Release ":"Clear the claim on ")+p.name+"?"))return;
    delete p.board.claim;if(TB().ready)delete TB().ready[p.id];save();render();return welcomeRender();}
  if(k==="add"){const np=newPlayer(D.players.length+1);np.id=Math.max(Date.now(),1+Math.max(0,...D.players.map(q=>+q.id||0)));D.players.push(np);
    (np.board.settlements||[]).forEach(s=>nameSett(np,s));reindex();save();render();renderList();return welcomeRender();}
  if(k==="cul"){WEL.cul=t.dataset.c||"";return welcomeRender();}
  if(!p||!canEdit(p))return;
  if(k==="gen"){const n=genPlaceName(nameCulture(p.board));if(n){p.name=n;save();render();renderList();welcomeRender();}return;}
  if(k==="choose"||k==="her"){const n=WEL.cul,was=cultureOf(p.board)||"";p.board.culture=n;
    if(k==="her")setFaction(t.dataset.f);
    else if(n!==was&&p.board.faction&&!heritagesFor(n).includes(p.board.faction))setFaction("");
    save();render();renderList();welcomeRender();}}
document.getElementById("profileBtn").onclick=()=>{const me=myClaimP();if(me)welcomeProfile(me);else{WEL.view="seat";welcomeRender();}};
setInterval(()=>{welcomeLinks();if(WEL.view==="seat")welcomeRender();},POLL_MS);
