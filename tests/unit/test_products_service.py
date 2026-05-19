from decimal import Decimal

import pytest

from app.models import Product
from app.schemas import ProductCreate
from app.services.products import (
    ProductAlreadyExistsError,
    ProductNotFoundError,
    create_product,
    delete_product,
    get_product,
    list_products,
)

pytestmark = pytest.mark.unit

SAMPLE_PRODUCTS: list[ProductCreate] = [
    ProductCreate(name="apple", price=Decimal("10.00"), description="desc 1")
]


@pytest.mark.parametrize(
    "product",
    SAMPLE_PRODUCTS,
)
def test_create_product(db_session, product) -> None:
    create_product(db_session, product)
    created_product = (
        db_session.query(Product).filter(Product.name == product.name).one()
    )
    assert created_product.name == product.name
    assert created_product.price == product.price
    assert created_product.description == product.description


@pytest.mark.parametrize("product", SAMPLE_PRODUCTS)
def test_create_product_raises_product_already_exists_error(
    db_session, product
) -> None:
    create_product(db_session, product)
    with pytest.raises(ProductAlreadyExistsError):
        create_product(db_session, product)


@pytest.mark.parametrize(
    "product",
    SAMPLE_PRODUCTS,
)
def test_list_products(db_session, product) -> None:
    create_product(db_session, product)
    products = list_products(db_session)
    assert any(
        p.name == product.name
        and p.price == product.price
        and p.description == product.description
        for p in products
    )


@pytest.mark.parametrize("product", SAMPLE_PRODUCTS)
def test_get_product(db_session, product) -> None:
    create_product(db_session, product)
    created_row = (
        db_session.query(Product).filter(Product.name == product.name).one()
    )
    current_product = get_product(db_session, created_row.id)
    assert current_product.name == product.name
    assert current_product.price == product.price
    assert current_product.description == product.description


@pytest.mark.parametrize("product_id", [1000])
def test_get_product_raises_product_not_found_error(
    db_session, product_id
) -> None:
    with pytest.raises(ProductNotFoundError):
        get_product(db_session, product_id)


@pytest.mark.parametrize("product_id", [1000])
def test_delete_product_raises_product_not_found_error(
    db_session, product_id
) -> None:
    with pytest.raises(ProductNotFoundError):
        delete_product(db_session, product_id)


@pytest.mark.parametrize("product", SAMPLE_PRODUCTS)
def test_delete_product(db_session, product) -> None:
    create_product(db_session, product)
    created_row = (
        db_session.query(Product).filter(Product.name == product.name).one()
    )
    delete_product(db_session, created_row.id)
    with pytest.raises(ProductNotFoundError):
        get_product(db_session, created_row.id)
