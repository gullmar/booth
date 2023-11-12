import os

from flask import Flask

from . import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        OFFERS_REFRESH_TOKEN="",
        OFFERS_ACCESS_TOKEN=""
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
        app.config.from_envvar('OFFERS_BASEURL')
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def main():
        return "We are set-up!"

    db.init_app(app)

    return app
