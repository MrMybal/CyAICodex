import {createServer} from 'node:http';
import {readFile,stat,realpath} from 'node:fs/promises';
import {resolve,dirname,relative,isAbsolute,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=await realpath(resolve(dirname(fileURLToPath(import.meta.url)),'../dist/website'));
const prefix='/preview/cyaicodex/';
const port=Number(process.argv.find(v=>v.startsWith('--port='))?.slice(7)||8892);
if(!Number.isInteger(port)||port<0||port>65535)throw Error('Use --port=0..65535.');
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.txt':'text/plain; charset=utf-8','.md':'text/markdown; charset=utf-8'};
const server=createServer(async(req,res)=>{
  try{
    if(!['GET','HEAD'].includes(req.method)){res.writeHead(405).end();return;}
    const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    if(path==='/'){res.writeHead(302,{Location:prefix}).end();return;}
    if(!path.startsWith(prefix)){res.writeHead(404).end();return;}
    let target=resolve(root,path.slice(prefix.length));
    if((await stat(target)).isDirectory())target=resolve(target,'index.html');
    target=await realpath(target);
    const delta=relative(root,target);
    if(delta.startsWith('..')||isAbsolute(delta)){res.writeHead(403).end();return;}
    const bytes=await readFile(target);
    res.writeHead(200,{'Content-Type':types[extname(target)]||'application/octet-stream','Content-Length':bytes.length,'Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'});
    res.end(req.method==='HEAD'?undefined:bytes);
  }catch{res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'}).end('Local file not found.');}
});
await new Promise((done,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',done);});
console.log('CyAICodex showcase: http://127.0.0.1:'+server.address().port+prefix);
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>server.close(()=>process.exit(0)));
