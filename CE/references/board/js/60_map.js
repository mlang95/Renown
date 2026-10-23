// ---- Map view ----
// ---- Map (on the Table): region generator (gen.js) + free placement + Outlaw Country + Bandits ----
const MG=(typeof RenownGen!=="undefined")?RenownGen:null, MP=(typeof RenownPresets!=="undefined")?RenownPresets:{};
const BAN=DATA.bandits||{};
const BOARD_SIZE={2:[19,15],3:[23,18],4:[26,21],5:[29,24],6:[32,26],7:[35,28]};   // mirrors renown-maps.html
// Climate palettes + terrain glyphs come from mapgen/hexstyle.py (RenownStyle, bundled with
// gen.js) - the same source as renown-maps.html and the print board. Fallback if not bundled.
const RS=(typeof RenownStyle!=="undefined")?RenownStyle:null;
const TTYPES=['plains','forest','wetland','tundra','mountain','water'];
const TCOL={plains:'#7fa452',forest:'#24502a',wetland:'#556b4a',tundra:'#8b6a45',mountain:'#6e6a62',water:'#4e7470'};
const TPAL={};
if(RS)Object.keys(RS.climates).forEach(k=>{const o={label:RS.climates[k].label};TTYPES.forEach(t=>o[t]=RS.climates[k][t]);TPAL[k]=o;});
const TDEF=RS?RS.default_climate:"temperate";if(!TPAL[TDEF])TPAL[TDEF]=Object.assign({label:"Temperate"},TCOL);
const RULE_NAME={plains:'Grassland',forest:'Forest',wetland:'Wetlands',tundra:'Tundra',mountain:'Mountains',water:'Water'};
const TREF=DATA.terrainRef||{terrain:{},movement:{},tactical:{},tacticalGlobal:[]};
// climate: the map's own (exports since hexstyle), else its preset's; legacy `art` exports -> wastes/scarlet
function mapClimate(g){if(!g)return TDEF;
  if(g.climate&&TPAL[g.climate])return g.climate;
  if(g.art&&g.art.plains)return g.art.plains==='wastes'?'wastes':'scarlet';
  const pc=(MP[g.preset]||{}).climate;return (pc&&TPAL[pc])?pc:TDEF;}
// colours: swatches saved with an app export (what the person chose) win over the climate
function mapPal(g){const base=TPAL[mapClimate(g)]||TPAL[TDEF];
  if(g&&g.colors&&TTYPES.every(t=>g.colors[t]))return Object.assign({label:base.label+" (custom)"},g.colors);
  return base;}
function tLum(hex){const n=parseInt(hex.slice(1),16),f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);};
  return 0.2126*f(n>>16&255)+0.7152*f(n>>8&255)+0.0722*f(n&255);}
function tTone(fill){return RS?(tLum(fill)<RS.lum_split?RS.light:RS.ink):"#2b241b";}
function tLighten(hex,k){const n=parseInt(hex.slice(1),16),f=v=>Math.min(255,Math.round(v*k));
  return "#"+[f(n>>16&255),f(n>>8&255),f(n&255)].map(v=>v.toString(16).padStart(2,"0")).join("");}
// glyph markup for one terrain, ready to place (relief tokens resolved against the fill)
function tGlyph(kind,fill){if(!RS||!RS.glyphs[kind])return "";
  return RS.glyphs[kind].replace(/currentColor/g,tTone(fill))
    .replace(/"SHADE"/g,'"'+tLighten(fill,RS.shade_k)+'"').replace(/"HILITE"/g,'"'+tLighten(fill,RS.hilite_k)+'"')
    .replace(/"DEEP"/g,'"'+tLighten(fill,RS.deep_k)+'"');}
// small hex swatch with its glyph, for the terrain tables
function tSwatch(kind,fill,px){px=px||26;const g=tGlyph(kind,fill);
  return '<svg class="tswg" width="'+px+'" height="'+(px*0.9).toFixed(0)+'" viewBox="0 0 120 108" aria-hidden="true">'+
    '<polygon points="114,54 87,100.8 33,100.8 6,54 33,7.2 87,7.2" fill="'+fill+'" stroke="#2b241b" stroke-opacity=".45" stroke-width="3"/>'+
    (g?'<g fill="'+fill+'" stroke-width="'+(RS.glyph_w*1.25)+'" stroke-linecap="round" stroke-linejoin="round" opacity="'+RS.glyph_opacity+'">'+g+'</g>':'')+'</svg>';}
const RCOL={mine:'#161616',quarry:'#8a3b2e',arable:'#7a4f2a',forestry:'#2f5d2f',apiary:'#e8c020',salt:'#ece6d6',peat:'#4a3420',fish:'#2f6f8f'};
const C2T={p:'plains',f:'forest',w:'wetland',t:'tundra',m:'mountain','~':'water'};
let MAPVIEW=null;                                   // decoded grid cache {sig, hex:{key:{t,res,reg,hill}}}
function mapState(){const M=D.map;M.cells=M.cells||{};M.outlaw=M.outlaw||{};M.camps=M.camps||{};return M;}
function hexDist(a,b){if(MG)return MG.dist(a,b);
  const cu=(c,r)=>{const x=c,z=r-((c-(c&1))>>1);return [x,-x-z,z];},A=cu(a[0],a[1]),B=cu(b[0],b[1]);
  return (Math.abs(A[0]-B[0])+Math.abs(A[1]-B[1])+Math.abs(A[2]-B[2]))/2;}
function decodeGrid(g){
  const sig=g?(g.preset+":"+g.seed+":"+g.width+"x"+g.height+":"+(g.terrain||[]).join("").length):"none";
  if(MAPVIEW&&MAPVIEW.sig===sig)return MAPVIEW;
  const hex={};
  if(g){let m=null;try{if(MG)m=MG.importMap(g);}catch(e){m=null;}
    for(let c=0;c<g.width;c++)for(let r=0;r<g.height;r++){const k=c+","+r;
      const h=m?m.get([c,r]):null;
      hex[k]={t:C2T[(g.terrain[c]||"")[r]]||"plains",res:(g.resources||{})[k]||null,reg:(g.regions||{})[k],hill:!!(h&&h.tactical==="hill")};}}
  MAPVIEW={sig,hex};return MAPVIEW;
}
function seedCode(g){return g?(g.preset+"/"+g.seed+"/"+g.players+"/"+g.width+"x"+g.height):"";}
function generateMap(preset,seed,players,w,h){
  if(!MG||!MP[preset]){flash("map generator not bundled");return false;}
  const res=MG.generateRegion(MP[preset],{seed:+seed,players:+players,width:+w,height:+h});
  const ex=MG.exportMap(res.map,res.params,+seed,res.violations);
  const M=mapState();M.grid=ex;M.cols=ex.width;M.rows=ex.height;M.seed=String(seed);MAPVIEW=null;
  if(ex.violations&&ex.violations.length)flash("generated with "+ex.violations.length+" validator note(s)");
  return true;
}
function parseSeedCode(s){ // Region/seed/players[/WxH]
  const p=String(s||"").split("/").map(x=>x.trim());if(p.length<3)return null;
  const [preset,seed,pl]=p,wh=(p[3]||"").split("x"),n=+pl,def=BOARD_SIZE[n]||BOARD_SIZE[6];
  if(!MP[preset]||isNaN(+seed)||!n)return null;
  return {preset,seed:+seed,players:n,w:+wh[0]||def[0],h:+wh[1]||def[1]};
}
// map zoom (per device): +/−, or fit to the panel width
// "wide": the Realm map takes the full width and the action panel drops below it (off by default)
let TB_WIDE=false;try{TB_WIDE=localStorage.getItem("renown_rlwide")==="1";}catch(e){}
document.addEventListener("click",e=>{if(!e.target.closest("#tbWide"))return;TB_WIDE=!TB_WIDE;try{localStorage.setItem("renown_rlwide",TB_WIDE?"1":"0");}catch(_){}render();});
const MAPZ={z:1,fit:true,fitScale(W){const el=document.querySelector("#viewTable .tb-map");const w=el?el.clientWidth-4:window.innerWidth-24;return Math.max(0.3,Math.min(3,w/W));}};
try{const mz=JSON.parse(localStorage.getItem("renown_mapz")||"null");if(mz){MAPZ.z=+mz.z||1;MAPZ.fit=!!mz.fit;}}catch(e){}
function mapZoom(k){if(k==="fit")MAPZ.fit=!MAPZ.fit;else{MAPZ.fit=false;MAPZ.z=Math.max(0.5,Math.min(3,Math.round((MAPZ.z*(k>0?1.25:0.8))*100)/100));}
  try{localStorage.setItem("renown_mapz",JSON.stringify({z:MAPZ.z,fit:MAPZ.fit}));}catch(e){}render();}
let MAPSETUP_OPEN=null;   // null = open until terrain is loaded, then remember the player's choice (per device)
document.addEventListener("click",e=>{const sm=e.target.closest("#mSetup > summary");if(sm)MAPSETUP_OPEN=!sm.parentElement.open;});   // user toggles only
// ---- Reach overlay: tier reach (SETTLEMENTS[*].reach) + "Reach +N" on the owner's active pieces,
// measured as a straight-line hex radius (Range as the crow flies). 1 owner = Controlled, 2+ = Contested.
function reachBonus(p){
  if(!p||!p.board)return {b:0,src:[]};
  return withBoard(p.board,()=>{const src=[];let b=0;   // registry: reach_plus (Holding Innate, else its Mastery once earned; faction), reach_plus_rec (Infra / Wonder)
    const earned=SIMPLE?{}:computeEarned(new Set(Object.keys(PC))).earned;
    Object.keys(PC).forEach(n=>{const m=hitOf("h:"+n,"reach_plus")||(earned[n]?hitOf("hm:"+n,"reach_plus"):null);if(m){b+=+m[1];src.push(n+" +"+m[1]);}});
    Object.keys(S.infra||{}).concat(Object.keys(S.wonders||{})).filter(infraOn).forEach(n=>{const m=hitOf((INFRA[n]?"i:":"w:")+n,"reach_plus_rec");if(m){b+=+m[1];src.push(n+" +"+m[1]);}});
    if(S.faction){const m=hitOf("F:"+S.faction,"reach_plus");if(m){b+=+m[1];src.push(S.faction+" +"+m[1]);}}
    return {b,src};});
}
function reachOwners(M,cols,rows){
  const own={},RB={};
  Object.keys(M.cells).forEach(k=>{const cell=M.cells[k];if(cell.type==="Army")return;
    const st=DATA.settlements[cell.type],pl=cellPlayer(cell);if(!st||!pl)return;{const cs=cellSett(k).s;if(cs&&settUnbuilt(cs))return;}
    const rb=RB[pl.id]||(RB[pl.id]=reachBonus(pl)),rad=(+st.reach||0)+rb.b,a=k.split(",").map(Number);
    for(let c=Math.max(0,a[0]-rad);c<=Math.min(cols-1,a[0]+rad);c++)for(let r=Math.max(0,a[1]-rad-1);r<=Math.min(rows-1,a[1]+rad+1);r++)
      if(hexDist(a,[c,r])<=rad)(own[c+","+r]=own[c+","+r]||new Set()).add(String(pl.id));});
  return own;
}
// Raw Materials need their resource within the owner's Reach. Map resources → pursuits;
// Common Land has no map resource (buildable anywhere) and is not checked.
const RES_NODE={mine:"Mine",quarry:"Quarry",arable:"Arable Land",forestry:"Forestry",apiary:"Apiary",salt:"Salt Works",peat:"Peat Bog",fish:"Fishmongery"};
function reachResources(p){
  const M=mapState(),g=M.grid;if(!g||!p)return null;
  if(!Object.values(M.cells).some(c=>c.type!=="Army"&&String(c.player)===String(p.id)))return null;   // not on the map yet
  const V=decodeGrid(g),own=reachOwners(M,g.width,g.height),have=new Set();
  Object.keys(own).forEach(k=>{if(!own[k].has(String(p.id)))return;const h=V.hex[k];if(!h)return;
    if(M.useNodes){if(h.res&&RES_NODE[h.res])have.add(RES_NODE[h.res]);}
    else (((TREF.terrain||{})[RULE_NAME[h.t]]||{})["Raw Materials"]||[]).forEach(n=>have.add(n));});
  return have;
}
// hexes within one Settlement's Reach (null = Settlement not on the map)
function settReachHexes(p,s){
  const M=mapState(),g=M.grid;if(!g)return null;const k=settHex(p,s);if(!k)return null;
  const rad=settReach(p,s),a=k.split(",").map(Number),out=[];
  for(let c=Math.max(0,a[0]-rad);c<=Math.min(g.width-1,a[0]+rad);c++)for(let r=Math.max(0,a[1]-rad-1);r<=Math.min(g.height-1,a[1]+rad+1);r++)
    if(hexDist(a,[c,r])<=rad)out.push(c+","+r);
  return out;
}
// Raw Materials per Settlement: the resource must lie within THAT Settlement's Reach.
// Terrain mode: each terrain type in a Settlement's Reach supplies at most one of its Raw Materials (max matching).
// Nodes mode: a node of that resource within the Settlement's Reach.
// Instances outside a Settlement (no Ward) fall back to Empire-wide Reach; the faction exemption skips claims.
function rawClaims(p){
  const out={},M=mapState(),g=M.grid;if(!g||!p)return out;
  const V=decodeGrid(g),b=p.board,useN=!!M.useNodes,noClaim=!!hitOf("F:"+(b.faction||""),"raw_noclaim");
  const isRaw=q=>!q.fac&&(R[q.name]||{}).type==="Raw Materials"&&Object.values(RES_NODE).includes(q.name);
  const terrRaw=t=>(((TREF.terrain||{})[RULE_NAME[t]]||{})["Raw Materials"]||[]);
  const nodeOf=Object.fromEntries(Object.entries(RES_NODE).map(([k,v])=>[v,k]));
  let emp;const empire=()=>emp!==undefined?emp:(emp=reachResources(p));
  const bySid={};(b.placed||[]).filter(isRaw).forEach(q=>{(bySid[String(q.sid)]=bySid[String(q.sid)]||[]).push(q);});
  Object.keys(bySid).forEach(sid=>{const L=bySid[sid],s=settById(p,sid);
    if(!s){const have=empire();L.forEach(q=>out[q.id]=have?{ok:have.has(q.name),checked:true,why:have.has(q.name)?"":"none in Reach"}:{ok:true,checked:false});return;}
    const hx=settReachHexes(p,s);if(!hx){L.forEach(q=>out[q.id]={ok:true,checked:false});return;}
    const opts=L.map(q=>{const o=new Set();hx.forEach(k=>{const h=V.hex[k];if(!h)return;
      if(useN){if(h.res===nodeOf[q.name])o.add(k);}else if(terrRaw(h.t).includes(q.name))o.add(RULE_NAME[h.t]);});return [...o];});
    if(useN||noClaim){L.forEach((q,i)=>out[q.id]={ok:opts[i].length>0,checked:true,why:opts[i].length?"":"none in Reach"});return;}
    const own={};const aug=(i,seen)=>{for(const t of opts[i]){if(seen.has(t))continue;seen.add(t);if(own[t]==null||aug(own[t],seen)){own[t]=i;return true;}}return false;};
    L.forEach((q,i)=>aug(i,new Set()));
    const got={};Object.keys(own).forEach(t=>got[own[t]]=t);
    L.forEach((q,i)=>out[q.id]=got[i]!=null?{ok:true,checked:true,terr:got[i]}:{ok:false,checked:true,why:opts[i].length?"terrain already claimed ("+opts[i].join(", ")+")":"none in Reach"});});
  return out;
}
// pixel map pieces (sprites.py army:/map:): one <symbol> per sprite, built once; key 'p' = owner colour via currentColor
let MAP_SPR_DEFS=null;
function mapSprId(k){return "ms-"+k.replace(/[^A-Za-z0-9]/g,"_");}
function mapSprDefs(){if(MAP_SPR_DEFS!=null)return MAP_SPR_DEFS;let d="";const P=SPR.P||{};
  const TV={H:"var(--tH)",S:"var(--tS)",D:"var(--tD)",k:"currentColor"};
  Object.keys(SPR.S).filter(k=>/^(army|map|prop|eq|st|mk):/.test(k)).forEach(k=>{const ter=k.startsWith("prop:");const rows=/^(eq|st|mk):/.test(k)?SPR.S[k]:SPR.S[k].slice(0,-1),w=rows[0].length,by={};   // last row = ground, skipped (eq: / st: / mk: have none)
    rows.forEach((r,y)=>{let x=0;while(x<w){const ch=r[x];let n=1;while(x+n<w&&r[x+n]===ch)n++;
      if(ch!=="."&&ch!=="g")by[ch]=(by[ch]||"")+"M"+x+" "+y+"h"+n+"v1h-"+n+"z";x+=n;}});
    d+='<symbol id="'+mapSprId(k)+'" viewBox="0 0 '+w+' '+rows.length+'" shape-rendering="crispEdges">'+
      Object.keys(by).map(ch=>'<path d="'+by[ch]+'" fill="'+(ter&&TV[ch]?TV[ch]:ch==="p"?"currentColor":(P[ch]||"#f0f"))+'"/>').join("")+'</symbol>';});
  return MAP_SPR_DEFS=d;}
// pixel terrain: relief tones mixed toward white/black from the hex fill (multiplying barely moves dark climates)
function tMix(hex,to,t){const a=parseInt(hex.slice(1),16),b=parseInt(to.slice(1),16),f=s=>Math.round((a>>s&255)*(1-t)+(b>>s&255)*t);
  return "#"+[16,8,0].map(s=>f(s).toString(16).padStart(2,"0")).join("");}
