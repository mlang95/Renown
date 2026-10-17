// ---- pixel scene: every settlement of the active player, drawn from sprites.py (every theme) ----
// Each settlement is a skyline (sky:core + tiled sky:fill) behind its holdings, faded toward the sky. The player's
// infrastructure is placed per sprites.SKYLINE (slot / edge / band / ground / gap / link / front); INFRA_SUPERSEDES
// hides the replaced piece; PLATE_NO_INFRA tiers get no slot/edge/band/front pieces (the shared road, bridge and
// aqueduct still pass them). The aqueduct is the farthest layer: only the sky is behind it. Each ward shows only its frontmost holding, with the
// raw material at the root of its chain as a terrain strip at its feet. Wonders stand on the capital's skyline.
// Ground = the loaded map's Grassland colour (hexstyle climate / map swatch), snow in Winter.
const SPR=DATA.sprites||null;
const SPR_RAW=new Set((SPR&&SPR.raw)||[]);
const SCN_STYLE=Object.assign({fade:0.2,sil:0,halo:0},(SPR&&SPR.style)||{});   // skyline fade, silhouette strength, holding halo
const SCN={sky:{Winter:["#5a6a88","#7a88a4","#9aa6bc","#b8c2d2"],Spring:["#4a8ad8","#6aa4e4","#8abcee","#b0d4f4"],
               Summer:["#1e6ad0","#3a86e0","#5aa2ea","#86c0f2"],Fall:["#3a3060","#7a4a6a","#c8705a","#e8a060"]},
           ground:{Winter:["#c8d4e2","#e8eef5"]},leaf:{Spring:"#7cc44e",Summer:"#2f7a26",Fall:"#d8742a"}};
function sceneInfra(){   // built infrastructure names, minus anything an upgrade replaces
  const on=n=>!!(S.infra||{})[n],sup=SPR.supersedes||{},hidden=new Set(Object.keys(sup).filter(on).map(k=>sup[k]));
  const out={};Object.keys(SPR.skyline||{}).forEach(n=>{if(on(n)&&!hidden.has(n))out[n]={kind:SPR.skyline[n][0],pos:SPR.skyline[n][1],
    bt:((S.itimer||{})[n]>0)||((S.idmg||{})[n]>0)};});
  return out;
}
function wardChains(sid){   // [{front, chain:[front..root], root}] using the board's own ward-sharing rule
  const occ=occupants(sid),ex=exemptionsOf(occ),byName={};occ.forEach(o=>{byName[o.name]=o;});
  const ridden=new Set(occ.filter(o=>ex.has(o.id)).map(o=>ex.hostOf[o.id]));
  return occ.filter(o=>!ridden.has(o.name)).map(f=>{const chain=[f];let cur=f,g=32;
    while(ex.has(cur.id)&&g--){const h=byName[ex.hostOf[cur.id]];if(!h)break;chain.push(h);cur=h;}
    return {front:f,chain,root:cur};});
}
function sceneLots(){
  const ord=S.settlements.filter(s=>s.capital).concat(S.settlements.filter(s=>!s.capital)),noInf=new Set(SPR.noInfra||[]);
  return ord.map(s=>{const items=[];
    wardChains(s.id).forEach(w=>{const k=SPR.key[w.front.name];if(!k)return;
      const ft=SPR_RAW.has(w.root.name)&&SPR.S["feet:"+w.root.name]?"feet:"+w.root.name:null;
      items.push({key:k,name:w.chain.map(x=>x.name).join(" ← "),bt:w.front.bt>0,ft});});
    for(let i=0,f=Math.max(0,wardUse(s.id).free);i<f;i++)items.push({key:"scenery:plot",name:"Open ward"});
    const wonders=s.capital?Object.keys(S.wonders||{}).filter(n=>S.wonders[n]&&SPR.key[n]).map(n=>({key:SPR.key[n],name:n,bt:(S.itimer||{})[n]>0})):[];
    return {s,items,wonders,bare:noInf.has(s.tier)};});
}
let ES_TAB="all";try{ES_TAB=localStorage.getItem("renown_es")||"all";}catch(e){}
// Empire filter bar: All / Holdings / Infrastructure / Armies filters the board sections AND the catalog (Holdings → the Holdings
// list, Infrastructure → the Infrastructure list, Armies → no catalog); "hide combat" hides combat / other effect chips
function renderEsBar(){const bar=document.getElementById("esBar"),col=document.getElementById("boardcol"),ap=document.getElementById("appBoard");if(!bar||!col)return;col.dataset.es=ES_TAB;if(ap)ap.dataset.es=ES_TAB;
  const n={h:S.placed.length,i:Object.keys(S.infra||{}).length+Object.keys(S.wonders||{}).length,a:(S.armies||[]).length},hc=document.getElementById("hideCombat");
  bar.innerHTML=[["all","All"],["h","Holdings "+n.h],["i","Infrastructure "+n.i],["a","Armies "+n.a]].map(([k,l])=>'<button data-nav="1" data-es="'+k+'"'+(ES_TAB===k?' class="on"':'')+'>'+l+'</button>').join("")+
    '<button data-nav="1" data-hc="1" class="chipb'+(hc&&hc.checked?' on':'')+'" title="hide combat / other effect chips on cards">hide combat</button>';
  bar.querySelectorAll("[data-es]").forEach(b=>b.onclick=()=>{ES_TAB=b.dataset.es;try{localStorage.setItem("renown_es",ES_TAB);}catch(e){}
    const want=ES_TAB==="h"?"pursuit":ES_TAB==="i"?"infra":null,t=want&&document.querySelector('#tabs .tab[data-k="'+want+'"]');if(t&&tab!==want)t.click();renderEsBar();});
  const hb=bar.querySelector("[data-hc]");if(hb&&hc)hb.onclick=()=>{hc.checked=!hc.checked;render();};}
// Armies in the scene: on the grass right of the Settlement they're inside, or of the Settlement nearest them on the map
function sceneArmies(SL){const p=playerOfBoard(S),out=SL.map(()=>[]);if(!p)return out;
  (S.armies||[]).forEach(a=>{let i=-1;const x=armyInside(p,a);
    if(x&&sameP(x.q,p))i=SL.findIndex(L=>L.s.id===x.s.id);
    else{const k=armyHex(p,a);if(k){let bd=1e9;SL.forEach((L,j)=>{const sk=settHex(p,L.s);if(!sk)return;const d=hexDist(hk(k),hk(sk));if(d<bd){bd=d;i=j;}});}}
    if(i>=0)out[i].push(a);});
  return out;}
