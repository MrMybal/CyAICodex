"""Portable package integrity and isolated client installation behavior."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import zipfile

import pytest

from tools.package_agent_skill import FILES, SOURCE, package_skill

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / 'integrations/skills/Install-Skill.ps1'
POWERSHELL = shutil.which('pwsh') or shutil.which('powershell')


def test_package_is_reproducible_and_contains_only_portable_files(tmp_path):
    first = package_skill(tmp_path / 'one')
    second = package_skill(tmp_path / 'two')
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert set(archive.namelist()) == {'cyaicodex/' + name for name in FILES}
        assert archive.testzip() is None
        for name in FILES:
            assert archive.read('cyaicodex/' + name).decode('utf-8') == (SOURCE / name).read_text(encoding='utf-8')
        assert archive.read('cyaicodex/LICENSE.txt') == (ROOT / 'LICENSE').read_text(encoding='utf-8').encode()
    assert (first.parent / 'SKILL.md').read_text(encoding='utf-8') == (SOURCE / 'SKILL.md').read_text(encoding='utf-8')
    assert (first.parent / 'SHA256SUMS.txt').read_text().split()[0] == hashlib.sha256(first.read_bytes()).hexdigest()


def install(profile, *args):
    if not POWERSHELL:
        pytest.skip('PowerShell is not installed')
    return subprocess.run([POWERSHELL, '-NoProfile', '-NonInteractive', '-File', str(INSTALLER), '-RootPath', str(profile), *args], text=True, capture_output=True, timeout=30)


def test_installer_dry_run_install_and_idempotence(tmp_path):
    profile = tmp_path / 'Profile with spaces'
    result = install(profile, '-WhatIf')
    assert result.returncode == 0, result.stderr
    assert not profile.exists()
    result = install(profile)
    assert result.returncode == 0, result.stderr
    destinations = [profile / sub / 'skills/cyaicodex' for sub in ('.agents', '.claude')]
    for destination in destinations:
        assert {p.name for p in destination.iterdir()} == set(FILES)
        for name in FILES:
            assert (destination / name).read_bytes() == (SOURCE / name).read_bytes()
    snapshots = {p: p.stat().st_mtime_ns for d in destinations for p in d.iterdir()}
    assert install(profile).returncode == 0
    assert all(p.stat().st_mtime_ns == timestamp for p, timestamp in snapshots.items())
    assert not list(profile.rglob('*.toml')) and not list(profile.rglob('*.json'))


def test_installer_preflights_all_clients_and_preserves_customizations(tmp_path):
    profile = tmp_path / 'isolated-profile'
    claude = profile / '.claude/skills/cyaicodex'
    claude.mkdir(parents=True)
    original = b'User customization\n'
    (claude / 'SKILL.md').write_bytes(original)
    (claude / 'notes.txt').write_text('Keep this unrelated file.', encoding='utf-8')
    result = install(profile)
    assert result.returncode != 0
    assert not (profile / '.agents').exists()
    assert (claude / 'SKILL.md').read_bytes() == original
    result = install(profile, '-Update')
    assert result.returncode == 0, result.stderr
    assert (claude / 'SKILL.md.previous').read_bytes() == original
    assert (claude / 'SKILL.md').read_bytes() == (SOURCE / 'SKILL.md').read_bytes()
    assert (claude / 'notes.txt').read_text() == 'Keep this unrelated file.'
    assert install(profile, '-Update').returncode == 0
    assert (claude / 'SKILL.md.previous').read_bytes() == original


@pytest.mark.parametrize('client,folder', [('codex', '.agents'), ('claude-code', '.claude')])
def test_installer_project_scope_selects_only_requested_client(tmp_path, client, folder):
    project = tmp_path / 'sample-project'
    result = install(project, '-Scope', 'Project', '-Client', client)
    assert result.returncode == 0, result.stderr
    assert {p.name for p in project.iterdir()} == {folder}
    assert (project / folder / 'skills/cyaicodex/SKILL.md').is_file()


def test_installer_does_not_copy_into_an_unrelated_backup_directory(tmp_path):
    profile = tmp_path / 'profile'
    destination = profile / '.agents/skills/cyaicodex'
    backup = destination / 'SKILL.md.previous'
    backup.mkdir(parents=True)
    (destination / 'SKILL.md').write_text('Keep customized skill.', encoding='utf-8')
    result = install(profile, '-Client', 'codex', '-Update')
    assert result.returncode != 0
    assert (destination / 'SKILL.md').read_text() == 'Keep customized skill.'
    assert list(backup.iterdir()) == []
