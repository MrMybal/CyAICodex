from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import pytest
from skills.examples import seed_examples
from skills.store import Store, Method


def test_starter_skills_are_bilingual_and_preserve_personal_content(tmp_path):
    store = Store(tmp_path)
    personal = store.save(Method(title='Personal skill', content='Private content'))
    added = seed_examples(store)
    assert len(added) == 2
    assert {x['category'] for x in added} == {'Privacy', 'Confidentialité'}
    assert all(x['scope'] == 'global' and x['status'] == 'published' for x in added)
    assert store.get(personal['id']) == personal
    assert all('Gitleaks' in x['content'] and 'MCP' in x['content'] for x in added)
    assert seed_examples(store) == []


def test_concurrent_seeding_does_not_duplicate_or_overwrite_edits(tmp_path):
    store = Store(tmp_path)
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(lambda _: seed_examples(store), range(3)))
    added = [item for batch in results for item in batch]
    assert len(added) == 2
    example = added[0]
    edited = store.save(Method(title='My adaptation', content='Keep my changes', status='archived'), example['id'], example['version'])
    assert seed_examples(store) == []
    assert store.get(edited['id']) == edited
    assert store.search(status='')['total'] == 2


@pytest.mark.parametrize('language', ['en', 'fr'])
def test_existing_example_is_preserved_and_only_missing_translation_added(tmp_path, language):
    store = Store(tmp_path)
    template = Method.model_validate_json((Path('skills/examples') / f'github-privacy.{language}.json').read_text(encoding='utf-8'))
    original = store.save(template, author='CyAICodex', once_key='example_github_privacy_v1')
    edited = store.save(Method(title='My adaptation', content='Keep my changes', status='archived'), original['id'], original['version'])
    store.set_setting('ui_language', 'fr' if language == 'en' else 'en')
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(lambda _: seed_examples(store), range(3)))
    assert sum(len(batch) for batch in results) == 1
    assert store.search(status='')['total'] == 2
    assert store.get(edited['id']) == edited
    assert seed_examples(store) == []


def test_existing_database_filename_is_preserved(tmp_path):
    store = Store(tmp_path)
    assert store.path.name == 'skills.sqlite3'
    personal = store.save(Method(title='Existing skill', content='Keep me'))
    store.path.rename(tmp_path / 'methodes.sqlite3')
    reopened = Store(tmp_path)
    assert reopened.path.name == 'methodes.sqlite3'
    assert reopened.get(personal['id']) == personal
    assert not (tmp_path / 'skills.sqlite3').exists()
