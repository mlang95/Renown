// ---- Dashboards view ----
// ---- seasons ----
const SEAS=DATA.seasons||{},SEAS_ORDER=Object.keys(SEAS);
function curSeason(){if(!D.season||!SEAS[D.season])D.season=SEAS.Summer?"Summer":SEAS_ORDER[0];return D.season;}
function stepSeason(dl){const i=SEAS_ORDER.indexOf(curSeason());D.season=SEAS_ORDER[(i+dl+SEAS_ORDER.length)%SEAS_ORDER.length];}
// ---- influence per turn (INFLUENCE_GAIN) ----
const IG=DATA.influenceGain||{};
function playerOfBoard(b){return D.players.find(p=>p.board===b);}
function igVal(k){const m=String((IG[k]||{}).change||"0").match(/^([+-]?\d+)/);return m?+m[1]:0;}
function eraIdx(){const ks=Object.keys(ERAS).sort((a,b)=>ERAS[a].renown-ERAS[b].renown);return Math.max(0,ks.indexOf(currentEra()));}
function playerAtWar(pid){return !!pid&&D.players.some(q=>String(q.id)!==String(pid)&&effPair(pid,q.id).war);}
function influenceRowsBase(b){
  const p=playerOfBoard(b),pid=p?String(p.id):null,d=diplo(),rows=[];
  const add=(k,cnt,val)=>{if(IG[k])rows.push({k,cnt,val:val||0});};
  if(IG.Era){const e=ERAS[currentEra()]||{},parts=String(IG.Era.change).split("/").map(x=>parseInt(x,10));add("Era",1,e.influence_per_turn??(parts[eraIdx()]||0));}
  const pairs=pid?D.players.filter(q=>String(q.id)!==pid).map(q=>effPair(pid,q.id)).filter(x=>!x.household):[];
  const tpx=srcMatch(b,"trade_extra").reduce((a,x)=>a+(+x.m[1]),0),tp=pairs.filter(x=>x.trade).length+tpx;
  add("Trading Partners",tp,tp*igVal("Trading Partners"));
  const am=pid?D.players.filter(q=>sameAlliance(pid,q.id)).length:0;add("Alliances",am,am*igVal("Alliances"));
  const tiers=withBoard(b,()=>{const T={};Object.keys(INFRA).forEach(n=>{(T[INFRA[n].tier]=T[INFRA[n].tier]||[]).push(n);});return Object.keys(T).filter(t=>T[t].every(infraOn)).length;});
  add("Infrastructure tier completed",tiers,tiers*igVal("Infrastructure tier completed"));
  dbActive(b).forEach(x=>{const m=/(?:\+(\d+) Influence|(?<!Max )Influence \+(\d+))(?: (?:per turn|each Empire Phase))?/i.exec(x.text);if(m)rows.push({k:x.name+" ("+x.tier+" "+x.dom+")",cnt:1,val:+(m[1]||m[2])});});
  const fa=(b.armies||[]).filter(a=>(a.count||0)>=EQ.army_max).length;add("Fully Mustered Army",fa,fa*igVal("Fully Mustered Army"));
  const ce=+b.condemned||0;add("Condemned Envoy last turn",ce,ce*igVal("Condemned Envoy last turn"));
  const war=playerAtWar(pid)&&!(p&&fxOf(p,"ignoreWar").length)?1:0,noLoss=dbActive(b).find(x=>/No longer lose Influence while at War/i.test(x.text));
  if(IG["At War"])rows.push({k:"At War"+(war&&noLoss&&igVal("At War")<0?" ("+noLoss.name+": no loss)":""),cnt:war,val:(noLoss&&igVal("At War")<0)?0:war*igVal("At War")});
  const mw=withBoard(b,()=>S.placed.filter(q=>pActive(q)&&(R[q.name]||{}).type==="Monument").length+Object.keys(S.wonders).filter(infraOn).length);
  add("Monuments & Wonders",mw,mw*igVal("Monuments & Wonders"));
  const oth=boardMetrics(b).infl;add("Other sources",oth?1:0,oth);
  royalMarriage(b).forEach(x=>{if(x.infl)rows.push({k:x.src,cnt:1,val:x.infl});});
  // Public Order bands "±N Influence" apply when Influence is gained (cumulative bands; Plague Pit immune, Charnel House ×2)
  {const dbl=poDoubled(),po=Math.max(PO_MIN,Math.min(PO_MAX,b.po||0));
   poActiveKeys(po,b).forEach(k=>{const e=POB(k);if(!Array.isArray(e))return;const m=String(e[1]).match(/^([+\-\u2212]\s?\d+)\s*Influence$/i)||String(e[1]).match(/^Influence\s*([+\-\u2212]\s?\d+)$/i);if(!m)return;
     const v=parseInt(m[1].replace(/\s/g,"").replace("\u2212","-"),10)*(dbl[e[0]]?2:1);
     rows.push({k:"Public Order: "+e[0]+(dbl[e[0]]?" ×2":""),cnt:1,val:v});});}
  if(p)fxOf(p,"pool").forEach(f=>{const dv=b.domains||{};
    const cnt=f.per==="Rising"?T_DOMS.filter(d=>(dv[d]||0)>=RIS).length:f.per==="Established"?T_DOMS.filter(d=>(dv[d]||0)>=EST).length:
      f.per==="others"?Math.max(0,D.players.length-1):f.per==="war"?(playerAtWar(pid)?1:0):
      f.per==="holdings"?Math.floor(withBoard(b,()=>S.placed.filter(q=>pActive(q)).length)/(f.n||1)):0;
    rows.push({k:f.src,cnt,val:f.val*f.q*cnt});});
  return rows;}
// Vassal: the Suzerain collects the first VASSAL_INFLUENCE_TAKE Influence the Vassal generates each turn
function influenceRows(b){const rows=influenceRowsBase(b),p=playerOfBoard(b),T=+DATA.vassalInfluenceTake||0;if(!p||!T)return rows;
  const take=bb=>Math.min(T,Math.max(0,influenceRowsBase(bb).reduce((a,r)=>a+r.val,0))),sz=diplo().suzerain[String(p.id)];
  if(sz){const t=take(b);if(t)rows.push({k:"Suzerain "+pname(sz)+" takes",cnt:1,val:-t});}
  vassalsOf(p.id).forEach(v=>{const t=take(v.board);if(t)rows.push({k:"Vassal "+v.name,cnt:1,val:t});});
  return rows;}
