import json

import pytest

from tests.data_factory import random_text, user_attributes
from tests.helpers import client_get, register_user


@pytest.mark.usefixtures('database')
def test_all_users(client, registered_users, number_of_users):
    """Test for list of all registered users."""
    with client:
        response = client_get(client, '/users/')
        body = json.loads(response.data.decode())
        data = body.get('data')
        assert response.status_code == 200
        assert len(data) == number_of_users
        for idx, item in enumerate(data):
            for attribute in ['email', 'username']:
                assert registered_users[idx].get(attribute) == item.get(attribute)
                assert item.get('password') is None

        users = [user_attributes() for _ in range(2)]
        register_user(client, users[1])
        users[0]['password'] = None
        expected = 400, 409
        for idx, user in enumerate(users):
            register_user(client, user, expected=expected[idx])


@pytest.mark.usefixtures('database')
def test_one_user(client, registered_user):
    """Test for specific registered user."""
    with client:
        body = json.loads(registered_user.data.decode())
        public_id = body.get('public_id')

        response = client_get(client, f'/users/{public_id}')
        body = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'email' and 'username' and 'public_id' in body
        assert body.get('password') is None

        fake_id = random_text()
        response = client_get(client, f'/users/{fake_id}')
        assert response.status_code == 404
