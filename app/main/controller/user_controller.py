from flask import request
from flask_restplus import Resource

from app.main.service.user_service import get_a_user, get_all_users, save_new_user
from app.main.util.dto import UserDto

api = UserDto.api
_user = UserDto.user


@api.route('/')
class UserList(Resource):
    @api.response(200, 'Users successfully listed.')
    @api.doc('list_of_registered_users')
    @api.marshal_list_with(_user, envelope='data')
    def get(self):
        """List all registered users"""
        return get_all_users()

    @api.response(409, 'User already exists.')
    @api.response(201, 'User successfully created.')
    @api.doc('create_a_new_user')
    @api.expect(_user, validate=True)
    def post(self):
        """Creates a new User"""
        data = request.json
        return save_new_user(data=data)


@api.route('/<public_id>')
@api.param('public_id', 'The User identifier')
@api.response(404, 'User not found.')
@api.response(200, 'User listed.')
class User(Resource):
    @api.doc('get_a_user')
    @api.marshal_with(_user)
    def get(self, public_id):
        """get a user given its identifier"""
        user = get_a_user(public_id)
        if not user:
            api.abort(404)
        return user
