import os

from app import create_app

app = create_app()

_debug_env: str = os.getenv("FLASK_DEBUG", "").strip().lower()
DEBUG: bool = _debug_env in {"1", "true", "yes", "y"}

if __name__ == "__main__":
    app.run(debug=DEBUG)
