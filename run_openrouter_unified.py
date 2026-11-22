#!/usr/bin/env python3
"""Run the selected three unified36 pilots with one aggregate USD cap."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import urllib.request

from openrouter_budget import Budget, Client, PROVIDER
import run_unified as runner
from unified_cases import CASES

MODELS = ['google/gemma-4-31b-it', 'qwen/qwen3.8-27b', 'qwen/qwen3.6-35b-a3b']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cap', default='1', help='Aggregate USD limit, including prior spend')
    parser.add_argument('--prior-spend', default='0', help='Conservative spend/reservations already used')
    parser.add_argument('--api-key-env', default='OPENROUTER_API_KEY')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    key = os.environ.get(args.api_key_env)
    if not key:
        parser.error('Configure the API key environment variable; never pass the key as an argument')
    budget = Budget(args.cap, args.prior_spend)
    with urllib.request.urlopen('https://openrouter.ai/api/v1/models', timeout=30) as response:
        catalog = {m['id']: m for m in json.load(response)['data']}
    for model in MODELS:
        if model not in catalog or not {'tools', 'tool_choice', 'reasoning'}.issubset(catalog[model]['supported_parameters']):
            parser.error('Catalog does not advertise required model capabilities: ' + model)
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder = args.output or runner.ROOT / 'runs' / ('unified-openrouter-' + stamp)
    if folder.exists():
        parser.error('Use a new output directory to preserve prior evidence')
    folder.mkdir(parents=True)
    cases = list(runner.expanded_cases(CASES))
    variants = {c['id']: sum(v['id'] == c['id'] for v in cases) for c in CASES}
    hashes = {f: hashlib.sha256((runner.ROOT / f).read_bytes()).hexdigest() for f in
              ['run_unified.py', 'unified_cases.py', 'unified_environment.py',
               'openrouter_budget.py', 'run_openrouter_unified.py']}
    interrupted = False
    try:
        for model in MODELS:
            m = catalog[model]
            out = folder / model.replace('/', '--')
            out.mkdir()
            (out / 'catalog.json').write_text(json.dumps(m, ensure_ascii=False, indent=2))
            client = Client(model, key, int(m['context_length']), budget)
            meta = {'model': model, 'suite': runner.VERSION, 'repeat': 1,
                    'case_ids': [c['id'] for c in CASES], 'variant_counts': variants,
                    'started_at_utc': stamp, 'source_sha256': hashes,
                    'max_tokens': 1024, 'max_steps': 12, 'timeout': 300,
                    'temperature': 0, 'reasoning_request': {'enabled': False},
                    'provider_request': PROVIDER, 'quantization': 'Unknown API artifact; not an exact Q4 GGUF run',
                    'aggregate_cap_usd': str(budget.cap), 'initial_spend_or_reserved_usd': args.prior_spend}
            results = []
            print('MODEL', model, flush=True)
            for case in cases:
                result = runner.run_case(case, client)
                result['repeat'] = 1
                results.append(result)
                meta['aggregate_spent_or_reserved_usd'] = str(budget.spent)
                runner.save_results(out, results, meta, variants)
                (folder / 'budget.json').write_text(json.dumps({'cap_usd': str(budget.cap),
                    'spent_or_reserved_usd': str(budget.spent), 'initial_spend_or_reserved_usd': args.prior_spend}, indent=2))
                print(model, case['id'], case['variant_id'], result.get('score'), result['status'],
                      'spent/reserved', budget.spent, flush=True)
                if result['status'] == 'harness_error':
                    break
    except KeyboardInterrupt:
        interrupted = True
    finally:
        # An interrupted in-flight request retains its full reservation.
        (folder / 'budget.json').write_text(json.dumps({'cap_usd': str(budget.cap),
            'spent_or_reserved_usd': str(budget.spent), 'initial_spend_or_reserved_usd': args.prior_spend,
            'interrupted': interrupted}, indent=2))
    print('Evidence:', folder, flush=True)
    return 130 if interrupted else 0


if __name__ == '__main__':
    raise SystemExit(main())
