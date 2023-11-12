import pytest

from booth.db import get_db


EMPTY_PRODUCT = {"id": "", "name": "", "description": ""}


def get_failing_db():
    def throw():
        raise Exception("Test error")

    return {"execute": throw}


def test_index(client, monkeypatch):
    response = client.get("/")
    assert b"Products" in response.data
    assert b"Register" in response.data

    monkeypatch.setattr("booth.db.get_db", get_failing_db)
    response = client.get("/")
    assert b"Something went wrong" in response.data


def test_register(client, app, monkeypatch):
    assert client.get("/register").status_code == 200
    client.post("/register", data={"name": "Apple", "description": "A fruit."})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM products").fetchone()[0]
        assert count == 3

    response = client.post(
        "/register", data={"name": "Onion", "description": "A vegetable?"}
    )
    assert b"Name &#34;Onion&#34; is already used by another product." in response.data

    monkeypatch.setattr("booth.db.get_db", get_failing_db)
    response = client.post(
        "/register", data={"name": "Pear", "description": "Another fruit."}
    )
    assert b"Something went wrong" in response.data


def test_edit(client, app, monkeypatch):
    assert client.get("/edit/97170a30-6550-4684-ae1e-6b31f81f2511").status_code == 200
    response = client.post(
        "/edit/97170a30-6550-4684-ae1e-6b31f81f2511",
        data={"name": "Onion", "description": "A layered vegetable."},
    )
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        product = db.execute(
            "SELECT * FROM products WHERE id = '97170a30-6550-4684-ae1e-6b31f81f2511'"
        ).fetchone()
        assert product["description"] == "A layered vegetable."

    response = client.post(
        "/edit/97170a30-6550-4684-ae1e-6b31f81f2511",
        data={"name": "Carrot", "description": "A layered vegetable."},
    )
    assert b"Name &#34;Carrot&#34; is already used by another product." in response.data

    monkeypatch.setattr("booth.db.get_db", get_failing_db)
    monkeypatch.setattr("booth.db.get_product", lambda _: (None, EMPTY_PRODUCT))
    response = client.post(
        "/edit/97170a30-6550-4684-ae1e-6b31f81f2511",
        data={"name": "Onion", "description": "A layered vegetable."},
    )
    assert b"Something went wrong" in response.data


def test_delete(client, app, monkeypatch):
    response = client.post("/delete/97170a30-6550-4684-ae1e-6b31f81f2511")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        product = db.execute(
            'SELECT * FROM products WHERE id = "97170a30-6550-4684-ae1e-6b31f81f2511"'
        ).fetchone()
        assert product is None

    monkeypatch.setattr("booth.db.get_db", get_failing_db)
    monkeypatch.setattr("booth.db.get_product", lambda _: (None, EMPTY_PRODUCT))
    response = client.post("/delete/97170a30-6550-4684-ae1e-6b31f81f2511")
    assert b"Something went wrong" in response.data


@pytest.mark.parametrize(
    "path",
    (
        "/register",
        "/edit/1562d569-8eee-4555-b991-79b32576b5b0",
    ),
)
def test_product_form_validation(client, path):
    response = client.post(path, data={"name": "", "description": "Some description."})
    assert b"Name is required." in response.data

    response = client.post(path, data={"name": "Some name", "description": ""})
    assert b"Description is required." in response.data
