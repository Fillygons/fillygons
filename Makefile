# Used by dxf_export/main.sh
INKSCAPE ?= inkscape
OPENSCAD ?= openscad
PYTHON ?= python2

PYTHON_CMD := PYTHONPATH="support:$$PYTHONPATH" $(PYTHON)

export INKSCAPE OPENSCAD

# All visible files in the src directory. Ignore files whose names contain spaces.
SRC_FILES := $(shell find src -not \( \( -name '.*' -or -name '* *' \) -prune \))
SRC_SCAD_FILES := $(filter %.scad,$(SRC_FILES))
SRC_SVG_FILES := $(filter %.svg,$(SRC_FILES))

# Run generate_scad.sh to get the names of all OpenSCAD files that should be generated using that same script.
GENERATED_FILES := $(addsuffix .scad,$(basename $(shell ./generate_sources.sh)))
GENERATED_SVG_FILES := $(filter %.svg, $(GENERATED_FILES))
GENERATED_SCAD_FILES := $(filter %.scad, $(GENERATED_FILES))

# Source SVG files.
SVG_FILES := $(SRC_SVG_FILES) $(GENERATED_SVG_FILES)

# Only OpenSCAD files whose names do not start with `_' are compiled to STL.
COMPILED_SCAD_FILES := $(foreach i, $(SRC_SCAD_FILES) $(GENERATED_SCAD_FILES),$(if $(filter-out _%,$(notdir $(i))),$(i)))

# Makefiles which are generated while compiling to record dependencies.
DEPENDENCY_FILES := $(patsubst %.scad,%.d,$(COMPILED_SCAD_FILES))

# All files that may be generated from the source files.
STL_FILES := $(patsubst %.scad,%.stl,$(COMPILED_SCAD_FILES))
DXF_FILES := $(patsubst %.svg,%.dxf,$(SVG_FILES))

# Everything. Also generates files which aren't compiled to anything else.
all: $(GENERATED_FILES) $(DXF_FILES) $(STL_FILES)

# Everything^-1.
clean:
	rm -rf $(GENERATED_FILES) $(DXF_FILES) $(STL_FILES) $(DEPENDENCY_FILES)

# Include the local configuration file and the dependency files. Needs to be included after the `all' target has been defined.
-include config.mk $(DEPENDENCY_FILES)

# Rule to convert an SVG file to a DXF file.
%.dxf: %.svg
	$(PYTHON_CMD) -m dxf_export $< $@

# Rule to compile an OpenSCAD file to an STL file. We require all DXF files to exist before an OpenSCAD file can be used to generate an STL file. Additional dependencies are read from the included makefiles generated during compiling.
%.stl: %.scad  | $(DXF_FILES)
	$(PYTHON_CMD) -m openscad $< $@ $*.d

# Rule for automaticlaly generated OpenSCAD files.
$(GENERATED_FILES): generate_sources.sh
	./generate_sources.sh $@
