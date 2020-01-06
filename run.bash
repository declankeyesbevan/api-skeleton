#!/usr/bin/env bash

# Argument check
environment=$1
if [[ "${environment}" == "" ]]
then
  echo "No environment passed: use 'dev', 'test' or 'prod'"
  exit 42
fi

echo "Environment ${environment} passed"

# Common
echo "Installing dependencies"
rm -rf venv
python3 -m venv venv
. venv/bin/activate
python -V
pip install --upgrade pip
pip install -r requirements.txt

# Load environment vars
echo "Loading environment vars"
set -a
. "configuration/${environment}.conf"
set +a

# Environment specific
command="run"
if [[ "${environment}" == "test" ]]
then
  pip install -r tests/test-requirements.txt
  command="test"
  echo "Testing"
fi

# Damn the torpedoes!
echo "Go time!"
python manage.py ${command}

# TODO: change to CLI argument instead once Flask Script replaced with Click
# Run integration tests
if [[ "${environment}" == "test" ]]
then
  export INTEGRATION=true
  python manage.py test
  exit 0
fi

exit 0
