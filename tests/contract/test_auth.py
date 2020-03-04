import pytest

from app.responses import OK, UNAUTHORIZED
from tests.data_factory import random_email, random_password, random_text
from tests.helpers import (
    API_BASE_URL, api_post, authenticate_user, confirm_email_token, deny_endpoint, get_email_token,
    register_user,
)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_login(user_data):
    """Test for login of registered user."""
    register_user(user_data)
    token = get_email_token(user_data)
    confirm_email_token(token)

    response = authenticate_user('login', data=user_data)
    body = response.json()
    assert response.status_code == OK
    assert 'token' in body.get('data')

    for key in ['email', 'password']:
        user_data[key] = random_email() if key == 'email' else random_password()
        response = authenticate_user('login', data=user_data, expected=UNAUTHORIZED)
        assert response.status_code == UNAUTHORIZED


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_logout(user_data):
    """Test for logout."""
    register_user(user_data)
    token = get_email_token(user_data)
    confirm_email_token(token)

    # Don't use fixture as we need a token that's been blacklisted in the database.
    response = authenticate_user('login', data=user_data)
    data = response.json().get('data')
    headers = dict(Authorization=f"Bearer {data.get('token')}")

    endpoint = f'{API_BASE_URL}/auth/logout'
    expected = [OK, UNAUTHORIZED]  # Second iteration, token is blacklisted
    for idx, header in enumerate([headers, headers]):
        response = authenticate_user('logout', headers=headers, expected=expected[idx])
        assert response.status_code == expected[idx]

    deny_endpoint(endpoint, method='post')


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_password_reset(user_data):
    """Test for password reset."""
    register_user(user_data)
    token = get_email_token(user_data)
    request_url = f'{API_BASE_URL}/auth/reset/request'

    response = api_post(request_url, data=user_data)
    assert response.status_code == UNAUTHORIZED

    confirm_email_token(token)
    old_email = user_data.get('email')
    old_password = user_data.get('password')

    response = api_post(request_url, data=user_data)
    assert response.status_code == OK
    user_data['email'] = random_email()
    response = api_post(request_url, data=user_data)
    assert response.status_code == UNAUTHORIZED
    user_data['email'] = old_email

    token = get_email_token(user_data)
    user_data['password'] = random_password()
    response = api_post(f'{API_BASE_URL}/auth/reset/{token}', data=user_data)
    assert response.status_code == OK

    bad_token = random_text()
    response = api_post(f'{API_BASE_URL}/auth/reset/{bad_token}', data=user_data)
    assert response.status_code == UNAUTHORIZED

    authenticate_user('login', data=user_data)
    user_data['password'] = old_password
    authenticate_user('login', data=user_data, expected=UNAUTHORIZED)
