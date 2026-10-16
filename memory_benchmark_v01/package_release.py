"""Build a self-contained delivery archive and fixture validation records; no provider calls."""
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path
import benchmark as b

root=Path(__file__).resolve().parent
validation=root/'validation'
validation.mkdir(exist_ok=True)
cases,gold=b.inputs()
example=b.prompt(next(c for c in cases if c['id']=='C010'))
(root/'example_prompt.txt').write_text(
    example['messages'][0]['content']+'\n\n'+example['messages'][1]['content']+'\n',encoding='utf-8')

commands=[
    [sys.executable,'-m','unittest','-v'],
    [sys.executable,'benchmark.py','validate'],
    [sys.executable,'benchmark.py','export','--out','prompts.jsonl'],
    [sys.executable,'benchmark.py','demo','--out','validation/demo_report.json'],
    [sys.executable,'benchmark.py','run','--adapter',sys.executable+' fixture_adapter.py',
     '--out','validation/fixture_predictions.jsonl'],
    [sys.executable,'benchmark.py','score','--predictions','validation/fixture_predictions.jsonl',
     '--out','validation/fixture_score.json'],
]
logs=[]
for command in commands:
    proc=subprocess.run(command,cwd=root,text=True,capture_output=True,check=True)
    logs.append('$ '+' '.join(command)+'\n'+proc.stdout+proc.stderr)
report=json.loads((validation/'fixture_score.json').read_text())
assert report['prediction_coverage']==1 and report['schema_valid_rate']==1
assert report['state_accuracy']==0.25 and report['strict_accuracy']==0
prompts=b.read_jsonl(root/'prompts.jsonl')
assert len(prompts)==24 and all(set(p)=={'id','messages'} for p in prompts)
logs.append('End-to-end fixture assertions passed. No real model was evaluated.\n')
(validation/'checks.txt').write_text('\n'.join(logs),encoding='utf-8')

files=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json']
manifest={'version':'0.1','kind':'synthetic_diagnostic_pilot','actual_models_evaluated':[],
          'source_cases':24,'pairs':12,'families':6,'software_tests':8,
          'files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
destination=root.parent/'Memory_Evidence_Benchmark_v01.zip'
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(files+[root/'manifest.json']):
        archive.write(file,arcname=str(Path(root.name)/file.relative_to(root)))
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
print(json.dumps({'archive':str(destination),'files':len(files)+1,'bytes':destination.stat().st_size,
                  'fixture_only':True,'tests_passed':8},indent=2))
