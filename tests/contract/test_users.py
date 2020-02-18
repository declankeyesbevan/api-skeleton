import copy

import pytest

from app.responses import BAD_REQUEST, CONFLICT, NOT_FOUND, OK
from app.utils import FIRST, SECOND, THIRD, THREE_ITEMS
from tests.data_factory import random_email, random_text, user_attributes
from tests.helpers import (API_BASE_URL, api_get, denied_api_get_endpoint, register_api_user)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_list_get(headers):
    """Test for list of all registered users."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    register_api_user(user_data)

    endpoint = f'{API_BASE_URL}/users'
    response = api_get(endpoint, headers=headers)
    assert response.status_code == OK
    body = response.json().get('data')
    users = body.get('users')
    assert len(users) > 0
    for key in ['email', 'username']:
        assert any(item.get(key) == user_data.get(key) for item in users)
        assert not any('password' in item for item in users)

    denied_api_get_endpoint(endpoint)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_list_post():
    """Test for creating a new user."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    register_api_user(user_data)

    users = [copy.copy(user_data) for _ in range(THREE_ITEMS)]

    users[FIRST]['password'] = None
    users[SECOND]['email'] = random_email()  # Must be unique username
    users[THIRD]['username'] = random_text()  # Must be unique email
    expected = [BAD_REQUEST, CONFLICT, CONFLICT]
    for idx, user in enumerate(users):
        register_api_user(user, expected=expected[idx])


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_get_by_id(headers):
    """Test for specific registered user."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    response = register_api_user(user_data)

    data = response.json().get('data')
    user = data.get('user')

    endpoint = f'{API_BASE_URL}/users/{user.get("public_id")}'
    response = api_get(endpoint, headers=headers)
    assert response.status_code == OK
    data = response.json().get('data')
    user = data.get('user')
    assert 'email' and 'username' and 'public_id' in user
    assert 'password' not in user

    fake_id = random_text()
    response = api_get(f'{API_BASE_URL}/users/{fake_id}', headers=headers)
    assert response.status_code == NOT_FOUND

    denied_api_get_endpoint(endpoint)
