# pylint: disable=logging-fstring-interpolation, missing-class-docstring, missing-function-docstring

"""
Class which defines a SQLAlchemy user object.
"""

import logging

from flask_jwt_simple import get_jwt
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError, Unauthorized

from app.i18n.base import FINDING_USER, JWT_INSUFFICIENT, JWT_REQUIRED
from app.main import db, flask_bcrypt

logger = logging.getLogger('api-skeleton')


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    public_id = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))
    email_confirmation_sent_on = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    email_confirmed_on = db.Column(db.DateTime, nullable=True)

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
            logger.critical(f"SQLAlchemyError: {err}", exc_info=True)
            raise InternalServerError(f"{FINDING_USER}: {filter_by}") from None
        return user

    def should_create_admin(self, data):
        users_exist = self.query.all()
        if not users_exist:
            should_create = True  # First user becomes Admin by default
        else:
            should_create = data.get('admin', False)
            if should_create:
                jwt_data = get_jwt()
                if not jwt_data:
                    raise Unauthorized(JWT_REQUIRED)
                if jwt_data.get('roles') != 'admin':
                    raise Unauthorized(JWT_INSUFFICIENT)
        return should_create
