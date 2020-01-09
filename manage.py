#!/usr/bin/env python

import os
import subprocess

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import blueprint
from app.main import create_app, db
from app.main.model import blacklist, user
from tests.helpers import set_up_database, tear_down_database

app = create_app(os.getenv('APP_ENV') or 'dev')
app.register_blueprint(blueprint)

app.app_context().push()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

docker_compose = ['docker-compose', '-f', 'tests/docker-compose.yml']

# FIXME: this is a crap solution
# To allow migration to find models these are imported but not called. Print them so they aren't
# unused imports which get auto-removed.
print(blacklist)
print(user)


@manager.command
def run():
    app.run()


@manager.command
def local_db_up():
    docker_compose.extend(['up', '-d'])
    result = subprocess.run(docker_compose)
    if result.returncode != 0:
        exit(result.returncode)
    set_up_database(db)
    exit(result.returncode)


@manager.command
def local_db_down():
    tear_down_database(db)
    docker_compose.extend(['stop'])
    result = subprocess.run(docker_compose)
    exit(result.returncode)


@manager.command
def test():
    """Runs the automated tests."""
    # FIXME: would prefer to use pytest.main(['tests']) but there is a known coverage bug in pytest
    # https://github.com/pytest-dev/pytest/issues/1357
    # TODO: change to CLI argument instead once Flask Script replaced with Click
    if os.environ.get('INTEGRATION'):
        result = subprocess.run(['pytest', 'tests/integration', 'tests/contract', '--no-cov'])
    else:
        result = subprocess.run(['pytest', 'tests/unit', 'tests/component'])
    return result.returncode


if __name__ == '__main__':
    manager.run()