const WON_GAP=12;   // px between the core and the first Wonder on each side (clears the left / right slot pieces)
function renderScene(){
  const box=document.getElementById("sceneBox");if(!box)return;
  const on=!!(SPR&&S.settlements.length);box.hidden=!on;if(!on){box.innerHTML="";return;}
  const sea=SCN.sky[curSeason()]?curSeason():"Summer",G=38,H=48,pal=Object.assign({},SPR.P),sky=SCN.sky[sea];
  pal.l=sea==="Winter"?null:SCN.leaf[sea];
  const INF=sceneInfra(),has=n=>!!INF[n],SW=k=>(SPR.S[k]||[""])[0].length;
  // ---- layout: lot width from its holdings and its skyline core
  const lots=[],placed=[],gapW=has("Bridges")?18:12;let x=12;
  const SL=sceneLots(),AR=sceneArmies(SL),GW=SL.map((L,i)=>Math.max(gapW,(AR[i]||[]).length*18+6));
  SL.forEach((L,i)=>{if(i)x+=GW[i-1];
    const core="sky:core:"+L.s.tier,cw=SW(core)||16,hw=L.items.reduce((a,it)=>a+SW(it.key)+2,0)-2;
    // Wonders stand outward of the core and its left / right slot pieces, alternating left, right, left …, 26 px apart
    const wn=L.wonders.length,wside=Math.ceil(wn/2);
    const Lw=Math.max(hw+6,cw+(L.bare?12:28)+(wn?2*(WON_GAP+wside*26):0),40),x0=x;let hx=x0+Math.floor((Lw-hw)/2);
    L.items.forEach(it=>{const rows=SPR.S[it.key];if(!rows)return;placed.push({rows,x:hx,w:rows[0].length,it});hx+=rows[0].length+2;});
    lots.push({x0,x1:x0+Lw-1,Lw,L});x+=Lw;});
  const W=Math.max(x+(SL.length?Math.max(12,GW[SL.length-1]):12),120),cv=document.createElement("canvas");cv.width=W;cv.height=H;
  const c=cv.getContext("2d");let seed=W*31+sea.length*977+placed.length;const R=()=>((seed=(seed*16807)%2147483647)/2147483647);
  const px=(a,b,col)=>{c.fillStyle=col;c.fillRect(a,b,1,1);};
  const rgb=h=>h[0]==="#"?[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)):h.match(/\d+/g).map(Number);
  const mix=(a,b,t)=>{const A=rgb(a),B=rgb(b);return "rgb("+A.map((v,i)=>Math.round(v+(B[i]-v)*t)).join(",")+")";};
  const skyAt=y=>sky[Math.max(0,Math.min(3,Math.floor(y/(G/4))))];
  for(let y=0;y<G;y++){const i=Math.min(3,Math.floor(y/(G/4))),b0=Math.floor(i*G/4);
    for(let q=0;q<W;q++)px(q,y,(i>0&&y===b0&&(q+y)%2)?sky[i-1]:sky[i]);}
  if(sea==="Summer"){c.fillStyle="#fff4b0";c.fillRect(W-24,5,6,6);c.fillRect(W-25,6,8,4);c.fillRect(W-23,4,4,8);}
  if(sea==="Fall"){c.fillStyle="#ffe8b0";c.fillRect(W-20,6,3,3);}
  if(sea==="Spring"){c.fillStyle="#ffffff";for(let q=18;q<W;q+=70){c.fillRect(q,6,10,2);c.fillRect(q+4,5,5,1);}}
  const occ=[];
  const SHADE="#141a2a",DARK=new Set(["k","d","u"]);
  // everything is drawn opaque, back to front, so nearer pieces hide whatever is behind them; a piece under
  // construction or damaged (alpha<1) is drawn paler (more sky in it), never see-through
  const draw=(rows,ox,alpha,tint,track,oyOverride)=>{if(!rows)return;const oy=oyOverride!=null?oyOverride:G-(rows.length-1);
    if(alpha<1)tint=Math.min(.8,(tint||0)+.45);
    rows.forEach((row,y)=>{for(let q=0;q<row.length;q++){const ch=row[q];if(ch==="."||ch==="g"||(ch==="l"&&!pal.l))continue;
      let col=pal[ch]||"#f0f";if(ch==="l"&&sea==="Spring"&&R()<.15)col="#f4a8c8";
      if(tint){if(SCN_STYLE.sil)col=mix(col,mix(skyAt(oy+y),SHADE,DARK.has(ch)?.55:.32),SCN_STYLE.sil);col=mix(col,skyAt(oy+y),tint);}
      px(ox+q,oy+y,col);if(track)(occ[ox+q]=occ[ox+q]||[]).push(oy+y);}});};
  const halo=(rows,ox)=>{const oy=G-(rows.length-1);c.fillStyle=pal.k;
    rows.forEach((row,y)=>{for(let q=0;q<row.length;q++){const ch=row[q];if(ch==="."||ch==="g"||(ch==="l"&&!pal.l))continue;
      [[1,0],[-1,0],[0,-1]].forEach(([dx,dy])=>c.fillRect(ox+q+dx,oy+y+dy,1,1));}});};
  const al=n=>INF[n]&&INF[n].bt?0.45:1,T=SCN_STYLE.fade;
  // ---- gaps between settlements: which one carries the single bridge
  const gaps=[];for(let i=0;i<=lots.length;i++)gaps.push({i,x0:i?lots[i-1].x1+1:0,x1:i<lots.length?lots[i].x0-1:W-1,between:i>0&&i<lots.length});
  const between=gaps.filter(g=>g.between),bridgeGap=has("Bridges")?(between.length?between[Math.floor((between.length-1)/2)]:gaps[gaps.length-1]):null;
  // ---- span: one aqueduct, the farthest layer. It joins the first and last settlement that carries infrastructure
  // (not PLATE_NO_INFRA), ends hidden behind their cores; with only one such settlement it runs off the right edge.
  const anchors=lots.filter(o=>!o.L.bare);
  if(has("Aqueducts")&&anchors.length){const k="inf:Aqueducts",w=SW(k),mid=o=>o.x0+Math.floor(o.Lw/2);
    const a0=mid(anchors[0]),a1=anchors.length>1?mid(anchors[anchors.length-1]):W;
    for(let q=a0;q<=a1;q+=w)draw(SPR.S[k],q,al("Aqueducts"),Math.min(.6,T+.2),false);}
  // ---- skylines
  lots.forEach(o=>{const t=o.L.s.tier,core="sky:core:"+t,fill="sky:fill:"+t,cw=SW(core),cx=o.x0+Math.floor((o.Lw-cw)/2),bare=o.L.bare,sa=settUnbuilt(o.L.s)?0.45:1;
    const inf=n=>!bare&&has(n);
    for(let q=o.x0,fw=SW(fill);fw&&q<=o.x1-fw+1;q+=fw+1)draw(SPR.S[fill],q,sa,T,true);
    const by=(kd,ps)=>Object.keys(INF).filter(n=>INF[n].kind===kd&&(ps==null||INF[n].pos===ps)&&inf(n)&&SPR.S["inf:"+n]);
    by("slot","left").forEach(n=>{const k="inf:"+n;draw(SPR.S[k],Math.max(o.x0,cx-SW(k)+3),al(n),T,true);});
    by("slot","right").forEach(n=>{const k="inf:"+n;draw(SPR.S[k],Math.min(o.x1-SW(k)+1,cx+cw-3),al(n),T,true);});
    o.L.wonders.forEach((wd,i)=>{const w=SW(wd.key),j=Math.floor(i/2),wx=i%2?cx+cw+WON_GAP+j*26:cx-WON_GAP-w-j*26;
      draw(SPR.S[wd.key],Math.max(o.x0,Math.min(o.x1-w+1,wx)),wd.bt?0.45:1,T,true);});
    draw(SPR.S[core],cx,sa,T,true);
    // centre slot (Chapel, then the Cathedral that replaces it) stands in front of the core, so a Chapel shorter than the core shows
    by("slot","center").forEach(n=>{const k="inf:"+n;draw(SPR.S[k],o.x0+Math.floor((o.Lw-SW(k))/2),al(n),T,true);});
    by("edge","left").forEach(n=>draw(SPR.S["inf:"+n],o.x0,al(n),T,true));
    by("edge","right").forEach(n=>draw(SPR.S["inf:"+n],o.x1-SW("inf:"+n)+1,al(n),T,true));
    by("band").forEach(n=>{const k="inf:"+n,w=SW(k);for(let q=o.x0;q<=o.x1-w+1;q+=w)draw(SPR.S[k],q,al(n),T,true);
      const tw="inf:"+n+":tower";if(SPR.S[tw]){draw(SPR.S[tw],o.x0,al(n),T,true);draw(SPR.S[tw],o.x1-SW(tw)+1,al(n),T,true);}});});
  // ---- ground, roads, gaps (trees or stream + bridge)
  const grass=(mapPal((D.map||{}).grid)||{}).plains||"#7fa452";
  const gr=sea==="Winter"?SCN.ground.Winter:[mix(grass,"#ffffff",.18),grass];
  c.fillStyle=gr[0];c.fillRect(0,G,W,1);c.fillStyle=gr[1];c.fillRect(0,G+1,W,H-G-1);
  const road=Object.keys(INF).find(n=>INF[n].kind==="ground");
  if(road&&lots.length){const stone=INF[road].pos==="stone",r0=lots[0].x0,r1=lots[lots.length-1].x1,rg=al(road)<1?.45:0,pv=col=>rg?mix(col,grass,rg):col;   // one road joining every settlement
    for(let q=r0;q<=r1;q++)for(let y=G+2;y<=G+4;y++)px(q,y,pv(stone?((q+y)%3?pal.t:pal.u):((q*7+y)%5?pal.b:pal.d)));}
  gaps.forEach(g=>{const mid=Math.floor((g.x0+g.x1)/2);
    if(g===bridgeGap){const wc=al("Bridges")<1?mix(pal.e,grass,.45):pal.e;for(let q=mid-5;q<=mid+5;q++)for(let y=G;y<H;y++)px(q,y,wc);
      draw(SPR.S["inf:Bridges"],mid-7,al("Bridges"),0,true);}
    else if(!(g.i>0&&(AR[g.i-1]||[]).length))draw(SPR.S["scenery:tree"],mid-8,1,0,true);});
  // ---- holdings, then the terrain at their feet, then foreground pieces
  if(SCN_STYLE.halo)placed.forEach(p=>halo(p.rows,p.x));
  placed.forEach(p=>draw(p.rows,p.x,p.it.bt?0.45:1,0,true));
  placed.forEach(p=>{if(p.it.ft){const f=SPR.S[p.it.ft];draw(f,p.x+Math.floor((p.w-f[0].length)/2),1,0,true);}});
  const SCA=[];{const own=playerOfBoard(S),keepP=pal.p;if(own)pal.p=own.color;
    lots.forEach((o,i)=>{let ax=o.x1+3;(AR[i]||[]).forEach(a=>{const rows=SPR.S["army:"+(a.retinue||BANDIT_DEFAULT_RETINUE)];if(!rows)return;
      draw(rows,ax,1,0,true);SCA.push({x:ax,w:rows[0].length,h:rows.length,name:(a.label||("Army "+a.id))+" · "+(a.retinue||"")+" ×"+(a.count||0)});ax+=rows[0].length+2;});});
    pal.p=keepP;}
  lots.forEach(o=>{if(o.L.bare)return;Object.keys(INF).filter(n=>INF[n].kind==="front"&&SPR.S["inf:"+n]).forEach(n=>{const k="inf:"+n;
    draw(SPR.S[k],INF[n].pos==="right"?o.x1-SW(k)+1:o.x0,al(n),0,true);});});
  if(sea==="Winter"){occ.forEach((ys,q)=>{if(!ys)return;const t=Math.min(...ys);px(q,t,"#ffffff");});
    for(let i=0;i<W/2;i++)px(Math.floor(R()*W),Math.floor(R()*G),"#ffffff");}
  if(sea==="Spring")for(let i=0;i<W/10;i++)px(Math.floor(R()*W),G+2+Math.floor(R()*6),R()<.5?"#f4e04a":"#f4a8c8");
  if(sea==="Summer")for(let i=0;i<W/14;i++)px(Math.floor(R()*W),G+2+Math.floor(R()*6),"#2a6a1e");
  if(sea==="Fall")for(let i=0;i<W/8;i++)px(Math.floor(R()*W),Math.floor(R()*G),R()<.5?"#d8742a":"#b8432f");
  const avail=box.clientWidth||600,z=Math.max(2,Math.min(4,Math.floor((avail-4)/W)));
  cv.style.width=(W*z)+"px";cv.style.height=(H*z)+"px";
  const hit=e=>{const q=Math.floor(e.offsetX/z),y=Math.floor(e.offsetY/z),h=placed.find(p=>q>=p.x&&q<p.x+p.w&&y>=G-p.rows.length);
    {const ah=SCA.find(a=>q>=a.x&&q<a.x+a.w&&y>=G-a.h);if(ah)return ah.name;}
    if(h)return h.it.name;const L=lots.find(l=>q>=l.x0&&q<=l.x1);return L?(L.L.s.name||L.L.s.tier):"";};
  cv.onmousemove=e=>{const t=hit(e);cv.title=window.dispName?window.dispName(t):t;};   // display names (NAME_DISPLAY), e.g. Castle Yard
  cv.onclick=e=>{const q=Math.floor(e.offsetX/z),L=lots.find(l=>q>=l.x0&&q<=l.x1);if(L&&L.L.s.id!==activeSid){activeSid=L.L.s.id;render();}};
  const lb=document.createElement("div");lb.className="scnlabels";lb.style.width=(W*z)+"px";
  lots.forEach(o=>{const s=o.L.s,sp=document.createElement("span");sp.textContent=s.name||s.tier;sp.className=s.id===activeSid?"on":"";
    {const pl=playerOfBoard(S),SL=pl?settStatus(pl,s):[],L=[...new Set(SL.map(o=>o.st))];if(L.length){sp.insertAdjacentHTML("afterbegin",L.map(t=>stIcon(t,12)).join("")+" ");sp.title=SL.map(o=>o.txt).join("\n");}}
    sp.style.left=(o.x0*z)+"px";sp.style.width=(o.Lw*z)+"px";sp.onclick=()=>{activeSid=s.id;render();};lb.appendChild(sp);});
  box.innerHTML="";box.appendChild(cv);box.appendChild(lb);
}
window.addEventListener("resize",()=>{renderScene();});
// the header follows the page; past the first screen-top it drops its secondary rows so the Table stays usable
// header: no scroll-driven resizing (a header that shrinks on scroll shortens the page, which un-scrolls it, which grows the
// header again — the flicker). Its height is measured whenever its own size changes and published as --tbh.

