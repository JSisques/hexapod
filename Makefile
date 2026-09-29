.DEFAULT_GOAL := help
.PHONY: help stl render firmware software docs clean

NOT_IMPLEMENTED = @echo "make $@: not implemented yet (see docs/adr/0001-repository-layout-and-licensing.md)" >&2; exit 1

help: ## List available targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-10s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

stl: ## Export STL models to build/ (placeholder)
	$(NOT_IMPLEMENTED)
render: ## Render PNG previews to build/ (placeholder)
	$(NOT_IMPLEMENTED)
firmware: ## Build firmware (placeholder)
	$(NOT_IMPLEMENTED)
software: ## Build software (placeholder)
	$(NOT_IMPLEMENTED)
docs: ## Build documentation (placeholder)
	$(NOT_IMPLEMENTED)
clean: ## Remove build outputs (placeholder)
	$(NOT_IMPLEMENTED)
