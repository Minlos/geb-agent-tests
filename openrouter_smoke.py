#!/usr/bin/env python3
"""Run the two synthetic smoke cases on a verified zero-priced endpoint."""
import argparse
import datetime
import getpass
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request


MODEL = 'google/gemma-4-26b-a4b-it:free'
BASE = 'https://openrouter.ai/api/v1'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='Verify the public model listing only; no key or inference')
    args = parser.parse_args()
    request = urllib.request.Request(BASE + '/models')
    # Catalog requests do not contain credentials. No model or paid fallback.
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            catalog = json.load(response)
        model = next(m for m in catalog['data'] if m['id'] == MODEL)
        from decimal import Decimal
        prices = model['pricing']
        if not all(Decimal(prices[k]) == 0 for k in ('prompt', 'completion')):
            raise ValueError('Model is not listed with zero input/output pricing')
        for name, value in prices.items():
            if name not in ('discount',) and Decimal(value) > 0:
                raise ValueError('Model lists an additional positive charge')
        if not {'tools', 'tool_choice'}.issubset(model['supported_parameters']):
            raise ValueError('Model does not advertise structured tool support')
    except Exception:
        print('Preflight failed: verify model availability, zero pricing and tool support. No inference sent.', file=sys.stderr)
        return 2
    print('Preflight passed:', MODEL, '(zero listed input/output price; tools advertised)')
    if args.check:
        return 0
    key = os.environ.get('OPENROUTER_API_KEY')
    if not key:
        if not sys.stdin.isatty():
            print('Set OPENROUTER_API_KEY or run in Terminal for a hidden key prompt.', file=sys.stderr)
            return 2
        key = getpass.getpass('Paste OpenRouter API key (hidden; not saved): ').strip()
    if not key:
        print('No key supplied. No inference sent.', file=sys.stderr)
        return 2
    root = Path(__file__).resolve().parent
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = root / 'runs' / ('openrouter-gemma4-smoke-' + stamp)
    output.mkdir(parents=True)
    (output / 'catalog-model.json').write_text(json.dumps(model, ensure_ascii=False, indent=2))
    env = dict(os.environ, OPENROUTER_API_KEY=key)
    command = [sys.executable, str(root / 'run_tests.py'), '--base-url', BASE,
               '--api-key-env', 'OPENROUTER_API_KEY', '--model', MODEL,
               '--only', 'MAIL-01,HOME-02', '--repeat', '1', '--max-tokens', '1024',
               '--timeout', '120', '--output', str(output)]
    print('Running MAIL-01 and HOME-02. Real model requests; synthetic tools only.')
    code = subprocess.run(command, cwd=root, env=env).returncode
    print('Evidence folder:', output)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
