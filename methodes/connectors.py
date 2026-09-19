"""Additional assistant transports, independent from the web interface."""
import asyncio
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from .local_clients import run_client


CONNECTORS = {
    'antigravity': {'name': 'Antigravity', 'kind': 'cli', 'executables': ['agy'],
        'paths': ['%LOCALAPPDATA%/agy/bin/agy.exe'], 'models_args': ['models'],
        'docs': 'https://antigravity.google/docs/cli/headless/', 'images': False,
        'policy': 'native-plan'},
    'command_code': {'name': 'Command Code', 'kind': 'cli', 'executables': ['command-code', 'cmdc'], 'npm': 'command-code',
        'paths': [], 'models_args': ['--list-models'],
        'docs': 'https://commandcode.ai/docs/headless', 'images': False, 'policy': 'native-plan'},
    'codebuddy': {'name': 'CodeBuddy', 'kind': 'cli', 'executables': ['codebuddy', 'cbc'], 'npm': '@tencent-ai/codebuddy-code',
        'paths': [], 'models_args': None,
        'docs': 'https://www.codebuddy.ai/docs/cli/cli-reference', 'images': False, 'policy': 'no-tools'},
    'openrouter': {'name': 'OpenRouter', 'kind': 'http', 'url': 'https://openrouter.ai/api/v1',
        'docs': 'https://openrouter.ai/docs/api/reference/overview', 'images': True, 'policy': 'no-tools'},
    'lmstudio': {'name': 'LM Studio', 'kind': 'http', 'url': 'http://127.0.0.1:1234/v1',
        'docs': 'https://lmstudio.ai/docs/developer/openai-compat', 'images': True, 'policy': 'no-tools'},
}


def descriptor(identifier):
    if identifier not in CONNECTORS:
        raise ValueError('Connecteur inconnu.')
    return CONNECTORS[identifier]


def configuration(store, identifier):
    info = descriptor(identifier)
    saved = json.loads(store.setting('connector_' + identifier, '{}'))
    return {'path': saved.get('path', ''), 'url': saved.get('url', info.get('url', '')),
            'model': saved.get('model', '')}


def endpoint(identifier, value):
    value = value.strip().rstrip('/')
    parsed = urlsplit(value)
    if identifier == 'openrouter':
        if value != CONNECTORS[identifier]['url']:
            raise ValueError('Utilisez l’adresse officielle OpenRouter.')
    elif (parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1', 'localhost', '::1'}
          or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path != '/v1'):
        raise ValueError('Indiquez une adresse HTTP locale terminée par /v1.')
    return value


def save_configuration(store, identifier, data):
    info = descriptor(identifier)
    current = configuration(store, identifier)
    updated = {**current, **{k: data[k].strip() for k in ('path', 'url', 'model') if k in data}}
    if info['kind'] == 'cli' and updated['path']:
        path = Path(updated['path'])
        if not path.is_file() or path.suffix.lower() != '.exe':
            raise ValueError('Le chemin du client doit désigner un fichier .exe existant.')
    if info['kind'] == 'http':
        updated['url'] = endpoint(identifier, updated['url'])
    encrypted = None
    if data.get('clear_key'):
        encrypted = ''
    elif data.get('key'):
        from .assist import protect
        encrypted = protect(data['key'].strip())
    with store.db() as db:
        db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)', ('connector_' + identifier, json.dumps(updated)))
        if encrypted is not None:
            db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)', (identifier + '_key', encrypted))
        db.execute('DELETE FROM settings WHERE key=?', ('connector_test_' + identifier,))
    return updated


def command(store, identifier):
    info = descriptor(identifier)
    override = configuration(store, identifier)['path']
    if override:
        path = Path(override)
        if path.is_file() and path.suffix.lower() == '.exe':
            return [str(path)]
        raise ValueError('Le chemin du client doit désigner un fichier .exe existant.')
    candidates = []
    for name in info['executables']:
        found = shutil.which(name + '.exe') or shutil.which(name)
        if found:
            candidates.append(Path(found))
        candidates.extend([Path.home()/'.local/bin'/(name+'.exe'), Path.home()/('.'+name)/'bin'/(name+'.exe')])
    candidates.extend(Path(os.path.expandvars(p)) for p in info['paths'])
    for path in candidates:
        if path.is_file() and path.suffix.lower() not in {'.cmd', '.bat', '.ps1'}:
            return [str(path)]
    if info.get('npm'):
        node = shutil.which('node.exe') or shutil.which('node')
        if not node:
            fallback = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'nodejs/node.exe'
            node = str(fallback) if fallback.is_file() else None
        roots = [Path(os.environ.get('APPDATA', Path.home()/'AppData/Roaming'))/'npm/node_modules',
                 store.folder/'local-clients/node_modules']
        roots.extend(path.parent/'node_modules' for path in candidates if path.suffix.lower() in {'.cmd', '.ps1'})
        for root in roots:
            package = root/info['npm']
            manifest = package/'package.json'
            if not manifest.is_file():
                continue
            try:
                data = json.loads(manifest.read_text(encoding='utf-8'))
                entries = data.get('bin', {})
                if isinstance(entries, str):
                    entries = {info['executables'][0]: entries}
                for name in info['executables']:
                    entry = entries.get(name)
                    if not isinstance(entry, str):
                        continue
                    path = (package/entry).resolve()
                    if not path.is_relative_to(package.resolve()) or not path.is_file():
                        continue
                    if path.suffix.lower() == '.exe':
                        return [str(path)]
                    if node and path.suffix.lower() in {'.js', '.mjs', '.cjs'}:
                        return [node, str(path)]
            except (ValueError, OSError, AttributeError):
                continue
    # Never treat Windows cmd.exe as the Command Code executable.
    raise ValueError('Client introuvable. Installez-le ou indiquez son chemin .exe.')


