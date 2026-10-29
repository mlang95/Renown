// ---- Battle field: a top-down view between the two datasheets ----
// Side A holds the left edge, side B the right. Each side forms the line (rules: Form the line): up to FRONT_LINE_MAX in
// front in the revealed Tactic's formation, up to RESERVE_MAX in reserve in front of the camp, the rest in camp at its edge. This
// Skirmish's casualties fall where they stand and reserves step up into the gaps; failed Saves not yet applied are marked
// wounded. Rolls play as short effects (strikes, shots, parries, ripostes, saves, heals, morale). The SVG persists across
// renders so figures glide between states. The battle hex's terrain colours the ground and its battle-terrain rule is shown.
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
function bfTerrain(){const B=battle(),M=mapState(),g=M.grid,k=sideHex(B.B)||sideHex(B.A);if(!g||!k)return null;
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
    pend:B.id?pendCas(X):0,rout:!!(rep&&rep.rout),ranged:c.eqX.mode==="ranged"};}
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
  h+='</g><g class="bf-fx"></g></svg><div class="bf-feed" aria-live="polite"></div></div><div class="bf-cap"></div>';
  wrap.innerHTML='<div class="bf-head"></div>'+h;
  const t0=()=>({parry:0,rip:0,save:0,heal:0,on:{}});                 // on = which of these have been rolled this Skirmish
  BF={wrap,sig,seen:{},rip:{},pos:{A:[],B:[]},fresh:true,t:{A:t0(),B:t0()},res:{A:S.A?S.A.c.reserve:0,B:S.B?S.B.c.reserve:0},panic:{}};
  // start everyone in camp
  wrap.querySelectorAll(".bf-u").forEach(u=>{const [x,y]=bfXY(u.dataset.x,28,0);u.style.transition="none";u.style.opacity="0";
    u.style.transform="translate("+(x-BF_S/2)+"px,"+(y-BF_S/2)+"px)";});}
function bfMount(host){const ph=host.querySelector("#bfield");if(!ph)return;
  try{const B=battle(),S={A:bfSideInfo("A"),B:bfSideInfo("B")},T=bfTerrain();
    const sig=[B.id,B.sk,T&&T.key].concat(["A","B"].map(X=>S[X]?[S[X].a.retinue,S[X].col,S[X].F0].join("/"):"-")).join("|");
    if(!BF||BF.sig!==sig)bfBuild(sig,S,T);
    ph.replaceWith(BF.wrap);bfUpdate(S,T);}
  catch(e){console.warn("battle field",e);}}
function bfUpdate(S,T){const W=BF.wrap,B=battle(),fresh=BF.fresh;BF.fresh=false;
  ["A","B"].forEach(X=>{const s=S[X];BF.pos[X]=[];if(!s)return;
    const F=bfForm(s.tac),st=bfPlace(s.F0,s.cas,s.pend,s.FM);
    const RS_=bfLine(s.RM,26,74,0);                                       // reserves stand in front of the camp
    const at=q=>q.k==="f"?F[q.i]:RS_[q.i];
    W.querySelectorAll('.bf-u[data-x="'+X+'"]').forEach(u=>{const id=+u.dataset.id,q=st[id];
      let p;
      if(!q)p=[28,(id%5-2)*16];                                          // in camp
      else if(q.k==="dead")p=at(q.at);
      else{p=at(q);if(s.rout)p=[28,p[1]*.3];}                            // a Rout runs back to camp
      const op=!q||(s.rout&&q.k!=="dead")?0:1;
      const [x,y]=bfXY(X,p[0],p[1]);
      if(fresh)requestAnimationFrame(()=>requestAnimationFrame(()=>{u.style.transition="";u.style.transform="translate("+(x-BF_S/2)+"px,"+(y-BF_S/2)+"px)";u.style.opacity=op;}));
      else{u.style.transform="translate("+(x-BF_S/2)+"px,"+(y-BF_S/2)+"px)";u.style.opacity=op;}
      u.classList.toggle("dead",!!q&&q.k==="dead");u.classList.toggle("wound",!!q&&!!q.wound);
      if(q&&q.k==="f"&&!q.wound)BF.pos[X].push({x,y,u});});});
  // header: army name + Equipped gear, Tactic (+ its modifiers once revealed), line / reserve / camp counts
  W.querySelector(".bf-head").innerHTML=["A","B"].map(X=>{const s=S[X];if(!s)return '<div></div>';
    const gear=SPR?bfGear(s).map(n=>'<span title="'+esc(n)+'">'+eqSVG(n,18)+'</span>').join(""):"",mods=s.c.cell?fmtModLong(s.c.tmEff)+s.c.tmBlk.map(t=>' · '+t).join(""):"";
    return '<div class="bf-side" style="--pc:'+s.col+'"><div class="bf-nm"><b>'+esc(s.nm)+'</b><span class="bf-gear">'+gear+'</span></div>'+
      '<div class="bf-tac">'+esc(s.tac||(s.locked?"Tactic locked in":"Tactic hidden"))+(s.tac?esc(s.tst):'')+(mods?' · <i>'+esc(mods)+'</i>':'')+'</div><span>front '+s.c.front+' · reserve '+s.c.reserve+' · camp '+s.c.camp+(s.cas?' · fallen '+s.cas:'')+(s.pend?' · wounded '+s.pend:'')+'</span></div>';}).join('<span class="bf-sk">Skirmish '+(B.id?B.sk:'—')+'</span>');
  // caption: the battle tile and its rule
  const TT=(TREF.tactical||{})[T&&T.tile]||null;
  W.querySelector(".bf-cap").innerHTML=T?((typeof pxSwatch==="function"&&SPR&&SCAT[T.kind]?pxSwatch(T.kind,T.fill,22):'')+'<b>'+esc(T.tile||"")+'</b>'+(TT?' <span>'+esc(TT.effect||"")+'</span>':'')+' <span class="note">hex '+esc(T.key)+'</span>')
    :'<span class="note">No map hex for this battle</span>';
  if(fresh){BF.seen=bfSeen();bfReport(S);return;}
  bfEffects(S);bfReport(S);BF.res={A:S.A?S.A.c.reserve:0,B:S.B?S.B.c.reserve:0};}
