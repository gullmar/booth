import json
import pytest
import requests_mock

from urllib.parse import urljoin

from booth import constants, offers, offers_api
from tests import conftest


@pytest.mark.parametrize(
    (
        "response_status",
        "response_text",
        "expected_error",
        "expected_retry",
    ),
    (
        (
            201,
            json.dumps({"access_token": "test_token"}),
            None,
            True,
        ),
        (
            401,
            "Bad authentication",
            offers_api.BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE,
            False,
        ),
        (
            500,
            "Server error",
            constants.GENERIC_ERROR_MESSAGE,
            False,
        ),
    ),
)
def test_evaluate_and_renovate_token(
    app,
    response_status,
    response_text,
    expected_error,
    expected_retry,
):
    with app.app_context():
        with requests_mock.Mocker() as m:
            m.post(
                urljoin(conftest.TEST_BASEURL, "/api/v1/auth"),
                request_headers={"Bearer": conftest.TEST_REFRESH_TOKEN},
                status_code=response_status,
                text=response_text,
            )
            error, retry = offers.evaluate_and_renovate_token(offers_api.BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE)
    assert error == expected_error
    assert retry == expected_retry