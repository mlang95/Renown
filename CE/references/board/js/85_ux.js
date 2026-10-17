// ===================== CHROME: Inbox · HUD drill-down · read-only badge · phone phase pill · setup stepper =====================

// ---- Inbox: everything asking for attention on the active board, in one list (top bar ⚑). Resolve or ignore each.
//   flags      rule flags on the board (ignore = until the flag's text changes, or it clears and comes back)
//   prompts    this turn's notices to the player (Toll House, Beacon Towers, Courier Network next turn, loans, …)
//   pending    actions performed but not yet placed on the board
//   once-per   limited effects usable in the current phase and not used yet
//   notices    this device's recent messages
let IBX_OPEN=false;
function inboxItems(){const p=D.players[D.active];if(!p)return [];const out=[],ph=tPhase();
  // flags (same keys as the old board flag box, so earlier ignores carry over)
  const fl=boardFlags(),fkey=x=>"b:"+x.replace(/\d+/g,"#");S.ign=S.ign||{};const live=new Set(fl.map(fkey));
  Object.keys(S.ign).filter(k=>k.startsWith("b:")&&!live.has(k)).forEach(k=>{delete S.ign[k];IGN_DIRTY=true;});
  Object.keys(S.ign).filter(k=>k.startsWith("b:")&&Array.isArray(S.ign[k])).forEach(k=>{const l=S.ign[k].filter(x=>fl.includes(x));if(l.length!==S.ign[k].length){IGN_DIRTY=true;if(l.length)S.ign[k]=l;else delete S.ign[k];}});
  let ign=0;fl.forEach(x=>{if(flagState(fkey(x),true,x)!=="on"){ign++;return;}const rl=FLAG_RULE.find(([re])=>re.test(x));
    out.push({kind:"flag",txt:x,go:rl?"reference#"+rslug(rl[1]):"board:board",ign:fkey(x),sig:x});});
  const c=tCur(p);(c.notes||[]).forEach((x,i)=>{if(!(c.notesDone||{})[i])out.push({kind:"prompt",txt:x,res:"note",i});});
  pendingOf(p.board).forEach(x=>out.push({kind:"pending",txt:x.act+": "+x.msg,res:"pend",id:x.id}));
  onceEffects(p).filter(e=>onceWindowNow(e,ph)&&!(+onceState(p,e.game)[e.key])&&!(onceState(p,false)["skip|"+e.key])).forEach(e=>
    out.push({kind:"once",txt:e.n+": "+e.c,res:"once",key:e.key,game:e.game,x:!!e.x}));
  if(ph==="rest"&&(p.board.dp||0)>0)out.push({kind:"prompt",txt:p.board.dp+" Domain Point"+(p.board.dp>1?"s":"")+" to spend",go:"table"});
  out.ign=ign+IGN_N;return out;}
function renderInbox(){const btn=document.getElementById("inboxBtn"),box=document.getElementById("inbox");if(!btn||!box)return;
  const L=inboxItems(),n=L.length;document.getElementById("inboxN").textContent=n;btn.classList.toggle("hot",L.some(x=>x.kind!=="once"));btn.classList.toggle("on",IBX_OPEN);
  if(IGN_DIRTY){IGN_DIRTY=false;setTimeout(save,0);}
  box.hidden=!IBX_OPEN;if(!IBX_OPEN)return;
  const p=D.players[D.active],lab={flag:"Flag",prompt:"Prompt",pending:"Pending",once:"Once per"};
  const row=x=>'<div class="ib-row ib-'+x.kind+'"><span class="tb-b">'+lab[x.kind]+'</span><span class="ib-t">'+kwify(x.txt)+'</span><span class="ib-a">'+
    (x.go?'<a href="#" data-goto="'+x.go+'" data-nav="1">go ▸</a>':'')+
    (x.res==="once"&&!x.x?'<button data-do="ibonce" data-k="'+esc(x.key)+'" data-game="'+(x.game?1:0)+'">used</button>':'')+
    (x.res==="note"?'<button data-do="ibnote" data-i="'+x.i+'" data-nav="1">done</button>':'')+
    (x.res==="pend"?'<button data-do="ibpend" data-env="'+esc(x.id)+'">done</button>':'')+
    (x.ign?'<button data-do="ibign" data-k="'+esc(x.ign)+'" data-sig="'+esc(x.sig)+'" data-nav="1">ignore</button>':'')+
    (x.res==="once"?'<button data-do="ibskip" data-k="'+esc(x.key)+'" data-nav="1" title="hide until next turn">ignore</button>':'')+'</span></div>';
  box.innerHTML='<div class="ib-h"><b>Inbox — '+esc(p?p.name:"")+'</b><span class="note">'+n+' item'+(n===1?'':'s')+'</span>'+
      (L.ign?'<a href="#" data-do="ibshow" data-nav="1">'+L.ign+' ignored · show</a>':'')+'<button data-do="ibclose" data-nav="1" class="tb-mini">✕</button></div>'+
    (n?L.map(row).join(""):'<div class="note">Nothing needs you.</div>')+
    (FLASHLOG.length?'<details class="ib-log"><summary class="note">Notices ('+FLASHLOG.length+')</summary>'+FLASHLOG.map(f=>'<div class="ib-row"><span class="note">'+new Date(f.ts).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})+'</span><span class="ib-t">'+esc(f.msg)+'</span></div>').join("")+'</details>':'');}
