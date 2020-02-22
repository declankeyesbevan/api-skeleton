# pylint: disable=invalid-name, logging-format-interpolation, no-self-use

import logging

from flask import request
from flask._compat import text_type as _
from flask_jwt_simple import jwt_required
from flask_restplus import Resource

from app.i18n.base import (
    EMAIL_PASSWORD, JWT_ERROR, JWT_UNPROCESSABLE, LOGIN_SUCCESS, LOGOUT_SUCCESS, MALFORMED,
)
from app.main.data.dto import AuthDto, ResponseDto
from app.main.service.auth import Auth
from app.responses import (
    BAD_REQUEST, INTERNAL_SERVER_ERROR, UNAUTHORIZED, UNKNOWN, UNPROCESSABLE_ENTITY,
)
from app.security import remove

logger = logging.getLogger('api-skeleton')
api = AuthDto.api
auth = AuthDto.auth
response = ResponseDto.response


@api.route('/login')
class UserLogin(Resource):
    """User Login Resource"""

    @api.doc('/auth/login')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(UNAUTHORIZED, _(EMAIL_PASSWORD))
    @api.response(BAD_REQUEST, _(MALFORMED))
    @api.expect(auth, validate=True)
    @api.marshal_with(response, description=_(LOGIN_SUCCESS), skip_none=True)
    def post(self):
        """Log the user in and return an auth token"""
        logger.info(f"Logging in user: {remove(request.json, ['password'])}")
        return Auth.login_user(request.json)


@api.route('/logout')
class UserLogout(Resource):
    """User Logout Resource"""

    @jwt_required
    @api.doc('/auth/logout')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(UNPROCESSABLE_ENTITY, _(JWT_UNPROCESSABLE))
    @api.response(UNAUTHORIZED, _(JWT_ERROR))
    @api.response(BAD_REQUEST, _(MALFORMED))
    @api.marshal_with(response, description=_(LOGOUT_SUCCESS), mask='status,data')
    def post(self):
        """Log the user out"""
        # Upon success the data attribute is returned but with null per the JSend spec. We want to
        # keep this but strip the 'message' attribute from the marshalling.
        # Using skip_none=True correctly removes the 'message' attribute but incorrectly removes
        # 'data: null' from the response.
        # Upon success we use a mask to keep the 'data' field.
        # Upon fail the data field has content so it won't be lost.
        # Upon error, 'message' is returned correctly and 'data' is not returned.
        # Status is ever present.
        logger.info(f"Logging out user")
        return Auth.logout_user(request.headers.get('Authorization'))