// the gear a side has Equipped this Skirmish: the weapon in hand, a usable shield, the armour
function bfGear(s){const a=s.a,c=s.c,w=c.eqX.mode==="ranged"&&a.ranged&&a.ranged!=="None"?a.ranged:a.weapon;
  return [w,c.dualW?w:null,a.shield&&a.shield!=="None"&&!c.shDest&&!c.shOff?a.shield:null,a.armor].filter(n=>n&&SPR.S["eq:"+n]);}
// pop-up feed over the field: one line per event (k replaces an earlier line of the same kind), fading after a few seconds
function bfToast(k,html,col,delay){const show=()=>{if(!BF)return;const F=BF.wrap.querySelector(".bf-feed");if(!F)return;
    const old=F.querySelector('[data-k="'+k+'"]');if(old)old.remove();
    const el=document.createElement("div");el.className="bf-toast";el.dataset.k=k;el.style.setProperty("--pc",col||"#888");el.innerHTML=html;F.appendChild(el);
    while(F.children.length>5)F.firstElementChild.remove();setTimeout(()=>el.remove(),6500);};
  if(delay)setTimeout(show,delay);else show();}
const bfN=(n,one,many)=>n+" "+(n===1?one:(many||one+"s"));
// the defending side's line for this Skirmish: only what it can roll (no Parry -> no parries / ripostes; no Recover -> no heals),
// and only once it has been rolled
function bfDefLine(s){const t=BF.t[s.X],c=s.c,o=[];
  if(c.canParry&&t.on.parry)o.push(bfN(t.parry,"parry","parries"));if(c.canParry&&(c.riposte||c.riposteMelee)&&(t.on.parry||t.rip))o.push(bfN(t.rip,"riposte"));
  if(t.on.save)o.push(bfN(t.save,"save"));if(c.recThr!=null&&t.on.heal)o.push(bfN(t.heal,"heal"));
  return '<b>'+esc(s.nm)+'</b>: '+o.join(" · ");}
// end-of-Skirmish report (Endurance, Fatigue, Break check, Rout), once per report
let BF_REP="";
function bfReport(S){const B=battle(),R=B.endRep&&B.endRep.sk===B.sk?B.endRep:null;if(!R)return;const key=B.id+"|"+JSON.stringify(R);if(key===BF_REP)return;BF_REP=key;
  R.rows.forEach((r,i)=>{const s=S[r.X];if(!s)return;const o=['Endurance '+r.e0+' → '+r.e1];
    if(r.brk)o.push(r.brk.dice?'<b>Break check</b>: '+bfN(r.brk.lost,"casualty","casualties")+' ('+r.brk.n+'d10 vs '+r.brk.target+'+)':'<b>Break check due</b>: '+r.brk.n+'d10 vs '+r.brk.target+'+');
    if(r.fat!=null)o.push('Fatigue '+r.fat+' → Morale '+r.m1+'+');if(r.rout)o.push('<b>Routs</b>');if(r.wiped)o.push('<b>wiped out</b>');
    bfToast("rep"+r.X,'<b>'+esc(s.nm)+'</b>, end of Skirmish '+(R.sk-1)+': '+o.join(' · '),s.col,i*250);});}
