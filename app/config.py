from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

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
    if not rest:
        return database_url

    sqlite_parts = urlsplit(url=rest)
    sqlite_path = sqlite_parts.path
    if sqlite_path.startswith(":memory:"):
        return database_url

    is_windows_drive_path: bool = (
        len(sqlite_path) > 1 and sqlite_path[1] == ":"
    )

    if sqlite_path.startswith("/") or is_windows_drive_path:
        normalized_path = sqlite_path
    else:
        normalized_path = (_PROJECT_ROOT / sqlite_path).resolve().as_posix()

    normalized_parts = sqlite_parts._replace(path=normalized_path)
    return _SQLITE_REL_URI_PREFIX + urlunsplit(normalized_parts)
