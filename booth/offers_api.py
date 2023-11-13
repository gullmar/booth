import requests
from urllib.parse import quote_plus, urljoin

from booth.constants import GENERIC_ERROR_MESSAGE


BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE = "Bad authentication to offers service."


def fetch_access_token(baseurl, refresh_token):
    endpoint = "/api/v1/auth"
    headers = {"Bearer": refresh_token}
    r = requests.post(urljoin(baseurl, endpoint), headers=headers)
    error: str | None = None
    access_token: str | None = None
    match r.status_code:
        case 201:
            access_token = r.json()["access_token"]
        case 401:
            error = BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE
        case _:
            error = GENERIC_ERROR_MESSAGE
    return error, access_token


def register_product(baseurl, access_token, product_id, name, description):
    endpoint = "/api/v1/products/register"
    headers = {"Bearer": access_token}
    data = {"id": product_id, "name": name, "description": description}
    r = requests.post(urljoin(baseurl, endpoint), headers=headers, data=data)
    error = None
    match r.status_code:
        case 201:
            pass
        case 401:
            error = BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE
        case _:
            error = GENERIC_ERROR_MESSAGE
    return error


def get_offers(baseurl, access_token, product_id):
    endpoint = f"/api/v1/products/{quote_plus(product_id)}/offers"
    headers = {"Bearer": access_token}
    r = requests.get(urljoin(baseurl, endpoint), headers=headers)
    error: str | None = None
    offers: list[dict[str, str]] | None = None
    match r.status_code:
        case 200:
            offers = r.json()
        case 401:
            error = BAD_OFFERS_AUTHENTICATION_ERROR_MESSAGE
        case _:
            error = GENERIC_ERROR_MESSAGE
    return error, offers
