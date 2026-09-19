// Run with node tests/i18n_browser.cjs. No browser or npm packages required.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const dictionary = Object.fromEntries(fs.readFileSync('methodes/web/translations.tsv', 'utf8').trim().split(/\r?\n/).map(line => line.split('\t').map(x => x.replace(/\\n/g, '\n'))));
for (const language of ['en', 'fr']) {
  const context = {UI_TRANSLATIONS: dictionary, document: {documentElement: {lang: language}}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('methodes/web/i18n.js', 'utf8'), context);
  assert.equal(context.uiText('Bibliothèque'), language === 'en' ? 'Library' : 'Bibliothèque');
  assert.equal(context.uiHTML(['<p>Modifiée le ', '</p><h3>', '</h3>'], '19 September', 'Bibliothèque'), language === 'en' ? '<p>Updated on 19 September</p><h3>Bibliothèque</h3>' : '<p>Modifiée le 19 September</p><h3>Bibliothèque</h3>');
  assert.equal(context.uiHTML(['', ' sur ', ''], 1, 12), language === 'en' ? '1 of 12' : '1 sur 12');
  assert.equal(context.uiFragment('<optgroup label="Types de projets">'), language === 'en' ? '<optgroup label="Project types">' : '<optgroup label="Types de projets">');
  assert.equal(context.uiHTML(['<div title="', '">', '</div>'], 'Paramètres', 'Enregistrer'), '<div title="Paramètres">Enregistrer</div>');
}
console.log('Translation, template interpolation and user-content isolation passed (FR/EN).');
