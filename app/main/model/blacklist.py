# pylint: disable=invalid-name

import dataclasses
import datetime

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError

from app.i18n.base import TOKEN_BLACKLIST
from app.main import db


@dataclasses.dataclass
class BlacklistToken(db.Model):
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.utcnow()

    @classmethod
    def check_blacklist(cls, auth_token):
        try:
            blacklisted = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        except SQLAlchemyError as err:
            raise InternalServerError(f"{TOKEN_BLACKLIST}: {err}")
        else:
            return bool(blacklisted)
