import json

import pytest

from app.responses import OK, UNAUTHORIZED
from tests.data_factory import random_email, random_password
from tests.helpers import denied_client_post_endpoint, log_in_client_user, log_out_client_user


@pytest.mark.usefixtures('database', 'registered_user')
def test_user_login(client, user_data):
    """Test for login of registered user."""
    with client:
        log_in_client_user(client, user_data)

        for key in ['email', 'password']:
            user_data[key] = random_email() if key == 'email' else random_password()
            log_in_client_user(client, user_data, UNAUTHORIZED)


@pytest.mark.usefixtures('database', 'registered_user')
def test_user_logout(client, user_data):
    """Test for logout before token expires."""
    with client:
        # Don't use fixture as we need a token that's been blacklisted in the database.
        login_response = log_in_client_user(client, user_data)
        data = json.loads(login_response.data.decode()).get('data')
        headers = dict(Authorization=f"Bearer {data.get('token')}")

        expected = [OK, UNAUTHORIZED]  # Second iteration, token is blacklisted
        for idx, header in enumerate([headers, headers]):
            log_out_client_user(client, header, expected=expected[idx])

        denied_client_post_endpoint(client, '/auth/logout')
