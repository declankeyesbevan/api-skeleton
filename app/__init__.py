from flask import Blueprint
from flask_restplus import Api
from werkzeug.exceptions import InternalServerError, Unauthorized

from app.main.data.dto import RequestDto, ResponseDto
from app.main.routes.auth import api as auth_ns
from app.main.routes.user import api as user_ns
from app.responses import FAIL, UNAUTHORIZED, UNKNOWN_ERROR_PAYLOAD

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

api.add_namespace(RequestDto.api)
api.add_namespace(ResponseDto.api)
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(user_ns, path='/users')


@api.errorhandler(Unauthorized)
def unauthorised_error_handler(error):
    """Unauthorised error handler"""
    print({'message': str(error)}, getattr(error, 'code', UNAUTHORIZED))
    return dict(status=FAIL, data=dict(unauthorised=error)), UNAUTHORIZED


@api.errorhandler(InternalServerError)
def default_error_handler(error):
    """Default error handler"""
    # TODO: use logging with correct error level
    print({'message': str(error)}, getattr(error, 'code', UNKNOWN_ERROR_PAYLOAD))
    return UNKNOWN_ERROR_PAYLOAD

# TODO: Use @api.marshal_with(error_fields, code=400)
