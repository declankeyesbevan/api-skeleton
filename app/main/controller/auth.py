from flask import request
from flask_restplus import Resource

from app.main.data.dto import AuthDto
from app.main.service.auth import Auth
from app.responses import (
    BAD_REQUEST, EMAIL_OR_PASSWORD, INTERNAL_SERVER_ERROR, LOGIN_SUCCESS, LOGOUT_SUCCESS, MALFORMED,
    OK, UNAUTHORIZED, UNKNOWN,
)

# pylint: disable=invalid-name, no-self-use

api = AuthDto.api
auth = AuthDto.auth


@api.route('/login')
class UserLogin(Resource):
    """User Login Resource"""

    @api.response(OK, LOGIN_SUCCESS)
    @api.response(BAD_REQUEST, MALFORMED)
    @api.response(UNAUTHORIZED, EMAIL_OR_PASSWORD)
    @api.response(INTERNAL_SERVER_ERROR, UNKNOWN)
    @api.doc('/auth/login')
    @api.expect(auth, validate=True)
    def post(self):
        """Log the user in and return an auth token"""
        return Auth.login_user(data=request.json)


@api.route('/logout')
class UserLogout(Resource):
    """User Logout Resource"""

    @api.response(OK, LOGOUT_SUCCESS)
    @api.response(BAD_REQUEST, MALFORMED)
    @api.response(UNAUTHORIZED, EMAIL_OR_PASSWORD)
    @api.response(INTERNAL_SERVER_ERROR, UNKNOWN)
    @api.doc('/auth/logout')
    def post(self):
        """Log the user out"""
        return Auth.logout_user(data=request.headers.get('Authorization'))
