import json

FIRST = 0
LAST = 1


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
            'events': ['token', 'public_id'],
        },
    ]
}

javascript_snippets = {
    'token': 'pm.environment.set("token", jsonData.token);',
    'public_id': 'pm.environment.set("public_id", jsonData.public_id);'
}


def add_header():
    return [
        {
            'key': 'Authorization',
            'value': 'Bearer {{token}}',
            'enabled': True
        }
    ]


def add_body():
    raw_data = {
        'email': '{{email}}',
        'password': '{{password}}',
        'username': '{{username}}',
        'public_id': '{{public_id}}',
    }
    return json.dumps(raw_data, indent=4)


def add_snippet(postman_variables):
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
        if postman_variable in javascript_snippets:
            event[FIRST]['script']['exec'].append(javascript_snippets[postman_variable])
    return event
