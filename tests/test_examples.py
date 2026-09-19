from concurrent.futures import ThreadPoolExecutor

from methodes.examples import seed_examples
from methodes.store import Store, Method


def test_example_is_searchable_without_changing_personal_methods(tmp_path):
    store = Store(tmp_path)
    personal = store.save(Method(title='Personal method', content='Private content'))
    result = seed_examples(store)
    assert result['scope'] == 'global' and result['status'] == 'published'
    assert store.search('github privacy')['total'] == 1
    assert store.get(personal['id']) == personal
    assert 'Gitleaks' in result['content'] and 'MCP' in result['content']


def test_concurrent_seeding_does_not_duplicate_or_overwrite_edits(tmp_path):
    store = Store(tmp_path)
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(lambda _: seed_examples(store), range(3)))
    assert sum(item is not None for item in results) == 1
    example = next(item for item in results if item)
    edited = store.save(Method(title='My adaptation', content='Keep my changes', status='archived'), example['id'], example['version'])
    assert seed_examples(store) is None
    assert store.get(edited['id']) == edited
    assert store.search(status='')['total'] == 1


def test_english_example_follows_initial_library_language(tmp_path):
    store = Store(tmp_path)
    store.set_setting('ui_language', 'en')
    result = seed_examples(store)
    assert result['title'].startswith('Example')
    assert '## Final checklist' in result['content']
    store.set_setting('ui_language', 'fr')
    assert seed_examples(store) is None
    assert store.get(result['id']) == result
