import copy
import json

import pytest

from app.responses import BAD_REQUEST, CONFLICT, NOT_FOUND, OK
from app.utils import FIRST, SECOND, THIRD, THREE_ITEMS
from tests.data_factory import random_email, random_text, user_attributes
from tests.helpers import client_get, denied_client_get_endpoint, register_client_user


@pytest.mark.usefixtures('database')
def test_user_list_get(client, headers, registered_users, number_of_users):
    """Test for list of all registered users."""
    with client:
        endpoint = '/users'
        response = client_get(client, endpoint, headers=headers)
        data = json.loads(response.data.decode()).get('data')
        users = data.get('users')
        assert response.status_code == OK
        assert len(users) == number_of_users
        for idx, item in enumerate(users):
            for attribute in ['email', 'username']:
                assert registered_users[idx].get(attribute) == item.get(attribute)
                assert 'password' not in item

        denied_client_get_endpoint(client, endpoint)


@pytest.mark.usefixtures('database')
def test_user_list_post(client):
    """Test for creating a new user."""
    with client:
        user = user_attributes()
        users = [copy.copy(user) for _ in range(THREE_ITEMS)]
        register_client_user(client, users[FIRST])

        users[FIRST]['password'] = None
        users[SECOND]['email'] = random_email()  # Must be unique username
        users[THIRD]['username'] = random_text()  # Must be unique email
        expected = [BAD_REQUEST, CONFLICT, CONFLICT]
        for idx, user in enumerate(users):
            register_client_user(client, user, expected=expected[idx])


@pytest.mark.usefixtures('database')
def test_user_get_by_id(client, registered_user, headers):
    """Test for specific registered user."""
    with client:
        data = json.loads(registered_user.data.decode()).get('data')
        user = data.get('user')

        endpoint = f'/users/{user.get("public_id")}'
        response = client_get(client, endpoint, headers=headers)
        data = json.loads(response.data.decode()).get('data')
        user = data.get('user')
        assert response.status_code == OK
        assert 'email' and 'username' and 'public_id' in user
        assert 'password' not in user

        fake_id = random_text()
        response = client_get(client, f'/users/{fake_id}', headers=headers)
        assert response.status_code == NOT_FOUND

        denied_client_get_endpoint(client, endpoint)
