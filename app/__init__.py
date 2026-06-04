from flask import Flask

from app.config import get_env_var
from app.extensions import db
from app.views import main_bp

__all__ = ["create_app"]


def create_app() -> Flask:
    app: Flask = Flask(import_name=__name__)
    app.config["SECRET_KEY"] = get_env_var("SECRET_KEY")

    db.init_engine(database_url=get_env_var("DATABASE_URL"))
    app.register_blueprint(blueprint=main_bp)

    return app
