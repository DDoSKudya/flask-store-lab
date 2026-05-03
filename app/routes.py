from collections.abc import Sequence
from typing import TypedDict

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


class ProductFormData(TypedDict):
    name: str
    price: str
    description: str


def _render_new_product(
    *,
    form_data: ProductFormData,
    errors: Sequence[ErrorDetails] | None,
    db_error: str | None = None,
) -> str:
    return render_template(
        _PRODUCT_NEW_TEMPLATE,
        page_title=_PRODUCT_NEW_TITLE,
        form_name=form_data["name"],
        form_price=form_data["price"],
        form_description=form_data["description"],
        errors=errors,
        db_error=db_error,
    )


def _read_product_form() -> ProductFormData:
    return {
        "name": request.form.get("name", "").strip(),
        "price": request.form.get("price", "").strip(),
        "description": request.form.get("description", "").strip(),
    }


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
            form_data={"name": "", "price": "", "description": ""},
            errors=None,
        )

    form_data = _read_product_form()
    payload: dict[str, str | None] = {
        "name": form_data["name"],
        "price": form_data["price"],
        "description": form_data["description"] or None,
    }

    try:
        data: ProductCreate = ProductCreate.model_validate(payload)
    except ValidationError as exc:
        return _render_new_product(
            form_data=form_data,
            errors=exc.errors(),
        )

    db_error_msg = _persist_product(data)
    if db_error_msg is not None:
        validated_form_data: ProductFormData = {
            "name": data.name,
            "price": str(data.price),
            "description": data.description or "",
        }
        return _render_new_product(
            form_data=validated_form_data,
            errors=None,
            db_error=db_error_msg,
        )

    flash(message="Product created.", category="success")
    return redirect(location=url_for(endpoint="main.index"))


@main_bp.route(rule="/products", methods=["GET"])
def list_products() -> ResponseReturnValue:
    products: Sequence[Product] = Product.query.order_by(
        Product.id.desc()
    ).all()
    return render_template(
        template_name_or_list="products/list.html",
        page_title="Products",
        products=products,
    )


@main_bp.route(rule="/products/<int:product_id>", methods=["GET"])
def product_detail(product_id: int) -> ResponseReturnValue:
    product: Product = db.get_or_404(entity=Product, ident=product_id)
    return render_template(
        template_name_or_list="products/detail.html",
        page_title=product.name,
        product=product,
    )


@main_bp.route(rule="/products/<int:product_id>/delete", methods=["GET"])
def delete_product(product_id: int) -> ResponseReturnValue:
    product: Product = db.get_or_404(entity=Product, ident=product_id)
    db.session.delete(instance=product)
    db.session.commit()
    flash(message="Product deleted.", category="success")
    return redirect(location=url_for(endpoint="main.list_products"))
