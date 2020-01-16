from app.main.data.dao import save_changes
from app.main.model.blacklist import BlacklistToken
from app.responses import LOGOUT_SUCCESS_PAYLOAD, UNKNOWN_ERROR_PAYLOAD


def blacklist_token(token):
    token = BlacklistToken(token=token)
    try:
        save_changes(token)
    except Exception:
        return UNKNOWN_ERROR_PAYLOAD
    else:
        return LOGOUT_SUCCESS_PAYLOAD
