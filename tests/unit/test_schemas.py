import pytest
from decimal import Decimal

from pydantic import ValidationError

from app.schemas import ProductCreate

SAMPLE_PRODUCTS: list[ProductCreate] = [
    ProductCreate(name="apple", price=Decimal("10.00"), description="desc 1"),
    ProductCreate(name="banana", price=Decimal("20.00"), description="desc 2"),
    ProductCreate(name="cherry", price=Decimal("30.00"), description="desc 3"),
]


@pytest.mark.unit
@pytest.mark.parametrize("product", SAMPLE_PRODUCTS)
def test_product_create_valid(product: ProductCreate) -> None:
    from_dict = ProductCreate.model_validate(product.model_dump(mode="python"))
    assert from_dict.name == product.name
    assert from_dict.price == product.price
    assert from_dict.description == product.description


@pytest.mark.unit
@pytest.mark.parametrize("product", SAMPLE_PRODUCTS)
def test_product_create_description_optional(product: ProductCreate) -> None:
    omitted = ProductCreate.model_validate(
        {"name": product.name, "price": product.price}
    )
    assert omitted.description is None


@pytest.mark.unit
@pytest.mark.parametrize("invalid_name", ["", "A"])
def test_product_create_name_length_too_short(invalid_name: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            name=invalid_name,
            price=Decimal("1.00"),
            description=None,
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("name",) for e in errors)


@pytest.mark.unit
def test_product_create_name_length_too_long() -> None:
    name = "x" * 101
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(name=name, price=Decimal("1.00"), description=None)
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("name",) for e in errors)


@pytest.mark.unit
@pytest.mark.parametrize("invalid_price", [Decimal("0"), Decimal("-1")])
def test_product_create_price_must_be_positive(invalid_price: Decimal) -> None:
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(name="Ok", price=invalid_price, description=None)
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("price",) for e in errors)


@pytest.mark.unit
@pytest.mark.parametrize("product", SAMPLE_PRODUCTS)
def test_product_create_description_too_long(product: ProductCreate) -> None:
    base = product.description or ""
    description = base + "x" * 1001
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(
            name=product.name,
            price=product.price,
            description=description,
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("description",) for e in errors)
