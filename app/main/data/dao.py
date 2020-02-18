from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError

from app.i18n.base import SAVING_TO_DATABASE
from app.main import db


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except SQLAlchemyError as err:
        raise InternalServerError(f"{SAVING_TO_DATABASE}: {err}")
