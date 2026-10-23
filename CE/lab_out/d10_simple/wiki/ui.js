
(function(){
  var root=document.documentElement, body=document.body;
  // theme toggle (head script already applied the stored/default theme)
  var tb=document.getElementById('theme');
  function setTheme(t){root.setAttribute('data-theme',t);try{localStorage.setItem('theme',t)}catch(e){}}
  if(tb)tb.addEventListener('click',function(){setTheme(root.getAttribute('data-theme')==='dark'?'light':'dark')});
  // game mode: rules + reference only
  var gm=document.getElementById('gamemode');
  function setGame(on){body.classList.toggle('game-mode',on);if(gm)gm.classList.toggle('on',on);root.classList.remove('game-pending');try{localStorage.setItem('gamemode',on?'1':'0')}catch(e){}}
  var gs=false;try{gs=localStorage.getItem('gamemode')==='1'}catch(e){}
  setGame(gs);
  if(gm)gm.addEventListener('click',function(){setGame(!body.classList.contains('game-mode'))});
  // collapsible nav groups (persisted); escalation collapsed by default
  var KEY='navcollapsed', collapsed;
  try{collapsed=JSON.parse(localStorage.getItem(KEY)||'null')}catch(e){collapsed=null}
  var first=(collapsed===null); if(first)collapsed=['escalation'];
  var groups=[].slice.call(document.querySelectorAll('.navgroup'));
  groups.forEach(function(g){ if(collapsed.indexOf(g.dataset.group)>=0)g.classList.add('collapsed'); });
  var act=document.querySelector('nav a.active');
  if(act){var ag=act.closest('.navgroup'); if(ag)ag.classList.remove('collapsed');}
  function persist(){var c=groups.filter(function(g){return g.classList.contains('collapsed')}).map(function(g){return g.dataset.group});try{localStorage.setItem(KEY,JSON.stringify(c))}catch(e){}}
  if(first)persist();
  groups.forEach(function(g){var h=g.querySelector('.navhead'); if(h)h.addEventListener('click',function(){g.classList.toggle('collapsed');persist();});});
  // term hover cards: the definition's first sentence + where it lives; on touch, first tap shows it, second follows the link
  var tip=null, shown=null, touch=window.matchMedia&&window.matchMedia('(hover: none)').matches;
  function hide(){if(tip)tip.remove();tip=null;shown=null;}
  function show(a){hide();if(!a.dataset.def)return;tip=document.createElement('div');tip.className='termtip';
    var b=document.createElement('b');b.textContent=a.textContent;var p=document.createElement('div');p.textContent=a.dataset.def;
    var w=document.createElement('small');w.textContent=a.dataset.where||'';tip.appendChild(b);tip.appendChild(p);tip.appendChild(w);body.appendChild(tip);
    var r=a.getBoundingClientRect(),x=Math.max(8,Math.min(r.left+window.scrollX,window.scrollX+document.documentElement.clientWidth-tip.offsetWidth-8)),
        y=r.bottom+window.scrollY+6;if(r.bottom+tip.offsetHeight+12>window.innerHeight)y=r.top+window.scrollY-tip.offsetHeight-6;
    tip.style.left=x+'px';tip.style.top=y+'px';shown=a;}
  document.addEventListener('mouseover',function(e){var a=e.target.closest&&e.target.closest('a.term');if(!touch&&a&&a!==shown)show(a);});
  document.addEventListener('mouseout',function(e){var a=e.target.closest&&e.target.closest('a.term');if(!touch&&a&&!a.contains(e.relatedTarget))hide();});
  document.addEventListener('focusin',function(e){if(e.target.matches&&e.target.matches('a.term'))show(e.target);});
  document.addEventListener('focusout',function(e){if(e.target.matches&&e.target.matches('a.term'))hide();});
  document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a.term');
    if(touch&&a&&a.dataset.def&&shown!==a){e.preventDefault();show(a);return;} if(!a)hide();});
  window.addEventListener('scroll',function(){if(!touch)hide();},{passive:true});
})();
