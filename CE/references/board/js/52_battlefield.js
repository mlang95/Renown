// ---- Battle field: a top-down view between the two datasheets ----
// Side A holds the left edge, side B the right. Each side forms the line (rules: Form the line): up to FRONT_LINE_MAX in
// front in the revealed Tactic's formation, up to RESERVE_MAX in reserve in front of the camp, the rest in camp at its edge. This
// Skirmish's casualties fall where they stand and reserves step up into the gaps; failed Saves not yet applied are marked
// wounded. Rolls play as short effects (strikes, shots, parries, ripostes, saves, heals, morale). The SVG persists across
// renders so figures glide between states. The battle hex's terrain colours the ground and its battle-terrain rule is shown.
// Playback: every change is a beat in a queue (BF.q) that holds long enough to watch, so the Skirmish plays in rules order
// however fast the dice are rolled: reveal -> the side that Strikes advances to contact (a ranged side shoots from where it
// stands; Defensive Formation, Ambush, Scout and Fall Back hold) -> Strikes -> Parries / Saves / Recover -> the fallen fall,
// Panic and Break losses run for their own edge -> the other side answers -> End Skirmish: the report floats over each
// army, the survivors walk back to camp, and the next Skirmish marches out. Display only: rolling never waits for it.
const BF_W=640,BF_H=400,BF_S=26,BF_DORD=[3,7,0,5,9,2,6,1,8,4];   // death order over front slots (spread along the line)
// a line of n slots, centre-out (the first slots are the ones a small army fills)
function bfLine(n,sp,adv,lat0,slant){return Array.from({length:n},(_,i)=>[adv+(slant||0)*i,lat0+(i-(n-1)/2)*sp])
  .sort((p,q)=>Math.abs(p[1]-lat0)-Math.abs(q[1]-lat0));}
// formation slots as [advance from own edge, offset to the side's right]; Fighting Formation also stands in before the reveal
function bfForm(t){switch(t){
  case "Charge":return bfLine(1,27,266,0).concat(bfLine(2,27,240,0),bfLine(3,27,214,0),bfLine(4,27,188,0));   // spearhead
  case "Fall Back":return bfLine(4,27,178,0).concat(bfLine(3,27,152,0),bfLine(2,27,126,0),bfLine(1,27,100,0));  // the wedge reversed
  case "Defensive Formation":return bfLine(5,23,128,0).concat(bfLine(5,23,154,0));                       // tight, sitting back
  case "Flank":return bfLine(5,25,200,118,6).concat(bfLine(5,25,226,118,6));                             // off centre
  case "Ambush":return [0,1,2,3,4].flatMap(i=>[[110+i*22,-(14+i*24)],[110+i*22,14+i*24]]);             // empty V, open to receive the attack
  case "Scout":return bfLine(5,30,234,-112).concat(bfLine(5,30,264,-112));                              // overlooks from the side
  default:return bfLine(10,27,190,0);}}                                                                  // close order
function bfXY(X,adv,lat){return X==="A"?[adv,BF_H/2+lat]:[BF_W-adv,BF_H/2-lat];}
// where every field figure stands this Skirmish: ids 0..FM-1 start in front, then the reserve; deaths walk BF_DORD and the
// next reserve steps into the gap. dead = cas (applied), wound = the next pend (rolled, not yet applied)
function bfPlace(F0,cas,pend,FM){const occ=[],res=[],st=[];
  for(let id=0;id<F0;id++){if(id<FM){occ[id]=id;st[id]={k:"f",i:id};}else{res.push(id);st[id]={k:"r",i:id-FM};}}
  let k=0;
  for(let n=0;n<cas+pend;n++){let slot=-1;
    for(let t=0;t<FM;t++){const s=BF_DORD[(k+t)%FM];if(occ[s]!=null){slot=s;k=(k+t+1)%FM;break;}}
    if(n>=cas){if(slot<0)break;st[occ[slot]].wound=true;occ[slot]=null;continue;}             // wounded stay in place
    if(slot<0){const id=res.shift();if(id==null)break;st[id]={k:"dead",at:st[id]};continue;}
    const id=occ[slot];st[id]={k:"dead",at:{k:"f",i:slot}};
    const r=res.shift();if(r!=null){occ[slot]=r;st[r]={k:"f",i:slot};}else occ[slot]=null;}
  return st;}
// the battle hex (the defender's, else the attacker's) -> {key, kind, tile, fill}
function bfTerrain(){const B=battle();
  if(B.terrain){const kind=BT_KIND[B.terrain]||"plains",PAL=mapPal(mapState().grid||null);   // a set terrain (Escalation)
    return {key:"",kind,tile:B.terrain,fill:kind==="hill"?tLighten(PAL.plains,1.16):(PAL[kind]||PAL.plains)};}
  const M=mapState(),g=M.grid,k=sideHex(B.B)||sideHex(B.A);if(!g||!k)return null;
  const hx=decodeGrid(g).hex[k];if(!hx)return null;const PAL=mapPal(g),kind=hx.hill?"hill":hx.t;
  const tile=hx.hill?"Hill":kind==="plains"?"Open Field":Object.keys(BT_KIND).find(n=>BT_KIND[n]===kind)||null;
  return {key:k,kind,tile,fill:hx.hill?tLighten(PAL.plains,1.16):(PAL[kind]||PAL.plains)};}
