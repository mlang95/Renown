// ---- Escalation Campaign (lobby game type) ----
// Two armies, Battle after Battle: Battle -> the winner gains an Edict -> both advance (Domain Points or Standings)
// and place Holdings (instant, combat Holdings only) -> both lock a hidden loadout -> next Battle. No economy, map
// or Table. Reuses the Battle view (sideCalc, rolls, hidden picks) unchanged; this file adds the round loop, the
// Campaign pane and the AI. Tuning: renown_data.ESCALATION (DATA.escalation); game options: D.esc.opts (lobby).
// The AI never sees a live pick: only public state (Holdings, Standings, loadouts and Tactics already revealed).
const ESCD=DATA.escalation||null;
function escOn(){return !!(ESCD&&D.esc);}
function escO(){return Object.assign({},ESCD.defaults,(D.esc||{}).opts||{});}
function escAiKey(){const k=escO().ai;return k&&ESCD.ai[k]?k:"";}
function escAiCfg(){const k=escAiKey();return k?ESCD.ai[k]:null;}
function escIsAi(p){return !!p&&!!D.esc&&D.esc.aiPid!=null&&String(p.id)===String(D.esc.aiPid);}
function escAiP(){return D.esc&&D.esc.aiPid!=null?pById(D.esc.aiPid):null;}
function escMe(){const m=myClaimP();if(m)return m;const p=D.players[D.active];return p&&escIsAi(p)?(D.players.find(q=>!escIsAi(q))||p):p;}
function escFoe(p){return D.players.find(q=>!sameP(q,p))||null;}
function escPB(p){p.board.esc=p.board.esc||{};return p.board.esc;}
function escDriver(){return !D.players.some(q=>!escIsAi(q)&&mine(q)&&!sameP(q,escMe()))&&!!escMe()&&!escIsAi(escMe());}
const ESC_STEPS=[["Rising",RIS],["Established",EST],["Sovereign",SOV]];

// ---- setup ----
function escStartLoad(){const s=ESCD.start||{};return {retinue:s.retinue||"Levy",weapon:s.weapon||"Farm Tools",ranged:"None",armor:s.armor||"Cloth",shield:"None",weapon2h:"None"};}
function escArmy(p){const b=p.board;b.armies=b.armies||[];let a=b.armies.find(x=>String(x.id)==="1");
  if(!a){a=Object.assign({id:1,label:p.name,count:ESCD.army_size,fatigue:0,open:true},escPB(p).load||escStartLoad());
    a.endurance=+((EQ.retinues[a.retinue]||{}).endurance)||0;b.armies=[a];}
  return a;}
function escRefit(p){const a=escArmy(p),L=escPB(p).load||escStartLoad();
  Object.assign(a,{retinue:L.retinue,weapon:L.weapon,weapon2h:L.weapon2h||"None",ranged:L.ranged||"None",armor:L.armor,shield:L.shield||"None",label:p.name,
    count:ESCD.army_size,fatigue:0,strained:false,blunder:false});
  if(L.b2h!=null)a.b2h=L.b2h;else delete a.b2h;
  a.endurance=+((EQ.retinues[a.retinue]||{}).endurance)||0;p.board.armies=[a];return a;}
function escInit(mode){
  while(D.players.length<2)D.players.push(newPlayer(D.players.length+1));
  D.players=D.players.slice(0,2);
  const opts={};["adv","advN","holdN","track","ai"].forEach(k=>{if(mode&&mode[k]!=null)opts[k]=mode[k];});
  D.esc={opts,round:1,phase:"loadout",score:{},hist:[],tacHist:{},shown:{},log:[],trk:{pid:null,n:0},boon:null};
  D.players.forEach(p=>{const b=p.board;withBoard(b,()=>setFaction(""));b.domains=startDoms();b.placed=[];b.armies=[];b.esc={};escRoundStart(p);escRefit(p);});
  const k=escAiKey();if(k){const ai=D.players[1];D.esc.aiPid=ai.id;ai.name="AI · "+ESCD.ai[k].label;escArmy(ai).label=ai.name;}
  D.view="esc";}
function escReset(){if(!confirm("Start the campaign over?"))return;const o=escO();D.battle=null;D.esc=null;
  D.players.forEach(p=>{if(!escIsAi(p))delete p.board.esc;});escInit(o);save();render();}
// ---- struggle track (ESCALATION_STRUGGLE): trk = {pid: whose side it is on, n: node}; boon = the loser's benefits this round
function escTrackN(){return Math.max(2,+escO().track||((ESCD.struggle||[]).length+1));}   // nodes a side; the last one loses
function escBoonKeys(k){return (ESCD.struggle||[]).slice(0,Math.min(k,escTrackN()-1)).map(x=>x.key);}
function escBoonLabel(key){return ((ESCD.struggle||[]).find(x=>x.key===key)||{}).label||key;}
function escBoon(p,key){const E=D.esc,b=E&&E.boon;return !!(b&&p&&String(b.pid)===String(p.id)&&b.r===E.round&&b.keys.includes(key));}
function escTrackMove(win){const E=D.esc,T=E.trk=E.trk||{pid:null,n:0},lose=escFoe(win);if(!lose)return null;
  if(!T.n||String(T.pid)===String(lose.id)){T.pid=lose.id;T.n++;}else{T.n--;if(!T.n)T.pid=null;}   // one node toward the loser
  return lose;}
// per-player round state: points / Holdings left this round, and a snapshot for "reset"
function escHoldN(p){return +escO().holdN+(escBoon(p,"holding")?1:0);}
function escRoundStart(p){const pb=escPB(p),o=escO();
  Object.assign(pb,{r:D.esc.round,left:+o.advN,hold:escHoldN(p),ready:false,lock:false,
    snap:{domains:clone(p.board.domains||{}),placed:clone(p.board.placed||[])}});
  if(!pb.load)pb.load=escStartLoad();}
function escLog(t){D.esc.log=(D.esc.log||[]).concat([{r:D.esc.round,t}]).slice(-60);}

// ---- Holdings: combat Holdings only; Standing requirement + one Holding on its Mastery Chain line ----
function escOwn(b){return new Set((b.placed||[]).map(x=>x.name));}
function escHoldWhy(b,n){const h=ESCD.hold[n];if(!h)return ["not a combat Holding"];const dv=b.domains||{},why=[];
  Object.keys(h.domain||{}).forEach(d=>{if(d==="*")(h.domain[d]||[]).forEach(([thr,cnt])=>{const have=DOMAINS.filter(x=>(+dv[x]||0)>=thr).length;
      if(have<cnt)why.push(cnt+" Domain"+(cnt>1?"s":"")+" "+domBand(thr));});
    else if((+dv[d]||0)<h.domain[d])why.push(domBand(h.domain[d])+" "+d);});
  if(!h.root&&!h.parents.some(q=>escOwn(b).has(q)))why.push(h.parents.join(" or "));
  return why;}
function escHoldOK(b,n){return !escOwn(b).has(n)&&!escHoldWhy(b,n).length;}
// combat text only (build cuts the rest) + the Holdings each one builds into on its Mastery Chain
function escNeeds(n){return escHoldWhy({domains:{},placed:[]},n);}
function escKids(n){return Object.keys(ESCD.hold).filter(k=>(ESCD.hold[k].parents||[]).includes(n));}
function escLeads(n){const out=[],seen=new Set([n]);let q=escKids(n);
  while(q.length){const nx=[];q.forEach(k=>{if(seen.has(k))return;seen.add(k);if((ESCD.hold[k]||{}).fx)out.push(k);else nx.push(...escKids(k));});q=nx;}
  return out;}
// a step with no combat effect of its own: what it unlocks instead
function escNoFx(n){const K=escKids(n);return K.length?'Unlocks '+K.join(", "):'no combat effect';}
function escFxHTML(n){const fx=(ESCD.hold[n]||{}).fx;return fx?'<div class="esc-fx">'+esc(fx)+'</div>':'<div class="note">'+esc(escNoFx(n))+'</div>';}
function escKidsHTML(n){const K=escKids(n);if(!K.length)return '';
  return '<div class="esc-kids"><span class="note">builds into</span>'+K.map(k=>{const fx=(ESCD.hold[k]||{}).fx,L=fx?[]:escLeads(k);
    return '<div><b>'+esc(k)+'</b>'+(fx?': '+esc(fx):L.length?' <span class="note">(leads to '+esc(L.join(", "))+')</span>':' <span class="note">'+esc(escNoFx(k))+'</span>')+'</div>';}).join("")+'</div>';}
