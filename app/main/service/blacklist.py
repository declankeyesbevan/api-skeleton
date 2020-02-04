from werkzeug.exceptions import InternalServerError

from app.main.data.dao import save_changes
from app.main.model.blacklist import BlacklistToken
from app.responses import OK, responder


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
        return responder(code=OK)
