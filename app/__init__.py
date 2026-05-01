import os

from flask import Flask

from app.routes import main_bp


def configure_app(app: Flask) -> None:
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(blueprint=main_bp)


def create_app() -> Flask:
    app: Flask = Flask(import_name=__name__)
    configure_app(app)
    register_blueprints(app)
    return app
