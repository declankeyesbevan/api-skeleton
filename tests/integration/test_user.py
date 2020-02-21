import pytest

from app.main import db
from tests.data_factory import user_attributes, user_model
from tests.helpers import add_to_database, set_up_database, tear_down_database


@pytest.mark.local
def test_user_to_db():
    """
    This does the same thing as these database fixtures but directly to be more explicit:
    # database()
    # user_data()
    # database_user()
    """
    set_up_database(db)

    user_data = user_attributes()
    database_user = user_model(user_data)
    add_to_database(db, database_user)

    tear_down_database(db)
