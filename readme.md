# OpenSCAD Template

## Repository structure

This repository, as it is maintained on [GitHub](http://github.com/Feuermurmel/openscad-template), contains two important branches, `master` and `examples`. `master` contains an empty project which is ready to be cloned and used for new project.

Branch `examples` additionally contains a few example source files which are ready to be compiled. The root directory on that branch also contains a second text document `examples.creole`, describing the example project in more detail.


## Prerequisites

- OpenSCAD snapshot > 2014.11.05
	- Used to compile OpenSCAD source files to STL.
	- A recent development snapshot is recommended, e.g. version 2014.11.05 or later.
		- The current release version (2014.03) generates invalid dependency information if the path to the project contains spaces or other characters that need to be treated specially in a makefile and also has trouble with 2D shapes containing holes. The current development version solves these problems.

- Inkscape > 0.91
	- Used to export DXF files to SVG.
	- Recommended to edit SVG files, especially if importing of separate layers in OpenSCAD is needed.
	- At least version 0.91 (or maybe some earlier development snapshot) is necessary because the command line verbs used to transform and massage an SVG prior to export have only recently been added.

- Python 2.7
	- Used for to run the plugin that exports DXF to SVG and to run scripts that wrap the OpenSCAD command line tool and work around problems with generation of dependency information in OpenSCAD.
	- Should already be installed as a dependency to Inkscape. The most recent version of Python 2.7 is recommended.

- Asymptote [0]
	- Used to compile Asymptote files to PDF.
	- Recommended when creating Vector cutting projects for Epilog laser cutters.

[0]: This project was tested with Asymptote Version 2.35. Earlier Versions will probably also work.


### Explicitly specifying paths to binaries

If any of the required binaries is not available on `$PATH` or a different version should be used, the paths to these binaries can be configured by creating a file called `config.mk` in the same directory as the makefile. There, variables can be set to the absolute or relative paths to these binaries. For example:

	# Path to the OpenSCAD binary
	OPENSCAD := /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD
	
	# Path to the Inkscape binary
	INKSCAPE := /opt/local/bin/inkscape
	
	# Path to the Python 2.7 binary
	PYTHON := /opt/local/bin/python2.7
	
	# Path to the Asymptote binary
	ASYMPTOTE := /opt/local/bin/asy


## Supported file types

### Using SVG files from OpenSCAD

Any file whose name ends in `.svg` may be used from an OpenSCAD file like this:

	import("file.dxf");

The makefile will automatically convert the SVG file to a DXF file when building the project. If Inkscape is used to edit the SVG file, multiple layers can be created which can then be imported individually:

	import("file.dxf", "background");

The DXF export supports all shapes supported by Inkscape (e.g. rectangles, circles, paths, spiro lines, text, …). Before the objects are exported, all objects are converted to paths and combined using the union operation. For objects which have a stroke style, the stroke instead of the filled area is converted to a path. Then, the resulting path is converted to a set of line segments which closely follow the curved parts of the path. The resulting line segments are exported to DXF and combined to the original shapes when imported in OpenSCAD. For these transformations to work, the objects need to be placed in Inkscape layers.

OpenSCAD itself does not define which unit is used to measure lengths [1]. Inkscape OTOH allows the user to define a document wide unit as well as using different units when specifying the size and position of shapes. When exporting the SVG document using Inkscape, all numbers are converted to the unit specified under _General_ in Inkscape's _Document Properties_ dialog. These numbers are the written to the DXF document and used OpenSCAD directly.

DXF and OpenSCAD both use a right-handed coordinate system (the Y axis runs up while the X-axis runs to the right). While SVG uses a left-handed coordinate system (the Y axis runs down instead). But Inkscape, surprisingly, also uses a right-handed coordinate system. The DXF export script honors this and places the origin of the document in the lower left corner when exporting the document.

[1]: Although millimeters seems to be the predominant unit.


### Using SVG files from Asymptote

SVG files may instead be used from Asymptote files. To do this, the makefile must be instructed to convert an SVG to Asymptote paths and write them to a `.asy` file instead of a DXF file. This can be done by setting the variable ASYMPTOTE_EXPORTED_SVG_FILES in a file called `settings.mk` in the same directory as the makefile. The variable should be set to the names of the SVG files that should be converted to Asymptote files in instead of DXF files:

	ASYMPTOTE_EXPORTED_SVG_FILES := src/example.svg

If you want to have all SVG files converted to Asymptote, you can use this shortcut instead:

	ASYMPTOTE_EXPORTED_SVG_FILES := $(info $(shell find src -name '*.svg'))

For each specified SVG file, an Asymptote file of the same name is generated. These files can be imported as modules from other Asymptote files. These modules will contain a member of type `path[]` for each layer in the original SVG file:

	import test;
	
	draw(test.Layer_1, red + 0.001mm);

The module also contains a member `all`, which just contains all paths in one array.


### OpenSCAD files

Files whose names end in `.scad` are compiled to STL files using OpenSCAD. OpenSCAD files whose name start with `_` are treated as "library" files which will not be compiled to STL files. These files can still be used from other OpenSCAD files using one of the following commands:

	include <filename>
	use <filename>

Please see the [OpenSCAD User Manual](http://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Print_version) for details this and other OpenSCAD functionality.


## Generating Source files

This template includes support for automatically generated source files. This works by editing the `generate_sources.sh` script.

The script defines a function `generate_file()`, which should be called in the remainder of the script once for each file to generate. The first argument to the function is be the name of the file. The remaining arguments are treated as a command, which, when run, should output the file's content to standard output. For example:

	generate_file "src/cube.scad" echo "cube(25);"

How the function `generate_file()` is called is up to the script and may e.g. be done from a `for` loop or while iterating over a set of other source files.


## Compiling

To compile the whole project, run `make` from the directory in which this readme is. This will generate all sources files, if any, process all SVG files and produce an STL file for each OpenSCAD source file whose name does not start with `_`. Individual files may be created or updated by passing their names to the make command, as usual.


### Makefile targets

These are the special makefile targets which can be used in addition to the names of individual files to update:

- `all`: Builds all files that can be built from any source files. This is the default target when running `make` without arguments.
- `clean`: Removes all built files [2].
- `generated`: Generates all files generated by `generate_sources.sh`.
- `dxf`: Exports all SVG files to DXF files.
- `stl`: Compiles all OpenSCAD files to STL files.
- `asy`: Exports all configured SVG files to Asymptote files.
- `pdf`: Compiles all Asymptote files to PDF files.

[2]: This will not remove files for which the source file was removed. There is no simple way to detect whether a file was previously built from a source file or if it placed in the `src` directory manually.


### Settings used for compilation

The quality of the DXF export can be specified by creating a file called `settings.mk` in the same directory as the makefile. Setting `DXF_FLATNESS` to a smaller value (which defaults to `0.1`) creates a shape that more closely follows curved parts of the exported shapes. For example:

	# Specify how far the exported approximation may deviate from the actual shape. The default is 0.1.
	DXF_FLATNESS := 0.02
	
	# Specify which SVG files should be exported to Asymptote files instead of DXF files. By default, this list is empty.
	ASYMPTOTE_EXPORTED_SVG_FILES := src/example.svg


### Dependency tracking

OpenSCAD has the ability to write dependency files which record all files used while producing an STL file. These dependency files can be read by `make`. This ability is used to only recompile necessary files when running make.

This same mechanism is currently not used for converting SVG files referring to other files or for the script used to generate source files. Therefore, if other file used in the process are changed, the corresponding source files tracked by the makefile (the main SVG files or the files `generate_sources.sh` in case of generated sources) needs to be manually marked as changes by calling `touch` on the file before calling `make`.

For Asymptote files, a safer approach is currently taken. If any of the Asymptote source files in the `src` directory are changed, all Asymptote source files are recompiled.
