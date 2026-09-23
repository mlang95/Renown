
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
})();
