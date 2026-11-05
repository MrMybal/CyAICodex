// DOM contract fixture: no browser is launched and no file URL is navigated.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('skills/web/help.js','utf8');
const flush = () => new Promise(resolve => setImmediate(resolve));
function fixture({language='en',page='images',hash='',legacy=false,ok=true}={}) {
  const events={},calls=[],status={textContent:''};
  const document={
    documentElement:{lang:language},
    body:{classList:{contains:value=>legacy&&value==='help-launcher'}},
    querySelector:()=>({id:'page-'+page}),
    getElementById:id=>id==='help-launch-status'?status:null,
    addEventListener:(name,fn)=>{events[name]=fn;}
  };
  const context={document,location:{hash},URLSearchParams,window:{},fetch:async(url,options)=>{
    calls.push({url,...options,body:JSON.parse(options.body)});
    return {ok,json:async()=>ok?{opened:true}:{detail:'Authentication required'}};
  }};
  vm.createContext(context);vm.runInContext(source,context);
  return {events,calls,status,window:context.window};
}
(async()=>{
  for(const language of ['en','fr']) {
    for(const [screen,chapter] of Object.entries({library:'skills',images:'images',projects:'projects',assistant:'assistant',connections:'mcp',settings:'providers'})) {
      const f=fixture({language,page:screen});let prevented=false;
      f.events.keydown({key:'F1',target:{closest:()=>null},preventDefault:()=>{prevented=true;}});
      await flush();assert(prevented);
      assert.equal(f.calls.length,1);assert.equal(f.calls[0].url,'/api/help/open');
      assert.equal(f.calls[0].credentials,'same-origin');assert.equal(f.calls[0].method,'POST');
      assert.equal(f.calls[0].body.language,language);assert.equal(f.calls[0].body.page,chapter);
    }
    const f=fixture({language});
    const tagged={dataset:{helpPage:'skills',helpSection:'illustration',helpMedia:'skills-illustration'}};
    f.events.keydown({key:'F1',target:{closest:()=>tagged},preventDefault:()=>{}});await flush();
    assert.equal(f.calls[0].body.anchor,'illustration');assert.equal(f.calls[0].body.media,'skills-illustration');
    const button={dataset:{openHelp:'context'},closest:()=>null};
    f.events.click({target:{closest:()=>button},preventDefault:()=>{}});await flush();assert.equal(f.calls[1].body.page,'images');
    await f.window.openDocumentation();assert.equal(f.calls[2].body.page,'welcome');
  }
  for(const [hash,page,anchor,media] of [
    ['#backup','backup',undefined,undefined],
    ['#/en/skills/illustration?media=skills-illustration','skills','illustration','skills-illustration'],
    ['#%broken','welcome',undefined,undefined]
  ]) {
    const f=fixture({legacy:true,hash});await flush();
    assert.equal(f.calls[0].body.page,page);
    assert.equal(f.calls[0].body.anchor??undefined,anchor);
    assert.equal(f.calls[0].body.media??undefined,media);
    assert.match(f.status.textContent,/opened/);
  }
  const failure=fixture({legacy:true,hash:'#backup',ok:false});await flush();
  assert.equal(failure.status.textContent,'Authentication required');
  console.log('Help DOM contracts passed: F1, all screens, section/media, EN/FR, legacy links and errors. No native browser test performed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
