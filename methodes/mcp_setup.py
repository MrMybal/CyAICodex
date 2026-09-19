"""Install only our MCP entry and diagnose the actual configured transport."""
import asyncio
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
from datetime import datetime, timezone

import httpx
import json5
import tomlkit
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

CLIENTS = {'codex':'Codex', 'claude_desktop':'Claude Desktop', 'opencode':'OpenCode'}
ENTRY = 'cyaicodex'
LOCK = threading.Lock()


def config_path(client):
    home = Path.home()
    if client == 'codex':
        return Path(os.environ.get('CODEX_HOME', home/'.codex'))/'config.toml'
    if client == 'opencode':
        if os.environ.get('OPENCODE_CONFIG'):
            return Path(os.environ['OPENCODE_CONFIG']).resolve()
        folder = Path(os.environ.get('XDG_CONFIG_HOME', home/'.config'))/'opencode'
        return folder/('opencode.jsonc' if (folder/'opencode.jsonc').exists() else 'opencode.json')
    if client == 'claude_desktop':
        standard = Path(os.environ.get('APPDATA', home/'AppData/Roaming'))/'Claude/claude_desktop_config.json'
        local = Path(os.environ.get('LOCALAPPDATA', home/'AppData/Local'))
        packaged = [folder/'claude_desktop_config.json' for folder in (local/'Packages').glob('Claude_*/LocalCache/Roaming/Claude') if folder.is_dir()]
        candidates = ([standard] if standard.parent.is_dir() else []) + packaged
        if len(candidates) > 1:
            raise ValueError('Plusieurs profils Claude Desktop détectés. Ouvrez sa configuration depuis Paramètres > Développeur pour identifier le profil actif.')
        return candidates[0] if candidates else standard
    raise ValueError('Client MCP inconnu.')


def root_path():
    return Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent


def read_config(client, path):
    raw = path.read_bytes() if path.exists() else None
    try:
        text = raw.decode('utf-8-sig') if raw else ''
        data = tomlkit.parse(text) if client == 'codex' else (json5.loads(text, allow_duplicate_keys=False) if text.strip() else {})
        if not isinstance(data, dict):
            raise ValueError()
        key = {'codex':'mcp_servers', 'claude_desktop':'mcpServers', 'opencode':'mcp'}[client]
        if key in data and not isinstance(data[key], dict):
            raise ValueError()
        return raw, data, key
    except Exception:
        raise ValueError('Configuration existante illisible. Aucun fichier ne sera remplacé ; corrigez sa syntaxe puis réessayez.') from None


