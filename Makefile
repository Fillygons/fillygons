# Installation-dependent settings. You can overwrite these in a file called config.mk in the same directory as this makefile. See readme.creole.
INKSCAPE := inkscape
OPENSCAD := openscad
PYTHON := python2
ASYMPTOTE := asy
CURA := cura

# Settings affecting the compiled results. You can overwrite these in a file called settings.mk in the same directory as this makefile. See readme.creole.
DXF_FLATNESS := 0.1
FLAT_SCAD_FILES :=

# Non-file goals.
.PHONY: all clean generated dxf stl asy pdf

# Remove targets whose command failed.
.DELETE_ON_ERROR:

# Do not print commands as they are executed. They do not show the actual invocation of the respective tools anyways but just the Pyton wrappers.
.SILENT:

# Set the default goal. Prevents it from being overwritten accidentially from config.mk or settings.mk.
.DEFAULT_GOAL := all

# Include the configuration files.
-include config.mk settings.mk

# Command to run the Python scripts.
PYTHON_CMD := PYTHONPATH="support" $(PYTHON)
INKSCAPE_CMD := INKSCAPE=$(INKSCAPE) DXF_FLATNESS=$(DXF_FLATNESS) $(PYTHON_CMD) -m inkscape  
OPENSCAD_CMD := OPENSCAD=$(OPENSCAD) $(PYTHON_CMD) -m openscad
ASYMPTOTE_CMD := ASYMPTOTE=$(ASYMPTOTE) $(PYTHON_CMD) -m asymptote
CURA_CMD := CURA=$(CURA) $(PYTHON_CMD) -m cura

# Function with arguments (ext, subst_ext, names).
# Takes a list of file names and returns all elements whose basename do not start with a `_' and which have extension ext. The returned names will have their extension replaced by subst_ext.
filter_compiled = $(foreach i,$(patsubst %$1,%$2,$(filter %$1,$3)),$(if $(filter-out _%,$(notdir $i)),$i))

# All considered source and target files currently existing.
EXISTING_FILES := $(shell find src -not \( \( -name '.*' -or -name '* *' \) -prune \) -type f)

# FIXME: Re-building the Makefile's prerequisites creates files which are also cleaned by the `clean` target.
# Run generate_scad.sh to get the names of all files that should be generated using that same script.
GENERATED_FILES := $(shell generate_sources --list-files)

# All visible files in the src directory that either exist or can be generated. Ignore files whose names contain spaces.
SRC_FILES := $(sort $(GENERATED_FILES) $(EXISTING_FILES))

# STL files produced from OpenSCAD files.
SCAD_STL_FILES := $(call filter_compiled,.scad,.stl,$(filter-out $(FLAT_SCAD_FILES),$(SRC_FILES)))

# DXF files produced from OpenSCAD fiels. Ignore non-OpenSCAD files in FLAT_SCAD_FILES.
SCAD_DXF_FILES := $(call filter_compiled,.scad,.dxf,$(filter $(FLAT_SCAD_FILES),$(SRC_FILES)))

# GCode files to be generated form compiled STL files.
STL_GCODE_FILES := $(call filter_compiled,.stl,.gcode,$(SCAD_STL_FILES))

# DXF files produced from SVG files. This excludes SVG files that are exported to Asymptote Files. Also, ignores an SVG file, if the same DXF file can also be produced from an OpenSCAD file. This is just to get reproducable builds without aborting it.
SVG_DXF_FILES := $(filter-out $(SCAD_DXF_FILES),$(call filter_compiled,.svg,.dxf,$(SRC_FILES)))

# Asymptote files produced from SVG files.
SVG_ASY_FILES := $(call filter_compiled,.svg,.asy,$(SRC_FILES))

# PDF files which can be generated from Asymptote files. We exclude SVG_ASY_FILES because they don't contain any drawing primitives and thus won't produce a PDF.
ASY_PDF_FILES := $(call filter_compiled,.asy,.pdf,$(filter-out $(SVG_ASY_FILES),$(SRC_FILES)))