function influenceTotal(b){return isSpring()?0:Math.max(0,influenceRows(b).reduce((a,r)=>a+r.val,0));}   // Nothing below zero
// ---- Public Order modifiers (PO_MODIFIERS; 1 per instance) ----
const POM=DATA.poModifiers||{faith:{},doubt:{}};
function poModRows(b){b.poMods=b.poMods||{};const p=playerOfBoard(b),pid=p?String(p.id):null,rows=[];
  const auto={"Deficit":()=>boardMetrics(b).net<0?1:0,"State of Alarm":()=>playerAtWar(pid)&&!(p&&fxOf(p,"ignoreWar").length)?1:0,
    "War Weariness":()=>srcHas(b,"immune_war_weariness")?0:(+b.lossStreak||0),"Lasting Legacy":()=>b.lastBattle==="won"?1:0,
    "Insolvency":()=>+b.insolv||0,"Mounting Panic":()=>p?besiegedCount(p):0,
    "Local Unrest":()=>p?unrestCamps(p).length:0,
    "Border Tension":()=>p?intrudersOf(p).filter(x=>!x.ally).length:0,"Invasion":()=>p?intrudersOf(p).filter(x=>x.war).length:0};
  ["faith","doubt"].forEach(side=>Object.keys(POM[side]||{}).forEach(k=>{const a=auto[k];
    rows.push({side,k,desc:POM[side][k],auto:!!a,n:a?a():(+b.poMods[k]||0)});}));
  royalMarriage(b).forEach(x=>{if(x.faith)rows.push({side:"faith",k:x.src,desc:"Royal Marriage Alliance member",auto:true,n:x.faith});});
  // faction "Gain Faith|Doubt +N per Empire Phase" (own faction only; "for every …" variants are counted in calcMetrics)
  if(b.faction)srcMatch(b,"fd_per_empire").filter(x=>x.n===b.faction).forEach(x=>
    rows.push({side:x.m[1].toLowerCase(),k:b.faction,desc:x.m[1]+" +"+x.m[2]+" per Empire Phase",auto:true,n:+x.m[2]}));
  // "Each other player gains Doubt +N each Empire Phase per Sacred War you're on" (Prophets of War): its owner keeps the Sacred War count (gains none)
  D.players.forEach(q=>srcMatch(q.board,"sacred_war_each").filter(x=>x.n===q.board.faction).forEach(x=>{
    const K="Sacred Wars · "+q.board.faction,cnt=+((q.board.poMods||{})[K])||0;
    if(q.board===b)rows.push({side:x.m[1].toLowerCase(),k:K,desc:"Sacred Wars you're on (each other player: "+x.m[1]+" +"+x.m[2]+" each)",auto:false,n:0});
    else if(cnt)rows.push({side:x.m[1].toLowerCase(),k:x.n+" · "+q.name,desc:cnt+" Sacred War"+(cnt>1?"s":"")+" ("+q.name+")",auto:true,n:cnt*+x.m[2]});}));
  if(p){const INN="trade_partner_faith",cr=q=>boardMetrics(q.board).craft;
    srcMatch(b,INN).forEach(x=>{const L=D.players.filter(q=>!sameP(q,p)&&effPair(p.id,q.id).trade&&cr(q)>=+x.m[2]);
      rows.push({side:"faith",k:x.n,desc:"Trade Partners with Craft "+x.m[2]+"+: "+(L.map(q=>q.name).join(", ")||"none"),auto:true,n:+x.m[1]*L.length});});
    if(boardMetrics(b).craft>0)D.players.forEach(q=>{if(sameP(q,p)||!effPair(p.id,q.id).trade)return;
      srcMatch(q.board,INN).forEach(x=>{if(boardMetrics(b).craft>=+x.m[2])rows.push({side:"faith",k:x.n+" · "+q.name,desc:"your Craft "+boardMetrics(b).craft+" ≥ "+x.m[2],auto:true,n:+x.m[3]});});});}
  if(p)bordersOf(p).forEach(q=>srcMatch(q.board,"border_fd").forEach(x=>
    rows.push({side:x.m[1].toLowerCase(),k:x.n+" · "+q.name,desc:"bordering "+q.name,auto:true,n:+x.m[2]})));
  return rows.concat(epRows(b));}
const TOT_TIPS={"t_gold": "Unconditional gold (+X) from your active Pursuits (Innate, and Mastery once earned) and active Infrastructure / Wonders. Season-only gold, scaling gold, Winter tax and trade are counted separately.", "t_scale": "Gold that multiplies by a count — e.g. Manor House: +100 per active Natural Pursuit (its Mastery: +100 per active Energy Pursuit).", "t_upkeep": "Upkeep of your built Infrastructure and Wonders. Faction Infrastructure pays none.", "t_pupkeep": "PU_TEXT", "t_reduce": "The sum of “Upkeep −X” effects on your active pieces. The pool is spent against Army upkeep; anything left over is unused.", "t_army": "Army upkeep: each Army costs its Retinue type's cost; the total of all Armies minus the reduction pool, never below 0.", "t_craft": "CRAFT", "t_trade": "Craft X × income per Craft: what each Trade Agreement pays both players on turns when you are the Host. None in Spring; both players need active Dirt Roads; none while at war.", "t_infl": "Unconditional “Influence +X” from your active pieces. Part of your Influence per turn — the full breakdown is on the Table.", "t_po": "Unconditional Faith minus Doubt from your active pieces, plus the Faith / Doubt modifiers under Public Order. Applied to Public Order at End turn.", "t_ext": "EXTORT"};
// SIMPLE has no Mastery: these two tips drop it, and the scaling example quotes the live Manor House text
function totTipSimple(k){if(k==="t_gold")return "Unconditional gold (+X) from your active Pursuits and active Infrastructure / Wonders. Season-only gold, scaling gold, Winter tax and trade are counted separately.";
  if(k==="t_scale"){const m=(R["Manor House"]||{}).innate_raw;return "Gold that multiplies by a count"+(m?" — e.g. Manor House: "+String(m).replace(/^\s*Natural;\s*/i,"").replace(/\*\*/g,"").replace(/\.\s*$/,""):"")+".";}
  return null;}
function totTip(k){let t=(SIMPLE&&totTipSimple(k))||TOT_TIPS[k]||"";
  if(t==="PU_TEXT"){const bt=(PUP.byType||{});t="Fixed by Pursuit type: "+Object.keys(bt).filter(x=>x!=="Other").map(x=>x+" "+bt[x]).join(", ")+", all others "+(bt.Other??PUP.def??0)+". None for faction pieces or Pursuits still building.";}
  if(t==="CRAFT")t=GLOSS["Craft"]||"Craft +X from your active pieces.";
  if(t==="EXTORT")t=(GLOSS["Extort X"]||"Take X from the stated source.")+" Flat Extort from your active pieces is summed here; conditional ones are counted as triggered. Not included in net gold \u2014 the gold comes from the stated source when it resolves (Empire Phase, Income & Upkeep).";
  return t;}
// ---- Empire Phase Faith/Doubt: DOMAIN_BOARD standings (cumulative) + active pieces ----
// self:  "<Name>: Faith|Doubt +N each Empire Phase"
// lower: "Each Empire Phase, each [other] non-allied player with a lower <Domain> value gains Faith|Doubt +N"
// floor: "If your Public Order would be set below N, set it to N"
const EP_SELF=/(Faith|Doubt)\s*\+(\d+)\s+each Empire Phase/i,EP_LOW=/Each Empire Phase, each (?:other )?non-allied player with a lower (\w+) value gains (Faith|Doubt)\s*\+(\d+)/i,
      EP_FLOOR=/If your Public Order would be set below (-?\d+), set it to (-?\d+)/i;
