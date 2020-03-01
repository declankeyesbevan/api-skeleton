import json

import pytest

from app.responses import OK, UNAUTHORIZED
from tests.data_factory import random_email, random_password
from tests.helpers import (
    authenticate_user, confirm_email_token, deny_endpoint, get_email_confirmation_token,
    register_user,
)


@pytest.mark.usefixtures('database')
def test_user_login(client, user_data):
    """Test for login of registered user."""
    with client:
        register_user(json.dumps(user_data), client=client)
        token = get_email_confirmation_token(user_data)
        confirm_email_token(token, client)
        authenticate_user('login', data=json.dumps(user_data), client=client)

        for key in ['email', 'password']:
            user_data[key] = random_email() if key == 'email' else random_password()
            authenticate_user(
                'login', data=json.dumps(user_data), expected=UNAUTHORIZED, client=client
            )


@pytest.mark.usefixtures('database')
def test_user_logout(client, user_data):
    """Test for logout."""
    with client:
        # Don't use fixture as we need a token that's been blacklisted in the database.
        register_user(json.dumps(user_data), client=client)
        token = get_email_confirmation_token(user_data)
        confirm_email_token(token, client)
        response = authenticate_user('login', data=json.dumps(user_data), client=client)
        data = response.json.get('data')
        headers = dict(Authorization=f"Bearer {data.get('token')}")

        expected = [OK, UNAUTHORIZED]  # Second iteration, token is blacklisted
        for idx, header in enumerate([headers, headers]):
            authenticate_user('logout', headers=header, expected=expected[idx], client=client)

        deny_endpoint('/auth/logout', method='post', client=client)


@pytest.mark.usefixtures('database')
def test_email_confirm(client, user_data):
    """Test for email confirmation."""
    with client:
        register_user(json.dumps(user_data), client=client)
        token = get_email_confirmation_token(user_data)

        authenticate_user('login', data=json.dumps(user_data), expected=UNAUTHORIZED, client=client)
        confirm_email_token(token, client)
        authenticate_user('login', data=json.dumps(user_data), client=client)