function escPlace(p,n){const pb=escPB(p),b=p.board;if(!(pb.hold>0)||!escHoldOK(b,n))return false;
  b.placed.push({id:nextId(b.placed),name:n,sid:null,esc:D.esc.round});pb.hold--;return true;}
function escAdvance(p,d){const pb=escPB(p),b=p.board,v=+((b.domains||{})[d])||0;if(!(pb.left>0)||v>=SOV)return false;
  b.domains=b.domains||{};b.domains[d]=escO().adv==="standing"?(ESC_STEPS.find(s=>s[1]>v)||[0,SOV])[1]:v+1;pb.left--;return true;}
function escRoundReset(p){const pb=escPB(p),o=escO();if(!pb.snap)return;p.board.domains=clone(pb.snap.domains);p.board.placed=clone(pb.snap.placed);
  pb.left=+o.advN;pb.hold=escHoldN(p);pb.ready=false;}

// ---- gear: what a board may equip (the same tests the Army editor applies, locked items left out) ----
function escU(b){return withBoard(b,()=>armyUnlocks(computeEarned(new Set(Object.keys(PC))).earned));}
function escGear(b){const u=escU(b),okT=(it,n)=>tierOK(it.tier,u.wTiers)||u.anyTier.has(n);
  return {u,
    retinue:Object.keys(EQ.retinues).filter(n=>u.retinues.has(n)),
    weapon:Object.keys(EQ.weapons).filter(n=>{const it=EQ.weapons[n];return okT(it,n)&&reqMet(it,u)&&weaponUnlockMet(n,u)&&lanceOnlyOK(n,u,true);}),
    ranged:["None"].concat(Object.keys(EQ.ranged).filter(n=>u.rangedUnl.has(n)&&okT(EQ.ranged[n],n)&&reqMet(EQ.ranged[n],u))),
    armor:Object.keys(EQ.armors).filter(n=>n==="Cloth"||u.armors.has(n)),
    shield:["None"].concat(u.shields?Object.keys(EQ.shields).filter(k=>k!=="null"&&tierOK(EQ.shields[k].tier,unlockedShieldTiers(u))):[]),
    // Guige Strap: a second set beside the 1H weapon + Shield: a 2H weapon, or (Florentine) a 1H weapon to Dual Wield
    weapon2h:["None"].concat((u.mods||[]).some(m=>m.tok==="Guige Strap")?Object.keys(EQ.weapons).filter(n=>{const it=EQ.weapons[n],t=it.tags||[];
      return ((t.includes("2H")&&!EQ.prof2hOf[n])||((u.mods||[]).some(m=>m.tok==="Florentine")&&canDualWield(n)))&&okT(it,n)&&reqMet(it,u)&&weaponUnlockMet(n,u);}):[])};}
function escFixLoad(b,L){const G=escGear(b),pick=(k,v,d)=>G[k].includes(v)?v:d;
  const o={retinue:pick("retinue",L.retinue,G.retinue[0]||"Levy"),weapon:pick("weapon",EQ.prof2hOf[L.weapon]||L.weapon,G.weapon[0]||"Farm Tools"),
    ranged:pick("ranged",L.ranged||"None","None"),armor:pick("armor",L.armor,"Cloth"),shield:pick("shield",L.shield||"None","None"),
    weapon2h:pick("weapon2h",L.weapon2h||"None","None")};
  if(L.b2h!=null&&prof2h(o.weapon))o.b2h=!!L.b2h;fixWeaponNotes(o);
  // the second set needs a 1H weapon + Shield to sit beside; carrying it rules out a Ranged weapon
  if(((EQ.weapons[o.weapon]||{}).tags||[]).includes("2H")||o.shield==="None")o.weapon2h="None";
  if(o.weapon2h!=="None")o.ranged="None";
  return o;}

// ---- phases ----
function escSeizer(){const E=D.esc,last=E.hist[E.hist.length-1],ps=D.players;
  if(E.seizeR&&E.seizeR.r===E.round)return pById(E.seizeR.pid)||ps[0];
  let p=null,why="random";
  if(last&&last.win!=null){p=pById(last.win);why="last winner";}
  else if(last&&last.seize!=null){p=pById(last.seize);why="no winner: keeps it";}
  if(!p)p=ps[Math.floor(Math.random()*ps.length)];
  E.seizeR={r:E.round,pid:p.id,why};return p;}
// the Battle's terrain: the loser's pick when they hold the terrain benefit, else the centre terrain; a Hill is under the chooser's army
function escTerrain(){const E=D.esc,b=E.boon,tl=ESCD.terrains||[],pick=b&&b.r===E.round&&b.keys.includes("terrain")&&tl.includes(b.terrain)?b.terrain:null;
  return {tile:pick||ESCD.centre_terrain||"Open Field",pid:pick?b.pid:null};}
function escReveal(){const E=D.esc;
  D.players.forEach(p=>{const pb=escPB(p);pb.load=escFixLoad(p.board,pb.load||escStartLoad());escRefit(p);
    E.shown[p.id]=clone(pb.load);});
  const s=escSeizer(),o=escFoe(s);D.battle=null;const B=battle();
  B.A=Object.assign(newSide(),{pid:s.id,aid:1});B.B=Object.assign(newSide(),{pid:o.id,aid:1});B.seize="A";B.seizeSet=true;B.escR=E.round;
  const T=escTerrain();B.terrain=T.tile;B.hillX=T.tile==="Hill"&&T.pid!=null?(String(T.pid)===String(s.id)?"A":"B"):null;
  E.phase="battle";escLog("Loadouts revealed · "+s.name+" Seizes the Initiative ("+E.seizeR.why+") · "+T.tile+(T.pid!=null?" (chosen by "+((pById(T.pid)||{}).name||"?")+")":""));}
// endBattle hook: the struggle track moves toward the loser; armies are restored for the next round
function escAfterBattle(win,B){const E=D.esc;if(!E||E.phase!=="battle"||B.escR!==E.round)return;
  const sd=win==="A"||win==="B"?B[win]:null,wp=sd?pById(sd.pid):null;
  E.hist.push({r:E.round,win:wp?wp.id:null,seize:B.A.pid,load:D.players.map(p=>({pid:p.id,l:clone(escPB(p).load)})),
    left:{A:(sideArmy(B.A).a||{}).count||0,B:(sideArmy(B.B).a||{}).count||0},terrain:B.terrain||""});
  const H=E.hist[E.hist.length-1],N=escTrackN();E.boon=null;
  if(wp){E.score[wp.id]=(+E.score[wp.id]||0)+1;const lp=escTrackMove(wp),T=E.trk,onL=lp&&String(T.pid)===String(lp.id);
    if(onL&&T.n<N){E.boon={pid:lp.id,r:E.round+1,n:T.n,keys:escBoonKeys(T.n),terrain:null};}
    escLog(wp.name+" wins Battle "+E.round+" · struggle: "+(T.n?((pById(T.pid)||{}).name||"?")+"'s side, node "+T.n+"/"+N:"centre")+
      (E.boon?" · "+lp.name+": "+E.boon.keys.map(escBoonLabel).join(", "):""));}
  else escLog("Battle "+E.round+": no winner · the struggle stays");
  H.trk=clone(E.trk);
  D.players.forEach(p=>escRefit(p));
  if(wp&&E.trk.n>=N&&String(E.trk.pid)!==String(wp.id)){E.phase="done";E.champ=wp.id;}
  else{E.round++;E.phase="advance";D.players.forEach(escRoundStart);}
  D.view="esc";}
// state machine: any client may move it on (idempotent)
function escStep(){const E=D.esc;let ch=false;
  if(E.phase==="advance"&&D.players.every(p=>escPB(p).ready)){E.phase="loadout";D.players.forEach(p=>{escPB(p).lock=false;});ch=true;}
  if(E.phase==="loadout"&&D.players.every(p=>escPB(p).lock)){escReveal();D.view="battle";ch=true;}
  // revealed Tactics are public: keep each player's history (the AI's exploit reads only this)
  const B=battle();if(E.phase==="battle"&&B.id&&B.rev&&B.rev.sk===B.sk&&B.escSeen!==B.id+":"+B.sk){B.escSeen=B.id+":"+B.sk;
    ["A","B"].forEach(X=>{const pid=String(B[X].pid);E.tacHist[pid]=(E.tacHist[pid]||[]).concat([B.rev[X]]).slice(-60);});ch=true;}
  return ch;}

