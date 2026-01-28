import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
print("Running pytest...")
code = subprocess.call([sys.executable, "-m", "pytest", str(ROOT / 'backend' / 'tests')])
if code != 0:
    print("Tests failed (exit code", code, ")")
    sys.exit(code)
print("Tests passed")
