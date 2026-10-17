from concurrent.futures import ThreadPoolExecutor

import pytest

from skills.store import Store, Method, Conflict


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path)


def m(title="Vérification de confidentialité", **kwargs):
    return Method(title=title, content="Étapes pour publier une démo sur GitHub.", **kwargs)


def test_search_accents_prefix_and_ranking(store):
    title = store.save(m())
    store.save(Method(title="Autre", content="Vérification de confidentialité"))
    assert store.search("confident")['items'][0]['id'] == title['id']
    assert store.search("verification confidentialite")['total'] == 2
    assert store.search('" OR * - ()')['total'] == 0
    assert 'content' not in store.search()['items'][0]


def test_project_type_and_global_isolation(store):
    kind = store.add_group("types", "Web")
    a = store.add_group("projects", "A", kind['id'])
    b = store.add_group("projects", "B", kind['id'])
    global_m = store.save(m())
    typed = store.save(m(scope="type", scope_id=kind['id']))
    specific = store.save(m(scope="project", scope_id=a['id']))
    secret = store.save(m(scope="project", scope_id=b['id']))
    store.save(m(status="draft"))
    ctx = store.context(project_id=a['id'])
    assert {x['id'] for x in store.search(context=ctx)['items']} == {global_m['id'], typed['id'], specific['id']}
    with pytest.raises(KeyError):
        store.get(secret['id'], ctx)
    with pytest.raises(ValueError):
        store.save(m(scope="project", scope_id=b['id']), context=ctx)
    assert len(store.search(context=store.context(project_id=a['id'], include_global=False))['items']) == 2
    assert store.search(context=store.context(include_global=False))['total'] == 0


def test_update_is_atomic_and_records_history(store):
    first = store.save(m())
    def update(title):
        try:
            return store.save(m(title), first['id'], 1)
        except Conflict:
            return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(update, ['One', 'Two']))
    assert sum(r is not None for r in results) == 1
    assert store.get(first['id'])['version'] == 2
    assert len(store.history(first['id'])) == 2
    assert store.history(first['id'])[-1]['snapshot']['title'] == first['title']


def test_tokens_are_hashed_and_revocable(store):
    c = store.new_connection("Test")
    assert store.authenticate(c['token'])['writable'] == 0
    with store.db() as db:
        assert db.execute('SELECT token_hash FROM connections').fetchone()[0] != c['token']
    assert store.authenticate('bogus') is None
    store.revoke(c['id'])
    assert store.authenticate(c['token']) is None


def test_export_excludes_secrets(store):
    store.new_connection('secret')
    store.set_setting('openai_key', 'encrypted-secret')
    store.save(m())
    data = store.export()
    assert set(data) == {'format', 'methods', 'types', 'projects'}
    assert len(data['methods']) == 1


def test_invalid_scope_and_blank_methods(store):
    with pytest.raises(ValueError):
        store.save(m(scope='project', scope_id='missing'))
    with pytest.raises(ValueError):
        m(title='   ')