// ---- settlements overview (read-only; build/place happens in the Pursuits section) ----
function renderSettlements(){
  const grid=document.getElementById("setGrid");grid.innerHTML="";const SET=DATA.settlements;
  const byTier={};S.settlements.forEach(s=>byTier[s.tier]=(byTier[s.tier]||0)+1);
  let avail=0,used=0,tax=0;
  const wtx=winterTax(S),tmod=t=>{const b=SET[t].tax_income||0;return b?b+Math.max(-b,wtx.mod):0;};
  S.settlements.forEach(s=>{const wu=wardUse(s.id);avail+=wu.cap;used+=wu.used;});tax=wtx.total;
  Object.keys(byTier).forEach(t=>{
    const lbl=document.createElement("div");
    lbl.innerHTML=t+' ×'+byTier[t]+' <span class="note">('+SET[t].wards+'w'+(SET[t].tax_income?', '+(wtx.mod?'<s>'+SET[t].tax_income+'</s> ':'')+tmod(t)+'g':'')+')</span>';
    const sp=document.createElement("div");sp.className="note";sp.textContent="";
    grid.appendChild(lbl);grid.appendChild(sp);
  });
  if(!S.settlements.length){const d=document.createElement("div");d.className="note";d.textContent="no settlements — add them in the Pursuits section";grid.appendChild(d);grid.appendChild(document.createElement("div"));}
  const unplaced=S.placed.filter(p=>p.sid==null).length;
  document.getElementById("wards").textContent=used+" / "+avail+(unplaced?("  ("+unplaced+" unplaced)"):"");
  {const ws=document.getElementById("wardsS");if(ws)ws.textContent=used+" / "+avail;}
  document.getElementById("tax").textContent=fmt(tax)+(wtx.src.length?" ("+wtx.src.join(", ")+")":"");
  const bar=document.getElementById("wardbar");bar.innerHTML="";const pct=avail?Math.min(100,used/avail*100):0;
  const f=document.createElement("span");f.style.width=pct+"%";f.style.background=used>avail?cvar("--upkeep"):cvar("--income");
  const rest=document.createElement("span");rest.style.width=(100-pct)+"%";rest.style.background=cvar("--barbg");
  bar.appendChild(f);bar.appendChild(rest);
}