// scattered terrain props (sprites.py SCATTER): seeded per map + hex so every client draws the same scatter;
// kept inside the hex, clear of the resource badge, and apart from each other (layer g = min gap, negative = overlap)
const SCAT=((DATA.sprites||{}).scatter)||{};
function hStr(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
function rng32(a){return ()=>{a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return ((t^t>>>14)>>>0)/4294967296;};}
function mapScatter(gk,key,cx,cy,R,fill,seed,badge,inline){const sc=SCAT[gk];if(!sc)return "";
  const pu=R*1.6/16,rnd=rng32(hStr(seed+"|"+key+"|"+gk)),tn=sc.tone||[.30,.20,.48],s3=Math.sqrt(3)/2,lim=R*.92*s3;
  const inside=(x,y)=>{x=Math.abs(x);y=Math.abs(y);return y<=lim&&x*s3+y/2<=lim;},boxes=[],items=[];
  (sc.layers||[]).forEach(L=>{const pool=[];(L.p||[]).forEach(([a,w])=>{for(let i=0;i<w;i++)pool.push(a);});if(!pool.length)return;
    const n=L.n[0]+Math.floor(rnd()*(L.n[1]-L.n[0]+1)),G=L.g!=null?L.g:1;
    for(let i=0;i<n;i++){const a=pool[Math.floor(rnd()*pool.length)],art=SPR.S["prop:"+a];if(!art)continue;
      const w=art[0].length,h=art.length-1;
      for(let t=0;t<40;t++){const ox=Math.round((rnd()*2-1)*L.r*R/pu),oy=Math.round((rnd()*2-1)*L.r*R/pu),
          b=[ox-Math.floor(w/2),oy-Math.floor(h/2)];b.push(b[0]+w,b[1]+h);
        if(![[b[0],b[1]],[b[2],b[1]],[b[0],b[3]],[b[2],b[3]]].every(([x,y])=>inside(x*pu,y*pu)))continue;
        if(badge&&!(b[2]*pu<badge[0]-badge[2]||b[0]*pu>badge[0]+badge[2]||b[3]*pu<badge[1]-badge[2]||b[1]*pu>badge[1]+badge[2]))continue;
        if(boxes.some(q=>!(b[2]+G<=q[0]||q[2]+G<=b[0]||b[3]+G<=q[1]||q[3]+G<=b[1])))continue;
        boxes.push(b);items.push({a,b});break;}}});
  items.sort((x,y)=>x.b[3]-y.b[3]);
  return '<g style="--tH:'+tMix(fill,"#ffffff",tn[0])+';--tS:'+tMix(fill,"#000000",tn[1])+';--tD:'+tMix(fill,"#000000",tn[2])+'" color="'+tTone(fill)+'" pointer-events="none">'+
    items.map(({a,b})=>{const at='x="'+(cx+b[0]*pu).toFixed(2)+'" y="'+(cy+b[1]*pu).toFixed(2)+'" width="'+((b[2]-b[0])*pu).toFixed(2)+'" height="'+((b[3]-b[1])*pu).toFixed(2)+'"';
      return inline?'<svg '+at+' viewBox="0 0 '+(b[2]-b[0])+' '+(b[3]-b[1])+'" shape-rendering="crispEdges">'+propPaths(a)+'</svg>':'<use href="#'+mapSprId("prop:"+a)+'" '+at+'/>';}).join("")+'</g>';}
// a prop sprite's paths, for drawing outside the map (no shared <symbol> defs): relief tones from the enclosing --tH / --tS / --tD
const PROP_PATHS={};
function propPaths(a){if(PROP_PATHS[a])return PROP_PATHS[a];const rows=SPR.S["prop:"+a].slice(0,-1),w=rows[0].length,by={},P=SPR.P||{},TV={H:"var(--tH)",S:"var(--tS)",D:"var(--tD)",k:"currentColor"};
  rows.forEach((r,y)=>{let x=0;while(x<w){const ch=r[x];let n=1;while(x+n<w&&r[x+n]===ch)n++;if(ch!=="."&&ch!=="g")by[ch]=(by[ch]||"")+"M"+x+" "+y+"h"+n+"v1h-"+n+"z";x+=n;}});
  return PROP_PATHS[a]=Object.keys(by).map(ch=>'<path d="'+by[ch]+'" fill="'+(TV[ch]||P[ch]||"#f0f")+'"/>').join("");}
// pixel hex swatch for the terrain tables: the map's own fill + its scattered pixel props (sprites.py SCATTER)
function pxSwatch(kind,fill,px){px=px||30;
  return '<svg class="tswg" width="'+px+'" height="'+(px*0.9).toFixed(0)+'" viewBox="0 0 120 108" aria-hidden="true">'+
    '<polygon points="114,54 87,100.8 33,100.8 6,54 33,7.2 87,7.2" fill="'+fill+'" stroke="#2b241b" stroke-opacity=".45" stroke-width="3"/>'+
    mapScatter(kind,"ref",60,54,52,fill,"terrain-ref",null,true)+'</svg>';}
// sprite standing on an owner-coloured base (dashed red ring when unlinked); col null = unowned (bandits)
function mapSpr(k,cx,cy,R,col,unl){const w=R*1.6,h=w*15/16,y0=cy+R*.62-h;
  return '<ellipse cx="'+cx.toFixed(1)+'" cy="'+(cy+R*.55).toFixed(1)+'" rx="'+(R*.62).toFixed(1)+'" ry="'+(R*.2).toFixed(1)+'" fill="'+(col||"#7a1414")+'" fill-opacity="'+(col?.9:.8)+'"'+
    (unl?' stroke="#b3392f" stroke-width="1.5" stroke-dasharray="3 2"':'')+' pointer-events="none"/>'+
    '<use href="#'+mapSprId(k)+'" x="'+(cx-w/2).toFixed(1)+'" y="'+y0.toFixed(1)+'" width="'+w.toFixed(1)+'" height="'+h.toFixed(1)+'" color="'+(col||"#888")+'" pointer-events="none"/>';}
// ---- loadout icons (sprites.py eq:<item>) + modified Army stats: Army card chips, map plate, hover title, Move panel
const EQ_SVG={};
function eqSVG(name,px,kind){return sprSVG((kind||"eq")+":"+name,px,kind!=="army");}
// any sprite as an inline <svg>: the ground row is dropped; tile = EQ_TILE backing square; col = owner colour for key 'p'
function sprSVG(key,px,tile,col){const raw=SPR&&SPR.S[key];if(!raw)return "";const ck=key+"|"+px+"|"+(tile?1:0)+"|"+(col||"");if(EQ_SVG[ck])return EQ_SVG[ck];
  const rows=/^g+$/.test(raw[raw.length-1])?raw.slice(0,-1):raw,kind=tile?"eq":"army";
  const P=SPR.P||{},w=rows[0].length,by={};
  rows.forEach((r,y)=>{let x=0;while(x<w){const ch=r[x];let n=1;while(x+n<w&&r[x+n]===ch)n++;if(ch!==".")by[ch]=(by[ch]||"")+"M"+x+" "+y+"h"+n+"v1h-"+n+"z";x+=n;}});
  return EQ_SVG[ck]='<svg class="eqi" width="'+px+'" height="'+px+'" viewBox="0 0 '+w+' '+rows.length+'" shape-rendering="crispEdges" aria-hidden="true">'+
    (kind==="army"?'':'<rect width="'+w+'" height="'+rows.length+'" rx=".8" fill="'+(SPR.eqTile||"#3a404c")+'"/>')+
    (col?'<g color="'+col+'">':'')+
    Object.keys(by).map(ch=>'<path d="'+by[ch]+'" fill="'+(ch==="p"&&col?"currentColor":(P[ch]||"#f0f"))+'"/>').join("")+(col?'</g>':'')+'</svg>';}
function stIcon(n,px){return sprSVG("st:"+n,px||14,true);}
function armyGear(a){return [a.weapon,(a.ranged&&a.ranged!=="None")?a.ranged:null,(a.shield&&a.shield!=="None"&&a.shield!=="null")?a.shield:null,a.armor].filter(n=>n&&SPR&&SPR.S["eq:"+n]);}
// the owner's army unlocks/modifiers, as renderArmy builds them for the active board
function armyUFor(p){return withBoard(p.board,()=>{const {earned}=computeEarned(new Set(Object.keys(PC)));const u=armyUnlocks(earned);u.mods=u.mods.concat(facCombat(S));return u;});}
// plate beside the sprite: name (if set), loadout icons, status icons — the stat line lives in the inspector (click the Army)
const PLATE_K=1.5;   // army plate scale vs the hex
const ST_K=2;        // status icon scale (plates and Settlement marks)
// statuses → one icon per kind, its texts joined for the hover title
function stDedup(L){const by={},out=[];L.forEach(o=>{if(!SPR.S["st:"+o.st])return;if(!by[o.st]){by[o.st]={st:o.st,txt:[]};out.push(by[o.st]);}by[o.st].txt.push(o.txt);});
  return out.map(o=>({st:o.st,txt:o.txt.filter(Boolean).join("\n")}));}
function stIconSVG(o,x,y,w){return '<g pointer-events="all" style="cursor:help"><title>'+esc(o.txt||o.st)+'</title><rect x="'+x.toFixed(2)+'" y="'+y.toFixed(2)+'" width="'+(w*.92).toFixed(2)+'" height="'+(w*.92).toFixed(2)+'" fill="'+(SPR.eqTile||"#3a404c")+'"/>'+
  '<use href="#'+mapSprId("st:"+o.st)+'" x="'+x.toFixed(2)+'" y="'+y.toFixed(2)+'" width="'+(w*.92).toFixed(2)+'" height="'+(w*.92).toFixed(2)+'"/></g>';}
function plateStatus(sts,x0,sy,pad,si){return sts.map((o,i)=>stIconSVG(o,x0+pad+i*si,sy,si)).join("");}
function plateBox(cx,cy,R,x0,y0,w,h,lead,col,op){return (lead?'<line x1="'+cx.toFixed(1)+'" y1="'+cy.toFixed(1)+'" x2="'+Math.max(x0,Math.min(x0+w,cx)).toFixed(1)+'" y2="'+Math.max(y0,Math.min(y0+h,cy)).toFixed(1)+'" stroke="'+col+'" stroke-opacity=".7" stroke-width=".7"/>':'')+
    '<rect x="'+x0.toFixed(1)+'" y="'+y0.toFixed(1)+'" width="'+w.toFixed(1)+'" height="'+h.toFixed(1)+'" rx="'+(R*.12).toFixed(1)+'" fill="#111" fill-opacity=".85" stroke="'+col+'" stroke-opacity="'+op+'" stroke-width=".7"/>';}
function mapPlate(k,cx,cy,R){const {p,a}=cellArmy(k);if(!p||!a)return "";R=R*PLATE_K;const g=armyGear(a),ic=R*.56,pad=R*.1,f0=R*.24,si=R*.34*ST_K,
    title=a.label||"",sts=stDedup(armyStatus(p,a,k));
  if(!title&&!g.length&&!sts.length)return "";
  const th=title?f0+R*.06:0,gh=g.length?ic:0,w=Math.max(title.length*f0*.62,g.length*ic,sts.length*si)+pad*2,h=pad*2+th+gh+(sts.length?(gh?pad*.6:0)+si:0),
    pos=PLATE_AT?PLATE_AT(cx,cy,w,h):{x:cx+R*.72,y:cy-R*1.1,lead:false},x0=pos.x,y0=pos.y,gy=y0+pad+th,sy=gy+gh+(gh?pad*.6:0);
  return '<g pointer-events="none" font-family="ui-monospace,Consolas,\'DejaVu Sans Mono\',monospace">'+plateBox(cx,cy,R,x0,y0,w,h,pos.lead,p.color,".8")+
    (title?'<text x="'+(x0+pad).toFixed(1)+'" y="'+(y0+pad+f0*.85).toFixed(1)+'" font-size="'+f0.toFixed(2)+'" font-weight="700" fill="#f3d38a">'+esc(title)+'</text>':'')+
    g.map((n,i)=>'<rect x="'+(x0+pad+i*ic+ic*.03).toFixed(2)+'" y="'+gy.toFixed(2)+'" width="'+(ic*.94).toFixed(2)+'" height="'+(ic*.94).toFixed(2)+'" rx="'+(ic*.07).toFixed(2)+'" fill="'+(SPR.eqTile||"#3a404c")+'"/>'+
      '<use href="#'+mapSprId("eq:"+n)+'" x="'+(x0+pad+i*ic).toFixed(1)+'" y="'+gy.toFixed(1)+'" width="'+ic.toFixed(1)+'" height="'+ic.toFixed(1)+'"/>').join("")+
    plateStatus(sts,x0,sy,pad,si)+'</g>';}
// Settlement plate: name (if set), then status icons — Tax / Reach / Wards / Garrison live in the inspector (click the Settlement)
function settPlate(k,cx,cy,R){const {p,s}=cellSett(k);if(!p||!s)return "";R=R*PLATE_K;const pad=R*.1,f0=R*.24,si=R*.34*ST_K;
  const title=s.name?(s.capital?"★ ":"")+s.name:"",
    sts=stDedup(settStatus(p,s));
  if(!title&&!sts.length)return "";
  const th=title?f0+R*.06:0,w=Math.max(title.length*f0*.62,sts.length*si)+pad*2,h=pad*2+th+(sts.length?si:0),
    pos=PLATE_AT?PLATE_AT(cx,cy,w,h):{x:cx+R*.72,y:cy-R*1.1,lead:false},x0=pos.x,y0=pos.y,sy=y0+pad+th;
  return '<g pointer-events="none" font-family="ui-monospace,Consolas,\'DejaVu Sans Mono\',monospace">'+plateBox(cx,cy,R,x0,y0,w,h,pos.lead,p.color,".8")+
    (title?'<text x="'+(x0+pad).toFixed(1)+'" y="'+(y0+pad+f0*.85).toFixed(1)+'" font-size="'+f0.toFixed(2)+'" font-weight="700" fill="#f3d38a">'+esc(title)+'</text>':'')+
    plateStatus(sts,x0,sy,pad,si)+'</g>';}
// Armies inside a Settlement: up to 3 mini retinue banners in their owners' colours (+N), Garrison as a shield with its size
// the (single) Army inside a Settlement stands behind it, peeking out at the right, in its owner's colour
function settBehind(cell,k,cx,cy,R){if(cell.type==="Army")return "";const cs=cellSett(k);if(!cs.s)return "";const ins=armiesInside(cs.p,cs.s);if(!ins.length)return "";
  const {p,a}=ins[0],key="army:"+(a.retinue||BANDIT_DEFAULT_RETINUE);if(!SPR.S[key])return "";const w=R*1.2,h=w*15/16;
  return '<use href="#'+mapSprId(key)+'" x="'+(cx+R*.12).toFixed(1)+'" y="'+(cy+R*.5-h-R*.18).toFixed(1)+'" width="'+w.toFixed(1)+'" height="'+h.toFixed(1)+'" color="'+p.color+'" pointer-events="none"/>';}
// the first Army inside stands behind the Settlement (settBehind); any extra (flagged) shows in the tab
function settInsideMarks(cx,cy,R,pix,g,ins){if(pix&&SPR)ins=ins.slice(1);let s="";const w=R*.6,st=w*.72,sh=ins.slice(0,3),bw=sh.length*st+w*.28+(ins.length>3?R*.42:0),y0=cy+R*.6,x0=cx-bw/2+R*.06;
  if(pix&&SPR){
    if(sh.length)s+='<rect x="'+(x0-R*.06).toFixed(1)+'" y="'+(y0+w*.04).toFixed(1)+'" width="'+bw.toFixed(1)+'" height="'+(w*.98).toFixed(1)+'" rx="'+(R*.14).toFixed(1)+'" fill="#111" fill-opacity=".72" stroke="#f3d38a" stroke-opacity=".55" stroke-width=".5" pointer-events="none"/>';
    sh.forEach(({p,a},i)=>{const k="army:"+(a.retinue||BANDIT_DEFAULT_RETINUE);if(!SPR.S[k])return;
      s+='<use href="#'+mapSprId(k)+'" x="'+(x0+i*st).toFixed(1)+'" y="'+y0.toFixed(1)+'" width="'+w.toFixed(1)+'" height="'+w.toFixed(1)+'" color="'+p.color+'" pointer-events="none"/>';});
    if(ins.length>3)s+='<text x="'+(x0+3*st+w*.2).toFixed(1)+'" y="'+(y0+w*.75).toFixed(1)+'" font-size="7" font-weight="700" fill="#fff" pointer-events="none">+'+(ins.length-3)+'</text>';
    if(g&&SPR.S["eq:Kite Shield"]){const gw=R*.42,gx=cx+R*.42,gy=cy+R*.42;s+='<use href="#'+mapSprId("eq:Kite Shield")+'" x="'+gx.toFixed(1)+'" y="'+gy.toFixed(1)+'" width="'+gw.toFixed(1)+'" height="'+gw.toFixed(1)+'" pointer-events="none"/>'+
      '<text x="'+(gx+gw).toFixed(1)+'" y="'+(gy+gw*.85).toFixed(1)+'" font-size="7" font-weight="700" fill="#fff" stroke="#111" stroke-width=".35" pointer-events="none">'+g.count+'</text>';}
    return s;}
  const t=(g?"G"+g.count:"")+(ins.length?(g?" ":"")+"A"+ins.length:"");
  return t?'<text x="'+(cx-R*.95).toFixed(1)+'" y="'+(cy+R*.85).toFixed(1)+'" font-size="7.5" font-weight="700" fill="#fff" stroke="#111" stroke-width=".35" pointer-events="none">'+t+'</text>':"";}
let PLATE_AT=null;
// ---- map bar: Select, and a Place palette for setup pieces ----
const PLACE_TOOLS=["Army","Hamlet","Village","Town","City","Metropolis","Outlaw Country","Bandit Camp","Erase"];
let PLACE_OPEN=false;
function mapBarHTML(){const P=mapAsP(),ic=t=>t==="Army"?sprSVG("army:Levy",18,false,P.color):SETT_TIERS_MAP.includes(t)?sprSVG("map:"+t,18,false,P.color):t==="Bandit Camp"?sprSVG("map:camp",18,false):
    t==="Outlaw Country"?'<span class="olh"></span>':'✕';
  const pl=PLACE_OPEN||mtool!=="Select";
  return '<div class="mapbar"><button data-mt="Select" data-nav="1" class="'+(mtool==="Select"?"on":"")+'" title="click a piece to inspect it; click your Army, then a lit hex, to move">Select</button>'+
    '<button data-mplace="1" data-nav="1" class="'+(pl?"on":"")+'" title="place / erase map pieces (setup)">Place '+(pl?'▾':'▸')+'</button>'+
    (pl?'<span class="mpal">'+PLACE_TOOLS.map(t=>'<button data-mt="'+esc(t)+'" data-nav="1" title="'+esc(t)+'" class="'+(mtool===t?"on":"")+'">'+ic(t)+'<span>'+esc(t==="Outlaw Country"?"Outlaw":t==="Bandit Camp"?"Camp":t==="Metropolis"?"Metro":t)+'</span></button>').join("")+
      '<span class="note">as '+pTok(P,12)+' '+esc(P.name)+'</span></span>':'')+'</div>';}
const SETT_TIERS_MAP=["Hamlet","Village","Town","City","Metropolis"];
// ================= Inspect tool =================
let INSP=null;
// Territory: hex -> Set of player ids whose Reach covers it
function terrOwners(){const M=mapState(),g=M.grid;return g?reachOwners(M,g.width,g.height):{};}
// how player p relates to the Territory owners of hex k: Border Tension (not Alliance / NAP / household), Invasion (at War)
function terrFlags(p,k,own){own=own||terrOwners();const pid=String(p.id),out=[];
  (own[k]&&own[k].size===1?[...own[k]]:[]).forEach(o=>{if(o===pid)return;const x=effPair(pid,o);if(x.household)return;const q=pById(o);
    if(!(x.nap||sameAlliance(pid,o)))out.push({st:"tension",txt:"Border Tension → "+(q?q.name:"?")+" (Doubt +1)",to:o});
    if(x.war)out.push({st:"invasion",txt:"Invasion → "+(q?q.name:"?")+" (Doubt +1)",to:o});});return out;}
// Territory terms (GLOSSARY): Controlled = within Reach of a player's Settlement(s); Contested = Controlled by 2+ players; Uncontested = by one
// Bandit Camps (any size) on hexes p Controls (PO_MODIFIERS "Local Unrest": per active Bandit Camp in your Controlled Territory)
function unrestCamps(p,own){if(!p)return [];own=own||terrOwners();const M=mapState(),pid=String(p.id);return Object.keys(M.camps).filter(k=>+M.camps[k].n>0&&own[k]&&own[k].has(pid));}
// other players' Armies standing in p's Uncontested Territory (PO_MODIFIERS "Border Tension" / "Invasion")
function intrudersOf(p,own){if(!p)return [];own=own||terrOwners();const M=mapState(),pid=String(p.id),out=[];
  Object.keys(M.cells).forEach(k=>{const c=M.cells[k];if(c.type!=="Army"||c.player==null)return;const o=String(c.player);
    if(o===pid||!(own[k]&&own[k].size===1&&own[k].has(pid)))return;const x=effPair(pid,o);if(x.household)return;
    out.push({k,pid:o,ally:!!x.nap||sameAlliance(pid,o),war:!!x.war});});return out;}
function settReach(q,s){if(settUnbuilt(s))return 0;return (+((DATA.settlements||{})[s.tier]||{}).reach||0)+reachBonus(q).b;}
// one Settlement's own numbers, from the Holdings in it (settFx) + its Winter tax
function settEcon(p,s){return withBoard(p.board,()=>{const have=new Set(Object.keys(PC)),E=computeEarned(have),sea=curSeason();
  const occ=S.placed.filter(q=>String(q.sid)===String(s.id)),F=settFx(occ,have,E.craft,E.tc),a=F.acc;
  const seas=F.net.filter(o=>o.grp==="Seasonal"&&o.label==="Gold in "+sea).reduce((t,o)=>t+o.val,0);
  const hUp=occ.reduce((t,q)=>t+pursuitUpkeep(q),0),tax=settTax(S,s),pl=playerOfBoard(S),dest=((D.bandit||{}).dest||{})[(pl?pl.id:"")+":"+s.id]||null;
  const mons=occ.filter(q=>(R[q.name]||{}).type==="Monument").map(q=>({name:q.name,on:pActive(q)}));
  const gold=(a.gold||0)+seas,winter=sea==="Winter";
  return {gold:a.gold||0,seas,sea,hUp,upRed:a.upkeep||0,craft:a.craft||0,infl:a.influence||0,faith:a.faith||0,doubt:a.doubt||0,tax,dest,mons,occ:occ.length,
    net:gold-hUp+(winter&&!dest?tax:0),pillageBase:gold+(winter&&!dest?tax:0)};});}
// ---- Pillage (Prowess action): a.pillage={tp,sid}; Extort half the Settlement's holding & tax income each Empire Phase ----
function pillageCheck(p,a){const pl=a.pillage;if(!pl)return null;const q=pById(pl.tp),s=q&&settById(q,pl.sid);
  if(!q||!s)return "Settlement gone";if(!effPair(p.id,q.id).war)return "war ended";if(siegeOn(q.id,s.id))return "Settlement besieged";
  if(armySieging(p,a))return "Army laid Siege";const ak=armyHex(p,a),sk=settHex(q,s);
  if(!ak||!sk||hexDist(hk(ak),hk(sk))>settReach(q,s))return "Army left Reach";return "";}
function pillageTargets(p,a){const ak=armyHex(p,a);if(!ak)return [];const out=[];
  D.players.forEach(q=>{if(sameP(q,p)||!effPair(p.id,q.id).war)return;(q.board.settlements||[]).forEach(s=>{const sk=settHex(q,s);
    if(sk&&!siegeOn(q.id,s.id)&&hexDist(hk(ak),hk(sk))<=settReach(q,s))out.push({q,s});});});return out;}
function runPillage(){const out=[],seen=new Set();D.players.forEach(p=>(p.board.armies||[]).forEach(a=>{if(!a.pillage)return;
  const q=pById(a.pillage.tp),s=q&&settById(q,a.pillage.sid),nm=s?(s.name||s.tier):"?",why=pillageCheck(p,a);
  if(why){out.push(p.name+": Pillage of "+nm+" ends — "+why);delete a.pillage;return;}
  const key=q.id+":"+s.id;if(seen.has(key))return;seen.add(key);                       // a Settlement may be Pillaged once per Empire Phase
  const amt=Math.max(0,Math.floor(settEcon(q,s).pillageBase/2)),t=extortGold({b:q.board},{b:p.board},amt,"Pillage of "+nm);
  out.push(p.name+" pillages "+nm+" ("+q.name+"): extort "+t.toLocaleString()+(t<amt?" (of "+amt.toLocaleString()+")":""));}));return out;}
// ---- Army states (Inspect rows + plate icons) ----
function armyStatus(p,a,k){const L=[];if(!p||!a)return L;const cell=k?mapState().cells[k]:null,B=battle();
  {const im=immuneStrainIn(p,a);if(effStrained(p,a))L.push({st:"strained",txt:"Strained"+(!a.strained&&siegeStrains(p,a)?" (Besieged)":"")});else if(im)L.push({st:"endurance",txt:"Immune Strained ("+im+")"});}
  if(armyBlocked(p,a)||(cell&&cell.blocked))L.push({st:"blocked",txt:"Blocked"+(a.sackT?" (Sacking)":"")+(cell&&cell.blocked?" (Sabotage"+(cell.blockedT!=null?", until the end of turn "+(cell.blockedT+1):"")+")":"")});
  if(+a.fatigue>0)L.push({st:"fatigue",txt:"Fatigue ×"+a.fatigue+" (Morale +"+((BT.fatigueMorale??2)*a.fatigue)+")"});
  if(isRouted(a))L.push({st:"routed",txt:"Routed"});
  if(a.muster&&a.muster.n>0)L.push({st:"muster",txt:"Mustering · Muster Timer "+(a.muster.t||0)+" · "+a.muster.n+" to go"});
  const sg=armySieging(p,a);if(sg)L.push({st:"sieging",txt:(sg.kind==="capture"?"Capturing":"Laying Siege")+" · "+(sg.label||"")+" · "+(sg.n??"?")+" left"});
  if(armyBesieged(p,a))L.push({st:"besieged",txt:"Besieged"+(armyBesiegeExempt(p,a)?"":" · Blocked except Sally Forth")});
  if(B.id&&["A","B"].some(X=>B[X].kind!=="bandit"&&String(B[X].pid)===String(p.id)&&String(B[X].aid)===String(a.id)))L.push({st:"battle",txt:"In Battle"});
  if(a.pillage){const q=pById(a.pillage.tp),s2=q&&settById(q,a.pillage.sid);L.push({st:"pillage",txt:"Pillaging "+(s2?(s2.name||s2.tier):"?")+(q?" ("+q.name+")":"")});}
  if(k)terrFlags(p,k).forEach(f=>L.push(f));
  return L;}
// ---- map markers: crossed swords on the Battle, a trebuchet + timer on each besieged / captured Settlement ----
function mapMarkers(R,dx,dy,pix){if(!pix||!SPR)return "";let s="";const C=k=>{const [c,r]=hk(k);return [R+c*dx,dy/2+r*dy+(c%2?dy/2:0)];},M=mapState();
  const B=battle(),fights=(B.id?[{A:B.A,B:B.B,on:1}]:[]).concat(bq().filter(o=>o.id!==B.qid||!B.id).map(o=>({A:o.A,B:o.B,on:0})));
  fights.forEach(F=>{const at=[sideHex(F.A),sideHex(F.B)].filter(Boolean);if(!at.length)return;
    let pts_=at.map(C);if(pts_.length===2&&hexDist(hk(at[0]),hk(at[1]))<=1)pts_=[[(pts_[0][0]+pts_[1][0])/2,(pts_[0][1]+pts_[1][1])/2]];
    pts_.forEach(([x,y])=>{const w=R*1.15;s+='<use href="#'+mapSprId("mk:battle")+'" x="'+(x-w/2).toFixed(1)+'" y="'+(y-w/2-R*.15).toFixed(1)+'" width="'+w.toFixed(1)+'" height="'+w.toFixed(1)+'"'+(F.on?'':' opacity=".55"')+' pointer-events="none"/>';});});
  realmTimers().filter(t=>(t.kind==="siege"||t.kind==="capture")&&t.tp!=null&&t.sid!=null).forEach(t=>{const q=pById(t.tp),st=q&&settById(q,t.sid),k=st&&settHex(q,st);if(!k)return;
    const [x,y]=C(k),w=R*.95,x0=x-R*1.05,y0=y-R*.95;
    s+='<use href="#'+mapSprId("mk:siege")+'" x="'+x0.toFixed(1)+'" y="'+y0.toFixed(1)+'" width="'+w.toFixed(1)+'" height="'+w.toFixed(1)+'" pointer-events="none"/>'+
      '<text x="'+(x0+w*.1).toFixed(1)+'" y="'+(y0+w*.32).toFixed(1)+'" font-size="'+(R*.42).toFixed(1)+'" font-weight="700" fill="#f3d38a" stroke="#111" stroke-width=".4" pointer-events="none">'+(t.n??"")+'</text>';});
  return s;}
// ---- the panel ----
function inspHTML(){if(mtool!=="Select"||!INSP)return "";const M=mapState(),k=INSP,c=M.cells[k],cp=M.camps[k];
  let h="";if(c&&c.type==="Army")h=inspArmy(k);else if(c)h=inspSett(k);else if(cp)h=inspCamp(k);else{INSP=null;return "";}
  return '<div class="insp" id="inspPanel">'+h+'</div>';}
function inspHead(art,title,sub,p){const i=p?D.players.indexOf(p):-1;
  return '<div class="ih">'+art+'<div><b>'+esc(title)+'</b>'+(sub?'<div class="note">'+sub+'</div>':'')+'</div><span class="ix">'+
    (i>=0?'<button data-insp-board="'+i+'" data-nav="1" title="open this player\u2019s Empire view">empire ▸</button>':'')+'<button data-insp-x="1" data-nav="1" title="close">✕</button></span></div>';}
function inspCell(k,v,cls){return '<div'+(cls?' class="'+cls+'"':'')+'><span class="k">'+k+'</span>'+v+'</div>';}
function g$(n){n=Math.round(+n||0);return n===0?"0":(n>0?"+":"")+n.toLocaleString();}
function inspCan(pid){return !lockOn()||ADMIN||canHost()||(!!myClaimP()&&String(myClaimP().id)===String(pid));}
function inspArmy(k){const {p,a}=cellArmy(k),cell=mapState().cells[k];if(!p)return inspHead("","Army","unowned",null);
  if(!a)return inspHead(sprSVG("army:"+BANDIT_DEFAULT_RETINUE,36,false,p.color),"Army","Army — unlinked (link it under Map ↔ board)",p);
  const rt=EQ.retinues[a.retinue]||{},u=armyUFor(p),v=armyVals(a,u),m=boardMetrics(p.board),sp=speedOf(p,a,k);
  let h=inspHead(sprSVG("army:"+(a.retinue||BANDIT_DEFAULT_RETINUE),36,false,p.color),a.label||("Army "+a.id),pTok(p,12)+esc(p.name)+' · '+esc(a.retinue||"")+' ×'+(a.count||0)+'/'+(EQ.army_max||25),p);
  h+='<div class="ir">'+armyGear(a).map(n=>'<span title="'+esc(n)+'">'+eqSVG(n,22)+'</span>').join("")+'</div>';
  h+='<div class="ig">'+inspCell("STRIKE",v.toStrike+"+")+inspCell("INIT",(v.init>=0?"+":"")+v.init)+inspCell("SAVE",v.save+"+")+inspCell("MORALE",v.morale+"+",v.routed?"neg":"")+
    inspCell("AP",v.ap)+inspCell("SPEED",sp.speed)+inspCell("END",(a.endurance??0)+"/"+(rt.endurance??"—"))+inspCell("SIZE",a.count||0)+'</div>';
  const en=Math.max(0,a.endurance||0);h+='<div class="ir"><span class="k">Endurance</span>'+(en?(en<=8?stIcon("endurance",13).repeat(en):stIcon("endurance",13)+" ×"+en):'<span class="neg">0</span>')+'</div>';
  const S_=armyStatus(p,a,k);h+='<div class="sec">Status</div>'+(S_.length?S_.map(o=>'<div class="ist">'+stIcon(o.st,16)+'<span>'+esc(o.txt)+'</span></div>').join(""):'<div class="note">—</div>');
  const mods=u.mods||[];h+='<div class="sec">Effects</div>'+(mods.length?'<div class="ir">'+mods.map(md=>'<span class="kw mod" data-tok="'+esc(md.tok)+'" title="'+esc(gloss(md.tok)+" — "+(md.node||""))+'">'+esc(md.tok)+'</span>').join("")+'</div>':'<div class="note">—</div>');
  h+='<div class="sec">Gold</div><div class="ir"><span class="k">Upkeep</span><b class="neg">'+g$(-armyUpkeep(a))+'</b><span class="k">· all Armies net</span><b class="neg">'+g$(-m.netArmy)+'</b></div>'+
    '<div class="ir"><span class="k">Spoils of War (if defeated)</span><b>'+(+rt.cost||0).toLocaleString()+'</b></div>';
  {const x=armyInside(p,a);if(x)h=h.replace('<div class="ir">','<div class="ir"><span class="badge tier">inside '+esc(x.s.name||x.s.tier)+(sameP(x.q,p)?'':' ('+esc(x.q.name)+')')+'</span>');}
  {const sa=selArmy();if(sa&&sa.a===a)h+=movePanelHTML();else if(canMoveArmy(p))h+='<div class="ir"><button data-insp-sel="'+p.id+':'+a.id+'" data-nav="1">Move ▸</button>'+armyMusterBtn(p,a)+'</div>';}
  if(canMoveArmy(p)){const T=engageTargets(p,a);if(T.length)h+='<div class="sec">Engage</div>'+T.map((t,i)=>'<div class="ist">'+stIcon(t.kind==="siege"?"sieging":"battle",16)+'<span>'+esc(t.label)+'</span>'+
    '<button data-insp-eng="'+p.id+':'+a.id+':'+i+'" data-nav="1" style="margin-left:auto">'+(t.kind==="siege"?"Lay Siege ▸":"Battle ▸")+'</button></div>').join("");}
  if(!a.pillage){const T=pillageTargets(p,a);if(T.length&&inspCan(p.id))h+='<div class="ir"><span class="k">Pillage</span><select data-insp-pil="'+p.id+':'+a.id+'" data-nav="1"><option value="">—</option>'+
    T.map(o=>'<option value="'+o.q.id+':'+o.s.id+'">'+esc((o.s.name||o.s.tier)+" ("+o.q.name+")")+'</option>').join("")+'</select></div>';}
  else if(inspCan(p.id))h+='<div class="ir"><button data-insp-unpil="'+p.id+':'+a.id+'" data-nav="1">cancel Pillage</button></div>';
  return h;}
function settStatus(p,s){const st=[],B=D.bandit||{};
  if(s.bt>0)st.push({st:"muster",txt:s.up?"Upgrading → "+s.up.to+" · Build Timer "+s.bt:"Building · Build Timer "+s.bt});
  realmTimers().filter(t=>String(t.tp)===String(p.id)&&String(t.sid)===String(s.id)).forEach(t=>st.push({st:t.kind==="siege"||t.kind==="capture"?"besieged":"blocked",txt:(t.type||t.kind)+" · "+(t.label||"")+" · "+(t.n??"?")+" left"}));
  const d=(B.dest||{})[p.id+":"+s.id];if(d)st.push({st:"destabilize",txt:"Destabilize: next Winter this Settlement's tax goes to "+(d.by!=null?pname(d.by):"Bandit Camp @ "+d.camp)});
  if(s.capital&&(B.ic||{})[p.id]){const ic=B.ic[p.id];const who=ic.by!=null?pname(ic.by):"Bandit Camp @ "+ic.camp;st.push({st:"intercept",txt:"Intercept Caravan: the next turn "+p.name+" is Host, their Trade Income goes to "+who+((DATA.rulesConst||{}).INTERCEPT_EXTORT_PER_CRAFT?" (none: Extort "+DATA.rulesConst.INTERCEPT_EXTORT_PER_CRAFT+" × Craft)":"")+(sameP(hostP(),p)?" (this turn)":"")});}
  D.players.forEach(q=>(q.board.armies||[]).forEach(a=>{if(a.pillage&&String(a.pillage.tp)===String(p.id)&&String(a.pillage.sid)===String(s.id))st.push({st:"pillage",txt:"Pillaged by "+q.name+" ("+(a.label||"Army "+a.id)+")"});}));
  const dm=(p.board.placed||[]).filter(q=>String(q.sid)===String(s.id)&&q.dmg>0);if(dm.length)st.push({st:"damaged",txt:"Damaged: "+dm.map(q=>q.name+" ("+q.dmg+")").join(", ")});
  if(s.capital){const idm=Object.keys(p.board.idmg||{}).filter(n=>p.board.idmg[n]>0);if(idm.length)st.push({st:"damaged",txt:"Damaged Infrastructure: "+idm.join(", ")});}
  if(occupyTaxOnly(p.board)&&!settInside(p.board,s))st.push({st:"blocked",txt:"No Army inside — no tax, Holdings unusable ("+p.board.faction+")"});
  return st;}
function settStatusMarks(pl,k,cx,cy,R){const cs=cellSett(k).s;if(!pl||!cs)return "";
  const L=stDedup(settStatus(pl,cs).filter(o=>o.st!=="besieged"));if(!L.length)return "";
  const w=R*.4*ST_K,x0=cx+R*.55,y0=cy-R*.75-w;
  return L.slice(0,4).map((o,i)=>stIconSVG(o,x0+i*w,y0,w)).join("");}
function inspSett(k){const {p,s}=cellSett(k),cell=mapState().cells[k];if(!p)return inspHead(sprSVG("map:"+cell.type,36,false),cell.type,"unowned",null);
  if(!s)return inspHead(sprSVG("map:"+cell.type,36,false,p.color),cell.type,esc(p.name)+" · unlinked (link it under Map ↔ board)",p);
  const e=settEcon(p,s),wt=winterTax(p.board),wu=withBoard(p.board,()=>wardUse(s.id)),g=garrisonOf(p,s.id),ins=(p.board.armies||[]).filter(x=>String(x.sid)===String(s.id));
  let h=inspHead(sprSVG("map:"+s.tier,36,false,p.color),(s.capital?"★ ":"")+(s.name||s.tier),pTok(p,12)+esc(p.name)+' · '+esc(s.tier)+' · wards '+wu.used+'/'+wu.cap+' · Reach '+settReach(p,s),p);
  if(inspCan(p.id))h+='<div class="ir"><span class="k">Name</span><input data-insp-name="'+p.id+':'+s.id+'" data-nav="1" value="'+esc(s.name||"")+'" placeholder="'+esc(s.tier)+'" style="flex:1;min-width:0">'+
    (PN?'<button data-insp-rename="'+p.id+':'+s.id+'" data-nav="1" title="new name ('+esc(nameCulture(p.board)||"")+')">🎲</button>':'')+'</div>';
  h+=settActionsHTML(p,s);
  h+='<div class="ig">'+inspCell("GOLD",g$(e.gold),e.gold<0?"neg":"pos")+inspCell(esc(e.sea.toUpperCase()),g$(e.seas))+inspCell("HLDG UPKEEP",g$(-e.hUp),"neg")+inspCell("NET",g$(e.net),e.net<0?"neg":"pos")+
    inspCell("TAX",e.tax.toLocaleString())+inspCell("CRAFT",e.craft)+inspCell("ARMY UPK −",Math.abs(e.upRed||0).toLocaleString(),e.upRed?"pos":"")+inspCell(esc(SCORE.toUpperCase()),g$(e.infl))+'</div>';
  h+='<div class="ir"><span class="k">Faith / Doubt</span><b>'+e.faith+' / '+e.doubt+'</b><span class="k">· Holdings</span><b>'+e.occ+'</b></div>';
  const tm=wt.src.filter(x=>x);h+='<div class="ir"><span class="k">Winter tax</span><b>'+e.tax.toLocaleString()+'</b>'+(tm.length?'<span class="note">'+esc(tm.join(" · "))+'</span>':'')+'</div>';
  if(e.mons.length)h+='<div class="sec">Monuments</div>'+e.mons.map(o=>{const sk=(SPR.key||{})[o.name];return '<div class="ist">'+(sk?sprSVG(sk,22,false):"")+'<span'+(o.on?'':' class="note"')+'>'+esc(o.name)+(o.on?'':' (inactive)')+'</span></div>';}).join("");
  const st=settStatus(p,s);
  h+='<div class="sec">Status</div>'+(st.length?st.map(o=>'<div class="ist">'+stIcon(o.st,16)+'<span>'+esc(o.txt)+'</span></div>').join(""):'<div class="note">—</div>');
  {const ai=armiesInside(p,s);h+='<div class="sec">Forces</div><div class="ir"><span class="k">Garrison</span><b>'+(g?g.count:0)+'</b></div>'+
    ai.map(({p:q,a:x})=>'<div class="ist">'+sprSVG("army:"+(x.retinue||BANDIT_DEFAULT_RETINUE),22,false,q.color)+'<span>'+esc(x.label||("Army "+x.id))+' · '+esc(x.retinue||"")+' ×'+(x.count||0)+(sameP(q,p)?'':' ('+esc(q.name)+')')+'</span>'+
      (canMoveArmy(q)?'<button data-insp-sel="'+q.id+':'+x.id+'" data-nav="1" style="margin-left:auto">move out ▸</button>':'')+'</div>').join("")+
    (ai.length?'':'<div class="note">no Armies inside</div>');
    {const sa=selArmy();if(sa&&ai.some(o=>o.a===sa.a))h+=movePanelHTML();}}
  realmTimers().filter(t=>t.kind==="siege"&&String(t.tp)===String(p.id)&&String(t.sid)===String(s.id)&&t.by!=null&&t.aid!=null).forEach(t=>{const bp=pById(t.by);if(!bp)return;
    const def=armiesInside(p,s)[0],gs=garrisonOf(p,s.id),dSide=def?{pid:String(def.p.id),aid:String(def.a.id)}:gs?{pid:String(p.id),aid:"g:"+s.id}:null,att={pid:String(bp.id),aid:String(t.aid)};
    if(!dSide)return;const noSally=srcHas(bp.board,"no_sally_forth"),btn=(lbl,o,pid)=>(inspCan(pid)?'<button data-insp-sf="'+esc(JSON.stringify(o))+'" data-nav="1" style="margin-left:auto">'+lbl+'</button>':'');
    h+='<div class="sec">Siege</div><div class="ist">'+stIcon("besieged",16)+'<span>'+esc(bp.name)+' · Siege Timer '+(t.n??"?")+'</span></div>'+
      (def?'<div class="ist">'+stIcon("battle",16)+'<span>Sally Forth (no action)</span>'+(noSally?'<span class="note" style="margin-left:auto">'+esc(bp.name)+" · Artillery Park: blocked"+'</span>':btn("Sally Forth ▸",{kind:"sally",A:dSide,B:att,seize:"",src:"Sally Forth"},def.p.id))+'</div>':'')+
      (+t.n<=0?'<div class="ist">'+stIcon("sieging",16)+'<span>Siege resolves: Battle</span>'+btn("Siege Battle ▸",{kind:"siege",A:att,B:dSide,seize:"",src:"Siege resolution"},bp.id)+'</div>':'');});
  if(!e.dest){const can=D.players.filter(q=>!sameP(q,p)&&inspCan(q.id));if(can.length)h+='<div class="ir"><span class="k">Destabilize (next Winter)</span><select data-insp-dest="'+p.id+':'+s.id+'" data-nav="1"><option value="">—</option>'+can.map(q=>'<option value="'+q.id+'">'+esc(q.name)+'</option>').join("")+'</select></div>';}
  else if(e.dest.by!=null&&inspCan(e.dest.by))h+='<div class="ir"><button data-insp-undest="'+p.id+':'+s.id+'" data-nav="1">cancel Destabilize</button></div>';
  return h;}
// ---- map-first actions: a Settlement card offers Build / Improve / Expand / Repair / Settle; an Army card Move / Muster / Lay Siege / Pillage.
// When the player has a Passed or Endorsed Envoy waiting whose actions include it, the action is Performed with that Envoy
// (cost, outcome and riders as on the Table); otherwise it is placed by hand (no cost).
function envoyFor(p,action){if(!p)return null;const R=tSim();
  return R.envoys.find(E=>sameP(E.owner,p)&&(E.out==="Passed"||E.out==="Endorsed")&&resolveOpen(R,E)&&canAct(p)&&pfActs(E).includes(action)&&
    (()=>{const rec=((tCur(p).perform)||{})[E.id];return !rec||rec.edit;})())||null;}
function settActionsHTML(p,s){if(!inspCan(p.id)||settUnbuilt(s))return "";
  const sid=s.id,opt=(L)=>L.map(x=>'<option value="'+esc(x.v)+'">'+esc(x.label)+'</option>').join("");
  const build=withBoard(p.board,()=>buildOpts(p).filter(x=>x.v!=="hand"&&!x.dis&&canPlace(x.v.slice(2),sid).ok));
  const imp=improveOpts(p).filter(x=>x.v!=="hand"),exp=expandOpts(p).filter(x=>x.v!=="hand"&&x.v.slice(2)===String(sid));
  const rep=repairOpts(p).filter(x=>x.v[0]==="i"?!!s.capital:(p.board.placed||[]).some(q=>String(q.id)===x.v.slice(2)&&String(q.sid)===String(sid)));
  const row=(act,L)=>{const E=envoyFor(p,act);return '<div class="ia-r"><span class="ia-l">'+act+'</span>'+(L.length?'<select data-ia="'+act+'" data-nav="1">'+opt(L)+'</select>'+
      '<button data-do="mapact" data-act="'+act+'" data-who="'+p.id+'" data-sid="'+sid+'" data-env="'+(E?esc(E.id):"")+'" data-nav="1">'+(E?'Perform ▸':'by hand ▸')+'</button>'+(E?'<span class="note">'+esc(E.dom)+' Envoy</span>':''):'<span class="note">nothing eligible</span>')+'</div>';};
  const ch=envoyFor(p,"Settle");
  return '<div class="sec">Actions</div><div class="ia">'+row("Build",build)+row("Improve",imp)+row("Expand",exp)+row("Repair",rep)+
    '<div class="ia-r"><span class="ia-l">Settle</span><button data-do="mapact" data-act="Settle" data-who="'+p.id+'" data-sid="'+sid+'" data-env="'+(ch?esc(ch.id):"")+'" data-nav="1">'+(ch?'Perform ▸':'by hand ▸')+'</button>'+
      '<span class="note">then place the Village on the map</span></div></div>';}
function armyMusterBtn(p,a){if(!inspCan(p.id))return "";const E=envoyFor(p,"Muster"),room=Math.max(0,(EQ.army_max||25)-(a.count||0));if(!room||(a.muster&&a.muster.n>0))return "";
  return '<button data-do="mapact" data-act="Muster" data-who="'+p.id+'" data-aid="'+a.id+'" data-env="'+(E?esc(E.id):"")+'" data-nav="1">Muster'+(E?' (Envoy) ▸':' ▸')+'</button>';}
DO.mapact=el=>{const p=pById(el.dataset.who),act=el.dataset.act;if(!p)return;
  const sel=el.parentElement.querySelector("[data-ia]"),sub=act==="Muster"?"r:"+el.dataset.aid:sel?sel.value:"";
  if(el.dataset.env){const c=tCurW(p);c.perform=c.perform||{};c.perform[el.dataset.env]={action:act,target:"",sub,place:act==="Build"?String(el.dataset.sid):"",ts:tnow()};
    if(act==="Settle")mtool="Village";save();D.view="table";render();flash(p.name+": "+act+" performed with the "+el.dataset.env.split(":")[2]+" Envoy");return;}
  const log=[],ctx={o:p,q:null,sub,log:x=>log.push(x),flag:x=>log.push("⚑ "+x),pend:()=>{},E:null,out:"Passed"};
  if(act==="Build"){const n=sub.slice(2),r=withBoard(p.board,()=>placeHolding(n,+el.dataset.sid,+el.dataset.sid));log.push(p.name+" builds "+n+(r.np.bt>0?" · Build Timer "+r.np.bt:""));}
  else if(act==="Improve")runImprove(ctx);else if(act==="Expand")runExpand(ctx);else if(act==="Repair")runRepair(ctx);else if(act==="Muster")runMuster(ctx);
  else if(act==="Settle"){runSettle(ctx);mtool="Village";PLACE_OPEN=true;}
  save();render();flash(log.join(" · ")||act);};
function inspCamp(k){const cp=mapState().camps[k],thr=BAN.armyThreshold||25,army=cp.n>=thr,cv=banditDomain(cp.n),sb=domBand(cv),inf=STAND_INF[sb]||1,mod=+cp.cmod||0,own=terrOwners()[k];
  let h=inspHead(sprSVG(army?"map:bandit_army":"map:camp",36,false),army?"Bandit Army":"Bandit Camp","@ "+k+" · Retinues "+cp.n+(army?"":" / "+thr+" to become an Army"),null);
  h+='<div class="ig">'+inspCell("TREASURY",(cp.gold||0).toLocaleString())+inspCell("PROWESS","+"+cv)+inspCell("CUNNING",cv)+inspCell(esc(SCORE.toUpperCase()),inf+mod)+'</div>';
  h+='<div class="ir"><span class="k">Cunning Standing</span><b>'+sb+'</b>'+(mod?'<span class="note">mod '+g$(mod)+'</span>':'')+'</div>';
  h+='<div class="ir"><span class="k">Armed ('+esc(currentEra())+')</span><span>'+esc(((BAN.equipment||{})[currentEra()])||"—")+'</span></div>';
  const st=[];if(+cp.n>0)(own?[...own]:[]).forEach(o=>st.push({st:"unrest",txt:"Local Unrest → "+pname(o)+" (Doubt +1)"}));
  const B=battle();if(B.id&&["A","B"].some(X=>B[X].kind==="bandit"&&B[X].camp===k))st.push({st:"battle",txt:"In Battle"});
  h+='<div class="sec">Status</div>'+(st.length?st.map(o=>'<div class="ist">'+stIcon(o.st,16)+'<span>'+esc(o.txt)+'</span></div>').join(""):'<div class="note">—</div>');
  if(cp.last)h+='<div class="note">last: '+esc(cp.last)+'</div>';
  h+='<div class="sec">Gold</div><div class="ir"><span class="k">Destroyed: Extort its Treasury</span><b>'+(cp.gold||0).toLocaleString()+'</b></div>';
  return h;}
// adjacent targets for an Army on the map: at-war Armies (not in a Settlement), Bandit Camps / Armies, at-war Settlements not under Siege
function engageTargets(p,a){const k=armyHex(p,a);if(!k||armyInside(p,a))return [];const M=mapState(),out=[];
  hexNb(k).forEach(n=>{const c=M.cells[n];
    if(c&&c.type==="Army"){const x=cellArmy(n);if(x.p&&x.a&&!sameP(x.p,p)&&effPair(p.id,x.p.id).war)out.push({kind:"battle",label:x.p.name+" · "+(x.a.label||("Army "+x.a.id)),B:{pid:String(x.p.id),aid:String(x.a.id)},seize:"A",src:"Battle action"});}
    else if(c){const cs=cellSett(n);if(cs.s&&!sameP(cs.p,p)&&effPair(p.id,cs.p.id).war&&!siegeOn(cs.p.id,cs.s.id))out.push({kind:"siege",label:cs.p.name+" · "+(cs.s.name||cs.s.tier),tp:cs.p.id,sid:cs.s.id});}
    if(M.camps[n])out.push({kind:"battle",label:(M.camps[n].n>=(BAN.armyThreshold||25)?"Bandit Army":"Bandit Camp")+" @ "+n,B:{kind:"bandit",camp:n},seize:"",src:"vs Bandits"});});
  return out;}
function wireInsp(host){const P=host.querySelector("#inspPanel");if(!P)return;
  P.querySelectorAll("[data-insp-eng]").forEach(b=>b.onclick=()=>{const [pid,aid,i]=b.dataset.inspEng.split(":"),p=pById(pid),a=p&&(p.board.armies||[]).find(x=>String(x.id)===aid);
    if(!a||!canMoveArmy(p))return;const t=engageTargets(p,a)[+i];if(!t)return;
    if(t.kind==="siege"){const sg=siegeState();sg.mode="Lay Siege";sg.tp=String(t.tp);sg.sid=t.sid;sg.by=String(p.id);sg.aid=String(a.id);
      if(mods().battle){D.view="battle";flash("Siege calculator filled: "+t.label);}else flash("Siege calculator is in the Battle tab (modules ▸ Battle tab)");save();render();return;}
    bqStart({kind:"battle",A:{pid:String(p.id),aid:String(a.id)},B:t.B,seize:t.seize,src:t.src});});
  P.querySelectorAll("[data-insp-sf]").forEach(b=>b.onclick=()=>{const o=JSON.parse(b.dataset.inspSf),besieger=o.kind==="sally"&&o.B&&pById(o.B.pid);
    if(besieger&&srcHas(besieger.board,"no_sally_forth")){flash(besieger.name+"'s Artillery Park prevents Sally Forth");return;}bqStart(o);});
  P.querySelectorAll("[data-insp-rename]").forEach(b=>b.onclick=()=>{const [pid,sid]=b.dataset.inspRename.split(":"),q=pById(pid),st=q&&settById(q,sid);if(!st)return;
    const nm=genPlaceName(nameCulture(q.board));if(nm){st.name=nm;save();render();}});
  P.querySelectorAll("[data-insp-name]").forEach(inp=>inp.onchange=()=>{const [pid,sid]=inp.dataset.inspName.split(":"),q=pById(pid),st=q&&settById(q,sid);
    if(!st||!inspCan(pid))return;const v=inp.value.trim();if(v)st.name=v;else delete st.name;save();render();});
  P.querySelectorAll("[data-insp-sel]").forEach(b=>b.onclick=()=>{const [pid,aid]=b.dataset.inspSel.split(":");SEL={pid,aid};render();});
  P.querySelectorAll("[data-insp-x]").forEach(b=>b.onclick=()=>{INSP=null;render();});
  P.querySelectorAll("[data-insp-board]").forEach(b=>b.onclick=()=>{D.active=+b.dataset.inspBoard;reindex();D.view="board";save();render();if(typeof renderList==="function")renderList();});
  P.querySelectorAll("[data-insp-dest]").forEach(sel=>sel.onchange=()=>{if(!sel.value)return;const [pid,sid]=sel.dataset.inspDest.split(":");if(!inspCan(sel.value)){flash("🔒 not your Destabilize");render();return;}
    BST().dest[pid+":"+sid]={by:sel.value};save();render();});
  P.querySelectorAll("[data-insp-undest]").forEach(b=>b.onclick=()=>{const key=b.dataset.inspUndest;delete BST().dest[key];save();render();});
  P.querySelectorAll("[data-insp-pil]").forEach(sel=>sel.onchange=()=>{if(!sel.value)return;const [pid,aid]=sel.dataset.inspPil.split(":"),[tp,sid]=sel.value.split(":"),q=pById(pid);
    if(!inspCan(pid)){flash("🔒 not your Army");render();return;}const a=q&&(q.board.armies||[]).find(x=>String(x.id)===aid);if(a){a.pillage={tp,sid};save();render();}});
  P.querySelectorAll("[data-insp-unpil]").forEach(b=>b.onclick=()=>{const [pid,aid]=b.dataset.inspUnpil.split(":"),q=pById(pid),a=q&&(q.board.armies||[]).find(x=>String(x.id)===aid);if(a){delete a.pillage;save();render();}});}
// The map is two layers. Base: terrain, glyphs, coast and the shared <defs> — rebuilt only when the map itself (grid,
// palette) changes. Overlay: Reach, Outlaw Country, resource badges, move range, pieces, markers, plates — every render.
// The Realm keeps the <svg> and swaps only the overlay (renderRealmMap); mapSVG() still returns the whole picture.
let MAP_BASE=null;
function mapLayers(M){
  const V=decodeGrid(M.grid),g=M.grid,cols=g?g.width:(M.cols||16),rows=g?g.height:(M.rows||12);
  const R=15,dx=1.5*R,dy=Math.sqrt(3)*R,W=cols*dx+R*2,H=rows*dy+dy,PAL=mapPal(g);
  const pts=(cx,cy)=>{let a=[];for(let k=0;k<6;k++){const t=Math.PI/180*60*k;a.push((cx+R*Math.cos(t)).toFixed(1)+","+(cy+R*Math.sin(t)).toFixed(1));}return a.join(" ");};
  const lighten=(hex,k)=>{const n=parseInt(hex.slice(1),16),f=v=>Math.min(255,Math.round(v*k));
    return "#"+[f(n>>16&255),f(n>>8&255),f(n&255)].map(v=>v.toString(16).padStart(2,"0")).join("");};
  const XY=k=>{const [c,r]=hk(k);return [R+c*dx,dy/2+r*dy+(c%2?dy/2:0)];};
  const letter={Army:"A",Hamlet:"Ha",Village:"V",Town:"T",City:"C",Metropolis:"M"};
  const z=MAPZ.fit?MAPZ.fitScale(W):MAPZ.z;
  const sc=R/54,gw=(120*sc).toFixed(2),gh=(108*sc).toFixed(2);
  const pix=!!SPR,pu=R*1.6/16;   // pixel map + sprites in every theme
  const key=[V.sig,JSON.stringify(PAL),pix?1:0,cols,rows,(g&&g.seed)||M.seed||"",M.showRes!==false?1:0].join("|");
  if(!MAP_BASE||MAP_BASE.key!==key){
    let defs='<pattern id="rch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><line x1="0" y1="0" x2="0" y2="5" stroke="#000" stroke-opacity=".28" stroke-width="1.2"/></pattern>'+
      '<pattern id="olh" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3" height="6" fill="rgba(120,20,20,.45)"/></pattern>';
    if(RS)Object.keys(RS.glyphs).forEach(gk=>{if(RS.glyphs[gk])defs+='<symbol id="tg-'+gk+'" viewBox="0 0 120 108"><g stroke-width="'+RS.glyph_w+'" stroke-linecap="round" stroke-linejoin="round">'+
      RS.glyphs[gk].replace(/stroke="SHADE"/g,'style="stroke:var(--shade)"').replace(/stroke="HILITE"/g,'style="stroke:var(--hilite)"')
        .replace(/fill="SHADE"/g,'style="fill:var(--shade)"').replace(/fill="DEEP"/g,'style="fill:var(--deep)"')+'</g></symbol>';});
    if(pix)defs+=mapSprDefs()+'<pattern id="pxd" width="'+(4*pu).toFixed(2)+'" height="'+(4*pu).toFixed(2)+'" patternUnits="userSpaceOnUse"><rect width="'+pu.toFixed(2)+'" height="'+pu.toFixed(2)+'" fill="#000" fill-opacity=".09"/></pattern>';
    let base='',glyphs='',coast='';
    for(let c=0;c<cols;c++)for(let r=0;r<rows;r++){
      const k=c+","+r,cx=R+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0),h=V.hex[k];
      let fill=h?PAL[h.t]:"var(--chip)";if(h&&h.hill)fill=lighten(fill,1.16);
      if(h&&RS){const gk=h.hill?'hill':h.t;
        if(pix&&SCAT[gk])glyphs+=mapScatter(gk,k,cx,cy,R,fill,String((g&&g.seed)||M.seed||""),h.res&&M.showRes!==false?[26*sc,-24*sc,17*sc+pu]:null);
        else if(RS.glyphs[gk]&&!(pix&&(gk==="plains"||gk==="water")))glyphs+='<use href="#tg-'+gk+'" x="'+(cx-60*sc).toFixed(2)+'" y="'+(cy-54*sc).toFixed(2)+'" width="'+gw+'" height="'+gh+'" fill="'+fill+'" color="'+tTone(fill)+'" opacity="'+RS.glyph_opacity+'" '+
          'style="--shade:'+tLighten(fill,RS.shade_k)+';--hilite:'+tLighten(fill,RS.hilite_k)+';--deep:'+tLighten(fill,RS.deep_k)+'" pointer-events="none"/>';
        if(h.t!=="water")[[0,-1],[0,1],[1,c%2?0:-1],[1,c%2?1:0],[-1,c%2?0:-1],[-1,c%2?1:0]].forEach(([oc,orr])=>{
          const nk=(c+oc)+","+(r+orr),n=V.hex[nk];if(!n||n.t!=="water")return;
          const nx=R+(c+oc)*dx,ny=dy/2+(r+orr)*dy+((c+oc)%2?dy/2:0),ang=Math.atan2(ny-cy,nx-cx)*180/Math.PI;
          const e=((Math.round((ang-30)/60)%6)+6)%6,v=t=>[cx+R*Math.cos(Math.PI/3*t),cy+R*Math.sin(Math.PI/3*t)];
          const a=v(e),b=v(e+1);coast+='M'+a[0].toFixed(1)+' '+a[1].toFixed(1)+'L'+b[0].toFixed(1)+' '+b[1].toFixed(1);});}
      base+='<polygon data-cell="'+k+'" points="'+pts(cx,cy)+'" fill="'+fill+'" stroke="#00000030" stroke-width="1" style="cursor:pointer"><title>'+k+(h?" · "+(RULE_NAME[h.t]||h.t)+(h.hill?" (Hill)":"")+(h.res?" · "+h.res:"")+(h.reg!=null?" · region "+h.reg:""):"")+'</title></polygon>';
      if(pix&&h)base+='<polygon points="'+pts(cx,cy)+'" fill="url(#pxd)" pointer-events="none"/>';}
    base+=glyphs;
    if(coast)base+='<path d="'+coast+'" fill="none" stroke="'+(RS?RS.ink:"#2b241b")+'" stroke-width="'+((RS?RS.coast_w:4.2)*sc).toFixed(2)+'" stroke-linecap="round" pointer-events="none"/>';
    MAP_BASE={key,defs,base};}
  // ---- overlay ----
  let s='',over='';
  Object.keys(V.hex).forEach(k=>{const h=V.hex[k],[cx,cy]=XY(k);
    if(M.outlaw[k])over+='<polygon points="'+pts(cx,cy)+'" fill="url(#olh)" stroke="#7a1414" stroke-width="1.5" pointer-events="none"/>';
    if(h&&h.res&&M.showRes!==false){const bx=cx+26*sc,by=cy-24*sc;   // badge top-right, as renown-maps / print
      over+='<circle cx="'+bx.toFixed(1)+'" cy="'+by.toFixed(1)+'" r="'+(17*sc).toFixed(2)+'" fill="#e9ddc2" stroke="#2b241b" stroke-width="0.6" pointer-events="none"/>'+
        '<circle cx="'+bx.toFixed(1)+'" cy="'+by.toFixed(1)+'" r="'+(10*sc).toFixed(2)+'" fill="'+RCOL[h.res]+'" stroke="#0006" stroke-width="0.5" pointer-events="none"/>';}});
  Object.keys(M.outlaw).forEach(k=>{if(V.hex[k])return;const [cx,cy]=XY(k);over+='<polygon points="'+pts(cx,cy)+'" fill="url(#olh)" stroke="#7a1414" stroke-width="1.5" pointer-events="none"/>';});
  if(M.showReach!==false){
    const own=reachOwners(M,cols,rows),colOf=id=>{const p=D.players.find(pp=>String(pp.id)===id);return p?p.color:"#888";};
    const sig=k=>own[k]?[...own[k]].sort().join("|"):"";let tint="",edge="";
    Object.keys(own).forEach(k=>{const [c,r]=k.split(",").map(Number),cx=R+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0),ids=[...own[k]];
      ids.forEach(id=>{tint+='<polygon points="'+pts(cx,cy)+'" fill="'+colOf(id)+'" fill-opacity="'+(ids.length>1?0.12:0.2)+'"/>';});
      if(ids.length>1)tint+='<polygon points="'+pts(cx,cy)+'" fill="url(#rch)"><title>'+k+' · Contested</title></polygon>';
      const ec=ids.length>1?"#444":colOf(ids[0]),me=sig(k),ri=R*0.9,v=t=>[cx+ri*Math.cos(Math.PI/3*t),cy+ri*Math.sin(Math.PI/3*t)];
      [[0,-1],[0,1],[1,c%2?0:-1],[1,c%2?1:0],[-1,c%2?0:-1],[-1,c%2?1:0]].forEach(([oc,orr])=>{
        const nc=c+oc,nr=r+orr,nk=nc+","+nr;if(sig(nk)===me)return;
        const nx=R+nc*dx,ny=dy/2+nr*dy+(nc%2?dy/2:0),ang=Math.atan2(ny-cy,nx-cx)*180/Math.PI,e=((Math.round((ang-30)/60)%6)+6)%6,a=v(e),b=v(e+1);
        edge+='<path d="M'+a[0].toFixed(1)+' '+a[1].toFixed(1)+'L'+b[0].toFixed(1)+' '+b[1].toFixed(1)+'" stroke="'+ec+'"/>';});});
    s+='<g pointer-events="none">'+tint+'</g><g fill="none" stroke-width="2" stroke-opacity=".8" stroke-linecap="round" pointer-events="none">'+edge+'</g>';
  }
  s+=over;
  if(mtool==="Select")s+=moveOverlay(R,dx,dy,pts);
  if(g&&M.showStarts)(g.settlements||[]).forEach(reg=>reg.forEach(st=>{const cx=R+st[0]*dx,cy=dy/2+st[1]*dy+(st[0]%2?dy/2:0),w=R*.42;
    s+='<rect x="'+(cx-w).toFixed(1)+'" y="'+(cy-w).toFixed(1)+'" width="'+(w*2).toFixed(1)+'" height="'+(w*2).toFixed(1)+'" fill="none" stroke="#b3392f" stroke-width="1.6" stroke-dasharray="3 2" pointer-events="none"/>';}));
  let hits='';
  Object.keys(M.cells).forEach(k=>{const cell=M.cells[k],[c,r]=k.split(",").map(Number),cx=R+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0);
    const pl=D.players.find(pp=>pp.id===cell.player),col=pl?pl.color:"#888";
    const unl=pl&&!(cell.type==="Army"?cellArmy(k).a:cellSett(k).s);
    const sk=cell.type==="Army"?"army:"+(((cellArmy(k).a||{}).retinue)||BANDIT_DEFAULT_RETINUE):"map:"+cell.type;
    s+=(pix&&SPR.S[sk]?settBehind(cell,k,cx,cy,R)+mapSpr(sk,cx,cy,R,col,unl)+(cell.type!=="Army"&&pl?mapBanner(pl,cx,cy,R):'')+(cell.blocked?'<text x="'+(cx-R*.98).toFixed(1)+'" y="'+(cy-R*.5).toFixed(1)+'" font-size="9" font-weight="700" fill="#fff" stroke="#111" stroke-width=".4" pointer-events="none">⊘</text>':''):
       '<circle cx="'+cx.toFixed(1)+'" cy="'+cy.toFixed(1)+'" r="'+(R*.62).toFixed(1)+'" fill="'+col+'" stroke="'+(unl?'#b3392f':'#111')+'"'+(unl?' stroke-width="2" stroke-dasharray="3 2"':'')+' pointer-events="none"/>'+
       '<text x="'+cx.toFixed(1)+'" y="'+(cy+4).toFixed(1)+'" text-anchor="middle" font-size="10" font-weight="700" fill="#fff" pointer-events="none">'+(letter[cell.type]||"?")+(cell.blocked?"⊘":"")+'</text>')+
       (()=>{if(cell.type==="Army"||!pl)return "";const cs=cellSett(k).s;if(!cs)return "";const g=garrisonOf(pl,cs.id),ins=armiesInside(pl,cs);return settInsideMarks(cx,cy,R,pix,g,ins)+(pix&&SPR&&M.showSPlates===false?settStatusMarks(pl,k,cx,cy,R):"");})()+
       (()=>{if(cell.type!=="Army")return "";const ca=cellArmy(k).a;return ca&&ca.muster&&ca.muster.n>0?'<text x="'+(cx+R*.55).toFixed(1)+'" y="'+(cy-R*.45).toFixed(1)+'" font-size="8" font-weight="700" fill="#f3d38a" stroke="#111" stroke-width=".4" pointer-events="none">M'+(ca.muster.t||0)+'</text>':"";})()+
       (()=>{if(cell.type!=="Army")return "";const ca=cellArmy(k).a;return ca&&+ca.count>0?'<text x="'+(cx+R*.8).toFixed(1)+'" y="'+(cy+R*.8).toFixed(1)+'" text-anchor="end" font-size="8" font-weight="700" fill="#fff" stroke="#111" stroke-width=".4" pointer-events="none">'+ca.count+'</text>':"";})();
    // the piece's hover title (the terrain polygon underneath only knows the terrain)
    hits+='<polygon data-cell="'+k+'" points="'+pts(cx,cy)+'" fill="#000" fill-opacity="0" style="cursor:pointer"><title>'+k+' · '+esc(cellTitle(k))+(cell.blocked?' · Blocked (Sabotage)'+(cell.blockedT!=null?' until the end of turn '+(cell.blockedT+1):' — re-place or erase the Army to clear'):'')+'</title></polygon>';});
  s+=mapMarkers(R,dx,dy,pix);
  if(mtool==="Select"&&INSP){const [c,r]=hk(INSP),cx=R+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0);s+='<polygon points="'+pts(cx,cy)+'" fill="none" stroke="#f3d38a" stroke-width="3" pointer-events="none"/>';}
  let plates="";if(pix&&(M.showPlates!==false||M.showSPlates!==false)){
    // every piece's sprite box is an obstacle; each plate takes the first spot around its Army that clears sprites and earlier plates
    const obs=[];
    Object.keys(M.cells).concat(Object.keys(M.camps)).forEach(k=>{const [x,y]=XY(k);obs.push([x-R*.82,y-R*.9,x+R*.82,y+R*.9]);});
    const ov=(a,b)=>Math.max(0,Math.min(a[2],b[2])-Math.max(a[0],b[0]))*Math.max(0,Math.min(a[3],b[3])-Math.max(a[1],b[1]));
    // corner-aligned spots first, on the side facing the nearer map edge (horizontal, then vertical); centred spots last
    PLATE_AT=(cx,cy,w,h)=>{const g=R*.08,ex=cx<W/2?-1:1,ey=cy<H/2?-1:1,side=sx=>sx>0?cx+R*.85:cx-R*.85-w,lvl=sy=>sy<0?cy-h-R*.1:cy+R*.1,
        C=[[side(ex),lvl(ey)],[side(ex),lvl(-ey)],[side(-ex),lvl(ey)],[side(-ex),lvl(-ey)],[cx-w/2,ey<0?cy-R*.95-h:cy+R*.95],[cx-w/2,ey<0?cy+R*.95:cy-R*.95-h],
        [side(ex),cy-h/2],[side(-ex),cy-h/2]];
      [1.9,2.9].forEach(m=>{[[ex,ey],[ex,-ey],[-ex,ey],[-ex,-ey],[0,ey],[0,-ey]].forEach(([sx,sy])=>C.push([cx+sx*R*m*.9-(sx<0?w:sx===0?w/2:0),cy+sy*R*m*.6-(sy<0?h:0)]));});
      let best=null;C.forEach(([x,y],i)=>{x=Math.max(1,Math.min(W-w-1,x));y=Math.max(1,Math.min(H-h-1,y));const b=[x-g,y-g,x+w+g,y+h+g],o=obs.reduce((t,q)=>t+ov(b,q),0);
        if(!best||o<best.o-1e-6)best={x,y,o,lead:i>=8};});obs.push([best.x,best.y,best.x+w,best.y+h]);return best;};
    Object.keys(M.cells).sort().forEach(k=>{const isA=M.cells[k].type==="Army";if(isA?M.showPlates===false:M.showSPlates===false)return;const [x,y]=XY(k);plates+=isA?mapPlate(k,x,y,R):settPlate(k,x,y,R);});PLATE_AT=null;}
  Object.keys(M.camps).forEach(k=>{const cp=M.camps[k],[c,r]=k.split(",").map(Number),cx=R+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0),army=cp.n>=(BAN.armyThreshold||25);
    const ck=army?"map:bandit_army":"map:camp";
    s+=pix&&SPR.S[ck]?mapSpr(ck,cx,cy,R,null,false)+'<text x="'+(cx+R*.8).toFixed(1)+'" y="'+(cy+R*.8).toFixed(1)+'" text-anchor="end" font-size="8" font-weight="700" fill="#f3d38a" stroke="#111" stroke-width=".4" pointer-events="none">'+cp.n+'</text>':
       '<rect x="'+(cx-R*.62).toFixed(1)+'" y="'+(cy-R*.5).toFixed(1)+'" width="'+(R*1.24).toFixed(1)+'" height="'+(R).toFixed(1)+'" fill="'+(army?"#5a0d0d":"#1b1b1b")+'" stroke="#e0b060" pointer-events="none"/>'+
       '<text x="'+cx.toFixed(1)+'" y="'+(cy+3.5).toFixed(1)+'" text-anchor="middle" font-size="9" font-weight="700" fill="#f3d38a" pointer-events="none">☠'+cp.n+'</text>';});
  return {key,W,H,z,defs:MAP_BASE.defs,base:MAP_BASE.base,over:s+plates+hits};
}
function mapSVG(M){const L=mapLayers(M);
  return '<svg width="'+(L.W*L.z).toFixed(0)+'" height="'+(L.H*L.z).toFixed(0)+'" viewBox="0 0 '+L.W.toFixed(0)+' '+L.H.toFixed(0)+'" style="display:block"><defs>'+L.defs+'</defs>'+L.base+L.over+'</svg>';}
