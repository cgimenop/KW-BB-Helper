#!/bin/bash
source venv/bin/activate
coverage run -m unittest test_scripts.py
coverage report
coverage html