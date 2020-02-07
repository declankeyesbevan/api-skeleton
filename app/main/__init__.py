# pylint: disable=invalid-name

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from app.config import CONFIG_BY_NAME
from app.logger import init_logging

db = SQLAlchemy()
flask_bcrypt = Bcrypt()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(CONFIG_BY_NAME[config_name])
    db.init_app(app)
    flask_bcrypt.init_app(app)
    init_logging(config_name)
    return app
