import os
import logging

from flask import Flask
from cerf7.config import DefaultConfig


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    app.config.from_object(DefaultConfig)
    if test_config is None:
        app.config.from_pyfile("cerf7.cfg", silent=True)
    else:
        app.config.from_pyfile(test_config)

    # Make sure instance directory exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        app.logger.debug("/hello")
        return "Hello, Cerf7!"

    from cerf7 import db
    db.init_app(app)

    return app