// ---- treasury ----
const trIn=document.getElementById("treasury");
trIn.value=S.treasury;document.getElementById("turn").textContent=S.turn;
document.getElementById("autoNet").checked=S.autoNet;
trIn.oninput=()=>{S.treasury=+trIn.value||0;save();treasLive();};
document.getElementById("autoNet").onchange=e=>{S.autoNet=e.target.checked;save();};
document.getElementById("endturn").onclick=()=>{
  boardEndTurn(S);trIn.value=S.treasury;document.getElementById("turn").textContent=S.turn;save();render();
};
document.getElementById("poMinus").onclick=()=>{S.po=Math.max(PO_MIN,(S.po||0)-1);save();render();};
document.getElementById("poPlus").onclick=()=>{S.po=Math.min(PO_MAX,(S.po||0)+1);save();render();};
document.querySelectorAll("[data-gold]").forEach(b=>b.onclick=()=>{S.treasury=(S.treasury||0)+(+b.dataset.gold);trIn.value=S.treasury;save();treasLive();});

// ---- toolbar ----
document.getElementById("clear").onclick=()=>{const b=activeBoard();b.placed=[];b.settlements=startSettlements();b.startSig=startSig();b.infra={};b.wonders={};b.armies=[];nameAllSetts();reindex();save();render();renderList();};
document.getElementById("export").onclick=()=>{const b=new Blob([JSON.stringify(D,null,2)],{type:"application/json"});
  const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="renown_build.json";a.click();};
document.getElementById("import").onclick=()=>document.getElementById("file").click();
document.getElementById("file").onchange=e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();
  rd.onload=()=>{try{const j=JSON.parse(rd.result); if(j&&j.players){D=j;}else{D={players:[newPlayer(1)],active:0,view:D.view,renown:1,map:D.map};D.players[0].board=Object.assign(newBoard(),j);} normalizeD(); D.active=0; reindex();
    trIn.value=S.treasury;document.getElementById("turn").textContent=S.turn;document.getElementById("autoNet").checked=S.autoNet;
    save();render();renderList();}catch(err){alert("bad json");}};rd.readAsText(f);};
document.getElementById("addArmy").onclick=()=>{const L=EQ.retinues.Levy||{};S.armies.push({id:aid++,label:"",upkeep:L.cost||0,retinue:"Levy",count:0,endurance:L.endurance||0,fatigue:0,weapon:"Farm Tools",ranged:"None",armor:"Cloth",shield:"None",strained:false,blunder:false,open:true});save();render();};
document.getElementById("hideCombat").onchange=render;
document.getElementById("search").oninput=renderList;

document.getElementById("ver").textContent=DATA.version;
if(DATA.warnings&&DATA.warnings.length)document.getElementById("assump").innerHTML="<span class='warn'>"+DATA.warnings.join("<br>")+"</span>";
else document.getElementById("assump").closest("details").remove();

// ---- top bar ⋯ (phones): modules, theme, shape ----
document.getElementById("tbMore").onclick=()=>{document.body.classList.toggle("tbopen");mnavSync();};
// ---- claim lock, enforced at the event level (capture phase, before any handler): on a server game you change only
// your claimed player's board; spectators (no claim) can't act at the Table, turn strip or Realm. Browsing stays free.
const LK_NAV='summary,.pcaret,.caret,.stitle,[data-nav],#export,#tabs .tab,#search,#typeFilters,#typeFilters *,#hideCombat,.kw,[data-tok],[data-goto],[data-mc],.vtab,.pchip,[data-claim]';
const LK_EDIT='button,input,select,textarea,[draggable="true"]';
// shared Table state: Duke only (Renown moves by Edicts and End turn; Season by End turn); Bandit controls: Host (or Duke)
const LK_DUKE='[data-ts="sea-"],[data-ts="sea+"],[data-ts="rn-"],[data-ts="rn+"],#rnMinus,#rnPlus,#rnVal,.sdbtn,#applyStart';
const LK_MAPSETUP='#mGen,#mCodeGo,#mImp,#mFile,#mClear,#mPreset,#mSeedN,#mPl,#mW,#mH,#mCode';   // Host during setup, Duke always
const LK_HOST='.bcn,.bct,.bcx,.bcr,.bcv,.bcm,#bGrow,#bSpawn,.bAuto';
function lockTarget(el){if(!lockOn())return null;
  if(el.closest(LK_DUKE))return "duke";
  if(el.closest(LK_MAPSETUP))return (firstHostOpen()&&canHost())?null:"duke";
  if(el.closest(LK_HOST)&&!canHost())return "host";
  if(el.closest("[data-claim],#viewTabs,#tbMore,#appMenu,.tbextra,#hud,.modalcard,#mnav,#chatDock"))return null;
  const rp=el.closest("#viewRealm [data-pi]");if(rp){const q=D.players[+rp.dataset.pi];return q&&!mine(q)?q:null;}
  if(el.closest("#appBoard,#playerBar")){const q=D.players[D.active];return q&&!mine(q)?q:null;}
  if(!myClaimP()&&el.closest("#viewTable,#turnStrip,#setupPanel,#viewRealm,#viewBattle"))return "spectator";
  return null;}
