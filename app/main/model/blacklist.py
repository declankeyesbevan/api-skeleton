# pylint: disable=invalid-name, logging-fstring-interpolation

"""
Creates a SQLAlchemy model for blacklisting JWT tokens and checking if tokens are blacklisted.
Initialising the object with a JWT will blacklist it. For example, when a user logs out, their token
is blacklisted. A method is provided to check if a passed token is blacklisted.
"""

import dataclasses
import datetime
import logging

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError

from app.i18n.base import TOKEN_BLACKLIST
from app.main import db

logger = logging.getLogger('api-skeleton')


@dataclasses.dataclass
class BlacklistToken(db.Model):
    """
    Pass a JWT to initialise an object and the token will be added to the blacklist_tokens database
    table.
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.utcnow()

    @classmethod
    def check_blacklist(cls, auth_token):
        """
        Pass a JWT to check if it has been blacklisted i.e. is it in the blacklist_tokens database
        table.
        :param auth_token: string containing a JWT token
        :return: boolean of blacklist state
        :raise: werkzeug.InternalServerError: if a SQLAlchemyError is caught
        """
        try:
            blacklisted = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        except SQLAlchemyError as err:
            logger.critical(f"SQLAlchemyError: {err}", exc_info=True)
            raise InternalServerError(TOKEN_BLACKLIST) from None
        else:
            return bool(blacklisted)
