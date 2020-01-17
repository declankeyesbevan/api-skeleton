import dataclasses
import os

from app.database import Postgres, SQLiteFile, SQLiteMemory

# pylint: disable=invalid-name


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
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@dataclasses.dataclass(frozen=True)
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', SQLiteFile().connection_string)


@dataclasses.dataclass(frozen=True)
class TestingConfig(Config):
    TESTING = True


@dataclasses.dataclass(frozen=True)
class NonIntegratedTestingConfig(TestingConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', SQLiteMemory().connection_string)


@dataclasses.dataclass(frozen=True)
class IntegratedTestingConfig(TestingConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', Postgres().connection_string)


@dataclasses.dataclass(frozen=True)
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', Postgres().connection_string)


CONFIG_BY_NAME = {
    'dev': DevelopmentConfig,
    'test-internal': NonIntegratedTestingConfig,
    'test-external': IntegratedTestingConfig,
    'prod': ProductionConfig,
}

KEY = Config.SECRET_KEY
