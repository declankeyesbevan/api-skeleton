# pylint: disable=invalid-name, too-many-instance-attributes, missing-class-docstring

"""
Classes used to configure the Flask app for various environments. A base class is used to set common
variables while all further environments inherit from this. There are standard and testing
configurations. The correct configuration is accessed by passing the environment name to the
CONFIG_BY_NAME constant dictionary.
"""

import dataclasses
import datetime
import os
from distutils import util

from app.database import Postgres, SQLiteFile, SQLiteMemory

BASEDIR = os.path.abspath(os.path.dirname(__file__))


@dataclasses.dataclass(frozen=True)
class Config:
    # It's yuck setting the SQLALCHEMY_DATABASE_URI in each sub-class but "some of those cannot be
    # modified after the engine was created so make sure to configure as early as possible and to
    # not modify them at runtime".
    # Ref: https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
    # Also, all of these CONSTANT style definitions must be defined as such as
    # Flask/Flask-SQLAlchemy expects them: convention over configuration. So don't touch 'em, eh?

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if SECRET_KEY is None:
        raise ValueError('Secret key has not been set')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if JWT_SECRET_KEY is None:
        raise ValueError('JWT secret key has not been set')
    EMAIL_CONFIRMATION_SALT = os.environ.get('EMAIL_CONFIRMATION_SALT')
    if EMAIL_CONFIRMATION_SALT is None:
        raise ValueError('Email confirmation salt has not been set')
    PASSWORD_RESET_SALT = os.environ.get('PASSWORD_RESET_SALT')
    if PASSWORD_RESET_SALT is None:
        raise ValueError('Password reset salt has not been set')
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PREFERRED_URL_SCHEME = os.environ.get('HTTP_PROTOCOL', 'http')
    SERVER_NAME = os.environ.get('SERVER_NAME')
    RESTX_MASK_SWAGGER = False
    RESTX_VALIDATE = True
    ERROR_INCLUDE_MESSAGE = False
    BABEL_TRANSLATION_DIRECTORIES = f'{BASEDIR}/i18n/translations'
    LANGUAGES = ['en', 'en_AU']
    JWT_EXPIRES = datetime.timedelta(days=1)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMIN = os.environ.get('ADMIN_EMAIL')


@dataclasses.dataclass(frozen=True)
class DevelopmentConfig(Config):
    PROPAGATE_EXCEPTIONS = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', SQLiteFile().connection_string)


@dataclasses.dataclass(frozen=True)
class TestingConfig(Config):
    PROPAGATE_EXCEPTIONS = False
    TESTING = True


@dataclasses.dataclass(frozen=True)
class InMemoryTestingConfig(TestingConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', SQLiteMemory().connection_string)


@dataclasses.dataclass(frozen=True)
class DeployedTestingConfig(TestingConfig):
    # Non-Flask var to allow running the integrated tests locally for debugging purposes.
    LOCAL = os.environ.get('LOCAL') and bool(util.strtobool(os.environ.get('LOCAL')))

    # Back to Flask vars.
    PREFERRED_URL_SCHEME = 'http' if LOCAL else 'https'
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', Postgres().connection_string)


@dataclasses.dataclass(frozen=True)
class ProductionConfig(Config):
    PREFERRED_URL_SCHEME = 'https'
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', Postgres().connection_string)


CONFIG_BY_NAME = {
    'dev': DevelopmentConfig,
    'test-in-memory': InMemoryTestingConfig,
    'test-deployed': DeployedTestingConfig,
    'prod': ProductionConfig,
}

KEY = Config.SECRET_KEY
