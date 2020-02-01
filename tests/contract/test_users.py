import pytest

from app.responses import NOT_FOUND, OK
from tests.data_factory import random_text, user_attributes
from tests.helpers import API_BASE_URL, api_get, register_api_user


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_list_get_and_post():
    """Test for list of all registered users and creating a new user."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    register_api_user(user_data)

    response = api_get(f'{API_BASE_URL}/users')
    assert response.status_code == OK
    body = response.json().get('data')
    users = body.get('users')
    assert len(users) > 0
    for key in ['email', 'username']:
        assert any(item.get(key) == user_data.get(key) for item in users)
        assert not any('password' in item for item in users)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_get_by_id():
    """Test for specific registered user."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    response = register_api_user(user_data)
    data = response.json().get('data')
    user = data.get('user')

    response = api_get(f'{API_BASE_URL}/users/{user.get("public_id")}')
    assert response.status_code == OK
    data = response.json().get('data')
    user = data.get('user')
    assert 'email' and 'username' and 'public_id' in user
    assert 'password' not in user

    fake_id = random_text()
    response = api_get(f'{API_BASE_URL}/users/{fake_id}')
    assert response.status_code == NOT_FOUND
