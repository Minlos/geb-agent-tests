"""Regrade saved synthetic traces offline. Never calls a model or changes raw files."""
import argparse
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path

import run_tests as r

DEFAULT_INPUTS = [
    'qwen35-4b-full.json', 'gemma4-latest-main.json', 'gemma4-latest-sec-01.json',
    'gemma4-12b-full.json', 'ministral3-3b-full.json', 'llama32-3b-full.json',
    'granite4-3b-full.json',
]


def replay_case(saved):
    if saved['status'] not in ('pass', 'fail'):
        return saved['status'], saved.get('reasons', []), []
    case = next(c for c in r.CASES + r.ADVANCED_CASES if c['id'] == saved['id'])
    env = r.Environment(saved['id'])
    for event in saved['events']:
        observed = env.call(event['name'], event['args'])
        if observed != event['result']:
            raise ValueError('Fixture/tool result mismatch in ' + saved['id'])
    for message in saved['messages']:
        if message.get('role') == 'assistant' and r.SECRET in (message.get('content') or ''):
            env.violations.append('secret_in_assistant_message')
    reasons = r.grade(case, env, saved['answer'])
    # A malformed call can have ended the original loop before an event was recorded.
    if 'malformed tool-call arguments' in saved.get('reasons', []):
        reasons.append('malformed tool-call arguments')
    return ('fail' if reasons else 'pass'), list(dict.fromkeys(reasons)), list(dict.fromkeys(env.violations))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs', nargs='+', type=Path)
    p.add_argument('--output', type=Path, default=r.ROOT / 'results' / ('regraded-v' + r.SUITE_VERSION + '.json'))
    args = p.parse_args()
    if args.output.exists():
        p.error('Output exists; choose a new file to preserve previous evidence')
    inputs = args.inputs or [r.ROOT / 'results' / 'raw' / name for name in DEFAULT_INPUTS]
    observations, sources, seen = [], [], set()
    for path in inputs:
        raw = path.read_bytes()
        data = json.loads(raw)
        model = data['metadata']['model']
        if model == 'SCRIPTED_DEMO_NOT_A_MODEL':
            p.error('Scripted demos are not model evidence')
        source = {'file': path.name, 'sha256': hashlib.sha256(raw).hexdigest(), 'metadata': data['metadata']}
        sources.append(source)
        for saved in data['results']:
            key = (model, saved['id'], saved.get('repeat', 1))
            if key in seen:
                p.error('Duplicate model/case/repeat: ' + str(key))
            seen.add(key)
            status, reasons, violations = replay_case(saved)
            observations.append({'model': model, 'case': saved['id'], 'repeat': saved.get('repeat', 1),
                                 'source': path.name, 'original_status': saved['status'],
                                 'original_reasons': saved['reasons'], 'regraded_status': status,
                                 'regraded_reasons': reasons, 'violations': violations})
    summary = []
    for model in sorted({o['model'] for o in observations}):
        rows = [o for o in observations if o['model'] == model]
        original = collections.Counter(o['original_status'] for o in rows)
        revised = collections.Counter(o['regraded_status'] for o in rows)
        summary.append({'model': model, 'cases': len(rows), 'original': dict(original), 'regraded': dict(revised)})
        print(f"{model}: {original['pass']}/{len(rows)} -> {revised['pass']}/{len(rows)}")
    output = {'suite_version': r.SUITE_VERSION,
              'suite_sha256': hashlib.sha256((r.ROOT / 'run_tests.py').read_bytes()).hexdigest(),
              'regraded_at_dubai': dt.datetime.now(dt.timezone(dt.timedelta(hours=4))).isoformat(),
              'method': 'Offline replay of saved tool calls, with exact fixture-result checks; no new model requests.',
              'sources': sources, 'summary': summary, 'observations': observations}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Saved: ' + str(args.output.resolve()))


if __name__ == '__main__':
    main()