function bfSideInfo(X){const B=battle(),sd=B[X],c=sideCalc(X);if(!c)return null;const a=c.a,FM=BT.frontMax||10,RM=BT.reserveMax??5;
  const pl=sd.kind==="bandit"?null:D.players.find(p=>String(p.id)===String(sd.pid));
  // revealed > this device's own locked-in pick (or Outrider peek) > this device's unlocked choice (own side / manual entry)
  const rev=B.rev&&B.rev.sk===B.sk?B.rev[X]:null,pk=(typeof PICKS!=="undefined"&&PICKS[X])||{},
        sel=!rev&&!pk.tactic&&!pk.picked&&TAC_SEL[X]&&(viewerSide()===X||sd.tmode==="manual"||!API.online)?TAC_SEL[X]:null,
        tac=rev||pk.tactic||sel,tst=rev?"":pk.tactic?" · locked in":sel?" · not locked in":pk.picked?"":"",cas=c.skCas||0,F0=Math.min((a.count||0)+cas,FM+RM),
        rep=B.endRep&&B.endRep.sk===B.sk?B.endRep.rows.find(r=>r.X===X):null;
  const nm=sd.kind==="bandit"?"Bandits":(a.label||(pl&&pl.name)||(X==="A"?"Left":"Right"));
  return {X,c,a,pl,nm,col:pl?pl.color:"#8b2b2b",rk:"army:"+(a.retinue||BANDIT_DEFAULT_RETINUE),tac,tst,locked:!!pk.picked,F0,FM,RM,cas,
    pend:B.id?pendCas(X):0,mor:!!(B.pendCas&&B.pendCas[X]&&B.pendCas[X].mor),rout:!!(rep&&rep.rout),ranged:c.eqX.mode==="ranged",
    rw:c.eqX.mode==="ranged"&&a.ranged&&a.ranged!=="None"?a.ranged:""};}
let BF=null;
function bfFigure(s,id){const flip=s.X==="B";
  return '<g class="bf-u" data-x="'+s.X+'" data-id="'+id+'" style="--lx:'+(flip?-12:12)+'px"><g class="bf-b">'+
    '<g'+(flip?' transform="translate('+BF_S+',0) scale(-1,1)"':'')+'>'+(SPR&&SPR.S[s.rk]?sprSVG(s.rk,BF_S,false,s.col):
    '<svg width="'+BF_S+'" height="'+BF_S+'"><circle cx="11" cy="11" r="7" fill="'+s.col+'" stroke="#000" stroke-opacity=".5"/></svg>')+'</g></g></g>';}
function bfGround(T){if(!T)return '<rect width="'+BF_W+'" height="'+BF_H+'" fill="var(--panel2)"/>';
  let h='<rect width="'+BF_W+'" height="'+BF_H+'" fill="'+T.fill+'"/>';
  if(SPR&&typeof SCAT!=="undefined"&&SCAT[T.kind])[[90,40],[320,34],[550,40],[90,360],[320,366],[550,360],[200,200],[440,200]].forEach(([x,y],i)=>
    h+=mapScatter(T.kind,"bf"+i,x,y,48,T.fill,"field|"+T.key,null,true));
  return h;}
function bfCamp(X,col){const x=X==="A"?6:BF_W-50,y=BF_H/2-54,cs=SPR&&SPR.S["map:camp"];
  return '<g><rect x="'+x+'" y="'+y+'" width="44" height="108" rx="4" fill="#000" fill-opacity=".25" stroke="'+col+'" stroke-opacity=".7" stroke-dasharray="3 3"/>'+
    [0,1].map(i=>'<g transform="translate('+(x+4)+','+(y+12+i*44)+')">'+(cs?sprSVG("map:camp",36,false,col):'<path d="M4 32L18 6L32 32Z" fill="'+col+'" stroke="#000" stroke-opacity=".5"/>')+'</g>').join("")+'</g>';}
