import json
from urllib.parse import urljoin
import requests_mock

from booth import db, scheduler as booth_scheduler

from tests import conftest


MOCK_OFFERS_A = [
    {"id": "1", "price": 100, "items_in_stock": 10},
    {"id": "2", "price": 250, "items_in_stock": 12},
]
MOCK_OFFERS_B = [
    {"id": "4", "price": 50, "items_in_stock": 2},
]


def test_sync_offer(app, scheduler):
    with app.app_context():
        with requests_mock.Mocker() as m:
            m.get(
                urljoin(conftest.TEST_BASEURL, "/api/v1/products/a/offers"),
                request_headers={"Bearer": conftest.TEST_ACCESS_TOKEN},
                status_code=200,
                text=json.dumps(MOCK_OFFERS_A),
            )
            m.get(
                urljoin(conftest.TEST_BASEURL, "/api/v1/products/b/offers"),
                request_headers={"Bearer": conftest.TEST_ACCESS_TOKEN},
                status_code=200,
                text=json.dumps(MOCK_OFFERS_B),
            )

            booth_scheduler.sync_offers(scheduler)

            _, offers_a = db.get_product_offers("a")
            assert offers_a
            assert [dict(offer) for offer in offers_a] == [
                {"id": "1", "product_id": "a", "price": 100, "items_in_stock": 10},
                {"id": "2", "product_id": "a", "price": 250, "items_in_stock": 12},
            ]
            _, offers_b = db.get_product_offers('b')
            assert offers_b
            assert [dict(offer) for offer in offers_b] == [
                {"id": "4", "product_id": "b", "price": 50, "items_in_stock": 2},
            ]
