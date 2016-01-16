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

code() {
	echo 'use <_fillygon.scad>'
	
	if [ "$1" ]; then
		echo "include <$1>"
	fi
	
	echo "render() $2;"

}

# Arguments: file-name, included-file, called-function, arguments
fillygon() {
	for i in 0.25 0.4; do
		generate_file "src/$1-${i}mm.scad" code "$2" "$3($4, gap = $i)"
		generate_file "src/$1-filled-${i}mm.scad" code "$2" "$3($4, filled = true, gap = $i)"
	done
}

# Arguments: file-name, sides, side-repetitions, reversed-sides
regular_fillygon() {
	fillygon "$1" '' 'regular_fillygon' "$2, side_repetitions = $3, reversed_sides = [$4]"
}

# Arguments: file-name, included-file, reversed-sides
non_regular_fillygon() {
	fillygon "$1" "$2" 'fillygon' "angles, reversed_sides = [$3]"
}

# Regular n-gons.
for i in {3..12}; do
	regular_fillygon "$i-gon" $i 1
done

# n-gons with reversed sides.
regular_fillygon "3-gon-reversed" 3 1 true
regular_fillygon "4-gon-reversed-1" 4 1 true
regular_fillygon "4-gon-reversed-2" 4 1 true,true
regular_fillygon "4-gon-reversed-3" 4 1 true,false,true

# n-gons with doubled sides.
for i in {3..6}; do
	regular_fillygon "$i-gon-double" $i 2
done

# n-gons with custom angles.
for i in $(ls src/custom_angles | sed -rn 's,^_(.*)\.scad$,\1,p'); do
	non_regular_fillygon "$i" "custom_angles/_$i.scad"
done
