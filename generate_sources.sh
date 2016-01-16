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

fillygon() {
	echo 'use <_fillygon.scad>'
	echo "render() regular_fillygon($1, side_repetitions = $2, filled = $3);"
}

generate_fillygon() {
	generate_file "src/$1.scad" fillygon $2 $3 false
	generate_file "src/$1-filled.scad" fillygon $2 $3 true
}

for i in {3..12}; do
	generate_fillygon "$i-gon" $i 1
done

for i in {3..6}; do
	generate_fillygon "$i-gon-double" $i 2
done
