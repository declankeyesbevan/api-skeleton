from werkzeug.exceptions import InternalServerError

from app.main.data.dao import save_changes
from app.main.model.blacklist import BlacklistToken
from app.responses import LOGOUT_SUCCESS_PAYLOAD


def blacklist_token(token):
    try:
        token = BlacklistToken(token=token)
    except InternalServerError:
        raise

    try:
        save_changes(token)
    except InternalServerError:
        raise
    else:
        return LOGOUT_SUCCESS_PAYLOAD
