from collections.abc import Sequence
from dataclasses import dataclass

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.typing import ResponseReturnValue
from pydantic import ValidationError
from pydantic_core import ErrorDetails
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Product
from app.schemas import ProductCreate

main_bp: Blueprint = Blueprint(name="main", import_name=__name__)

_PRODUCT_NEW_TEMPLATE = "products/new.html"
_PRODUCT_NEW_TITLE = "New product"


@dataclass(slots=True)
class ProductFormData:
    name: str
    price: str
    description: str

    @property
    def payload(self) -> dict[str, str | None]:
        return {
            "name": self.name,
            "price": self.price,
            "description": self.description or None,
        }


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


def _read_product_form() -> ProductFormData:
    return ProductFormData(
        name=request.form.get("name", "").strip(),
        price=request.form.get("price", "").strip(),
        description=request.form.get("description", "").strip(),
    )


def _persist_product(data: ProductCreate) -> str | None:
    product: Product = Product()
    product.name = data.name
    product.price = data.price
    product.description = data.description
    db.session.add(instance=product)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Error while saving product to database")
        return "Could not save the product. Please try again."
    return None


@main_bp.route(rule="/", methods=["GET"])
def index() -> str:
    return render_template(
        template_name_or_list="base.html", page_title="Home"
    )


@main_bp.route(rule="/health", methods=["GET"])
def health() -> ResponseReturnValue:
    return "OK", 200


@main_bp.route("/products/new", methods=["GET", "POST"])
def new_product() -> ResponseReturnValue:
    if request.method != "POST":
        return _render_new_product(
            form_name="",
            form_price="",
            form_description="",
            errors=None,
        )

    form = _read_product_form()

    try:
        data: ProductCreate = ProductCreate.model_validate(form.payload)
    except ValidationError as exc:
        return _render_new_product(
            form_name=form.name,
            form_price=form.price,
            form_description=form.description,
            errors=exc.errors(),
        )

    db_error_msg = _persist_product(data)
    if db_error_msg is not None:
        db_errors: list[ErrorDetails] = [
            {
                "type": "database_error",
                "loc": (),
                "msg": db_error_msg,
                "input": None,
            }
        ]
        return _render_new_product(
            form_name=data.name,
            form_price=str(data.price),
            form_description=data.description or "",
            errors=db_errors,
        )

    flash(message="Product created.", category="success")
    return redirect(location=url_for(endpoint="main.index"))
