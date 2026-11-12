"""Build a portable Agent Skill ZIP using only reviewed, explicit files."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'integrations' / 'skills' / 'cyaicodex'
FILES = ('SKILL.md', 'LICENSE.txt')


def package_skill(output: Path) -> Path:
    contents = {}
    for name in FILES:
        path = SOURCE / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Missing or linked packaged file: {name}')
        contents[name] = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n').encode('utf-8')
    skill = contents['SKILL.md'].decode('utf-8')
    if not skill.startswith('---\nname: cyaicodex\n') or '\ndescription: ' not in skill:
        raise ValueError('Invalid CyAICodex Skill manifest')
    if not contents['LICENSE.txt'].startswith(b'                    GNU AFFERO GENERAL PUBLIC LICENSE'):
        raise ValueError('Missing AGPL license')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / 'CyAICodex-Skill.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in contents.items():
            entry = zipfile.ZipInfo('cyaicodex/' + name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            bundle.writestr(entry, data)
    (output / 'SKILL.md').write_bytes(contents['SKILL.md'])
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / 'SHA256SUMS.txt').write_text(f'{checksum}  {archive.name}\n', encoding='utf-8', newline='\n')
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist' / 'agent-skills')
    args = parser.parse_args()
    result = package_skill(args.output)
    print(f'Agent Skill package: {result}')
