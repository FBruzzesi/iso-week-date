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
	ruff format iso_week_date tests
	ruff check iso_week_date tests --fix
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

type:
	mypy iso_week_date tests

check: interrogate lint test type clean-folders

docs-serve:
	mkdocs serve

docs-deploy:
	mkdocs gh-deploy

pypi-push:
	rm -rf dist
	python -m hatch build
	python -m hatch publish

get-version :
	@echo $(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)
