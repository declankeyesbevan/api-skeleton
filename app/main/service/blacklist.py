# pylint: disable=try-except-raise

"""
Uses the SQLAlchemy model for blacklisting JWT tokens.
"""

from werkzeug.exceptions import InternalServerError

from app.main.data.dao import save_changes
from app.main.model.blacklist import BlacklistToken
from app.responses import OK, responder


def blacklist_token(token):
    """
    Pass a JWT and it will initialise a BlacklistToken SQLAlchemy object and then write the changes
    to the database.
    :param token: string containing a JWT token
    :return: dict containing the HTTP success code
    :raise: werkzeug.InternalServerError: if a SQLAlchemyError is caught
    """
    try:
        token = BlacklistToken(token=token)
    except InternalServerError:
        raise

    try:
        save_changes(token)
    except InternalServerError:
        raise
    else:
        return responder(code=OK)
