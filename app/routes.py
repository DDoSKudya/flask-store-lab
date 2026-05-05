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

main_bp: Blueprint = Blueprint(name="main", import_name=__name__)

_HOME_TEMPLATE = "base.html"
_PRODUCT_NEW_TEMPLATE = "products/new.html"
_PRODUCT_LIST_TEMPLATE = "products/list.html"
_PRODUCT_DETAIL_TEMPLATE = "products/detail.html"
_HOME_TITLE = "Home"
_HEALTH_OK = "OK"
_PRODUCT_NEW_TITLE = "New product"
_PRODUCT_LIST_TITLE = "Products"
_FLASH_PRODUCT_CREATED = "Product created."
_FLASH_PRODUCT_DELETED = "Product deleted."
_ERROR_PRODUCT_EXISTS = "Product with this name already exists."
_ERROR_PRODUCT_SAVE_FAILED = "Could not save the product. Please try again."
_LOG_SAVE_PRODUCT_ERROR = "Error while saving product to database"
_LOG_FETCH_PRODUCTS_ERROR = "Error while fetching products from database"
_LOG_FETCH_PRODUCT_ERROR = "Error while fetching product from database"
_LOG_DELETE_PRODUCT_ERROR = "Error while deleting product from database"


@main_bp.route(rule="/")
def index() -> str:
    return render_template(
        template_name_or_list=_HOME_TEMPLATE,
        page_title=_HOME_TITLE,
    )


@main_bp.route(rule="/health")
def health() -> ResponseReturnValue:
    return _HEALTH_OK, 200


@main_bp.route("/products/new", methods=["GET"])
def new_product() -> ResponseReturnValue:
    return render_template(
        _PRODUCT_NEW_TEMPLATE,
        page_title=_PRODUCT_NEW_TITLE,
        errors=None,
        db_error=None,
    )


@main_bp.route("/products", methods=["POST"])
def create_product_handler() -> ResponseReturnValue:
    try:
        data = ProductCreate.model_validate(request.form)
    except ValidationError as exc:
        return render_template(
            _PRODUCT_NEW_TEMPLATE,
            page_title=_PRODUCT_NEW_TITLE,
            errors=exc.errors(),
            db_error=None,
            **request.form,
        )

    try:
        create_product(data)
        flash(message=_FLASH_PRODUCT_CREATED, category="success")
        return redirect(location=url_for(endpoint="main.list_products"))
    except ProductAlreadyExistsError:
        return render_template(
            _PRODUCT_NEW_TEMPLATE,
            page_title=_PRODUCT_NEW_TITLE,
            errors=None,
            db_error=_ERROR_PRODUCT_EXISTS,
            **request.form,
        )
    except ProductPersistenceError:
        current_app.logger.exception(_LOG_SAVE_PRODUCT_ERROR)
        return render_template(
            _PRODUCT_NEW_TEMPLATE,
            page_title=_PRODUCT_NEW_TITLE,
            errors=None,
            db_error=_ERROR_PRODUCT_SAVE_FAILED,
            **request.form,
        )


@main_bp.route(rule="/products")
def list_products() -> ResponseReturnValue:
    try:
        products = list_products_service()
        return render_template(
            template_name_or_list=_PRODUCT_LIST_TEMPLATE,
            page_title=_PRODUCT_LIST_TITLE,
            products=products,
        )
    except ProductPersistenceError:
        current_app.logger.exception(_LOG_FETCH_PRODUCTS_ERROR)
        abort(500)


@main_bp.route(rule="/products/<int:product_id>")
def product_detail(product_id: int) -> ResponseReturnValue:
    try:
        product = get_product(product_id)
        return render_template(
            template_name_or_list=_PRODUCT_DETAIL_TEMPLATE,
            page_title=product.name,
            product=product,
        )
    except ProductNotFoundError:
        abort(404)
    except ProductPersistenceError:
        current_app.logger.exception(_LOG_FETCH_PRODUCT_ERROR)
        abort(500)


@main_bp.route(rule="/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int) -> ResponseReturnValue:
    try:
        delete_product_by_id(product_id)
        flash(message=_FLASH_PRODUCT_DELETED, category="success")
        return redirect(location=url_for(endpoint="main.list_products"))
    except ProductNotFoundError:
        abort(404)
    except ProductPersistenceError:
        current_app.logger.exception(_LOG_DELETE_PRODUCT_ERROR)
        abort(500)
