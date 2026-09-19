'use strict';
const mcpNames={codex:'Codex',claude_desktop:'Claude Desktop',opencode:'OpenCode'};
let setupPrefs=null;
function showSetupAccess(){
  const local=$('#setup-auth').value==='local';
  $('#setup-context-label').hidden=local;$('#setup-rights').hidden=local;
  $('#setup-access-note').textContent=local
    ?uiFragment('Cet accès reprend le contexte et les droits définis dans Paramètres → Autorisations MCP. ')+(setupPrefs?.local_writable?uiFragment('Écriture autorisée.'):uiFragment('Lecture seule.'))
    :uiFragment('Chaque client recevra son propre jeton avec les droits choisis ci-dessus. Vous pourrez le révoquer dans la liste des connexions.');
}
function renderMCPClient(result){
  const card=$('#mcp-client-'+result.client);
  if(!card)return;
  const stage=(ok,label)=>uiHTML`<span class="mcp-stage ${ok?'ok':'pending'}">${ok?'✓':'○'} ${label}</span>`;
  card.innerHTML=uiHTML`<h3>${esc(mcpNames[result.client])}</h3><div class="mcp-stages">${stage(result.server,uiFragment('Serveur lancé'))}${stage(result.configured,uiFragment('Client configuré'))}${stage(result.mcp,uiFragment('Connexion MCP testée'))}</div><p>${esc(result.message)}</p>${result.context?uiHTML`<p class="small">${result.context.writable?uiFragment('Lecture et écriture'):uiFragment('Lecture seule')} · ${esc(result.context.project_id?uiFragment('Projet : ')+(state.catalog.projects.find(p=>p.id===result.context.project_id)?.name||result.context.project_id):result.context.type_id?uiFragment('Type : ')+(state.catalog.types.find(p=>p.id===result.context.type_id)?.name||result.context.type_id):'Global')}${result.context.include_global?uiFragment(' · global inclus'):''}</p>`:''}<button class="primary" data-setup-client="${result.client}">${result.mcp?uiFragment('Reconfigurer et tester'):uiFragment('Configurer et tester')}</button><button class="quiet" data-test-mcp="${result.client}">Tester seulement</button><details><summary>Détails</summary><p class="small mcp-path">${esc(result.path||'')}</p><p class="small">${esc(result.restart||'')}</p>${result.tools?.length?uiHTML`<p class="small">Outils : ${esc(result.tools.join(', '))}</p>`:''}</details>`;
}
async function refreshMCPSetup(){
  $('#mcp-clients').innerHTML=Object.entries(mcpNames).map(([id,label])=>uiHTML`<article class="mcp-client" id="mcp-client-${id}"><h3>${label}</h3><p>Diagnostic en cours…</p></article>`).join('');
  try{
    setupPrefs=await api('/preferences');
    $('#setup-context').innerHTML=contextOptions(uiFragment('Global uniquement'));
    $('#setup-write').checked=setupPrefs.default_writable;
    $('#setup-auth').value=setupPrefs.local_no_token?'local':'token';
    $('#setup-auth').querySelector('option[value="local"]').disabled=!setupPrefs.local_no_token;
    showSetupAccess();$('#mcp-discovery-url').textContent=location.origin+'/mcp-info';
    const results=await api('/mcp-setup');results.forEach(renderMCPClient);
  }catch(err){$('#mcp-clients').textContent=uiFragment('Diagnostic indisponible : ')+err.message;throw err;}
}
$('#setup-auth').addEventListener('change',showSetupAccess);
$('#mcp-refresh').addEventListener('click',guarded(async()=>{const b=$('#mcp-refresh');b.disabled=true;try{await refreshMCPSetup();}finally{b.disabled=false;}}));
document.addEventListener('click',guarded(async e=>{
  const button=e.target.closest('[data-setup-client],[data-test-mcp]');if(!button)return;
  const client=button.dataset.setupClient||button.dataset.testMcp,card=$('#mcp-client-'+client);
  card.querySelectorAll('button').forEach(b=>b.disabled=true);button.textContent=uiFragment('Connexion en cours…');
  try{
    if(button.dataset.setupClient){
      const result=await send('/mcp-setup/'+client,{without_token:$('#setup-auth').value==='local',project_id:'',type_id:'',...contextParams($('#setup-context').value),include_global:$('#setup-global').checked,writable:$('#setup-write').checked});
      renderMCPClient(result.diagnostic);
      notify(result.diagnostic.mcp?uiFragment('Connexion prête. Rechargez les serveurs MCP ou redémarrez ')+mcpNames[client]+'.':uiFragment('Configuration enregistrée, mais le test a échoué : consultez le diagnostic.'));
      await refreshConnections();
    }else renderMCPClient(await api('/mcp-setup/'+client));
  }catch(err){
    card.querySelector('p').textContent=err.message;
    button.textContent=button.dataset.setupClient?uiFragment('Configurer et tester'):uiFragment('Tester seulement');throw err;
  }finally{card.querySelectorAll('button').forEach(b=>b.disabled=false);}
}));
