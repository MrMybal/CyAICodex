"""Bundled, read-only user documentation; independent of the personal library."""
import json
from functools import lru_cache
from pathlib import Path
from . import __version__

ROOT = Path(__file__).parent / 'web' / 'manual'


@lru_cache(maxsize=2)
def _content(lang):
    if lang not in ('en', 'fr'):
        raise ValueError('Unsupported documentation language')
    return json.loads((ROOT / f'{lang}.json').read_text(encoding='utf-8'))


def manual_content(lang='en'):
    return {**_content(lang), 'version': __version__}


def manual_page(lang='en'):
    if lang not in ('en', 'fr'):
        raise ValueError('Unsupported documentation language')
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>CyAICodex — Documentation</title>
<link rel="icon" href="/static/logo-cy-book-transparent.ico">
<link rel="stylesheet" href="/static/documentation.css">
<script src="/static/documentation.js" defer></script></head>
<body class="manual-standalone"><main id="documentation-root" class="documentation" data-standalone="true" aria-label="Documentation">
<noscript>{'Activez JavaScript pour parcourir le manuel.' if lang == 'fr' else 'Enable JavaScript to browse the manual.'}</noscript>
</main></body></html>'''