// (re)build the SVG for this Skirmish: figures start in camp and march out on the next frame
function bfBuild(sig,S,T){const wrap=document.createElement("div");wrap.className="bf-wrap";
  let h='<div class="bf-stage"><svg class="bf" viewBox="0 0 '+BF_W+' '+BF_H+'" role="img" aria-label="Battle field">'+bfGround(T)+
    '<line x1="'+BF_W/2+'" y1="8" x2="'+BF_W/2+'" y2="'+(BF_H-8)+'" stroke="#000" stroke-opacity=".25" stroke-dasharray="5 6"/>';
  ["A","B"].forEach(X=>{const s=S[X];if(s)h+=bfCamp(X,s.col);});
  h+='<g class="bf-units">';["A","B"].forEach(X=>{const s=S[X];if(!s)return;for(let id=0;id<s.FM+s.RM;id++)h+=bfFigure(s,id);});
  h+='</g><g class="bf-fx"></g></svg></div><div class="bf-cap"></div>';
  wrap.innerHTML='<div class="bf-head"></div>'+h;   // no event feed under the header (bfFeedPaint finds no .bf-feed); the Chronicle keeps the log
  const t0=()=>({parry:0,rip:0,save:0,heal:0,on:{}});                 // on = which of these have been rolled this Skirmish
  const Bt=battle();
  BF={wrap,sig,seen:{},rip:{},pos:{A:[],B:[]},fresh:true,t:{A:t0(),B:t0()},res:{A:S.A?S.A.c.reserve:0,B:S.B?S.B.c.reserve:0},panic:{},
    q:[],qOn:false,eng:{A:false,B:false},fledN:{A:0,B:0},fled:{A:new Set(),B:new Set()},lay:"",S,bid:Bt.id,sk:Bt.sk,leaving:null};
  // start everyone in camp
  wrap.querySelectorAll(".bf-u").forEach(u=>{const [x,y]=bfXY(u.dataset.x,28,0);u.style.transition="none";u.style.opacity="0";
    u.style.transform="translate("+(x-BF_S/2)+"px,"+(y-BF_S/2)+"px)";});}
function bfState(){const B=battle(),S={A:bfSideInfo("A"),B:bfSideInfo("B")},T=bfTerrain();
  const sig=[B.id,B.sk,T&&T.key].concat(["A","B"].map(X=>S[X]?[S[X].a.retinue,S[X].col,S[X].F0].join("/"):"-")).join("|");
  return {S,T,sig};}
// ---- playback queue: a beat runs, then holds ms before the next (a long queue plays faster so it catches up) ----
const BF_PACE=1;   // a long queue only plays faster when dice are entered by hand (emulated dice keep full pace)
function bfQ(fn,ms,tag){const b=BF;if(!b)return;
  if(tag==="layout"&&b.q.length&&b.q[b.q.length-1].tag==="layout")b.q.pop();   // a newer layout replaces one still waiting
  b.q.push({fn,ms,tag});if(!b.qOn)bfQRun(b);}
function bfQRun(b){const it=b.q.shift();if(!it){b.qOn=false;return;}b.qOn=true;
  try{it.fn();}catch(e){console.warn("battle field beat",e);}
  setTimeout(()=>bfQRun(b),it.ms*BF_PACE*(b.q.length>6&&!battle().dice?.5:1));}   // emulated dice: always full pace
// Skirmish over: the report floats over each army, the survivors walk back to camp, then the next Skirmish's field is built
function bfLeave(sig){const b=BF;b.leaving=sig;const B=battle(),R=B.endRep&&B.endRep.sk===B.sk?B.endRep:null;
  if(R){BF_REP=B.id+"|"+JSON.stringify(R);bfQ(()=>bfReportFloats(R,b.S),2000);}
  bfQ(()=>{b.wrap.querySelectorAll(".bf-u").forEach(u=>{if(u.classList.contains("dead")||u.style.opacity==="0"){u.style.opacity="0";return;}
      const [x,y]=bfXY(u.dataset.x,28,(+u.dataset.id%5-2)*16);u.style.transform="translate("+(x-BF_S/2)+"px,"+(y-BF_S/2)+"px)";});},1300);
  bfQ(()=>b.wrap.querySelectorAll(".bf-u").forEach(u=>{u.style.opacity="0";}),500);
  bfQ(()=>{if(BF!==b)return;const old=b.wrap,{S,T,sig:sg}=bfState();bfBuild(sg,S,T);if(old.isConnected)old.replaceWith(BF.wrap);bfUpdate(S,T);},0);}
function bfMount(host){const ph=host.querySelector("#bfield");if(!ph)return;
  try{const {S,T,sig}=bfState(),B=battle();
    if(BF&&BF.sig!==sig&&BF.leaving===sig){ph.replaceWith(BF.wrap);return;}             // still walking back to camp
    if(BF&&BF.sig!==sig&&BF.bid===B.id&&B.sk===BF.sk+1&&!BF.fresh){ph.replaceWith(BF.wrap);bfLeave(sig);return;}
    if(!BF||BF.sig!==sig)bfBuild(sig,S,T);
    ph.replaceWith(BF.wrap);bfUpdate(S,T);}
  catch(e){console.warn("battle field",e);}}
// the field is already in the page: redraw the panels around it (around()), then update it in place. false = rebuild instead
function bfRefresh(around){try{const {S,T,sig}=bfState();
    if(BF&&BF.leaving===sig){around();return true;}
    if(!BF||BF.sig!==sig)return false;around();bfUpdate(S,T);return true;}
  catch(e){console.warn("battle field",e);return false;}}
// how far a side's line moves up once it engages: to contact with the enemy's front, or to the middle when both engage
const BF_HOLD=new Set(["Defensive Formation","Ambush","Scout","Fall Back"]);
function bfFrontAdv(s){const F=bfForm(s.tac).slice(0,s.FM);return F.length?Math.max(...F.map(p=>p[0])):190;}
function bfAdvance(S,X){if(!BF.eng[X])return 0;const s=S[X],O=X==="A"?"B":"A",o=S[O];if(!s)return 0;
  const target=BF.eng[O]||!o?BF_W/2-16:BF_W-bfFrontAdv(o)-30;return Math.max(0,target-bfFrontAdv(s));}
