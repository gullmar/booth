import json
import os

from flask import Flask


def read_config_from_env(app, name):
    if name in os.environ:
        app.config.update({name: os.environ[name]})


def read_config_from_file(app, name):
    file_path = app.config[f'{name}_FILE']
    if os.path.exists(file_path):
        with open(file_path) as f:
            app.config.update({name: f.read().rstrip('\n')})


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.logger.setLevel("INFO")
    app.logger.info(os.environ)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "db.sqlite"),
        OFFERS_BASEURL="",
        OFFERS_REFRESH_TOKEN="",
        OFFERS_ACCESS_TOKEN="",
        OFFERS_SYNC_INTERVAL_SECONDS="60",
        SECRET_KEY_FILE="",
        OFFERS_REFRESH_TOKEN_FILE="",
    )

    if test_config is None:
        # Load access token from a previous session
        app.config.from_file("offers_access_token.json", load=json.load, silent=True)

        # Load variables from instance file
        app.config.from_pyfile("config.py", silent=True)

        # Load variables directly from environment
        read_config_from_env(app, "SECRET_KEY")
        read_config_from_env(app, "OFFERS_BASEURL")
        read_config_from_env(app, "OFFERS_REFRESH_TOKEN")
        read_config_from_env(app, "OFFERS_ACCESS_TOKEN")
        read_config_from_env(app, "OFFERS_SYNC_INTERVAL_SECONDS")
        read_config_from_env(app, "SECRET_KEY_FILE")
        read_config_from_env(app, "OFFERS_REFRESH_TOKEN_FILE")
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Load secrets from files
    read_config_from_file(app, "SECRET_KEY")
    read_config_from_file(app, "OFFERS_REFRESH_TOKEN")

    app.logger.info(app.config)

    from . import db, booth, scheduler

    db.init_app(app)
    app.register_blueprint(booth.bp)
    scheduler.init_app(app)

    return app
