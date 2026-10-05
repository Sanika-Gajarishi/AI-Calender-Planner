from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.database.base import Base
from app.database.connection import settings

# Import all models so they are registered with Base.metadata
from app.models import (
    User,
    Task,
    UserPreference,
    ScheduledBlock,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# --------------------------------------------------
# SQLAlchemy metadata
# --------------------------------------------------

target_metadata = Base.metadata


# --------------------------------------------------
# Offline migration
# --------------------------------------------------

def run_migrations_offline() -> None:

    url = settings.DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------
# Online migration
# --------------------------------------------------

def run_migrations_online() -> None:

    connectable = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# --------------------------------------------------
# Run
# --------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()