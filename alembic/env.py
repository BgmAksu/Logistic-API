from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import app metadata
from app.db import Base
from app.settings import settings
import app.models  # ensure models are imported so Base.metadata has tables

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLAlchemy URL programmatically from settings if not provided in alembic.ini
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.sqlalchemy_url)

# target_metadata for 'autogenerate'
target_metadata = Base.metadata

# tables we never want Alembic to touch
SKIP_TABLES = {
    # common PostGIS / tiger / topology tables (public schema)
    "spatial_ref_sys", "geography_columns", "geometry_columns",
    "raster_columns", "raster_overviews",
    "geocode_settings", "geocode_settings_default",
    "loader_lookuptables", "loader_platform", "loader_variables",
    # tiger / tiger_data sample tables
    "addr", "addrfeat", "edges", "faces", "featnames",
    "place", "place_lookup", "county", "county_lookup", "state",
    "zcta5", "cousub", "countysub_lookup", "direction_lookup",
    "secondary_unit_lookup", "street_type_lookup",
    "tabblock", "tabblock20", "tract", "zip_lookup",
    "zip_lookup_all", "zip_lookup_base", "zip_state", "zip_state_loc",
    "pagc_gaz", "pagc_lex", "pagc_rules", "layer", "topology",
}

SKIP_SCHEMAS = {"tiger", "tiger_data", "topology"}

def include_object(object, name, type_, reflected, compare_to):
    """
    - Skip PostGIS/tiger/topology schemas and known extension tables.
    - Also skip 'reflected-only' objects (present in DB but not in metadata),
      so Alembic doesn't emit DROP statements for them.
    """
    if type_ == "table":
        schema = getattr(object, "schema", None)
        if schema in SKIP_SCHEMAS or name in SKIP_TABLES:
            return False
        if reflected and compare_to is None:
            return False
    if type_ == "index":
        tbl = getattr(object, "table", None)
        if tbl is not None:
            schema = getattr(tbl, "schema", None)
            if schema in SKIP_SCHEMAS or tbl.name in SKIP_TABLES:
                return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
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
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
