import {readFile,writeFile,mkdir,cp,rm,realpath,stat} from 'node:fs/promises';
import {resolve,dirname,relative,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {copy,shotIds,destinations} from './content.mjs';
import {renderPage} from './template.mjs';
import {checkSite} from './check.mjs';

const source=await realpath(dirname(fileURLToPath(import.meta.url)));
const root=await realpath(resolve(source,'..'));
const output=resolve(root,'dist/website');
const digest=bytes=>createHash('sha256').update(bytes).digest('hex').slice(0,12);
if(Number(process.versions.node.split('.')[0])<22)throw Error('Node.js 22+ is required.');
if(!process.argv.includes('--skip-manual')) {
  const build=spawnSync(process.execPath,[join(root,'.CyDocBuild/build.mjs')],{cwd:root,stdio:'inherit'});
  if(build.error)throw build.error;
  if(build.status!==0)process.exit(build.status||1);
}
const manifest=JSON.parse(await readFile(join(root,'Documentation/DocData/manifest.json'),'utf8'));
const report=JSON.parse(await readFile(join(root,'Documentation/DocData/translation-report.json'),'utf8'));
const version=(await readFile(join(root,'skills/__init__.py'),'utf8')).match(/__version__ = "([^"]+)"/)[1];
if(manifest.version!==version)throw Error('Rebuild the application manual: version mismatch.');
if(report.missing.length||report.outdated.length||report.untracked.length)throw Error('The manual needs current English/French translations.');
if(!copy.en['hero.status'].includes(version)||!destinations.download.includes('/v'+version+'/'))throw Error('Update showcase version and verified download destination.');
if(JSON.stringify(Object.keys(copy.en).sort())!==JSON.stringify(Object.keys(copy.fr).sort()))throw Error('Translation keys differ.');
for(const [lang,strings] of Object.entries(copy))for(const [key,value] of Object.entries(strings))if(typeof value!=='string'||!value.trim())throw Error('Empty translation: '+lang+'/'+key);

// Only this generated directory is replaced; reject links or paths outside dist.
await mkdir(dirname(output),{recursive:true});
if(await realpath(dirname(output))!==resolve(root,'dist')||relative(root,output)!==join('dist','website'))throw Error('Unsafe showcase output.');
try{if(await realpath(output)!==output)throw Error('Showcase output must not be a link.');}catch(error){if(error.code!=='ENOENT')throw error;}
await rm(output,{recursive:true,force:true});
await mkdir(join(output,'assets'),{recursive:true});
const assets={};
function dimensions(bytes) {
  if(bytes.subarray(1,4).toString()==='PNG')return {width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20)};
  if(bytes[0]!==0xff||bytes[1]!==0xd8)throw Error('Expected a PNG or JPEG screenshot.');
  let offset=2;
  while(offset<bytes.length){
    if(bytes[offset++]!==0xff)continue;
    let marker=bytes[offset++];while(marker===0xff)marker=bytes[offset++];
    if(marker===0xd9||marker===0xda)break;
    const length=bytes.readUInt16BE(offset);
    if([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf].includes(marker))return {height:bytes.readUInt16BE(offset+3),width:bytes.readUInt16BE(offset+5)};
    offset+=length;
  }
  throw Error('Screenshot dimensions not found.');
}
async function asset(path,name) {
  const bytes=await readFile(join(source,path));
  const dot=name.lastIndexOf('.');
  const file=name.slice(0,dot)+'.'+digest(bytes)+name.slice(dot);
  await writeFile(join(output,'assets',file),bytes);
  return './assets/'+file;
}
for(const id of shotIds){
  assets[id]={};
  for(const lang of ['en','fr']){
    const path='assets/screenshots/'+id+'.'+lang+'.jpg';
    assets[id][lang]={path:await asset(path,id+'.'+lang+'.jpg'),...dimensions(await readFile(join(source,path)))};
  }
}
assets.logo=await asset('assets/logo.png','logo.png');
const css=await asset('styles.css','site.css');
const script='"use strict";\nconst copy='+JSON.stringify(copy)+';\nconst assets='+JSON.stringify(assets)+';\n'+await readFile(join(source,'main.js'),'utf8');
const js='./assets/site.'+digest(script)+'.js';
await writeFile(join(output,js),script);
await writeFile(join(output,'index.html'),renderPage(assets).replace('__CSS__',css).replace('__JS__',js));
await cp(join(root,'Documentation'),join(output,'manual'),{recursive:true});
await cp(join(root,'LICENSE'),join(output,'LICENSE.txt'));
await writeFile(join(output,'NOTICES.txt'),'CyAICodex showcase and application: AGPL-3.0-only. Copyright (c) 2026 Cyberalien.\n\nThe bundled CyDoc reader is MIT licensed. Its full license is in manual/DocData/CyDoc.LICENSE.txt. Other reader component notices remain with the complete manual export.\nNo application installer, credentials or library database is included.\n');
await writeFile(join(output,'.nojekyll'),'');
await checkSite(output);
console.log('Showcase ready in dist/website/index.html (EN/FR; '+shotIds.length+' localized views; complete local CyDoc manual).');
