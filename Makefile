######################################################################
# Cloudmesh OpenAPI Makefile
######################################################################

# Variables
PYTHON       := python
PIP          := $(PYTHON) -m pip
PACKAGE_NAME := $(shell basename $(CURDIR))
COMMAND_NAME := cmc
TWINE        := $(PYTHON) -m twine
VERSION_FILE := VERSION
GIT          := git
PYENVVERSION := $(shell pyenv version-name)
OPEN         := open
BROWSER      := open -a "DuckDuckGo"

.PHONY: help install clean build test reinstall \
        check tag release test-html test-cov setup-test uninstall-all \
        tmp-setup view doc doc-real doc-publish pdoc serve watch

help:
	@echo
	@echo "Makefile for the OpenAPI Cloudmesh extension:"
	@echo
	@echo "  install       - Install in editable mode for local development"
	@echo "  reinstall     - Clean and reinstall locally"
	@echo "  clean         - Remove build artifacts, cache, and test debris"
	@echo "  build         - Build distributions (sdist and wheel)"
	@echo "  check         - Build and validate metadata/README"
	@echo "  test          - Run pytest suite with HTML report"
	@echo "  test-cov      - Run pytest with coverage report"
	@echo "  setup-test    - Install test deps"
	@echo "  tag           - Create a git tag based on current version and push"
	@echo "  release       - Full Production Cycle: upload + tag"
	@echo "  doc           - Generate documentation (pdoc + MkDocs)"
	@echo "  doc-real      - Generate documentation (pdoc + MkDocs)"
	@echo "  doc-publish   - Publish documentation to gh-pages"
	@echo "  pdoc          - Serve documentation locally"
	@echo "  view          - View the generated documentation"
	@echo

# --- DEVELOPMENT & TESTING ---

install:
	$(PIP) install -e .

requirements:
	pip-compile --output-file=requirements.txt pyproject.toml

test:
	$(PYTHON) -m pytest -v tests/
	for d in ../cloudmesh-ai-*; do echo "--- \$$d ---"; git -C \$$d status -s; done

test-html:
	$(PYTHON) -m pytest -v --html=.report.html tests/
	open .report.html

test-cov:
	pytest --cov=cloudmesh.ai.command.openapi --cov-report=term-missing tests/

setup-test:
	$(PIP) install pytest pytest-mock pytest-cov pytest-html

# --- BUILD AND VALIDATE ---

build: clean
	@echo "Building distributions..."
	$(PYTHON) -m build

check: build
	@echo "Validating distribution metadata..."
	$(TWINE) check dist/*

tmp-setup:
	cd /tmp && pyenv local $$(pyenv global)

tag:
	@VERSION=$$(cat $(VERSION_FILE)); \
	echo "Tagging version v$$VERSION..."; \
	$(GIT) tag -a v$$VERSION -m "Release v$$VERSION"; \
	$(GIT) push origin v$$VERSION

release: upload tag
	@echo "Production release and tagging complete."

# --- DOCUMENTATION ---

view: 
	$(OPEN) site/index.html

create: doc
	$(BROWSER) site/api.html

watch:
	@echo "Cleaning up port 8000..."
	-@lsof -ti:8000 | xargs kill -9
	@echo "Building site..."
	$(MAKE) doc
	@echo "Opening API reference page as file..."
	@$(BROWSER) "file://$(CURDIR)/site/api.html"
	@echo "Watching for changes (polling every 2s)..."
	@touch .last_css_check; \
	while true; do \
		if find docs -name "*.md" -o -name "*.css" -newer .last_css_check | grep -q .; then \
			echo "Change detected, rebuilding..."; \
			$(MAKE) doc; \
			sleep 1; \
			$(BROWSER) "file://$(CURDIR)/site/api.html?v=$(shell date +%s)"; \
		fi; \
		touch .last_css_check; \
		sleep 2; \
	done


doc:
	mkdocs build
	touch docs/.nojekyll

doc-real: doc


publish:
	@echo "Deploying MkDocs site to GitHub Pages..."
	mkdocs gh-deploy --clean
