import json
import sqlite3

import pytest

from methodes.installation import migrate_data, reconnect_existing
from methodes.store import Store, Method
from methodes.mcp_setup import MCPSetup, read_config
from methodes import runtime


def test_migration_keeps_original_and_refuses_existing_library(tmp_path):
    source = tmp_path / 'portable/data'; target = tmp_path / 'installed/data'
    store = Store(source)
    method = store.save(Method(title='Migration fixture', content='Keep this method.'))
    (source / 'images').mkdir(); (source / 'images/example.png').write_bytes(b'example image')
    migrate_data(source, target)
    copied = Store(target)
    assert copied.get(method['id'])['content'] == 'Keep this method.'
    assert (target / 'images/example.png').read_bytes() == b'example image'
    assert store.get(method['id'])['content'] == 'Keep this method.'
    assert copied.setting('admin_token') == store.setting('admin_token')
    with pytest.raises(ValueError): migrate_data(source, target)
    assert copied.get(method['id'])['content'] == 'Keep this method.'


@pytest.mark.parametrize('client', ['codex', 'claude_desktop', 'opencode'])
def test_all_clients_launch_same_executable_and_preserve_old_token(tmp_path, client):
    root = tmp_path / 'app'; root.mkdir(); (root / 'CyAICodex.exe').write_bytes(b'fixture')
    store = Store(tmp_path / 'data')
    setup = MCPSetup(store, 8765, root)
    entry = setup.entry(client, 'token-fixture')
    cmd = entry['command'] if isinstance(entry['command'], list) else [entry['command'], *entry['args']]
    assert cmd[0] == str(root / 'CyAICodex.exe') and '--mcp-stdio' in cmd and '--data-dir' in cmd
    assert setup.token(client, entry) == 'token-fixture'
    assert setup.managed(client, entry)
    if client != 'claude_desktop':
        old = {'url': setup.url, 'http_headers' if client == 'codex' else 'headers': {'Authorization': 'Bearer token-fixture'}}
    else:
        old = {'command': str(root / 'CyAICodex-MCP.exe'), 'args': ['--mcp-stdio', '--port', '8765'], 'env': {'CYAICODEX_MCP_TOKEN': 'token-fixture'}}
    assert setup.managed(client, old) and setup.token(client, old) == 'token-fixture'


def test_reconnect_does_not_replace_unrelated_client_config(tmp_path, monkeypatch):
    store = Store(tmp_path / 'data')
    root = tmp_path / 'app'; root.mkdir(); (root / 'CyAICodex.exe').write_bytes(b'fixture')
    config = tmp_path / 'config.toml'
    config.write_text('[mcp_servers.cyaicodex]\nurl="http://127.0.0.1:8765/mcp"\nenabled=false\n[mcp_servers.cyaicodex.http_headers]\nAuthorization="Bearer saved-fixture"\n[mcp_servers.other]\ncommand="untouched"\n')
    monkeypatch.setattr('methodes.mcp_setup.root_path', lambda: root)
    monkeypatch.setattr('methodes.mcp_setup.CLIENTS', {'codex': 'Codex'})
    monkeypatch.setattr('methodes.mcp_setup.config_path', lambda _: config)
    reconnect_existing(store)
    _, data, _ = read_config('codex', config)
    assert data['mcp_servers']['other']['command'] == 'untouched'
    entry = data['mcp_servers']['cyaicodex']
    assert entry['enabled'] is False
    assert entry['env']['CYAICODEX_MCP_TOKEN'] == 'saved-fixture'
    assert 'url' not in entry
    assert list((tmp_path / '.cyaicodex-backups').iterdir())


def test_bridge_does_not_start_another_application_on_occupied_port(tmp_path, monkeypatch):
    import httpx
    monkeypatch.setattr(runtime, 'maintenance_active', lambda: False)
    monkeypatch.setattr(runtime.httpx, 'get', lambda *a, **kw: httpx.Response(200, json={'app': 'unrelated'}))
    monkeypatch.setattr(runtime, 'launch_independent', lambda _: pytest.fail('Must not launch'))
    with pytest.raises(RuntimeError, match='another application'): runtime.ensure_server(8765, tmp_path)