function lockBlock(e){const el=e.target;if(!(el instanceof Element))return null;const t=lockTarget(el);if(!t)return null;
  const hit=el.closest(LK_EDIT+","+LK_NAV);if(hit&&hit.matches(LK_NAV))return null;return t;}
["pointerdown","click","change","input","keydown","dragstart","drop"].forEach(ty=>document.addEventListener(ty,e=>{
  if(ty==="keydown"&&(e.key==="Tab"||e.key==="Escape"))return;
  const t=lockBlock(e);if(!t)return;
  e.stopImmediatePropagation();if(ty!=="pointerdown")e.preventDefault();
  if(ty==="click")flash(t==="spectator"?"claim a player to act":t==="duke"?"Duke only":t==="host"?"Host only":"\ud83d\udd12 "+t.name+"'s board");
  if(ty==="change"||ty==="input")setTimeout(render,0);},true));
document.addEventListener("click",e=>{if(document.body.classList.contains("tbopen")&&!e.target.closest("#appMenu,#tbMore,.tbextra"))document.body.classList.remove("tbopen");});
document.addEventListener("click",e=>{const v=e.target.closest("#viewTable [data-mz]");if(v){mapZoom(v.dataset.mz==="fit"?"fit":+v.dataset.mz);}
  const b=e.target.closest("[data-bs]");if(b&&b.closest(".bside-nav")){BSIDE=b.dataset.bs;render();}});
let BSIDE="";   // phone Battle view: which side card to show (per device, not synced)
// ---- admin unlock ----
function adminUI(){const st=document.getElementById("adminState");if(st)st.innerHTML=ADMIN?'<b style="color:var(--order)">ON</b>':'off';
  document.body.classList.toggle("is-admin",ADMIN);}
async function adminSet(on){
  if(!on){ADMIN=false;try{sessionStorage.removeItem("renown_admin");sessionStorage.removeItem("renown_pin");}catch(e){}adminUI();render();flash("the Duke steps down");return;}
  const pin=(document.getElementById("adminPin")||{}).value||"";
  if(API.online){let ok=false,open=false;
    try{const h={"Content-Type":"application/json"};if(TOKEN)h["X-Renown-Token"]=TOKEN;
      const r=await fetch("/api/admin",{method:"POST",headers:h,body:JSON.stringify({pin})});const j=await r.json().catch(()=>({}));ok=!!j.ok;open=!!j.open;}catch(e){}
    if(!ok){flash("wrong Duke PIN");return;}if(open)flash("Duke unlocked (server has no PIN set)");}
  ADMIN=true;try{sessionStorage.setItem("renown_admin","1");if(pin)sessionStorage.setItem("renown_pin",pin);}catch(e){}const pi=document.getElementById("adminPin");if(pi)pi.value="";
  adminUI();render();if(API.online)flash("the Duke presides");else flash("Duke unlocked (offline)");}
document.getElementById("adminOn").onclick=()=>adminSet(true);document.getElementById("adminOff").onclick=()=>adminSet(false);
document.getElementById("adminPin").onkeydown=e=>{if(e.key==="Enter")adminSet(true);};
adminUI();
// ---- turn strip: Turn · Season · Renown/Era · Phase · Host · End turn (one place for all turn state) ----
// first Host (setup): any seated player can take the Host card, or hand it back, until the first turn gets going
function firstHostOpen(){return tTurn()===1&&!TB().phaseTs;}
function firstHostBtn(){if(!firstHostOpen())return "";const me=meP(),hp=hostP(),t=TB();
  if(!me||!seated().some(p=>sameP(p,me)))return ' <span class="note">(sit at the Table to claim Host)</span>';
  if(t.hostSet&&sameP(hp,me))return '<button data-ts="host-off" title="hand the Host card back">give up Host</button>';
  if(t.hostSet)return "";                                   // someone has claimed it; they can give it up
  return '<button data-ts="host-on" title="take the Host card for the first turn">take first Host</button>';}
// ---- HUD: the active player's numbers in one condensed row (label over value); click a cell to jump to its panel ----
function hudSign(v){return (v>0?"+":v<0?"\u2212":"\u00b1")+Math.abs(Math.round(v)).toLocaleString();}
function hudData(p){const b=p.board,sn=seasonNet(b),m=sn.m,rows=poModRows(b),po=b.po||0,dbl=1;
  const wu=withBoard(b,()=>(b.settlements||[]).reduce((a,s)=>{const w=wardUse(s.id);a.u+=w.used;a.c+=w.cap;return a;},{u:0,c:0}));
  const caps=withBoard(b,()=>({a:eraCap("armies"),s:eraCap("max_settlements")}));
  const fRows=rows.filter(r=>r.side==="faith"&&r.n),dRows=rows.filter(r=>r.side==="doubt"&&r.n);
  return {gold:b.treasury||0,net:sn.net,infl:influenceTotal(b),env:personalEnvoys(p),po,
    faith:(m.faith||0)+fRows.reduce((a,r)=>a+r.n,0)*dbl,doubt:(m.doubt||0)+dRows.reduce((a,r)=>a+r.n,0)*dbl,pieceF:m.faith||0,pieceD:m.doubt||0,fRows,dRows,dbl,
    craft:m.craft||0,band:(poBandName(po)||[])[0]||"",armies:(b.armies||[]).length,armyCap:caps.a,
    setts:(b.settlements||[]).length,settCap:caps.s,wu,dom:b.domains||{},edicts:edictTotal(p),flags:p===D.players[D.active]?boardFlags().length:0};}
// descriptor lines per HUD value for any player (HUD title, player table hover)
function hudTips(p,h){h=h||hudData(p);const b=p.board,sg=v=>(v>0?"+":"")+v;
  const po=["Public Order "+h.po+" · "+h.band,"Faith +"+h.faith+" / Doubt +"+h.doubt+" at the next Empire Phase"+(h.dbl>1?" (modifiers ×2)":""),
    "  pieces: Faith +"+h.pieceF+" / Doubt +"+h.pieceD].concat(h.fRows.map(r=>"  Faith +"+r.n+" · "+r.k)).concat(h.dRows.map(r=>"  Doubt +"+r.n+" · "+r.k));
  let infl=[];try{infl=influenceRows(b).filter(r=>r.val||r.cnt).map(r=>"  "+r.k+(r.cnt>1?" ×"+r.cnt:"")+" "+sg(r.val));}catch(e){}
  const W=withBoard(b,()=>(b.settlements||[]).map(s=>{const w=wardUse(s.id);return "  "+(s.capital?"★ ":"")+(s.name?s.name+" · ":"")+s.tier+" · Wards "+w.used+"/"+w.cap;}));
  return {gold:goldBreakTxt(goldBreak(b)),
    infl:["Influence this turn "+inflPool(p)].concat(infl).join("\n"),
    env:["Personal Envoys "+h.env,"  "+currentEra()+" (Era) "+(+eraRec().personal_envoys||1)].join("\n"),
    po:po.join("\n"),
    armies:["Armies "+h.armies+(h.armyCap!=null?" / "+h.armyCap+" ("+currentEra()+")":"")].concat((b.armies||[]).map(a=>"  "+(a.label||("Army "+a.id))+" · "+(a.retinue||"")+" ×"+(a.count||0))).join("\n"),
    setts:["Settlements "+h.setts+(h.settCap!=null?" / "+h.settCap:"")+" · Wards "+h.wu.u+"/"+h.wu.c].concat(W).join("\n"),
    edicts:"Completed Edicts "+h.edicts,
    dom:DOMAINS.map(d=>d+" "+(+(h.dom[d])||0)+" · "+domBand(+(h.dom[d])||0)).join("\n")};}
