#!/usr/bin/env bash

set -e
set -x

mypy judge
flake8 judge tests
black judge tests --check
isort judge tests scripts --check-only