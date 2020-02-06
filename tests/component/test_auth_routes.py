import json

import pytest

from app.responses import BAD_REQUEST, UNAUTHORIZED
from tests.data_factory import random_text
from tests.helpers import log_in_user, log_out_user


@pytest.mark.usefixtures('database', 'registered_user')
def test_user_login(client, user_data):
    """Test for login of registered user."""
    with client:
        log_in_user(client, user_data)

        for key in ['email', 'password']:
            user_data[key] = random_text()
            log_in_user(client, user_data, UNAUTHORIZED)


@pytest.mark.usefixtures('database', 'registered_user')
def test_user_logout(client, user_data):
    """Test for logout before token expires."""
    with client:
        login_response = log_in_user(client, user_data)
        data = json.loads(login_response.data.decode()).get('data')
        headers = dict(Authorization=f"Bearer {data.get('token')}")
        log_out_user(client, headers)

        headers['Authorization'] = f"Bearer {random_text()}"
        test_headers = [headers, None]
        expected = [UNAUTHORIZED, BAD_REQUEST]
        for idx, header in enumerate(test_headers):
            log_out_user(client, header, expected=expected[idx])
