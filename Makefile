INKSCAPE ?= inkscape
OPENSCAD ?= openscad

# Used by dxf_export/main.sh
export INKSCAPE

# Run generate_scad.sh to get the names of all OpenSCAD files that should be generated using that same script.
GENERATED_FILES := $(addsuffix .scad,$(basename $(shell ./generate_sources.sh)))
GENERATED_SVG_FILES := $(filter %.svg, $(GENERATED_FILES))
GENERATED_SCAD_FILES := $(filter %.scad, $(GENERATED_FILES))

# Source SVG files.
SVG_FILES := $(shell find src -name '*.svg') $(GENERATED_SVG_FILES)

# Only OpenSCAD files whose names do not start with `_' are compiled to STL.
SCAD_FILES := $(shell find src -name '*.scad') $(GENERATED_SCAD_FILES)
LIBRARY_SCAD_FILES := $(foreach i,$(SCAD_FILES),$(if $(filter _%,$(notdir $(i))),$(i)))  
COMPILED_SCAD_FILES := $(filter-out $(LIBRARY_SCAD_FILES),$(SCAD_FILES))

# All files that may be generated from the source files.
STL_FILES := $(patsubst %.scad,%.stl,$(COMPILED_SCAD_FILES))
DXF_FILES := $(patsubst %.svg,%.dxf,$(SVG_FILES))

# Everything.
all: $(STL_FILES)

# Everything^-1.
clean:
	rm -rf $(DXF_FILES) $(STL_FILES) $(GENERATED_SCAD_FILES)

# Needs to be included after target all has been defined.
-include config.mk

# Assume that any compiled OpenSCAD file may depend on any non-compiled OpenSCAD file in the same directory.
$(foreach i,$(COMPILED_SCAD_FILES),$(eval $(i): $(filter $(dir $(i))%,$(LIBRARY_SCAD_FILES) $(DXF_FILES))))

# Rule to convert an SVG file to a DXF file.
%.dxf: %.svg
	dxf_export/main.sh $< $@

# Rule to compile an OpenSCAD file to an STL file.
%.stl: %.scad
	$(OPENSCAD) -o $@ $<

# Rule for automaticlaly generated OpenSCAD files.
$(GENERATED_FILES): generate_sources.sh
	./generate_sources.sh $@
