ARG := $(word 2, $(MAKECMDGOALS))
$(eval $(ARG):;@:)


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
	pytest tests
	PYTHONHASHSEED=42 pytest iso_week_date --doctest-modules

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
	mypy iso_week_date
	pyright iso_week_date

check: interrogate lint test type clean-folders

docs-serve:
	mkdocs serve

docs-deploy:
	mkdocs gh-deploy

pypi-push:
	rm -rf dist
	uv build
	uv publish


setup-release:
	git checkout main
	git fetch upstream
	git reset --hard upstream/main
	git checkout -b bump-version
	python bump-version $(ARG)
	gh pr create --title "release: Bump version to " --body "Bump version to $(ARG)" --base main --label release
