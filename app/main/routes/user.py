# pylint: disable=invalid-name, no-self-use, logging-format-interpolation

import logging

from flask import request
from flask._compat import text_type as _
from flask_jwt_simple import jwt_required
from flask_restplus import Resource
from werkzeug.exceptions import NotFound

from app.i18n.base import (
    JWT_BLACKLISTED, JWT_EXPIRED, JWT_INVALID, JWT_UNPROCESSABLE, MALFORMED, USERS_LIST_SUCCESS,
    USER_CREATE_SUCCESS, USER_EXISTS, USER_LIST_SUCCESS, USER_NOT_FOUND,
)
from app.main.data.dto import ResponseDto, UserDto
from app.main.service.user import get_a_user, get_all_users, save_new_user
from app.responses import (
    BAD_REQUEST, CONFLICT, INTERNAL_SERVER_ERROR, NOT_FOUND, UNAUTHORIZED, UNKNOWN,
    UNPROCESSABLE_ENTITY,
)
from app.security import remove

logger = logging.getLogger('api-skeleton')
api = UserDto.api
user = UserDto.user
response = ResponseDto.response


@api.route('')
class UserList(Resource):
    """User List Resource"""

    @jwt_required
    @api.doc('/users')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(UNPROCESSABLE_ENTITY, _(JWT_UNPROCESSABLE))
    @api.response(UNAUTHORIZED, _(f'{JWT_BLACKLISTED} | {JWT_EXPIRED} | {JWT_INVALID}'))
    @api.marshal_with(response, description=_(USERS_LIST_SUCCESS), skip_none=True)
    def get(self):
        """List all users"""
        logger.info(f"Getting all users")
        return get_all_users()

    @api.doc('/users')
    @api.response(INTERNAL_SERVER_ERROR, _(UNKNOWN))
    @api.response(CONFLICT, _(USER_EXISTS))
    @api.response(BAD_REQUEST, _(MALFORMED))
    @api.expect(user, validate=True)
    @api.marshal_with(response, description=_(USER_CREATE_SUCCESS), skip_none=True)
    def post(self):
        """Create a new user"""
        logger.info(f"Creating new user: {remove(request.json, ['password'])}")
        return save_new_user(data=request.json)


@api.route('/<public_id>')
@api.param('public_id', description='The User identifier')
class User(Resource):
    """User Resource"""

    @jwt_required
    @api.doc('/users/:public_id')
    @api.response(UNPROCESSABLE_ENTITY, _(JWT_UNPROCESSABLE))
    @api.response(UNAUTHORIZED, _(f'{JWT_BLACKLISTED} | {JWT_EXPIRED} | {JWT_INVALID}'))
    @api.response(NOT_FOUND, _(USER_NOT_FOUND))
    @api.marshal_with(response, description=_(USER_LIST_SUCCESS), skip_none=True)
    def get(self, public_id):
        """Get a user given their identifier."""
        logger.info(f"Getting user with public_id: {public_id}")
        user_to_get = get_a_user(public_id)
        if not user_to_get:
            raise NotFound(USER_NOT_FOUND)
        return user_to_get
