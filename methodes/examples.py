"""Public starter content, independent of every user's private library."""
from pathlib import Path

from .i18n import language
from .store import Method


def seed_examples(store):
    locale = language(store)
    path = Path(__file__).with_name('examples') / f'github-privacy.{locale}.json'
    if not path.is_file():
        path = path.with_name('github-privacy.fr.json')
    method = Method.model_validate_json(path.read_text(encoding='utf-8'))
    return store.save(method, author='CyAICodex', once_key='example_github_privacy_v1')
