import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "db.sqlite"),
        OFFERS_BASEURL="",
        OFFERS_REFRESH_TOKEN="",
        OFFERS_ACCESS_TOKEN="",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
        app.config.from_envvar("OFFERS_BASEURL", silent=True)
        app.config.from_envvar("OFFERS_REFRESH_TOKEN", silent=True)
        app.config.from_envvar("OFFERS_ACCESS_TOKEN", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db, booth

    db.init_app(app)
    app.register_blueprint(booth.bp)

    return app
