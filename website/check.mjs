import {readFile,readdir,stat} from 'node:fs/promises';
import {resolve,join,dirname,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {copy,shotIds,chapters} from './content.mjs';
export async function checkSite(directory) {
  const root=resolve(directory);
  const html=await readFile(join(root,'index.html'),'utf8');
  const manifest=JSON.parse(await readFile(join(root,'manual/DocData/manifest.json'),'utf8'));
  if(manifest.defaultLocale!=='en')throw Error('Manual default locale must be English.');
  for(const lang of ['en','fr'])if(!manifest.pages.some(p=>p.locale===lang&&p.id==='welcome'))throw Error('Missing welcome page: '+lang);
  for(const key of Object.keys(copy.en))if(!copy.fr[key]?.trim())throw Error('Missing French copy: '+key);
  for(const match of html.matchAll(/data-(?:i18n|i18n-label)="([^"]+)"/g))for(const lang of ['en','fr'])if(!copy[lang][match[1]])throw Error('Unknown translation: '+match[1]);
  for(const id of chapters)if(!html.includes('id="'+id+'"'))throw Error('Missing chapter: '+id);
  for(const id of shotIds)if(!html.includes('data-shot="'+id+'"'))throw Error('Missing view: '+id);
  for(const match of html.matchAll(/data-doc="([^"]+)"/g)) {
    const [id,anchor]=match[1].split('#');
    for(const lang of ['en','fr']){
      const page=manifest.pages.find(p=>p.id===id&&p.locale===lang);
      if(!page||anchor&&!page.headings.some(h=>h.id===anchor))throw Error('Invalid manual destination: '+lang+'/'+match[1]);
    }
  }
  for(const match of html.matchAll(/(?:href|src)="([^"]*)"/g)){
    const value=match[1];
    if(!value||value==='#')throw Error('Empty destination.');
    if(/^https:\/\//.test(value))continue;
    if(value.startsWith('#')){if(!html.includes('id="'+value.slice(1)+'"'))throw Error('Missing anchor: '+value);continue;}
    if(!value.startsWith('./'))throw Error('Use relative resources: '+value);
    const path=resolve(root,decodeURIComponent(value.split('#')[0]));
    const delta=relative(root,path);
    if(delta.startsWith('..')||isAbsolute(delta)||!(await stat(path)).isFile())throw Error('Missing/outside resource: '+value);
  }
  const files=[];
  async function walk(path){for(const entry of await readdir(path,{withFileTypes:true})){const child=join(path,entry.name);if(entry.isSymbolicLink())throw Error('Symlink in output');if(entry.isDirectory())await walk(child);else files.push(child);}}
  await walk(root);
  for(const path of files){
    const local=relative(root,path).replaceAll('\\','/');
    if(/(?:^|\/)(?:node_modules|source|\.git|internal|data|\.env)(?:\/|$)|\.(?:sqlite3|db|log|py|exe)$/i.test(local))throw Error('Unexpected site file: '+local);
    const match=local.match(/^assets\/.+\.([a-f0-9]{12})\.(css|js|jpg|png)$/);
    if(match&&createHash('sha256').update(await readFile(path)).digest('hex').slice(0,12)!==match[1])throw Error('Asset revision mismatch: '+local);
  }
  for(const path of ['manual/Documentation.html','manual/DocAI.md','manual/DocData/data.js','manual/DocData/viewer.js','manual/DocData/viewer.css','manual/DocData/media-image.js','manual/DocData/CyDoc.LICENSE.txt','manual/AgentSkills/CyAICodex-Skill.zip','manual/AgentSkills/SKILL.md','manual/AgentSkills/SHA256SUMS.txt','LICENSE.txt','NOTICES.txt'])await stat(join(root,path));
  if(files.some(p=>/(?:media-mesh|three(?:\.min)?\.js)/i.test(p)))throw Error('Unexpected mesh dependency.');
  if(html.includes('DocAI.md')||html.includes('type="module"')||html.includes('<iframe'))throw Error('Human showcase must keep its dedicated classic-script reader link.');
  console.log('Showcase checks passed: '+Object.keys(copy.en).length+' matching strings, '+shotIds.length+' views, '+manifest.pages.length+' manual pages, '+files.length+' packaged files.');
  return {files:files.length,pages:manifest.pages.length};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await checkSite(process.argv[2]||resolve(dirname(fileURLToPath(import.meta.url)),'../dist/website'));
