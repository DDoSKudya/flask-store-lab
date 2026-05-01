from __future__ import annotations

import os

from dotenv import load_dotenv

from app.messages import DATABASE_URL_NOT_SET, SECRET_KEY_NOT_SET

load_dotenv()


def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")
    if secret_key is None:
        raise ValueError(SECRET_KEY_NOT_SET)
    return secret_key


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise ValueError(DATABASE_URL_NOT_SET)
    return database_url
