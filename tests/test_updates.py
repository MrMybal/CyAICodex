import hashlib
import json
import sys

import httpx
import pytest
from fastapi.testclient import TestClient

from methodes.store import Store
from methodes.server import create_app
from methodes import updates
from methodes.updates import Updater, API, asset_details, version_tuple


def release(raw=b'MZinstaller'):
    return {'tag_name': 'v0.7.0', 'draft': False, 'prerelease': False, 'assets': [
        {'id': 123, 'name': 'CyAICodex-Setup-0.7.0.exe', 'url': API + '/releases/assets/123',
         'size': len(raw), 'state': 'uploaded', 'digest': 'sha256:' + hashlib.sha256(raw).hexdigest()}]}


def test_versions_assets_and_untrusted_redirects(tmp_path):
    assert version_tuple('v0.10.0') > version_tuple('0.9.9')
    for value in ['v0.7.0-beta', '../setup.exe', '', None]:
        with pytest.raises(ValueError): version_tuple(value)
    for change in [{'digest': None}, {'url': 'https://example.com/file'}, {'size': updates.MAX_INSTALLER + 1}, {'state': 'new'}]:
        r = release(); r['assets'][0].update(change)
        with pytest.raises(ValueError): asset_details(r)
    updater = Updater(Store(tmp_path / 'data'))
    for location in ['http://github.com/file', 'https://api.github.com.evil.invalid/x', 'https://example.com/file', 'https://user:secret@github.com/file']:
        def respond(request):
            return httpx.Response(302, headers={'location': location})
        with httpx.Client(transport=httpx.MockTransport(respond)) as client:
            with pytest.raises(ValueError): updater.download(client, release()['assets'][0], 'credential-fixture', tmp_path / 'download')
        assert not (tmp_path / 'download').exists()


def test_private_asset_credentials_not_forwarded_and_hash_checked(tmp_path):
    updater = Updater(Store(tmp_path / 'data'))
    seen = []
    def respond(request):
        seen.append((request.url.host, request.headers.get('authorization')))
        if request.url.host == 'api.github.com':
            return httpx.Response(302, headers={'location': 'https://release-assets.githubusercontent.com/installer'})
        return httpx.Response(200, content=b'MZinstaller')
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        updater.download(client, release()['assets'][0], 'credential-fixture', tmp_path / 'good')
    assert seen == [('api.github.com', 'Bearer credential-fixture'), ('release-assets.githubusercontent.com', None)]
    corrupt = release(); corrupt['assets'][0]['digest'] = 'sha256:' + '0' * 64
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(ValueError, match='vérification'): updater.download(client, corrupt['assets'][0], '', tmp_path / 'bad')


def test_private_to_public_transition_ignores_expired_credentials(tmp_path, monkeypatch):
    updater = Updater(Store(tmp_path / 'data'))
    monkeypatch.setattr(updater, 'credentials', lambda: (_ for _ in ()).throw(AssertionError('No credential needed for public repo')))
    with httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json=release()))) as client:
        latest, token = updater.fetch_latest(client)
    assert latest['tag_name'] == 'v0.7.0' and not token
    monkeypatch.setattr(updater, 'credentials', lambda: 'credential-fixture')
    calls = []
    def respond(request):
        calls.append(request.headers.get('authorization'))
        return httpx.Response(200, json=release()) if len(calls) == 2 else httpx.Response(404)
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        assert updater.fetch_latest(client)[1] == 'credential-fixture'
    assert calls == [None, 'Bearer credential-fixture']


def test_updater_routes_require_admin_and_token_is_encrypted(tmp_path):
    app = create_app(tmp_path)
    with TestClient(app, base_url='http://127.0.0.1:8765') as client:
        for method, path in [('GET', '/api/updates'), ('PUT', '/api/updates/settings'), ('POST', '/api/updates/check'), ('POST', '/api/updates/install')]:
            assert client.request(method, path, json={}).status_code == 401
        client.post('/api/session', json={'token': app.state.store.setting('admin_token')})
        secret = 'private-test-credential'
        result = client.put('/api/updates/settings', json={'token': secret, 'automatic': False, 'use_git': True})
        assert result.status_code == 200 and secret not in result.text
        assert app.state.store.setting('updates_token') != secret
        assert app.state.updater.credentials() == secret
        client.put('/api/updates/settings', json={'token': '', 'automatic': False, 'use_git': False})
        assert app.state.updater.credentials() == secret
        result = client.put('/api/updates/settings', json={'clear_token': True, 'automatic': False})
        assert not result.json()['token_configured']


def test_install_only_executes_verified_new_release(tmp_path, monkeypatch):
    updater = Updater(Store(tmp_path / 'data'))
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    monkeypatch.setattr(updates, 'root_path', lambda: tmp_path)
    real_client = httpx.Client
    published = release()
    raw = b'MZinstaller'
    def respond(request):
        if request.url.path.endswith('/latest'): return httpx.Response(200, json=published)
        return httpx.Response(200, content=raw)
    monkeypatch.setattr(updates.httpx, 'Client', lambda **kwargs: real_client(transport=httpx.MockTransport(respond), **kwargs))
    launched = []
    monkeypatch.setattr(updates, 'launch_independent', lambda args, visible: launched.append(args))
    assert updater.install()['status'] == 'installing'
    assert len(launched) == 1 and '/LEGACYDATA=' in launched[0][-1]
    published['assets'][0]['digest'] = 'sha256:' + '0' * 64
    with pytest.raises(ValueError): updater.install()
    assert len(launched) == 1
    assert not list((tmp_path / 'data/updates').rglob('*.part'))
    published['tag_name'] = 'v0.1.0'
    with pytest.raises(ValueError, match='déjà à jour'): updater.install()
    assert len(launched) == 1


def test_network_failure_does_not_expose_private_urls_or_tokens(tmp_path, monkeypatch):
    updater = Updater(Store(tmp_path / 'data'))
    def fail(client): raise httpx.ConnectError('sensitive provider detail')
    monkeypatch.setattr(updater, 'fetch_latest', fail)
    status = updater.check()
    assert status['status'] == 'error' and 'sensitive' not in json.dumps(status)
