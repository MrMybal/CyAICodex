"""Local export contracts and native launcher security; no browser is launched."""
import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
from urllib.parse import unquote, urlsplit

import pytest
from fastapi.testclient import TestClient
from skills import documentation
from skills.server import create_app

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / 'build' / 'help'
ORIGINAL_IDS = set('welcome quick-start skills search history projects images mcp manual-setup permissions assistant providers windows language backup updates troubleshooting tools example-workflow about'.split())


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'img', 'source', 'video', 'audio') and attrs.get('src'):
            self.sources.append(attrs['src'])
        if tag == 'link' and attrs.get('href'):
            self.sources.append(attrs['href'])


@pytest.fixture(scope='module')
def manifest():
    assert (EXPORT / 'manifest.json').is_file(), 'Run npm ci and npm run docs:build before pytest.'
    return json.loads((EXPORT / 'manifest.json').read_text(encoding='utf-8'))


def test_complete_bilingual_export_and_translation_tracking(manifest):
    assert manifest['defaultLocale'] == 'en'
    groups = {lang: {p['id']: p for p in manifest['pages'] if p['locale'] == lang} for lang in ('en','fr')}
    assert groups['en'].keys() == groups['fr'].keys()
    assert ORIGINAL_IDS | {'help-integration','building-help','project-readme','license','changelog','translation-report'} == groups['en'].keys()
    for name, english in groups['en'].items():
        french = groups['fr'][name]
        assert english['html'] and french['html']
        assert {h['id'] for h in english['headings']} == {h['id'] for h in french['headings']}
    report = json.loads((EXPORT / 'translation-report.json').read_text(encoding='utf-8'))
    assert report['missing'] == report['outdated'] == report['untracked'] == []
    assert report['current'] == len(groups['en']) - 1
    api = groups['en']['help-integration']
    assert api['source'].startswith('skills/documentation.py:') and api['symbol'] == 'help_url'
    assert 'open_help' in api['text']


def test_export_resources_are_local_and_only_image_is_bundled(manifest):
    config = json.loads((ROOT/'cydoc.config.json').read_text(encoding='utf-8'))
    assert config['modules'] == ['image']
    assert {p.name for p in EXPORT.glob('media-*.js')} == {'media-image.js'}
    assert not (ROOT/'node_modules/three').exists()
    parser = Resources()
    index = (EXPORT/'index.html').read_text(encoding='utf-8')
    parser.feed(index)
    for page in manifest['pages']:
        parser.feed(page['html'])
        for asset in page.get('assets', []):
            assert asset.startswith('assets/')
            assert (EXPORT/unquote(asset)).is_file()
    for src in parser.sources:
        if src.startswith('data:'):
            continue
        assert not urlsplit(src).scheme and not src.startswith(('/', '//'))
        assert (EXPORT/unquote(src)).is_file(), src
    assert '<html lang="en">' in index and 'type="module"' not in index
    assert (EXPORT/'data.js').read_text(encoding='utf-8').startswith('globalThis.CYDOC_DATA=')
    for file in ('viewer.js','media-image.js'):
        code = (EXPORT/file).read_text(encoding='utf-8')
        assert 'fetch(' not in code
    assert (EXPORT/'CyDoc.LICENSE.txt').is_file()
    for lang in ('en','fr'):
        pages = [p for p in manifest['pages'] if p['locale'] == lang]
        assert sum('data-cydoc-id=' in p['html'] for p in pages) >= 4
        assert sum('<svg' in p['html'] for p in pages) >= 4


