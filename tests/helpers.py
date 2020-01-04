import json


def client_get(client, url, headers=None):
    return client.get(
        url,
        headers=headers,
        content_type='application/json'
    )


def client_post(client, url, headers=None, data=None):
    return client.post(
        url,
        headers=headers,
        data=data,
        content_type='application/json'
    )


def register_user(client, user_data, expected=201):
    response = client_post(client, '/users/', data=json.dumps(user_data))
    data = json.loads(response.data.decode())
    if expected == 201:
        assert data['Authorization']
    assert response.status_code == expected
    return response


def log_in_user(client, user_data, expected=200):
    response = client_post(client, '/auth/login', data=json.dumps(user_data))
    data = json.loads(response.data.decode())
    if expected == 200:
        assert data['Authorization']
    assert response.status_code == expected
    return response


def log_out_user(client, headers, expected=200):
    response = client_post(client, '/auth/logout', headers=headers)
    assert response.status_code == expected
    return response