function epSources(b){const out=[],dv=b.domains||{},TIERS=[["Rising",RIS],["Established",EST],["Sovereign",SOV]];
  DOMAINS.forEach(d=>{const e=DBOARD[d];if(!e||typeof e!=="object")return;TIERS.forEach(([t,th])=>{const tx=e[t];if(!tx||(dv[d]||0)<th)return;
    const nm=String(tx).split(":")[0].trim(),m1=tx.match(EP_LOW),m2=!m1&&tx.match(EP_SELF),m3=tx.match(EP_FLOOR);
    if(m1)out.push({src:nm,kind:"lower",dom:m1[1],side:m1[2].toLowerCase(),val:+m1[3]});
    if(m2)out.push({src:nm,kind:"self",side:m2[1].toLowerCase(),val:+m2[2]});
    if(m3)out.push({src:nm,kind:"floor",below:+m3[1],to:+m3[2]});});});
  dbActive(b).filter(x=>x.free&&x.tier==="Sovereign").forEach(x=>{const m=String(x.text).match(EP_FLOOR);if(m)out.push({src:"Studium Generale · "+x.name,kind:"floor",below:+m[1],to:+m[2]});});
  withBoard(b,()=>{const have=new Set(Object.keys(PC)),{earned}=computeEarned(have);
    Object.keys(PC).forEach(n=>{[["h:",true],["hm:",!!earned[n]]].forEach(([k,on])=>{if(!on)return;
      const m=hitOf(k+n,"ep_lower");if(m)out.push({src:n,kind:"lower",dom:m[1],side:m[2].toLowerCase(),val:+m[3]});});});});
  return out;}
// allied: a Vassal inherits every Treaty its (top) Suzerain holds → allied to that Suzerain, the Suzerain's other Vassals,
// and the Suzerain's Alliance group. (Possible later carve-out: Trade Agreements.)
function topSuz(id){const d=diplo();let c=String(id),g=16;while(d.suzerain[c]&&g--)c=String(d.suzerain[c]);return c;}
// "While in that Alliance, each member gains Faith +N and +M Influence per turn" (Royal Marriage): applied to every member of
// the Alliance the faction's owner is in (the board doesn't record which Alliance the once-per-game ability formed)
function royalMarriage(b){const p=playerOfBoard(b),out=[];if(!p)return out;const d=diplo();
  D.players.forEach(q=>{const h=hitOf("F:"+(q.board.faction||""),"royal_marriage");if(!h)return;const m=h.slice();m[2]=m[2]||m[3];
    const inA=sameP(q,p)?!!d.member[topSuz(String(q.id))]:sameAlliance(String(p.id),String(q.id));
    if(inA)out.push({src:q.board.faction+" · "+q.name,faith:+m[1],infl:+m[2]});});
  return out;}
function sameAlliance(a,b){a=String(a);b=String(b);if(a===b)return false;const d=diplo(),ra=topSuz(a),rb=topSuz(b);
  if(ra===rb)return true;                                   // same Suzerain household
  const g=d.member[ra];return !!g&&g===d.member[rb];}
function poFloor(b){const f=epSources(b).filter(x=>x.kind==="floor"),t=poTextFloor(b);if(t)f.push(t);return f.length?f.reduce((a,x)=>x.to>a.to?x:a):null;}
function applyPOFloor(b,v){const f=poFloor(b);if(f&&v<f.below)v=f.to;const c=poCap(b);return c!=null&&v>c?c:v;}
function epRows(b){const rows=[],me=playerOfBoard(b),mid=me?String(me.id):null,dv=b.domains||{};
  epSources(b).filter(x=>x.kind==="self").forEach(x=>rows.push({side:x.side,k:x.src,desc:x.side[0].toUpperCase()+x.side.slice(1)+" +"+x.val+" each Empire Phase",auto:true,n:x.val}));
  if(mid)D.players.forEach(q=>{if(String(q.id)===mid||sameAlliance(String(q.id),mid))return;const qv=q.board.domains||{};
    epSources(q.board).filter(x=>x.kind==="lower"&&(dv[x.dom]||0)<(qv[x.dom]||0)).forEach(x=>
      rows.push({side:x.side,k:x.src+" · "+q.name,desc:q.name+"'s "+x.dom+" "+(qv[x.dom]||0)+" > your "+(dv[x.dom]||0)+", not allied",auto:true,n:x.val}));});
  if(mid)D.players.forEach(q=>{if(String(q.id)===mid)return;          // other players' Holdings aimed at you
    withBoard(q.board,()=>Object.keys(PC).filter(n=>PC[n]>0))
    .forEach(n=>{let m=hitOf("h:"+n,"fd_others_without");
      if(m&&!holdsActive(b,m[1].trim()))rows.push({side:m[2].toLowerCase(),k:n+" · "+q.name,desc:"no "+m[1].trim(),auto:true,n:+m[3]});
      m=hitOf("h:"+n,"fd_per_treaty");
      if(m&&!isVassal(mid)){const x=effPair(mid,q.id),c=x.household?0:(x.trade?1:0)+(x.nap?1:0)+(sameAlliance(mid,String(q.id))?1:0);
        if(c)rows.push({side:m[1].toLowerCase(),k:n+" · "+q.name,desc:c+(c>1?" Treaties":" Treaty")+" with "+q.name+" (not Peace)",auto:true,n:+m[2]*c});}});});
  return rows;}
function poModTotal(b){const t=poModRows(b).reduce((a,r)=>a+(r.side==="faith"?r.n:-r.n),0);return t;}
function dpButtons(p,i){const b=p.board,n=b.dp||0;if(n<=0)return "";
  return '<span class="dpask"><b>'+n+' Domain Point'+(n>1?'s':'')+'</b> to spend: '+DOMAINS.filter(d=>(+((b.domains||{})[d])||0)<SOV).map(d=>'<button class="dpsp" data-pi="'+i+'" data-dom="'+d+'">'+d+' +1</button>').join('')+   // a Domain at its maximum takes no more points
    '<button class="dpsk" data-pi="'+i+'" title="drop one unspent point">skip</button></span>';}
function renderDP(){const box=document.getElementById("dpBox");if(!box)return;const i=D.active,h=dpButtons(D.players[i]||{board:S},i);
  box.style.display=h?"":"none";box.innerHTML=h;}
// spend one of p's Domain Points on Domain d (null = skip); false if there's no point or d is already at its maximum
function dpSpend(p,d){const bd=p&&p.board;if(!bd||!(bd.dp>0))return false;
  if(d){bd.domains=bd.domains||{};const old=+(bd.domains[d]||0),next=Math.min(SOV,old+1);if(old>=SOV)return false;bd.domains[d]=next;armStanding(p,d,old,next);}
  bd.dpLog=(bd.dpLog||[]).concat([{turn:tTurn(),dom:d||"(skipped)"}]).slice(-12);bd.dp--;return true;}
document.addEventListener("click",e=>{const b=e.target.closest(".dpsp,.dpsk");if(!b)return;const p=D.players[+b.dataset.pi];
  if(dpSpend(p,b.classList.contains("dpsp")?b.dataset.dom:null)){save();render();}});
