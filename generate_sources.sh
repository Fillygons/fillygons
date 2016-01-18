#! /usr/bin/env bash

set -e -o pipefail

if [ "$1" ]; then
	python3 generate_sources.py "$1" > "$1"
else
	python3 generate_sources.py
fi
