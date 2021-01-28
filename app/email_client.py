# pylint: disable=logging-fstring-interpolation, no-name-in-module, expression-not-assigned

import json
import logging
import os

from flask import current_app, render_template, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from app.i18n.base import (
    EMAIL_CONFIRM, PASSWORD_RESET, PLAINTEXT_EMAIL_CONFIRMATION_BODY, PLAINTEXT_PASSWORD_RESET_BODY,
)
from app.main import mail
from app.utils import FIRST, JSON_INDENT
from tools.email_server import SECOND

logger = logging.getLogger('api-skeleton')


def send_confirmation_email(user_email):
    logger.info(f"Sending confirmation email to: {user_email}")

    attributes = dict(
        base_url='users_email_confirm',
        user_email=user_email,
        salt=current_app.config['EMAIL_CONFIRMATION_SALT'],
        template='email_confirmation',
        plain_body=PLAINTEXT_EMAIL_CONFIRMATION_BODY,
    )
    html, plain = _compose_email(**attributes)
    _send_email(EMAIL_CONFIRM, current_app.config['ADMIN'], [user_email], html, plain)


def send_password_reset_email(user_email):
    logger.info(f"Sending password reset email to: {user_email}")

    attributes = dict(
        base_url='auth_password_reset_confirm',
        user_email=user_email,
        salt=current_app.config['PASSWORD_RESET_SALT'],
        template='password_reset',
        plain_body=PLAINTEXT_PASSWORD_RESET_BODY,
    )
    html, plain = _compose_email(**attributes)
    _send_email(PASSWORD_RESET, current_app.config['ADMIN'], [user_email], html, plain)


def _compose_email(base_url, user_email, salt, template, plain_body):
    timed_serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    url = url_for(
        f'api.{base_url}',
        token=timed_serialiser.dumps(user_email, salt=salt),
        _external=True
    )
    html = render_template(f'{template}.html', url=url)
    plain = plain_body.format(url=url, email=current_app.config['ADMIN'])
    return html, plain


def _send_email(subject, sender, recipients, html_body, plain_body):
    testing = current_app.config['TESTING']
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    msg.body = plain_body
    mail.send(msg) if not testing else _intercept_test_mail(msg, recipients)


def _intercept_test_mail(msg, recipients):
    values = dict()
    preferred_url_scheme = current_app.config['PREFERRED_URL_SCHEME']
    server_name = current_app.config['SERVER_NAME']
    auth_confirm_url = f'{preferred_url_scheme}://{server_name}/users/email/confirm/'
    password_reset_url = f'{preferred_url_scheme}://{server_name}/auth/password/reset/'

    with mail.record_messages() as outbox:
        mail.send(msg)
        body = outbox[FIRST].body

    for line in body.splitlines():
        for url in [auth_confirm_url, password_reset_url]:
            if line.startswith(url):
                values['token'] = line.split(url)[SECOND]

    _write_mail_to_file(recipients, values)


def _write_mail_to_file(recipients, values):
    build_dir = os.environ.get('BUILD_DIR', 'build')
    with open(f'{build_dir}/{recipients[FIRST].split("@")[FIRST]}.json', 'w') as email_file:
        json.dump(values, email_file, ensure_ascii=False, indent=JSON_INDENT)
