import json
import os
import subprocess
from pathlib import Path

from dotenv import dotenv_values

from app import api
from app.constants import FIRST, JSON_INDENT
from tools.postman_config import (
    add_attribute_to_body, add_attribute_to_path_variables, add_auth, add_snippet_to_event, routes,
)

BUILD_DIR = os.environ.get('BUILD_DIR', 'build')


def create_postman(app):
    with app.app_context():
        postman_api = api.as_postman(swagger=True)
        postman_vars = dotenv_values(dotenv_path=Path('configuration') / 'postman-environment.env')
        files = dict(
            postman_collection_v1=_update_api_json(postman_api),
            postman_environment=_template_environment_file(postman_vars),
        )
        for filename, data in files.items():
            _write_to_file(filename, data)
    _convert_to_v2()


def _template_environment_file(env_vars):
    values = [dict(key=f'{k.lower()}', value=v, enabled=True) for k, v in env_vars.items()]
    return dict(
        name='Flask-RESTX API skeleton 0.1.0',  # TODO: set dynamically from app config
        values=values,
        _postman_variable_scope='environment',
    )


def _write_to_file(filename, data):
    Path(f'{BUILD_DIR}').mkdir(parents=True, exist_ok=True)
    with open(f'{BUILD_DIR}/{filename}.json', 'w') as file:
        file.write(json.dumps(data, indent=JSON_INDENT))


def _convert_to_v2():
    # An upgrade to Postman has meant v1 can't be imported any more.
    subprocess.run(['rm', f'{BUILD_DIR}/postman_collection.json'])
    subprocess.run([
        'postman-collection-transformer', 'convert',
        '-i', f'{BUILD_DIR}/postman_collection_v1.json',
        '-o', f'{BUILD_DIR}/postman_collection.json',
        '-j', '1.0.0',
        '-p', '2.0.0',
        '-P'
    ])


def _update_api_json(data):
    _execute_parent_auth(data)
    for request in data.get('requests'):
        for section, metadata in routes.items():
            _execute_actions(request, section, metadata)
    return data


def _execute_parent_auth(data):
    data['auth'] = add_auth()


def _execute_body(request, keys):
    request['dataMode'] = 'raw'
    request['rawModeData'] = add_attribute_to_body(keys.get('attributes'))


def _execute_event(request, keys):
    request['events'] = add_snippet_to_event(keys.get('events'))


def _execute_path_variables(request, keys):
    key = [*request.get('pathVariables')][FIRST]
    value = keys.get('variables')[FIRST]
    request['pathVariables'][key] = add_attribute_to_path_variables(value)


def _drop_auth_header(request):
    headers = request.get('headers').replace('Authorization:', '')
    if headers.endswith('\n'):
        headers = headers.replace('\n', '')
    request['headers'] = headers


def _execute_actions(request, section, metadata):
    _drop_auth_header(request)
    for keys in metadata:
        if request.get('name') == keys.get('name') and request.get('method') == keys.get('method'):
            if section == 'bodies':
                _execute_body(request, keys)
            if section == 'path_variables':
                _execute_path_variables(request, keys)
            if section == 'snippets':
                _execute_event(request, keys)