// ---- AI: build pool (tournament) ----
let ESC_POOL=null;
function escPool(){if(ESC_POOL)return ESC_POOL;const H=ESCD.holdNames||[];
  const rows=(ESCD.pool||[]).map(r=>({name:r[0],retinue:r[1],weapon:EQ.prof2hOf[r[2]]||r[2],shield:r[3]||"None",armor:r[4],ranged:r[5]||"None",
    hold:r[6].map(i=>H[i]),wr:r[7],weapon2h:r[8]&&EQ.weapons[r[8]]?r[8]:"None"})).filter(r=>EQ.retinues[r.retinue]&&EQ.weapons[r.weapon]&&EQ.armors[r.armor]&&
    (r.shield==="None"||EQ.shields[r.shield])&&(r.ranged==="None"||EQ.ranged[r.ranged]));
  const key=r=>ESCD.poolRated?(r.wr||0):r.hold.length;           // no tournament win rates: investment stands in
  rows.sort((a,b)=>key(a)-key(b));rows.forEach((r,i)=>{r.pct=rows.length>1?i/(rows.length-1):1;});
  ESC_POOL=rows;return rows;}
function escRow(name){return escPool().find(r=>r.name===name)||null;}
function escBucket(cfg){const [lo,hi]=cfg.bucket||[0,1];return escPool().filter(r=>r.pct>=lo&&r.pct<=hi);}
// the Standings a Holding set needs (highest Domains meet "N Domains at X")
function escNeedDoms(hold){const dv={};DOMAINS.forEach(d=>dv[d]=+ST.Untested||1);const any=[];
  hold.forEach(n=>{const h=ESCD.hold[n];if(!h)return;Object.keys(h.domain||{}).forEach(d=>{if(d==="*")any.push(...h.domain[d]);else dv[d]=Math.max(dv[d],h.domain[d]);});});
  any.sort((a,b)=>a[0]-b[0]).forEach(([thr,cnt])=>DOMAINS.slice().sort((a,b)=>dv[b]-dv[a]).slice(0,cnt).forEach(d=>{dv[d]=Math.max(dv[d],thr);}));
  return dv;}
function escAiMem(){D.esc.ai=D.esc.ai||{pivots:0,notes:[]};return D.esc.ai;}
function escAiNote(t){const m=escAiMem();m.notes=(m.notes||[]).concat([{r:D.esc.round,t}]).slice(-40);}
function escAiInitTarget(){const m=escAiMem();if(m.target&&escRow(m.target))return;const cfg=escAiCfg(),B=escBucket(cfg),L=B.length?B:escPool();
  if(!L.length){escAiNote("no tournament pool in this build: best gear each round");return;}
  const r=L[Math.floor(Math.random()*L.length)];m.target=r.name;
  escAiNote("target "+r.name+" ("+(ESCD.poolRated?"win rate "+Math.round((r.wr||0)*100)+"%, ":"")+"pct "+Math.round(r.pct*100)+")");}

// ---- AI: evaluation sandbox — sideCalc on hypothetical boards / loadouts, then everything is put back ----
let ESC_MEMO=null;const _escSideUnlocks=sideUnlocks;
sideUnlocks=function(p){if(!ESC_MEMO||!p)return _escSideUnlocks(p);const k=String(p.id);if(!ESC_MEMO.has(k))ESC_MEMO.set(k,_escSideUnlocks(p));return ESC_MEMO.get(k);};
// s = {p, hold?:[names], domains?:{}, load:{retinue,…}}
function escSandbox(sx,so,fn){const keepB=D.battle,keepSel=EQSEL,saved=[sx,so].map(s=>{const b=s.p.board;return [b,b.placed,b.domains,b.armies];});
  try{[sx,so].forEach(s=>{const b=s.p.board;if(s.hold)b.placed=s.hold.map((n,i)=>({id:i+1,name:n,sid:null}));if(s.domains)b.domains=clone(s.domains);
      const L=s.load||escStartLoad();b.armies=[Object.assign({id:1,label:s.p.name,count:s.count||ESCD.army_size,fatigue:0,
        endurance:+((EQ.retinues[L.retinue]||{}).endurance)||0},clone(L))];});
    D.battle={id:"esc-eval",sk:1,round:0,dice:true,seize:"A",seizeSet:true,A:Object.assign(newSide(),{pid:sx.p.id,aid:1}),
      B:Object.assign(newSide(),{pid:so.p.id,aid:1}),rev:null,rolls:{},log:[],start:{},terrain:ESC_EVAL_T||"",hillX:ESC_EVAL_T==="Hill"?"A":null};
    EQSEL={};ESC_MEMO=new Map();return fn();}
  finally{saved.forEach(([b,pl,dm,ar])=>{b.placed=pl;b.domains=dm;b.armies=ar;});D.battle=keepB;EQSEL=keepSel;ESC_MEMO=null;}}
// chance a Strike from side `a` gets through side d's Parry, Save and Recover
function escThrough(d){let s=aiPFail(d.save);if(d.canParry)s*=1-aiPHit(d.parryThr);if(d.recThr!=null)s*=1-aiPHit(d.recThr);return s;}
// one Skirmish's expected exchange from X's side (−1 … +1 of an army): who Strikes first thins the other's front
function escPay(X,c,oc){const B=battle(),cell=TMX[B.rev.A+"|"+B.rev.B]||[{},{}],me=cell[X==="A"?0:1]||{},them=cell[X==="A"?1:0]||{};
  if(me.no_combat||them.no_combat)return 0;
  if(me.end||them.end){const n=(c.a.count||0),on=(oc.a.count||0);return Math.max(-0.4,Math.min(0.4,(on-n)/(ESCD.army_size||25)));}   // breaking off helps whoever is behind
  let dealt=(c.blunder?0.1:1)*c.front*aiPHit(c.toStrike)*escThrough(oc),taken=(oc.blunder?0.1:1)*oc.front*aiPHit(oc.toStrike)*escThrough(c);
  if(c.I>oc.I)taken*=Math.max(0,1-dealt/Math.max(1,oc.front));else if(oc.I>c.I)dealt*=Math.max(0,1-taken/Math.max(1,c.front));
  return (dealt-taken)/Math.max(1,BT.frontMax||10);}
// the Tactic game for side X: payoff matrix over X's legal Tactics × the opponent's; the opponent's equipment is its
// default (nothing this device has selected for it is read)
function escGame(X,eqX){const B=battle(),O=X==="A"?"B":"A",T=(BT.tactics||[]).filter(t=>tacOK(X,t)),TO=(BT.tactics||[]).filter(t=>tacOK(O,t));
  const so=EQSEL[O];delete EQSEL[O];const eqO=eqCode(O);if(so)EQSEL[O]=so;
  const ex=eqX||eqCode(X),keep=B.rev,had=Object.prototype.hasOwnProperty.call(B,"rev"),P=[];
  try{T.forEach(i=>{P.push(TO.map(j=>{B.rev=X==="A"?{sk:B.sk,A:i,B:j,eqA:ex,eqB:eqO}:{sk:B.sk,A:j,B:i,eqA:eqO,eqB:ex};
      const c=sideCalc(X),oc=sideCalc(O);return c&&oc?escPay(X,c,oc):0;}));});}
  finally{if(had)B.rev=keep;else delete B.rev;}
  return {T,TO,P};}
// zero-sum equilibrium by fictitious play: x = row mix, y = column mix, val = value to the row player
function escSolve(P,iters){const m=P.length,n=m?P[0].length:0;if(!m||!n)return {x:[],y:[],val:0};const cx=Array(m).fill(0),cy=Array(n).fill(0);let i=0,j=0;
  iters=iters||ESCD.solver_iters||400;
  for(let t=0;t<iters;t++){cx[i]++;cy[j]++;let bv=-Infinity,bw=Infinity;
    for(let a=0;a<m;a++){let v=0;for(let b=0;b<n;b++)v+=P[a][b]*cy[b];if(v>bv){bv=v;i=a;}}
    for(let b=0;b<n;b++){let v=0;for(let a=0;a<m;a++)v+=P[a][b]*cx[a];if(v<bw){bw=v;j=b;}}}
  const x=cx.map(v=>v/iters),y=cy.map(v=>v/iters);let val=0;for(let a=0;a<m;a++)for(let b=0;b<n;b++)val+=x[a]*y[b]*P[a][b];return {x,y,val};}
