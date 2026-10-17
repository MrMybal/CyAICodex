import asyncio
import base64
import json
from io import BytesIO

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from skills.server import create_app
from skills.store import Store
from skills.images import ImageLibrary, ImageDescription
from skills import assist, local_clients


def png():
    out=BytesIO();Image.new('RGBA',(12,12),(0,150,80,0)).save(out,format='PNG');return out.getvalue()


def rpc(c, token, name, arguments):
    headers={'Accept':'application/json, text/event-stream'}
    if token is not None:headers['Authorization']='Bearer '+token
    return c.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':name,'arguments':arguments}})


def test_import_image_permissions_scope_and_original(tmp_path):
    app=create_app(tmp_path);store=app.state.store
    project=store.add_group('projects','Private')
    write=store.new_connection('Writer',writable=True)['token']
    read=store.new_connection('Reader')['token']
    source=tmp_path/'logo.png';source.write_bytes(png())
    description={'title':'Logo CY','description':'Livre transparent','preserve':'CY intact'}
    with TestClient(app,base_url='http://127.0.0.1:8765') as c:
        args={'description':description,'file_path':str(source)}
        assert rpc(c,None,'import_image',args).status_code==401
        assert rpc(c,read,'import_image',args).json()['result']['isError']
        assert rpc(c,write,'import_image',{**args,'description':{**description,'scope':'project','scope_id':project['id']}}).json()['result']['isError']
        result=rpc(c,write,'import_image',args).json()['result'];assert not result['isError']
        item=json.loads(result['content'][0]['text']);assert app.state.images.path(item['id']).read_bytes()==png()
        for invalid in [dict(args,data_base64='AAAA'),dict(description=description,data_base64='???'),dict(description=description,file_path='relative.png')]:
            assert rpc(c,write,'import_image',invalid).json()['result']['isError']
        result=rpc(c,write,'import_image',{'description':description,'data_base64':base64.b64encode(png()).decode()}).json()['result']
        assert not result['isError']
        assert app.state.images.search()['total']==2


def test_optional_local_access_and_revocation_remain_scoped(tmp_path):
    app=create_app(tmp_path);store=app.state.store
    p=store.add_group('projects','Only this project')
    token=store.new_connection('Revoked')['token']
    with TestClient(app,base_url='http://127.0.0.1:8765') as c:
        assert c.put('/api/preferences',json={'local_no_token':True}).status_code==401
        c.post('/api/session',json={'token':store.setting('admin_token')})
        prefs={'local_no_token':True,'local_writable':False,'project_id':p['id'],'include_global':False,'default_writable':True}
        assert c.put('/api/preferences',json=prefs).status_code==200
        context=rpc(c,None,'get_context',{}).json()['result'];assert not context['isError']
        args={'description':{'title':'Local','description':'Test','scope':'project','scope_id':p['id']},'data_base64':base64.b64encode(png()).decode()}
        assert rpc(c,None,'import_image',args).json()['result']['isError']
        prefs['local_writable']=True;c.put('/api/preferences',json=prefs)
        assert not rpc(c,None,'import_image',args).json()['result']['isError']
        args['description']['scope']='global';assert rpc(c,None,'import_image',args).json()['result']['isError']
        assert c.get('/api/catalog',headers={'Origin':'https://evil.test'}).status_code==403
        assert rpc(c,'invalid','get_context',{}).status_code==401
        connection=c.post('/api/connections',json={'name':'Default write'}).json()
        assert store.authenticate(connection['token'])['writable']
        assert c.put('/api/connections/'+connection['id'],json={'writable':False}).status_code==200
        assert not store.authenticate(connection['token'])['writable']
        prefs['local_no_token']=False;c.put('/api/preferences',json=prefs)
        assert rpc(c,None,'get_context',{}).status_code==401


def test_codex_discovery_without_path(monkeypatch,tmp_path):
    monkeypatch.setattr(local_clients.shutil,'which',lambda _:None)
    monkeypatch.setenv('LOCALAPPDATA',str(tmp_path))
    exe=tmp_path/'OpenAI/Codex/bin/version/codex.exe';exe.parent.mkdir(parents=True);exe.write_bytes(b'test')
    assert local_clients.client_command('codex')==[str(exe)]


@pytest.mark.parametrize('provider',['claude_code','opencode'])
def test_local_adapters_send_prompt_and_images_without_shell(monkeypatch,tmp_path,provider):
    store=Store(tmp_path);item=ImageLibrary(store).add(png(),ImageDescription(title='Logo',description='Image'))
    monkeypatch.setattr(assist,'client_command',lambda *args:['client.exe'])
    seen={}
    async def run(args,text='',cwd=None,env=None,timeout=180):
        seen.update(args=args,text=text,env=env)
        if provider=='claude_code':return json.dumps({'result':'Bonjour','is_error':False})
        return json.dumps({'type':'text','part':{'text':'Bonjour'}})
    monkeypatch.setattr(assist,'run_client',run)
    assert asyncio.run(assist.answer(store,provider,'model',[{'role':'user','content':'Salut'}],[],[item['id']]))=='Bonjour'
    assert 'Salut' in seen['text']
    if provider=='claude_code':
        assert any(x['type']=='image' for x in json.loads(seen['text'])['message']['content'])
        assert '--tools' in seen['args']
    else:
        assert '--file' in seen['args'] and seen['env']['OPENCODE_AUTO_SHARE']=='false'


def test_ollama_payload_and_loopback_validation(monkeypatch,tmp_path):
    store=Store(tmp_path);item=ImageLibrary(store).add(png(),ImageDescription(title='Logo',description='Image'))
    seen={}
    class Client:
        def __init__(self,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,url,**kwargs):
            seen.update(url=url,**kwargs)
            return httpx.Response(200,json={'message':{'content':'Un logo'}},request=httpx.Request('POST',url))
    monkeypatch.setattr(assist.httpx,'AsyncClient',Client)
    assert asyncio.run(assist.answer(store,'ollama','vision',[{'role':'user','content':'Décris'}],[],[item['id']]))=='Un logo'
    assert seen['url']=='http://127.0.0.1:11434/api/chat'
    assert seen['json']['messages'][-1]['images']
    assert not seen['json']['stream']
    store.set_setting('ollama_url','http://example.com')
    with pytest.raises(ValueError):local_clients.ollama_url(store)
