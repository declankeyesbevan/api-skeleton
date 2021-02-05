import json

from app.utils import FIRST, JSON_INDENT

routes = {
    'path_variables': [
        {
            'name': '/auth/password/reset/:token',
            'method': 'POST',
            'variables': ['reset_token'],
        },
        {
            'name': '/users/email/confirm/:token',
            'method': 'POST',
            'variables': ['confirmation_token'],
        },
        {
            'name': '/users/:public_id',
            'method': 'GET',
            'variables': ['public_id'],
        },
    ],
    'bodies': [
        {
            'name': '/auth/login',
            'method': 'POST',
            'attributes': ['email', 'password'],
        },
        {
            'name': '/auth/password/reset/request',
            'method': 'POST',
            'attributes': ['email'],
        },
        {
            'name': '/auth/password/reset/:token',
            'method': 'POST',
            'attributes': ['password'],
        },
        {
            'name': '/auth/password/change',
            'method': 'POST',
            'attributes': ['password'],
        },
        {
            'name': '/users',
            'method': 'POST',
            'attributes': ['email', 'password', 'username'],
        },
        {
            'name': '/users/email/confirm/resend',
            'method': 'POST',
            'attributes': ['email'],
        },
        {
            'name': '/users/email/change',
            'method': 'POST',
            'attributes': ['email'],
        },
    ],
    'snippets': [
        {
            'name': '/auth/login',
            'method': 'POST',
            'events': ['token'],
        },
        {
            'name': '/users',
            'method': 'POST',
            'events': ['public_id'],
        },
    ]
}

_javascript_snippets = {
    'token': 'pm.environment.set("token", jsonData.data.token);',
    'public_id': 'pm.environment.set("public_id", jsonData.data.user.public_id);',
}

_path_variable_attributes = {
    'reset_token': '{{reset_token}}',
    'confirmation_token': '{{confirmation_token}}',
    'public_id': '{{public_id}}',
}

_body_attributes = {
    'email': '{{email}}',
    'password': '{{password}}',
    'username': '{{username}}',
}


def add_auth():
    return {
        'type': 'bearer',
        'bearer': [
            {
                'key': 'token',
                'value': '{{token}}'
            }
        ]
    }


def add_snippet_to_event(postman_variables):
    event = [
        {
            'listen': 'test',
            'script': {
                'exec': [
                    'jsonData = pm.response.json();',
                ],
                'type': 'text/javascript'
            }
        }
    ]
    for postman_variable in postman_variables:
        if postman_variable in _javascript_snippets:
            event[FIRST]['script']['exec'].append(_javascript_snippets[postman_variable])
    return event


def add_attribute_to_path_variables(value):
    return _path_variable_attributes[value]


def add_attribute_to_body(postman_variables):
    body = dict()
    for postman_variable in postman_variables:
        if postman_variable in _body_attributes:
            body.update({postman_variable: _body_attributes[postman_variable]})
    return json.dumps(body, indent=JSON_INDENT)
