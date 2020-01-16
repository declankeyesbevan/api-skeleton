from app.http_codes import OK
from app.main import db
from app.main.model.blacklist import BlacklistToken


def blacklist_token(token):
    token = BlacklistToken(token=token)
    try:
        db.session.add(token)
        db.session.commit()
    except Exception as exc:
        return dict(status='fail', message=exc), OK
    else:
        return dict(status='success', message='Successfully logged out.'), OK
