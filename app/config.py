from __future__ import annotations

import os

from dotenv import load_dotenv

from app.messages import Messages

load_dotenv()


def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")
    if secret_key is None:
        raise ValueError(Messages.SECRET_KEY_NOT_SET.value)
    return secret_key


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise ValueError(Messages.DATABASE_URL_NOT_SET.value)
    return database_url
