const DATA = /*__DATA__*/;
const R = DATA.records, INFRA = DATA.infra, WON = DATA.wonders;
const EQ = DATA.equip, ARMYSRC = DATA.armySrc, GLOSS = DATA.glossary || {};
// A weapon with "profile_2h" (Bastard Sword, Spears, …) is ONE item with two profiles (1H / 2H, chosen each
// Skirmish with the Tactic). The data's separate "2H…" entry is folded into it here so it never shows up as its own weapon.
EQ.prof2hOf={};   // "2H…" entry → its weapon
Object.keys(EQ.weapons||{}).forEach(n=>{const w=EQ.weapons[n],k2=w.profile_2h;if(!k2||!EQ.weapons[k2])return;
  w.profile2h=EQ.weapons[k2];EQ.prof2hOf[k2]=n;});
Object.keys(EQ.prof2hOf).forEach(k2=>delete EQ.weapons[k2]);
function prof2h(n){return (EQ.weapons[n]||{}).profile2h||null;}
function fixBastard(a){const n=a&&EQ.prof2hOf[a.weapon];if(n){a.weapon=n;if(a.b2h==null)a.b2h=true;}}
const TIER_RANK = {Crude:0,Cast:1,Wrought:2,Forged:3,Crafted:4};
const ARMOR_TAG = {Gambeson:"Gambeson",Leather:"Leather",Chainmail:"Chainmail",FullPlate:"Full Plate"};
const NAMES = Object.keys(R).filter(n=>!R[n].deprecated).sort();   // deprecated Holdings: in R for saved games, offered nowhere
const NATURAL = new Set(DATA.naturalNames);
const SIMPLE=!!DATA.simple;   // SIMPLE pursuit graph (renown_data.SIMPLE)
const SCORE=DATA.scoreTerm||"Influence";
function dispScore(t){if(!t)return t;
  return String(t).replace(/\b([Nn]et|[Ii]nnate|[Ss]tarting|Envoy's net|Envoy's|action's) Influence\b/g,"$1 "+SCORE)
    .replace(/\bAuthority(\**\s?)([+\-\u2212\u00b1]\s?\d+|[+\-\u2212\u00b1]?X\b)/g,SCORE+"$1$2");}
const CHAIN=DATA.chainTerm||"Efficient", CHAINL=CHAIN.toLowerCase();   // display name of the efficient field
const PHASE = {gold:"income",scale:"income",extort:"income",recoup:"income",tax:"income",
  craft:"craft",influence:"influence",authority:"envoy",faith:"order",doubt:"order",upkeep:"upkeep",dues:"upkeep",
  build_timer:"build",siege_timer:"battle",speed:"battle",combat:"battle",envoy:"envoy",
  natural:"other",other:"other"};
const PHASE_COLOR={income:"--income",craft:"--craft",influence:"--influence",order:"--order",
  upkeep:"--upkeep",build:"--build",battle:"--battle",envoy:"--envoy",season:"--season",other:"--other"};
const PHASE_LABEL={income:"Income / Extort",craft:"Craft → Trade",influence:"Influence",
  order:"Public Order",upkeep:"Upkeep",build:"Build timers",battle:"Battle / siege",
  envoy:"Council / Envoy",season:"Seasonal",other:"Other"};
const SEASONS=["Spring","Summer","Fall","Winter"];
const DOMAINS=DATA.domains||["Industry","Prowess","Piety","Cunning"];
const STANDINGS=DATA.standings||["Rising","Established","Sovereign"];
const DBOARD=DATA.domainBoard||{};
// Presence (PRESENCE_RANGE): one flat range for every Settlement / Army / Bandit Army
function presR(){return +((DATA.rulesConst||{}).PRESENCE_RANGE)||0;}
// a player's Settlement Presence Range: PRESENCE_RANGE + every "Presence +N" they hold (Keep)
function presRof(p){return presR()+(p&&p.board?srcMatch(p.board,"presence_plus").reduce((t,x)=>t+(+x.m[1]||0),0):0);}
const PO=DATA.publicOrder||{};
// Public Order bands in the current Era (negative bands scale with ERAS po_scale_neg; positive with po_scale_pos)
function POB(k){const t=(DATA.poByEra||{})[currentEra()];return (t&&t[String(k)])||PO[String(k)];}
function poNum(k){const e=POB(k),m=e&&String(e[1]).match(/(\d+)/);return m?+m[1]:0;}
const LIM=DATA.limits||{};
const PO_MIN=(LIM.poMin??-5),PO_MAX=(LIM.poMax??10),INIT_MIN=(LIM.initMin??-2),INIT_MAX=(LIM.initMax??2),
      INIT_CAP_FIRST=!!LIM.initCapFirst,INIT_FLOOR=LIM.initFloor!==false,   // bonuses capped before penalties · Initiative floored at INIT_MIN
      INIT_LIMIT_TXT=(INIT_CAP_FIRST?"bonuses to +"+INIT_MAX+", then penalties":"limit +"+INIT_MAX)+(INIT_FLOOR?", floor "+INIT_MIN:"");
const ST=LIM.standing||{Untested:1,Rising:3,Established:6,Sovereign:10};
const SOV=ST.Sovereign,EST=ST.Established,RIS=ST.Rising;
const ERAS=DATA.eras||{};
const EDICTS=DATA.edicts||{};
const STAND_THRESH={Rising:RIS,Established:EST,Sovereign:SOV};
const PLAYER_COLORS=["#4caf50","#ef5350","#42a5f5","#ffb300","#ab47bc","#26c6da","#ec407a"];
// effect registry hits (references/effect_registry.py); the plumbing is in 70_rules.js
const EFX=DATA.efx||{};
function efxOf(key,id){const o=EFX[key];return (o&&o[id])||[];}
function hitOf(key,id){return efxOf(key,id)[0]||null;}   // a source's first hit of pattern id, or null
function facHit(b,id){return hitOf("F:"+((b||{}).faction||""),id);}   // the board's faction mechanic (as written): first hit of pattern id
