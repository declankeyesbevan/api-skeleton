#!/usr/bin/env python

"""
Requires:
 - python 3.7+

Pre-requisites:
 - pip install -r tests/test-requirements.txt
"""

import os
import subprocess
from distutils import util

import click
from flask_migrate import Migrate, init, upgrade

from app import BLUEPRINT
from app.main import DB, create_app
from app.main.model import blacklist, user
from tests.helpers import set_up_database, tear_down_database
from tools.static_code_analysis import CyclomaticComplexity, Lint

app = create_app(os.environ.get('APP_ENV') or 'dev')
app.register_blueprint(BLUEPRINT)
app.app_context().push()

migrate = Migrate(app, DB)

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
        set_up_database(DB)
    elif action == 'upgrade':
        upgrade()
        set_up_database(DB)
    elif action == 'drop':
        tear_down_database(DB)


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


@cli.command()
def lint():
    """Calculate lintiness and create badge from score"""
    pylint = Lint()
    score = pylint.run_test()
    pylint.create_badge(score)


@cli.command()
def cc():
    """Calculate Cyclomatic Complexity and create badge from score"""
    radon = CyclomaticComplexity()
    score = radon.run_test()
    radon.create_badge(score)


if __name__ == '__main__':
    # FIXME: this is a crap solution
    # To allow migration to find models these are imported but not called. Print them so they aren't
    # unused imports which get auto-removed.
    print(blacklist)
    print(user)

    cli()
