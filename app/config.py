import os

from app.database import SQLiteFile, SQLiteMemory, Postgres


class Config:
    # It's yuck setting the SQLALCHEMY_DATABASE_URI in each sub-class but "some of those cannot be
    # modified after the engine was created so make sure to configure as early as possible and to
    # not modify them at runtime"
    # Ref: https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if SECRET_KEY is None:
        raise ValueError('Secret key has not been set')
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    DEFAULT = SQLiteFile().connection_string
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', DEFAULT)


class TestingConfig(Config):
    TESTING = True
    INTEGRATED = os.environ.get('INTEGRATION')
    DEFAULT = Postgres().connection_string if INTEGRATED else SQLiteMemory().connection_string
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', DEFAULT)


class ProductionConfig(Config):
    DEFAULT = Postgres().connection_string
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', DEFAULT)


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig,
)

key = Config.SECRET_KEY
