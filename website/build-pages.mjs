import {cp,mkdir,readFile,realpath,rm} from 'node:fs/promises';
import {resolve,dirname,join,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {checkSite} from './check.mjs';

const source=await realpath(dirname(fileURLToPath(import.meta.url)));
const root=await realpath(resolve(source,'..'));
const output=resolve(root,'dist/pages');
const build=spawnSync(process.execPath,[join(source,'build.mjs')],{cwd:root,stdio:'inherit'});
if(build.error)throw build.error;
if(build.status!==0)process.exit(build.status||1);

// Keep the existing manual URLs at the root and add a self-contained showcase.
await mkdir(dirname(output),{recursive:true});
if(await realpath(dirname(output))!==resolve(root,'dist')||relative(root,output)!==join('dist','pages'))throw Error('Unsafe Pages output.');
try{if(await realpath(output)!==output)throw Error('Pages output must not be a link.');}catch(error){if(error.code!=='ENOENT')throw error;}
await rm(output,{recursive:true,force:true});
await cp(join(root,'Documentation'),output,{recursive:true});
await cp(join(root,'dist/website'),join(output,'showcase'),{recursive:true});
await cp(join(root,'dist/website/.nojekyll'),join(output,'.nojekyll'));
await checkSite(join(output,'showcase'));
for(const name of ['Documentation.html','index.html','DocAI.md','DocData/manifest.json','DocData/data.js','DocData/viewer.js','DocData/viewer.css']) {
  const original=await readFile(join(root,'Documentation',name));
  if(!original.equals(await readFile(join(output,name))))throw Error('Existing manual entry changed: '+name);
}
console.log('GitHub Pages artifact ready in dist/pages/: existing manual at root, showcase at showcase/.');
