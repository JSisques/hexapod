.DEFAULT_GOAL := help
.PHONY: help stl render firmware software docs clean doctor gate-test preflight
.DELETE_ON_ERROR:
.SUFFIXES:

# Pinned CI/canonical image: dated tag plus multi-arch index digest (see docs/adr/0002-openscad-toolchain.md).
OPENSCAD_IMAGE ?= openscad/openscad:dev.2026-01-19@sha256:0af06bc2aa7a45d18b01a23cfb9dae6dddcd9542611e7be50edea6beb3b52fa7
TOOLCHAIN ?= auto
BACKEND ?= manifold
IMGSIZE ?= 1024,768

# Local binary: PATH first, then the macOS app bundle. Skipped when OPENSCAD is already set.
ifeq ($(origin OPENSCAD),undefined)
OPENSCAD := $(or $(shell command -v openscad 2>/dev/null),$(wildcard /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD))
endif

ifeq ($(TOOLCHAIN),auto)
ifneq ($(strip $(OPENSCAD)),)
TC := local
else
TC := docker
endif
else
TC := $(TOOLCHAIN)
endif
ifeq ($(filter $(TC),local docker),)
$(error TOOLCHAIN must be one of: auto, local, docker (got '$(TOOLCHAIN)'))
endif

export OPENSCADPATH := $(CURDIR)/libs

ifeq ($(TC),docker)
OPENSCAD_CMD = docker run --rm -u $$(id -u):$$(id -g) -e HOME=/tmp -e OPENSCADPATH=$(CURDIR)/libs -v "$(CURDIR):$(CURDIR)" -w "$(CURDIR)" --entrypoint openscad $(OPENSCAD_IMAGE)
HAS_BACKEND = yes
HAS_EXPORT_FORMAT = yes
else
OPENSCAD_CMD = "$(OPENSCAD)"
HAS_BACKEND = $(shell "$(OPENSCAD)" --help 2>&1 | grep -q -- --backend && echo yes)
HAS_EXPORT_FORMAT = $(shell "$(OPENSCAD)" --help 2>&1 | grep -q -- --export-format && echo yes)
endif
BACKEND_FLAG = $(if $(HAS_BACKEND),--backend=$(BACKEND))
# ASCII STL so the awk gates can read vertices; binaries without the flag already write ASCII.
STL_FMT = $(if $(HAS_EXPORT_FORMAT),--export-format asciistl)

PARAMS := hardware/cad/common/params.scad
# Value of a one-line "name = value;" in params.scad; list brackets and commas become spaces.
param = $(strip $(shell LC_ALL=C awk '$$1 == "$(1)" && $$2 == "=" { sub(/^[^=]*=/, ""); sub(/;.*/, ""); gsub(/[][,]/, " "); print; exit }' $(PARAMS)))
ifeq ($(origin BED_MAX),undefined)
BED_MAX := $(call param,bed_max)
endif

