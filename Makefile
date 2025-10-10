ARG := $(word 2, $(MAKECMDGOALS))
$(eval $(ARG):;@:)

sources = iso_week_date tests


init-env:
	uv pip install .

init-dev:
	uv pip install -e . --group dev --upgrade
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
	uvx ruff version
	uvx ruff format $(sources)
	uvx ruff check $(sources) --fix
	uvx ruff clean

test:
	uv run --active --no-sync --group tests pytest $(sources) --cov=iso_week_date --cov=tests --cov-fail-under=80 --cache-clear
	uv run --active --no-sync --group tests pytest iso_week_date --doctest-modules

slotscheck:
	slotscheck $(sources)

coverage:
	rm -rf .coverage
	(rm docs/img/coverage.svg) || (echo "No coverage.svg file found")
	coverage run -m pytest
	coverage report -m
	coverage-badge -o docs/img/coverage.svg

interrogate:
	interrogate $(sources)

interrogate-badge:
	interrogate --generate-badge docs/img/interrogate-shield.svg

typing:
	uv run --active --no-sync --group typing mypy $(sources)
	uv run --active --no-sync --group typing pyright $(sources)

check: interrogate lint test slotscheck typing clean-folders

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
	python bump-version.py $(ARG)
	gh pr create --title "release: Bump version to " --body "Bump version" --base main --label release
