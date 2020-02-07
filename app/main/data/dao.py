from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError

from app.main import db


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except SQLAlchemyError as err:
        raise InternalServerError(f"Error saving to database: {err}")
