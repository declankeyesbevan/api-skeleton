from distutils import util

from flask_jwt_simple import get_jwt
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError, Unauthorized

from app.i18n.base import FINDING_USER, JWT_INSUFFICIENT, JWT_REQUIRED
from app.main import db, flask_bcrypt


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
            raise InternalServerError(f"{FINDING_USER} {filter_by}: {err}")
        return user

    @classmethod
    def deserialise_users(cls, users):
        return [
            dict(username=user.username, public_id=user.public_id, email=user.email) for user in
            users
        ]

    @classmethod
    def should_create_admin(cls, data):
        users_exist = User().query.all()
        if not users_exist:
            should_create = True  # First user becomes Admin by default
        else:
            should_create = bool(util.strtobool(data.get('admin', 'false')))
            if should_create:
                jwt_data = get_jwt()
                if not jwt_data:
                    raise Unauthorized(JWT_REQUIRED)
                if jwt_data.get('roles') != 'admin':
                    raise Unauthorized(JWT_INSUFFICIENT)
        return should_create

    @classmethod
    def is_admin(cls):
        jwt_data = get_jwt()
        return jwt_data.get('roles') == 'admin', jwt_data.get('sub')
