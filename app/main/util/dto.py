from flask_restplus import Namespace, fields

common = dict(
    email=fields.String(required=True, description='User email address'),
    password=fields.String(required=True, description='User password')
)


class UserDto:
    api = Namespace('user', description='user related operations')
    user = api.model(
        'user',
        dict(
            email=common.get('email'),
            username=fields.String(required=True, description='User username'),
            password=common.get('password'),
            public_id=fields.String(description='User identifier'),
        )
    )


class AuthDto:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model(
        'auth_details',
        dict(
            email=common.get('email'),
            password=common.get('password'),
        )
    )
