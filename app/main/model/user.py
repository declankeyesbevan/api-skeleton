import datetime

import jwt

from app.config import KEY
from app.exceptions import UnauthorisedException
from app.main import DB, FLASK_BCRYPT
from app.main.model.blacklist import BlacklistToken
from app.responses import INVALID_TOKEN, SIGNATURE_EXPIRED, TOKEN_BLACKLISTED


class User(DB.Model):
    """User Model for storing user related details."""
    __tablename__ = 'user'

    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    email = DB.Column(DB.String(255), unique=True, nullable=False)
    registered_on = DB.Column(DB.DateTime, nullable=False)
    admin = DB.Column(DB.Boolean, nullable=False, default=False)
    public_id = DB.Column(DB.String(100), unique=True)
    username = DB.Column(DB.String(50), unique=True)
    password_hash = DB.Column(DB.String(100))

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = FLASK_BCRYPT.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return FLASK_BCRYPT.check_password_hash(self.password_hash, password)

    @classmethod
    def encode_auth_token(cls, user_id):
        """Generates an Auth Token."""
        time_now = datetime.datetime.utcnow()
        payload = dict(
            exp=time_now + datetime.timedelta(days=1, seconds=5), iat=time_now, sub=user_id
        )
        try:
            token = jwt.encode(payload, KEY, algorithm='HS256')
        except Exception:
            raise
        else:
            return token

    @classmethod
    def decode_auth_token(cls, auth_token):
        """Decodes an auth token."""
        try:
            payload = jwt.decode(auth_token, KEY)
        except jwt.ExpiredSignatureError:
            raise UnauthorisedException(SIGNATURE_EXPIRED)
        except jwt.InvalidTokenError:
            raise UnauthorisedException(INVALID_TOKEN)
        else:
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                raise UnauthorisedException(TOKEN_BLACKLISTED)
            return payload['sub']

    @classmethod
    def deserialise_users(cls, users):
        # FIXME: figure out how to combine response and DTO or use marshmallow
        return [
            dict(username=user.username, public_id=user.public_id, email=user.email) for user in
            users
        ]
