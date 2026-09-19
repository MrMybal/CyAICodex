import asyncio
import json
from pathlib import Path

import pytest
import tomlkit
from fastapi.testclient import TestClient

from methodes.mcp_setup import MCPSetup, read_config, write_config, config_path
from methodes.store import Store
from methodes.server import create_app


def manager(tmp_path):
    root=tmp_path/'app';root.mkdir();(root/'CyAICodex.exe').write_bytes(b'fake executable, never run')
    paths={c:tmp_path/c/('config.toml' if c=='codex' else 'config.jsonc') for c in ['codex','claude_desktop','opencode']}
    folder=tmp_path/'data';folder.mkdir()
    return MCPSetup(Store(folder),18769,root,paths)


def options(**kwargs):
    return dict(without_token=False,project_id='',type_id='',include_global=True,writable=False,**kwargs)


def test_claude_store_profile_detected_before_first_mcp_configuration(tmp_path,monkeypatch):
    monkeypatch.setenv('APPDATA',str(tmp_path/'roaming'))
    monkeypatch.setenv('LOCALAPPDATA',str(tmp_path/'local'))
    folder=tmp_path/'local/Packages/Claude_example/LocalCache/Roaming/Claude'
    folder.mkdir(parents=True)
    assert config_path('claude_desktop')==folder/'claude_desktop_config.json'


@pytest.mark.parametrize('client',['codex','claude_desktop','opencode'])
def test_install_preserves_other_servers_backup_and_idempotence(tmp_path,client):
    setup=manager(tmp_path);path=setup.path(client);path.parent.mkdir()
    original=(b'# User comment\nmodel="my-model"\n[mcp_servers.other]\ncommand="keep-me"\n' if client=='codex'
              else ('{ // My settings\n "theme":"dark", "'+('mcpServers' if client=='claude_desktop' else 'mcp')+'":{"other":{"command":"keep-me"}}}').encode())
    path.write_bytes(original)
    installed=setup.install(client,options())
    assert Path(installed['backup']).read_bytes()==original
    _,data,key=read_config(client,path)
    assert data[key]['other']['command']=='keep-me'
    assert data.get('model',data.get('theme')) in ['my-model','dark']
    if client=='codex':assert '# User comment' in path.read_text()
    entry=data[key]['cyaicodex'];token=setup.token(client,entry)
    assert not setup.store.authenticate(token)['writable']
    assert not setup.install(client,options())['changed']
    assert len(setup.store.connections())==1
    # Revoked credentials are repaired, without touching the unrelated server.
    setup.store.revoke(setup.store.connections()[0]['id'])
    assert setup.install(client,options())['changed']
    _,data,key=read_config(client,path)
    assert setup.token(client,data[key]['cyaicodex'])!=token
    assert len(setup.store.connections())==1


def test_scope_change_rotates_only_managed_token(tmp_path):
    setup=manager(tmp_path);manual=setup.store.new_connection('Manual')
    setup.install('codex',options())
    p=setup.store.add_group('projects','Private')
    changed=options();changed.update(project_id=p['id'],include_global=False,writable=True)
    setup.install('codex',changed)
    assert setup.store.authenticate(manual['token'])
    assert len(setup.store.connections())==2
    _,data,key=read_config('codex',setup.path('codex'))
    access=setup.store.authenticate(setup.token('codex',data[key]['cyaicodex']))
    assert access['project_id']==p['id'] and not access['include_global'] and access['writable']


def test_invalid_foreign_and_changed_configs_are_not_overwritten(tmp_path):
    setup=manager(tmp_path);p=setup.path('codex');p.parent.mkdir()
    for content in ['[broken','[mcp_servers.cyaicodex]\nurl="http://elsewhere"\n']:
        p.write_text(content)
        with pytest.raises(ValueError):setup.install('codex',options())
        assert p.read_text()==content
        assert not setup.store.connections()
    p.write_text('model="original"')
    raw,data,_=read_config('codex',p)
    p.write_text('model="changed-by-user"')
    with pytest.raises(ValueError):write_config('codex',p,raw,data)
    assert p.read_text()=='model="changed-by-user"'


def test_failed_write_rolls_back_new_token(tmp_path,monkeypatch):
    setup=manager(tmp_path)
    def fail(*args):raise PermissionError('test')
    monkeypatch.setattr('methodes.mcp_setup.write_config',fail)
    with pytest.raises(PermissionError):setup.install('codex',options())
    assert not setup.store.connections()


def test_without_token_requires_explicit_server_setting(tmp_path):
    setup=manager(tmp_path);opts=options();opts['without_token']=True
    with pytest.raises(ValueError):setup.install('codex',opts)
    setup.store.set_setting('preferences',json.dumps({'local_no_token':True}))
    setup.install('codex',opts)
    _,data,key=read_config('codex',setup.path('codex'))
    assert not setup.token('codex',data[key]['cyaicodex'])
    assert not setup.store.connections()


def test_setup_api_requires_admin_and_discovery_has_no_secrets(tmp_path,monkeypatch):
    app=create_app(tmp_path)
    called=[]
    def install(*args):called.append(1);return {'changed':True}
    async def diagnose(*args):return {'configured':True,'mcp':True}
    monkeypatch.setattr(MCPSetup,'install',install);monkeypatch.setattr(MCPSetup,'diagnose',diagnose)
    with TestClient(app,base_url='http://127.0.0.1:8765') as c:
        assert c.post('/api/mcp-setup/codex',json=options()).status_code==401
        assert not called
        info=c.get('/mcp-info').json();assert info['transport']=='Streamable HTTP' and info['token_required']
        assert app.state.store.setting('admin_token') not in json.dumps(info)
        c.post('/api/session',json={'token':app.state.store.setting('admin_token')})
        assert c.post('/api/mcp-setup/codex',json=options()).json()['diagnostic']['mcp']
        assert called
