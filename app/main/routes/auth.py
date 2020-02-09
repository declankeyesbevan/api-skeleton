# pylint: disable=invalid-name, logging-format-interpolation, no-self-use

import logging

from flask import request
from flask_restplus import Resource

from app.i18n.base import EMAIL_PASSWORD, LOGIN_SUCCESS, LOGOUT_SUCCESS, MALFORMED
from app.main.data.dto import AuthDto, ResponseDto
from app.main.service.auth import Auth
from app.responses import BAD_REQUEST, INTERNAL_SERVER_ERROR, UNAUTHORIZED, UNKNOWN
from app.security import remove

logger = logging.getLogger('api-skeleton')
api = AuthDto.api
auth = AuthDto.auth
response = ResponseDto.response


@api.route('/login')
class UserLogin(Resource):
    """User Login Resource"""

    @api.doc('/auth/login')
    @api.response(INTERNAL_SERVER_ERROR, UNKNOWN)
    @api.response(UNAUTHORIZED, EMAIL_PASSWORD)
    @api.response(BAD_REQUEST, MALFORMED)
    @api.expect(auth, validate=True)
    @api.marshal_with(response, description=LOGIN_SUCCESS, skip_none=True)
    def post(self):
        """Log the user in and return an auth token"""
        logger.info(f"Logging in user: {remove(request.json, ['password'])}")
        return Auth.login_user(data=request.json)


@api.route('/logout')
class UserLogout(Resource):
    """User Logout Resource"""

    @api.doc('/auth/logout')
    @api.response(INTERNAL_SERVER_ERROR, UNKNOWN)
    @api.response(UNAUTHORIZED, EMAIL_PASSWORD)
    @api.response(BAD_REQUEST, MALFORMED)
    @api.marshal_with(response, description=LOGOUT_SUCCESS, mask='status,data')
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
        return Auth.logout_user(data=request.headers.get('Authorization'))
