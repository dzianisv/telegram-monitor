#!/bin/sh

if ! command -v pipenv; then
    python3 -m pip install pipenv
fi

pipenv shell ./monitor.py