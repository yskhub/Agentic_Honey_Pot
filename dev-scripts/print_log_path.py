from pathlib import Path
import sys
sys.path.insert(0, str(Path('.').resolve()))
import importlib
ow = importlib.import_module('backend.app.outgoing_worker')
print('LOG_PATH:', ow.LOG_PATH)
print('exists:', ow.LOG_PATH.exists())
