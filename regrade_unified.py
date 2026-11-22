"""Offline unified rubric review with explicit changed-prompt replacements. No API."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

import run_unified as runner
from unified_cases import CASES, POLICY


def combine(primary, supplemental):
    if primary['metadata']['model'] != supplemental['metadata']['model']:
        raise ValueError('Different model identities cannot be combined')
    environment_hash = hashlib.sha256((runner.ROOT / 'unified_environment.py').read_bytes()).hexdigest()
    for data in [primary, supplemental]:
        if data['metadata']['source_sha256']['unified_environment.py'] != environment_hash:
            raise ValueError('Fixture/environment changed; offline comparison needs review')
    cases = {(c['id'], c['variant_id']): c for c in runner.expanded_cases(CASES)}
    replacement = {(r['id'], r['variant_id']): r for r in supplemental['results']}
    if set(replacement) != {key for key in cases if key[0] == 'T01'}:
        raise ValueError('Expected exactly the two changed T01 prompt variants')
    results = []
    seen = set()
    for original in primary['results']:
        key = original['id'], original['variant_id']
        if key in seen or key not in cases:
            raise ValueError('Duplicate or unknown observation')
        seen.add(key)
        source = replacement[key] if key[0] == 'T01' else original
        case = cases[key]
        if [t['user'] for t in source['turns']] != case['user_turns']:
            raise ValueError('Changed model prompt cannot be regraded as an unchanged task: ' + str(key))
        if source['messages'][0]['content'] != POLICY:
            raise ValueError('System prompt differs')
        row = copy.deepcopy(source)
        row['original_score'] = source.get('score')
        row['original_unmet_criteria'] = source.get('unmet_criteria', [])
        row['evidence_source'] = 'supplemental_T01' if key[0] == 'T01' else 'original_pilot'
        if row['status'] != 'harness_error':
            row.update(runner.grade_case(case, row))
            if row['status'] != 'complete' and row['score'] == 2:
                row.update(score=1, full_pass=False)
        results.append(row)
    if seen != set(cases):
        raise ValueError('Primary pilot does not cover every scenario variant')
    counts = {c['id']: sum(key[0] == c['id'] for key in cases) for c in CASES}
    summary = runner.summarize(results, expected_variants=counts)
    summary['fully_passed_scenarios'] = sum(all(r.get('score') == 2 for r in results if r['id'] == c['id']) for c in CASES)
    metadata = copy.deepcopy(primary['metadata'])
    metadata.update(grading_suite=runner.VERSION, grading_source_sha256={
        f: hashlib.sha256((runner.ROOT / f).read_bytes()).hexdigest()
        for f in ['run_unified.py', 'unified_cases.py', 'regrade_unified.py']},
        prompt_replacements=['T01'], supplemental_metadata=copy.deepcopy(supplemental['metadata']),
        note='Only T01 prompts changed; both original T01 records remain in the original source file. Other answers regraded offline; no new inference.')
    return {'metadata': metadata, 'summary': summary, 'results': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('primary', type=Path)
    parser.add_argument('supplemental', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new output file')
    result = combine(json.loads(args.primary.read_text()), json.loads(args.supplemental.read_text()))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()
