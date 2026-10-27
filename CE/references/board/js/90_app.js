// ===================== UNDO / REDO =====================
// Snapshots everything except Table data (votes are timestamped; undoing them would rewrite the sequence)
// and view-local keys. Online with several players (not hot-seat): undo restores only YOUR board.
const UNDO={past:[],future:[],last:null,t:null,mute:false,MAX:60};
function undoSnap(){return JSON.stringify(D,function(k,v){if(k==="tbl"||k==="act")return undefined;
  if(this===D&&(k==="view"||k==="active"))return undefined;return v;});}
function undoRecord(){if(UNDO.mute)return;let cur;try{cur=undoSnap();}catch(e){return;}
  if(UNDO.last===null){UNDO.last=cur;return;}
  if(cur===UNDO.last)return;
  if(!UNDO.t){UNDO.past.push(UNDO.last);if(UNDO.past.length>UNDO.MAX)UNDO.past.shift();UNDO.future=[];}
  clearTimeout(UNDO.t);UNDO.t=setTimeout(()=>{UNDO.t=null;},700);          // bursts (drag, typing) = one step
  UNDO.last=cur;undoButtons();}
function undoRebase(){try{UNDO.last=undoSnap();}catch(e){}}                // remote changes never become undo steps
function undoScoped(){return !!(typeof SYNC!=="undefined"&&SYNC.ready)&&!HOTSEAT&&D.players.length>1;}
function undoApply(sn){const o=JSON.parse(sn);UNDO.mute=true;
  try{
    if(undoScoped()){const me=meP(),src=(o.players||[]).find(p=>String(p.id)===String(me.id));
      if(src){const tb=me.board.tbl,ac=me.board.act;me.board=src.board;if(tb)me.board.tbl=tb;if(ac)me.board.act=ac;}}
    else{const tbls={},acts={};D.players.forEach(p=>{if(p.board&&p.board.tbl)tbls[p.id]=p.board.tbl;if(p.board&&p.board.act)acts[p.id]=p.board.act;});
      Object.keys(D).forEach(k=>{if(k!=="view"&&k!=="active"&&k!=="tbl"&&!(k in o))delete D[k];});
      Object.keys(o).forEach(k=>{D[k]=o[k];});
      D.players.forEach(p=>{if(tbls[p.id])p.board.tbl=tbls[p.id];if(acts[p.id])p.board.act=acts[p.id];});
      if(!(D.active<D.players.length))D.active=0;}
    reindex();render();renderList();
    const tr=document.getElementById("treasury");if(tr)tr.value=S.treasury;
    save();
  }finally{UNDO.last=undoSnap();UNDO.mute=false;undoButtons();}}
function doUndo(){if(!UNDO.past.length)return;ACT.undo="undo";clearTimeout(UNDO.t);UNDO.t=null;UNDO.future.push(undoSnap());undoApply(UNDO.past.pop());}
function doRedo(){if(!UNDO.future.length)return;ACT.undo="redo";clearTimeout(UNDO.t);UNDO.t=null;UNDO.past.push(undoSnap());undoApply(UNDO.future.pop());}
function undoButtons(){const u=document.getElementById("undoBtn"),r=document.getElementById("redoBtn");
  if(u){u.disabled=!UNDO.past.length;u.title="Undo (Ctrl+Z)"+(UNDO.past.length?" · "+UNDO.past.length+" step"+(UNDO.past.length>1?"s":""):"")+(undoScoped()?" · your board only":"");}
  if(r)r.disabled=!UNDO.future.length;}
document.getElementById("undoBtn").onclick=doUndo;document.getElementById("redoBtn").onclick=doRedo;
document.addEventListener("keydown",e=>{if(!(e.ctrlKey||e.metaKey))return;const k=(e.key||"").toLowerCase();if(k!=="z"&&k!=="y")return;
  const tg=e.target;if(tg&&(tg.isContentEditable||tg.tagName==="TEXTAREA"||
    (tg.tagName==="INPUT"&&!["checkbox","radio","button","color","range"].includes(tg.type))))return;   // native text undo
  e.preventDefault();if(k==="y"||e.shiftKey)doRedo();else doUndo();});

// ===================== ACTIVITY LOG =====================
// Each client diffs the boards it changed (≈1 s after the last edit) and appends a summary to that
// board's own log (b.act, last 40), so it syncs like everything else. Remote edits are never re-logged here.
const ACT={base:null,t:null,saving:false,undo:false};
function actSnap(b){const o=Object.assign({},b);delete o.tbl;delete o.act;delete o.expanded;return JSON.stringify(o);}
function actRebase(){ACT.base={};D.players.forEach(p=>{ACT.base[p.id]=actSnap(p.board);});ACT.shared=JSON.stringify([D.renown,D.season]);}
// after a remote merge: re-baseline only boards the remote actually changed, so local edits still pending get logged
function actJoin(pre,preSh){if(!ACT.base){actRebase();return;}
  D.players.forEach(p=>{const post=actSnap(p.board);if(pre[p.id]!==post||ACT.base[p.id]===undefined)ACT.base[p.id]=post;});
  const sh=JSON.stringify([D.renown,D.season]);if(sh!==preSh)ACT.shared=sh;}
