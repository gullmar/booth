import requests
from urllib.parse import quote_plus, urljoin


def fetch_access_token(baseurl, refresh_token):
    endpoint = '/api/v1/auth'
    headers = {'Bearer': refresh_token}
    r = requests.post(urljoin(baseurl, endpoint), headers=headers)
    error: str | None = None
    access_token: str | None = None
    if r.status_code == 201:
        access_token = r.json()['access_token']
    else:
        error = r.text
    return error, access_token


def register_product(baseurl, access_token, id, name, description):
    endpoint = '/api/v1/products/register'
    headers = {'Bearer': access_token}
    data = {'id': id, 'name': name, 'description': description}
    r = requests.post(urljoin(baseurl, endpoint), headers=headers, data=data)
    error = None
    if r.status_code != 201:
        error = r.text
    return error


def get_offers(baseurl, access_token, id):
    endpoint = f'/api/v1/products/{quote_plus(id)}/offers'
    headers = {'Bearer': access_token}
    r = requests.get(urljoin(baseurl, endpoint), headers=headers)
    error: str | None = None
    offers: list[dict[str, str]] | None = None
    if r.status_code == 200:
        offers = r.json()
    else:
        error = r.text
    return error, offers
