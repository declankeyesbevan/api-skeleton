import datetime
import json

import pytest
from freezegun import freeze_time
from werkzeug.exceptions import Unauthorized

from app.main import db
from app.main.model.user import User
from tests.data_factory import random_text, user_attributes
from tests.helpers import add_to_database, authenticate_client_user, register_user


@pytest.mark.usefixtures('database')
def test_encode_auth_token(auth_token):
    # TODO: make a better test to see structure of JWT
    assert isinstance(auth_token, str)


@pytest.mark.usefixtures('database')
def test_decode_auth_token(client, user_obj):
    add_to_database(db, user_obj)
    auth_token = User.encode_auth_token(user_obj.id)
    assert User.decode_auth_token(auth_token) == 1
    with freeze_time(datetime.datetime.utcnow() + datetime.timedelta(days=2)):
        with pytest.raises(Unauthorized):
            User.decode_auth_token(auth_token)
    with pytest.raises(Unauthorized):
        assert User.decode_auth_token(random_text())

    user_data = user_attributes()  # FIXME: using fixture for this causes user conflict error
    register_user(json.dumps(user_data), client=client)

    # Don't use fixture as we need a token that's been blacklisted in the database.
    response = authenticate_client_user(client, 'login', data=json.dumps(user_data))
    data = response.json.get('data')
    token = data.get('token')
    headers = dict(Authorization=f"Bearer {token}")

    authenticate_client_user(client, 'logout', headers=headers)
    with pytest.raises(Unauthorized):
        User.decode_auth_token(token)
