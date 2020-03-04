import json
import os
from smtpd import DebuggingServer
from types import SimpleNamespace

FLASK_SERVER = 'http://localhost.localdomain:5000'
FIRST = 0
SECOND = 1
JSON_INDENT = 4
BUILD_DIR = os.environ.get('BUILD_DIR', 'build')
AUTH_CONFIRM_URL = f'{FLASK_SERVER}/auth/confirm/'
AUTH_RESET_URL = f'{FLASK_SERVER}/auth/reset/'


class CustomSMTPServer(DebuggingServer):

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        simple_namespace = SimpleNamespace()
        simple_namespace.peer = peer
        simple_namespace.mailfrom = mailfrom
        simple_namespace.rcpttos = rcpttos
        values = self._split_body(data)
        self._write_mail_to_file(values)

    @classmethod
    def _split_body(cls, data):
        values = dict()
        for line in data.decode('utf-8').splitlines():
            for splitter in ['Subject: ', 'From: ', 'To: ']:
                if line.startswith(splitter):
                    values[splitter.lower().split(':')[FIRST]] = line.split(splitter)[SECOND]
            for url in [AUTH_CONFIRM_URL, AUTH_RESET_URL]:
                if line.startswith(url):
                    values['token'] = line.split(url)[SECOND]
        return values

    @classmethod
    def _write_mail_to_file(cls, values):
        with open(f'{BUILD_DIR}/{values.get("to").split("@")[FIRST]}.json', 'w') as email_file:
            json.dump(values, email_file, ensure_ascii=False, indent=JSON_INDENT)
