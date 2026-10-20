// parity_efx.js — replays effect_registry.py's patterns with JavaScript RegExp, the way the board used to read text at
// runtime, and compares with the hits Python shipped in DATA.efx. Exit 1 on any difference.
//   node parity_efx.js settlement_board.html [python]      (run from references/; python defaults to "python")
// The board's DATA is read from the built page; the patterns from effect_registry.REG (via python).
const fs=require("fs"),path=require("path"),{execFileSync}=require("child_process");
const html=fs.readFileSync(process.argv[2],"utf8"),m=/const DATA = (\{[\s\S]*?\});\nconst R = DATA/.exec(html);
if(!m){console.log("DATA not found in "+process.argv[2]);process.exit(2);}
const D=JSON.parse(m[1]);
const REG=JSON.parse(execFileSync(process.argv[3]||"python",["-c","import sys,json;sys.path.insert(0,sys.argv[1]);import effect_registry as E;print(json.dumps({k:list(v) for k,v in E.REG.items()}))",__dirname],{encoding:"utf8"}));
const R=D.records,INFRA=D.infra,WON=D.wonders,FAC=D.factions||{},EFX=D.efx||{};
const src=[];
Object.keys(R).forEach(n=>{src.push(["h:"+n,n,"h",R[n].innate_raw||""]);if(R[n].mastery_raw)src.push(["hm:"+n,n,"hm",R[n].mastery_raw]);});
Object.keys(INFRA).forEach(n=>src.push(["i:"+n,n,"i",INFRA[n].effect_raw||""]));
Object.keys(WON).forEach(n=>src.push(["w:"+n,n,"w",WON[n].effect_raw||""]));
Object.keys(FAC).forEach(n=>{const m=String(FAC[n].mechanic||"");if(!m)return;src.push(["f:"+n,n,"f",m.replace(/\*\*/g,"")]);src.push(["F:"+n,n,"F",m]);});
const norm=a=>JSON.stringify(a,(k,v)=>v===undefined?null:v);
const arr=m=>Array.from(m);
let bad=0,checked=0;
function cmp(key,id,js,py){checked++;if(norm(js)!==norm(py||[])){bad++;if(bad<=25)console.log("DIFF",key,id,"\n  js:",norm(js),"\n  py:",norm(py||[]));}}
const kindLetter=k=>k==="hm"?"M":k;
src.forEach(([key,name,kind,text])=>{const E=EFX[key]||{};
  Object.keys(REG).forEach(id=>{const [sc,kinds,p]=REG[id];if(!kinds.includes(kindLetter(kind)))return;
    let hits=[];
    if(sc==="clause")String(text).split(/;|\.\s+|\.$/).forEach(c=>{const m=new RegExp(p,"i").exec(c.trim());if(m)hits.push(arr(m));});
    else if(sc==="craw")String(text).split(/;|\.\s+|\.$/).forEach(c=>{const m=new RegExp(p,"i").exec(c);if(m)hits.push(arr(m));});
    else if(sc==="text"){const m=String(text).match(new RegExp(p,"i"));if(m)hits.push(arr(m));}
    else if(sc==="all"){const re=new RegExp(p,"gi");let m;while((m=re.exec(text)))hits.push(arr(m));}
    else if(sc==="json"){const m=JSON.stringify(INFRA[name]||WON[name]||{}).match(new RegExp(p,"i"));if(m)hits.push(arr(m));}
    cmp(key,id,hits,E[id]);});
  if("hiwf".includes(kind)&&kind.length===1){
    // once-per tracker rows (old onceEffects)
    const ONCE_RE=/\b(?:Once\s*\/\s*turn|Once per turn|Once per game|Once per \w+ Phase|\d+x\s*(?:\/\s*turn|per \w+ Phase)|Each turn|Every turn|Every Skirmish|At the Start of the Empire Phase)\b|\bmay\b(?!\s+not)/i;
    const XCH_RE=/(\d+)x\s*(?:\/\s*turn|per \w+ Phase):?\s*exchange (\d+) gold for (?:(\d+) Influence|Influence \+(\d+))/i;
    const oncePhase=c=>{if(/\bOnce per turn\b/i.test(c))return "turn";const m=/per (\w+) Phase|At the (Start) of the Empire Phase|\bin the (\w+) Phase\b/i.exec(c);if(!m)return "";return m[1]?m[1].toLowerCase():m[3]?m[3].toLowerCase():"empire";};
    const once=[];String(text).split(/;|\.\s+|\.$/).forEach(c=>{c=c.trim();if(!c||!ONCE_RE.test(c)||new RegExp(REG.siege_double[2],"i").test(c))return;const i=c.search(ONCE_RE),cm=c.lastIndexOf(", ",i);if(cm>0)c=c.slice(cm+2);
      const x=XCH_RE.exec(c);once.push({c,ph:oncePhase(c),game:/Once per game/i.test(c),x:x?arr(x):null});});
    cmp(key,"_once",once,(E._once||[]).map(o=>({c:o.c,ph:o.ph,game:o.game,x:o.x})));
    // can't-restrictions (old actRestrict scan, before its per-action filter)
    const cant=[];String(text).split(/;|\.\s+|\.$/).forEach(cl=>{const re=/(?:can.t|cannot)\s+(.+?)(?=,?\s+and\s+(?:you\s+)?(?:can.t|cannot)\b|$)/gi;let m;
      while((m=re.exec(cl))){const c=m[1];if(/^(?:be the target|be in an Alliance|pursue|build|equip|use shields|gain Immune|exceed|refuse|choose|vote|be modified|be Razed)|\bon you$/i.test(c))continue;cant.push(c);}});
    cmp(key,"_cant",cant,E._cant);}
  // Speed clauses (old spClauses + speedOf / scanO classification)
  const SP_RE=/Speed\s*([+\-−])\s?(\d+)/i;
  const spRows=(t,fac)=>{t=String(t||"").replace(/\*\*/g,"");if(fac)t=t.replace(/don.t gain Speed[^.;]*/ig,"");
    return t.split(/[;.]\s*/).filter(c=>SP_RE.test(c)).map(c=>{const m=SP_RE.exec(c),r={c,v:(m[1]==="+"?1:-1)*(+m[2]),yp:/your Province/i.test(c),en:/Enemy/i.test(c),na:/non-allied/i.test(c)};
      if(/start a Move action within (?:your )?Province/i.test(c))r.k="startProv";else if(/your Province|non-allied|Enemy/i.test(c))r.k="others";
      else{const ms=/in (Spring|Summer|Fall|Winter)/i.exec(c);if(ms){r.k="season";r.s=ms[1];}else if(/\b(while|if|when)\b/i.test(c))r.k="cond";else r.k="plain";}
      return r;});};
  const srt=L=>(L||[]).map(r=>{const o={};Object.keys(r).sort().forEach(k=>o[k]=r[k]);return o;});
  if(kind==="h"||kind==="i")cmp(key,"_sp",srt(spRows(text)),srt(E._sp));
  if(kind==="F"){cmp(key,"_sp",srt(spRows(text,true)),srt(E._sp));cmp(key,"_spo",srt(spRows(text)),srt(E._spo));}
});
console.log((bad?"FAIL ":"OK ")+checked+" checks, "+bad+" differences");process.exit(bad?1:0);