function outlawReport(M){
  const V=decodeGrid(M.grid),by={},warn=[];
  const cen=(M.grid&&M.grid.centers)||[];
  Object.keys(M.outlaw).forEach(k=>{const h=V.hex[k],a=k.split(",").map(Number);
    let rg=h&&h.reg!=null?h.reg:null;
    if(rg===null&&cen.length){let bd=1e9;cen.forEach((c,i)=>{const d=hexDist(a,c);if(d<bd){bd=d;rg=i;}});}
    rg=rg===null?"?":rg;by[rg]=(by[rg]||0)+1;
    Object.keys(M.cells).forEach(sk=>{const cell=M.cells[sk];if(cell.type==="Army")return;
      const b=sk.split(",").map(Number);if(BAN.outlawBuffer&&hexDist(a,b)<BAN.outlawBuffer)warn.push(k+" is within "+BAN.outlawBuffer+" of "+cell.type+" "+sk);});});
  return {by,warn};
}
function banditDomain(n){return Math.floor(n/5)*2;}
function banditAutoHTML(full){const B=BST();
  let h='<label class="note" style="display:flex;gap:6px;align-items:center"><input type="checkbox" class="bAuto"'+(B.auto!==false?' checked':'')+'> auto Bandit Mechanics at Empire Phase</label>';
  if(full)h+=full;
  const pend=[].concat(Object.keys(B.dest).map(k=>{const [pid,sid]=k.split(":"),p=D.players.find(q=>String(q.id)===pid);const st=p&&(p.board.settlements||[]).find(x=>String(x.id)===sid);return 'Destabilize: '+(p?esc(p.name):'?')+' '+esc(st?(st.name||st.tier):'#'+sid)+' (next Winter)';}),
    Object.keys(B.ic).map(pid=>'Intercept Caravan: '+esc(pname(pid))+' (next turn as Host)'),B.foster.map(x=>'Foster Rebellion: '+esc(pname(x.pid))+' (next Bandit Mechanics)'));
  if(pend.length)h+='<div class="note" style="margin-top:4px"><b>Pending</b><br>'+pend.join('<br>')+'</div>';
  if(B.log.length)h+='<details style="margin-top:4px"><summary class="note">Bandit log ('+B.log.length+')</summary><div class="note">'+B.log.slice(0,80).map(esc).join('<br>')+'</div></details>';
  return h;}