// place every figure for state S: formation (moved up if engaged), reserve, camp, the fallen; Panic / Break losses run off
function bfLayout(S,fresh){const W=BF.wrap;BF.S=S;
  ["A","B"].forEach(X=>{const s=S[X];BF.pos[X]=[];if(!s)return;
    const F=bfForm(s.tac),st=bfPlace(Math.min(s.F0+BF.fledN[X],s.FM+s.RM),s.cas,s.mor?0:s.pend,s.FM),dv=bfAdvance(S,X);
    const RS_=bfLine(s.RM,26,74,0);                                       // reserves stand in front of the camp
    const at=q=>q.k==="f"?[F[q.i][0]+dv,F[q.i][1]]:[RS_[q.i][0]+dv*.7,RS_[q.i][1]];
    W.querySelectorAll('.bf-u[data-x="'+X+'"]').forEach(u=>{const id=+u.dataset.id,q=st[id];
      let p,op=1;
      if(!q){p=[28,(id%5-2)*16];op=0;}                                   // in camp
      else if(BF.fled[X].has(id)){p=q.k==="dead"?at(q.at):at(q);p=[6,p[1]*.6];op=0;}   // Panic / Break: ran for their own edge
      else if(q.k==="dead")p=at(q.at);
      else{p=at(q);if(s.rout){p=[28,p[1]*.3];op=0;}}                     // a Rout runs back to camp
      const fled=BF.fled[X].has(id),[x,y]=bfXY(X,p[0],p[1]);
      if(fresh)requestAnimationFrame(()=>requestAnimationFrame(()=>{u.style.transition="";u.style.transform="translate("+(x-BF_S/2)+"px,"+(y-BF_S/2)+"px)";u.style.opacity=op;}));
      else{u.style.transform="translate("+(x-BF_S/2)+"px,"+(y-BF_S/2)+"px)";u.style.opacity=op;}
      const dead=!!q&&q.k==="dead"&&!fled&&!u.classList.contains("fled");if(dead&&!fresh&&!u.classList.contains("dead"))bfAnim(u,"dying",1000);   // struck down: flash, reel, fall
      u.classList.toggle("dead",dead);u.classList.toggle("fled",fled);u.classList.toggle("wound",!!q&&!!q.wound);
      if(q&&q.k==="f"&&!q.wound)BF.pos[X].push({x,y,u});});});}
function bfLaySig(S){return ["A","B"].map(X=>{const s=S[X];return s?[s.tac,s.F0,s.cas,s.pend,s.rout,BF.eng[X],BF.fledN[X]].join(","):"-";}).join("|");}
function bfUpdate(S,T){const W=BF.wrap,B=battle(),fresh=BF.fresh;BF.fresh=false;
  // header: army name + Equipped gear, Tactic (+ its modifiers once revealed), line / reserve / camp counts
  W.querySelector(".bf-head").innerHTML=["A","B"].map(X=>{const s=S[X];if(!s)return '<div></div>';
    const gear=SPR?bfGear(s).map(n=>'<span title="'+esc(n)+'">'+eqSVG(n,18)+'</span>').join(""):"",mods=s.c.cell?fmtModLong(s.c.tmEff)+s.c.tmBlk.map(t=>' · '+t).join(""):"";
    return '<div class="bf-side" style="--pc:'+s.col+'"><div class="bf-nm"><b>'+esc(s.nm)+'</b><span class="bf-gear">'+gear+'</span></div>'+
      '<div class="bf-tac">'+esc(s.tac||(s.locked?"Tactic locked in":"Tactic hidden"))+(s.tac?esc(s.tst):'')+(mods?' · <i>'+esc(mods)+'</i>':'')+'</div><span>front '+s.c.front+' · reserve '+s.c.reserve+' · camp '+s.c.camp+(s.cas?' · fallen '+s.cas:'')+(s.pend?' · wounded '+s.pend:'')+'</span></div>';}).join('<div class="bf-mid"><span class="bf-sk">Skirmish '+(B.id?B.sk:'—')+'</span></div>');
  // caption: the battle tile and its rule
  const TT=(TREF.tactical||{})[T&&T.tile]||null;
  W.querySelector(".bf-cap").innerHTML=T?((typeof pxSwatch==="function"&&SPR&&SCAT[T.kind]?pxSwatch(T.kind,T.fill,22):'')+'<b>'+esc(T.tile||"")+'</b>'+(TT?' <span>'+esc(TT.effect||"")+'</span>':'')+(T.key?' <span class="note">hex '+esc(T.key)+'</span>':''))
    :'<span class="note">No map hex for this battle</span>';
  bfFeedPaint();
  if(fresh){bfLayout(S,true);BF.lay=bfLaySig(S);BF.seen=bfSeen();BF.res={A:S.A?S.A.c.reserve:0,B:S.B?S.B.c.reserve:0};
    const R=B.endRep&&B.endRep.sk===B.sk?B.endRep:null,key=R?B.id+"|"+JSON.stringify(R):"";
    if(R&&key!==BF_REP){BF_REP=key;bfQ(()=>{},1000);bfQ(()=>bfReportFloats(R,S),2000);}      // opened mid-battle: still show the last report
    return;}
  bfEffects(S);BF.res={A:S.A?S.A.c.reserve:0,B:S.B?S.B.c.reserve:0};
  const ls=bfLaySig(S);if(ls!==BF.lay){BF.lay=ls;bfQ(()=>bfLayout(S,false),1000,"layout");}}
