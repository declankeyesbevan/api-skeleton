from flask import Blueprint
from flask_restplus import Api

from app.main.controller.auth import api as auth_ns
from app.main.controller.user import api as user_ns

BLUEPRINT = Blueprint('api', __name__)
AUTHORIZATIONS = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

API = Api(
    BLUEPRINT,
    title='Flask-RESTPlus API boiler-plate with JWT',
    version='1.0',
    description='A boilerplate for Flask-RESTPlus web service',
    authorizations=AUTHORIZATIONS,
    security='apikey',
)

API.add_namespace(auth_ns)
API.add_namespace(user_ns, path='/users')
