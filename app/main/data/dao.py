from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError

from app.main import DB


def save_changes(data):
    try:
        DB.session.add(data)
        DB.session.commit()
    except SQLAlchemyError as err:
        raise InternalServerError(f"Error saving to database: {err}")
