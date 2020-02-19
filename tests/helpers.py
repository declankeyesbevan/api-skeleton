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


def client_get(client, url, headers=None):
    return client.get(url, headers=headers, content_type='application/json')


def client_post(client, url, headers=None, data=None):
    return client.post(url, headers=headers, data=data, content_type='application/json')


def api_get(url, headers=None):
    return requests.get(url, headers=headers)


def api_post(url, headers=None, data=None):
    return requests.post(url, headers=headers, json=data)


def register_user(user_data, expected=CREATED, client=None):
    url = '/users' if client else f'{API_BASE_URL}/users'
    response = client_post(client, url, data=user_data) if client else api_post(url, data=user_data)
    if expected == CREATED:
        data = (response.json if client else response.json()).get('data')
        user = data.get('user')
        assert user.get('token')
    assert response.status_code == expected
    return response


def authenticate_client_user(client, action, data=None, headers=None, expected=OK):
    response = client_post(client, f'auth/{action}', data=data, headers=headers)
    if expected == OK and action == 'login':
        data = response.json.get('data')
        assert data.get('token')
    assert response.status_code == expected
    return response


def denied_endpoint(endpoint, method='get', client=None):
    methods = dict(get=client_get, post=client_post) if client else dict(get=api_get, post=api_post)
    method = methods.get(method)

    headers = dict(Authorization=f"Bearer {random_text()}")
    expected = [UNPROCESSABLE_ENTITY, UNAUTHORIZED]
    for idx, header in enumerate([headers, None]):
        response = method(
            client, endpoint, headers=header) if client else method(endpoint, headers=header)
        assert response.status_code == expected[idx]