function actSchedule(){if(!ACT.base){actRebase();return;}clearTimeout(ACT.t);ACT.t=setTimeout(actFlush,1200);}
function fmtG(v){return (+v||0).toLocaleString();}
function boardDiff(a,b){const L=[];
  const sN=(bd,id)=>{if(id==="faction")return "faction";const x=(bd.settlements||[]).find(s=>s.id===id);return x?(x.name||x.tier):"?";};
  const pa=new Map((a.placed||[]).map(x=>[x.id,x])),pb=new Map((b.placed||[]).map(x=>[x.id,x]));
  pb.forEach((x,id)=>{const o=pa.get(id);
    if(!o){L.push("placed "+x.name+" in "+sN(b,x.sid)+(x.bt>0?" (build "+x.bt+")":""));return;}
    if(o.sid!==x.sid||o.ward!==x.ward)L.push("moved "+x.name+" → "+sN(b,x.sid));
    if((o.bt||0)!==(x.bt||0))L.push(x.bt>0?x.name+" build timer "+(o.bt||0)+" → "+x.bt:x.name+" built");
    if((o.dmg||0)!==(x.dmg||0))L.push(x.dmg>0?x.name+" damaged ("+x.dmg+")":x.name+" repaired");});
  pa.forEach((x,id)=>{if(!pb.has(id))L.push("removed "+x.name);});
  const sa=new Map((a.settlements||[]).map(x=>[x.id,x])),sb=new Map((b.settlements||[]).map(x=>[x.id,x]));
  sb.forEach((x,id)=>{const o=sa.get(id);if(!o){L.push("new settlement: "+x.tier);return;}
    if(o.tier!==x.tier)L.push((x.name||o.tier)+" "+o.tier+" → "+x.tier);
    if(!o.capital&&x.capital)L.push("capital moved to "+(x.name||x.tier));
    if((o.bt||0)!==(x.bt||0)&&!(x.bt>0))L.push((x.name||x.tier)+" finished");});
  sa.forEach((x,id)=>{if(!sb.has(id))L.push("lost settlement: "+(x.name||x.tier));});
  [["infra","Infrastructure"],["wonders","Wonder"]].forEach(([k,lab])=>{const A=a[k]||{},B_=b[k]||{};
    Object.keys(B_).filter(n=>!(n in A)).forEach(n=>L.push("built "+lab+": "+n));
    Object.keys(A).filter(n=>!(n in B_)).forEach(n=>L.push("removed "+lab+": "+n));});
  const aa=new Map((a.armies||[]).map(x=>[x.id,x])),ab=new Map((b.armies||[]).map(x=>[x.id,x]));
  const an=x=>(x.label||"Army "+x.id);
  ab.forEach((x,id)=>{const o=aa.get(id);if(!o){L.push("raised "+an(x)+": "+(x.count||0)+"× "+x.retinue);return;}
    if((o.count||0)!==(x.count||0))L.push(an(x)+" "+(o.count||0)+" → "+(x.count||0)+" "+x.retinue);
    ["retinue","weapon","ranged","armor","shield"].forEach(f=>{if(o[f]!==x[f])L.push(an(x)+" "+f+": "+o[f]+" → "+x[f]);});
    if(!o.strained&&x.strained)L.push(an(x)+" Strained");});
  aa.forEach((x,id)=>{if(!ab.has(id))L.push("disbanded "+an(x));});
  if((a.turn||0)!==(b.turn||0))L.push("ended turn "+(a.turn||0)+" → "+(b.turn||0));
  if((a.treasury||0)!==(b.treasury||0)){const d=(b.treasury||0)-(a.treasury||0);L.push("gold "+fmtG(a.treasury)+" → "+fmtG(b.treasury)+" ("+(d>0?"+":"")+fmtG(d)+")");}
  if((a.po||0)!==(b.po||0))L.push("Public Order "+(a.po||0)+" → "+(b.po||0));
  const da=a.domains||{},db=b.domains||{};new Set([...Object.keys(da),...Object.keys(db)]).forEach(d=>{if((da[d]||0)!==(db[d]||0))L.push(d+" "+(da[d]||0)+" → "+(db[d]||0));});
  if((a.faction||"")!==(b.faction||""))L.push("faction: "+(b.faction||"none"));
  const ea=a.edictLog||{},eb=b.edictLog||{};Object.keys(eb).forEach(k=>{const n0=(ea[k]||[]).length,n1=(eb[k]||[]).length;if(n1>n0)L.push("Edict progress: "+k+" ("+n1+")");});
  return L;}
