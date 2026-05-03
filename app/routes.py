from collections.abc import Sequence

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from pydantic import ValidationError
from pydantic_core import ErrorDetails
from sqlalchemy.exc import SQLAlchemyError
from werkzeug import Response as WerkzeugResponse

from app.extensions import db
from app.models import Product
from app.schemas import ProductCreate

main_bp: Blueprint = Blueprint(name="main", import_name=__name__)

_PRODUCT_NEW_TEMPLATE = "products/new.html"
_PRODUCT_NEW_TITLE = "New product"


def _render_new_product(
    *,
    form_name: str,
    form_price: str,
    form_description: str,
    errors: Sequence[ErrorDetails] | None,
) -> str:
    return render_template(
        _PRODUCT_NEW_TEMPLATE,
        page_title=_PRODUCT_NEW_TITLE,
        form_name=form_name,
        form_price=form_price,
        form_description=form_description,
        errors=errors,
    )


def _read_product_form() -> tuple[str, str, str, dict[str, str | None]]:
    form_name: str = request.form.get("name", "").strip()
    form_price: str = request.form.get("price", "").strip()
    form_description: str = request.form.get("description", "").strip()
    payload: dict[str, str | None] = {
        "name": form_name,
        "price": form_price,
        "description": form_description or None,
    }
    return form_name, form_price, form_description, payload


def _persist_product(data: ProductCreate) -> list[ErrorDetails] | None:
    product: Product = Product(
        name=data.name,  # pyright: ignore[reportCallIssue]
        price=data.price,  # pyright: ignore[reportCallIssue]
        description=data.description,  # pyright: ignore[reportCallIssue]
    )
    db.session.add(instance=product)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        msg = "Could not save the product. Please try again."
        db_error: ErrorDetails = {
            "type": "database_error",
            "loc": (),
            "msg": msg,
            "input": None,
        }
        return [db_error]
    return None


@main_bp.route(rule="/", methods=["GET"])
def index() -> str:
    return render_template(
        template_name_or_list="base.html", page_title="Home"
    )


@main_bp.route(rule="/health", methods=["GET"])
def health() -> WerkzeugResponse:
    return WerkzeugResponse(status=200, response="OK")


@main_bp.route("/products/new", methods=["GET", "POST"])
def new_product() -> str | WerkzeugResponse:
    if request.method != "POST":
        return _render_new_product(
            form_name="",
            form_price="",
            form_description="",
            errors=None,
        )

    form_name, form_price, form_description, payload = _read_product_form()

    try:
        data: ProductCreate = ProductCreate.model_validate(payload)
    except ValidationError as exc:
        return _render_new_product(
            form_name=form_name,
            form_price=form_price,
            form_description=form_description,
            errors=exc.errors(),
        )

    db_errors: list[ErrorDetails] | None = _persist_product(data)
    if db_errors is not None:
        return _render_new_product(
            form_name=data.name,
            form_price=str(data.price),
            form_description=data.description or "",
            errors=db_errors,
        )

    flash(message="Product created.", category="success")
    return redirect(location=url_for(endpoint="main.index"))
