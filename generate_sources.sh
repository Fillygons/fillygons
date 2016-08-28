#! /usr/bin/env bash

set -e -o pipefail

if [ "$1" ]; then
	python3 -m generate_sources "$1" > "$1"
else
	python3 -m generate_sources
fi
