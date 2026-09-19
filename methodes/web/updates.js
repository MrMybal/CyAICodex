'use strict';
let updateBusy = false;
const updateLabels = {
  idle: 'Rechercher une nouvelle version sur GitHub.',
  checking: 'Vérification des mises à jour…',
  available: 'Une nouvelle version est disponible.',
  current: 'CyAICodex est à jour.',
  downloading: 'Téléchargement et vérification de l’installateur…',
  installing: 'L’installateur est ouvert. Suivez ses étapes ; vos données seront conservées.',
  error: 'La vérification a échoué.'
};
function renderUpdates(value, fill = false) {
  $('#update-version').textContent = 'CyAICodex ' + value.current_version + (value.available ? ' → ' + value.latest_version : '');
  $('#update-status').textContent = uiFragment(value.message || updateLabels[value.status]);
  $('#update-install').hidden = !value.available;
  $('#update-install').disabled = updateBusy || !value.install_supported || ['downloading', 'installing'].includes(value.status);
  $('#update-check').disabled = updateBusy || value.status === 'downloading';
  $('#update-notice').hidden = !value.available;
  if (fill) {
    const f = $('#updates-form');
    f.elements.automatic.checked = value.automatic;
    f.elements.use_git.checked = value.use_git;
    $('#update-token-state').textContent = uiFragment(value.token_configured ? 'Jeton GitHub enregistré.' : 'Aucun jeton GitHub enregistré.');
  }
}
async function refreshUpdates() { renderUpdates(await api('/updates'), true); }
$('#updates-form').addEventListener('submit', guarded(async e => {
  e.preventDefault(); const f = e.target;
  renderUpdates(await send('/updates/settings', {
    automatic: f.elements.automatic.checked, use_git: f.elements.use_git.checked,
    token: f.elements.token.value.trim(), clear_token: f.elements.clear_token.checked
  }, 'PUT'), true);
  f.elements.token.value = ''; f.elements.clear_token.checked = false;
  notify(uiFragment('Paramètres enregistrés et appliqués.'));
}));
$('#update-check').addEventListener('click', guarded(async () => {
  updateBusy = true; $('#update-check').disabled = true;
  $('#update-status').textContent = uiFragment(updateLabels.checking);
  try { const result = await send('/updates/check', {}); updateBusy = false; renderUpdates(result); }
  finally { updateBusy = false; $('#update-check').disabled = false; }
}));
$('#update-install').addEventListener('click', guarded(async () => {
  updateBusy = true; $('#update-install').disabled = true;
  $('#update-status').textContent = uiFragment(updateLabels.downloading);
  try { const result = await send('/updates/install', {}); updateBusy = false; renderUpdates(result); }
  catch (error) { $('#update-status').textContent = error.message; throw error; }
  finally { updateBusy = false; }
}));
$('#update-notice').addEventListener('click', guarded(async () => { await changePage('settings'); $('#updates-panel').scrollIntoView({behavior:'smooth'}); }));
setInterval(async () => { if (!updateBusy) { try { renderUpdates(await api('/updates')); } catch (_) {} } }, 30000);
