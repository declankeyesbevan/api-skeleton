import pytest

from app.main import db
from app.main.model.blacklist import BlacklistToken
from app.main.service.auth import Auth
from tests.data_factory import user_attributes, user_model
from tests.helpers import add_to_database, set_up_database, tear_down_database


@pytest.mark.local
def test_blacklist_to_db():
    """
    This does the same thing as these database fixtures but directly to be more explicit:
    # database()
    # user_data()
    # database_user()
    # auth_token()
    """
    set_up_database(db)

    user_data = user_attributes()
    database_user = user_model(user_data)
    token_obj = BlacklistToken(token=Auth.encode_auth_token(database_user))
    add_to_database(db, token_obj)

    tear_down_database(db)
