from app.main import db
from app.main.model.blacklist import BlacklistToken
from http_codes import OK


def blacklist_token(token):
    token = BlacklistToken(token=token)
    try:
        db.session.add(token)
        db.session.commit()
    except Exception as exc:
        return dict(status='fail', message=exc), OK
    else:
        return dict(status='success', message='Successfully logged out.'), OK
