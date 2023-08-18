init-env:
	pip install . --no-cache-dir

init-dev:
	pip install -e ".[all]" --no-cache-dir
	pre-commit install

clean-notebooks:
	jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace notebooks/*.ipynb

clean-folders:
	rm -rf __pycache__ */__pycache__ */**/__pycache__ \
		.pytest_cache */.pytest_cache */**/.pytest_cache \
		.ruff_cache */.ruff_cache */**/.ruff_cache \
		.mypy_cache */.mypy_cache */**/.mypy_cache \
		site build dist htmlcov .coverage .tox

interrogate:
	interrogate -vv --ignore-nested-functions --ignore-module --ignore-init-method \
	 --fail-under=90 iso_week tests

style:
	black --target-version py38 --line-length 90 iso_week tests
	isort --profile black -l 90 iso_week tests
	ruff iso_week tests && ruff clean


test:
	pytest tests -n auto

test-coverage:
	rm -rf .coverage
	rm docs/img/coverage.svg
	coverage run -m pytest
	coverage report -m
	coverage-badge -o docs/img/coverage.svg

check: interrogate style test clean-folders

docs-serve:
	mkdocs serve

docs-deploy:
	mkdocs gh-deploy

pypi-push:
	python -m pip install twine wheel --no-cache-dir

	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine upload dist/*

interrogate-badge:
	interrogate -vv --ignore-nested-functions --ignore-module --ignore-init-method --generate-badge docs/img/interrogate-shield.svg
