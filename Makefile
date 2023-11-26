init-env:
	pip install . --no-cache-dir

init-dev:
	pip install -e ".[all-dev]" --no-cache-dir --upgrade
	pre-commit install

clean-notebooks:
	jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace notebooks/*.ipynb

clean-folders:
	rm -rf __pycache__ */__pycache__ */**/__pycache__ \
		.pytest_cache */.pytest_cache */**/.pytest_cache \
		.ruff_cache */.ruff_cache */**/.ruff_cache \
		.mypy_cache */.mypy_cache */**/.mypy_cache \
		site build dist htmlcov .coverage .tox

lint:
	ruff version
	ruff check iso_week_date tests --fix
	ruff format iso_week_date tests
	ruff clean

test:
	pytest tests -n auto

coverage:
	rm -rf .coverage
	(rm docs/img/coverage.svg) || (echo "No coverage.svg file found")
	coverage run -m pytest
	coverage report -m
	coverage-badge -o docs/img/coverage.svg

interrogate:
	interrogate iso_week_date tests

interrogate-badge:
	interrogate --generate-badge docs/img/interrogate-shield.svg

check: interrogate lint test clean-folders

docs-serve:
	mkdocs serve

docs-deploy:
	mike set-default --push --update-aliases $(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3) latest

pypi-push:
	rm -rf dist
	hatch build
	hatch publish

get-version :
	@echo $(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)
