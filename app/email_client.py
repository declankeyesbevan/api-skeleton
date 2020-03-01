import json
import logging
import os

from flask import current_app, render_template, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from app.i18n.base import CONFIRM, PLAINTEXT_EMAIL_BODY
from app.main import mail
from app.utils import FIRST
from tools.email_server import SECOND

logger = logging.getLogger('api-skeleton')


def send_confirmation_email(user_email):
    logger.info(f"Sending confirmation email to: {user_email}")

    confirm_serialiser = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    confirm_url = url_for(
        'api.auth_email_confirm',
        confirmation_token=confirm_serialiser.dumps(
            user_email, salt=current_app.config['EMAIL_SALT']
        ),
        _external=True
    )
    html = render_template('email_confirmation.html', confirm_url=confirm_url)

    sender = current_app.config['ADMIN']
    text_body = PLAINTEXT_EMAIL_BODY.format(url=confirm_url, email=sender)
    _send_email(CONFIRM, sender, [user_email], text_body, html)


def _send_email(subject, sender, recipients, text_body, html_body):
    testing = current_app.config['TESTING']
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg) if not testing else _intercept_test_mail(msg, recipients)


def _intercept_test_mail(msg, recipients):
    values = dict()
    preferred_url_scheme = current_app.config['PREFERRED_URL_SCHEME']
    server_name = current_app.config['SERVER_NAME']
    auth_confirm_url = f'{preferred_url_scheme}://{server_name}/auth/confirm/'

    with mail.record_messages() as outbox:
        mail.send(msg)
        body = outbox[FIRST].body

    for line in body.splitlines():
        if line.startswith(auth_confirm_url):
            values['token'] = line.split(auth_confirm_url)[SECOND]

    _write_mail_to_file(recipients, values)


def _write_mail_to_file(recipients, values):
    build_dir = os.environ.get('BUILD_DIR', 'build')
    with open(f'{build_dir}/{recipients[FIRST].split("@")[FIRST]}.json', 'w') as email_file:
        json.dump(values, email_file, ensure_ascii=False, indent=4)
