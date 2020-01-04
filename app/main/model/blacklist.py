import datetime

from app.main import db


class BlacklistToken(db.Model):
    """Token Model for storing JWT tokens."""
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    @classmethod
    def check_blacklist(cls, auth_token):
        blacklisted = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        return True if blacklisted else False
