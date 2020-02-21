import pytest

from api_skeleton import app
from app.main import db
from tests.data_factory import user_attributes
from tests.helpers import create_header, create_user, set_up_database, tear_down_database


def pytest_addoption(parser):
    parser.addoption(
        '--runlocal', action='store_true', default=False, help='run integration tests locally'
    )


def pytest_configure(config):
    config.addinivalue_line('markers', 'local: mark integration test as local to run')


def pytest_collection_modifyitems(config, items):
    if config.getoption('--runlocal'):  # --runlocal given in cli: do not skip local tests
        return
    skip_local = pytest.mark.skip(reason='need --runlocal option to run')
    for item in items:
        if 'local' in item.keywords:
            item.add_marker(skip_local)


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
    return user_attributes()


@pytest.fixture(scope='function')
def database_user():
    return create_user(db, user_attributes())


@pytest.fixture(scope='function')
def headers():
    return create_header(db, user_attributes())


@pytest.fixture(scope='function')
def admin_headers():
    return create_header(db, user_attributes(), admin=True)
