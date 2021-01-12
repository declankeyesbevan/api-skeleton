# pylint: disable=invalid-name, logging-fstring-interpolation, no-self-use

import logging

from flask import request
from flask._compat import text_type as _
from flask_jwt_simple import jwt_required
from flask_restplus import Resource

from app.i18n.base import (
    ACCOUNT_ALREADY_CONFIRMED, CONFIRMATION_FAILED, EMAIL_CONFIRMED, EMAIL_PASSWORD, JWT_ERROR,
    JWT_UNPROCESSABLE, LOGIN_SUCCESS, LOGOUT_SUCCESS, MALFORMED, PASSWORD_UPDATE_FAILED,
    USER_NOT_FOUND,
)
from app.main.data.dto import AuthDto, BaseDto, ResponseDto
from app.main.service.auth import Auth, jwt_valid
from app.responses import (
    BAD_REQUEST, CONFLICT, INTERNAL_SERVER_ERROR, NOT_FOUND, UNAUTHORIZED, UNKNOWN,
    UNPROCESSABLE_ENTITY,
)
from app.security import remove
from app.utils import SECOND

logger = logging.getLogger('api-skeleton')
api = AuthDto.api
auth = AuthDto.auth
base = BaseDto.base
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
    @jwt_valid
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
        logger.info("Logging out user")
        auth_token = request.headers.get('Authorization').split('Bearer ')[SECOND]
        return Auth.logout_user(auth_token)


@api.route('/confirm/<token>')
@api.param('token', description='Email confirmation token')
class EmailConfirm(Resource):
    """Email Confirmation Resource"""

    @api.doc('/auth/confirm/:token')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(CONFLICT, _(ACCOUNT_ALREADY_CONFIRMED))
    @api.response(UNAUTHORIZED, _(CONFIRMATION_FAILED))
    @api.marshal_with(response, description=_(EMAIL_CONFIRMED), skip_none=True)
    def post(self, token):
        logger.info("Confirming user email address")
        return Auth.confirm_email(token)


@api.route('/confirm/resend')
class ResendEmailConfirm(Resource):
    """Resend Email Confirmation Resource"""

    @api.doc('/auth/confirm/resend')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(CONFLICT, _(ACCOUNT_ALREADY_CONFIRMED))
    @api.response(NOT_FOUND, _(USER_NOT_FOUND))
    @api.expect(base, validate=True)
    @api.marshal_with(response, description=_(EMAIL_CONFIRMED), skip_none=True)
    def post(self):
        logger.info(f"Re-sending email confirmation for: {request.json.get('email')}")
        return Auth.resend_confirmation_email(request.json.get('email'))


@api.route('/reset/request')
class PasswordResetRequest(Resource):
    """Request Password Reset Resource"""

    @api.doc('/auth/reset/request')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(UNAUTHORIZED, _(PASSWORD_UPDATE_FAILED))
    @api.response(BAD_REQUEST, _(MALFORMED))
    def post(self):
        logger.info("User requesting to reset password")
        return Auth.request_password_reset(request.json)


@api.route('/reset/<token>')
class PasswordResetConfirm(Resource):
    """Password Reset Confirm Resource"""

    @api.doc('/auth/reset/:token')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(UNAUTHORIZED, _(PASSWORD_UPDATE_FAILED))
    @api.response(BAD_REQUEST, _(MALFORMED))
    def post(self, token):
        logger.info("User attempting to reset password")
        return Auth.reset_password(token, request.json)


@api.route('/change')
class PasswordChange(Resource):
    """Password Change Resource"""

    @jwt_required
    @jwt_valid
    @api.doc('/auth/change')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(UNAUTHORIZED, _(PASSWORD_UPDATE_FAILED))
    @api.response(BAD_REQUEST, _(MALFORMED))
    def post(self):
        logger.info("User attempting to change password")
        return Auth.change_password(request.json)