// Map ↔ board links: settlements by tier, armies by id (explicit link, else the owner's only one)
function armyName(a){return (a.label||("Army "+a.id))+' — '+(a.retinue||'')+' ×'+(a.count||0);}
// a map piece keeps the board piece it is linked to (sid / aid); a Settlement's map tier follows its board tier
function syncMapTiers(){const M=mapState();let ch=false;
  Object.keys(M.cells).forEach(k=>{const c=M.cells[k],cp=cellPlayer(c);if(!cp||(lockOn()&&!mine(cp)))return;   // each device keeps its own pieces in step
    if(c.type==="Army"){const a=cellArmy(k).a;if(a&&c.aid==null){c.aid=a.id;ch=true;}return;}
    const s=cellSett(k).s;if(!s)return;if(c.sid==null){c.sid=s.id;ch=true;}if(!s.name){nameSett(cp,s);if(s.name)ch=true;}
    if(c.type!==s.tier&&(DATA.settlements||{})[s.tier]){c.type=s.tier;ch=true;}});
  return ch;}
function mapLinkBad(){return mapSetts().filter(x=>cellPlayer(x.cell)&&!cellSett(x.k).s).length+mapArmies().filter(x=>cellPlayer(x.cell)&&!cellArmy(x.k).a).length;}
function mapLinksHTML(){const SL=mapSetts().filter(x=>cellPlayer(x.cell)),AL=mapArmies().filter(x=>cellPlayer(x.cell));
  if(!SL.length&&!AL.length)return '<div class="note">No settlements or armies on the map.</div>';
  const bad=mapLinkBad();
  let h=bad?'<div class="note"><b style="color:var(--upkeep)">'+bad+' unlinked</b></div>':'';
  if(SL.length)h+='<div class="note" style="margin-top:4px"><b>Settlements</b></div>'+SL.map(x=>{const p=cellPlayer(x.cell),cs=cellSett(x.k),opts=(p.board.settlements||[]).filter(q=>q.tier===x.cell.type);
      return '<div class="note">'+esc(p.name)+' '+esc(x.cell.type)+' @ '+x.k+' → '+(opts.length>1||x.cell.sid!=null?'<select class="bLink" data-k="'+x.k+'"><option value="">—</option>'+
        opts.map(q=>'<option value="'+q.id+'"'+(cs.s&&cs.s.id===q.id?' selected':'')+'>'+esc(q.name||q.tier)+' #'+q.id+'</option>').join('')+'</select>':(cs.s?esc(cs.s.name||cs.s.tier):'<b style="color:var(--upkeep)">no '+esc(x.cell.type)+' on board</b>'))+'</div>';}).join('');
  if(AL.length)h+='<div class="note" style="margin-top:4px"><b>Armies</b></div>'+AL.map(x=>{const p=cellPlayer(x.cell),ca=cellArmy(x.k),opts=p.board.armies||[];
      return '<div class="note">'+esc(p.name)+' Army @ '+x.k+(x.cell.blocked?' ⊘':'')+' → '+(opts.length>1||x.cell.aid!=null?'<select class="aLink" data-k="'+x.k+'"><option value="">—</option>'+
        opts.map(a=>'<option value="'+a.id+'"'+(ca.a&&ca.a.id===a.id?' selected':'')+'>'+esc(armyName(a))+'</option>').join('')+'</select>':(ca.a?esc(armyName(ca.a)):'<b style="color:var(--upkeep)">no Army on board</b>'))+'</div>';}).join('');
  return h;}
