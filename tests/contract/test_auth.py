import pytest

from app.responses import BAD_REQUEST, OK, UNAUTHORIZED
from tests.data_factory import random_text, user_attributes
from tests.helpers import API_BASE_URL, api_post, register_api_user


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_login():
    """Test for login of registered user."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    register_api_user(user_data)

    response = api_post(f'{API_BASE_URL}/auth/login', data=user_data)
    body = response.json()
    assert response.status_code == OK
    assert 'token' in body.get('data')

    for key in ['email', 'password']:
        user_data[key] = random_text()
        response = api_post(f'{API_BASE_URL}/auth/login', data=user_data)
        assert response.status_code == UNAUTHORIZED


@pytest.mark.local
@pytest.mark.usefixtures('database')
def test_user_logout():
    """Test for logout before token expires."""
    # TODO: Convert set up to fixture
    user_data = user_attributes()
    register_api_user(user_data)
    response = api_post(f'{API_BASE_URL}/auth/login', data=user_data)
    data = response.json().get('data')
    headers = dict(Authorization=f"Bearer {data.get('token')}")

    response = api_post(f'{API_BASE_URL}/auth/logout', headers=headers)
    assert response.status_code == OK

    headers['Authorization'] = f"Bearer {random_text()}"
    test_headers = [headers, None]
    expected = [UNAUTHORIZED, BAD_REQUEST]
    for idx, header in enumerate(test_headers):
        response = api_post(f'{API_BASE_URL}/auth/logout', headers=header)
        assert response.status_code == expected[idx]
