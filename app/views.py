from enum import StrEnum

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.typing import ResponseReturnValue
from pydantic import ValidationError

from app.extensions import db
from app.schemas import ProductCreate
from app.services.products import (
    ProductAlreadyExistsError,
    ProductNotFoundError,
    ProductPersistenceError,
    create_product,
    get_product,
)
from app.services.products import (
    delete_product as delete_product_by_id,
)
from app.services.products import (
    list_products as list_products_service,
)


class ViewTemplate(StrEnum):
    HOME = "base.html"
    PRODUCT_NEW = "products/new.html"
    PRODUCT_LIST = "products/list.html"
    PRODUCT_DETAIL = "products/detail.html"


class PageTitle(StrEnum):
    HOME = "Home"
    PRODUCT_NEW = "New product"
    PRODUCT_LIST = "Products"


class FlashMessage(StrEnum):
    PRODUCT_CREATED = "Product created."
    PRODUCT_DELETED = "Product deleted."


class LogMessage(StrEnum):
    SAVE_PRODUCT = "Error while saving product to database"
    FETCH_PRODUCTS = "Error while fetching products from database"
    FETCH_PRODUCT = "Error while fetching product from database"
    DELETE_PRODUCT = "Error while deleting product from database"


class HealthResponse(StrEnum):
    OK = "OK"


main_bp: Blueprint = Blueprint(name="main", import_name=__name__)


@main_bp.route(rule="/")
def index() -> str:
    return render_template(
        template_name_or_list=ViewTemplate.HOME.value,
        page_title=PageTitle.HOME.value,
    )


@main_bp.route(rule="/health")
def health() -> ResponseReturnValue:
    return HealthResponse.OK.value, 200


@main_bp.route("/products/new", methods=["GET"])
def new_product() -> ResponseReturnValue:
    return render_template(
        ViewTemplate.PRODUCT_NEW.value,
        page_title=PageTitle.PRODUCT_NEW.value,
        errors=None,
        db_error=None,
    )


@main_bp.route("/products", methods=["POST"])
def create_product_handler() -> ResponseReturnValue:
    try:
        data = ProductCreate.model_validate(request.form)
    except ValidationError as exc:
        return render_template(
            ViewTemplate.PRODUCT_NEW.value,
            page_title=PageTitle.PRODUCT_NEW.value,
            errors=exc.errors(),
            db_error=None,
            **request.form,
        )

    try:
        with db.session_scope() as session:
            create_product(session, data)
        flash(message=FlashMessage.PRODUCT_CREATED.value, category="success")
        return redirect(location=url_for(endpoint="main.list_products"))
    except ProductAlreadyExistsError as exc:
        return render_template(
            ViewTemplate.PRODUCT_NEW.value,
            page_title=PageTitle.PRODUCT_NEW.value,
            errors=None,
            db_error=str(exc),
            **request.form,
        )
    except ProductPersistenceError as exc:
        current_app.logger.exception(LogMessage.SAVE_PRODUCT.value)
        return render_template(
            ViewTemplate.PRODUCT_NEW.value,
            page_title=PageTitle.PRODUCT_NEW.value,
            errors=None,
            db_error=str(exc),
            **request.form,
        )


@main_bp.route(rule="/products")
def list_products() -> ResponseReturnValue:
    try:
        with db.session_scope() as session:
            products = list_products_service(session)
        return render_template(
            template_name_or_list=ViewTemplate.PRODUCT_LIST.value,
            page_title=PageTitle.PRODUCT_LIST.value,
            products=products,
        )
    except ProductPersistenceError:
        current_app.logger.exception(LogMessage.FETCH_PRODUCTS.value)
        abort(500)


@main_bp.route(rule="/products/<int:product_id>")
def product_detail(product_id: int) -> ResponseReturnValue:
    try:
        with db.session_scope() as session:
            product = get_product(session, product_id)
        return render_template(
            template_name_or_list=ViewTemplate.PRODUCT_DETAIL.value,
            page_title=product.name,
            product=product,
        )
    except ProductNotFoundError:
        abort(404)
    except ProductPersistenceError:
        current_app.logger.exception(LogMessage.FETCH_PRODUCT.value)
        abort(500)


@main_bp.route(rule="/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int) -> ResponseReturnValue:
    try:
        with db.session_scope() as session:
            delete_product_by_id(session, product_id)
        flash(message=FlashMessage.PRODUCT_DELETED.value, category="success")
        return redirect(location=url_for(endpoint="main.list_products"))
    except ProductNotFoundError:
        abort(404)
    except ProductPersistenceError:
        current_app.logger.exception(LogMessage.DELETE_PRODUCT.value)
        abort(500)
