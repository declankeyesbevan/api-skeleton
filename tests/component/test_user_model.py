import datetime
import json

import pytest
from freezegun import freeze_time
from werkzeug.exceptions import Unauthorized

from app.main.service.auth import Auth
from tests.data_factory import random_text
from tests.helpers import (
    authenticate_user, confirm_email_token, get_email_confirmation_token, register_user,
)


@pytest.mark.usefixtures('database')
def test_encode_auth_token(database_user):
    # TODO: make a better test to see structure of JWT
    auth_token = Auth.encode_auth_token(database_user)
    assert isinstance(auth_token, str)


@pytest.mark.usefixtures('database')
def test_decode_auth_token(client, database_user, user_data):
    auth_token = Auth.encode_auth_token(database_user)
    assert Auth.decode_auth_token(auth_token) == database_user.public_id
    with freeze_time(datetime.datetime.utcnow() + datetime.timedelta(days=2)):
        with pytest.raises(Unauthorized):
            Auth.decode_auth_token(auth_token)
    with pytest.raises(Unauthorized):
        assert Auth.decode_auth_token(random_text())

    register_user(json.dumps(user_data), client=client)
    token = get_email_confirmation_token(user_data)
    confirm_email_token(token, client)
    # Don't use fixture as we need a token that's been blacklisted in the database.
    response = authenticate_user('login', data=json.dumps(user_data), client=client)
    data = response.json.get('data')
    token = data.get('token')
    headers = dict(Authorization=f"Bearer {token}")

    authenticate_user('logout', headers=headers, client=client)
    with pytest.raises(Unauthorized):
        Auth.validate_token_blacklist(token)
