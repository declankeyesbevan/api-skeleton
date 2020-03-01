#!/usr/bin/env python

"""
Requires:
 - python 3.7+

Pre-requisites:
 - pip install -r tests/test-requirements.txt
"""
import asyncore
import os
import subprocess
from distutils import util
from types import SimpleNamespace

import click
from flask_migrate import Migrate, init, migrate, upgrade

from app import blueprint
from app.main import create_app, db
from app.main.model import blacklist, user
from tests.helpers import set_up_database, tear_down_database
from tools.email_server import CustomSMTPServer
from tools.postman_creator import create_postman
from tools.static_code_analysis import CyclomaticComplexity, Lint, LogicalLinesOfCode

app = create_app(os.environ.get('APP_ENV') or 'dev')
app.register_blueprint(blueprint)
app.app_context().push()

Migrate(app, db)

runner = subprocess.run
docker_compose = ['docker-compose', '-f', 'tests/docker-compose.yml']
integration_tests = ['pytest', 'tests/integration', 'tests/contract', '--no-cov']
non_integration_tests = ['pytest', 'tests/unit', 'tests/component']

# Run the integration tests locally by replacing a remote database with a local Postgres Docker.
if os.environ.get('LOCAL') and bool(util.strtobool(os.environ.get('LOCAL'))):
    integration_tests.append('--runlocal')


@click.group()
def cli():
    pass


# Database Commands
@cli.command()
@click.option('--state', '-s', required=True, type=click.Choice(['up', 'down']))
def db_container(state):
    if state == 'up':
        docker_compose.extend(['up', '-d'])
        result = subprocess.run(docker_compose)
        exit(result.returncode)
    elif state == 'down':
        docker_compose.extend(['stop'])
        result = subprocess.run(docker_compose)
        exit(result.returncode)


@cli.command()
@click.option(
    '--action', '-a',
    required=True,
    type=click.Choice(['init', 'migrate', 'upgrade', 'drop'])
)
def db_ddl(action):
    if action == 'init':
        init()
        set_up_database(db)
    elif action == 'migrate':
        migrate()
    elif action == 'upgrade':
        upgrade()
        set_up_database(db)
    elif action == 'drop':
        tear_down_database(db)


# App Commands
@cli.command()
def run():
    app.run()


# Test Commands
@cli.command()
@click.option('--integrated', '-i', required=True, type=click.Choice(['true', 'false']))
def test(integrated):
    # FIXME: would prefer to use pytest.main(['tests']) but there is a known coverage bug in pytest
    # https://github.com/pytest-dev/pytest/issues/1357
    integrated = bool(util.strtobool(integrated))
    result = (runner(integration_tests) if integrated else runner(non_integration_tests))
    exit(result.returncode)


@cli.command()
def lint():
    """Calculate lintiness and create badge from score"""
    pylint = Lint()
    score = pylint.run_test()
    pylint.create_badge(score)


@cli.command()
def cc():
    """Calculate cyclomatic complexity and create badge from score"""
    radon_cc = CyclomaticComplexity()
    score = radon_cc.run_test()
    radon_cc.create_badge(score)


@cli.command()
def lloc():
    """Calculate logical lines of code and create badge from score"""
    radon_raw = LogicalLinesOfCode()
    score = radon_raw.run_test()
    radon_raw.create_badge(score)


@cli.command()
def postman():
    """Dump the API to a Postman collection"""
    create_postman(app)


@cli.command()
def mail():
    """Create a local SMTP server"""
    mail_server = 'localhost'
    mail_port = 1025
    CustomSMTPServer((mail_server, mail_port), None)
    asyncore.loop()


if __name__ == '__main__':
    # To allow flask_migrate to find models these are imported but not used. To avoid them being
    # auto removed by PyCharm when using 'Optimize Imports', pop them here so they are "used".
    simple_namespace = SimpleNamespace()
    simple_namespace.blacklist = blacklist
    simple_namespace.user = user

    cli()
