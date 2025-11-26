#!/bin/bash
source venv/bin/activate
echo "Running Pylint..."
pylint update_classification.py generate_league.py --rcfile=.pylintrc
echo "Running Flake8..."
flake8 update_classification.py generate_league.py --max-line-length=120 --ignore=E501,W503,E203,W293,W292,E302,E305,F401,F841