// matchup score (−1 … +1) of state sx against so, first Skirmish, sx Seizing half the time
function escMatch(sx,so){const v=s=>escSandbox(sx,so,()=>{battle().seize=s;const g=escGame("A");return escSolve(g.P,150).val;});
  return (v("A")+v("B"))/2;}

// ---- AI: who the player is becoming (public: Holdings, Standings, last revealed loadout) ----
function escShownLoad(p){return (D.esc.shown||{})[p.id]||escPB(p).snapLoad||escStartLoad();}
function escArch(p){const own=[...escOwn(p.board)],P=escPool();let best=null,bs=-1;
  if(own.length)P.forEach(r=>{const S=new Set(r.hold),inter=own.filter(n=>S.has(n)).length,j=inter/Math.max(1,new Set(own.concat(r.hold)).size);
    if(j>bs||(j===bs&&(r.wr||0)>((best||{}).wr||0))){bs=j;best=r;}});
  const pv=ESCD.pivot||{},committed=own.length>=(pv.commit_holdings||4)&&best&&own.filter(n=>best.hold.includes(n)).length/own.length>=(pv.commit_overlap||0.5);
  return {row:committed?best:null,committed,state:committed?{p,hold:best.hold,domains:escNeedDoms(best.hold),load:{retinue:best.retinue,weapon:best.weapon,weapon2h:best.weapon2h,ranged:best.ranged,armor:best.armor,shield:best.shield}}
    :{p,load:escShownLoad(p)}};}
function escRowState(p,r){return {p,hold:r.hold,domains:escNeedDoms(r.hold),load:{retinue:r.retinue,weapon:r.weapon,weapon2h:r.weapon2h,ranged:r.ranged,armor:r.armor,shield:r.shield}};}
function escAiRetarget(ai){const cfg=escAiCfg(),m=escAiMem(),pv=ESCD.pivot||{};if(!cfg||!cfg.pivot)return;
  const dyn=cfg.pivot==="dynamic";if(!dyn&&(m.pivots||0)>=(pv.max_pivots||1))return;
  const foe=escFoe(ai),arch=escArch(foe);if(!dyn&&!arch.committed)return;
  const own=[...escOwn(ai.board)],cur=escRow(m.target),cand=escBucket(cfg).slice(-(pv.candidates||24));if(cur&&!cand.includes(cur))cand.push(cur);
  if(!cand.length)return;
  const score=r=>escMatch(escRowState(ai,r),arch.state)-(pv.switch_cost||0)*own.filter(n=>!r.hold.includes(n)).length;
  const S=cand.map(r=>({r,s:score(r)})).sort((a,b)=>b.s-a.s),cs=cur?(S.find(x=>x.r===cur)||{}).s:-Infinity,top=S[0];
  if(top.r!==cur&&top.s-cs>(dyn?0:(pv.margin||0))){m.target=top.r.name;if(!dyn)m.pivots=(m.pivots||0)+1;
    escAiNote((dyn?"counter":"pivot")+" → "+top.r.name+" ("+top.s.toFixed(2)+" vs "+(isFinite(cs)?cs.toFixed(2):"—")+") against "+(arch.row?arch.row.name:"current build"));}}

// ---- AI: advancement ----
function escAiOrder(ai,names,cfg){const b=ai.board,L=names.filter(n=>!escOwn(b).has(n));
  if(cfg.holdOrder==="random"){for(let i=L.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[L[i],L[j]]=[L[j],L[i]];}return L;}
  // "unlock": the cheapest complete path (line + Standings) to each payoff Holding (one with combat text) in the set,
  // nearest payoff first (gear unlocks break ties); its line Holdings come before it
  const own=escOwn(b),set=new Set(L),dv=b.domains||{},
    gear=n=>((ARMYSRC[n]||{}).innate||[]).some(t=>/^(tier|armor|shield|weapon|retinue|ranged):/.test(t))?0:1,
    path=(n,seen)=>{if(own.has(n)||seen.has(n))return [];seen.add(n);const h=ESCD.hold[n];if(!h)return [];
      if(h.root||h.parents.some(q=>own.has(q)))return [n];let best=null;
      h.parents.forEach(q=>{if(!ESCD.hold[q])return;const sub=path(q,new Set(seen)),len=sub.length+(set.has(q)?0:0.5);if(!best||len<best.len)best={sub,len};});
      return (best?best.sub:[]).concat([n]);},
    cost=P=>{const nd=escNeedDoms(P);return P.length*(+escO().advN||1)+DOMAINS.reduce((s,d)=>s+Math.max(0,nd[d]-(+dv[d]||0)),0);};
  const pay=L.filter(n=>ESCD.hold[n]&&ESCD.hold[n].combat).map(n=>{const P=path(n,new Set());return {n,P,c:cost(P)};}).sort((x,y)=>x.c-y.c||gear(x.n)-gear(y.n));
  const out=[];pay.forEach(x=>x.P.forEach(n=>{if(!out.includes(n))out.push(n);}));L.forEach(n=>{if(!out.includes(n))out.push(n);});
  return out.filter(n=>!own.has(n));}
function escAiAdvance(ai){const pb=escPB(ai),cfg=escAiCfg()||{},m=escAiMem(),b=ai.board;
  escAiInitTarget();try{escAiRetarget(ai);}catch(e){console.warn("esc retarget",e);}
  const tg=escRow(m.target),want=tg?tg.hold:[],order=escAiOrder(ai,want,cfg),goal=escNeedDoms(want);
  // points / Standings: the next unmet requirement of the next target Holding, then the target's Standings
  let guard=20;while(pb.left>0&&guard--){const dv=b.domains||{};let d=null;
    for(const n of order){const nd=escNeedDoms([n]),miss=DOMAINS.find(x=>(+dv[x]||0)<nd[x]);if(miss){d=miss;break;}}
    if(!d)d=DOMAINS.find(x=>(+dv[x]||0)<goal[x])||(DOMAINS.includes("Prowess")&&(+dv.Prowess||0)<SOV?"Prowess":DOMAINS.find(x=>(+dv[x]||0)<SOV));
    if(!d||!escAdvance(ai,d))break;}
  // Holdings: target Holdings now legal (lines place parents first), then the best other combat Holding
  guard=20;while(pb.hold>0&&guard--){let n=escAiOrder(ai,want,cfg).find(x=>escHoldOK(b,x));
    if(!n){const rest=Object.keys(ESCD.hold).filter(x=>escHoldOK(b,x)&&ESCD.hold[x].combat);
      n=cfg.holdOrder==="random"?rest[Math.floor(Math.random()*rest.length)]:escAiOrder(ai,rest,cfg)[0];}
    if(!n||!escPlace(ai,n))break;}
  if(escBoon(ai,"terrain")&&!D.esc.boon.terrain)try{escAiTerrain(ai);}catch(e){console.warn("esc terrain",e);}
  pb.ready=true;escAiNote("advance: "+DOMAINS.map(d=>d[0]+(b.domains[d]||0)).join(" ")+" · "+[...escOwn(b)].length+" Holdings");}
let ESC_EVAL_T=null;   // terrain for escSandbox's evaluation Battle (the AI's terrain pick)
function escAiTerrain(ai){const cfg=escAiCfg()||{},tl=ESCD.terrains||[],b=D.esc.boon;if(!tl.length)return;
  if(cfg.tactic==="random"){b.terrain=tl[Math.floor(Math.random()*tl.length)];escAiNote("terrain → "+b.terrain+" (random)");return;}
  const foe=escFoe(ai),me={p:ai,load:escPB(ai).load||escStartLoad()},them={p:foe,load:escShownLoad(foe)};
  const S=tl.map(t=>{ESC_EVAL_T=t;try{return {t,v:escMatch(me,them)};}finally{ESC_EVAL_T=null;}}).sort((x,y)=>y.v-x.v);
  b.terrain=S[0].t;escAiNote("terrain → "+b.terrain+" ("+S.map(x=>x.t+" "+x.v.toFixed(2)).join(", ")+")");}

