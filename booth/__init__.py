import json
import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.logger.setLevel("INFO")
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "db.sqlite"),
        OFFERS_BASEURL="",
        OFFERS_REFRESH_TOKEN="",
        OFFERS_ACCESS_TOKEN="",
        OFFERS_SYNC_INTERVAL_SECONDS="60",
    )

    if test_config is None:
        app.config.from_file("offers_access_token.json", load=json.load, silent=True)
        app.config.from_pyfile("config.py", silent=True)
        app.config.from_envvar("OFFERS_BASEURL", silent=True)
        app.config.from_envvar("OFFERS_REFRESH_TOKEN", silent=True)
        app.config.from_envvar("OFFERS_ACCESS_TOKEN", silent=True)
        app.config.from_envvar("OFFERS_SYNC_INTERVAL_SECONDS", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db, booth, scheduler

    db.init_app(app)
    app.register_blueprint(booth.bp)
    scheduler.init_app(app)

    return app
