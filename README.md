# flask-store-lab

`flask-store-lab` — учебный Flask-проект каталога товаров.

Стек:

- Flask
- SQLAlchemy 2.x
- Alembic
- Pydantic
- Pytest
- uWSGI

## 1) Требования

- Python 3.12+
- `pip`
- Linux/macOS/WSL (команды ниже в bash/zsh)

## 2) Установка зависимостей

Из корня проекта:

```bash
python -m venv .venv
source .venv/bin/activate
# Для Windows:
## cmd: .venv\Scripts\activate.bat
## ps: .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Настройка переменных окружения

Приложение читает переменные из `.env` (через `python-dotenv`).

Создайте `.env` на основе примера:

```bash
cp .env.example .env
```

Минимально нужно задать:

```env
SECRET_KEY=change-me
DATABASE_URL=sqlite:///instance/app.db
FLASK_DEBUG=1
```

## 4) Миграции (Alembic)

Перед запуском приложения примените миграции:

```bash
alembic upgrade head
```

Создать новую миграцию:

```bash
alembic revision --autogenerate -m "your message"
```

Откатить на 1 шаг:

```bash
alembic downgrade -1
```

## 5) Запуск dev-версии (с reload)

### Вариант A (рекомендуемый)

```bash
flask --app main:app --debug run
```

### Вариант B

`main.py` тоже поддерживает debug-режим через `FLASK_DEBUG`:

```bash
python main.py
```

## 6) Тесты (pytest)

Установите зависимости для разработки (в них входит pytest, см. `requirements-dev.txt`):

```bash
pip install -r requirements-dev.txt
```

Запуск всех тестов из корня репозитория:

```bash
python -m pytest
```

Только интеграционные или только юнит-тесты (маркеры заданы в `pyproject.toml`):

```bash
python -m pytest -m integration
python -m pytest -m unit
```

## 7) Запуск через uWSGI

Базовый запуск uWSGI:

```bash
uwsgi --http 127.0.0.1:8000 --wsgi-file main.py --callable app --master --processes 2 --threads 2
```

Где:

- `--wsgi-file main.py` — точка входа
- `--callable app` — Flask-приложение из `main.py`
- `--http 127.0.0.1:8000` — HTTP-сокет uWSGI

## 8) Быстрый чек-лист запуска с нуля

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')|" .env
alembic upgrade head
flask --app main:app --debug run
```

## Лицензия

Исходный код распространяется по лицензии MIT — см. файл [LICENSE](LICENSE).

## История изменений

Список версий и изменений — в [CHANGELOG.md](CHANGELOG.md).
