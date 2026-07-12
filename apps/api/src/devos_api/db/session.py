from collections.abc import Generator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from devos_api.config import Settings, get_settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine(settings: Settings | None = None) -> Engine:
    global _engine
    if _engine is None:
        settings = settings or get_settings()
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine


def get_session_factory(settings: Settings | None = None) -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(settings), autoflush=False, autocommit=False
        )
    return _session_factory


@contextmanager
def tenant_session(tenant_id: UUID | None) -> Generator[Session, None, None]:
    """Open a DB session with tenant context enforced via SET LOCAL."""
    factory = get_session_factory()
    session = factory()
    try:
        with session.begin():
            if tenant_id is None:
                session.execute(text("RESET app.tenant_id"))
            else:
                session.execute(
                    text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                    {"tenant_id": str(tenant_id)},
                )
            yield session
    finally:
        session.close()


def reset_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
