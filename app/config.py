import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Database:
    connection_string = None


class SQLite(Database):
    connection_string = 'sqlite:///{}'


class SQLiteFile(SQLite):
    connection_string = SQLite.connection_string.format(
        os.path.join(basedir, 'api-skeleton-dev.db')
    )


class SQLiteMemory(SQLite):
    connection_string = SQLite.connection_string.format(':memory:')


class Postgres(Database):
    user = os.environ.get('POSTGRES_USER')
    password = os.environ.get('POSTGRES_PASSWORD')
    host = os.environ.get('POSTGRES_HOST')
    port = os.environ.get('POSTGRES_PORT')
    database = os.environ.get('POSTGRES_DB')

    connection_string = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    if SECRET_KEY is None:
        raise ValueError
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = SQLiteFile.connection_string


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        Postgres.connection_string if os.environ.get('INTEGRATION') else
        SQLiteMemory.connection_string
    )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = Postgres.connection_string


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig,
)

key = Config.SECRET_KEY
