# pylint: disable=missing-class-docstring

"""
Data Transfer Object for marshalling and un-marshalling data. Flask-RESTX uses decorators on routes
to execute this process. To un-marshall and validate the request use the 'expect' decorator. To
marshall the response use the 'marshall_with' decorator. The following classes are the models used
by Flask-RESTX for this.
See this documentation for further detail:
https://flask-restx.readthedocs.io/en/latest/swagger.html#the-api-expect-decorator
https://flask-restx.readthedocs.io/en/latest/swagger.html#the-api-marshal-with-decorator
"""

import dataclasses

from flask_restx import Namespace, fields

USERNAME_EMAIL_MINIMUM_LENGTH = 6
COMMON = dict(
    password=fields.String(
        required=True,
        allow_null=False,
        description='Password'
    ),
    email=fields.String(
        required=True,
        allow_null=False,
        min_length=USERNAME_EMAIL_MINIMUM_LENGTH,
        description='User email address'
    ),
)
USERNAME = dict(
    username=fields.String(
        required=True,
        allow_null=False,
        min_length=USERNAME_EMAIL_MINIMUM_LENGTH,
        description='User username'
    ),
)


@dataclasses.dataclass(frozen=True)
class EmailDto:
    api = Namespace('email', description='Email object')
    email = api.model('email', dict(email=COMMON.get('email')))


@dataclasses.dataclass(frozen=True)
class PasswordDto:
    api = Namespace('password', description='Password object')
    password = api.model('password', dict(password=COMMON.get('password')))


@dataclasses.dataclass(frozen=True)
class AuthDto:
    api = Namespace('auth', description='Authentication related operations')
    auth = api.model('auth', COMMON)
    api.add_model('auth', auth)


@dataclasses.dataclass(frozen=True)
class UserDto:
    api = Namespace('users', description='User related operations')
    user = AuthDto.auth.inherit('user', USERNAME)
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
