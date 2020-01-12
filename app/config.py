import os

from app.database import Postgres, SQLiteFile, SQLiteMemory


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
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', SQLiteFile().connection_string)


class TestingConfig(Config):
    TESTING = True


class NonIntegratedTestingConfig(TestingConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', SQLiteMemory().connection_string)


class IntegratedTestingConfig(TestingConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', Postgres().connection_string)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING', Postgres().connection_string)


config_by_name = {
    'dev': DevelopmentConfig,
    'test-internal': NonIntegratedTestingConfig,
    'test-external': IntegratedTestingConfig,
    'prod': ProductionConfig,
}

key = Config.SECRET_KEY
