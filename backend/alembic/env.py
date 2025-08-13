
from __future__ import annotations
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def get_url():
    return os.getenv('DATABASE_URL', 'postgresql+psycopg2://sla_user:sla_pass@db:5432/sla_db')

from app.db import Base
from app.models.user import User  # noqa
from app.models.common import TimestampMixin, SoftDeleteMixin  # noqa
from app.models.calendar import Calendar  # noqa
from app.models.sla import SLA, SLAStatus  # noqa
from app.models.event import Event  # noqa
from app.models.incident import Incident  # noqa
from app.models.alert import Alert  # noqa
from app.models.delivery import DeliveryLog  # noqa
from app.models.audit import AuditLog  # noqa

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    connectable = engine_from_config(
        configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
        url=get_url(),
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
