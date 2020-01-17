import pytest

from app.main import DB
from tests.data_factory import user_attributes, user_model
from tests.helpers import add_to_database, set_up_database, tear_down_database


@pytest.mark.local
def test_user_to_db():
    """
    This does the same thing as these database fixtures but directly to be more explicit:
    # database()
    # user_data()
    # user_obj()
    # database_user()
    """
    set_up_database(DB)

    user_data = user_attributes()
    user_obj = user_model(user_data)
    add_to_database(DB, user_obj)

    tear_down_database(DB)
