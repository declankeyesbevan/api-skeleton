import json

import requests

from app.config import CONFIG_BY_NAME
from app.responses import CREATED, OK, UNAUTHORIZED, UNPROCESSABLE_ENTITY
from tests.data_factory import random_text

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


# TODO: maybe convert to class for re-use below
def client_get(client, url, headers=None):
    return client.get(url, headers=headers, content_type='application/json')


def client_post(client, url, headers=None, data=None):
    return client.post(url, headers=headers, data=data, content_type='application/json')


def api_get(url, headers=None):
    return requests.get(url, headers=headers)


def api_post(url, headers=None, data=None):
    return requests.post(url, json=data, headers=headers)


def register_client_user(client, user_data, expected=CREATED):
    response = client_post(client, '/users', data=json.dumps(user_data))
    if expected == CREATED:
        data = json.loads(response.data.decode()).get('data')
        user = data.get('user')
        assert user.get('token')
    assert response.status_code == expected
    return response


def register_api_user(user_data, expected=CREATED):
    response = api_post(f'{API_BASE_URL}/users', data=user_data)
    assert response.status_code == expected
    return response


def log_in_client_user(client, user_data, expected=OK):
    response = client_post(client, '/auth/login', data=json.dumps(user_data))
    if expected == OK:
        data = json.loads(response.data.decode()).get('data')
        assert data.get('token')
    assert response.status_code == expected
    return response


def log_out_client_user(client, headers, expected=OK):
    response = client_post(client, '/auth/logout', headers=headers)
    assert response.status_code == expected
    return response


def denied_client_get_endpoint(client, endpoint):
    headers = dict(Authorization=f"Bearer {random_text()}")
    expected = [UNPROCESSABLE_ENTITY, UNAUTHORIZED]
    for idx, header in enumerate([headers, None]):
        response = client_get(client, endpoint, headers=header)
        assert response.status_code == expected[idx]


def denied_client_post_endpoint(client, endpoint):
    headers = dict(Authorization=f"Bearer {random_text()}")
    expected = [UNPROCESSABLE_ENTITY, UNAUTHORIZED]
    for idx, header in enumerate([headers, None]):
        response = client_post(client, endpoint, headers=header)
        assert response.status_code == expected[idx]


def denied_api_get_endpoint(endpoint):
    headers = dict(Authorization=f"Bearer {random_text()}")
    expected = [UNPROCESSABLE_ENTITY, UNAUTHORIZED]
    for idx, header in enumerate([headers, None]):
        response = api_get(endpoint, headers=header)
        assert response.status_code == expected[idx]


def denied_api_post_endpoint(endpoint):
    headers = dict(Authorization=f"Bearer {random_text()}")
    expected = [UNPROCESSABLE_ENTITY, UNAUTHORIZED]
    for idx, header in enumerate([headers, None]):
        response = api_post(endpoint, headers=header)
        assert response.status_code == expected[idx]
