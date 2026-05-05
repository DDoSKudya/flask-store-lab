import pytest
from decimal import Decimal
from app.services.products import (
    create_product,
    list_products,
    get_product,
    delete_product,
    ProductAlreadyExistsError,
    ProductNotFoundError,
)

from app.models import Product
from app.schemas import ProductCreate

SAMPLE_PRODUCTS: list[ProductCreate] = [
    ProductCreate(name="apple", price=Decimal("10.00"), description="desc 1"),
    ProductCreate(name="banana", price=Decimal("20.00"), description="desc 2"),
    ProductCreate(name="cherry", price=Decimal("30.00"), description="desc 3"),
]


@pytest.mark.unit
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


@pytest.mark.unit
@pytest.mark.parametrize("product", SAMPLE_PRODUCTS)
def test_create_product_raises_product_already_exists_error(product) -> None:
    create_product(product)
    with pytest.raises(ProductAlreadyExistsError):
        create_product(product)


@pytest.mark.unit
@pytest.mark.parametrize(
    "product",
    SAMPLE_PRODUCTS,
)
def test_list_products(product) -> None:
    create_product(product)
    products = list_products()
    assert any(
        p.name == product.name
        and p.price == product.price
        and p.description == product.description
        for p in products
    )


@pytest.mark.unit
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


@pytest.mark.unit
@pytest.mark.parametrize("product_id", [1000, 2000, 3000])
def test_get_product_raises_product_not_found_error(product_id) -> None:
    with pytest.raises(ProductNotFoundError):
        get_product(product_id)


@pytest.mark.unit
@pytest.mark.parametrize("product_id", [1000, 2000, 3000])
def test_delete_product_raises_product_not_found_error(product_id) -> None:
    with pytest.raises(ProductNotFoundError):
        delete_product(product_id)


@pytest.mark.unit
@pytest.mark.parametrize("product", SAMPLE_PRODUCTS)
def test_delete_product(db_session, product) -> None:
    create_product(product)
    created_row = (
        db_session.query(Product).filter(Product.name == product.name).one()
    )
    delete_product(created_row.id)
    with pytest.raises(ProductNotFoundError):
        get_product(created_row.id)
