#!/usr/bin/env bash

# Argument check
environment=$1
env_file=$1

if [[ "${environment}" == "" ]]
then
  echo "No environment passed: use 'dev' or 'test'"
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

# Environment specific
if [[ "${environment}" == "test" ]]
then
  pip install -r tests/test-requirements.txt
  echo "Testing"
fi

# Load environment var
echo "Loading environment vars"
if [[ "${environment}" == "test" ]]
then
  env_file="test-internal"
fi
set -a
. "configuration/${env_file}.conf"
set +a

# Damn the torpedoes!
echo "Go time!"
command="run"

if [[ "${environment}" == "dev" ]]
then
  python api_skeleton.py "${command}"
elif [[ "${environment}" == "test" ]]
then
  python api_skeleton.py test --integrated false
fi

exit 0
