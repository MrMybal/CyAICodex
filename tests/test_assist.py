import asyncio
import os

import httpx
import pytest

from skills.assist import answer, protect
from skills.store import Store


@pytest.mark.skipif(os.name!='nt', reason='DPAPI is Windows-only')
def test_dpapi_round_trip():
    key='test-not-a-real-secret-é'
    encrypted=protect(key)
    assert key not in encrypted
    assert protect(encrypted, decrypt=True)==key


@pytest.mark.parametrize('provider', ['openai','claude'])
def test_provider_request_and_text_response(tmp_path, monkeypatch, provider):
    s=Store(tmp_path)
    monkeypatch.setenv('OPENAI_API_KEY' if provider=='openai' else 'ANTHROPIC_API_KEY','test-key')
    captured={}
    class Client:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self,*args): pass
        async def post(self,url,**kwargs):
            captured.update(url=url,**kwargs)
            data={'output':[{'content':[{'type':'output_text','text':'Réponse'}]}]} if provider=='openai' else {'content':[{'type':'text','text':'Réponse'}]}
            return httpx.Response(200,json=data)
    monkeypatch.setattr('skills.assist.httpx.AsyncClient',Client)
    assert asyncio.run(answer(s,provider,'my-model',[{'role':'user','content':'Bonjour'}],[]))=='Réponse'
    assert captured['json']['model']=='my-model'
    assert 'test-key' not in str(captured['json'])
    if provider=='openai': assert captured['json']['store'] is False
