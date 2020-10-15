# pylint: disable=invalid-name, logging-format-interpolation

import logging

from flask import Blueprint
from flask_restplus import Api
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, NotFound, Unauthorized

from app.main.data.dto import BaseDto, RequestDto, ResponseDto
from app.main.routes.auth import api as auth_ns
from app.main.routes.user import api as user_ns
from app.responses import responder

logger = logging.getLogger('api-skeleton')
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

api.add_namespace(BaseDto.api)
api.add_namespace(RequestDto.api)
api.add_namespace(ResponseDto.api)
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(user_ns, path='/users')


@api.errorhandler(Conflict)
@api.errorhandler(NotFound)
@api.errorhandler(Unauthorized)
@api.errorhandler(BadRequest)
def fail_handler(error):
    logger.error(f"Error code: {error.code}")
    logger.error(f"Error description: {str(error.description)}")
    return responder(code=error.code, data={error.name.lower(): str(error.description)})


@api.errorhandler(InternalServerError)
def error_handler(error):
    logger.critical(f"Error code: {error.code}")
    logger.critical(f"Error description: {str(error.description)}")
    return responder(code=error.code, data={error.name.lower(): str(error.description)})