// ---- mini standings (Board, left column): active player's Domains, Rest-Phase points, unlocked Domain effects + Pursuits ----
let MINI_OPEN=null;try{MINI_OPEN=JSON.parse(localStorage.getItem("renown_ministand")||"null");}catch(e){}
function renderMiniStand(){const box=document.getElementById("miniStand");if(!box)return;
  if(!box.dataset.w){box.dataset.w=1;box.addEventListener("toggle",()=>{MINI_OPEN=box.open;try{localStorage.setItem("renown_ministand",JSON.stringify(MINI_OPEN));}catch(e){}});}
  if(MINI_OPEN!=null&&box.open!==MINI_OPEN)box.open=MINI_OPEN;
  const dv=S.domains||{},TI=[["Rising",RIS],["Established",EST],["Sovereign",SOV]],i=D.active,p=D.players[i]||{board:S};
  document.getElementById("miniStandSum").textContent=DOMAINS.map(d=>d.slice(0,3)+" "+(dv[d]||0)).join(" · ")+((S.dp||0)>0?" · "+S.dp+" pt to spend":"");
  const pu=(d,t)=>Object.keys(R).filter(n=>new RegExp("^"+t+"\\s+"+d+"$","i").test(R[n].unlock_raw||"")).length;
  let h=dpButtons(p,i);
  h+=DOMAINS.map(d=>{const v=dv[d]||0,E=DBOARD[d]||{};
    return '<div class="dbk" style="--dc:'+DOMC[d]+'"><div class="dbk-h"><b>'+esc(d)+'</b><span class="note">'+v+' · '+domBand(v)+'</span></div>'+domTrackHTML(d,[p],canEdit(p))+
      '<div class="dbk-e">'+TI.map(([t,th])=>{const on=v>=th,nm=String(E[t]||"").split(":")[0].trim(),bfx=(BT.standingFx||{})[d+"|"+t];
        return '<span class="dbs'+(on?' on':'')+'" title="'+esc(t+" ("+th+"): "+(E[t]||"")+(bfx?" · Battle: "+bfx:"")+" · "+pu(d,t)+" Holdings unlock")+'">'+(on?'✓ ':'')+esc(nm||t)+'</span>';}).join('')+'</div></div>';}).join('');
  document.getElementById("miniStandBody").innerHTML=h;
  box.querySelectorAll("[data-dset]").forEach(c=>c.onclick=()=>{const [d,v]=c.dataset.dset.split("|");S.domains=S.domains||{};
    const old=+(S.domains[d]||0);S.domains[d]=old===+v?Math.max(0,+v-1):+v;armStanding(playerOfBoard(S),d,old,S.domains[d]);save();render();});}
function renderInfluence(){renderDP();const box=document.getElementById("inflBox");if(!box)return;const tot=influenceTotal(S);
  box.innerHTML='<div style="display:flex;align-items:center;gap:8px"><b>Influence / turn</b><span style="margin-left:auto;font-size:15px">'+(tot>0?'+':'')+tot+'</span></div>'+(isSpring()?'<div class="note">Spring: no Influence gained</div>':'')+
    '<div class="note">Breakdown, Envoys and modifiers: <a href="#" data-goto="table">Table ▸</a></div>';}
let PO_ACTIVE_ONLY=true;try{PO_ACTIVE_ONLY=localStorage.getItem("renown_po_active")!=="0";}catch(e){}
function renderPOMods(){const box=document.getElementById("poMods");if(!box)return;const rows=poModRows(S),tot=poModTotal(S),m=boardMetrics(S);
  {const pt=document.getElementById("poPT");if(pt)pt.textContent=fmt(m.po+tot)+" / turn";}
  const shown=r=>!PO_ACTIVE_ONLY||+r.n!==0,hid=rows.filter(r=>!shown(r)).length;
  box.innerHTML='<label class="note pomtog"><input type="checkbox" id="poActOnly"'+(PO_ACTIVE_ONLY?' checked':'')+'> active only'+(PO_ACTIVE_ONLY&&hid?' ('+hid+' hidden)':'')+'</label>'+
    '<div class="pomh">'+['faith','doubt'].map(side=>'<div><div class="lbl tipk" data-tip="'+esc(GLOSS[side==='faith'?'Faith X':'Doubt X']||'')+'">'+side.toUpperCase()+'</div>'+
    rows.filter(r=>r.side===side&&shown(r)).map(r=>'<div class="pomr"><span class="tipk" data-tip="'+esc(r.k+": "+r.desc)+'">'+esc(r.k)+'</span><span>'+
      (r.auto?'<b>'+r.n+'</b>':'<button class="pmd" data-k="'+esc(r.k)+'" data-d="-1">−</button><b>'+r.n+'</b><button class="pmd" data-k="'+esc(r.k)+'" data-d="1">+</button>')+'</span></div>').join('')+'</div>').join('')+'</div>'+
    '<div class="kv"><span class="k">PO / turn</span><span class="val">'+fmt(m.po)+' '+(tot<0?'−':'+')+' '+Math.abs(tot)+' = '+fmt(m.po+tot)+'</span></div>'+
    (()=>{const pf=poFloor(S);return pf?'<div class="kv"><span class="k">'+esc(pf.src)+'</span><span class="val">floor '+pf.to+'</span></div>':'';})();
  {const cb=box.querySelector("#poActOnly");if(cb)cb.onchange=()=>{PO_ACTIVE_ONLY=cb.checked;try{localStorage.setItem("renown_po_active",PO_ACTIVE_ONLY?"1":"0");}catch(e){}renderPOMods();};}
  box.querySelectorAll(".pmd").forEach(bt=>bt.onclick=()=>{S.poMods=S.poMods||{};const k=bt.dataset.k;S.poMods[k]=Math.max(0,(+S.poMods[k]||0)+(+bt.dataset.d));save();render();});}
// ---- siege calculator (SIEGE_CALCULUS / SIEGE_SOURCE_VALUES) ----
function siegeState(){D.siege=D.siege||{tp:null,sid:null,mode:"Lay Siege",army:false,att:0,def:0};return D.siege;}
function siegeCalc(opts){const sg=siegeState(),C=(DATA.siege||{}).calculus||{},SV=(DATA.siege||{}).sources||{};
  const mode=C[sg.mode]?sg.mode:(Object.keys(C)[0]||""),cfg=C[mode]||{settlement_sources:[],floor:1,attacker_sources:false};
  const p=D.players.find(q=>String(q.id)===String(sg.tp))||D.players[0],b=p.board;
  const st=(b.settlements||[]).find(x=>String(x.id)===String(sg.sid))||(b.settlements||[])[0];
  const rows=[];
  withBoard(b,()=>{const have=new Set(Object.keys(PC)),ce=computeEarned(have).earned;
    (cfg.settlement_sources||[]).forEach(src=>{const v=SV[src]||{};let val=0;
      if(src==="Settlement Size")val=st?(((DATA.settlements||{})[st.tier]||{})[v.field||"tier"]||0):0;
      else if(src==="Standing Army")val=sg.army?(v.value||0):0;
      else if(v.from==="text"){const c=S.placed.find(q=>q.name===src&&pActive(q)&&st&&q.sid===st.id);   // its own "Siege Timer +X", in its own Settlement only
        val=c?efxOf("h:"+src,"siege_def_plus").concat(ce[src]?efxOf("hm:"+src,"siege_def_plus"):[]).reduce((t,m)=>t+(+m[1]||0),0):0;}
      else val=infraOn(src)?(v.value||0):0;
      rows.push({src,val});});});
  const tm=mode==="Convert"?{rows:[],noWalls:[]}:siegeTextMods(p,opts&&("att" in opts)?opts.att:(pById(sg.by)||D.players.find(q=>q!==p)));
  tm.rows.forEach(r=>rows.push(r));
  if(tm.noWalls.length)rows.forEach(r=>{if(/Walls\b/.test(r.src)&&r.val){r.val=0;r.src+=" (ignored: "+tm.noWalls.join(", ")+")";}});
  const base=rows.reduce((a,r)=>a+r.val,0),att=cfg.attacker_sources?(+sg.att||0):0,def=+sg.def||0;
  return {p,st,mode,cfg,rows,base,att,def,total:Math.max(cfg.floor||1,base+def-att)};}
