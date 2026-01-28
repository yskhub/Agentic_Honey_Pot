import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add project root so we can import backend.app.db
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging. Be tolerant if logging
# sections expected by the project's alembic.ini are missing (CI/local
# environments may not provide logger_sqlalchemy entries). Use fileConfig
# only when the file exists and the necessary sections can be read.
if config.config_file_name is not None:
    try:
        # Attempt to configure logging from file; guard against missing sections
        fileConfig(config.config_file_name)
    except Exception:
        # Fallback: configure basic logging to avoid KeyError during env import
        import logging
        logging.basicConfig(level=logging.INFO)

# import your model's MetaData object here
from backend.app import db as app_db

target_metadata = app_db.Base.metadata


def run_migrations_offline():
    url = config.get_main_option('sqlalchemy.url')
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
