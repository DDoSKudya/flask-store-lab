from __future__ import annotations

import os
from pathlib import Path

from app.messages import DATABASE_URL_NOT_SET, SECRET_KEY_NOT_SET

__all__ = ["get_secret_key", "get_database_url"]

_PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
_SQLITE_REL_URI_PREFIX: str = "sqlite:///"


def get_secret_key() -> str:
    secret_key: str | None = os.getenv("SECRET_KEY")
    if secret_key is None:
        raise ValueError(SECRET_KEY_NOT_SET)
    return secret_key


def get_database_url() -> str:
    database_url: str | None = os.getenv("DATABASE_URL")
    if database_url is None:
        raise ValueError(DATABASE_URL_NOT_SET)

    if not database_url.startswith(_SQLITE_REL_URI_PREFIX):
        return database_url

    rest: str = database_url.removeprefix(_SQLITE_REL_URI_PREFIX)
    if not rest or rest == ":memory:":
        return database_url

    path: Path = (
        Path(rest)
        if rest.startswith("/")
        else (_PROJECT_ROOT / rest).resolve()
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    return _SQLITE_REL_URI_PREFIX + path.resolve().as_posix()