function siegeHTML(){const sg=siegeState(),c=siegeCalc(),C=(DATA.siege||{}).calculus||{};
  let h='<div class="tot" style="margin-top:12px"><h3 style="font-size:13px">Siege calculator</h3><div class="bcrow">'+
    '<select id="sgMode">'+Object.keys(C).map(m=>'<option'+(m===c.mode?' selected':'')+'>'+esc(m)+'</option>').join('')+'</select>'+
    '<select id="sgP">'+D.players.map(p=>'<option value="'+p.id+'"'+(p===c.p?' selected':'')+'>'+esc(p.name)+'</option>').join('')+'</select>'+
    '<select id="sgS">'+(c.p.board.settlements||[]).map(x=>'<option value="'+x.id+'"'+(x===c.st?' selected':'')+'>'+(x.capital?'★ ':'')+esc(x.name||x.tier)+'</option>').join('')+'</select>'+
    (c.mode!=="Convert"?'<span class="note">besieger</span><select id="sgBy">'+D.players.filter(p=>p!==c.p).map(p=>'<option value="'+p.id+'"'+(String(sg.by)===String(p.id)?' selected':'')+'>'+esc(p.name)+'</option>').join('')+'</select>'+
      (()=>{const bp=pById(sg.by)||D.players.find(p=>p!==c.p);return bp?'<select id="sgAid"><option value="">Army…</option>'+(bp.board.armies||[]).map(a=>'<option value="'+a.id+'"'+(String(sg.aid)===String(a.id)?' selected':'')+'>'+esc(armyName(a))+'</option>').join('')+'</select>':'';})():'')+
    ((c.cfg.settlement_sources||[]).includes("Standing Army")?'<label><input type="checkbox" id="sgArmy"'+(sg.army?' checked':'')+'> Standing Army</label>':'')+'</div>'+
    '<table class="dtable ttab" style="margin-top:6px;max-width:420px"><tbody>'+c.rows.map(r=>'<tr><td>'+esc(r.src)+'</td><td class="num">'+r.val+'</td></tr>').join('')+
    '<tr><td>defender modifiers</td><td class="num"><input id="sgDef" type="number" value="'+(+sg.def||0)+'" style="width:56px"></td></tr>'+
    (c.cfg.attacker_sources?'<tr><td>attacker Siege effects (−)</td><td class="num"><input id="sgAtt" type="number" value="'+(+sg.att||0)+'" style="width:56px"></td></tr>':'')+
    '<tr><td><b>'+esc(c.mode==="Convert"?"Convert Timer":"Siege Timer")+'</b> (min '+(c.cfg.floor||1)+')</td><td class="num"><b>'+c.total+'</b></td></tr></tbody></table>'+
    '<button id="sgStart" style="margin-top:6px">start timer</button></div>';
  return h;}
// ---- realm timers ----
function realmTimers(){D.rtimers=D.rtimers||[];return D.rtimers;}
function timerAddHTML(){const keys=Object.keys(TMR),p=D.players[D.active]||{};
  return '<h3 style="font-size:13px">Start a timer</h3><div class="bcrow" style="margin-top:6px;flex-wrap:wrap"><select id="rtType">'+keys.map(k=>'<option>'+esc(k)+'</option>').join('')+'</select>'+
    '<input id="rtLabel" placeholder="label (e.g. target)" style="width:150px"><input id="rtN" type="number" style="width:56px" value="'+(((TMR[keys[0]]||{}).default)||1)+'">'+
    '<button id="rtAdd">start</button></div>';}
function boardTimerRows(){const R_=[];
  D.players.forEach(p=>{const b=p.board,sn=id=>{const x=(b.settlements||[]).find(s=>s.id===id);return x?(x.name||x.tier):"";};
    (b.placed||[]).forEach(q=>{if(q.bt>0)R_.push([p,"Build Timer",q.name+" · "+sn(q.sid),q.bt]);if(q.dmg>0)R_.push([p,q.rep?"Repair Timer":"Damaged",q.name+" · "+sn(q.sid)+(q.rep?"":" (awaiting Repair)"),q.rep?q.dmg:"—"]);});
    Object.keys(b.itimer||{}).forEach(n=>R_.push([p,"Build Timer",n,b.itimer[n]]));Object.keys(b.idmg||{}).forEach(n=>R_.push([p,(b.irep||{})[n]?"Repair Timer":"Damaged",n+((b.irep||{})[n]?"":" (awaiting Repair)"),(b.irep||{})[n]?b.idmg[n]:"—"]));
    (b.settlements||[]).forEach(s=>{if(s.bt>0)R_.push([p,"Build Timer",(s.name||s.tier)+(s.up?" → "+s.up.to:" (settlement)"),s.bt]);});});
  return R_;}
function siegeResolveHTML(t,i){if(t.kind!=="siege"||t.n>0)return "";
  if(t.bandit)return '<div class="bcrow"><button class="rtBsb" data-i="'+i+'">Siege Battle vs Bandits ▸</button></div>';const from=pById(t.tp),s=from?(from.board.settlements||[]).find(x=>String(x.id)===String(t.sid)):null;
  if(!s)return '<div class="note">Settlement not found</div>';
  const W=sackWards(from,s);
  return '<div class="bcrow" style="flex-wrap:wrap"><button class="rtCap" data-i="'+i+'">Capture</button> <span class="note">or Sack — raze the top Holding of each Ward; choose the Ward that leaves play:</span> '+
    (W.length?W.map((w,k)=>'<label class="note"><input type="radio" name="rtSkW'+i+'" class="rtSkW" data-i="'+i+'" value="'+k+'"'+(k?'':' checked')+'> '+esc(w.map(q=>q.name).join(" → "))+'</label>').join(' '):'<span class="note">(no Wards in use)</span>')+
    ' <button class="rtSack" data-i="'+i+'">Sack</button></div>';}
function activeTimersHTML(){const T=realmTimers(),B_=boardTimerRows();
  return '<div class="tot"><h3 style="font-size:13px">Active timers</h3>'+
    (T.length?'<table class="dtable ttab"><tbody>'+T.map((t,i)=>'<tr'+(t.n<=0?' class="broll"':'')+'><td>'+esc(t.type)+'</td><td>'+esc(t.label||'')+siegeResolveHTML(t,i)+'</td><td class="num"><button class="rtd" data-i="'+i+'" data-d="-1">−</button> <b>'+t.n+'</b> <button class="rtd" data-i="'+i+'" data-d="1">+</button></td><td><button class="rtx" data-i="'+i+'">✕</button></td></tr>').join('')+'</tbody></table>':'<div class="note">No realm timers.</div>')+
    (T.length?'<div class="bcrow" style="margin-top:6px"><button id="rtTick">−1 all</button><span class="note">Sieges don\'t tick in Winter.</span></div>':'')+
    (B_.length?'<div class="lbl" style="margin-top:8px">Build & Repair (set on each Board)</div><table class="dtable ttab"><tbody>'+B_.map(r=>'<tr><td>'+pTok(r[0],12)+esc(r[0].name)+'</td><td>'+esc(r[1])+'</td><td>'+kwify(r[2])+'</td><td class="num"><b>'+r[3]+'</b></td></tr>').join('')+'</tbody></table>':'')+
    '</div>';}
