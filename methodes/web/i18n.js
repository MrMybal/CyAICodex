'use strict';
const uiLanguage = document.documentElement.lang === 'en' ? 'en' : 'fr';
function uiText(value) {
  if (uiLanguage !== 'en') return value;
  const key = value.trim();
  return Object.hasOwn(UI_TRANSLATIONS, key) ? value.replace(key, () => UI_TRANSLATIONS[key]) : value;
}
// Translate only static template segments. Interpolated user content stays untouched.
function uiFragment(value) {
  const direct = uiText(value);
  if (direct !== value || !/[<>]/.test(value)) return direct;
  return value.replace(/(^|>)([^<>]*)(?=<|$)/g, (_, prefix, text) => prefix + uiText(text))
    .replace(/\b(label|placeholder|aria-label|alt|title)="([^"]*)"/g, (_, name, text) => name + '="' + uiText(text).replace(/"/g, '&quot;') + '"');
}
function uiHTML(strings, ...values) {
  return strings.reduce((result, part, index) => result + uiFragment(part) + (index < values.length ? values[index] : ''), '');
}
