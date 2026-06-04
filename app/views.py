from enum import Enum, StrEnum
from http import HTTPStatus

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
    count_products,
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
    PERSISTENCE_FAILURE = "Product persistence failure"


class HealthResponse(StrEnum):
    OK = "OK"


class PaginationParams(Enum):
    PAGE = 1
    PER_PAGE = 10
    MAX_PER_PAGE = 10


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
        with db.session_scope():
            create_product(data)
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
    page = request.args.get("page", type=int)
    if page is None or page < 1:
        page = PaginationParams.PAGE.value
    per_page = PaginationParams.PER_PAGE.value

    with db.session_scope():
        total = count_products()
        total_pages = (total + per_page - 1) // per_page if total else 0
        if total_pages and page > total_pages:
            page = total_pages
        products = list_products_service(page=page, per_page=per_page)

    has_prev = page > 1
    has_next = page < total_pages
    return render_template(
        template_name_or_list=ViewTemplate.PRODUCT_LIST.value,
        page_title=PageTitle.PRODUCT_LIST.value,
        products=products,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
    )


@main_bp.route(rule="/products/<int:product_id>")
def product_detail(product_id: int) -> ResponseReturnValue:
    try:
        with db.session_scope():
            product = get_product(product_id)
    except ProductNotFoundError:
        abort(404)

    return render_template(
        template_name_or_list=ViewTemplate.PRODUCT_DETAIL.value,
        page_title=product.name,
        product=product,
    )


@main_bp.route(rule="/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int) -> ResponseReturnValue:
    try:
        with db.session_scope():
            delete_product_by_id(product_id)
    except ProductNotFoundError:
        abort(404)

    flash(message=FlashMessage.PRODUCT_DELETED.value, category="success")
    return redirect(location=url_for(endpoint="main.list_products"))


@main_bp.errorhandler(ProductPersistenceError)
def handle_product_persistence_error(
    error: ProductPersistenceError,
) -> tuple[str, int]:
    """
    Handle uncaught product persistence errors from view handlers.

    Logs the underlying failure and returns a generic 500 response body and status code
    to the client.

    Args:
        error:
            The domain-level persistence error raised during request handling.

    Returns:
        A tuple containing the error message body and the HTTP 500 status code.
    """
    current_app.logger.exception(LogMessage.PERSISTENCE_FAILURE.value)
    return str(error), HTTPStatus.INTERNAL_SERVER_ERROR
