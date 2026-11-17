// ---- Auto battle: plays the open Battle with emulated dice, one step at a time, at the battle field's pace ----
// Players still pick their own Tactics: before the reveal it just waits. Each step waits until the field has finished
// playing the last one (BF.q empty), then rolls the next roll bFlow() allows (Strike, Cleave, Parry, Save, Recover,
// Riposte, apply casualties, Panic, Break), else ends the Skirmish. It stops once the Battle is decided (the
// result buttons are left to the players). An Escalation AI side keeps playing itself; this device only (not saved).
let AUTO_B=null,AUTO_T=null;
function autoOn(){const B=battle();return !!(AUTO_B&&B.id&&B.id===AUTO_B);}
function autoSet(on){const B=battle();if(on&&B.id){B.dice=true;AUTO_B=B.id;save();autoKick();}else AUTO_B=null;render();}
function autoKick(){if(AUTO_T)return;AUTO_T=setTimeout(()=>{AUTO_T=null;autoStep();},400);}
function autoBusy(){return !!(BF&&(BF.qOn||BF.q.length||BF.leaving))||(typeof ESC_AI_T!=="undefined"&&!!ESC_AI_T);}
function autoStep(){if(!autoOn())return;
  if(autoBusy()){autoKick();return;}
  const B=battle(),escX=typeof escOn==="function"&&escOn()&&typeof escAiSide==="function"?escAiSide():null,mine=X=>X!==escX;
  try{
    if(battleOutcome()&&!battleOwed()){AUTO_B=null;flash("Auto battle: the Battle is decided");render();return;}
    if(!(B.rev&&B.rev.sk===B.sk)){autoKick();return;}                     // players pick their own Tactics: wait for the reveal
    const rp=B.endRep&&B.endRep.sk===B.sk&&B.endRep.rows.find(r=>mine(r.X)&&brkPending(r));
    if(rp){rollBreakBtn(rp.X);autoKick();return;}
    const fl=bFlow();if(!fl){autoKick();return;}
    if(fl.done){endSkirmish();autoKick();return;}
    const ord=fl.first?[fl.first,fl.first==="A"?"B":"A"]:["A","B"];
    for(const X of ord){if(!mine(X))continue;const k=fl.can[X],c=sideCalc(X);
      const act=k.strike?()=>roll(X,"Strike"):k.cleave?()=>roll(X,"Cleave"):
        k.parry?()=>roll(X,"Parry"):k.save?()=>roll(X,"Save"):k.recover?()=>roll(X,"Recover"):
        k.rip?()=>{if(c.canParry)roll(X,"RipParry");roll(X,"RipSave");}:k.apply?()=>{applyCas(X,pendCas(X));save();render();}:
        k.panic?()=>roll(X,"Morale"):k.brk?()=>roll(X,"Break"):null;
      if(act){act();break;}}
  }catch(e){console.warn("auto battle",e);AUTO_B=null;render();return;}
  autoKick();}
