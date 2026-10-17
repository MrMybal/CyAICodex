import asyncio
import json
import pytest

from fastapi.testclient import TestClient
from skills.server import create_app
from skills.store import Method


def test_api_session_origin_and_conflicts(tmp_path):
    app = create_app(tmp_path)
    with TestClient(app, base_url='http://127.0.0.1:8765') as c:
        assert c.get('/api/catalog').status_code == 401
        token = app.state.store.setting('admin_token')
        assert c.post('/api/session', json={'token': token}, headers={'Origin': 'https://evil.example'}).status_code == 403
        assert c.post('/api/session', json={'token': token}).status_code == 200
        assert c.get('/api/catalog').status_code == 200
        assert c.get('/api/catalog', headers={'Host': 'evil.example:8765'}).status_code == 403
        body = {'method': {'title': 'Test', 'content': 'Contenu'}}
        result = c.post('/api/methods', json=body).json()
        assert c.put('/api/methods/'+result['id'], json={**body,'version':1}).status_code == 200
        assert c.put('/api/methods/'+result['id'], json={**body,'version':1}).status_code == 409
        assert 'admin_token' not in c.get('/api/export').text
        assert c.get('/').headers['content-security-policy']


def rpc(client, token, method, params, request_id=1):
    return client.post('/mcp', headers={'Authorization': 'Bearer '+token,
        'Accept': 'application/json, text/event-stream', 'MCP-Protocol-Version':'2025-06-18'},
        json={'jsonrpc':'2.0','id':request_id,'method':method,'params':params})


@pytest.mark.parametrize('skill_names', [False, True])
def test_mcp_initialize_tools_scoping_and_write_permissions(tmp_path, skill_names):
    app = create_app(tmp_path)
    s = app.state.store
    project = s.add_group('projects','Private')
    secret = s.save(Method(title='Secret',content='Private text',scope='project',scope_id=project['id']))
    public = s.save(Method(title='Global',content='Global text'))
    read = s.new_connection('Read')['token']
    write = s.new_connection('Write', project_id=project['id'], writable=True)['token']
    with TestClient(app, base_url='http://127.0.0.1:8765') as c:
        assert c.post('/mcp',json={}).status_code==401
        init=rpc(c,read,'initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'test','version':'1'}})
        assert init.status_code==200, init.text
        assert init.json()['result']['serverInfo']['name']=='CyAICodex'
        tools=rpc(c,read,'tools/list',{}).json()['result']['tools']
        assert {t['name'] for t in tools} >= {'search_methods','get_method','create_method','update_method', 'search_skills', 'get_skill', 'create_skill', 'update_skill'}
        def call(token,name,args):
            if skill_names:
                name = name.replace('methods', 'skills').replace('method', 'skill')
                args = {k.replace('method', 'skill'): v for k, v in args.items()}
            response=rpc(c,token,'tools/call',{'name':name,'arguments':args})
            assert response.status_code==200, response.text
            return response.json()['result']
        assert call(read,'get_method',{'method_id':secret['id']})['isError']
        assert not call(write,'get_method',{'method_id':secret['id']})['isError']
        payload={'method':{'title':'New','content':'Text'}}
        assert call(read,'create_method',payload)['isError']
        assert not call(write,'create_method',payload)['isError']
        assert call(read, 'update_method', {'method_id':public['id'], 'expected_version':1, 'method':{'title':'Changed','content':'Text'}})['isError']
        assert call(write, 'update_method', {'method_id':public['id'], 'expected_version':999, 'method':{'title':'Changed','content':'Text'}})['isError']
        results=call(read,'search_methods',{})
        text=' '.join(v.get('text','') for v in results['content'])
        assert secret['id'] not in text and public['id'] in text
        s.revoke(s.authenticate(read)['id'])
        assert rpc(c,read,'tools/list',{}).status_code==401
