"""GitHub release updates. Credentials never leave the GitHub API host."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
from urllib.parse import urlparse

import httpx

from . import __version__
from .assist import protect
from .runtime import root_path, launch_independent

REPOSITORY = 'MrMybal/CyAICodex'
API = 'https://api.github.com/repos/' + REPOSITORY
RELEASES = 'https://github.com/' + REPOSITORY + '/releases'
MAX_INSTALLER = 300 * 1024 * 1024


def version_tuple(value):
    if not isinstance(value, str) or not re.fullmatch(r'v?\d+\.\d+\.\d+', value):
        raise ValueError('Version GitHub non reconnue.')
    return tuple(map(int, value.removeprefix('v').split('.')))


def asset_details(release):
    version_tuple(release.get('tag_name'))
    if release.get('draft') or release.get('prerelease'):
        raise ValueError('Cette version n’est pas une version stable publiée.')
    version = release['tag_name'].removeprefix('v')
    name = f'CyAICodex-Setup-{version}.exe'
    assets = [a for a in release.get('assets', []) if a.get('name') == name]
    if len(assets) != 1:
        raise ValueError('Cette release ne contient pas encore d’installateur compatible.')
    asset = assets[0]
    if (not isinstance(asset.get('id'), int) or asset['id'] <= 0 or
        asset.get('url') != API + '/releases/assets/' + str(asset['id']) or
        asset.get('state') != 'uploaded' or not isinstance(asset.get('size'), int) or
        not 0 < asset['size'] <= MAX_INSTALLER or
        not re.fullmatch(r'sha256:[0-9a-f]{64}', asset.get('digest') or '')):
        raise ValueError('Les informations de vérification de l’installateur sont incomplètes.')
    return version, asset


def allowed_download(url):
    parsed = urlparse(url)
    return (parsed.scheme == 'https' and parsed.hostname in {
        'api.github.com', 'github.com', 'release-assets.githubusercontent.com',
        'objects.githubusercontent.com', 'objects-origin.githubusercontent.com'}
        and parsed.port in (None, 443) and not parsed.username and not parsed.password)


class Updater:
    def __init__(self, store, port=8765):
        self.store, self.port = store, port
        self.lock = threading.Lock()
        self.latest = None
        self.status = 'idle'
        self.message = ''

    def settings(self):
        return {'automatic': self.store.setting('updates_automatic', 'true') == 'true',
                'use_git': self.store.setting('updates_use_git', 'false') == 'true',
                'token_configured': bool(self.store.setting('updates_token'))}

    def configure(self, body):
        token = body.get('token', '').strip()
        if token or body.get('clear_token'):
            self.store.set_setting('updates_token', protect(token) if token and not body.get('clear_token') else '')
        for key in ('automatic', 'use_git'):
            if key in body:
                self.store.set_setting('updates_' + key, json.dumps(body[key]))
        self.latest = None
        self.status, self.message = 'idle', ''
        return self.snapshot()

    def credentials(self):
        encrypted = self.store.setting('updates_token')
        if encrypted:
            return protect(encrypted, decrypt=True)
        if not self.settings()['use_git']:
            return ''
        git = shutil.which('git')
        if not git:
            raise ValueError('Git est introuvable. Ajoutez un jeton GitHub pour ce dépôt privé.')
        env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'Never'}
        try:
            result = subprocess.run([git, 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n',
                text=True, capture_output=True, timeout=15, env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        except (OSError, subprocess.TimeoutExpired):
            raise ValueError('La connexion GitHub locale est indisponible.') from None
        data = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
        if result.returncode or not data.get('password'):
            raise ValueError('Connectez Git à GitHub ou ajoutez un jeton pour ce dépôt privé.')
        return data['password']

    def snapshot(self):
        latest = self.latest
        return {**self.settings(), 'current_version': __version__, 'repository': REPOSITORY,
                'release_url': RELEASES, 'status': self.status, 'message': self.message,
                'latest_version': latest['tag_name'].removeprefix('v') if latest else None,
                'available': bool(latest and version_tuple(latest['tag_name']) > version_tuple(__version__)),
                'install_supported': os.name == 'nt' and bool(getattr(sys, 'frozen', False)) and self.port == 8765}

    def fetch_latest(self, client):
        # Public repositories need no credential, including after a visibility change.
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'CyAICodex/' + __version__}
        response = client.get(API + '/releases/latest', headers=headers)
        token = ''
        if response.status_code in (401, 403, 404):
            token = self.credentials()
            if token:
                response = client.get(API + '/releases/latest', headers={**headers, 'Authorization': 'Bearer ' + token})
        if response.status_code == 404:
            raise ValueError('Dépôt privé inaccessible ou aucune release publiée : configurez l’accès GitHub.')
        if response.status_code in (401, 403):
            raise ValueError('Accès GitHub refusé ou limite de requêtes atteinte. Vérifiez les droits du compte.')
        response.raise_for_status()
        if len(response.content) > 2 * 1024 * 1024:
            raise ValueError('Réponse GitHub trop volumineuse.')
        release = response.json()
        version_tuple(release.get('tag_name'))
        if release.get('draft') or release.get('prerelease'):
            raise ValueError('Aucune version stable publiée.')
        return release, token

    def check(self):
        if not self.lock.acquire(blocking=False):
            return self.snapshot()
        try:
            self.status, self.message = 'checking', ''
            with httpx.Client(timeout=20, trust_env=False, follow_redirects=False) as client:
                self.latest, _ = self.fetch_latest(client)
            self.status = 'available' if self.snapshot()['available'] else 'current'
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            self.latest = None
            self.status = 'error'
            self.message = 'Impossible de vérifier les mises à jour. Pour un dépôt privé, vérifiez votre connexion GitHub ou votre jeton ; sinon vérifiez le réseau.'
        finally:
            self.lock.release()
        return self.snapshot()

    def download(self, client, asset, token, path):
        url = asset['url']
        digest = hashlib.sha256()
        count = 0
        for _ in range(5):
            if not allowed_download(url):
                raise ValueError('Adresse de téléchargement GitHub refusée.')
            headers = {'Accept': 'application/octet-stream', 'User-Agent': 'CyAICodex/' + __version__}
            if urlparse(url).hostname == 'api.github.com' and token:
                headers['Authorization'] = 'Bearer ' + token
            with client.stream('GET', url, headers=headers) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    url = response.headers.get('location', '')
                    continue
                response.raise_for_status()
                with path.open('xb') as output:
                    for chunk in response.iter_bytes():
                        count += len(chunk)
                        if count > asset['size'] or count > MAX_INSTALLER:
                            raise ValueError('Installateur trop volumineux.')
                        digest.update(chunk)
                        output.write(chunk)
                if count != asset['size'] or 'sha256:' + digest.hexdigest() != asset['digest']:
                    raise ValueError('La vérification de l’installateur a échoué. Aucun fichier ne sera exécuté.')
                if path.read_bytes()[:2] != b'MZ':
                    raise ValueError('Format de l’installateur invalide.')
                return
        raise ValueError('Trop de redirections pendant le téléchargement.')

    def install(self):
        if not self.snapshot()['install_supported']:
            raise ValueError('Installez la version Windows standard pour utiliser la mise à jour intégrée.')
        if not self.lock.acquire(blocking=False):
            raise ValueError('Une vérification ou une installation est déjà en cours.')
        temporary = None
        try:
            self.status, self.message = 'downloading', ''
            with httpx.Client(timeout=120, trust_env=False, follow_redirects=False) as client:
                release, token = self.fetch_latest(client)
                if version_tuple(release['tag_name']) <= version_tuple(__version__):
                    raise ValueError('CyAICodex est déjà à jour.')
                version, asset = asset_details(release)
                import uuid
                folder = self.store.folder / 'updates' / str(uuid.uuid4())
                folder.mkdir(parents=True)
                temporary = folder / (asset['name'] + '.part')
                self.download(client, asset, token, temporary)
            installer = temporary.with_suffix('')
            temporary.replace(installer)
            args = [str(installer), '/NORESTART', '/CURRENTUSER']
            if (root_path() / 'installed.txt').is_file():
                args.append('/DIR=' + str(root_path()))
            else:
                args.append('/LEGACYDATA=' + str(self.store.folder.resolve()))
            launch_independent(args, visible=True)
            self.latest, self.status = release, 'installing'
            return self.snapshot()
        except (httpx.HTTPError, OSError):
            self.status = 'error'
            raise ValueError('Téléchargement ou lancement impossible. Réessayez la mise à jour.') from None
        except ValueError:
            self.status = 'error'
            raise
        finally:
            if temporary and temporary.exists():
                temporary.unlink()
            self.lock.release()
