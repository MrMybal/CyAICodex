// copy and assets are embedded by build.mjs; this remains a classic local script.
(() => {
  const readLanguage = () => new URL(location.href).searchParams.get('lang') === 'fr' ? 'fr' : 'en';
  let language = readLanguage();
  const dialog = document.querySelector('#image-viewer');
  const viewerImage = document.querySelector('#viewer-image');
  const viewerCaption = document.querySelector('#viewer-caption');
  const closeButton = document.querySelector('[data-viewer-close]');
  const menu = document.querySelector('.menu-button');
  const navigation = document.querySelector('#primary-nav');
  const shots = [...document.querySelectorAll('[data-shot]')];
  let index = 0;
  let openedBy;
  let previousScroll = 0;
  let previousOverflow = '';
  function docUrl(target) {
    const [page, anchor] = target.split('#');
    return './manual/Documentation.html#/' + language + '/' + encodeURIComponent(page) + (anchor ? '/' + encodeURIComponent(anchor) : '');
  }
  function localize() {
    const text = copy[language];
    document.documentElement.lang = language;
    document.title = text['meta.title'];
    document.querySelector('meta[name="description"]').content = text['meta.description'];
    document.querySelector('meta[property="og:title"]').content = text['meta.title'];
    document.querySelector('meta[property="og:description"]').content = text['meta.description'];
    document.querySelector('meta[property="og:image"]').content = assets['skills-library'][language].path;
    document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = text[el.dataset.i18n]; });
    document.querySelectorAll('[data-i18n-label]').forEach(el => { el.setAttribute('aria-label', text[el.dataset.i18nLabel]); });
    document.querySelectorAll('[data-doc]').forEach(el => { el.href = docUrl(el.dataset.doc); });
    document.querySelectorAll('[data-lang]').forEach(el => { el.setAttribute('aria-pressed', String(el.dataset.lang === language)); });
    shots.forEach(button => {
      const id = button.dataset.shot;
      const image = button.querySelector('img');
      const source = assets[id][language];
      image.src = source.path;
      image.width = source.width;
      image.height = source.height;
      image.alt = text['shot.' + id + '.alt'];
      button.setAttribute('aria-label', text['viewer.open'] + ': ' + text['shot.' + id + '.caption']);
    });
    if (dialog.open) showImage(index);
  }
  function setLanguage(value) {
    language = value === 'fr' ? 'fr' : 'en';
    const url = new URL(location.href);
    url.searchParams.set('lang', language);
    history.replaceState(null, '', url);
    localize();
  }
  function showImage(value) {
    index = (value + shots.length) % shots.length;
    const image = shots[index].querySelector('img');
    viewerImage.src = image.src;
    viewerImage.alt = image.alt;
    viewerCaption.textContent = copy[language]['shot.' + shots[index].dataset.shot + '.caption'];
    document.querySelector('#viewer-count').textContent = (index + 1) + ' / ' + shots.length;
  }
  function openImage(button) {
    openedBy = button;
    previousScroll = window.scrollY;
    previousOverflow = document.documentElement.style.overflow;
    showImage(shots.indexOf(button));
    dialog.showModal();
    document.documentElement.style.overflow = 'hidden';
    closeButton.focus();
  }
  function closeMenu() { menu.setAttribute('aria-expanded', 'false'); navigation.dataset.open = 'false'; }
  shots.forEach(button => button.addEventListener('click', () => openImage(button)));
  document.querySelectorAll('[data-lang]').forEach(button => button.addEventListener('click', () => setLanguage(button.dataset.lang)));
  menu.addEventListener('click', () => {
    const expanded = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(expanded));
    navigation.dataset.open = String(expanded);
  });
  navigation.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  closeButton.addEventListener('click', () => dialog.close());
  document.querySelector('[data-viewer-prev]').addEventListener('click', () => showImage(index - 1));
  document.querySelector('[data-viewer-next]').addEventListener('click', () => showImage(index + 1));
  dialog.addEventListener('keydown', event => {
    if (event.key === 'Tab') {
      const buttons = [...dialog.querySelectorAll('button')];
      const current = buttons.indexOf(document.activeElement);
      event.preventDefault();
      buttons[(current + (event.shiftKey ? -1 : 1) + buttons.length) % buttons.length].focus();
    }
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') { event.preventDefault(); showImage(index + (event.key === 'ArrowRight' ? 1 : -1)); }
  });
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => {
    viewerImage.removeAttribute('src');
    document.documentElement.style.overflow = previousOverflow;
    window.scrollTo({top: previousScroll, behavior: 'instant'});
    openedBy?.focus({preventScroll: true});
  });
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && !dialog.open) { closeMenu(); if(document.activeElement.closest('#primary-nav'))menu.focus(); } });
  let scheduled = false;
  const chapterLinks = [...document.querySelectorAll('[data-chapter]')];
  function updateChapter() {
    scheduled = false;
    const threshold = document.querySelector('.site-header').offsetHeight + document.querySelector('.chapters').offsetHeight + 28;
    let current;
    chapterLinks.forEach(link => { if (document.getElementById(link.dataset.chapter).getBoundingClientRect().top <= threshold) current = link; });
    chapterLinks.forEach(link => { if(link===current)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current'); });
  }
  function scheduleChapter() { if(!scheduled){scheduled=true; requestAnimationFrame(updateChapter);} }
  window.addEventListener('scroll', scheduleChapter, {passive:true});
  window.addEventListener('resize', scheduleChapter);
  window.addEventListener('popstate', () => {language = readLanguage();localize();});
  const initial = new URL(location.href);
  if(initial.searchParams.has('lang') && !['en','fr'].includes(initial.searchParams.get('lang')))setLanguage('en');
  else localize();
  scheduleChapter();
})();
