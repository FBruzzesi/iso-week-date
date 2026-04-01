ARG := $(word 2, $(MAKECMDGOALS))
$(eval $(ARG):;@:)

sources = src tests

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
	uvx rumdl check .

test:
	uv run --group tests pytest $(sources) --cov=src --cov=tests --cov-fail-under=95 --doctest-modules --cache-clear

slotscheck:
	uvx --with ".[all]" slotscheck -m iso_week_date

interrogate:
	uvx interrogate src

interrogate-badge:
	uvx interrogate src --generate-badge docs/img/interrogate-shield.svg

typing:
	uv run --group typing mypy $(sources)
	uv run --group typing pyright $(sources)

check: interrogate lint test slotscheck typing clean-folders

setup-release:
	git checkout main
	git fetch upstream
	git reset --hard upstream/main
	git checkout -b bump-version
	python bump-version.py $(ARG)
	gh pr create --title "release: Bump version to " --body "Bump version" --base main --label release