// the gear a side has Equipped this Skirmish: the weapon in hand, a usable shield, the armour
function bfGear(s){const a=s.a,c=s.c,w=c.eqX.mode==="ranged"&&a.ranged&&a.ranged!=="None"?a.ranged:a.weapon;
  return [w,c.dualW?w:null,a.shield&&a.shield!=="None"&&!c.shDest&&!c.shOff?a.shield:null,a.armor].filter(n=>n&&SPR.S["eq:"+n]);}
// pop-up feed under the field header: every event of this Skirmish, one line each, stacked (k replaces an earlier line of the
// same kind). Kept here, not in the DOM, so a redraw that rebuilds the field repaints them; they stay until the Skirmish ends.
// The end-of-Skirmish report (Endurance / Morale lost) is posted as the next Skirmish begins and stays through it.
// The Chronicle keeps everything.
let BF_FEED=[],BF_FEED_ID=null;
function bfFeedPaint(){if(!BF)return;const F=BF.wrap.querySelector(".bf-feed");if(!F)return;const B=battle(),id=B.id;if(BF_FEED_ID!==id){BF_FEED=[];BF_FEED_ID=id;}
  BF_FEED=BF_FEED.filter(t=>t.sk===B.sk);
  const h=BF_FEED.map(t=>'<div class="bf-toast'+(t.fresh?'':' seen')+'" style="--pc:'+t.col+'">'+t.html+'</div>').join("");
  if(F.innerHTML!==h)F.innerHTML=h;BF_FEED.forEach(t=>t.fresh=false);}
function bfToast(k,html,col,delay){const show=()=>{const B=battle(),id=B.id;if(BF_FEED_ID!==id){BF_FEED=[];BF_FEED_ID=id;}
    const t={k,html,col:col||"#888",fresh:true,sk:B.sk},i=BF_FEED.findIndex(x=>x.k===k);if(i>=0)BF_FEED[i]=t;else BF_FEED.push(t);bfFeedPaint();};
  if(delay)setTimeout(show,delay);else show();}
const bfN=(n,one,many)=>n+" "+(n===1?one:(many||one+"s"));
// the defending side's line for this Skirmish: only what it can roll (no Parry -> no parries / ripostes; no Recover -> no heals),
// and only once it has been rolled
function bfDefLine(s){const t=BF.t[s.X],c=s.c,o=[];
  if(c.canParry&&t.on.parry)o.push(bfN(t.parry,"parry","parries"));if(c.canParry&&(c.riposte||c.riposteMelee)&&(t.on.parry||t.rip))o.push(bfN(t.rip,"riposte"));
  if(t.on.save)o.push(bfN(t.save,"save"));if(c.recThr!=null&&t.on.heal)o.push(bfN(t.heal,"heal"));
  return '<b>'+esc(s.nm)+'</b>: '+o.join(" · ");}
// end-of-Skirmish report, as combat text over each army: Endurance lost, the Break check, the Fatigue token, Routs / wiped out
let BF_REP="";
function bfReportFloats(R,S){R.rows.forEach((r,i)=>{const s=S&&S[r.X];if(!s)return;const d=r.e0-r.e1,X=r.X,t0=i*300;
  bfFloat(X,d>0?'Endurance −'+d:'Endurance holds',"#cfd8dc",t0,"md");
  if(r.brk)bfFloat(X,r.brk.dice?'Break: '+bfN(r.brk.lost,"lost","lost"):'Break check due',"#ffb74d",t0+350,"md");
  if(r.fat!=null)bfFloat(X,'Fatigue '+r.fat+' · Morale '+r.m1+'+',"#ffcc80",t0+700);
  if(r.rout||r.wiped)bfFloat(X,r.rout?'ROUT!':'WIPED OUT',"#ff5252",t0+1000,"xl");});}
// what has already been shown: each side's last roll, pending Ripostes, the reveal
function bfSeen(){const B=battle(),o={rev:B.rev&&B.rev.sk===B.sk?B.rev.A+"|"+B.rev.B:""};
  ["A","B"].forEach(X=>{o[X]=JSON.stringify((B.rolls||{})[X]||null);o["rip"+X]=ripN(X);o["cas"+X]=(B[X]||{}).cas||0;});return o;}
