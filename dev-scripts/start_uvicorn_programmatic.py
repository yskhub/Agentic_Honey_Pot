import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from uvicorn import run

os.environ['API_KEY'] = os.environ.get('API_KEY', 'test_server_key')
os.environ['ADMIN_API_KEY'] = os.environ.get('ADMIN_API_KEY', 'test_admin_key')

if __name__ == '__main__':
    port = int(os.environ.get('DEV_SERVER_PORT', '8001'))
    run('backend.app.main:app', host='127.0.0.1', port=port)
