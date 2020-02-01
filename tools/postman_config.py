import json

from app.utils import FIRST

routes = {
    'headers': [
        {
            'name': '/auth/logout',
            'method': 'POST',
            'events': [],
        },
    ],
    'bodies': [
        {
            'name': '/auth/login',
            'method': 'POST',
            'events': [],
        },
        {
            'name': '/users',
            'method': 'POST',
            'events': [],
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
            'events': ['token_user', 'public_id_user'],
        },
    ]
}

_javascript_snippets = {
    'token': 'pm.environment.set("token", jsonData.data.token);',
    'token_user': 'pm.environment.set("token", jsonData.data.user.token);',
    'public_id_user': 'pm.environment.set("public_id", jsonData.data.user.public_id);',
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


def add_body():
    raw_data = {
        'email': '{{email}}',
        'password': '{{password}}',
        'username': '{{username}}',
        'public_id': '{{public_id}}',
    }
    return json.dumps(raw_data, indent=4)


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
