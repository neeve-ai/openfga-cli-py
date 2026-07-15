.PHONY: install quality

install:
	pip install setuptools wheel setuptools-download
	pip install . --no-build-isolation

quality: install
	fga version
	fga help
	pip install --quiet pytest
	pytest tests/
	pip wheel --no-deps --no-build-isolation --wheel-dir dist .
