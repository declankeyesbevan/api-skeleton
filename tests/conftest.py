import pytest

from api_skeleton import app
from app.main import db
from tests.data_factory import user_attributes, user_model
from tests.helpers import add_to_database, register_client_user, set_up_database, tear_down_database

NUM_USERS = 3


@pytest.fixture(scope='function')
def client():
    """Stub Flask client for component testing."""
    return app.test_client()


@pytest.fixture(scope='function')
def database():
    set_up_database(db)
    yield
    tear_down_database(db)


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
    return register_client_user(client, user_data)


@pytest.fixture(scope='function')
def number_of_users():
    return NUM_USERS


@pytest.fixture(scope='function')
def registered_users(client, user_data, number_of_users):
    users = [user_attributes() for _ in range(number_of_users)]
    for user in users:
        register_client_user(client, user)
    return users


@pytest.fixture(scope='function')
def database_user(user_obj):
    add_to_database(db, user_obj)
    return user_obj


@pytest.fixture(scope='function')
def auth_token(user_obj):
    return user_obj.encode_auth_token(user_obj.id)
