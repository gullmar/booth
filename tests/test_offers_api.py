import pytest
import requests_mock

from urllib.parse import urljoin
import json

from booth import offers_api, constants
from tests import conftest


@pytest.mark.parametrize(
    (
        "response_status",
        "response_text",
        "expected_error",
        "expected_token",
    ),
    (
        (
            201,
            json.dumps({"access_token": "test_token"}),
            None,
            "test_token",
        ),
        (
            401,
            "Bad authentication",
            offers_api.BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE,
            None,
        ),
        (
            500,
            "Server error",
            constants.GENERIC_ERROR_MESSAGE,
            None,
        ),
    ),
)
def test_fetch_access_token(
    response_status,
    response_text,
    expected_error,
    expected_token,
):
    with requests_mock.Mocker() as m:
        m.post(
            urljoin(conftest.TEST_BASEURL, "/api/v1/auth"),
            request_headers={"Bearer": conftest.TEST_REFRESH_TOKEN},
            status_code=response_status,
            text=response_text,
        )
        error, access_token = offers_api.fetch_access_token(conftest.TEST_BASEURL, conftest.TEST_REFRESH_TOKEN)
    assert error == expected_error
    assert access_token == expected_token


@pytest.mark.parametrize(
    (
        "product_id",
        "name",
        "description",
        "response_status",
        "response_text",
        "expected_error",
    ),
    (
        (
            "test_id",
            "test_name",
            "test_description",
            201,
            json.dumps({"id": "test_id"}),
            None,
        ),
        (
            "test_id",
            "test_name",
            "test_description",
            401,
            "Bad authentication",
            offers_api.BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE,
        ),
        (
            "test_id",
            "test_name",
            "test_description",
            500,
            "Server error",
            constants.GENERIC_ERROR_MESSAGE,
        ),
    ),
)
def test_register_product(
    product_id,
    name,
    description,
    response_status,
    response_text,
    expected_error,
):
    with requests_mock.Mocker() as m:
        m.post(
            urljoin(conftest.TEST_BASEURL, "/api/v1/products/register"),
            request_headers={"Bearer": conftest.TEST_ACCESS_TOKEN},
            status_code=response_status,
            text=response_text,
        )
        error = offers_api.register_product(conftest.TEST_BASEURL, conftest.TEST_ACCESS_TOKEN, product_id, name, description)
    assert error == expected_error


@pytest.mark.parametrize(
    (
        "product_id",
        "response_status",
        "response_text",
        "expected_error",
        "expected_offers"
    ),
    (
        (
            "test_id",
            200,
            json.dumps([{"id": "test_id", "price": 100, "items_in_stock": 10}]),
            None,
            [{"id": "test_id", "price": 100, "items_in_stock": 10}]
        ),
        (
            "test_id",
            401,
            "Bad authentication",
            offers_api.BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE,
            None
        ),
        (
            "test_id",
            500,
            "Server error",
            constants.GENERIC_ERROR_MESSAGE,
            None
        ),
    ),
)
def test_get_offers(
    product_id,
    response_status,
    response_text,
    expected_error,
    expected_offers
):
    with requests_mock.Mocker() as m:
        m.get(
            urljoin(conftest.TEST_BASEURL, f"/api/v1/products/{product_id}/offers"),
            request_headers={"Bearer": conftest.TEST_ACCESS_TOKEN},
            status_code=response_status,
            text=response_text,
        )
        error, offers = offers_api.get_offers(conftest.TEST_BASEURL, conftest.TEST_ACCESS_TOKEN, product_id)
    assert error == expected_error
    assert offers == expected_offers
