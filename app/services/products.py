from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

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


def create_product(session: Session, data: ProductCreate) -> None:
    try:
        session.add(Product(**data.model_dump(mode="python")))
        session.flush()
    except IntegrityError as exc:
        raise ProductAlreadyExistsError from exc
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc


def list_products(session: Session) -> Sequence[Product]:
    try:
        return session.scalars(
            select(Product).order_by(Product.id.desc())
        ).all()
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc


def get_product(session: Session, product_id: int) -> Product:
    try:
        product = session.get(Product, product_id)
        if product is None:
            raise ProductNotFoundError
        return product
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc


def delete_product(session: Session, product_id: int) -> None:
    try:
        product = get_product(session, product_id)
        session.delete(product)
    except SQLAlchemyError as exc:
        raise ProductPersistenceError from exc
