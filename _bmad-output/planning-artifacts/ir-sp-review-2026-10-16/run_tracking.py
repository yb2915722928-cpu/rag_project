"""Run the unmodified sprint planner with a locally cached, read-only dependency."""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import runpy
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SCRIPT = ROOT / '.agents/skills/bmad-sprint-planning/scripts/sprint_plan.py'
CACHE = Path('E:/government/uv/cache/archive-v0/jFALiVrvihRXS3CK')
sys.dont_write_bytecode = True
sys.path.insert(0, str(CACHE))
import ruamel.yaml

if len(sys.argv) < 3:
    raise SystemExit('usage: run_tracking.py REPORT_NAME SCRIPT_SUBCOMMAND [ARGS...]')
report_name = sys.argv[1]
assert Path(report_name).name == report_name and report_name.endswith('.json')
arguments = sys.argv[2:]
sys.argv = [str(SCRIPT), *arguments]
capture = io.StringIO()
exit_code = 0
try:
    with contextlib.redirect_stdout(capture):
        namespace = runpy.run_path(str(SCRIPT))
        namespace['main'](arguments)
except SystemExit as exc:
    exit_code = exc.code or 0
raw = capture.getvalue()
report = json.loads(raw)
(OUT / report_name).write_text(raw, encoding='utf-8')
(OUT / (report_name.removesuffix('.json') + '.invocation.json')).write_text(json.dumps({
    'interpreter': sys.executable,
    'script': str(SCRIPT),
    'script_sha256': hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
    'script_modified': False,
    'dependency': 'ruamel.yaml',
    'dependency_version': ruamel.yaml.__version__,
    'dependency_path': ruamel.yaml.__file__,
    'arguments': arguments,
    'exit_code': exit_code,
    'scope': 'sprint document generation/validation only; product runtime not executed'
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(raw, end='')
raise SystemExit(exit_code)