document.getElementById("inboxBtn").onclick=()=>{IBX_OPEN=!IBX_OPEN;renderInbox();};
// "inside" is read from the event path (taken at dispatch), since a handler may have re-rendered the clicked element away
function evIn(e,ids){return e.composedPath().some(n=>n&&n.id&&ids.includes(n.id));}
document.addEventListener("click",e=>{if(IBX_OPEN&&!evIn(e,["inbox","inboxBtn"])){IBX_OPEN=false;renderInbox();}});
DO.ibclose=()=>{IBX_OPEN=false;renderInbox();};
DO.ibshow=()=>{S.ign={};save();render();};
DO.ibign=el=>{S.ign=S.ign||{};const v=S.ign[el.dataset.k],L=Array.isArray(v)?v:(v!=null?[v]:[]);if(!L.includes(el.dataset.sig))L.push(el.dataset.sig);S.ign[el.dataset.k]=L;save();render();};
DO.ibnote=el=>{const c=tCurW(D.players[D.active]);c.notesDone=c.notesDone||{};c.notesDone[el.dataset.i]=1;save();render();};
DO.ibpend=el=>{const p=D.players[D.active];p.board.pending=(p.board.pending||[]).filter(x=>x.id!==el.dataset.env);save();render();};
DO.ibonce=el=>{onceUse(D.players[D.active],el.dataset.k,el.dataset.game==="1",true);save();render();};
DO.ibskip=el=>{onceState(D.players[D.active],false)["skip|"+el.dataset.k]=1;save();render();};

// ---- HUD drill-down: click a HUD cell → its breakdown in a popover. The Ledger's Gold, Craft / Influence / Extort,
// Settlements and Effects sections live here now (moved in from #hudStore while open, so their renderers keep working).
let HPOP=null;
const HPOP_NODES={craft:["lsYield","lsFx"],setts:["lsSett"]};
function hudPopBack(){const st=document.getElementById("hudStore"),pop=document.getElementById("hudPop");if(!st||!pop)return;
  pop.querySelectorAll(":scope > .hp-body > .lsec, :scope > .hp-body > #inflBox").forEach(n=>st.appendChild(n));}
