import datetime

from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError, decode, encode
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError, Unauthorized

from app.config import KEY
from app.main import DB, FLASK_BCRYPT
from app.main.model.blacklist import BlacklistToken
from app.responses import INVALID_TOKEN, SIGNATURE_EXPIRED, TOKEN_BLACKLISTED


class User(DB.Model):
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

    def find_user_by_email(self, data):
        try:
            user = self.query.filter_by(email=data.get('email')).first()
        except SQLAlchemyError as err:
            raise InternalServerError(f"Error finding user by email: {err}")
        return user

    @classmethod
    def encode_auth_token(cls, user_id):
        time_now = datetime.datetime.utcnow()
        payload = dict(
            exp=time_now + datetime.timedelta(days=1, seconds=5), iat=time_now, sub=user_id
        )
        try:
            token = encode(payload, KEY, algorithm='HS256')
        except PyJWTError as err:
            raise InternalServerError(f"Error encoding JWT token: {err}")
        else:
            return token

    @classmethod
    def decode_auth_token(cls, auth_token):
        try:
            payload = decode(auth_token, KEY)
        except ExpiredSignatureError:
            raise Unauthorized(SIGNATURE_EXPIRED)
        except InvalidTokenError:
            raise Unauthorized(INVALID_TOKEN)
        else:
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                raise Unauthorized(TOKEN_BLACKLISTED)
            return payload['sub']

    @classmethod
    def deserialise_users(cls, users):
        return [
            dict(username=user.username, public_id=user.public_id, email=user.email) for user in
            users
        ]
