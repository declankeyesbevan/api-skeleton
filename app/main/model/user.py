import datetime

import jwt

from app.config import key
from app.exceptions import UnauthorisedException
from app.main import db, flask_bcrypt
from app.main.model.blacklist import BlacklistToken


class User(db.Model):
    """User Model for storing user related details."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    public_id = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = flask_bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return flask_bcrypt.check_password_hash(self.password_hash, password)

    @classmethod
    def encode_auth_token(cls, user_id):
        """Generates an Auth Token."""
        time_now = datetime.datetime.utcnow()
        payload = dict(
            exp=time_now + datetime.timedelta(days=1, seconds=5), iat=time_now, sub=user_id
        )
        try:
            enc = jwt.encode(payload, key, algorithm='HS256')
        except Exception as exc:
            raise exc
        else:
            return enc

    @classmethod
    def decode_auth_token(cls, auth_token):
        """Decodes an auth token."""
        try:
            payload = jwt.decode(auth_token, key)
        except jwt.ExpiredSignatureError:
            raise UnauthorisedException('Signature expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise UnauthorisedException('Invalid token. Please log in again.')
        else:
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                raise UnauthorisedException('Token blacklisted. Please log in again.')
            return payload['sub']
