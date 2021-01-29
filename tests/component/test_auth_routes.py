import pytest

from app.responses import BAD_REQUEST, OK, UNAUTHORIZED
from tests.data_factory import CRAP_PASSWORD, random_email, random_password, random_text
from tests.helpers import (
    authenticate_user, check_endpoint_denied, client_post, confirm_and_login_user,
    confirm_email_token, get_email_token, register_user,
)


@pytest.mark.usefixtures('database')
def test_user_login(client, user_data):
    """Test for login of registered user."""
    with client:
        register_user(user_data, client=client)
        token = get_email_token(user_data)
        confirm_email_token(token, client=client)

        expected = [OK, BAD_REQUEST]
        for idx, data in enumerate([user_data, dict(foo='bar')]):
            authenticate_user('login', data=data, expected=expected[idx], client=client)

        for key in ['email', 'password']:
            user_data[key] = random_email() if key == 'email' else random_password()
            authenticate_user('login', data=user_data, expected=UNAUTHORIZED, client=client)


@pytest.mark.usefixtures('database')
def test_user_logout(client, user_data):
    """Test for logout."""
    with client:
        # Don't use fixture as we need a token that's been blacklisted in the database.
        register_user(user_data, client=client)
        headers = confirm_and_login_user(user_data, client=client)

        expected = [OK, UNAUTHORIZED]  # Second iteration, token is blacklisted
        for idx, header in enumerate([headers, headers]):
            authenticate_user('logout', headers=header, expected=expected[idx], client=client)

        check_endpoint_denied('/auth/logout', method='post', client=client)


@pytest.mark.usefixtures('database')
def test_password_reset(client, user_data):
    """Test for password reset."""
    with client:
        register_user(user_data, client=client)
        token = get_email_token(user_data)
        request_url = '/auth/password/reset/request'

        response = client_post(client, request_url, data=user_data)
        assert response.status_code == UNAUTHORIZED

        confirm_email_token(token, client=client)
        old_email = user_data.get('email')
        old_password = user_data.get('password')

        response = client_post(client, request_url, data=user_data)
        assert response.status_code == OK
        user_data['email'] = random_email()
        response = client_post(client, request_url, data=user_data)
        assert response.status_code == UNAUTHORIZED
        user_data['email'] = old_email

        token = get_email_token(user_data)
        expected = [BAD_REQUEST, OK]
        for idx, password in enumerate([CRAP_PASSWORD, random_password()]):
            user_data['password'] = password
            response = client_post(client, f'/auth/password/reset/{token}', data=user_data)
            assert response.status_code == expected[idx]

        bad_token = random_text()
        response = client_post(client, f'/auth/password/reset/{bad_token}', data=user_data)
        assert response.status_code == UNAUTHORIZED

        authenticate_user('login', data=user_data, client=client)
        user_data['password'] = old_password
        authenticate_user('login', data=user_data, expected=UNAUTHORIZED, client=client)


@pytest.mark.usefixtures('database')
def test_password_change(client, user_data):
    """Test for password change."""
    with client:
        register_user(user_data, client=client)
        request_url = '/auth/password/change'

        response = client_post(client, request_url, data=user_data)
        assert response.status_code == UNAUTHORIZED

        headers = confirm_and_login_user(user_data, client=client)
        old_password = user_data.get('password')

        expected = [BAD_REQUEST, OK]
        for idx, password in enumerate([CRAP_PASSWORD, random_password()]):
            user_data['password'] = password
            response = client_post(client, request_url, headers=headers, data=user_data)
            assert response.status_code == expected[idx]

        authenticate_user('login', data=user_data, client=client)
        user_data['password'] = old_password
        authenticate_user('login', data=user_data, expected=UNAUTHORIZED, client=client)

        check_endpoint_denied(request_url, method='post', client=client)
