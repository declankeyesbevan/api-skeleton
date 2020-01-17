import dataclasses
import datetime

from app.main import DB


@dataclasses.dataclass
class BlacklistToken(DB.Model):
    """Token Model for storing JWT tokens."""
    __tablename__ = 'blacklist_tokens'

    # Seriously pylint?!
    # pylint: disable=invalid-name
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    # pylint: enable=invalid-name
    token = DB.Column(DB.String(500), unique=True, nullable=False)
    blacklisted_on = DB.Column(DB.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    @classmethod
    def check_blacklist(cls, auth_token):
        blacklisted = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        return bool(blacklisted)
