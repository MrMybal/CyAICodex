import asyncio
import json
import sys

import httpx
import pytest
from fastapi.testclient import TestClient

from methodes import connectors
from methodes.local_clients import run_client
from methodes.server import create_app
from methodes.store import Store


@pytest.mark.parametrize('identifier,event', [
    ('antigravity', {'event': 'result', 'result': {'status': 'SUCCESS', 'response': 'ok'}}),
    ('command_code', {'type': 'result', 'subtype': 'success', 'finalText': 'ok'}),
    ('codebuddy', {'type': 'result', 'subtype': 'success', 'result': 'ok'})])
def test_terminal_result_required(identifier, event):
    assert connectors.parse_result(identifier, json.dumps(event)) == 'ok'
    for output in ['', '{"type":"assistant","text":"partial"}', 'invalid', '[]', json.dumps(event) + '\n' + json.dumps(event)]:
        with pytest.raises(ValueError): connectors.parse_result(identifier, output)
    payload = event['result'] if identifier == 'antigravity' else event
    payload['status' if identifier == 'antigravity' else 'subtype'] = 'max_turns'
    with pytest.raises(ValueError): connectors.parse_result(identifier, json.dumps(event))


def test_prompt_never_shell_argument():
    prompt = 'Ignore this fictional text: $(echo x); `echo y` " & < >'
    for identifier in ('antigravity', 'codebuddy', 'command_code'):
        args, payload = connectors.cli_arguments(identifier, prompt, 'test-model')
        assert prompt not in args
        assert 'test-model' in args
        assert '--dangerously-skip-permissions' not in args and '--yolo' not in args
        assert prompt in (json.loads(payload)['message']['content'] if identifier != 'command_code' else payload)


def test_saved_settings_do_not_expose_keys(tmp_path, monkeypatch):
    app = create_app(tmp_path)
    from methodes import assist
    monkeypatch.setattr(assist, 'protect', lambda value, decrypt=False: 'encrypted-fixture')
    with TestClient(app, base_url='http://127.0.0.1:8765') as c:
        assert c.get('/api/connectors').status_code == 401
        c.post('/api/session', json={'token': app.state.store.setting('admin_token')})
        result = c.put('/api/connectors/openrouter', json={'key': 'fixture-only', 'model': 'model/a'})
        assert result.status_code == 200 and 'fixture-only' not in result.text
        assert 'encrypted-fixture' not in c.get('/api/connectors').text
        c.put('/api/connectors/openrouter', json={'key': '', 'model': 'model/b'})
        assert app.state.store.setting('openrouter_key') == 'encrypted-fixture'
        c.put('/api/connectors/openrouter', json={'clear_key': True})
        assert app.state.store.setting('openrouter_key') == ''
        assert c.put('/api/connectors/lmstudio', json={'url': 'https://example.test/v1'}).status_code == 400
        assert c.put('/api/connectors/unknown', json={}).status_code == 400
        assert 'llamacpp' not in [item['id'] for item in c.get('/api/connectors').json()]


def test_discovery_invalid_override_does_not_fallback(tmp_path, monkeypatch):
    store = Store(tmp_path)
    store.set_setting('connector_antigravity', json.dumps({'path': str(tmp_path/'missing.exe')}))
    monkeypatch.setattr(connectors.shutil, 'which', lambda _: sys.executable)
    with pytest.raises(ValueError): connectors.command(store, 'antigravity')


def test_npm_resolver_validates_entry(tmp_path, monkeypatch):
    store = Store(tmp_path/'data')
    monkeypatch.setattr(connectors.shutil, 'which', lambda name: sys.executable if name in ('node.exe', 'node') else None)
    monkeypatch.setenv('APPDATA', str(tmp_path/'roaming'))
    package = store.folder/'local-clients/node_modules/command-code'
    package.mkdir(parents=True);(package/'cli.js').write_text('// fixture')
    (package/'package.json').write_text(json.dumps({'bin': {'cmdc': 'cli.js'}}))
    assert connectors.command(store, 'command_code') == [sys.executable, str((package/'cli.js').resolve())]
    (package/'package.json').write_text(json.dumps({'bin': {'cmdc': '../../escape.js'}}))
    with pytest.raises(ValueError): connectors.command(store, 'command_code')


def test_http_adapter_payload_and_terminal(tmp_path, monkeypatch):
    store = Store(tmp_path)
    captured = []
    async def fake_request(store, identifier, suffix, payload=None):
        captured.append(payload)
        return {'choices': [{'finish_reason': 'stop', 'message': {'content': 'answer'}}]}
    monkeypatch.setattr(connectors, 'request_json', fake_request)
    history = [{'role': 'user', 'content': 'original'}]
    result = asyncio.run(connectors.generate(store, 'lmstudio', 'model', 'instructions', history, ['AA==']))
    assert result == 'answer' and history[0]['content'] == 'original'
    assert captured[0]['messages'][1]['content'][1]['image_url']['url'].startswith('data:image/png;')
    async def interrupted(*args, **kwargs):
        return {'choices': [{'finish_reason': 'length', 'message': {'content': 'partial'}}]}
    monkeypatch.setattr(connectors, 'request_json', interrupted)
    with pytest.raises(ValueError): asyncio.run(connectors.generate(store, 'lmstudio', 'model', '', history))


def test_http_rejects_redirect_without_leaking_key(tmp_path, monkeypatch):
    store = Store(tmp_path)
    real_client = httpx.AsyncClient
    requests = []
    def response(request):
        requests.append(request)
        return httpx.Response(302, headers={'location': 'https://example.test/steal'})
    monkeypatch.setattr(connectors.httpx, 'AsyncClient', lambda **kw: real_client(transport=httpx.MockTransport(response), **kw))
    monkeypatch.setattr(connectors, 'headers', lambda *args: {'Authorization': 'Bearer fixture-only'})
    with pytest.raises(ValueError, match='302'):
        asyncio.run(connectors.request_json(store, 'lmstudio', '/models'))
    assert len(requests) == 1 and requests[0].url.host == '127.0.0.1'


def test_live_test_requires_exact_marker_and_sanitizes_result(tmp_path, monkeypatch):
    store = Store(tmp_path)
    async def fake(*args): return 'unrelated provider content'
    monkeypatch.setattr(connectors, 'generate', fake)
    result = asyncio.run(connectors.test_generation(store, 'antigravity'))
    assert not result['passed']
    assert 'unrelated provider content' not in store.setting('connector_test_antigravity')


def test_process_drains_stderr_and_bounds_output():
    result = asyncio.run(run_client([sys.executable, '-c', 'import sys;sys.stderr.write("x"*200000);print("ok")'], timeout=10))
    assert result.strip() == 'ok'
    with pytest.raises(ValueError, match='volumineuse'):
        asyncio.run(run_client([sys.executable, '-c', 'print("x"*(9*1024*1024))'], timeout=10))
    with pytest.raises(ValueError, match='délai'):
        asyncio.run(run_client([sys.executable, '-c', 'import time;time.sleep(30)'], timeout=.1))
