# Fillygons

Small, hinged polygons to assemble polyhedrons and play with.


## Setup

The repository needs a working OpenSCAD installation to work, see [OpenSCAD Template](https://github.com/Feuermurmel/openscad-template) for instructions.

Also, Python 3.4 or later is necessary.


## Compiling

Type `make -j 10 generated` to generate OpenSCAD source files for all variants. The files are placed in subdirectories of `src/variants`.

You can either open up the `.scad` files on OpenSCAD or compile them directly to STL files using e.g. `make src/variants/0.2mm/4-gon/normal.scad`.

To build all STL files, run `make stl`. But this will take a very long time.
