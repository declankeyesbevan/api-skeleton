import dataclasses
import datetime

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError

from app.main import db


@dataclasses.dataclass
class BlacklistToken(db.Model):
    __tablename__ = 'blacklist_tokens'

    # Seriously pylint?!
    # pylint: disable=invalid-name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # pylint: enable=invalid-name
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    @classmethod
    def check_blacklist(cls, auth_token):
        try:
            blacklisted = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        except SQLAlchemyError as err:
            raise InternalServerError(f"Error getting token blacklist: {err}")
        else:
            return bool(blacklisted)
