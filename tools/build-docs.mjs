import { readFile, writeFile, mkdir, cp, rm, realpath } from 'node:fs/promises';
import { resolve, dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { extractComments } from 'cydoc/extract';

const root = await realpath(resolve(dirname(fileURLToPath(import.meta.url)), '..'));
const config = JSON.parse(await readFile(join(root, 'cydoc.config.json'), 'utf8'));
// Only these generated application-owned directories may be cleaned.
for (const folder of ['build/help', 'build/cydoc-input']) {
  const target = resolve(root, folder);
  if (relative(root, target).replaceAll('\\','/') !== folder) throw Error('Unsafe documentation output');
  try { if (await realpath(target) !== target) throw Error('Documentation output cannot be a link'); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  await rm(target, {recursive:true, force:true});
}
const input = join(root, config.content);
await mkdir(input, {recursive:true});
await cp(join(root, 'docs/content'), input, {recursive:true});
const revisions = JSON.parse(await readFile(join(root,'docs/generated-revisions.json'),'utf8'));
const extracted = extractComments(await readFile(join(root,'skills/documentation.py'),'utf8'), 'skills/documentation.py');
for (const page of extracted) {
  const tracking = revisions[page.id];
  if (!tracking) throw Error('Track annotation revisions explicitly: ' + page.id);
  const revision = page.locale === 'en' ? tracking.revision : tracking.sourceRevision[page.locale];
  const front = `---\nid: ${page.id}\ntitle: ${page.title}\ndescription: ${page.title}\nsection: ${page.section}\norder: 230\nrevision: ${tracking.revision}\n${page.locale==='en'?'':`sourceRevision: ${revision}\n`}symbol: ${page.symbol}\nsource: ${page.source}\n---\n\n`;
  await writeFile(join(input,page.locale,page.id+'.md'),front+page.markdown+'\n');
}
const trackingFront = (id,lang) => {
  const value=revisions[id];
  if (!value || (lang!=='en' && !value.sourceRevision[lang])) throw Error('Missing generated-page revision: '+id);
  return `revision: ${value.revision}\n${lang==='en'?'':`sourceRevision: ${value.sourceRevision[lang]}\n`}`;
};
// Keep the complete repository reference, not just the former twenty chapters.
for (const lang of ['en','fr']) {
  const title=lang==='en'?'Application reference':'Référence de l’application';
  let source=await readFile(join(root,lang==='en'?'README.md':'README.fr.md'),'utf8');
  let media=0;
  source=source.replace(/<\/?details>/g,'').replace(/<summary>(.*?)<\/summary>/g,'**$1**')
    .replace(/^#{1,6} (.+)$/gm,'**$1**')
    .replace(/!\[([^\]]*)\]\(docs\/assets\/images\/([^)]+)\)/g,(_,alt,name)=>'```image\n'+JSON.stringify({id:'readme-image-'+(++media),src:'assets/images/'+name,alt,controls:'minimal'})+'\n```')
    .replace(/\]\(README(?:\.fr)?\.md\)/g,'](doc:project-readme#content)')
    .replace(/\]\(LICENSE\)/g,'](doc:license#license-text)')
    .replace(/\]\(CHANGELOG\.md\)/g,'](doc:changelog#content)')
    .replace(/\]\(docs\/content\/(?:en|fr)\/building-help\.md\)/g,'](doc:building-help#content)');
  await writeFile(join(input,lang,'project-readme.md'),`---\nid: project-readme\ntitle: ${title}\ndescription: ${title}\nsection: ${lang==='en'?'Reference':'Références'}\norder: 220\n${trackingFront('project-readme',lang)}---\n\n## ${title} {#content}\n\n${source}\n`);
  const license=await readFile(join(root,'LICENSE'),'utf8');
  await writeFile(join(input,lang,'license.md'),`---\nid: license\ntitle: ${lang==='en'?'License':'Licence'}\nsection: ${lang==='en'?'Reference':'Références'}\norder: 280\n${trackingFront('license',lang)}---\n\n## ${lang==='en'?'Official license text':'Texte officiel de la licence'} {#license-text}\n\n${lang==='en'?'The following is the original English AGPL v3 license. Third-party components keep their own licenses.':'Le texte suivant est la licence AGPL v3 originale en anglais. Les composants tiers conservent leurs licences.'}\n\n\`\`\`text\n${license}\n\`\`\`\n`);
}
const version=(await readFile(join(root,'skills/__init__.py'),'utf8')).match(/__version__ = "([^"]+)"/)[1];
if(config.version!==version)throw Error('Documentation/application versions differ');
const cli=join(root,'node_modules/cydoc/tools/cli.mjs');
const built=spawnSync(process.execPath,[cli,process.argv.includes('--check')?'check':'build',join(root,'cydoc.config.json')],{stdio:'inherit'});
if(built.status!==0)process.exit(built.status||1);
const out=join(root,config.out);
await cp(join(root,'vendor/cydoc/LICENSE'),join(out,'CyDoc.LICENSE.txt'));
// Application-owned HTML shell; the CyDoc bundles and local resource providers stay unmodified.
await cp(join(root,'docs/reader.html'),join(out,'index.html'));
const manifest=JSON.parse(await readFile(join(out,'manifest.json'),'utf8'));
const report=JSON.parse(await readFile(join(out,'translation-report.json'),'utf8'));
if(report.missing.length||report.outdated.length||report.untracked.length)throw Error('Resolve translation tracking: '+JSON.stringify(report));
for(const id of new Set(manifest.pages.map(p=>p.id))){
  const pages=manifest.pages.filter(p=>p.id===id);
  if(pages.length!==2)throw Error('Both translations required: '+id);
  const ids=p=>p.headings.map(h=>h.id).sort().join('|');
  if(ids(pages[0])!==ids(pages[1]))throw Error('Translated anchors differ: '+id);
}
console.log('CyAICodex: local CyDoc export ready; image module only; translations current.');
