from pathlib import Path
import hashlib,json,re,subprocess
root=Path(__file__).resolve().parents[1]
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0');tracked=[p for p in tracked if p]
missing=[]
for rel in tracked:
 p=root/rel
 if p.suffix=='.md':
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' in target or target.startswith('#'):continue
   target=target.split('#')[0]
   if not (p.parent/target).exists():missing.append((rel,target))
assert not missing,missing
for rel in tracked:
 if rel.endswith('.json'):json.loads((root/rel).read_text())
for rel,sha in json.loads((root/'ml/artifact-hashes.json').read_text()).items():
 assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==sha,rel
nb=json.loads((root/'ml/comparacao_logistica_lif.ipynb').read_text());assert not [o for c in nb['cells'] for o in c.get('outputs',[]) if o.get('output_type')=='error']
metrics=json.loads((root/'ml/results/metrics.json').read_text());sets=[set(v) for v in metrics['split_ids'].values()];assert sum(map(len,sets))==len(set.union(*sets))==1200
web=json.loads((root/'evidence/wokwi-project.json').read_text());firm=root/'firmware';expanded=(firm/'sketch.ino').read_text().replace('#include "RingBuffer.h"',(firm/'RingBuffer.h').read_text().replace('#pragma once',''));assert hashlib.sha256(expanded.encode()).hexdigest()==web['web_sketch_sha256']
serial=(root/'evidence/wokwi-final-serial.txt').read_text();assert 'SIMULATED_ONLINE=0' in serial and 'SIMULATED_ONLINE=1' in serial and '"age_ms":16040' in serial
records=[json.loads(l)['payload'] for l in (root/'evidence/wokwi-final-mqtt.jsonl').read_text().splitlines()];assert any(p['age_ms']>15000 for p in records);assert any(p['bpm']==180 for p in records)
for f in ['mqtt-local.json','mqtt-public.json']:assert json.loads((root/'evidence'/f).read_text())['result']=='PASS'
print('PASS: links locais, JSONs, hashes ML, notebook sem erros, split sem sobreposição, sketch Web equivalente, Wokwi offline/MQTT e testes registrados.')
