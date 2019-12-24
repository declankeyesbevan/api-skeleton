import pytest

from app.main import db
from manage import app


def create_app(config):
    app.config.from_object(f'app.main.config.{config}')
    return app


@pytest.fixture(scope='function')
def handle_db():
    db.create_all()
    db.session.commit()
    yield
    db.session.remove()
    db.drop_all()
