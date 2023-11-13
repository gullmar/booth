import os
import tempfile

import pytest
from booth import create_app
from booth.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf-8")


TEST_BASEURL = "http://testurl"
TEST_REFRESH_TOKEN = "test-refresh-token"
TEST_ACCESS_TOKEN = "test-access-token"


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
            "OFFERS_BASEURL": TEST_BASEURL,
            "OFFERS_REFRESH_TOKEN": TEST_REFRESH_TOKEN,
            "OFFERS_ACCESS_TOKEN": TEST_ACCESS_TOKEN,
        }
    )

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
