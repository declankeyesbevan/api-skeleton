import pytest

from app.main import db
from manage import app
from tests.data_factory import user_attributes, user_model
from tests.helpers import register_user

NUM_USERS = 3


@pytest.fixture(scope='function')
def client():
    """Stub Flask client for component testing."""
    app.config.from_object('app.main.config.TestingConfig')
    return app.test_client()


@pytest.fixture(scope='function')
def database():
    db.create_all()
    db.session.commit()
    yield
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')
def user_data():
    """Used to create a user through the public API using a dict."""
    return user_attributes()


@pytest.fixture(scope='function')
def user_obj(user_data):
    """Used to create a user through the ORM using an object."""
    return user_model(user_data)


@pytest.fixture(scope='function')
def registered_user(client, user_data):
    return register_user(client, user_data)


@pytest.fixture(scope='function')
def number_of_users():
    return NUM_USERS


@pytest.fixture(scope='function')
def registered_users(client, user_data, number_of_users):
    users = [user_attributes() for _ in range(number_of_users)]
    for user in users:
        register_user(client, user)
    return users


@pytest.fixture(scope='function')
def database_user(user_obj):
    db.session.add(user_obj)
    db.session.commit()


@pytest.fixture(scope='function')
def auth_token(user_obj):
    return user_obj.encode_auth_token(user_obj.id)
