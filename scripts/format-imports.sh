#!/bin/sh -e
set -x

isort judge tests scripts 
sh ./scripts/format.sh