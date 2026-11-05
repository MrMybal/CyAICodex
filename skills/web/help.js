'use strict';
(() => {
  const french = document.documentElement.lang === 'fr';
  const pageMap = {library:'skills',images:'images',projects:'projects',assistant:'assistant',connections:'mcp',settings:'providers'};
  function contextRoute(target) {
    const tagged = target?.closest?.('[data-help-page]');
    if (tagged) return {page:tagged.dataset.helpPage,anchor:tagged.dataset.helpSection||null,media:tagged.dataset.helpMedia||null};
    const active = document.querySelector('.page:not([hidden])');
    return {page:pageMap[active?.id.replace('page-','')]||'welcome'};
  }
  function legacyRoute() {
    let hash=location.hash.slice(1),route={page:'welcome'};
    try {
      if(hash.startsWith('/')) {
        const [path,query] = hash.slice(1).split('?'),parts=path.split('/');
        route.page=decodeURIComponent(parts[1]||'welcome');route.anchor=parts[2]?decodeURIComponent(parts[2]):null;route.media=new URLSearchParams(query||'').get('media');
      } else if(hash) route.page=decodeURIComponent(hash);
    } catch { route={page:'welcome'}; }
    return route;
  }
  window.openDocumentation = async function(page='welcome',anchor=null,media=null) {
    const response=await fetch('/api/help/open',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({language:document.documentElement.lang==='fr'?'fr':'en',page,anchor,media})});
    const value=await response.json();
    if(!response.ok)throw Error(typeof value.detail==='string'?value.detail:(french?'Impossible d’ouvrir l’aide locale.':'Cannot open local help.'));
    return value;
  };
  function report(error) {
    const status=document.getElementById('help-launch-status');
    const text=error?.message||(french?'Ouvrez Documentation depuis l’icône Windows.':'Open Documentation from the Windows tray.');
    if(status)status.textContent=text;
    else if(typeof window.notify==='function')window.notify(text);
    else {const notice=document.getElementById('notice');if(notice){notice.hidden=false;notice.textContent=text;}}
  }
  async function open(route) {
    try {await window.openDocumentation(route.page,route.anchor,route.media);const s=document.getElementById('help-launch-status');if(s)s.textContent=french?'La documentation locale a été ouverte dans votre navigateur.':'Local documentation opened in your browser.';}catch(error){report(error);}
  }
  document.addEventListener('click',event=>{
    const button=event.target.closest('[data-open-help]');if(!button)return;
    event.preventDefault();open(button.dataset.openHelp==='legacy'?legacyRoute():contextRoute(button));
  });
  document.addEventListener('keydown',event=>{if(event.key==='F1'){event.preventDefault();open(contextRoute(event.target));}});
  if(document.body.classList.contains('help-launcher'))open(legacyRoute());
})();
