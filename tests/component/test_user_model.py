import datetime
import json

import pytest
from freezegun import freeze_time
from werkzeug.exceptions import Unauthorized

from app.main.model.user import User
from tests.data_factory import random_text, user_attributes
from tests.helpers import log_in_client_user, log_out_client_user, register_client_user


@pytest.mark.usefixtures('database')
def test_encode_auth_token(auth_token):
    # TODO: make a better test to see structure of JWT
    assert isinstance(auth_token, str)


@pytest.mark.usefixtures('database', 'database_user')
def test_decode_auth_token(client, auth_token):
    assert User.decode_auth_token(auth_token) == 1
    with freeze_time(datetime.datetime.utcnow() + datetime.timedelta(days=2)):
        with pytest.raises(Unauthorized):
            User.decode_auth_token(auth_token)
    with pytest.raises(Unauthorized):
        assert User.decode_auth_token(random_text())

    user = user_attributes()
    register_client_user(client, user)

    # Don't use fixture as we need a token that's been blacklisted in the database.
    login_response = log_in_client_user(client, user)
    data = json.loads(login_response.data.decode()).get('data')
    token = data.get('token')
    headers = dict(Authorization=f"Bearer {token}")

    log_out_client_user(client, headers)
    with pytest.raises(Unauthorized):
        User.decode_auth_token(token)
