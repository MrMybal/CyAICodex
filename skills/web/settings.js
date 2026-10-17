'use strict';
const localLabels={codex:uiFragment('Codex · compte ChatGPT'),claude_code:uiFragment('Claude Code · compte Claude'),opencode:uiFragment('OpenCode · client local'),ollama:'Ollama · local'};
$('#local-clients').innerHTML=Object.entries(localLabels).map(([id,label])=>uiHTML`<div class="provider-row"><div><strong>${label}</strong><p id="local-status-${id}">Cliquez sur Vérifier</p></div><button class="quiet" data-check-local="${id}">Vérifier</button>${['claude_code','opencode'].includes(id)?uiHTML`<button class="primary" data-login-local="${id}">Se connecter</button>`:''}</div>`).join('');
async function refreshPreferences(){
  const p=await api('/preferences'),f=$('#preferences-form');
  await refreshConnectorSettings();
  await refreshUpdates();
  $('#local-context').innerHTML=contextOptions(uiFragment('Global uniquement'));
  for(const name of ['local_no_token','local_writable','default_writable','include_global'])f.elements[name].checked=p[name];
  for(const name of ['codex_path','claude_code_path','opencode_path','ollama_url'])f.elements[name].value=p[name];
  f.elements.context.value=p.project_id?'project:'+p.project_id:p.type_id?'type:'+p.type_id:'';
  $('#no-token-endpoint').textContent=p.local_no_token?uiFragment('Accès sans jeton : ')+location.origin+'/mcp':uiFragment('Accès MCP sans jeton désactivé');
}
$('#preferences-form').addEventListener('submit',guarded(async e=>{
  e.preventDefault();const f=e.target,data={project_id:'',type_id:'',...contextParams(f.elements.context.value)};
  for(const name of ['local_no_token','local_writable','default_writable','include_global'])data[name]=f.elements[name].checked;
  for(const name of ['codex_path','claude_code_path','opencode_path','ollama_url'])data[name]=f.elements[name].value.trim();
  await send('/preferences',data,'PUT');settingsDirty=false;await refreshPreferences();$('#preferences-state').textContent=uiFragment('Paramètres enregistrés et appliqués.');
}));
document.addEventListener('change',guarded(async e=>{
  if(e.target.matches('[data-write-connection]')){
    const b=e.target;b.disabled=true;try{await send('/connections/'+b.dataset.writeConnection,{writable:b.checked},'PUT');notify(uiFragment('Droit d’écriture mis à jour.'));}
    catch(err){b.checked=!b.checked;throw err;}finally{b.disabled=false;}
  }
}));
document.addEventListener('click',guarded(async e=>{
  const b=e.target.closest('[data-check-local]');if(b){
    b.disabled=true;const provider=b.dataset.checkLocal,view=$('#local-status-'+provider);view.textContent=uiFragment('Vérification…');
    try{const result=await api('/local/'+provider+'/check');view.textContent=result.message;
      if(provider==='codex'&&result.available){const account=await api('/codex/account');view.textContent+=account.connected?uiFragment(' · compte connecté'):uiFragment(' · compte à connecter dans Connexions');}
      if(provider==='ollama')$('#ollama-models').innerHTML=uiFragment('<option value="">Choisir un modèle</option>')+(result.models||[]).map(m=>uiHTML`<option value="${esc(m)}">${esc(m)}</option>`).join('');
    }catch(err){view.textContent=err.message;}finally{b.disabled=false;}
  }
  const login=e.target.closest('[data-login-local]');if(login){login.disabled=true;try{await send('/local/'+login.dataset.loginLocal+'/login',{});notify(uiFragment('Terminez la connexion dans la fenêtre du client qui vient de s’ouvrir.'));}finally{login.disabled=false;}}
}));
$('#use-ollama').addEventListener('click',guarded(async()=>{
  const model=$('#ollama-models').value;if(!model)throw Error(uiFragment('Choisissez un modèle Ollama installé.'));
  $('#assistant-provider').value='ollama';$('#assistant-model').value=model;localStorage.setItem('model-ollama',model);await changePage('assistant');
}));

for (const selector of ['#ui-language', '#settings-language']) {
  $(selector).value = uiLanguage;
  $(selector).addEventListener('change', guarded(async event => {
    const control = event.target, next = control.value;
    if (next === uiLanguage) return;
    if (state.dirty || imageState.dirty || state.messages.length || $('#chat-input').value || $('dialog[open]') || settingsDirty || $('[data-connector][data-dirty="true"]')) {
      if (!confirm(uiText('Changer de langue rechargera l’interface et effacera la conversation affichée. Continuer ?'))) {control.value = uiLanguage;return;}
    }
    control.disabled = true;
    try {
      await send('/language', {language: next}, 'PUT');
      state.dirty = false; imageState.dirty = false;
      location.reload();
    } catch (error) {control.disabled = false; control.value = uiLanguage; throw error;}
  }));
}
let settingsDirty = false;
$('#preferences-form').addEventListener('input', () => settingsDirty = true);