function hudPopFill(){const pop=document.getElementById("hudPop");if(!pop||!HPOP)return;hudPopBack();const p=D.players[D.active];if(!p)return;
  try{computeAll();renderSettlements();renderInfluence();}catch(e){console.warn("hud pop",e);}
  const h=hudData(p),k=HPOP,T={gold:"Gold",infl:"Influence",env:"Envoys",po:"Public Order",craft:"Craft · Influence · Extort",dom:"Domains",armies:"Armies",setts:"Settlements",edicts:"Edicts"};
  let body="";
  if(k==="gold")body=goldBreakHTML(goldBreak(p.board));
  else if(k==="infl")body=influenceRows(p.board).filter(r=>r.val||r.cnt).map(r=>'<div class="hp-r"><span>'+kwify(r.k)+(r.cnt>1?' <span class="note">×'+r.cnt+'</span>':'')+'</span><b>'+(r.val>0?'+':'')+r.val+'</b></div>').join("")+
    '<div class="hp-r tot"><span>Influence this turn</span><b>'+inflPool(p)+'</b></div>'+(isSpring()?'<div class="note">Spring: no Influence gained</div>':'');
  else if(k==="env"){const e=eraRec(),c=tCur(p),nx=PT(p).envNext;body='<div class="hp-r"><span>'+esc(currentEra())+' (Era)</span><b>'+(+e.personal_envoys||1)+'</b></div>'+
    (+c.envAdj?'<div class="hp-r"><span>adjust</span><b>'+(+c.envAdj>0?'+':'')+c.envAdj+'</b></div>':'')+(nx&&nx.turn===tTurn()?'<div class="hp-r"><span>'+esc(nx.src||"next turn")+'</span><b>'+nx.n+'</b></div>':'')+
    '<div class="hp-r tot"><span>Personal Envoys</span><b>'+personalEnvoys(p)+'</b></div><div class="note">'+esc(e.envoys||"")+'</div>';}
  else if(k==="po")body='<div class="hp-r"><span>Public Order</span><b>'+(h.po>0?'+':'')+h.po+' · '+esc(h.band)+'</b></div>'+
    '<div class="hp-r"><span>Pieces</span><b>Faith +'+h.pieceF+' / Doubt +'+h.pieceD+'</b></div>'+
    h.fRows.map(r=>'<div class="hp-r"><span>'+kwify(r.k)+'</span><b class="pos">Faith +'+r.n+'</b></div>').join("")+
    h.dRows.map(r=>'<div class="hp-r"><span>'+kwify(r.k)+'</span><b class="neg">Doubt +'+r.n+'</b></div>').join("")+
    '<div class="hp-r tot"><span>At the next Empire Phase'+(h.dbl>1?' (modifiers ×2)':'')+'</span><b>Faith +'+h.faith+' / Doubt +'+h.doubt+'</b></div>';
  else if(k==="dom"){const dv=p.board.domains||{};body=DOMAINS.map(d=>'<div class="hp-r"><span>'+d+'</span><b>'+(+dv[d]||0)+' · '+domBand(+dv[d]||0)+'</b></div>').join("")+
    dbActive(p.board).map(x=>'<div class="hp-r"><span class="note">'+esc(x.tier+" "+x.dom)+'</span><span>'+kwify(x.text)+'</span></div>').join("");}
  else if(k==="armies")body=((p.board.armies||[]).map(a=>'<div class="hp-r"><span>'+esc(a.label||("Army "+a.id))+'</span><b>'+esc(a.retinue||"")+' ×'+(a.count||0)+(a.muster&&a.muster.n>0?' · Muster '+a.muster.t:'')+'</b></div>').join("")||'<div class="note">No Armies.</div>')+
    (h.armyCap!=null?'<div class="hp-r tot"><span>'+esc(currentEra())+' allows</span><b>'+h.armyCap+'</b></div>':'');
  else if(k==="edicts"){const bst=Math.max(0,...D.players.map(edictTotal));body=D.players.map(q=>'<div class="hp-r"><span>'+tName(q)+'</span><b>'+edictTotal(q)+(edictTotal(q)===bst&&bst?' ★':'')+'</b></div>').join("");}
  const go={gold:"board:summary",infl:"table",env:"table",po:"board:summary",craft:"board:summary",dom:"reference#refStanding",armies:"board:board",setts:"board:board",edicts:"table#rlEdicts"}[k];
  pop.innerHTML='<div class="hp-h"><b>'+T[k]+'</b> <span class="note">'+esc(p.name)+'</span>'+(go?' <a href="#" data-goto="'+go+'" data-nav="1">go ▸</a>':'')+'<button class="tb-mini" data-hpx="1" data-nav="1">✕</button></div><div class="hp-body">'+body+'</div>';
  const B=pop.querySelector(".hp-body");(HPOP_NODES[k]||[]).forEach(id=>{const n=document.getElementById(id);if(n){B.appendChild(n);if(n.tagName==="DETAILS")n.open=true;}});
  if(k==="infl"){}   // generated above
  const cell=document.querySelector('#hud [data-pop="'+k+'"]');if(cell){const r=cell.getBoundingClientRect();pop.style.left=Math.max(6,Math.min(r.left,window.innerWidth-pop.offsetWidth-6))+"px";pop.style.top=(r.bottom+4)+"px";}
  pop.hidden=false;}
function hudPop(k){if(HPOP===k){hudPopClose();return;}HPOP=k;hudPopFill();}
function hudPopClose(){hudPopBack();HPOP=null;const pop=document.getElementById("hudPop");if(pop)pop.hidden=true;}
document.addEventListener("click",e=>{const c=e.target.closest("#hud [data-pop]");if(c){e.preventDefault();hudPop(c.dataset.pop);return;}
  if(!HPOP)return;if(!evIn(e,["hudPop"])||e.target.closest("[data-hpx],[data-goto]"))hudPopClose();});
window.addEventListener("resize",()=>{if(HPOP)hudPopFill();});

// ---- read-only badge (spectator, someone else's board, spectating) · phone phase pill ----
function renderChrome(){const rb=document.getElementById("roBadge");
  if(rb){const sp=spectating(),lk=lockOn()&&!myClaimP(),lb=lockOn()&&D.view==="board"&&!mine(D.players[D.active]);
    rb.hidden=!(sp||lk||lb);rb.innerHTML=sp?'read-only · '+esc((D.players[D.active]||{}).name||"")+' <button data-do="unspectate" data-nav="1" class="tb-mini">back to yours</button>':lk?'spectator · read-only':lb?'read-only · '+esc((D.players[D.active]||{}).name||""):'';}
  const pill=document.getElementById("phPill");if(pill){const ph=tPhase(),hc=canHost(),nx=tNext(ph);
    pill.innerHTML='<b>'+esc(T_PHL[ph].replace(" Phase",""))+'</b> <span class="note">T'+tTurn()+' · '+esc(curSeason())+'</span>'+
      (hc?(ph==="rest"?'<button data-do="endturn">End turn</button>':'<button data-do="phase" data-ph="'+nx+'">'+esc(T_PHL[nx].replace(" Phase",""))+' ▸</button>'):'');}
  if(HPOP)hudPopFill();}