function bfFx(svg){const fx=BF.wrap.querySelector(".bf-fx");fx.insertAdjacentHTML("beforeend",svg);const el=fx.lastElementChild;setTimeout(()=>el&&el.remove(),2700);}
// Recover: green glow on the recovered (the wounded first, they are the ones getting back up)
function W_heal(X,n){if(!BF||n<=0)return;const W=[...BF.wrap.querySelectorAll('.bf-u.wound[data-x="'+X+'"]')],F=(BF.pos[X]||[]).map(m=>m.u);
  W.concat(F.filter(u=>!W.includes(u))).slice(0,n).forEach(u=>{const b=u.getBBox?u:null;bfAnim(u,"healed",900);
    const p=(BF.pos[X]||[]).find(m=>m.u===u);if(p)bfFx(BF_MARK.heal(p.x,p.y));});}
// a short animation class on one figure
function bfAnim(u,cls,ms){u.classList.remove(cls);void u.getBBox();u.classList.add(cls);setTimeout(()=>u.classList.remove(cls),ms||700);}
// floating text over a side's line ("6 Strikes", "2 saved", "✝ 3"): rises and fades; several in a row stack upwards
function bfFloat(X,txt,col,delay,size){const go=()=>{if(!BF)return;const P=BF.pos[X]||[],now=Date.now();
    let x,y;if(P.length){x=P.reduce((a,m)=>a+m.x,0)/P.length;y=Math.min(...P.map(m=>m.y))-16;}else[x,y]=bfXY(X,190,0);
    BF.fl=BF.fl||{};const L=(BF.fl[X]||[]).filter(t=>now-t<1600);L.push(now);BF.fl[X]=L;y-=(L.length-1)*42;
    x=Math.max(110,Math.min(BF_W-110,x));y=Math.max(40,y);
    bfFx('<text class="bf-float'+(size?' '+size:'')+'" x="'+x.toFixed(0)+'" y="'+y.toFixed(0)+'" text-anchor="middle" fill="'+col+'">'+txt+'</text>');};
  if(delay)setTimeout(go,delay);else go();}
function bfPick(L,n){const a=L.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a.slice(0,n);}
const BF_MARK={
  hit:(x,y,red)=>'<g transform="translate('+x+','+y+')"><polygon class="bf-pop" points="0,-9 2.5,-2.5 9,0 2.5,2.5 0,9 -2.5,2.5 -9,0 -2.5,-2.5" fill="'+(red?"#ef5350":"#ffd54f")+'" stroke="#000" stroke-opacity=".6"/></g>',
  parry:(x,y)=>'<g transform="translate('+x+','+(y-14)+')"><g class="bf-pop" stroke-linecap="round">'+                  // crossed blades + glint
    '<path d="M-8 8L7 -7M8 8L-7 -7" stroke="#0b0f14" stroke-width="4"/><path d="M-8 8L7 -7M8 8L-7 -7" stroke="#e8edf2" stroke-width="2"/>'+
    '<path d="M-9 4L-4 9M9 4L4 9" stroke="#c9a227" stroke-width="2"/><path d="M0 -6L1.3 -1.3L6 0L1.3 1.3L0 6L-1.3 1.3L-6 0L-1.3 -1.3Z" fill="#fff"/></g></g>',
  save:(x,y)=>'<g transform="translate('+x+','+(y-14)+')"><path class="bf-pop" d="M-6 -6H6V0Q6 6 0 9Q-6 6 -6 0Z" fill="#90caf9" stroke="#0d2a45"/></g>',
  heal:(x,y)=>'<g transform="translate('+x+','+(y-14)+')"><path class="bf-pop" d="M-2 -7H2V-2H7V2H2V7H-2V2H-7V-2H-2Z" fill="#66bb6a" stroke="#0b3d0e"/></g>',
  shot:(x1,y1,x2,y2,c)=>'<line class="bf-shot" x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="'+(c||"#f5e6c8")+'" stroke-width="2" stroke-linecap="round"/>'};
