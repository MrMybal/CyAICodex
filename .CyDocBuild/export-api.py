"""Export declarations only; never import the server or inspect user libraries."""
import ast
import json
from pathlib import Path
import sys

work = Path(__file__).resolve().parent
root = work.parent
prose = json.loads((work / 'api-prose.json').read_text(encoding='utf-8'))
tree = ast.parse((root / 'skills/server.py').read_text(encoding='utf-8'))
nodes = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
for locale in ('en', 'fr'):
    lang = int(locale == 'fr')
    symbols = []
    for name, entry in prose['tools'].items():
        node = nodes[name]
        if not any(isinstance(d, ast.Call) and ast.unparse(d.func) == 'mcp.tool' for d in node.decorator_list):
            raise ValueError('Not a public MCP tool: ' + name)
        parameters = []
        defaults = [None] * (len(node.args.args) - len(node.args.defaults)) + node.args.defaults
        for arg, default in zip(node.args.args, defaults):
            parameters.append({'name': arg.arg, 'type': ast.unparse(arg.annotation),
                'default': ast.unparse(default) if default is not None else '',
                'description': prose['parameters'][arg.arg][lang]})
        symbols.append({'key': name, 'name': name, 'kind': 'function', 'language': 'python',
            'signature': name + '(' + ast.unparse(node.args) + ') -> ' + ast.unparse(node.returns),
            'parameters': parameters, 'returnType': ast.unparse(node.returns),
            'description': entry['description'][lang], 'returns': entry['returns'][lang],
            'references': [{'key': ref, 'name': ref} for ref in entry['refs']]})
    target = work / '.generated' / ('api-' + locale + '.json')
    target.write_text(json.dumps({'symbols': symbols}, ensure_ascii=False, indent=2), encoding='utf-8')

# This pure helper contains only public, static setup text and the application version.
sys.path.insert(0, str(root))
from skills.onboarding import setup_guide
(work / '.generated' / 'app-ai.md').write_text(
    '# CyAICodex assistant guidance\n\n' + setup_guide(language='en')['markdown'] +
    '\n---\n\n' + setup_guide(language='fr')['markdown'], encoding='utf-8')
