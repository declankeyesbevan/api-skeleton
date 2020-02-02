from flask import request
from flask_restplus import Resource

from app.main.data.dto import AuthDto, ResponseDto
from app.main.service.auth import Auth
from app.responses import (
    BAD_REQUEST, EMAIL_OR_PASSWORD, INTERNAL_SERVER_ERROR, LOGIN_SUCCESS, LOGOUT_SUCCESS, MALFORMED,
    UNAUTHORIZED, UNKNOWN,
)

# pylint: disable=invalid-name, no-self-use

api = AuthDto.api
auth = AuthDto.auth
response = ResponseDto.response


@api.route('/login')
class UserLogin(Resource):
    """User Login Resource"""

    @api.doc('/auth/login')
    @api.response(INTERNAL_SERVER_ERROR, UNKNOWN)
    @api.response(UNAUTHORIZED, EMAIL_OR_PASSWORD)
    @api.response(BAD_REQUEST, MALFORMED)
    @api.expect(auth, validate=True)
    @api.marshal_with(response, description=LOGIN_SUCCESS, skip_none=True)
    def post(self):
        """Log the user in and return an auth token"""
        return Auth.login_user(data=request.json)


@api.route('/logout')
class UserLogout(Resource):
    """User Logout Resource"""

    @api.doc('/auth/logout')
    @api.response(INTERNAL_SERVER_ERROR, UNKNOWN)
    @api.response(UNAUTHORIZED, EMAIL_OR_PASSWORD)
    @api.response(BAD_REQUEST, MALFORMED)
    @api.marshal_with(response, description=LOGOUT_SUCCESS)
    def post(self):
        """Log the user out"""
        return Auth.logout_user(data=request.headers.get('Authorization'))