def write_config(client, path, original, data):
    text = tomlkit.dumps(data) if client == 'codex' else json.dumps(data, ensure_ascii=False, indent=2)+'\n'
    encoded = text.encode('utf-8')
    if (path.read_bytes() if path.exists() else None) != original:
        raise ValueError('Le client vient de modifier sa configuration. Réessayez pour conserver ses changements.')
    if original == encoded:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    if (path.read_bytes() if path.exists() else None) != original:
        raise ValueError('Le client vient de modifier sa configuration. Réessayez pour conserver ses changements.')
    backup = None
    if original is not None:
        folder = path.parent/'.cyaicodex-backups'
        folder.mkdir(exist_ok=True)
        backup = folder/(path.name+'.'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.bak')
        shutil.copy2(path, backup)
    fd, filename = tempfile.mkstemp(prefix='.cyaicodex-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(encoded)
        if (path.read_bytes() if path.exists() else None) != original:
            raise ValueError('Configuration modifiée pendant la sauvegarde. Réessayez.')
        os.replace(filename, path)
    finally:
        Path(filename).unlink(missing_ok=True)
    return str(backup) if backup else None


class MCPSetup:
    def __init__(self, store, port, root=None, paths=None):
        self.store, self.port = store, port
        self.root = Path(root) if root else root_path()
        self.paths = paths
        self.url = f'http://127.0.0.1:{port}/mcp'

    def path(self, client):
        if client not in CLIENTS:
            raise ValueError('Client MCP inconnu.')
        return self.paths[client] if self.paths else config_path(client)

    def entry(self, client, token):
        headers = {'Authorization':'Bearer '+token} if token else {}
        if client == 'codex':
            result = {'url':self.url, 'enabled':True, 'startup_timeout_sec':30}
            if headers:
                result['http_headers'] = headers
            return result
        if client == 'opencode':
            result = {'type':'remote','url':self.url,'enabled':True, 'oauth':False}
            if headers:
                result['headers'] = headers
            return result
        return {'command':str(self.root/'CyAICodex-MCP.exe'), 'args':['--mcp-stdio','--port',str(self.port)],
                'env':{'CYAICODEX_MCP_TOKEN':token} if token else {}}

    def managed(self, client, entry):
        if not isinstance(entry, dict):
            return False
        if client == 'claude_desktop':
            return str(entry.get('command','')).lower() == str(self.root/'CyAICodex-MCP.exe').lower() and entry.get('args') == ['--mcp-stdio','--port',str(self.port)]
        return entry.get('url') == self.url

    def token(self, client, entry):
        if client == 'claude_desktop':
            return entry.get('env',{}).get('CYAICODEX_MCP_TOKEN','')
        headers = entry.get('http_headers' if client == 'codex' else 'headers',{})
        auth = headers.get('Authorization','')
        return auth[7:] if auth.startswith('Bearer ') else ''

    def install(self, client, options):
        with LOCK:
            path = self.path(client)
            original, data, section = read_config(client, path)
            existing = data.get(section,{}).get(ENTRY)
            if existing and not self.managed(client, existing):
                raise ValueError('Une entrée cyaicodex pointe ailleurs. Elle est conservée : renommez-la dans le client avant de connecter cette installation.')
            if client == 'claude_desktop' and not (self.root/'CyAICodex-MCP.exe').is_file():
                raise ValueError('Le relais CyAICodex-MCP.exe manque à côté de l’application. Réinstallez les deux exécutables ensemble.')
            context = self.store.context(options['project_id'], options['type_id'], options['include_global'])
            created = None
            token = ''
            if options['without_token']:
                prefs = json.loads(self.store.setting('preferences','{}'))
                if not prefs.get('local_no_token'):
                    raise ValueError('Activez d’abord l’accès sans jeton dans Paramètres, ou choisissez un jeton dédié.')
            else:
                previous = self.token(client, existing) if existing else ''
                connection = self.store.authenticate(previous) if previous else None
                if connection and all(connection[k] == context[k] for k in context) and bool(connection['writable']) == options['writable']:
                    token = previous
                else:
                    created = self.store.new_connection('Configuration automatique · '+CLIENTS[client], **context, writable=options['writable'])
                    token = created['token']
            try:
                entry = self.entry(client, token)
                if existing == entry:
                    return {'client':client,'path':str(path),'changed':False,'backup':None}
                if section not in data:
                    data[section] = {}
                data[section][ENTRY] = entry
                backup = write_config(client,path,original,data)
            except Exception:
                if created:
                    self.store.revoke(created['id'])
                raise
            # Keep unrelated/manual connections; only retire a previously generated token.
            key = 'setup_connection_'+client
            old_id = self.store.setting(key)
            if created or options['without_token']:
                self.store.set_setting(key,created['id'] if created else '')
                if old_id and (not created or old_id != created['id']):
                    self.store.revoke(old_id)
            return {'client':client,'path':str(path),'changed':True,'backup':backup}

    async def diagnose(self, client):
        result = {'client':client,'label':CLIENTS[client],'server':False,'configured':False,'mcp':False,
                  'tools':[], 'message':'', 'restart':'Après configuration, redémarrez ce client ou rechargez ses serveurs MCP. Les conversations déjà ouvertes peuvent garder leur ancienne liste d’outils.'}
        async with httpx.AsyncClient(timeout=3,trust_env=False) as http:
            try:
                r = await http.get(self.url.removesuffix('/mcp')+'/health')
                result['server'] = r.status_code == 200 and r.json().get('app') == 'methodes'
            except (httpx.HTTPError,ValueError):
                pass
        try:
            path = self.path(client)
            result['path'] = str(path)
            _, data, section = read_config(client,path)
            entry = data.get(section,{}).get(ENTRY)
            if not entry:
                result['message'] = 'CyAICodex n’est pas configuré dans ce client. Cliquez sur Configurer et tester.'
                return result
            if not self.managed(client,entry):
                result['message'] = 'L’entrée cyaicodex pointe vers une autre adresse ou un autre relais.'
                return result
            if entry.get('enabled') is False:
                result['message'] = 'Le serveur est désactivé dans la configuration du client.'
                return result
            result['configured'] = True
            if not result['server']:
                result['message'] = 'Serveur local arrêté ou inaccessible. Lancez CyAICodex et réessayez.'
                return result
            token = self.token(client,entry)
            if token and not self.store.authenticate(token):
                result['message'] = 'Jeton refusé ou révoqué. Cliquez sur Configurer et tester pour réparer la connexion.'
                return result
            if not token and not json.loads(self.store.setting('preferences','{}')).get('local_no_token'):
                result['message'] = 'Cette configuration n’a pas de jeton et l’accès sans jeton est désactivé.'
                return result
            async def probe(read,write):
                async with ClientSession(read,write) as session:
                    initialized = await session.initialize()
                    if initialized.serverInfo.name != 'CyAICodex':
                        raise ValueError('Serveur MCP inattendu.')
                    tools = await session.list_tools()
                    context = await session.call_tool('get_context',{})
                    if context.isError:
                        raise ValueError('Lecture du contexte refusée.')
                    result['tools'] = [t.name for t in tools.tools]
                    if not {'get_context','search_methods','import_image'}.issubset(result['tools']):
                        raise ValueError('Version MCP incomplète : mettez à jour CyAICodex.')
                    result['context'] = context.structuredContent or json.loads(context.content[0].text)
            async with asyncio.timeout(20):
                if client == 'claude_desktop':
                    if not Path(entry['command']).is_file():
                        raise ValueError('Relais CyAICodex-MCP.exe introuvable.')
                    params = StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})})
                    async with stdio_client(params) as (read,write):
                        await probe(read,write)
                else:
                    headers = {'Authorization':'Bearer '+token} if token else {}
                    async with httpx.AsyncClient(headers=headers,timeout=15,trust_env=False) as http:
                        async with streamable_http_client(self.url,http_client=http) as (read,write,_):
                            await probe(read,write)
            result['mcp'] = True
            result['message'] = f"Connexion MCP testée avec la configuration enregistrée : {len(result['tools'])} outils accessibles."
        except ValueError as exc:
            result['message'] = str(exc)
        except Exception:
            result['message'] = 'Échec du dialogue MCP avec cette configuration. Vérifiez le relais et relancez le client. Aucun secret n’est affiché dans ce diagnostic.'
        return result
