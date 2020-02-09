# pylint: disable=invalid-name, method-hidden

from flask import Flask, current_app, request
from flask._compat import text_type
from flask.json import JSONEncoder as BaseEncoder
from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from speaklater import _LazyString

from app.config import CONFIG_BY_NAME
from app.logger import init_logging

db = SQLAlchemy()
flask_bcrypt = Bcrypt()
babel = Babel()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(CONFIG_BY_NAME[config_name])
    db.init_app(app)
    flask_bcrypt.init_app(app)
    babel.init_app(app)
    app.json_encoder = JSONEncoder
    init_logging(config_name)
    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


class JSONEncoder(BaseEncoder):
    def default(self, o):
        if isinstance(o, _LazyString):
            return text_type(o)

        return BaseEncoder.default(self, o)
