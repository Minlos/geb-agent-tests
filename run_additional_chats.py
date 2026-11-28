#!/usr/bin/env python3
"""Sequential persona pairs share one durable aggregate budget; no concurrent invocations."""
import argparse
import json
import sys
from pathlib import Path
import run_natural_chat as chat
PERSONAS={'marina':'marina-product-lead-v1.json','dmitry':'dmitry-it-owner-v1.json','olga':'olga-finance-director-v1.json'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--turns',type=Path,required=True);args=parser.parse_args()
    groups=json.loads(args.turns.read_text())
    if not groups or set(groups)-set(PERSONAS):raise SystemExit('Unknown persona')
    base=chat.ROOT/'runs/natural-chat-additional-20261128'
    for name,turns in groups.items():
        turnfile=base/(name+'-current-input.json');turnfile.write_text(json.dumps(turns,ensure_ascii=False)+'\n')
        sys.argv=['run_natural_chat.py','--turns',str(turnfile),'--output',str(base/name),'--transport','curl',
                  '--persona-file',str(chat.ROOT/'personas'/PERSONAS[name]),'--shared-budget',str(base/'budget.json'),'--continue-truncated']
        print('\nPERSONA '+name,flush=True);chat.main()
if __name__=='__main__':main()
