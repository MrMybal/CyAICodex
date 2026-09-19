'use strict';
const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];
const state = {catalog:{types:[],projects:[]}, methods:[], category:'', offset:0, total:0, editing:null, config:null, messages:[], searching:0, dirty:false};
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let noticeTimer;
function notify(message) { const n=$('#notice'); n.textContent=message; n.hidden=false; clearTimeout(noticeTimer); noticeTimer=setTimeout(()=>n.hidden=true,7000); }
async function api(path, options={}) {
  const response = await fetch('/api'+path, {credentials:'same-origin',...options,headers:{'Content-Type':'application/json',...options.headers}});
  const data = await response.json();
  if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:uiFragment('Vérifiez les champs du formulaire.'));
  return data;
}
const send = (path,body,method='POST') => api(path,{method,body:JSON.stringify(body)});
function guarded(fn) {return async (...args)=>{try{await fn(...args);}catch(e){notify(e.message);}};}
function contextOptions(first=uiFragment('Tous les contextes')) {
  return uiHTML`<option value="">${first}</option>` + (state.catalog.types.length?uiFragment('<optgroup label="Types de projets">')+state.catalog.types.map(t=>uiHTML`<option value="type:${t.id}">${esc(t.name)}</option>`).join('')+'</optgroup>':'') + (state.catalog.projects.length?uiFragment('<optgroup label="Projets">')+state.catalog.projects.map(p=>uiHTML`<option value="project:${p.id}">${esc(p.name)}</option>`).join('')+'</optgroup>':'');
}
function contextParams(value) {const [kind,id]=value.split(':');return id ? {[kind==='type'?'type_id':'project_id']:id} : {};}
function scopeName(m) {return m.scope==='global'?uiFragment('Globale'):(state.catalog[m.scope==='type'?'types':'projects'].find(g=>g.id===m.scope_id)?.name || uiFragment('Groupe'));}
function shortDate(value){return new Intl.DateTimeFormat(uiLanguage === 'en' ? 'en-GB' : 'fr-FR',{day:'numeric',month:'short'}).format(new Date(value));}
async function refreshCatalog() {
  state.catalog=await api('/catalog');
  const selected=$('#context-filter').value;
  $('#context-filter').innerHTML=contextOptions(); $('#context-filter').value=selected;
  $('#connection-context').innerHTML=contextOptions(uiFragment('Méthodes globales uniquement'));
  $('#project-type').innerHTML=uiFragment('<option value="">Sans type</option>')+state.catalog.types.map(t=>uiHTML`<option value="${t.id}">${esc(t.name)}</option>`).join('');
  $('#type-list').innerHTML=state.catalog.types.map(t=>uiHTML`<div class="group-item"><span>⊞ &nbsp; ${esc(t.name)}</span><small>${state.catalog.projects.filter(p=>p.type_id===t.id).length} projet(s)</small></div>`).join('')||uiFragment('<p>Aucun type pour le moment.</p>');
  $('#project-list').innerHTML=state.catalog.projects.map(p=>uiHTML`<div class="group-item"><span>${esc(p.name)}<small>${esc(state.catalog.types.find(t=>t.id===p.type_id)?.name||uiFragment('Sans type'))}</small></span><button class="quiet" data-project="${p.id}">Voir les méthodes →</button></div>`).join('')||uiFragment('<p>Créez votre premier projet.</p>');
  $('#project-count').textContent=state.catalog.projects.length;
}
async function refreshStats(){const [methods,conns]=await Promise.all([api('/methods?limit=100'),api('/connections')]);$('#method-count').textContent=methods.total;$('#connection-count').textContent=conns.length;
  const current=$('#assistant-reference').value;
  $('#assistant-reference').innerHTML=uiFragment('<option value="">Aucune</option>')+methods.items.map(m=>uiHTML`<option value="${m.id}">${esc(m.title)}</option>`).join(''); $('#assistant-reference').value=current;
  const catalog=await api('/catalog');
  const cats=[...new Set(['Confidentialité','Développement','Démonstrations','Qualité',...catalog.categories])];
  $('#categories').innerHTML=[uiFragment('Toutes'),...cats].map((c,i)=>uiHTML`<button class="chip ${state.category===(i?c:'')?'active':''}" data-category="${esc(i?c:'')}">${esc(uiText(c))}</button>`).join('');
}
async function refreshMethods(){
  const seq=++state.searching;
  const params=new URLSearchParams({q:$('#search').value,status:$('#status-filter').value,category:state.category,limit:12,offset:state.offset,include_global:$('#include-global').checked,...contextParams($('#context-filter').value)});
  const data=await api('/methods?'+params);
  if(seq!==state.searching)return;
  state.methods=data.items;state.total=data.total;
  $('#result-count').textContent=data.total;
  $('#method-grid').innerHTML=data.items.map(m=>uiHTML`<button class="method-card" data-method="${m.id}"><div class="card-top"><span class="method-icon">${m.category==='Confidentialité'?'♧':m.category==='Démonstrations'?'▷':'▤'}</span><span class="scope-badge">${esc(scopeName(m))}</span></div><h3>${esc(m.title)}</h3><p>${esc(m.summary||m.excerpt)}</p><div class="tags">${m.tags.slice(0,3).map(t=>uiHTML`<span class="tag">${esc(t)}</span>`).join('')}</div><div class="card-bottom"><span>Modifiée le ${shortDate(m.updated_at)} · v${m.version}</span><span>↗</span></div></button>`).join('') || uiHTML`<div class="empty"><span class="empty-icon">▤</span><h2>${$('#search').value||state.category||$('#context-filter').value?uiFragment('Aucune méthode ne correspond'):uiFragment('Votre prochaine bonne pratique commence ici.')}</h2><p>Enregistrez une méthode à la main, ou faites-vous aider par l’assistant. Vos IA pourront ensuite la retrouver.</p><button class="primary" id="empty-create">＋ Créer une méthode</button></div>`;
  $('#previous').disabled=state.offset===0;$('#next').disabled=state.offset+12>=data.total;
  $('#pagination-info').textContent=data.total?uiHTML`${state.offset+1}–${Math.min(state.offset+12,data.total)} sur ${data.total}`:uiFragment('0 méthode');
}
async function changePage(page){
  sessionStorage.setItem('cyaicodex-page',page);
  $$('.page').forEach(p=>p.hidden=p.id!=='page-'+page); $$('.nav').forEach(b=>b.classList.toggle('active',b.dataset.page===page));
  $('#breadcrumb').textContent={library:uiFragment('Bibliothèque'),projects:uiFragment('Projets & types'),images:uiFragment('Ressources d’images'),assistant:'Assistant',connections:uiFragment('Connexions'),settings:uiFragment('Paramètres')}[page];
  if(page==='settings')await refreshPreferences();
  if(page==='images')await refreshImages();
  if(page==='assistant')await refreshImageReferences();
  if(page==='connections')await Promise.all([refreshConnections(),refreshMCPSetup()]);
  if(page==='library')await Promise.all([refreshStats(),refreshMethods()]);
}
function scopeChoices(selected=''){
  const scope=$('#editor-scope').value;$('#scope-id-label').hidden=scope==='global';
  $('#editor-scope-id').required=scope!=='global';
  $('#editor-scope-id').innerHTML=uiFragment('<option value="">Choisir un groupe</option>')+(scope==='global'?'':state.catalog[scope==='type'?'types':'projects'].map(g=>uiHTML`<option value="${g.id}">${esc(g.name)}</option>`).join(''));
  $('#editor-scope-id').value=selected;
}
async function openEditor(id=null,content=''){
  const method=id?await api('/methods/'+id):null;state.editing=method;state.dirty=false;
  const f=$('#editor-form');f.reset();$('#editor-error').textContent='';$('#history-details').open=false;$('#history-details').hidden=!method;
  $('#editor-heading').textContent=method?uiFragment('Modifier la méthode'):uiFragment('Nouvelle méthode');
  if(method){for(const name of ['title','summary','category','content','scope','status'])f.elements[name].value=method[name];f.elements.tags.value=method.tags.join(', ');}
  else{f.elements.content.value=content;const [scope,id]=$('#context-filter').value.split(':');if(id)f.elements.scope.value=scope;f.elements.status.value=content?'draft':'published';}
  scopeChoices(method?.scope_id||$('#context-filter').value.split(':')[1]||'');
  $('#editor-version').textContent=method?uiHTML`Version ${method.version} · ${shortDate(method.updated_at)}`:uiFragment('Nouvelle fiche');
  $('#history-list').replaceChildren();$('#editor-dialog').showModal();
}
async function saveMethod(e){e.preventDefault();const f=e.currentTarget;const button=$('#save-method');button.disabled=true;$('#editor-error').textContent='';
  try{const method=Object.fromEntries(new FormData(f));method.tags=method.tags.split(',').map(s=>s.trim()).filter(Boolean);if(method.scope==='global')method.scope_id='';
    const old=state.editing;await send('/methods'+(old?'/'+old.id:''),{method,version:old?.version},old?'PUT':'POST');
    state.dirty=false;$('#editor-dialog').close();notify(old?uiFragment('Méthode mise à jour.'):uiFragment('Méthode enregistrée.'));await Promise.all([refreshMethods(),refreshStats()]);
  }catch(err){$('#editor-error').textContent=err.message;}finally{button.disabled=false;}
}
async function refreshConnections(){
  await refreshStartup();
  const [connections,providers,prefs]=await Promise.all([api('/connections'),api('/providers'),api('/preferences')]);
  $('#connection-form').elements.writable.checked=prefs.default_writable;
  $('#local-provider-summary').textContent=['claude_code','opencode'].map(p=>(p==='claude_code'?'Claude Code':'OpenCode')+' : '+(providers[p]?uiFragment('client disponible'):uiFragment('à configurer'))).join(' · ');
  $('#connection-count').textContent=connections.length;
  $('#connection-list').innerHTML=connections.map(c=>uiHTML`<div class="group-item"><div><strong>${esc(c.name)}</strong><small>${c.writable?uiFragment('Lecture & écriture'):uiFragment('Lecture seule')} · ${esc(c.project_id?state.catalog.projects.find(p=>p.id===c.project_id)?.name:c.type_id?state.catalog.types.find(t=>t.id===c.type_id)?.name:'Global')}${c.include_global?' + global':''}</small><small>${c.last_seen?uiFragment('Dernier accès le ')+shortDate(c.last_seen):uiFragment('Pas encore utilisée')}</small></div><label class="check"><input type="checkbox" data-write-connection="${c.id}" ${c.writable?'checked':''}>Écriture</label><button class="quiet danger" data-revoke="${c.id}">Révoquer</button></div>`).join('')||uiFragment('<p>Aucune connexion. Créez-en une pour votre première IA.</p>');
  for(const provider of ['openai','claude'])$('#'+provider+'-status').textContent=providers[provider]?uiFragment('Clé configurée'):uiFragment('Aucune clé configurée');
  $('#codex-status').textContent=providers.codex?uiFragment('Client Codex disponible · compte à vérifier'):uiFragment('Client Codex introuvable sur ce PC');
}
async function refreshStartup(){
  const result=await api('/startup');
  $('#windows-startup').checked=result.enabled;
  $('#windows-startup').disabled=!result.supported;
  $('#startup-state').textContent=!result.supported?uiFragment('Disponible sous Windows uniquement'):result.enabled?uiFragment('Activé · lancement en arrière-plan à l’ouverture de votre session'):uiFragment('Désactivé · lancement manuel');
}
$('#windows-startup').addEventListener('change',guarded(async()=>{
  const control=$('#windows-startup');const enabled=control.checked;control.disabled=true;
  try{await send('/startup',{enabled},'PUT');notify(enabled?uiFragment('Le serveur démarrera automatiquement avec Windows.'):uiFragment('Démarrage automatique désactivé.'));}
  finally{await refreshStartup();}
}));
function showConfig(){
  const c=state.config;if(!c)return;
  let value;
  if($('#config-format').value==='codex')value='[mcp_servers.cyaicodex]\ncommand = '+JSON.stringify(c.command[0])+'\nargs = '+JSON.stringify(c.command.slice(1))+'\nstartup_timeout_sec = 45\n[mcp_servers.cyaicodex.env]\nCYAICODEX_MCP_TOKEN = '+JSON.stringify(c.token);
  else if($('#config-format').value==='claude')value=uiHTML`claude mcp add --transport http methodes ${c.url} --header "Authorization: Bearer ${c.token}"`;
  else if($('#config-format').value==='claude-desktop')value=JSON.stringify({mcpServers:{cyaicodex:{command:c.command[0],args:c.command.slice(1),env:{CYAICODEX_MCP_TOKEN:c.token}}}},null,2);
  else if($('#config-format').value==='opencode')value=JSON.stringify({mcp:{cyaicodex:{type:'local',command:c.command,environment:{CYAICODEX_MCP_TOKEN:c.token},enabled:true,timeout:45000}}},null,2);
  else value=JSON.stringify({mcpServers:{methodes:{type:'http',url:c.url,headers:{Authorization:'Bearer '+c.token}}}},null,2);
  $('#connection-config').textContent=value;
}
function renderChat(){
  const chat=$('#chat');chat.replaceChildren();
  for(const message of state.messages){const div=document.createElement('div');div.className='chat-message '+message.role;const label=document.createElement('strong');label.textContent=message.role==='user'?uiFragment('VOUS'):'ASSISTANT';div.append(label,document.createTextNode(message.content));
    if(message.role==='assistant'){const b=document.createElement('button');b.className='quiet';b.textContent=uiFragment('＋ En faire une méthode');b.addEventListener('click',guarded(()=>openEditor(null,message.content)));div.append(document.createElement('br'),b);}chat.append(div);}
  chat.scrollTop=chat.scrollHeight;
}
function closeDialog(dialog){if(dialog.id==='editor-dialog'&&state.dirty&&!confirm(uiFragment('Fermer sans enregistrer vos modifications ?')))return;dialog.close();}
document.addEventListener('click',guarded(async e=>{
  const page=e.target.closest('[data-page]');if(page)await changePage(page.dataset.page);
  const method=e.target.closest('[data-method]');if(method)await openEditor(method.dataset.method);
  const cat=e.target.closest('[data-category]');if(cat){state.category=cat.dataset.category;state.offset=0;$$('[data-category]').forEach(b=>b.classList.toggle('active',b===cat));await refreshMethods();}
  const project=e.target.closest('[data-project]');if(project){$('#context-filter').value='project:'+project.dataset.project;state.offset=0;await changePage('library');}
  const revoke=e.target.closest('[data-revoke]');if(revoke&&confirm(uiFragment('Révoquer cette connexion ? Son jeton cessera de fonctionner.'))){await api('/connections/'+revoke.dataset.revoke,{method:'DELETE'});await refreshConnections();}
  const close=e.target.closest('.close-dialog');if(close)closeDialog(close.closest('dialog'));
  if(e.target.id==='empty-create')await openEditor();
}));
$('#new-method').addEventListener('click',guarded(()=>openEditor()));
$('#editor-form').addEventListener('submit',saveMethod);
$('#editor-form').addEventListener('input',()=>state.dirty=true);
$('#editor-scope').addEventListener('change',()=>scopeChoices());
$('#editor-dialog').addEventListener('cancel',e=>{e.preventDefault();closeDialog(e.currentTarget);});
$('#config-dialog').addEventListener('close',()=>{state.config=null;$('#connection-config').textContent='';});
$('#history-details').addEventListener('toggle',guarded(async()=>{
  if(!$('#history-details').open||!state.editing)return;const history=await api('/methods/'+state.editing.id+'/history');
  $('#history-list').replaceChildren();history.forEach(h=>{const row=document.createElement('div');row.className='history-row';const text=document.createElement('span');text.textContent=uiHTML`v${h.version} · ${h.author} · ${shortDate(h.at)}`;const b=document.createElement('button');b.type='button';b.className='quiet';b.textContent=uiFragment('Reprendre cette version');b.addEventListener('click',()=>{const f=$('#editor-form');for(const name of ['title','summary','content','category','scope','status'])f.elements[name].value=h.snapshot[name];f.elements.tags.value=h.snapshot.tags.join(', ');scopeChoices(h.snapshot.scope_id);state.dirty=true;notify(uiFragment('Version chargée dans l’éditeur. Enregistrez pour créer une nouvelle version.'));});row.append(text,b);$('#history-list').append(row);});
}));
let searchTimer;$('#search').addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(guarded(async()=>{state.offset=0;await refreshMethods();}),180);});
for(const id of ['context-filter','status-filter','include-global'])$('#'+id).addEventListener('change',guarded(async()=>{state.offset=0;await refreshMethods();}));
$('#previous').addEventListener('click',guarded(async()=>{state.offset=Math.max(0,state.offset-12);await refreshMethods();}));
$('#next').addEventListener('click',guarded(async()=>{state.offset+=12;await refreshMethods();}));
document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!$('dialog[open]')){e.preventDefault();$('#search').focus();}});
for(const kind of ['type','project'])$('#'+kind+'-form').addEventListener('submit',guarded(async e=>{e.preventDefault();await send('/groups/'+(kind==='type'?'types':'projects'),Object.fromEntries(new FormData(e.target)));e.target.reset();await refreshCatalog();notify(kind==='type'?uiFragment('Type créé.'):uiFragment('Projet créé.'));}));
$('#connection-form').addEventListener('submit',guarded(async e=>{e.preventDefault();const f=e.target;const data=Object.fromEntries(new FormData(f));state.config=await send('/connections',{name:data.name,...contextParams(data.context),include_global:f.elements.include_global.checked,writable:f.elements.writable.checked});showConfig();$('#config-dialog').showModal();await refreshConnections();}));
$('#config-format').addEventListener('change',showConfig);
$('#copy-config').addEventListener('click',guarded(async()=>{await navigator.clipboard.writeText($('#connection-config').textContent);notify(uiFragment('Configuration copiée.'));}));
$$('.key-form').forEach(f=>f.addEventListener('submit',guarded(async e=>{e.preventDefault();await send('/providers/'+f.dataset.provider,{key:f.elements.key.value},'PUT');f.reset();await refreshConnections();notify(uiFragment('Configuration de la clé enregistrée.'));})));
$('#codex-login').addEventListener('click',guarded(async()=>{const b=$('#codex-login');b.disabled=true;try{const result=await send('/codex/login',{});const url=new URL(result.authUrl);if(url.protocol!=='https:')throw new Error(uiFragment('URL de connexion Codex invalide.'));const a=document.createElement('a');a.href=url.href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=uiFragment('Continuer la connexion Codex dans le navigateur ↗');$('#codex-login-link').replaceChildren(a);}finally{b.disabled=false;}}));
$('#codex-check').addEventListener('click',guarded(async()=>{const result=await api('/codex/account');$('#codex-status').textContent=result.connected?uiFragment('Compte Codex connecté (')+result.type+')':uiFragment('Compte non connecté');if(result.connected)$('#codex-login-link').replaceChildren();}));
$('#assistant-provider').addEventListener('change',()=>{const p=$('#assistant-provider').value;$('#assistant-model').value=localStorage.getItem('model-'+p)||'';$('#assistant-model').placeholder=({codex:uiFragment('Modèle par défaut de Codex'),claude_code:uiFragment('Modèle par défaut de Claude'),opencode:uiFragment('fournisseur/modèle, ex. ollama/qwen3:0.6b'),ollama:uiFragment('Modèle installé, ex. qwen3:0.6b')})[p]||uiFragment('Identifiant du modèle');});
$('#chat-form').addEventListener('submit',guarded(async e=>{e.preventDefault();const text=$('#chat-input').value.trim();if(!text)return;const b=$('#send-chat');b.disabled=true;$('#clear-chat').disabled=true;const provider=$('#assistant-provider').value;const model=$('#assistant-model').value.trim();localStorage.setItem('model-'+provider,model);
  state.messages.push({role:'user',content:text});renderChat();b.textContent=uiFragment('En cours…');
  try{const ref=$('#assistant-reference').value;const result=await send('/assistant',{provider,model,messages:state.messages.slice(-29),method_ids:ref?[ref]:[],image_ids:$('#assistant-image').value?[$('#assistant-image').value]:[]});state.messages.push({role:'assistant',content:result.text});$('#chat-input').value='';renderChat();}
  catch(err){state.messages.pop();renderChat();throw err;}finally{b.disabled=false;$('#clear-chat').disabled=false;b.textContent=uiFragment('Envoyer ↗');}
}));
$('#clear-chat').addEventListener('click',()=>{state.messages=[];renderChat();$('#chat-input').value='';});
async function boot(){
  const token=new URLSearchParams(location.hash.slice(1)).get('token');
  if(token){history.replaceState(null,'',location.pathname);await send('/session',{token});}
  await refreshCatalog();await Promise.all([refreshMethods(),refreshStats(),loadExtraConnectors()]);
  const page=sessionStorage.getItem('cyaicodex-page');if(['library','images','projects','assistant','connections','settings'].includes(page))await changePage(page);
}
guarded(boot)();
setInterval(async()=>{try{const r=await fetch('/health');if(!r.ok)throw Error();$('#server-dot').style.background='';$('#server-label').firstChild.textContent=uiFragment('Serveur MCP actif');}catch{$('#server-dot').style.background='#bb7070';$('#server-label').firstChild.textContent=uiFragment('Serveur arrêté');}},15000);
window.addEventListener('beforeunload',e=>{if(state.dirty&&$('#editor-dialog').open){e.preventDefault();e.returnValue='';}});
