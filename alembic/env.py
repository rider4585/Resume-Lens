"""Alembic environment: use app's Base and DATABASE_URL from .env."""

import os
import sys
from pathlib import Path

# Project root = parent of alembic dir (this file is in alembic/env.py)
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from app.config import get_settings
from app.models.db import Base

# Import all models so they are registered on Base.metadata
from app.models import match  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from app settings (reads .env)
database_url = get_settings().database_url
if "USERNAME" in database_url.upper() or "PASSWORD" in database_url.upper():
    raise ValueError(
        "DATABASE_URL in .env still contains placeholders. "
        "Replace USERNAME and PASSWORD with your real MySQL user and password. "
        "Example: mysql+pymysql://root:yourpassword@127.0.0.1:8889/resume_lens"
    )
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL only)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connect to DB)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
