"""UI translations only: never translate stored methods or image metadata."""
import html
import json
import re
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path

WEB = Path(__file__).parent / 'web'


@lru_cache
def catalog():
    return {key.replace('\\n', '\n'): value.replace('\\n', '\n')
            for key, value in (line.split('\t', 1) for line in (WEB / 'translations.tsv').read_text(encoding='utf-8').splitlines() if line)}


def language(store):
    return 'en' if store.setting('ui_language', 'fr') == 'en' else 'fr'


def translate(text, lang):
    if lang != 'en':
        return text
    key = text.strip()
    if key in catalog():
        start = len(text) - len(text.lstrip())
        return text[:start] + catalog()[key] + text[start + len(key):]
    # Match only known message templates; captured names and paths are preserved.
    for source, target in catalog().items():
        names = re.findall(r'\{(\w+)\}', source)
        if not names:
            continue
        pattern = re.escape(source)
        for name in names:
            pattern = pattern.replace(re.escape('{' + name + '}'), f'(?P<{name}>.*?)')
        match = re.fullmatch(pattern, text, re.DOTALL)
        if match:
            return target.format(**match.groupdict())
    return text


def translated_status(result, lang):
    return {key: translate(value, lang) if key in ('message', 'restart') and isinstance(value, str) else value
            for key, value in result.items()}


class TranslatedHTML(HTMLParser):
    def __init__(self, lang):
        super().__init__(convert_charrefs=True)
        self.lang, self.parts = lang, []

    def handle_decl(self, decl):
        self.parts.append('<!' + decl + '>')

    def handle_starttag(self, tag, attrs):
        converted = []
        for key, value in attrs:
            if tag == 'html' and key == 'lang':
                value = self.lang
            elif key in ('placeholder', 'aria-label', 'alt', 'title'):
                value = translate(value, self.lang)
            converted.append(key if value is None else f'{key}="{html.escape(value, quote=True)}"')
        self.parts.append('<' + tag + (' ' + ' '.join(converted) if converted else '') + '>')

    def handle_endtag(self, tag):
        self.parts.append('</' + tag + '>')

    def handle_data(self, data):
        self.parts.append(html.escape(translate(data, self.lang), quote=False))

    def handle_comment(self, data):
        self.parts.append('<!--' + data + '-->')


def render_index(lang):
    parser = TranslatedHTML(lang)
    parser.feed((WEB / 'index.html').read_text(encoding='utf-8'))
    return ''.join(parser.parts)


def browser_catalog():
    return 'const UI_TRANSLATIONS = ' + json.dumps(catalog(), ensure_ascii=False) + ';'
