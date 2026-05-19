from collections.abc import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from app import create_app
from app.extensions import Base, db


@pytest.fixture
def app(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> Generator[Flask, None, None]:
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")

    app = create_app()
    app.config["TESTING"] = True

    bootstrap_session = db.session()
    engine = bootstrap_session.get_bind()
    bootstrap_session.close()
    db.remove_session()
    Base.metadata.create_all(bind=engine)

    yield app

    Base.metadata.drop_all(bind=engine)
    db.remove_session()


@pytest.fixture(autouse=True)
def db_session(app: Flask) -> Generator[Session, None, None]:
    session = db.session()
    try:
        yield session
    finally:
        if session.in_transaction():
            session.rollback()
        session.close()
        db.remove_session()


@pytest.fixture
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    with app.test_client() as client:
        yield client
