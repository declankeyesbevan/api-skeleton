# pylint: disable=invalid-name, no-self-use, logging-fstring-interpolation

import logging

from flask import request
from flask._compat import text_type as _
from flask_jwt_simple import jwt_optional, jwt_required
from flask_restx import Resource
from werkzeug.exceptions import NotFound

from app.i18n.base import (
    EMAIL_ALREADY_EXISTS, EMAIL_UPDATED, JWT_ERROR, JWT_UNPROCESSABLE, MALFORMED,
    USERS_LIST_SUCCESS,
    USER_CREATE_SUCCESS, USER_EXISTS,
    USER_LIST_SUCCESS, USER_NOT_FOUND,
)
from app.main.data.dto import BaseDto, ResponseDto, UserDto
from app.main.service.auth import jwt_valid
from app.main.service.user import get_user_by_id, get_all_users, save_new_user, update_email
from app.responses import (
    BAD_REQUEST, CONFLICT, INTERNAL_SERVER_ERROR, NOT_FOUND, UNAUTHORIZED, UNKNOWN,
    UNPROCESSABLE_ENTITY,
)
from app.security import remove

logger = logging.getLogger('api-skeleton')
api = UserDto.api
user = UserDto.user
base = BaseDto.base
response = ResponseDto.response


@api.route('')
class UserList(Resource):
    """User List Resource"""

    @jwt_required
    @jwt_valid
    @api.doc('/users')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(UNPROCESSABLE_ENTITY, _(JWT_UNPROCESSABLE))
    @api.response(UNAUTHORIZED, _(JWT_ERROR))
    @api.marshal_with(response, description=_(USERS_LIST_SUCCESS), skip_none=True)
    def get(self):
        """List all users"""
        logger.info("Getting all users")
        return get_all_users()

    @jwt_optional
    @api.doc('/users')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(CONFLICT, _(USER_EXISTS))
    @api.response(BAD_REQUEST, _(MALFORMED))
    @api.expect(user, validate=True)
    @api.marshal_with(response, description=_(USER_CREATE_SUCCESS), skip_none=True)
    def post(self):
        """Create a new user"""
        logger.info(f"Creating new user: {remove(request.json, ['password'])}")
        return save_new_user(request.json)


@api.route('/<public_id>')
@api.param('public_id', description='User identifier')
class User(Resource):
    """User Resource"""

    @jwt_required
    @jwt_valid
    @api.doc('/users/:public_id')
    @api.response(UNPROCESSABLE_ENTITY, _(JWT_UNPROCESSABLE))
    @api.response(NOT_FOUND, _(USER_NOT_FOUND))
    @api.response(UNAUTHORIZED, _(JWT_ERROR))
    @api.marshal_with(response, description=_(USER_LIST_SUCCESS), skip_none=True)
    def get(self, public_id):
        """Get a user given their identifier."""
        logger.info(f"Getting user with public_id: {public_id}")
        user_to_get = get_user_by_id(public_id)
        if not user_to_get:
            raise NotFound(USER_NOT_FOUND)
        return user_to_get


@api.route('/email/change')
class EmailChange(Resource):
    """Email Change Resource"""

    @jwt_required
    @jwt_valid
    @api.doc('/users/email/change')
    @api.response(UNPROCESSABLE_ENTITY, _(JWT_UNPROCESSABLE))
    @api.response(CONFLICT, _(EMAIL_ALREADY_EXISTS))
    @api.response(UNAUTHORIZED, _(JWT_ERROR))
    @api.expect(base, validate=True)
    @api.marshal_with(response, description=_(EMAIL_UPDATED), skip_none=True)
    def post(self):
        """Change a user's email address."""
        logger.info(f"Updating to new user email address: {request.json.get('email')}")
        return update_email(request.json.get('email'))
