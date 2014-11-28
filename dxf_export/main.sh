#! /usr/bin/env bash

set -e -o pipefail

in_file=$1
out_file=$2

# If environment variable DXF_EXPORT_DEBUG is set, the temporary file that is modified using Inkscape is saved in the same directory as the source file and not removed.
if [ "$DXF_EXPORT_DEBUG" ]; then
	temp_file="$(dirname "$in_file")/$(basename "$in_file" '.svg')~temp.svg"
else
	temp_dir=$(mktemp -d)
	temp_file="$temp_dir/temp.svg"
fi

script_path=$(dirname "$BASH_SOURCE")

cp "$in_file" "$temp_file"

# Run a few commands using Inkscape on the SVG file to get in into a shape that makes a successful conversion to DXF more likely.
"$INKSCAPE" \
	--verb UnlockAllInAllLayers \
	--verb EditSelectAllInAllLayers \
	--verb ObjectToPath \
	--verb EditSelectAllInAllLayers \
	--verb SelectionUnGroup \
	--verb EditSelectAllInAllLayers \
	--verb StrokeToPath \
	--verb FileSave \
	--verb FileClose \
	"$temp_file"

# Convert the SVG to a DXF file.
python2 "$script_path/better_dxf_outlines.py" "$temp_file" > "$out_file"

if ! [ "$DXF_EXPORT_DEBUG" ]; then
	rm -rf "$temp_dir"
fi
