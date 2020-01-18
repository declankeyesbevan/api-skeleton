import os

import pytest

from app.responses import NOT_FOUND, OK
from tests.data_factory import random_text, user_attributes
from tests.helpers import api_get, register_api_user

api_base_url = os.environ.get('API_BASE_URL')


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_list_get_and_post():
    """Test for list of all registered users and creating a new user."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    register_api_user(user_data)

    response = api_get(f'{api_base_url}/users/')
    assert response.status_code == OK
    body = response.json()
    assert len(body) > 0
    for key in ['email', 'username']:
        assert any(item.get(key) == user_data.get(key) for item in body)
        assert not any(item.get('password') == user_data.get('password') for item in body)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_get_by_id():
    """Test for specific registered user."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    response = register_api_user(user_data)
    body = response.json()

    response = api_get(f'{api_base_url}/users/{body.get("public_id")}')
    assert response.status_code == OK
    body = response.json()
    assert 'email' and 'username' and 'public_id' in body
    assert body.get('password') is None

    fake_id = random_text()
    response = api_get(f'{api_base_url}/users/{fake_id}')
    assert response.status_code == NOT_FOUND
