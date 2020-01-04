from flask import request
from flask_restplus import Resource

from app.main.service.user import get_a_user, get_all_users, save_new_user
from app.main.util.dto import UserDto

api = UserDto.api
user = UserDto.user


@api.route('/')
class UserList(Resource):
    """User List Resource."""
    @api.response(200, 'Users successfully listed.')
    @api.doc('list_of_users')
    @api.marshal_list_with(user, envelope='data')
    def get(self):
        """List all users."""
        return get_all_users()

    @api.response(409, 'User already exists.')
    @api.response(400, 'Malformed user data passed.')
    @api.response(201, 'User successfully created.')
    @api.doc('create_a_new_user')
    @api.expect(user, validate=True)
    def post(self):
        """Creates a new user."""
        return save_new_user(data=request.json)


@api.route('/<public_id>')
@api.param('public_id', 'The User identifier')
class User(Resource):
    """User Resource."""
    @api.response(404, 'User not found.')
    @api.response(200, 'User successfully listed.')
    @api.doc('get_a_user')
    @api.marshal_with(user)
    def get(self, public_id):
        """Get a user given their identifier."""
        user_to_get = get_a_user(public_id)
        if not user_to_get:
            api.abort(404)
        return user_to_get
