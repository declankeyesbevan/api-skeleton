#!/usr/bin/env python

"""
This script is for zero-config running of the test suite on the GitLab Continuous Integration
server.

When the environment variable LOCAL is set to true, the runner will start the Docker Postgres
database container, upgrade the DDL and start a Flask app. This allows for local debugging of an
"integrated" database and "deployed" HTTP Flask endpoint. The Flask app is in separate daemon thread
because otherwise it would begin and never return to the script as it is a foreground process.

The goal is to avoid writing this in a BASH script - because that existed previously and it was
horrible. This drops down into the shell when necessary but allows a nice high-level Python wrapper.
It calls Python from Python so make sure you have the below version in your path.

Requires:
 - python 3.8+

Pre-requisites:
 - python3 -m venv runnervenv
 - source runnervenv/bin/activate
 - pip install --upgrade pip
 - pip install -r tools/tools-requirements.txt
"""

import os
import subprocess
import sys
from distutils import util
from pathlib import Path
from threading import Thread

import click
from dotenv import load_dotenv

python_executable = sys.executable
runner = subprocess.run
app_dependencies = 'requirements.txt'
test_dependencies = 'tests/tests-requirements.txt'


@click.command()
def run():
    _set_up_environment()
    _run_tests()


def _set_up_environment():
    click.echo('Creating venv/build directory and installing app dependencies')

    commands = [
        ['-V'],
        ['-m', 'pip', 'install', '-r', app_dependencies],
    ]
    for command in commands:
        execute = [python_executable]
        execute.extend(command)
        runner(execute)

    Path(f'{os.environ.get("BUILD_DIR", "build")}').mkdir(parents=True, exist_ok=True)


def _run_tests():
    click.echo('Running in-memory then deployed test suites')
    click.echo('Installing test dependencies')
    runner([python_executable, '-m', 'pip', 'install', '-r', test_dependencies])
    for env_file, integrated in {'test-in-memory': False, 'test-deployed': True}.items():
        message = 'deployed' if integrated else 'in-memory'
        click.echo(f'Running {message} test suite')
        local = os.environ.get('LOCAL') and bool(util.strtobool(os.environ.get('LOCAL')))
        if local and integrated:
            _start_local_dependencies()
        _run_manager_commands('test', options=['--integrated', str(integrated).lower()])

    for static_analyser in ['lint', 'cc', 'lloc']:
        _run_manager_commands(static_analyser)


def _start_local_dependencies():
    _start_docker_database()
    _start_flask_app()


def _start_docker_database():
    click.echo("Starting Docker database")
    database = {
        'db-container': ['--state', 'up'],
        'db-ddl': ['--action', 'upgrade', '--environment', 'deployed'],
    }
    for command, options in database.items():
        _run_manager_commands(command, options=options)


def _start_flask_app():
    click.echo("Starting Flask daemon app")
    for var_file in ['common', 'test-deployed.env']:
        load_dotenv(dotenv_path=Path('configuration') / f'{var_file}.env', override=True)
    # Cannot import at start of module execution as env vars haven't loaded.
    from app import blueprint
    from app.main import create_app
    app = create_app('test-deployed')
    app.register_blueprint(blueprint)
    app.app_context().push()
    # The Flask app must be run as a daemon thread because it runs in the foreground and will not
    # return control to this script if invoked in this process. As a daemon, it will exit when this
    # script's process ends.
    thread = Thread(target=app.run)
    thread.daemon = True
    thread.start()


def _run_manager_commands(command, options=None):
    # Runs commands in the manager script e.g.
    # To run the Flask app:
    #   python api_skeleton.py run
    # To start the database container:
    #   python api_skeleton.py db-container --state up
    execute = [python_executable, 'api_skeleton.py', command]
    if options:
        execute.extend(options)
    result = runner(execute)
    if result.returncode:  # Fail the build if we get exceptions or failed tests.
        exit(result.returncode)


if __name__ == '__main__':
    run()