function actFlush(){ACT.t=null;if(!ACT.base){actRebase();return;}let ch=false;const by=meP()?meP().name:"";
  const tag=ACT.undo?ACT.undo:"";ACT.undo=false;
  D.players.forEach(p=>{const cur=actSnap(p.board),prev=ACT.base[p.id];ACT.base[p.id]=cur;
    if(prev===undefined||prev===cur)return;
    const lines=boardDiff(JSON.parse(prev),JSON.parse(cur));if(!lines.length)return;
    const L=p.board.act=p.board.act||[];L.push({ts:Date.now(),turn:tTurn(),season:curSeason(),by:by!==p.name?by:"",tag,lines});
    if(L.length>40)L.splice(0,L.length-40);ch=true;});
  const sh=JSON.stringify([D.renown,D.season]);
  if(ACT.shared&&sh!==ACT.shared&&meP()){const [r0,s0]=JSON.parse(ACT.shared),lines=[];
    if(r0!==D.renown)lines.push("Renown "+r0+" → "+D.renown);if((s0||"")!==(D.season||""))lines.push("Season → "+curSeason());
    if(lines.length){const L=meP().board.act=meP().board.act||[];L.push({ts:Date.now(),turn:tTurn(),season:curSeason(),by:"",tag,lines});ch=true;}}
  ACT.shared=sh;
  if(ch){ACT.saving=true;try{save();}finally{ACT.saving=false;}if(D.view==="table"&&!editing())renderTable();}}
// activity entries are shown in the Realm's Turn log (filter: Mine / All)

// ===================== GAME: save · load · new =====================
const GAME_PREFIX="game: ";
function gameAllowed(){return !(typeof SYNC!=="undefined"&&SYNC.ready)||HOTSEAT||ADMIN||D.players.length<2||canHost();}
function gameData(){return JSON.parse(JSON.stringify(D,function(k,v){if(this===D&&(k==="view"||k==="active"))return undefined;return v;}));}
function refreshGames(list){const sel=document.getElementById("gameList");if(!sel)return;
  const g=(list||[]).filter(b=>String(b.name).startsWith(GAME_PREFIX));
  sel.innerHTML='<option value="">— saved games —</option>'+g.map(b=>'<option value="'+esc(b.name)+'">'+esc(b.name.slice(GAME_PREFIX.length))+' ('+(b.updated_at||"").slice(0,16).replace("T"," ")+')</option>').join("");}
function gameReplace(nd){const keepV=D.view,keepA=D.active;UNDO.mute=true;
  try{Object.keys(D).forEach(k=>delete D[k]);Object.assign(D,nd);D.view=keepV;D.active=Math.min(keepA||0,(D.players||[1]).length-1);
    normalizeD();nameAllSetts();reindex();render();renderList();const tr=document.getElementById("treasury");if(tr)tr.value=S.treasury;save();
  }finally{UNDO.past=[];UNDO.future=[];UNDO.last=undoSnap();UNDO.mute=false;undoButtons();actRebase();}}
// keepPicks (Start game): culture, heraldry, Rising and faction picked before Start carry onto the fresh board
function newGameState(keepPicks){const o=gameData();
  o.players=o.players.map(p=>{const b=newBoard(),ob=p.board||{},tb=ob.tbl||{};
    b.tbl={seat:tb.seat,seatTs:tb.seatTs,mods:tb.mods||{}};
    if(keepPicks)["culture","heraldry","ageRising"].forEach(k=>{if(ob[k])b[k]=ob[k];});
    b.domains=startDomsFor({board:b});
    if(keepPicks&&ob.faction){const pS=S;S=b;try{setFaction(ob.faction);}finally{S=pS;}}   // re-grants the faction's starting pieces
    if(ob.claim)b.claim=clone(ob.claim);                       // claims are identity, not game state
    return {id:p.id,name:p.name,color:p.color,board:b};});
  o.renown=1;delete o.season;delete o.diplo;delete o.battle;delete o.bqueue;delete o.rtimers;delete o.siege;delete o.yearsGone;delete o.started;delete o.bandit;delete o.chron;delete o.chronSnap;
  const t=o.tbl||{};o.tbl={seats:t.seats,timer:t.timer,auto:t.auto,boardEnd:t.boardEnd,host:t.host,hostSet:t.hostSet,skip:{}};
  return o;}
document.getElementById("gameSave").onclick=async()=>{const nm=(document.getElementById("gameName").value||"").trim()||("Turn "+tTurn()+" "+new Date().toLocaleDateString());
  if(API.online){const r=await apiFetch("PUT","/api/builds/"+encodeURIComponent(GAME_PREFIX+nm),{data:gameData()});flash(r?"saved game “"+nm+"”":"save failed");refreshBuilds();}
  else{const b=new Blob([JSON.stringify(gameData(),null,2)],{type:"application/json"}),a=document.createElement("a");
    a.href=URL.createObjectURL(b);a.download="renown_game_"+nm.replace(/[^A-Za-z0-9_-]+/g,"_")+".json";a.click();flash("no server — downloaded the game file");}};
document.getElementById("gameLoad").onclick=async()=>{const nm=document.getElementById("gameList").value;if(!nm)return;
  if(!gameAllowed()){flash("only the Host can load a game");return;}
  if(!confirm("Load “"+nm.slice(GAME_PREFIX.length)+"”? This replaces the current game for everyone."))return;
  const r=await apiFetch("GET","/api/builds/"+encodeURIComponent(nm));if(!r||!r.data){flash("load failed");return;}
  gameReplace(r.data);flash("loaded “"+nm.slice(GAME_PREFIX.length)+"”");};
document.getElementById("gameDel").onclick=async()=>{const nm=document.getElementById("gameList").value;if(!nm)return;
  if(!confirm("Delete saved game “"+nm.slice(GAME_PREFIX.length)+"”?"))return;
  await apiFetch("DELETE","/api/builds/"+encodeURIComponent(nm));refreshBuilds();};
