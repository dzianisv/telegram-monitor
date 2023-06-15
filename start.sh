#!/bin/sh

set -eu

if ! command -v ffprobe; then
    brew install ffmpeg
fi

if ! command -v pipenv; then
    python3 -m pip install pipenv
fi

python3 -m pipenv run python3 ./monitor.py