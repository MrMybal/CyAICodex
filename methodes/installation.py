"""Per-user installation maintenance; application data survives uninstall."""
import argparse
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
from contextlib import closing

from .runtime import default_data, root_path


def migrate_data(source, target):
    source, target = Path(source).resolve(), Path(target).resolve()
    if source == target:
        return
    if not (source / 'methodes.sqlite3').is_file():
        raise ValueError('Le dossier sélectionné ne contient pas de bibliothèque CyAICodex.')
    if target.exists() and any(target.iterdir()):
        raise ValueError('Une bibliothèque existe déjà à destination. Elle ne sera pas remplacée.')
    target.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix='migration-', dir=target.parent))
    try:
        for path in source.iterdir():
            if path.name in ('methodes.sqlite3', 'methodes.sqlite3-wal', 'methodes.sqlite3-shm', 'updates') or path.suffix == '.log':
                continue
            if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
                raise ValueError('La bibliothèque contient un lien de dossier non pris en charge.')
            if path.is_dir():
                shutil.copytree(path, staged / path.name)
            else:
                shutil.copy2(path, staged / path.name)
        with closing(sqlite3.connect(source / 'methodes.sqlite3')) as src, closing(sqlite3.connect(staged / 'methodes.sqlite3')) as dst:
            src.backup(dst)
            if dst.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('La copie de la bibliothèque n’a pas pu être vérifiée.')
            dst.execute('INSERT OR REPLACE INTO settings VALUES (?, ?)', ('previous_install_root', str(source.parent)))
            dst.commit()
        if target.exists():
            target.rmdir()  # Only an empty destination is accepted above.
        staged.replace(target)
    finally:
        if staged.exists() and staged.resolve().parent == target.parent and staged.name.startswith('migration-'):
            shutil.rmtree(staged)


def reconnect_existing(store):
    from .mcp_setup import MCPSetup, CLIENTS, read_config, write_config
    setup = MCPSetup(store, 8765)
    results = {}
    for client in CLIENTS:
        try:
            path = setup.path(client)
            if not path.exists():
                continue
            raw, data, section = read_config(client, path)
            old = data.get(section, {}).get('cyaicodex')
            if not old or not setup.managed(client, old):
                continue
            entry = setup.entry(client, setup.token(client, old))
            # Keep client policies and explicit disabled state, replacing transport fields only.
            transport = {'url', 'headers', 'http_headers', 'oauth', 'type', 'command', 'args', 'env', 'environment', 'timeout', 'startup_timeout_sec'}
            entry.update({key: value for key, value in old.items() if key not in transport})
            data[section]['cyaicodex'] = entry
            write_config(client, path, raw, data)
            results[client] = 'updated'
        except (ValueError, OSError):
            results[client] = 'Configure this client from Connections'
    store.set_setting('installation_connections', json.dumps(results))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--finish-install', action='store_true')
    parser.add_argument('--legacy-data', type=Path)
    parser.add_argument('--data-dir', type=Path, default=default_data())
    parser.add_argument('--startup', choices=['enabled', 'disabled'])
    args = parser.parse_args()
    import logging
    args.data_dir.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=args.data_dir.parent / 'installation.log', level=logging.INFO,
                        encoding='utf-8', format='%(asctime)s %(levelname)s %(message)s')
    if args.legacy_data:
        migrate_data(args.legacy_data, args.data_dir)
    existing = args.data_dir / 'methodes.sqlite3'
    if existing.is_file():
        from datetime import datetime, timezone
        folder = args.data_dir / 'backups'
        folder.mkdir(exist_ok=True)
        backup = folder / ('before-install-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f') + '.sqlite3')
        with closing(sqlite3.connect(existing)) as source, closing(sqlite3.connect(backup)) as target:
            source.backup(target)
    from .store import Store
    from .startup import startup_enabled, set_startup
    store = Store(args.data_dir)
    from .examples import seed_examples
    seed_examples(store)
    reconnect_existing(store)
    store.set_setting('installation_root', str(root_path()))
    if args.startup is not None:
        set_startup(args.startup == 'enabled', 8765, args.data_dir)
    elif startup_enabled():
        set_startup(True, 8765, args.data_dir)
