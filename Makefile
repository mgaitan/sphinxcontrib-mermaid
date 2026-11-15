#########
# BUILD #
#########
.PHONY: develop-py develop-js develop
develop-py:
	uv pip install -e .[develop]

develop-js: requirements-js

develop: develop-js develop-py  ## setup project for development

.PHONY: requirements-py requirements-js requirements
requirements-py:  ## install prerequisite python build requirements
	uv pip install -r pyproject.toml --extra develop

requirements-js:  ## install prerequisite javascript build requirements
	pnpm --dir js install --frozen-lockfile
	pnpm --dir js exec playwright install chromium

requirements: requirements-js requirements-py  ## setup project for development

.PHONY: build-py build-js build
build-py:
	python -m build -w -n

build-js:
	cd js; pnpm build

build: build-js build-py  ## build the project

.PHONY: docs
docs:  ## build docs
	python -m sphinx -W -b html docs docs/_build/html

.PHONY: install
install:  ## install python library
	uv pip install .

#########
# LINTS #
#########
.PHONY: lint-py lint-js lint lints
lint-py:  ## run python linter with ruff
	python -m ruff check sphinxcontrib tests
	python -m ruff format --check sphinxcontrib tests

lint-js:  ## run js linter
	cd js; pnpm lint

lint-docs:  ## lint docs with mdformat and codespell
	python -m mdformat --check README.md $(wildcard docs/index.md docs/src)
	python -m codespell_lib README.md $(wildcard docs/index.md docs/src)

lint: lint-js lint-py lint-docs  ## run project linters

# alias
lints: lint

.PHONY: fix-py fix-js fix-docs fix format
fix-py:  ## fix python formatting with ruff
	python -m ruff check --fix sphinxcontrib tests
	python -m ruff format sphinxcontrib tests

fix-js:  ## fix js formatting
	cd js; pnpm fix

fix-docs:  ## autoformat docs with mdformat and codespell
	python -m mdformat README.md $(wildcard docs/index.md docs/src)
	python -m codespell_lib --write README.md $(wildcard docs/index.md docs/src)

fix: fix-js fix-py fix-docs  ## run project autoformatters

# alias
format: fix

################
# Other Checks #
################
.PHONY: check-dist check-types checks check

check-dist:  ## check python sdist and wheel with check-dist
	check-dist -v

check-types:  ## check python types with ty
	ty check --python $$(which python) sphinxcontrib

checks: check-dist check-types

# alias
check: checks

#########
# TESTS #
#########
.PHONY: test-py tests-py coverage-py
test-py:  ## run python tests
	python -m pytest -v tests

# alias
tests-py: test-py

coverage-py:  ## run python tests and collect test coverage
	python -m pytest -v tests --cov=sphinxcontrib.mermaid --cov-report term-missing --cov-report xml

.PHONY: test-js tests-js coverage-js
test-js:  ## run js tests
	cd js; pnpm test

# alias
tests-js: test-js

coverage-js: test-js  ## run js tests and collect test coverage

.PHONY: test coverage tests
test: test-py test-js  ## run all tests
coverage: coverage-py coverage-js  ## run all tests and collect test coverage

# alias
tests: test

###########
# VERSION #
###########
.PHONY: show-version patch minor major

show-version:  ## show current library version
	@bump-my-version show current_version

patch:  ## bump a patch version
	@bump-my-version bump patch

minor:  ## bump a minor version
	@bump-my-version bump minor

major:  ## bump a major version
	@bump-my-version bump major

########
# DIST #
########
.PHONY: dist dist-py dist-js dist-check publish

dist-py:  ## build python dists
	python -m build -w -s

dist-js:  # build js dists
	cd js; pnpm pack

dist-check:  ## run python dist checker with twine
	python -m twine check dist/*

dist: clean build dist-py dist-check  ## build all dists

publish: dist  ## publish python assets

#########
# CLEAN #
#########
.PHONY: deep-clean clean

deep-clean: ## clean everything from the repository
	git clean -fdx

clean: ## clean the repository
	rm -rf .coverage coverage cover htmlcov logs build dist *.egg-info

############################################################################################

.PHONY: help

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'
