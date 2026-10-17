import asyncio
from html.parser import HTMLParser

from fastapi.testclient import TestClient

from methodes import assist
from methodes.i18n import catalog, render_index, translate, translated_status
from methodes.server import create_app
from methodes.store import Store


def test_language_persistence_security_and_content(tmp_path):
    app = create_app(tmp_path)
    with TestClient(app, base_url='http://127.0.0.1:8765') as client:
        assert '<html lang="en">' in client.get('/').text
        assert client.put('/api/language', json={'language': 'en'}).status_code == 401
        client.post('/api/session', json={'token': app.state.store.setting('admin_token')})
        prefs = client.get('/api/preferences').json()
        saved = client.post('/api/methods', json={'method': {'title': 'Bibliothèque', 'content': 'Ne pas traduire mes consignes.'}}).json()
        assert client.put('/api/language', json={'language': 'de'}).status_code == 422
        assert client.put('/api/language', json={'language': 'en'}, headers={'Origin': 'https://evil.example'}).status_code == 403
        assert client.put('/api/language', json={'language': 'en'}).json() == {'language': 'en'}
        html = client.get('/').text
        assert '<html lang="en">' in html and 'Save settings' in html and 'Image resources' in html
        assert 'When to use it' in html
        assert client.get('/api/methods/' + saved['id']).json()['title'] == 'Bibliothèque'
        assert client.get('/api/preferences').json() == prefs
        assert client.get('/api/methods/missing').json()['detail'] == 'Method not found.'
        assert 'const UI_TRANSLATIONS' in client.get('/static/i18n-data.js').text
    with TestClient(create_app(tmp_path), base_url='http://127.0.0.1:8765') as client:
        assert '<html lang="en">' in client.get('/').text
        client.post('/api/session', json={'token': app.state.store.setting('admin_token')})
        client.put('/api/language', json={'language': 'fr'})
        assert 'Enregistrer les paramètres' in client.get('/').text


def test_translations_preserve_parameters_and_user_data():
    assert translate('Connexion MCP testée avec la configuration enregistrée : 10 outils accessibles.', 'en') == 'MCP connection tested with the saved configuration: 10 tools available.'
    value = {'message': 'Client disponible', 'path': 'D:/Bibliothèque/Paramètres.exe', 'context': {'name': 'Bibliothèque'}}
    translated = translated_status(value, 'en')
    assert translated['message'] == 'Client available'
    assert translated['path'] == value['path'] and translated['context'] == value['context']
    assert translate('Un texte personnel inconnu', 'en') == 'Un texte personnel inconnu'


def test_assistant_uses_language(tmp_path, monkeypatch):
    store = Store(tmp_path)
    captured = []
    async def fake_answer(prompt, *args):
        captured.append(prompt)
        return 'ok'
    monkeypatch.setattr(assist, 'codex_answer', fake_answer)
    for language in ('fr', 'en'):
        store.set_setting('ui_language', language)
        asyncio.run(assist.answer(store, 'codex', '', [{'role': 'user', 'content': 'Ma demande personnelle'}], []))
    assert 'Réponds en français' in captured[0]
    assert 'Reply in English' in captured[1]
    assert all('Ma demande personnelle' in prompt for prompt in captured)


def test_static_translation_coverage_and_dom_integrity():
    class Page(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids, self.values, self.texts = [], [], []
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if 'id' in attrs: self.ids.append(attrs['id'])
            if 'value' in attrs: self.values.append(attrs['value'])
        def handle_data(self, text):
            self.texts.append(text.strip())
    french, english = Page(), Page()
    french.feed(render_index('fr')); english.feed(render_index('en'))
    assert french.ids == english.ids and french.values == english.values
    assert len(french.ids) == len(set(french.ids))
    unchanged = {'CyAICodex', 'C', 'Assistant', 'FR / EN', 'Français', 'English', 'Claude · API', 'OpenAI · API', 'Codex', 'OpenAI API', 'Claude API', 'Tags', 'Format', 'Codex · config.toml', 'Claude Desktop · application', 'OpenCode · configuration'}
    missing = {text for text in french.texts if any(c.isalpha() for c in text) and text not in catalog() and text not in unchanged}
    assert not missing


def test_saved_french_preference_survives_restart(tmp_path):
    store = Store(tmp_path)
    store.set_setting('ui_language', 'fr')
    with TestClient(create_app(tmp_path), base_url='http://127.0.0.1:8765') as client:
        assert '<html lang="fr">' in client.get('/').text
        assert 'Enregistrer les paramètres' in client.get('/').text
    assert Store(tmp_path).setting('ui_language') == 'fr'
