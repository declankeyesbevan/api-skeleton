# pylint: disable=logging-fstring-interpolation

import logging

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError

from app.i18n.base import SAVING_TO_DATABASE
from app.main import db

logger = logging.getLogger('api-skeleton')


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except SQLAlchemyError as err:
        logger.critical(f"SQLAlchemyError: {err}", exc_info=True)
        raise InternalServerError(SAVING_TO_DATABASE) from None