// ---- AI: loadout ----
function escRank(kind,n){if(kind==="retinue"){const r=EQ.retinues[n]||{};return (+r.cost||0)*10-(+r.to_hit||9);}
  if(kind==="ranged"){const r=EQ.ranged[n];return r?((EQ.tiers||[]).indexOf(r.tier)*100-(+r.ap||0)):-1;}return aiGearRank(kind,n);}
function escBest(G,kind){return G[kind].slice().sort((a,b)=>escRank(kind,b)-escRank(kind,a))[0];}
function escAiLoad(ai){const cfg=escAiCfg()||{},m=escAiMem(),b=ai.board,G=escGear(b),tg=escRow(m.target);
  const has=(k,v)=>G[k].includes(v),pick=(k,v)=>v&&has(k,v)?v:null;
  const base={retinue:pick("retinue",tg&&tg.retinue)||escBest(G,"retinue"),armor:pick("armor",tg&&tg.armor)||escBest(G,"armor"),
    weapon:pick("weapon",tg&&tg.weapon),shield:pick("shield",tg&&tg.shield),ranged:pick("ranged",tg&&tg.ranged),weapon2h:pick("weapon2h",tg&&tg.weapon2h)||"None"};
  if(!base.weapon){const is2=n=>((EQ.weapons[n]||{}).tags||[]).includes("2H"),want2=tg&&is2(tg.weapon),L=G.weapon.filter(n=>!want2||is2(n));
    base.weapon=(L.length?L:G.weapon).sort((a,b)=>escRank("weapon",b)-escRank("weapon",a))[0]||"Farm Tools";}
  if(base.shield==null)base.shield=((EQ.weapons[base.weapon]||{}).tags||[]).includes("2H")?"None":escBest(G,"shield");
  if(base.ranged==null)base.ranged=tg&&tg.ranged!=="None"?escBest(G,"ranged"):"None";
  let L=escFixLoad(b,base),why="target gear";
  if(cfg.gear==="counter"){const foe=escFoe(ai),fs={p:foe,load:escShownLoad(foe)},K=ESCD.gear_candidates||12;
    const W=G.weapon.slice().sort((a,b)=>escRank("weapon",b)-escRank("weapon",a)).slice(0,8),R=G.retinue.slice().sort((a,b)=>escRank("retinue",b)-escRank("retinue",a)).slice(0,2),
      SH=["None",escBest(G,"shield")].filter((x,i,a)=>x&&a.indexOf(x)===i),RG=["None",escBest(G,"ranged")].filter((x,i,a)=>x&&a.indexOf(x)===i);
    const C=[];R.forEach(r=>W.forEach(w=>SH.forEach(s=>RG.forEach(g=>C.push(escFixLoad(b,{retinue:r,weapon:w,shield:s,ranged:g,armor:base.armor}))))));
    C.push(L);const seen=new Set(),U=C.filter(x=>{const k=JSON.stringify(x);if(seen.has(k))return false;seen.add(k);return true;});
    const quick=U.map(x=>({x,q:escSandbox({p:ai,load:x},fs,()=>{const c=sideCalc("A"),oc=sideCalc("B");battle().rev={sk:1,A:"Fighting Formation",B:"Fighting Formation"};
      const c2=sideCalc("A"),oc2=sideCalc("B");return c&&oc&&c2&&oc2?escPay("A",c2,oc2):-9;})})).sort((a,b)=>b.q-a.q).slice(0,K);
    const full=quick.map(o=>({x:o.x,v:escMatch({p:ai,load:o.x},fs)})).sort((a,b)=>b.v-a.v);
    if(full.length){L=full[0].x;why="counter to "+[fs.load.retinue,fs.load.weapon,fs.load.armor].join("/")+" ("+full[0].v.toFixed(2)+")";}}
  escPB(ai).load=L;escPB(ai).lock=true;escAiNote("loadout "+[L.retinue,L.weapon+(escW2Txt(L)?" | "+escW2Txt(L):""),L.ranged!=="None"?L.ranged:"",L.armor,L.shield!=="None"?L.shield:""].filter(Boolean).join(", ")+" · "+why);}

// ---- AI: Battle (Tactic + equipment each Skirmish, then its own rolls) ----
function escAiSide(){const B=battle();return ["A","B"].find(X=>B[X]&&escIsAi(pById(B[X].pid)))||null;}
function escAiTactic(X){const cfg=escAiCfg()||{},B=battle(),O=X==="A"?"B":"A";
  if(cfg.tactic==="random"){const pool=randomTacticPool(X);return {t:pool[Math.floor(Math.random()*pool.length)],why:"random"};}
  const eo=eqOptions(X),modes=[];eo.opts.forEach(m=>{modes.push({mode:m});if(eo.bastard&&m==="melee")modes.push({mode:m,b2h:true});});
  let best=null;modes.forEach(e=>{EQSEL[X]=e;const g=escGame(X),s=escSolve(g.P);if(!best||s.val>best.s.val)best={e,g,s};});
  EQSEL[X]=best.e;const {g,s}=best;let x=s.x.slice();
  if(cfg.tactic==="mixed"){const nz=+cfg.noise||0;x=x.map(v=>(1-nz)*v+nz/x.length);}
  const H=((D.esc.tacHist||{})[String(B[O].pid)]||[]),ex=+cfg.exploit||0;
  if(ex>0&&H.length>=(ESCD.exploit_min_reveals||3)){const q=g.TO.map(t=>1+H.filter(h=>h===t).length),qs=q.reduce((a,b)=>a+b,0);
    const br=g.P.map(row=>row.reduce((a,v,j)=>a+v*q[j]/qs,0)),bi=br.indexOf(Math.max(...br));x=x.map((v,i)=>(1-ex)*v+(i===bi?ex:0));}
  let r=Math.random(),i=0;for(;i<x.length-1;i++){r-=x[i];if(r<=0)break;}
  return {t:g.T[i],why:cfg.tactic+" · value "+s.val.toFixed(2)+" · "+g.T.map((t,k)=>t+" "+Math.round(x[k]*100)+"%").filter(z=>!/ 0%$/.test(z)).join(", ")};}
let ESC_AI_T=null;
function escAiBattle(){const B=battle(),X=escAiSide();if(!B.id||!X||ESC_AI_T)return;const ms=ESCD.ai_step_ms||450;
  const bid=B.id,go=f=>{ESC_AI_T=setTimeout(()=>{ESC_AI_T=null;const B2=battle();if(!B2.id||B2.id!==bid||D.esc.phase!=="battle"||!escAiSide())return;
    try{f();}catch(e){console.warn("esc ai",e);}},ms);};
  if(!(B.rev&&B.rev.sk===B.sk)){const key=B.id+":"+pickKey();if((PICKS[X]||{}).picked||B.escAiPk===key)return;
    go(()=>{if(B.escAiPk===key)return;B.escAiPk=key;const r=escAiTactic(X);escAiNote("S"+B.sk+" Tactic → "+r.t+" ("+r.why+")");pickTactic(X,r.t);});return;}
  if(battleOutcome()&&!battleOwed())return;   // decided: the AI still rolls anything it owes first
  const rp=B.endRep&&B.endRep.sk===B.sk&&B.endRep.rows.find(r=>r.X===X&&brkPending(r));if(rp){go(()=>rollBreakBtn(X));return;}
  const fl=bFlow();if(!fl)return;const k=fl.can[X],c=sideCalc(X);
  const st=(B.strk||{})[X],act=k.strike?()=>roll(X,"Strike"):k.cleave?()=>roll(X,"Cleave"):
    k.parry?()=>roll(X,"Parry"):k.save?()=>roll(X,"Save"):k.recover?()=>roll(X,"Recover"):
    k.rip?()=>{if(c.canParry)roll(X,"RipParry");roll(X,"RipSave");}:k.apply?()=>{applyCas(X,pendCas(X));save();render();}:
    k.panic?()=>roll(X,"Morale"):k.brk?()=>roll(X,"Break"):null;
  if(act)go(act);}
function escAiTick(){const ai=escAiP(),E=D.esc;if(!ai||!escDriver())return false;let ch=false;
  if(E.phase==="advance"&&!escPB(ai).ready){escAiAdvance(ai);ch=true;}
  if(E.phase==="loadout"&&!escPB(ai).lock){escAiInitTarget();escAiLoad(ai);ch=true;}
  if(E.phase==="battle"&&D.view==="battle")escAiBattle();
  return ch;}
