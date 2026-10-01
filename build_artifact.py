import argparse
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
WORK = ROOT / 'output'


def show(value):
    print(json.dumps(value, indent=2) if not isinstance(value, str) else value)

def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()

def build():
    WORK.mkdir(exist_ok=True)
    if git('status','--porcelain'):
        raise SystemExit('Commit the source changes before building.')
    commit=git('rev-parse','HEAD')
    version=git('show','HEAD:VERSION').strip()
    inventory={'version':version,'source_commit':commit,'components':['app.py','VERSION'],'external_dependencies':[]}
    target=WORK/'artifact.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for filename in inventory['components']:
            z.writestr(filename, subprocess.check_output(['git', 'show', f'HEAD:{filename}'], cwd=ROOT))
        z.writestr('manifest.json',json.dumps(inventory,indent=2))
    show(str(target))

def inspect():
    with zipfile.ZipFile(WORK/'artifact.zip') as z:
        show(z.namelist())
        show(json.loads(z.read('manifest.json')))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=['build', 'inspect'])
    action = parser.parse_args().action
    tasks = {'build': build, 'inspect': inspect}
    tasks[action]()