function renderHUD(){const el=document.getElementById("hud");if(!el)return;const p=D.players[D.active];if(!p){el.innerHTML="";return;}
  const h=hudData(p),cls=v=>v>0?"up":v<0?"dn":"";
  let left=null;try{const R=tSim();const pool=R.pool[p.id]??inflPool(p);left=pool-(R.spent[p.id]||0);}catch(e){}
  const cell=(col,lab,val,pop,tip)=>{const [cv,cx]=col.split(" ");return '<div class="hc'+(cx?' '+cx:'')+(HPOP===pop?' on':'')+'" style="--hcol:var('+cv+')" data-pop="'+pop+'" title="'+esc(tip||"")+'"><span class="hl">'+lab+'</span><span class="hv">'+val+'</span></div>';};
  const ST=["Untested","Rising","Established","Sovereign"],dom=DOMAINS.map(d=>{const v=h.dom[d]||0,i=ST.indexOf(domBand(v));
    return '<span title="'+esc(d+" "+v+" · "+domBand(v))+'" class="st'+i+'"><em>'+d.slice(0,3)+'</em>'+v+'</span>';}).join("");
  const poTip=["Public Order "+h.po+" · "+h.band,"Faith +"+h.faith+" / Doubt +"+h.doubt+" at the next Empire Phase"+(h.dbl>1?" (modifiers ×2)":""),
    "  pieces: Faith +"+h.pieceF+" / Doubt +"+h.pieceD].concat(h.fRows.map(r=>"  Faith +"+r.n+" · "+r.k)).concat(h.dRows.map(r=>"  Doubt +"+r.n+" · "+r.k)).join("\n");
  const bst=Math.max(0,...D.players.map(edictTotal)),lead=bst>0&&h.edicts===bst;
  el.innerHTML='<div class="hrow">'+
    cell("--order","Gold",fmtG(h.gold)+' <small class="'+cls(h.net)+'">'+hudSign(h.net)+'</small>',"gold","Treasury · this Season's net (income, Winter tax, trade, upkeep) — click for the breakdown")+
    cell("--influence","Influence",(left!=null?left:hudSign(h.infl).replace("\u00b1","")),"infl","Influence you have this turn"+(left!=null?" (gain "+h.infl+")":""))+
    cell("--envoy","Envoys",h.env,"env","Personal Envoys this turn")+
    cell("--income wide","Public Order",(h.po>0?"+":"")+h.po+' <small>'+esc(h.band)+'</small> <small class="up">F'+h.faith+'</small><small class="dn">D'+h.doubt+'</small>',"po",poTip)+
    cell("--craft","Craft",h.craft,"craft","Craft X")+
    '<div class="hc wide'+(HPOP==="dom"?' on':'')+'" style="--hcol:var(--build)" data-pop="dom" title="Domain values (colour = Standing)"><span class="hl">Domains</span><span class="hv hdom">'+dom+'</span></div>'+
    cell("--battle","Armies",h.armies+(h.armyCap!=null?"/"+h.armyCap:""),"armies","Armies / Era cap")+
    cell("--season","Settlements",h.setts+(h.settCap!=null?"/"+h.settCap:"")+' <small>W'+h.wu.u+'/'+h.wu.c+'</small>',"setts","Settlements / Era cap · Wards used / available")+
    cell("--order","Edicts",h.edicts+(lead?" ★":""),"edicts","Completed Edicts"+(bst?" · most "+bst:""))+'</div>';}
// Turn · (Year) · Age — Age, starting Year and (Age of Renown) each player's Rising are picked during setup
function ageStripHTML(){const a=ageRec(),y=curYear(),edit=firstHostOpen()&&canHost(),me=meP();
  let h='<span class="ts-i"><span class="note">Turn</span> <b>'+tTurn()+'</b>'+(y!=null?' <span class="note">(Year '+y+')</span>':'');
  if(edit){h+=' <select data-ts-age title="Age"><option value="">— Age —</option>'+AGE_L.map(x=>'<option'+(x.name===D.age?' selected':'')+'>'+esc(x.name)+'</option>').join('')+'</select>';
    if(a)h+=' <input type="number" data-ts-year min="'+a.years[0]+'" max="'+a.years[1]+'" value="'+(D.year0!=null?D.year0:a.years[0])+'" style="width:64px" title="starting Year '+a.years[0]+'–'+a.years[1]+'">';}
  else if(a)h+=' <b>'+esc(a.name)+'</b>';
  if(a&&!a.rising&&firstHostOpen()&&me&&canAct(me))h+=' <span class="note">Rising</span> <select data-ts-rise><option value="">—</option>'+
    DOMAINS.map(d=>'<option'+(d===me.board.ageRising?' selected':'')+'>'+d+'</option>').join('')+'</select>';
  return h+'</span>';}
document.addEventListener("change",e=>{const el=e.target;if(!el.closest||!el.closest("#turnStrip"))return;
  if(el.hasAttribute("data-ts-age")){if(el.value)D.age=el.value;else delete D.age;delete D.year0;D.yearsGone=0;applyAgeStart();save();render();}
  else if(el.hasAttribute("data-ts-year")){const a=ageRec();if(!a)return;D.year0=Math.max(a.years[0],Math.min(a.years[1],Math.round(+el.value||a.years[0])));save();render();}
  else if(el.hasAttribute("data-ts-rise")){const me=meP();if(!me)return;if(el.value)me.board.ageRising=el.value;else delete me.board.ageRising;
    me.board.domains=startDomsFor(me);save();render();}});
