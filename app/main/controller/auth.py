from flask import request
from flask_restplus import Resource

from app.main.service.auth import Auth
from app.main.util.dto import AuthDto

api = AuthDto.api
auth = AuthDto.auth


@api.route('/login')
class UserLogin(Resource):
    """User Login Resource."""
    @api.doc('user_login')
    @api.expect(auth, validate=True)
    def post(self):
        """Log the user in and return an auth token."""
        return Auth.login_user(data=request.json)


@api.route('/logout')
class UserLogout(Resource):
    """User Logout Resource."""
    @api.doc('user_logout')
    def post(self):
        """Log the user out."""
        return Auth.logout_user(data=request.headers.get('Authorization'))