let ESC_BUSY=false;
function escAfterRender(){if(ESC_BUSY||!escOn())return;ESC_BUSY=true;
  try{let ch=escStep();if(escAiTick())ch=true;if(escStep())ch=true;if(ch){save();setTimeout(()=>{ESC_BUSY=false;render();},0);return;}}
  catch(e){console.warn("escalation",e);}ESC_BUSY=false;}

// ---- view ----
function escW2Txt(L){const n=L&&L.weapon2h;return n&&n!=="None"?(((EQ.weapons[n]||{}).tags||[]).includes("2H")?n:"2× "+n):"";}
function escLoadTxt(L){return L?[L.retinue,(L.weapon||"")+(L.b2h&&prof2h(L.weapon)?" (2H)":"")+(escW2Txt(L)?" | "+escW2Txt(L):""),L.ranged&&L.ranged!=="None"?L.ranged:"",L.armor,L.shield&&L.shield!=="None"?L.shield:""].filter(Boolean).map(esc).join(" · "):"—";}
function escTok(t){const m=/^(tier|armor|shield|weapon|retinue|anytier|ranged):(.+)$/.exec(t);if(!m)return t;
  return m[1]==="tier"?m[2]+" weapons":m[1]==="armor"?m[2]+" armor":m[1]==="shield"?m[2]+" shields":m[1]==="retinue"?m[2]:m[1]==="weapon"||m[1]==="ranged"?m[2]:"";}
function escSideHTML(p,me){const b=p.board,u=escU(b),pb=escPB(p),foeView=!sameP(p,me),E=D.esc;
  const stand=DOMAINS.map(d=>{const v=+((b.domains||{})[d])||0;return '<span class="kw" title="'+esc(d+" "+v)+'">'+esc(d)+' '+v+' <span style="opacity:.6">'+esc(domBand(v))+'</span></span>';}).join(" ");
  const fx=standingFxOf(b.domains||{}).map(f=>'<span class="kw mod" title="'+esc(f.t+" "+f.d)+'">'+esc(f.text)+'</span>').join(" ");
  const hold=[...escOwn(b)].map(n=>'<span class="kw'+(ESCD.hold[n]&&ESCD.hold[n].monument?' mod':'')+'" title="'+esc((ESCD.hold[n]||{}).fx||"")+'">'+esc(n)+'</span>').join(" ");
  const wt=[...u.wTiers].sort((a,b)=>TIER_RANK[a]-TIER_RANK[b]).join(", ");
  const mods=u.mods.map(m=>'<span class="kw mod" data-tok="'+esc(m.tok)+'" title="'+esc(gloss(m.tok))+'">'+esc(m.tok)+' <span style="opacity:.6">('+esc(m.node)+')</span></span>').join(" ");
  const row=(k,v)=>'<div class="kv"><span class="k">'+k+'</span><span class="val" style="text-align:right">'+(v||'<span class="note">none</span>')+'</span></div>';
  return '<div class="tot esc-side"><h3 style="font-size:14px">'+esc(p.name)+(escIsAi(p)?' <span class="badge tier">AI</span>':'')+
    (E.trk&&E.trk.n&&String(E.trk.pid)===String(p.id)?' <span class="badge earn">struggle on their side: node '+E.trk.n+'/'+escTrackN()+'</span>':'')+'</h3>'+
    row("Standings",stand)+row("Battle effects",fx)+row("Holdings",hold)+
    row("Retinues",esc([...u.retinues].join(", ")))+row("Weapon tiers",esc(wt))+row("Armor",esc([...u.armors].join(", ")))+
    row("Shields",u.shields?esc([...unlockedShieldTiers(u)].join(", ")):"")+row("Ranged",esc([...u.rangedUnl].join(", ")))+
    row("Modifiers",mods)+row(foeView?"Last revealed":"Loadout",foeView?escLoadTxt(E.shown[p.id]):escLoadTxt(pb.load))+'</div>';}
function escAdvHTML(p){const pb=escPB(p),b=p.board,o=escO(),mineP=!escIsAi(p);
  if(pb.ready)return '<div class="note">Ready. Waiting for '+esc((escFoe(p)||{}).name||"opponent")+'.</div><button data-esc="unready">change</button>';
  const unit=o.adv==="standing"?"Standing":"Domain Point";
  let h='<div class="esc-row"><b>'+pb.left+'</b> '+unit+(pb.left===1?'':'s')+' · <b>'+pb.hold+'</b> Holding'+(pb.hold===1?'':'s')+' left</div><div class="esc-doms">';
  DOMAINS.forEach(d=>{const v=+((b.domains||{})[d])||0,nx=o.adv==="standing"?(ESC_STEPS.find(s=>s[1]>v)||[null,null]):[null,Math.min(SOV,v+1)];
    h+='<div class="esc-dom" style="--dc:'+(DOMC[d]||"var(--dim)")+'"><b>'+esc(d)+'</b> <span>'+v+' · '+esc(domBand(v))+'</span>'+
      (mineP?'<button data-esc="dom" data-d="'+esc(d)+'"'+(pb.left>0&&v<SOV?'':' disabled')+'>+ '+(o.adv==="standing"?esc(nx[0]||"max"):"1")+'</button>':'')+'</div>';});
  h+='</div>';
  const own=escOwn(b),all=Object.keys(ESCD.hold).filter(n=>!own.has(n)),ok=all.filter(n=>escHoldOK(b,n)),no=all.filter(n=>!escHoldOK(b,n));
  const card=(n,can)=>{const h_=ESCD.hold[n],why=can?[]:escHoldWhy(b,n);
    return '<div class="esc-hold'+(can?'':' off')+(h_.monument?' mon':'')+'"><div><b>'+esc(n)+'</b>'+(h_.monument?' <span class="badge tier">Monument</span>':'')+
      escFxHTML(n)+escKidsHTML(n)+(why.length?'<div class="note neg">needs '+esc(why.join(" · "))+'</div>':'')+'</div>'+
      (can?'<button data-esc="hold" data-n="'+esc(n)+'"'+(pb.hold>0?'':' disabled')+'>place</button>':'')+'</div>';};
  h+='<div class="lbl" style="margin-top:8px">HOLDINGS YOU CAN PLACE</div><div class="esc-holds">'+(ok.map(n=>card(n,true)).join("")||'<div class="note">none</div>')+'</div>'+
    '<details style="margin-top:6px"><summary class="note" style="cursor:pointer">locked ('+no.length+')</summary><div class="esc-holds">'+no.map(n=>card(n,false)).join("")+'</div></details>';
  const added=(b.placed||[]).filter(x=>x.esc===D.esc.round).map(x=>x.name);
  h+='<div class="esc-row" style="margin-top:8px">'+(added.length?'<span class="note">placed: '+esc(added.join(", "))+'</span>':'')+
    '<button data-esc="rreset">reset round</button><button class="go" data-esc="ready">Ready ▸</button></div>';
  return h;}