function wireBanditAuto(host){host.querySelectorAll(".bAuto").forEach(c=>c.onchange=()=>{BST().auto=c.checked;save();render();});
  host.querySelectorAll(".bLink").forEach(sl=>sl.onchange=()=>{const cell=mapState().cells[sl.dataset.k];if(!cell)return;if(sl.value)cell.sid=+sl.value;else delete cell.sid;save();render();});
  host.querySelectorAll(".aLink").forEach(sl=>sl.onchange=()=>{const cell=mapState().cells[sl.dataset.k];if(!cell)return;if(sl.value)cell.aid=+sl.value;else delete cell.aid;save();render();});
  host.querySelectorAll(".bAuto").forEach(c=>{if(c.onchange)c.onchange=guarded("bandit",c.onchange);});
  host.querySelectorAll(".bLink,.aLink").forEach(c=>{if(c.onchange)c.onchange=guarded("view",c.onchange);});}
// ---- Bandit automation: Host's Bandit Mechanics step, run as the new turn's Empire Phase opens (End turn) when switched on ----
function banditAuto(){return BST().auto!==false;}   // on unless switched off
function BST(){D.bandit=D.bandit||{};const b=D.bandit;b.dest=b.dest||{};b.ic=b.ic||{};b.foster=b.foster||[];b.log=b.log||[];return b;}
function bLog(m,k){const b=BST(),t=b._t||tTurn();b.log.unshift("T"+t+" "+curSeason()+" · "+m);b.log=b.log.slice(0,80);
  const ok=k&&hk(k).every(Number.isFinite)?outlawOwner(k):null;b.slog=(b.slog||[]).concat([{t,pid:ok?String(ok.id):null,m}]).slice(-200);}
