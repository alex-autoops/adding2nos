"""Course 14: Trace a Failed Workflow. Python standard library only."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
WORK = ROOT / 'output'

def show(value):
    print(json.dumps(value, indent=2) if not isinstance(value, str) else value)

def pipeline():
    WORK.mkdir(exist_ok=True)
    temp=WORK/'pipeline-temp.txt'
    records=[]
    temp.write_text('temporary build workspace')
    records.append({'stage':'prepare','status':'passed'})
    try:
        test=subprocess.run([sys.executable,'-c','assert 2 + 2 == 5, "intentional failing check"'],capture_output=True,text=True)
        records.append({'stage':'check','status':'failed' if test.returncode else 'passed','exit_code':test.returncode,'detail':test.stderr.strip()})
        if test.returncode:
            records.append({'stage':'package','status':'skipped','reason':'requires successful check'})
        else:
            records.append({'stage':'package','status':'passed'})
    finally:
        temp.unlink(missing_ok=True)
        records.append({'stage':'cleanup','status':'passed','temporary_file_removed':not temp.exists()})
    (WORK/'workflow-records.json').write_text(json.dumps(records,indent=2))
    show(records)
    return 1 if test.returncode else 0

if __name__ == "__main__":
    sys.exit(pipeline())
