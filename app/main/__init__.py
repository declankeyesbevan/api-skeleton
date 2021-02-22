# pylint: disable=invalid-name, method-hidden

"""
Initialisation module for Flask. Creates a Flask application and initialises a number of extensions
such as SQLAlchemy and Bcrypt. Defines a number functions which adjust certain Flask behaviours. For
example how to handle specific values when converting to JSON.
"""

import datetime

from flask import current_app, Flask, request
from flask._compat import text_type
from flask.json import JSONEncoder as BaseEncoder
from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_simple import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from speaklater import _LazyString

from app.config import CONFIG_BY_NAME
from app.logger import init_logging

db = SQLAlchemy()
jwt = JWTManager()
flask_bcrypt = Bcrypt()
babel = Babel()
mail = Mail()


def create_app(config_name):
    """
    Creates a Flask app based on the environment name passed to it. For example dev or prod.
    Initialises a number of Flask extensions.
    :param config_name: string containing the config to load
    :return: initialised Flask application
    """
    app = Flask(__name__)
    app.config.from_object(CONFIG_BY_NAME[config_name])
    db.init_app(app)
    jwt.init_app(app)
    flask_bcrypt.init_app(app)
    babel.init_app(app)
    app.json_encoder = JSONEncoder
    init_logging(config_name)
    mail.init_app(app)
    CORS(app)
    return app


@jwt.jwt_data_loader
def add_claims_to_access_token(identity):
    """
    Uses a decorator in Flask JWT Simple to override existing claims on a JWT token. This is
    necessary to update a user role from standard to admin. The process is not additive so all
    values must be set again.
    https://flask-jwt-simple.readthedocs.io/en/latest/change_jwt_claims.html
    :param identity: SQLAlchemy model representing a user object
    :return: dict with updated JWT claims
    """
    roles = 'user'
    if identity.admin:
        roles = 'admin'

    now = datetime.datetime.utcnow()
    return {
        'exp': now + current_app.config['JWT_EXPIRES'],
        'iat': now,
        'nbf': now,
        'sub': identity.public_id,
        'roles': roles
    }


@babel.localeselector
def get_locale():
    """
    Attempts to match the user's language based on supported configurations. The header
    'Accept-Language' is compared with what the app supports. In this case, it only supports and
    defaults to Australian English. Other languages can be added using Babel per the existing
    application layout.
    https://flask-babel.tkte.ch/#configuration
    :return: String of supported locale or None
    """
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


class JSONEncoder(BaseEncoder):
    """
    Overrides the default Flask JSON encoder. When creating strings for Babel to localise, we use
    the speaklater package to create lazy strings. This allows setting a default string value in
    app.main.base.py which can then be changed to another language using Babel. The lazy string only
    appears to be a real string so when attempting to marshall it to JSON it will fail. This casts
    to a real string first.
    https://pypi.org/project/speaklater/
    """
    def default(self, o):
        """
        If a speaklater lazy string is passed, casts to a unicode string.
        :param o: speaklater._LazyString object
        :return: a serialisable object for o
        """
        if isinstance(o, _LazyString):
            return text_type(o)

        return BaseEncoder.default(self, o)
