import datetime

import pytest

from app.main import db
from app.main.model.user import User


@pytest.mark.usefixtures('handle_db')
def test_encode_auth_token():
    user = User(
        email='test@test.com',
        password='test',
        registered_on=datetime.datetime.utcnow()
    )
    # FIXME: remove direct call to DB
    db.session.add(user)
    db.session.commit()
    auth_token = user.encode_auth_token(user.id)
    assert isinstance(auth_token, bytes)


@pytest.mark.usefixtures('handle_db')
def test_decode_auth_token():
    user = User(
        email='test@test.com',
        password='test',
        registered_on=datetime.datetime.utcnow()
    )
    # FIXME: remove direct call to DB
    db.session.add(user)
    db.session.commit()
    auth_token = user.encode_auth_token(user.id)
    assert isinstance(auth_token, bytes)
    assert User.decode_auth_token(auth_token.decode('utf-8')) == 1
