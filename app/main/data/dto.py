import dataclasses

from flask_restplus import Namespace, fields


@dataclasses.dataclass(frozen=True)
class RequestDto:
    api = Namespace('request', description='Request object')
    request = api.model(
        'request',
        dict(
            email=fields.String(required=True, description='User email address'),
            password=fields.String(required=True, description='User password')
        )
    )


@dataclasses.dataclass(frozen=True)
class AuthDto:
    api = Namespace('auth', description='Authentication related operations')
    auth = RequestDto.request.inherit(
        'auth',
        dict()
    )
    api.add_model('auth', auth)


@dataclasses.dataclass(frozen=True)
class UserDto:
    api = Namespace('users', description='User related operations')
    user = RequestDto.request.inherit(
        'user',
        dict(
            username=fields.String(required=True, description='User username'),
        )
    )
    api.add_model('user', user)


@dataclasses.dataclass(frozen=True)
class ResponseDto:
    api = Namespace('response', description='Response object')
    response = api.model(
        'response',
        dict(
            status=fields.String(required=True, description='Success, fail or error'),
            data=fields.Raw(
                required=False,
                description='Dict of data or null: returned with success or fail'
            ),
            message=fields.String(required=False, description='String returned with error'),
        )
    )
    api.add_model('response', response)
