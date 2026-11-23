#!/usr/bin/env python3
"""Build a small standalone offline-ready package; includes no credentials or live runs."""
from pathlib import Path
import argparse
import zipfile
ROOT=Path(__file__).resolve().parents[1]
FILES=['run_advanced.py','advanced_suite.py','advanced_environment.py','run_unified.py','run_tests.py',
       'unified_environment.py','unified_cases.py','openrouter_budget.py',
       'prompts/household-procedure-v3.txt','testsets/advanced-32.json',
       'scripts/build_advanced_cases.py','scripts/package_advanced.py',
       'test_advanced_environment.py','test_advanced_suite.py','test_advanced_cli.py',
       'docs/advanced-32.md','docs/advanced-32-catalog.md','docs/grok-advanced-cases.md',
       'results/advanced32-readiness/readiness.json']

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);args=p.parse_args()
    with zipfile.ZipFile(args.output,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:archive.write(ROOT/name,'geb-advanced-32/'+name)
        archive.writestr('geb-advanced-32/README.md',
            '# Advanced-1.0\n\n32 synthetic scenarios. See docs/advanced-32.md for Russian instructions.\n\n'
            'Offline verification (no model/API):\n\n```bash\npython3 run_advanced.py --self-test\n```\n')
    print(args.output)
if __name__=='__main__':main()
