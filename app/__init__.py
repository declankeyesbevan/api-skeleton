# pylint: disable=invalid-name, logging-fstring-interpolation

"""
Initialisation module for Flask-RESTX. Creates a Flask Blueprint which is passed to initialise a
Flask-RESTX object. Flask-RESTX defers initialisation when a Blueprint is passed. Adds Flask-RESTX
namespaces and error handlers to the Flask-RESTX object.
"""

import logging

from flask import Blueprint
from flask_restx import Api
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, NotFound, Unauthorized

from app.main.data.dto import EmailDto, PasswordDto, ResponseDto
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
    title='Flask-RESTX API skeleton',
    version='0.1.0',
    description='Boilerplate for Flask-RESTX web service',
    authorizations=authorizations,
    security='bearer',
)

api.add_namespace(EmailDto.api)
api.add_namespace(PasswordDto.api)
api.add_namespace(ResponseDto.api)
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(user_ns, path='/users')


@api.errorhandler(Conflict)
@api.errorhandler(NotFound)
@api.errorhandler(Unauthorized)
@api.errorhandler(BadRequest)
def fail_handler(error):
    """
    Any kind of expected failures e.g. HTTP 404, HTTP 409 are caught by this handler. Failures are
    consistently wrapped and returned to the client as JSON.
    :param error: werkzeug.exceptions object thrown by the application
    :return: dict containing the HTTP error code and the name and description of the failure
    """
    logger.error(f"Error code: {error.code}")
    logger.error(f"Error description: {str(error.description)}")
    return responder(code=error.code, data={error.name.lower(): str(error.description)})


@api.errorhandler(InternalServerError)
def error_handler(error):
    """
    An unexpected error i.e. HTTP 500 is caught by this handler. The error is consistently
    wrapped and returned to the client as JSON.
    :param error: werkzeug.exceptions object thrown by the application
    :return: dict containing the HTTP error code and the name and description of the error
    """
    logger.critical(f"Error code: {error.code}")
    logger.critical(f"Error description: {str(error.description)}")
    return responder(code=error.code, data={error.name.lower(): str(error.description)})
