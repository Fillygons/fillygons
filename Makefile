# Installation-dependent settings. You can overwrite these in a file called config.mk in the same directory as this makefile. See readme.creole.
INKSCAPE := inkscape
OPENSCAD := openscad
PYTHON := python2
ASYMPTOTE := asy

# Settings affecting the compiled results. You can overwrite these in a file called settings.mk in the same directory as this makefile. See readme.creole.
DXF_FLATNESS := 0.1
FLAT_SCAD_FILES :=
ASYMPTOTE_EXPORTED_SVG_FILES :=

# Non-file goals.
.PHONY: all clean generated dxf stl asy pdf

# Remove targets whose command failed.
.DELETE_ON_ERROR:

# Goal to build Everything. Also generates files which aren't compiled to anything else. Deined here to make it the default goal.
all: generated dxf stl asy pdf

# Include the configuration files.
-include config.mk settings.mk

# Command to run the Python scripts.
PYTHON_CMD := PYTHONPATH="support:$$PYTHONPATH" $(PYTHON)
INKSCAPE_CMD := INKSCAPE=$(INKSCAPE) DXF_FLATNESS=$(DXF_FLATNESS) $(PYTHON_CMD) -m inkscape  
OPENSCAD_CMD := OPENSCAD=$(OPENSCAD) $(PYTHON_CMD) -m openscad
ASYMPTOTE_CMD := ASYMPTOTE=$(ASYMPTOTE) $(PYTHON_CMD) -m asymptote

# Function with arguments (ext, subst_ext, names).
# Takes a list of file names and returns all elements whose basename do not start with a `_' and which have extension ext. The returned names will have their extension replaced by subst_ext.
filter_compiled = $(foreach i,$(patsubst %$1,%$2,$(filter %$1,$3)),$(if $(filter-out _%,$(notdir $i)),$i))

# Run generate_scad.sh to get the names of all files that should be generated using that same script.
GENERATED_FILES := $(shell ./generate_sources.sh)

# All visible files in the src directory that either exist or can be generated. Ignore files whose names contain spaces.
SRC_FILES := $(sort $(GENERATED_FILES) $(shell find src -not \( \( -name '.*' -or -name '* *' \) -prune \) -type f))

# STL files produced from OpenSCAD files.
SCAD_STL_FILES := $(call filter_compiled,.scad,.stl,$(filter-out $(FLAT_SCAD_FILES),$(SRC_FILES)))

# DXF files produced from OpenSCAD fiels. Ignore non-OpenSCAD files in FLAT_SCAD_FILES.
SCAD_DXF_FILES := $(call filter_compiled,.scad,.dxf,$(filter $(FLAT_SCAD_FILES),$(SRC_FILES)))

# DXF files produced from SVG files. This excludes SVG files that are exported to Asymptote Files. Also, ignores an SVG file, if the same DXF file can also be produced from an OpenSCAD file. This is just to get reproducable builds without aborting it.
SVG_DXF_FILES := $(filter-out $(SCAD_DXF_FILES),$(call filter_compiled,.svg,.dxf,$(filter-out $(ASYMPTOTE_EXPORTED_SVG_FILES),$(SRC_FILES))))

# Asymptote files produced from SVG files.
SVG_ASY_FILES := $(call filter_compiled,.svg,.asy,$(filter $(ASYMPTOTE_EXPORTED_SVG_FILES),$(SRC_FILES)))

# PDF files which can be generated from Asymptote files. We exclude SVG_ASY_FILES because they don't contain any drawing primitives and thus won't produce a PDF.
ASY_PDF_FILES := $(call filter_compiled,.asy,.pdf,$(filter-out $(SVG_ASY_FILES),$(SRC_FILES)))

# Makefiles which are generated while compiling to record dependencies.
DEPENDENCY_FILES := $(foreach i,.scad,$(call filter_compiled,$i,.d,$(filter-out $(SVG_ASY_FILES),$(SRC_FILES))))

# Files that may be used from OpenSCAD files and thus must exist before OpenSCAD is called.
SCAD_ORDER_DEPS := $(filter %.scad %.dxf,$(SRC_FILES)) $(SVG_DXF_FILES)

# Files that may be used from Asymptote files.
ASY_DEPS := $(filter %.asy,$(SRC_FILES)) $(SVG_ASY_FILES)

# Dependencies which may affect the result of all build products.
GLOBAL_DEPS := Makefile $(wildcard config.mk settings.mk)

# Everything^-1.
clean:
	rm -rf $(SVG_DXF_FILES) $(SCAD_DXF_FILES) $(SCAD_STL_FILES) $(SVG_ASY_FILES) $(ASY_PDF_FILES) $(GENERATED_FILES) $(DEPENDENCY_FILES)

# Goals to build the project up to a specific step.
generated: $(GENERATED_FILES)
dxf: $(SVG_DXF_FILES) $(SCAD_DXF_FILES)
stl: $(SCAD_STL_FILES)
pdf: $(ASY_PDF_FILES)
asy: $(SVG_ASY_FILES)

# Rule to convert an SVG file to a DXF file.
$(SVG_DXF_FILES): %.dxf: %.svg $(GLOBAL_DEPS)
	$(INKSCAPE_CMD) $< $@

$(SVG_ASY_FILES): %.asy: %.svg $(GLOBAL_DEPS)
	$(INKSCAPE_CMD) $< $@

# Rule to compile an OpenSCAD file to a DXF file.
$(SCAD_DXF_FILES): %.dxf: %.scad $(GLOBAL_DEPS) | $(SCAD_ORDER_DEPS)
	$(OPENSCAD_CMD) $< $@ $*.d

# Rule to compile an OpenSCAD file to an STL file.
$(SCAD_STL_FILES): %.stl: %.scad $(GLOBAL_DEPS) | $(SCAD_ORDER_DEPS)
	$(OPENSCAD_CMD) $< $@ $*.d

# Rule to export an SVG file to an Asymptote file.
$(ASY_PDF_FILES): %.pdf: $(ASY_DEPS) $(GLOBAL_DEPS)
	$(ASYMPTOTE_CMD) $*.asy $@

# Rule for automaticaly generated OpenSCAD files.
$(GENERATED_FILES): generate_sources.sh $(GLOBAL_DEPS)
	./generate_sources.sh $@

# Include dependency files produced by an earlier build.
-include $(DEPENDENCY_FILES)
