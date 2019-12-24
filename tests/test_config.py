import os

from flask import current_app

from app.main.config import basedir
from conftest import create_app


# FIXME: convert to single parametrised test
def test_app_is_development():
    dev_app = create_app('DevelopmentConfig')
    assert dev_app.config['SECRET_KEY'] != 'my_precious'
    assert dev_app.config['DEBUG'] is True
    assert current_app is not None
    assert (
            dev_app.config['SQLALCHEMY_DATABASE_URI'] ==
            f"sqlite:///{os.path.join(basedir, 'flask_boilerplate_main.db')}"
    )


def test_app_is_testing():
    test_app = create_app('TestingConfig')
    assert test_app.config['SECRET_KEY'] != 'my_precious'
    assert test_app.config['DEBUG'] is True
    assert current_app is not None
    assert (
            test_app.config['SQLALCHEMY_DATABASE_URI'] ==
            f"sqlite:///{os.path.join(basedir, 'flask_boilerplate_test.db')}"
    )


def test_app_is_production():
    prod_app = create_app('ProductionConfig')
    assert prod_app.config['SECRET_KEY'] != 'my_precious'
    assert prod_app.config['DEBUG'] is False
    assert current_app is not None
    # TODO: add prod DB test when real Postgres added