// what has already been shown: each side's last roll, pending Ripostes, the reveal
function bfSeen(){const B=battle(),o={rev:B.rev&&B.rev.sk===B.sk?B.rev.A+"|"+B.rev.B:""};
  ["A","B"].forEach(X=>{o[X]=JSON.stringify((B.rolls||{})[X]||null);o["rip"+X]=ripN(X);o["cas"+X]=(B[X]||{}).cas||0;});return o;}
function bfFx(svg){const fx=BF.wrap.querySelector(".bf-fx");fx.insertAdjacentHTML("beforeend",svg);const el=fx.lastElementChild;setTimeout(()=>el&&el.remove(),2700);}
function bfPick(L,n){const a=L.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a.slice(0,n);}
const BF_MARK={
  hit:(x,y,red)=>'<g transform="translate('+x+','+y+')"><polygon class="bf-pop" points="0,-9 2.5,-2.5 9,0 2.5,2.5 0,9 -2.5,2.5 -9,0 -2.5,-2.5" fill="'+(red?"#ef5350":"#ffd54f")+'" stroke="#000" stroke-opacity=".6"/></g>',
  parry:(x,y)=>'<g transform="translate('+x+','+(y-14)+')"><g class="bf-pop" stroke-linecap="round">'+                  // crossed blades + glint
    '<path d="M-8 8L7 -7M8 8L-7 -7" stroke="#0b0f14" stroke-width="4"/><path d="M-8 8L7 -7M8 8L-7 -7" stroke="#e8edf2" stroke-width="2"/>'+
    '<path d="M-9 4L-4 9M9 4L4 9" stroke="#c9a227" stroke-width="2"/><path d="M0 -6L1.3 -1.3L6 0L1.3 1.3L0 6L-1.3 1.3L-6 0L-1.3 -1.3Z" fill="#fff"/></g></g>',
  save:(x,y)=>'<g transform="translate('+x+','+(y-14)+')"><path class="bf-pop" d="M-6 -6H6V0Q6 6 0 9Q-6 6 -6 0Z" fill="#90caf9" stroke="#0d2a45"/></g>',
  heal:(x,y)=>'<g transform="translate('+x+','+(y-14)+')"><path class="bf-pop" d="M-2 -7H2V-2H7V2H2V7H-2V2H-7V-2H-2Z" fill="#66bb6a" stroke="#0b3d0e"/></g>',
  shot:(x1,y1,x2,y2,c)=>'<line class="bf-shot" x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="'+(c||"#f5e6c8")+'" stroke-width="2" stroke-linecap="round"/>'};
