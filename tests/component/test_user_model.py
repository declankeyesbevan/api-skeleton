import datetime
import json

import pytest
from freezegun import freeze_time

from app.main.model.user import User
from tests.data_factory import random_text, user_attributes
from tests.helpers import log_in_user, log_out_user, register_client_user


@pytest.mark.usefixtures('database')
def test_encode_auth_token(auth_token):
    assert isinstance(auth_token, bytes)


@pytest.mark.usefixtures('database', 'database_user')
def test_decode_auth_token(client, auth_token):
    assert User.decode_auth_token(auth_token.decode('utf-8')) == 1
    with freeze_time(datetime.datetime.utcnow() + datetime.timedelta(days=2)):
        assert User.decode_auth_token(
            auth_token.decode('utf-8')
        ) == 'Signature expired. Please log in again.'
    assert User.decode_auth_token(random_text()) == 'Invalid token. Please log in again.'

    user = user_attributes()
    register_client_user(client, user)
    login_response = log_in_user(client, user)
    token = json.loads(login_response.data.decode())['Authorization']
    headers = dict(
        Authorization=f"Bearer {token}"
    )
    log_out_user(client, headers)
    assert User.decode_auth_token(token) == 'Token blacklisted. Please log in again.'
