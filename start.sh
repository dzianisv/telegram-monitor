#!/bin/sh

set -eu

for cmd in brew apt dnf choco; do
    if command -v "$cmd" > /dev/null; then
        PACAKGE_MANAGER=$cmd
        break
    fi
done

_require() {
    if ! command -v "$@" > /dev/null; then
        "$PACAKGE_MANAGER" install -y "$@"
    fi
}

for package in python3 pipenv ffmpeg; do
    _require "$package"
done

pipenv run python3 ./monitor.py