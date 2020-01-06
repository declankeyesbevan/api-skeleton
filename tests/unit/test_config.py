import os

import pytest

from app.config import DevelopmentConfig, ProductionConfig, TestingConfig, basedir

sqlite_file_uri = f'sqlite:///{os.path.join(basedir, "api-skeleton-dev.db")}'
sqlite_memory_uri = 'sqlite:///:memory:'
postgres_database_uri = 'postgresql+psycopg2://test:password@localhost:5432/example'


@pytest.mark.parametrize('config, database_uri, debug, testing', [
    (DevelopmentConfig, sqlite_file_uri, True, False),
    (TestingConfig, sqlite_memory_uri, False, True),
    (ProductionConfig, postgres_database_uri, False, False),
])
def test_app_is_correct_env(config, database_uri, debug, testing):
    assert config.SQLALCHEMY_DATABASE_URI == database_uri
    assert config.SECRET_KEY
    assert config.DEBUG is debug
    assert config.TESTING is testing
