import pytest

from app.config import check_key, get_database_url, get_env_var, get_secret_key

pytestmark = pytest.mark.unit


def test_get_secret_key(monkeypatch) -> None:
    secret_key_value = "test-secret-token"
    monkeypatch.setenv("SECRET_KEY", secret_key_value)
    secret_key = get_secret_key()
    assert secret_key is not None
    assert secret_key == secret_key_value


def test_get_secret_key_raises_when_missing(monkeypatch) -> None:
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValueError, match="SECRET_KEY is not set"):
        get_secret_key()


def test_get_database_url(monkeypatch) -> None:
    expected_database_url = "sqlite:///test.db"
    monkeypatch.setenv("DATABASE_URL", expected_database_url)
    database_url = get_database_url()
    assert database_url is not None
    assert database_url == expected_database_url


def test_get_database_url_raises_when_missing(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="DATABASE_URL is not set"):
        get_database_url()


def test_get_env_var(monkeypatch) -> None:
    monkeypatch.setenv("EXAMPLE_VAR", "example-value")
    assert get_env_var("EXAMPLE_VAR") == "example-value"


def test_get_env_var_raises_when_missing(monkeypatch) -> None:
    monkeypatch.delenv("EXAMPLE_VAR", raising=False)
    with pytest.raises(ValueError, match="EXAMPLE_VAR is not set"):
        get_env_var("EXAMPLE_VAR")


@pytest.mark.parametrize(
    "message",
    [
        "foo",
    ],
)
def test_check_key_success(message) -> None:
    @check_key(message)
    def test_func() -> str:
        return message

    assert test_func() == message


@pytest.mark.parametrize(
    "message",
    [
        "foo",
    ],
)
def test_check_key_failure(message) -> None:
    @check_key(message)
    def test_func() -> str | None:
        return None

    with pytest.raises(ValueError, match=message):
        test_func()
