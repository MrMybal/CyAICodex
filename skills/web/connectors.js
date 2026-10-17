'use strict';
let extraConnectors = [];
async function loadExtraConnectors() {
  extraConnectors = await api('/connectors');
  const select = $('#assistant-provider');
  for (const item of extraConnectors) {
    if (![...select.options].some(option => option.value === item.id)) select.add(new Option(item.name, item.id));
  }
}
async function refreshConnectorSettings() {
  await loadExtraConnectors();
  const host = $('#extra-connectors');
  host.innerHTML = extraConnectors.map(item => uiHTML`<article class="panel connector-card" data-connector="${esc(item.id)}"><h3>${esc(item.name)}</h3>
    <p>${uiText(item.kind === 'cli' ? 'Compte du CLI local. La connexion du logiciel graphique peut être distincte.' : 'Serveur de modèles. Choisissez un modèle disponible sur votre compte ou votre PC.')}</p>
    ${item.policy === 'native-plan' ? uiHTML`<p class="small">Mode plan du client natif, dans un dossier temporaire. Ses règles de lecture et ses intégrations restent celles du client.</p>` : ''}
    <form class="stack connector-form">
    ${item.kind === 'cli' ? uiHTML`<label>Chemin du client .exe<input name="path" value="${esc(item.config.path)}" placeholder="Automatique"></label>` : uiHTML`<label>Adresse du serveur<input name="url" type="url" required value="${esc(item.config.url)}" ${item.id === 'openrouter' ? 'readonly' : ''}></label><label>${uiText(item.id === 'openrouter' ? 'Clé API OpenRouter' : 'Clé API facultative pour un serveur local')}<input name="key" type="password" maxlength="1000" autocomplete="off" placeholder="${uiText(item.key_configured ? 'Clé enregistrée — laisser vide pour la conserver' : 'Clé API')}" /></label><label class="check"><input name="clear_key" type="checkbox">Retirer la clé enregistrée</label>`}
    <label>Modèle<input name="model" maxlength="200" value="${esc(item.config.model)}" list="connector-models-${esc(item.id)}" placeholder="Identifiant du modèle"></label><datalist id="connector-models-${esc(item.id)}"></datalist>
    <button class="primary">Enregistrer</button></form>
    <div class="connector-actions"><button class="quiet" data-connector-action="check">Vérifier</button><button class="quiet" data-connector-action="models">Charger les modèles</button><button class="quiet" data-connector-action="test">Tester une réponse</button><button class="quiet" data-connector-action="use">Utiliser dans l’assistant</button>${item.kind === 'cli' ? uiHTML`<button class="quiet" data-connector-action="login">Ouvrir le client</button>` : ''}<a href="${esc(item.docs)}" target="_blank" rel="noopener noreferrer">Installation et connexion ↗</a></div>
    <p class="small connector-status" role="status">${uiText(item.last_test ? (item.last_test.passed ? 'Dernier test de réponse réussi.' : 'Dernier test de réponse échoué.') : 'Pas encore testé dans cette application.')}</p></article>`).join('');
}
document.addEventListener('submit', guarded(async event => {
  if (!event.target.matches('.connector-form')) return;
  event.preventDefault();
  const form = event.target, card = form.closest('[data-connector]');
  const values = Object.fromEntries(new FormData(form));
  values.clear_key = !!form.elements.clear_key?.checked;
  const button = form.querySelector('button');button.disabled = true;
  try {
    const config = await send('/connectors/' + card.dataset.connector, values, 'PUT');
    extraConnectors.find(item => item.id === card.dataset.connector).config = config;
    if (form.elements.key) {form.elements.key.value = '';form.elements.key.placeholder = uiText('Clé enregistrée — laisser vide pour la conserver');}
    if (form.elements.clear_key) form.elements.clear_key.checked = false;
    card.dataset.dirty = '';
    card.querySelector('.connector-status').textContent = uiText('Paramètres enregistrés et appliqués.');
  } finally {button.disabled = false;}
}));
document.addEventListener('input', event => {
  const form = event.target.closest('.connector-form');
  if (form) form.closest('[data-connector]').dataset.dirty = 'true';
});
document.addEventListener('click', guarded(async event => {
  const button = event.target.closest('[data-connector-action]');if (!button) return;
  const card = button.closest('[data-connector]'), id = card.dataset.connector, action = button.dataset.connectorAction;
  const view = card.querySelector('.connector-status'), model = card.querySelector('[name="model"]').value.trim();
  if (card.dataset.dirty && action !== 'models') {notify(uiText('Enregistrez les réglages de ce connecteur avant de continuer.'));return;}
  const buttons = [...card.querySelectorAll('button')];buttons.forEach(b => b.disabled = true);
  view.textContent = uiText('En cours…');
  try {
    if (action === 'use') {
      $('#assistant-provider').value = id;$('#assistant-model').value = model;$('#assistant-model').placeholder = uiText('Identifiant du modèle');
      localStorage.setItem('model-' + id, model);await changePage('assistant');
      view.textContent = uiText('Connecteur sélectionné.');
    } else if (action === 'models') {
      const result = await api('/connectors/' + id + '/models');
      card.querySelector('datalist').replaceChildren(...result.models.map(value => new Option(value, value)));
      view.textContent = uiText(result.models.length ? 'Catalogue chargé. Choisissez un modèle dans le champ Modèle.' : 'Aucun modèle disponible sur ce serveur.');
    } else if (action === 'login') {
      await send('/connectors/' + id + '/login', {});view.textContent = uiText('Terminez la connexion dans la fenêtre du client qui vient de s’ouvrir.');
    } else {
      const result = action === 'test' ? await send('/connectors/' + id + '/test', {model}) : await api('/connectors/' + id + '/check');
      view.textContent = result.message + (result.version ? ' · ' + result.version : '');
    }
  } catch (error) {view.textContent = error.message;throw error;}
  finally {buttons.forEach(b => b.disabled = false);}
}));
$('#assistant-provider').addEventListener('change', () => {
  const item = extraConnectors.find(c => c.id === $('#assistant-provider').value);
  if (item) {$('#assistant-model').value = localStorage.getItem('model-' + item.id) || item.config.model;$('#assistant-model').placeholder = uiText('Identifiant du modèle');}
});
