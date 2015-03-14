# Installation-dependent settings. You can overwrite these in a file called config.mk in the same directory as this makefile. See readme.creole.
INKSCAPE := inkscape
OPENSCAD := openscad
PYTHON := python2

# Settings affecting the compiled results. You can overwrite these in a file called settings.mk in the same directory as this makefile. See readme.creole.
DXF_FLATNESS := 0.1
FLAT_SCAD_FILES :=

# Include the configuration files.
-include config.mk settings.mk

# Export variables used by the Python scripts.
export INKSCAPE OPENSCAD DXF_FLATNESS

# Command to run the Python scripts.
PYTHON_CMD := PYTHONPATH="support:$$PYTHONPATH" $(PYTHON)

# Run generate_scad.sh to get the names of all OpenSCAD files that should be generated using that same script.
GENERATED_FILES := $(addsuffix .scad,$(basename $(shell ./generate_sources.sh)))
GENERATED_SVG_FILES := $(filter %.svg, $(GENERATED_FILES))
GENERATED_SCAD_FILES := $(filter %.scad, $(GENERATED_FILES))

# All visible files in the src directory. Ignore files whose names contain spaces. Also ignore generated files.
SRC_FILES := $(filter-out $(GENERATED_FILES),$(shell find src -not \( \( -name '.*' -or -name '* *' \) -prune \)))
SRC_SCAD_FILES := $(filter %.scad,$(SRC_FILES))
SRC_SVG_FILES := $(filter %.svg,$(SRC_FILES))

# Source SVG files.
SVG_FILES := $(SRC_SVG_FILES) $(GENERATED_SVG_FILES)

# Only OpenSCAD files whose names do not start with `_' are compiled to STL.
COMPILED_SCAD_FILES := $(foreach i, $(SRC_SCAD_FILES) $(GENERATED_SCAD_FILES),$(if $(filter-out _%,$(notdir $(i))),$(i)))

# Makefiles which are generated while compiling to record dependencies.
DEPENDENCY_FILES := $(patsubst %.scad,%.d,$(COMPILED_SCAD_FILES))

# STL files produced from OpenSCAD files.
SCAD_STL_FILES := $(patsubst %.scad,%.stl,$(filter-out $(FLAT_SCAD_FILES),$(COMPILED_SCAD_FILES)))

# DXF files produced from OpenSCAD fiels. Ignore non-OpenSCAD files in FLAT_SCAD_FILES.
SCAD_DXF_FILES := $(patsubst %.scad,%.dxf,$(filter $(FLAT_SCAD_FILES),$(COMPILED_SCAD_FILES)))

# DXF files produced from SVG files. Ignore an SVG file if the same DXF file can also be produced from an OpenSCAD file. This is just to get reproducable builds without aborting it.
SVG_DXF_FILES := $(filter-out $(SCAD_DXF_FILES),$(patsubst %.svg,%.dxf,$(SVG_FILES)))

# Files that may be used from OpenSCAD files and thus must exist before OpenSCAD is called.
SCAD_ORDER_DEPS := $(SVG_DXF_FILES) $(GENERATED_FILES)

# Dependencies which may affect the result of all build products.
GLOBAL_DEPS := Makefile $(wildcard config.mk settings.mk)

# Make the next goal (`all`) the default goal.
.DEFAULT_GOAL :=

# Non-file goals.
.PHONY: all clean generated dxf stl

# Goal to build Everything. Also generates files which aren't compiled to anything else.
all: generated dxf stl

# Everything^-1.
clean:
	rm -rf $(GENERATED_FILES) $(SVG_DXF_FILES) $(SCAD_DXF_FILES) $(SCAD_STL_FILES) $(DEPENDENCY_FILES)

# Goals to build the project up to a specific step.
generated: $(GENERATED_FILES)
dxf: $(SVG_DXF_FILES) $(SCAD_DXF_FILES)
stl: $(SCAD_STL_FILES)

# Rule to convert an SVG file to a DXF file.
$(SVG_DXF_FILES): %.dxf: %.svg $(GLOBAL_DEPS)
	$(PYTHON_CMD) -m dxf_export $< $@

# Rule to compile an OpenSCAD file to a DXF file.
$(SCAD_DXF_FILES): %.dxf: %.scad $(GLOBAL_DEPS) | $(SCAD_ORDER_DEPS)
	$(PYTHON_CMD) -m openscad $< $@ $*.d

# Rule to compile an OpenSCAD file to an STL file.
$(SCAD_STL_FILES): %.stl: %.scad $(GLOBAL_DEPS) | $(SCAD_ORDER_DEPS)
	$(PYTHON_CMD) -m openscad $< $@ $*.d

# Rule for automaticaly generated OpenSCAD files.
$(GENERATED_FILES): generate_sources.sh $(GLOBAL_DEPS)
	./generate_sources.sh $@

# Include dependency files produced by an earlier build.
-include $(DEPENDENCY_FILES)
