from booth.constants import GENERIC_ERROR_MESSAGE
import pytest
import requests_mock

from urllib.parse import urljoin
import json

from booth.offers_api import BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE, fetch_access_token, get_offers, register_product


TEST_URL = "http://testurl"


@pytest.mark.parametrize(
    (
        "baseurl",
        "refresh_token",
        "response_status",
        "response_text",
        "expected_error",
        "expected_token",
    ),
    (
        (
            TEST_URL,
            "rtoken",
            201,
            json.dumps({"access_token": "test_token"}),
            None,
            "test_token",
        ),
        (
            TEST_URL,
            "rtoken",
            401,
            "Bad authentication",
            BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE,
            None,
        ),
        (
            TEST_URL,
            "rtoken",
            500,
            "Server error",
            GENERIC_ERROR_MESSAGE,
            None,
        ),
    ),
)
def test_fetch_access_token(
    baseurl,
    refresh_token,
    response_status,
    response_text,
    expected_error,
    expected_token,
):
    with requests_mock.Mocker() as m:
        m.post(
            urljoin(baseurl, "/api/v1/auth"),
            request_headers={"Bearer": refresh_token},
            status_code=response_status,
            text=response_text,
        )
        error, access_token = fetch_access_token(baseurl, refresh_token)
    assert error == expected_error
    assert access_token == expected_token


@pytest.mark.parametrize(
    (
        "baseurl",
        "access_token",
        "product_id",
        "name",
        "description",
        "response_status",
        "response_text",
        "expected_error",
    ),
    (
        (
            TEST_URL,
            "test_token",
            "test_id",
            "test_name",
            "test_description",
            201,
            json.dumps({"id": "test_id"}),
            None,
        ),
        (
            TEST_URL,
            "test_token",
            "test_id",
            "test_name",
            "test_description",
            401,
            "Bad authentication",
            BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE,
        ),
        (
            TEST_URL,
            "test_token",
            "test_id",
            "test_name",
            "test_description",
            500,
            "Server error",
            GENERIC_ERROR_MESSAGE,
        ),
    ),
)
def test_register_product(
    baseurl,
    access_token,
    product_id,
    name,
    description,
    response_status,
    response_text,
    expected_error,
):
    with requests_mock.Mocker() as m:
        m.post(
            urljoin(baseurl, "/api/v1/products/register"),
            request_headers={"Bearer": access_token},
            status_code=response_status,
            text=response_text,
        )
        error = register_product(baseurl, access_token, product_id, name, description)
    assert error == expected_error


@pytest.mark.parametrize(
    (
        "baseurl",
        "access_token",
        "product_id",
        "response_status",
        "response_text",
        "expected_error",
        "expected_offers"
    ),
    (
        (
            TEST_URL,
            "test_token",
            "test_id",
            200,
            json.dumps([{"id": "test_id", "price": 100, "items_in_stock": 10}]),
            None,
            [{"id": "test_id", "price": 100, "items_in_stock": 10}]
        ),
        (
            TEST_URL,
            "test_token",
            "test_id",
            401,
            "Bad authentication",
            BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE,
            None
        ),
        (
            TEST_URL,
            "test_token",
            "test_id",
            500,
            "Server error",
            GENERIC_ERROR_MESSAGE,
            None
        ),
    ),
)
def test_get_offers(
    baseurl,
    access_token,
    product_id,
    response_status,
    response_text,
    expected_error,
    expected_offers
):
    with requests_mock.Mocker() as m:
        m.get(
            urljoin(baseurl, f"/api/v1/products/{product_id}/offers"),
            request_headers={"Bearer": access_token},
            status_code=response_status,
            text=response_text,
        )
        error, offers = get_offers(baseurl, access_token, product_id)
    assert error == expected_error
    assert offers == expected_offers
