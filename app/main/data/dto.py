import dataclasses

from flask_restplus import Namespace, fields


@dataclasses.dataclass(frozen=True)
class BaseDto:
    api = Namespace('base', description='Base operations')
    base = api.model(
        'base',
        dict(
            email=fields.String(required=True, description='User email address'),
            password=fields.String(required=True, description='User password')
        )
    )


api = BaseDto.api


@dataclasses.dataclass(frozen=True)
class UserDto:
    api = Namespace('users', description='User related operations')
    user = BaseDto.base.inherit(
        'user',
        dict(
            username=fields.String(required=True, description='User username'),
            public_id=fields.String(description='User identifier'),
        )
    )
    api.add_model('user', user)


@dataclasses.dataclass(frozen=True)
class AuthDto:
    api = Namespace('auth', description='Authentication related operations')
    auth = BaseDto.base.inherit(
        'auth',
    )
    api.add_model('auth', auth)
