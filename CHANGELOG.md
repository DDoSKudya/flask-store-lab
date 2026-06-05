# Changelog

## [1.1.0] - 2026-06-04

### Added

- Paginated product catalog: `?page=` query parameter, `count_products()` and
  `ROW_NUMBER()`-based page window in `list_products()`, Bootstrap pagination
  footer on the products list template (prev/next, page numbers, total count).
- Integration coverage for list pagination and HTTP 500 on persistence failure
  (monkeypatched `count_products`); unit test for two-page product pagination.

### Changed

- Database access: replace `scoped_session` with `ContextVar`, `session_scope()`,
  and `db.session` in the service layer (no `session` argument in product
  services); update `tests/conftest.py` fixtures accordingly.
- Config: remove `check_key`, `get_secret_key`, and `get_database_url`; use
  `get_env_var()` directly in the app factory and Alembic `env.py`.
- Product delete: single `DELETE … RETURNING` instead of select-then-delete.
- Views: drop redundant per-route `ProductPersistenceError` + `abort(500)` on
  list/detail/delete; handle unhandled persistence errors via blueprint
  `@main_bp.errorhandler(ProductPersistenceError)`; keep create-form DB error UX.
- Tests: rename `tests/integration/test_routes.py` to `test_views.py`; assert
  HTTP statuses with `http.HTTPStatus`.
- Tooling: increase Ruff `line-length` to 120; add service-layer docstrings in
  `app/services/products.py`.

## [1.0.0] - 2026-05-06

### Added

- Initial release of **flask-store-lab** (`flask-store-lab`): Flask catalog with
  Jinja2 templates, Pydantic `ProductCreate` validation, SQLite storage via
  SQLAlchemy 2.x and Alembic migrations (unique product names), service layer
  for products, Bootstrap forms and `app.js` client checks, pytest unit and
  integration tests (`tests/conftest.py`), README (including dev, pytest, uWSGI),
  `CHANGELOG.md`, and MIT `LICENSE`.
