from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models import Product
from app.schemas import ProductCreate


class ProductServiceError(Exception):
    default_message = "Product service error."

    def __init__(self) -> None:
        super().__init__(self.default_message)


class ProductAlreadyExistsError(ProductServiceError):
    default_message = "Product with this name already exists."


class ProductNotFoundError(ProductServiceError):
    default_message = "Product not found."


class ProductPersistenceError(ProductServiceError):
    default_message = "Database operation failed."


def create_product(data: ProductCreate) -> None:
    try:
        with db.session_scope() as session:
            session.add(Product(**data.model_dump(mode="python")))
    except IntegrityError as exc:
        raise ProductAlreadyExistsError from exc
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc


def list_products() -> Sequence[Product]:
    try:
        with db.session_scope() as session:
            return session.scalars(
                select(Product).order_by(Product.id.desc())
            ).all()
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc


def get_product(product_id: int) -> Product:
    try:
        with db.session_scope() as session:
            product = session.get(Product, product_id)
            if product is None:
                raise ProductNotFoundError
            return product
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc


def delete_product(product_id: int) -> None:
    try:
        with db.session_scope() as session:
            product = session.get(Product, product_id)
            if product is None:
                raise ProductNotFoundError
            session.delete(product)
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc
