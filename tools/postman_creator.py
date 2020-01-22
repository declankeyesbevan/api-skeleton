import json
from pathlib import Path

from dotenv import dotenv_values

from app import API
from tools.postman_config import FIRST, add_body, add_header, add_snippet, routes


def create_postman(app):
    with app.app_context():
        env_vars = dotenv_values(dotenv_path=Path('configuration') / 'postman.env')
        api = API.as_postman(swagger=True)
        files = dict(
            postman_collection=add_to_json(api),
            postman_environment=template_environment_file(env_vars),
        )
        for filename, data in files.items():
            write_to_file(filename, data)


def template_environment_file(env_vars):
    values = [dict(key=f'{k.lower()}', value=v, enabled=True) for k, v in env_vars.items()]
    return dict(
        name='Flask-RESTPlus API skeleton 0.1.0',
        values=values,
        _postman_variable_scope='environment',
    )


def write_to_file(filename, data):
    with open(f'{filename}.json', 'w') as file:
        file.write(json.dumps(data, indent=4))


def add_to_json(data):
    for request in data.get('requests'):
        for section, metadata in routes.items():
            _execute_actions(request, section, metadata)
        if request.get('pathVariables'):
            variable = [*request.get('pathVariables')][FIRST]
            request['pathVariables'][variable] = f'{{{{{variable}}}}}'  # Madness!
    return data


def execute_actions(request, section, actions):
    for route, methods in section.items():
        if request.get('name') == route and request.get('method') in methods:
            actions()


def execute_header(request):
    request['headerData'] = add_header()


def execute_body(request):
    request['dataMode'] = 'raw'
    request['rawModeData'] = add_body()


def execute_snippet(request, keys):
    request['events'] = add_snippet(keys.get('events'))


def _execute_actions(request, section, metadata):
    for keys in metadata:
        if request.get('name') == keys.get('name') and request.get('method') == keys.get('method'):
            if section == 'headers':
                execute_header(request)
            if section == 'bodies':
                execute_body(request)
            if section == 'snippets':
                execute_snippet(request, keys)
