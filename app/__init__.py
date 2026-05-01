from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.config import get_database_url, get_secret_key
from app.routes import main_bp

__all__ = ["db", "create_app"]

db: SQLAlchemy = SQLAlchemy()


def configure_secret_key(app: Flask) -> None:
    app.config["SECRET_KEY"] = get_secret_key()


def configure_database(app: Flask) -> None:
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()
    db.init_app(app=app)


def configure_app(app: Flask) -> None:
    configure_secret_key(app)


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(blueprint=main_bp)


def create_app() -> Flask:
    app: Flask = Flask(import_name=__name__)
    configure_app(app)
    register_blueprints(app)
    configure_database(app)
    return app
