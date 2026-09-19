"""Built-in stdio MCP transport; starts the shared desktop server on demand."""
import argparse
import json
import os
import sys
import threading
from pathlib import Path

from .runtime import default_data, ensure_server, watch_bridge

import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mcp-stdio', action='store_true')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--data-dir', type=Path, default=default_data())
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Invalid port')
    headers = {'Accept':'application/json, text/event-stream'}
    token = os.environ.get('CYAICODEX_MCP_TOKEN', '')
    if token:
        headers['Authorization'] = 'Bearer '+token
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    ensure_server(args.port, args.data_dir)
    threading.Thread(target=watch_bridge, args=(args.port,), daemon=True).start()
    with httpx.Client(base_url=f'http://127.0.0.1:{args.port}', headers=headers, timeout=120, trust_env=False) as client:
        for line in sys.stdin:
            message = None
            try:
                message = json.loads(line)
                response = client.post('/mcp', json=message)
                response.raise_for_status()
                if 'id' not in message:
                    continue
                result = response.json()
            except Exception:
                if not isinstance(message, dict) or 'id' not in message:
                    continue
                result = {'jsonrpc':'2.0','id':message['id'],'error':{'code':-32000,
                    'message':'CyAICodex inaccessible : vérifiez que le serveur est lancé et que le jeton est valide.'}}
            print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
