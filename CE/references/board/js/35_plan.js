// ---- Plans (this device only): goal Holdings / Infrastructure / Wonders per player, in priority order. Each goal's path is worked
// out from the same checks the Build / Improve actions use — the Holding line back to a Raw Material (the cheapest branch, preferring
// what you already have), every Infrastructure chain those Holdings need, the Standings each step unlocks at — and orders the
// catalog's Plan view and the Build / Improve choices. Advice only: nothing is blocked.
let PLANS={};try{PLANS=JSON.parse(localStorage.getItem(gkey("renown_plan"))||"{}")||{};}catch(e){}
let PLAN_PICK=false;try{PLAN_PICK=localStorage.getItem("renown_planpick")==="1";}catch(e){}
function planSave(){try{localStorage.setItem(gkey("renown_plan"),JSON.stringify(PLANS));}catch(e){}}
function planKey(b){const p=playerOfBoard(b||S);return p?String(p.id):"_";}
function planOf(b){return (PLANS[planKey(b)]||[]).filter(n=>R[n]||INFRA[n]||WON[n]);}
function planSet(L,b){PLANS[planKey(b)]=L;planSave();}
function planToggle(n){const L=planOf(S),i=L.indexOf(n);if(i<0)L.push(n);else L.splice(i,1);planSet(L);flash((i<0?"Plan + ":"Plan − ")+(window.dispName?dispName(n):n));}
function planMove(n,d){const L=planOf(S),i=L.indexOf(n),j=i+d;if(i<0||j<0||j>=L.length)return;[L[i],L[j]]=[L[j],L[i]];planSet(L);}
// where a Raw Material comes from: its resource nodes, else the terrains that yield it
function rawWhere(n){if(nodesMode())return Object.keys(RES_NODE).filter(k=>RES_NODE[k]===n);
  return Object.keys(TREF.terrain||{}).filter(t=>(((TREF.terrain[t]||{})["Raw Materials"])||[]).includes(n));}
// one step's state: done · building · now (can start) · blocked (why) · taken (Realm Scope: another player has it)
function planHStep(n,ctx){const own=S.placed.filter(p=>p.name===n&&p.sid!=null);
  if(own.some(chainOK))return {st:"done"};
  if(own.some(p=>p.bt>0))return {st:"building",why:"Build Timer "+Math.min(...own.filter(p=>p.bt>0).map(p=>p.bt))};
  if(own.length)return {st:"blocked",why:"Damaged — Repair it"};
  const blk=scopeBlock(n,null);if(blk&&scopeOf(n)==="Realm")return {st:"taken",why:blk};
  const r=R[n]||{},wh=rawRes(n)?rawWhere(n):[],inR=rawRes(n)&&ctx.res?ctx.res.has(n):null;
  if(pLegal(n,null,ctx))return {st:"now",why:inR?wh.join(" / ")+" in Reach":""};
  const why=[],us=unlockStatus(n);if(!us.ok)why.push(us.toks.filter(x=>x.ok===false).map(x=>x.t).join(" + "));
  if(inR===false)why.push((wh.length?wh.join(" or "):n)+" in Reach"+(ctx.raws&&!ctx.raws.has(n)?" (none on the map)":""));
  if((r.mreq||[]).length){const st=reqStatus(r,ctx.have,ctx.craft,ctx.tc);if(!st.earned)why.push(st.missing.map(x=>String(x).replace(/\s*\[[^\]]*\]/g,"")).join(" + "));}
  if(!r.root&&!chainLine(n,ctx.own))why.push("its line first");
  return {st:"blocked",why:why.length?"needs "+why.join(" · "):""};}
function planIStep(n){itm();const have=(INFRA[n]?S.infra:S.wonders)||{};
  if(have[n]&&!(S.itimer[n]>0))return S.idmg[n]>0?{st:"blocked",why:"Damaged — Repair it"}:{st:"done"};
  if(have[n])return {st:"building",why:"Build Timer "+S.itimer[n]};
  const blk=scopeBlock(n,null);if(blk)return {st:"taken",why:blk};
  if(iAvail(INFRA[n]?"infra":"wonder",n)){const wb=WON[n]?wonderBuilding(S,n):null;return {st:"now",why:wb?wb+" still building":""};}
  const rec=INFRA[n]||WON[n],rs=infraReqStatus(rec),named=infraReqToks(rec).filter(t=>INFRA[t]||WON[t]).map(t=>((INFRA[t]||WON[t]).tier||"").toLowerCase());
  const miss=rs.missing.filter(m=>{const t=String(m).match(/^any one (\w+)/i);return !t||!named.includes(t[1].toLowerCase());});   // the named piece is of that tier
  return {st:"blocked",why:miss.length?"needs "+miss.join(", "):""};}
