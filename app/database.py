import dataclasses
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


@dataclasses.dataclass(frozen=True)
class Database:
    @property
    def connection_string(self):
        raise NotImplementedError('Subclasses should implement this')


@dataclasses.dataclass(frozen=True)
class SQLite(Database):
    @property
    def connection_string(self):
        return 'sqlite:///{}'


@dataclasses.dataclass(frozen=True)
class SQLiteFile(SQLite):
    @property
    def connection_string(self):
        return super().connection_string.format(os.path.join(BASEDIR, 'api-skeleton-dev.db'))


@dataclasses.dataclass(frozen=True)
class SQLiteMemory(SQLite):
    @property
    def connection_string(self):
        return super().connection_string.format(':memory:')


@dataclasses.dataclass(frozen=True)
class Postgres(Database):
    @property
    def connection_string(self):
        user = os.environ.get('POSTGRES_USER')
        password = os.environ.get('POSTGRES_PASSWORD')
        host = os.environ.get('POSTGRES_HOST')
        port = os.environ.get('POSTGRES_PORT')
        database = os.environ.get('POSTGRES_DB')
        return f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