function escLoadHTML(p){const pb=escPB(p),G=escGear(p.board),L=escFixLoad(p.board,pb.load||escStartLoad());pb.load=L;
  if(pb.lock)return '<div class="note">Loadout locked: '+escLoadTxt(L)+'. Waiting for '+esc((escFoe(p)||{}).name||"opponent")+'.</div><button data-esc="unlock">change</button>';
  const sel=(k,lab,off)=>'<label class="fld"><span class="note">'+lab+'</span><select data-esc-l="'+k+'"'+(off?' disabled':'')+'>'+G[k].map(n=>{const it=k==="retinue"?null:(k==="shield"?EQ.shields[n]:EQ[k==="weapon"||k==="weapon2h"?"weapons":k==="ranged"?"ranged":"armors"][n]);
    const pair=k==="weapon2h"&&it&&!(it.tags||[]).includes("2H");   // Florentine pair
    return '<option value="'+esc(n)+'"'+(L[k]===n?' selected':'')+'>'+esc(n)+(pair?' ×2 (Florentine)':'')+(it&&it.tier?' ['+esc(it.tier_label||it.tier)+']':'')+'</option>';}).join("")+'</select></label>';
  const no2=((EQ.weapons[L.weapon]||{}).tags||[]).includes("2H")||L.shield==="None";   // Guige Strap's second set sits beside a 1H weapon + Shield
  // Secondary: a Ranged weapon, or (Guige Strap, beside a 1H weapon + Shield) a 2H weapon or a Florentine 1H pair
  const tl=it=>it&&it.tier?' ['+esc(it.tier_label||it.tier)+']':'',cur=secondaryValue(L),opt=(v,t)=>'<option value="'+esc(v)+'"'+(cur===v?' selected':'')+'>'+t+'</option>',
    rg=G.ranged.filter(n=>n!=="None"),w2=no2?[]:G.weapon2h.filter(n=>n!=="None"),two=n=>((EQ.weapons[n]||{}).tags||[]).includes("2H"),
    grp=(lab,L2,f)=>L2.length?'<optgroup label="'+esc(lab)+'">'+L2.map(f).join("")+'</optgroup>':'';
  const sec='<label class="fld"><span class="note">Secondary</span><select data-esc-l="secondary">'+opt("None","None")+
    grp("Ranged",rg,n=>opt("r:"+n,esc(n)+tl(EQ.ranged[n])))+grp("2H Weapon (Guige Strap)",w2.filter(two),n=>opt("w:"+n,esc(n)+tl(EQ.weapons[n])))+
    grp("Florentine pair (Guige Strap)",w2.filter(n=>!two(n)),n=>opt("w:"+n,esc(n)+' ×2'+tl(EQ.weapons[n])))+'</select></label>';
  const w=EQ.weapons[L.weapon]||{},ar=EQ.armors[L.armor]||{},rt=EQ.retinues[L.retinue]||{},sh=EQ.shields[L.shield==="None"?"null":L.shield]||{};
  return '<div class="esc-load">'+sel("retinue","Retinue")+sel("weapon","Main")+
    (prof2h(L.weapon)?'<label class="fld"><span class="note">Grip</span><select data-esc-l="b2h"><option value="0"'+(L.b2h?'':' selected')+'>1H</option><option value="1"'+(L.b2h?' selected':'')+'>2H</option></select></label>':'')+
    sec+sel("armor","Armor")+sel("shield","Shield")+'</div>'+
    (G.weapon2h.length>1&&no2?'<div class="note">Guige Strap: pick a 1H Main weapon and a Shield to carry a 2H weapon or pair as Secondary.</div>':'')+
    '<div class="note">to Strike '+(rt.to_hit||"?")+'+ · Morale '+(rt.shaking||"?")+'+ · Endurance '+(rt.endurance||"?")+' · AP '+(w.ap||0)+' · Init '+((w.init||0)+(sh.init||0))+
    ' · Save '+(ar.save||"?")+'+'+(sh.save_bonus?' (shield +'+sh.save_bonus+')':'')+((w.tags||[]).length?' · '+esc(w.tags.join(", ")):'')+'</div>'+
    '<div class="esc-row"><button class="go" data-esc="lock">Lock loadout ▸</button></div>';}
// the struggle track: players[0]'s losing node on the left, players[1]'s on the right, the tracker where it stands
function escTrackHTML(){const E=D.esc,ps=D.players,N=escTrackN(),T=E.trk||{pid:null,n:0};if(ps.length<2)return "";
  const pos=!T.n?0:(String(T.pid)===String(ps[0].id)?-T.n:T.n),col=i=>i<0?ps[0].color:i>0?ps[1].color:"var(--dim)";
  const tip=i=>{const k=Math.abs(i),who=i<0?ps[0]:ps[1];if(!k)return "centre";if(k>=N)return who.name+" loses the campaign";
    return who.name+"'s side, node "+k+": "+escBoonKeys(k).map(escBoonLabel).join(", ");};
  let h='';for(let i=-N;i<=N;i++)h+='<span class="esc-node'+(i===pos?' on':'')+(Math.abs(i)===N?' end':'')+'" style="--pc:'+esc(col(i))+'" title="'+esc(tip(i))+'">'+(Math.abs(i)===N?'✝':i?Math.abs(i):'·')+'</span>';
  return '<div class="esc-trackrow"><b style="color:'+esc(ps[0].color)+'">'+esc(ps[0].name)+'</b><div class="esc-track">'+h+'</div><b style="color:'+esc(ps[1].color)+'">'+esc(ps[1].name)+'</b></div>';}
// this round's benefits (the loser's), with the terrain pick for its holder
function escBoonHTML(me){const E=D.esc,b=E.boon;if(!b||b.r!==E.round||E.phase==="done")return "";const p=pById(b.pid);if(!p)return "";
  const mine=me&&String(me.id)===String(p.id)&&!escIsAi(p),open=E.phase==="advance"||E.phase==="loadout",tl=ESCD.terrains||[];
  let h='<div class="tot esc-boon" style="border-color:'+esc(p.color||"var(--line2)")+'"><b>'+esc(p.name)+'</b> · struggle node '+b.n+': '+b.keys.map(k=>esc(escBoonLabel(k))).join(" · ");
  if(b.keys.includes("terrain")){const cur=tl.includes(b.terrain)?b.terrain:"",TT=TREF.tactical||{};
    if(mine&&open)h+='<div class="esc-row"><label class="fld"><span class="note">Terrain for Battle '+E.round+'</span><select data-esc-t="1">'+
      tl.map(t=>'<option value="'+esc(t)+'"'+((cur||ESCD.centre_terrain)===t?' selected':'')+'>'+esc(t)+'</option>').join("")+'</select></label>'+
      (cur&&TT[cur]?'<span class="note">'+esc(TT[cur].effect||"")+(cur==="Hill"?' (your army)':'')+'</span>':'')+'</div>';
    else h+='<div class="note">Terrain: '+esc(cur||(E.phase==="battle"?(battle().terrain||""):"not chosen yet"))+'</div>';}
  return h+'</div>';}
function escPaneHTML(){const E=D.esc,o=escO(),me=escMe(),foe=escFoe(me),ps=D.players;
  const ph={advance:"Advance",loadout:"Loadouts",battle:"Battle",done:"Campaign over"}[E.phase]||E.phase;
  let h='<div class="bm-card esc"><div class="esc-top"><h2>Escalation</h2><span class="badge tier">Round '+E.round+'</span><span class="badge earn">'+esc(ph)+'</span>'+
    '<span class="note">'+esc((o.adv==="standing"?o.advN+" Standing":o.advN+" Domain Point")+(+o.advN>1?"s":"")+" · "+o.holdN+" Holding"+(+o.holdN>1?"s":"")+" per round · the last winner Seizes")+'</span></div>'+
    escTrackHTML()+escBoonHTML(me);
  if(!me){return h+'<div class="note">Pick your seat in the top bar.</div></div>';}
  h+='<div class="tot esc-phase">';
  if(E.phase==="done"){const w=pById(E.champ);h+='<div class="bcmd-t">'+esc(w?w.name:"?")+' wins the campaign</div><button data-esc="again">Play again</button>';}
  else if(E.phase==="battle"){const s=pById((E.seizeR||{}).pid);h+='<div><b>Battle '+E.round+'</b> · '+esc(s?s.name:"?")+' Seizes the Initiative ('+esc((E.seizeR||{}).why||"")+')</div><button class="go" data-esc="tobattle">Go to Battle ▸</button>';}
  else{const st=q=>E.phase==="advance"?(escPB(q).ready?"ready":"advancing"):(escPB(q).lock?"locked":"choosing");
    h+='<div class="note" style="margin-bottom:6px">'+esc(foe?foe.name:"")+': '+esc(foe?st(foe):"")+'</div>'+(E.phase==="advance"?escAdvHTML(me):escLoadHTML(me));}
  h+='</div><div class="esc-sides">'+[me].concat(foe?[foe]:[]).map(p=>escSideHTML(p,me)).join("")+'</div>';
  if(E.hist.length)h+='<div class="tot"><div class="lbl">BATTLES</div><table class="dtable" style="font-size:12px"><thead><tr><th>#</th><th>Seized</th><th>Winner</th><th>Left</th>'+
    ps.map(p=>'<th>'+esc(p.name)+'</th>').join("")+'</tr></thead><tbody>'+E.hist.map(x=>'<tr><td>'+x.r+'</td><td>'+esc((pById(x.seize)||{}).name||"")+'</td><td>'+esc(x.win!=null?(pById(x.win)||{}).name||"":"—")+'</td><td>'+x.left.A+' / '+x.left.B+'</td>'+
      ps.map(p=>'<td>'+escLoadTxt((x.load.find(l=>String(l.pid)===String(p.id))||{}).l)+'</td>').join("")+'</tr>').join("")+'</tbody></table></div>';
  if(E.log&&E.log.length)h+='<details class="tot"><summary class="note" style="cursor:pointer">Log</summary><div class="note">'+E.log.slice().reverse().map(x=>'R'+x.r+': '+esc(x.t)).join('<br>')+'</div></details>';
  const m=E.ai;if(m&&m.notes&&m.notes.length)h+='<details class="tot"><summary class="note" style="cursor:pointer">AI log</summary><div class="note">'+
    (escAiCfg()?esc(escAiCfg().label)+' · pool: '+esc(ESCD.poolSrc||"none")+(ESCD.poolRated?'':' (no win rates)')+'<br>':'')+m.notes.slice().reverse().map(x=>'R'+x.r+': '+esc(x.t)).join('<br>')+'</div></details>';
  h+='<div class="esc-row" style="margin-top:8px"><button data-esc="restart">restart campaign</button></div>';
  return h+'</div>';}
