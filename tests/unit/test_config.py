import os

import pytest
from flask import current_app

from app.main.config import basedir
from manage import app

user = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')
host = os.environ.get('POSTGRES_HOST')
port = os.environ.get('POSTGRES_PORT')
database = os.environ.get('POSTGRES_DB')
sqlalchemy_database_uri = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'


@pytest.mark.parametrize('environment, database_uri, debug, testing', [
    ('Development', f'sqlite:///{os.path.join(basedir, "api-skeleton-dev.db")}', True, False),
    ('Testing', 'sqlite:///:memory:', False, True),
    ('Production', sqlalchemy_database_uri, False, False),
])
def test_app_is_correct_env(environment, database_uri, debug, testing):
    app.config.from_object(f'app.main.config.{environment}Config')
    assert app.config['SQLALCHEMY_DATABASE_URI'] == database_uri
    assert current_app is not None
    assert current_app.secret_key
    assert current_app.debug is debug
    assert current_app.testing is testing
