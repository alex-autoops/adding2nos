import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / 'lab_work'

def show(value):
    print(json.dumps(value, indent=2) if not isinstance(value, str) else value)

def apply():
    WORK.mkdir(exist_ok=True)
    target = WORK/'managed.json'
    desired = json.loads((ROOT/'desired.json').read_text())
    current = json.loads(target.read_text()) if target.exists() else {}
    changes = {key:{'before':current.get(key), 'after':value} for key,value in desired.items() if current.get(key)!=value}
    if changes:
        current.update(desired)
        target.write_text(json.dumps(current,indent=2))
    show({'changed':len(changes), 'changes':changes, 'matches_desired':all(current.get(k)==v for k,v in desired.items())})

def compare():
    desired=json.loads((ROOT/'desired.json').read_text())
    actual=json.loads((WORK/'managed.json').read_text())
    show({k:{'desired':v,'actual':actual.get(k),'match':actual.get(k)==v} for k,v in desired.items()})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=['apply', 'compare'])
    action = parser.parse_args().action
    tasks = {'apply': apply, 'compare': compare}
    tasks[action]()
