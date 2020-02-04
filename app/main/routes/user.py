from flask import request
from flask_restplus import Resource
from werkzeug.exceptions import NotFound

from app.main.data.dto import ResponseDto, UserDto
from app.main.service.user import get_a_user, get_all_users, save_new_user
from app.responses import (
    BAD_REQUEST, CONFLICT, INTERNAL_SERVER_ERROR, MALFORMED, NOT_FOUND, UNKNOWN, USERS_LIST_SUCCESS,
    USER_CREATE_SUCCESS, USER_EXISTS, USER_LIST_SUCCESS, USER_NOT_FOUND,
)

# pylint: disable=invalid-name, no-self-use

api = UserDto.api
user = UserDto.user
response = ResponseDto.response


@api.route('')
class UserList(Resource):
    """User List Resource"""

    @api.doc('/users')
    @api.response(INTERNAL_SERVER_ERROR, UNKNOWN)
    @api.marshal_with(response, description=USERS_LIST_SUCCESS, skip_none=True)
    def get(self):
        """List all users"""
        return get_all_users()

    @api.doc('/users')
    @api.response(INTERNAL_SERVER_ERROR, UNKNOWN)
    @api.response(CONFLICT, USER_EXISTS)
    @api.response(BAD_REQUEST, MALFORMED)
    @api.expect(user, validate=True)
    @api.marshal_with(response, description=USER_CREATE_SUCCESS, skip_none=True)
    def post(self):
        """Create a new user"""
        return save_new_user(data=request.json)


@api.route('/<public_id>')
@api.param('public_id', description='The User identifier')
class User(Resource):
    """User Resource"""

    @api.doc('/users/:public_id')
    @api.response(NOT_FOUND, USER_NOT_FOUND)
    @api.marshal_with(response, description=USER_LIST_SUCCESS, skip_none=True)
    def get(self, public_id):
        """Get a user given their identifier."""
        user_to_get = get_a_user(public_id)
        if not user_to_get:
            raise NotFound(USER_NOT_FOUND)
        return user_to_get
