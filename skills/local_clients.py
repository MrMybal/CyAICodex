"""Local client discovery works even with Explorer's stale PATH."""
import asyncio
import json
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import httpx


def client_command(name, store=None):
    override = store.setting(name + '_path') if store else ''
    if override:
        path = Path(override)
        if path.is_file() and path.suffix.lower() == '.exe':
            return [str(path)]
        raise ValueError(f'Le chemin configuré pour {name} doit désigner un fichier .exe existant.')
    executable_name = 'claude' if name == 'claude_code' else name
    home = Path.home()
    local = Path(os.environ.get('LOCALAPPDATA', home / 'AppData/Local'))
    roaming = Path(os.environ.get('APPDATA', home / 'AppData/Roaming'))
    candidates = []
    if name == 'codex':
        candidates += sorted((local / 'OpenAI/Codex/bin').glob('*/codex.exe'), key=lambda p: p.stat().st_mtime, reverse=True)
    candidates += [home / '.local/bin' / (executable_name+'.exe'), home / ('.'+executable_name) / 'bin' / (executable_name+'.exe'),
                   local / 'Programs' / executable_name / (executable_name+'.exe'), roaming / 'npm' / (executable_name+'.exe')]
    found = shutil.which(executable_name+'.exe') or shutil.which(executable_name)
    if found and Path(found).suffix.lower() not in ('.cmd', '.bat', '.ps1'):
        candidates.insert(0, Path(found))
    if store and name in ('claude_code', 'opencode'):
        package = '@anthropic-ai/claude-code/bin/claude.exe' if name == 'claude_code' else 'opencode-ai/bin/opencode.exe'
        candidates.insert(0, store.folder / 'local-clients/node_modules' / package)
    for path in candidates:
        if path.is_file():
            return [str(path)]
    # Call npm entry points through node, never a shell containing the prompt.
    node = shutil.which('node.exe') or shutil.which('node')
    if not node:
        path = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'nodejs/node.exe'
        node = str(path) if path.is_file() else None
    entry = {'claude_code': '@anthropic-ai/claude-code/cli.js',
             'claude': '@anthropic-ai/claude-code/cli.js', 'opencode': 'opencode-ai/bin/opencode'}.get(name)
    if node and entry:
        entries = ([store.folder / 'local-clients/node_modules' / entry] if store else []) + [roaming / 'npm/node_modules' / entry]
        for path in entries:
            if path.is_file():
                return [node, str(path)]
    raise ValueError(f'{name} introuvable. Installez son client local ou indiquez son chemin dans Paramètres.')


def ollama_url(store):
    url = store.setting('ollama_url', 'http://127.0.0.1:11434').rstrip('/')
    parsed = urlparse(url)
    if parsed.scheme != 'http' or parsed.hostname not in ('localhost', '127.0.0.1', '::1') or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path:
        raise ValueError('Ollama : indiquez une adresse HTTP locale, par exemple http://127.0.0.1:11434.')
    return url


async def run_client(args, text='', cwd=None, env=None, timeout=180):
    process = await asyncio.create_subprocess_exec(*args, cwd=cwd, env=env,
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
        limit=32 * 1024 * 1024)
    async def read_bounded(stream, retain):
        chunks, size = [], 0
        while chunk := await stream.read(65536):
            size += len(chunk)
            if size > 8 * 1024 * 1024:
                raise ValueError('Réponse du connecteur trop volumineuse.')
            if retain:
                chunks.append(chunk)
        return b''.join(chunks)

    async def write_input():
        try:
            process.stdin.write(text.encode('utf-8'))
            await process.stdin.drain()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            process.stdin.close()

    tasks = [asyncio.create_task(read_bounded(process.stdout, True)),
             asyncio.create_task(read_bounded(process.stderr, False)), asyncio.create_task(write_input())]
    try:
        async with asyncio.timeout(timeout):
            out, _, _ = await asyncio.gather(*tasks)
            await process.wait()
    except asyncio.TimeoutError:
        raise ValueError('Le client local a dépassé le délai de réponse. Vérifiez son compte et le modèle.') from None
    finally:
        if process.returncode is None:
            if os.name == 'nt':
                killer = await asyncio.create_subprocess_exec('taskkill.exe', '/PID', str(process.pid), '/T', '/F',
                    stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                await killer.wait()
            if process.returncode is None:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
            await process.wait()
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    if process.returncode:
        # Do not return stderr: providers may repeat prompts or credentials.
        raise ValueError(f'Le client local a échoué (code {process.returncode}). Vérifiez sa connexion et sa version dans Paramètres.')
    return out.decode('utf-8', errors='replace')


async def local_status(provider, store):
    if provider == 'ollama':
        async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
            try:
                response = await client.get(ollama_url(store)+'/api/tags')
                response.raise_for_status()
            except httpx.HTTPError:
                return {'available': False, 'message': 'Ollama ne répond pas. Lancez Ollama sur ce PC.', 'models': []}
        models = [m['name'] for m in response.json().get('models', [])]
        return {'available': True, 'models': models, 'message': 'Ollama actif · '+str(len(models))+' modèle(s) installé(s)'}
    try:
        command = client_command(provider, store)
        version = (await run_client(command+['--version'], timeout=20)).strip()[:150]
    except ValueError as exc:
        return {'available': False, 'message': str(exc)}
    message = version or 'Client disponible'
    connected = None
    if provider == 'claude_code':
        try:
            account = json.loads(await run_client(command+['auth','status','--json'], timeout=20))
            connected = bool(account.get('loggedIn'))
        except (ValueError, json.JSONDecodeError):
            connected = False
        message += ' · compte connecté' if connected else ' · cliquez sur Se connecter'
    return {'available': True, 'message': message, 'path': command[-1], 'connected': connected}


def launch_login(provider, store):
    command = client_command(provider, store)
    command += ['auth', 'login']
    # A terminal is intentional here: the user clicked the interactive sign-in button.
    script = '& ' + ' '.join("'"+arg.replace("'", "''")+"'" for arg in command)
    import base64
    encoded = base64.b64encode(script.encode('utf-16le')).decode()
    subprocess.Popen(['powershell.exe', '-NoProfile', '-NoExit', '-EncodedCommand', encoded],
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
