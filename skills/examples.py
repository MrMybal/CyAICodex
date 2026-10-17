"""Public bilingual starter skills; never replace a user's adaptations."""
from pathlib import Path
from .store import Method


def seed_examples(store):
    templates = {lang: Method.model_validate_json(
        (Path(__file__).with_name('examples') / f'github-privacy.{lang}.json').read_text(encoding='utf-8'))
        for lang in ('en', 'fr')}
    # Versions before 0.7 seeded one language. Identify it from the original
    # revision, even if the current title/content was edited or archived.
    legacy_id = store.setting('example_github_privacy_v1')
    if legacy_id:
        history = store.history(legacy_id)
        original = history[-1]['snapshot'] if history else {}
        for lang, template in templates.items():
            if original.get('summary') == template.summary:
                with store.db() as db:
                    db.execute('INSERT OR IGNORE INTO settings VALUES (?, ?)',
                               (f'example_github_privacy_{lang}_v1', legacy_id))
                break
        else:
            # Unknown legacy provenance: preserve it without guessing its language.
            return []
    added = []
    for lang, template in templates.items():
        result = store.save(template, author='CyAICodex',
                            once_key=f'example_github_privacy_{lang}_v1')
        if result is not None:
            added.append(result)
    return added
