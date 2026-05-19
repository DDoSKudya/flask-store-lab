from flask import Flask

from app.config import (
    get_database_url,
    get_secret_key,
)
from app.extensions import db
from app.views import main_bp

__all__ = ["create_app"]


def create_app() -> Flask:
    app: Flask = Flask(import_name=__name__)
    # Configure app
    app.config["SECRET_KEY"] = get_secret_key()

    # Configure database
    db.init_engine(database_url=get_database_url())

    # Register blueprints
    app.teardown_appcontext(lambda exception: db.remove_session())

    # Register blueprints
    app.register_blueprint(blueprint=main_bp)

    return app