def test_local_urls_encode_paths_and_preserve_targets(tmp_path, monkeypatch, manifest):
    local = tmp_path/'Manual # été with spaces'
    local.mkdir()
    (local/'index.html').write_text('<!doctype html>', encoding='utf-8')
    (local/'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    monkeypatch.setattr(documentation, 'help_root', lambda: local)
    url = documentation.help_url('fr','backup','restore')
    assert url.startswith(local.as_uri()+'/index.html#/fr/backup/restore')
    assert '%23' in url and '%20' in url and '%C3%A9' in url
    assert documentation.help_url('en','quickstart').endswith('#/en/quick-start')
    assert documentation.help_url('en','skills',media='skills-illustration').endswith('#/en/skills?media=skills-illustration')
    calls = []
    monkeypatch.setattr(documentation.webbrowser, 'open', lambda url, new: calls.append((url,new)) or True)
    assert documentation.open_help('fr','backup','restore') == url
    assert calls == [(url,2)]
    for args in [('de','welcome'),('en','missing'),('en','backup','missing'),('en','skills',None,'missing')]:
        with pytest.raises(ValueError): documentation.help_url(*args)
    monkeypatch.setattr(documentation.webbrowser, 'open', lambda *a,**kw: False)
    with pytest.raises(OSError): documentation.open_help()
    (local/'index.html').unlink()
    with pytest.raises(FileNotFoundError): documentation.help_url()


def test_missing_translation_falls_back_and_alias_cycles_fail(tmp_path, monkeypatch, manifest):
    manifest = json.loads(json.dumps(manifest))
    manifest['pages'] = [p for p in manifest['pages'] if (p['id'],p['locale']) != ('backup','fr')]
    manifest['aliases'].update({'cycle-a':'cycle-b','cycle-b':'cycle-a'})
    (tmp_path/'index.html').write_text('reader',encoding='utf-8')
    (tmp_path/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    monkeypatch.setattr(documentation,'help_root',lambda:tmp_path)
    assert documentation.help_url('fr','backup','restore').endswith('#/fr/backup/restore')
    with pytest.raises(ValueError, match='alias'): documentation.help_url('en','cycle-a')


def test_help_launch_is_authenticated_and_legacy_links_remain(tmp_path, monkeypatch):
    app = create_app(tmp_path)
    calls = []
    def fake_open(*args):
        calls.append(args)
        if args[1] == 'unknown': raise ValueError('Unknown documentation page')
        return 'file:///fixture/help/index.html#/en/welcome'
    monkeypatch.setattr('skills.server.open_help',fake_open)
    with TestClient(app,base_url='http://127.0.0.1:8765') as client:
        assert client.post('/api/help/open',json={}).status_code == 401
        assert calls == []
        for lang in ('en','fr'):
            response = client.get('/help?lang='+lang)
            assert response.status_code == 200 and f'lang="{lang}"' in response.text
            assert 'data-open-help="legacy"' in response.text
            assert '/static/help.js' in response.text
            assert client.get('/help/content?lang='+lang).status_code == 410
        assert client.get('/help?lang=de').status_code == 422
        assert client.get('/help',headers={'Origin':'https://evil.example'}).status_code == 403
        client.post('/api/session',json={'token':app.state.store.setting('admin_token')})
        before = client.get('/api/export').json()
        assert client.post('/api/help/open',json={},headers={'Origin':'https://evil.example'}).status_code == 403
        assert client.post('/api/help/open',json={}).status_code == 200
        assert calls[-1] == ('en','welcome',None,None)
        assert client.post('/api/help/open',json={'language':'fr','page':'skills','media':'skills-illustration'}).status_code == 200
        assert calls[-1] == ('fr','skills',None,'skills-illustration')
        for body in [{'language':'de'},{'page':'../../private'},{'anchor':'x/y'},{'media':'file:///x'}]:
            assert client.post('/api/help/open',json=body).status_code == 422
        assert client.post('/api/help/open',json={'page':'unknown'}).status_code == 400
        assert client.get('/api/export').json() == before
        assert 'Open help (F1)' in client.get('/').text


def test_cli_can_resolve_help_without_server_or_browser(manifest):
    result = subprocess.run([sys.executable,'run.py','--open-help','--help-language','fr','--help-page','backup','--help-section','restore','--print-help-url'],cwd=ROOT,capture_output=True,text=True,timeout=15)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == documentation.help_url('fr','backup','restore')


def test_all_declared_contextual_targets_exist(manifest):
    class Targets(HTMLParser):
        def __init__(self):
            super().__init__()
            self.targets = []
        def handle_starttag(self,tag,attrs):
            attrs = dict(attrs)
            if 'data-help-page' in attrs: self.targets.append(attrs)
    parser = Targets()
    parser.feed((ROOT/'skills/web/index.html').read_text(encoding='utf-8'))
    assert len(parser.targets) >= 16
    for attrs in parser.targets:
        for lang in ('en','fr'):
            page = next(p for p in manifest['pages'] if p['id']==attrs['data-help-page'] and p['locale']==lang)
            if attrs.get('data-help-section'):
                assert attrs['data-help-section'] in {h['id'] for h in page['headings']}
            if attrs.get('data-help-media'):
                assert 'data-cydoc-id="'+attrs['data-help-media']+'"' in page['html']
