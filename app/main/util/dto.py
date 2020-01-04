from flask_restplus import Namespace, fields

common = dict(
    email=fields.String(required=True, description='User email address'),
    password=fields.String(required=True, description='User password')
)


class UserDto:
    api = Namespace('user', description='User related operations')
    user = api.model(
        'user',
        dict(
            email=common.get('email'),
            password=common.get('password'),
            username=fields.String(required=True, description='User username'),
            public_id=fields.String(description='User identifier'),
        )
    )


class AuthDto:
    api = Namespace('auth', description='Authentication related operations')
    auth = api.model(
        'auth',
        dict(
            email=common.get('email'),
            password=common.get('password'),
        )
    )
