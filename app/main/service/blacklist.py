from app.main.model.blacklist import BlacklistToken
from app.main.util.dao import save_changes
from app.responses import FAIL, LOGOUT_SUCCESS, OK, SUCCESS


def blacklist_token(token):
    token = BlacklistToken(token=token)
    try:
        save_changes(token)
    except Exception as exc:
        return dict(status=FAIL, message=exc.args[0]), OK
    else:
        return dict(status=SUCCESS, message=LOGOUT_SUCCESS), OK
