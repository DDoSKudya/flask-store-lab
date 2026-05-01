import os

from flask import Flask

from app.routes import main_bp


def configure_app(app: Flask) -> None:
    secret_key: str | None = os.getenv("SECRET_KEY")
    if secret_key is None:
        raise ValueError("SECRET_KEY is not set")
    app.config["SECRET_KEY"] = secret_key


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(blueprint=main_bp)


def create_app() -> Flask:
    app: Flask = Flask(import_name=__name__)
    configure_app(app)
    register_blueprints(app)
    return app
