from flask_jwt_simple import create_jwt, decode_jwt
from flask_jwt_simple.exceptions import FlaskJWTException
from jwt import DecodeError, ExpiredSignatureError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError, Unauthorized

from app.i18n.base import JWT_BLACKLISTED, JWT_EXPIRED, JWT_INVALID
from app.main import db, flask_bcrypt
from app.main.model.blacklist import BlacklistToken


class User(db.Model):
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

    def find_user(self, filter_by):
        try:
            user = self.query.filter_by(**filter_by).first()
        except SQLAlchemyError as err:
            raise InternalServerError(f"Error finding user by {filter_by}: {err}")
        return user

    @classmethod
    def encode_auth_token(cls, user_id):
        try:
            token = create_jwt(identity=user_id)
        except FlaskJWTException as err:
            raise InternalServerError(f"Error encoding JWT token: {err}")
        else:
            return token

    @classmethod
    def decode_auth_token(cls, auth_token):
        try:
            payload = decode_jwt(auth_token)
        except ExpiredSignatureError:
            raise Unauthorized(JWT_EXPIRED)
        except DecodeError:
            raise Unauthorized(JWT_INVALID)
        else:
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                raise Unauthorized(JWT_BLACKLISTED)
            return payload['sub']

    @classmethod
    def deserialise_users(cls, users):
        return [
            dict(username=user.username, public_id=user.public_id, email=user.email) for user in
            users
        ]
