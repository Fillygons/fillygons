#! /usr/bin/env bash

set -e -o pipefail

if [ "$1" ]; then
	./generate_sources.py "$1" > "$1"
else
	./generate_sources.py
fi
