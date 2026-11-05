'use strict';
(() => {
  let requestId = 0;
  const normalize = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const element = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const flatten = value => typeof value === 'string' ? value : Array.isArray(value)
    ? value.map(flatten).join(' ') : value && typeof value === 'object' ? Object.values(value).map(flatten).join(' ') : '';
  function blockView(block, labels) {
    if (block.type === 'paragraph') return element('p', block.text);
    if (block.type === 'heading') return element('h3', block.text);
    if (block.type === 'note') return element('aside', block.text, 'doc-note');
    if (block.type === 'code') { const pre = element('pre'); pre.append(element('code', block.text)); return pre; }
    if (block.type === 'steps' || block.type === 'list') {
      const list = element(block.type === 'steps' ? 'ol' : 'ul', undefined, 'doc-' + block.type);
      block.items.forEach(item => list.append(element('li', item))); return list;
    }
    if (block.type === 'table') {
      const wrapper = element('div', undefined, 'doc-table-wrap'), table = element('table'), head = element('thead'), row = element('tr');
      block.headers.forEach(text => { const th = element('th', text); th.scope = 'col'; row.append(th); });
      head.append(row); table.append(head); const body = element('tbody');
      block.rows.forEach(values => { const tr = element('tr'); values.forEach(text => tr.append(element('td', text))); body.append(tr); });
      table.append(body); wrapper.append(table); return wrapper;
    }
    if (block.type === 'image') {
      const figure = element('figure', undefined, 'doc-figure'), image = element('img');
      image.src = block.src; image.alt = block.caption; image.loading = 'lazy'; image.decoding = 'async';
      figure.append(image, element('figcaption', block.caption)); return figure;
    }
    if (block.type === 'diagram') {
      const figure = element('figure', undefined, 'doc-diagram'); figure.append(element('figcaption', block.title));
      const flow = element('ol'); flow.setAttribute('aria-label', block.title);
      block.nodes.forEach((item, index) => {
        const card = element('li'); card.append(element('span', String(index + 1).padStart(2,'0'), 'doc-node-number'), element('strong', item.title), element('p', item.text)); flow.append(card);
      });
      figure.append(flow); return figure;
    }
    return element('p');
  }
  window.loadDocumentation = async function (language) {
    const root = document.getElementById('documentation-root'); if (!root) return;
    const lang = language === 'fr' ? 'fr' : 'en', standalone = root.dataset.standalone === 'true';
    if (root.dataset.loaded === lang) return;
    const currentRequest = ++requestId;
    const fallback = lang === 'fr' ? 'Chargement du manuel…' : 'Loading the manual…'; root.replaceChildren(element('p', fallback));
    let data;
    try {
      const response = await fetch('/help/content?lang=' + lang, {credentials:'same-origin'});
      if (!response.ok) throw new Error('Manual unavailable');
      data = await response.json();
      if (currentRequest !== requestId) return;
    } catch {
      if (currentRequest !== requestId) return;
      const error = element('p', lang === 'fr' ? 'Impossible de charger le manuel. Vérifiez que CyAICodex est lancé.' : 'The manual could not be loaded. Check that CyAICodex is running.');
      const retry = element('button', lang === 'fr' ? 'Réessayer' : 'Retry', 'doc-button');
      retry.type = 'button'; retry.addEventListener('click', () => window.loadDocumentation(lang)); root.replaceChildren(error, retry); return;
    }
    const L = data.labels;
    root.dataset.loaded = lang;
    const hero = element('header', undefined, 'doc-hero'), heading = element('div');
    heading.append(element('p', 'CyAICodex · ' + data.version, 'doc-kicker'), element('h1', L.title), element('p', L.subtitle));
    const actions = element('div', undefined, 'doc-actions'); actions.append(element('span', '● ' + L.offline, 'doc-offline'));
    if (standalone) {
      const label = element('label', L.language), select = element('select'); select.setAttribute('aria-label', L.language);
      [['en','English'],['fr','Français']].forEach(([value,text]) => { const o=element('option',text);o.value=value;select.append(o); }); select.value=lang;
      select.addEventListener('change', () => { location.href = '/help?lang=' + select.value + location.hash; }); label.append(select); actions.append(label);
    } else {
      const link = element('a', L.open, 'doc-button'); link.href='/help?lang='+lang;link.target='_blank';link.rel='noopener';actions.append(link);
    }
    const print = element('button',L.print,'doc-button');print.type='button';print.addEventListener('click',()=>window.print());actions.append(print);hero.append(heading,actions);
    const layout=element('div',undefined,'doc-layout'), aside=element('aside',undefined,'doc-sidebar');
    const searchLabel=element('label',L.search), search=element('input');search.type='search';search.placeholder=L.search;search.setAttribute('aria-label',L.search);searchLabel.append(search);
    const counter=element('p',undefined,'doc-counter');counter.setAttribute('role','status');counter.setAttribute('aria-live','polite');
    const clear=element('button',L.clear,'doc-clear');clear.type='button';
    const nav=element('nav');nav.setAttribute('aria-label',L.contents);aside.append(searchLabel,clear,counter,nav);
    const reading=element('div',undefined,'doc-reading'), article=element('article',undefined,'doc-article');article.id='manual-article';article.setAttribute('aria-label',L.title);
    const pagination=element('div',undefined,'doc-pagination');reading.append(article,pagination);layout.append(aside,reading);root.replaceChildren(hero,layout);
    const indexed=data.topics.map(topic=>({...topic,index:normalize(flatten([topic.title,topic.blocks]))}));
    let active=(standalone?decodeURIComponent(location.hash.slice(1)):'')||sessionStorage.getItem('cyaicodex-manual-chapter')||indexed[0].id;
    if (!indexed.some(t=>t.id===active)) active=indexed[0].id;
    function render() {
      const words=normalize(search.value).trim().split(/\s+/).filter(Boolean), filtered=indexed.filter(topic=>words.every(word=>topic.index.includes(word)));
      clear.hidden=!words.length;counter.textContent=filtered.length+' / '+indexed.length+' '+L.results;nav.replaceChildren();pagination.replaceChildren();
      if (!filtered.length) {article.replaceChildren(element('p',L.empty,'doc-empty'));return;}
      if (!filtered.some(t=>t.id===active)) active=filtered[0].id;
      filtered.forEach(topic=>{const b=element('button',topic.title,'doc-topic');b.type='button';if(topic.id===active)b.setAttribute('aria-current','page');b.addEventListener('click',()=>{active=topic.id;render();article.scrollIntoView({block:'start'});});nav.append(b);});
      const topic=filtered.find(t=>t.id===active), index=indexed.findIndex(t=>t.id===active);
      sessionStorage.setItem('cyaicodex-manual-chapter',active);
      if (standalone) history.replaceState(null,'',location.pathname+location.search+'#'+active);
      article.replaceChildren(element('p',L.chapter+' '+String(index+1).padStart(2,'0')+' / '+indexed.length,'doc-kicker'),element('h2',topic.title));
      topic.blocks.forEach(block=>article.append(blockView(block,L)));
      const inResults=filtered.findIndex(t=>t.id===active);
      [[-1,L.previous],[1,L.next]].forEach(([direction,label])=>{const b=element('button',(direction<0?'← ':'')+label+(direction>0?' →':''),'doc-button');b.type='button';b.disabled=!filtered[inResults+direction];b.addEventListener('click',()=>{active=filtered[inResults+direction].id;render();article.scrollIntoView({block:'start'});});pagination.append(b);});
    }
    search.addEventListener('input',render); clear.addEventListener('click',()=>{search.value='';render();search.focus();});render();
  };
  if (document.getElementById('documentation-root')?.dataset.standalone === 'true') {
    window.loadDocumentation(document.documentElement.lang);
  }
})();