// each change since the last update becomes beats in the queue (the header comment gives the order they play in)
function bfEffects(S){const B=battle(),now=bfSeen(),was=BF.seen;BF.seen=now;const F=BT.faces||10;
  if(now.rev&&now.rev!==was.rev&&S.A&&S.B){const [ta,tb]=now.rev.split("|"),ml=s=>esc(s.nm)+': '+esc(fmtModLong(s.c.tmEff))+(s.c.tmBlk.length?' ('+esc(s.c.tmBlk.join('; '))+')':'');
    const nc=S.A.c.tm.no_combat||S.B.c.tm.no_combat,IA=S.A.c.I,IB=S.B.c.I,f=IA>IB?S.A:IB>IA?S.B:null;
    bfQ(()=>bfFx('<g class="bf-ban"><rect x="'+(BF_W/2-230)+'" y="'+(BF_H/2-40)+'" width="460" height="80" rx="6" fill="#000" fill-opacity=".75"/>'+
      '<text x="'+BF_W/2+'" y="'+(BF_H/2-10)+'" text-anchor="middle" font-size="20" font-weight="600" fill="#fff">'+esc(ta)+'  vs  '+esc(tb)+'</text>'+
      '<text x="'+BF_W/2+'" y="'+(BF_H/2+12)+'" text-anchor="middle" font-size="13" fill="#ddd">'+ml(S.A)+'</text>'+
      '<text x="'+BF_W/2+'" y="'+(BF_H/2+29)+'" text-anchor="middle" font-size="13" fill="#ddd">'+ml(S.B)+'</text></g>'),2400);
    bfQ(()=>{bfLayout(S,false);BF.lay=bfLaySig(S);},900);                     // into the revealed formations
    bfQ(()=>{if(nc){bfFloat("A","No combat","#cfd8dc",0,"md");bfFloat("B","No combat","#cfd8dc",0,"md");}
      else if(f)bfFloat(f.X,'Strikes first · Initiative '+f.c.I,"#fff59d",0,"md");
      else{bfFloat("A","Simultaneous","#fff59d",0,"md");bfFloat("B","Simultaneous","#fff59d",0,"md");}
      if(S.A.c.tm.end||S.B.c.tm.end)bfFloat(S.A.c.tm.end?"A":"B","Fall Back: last Skirmish","#cfd8dc",500);},1400);}
  const casBeat=X=>{const s=S[X],d=now["cas"+X]-(was["cas"+X]||0);if(!s||d<=0)return;const up=Math.min(d,BF.res[X]||0);
    bfQ(()=>{bfLayout(S,false);BF.lay=bfLaySig(S);bfFloat(X,'✝ '+d,"#ff5252",150,"lg");if(up)bfFloat(X,up+' step up',"#cfd8dc",500);},1300);
    const sd=B[X],pn=(sd.cas||0)+(s.c.enduring?0:(sd.rcv||0)),T=BT.panicThreshold||5;
    if(pn>=T&&!BF.panic[X]){BF.panic[X]=1;bfQ(()=>bfFloat(X,s.c.immunePanic?'Immune Panic':'PANIC CHECK',"#ffb74d",0,"md"),900);}};
  const casDone={};
  ["A","B"].forEach(X=>{if(now[X]===was[X])return;const R=(B.rolls||{})[X],s=S[X],O=X==="A"?"B":"A";if(!R||!s)return;
    const dl=R.dl?R.dl.succ:0;
    if(R.kind==="Strike"){
      if(!s.ranged&&!BF.eng[X]&&!BF_HOLD.has(s.tac))                    // up to contact before the blow lands
        bfQ(()=>{BF.eng[X]=true;bfLayout(BF.S,false);BF.lay=bfLaySig(BF.S);},1100);
      bfQ(()=>{const mine=BF.pos[X],theirs=BF.pos[O],fly=s.ranged?bfShotTime(s.rw):220;
        if(s.ranged)bfPick(mine,10).forEach((m,i)=>{const t=theirs[Math.floor(Math.random()*Math.max(1,theirs.length))];
          if(t)setTimeout(()=>bfFx(bfShot(s.rw,m.x,m.y-6,t.x,t.y)),i*40);});
        else mine.forEach(m=>bfAnim(m.u,"lunge",600));
        setTimeout(()=>bfPick(theirs,R.succ).forEach((t,i)=>bfFx(BF_MARK.hit(t.x,t.y,i<(R.deadly||0)))),fly);
        const cl=cleaveN(X);
        bfFloat(O,(R.cleave?'Cleave +':R.rr?'Re-roll +':'')+bfN(R.succ,"Strike")+(R.target>F?" (can't Strike)":''),"#ffd54f",fly,R.succ>=6?"lg":"md");
        if(R.deadly)bfFloat(O,R.deadly+' DEADLY',"#ff5252",650,"lg");
        if(cl)bfFloat(X,'Cleave ×'+cl,"#ffb74d",900);},1600);}
    else if(R.kind==="Parry")bfQ(()=>{bfPick(BF.pos[X],R.succ+dl).forEach(m=>{bfFx(BF_MARK.parry(m.x,m.y));bfAnim(m.u,"parry",600);});
      bfFloat(X,(R.succ+dl)+' parried'+(R.prr?' ↻':''),"#eceff1",0,"md");BF.t[X].parry+=R.succ+dl;BF.t[X].on.parry=1;},1300);
    else if(R.kind==="Save")bfQ(()=>{bfPick(BF.pos[X],R.succ+dl).forEach(m=>{bfFx(BF_MARK.save(m.x,m.y));bfAnim(m.u,"saved",700);});
      bfFloat(X,(R.succ+dl)+' saved',"#90caf9",0,"md");if(R.cas)bfFloat(X,R.cas+' unsaved',"#ef9a9a",350);BF.t[X].save+=R.succ+dl;BF.t[X].on.save=1;},1300);
    else if(R.kind==="Recover")bfQ(()=>{W_heal(X,R.succ+dl);bfFloat(X,'+'+(R.succ+dl)+' recovered',"#81c784",0,"md");BF.t[X].heal+=R.succ+dl;BF.t[X].on.heal=1;},1200);
    else if(R.kind==="Morale"||R.kind==="Break"){            // instant: the losses already left the army; they run now
      const fl=R.kind==="Morale"?R.dice.length-R.succ:(R.cas||0);
      casBeat(X);casDone[X]=1;BF.fledN[X]+=fl;                // anyone who fell before the check falls first
      bfQ(()=>{const P=BF.pos[X].slice();P.forEach(m=>bfAnim(m.u,"shake",500));
        bfFloat(X,R.kind==="Morale"?'PANIC!':'BREAK!',"#ffb74d",0,"lg");
        bfFloat(X,fl?bfN(fl,"flees","flee"):'they hold',fl?"#ffcc80":"#c5e1a5",350,"md");
        setTimeout(()=>{bfPick(P,fl).forEach(m=>BF.fled[X].add(+m.u.dataset.id));bfLayout(S,false);BF.lay=bfLaySig(S);},500);},1900);}});
  // Riposte: a new pending Riposte against O comes back from X's line
  ["A","B"].forEach(O=>{const X=O==="A"?"B":"A",d=now["rip"+O]-(was["rip"+O]||0);if(d<=0)return;
    bfQ(()=>{if(S[X]){BF.t[X].rip+=d;bfFloat(X,'Riposte ×'+d,"#ffb300",0,"md");}
      bfPick(BF.pos[X],d).forEach((m,i)=>{bfAnim(m.u,"lunge",600);const t=BF.pos[O][i%Math.max(1,BF.pos[O].length)];if(t){bfFx(BF_MARK.shot(m.x,m.y,t.x,t.y,"#ffb300"));setTimeout(()=>bfFx(BF_MARK.hit(t.x,t.y,false)),400);}});},1300);});
  // casualties applied: who falls, who steps up from reserve; a Panic check is due once losses pass the threshold
  ["A","B"].forEach(X=>{if(!casDone[X])casBeat(X);});}

