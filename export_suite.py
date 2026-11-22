"""Export the fixed cases and package only explicit, synthetic release files."""
import hashlib
import json
from pathlib import Path
import zipfile

import run_tests as r

root = Path(__file__).resolve().parent
env = r.Environment('EXPORT')
spec = dict(version=r.SUITE_VERSION, policy=r.POLICY, tools=r.TOOLS, cases=r.CASES, advanced_cases=r.ADVANCED_CASES,
            virtual_files=env.files, mail=env.mail, drafts=env.drafts,
            devices=env.devices, products=env.products, web_pages=env.pages,
            suite_sha256=hashlib.sha256((root / 'run_tests.py').read_bytes()).hexdigest(),
            note='Reference actions and answers are evaluator-only; do not send them to the model.')
(root / 'test-spec.json').write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding='utf-8')
lines = ['# Household assistant test cases', '',
         'All data is synthetic. Every case resets the environment. The system policy and tools are in test-spec.json.', '',
         'Reference answers below are for the evaluator only. They are not added to model requests.', '']
for title, cases in (('Baseline suite', r.CASES), ('Advanced suite', r.ADVANCED_CASES)):
    lines += ['## ' + title, '']
    for c in cases:
        lines += ['### ' + c['id'], '', '**Task:** ' + c['prompt'], '']
        if c['context']:
            lines += ['**Initial context:** ' + c['context'], '']
        lines += ['**Example expected answer:** ' + c['expected_text'], '', '**Automatic acceptance checks:**', '',
                  '```json', json.dumps(c['checks'], ensure_ascii=False, indent=2), '```', '']
(root / 'TEST_CASES.md').write_text('\n'.join(lines), encoding='utf-8')
files = ['README.md', 'TEST_CASES.md', 'run_tests.py', 'test_runner.py',
         'export_suite.py', 'regrade_saved.py', 'test-spec.json',
         'results/fix-and-rerun-instructions.md', 'example-demo/results.json', 'example-demo/summary.md']
target = root / ('geb-agent-tests-v' + r.SUITE_VERSION + '.zip')
with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for name in files:
        z.write(root / name, 'geb-agent-tests/' + name)
print('Written: ' + str(target))
