#!/usr/bin/env python3
"""Continue uncompleted Qwen observations with isolated concurrent scenario pairs."""
from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import json
import os
from pathlib import Path
import threading
import run_qwen_new_sets as base
import openrouter_budget as transport
ROOT=base.ROOT
class Budget(base.Budget):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.lock=threading.RLock()
    def reserve(self,*args):
        with self.lock:return super().reserve(*args)
    def settle(self,*args):
        with self.lock:return super().settle(*args)

def pending(groups,done):
    return [(name,module,case,i,[p for p in (['original','v3'] if i%2==0 else ['v3','original']) if (name,case['id'],p) not in done]) for name,module,cases in groups for i,case in enumerate(cases) if any((name,case['id'],p) not in done for p in ['original','v3'])]

def main():
    source=ROOT/'runs/qwen-new-sets-original-v3-20261124/results.json'
    folder=ROOT/'runs/qwen-new-sets-parallel-20261124'
    if folder.exists():raise SystemExit('New output required')
    first=json.loads(source.read_text())
    for f,digest in first['metadata']['source_sha256'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==digest
    meta=copy.deepcopy(first['metadata']);meta.update(continuation_of_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        continuation_source=str(source.relative_to(ROOT)),continuation_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        workers=4,method='Four isolated scenario pairs concurrently. Within pair alternate original/v3; per-case/profile client traces isolated. Completed observations never repeated. Initial interrupted partial scenario has no completed observation; earlier spend and unknown reservation retained.',
        prior_spent_or_reserved_usd=first['budget']['spent_or_reserved_usd'])
    budget=Budget('0.50',meta['prior_spent_or_reserved_usd'])
    transport.PROVIDER.clear();transport.PROVIDER.update(copy.deepcopy(base.PROVIDER))
    key=os.environ['OPENROUTER_API_KEY'];context=int(meta['endpoint_catalog']['context_length'])
    suffix=(ROOT/'prompts/household-procedure-v3.txt').read_text()
    done={(r['dataset'],r['id'],r['profile']) for r in first['results']};jobs=pending(base.datasets(),done)
    results=[];result_lock=threading.Lock();folder.mkdir()
    def save():
        data={'metadata':meta,'budget':{'cap_usd':str(budget.cap),'spent_or_reserved_usd':str(budget.spent)},'results':results}
        (folder/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    def work(job):
        name,module,case,index,profiles=job
        for profile in profiles:
            client=transport.Client(base.MODEL,key,context,budget)
            r=module.run_case(case,client,None if profile=='original' else suffix)
            r.update(dataset=name,profile=profile,kind=case.get('kind'),family=case.get('family'))
            base.normalize_record(r,case)
            with result_lock:
                results.append(r);save()
                print(name,profile,case['id'],r.get('score'),r['status'],'critical='+str(len(r.get('critical_violations',[]))),'spent/reserved='+str(budget.spent),flush=True)
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(work,jobs))
    finally:
        with result_lock:save()
if __name__=='__main__':main()