function seasonsHTML(){const cs=curSeason();
  return '<div class="tot" style="margin-top:12px"><h3 style="font-size:13px">Season <button id="seaPrev">◂</button> <b>'+esc(cs)+'</b> — '+esc((SEAS[cs]||{}).name||'')+' <button id="seaNext">▸</button></h3>'+
    '<table class="dtable ttab" style="max-width:760px"><tbody>'+SEAS_ORDER.map(k=>'<tr'+(k===cs?' class="broll"':'')+'><td>'+esc(k)+'</td><td>'+esc(SEAS[k].name||'')+'</td><td>'+esc(SEAS[k].effect||'')+'</td></tr>').join('')+'</tbody></table></div>';}
function costsHTML(){const C=DATA.costs||{};if(!Object.keys(C).length)return '';
  return '<div class="tot" style="margin-top:12px"><h3 style="font-size:13px">Costs</h3><table class="dtable ttab" style="max-width:760px"><tbody>'+
    Object.keys(C).map(k=>'<tr><td>'+esc(k)+'</td><td>'+esc(C[k])+'</td></tr>').join('')+'</tbody></table></div>';}
function wireDashExtras(host){const $=id=>host.querySelector("#"+id),sg=siegeState();
  const on=(id,ev,fn)=>{const e=$(id);if(e)e[ev]=fn;};
  on("seaPrev","onclick",()=>{stepSeason(-1);save();render();});on("seaNext","onclick",()=>{stepSeason(1);save();render();});
  on("sgMode","onchange",e=>{sg.mode=e.target.value;save();render();});
  on("sgP","onchange",e=>{sg.tp=e.target.value;sg.sid=null;save();render();});
  on("sgS","onchange",e=>{sg.sid=e.target.value;save();render();});
  on("sgArmy","onchange",e=>{sg.army=e.target.checked;save();render();});
  on("sgDef","onchange",e=>{sg.def=Math.round(+e.target.value)||0;save();setTimeout(render,0);});
  on("sgAtt","onchange",e=>{sg.att=Math.round(+e.target.value)||0;save();setTimeout(render,0);});
  on("sgBy","onchange",e=>{sg.by=e.target.value;sg.aid=null;save();render();});on("sgAid","onchange",e=>{sg.aid=e.target.value;save();});
  on("sgStart","onclick",()=>{const c=siegeCalc(),conv=c.mode==="Convert",by=sg.by||((D.players.find(p=>p!==c.p)||{}).id);
    realmTimers().push(Object.assign({type:conv?"Convert Timer":"Siege Timer",label:(conv?"":(pById(by)||{name:"?"}).name+" → ")+c.p.name+" · "+(c.st?(c.st.name||c.st.tier):""),n:c.total},
      conv?{}:{kind:"siege",tp:c.p.id,sid:c.st?c.st.id:null,by,aid:sg.aid||null}));save();render();});
  on("rtType","onchange",e=>{const d=(TMR[e.target.value]||{}).default;$("rtN").value=d==null?1:d;});
  on("rtAdd","onclick",()=>{const p=D.players[D.active]||{};realmTimers().push({type:$("rtType").value,label:($("rtLabel").value||"")+(p.name?" — "+p.name:""),pid:p.id,n:Math.round(+$("rtN").value)||0});save();render();});
  on("rtTick","onclick",()=>{const w=curSeason()==="Winter";realmTimers().forEach(t=>stepRealmTimer(t,w));resolveRealm().forEach(x=>flash(x));save();render();});
  host.querySelectorAll(".rtd").forEach(b=>b.onclick=()=>{const t=realmTimers()[+b.dataset.i];t.n=Math.max(0,t.n+(+b.dataset.d));resolveRealm().forEach(x=>flash(x));save();render();});
  host.querySelectorAll(".rtCap").forEach(b=>b.onclick=()=>{const T=realmTimers(),t=T[+b.dataset.i];if(!t)return;
    T.splice(+b.dataset.i,1,{type:"Capture Timer",kind:"capture",tp:t.tp,sid:t.sid,by:t.by,aid:t.aid,label:t.label,n:+((TMR["Capture Timer"]||{}).default)||1});
    resolveRealm().forEach(x=>flash(x));save();render();});
  host.querySelectorAll(".rtSack").forEach(b=>b.onclick=()=>{const i=+b.dataset.i,c=host.querySelector('.rtSkW[data-i="'+i+'"]:checked'),k=c?+c.value:-1;
    if(!confirm("Sack: raze the top Holding of each Ward, remove the chosen Ward, drop a tier, extort and set a Sack Timer?"))return;sackApply(i,k);save();render();});
  host.querySelectorAll(".rtx").forEach(b=>b.onclick=()=>{realmTimers().splice(+b.dataset.i,1);save();render();});
  host.querySelectorAll(".rtBsb").forEach(b=>b.onclick=()=>{const t=realmTimers()[+b.dataset.i];if(!t)return;const M=mapState(),ck=Object.keys(M.camps).find(k=>M.camps[k].uid===t.bandit),q=pById(t.tp),s=q&&settById(q,t.sid);
    if(!ck||!s){flash("Bandit Army or Settlement gone");return;}const def=armiesInside(q,s)[0],gs=garrisonOf(q,s.id);
    const B=def?{pid:String(def.p.id),aid:String(def.a.id)}:gs?{pid:String(q.id),aid:"g:"+s.id}:null;if(!B){flash("no defender to Battle");return;}
    bqStart({kind:"siege",A:{kind:"bandit",camp:ck},B,seize:"",src:"Bandit Siege"});});}

function renderDash(){const host=document.getElementById("viewDash");if(!host)return;host.innerHTML="";
  if(mods().diplomacy){host.insertAdjacentHTML("beforeend",diploHTML());wireDiplo(host);}}

function domBand(v){return v>=SOV?"Sovereign":v>=EST?"Established":v>=RIS?"Rising":"Untested";}
// ============================================================================
// ---- optional modules (shared table settings) ----
function mods(){D.modules=D.modules||{};return D.modules;}

// ---- Diplomacy (Dashboards) ----
const TREATIES=DATA.treaties||{};
const TRUCE_LEN=(()=>{const d=((DATA.timers||{})["Truce Timer"]||{}).default;if(d!=null)return +d;const m=/Truce Timer\s*(\d+)/i.exec((TREATIES["Peace Treaty"]||{}).effect||"");return m?+m[1]:0;})();
function diplo(){D.diplo=D.diplo||{};const d=D.diplo;d.pairs=d.pairs||{};d.alliances=d.alliances||{};d.member=d.member||{};d.suzerain=d.suzerain||{};return d;}
function pk(a,b){return [String(a),String(b)].sort().join("|");}
// ---- Vassalage (RULES §Vassalization): a Vassal's Treaties mirror its Suzerain's → every pair resolves to the top Suzerains' pair ----
function isVassal(id){return !!diplo().suzerain[String(id)];}
function vassalsOf(id){const d=diplo();return D.players.filter(q=>String(d.suzerain[String(q.id)])===String(id));}
function effPair(a,b){a=String(a);b=String(b);const ra=topSuz(a),rb=topSuz(b),Z={war:false,trade:false,nap:false,truce:0};
  if(ra===rb)return Object.assign({household:true,mirror:false},Z);
  const x=diplo().pairs[pk(ra,rb)]||Z,mir=ra!==a||rb!==b;return Object.assign({},Z,x,{household:false,mirror:mir,ra,rb});}
