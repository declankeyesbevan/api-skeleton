from flask import Blueprint
from flask_restplus import Api

from app.main.controller.auth import api as auth_ns
from app.main.controller.user import api as user_ns

BLUEPRINT = Blueprint('api', __name__)
AUTHORIZATIONS = {
    'bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT: use \'Bearer {{token}}\' i.e. Bearer then space then your token'
    }
}

API = Api(
    BLUEPRINT,
    title='Flask-RESTPlus API skeleton',
    version='0.1.0',  # TODO: set dynamically from Git
    description='Boilerplate for Flask-RESTPlus web service',
    authorizations=AUTHORIZATIONS,
    security='bearer',
)

API.add_namespace(auth_ns, path='/auth')
API.add_namespace(user_ns, path='/users')
