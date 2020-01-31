from flask import request
from flask_restplus import Resource

from app.main.data.dto import UserDto
from app.main.service.user import get_a_user, get_all_users, save_new_user
from app.responses import (
    BAD_REQUEST, CONFLICT, CREATED, CREATE_SUCCESS, INTERNAL_SERVER_ERROR, MALFORMED, NOT_FOUND, OK,
    UNKNOWN, USERS_LIST_SUCCESS, USER_EXISTS, USER_LIST_SUCCESS, USER_NOT_FOUND,
)

# pylint: disable=invalid-name, no-self-use

api = UserDto.api
user = UserDto.user


@api.route('')
class UserList(Resource):
    """User List Resource"""

    @api.response(OK, USERS_LIST_SUCCESS)
    @api.doc('/users')
    @api.marshal_list_with(user, skip_none=True)
    def get(self):
        """List all users"""
        return get_all_users()

    @api.response(CREATED, CREATE_SUCCESS)
    @api.response(BAD_REQUEST, MALFORMED)
    @api.response(CONFLICT, USER_EXISTS)
    @api.response(INTERNAL_SERVER_ERROR, UNKNOWN)
    @api.doc('/users')
    @api.expect(user, validate=True)
    def post(self):
        """Create a new user"""
        return save_new_user(data=request.json)


@api.route('/<public_id>')
@api.param('public_id', 'The User identifier')
class User(Resource):
    """User Resource"""

    @api.response(OK, USER_LIST_SUCCESS)
    @api.response(NOT_FOUND, USER_NOT_FOUND)
    @api.doc('/users/:public_id')
    @api.marshal_with(user, skip_none=True)
    def get(self, public_id):
        """Get a user given their identifier."""
        user_to_get = get_a_user(public_id)
        if not user_to_get:
            api.abort(NOT_FOUND)
        return user_to_get
