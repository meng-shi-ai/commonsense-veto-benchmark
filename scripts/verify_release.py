"""Offline public-byte, parse and local Markdown-link checks. Executes no runners."""
from pathlib import Path
import ast
import hashlib
import json
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

def main():
    manifest = json.loads((ROOT / 'PUBLIC_MANIFEST.json').read_text())
    paths = {item['path'] for item in manifest['files']}
    for item in manifest['files']:
        p = ROOT / item['path']
        assert p.is_file(), item['path']
        data = p.read_bytes()
        assert len(data) == item['bytes'], item['path']
        assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    counts = {'files_verified': len(paths), 'python': 0, 'json': 0, 'jsonl': 0, 'local_links': 0}
    for name in sorted(paths):
        p = ROOT / name
        s = p.read_text(encoding='utf-8')
        if p.suffix == '.py':
            ast.parse(s, filename=name)
            counts['python'] += 1
        elif p.suffix == '.json':
            json.loads(s)
            counts['json'] += 1
        elif p.suffix == '.jsonl':
            for line in s.splitlines():
                if line.strip():
                    json.loads(line)
            counts['jsonl'] += 1
        elif p.suffix == '.md':
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', s):
                target = target.strip('<>').split('#')[0]
                if not target or re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                    continue
                assert not target.startswith('/'), (name, target)
                assert (p.parent / unquote(target)).exists(), (name, target)
                counts['local_links'] += 1
    print(json.dumps({'status': 'passed', **counts}, indent=2))

if __name__ == '__main__':
    main()
