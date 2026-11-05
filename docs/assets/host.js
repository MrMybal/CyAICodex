// Application license attribution. The CyDoc reader itself remains MIT licensed.
(() => {
  const root = document.getElementById('app');
  const update = () => {
    const label = root.querySelector('.footer > div > span:last-child');
    const value = document.documentElement.lang === 'fr'
      ? 'Application : AGPL-3.0-only · Lecteur CyDoc : MIT'
      : 'Application: AGPL-3.0-only · CyDoc reader: MIT';
    if (label && label.textContent !== value) label.textContent = value;
  };
  new MutationObserver(update).observe(root, { childList: true, subtree: true });
  update();
})();
