import pytest

from app.main import db
from tests.data_factory import blacklist_token_model, user_attributes, user_model
from tests.helpers import add_to_database, set_up_database, tear_down_database


@pytest.mark.local
def test_blacklist_to_db():
    """
    This does the same thing as these database fixtures but directly to be more explicit:
    # database()
    # user_data()
    # user_obj()
    # auth_token()
    """
    set_up_database(db)

    user_data = user_attributes()
    user_obj = user_model(user_data)
    token_obj = blacklist_token_model(user_obj)
    add_to_database(db, token_obj)

    tear_down_database(db)