def headers(store, identifier):
    from .assist import protect
    encrypted = store.setting(identifier + '_key')
    key = protect(encrypted, decrypt=True) if encrypted else ''
    if identifier == 'openrouter' and not key:
        key = os.environ.get('OPENROUTER_API_KEY', '')
    if identifier == 'openrouter' and not key:
        raise ValueError('Ajoutez une clé API pour ce connecteur.')
    return {'Authorization': 'Bearer ' + key} if key else {}


def launch(store, identifier):
    import base64
    import subprocess
    if descriptor(identifier)['kind'] != 'cli':
        raise ValueError('Ce connecteur utilise une clé API ou un serveur local.')
    argv = command(store, identifier)
    workspace = store.folder / 'cli-workspaces' / identifier
    workspace.mkdir(parents=True, exist_ok=True)
    script = '& ' + ' '.join("'" + arg.replace("'", "''") + "'" for arg in argv)
    encoded = base64.b64encode(script.encode('utf-16le')).decode()
    # Explicit user action opens the client's own interactive sign-in interface.
    subprocess.Popen(['powershell.exe', '-NoProfile', '-NoExit', '-EncodedCommand', encoded],
                     cwd=workspace, creationflags=subprocess.CREATE_NEW_CONSOLE)


def model_rows(data):
    rows = data if isinstance(data, list) else data.get('models', data.get('data', [])) if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise ValueError('Catalogue de modèles invalide.')
    result = []
    for row in rows:
        value = row if isinstance(row, str) else row.get('id') or row.get('name') if isinstance(row, dict) else None
        if isinstance(value, str) and value and len(value) <= 200:
            result.append(value)
    return list(dict.fromkeys(result))


async def request_json(store, identifier, suffix, payload=None):
    config = configuration(store, identifier)
    url = endpoint(identifier, config['url']) + suffix
    async with httpx.AsyncClient(timeout=180 if payload is not None else 15, trust_env=False,
                                 follow_redirects=False) as client:
        try:
            async with client.stream('POST' if payload is not None else 'GET', url,
                                     headers=headers(store, identifier), json=payload) as response:
                if response.status_code >= 300:
                    raise ValueError(f'Le fournisseur a refusé la requête (HTTP {response.status_code}). Vérifiez clé, modèle et quota.')
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > 8 * 1024 * 1024:
                        raise ValueError('Réponse du connecteur trop volumineuse.')
        except httpx.HTTPError:
            raise ValueError('Connecteur inaccessible. Vérifiez son adresse et son démarrage.') from None
    try:
        return json.loads(body)
    except (ValueError, UnicodeError):
        raise ValueError('Réponse JSON du connecteur invalide.') from None


async def models(store, identifier):
    info = descriptor(identifier)
    if info['kind'] == 'http':
        return model_rows(await request_json(store, identifier, '/models'))
    if not info['models_args']:
        raise ValueError('Catalogue non disponible : saisissez un identifiant de modèle.')
    output = await run_client(command(store, identifier) + info['models_args'], timeout=30)
    try:
        return model_rows(json.loads(output))
    except json.JSONDecodeError:
        if identifier == 'antigravity':
            values = [line.split('\t')[0].strip() for line in output.splitlines() if '\t' in line]
            if values:
                return values
        raise ValueError('Catalogue non disponible : saisissez un identifiant de modèle.') from None


async def detect(store, identifier):
    info = descriptor(identifier)
    result = {'available': False, 'authenticated': None, 'generation': 'not_tested', 'version': '', 'models': []}
    try:
        if info['kind'] == 'cli':
            argv = command(store, identifier)
            version = await run_client(argv + ['--version'], timeout=20)
            result.update(available=True, version=version.strip()[:150], message='Client détecté. La génération reste à tester.')
        else:
            result['models'] = await models(store, identifier)
            result.update(available=True, message='Serveur accessible. La génération reste à tester.')
    except (ValueError, OSError):
        result['message'] = 'Connecteur indisponible. Vérifiez son installation et ses paramètres.'
    result['last_test'] = json.loads(store.setting('connector_test_' + identifier, 'null'))
    return result


