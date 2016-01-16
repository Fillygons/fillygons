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
	echo "render() $1;"
}

generate_regular_fillygon() {
	generate_file "src/$1.scad" fillygon "regular_fillygon($2, side_repetitions = $3, reversed_sides = [$4])"
	generate_file "src/$1-filled.scad" fillygon "regular_fillygon($2, side_repetitions = $3, reversed_sides = [$4], filled = true)"
}

for i in {3..12}; do
	generate_regular_fillygon "$i-gon" $i 1
done

generate_regular_fillygon "3-gon-reversed" $i 1 true
generate_regular_fillygon "4-gon-reversed-1" $i 1 true
generate_regular_fillygon "4-gon-reversed-2" $i 1 true,true
generate_regular_fillygon "4-gon-reversed-3" $i 1 true,false,true

for i in {3..6}; do
	generate_regular_fillygon "$i-gon-double" $i 2
done
