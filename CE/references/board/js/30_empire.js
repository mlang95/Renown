// ---- catalog ----
const TYPES=[...new Set(NAMES.map(n=>R[n].type))].sort();
document.querySelectorAll(".tab").forEach(t=>t.onclick=()=>{
  tab=t.dataset.k; document.querySelectorAll(".tab").forEach(x=>x.classList.toggle("on",x===t));
  document.getElementById("typeFilters").style.display = tab==="pursuit"?"flex":"none";
  renderList();
});
function buildFilters(){
  const box=document.getElementById("typeFilters"); box.innerHTML="";
  ["Monument"].filter(t=>TYPES.includes(t)).forEach(t=>{const c=document.createElement("span");c.className="chip"+(activeTypes.has(t)?" on":"");c.textContent=t;
    c.onclick=()=>{activeTypes.has(t)?activeTypes.delete(t):activeTypes.add(t);c.classList.toggle("on");renderList();};
    box.appendChild(c);});
}
// catalog view prefs: grouping (type | root chart) and Available / All
let CAT={group:"root",avail:true};
try{const c=JSON.parse(localStorage.getItem("renown_cat")||"null");if(c)CAT=Object.assign(CAT,c);}catch(_){}
CAT.group="root";                                     // Root charts are the only grouping (Type chips removed; Monument toggle kept)
function catSave(){try{localStorage.setItem("renown_cat",JSON.stringify(CAT));}catch(_){}}
const ROOTS=((DATA.tree&&DATA.tree.charts)||[]).map(c=>[c.title,Object.keys(c.nodes||{}).filter(n=>R[n])]).filter(x=>x[0]&&x[1].length);
{const inR=new Set(ROOTS.flatMap(x=>x[1])),rest=NAMES.filter(n=>!inR.has(n));if(ROOTS.length&&rest.length)ROOTS.push(["Other",rest]);}   // nothing drops out of the catalog
let WP=null;          // empty-ward picker: {gid, wi, q} while its modal is open
let FOR_SID=null;     // empty-ward click: catalog shows only what that settlement can take; next add goes there
function pAvail(n){return !scopeBlock(n,null)&&(scopeOf(n)!=="Settlement"||!S.settlements.length||S.settlements.some(s=>!occupants(s.id).some(o=>o.name===n)))&&unlockStatus(n).ok;}
function iAvail(kind,n){const src=kind==="infra"?INFRA:WON,have=kind==="infra"?S.infra:S.wonders;return !have[n]&&!scopeBlock(n,null)&&infraReqStatus(src[n]).ok;}
function catUpkeep(n){if(NATURAL.has(n))return 0;const r=R[n]||{};if(r.upkeep!=null)return r.upkeep;const t=r.type;return (PUP.byType&&t in PUP.byType)?PUP.byType[t]:(PUP.def||0);}
function seg(opts,cur,fn){const w=document.createElement("span");w.className="seg";
  opts.forEach(([k,l])=>{const c=document.createElement("span");c.className="chip"+(k===cur?" on":"");c.textContent=l;c.onclick=()=>fn(k);w.appendChild(c);});return w;}
function renderList(){
  const q=document.getElementById("search").value.toLowerCase();
  const list=document.getElementById("list"); list.innerHTML="";
  const ctl=document.createElement("div");ctl.className="catctl";
  ctl.appendChild(seg([[true,"Available"],[false,"All"]],CAT.avail,k=>{CAT.avail=k;catSave();renderList();}));
  if(tab==="pursuit"&&FOR_SID!=null){if(!S.settlements.some(s=>s.id===FOR_SID))FOR_SID=null;else{
    const c=document.createElement("span");c.className="chip on forsid";c.textContent=settTier(FOR_SID)+" ✕";c.title="clear";
    c.onclick=()=>{FOR_SID=null;renderList();};ctl.appendChild(c);}}
  list.appendChild(ctl);
  if(tab==="pursuit"){
    const searching=q.length>0;
    const keep=n=>nameHit(n,q)&&!(activeTypes.size&&!activeTypes.has(R[n].type))&&(!CAT.avail||pAvail(n))&&(FOR_SID==null||canPlace(n,FOR_SID).ok)&&cultureKeep(n);
    const groups=(CAT.group==="root"&&ROOTS.length?ROOTS.map(([t,ns])=>[t,ns]):TYPES.map(t=>[t,NAMES.filter(n=>R[n].type===t)]))
      .map(([t,ns])=>[t,ns.filter(keep)]).filter(g=>g[1].length);
    const ctl2=document.createElement("div");ctl2.className="catctl";
    const mk=(txt,fn,gt)=>{const c=document.createElement("span");c.className="chip";c.textContent=txt;if(fn)c.onclick=fn;if(gt)c.dataset.goto=gt;ctl2.appendChild(c);};
    const gk=t=>CAT.group+":"+t;
    mk("expand all",()=>{groups.forEach(g=>catOpen.add(gk(g[0])));renderList();});
    mk("collapse all",()=>{catOpen.clear();renderList();});
    mk("tree ▸",null,"reference#refTree");
    list.appendChild(ctl2);
    if(!groups.length){const e=document.createElement("div");e.className="empty";e.textContent=CAT.avail?"None available.":"No match.";list.appendChild(e);return;}
    groups.forEach(([t,mem])=>{
      const openT=searching||FOR_SID!=null||catOpen.has(gk(t));
      const g=document.createElement("div");g.className="typegroup";
      const th=document.createElement("div");th.className="th";th.style.cursor="pointer";
      th.textContent=(openT?"▾ ":"▸ ")+t+" ("+mem.length+")";
      th.onclick=()=>{catOpen.has(gk(t))?catOpen.delete(gk(t)):catOpen.add(gk(t));renderList();};
      g.appendChild(th);
      if(openT) mem.forEach(n=>g.appendChild(pursuitRow(n)));
      list.appendChild(g);
    });
  } else {
    const kindOf=n=>WON[n]?"wonder":"infra",srcOf=n=>WON[n]||INFRA[n],haveOf=n=>(WON[n]?S.wonders:S.infra)[n];
    const ns=Object.keys(INFRA).concat(Object.keys(WON)).filter(n=>nameHit(n,q)&&(!CAT.avail||iAvail(kindOf(n),n))&&cultureKeepWonder(n));
    if(!ns.length){const e=document.createElement("div");e.className="empty";e.textContent=CAT.avail?"None available.":"No match.";list.appendChild(e);return;}
    ns.forEach(n=>{
      const r=srcOf(n);const row=itemRow(n,false,!!haveOf(n));
      const rs=infraReqStatus(r);
      if(!rs.ok||rs.manual){const meta=document.createElement("span");meta.className="meta";meta.textContent=!rs.ok?"🔒":"?";
        meta.title=(!rs.ok?"missing: "+rs.missing.join(", "):"")+(rs.manual?(rs.ok?"":"\n")+"check manually: "+rs.toks.filter(x=>x.ok===null).map(x=>x.tok).join(", "):"");
        if(!rs.ok)meta.style.color="var(--upkeep)";row.querySelector(".rtop").insertBefore(meta,row.querySelector(".addbtn"));}
      const bt=infraBuildTime(n);
      sub(row,[r.tier,"Upkeep "+(r.upkeep||0),"Build Timer "+bt].concat(r.requirement?["req: "+r.requirement]:[]).join(" · "),r.effect_raw);
      tip(row,[r.effect_raw,r.requirement?"Requires: "+r.requirement:""]);
      list.appendChild(row);
    });
  }
}
// ---- empty-ward picker: choose a holding for that settlement in place (catalog filters; Available/All shared) ----
function wardPick(gid,wi){openModal("");WP={gid,wi,q:""};wpRender();
  if(window.innerWidth>700){const i=document.getElementById("wpQ");if(i)i.focus();}}
function wpRender(){if(!WP)return;const gid=WP.gid,card=document.getElementById("inspectCard");
  if(!S.settlements.some(x=>x.id===gid)){closeModal();return;}
  const q=WP.q.toLowerCase(),keep=n=>nameHit(n,q)&&(!CAT.avail||pAvail(n))&&canPlace(n,gid).ok;
  const groups=(ROOTS.length?ROOTS.map(([t,ns])=>[t,ns.filter(keep)]):TYPES.map(t=>[t,NAMES.filter(n=>R[n].type===t&&keep(n))])).filter(g=>g[1].length);
  card.innerHTML='<h3>'+esc(settTier(gid))+' · Ward '+(WP.wi+1)+'<button class="close">×</button></h3>';
  card.querySelector(".close").onclick=closeModal;
  const ctl=document.createElement("div");ctl.className="catctl";
  const inp=document.createElement("input");inp.id="wpQ";inp.placeholder="filter…";inp.value=WP.q;inp.style.flex="1";inp.style.minWidth="0";
  inp.oninput=()=>{const pos=inp.selectionStart;WP.q=inp.value;wpRender();const n=document.getElementById("wpQ");if(n){n.focus();n.setSelectionRange(pos,pos);}};
  ctl.appendChild(inp);
  ctl.appendChild(seg([[true,"Available"],[false,"All"]],CAT.avail,k=>{CAT.avail=k;catSave();wpRender();renderList();}));
  card.appendChild(ctl);
  if(!groups.length){const e=document.createElement("div");e.className="empty";e.textContent=CAT.avail?"None available.":"No match.";card.appendChild(e);return;}
  groups.forEach(([t,mem])=>{const g=document.createElement("div");g.className="typegroup";
    const th=document.createElement("div");th.className="th";th.textContent=t+" ("+mem.length+")";g.appendChild(th);
    mem.forEach(n=>{const row=pursuitRow(n),go=e=>{e.stopPropagation();wpPlace(n);};
      row.querySelector(".nm").onclick=go;row.querySelector(".addbtn").onclick=go;g.appendChild(row);});
    card.appendChild(g);});}
function wpPlace(n){const gid=WP?WP.gid:null;closeModal();if(gid==null)return;
  const pf=FOR_SID,pt=tab;FOR_SID=gid;activeSid=gid;tab="pursuit";
  try{addItem(n);}finally{tab=pt;FOR_SID=pf===gid?null:pf;}
  renderList();}
function pursuitRow(n){
  const r=R[n],row=itemRow(n,r.monument,(PC[n]||0)>0),us=unlockStatus(n);
  if(r.unlock_raw&&r.unlock_raw!=="-"&&r.unlock_raw!=="—"&&(!CAT.avail||us.manual)){const m=document.createElement("span");m.className="meta";
    m.textContent=(us.ok?(us.manual?"? ":""):"🔒 ")+r.unlock_raw;m.title=us.toks.map(x=>(x.ok===false?"✗ ":x.ok?"✓ ":"? ")+x.t+" — "+x.why).join("\n");
    if(!us.ok)m.style.color="var(--upkeep)";row.querySelector(".rtop").insertBefore(m,row.querySelector(".addbtn"));}
  const parts=[NATURAL.has(n)?"Natural":"Upkeep "+catUpkeep(n),"Build Timer "+pursuitBuildTime(n)];
  if(CAT.group==="root")parts.unshift(r.type);
  sub(row,parts.join(" · "),NATURAL.has(n)?(r.innate_raw||"").replace(/^Natural\s*[;,.]\s*/i,""):r.innate_raw);
  tip(row,[r.innate_raw,(r.efficient||[]).length?"Efficient: "+r.efficient.join(", "):"",r.unlock_raw&&r.unlock_raw!=="-"&&r.unlock_raw!=="—"?"Unlock: "+r.unlock_raw:""]);
  return row;
}
function sub(row,cost,fx){const s=document.createElement("div");s.className="rsub";
  s.innerHTML='<span class="rc">'+esc(cost)+'</span>'+(fx?'<span class="rfx">'+esc(fx)+'</span>':'');row.appendChild(s);}
function tip(row,lines){const t=lines.filter(Boolean).join("\n");if(t)row.querySelector(".nm").dataset.tip=t;}
function itemRow(n,mon,have){
  const row=document.createElement("div");row.className="row"+(mon?" mon":"")+(have?" have":"");
  const top=document.createElement("div");top.className="rtop";
  const nm=document.createElement("span");nm.className="nm";nm.textContent=n;nm.onclick=()=>addItem(n);
  const b=document.createElement("button");b.className="addbtn";b.textContent="+";
  b.onclick=(e)=>{e.stopPropagation();addItem(n);};
  top.appendChild(nm);top.appendChild(b);row.appendChild(top);return row;
}
// toast + Inbox notice log (this device, this session)
const FLASHLOG=[];
function flash(msg){const el=document.getElementById("flash");if(el){el.textContent=msg;el.style.opacity=1;clearTimeout(flash._t);flash._t=setTimeout(()=>el.style.opacity=0,2600);}
  FLASHLOG.unshift({msg:String(msg),ts:Date.now()});FLASHLOG.length=Math.min(FLASHLOG.length,25);try{renderInbox();}catch(e){}}
function addInfraByName(kind,n){                   // kind "infra" | "wonder"; same as adding it from the catalog
  kind=WON[n]?"wonder":"infra";                      // Wonders are the Wondrous tier: one catalog list
  {const blk=scopeBlock(n,null);if(blk){flash(blk);return;}}
  (kind==="infra"?S.infra:S.wonders)[n]=1;itm();
  let bn="";if(gameStarted()){const t=infraBuildTime(n);if(t>0)S.itimer[n]=t;bn=buildNote(infraBaseTime(n));}save();render();renderList();flash(n+(bn||" added"));}
// place one Holding on the board S (Scope already checked): best efficient pairing, else pref / capital / any free Ward, else Unplaced
function placeHolding(n,pref,forcedSid){
  // Natural Pursuits fill Hamlets first (the only Pursuits a Hamlet takes); everything else: active settlement, capital, the rest
  const hams=(SIMPLE?hamletRoot(n):hamletOK(n))?S.settlements.filter(x=>x.tier==="Hamlet").map(x=>x.id):[];
  const forced=forcedSid!=null&&S.settlements.some(s=>s.id===forcedSid)&&canPlace(n,forcedSid).ok;
  const order=forced?[forcedSid]:hams.concat([pref],[capitalSett()&&capitalSett().id],S.settlements.map(x=>x.id)).filter((x,i,a)=>x!=null&&a.indexOf(x)===i);
  let target=null,host=null,note="",hosts=null;
  // 1) efficient pairing first — before a Natural goes solo into a Hamlet: pick the settlement where adding
  //    it creates the most new efficient pairs (it rides a host there, or something already there rides it).
  //    Ties keep the usual order (Hamlets for Naturals, active settlement, capital, the rest).
  {let best=0;
    for(const sd of order){const c=canPlace(n,sd);if(!c.ok)continue;
      const occ=occupants(sd),before=exemptionsOf(occ).size,ex=exemptionsOf(occ.concat([{id:1e9,name:n}]));
      const gain=ex.size-before;if(gain>best){best=gain;target=sd;host=ex.hostOf[1e9]||null;
        hosts=occ.filter(q=>ex.hostOf[q.id]===n).map(q=>q.name);}}}
  // 2) the active settlement, 3) any settlement with an eligible free Ward (capital first)
  if(target==null)for(const sd of order){if(canPlace(n,sd).ok){target=sd;break;}}
  if(target==null)note=" — no eligible free Ward, left Unplaced";
  const np={id:nextId(S.placed),name:n,sid:target};if(S===activeBoard())pid=np.id+1;if(gameStarted()){const t=pursuitBuildTime(n);if(t>0)np.bt=t;}
  if(host){np.rideOn=host;np.ride=1+Math.max(0,...S.placed.map(p=>p.ride||0));}
  S.placed.push(np);
  return {np,target,host,hosts,note,forced};}
function addItem(n){
  if(tab==="infra"||tab==="wonder"){addInfraByName(tab,n);return;}
  // pursuit — Scope: Settlement / Empire / Realm (Principle 15)
  {const blk=scopeBlock(n,null);if(blk){flash(blk);return;}}
  const P_=placeHolding(n,activeSid,FOR_SID),target=P_.target,host=P_.host,hosts=P_.hosts,note=P_.note,forced=P_.forced;
  if(forced){FOR_SID=null;const ap=document.getElementById("appBoard");
    if(window.innerWidth<=700&&ap){ap.dataset.mc="board";document.querySelectorAll("#mnav [data-mc]").forEach(x=>x.classList.toggle("on",x.dataset.mc==="board"));}}
  save();render();renderList();
  flash(n+(target!=null?" → "+settTier(target)+(host?" (efficient with "+host+")":(hosts&&hosts.length?" ("+hosts.join(", ")+" efficient with it)":"")):"")+note+(gameStarted()?buildNote(pursuitBaseTime(n)):""));   // after render (it rebuilds the toolbar)
}
function removeInstance(id){S.placed=S.placed.filter(p=>p.id!==id);save();render();renderList();}
function addPursuitByName(n){if(!R[n])return;const t=tab;tab="pursuit";try{addItem(n);}finally{tab=t;}}   // used by card '+' (respects active settlement)
function moveInstance(id,sid){
  const p=S.placed.find(x=>x.id===id);if(!p)return;
  if(sid!=null&&sid!=="faction"&&String(p.sid)!==String(sid)&&scopeOf(p.name)==="Settlement"&&occupants(sid).some(o=>o.name===p.name)){flash("one "+p.name+" per Settlement");render();return;}
  p.sid=sid;save();render();
}

// ---- mastery ----
// ---- infrastructure / wonder requirements ----
// requirement string = '+'-joined tokens. Token kinds:
//   <Infra name>          → that Infrastructure built AND its own requirements met
//   One Tier <Tier>       → any ONE Infrastructure of that tier built and active (ruling)
//   All Infrastructure…   → every Infrastructure built and requirement-valid (Wonders)
//   …Capital City…        → your capital is City tier or higher (City / Metropolis)
//   …Capital…             → you have a capital settlement (every player has one)
//   anything else         → not modelled → manual "?" flag, non-blocking
const INFRA_TIERS=(()=>{const t=(DATA.infraTiers||[]).length?DATA.infraTiers:Object.keys((DATA.buildTimers||{}).Infrastructure||{});return t.length?t:["Primitive","Developed","Sophisticated","Prodigious","Wondrous"];})();
function infraReqToks(rec){const s=((rec&&rec.requirement)||"").trim();
  const toks=(!s||/^none$/i.test(s))?[]:s.split("+").map(t=>t.trim()).filter(Boolean);
  // general rule: every tier needs one active Infrastructure of the tier below (transitive through that piece's own validity)
  const ti=INFRA_TIERS.indexOf(rec&&rec.tier);
  if(ti>0){const prev=INFRA_TIERS[ti-1];if(!toks.some(t=>new RegExp("^One\\s+Tier\\s+"+prev+"$","i").test(t)))toks.unshift("One Tier "+prev);}
  return toks;}