// ---- Setup Order (RULES › Setup): shown from Start game until the Host begins Turn 1's first phase ----
function setupOn(){return !!D.started&&firstHostOpen();}
function renderSetup(){const el=document.getElementById("setupPanel");if(!el)return;
  if(!setupOn()){el.hidden=true;el.innerHTML="";return;}el.hidden=false;
  const M=mapState(),g=M.grid,a=ageRec(),hp=hostP(),P=D.players,need=+BAN.outlawStart||0;
  const ok=v=>v?'<b class="su-ok">\u2713</b>':'<b class="su-no">\u00b7</b>',dot=p=>'<span class="pdot" style="background:'+p.color+'"></span>';
  const rise=a&&!a.rising?P.map(p=>({p,d:p.board.ageRising||""})):null;
  const dep=P.map(p=>{const st=mapSetts().filter(x=>String(x.cell.player)===String(p.id));
    return {p,town:st.some(x=>x.cell.type==="Town"),ham:st.some(x=>x.cell.type==="Hamlet"),oc:outlawOf(p).filter(o=>!isWild(o)).length,fl:charterFlags(p).length};});
  const rows=[
    ["Select Map",!!g,g?esc(g.preset)+' · seed '+g.seed+' · '+g.width+'\u00d7'+g.height:'<a href="#" data-goto="table#tMapTools">map setup \u25b8</a>'],
    ["Select Age",!!a&&(!rise||rise.every(x=>x.d)),a?esc(a.name)+' · Year '+curYear()+(rise?'<br>'+rise.map(x=>dot(x.p)+esc(x.p.name)+' '+esc(x.d||"\u2014")).join(' · '):''):'turn strip'],
    ["Select Faction",P.every(p=>p.board.faction),P.map(p=>dot(p)+esc(p.name)+' '+esc(p.board.faction||"\u2014")).join(' · ')],
    ["Determine Host",!!TB().hostSet,hp?dot(hp)+esc(hp.name)+(TB().hostSet?'':' (default)'):'\u2014'],
    ["Deploy",dep.every(x=>x.town&&x.ham&&x.oc>=need&&!x.fl),dep.map(x=>dot(x.p)+esc(x.p.name)+' Town '+ok(x.town)+' Hamlet '+ok(x.ham)+' Outlaw '+x.oc+'/'+need+(x.fl?' <span class="su-fl">\u2691'+x.fl+'</span>':'')).join('<br>')],
    ["Wild Outlaw Country",wildDone(),(()=>{const n=Object.keys(wildZones()).length,c=wildCount();return n+(c!=null?'/'+c:'')+' zones'+
      (canHost()&&g?(wildDone()?' <button data-setup-wild="redo">redo</button>':' <button data-setup-wild="1">place \u25b8</button>'):'');})()]];
  // stepper: one step open at a time (the first not done, unless you stepped elsewhere); the panel closes once Turn 1 begins
  if(SETUP_STEP==null||SETUP_STEP>=rows.length){const f=rows.findIndex(r=>!r[1]);SETUP_STEP=f<0?rows.length-1:f;}
  const k=SETUP_STEP,r=rows[k],last=k===rows.length-1;
  el.innerHTML='<div class="su-step"><b>Setup</b> <span class="su-chips">'+rows.map((x,i)=>'<button data-setup-go="'+i+'" data-nav="1" class="su-chip'+(i===k?' on':'')+(x[1]?' ok':'')+'" title="'+esc(x[0])+'">'+(x[1]?'\u2713':(i+1))+' '+esc(x[0])+'</button>').join('')+'</span></div>'+
    '<div class="su-body"><div class="su-t"><span class="su-n">'+(k+1)+'/'+rows.length+'</span> <b>'+r[0]+'</b> '+ok(r[1])+'</div><div class="su-d">'+r[2]+'</div>'+
    '<div class="su-nav">'+(k>0?'<button data-setup-go="'+(k-1)+'" data-nav="1">\u25c2 back</button>':'')+(!last?'<button data-setup-go="'+(k+1)+'" data-nav="1">next \u25b8</button>':'')+
    '<button data-setup-begin="1" class="'+(rows.every(x=>x[1])?'on':'')+'"'+(canHost()?'':' disabled')+'>Begin Turn 1 \u2014 '+esc(T_PHL[tPhase()])+'</button>'+
    '<span class="note">'+rows.filter(x=>x[1]).length+'/'+rows.length+' done</span></div></div>';}
let SETUP_STEP=null;
document.addEventListener("click",e=>{const b=e.target.closest("[data-setup-go]");if(!b)return;SETUP_STEP=+b.dataset.setupGo;renderSetup();});
document.addEventListener("click",e=>{const w=e.target.closest("[data-setup-wild]");if(w){if(!canHost()){flash("Host only");return;}const n=w.dataset.setupWild==="redo"?rescatterWild():placeWildOutlaw();flash(n?n+" Wild Outlaw Country zone"+(n>1?"s":"")+" placed":"no room for Wild Outlaw Country");save();render();return;}
  const b=e.target.closest("[data-setup-begin]");if(!b)return;if(!canHost()){flash("Host only");return;}if(!wildDone()){placeWildOutlaw();save();}
  D.players.forEach(p=>(p.board.settlements||[]).forEach(s=>nameSett(p,s)));save();tSetPhase(tPhase());});
function renderTurnStrip(){const el=document.getElementById("turnStrip");if(!el)return;
  const ph=tPhase(),hp=hostP(),hc=canHost(),nx=tNext(ph);
  const me=meP(),unseated=me&&!seated().some(p=>sameP(p,me)),steps=(DATA.phaseSteps||{})[ph]||[];
  const cap=s=>s.length>28?s.slice(0,27).replace(/\s+\S*$/,"")+"…":s;
  el.innerHTML=(unseated?'<button class="ts-seat" data-goto="table">Take a seat ▸</button>':'')+
    (()=>{let on=false;try{on=!!SYNC.ready;}catch(e){}if(!on||D.started)return "";
      const rc=readyCheck(),mc=myClaimP(),rdy=mc&&isReady(mc);
      let h='<span class="ts-i" title="'+esc(rc.seat.map(p=>p.name+": "+(isReady(p)?"ready":claimOf(p)?"not ready":"unclaimed")).join("\n"))+'"><span class="note">Ready</span> <b>'+rc.n+'/'+rc.seat.length+'</b></span>';
      if(mc)h+='<button class="ts-ready'+(rdy?' on':'')+'" data-ts="ready">'+(rdy?'\u2713 ready':'ready up')+'</button>';
      if(ADMIN||canHost())h+='<button class="ts-start" data-ts="start"'+(rc.all||ADMIN?'':' disabled')+' title="'+(rc.all?'wipe all but the map and turn on player restrictions':'every seated player must claim and ready up')+'">Start game</button>';
      return h;})()+
    ageStripHTML()+
    '<span class="ts-i"><button data-ts="sea-" title="previous Season">◂</button><b>'+esc(curSeason())+'</b><button data-ts="sea+" title="next Season">▸</button></span>'+
    '<span class="ts-i"><span class="note">Renown</span><button data-ts="rn-">−</button><b>'+(D.renown||1)+'</b><button data-ts="rn+">+</button><span class="note">'+esc(currentEra())+'</span></span>'+
    '<span class="ts-i"><span class="note">Host</span> <b>'+(hp?esc(hp.name):'—')+'</b>'+(hp&&!TB().hostSet?' <span class="note">(default)</span>':'')+(unseated?'':firstHostBtn())+'</span>'+
    '<span class="ts-i ts-ph"><b>'+esc(T_PHL[ph])+'</b>'+(hc?'<button data-ts="ph" title="'+esc(T_PHL[nx])+'">▸</button>':'')+'</span>'+
    (steps.length?'<span class="ts-steps">'+steps.map((s,k)=>'<span class="ts-step" data-tip="'+esc(s[1])+'"><i>'+(k+1)+'</i>'+esc(cap(s[0]))+'</span>').join('')+'</span>':'')+
    ((ADMIN||hc)?'<span class="ts-endg">'+(ADMIN?'<b style="color:var(--order)">♛ DUKE</b>':'')+(hc?'<button class="ts-end" data-ts="end">End turn</button>':'')+'</span>':'');}
