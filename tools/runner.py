#!/usr/bin/env python

"""
This script is for zero-config running of the test suite on the GitLab Continuous Integration server
or it can be used to run the Flask development server. It loads pre-defined environment variables
from *.env files.

When the environment variable LOCAL is set to true, the runner will start the Docker Postgres
database container, upgrade the DDL and start a Flask app. This allows for local debugging of an
"integrated" database and "deployed" HTTP Flask endpoint. The Flask app is in separate daemon thread
because otherwise it would begin and never return to the script as it is a foreground process.

The goal is to avoid writing this in a BASH script - because that existed previously and it was
horrible. This drops down into the shell when necessary but allows a nice high-level Python wrapper.
It calls Python from Python so make sure you have the below version in your path.

Requires:
 - python 3.7+

Pre-requisites:
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

runner = subprocess.run
app_dependencies = 'requirements.txt'
test_dependencies = 'tests/test-requirements.txt'
local = os.environ.get('LOCAL') and bool(util.strtobool(os.environ.get('LOCAL')))


@click.command()
@click.option('--env', '-e', required=True, type=click.Choice(['dev', 'test']))
def run(env):
    click.echo(f'Environment: {env}')
    _set_up_environment()
    _run_per_env(env)


def _set_up_environment():
    click.echo('Creating venv and installing app dependencies')
    commands = [
        ['-V'],
        ['-m', 'venv', 'venv'],
        ['-m', 'pip', 'install', '--upgrade', 'pip'],
        ['-m', 'pip', 'install', '-r', app_dependencies],
    ]
    for command in commands:
        python_executable = [sys.executable]
        python_executable.extend(command)
        runner(python_executable)


def _run_per_env(env):
    if env == 'dev':
        # Database must have DDL manually set by the developer using api_skeleton.db_ddl(). Unlike
        # tests below, it is not automatically run to allow control over data persistence.
        click.echo('Running Flask development server')
        _load_env_vars(env)
        _run_commands('run')
    elif env == 'test':
        click.echo('Running non-integrated then integrated test suites')
        click.echo('Installing test dependencies')
        runner([sys.executable, '-m', 'pip', 'install', '-r', test_dependencies])
        for env_file, integrated in {'test-internal': False, 'test-external': True}.items():
            message = 'integrated' if integrated else 'non-integrated'
            click.echo(f'Running {message} test suite')
            _load_env_vars(env_file)
            if local and integrated:
                _start_local_dependencies()
            _run_commands('test', options=['--integrated', str(integrated).lower()])

        for static_analyser in ['lint', 'cc', 'lloc']:
            _run_commands(static_analyser)


def _start_local_dependencies():
    database = {
        'db-container': ['--state', 'up'],
        'db-ddl': ['--action', 'upgrade'],
    }
    for command, options in database.items():
        _run_commands(command, options=options)

    from api_skeleton import app  # Cannot import at start of execution as env vars haven't loaded.
    # The Flask app must be run as a daemon thread because it runs in the foreground and will not
    # return control to this script if invoked in this process. As a daemon, it will exit when this
    # script's process ends.
    thread = Thread(target=app.run)
    thread.daemon = True
    thread.start()


def _run_commands(command, options=None):
    commands = [sys.executable, 'api_skeleton.py', command]
    if options:
        commands.extend(options)
    runner(commands)


def _load_env_vars(env_file):
    for var_file in ['common', env_file]:
        load_dotenv(dotenv_path=Path('configuration') / f'{var_file}.env', override=True)


if __name__ == '__main__':
    run()