// Start game (Duke): boards, Table, Renown, Season and map pieces reset; terrain, players, seats and claims kept;
// claims and Duke/Host locks take effect. Deploy (Setup step 5) then happens on the cleared map.
// ready check (before Start): every seated player must be claimed and ready; the Duke can start regardless
function isReady(p){return !!p&&!!claimOf(p)&&!!(TB().ready||{})[p.id];}
function readyCheck(){const seat=seated(),n=seat.filter(isReady).length;return {seat,n,all:seat.length>0&&n===seat.length};}
async function startGame(){if(!(ADMIN||canHost())){flash("Host or Duke only");return;}
  if(!ADMIN&&!readyCheck().all){flash("every seated player must claim and ready up");return;}
  if(!confirm("Start the game? Every board, the Table, Renown, Season and all map pieces are wiped (terrain, players, seats, claims, cultures and factions stay). Player restrictions turn on."))return;
  const o=newGameState(true);o.map=Object.assign({},o.map||{},{cells:{},outlaw:{},camps:{},markers:[]});o.started=true;
  gameReplace(o);flash("game started");}
document.getElementById("gameNew").onclick=async()=>{if(!gameAllowed()){flash("only the Host can start a new game");return;}
  if(!confirm("Start a new game? Players, seats, claims, map and settings are kept; every board, Renown, Season, diplomacy, battle and the Table reset, and the game returns to setup (restrictions off until Start game)."))return;
  if(confirm("Save the current game first?"))await document.getElementById("gameSave").onclick();
  gameReplace(newGameState());flash("new game started");};

// ===================== HOVER KEYWORDS =====================
// Glossary terms, Pursuits, Infrastructure and Wonders inside rules text become hoverable (tap on touch).
function gslug(s){return String(s).toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"");}
const GK_LIST=[],GK_BY={},GK_LC={};
(()=>{const add=(t,k,label)=>{const e=esc(label||t);if(!t||GK_BY[e]!=null)return;GK_BY[e]=GK_LIST.length;GK_LC[e.toLowerCase()]=GK_LIST.length;GK_LIST.push({t,k});};
  Object.keys(R).forEach(n=>add(n,"p"));Object.keys(WON||{}).forEach(n=>add(n,"w"));Object.keys(INFRA||{}).forEach(n=>add(n,"i"));
  Object.keys(GLOSS).filter(t=>/^[A-Z][A-Za-z' /-]{2,}$/.test(t)).forEach(t=>{
    const m=t.match(/^(.+?) X$/);                                   // "Extort X" → Extort, Extorts, Extorted…
    if(m){const b=m[1];[b,b+"s",b+"ed",b+"ing",b+"ion"].forEach(v=>add(t,"g",v));}else add(t,"g");
    if(/^[A-Z][a-z]+$/.test(t))[t+"s",t+"ed"].forEach(v=>add(t,"g",v));});
  if(SCORE!=="Influence"){if(GLOSS["Net Influence"])add("Net Influence","g","Net "+SCORE);   // score text → score entries
    if(GLOSS["Influence X"])add("Influence X","g",SCORE);}})();   // Recoup → Recoups, Recouped
const GK_RE=GK_LIST.length?new RegExp("(^|[^A-Za-z0-9])("+Object.keys(GK_BY).sort((a,b)=>b.length-a.length)
  .map(x=>x.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).join("|")+")(?![A-Za-z0-9])","gi"):null;
function kwify(text,self){const h=esc(dispScore(text==null?"":text));if(!GK_RE)return h;const seen=new Set();
  return h.replace(GK_RE,(m,pre,term)=>{
    // single words must match case exactly (so "cast" in prose isn't linked); multi-word terms match any case ("Cast armor")
    const idx=GK_BY[term]!=null?GK_BY[term]:(/\s/.test(term)?GK_LC[term.toLowerCase()]:undefined);
    if(idx==null)return m;const key=GK_LIST[idx].t;
    if(seen.has(key)||key===self)return m;seen.add(key);
    return pre+'<span class="gk" data-gk="'+idx+'">'+term+'</span>';});}