const PLAN_COST={done:0,building:.5,now:1,blocked:3,taken:1e5};
// the Holding line to n: the cheapest chain parent (what you hold costs nothing; a Raw Material not in Reach costs extra), back to a Root
function planHPath(n,ctx,memo,seen){if(memo[n])return memo[n];if(seen.has(n))return {cost:1e6,line:[n],alts:{}};seen=new Set(seen).add(n);
  const st=planHStep(n,ctx),self=PLAN_COST[st.st]+(st.st==="blocked"&&/in Reach/.test(st.why)?50:0),r=R[n]||{},el=effLabel(n),eff=effList(n);
  let out;
  if(st.st==="done"||r.root||(!eff.length&&!el.some(e=>/^natural$/i.test(String(e)))))out={cost:self,line:[n],alts:{}};
  else{const facOK=el.some(e=>/^natural$/i.test(String(e)))&&S.placed.some(p=>p.fac);
    const C=eff.map(p=>({p,x:planHPath(p,ctx,memo,seen)})).filter(c=>c.x.cost<1e4).sort((a,b)=>a.x.cost-b.x.cost);
    if(facOK||!C.length)out={cost:self+(facOK?0:1e4),line:[n],alts:{}};
    else{const b=C[0];out={cost:b.x.cost+self,line:b.x.line.concat([n]),alts:Object.assign({},b.x.alts,C.length>1?{[n]:C.slice(1,4).map(c=>c.p)}:{})};}}
  return memo[n]=out;}
function planIPath(n,acc){if(acc.includes(n))return;infraReqToks(INFRA[n]||WON[n]).forEach(t=>{if(INFRA[t]||WON[t])planIPath(t,acc);});acc.push(n);}
function planCtx(){const c=legalCtx();c.raws=mapRaws();return c;}
// a goal's whole path: {t, h:[steps], i:[steps], done, total, taken}
function planGoal(T,ctx){const h=[],i=[],acc=[];
  if(R[T]){const P=planHPath(T,ctx,{},new Set());
    P.line.forEach(n=>{h.push(Object.assign({n,k:"h",alts:P.alts[n]||null},planHStep(n,ctx)));
      const r=R[n];if(r&&r.mreq)masteryInfraToks(r).forEach(t=>planIPath(t,acc));});}
  else planIPath(T,acc);
  acc.forEach(n=>i.push(Object.assign({n,k:"i"},planIStep(n))));
  const all=h.concat(i),own=(R[T]?h:i).find(s=>s.n===T)||{};
  return {t:T,h,i,done:all.filter(s=>s.st==="done").length,total:all.length,taken:own.st==="taken"?own.why:"",
    left:all.reduce((a,s)=>a+(s.st==="done"?0:s.st==="blocked"?3:1),0)};}
function planGoals(b){b=b||S;const L=planOf(b);if(!L.length)return [];return withBoard(b,()=>{const ctx=planCtx();return L.map(T=>planGoal(T,ctx));});}
// steps still to do, highest-priority goal first: name → {rank, goal, k, st}
function planSteps(b){const m=new Map();planGoals(b).forEach((g,ri)=>{if(!g.taken)g.h.concat(g.i).forEach(s=>{if(s.st!=="done"&&s.st!=="taken"&&!m.has(s.n))m.set(s.n,{rank:ri,goal:g.t,k:s.k,st:s.st});});});return m;}   // a taken goal pushes nothing
function planSort(by){const G=planGoals(S),kind=g=>WON[g.t]?0:(R[g.t]||{}).monument?1:R[g.t]?2:3;
  const f=by==="wonders"?(a,b)=>kind(a)-kind(b):by==="holdings"?(a,b)=>(R[a.t]?0:1)-(R[b.t]?0:1):(a,b)=>(!!a.taken-!!b.taken)||a.left-b.left;
  planSet(G.slice().sort(f).map(g=>g.t));}
