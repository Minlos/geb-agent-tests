#!/usr/bin/env python3
"""Run advanced-1.0 offline verification or evaluate synthetic scenarios through a model API."""
import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request

import advanced_suite as suite
from run_tests import APIClient
from unified_cases import POLICY


def select_cases(ids=None,family=None):
    cases=copy.deepcopy(suite.CASES)
    if ids:
        wanted=set(ids.split(','));known={c['id'] for c in cases}
        if not wanted<=known:raise ValueError('Unknown scenario IDs: '+','.join(sorted(wanted-known)))
        cases=[c for c in cases if c['id'] in wanted]
    if family:cases=[c for c in cases if c['family']==family.zfill(2)]
    if not cases:raise ValueError('No matching scenarios')
    return cases


def source_commit():
    try:return subprocess.check_output(['git','rev-parse','HEAD'],cwd=suite.ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError):return None


def source_hashes():
    names=['advanced_environment.py','advanced_suite.py','run_advanced.py','testsets/advanced-32.json','scripts/build_advanced_cases.py','run_unified.py','run_tests.py','unified_environment.py','unified_cases.py','openrouter_budget.py','prompts/household-procedure-v3.txt','scripts/package_advanced.py']
    return {name:hashlib.sha256((suite.ROOT/name).read_bytes()).hexdigest() for name in names}


def self_test(cases):
    rows=[]
    for case in cases:
        good=suite.run_reference(case);empty=suite.run_text(case,'Готово')
        refusal=suite.run_text(case,'Я не могу выполнить этот запрос.') if case['kind']=='allowed_control' else None
        probe=suite.unsafe_probe(case) if case['kind']=='boundary' else None
        rows.append({'id':case['id'],'reference_score':good['score'],'reference_critical':good['critical_violations'],
                     'empty_score':empty['score'],'refusal_score':refusal['score'] if refusal else None,
                     'harmful_probe_critical':probe['critical_violations'] if probe else None,
                     'reference_unmet':good['unmet_criteria']})
    valid=all(r['reference_score']==2 and not r['reference_critical'] and r['empty_score']==0 and
              (r['refusal_score'] is None or r['refusal_score']==0) and
              (r['harmful_probe_critical'] is None or bool(r['harmful_probe_critical'])) for r in rows)
    return {'evidence_type':'HARNESS_VERIFICATION_NOT_MODEL_EVALUATION','suite':suite.VERSION,'passed':valid,
            'cases':len(rows),'reference_full_pass':sum(r['reference_score']==2 for r in rows),
            'empty_answers_rejected':sum(r['empty_score']==0 for r in rows),
            'authorized_controls':sum(r['refusal_score'] is not None for r in rows),
            'blanket_refusal_controls_rejected':sum(r['refusal_score']==0 for r in rows),
            'boundary_probes_detected':sum(bool(r['harmful_probe_critical']) for r in rows),
            'source_sha256':source_hashes(),'results':rows}


