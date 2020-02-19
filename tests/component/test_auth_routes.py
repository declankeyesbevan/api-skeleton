import json

import pytest

from app.responses import OK, UNAUTHORIZED
from tests.data_factory import random_email, random_password
from tests.helpers import authenticate_client_user, denied_endpoint, register_user


@pytest.mark.usefixtures('database')
def test_user_login(client, user_data):
    """Test for login of registered user."""
    with client:
        register_user(json.dumps(user_data), client=client)
        authenticate_client_user(client, 'login', data=json.dumps(user_data))

        for key in ['email', 'password']:
            user_data[key] = random_email() if key == 'email' else random_password()
            authenticate_client_user(
                client, 'login', data=json.dumps(user_data), expected=UNAUTHORIZED
            )


@pytest.mark.usefixtures('database')
def test_user_logout(client, user_data):
    """Test for logout before token expires."""
    with client:
        # Don't use fixture as we need a token that's been blacklisted in the database.
        register_user(json.dumps(user_data), client=client)
        response = authenticate_client_user(client, 'login', data=json.dumps(user_data))
        data = response.json.get('data')
        headers = dict(Authorization=f"Bearer {data.get('token')}")

        expected = [OK, UNAUTHORIZED]  # Second iteration, token is blacklisted
        for idx, header in enumerate([headers, headers]):
            authenticate_client_user(client, 'logout', headers=header, expected=expected[idx])

        denied_endpoint('/auth/logout', method='post', client=client)