function infraTokStatus(tok,seen){
  let m;seen=seen||new Set();
  if(m=tok.match(/^One\s+Tier\s+(\w+)$/i)){const t=m[1].toLowerCase();
    const all=Object.keys(INFRA).filter(n=>(INFRA[n].tier||"").toLowerCase()===t),have=all.filter(n=>S.infra[n]&&infraValid(n,seen));
    return {tok,ok:have.length>0,missing:have.length?[]:["any one "+cap(t)+" Infrastructure"],why:"one "+cap(t)+(have.length?" ("+have[0]+")":"")};}
  if(/^All\s+Infrastructure/i.test(tok)){const all=Object.keys(INFRA),miss=all.filter(n=>!infraValid(n,seen));
    return {tok,ok:!miss.length,missing:miss,why:"all Infrastructure ("+(all.length-miss.length)+"/"+all.length+")"};}
  if(INFRA[tok]){const built=!!S.infra[tok],ok=built&&infraValid(tok,seen);
    return {tok,ok,missing:ok?[]:[tok+(built?" (req unmet)":"")],why:tok};}
  if(/capital\s+city/i.test(tok)){const c=capitalSett(),ok=!!c&&TIER_CHAIN.indexOf(c.tier)>=TIER_CHAIN.indexOf("City");
    return {tok,ok,missing:ok?[]:[c?"Capital is a "+c.tier+" (needs City)":"a Capital"],why:"Capital is a City+"+(c?" (now "+c.tier+")":" — none set")};}
  if(/capital/i.test(tok)){const c=capitalSett();return {tok,ok:!!c,missing:c?[]:["a Capital"],why:"Capital"+(c?" ("+c.tier+")":" — none set")};}
  return {tok,ok:null,missing:[],why:tok+" — check manually"};
}
function infraReqStatus(rec,seen){
  const st=infraReqToks(rec).map(t=>infraTokStatus(t,seen));
  const bad=st.filter(x=>x.ok===false),man=st.filter(x=>x.ok===null);
  return {ok:!bad.length,manual:man.length>0,toks:st,missing:[].concat(...bad.map(x=>x.missing))};
}
function infraValid(n,seen){               // built + requirements met (manual tokens don't block)
  const src=INFRA[n]?S.infra:S.wonders, rec=INFRA[n]||WON[n];
  if(!rec||!src[n])return false;
  if(((S.itimer||{})[n]>0)||((S.idmg||{})[n]>0))return false;
  seen=seen||new Set(); if(seen.has(n))return true; const s2=new Set(seen);s2.add(n);
  return infraReqStatus(rec,s2).ok;
}
function infraActive(tok){return infraValid(tok);}
function infraReqLinesHTML(rec){
  return infraReqStatus(rec).toks.map(x=>'<div class="ireq"><span class="'+(x.ok===true?'ok':x.ok===false?'no':'mn')+'">'+(x.ok===true?'✓':x.ok===false?'✗':'?')+'</span><span>'+esc(x.why)+'</span>'+(x.ok===false&&x.missing.length?'<span class="why">missing: '+esc(x.missing.join(", "))+'</span>':'')+'</div>').join("");
}
// infra/wonder tokens a pursuit's mastery depends on
function masteryInfraToks(r){return [...new Set([].concat(...r.mreq).map(t=>t.trim()).filter(t=>INFRA[t]||WON[t]))];}
function masteryInfraHTML(r){
  const toks=masteryInfraToks(r);if(!toks.length)return "";
  return '<div class="lbl" style="margin-top:6px">INFRASTRUCTURE REQ</div>'+toks.map(t=>{const rec=INFRA[t]||WON[t],built=!!(INFRA[t]?S.infra:S.wonders)[t],st=infraReqStatus(rec),ok=built&&st.ok;
    return '<div class="ireq"><span class="'+(ok?'ok':'no')+'">'+(ok?'✓':'✗')+'</span><span>'+esc(t)+'</span><span class="why">'+
      (!built?'not built':!st.ok?'built — its req unmet: '+esc(st.missing.join(", ")):'active')+(st.manual?' · ? '+esc(st.toks.filter(x=>x.ok===null).map(x=>x.tok).join(", ")):'')+'</span></div>'+
      (!ok&&rec.requirement&&!/^none$/i.test(rec.requirement)?'<div class="ireq"><span class="why" style="margin-left:14px">'+esc(t)+' needs: '+esc(rec.requirement)+'</span></div>':'');}).join("");
}
function annotReqTok(o){o=o.trim();
  if(INFRA[o]||WON[o]){const built=!!(INFRA[o]?S.infra:S.wonders)[o];
    if(!built)return o+" [infra: not built]";
    const st=infraReqStatus(INFRA[o]||WON[o]);if(!st.ok)return o+" [infra req unmet: "+st.missing.join(", ")+"]";}
  return o;}
function optionMet(tok,have,craft,tc){
  tok=tok.trim();let m;
  if(m=tok.match(/^Craft\s+(\d+)$/i))return craft>=+m[1];
  if(m=tok.match(/^(\d+)\s+(.+)$/))return (tc[m[2].trim()]||0)>=+m[1];
  if(R[tok])return have.has(tok);
  if(DATA.settlements[tok])return S.settlements.some(s=>s.tier===tok);
  return infraActive(tok);
}
function reqStatus(rec,have,craft,tc){
  if(!rec.mreq.length)return{earned:true,missing:[]};
  const missing=[];let ok=true;
  rec.mreq.forEach(g=>{if(!g.some(o=>optionMet(o,have,craft,tc))){ok=false;missing.push(g.map(annotReqTok).join(" / "));}});
  return{earned:ok,missing};
}
// Faction pieces: Mastery always counts as active, regardless of requirements.
function instStatus(inst,r,have,craft,tc){return inst.fac?{earned:true,missing:[]}:reqStatus(r,have,craft,tc);}
// SIMPLE requirements (flags, never blocks):
//   UNLOCK  — you control (anywhere, active) one complete line of its Mastery Chain back to its root, plus its infrastructure_req.
//             Checked when it is started: once met it stays met (a parent lost later changes nothing).
//   FREE RIDE (Ward) — sharing a settlement with that parent; handled by exemptionsOf / the ⚡ badge.
// One complete line of the Mastery Chain: a controlled, active parent whose own line is complete, back to a
// root (a piece with no chain parent — Raw Materials — or a faction piece). Returns the line or null.
function chainLine(name,own,seen){
  seen=seen||new Set();if(seen.has(name))return null;seen.add(name);
  const eff=effList(name),el=effLabel(name);
  if((R[name]||{}).root)return [];                                                // Root: exempt from the chain check
  if(!eff.length&&!el.some(e=>/^natural$/i.test(String(e))))return [];          // no chain parent
  const cands=own.filter(o=>eff.includes(o.name)||(o.fac&&el.some(e=>/^natural$/i.test(String(e)))));
  for(const o of cands){if(o.fac)return [o.name];const up=chainLine(o.name,own,new Set(seen));if(up)return up.concat([o.name]);}
  return null;
}
function simpleReq(inst,r,have,craft,tc){
  if(inst.fac)return {ok:true,unl:true,infra:{earned:true,missing:[]},missing:[],sticky:false};
  const own=S.placed.filter(o=>o.id!==inst.id&&o.sid!=null&&pActive(o));
  const line=chainLine(inst.name,own),unl=!!line,via=line&&line.length?line.join(" → "):null;
  const infra=reqStatus(r,have,craft,tc),ok=unl&&infra.earned;
  if(ok&&!inst.unl){inst.unl=1;IGN_DIRTY=true;}          // met at start → stays met
  if(inst.unl)return {ok:true,unl:true,via,infra:{earned:true,missing:[]},missing:[],sticky:!ok};
  const missing=[];
  if(!unl)missing.push("control a complete line of its "+CHAINL+": "+effLabel(inst.name).join(" or "));
  if(!infra.earned)missing.push(...infra.missing);
  return {ok:false,unl,via,infra,missing,sticky:false};
}
function simpleReqHTML(inst,sr){
  const L=[];const el=effLabel(inst.name).filter(e=>!/^hamlet$/i.test(String(e)));
  if(el.length&&!(R[inst.name]||{}).root)L.push('<div class="ireq"><span class="'+(sr.unl?'ok':'no')+'">'+(sr.unl?'✓':'✗')+'</span><span>'+esc(CHAINL)+': '+
    el.map(e=>R[e]?quickChip(e):(/^natural$/i.test(String(e))?"any "+kwify("Natural")+" Pursuit":"any "+esc(e)+" Pursuit")).join(" or ")+'</span><span class="why">'+
    (sr.sticky?'met when started':sr.unl?(sr.via?'line: '+esc(sr.via):'met'):'no complete line controlled')+'</span></div>');
  const r=R[inst.name]||{};if(r.mreq_raw)L.push('<div class="ireq"><span class="'+(sr.infra.earned?'ok':'no')+'">'+(sr.infra.earned?'✓':'✗')+'</span><span>infrastructure: '+esc(r.mreq_raw)+'</span>'+(sr.infra.earned||sr.sticky?'':'<span class="why">missing: '+esc(missTxt(sr.infra.missing))+'</span>')+'</div>');
  return L.length?'<div class="lbl">REQUIRES</div>'+L.join(""):"";
}
function computeEarned(have){
  const tc={};Object.keys(PC).forEach(n=>tc[R[n].type]=(tc[R[n].type]||0)+PC[n]);
  let earned={},craft=0;
  for(let it=0;it<4;it++){
    craft=0;
    Object.keys(PC).forEach(n=>{const r=R[n],q=PC[n];
      r.innate.forEach(a=>{if(a.flat&&a.cat==="craft")craft+=a.val*q;});
      if(earned[n])r.mastery.forEach(a=>{if(a.flat&&a.cat==="craft")craft+=a.val*q;});});
    Object.keys(S.infra).filter(infraOn).forEach(n=>INFRA[n].atoms.forEach(a=>{if(a.flat&&a.cat==="craft")craft+=a.val;}));
    Object.keys(S.wonders).filter(infraOn).forEach(n=>WON[n].atoms.forEach(a=>{if(a.flat&&a.cat==="craft")craft+=a.val;}));
    const ne={};Object.keys(PC).forEach(n=>{ne[n]=reqStatus(R[n],have,craft,tc).earned;});
    S.placed.forEach(p=>{if(p.fac&&pActive(p))ne[p.name]=true;});      // faction pieces: always-active Mastery
    earned=ne;
  }
  return{earned,craft,tc};
}

// ---- atom chip ----
function atomEl(a){
  const phase=a.season?"season":(PHASE[a.cat]||"other");const col=cvar(PHASE_COLOR[phase]);
  const el=document.createElement("span");el.className="atom"+(a.cond?" cond":"");
  el.style.borderColor=col;el.style.color=col;
  el.innerHTML=kwify(a.text);
  if(a.season){const s=document.createElement("span");s.className="s";s.textContent="["+a.season+"]";el.appendChild(s);}
  el.title=(a.scale?"scales: +"+a.scale.per+" per "+a.scale.of+" · ":"")+(a.flat?"flat — summed":"conditional/triggered — not summed")+" · "+PHASE_LABEL[phase];
  return el;
}
function atomsBlock(atoms,hideCombat){
  const wrap=document.createElement("div");wrap.className="atoms";
  const vis=atoms.filter(a=>!(hideCombat&&(a.cat==="combat"||a.cat==="other"||a.cat==="natural")));
  if(!vis.length){const s=document.createElement("span");s.className="note";s.textContent="—";wrap.appendChild(s);}
  else{ // a clause the parser split at a comma ("…Oppose" | "you may…") is shown as one chip again
    const merged=[];vis.forEach(a=>{const p=merged[merged.length-1];
      if(p&&!a.scale&&!p.scale&&a.val==null&&p.val==null&&a.cat===p.cat&&/^[a-z]/.test(a.text||""))merged[merged.length-1]=Object.assign({},p,{text:p.text+", "+a.text});
      else merged.push(a);});
    merged.forEach(a=>wrap.appendChild(atomEl(a)));}
  return wrap;
}

// ---- render ----
function render(){
  if(lockOn())HOTSEAT=false;                // claims replace hot-seat on a server game (the Duke keeps it)
  document.body.classList.toggle("lk-board",lockOn()&&!mine(D.players[D.active]));
  document.body.classList.toggle("lk-spec",lockOn()&&!myClaimP());
  document.body.classList.toggle("lk-on",lockOn());
  IGN_N=0;setTimeout(ignNote,0);
  reindex();                    // S := active board, ids synced
  try{syncMapTiers();}catch(e){console.warn("map sync",e);}
  applyTheme(D.theme||"pixel");
  applySkin(D.shape||"sharp");
  renderTopBar();
  if(D.view==="battle"&&!mods().battle)D.view="table";
  if(D.view==="dash"||D.view==="renown"||D.view==="realm")D.view="table";
  if(D.view==="map")D.view="table";
  const view=D.view||"table";
  // Battle is a modal over the Realm (no tab): the Realm renders underneath
  const base=view==="battle"?"table":view;
  document.body.classList.toggle("spectating",spectating());
  renderTurnStrip();try{renderSetup();}catch(e){console.warn("setup",e);}syncBoardEndBtn();try{renderHUD();}catch(e){console.warn("HUD",e);}
  document.body.dataset.view=base;document.body.classList.toggle("bmodal",view==="battle");
  document.querySelectorAll(".modcb").forEach(cb=>{cb.checked=!!mods()[cb.dataset.m];
    if(!cb._w){cb._w=1;cb.onchange=()=>{mods()[cb.dataset.m]=cb.checked;save();render();};}});
  document.getElementById("viewBattle").style.display = view==="battle"?"":"none";
  document.getElementById("appBoard").style.display = base==="board"?"":"none";
  document.getElementById("viewReference").style.display = base==="reference"?"":"none";
  document.getElementById("viewTable").style.display = base==="table"?"":"none";
  document.querySelectorAll(".vtab,#tabbar [data-v]").forEach(t=>t.classList.toggle("on",t.dataset.v===base));
  try{renderInbox();renderChrome();}catch(e){console.warn("inbox",e);}
  if(view==="battle"){renderTable();renderBattle();return;}
  if(base==="reference"){renderReference();return;}
  if(base==="table"){renderTable();return;}

  recomputePC();
  const have=new Set(Object.keys(PC));
  const {earned,craft,tc}=computeEarned(have);
  const hideCombat=document.getElementById("hideCombat").checked;
  renderFaction();
  renderPursuitBoard(earned,craft,tc,hideCombat,have);
  renderInfraSection("infra",INFRA,S.infra,hideCombat);
  renderInfraSection("wonder",WON,S.wonders,hideCombat);
  renderArmy();
  computeTotals(have,earned,tc);
  renderSettlements();
  renderScene();
  renderEsBar();
  renderPO();
  {const sig=JSON.stringify([D.active,S.domains,S.placed.map(p=>p.name+(p.bt||0)),S.infra,S.wonders,curSeason()]);if(sig!==renderList._sig){renderList._sig=sig;renderList();}}
  trIn.value=S.treasury;document.getElementById("turn").textContent=S.turn;document.getElementById("autoNet").checked=!!S.autoNet;
  const total=S.placed.length;
  document.getElementById("poolcount").textContent=total?(total+" placed · "+Object.keys(PC).length+" types"):"";
}

