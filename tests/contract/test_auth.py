import pytest

from app.responses import BAD_REQUEST, OK, UNAUTHORIZED
from tests.data_factory import CRAP_PASSWORD, random_email, random_password, random_text
from tests.helpers import (
    api_post, authenticate_user, check_endpoint_denied, confirm_and_login_user,
    confirm_email_token, get_email_token, register_user,
)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_login(user_data):
    """Test for login of registered user."""
    register_user(user_data)
    token = get_email_token(user_data)
    confirm_email_token(token)

    expected = [OK, BAD_REQUEST]
    for idx, data in enumerate([user_data, dict(foo='bar')]):
        authenticate_user('login', data=data, expected=expected[idx])

    for key in ['email', 'password']:
        user_data[key] = random_email() if key == 'email' else random_password()
        authenticate_user('login', data=user_data, expected=UNAUTHORIZED)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_logout(user_data):
    """Test for logout."""
    # Don't use fixture as we need a token that's been blacklisted in the database.
    register_user(user_data)
    headers = confirm_and_login_user(user_data)

    expected = [OK, UNAUTHORIZED]  # Second iteration, token is blacklisted
    for idx, header in enumerate([headers, headers]):
        authenticate_user('logout', headers=header, expected=expected[idx])

    check_endpoint_denied('/auth/logout', method='post')


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_password_reset(user_data):
    """Test for password reset."""
    register_user(user_data)
    token = get_email_token(user_data)
    request_url = '/auth/password/reset/request'

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
    expected = [BAD_REQUEST, OK]
    for idx, password in enumerate([CRAP_PASSWORD, random_password()]):
        user_data['password'] = password
        response = api_post(f'/auth/password/reset/{token}', data=user_data)
        assert response.status_code == expected[idx]

    bad_token = random_text()
    response = api_post(f'/auth/password/reset/{bad_token}', data=user_data)
    assert response.status_code == UNAUTHORIZED

    authenticate_user('login', data=user_data)
    user_data['password'] = old_password
    authenticate_user('login', data=user_data, expected=UNAUTHORIZED)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_password_change(user_data):
    """Test for password change."""
    register_user(user_data)
    request_url = '/auth/password/change'

    response = api_post(request_url, data=user_data)
    assert response.status_code == UNAUTHORIZED

    headers = confirm_and_login_user(user_data)
    old_password = user_data.get('password')

    expected = [BAD_REQUEST, OK]
    for idx, password in enumerate([CRAP_PASSWORD, random_password()]):
        user_data['password'] = password
        response = api_post(request_url, headers=headers, data=user_data)
        assert response.status_code == expected[idx]

    authenticate_user('login', data=user_data)
    user_data['password'] = old_password
    authenticate_user('login', data=user_data, expected=UNAUTHORIZED)

    check_endpoint_denied(request_url, method='post')