function escWire(host){
  host.querySelectorAll("[data-esc]").forEach(b=>b.onclick=()=>{const k=b.dataset.esc,me=escMe(),pb=me?escPB(me):null;
    if(k==="dom"&&me)escAdvance(me,b.dataset.d);
    else if(k==="hold"&&me){if(!escPlace(me,b.dataset.n))flash("can't place "+b.dataset.n);}
    else if(k==="rreset"&&me)escRoundReset(me);
    else if(k==="ready"&&pb){if((pb.left>0||pb.hold>0)&&!confirm("Unused this round: "+pb.left+" point(s), "+pb.hold+" Holding(s). Ready anyway?"))return;pb.ready=true;}
    else if(k==="unready"&&pb&&D.esc.phase==="advance")pb.ready=false;
    else if(k==="lock"&&pb){pb.load=escFixLoad(me.board,pb.load||escStartLoad());pb.lock=true;}
    else if(k==="unlock"&&pb&&D.esc.phase==="loadout")pb.lock=false;
    else if(k==="tobattle")D.view="battle";
    else if(k==="again"||k==="restart"){escReset();return;}
    save();render();});
  host.querySelectorAll("[data-esc-t]").forEach(s=>s.onchange=()=>{const me=escMe(),b=D.esc.boon;if(!me||!b||String(b.pid)!==String(me.id))return;
    b.terrain=s.value||null;escLog(me.name+" picks the terrain: "+(b.terrain||ESCD.centre_terrain||"Open Field"));save();render();});
  host.querySelectorAll("[data-esc-l]").forEach(s=>s.onchange=()=>{const me=escMe();if(!me)return;const pb=escPB(me),k=s.dataset.escL;
    pb.load=Object.assign({},pb.load,k==="b2h"?{b2h:s.value==="1"}:k==="secondary"?{}:{[k]:s.value});if(k==="secondary")setSecondary(pb.load,s.value);
    pb.load=escFixLoad(me.board,pb.load);save();render();});
  wireDashExtras(host);}
function escSeizeHTML(){const E=D.esc,B=battle(),f=seizeForced(),s=f?f:"A",ready=!!(sideCalc("A")&&sideCalc("B"));
  return '<div class="bcmd bseizebox"><div class="bcmd-t">Battle '+E.round+'</div><div>'+esc(sideNm(s))+' Seizes the Initiative'+(f?' (Ministry)':' ('+esc((E.seizeR||{}).why||"")+')')+'</div>'+
    '<button id="bStartGo" class="bstart'+(ready?' go':'')+'"'+(ready?'':' disabled')+'>Start battle</button></div>';}
function escReferenceHTML(){return '<div style="padding:14px"><h2 style="margin-bottom:8px">Combat reference</h2><div id="refStanding">'+standingEffectsHTML()+'</div><div id="refBattle">'+battleRulesHTML()+'</div>'+escHoldRefHTML()+escArmoryHTML()+'</div>';}
// Combat Holdings as the Pursuit tree's flow charts (one per root), cut to the combat Holdings and the steps toward them;
// each box shows its unlock and its combat effect. The table stays below as a list.
function escHoldRefHTML(){const AL=DATA.aliases||{},dn=n=>AL[n]||n,H=Object.keys(ESCD.hold).sort((a,b)=>dn(a).localeCompare(dn(b)));   // order by the name players read
  const tree=DATA.tree?treeHTML({only:new Set(H),need:n=>!!(ESCD.hold[n]||{}).fx,body:n=>{const fx=(ESCD.hold[n]||{}).fx;return fx?kwify(fx,n):'<span class="note">'+esc(escNoFx(n))+'</span>';}}):'';
  return (tree?'<details id="refTree" class="tot" open><summary><b>Combat Holdings</b> <span class="note">one chart per root Holding · arrows = builds into</span></summary>'+
      '<div class="tb-row" style="margin:6px 0"><button data-tree="open">expand all</button><button data-tree="close">collapse all</button></div>'+tree+'</details>':'')+
    '<details class="tot"'+(tree?'':' open')+'><summary><b>Combat Holdings</b> <span class="note">as a list</span></summary><div style="overflow-x:auto"><table class="dtable esc-reft" style="font-size:12px"><thead><tr><th></th><th>Needs</th><th>Combat effect</th><th>Builds into</th></tr></thead><tbody>'+
    H.map(n=>{const h=ESCD.hold[n],nd=escNeeds(n);
      return '<tr><td><b>'+esc(n)+'</b>'+(h.monument?' <span class="badge tier">Monument</span>':'')+'</td><td>'+esc(nd.join(" · ")||"—")+'</td><td>'+escFxHTML(n)+'</td><td>'+(escKidsHTML(n)||'<span class="note">—</span>')+'</td></tr>';}).join("")+
    '</tbody></table></div></details>';}
function escArmoryHTML(){const t=(title,o,cols,f)=>'<details class="tot"><summary><b>'+title+'</b></summary><div style="overflow-x:auto"><table class="dtable" style="font-size:12px"><thead><tr><th></th>'+cols.map(c=>'<th>'+c+'</th>').join("")+'</tr></thead><tbody>'+
    Object.keys(o).filter(n=>n!=="null").map(n=>'<tr><td><b>'+esc(n)+'</b></td>'+f(o[n]).map(v=>'<td>'+esc(v==null?"":String(v))+'</td>').join("")+'</tr>').join("")+'</tbody></table></div></details>';
  return t("Retinues",EQ.retinues,["to Strike","Morale","Endurance"],r=>[r.to_hit+"+",r.shaking+"+",r.endurance])+
    t("Weapons",EQ.weapons,["Tier","AP","Init","Keywords"],w=>[w.tier_label||w.tier,w.ap||0,w.init||0,(w.tags||[]).join(", ")])+
    t("Ranged",EQ.ranged,["Tier","AP","Init","Keywords"],w=>[w.tier_label||w.tier,w.ap||0,w.init||0,(w.tags||[]).join(", ")])+
    t("Armor",EQ.armors,["Tier","Save"],a=>[a.tier_label||a.tier,a.save+"+"])+
    t("Shields",EQ.shields,["Tier","Save","Init","Keywords"],s=>[s.tier_label||s.tier,"+"+(s.save_bonus||0),s.init||0,(s.tags||[]).join(", ")]);}
// render(): Escalation shows only Campaign | Battle | Reference
function escRoute(view){const v=["esc","battle","reference"].includes(view)?view:"esc";D.view=v;
  document.body.classList.add("esc-on");
  [["viewBattle","battle"],["viewReference","reference"],["viewEsc","esc"]].forEach(([id,k])=>{const el=document.getElementById(id);if(el)el.style.display=v===k?"":"none";});
  ["appBoard","viewTable"].forEach(id=>{const el=document.getElementById(id);if(el)el.style.display="none";});
  document.querySelectorAll(".vtab,#tabbar [data-v]").forEach(t=>t.classList.toggle("on",t.dataset.v===v));
  const vb=document.getElementById("vtBattle");if(vb)vb.hidden=false;const ve=document.getElementById("vtEsc");if(ve)ve.hidden=false;
  try{renderInbox();renderChrome();}catch(e){}
  if(v==="battle"){try{renderBattle();}catch(e){console.error("battle",e);}}
  else if(v==="reference"){const host=document.getElementById("viewReference");host.innerHTML=escReferenceHTML();wireDashExtras(host);}
  else{const host=document.getElementById("viewEsc");host.innerHTML=escPaneHTML();escWire(host);}
  setTimeout(escAfterRender,0);}
