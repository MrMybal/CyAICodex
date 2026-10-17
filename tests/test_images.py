import asyncio
import hashlib
import json
from io import BytesIO

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from skills.assist import answer
from skills.images import ImageDescription, ImageLibrary
from skills.server import create_app
from skills.store import Conflict, Store


def picture():
    buffer=BytesIO()
    Image.new('RGBA',(40,30),(20,100,70,0)).save(buffer,format='PNG')
    return buffer.getvalue()


def description(**kwargs):
    return ImageDescription(title='Logo CY',description='Livre ouvert vert',preserve='Conserver le monogramme exactement',**kwargs)


def test_original_preserved_search_scope_and_history(tmp_path):
    store=Store(tmp_path);library=ImageLibrary(store)
    project=store.add_group('projects','Private')
    raw=picture();item=library.add(raw,description(scope='project',scope_id=project['id']))
    assert library.path(item['id']).read_bytes()==raw
    assert item['sha256']==hashlib.sha256(raw).hexdigest()
    assert item['transparent']
    assert library.search('monogram')['total']==1
    assert library.search(context=store.context())['total']==0
    with pytest.raises(KeyError):library.preview(item['id'],store.context())
    assert library.get(item['id'],store.context(project_id=project['id']))['id']==item['id']
    library.update(item['id'],description(status='draft'),1)
    with pytest.raises(Conflict):library.update(item['id'],description(),1)
    assert len(library.history(item['id']))==2
    assert library.path(item['id']).read_bytes()==raw
    assert library.search()['total']==0


def test_invalid_uploads_do_not_leave_files(tmp_path):
    library=ImageLibrary(Store(tmp_path))
    for raw in [b'',b'<svg onload="alert(1)"></svg>',b'not an image',picture()[:20]]:
        with pytest.raises(ValueError):library.add(raw,description())
    with pytest.raises(ValueError):library.add(picture(),description(scope='project',scope_id='absent'))
    assert list(library.folder.iterdir())==[]


def test_image_api_and_mcp_scopes(tmp_path):
    app=create_app(tmp_path);store=app.state.store
    with TestClient(app,base_url='http://127.0.0.1:8765') as client:
        upload=lambda:client.post('/api/images',files={'file':('../../image.png',picture(),'image/png')},data={'metadata':description().model_dump_json()})
        assert upload().status_code==401
        client.post('/api/session',json={'token':store.setting('admin_token')})
        response=upload();assert response.status_code==200,response.text
        item=response.json();identifier=item['id']
        assert client.get(f'/api/images/{identifier}/file').content==picture()
        assert client.get(f'/api/images/{identifier}/preview').headers['content-type']=='image/png'
        assert client.get('/api/images?q=monogram').json()['total']==1
        token=store.new_connection('Read only')['token']
        def call(name,arguments):
            r=client.post('/mcp',headers={'Authorization':'Bearer '+token,'Accept':'application/json, text/event-stream'},json={
                'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':name,'arguments':arguments}})
            assert r.status_code==200,r.text
            return r.json()['result']
        assert not call('get_image',{'image_id':identifier})['isError']
        visual=call('view_image',{'image_id':identifier})
        assert not visual['isError']
        assert any(c['type']=='image' for c in visual['content'])
        assert call('update_image',{'image_id':identifier,'expected_version':1,'description':description().model_dump()})['isError']
        project=store.add_group('projects','Private')
        app.state.images.update(identifier,description(scope='project',scope_id=project['id']),1)
        assert call('view_image',{'image_id':identifier})['isError']


@pytest.mark.parametrize('provider',['openai','claude'])
def test_assistant_receives_visual_and_preservation_instructions(tmp_path,monkeypatch,provider):
    store=Store(tmp_path);image=ImageLibrary(store).add(picture(),description())
    monkeypatch.setenv('OPENAI_API_KEY' if provider=='openai' else 'ANTHROPIC_API_KEY','test-key')
    captured={}
    class Client:
        def __init__(self,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,url,**kwargs):
            captured.update(kwargs['json'])
            payload={'output':[{'content':[{'type':'output_text','text':'ok'}]}]} if provider=='openai' else {'content':[{'type':'text','text':'ok'}]}
            return httpx.Response(200,json=payload)
    monkeypatch.setattr('skills.assist.httpx.AsyncClient',Client)
    messages=[{'role':'user','content':'Décris le logo'}]
    assert asyncio.run(answer(store,provider,'vision-model',messages,[],[image['id']]))=='ok'
    assert messages[0]['content']=='Décris le logo'
    content=captured['input' if provider=='openai' else 'messages'][0]['content']
    assert any(c['type']==('input_image' if provider=='openai' else 'image') for c in content)
    assert 'Conserver le monogramme exactement' in captured['instructions' if provider=='openai' else 'system']