// ---- top bar: view tabs + player switcher ----
document.querySelectorAll(".vtab,#tabbar [data-v]").forEach(t=>t.onclick=()=>{D.view=t.dataset.v;if(t.dataset.v!=="board")SPECTATE=null;save();render();window.scrollTo(0,0);});
function renderTopBar(){
  const ts=document.getElementById("themeSel");
  if(ts){ts.value=D.theme||"pixel";if(!ts._wired){ts._wired=1;ts.onchange=()=>{D.theme=ts.value;applyTheme(D.theme);save();render();};}}
  const sh=document.getElementById("shapeSel");
  if(sh){sh.value=D.shape||"sharp";if(!sh._wired){sh._wired=1;sh.onchange=()=>{D.shape=sh.value;applySkin(D.shape);save();render();};}}
  const bar=document.getElementById("playerBar");bar.innerHTML="";
  const chips=[];
  D.players.forEach((p,i)=>{
    const c=document.createElement("span");c.className="pchip"+(i===D.active?" on":"");
    const cl=claimOf(p);
    c.innerHTML='<span class="pdot" style="background:'+p.color+'"></span><span class="pname">'+esc(p.name)+'</span>'+
      (cl?'<span class="note" title="'+(mine(p)?"claimed by this device":"claimed")+'">'+(mine(p)?" \u2605":" \ud83d\udd12")+'</span>':'')+
      (!D.started&&isReady(p)?'<span class="su-ok" title="ready"> \u2713</span>':'');
    c.onclick=()=>{D.active=i;SPECTATE=null;reindex();render();renderList();};
    bar.appendChild(c);chips.push(c);
  });
  const add=document.createElement("span");add.className="pchip";add.textContent="+ player";
  add.onclick=()=>{const np=newPlayer(D.players.length+1);np.id=Math.max(Date.now(),1+Math.max(0,...D.players.map(p=>+p.id||0)));D.players.push(np);D.active=D.players.length-1;reindex();save();render();renderList();};
  bar.appendChild(add);
  const p=D.players[D.active], chip=chips[D.active];
  const card=document.getElementById("playerCard");if(card)card.innerHTML="";
  const put=el=>(card||bar).appendChild(el);
  const nm=document.createElement("input");nm.value=p.name;nm.style.width="110px";nm.title="rename player";
  nm.oninput=()=>{p.name=nm.value;const l=chip&&chip.querySelector(".pname");if(l)l.textContent=p.name;save();};
  const col=document.createElement("input");col.type="color";col.value=p.color;col.style.width="30px";col.style.padding="0";col.title="player color";
  col.oninput=()=>{p.color=col.value;const d=chip&&chip.querySelector(".pdot");if(d)d.style.background=p.color;};
  col.onchange=()=>{p.color=col.value;save();render();};
  const ed=canEdit(p);nm.disabled=col.disabled=!ed;
  const gen=document.createElement("button");gen.textContent="Generate";gen.title="random name ("+(nameCulture(p.board)||"")+")";gen.disabled=!ed;
  gen.onclick=()=>{const n=genPlaceName(nameCulture(p.board));if(!n)return;p.name=n;save();render();renderList();};
  {const h=heraldOf(p,26);if(h){const w=document.createElement("span");w.className="pc-her";w.innerHTML=h;put(w);}}
  put(nm);put(gen);put(col);
  {const w=document.createElement("span");w.innerHTML=facSelectHTML();const fs=w.firstChild;fs.disabled=!ed;
    fs.onchange=e=>{setFaction(e.target.value);save();render();renderList();};put(fs);}
  {const w=document.createElement("span");w.innerHTML=culSelectHTML(p.board);const cs=w.firstChild;
    cs.onchange=e=>{p.board.culture=e.target.value||"";save();render();renderList();};put(cs);}
  {let on=false;try{on=!!SYNC.ready;}catch(e){}
    if(on){const cl=claimOf(p),mc=myClaimP(),b=document.createElement("button");b.dataset.claim="1";
      if(mine(p)){b.textContent="\u2605 yours \u00b7 release";b.onclick=()=>{if(!confirm("Release "+p.name+"?"))return;delete p.board.claim;if(TB().ready)delete TB().ready[p.id];save();render();};}
      else if(cl){b.textContent=ADMIN?"\ud83d\udd12 clear claim":"\ud83d\udd12 claimed";b.disabled=!ADMIN;
        if(ADMIN)b.onclick=()=>{if(!confirm("Clear the claim on "+p.name+"?"))return;delete p.board.claim;if(TB().ready)delete TB().ready[p.id];save();render();};}
      else{b.textContent="claim";if(mc){b.disabled=true;b.title="release "+mc.name+" first";}
        else b.onclick=()=>{p.board.claim={dev:DEV,ts:Date.now()};save();render();flash("you are "+p.name);};}
      put(b);}}
  if(D.players.length>1&&ed){const del=document.createElement("button");del.className="rm";del.textContent="✕ player";
    del.onclick=()=>{D.players.splice(D.active,1);D.active=0;reindex();save();render();renderList();};put(del);}
}
function toggleEmpty(k,n){const e=document.getElementById("e-"+k);if(e)e.style.display=n?"none":"block";
  const c=document.getElementById("c-"+k);if(c)c.textContent=n?("· "+n):"";}


// ---- settlement Σ: flat totals as header chips; the rest netted where parseable, clause text otherwise ----
// active pieces only, Mastery when earned (Infrastructure is empire-wide: not counted)
const SFX_NET=new Set(["envoy","act","defend","bandit","pool","cap","jester"]);
const SFX_GRP=["Seasonal","Envoys & Influence","Extort","Timers & Speed","Combat & Unlocks","Conditional & Other"];
const SFX_SEAS=/\bin (Winter|Spring|Summer|Fall)\b/i;
function sfxNorm(t){return String(t||"").toLowerCase().replace(/[^a-z0-9+\-]+/g," ").trim();}
function sfxLabel(f){const dm=f.dom&&f.dom!=="All"?f.dom:"";
  if(f.k==="envoy")return SCORE+" on "+(dm?dm+" Envoys":f.scope==="council"?"Council Envoys":f.scope==="personal"?"Personal Envoys":"all Envoys")+(f.noSpring?" (not Spring)":"");
  if(f.k==="act")return SCORE+" on your "+(dm?dm+" ":"")+"actions"+(f.tgtPOabove!=null?" vs Public Order above "+f.tgtPOabove:"");
  if(f.k==="defend")return SCORE+" on "+(f.dom||f.action||"")+" actions targeting you";
  if(f.k==="bandit")return SCORE+" on Bandit actions targeting you";
  if(f.k==="pool")return "Influence "+({Rising:"per Rising Domain",Established:"per Established Standing",others:"per other player",war:"while At War",holdings:"per "+f.n+" Holdings"}[f.per]||f.per);
  if(f.k==="cap")return "Influence spend cap per vote";
  if(f.k==="jester")return (f.n===1?"1st":"2nd")+" Oppose on your Envoy reduced by";
  return f.k;}
function settFx(occ,have,craft,tc){const acc={},net={},txt={};
  const add=(grp,label,val,src)=>{const k=grp+"|"+label,o=net[k]=net[k]||{grp,label,val:0,src:new Set()};o.val+=val;o.src.add(src);};
  const addT=(grp,t,src)=>{const k=grp+"|"+t,o=txt[k]=txt[k]||{grp,text:t,n:0,src:new Set()};o.n++;o.src.add(src);};
  occ.filter(pActive).forEach(p=>{const r=R[p.name];if(!r)return;const em=!!instStatus(p,r,have,craft,tc).earned;
    contribAcc(r,em,acc);
    const cov=[],tl=[];
    (r.innate_fx||[]).concat(em?(r.mastery_fx||[]):[]).forEach(f=>{if(!SFX_NET.has(f.k)||f.val==null)return;
      add("Envoys & Influence",sfxLabel(f),+f.val,p.name);cov.push(sfxNorm(f.t));});
    (r.innate||[]).concat(em&&r.mastery_raw?(r.mastery||[]):[]).forEach(a=>{if(a.cat==="natural")return;
      if(a.flat&&!a.season&&["gold","craft","faith","doubt","influence","upkeep"].includes(a.cat))return;      // header chips
      const nt=sfxNorm(a.text);if(nt&&cov.some(c=>c&&c.includes(nt)))return;                                  // netted from Envoy fx
      if(a.season&&a.val!=null&&a.cat==="gold"){add("Seasonal","Gold in "+a.season,a.val,p.name);return;}
      const sm=SFX_SEAS.exec(a.text||""),sx=sm?" in "+sm[1][0].toUpperCase()+sm[1].slice(1).toLowerCase():"";
      if(!a.cond&&a.val!=null){
        if(a.cat==="extort"&&a.every){add("Extort","Extort each Empire Phase",a.val,p.name);return;}
        if(a.cat==="build_timer"){add(sx?"Seasonal":"Timers & Speed","Build Timer"+sx,a.val,p.name);return;}
        if(a.cat==="siege_timer"){add(sx?"Seasonal":"Timers & Speed","Siege Timer"+sx,a.val,p.name);return;}
        if(a.cat==="speed"){add(sx?"Seasonal":"Timers & Speed","Speed"+sx,a.val,p.name);return;}}
      const t=dispScore(a.text||""),rw=dispScore((r.innate_raw||"")+" "+(r.mastery_raw||""));
      if(tl.length&&rw.includes(tl[tl.length-1].t+", "+t)){tl[tl.length-1].t+=", "+t;return;}   // comma-split tail ("…, to a minimum of 0") stays with its clause
      tl.push({g:a.cat==="combat"?"Combat & Unlocks":"Conditional & Other",t});});
    tl.forEach(x=>addT(x.g,x.t,p.name));});
  return {acc,net:Object.values(net).filter(o=>o.val),txt:Object.values(txt)};}
function settFxPanel(F){const el=document.createElement("div");el.className="sfx";
  const fv=(l,v)=>(v>0?"+":"\u2212")+(/^(Gold|Extort)/.test(l)?Math.abs(v).toLocaleString():Math.abs(v));
  const row=(a,b,src)=>'<div class="sfx-r"><span>'+esc(a)+'</span><b>'+b+'</b><i>'+esc([...src].join(", "))+'</i></div>';
  el.innerHTML=SFX_GRP.map(g=>{const n=F.net.filter(o=>o.grp===g),t=F.txt.filter(o=>o.grp===g);if(!n.length&&!t.length)return "";
    return '<div><div class="sfx-h">'+esc(g)+'</div>'+n.map(o=>row(o.label,fv(o.label,o.val),o.src)).join("")+
      t.map(o=>row(o.text,o.n>1?"\u00d7"+o.n:"",o.src)).join("")+'</div>';}).join("");
  return el;}
function renderPursuitBoard(earned,craft,tc,hideCombat,have){
  const host=document.getElementById("board-pursuit");host.innerHTML="";
  // settlement builder toolbar
  const tb=document.createElement("div");tb.className="settbuild";
  const sel=document.createElement("select");
  Object.keys(DATA.settlements).forEach(t=>{const o=document.createElement("option");o.value=t;
    o.textContent=t+" ("+DATA.settlements[t].wards+"w)";
    sel.appendChild(o);});
  const addB=document.createElement("button");addB.textContent="+ settlement";
  addB.onclick=()=>{
    const id=sid++;const ns={id,tier:sel.value};if(gameStarted()){const t=settBuildTime(sel.value);if(t>0)ns.bt=t;}S.settlements.push(ns);activeSid=id;autoFill();save();render();if(gameStarted()){const bn=buildNote(settBaseTime(sel.value));if(bn)flash(sel.value+bn);}};
  tb.appendChild(sel);tb.appendChild(addB);
  const exAll=document.createElement("button");exAll.textContent="expand all";exAll.dataset.nav="1";
  exAll.onclick=()=>{S.expanded=S.placed.map(p=>p.id);save();render();};
  const colAll=document.createElement("button");colAll.textContent="collapse all";colAll.dataset.nav="1";
  colAll.onclick=()=>{S.expanded=[];save();render();};
  tb.appendChild(exAll);tb.appendChild(colAll);
  const vt=document.createElement("button");vt.textContent=(D.pursuitView==="table")?"▤ cards":"▦ table";vt.dataset.nav="1";
  vt.title="toggle card / dense table view";
  vt.onclick=()=>{D.pursuitView=(D.pursuitView==="table")?"cards":"table";save();render();};
  tb.appendChild(vt);
  host.appendChild(tb);
  // board flags live in the top-bar Inbox (renderInbox)
  const facP=S.placed.filter(p=>p.sid==="faction");
  if(facP.length){const grp=document.createElement("div");grp.className="sgroup";
    const hd=document.createElement("div");hd.className="sgroup-hd";hd.innerHTML='<span class="stitle">Faction <span class="note">'+esc(S.faction||"")+'</span></span>';grp.appendChild(hd);
    const bd=document.createElement("div");bd.className="board";facP.forEach(p=>bd.appendChild(pursuitCard(p,earned,craft,tc,hideCombat,have)));grp.appendChild(bd);host.appendChild(grp);}
  const groups=[...S.settlements.map(s=>s.id), null];
  let any=false;
  groups.forEach(gid=>{
    const occ=S.placed.filter(p=>p.sid===gid);
    const unpEmpty=(gid==null&&!occ.length);
    any=any||occ.length>0||gid!=null;
    const closed=(S.settClosed||[]).includes(gid==null?"unplaced":gid);
    const key=(gid==null?"unplaced":gid);
    let SFX=null;
    const grp=document.createElement("div");grp.className="sgroup"+(gid===activeSid?" active":"")+(unpEmpty?" unp-empty":"");
    grp.dataset.dropSid=(gid==null?"none":gid);
    const hd=document.createElement("div");hd.className="sgroup-hd";
    const car=document.createElement("span");car.className="pcaret";car.style.cursor="pointer";car.textContent=closed?"▸":"▾";
    car.onclick=(e)=>{e.stopPropagation();S.settClosed=S.settClosed||[];const i=S.settClosed.indexOf(key);
      if(i<0)S.settClosed.push(key);else S.settClosed.splice(i,1);save();render();};
    hd.appendChild(car);
    if(gid!=null){
      const tier=settTier(gid),wu=wardUse(gid);
      const t=document.createElement("span");t.className="stitle";t.style.cursor="pointer";
      t.onclick=()=>{activeSid=gid;render();};
      const isCap=!!(S.settlements.find(x=>x.id===gid)||{}).capital;
      t.innerHTML=(gid===activeSid?"● ":"")+(isCap?"★ ":"")+tier+(((S.settlements.find(x=>x.id===gid)||{}).up)?" → "+S.settlements.find(x=>x.id===gid).up.to:"")+(isCap?' <span class="badge earn">Capital</span>':'')+' <span class="note">wards '+wu.used+'/'+wu.cap+(wu.free>0?' · <b style="color:var(--income)">'+wu.free+' empty</b>':'')+(wu.free<0?' · <b style="color:var(--upkeep)">'+(-wu.free)+' over</b>':'')+' · '+occ.length+' pursuits'+(wu.typeBad?' · <span style="color:var(--upkeep)">type!</span>':'')+(tier==="Hamlet"?' · Natural only':'')+'</span>';
      hd.appendChild(t);
      {const wc=document.createElement("span");wc.className="wchips";const W=wardChains(gid),fr=Math.max(0,wu.free);   // one chip per Ward: its front Holding (+ riders sharing it), or open
        wc.innerHTML=W.map(w=>'<span class="wchip'+(w.front.bt>0||w.front.dmg>0?' off':'')+'" title="'+esc(w.chain.map(x=>x.name).join(" ← "))+'">'+esc(w.front.name)+(w.chain.length>1?' <i>+'+(w.chain.length-1)+'</i>':'')+'</span>').join("")+
          Array.from({length:fr},()=>'<span class="wchip open" data-nav="1">open</span>').join("");
        wc.querySelectorAll(".wchip.open").forEach((c,i)=>c.onclick=e=>{e.stopPropagation();wardPick(gid,W.length+i);});
        hd.appendChild(wc);}
      {const so=S.settlements.find(x=>x.id===gid),ni=document.createElement("input");ni.className="snm";ni.placeholder="name";ni.value=(so&&so.name)||"";ni.title="Settlement name";
        ni.onclick=e=>e.stopPropagation();ni.onchange=()=>{if(so){so.name=ni.value.trim()||undefined;if(!so.name)delete so.name;save();render();}};hd.appendChild(ni);
        if(so&&PN){const gb=document.createElement("button");gb.className="shb";gb.textContent="Generate";gb.title="random name ("+(nameCulture(S)||"")+")";
          gb.onclick=e=>{e.stopPropagation();const nm=genPlaceName(nameCulture(S));if(nm){so.name=nm;save();render();}};hd.appendChild(gb);}}
      {const so=S.settlements.find(x=>x.id===gid);if(so&&so.bt>0)hd.appendChild(timerCtl("build",so.bt,d=>{so.bt=Math.max(0,so.bt+d);if(!so.bt)settFinish(playerOfBoard(S),so);save();render();}));}
      SFX=settFx(occ,have,craft,tc);
      {const ch=accChips(SFX.acc);if(ch.children.length){const w=document.createElement("span");w.className="stot";
        const l=document.createElement("span");l.className="lbl";l.textContent="\u03a3";w.appendChild(l);w.appendChild(ch);hd.appendChild(w);}}
      {const nx=SFX.net.length+SFX.txt.length;if(nx){const op=(S.settFx||[]).includes(gid),fb=document.createElement("button");fb.className="shb";fb.dataset.nav="1";
        fb.textContent=(op?"\u25be":"\u25b8")+" effects "+nx;
        fb.onclick=e=>{e.stopPropagation();S.settFx=S.settFx||[];const i=S.settFx.indexOf(gid);if(i<0)S.settFx.push(gid);else S.settFx.splice(i,1);save();render();};
        hd.appendChild(fb);}}
      const cb=document.createElement("button");cb.className="shb";cb.style.marginLeft="auto";cb.textContent=isCap?"★ capital":"☆ capital";
if(isCap)cb.style.color="var(--income)";
      cb.onclick=(e)=>{e.stopPropagation();if(isCap){flash("every player has a capital — set another to move it");return;}
        setCapital(gid);save();render();};
      hd.appendChild(cb);
      const nt=(S.settlements.find(x=>x.id===gid)||{}).up?null:nextTier(tier);
      if(nt){
        const ex=document.createElement("button");ex.className="shb";ex.textContent="▲ "+nt;ex.title="expand to "+nt;
        ex.onclick=(e)=>{e.stopPropagation();
          const s=S.settlements.find(x=>x.id===gid);settExpand(playerOfBoard(S),s,nt);autoFill();save();render();if(gameStarted()){const bn=buildNote(settBaseTime(nt));if(bn)flash(nt+bn);}};
        hd.appendChild(ex);
      }
      const del=document.createElement("button");del.className="rm shb";del.textContent="✕";del.title="remove settlement";
      del.onclick=(e)=>{e.stopPropagation();occ.forEach(p=>p.sid=null);S.settlements=S.settlements.filter(s=>s.id!==gid);
        if(activeSid===gid)activeSid=S.settlements[0]?S.settlements[0].id:null;save();render();};
      hd.appendChild(del);
    } else {
      const t=document.createElement("span");t.className="stitle";
      t.innerHTML='Unplaced <span class="note">('+occ.length+')</span>';
      hd.appendChild(t);
    }
    grp.appendChild(hd);
    if(!closed&&gid!=null&&SFX&&(SFX.net.length+SFX.txt.length)&&(S.settFx||[]).includes(gid))grp.appendChild(settFxPanel(SFX));
    if(!closed){
      if((D.pursuitView||"cards")==="table"){
        grp.appendChild(pursuitTable(occ,earned,craft,tc,hideCombat,have));
      } else if(gid!=null){
        grp.appendChild(wardGrid(gid,occ,earned,craft,tc,hideCombat,have));
      } else {
        const board=document.createElement("div");board.className="board";
        occ.sort((a,b)=>R[a.name].type.localeCompare(R[b.name].type)||a.name.localeCompare(b.name));
        occ.forEach(p=>board.appendChild(pursuitCard(p,earned,craft,tc,hideCombat,have)));
        grp.appendChild(board);
      }
    }
    host.appendChild(grp);
  });
  document.getElementById("e-pursuit").style.display=S.placed.length?"none":"block";
  document.getElementById("c-pursuit").textContent=S.placed.length?("· "+S.placed.length):"";
}

