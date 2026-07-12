import os
from collections.abc import AsyncGenerator
from pathlib import Path

import psycopg
import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from psycopg import sql

from alembic import command
from devos_api.main import app

ROOT = Path(__file__).resolve().parents[1]


def _admin_dsn(db: str = "postgres") -> str:
    base = os.getenv("DATABASE_ADMIN_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    return base.rsplit("/", 1)[0] + f"/{db}"


def _migrator_dsn() -> str:
    return os.getenv(
        "DATABASE_MIGRATOR_URL",
        "postgresql://devos_migrator:devos_migrator@localhost:5432/devos_app",
    )


def _api_dsn() -> str:
    return os.getenv(
        "DATABASE_API_URL",
        "postgresql://devos_api:devos_api@localhost:5432/devos_app",
    )


def _bootstrap_roles() -> None:
    admin = psycopg.connect(_admin_dsn("postgres"), autocommit=True)
    try:
        with admin.cursor() as cur:
            for db in ("devos_app", "devos_audit"):
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db,))
                if cur.fetchone() is None:
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db)))
    finally:
        admin.close()

    app_sql = """
    CREATE EXTENSION IF NOT EXISTS pgcrypto;

    DO $$
    BEGIN
      IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'devos_migrator') THEN
        CREATE ROLE devos_migrator LOGIN PASSWORD 'devos_migrator' BYPASSRLS;
      END IF;
      IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'devos_api') THEN
        CREATE ROLE devos_api LOGIN PASSWORD 'devos_api' NOSUPERUSER NOBYPASSRLS;
      END IF;
      IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'devos_readonly') THEN
        CREATE ROLE devos_readonly LOGIN PASSWORD 'devos_readonly' NOSUPERUSER NOBYPASSRLS;
      END IF;
    END
    $$;

    ALTER ROLE devos_migrator BYPASSRLS;

    GRANT CONNECT ON DATABASE devos_app TO devos_migrator, devos_api, devos_readonly;
    GRANT CREATE ON SCHEMA public TO devos_migrator;
    GRANT USAGE ON SCHEMA public TO devos_api, devos_readonly;

    ALTER DEFAULT PRIVILEGES FOR ROLE devos_migrator IN SCHEMA public
      GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO devos_api;
    ALTER DEFAULT PRIVILEGES FOR ROLE devos_migrator IN SCHEMA public
      GRANT SELECT ON TABLES TO devos_readonly;
    """

    audit_sql = """
    CREATE EXTENSION IF NOT EXISTS pgcrypto;

    GRANT CONNECT ON DATABASE devos_audit TO devos_migrator, devos_api, devos_readonly;
    GRANT CREATE ON SCHEMA public TO devos_migrator;
    GRANT USAGE ON SCHEMA public TO devos_api, devos_readonly;

    ALTER DEFAULT PRIVILEGES FOR ROLE devos_migrator IN SCHEMA public
      GRANT SELECT, INSERT ON TABLES TO devos_api;
    ALTER DEFAULT PRIVILEGES FOR ROLE devos_migrator IN SCHEMA public
      GRANT SELECT ON TABLES TO devos_readonly;
    """

    for db_name, bootstrap_sql in (("devos_app", app_sql), ("devos_audit", audit_sql)):
        conn = psycopg.connect(_admin_dsn(db_name), autocommit=True)
        try:
            with conn.cursor() as cur:
                cur.execute(bootstrap_sql)  # type: ignore[arg-type]
        finally:
            conn.close()


@pytest.fixture(scope="session")
def database_ready() -> None:
    _bootstrap_roles()

    alembic_cfg = Config(str(ROOT / "infra" / "db" / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(ROOT / "infra" / "db" / "alembic"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        _migrator_dsn().replace("postgresql://", "postgresql+psycopg://"),
    )
    command.upgrade(alembic_cfg, "head")


@pytest.fixture
def api_conn(database_ready: None):
    conn = psycopg.connect(_api_dsn())
    conn.autocommit = False
    yield conn
    conn.rollback()
    conn.close()


@pytest.fixture
def migrator_conn(database_ready: None):
    conn = psycopg.connect(_migrator_dsn())
    conn.autocommit = True
    yield conn
    conn.close()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
