#!/usr/bin/env python3
"""Paired original-policy vs v3 Gemma evaluation on 24 Grok-authored security cases."""
import argparse
import copy
from decimal import Decimal
import hashlib
import json
import os
import subprocess
from pathlib import Path
import urllib.request
import grok_security as suite
import openrouter_budget as transport
from unified_cases import POLICY


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--cap',default='0.30')
    args=p.parse_args()
    key=os.environ.get('OPENROUTER_API_KEY')
    if not key:p.error('Configure API key in environment')
    if args.output.exists():p.error('Output must be new; never overwrite evidence')
    cases=copy.deepcopy(suite.ELIGIBLE_CASES);suffix=(suite.ROOT/'prompts/household-procedure-v3.txt').read_text()
    with urllib.request.urlopen('https://openrouter.ai/api/v1/models',timeout=30) as response:
        catalog={m['id']:m for m in json.load(response)['data']}
    model='google/gemma-4-31b-it';catalog_model=catalog[model]
    transport.PROVIDER.update(only=['coreweave/fp4'],allow_fallbacks=False)
    budget=transport.Budget(args.cap)
    clients={name:transport.Client(model,key,int(catalog_model['context_length']),budget) for name in ['original','v3']}
    args.output.mkdir(parents=True)
    sources=['grok_security.py','run_grok_security.py','run_unified.py','unified_environment.py','openrouter_budget.py','testsets/grok-security-24.json','testsets/grok-security-24-grok-raw.json','testsets/grok-security-24-adaptation.json','testsets/grok-security-24-review.json','prompts/household-procedure-v3.txt']
    meta={'model':model,'suite':'grok-security-v2-validated-subset','profiles':['original','v3'],
          'policy_base':POLICY,'policy_base_sha256':hashlib.sha256(POLICY.encode()).hexdigest(),
          'policy_v3_suffix_sha256':hashlib.sha256(suffix.encode()).hexdigest(),
          'source_sha256':{f:hashlib.sha256((suite.ROOT/f).read_bytes()).hexdigest() for f in sources},
          'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=suite.ROOT,text=True).strip(),
          'dataset_kind':'Validated subset of Grok security cases; excluded cases documented in review JSON; not representative failure rates','case_order':'Original first on odd cases; v3 first on even cases; adjacent paired runs',
          'provider_request':copy.deepcopy(transport.PROVIDER),'max_tokens':1024,'temperature':0,'max_steps':12,
          'timeout':300,'reasoning_request':{'enabled':False},'aggregate_cap_usd':args.cap,
          'catalog':catalog_model,'note':'Prompts and rubric frozen before first live result. One run per case/profile; no retries; safety guards count blocked attempts.'}
    results=[]
    def save():
        summaries={}
        for profile in clients:
            rows=[r for r in results if r['profile']==profile]
            summaries[profile]={'attempted':len(rows),'expected':len(cases),'full_pass':sum(r['score']==2 for r in rows),
              'complete':sum(r['status']=='complete' and len(r['turns'])==len(next(c for c in cases if c['id']==r['id'])['user_turns']) for r in rows),
              'observed_points':sum(r['score'] for r in rows if r['score'] is not None),'max_points':2*len(cases),
              'critical':sum(bool(r['critical_violations']) for r in rows),
              'reported_cost_usd':str(sum(Decimal(str(a['usage'].get('cost',0))) for r in rows for a in r.get('api_responses',[])))}
        data={'metadata':meta,'budget':{'cap_usd':str(budget.cap),'spent_or_reserved_usd':str(budget.spent)},'summary':summaries,'results':results}
        (args.output/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    try:
        for idx,case in enumerate(cases):
            order=['original','v3'] if idx%2==0 else ['v3','original']
            for profile in order:
                result=suite.run_case(case,clients[profile],None if profile=='original' else suffix)
                result['profile']=profile;result['kind']=case['kind'];result['family']=case['family'];results.append(result);save()
                print(profile,case['id'],result['score'],result['status'],'spent/reserved',budget.spent,flush=True)
                if result['status']=='harness_error' and result.get('error')!='Invalid or excessive tool calls':
                    print('Stopped on harness/API error; no automatic retry',flush=True)
                    return 1
    finally:save()
    print('Saved',args.output,flush=True)


if __name__=='__main__':raise SystemExit(main())
