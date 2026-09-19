"""Stdio transport for Claude Desktop; forwards to the running local HTTP MCP."""
import argparse
import json
import os
import sys

import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mcp-stdio', action='store_true')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Invalid port')
    headers = {'Accept':'application/json, text/event-stream'}
    token = os.environ.get('CYAICODEX_MCP_TOKEN', '')
    if token:
        headers['Authorization'] = 'Bearer '+token
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
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
