import json

import pytest

from conftest import create_app

flask_app = create_app('TestingConfig')


def register_user(client):
    return client.post(
        '/user/',
        data=json.dumps(dict(
            email='example@gmail.com',
            username='username',
            password='123456'
        )),
        content_type='application/json'
    )


def login_user(client):
    return client.post(
        '/auth/login',
        data=json.dumps(dict(
            email='example@gmail.com',
            password='123456'
        )),
        content_type='application/json'
    )


@pytest.mark.usefixtures('handle_db')
def test_registered_user_login():
    """ Test for login of registered-user login """
    with flask_app.test_client() as client:
        user_response = register_user(client)
        response_data = json.loads(user_response.data.decode())
        assert response_data['Authorization']
        assert user_response.status_code == 201

        # registered user login
        login_response = login_user(client)
        data = json.loads(login_response.data.decode())
        assert data['Authorization']
        assert login_response.status_code == 200


@pytest.mark.usefixtures('handle_db')
def test_valid_logout():
    """ Test for logout before token expires """
    with flask_app.test_client() as client:
        # user registration
        user_response = register_user(client)
        response_data = json.loads(user_response.data.decode())
        assert response_data['Authorization']
        assert user_response.status_code == 201

        # registered user login
        login_response = login_user(client)
        data = json.loads(login_response.data.decode())
        assert data['Authorization']
        assert login_response.status_code == 200

        # valid token logout
        response = client.post(
            '/auth/logout',
            headers=dict(
                Authorization=(
                    f"Bearer {json.loads(login_response.data.decode())['Authorization']}"
                )
            )
        )
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert response.status_code == 200
