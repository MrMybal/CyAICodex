import asyncio
import socket
import threading
import time

import httpx
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from methodes.server import create_app
from methodes.store import Method, Store


def test_three_real_mcp_clients_in_parallel_and_persistence(tmp_path):
    sock = socket.socket()
    sock.bind(('127.0.0.1',0))
    port = sock.getsockname()[1]
    sock.close()
    app = create_app(tmp_path,port)
    store = app.state.store
    clients=[]
    for n in range(3):
        project=store.add_group('projects',f'Project {n}')
        saved=store.save(Method(title=f'Unique {n}',content=f'Method for {n}',scope='project',scope_id=project['id']))
        token=store.new_connection(f'Client {n}',project_id=project['id'],include_global=False,writable=True)['token']
        clients.append((token,saved['id']))
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=port,log_level='error'))
    thread=threading.Thread(target=lambda: asyncio.run(server.serve()),daemon=True)
    thread.start()
    try:
        for _ in range(100):
            if server.started: break
            time.sleep(.02)
        assert server.started
        async def visit(token,expected):
            async with httpx.AsyncClient(headers={'Authorization':'Bearer '+token},trust_env=False) as http:
                async with streamable_http_client(f'http://127.0.0.1:{port}/mcp',http_client=http) as (read,write,_):
                    async with ClientSession(read,write) as session:
                        await session.initialize()
                        result=await session.call_tool('search_methods',{'query':'unique'})
                        assert not result.isError
                        assert [m['id'] for m in result.structuredContent['items']]==[expected]
                        full=await session.call_tool('get_method',{'method_id':expected})
                        method=full.structuredContent
                        for field in ['id','version','created_at','updated_at']:method.pop(field)
                        method['content']='Updated concurrently'
                        updated=await session.call_tool('update_method',{'method_id':expected,'expected_version':1,'method':method})
                        assert not updated.isError
                        assert updated.structuredContent['version']==2
        async def run():
            await asyncio.gather(*(visit(*c) for c in clients))
        asyncio.run(run())
    finally:
        server.should_exit=True
        thread.join(5)
    reopened=Store(tmp_path)
    for _,identifier in clients:
        assert reopened.get(identifier)['content']=='Updated concurrently'
