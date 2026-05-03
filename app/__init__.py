from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from flask import Flask

from app.config import (
    ensure_sqlite_parent_dir,
    get_database_url,
    get_secret_key,
)
from app.extensions import db
from app.routes import main_bp

__all__ = ["db", "create_app"]


def configure_secret_key(app: Flask) -> None:
    app.config["SECRET_KEY"] = get_secret_key()


def configure_database(app: Flask) -> None:
    database_url = get_database_url()
    ensure_sqlite_parent_dir(database_url=database_url)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    db.init_app(app=app)


def configure_app(app: Flask) -> None:
    configure_secret_key(app)


def format_price(value: object) -> str:
    try:
        amount = Decimal(str(value)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    except (InvalidOperation, ValueError):
        return str(value)
    return f"{amount:,.2f}"


def configure_jinja(app: Flask) -> None:
    app.jinja_env.filters["price"] = format_price


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(blueprint=main_bp)


def create_app() -> Flask:
    app: Flask = Flask(import_name=__name__)
    configure_app(app)
    configure_database(app)
    configure_jinja(app)
    register_blueprints(app)
    return app
