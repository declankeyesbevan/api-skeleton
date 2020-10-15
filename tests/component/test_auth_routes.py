import json

import pytest

from app.responses import CONFLICT, OK, UNAUTHORIZED
from tests.data_factory import random_email, random_password, random_text
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
        authenticate_user('login', data=user_data, client=client)

        for key in ['email', 'password']:
            user_data[key] = random_email() if key == 'email' else random_password()
            authenticate_user('login', data=user_data, expected=UNAUTHORIZED, client=client)


@pytest.mark.usefixtures('database')
def test_user_logout(client, user_data):
    """Test for logout."""
    with client:
        # Don't use fixture as we need a token that's been blacklisted in the database.
        register_user(user_data, client=client)
        headers = confirm_and_login_user(user_data, client)

        expected = [OK, UNAUTHORIZED]  # Second iteration, token is blacklisted
        for idx, header in enumerate([headers, headers]):
            authenticate_user('logout', headers=header, expected=expected[idx], client=client)

        check_endpoint_denied('/auth/logout', method='post', client=client)


@pytest.mark.usefixtures('database')
def test_email_confirm(client, user_data):
    """Test for email confirmation."""
    with client:
        register_user(user_data, client=client)
        token = get_email_token(user_data)

        authenticate_user('login', data=user_data, expected=UNAUTHORIZED, client=client)
        confirm_email_token(token, client=client)
        authenticate_user('login', data=user_data, client=client)
        confirm_email_token(token, expected=CONFLICT, client=client)


@pytest.mark.usefixtures('database')
def test_password_reset(client, user_data):
    """Test for password reset."""
    with client:
        register_user(user_data, client=client)
        token = get_email_token(user_data)
        request_url = '/auth/reset/request'

        response = client_post(client, request_url, data=json.dumps(user_data))
        assert response.status_code == UNAUTHORIZED

        confirm_email_token(token, client=client)
        old_email = user_data.get('email')
        old_password = user_data.get('password')

        response = client_post(client, request_url, data=json.dumps(user_data))
        assert response.status_code == OK
        user_data['email'] = random_email()
        response = client_post(client, request_url, data=json.dumps(user_data))
        assert response.status_code == UNAUTHORIZED
        user_data['email'] = old_email

        token = get_email_token(user_data)
        user_data['password'] = random_password()
        response = client_post(client, f'/auth/reset/{token}', data=json.dumps(user_data))
        assert response.status_code == OK

        bad_token = random_text()
        response = client_post(client, f'/auth/reset/{bad_token}', data=json.dumps(user_data))
        assert response.status_code == UNAUTHORIZED

        authenticate_user('login', data=user_data, client=client)
        user_data['password'] = old_password
        authenticate_user('login', data=user_data, expected=UNAUTHORIZED, client=client)
