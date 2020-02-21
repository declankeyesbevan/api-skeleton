import copy
import json

import pytest

from app.responses import BAD_REQUEST, CONFLICT, NOT_FOUND, OK, UNAUTHORIZED
from app.utils import FIRST, SECOND, THIRD, THREE_ITEMS
from tests.data_factory import (
    NUM_GENERIC_USERS, NUM_STANDARD_CLIENT_USERS, TOTAL_USERS, random_email, random_text,
    user_attributes,
)
from tests.helpers import client_get, deny_endpoint, register_user


@pytest.mark.usefixtures('database')
def test_user_list_get(client, headers, admin_headers):
    """Test for list of all registered users."""
    with client:
        users = [user_attributes() for _ in range(NUM_GENERIC_USERS)]
        for user_data in users:
            register_user(json.dumps(user_data), client=client)

        # Standard User can only see themselves, Admin users can see full list.
        endpoint = '/users'
        expected = [NUM_STANDARD_CLIENT_USERS, TOTAL_USERS]
        for outer_idx, header in enumerate([headers, admin_headers]):
            response = client_get(client, endpoint, headers=header)
            data = response.json.get('data')
            users = data.get('users')
            assert response.status_code == OK
            assert len(users) == expected[outer_idx]
            for inner_idx, item in enumerate(users):
                for attribute in ['email', 'username']:
                    assert users[inner_idx].get(attribute) == item.get(attribute)
                    assert 'password' not in item

        deny_endpoint(endpoint, client=client)


@pytest.mark.usefixtures('database')
def test_user_list_post(client):
    """Test for creating a new user."""
    with client:
        user = user_attributes()
        users = [copy.copy(user) for _ in range(THREE_ITEMS)]
        register_user(json.dumps(users[FIRST]), client=client)

        users[FIRST]['password'] = None
        users[SECOND]['email'] = random_email()  # Must be unique username
        users[THIRD]['username'] = random_text()  # Must be unique email
        expected = [BAD_REQUEST, CONFLICT, CONFLICT]
        for idx, user in enumerate(users):
            register_user(json.dumps(user), expected=expected[idx], client=client)


@pytest.mark.usefixtures('database')
def test_user_get_by_id(client, user_data, headers, admin_headers):
    """Test for specific registered user."""
    with client:
        registered_user = register_user(json.dumps(user_data), client=client)
        data = json.loads(registered_user.data.decode()).get('data')
        user = data.get('user')

        # Standard User can only see themselves, Admin users can see anyone.
        endpoint = f'/users/{user.get("public_id")}'
        expected = [UNAUTHORIZED, OK]
        for idx, header in enumerate([headers, admin_headers]):
            response = client_get(client, endpoint, headers=header)
            if expected == OK:
                data = response.json.get('data')
                user = data.get('user')
                assert 'email' and 'username' and 'public_id' in user
                assert 'password' not in user
            assert response.status_code == expected[idx]

        fake_id = random_text()
        response = client_get(client, f'/users/{fake_id}', headers=admin_headers)
        assert response.status_code == NOT_FOUND

        deny_endpoint(endpoint, client=client)