function hk(k){return k.split(",").map(Number);}
function mapSetts(){const M=mapState();return Object.keys(M.cells).filter(k=>M.cells[k].type&&M.cells[k].type!=="Army").map(k=>({k,cell:M.cells[k]}));}
function cellPlayer(cell){return D.players.find(p=>String(p.id)===String(cell.player))||null;}
// map settlement → board settlement: explicit link, else the owner's only settlement of that tier
function cellSett(k){const cell=mapState().cells[k];if(!cell)return {p:null,s:null};const p=cellPlayer(cell);if(!p)return {p:null,s:null};
  const ss=p.board.settlements||[];if(cell.sid!=null){const s=ss.find(x=>String(x.id)===String(cell.sid));if(s)return {p,s};}
  const c=ss.filter(x=>x.tier===cell.type);return {p,s:c.length===1?c[0]:null};}
function mapArmies(){const M=mapState();return Object.keys(M.cells).filter(k=>M.cells[k].type==="Army").map(k=>({k,cell:M.cells[k]}));}
function cellArmy(k){const cell=mapState().cells[k];if(!cell||cell.type!=="Army")return {p:null,a:null};const p=cellPlayer(cell);if(!p)return {p:null,a:null};
  const as=p.board.armies||[];if(cell.aid!=null){const a=as.find(x=>String(x.id)===String(cell.aid));if(a)return {p,a};}
  return {p,a:as.length===1?as[0]:null};}
function cellTitle(k){const cell=mapState().cells[k];if(!cell)return "";const p=cellPlayer(cell);
  const nm=cell.type==="Army"?(cellArmy(k).a?armyName(cellArmy(k).a):"Army — unlinked"):(cellSett(k).s?(cellSett(k).s.name||cellSett(k).s.tier):cell.type+" — unlinked");
  const ca=cell.type==="Army"?cellArmy(k):null,ast=ca&&ca.a?[...new Set(armyStatus(ca.p,ca.a,k).map(o=>o.txt))]:[];
  return (p?p.name+" ":"")+nm+(ca&&ca.a?" · "+armyGear(ca.a).join(", "):"")+(ast.length?" · "+ast.join(" · "):"")+(cell.blocked?" · Blocked":"");}
function byDist(k,list,randomTies){const a=hk(k);return list.map((x,i)=>({x,d:hexDist(a,hk(x.k)),r:randomTies?Math.random():i})).sort((u,v)=>u.d-v.d||u.r-v.r).map(o=>o.x);}
// Outlaw Country: M.outlaw[k] = true (placed by a player at Deploy) or "w<n>" (placed by the Host at Setup, Wild zone n).
// After Setup every zone works the same: a zone is a player's Outlaw Country while any of its Territories is within their
// Province. A Deploy zone in nobody's Province (placement in progress) falls back to its nearest Settlement's owner.
function isWild(k){return typeof mapState().outlaw[k]==="string";}
function wildZones(){const M=mapState(),z={};Object.keys(M.outlaw).forEach(k=>{const v=M.outlaw[k];if(typeof v==="string")(z[v]=z[v]||[]).push(k);});return z;}
// every zone: Wild zones by id, Deploy zones as connected groups ("o<n>")
function outlawZones(){const M=mapState(),z=wildZones(),seen=new Set();let n=0;
  Object.keys(M.outlaw).filter(k=>M.outlaw[k]===true).forEach(k0=>{if(seen.has(k0))return;const L=[],Q=[k0];seen.add(k0);
    while(Q.length){const k=Q.pop();L.push(k);hexNb(k).forEach(q=>{if(M.outlaw[q]===true&&!seen.has(q)){seen.add(q);Q.push(q);}});}
    z["o"+(++n)]=L;});
  return z;}
function zoneOf(k){const Z=outlawZones();return Object.keys(Z).find(z=>Z[z].includes(k))||null;}
function zoneOwners(hexes,own){own=own||terrOwners();const ids=new Set();hexes.forEach(k=>(own[k]||[]).forEach(id=>ids.add(String(id))));
  let L=D.players.filter(q=>ids.has(String(q.id)));
  if(!L.length&&hexes.length&&hexes.every(k=>mapState().outlaw[k]===true)){const N=byDist(hexes[0],mapSetts(),false);if(N.length&&cellPlayer(N[0].cell))L=[cellPlayer(N[0].cell)];}
  return L;}
// owners of the zone holding hex k (nearest Settlement's owner first)
function outlawOwners(k){const z=zoneOf(k);if(!z)return [];const L=zoneOwners(outlawZones()[z]);if(L.length<2)return L;
  const N=byDist(k,mapSetts(),false).map(x=>cellPlayer(x.cell));return L.slice().sort((a,b)=>N.findIndex(q=>sameP(q,a))-N.findIndex(q=>sameP(q,b)));}
function outlawOwner(k){return outlawOwners(k)[0]||null;}
// a player's Outlaw Country: every Territory of every zone that is theirs
function outlawOf(p){const Z=outlawZones(),own=terrOwners(),out=[];Object.values(Z).forEach(hx=>{if(zoneOwners(hx,own).some(q=>sameP(q,p)))out.push(...hx);});return out;}
// a camp is Wild while it sits on a Wild Territory or was spawned in one (Bandit Armies keep the tag when they move)
function campWild(k){const M=mapState(),cp=M.camps[k];return (cp&&cp.wild)||(isWild(k)?M.outlaw[k]:null);}
// zones to place: "formula" = floor(players / per_players) + plus; "fill" = as many as the ranges allow (null = no fixed count)
function wildCount(){const W=BAN.wild||{};if(W.count==="fill")return null;return Math.floor((D.players||[]).length/(+W.per_players||2))+(+(W.plus??1));}
function wildDone(){const M=mapState(),n=Object.keys(wildZones()).length,c=wildCount();return c==null?!!M.wildSeeded:n>=c;}
// Setup (last step, after Deploy): scatter Wild zones over the unclaimed board. Every Wild hex is land (no Water / Mountains /
// Impassable), free, at least Range border_range from every player's Province (Settlement Reach) and at least Range spacing from
// every other Outlaw Country zone. Seeds go nearest the middle of the map first (random ties), so zones sit in the contested centre
// and the spacing pushes later ones outward; each seed grows compactly round itself to OUTLAW_COUNTRY_START connected Territories
// under the same ranges. Stops when no seed fits (or max / formula count).
function placeWildOutlaw(){const M=mapState();if(!M.grid)return 0;const V=decodeGrid(M.grid),W=BAN.wild||{},size=+BAN.outlawStart||3;
  const bR=+(W.border_range??3),sp=+(W.spacing??5),cnt=wildCount(),cap=cnt!=null?cnt-Object.keys(wildZones()).length:(W.max!=null?+W.max-Object.keys(wildZones()).length:1e9);
  if(cap<=0){M.wildSeeded=true;return 0;}
  const own=terrOwners(),prov=Object.keys(own).filter(k=>own[k]&&own[k].size).map(hk);
  const land=k=>{const h=V.hex[k];return !!h&&h.t!=="water"&&h.t!=="mountain"&&!terrBlocked(h.t)&&hexFree(k)&&!M.outlaw[k];};
  const dProv={};Object.keys(V.hex).forEach(k=>{const a=hk(k);let d=1e9;for(const q of prov){const x=hexDist(a,q);if(x<d)d=x;if(d===0)break;}dProv[k]=d;});
  const dZone=(k,skipZ)=>{const a=hk(k);let d=1e9;Object.keys(M.outlaw).forEach(x=>{if(!M.outlaw[x]||(skipZ&&M.outlaw[x]===skipZ))return;d=Math.min(d,hexDist(a,hk(x)));});return d;};
  const fits=(k,z)=>land(k)&&dProv[k]>=bR&&dZone(k,z)>=sp;
  const ctr=[Math.floor((M.grid.width-1)/2),Math.floor((M.grid.height-1)/2)],dC=k=>hexDist(hk(k),ctr);
  let made=0;const tried=new Set();
  while(made<cap){let id=1;while(Object.values(M.outlaw).includes("w"+id))id++;const z="w"+id;
    const seeds=Object.keys(V.hex).filter(k=>!tried.has(k)&&fits(k,null)).map(k=>({k,o:dC(k),r:Math.random()})).sort((x,y)=>x.o-y.o||x.r-y.r);
    if(!seeds.length)break;
    let ok=false;
    for(const sd of seeds){tried.add(sd.k);const zone=[sd.k];M.outlaw[sd.k]=z;
      while(zone.length<size){const cand=new Set();zone.forEach(k=>hexNb(k).forEach(q=>{if(fits(q,z))cand.add(q);}));
        const L=[...cand].map(q=>({q,o:hexDist(hk(q),hk(sd.k)),r:Math.random()})).sort((x,y)=>x.o-y.o||x.r-y.r);if(!L.length)break;M.outlaw[L[0].q]=z;zone.push(L[0].q);}
      if(zone.length>=size){ok=true;bLog("Wild Outlaw Country "+z+" placed @ "+zone.join(" "));break;}
      zone.forEach(k=>delete M.outlaw[k]);}
    if(!ok)break;made++;}
  M.wildSeeded=true;return made;}
// Host redo: clear the Wild zones that hold no Bandit Camp, then scatter again
function rescatterWild(){const M=mapState();Object.entries(wildZones()).forEach(([z,hx])=>{if(hx.some(k=>M.camps[k]))return;hx.forEach(k=>delete M.outlaw[k]);});
  M.wildSeeded=false;return placeWildOutlaw();}
// a piece's Presence (PRESENCE_RANGE, one flat range for Settlements and Armies), the range at which a Bandit Camp can target it
function pieceAura(k){const c=mapState().cells[k];if(!c)return 0;if(c.type==="Army"){return presR();}
  const s=cellSett(k).s;return s&&settUnbuilt(s)?0:presR();}
// BANDIT_CAMP_REACH: "province" = the camp sits in the target's owner's Province (any of that player's pieces);
// null = within the target piece's Presence; N = within Range N of the camp
function campInRange(ck,tk,own){const c=BAN.campReach;
  if(c==="province"){const p=cellPlayer(mapState().cells[tk]);own=own||terrOwners();return !!p&&!!own[ck]&&own[ck].has(String(p.id));}
  const r=c!=null?+c:pieceAura(tk);return hexDist(hk(ck),hk(tk))<=r;}
function hexFree(k){const M=mapState();return !M.camps[k]&&!M.cells[k];}
function spawnCamp(p,n,why){const M=mapState(),free=outlawOf(p).filter(hexFree);if(!free.length)return null;
  const k=free[Math.floor(Math.random()*free.length)];M.camps[k]={n,gold:+BAN.campGold||0};if(isWild(k))M.camps[k].wild=M.outlaw[k];armBandits(M.camps[k]);bLog("camp of "+n+" spawns @ "+k+" ("+why+")",k);return k;}
function growCamps(keys,why){const M=mapState(),gr=(BAN.growth||{})[currentEra()]||0,cap=BAN.armyThreshold||25;
  keys.forEach(k=>{const cp=M.camps[k];if(!cp)return;const n0=cp.n;cp.n=Math.min(cap,cp.n+gr);
    if(n0<cap&&cp.n>=cap){bLog("camp @ "+k+" reaches "+cap+" → Bandit Army",k);const ns=byDist(k,mapSetts(),false)[0],q=ns&&cellSett(ns.k);
      chron("bandit_army",{near:q&&q.s?(q.s.name||q.s.tier)+(q.p?" ("+q.p.name+")":""):k});}});if(keys.length)bLog("grow +"+gr+" ×"+keys.length+(why?" ("+why+")":""));}
function expandOutlaw(p){const M=mapState(),V=decodeGrid(M.grid),own=outlawOf(p),cand=new Set();
  own.forEach(k=>{const a=hk(k);Object.keys(V.hex).forEach(q=>{if(!M.outlaw[q]&&hexFree(q)&&V.hex[q].t!=="water"&&hexDist(a,hk(q))===1)cand.add(q);});});
  const L=[...cand];if(!L.length)return null;const k=L[Math.floor(Math.random()*L.length)];M.outlaw[k]=true;bLog(p.name+"'s Outlaw Country expands to "+k);return k;}
function immuneUprising(p){return withBoard(p.board,()=>Object.keys(PC).some(n=>!!hitOf("h:"+n,"immune_uprising")));}
function banditTargetMods(p,action){if(!p)return {v:0,src:[]};const src=[];let v=0;
  boardFx(p).forEach(f=>{if((f.k==="bandit")||(f.k==="defend"&&!f.players&&f.action&&f.action.toLowerCase()===action.toLowerCase())){v+=f.val*(f.q||1);src.push(f.src+" "+sgn(f.val*(f.q||1)));}});return {v,src};}
function cunningAction(roll){const t=(BAN.cunningTable||[]).find(r=>roll>=r[0]&&roll<=r[1]);return t?t[2]:null;}
function endorsedExtort(action){const m=String(((DATA.actions||{})[action]||{}).endorsed||"").match(/Extort\s*(\d+)/i);return m?+m[1]:0;}
function banditAct(k){const M=mapState(),cp=M.camps[k],B=BST(),F=BAN.faces||10,roll=1+Math.floor(Math.random()*F),act=cunningAction(roll);
  cp.roll=roll;if(!act){bLog("camp @ "+k+" rolls "+roll+" → no action",k);return;}
  // targets: pieces of the players whose Province covers the camp (BANDIT_CAMP_REACH); Smuggler's Nook-style carve-out:
  // camps in that player's Outlaw Country skip them and pick another player at random, at any range
  const NK=outlawOwners(k).filter(q=>srcHas(q.board,"bandit_redirect")),nook=NK.length>0,
    TO=terrOwners(),okT=t=>{const p=cellPlayer(mapState().cells[t]);return !!p&&(nook?!NK.some(q=>sameP(q,p)):campInRange(k,t,TO));};
  let L=byDist(k,mapSetts(),true).filter(x=>okT(x.k));if(nook)L=L.map(x=>({x,r:Math.random()})).sort((a,b)=>a.r-b.r).map(o=>o.x);
  let tgt=null;
  if(act==="Raze")tgt=L.map(x=>Object.assign({k:x.k},cellSett(x.k))).find(t=>t.s&&t.p.board.placed.some(q=>q.sid===t.s.id&&!(q.bt>0)&&!(q.dmg>0)));
  else if(act==="Destabilize")tgt=L.map(x=>Object.assign({k:x.k},cellSett(x.k))).find(t=>t.s&&!B.dest[t.p.id+":"+t.s.id]);
  else if(act==="Intercept Caravan")tgt=L.map(x=>Object.assign({k:x.k},cellSett(x.k))).find(t=>t.p&&!B.ic[t.p.id]);
  else if(act==="Sabotage"){const M_=mapState(),arm=Object.keys(M_.cells).filter(q=>M_.cells[q].type==="Army"&&cellPlayer(M_.cells[q])&&!M_.cells[q].blocked).map(q=>({k:q,cell:M_.cells[q]}));
    const AL=byDist(k,arm,true).filter(x=>okT(x.k)),A=nook?AL[Math.floor(Math.random()*AL.length)]:AL[0];tgt=A?{k:A.k,p:cellPlayer(A.cell),s:null,army:true,a:cellArmy(A.k).a}:null;}   // closest Army in range
  else tgt=L.length?Object.assign({k:L[0].k},cellSett(L[0].k)):null;
  if(!tgt||!tgt.p){bLog("camp @ "+k+" rolls "+roll+" → "+act+": no valid target in range"+(campWild(k)?" (Wild)":""),k);return;}
  const rk=[];D.players.forEach(q=>srcMatch(q.board,"bandit_cunning_auth").forEach(x=>{rk.push({v:+x.m[1],src:x.n+" ("+q.name+")"});}));
  const base=STAND_INF[domBand(banditDomain(cp.n))]||1,tm=banditTargetMods(tgt.p,act);tm.v+=rk.reduce((a,x)=>a+x.v,0);rk.forEach(x=>tm.src.push(x.src+" "+sgn(x.v)));
  const net=base+(+cp.cmod||0)+tm.v,oc=envoyOutcome(net);
  const head="camp @ "+k+" rolls "+roll+" → "+act+" vs "+tgt.p.name+(tgt.s?" ("+(tgt.s.name||tgt.s.tier)+")":tgt.army?" ("+(tgt.a?(tgt.a.label||"Army "+tgt.a.id):"Army")+" @ "+tgt.k+")":"")+" · Influence "+base+((+cp.cmod)?" "+sgn(+cp.cmod):"")+(tm.src.length?" "+tm.src.join(" "):"")+" = "+net+" → "+oc;
  cp.last=head;if(oc!=="Passed"&&oc!=="Endorsed"){bLog(head,k);return;}
  let fx="";
  if(act==="Raze"){const pool=tgt.p.board.placed.filter(q=>q.sid===tgt.s.id&&!(q.bt>0)&&!(q.dmg>0)),q=pool[Math.floor(Math.random()*pool.length)],rt=((DATA.timers||{})["Repair Timer"]||{}).default||2;
    q.dmg=rt;delete q.rep;fx=q.name+" Damaged (inactive until Repaired)";}
  else if(act==="Destabilize"){B.dest[tgt.p.id+":"+tgt.s.id]={camp:k};fx="next Winter: "+(tgt.s.name||tgt.s.tier)+"'s tax → camp";}
  else if(act==="Intercept Caravan"){B.ic[tgt.p.id]={camp:k};fx="next turn "+tgt.p.name+" is Host: trade income → camp";}
  else if(act==="Sabotage"){mapState().cells[tgt.k].blocked=true;mapState().cells[tgt.k].blockedT=tTurn();fx=tgt.p.name+"'s "+(tgt.a?(tgt.a.label||"Army "+tgt.a.id):"Army")+" @ "+tgt.k+" gains Blocked";}
  else if(act==="Foster Rebellion"){B.foster.push({pid:String(tgt.p.id)});fx="next Bandit Mechanics: 10-Retinue camp in "+tgt.p.name+"'s Outlaw Country";}
  if(oc==="Endorsed"){const x=endorsedExtort(act),b=tgt.p.board,t=Math.min(x,Math.max(0,b.treasury||0));tGold(b,-t,"Extorted by Bandits (Endorsed "+act+")");cp.gold=(cp.gold||0)+t;fx+=" · Endorsed: Extort "+t;
    if(t){const own=terrOwners()[k];D.players.forEach(h=>{if(!own||!own.has(String(h.id)))return;srcMatch(h.board,"syndicate_camp_extort").forEach(y=>{const take=Math.min(Math.floor(t/2),Math.max(0,+cp.gold||0));if(take){cp.gold-=take;tGold(h.board,take,"Syndicate Hub: half of Bandit Extort");fx+=" · "+h.name+" Syndicate Hub takes "+take+" from camp";}});});}}
  bLog(head+": "+fx,k);}