// piles: each ward-consuming pursuit is a pile root; its efficient rider chain stacks on top (chains, not branches)
function wardPiles(occ){
  const exempt=exemptionsOf(occ), riderOf={};
  occ.forEach(o=>{if(exempt.has(o.id))riderOf[exempt.hostOf[o.id]]=o;});
  const used=new Set(), piles=[];
  occ.filter(o=>!exempt.has(o.id))
     .sort((a,b)=>R[a.name].type.localeCompare(R[b.name].type)||a.name.localeCompare(b.name))
     .forEach(root=>{const pile=[root];used.add(root.id);let cur=root;
       while(riderOf[cur.name]&&!used.has(riderOf[cur.name].id)){cur=riderOf[cur.name];used.add(cur.id);pile.push(cur);}
       piles.push(pile);});
  occ.filter(o=>!used.has(o.id)).forEach(o=>piles.push([o]));   // safety: orphaned riders
  return piles;
}
function wardGrid(gid,occ,earned,craft,tc,hideCombat,have){
  const wu=wardUse(gid), piles=wardPiles(occ), n=Math.max(wu.cap,piles.length);
  const grid=document.createElement("div");grid.className="wards";
  for(let i=0;i<n;i++){
    const w=document.createElement("div");w.className="ward";w.dataset.dropSid=gid;const pile=piles[i];
    const lbl=document.createElement("div");lbl.className="ward-lbl";
    lbl.innerHTML='<span>Ward '+(i+1)+(i>=wu.cap?' · over cap':'')+'</span>'+(pile&&pile.length>1?'<span>⚡ '+(pile.length-1)+' stacked</span>':'');
    w.appendChild(lbl);
    if(i>=wu.cap)w.classList.add("over");
    if(!pile){
      w.classList.add("empty");
      const e=document.createElement("div");e.className="emp";e.textContent="+";w.appendChild(e);
      w.onclick=()=>wardPick(gid,i);
    } else {
      const pl=document.createElement("div");pl.className="pile";
      pile.forEach((p,j)=>{const pc=document.createElement("div");pc.className="pc"+(j<pile.length-1?" buried":"");
        pc.style.zIndex=j+1;pc.dataset.pid=p.id;pc.appendChild(pursuitCard(p,earned,craft,tc,hideCombat,have));pl.appendChild(pc);});
      w.appendChild(pl);
    }
    grid.appendChild(w);
  }
  return grid;
}
// ---- drag & drop (pointer events: mouse + touch) ----
// grab a pile's root → whole pile moves; grab any other card → just that card.
// drop on a card → ride it (must be efficient with it; replaces its current rider).
// drop on a ward / settlement → move in.  Riders that lose their stack keep a ward if free, else → Unplaced.
function unitFor(inst){
  if(inst.sid==null)return [inst];
  const pl=wardPiles(occupants(inst.sid)).find(p=>p[0].id===inst.id);
  return pl?pl.slice():[inst];
}
function tryMove(unit,t,commit){
  const snap=S.placed.map(p=>[p,p.sid,p.ride,p.rideOn]);
  const restore=()=>snap.forEach(([p,sd,r,ro])=>{p.sid=sd;p.ride=r;p.rideOn=ro;});
  const ids=new Set(unit.map(u=>u.id)),root=unit[0],src=root.sid;
  let onto=null,displaced=null,tsid;
  if(t.kind==="card"){
    onto=S.placed.find(p=>p.id===t.pid);
    if(!onto||ids.has(onto.id)||onto.sid==null)return {ok:false,why:""};
    if(!effList(root.name).includes(onto.name))return {ok:false,why:root.name+" is not efficient with "+onto.name};
    tsid=onto.sid;
    const ex=exemptionsOf(occupants(tsid));
    displaced=occupants(tsid).find(o=>ex.has(o.id)&&ex.hostOf[o.id]===onto.name&&!ids.has(o.id))||null;
  } else {
    tsid=t.sid==="none"?null:+t.sid;
    if(tsid===src)return {ok:false,why:""};
  }
  const before={};[src,tsid].forEach(x=>{if(x!=null)before[x]=exemptionsOf(occupants(x));});
  unit.forEach(u=>u.sid=tsid);
  if(onto){root.ride=1+Math.max(0,...S.placed.map(p=>p.ride||0));root.rideOn=onto.name;if(displaced){displaced.ride=0;delete displaced.rideOn;}}
  else{root.ride=(tsid==null?0:-1);delete root.rideOn;}           // plain move never steals an existing rider's slot
  const evicted=[];
  for(const x of [tsid,src]){if(x==null)continue;let guard=200;
    while(wardUse(x).free<0&&guard--){
      const ex=exemptionsOf(occupants(x));
      const c=occupants(x).filter(o=>!ex.has(o.id)&&!ids.has(o.id));
      const pick=c.find(o=>displaced&&o.id===displaced.id)||c.find(o=>before[x]&&before[x].has(o.id));
      if(!pick){restore();return {ok:false,why:"no free ward in "+settTier(x)};}
      pick.sid=null;pick.ride=0;evicted.push(pick.name);
    }}
  if(!commit)restore();
  return {ok:true,evicted,displaced:displaced?displaced.name:null,to:tsid==null?"Unplaced":settTier(tsid)};
}
let DRAG=null;
function scrollHost(el){for(let e=el;e&&e!==document.body;e=e.parentElement){const cs=getComputedStyle(e);if(/(auto|scroll)/.test(cs.overflowY)&&e.scrollHeight>e.clientHeight)return e;}return null;}
function dropTargetAt(x,y){
  const el=document.elementFromPoint(x,y);if(!el)return null;
  const pc=el.closest(".ward [data-pid]");
  if(pc)return {kind:"card",pid:+pc.dataset.pid,el:pc.firstElementChild||pc};
  const w=el.closest("[data-drop-sid]");
  if(w)return {kind:"sett",sid:w.dataset.dropSid,el:w};
  return null;
}
function clearDropHL(){document.querySelectorAll(".drop-ok,.drop-bad").forEach(e=>e.classList.remove("drop-ok","drop-bad"));}
function armDrag(handle,inst,threshold){
  handle.addEventListener("pointerdown",ev=>{
    if(ev.button!==0)return;
    if(threshold&&ev.pointerType!=="mouse")return;           // header drag = mouse only; touch uses the grip
    if(ev.target.closest("button,select,input")||(threshold&&ev.target.closest(".grip")))return;
    const sx=ev.clientX,sy=ev.clientY;let started=false;
    if(!threshold){ev.preventDefault();}
    const move=e=>{
      if(!started){if(Math.hypot(e.clientX-sx,e.clientY-sy)<threshold)return;started=true;beginDrag(inst,handle,e);}
      e.preventDefault();dragMove(e.clientX,e.clientY);};
    const up=e=>{window.removeEventListener("pointermove",move);window.removeEventListener("pointerup",up);window.removeEventListener("pointercancel",cancel);
      if(started){handle._suppressClick=true;setTimeout(()=>handle._suppressClick=false,0);dragEnd(true);}};
    const cancel=()=>{window.removeEventListener("pointermove",move);window.removeEventListener("pointerup",up);window.removeEventListener("pointercancel",cancel);if(started)dragEnd(false);};
    window.addEventListener("pointermove",move,{passive:false});window.addEventListener("pointerup",up);window.addEventListener("pointercancel",cancel);
    if(!threshold){started=true;beginDrag(inst,handle,ev);dragMove(ev.clientX,ev.clientY);}
  });
}
function beginDrag(inst,handle,ev){
  const unit=unitFor(inst);
  const ghost=document.createElement("div");ghost.className="dragghost";
  ghost.innerHTML=unit.map((u,i)=>'<div class="gl"'+(i?' style="margin-left:'+(i*8)+'px"':'')+'>'+esc(u.name)+'</div>').join("")+'<div class="gw"></div>';
  document.body.appendChild(ghost);document.body.classList.add("dnd");
  const srcEl=handle.closest(".pile")&&unit.length>1?handle.closest(".pile"):(handle.closest(".pc")||handle.closest(".card"));
  if(srcEl)srcEl.classList.add("dragging");
  DRAG={unit,ghost,srcEl,t:null,res:null,x:ev.clientX,y:ev.clientY,sc:scrollHost(document.getElementById("board-pursuit")),raf:0};
  const loop=()=>{if(!DRAG)return;const h=DRAG.sc,y=DRAG.y,E=60,sp=14;
    if(h){const r=h.getBoundingClientRect();if(y<r.top+E)h.scrollTop-=sp;else if(y>r.bottom-E)h.scrollTop+=sp;}
    if(y<E)window.scrollBy(0,-sp);else if(y>window.innerHeight-E)window.scrollBy(0,sp);
    DRAG.raf=requestAnimationFrame(loop);};
  DRAG.raf=requestAnimationFrame(loop);
}
function dragMove(x,y){
  if(!DRAG)return;DRAG.x=x;DRAG.y=y;
  DRAG.ghost.style.left=(x+12)+"px";DRAG.ghost.style.top=(y+10)+"px";
  const t=dropTargetAt(x,y),key=t?(t.kind+":"+(t.pid||t.sid)):"";
  if(key===(DRAG.key||""))return;DRAG.key=key;DRAG.t=t;clearDropHL();
  const gw=DRAG.ghost.querySelector(".gw");
  if(!t){DRAG.res=null;gw.textContent="";return;}
  const r=tryMove(DRAG.unit,t,false);DRAG.res=r;
  t.el.classList.add(r.ok?"drop-ok":"drop-bad");
  gw.textContent=r.ok?("→ "+(t.kind==="card"?"ride "+(S.placed.find(p=>p.id===t.pid)||{}).name:r.to)+(r.displaced?" · "+r.displaced+" bumped":"")+(r.evicted.length?" · to Unplaced: "+r.evicted.join(", "):"")):r.why;
  gw.className="gw "+(r.ok?"ok":"bad");
}
function dragEnd(drop){
  if(!DRAG)return;const d=DRAG;DRAG=null;cancelAnimationFrame(d.raf);
  d.ghost.remove();document.body.classList.remove("dnd");clearDropHL();if(d.srcEl)d.srcEl.classList.remove("dragging");
  if(drop&&d.t&&d.res&&d.res.ok){const r=tryMove(d.unit,d.t,true);save();render();
    if(r.ok&&(r.evicted.length||r.displaced))flash((r.displaced?r.displaced+" bumped":"")+(r.evicted.length?(r.displaced?" · ":"")+"to Unplaced: "+r.evicted.join(", "):""));}
  else if(drop&&d.res&&!d.res.ok&&d.res.why)flash(d.res.why);
}
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&DRAG)dragEnd(false);});
// ---- factions ----
const FAC=DATA.factions||{};
function factionFree(fn){const f=FAC[fn];if(!f)return [];const out=[],re=/begin the game with (?:an? )?([^(.;]+?)\s*\((?:no Ward|no upkeep)/gi;let m;
  while((m=re.exec(f.mechanic))){const n=m[1].trim().replace(/\s+Raw-Material Pursuit$/i,"").replace(/\s+Pursuit$/i,"");
    if(R[n])out.push({kind:"pursuit",name:n});else if(INFRA[n])out.push({kind:"infra",name:n});else if(WON[n])out.push({kind:"wonder",name:n});}
  return out;}
function setFaction(fn){itm();
  S.placed=S.placed.filter(p=>!p.fac);
  S.facInfra.forEach(n=>{delete S.infra[n];delete S.wonders[n];});S.facInfra=[];
  S.faction=fn||"";
  factionFree(fn).forEach(x=>{if(x.kind==="pursuit")S.placed.push({id:pid++,name:x.name,sid:"faction",fac:true});
    else{(x.kind==="infra"?S.infra:S.wonders)[x.name]=1;S.facInfra.push(x.name);}});
}
// Faction gear rules read from the mechanic text (flags, never blocks): "must always equip a ranged weapon",
// "can't equip <armor>[ or <armor>]", "can't use shields".
function facGearFlags(a){const f=FAC[S.faction||""];if(!f)return [];const t=String(f.mechanic||""),out=[],lc=t.toLowerCase();
  if(/must always (?:equip|have) a ranged weapon/i.test(t)&&(!a.ranged||a.ranged==="None"))out.push(S.faction+": must equip a Ranged weapon");
  const m=t.match(/can't equip ([^.;]+)/i),ban=m?m[1].split(/,\s*(?:or\s+)?|\s+or\s+/).map(x=>x.trim().toLowerCase()).filter(Boolean):[];
  if(a.armor&&a.armor!=="Cloth"&&ban.some(x=>x!=="shields"&&x.includes(String(a.armor).toLowerCase())))out.push(S.faction+": can't equip "+a.armor);
  if((/can't use shields/i.test(t)||ban.includes("shields"))&&a.shield&&a.shield!=="None")out.push(S.faction+": can't use Shields");
  return out;}
function factionFlags(){const f=FAC[S.faction];if(!f)return [];const out=[];
  const types=[...new Set(Object.values(R).map(r=>r.type))];
  f.mechanic.split(/(?<=[.;])\s+/).forEach(sen=>{
    // "can't … build Holdings that require <Domain>[ or <Domain>] Standing": flag Holdings whose unlock names that Domain
    const sd=sen.match(/can't\b[^.]*\bbuild (?:Holdings|Pursuits) that require (\w+)(?:,? or (\w+))? Standing/i);
    if(sd){const ds=[sd[1],sd[2]].filter(Boolean);S.placed.filter(p=>!p.fac).forEach(p=>{const u=(R[p.name]||{}).unlock_raw||"";
      if(ds.some(d=>u.includes(d)))out.push(S.faction+": "+p.name+" — "+sen.trim());});return;}
    if(!/can't (pursue|build)/i.test(sen))return;
    S.placed.filter(p=>!p.fac).forEach(p=>{const r=R[p.name];
      if(sen.includes(p.name)||types.some(t=>t===r.type&&new RegExp("\\b"+t+" (?:Pursuits|Holdings)","i").test(sen)))out.push(S.faction+": "+p.name+" — "+sen.trim());});});
  return out;}
function facSelectHTML(){const names=Object.keys(FAC),fin=names.filter(n=>FAC[n].final),oth=names.filter(n=>!FAC[n].final);
  const opt=n=>'<option value="'+esc(n)+'"'+(n===S.faction?' selected':'')+'>'+esc(n)+'</option>';
  return '<select id="facSel" class="facsel" title="faction"><option value="">— faction —</option><optgroup label="Final cut">'+fin.map(opt).join('')+'</optgroup>'+
    (oth.length?'<optgroup label="Other">'+oth.map(opt).join('')+'</optgroup>':'')+'</select>';}
// ---- Culture (view filter, no game effect) + generated Settlement names ----
const CUL=DATA.cultures||{},CUL_SELF=DATA.cultureSelf||"Self-made",PN=DATA.placeNames||null,CUL_DOMS=["Industry","Prowess","Cunning","Piety"];
function culSelectHTML(b){const by={};Object.keys(CUL).forEach(n=>{const t=CUL[n].type||"";(by[t]=by[t]||[]).push(n);});
  const cur=(b&&b.culture&&CUL[b.culture])?b.culture:"";
  return '<select id="culSel" class="facsel" title="culture — focuses the Holding catalog and tree; no game effect"><option value="">'+esc(CUL_SELF)+'</option>'+
    Object.keys(by).map(t=>'<optgroup label="'+esc(t)+'">'+by[t].map(n=>'<option value="'+esc(n)+'"'+(n===cur?' selected':'')+'>'+esc(n)+' · '+esc(CUL[n].domains.join("/"))+'</option>').join("")+'</optgroup>').join("")+'</select>';}
function cultureOf(b){return b&&b.culture&&CUL[b.culture]?b.culture:null;}
function holdDom(n){const u=(R[n]||{}).unlock_raw||"";return CUL_DOMS.find(d=>u.includes(d))||"";}
// the Holdings a culture focuses on: unlocks in its Domains, Domain-free Holdings (Raw Materials, Common Land…),
// its Monuments and every Holding on their chains
const CUL_SET={};
function cultureSet(c){if(!c||!CUL[c])return null;if(CUL_SET[c])return CUL_SET[c];const C=CUL[c],ds=new Set(C.domains),out=new Set();
  NAMES.forEach(n=>{const d=holdDom(n);if(!d||ds.has(d))out.add(n);});
  const seen=new Set(),up=n=>{if(seen.has(n))return;seen.add(n);out.add(n);effList(n).forEach(up);};
  C.monuments.filter(n=>R[n]).forEach(up);
  return CUL_SET[c]=out;}
function cultureKeep(n,b){const c=cultureOf(b||S);if(!c)return true;return cultureSet(c).has(n);}
function cultureKeepWonder(n,b){const c=cultureOf(b||S);if(!c||!WON[n])return true;const W=CUL[c].wonders||[];return !W.length||W.includes(n);}
// Self-made names follow the culture its Domain Standings match: the Domains at its highest value
function derivedCulture(b){const dv=(b&&b.domains)||{},mx=Math.max(...CUL_DOMS.map(d=>+dv[d]||0)),top=CUL_DOMS.filter(d=>(+dv[d]||0)===mx).sort().join("|");
  return Object.keys(CUL).find(n=>CUL[n].domains.slice().sort().join("|")===top)||null;}
function nameCulture(b){return cultureOf(b)||derivedCulture(b)||Object.keys(CUL).find(n=>CUL[n].type==="centre")||Object.keys(PN?PN.banks:{})[0];}
function usedSettNames(){const s=new Set();(D.players||[]).forEach(p=>(p.board.settlements||[]).forEach(x=>{if(x.name)s.add(x.name);}));return s;}
function genPlaceName(cul){if(!PN||!PN.banks)return "";const ex=new Set((PN.exclude||[]).concat([...usedSettNames()])),pick=L=>L[Math.floor(Math.random()*L.length)];let nm="";
  for(let t=0;t<60;t++){let B=PN.banks[cul]||PN.banks[pick(Object.keys(PN.banks))],pat=pick(B.patterns);
    if(pat==="@borrow"){B=PN.banks[pick(B.borrow)]||B;pat=pick(B.patterns.filter(x=>x!=="@borrow"));}
    nm=pat.replace(/\{(\w+)\}/g,(_,k)=>pick(B[k]||[""]));nm=(nm.charAt(0).toUpperCase()+nm.slice(1)).replace(/s's\b/g,"s'");
    if(!ex.has(nm))return nm;}
  return nm;}
function nameSett(p,s){if(!s||s.name||!PN)return;const nm=genPlaceName(nameCulture(p.board));if(nm)s.name=nm;}
function renderFaction(){const box=document.getElementById("facBox");if(!box)return;const f=FAC[S.faction];
  box.style.display=f?"":"none";
  const was=box.querySelector("details"),open=was?was.open:false;
  box.innerHTML=f?'<details'+(open?' open':'')+'><summary><b>'+esc(S.faction)+'</b> <span class="note">Difficulty '+esc(f.difficulty)+' · Strength '+esc(f.strength)+'</span></summary>'+
    '<div class="fm">'+esc(f.body||f.mechanic)+'</div><div class="fk">'+(f.feel?esc(f.feel):'')+
      (f.pair?'<br>Pair: '+esc(f.pair):'')+(f.complement?'<br>Complement: '+esc(f.complement):'')+'</div></details>':'';
}
function timerCtl(kind,n,step){
  const w=document.createElement("span");w.className="badge noearn tmr";w.onclick=e=>e.stopPropagation();
  const m=document.createElement("button");m.textContent="−";m.onclick=e=>{e.stopPropagation();step(-1);};
  const pl=document.createElement("button");pl.textContent="+";pl.onclick=e=>{e.stopPropagation();step(1);};
  w.appendChild(document.createTextNode(kind+" "));w.appendChild(m);w.appendChild(document.createTextNode(" "+n+" "));w.appendChild(pl);return w;}
function placementSelect(inst){
  const n=inst.name, psel=document.createElement("select");psel.style.fontSize="11px";
  const uo=document.createElement("option");uo.value="";uo.textContent="Unplaced";psel.appendChild(uo);
  // SIMPLE: each faction pursuit is its own Ward — efficient pursuits can be built onto it (riders only)
  if(SIMPLE&&S.placed.some(p=>p.fac)){const fo=document.createElement("option");fo.value="faction";
    const c=canPlace(n,"faction");fo.textContent="Faction"+(c.ok||inst.sid==="faction"?"":" (not efficient with a faction piece)");psel.appendChild(fo);}
  S.settlements.forEach(s=>{const c=canPlace(n,s.id);const o=document.createElement("option");
    o.value=s.id;const wu=wardUse(s.id);
    o.textContent=(s.capital?"★ ":"")+s.tier+" ("+wu.used+"/"+wu.cap+")";
    psel.appendChild(o);});
  psel.value=inst.sid==null?"":String(inst.sid);
  psel.onchange=()=>moveInstance(inst.id, psel.value===""?null:psel.value==="faction"?"faction":+psel.value);
  return psel;
}
// flat, unconditional, non-seasonal atoms only (the same rule as the headline totals)
function contribAcc(r,masteryEarned,acc){acc=acc||{};
  const addA=(atoms,act)=>{if(!act)return;atoms.forEach(a=>{if(a.flat&&!a.season&&["gold","craft","faith","doubt","influence","upkeep"].includes(a.cat))acc[a.cat]=(acc[a.cat]||0)+a.val;});};
  addA(r.innate,true); if(r.mastery_raw)addA(r.mastery,masteryEarned);return acc;}
function contribChips(r,masteryEarned){return accChips(contribAcc(r,masteryEarned));}
function accChips(acc){
  const wrap=document.createElement("div");wrap.className="atoms";
  ["gold","upkeep","craft","influence","faith","doubt"].forEach(catk=>{
    if(!acc[catk])return;const ph=PHASE[catk],col=cvar(PHASE_COLOR[ph]);
    const s=document.createElement("span");s.className="atom";s.style.borderColor=col;s.style.color=col;
    s.textContent=(catk==="gold"?"":cap(catk)+" ")+(acc[catk]>0?"+":"")+acc[catk];wrap.appendChild(s);});
  return wrap;
}
function pursuitDetail(r,hideCombat,me,inst,have,craft,tc){
  const wrap=document.createElement("div");
  const bi=document.createElement("div");bi.className="block";bi.innerHTML='<div class="lbl">'+(SIMPLE?"EFFECT":"INNATE")+'</div>';
  bi.appendChild(atomsBlock(r.innate,hideCombat));
  wrap.appendChild(bi);
  if(SIMPLE&&inst){const rh=simpleReqHTML(inst,simpleReq(inst,r,have,craft,tc));if(rh){const b=document.createElement("div");b.className="block";b.innerHTML=rh;wrap.appendChild(b);}}
  const bm=document.createElement("div");bm.className="block mastery"+(r.mastery_raw?(me.earned?" on":" off"):"");
  const badge=r.mastery_raw?('<span class="badge '+(me.earned?"earn":"noearn")+'">'+(me.earned?"earned ✓":"not earned ✗")+'</span>'):'<span class="badge nomast">none</span>';
  bm.innerHTML='<div class="lbl">MASTERY<span class="sp"></span>'+badge+'</div>';
  if(r.mastery_raw){
    const ab=atomsBlock(r.mastery,hideCombat);if(!me.earned)ab.style.opacity=".5";bm.appendChild(ab);
    if(r.mreq_raw){const rq=document.createElement("div");rq.className="req";rq.innerHTML="req: "+kwify(r.mreq_raw,r.name);bm.appendChild(rq);}
    {const ih=masteryInfraHTML(r);if(ih){const d=document.createElement("div");d.innerHTML=ih;bm.appendChild(d);}}
    if(!me.earned){const mm=document.createElement("div");mm.className="miss";mm.textContent="missing: "+missTxt(me.missing);bm.appendChild(mm);}
  }
  if(!(SIMPLE&&!r.mastery_raw))wrap.appendChild(bm);
  const bl=nextLinksHTML(r);if(bl){const b=document.createElement("div");b.className="block";b.innerHTML=bl;wrap.appendChild(b);}
  return wrap;
}
// "builds into" / "Mastery for" chips: ✓ built, 🔒 unlock not met (flags only)
let NX_OPEN=true;try{NX_OPEN=localStorage.getItem("renown_nx_open")!=="0";}catch(e){}
document.addEventListener("click",e=>{const sm=e.target.closest("details.nxd > summary");if(!sm)return;NX_OPEN=!sm.parentElement.open;
  try{localStorage.setItem("renown_nx_open",NX_OPEN?"1":"0");}catch(_){}
  document.querySelectorAll("details.nxd").forEach(d=>{if(d!==sm.parentElement)d.open=NX_OPEN;});});
function quickChip(n){const have=(PC[n]||0)>0,us=unlockStatus(n);
  if(have)return '<span class="qchip have" title="on your board">\u2713 '+esc(n)+'</span>';
  return '<button class="qchip'+(us.ok?'':' lock')+'" data-addp="'+esc(n)+'" title="add '+esc(n)+' to your board'+
    (us.ok?'':'\nUnlock not met: '+esc((R[n]||{}).unlock_raw||""))+'">+ '+esc(n)+'</button>';}
function buildsIntoRow(r){const bi=r.builds_into||[];if(!bi.length)return "";
  return '<div class="qrow"><span class="lbl">BUILDS INTO</span>'+bi.map(quickChip).join("")+'</div>';}
function nextLinksHTML(r){const chip=n=>{const have=(PC[n]||0)>0,us=unlockStatus(n),i=GK_BY[esc(n)];
    return '<span class="nx'+(have?' have':'')+'"'+(us.ok?'':' title="Unlock not met: '+esc((R[n]||{}).unlock_raw||"")+'"')+'>'+(have?'✓ ':(us.ok?'':'🔒 '))+
      (i!=null?'<span class="gk" data-gk="'+i+'">'+esc(n)+'</span>':esc(n))+(have?'':' <button class="nxadd" data-addp="'+esc(n)+'" title="add '+esc(n)+' to your board">+</button>')+'</span>';};
  const bi=r.builds_into||[],mf=(r.mastery_for||[]).filter(x=>!bi.includes(x));
  if(!bi.length&&!mf.length)return "";
  return '<div class="lbl">BUILDS INTO</div>'+(bi.length?'<div class="nxrow">'+bi.map(chip).join("")+'</div>':'<div class="note">—</div>')+
    (mf.length?'<div class="lbl" style="margin-top:4px">MASTERY NEEDED BY</div><div class="nxrow">'+mf.map(chip).join("")+'</div>':'');}
// dense row-per-pursuit table for one settlement group
function pursuitTable(occ,earned,craft,tc,hideCombat,have){
  occ.sort((a,b)=>R[a.name].type.localeCompare(R[b.name].type)||a.name.localeCompare(b.name));
  const tbl=document.createElement("table");tbl.className="dtable ptable";
  tbl.innerHTML='<thead><tr><th>Pursuit</th><th>Type</th><th>Contribution</th><th>'+(SIMPLE?"Req":"Mastery")+'</th><th>Ward</th><th>Place</th><th></th></tr></thead>';
  const tb=document.createElement("tbody");
  occ.forEach(inst=>{
    const n=inst.name,r=R[n],me=instStatus(inst,r,have,craft,tc),open=S.expanded.includes(inst.id);
    const tr=document.createElement("tr");
    const c1=document.createElement("td");c1.style.cursor="pointer";
    c1.innerHTML='<span class="pcaret">'+(open?"▾":"▸")+'</span> '+esc(n)+(r.monument?' <span class="badge mon">M</span>':'');
    c1.onclick=()=>{const i=S.expanded.indexOf(inst.id);if(i<0)S.expanded.push(inst.id);else S.expanded.splice(i,1);save();render();};
    const c2=document.createElement("td");c2.className="note";c2.textContent=r.type;
    const c3=document.createElement("td");c3.appendChild(contribChips(r,me.earned));
    const c4=document.createElement("td");
    if(SIMPLE){const sr=simpleReq(inst,r,have,craft,tc);c4.innerHTML='<span class="badge '+(sr.ok?"earn":"noearn")+'">'+(sr.ok?"✓":"✗")+'</span>';if(!sr.ok)c4.title=sr.missing.join("\n");}
    else c4.innerHTML=r.mastery_raw?('<span class="badge '+(me.earned?"earn":"noearn")+'">'+(me.earned?"✓":"✗")+'</span>'):'<span class="note">—</span>';
    if(!SIMPLE&&!me.earned&&me.missing.length)c4.title="missing: "+missTxt(me.missing);
    const c5=document.createElement("td");c5.innerHTML=(inst.sid!=null&&isFreeRider(inst))?'<span class="badge earn" title="'+CHAINL+' rider">⚡</span>':'<span class="note">·</span>';
    const c6=document.createElement("td");c6.appendChild(placementSelect(inst));
    const c7=document.createElement("td");const rm=document.createElement("button");rm.className="rm";rm.textContent="✕";rm.onclick=()=>removeInstance(inst.id);c7.appendChild(rm);
    [c1,c2,c3,c4,c5,c6,c7].forEach(td=>tr.appendChild(td));tb.appendChild(tr);
    if(open){const dr=document.createElement("tr");const dc=document.createElement("td");dc.colSpan=7;
      dc.appendChild(pursuitDetail(r,hideCombat,me,inst,have,craft,tc));dr.appendChild(dc);tb.appendChild(dr);}
  });
  tbl.appendChild(tb);return tbl;
}

function pursuitCard(inst,earned,craft,tc,hideCombat,have){
  const n=inst.name, r=R[n], me=instStatus(inst,r,have,craft,tc);
  const open=S.expanded.includes(inst.id);
  const card=document.createElement("div");card.className="card";
  card.style.borderLeftColor=cvar(PHASE_COLOR[PHASE[(r.innate[0]||{}).cat]||"other"]);
  const h=document.createElement("h3");h.style.cursor="pointer";h.dataset.nav="1";
  if(!inst.fac){const grip=document.createElement("span");grip.className="grip";grip.textContent="⋮⋮";
    grip.onclick=e=>e.stopPropagation();h.appendChild(grip);armDrag(grip,inst,0);armDrag(h,inst,6);}
  const car=document.createElement("span");car.className="pcaret";car.textContent=open?"▾":"▸";h.appendChild(car);
  const nm=document.createElement("span");nm.className="nm";nm.textContent=n;h.appendChild(nm);
  if(r.monument){const b=document.createElement("span");b.className="badge mon";b.textContent="Monument";h.appendChild(b);}
  const mFlag=r.mastery_raw?flagState("m:"+inst.id,!me.earned,(me.missing||[]).join("|")):"off";
  if(r.mastery_raw&&mFlag!=="ignored"){const b=document.createElement("span");b.className="badge "+(me.earned?"earn":"noearn");b.textContent=me.earned?"✓":"✗";h.appendChild(b);}
  if(!inst.fac){const us=unlockStatus(n),uf=flagState("u:"+inst.id,!us.ok,us.missing.join("|"));
    if((!us.ok&&uf==="on")||(us.ok&&us.manual)){const b=document.createElement("span");b.className="badge "+(us.ok?"":"noearn");
    b.textContent=us.ok?"unlock ?":"unlock ✗";b.title="Unlock: "+r.unlock_raw+"\n"+us.toks.map(x=>(x.ok===false?"✗ ":x.ok?"✓ ":"? ")+x.t+" — "+x.why).join("\n");h.appendChild(b);
    if(!us.ok)h.appendChild(ignBtn("u:"+inst.id,us.missing.join("|")));}}
  inst._mFlag=mFlag;
  if(!inst.fac&&r.type==="Raw Materials"){const _p=D.players.find(pp=>pp.board===S),rs=(rawClaims(_p)[inst.id])||{ok:true},rf=flagState("r:"+inst.id,!rs.ok,"reach");
    if(rs.ok&&rs.terr)h.title=(h.title?h.title+"\n":"")+"Claims "+rs.terr;
    if(!rs.ok&&rf==="on"){const b=document.createElement("span");b.className="badge noearn";b.textContent="reach ✗";b.title=n+": "+(rs.why||"none in Reach")+(mapState().useNodes?" (resource nodes)":" (terrain)")+" — this Settlement's Reach";h.appendChild(b);h.appendChild(ignBtn("r:"+inst.id,"reach"));}}
  if(SIMPLE&&!inst.fac){const sr=simpleReq(inst,r,have,craft,tc),sf=flagState("s:"+inst.id,!sr.ok,sr.missing.join("|"));
    if(!sr.ok&&sf==="on"){const b=document.createElement("span");b.className="badge noearn";b.textContent="req ✗";b.title=sr.missing.join("\n");h.appendChild(b);h.appendChild(ignBtn("s:"+inst.id,sr.missing.join("|")));}}
  if(inst.sid!=null && !inst.fac && isFreeRider(inst)){const b=document.createElement("span");b.className="badge earn";b.textContent="⚡";b.title=CHAINL+" rider";h.appendChild(b);}
  if(inst.fac){const b=document.createElement("span");b.className="badge earn";b.textContent="Faction";h.appendChild(b);}
  if(!inst.fac){const rm=document.createElement("button");rm.className="rm";rm.textContent="✕";rm.onclick=(e)=>{e.stopPropagation();removeInstance(inst.id);};
    h.appendChild(rm);}
  h.onclick=()=>{if(h._suppressClick)return;const i=S.expanded.indexOf(inst.id);if(i<0)S.expanded.push(inst.id);else S.expanded.splice(i,1);save();render();};
  card.appendChild(h);

  // secondary row: type · location · build / repair timers (and, when open, the timer / damage buttons)
  const sec=document.createElement("div");sec.className="sub psec";
  {const ty=document.createElement("span");ty.className="note";ty.textContent=r.type;sec.appendChild(ty);}
  if(!inst.fac)sec.appendChild(placementSelect(inst));
  if(inst.bt>0)sec.appendChild(timerCtl("build",inst.bt,d=>{inst.bt=Math.max(0,inst.bt+d);save();render();}));
  if(inst.dmg>0)sec.appendChild(timerCtl("repair",inst.dmg,d=>{inst.dmg=Math.max(0,inst.dmg+d);save();render();}));
  if(open){const bb=document.createElement("button");bb.textContent="build timer";
      bb.onclick=e=>{e.stopPropagation();const t=pursuitBuildTime(n);if(t>0){inst.bt=t;save();render();flash(n+" Build Timer "+t+buildNote(pursuitBaseTime(n)));}else flash(n+": Build Timer 0 — builds immediately"+buildNote(pursuitBaseTime(n)));};
    const db=document.createElement("button");db.textContent=inst.dmg>0?"repaired":"damage";
      db.onclick=e=>{e.stopPropagation();inst.dmg=inst.dmg>0?0:REPAIR_T;save();render();};
    if(!(inst.bt>0))sec.appendChild(bb);sec.appendChild(db);}
  if(!pActive(inst))card.classList.add("inactive");
  const biRow=()=>{const h=buildsIntoRow(r);if(!h)return null;const d=document.createElement("div");d.innerHTML=h;return d.firstChild;};

  if(!open){   // cursory view: builds into, then effect, then type / location / timers
    {const q=biRow();if(q)card.appendChild(q);}
    const sum=contribChips(r,me.earned);sum.style.marginTop="5px";
    if(sum.children.length)card.appendChild(sum);
    card.appendChild(sec);
    return card;
  }

  // expanded view: EFFECT first
  const bi=document.createElement("div");bi.className="block";bi.innerHTML='<div class="lbl">'+(SIMPLE?"EFFECT":"INNATE")+'</div>';
  bi.appendChild(atomsBlock(r.innate,hideCombat));
  card.appendChild(bi);
  // MASTERY
  const bm=document.createElement("div");bm.className="block mastery"+(r.mastery_raw?(me.earned?" on":" off"):"");
  const badge=r.mastery_raw?('<span class="badge '+(me.earned?"earn":"noearn")+'">'+(me.earned?"earned ✓":"not earned ✗")+'</span>'):'<span class="badge nomast">none</span>';
  bm.innerHTML='<div class="lbl">MASTERY<span class="sp"></span>'+badge+'</div>';
  if(r.mastery_raw){
    const ab=atomsBlock(r.mastery,hideCombat);if(!me.earned)ab.style.opacity=".5";bm.appendChild(ab);
    if(r.mreq_raw){const rq=document.createElement("div");rq.className="req";rq.innerHTML="req: "+kwify(r.mreq_raw,r.name);bm.appendChild(rq);}
    {const ih=masteryInfraHTML(r);if(ih){const d=document.createElement("div");d.innerHTML=ih;bm.appendChild(d);}}
    if(!me.earned&&inst._mFlag!=="ignored"){const mm=document.createElement("div");mm.className="miss";mm.textContent="missing: "+missTxt(me.missing)+" ";
      mm.appendChild(ignBtn("m:"+inst.id,(me.missing||[]).join("|")));bm.appendChild(mm);}
  }
  if(r.mastery_raw&&me.earned&&!hideCombat&&(r.combo_parts||[]).length){
    // Mastery met: one summed row (colour shows the origin), the separate blocks folded underneath
    const cb=document.createElement("div");cb.className="block combo";
    cb.innerHTML='<div class="lbl">INNATE + MASTERY<span class="sp"></span><span class="badge earn">earned ✓</span></div>'+
      '<div class="atoms">'+r.combo_parts.map(([t,o])=>'<span class="atom cmb o-'+o+'" title="'+({i:"Innate",m:"Mastery",im:"Innate + Mastery, summed"}[o]||"")+'">'+(o==="im"?'<b class="cmbS">Σ</b> ':o==="m"?'<b class="cmbM">M</b> ':'')+kwify(t)+'</span>').join("")+'</div>'+
      '<div class="note cmbL"><span class="o-i-k">innate</span> · <span class="o-m-k">M mastery</span> · <span class="o-im-k">Σ both, summed</span></div>';
    card.appendChild(cb);
    const det=document.createElement("details");det.className="block sep";det.innerHTML='<summary class="note">innate / mastery separately</summary>';
    det.appendChild(bi);det.appendChild(bm);card.appendChild(det);
  } else if(!(SIMPLE&&!r.mastery_raw)) card.appendChild(bm);
  // BUILDS INTO (add chips) + MASTERY NEEDED BY
  {const q=biRow();if(q){const b=document.createElement("div");b.className="block";b.appendChild(q);
    const mf=(r.mastery_for||[]).filter(x=>!(r.builds_into||[]).includes(x));
    if(mf.length){const d=document.createElement("div");d.className="qrow";d.innerHTML='<span class="lbl">MASTERY NEEDED BY</span>'+mf.map(quickChip).join("");b.appendChild(d);}
    card.appendChild(b);}}
  // REQUIRES (mastery chain with add chips, infrastructure)
  if(SIMPLE){const rh=simpleReqHTML(inst,simpleReq(inst,r,have,craft,tc));if(rh){const b=document.createElement("div");b.className="block";b.innerHTML=rh;card.appendChild(b);}}
  card.appendChild(sec);
  return card;
}

function renderInfraSection(kind,src,have,hideCombat){
  const box=document.getElementById("board-"+kind);box.innerHTML="";
  const keys=Object.keys(have);
  keys.forEach(n=>{
    const open=(S.eqOpen||[]).includes(n);
    const r=src[n];const card=document.createElement("div");card.className="card";
    card.style.borderLeftColor=cvar(PHASE_COLOR[PHASE[(r.atoms[0]||{}).cat]||"other"]);
    const h=document.createElement("h3");h.style.cursor="pointer";
    const car=document.createElement("span");car.className="pcaret";car.textContent=open?"▾":"▸";h.appendChild(car);
    const nm=document.createElement("span");nm.className="nm";nm.textContent=n;h.appendChild(nm);
    const tb=document.createElement("span");tb.className="badge tier";tb.textContent=r.tier;h.appendChild(tb);
    const rs=infraReqStatus(r),rf=flagState("i:"+kind+":"+n,!rs.ok,rs.missing.join("|"));
    if(infraReqToks(r).length&&rf!=="ignored"){const qb=document.createElement("span");qb.className="badge "+(!rs.ok?"noearn":rs.manual?"manual":"earn");
      qb.textContent=!rs.ok?"req ✗":rs.manual?"req ?":"req ✓";qb.title=r.requirement;h.appendChild(qb);}
    if(!rs.ok&&rf==="on")card.classList.add("illegal");
    itm();const isFac=S.facInfra.includes(n);
    if(isFac){const fb=document.createElement("span");fb.className="badge earn";fb.textContent="Faction";h.appendChild(fb);}
    if(r.upkeep&&!isFac){const ub=document.createElement("span");ub.className="badge";ub.style.borderColor="var(--upkeep)";ub.style.color="var(--upkeep)";ub.textContent="up "+r.upkeep;h.appendChild(ub);}
    if(S.itimer[n]>0)h.appendChild(timerCtl("build",S.itimer[n],d=>{S.itimer[n]=Math.max(0,S.itimer[n]+d);if(!S.itimer[n])delete S.itimer[n];save();render();}));
    if(S.idmg[n]>0)h.appendChild(timerCtl("repair",S.idmg[n],d=>{S.idmg[n]=Math.max(0,S.idmg[n]+d);if(!S.idmg[n])delete S.idmg[n];save();render();}));
    if(!isFac){const rm=document.createElement("button");rm.className="rm";rm.textContent="✕";
      rm.onclick=(e)=>{e.stopPropagation();delete have[n];delete S.itimer[n];delete S.idmg[n];save();render();renderList();};h.appendChild(rm);}
    h.onclick=()=>{S.eqOpen=S.eqOpen||[];const i=S.eqOpen.indexOf(n);if(i<0)S.eqOpen.push(n);else S.eqOpen.splice(i,1);save();render();};
    card.appendChild(h);
    if(!rs.ok&&rf==="on"){const mm=document.createElement("div");mm.className="miss";mm.textContent="missing: "+rs.missing.join(", ")+" ";
      mm.appendChild(ignBtn("i:"+kind+":"+n,rs.missing.join("|")));card.appendChild(mm);}
    if(open){
      const sub=document.createElement("div");sub.className="sub";
      sub.textContent="upkeep "+(isFac?0:r.upkeep)+(r.requirement?(" · req: "+r.requirement):"");card.appendChild(sub);
      {const tl=document.createElement("div");tl.className="sub";
        const bb=document.createElement("button");bb.textContent="build timer";bb.onclick=e=>{e.stopPropagation();const t=infraBuildTime(n);if(t>0){S.itimer[n]=t;save();render();flash(n+" Build Timer "+t+buildNote(infraBaseTime(n)));}else flash(n+": Build Timer 0 — builds immediately"+buildNote(infraBaseTime(n)));};
        const db=document.createElement("button");db.textContent=S.idmg[n]>0?"repaired":"damage";db.onclick=e=>{e.stopPropagation();if(S.idmg[n]>0)delete S.idmg[n];else S.idmg[n]=REPAIR_T;save();render();};
        if(!(S.itimer[n]>0))tl.appendChild(bb);tl.appendChild(db);card.appendChild(tl);}
      if(infraReqToks(r).length){const rq=document.createElement("div");rq.className="block";rq.innerHTML='<div class="lbl">REQUIREMENTS</div>'+infraReqLinesHTML(r);card.appendChild(rq);}
      const bi=document.createElement("div");bi.className="block";bi.innerHTML='<div class="lbl">EMPIRE EFFECT</div>';
      bi.appendChild(atomsBlock(r.atoms,hideCombat));
      if(r.effect_raw){const v=document.createElement("div");v.className="verb";v.innerHTML=kwify(r.effect_raw);bi.appendChild(v);}
      card.appendChild(bi);
    }
    box.appendChild(card);
  });
  toggleEmpty(kind,keys.length);
}

// ---- army: aggregate unlocks/modifiers from pool (innate always, mastery if mastered) ----
function armyUnlocks(earned){
  const active=[];               // {tok, node, via}
  Object.keys(PC).forEach(n=>{
    const src=ARMYSRC[n]; if(!src)return;
    src.innate.forEach(t=>active.push({tok:t,node:n,via:"innate"}));
    if(earned[n]) src.mastery.forEach(t=>active.push({tok:t,node:n,via:"mastery"}));
  });
  const tset=new Set(active.map(a=>a.tok));
  const wTiers=new Set(["Crude"]), armors=new Set(["Cloth"]);
  let shields=false, ranged=false, cavalry=false;const weaponsUnl=new Set();
  const shieldTiers=new Set();let shieldByTier=SIMPLE;     // SIMPLE: shield tier from "X armor & shield" (plus Joinery for Shields)
  const retinues=new Set(["Levy"]); const mods=[];
  active.forEach(a=>{
    const t=a.tok;
    if(t.startsWith("tier:")){
      const x=t.slice(5);
      if(TIER_RANK.hasOwnProperty(x)) wTiers.add(x);
      else if(ARMOR_TAG[x]) armors.add(ARMOR_TAG[x]);
      else if(x==="Shields") shields=true;
    } else if(t.startsWith("armor:")){const x=t.slice(6);Object.keys(EQ.armors).forEach(k=>{if(EQ.armors[k]&&EQ.armors[k].tier===x)armors.add(k);});}
    else if(t.startsWith("shield:")){shieldByTier=true;shieldTiers.add(t.slice(7));}
    else if(t==="ranged") ranged=true;
    else if(t==="cavalry") cavalry=true;
    else if(t.startsWith("weapon:")){weaponsUnl.add(t.slice(7));cavalry=true;}
    else if(t.startsWith("retinue:")) retinues.add(t.slice(8));
    else mods.push(a);           // keyword / modifier
  });
  // armor also implied by weapon tiers? no — armor unlocked only by explicit armor tags.
  Object.keys(EQ.reqAlias||{}).forEach(al=>{if((PC[EQ.reqAlias[al]]||0)>0)tset.add(al);});   // legacy alias in "requires" (e.g. ABF)
  Object.keys(PC).forEach(n=>{if(PC[n]>0)tset.add(n);});                                      // or the Holding's own name
  return {set:tset,wTiers,armors,shields,shieldTiers,shieldByTier,ranged,cavalry,weaponsUnl,retinues,mods,active};
}
function unlockedShieldTiers(u){ // Shields (Joinery) + tier: SIMPLE = "X armor & shield" Holdings; legacy = weapon-tier progression
  return u.shields ? (u.shieldByTier?u.shieldTiers:u.wTiers) : new Set();
}

function tierOK(tier,tiers){ return tier==null || tiers.has(tier); }
function gloss(k){ return GLOSS[k]?(k+": "+GLOSS[k]):k; }

// ---- inspector ----
const TAG2SRC={};
Object.keys(ARMYSRC).forEach(n=>{
  (ARMYSRC[n].innate||[]).forEach(t=>{(TAG2SRC[t]=TAG2SRC[t]||[]).push({node:n,via:"innate"});});
  (ARMYSRC[n].mastery||[]).forEach(t=>{(TAG2SRC[t]=TAG2SRC[t]||[]).push({node:n,via:"mastery"});});
});
const SYN={"Strain":"Strained"};
function glossLookup(tok){
  if(GLOSS[tok]) return {term:tok,def:GLOSS[tok]};
  let base=tok.replace(/\s*[:+].*$/,"").replace(/\s+\d+$/,"").trim();
  base=SYN[base]||base;
  if(base && GLOSS[base]) return {term:base,def:GLOSS[base],mod:tok};
  let m=tok.match(/^(Immune|Negate)\s+(.+)$/i);
  if(m){let x=SYN[m[2]]||m[2]; if(GLOSS[x]) return {term:x,def:GLOSS[x],mod:tok,prefix:m[1]};}
  return {term:tok,def:null};
}
function openModal(html){
  document.getElementById("inspectCard").innerHTML=html;
  document.getElementById("inspect").style.display="flex";
}
function closeModal(){WP=null;document.getElementById("inspect").style.display="none";}
function kwChipHTML(tok,cls){return '<span class="kw '+(cls||"")+'" data-tok="'+esc(tok)+'">'+esc(tok)+'</span>';}
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;");}
function inspectKeyword(tok){
  const g=glossLookup(tok);
  let h='<h3>'+esc(tok)+'<button class="close" onclick="closeModal()">✕</button></h3>';
  if(g.mod && g.term!==tok) h+='<div class="note">base keyword: <b>'+esc(g.term)+'</b>'+(g.prefix?(" ("+g.prefix+")"):"")+'</div>';
  if(g.def) h+='<div class="def">'+kwify(g.def,g.term)+'</div>';
  // sources: engine-tag grants + any node whose innate/mastery text names the keyword
  const seen=new Set(), srcs=[];
  (TAG2SRC[tok]||[]).forEach(s=>{const k=s.node+"|"+s.via;if(!seen.has(k)){seen.add(k);srcs.push(s);}});
  const base=(g.term||tok);
  [tok,base].forEach(term=>{
    let re;try{re=new RegExp("\\b"+term.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+"\\b","i");}catch(e){return;}
    Object.keys(R).forEach(n=>{["innate","mastery"].forEach(via=>{
      const txt=R[n][via+"_raw"]||"";if(re.test(txt)){const k=n+"|"+via;if(!seen.has(k)){seen.add(k);srcs.push({node:n,via});}}});});
  });
  if(srcs.length){
    h+='<div class="lbl2">DEFINED / GRANTED BY</div>';
    srcs.slice(0,6).forEach(s=>{const r=R[s.node];const txt=(s.via==="mastery"?r.mastery_raw:r.innate_raw)||"";
      h+='<div class="note"><b>'+esc(s.node)+'</b> ('+s.via+')'+(txt?': '+esc(txt):"")+'</div>';});
  }
  if(!g.def && !srcs.length) h+='<div class="def nodef">No glossary entry — see rulebook.</div>';
  openModal(h);
}
function inspectItem(kind,name){
  const src={weapon:EQ.weapons,ranged:EQ.ranged,armor:EQ.armors,shield:EQ.shields,retinue:EQ.retinues}[kind];
  const it=src&&src[name]; if(!it){openModal('<h3>'+esc(name)+'<button class="close" onclick="closeModal()">✕</button></h3>');return;}
  let h='<h3>'+esc(name);
  if(it.tier)h+=' <span class="badge tier">'+(it.tier_label||it.tier)+'</span>';
  h+='<button class="close" onclick="closeModal()">✕</button></h3>';
  const S_=[];
  const push=(k,v)=>{if(v!==undefined&&v!==null&&v!=="")S_.push('<span class="stat"><span class="k">'+k+'</span><b>'+v+'</b></span>');};
  if(kind==="retinue"){push("TO-STRIKE",it.to_hit+"+");push("ENDURANCE",it.endurance);push("SHAKING",it.shaking+"+");push("SPEED",it.speed);push("MAX",it.max_size);push("COST",it.cost);}
  if(kind==="weapon"||kind==="ranged"){push("AP",it.ap);push("INIT",(it.init>=0?"+":"")+it.init);}
  if(kind==="armor"){push("SAVE",it.save+"+");}
  if(kind==="shield"){push("SAVE +",it.save_bonus);push("INIT",(it.init>=0?"+":"")+it.init);}
  if(S_.length)h+='<div class="sgrid">'+S_.join("")+'</div>';
  if(it.tags&&it.tags.length){h+='<div class="lbl2">'+(it.profile2h?'1H PROFILE — ':'')+'KEYWORDS (tap for detail)</div><div class="atoms">'+it.tags.map(t=>kwChipHTML(t)).join(" ")+'</div>';}
  if(kind==="weapon"&&it.profile2h){const q=it.profile2h;
    h+='<div class="lbl2">2H PROFILE — chosen each Skirmish with your Tactic (no Shield while 2H)</div><div class="sgrid"><span class="stat"><span class="k">AP</span><b>'+q.ap+'</b></span><span class="stat"><span class="k">INIT</span><b>'+((q.init>=0?"+":"")+q.init)+'</b></span></div>'+
      '<div class="atoms">'+(q.tags||[]).map(t=>kwChipHTML(t)).join(" ")+'</div>';}
  if(it.requires)h+='<div class="note">Requires: '+it.requires.map(esc).join(", ")+'</div>';
  if(it.tactics_allowed)h+='<div class="note">Tactics: '+it.tactics_allowed.map(esc).join(", ")+'</div>';
  if(it.note)h+='<div class="note">'+esc(it.note)+'</div>';
  openModal(h);
}

function optionList(sel, items, tierset, u, chosen, extra){
  // items: {name:record}; build <option>s, marking locked
  sel.innerHTML="";
  Object.keys(items).forEach(name=>{
    const it=items[name]; const o=document.createElement("option"); o.value=name;
    let ok = tierOK(it.tier, tierset);
    if(extra) ok = ok && extra(name,it);
    o.textContent=(ok?"":"🔒 ")+name+(it.tier?(" ["+(it.tier_label||it.tier)+"]"):"");
    if(!ok) o.className="locked";
    sel.appendChild(o);
  });
  sel.value = chosen && items[chosen] ? chosen : sel.querySelector("option")?.value;
}

// Shared loadout builder (Army cards and the Garrison card): Retinue · Weapon · Ranged · Armor · Shield selects bound to obj,
// locked options marked by the owner's unlocks u. opts.onRetinue runs after a Retinue change; opts.bastard folds 2H Bastard.
function loadoutFields(obj,u,opts){opts=opts||{};const lo=document.createElement("div");lo.className="loadout";
  const field=(labelTxt,key,items,tierset,extra,after)=>{const f=document.createElement("div");f.className="fld";f.innerHTML='<label>'+labelTxt+'</label>';
    const sel=document.createElement("select");optionList(sel,items,tierset,u,obj[key],extra);if(!obj[key]||!items[obj[key]])obj[key]=sel.value;
    sel.onchange=()=>{obj[key]=sel.value;if(after)after();save();render();};f.appendChild(sel);lo.appendChild(f);return sel;};
  const retItems={};Object.keys(EQ.retinues).forEach(k=>retItems[k]={tier:null});
  field("Retinue","retinue",retItems,new Set(Object.keys(EQ.retinues)),name=>u.retinues.has(name),opts.onRetinue);
  if(opts.bastard)fixBastard(obj);
  field("Weapon","weapon",EQ.weapons,u.wTiers,(name,it)=>reqMet(it,u)&&weaponUnlockMet(name,u));
  field("Ranged","ranged",Object.assign({"None":{tier:null}},EQ.ranged),u.wTiers,(name,it)=>name==="None"||(u.ranged&&reqMet(it,u)));
  field("Armor","armor",EQ.armors,new Set(EQ.tiers),name=>u.armors.has(name)||name==="Cloth");
  const shieldItems={};Object.keys(EQ.shields).forEach(k=>shieldItems[k==="null"?"None":k]=EQ.shields[k]);
  field("Shield","shield",shieldItems,unlockedShieldTiers(u),name=>name==="None"||u.shields);
  return lo;}
const MUSTER_DEFAULT=25;   // Retinues a Muster asks for by default
function renderArmy(){
  recomputePC();const have=new Set(Object.keys(PC));
  const {earned}=computeEarned(have);
  const u=armyUnlocks(earned);u.mods=u.mods.concat(facCombat(S));   // faction army mechanics shown with the Holding ones


  // top unlocks panel — everything the army can pull, in one place
  const up=document.getElementById("armyUnlocks");
  const g=(h,body)=>'<div class="grp"><span class="h">'+h+'</span>'+body+'</div>';
  const wt=[...u.wTiers].sort((a,b)=>TIER_RANK[a]-TIER_RANK[b]).join(", ");
  const modChips=u.mods.length
    ? u.mods.map(m=>'<span class="kw mod" data-tok="'+m.tok.replace(/"/g,"&quot;")+'" title="'+gloss(m.tok).replace(/"/g,"&#39;")+'">'+m.tok+' <span style="opacity:.6">('+m.node+(m.via==="mastery"?"·M":"")+')</span></span>').join(" ")
    : '<span class="note">none</span>';
  up.className="block unlocks";
  const unlOpen=!!(up.querySelector("details")||{}).open;
  up.innerHTML='<details'+(unlOpen?' open':'')+'><summary class="lbl" style="cursor:pointer">ARMY UNLOCKS &amp; MODIFIERS <span class="note" style="text-transform:none;letter-spacing:0">'
    + esc([wt,[...u.armors].join(", "),[...u.retinues].join(", ")].filter(Boolean).join(" · ")+(u.mods.length?" · "+u.mods.length+" mod"+(u.mods.length>1?"s":""):""))+'</span></summary>'
    + g("Weapon tiers", wt)
    + g("Ranged", u.ranged?"yes":"no") + g("Cavalry", u.weaponsUnl&&u.weaponsUnl.size?[...u.weaponsUnl].join(", "):(u.cavalry?"yes":"no"))
    + g("Armor", [...u.armors].join(", "))
    + g("Shields", u.shields?("yes ("+[...unlockedShieldTiers(u)].sort((a,b)=>TIER_RANK[a]-TIER_RANK[b]).join(", ")+")"):"no")
    + g("Retinues", [...u.retinues].join(", "))
    + '<div class="grp"><span class="h">Modifiers</span></div><div class="kwrow">'+modChips+'</div></details>';

  // army cards
  const list=document.getElementById("armyList"); list.innerHTML="";
  S.armies.forEach(a=>list.appendChild(armyCard(a,u)));
  {const gc=garrisonCard(u);if(gc)list.appendChild(gc);}
  const tot=S.armies.reduce((s,a)=>s+armyUpkeep(a),0);
  document.getElementById("armyTotal").textContent=fmt(-tot);
  document.getElementById("c-army").textContent=S.armies.length?("· "+S.armies.length):"";
}

function armyCard(a,u){
  if(a.open===undefined)a.open=true;
  const routed=isRouted(a);
  const card=document.createElement("div");card.className="acard"+(routed?" routed":"");

  // header: caret, label, morale summary, upkeep, remove
  const top=document.createElement("div");top.className="top";
  const car=document.createElement("span");car.className="pcaret";car.style.cursor="pointer";car.textContent=a.open?"▾":"▸";
  car.onclick=()=>{a.open=!a.open;save();render();};top.appendChild(car);
  const lab=document.createElement("input");lab.className="lab";lab.placeholder="army label";lab.value=a.label||"";
  lab.oninput=()=>{a.label=lab.value;save();};top.appendChild(lab);
  const mor=document.createElement("span");mor.className="badge "+(routed?"noearn":"tier");
  mor.textContent="morale "+effMorale(a)+"+"+(a.fatigue?(" ("+moraleBase(a)+"+ +"+(2*a.fatigue)+")"):"");top.appendChild(mor);
  const upL=document.createElement("span");upL.className="note";upL.textContent="upkeep";top.appendChild(upL);
  const up=document.createElement("b");up.textContent=fmt(-armyUpkeep(a));up.title=a.retinue+" Army cost";top.appendChild(up);
  const rm=document.createElement("button");rm.className="rm";rm.textContent="✕";
  rm.onclick=()=>{S.armies=S.armies.filter(x=>x!==a);save();render();};top.appendChild(rm);
  card.appendChild(top);

  {const p=playerOfBoard(S),ms=document.createElement("div");ms.className="bcrow";ms.style.margin="4px 0";
    const L=p?musterLimit(p,a):{lim:0,src:[],paused:[],onMap:false},m=a.muster;
    if(m&&m.n>0){ms.innerHTML='<span class="badge tier">Muster Timer '+(m.t||0)+'</span> <span class="note">+'+L.lim+'/turn · '+m.n+' to go'+(L.paused.length?' · besieged: '+esc(L.paused.join(", ")):'')+(L.onMap?'':' · not on the map: all Settlements count')+'</span> ';
      const x=document.createElement("button");x.textContent="cancel";x.onclick=()=>{delete a.muster;save();render();};ms.appendChild(x);}
    else{const room=Math.max(0,(EQ.army_max||25)-(a.count||0));
      ms.innerHTML='<span class="note">Muster</span> ';const inp=document.createElement("input");inp.type="number";inp.min="1";inp.max=String(room);inp.value=String(Math.min(room,MUSTER_DEFAULT));inp.style.width="56px";
      const go=document.createElement("button");go.textContent="start";
      const nt=document.createElement("span");nt.className="note";const upd=()=>{const n=Math.max(0,Math.min(room,+inp.value||0));nt.textContent=L.lim?" Muster Timer "+Math.ceil(n/L.lim)+" (limit "+L.lim+(L.src.length?": "+L.src.join(", "):"")+")":" no muster limit in reach";};
      inp.oninput=upd;upd();go.onclick=()=>{const n=Math.max(0,Math.min(room,+inp.value||0));if(!n)return;a.muster={n,t:L.lim?Math.ceil(n/L.lim):0};save();render();};
      ms.appendChild(inp);ms.appendChild(go);ms.appendChild(nt);}
    card.appendChild(ms);
    if(p){const st=document.createElement("div");st.className="bcrow";st.style.margin="2px 0";st.style.flexWrap="wrap";
      const lab=document.createElement("span");lab.className="note";lab.textContent="Inside";st.appendChild(lab);
      const sel=document.createElement("select");sel.innerHTML='<option value="">— field —</option>'+(S.settlements||[]).map(x=>{const cur=String(a.sid)===String(x.id),ec=cur?{ok:true}:enterCheck(p,a,p,x);
        return '<option value="'+x.id+'"'+(cur?' selected':'')+(ec.ok?'':' disabled')+'>'+esc(x.name||x.tier)+(ec.ok?(ec.kick?' (ally pushed out)':''):' (occupied)')+'</option>';}).join('');
      sel.onchange=()=>{const M=mapState();if(sel.value){const k=armyHex(p,Object.assign({},a,{sid:null}));if(k&&M.cells[k]&&M.cells[k].type==="Army")delete M.cells[k];{const st=settById(p,sel.value),ec=st?enterCheck(p,a,p,st):null;if(ec&&ec.kick)kickOut(p,st,ec.kick);}a.sid=+sel.value;delete a.inAlly;}else{delete a.sid;delete a.inAlly;}save();render();};
      st.appendChild(sel);
      armyStateTags(p,a).filter(x=>x.k!=="in").forEach(x=>{const bd=document.createElement("span");bd.className="badge "+(x.k==="note"||x.k==="in"?"tier":"noearn");bd.textContent=x.txt;st.appendChild(bd);});
      if(a.blocked&&!a.sackT){const bl=document.createElement("span");bl.className="badge noearn";bl.textContent="Blocked";st.appendChild(bl);}
      card.appendChild(st);}}
  if(routed){const b=document.createElement("div");b.className="routebar";
    b.textContent="ROUTED — morale ≥ 11+, retinues drop to 0";card.appendChild(b);}
  if(!a.open) return card;

  // loadout selects
  const lo=loadoutFields(a,u,{onRetinue:()=>{const rt=EQ.retinues[a.retinue];if(rt)a.endurance=rt.endurance;},bastard:true});
  card.appendChild(lo);
  const gf=facGearFlags(a);if(gf.length){const fb=document.createElement("div");fb.className="flagbox";fb.style.marginTop="4px";fb.textContent="⚑ "+gf.join(" · ");card.appendChild(fb);}

  card.appendChild(armyStats(a,u));

  // clickable loadout chips
  const loch=document.createElement("div");loch.className="lochips";
  [["Retinue","retinue",a.retinue],["Weapon","weapon",a.weapon],["Ranged","ranged",a.ranged],
   ["Armor","armor",a.armor],["Shield","shield",a.shield]].forEach(([lbl,kind,val])=>{
    if(!val||val==="None")return;
    const c=document.createElement("span");c.className="lochip";c.dataset.kind=kind;c.dataset.item=val;
    c.innerHTML=eqSVG(val,16,kind==="retinue"?"army":"eq")+'<span class="k">'+lbl+'</span>'+esc(val);loch.appendChild(c);
  });
  card.appendChild(loch);

  // counters: retinues, endurance, fatigue
  const line=document.createElement("div");line.className="status";
  const cnt=document.createElement("div");cnt.className="endr";
  cnt.innerHTML='<span class="stat"><span class="k">RETINUES</span></span>';
  const cin=document.createElement("input");cin.type="number";cin.min="0";cin.max=EQ.army_max;cin.style.width="52px";
  cin.value=a.count||0;cin.oninput=()=>{a.count=Math.max(0,Math.min(EQ.army_max,+cin.value||0));up.textContent=fmt(-armyUpkeep(a));save();};cin.onchange=()=>computeAll();
  cnt.appendChild(cin);cnt.insertAdjacentHTML("beforeend",'<span class="note">/'+EQ.army_max+'</span>');
  line.appendChild(cnt);
  const end=document.createElement("div");end.className="endr";
  end.innerHTML='<span class="stat"><span class="k">ENDURANCE</span></span>';
  const eminus=document.createElement("button");eminus.textContent="−";eminus.onclick=()=>{a.endurance=(a.endurance||0)-1;save();render();};
  const eval_=document.createElement("span");eval_.textContent=(a.endurance!=null?a.endurance:0);
  const eplus=document.createElement("button");eplus.textContent="+";eplus.onclick=()=>{a.endurance=(a.endurance||0)+1;save();render();};
  end.appendChild(eminus);end.appendChild(eval_);end.appendChild(eplus);line.appendChild(end);
  const fat=document.createElement("div");fat.className="endr";
  fat.innerHTML='<span class="stat"><span class="k">FATIGUE</span></span>';
  const fminus=document.createElement("button");fminus.textContent="−";
  fminus.onclick=()=>{a.fatigue=Math.max(0,(a.fatigue||0)-1);save();render();};
  const fval=document.createElement("span");fval.textContent=(a.fatigue||0);
  const fplus=document.createElement("button");fplus.textContent="+";
  fplus.onclick=()=>{a.fatigue=(a.fatigue||0)+1; if(isRouted(a))a.count=0; save();render();};
  fat.appendChild(fminus);fat.appendChild(fval);fat.appendChild(fplus);line.appendChild(fat);
  card.appendChild(line);

  // status toggles
  const st=document.createElement("div");st.className="status";
  [["strained","Strained"],["blunder","Blunder"]].forEach(([key,lbl])=>{
    const c=document.createElement("span");c.className="stog"+(key==="blunder"?" blunder":"")+(a[key]?" on":"");
    c.textContent=lbl;c.onclick=()=>{a[key]=!a[key];save();render();};st.appendChild(c);
  });
  card.appendChild(st);
  return card;
}

function reqMet(it,u){ if(!it.requires)return true; return it.requires.every(r=>u.set.has(r)); }
// weapons that some pursuit explicitly unlocks ("Unlocks Cavalry Spear" / "Unlocks Lance") need that unlock active
const WEAPON_GATED=new Set(Object.values(ARMYSRC||{}).flatMap(v=>[].concat(v.innate||[],v.mastery||[])).filter(t=>String(t).startsWith("weapon:")).map(t=>t.slice(7)));
function weaponUnlockMet(name,u){return !WEAPON_GATED.has(name)||(u.weaponsUnl&&u.weaponsUnl.has(name));}
// morale characteristic = retinue Shaking + 2 per Fatigue token; >=11 = instant rout
function moraleBase(a){const rt=EQ.retinues[a.retinue];return rt?rt.shaking:0;}
function armyUpkeep(a){const rt=EQ.retinues[a.retinue]||{};return +rt.cost||0;}   // per Army: its Retinue type's cost
// Faction "Armies' Morale can't be modified beyond N+" (The Undying Flame): Morale is capped, so it never reaches the Rout value
function moraleCap(a){const b=(D.players||[]).map(p=>p.board).find(bb=>(bb.armies||[]).includes(a));const f=b&&FAC[b.faction||""];
  const m=f&&hitOf("F:"+b.faction,"morale_cap");return m?+m[1]:null;}
function effMorale(a){const v=moraleBase(a)+(BT.fatigueMorale??2)*(a.fatigue||0),c=moraleCap(a);return c!=null?Math.min(c,v):v;}
function isRouted(a){return effMorale(a)>=(BT.routThr||11);}

// modified Army stats (shared by the Army card, map plate, hover title and Move panel)
function armyVals(a,u){
  const rt=EQ.retinues[a.retinue]||{}, w=EQ.weapons[a.weapon]||{},
        r=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,
        ar=EQ.armors[a.armor]||{}, shKey=(a.shield==="None"||!a.shield)?"null":a.shield,
        sh=EQ.shields[shKey]||{save_bonus:0,init:0,tags:[]};
  const strikePlus=u.mods.filter(m=>m.tok==="Strike +1").length,initPlus=u.mods.filter(m=>m.tok==="Init +1").length,wpn=r||w;
  return {toStrike:(rt.to_hit!=null?rt.to_hit:0)-strikePlus,save:(ar.save!=null?ar.save:0)-(sh.save_bonus||0),
    init:(wpn.init||0)+(sh.init||0)+initPlus,ap:(wpn.ap!=null?wpn.ap:0),morale:effMorale(a),routed:isRouted(a)};}
function armyStats(a,u){
  const box=document.createElement("div");box.className="stats";
  const rt=EQ.retinues[a.retinue]||{}, w=EQ.weapons[a.weapon]||{},
        r=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,
        ar=EQ.armors[a.armor]||{}, shKey=(a.shield==="None"||!a.shield)?"null":a.shield,
        sh=EQ.shields[shKey]||{save_bonus:0,init:0,tags:[]};
  const V=armyVals(a,u),toStrike=V.toStrike,save=V.save,init=V.init,wpn=r||w;
  const stat=(k,v)=>{const s=document.createElement("span");s.className="stat";s.innerHTML='<span class="k">'+k+'</span><b>'+v+'</b>';box.appendChild(s);};
  stat("TO-STRIKE",toStrike+"+");
  stat("SAVE",save+"+");
  stat("INIT",(init>=0?"+":"")+init);
  stat("AP",(wpn.ap!=null?wpn.ap:0));
  stat("SPEED",rt.speed!=null?rt.speed:"—");
  stat("MORALE",effMorale(a)+"+"+(isRouted(a)?" ⚠":""));
  stat("BASE END",rt.endurance!=null?rt.endurance:"—");
  // keywords: weapon + ranged + shield + armor + army modifiers
  const kws=new Set([...(w.tags||[]),...(r?r.tags:[]),...(sh.tags||[]),...(ar.tags||[])]);
  const kwrow=document.createElement("div");kwrow.className="kwrow";
  [...kws].forEach(k=>{const s=document.createElement("span");s.className="kw";s.dataset.tok=k;s.title=gloss(k).replace(/"/g,"'");s.textContent=k;kwrow.appendChild(s);});
  u.mods.filter(m=>!/^(Strike|Init) \+1$/.test(m.tok)).forEach(m=>{
    const s=document.createElement("span");s.className="kw mod";s.dataset.tok=m.tok;s.title=gloss(m.tok).replace(/"/g,"'");s.textContent=m.tok;kwrow.appendChild(s);});
  const wrap=document.createElement("div");wrap.appendChild(box);
  if(kwrow.children.length)wrap.appendChild(kwrow);
  return wrap;
}

// ---- totals ----
function noUpkeepTiers(){const out={};Object.keys(PC).forEach(n=>{if(!(PC[n]>0))return;
  efxOf("h:"+n,"no_upkeep_tier").forEach(m=>{out[m[1]]=n;});});return out;}
function holdsActive(b,name){return withBoard(b,()=>(PC[name]||0)>0);}
// other players (not this board's owner) without an active <name>
function playersWithout(name){const me=playerOfBoard(S);if(!me)return 0;const nm=String(name).replace(/\.$/,"").trim();
  return D.players.filter(q=>!sameP(q,me)&&!holdsActive(q.board,nm)).length;}
function calcMetrics(have,earned,tc){
  let gold=0,reduce=0,craft=0,infl=0,faith=0,doubt=0,scale=0,infraUp=0,extort=0,extTrig=0;
  const seasonAdd={Spring:0,Summer:0,Fall:0,Winter:0};
  const phaseCount={};
  const naturalCount=Object.keys(PC).filter(n=>NATURAL.has(n)).reduce((a,n)=>a+PC[n],0)
    +(SIMPLE?S.placed.filter(p=>p.fac&&pActive(p)&&!NATURAL.has(p.name)).length:0);   // SIMPLE: faction pursuits are Natural
  function eat(atoms,active,q){
    atoms.forEach(a=>{
      const ph=a.season?"season":(PHASE[a.cat]||"other");phaseCount[ph]=(phaseCount[ph]||0)+q;
      if(!active)return;
      if(a.scale){const cnt=a.scale.of==="natural"?naturalCount:(tc[cap(a.scale.of)]||0);scale+=a.scale.per*cnt*q;return;}
      if(a.cat==="extort"){if(a.val&&(a.every||/^Extort\s*\d+\.?$/i.test((a.text||"").trim())))extort+=a.val*q;   // bare "Extort N" (or "twice") = every Empire Phase
        else if(a.val&&a.without)extort+=a.val*q*playersWithout(a.without);                                        // "Extort N per player without X"
        else extTrig+=q;return;}
      if(!a.flat)return;
      if(a.season){seasonAdd[a.season]+=a.val*q;return;}
      if(a.cat==="gold")gold+=a.val*q;
      else if(a.cat==="upkeep")reduce+=(-a.val)*q;
      else if(a.cat==="craft")craft+=a.val*q;else if(a.cat==="influence")infl+=a.val*q;
      else if(a.cat==="faith")faith+=a.val*q;else if(a.cat==="doubt")doubt+=a.val*q;
    });
  }
  Object.keys(PC).forEach(n=>{const r=R[n],q=PC[n];
    eat(r.innate,true,q); if(r.mastery_raw)eat(r.mastery,!!earned[n],q);});
  itm();
  // Infrastructure / Wonders pay upkeep only while active (not building, Damaged or under repair)
  const freeT=noUpkeepTiers();   // "No Upkeep on <Tier> Infrastructure" (Masonry / Trade Guild / College of Engineering)
  Object.keys(S.infra).forEach(n=>{const on=infraOn(n);eat(INFRA[n].atoms,on,1);if(on&&!S.facInfra.includes(n)&&!freeT[INFRA[n].tier])infraUp+=INFRA[n].upkeep;});
  Object.keys(S.wonders).forEach(n=>{const on=infraOn(n);eat(WON[n].atoms,on,1);if(on)infraUp+=WON[n].upkeep;});
  {const me=playerOfBoard(S);if(me)S.placed.forEach(q=>{if(!pActive(q)||!settBesieged(me,q.sid))return;
     ((R[q.name]||{}).innate||[]).forEach(a=>{if(a.cat==="craft"&&a.flat&&!a.season)craft-=a.val;});});}   // besieged: no Craft X
  {const tb=facTypeBonus(S),me=playerOfBoard(S);if(tb)S.placed.forEach(q=>{if(q.fac||!pActive(q)||!tb.types.includes((R[q.name]||{}).type))return;
     if(me&&settBesieged(me,q.sid))return;craft+=tb.craft;});}
  {const me=playerOfBoard(S),pid=me?String(me.id):null,war=playerAtWar(pid),cpg=[];
   srcMatch(S,"faith_war").forEach(x=>{if(!!x.m[2]!==war)faith+=+x.m[1];});
   srcMatch(S,"faith_per_war").forEach(x=>{faith+=(+x.m[1])*D.players.filter(q=>pid&&String(q.id)!==pid&&effPair(pid,q.id).war).length;});
   srcMatch(S,"gold_per_craft").forEach(x=>cpg.push(+x.m[1]));
   if(pid)D.players.forEach(q=>{if(String(q.id)===pid||!effPair(pid,q.id).trade)return;
     srcMatch(q.board,"partner_craft").forEach(x=>{craft+=+x.m[1];});});
   cpg.forEach(v=>{scale+=v*craft;});
   if(me&&mapState().grid){const prov=provinceOf(me),bt=srcMatch(S,"army_free_province").length,bo=srcMatch(S,"army_upkeep_outside"),
       lh=srcMatch(S,"army_upkeep_home");
     let outside=false;S.armies.forEach(a=>{const k=armyHex(me,a);if(!k)return;const c=armyUpkeep(a);
       if(prov.has(k)){if(bt)reduce+=c;}else outside=true;});
     if(outside)bo.forEach(x=>{reduce+=+x.m[1];});                                    // once, while an Army is not in Province
     danegeldRows(me).forEach(x=>{extort+=x.amt;});   // Danegeld: upkeep still owed here; the at-war controller pays it (Extort, Empire Phase)
     if(lh.length&&S.armies.some(a=>{const k=armyHex(me,a);return k&&(S.settlements||[]).some(s=>settHex(me,s)===k);}))lh.forEach(x=>{reduce+=+x.m[1];});}}
  const pursUp=S.placed.reduce((a,p)=>a+pursuitUpkeep(p),0);
  const armyGross=S.armies.reduce((s,a)=>s+armyUpkeep(a),0);
  const netArmy=Math.max(0,armyGross-reduce);
  const unusedReduce=Math.max(0,reduce-armyGross);
  const baseNet=gold+scale-infraUp-pursUp-netArmy;
  return {gold,reduce,craft,infl,faith,doubt,scale,infraUp,pursUp,armyGross,netArmy,unusedReduce,baseNet,seasonAdd,phaseCount,extort,extTrig};
}
function computeTotals(have,earned,tc){
  const m=calcMetrics(have,earned,tc);
  set("t_gold",fmt(m.gold));set("t_scale",fmt(m.scale));set("t_upkeep",fmt(-m.infraUp));set("t_pupkeep",fmt(-m.pursUp));
  set("t_reduce",m.reduce?("pool "+fmt(m.reduce)+(m.unusedReduce?(" · "+fmt(-m.unusedReduce)+" unused"):"")):"0");
  set("t_army",fmt(-m.netArmy));set("t_craft",fmt(m.craft));
  set("t_ext",fmt(m.extort)+(m.extTrig?" · "+m.extTrig+" triggered":""));
  set("t_trade",fmt(m.craft*DATA.tradePerCraft)+" g");set("t_infl",fmt(m.infl));set("t_po",fmt(m.faith-m.doubt+poModTotal(S)));
  const cs0=curSeason(),sa0=((m.seasonAdd||{})[cs0]||0)+(SEASON_DBL_TYPE(cs0)?husbandryGoldFor(S,cs0):0),wt=winterTax(S),tx0=cs0==="Winter"?wt.total:0,tr0=tradeIncome(S,cs0),net0=m.baseNet+sa0+tx0+tr0.total;
  const ng=document.getElementById("netgold");ng.textContent=fmt(net0);
  ng.className="n "+(net0<0?"neg":net0>0?"pos":"");
  document.getElementById("netnote").innerHTML=[
    (()=>{const nb=(S.placed||[]).filter(q=>q.bt>0).length;return nb?nb+" building":"";})(),
    sa0?cs0+" "+fmt(sa0):"",
    cs0==="Winter"?"Winter tax "+fmt(wt.base)+(wt.adj?" "+(wt.adj>0?"+":"−")+Math.abs(wt.adj)+" PO":"")+((wt.dbl||[]).length?" ×2 ("+wt.dbl.join(", ")+")":""):"",
    tr0.total?"trade "+fmt(tr0.total)+" ("+tr0.lines.join(", ")+"; Host "+(hostP()?hostP().name:"?")+")":""].filter(Boolean).join(" · ");
  const sg=document.getElementById("seasons");sg.innerHTML="";
  const cse=curSeason();
  SEASONS.forEach(s=>{const v=m.baseNet+m.seasonAdd[s]+(s==="Winter"?wt.total:0)+tradeIncome(S,s).total;const c=document.createElement("div");c.className="scell"+(s===cse?" cur":"");
    c.innerHTML='<div class="sn">'+s+'</div><div class="sv" style="color:'+(v<0?cvar("--upkeep"):v>m.baseNet?cvar("--income"):cvar("--ink"))+'">'+fmt(v)+'</div>';sg.appendChild(c);});
  const leg=document.getElementById("legend");leg.innerHTML="";
  Object.keys(PHASE_LABEL).forEach(ph=>{const li=document.createElement("div");li.className="li";
    li.innerHTML='<span class="sw" style="background:'+cvar(PHASE_COLOR[ph])+'"></span>'+PHASE_LABEL[ph]+(m.phaseCount[ph]?(" ("+m.phaseCount[ph]+")"):"");leg.appendChild(li);});
  window._net=net0;
  renderInfluence();renderPOMods();renderMiniStand();
}
// Winter tax (rules: "gain tax income equal to your Settlements' tiers, adjusted by any modifiers"):
// SETTLEMENTS[tier].tax_income for each Settlement, plus the Public Order "Tax income ±X per settlement" effect at the board's PO level
// (applied to each Settlement that pays tax; never below 0 per Settlement).
function poTaxMod(v,b){let mod=0;const src=[],dbl=poDoubled();poActiveKeys(v||0,b).forEach(k=>{const e=POB(k),txt=Array.isArray(e)?e.join(" "):String(e||"");
    const m=txt.match(/Tax income\s*([+\-\u2212]\s?\d+)\s*per settlement/i)||txt.match(/([+\-\u2212]\s?\d+)\s*Tax Income per Settlement/i);
    if(m){const bn=Array.isArray(e)?e[0]:String(k),x=parseInt(m[1].replace(/\s/g,"").replace("\u2212","-"),10)*(dbl[bn]?2:1);mod+=x;src.push(bn+" "+(x>0?"+":"")+x+(dbl[bn]?" (×2)":""));}});
  return {mod,src};}
// "Tax Income is Doubled" (e.g. Castle Hall) on an active piece doubles the Settlements' tax
function taxDouble(b){return withBoard(b,()=>Object.keys(PC).filter(n=>!!hitOf("h:"+n,"tax_double")));}
function winterTax(b){const sets=b.settlements||[],pm=poTaxMod(b.po||0,b),mod=pm.mod;let base=0,adj=0;
  const pl=playerOfBoard(b),dest=(D.bandit||{}).dest||{};let destab=0;
  const occT=occupyTaxOnly(b),outside=[];
  sets.forEach(s=>{const t=settUnbuilt(s)?0:((((DATA.settlements||{})[s.tier]||{}).tax_income)||0);if(!t)return;
    if(occT&&!settInside(b,s)){outside.push(s.name||s.tier);return;}
    if(pl&&dest[pl.id+":"+s.id]){destab+=t+Math.max(-t,mod);return;}base+=t;adj+=Math.max(-t,mod);});
  const dbl=taxDouble(b),k=dbl.length?2:1;
  return {base,mod,adj,src:pm.src.concat(dbl.map(n=>n+" ×2")).concat(outside.length?[(b.faction||"Occupy")+": not inside "+outside.join(", ")]:[]),destab,dbl,outside,total:(base+adj)*k};}
// faction "to collect taxes … end your turn inside it" (The Squatters' Crown): a Settlement pays tax only with one of your Armies inside
function occupyTaxOnly(b){return !!hitOf("F:"+((b||{}).faction||""),"occupy_tax");}
function settInside(b,s){return (b.armies||[]).some(a=>String(a.sid)===String(s.id));}
function settTax(b,s){if(settUnbuilt(s))return 0;const t=(((DATA.settlements||{})[s.tier]||{}).tax_income)||0;if(occupyTaxOnly(b)&&!settInside(b,s))return 0;return t?(t+Math.max(-t,poTaxMod(b.po||0,b).mod))*(taxDouble(b).length?2:1):0;}
// Trade income (rules): for each active Trade Agreement, both players gain income_per_craft × the Host's Craft X —
// only on turns when one of the two is the Host; both need active Dirt Roads; none in TRADE_RULES.no_trade_season (Spring).
function tradeIncome(b,season){const sea=season||curSeason(),out=tradeRaw(b,sea),me=D.players.find(p=>p.board===b);if(!me)return out;
  {const ex=srcMatch(b,"trade_extra").reduce((a,x)=>a+(+x.m[1]),0);
    if(ex&&sameP(hostP(),me)&&!(DATA.noTradeSeason&&sea===DATA.noTradeSeason)&&hasRoad(me.id)){const g=ex*(DATA.tradePerCraft||100)*(boardMetrics(b).craft||0);
      if(g){out.total+=g;out.lines.push("+"+ex+" partners (Host) +"+g);}}}
  {const m=srcMatch(b,"trade_mult")[0];if(m&&out.total){const k=m.m[1].toLowerCase()==="thrice"?3:2,add=out.total*(k-1);out.total+=add;out.lines.push(m.n+" ×"+k+" +"+add);}}
  const icp=((D.bandit||{}).ic||{})[me.id];if(icp&&out.total&&sameP(hostP(),me)){out.lines.push("Intercept Caravan (bandits) −"+out.total);out.intercepted=out.total;out.total=0;}
  if(isVassal(me.id)&&out.total){const h=out.total/2;out.total-=h;out.lines.push("½ to Suzerain "+pname(diplo().suzerain[String(me.id)])+" −"+h);}
  vassalsOf(me.id).forEach(v=>{const h=tradeRaw(v.board,sea).total/2;if(h){out.total+=h;out.lines.push("½ of Vassal "+v.name+" +"+h);}});
  return out;}
function tradeRaw(b,season){const sea=season||curSeason(),out={total:0,lines:[]};
  if(DATA.noTradeSeason&&sea===DATA.noTradeSeason)return out;
  const me=D.players.find(p=>p.board===b),h=hostP();if(!me||!h)return out;
  const rate=DATA.tradePerCraft||100;
  D.players.forEach(q=>{if(sameP(q,me))return;const x=effPair(me.id,q.id);if(x.household||!x.trade||x.war)return;
    if(!(sameP(h,me)||sameP(h,q)))return;if(!hasRoad(me.id)||!hasRoad(q.id))return;
    const g=rate*(boardMetrics(h.board).craft||0);out.total+=g;out.lines.push(q.name+" "+(g>=0?"+":"")+g);});
  return out;}
function seasonNet(b,season){const m=boardMetrics(b),sea=season||curSeason(),sa=((m.seasonAdd||{})[sea]||0)+(SEASON_DBL_TYPE(sea)?husbandryGoldFor(b,sea):0),tx=sea==="Winter"?winterTax(b).total:0,tr=tradeIncome(b,sea).total;
  return {net:m.net+sa+tx+tr,base:m.net,seasonal:sa,tax:tx,trade:tr,m};}
// metrics for any board (used by dashboards)
// direct gold income from active Husbandry Holdings (SEASONS: "<Type> Income is doubled")
function husbandryGoldFor(b,sea){const t=SEASON_DBL_TYPE(sea);if(!t)return 0;return withBoard(b,()=>{let g=0;const earned=SIMPLE?{}:computeEarned(new Set(Object.keys(PC))).earned;
  Object.keys(PC).forEach(n=>{const r=R[n]||{};if(r.type!==t)return;const eat=at=>(at||[]).forEach(a=>{if(a.cat==="gold"&&a.flat&&!a.season&&!a.scale)g+=a.val*PC[n];});eat(r.innate);if(earned[n])eat(r.mastery);});return g;});}
function SEASON_DBL_TYPE(sea){const m=/^(\w[\w ]*?) Income is doubled/i.exec(((SEAS[sea]||{}).effect)||"");return m?m[1]:null;}
function boardMetrics(b){
  return withBoard(b,()=>{const have=new Set(Object.keys(PC));const {earned,tc}=computeEarned(have);
    const m=calcMetrics(have,earned,tc);
    return {net:m.baseNet,gold:m.gold,craft:m.craft,infl:m.infl,po:m.faith-m.doubt,faith:m.faith,doubt:m.doubt,netArmy:m.netArmy,seasonAdd:m.seasonAdd};});
}

// ---- Public Order tracker ----
function poBandName(v){let best=null;Object.keys(PO).map(Number).sort((a,b)=>a-b).forEach(k=>{if(k<=v)best=k;});return best!=null?POB(best):null;}
// Public Order is cumulative in both directions: at +4 bands 1..4 are all active; at −3 bands −1..−3 are all active.
function poActiveKeys(v,b){if(b&&poImmune(b))return [];
  return Object.keys(PO).map(Number).filter(k=>v>0?(k>=1&&k<=v):v<0?(k<=-1&&k>=v):k===0).sort((a,b)=>Math.abs(a)-Math.abs(b));}
function poActiveEffects(v,b){const dbl=poDoubled();return poActiveKeys(v,b).map(k=>POB(k)).filter(x=>x&&!/^no effect$/i.test(x[1]))
  .map(x=>dbl[x[0]]?[x[0],x[1]+" ×2 ("+dbl[x[0]]+")"]:x);}
// Holdings that change Public Order effects: "No longer affected by all Public Order effects" (this board) and
// "<Band>, <Band>, & <Band> effects are doubled for all players" (any player's active Holding).
const PO_IMM=Object.keys(R).filter(n=>!!hitOf("h:"+n,"po_immune"));
const PO_DBL={};Object.keys(R).forEach(n=>{const m=hitOf("h:"+n,"po_band_double");
  if(m)PO_DBL[n]=m[1].split(/\s*(?:,|&|\band\b)\s*/).map(x=>x.trim()).filter(Boolean);});
function poImmune(b){const n=PO_IMM.find(x=>holdsActive(b,x));return n||null;}
function poDoubled(){const out={};Object.keys(PO_DBL).forEach(n=>{const q=(D.players||[]).find(p=>holdsActive(p.board,n));
  if(q)PO_DBL[n].forEach(bn=>out[bn]=n+" · "+q.name);});return out;}
function renderPO(){
  const v=Math.max(PO_MIN,Math.min(PO_MAX,S.po||0));S.po=v;
  set("poVal",v);const band=poBandName(v);
  document.getElementById("poBand").textContent=band?band[0]:"";
  {const bs=document.getElementById("poBandS");if(bs)bs.textContent=(band?band[0]+" ":"")+(S.po>0?"+":"")+(S.po||0);}
  const act=poActiveEffects(v,S),imm=poImmune(S);
  document.getElementById("poEffect").textContent=imm?("no effects — "+imm):act.length?("active ("+act.length+"): "+act.map(b=>b[1]).join(" · ")):"no active effects";
  const on=new Set(poActiveKeys(v,S)), curK=Math.max(...Object.keys(PO).map(Number).filter(k=>k<=v));
  const lad=document.getElementById("poLadder");
  const ks=Object.keys(PO).map(Number).sort((a,b)=>b-a),near=k=>PO_FULL||Math.abs(k-curK)<=2||(on.has(k)&&k!==0);
  lad.innerHTML=ks.filter(near).map(k=>{const b=POB(k);
    return '<div class="pr'+(on.has(k)?' on '+(k<0?'neg':'pos'):'')+(k===curK?' cur':'')+'"><span class="v">'+(k>0?'+':'')+k+'</span><span>'+esc(b[0])+'</span><span>'+esc(b[1])+'</span></div>';}).join("")+
    (ks.some(k=>!near(k))||PO_FULL?'<div class="more" id="poMore">'+(PO_FULL?'▴ less':'▾ full track')+'</div>':'');
  {const mo=document.getElementById("poMore");if(mo)mo.onclick=()=>{PO_FULL=!PO_FULL;renderPO();};}
}

let PO_FULL=false;
