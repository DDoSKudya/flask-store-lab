from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

__all__ = ["db", "Session", "Database"]


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Database:
    def __init__(self) -> None:
        self._engine: Engine | None = None
        self._session_ctx = ContextVar[Session | None]("db_session", default=None)
        self._session_factory: sessionmaker[Session] | None = None

    def _new_session(self) -> Session:
        """
        Create a new database session from the configured factory.

        Ensures a session factory has been initialized before constructing and returning
        a session.

        Returns:
            A new SQLAlchemy Session instance bound to the configured engine.

        Raises:
            RuntimeError:
                If the session factory has not been initialized via init_engine.
        """
        if self._session_factory is None:
            raise RuntimeError("Session factory not initialized")
        return self._session_factory()

    @property
    def metadata(self) -> MetaData:
        return Base.metadata

    @property
    def session(self) -> Session:
        """
        Access the current scoped database session.

        Retrieves the session bound to the active context and enforces that one has been
        established.

        Returns:
            The SQLAlchemy Session associated with the current context.

        Raises:
            RuntimeError:
                If no session has been set in the current context.
        """
        s = self._session_ctx.get()
        if s is None:
            raise RuntimeError("No session found")
        return s

    @property
    def engine(self) -> Engine:
        """
        Access the underlying SQLAlchemy engine.

        Returns the lazily initialized engine and enforces that it has been configured
        before use.

        Returns:
            The SQLAlchemy Engine backing this Database instance.

        Raises:
            RuntimeError:
                If the engine has not been initialized via init_engine.
        """
        if self._engine is None:
            raise RuntimeError("Engine not initialized")
        return self._engine

    def init_engine(self, database_url: str) -> None:
        """
        Initialize the database engine and session factory.

        Creates an Engine for the given database URL and configures a session factory
        for producing ORM sessions bound to it.

        Args:
            database_url:
                Connection URL used to create the SQLAlchemy Engine and bind sessions.
        """
        self._engine = create_engine(database_url, pool_pre_ping=True)
        self._session_factory = sessionmaker(
            bind=self._engine,
            class_=Session,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.

        Creates a new session bound to the current context, commits on success, and
        rolls back and cleans up on error.

        Yields:
            The managed SQLAlchemy Session for use within the context block.
        """
        s = self._new_session()
        token = self._session_ctx.set(s)
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()
            self._session_ctx.reset(token)


db = Database()
