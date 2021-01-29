import copy

import pytest

from app.responses import CONFLICT, NOT_FOUND, OK, UNAUTHORIZED
from app.utils import SEVEN_ITEMS
from tests.data_factory import (
    NUM_GENERIC_USERS, NUM_STANDARD_CLIENT_USERS, random_email, random_text, TOTAL_USERS,
    user_attributes,
)
from tests.helpers import (
    api_get, api_post, authenticate_user, bad_username_and_email, check_endpoint_denied,
    confirm_and_login_user, confirm_email_token, get_email_token, register_user,
)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_list_users(headers, admin_headers):
    """Test for list of all registered users."""
    users = [user_attributes() for _ in range(NUM_GENERIC_USERS)]
    for user_data in users:
        register_user(user_data)

    # Standard User can only see themselves, Admin users can see full list.
    endpoint = '/users'
    expected = [NUM_STANDARD_CLIENT_USERS, TOTAL_USERS]
    for outer_idx, header in enumerate([headers, admin_headers]):
        response = api_get(endpoint, headers=header)
        assert response.status_code == OK
        body = response.json().get('data')
        users = body.get('users')
        assert len(users) == expected[outer_idx]
        for inner_idx, item in enumerate(users):
            for key in ['email', 'username']:
                assert any(item.get(key) == users[inner_idx].get(key) for item in users)
                assert not any('password' in item for item in users)

    check_endpoint_denied(endpoint)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_create_user(user_data):
    """Test for creating a new user."""
    users = [copy.copy(user_data) for _ in range(SEVEN_ITEMS)]
    register_user(user_data)  # First user to register becomes Admin.

    # Standard user registration is open to anyone. Ensure subsequent anonymous registrations
    # can't create an Admin.
    anonymous_user = user_attributes(admin=True)
    register_user(anonymous_user, expected=UNAUTHORIZED)
    del anonymous_user['admin']
    register_user(anonymous_user)
    headers = confirm_and_login_user(anonymous_user)
    # Ensure registered Standard user can't create Admin.
    admin_user = user_attributes(admin=True)
    register_user(admin_user, headers=headers, expected=UNAUTHORIZED)

    users, expected = bad_username_and_email(users)
    for idx, user in enumerate(users):
        register_user(user, expected=expected[idx])


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_get_user_by_id(user_data, headers, admin_headers):
    """Test for specific registered user."""
    response = register_user(user_data)
    data = response.json().get('data')
    user = data.get('user')

    # Standard User can only see themselves, Admin users can see anyone.
    endpoint = f'/users/{user.get("public_id")}'
    expected = [UNAUTHORIZED, OK]
    for idx, header in enumerate([headers, admin_headers]):
        response = api_get(endpoint, headers=header)
        if expected == OK:
            data = response.json().get('data')
            user = data.get('user')
            assert 'email' and 'username' and 'public_id' in user
            assert 'password' not in user
        assert response.status_code == expected[idx]

    fake_id = random_text()
    response = api_get(f'/users/{fake_id}', headers=admin_headers)
    assert response.status_code == NOT_FOUND

    check_endpoint_denied(endpoint)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_email_confirm(user_data):
    """Test for email confirmation."""
    register_user(user_data)
    token = get_email_token(user_data)

    authenticate_user('login', data=user_data, expected=UNAUTHORIZED)
    confirm_email_token(token)
    authenticate_user('login', data=user_data)
    confirm_email_token(token, expected=CONFLICT)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_resend_email_confirm(user_data):
    """Test for resend email confirmation."""
    register_user(user_data)
    request_url = '/users/email/confirm/resend'

    authenticate_user('login', data=user_data, expected=UNAUTHORIZED)

    response = api_post(request_url, data=user_data)
    assert response.status_code == OK

    unconfirmed_email = user_data.get('email')
    user_data['email'] = random_email()
    response = api_post(request_url, data=user_data)
    assert response.status_code == NOT_FOUND

    user_data['email'] = unconfirmed_email
    token = get_email_token(user_data)

    confirm_email_token(token)
    confirm_email_token(token, expected=CONFLICT)

    authenticate_user('login', data=user_data)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_change_email(user_data):
    """Test for changing user's email address."""
    response = register_user(user_data)
    data = response.json().get('data')
    user = data.get('user')

    headers = confirm_and_login_user(user_data)

    endpoint = '/users/email/change'
    data = dict(email=random_email())
    for expected in [OK, CONFLICT]:
        response = api_post(endpoint, headers=headers, data=data)
        assert response.status_code == expected

    user_endpoint = f'/users/{user.get("public_id")}'
    response = api_get(user_endpoint, headers=headers)
    data = response.json().get('data')
    updated_user = data.get('user')

    assert updated_user.get('email') != user_data.get('email')

    data = dict(email=random_email())
    check_endpoint_denied(endpoint, method='post', data=data)
