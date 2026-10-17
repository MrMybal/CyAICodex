import sys
from contextlib import nullcontext
from types import SimpleNamespace

from fastapi.testclient import TestClient
from skills import startup
from skills.server import create_app


def test_startup_is_idempotent_and_preserves_launch_options(monkeypatch, tmp_path):
    values = {}
    def read(key, name):
        if name not in values:
            raise FileNotFoundError()
        return values[name], 1
    def delete(key, name):
        if name not in values:
            raise FileNotFoundError()
        del values[name]
    registry = SimpleNamespace(HKEY_CURRENT_USER=1, REG_SZ=1,
        OpenKey=lambda *args: nullcontext(1), CreateKey=lambda *args: nullcontext(1),
        QueryValueEx=read, DeleteValue=delete,
        SetValueEx=lambda key, name, reserved, kind, value: values.update({name:value}))
    monkeypatch.setitem(sys.modules, 'winreg', registry)
    folder = tmp_path / 'data with spaces'
    assert startup.set_startup(True, 9876, folder)
    assert startup.set_startup(True, 9876, folder)
    command = values['Methode']
    assert '--no-open' in command and '--port 9876' in command
    assert '"'+str(folder.resolve())+'"' in command
    assert 'pythonw.exe' in command and 'run.py' in command
    assert not startup.set_startup(False)
    assert not startup.set_startup(False)


def test_startup_api_is_authenticated_and_sets_explicit_state(monkeypatch, tmp_path):
    state = {'enabled':False}
    def save(enabled, port, folder):
        assert port == 8765 and folder == tmp_path
        state['enabled'] = enabled
        return enabled
    monkeypatch.setattr('skills.server.startup_enabled', lambda:state['enabled'])
    monkeypatch.setattr('skills.server.set_startup', save)
    app = create_app(tmp_path)
    with TestClient(app, base_url='http://127.0.0.1:8765') as client:
        assert client.put('/api/startup', json={'enabled':True}).status_code == 401
        client.post('/api/session', json={'token':app.state.store.setting('admin_token')})
        assert client.put('/api/startup', json={'enabled':True}).json()['enabled']
        assert client.get('/api/startup').json()['enabled']
        assert not client.put('/api/startup', json={'enabled':False}).json()['enabled']


def test_frozen_startup_points_to_executable(monkeypatch, tmp_path):
    executable = tmp_path / 'App with spaces' / 'Methode.exe'
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(sys, 'executable', str(executable))
    command = startup.startup_command(8765, tmp_path / 'data')
    assert command.startswith('"'+str(executable)+'" --no-open')
    assert 'pythonw' not in command and 'run.py' not in command
