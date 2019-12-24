import os

import pytest
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from pytest import ExitCode

from app import blueprint
from app.main import create_app, db
from app.main.model import blacklist, user

app = create_app(os.getenv('BOILERPLATE_ENV') or 'dev')
app.register_blueprint(blueprint)

app.app_context().push()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

# To allow migration to find models these are imported but not called. Print them so they aren't
# unused imports which get auto-removed.
print(blacklist)
print(user)


@manager.command
def run():
    app.run()


@manager.command
def test():
    """Runs the unit tests."""
    result = pytest.main(['tests', '--cov-report', 'term-missing', '--cov=app'])
    return 0 if result == ExitCode.OK else 1


if __name__ == '__main__':
    manager.run()
