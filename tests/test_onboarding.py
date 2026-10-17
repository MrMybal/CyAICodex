import json
from fastapi.testclient import TestClient
from skills.server import create_app
from skills.onboarding import setup_guide
from test_api import rpc


def test_public_guide_is_available_before_auth_and_contains_no_private_data(tmp_path):
    app = create_app(tmp_path, port=18775)
    store = app.state.store
    store.set_setting('admin_token', 'admin-secret-fixture')
    store.set_setting('openai_api_key', 'private-key-fixture')
    token = store.new_connection('private-connection-name')['token']
    with TestClient(app, base_url='http://127.0.0.1:18775') as client:
        for lang, expected in [('en', 'Verify the connection'), ('fr', 'Vérifier la connexion')]:
            result = client.get('/mcp-guide', params={'lang':lang,'client':'claude_desktop'})
            assert result.status_code == 200 and expected in result.text
            assert 'Claude Desktop' in result.text and '18775/mcp' in result.text
            assert 'text/markdown' in result.headers['content-type']
            assert f'CyAICodex-Setup-{lang}.md' in result.headers['content-disposition']
            for private in ('admin-secret-fixture','private-key-fixture',token,'private-connection-name',str(tmp_path)):
                assert private not in result.text
        assert client.get('/mcp-guide?client=unknown').status_code == 422
        assert client.get('/mcp-guide?lang=de').status_code == 422
        assert client.get('/mcp-guide',headers={'Origin':'https://evil.example'}).status_code == 403
        info = client.get('/mcp-info').json()
        assert info['setup_tool'] == 'get_setup_guide'
        assert 'search_skills' in info['workflow']
        assert 'lang=fr' in info['guides']['fr']


def test_mcp_guide_is_read_only_and_uses_requested_language(tmp_path):
    app = create_app(tmp_path)
    store = app.state.store
    token = store.new_connection('Read only')['token']
    with store.db() as db:
        before = list(db.execute('select * from settings'))
    with TestClient(app, base_url='http://127.0.0.1:8765') as client:
        tools = rpc(client, token, 'tools/list', {}).json()['result']['tools']
        tool = next(x for x in tools if x['name']=='get_setup_guide')
        assert tool['annotations']['readOnlyHint']
        result = rpc(client, token, 'tools/call', {'name':'get_setup_guide','arguments':{'client':'opencode','language':'fr'}}).json()['result']
        assert not result.get('isError')
        text = json.dumps(result, ensure_ascii=False)
        assert 'OpenCode' in text and 'Vérifier la connexion' in text
        assert token not in text
    with store.db() as db:
        assert list(db.execute('select * from settings')) == before


def test_manual_clients_are_not_advertised_as_automatic():
    for client in ('claude_code','other'):
        guide = setup_guide(client)['markdown']
        assert 'generated configuration' in guide
        assert 'on this client’s card' not in guide