function runBanditMechanics(){const M=mapState(),B=BST(),sea=curSeason(),keys=Object.keys(M.camps),queued=B.foster.slice();
  const W=BAN.wild||{};
  if(sea==="Spring"){growCamps(keys.filter(k=>W.spring_growth!==false||!campWild(k)),"Spring");
    // Spring: one camp in each Outlaw Country zone (a full zone's camps grow instead)
    Object.entries(outlawZones()).forEach(([z,hx])=>{if(z[0]==="w"&&W.spring_spawn===false)return;const free=hx.filter(hexFree),ow=zoneOwners(hx),nm=ow.length?ow.map(q=>q.name).join(" / ")+"'s":"unclaimed";
      if(free.length){const k=free[Math.floor(Math.random()*free.length)];M.camps[k]={n:BAN.campStart||5,gold:+BAN.campGold||0};if(isWild(k))M.camps[k].wild=M.outlaw[k];armBandits(M.camps[k]);bLog("camp of "+M.camps[k].n+" spawns @ "+k+" ("+nm+" Outlaw Country, Spring)",k);}
      else{bLog(nm+" Outlaw Country ("+hx[0]+") is full");growCamps(hx.filter(k=>M.camps[k]),"no room to spawn");}});
    return;}
  growCamps(keys,"");
  keys.forEach(k=>{const cp=M.camps[k];if(cp&&cp.n>=(BAN.cunningMin||10))banditAct(k);});
  B.foster=B.foster.filter(x=>!queued.includes(x));
  queued.forEach(x=>{const p=D.players.find(q=>String(q.id)===x.pid);if(!p)return;
    const fn=+x.n||10;if(!spawnCamp(p,fn,"Foster Rebellion")){if(expandOutlaw(p))spawnCamp(p,fn,"Foster Rebellion");else bLog("Foster Rebellion: no room for "+p.name);}});
  D.players.forEach(p=>{if((p.board.po||0)>PO_MIN||immuneUprising(p)||poImmune(p.board))return;const n=Math.max(1,poNum(PO_MIN))*(poDoubled()[(POB(PO_MIN)||[])[0]]?2:1);
    for(let i=0;i<n;i++){if(!spawnCamp(p,BAN.campStart||5,"Uprising "+(i+1)+"/"+n)){
      bLog(p.name+"'s Outlaw Country is full (Uprising)");growCamps(Object.keys(M.camps).filter(k=>outlawOf(p).includes(k)),"Uprising, no room");break;}}});
  banditMoves();}
// ---- Bandit Army Move (BANDIT_BEHAVIOR "Army Behavior"), after the mechanics: Skirmish (a player Army in range) >
// Lay Siege (a player Settlement in range) > March toward the closest Army or Settlement. Ties: random (the Host may redo it).
function banditSpeed(cp){armBandits(cp);const a=banditArmy(cp),base=+((EQ.retinues[a.retinue||BANDIT_DEFAULT_RETINUE]||{}).speed)||0;
  const sm=/All Armies gain Speed\s*([+\-\u2212])\s?(\d+)/i.exec((SEAS[curSeason()]||{}).effect||"");return Math.max(0,base+(sm?(sm[1]==="+"?1:-1)*(+sm[2]):0));}
function banditAuraList(){const M=mapState(),RT=EQ.retinues||{},out=[],hexes=Object.keys(decodeGrid(M.grid).hex);
  Object.keys(M.cells).forEach(k=>{const c=M.cells[k];if(!cellPlayer(c))return;let r=0;
    if(c.type==="Army")r=presR();
    else{const s=cellSett(k).s;r=s&&settUnbuilt(s)?0:presR();}
    if(r>0)out.push({k,set:new Set(hexes.filter(h=>hexDist(hk(k),hk(h))<=r))});});
  return out;}
// cheapest cost to each hex; Presence blocks (the start's own auras and the lifted target's excepted), Water: one hex then land
function banditRun(k0,speed,AU,lift){const M=mapState(),V=decodeGrid(M.grid),best={},Q=[[0,k0,0]],reach={},key=(k,w)=>k+"|"+w;best[key(k0,0)]=0;
  const blocked=h=>AU.some((o,i)=>i!==lift&&!o.set.has(k0)&&o.set.has(h));
  while(Q.length){Q.sort((x,y)=>x[0]-y[0]);const [d,k,w]=Q.shift();if(d>best[key(k,w)])continue;
    if(k!==k0&&w!==1&&(reach[k]===undefined||reach[k]>d))reach[k]=d;if(w===2)continue;
    hexNb(k).forEach(nk=>{const h=V.hex[nk];if(!h||terrBlocked(h.t)||blocked(nk))return;
      const water=terrWaterStop(h.t),nd=d+1+terrPen(h.t);if(nd>speed)return;let nw;if(w===1){if(water)return;nw=2;}else nw=water?1:0;
      const kk=key(nk,nw);if(best[kk]===undefined||nd<best[kk]){best[kk]=nd;Q.push([nd,nk,nw]);}});}
  return reach;}
function moveCamp(k0,k1){const M=mapState();if(k0===k1||!M.camps[k0])return;M.camps[k1]=M.camps[k0];delete M.camps[k0];delete M.camps[k1].sackTarget;}
function banditSiegeTimer(q,s){const keep=D.siege;D.siege={tp:q.id,sid:s.id,mode:"Lay Siege",army:armiesInside(q,s).length>0,att:0,def:0,by:null};
  let n=1;try{n=siegeCalc({att:null}).total;}finally{D.siege=keep;}return n;}
function banditMoves(){const M=mapState();if(!M.grid)return;const thr=BAN.armyThreshold||25;
  Object.keys(M.camps).filter(k=>+M.camps[k].n>=thr).forEach(k0=>{const cp=M.camps[k0];if(!cp)return;
    if(cp.uid&&realmTimers().some(t=>t.kind==="siege"&&t.bandit===cp.uid)){bLog("Bandit Army @ "+k0+" holds its Siege",k0);return;}
    if(bq().some(o=>[o.A,o.B].some(sd=>sd&&sd.kind==="bandit"&&sd.camp===k0))){bLog("Bandit Army @ "+k0+" is in a queued Battle",k0);return;}
    const AU=banditAuraList(),sp=banditSpeed(cp),V=decodeGrid(M.grid),free=h=>!!V.hex[h]&&!M.cells[h]&&!M.camps[h];
    const inAura=(h,lift)=>AU.some((o,i)=>i!==lift&&o.set.has(h));
    const reach0=banditRun(k0,sp,AU,-1);
    const pick=L=>{if(!L.length)return null;const m=Math.min(...L.map(x=>x.cost)),T=L.filter(x=>x.cost===m),c=T[Math.floor(Math.random()*T.length)];c.tie=T.length>1;return c;};
    const reachOf=tk=>{const li=AU.findIndex(o=>o.k===tk),R0=li<0?reach0:banditRun(k0,sp,AU,li),out=[];
      if(hexDist(hk(k0),hk(tk))===1)out.push({end:k0,cost:0});
      hexNb(tk).forEach(h=>{if(R0[h]!==undefined&&free(h)&&!inAura(h,li))out.push({end:h,cost:R0[h]});});
      return out.sort((a,b)=>a.cost-b.cost)[0]||null;};
    const armies=Object.keys(M.cells).filter(k=>M.cells[k].type==="Army"&&cellPlayer(M.cells[k])&&cellArmy(k).a).map(k=>({k,p:cellPlayer(M.cells[k]),a:cellArmy(k).a}));
    const setts=Object.keys(M.cells).filter(k=>M.cells[k].type!=="Army"&&cellPlayer(M.cells[k])).map(k=>Object.assign({k},cellSett(k))).filter(t=>t.s&&!settUnbuilt(t.s)&&!siegeOn(t.p.id,t.s.id)&&cp.sackTarget!==String(t.p.id)+":"+String(t.s.id));
    const sk=pick(armies.map(t=>{const r=reachOf(t.k);return r?Object.assign({},t,r):null;}).filter(Boolean));
    if(sk){moveCamp(k0,sk.end);bqAdd({kind:"battle",A:{kind:"bandit",camp:sk.end},B:{pid:String(sk.p.id),aid:String(sk.a.id)},seize:"A",src:"Bandit Army"});
      bLog("Bandit Army "+(sk.end===k0?"@ "+k0:k0+" → "+sk.end)+": Skirmish vs "+sk.p.name+"'s "+(sk.a.label||("Army "+sk.a.id))+" (Battle queued)"+(sk.tie?" · tie broken at random":""),sk.end);return;}
    const sg=pick(setts.map(t=>{const r=reachOf(t.k);return r?Object.assign({},t,r):null;}).filter(Boolean));
    if(sg){moveCamp(k0,sg.end);cp.uid=cp.uid||("b"+Date.now().toString(36)+Math.floor(Math.random()*1e4).toString(36));const n=banditSiegeTimer(sg.p,sg.s);
      realmTimers().push({type:"Siege Timer",kind:"siege",tp:sg.p.id,sid:sg.s.id,by:null,aid:null,bandit:cp.uid,label:"Bandits → "+sg.p.name+" · "+(sg.s.name||sg.s.tier),n});
      bLog("Bandit Army "+(sg.end===k0?"@ "+k0:k0+" → "+sg.end)+": Lay Siege to "+sg.p.name+"'s "+(sg.s.name||sg.s.tier)+" · Siege Timer "+n+(sg.tie?" · tie broken at random":""),sg.end);return;}
    if(campWild(k0)&&(BAN.wild||{}).march===false){bLog("Wild Bandit Army @ "+k0+": nothing in range — holds",k0);return;}
    const all=armies.concat(setts.map(t=>({k:t.k,p:t.p})));if(!all.length){bLog("Bandit Army @ "+k0+": no target",k0);return;}
    const d0=Math.min(...all.map(t=>hexDist(hk(k0),hk(t.k)))),tg=all.filter(t=>hexDist(hk(k0),hk(t.k))===d0),tgt=tg[Math.floor(Math.random()*tg.length)];
    let best=null;Object.keys(reach0).forEach(h=>{if(!free(h)||inAura(h,-1))return;const d=hexDist(hk(h),hk(tgt.k));
      if(!best||d<best.d||(d===best.d&&reach0[h]<best.c))best={h,d,c:reach0[h]};});
    if(!best||best.d>=d0){bLog("Bandit Army @ "+k0+": March toward "+tgt.p.name+" @ "+tgt.k+" — no closer hex",k0);return;}
    moveCamp(k0,best.h);bLog("Bandit Army "+k0+" → "+best.h+": March toward "+tgt.p.name+" @ "+tgt.k+(tg.length>1?" · tie broken at random":""),best.h);});}
// gold diverted by Destabilize / Intercept Caravan, measured before income and credited after
function banditSkims(){const B=BST(),out=[],w=curSeason()==="Winter";
  if(w)Object.keys(B.dest).forEach(key=>{const [pid,sid]=key.split(":"),p=D.players.find(q=>String(q.id)===pid),s=p&&(p.board.settlements||[]).find(x=>String(x.id)===sid);
    out.push({kind:"dest",key,camp:B.dest[key].camp,by:B.dest[key].by,p,amt:(p&&s)?settTax(p.board,s):0,what:s?(s.name||s.tier)+" tax":"tax"});});
  // no Trade Income that turn → Extort INTERCEPT_EXTORT_PER_CRAFT × the target's Craft instead
  const h=hostP();if(h&&B.ic[h.id]){const t=tradeRaw(h.board),pc=+((DATA.rulesConst||{}).INTERCEPT_EXTORT_PER_CRAFT)||0,cr=boardMetrics(h.board).craft||0;
    out.push(t.total||!pc?{kind:"ic",key:String(h.id),camp:B.ic[h.id].camp,by:B.ic[h.id].by,p:h,amt:t.total,what:"trade income"}
      :{kind:"ic",ext:true,key:String(h.id),camp:B.ic[h.id].camp,by:B.ic[h.id].by,p:h,amt:pc*cr,what:"no trade income · Extort "+pc+" × Craft "+cr});}
  return out;}
function creditSkims(L){const M=mapState(),B=BST(),out=[];L.forEach(x=>{const by=x.by!=null?pById(x.by):null,cp=by?null:M.camps[x.camp];
  if(x.ext){if(x.p)x.amt=extortGold({b:x.p.board},by?{b:by.board}:cp?{camp:cp}:null,x.amt,"Intercept Caravan");}
  else if(by)tGold(by.board,x.amt,(x.kind==="dest"?"Destabilize":"Intercept Caravan")+": "+(x.p?x.p.name+" · ":"")+x.what);else if(cp)cp.gold=(cp.gold||0)+x.amt;
  const line=(x.kind==="dest"?"Destabilize":"Intercept Caravan")+": "+(x.p?x.p.name:"?")+"'s "+x.what+" "+x.amt+(by?" → "+by.name:cp?" → camp @ "+x.camp:" (camp gone)");
  if(by)out.push(line);else bLog(line);
  if(x.kind==="dest")delete B.dest[x.key];else delete B.ic[x.key];});return out;}
const STAND_INF={Untested:1,Rising:2,Established:3,Sovereign:4};
function envoyOutcome(net){const T=BAN.outcomeThresh||{};
  if(T.Condemned!=null&&net<=T.Condemned)return "Condemned";
  if(T.Failed!=null&&net<=T.Failed)return "Failed";
  if(T.Endorsed!=null&&net>=T.Endorsed)return "Endorsed";
  return "Passed";}
function banditCunningHTML(k,cp){
  const cv=banditDomain(cp.n),st=domBand(cv),inf=STAND_INF[st]||1,mod=+cp.cmod||0,net=inf+mod,oc=envoyOutcome(net);
  const col=oc==="Condemned"||oc==="Failed"?"var(--upkeep)":"var(--income)";
  const O=BAN.cunningOutcomes||{},A=BAN.cunningActions||{},tbl=BAN.cunningTable||[],canRoll=cp.n>=(BAN.cunningMin||10);
  const act=cp.croll?dieLookup(tbl,cp.croll):null;
  let h='<div class="bcun"><div class="bcrow"><span><b>Cunning</b> '+cv+' · '+st+'</span><span>Influence '+inf+'</span>'+
    '<span>mod <input class="bcm" data-k="'+k+'" type="number" value="'+mod+'" style="width:48px"></span>'+
    '<span>net <b>'+net+'</b> → <b style="color:'+col+'">'+oc+'</b></span></div>';
  if(O[oc.toLowerCase()])h+='<div class="note">'+esc(oc)+': '+esc(O[oc.toLowerCase()])+'</div>';
  h+='<table class="dtable ttab" style="margin-top:4px"><thead><tr><th>d'+(BAN.faces||10)+'</th><th>Action</th><th>Effect</th></tr></thead><tbody>'+
    tbl.map(([lo,hi,a])=>{const on=cp.croll&&cp.croll>=lo&&cp.croll<=hi;
      return '<tr'+(on?' class="broll"':'')+'><td>'+(lo===hi?lo:lo+'–'+hi)+'</td><td>'+esc(a)+'</td><td>'+esc((A[a]||{}).effect||'')+(on&&oc==="Endorsed"&&(A[a]||{}).endorsed?' <b>Endorsed:</b> '+esc(A[a].endorsed):'')+'</td></tr>';}).join('')+'</tbody></table>';
  h+='<div class="bcrow" style="margin-top:4px">'+(canRoll?'<button class="bcr" data-k="'+k+'" data-r="cunning">roll d'+(BAN.faces||10)+'</button>':'<span class="note">'+(BAN.cunningMin||10)+'+ retinues to roll</span>')+
    '<span>rolled <input class="bcv" data-k="'+k+'" type="number" min="1" max="'+(BAN.faces||10)+'" value="'+(cp.croll||'')+'" style="width:48px"'+(canRoll?'':' disabled')+'></span>'+
    (act?'<span>→ <b>'+esc(act)+'</b></span>':'')+'</div></div>';
  return h;
}
function dieLookup(tbl,v){const x=(tbl||[]).find(([lo,hi])=>v>=lo&&v<=hi);return x?x[2]:"?";}
// battle tiles -> the map terrain they are drawn from (per the table's own "Map" column)
const BT_KIND={"Hill":"hill","Open Field":"plains","Forest":"forest","Mire":"wetland","Tundra":"tundra","Mountains":"mountain","Water":"water"};
function terrainTablesHTML(PAL){
  const T=TREF.terrain||{},MV=TREF.movement||{},X=TREF.tactical||{};
  const sw=(c,hill,kind)=>RS?tSwatch(hill?'hill':kind,hill?tLighten(c,1.16):c):'<i class="tsw" style="background:'+c+(hill?';filter:brightness(1.16)':'')+'"></i>';
  const fx=v=>Array.isArray(v)?v.join(' '):(v||'—');
  let h='<div class="ttwrap"><div class="tot"><h3 style="font-size:13px">Terrain'+(PAL.label?' <span class="note">· '+esc(PAL.label)+' climate</span>':'')+'</h3><table class="dtable ttab"><thead><tr><th>Terrain</th><th>Effect</th><th>Raw Materials</th></tr></thead><tbody>';
  Object.keys(RULE_NAME).forEach(k=>{const nm=RULE_NAME[k],e=T[nm]||{};
    h+='<tr><td>'+sw(PAL[k],0,k)+esc(nm)+'</td><td>'+esc(fx(e.Effect))+'</td><td>'+esc((e["Raw Materials"]||[]).join(", ")||'—')+'</td></tr>';});
  if(T.Hill)h+='<tr><td>'+sw(PAL.plains,1,'plains')+'Hill</td><td>'+esc(fx(T.Hill.Effect))+'</td><td>—</td></tr>';
  h+='</tbody></table></div>';
  if(Object.keys(MV).length)h+='<div class="tot"><h3 style="font-size:13px">Movement</h3><table class="dtable ttab"><thead><tr><th>Source</th><th>Effect</th></tr></thead><tbody>'+
    Object.keys(MV).map(k=>'<tr><td>'+esc(k)+'</td><td>'+esc(fx((MV[k]||{}).Effect))+'</td></tr>').join('')+'</tbody></table></div>';
  // battle tiles: pixel hex (map fill + scattered sprites) when the sprites are loaded, else the glyph swatch
  const bsw=kd=>{const hill=kd==='hill',c=PAL[hill?'plains':kd];if(!c)return '';return SPR&&SCAT[kd]?pxSwatch(kd,hill?tLighten(c,1.16):c,46):RS?sw(c,hill,kd):'';};
  if(Object.keys(X).length){h+='<div class="tot"><h3 style="font-size:13px">Battle terrain</h3><table class="dtable ttab"><thead><tr><th>Tile</th><th>Map</th><th>Effect</th></tr></thead><tbody>'+
    Object.keys(X).map(k=>'<tr><td>'+(BT_KIND[k]?bsw(BT_KIND[k]):'')+esc(k)+'</td><td>'+esc(X[k].identify||'')+'</td><td>'+esc(X[k].effect||'')+'</td></tr>').join('')+'</tbody></table>';
    if((TREF.tacticalGlobal||[]).length)h+='<div class="note" style="margin-top:4px">'+TREF.tacticalGlobal.map(esc).join(' ')+'</div>';h+='</div>';}
  return h+'</div>';
}
// Map tools (Table, collapsible) + Bandits panel; per-device open state
let MTOOLS_OPEN=true,BPANEL_OPEN=false;
try{MTOOLS_OPEN=localStorage.getItem("renown_mtools")!=="0";BPANEL_OPEN=localStorage.getItem("renown_bpanel")==="1";}catch(e){}
document.addEventListener("click",e=>{const a=e.target.closest("#tMapTools > summary");if(a){MTOOLS_OPEN=!a.parentElement.open;try{localStorage.setItem("renown_mtools",MTOOLS_OPEN?"1":"0");}catch(_){}}
  const b=e.target.closest("#tBandits > summary");if(b){BPANEL_OPEN=!b.parentElement.open;try{localStorage.setItem("renown_bpanel",BPANEL_OPEN?"1":"0");}catch(_){}}});