function planAdd(n,k){if(k==="i"){addInfraByName("infra",n);return;}const t=tab;tab="pursuit";try{addItem(n);}finally{tab=t;}}
// catalog Plan view: goals in priority order, each with its Holding line and Infrastructure route
const PLAN_ICON={done:"✓",building:"⏳",now:"▸",blocked:"🔒",taken:"✗"};
function planPanel(host){const G=planGoals(S),dn=n=>window.dispName?dispName(n):n;
  const bar=document.createElement("div");bar.className="catctl";
  [["ease","easiest first"],["wonders","Wonders first"],["holdings","Holdings first"]].forEach(([k,l])=>{const c=document.createElement("span");c.className="chip";c.textContent=l;c.onclick=()=>{planSort(k);renderList();};bar.appendChild(c);});
  {const c=document.createElement("span");c.className="chip";c.dataset.goto="reference#refTree";c.textContent="pick goals ▸";bar.appendChild(c);}
  host.appendChild(bar);
  if(!G.length){const e=document.createElement("div");e.className="empty";e.textContent="No goals yet.";host.appendChild(e);return;}
  G.forEach((g,ri)=>{const box=document.createElement("div");box.className="plang"+(g.taken?" taken":"");
    const hd=document.createElement("div");hd.className="planh";
    hd.innerHTML='<b>'+(ri+1)+'. '+esc(dn(g.t))+'</b>'+(WON[g.t]?' <span class="badge mon">Wonder</span>':(R[g.t]||{}).monument?' <span class="badge mon">Monument</span>':'')+
      ' <span class="note">'+g.done+'/'+g.total+'</span>'+(g.taken?' <span class="badge noearn" title="'+esc(g.taken)+'">taken</span>':'');
    [["▲",-1],["▼",1]].forEach(([t,d])=>{const b=document.createElement("button");b.className="shb";b.textContent=t;b.disabled=(d<0?ri===0:ri===G.length-1);b.onclick=()=>{planMove(g.t,d);renderList();};hd.appendChild(b);});
    {const b=document.createElement("button");b.className="rm";b.textContent="✕";b.onclick=()=>{planToggle(g.t);render();renderList();};hd.appendChild(b);}
    box.appendChild(hd);
    if(g.taken){const m=document.createElement("div");m.className="miss";m.textContent=g.taken;box.appendChild(m);}
    [["Holdings",g.h],["Infrastructure",g.i]].forEach(([lab,L])=>{if(!L.length)return;const sec=document.createElement("div");sec.className="plans";
      sec.innerHTML='<div class="lbl">'+lab+'</div>';
      L.forEach(s=>{const row=document.createElement("div");row.className="planr st-"+s.st;
        row.innerHTML='<span class="pi">'+PLAN_ICON[s.st]+'</span><span class="pn">'+esc(dn(s.n))+'</span>'+(s.why?'<span class="note">'+esc(s.why)+'</span>':'')+
          (s.alts&&s.st!=="done"?'<span class="note">or after '+s.alts.map(x=>esc(dn(x))).join(" / ")+'</span>':'');
        if(s.st==="now"){const b=document.createElement("button");b.className="addbtn";b.textContent="+";b.title="add "+s.n;b.onclick=e=>{e.stopPropagation();planAdd(s.n,s.k);};row.appendChild(b);}
        sec.appendChild(row);});
      box.appendChild(sec);});
    host.appendChild(box);});}
// Reference trees: with Plan on, a click on a box adds / removes it as a goal; goals and their steps are outlined
document.addEventListener("click",e=>{
  const pp=e.target.closest("#planPick,#planPick2");if(pp){PLAN_PICK=pp.checked;try{localStorage.setItem("renown_planpick",PLAN_PICK?"1":"0");}catch(_){}render();return;}
  if(!PLAN_PICK)return;const tn=e.target.closest("#viewReference .tn[data-pn]");if(!tn)return;
  e.preventDefault();planToggle(tn.dataset.pn);render();renderList();});
function planPickHTML(id){return '<label class="note"><input type="checkbox" id="'+id+'"'+(PLAN_PICK?' checked':'')+'> Plan: click a box to add or remove a goal'+(planOf(S).length?' ('+planOf(S).length+' · see Catalog ▸ Plan)':'')+'</label>';}
function planMarks(){const L=planOf(S);return L.length?{t:new Set(L),s:planSteps(S)}:null;}
function planCls(PM,n){return !PM?"":PM.t.has(n)?" plan-t":PM.s.has(n)?" plan-s":"";}
