import json

import pytest

from app.responses import BAD_REQUEST, CONFLICT, NOT_FOUND, OK
from tests.data_factory import random_text, user_attributes
from tests.helpers import client_get, register_client_user


@pytest.mark.usefixtures('database')
def test_user_list_get(client, registered_users, number_of_users):
    """Test for list of all registered users."""
    with client:
        response = client_get(client, '/users')
        data = json.loads(response.data.decode())
        assert response.status_code == OK
        assert len(data) == number_of_users
        for idx, item in enumerate(data):
            for attribute in ['email', 'username']:
                assert registered_users[idx].get(attribute) == item.get(attribute)
                assert item.get('password') is None


@pytest.mark.usefixtures('database')
def test_user_list_post(client):
    """Test for creating a new user."""
    with client:
        users = [user_attributes() for _ in range(2)]
        register_client_user(client, users[1])

        users[0]['password'] = None
        expected = [BAD_REQUEST, CONFLICT]
        for idx, user in enumerate(users):
            register_client_user(client, user, expected=expected[idx])


@pytest.mark.usefixtures('database')
def test_user_get(client, registered_user):
    """Test for specific registered user."""
    with client:
        body = json.loads(registered_user.data.decode())

        response = client_get(client, f'/users/{body.get("public_id")}')
        body = json.loads(response.data.decode())
        assert response.status_code == OK
        assert 'email' and 'username' and 'public_id' in body
        assert body.get('password') is None

        fake_id = random_text()
        response = client_get(client, f'/users/{fake_id}')
        assert response.status_code == NOT_FOUND