function pairOf(a,b){if(String(a)===String(b))return null;const d=diplo(),k=pk(a,b);return d.pairs[k]=d.pairs[k]||{war:false,trade:false,nap:false,truce:0};}
function pname(id){const p=D.players.find(q=>String(q.id)===String(id));return p?p.name:"?";}
function allianceLabel(gid){const a=diplo().alliances[gid];return a?(a.type+" Alliance "+gid):"";}
function pboard(id){const p=D.players.find(q=>String(q.id)===String(id));return p&&p.board||{};}
// TRADE_RULES.requires_border: Trade Agreements need the two Provinces to border
function tradeBorderOK(a,b){if(!DATA.tradeBorder)return true;const p=pById(a);return !!p&&bordersOf(p).some(q=>String(q.id)===String(b));}
function hasRoad(id){const b=pboard(id);if((b.infra||{})["Dirt Roads"])return true;if(srcHas(b,"trade_no_roads"))return true;
  if(srcHas(b,"trade_border")){const p=pById(id);return !!p&&bordersOf(p).length>0;}return false;}
// alliance types locked by Era (TREATIES[<type> Alliance].era)
function eraRank(e){const ks=Object.keys(ERAS).sort((a,b)=>ERAS[a].renown-ERAS[b].renown);return ks.indexOf(e);}
function allianceEra(type){return ((TREATIES[type+" Alliance"]||{}).era)||"Any";}
function allianceOK(type){const e=allianceEra(type);return e==="Any"||eraRank(currentEra())>=eraRank(e);}
function pairFlags(a,b,x){const d=diplo(),f=[];const sameAl=sameAlliance(a,b);
  if(x.war&&x.nap)f.push("War with Non-Aggression Pact in force");
  if(x.war&&x.truce>0)f.push("War during truce ("+x.truce+")");
  if(x.war&&sameAl)f.push("War within the same alliance");
  if(sameAl)[a,b].forEach(id=>{const q=pById(id),n=q?fxOf(q,"noAlliance")[0]:null;if(n)f.push(q.name+" can't be in an Alliance ("+n.src+")");});
  if(x.trade&&x.war)f.push("Trade Agreement while at war");
  if(x.trade&&!tradeBorderOK(a,b))f.push("Trade Agreement between players who don't border");
  if(x.trade&&(!hasRoad(a)||!hasRoad(b)))f.push("Trade Agreement without Dirt Roads or Can Trade ("+[a,b].filter(q=>!hasRoad(q)).map(pname).join(", ")+")");
  return f;}
