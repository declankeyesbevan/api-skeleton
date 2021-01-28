import copy
import json

import pytest

from app.responses import CONFLICT, NOT_FOUND, OK, UNAUTHORIZED
from app.utils import FIRST, SEVEN_ITEMS
from tests.data_factory import (
    NUM_GENERIC_USERS, NUM_STANDARD_CLIENT_USERS, random_email, random_text, TOTAL_USERS,
    user_attributes,
)
from tests.helpers import (
    authenticate_user, bad_username_and_email, check_endpoint_denied, client_get, client_post,
    confirm_and_login_user, confirm_email_token, get_email_token, register_user,
)


@pytest.mark.usefixtures('database')
def test_user_list_get(client, headers, admin_headers):
    """Test for list of all registered users."""
    with client:
        users = [user_attributes() for _ in range(NUM_GENERIC_USERS)]
        for user_data in users:
            register_user(user_data, client=client)

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

        check_endpoint_denied(endpoint, client=client)


@pytest.mark.usefixtures('database')
def test_user_list_post(client):
    """Test for creating a new user."""
    with client:
        user = user_attributes()
        users = [copy.copy(user) for _ in range(SEVEN_ITEMS)]
        register_user(users[FIRST], client=client)

        users, expected = bad_username_and_email(users)
        for idx, user in enumerate(users):
            register_user(user, expected=expected[idx], client=client)


@pytest.mark.usefixtures('database')
def test_user_get_by_id(client, user_data, headers, admin_headers):
    """Test for specific registered user."""
    with client:
        response = register_user(user_data, client=client)
        data = json.loads(response.data.decode()).get('data')
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

        check_endpoint_denied(endpoint, client=client)


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
def test_resend_email_confirm(client, user_data):
    """Test for resend email confirmation."""
    with client:
        register_user(user_data, client=client)
        request_url = '/users/email/confirm/resend'

        authenticate_user('login', data=user_data, expected=UNAUTHORIZED, client=client)

        response = client_post(client, request_url, data=user_data)
        assert response.status_code == OK

        unconfirmed_email = user_data.get('email')
        user_data['email'] = random_email()
        response = client_post(client, request_url, data=user_data)
        assert response.status_code == NOT_FOUND

        user_data['email'] = unconfirmed_email
        token = get_email_token(user_data)

        confirm_email_token(token, client=client)
        confirm_email_token(token, client=client, expected=CONFLICT)

        authenticate_user('login', data=user_data, client=client)


@pytest.mark.usefixtures('database')
def test_user_change_email(client, user_data):
    """Test for changing user's email address."""
    with client:
        response = register_user(user_data, client=client)
        data = json.loads(response.data.decode()).get('data')
        user = data.get('user')

        headers = confirm_and_login_user(user_data, client=client)

        endpoint = '/users/email/change'
        data = dict(email=random_email())
        response = client_post(client, endpoint, headers=headers, data=data)
        assert response.status_code == OK

        user_endpoint = f'/users/{user.get("public_id")}'
        response = client_get(client, user_endpoint, headers=headers)
        data = response.json.get('data')
        updated_user = data.get('user')

        assert updated_user.get('email') != user_data.get('email')

        data = dict(email=random_email())
        check_endpoint_denied(endpoint, method='post', data=data, client=client)