// ---- a shot for each Ranged Weapon (Javelin is shown as a Throwing Axe, Pilum as a Throwing Spear) ----
function bfShotTime(n){return {"Longbow":850,"Hunting Bow":600,"Crossbow":300,"Arquebus":220,"Javelin":650,"Pilum":650}[n]||450;}
function bfShot(n,x1,y1,x2,y2){const dx=x2-x1,dy=y2-y1,L=Math.hypot(dx,dy)||1,mx=(x1+x2)/2,my=(y1+y2)/2,
    arc=h=>'M'+x1.toFixed(0)+' '+y1.toFixed(0)+'Q'+mx.toFixed(0)+' '+(my-Math.min(h,2*(Math.min(y1,y2)-10))).toFixed(0)+' '+x2.toFixed(0)+' '+y2.toFixed(0),
    t=bfShotTime(n),fly=g=>'<g transform="translate('+x1.toFixed(0)+','+y1.toFixed(0)+')"><g class="bf-fly" style="--dx:'+dx.toFixed(0)+'px;--dy:'+dy.toFixed(0)+'px;animation-duration:'+t+'ms">'+g+'</g></g>';
  switch(n){
    case "Longbow":     return '<path class="bf-arc" pathLength="100" d="'+arc(L*.42)+'" stroke="#f5e6c8" stroke-width="2.2" fill="none" stroke-linecap="round" style="animation-duration:'+t+'ms"/>';
    case "Hunting Bow": return '<path class="bf-arc" pathLength="100" d="'+arc(L*.16)+'" stroke="#efe2c4" stroke-width="1.8" fill="none" stroke-linecap="round" style="animation-duration:'+t+'ms"/>';
    case "Crossbow":    return '<path class="bf-arc bolt" pathLength="100" d="M'+x1+' '+y1+'L'+x2+' '+y2+'" stroke="#d9c08a" stroke-width="3.2" fill="none" stroke-linecap="square" style="animation-duration:'+t+'ms"/>';
    case "Arquebus":    return '<g><circle class="bf-flash" cx="'+x1+'" cy="'+y1+'" r="6" fill="#ffb74d"/><circle class="bf-smoke" cx="'+x1+'" cy="'+(y1-4)+'" r="7" fill="#cfd2d6"/>'+
                          '<path class="bf-arc ball" pathLength="100" d="M'+x1+' '+y1+'L'+x2+' '+y2+'" stroke="#fff3b0" stroke-width="1.6" fill="none" style="animation-duration:'+t+'ms"/></g>';
    case "Javelin":     return fly('<g class="bf-spin"><path d="M-5 5L5 -5" stroke="#8a5a3a" stroke-width="2.2" stroke-linecap="round"/><path d="M2 -8L8 -2L4.5 1.5L-1.5 -4.5Z" fill="#d6dce4" stroke="#0b0f14" stroke-width=".8"/></g>');
    case "Pilum":       return fly('<g transform="rotate('+(Math.atan2(dy,dx)*180/Math.PI).toFixed(0)+')"><path d="M-15 0H7" stroke="#8a5a3a" stroke-width="2.2" stroke-linecap="round"/><path d="M4 0H9" stroke="#b8c0cc" stroke-width="1.6"/><path d="M9 -2.6L16 0L9 2.6Z" fill="#d6dce4" stroke="#0b0f14" stroke-width=".7"/></g>');
    default:            return BF_MARK.shot(x1,y1,x2,y2);}}
