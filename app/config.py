import os
from collections.abc import Callable
from typing import Any


def check_key(
    message: str,
) -> Callable[[Callable[..., str | None]], Callable[..., str]]:
    def decorator(func: Callable[..., str | None]) -> Callable[..., str]:
        def wrapper(*args: list[Any], **kwargs: dict[Any, Any]) -> str:
            value = func(*args, **kwargs)
            if value is None:
                raise ValueError(message)
            return value

        return wrapper

    return decorator


@check_key("SECRET_KEY is not set")
def get_secret_key() -> str | None:
    return os.getenv("SECRET_KEY")


@check_key("DATABASE_URL is not set")
def get_database_url() -> str | None:
    return os.getenv("DATABASE_URL")
