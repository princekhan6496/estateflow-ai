from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.db.database import Base, database_url
from app.models.models import Lead, Property, Interaction, LeadProperty


config = context.config

# Use the normalized database URL from the central database configuration.
# This converts:
#   postgresql://...
# into:
#   postgresql+psycopg://...
config.set_main_option("sqlalchemy.url", database_url)


# Load Alembic logging configuration if available.
# Some minimal alembic.ini files do not contain the logging sections,
# so migration should not fail just because logging configuration is absent.
if config.config_file_name:
    try:
        fileConfig(config.config_file_name)
    except KeyError:
        pass


# Metadata for Alembic autogenerate
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in offline mode."""

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in online mode."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()