import pytest


HTTP_OK = 200
HTTP_REDIRECT = 302
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500


@pytest.mark.integration
def test_connect_to_index(client) -> None:
    response = client.get("/")
    response_text = response.get_data(as_text=True)
    assert response.status_code == HTTP_OK
    assert "<title>Home</title>" in response_text
    assert "flask-store-lab" in response_text


@pytest.mark.integration
def test_connect_to_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == HTTP_OK
    assert response.get_data(as_text=True) == "OK"


@pytest.mark.integration
def test_connect_to_new_product(client) -> None:
    response = client.get("/products/new")
    response_text = response.get_data(as_text=True)
    assert response.status_code == HTTP_OK
    assert "<title>New product</title>" in response_text
    assert 'name="name"' in response_text
    assert 'name="price"' in response_text


@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        {"name": "apple", "price": "10.00"},
        {"name": "banana", "price": "20.00"},
        {
            "name": "cherry",
            "price": "30.00",
            "description": "A small, sweet fruit",
        },
    ],
)
def test_create_product_redirects_on_success(client, data) -> None:
    response = client.post("/products", data=data, follow_redirects=True)
    response_text = response.get_data(as_text=True)
    assert response.status_code == HTTP_OK
    assert "<title>Products</title>" in response_text
    assert data["name"] in response_text


@pytest.mark.integration
@pytest.mark.parametrize(
    ("data", "expected_error"),
    [
        (
            {"name": "", "price": "10.00"},
            "String should have at least 2 characters",
        ),
        (
            {"name": "apple", "price": ""},
            "Input should be a valid decimal",
        ),
        (
            {"name": "apple", "price": "apple", "description": ""},
            "Input should be a valid decimal",
        ),
    ],
)
def test_create_product_with_invalid_data(
    client, data, expected_error
) -> None:
    response = client.post("/products", data=data)
    response_text = response.get_data(as_text=True)

    assert response.status_code == HTTP_OK
    assert "Please fix the following" in response_text
    assert expected_error in response_text


@pytest.mark.integration
def test_create_product_with_duplicate_name(client) -> None:
    payload = {
        "name": "duplicate-name",
        "price": "10.00",
        "description": "first product",
    }
    first_response = client.post("/products", data=payload)
    assert first_response.status_code == HTTP_REDIRECT

    second_response = client.post("/products", data=payload)
    second_response_text = second_response.get_data(as_text=True)

    assert second_response.status_code == HTTP_OK
    assert "Product with this name already exists." in second_response_text
    assert 'value="duplicate-name"' in second_response_text


@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        {
            "name": "product 1",
            "price": "10.00",
            "description": "description 1",
        },
        {
            "name": "product 2",
            "price": "20.00",
            "description": "description 2",
        },
        {
            "name": "product 3",
            "price": "30.00",
            "description": "description 3",
        },
    ],
)
def test_get_list_products(client, data) -> None:
    client.post("/products", data=data)
    response = client.get("/products")
    response_text = response.get_data(as_text=True)
    assert response.status_code == HTTP_OK
    assert "<title>Products</title>" in response_text
    assert data["name"] in response_text


@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        {
            "name": "product 1",
            "price": "10.00",
            "description": "description 1",
        },
        {
            "name": "product 2",
            "price": "20.00",
            "description": "description 2",
        },
        {
            "name": "product 3",
            "price": "30.00",
            "description": "description 3",
        },
    ],
)
def test_get_product_detail_by_id(client, data) -> None:
    client.post("/products", data=data)
    response = client.get("/products/1")
    response_text = response.get_data(as_text=True)
    assert response.status_code == HTTP_OK
    assert f"<title>{data['name']}</title>" in response_text
    assert data["name"] in response_text
    assert data["price"] in response_text
    assert data["description"] in response_text


@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        {
            "name": "product 1",
            "price": "10.00",
            "description": "description 1",
        },
        {
            "name": "product 2",
            "price": "20.00",
            "description": "description 2",
        },
        {
            "name": "product 3",
            "price": "30.00",
            "description": "description 3",
        },
    ],
)
def test_delete_product_by_id(client, data) -> None:
    client.post("/products", data=data)
    delete_response = client.delete("/products/1")
    response = client.get("/products")
    assert delete_response.status_code == HTTP_REDIRECT
    assert (
        "You should be redirected automatically to the target URL"
        in delete_response.get_data(as_text=True)
    )
    assert data["name"] not in response.get_data(as_text=True)


@pytest.mark.integration
def test_get_product_not_found(client) -> None:
    response = client.get("/products/1")
    assert response.status_code == HTTP_NOT_FOUND
    assert "Not Found" in response.get_data(as_text=True)


@pytest.mark.integration
def test_delete_product_not_found(client) -> None:
    response = client.delete("/products/9999")
    assert response.status_code == HTTP_NOT_FOUND
    assert "Not Found" in response.get_data(as_text=True)