// Wiki links: the wiki's own copy (build_wiki flips WIKI_LOCAL) uses sibling pages and opens them in the wiki frame;
// anywhere else (server.py / a local file) they go to the hosted wiki in a new tab. --wiki-base overrides both.
const WIKI_LOCAL=/*__WIKI_LOCAL__*/false;
const WIKI_BASE=DATA.wikiBase||(WIKI_LOCAL?"":(DATA.wikiHome||""));
function wikiA(href){return '<div><a href="'+esc(WIKI_BASE+href)+'" target="'+(WIKI_LOCAL&&window.top!==window?"_top":"_blank")+'" rel="noopener">wiki ↗</a></div>';}
function gkHtml(e){
  if(e.k==="g"){return '<div class="gh">'+esc(e.t)+'</div><div>'+esc(GLOSS[e.t]||"")+'</div>'+wikiA("glossary.html#"+gslug(e.t));}
  if(e.k==="p"){const r=R[e.t]||{};return '<div class="gh">'+esc(e.t)+' <span class="note">'+esc(r.monument&&r.group?r.group:(r.type||""))+(r.monument?" · Monument":"")+'</span></div>'+
    (r.unlock_raw&&!/^[-\u2014]$/.test(r.unlock_raw.trim())?'<div class="note">Unlock: '+esc(r.unlock_raw)+'</div>':'')+
    '<div><b>Innate</b> '+esc(r.innate_raw||"—")+'</div>'+
    (r.mastery_raw?'<div><b>Mastery</b> '+esc(r.mastery_raw)+(r.mreq_raw?' <span class="note">(req: '+esc(r.mreq_raw)+')</span>':'')+'</div>':'')+
    (onBoard(e.t)?'<div class="note">✓ on your board</div>':'<div><button data-addp="'+esc(e.t)+'">+ add to board</button></div>')+
    wikiA("type-"+gslug(r.type||"other")+".html#"+gslug(e.t));}
  const r=(e.k==="w"?WON:INFRA)[e.t]||{};
  return '<div class="gh">'+esc(e.t)+' <span class="note">'+(e.k==="w"?"Wonder":esc(r.tier||"Infrastructure"))+'</span></div>'+
    (r.requirement?'<div class="note">Requires: '+esc(r.requirement)+'</div>':'')+
    '<div>'+esc(r.effect_raw||"")+'</div>'+(r.upkeep?'<div class="note">Upkeep '+esc(r.upkeep)+'</div>':'')+
    wikiA("infrastructure-ref.html#"+gslug(e.t))+
    (((e.k==="w"?S.wonders:S.infra)||{})[e.t]?'<div class="note">✓ in your '+(e.k==="w"?'Wonders':'Infrastructure')+'</div>'
      :'<div><button data-addi="'+(e.k==="w"?"wonder":"infra")+'|'+esc(e.t)+'">+ add to '+(e.k==="w"?'Wonders':'Infrastructure')+'</button></div>');}
const GKT=document.createElement("div");GKT.id="gkTip";document.body.appendChild(GKT);
// Deep link from the wiki: settlement_board.html#h=<Holding | Infrastructure | Wonder | glossary term> opens its card.
function openFromHash(){const m=(location.hash||"").match(/^#h=(.+)$/);if(!m)return;let n;try{n=decodeURIComponent(m[1]);}catch(e){return;}
  const idx=GK_BY[esc(n)]!=null?GK_BY[esc(n)]:GK_LC[esc(n).toLowerCase()];if(idx==null)return;
  openModal('<h3>'+esc(n)+'<button class="close" onclick="closeModal()">✕</button></h3>'+gkHtml(GK_LIST[idx]));}
window.addEventListener("hashchange",openFromHash);setTimeout(openFromHash,0);
// ---- Display layer (NAME_DISPLAY / ALIASES from the data): rename what players READ on the page. ----
// Ids in the state, data-* attributes, select values and every lookup stay as engine ids; only visible text
// nodes and title tooltips are rewritten, as they appear (MutationObserver), so it covers every view.
(function(){const AL=DATA.aliases||{},keys=Object.keys(AL);
  const re=new RegExp("\\b("+keys.sort((a,b)=>b.length-a.length).map(k=>k.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).join("|")+")\\b","g");
  // idempotent: skip a match that already sits inside its own new name ("Reliquary" in "Reliquary Sanctum"),
  // so re-processing text (this observer sees its own edits) can never stack renames
  const disp=t=>!keys.length?dispScore(t):dispScore(t).replace(re,(m,_g,i,str)=>{const v=AL[m];let o=v.indexOf(m);while(o!==-1){if(str.substr(i-o,v.length)===v)return m;o=v.indexOf(m,o+1);}return v;});window.dispName=disp;
  const SKIP={SCRIPT:1,STYLE:1,TEXTAREA:1,INPUT:1};
  const fixText=n=>{const p=n.parentNode;if(!p||SKIP[p.nodeName]||(p.isContentEditable))return;const v=n.nodeValue,w=disp(v);if(w!==v)n.nodeValue=w;};
  const fixEl=el=>{if(el.nodeType===3){fixText(el);return;}if(el.nodeType!==1||SKIP[el.nodeName])return;
    if(el.hasAttribute&&el.hasAttribute("title")){const v=el.getAttribute("title"),w=disp(v);if(w!==v)el.setAttribute("title",w);}
    const tw=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let x;while((x=tw.nextNode()))fixText(x);
    el.querySelectorAll&&el.querySelectorAll("[title]").forEach(e=>{const v=e.getAttribute("title"),w=disp(v);if(w!==v)e.setAttribute("title",w);});};
  new MutationObserver(ms=>{for(const m of ms){if(m.type==="characterData")fixText(m.target);
      else if(m.type==="attributes")fixEl(m.target);else m.addedNodes.forEach(fixEl);}})
    .observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:["title"]});
  fixEl(document.body);})();
// Buried pile cards: "lift" (expand to the front) on hover, and STAY lifted while the cursor is on that card or
// on a tooltip opened from it. Switching to another buried card needs a short dwell, so passing over its
// edge on the way to a link doesn't drop the one you're reading back into the stack.
let LIFT=null,LIFT_T=null;
function setLift(pc){if(LIFT&&!document.body.contains(LIFT))LIFT=null;if(LIFT===pc)return;
  if(LIFT)LIFT.classList.remove("lift");LIFT=pc;if(pc)pc.classList.add("lift");}
