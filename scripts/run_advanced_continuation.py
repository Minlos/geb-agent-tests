#!/usr/bin/env python3
"""Continue the interrupted Advanced32 experiment; preserve all original attempts.

The first ADV01D pair is excluded before repeating both sides, due to a reproduced
simulator bug. Other completed observations are retained, never cherry-picked.
"""
import copy
import datetime as dt
from decimal import Decimal
import json
import os
from pathlib import Path
import sys
import urllib.request
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import advanced_suite as suite
import openrouter_budget as transport
import run_advanced as cli
from run_tests import APIError
from unified_cases import POLICY
import hashlib

class PricedBudget(transport.Budget):
    def reserve(self,context,max_tokens):
        amount=Decimal(context)*Decimal('0.1')/1000000+Decimal(max_tokens)*Decimal('0.34')/1000000
        if self.spent+amount>self.cap:raise APIError('Aggregate budget guard stopped before request')
        self.spent+=amount;return amount

def main():
    source=ROOT/'runs/advanced32-gemma-original-v3-20261123/results.json'
    out=ROOT/'runs/advanced32-gemma-original-v3-continuation-20261123'
    if out.exists():raise SystemExit('New output required')
    first=json.loads(source.read_text());prior=first['budget']['spent_or_reserved_usd']
    keep=[r for r in first['results'] if r['id']!='ADV-01D' and r.get('conversation_complete') and r.get('score') is not None]
    done={(r['id'],r['profile']) for r in keep}
    budget=PricedBudget('0.30',prior)
    transport.PROVIDER.update(only=['coreweave/fp4'],allow_fallbacks=False,max_price={'prompt':0.1,'completion':0.34,'request':0})
    with urllib.request.urlopen('https://openrouter.ai/api/v1/models',timeout=30) as response:
        catalog={m['id']:m for m in json.load(response)['data']}
    model='google/gemma-4-31b-it';context=int(catalog[model]['context_length'])
    clients={p:transport.Client(model,os.environ['OPENROUTER_API_KEY'],context,budget,max_tokens=1024,timeout=300) for p in ['original','v3']}
    suffix=(ROOT/'prompts/household-procedure-v3.txt').read_text()
    meta={**first['metadata'],'source_sha256':cli.source_hashes(),'source_commit':cli.source_commit(),
          'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'provider_request':copy.deepcopy(transport.PROVIDER),
          'prior_spent_or_reserved_usd':prior,'reservation_prices_per_million':{'prompt':'0.1','completion':'0.34'},
          'source_results':str(source.relative_to(ROOT)),'excluded_pair':'ADV-01D: actual shown preview rejected by parser; both sides repeated after fix',
          'note':'Continuation only; completed valid first-stage observations retained separately. Shared $0.30 including unknown interrupted-request reservation. No retries of model failures.'}
    out.mkdir(parents=True);rows=[]
    try:
        for i,case in enumerate(suite.CASES):
            for profile in (['original','v3'] if i%2==0 else ['v3','original']):
                if (case['id'],profile) in done:continue
                r=suite.run_case(case,clients[profile],None if profile=='original' else suffix)
                r['profile']=profile;rows.append(r);cli.save(out,meta,rows,suite.CASES,['original','v3'],budget)
                print(profile,case['id'],r['score'],r['status'],'critical='+str(len(r['critical_violations'])),flush=True)
                if r['status']=='harness_error' and r.get('error')!='Invalid or excessive tool calls':return 1
    finally:cli.save(out,meta,rows,suite.CASES,['original','v3'],budget)
    return 0
if __name__=='__main__':raise SystemExit(main())
