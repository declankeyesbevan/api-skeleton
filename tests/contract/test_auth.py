import os

import pytest

from app.responses import BAD_REQUEST, OK, UNAUTHORIZED
from tests.data_factory import random_text, user_attributes
from tests.helpers import api_post, register_api_user

api_base_url = os.environ.get('API_BASE_URL')


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_login():
    """Test for login of registered user."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    register_api_user(user_data)

    response = api_post(f'{api_base_url}/auth/login', data=user_data)
    body = response.json()
    assert response.status_code == OK
    assert 'Authorization' in body

    user_data['password'] = random_text()
    response = api_post(f'{api_base_url}/auth/login', data=user_data)
    assert response.status_code == UNAUTHORIZED


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_logout():
    """Test for logout before token expires."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    register_api_user(user_data)
    response = api_post(f'{api_base_url}/auth/login', data=user_data)
    headers = dict(
        Authorization=f"Bearer {response.json().get('Authorization')}"
    )

    response = api_post(f'{api_base_url}/auth/logout', headers=headers)
    assert response.status_code == OK

    headers['Authorization'] = f"Bearer {random_text()}"
    test_headers = [headers, None]
    expected = [UNAUTHORIZED, BAD_REQUEST]
    for idx, header in enumerate(test_headers):
        response = api_post(f'{api_base_url}/auth/logout', headers=header)
        assert response.status_code == expected[idx]
