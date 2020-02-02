import json

import pytest

from app.responses import BAD_REQUEST, CONFLICT, NOT_FOUND, OK
from app.utils import FIRST, SECOND
from tests.data_factory import random_text, user_attributes
from tests.helpers import client_get, register_client_user


@pytest.mark.usefixtures('database')
def test_user_list_get(client, registered_users, number_of_users):
    """Test for list of all registered users."""
    with client:
        response = client_get(client, '/users')
        data = json.loads(response.data.decode()).get('data')
        users = data.get('users')
        assert response.status_code == OK
        assert len(users) == number_of_users
        for idx, item in enumerate(users):
            for attribute in ['email', 'username']:
                assert registered_users[idx].get(attribute) == item.get(attribute)
                assert 'password' not in item


@pytest.mark.usefixtures('database')
def test_user_list_post(client):
    """Test for creating a new user."""
    with client:
        users = [user_attributes() for _ in range(2)]
        register_client_user(client, users[SECOND])

        users[FIRST]['password'] = None
        expected = [BAD_REQUEST, CONFLICT]
        for idx, user in enumerate(users):
            register_client_user(client, user, expected=expected[idx])


@pytest.mark.usefixtures('database')
def test_user_get(client, registered_user):
    """Test for specific registered user."""
    with client:
        data = json.loads(registered_user.data.decode()).get('data')
        user = data.get('user')

        response = client_get(client, f'/users/{user.get("public_id")}')
        data = json.loads(response.data.decode()).get('data')
        user = data.get('user')
        assert response.status_code == OK
        assert 'email' and 'username' and 'public_id' in user
        assert 'password' not in user

        fake_id = random_text()
        response = client_get(client, f'/users/{fake_id}')
        assert response.status_code == NOT_FOUND