# Makefiles which are generated while compiling to record dependencies.
DEPENDENCY_FILES := $(patsubst %,%.d,$(SCAD_STL_FILES) $(SCAD_DXF_FILES) $(ASY_PDF_FILES))

# Files that may be used from OpenSCAD files and thus must exist before OpenSCAD is called.
SCAD_ORDER_DEPS := $(filter %.scad %.dxf,$(SRC_FILES)) $(SVG_DXF_FILES)

# Files that may be used from Asymptote files.
ASY_DEPS := $(filter %.asy,$(SRC_FILES)) $(SVG_ASY_FILES)

# Dependencies which may affect the result of all build products.
GLOBAL_DEPS := Makefile $(wildcard config.mk settings.mk)

# All existing target files.
EXISTING_TARGETS := $(filter $(SVG_DXF_FILES) $(SCAD_DXF_FILES) $(SCAD_STL_FILES) $(SVG_ASY_FILES) $(ASY_PDF_FILES) $(STL_GCODE_FILES) $(GENERATED_FILES) $(DEPENDENCY_FILES),$(EXISTING_FILES))

# Goal to build Everything. Also generates files which aren't compiled to anything else. Deined here to make it the default goal.
all: generated $(SCAD_DXF_FILES) $(SCAD_STL_FILES) $(ASY_PDF_FILES) $(STL_GCODE_FILES)

# Everything^-1.
clean:
	echo [clean] $(EXISTING_TARGETS)
	rm -rf $(EXISTING_TARGETS)

# Goals to build the project up to a specific step.
generated: $(GENERATED_FILES)
dxf: $(SVG_DXF_FILES) $(SCAD_DXF_FILES)
stl: $(SCAD_STL_FILES)
asy: $(SVG_ASY_FILES)
pdf: $(ASY_PDF_FILES)
gcode: $(STL_GCODE_FILES)

# Rule to convert an SVG file to a DXF file.
$(SVG_DXF_FILES): %.dxf: %.svg $(GLOBAL_DEPS)
	echo [inkscape] $@
	$(INKSCAPE_CMD) $< $@

# Rule to export an SVG file to an Asymptote file.
$(SVG_ASY_FILES): %.asy: %.svg $(GLOBAL_DEPS)
	echo [inkscape] $@
	$(INKSCAPE_CMD) $< $@

# Rule to compile an OpenSCAD file to a DXF file.
$(SCAD_DXF_FILES): %.dxf: %.scad $(GLOBAL_DEPS) | $(SCAD_ORDER_DEPS)
	echo [openscad] $@
	$(OPENSCAD_CMD) $< $@

# Rule to compile an OpenSCAD file to an STL file.
$(SCAD_STL_FILES): %.stl: %.scad $(GLOBAL_DEPS) | $(SCAD_ORDER_DEPS)
	echo [openscad] $@
	$(OPENSCAD_CMD) $< $@

# Rule to generate GCode from an STL file.
$(STL_GCODE_FILES): %.gcode: %.stl stuff/profile.ini $(GLOBAL_DEPS)
	echo [cura] $@
	$(CURA_CMD) $< $@ stuff/profile.ini

# Rule to compile an Asymptote file to a PDF file.
$(ASY_PDF_FILES): %.pdf: %.asy $(GLOBAL_DEPS) | $(ASY_DEPS)
	echo [asymptote] $@
	$(ASYMPTOTE_CMD) $< $@

GENERATED_FILES_DEPS := $(shell find fillygons/generate_sources -name *.py)

# Mark the target which creates generated files as intermediate so that its non-existence doesn't result in it being called even if all generated files are up-to-date.
.INTERMEDIATE: __generate_sources__

# Target which is used to create all generated files and on which all generated files depen.
__generate_sources__: $(GLOBAL_DEPS) $(GENERATED_FILES_DEPS)
	echo [generate_sources]
	generate_sources

# Make all generated files depend on the target which actually creates them.
$(GENERATED_FILES): __generate_sources__

# Include dependency files produced by an earlier build.
-include $(DEPENDENCY_FILES)