function bfEffects(S){const B=battle(),now=bfSeen(),was=BF.seen;BF.seen=now;const F=BT.faces||10;
  if(now.rev&&now.rev!==was.rev&&S.A&&S.B){const [ta,tb]=now.rev.split("|"),ml=s=>esc(s.nm)+': '+esc(fmtModLong(s.c.tmEff))+(s.c.tmBlk.length?' ('+esc(s.c.tmBlk.join('; '))+')':'');
    bfFx('<g class="bf-ban"><rect x="'+(BF_W/2-230)+'" y="'+(BF_H/2-40)+'" width="460" height="80" rx="6" fill="#000" fill-opacity=".75"/>'+
      '<text x="'+BF_W/2+'" y="'+(BF_H/2-10)+'" text-anchor="middle" font-size="20" font-weight="600" fill="#fff">'+esc(ta)+'  vs  '+esc(tb)+'</text>'+
      '<text x="'+BF_W/2+'" y="'+(BF_H/2+12)+'" text-anchor="middle" font-size="13" fill="#ddd">'+ml(S.A)+'</text>'+
      '<text x="'+BF_W/2+'" y="'+(BF_H/2+29)+'" text-anchor="middle" font-size="13" fill="#ddd">'+ml(S.B)+'</text></g>');
    const nc=S.A.c.tm.no_combat||S.B.c.tm.no_combat,IA=S.A.c.I,IB=S.B.c.I,f=IA>IB?S.A:IB>IA?S.B:null;
    bfToast("init",nc?'<b>No combat</b> this Skirmish':f?'<b>'+esc(f.nm)+'</b> fights first (Initiative '+f.c.I+' vs '+(f===S.A?IB:IA)+')':'<b>Both sides</b> strike at once (Initiative '+IA+')',f?f.col:"#aaa",1400);
    [S.A,S.B].forEach((s,i)=>{if(s.c.tmBlk.length)bfToast("blk"+s.X,'<b>'+esc(s.nm)+'</b>: '+esc(s.c.tmBlk.join(' · ')),s.col,900+i*200);});
    if(S.A.c.tm.end||S.B.c.tm.end)bfToast("end",'<b>Fall Back</b>: the Battle ends after this Skirmish',"#aaa",1700);}
  ["A","B"].forEach(X=>{if(now[X]===was[X])return;const R=(B.rolls||{})[X],s=S[X],O=X==="A"?"B":"A";if(!R||!s)return;
    const mine=BF.pos[X],theirs=BF.pos[O],nm='<b>'+esc(s.nm)+'</b>',dl=R.dl?R.dl.succ:0;
    if(R.kind==="Strike"){
      if(s.ranged)bfPick(mine,10).forEach((m,i)=>{const t=theirs[i%Math.max(1,theirs.length)];if(t)bfFx(BF_MARK.shot(m.x,m.y,t.x,t.y));});
      else mine.forEach(m=>{m.u.classList.remove("lunge");void m.u.getBBox();m.u.classList.add("lunge");setTimeout(()=>m.u.classList.remove("lunge"),600);});
      setTimeout(()=>bfPick(theirs,R.succ).forEach((t,i)=>bfFx(BF_MARK.hit(t.x,t.y,i<(R.deadly||0)))),s.ranged?450:220);
      const cl=(R.extra||[]).filter(v=>v>=R.target&&R.target<=F).length;
      bfToast("st"+X,nm+(R.rr?' re-rolls its misses (Dual Wield): +'+bfN(R.succ,"hit"):' strikes: '+bfN(R.succ,"hit"))+
        (s.c.hasDeadly?' · '+(R.deadly||0)+' Deadly':'')+(s.c.hasCleave?' · '+cl+' Cleave':'')+(R.target>F?' (can\'t hit)':''),s.col);}
    else if(R.kind==="Parry"){bfPick(mine,R.succ+dl).forEach(m=>bfFx(BF_MARK.parry(m.x,m.y)));BF.t[X].parry+=R.succ+dl;BF.t[X].on.parry=1;bfToast("df"+X,bfDefLine(s),s.col);}
    else if(R.kind==="Save"){bfPick(mine,R.succ+dl).forEach(m=>bfFx(BF_MARK.save(m.x,m.y)));BF.t[X].save+=R.succ+dl;BF.t[X].on.save=1;bfToast("df"+X,bfDefLine(s),s.col);}
    else if(R.kind==="Recover"){bfPick(mine,R.succ+dl).forEach(m=>bfFx(BF_MARK.heal(m.x,m.y)));BF.t[X].heal+=R.succ+dl;BF.t[X].on.heal=1;bfToast("df"+X,bfDefLine(s),s.col);}
    else if(R.kind==="Morale"){mine.forEach(m=>{m.u.classList.add("shake");setTimeout(()=>m.u.classList.remove("shake"),900);});
      bfToast("mo"+X,nm+' <b>Panic check</b>: '+R.succ+' hold, '+(R.dice.length-R.succ)+' flee ('+R.dice.length+'d10 vs '+R.target+'+)',s.col);}
    else if(R.kind==="Break"){mine.forEach(m=>{m.u.classList.add("shake");setTimeout(()=>m.u.classList.remove("shake"),900);});
      bfToast("br"+X,nm+' <b>Break check</b>: '+R.succ+' hold, '+bfN(R.cas,"casualty","casualties")+' ('+R.dice.length+'d10 vs '+R.target+'+)',s.col);}});
  // Riposte: a new pending Riposte against O comes back from X's line
  ["A","B"].forEach(O=>{const X=O==="A"?"B":"A",d=now["rip"+O]-(was["rip"+O]||0);if(d<=0)return;
    if(S[X]){BF.t[X].rip+=d;bfToast("df"+X,bfDefLine(S[X]),S[X].col);}
    bfPick(BF.pos[X],d).forEach((m,i)=>{const t=BF.pos[O][i%Math.max(1,BF.pos[O].length)];if(t){bfFx(BF_MARK.shot(m.x,m.y,t.x,t.y,"#ffb300"));setTimeout(()=>bfFx(BF_MARK.hit(t.x,t.y,false)),400);}});});
  // casualties applied: who falls, who steps up from reserve; Panic check due once losses pass the threshold
  ["A","B"].forEach(X=>{const s=S[X],d=now["cas"+X]-(was["cas"+X]||0);if(!s||d<=0)return;const up=Math.min(d,BF.res[X]||0);
    bfToast("cas"+X,'<b>'+esc(s.nm)+'</b>: '+bfN(d,"falls","fall")+(up?' · '+up+' step up from reserve':'')+(s.c.front<(BT.frontMax||10)?' · front '+s.c.front:''),s.col);
    const sd=B[X],pn=(sd.cas||0)+(s.c.enduring?0:(sd.rcv||0)),T=BT.panicThreshold||5;
    if(pn>T&&!BF.panic[X]){BF.panic[X]=1;bfToast("pn"+X,s.c.immunePanic?'<b>'+esc(s.nm)+'</b>: '+pn+' lost this Skirmish, Immune Panic':
      '<b>'+esc(s.nm)+'</b>: '+pn+' lost this Skirmish (over '+T+'), <b>Panic check</b> after both sides Strike',s.col,300);}});}
