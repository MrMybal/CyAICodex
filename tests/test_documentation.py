import json
from pathlib import Path
from html.parser import HTMLParser
from fastapi.testclient import TestClient
from skills.server import create_app
from skills.documentation import ROOT, manual_content


class Resources(HTMLParser):
    def __init__(self): super().__init__(); self.urls=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        for key in ('src','href'):
            if key in attrs:self.urls.append(attrs[key])


def test_manual_is_complete_bilingual_and_readable_without_auth(tmp_path):
    app=create_app(tmp_path)
    app.state.store.set_setting('admin_token','private-admin-fixture')
    app.state.store.new_connection('private-project-name')
    with TestClient(app,base_url='http://127.0.0.1:8765') as client:
        english=client.get('/help/content').json()
        french=client.get('/help/content?lang=fr').json()
        assert english['language']=='en'
        assert [t['id'] for t in english['topics']]==[t['id'] for t in french['topics']]
        assert len(english['topics'])==20
        for lang,data in [('en',english),('fr',french)]:
            assert len({t['id'] for t in data['topics']})==20
            assert {'backup','providers','permissions','troubleshooting','images','mcp'} <= {t['id'] for t in data['topics']}
            text=json.dumps(data,ensure_ascii=False)
            assert 'private-admin-fixture' not in text and 'private-project-name' not in text and str(tmp_path) not in text
            assert all(t['blocks'] and all(b.get('text') or b.get('items') or b.get('rows') or b.get('nodes') or b.get('caption') for b in t['blocks']) for t in data['topics'])
            response=client.get('/help?lang='+lang)
            assert response.status_code==200 and f'lang="{lang}"' in response.text
            parser=Resources();parser.feed(response.text)
            for url in parser.urls:
                assert url.startswith('/static/')
                assert client.get(url).status_code==200
            assert 'https://' not in response.text and 'http://' not in response.text
        assert client.get('/help/content?lang=de').status_code==422
        assert client.get('/help?lang=de').status_code==422
        assert client.get('/help',headers={'Origin':'https://evil.example'}).status_code==403
        assert client.get('/api/catalog').status_code==401


def test_diagrams_and_screenshots_are_bundled_and_translated():
    for lang in ('en','fr'):
        data=manual_content(lang)
        images=[b for t in data['topics'] for b in t['blocks'] if b['type']=='image']
        diagrams=[b for t in data['topics'] for b in t['blocks'] if b['type']=='diagram']
        assert len(images)==3 and len(diagrams)>=4
        for b in images:
            assert b['src'].startswith('/static/manual/images/')
            assert (ROOT/'images'/Path(b['src']).name).is_file()
            assert b['caption']
        assert all(len(b['nodes'])==3 and all(n['title'] and n['text'] for n in b['nodes']) for b in diagrams)
