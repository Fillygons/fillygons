#! /usr/bin/env bash

set -e -o pipefail

current_file_name=$1

# This function should be called for each generated file with the file's name as the first argument and the command to call to produce the file's content as the remaining arguments.
function generate_file() {
	file_name=$1
	shift
	generate_command=("$@")
	
	if ! [ "$current_file_name" ]; then
		echo "$file_name"
	elif [ "$current_file_name" == "$file_name" ]; then
		mkdir -p "$(dirname "$file_name")"
		"${generate_command[@]}" > "$file_name"
	fi
}

n-gon() {
	echo 'use <_fillygon.scad>'
	echo "render() regular_fillygon($1);"
}

for i in {3..12}; do
	generate_file "src/$i-gon.scad" n-gon "$i"
done

n-gon-large() {
	echo 'use <_fillygon.scad>'
	echo "render() regular_fillygon_large($1, $2);"
}

for i in {3..6}; do
	generate_file "src/$i-gon-double.scad" n-gon-large "$i" 2
done
