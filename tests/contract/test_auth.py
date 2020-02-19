import pytest

from app.responses import OK, UNAUTHORIZED
from tests.data_factory import random_email, random_password
from tests.helpers import API_BASE_URL, api_post, denied_endpoint, register_user


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_login(user_data):
    """Test for login of registered user."""
    register_user(user_data)

    response = api_post(f'{API_BASE_URL}/auth/login', data=user_data)
    body = response.json()
    assert response.status_code == OK
    assert 'token' in body.get('data')

    for key in ['email', 'password']:
        user_data[key] = random_email() if key == 'email' else random_password()
        response = api_post(f'{API_BASE_URL}/auth/login', data=user_data)
        assert response.status_code == UNAUTHORIZED


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_logout(user_data):
    """Test for logout before token expires."""
    register_user(user_data)

    # Don't use fixture as we need a token that's been blacklisted in the database.
    response = api_post(f'{API_BASE_URL}/auth/login', data=user_data)
    data = response.json().get('data')
    headers = dict(Authorization=f"Bearer {data.get('token')}")

    endpoint = f'{API_BASE_URL}/auth/logout'
    expected = [OK, UNAUTHORIZED]  # Second iteration, token is blacklisted
    for idx, header in enumerate([headers, headers]):
        response = api_post(endpoint, headers=headers)
        assert response.status_code == expected[idx]

    denied_endpoint(endpoint, method='post')
