import pytest
import requests_mock

from urllib.parse import urljoin
import json

from booth.offers_api import fetch_access_token


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
            "https://testurl",
            "rtoken",
            201,
            json.dumps({"access_token": "test_token"}),
            None,
            "test_token",
        ),
        (
            "https://testurl",
            "rtoken",
            401,
            "Bad authentication",
            "Bad authentication",
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