def cli_arguments(identifier, prompt, model):
    if identifier == 'antigravity':
        args = ['--input-format', 'stream-json', '--output-format', 'stream-json',
                '--mode', 'plan', '--disable-slash-commands', '--print-timeout', '3m']
        payload = json.dumps({'event': 'user', 'message': {'content': prompt}}) + '\n'
    elif identifier == 'command_code':
        args = ['-p', '--output-format', 'json', '--skip-onboarding', '--plan']
        payload = prompt
    elif identifier == 'codebuddy':
        args = ['-p', '--output-format', 'stream-json', '--input-format', 'stream-json', '--verbose',
                '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                '--setting-sources', '', '--no-session-persistence']
        payload = json.dumps({'type': 'user', 'message': {'role': 'user', 'content': prompt}}) + '\n'
    else:
        raise ValueError('Connecteur inconnu.')
    if model:
        args += ['--model', model]
    return args, payload


def parse_result(identifier, output):
    """A partial response, EOF or exit code zero alone is never success."""
    final = None
    for line in output.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            raise ValueError('Réponse JSON du connecteur invalide.') from None
        if not isinstance(event, dict):
            raise ValueError('Réponse JSON du connecteur invalide.')
        kind = event.get('event') if identifier == 'antigravity' else event.get('type')
        if kind in {'error', 'turn.failed'}:
            raise ValueError('Le connecteur a refusé la demande. Vérifiez votre compte et le modèle.')
        if kind != 'result':
            continue
        if final is not None:
            raise ValueError('Plusieurs résultats terminaux reçus du connecteur.')
        payload = event.get('result') if identifier == 'antigravity' else event
        if not isinstance(payload, dict):
            raise ValueError('Réponse JSON du connecteur invalide.')
        status_key = 'status' if identifier == 'antigravity' else 'subtype'
        if payload.get(status_key) not in {'SUCCESS', 'success'} or payload.get('is_error') or payload.get('denied_actions'):
            raise ValueError('Le connecteur a refusé la demande. Vérifiez votre compte et le modèle.')
        text = payload.get({'antigravity': 'response', 'command_code': 'finalText', 'codebuddy': 'result'}[identifier])
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Le fournisseur a renvoyé une réponse sans texte.')
        final = text
    if final is None:
        raise ValueError('Flux fermé sans résultat final confirmé.')
    return final


async def generate(store, identifier, model, instructions, messages, previews=()):
    info = descriptor(identifier)
    model = model or configuration(store, identifier)['model']
    if previews and not info['images']:
        raise ValueError('Ce connecteur accepte uniquement le texte. Retirez l’image ou choisissez un autre assistant.')
    if info['kind'] == 'cli':
        prompt = instructions + '\nConversation:\n' + json.dumps(messages, ensure_ascii=False)
        args, payload = cli_arguments(identifier, prompt, model)
        with tempfile.TemporaryDirectory(prefix='assistant-', dir=store.folder) as scratch:
            output = await run_client(command(store, identifier) + args, payload, scratch)
        return parse_result(identifier, output)
    if not model:
        raise ValueError("Indiquez l'identifiant du modèle à utiliser.")
    chat = [{'role': 'system', 'content': instructions}] + [dict(message) for message in messages]
    if previews:
        index = next(i for i in range(len(chat) - 1, 0, -1) if chat[i]['role'] == 'user')
        chat[index]['content'] = [{'type': 'text', 'text': chat[index]['content']}] + [
            {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + image}} for image in previews]
    data = await request_json(store, identifier, '/chat/completions',
                              {'model': model, 'messages': chat, 'stream': False, 'max_tokens': 4000})
    choices = data.get('choices') if isinstance(data, dict) else None
    if not choices or not isinstance(choices, list) or not isinstance(choices[0], dict):
        raise ValueError('Réponse JSON du connecteur invalide.')
    choice = choices[0]
    if choice.get('finish_reason') != 'stop':
        raise ValueError('Réponse interrompue ou refusée par le fournisseur.')
    message = choice.get('message', {})
    text = message.get('content') if isinstance(message, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Le fournisseur a renvoyé une réponse sans texte.')
    return text


async def test_generation(store, identifier, model=''):
    result = {'at': datetime.now(timezone.utc).isoformat(), 'model': model or configuration(store, identifier)['model'],
              'passed': False, 'message': 'Test de génération échoué.'}
    try:
        answer = await generate(store, identifier, model, 'Do not use tools. Reply exactly with CYAICODEX_OK.',
                                [{'role': 'user', 'content': 'Reply exactly with CYAICODEX_OK.'}])
        result['passed'] = answer.strip() == 'CYAICODEX_OK'
        result['message'] = 'Réponse réelle vérifiée.' if result['passed'] else 'Réponse reçue, mais différente du marqueur attendu.'
    except (ValueError, OSError) as exc:
        result['message'] = str(exc) if isinstance(exc, ValueError) else 'Connecteur inaccessible. Vérifiez son adresse et son démarrage.'
    store.set_setting('connector_test_' + identifier, json.dumps(result))
    return result
