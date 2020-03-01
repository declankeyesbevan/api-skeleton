import json
import os

import requests

from app.config import CONFIG_BY_NAME
from app.main.service.auth import Auth
from app.responses import CREATED, OK, UNAUTHORIZED, UNPROCESSABLE_ENTITY
from app.utils import FIRST
from tests.data_factory import random_text, user_model

CONFIG_OBJECT = CONFIG_BY_NAME['test-external']
API_BASE_URL = f'{CONFIG_OBJECT.PREFERRED_URL_SCHEME}://{CONFIG_OBJECT.SERVER_NAME}'


def set_up_database(db):
    db.create_all()
    db.session.commit()


def add_to_database(db, db_object):
    db.session.add(db_object)
    db.session.commit()


def tear_down_database(db):
    db.session.remove()
    db.drop_all()


def client_get(client, url, headers=None):
    return client.get(url, headers=headers, content_type='application/json')


def client_post(client, url, headers=None, data=None):
    return client.post(url, headers=headers, data=data, content_type='application/json')


def api_get(url, headers=None):
    return requests.get(url, headers=headers)


def api_post(url, headers=None, data=None):
    return requests.post(url, headers=headers, json=data)


def create_user(db, user_data, admin=False):
    user = user_model(user_data, admin=admin)
    add_to_database(db, user)
    return user


def create_header(db, user_data, admin=False):
    auth_token = Auth.encode_auth_token(create_user(db, user_data, admin=admin))
    return dict(Authorization=f"Bearer {auth_token}")


def register_user(user_data, expected=CREATED, client=None):
    url = '/users' if client else f'{API_BASE_URL}/users'
    response = client_post(client, url, data=user_data) if client else api_post(url, data=user_data)
    if expected == CREATED:
        data = (response.json if client else response.json()).get('data')
        user = data.get('user')
        assert user.get('public_id')
    assert response.status_code == expected
    return response


def authenticate_user(action, data=None, headers=None, expected=OK, client=None):
    url = f'auth/{action}' if client else f'{API_BASE_URL}/auth/{action}'
    response = (
        client_post(client, url, data=data, headers=headers) if client else
        api_post(url, data=data, headers=headers)
    )
    if expected == OK and action == 'login':
        data = (response.json if client else response.json()).get('data')
        assert data.get('token')
    assert response.status_code == expected
    return response


def deny_endpoint(endpoint, method='get', client=None):
    methods = dict(get=client_get, post=client_post) if client else dict(get=api_get, post=api_post)
    method = methods.get(method)

    headers = dict(Authorization=f"Bearer {random_text()}")
    expected = [UNPROCESSABLE_ENTITY, UNAUTHORIZED]
    for idx, header in enumerate([headers, None]):
        response = (
            method(client, endpoint, headers=header) if client else
            method(endpoint, headers=header)
        )
        assert response.status_code == expected[idx]


def get_email_confirmation_token(user_data):
    build_dir = os.environ.get('BUILD_DIR', 'build')
    with open(f'{build_dir}/{user_data.get("email").split("@")[FIRST]}.json', 'r') as f:
        token_dict = json.load(f)
    return token_dict.get('token')


def confirm_email_token(token, client=None):
    url = f'auth/confirm/{token}' if client else f'{API_BASE_URL}/auth/confirm/{token}'
    response = client_post(client, url) if client else api_post(url)
    assert response.status_code == OK