document.addEventListener("mouseover",e=>{if(LIFT&&!document.body.contains(LIFT))LIFT=null;
  const inTip=e.target.closest("#gkTip"),inLift=LIFT&&LIFT.contains(e.target),pc=e.target.closest(".pc.buried");
  if(inTip||inLift){clearTimeout(LIFT_T);return;}
  clearTimeout(LIFT_T);
  if(pc){if(!LIFT)setLift(pc);else LIFT_T=setTimeout(()=>setLift(pc),350);return;}
  LIFT_T=setTimeout(()=>{if(!GK_PIN)setLift(null);},350);});
let GK_PIN=false,GK_HIDE=null;
function gkShow(el,html){clearTimeout(GK_HIDE);GKT.innerHTML=html;GKT.style.display="block";
  const r=el.getBoundingClientRect(),w=GKT.offsetWidth,h=GKT.offsetHeight;
  let x=Math.min(Math.max(6,r.left),window.innerWidth-w-6),y=r.bottom+6;if(y+h>window.innerHeight-6)y=Math.max(6,r.top-h-6);
  GKT.style.left=x+"px";GKT.style.top=y+"px";}
function gkHide(){if(GK_PIN)return;GK_HIDE=setTimeout(()=>{GKT.style.display="none";},180);}
function gkFor(el){if(el.dataset.tipk!=null){const t=totTip(el.dataset.tipk);return t?'<div class="gh">'+esc(el.textContent)+'</div><div>'+kwify(t)+'</div>':"";}
  if(el.dataset.tip!=null){return el.dataset.tip?'<div>'+kwify(el.dataset.tip)+'</div>':"";}
  if(el.dataset.tipl!=null){const L=String(el.dataset.tipl).split("\n").filter(Boolean);return L.length?'<div class="gh">'+kwify(L[0])+'</div>'+L.slice(1).map(x=>'<div class="tl'+(/^\s/.test(x)?' in':'')+'">'+kwify(x.trim())+'</div>').join(""):"";}
  if(el.dataset.gk!=null){const e=GK_LIST[+el.dataset.gk];return e?gkHtml(e):"";}
  if(el.dataset.tok!=null){const g=glossLookup(el.dataset.tok);return g.def?'<div class="gh">'+esc(el.dataset.tok)+'</div><div>'+esc(g.def)+'</div><div class="note">click for sources</div>':"";}
  return "";}
document.addEventListener("mouseover",e=>{if(GK_PIN)return;const el=e.target.closest(".gk,[data-tok],[data-tip],[data-tipk],[data-tipl]");
  if(el){const h=gkFor(el);if(h)gkShow(el,h);}else if(e.target.closest("#gkTip"))clearTimeout(GK_HIDE);});
document.addEventListener("mouseout",e=>{const el=e.target.closest(".gk,[data-tok],[data-tip],[data-tipk],[data-tipl],#gkTip");if(el)gkHide();});
document.addEventListener("click",e=>{const a=e.target.closest("[data-addp]");if(!a)return;e.preventDefault();e.stopPropagation();
  GK_PIN=false;GKT.style.display="none";addPursuitByName(a.dataset.addp);},true);
document.addEventListener("click",e=>{const a=e.target.closest("[data-addi]");if(!a)return;e.preventDefault();e.stopPropagation();
  GK_PIN=false;GKT.style.display="none";const i=a.dataset.addi.indexOf("|");addInfraByName(a.dataset.addi.slice(0,i),a.dataset.addi.slice(i+1));},true);
document.addEventListener("click",e=>{const el=e.target.closest(".gk,.tipk");
  if(el){e.preventDefault();GK_PIN=true;gkShow(el,gkFor(el));return;}
  if(!e.target.closest("#gkTip")){GK_PIN=false;GKT.style.display="none";}});

document.addEventListener("click",e=>{
  const it=e.target.closest("[data-item]"); if(it){inspectItem(it.dataset.kind,it.dataset.item);return;}
  const k=e.target.closest("[data-tok]"); if(k){inspectKeyword(k.dataset.tok);return;}
});
document.getElementById("inspect").onclick=e=>{if(e.target.id==="inspect")closeModal();};
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeModal();});

