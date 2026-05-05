from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    scoped_session,
    sessionmaker,
)

__all__ = ["db", "Session", "Database"]


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Database:
    def __init__(self) -> None:
        self._engine: Engine | None = None
        self.session: scoped_session[Session] = scoped_session(
            sessionmaker(
                autocommit=False, autoflush=False, expire_on_commit=False
            )
        )

    @property
    def metadata(self) -> MetaData:
        return Base.metadata

    def init_engine(self, database_url: str) -> None:
        self._engine = create_engine(database_url)
        self.session.configure(bind=self._engine)

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        s = self.session()
        try:
            yield s
            s.commit()
        except SQLAlchemyError:
            s.rollback()
            raise
        finally:
            self.session.remove()

    def remove_session(self) -> None:
        self.session.remove()


db = Database()
