#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --in-place judge tests scripts --exclude=__init__.py
black judge tests scripts
isort judge tests scripts