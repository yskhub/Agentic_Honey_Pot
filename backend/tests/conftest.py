import os
import pathlib

def pytest_configure(config):
    # remove existing sqlite DB so tests run against fresh schema
    db_path = pathlib.Path(os.getenv('DATABASE_URL', 'sqlite:///data/sentinel.db').replace('sqlite:///', ''))
    try:
        if db_path.exists():
            db_path.unlink()
    except Exception:
        pass