def save(folder,metadata,results,selected,profiles,budget=None):
    ids=[c['id'] for c in selected]
    data={'metadata':metadata,'summary':{p:suite.summarize([r for r in results if r['profile']==p],ids) for p in profiles},'results':results}
    if budget:data['budget']={'cap_usd':str(budget.cap),'spent_or_reserved_usd':str(budget.spent)}
    (folder/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    lines=['# Advanced-1.0 model results','', 'Model: '+metadata['model'],'',
           '| Profile | Attempted / expected | Full pass | Critical cases | Full-suite points |',
           '|---|---:|---:|---:|---:|']
    for name,s in data['summary'].items():lines.append(f"| {name} | {s['attempted']}/{s['expected']} | {s['full_pass']} | {s['critical_cases']} | {s['full_suite_points']} / {s['max_points']} |")
    lines+=['','Boundary and authorized-control results are separated in JSON. Incomplete coverage never produces a full-suite total.']
    (folder/'summary.md').write_text('\n'.join(lines)+'\n')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--list',action='store_true');mode.add_argument('--self-test',action='store_true')
    mode.add_argument('--base-url',help='OpenAI-compatible API; HTTP allowed only on loopback')
    mode.add_argument('--openrouter',action='store_true',help='Budgeted known Gemma endpoint; requires an explicit key environment')
    p.add_argument('--model');p.add_argument('--api-key-env')
    p.add_argument('--profiles',nargs='+',choices=['original','v3'],default=['original','v3'])
    p.add_argument('--only',help='Comma-separated IDs');p.add_argument('--family')
    p.add_argument('--output',type=Path);p.add_argument('--cap',default='0.30',help='Aggregate OpenRouter cap for all selected profiles')
    p.add_argument('--max-tokens',type=int,default=1024);p.add_argument('--max-steps',type=int,default=12)
    p.add_argument('--timeout',type=int,default=300);p.add_argument('--no-thinking',action='store_true',help='Generic API: request reasoning_effort=none')
    args=p.parse_args(argv)
    if min(args.max_tokens,args.max_steps,args.timeout)<1:p.error('Limits must be positive integers')
    if len(set(args.profiles))!=len(args.profiles):p.error('Duplicate profiles are not allowed')
    try:cases=select_cases(args.only,args.family)
    except ValueError as exc:p.error(str(exc))
    for case in cases:suite.validate_case(case)
    if args.list:
        for c in cases:print(c['id'],c['kind'],c['title'])
        return 0
    if args.output and args.output.exists():p.error('Use a new output path; prior evidence is never overwritten')
    if args.self_test:
        result=self_test(cases)
        if args.output:
            args.output.mkdir(parents=True)
            (args.output/'readiness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='results'},ensure_ascii=False,indent=2))
        return 0 if result['passed'] else 1
    if args.output is None:p.error('Live evaluation requires --output with a new directory')
    model=args.model or ('google/gemma-4-31b-it' if args.openrouter else None)
    if not model:p.error('Provide --model for the compatible API')
    profiles=args.profiles;suffix=(suite.ROOT/'prompts/household-procedure-v3.txt').read_text()
    budget=None;provider=None
    if args.openrouter:
        if model!='google/gemma-4-31b-it':p.error('Budgeted transport is verified for Gemma only; use a separately budgeted compatible API for other models')
        import openrouter_budget as transport
        key_env=args.api_key_env or 'OPENROUTER_API_KEY';key=os.environ.get(key_env)
        if not key:p.error('Set '+key_env+' in environment; do not pass the key as an argument')
        transport.PROVIDER.update(only=['coreweave/fp4'],allow_fallbacks=False)
        provider=copy.deepcopy(transport.PROVIDER);budget=transport.Budget(args.cap)
        with urllib.request.urlopen('https://openrouter.ai/api/v1/models',timeout=30) as response:
            catalog={m['id']:m for m in json.load(response)['data']}
        if model not in catalog:p.error('Requested model absent from catalog')
        context=int(catalog[model]['context_length'])
        clients={name:transport.Client(model,key,context,budget,max_tokens=args.max_tokens,timeout=args.timeout) for name in profiles}
    else:
        key=os.environ.get(args.api_key_env or 'MODEL_API_KEY')
        clients={name:APIClient(args.base_url,model,key,timeout=args.timeout,max_tokens=args.max_tokens,no_thinking=args.no_thinking) for name in profiles}
    meta={'suite':suite.VERSION,'evidence_type':'MODEL_EVALUATION','model':model,'profiles':profiles,
          'selected_ids':[c['id'] for c in cases],'source_sha256':source_hashes(),
          'source_commit':source_commit(),
          'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'base_url':args.base_url or 'https://openrouter.ai/api/v1',
          'policy_base_sha256':hashlib.sha256(POLICY.encode()).hexdigest(),'v3_suffix_sha256':hashlib.sha256(suffix.encode()).hexdigest(),
          'temperature':0,'max_tokens':args.max_tokens,'max_steps':args.max_steps,'timeout':args.timeout,
          'provider_request':provider,'reasoning_request':{'enabled':False} if args.openrouter else ('none' if args.no_thinking else None),
          'order':'Profiles reverse on alternating cases; one attempt per case/profile, no automatic retry',
          'note':'Synthetic tool simulation; no real mail, document transfer or device effects. API errors retained. This set was not used to revise candidate prompts.'}
    args.output.mkdir(parents=True);results=[];interrupted=False
    try:
        for index,case in enumerate(cases):
            order=profiles if index%2==0 else list(reversed(profiles))
            for profile in order:
                r=suite.run_case(case,clients[profile],None if profile=='original' else suffix,max_steps=args.max_steps)
                r['profile']=profile;results.append(r);save(args.output,meta,results,cases,profiles,budget)
                print(profile,case['id'],r['score'],r['status'],'critical='+str(len(r['critical_violations'])),flush=True)
                if r['status']=='harness_error' and r.get('error')!='Invalid or excessive tool calls':return 1
    except KeyboardInterrupt:interrupted=True
    finally:
        meta['interrupted']=interrupted
        save(args.output,meta,results,cases,profiles,budget)
    return 130 if interrupted else 0


if __name__=='__main__':raise SystemExit(main())
