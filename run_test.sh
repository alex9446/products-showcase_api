#!/bin/sh

set -e
export DATABASE_URL=sqlite://

flake8 *.py src/*.py
coverage run --omit 'venv/*' test.py
echo '\n\nCoverage results:'
echo     '-----------------'
coverage report
