import dataclasses

from flask_restplus import Namespace, fields

COMMON = dict(
    email=fields.String(required=True, description='User email address'),
    password=fields.String(required=True, description='User password')
)


@dataclasses.dataclass(frozen=True)
class UserDto:
    api = Namespace('users', description='User related operations')
    user = api.model(
        'user',
        dict(
            email=COMMON.get('email'),
            password=COMMON.get('password'),
            username=fields.String(required=True, description='User username'),
            public_id=fields.String(description='User identifier'),
        )
    )


@dataclasses.dataclass(frozen=True)
class AuthDto:
    api = Namespace('auth', description='Authentication related operations')
    auth = api.model(
        'auth',
        dict(
            email=COMMON.get('email'),
            password=COMMON.get('password'),
        )
    )