function mapToolsHTML(){const M=mapState(),g=M.grid;
  const tools=["Select"].concat(PLACE_TOOLS);
  const p=D.players[D.active];
  const presets=Object.keys(MP),np=D.players.length>=2?Math.min(7,D.players.length):4,def=BOARD_SIZE[np]||BOARD_SIZE[6];
  const setupOpen=MAPSETUP_OPEN===null?!g:MAPSETUP_OPEN,bad=mapLinkBad();
  let h='<details class="tot" id="tMapTools"'+(MTOOLS_OPEN?' open':'')+'><summary><b style="font-size:13px">Map</b> <span class="note">— '+
    (g?esc(g.preset)+' · seed '+g.seed+' · '+g.width+'×'+g.height:'no terrain loaded')+' · tool '+esc(mtool)+'</span>'+(bad?' <b class="note" style="color:var(--upkeep)">'+bad+' unlinked</b>':'')+'</summary>';
  h+='<details class="msetup" id="mSetup"'+(setupOpen?' open':'')+'><summary><b>Map setup</b> <span class="note">— '+
    (g?esc(g.preset)+' · seed '+g.seed+' · '+g.players+' players · '+g.width+'×'+g.height:'no terrain loaded')+'</span></summary><div class="mtoolbar">'+
    (MG?'<select id="mPreset">'+presets.map(n=>'<option'+((g?g.preset:"Default")===n?' selected':'')+'>'+esc(n)+'</option>').join('')+'</select>'+
      ' seed <input id="mSeedN" type="number" value="'+esc(g?g.seed:(M.seed||Math.floor(Math.random()*100000)))+'" style="width:80px">'+
      ' players <input id="mPl" type="number" min="2" max="7" value="'+(g?g.players:np)+'" style="width:46px">'+
      ' size <input id="mW" type="number" value="'+(g?g.width:def[0])+'" style="width:46px">×<input id="mH" type="number" value="'+(g?g.height:def[1])+'" style="width:46px">'+
      ' <button id="mGen">generate</button>':'<span class="note">map generator not bundled — JSON import only</span>')+
    ' <input id="mCode" placeholder="Region/seed/players[/WxH]" style="width:210px" value="'+esc(seedCode(g))+'"><button id="mCodeGo">load code</button>'+
    ' <button id="mImp">import map JSON</button><input type="file" id="mFile" accept="application/json" style="display:none">'+
    '</div>'+(g?'<div class="note" style="margin:0 0 6px">generator '+esc(g.generator||'?')+' · climate '+esc(mapPal(g).label||mapClimate(g))+'</div>':'')+'</details>';
  h+='<div class="mtoolbar"><span class="note">tool '+esc(mtool)+' · placing as</span> '+pTok(mapAsP(),12)+' '+esc(mapAsP().name)+
    ' <label class="note"><input type="checkbox" id="mRes"'+(M.showRes!==false?' checked':'')+'> resources</label>'+
    ' <label class="note"><input type="checkbox" id="mReach"'+(M.showReach!==false?' checked':'')+'> reach borders</label>'+
    ' <label class="note"><input type="checkbox" id="mPlates"'+(M.showPlates!==false?' checked':'')+'> army plates</label>'+
    ' <label class="note"><input type="checkbox" id="mSPlates"'+(M.showSPlates!==false?' checked':'')+'> settlement plates</label>'+
    ' <label class="note"><input type="checkbox" id="mStarts"'+(M.showStarts?' checked':'')+'> suggested settlement spots</label>'+
    ' <label class="note"><input type="checkbox" id="mNodes"'+(M.useNodes?' checked':'')+'> Reach check uses resource nodes</label>'+
    ' <button id="mClear">clear markers</button>'+
    ' <span class="mapzoom" style="display:inline-flex;margin:0"><button data-mz="-1" title="zoom out">−</button><button data-mz="1" title="zoom in">+</button><button data-mz="fit"'+(MAPZ.fit?' class="on"':'')+'>fit</button><button id="tbWide" data-nav="1" title="table across the whole width; phase, log and panel below"'+(TB_WIDE?' class="on"':'')+'>wide</button><span class="note">'+(MAPZ.fit?"fit":Math.round(MAPZ.z*100)+"%")+'</span></span></div>';
  const rep=outlawReport(M);
  h+='<div class="tmrow"><div class="tot"><h3 style="font-size:13px">Outlaw Country</h3>'+
    '<div class="note">'+(BAN.outlawStart?BAN.outlawStart+' per player at setup, within range 1 of each other, range '+BAN.outlawBuffer+'+ from any Settlement.':'')+'</div>'+
    '<div style="margin-top:4px">'+(Object.keys(rep.by).length?Object.keys(rep.by).map(rg=>'<span class="badge tier">region '+esc(rg)+': '+rep.by[rg]+'</span>').join(' '):'<span class="note">none marked</span>')+'</div>'+
    (rep.warn.length?'<div class="note" style="color:var(--upkeep);margin-top:4px">'+rep.warn.slice(0,6).map(esc).join('<br>')+'</div>':'')+'</div>'+
    '<div class="tot"><h3 style="font-size:13px">Map ↔ board</h3>'+mapLinksHTML()+'</div></div>'+
    '<div class="note" style="margin:6px 0 0">Terrain, movement and battle-terrain tables are in <a href="#" data-goto="reference#refTerrain">Reference ▸</a></div></details>';
  return h;}
function banditPanelHTML(){const M=mapState(),era=currentEra(),camps=Object.keys(M.camps);
  let c='<details id="tBandits" style="margin-top:4px"'+(BPANEL_OPEN?' open':'')+'><summary class="note" style="cursor:pointer"><b>Camps ('+camps.length+')</b> · Era '+esc(era)+'</summary>'+
    '<div class="note">Era '+esc(era)+': grow +'+((BAN.growth||{})[era]||0)+'/turn · armed with '+esc((BAN.equipment||{})[era]||'—')+
    ' · camp starts at '+(BAN.campStart||'?')+', becomes an Army at '+(BAN.armyThreshold||'?')+'.</div>'+
    '<div style="margin:6px 0"><button id="bGrow">grow all camps</button> <button id="bSpawn">spawn at selected hex</button></div>';
  camps.forEach(k=>{const cp=M.camps[k],army=cp.n>=(BAN.armyThreshold||25),dv=banditDomain(cp.n);
    c+='<div style="border-top:1px solid var(--line);padding:5px 0"><b>'+(army?'Bandit Army':'Bandit Camp')+'</b> <span class="note">@ '+k+'</span>'+
      '<div class="dctrls" style="margin:3px 0 0 0"><span class="dctrl"><span class="note">retinues</span><button class="bcn" data-k="'+k+'" data-d="-1">−</button><span class="dcv">'+cp.n+'</span><button class="bcn" data-k="'+k+'" data-d="1">+</button></span>'+
      '<span class="note">treasury</span><input class="bct" data-k="'+k+'" type="number" step="100" value="'+(cp.gold||0)+'" style="width:80px"></div>'+
      '<div class="note">Prowess +'+dv+'</div>'+banditCunningHTML(k,cp)+
      '<div style="display:flex;gap:4px;margin-top:3px">'+
      '<button class="bcr" data-k="'+k+'" data-r="tactic">tactic roll</button><button class="bcx" data-k="'+k+'">remove</button></div>'+
      (cp.last?'<div class="note">'+esc(cp.last)+'</div>':'')+'</div>';});
  c+='</details>';
  return '<div class="tot" id="tBanditBox"><h3 style="font-size:13px">Bandits</h3>'+banditAutoHTML(c)+'</div>';}
// map edits on a server game: your own pieces only; Outlaw Country by players during setup only; camps by the Host
function mapAsP(){return (lockOn()&&myClaimP())||D.players[D.active];}
function mapEditBlock(k){if(!lockOn())return "";const M=mapState(),c=M.cells[k],me=myClaimP();
  if(!me)return "claim a player to act";
  const own=x=>!!x&&String(x.player)===String(me.id),who=x=>((x&&cellPlayer(x))||{}).name||"another player";
  if(mtool==="Bandit Camp")return canHost()?"":"Host only";
  if(mtool==="Outlaw Country"){if(!firstHostOpen())return "Outlaw Country: setup only";const o=terrOwners()[k];return (o&&o.size)||canHost()?"":"Host only (outside every Province)";}
  if(mtool==="Erase"){if(c&&!own(c))return "\ud83d\udd12 "+who(c)+"'s piece";
    if(M.camps[k]&&!canHost())return "Host only";if(M.outlaw[k]&&!firstHostOpen())return "Outlaw Country: setup only";return "";}
  if(c&&!own(c))return "\ud83d\udd12 "+who(c)+"'s piece";
  return "";}
function mapGuard(kind){if(!lockOn())return "";if(kind==="setup")return ADMIN?"":"Duke only once the game has started";
  if(kind==="bandit")return canHost()?"":"Host only";return myClaimP()?"":"spectators can't change the map";}
function guarded(kind,fn){return function(...a){const w=mapGuard(kind);if(w){flash(w);render();return;}return fn.apply(this,a);};}
// a map hex was clicked (one delegated listener; the overlay redraws without re-wiring)
function mapCellClick(k){const M=mapState();MAPSEL=k;
    if(mtool==="Select"){const mi=SEL?moveInfo():null;
      if(mi&&mi.dest&&mi.dest[k]){if(!canMoveArmy(mi.p)){flash("\ud83d\udd12 not your army");return;}if(moveArmyTo(k)){save();render();}return;}
      const hold=D.players.find(q=>{const x=PT(q).holdMove;return x&&x.turn===tTurn()&&SEL&&String(x.armyPid)===String(SEL.pid)&&String(x.aid)===String(SEL.aid);});
      if(hold){const c=M.cells[k],a=c&&c.type==="Army"?cellArmy(k).a:null;if(a&&String(c.player)===String(SEL.pid)&&String(a.id)===String(SEL.aid)){INSP=k;render();return;}flash("Finish this Holding Move or cancel it before selecting another hex");return;}
      if(INSP===k){INSP=null;SEL=null;render();return;}
      INSP=k;SEL=null;const c=M.cells[k];
      if(c&&c.type==="Army"){const x=cellArmy(k);if(x.p&&x.a&&canMoveArmy(x.p))SEL={pid:String(x.p.id),aid:String(x.a.id)};}
      render();return;}
    {const why=mapEditBlock(k);if(why){flash(why);render();return;}}
    if(mtool==="Erase"){delete M.cells[k];delete M.outlaw[k];delete M.camps[k];}
    else if(mtool==="Outlaw Country"){if(M.outlaw[k])delete M.outlaw[k];
      else{const own=terrOwners(),nz=hexNb(k).map(q=>M.outlaw[q]).find(v=>typeof v==="string");   // joins a neighbouring Wild zone; outside every Province it starts one
        if(nz)M.outlaw[k]=nz;else if(own[k]&&own[k].size)M.outlaw[k]=true;else{let id=1;while(Object.values(M.outlaw).includes("w"+id))id++;M.outlaw[k]="w"+id;}}}
    else if(mtool==="Bandit Camp"){if(!M.camps[k])M.camps[k]={n:BAN.campStart||5,gold:+BAN.campGold||0};}
    else M.cells[k]={type:mtool,player:mapAsP().id};
    save();render();}
document.addEventListener("click",e=>{const el=e.target.closest&&e.target.closest("#rlMap [data-cell]");if(el)mapCellClick(el.dataset.cell);});
function wireMap(host){const M=mapState(),g=M.grid,era=currentEra(),$=id=>host.querySelector("#"+id);
  if(MG&&$("mGen")){$("mGen").onclick=()=>{if(g&&!confirm("Replace the current terrain? Markers stay."))return;
      if(generateMap($("mPreset").value,$("mSeedN").value,$("mPl").value,$("mW").value,$("mH").value)){save();render();}};
    $("mPl").onchange=()=>{const d=BOARD_SIZE[+$("mPl").value];if(d){$("mW").value=d[0];$("mH").value=d[1];}};}
  if($("mCodeGo"))$("mCodeGo").onclick=()=>{const c=parseSeedCode($("mCode").value);if(!c){flash("code format: Region/seed/players[/WxH]");return;}
    if(generateMap(c.preset,c.seed,c.players,c.w,c.h)){save();render();}};
  if($("mImp"))$("mImp").onclick=()=>$("mFile").click();
  if($("mFile"))$("mFile").onchange=e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();
    rd.onload=()=>{try{const j=JSON.parse(rd.result);if(!j.terrain||!j.width)throw 0;M.grid=j;M.cols=j.width;M.rows=j.height;M.seed=String(j.seed);MAPVIEW=null;save();render();}
      catch(err){flash("not a renown-maps JSON export");}};rd.readAsText(f);};
  host.querySelectorAll("[data-mt]").forEach(b=>b.onclick=()=>{mtool=b.dataset.mt;SEL=null;if(mtool!=="Select")INSP=null;render();});
  host.querySelectorAll("[data-mplace]").forEach(b=>b.onclick=()=>{PLACE_OPEN=!PLACE_OPEN;if(!PLACE_OPEN&&mtool!=="Select"){mtool="Select";}render();});
  if($("mvMarch"))$("mvMarch").onchange=e=>{MOVEMARCH=e.target.checked;render();};
  if($("mvAdj"))$("mvAdj").onchange=e=>{MOVEADJ=Math.round(+e.target.value)||0;render();};
  if($("mvCancel"))$("mvCancel").onclick=()=>{const x=selArmy();if(x)D.players.forEach(q=>{const h=PT(q).holdMove;if(h&&String(h.armyPid)===String(x.p.id)&&String(h.aid)===String(x.a.id))delete PT(q).holdMove;});SEL=null;render();};
  if($("mRes"))$("mRes").onchange=e=>{M.showRes=e.target.checked;save();render();};
  if($("mReach"))$("mReach").onchange=e=>{M.showReach=e.target.checked;save();render();};
  if($("mPlates"))$("mPlates").onchange=e=>{M.showPlates=e.target.checked;save();render();};
  if($("mSPlates"))$("mSPlates").onchange=e=>{M.showSPlates=e.target.checked;save();render();};
  if($("mStarts"))$("mStarts").onchange=e=>{M.showStarts=e.target.checked;save();render();};
  if($("mClear"))$("mClear").onclick=()=>{if(confirm("Clear settlements, armies, Outlaw Country and camps? Terrain stays.")){M.cells={};M.outlaw={};M.camps={};save();render();}};

  if($("bGrow"))$("bGrow").onclick=()=>{const gr=(BAN.growth||{})[era]||0,cap=BAN.armyThreshold||25;Object.values(M.camps).forEach(cp=>{cp.n=Math.min(cap,cp.n+gr);});save();render();};
  if($("bSpawn"))$("bSpawn").onclick=()=>{if(!MAPSEL){flash("click a hex first");return;}if(!M.camps[MAPSEL])M.camps[MAPSEL]={n:BAN.campStart||5,gold:+BAN.campGold||0};save();render();};
  host.querySelectorAll(".bcn").forEach(b=>b.onclick=()=>{const cp=M.camps[b.dataset.k];cp.n=Math.max(0,Math.min(BAN.armyThreshold||25,cp.n+(+b.dataset.d)));save();render();});
  host.querySelectorAll(".bct").forEach(i=>i.onchange=()=>{M.camps[i.dataset.k].gold=+i.value||0;save();});
  host.querySelectorAll(".bcx").forEach(b=>b.onclick=()=>{delete M.camps[b.dataset.k];save();render();});
  host.querySelectorAll(".bcr").forEach(b=>b.onclick=()=>{const cp=M.camps[b.dataset.k],v=1+Math.floor(Math.random()*(BAN.faces||10));
    if(b.dataset.r==="cunning")cp.croll=v;else cp.last="Tactic d"+(BAN.faces||10)+": "+v+" → "+dieLookup(BAN.tacticTable,v);save();render();});
  host.querySelectorAll(".bcv").forEach(i=>i.onchange=()=>{const cp=M.camps[i.dataset.k];if(!cp)return;const v=Math.round(+i.value),F=BAN.faces||10,nv=(v>=1&&v<=F)?v:null;
    if(nv===(cp.croll||null))return;cp.croll=nv;save();setTimeout(render,0);});
  host.querySelectorAll(".bcm").forEach(i=>i.onchange=()=>{const cp=M.camps[i.dataset.k];if(!cp)return;const nv=Math.round(+i.value)||0;
    if(nv===(+cp.cmod||0))return;cp.cmod=nv;save();setTimeout(render,0);});
  if($("mNodes"))$("mNodes").onchange=e=>{M.useNodes=e.target.checked;save();render();};
  [["mGen","setup"],["mCodeGo","setup"],["mImp","setup"],["mClear","setup"],["bGrow","bandit"],["bSpawn","bandit"]].forEach(([id,kd])=>{const e=$(id);if(e&&e.onclick)e.onclick=guarded(kd,e.onclick);});
  ["mRes","mReach","mPlates","mSPlates","mStarts","mNodes"].forEach(id=>{const e=$(id);if(e&&e.onchange)e.onchange=guarded("view",e.onchange);});
  host.querySelectorAll(".bcn,.bcx,.bcr").forEach(b=>{if(b.onclick)b.onclick=guarded("bandit",b.onclick);});
  host.querySelectorAll(".bct,.bcv,.bcm").forEach(b=>{if(b.onchange)b.onchange=guarded("bandit",b.onchange);});
}
