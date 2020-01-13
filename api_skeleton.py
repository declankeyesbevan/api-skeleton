#!/usr/bin/env python

"""
Requires:
 - Python 3.6+

Pre-requisites:
 - pip install -r dev/dev-requirements.txt
"""

import os
import subprocess
from distutils import util

import click
from flask_migrate import Migrate, init, upgrade

from app import blueprint
from app.main import create_app, db
from app.main.model import blacklist, user
from tests.helpers import set_up_database, tear_down_database

app = create_app(os.environ.get('APP_ENV') or 'dev')
app.register_blueprint(blueprint)
app.app_context().push()

migrate = Migrate(app, db)

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
@click.option('--action', '-a', required=True, type=click.Choice(['init', 'upgrade', 'drop']))
def db_ddl(action):
    if action == 'init':
        init()
        set_up_database(db)
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
    return (runner(integration_tests) if integrated else runner(non_integration_tests)).returncode


if __name__ == '__main__':
    # FIXME: this is a crap solution
    # To allow migration to find models these are imported but not called. Print them so they aren't
    # unused imports which get auto-removed.
    print(blacklist)
    print(user)

    cli()
