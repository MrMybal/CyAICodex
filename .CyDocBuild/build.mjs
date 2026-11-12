import { readFile, writeFile, mkdir, cp, rm, realpath, access } from 'node:fs/promises';
import { resolve, dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { extractComments } from 'cydoc/extract';
import { importApi } from 'cydoc/api-import';

const work = await realpath(dirname(fileURLToPath(import.meta.url)));
const root = await realpath(resolve(work, '..'));
const configPath = join(work, 'cydoc.config.json');
const config = JSON.parse(await readFile(configPath, 'utf8'));
const out = resolve(work, config.out);
if (relative(root, out).replaceAll('\\','/') !== 'Documentation') throw Error('Unexpected output');
async function cleanGenerated(path, expected) {
  if (relative(root, path).replaceAll('\\','/') !== expected) throw Error('Unsafe output path');
  try { if (await realpath(path) !== path) throw Error('Output must not be a link'); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  await rm(path, {recursive:true, force:true});
}
await cleanGenerated(join(work, '.generated'), '.CyDocBuild/.generated');
// Clean only CyDoc-owned data, leaving unrelated files beside the reader intact.
await cleanGenerated(join(out, 'DocData'), 'Documentation/DocData');
const input = resolve(work, config.content);
if (input !== join(work, '.generated', 'manual')) throw Error('Unexpected content path');
await mkdir(dirname(input), {recursive:true});
await cp(join(work, 'manual'), input, {recursive:true});
const front = (page, revision, extra={}) => {
  const fields = {id:page.id, title:page.title, description:page.description, section:page.locale==='fr'?'Références / API publique':'Reference / Public API', parent:'tools', order:230, revision, ...(page.locale==='fr'?{sourceRevision:revision}:{}), ...extra};
  return '---\n' + Object.entries(fields).map(([k,v])=>k+': '+JSON.stringify(v)).join('\n')+'\n---\n\n';
};
// One explicit source allowlist. Only tagged prose is extracted; no file listings.
for (const page of extractComments(await readFile(join(root, 'skills/documentation.py'),'utf8'), 'skills/documentation.py')) {
  page.description = page.locale==='fr'?'Adresses locales, paramètres et erreurs des fonctions d’aide Python.':'Local URLs, parameters and errors of the Python help functions.';
  await writeFile(join(input,page.locale,page.id+'.md'),front(page,2,{symbol:page.symbol,source:page.source})+page.markdown+'\n');
}
let python = process.env.PYTHON;
if (!python) {
  const local = join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
  try { await access(local); python=local; } catch { python=process.platform==='win32'?'python':'python3'; }
}
function run(command,args) {
  const result=spawnSync(command,args,{cwd:root,stdio:'inherit'});
  if(result.error)throw result.error;
  if(result.status!==0)process.exit(result.status||1);
}
run(python,[join(work,'export-api.py')]);
const revision=JSON.parse(await readFile(join(work,'api-prose.json'),'utf8')).revision;
const pages=await importApi(['en','fr'].map(locale=>({format:'cydoc',path:'.generated/api-'+locale+'.json',prefix:'api',locale})),{base:work,locales:config.locales});
for(const page of pages) {
  const neutral=JSON.parse(await readFile(join(work,'.generated','api-'+page.locale+'.json'),'utf8')).symbols.find(s=>s.name===page.symbol);
  page.description=neutral.description;
  // The reader already displays this prose in its article header.
  if(page.markdown.startsWith(neutral.description))page.markdown=page.markdown.slice(neutral.description.length).trimStart();
  await writeFile(join(input,page.locale,page.id+'.md'),front(page,revision,{symbol:page.symbol})+page.markdown+'\n');
}
const version=(await readFile(join(root,'skills/__init__.py'),'utf8')).match(/__version__ = "([^"]+)"/)[1];
if(config.version!==version)throw Error('Documentation and application versions differ');
run(process.execPath,[join(work,'node_modules/cydoc/tools/cli.mjs'),process.argv.includes('--check')?'check':'build',configPath]);
await cp(join(work,'vendor/LICENSE'),join(out,'DocData/CyDoc.LICENSE.txt'));
// Host-owned HTML shell: English metadata and app icon; native CyDoc viewer unchanged.
await cp(join(work,'reader.html'),join(out,'Documentation.html'));
await cp(join(work,'index-redirect.html'),join(out,'index.html'));
const assistantGuide=await readFile(join(out,'DocAI.md'),'utf8');
await writeFile(join(out,'DocAI.md'),assistantGuide+'\n---\n\n'+await readFile(join(work,'.generated/app-ai.md'),'utf8'));
const manifest=JSON.parse(await readFile(join(out,'DocData/manifest.json'),'utf8'));
const report=JSON.parse(await readFile(join(out,'DocData/translation-report.json'),'utf8'));
if(report.missing.length||report.outdated.length||report.untracked.length)throw Error('Incomplete translations');
for(const id of new Set(manifest.pages.map(p=>p.id))) {
 const translated=manifest.pages.filter(p=>p.id===id);
 if(translated.length!==2)throw Error('Both languages required: '+id);
 const anchors=p=>p.headings.map(h=>h.id).sort().join('|');
 if(anchors(translated[0])!==anchors(translated[1]))throw Error('Translated anchors differ: '+id);
}
if(manifest.pages.some(p=>['project-readme','building-help','translation-report','DocAI'].includes(p.id)||p.kind==='source'))throw Error('Internal content in human manual');
run(python,[join(root,'tools/package_agent_skill.py'),'--output',join(out,'AgentSkills')]);
console.log('CyAICodex: '+manifest.pages.length+' translated pages; image module only; ready in Documentation/Documentation.html.');
