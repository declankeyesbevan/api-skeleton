import json
import os

import requests

from app.config import CONFIG_BY_NAME
from app.main.service.auth import Auth
from app.responses import BAD_REQUEST, CONFLICT, CREATED, OK, UNAUTHORIZED, UNPROCESSABLE_ENTITY
from app.utils import FIFTH, FIRST, FOURTH, SECOND, SEVENTH, SIXTH, THIRD
from tests.data_factory import random_email, random_text, user_model

CONFIG_OBJECT = CONFIG_BY_NAME['test-deployed']
API_BASE_URL = f'{CONFIG_OBJECT.PREFERRED_URL_SCHEME}://{CONFIG_OBJECT.SERVER_NAME}'
JSON = 'application/json'


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
    return client.get(url, headers=headers, content_type=JSON)


def client_post(client, url, headers=None, data=None):
    return client.post(url, headers=headers, data=json.dumps(data), content_type=JSON)


def api_get(url, headers=None):
    return requests.get(f'{API_BASE_URL}{url}', headers=headers)


def api_post(url, headers=None, data=None):
    return requests.post(f'{API_BASE_URL}{url}', headers=headers, json=data)


def create_user(db, user_data, admin=False):
    user = user_model(user_data, admin=admin)
    add_to_database(db, user)
    return user


def create_header(db, user_data, admin=False):
    auth_token = Auth.encode_auth_token(create_user(db, user_data, admin=admin))
    return dict(Authorization=f"Bearer {auth_token}")


def register_user(data, expected=CREATED, client=None):
    url = '/users'
    response = client_post(client, url, data=data) if client else api_post(url, data=data)
    if expected == CREATED:
        data = (response.json if client else response.json()).get('data')
        user = data.get('user')
        assert user.get('public_id')
    assert response.status_code == expected
    return response


def authenticate_user(action, data=None, headers=None, expected=OK, client=None):
    url = f'/auth/{action}'
    response = (
        client_post(client, url, data=data, headers=headers) if client else
        api_post(url, data=data, headers=headers)
    )
    if expected == OK and action == 'login':
        data = (response.json if client else response.json()).get('data')
        assert data.get('token')
    assert response.status_code == expected
    return response


def check_endpoint_denied(endpoint, method='get', data=None, client=None):
    methods = dict(get=client_get, post=client_post) if client else dict(get=api_get, post=api_post)
    method = methods.get(method)

    headers = dict(Authorization=f"Bearer {random_text()}")
    expected = [UNPROCESSABLE_ENTITY, UNAUTHORIZED]
    for idx, header in enumerate([headers, None]):
        response = _add_body_if_present(method, endpoint, header, data=data, client=client)
        assert response.status_code == expected[idx]


def confirm_and_login_user(user_data, client=None):
    token = get_email_token(user_data)
    confirm_email_token(token, client=client)
    response = authenticate_user('login', data=user_data, client=client)
    data = response.json.get('data') if client else response.json().get('data')
    return dict(Authorization=f"Bearer {data.get('token')}")


def get_email_token(user_data):
    build_dir = os.environ.get('BUILD_DIR', 'build')
    with open(f'{build_dir}/{user_data.get("email").split("@")[FIRST]}.json', 'r') as f:
        token_dict = json.load(f)
    return token_dict.get('token')


def confirm_email_token(token, expected=OK, client=None):
    url = f'/users/email/confirm/{token}'
    response = client_post(client, url) if client else api_post(url)
    assert response.status_code == expected


def bad_username_and_email(users):
    users[FIRST]['password'] = None
    users[SECOND]['email'] = random_email()  # Must be unique username
    users[THIRD]['username'] = random_text()  # Must be unique email
    users[FOURTH]['email'] = ''  # Must not be null
    users[FIFTH]['email'] = 'a@b.c'  # Must be at least 6 chars 'a@b.co'
    users[SIXTH]['username'] = ''  # Must not be null
    users[SEVENTH]['username'] = 'fooba'  # Must be at least 6 chars
    expected = [BAD_REQUEST, CONFLICT, CONFLICT, BAD_REQUEST, BAD_REQUEST, BAD_REQUEST, BAD_REQUEST]
    return users, expected


def _add_body_if_present(method, endpoint, header, data=None, client=None):
    if client:
        return (
            method(client, endpoint, headers=header, data=data) if data
            else method(client, endpoint, headers=header)
        )
    return (
        method(endpoint, headers=header, data=data) if data
        else method(endpoint, headers=header)
    )