// ---- server build management ----
async function refreshBuilds(){
  const res=await apiFetch("GET","/api/builds");
  const sel=document.getElementById("buildList");
  if(!res||!res.builds){sel.innerHTML='<option value="">— saved builds —</option>';return;}
  sel.innerHTML='<option value="">— saved builds —</option>'+
    res.builds.filter(b=>!String(b.name).startsWith(GAME_PREFIX)).map(b=>'<option value="'+esc(b.name)+'">'+esc(b.name)+' ('+(b.updated_at||"").slice(0,16).replace("T"," ")+')</option>').join("");
  refreshGames(res.builds);
}
document.getElementById("buildSave").onclick=async()=>{
  const name=document.getElementById("buildName").value.trim();if(!name){flash("name the build first");return;}
  const r=await apiFetch("PUT","/api/builds/"+encodeURIComponent(name),{data:S});
  flash(r?("saved “"+name+"”"):"no server — use export instead");refreshBuilds();
};
document.getElementById("buildSnap").onclick=async()=>{
  const name=document.getElementById("buildName").value.trim()||"autosnap";
  const r=await apiFetch("POST","/api/builds/"+encodeURIComponent(name)+"/snapshot",{data:S});
  flash(r?("snapshot recorded"):"no server");
};
document.getElementById("buildLoad").onclick=async()=>{
  const name=document.getElementById("buildList").value;if(!name){flash("pick a build");return;}
  const r=await apiFetch("GET","/api/builds/"+encodeURIComponent(name));
  if(r&&r.data){const j=r.data; if(j.players){D=j;}else{D.players[0].board=Object.assign(newBoard(),j);} normalizeD(); reindex();document.getElementById("buildName").value=name;save();render();flash("loaded “"+name+"”");}
  else flash("load failed");
};
document.getElementById("buildDel").onclick=async()=>{
  const name=document.getElementById("buildList").value;if(!name){flash("pick a build");return;}
  await apiFetch("DELETE","/api/builds/"+encodeURIComponent(name));refreshBuilds();flash("deleted “"+name+"”");
};
// ---- chat (server games): All · /whisper <player> <text> · /alliance <text>. The server filters recipients;
// identity = this device's claim, proven by a per-device secret. The Duke sees everything.
let DEVKEY="";try{DEVKEY=localStorage.getItem("renown_devkey")||"";if(!DEVKEY){const a=new Uint8Array(24);crypto.getRandomValues(a);
  DEVKEY=Array.from(a,x=>x.toString(16).padStart(2,"0")).join("");localStorage.setItem("renown_devkey",DEVKEY);}}
  catch(e){DEVKEY=DEVKEY||(Math.random().toString(36).slice(2)+Math.random().toString(36).slice(2)+Date.now().toString(36));}
const CHAT={id:0,open:false,unread:0,msgs:[],me:null,busy:false,sig:null,first:true};
function chatHdr(){const h={"X-Renown-Dev":DEV,"X-Renown-Key":DEVKEY};if(TOKEN)h["X-Renown-Token"]=TOKEN;
  if(ADMIN){let pin="";try{pin=sessionStorage.getItem("renown_pin")||"";}catch(e){}if(pin)h["X-Renown-Pin"]=pin;else h["X-Renown-Duke"]="1";}
  return h;}
async function chatApi(method,body,q){try{const h=chatHdr();if(body!==undefined)h["Content-Type"]="application/json";
  const r=await fetch("/api/chat"+(q||""),{method,headers:h,body:body!==undefined?JSON.stringify(body):undefined});
  return {status:r.status,json:await r.json().catch(()=>null)};}catch(e){return null;}}
function chatTargets(){const me=myClaimP(),t=(D.players||[]).filter(p=>!sameP(p,me)).map(p=>({id:String(p.id),name:String(p.name||"")}));
  if(!t.some(x=>x.name.toLowerCase()==="duke"))t.push({id:"duke",name:"Duke"});return t;}
function chatParse(raw){const s=raw.trim();if(!s)return null;
  let m=/^\/whisper(?:\s+([\s\S]*))?$/i.exec(s);
  if(m){const rest=m[1]||"",rl=rest.toLowerCase(),c=chatTargets().filter(t=>t.name&&rl.startsWith(t.name.toLowerCase()+" "))
      .sort((a,b)=>b.name.length-a.name.length)[0];
    if(!c)return {err:"/whisper <player> <text>"};return {scope:"whisper",to:c.id,text:rest.slice(c.name.length+1)};}
  m=/^\/alliance(?:\s+([\s\S]*))?$/i.exec(s);if(m)return {scope:"alliance",text:m[1]||""};
  if(s[0]==="/")return {err:"/whisper <player> <text> · /alliance <text>"};
  return {scope:"all",text:s};}
