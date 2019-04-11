# Fillygons

Small, hinged polygons to assemble polyhedrons and play with. For more information, see the [fillygons](https://fillygons.ch/) website.


## Setup

The repository needs a working [OpenScad](http://www.openscad.org/) installation to work, see [OpenSCAD Template](https://github.com/Feuermurmel/openscad-template) for instructions. Also, Python 3.4 or later is necessary.

To run, the Python project in the repository needs to be installed into a virtualenv and the virtualenv needs to be activated the Makefile needs an activated Python virtualenv with the Python project in the repository installed:

    $ python3 -m venv venv
    $ . venv/bin/activate
    (venv) $ pip install -e .
    Obtaining file:///[...]/fillygons
    Requirement already satisfied: sympy in ./venv/lib/python3.5/site-packages (from fillygons==0.0.0)
    Requirement already satisfied: mpmath>=0.19 in ./venv/lib/python3.5/site-packages (from sympy->fillygons==0.0.0)
    Installing collected packages: fillygons
      Found existing installation: fillygons 0.0.0
        Uninstalling fillygons-0.0.0:
          Successfully uninstalled fillygons-0.0.0
      Running setup.py develop for fillygons
    Successfully installed fillygons


## Compiling

Type `make -j 10 generated` to generate OpenSCAD source files for all variants. The files are placed in subdirectories of `src/variants`.

You can either open up the `.scad` files on OpenSCAD or compile them directly to _STL_ files using e.g. `make src/variants/0.2mm/4-gon/normal.scad`.

To build all _STL_ files, run `make stl`. But this will take a very long time, up to several hours.
Therefore [this repository](https://github.com/Fillygons/fillygons-stl) contains precompiled _STL_ files:

    (venv) $ make
    [generate_sources] 433 files
    [openscad] src/variants/0.2mm/3-gon/filled.stl
    [...]


## Unit tests

Some unit tests are included in the form images being rendered from of specifically generated test STL files. The rendered images are compared with expected images. Run `make test` to compare the rendered to the expected images and report any differences



## Contributing

To add new fillygon models, edit the file `fillygons/generate_sources/variants.py`.
