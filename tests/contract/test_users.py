import copy

import pytest

from app.responses import NOT_FOUND, OK, UNAUTHORIZED
from app.utils import SEVEN_ITEMS
from tests.data_factory import (
    NUM_GENERIC_USERS, NUM_STANDARD_CLIENT_USERS, TOTAL_USERS, random_email, random_text,
    user_attributes,
)
from tests.helpers import (
    API_BASE_URL, api_get, api_post, bad_username_and_email, check_endpoint_denied,
    confirm_and_login_user, register_user,
)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_list_get(headers, admin_headers):
    """Test for list of all registered users."""
    users = [user_attributes() for _ in range(NUM_GENERIC_USERS)]
    for user_data in users:
        register_user(user_data)

    # Standard User can only see themselves, Admin users can see full list.
    endpoint = f'{API_BASE_URL}/users'
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
def test_user_list_post(user_data):
    """Test for creating a new user."""
    register_user(user_data)
    users = [copy.copy(user_data) for _ in range(SEVEN_ITEMS)]

    users, expected = bad_username_and_email(users)
    for idx, user in enumerate(users):
        register_user(user, expected=expected[idx])


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_get_by_id(user_data, headers, admin_headers):
    """Test for specific registered user."""
    response = register_user(user_data)
    data = response.json().get('data')
    user = data.get('user')

    # Standard User can only see themselves, Admin users can see anyone.
    endpoint = f'{API_BASE_URL}/users/{user.get("public_id")}'
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
    response = api_get(f'{API_BASE_URL}/users/{fake_id}', headers=admin_headers)
    assert response.status_code == NOT_FOUND

    check_endpoint_denied(endpoint)


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_change_email(user_data):
    """Test for changing user's email address."""
    response = register_user(user_data)
    data = response.json().get('data')
    user = data.get('user')

    headers = confirm_and_login_user(user_data)

    endpoint = f'{API_BASE_URL}/users/email/change'
    data = dict(email=random_email())
    response = api_post(endpoint, headers=headers, data=data)
    assert response.status_code == OK

    user_endpoint = f'{API_BASE_URL}/users/{user.get("public_id")}'
    response = api_get(user_endpoint, headers=headers)
    data = response.json().get('data')
    updated_user = data.get('user')

    assert updated_user.get('email') != user_data.get('email')

    data = dict(email=random_email())
    check_endpoint_denied(endpoint, method='post', data=data)
