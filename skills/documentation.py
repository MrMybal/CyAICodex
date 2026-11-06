"""Open the exported CyDoc manual using an encoded local file URL."""
import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote, urlencode
import webbrowser

"""
@doc help-integration
@locale en
@title Python help integration
@section Integration
@symbol help_url
## Open local documentation {#open-local}

The Python host opens the exported CyDoc reader through a file URL. No HTTP reader is needed.

```python
from skills.documentation import open_help, help_url

# Opens the chapter in the system browser, even without the app server.
open_help('en', 'backup', 'restore')

# Stable media address inside the same reader window.
url = help_url('en', 'skills', media='skills-illustration')
```

## Public functions {#contracts}

| Function | Return | Behavior |
| --- | --- | --- |
| `help_root()` | `pathlib.Path` | The `Documentation` folder beside the executable, or at the source project root. |
| `help_url(locale='en', page='welcome', anchor=None, media=None)` | `str` | An encoded `file://` URL targeting `Documentation.html`. |
| `open_help(locale='en', page='welcome', anchor=None, media=None)` | `str` | Open the validated URL in the system browser, then return it. |

`locale` is `en` or `fr`; `page` is a stable chapter ID or alias. Optional `anchor` is an explicit section ID; `media` is an image block ID in that page. These helpers belong to the `skills.documentation` module. The host imports `pathlib`, `urllib.parse` and `webbrowser`; no browser JavaScript API is required.

help_url(locale='en', page='welcome', anchor=None, media=None) validates the page, section and media against the exported manifest, resolves page aliases, and returns a local file URL. Unknown targets raise ValueError; a missing export raises FileNotFoundError. The distributed manual contains complete English and French editions.

open_help has the same parameters, opens that URL through the operating system, and returns the URL. It does not start the application server or alter the library. A browser launch failure raises OSError.

The application’s authenticated POST /api/help/open calls this helper. F1 uses the current screen’s page. Legacy /help links pass through a small authenticated launcher preserving their old chapter hash.
"""
"""
@doc help-integration
@locale fr
@title Intégration de l’aide en Python
@section Intégration
@symbol help_url
## Ouvrir la documentation locale {#open-local}

L’hôte Python ouvre le lecteur CyDoc exporté avec une URL de fichier. Aucun lecteur HTTP n’est nécessaire.

```python
from skills.documentation import open_help, help_url

# Ouvre le chapitre même sans serveur applicatif.
open_help('fr', 'backup', 'restore')

# Adresse stable d’un média dans la même fenêtre de lecture.
url = help_url('fr', 'skills', media='skills-illustration')
```

## Fonctions publiques {#contracts}

| Fonction | Retour | Comportement |
| --- | --- | --- |
| `help_root()` | `pathlib.Path` | Le dossier `Documentation` à côté de l’exécutable ou à la racine du projet source. |
| `help_url(locale='en', page='welcome', anchor=None, media=None)` | `str` | Une URL `file://` encodée vers `Documentation.html`. |
| `open_help(locale='en', page='welcome', anchor=None, media=None)` | `str` | Ouvrir l’URL validée dans le navigateur système, puis la retourner. |

`locale` vaut `en` ou `fr` ; `page` est un identifiant stable de chapitre ou un alias. Les paramètres facultatifs `anchor` et `media` sont les identifiants explicites d’une section et d’une image de la page. Ces fonctions appartiennent au module `skills.documentation`. L’hôte importe `pathlib`, `urllib.parse` et `webbrowser` ; aucune API JavaScript de navigateur n’est requise.

help_url(locale='en', page='welcome', anchor=None, media=None) valide page, section et média contre le manifeste exporté, résout les alias et retourne une URL de fichier locale. Une cible inconnue lève ValueError ; un export absent lève FileNotFoundError. Le manuel distribué contient des éditions anglaise et française complètes.

open_help accepte les mêmes paramètres, ouvre l’URL via le système puis la retourne. Il ne démarre pas le serveur applicatif et ne modifie pas la bibliothèque. Un échec d’ouverture du navigateur lève OSError.

Le POST authentifié /api/help/open utilise cet utilitaire. F1 cible le chapitre de l’écran courant. Les anciens liens /help passent par un petit lanceur authentifié qui préserve leur ancien fragment de chapitre.
"""