function chatColor(c){return /^#[0-9a-f]{3,8}$/i.test(c||"")?c:"var(--ink)";}
function chatLine(m){if(m.sys)return '<div class="cm sys">'+esc(m.text)+'</div>';
  const tag=m.scope==="whisper"?' <span class="cs">→ '+esc(m.toName||"?")+'</span>':m.scope==="alliance"?' <span class="cs">[Alliance]</span>':'';
  return '<div class="cm'+(m.scope==="whisper"?" wh":m.scope==="alliance"?" al":"")+'"><span class="ct">'+esc((m.ts||"").slice(11,16))+'</span>'+
    '<b style="color:'+chatColor(m.color)+'">'+esc(m.name||"?")+'</b>'+tag+': '+esc(m.text)+'</div>';}
function chatRender(){const lg=document.getElementById("chatLog");if(!lg)return;
  const atEnd=lg.scrollHeight-lg.scrollTop-lg.clientHeight<40;lg.innerHTML=CHAT.msgs.map(chatLine).join("");if(atEnd)lg.scrollTop=lg.scrollHeight;
  const b=document.getElementById("chatBtn");b.textContent="💬"+(CHAT.unread?" "+CHAT.unread:"");b.classList.toggle("unread",!!CHAT.unread);
  const me=CHAT.me||{};document.getElementById("chatWho").textContent=me.name?(me.duke&&me.pid?me.name+" · Duke":me.name):"";
  document.getElementById("chatClr").style.display=ADMIN?"":"none";
  const inp=document.getElementById("chatIn");inp.placeholder=me.pid||me.duke?"message · /whisper · /alliance":"message (All)";}
function chatSys(t){CHAT.msgs.push({sys:true,text:t});chatRender();}
async function chatPoll(){document.body.classList.toggle("chat-on",API.online===true);
  if(API.online!==true||CHAT.busy)return;
  const sig=(ADMIN?1:0)+"|"+String((myClaimP()||{}).id??"");
  if(sig!==CHAT.sig){CHAT.sig=sig;CHAT.id=0;CHAT.msgs=[];CHAT.unread=0;CHAT.first=true;}
  CHAT.busy=true;const r=await chatApi("GET",undefined,"?since="+CHAT.id);CHAT.busy=false;
  if(!r||r.status!==200||!r.json||sig!==CHAT.sig)return;const j=r.json;CHAT.me=j.me;
  if(j.last<CHAT.id){CHAT.id=0;CHAT.msgs=[];CHAT.unread=0;CHAT.first=true;chatRender();return;}   // log cleared by the Duke
  if(j.msgs.length){CHAT.msgs=CHAT.msgs.concat(j.msgs).slice(-300);if(!CHAT.open&&!CHAT.first)CHAT.unread+=j.msgs.filter(m=>!m.mine).length;}
  CHAT.id=j.last;CHAT.first=false;chatRender();}
async function chatSend(){const inp=document.getElementById("chatIn"),p=chatParse(inp.value);if(!p)return;
  if(p.err){chatSys(p.err);return;}if(!p.text.trim()){chatSys("empty message");return;}
  const r=await chatApi("POST",p);if(!r){chatSys("not sent (offline)");return;}
  if(r.status!==200){chatSys((r.json&&r.json.error)||"not sent");return;}
  inp.value="";chatPoll();}
function chatComplete(inp){const v=inp.value;let m=/^\/(\w*)$/.exec(v);
  if(m){const c=["whisper","alliance"].filter(x=>x.startsWith(m[1].toLowerCase()));if(c.length===1)inp.value="/"+c[0]+" ";return;}
  m=/^(\/whisper\s+)(.*)$/i.exec(v);if(!m||/\s$/.test(m[2])&&m[2].trim()&&chatTargets().some(t=>m[2].toLowerCase().startsWith(t.name.toLowerCase()+" ")))return;
  const part=m[2].toLowerCase(),c=chatTargets().filter(t=>t.name.toLowerCase().startsWith(part));if(c.length)inp.value=m[1]+c[0].name+" ";}
(()=>{const d=document.createElement("div");d.id="chatDock";
  d.innerHTML='<button id="chatBtn">💬</button><div id="chatPanel"><div id="chatHead"><b>Chat</b><span class="note grow" id="chatWho"></span>'+
    '<button id="chatClr">clear</button><button id="chatX">×</button></div><div id="chatLog"></div>'+
    '<form id="chatForm" autocomplete="off"><input id="chatIn" maxlength="600"><button>send</button></form></div>';
  document.body.appendChild(d);
  document.getElementById("chatBtn").onclick=()=>{CHAT.open=true;CHAT.unread=0;d.classList.add("open");chatRender();
    const lg=document.getElementById("chatLog");lg.scrollTop=lg.scrollHeight;document.getElementById("chatIn").focus();};
  document.getElementById("chatX").onclick=()=>{CHAT.open=false;d.classList.remove("open");chatRender();};
  document.getElementById("chatClr").onclick=async()=>{if(!confirm("Clear the chat log for everyone?"))return;
    const r=await chatApi("DELETE");if(!r||r.status!==200){chatSys((r&&r.json&&r.json.error)||"not cleared");return;}chatPoll();};
  document.getElementById("chatForm").onsubmit=e=>{e.preventDefault();chatSend();};
  document.getElementById("chatIn").addEventListener("keydown",e=>{if(e.key==="Tab"){e.preventDefault();chatComplete(e.target);}
    else if(e.key==="Escape")document.getElementById("chatX").click();});})();
setInterval(chatPoll,POLL_MS);
async function initServer(){
  const tok=document.getElementById("srvToken");
  if(tok){tok.value=TOKEN;tok.onchange=()=>{TOKEN=tok.value.trim();try{localStorage.setItem("renown_token",TOKEN);}catch(e){}initServer();};}
  SYNC.ready=false;
  const res=await apiRaw("GET","/api/state");       // full server state
  if(!res||res.status!==200||!res.json)return;
  const j=res.json;SYNC.base={};SYNC.ver={};SYNC.rev=j.rev;
  Object.keys(j.parts).forEach(k=>{SYNC.base[k]=j.parts[k].data;SYNC.ver[k]=j.parts[k].version;});
  if(j.parts.shared){joinD(Object.fromEntries(Object.keys(j.parts).map(k=>[k,j.parts[k].data])));reindex();}
  SYNC.ready=true;if(nameAllSetts())save();render();renderList();
  if(!j.parts.shared)push();                         // empty server: seed it from this browser
  refreshBuilds();chatPoll();
}
setInterval(poll,POLL_MS);

buildFilters();if(nameAllSetts())save();renderList();render();
initServer();