function dStatus(x){return x.war?"W":x.truce>0?"TR":"P";}
// letter codes (no emoji)
const DCODE={W:"War",P:"Peace",TR:"Truce (turns left)",TA:"Trade Agreement",NAP:"Non-Aggression Pact",AL:"same Alliance",VS:"Vassal / Suzerain"};
let DIPLO_SEL=null;
function diploHTML(){
  const d=diplo(),P=D.players;
  let h='<div class="tot" style="margin-top:12px"><h3 style="font-size:13px">Diplomacy</h3>'+
    '<div class="note" style="margin-bottom:6px">'+Object.keys(DCODE).map(k=>'<b>'+k+'</b> '+DCODE[k]).join(' · ')+'</div>'+
    '<div style="overflow-x:auto"><table class="dtable"><thead><tr><th></th>'+P.map(p=>'<th>'+pTok(p,15)+' '+esc(p.name)+'</th>').join('')+'</tr></thead><tbody>';
  P.forEach(r=>{
    h+='<tr><th style="text-align:left">'+pTok(r,15)+' '+esc(r.name)+'</th>';
    P.forEach(c=>{
      if(r.id===c.id){const g=d.member[r.id],sz=d.suzerain[r.id];
        h+='<td class="note" style="background:var(--chip);text-align:center">self'+(g?'<br>AL '+esc(allianceLabel(g)):'')+(sz?'<br>VS of '+esc(pname(sz)):'')+'</td>';return;}
      const x=effPair(r.id,c.id),b=[];
      const st=dStatus(x);
      b.push(st==="W"?'<b style="color:var(--upkeep)">W</b>':st==="TR"?'<b style="color:var(--order)">TR'+x.truce+'</b>':'<span style="color:var(--income)">P</span>');
      if(x.sacredWar)b.push('<span title="Sacred War">SW</span>');
      if(x.trade)b.push('TA');if(x.nap)b.push('NAP');
      if(sameAlliance(r.id,c.id))b.push('AL');if(x.mirror&&!x.household)b.push('<span class="note" title="mirrors '+esc(pname(x.ra)+' – '+pname(x.rb))+'">m</span>');
      if(String(d.suzerain[r.id])===String(c.id)||String(d.suzerain[c.id])===String(r.id))b.push('VS');
      if(pairFlags(r.id,c.id,x).length)b.push('<b style="color:var(--upkeep)">!</b>');
      const sel=DIPLO_SEL===pk(r.id,c.id);
      h+='<td class="dpcell" data-a="'+r.id+'" data-b="'+c.id+'" style="cursor:pointer;'+(sel?'outline:2px solid var(--ink);':'')+(x.war?'background:rgba(198,40,40,.12)':'')+'">'+b.join(' ')+'</td>';});
    h+='</tr>';});
  h+='</tbody></table></div>';
  if(DIPLO_SEL&&(()=>{const [a,b]=DIPLO_SEL.split("|");return isVassal(a)||isVassal(b);})()){const [a,b]=DIPLO_SEL.split("|"),x=effPair(a,b);
    h+='<div class="tot" style="margin-top:8px;background:var(--panel2)"><b>'+esc(pname(a))+' – '+esc(pname(b))+'</b> '+
      '<span class="note">status: <b>'+DCODE[dStatus(x)]+(x.truce>0&&!x.war?' '+x.truce:'')+'</b>'+(x.trade?' · TA':'')+(x.nap?' · NAP':'')+(sameAlliance(a,b)?' · AL':'')+'</span>'+
      '<div class="note" style="margin-top:4px">Vassal: Treaties mirror the Suzerain\u2019s; can\u2019t perform or be targeted by Diplomacy actions.'+
      (x.household?' Same Suzerain household \u2014 allied.':' Mirrors <a href="#" class="dpjump" data-k="'+esc(pk(x.ra,x.rb))+'">'+esc(pname(x.ra)+' – '+pname(x.rb))+' ▸</a>')+'</div></div>';}
  else if(DIPLO_SEL){const [a,b]=DIPLO_SEL.split("|"),x=pairOf(a,b);
    const sameAl=sameAlliance(a,b);
    const warNo=x.war?"already at war":x.truce>0?"truce active ("+x.truce+")":x.nap?"Non-Aggression Pact in force":sameAl?"same alliance":"";
    const warFlag="";
    const trNo=x.trade?"":!tradeBorderOK(a,b)?"players don't border":(!hasRoad(a)||!hasRoad(b))?"needs active Dirt Roads or Can Trade ("+[a,b].filter(q=>!hasRoad(q)).map(pname).join(", ")+" missing)":"";
    const btn=(act,label,dis)=>'<button class="dpa'+(dis?' flagged':'')+'" data-act="'+act+'"'+(dis?' title="'+esc(dis)+'"':'')+'>'+esc(label)+'</button> ';
    const pf=pairFlags(a,b,x);
    h+='<div class="tot" style="margin-top:8px;background:var(--panel2)"><b>'+esc(pname(a))+' – '+esc(pname(b))+'</b> '+
      '<span class="note">status: <b>'+DCODE[dStatus(x)]+(x.truce>0&&!x.war?' '+x.truce:'')+'</b>'+(x.trade?' · TA':'')+(x.nap?' · NAP':'')+'</span>'+
      '<div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;align-items:center">'+
      btn("war","Declare War",warNo)+
      btn("peace","Peace Treaty"+(TRUCE_LEN?" (truce "+TRUCE_LEN+")":""),x.war?"":"not at war")+
      (x.trade?btn("endtrade","End Trade Agreement"):btn("trade","Trade Agreement",x.war?"at war":trNo))+
      (x.nap?btn("endnap","End NAP"+(TRUCE_LEN?" (truce "+TRUCE_LEN+")":"")):btn("nap","Non-Aggression Pact",x.war?"at war":""))+
      '<span style="margin-left:6px">Truce <button class="dpt" data-d="-1">−</button> '+x.truce+' <button class="dpt" data-d="1">+</button></span></div>'+
      (pf.length?'<div class="flagbox" style="margin-top:6px">⚑ '+pf.map(esc).join(' · ')+'</div>':'')+
      '<div class="note" style="margin-top:4px">'+Object.keys(TREATIES).map(t=>'<b>'+esc(t)+'</b> ('+esc(TREATIES[t].era||'')+'): '+esc(TREATIES[t].effect||'')).join('<br>')+'</div></div>';}
  // alliances + vassals
  h+='<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:8px">'+P.map(p=>{
      const g=d.member[p.id]||"",opts=Object.keys(d.alliances).map(k=>'<option value="'+k+'"'+(k===g?' selected':'')+(!allianceOK(d.alliances[k].type)?' style="color:var(--upkeep)"':'')+'>'+esc(allianceLabel(k))+'</option>').join('');
      const sz=d.suzerain[p.id]||"",ig=d.member[topSuz(p.id)];
      return '<div>'+pTok(p,15)+' '+esc(p.name)+'<br>'+
        (sz?'<span class="note">inherits '+(ig?esc(allianceLabel(ig)):'no alliance')+'</span> ':'<select class="dal" data-p="'+p.id+'"><option value="">no alliance</option>'+opts+''+["Military","Defensive"].map(t=>'<option value="+'+t+'"'+(allianceOK(t)?'':' style="color:var(--upkeep)"')+'>+ new '+t+(allianceOK(t)?'':' ('+allianceEra(t)+')')+'</option>').join('')+'</select> ')+
        '<select class="dvs" data-p="'+p.id+'"><option value="">not a vassal</option>'+P.filter(q=>q.id!==p.id).map(q=>'<option value="'+q.id+'"'+(String(sz)===String(q.id)?' selected':'')+'>vassal of '+esc(q.name)+'</option>').join('')+'</select></div>';}).join('')+'</div>'+
    (()=>{const bad=Object.keys(d.alliances).filter(k=>!allianceOK(d.alliances[k].type));
      return bad.length?'<div class="flagbox" style="margin-top:8px">⚑ '+bad.map(k=>esc(allianceLabel(k))+' requires '+esc(allianceEra(d.alliances[k].type))+' (now '+esc(currentEra())+')').join(' · ')+'</div>':'';})()+
    '<div style="margin-top:8px"><button id="truceTick">−1 all truce timers</button> '+
    '<span class="note">'+(DATA.allianceRules||[]).map(esc).join(' · ')+'</span></div></div>';
  return h;
}
function wireDiplo(host){
  const d=diplo();
  host.querySelectorAll(".dpcell").forEach(td=>td.onclick=()=>{if(td.dataset.a===td.dataset.b)return;const k=pk(td.dataset.a,td.dataset.b);DIPLO_SEL=DIPLO_SEL===k?null:k;render();});
  const cur=()=>{const [a,b]=DIPLO_SEL.split("|");return pairOf(a,b);};
  host.querySelectorAll(".dpt").forEach(b=>b.onclick=()=>{const x=cur();x.truce=Math.max(0,x.truce+(+b.dataset.d));save();render();});
  host.querySelectorAll(".dpa").forEach(b=>b.onclick=()=>{const x=cur();
    const act=b.dataset.act;
    if(act==="war"){x.war=true;x.sacredWar=false;x.trade=false;}   // declaring war ends trade
    if(act==="peace"){x.war=false;x.sacredWar=false;x.truce=TRUCE_LEN;}
    if(act==="trade")x.trade=true;
    if(act==="endtrade")x.trade=false;
    if(act==="nap")x.nap=true;
    if(act==="endnap"){x.nap=false;x.truce=TRUCE_LEN;}
    save();render();});
  host.querySelectorAll(".dal").forEach(s=>s.onchange=()=>{let v=s.value;
    if(v.startsWith("+")){let n=1;while(d.alliances[String(n)])n++;v=String(n);d.alliances[v]={type:s.value.slice(1)};}
    if(v)d.member[s.dataset.p]=v;else delete d.member[s.dataset.p];
    Object.keys(d.alliances).forEach(k=>{if(!Object.values(d.member).includes(k))delete d.alliances[k];});save();render();});
  host.querySelectorAll(".dvs").forEach(s=>s.onchange=()=>{const me=s.dataset.p,v=s.value;
    if(v&&(String(v)===String(me)||String(d.suzerain[v])===String(me))){s.value=d.suzerain[me]||"";return;}   // no self / mutual vassalage
    if(v){d.suzerain[me]=v;
      Object.keys(d.pairs).forEach(k=>{if(k.split("|").includes(String(me)))delete d.pairs[k];});   // Vassal ends all existing Treaties
      delete d.member[me];Object.keys(d.alliances).forEach(k=>{if(!Object.values(d.member).includes(k))delete d.alliances[k];});
      Object.keys(d.suzerain).forEach(q=>{if(String(d.suzerain[q])===String(me))d.suzerain[q]=v;});}   // Suzerain vassalized → its Vassals follow to the new Suzerain
    else delete d.suzerain[me];save();render();});
  host.querySelectorAll(".dpjump").forEach(a=>a.onclick=e=>{e.preventDefault();DIPLO_SEL=a.dataset.k;render();});
  const tt=host.querySelector("#truceTick");if(tt)tt.onclick=()=>{Object.values(d.pairs).forEach(x=>{if(x.truce>0)x.truce--;});save();render();};
}

