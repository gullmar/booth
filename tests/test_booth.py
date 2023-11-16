import re
from urllib.parse import urljoin
import requests_mock
import pytest

from booth.db import get_db
from tests import conftest


EMPTY_PRODUCT = {"id": "", "name": "", "description": ""}


class MockUserFetcher:
    def fetchone(self):
        return {
            "id": "1",
            "username": "test",
            "password": "0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f"
        }


class FailingDB:
    def execute(self, query, _=None):
        if query == "SELECT * FROM users WHERE (username = ?)":
            return MockUserFetcher()
        raise Exception("Test error")


def throw():
    raise Exception("Test error")



def get_failing_db2():
    return FailingDB()

def get_failing_db():
    def throw():
        raise Exception("Test error")

    return {"execute": throw}


def test_index(client, auth, monkeypatch):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/")
    assert b"Log Out" in response.data
    assert b"Products" in response.data
    assert b"Register" in response.data

    auth.login()
    monkeypatch.setattr("booth.db.get_all_products", lambda: ("Test error", None))
    response = client.get("/")
    assert b"Test error" in response.data


def test_register(client, app, auth, monkeypatch):
    with requests_mock.Mocker() as m:
        monkeypatch.setattr("uuid.uuid4", lambda: "test-uuid")

        auth.login()
        m.post(
            urljoin(conftest.TEST_BASEURL, "/api/v1/products/register"),
            request_headers={"Bearer": conftest.TEST_ACCESS_TOKEN},
            status_code=201,
        )
        matcher = re.compile("/api/v1/products/.+/offers")
        auth.login()
        m.get(
            matcher,
            request_headers={"Bearer": conftest.TEST_ACCESS_TOKEN},
            status_code=200,
            text="[]"
        )

        auth.login()
        assert client.get("/register").status_code == 200
        auth.login()
        client.post("/register", data={"name": "Apple", "description": "A fruit."})

        with app.app_context():
            db = get_db()
            count = db.execute("SELECT COUNT(id) FROM products").fetchone()[0]
            assert count == 3

        auth.login()
        response = client.post(
            "/register", data={"name": "Onion", "description": "A vegetable?"}
        )
        assert (
            b"Name &#34;Onion&#34; is already used by another product." in response.data
        )

        monkeypatch.setattr("booth.db.register_product", lambda *_: ("Test error", None))
        auth.login()
        response = client.post(
            "/register", data={"name": "Pear", "description": "Another fruit."}
        )
        assert b"Test error" in response.data


def test_edit(client, app, auth, monkeypatch):
    auth.login()
    assert client.get("/a/edit").status_code == 200
    auth.login()
    response = client.post(
        "/a/edit",
        data={"name": "Onion", "description": "A layered vegetable."},
    )
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        product = db.execute(
            "SELECT * FROM products WHERE id = 'a'"
        ).fetchone()
        assert product["description"] == "A layered vegetable."

    auth.login()
    response = client.post(
        "/a/edit",
        data={"name": "Carrot", "description": "A layered vegetable."},
    )
    assert b"Name &#34;Carrot&#34; is already used by another product." in response.data

    monkeypatch.setattr("booth.db.update_product", lambda *_: "Test error")
    monkeypatch.setattr("booth.db.get_product", lambda _: (None, EMPTY_PRODUCT))
    auth.login()
    response = client.post(
        "/a/edit",
        data={"name": "Onion", "description": "A layered vegetable."},
    )
    assert b"Test error" in response.data


def test_delete(client, app, auth, monkeypatch):
    auth.login()
    response = client.post("/a/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        product = db.execute(
            'SELECT * FROM products WHERE id = "a"'
        ).fetchone()
        assert product is None

    monkeypatch.setattr("booth.db.delete_product", lambda *_: "Test error")
    monkeypatch.setattr("booth.db.get_product", lambda _: (None, EMPTY_PRODUCT))
    auth.login()
    response = client.post("/a/delete")
    assert b"Test error" in response.data


@pytest.mark.parametrize(
    "path",
    (
        "/register",
        "/b/edit",
    ),
)
def test_product_form_validation(client, path, auth):
    auth.login()
    response = client.post(path, data={"name": "", "description": "Some description."})
    assert b"Name is required." in response.data

    auth.login()
    response = client.post(path, data={"name": "Some name", "description": ""})
    assert b"Description is required." in response.data


def test_product_offers(client, auth):
    auth.login()
    response = client.get("/a/offers")
    assert response.status_code == 200
    assert b'100' in response.data