def help_root():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent / 'Documentation'
    return Path(__file__).resolve().parent.parent / 'Documentation'


def help_url(locale='en', page='welcome', anchor=None, media=None):
    root = help_root()
    index = root / 'Documentation.html'
    if not index.is_file():
        raise FileNotFoundError('Local documentation is missing. Build it with npm --prefix .CyDocBuild run build or repair the installation.')
    manifest = json.loads((root / 'DocData' / 'manifest.json').read_text(encoding='utf-8'))
    locales = {value['code'] for value in manifest['locales']}
    if locale not in locales:
        raise ValueError('Unsupported documentation language')
    aliases = manifest.get('aliases', {})
    visited = set()
    alias_anchor = None
    while page in aliases:
        if page in visited:
            raise ValueError('Invalid documentation alias')
        visited.add(page)
        page, _, aliased_anchor = aliases[page].partition('#')
        alias_anchor = aliased_anchor or alias_anchor
        anchor = anchor or aliased_anchor or None
    target = next((p for p in manifest['pages'] if p['id'] == page and p['locale'] == locale), None)
    target = target or next((p for p in manifest['pages'] if p['id'] == page and p['locale'] == manifest['defaultLocale']), None)
    if not target:
        raise ValueError('Unknown documentation page')
    anchors = {h['id'] for h in target.get('headings', [])} | set(target.get('anchors', []))
    if anchor and anchor not in anchors:
        if alias_anchor in anchors:
            anchor = alias_anchor
        else:
            raise ValueError('Unknown documentation section')
    if media and media not in re.findall(r'data-cydoc-id="([^"]+)"', target['html']):
        raise ValueError('Unknown documentation media')
    route = '#/' + quote(locale, safe='') + '/' + quote(page, safe='')
    if anchor:
        route += '/' + quote(anchor, safe='')
    if media:
        route += '?' + urlencode({'media': media})
    return index.resolve().as_uri() + route


def open_help(locale='en', page='welcome', anchor=None, media=None):
    url = help_url(locale, page, anchor, media)
    if not webbrowser.open(url, new=2):
        raise OSError('The system browser could not open local documentation.')
    return url


def legacy_help_page(lang='en'):
    french = lang == 'fr'
    title = 'Ouvrir la documentation locale' if french else 'Open local documentation'
    text = 'Le manuel utilise maintenant CyDoc. Ouvrez-le depuis l’icône Windows ou le bouton ci-dessous.' if french else 'The manual now uses CyDoc. Open it from the Windows tray or the button below.'
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CyAICodex — Documentation</title><link rel="stylesheet" href="/static/style.css"><script src="/static/help.js" defer></script></head><body class="help-launcher"><main><h1>{title}</h1><p>{text}</p><button class="primary" data-open-help="legacy">{title}</button><p id="help-launch-status" role="status"></p></main></body></html>'''


def main():
    parser = argparse.ArgumentParser(description='Open the local CyDoc manual without starting the server.')
    parser.add_argument('--open-help', action='store_true')
    parser.add_argument('--help-language', choices=['en', 'fr'], default='en')
    parser.add_argument('--help-page', default='welcome')
    parser.add_argument('--help-section')
    parser.add_argument('--help-media')
    parser.add_argument('--print-help-url', action='store_true')
    args = parser.parse_args()
    if args.print_help_url:
        print(help_url(args.help_language, args.help_page, args.help_section, args.help_media))
    else:
        open_help(args.help_language, args.help_page, args.help_section, args.help_media)
