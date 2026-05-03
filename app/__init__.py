from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask

from app.config import get_database_url, get_secret_key
from app.extensions import db
from app.routes import main_bp

__all__ = ["db", "create_app"]


def configure_secret_key(app: Flask) -> None:
    app.config["SECRET_KEY"] = get_secret_key()


def _ensure_sqlite_parent_dir(database_url: str) -> None:
    sqlite_prefix = "sqlite:///"
    if not database_url.startswith(sqlite_prefix):
        return

    sqlite_rest = database_url.removeprefix(sqlite_prefix)
    sqlite_parts = urlsplit(url=sqlite_rest)
    sqlite_path = sqlite_parts.path
    is_memory = sqlite_path.startswith(":memory:")
    has_windows_drive = len(sqlite_path) > 1 and sqlite_path[1] == ":"
    if is_memory or has_windows_drive:
        return

    Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)


def configure_database(app: Flask) -> None:
    database_url = get_database_url()
    _ensure_sqlite_parent_dir(database_url=database_url)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    db.init_app(app=app)


def configure_app(app: Flask) -> None:
    configure_secret_key(app)


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(blueprint=main_bp)


def create_app() -> Flask:
    app: Flask = Flask(import_name=__name__)
    configure_app(app)
    configure_database(app)
    register_blueprints(app)
    return app
