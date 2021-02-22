# pylint: disable=logging-fstring-interpolation

"""
Data Access Object helper functions to interact with the database.
"""

import logging

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError

from app.i18n.base import SAVING_TO_DATABASE
from app.main import db

logger = logging.getLogger('api-skeleton')


def save_changes(data):
    """
    Pass in data to be saved to the database.
    :param data: SQLAlchemy model representing data
    :raise: werkzeug.InternalServerError: if a SQLAlchemyError is caught
    """
    try:
        db.session.add(data)
        db.session.commit()
    except SQLAlchemyError as err:
        logger.critical(f"SQLAlchemyError: {err}", exc_info=True)
        raise InternalServerError(SAVING_TO_DATABASE) from None
