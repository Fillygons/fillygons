# Fillygons

Small, hinged polygons to assemble polyhedrons and play with. For more information, see the [fillygons](http://fillygons.feuermurmel.ch/) website.


## Setup

The repository needs a working [OpenScad](http://www.openscad.org/) installation to work, see [OpenSCAD Template](https://github.com/Feuermurmel/openscad-template) for instructions.

Also, Python 3.4 or later is necessary.


## Compiling

Type `make -j 10 generated` to generate OpenSCAD source files for all variants. The files are placed in subdirectories of `src/variants`.

You can either open up the `.scad` files on OpenSCAD or compile them directly to _STL_ files using e.g. `make src/variants/0.2mm/4-gon/normal.scad`.

To build all _STL_ files, run `make stl`. But this will take a very long time, up to several hours.
Therefore [this repository](https://github.com/Fillygons/fillygons-stl) contains precompiled _STL_ files.
