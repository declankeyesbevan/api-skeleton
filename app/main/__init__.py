# pylint: disable=invalid-name, method-hidden

from datetime import datetime

from flask import Flask, current_app, request
from flask._compat import text_type
from flask.json import JSONEncoder as BaseEncoder
from flask_babel import Babel
from flask_bcrypt import Bcrypt
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
    app = Flask(__name__)
    app.config.from_object(CONFIG_BY_NAME[config_name])
    db.init_app(app)
    jwt.init_app(app)
    flask_bcrypt.init_app(app)
    babel.init_app(app)
    app.json_encoder = JSONEncoder
    init_logging(config_name)
    mail.init_app(app)
    return app


@jwt.jwt_data_loader
def add_claims_to_access_token(identity):
    roles = 'user'
    if identity.admin:
        roles = 'admin'

    now = datetime.utcnow()
    return {
        'exp': now + current_app.config['JWT_EXPIRES'],
        'iat': now,
        'nbf': now,
        'sub': identity.public_id,
        'roles': roles
    }


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


class JSONEncoder(BaseEncoder):
    def default(self, o):
        if isinstance(o, _LazyString):
            return text_type(o)

        return BaseEncoder.default(self, o)
