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
    create_product(product)
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
    create_product(product)
    with pytest.raises(ProductAlreadyExistsError):
        create_product(product)
    db_session.rollback()


@pytest.mark.parametrize(
    "product",
    SAMPLE_PRODUCTS,
)
def test_list_products_returns_created_product(db_session, product) -> None:
    create_product(product)
    products = list_products(page=1, per_page=10)
    assert any(
        p.name == product.name
        and p.price == product.price
        and p.description == product.description
        for p in products
    )


def test_list_products_pagination_two_pages(db_session) -> None:
    create_product(
        ProductCreate(name="first", price=Decimal("10.00"), description="a")
    )
    create_product(
        ProductCreate(name="second", price=Decimal("20.00"), description="b")
    )

    page1 = list_products(page=1, per_page=1)
    page2 = list_products(page=2, per_page=1)

    assert len(page1) == 1
    assert len(page2) == 1
    assert page1[0].name != page2[0].name


@pytest.mark.parametrize("product", SAMPLE_PRODUCTS)
def test_get_product(db_session, product) -> None:
    create_product(product)
    created_row = (
        db_session.query(Product).filter(Product.name == product.name).one()
    )
    current_product = get_product(created_row.id)
    assert current_product.name == product.name
    assert current_product.price == product.price
    assert current_product.description == product.description


@pytest.mark.parametrize("product_id", [1000])
def test_get_product_raises_product_not_found_error(
    db_session, product_id
) -> None:
    with pytest.raises(ProductNotFoundError):
        get_product(product_id)


@pytest.mark.parametrize("product_id", [1000])
def test_delete_product_raises_product_not_found_error(
    db_session, product_id
) -> None:
    with pytest.raises(ProductNotFoundError):
        delete_product(product_id)


@pytest.mark.parametrize("product", SAMPLE_PRODUCTS)
def test_delete_product(db_session, product) -> None:
    create_product(product)
    created_row = (
        db_session.query(Product).filter(Product.name == product.name).one()
    )
    delete_product(created_row.id)
    with pytest.raises(ProductNotFoundError):
        get_product(created_row.id)