SRCS := $(wildcard hardware/cad/*/main.scad)
PARTS := $(patsubst hardware/cad/%/main.scad,%,$(SRCS))
STL_PARTS := $(filter-out asm-%,$(PARTS))
STLS := $(STL_PARTS:%=build/stl/%.stl)
PNGS := $(PARTS:%=build/png/%.png)

NOT_IMPLEMENTED = @echo "make $@: not implemented yet (see docs/adr/0001-repository-layout-and-licensing.md)" >&2; exit 1

# Run OpenSCAD with the warnings gate. $(1) output, $(2) input, $(3) extra flags, $(4) kind.
# The build fails on a non-zero exit or on any WARNING/ERROR in stderr, and the output is removed.
scad = mkdir -p $(@D) build/dep/$(4) build/log/$(4); log=build/log/$(4)/$*.log; \
  $(OPENSCAD_CMD) --hardwarnings $(BACKEND_FLAG) $(3) -o $(1) -d build/dep/$(4)/$*.d $(2) 2>"$$log"; st=$$?; \
  cat "$$log" >&2; \
  if [ $$st -ne 0 ] || grep -Eq 'WARNING|ERROR' "$$log"; then rm -f $(1); echo "error: OpenSCAD warnings/errors in $(2)" >&2; exit 1; fi

# Mesh bed check: $(1) ASCII STL, $(2) name. The STL is removed on failure.
bed_check  = LC_ALL=C awk -v max='$(BED_MAX)' -v name='$(2)' -f tools/cad/stl-bbox.awk $(1) || { rm -f $(1); exit 1; }
stl_export = $(call scad,$(1),$(2),$(STL_FMT),$(3)); $(call bed_check,$(1),$*)

# Build $(1) and pass only if it fails with output matching the ERE $(2); $(3) is the label.
expect_fail = rm -f $(1); out=$$($(MAKE) --no-print-directory $(1) 2>&1); st=$$?; \
  if [ $$st -ne 0 ] && printf '%s\n' "$$out" | grep -Eq '$(2)'; then echo "gate-test: $(3) OK"; \
  else printf '%s\n' "$$out" >&2; echo "gate-test: FAILED ($(3) gate did not fire)" >&2; exit 1; fi

help: ## List available targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

stl: $(STLS) ## Export ASCII STL models to build/stl and check them against bed_max (asm-* parts are PNG-only)
render: $(PNGS) ## Render PNG previews to build/png

build/stl/%.stl: hardware/cad/%/main.scad tools/cad/stl-bbox.awk | preflight ; @$(call stl_export,$@,$<,stl)
build/png/%.png: hardware/cad/%/main.scad | preflight ; @$(call scad,$@,$<,--imgsize=$(IMGSIZE) --autocenter --viewall --render,png)
build/gate/%.stl: tools/cad/fixtures/%.scad tools/cad/stl-bbox.awk | preflight ; @$(call stl_export,$@,$<,gate)

# Deleted includes listed in stale .d files must not break the build.
%.scad: ;

preflight:
	@if [ ! -f libs/BOSL2/std.scad ]; then echo "error: libs/BOSL2 is missing; run: git submodule update --init libs/BOSL2" >&2; exit 1; fi
ifeq ($(TC),docker)
	@command -v docker >/dev/null 2>&1 || { echo "error: docker not found; install Docker (https://docs.docker.com/get-docker/) or install OpenSCAD and use TOOLCHAIN=local" >&2; exit 1; }
else
	@if [ -z "$(strip $(OPENSCAD))" ]; then echo "error: openscad not found; install OpenSCAD or use TOOLCHAIN=docker" >&2; exit 1; fi
	@if [ -z "$(HAS_BACKEND)" ]; then echo "warning: local OpenSCAD lacks --backend (Manifold): $$($(OPENSCAD_CMD) --version 2>&1)" >&2; echo "warning: CI image is canonical; use TOOLCHAIN=docker for parity" >&2; fi
endif

clean: ## Remove build outputs
	rm -rf build

doctor: ## Show the resolved toolchain, versions and submodule state
	@echo "toolchain:  $(TC) (TOOLCHAIN=$(TOOLCHAIN))"
ifeq ($(TC),docker)
	@echo "image:      $(OPENSCAD_IMAGE)"
	@echo "version:    $$($(OPENSCAD_CMD) --version 2>&1 | tail -1)"
else
	@echo "binary:     $(OPENSCAD)"
	@echo "version:    $$($(OPENSCAD_CMD) --version 2>&1 | tail -1)"
endif
	@echo "backend:    $(if $(HAS_BACKEND),$(BACKEND) (supported),not supported)"
	@echo "stl format: $(if $(HAS_EXPORT_FORMAT),asciistl,default)"
	@echo "bed_max:    $(BED_MAX) mm"
	@echo "BOSL2:      $$(git submodule status libs/BOSL2 2>&1)"
	@if command -v docker >/dev/null 2>&1; then echo "docker:     available"; else echo "docker:     not found"; fi

gate-test: ## Prove the warnings, torque and bed gates fail on their fixtures
	@$(call expect_fail,build/gate/warning.stl,WARNING,warnings)
	@$(call expect_fail,build/gate/torque-infeasible.stl,torque budget exceeded,torque)
	@$(call expect_fail,build/gate/bed-oversize.stl,exceeds bed_max,bed)

firmware: ## Build firmware (placeholder)
	$(NOT_IMPLEMENTED)
software: ## Build software (placeholder)
	$(NOT_IMPLEMENTED)
docs: ## Build documentation (placeholder)
	$(NOT_IMPLEMENTED)

-include $(wildcard build/dep/*/*.d)
