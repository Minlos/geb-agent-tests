#!/usr/bin/env python3
"""Export exact six-exchange model conversations and measured response lengths."""
import hashlib,json,re
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'runs/natural-chat-frontier-20261128/state.json'
if not source.exists():source=ROOT/'results/natural-chat-frontier-20261128/raw.json'
s=json.loads(source.read_text())
out=ROOT/'results/natural-chat-frontier-20261128';out.mkdir(exist_ok=True)
archived=list((ROOT/'configurations/natural-chat-frontier').glob('*.py'))
hashes={hashlib.sha256(p.read_bytes()).hexdigest() for p in archived}
summary={}
for a in ['deepseek','glm']:
 c=s['conversations'][a]
 assert c['status']=='ready' and len(c['responses'])==6
 assert [m['role'] for m in c['messages']]==['system']+['user','assistant']*6
 assert [m['content'] for m in c['messages'] if m['role']=='assistant']==[r['message']['content'] for r in c['responses']]
 assert all(r['driver_sha256'] in hashes for r in c['responses'])
 lengths=[len(re.findall(r'[^\W_]+(?:[-’\'][^\W_]+)*',r['message']['content'])) for r in c['responses']]
 summary[a]={'responses':6,'words_per_answer':lengths,'max_words':max(lengths),'mean_words':sum(lengths)/6,'cost_usd':str(sum(Decimal(str(r['usage']['cost'])) for r in c['responses'])),'reasoning_tokens':sum(r['usage'].get('completion_tokens_details',{}).get('reasoning_tokens',0) for r in c['responses'])}
 page=['# Александр — '+s['models'][a]['id'],'','[Условия и разбор](comparison-ru.md)','']
 for i in range(6):
  for msg in c['messages'][1+2*i:3+2*i]:page+=['## '+str(i+1)+'. '+('Александр' if msg['role']=='user' else 'Модель'),'',msg['content'],'']
 (out/(a+'-dialogue.md')).write_text('\n'.join(page))
(out/'raw.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(out/'assistant-prompt.txt').write_text(s['assistant_prompt'])
(out/'persona.json').write_text(json.dumps(s['persona'],ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
