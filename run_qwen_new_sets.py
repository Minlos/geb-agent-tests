#!/usr/bin/env python3
"""Frozen Qwen original/v3 evaluation on existing Grok12, validated Security23 and Advanced32."""
import argparse
import copy
import datetime as dt
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request
import advanced_suite
import grok_holdout
import grok_security
import openrouter_budget as transport
from run_tests import APIError
from unified_cases import POLICY
ROOT=Path(__file__).resolve().parent
MODEL='qwen/qwen3.8-27b'
PRICE={'prompt':'0.035','completion':'1.5'}
PROVIDER={'only':['darkbloom/fp4'],'allow_fallbacks':False,'require_parameters':True,
          'max_price':{'prompt':0.035,'completion':1.5,'request':0}}

class Budget(transport.Budget):
    def reserve(self,context,max_tokens):
        if type(context)is not int or type(max_tokens)is not int or min(context,max_tokens)<1:raise ValueError('Positive limits required')
        amount=(Decimal(context)*Decimal(PRICE['prompt'])+Decimal(max_tokens)*Decimal(PRICE['completion']))/1000000
        if self.spent+amount>self.cap:raise APIError('Aggregate budget guard stopped before request')
        self.spent+=amount;return amount

def datasets():
    return [('grok12',grok_holdout,grok_holdout.load_cases()),
            ('security23',grok_security,copy.deepcopy(grok_security.ELIGIBLE_CASES)),
            ('advanced32',advanced_suite,copy.deepcopy(advanced_suite.CASES))]

def normalize_record(r,case):
    r['conversation_complete']=r['status']=='complete' and len(r['turns'])==len(case['user_turns']) and all(t.get('finished') for t in r['turns'])
    infra=r['status']=='harness_error' and r.get('error')!='Invalid or excessive tool calls'
    if infra and not r.get('critical_violations'):r.update(score=None,full_pass=False)
    if not r['conversation_complete'] and r.get('score')==2:r.update(score=1,full_pass=False)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--cap',default='0.50')
    args=p.parse_args(argv)
    if args.output.exists():p.error('Output must be new')
    key=os.environ.get('OPENROUTER_API_KEY')
    if not key:p.error('Configure OPENROUTER_API_KEY in environment')
    with urllib.request.urlopen('https://openrouter.ai/api/v1/models/qwen/qwen3.8-27b/endpoints',timeout=30) as response:catalog=json.load(response)
    endpoint=next(e for e in catalog['data']['endpoints'] if e['tag']=='darkbloom/fp4')
    if any(Decimal(endpoint['pricing'][k])*1000000>Decimal(PRICE[k]) for k in PRICE):p.error('Endpoint exceeds fixed price ceilings')
    if not {'tools','reasoning'}<=set(endpoint['supported_parameters']):p.error('Endpoint lacks tools/reasoning controls')
    transport.PROVIDER.clear();transport.PROVIDER.update(copy.deepcopy(PROVIDER))
    budget=Budget(args.cap);profiles=['original','v3'];suffix=(ROOT/'prompts/household-procedure-v3.txt').read_text()
    sources=['run_qwen_new_sets.py','grok_holdout.py','grok_security.py','advanced_suite.py','advanced_environment.py','run_unified.py','unified_environment.py','unified_cases.py','run_tests.py','openrouter_budget.py','testsets/grok-independent-12.json','testsets/grok-security-24.json','testsets/grok-security-24-review.json','testsets/advanced-32.json','prompts/household-procedure-v3.txt']
    groups=datasets()
    metadata={'model':MODEL,'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'profiles':profiles,
              'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'source_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sources},
              'policy_base_sha256':hashlib.sha256(POLICY.encode()).hexdigest(),'policy_v3_suffix_sha256':hashlib.sha256(suffix.encode()).hexdigest(),
              'provider_request':PROVIDER,'endpoint_catalog':endpoint,'max_tokens':1024,'max_steps':12,'temperature':0,'timeout':300,
              'reasoning_request':{'enabled':False},'reservation_prices_per_million':PRICE,
              'selected_ids':{name:[c['id'] for c in cases] for name,module,cases in groups},
              'comparison':'No winner chosen. Compare within each suite and safety mechanism; model/provider effects not separable.',
              'method':'Original/v3 adjacent, reverse order on alternating cases; no retries; all attempts retained. Existing cases are public regressions, not fresh unseen holdouts.'}
    clients={name:transport.Client(MODEL,key,int(endpoint['context_length']),budget) for name in profiles}
    args.output.mkdir(parents=True);results=[]
    def save():
        summary={}
        for name,module,cases in groups:
            summary[name]={}
            for profile in profiles:
                rows=[r for r in results if r['dataset']==name and r['profile']==profile]
                complete=len(rows)==len(cases) and all(r['conversation_complete'] and r.get('score') is not None for r in rows)
                summary[name][profile]={'attempted':len(rows),'expected':len(cases),'complete_conversations':sum(r['conversation_complete'] for r in rows),
                    'full_pass':sum(r.get('score')==2 for r in rows),'critical_cases':sum(bool(r.get('critical_violations')) for r in rows),
                    'observed_points':sum(r['score'] for r in rows if r.get('score') is not None),'full_suite_points':sum(r['score'] for r in rows) if complete else None,'max_points':2*len(cases)}
        data={'metadata':metadata,'summary':summary,'budget':{'cap_usd':str(budget.cap),'spent_or_reserved_usd':str(budget.spent)},'results':results}
        (args.output/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    try:
        for name,module,cases in groups:
            for i,case in enumerate(cases):
                for profile in (profiles if i%2==0 else list(reversed(profiles))):
                    r=module.run_case(case,clients[profile],None if profile=='original' else suffix)
                    r.update(dataset=name,profile=profile,kind=case.get('kind'),family=case.get('family'))
                    normalize_record(r,case);results.append(r);save()
                    print(name,profile,case['id'],r.get('score'),r['status'],'critical='+str(len(r.get('critical_violations',[]))),'spent/reserved='+str(budget.spent),flush=True)
                    if r.get('error','').startswith('Aggregate budget guard'):return 1
    finally:save()
    return 0
if __name__=='__main__':raise SystemExit(main())