document.addEventListener("click",e=>{const b=e.target.closest("#turnStrip [data-ts]");if(!b)return;const k=b.dataset.ts;
  if(k==="sea-"||k==="sea+"){const ys=RC.AGE_YEAR_SEASON,was=curSeason();stepSeason(k==="sea+"?1:-1);
    if(ys&&k==="sea+"&&curSeason()===ys)D.yearsGone=(+D.yearsGone||0)+1;
    else if(ys&&k==="sea-"&&was===ys)D.yearsGone=Math.max(0,(+D.yearsGone||0)-1);
    save();render();}
  else if(k==="rn-"||k==="rn+"){D.renown=Math.max(1,Math.min(+RC.RENOWN_MAX||30,(D.renown||1)+(k==="rn+"?1:-1)));save();render();}
  else if(k==="ph"){tSetPhase(tNext(tPhase()));}
  else if(k==="start"){startGame();}
  else if(k==="ready"){const mc=myClaimP();if(!mc)return;const t=TB();t.ready=t.ready||{};
    if(t.ready[mc.id])delete t.ready[mc.id];else t.ready[mc.id]=true;save();render();}
  else if(k==="host-on"){const t=TB();t.host=String(meP().id);t.hostSet=true;save();render();flash(meP().name+" takes the Host card");}
  else if(k==="host-off"){const t=TB();delete t.host;t.hostSet=false;save();render();flash("Host card is free");}
  else if(k==="end"){if(tPhase()!=="rest"&&!confirm("End the turn now? (current phase: "+T_PHL[tPhase()]+")"))return;tEndTurn();}});
// one End turn: with the Table's "every board" toggle on, the Treasury button defers to it
function syncBoardEndBtn(){const b=document.getElementById("endturn");if(!b)return;const on=boardEndOn();
  b.disabled=on;b.style.display=on?"none":"";b.title="";}
// ⋯ menu: Game + server panels live here (moved once at startup, ids unchanged)
(()=>{const m=document.getElementById("appMenu");["gameBox","srvBox"].forEach(id=>{const e=document.getElementById(id);if(e){e.style.marginTop="0";m.appendChild(e);}});})();
// jump links: data-goto="view", "board:<board|catalog|summary>", "view#elementId"
document.addEventListener("click",e=>{const a=e.target.closest("[data-goto]");if(!a)return;e.preventDefault();
  const [v0,anchor]=a.dataset.goto.split("#"),[v,sec]=v0.split(":");D.view=v;
  if(v==="board"&&sec){const ap=document.getElementById("appBoard");ap.dataset.mc=sec;
    document.querySelectorAll("#mnav [data-mc]").forEach(x=>x.classList.toggle("on",x.dataset.mc===sec));}
  render();setTimeout(()=>{const t=anchor?document.getElementById(anchor):(sec&&window.innerWidth<=700?null:document.getElementById(sec==="summary"?"summary":sec==="board"?"boardcol":""));
    if(t&&t.tagName==="DETAILS"&&!t.open){t.open=true;if(t.id==="refTree"){TREE_SEC=true;treeSave();}if(t.dataset.keep!=null)rlToggle(t);}
    {let pd=t&&t.parentElement&&t.parentElement.closest("details");while(pd){if(!pd.open)pd.open=true;pd=pd.parentElement&&pd.parentElement.closest("details");}}
    if(t)t.scrollIntoView({behavior:"smooth",block:"start"});else window.scrollTo(0,0);},60);});
// ---- phone section switcher (Board / Catalog / Totals) ----
document.querySelectorAll("#mnav [data-mc]").forEach(b=>b.onclick=()=>{document.getElementById("appBoard").dataset.mc=b.dataset.mc;
  document.querySelectorAll("#mnav [data-mc]").forEach(x=>x.classList.toggle("on",x===b));window.scrollTo(0,0);});
function mnavSync(){const tb=document.querySelector(".topbar");if(!tb)return;const v=(getComputedStyle(tb).position==="sticky"?tb.offsetHeight:0)+"px";
  if(document.documentElement.style.getPropertyValue("--tbh")!==v)document.documentElement.style.setProperty("--tbh",v);}
try{new ResizeObserver(()=>mnavSync()).observe(document.querySelector(".topbar"));}catch(e){}
window.addEventListener("resize",mnavSync);

// ---- heraldry (sprites.py her:<charge>): each culture's charge (worldbuilding CULTURES heraldry.primary) on a shield in
// the player's colour. Pale player colours get a dark charge. Shown on Domain tracks, the Realm table, the Empire header, map banners.
const HER=((DATA.placeNames||{}).heraldry)||{};
function herKey(p){const c=p&&p.board&&p.board.culture,a=c&&HER[c];return a&&SPR&&SPR.S["her:"+a]?"her:"+a:null;}
function lumOf(hex){const m=/^#?([0-9a-f]{6})$/i.exec(String(hex||""));if(!m)return 0;const n=parseInt(m[1],16);return (0.299*(n>>16&255)+0.587*(n>>8&255)+0.114*(n&255))/255;}
const HER_SVG={};
// inner markup (paths) of a heraldry sprite in colour col: 'p' = col, 's' = pale or dark by col's lightness
function herPaths(key,col){const ck=key+"|"+col;if(HER_SVG[ck])return HER_SVG[ck];const P=SPR.P||{},rows=SPR.S[key],w=rows[0].length,by={};
  rows.forEach((r,y)=>{let x=0;while(x<w){const ch=r[x];let n=1;while(x+n<w&&r[x+n]===ch)n++;if(ch!=="."&&ch!=="g")by[ch]=(by[ch]||"")+"M"+x+" "+y+"h"+n+"v1h-"+n+"z";x+=n;}});
  const dark=lumOf(col)>0.62,fill=ch=>ch==="p"?col:ch==="s"?(dark?"#1d1a17":(P.s||"#eee")):(P[ch]||"#f0f");
  return HER_SVG[ck]=Object.keys(by).map(ch=>'<path d="'+by[ch]+'" fill="'+fill(ch)+'"/>').join("");}
function heraldOf(p,px){const k=herKey(p);if(!k)return "";
  return '<svg class="her" width="'+px+'" height="'+px+'" viewBox="0 0 16 16" shape-rendering="crispEdges" aria-hidden="true"><title>'+esc(p.board.culture+" · "+HER[p.board.culture])+'</title>'+herPaths(k,p.color)+'</svg>';}
// map: a small banner on each of the player's Settlements
function mapBanner(p,cx,cy,R){const k=herKey(p);if(!k)return "";const w=R*.62;
  return '<svg x="'+(cx-R*1.02).toFixed(1)+'" y="'+(cy-R*1.0).toFixed(1)+'" width="'+w.toFixed(1)+'" height="'+w.toFixed(1)+'" viewBox="0 0 16 16" shape-rendering="crispEdges" pointer-events="none">'+herPaths(k,p.color)+'</svg>';}
