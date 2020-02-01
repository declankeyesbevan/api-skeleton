from flask import Blueprint
from flask_restplus import Api

from app.main.data.dto import ResponseDto, BaseDto
from app.main.routes.auth import api as auth_ns
from app.main.routes.user import api as user_ns

# pylint: disable=invalid-name

blueprint = Blueprint('api', __name__)
authorizations = {
    'bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT: use \'Bearer {{token}}\' i.e. Bearer then space then token'
    }
}

api = Api(
    blueprint,
    title='Flask-RESTPlus API skeleton',
    version='0.1.0',  # TODO: set dynamically from Git
    description='Boilerplate for Flask-RESTPlus web service',
    authorizations=authorizations,
    security='bearer',
)

api.add_namespace(ResponseDto.api)
api.add_namespace(BaseDto.api)
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(user_ns, path='/users')
