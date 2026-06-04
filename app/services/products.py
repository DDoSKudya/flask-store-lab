from collections.abc import Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models import Product
from app.schemas import ProductCreate


class ProductServiceError(Exception):
    default_message = "Product service error."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or type(self).default_message)


class ProductAlreadyExistsError(ProductServiceError):
    default_message = "Product with this name already exists."


class ProductNotFoundError(ProductServiceError):
    default_message = "Product not found."


class ProductPersistenceError(ProductServiceError):
    default_message = "Could not save the product. Please try again."


def count_products() -> int:
    """
    Count all products stored in the database.

    Executes an aggregate query and returns zero when no products exist.

    Returns:
        The total number of products currently persisted.

    Raises:
        ProductPersistenceError:
            If a database error occurs while executing the count query.
    """
    try:
        return db.session.scalar(select(func.count()).select_from(Product)) or 0
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc


def create_product(data: ProductCreate) -> None:
    """
    Validate and persist a new product record.

    Transforms the validated payload into a model instance and flushes it to the
    database.

    Args:
        data:
            Validated product creation payload containing the product attributes.

    Raises:
        ProductAlreadyExistsError:
            If a product with the same unique attributes already exists.
        ProductPersistenceError:
            If a database error occurs during insertion or flushing.
    """
    try:
        db.session.add(Product(**data.model_dump(mode="python")))
        db.session.flush()
    except IntegrityError as exc:
        raise ProductAlreadyExistsError from exc
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc


def list_products(page: int, per_page: int) -> Sequence[Product]:
    """
    Retrieve a paginated slice of products ordered by newest first.

    Computes a bounded page window and returns the products whose row numbers fall
    within that window.

    Args:
        page:
            One-based page index used to compute the lower bound of the row window.
        per_page:
            Maximum number of products per page; constrained to the range 1–10.

    Returns:
        A sequence of products for the requested page, ordered by descending ID.

    Raises:
        ProductPersistenceError:
            If a database error occurs while executing the pagination query.
    """
    try:
        page = max(page, 1)
        per_page = min(max(per_page, 1), 10)
        row_start = (page - 1) * per_page + 1
        row_end = page * per_page
        numbered = (
            select(
                Product.id,
                func.row_number().over(order_by=Product.id.desc()).label("rn"),
            )
        ).subquery()
        stmt = (
            select(Product)
            .join(numbered, Product.id == numbered.c.id)
            .where(numbered.c.rn.between(row_start, row_end))
            .order_by(Product.id.desc())
        )
        return db.session.scalars(stmt).all()
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc


def get_product(product_id: int) -> Product:
    """
    Retrieve a single product by its identifier.

    Looks up the product in the database and maps missing records to a domain not-found
    error.

    Args:
        product_id:
            Identifier of the product to retrieve.

    Returns:
        The matching product instance loaded from the database.

    Raises:
        ProductNotFoundError:
            If no product exists for the given identifier.
        ProductPersistenceError:
            If a database error occurs while fetching the product.
    """
    try:
        product = db.session.get(Product, product_id)
        if product is None:
            raise ProductNotFoundError
        return product
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc


def delete_product(product_id: int) -> None:
    """
    Delete a single product by its identifier.

    Removes the matching product from persistent storage and reports when no record was
    affected.

    Args:
        product_id:
            Identifier of the product to delete.

    Raises:
        ProductNotFoundError:
            If no product exists for the given identifier.
        ProductPersistenceError:
            If a database error occurs while executing the delete operation.
    """
    try:
        deleted_id = db.session.scalar(delete(Product).where(Product.id == product_id).returning(Product.id))
        db.session.flush()
        if deleted_id is None:
            raise ProductNotFoundError
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc
