#!/usr/bin/env python3
"""Continue only unattempted security pairs, retaining infrastructure failures/reservations."""
import copy
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import grok_security as suite
import openrouter_budget as transport
from run_tests import APIError

PRICE_PROMPT=Decimal('0.1')
PRICE_COMPLETION=Decimal('0.34')

class PinnedPriceBudget(transport.Budget):
    """Reserve full context at tighter provider-enforced ceilings, never release old holds."""
    def reserve(self,context,max_tokens):
        if type(context)is not int or type(max_tokens)is not int or min(context,max_tokens)<1:
            raise ValueError('Positive integer limits required')
        amount=Decimal(context)*PRICE_PROMPT/1000000+Decimal(max_tokens)*PRICE_COMPLETION/1000000
        if self.spent+amount>self.cap:raise APIError('Aggregate budget guard stopped before request')
        self.spent+=amount;return amount


def main():
    root=suite.ROOT;primary_path=root/'runs/grok-security-original-v3/results.json'
    primary=json.loads(primary_path.read_text());folder=root/'runs/grok-security-original-v3-tail'
    if folder.exists():raise SystemExit('Never overwrite evidence')
    for f,digest in primary['metadata']['source_sha256'].items():
        assert hashlib.sha256((root/f).read_bytes()).hexdigest()==digest
    meta=copy.deepcopy(primary['metadata'])
    meta.update(continuation_of_sha256=hashlib.sha256(primary_path.read_bytes()).hexdigest(),
        continuation_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        note='Unattempted pairs only; failed transport record and original full-context reservation retained. Price ceilings tightened to pinned endpoint advertised rates; all quality parameters unchanged.')
    meta['provider_request']['max_price']={'prompt':float(PRICE_PROMPT),'completion':float(PRICE_COMPLETION),'request':0}
    transport.PROVIDER.clear();transport.PROVIDER.update(meta['provider_request'])
    budget=PinnedPriceBudget(meta['aggregate_cap_usd'],primary['budget']['spent_or_reserved_usd'])
    key=os.environ['OPENROUTER_API_KEY'];clients={p:transport.Client(meta['model'],key,int(meta['catalog']['context_length']),budget) for p in ['original','v3']}
    suffix=(root/'prompts/household-procedure-v3.txt').read_text();cases=copy.deepcopy(suite.CASES)
    done={(r['id'],r['profile']) for r in primary['results']};results=[];folder.mkdir()
    def save():
        (folder/'results.json').write_text(json.dumps({'metadata':meta,'budget':{'cap_usd':str(budget.cap),'spent_or_reserved_usd':str(budget.spent)},'results':results},ensure_ascii=False,indent=2)+'\n')
    try:
        for idx,case in enumerate(cases):
            for profile in (['original','v3'] if idx%2==0 else ['v3','original']):
                if (case['id'],profile) in done:continue
                r=suite.run_case(case,clients[profile],None if profile=='original' else suffix)
                r.update(profile=profile,kind=case['kind'],family=case['family']);results.append(r);save()
                print(profile,case['id'],r['score'],r['status'],'critical',r['critical_violations'],'spent/reserved',budget.spent,flush=True)
                if r['status']=='harness_error' and r.get('error') not in ['Invalid or excessive tool calls','Transport/JSON error; no automatic retry; reservation retained']:
                    raise SystemExit('Stopped for budget/API review; evidence preserved')
    finally:save()


if __name__=='__main__':main()
